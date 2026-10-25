"""Encounter presets. Reference delays remain editable; they are not hardware certification."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Encounter:
    name: str
    species: int
    profile: str
    graphics: int
    offset: int
    model: str = "static"
    menus: bool = False
    egg: bool = False
    delay_source: str = "reference_uncalibrated"
    decision: str = "停在最后一次确认的位置，等待插件按 A。"
    button: int = 1


BASE_PRESS_OFFSETS = {"mewtwo": 1, "birds": 2, "static": 2, "wild": 1}
ENCOUNTERS = {
    "mewtwo": Encounter("超梦", 150, "mewtwo", 139, 3, delay_source="source_phase_model",
                        decision="对话结束后，停在文字框等待按键的位置。"),
    "articuno": Encounter("急冻鸟", 144, "birds", 138, 5, delay_source="source_phase_model",
                          decision="站在急冻鸟面前，等待自动 A 开始对话。"),
    "zapdos": Encounter("闪电鸟", 145, "birds", 136, 5, delay_source="source_phase_model"),
    "moltres": Encounter("火焰鸟", 146, "birds", 137, 5, delay_source="source_phase_model"),
}

# Extra Offset reference values supplied by the user. They are starting presets,
# not measurements of every script / language / decision point in this plugin.
for key, name, species, extra, decision in (
    ("bulbasaur", "妙蛙种子（御三家）", 1, 3, "停在选择这只御三家的最后 Yes 确认。"),
    ("charmander", "小火龙（御三家）", 4, 3, "停在选择这只御三家的最后 Yes 确认。"),
    ("squirtle", "杰尼龟（御三家）", 7, 3, "停在选择这只御三家的最后 Yes 确认。"),
    ("magikarp", "鲤鱼王（购买）", 129, 3, "停在购买鲤鱼王的最后 Yes 确认。"),
    ("eevee", "伊布（玉虹市礼物）", 133, 4, "站在伊布精灵球前，等待自动 A。"),
    ("hitmonlee", "飞腿郎（格斗道场）", 106, 6, "停在接受飞腿郎的最后确认。"),
    ("hitmonchan", "快拳郎（格斗道场）", 107, 6, "停在接受快拳郎的最后确认。"),
    ("snorlax12", "卡比兽（12 号道路）", 143, 3, "停在吹笛后最后一段文字的确认处。"),
    ("snorlax16", "卡比兽（16 号道路）", 143, 3, "停在吹笛后最后一段文字的确认处。"),
    ("hypno", "引梦貘人（树果森林）", 97, 86, "停在触发引梦貘人事件的最后一次确认。"),
    ("togepi", "波克比（赠蛋）", 175, 3, "停在接受蛋的最后一次确认。"),
    ("raikou", "雷公（游走个体初始化）", 243, 3, "停在一岛任务结束、初始化游走宝可梦前的最后确认；不是野外遇见它时。"),
    ("entei", "炎帝（游走个体初始化）", 244, 3, "停在一岛任务结束、初始化游走宝可梦前的最后确认；不是野外遇见它时。"),
    ("suicune", "水君（游走个体初始化）", 245, 3, "停在一岛任务结束、初始化游走宝可梦前的最后确认；不是野外遇见它时。"),
    ("deoxys", "代欧奇希斯", 410, 501, "完成三角谜题，停在最后一次触碰三角前。"),
    ("lugia", "洛奇亚", 249, 277, "站在洛奇亚面前，等待自动 A。"),
    ("hooh", "凤王", 250, 379, "停在凤王触发格南边相邻一格并朝上，等待自动 ↑ 走一步。"),
    ("omanyte", "菊石兽（化石）", 138, 3, "停在领取复活宝可梦前的最后一段文字。"),
    ("kabuto", "化石盔（化石）", 140, 3, "停在领取复活宝可梦前的最后一段文字。"),
    ("aerodactyl", "化石翼龙（化石）", 142, 3, "停在领取复活宝可梦前的最后一段文字。"),
    ("abra", "凯西（游戏厅）", 63, 3, "选好奖品，停在兑换的最后 Yes 确认。"),
    ("clefairy", "皮皮（游戏厅）", 35, 3, "选好奖品，停在兑换的最后 Yes 确认。"),
    ("scyther", "飞天螳螂（游戏厅）", 123, 3, "选好奖品，停在兑换的最后 Yes 确认。"),
    ("pinsir", "凯罗斯（游戏厅）", 127, 3, "选好奖品，停在兑换的最后 Yes 确认。"),
    ("dratini", "迷你龙（游戏厅）", 147, 3, "选好奖品，停在兑换的最后 Yes 确认。"),
    ("porygon", "多边兽（游戏厅）", 137, 3, "选好奖品，停在兑换的最后 Yes 确认。"),
):
    ENCOUNTERS[key] = Encounter(name, species, "static", 0, 2 + extra,
                               menus=key in ("bulbasaur", "charmander", "squirtle"),
                               egg=key == "togepi", decision=decision, button=64 if key == "hooh" else 1)

for key, name, species in (
    ("electrode", "顽皮雷弹（发电厂，两处通用）", 101),
    ("lapras", "拉普拉斯（西尔佛公司）", 131),
    ("custom", "其他定点 / 礼物（自定 Offset）", 0),
):
    ENCOUNTERS[key] = Encounter(name, species, "static", 0, 2, delay_source="uncalibrated")

for key, name in (
    ("sweet-land", "野生：甜甜香气（草地 / 洞窟）"),
    ("sweet-surf", "野生：甜甜香气（水面）"),
    ("fish-old", "野生：破旧钓竿"),
    ("fish-good", "野生：好钓竿"),
    ("fish-super", "野生：厉害钓竿"),
    ("wild-land", "野生：碎岩（最后 A 确认）"),
):
    ENCOUNTERS[key] = Encounter(name, 0, "wild", 0, 1, model="wild", menus=True,
                               delay_source="uncalibrated",
                               decision="甜香停在队伍菜单的甜甜香气选项；钓鱼自行完成咬钩，停在最后确认；其他方式自行停在最后 A 决定点。")

UNOWN_CHAMBERS = {
    "monean": (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 27),
    "liptoo": (2, 2, 2, 3, 3, 3, 7, 7, 7, 20, 20, 14),
    "weepth": (13, 13, 13, 13, 18, 18, 18, 18, 8, 8, 4, 4),
    "dilford": (15, 15, 11, 11, 9, 9, 17, 17, 17, 16, 16, 16),
    "scufib": (24, 24, 19, 19, 6, 6, 6, 5, 5, 5, 10, 10),
    "rixy": (21, 21, 21, 22, 22, 22, 23, 23, 12, 12, 1, 1),
    "viapois": (25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 26),
}
ENCOUNTERS["unown"] = Encounter("野生：未知图腾（阿斯卡纳遗迹）", 201, "wild", 0, 1,
                                model="unown", menus=True, delay_source="uncalibrated")


def default_offset(target):
    encounter = ENCOUNTERS[target]
    return encounter.offset - BASE_PRESS_OFFSETS[encounter.profile]


def offset_flag(target):
    return "--offset-" + target
