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
from frlg_rng_assist_core.i18n import set_language, species_name, target_name, tr


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
    set_language(args.ui_language)
    try:
        criteria = Criteria(not args.allow_normal, args.nature, None, args.iv_min, args.iv_max)
        plan = install_plan(
            args.game, args.build, args.target, first=args.start, last=args.end, criteria=criteria,
            offset=args.offset, method=args.method, chamber=args.chamber, location=args.location, species=args.species,
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
            print(tr("正在安装 {target}。在掌机选择 Mystery Gift → Wonder Cards → Friend。", target=target_name(args.target)))
            statuses = run_gift(arguments, radio=args.radio)
            original = validate_install_ack(statuses)
            plan.update(status="installed", installer_ack=original)
        save_report(plan, output)
    except HostFailure as exc:
        if exc.statuses:
            try:
                validate_install_ack(list(exc.statuses))
            except ValueError as reason:
                print(f"RNG Assist: {tr(str(reason))}")
        print(str(exc))
        return exc.code
    except (ValueError, RuntimeError, OSError, LookupError) as exc:
        parser.exit(2, f"RNG Assist: {tr(str(exc))}\n")
    if args.json:
        print(json.dumps(plan, ensure_ascii=False))
    else:
        if args.preview:
            print(tr("预览已生成：{path}。本次没有连接掌机。", path=plan['gift']['path']))
        else:
            print(tr("安装回执已确认。退出 Mystery Gift，返回标题，再选择继续游戏。"))
            print(tr("上排当前 seed，下排 A 搜索 / B 倒计时；L 查看初始 seed 和绝对 advances；L+R 查看队尾 PID 和队伍位置。"))
            print(tr("R 查看队尾 IV / 觉醒力量：上排 HP、攻击、防御、速度；下排特攻、特防、属性编号、威力，每项两位十进制。"))
            print(tr("L/R 打开帮助时，先将 OPTIONS → BUTTON MODE 设为 L/R 并保存；本插件不单独识别 ZL/ZR。"))
            button = "↑" if plan["trigger_button"] == "UP" else "A"
            print(tr("额外 Offset={offset} advances；合计在目标生成前 {total} advances 排定 {button}。",
                     offset=plan['offset_advances'], total=plan['auto_a_offset_advances'], button=button))
            print(tr(plan["decision_point"]))
            print(tr("自行停在决定点，插件到点按一次 {button}；不检测站位、朝向、对象、脚本等待或 B 键。", button=button))
            if plan["model"] != "static":
                print(tr("野生 H{method}：范围按遭遇槽位抽取前计数，包含性格 / PID 重抽。Offset 首次需校准。", method=plan['method']))
            elif plan["offset_source"] == "reference_uncalibrated":
                print(tr("此 Offset 是参考预设，尚未在这个决定点做实机校准；先允许非闪光测试实际 PID。"))
            print(tr("C0000001=等待注入，C0000000=已注入 {button}；是否实际触发仍须观察。", button=button))
            print(tr("黄色表示按键时机奇偶不符，绿色表示一致；错过后红色 D 保留约 1 秒再续搜。C 已发按键，E 范围耗尽，F 计数失效。"))
            print(tr("续搜保留初始 seed 和筛选条件，不补按旧目标。发送一次按键后结束；E=范围耗尽，F=计数失效，也会结束。"))
            print(tr("捕获后按 L+R 读实际 PID，用下方 PID 反查核对。软重启 / 关闭游戏会清除注入，下一轮需重新安装。"))
        if plan["wild_species"]:
            print(tr("筛选物种：{species}（#{number:03d}）", species=species_name(plan['wild_species']), number=plan['wild_species']))
        print(f"{tr('报告')}: {output}")
        card(
            tr("实机 RNG 搜索"),
            [
                f"{tr('目标')}\t{target_name(args.target)}",
                f"{tr('触发按键')}\t{plan['trigger_button']}",
                f"{tr('状态')}\t{tr('仅预览' if args.preview else '安装回执已确认')}",
                tr("范围\t{first}..{last} advances（从标题初始 seed 起算）", first=args.start, last=args.end),
                tr("额外 Offset\t{offset} advances（总提前量 {total}）", offset=plan['offset_advances'], total=plan['auto_a_offset_advances']),
                tr("实机验证\t尚未完成"),
                tr("捕获结果\t等待核对"),
            ],
            ok=None,
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
