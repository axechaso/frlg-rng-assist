import argparse

from .backend import NATURES, NATURES_ZH
from .native import ENCOUNTERS, GAMES


def hex_word(text):
    try:
        result = int(text.strip(), 16)
        if not 0 <= result <= 0xFFFFFFFF:
            raise ValueError()
        return result
    except ValueError:
        raise argparse.ArgumentTypeError("请输入 32 位十六进制 seed/PID，例如 12345678") from None


def ivs(text):
    try:
        result = tuple(int(part.strip()) for part in text.replace("/", ",").split(","))
        if len(result) != 6 or any(not 0 <= value <= 31 for value in result):
            raise ValueError()
        return result
    except ValueError:
        raise argparse.ArgumentTypeError("请输入六项 0..31 的 IV：HP,攻击,防御,特攻,特防,速度") from None


def nature(text):
    from .wild_tables import names

    for language in ("zh", "ja", "en"):
        for index, name in enumerate(names()["natures"][language]):
            if text.casefold() == name.casefold():
                return index
    for index, name in enumerate(NATURES):
        if text.casefold() == name.casefold() or text == NATURES_ZH[index]:
            return index
    try:
        result = int(text)
        if not 0 <= result <= 24:
            raise ValueError()
        return result
    except ValueError:
        raise argparse.ArgumentTypeError("请输入性格的中文名、英文名或 0..24 编号") from None


def output_arguments(parser):
    parser.add_argument("--ui-language", choices=("zh", "en", "ja"), default="zh", help=argparse.SUPPRESS)
    parser.add_argument("--output", help="新建 JSON 报告；默认保存到插件资料库")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出报告")


def console_arguments(parser):
    parser.add_argument("--game", choices=GAMES, default="firered")
    parser.add_argument("--build", default="auto", help="auto 根据卡带选择地址；也可指定 BPRE/BPGE 等")
    parser.add_argument("--target", choices=ENCOUNTERS, default="mewtwo")
    parser.add_argument("--keys", help="PokeLDN 自动传入的 prod.keys 路径")
    parser.add_argument("--radio", help="高级：覆盖 Board，例如 esp32:COM8")
    output_arguments(parser)
