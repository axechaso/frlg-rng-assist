"""PID-only recovery of past static / wild rolls in one title-seed epoch."""

from .backend import backend, bounded, predict
from .encounters import ENCOUNTERS, UNOWN_CHAMBERS, allowed_methods, default_offset
from .wild import predict_wild, slot_from, unown_letter
from .wild_tables import area_for, predicted_species, species_mask


HP_TYPES = ("格斗", "飞行", "毒", "地面", "岩石", "虫", "幽灵", "钢",
            "火", "水", "草", "电", "超能", "冰", "龙", "恶")


def hidden_power(ivs):
    hp, attack, defense, spa, spd, speed = ivs
    ordered = (hp, attack, defense, speed, spa, spd)
    kind = sum((v & 1) << i for i, v in enumerate(ordered)) * 15 // 63
    power = 30 + sum((v >> 1 & 1) << i for i, v in enumerate(ordered)) * 40 // 63
    return {"type": HP_TYPES[kind], "type_index": kind + 1, "power": power}


def pid_states(pid):
    """The two consecutive high halves fix at most a few pre-PID states."""
    lcg, _ = backend()
    low, high = pid & 0xFFFF, pid >> 16
    for bottom in range(65536):
        first = (low << 16) | bottom
        if lcg.step(first) >> 16 == high:
            yield lcg.unstep(first)


def distance(start, end):
    """Bitwise full-period LCG distance, as used by our resident; O(32)."""
    a, c, result = 0x41C64E6D, 0x6073, 0
    for bit in range(32):
        if (start ^ end) & (1 << bit):
            start = (start * a + c) & 0xFFFFFFFF
            result |= 1 << bit
        c = c * (a + 1) & 0xFFFFFFFF
        a = a * a & 0xFFFFFFFF
    return result


def wild_starts(pid, pid_seed, model, chamber):
    lcg, _ = backend()
    wanted = pid % 25 if model == "wild" else unown_letter(pid)
    current = pid_seed
    for _ in range(65536):
        if model == "wild":
            if (current >> 16) % 25 == wanted:
                yield lcg.advance(current, -3)
        else:
            start = lcg.advance(current, -2)
            if UNOWN_CHAMBERS[chamber][slot_from(lcg.step(start) >> 16)] == wanted:
                yield start
        # The previous rejected PID pair ends at the current pre-PID state.
        previous_low = lcg.unstep(current)
        previous = (current & 0xFFFF0000) | (previous_low >> 16)
        current = lcg.unstep(previous_low)
        if model == "unown":
            previous = (previous >> 16) | ((previous & 0xFFFF) << 16)
        if (previous % 25 if model == "wild" else unown_letter(previous)) == wanted:
            return
    raise ValueError("此 PID 的野生重抽链超过反查工作上限，未将不完整搜索当作无结果。")


def lookup(initial_seed, pid, target, *, first=0, last=9999999, method=1, chamber="monean",
           game="firered", location="other", target_advance=None, offset=None, species=0):
    bounded(initial_seed, 0, 0xFFFF, "初始 seed")
    bounded(pid, 0, 0xFFFFFFFF, "PID")
    bounded(first, 0, 9999999, "范围起点")
    bounded(last, first, 9999999, "范围终点")
    if target not in ENCOUNTERS or game not in ("firered", "leafgreen"):
        raise ValueError("请选择有效的游戏和目标")
    if type(method) is not int or method not in allowed_methods(target):
        raise ValueError("定点仅支持 Method 1 / 4；野生支持 H1 / H2 / H4")
    if chamber not in UNOWN_CHAMBERS:
        raise ValueError("未知图腾房间无效")
    if target_advance is not None:
        bounded(target_advance, 0, 9999999, "原目标 advance")
    extra = default_offset(target, game, location) if offset is None else bounded(offset, 0, 65533, "Offset")
    model = ENCOUNTERS[target].model
    if species and model != "wild":
        raise ValueError("物种筛选只用于普通野生遭遇。")
    mask = int.from_bytes(species_mask(target, game, location, species), "little")
    lcg, _ = backend()
    encoded = pid if model != "unown" else (pid >> 16) | ((pid & 0xFFFF) << 16)
    candidates = {}
    area = area_for(target)
    for pid_seed in pid_states(encoded):
        starts = (pid_seed,) if model == "static" else wild_starts(pid, pid_seed, model, chamber)
        for start in starts:
            advance = distance(initial_seed, start)
            if not first <= advance <= last:
                continue
            if model == "wild" and not (mask >> ((lcg.step(start) >> 16) % 100)) & 1:
                continue
            mon = (predict(start, 0, 0, method) if model == "static" else
                   predict_wild(start, 0, 0, method, model=model, area=area, chamber=chamber))
            if mon["personality"] != pid:
                raise RuntimeError("反查候选未通过正向 PID 核对")
            result = {"actual_advance": advance, "generation_seed": start, "pid": pid,
                      "method": method, "predicted_ivs": mon["ivs"], "nature": mon["nature_zh"],
                      "predicted_hidden_power": hidden_power(mon["ivs"])}
            if model != "static":
                result.update(pid_advance=distance(initial_seed, pid_seed),
                              encounter_slot=mon["encounter_slot"], rerolls=mon["rerolls"])
                result["predicted_species"] = (201 if model == "unown" else
                                               predicted_species(target, game, location, mon["encounter_slot"]))
            if target_advance is not None:
                error = advance - target_advance
                suggested = extra + error
                result.update(error_advances=error, previous_offset=extra,
                              suggested_offset=suggested if 0 <= suggested <= 65533 else None)
            candidates[advance] = result
    return {"kind": "pid_lookup", "initial_seed": initial_seed, "actual_pid": pid,
            "target": target, "target_name": ENCOUNTERS[target].name, "model": model,
            "game": game, "location": location, "method": method,
            "wild_species": species or None,
            "range": {"first": first, "last": last, "inclusive": True},
            "result": "unique" if len(candidates) == 1 else "ambiguous" if candidates else "no_match",
            "candidates": [candidates[key] for key in sorted(candidates)],
            "input_timing_measured": False, "ivs_are_predictions": True}
