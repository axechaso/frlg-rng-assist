"""Verified search vectors plus real guest execution in synthetic memory.

These checks do not certify the plugin's physical throw delay. The offset of
the supplied SysBot / EasyCon tool is deliberately not marked plugin-verified.
"""

from dataclasses import replace
from math import isqrt
from pathlib import Path
from types import SimpleNamespace

import pytest

import install
import plugin
from console import Console
from frlg_rng_assist_core.backend import backend
from frlg_rng_assist_core.capture import ULTRA_THRESHOLD, THRESHOLD, check_band, find_window, settings
from frlg_rng_assist_core.model import Criteria
from frlg_rng_assist_core.native import guest, payloads
from test_wild import finish_match, reference


def test_fixed_minimum_threshold_matches_game_integer_formula():
    # catchRate=3, normal ball=10, full HP, no status -> odds=1.
    assert 1048560 // isqrt(isqrt(16711680)) == THRESHOLD == 16643
    assert settings(True)["threshold"] == THRESHOLD
    assert settings(True, ball="ultra")["threshold"] == ULTRA_THRESHOLD == 19784


def test_ultra_ball_guest_uses_the_higher_threshold():
    pre = 0x9B4FDE3A  # first five high halves: 4499,15779,19309,17049,1860
    normal = Console(criteria=Criteria(shiny=False), capture=True)
    ultra = Console(criteria=Criteria(shiny=False), capture=True, capture_ball="ultra")
    for c in (normal, ultra):
        generate(c)
        c.set_overworld(False)
        arm(c, c.s("index") + 20)
        c.s("next", 1234)
    assert normal.call(normal.manifest["symbols"]["matches"] | 1, pre) == 0
    assert normal.s("next") == 1234
    assert ultra.call(ultra.manifest["symbols"]["matches"] | 1, pre) == 1
    assert ultra.s("next") == 1235


def test_v27g_verified_legacy_capture_vector_and_minimum_rate():
    # run_selftest() in the user's frlg_easycon_capture_calibrator_v27g.py.
    assert check_band(0xCA532E6A, 242, 245)
    lcg, _ = backend()
    pre = lcg.advance(0xCA532E6A, 243)
    assert all(roll < THRESHOLD for roll in lcg.draws(pre, 4)[0])


def test_capture_uses_the_middle_of_a_three_start_success_run():
    c = Console(criteria=Criteria(shiny=False), capture=True)
    generate(c)
    c.set_overworld(False)
    arm(c, c.s("index") + 20)
    c.s("next", 1234)
    before = c.s("next")
    # Six passing draws contain three overlapping four-draw success starts.
    # Capture selection advances once, to the centre of that three-start run.
    pre = 0xA420C7D4
    assert c.call(c.manifest["symbols"]["matches"] | 1, pre) == 1
    assert c.s("next") == before + 1


def test_threshold_equality_is_a_failure():
    lcg, _ = backend()
    # Force the first draw's high half to be exactly the threshold.
    pre = lcg.advance(THRESHOLD << 16, 0xFFFFFFFF)
    assert not check_band(pre, 0, 0)


@pytest.mark.parametrize("seed", [0, 0xFFFF, 0xABCDEF01, 0xCA532E6A])
@pytest.mark.parametrize("lo,hi", [(0, 0), (1, 1), (241, 241), (242, 245), (0, 12)])
def test_entire_band_equals_four_rolls_at_each_possible_start(seed, lo, hi):
    lcg, _ = backend()
    for index in range(100):
        cursor = lcg.advance(seed, index)
        expected = all(all(roll < THRESHOLD for roll in lcg.draws(lcg.advance(cursor, offset), 4)[0])
                       for offset in range(lo, hi + 1))
        assert check_band(cursor, lo, hi) == expected


@pytest.mark.parametrize("first,last", [(-1, 1), (1, 0), (0, 13), (True, 1), (0, 65533)])
def test_bad_offset_band_is_refused_before_injection(first, last):
    with pytest.raises(ValueError):
        settings(True, first, last)


def test_offline_window_scans_inclusively():
    index = find_window(0xB8C0, 3000, 30000)
    assert index is not None
    assert find_window(0xB8C0, index, index) == index
    assert find_window(0xB8C0, index - 1, index - 1) is None


def arm(c, index):
    c.write(c.profile["main"] + 0x2C, 0x104, 2)
    c.write(c.profile["main"] + 0x2E, 4, 2)
    c.frame(index)
    c.write(c.profile["main"] + 0x2C, 0, 2)
    c.write(c.profile["main"] + 0x2E, 0, 2)


def generate(c):
    first = 3500 + ((c.plan["range"]["first"] - c.plan["auto_a_offset_advances"]) & 1)
    for index in range(first, first + 1000, 2):
        c.frame(index)
        if c.s("status") == 2:
            break
        assert c.s("status") == 1 and c.main_loop() == 0
    assert c.s("status") == 2
    c.frame(c.s("target") - c.plan["auto_a_offset_advances"])
    c.main_loop()
    assert c.s("status") == 7


def find(c):
    for _ in range(20000):
        if c.s("status") == 2:
            return
        assert c.s("status") == 1
        c.frame(c.s("index") + 2)
        assert c.main_loop() == 0
    pytest.fail("capture window was not found")


@pytest.mark.parametrize("code", ["BPRE", "BPGE", "BPRF", "BPGF"])
@pytest.mark.parametrize("offset,upper", [(0, 0), (241, 241), (242, 245)])
def test_generation_then_capture_without_reinstall_or_reseed(code, offset, upper):
    c = Console(code, criteria=Criteria(shiny=False), first=20000, last=20000,
                capture=True, capture_offset=offset, capture_offset_max=upper)
    generate(c)
    initial = c.s("initial")
    c.set_overworld(False)  # Final bag confirmation, not the battle-main callback.
    arm(c, c.s("index") + 20)
    assert c.s("status") in (1, 2)
    assert c.s("initial") == initial
    assert c.s("shown") >> 28 in (8, 9)
    find(c)
    target = c.s("target")
    c.frame(target - offset - 1)
    assert c.s("status") == 6
    assert c.main_loop() & 1
    assert c.s("status") == 7
    assert check_band(c.inputs[-1][1], offset, upper)
    count = len(c.inputs)
    for _ in range(20):
        c.frame(c.s("index") + 2)
        assert c.main_loop() == 0
    assert len(c.inputs) == count
    assert c.s("initial") == initial
    assert c.s("shown") == 0xC0000000


def test_r_select_does_not_interrupt_generation_or_enable_an_unloaded_feature():
    for preload in (False, True):
        c = Console(criteria=Criteria(shiny=False), capture=preload)
        arm(c, 3500)
        assert c.s("status") == 2 and c.s("shown") >> 28 == 11
        generate(c)
        if not preload:
            arm(c, c.s("index") + 20)
            assert c.s("status") == 7


def test_capture_cancel_rearm_and_one_key_edge_preserve_the_encounter_epoch():
    c = Console(criteria=Criteria(shiny=False), capture=True)
    generate(c)
    c.set_overworld(False)
    arm(c, c.s("index") + 20)
    arm(c, c.s("index") + 2)
    assert c.s("status") == 3 and c.s("shown") == 0xE0000000
    for _ in range(5):
        c.frame(c.s("index") + 2)
        assert c.main_loop() == 0
    arm(c, c.s("index") + 2)
    assert c.s("status") in (1, 2)
    c.write(c.profile["main"] + 0x2C, 0x104, 2)  # Held, not a new SELECT.
    c.frame(c.s("index") + 2)
    assert c.s("status") in (1, 2)


def test_capture_miss_has_a_red_notice_then_retries():
    c = Console(criteria=Criteria(shiny=False), capture=True)
    generate(c)
    c.set_overworld(False)
    arm(c, c.s("index") + 20)
    find(c)
    c.frame(c.s("target") - 242 + 1)
    assert c.s("status") == 4 and c.s("shown") == 0xD0000009
    assert c.main_loop() == 0
    c.resume_after_notice()
    find(c)
    c.frame(c.s("target") - 242)
    assert c.main_loop() == 1


def test_reset_invalidates_capture_before_any_input():
    c = Console(criteria=Criteria(shiny=False), capture=True)
    generate(c)
    c.set_overworld(False)
    arm(c, c.s("index") + 20)
    c.frame(100)
    assert c.s("status") == 5
    arm(c, 102)
    assert c.s("status") == 5 and c.main_loop() == 0


@pytest.mark.parametrize("code", ["BPRE", "BPGE", "BPRF", "BPGF"])
@pytest.mark.parametrize("target", ["sweet-land", "unown"])
@pytest.mark.parametrize("method", [1, 2, 4])
def test_specialized_generation_keeps_nature_and_ivs_before_capture(code, target, method):
    lcg, _ = backend()
    seed = lcg.advance(0xB8C0, 20000)
    pid, ivs, _ = reference(seed, method, unown=target == "unown")
    c = Console(code, target, method=method, capture=True,
                criteria=Criteria(False, pid % 25, iv_min=ivs, iv_max=ivs))
    negative = Console(code, target, method=method, capture=True,
                       criteria=Criteria(False, (pid % 25 + 1) % 25))
    assert finish_match(negative, seed) == 0
    # Switch after a completed generation; every specialized payload must now
    # match the very same conservative capture model, without PID rejection.
    generate(c)
    c.set_overworld(False)
    arm(c, c.s("index") + 20)
    assert c.s("status") in (1, 2)
    pre = c.lcg.advance(0xCA532E6A, 242)
    assert c.call(c.manifest["symbols"]["matches"] | 1, pre) == 1


@pytest.mark.parametrize("target", ["mewtwo", "sweet-land", "unown"])
def test_each_resident_variant_and_transfer_stays_within_verified_memory(target):
    c = Console(target=target, capture=True)
    image = guest(c.plan)
    assert image["base"] + image["length"] <= 0x02040000
    assert image["length"] > 1024
    assert all(len(part) <= 1024 for part in payloads(c.plan, c.code))


def test_hooh_capture_uses_a_instead_of_the_generation_up_key():
    c = Console(target="hooh", criteria=Criteria(shiny=False), capture=True)
    generate(c)
    assert c.input_keys[-1][1] == 64
    c.set_overworld(False)
    arm(c, c.s("index") + 20)
    find(c)
    c.frame(c.s("target") - 242)
    assert c.main_loop() == 1
    assert c.input_keys[-1][1] == 1


@pytest.mark.parametrize("rfu_calls", [0, 2])
def test_capture_final_seed_recheck_rejects_an_unexpected_draw(rfu_calls):
    c = Console(criteria=Criteria(shiny=False), capture=True)
    generate(c)
    c.set_overworld(False)
    arm(c, c.s("index") + 20)
    find(c)
    c.frame(c.s("target") - 242)
    assert c.s("status") == 6
    assert c.main_loop(rfu_calls=rfu_calls) == 0
    assert c.s("status") == 4 and c.s("shown") != 0xC0000000
    c.frame(c.s("index") + 2)
    assert c.s("shown") == 0xD0000011


def test_capture_never_writes_rng_pokemon_saves_or_rom():
    c = Console(criteria=Criteria(shiny=False), capture=True)
    generate(c)
    c.set_overworld(False)
    arm(c, c.s("index") + 20)
    find(c)
    c.frame(c.s("target") - 242)
    assert c.main_loop() == 1
    p = c.profile
    allowed = [(c.manifest["base"], 0x02040000), (0x03007800, 0x03007D00),
               (0x070003C0, 0x07000400), (p["main"], p["main"] + 8),
               (p["main"] + 0x2C, p["main"] + 0x30), (0x06017E00, 0x06018000),
               (p["palette"], p["palette"] + 4), (p["palette"] - 0x400, p["palette"] - 0x3FC),
               (0x04000208, 0x0400020A)]
    assert c.writes and all(any(lo <= at and at + size <= hi for lo, hi in allowed)
                            for at, size, value in c.writes)


def test_capture_stops_at_the_absolute_tracking_limit():
    c = Console(criteria=Criteria(shiny=False), capture=True)
    generate(c)
    c.set_overworld(False)
    arm(c, 9999990)
    assert c.s("status") == 3
    assert c.main_loop() == 0


@pytest.mark.parametrize("language", ["zh", "ja", "en"])
@pytest.mark.parametrize("logging", [False, True])
def test_capture_fields_work_with_real_host_command_builder(monkeypatch, language, logging, tmp_path):
    from pokeldn.app import command, i18n
    monkeypatch.setattr(i18n, "locale", lambda: language)
    tools = []
    plugin.register(SimpleNamespace(add_tool=lambda game, tool: tools.append(tool)))
    tool = replace(tools[0], script=str(Path(install.__file__)))
    values = {"--capture-rng": True, "--capture-ball": "ultra",
              "--capture-offset": "242", "--capture-offset-max": "245"}
    assert command.applies(next(f for f in tool.fields if f.flag == "--capture-offset"), tool, values)
    host = SimpleNamespace(received="", keys="", capture=logging, language=2, gender=0,
                           ids=lambda game: (12345, 2791), name=lambda game: "TEST")
    assert not command.problems(tool, values)
    argv = command.build(tool, values, {}, host)
    assert "--capture" not in argv  # Reserved by the host for a capture log filename.
    args = install.build_parser().parse_args(argv)
    assert args.capture and args.capture_ball == "ultra" and (args.capture_offset, args.capture_offset_max) == (242, 245)
    values["--capture-rng"] = False
    assert not command.applies(next(f for f in tool.fields if f.flag == "--capture-offset"), tool, values)
    args = install.build_parser().parse_args(command.build(tool, values, {}, host))
    assert not args.capture
