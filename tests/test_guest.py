import random
import struct

import pytest
from unicorn import UC_HOOK_MEM_READ

from frlg_rng_assist_core.backend import predict
from frlg_rng_assist_core.model import Criteria
from frlg_rng_assist_core.native import ACK, PROFILES, guest, payloads, resident
from console import Console, ROM_GETTERS, SEED16

pytestmark = pytest.mark.emulation


def overlay_values(c):
    """Read both visible numbers from their rendered OBJ pixels."""
    glyphs = (0x7B6F, 0x749A, 0x73E7, 0x79E7, 0x49ED, 0x79CF, 0x7BCF, 0x4927,
              0x7BEF, 0x79EF, 0x5BEF, 0x3AEB, 0x724F, 0x3B6B, 0x73CF, 0x13CF)
    values = []
    for row in range(2):
        value = 0
        for digit in range(8):
            glyph = 0
            for y in range(5):
                pixels = c.read(0x06017E00 + digit * 64 + row * 32 + (y + 1) * 4)
                for x in range(3):
                    if (pixels >> (8 + 4 * x)) & 15 == 1:
                        glyph |= 1 << (y * 3 + x)
            value = (value << 4) | glyphs.index(glyph)
        values.append(value)
    return tuple(values)


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("count", range(1, 7))
def test_lr_reads_last_live_party_pid_for_every_party_size_and_restores_countdown(code, count):
    from pokeldn.frlg.rom.rom_map import GPLAYER_PARTY, GPLAYER_PARTY_COUNT

    c = Console(code, "articuno", criteria=Criteria(shiny=False))
    assert c.profile["party"] == GPLAYER_PARTY
    assert c.profile["party_count"] == GPLAYER_PARTY_COUNT
    pids = (0x00123456, 0x89ABCDEF, 0xDEADBEEF, 0xA0000000, 0xFFFFFFFF, 0)
    for slot, pid in enumerate(pids):
        c.write(GPLAYER_PARTY + slot * 100, pid)
    c.write(GPLAYER_PARTY_COUNT, 0xEFCDAB00 | count)  # Only the count byte is valid.
    before = bytes(c.uc.mem_read(GPLAYER_PARTY, 600))
    c.write(c.profile["main"] + 0x2C, 0x300, 2)
    c.frame(3500)
    assert overlay_values(c) == (pids[count - 1], count)
    assert c.read(c.profile["palette"], 2) == 0x7FFF
    assert c.s("index") == 3500
    assert c.s("target") == 20000
    c.write(c.profile["main"] + 0x2C, 0x100, 2)  # R alone restores normal display.
    c.frame(3502)
    assert overlay_values(c) == (c.s("seed"), c.s("shown"))
    assert c.s("shown") == 0xB0016496
    c.write(c.profile["main"] + 0x2C, 0, 2)
    c.frame(3504)
    assert overlay_values(c) == (c.s("seed"), c.s("shown"))
    assert c.s("initial") == c.seed
    assert bytes(c.uc.mem_read(GPLAYER_PARTY, 600)) == before
    assert c.read(GPLAYER_PARTY_COUNT) == 0xEFCDAB00 | count


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("count", [0, 7, 255])
def test_lr_empty_or_invalid_count_reads_no_party_entry(code, count):
    from pokeldn.frlg.rom.rom_map import GPLAYER_PARTY_COUNT

    c = Console(code, "articuno", criteria=Criteria(shiny=False))
    c.write(GPLAYER_PARTY_COUNT, 0xBEEF0000 | count)
    c.write(c.profile["main"] + 0x2C, 0x300, 2)
    reads = []
    c.uc.hook_add(UC_HOOK_MEM_READ, lambda uc, access, at, size, value, user: reads.append((at, size)),
                  begin=0x02024000, end=0x0202B000)
    c.frame(3500)
    assert overlay_values(c) == (0xFFFFFFFF, 0)
    assert reads == [(GPLAYER_PARTY_COUNT, 1)]
    assert c.s("target") == 20000


@pytest.mark.parametrize("code", PROFILES)
def test_lr_refreshes_pid_and_party_size_live_and_returns_to_l_view_when_r_is_released(code):
    from pokeldn.frlg.rom.rom_map import GPLAYER_PARTY, GPLAYER_PARTY_COUNT

    c = Console(code, "articuno", criteria=Criteria(shiny=False))
    c.write(GPLAYER_PARTY_COUNT, 2, 1)
    c.write(GPLAYER_PARTY, 0x11112222)
    c.write(GPLAYER_PARTY + 100, 0xAABBCCDD)
    c.write(c.profile["main"] + 0x2C, 0x300, 2)  # R + L: PID view.
    c.frame(3500)
    assert overlay_values(c) == (0xAABBCCDD, 2)
    c.write(GPLAYER_PARTY + 100, 0x0000FFFF)
    c.frame(3502)
    assert overlay_values(c) == (0x0000FFFF, 2)
    c.write(GPLAYER_PARTY_COUNT, 1, 1)
    c.frame(3504)
    assert overlay_values(c) == (0x11112222, 1)
    c.write(c.profile["main"] + 0x2C, 0x200, 2)  # R released: existing L view.
    c.frame(3506)
    assert overlay_values(c) == (c.seed, 0x3506)
    assert c.s("target") == 20000


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target", ["mewtwo", "articuno", "zapdos", "moltres"])
def test_viewing_pid_does_not_pause_or_repeat_the_scheduled_a(code, target):
    c = Console(code, target, criteria=Criteria(shiny=False))
    c.write(c.profile["party_count"], 1, 1)
    c.write(c.profile["party"], 0x10203040)
    c.write(c.profile["main"] + 0x2C, 0x300, 2)
    c.frame(3500)
    c.frame(20000 - c.plan["auto_a_offset_advances"])
    assert overlay_values(c) == (0x10203040, 1)
    assert c.main_loop() == 1
    assert c.presses[0][0] == c.lcg.advance(c.seed, 20000)
    c.frame(20002)
    assert overlay_values(c) == (0x10203040, 1)
    assert c.main_loop() == 0
    c.write(c.profile["main"] + 0x2C, 0, 2)
    c.frame(20004)
    assert overlay_values(c) == (c.s("seed"), 0xC0000000)
    assert len(c.presses) == 1


@pytest.mark.parametrize("code", PROFILES)
def test_lr_does_not_draw_over_a_menu(code):
    c = Console(code, "articuno", criteria=Criteria(shiny=False))
    c.frame(3500)
    before = bytes(c.uc.mem_read(0x06017E00, 512))
    c.set_overworld(False)
    c.write(c.profile["main"] + 0x2C, 0x300, 2)
    c.frame(3502)
    assert bytes(c.uc.mem_read(0x06017E00, 512)) == before


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target", ["mewtwo", "articuno", "zapdos", "moltres"])
def test_wireless_link_draw_before_callback_is_expected_and_preserves_generation_seed(code, target):
    c = Console(code, target, criteria=Criteria(shiny=False))
    # Independent measured post-VBlank deadlines, rather than deriving the
    # encounter's remaining script consumption from the configured offset.
    deadline = 19999 if target == "mewtwo" else 19998
    c.frame(3500)
    c.frame(deadline)
    assert c.s("status") == 6
    assert c.s("seed") == c.lcg.advance(c.seed, deadline)
    assert c.main_loop() == 1
    assert c.phases[-3:] == [
        ("vblank", c.lcg.advance(c.seed, deadline)),
        ("link", c.lcg.advance(c.seed, deadline + 1)),
        ("callback1_a", c.lcg.advance(c.seed, deadline + 1)),
    ]
    assert c.s("status") == 7
    assert c.read(c.profile["main"]) == c.profile["cb1"]
    assert c.presses[0][0] == c.s("generation") == c.lcg.advance(c.seed, 20000)
    c.frame(20002)
    assert c.main_loop() == 0
    assert len(c.presses) == 1


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target", ["mewtwo", "articuno", "zapdos", "moltres"])
@pytest.mark.parametrize("rfu_calls", [0, 2, 3])
def test_callback_rejects_missing_or_additional_draws_instead_of_pressing_the_wrong_seed(code, target, rfu_calls):
    c = Console(code, target, criteria=Criteria(shiny=False))
    deadline = 19999 if target == "mewtwo" else 19998
    c.frame(3500)
    c.frame(deadline)
    assert c.s("status") == 6
    assert c.main_loop(rfu_calls=rfu_calls) == 0
    assert c.s("status") == 4
    assert c.s("reason") == 11
    assert c.read(c.profile["main"]) == c.profile["cb1"]
    assert not c.presses


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
    assert c.s("shown") == int("A0020000", 16)  # Candidate is not a visible countdown until confirmed.
    c.frame(3971)  # More than 64 consumes, e.g. load/extra RNG; no invented zero.
    assert c.s("index") == 3971
    assert c.s("target") == 20000
    assert c.s("shown") == int("B0016028", 16)  # 20000 - 3971 - Mewtwo's one advance.


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


@pytest.mark.parametrize("change", ["rng", "context", "bird_scene"])
def test_shim_rechecks_scene_and_rng_after_readkeys(change):
    c = Console(target="zapdos" if change.startswith("bird") else "mewtwo", criteria=Criteria(shiny=False))
    c.frame(3500)
    c.frame(20000 - c.plan["auto_a_offset_advances"])
    if change == "rng":
        c.write(c.profile["rng"], c.lcg.step(c.read(c.profile["rng"])))
    if change == "context":
        c.write(c.profile["context"] + 1, 0, 1)
    if change == "bird_scene":
        c.write(c.profile["main"] + 4, 0x0807C419)
    assert c.main_loop() == 0
    assert c.s("status") == 4
    assert c.s("reason") == {"rng": 11, "context": 3, "bird_scene": 4}[change]


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target", ["articuno", "zapdos", "moltres"])
def test_birds_press_once_at_deadline_without_any_held_button(code, target):
    # The intended workflow is to walk into place and let go of the controls.
    # The old B gate refused this hardware attempt instead of sending A.
    c = Console(code, target, criteria=Criteria(shiny=False))
    assert c.read(c.profile["main"] + 0x2C, 2) == 0
    c.frame(3500)
    assert c.s("status") == 2
    assert c.s("reason") == 0
    assert c.s("shown") == 0xA0020000  # One provisional sample, not yet the fixed B countdown.
    assert c.read(c.profile["palette"], 2) == 0x7FFF
    c.frame(3502)
    assert c.s("locked") == 1
    assert c.s("shown") == 0xB0016496
    assert c.read(c.profile["palette"], 2) == 0x03E0
    assert c.main_loop() == 0  # Never press before the selected advance.
    c.frame(19998)
    assert c.s("shown") == 0xC0000001
    assert not c.presses
    assert c.main_loop() == 1
    assert c.read(c.profile["main"] + 0x2C, 2) == 0
    c.frame(20000)
    assert c.s("shown") == 0xC0000000
    assert c.main_loop() == 0
    assert len(c.presses) == 1


@pytest.mark.parametrize("target", ["articuno", "zapdos", "moltres"])
@pytest.mark.parametrize("when", ["before_deadline", "after_readkeys"])
@pytest.mark.parametrize(
    "change", ["direction_held", "script", "no_objects", "moving", "position", "facing", "elevation"]
)
def test_birds_do_not_gate_a_on_controls_or_player_and_target_state(target, when, change):
    # Positioning is the user's responsibility, including changes between the
    # VBlank schedule and the callback after ReadKeys. No hidden arming gate.
    c = Console(target=target, criteria=Criteria(shiny=False))
    c.frame(3500)
    if when == "after_readkeys":
        c.frame(19998)
        assert c.s("status") == 6
    objects = c.profile["objects"]
    if change == "direction_held":
        c.write(c.profile["main"] + 0x2C, 0x40, 2)
    if change == "script":
        c.write(c.profile["context"] + 1, 1, 1)
    if change == "no_objects":
        c.uc.mem_write(objects, bytes(16 * 36))
        c.write(c.profile["selected"], 255, 1)
    if change == "moving":
        c.write(objects, 0x10003)
    if change == "position":
        c.write(objects + 16, 10, 2)
    if change == "facing":
        c.write(objects + 24, 1, 1)
    if change == "elevation":
        c.write(objects + 11, 4, 1)
    if when == "before_deadline":
        c.frame(19998)
    assert c.s("status") == 6
    assert c.main_loop() == 1
    assert c.s("status") == 7
    assert len(c.presses) == 1


@pytest.mark.parametrize("held", [0, 0x100, 0x300])
def test_no_stores_to_rng_pokemon_save_blocks_or_rom(held):
    c = Console(criteria=Criteria(shiny=False))
    c.write(c.profile["party_count"], 6, 1)
    c.write(c.profile["main"] + 0x2C, held, 2)
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
    assert c.s("shown") == 0xA0020000
    c.frame(3502)
    assert c.s("target") == 20001  # Mewtwo's press index 20000 is reachable from an even index.
    assert c.s("shown") == 0xB0016498
    assert c.s("locked") == 1
    c.frame(20000)
    assert c.main_loop() == 1
    assert c.s("status") == 7


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target", ["mewtwo", "articuno", "zapdos", "moltres"])
def test_visible_countdown_keeps_its_target_through_transient_stride_changes(code, target):
    probe = Console(code, target)
    mon = predict(probe.lcg.advance(probe.seed, 20000), 12345, 2791)
    criteria = Criteria(False, mon["nature"], None, mon["ivs"], mon["ivs"])
    c = Console(code, target, criteria=criteria, first=20000, last=21000)
    press = 20000 - c.plan["auto_a_offset_advances"]
    start = 3500 + (press & 1)
    c.frame(start)
    c.frame(start + 2)
    assert c.s("shown") >> 28 == 0xB
    # A one-call interval changes parity; a later one-call interval restores it.
    # Version 0.3.3 discards the reachable target at press-5 and shows A again.
    for current in (press - 8, press - 7, press - 5, press - 4, press - 2):
        c.frame(current)
        assert c.s("shown") >> 28 == 0xB
        assert c.s("target") == 20000
        assert c.read(c.profile["palette"], 2) == (0x02FF if (press - current) & 1 else 0x03E0)
        assert c.main_loop() == 0
    c.frame(press)
    assert c.main_loop() == 1
    assert len(c.presses) == 1
    assert c.presses[0][0] == c.lcg.advance(c.seed, 20000)


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target", ["mewtwo", "articuno", "zapdos", "moltres"])
def test_miss_reason_is_red_and_readable_for_sixty_map_frames_before_retry(code, target):
    c = Console(code, target, criteria=Criteria(shiny=False), first=20000, last=21000)
    offset = c.plan["auto_a_offset_advances"]
    start = 3500 + ((20000 - offset) & 1)
    c.frame(start)
    c.frame(start + 2)
    deadline = c.s("target") - offset
    c.frame(deadline + 1)
    for frame in range(60):
        if frame:
            c.frame(c.s("index") + 2)
        assert c.s("shown") == 0xD0000009
        assert c.read(c.profile["palette"], 2) == 0x001F
        assert c.s("initial") == c.seed
        assert c.s("target") == 20000
        assert c.main_loop() == 0
    c.frame(c.s("index") + 2)
    assert c.s("shown") >> 28 in (0xA, 0xB)
    assert c.s("target") > 20000
    c.frame(c.s("target") - offset)
    assert c.main_loop() == 1
    assert len(c.presses) == 1


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("held", [0x200, 0x300])
def test_seed_and_pid_views_do_not_consume_a_hidden_miss_reason(code, held):
    c = Console(code, "articuno", criteria=Criteria(shiny=False), first=20000, last=21000)
    c.frame(3500)
    c.frame(3502)
    c.frame(19999)
    assert c.s("shown") == 0xD0000009
    c.write(c.profile["main"] + 0x2C, held, 2)
    for _ in range(90):
        c.frame(c.s("index") + 2)
        assert c.s("status") == 4
        assert c.main_loop() == 0
    c.write(c.profile["main"] + 0x2C, 0, 2)
    for _ in range(59):
        c.frame(c.s("index") + 2)
        assert c.s("shown") == 0xD0000009
        assert c.read(c.profile["palette"], 2) == 0x001F
    c.frame(c.s("index") + 2)
    assert c.s("shown") >> 28 in (0xA, 0xB)
    assert not c.presses


@pytest.mark.parametrize("code", PROFILES)
def test_r_alone_does_not_hide_or_pause_the_miss_notice(code):
    c = Console(code, "articuno", criteria=Criteria(shiny=False), first=20000, last=21000)
    c.frame(3500)
    c.frame(19999)
    notice = c.s("notice")
    c.write(c.profile["main"] + 0x2C, 0x100, 2)
    c.frame(20001)
    assert c.s("notice") == notice - 1
    assert overlay_values(c) == (c.s("seed"), 0xD0000009)
    assert c.read(c.profile["palette"], 2) == 0x001F


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target", ["mewtwo", "articuno", "zapdos", "moltres"])
def test_tv_bursts_keep_a_future_target_and_report_an_overrun_after_returning_to_map(code, target):
    # TeachyTvBg2AnimController calls Random 12 * 26 times per update;
    # the substitute VBlank adds one more. This models consumption and scene
    # changes, not the TV's actual ROM callbacks or console cycle timing.
    c = Console(code, target, criteria=Criteria(shiny=False), first=50000, last=100000)
    offset = c.plan["auto_a_offset_advances"]
    start = 3500 + ((50000 - offset) & 1)
    c.frame(start)
    c.frame(start + 2)
    generation = c.s("generation")
    assert c.s("shown") >> 28 == 0xB
    c.set_overworld(False)
    for _ in range(64):
        c.frame(c.s("index") + 313)
        assert c.s("target") == 50000
        assert c.s("generation") == generation
        assert c.s("status") == 2
    c.set_overworld()
    c.frame(c.s("index") + 2)
    assert c.s("shown") >> 28 == 0xB
    assert c.s("target") == 50000
    c.set_overworld(False)
    c.frame(50000 - offset + 1)
    for _ in range(90):
        c.frame(c.s("index") + 313)
        assert c.s("status") == 4
    c.set_overworld()
    c.set_ready()
    for _ in range(60):
        c.frame(c.s("index") + 2)
        assert c.s("shown") == 0xD0000009
        assert c.read(c.profile["palette"], 2) == 0x001F
        assert c.main_loop() == 0
    c.frame(c.s("index") + 2)
    assert c.s("shown") >> 28 in (0xA, 0xB)
    assert c.s("target") > c.s("index") + offset
    assert c.s("generation") == c.lcg.advance(c.seed, c.s("target"))
    c.frame(c.s("target") - offset)
    assert c.main_loop() == 1
    assert len(c.presses) == 1


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target", ["mewtwo", "articuno", "zapdos", "moltres"])
def test_visible_countdown_retries_only_after_an_actual_miss_and_hits_the_range_endpoint(code, target):
    c = Console(code, target, criteria=Criteria(shiny=False), first=20000, last=20123)
    press = 20000 - c.plan["auto_a_offset_advances"]
    start = 3500 + (press & 1)
    c.frame(start)
    c.frame(start + 2)
    assert c.s("shown") >> 28 == 0xB
    for current in (press - 8, press - 7, press - 5, press - 3, press - 1):
        c.frame(current)
        assert c.s("shown") >> 28 == 0xB
        assert c.s("target") == 20000
        assert c.main_loop() == 0
    c.frame(press + 1)  # The engine really skipped past the exact press advance.
    assert c.s("shown") == 0xD0000009
    assert c.main_loop() == 0
    c.resume_after_notice()
    assert c.s("status") == 2
    assert c.s("target") == c.plan["range"]["last"] == 20123
    assert c.s("generation") == c.lcg.advance(c.seed, 20123)
    assert c.s("shown") == 0xB0000002
    assert c.main_loop() == 0
    assert not c.presses
    c.frame(20123 - c.plan["auto_a_offset_advances"])
    assert c.main_loop() == 1
    assert c.s("initial") == c.seed
    assert c.s("status") == 7
    assert c.presses[0][0] == c.lcg.advance(c.seed, 20123)
    for index in (20124, 20126, 20128):
        c.frame(index)
        assert c.main_loop() == 0
    assert len(c.presses) == 1


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target", ["mewtwo", "articuno", "zapdos", "moltres"])
def test_repeated_misses_keep_searching_until_one_future_candidate_is_pressed(code, target):
    c = Console(code, target, criteria=Criteria(shiny=False), first=20000, last=21000)
    offset = c.plan["auto_a_offset_advances"]
    c.frame(3500 + ((20000 - offset) & 1))
    for attempt in range(4):
        deadline = c.s("target") - offset
        c.frame(deadline - 2)
        assert c.main_loop() == 0
        c.frame(deadline + 1)
        assert c.s("shown") == 0xD0000009
        assert c.main_loop() == 0
        assert not c.presses
        c.resume_after_notice()
        assert c.s("status") == 2
        assert 20000 < c.s("target") <= 21000
        assert c.s("target") - offset > c.s("index")
        assert c.s("generation") == c.lcg.advance(c.seed, c.s("target"))
        assert c.main_loop() == 0
    generation = c.s("generation")
    c.frame(c.s("target") - offset)
    assert c.main_loop() == 1
    assert c.presses[0][0] == generation
    assert c.s("initial") == c.seed
    c.frame(c.s("index") + 2)
    assert c.main_loop() == 0
    assert len(c.presses) == 1


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target", ["mewtwo", "articuno", "zapdos", "moltres"])
def test_retry_never_extends_the_configured_range_when_all_candidates_are_past(code, target):
    c = Console(code, target, criteria=Criteria(shiny=False), first=20000, last=20000)
    c.frame(3500)
    deadline = 20000 - c.plan["auto_a_offset_advances"]
    c.frame(deadline + 1)
    assert c.s("shown") == 0xD0000009
    c.resume_after_notice()
    assert c.s("shown") == 0xE0000000
    assert c.main_loop() == 0
    c.frame(c.s("index") + 2)
    assert c.s("shown") == 0xE0000000
    assert c.main_loop() == 0
    assert not c.presses


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("problem", ["lag", "menu", "script", "target", "rng", "expired"])
def test_recoverable_failures_resume_search_and_stale_shims_cannot_rearm_after_success(code, problem):
    c = Console(code, criteria=Criteria(shiny=False), first=20000, last=21000)
    c.frame(3501)
    deadline, reason = 19999, {"lag": 10, "menu": 4, "script": 3, "target": 5, "rng": 11, "expired": 12}[problem]
    if problem == "menu":
        c.set_overworld(False)
    if problem == "script":
        c.write(c.profile["context"] + 1, 0, 1)
    if problem == "target":
        c.write(c.profile["objects"] + 36 + 5, 0, 1)
    c.frame(deadline, lag=problem == "lag")
    if problem == "rng":
        c.write(c.profile["rng"], c.lcg.step(c.read(c.profile["rng"])))
        assert c.main_loop() == 0
        c.frame(deadline + 1)
    elif problem == "expired":
        c.frame(deadline + 1, lag=True)
    assert c.s("shown") == 0xD0000000 + int(str(reason), 16)
    assert not c.presses
    if problem == "menu":
        c.frame(deadline + 2)
        assert c.s("status") == 4  # Wait for the map callback before resuming.
        c.set_overworld()
    c.set_ready()
    c.resume_after_notice()
    assert c.s("status") == 2
    assert c.s("target") > 20000
    assert c.main_loop() == 0
    generation = c.s("generation")
    c.frame(c.s("target") - 1)
    assert c.main_loop() == 1
    assert c.s("status") == 7
    assert c.presses[0][0] == generation
    # A callback address retained by an interrupted caller must not turn FIRED
    # back into MISSED, which would otherwise permit a second automatic A.
    c.write(c.profile["main"] + 0x2E, 0, 2)
    c.call(c.manifest["symbols"]["press_shim"] | 1)
    assert c.s("status") == 7
    c.frame(c.s("index") + 2)
    assert c.s("shown") == 0xC0000000
    assert c.main_loop() == 0
    assert len(c.presses) == 1


@pytest.mark.parametrize("problem", ["reseed", "rewind"])
def test_retry_does_not_cross_an_invalid_rng_epoch(problem):
    c = Console(criteria=Criteria(shiny=False))
    c.frame(3501)
    c.frame(20000)
    assert c.s("shown") == 0xD0000009
    if problem == "reseed":
        c.write(SEED16, 0x1234, 2)
        c.frame(20002)
    else:
        c.frame(3501)
    assert c.s("shown") == 0xF0000000
    assert c.main_loop() == 0
    c.frame(20004)
    assert c.s("shown") == 0xF0000000
    assert c.main_loop() == 0
    assert not c.presses


@pytest.mark.parametrize("code,target", [("BPRE", "articuno"), ("BPGF", "mewtwo")])
@pytest.mark.parametrize("filter_kind", ["shiny", "nature_and_ivs"])
def test_retry_preserves_filters_and_rebases_from_the_live_rng_after_a_large_skip(code, target, filter_kind):
    probe = Console(code, target)
    offset = probe.plan["auto_a_offset_advances"]
    mon = predict(probe.lcg.advance(probe.seed, 20000), 12345, 2791)
    criteria = Criteria() if filter_kind == "shiny" else Criteria(
        False, mon["nature"], None,
        tuple(max(0, value - 8) for value in mon["ivs"]),
        tuple(min(31, value + 8) for value in mon["ivs"]),
    )
    candidates, seed = [], probe.lcg.advance(probe.seed, 20000)
    for index in range(20000, 200000):
        if (index - offset) % 2 == 0 and criteria.matches(predict(seed, 12345, 2791)):
            if not candidates:
                candidates.append(index)
            elif index - candidates[0] < 256:
                candidates[0] = index
            else:
                candidates.append(index)
                break
        seed = probe.lcg.step(seed)
    assert len(candidates) == 2
    first, last = candidates
    c = Console(code, target, criteria=criteria, first=first, last=last)
    c.frame(3500)
    c.frame(3502)
    assert c.s("target") == first
    assert c.s("shown") >> 28 == 0xB
    c.frame(last - offset - 160)  # Large skip, with room for the visible notice before the next target.
    assert c.s("shown") == 0xD0000009
    assert c.main_loop() == 0
    c.resume_after_notice()
    while c.s("status") == 1 and c.s("index") < last - offset:
        c.frame(c.s("index") + 2)
    assert c.s("target") == last
    assert c.s("generation") == c.lcg.advance(c.seed, last)
    c.frame(last - offset)
    assert c.main_loop() == 1
    assert len(c.presses) == 1
    assert criteria.matches(c.presses[0][1])
    assert c.presses[0][0] == c.lcg.advance(c.seed, last)


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
