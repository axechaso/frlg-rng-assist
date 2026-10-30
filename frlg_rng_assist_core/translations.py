"""English / Japanese UI copy keyed by the original Chinese text."""

TEXT = {
    "捕获搜索\t{mode}": ("Capture search\t{mode}", "捕獲検索\t{mode}"),
    "已预载": ("Preloaded", "読み込み済み"), "未启用": ("Disabled", "無効"),
    "捕获 Offset\t{first}..{last} advances（独立于生成 Offset）": (
        "Capture offset\t{first}..{last} advances (separate from generation offset)",
        "捕獲Offset\t{first}..{last}消費（生成Offsetとは別）"),
    "预载出闪后的捕获搜索": ("Preload capture search after the encounter", "遭遇後の捕獲検索を事前に読み込む"),
    "固定最低阈值 16643。手动停在球的最后一次使用确认处，用 R+SELECT 启动 / 取消。": (
        "Fixed minimum threshold 16643. Stop at the ball's final Use confirmation; R+SELECT starts / cancels.",
        "最低しきい値16643で固定。ボールの最後の「つかう」で待機し、R+SELECTで開始・中止します。"),
    "捕获 Offset 下限": ("Capture offset minimum", "捕獲Offsetの下限"),
    "捕获 Offset 上限（留空等于下限）": ("Capture offset maximum (blank = minimum)", "捕獲Offsetの上限（空欄＝下限）"),
    "捕获球种": ("Capture ball", "捕獲ボール"),
    "精灵球": ("Poké Ball", "モンスターボール"),
    "高级球": ("Ultra Ball", "ハイパーボール"),
    "精灵球阈值 16643；高级球（Ultra Ball）阈值 19784。": (
        "Poké Ball threshold 16643; Ultra Ball threshold 19784.",
        "モンスターボールのしきい値は16643、ハイパーボールは19784です。"),
    "从 A 回调 seed 到首次摇球判定前；独立于生成 Offset。241 为参考起点，须按本插件校准。": (
        "Advances from the A callback seed to before the first shake roll; separate from generation offset. "
        "241 is a reference starting point; calibrate with this plugin.",
        "A入力コールバックのseedから最初の揺れ判定直前までの消費数。生成Offsetとは別です。"
        "241は参考値で、このプラグインでの実測調整が必要です。"),
    "整个偏移带的所有起点都须四次成功；上下限之差最多 12 advances。": (
        "All four checks must pass at every offset in the band. Maximum width: 12 advances.",
        "範囲内の全ての起点で4回とも成功する必要があります。上下限の差は最大12消費です。"),
    "勾选预载捕获后，出闪并停在球的最后一次使用确认处，按 R+SELECT 启动，再按取消；无需重新注入。": (
        "With capture preloaded, stop at the ball's final Use confirmation after the encounter; "
        "R+SELECT starts / cancels. No reinjection is needed.",
        "捕獲機能を事前に読み込み、遭遇後にボールの最後の「つかう」で待機。"
        "R+SELECTで開始・中止でき、再注入は不要です。"),
    "已预载捕获搜索：出闪后停在球的最后一次使用确认处，按 R+SELECT 启动，再按取消；无需重新注入。": (
        "Capture preloaded: after the encounter, stop at the ball's final Use confirmation. "
        "R+SELECT starts / cancels; no reinjection is needed.",
        "捕獲検索を読み込み済み。遭遇後、ボールの最後の「つかう」でR+SELECTを押すと開始、"
        "もう一度で中止。再注入は不要です。"),
    "捕获阈值固定 16643；独立 Offset={first}..{last} advances。241 仅为参考起点，须按本插件校准。": (
        "Capture threshold fixed at 16643; separate offset={first}..{last} advances. "
        "241 is only a reference starting point; calibrate with this plugin.",
        "捕獲しきい値16643で固定。独立したOffset={first}..{last}消費。"
        "241は参考値で、このプラグインでの実測調整が必要です。"),
    "捕获球种={ball}，阈值={threshold}；独立 Offset={first}..{last} advances。241 仅为参考起点，须按本插件校准。": (
        "Capture ball={ball}, threshold={threshold}; separate offset={first}..{last} advances. "
        "241 is only a reference starting point; calibrate with this plugin.",
        "捕獲ボール={ball}、しきい値={threshold}。独立したOffset={first}..{last}消費。"
        "241は参考値で、このプラグインでの実測調整が必要です。"),
    "捕获下排 8=搜索，9=投球倒计时，C=已发一次 A，E=取消或耗尽；错过先显示红色 D 再续搜。": (
        "Capture lower row: 8=search, 9=countdown, C=one A sent, E=cancelled / exhausted; "
        "a miss displays red D before retrying.",
        "捕獲時の下段：8=検索、9=投球カウントダウン、C=Aを1回送信、E=中止・範囲終了。"
        "逃した場合は赤いDを表示してから再検索します。"),
    "捕获开关必须是布尔值": ("Capture switch must be boolean", "捕獲スイッチは真偽値で指定してください"),
    "捕获球种必须是 poke 或 ultra": ("Capture ball must be poke or ultra", "捕獲ボールはpokeまたはultraです"),
    "捕获 Offset 上下限之差不能超过 12 advances": (
        "Capture offset width cannot exceed 12 advances", "捕獲Offsetの上下限の差は12消費以内にしてください"),
    "游戏": ("Game", "ゲーム"), "火红": ("FireRed", "ファイアレッド"), "叶绿": ("LeafGreen", "リーフグリーン"),
    "类别": ("Category", "カテゴリ"), "目标": ("Target", "対象"), "遭遇方式": ("Encounter type", "遭遇方法"),
    "生成方式": ("Generation method", "生成方式"), "不限": ("Any", "指定なし"),
    "御三家": ("Starters", "御三家"), "化石": ("Fossils", "化石"),
    "礼物 / 购买": ("Gifts / purchases", "もらう・購入"), "游戏厅": ("Game Corner", "ゲームコーナー"),
    "普通定点": ("Stationary", "通常の固定シンボル"), "传说定点": ("Legendaries", "伝説の固定シンボル"),
    "活动定点": ("Events", "イベント"), "游走初始化": ("Roamer initialization", "徘徊ポケモンの初期化"),
    "野生": ("Wild", "野生"), "未知图腾": ("Unown", "アンノーン"),
    "其他定点 / 礼物": ("Other stationary / gift", "その他の固定・もらうポケモン"),
    "野生地点 · 预设 Offset（火红 / 叶绿）": ("Wild location · preset Offset (FireRed / LeafGreen)", "野生の場所・既定 Offset（FR / LG）"),
    "斜杠左侧火红、右侧叶绿。选定后自动使用对应游戏的值；未知为 256。":
        ("FireRed is left of /, LeafGreen is right. The selected game's preset is applied automatically; unknown values use 256.",
         "左がFR、右がLGです。選択したゲームの既定値を使用し、不明な値は256とします。"),
    "野生宝可梦": ("Wild Pokémon", "野生ポケモン"),
    "筛选物种时须选择具体楼层 / 区域及正确游戏、遭遇方式；不在该表中的物种会在安装前提示。":
        ("To filter species, select the exact floor / area, game and encounter type. Unavailable species are refused before installation.",
         "種類を絞り込む場合は階・区画、ゲーム、遭遇方法を正しく選んでください。出現しない種類は注入前にエラーになります。"),
    "未知图腾房间": ("Unown chamber", "アンノーンの石室"),
    "手动 Offset（留空使用上方预设）": ("Manual Offset (blank uses preset)", "手動 Offset（空欄で既定値）"),
    "目标 / 地点后的数字即默认值，随游戏自动选用；校准时填 0..65533 覆盖，单位为 RNG advances。":
        ("Numbers beside targets / locations are presets. To calibrate, override with 0..65533 RNG advances.",
         "対象・場所の横の数値が既定値です。調整時は0..65533の乱数消費数で上書きできます。"),
    "RNG：搜索与到点按键": ("RNG: search and timed input", "RNG：検索と時刻指定入力"),
    "从实际初始 seed 搜索范围和个体条件，到点按一次键：凤王 ↑，其他目标 A。":
        ("Search from the actual initial seed with range and IV filters, then press once: UP for Ho-Oh, A for other targets.",
         "実際の初期seedから範囲と個体条件で検索し、時刻になったら一度だけ入力します。ホウオウは↑、その他はAです。"),
    "起始 advance": ("First advance", "開始消費数"), "结束 advance（含）": ("Last advance (inclusive)", "終了消費数（含む）"),
    "从本次标题重新播种的实际初始 seed 起算，初始 seed 为 0。":
        ("Count from this title screen's actual initial seed; that seed is advance 0.", "今回のタイトル画面で決まった実際の初期seedを消費数0として数えます。"),
    "定点为首次 PID 抽取前，野生为遭遇槽位抽取前。":
        ("Stationary: before the first PID draw. Wild: before the encounter-slot draw.", "固定は最初のPID抽選前、野生は遭遇スロット抽選前の消費数です。"),
    "性格（留空不限）": ("Nature (blank for any)", "性格（空欄で指定なし）"),
    "IV 下限": ("Minimum IVs", "個体値の下限"), "IV 上限": ("Maximum IVs", "個体値の上限"),
    "HP,攻击,防御,特攻,特防,速度。": ("HP, Attack, Defense, Sp. Atk, Sp. Def, Speed.", "HP、攻撃、防御、特攻、特防、素早さ。"),
    "允许非闪光（首轮按键测试可打开）": ("Allow non-shiny (use for initial input tests)", "色違い以外も許可（初回の入力確認用）"),
    "安装并启用到点按键": ("Install and enable timed input", "注入して時刻指定入力を有効にする"),
    "仅预览配置（不连接掌机）": ("Preview configuration (offline)", "設定のプレビューのみ（接続しない）"),
    "卡带构建": ("Cartridge build", "カートリッジのビルド"),
    "自动识别英文 / 法文 rev 0A，BPRE / BPRF / BPGE / BPGF。":
        ("Automatically detect English / French rev 0A: BPRE / BPRF / BPGE / BPGF.", "英語・フランス語版rev 0Aを自動判定：BPRE / BPRF / BPGE / BPGF。"),
    "Radio 覆盖": ("Radio override", "Radioの上書き"), "报告保存路径": ("Report path", "レポート保存先"),
    "RNG：PID 反查实际命中": ("RNG: find actual hit from PID", "RNG：PIDから実際の消費数を逆算"),
    "输入本轮初始 seed 和队尾实际 PID，反查范围内的命中 advance；可对照目标计算 Offset 修正。":
        ("Manually enter this attempt's initial seed and tail PID to find actual advances and optionally calculate an Offset correction.",
         "今回の初期seedと手持ち末尾の実際のPIDを手入力し、範囲内の消費数を逆算します。Offsetの補正も計算できます。"),
    "本轮初始 seed（十六进制）": ("Initial seed for this attempt (hex)", "今回の初期seed（16進数）"),
    "实际 PID（十六进制）": ("Actual PID (hex)", "実際のPID（16進数）"),
    "反查起始 advance": ("First advance to check", "逆算の開始消費数"),
    "反查结束 advance（含）": ("Last advance to check (inclusive)", "逆算の終了消費数（含む）"),
    "原目标 advance（可选，用于 Offset 修正）": ("Planned advance (optional, for Offset correction)", "元の目標消費数（任意・Offset補正用）"),
    "留空只反查命中；填写 0..9999999 以计算误差。":
        ("Leave blank to find hits only; enter 0..9999999 to calculate the error.", "空欄では消費数のみ逆算します。誤差を計算する場合は0..9999999を入力してください。"),
    "先在目标附近保存，OPTIONS → BUTTON MODE 设为 L/R，重新启动并清除其他 boosts。":
        ("Save near the target, set OPTIONS → BUTTON MODE to L/R, then restart to clear other boosts.",
         "対象の近くで保存し、OPTIONS → BUTTON MODEをL/Rに設定して再起動し、他のboostを解除してください。"),
    "Mystery Gift → Wonder Cards → Friend，选择 POKELDN，等待日志确认安装回执；退出到标题，再继续游戏。":
        ("Mystery Gift → Wonder Cards → Friend → POKELDN. Wait for the installation receipt, return to the title, then Continue.",
         "Mystery Gift → Wonder Cards → FriendでPOKELDNを選び、注入の受領確認を待ちます。タイトルへ戻り、つづきから始めてください。"),
    "上排当前 seed，下排 A 搜索 / B 倒计时；L 查看初始 seed 和绝对 advances；L+R 查看队尾 PID 和队伍位置。":
        ("Top: current seed. Bottom: A searching / B countdown. L: initial seed and absolute advances. L+R: tail PID and party position.",
         "上段は現在seed、下段はA=検索/B=カウントダウン。Lで初期seedと総消費数、L+Rで末尾のPIDと位置を表示します。"),
    "R 查看队尾 IV / 觉醒力量：上排 HP、攻击、防御、速度；下排特攻、特防、属性编号、威力，每项两位十进制。":
        ("R: tail IVs / Hidden Power. Top: HP, Atk, Def, Speed. Bottom: SpA, SpD, type number, power. Each value is two decimal digits.",
         "Rで末尾の個体値・めざめるパワー。上段はHP/攻撃/防御/素早さ、下段は特攻/特防/タイプ番号/威力。各2桁の10進数です。"),
    "觉醒属性 01..16：格斗、飞行、毒、地面、岩石、虫、幽灵、钢、火、水、草、电、超能、冰、龙、恶。":
        ("Hidden Power types 01..16: Fighting, Flying, Poison, Ground, Rock, Bug, Ghost, Steel, Fire, Water, Grass, Electric, Psychic, Ice, Dragon, Dark.",
         "タイプ01..16：かくとう/ひこう/どく/じめん/いわ/むし/ゴースト/はがね/ほのお/みず/くさ/でんき/エスパー/こおり/ドラゴン/あく。"),
    "自行停在决定点等待；不需要按住 B。甜香停在队伍菜单的选项；钓鱼自行完成咬钩；凤王停在触发格南侧朝上。":
        ("Wait at the decision point; holding B is unnecessary. Sweet Scent: its party-menu option. Fishing: complete earlier bites. Ho-Oh: face north below the trigger tile.",
         "決定点で待ち、Bを押し続ける必要はありません。あまいかおりは手持ちの技選択、釣りは前段階を手動で完了、ホウオウは発動マスの南で北向きです。"),
    "黄色表示按键时机奇偶不符，绿色表示一致；错过后红色 D 保留约 1 秒再续搜。C 已发按键，E 范围耗尽，F 计数失效。":
        ("Yellow: input parity differs. Green: parity agrees. A miss shows red D for about one second, then searches again. C: input sent; E: range exhausted; F: invalid count.",
         "黄色は入力時刻の偶奇不一致、緑色は一致。逃すと赤いDを約1秒表示して再検索します。C=入力送信、E=範囲終了、F=カウント無効。"),
    "捕获后按 L+R 读实际 PID，用下方 PID 反查核对。软重启 / 关闭游戏会清除注入，下一轮需重新安装。":
        ("After capture, read the actual PID with L+R and check it in PID lookup. A soft reset / game exit clears the injection; reinstall for another attempt.",
         "捕獲後にL+Rで実際のPIDを読み、逆算ツールで確認してください。ソフトリセット・ゲーム終了で注入は消えるため、次回は再注入が必要です。"),
    "无需连接掌机。L 读取本轮初始 seed，L+R 读取队尾 PID，填入下面两个十六进制数。":
        ("No console connection is needed. Read the initial seed with L and tail PID with L+R, then manually enter both hexadecimal values below.",
         "接続は不要です。Lで初期seed、L+Rで手持ち末尾のPIDを読み、下の2欄へ16進数で手入力してください。"),
    "类别、目标、生成方式与实机搜索保持一致；填写搜索范围。野生可能存在多个遭遇起点，所有候选都会列出。":
        ("Use the same category, target and method as the live search, and enter the range. Wild encounters can have multiple starts; all candidates are listed.",
         "実機検索と同じカテゴリ・対象・方式を選んで範囲を入力します。野生では複数の遭遇開始点が候補になるため、すべて表示します。"),
    "可填写原目标 advance 计算误差与建议 Offset。建议以重复实测核对，单次 PID 不证明自动按键成功。":
        ("Optionally enter the planned advance for an error and suggested Offset. Confirm with repeated measurements; a PID alone does not prove input success.",
         "元の目標消費数を入力すると誤差と推奨Offsetを計算します。繰り返し実測し、PIDだけで自動入力成功と判断しないでください。"),
    "停在最后一次确认的位置，等待插件按 A。": ("Wait at the final confirmation for the plugin's A input.", "最後の決定点でプラグインのA入力を待ってください。"),
    "对话结束后，停在文字框等待按键的位置。": ("Stop at the final dialogue's button wait.", "会話の最後のボタン待ちで止めてください。"),
    "站在急冻鸟面前，等待自动 A 开始对话。": ("Face Articuno and wait for A to begin the dialogue.", "フリーザーの前で向き合い、会話開始のAを待ってください。"),
    "停在选择这只御三家的最后 Yes 确认。": ("Stop at the starter's final Yes confirmation.", "御三家を選ぶ最後の「はい」で止めてください。"),
    "停在购买鲤鱼王的最后 Yes 确认。": ("Stop at the Magikarp purchase's final Yes.", "コイキング購入の最後の「はい」で止めてください。"),
    "站在伊布精灵球前，等待自动 A。": ("Wait in front of Eevee's Poké Ball for A.", "イーブイのボールの前でAを待ってください。"),
    "停在接受飞腿郎的最后确认。": ("Stop at the final confirmation to receive Hitmonlee.", "サワムラーを受け取る最後の確認で止めてください。"),
    "停在接受快拳郎的最后确认。": ("Stop at the final confirmation to receive Hitmonchan.", "エビワラーを受け取る最後の確認で止めてください。"),
    "停在吹笛后最后一段文字的确认处。": ("Stop at the final text confirmation after playing the flute.", "笛を吹いた後、最後の文章の確認で止めてください。"),
    "停在触发引梦貘人事件的最后一次确认。": ("Stop at the final confirmation that triggers Hypno.", "スリーパーのイベントを始める最後の確認で止めてください。"),
    "停在接受蛋的最后一次确认。": ("Stop at the final confirmation to receive the Egg.", "タマゴを受け取る最後の確認で止めてください。"),
    "停在一岛任务结束、初始化游走宝可梦前的最后确认；不是野外遇见它时。":
        ("Stop at the final confirmation before initializing the roamer after One Island's quest, not a later wild encounter.",
         "１のしまの用事の後、徘徊ポケモンを初期化する最後の確認で止めます。後の野生遭遇時ではありません。"),
    "完成三角谜题，停在最后一次触碰三角前。": ("Solve the triangle puzzle and stop before its last touch.", "三角形の謎を解き、最後に触れる直前で止めてください。"),
    "站在洛奇亚面前，等待自动 A。": ("Face Lugia and wait for A.", "ルギアの前で向き合い、Aを待ってください。"),
    "停在凤王触发格南边相邻一格并朝上，等待自动 ↑ 走一步。":
        ("Face north one tile south of Ho-Oh's trigger tile and wait for one UP step.", "ホウオウの発動マスの1マス南で北を向き、↑の1歩を待ってください。"),
    "停在领取复活宝可梦前的最后一段文字。": ("Stop at the final text before receiving the revived Pokémon.", "復元したポケモンを受け取る直前の文章で止めてください。"),
    "选好奖品，停在兑换的最后 Yes 确认。": ("Choose the prize, then stop at the exchange's final Yes.", "景品を選び、交換の最後の「はい」で止めてください。"),
    "甜香停在队伍菜单的甜甜香气选项；钓鱼自行完成咬钩，停在最后确认；其他方式自行停在最后 A 决定点。":
        ("Sweet Scent: wait on its party-menu option. Fishing: complete earlier bites and wait at the final confirmation. Otherwise stop at the final A decision point.",
         "あまいかおりは手持ちの技選択、釣りは前段階を手動で済ませて最後の確認、その他は最後のA決定点で止めてください。"),
    "购买": ("Purchase", "購入"), "玉虹市礼物": ("Celadon gift", "タマムシでもらう"),
    "格斗道场": ("Fighting Dojo", "かくとうどうじょう"), "12 号道路": ("Route 12", "12ばんどうろ"),
    "16 号道路": ("Route 16", "16ばんどうろ"), "树果森林": ("Berry Forest", "きのみのもり"),
    "赠蛋": ("Gift Egg", "もらうタマゴ"), "游走个体初始化": ("Roamer initialization", "徘徊ポケモンの初期化"),
    "发电厂，两处通用": ("Power Plant, both spots", "むじんはつでんしょ・両方共通"),
    "西尔佛公司": ("Silph Co.", "シルフカンパニー"),
    "野生：甜甜香气（草地 / 洞窟）": ("Wild: Sweet Scent (grass / cave)", "野生：あまいかおり（草むら・洞窟）"),
    "野生：甜甜香气（水面）": ("Wild: Sweet Scent (surfing)", "野生：あまいかおり（水上）"),
    "野生：破旧钓竿": ("Wild: Old Rod", "野生：ボロのつりざお"),
    "野生：好钓竿": ("Wild: Good Rod", "野生：いいつりざお"),
    "野生：厉害钓竿": ("Wild: Super Rod", "野生：すごいつりざお"),
    "野生：碎岩（最后 A 确认）": ("Wild: Rock Smash (final A)", "野生：いわくだき（最後のA）"),
    "野生：未知图腾（阿斯卡纳遗迹）": ("Wild: Unown (Tanoby Ruins)", "野生：アンノーン（アスカナいせき）"),
    "其他定点 / 礼物（自定 Offset）": ("Other stationary / gift (custom Offset)", "その他の固定・もらうポケモン（手動Offset）"),
    "其他地点 / 未知": ("Other / unknown location", "その他・不明な場所"),
    "月见山": ("Mt. Moon", "おつきみやま"), "宝可梦塔 4F–7F": ("Pokémon Tower 4F–7F", "ポケモンタワー 4F–7F"),
    "狩猎地带（各区）": ("Safari Zone (all areas)", "サファリゾーン（全区画）"),
    "宝可梦屋（各层）": ("Pokémon Mansion (all floors)", "ポケモンやしき（全階）"),
    "冠军之路（各层）": ("Victory Road (all floors)", "チャンピオンロード（全階）"),
    "灯火山": ("Mt. Ember", "ともしびやま"), "冻瀑洞窟": ("Icefall Cave", "いてだきのどうくつ"),
    "华蓝洞窟": ("Cerulean Cave", "ハナダのどうくつ"), "岩山隧道": ("Rock Tunnel", "イワヤマトンネル"),
    "双子岛": ("Seafoam Islands", "ふたごじま"), "不归之穴": ("Lost Cave", "かえらずのあな"),
    "七宝溪谷": ("Sevault Canyon", "しっぽうけいこく"), "阿斯卡纳遗迹（水面）": ("Tanoby Ruins (water)", "アスカナいせき（水上）"),
    "筛选野生宝可梦时请选择具体楼层 / 区域，不能使用未知地点或合并地点。":
        ("Select an exact floor / area to filter wild species; unknown or grouped locations cannot be used.", "野生の種類を絞る場合は具体的な階・区画を選んでください。不明・まとめた場所は使用できません。"),
    "所选游戏、地点和遭遇方式没有这种宝可梦；请更换条件。":
        ("This species is not in the selected game's location / encounter table. Change the selection.", "選択したゲーム・場所・遭遇方法ではこの種類は出現しません。条件を変更してください。"),
    "物种筛选只用于普通野生遭遇。": ("Species filtering applies only to ordinary wild encounters.", "種類の絞り込みは通常の野生遭遇専用です。"),
    "未知图腾请使用「未知图腾」类别并选择房间，不能使用普通野生物种筛选。":
        ("For Unown, use the Unown category and select its chamber instead of the ordinary wild species filter.",
         "アンノーンは通常の野生の絞り込みではなく、アンノーンカテゴリで石室を選んでください。"),
    "唯一命中": ("Unique hit", "候補は1件"), "多个候选，请缩小范围": ("Multiple candidates; narrow the range", "複数候補・範囲を絞ってください"),
    "范围内无匹配": ("No match in range", "範囲内に一致なし"), "PID 反查实际命中": ("Actual advances from PID", "PIDから実際の消費数を逆算"),
    "结果": ("Result", "結果"), "候选": ("Candidates", "候補"), "报告": ("Report", "レポート"),
    "实际 advance {advance} | 生成前 seed {seed:08X} | {nature} | 预测 IV {ivs}":
        ("Actual advance {advance} | pre-generation seed {seed:08X} | {nature} | predicted IVs {ivs}",
         "実際の消費数 {advance} | 生成前seed {seed:08X} | {nature} | 予測個体値 {ivs}"),
    "与原目标相差 {error:+d} advances；建议额外 Offset {offset}。":
        ("Difference from plan: {error:+d} advances; suggested extra Offset: {offset}.", "目標との差は{error:+d}消費、推奨追加Offsetは{offset}です。"),
    "IV 为所选生成方式的预测值；实际值可在掌机按 R 查看。":
        ("IVs are predictions for the selected method; hold R on the console to read actual IVs.", "個体値は選んだ方式の予測値です。実際の値は実機でRを押して確認できます。"),
    "预测物种：{species}（#{number:03d}）": ("Predicted species: {species} (#{number:03d})", "予測される種類：{species}（#{number:03d}）"),
    "筛选物种：{species}（#{number:03d}）": ("Species filter: {species} (#{number:03d})", "種類の条件：{species}（#{number:03d}）"),
    "正在安装 {target}。在掌机选择 Mystery Gift → Wonder Cards → Friend。":
        ("Installing {target}. On the console, select Mystery Gift → Wonder Cards → Friend.",
         "{target}の設定を注入します。実機でMystery Gift → Wonder Cards → Friendを選んでください。"),
    "预览已生成：{path}。本次没有连接掌机。":
        ("Preview created: {path}. No console connection was made.", "プレビューを作成しました：{path}。実機には接続していません。"),
    "安装回执已确认。退出 Mystery Gift，返回标题，再选择继续游戏。":
        ("Installation receipt confirmed. Leave Mystery Gift, return to the title, then Continue.",
         "注入の受領を確認しました。Mystery Giftを終了し、タイトルからつづきで始めてください。"),
    "L/R 打开帮助时，先将 OPTIONS → BUTTON MODE 设为 L/R 并保存；本插件不单独识别 ZL/ZR。":
        ("If L/R opens Help, save OPTIONS → BUTTON MODE as L/R first. ZL/ZR are not separate inputs in this plugin.",
         "L/Rでヘルプが開く場合は、先にOPTIONS → BUTTON MODEをL/Rにして保存してください。ZL/ZRは別の入力として扱いません。"),
    "额外 Offset={offset} advances；合计在目标生成前 {total} advances 排定 {button}。":
        ("Extra Offset={offset} advances; schedule {button} a total of {total} advances before generation.",
         "追加Offsetは{offset}消費、生成の合計{total}消費前に{button}を入力します。"),
    "自行停在决定点，插件到点按一次 {button}；不检测站位、朝向、对象、脚本等待或 B 键。":
        ("Wait at the decision point for one {button} input. Position, facing, objects, script waits and B are not checked.",
         "決定点で{button}の1回の入力を待ってください。位置・向き・対象・スクリプト待ち・Bは確認しません。"),
    "野生 H{method}：范围按遭遇槽位抽取前计数，包含性格 / PID 重抽。Offset 首次需校准。":
        ("Wild H{method}: count before the slot draw, including nature / PID rerolls. Calibrate Offset on the first attempt.",
         "野生H{method}：スロット抽選前から数え、性格・PID再抽選を含みます。初回にOffsetを調整してください。"),
    "此 Offset 是参考预设，尚未在这个决定点做实机校准；先允许非闪光测试实际 PID。":
        ("This Offset is a reference preset, uncalibrated at this decision point. Allow non-shiny first and check the actual PID.",
         "このOffsetは実機で未調整の参考値です。まず色違い以外も許可し、実際のPIDを確認してください。"),
    "C0000001=等待注入，C0000000=已注入 {button}；是否实际触发仍须观察。":
        ("C0000001=input pending; C0000000={button} sent. Observe whether the game actually responds.",
         "C0000001=入力待ち、C0000000={button}送信済み。実際に反応したかは画面で確認してください。"),
    "续搜保留初始 seed 和筛选条件，不补按旧目标。发送一次按键后结束；E=范围耗尽，F=计数失效，也会结束。":
        ("A resumed search keeps the initial seed and filters. Expired targets are not pressed. One input, E or F ends the attempt.",
         "再検索は初期seedと条件を保持し、過ぎた目標には入力しません。1回の入力、E、Fで今回の試行は終了します。"),
    "实机 RNG 搜索": ("Console RNG search", "実機RNG検索"),
    "触发按键": ("Trigger input", "発動入力"), "状态": ("Status", "状態"),
    "仅预览": ("Preview only", "プレビューのみ"), "安装回执已确认": ("Receipt confirmed", "受領確認済み"),
    "范围\t{first}..{last} advances（从标题初始 seed 起算）":
        ("Range\t{first}..{last} advances from the title seed", "範囲\tタイトルの初期seedから{first}..{last}消費"),
    "额外 Offset\t{offset} advances（总提前量 {total}）":
        ("Extra Offset\t{offset} advances (total lead {total})", "追加Offset\t{offset}消費（合計先行消費数{total}）"),
    "实机验证\t尚未完成": ("Hardware validation\tPending", "実機検証\t未完了"),
    "捕获结果\t等待核对": ("Capture result\tAwaiting verification", "捕獲結果\t確認待ち"),
    "每项 IV 下限必须不大于上限": ("Each minimum IV must be no greater than its maximum.", "個体値の下限は各上限以下にしてください。"),
    "需要六项 IV，顺序为 HP / 攻击 / 防御 / 特攻 / 特防 / 速度":
        ("Enter six IVs in HP / Atk / Def / SpA / SpD / Speed order.", "HP・攻撃・防御・特攻・特防・素早さの順で6つの個体値を入力してください。"),
    "请勾选「安装并启用到点按键」；只检查配置可选择「仅预览」。":
        ("Enable timed input to install, or select Preview to check the configuration offline.", "注入時は時刻指定入力を有効にしてください。設定の確認のみならプレビューを選んでください。"),
}
