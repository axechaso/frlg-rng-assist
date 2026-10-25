import random
import struct

import pytest

from frlg_rng_assist_core.backend import predict
from frlg_rng_assist_core.model import Criteria
from frlg_rng_assist_core.native import ACK, PROFILES, guest, payloads, resident
from console import Console, ROM_GETTERS, SEED16

pytestmark = pytest.mark.emulation


@pytest.mark.parametrize("code", PROFILES)
def test_seed_getter_uses_the_french_to_english_mapping_in_the_correct_direction(code):
    assert PROFILES[code]["seed_getter"] == ROM_GETTERS[code] | 1


@pytest.mark.parametrize("code", PROFILES)
def test_030_wrong_getter_address_reproduces_the_hardware_refusal(code):
    c = Console(code, install=False)
    first = bytearray(payloads(c.plan, code)[0])
    old_address = ROM_GETTERS[code] - 0x18
    struct.pack_into("<I", first, guest()["loader"]["symbols"]["p_getter"], old_address)
    assert c.load(bytes(first)) == 0xBAD00004
    assert c.read(c.profile["table"]) == c.profile["original"]
    assert bytes(c.uc.mem_read(c.manifest["base"], c.manifest["length"])) == bytes(c.manifest["length"])


@pytest.mark.parametrize("code", PROFILES)
def test_installed_image_exact_and_atomic(code):
    c = Console(code, install=False)
    for part in payloads(c.plan, code)[:-1]:
        assert c.load(part) == ACK
        assert c.read(c.profile["table"]) == c.profile["original"]
    image = resident(c.plan, code)
    assert bytes(c.uc.mem_read(c.manifest["base"], len(image))) == image
    assert c.load(payloads(c.plan, code)[-1]) == ACK
    assert c.read(c.profile["table"]) == c.manifest["symbols"]["hook"] | 1
    assert c.read(0x04000208, 2) == 1


@pytest.mark.parametrize("problem,status", [("revision", 2), ("game", 1), ("hook", 3), ("getter", 4)])
def test_preflight_refuses_without_writing_resident(problem, status):
    c = Console(install=False)
    if problem == "revision":
        c.write(0x080000BC, 0, 1)
    if problem == "game":
        c.write(0x080000AC, 0)
    if problem == "hook":
        c.write(c.profile["table"], 0x0203FC01)
    if problem == "getter":
        c.write(c.profile["seed_getter"] & ~1, 0)
    assert c.load(payloads(c.plan, c.code)[0]) == 0xBAD00000 + status
    assert bytes(c.uc.mem_read(c.manifest["base"], c.manifest["length"])) == bytes(c.manifest["length"])


@pytest.mark.parametrize("missing", [0, 1, 2])
def test_missing_or_corrupted_lead_never_enables_hook(missing):
    c = Console(install=False)
    parts = payloads(c.plan, c.code)
    for i, part in enumerate(parts[:-1]):
        if i != missing:
            assert c.load(part) == ACK
    assert c.load(parts[-1]) == 0xBAD00005
    assert c.read(c.profile["table"]) == c.profile["original"]


def test_corrupted_complete_image_never_enables_hook():
    c = Console(install=False)
    parts = payloads(c.plan, c.code)
    for part in parts[:-1]:
        c.load(part)
    c.write(c.manifest["base"] + 100, 0)
    assert c.load(parts[-1]) == 0xBAD00005
    assert c.read(c.profile["table"]) == c.profile["original"]


@pytest.mark.parametrize("code", PROFILES)
def test_absolute_advances_start_from_title_seed_not_first_overworld(code):
    c = Console(code, criteria=Criteria(shiny=False))
    c.set_overworld(False)
    c.frame()
    assert c.s("status") == 0
    c.write(SEED16, 0x1234, 2)  # Title screen reseed, not the MG epoch.
    c.seed = 0x1234
    c.set_overworld()
    c.frame(3500)
    assert c.s("initial") == 0x1234
    assert c.s("index") == 3500
    assert c.s("target") == 20000
    assert c.s("shown") == int("B0016499", 16)  # 20000 - 3500 - Mewtwo's one advance.
    c.frame(3971)  # More than 64 consumes, e.g. load/extra RNG; no invented zero.
    assert c.s("index") == 3971
    assert c.s("target") == 20000


def test_distance_machine_code_matches_public_lcg_for_all_bits():
    c = Console()
    rng = random.Random(42)
    cases = [0, 1, 2, 3500, 9999999, 0xFFFFFFFF, *(1 << bit for bit in range(32))]
    for n in cases:
        initial = rng.getrandbits(32)
        assert c.call(c.manifest["symbols"]["distance"] | 1, initial, c.lcg.advance(initial, n)) == n


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target", ["mewtwo", "articuno", "zapdos", "moltres"])
def test_exact_nature_six_ivs_and_press_once(code, target):
    seed, index = 0xB8C0, 20000
    mon = predict(Console().lcg.advance(seed, index), 12345, 2791)
    criteria = Criteria(False, mon["nature"], None, mon["ivs"], mon["ivs"])
    c = Console(code, target, criteria=criteria, first=index, last=index)
    c.frame(3500)
    assert c.s("status") == 2
    assert c.s("target") == index
    c.frame(index - c.plan["auto_a_offset_advances"])
    assert c.s("status") == 6
    assert c.main_loop() == 1
    assert c.s("status") == 7
    assert c.read(c.profile["main"]) == c.profile["cb1"]
    assert len(c.presses) == 1
    assert c.presses[0][1]["personality"] == mon["personality"]
    assert c.presses[0][1]["ivs"] == mon["ivs"]
    for n in range(index + 1, index + 6):
        c.frame(n)
        assert c.main_loop() == 0
    assert len(c.presses) == 1


@pytest.mark.parametrize("field", range(6))
def test_each_iv_bound_rejects_independently_in_ui_order(field):
    c = Console()
    mon = predict(c.lcg.advance(c.seed, 20000), 12345, 2791)
    values = list(mon["ivs"])
    values[field] = (values[field] + 1) % 32
    c = Console(
        criteria=Criteria(False, mon["nature"], None, tuple(values), tuple(values)), first=20000, last=20000
    )
    c.frame(3500)
    assert c.s("status") == 3


def test_nature_and_shiny_are_applied_on_console():
    c = Console()
    for index in (20000, 20001, 20002, 20015, 20016, 20017, 30000, 30001):
        seed = c.lcg.advance(c.seed, index)
        assert bool(c.call(c.manifest["symbols"]["matches"] | 1, seed)) == predict(seed, 12345, 2791)["shiny"]
    mon = predict(c.lcg.advance(c.seed, 20000), 12345, 2791)
    c = Console(criteria=Criteria(False, (mon["nature"] + 1) % 25), first=20000, last=20000)
    c.frame(3500)
    assert c.s("status") == 3


@pytest.mark.parametrize("code,target", [("BPRE", "mewtwo"), ("BPGF", "articuno")])
def test_real_shiny_candidate_is_found_over_multiple_batches_and_pressed_once(code, target):
    # Independently locate a positive shiny result instead of testing only random negatives.
    probe = Console(code, target)
    offset, index = probe.plan["auto_a_offset_advances"], 10000
    seed = probe.lcg.advance(probe.seed, index)
    while index < 200000:
        if (index - offset) % 2 == 0 and predict(seed, 12345, 2791)["shiny"]:
            break
        seed = probe.lcg.step(seed)
        index += 1
    assert index < 200000
    c = Console(code, target, first=index - 64, last=index)
    assert c.call(c.manifest["symbols"]["matches"] | 1, seed) == 1
    for current in range(3500, 3540, 2):
        c.frame(current)
        if c.s("status") == 2:
            break
    assert c.s("status") == 2
    generation = c.s("generation")
    assert predict(generation, 12345, 2791)["shiny"]
    c.frame(c.s("target") - offset)
    assert c.main_loop() == 1
    assert len(c.presses) == 1
    assert c.presses[0][1]["shiny"]
    assert c.presses[0][0] == generation


@pytest.mark.parametrize("condition", ["lag", "menu", "not_ready", "passed", "changed_seed", "rewind"])
def test_never_presses_when_target_cannot_be_hit(condition):
    c = Console(criteria=Criteria(shiny=False))
    c.frame(3500)
    at = 19999
    if condition == "menu":
        c.set_overworld(False)
    if condition == "not_ready":
        c.write(c.profile["context"] + 1, 0, 1)
    if condition == "passed":
        at += 1
    if condition == "changed_seed":
        c.write(SEED16, 0x1234, 2)
    if condition == "rewind":
        at = 3000
    c.frame(at, lag=condition == "lag")
    assert c.s("status") in (4, 5)
    if condition in ("lag", "menu", "not_ready", "passed"):
        reason = {"lag": 10, "menu": 4, "not_ready": 3, "passed": 9}[condition]
        assert c.s("reason") == reason
        assert c.s("shown") == 0xD0000000 + int(str(reason), 16)
    if condition != "menu":
        assert c.main_loop() == 0
    assert not c.presses


def test_pending_shim_expires_on_second_interrupt_without_late_press():
    c = Console(criteria=Criteria(shiny=False))
    c.frame(3500)
    c.frame(19999)
    assert c.s("status") == 6
    c.frame(20000, lag=True)
    assert c.s("status") == 4
    assert c.s("shown") == 0xD0000012
    assert c.main_loop() == 0
    assert not c.presses


@pytest.mark.parametrize("change", ["rng", "context", "bird_position", "bird_release_b"])
def test_shim_rechecks_scene_and_rng_after_readkeys(change):
    c = Console(target="zapdos" if change.startswith("bird") else "mewtwo", criteria=Criteria(shiny=False))
    c.frame(3500)
    c.frame(20000 - c.plan["auto_a_offset_advances"])
    if change == "rng":
        c.write(c.profile["rng"], c.lcg.step(c.read(c.profile["rng"])))
    if change == "context":
        c.write(c.profile["context"] + 1, 0, 1)
    if change == "bird_position":
        c.write(c.profile["objects"] + 16, 10, 2)
    if change == "bird_release_b":
        c.write(c.profile["main"] + 0x2C, 0, 2)
    assert c.main_loop() == 0
    assert c.s("status") == 4
    assert c.s("reason") == {"rng": 11, "context": 3, "bird_position": 7, "bird_release_b": 1}[change]


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target", ["articuno", "zapdos", "moltres"])
def test_bird_countdown_without_b_explains_refusal_and_never_presses_late(code, target):
    # User's 0.3.1 report: at the bird, but B was not held. The old overlay
    # kept counting without warning and collapsed every refusal to D0000000.
    c = Console(code, target, criteria=Criteria(shiny=False))
    c.write(c.profile["main"] + 0x2C, 0, 2)
    c.frame(3500)
    assert c.s("status") == 2
    assert c.s("reason") == 1
    assert c.read(c.profile["palette"], 2) == 0x02FF  # Amber: not armed.
    c.frame(19998)
    assert c.s("shown") == 0xD0000001  # B not held at the trigger check.
    assert c.main_loop() == 0
    # Pressing B after the deadline must not arm a late A or overwrite the reason.
    c.write(c.profile["main"] + 0x2C, 2, 2)
    c.frame(20000)
    assert c.s("shown") == 0xD0000001
    assert c.main_loop() == 0
    assert not c.presses


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target", ["articuno", "zapdos", "moltres"])
def test_holding_b_before_deadline_turns_countdown_green_and_enables_exactly_one_a(code, target):
    c = Console(code, target, criteria=Criteria(shiny=False))
    c.write(c.profile["main"] + 0x2C, 0, 2)
    c.frame(3500)
    assert c.read(c.profile["palette"], 2) == 0x02FF
    c.write(c.profile["main"] + 0x2C, 2, 2)
    c.frame(3502)
    assert c.s("reason") == 0
    assert c.read(c.profile["palette"], 2) == 0x03E0
    c.frame(19998)
    assert c.s("status") == 6
    assert c.s("shown") == 0xC0000001  # Scheduled, not yet sent.
    assert not c.presses
    assert c.main_loop() == 1
    c.frame(20000)
    assert c.s("shown") == 0xC0000000
    assert c.main_loop() == 0
    assert len(c.presses) == 1


@pytest.mark.parametrize(
    "problem,reason",
    [("direction_held", 2), ("script", 3), ("target", 5), ("moving", 6), ("facing", 7), ("elevation", 8)],
)
def test_bird_refusal_reports_the_unmet_condition(problem, reason):
    c = Console(target="articuno", criteria=Criteria(shiny=False))
    c.frame(3500)
    objects = c.profile["objects"]
    if problem == "direction_held":
        c.write(c.profile["main"] + 0x2C, 0x42, 2)
    if problem == "script":
        c.write(c.profile["context"] + 1, 1, 1)
    if problem == "target":
        c.write(objects + 36 + 5, 0, 1)
    if problem == "moving":
        c.write(objects, 0x10003)
    if problem == "facing":
        c.write(objects + 24, 1, 1)
    if problem == "elevation":
        c.write(objects + 11, 4, 1)
    c.frame(19998)
    assert c.s("status") == 4
    assert c.s("shown") == 0xD0000000 + reason
    assert c.main_loop() == 0
    assert not c.presses


@pytest.mark.parametrize("player,target", [(0, 3), (3, 0), (0, 0), (3, 3)])
def test_zero_object_elevation_is_compatible_like_the_game(player, target):
    # pret/pokefirered src/event_object_movement.c:ObjectEventDoesElevationMatch:
    # an elevation mismatch rejects only when both elevations are nonzero.
    c = Console(target="articuno", criteria=Criteria(shiny=False))
    c.write(c.profile["objects"] + 11, player, 1)
    c.write(c.profile["objects"] + 36 + 11, target, 1)
    assert c.call(c.manifest["symbols"]["readiness"] | 1) == 0


def test_no_stores_to_rng_pokemon_save_blocks_or_rom():
    c = Console(criteria=Criteria(shiny=False))
    c.frame(3500)
    c.frame(19999)
    c.main_loop()
    p = c.profile
    allowed = [
        (c.manifest["base"], 0x02040000),
        (0x03007800, 0x03007D00),
        (p["main"] + 0x3F8, p["main"] + 0x438),
        (p["main"], p["main"] + 4),
        (p["main"] + 0x2E, p["main"] + 0x30),
        (0x06017E00, 0x06018000),
        (p["palette"], p["palette"] + 4),
        (p["palette"] - 0x400, p["palette"] - 0x3FC),
        (0x04000208, 0x0400020A),
    ]
    assert c.writes
    assert all(
        any(lo <= address and address + size <= hi for lo, hi in allowed) for address, size, value in c.writes
    )


def test_guest_fits_and_payloads_do_not_exceed_protocol_limit():
    c = Console()
    manifest = guest()
    assert manifest["base"] == 0x0203F768
    assert manifest["base"] + manifest["length"] <= 0x02040000
    assert all(len(part) <= 1024 for part in payloads(c.plan, c.code))


def test_stationary_two_advance_stride_reselects_a_reachable_target():
    c = Console(criteria=Criteria(shiny=False), first=20000, last=20005)
    c.frame(3500)
    assert c.s("target") == 20000
    c.frame(3502)
    assert c.s("target") == 20001  # Mewtwo's press index 20000 is reachable from an even index.
    c.frame(20000)
    assert c.main_loop() == 1
    assert c.s("status") == 7


def test_overlay_renders_all_eight_seed_digits_and_the_decimal_count():
    c = Console(criteria=Criteria(shiny=False))
    c.frame(3500)
    font = [
        0x7B6F,
        0x749A,
        0x73E7,
        0x79E7,
        0x49ED,
        0x79CF,
        0x7BCF,
        0x4927,
        0x7BEF,
        0x79EF,
        0x5BEF,
        0x3AEB,
        0x724F,
        0x3B6B,
        0x73CF,
        0x13CF,
    ]
    for row, value in enumerate((c.s("seed"), c.s("shown"))):
        for digit in range(8):
            glyph = font[(value >> (28 - digit * 4)) & 15]
            tile = 0x06017E00 + digit * 64 + row * 32
            for y in range(8):
                bits = glyph >> ((y - 1) * 3) & 7 if 1 <= y <= 5 else 0
                pixels = 0x22222222 - ((bits & 1) << 8) - ((bits & 2) << 11) - ((bits & 4) << 14)
                assert c.read(tile + y * 4) == pixels
    c.write(c.profile["main"] + 0x2C, 0x200, 2)
    c.frame(3502)
    # L changes the values rendered; no rewind or false advance-zero.
    assert c.s("initial") == 0xB8C0
    assert c.s("index") == 3502


@pytest.mark.parametrize(
    "name", ["rng", "main", "cb1", "cb2", "original", "context", "wait", "selected", "table"]
)
@pytest.mark.parametrize("code", PROFILES)
def test_profile_facts_agree_with_pinned_upstream(name, code):
    from pokeldn.frlg.rom.builds import for_game_code

    build = for_game_code(code)
    attributes = {
        "main": "gmain",
        "cb1": "cb1_overworld",
        "cb2": "cb2_overworld",
        "original": "vblank_intr",
        "context": "script_context",
        "wait": "wait_button",
        "selected": "selected_object",
        "table": "intr_vblank",
        "rng": "rng",
    }
    actual = getattr(build, attributes[name]) | (1 if name in ("cb1", "cb2", "original", "wait") else 0)
    assert PROFILES[code][name] == actual
