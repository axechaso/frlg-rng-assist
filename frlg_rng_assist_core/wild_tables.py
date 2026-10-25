"""Version-specific FRLG encounter tables and pre-slot species filters."""

from functools import lru_cache
import json
from pathlib import Path


@lru_cache(maxsize=1)
def tables():
    return json.loads((Path(__file__).with_name("data") / "wild_tables.json").read_text(encoding="utf-8"))["tables"]


@lru_cache(maxsize=1)
def names():
    return json.loads((Path(__file__).with_name("data") / "names.json").read_text(encoding="utf-8"))


def table_at(location):
    data = tables()
    if location in data:
        return data[location]
    candidates = [row for row in data.values() if row["region"] == location]
    return candidates[0] if len(candidates) == 1 else None


def offset_region(location):
    row = tables().get(location)
    return row["region"] if row else location


def area_for(target):
    return {"sweet-surf": "surf", "wild-land": "rock", "fish-old": "old", "fish-good": "good",
            "fish-super": "super"}.get(target, "land")


def rows_at(target, game, location):
    table = table_at(location)
    if not table:
        return None
    field = {"land": "land_mons", "surf": "water_mons", "rock": "rock_smash_mons",
             "old": "fishing_mons", "good": "fishing_mons", "super": "fishing_mons"}[area_for(target)]
    return table[game].get(field)


def available_species(target, game, location):
    rows = rows_at(target, game, location)
    if rows is None:
        return ()
    area = area_for(target)
    indices = {"old": range(2), "good": range(2, 5), "super": range(5, 10)}.get(area, range(len(rows)))
    return tuple(sorted({rows[index][0] for index in indices}))


def species_mask(target, game, location, species=0):
    """100 accepted/rejected percentile rolls, encoded as 13 bytes for the resident."""
    from .backend import bounded
    from .wild import slot_from

    bounded(species, 0, 386, "宝可梦图鉴编号")
    if species == 201:
        raise ValueError("未知图腾请使用「未知图腾」类别并选择房间，不能使用普通野生物种筛选。")
    if not species:
        return b"\xff" * 12 + b"\x0f"
    if species not in available_species(target, game, location):
        if table_at(location) is None:
            raise ValueError("筛选野生宝可梦时请选择具体楼层 / 区域，不能使用未知地点或合并地点。")
        raise ValueError("所选游戏、地点和遭遇方式没有这种宝可梦；请更换条件。")
    rows = rows_at(target, game, location)
    mask = sum((rows[slot_from(roll, area_for(target))][0] == species) << roll for roll in range(100))
    return mask.to_bytes(13, "little")


def predicted_species(target, game, location, slot):
    rows = rows_at(target, game, location)
    return rows[slot][0] if rows and 0 <= slot < len(rows) else None


def selectable_locations(legacy):
    """Keep saved Offset-region keys; add concrete floors beside their region."""
    result, used = [], set()
    for region, label in legacy:
        result.append((region, label))
        used.add(region)
        for key, row in tables().items():
            if row["region"] == region and key not in used and "CHAMBER" not in row["map"]:
                result.append((key, row["labels"]["zh"]))
                used.add(key)
    for key, row in tables().items():
        if key not in used and "CHAMBER" not in row["map"]:
            result.append((key, row["labels"]["zh"]))
            used.add(key)
    return tuple(result)
