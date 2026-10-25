"""Offline candidate search using the public API 1.11 RNG helpers."""

import argparse
import json

from frlg_rng_assist_core.arguments import hex_word, ivs, nature, output_arguments
from frlg_rng_assist_core.display import card, progress
from frlg_rng_assist_core.model import Criteria, search
from frlg_rng_assist_core.records import report_path, save_report


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    output_arguments(parser)
    parser.add_argument("--seed", type=hex_word, required=True)
    parser.add_argument("--tid", type=int, required=True)
    parser.add_argument("--sid", type=int, required=True)
    parser.add_argument("--method", type=int, choices=(1, 2, 4), default=1)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--advances", type=int, default=100000)
    parser.add_argument("--max-results", type=int, default=10)
    parser.add_argument("--any-shininess", action="store_true")
    parser.add_argument("--nature", type=nature)
    parser.add_argument("--pid", type=hex_word)
    parser.add_argument("--iv-min", type=ivs, default=(0, 0, 0, 0, 0, 0))
    parser.add_argument("--iv-max", type=ivs, default=(31, 31, 31, 31, 31, 31))
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        output = report_path(args.output, "search")
        report = search(
            args.seed,
            args.tid,
            args.sid,
            method=args.method,
            start=args.start,
            advances=args.advances,
            max_results=args.max_results,
            criteria=Criteria(not args.any_shininess, args.nature, args.pid, args.iv_min, args.iv_max),
            progress=None if args.json else progress,
        )
        save_report(report, output)
    except (ValueError, RuntimeError, OSError, LookupError) as exc:
        parser.exit(2, f"RNG Assist：{exc}\n")
    if args.json:
        print(json.dumps(report, ensure_ascii=False))
    else:
        print(f"离线搜索：检查 {report['candidates_tested']} 个候选，找到 {len(report['targets'])} 个目标。")
        for hit in report["targets"]:
            print(
                f"+{hit['advance']} advances | seed {hit['generation_seed']:08X} | PID {hit['pid']:08X} | "
                f"{hit['nature_zh']} | IV {'/'.join(map(str, hit['ivs']))}"
            )
        print("这是离线预测；Mystery Gift 中读取的 seed 在返回标题后失效。")
        print(f"报告：{output}")
        card(
            "离线 RNG 搜索",
            [
                f"候选\t{report['candidates_tested']}",
                f"结果\t{len(report['targets'])}",
                "时段\t输入 seed 的时段；无法跨标题界面使用",
            ],
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
