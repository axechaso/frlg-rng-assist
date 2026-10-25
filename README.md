# FRLG RNG Assist 0.3.0

PokeLDN 的第三方插件：设置 RNG advances 范围与条件，注入临时掌机程序，显示 seed / 倒计时，在超梦或三鸟的指定等待位置按一次 A。**这是待实机验证的测试版。软件模拟通过不代表掌机时序已经通过。**

首轮先按 [实机测试步骤](docs/HARDWARE_TEST_ZH.md) 测试，不限制性格或 IV，并打开「允许非闪光」。

## 安装与支持范围

- 使用 PokeLDN **v0.39.1 / 插件 API 1.11**。开发检查固定在该版本。
- 安装 `frlg-rng-assist-0.3.0.pokeplugin`：Plugins → Add a plugin；已有旧版时用插件卡片的文件更新入口。
- Games → FireRed & LeafGreen → **RNG：搜索与到点自动 A**。
- 本版只接受 Switch 火红 / 叶绿英文、法文 **rev 0A**：BPRE、BPGE、BPRF、BPGF。原版 GBA 卡带的 rev 0/1、其他语言或改版 ROM 不在本版范围内。
- ESP32 的 Wireless 固件版本与插件 API 是两回事；无需为了这个插件更换已经能正常运行 PokeLDN 的 Wireless 1.8.0。
- 无需安装 Python 或 ARM 编译器。包内附有掌机源码、生成脚本和预编译资源。

## 工作逻辑

1. PC 导出范围、目标、闪光 / 性格 / IV 条件，使用 PokeLDN 的公开 Mystery Gift 工具传输。未完整传完、校验失败或已有 resident hook 时不启用。
2. 离开 Mystery Gift 回到标题。标题按 START 后，游戏用计时器重新播种；插件读取游戏保留的**这个实际初始 seed**。Mystery Gift 会话中的 seed 不用于地图计数。
3. 以实际初始 seed 为 advance 0，读取当前 RNG 状态并算出绝对 advances。因此进入地图时一般已经不是 0。PC 配置的范围也使用这个起点。
4. 掌机在正常地图运行期间分批搜索自然 Method 1 结果，使用当前存档的 TID/SID，并读取实际 RNG 推进量。走路等额外消耗会反映到计数中；静止后也会调整到可达的后续候选。
5. 找到候选后显示到自动 A 时机的剩余 advances。只在超梦的指定按键等待，或面向三鸟并静止按住 B 时触发。超梦使用上游测得的 1 advance 偏移，三鸟使用 2 advances；这些偏移在本插件中的集成仍须实测。
6. 每次安装最多注入一次 A。目标已过、状态不符或时段失效时不补按。插件不会改 RNG、PID、IV 或存档内容。

范围包含端点，最大 `9999999`，针对**生成 PID 前**的 RNG 状态。倒计时针对**按 A**的时机，包含上述偏移；不是屏幕帧数或秒数。重新启动游戏会清除临时程序。

## 掌机显示

右上角上排显示 8 位十六进制当前 seed；下排是状态字母加 7 位十进制数字。

| 下排 | 含义 |
|---|---|
| `Axxxxxxx` | 搜索中；数字是当前搜索到的绝对 advance |
| `Bxxxxxxx` | 已找到未来候选；数字是距离按 A 的剩余 advances |
| `C0000000` | 已排定本次 A / 已触发；是否实际进入战斗仍需观察 |
| `D0000000` | 错过，或触发前位置 / RNG 改变；不再按 A |
| `E0000000` | 范围内没有剩余可用候选；不按 A |
| `F0000000` | 初始 seed 改变、回退或超出计数范围；不按 A |

**按住 L**：上排改为实际初始 seed，下排改为当前绝对 advances。松开恢复；L 不重置计数。菜单和战斗中不绘制这个显示。

## 其他工具

- **核对捕获结果**：目标放在队伍中，游戏内保存，再进 Mystery Gift 读取最后保存的队伍；也可导入 `.pk3` / `.ek3` / 608 字节队伍 dump。可关联安装报告继承条件，并输入按 L 记录的初始 seed 核对生成 advance 是否在范围内。仅核对所选宝可梦记录，不自动证明实际按键时序或捕获来源。
- **离线目标搜索**：公开 API 的 Method 1/2/4 预测，筛选闪光、性格、PID 和六项 IV。
- **PID / IV 反推**：恢复过去可能的生成状态，可比较同一时段内的距离；不把反推结果当实时读数。

IV 顺序统一为 HP、攻击、防御、特攻、特防、速度。首轮实机先保留全范围 `0..31`；IV 筛选不作为本轮验收条件。

报告与采集文件保存到 PokeLDN 的 **FRLG RNG Assist** 资料库。显式指定文件名时不覆盖已有文件。安装失败不会生成“安装成功”报告。

## 当前限制

一次只安装本插件；开始前重新启动游戏，清除其他 boosts / resident hooks。代码使用上游记录的未使用 newlib 区和 EWRAM 顶部区域，合计最多 2200 字节；已知 revision / 函数特征不符时拒绝。它不应与其他驻留扩展叠加使用。

目前自动 A 仅覆盖超梦和三鸟的这两类等待方式。其他静态、野生、蛋或礼物遭遇没有可用的自动 A 配置。范围过窄、赶路耗尽候选、额外 RNG 消耗或过迟到达等待点都可能失败。先验证「出现显示 → 倒计时 → 自动开战」，再验证闪光和筛选结果。

## 开发与检查

Python 3.13，独立 PokeLDN v0.39.1 源码目录（含其依赖），开发依赖见 `requirements-dev.txt`：

```powershell
python -m pip install -r requirements-dev.txt
$env:POKELDN_SOURCE = 'D:\path\to\pokeldn-v0.39.1'
python -m pytest -q
python -m ruff check .
```

重新编译掌机程序需要 GNU Arm Embedded GCC，并将工具目录设为 `ARM_TOOLCHAIN`（以目录分隔符结尾），或把工具加入 PATH：

```powershell
python scripts/build_guest.py
python -m pytest -q
```

`scripts/build_guest.py --check` 在相同 GCC 版本下核对已提交资源。不同编译器生成的地址和字节可以不同，重新生成后必须重新跑模拟测试。交付资源使用 GCC 15.2.1。

用 PokeLDN 自带的打包器，不向其仓库添加插件：

```powershell
python D:\path\to\pokeldn-v0.39.1\scripts\pack_plugin.py . -o dist\frlg-rng-assist-0.3.0.pokeplugin
```

验证范围和已知未测项见 [验证记录](docs/VALIDATION.md)。本项目独立开发，目前交付本地测试包，没有配置远程发布地址。

## 许可

AGPL-3.0-or-later。代码来源和上游贡献归属见 [NOTICE.md](NOTICE.md)。本插件由 axechaso 独立分发，PokeLDN 原作者不负责审核或支持。
