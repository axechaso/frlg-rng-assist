"""Read Gen III records without importing private host modules.

Layout and XOR/shuffle conversion adapted from PokeLDN's AGPL-3.0 code; see NOTICE.md.
The IV word is PokemonSubstruct3.ivs [pret/pokefirered include/pokemon.h].
"""

from .backend import bounded

ORDERS = (
    "GAEM",
    "GAME",
    "GEAM",
    "GEMA",
    "GMAE",
    "GMEA",
    "AGEM",
    "AGME",
    "AEGM",
    "AEMG",
    "AMGE",
    "AMEG",
    "EGAM",
    "EGMA",
    "EAGM",
    "EAMG",
    "EMGA",
    "EMAG",
    "MGAE",
    "MGEA",
    "MAGE",
    "MAEG",
    "MEGA",
    "MEAG",
)
PARTY_DUMP_SIZE = 608


def decode_mon(raw, *, encrypted):
    if len(raw) not in (80, 100):
        raise ValueError("宝可梦记录必须为 80 或 100 字节")
    if raw[19] & 1:
        raise ValueError("记录被游戏标记为 Bad Egg，不能作为有效捕获结果")
    pid = int.from_bytes(raw[:4], "little")
    otid = int.from_bytes(raw[4:8], "little")
    secure = raw[32:80]
    if encrypted:
        key = pid ^ otid
        secure = b"".join(
            (int.from_bytes(secure[i : i + 4], "little") ^ key).to_bytes(4, "little") for i in range(0, 48, 4)
        )
        order = ORDERS[pid % 24]
        secure = b"".join(
            secure[order.index(letter) * 12 : order.index(letter) * 12 + 12] for letter in "GAEM"
        )
    checksum = sum(int.from_bytes(secure[i : i + 2], "little") for i in range(0, 48, 2)) & 0xFFFF
    if checksum != int.from_bytes(raw[28:30], "little"):
        raise ValueError("宝可梦校验和不符；请重新采集，或检查 .pk3/.ek3 格式")
    species = int.from_bytes(secure[:2], "little")
    if not 1 <= species <= 411 or 252 <= species <= 276:
        raise ValueError("宝可梦种类字段无效")
    misc = secure[36:48]
    iv_word = int.from_bytes(misc[4:8], "little")
    stored = [(iv_word >> (5 * index)) & 31 for index in range(6)]
    hp, attack, defense, speed, spa, spd = stored
    tid, sid = otid & 0xFFFF, otid >> 16
    return {
        "pid": pid,
        "tid": tid,
        "sid": sid,
        "species": species,
        "nature": pid % 25,
        "ivs": (hp, attack, defense, spa, spd, speed),
        "checksum_ok": True,
        "shiny": (tid ^ sid ^ (pid & 0xFFFF) ^ (pid >> 16)) < 8,
        "is_egg": bool(iv_word >> 30 & 1 or raw[19] & 4),
        "origin_game": int.from_bytes(misc[2:4], "little") >> 7 & 15,
        "met_location": misc[1],
        "met_level": misc[2] & 0x7F,
        "level": raw[84] if len(raw) == 100 else None,
    }


def party_records(raw):
    if len(raw) != PARTY_DUMP_SIZE:
        raise ValueError(f"队伍采集应为 {PARTY_DUMP_SIZE} 字节")
    count = raw[0]  # u8 playerPartyCount; the next three bytes are struct padding.
    bounded(count, 1, 6, "队伍数量")
    records = []
    for index in range(count):
        try:
            mon = decode_mon(raw[4 + index * 100 : 104 + index * 100], encrypted=True)
        except ValueError as exc:
            raise ValueError(f"队伍第 {index + 1} 位：{exc}") from exc
        records.append({"slot": index + 1, **mon})
    return records


def choose_record(records, species, slot=0):
    bounded(slot, 0, 6, "队伍位置")
    if slot:
        selected = [mon for mon in records if mon.get("slot") == slot]
        if not selected:
            raise ValueError("所选队伍位置为空")
        return selected[0]
    matching = [mon for mon in records if mon["species"] == species]
    if not matching:
        raise ValueError("队伍里没有所选目标；请把捕获的目标放入队伍并在游戏里保存")
    if len(matching) != 1:
        raise ValueError("队伍里有多个同种目标，请明确选择队伍位置 1..6")
    return matching[0]
