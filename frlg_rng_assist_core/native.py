"""Build the standalone guest using the public RNG helpers and versioned gift format."""

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import struct

from .backend import backend, bounded
from .model import Criteria
from .wild_tables import species_mask
from .encounters import (
    BASE_PRESS_OFFSETS, ENCOUNTERS, UNOWN_CHAMBERS, WILD_LOCATIONS, allowed_methods,
    default_offset, offset_source,
)


GAMES = {"firered": "火红", "leafgreen": "叶绿"}
GAME_ORIGINS = {"firered": 4, "leafgreen": 5}
ACK = 0x524E4703
# Revision-0A address facts from upstream v0.39.1 builds.py, follower.s, shiny.inc, rom_map.py,
# english_names.py. That table is keyed by French addresses: French + offset = English.
# Production code does not import their private implementations.
PROFILES = {
    "BPRE": {
        "main": 0x03002380,
        "rng": 0x030042D0,
        "sb2ptr": 0x030042DC,
        "cb1": 0x08059CED,
        "cb2": 0x08059D6D,
        "original": 0x08000735,
        "context": 0x03000FB0,
        "wait": 0x0806EFF5,
        "objects": 0x02036E34,
        "selected": 0x03004344,
        "seed_getter": 0x0800059D,
        "palette": 0x020379D6,
        "party": 0x02024280,
        "party_count": 0x02024025,
        "battle_cb2": 0x0801489D,
        "mon_data": 0x08043391,
        "table": 0x030027E0,
    },
    "BPRF": {
        "main": 0x030022D0,
        "rng": 0x03004220,
        "sb2ptr": 0x0300422C,
        "cb1": 0x08059E49,
        "cb2": 0x08059EC9,
        "original": 0x0800071D,
        "context": 0x03000FB0,
        "wait": 0x0806F159,
        "objects": 0x02036E34,
        "selected": 0x03004294,
        "seed_getter": 0x08000585,
        "palette": 0x020379D6,
        "party": 0x02024280,
        "party_count": 0x02024025,
        "battle_cb2": 0x08014889,
        "mon_data": 0x080432E5,
        "table": 0x03002730,
    },
}
PROFILES["BPGE"] = dict(PROFILES["BPRE"])
PROFILES["BPGF"] = dict(PROFILES["BPRF"])
CONFIG_WORDS = (
    "main",
    "rng",
    "sb2ptr",
    "cb1",
    "cb2",
    "original",
    "seed_getter",
    "palette",
    "party",
    "party_count",
    "battle_cb2",
    "mon_data",
)


def validate_context(game, build, target):
    if game not in GAMES or target not in ENCOUNTERS:
        raise ValueError("请选择有效的火红/叶绿游戏和遭遇目标")
    if build != "auto":
        if build not in PROFILES:
            raise ValueError("本版仅支持 Switch 英文 / 法文 rev 0A：BPRE、BPGE、BPRF、BPGF")
        if not build.startswith("BPR" if game == "firered" else "BPG"):
            raise ValueError("游戏与卡带代码不匹配")


def install_plan(game, build, target, *, first=10000, last=200000, criteria=None, offset=None,
                 method=1, chamber="monean", location="other", species=0):
    backend()
    validate_context(game, build, target)
    bounded(first, 0, 9_999_999, "范围起点")
    bounded(last, first, 9_999_999, "范围终点")
    criteria = criteria or Criteria()
    if criteria.pid is not None:
        raise ValueError("实机搜索仅支持闪光、性格及 IV 条件；精确 PID 请使用离线搜索")
    encounter = ENCOUNTERS[target]
    if species and encounter.model != "wild":
        raise ValueError("物种筛选只用于普通野生遭遇。")
    mask = species_mask(target, game, location, species)
    base_offset = BASE_PRESS_OFFSETS[encounter.profile]
    if location not in dict(WILD_LOCATIONS):
        raise ValueError("野生地点无效")
    extra_offset = default_offset(target, game, location) if offset is None else bounded(offset, 0, 65533, "Offset")
    if type(method) is not int or method not in allowed_methods(target):
        raise ValueError("定点仅支持 Method 1 / 4；野生支持 H1 / H2 / H4")
    if chamber not in UNOWN_CHAMBERS:
        raise ValueError("未知图腾房间无效")
    return {
        "kind": "native_install",
        "status": "prepared",
        "game": game,
        "build": build,
        "target": target,
        "target_name": encounter.name,
        "profile": encounter.profile,
        "range": {
            "first": first,
            "last": last,
            "inclusive": True,
            "unit": "rng_advances",
            "origin": "title_reseed_initial_seed",
            "boundary": "before_first_pid_draw" if encounter.model == "static" else "before_encounter_slot_draw",
        },
        "criteria": asdict(criteria),
        "method": method,
        "model": encounter.model,
        "wild_species": species or None,
        "slot_roll_mask": mask.hex(),
        "location": location if encounter.model != "static" else None,
        "chamber": chamber if encounter.model == "unown" else None,
        "offset_source": (offset_source(target, game, location)
                          if extra_offset == default_offset(target, game, location) else "manual"),
        "decision_point": encounter.decision,
        "trigger_button": "UP" if encounter.button == 64 else "A",
        "trigger_key_mask": encounter.button,
        "offset_advances": extra_offset,
        "auto_a_base_offset_advances": base_offset,
        "auto_a_offset_advances": base_offset + extra_offset,
        "rng_tracking": "on_console_from_actual_initial_seed",
        "volatile": True,
        "result_verified": False,
        "hardware_tested": False,
    }


def guest():
    return json.loads(Path(__file__).with_name("guest.json").read_text(encoding="utf-8"))


def resident(plan, code):
    manifest = guest()
    blob = bytearray.fromhex(manifest["hex"])
    if hashlib.sha256(blob).hexdigest() != manifest["sha256"]:
        raise ValueError("插件的掌机端代码 SHA-256 不符，请重新安装插件")
    profile, encounter, criteria = PROFILES[code], ENCOUNTERS[plan["target"]], plan["criteria"]
    lcg, _ = backend()
    first = plan["range"]["first"]
    increment = lcg.advance(0, first)
    multiplier = (lcg.advance(1, first) - increment) & 0xFFFFFFFF
    advance = plan["auto_a_offset_advances"] + 1
    offset_c = lcg.advance(0, advance)
    offset_a = (lcg.advance(1, advance) - offset_c) & 0xFFFFFFFF
    order = (0, 1, 2, 5, 3, 4)  # Random's IV fields: HP, ATK, DEF, SPE, SPA, SPD.
    settings = struct.pack(
        "<18IH31B",
        *(profile[name] for name in CONFIG_WORDS),
        first,
        plan["range"]["last"],
        multiplier,
        increment,
        offset_a,
        offset_c,
        plan["auto_a_offset_advances"],
        {"static": 0, "wild": 1, "unown": 2}[encounter.model],
        plan["method"],
        int(criteria["shiny"]),
        255 if criteria["nature"] is None else criteria["nature"],
        int(encounter.menus),
        encounter.button,
        *(criteria["iv_min"][i] for i in order),
        *(criteria["iv_max"][i] for i in order),
        *(UNOWN_CHAMBERS[plan["chamber"]] + (0,) if encounter.model == "unown"
          else bytes.fromhex(plan["slot_roll_mask"])),
    )
    at = manifest["symbols"]["config"] - manifest["base"]
    blob[at : at + len(settings)] = settings
    if len(blob) != manifest["length"] or manifest["base"] + len(blob) > 0x02040000:
        raise ValueError("掌机端布局不正确，已停止")
    return bytes(blob)


def fnv1a(data):
    result = 0x811C9DC5
    for value in data:
        result = ((result ^ value) * 0x01000193) & 0xFFFFFFFF
    return result


def payloads(plan, code):
    manifest, profile = guest(), PROFILES[code]
    image = resident(plan, code)
    loader = bytes.fromhex(manifest["loader"]["hex"])
    chunk_size = ((1024 - len(loader)) // 4) * 4
    if chunk_size < 256:
        raise ValueError("安装器过大，已停止")
    result = []
    for offset in (*range(0, len(image), chunk_size), len(image)):
        chunk = image[offset : offset + chunk_size]
        final = offset == len(image)
        blob = bytearray(loader)
        values = {
            "dest": manifest["base"] + offset,
            "size": len(chunk),
            "table": profile["table"],
            "original": profile["original"],
            "getter": profile["seed_getter"] & ~1,
            "game": int.from_bytes(code.encode("ascii"), "little"),
            "final": int(final),
            "image_size": len(image),
            "hash": fnv1a(image),
            "entry": manifest["symbols"]["hook"] | 1,
            "source": len(loader),
            "base": manifest["base"],
        }
        for name, value in values.items():
            struct.pack_into("<I", blob, manifest["loader"]["symbols"]["p_" + name], value)
        blob += chunk
        if len(blob) > 1024:
            raise ValueError("安装器超过 Mystery Gift 的 1024 字节限制")
        result.append(bytes(blob))
    return tuple(result)


def write_gift(plan, path):
    from pokeldn.gifts import load

    codes = [
        code
        for code in PROFILES
        if code.startswith("BPR" if plan["game"] == "firered" else "BPG") and plan["build"] in ("auto", code)
    ]
    variants = {}
    for code in codes:
        parts = payloads(plan, code)
        components = {f"buffer_lead_{i + 1}": blob for i, blob in enumerate(parts[:-1])}
        components["buffer_code"] = parts[-1]
        variants[code] = {
            "data": {
                name: {"hex": blob.hex(), "sha256": hashlib.sha256(blob).hexdigest()}
                for name, blob in components.items()
            },
            "options": {"buffer_expect": ACK},
        }
    document = {
        "format": "pokeldn.gift",
        "version": 2,
        "game": "frlg",
        "name": f"FRLG RNG Assist · {plan['target_name']}",
        "variants": variants,
    }
    with Path(path).open("x", encoding="utf-8") as output:
        json.dump(document, output, ensure_ascii=False, indent=2)
        output.write("\n")
    load(path, game="frlg")  # Same public parser as the released host.
    return {
        "path": str(path),
        "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        "builds": codes,
        "resident_bytes": guest()["length"],
    }


def console_arguments(game, build, *, keys=None):
    out = ["--live", "--version", game, "--expect-console", game, "--console-build", build]
    if keys:
        out += ["--keys", keys]
    return out


def validate_install_ack(statuses):
    if statuses != [ACK]:
        errors = {
            0xBAD00001: "卡带代码不符",
            0xBAD00002: "不是受支持的 rev 0A",
            0xBAD00003: "已有其他钩子，请重新启动游戏后再安装",
            0xBAD00004: "初始 seed 读取函数与已知指令不符",
            0xBAD00005: "分段传输校验失败",
        }
        detail = errors.get(statuses[-1], f"回执 {statuses!r}") if statuses else "没有收到安装回执"
        raise ValueError(f"未确认安装成功：{detail}")
    return ACK
