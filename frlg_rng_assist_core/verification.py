from .backend import backend, bounded, recover
from .model import Criteria, IV_ORDER
from .native import ENCOUNTERS, GAME_ORIGINS


def verify(
    mon,
    game,
    target,
    *,
    nature=None,
    iv_min=(0, 0, 0, 0, 0, 0),
    iv_max=(31, 31, 31, 31, 31, 31),
    pid=None,
    shiny=True,
    initial_seed=None,
    search_range=None,
):
    criteria = Criteria(shiny, nature, pid, iv_min, iv_max)
    encounter = ENCOUNTERS[target]
    states = recover(mon["pid"], mon["ivs"])
    if initial_seed is not None:
        bounded(initial_seed, 0, 65535, "标题初始 seed")
        lcg, _ = backend()
        states = [
            {**state, "absolute_advance": lcg.distance(initial_seed, state["generation_seed"])}
            for state in states
        ]
    checks = {
        "checksum": mon["checksum_ok"],
        "species": mon["species"] == encounter.species,
        "not_egg": not mon["is_egg"],
        "origin_game": mon["origin_game"] == GAME_ORIGINS[game],
        "shiny": not shiny or mon["shiny"],
        "method_1_model": any(s["method"] == 1 for s in states),
        "nature": nature is None or mon["nature"] == nature,
        "pid": pid is None or mon["pid"] == pid,
        "iv_bounds": all(
            low <= value <= high for low, value, high in zip(criteria.iv_min, mon["ivs"], criteria.iv_max)
        ),
    }
    if initial_seed is not None and search_range is not None:
        checks["advance_range"] = any(
            s["method"] == 1 and search_range["first"] <= s["absolute_advance"] <= search_range["last"]
            for s in states
        )
    return {
        "kind": "result_verification",
        "game": game,
        "target": target,
        "target_name": encounter.name,
        "status": "matched" if all(checks.values()) else "mismatch",
        "checks": checks,
        "pokemon": dict(mon),
        "criteria": {"shiny": shiny, "nature": nature, "pid": pid, "iv_min": iv_min, "iv_max": iv_max},
        "generation_states": states,
        "iv_order": IV_ORDER,
        "initial_seed": initial_seed,
        "range_verified": bool(checks.get("advance_range", False)),
        "evidence_scope": "selected_pokemon_record",
        "input_timing_measured": False,
    }
