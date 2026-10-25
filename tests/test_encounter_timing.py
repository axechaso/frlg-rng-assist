import pytest

from frlg_rng_assist_core.backend import backend, predict
from frlg_rng_assist_core.model import Criteria
from frlg_rng_assist_core.native import PROFILES
from console import Console
from encounter_timing import generation_trace


@pytest.mark.parametrize("target,passes,draws", [
    ("mewtwo", 2, 3), ("articuno", 3, 5), ("zapdos", 3, 5), ("moltres", 3, 5),
])
def test_script_yields_include_rfu_draws_on_every_pass(target, passes, draws):
    lcg, _ = backend()
    result, trace = generation_trace(0x12345678, target, lcg)
    assert sum(name.endswith(":rfu") for name, _ in trace) == passes
    assert sum(name.endswith(":vblank") for name, _ in trace) == passes - 1
    assert sum("native_complete_return" in name for name, _ in trace) == 1
    assert result == lcg.advance(0x12345678, draws)
    assert trace[-1][0] == f"{passes - 1}:setwildbattle"


def test_c76f_report_reproduces_3351_target_generating_3354_with_old_offset():
    lcg, _ = backend()
    intended = predict(lcg.advance(0xC76F, 3351), 0, 0)
    actual, trace = generation_trace(lcg.advance(0xC76F, 3349), "articuno", lcg)
    assert intended["personality"] == 0x1D138B25
    assert predict(actual, 0, 0)["personality"] == 0x4762A09B
    assert lcg.distance(0xC76F, actual) == 3354
    assert [name for name, _ in trace] == [
        "post_vblank", "0:rfu", "0:lock_yield_task_complete", "1:vblank", "1:rfu",
        "1:native_complete_return", "2:vblank", "2:rfu", "2:setwildbattle",
    ]


@pytest.mark.emulation
@pytest.mark.parametrize("code", PROFILES)
def test_c76f_fixed_deadline_is_green_and_generates_the_3351_pid(code):
    lcg, _ = backend()
    intended = predict(lcg.advance(0xC76F, 3351), 12345, 2791)
    criteria = Criteria(False, intended["nature"], None, intended["ivs"], intended["ivs"])
    c = Console(code, "articuno", initial=0xC76F, index=3000, first=3351, last=3351, criteria=criteria)
    c.frame(3300)
    c.frame(3302)
    assert c.s("target") == 3351
    assert c.s("shown") == 0xB0000044
    assert c.read(c.profile["palette"], 2) == 0x03E0
    for current in range(3304, 3347, 2):
        c.frame(current)
        if current < 3346:
            assert c.read(c.profile["palette"], 2) == 0x03E0
            assert c.main_loop() == 0
    assert c.s("index") == 3346
    assert c.s("status") == 6
    assert c.main_loop() == 1
    assert c.presses[0][0] == lcg.advance(0xC76F, 3351)
    assert c.presses[0][1]["personality"] == 0x1D138B25
    assert c.presses[0][1]["ivs"] == intended["ivs"]
    c.frame(3353)
    assert c.main_loop() == 0
    assert len(c.presses) == 1


@pytest.mark.emulation
@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("offset,press,actual", [(0, 3349, 3354), (3, 3346, 3351), (4, 3345, 3350)])
def test_custom_offset_changes_press_and_colour_without_moving_generation_target(code, offset, press, actual):
    lcg, _ = backend()
    intended = predict(lcg.advance(0xC76F, 3351), 12345, 2791)
    criteria = Criteria(False, intended["nature"], None, intended["ivs"], intended["ivs"])
    c = Console(code, "articuno", initial=0xC76F, first=3351, last=3351, criteria=criteria, offset=offset)
    start = 3300 + (press & 1)
    c.frame(start)
    c.frame(start + 2)
    assert c.s("target") == 3351
    assert c.s("generation") == lcg.advance(0xC76F, 3351)
    assert c.read(c.profile["palette"], 2) == 0x03E0
    c.frame(press - 1)
    assert c.read(c.profile["palette"], 2) == 0x02FF
    c.frame(press)
    assert c.main_loop() == 1
    assert c.presses[0][0] == lcg.advance(0xC76F, actual)
    assert c.plan["offset_advances"] == offset
    assert c.plan["auto_a_offset_advances"] == offset + 2
