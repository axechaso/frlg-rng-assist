"""Find the actual hit from the initial seed and captured PID, without a radio session."""

import argparse
import json

from frlg_rng_assist_core.arguments import hex_word, output_arguments
from frlg_rng_assist_core.display import card
from frlg_rng_assist_core.encounters import ENCOUNTERS
from frlg_rng_assist_core.lookup import lookup
from frlg_rng_assist_core.records import report_path, save_report
from frlg_rng_assist_core.selection import normalize_selection, selection_arguments


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    output_arguments(parser)
    selection_arguments(parser)
    parser.add_argument("--game", choices=("firered", "leafgreen"), default="firered")
    parser.add_argument("--target", choices=ENCOUNTERS, default="mewtwo")
    parser.add_argument("--method", type=int, choices=(1, 2, 4), default=1)
    parser.add_argument("--initial-seed", type=hex_word, required=True)
    parser.add_argument("--pid", type=hex_word, required=True)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=9999999)
    parser.add_argument("--target-advance", type=int)
    parser.add_argument("--offset", type=int)
    return parser


def main(argv=None):
    parser = build_parser()
    args = normalize_selection(parser.parse_args(argv))
    try:
        report = lookup(args.initial_seed, args.pid, args.target, first=args.start, last=args.end,
                        method=args.method, chamber=args.chamber, game=args.game, location=args.location,
                        target_advance=args.target_advance, offset=args.offset)
        output = report_path(args.output, "pid-lookup")
        save_report(report, output)
    except (ValueError, RuntimeError, LookupError, OSError) as exc:
        parser.exit(2, f"RNG Assist：{exc}\n")
    if args.json:
        print(json.dumps(report, ensure_ascii=False))
    else:
        status = {"unique": "唯一命中", "ambiguous": "多个候选，请缩小范围", "no_match": "范围内无匹配"}[report["result"]]
        print(f"PID {args.pid:08X}：{status}。")
        for item in report["candidates"]:
            print(f"实际 advance {item['actual_advance']} | 生成前 seed {item['generation_seed']:08X}"
                  f" | {item['nature']} | 预测 IV {','.join(map(str, item['predicted_ivs']))}")
            if "error_advances" in item:
                print(f"与原目标相差 {item['error_advances']:+d} advances；建议额外 Offset {item['suggested_offset']}。")
        print("IV 为所选生成方式的预测值；实际值可在掌机按 R 查看。")
        print(f"报告：{output}")
        card("PID 反查实际命中", [f"结果\t{status}", f"候选\t{len(report['candidates'])}"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
