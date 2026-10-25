"""Model arithmetic and compiled input hooks; substitute callbacks, not a game-ROM run."""

from pathlib import Path

import pytest

from frlg_rng_assist_core.encounters import ENCOUNTERS, UNOWN_CHAMBERS, default_offset
from frlg_rng_assist_core.model import Criteria, search
from frlg_rng_assist_core.native import PROFILES, install_plan, resident
from frlg_rng_assist_core.pk3 import choose_record, decode_mon, party_records
from frlg_rng_assist_core.verification import verify
from frlg_rng_assist_core.wild import predict_wild, recover_wild, slot_from, unown_letter
from console import Console
from test_model_and_records import record


def reference(seed, method=1, *, unown=False, letters=UNOWN_CHAMBERS["monean"]):
    # Direct control-flow transcription of the decompilation's random-call order.
    # It does not use the plugin or public predictor to generate the expected PID / IVs.
    def draw():
        nonlocal seed
        seed = (1103515245 * seed + 24691) & 0xFFFFFFFF
        return seed >> 16

    slot_roll = draw() % 100
    draw()  # level
    if unown:
        slot = sum(slot_roll >= threshold for threshold in (20, 40, 50, 60, 70, 80, 85, 90, 94, 98, 99))
        wanted = letters[slot]
    else:
        wanted = draw() % 25
    rerolls = 0
    while True:
        lo, hi = draw(), draw()
        if unown:
            lo, hi = hi, lo
        pid = lo + hi * 65536
        letter = (((pid >> 24) & 3) * 64 + ((pid >> 16) & 3) * 16
                  + ((pid >> 8) & 3) * 4 + (pid & 3)) % 28
        if (letter if unown else pid % 25) == wanted:
            break
        rerolls += 1
    if method == 2:
        draw()
    first = draw()
    if method == 4:
        draw()
    second = draw()
    ivs = (first & 31, first >> 5 & 31, first >> 10 & 31,
           second >> 5 & 31, second >> 10 & 31, second & 31)
    return pid, ivs, rerolls


@pytest.mark.parametrize("method", [1, 2, 4])
@pytest.mark.parametrize("chamber", [None, *UNOWN_CHAMBERS])
def test_wild_prediction_and_reverse_match_independent_random_call_order(method, chamber):
    model = "wild" if chamber is None else "unown"
    chamber = chamber or "monean"
    for seed in (0xC76F, 0x12345678, 0xDEADBEEF):
        pid, ivs, rerolls = reference(seed, method, unown=model == "unown", letters=UNOWN_CHAMBERS[chamber])
        mon = predict_wild(seed, 12345, 2791, method, model=model, chamber=chamber)
        assert (mon["personality"], mon["ivs"], mon["rerolls"]) == (pid, ivs, rerolls)
        assert mon["pid_offset"] == 2 + (model == "wild") + rerolls * 2
        assert {"generation_seed": seed, "method": method, "pid_seed": mon["pid_seed"]} in recover_wild(
            pid, ivs, model=model, chamber=chamber)
        for state in recover_wild(pid, ivs, model=model, chamber=chamber):
            other = predict_wild(state["generation_seed"], 12345, 2791, state["method"],
                                 model=model, chamber=chamber)
            assert (other["personality"], other["ivs"]) == (pid, ivs)


@pytest.mark.parametrize("area,roll,slot", [
    ("land", 0, 0), ("land", 19, 0), ("land", 20, 1), ("land", 99, 11),
    ("surf", 59, 0), ("surf", 60, 1), ("surf", 99, 4),
    ("old", 69, 0), ("old", 70, 1), ("good", 0, 2), ("good", 99, 4),
    ("super", 39, 5), ("super", 40, 6), ("super", 99, 9),
])
def test_encounter_slots(area, roll, slot):
    assert slot_from(roll, area) == slot


@pytest.mark.parametrize("target", ENCOUNTERS)
def test_each_target_has_a_bounded_plan_and_buildable_guest(target):
    plan = install_plan("firered", "BPRE", target)
    assert plan["offset_advances"] == default_offset(target)
    assert plan["auto_a_offset_advances"] == ENCOUNTERS[target].offset
    assert len(resident(plan, "BPRE")) <= 2200
    assert not plan["hardware_tested"]


def test_actual_host_form_prefills_only_the_selected_targets_offset():
    import plugin
    from scripts.release_smoke import check_catalog_offsets

    class Catalog:
        tools = []

        def add_tool(self, game, tool):
            self.tools.append(tool)

    catalog = Catalog()
    plugin.register(catalog)
    check_catalog_offsets(next(t for t in catalog.tools if t.key == "frlg-rng-assist-install"),
                          Path(plugin.__file__).parent)


@pytest.mark.parametrize("target,model,chamber", [
    ("sweet-land", "wild", "monean"), ("fish-super", "wild", "monean"),
    ("unown", "unown", "rixy"),
])
@pytest.mark.parametrize("method", [1, 2, 4])
def test_offline_and_capture_use_the_same_wild_start_boundary(target, model, chamber, method):
    c = Console(target=target, chamber=chamber, method=method)
    seed = c.lcg.advance(c.seed, 20000)
    mon = predict_wild(seed, 12345, 2791, method, model=model, chamber=chamber)
    report = search(c.seed, 12345, 2791, start=20000, advances=1, model=model, method=method,
                    chamber=chamber, criteria=Criteria(False, pid=mon["personality"]))
    assert report["seed_boundary"] == "before_encounter_slot_draw"
    assert report["targets"][0]["pid"] == mon["personality"]
    species = ENCOUNTERS[target].species or 25
    actual = decode_mon(record(mon["personality"], species=species, values=mon["ivs"]), encrypted=False)
    verified = verify(actual, "firered", target, shiny=False, method=method, chamber=chamber,
                      initial_seed=c.seed, search_range={"first": 20000, "last": 20000})
    assert verified["status"] == "matched" and verified["range_verified"]


def test_generic_capture_selects_party_tail_and_explicit_slot_still_wins():
    records = party_records(bytes((2, 0, 0, 0)) + record(encrypted=True, species=150)
                            + record(encrypted=True, species=25) + bytes(404))
    assert choose_record(records, 0)["species"] == 25
    assert choose_record(records, 0, 1)["species"] == 150


def finish_match(c, seed):
    for _ in range(256):
        value = c.call(c.manifest["symbols"]["matches"] | 1, seed)
        if value != 0xFFFFFFFF:
            return value
    pytest.fail("wild candidate did not complete its resumed search")


@pytest.mark.emulation
@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target,chamber", [("sweet-land", "monean"), ("unown", "weepth")])
@pytest.mark.parametrize("method", [1, 2, 4])
def test_compiled_wild_search_checks_positive_and_negative_nature_and_all_six_ivs(code, target, chamber, method):
    seed = 0xDEADBEEF
    expected = reference(seed, method, unown=target == "unown", letters=UNOWN_CHAMBERS[chamber])
    pid, ivs, _ = expected
    criteria = Criteria(False, pid % 25, iv_min=ivs, iv_max=ivs)
    c = Console(code, target, criteria=criteria, method=method, chamber=chamber)
    assert finish_match(c, seed) == 1
    for index in range(6):
        bad = list(ivs)
        bad[index] = (bad[index] + 1) % 32
        negative = Console(code, target, method=method, chamber=chamber,
                           criteria=Criteria(False, pid % 25, iv_min=tuple(bad), iv_max=tuple(bad)))
        assert finish_match(negative, seed) == 0


@pytest.mark.emulation
@pytest.mark.parametrize("target", ["sweet-land", "unown"])
def test_long_pid_rejection_resumes_over_interrupts_without_losing_candidate(target):
    # This search locates a long rejection chain independently; the guest must not
    # truncate the result at its per-interrupt work budget of eight PID pairs.
    c = Console(target=target, criteria=Criteria(shiny=False), first=20000, last=20000)
    for seed in range(100):
        pid, ivs, rerolls = reference(seed, unown=target == "unown")
        if rerolls >= 32:
            break
    assert rerolls >= 32
    assert c.call(c.manifest["symbols"]["matches"] | 1, seed) == 0xFFFFFFFF
    assert c.s("work_active") == 1
    assert finish_match(c, seed) == 1
    assert c.s("work_active") == 0
    assert unown_letter(pid) < 28


@pytest.mark.emulation
@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target", ENCOUNTERS)
def test_all_targets_send_one_input_without_button_object_or_script_gates(code, target):
    c = Console(code, target, criteria=Criteria(shiny=False))
    c.frame(3500)
    for index in range(1, 100):
        if c.s("status") == 2:
            break
        c.frame(3500 + 2 * index)
    assert c.s("status") == 2
    c.uc.mem_write(c.profile["objects"], bytes(16 * 36))
    c.write(c.profile["context"] + 1, 0, 1)
    c.write(c.profile["selected"], 255, 1)
    c.write(c.profile["main"] + 0x2C, 0, 2)
    deadline = c.s("target") - c.plan["auto_a_offset_advances"]
    c.frame(deadline)
    assert c.s("status") == 6
    assert c.main_loop() == ENCOUNTERS[target].button
    assert c.s("status") == 7 and len(c.inputs) == 1
    assert c.inputs[0][1] == c.lcg.advance(c.seed, deadline + 1)
    assert c.input_keys == [(ENCOUNTERS[target].button, ENCOUNTERS[target].button)]
    c.frame(deadline + 2)
    assert c.main_loop() == 0
    assert len(c.inputs) == 1


@pytest.mark.emulation
@pytest.mark.parametrize("code", PROFILES)
def test_hooh_sends_up_as_both_new_and_held_input_and_releases_next_loop(code):
    c = Console(code, "hooh", criteria=Criteria(shiny=False))
    assert c.plan["trigger_button"] == "UP" and c.plan["offset_advances"] == 379
    c.frame(3500)
    c.frame(20000 - c.plan["auto_a_offset_advances"])
    assert c.main_loop() == 0x40
    assert c.input_keys == [(0x40, 0x40)]
    assert not c.read(c.profile["main"] + 0x2C, 4) & 0x10001
    c.frame(20000)
    assert c.main_loop() == 0
    assert c.read(c.profile["main"] + 0x2C, 4) == 0
    assert len(c.inputs) == 1


@pytest.mark.emulation
@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("target", ["sweet-land", "sweet-surf", "fish-old", "fish-good", "fish-super", "unown"])
def test_menu_targets_wrap_and_restore_callback2_once(code, target):
    c = Console(code, target, criteria=Criteria(shiny=False))
    c.frame(3500)  # Establish the actual title seed on the map first.
    c.set_overworld(False)
    original = c.read(c.profile["main"] + 4)
    for index in range(1, 100):
        if c.s("status") == 2:
            break
        c.frame(3500 + index * 2)
    deadline = c.s("target") - c.plan["auto_a_offset_advances"]
    c.frame(deadline)
    assert c.s("status") == 6
    assert c.read(c.profile["main"]) == 0
    from test_guest import overlay_values

    assert overlay_values(c) == (c.s("seed"), 0xC0000001)
    assert c.read(c.profile["main"] + 4) == c.manifest["symbols"]["press_shim"] | 1
    assert c.main_loop() == 1
    assert c.read(c.profile["main"] + 4) == original
    assert len(c.inputs) == 1 and c.s("status") == 7
    c.frame(deadline + 2)
    assert c.main_loop() == 0 and len(c.inputs) == 1


@pytest.mark.emulation
@pytest.mark.parametrize("code", PROFILES)
def test_large_offset_catchup_uses_a_jump_and_stays_within_interrupt_budget(code):
    c = Console(code, "deoxys", criteria=Criteria(shiny=False), offset=65533, first=0, last=500000)
    before = c.instructions
    c.frame(3500)
    assert c.instructions - before < 20000
    assert c.s("target") == 3500 + 65535 + 1
    assert c.s("generation") == c.lcg.advance(c.seed, c.s("target"))
    c.frame(3501)
    assert c.main_loop() == 1 and c.s("status") == 7


@pytest.mark.emulation
@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("blocked", ["title", "battle", "missing_callback"])
def test_menu_input_waits_for_map_activation_and_rejects_battle_or_missing_callback(code, blocked):
    c = Console(code, "sweet-land", criteria=Criteria(shiny=False))
    if blocked != "title":
        c.frame(3500)
        for index in range(1, 100):
            if c.s("status") == 2:
                break
            c.frame(3500 + 2 * index)
        assert c.s("status") == 2
    c.set_overworld(False)
    if blocked != "title":
        c.write(c.profile["main"] + 4, c.profile["battle_cb2"] if blocked == "battle" else 0)
    c.frame(19999 if blocked == "title" else c.s("target") - c.plan["auto_a_offset_advances"])
    assert c.s("status") == (0 if blocked == "title" else 4)
    assert c.main_loop() == 0 and not c.inputs


@pytest.mark.emulation
@pytest.mark.parametrize("code", PROFILES)
def test_menu_shim_expiry_retains_a_replacement_callback_and_retries_after_notice(code):
    c = Console(code, "sweet-land", criteria=Criteria(shiny=False))
    c.frame(3500)
    for index in range(1, 100):
        if c.s("status") == 2:
            break
        c.frame(3500 + 2 * index)
    assert c.s("status") == 2
    c.set_overworld(False)
    deadline = c.s("target") - c.plan["auto_a_offset_advances"]
    c.frame(deadline)
    assert c.s("status") == 6
    c.write(c.profile["main"] + 4, c.profile["cb2"])
    c.frame(deadline + 1)
    assert c.s("shown") == 0xD0000012
    assert c.read(c.profile["main"] + 4) == c.profile["cb2"]
    c.set_overworld()
    c.resume_after_notice()
    assert c.s("status") in (1, 2) and not c.inputs


@pytest.mark.emulation
@pytest.mark.parametrize("target", ["sweet-land", "unown"])
def test_wild_shiny_filter_accepts_trainer_xor_and_rejects_another_sid(target):
    c = Console(target=target)
    pid, _, _ = reference(0xC76F, unown=target == "unown")
    sid = 12345 ^ (pid >> 16) ^ (pid & 0xFFFF)
    c.write(c.read(c.profile["sb2ptr"]) + 12, sid, 2)
    assert finish_match(c, 0xC76F) == 1
    c.write(c.read(c.profile["sb2ptr"]) + 12, sid ^ 8, 2)
    assert finish_match(c, 0xC76F) == 0


@pytest.mark.emulation
def test_compact_decimal_renderer_handles_carries_through_the_maximum_index():
    from test_guest import overlay_values

    c = Console(criteria=Criteria(shiny=False))
    c.write(c.profile["main"] + 0x2C, 0x200, 2)
    for index in (1, 9, 10, 99, 100, 999, 1000, 999999, 1000000, 9999999):
        c.frame(index)
        assert overlay_values(c) == (c.seed, int(str(index), 16))
