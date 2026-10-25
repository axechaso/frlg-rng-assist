"""Recover past generation states from an actual PID and six IVs."""

import argparse
import json

from frlg_rng_assist_core.arguments import hex_word, ivs, output_arguments
from frlg_rng_assist_core.display import card
from frlg_rng_assist_core.model import recovery_report
from frlg_rng_assist_core.records import report_path, save_report


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    output_arguments(parser)
    parser.add_argument("--pid", type=hex_word, required=True)
    parser.add_argument("--ivs", type=ivs, required=True)
    parser.add_argument(
        "--reference-seed", type=hex_word, help="可选：同一 RNG 时段的观测 seed；不接受跨标题的计时解释"
    )
    parser.add_argument("--max-offset", type=int, default=4096)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        output = report_path(args.output, "recover")
        report = recovery_report(
            args.pid, args.ivs, reference_seed=args.reference_seed, max_offset=args.max_offset
        )
        save_report(report, output)
    except (ValueError, RuntimeError, OSError, LookupError) as exc:
        parser.exit(2, f"RNG Assist：{exc}\n")
    if args.json:
        print(json.dumps(report, ensure_ascii=False))
    else:
        print(f"反推结果：{report['result']}。")
        for candidate in report["candidates"]:
            print(
                f"Method {candidate['method']} | 生成前 seed {candidate['generation_seed']:08X}"
                + (
                    f" | 距参考 seed {candidate['offset_advances']} advances"
                    if "offset_advances" in candidate
                    else ""
                )
            )
        print(f"反推只说明过去的生成状态。报告：{output}")
        card("PID/IV 状态反推", [f"结果\t{report['result']}", f"候选\t{len(report['candidates'])}"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
