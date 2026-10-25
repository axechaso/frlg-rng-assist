import pytest

from console import Console, MON_DATA
from test_guest import overlay_values
from test_model_and_records import record
from frlg_rng_assist_core.model import Criteria
from frlg_rng_assist_core.native import PROFILES

pytestmark = pytest.mark.emulation


def expected(values):
    hp, attack, defense, spa, spd, speed = values
    order = hp, attack, defense, speed, spa, spd
    kind = sum((value % 2) * 2 ** i for i, value in enumerate(order)) * 15 // 63 + 1
    power = sum((value // 2 % 2) * 2 ** i for i, value in enumerate(order)) * 40 // 63 + 30
    return tuple(int("".join(f"{v:02d}" for v in row), 16)
                 for row in ((hp, attack, defense, speed), (spa, spd, kind, power)))


@pytest.mark.parametrize("code", PROFILES)
def test_r_decrypts_every_shuffle_from_a_copy_and_updates_the_live_tail(code):
    from pokeldn.frlg.rom import builds

    c = Console(code, "articuno", criteria=Criteria(shiny=False))
    assert MON_DATA[code] == getattr(builds, code).get_mon_data
    assert c.profile["mon_data"] == MON_DATA[code] | 1
    c.write(c.profile["main"] + 0x2C, 0x100, 2)
    values = (31, 1, 22, 13, 4, 25)
    for order in range(24):
        count = order % 6 + 1
        c.write(c.profile["party_count"], count, 1)
        c.uc.mem_write(c.profile["party"] + (count - 1) * 100, record(order, encrypted=True, values=values))
        before = bytes(c.uc.mem_read(c.profile["party"], 600))
        c.frame(3500 + order * 2)
        assert overlay_values(c) == expected(values)
        assert c.read(c.profile["palette"], 2) == 0x7FFF
        assert bytes(c.uc.mem_read(c.profile["party"], 600)) == before
        assert 0x03007800 <= c.mon_reads[-1] < 0x03007D00
    c.write(c.profile["main"] + 0x2C, 0, 2)
    c.frame(3550)
    assert overlay_values(c) == (c.s("seed"), c.s("shown"))


@pytest.mark.parametrize("code", PROFILES)
def test_r_matches_every_hidden_power_bit_pattern_and_boundary_ivs(code):
    c = Console(code, criteria=Criteria(shiny=False))
    c.write(c.profile["party_count"], 1, 1)
    c.write(c.profile["main"] + 0x2C, 0x100, 2)
    for bits in range(64):
        stored = tuple(28 + ((bits >> i) & 1) + (((63 - bits) >> i) & 1) * 2 for i in range(6))
        values = (*stored[:3], stored[4], stored[5], stored[3])
        c.uc.mem_write(c.profile["party"], record(0x12345678 + bits, encrypted=True, values=values))
        c.frame(3500 + bits * 2)
        assert overlay_values(c) == expected(values)


@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("bad", ["checksum", "bad-egg", "no-species", "empty", "invalid-count"])
def test_r_rejects_invalid_records_without_touching_the_live_party(code, bad):
    c = Console(code, criteria=Criteria(shiny=False))
    raw = bytearray(record(encrypted=True))
    if bad == "checksum":
        raw[44] ^= 1
    if bad == "bad-egg":
        raw[19] |= 1
    if bad == "no-species":
        raw[19] &= ~2
    c.uc.mem_write(c.profile["party"], bytes(raw))
    c.write(c.profile["party_count"], 0 if bad == "empty" else 7 if bad == "invalid-count" else 1, 1)
    before = bytes(c.uc.mem_read(c.profile["party"], 600))
    c.write(c.profile["main"] + 0x2C, 0x100, 2)
    c.frame(3500)
    assert overlay_values(c) == (0xFFFFFFFF, 0xFFFFFFFF)
    assert bytes(c.uc.mem_read(c.profile["party"], 600)) == before
    if bad in ("empty", "invalid-count"):
        assert c.mon_reads == []


@pytest.mark.parametrize("target", ["articuno", "sweet-land", "hooh"])
def test_r_keeps_counting_and_fires_exactly_one_input_in_maps_and_menus(target):
    c = Console(target=target, criteria=Criteria(shiny=False))
    c.uc.mem_write(c.profile["party"], record(encrypted=True, values=(31,) * 6))
    c.write(c.profile["party_count"], 1, 1)
    c.frame(3500)
    for i in range(100):
        if c.s("status") == 2:
            break
        c.frame(3502 + i * 2)
    if target == "sweet-land":
        c.set_overworld(False)
    c.write(c.profile["main"] + 0x2C, 0x100, 2)
    deadline = c.s("target") - c.plan["auto_a_offset_advances"]
    c.frame(deadline)
    assert overlay_values(c) == expected((31,) * 6)
    assert c.main_loop() == c.plan["trigger_key_mask"]
    c.frame(deadline + 2)
    assert c.main_loop() == 0 and len(c.inputs) == 1


def test_overlay_patches_hardware_after_the_game_oam_copy_without_editing_the_buffer():
    c = Console(criteria=Criteria(shiny=False))
    original = bytes([0x33]) * 1024
    c.uc.mem_write(c.profile["main"] + 0x38, original)
    c.frame(3500)
    assert bytes(c.uc.mem_read(c.profile["main"] + 0x38, 1024)) == original
    assert bytes(c.uc.mem_read(0x07000000, 960)) == original[:960]
    for i in range(8):
        assert c.read(0x070003C0 + i * 8, 2) == 0x8002
        assert c.read(0x070003C2 + i * 8, 2) == 174 + i * 8
        assert c.read(0x070003C4 + i * 8, 2) == 0xF3F0 + i * 2
    c.set_overworld(False)
    c.frame(3502)
    assert bytes(c.uc.mem_read(0x07000000, 1024)) == original
