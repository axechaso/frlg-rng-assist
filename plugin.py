"""Registration only. Importing this file never starts a session or touches a board."""

from pokeldn.plugins import Field, Tool

from frlg_rng_assist_core.encounters import (
    CATEGORIES, ENCOUNTERS, UNOWN_CHAMBERS, WILD_LOCATIONS, default_offset,
)
from frlg_rng_assist_core.selection import method_flag, target_flag
from frlg_rng_assist_core.i18n import host_language, localized_tool
from frlg_rng_assist_core.wild_tables import names, tables


def selection_fields():
    fields = [
        Field("--game", "游戏", "choice", default="firered",
              choices=(("firered", "火红"), ("leafgreen", "叶绿"))),
        Field("--category", "类别", "choice", default="legends",
              choices=tuple((key, name) for key, (name, _) in CATEGORIES.items())),
    ]
    for category, (_, targets) in CATEGORIES.items():
        fields.append(Field(
            target_flag(category), "遭遇方式" if category == "wild" else "目标", "choice",
            default=targets[0], when=("--category", category),
            choices=tuple((key, ENCOUNTERS[key].name + (
                "" if category in ("wild", "unown") else f" · Offset {default_offset(key)}"
            )) for key in targets),
            choice_help=tuple((key, ENCOUNTERS[key].decision) for key in targets),
        ))
    fields.extend((
        Field("--location", "野生地点 · 预设 Offset（火红 / 叶绿）", "choice", default="other",
              when=("--category", "wild"),
              choices=tuple((key, f"{name} · {default_offset('sweet-land', 'firered', key)} / "
                             f"{default_offset('sweet-land', 'leafgreen', key)}")
                            for key, name in WILD_LOCATIONS),
              help="斜杠左侧火红、右侧叶绿。选定后自动使用对应游戏的值；未知为 256。"),
        Field("--species", "野生宝可梦", "choice", default="0", when=("--category", "wild"),
              choices=(("0", "不限"),) + tuple((str(n), names()["zh"][n]) for n in sorted(
                  {mon[0] for row in tables().values() for game in ("firered", "leafgreen")
                   for mons in row[game].values() for mon in mons if mon[0] != 201})),
              help="筛选物种时须选择具体楼层 / 区域及正确游戏、遭遇方式；不在该表中的物种会在安装前提示。"),
        Field("--chamber", "未知图腾房间", "choice", default="monean",
              when=("--category", "unown"), choices=tuple((key, key.title()) for key in UNOWN_CHAMBERS)),
    ))
    for category in CATEGORIES:
        wild = category in ("wild", "unown")
        fields.append(Field(
            method_flag(category), "生成方式", "choice", default="1", when=("--category", category),
            choices=tuple((str(m), f"{'H' if wild else 'Method '}{m}")
                          for m in ((1, 2, 4) if wild else (1, 4))),
        ))
    # API 1.11 rejects empty bounded numbers, including optional ones. Keep
    # optional numeric fields unbounded here; the backend checks their ranges.
    fields.append(Field(
        "--offset", "手动 Offset（留空使用上方预设）", "number",
        help="目标 / 地点后的数字即默认值，随游戏自动选用；校准时填 0..65533 覆盖，单位为 RNG advances。",
    ))
    return tuple(fields)


def register(api):
    language = host_language()

    def add_tool(game, tool):
        api.add_tool(game, localized_tool(tool, language))

    selection = selection_fields()
    add_tool("frlg", Tool(
        "frlg-rng-assist-install", "RNG：搜索与到点按键", "install.py",
        "从实际初始 seed 搜索范围和个体条件，到点按一次键：凤王 ↑，其他目标 A。",
        (
            "先在目标附近保存，OPTIONS → BUTTON MODE 设为 L/R，重新启动并清除其他 boosts。",
            "Mystery Gift → Wonder Cards → Friend，选择 POKELDN，等待日志确认安装回执；退出到标题，再继续游戏。",
            "上排当前 seed，下排 A 搜索 / B 倒计时；L 查看初始 seed 和绝对 advances；L+R 查看队尾 PID 和队伍位置。",
            "R 查看队尾 IV / 觉醒力量：上排 HP、攻击、防御、速度；下排特攻、特防、属性编号、威力，每项两位十进制。",
            "觉醒属性 01..16：格斗、飞行、毒、地面、岩石、虫、幽灵、钢、火、水、草、电、超能、冰、龙、恶。",
            "自行停在决定点等待；不需要按住 B。甜香停在队伍菜单的选项；钓鱼自行完成咬钩；凤王停在触发格南侧朝上。",
            "黄色表示按键时机奇偶不符，绿色表示一致；错过后红色 D 保留约 1 秒再续搜。C 已发按键，E 范围耗尽，F 计数失效。",
            "捕获后按 L+R 读实际 PID，用下方 PID 反查核对。软重启 / 关闭游戏会清除注入，下一轮需重新安装。",
            "勾选预载捕获后，出闪并停在球的最后一次使用确认处，按 R+SELECT 启动，再按取消；无需重新注入。",
        ),
        fields=(
            *selection,
            Field("--start", "起始 advance", "number", default="10000", bounds=(0, 9999999),
                  help="从本次标题重新播种的实际初始 seed 起算，初始 seed 为 0。"),
            Field("--end", "结束 advance（含）", "number", default="200000", bounds=(0, 9999999),
                  help="定点为首次 PID 抽取前，野生为遭遇槽位抽取前。"),
            Field("--nature", "性格（留空不限）", "choice",
                  choices=(("", "不限"),) + tuple((str(i), name) for i, name in enumerate(names()["natures"]["zh"]))),
            Field("--iv-min", "IV 下限", default="0,0,0,0,0,0", help="HP,攻击,防御,特攻,特防,速度。"),
            Field("--iv-max", "IV 上限", default="31,31,31,31,31,31", help="HP,攻击,防御,特攻,特防,速度。"),
            Field("--allow-normal", "允许非闪光（首轮按键测试可打开）", "switch", default=False),
            Field("--enable-auto-a", "安装并启用到点按键", "switch", default=True),
            Field("--capture-rng", "预载出闪后的捕获搜索", "switch", default=True,
                  help="固定最低阈值 16643。手动停在球的最后一次使用确认处，用 R+SELECT 启动 / 取消。"),
            Field("--capture-ball", "捕获球种", "choice", default="poke",
                  choices=(("poke", "精灵球"), ("ultra", "高级球")),
                  when=("--capture-rng", "True"),
                  help="精灵球阈值 16643；高级球（Ultra Ball）阈值 19784。"),
            Field("--capture-offset", "捕获 Offset 下限", "number", default="241", bounds=(0, 65532),
                  when=("--capture-rng", "True"),
                  help="从 A 回调 seed 到首次摇球判定前；独立于生成 Offset。241 为参考起点，须按本插件校准。"),
            Field("--capture-offset-max", "捕获 Offset 上限（留空等于下限）", "number",
                  when=("--capture-rng", "True"),
                  help="整个偏移带的所有起点都须四次成功；上下限之差最多 12 advances。"),
            Field("--preview", "仅预览配置（不连接掌机）", "switch", default=False),
            Field("--build", "卡带构建", default="auto", hidden=True,
                  help="自动识别英文 / 法文 rev 0A，BPRE / BPRF / BPGE / BPGF。"),
            Field("--radio", "Radio 覆盖", hidden=True),
            Field("--output", "报告保存路径", hidden=True),
        ),
    ))
    add_tool("frlg", Tool(
        "frlg-rng-assist-lookup", "RNG：PID 反查实际命中", "lookup.py",
        "输入本轮初始 seed 和队尾实际 PID，反查范围内的命中 advance；可对照目标计算 Offset 修正。",
        (
            "无需连接掌机。L 读取本轮初始 seed，L+R 读取队尾 PID，填入下面两个十六进制数。",
            "类别、目标、生成方式与实机搜索保持一致；填写搜索范围。野生可能存在多个遭遇起点，所有候选都会列出。",
            "可填写原目标 advance 计算误差与建议 Offset。建议以重复实测核对，单次 PID 不证明自动按键成功。",
        ),
        fields=(
            *selection,
            Field("--initial-seed", "本轮初始 seed（十六进制）", required=True),
            Field("--pid", "实际 PID（十六进制）", required=True),
            Field("--start", "反查起始 advance", "number", default="0", bounds=(0, 9999999)),
            Field("--end", "反查结束 advance（含）", "number", default="9999999", bounds=(0, 9999999)),
            Field("--target-advance", "原目标 advance（可选，用于 Offset 修正）", "number",
                  help="留空只反查命中；填写 0..9999999 以计算误差。"),
            Field("--output", "报告保存路径", hidden=True),
        ),
    ))
