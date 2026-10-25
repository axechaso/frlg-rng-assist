"""Only the RNG helpers promised by docs/plugins.md, API 1.11."""

from functools import lru_cache

NATURES = (
    "Hardy Lonely Brave Adamant Naughty Bold Docile Relaxed Impish Lax Timid Hasty "
    "Serious Jolly Naive Modest Mild Quiet Bashful Rash Calm Gentle Sassy Careful Quirky"
).split()
NATURES_ZH = (
    "勤奋 怕寂寞 勇敢 固执 顽皮 大胆 坦率 悠闲 淘气 乐天 胆小 急躁 "
    "认真 爽朗 天真 内敛 慢吞吞 冷静 害羞 马虎 温和 温顺 自大 慎重 浮躁"
).split()


@lru_cache(maxsize=1)
def backend():
    try:
        from pokeldn.frlg.rom import lcg
        from pokeldn.frlg.rom.rng_countdown import mon_from
    except ImportError as exc:
        raise RuntimeError("请更新 PokeLDN 主程序至 v0.39.1 或更新的 API 1.11 版本。") from exc
    return lcg, mon_from


def bounded(value, low, high, name):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} 必须是 {low}..{high} 之间的整数")
    return value


def validate_ivs(values):
    if len(values) != 6:
        raise ValueError("需要六项 IV，顺序为 HP / 攻击 / 防御 / 特攻 / 特防 / 速度")
    for value in values:
        bounded(value, 0, 31, "IV")


def predict(seed, tid, sid, method=1):
    """Return summary-screen IV order, converting the public API's stored order exactly once."""
    if type(method) is not int or method not in (1, 2, 4):
        raise ValueError("仅支持 Method 1、2、4")
    lcg, mon_from = backend()
    mon = dict(mon_from(seed, tid, sid))
    if method != 1:
        draws, _ = lcg.draws(seed, 5)
        first, second = (draws[3], draws[4]) if method == 2 else (draws[2], draws[4])
        mon["ivs"] = (
            first & 31,
            first >> 5 & 31,
            first >> 10 & 31,
            second & 31,
            second >> 5 & 31,
            second >> 10 & 31,
        )
    hp, attack, defense, speed, spa, spd = mon["ivs"]
    mon["ivs"] = (hp, attack, defense, spa, spd, speed)
    mon["nature_name"] = NATURES[mon["nature"]]
    mon["nature_zh"] = NATURES_ZH[mon["nature"]]
    return mon


def recover(pid, ivs):
    """Recover pre-PID states; a recovered state is evidence about a past roll, not live telemetry."""
    bounded(pid, 0, 0xFFFFFFFF, "PID")
    validate_ivs(ivs)
    lcg, _ = backend()
    hp, attack, defense, spa, spd, speed = ivs
    states = lcg.recover_wild_state(pid, (hp, attack, defense, speed, spa, spd), max_gap=1)
    methods = {(0, 0): 1, (1, 0): 2, (0, 1): 4}
    unique = set()
    for state in states:
        method = methods.get((state["gap"], state["iv_gap"]))
        if (
            method is not None
            and state["order"] == "low-half first"
            and state["iv_order"] == "HP/ATK/DEF first"
        ):
            unique.add((state["before"], method))
    return [{"generation_seed": seed, "method": method} for seed, method in sorted(unique)]
