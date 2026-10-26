"""Development only: exercise the public catalog launcher inside the frozen release, offline."""

import argparse
import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from frlg_rng_assist_core.backend import backend, predict, recover
from frlg_rng_assist_core.launcher import run_gift
from frlg_rng_assist_core.model import Criteria
from frlg_rng_assist_core.encounters import CATEGORIES, WILD_LOCATIONS, allowed_methods, default_offset
from frlg_rng_assist_core.native import ACK, console_arguments, install_plan, write_gift
from frlg_rng_assist_core.selection import method_flag, normalize_selection, target_flag


def check_catalog_offsets(installer, plugin_root):
    """Use the actual host form-to-argv path, including conditional field visibility."""
    from pokeldn.app import command
    from install import build_parser

    tool = replace(installer, script=str(Path(plugin_root) / "install.py"))
    settings = SimpleNamespace(received="", keys="", capture=False, language=2, gender=0,
                               ids=lambda game: (12345, 2791), name=lambda game: "TEST")
    # Retain stale values from previously visited categories, exactly as the form
    # does. They must neither display nor leak into the command being launched.
    values = {target_flag(category): targets[-1] for category, (_, targets) in CATEGORIES.items()}
    parser = build_parser()
    for category, (_, targets) in CATEGORIES.items():
        for target in targets:
            values.update({"--category": category, target_flag(category): target})
            active = [f for f in tool.fields if f.flag.startswith("--target-") and command.applies(f, tool, values)]
            assert len(active) == 1 and active[0].flag == target_flag(category)
            methods = [f for f in tool.fields if f.flag.startswith("--method-") and command.applies(f, tool, values)]
            assert len(methods) == 1
            assert tuple(int(v) for v, _ in methods[0].choices) == allowed_methods(target)
            for method in allowed_methods(target):
                values[method_flag(category)] = str(method)
                assert not command.problems(tool, values)
                parsed = normalize_selection(parser.parse_args(command.build(tool, values, {}, settings)))
                assert (parsed.target, parsed.method, parsed.offset) == (target, method, None)
                plan = install_plan(parsed.game, parsed.build, parsed.target, method=parsed.method)
                assert plan["offset_advances"] == default_offset(target)
    for game in ("firered", "leafgreen"):
        for location, _ in WILD_LOCATIONS:
            values.update({"--game": game, "--category": "wild", "--location": location,
                           "--target-wild": "sweet-land"})
            assert not command.problems(tool, values)
            parsed = normalize_selection(parser.parse_args(command.build(tool, values, {}, settings)))
            plan = install_plan(parsed.game, parsed.build, parsed.target, location=parsed.location)
            assert plan["offset_advances"] == default_offset(parsed.target, game, location)
    values.update({"--category": "legends", "--target-legends": "articuno"})
    for offset in ("0", "17"):
        values["--offset"] = offset
        assert not command.problems(tool, values)
        assert parser.parse_args(command.build(tool, values, {}, settings)).offset == int(offset)
    values["--offset"] = ""
    assert not command.problems(tool, values)
    parsed = normalize_selection(parser.parse_args(command.build(tool, values, {}, settings)))
    assert install_plan(parsed.game, parsed.build, parsed.target, offset=parsed.offset)["offset_advances"] == 3


def check_localized_species_forms(plugin, plugin_root, work):
    from pokeldn.app import command, i18n
    from install import build_parser, main as install_main

    # The host owns --capture <logfile>; the plugin must not advertise that flag.
    settings = SimpleNamespace(received="", keys="", capture=True, language=2, gender=0,
                               ids=lambda game: (12345, 2791), name=lambda game: "TEST")
    original = i18n.locale
    gifts = []
    try:
        for language in ("zh", "en", "ja"):
            i18n.locale = lambda: language
            tools = []
            plugin.register(SimpleNamespace(add_tool=lambda game, tool: tools.append(tool)))
            assert len(tools) == 2
            tool = replace(tools[0], script=str(plugin_root / "install.py"))
            values = {"--category": "wild", "--target-wild": "sweet-land", "--location": "viridian-forest",
                      "--species": "25", "--nature": "15", "--iv-min": "20,0,0,0,0,20", "--preview": True,
                      "--capture-rng": True, "--capture-offset": "242", "--capture-offset-max": "245",
                      "--output": str(work / f"localized-{language}.json")}
            assert not command.problems(tool, values)
            argv = command.build(tool, values, {}, settings)
            parsed = normalize_selection(build_parser().parse_args(argv))
            assert (parsed.ui_language, parsed.species, parsed.nature) == (language, 25, 15)
            assert parsed.iv_min == (20, 0, 0, 0, 0, 20)
            assert parsed.capture and (parsed.capture_offset, parsed.capture_offset_max) == (242, 245)
            assert install_main(argv) == 0
            result = json.loads(Path(values["--output"]).read_text(encoding="utf-8"))
            assert result["wild_species"] == 25
            assert result["capture"]["enabled"] and result["capture"]["threshold"] == 16643
            gifts.append(Path(result["gift"]["path"]).read_bytes())
        assert gifts[0] == gifts[1] == gifts[2]
    finally:
        i18n.locale = original


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True)
    parser.add_argument("--expect-plugin-root")
    args = parser.parse_args()
    import frlg_rng_assist_core

    plugin_root = Path(frlg_rng_assist_core.__file__).resolve().parent.parent
    if args.expect_plugin_root:
        assert plugin_root == Path(args.expect_plugin_root).resolve()
    import plugin

    assert Path(plugin.__file__).resolve().parent == plugin_root

    class Catalog:
        def __init__(self):
            self.tools = []

        def add_tool(self, game, tool):
            assert game == "frlg"
            self.tools.append(tool)

    catalog = Catalog()
    plugin.register(catalog)
    assert [t.key for t in catalog.tools] == ["frlg-rng-assist-install", "frlg-rng-assist-lookup"]
    installer = next(tool for tool in catalog.tools if tool.key == "frlg-rng-assist-install")
    check_catalog_offsets(installer, plugin_root)
    work = Path(args.work).resolve()
    work.mkdir(exist_ok=True)
    check_localized_species_forms(plugin, plugin_root, work)
    # Exercise the second tool through the real form parser as a manual, offline
    # operation. No radio or IV input is accepted / needed for PID lookup.
    from pokeldn.app import command
    from lookup import build_parser as lookup_parser, main as lookup_main

    lookup_tool = replace(catalog.tools[1], script=str(plugin_root / "lookup.py"))
    settings = SimpleNamespace(received="", keys="", capture=False, language=2, gender=0,
                               ids=lambda game: (12345, 2791), name=lambda game: "TEST")
    values = {"--category": "legends", "--target-legends": "articuno", "--initial-seed": "C76F",
              "--pid": "4762A09B", "--output": str(work / "manual-pid.json")}
    assert not command.problems(lookup_tool, values)
    without_correction = lookup_parser().parse_args(command.build(lookup_tool, values, {}, settings))
    assert without_correction.offset is None and without_correction.target_advance is None
    values["--target-advance"] = "3351"
    assert not command.problems(lookup_tool, values)
    argv = command.build(lookup_tool, values, {}, settings)
    parsed = normalize_selection(lookup_parser().parse_args(argv))
    assert parsed.initial_seed == 0xC76F and parsed.pid == 0x4762A09B and parsed.target == "articuno"
    assert "--keys" not in argv and "--radio" not in argv and "--ivs" not in argv
    assert lookup_main(argv) == 0
    hit = json.loads((work / "manual-pid.json").read_text(encoding="utf-8"))
    assert hit["result"] == "unique" and hit["candidates"][0]["actual_advance"] == 3354
    assert hit["candidates"][0]["suggested_offset"] == 6
    lcg, _ = backend()
    seed = lcg.advance(0xB8C0, 20000)
    mon = predict(seed, 12345, 2791)
    assert {"generation_seed": seed, "method": 1} in recover(mon["personality"], mon["ivs"])
    results = []
    for game, target, location, species in (
        ("firered", "mewtwo", "other", 0), ("leafgreen", "articuno", "other", 0),
        ("firered", "deoxys", "other", 0), ("leafgreen", "sweet-land", "viridian-forest", 25),
        ("firered", "fish-super", "safari-zone-center", 147),
        ("leafgreen", "sweet-surf", "safari-zone-center", 79),
        ("firered", "unown", "other", 0),
    ):
        plan = install_plan(
            game, "auto", target, criteria=Criteria(shiny=False),
            offset=3 if target == "articuno" else None,
            location=location, species=species, capture=True, capture_offset=242, capture_offset_max=245,
        )
        assert plan["offset_advances"] == default_offset(target, game, location)
        gift = work / f"{game}-{target}.pokegift"
        exported = work / f"{game}-{target}-host-export.pokegift"
        info = write_gift(plan, gift)
        assert (
            run_gift(
                [*console_arguments(game, "auto"), "--gift-file", str(gift), "--export-gift", str(exported)]
            )
            == []
        )
        from pokeldn.gifts import load

        document = load(exported, game="frlg")
        assert set(document.variants) == set(info["builds"])
        assert all(variant.options["buffer_expect"] == ACK for variant in document.variants.values())
        results.append({"game": game, "exported": str(exported), **info})
    print(
        json.dumps(
            {
                "status": "passed",
                "mode": "offline_frozen_host_export",
                "plugin_root": str(plugin_root),
                "results": results,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
