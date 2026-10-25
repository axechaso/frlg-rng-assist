"""Versioned encounter facts and execution of the actual compiled species filter."""

import json
from pathlib import Path

import pytest

import install
from console import Console, SB2
from test_wild import finish_match, reference
from frlg_rng_assist_core.backend import backend
from frlg_rng_assist_core.lookup import lookup
from frlg_rng_assist_core.model import Criteria
from frlg_rng_assist_core.native import PROFILES, install_plan
from frlg_rng_assist_core.wild import predict_wild
from frlg_rng_assist_core.wild_tables import available_species, names, species_mask, tables


def accepted(target, game, location, species):
    mask = int.from_bytes(species_mask(target, game, location, species), "little")
    return {roll for roll in range(100) if mask >> roll & 1}


def test_committed_snapshots_have_both_versions_and_valid_national_ids():
    data = tables()
    assert len(data) == 132
    lengths = {"land_mons": 12, "water_mons": 5, "rock_smash_mons": 5, "fishing_mons": 10}
    for row in data.values():
        assert set(row["labels"]) == {"zh", "en", "ja"}
        for game in ("firered", "leafgreen"):
            for field, mons in row[game].items():
                assert len(mons) == lengths[field]
                assert all(1 <= species <= 386 and 1 <= low <= high <= 100 for species, low, high in mons)
    for language in ("en", "ja", "zh"):
        assert len(names()[language]) == 387 and names()[language][0] == ""
        assert len(names()["natures"][language]) == 25
    assert [names()[lang][25] for lang in ("en", "ja", "zh")] == ["Pikachu", "ピカチュウ", "皮卡丘"]


@pytest.mark.parametrize("game", ["firered", "leafgreen"])
def test_percentile_boundaries_against_known_land_tables(game):
    pidgey = set(range(20)) | set(range(40, 50)) | set(range(60, 70)) | set(range(80, 85)) | set(range(90, 94)) | {98}
    assert accepted("sweet-land", game, "route-1", 16) == pidgey
    assert accepted("sweet-land", game, "route-1", 19) == set(range(100)) - pidgey
    assert accepted("sweet-land", game, "viridian-forest", 25) == {94, 95, 96, 97, 99}
    assert accepted("sweet-land", game, "diglett-cave", 51) == {94, 95, 96, 97, 99}


@pytest.mark.parametrize("game,surf_species", [("firered", 54), ("leafgreen", 79)])
def test_safari_surf_and_individual_rods_use_the_correct_tables(game, surf_species):
    location = "safari-zone-center"
    assert accepted("sweet-surf", game, location, surf_species) == set(range(100))
    assert available_species("fish-old", game, location) == (129,)
    assert available_species("fish-good", game, location) == (60, 118, 129)
    assert available_species("fish-super", game, location) == tuple(sorted((118, 119, 147, surf_species, 148)))
    assert accepted("fish-good", game, location, 60) == set(range(80, 100))
    assert accepted("fish-super", game, location, 147) == set(range(80, 95))
    assert accepted("fish-super", game, location, 148) == {99}


def test_version_exclusive_species_are_not_silently_matched_in_the_other_game():
    assert accepted("sweet-land", "firered", "power-plant", 125) == {94, 95, 96, 97, 99}
    with pytest.raises(ValueError, match="没有这种宝可梦"):
        species_mask("sweet-land", "leafgreen", "power-plant", 125)
    with pytest.raises(ValueError, match="没有这种宝可梦"):
        species_mask("sweet-surf", "leafgreen", "safari-zone-center", 54)


def test_unown_uses_its_letter_model_instead_of_ordinary_species_search():
    from frlg_rng_assist_core.encounters import WILD_LOCATIONS

    assert not any("CHAMBER" in tables().get(key, {}).get("map", "") for key, _ in WILD_LOCATIONS)
    with pytest.raises(ValueError, match="未知图腾.*类别"):
        install_plan("firered", "auto", "sweet-land", species=201)


@pytest.mark.parametrize("location", ["other", "mt-moon", "safari-zone", "route-21"])
def test_species_filter_requires_a_concrete_unambiguous_area(location):
    with pytest.raises(ValueError, match="具体楼层"):
        install_plan("firered", "auto", "sweet-land", location=location, species=16)
    # Older offset-only / unknown locations still work when no species is requested.
    assert install_plan("firered", "auto", "sweet-land", location=location)["slot_roll_mask"] == "ff" * 12 + "0f"


@pytest.mark.parametrize("target,location,species", [
    ("fish-old", "route-1", 129), ("sweet-land", "route-1", 25), ("mewtwo", "other", 150),
])
def test_invalid_species_selection_is_refused_before_creating_any_files(target, location, species, tmp_path):
    with pytest.raises(SystemExit) as error:
        install.main(["--preview", "--target", target, "--location", location, "--species", str(species),
                      "--output", str(tmp_path / "bad.json")])
    assert error.value.code == 2 and not list(tmp_path.iterdir())


@pytest.mark.emulation
@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("method", [1, 2, 4])
def test_compiled_filter_uses_every_percentile_without_changing_the_rng_sequence(code, method):
    console = Console(code, "sweet-land", location="route-1", species=16, method=method,
                      criteria=Criteria(False))
    lcg, _ = backend()
    # Set the first draw to each boundary value directly. These are independent
    # hand-copied slots from the actual Route 1 table, not the generated bitmask.
    pidgey = set(range(20)) | set(range(40, 50)) | set(range(60, 70)) | set(range(80, 85)) | set(range(90, 94)) | {98}
    for roll in range(100):
        seed = lcg.unstep(roll << 16)
        assert finish_match(console, seed) == int(roll in pidgey)
    assert console.plan["wild_species"] == 16


@pytest.mark.emulation
@pytest.mark.parametrize("code", PROFILES)
@pytest.mark.parametrize("method", [1, 2, 4])
def test_species_shiny_nature_and_all_six_ivs_are_combined_on_the_console(code, method):
    lcg, _ = backend()
    seed = lcg.unstep(10 << 16)  # Route 1's first slot: Pidgey.
    pid, ivs, _ = reference(seed, method)
    criteria = Criteria(True, pid % 25, iv_min=ivs, iv_max=ivs)

    def configured(species=16, chosen=criteria):
        c = Console(code, "sweet-land", location="route-1", species=species, method=method, criteria=chosen)
        c.write(SB2 + 12, (pid & 0xFFFF) ^ (pid >> 16) ^ 12345, 2)
        return c

    positive = configured()
    assert finish_match(positive, seed) == 1
    assert finish_match(configured(19), seed) == 0  # Same PID / IVs, wrong species.
    positive.write(SB2 + 12, positive.read(SB2 + 12, 2) ^ 8, 2)
    assert finish_match(positive, seed) == 0  # Same species / IVs, non-shiny.
    assert finish_match(configured(chosen=Criteria(False, (pid % 25 + 1) % 25)), seed) == 0
    for index in range(6):
        wrong = list(ivs)
        wrong[index] = (wrong[index] + 1) % 32
        c = configured(chosen=Criteria(True, pid % 25, iv_min=tuple(wrong), iv_max=tuple(wrong)))
        assert finish_match(c, seed) == 0


@pytest.mark.parametrize("target,location,species,other", [
    ("sweet-land", "route-1", 16, 19), ("fish-good", "safari-zone-center", 60, 118),
    ("fish-super", "safari-zone-center", 147, 119),
])
@pytest.mark.parametrize("method", [1, 2, 4])
def test_manual_pid_reverse_filters_species_at_the_same_encounter_start(target, location, species, other, method):
    lcg, _ = backend()
    initial = 0xC76F
    from frlg_rng_assist_core.wild_tables import area_for

    for advance in range(20000, 21000):
        seed = lcg.advance(initial, advance)
        if (lcg.step(seed) >> 16) % 100 in accepted(target, "firered", location, species):
            break
    mon = predict_wild(seed, 0, 0, method, area=area_for(target))
    result = lookup(initial, mon["personality"], target, location=location, species=species,
                    first=advance, last=advance, method=method)
    assert result["result"] == "unique"
    assert result["candidates"][0]["predicted_species"] == species
    assert result["candidates"][0]["predicted_ivs"] == mon["ivs"]
    assert lookup(initial, mon["personality"], target, location=location, species=other,
                  first=advance, last=advance, method=method)["result"] == "no_match"


def test_saved_preview_carries_the_actual_species_mask(tmp_path):
    output = tmp_path / "species.json"
    assert install.main(["--preview", "--category", "wild", "--target-wild", "sweet-land",
                         "--location", "viridian-forest", "--species", "25", "--output", str(output)]) == 0
    plan = json.loads(output.read_text(encoding="utf-8"))
    assert plan["wild_species"] == 25
    assert bytes.fromhex(plan["slot_roll_mask"]) == species_mask("sweet-land", "firered", "viridian-forest", 25)
    assert Path(plan["gift"]["path"]).is_file()
