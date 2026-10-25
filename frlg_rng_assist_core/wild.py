"""FRLG wild generation: slot / level, nature rejection, and Tanoby's reversed PID halves."""

from .backend import NATURES, NATURES_ZH, backend, bounded, predict, recover
from .encounters import UNOWN_CHAMBERS

LAND_ENDS = (20, 40, 50, 60, 70, 80, 85, 90, 94, 98, 99, 100)


def slot_from(roll, area="land"):
    ends, start = {
        "land": (LAND_ENDS, 0), "surf": ((60, 90, 95, 99, 100), 0),
        "old": ((70, 100), 0), "good": ((60, 80, 100), 2),
        "super": ((40, 80, 95, 99, 100), 5),
    }[area]
    return start + next(i for i, end in enumerate(ends) if roll % 100 < end)


def unown_letter(pid):
    return (((pid >> 24 & 3) << 6) | ((pid >> 16 & 3) << 4)
            | ((pid >> 8 & 3) << 2) | (pid & 3)) % 28


def predict_wild(seed, tid, sid, method=1, *, model="wild", area="land", chamber="monean"):
    bounded(seed, 0, 0xFFFFFFFF, "seed")
    if model not in ("wild", "unown") or chamber not in UNOWN_CHAMBERS:
        raise ValueError("野生模型或未知图腾房间无效")
    lcg, _ = backend()
    state = lcg.step(seed)
    slot = slot_from(state >> 16, "land" if model == "unown" else area)
    state = lcg.step(state)
    level_roll, consumed = state >> 16, 2
    if model == "wild":
        state = lcg.step(state)
        wanted, consumed = (state >> 16) % 25, 3
    else:
        wanted = UNOWN_CHAMBERS[chamber][slot]
    attempts = 0
    while True:
        pid_seed = state
        low = lcg.step(state)
        state = lcg.step(low)
        pid = ((state >> 16) << 16) | (low >> 16)
        if model == "unown":
            pid = (pid >> 16) | ((pid & 0xFFFF) << 16)
        attempts += 1
        if (pid % 25 if model == "wild" else unown_letter(pid)) == wanted:
            break
        consumed += 2
    mon = dict(predict(pid_seed, tid, sid, method))
    nature = pid % 25
    mon.update(personality=pid, nature=nature, nature_name=NATURES[nature], nature_zh=NATURES_ZH[nature],
               generation_seed=seed, pid_seed=pid_seed, pid_offset=consumed, rerolls=attempts - 1,
               encounter_slot=slot, level_roll=level_roll, model=model, method=method)
    return mon


def recover_wild(pid, ivs, *, model="wild", chamber="monean"):
    """Recover encounter starts, rejecting prefixes that would have accepted an earlier PID."""
    lcg, _ = backend()
    encoded = pid if model == "wild" else (pid >> 16) | ((pid & 0xFFFF) << 16)
    result = set()
    wanted = pid % 25 if model == "wild" else unown_letter(pid)
    for match in recover(encoded, ivs):
        current = match["generation_seed"]
        for _ in range(65536):
            if model == "wild":
                if (current >> 16) % 25 == wanted:
                    result.add((lcg.advance(current, 0xFFFFFFFD), match["method"], match["generation_seed"]))
            else:
                start = lcg.advance(current, 0xFFFFFFFE)
                slot = slot_from(lcg.step(start) >> 16)
                if UNOWN_CHAMBERS[chamber][slot] == wanted:
                    result.add((start, match["method"], match["generation_seed"]))
            current = lcg.advance(current, 0xFFFFFFFE)
            previous = predict(current, 0, 0)["personality"]
            if model == "unown":
                previous = (previous >> 16) | ((previous & 0xFFFF) << 16)
            if (previous % 25 if model == "wild" else unown_letter(previous)) == wanted:
                break
        else:
            raise ValueError("野生反推超过单次工作上限；无法完成此记录的范围核对")
    return [{"generation_seed": seed, "method": method, "pid_seed": pid_seed}
            for seed, method, pid_seed in sorted(result)]
