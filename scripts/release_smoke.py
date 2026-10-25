"""Development only: exercise the public catalog launcher inside the frozen release, offline."""

import argparse
import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from frlg_rng_assist_core.backend import backend, predict, recover
from frlg_rng_assist_core.launcher import run_gift
from frlg_rng_assist_core.model import Criteria
from frlg_rng_assist_core.encounters import ENCOUNTERS, default_offset, offset_flag
from frlg_rng_assist_core.native import ACK, console_arguments, install_plan, write_gift


def check_catalog_offsets(installer, plugin_root):
    """Use the actual host form-to-argv path, including conditional field visibility."""
    from pokeldn.app import command
    from install import build_parser

    tool = replace(installer, script=str(Path(plugin_root) / "install.py"))
    settings = SimpleNamespace(received="", keys="", capture=False, language=2, gender=0,
                               ids=lambda game: (12345, 2791), name=lambda game: "TEST")
    for target in ENCOUNTERS:
        values = {"--target": target}
        visible = [field for field in tool.fields if str(field.flag).startswith("--offset-")
                   and command.applies(field, tool, values)]
        assert len(visible) == 1 and visible[0].flag == offset_flag(target)
        assert visible[0].kind == "number" and not visible[0].hidden
        assert command.value_of(visible[0], values) == str(default_offset(target))
        parsed = build_parser().parse_args(command.build(tool, values, {}, settings))
        assert (parsed.target, parsed.offset) == (target, default_offset(target))
    values = {"--target": "articuno", "--offset-articuno": "17"}
    assert build_parser().parse_args(command.build(tool, values, {}, settings)).offset == 17
    values["--target"] = "deoxys"
    assert build_parser().parse_args(command.build(tool, values, {}, settings)).offset == 501
    values["--target"] = "articuno"
    assert build_parser().parse_args(command.build(tool, values, {}, settings)).offset == 17


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
    installer = next(tool for tool in catalog.tools if tool.key == "frlg-rng-assist-install")
    check_catalog_offsets(installer, plugin_root)
    work = Path(args.work).resolve()
    work.mkdir(exist_ok=True)
    lcg, _ = backend()
    seed = lcg.advance(0xB8C0, 20000)
    mon = predict(seed, 12345, 2791)
    assert {"generation_seed": seed, "method": 1} in recover(mon["personality"], mon["ivs"])
    results = []
    for game, target in (("firered", "mewtwo"), ("leafgreen", "articuno"),
                         ("firered", "deoxys"), ("leafgreen", "sweet-land"), ("firered", "fish-super")):
        plan = install_plan(
            game, "auto", target, criteria=Criteria(shiny=False),
            offset=3 if target == "articuno" else None,
        )
        assert plan["offset_advances"] == default_offset(target)
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
