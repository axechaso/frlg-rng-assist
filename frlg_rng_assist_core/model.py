"""Offline arithmetic. Nothing here schedules a console input."""

from dataclasses import asdict, dataclass

from .backend import backend, bounded, predict, recover, validate_ivs

IV_ORDER = ("hp", "attack", "defense", "sp_attack", "sp_defense", "speed")


@dataclass(frozen=True)
class Criteria:
    shiny: bool = True
    nature: int | None = None
    pid: int | None = None
    iv_min: tuple = (0, 0, 0, 0, 0, 0)
    iv_max: tuple = (31, 31, 31, 31, 31, 31)

    def __post_init__(self):
        if type(self.shiny) is not bool:
            raise ValueError("shiny 必须是布尔值")
        if self.nature is not None:
            bounded(self.nature, 0, 24, "性格")
        if self.pid is not None:
            bounded(self.pid, 0, 0xFFFFFFFF, "PID")
        validate_ivs(self.iv_min)
        validate_ivs(self.iv_max)
        if any(low > high for low, high in zip(self.iv_min, self.iv_max)):
            raise ValueError("每项 IV 下限必须不大于上限")

    def matches(self, mon):
        return (
            (not self.shiny or mon["shiny"])
            and (self.nature is None or self.nature == mon["nature"])
            and (self.pid is None or self.pid == mon["personality"])
            and all(low <= value <= high for value, low, high in zip(mon["ivs"], self.iv_min, self.iv_max))
        )


def search(
    seed,
    tid,
    sid,
    *,
    method=1,
    start=0,
    advances=100000,
    max_results=10,
    criteria=None,
    progress=None,
    cancel=None,
):
    bounded(seed, 0, 0xFFFFFFFF, "seed")
    bounded(tid, 0, 65535, "TID")
    bounded(sid, 0, 65535, "SID")
    bounded(start, 0, 0xFFFFFFFF, "起始 advance")
    bounded(advances, 1, 10_000_000, "候选数量")
    bounded(max_results, 1, 1000, "结果上限")
    if start + advances > 0x100000000:
        raise ValueError("搜索范围不能跨过 32 位索引的末尾")
    if type(method) is not int or method not in (1, 2, 4):
        raise ValueError("仅支持 Method 1、2、4")
    criteria = criteria or Criteria()
    lcg, _ = backend()
    state, targets, tested = lcg.advance(seed, start), [], 0
    reason = "range_exhausted"
    for index in range(start, start + advances):
        if cancel and cancel():
            reason = "cancelled"
            break
        mon = predict(state, tid, sid, method)
        tested += 1
        if criteria.matches(mon):
            targets.append(
                {
                    "generation_seed": state,
                    "advance": index,
                    "pid": mon["personality"],
                    "nature": mon["nature"],
                    "nature_name": mon["nature_name"],
                    "nature_zh": mon["nature_zh"],
                    "ivs": mon["ivs"],
                    "shiny": mon["shiny"],
                }
            )
            if len(targets) >= max_results:
                reason = "result_limit"
                break
        if progress and tested % 4096 == 0:
            progress(tested, advances)
        state = lcg.step(state)
    if progress:
        progress(tested, advances)
    return {
        "kind": "offline_search",
        "seed": seed,
        "seed_boundary": "before_first_pid_draw",
        "tid": tid,
        "sid": sid,
        "method": method,
        "start": start,
        "requested_candidates": advances,
        "candidates_tested": tested,
        "stop_reason": reason,
        "criteria": asdict(criteria),
        "targets": targets,
        "iv_order": IV_ORDER,
        "live_synchronized": False,
        "can_schedule_inputs": False,
    }


def recovery_report(pid, ivs, *, reference_seed=None, max_offset=4096):
    candidates = recover(pid, ivs)
    if reference_seed is not None:
        bounded(reference_seed, 0, 0xFFFFFFFF, "同一 RNG 时段的参考 seed")
        bounded(max_offset, 0, 1_000_000, "最大距离")
        lcg, _ = backend()
        candidates = [
            {**candidate, "offset_advances": lcg.distance(reference_seed, candidate["generation_seed"])}
            for candidate in candidates
        ]
        candidates = [candidate for candidate in candidates if candidate["offset_advances"] <= max_offset]
    return {
        "kind": "state_recovery",
        "pid": pid,
        "ivs": tuple(ivs),
        "iv_order": IV_ORDER,
        "reference_seed": reference_seed,
        "candidates": candidates,
        "result": "unique" if len(candidates) == 1 else "ambiguous" if candidates else "no_match",
        "live_synchronized": False,
        "can_schedule_inputs": False,
    }
