"""Inject a natural RNG search from the actual title seed, and press A on the console."""

import argparse
import json

from frlg_rng_assist_core.arguments import console_arguments, ivs, nature
from frlg_rng_assist_core.display import card
from frlg_rng_assist_core.launcher import HostFailure, run_gift
from frlg_rng_assist_core.native import console_arguments as host_arguments
from frlg_rng_assist_core.model import Criteria
from frlg_rng_assist_core.native import install_plan, validate_install_ack, write_gift
from frlg_rng_assist_core.records import capture_path, report_path, save_report


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    console_arguments(parser)
    parser.add_argument("--enable-auto-a", action="store_true", help="安装并启用到点自动 A")
    parser.add_argument("--start", type=int, default=10000, help="从标题实际初始 seed 起算的 advance 下限")
    parser.add_argument("--end", type=int, default=200000, help="advance 上限，含端点，最大 9999999")
    parser.add_argument("--nature", type=nature, help="性格：中文、英文或 0..24；留空不限")
    parser.add_argument("--iv-min", type=ivs, default=(0, 0, 0, 0, 0, 0))
    parser.add_argument("--iv-max", type=ivs, default=(31, 31, 31, 31, 31, 31))
    parser.add_argument("--allow-normal", action="store_true", help="也接受非闪光；适合首轮按 A 测试")
    parser.add_argument("--preview", action="store_true", help="仅导出真实安装配置，不连接掌机")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        criteria = Criteria(not args.allow_normal, args.nature, None, args.iv_min, args.iv_max)
        plan = install_plan(
            args.game, args.build, args.target, first=args.start, last=args.end, criteria=criteria
        )
        if not args.preview and not args.enable_auto_a:
            raise ValueError("请勾选「安装并启用自动 A」；只检查配置可选择「仅预览」。")
        output = report_path(args.output, "install")
        gift = capture_path(output, ".pokegift")
        plan["gift"] = write_gift(plan, gift)
        arguments = host_arguments(args.game, args.build, keys=args.keys) + ["--gift-file", str(gift)]
        if args.preview:
            plan.update(status="preview")
        else:
            print(f"正在安装{plan['target_name']}配置。在掌机选择 Mystery Gift → Wonder Cards → Friend。")
            statuses = run_gift(arguments, radio=args.radio)
            original = validate_install_ack(statuses)
            plan.update(status="installed", installer_ack=original)
        save_report(plan, output)
    except HostFailure as exc:
        if exc.statuses:
            try:
                validate_install_ack(list(exc.statuses))
            except ValueError as reason:
                print(f"RNG Assist：{reason}")
        print(str(exc))
        return exc.code
    except (ValueError, RuntimeError, OSError, LookupError) as exc:
        parser.exit(2, f"RNG Assist：{exc}\n")
    if args.json:
        print(json.dumps(plan, ensure_ascii=False))
    else:
        if args.preview:
            print(f"预览已生成：{plan['gift']['path']}。本次没有连接掌机。")
        else:
            print("安装回执已确认。退出 Mystery Gift，返回标题，再选择继续游戏。")
            print("回到地图后：上排为当前 seed；下排 A=搜索，B=剩余 advances。按住 L 查看初始 seed。")
            print("L 打开帮助时，先将 OPTIONS → BUTTON MODE 设为 L/R 并保存；本插件不单独识别 ZL。")
            print("倒计时绿色=计时可触发，不代表站位已就绪。")
            if args.target == "mewtwo":
                print("超梦：提前对话，等叫声和文字结束，停在按键等待；之后不要再手动按 A/B。")
            else:
                print("三鸟：提前走到想按 A 的位置，松开所有按键等倒计时；到点自动按一次 A，无需按住 B。")
                print("站位由你负责；插件不检测相邻、朝向、移动、目标对象或脚本状态。")
            print("C0000001=等待注入，C0000000=已注入 A；是否实际开战仍须观察。")
            print("D=时序或游戏状态不符，原因见测试说明。E=无可用目标，F=计数失效，均不会补按 A。")
            print("捕获后把目标留在队伍中，游戏内保存，再运行「核对捕获结果」。")
            print("软重启或关闭游戏会清除注入；下一次尝试需重新安装。")
        print(f"报告：{output}")
        card(
            "实机 RNG 搜索",
            [
                f"目标\t{plan['target_name']}",
                f"状态\t{'仅预览' if args.preview else '安装回执已确认'}",
                f"范围\t{args.start}..{args.end} advances（从标题初始 seed 起算）",
                "实机验证\t尚未完成",
                "捕获结果\t等待核对",
            ],
            ok=None,
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
