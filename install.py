"""Inject a natural RNG search from the actual title seed, and press A on the console."""

import argparse
import json

from frlg_rng_assist_core.arguments import console_arguments, ivs, nature
from frlg_rng_assist_core.display import card
from frlg_rng_assist_core.encounters import ENCOUNTERS, offset_flag
from frlg_rng_assist_core.launcher import HostFailure, run_gift
from frlg_rng_assist_core.native import console_arguments as host_arguments
from frlg_rng_assist_core.model import Criteria
from frlg_rng_assist_core.native import install_plan, validate_install_ack, write_gift
from frlg_rng_assist_core.records import capture_path, report_path, save_report
from frlg_rng_assist_core.selection import normalize_selection, selection_arguments


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    console_arguments(parser)
    selection_arguments(parser)
    parser.add_argument("--enable-auto-a", action="store_true", help="安装并启用到点按键；凤王为 ↑，其他目标为 A")
    parser.add_argument("--start", type=int, default=10000, help="从标题实际初始 seed 起算的 advance 下限")
    parser.add_argument("--end", type=int, default=200000, help="advance 上限，含端点，最大 9999999")
    offsets = parser.add_mutually_exclusive_group()
    offsets.add_argument("--offset", type=int, help="额外提前量 0..65533 advances；默认使用目标预设")
    for target in ENCOUNTERS:
        offsets.add_argument(offset_flag(target), dest="offset", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--method", type=int, choices=(1, 2, 4), default=1,
                        help="定点 1/4；野生 H1/H2/H4，通常用 1")
    parser.add_argument("--nature", type=nature, help="性格：中文、英文或 0..24；留空不限")
    parser.add_argument("--iv-min", type=ivs, default=(0, 0, 0, 0, 0, 0))
    parser.add_argument("--iv-max", type=ivs, default=(31, 31, 31, 31, 31, 31))
    parser.add_argument("--allow-normal", action="store_true", help="也接受非闪光；适合首轮按 A 测试")
    parser.add_argument("--preview", action="store_true", help="仅导出真实安装配置，不连接掌机")
    return parser


def main(argv=None):
    parser = build_parser()
    args = normalize_selection(parser.parse_args(argv))
    try:
        criteria = Criteria(not args.allow_normal, args.nature, None, args.iv_min, args.iv_max)
        plan = install_plan(
            args.game, args.build, args.target, first=args.start, last=args.end, criteria=criteria,
            offset=args.offset, method=args.method, chamber=args.chamber, location=args.location,
        )
        if not args.preview and not args.enable_auto_a:
            raise ValueError("请勾选「安装并启用到点按键」；只检查配置可选择「仅预览」。")
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
            print("回到地图后：上排为当前 seed；下排 A=搜索，B=固定目标剩余 advances。按住 L 查看初始 seed。")
            print("同时按住 L+R 查看队尾：上排白色 8 位十六进制 PID，下排队伍位置 1..6；松开恢复，查看不暂停计时或自动 A。")
            print("L/R 打开帮助时，先将 OPTIONS → BUTTON MODE 设为 L/R 并保存；本插件不单独识别 ZL/ZR。")
            button = "↑" if plan["trigger_button"] == "UP" else "A"
            print("倒计时：与按键时机奇偶不一致为黄色，一致且当前可触发为绿色；不代表站位已就绪。")
            print(f"额外 Offset={plan['offset_advances']} advances；合计在目标生成前 {plan['auto_a_offset_advances']} advances 排定 {button}。")
            print(plan["decision_point"])
            print(f"自行停在决定点，插件到点按一次 {button}；不检测站位、朝向、对象、脚本等待或 B 键。")
            if plan["model"] != "static":
                print(f"野生 H{plan['method']}：范围按遭遇槽位抽取前计数，包含性格 / PID 重抽。Offset 首次需校准。")
            elif plan["offset_source"] == "reference_uncalibrated":
                print("此 Offset 是参考预设，尚未在这个决定点做实机校准；先允许非闪光测试实际 PID。")
            print(f"C0000001=等待注入，C0000000=已注入 {button}；是否实际触发仍须观察。")
            print("颜色变化不会提前丢弃原目标；原目标保留到指定时机。")
            print("错过或本次按键失败时，红色 D 原因码在地图保留约 1 秒，再自动续搜；在电视里错过则返回地图后提示。")
            print("续搜保留初始 seed 和筛选条件，不补按旧目标。发送一次按键后结束；E=范围耗尽，F=计数失效，也会结束。")
            print("按 R 查看队尾 IV / 觉醒力量；按 L+R 读取 PID，用「PID 反查实际命中」输入初始 seed 和 PID。")
            print("软重启或关闭游戏会清除注入；下一次尝试需重新安装。")
        print(f"报告：{output}")
        card(
            "实机 RNG 搜索",
            [
                f"目标\t{plan['target_name']}",
                f"触发按键\t{plan['trigger_button']}",
                f"状态\t{'仅预览' if args.preview else '安装回执已确认'}",
                f"范围\t{args.start}..{args.end} advances（从标题初始 seed 起算）",
                f"额外 Offset\t{plan['offset_advances']} advances（总提前量 {plan['auto_a_offset_advances']}）",
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
