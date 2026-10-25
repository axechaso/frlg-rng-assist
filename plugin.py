"""Registration only. Importing this file never runs a launcher or touches the board."""

from pokeldn.plugins import Field, Tool
from frlg_rng_assist_core.encounters import ENCOUNTERS, UNOWN_CHAMBERS, default_offset, offset_flag


def register(api):
    from frlg_rng_assist_core.native import PROFILES

    target_choices = tuple((key, encounter.name) for key, encounter in ENCOUNTERS.items())
    common = (
        Field(
            "--game",
            "游戏",
            "choice",
            default="firered",
            choices=(("firered", "火红"), ("leafgreen", "叶绿")),
        ),
        Field("--target", "目标", "choice", default="mewtwo", choices=target_choices,
              choice_help=tuple((key, encounter.decision) for key, encounter in ENCOUNTERS.items())),
        Field(
            "--build",
            "卡带语言 / 构建",
            "choice",
            default="auto",
            choices=(("auto", "自动识别：英文 / 法文 rev 0A"), *((code, code) for code in PROFILES)),
            hidden=True,
            help="自动按加入会话的卡带选择地址；指定错误构建时，主程序会拒绝发送。",
        ),
        Field("--radio", "Radio 覆盖", hidden=True, help="一般使用 Board 页面选定的设备。"),
        Field("--output", "报告保存路径", hidden=True, help="留空保存到 FRLG RNG Assist 资料库。"),
    )
    api.add_tool(
        "frlg",
        Tool(
            "frlg-rng-assist-install",
            "RNG：搜索与到点按键",
            "install.py",
            "注入范围和筛选条件；从实际初始 seed 计算 advances，到点触发一次：凤王按 ↑，其他目标按 A。",
            (
                "先在目标附近保存，重新启动游戏，清除其他 boosts。查看 seed / PID 前把 OPTIONS → BUTTON MODE 设为 L/R 并保存。",
                "掌机：Mystery Gift → Wonder Cards → Friend，选择 POKELDN，等待日志确认安装回执。",
                "退出到标题，继续游戏。上排当前 seed；下排 A 搜索，B 为固定目标倒计时。按住 L 查看初始 seed 和绝对 advances。",
                "同时按住 L+R：上排白色显示队尾宝可梦的 8 位十六进制 PID，下排显示队尾位置 1..6；松开恢复。查看不暂停计时或自动 A。",
                "所有目标流程一致：你自行到决定点，插件负责搜索、倒计时和一次按键；凤王按 ↑，其他目标按 A。不检测站位、朝向、对象或 B 键。",
                "超梦停在对话的按键等待；三鸟停在面前；甜甜香气停在队伍菜单该选项；钓鱼自行完成咬钩，停在最终确认。参考 Offset 按目标预填，野生首次需校准。",
                "倒计时与按键时机奇偶不一致显示黄色，一致且可触发显示绿色；不因颜色变化提前换目标。错过后红色 D 保留约 1 秒，再在原范围续搜。C0000000 表示已发按键，E 范围耗尽 / F 计数失效。",
                "捕获后把目标留在队伍中，游戏内保存，再用下方工具核对。软重启或关闭游戏会清除注入，需重新安装。",
            ),
            fields=(
                *common,
                Field(
                    "--start",
                    "起始 advance",
                    "number",
                    default="10000",
                    help="以本次标题重新播种的实际初始 seed 为 0；不是从进入地图归零。",
                ),
                Field(
                    "--end",
                    "结束 advance（含）",
                    "number",
                    default="200000",
                    help="最大 9999999；定点为首次 PID 抽取前，野生为遭遇槽位抽取前。",
                ),
                *(Field(
                    offset_flag(key),
                    "额外 Offset（advances）",
                    "number",
                    default=str(default_offset(key)),
                    when=("--target", key),
                    bounds=(0, 65533),
                    help="按目标预填并分别保存；0..65533，在基础时机上额外提前。参考预设仍可校准；野生首次需校准。",
                ) for key in ENCOUNTERS),
                Field("--method", "生成方式", "choice", default="1",
                      choices=(("1", "1 / H1（默认）"), ("2", "2 / H2"), ("4", "4 / H4"))),
                Field("--chamber", "未知图腾房间", "choice", default="monean",
                      choices=tuple((key, key.title()) for key in UNOWN_CHAMBERS), when=("--target", "unown")),
                Field("--nature", "性格（留空不限）", help="中文名、英文名或 0..24。首测留空。"),
                Field(
                    "--iv-min",
                    "IV 下限",
                    default="0,0,0,0,0,0",
                    help="HP,攻击,防御,特攻,特防,速度。首测保留默认。",
                ),
                Field(
                    "--iv-max", "IV 上限", default="31,31,31,31,31,31", help="HP,攻击,防御,特攻,特防,速度。"
                ),
                Field("--allow-normal", "允许非闪光（首轮按 A 测试可打开）", "switch", default=False),
                Field(
                    "--enable-auto-a",
                    "安装并启用到点按键",
                    "switch",
                    default=True,
                    help="自行停在决定点，无需按住 B；凤王发 ↑，其余发 A。首测允许非闪光，性格 / IV 不限。仅预览不连接掌机。",
                ),
                Field("--preview", "仅预览配置（不连接掌机）", "switch", default=False),
            ),
        ),
    )
    api.add_tool(
        "frlg",
        Tool(
            "frlg-rng-assist-verify",
            "RNG：核对捕获结果",
            "verify.py",
            "读取游戏最后保存的队伍，核对闪光、PID、性格、六项 IV 和生成模型，并保存报告。",
            (
                "把刚捕获的目标放进队伍，先在游戏里保存。指定种类时自动选择唯一同种目标；野生 / 自定目标默认选队尾。",
                "掌机：Mystery Gift → Wonder Cards → Friend，选择 POKELDN，等待读取完毕。",
                "已有 .pk3/.ek3 或队伍采集文件时可在高级选项中导入；导入模式不连接掌机。",
            ),
            fields=(
                *common,
                Field(
                    "--slot", "队伍位置", "number", default="0", help="0 自动选择（野生 / 自定为队尾）；1..6 指定位置。"
                ),
                Field("--installation", "关联安装报告（可选）", "file", exts=("json",), hidden=True),
                Field(
                    "--initial-seed",
                    "地图按 L 显示的初始 seed（可选）",
                    hidden=True,
                    help="同时关联安装报告时，可核对实际生成的绝对 advance 是否在范围内。",
                ),
                Field("--pokemon", "导入 .pk3 / .ek3（可选）", "file", exts=("pk3", "ek3"), hidden=True),
                Field("--party-dump", "导入队伍 dump（可选）", "file", exts=("bin",), hidden=True),
                Field(
                    "--nature",
                    "核对性格（可选）",
                    hidden=True,
                    help="留空继承关联安装报告；也支持中文名、英文名或 0..24。",
                ),
                Field("--pid", "核对 PID（可选）", hidden=True),
                Field(
                    "--iv-min",
                    "核对 IV 下限（可选）",
                    hidden=True,
                    help="留空继承关联安装报告；顺序 HP,攻击,防御,特攻,特防,速度。",
                ),
                Field("--iv-max", "核对 IV 上限（可选）", hidden=True),
                Field("--allow-normal", "允许非闪光（按 A 测试结果）", "switch", default=False, hidden=True),
            ),
        ),
    )
    api.add_tool(
        "frlg",
        Tool(
            "frlg-rng-assist-search",
            "RNG：离线目标搜索",
            "search.py",
            "按闪光、性格、PID 和 IV 搜索定点 Method 1/2/4、野生 H1/H2/H4 或未知图腾。",
            (
                "无需操作掌机。输入待分析的 seed 与游戏实际 TID/SID。",
                "结果单位为 RNG advances。Mystery Gift 的 seed 无法带回地图使用；本工具不设置自动 A。",
            ),
            fields=(
                Field("--seed", "起始 seed（十六进制）", required=True),
                Field("--tid", "游戏 TID", "number", required=True),
                Field("--sid", "游戏 SID", "number", required=True),
                Field("--model", "遭遇模型", "choice", default="static",
                      choices=(("static", "定点 / 礼物"), ("wild", "野生"), ("unown", "未知图腾"))),
                Field("--area", "野生槽位表", "choice", default="land", when=("--model", "wild"),
                      choices=(("land", "草地 / 洞窟 / 碎岩"), ("surf", "水面"),
                               ("old", "破旧钓竿"), ("good", "好钓竿"), ("super", "厉害钓竿"))),
                Field("--chamber", "未知图腾房间", "choice", default="monean", when=("--model", "unown"),
                      choices=tuple((key, key.title()) for key in UNOWN_CHAMBERS)),
                Field(
                    "--method",
                    "生成模型",
                    "choice",
                    default="1",
                    choices=(("1", "1 / H1"), ("2", "2 / H2"), ("4", "4 / H4")),
                ),
                Field("--start", "起始 advance", "number", default="0"),
                Field("--advances", "候选数量", "number", default="100000"),
                Field("--max-results", "结果上限", "number", default="10"),
                Field("--any-shininess", "包含非闪光", "switch", default=False),
                Field("--nature", "性格（可选）", help="中文名、英文名或 0..24。"),
                Field("--pid", "确切 PID（可选）"),
                Field("--iv-min", "IV 下限", default="0,0,0,0,0,0", help="HP,攻击,防御,特攻,特防,速度。"),
                Field("--iv-max", "IV 上限", default="31,31,31,31,31,31"),
                Field("--output", "报告保存路径", hidden=True),
            ),
        ),
    )
    api.add_tool(
        "frlg",
        Tool(
            "frlg-rng-assist-recover",
            "RNG：PID / IV 反推",
            "recover.py",
            "由实际 PID 与 IV 反推出可能的生成前状态；可核对同一 RNG 时段内的消耗距离。",
            (
                "无需操作掌机。输入实际宝可梦的 PID 和六项 IV。",
                "参考 seed 可留空。反推状态属于过去的生成过程，不是可继续使用的实机读数。",
            ),
            fields=(
                Field("--pid", "实际 PID（十六进制）", required=True),
                Field("--ivs", "实际 IV", required=True, help="HP,攻击,防御,特攻,特防,速度。"),
                Field("--reference-seed", "同一时段的参考 seed（可选）"),
                Field("--max-offset", "最大消耗距离", "number", default="4096"),
                Field("--output", "报告保存路径", hidden=True),
            ),
        ),
    )
