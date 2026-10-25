"""Read the saved party or an exported Gen III record and verify the actual result."""

import argparse
import json
from pathlib import Path

from frlg_rng_assist_core.arguments import console_arguments, hex_word, ivs, nature
from frlg_rng_assist_core.backend import backend
from frlg_rng_assist_core.display import card, mon_line
from frlg_rng_assist_core.launcher import HostFailure, run_gift
from frlg_rng_assist_core.model import Criteria
from frlg_rng_assist_core.native import ENCOUNTERS, console_arguments as host_arguments, validate_context
from frlg_rng_assist_core.pk3 import PARTY_DUMP_SIZE, choose_record, decode_mon, party_records
from frlg_rng_assist_core.records import (
    capture_path,
    digest,
    installation,
    read_capture,
    report_path,
    save_report,
)
from frlg_rng_assist_core.verification import verify


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    console_arguments(parser)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--pokemon", help="改为读取 .pk3/.ek3 文件，不连接掌机")
    source.add_argument("--party-dump", help="改为读取已有的 608 字节队伍 dump，不连接掌机")
    parser.add_argument("--slot", type=int, default=0, help="0 自动选择唯一目标；1..6 明确选择位置")
    parser.add_argument("--installation", help="可选：关联本插件的安装 JSON 报告")
    parser.add_argument("--nature", type=nature, help="可选：核对性格，不改变自动 A 的筛选条件")
    parser.add_argument("--pid", type=hex_word, help="可选：核对确切 PID")
    parser.add_argument("--iv-min", type=ivs)
    parser.add_argument("--iv-max", type=ivs)
    parser.add_argument("--allow-normal", action="store_true", help="非闪光也符合条件；关联报告时自动继承")
    parser.add_argument(
        "--initial-seed", type=hex_word, help="可选：在地图按 L 显示的初始 seed，用于核对范围"
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        backend()
        validate_context(args.game, args.build, args.target)
        if not 0 <= args.slot <= 6:
            raise ValueError("队伍位置必须为 0..6")
        receipt = installation(args.installation, args.game, args.build, args.target)
        inherited = receipt["criteria"] if receipt else {}
        criteria = Criteria(
            shiny=False if args.allow_normal else inherited.get("shiny", True),
            nature=args.nature if args.nature is not None else inherited.get("nature"),
            pid=args.pid if args.pid is not None else inherited.get("pid"),
            iv_min=args.iv_min if args.iv_min is not None else inherited.get("iv_min", (0,) * 6),
            iv_max=args.iv_max if args.iv_max is not None else inherited.get("iv_max", (31,) * 6),
        )
        output = report_path(args.output, "result")
        if args.pokemon:
            source = Path(args.pokemon).expanduser().resolve()
            if source.suffix.lower() not in (".pk3", ".ek3"):
                raise ValueError("请选择 .pk3 或 .ek3 文件")
            with source.open("rb") as stream:
                raw = stream.read(101)
            mon = decode_mon(raw, encrypted=source.suffix.lower() == ".ek3")
            evidence = "exported_record"
        else:
            source = (
                Path(args.party_dump).expanduser().resolve()
                if args.party_dump
                else capture_path(output, ".party.bin")
            )
            if not args.party_dump:
                print("请先在游戏中保存，并将目标放入队伍。选择 Mystery Gift → Wonder Cards → Friend。")
                run_gift(
                    [
                        *host_arguments(args.game, args.build, keys=args.keys),
                        "--buffer-script",
                        "save-dump",
                        "--dump-block",
                        "sav1",
                        "--dump-offset",
                        "0x34",
                        "--dump-size",
                        str(PARTY_DUMP_SIZE),
                        "--dump-file",
                        str(source),
                    ],
                    radio=args.radio,
                )
            raw = read_capture(source, PARTY_DUMP_SIZE)
            mon = choose_record(party_records(raw), ENCOUNTERS[args.target].species, args.slot)
            evidence = "imported_saved_party" if args.party_dump else "console_saved_party"
        report = verify(
            mon,
            args.game,
            args.target,
            nature=criteria.nature,
            shiny=criteria.shiny,
            iv_min=criteria.iv_min,
            iv_max=criteria.iv_max,
            pid=criteria.pid,
            initial_seed=args.initial_seed,
            search_range=receipt["range"] if receipt else None,
        )
        report.update(
            source=str(source), source_sha256=digest(raw), source_kind=evidence, installation=receipt
        )
        save_report(report, output)
    except HostFailure as exc:
        print(str(exc))
        return exc.code
    except (ValueError, RuntimeError, OSError, LookupError) as exc:
        parser.exit(2, f"RNG Assist：{exc}\n")
    ok = report["status"] == "matched"
    if args.json:
        print(json.dumps(report, ensure_ascii=False))
    else:
        print(mon_line(mon))
        print(
            "所选记录符合核对条件。"
            if ok
            else "核对未通过：" + "、".join(k for k, v in report["checks"].items() if not v)
        )
        print(f"PID/IV 反推得到 {len(report['generation_states'])} 个生成状态。报告：{output}")
        card(
            "捕获记录核对",
            [
                f"目标\t{report['target_name']}",
                f"结果\t{'符合条件' if ok else '不符合条件'}",
                f"PID\t{mon['pid']:08X}",
                f"IV\t{'/'.join(map(str, mon['ivs']))}",
            ],
            ok=ok,
        )
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
