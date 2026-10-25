import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

import install
import lookup as lookup_tool
from frlg_rng_assist_core.backend import backend, predict
from frlg_rng_assist_core.encounters import CATEGORIES, WILD_LOCATIONS, default_offset
from frlg_rng_assist_core.lookup import distance, hidden_power, lookup
from frlg_rng_assist_core.native import install_plan
from frlg_rng_assist_core.wild import predict_wild


def test_only_search_and_manual_pid_lookup_are_registered():
    import plugin

    class Catalog:
        tools = []

        def add_tool(self, game, tool):
            self.tools.append(tool)

    catalog = Catalog()
    plugin.register(catalog)
    assert [t.key for t in catalog.tools] == ["frlg-rng-assist-install", "frlg-rng-assist-lookup"]
    fields = {f.flag: f for f in catalog.tools[1].fields}
    assert fields["--initial-seed"].kind == fields["--pid"].kind == "text"
    assert fields["--initial-seed"].required and fields["--pid"].required
    assert not fields["--initial-seed"].default and not fields["--pid"].default


@pytest.mark.parametrize("tool_key", ["frlg-rng-assist-install", "frlg-rng-assist-lookup"])
@pytest.mark.parametrize("offset", ["", "0", "17"])
def test_host_form_accepts_optional_blank_numbers_and_preserves_zero(tool_key, offset):
    import plugin
    from pokeldn.app import command

    tools = []
    plugin.register(SimpleNamespace(add_tool=lambda game, tool: tools.append(tool)))
    registered = next(tool for tool in tools if tool.key == tool_key)
    root = Path(__file__).resolve().parent.parent
    tool = replace(registered, script=str(root / registered.script))
    settings = SimpleNamespace(received="", keys="", capture=False, language=2, gender=0,
                               ids=lambda game: (12345, 2791), name=lambda game: "TEST")
    values = {"--offset": offset, "--initial-seed": "C76F", "--pid": "4762A09B"}
    assert not command.problems(tool, values)
    parser = install.build_parser() if tool_key.endswith("install") else lookup_tool.build_parser()
    parsed = parser.parse_args(command.build(tool, values, {}, settings))
    assert parsed.offset == (None if offset == "" else int(offset))
    if tool_key.endswith("lookup"):
        assert parsed.target_advance is None
        values["--target-advance"] = "0"
        assert not command.problems(tool, values)
        assert parser.parse_args(command.build(tool, values, {}, settings)).target_advance == 0


@pytest.mark.parametrize("flag,value", [("--offset", "65534"), ("--target-advance", "10000000")])
def test_optional_lookup_numbers_still_reject_out_of_bounds_before_reporting(flag, value, tmp_path):
    with pytest.raises(SystemExit) as error:
        lookup_tool.main(["--initial-seed", "C76F", "--pid", "4762A09B", flag, value,
                          "--output", str(tmp_path / "bad.json")])
    assert error.value.code == 2
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("category", [c for c in CATEGORIES if c not in ("wild", "unown")])
def test_every_static_category_rejects_method_two_before_export(category, tmp_path):
    with pytest.raises(SystemExit) as error:
        install.main(["--preview", "--category", category, "--method", "2", "--output", str(tmp_path / "bad.json")])
    assert error.value.code == 2
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("location,fr,lg", [
    ("route-1", 256, 256), ("route-25", 256, 256), ("viridian-forest", 250, 256),
    ("mt-moon", 263, 256), ("diglett-cave", 263, 256), ("power-plant", 256, 263),
    ("pokemon-tower-3f", 259, 256), ("safari-zone", 256, 257), ("pokemon-mansion", 257, 257),
    ("victory-road", 263, 256), ("mt-ember", 256, 256), ("icefall-cave", 263, 256),
    ("cerulean-cave", 263, 256), ("other", 256, 256),
])
def test_reference_columns_are_fire_red_and_leaf_green_with_unknown_256(location, fr, lg):
    for game, expected in (("firered", fr), ("leafgreen", lg)):
        assert default_offset("sweet-land", game, location) == expected
        plan = install_plan(game, "auto", "sweet-land", location=location)
        assert plan["offset_advances"] == expected
        assert plan["auto_a_offset_advances"] == expected + 1
        assert install_plan(game, "auto", "sweet-land", location=location, offset=0)["offset_advances"] == 0


def test_all_selectable_unknown_wild_locations_default_to_256():
    for location, _ in WILD_LOCATIONS:
        assert 250 <= default_offset("fish-super", "firered", location) <= 263
        assert 256 <= default_offset("fish-super", "leafgreen", location) <= 263


@pytest.mark.parametrize("initial,advance", [(0, 0), (0xC76F, 3354), (0xB8C0, 9999999), (0xFFFF, 0xFFFFFFFF)])
def test_bit_distance_agrees_with_independent_public_jump(initial, advance):
    lcg, _ = backend()
    assert distance(initial, lcg.advance(initial, advance)) == advance


def test_users_articuno_pid_reproduces_3354_without_ivs():
    result = lookup(0xC76F, 0x4762A09B, "articuno", first=3000, last=4000, target_advance=3351)
    assert result["result"] == "unique"
    hit = result["candidates"][0]
    assert hit["actual_advance"] == 3354
    assert hit["error_advances"] == 3 and hit["suggested_offset"] == 6
    assert result["ivs_are_predictions"] and not result["input_timing_measured"]


@pytest.mark.parametrize("method", [1, 4])
def test_pid_lookup_is_inclusive_and_calibrates_using_one_advance_boundary(method):
    lcg, _ = backend()
    mon = predict(lcg.advance(0xC76F, 3354), 0, 0, method)
    result = lookup(0xC76F, mon["personality"], "articuno", first=3354, last=3354,
                    method=method, target_advance=3351, offset=3)
    assert result["result"] == "unique"
    hit = result["candidates"][0]
    assert hit["actual_advance"] == 3354 and hit["suggested_offset"] == 6
    assert hit["predicted_ivs"] == mon["ivs"]
    assert lookup(0xC76F, mon["personality"], "articuno", first=3355, last=3355)["result"] == "no_match"


@pytest.mark.parametrize("target,chamber", [("sweet-land", "monean"), ("fish-super", "monean"), ("unown", "rixy")])
@pytest.mark.parametrize("method", [1, 2, 4])
def test_pid_only_wild_reverse_preserves_all_rejection_prefixes_and_forward_checks(target, chamber, method):
    lcg, _ = backend()
    model = "unown" if target == "unown" else "wild"
    initial, advance = 0xC76F, 20000
    mon = predict_wild(lcg.advance(initial, advance), 0, 0, method, model=model, chamber=chamber)
    result = lookup(initial, mon["personality"], target, first=19500, last=20500, method=method, chamber=chamber)
    assert advance in [c["actual_advance"] for c in result["candidates"]]
    for candidate in result["candidates"]:
        forward = predict_wild(candidate["generation_seed"], 0, 0, method, model=model, chamber=chamber)
        assert forward["personality"] == mon["personality"]
        assert candidate["predicted_ivs"] == forward["ivs"]


def test_manual_lookup_cli_needs_no_radio_keys_or_iv_input(tmp_path, capsys):
    output = tmp_path / "hit.json"
    assert lookup_tool.main(["--initial-seed", "C76F", "--pid", "4762A09B", "--target", "articuno",
                             "--output", str(output), "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["result"] == "unique" and result["candidates"][0]["actual_advance"] == 3354
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert {key: saved[key] for key in result} == result
    assert saved["schema"] == 2 and saved["plugin_version"]


def test_manual_lookup_human_output_has_actual_advance_and_offset_correction(tmp_path, capsys):
    assert lookup_tool.main(["--initial-seed", "C76F", "--pid", "4762A09B", "--target", "articuno",
                             "--target-advance", "3351", "--output", str(tmp_path / "human.json")]) == 0
    out = capsys.readouterr().out
    assert "实际 advance 3354" in out and "建议额外 Offset 6" in out


@pytest.mark.parametrize("values,kind,power", [((0,) * 6, 1, 30), ((31,) * 6, 16, 70), ((30,) * 6, 1, 70)])
def test_hidden_power_extremes(values, kind, power):
    assert hidden_power(values)["type_index"] == kind
    assert hidden_power(values)["power"] == power
