"""Development only: exercise the public catalog launcher inside the frozen release, offline."""

import argparse
import json
from pathlib import Path

from frlg_rng_assist_core.backend import backend, predict, recover
from frlg_rng_assist_core.launcher import run_gift
from frlg_rng_assist_core.model import Criteria
from frlg_rng_assist_core.native import ACK, console_arguments, install_plan, write_gift


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
    offset_field = next(field for field in installer.fields if field.flag == "--offset")
    assert offset_field.kind == "number" and offset_field.default == "" and not offset_field.hidden
    work = Path(args.work).resolve()
    work.mkdir(exist_ok=True)
    lcg, _ = backend()
    seed = lcg.advance(0xB8C0, 20000)
    mon = predict(seed, 12345, 2791)
    assert {"generation_seed": seed, "method": 1} in recover(mon["personality"], mon["ivs"])
    results = []
    for game, target in (("firered", "mewtwo"), ("leafgreen", "articuno")):
        plan = install_plan(
            game, "auto", target, criteria=Criteria(shiny=False),
            offset=3 if target == "articuno" else None,
        )
        assert plan["offset_advances"] == (3 if target == "articuno" else 2)
        assert plan["auto_a_offset_advances"] == (5 if target == "articuno" else 3)
        gift = work / f"{game}.pokegift"
        exported = work / f"{game}-host-export.pokegift"
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
