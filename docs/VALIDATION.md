# 0.6.0 validation record

Date: 2026-10-25. **971 pytest cases passed in 124.73 s; Ruff and GCC 15.2.1 guest reproduction passed. Physical-console acceptance remains pending.**

The 64 new checks cover 132 committed versioned encounter tables; national-dex / name integrity; independent Route 1, forest, Diglett, Safari and rod-slot boundaries; game-exclusive refusal; exact-area requirements; Unown's separate model; and rejection before any gift / report is written. Real compiled ARM code tests all 100 percentile rolls on all four builds and H1/H2/H4. Species, shiny, nature and all six exact IV bounds are combined, then individually failed. Manual PID recovery uses the same species mask and reports the predicted species; selecting another valid species excludes the same start. These are synthetic-memory tests with substituted callbacks, not execution of a retail game ROM.

Translated catalogs use the actual pinned host's form validation and command builder in Chinese, Japanese and English, independently of trainer / ROM language. Tests check stable values and flags, required manual PID fields, all translated English catalog text, placeholder parity, every nature name in all three languages, localized PID / preview / IV-error output, and byte-identical generated gifts across display languages. The optional non-private host `i18n.locale()` helper is verified against v0.39.1; it is not part of the guaranteed API table and its absence falls back to English. A language change requires reloading the plugin by restarting the host.

The resident now occupies **2200 / 2200 bytes** in the unchanged 0x0203F768..0x02040000 reservation. Its configuration carries the selected species as a 100-bit percentile mask (13 bytes), checked before nature / PID rejection. The existing Unown letter list shares that field. Inlining the stack-copy IV accessor keeps the guest within its reservation; prior party-read bounds, decrypted-block permutations, overlay pixels, retry / countdown, one-shot input and protected-store tests all remain in the full passing run. No extra live RNG draw or map / player gate is introduced.

The official frozen PokeLDN v0.39.1 Windows executable read and installed the 38-file 0.6.0 package in isolated data with Python module fallback disabled. Its loader confirmed version / API, source and guest hashes, RAM bounds, both JSON resources and the bundled resource license; `--module pokeldn --plugins` reported the plugin loaded. The installed files passed actual-host form checks for all categories / methods / locations, three-language species + nature + IV previews with identical gifts, manual PID lookup, and six real offline gift exports including Pikachu, Super Rod Dratini and LeafGreen surf Slowpoke. Corrected runs exited 0 with empty stderr; evidence is in ignored `dist/packed-060-*.log`. An initial test configured POKELDN_PLUGINS as the parent directory instead of the plugin directory, so it did not load; correcting that isolated test configuration resolved it. These checks do not establish native GUI rendering, radio connection, game-ROM execution or physical timing.

The following records describe older versions. In particular, 0.5.0's lack of species selection is superseded here; its timing and live party display limitations still apply.

## 0.5.0 validation record

Date: 2026-10-25. **907 pytest cases passed in 104.96 s; Ruff, guest reproduction and offline frozen-host checks passed. Physical-console acceptance remains pending.**

The catalog now registers exactly two tools: live search / timed input and manual PID lookup. Both initial seed and PID are empty required text fields; the user fills them in. The real pinned-host form validation and command builder check every category and target, stale selections from other categories, the static Method 1 / 4 restriction, all wild locations under both games, automatic preset selection and explicit manual overrides. Blank optional Offset / original-target fields pass validation, while explicit zero survives command construction and the backend still rejects out-of-range values. Unknown wild reference delays use 256; the supplied columns are FireRed / LeafGreen, including Safari 256 / 257 and Power Plant unknown / 263.

The compiled resident's R page is decoded from actual rendered tile pixels across all four supported builds, all 24 encrypted-block orders, party-tail changes, checksum / Bad Egg / missing-record refusal, Hidden Power bit patterns, map / menu countdown and one-shot input. GetMonData is called with MON_DATA_IVS=66 on a stack copy, never the live party. The ROM accessor is substituted by a contract fixture that reproduces XOR / shuffle / checksum behavior; its actual game-ROM body and execution cycles have not been run. Store-address checks retain the no-RNG / party / save / ROM-write condition. L / L+R retain their initial-seed and PID views, and all shoulder-key views preserve hidden miss notices.

The hardware overlay is written after the original VBlank OAM copy. A synthetic original callback copies gMain.oamBuffer into hardware OAM before the compiled hook patches only slots 120..127. Checks verify the game buffer is untouched, earlier hardware slots survive, and menu suppression restores the game's OAM. The new state layout removes redundant generation / lock copies; its cursor is the selected generation seed while FOUND. Entry memory barriers delimit callback snapshots; the shim still masks IME while restoring / validating / emitting its one input. The existing RAM reservation is unchanged: **2192 / 2200 bytes**. GCC 15.2.1 reproduces guest.json with build_guest.py --check.

PID-only recovery enumerates consecutive PID-half states and validates each wild / Unown rejection prefix by forward generation. Range endpoints, ambiguous starts, no-match results, Method restrictions and Offset corrections are checked. The user's C76F / 4762A09B case yields advance 3354, with +3 against target 3351; existing extra Offset 3 gives suggestion 6. Reported IVs are explicitly predictions, and no PID result is labeled proof of input timing.

The final 0.5.0 package was read and installed in isolated data by the official frozen PokeLDN v0.39.1 Windows executable, with Python module fallback disabled. Its reader checked version / API, 31 archive files, source / guest SHA-256 and RAM bounds. The installed copy passed the actual catalog validation / command checks, the manual lookup's human-output path and five real gift exports (FireRed Mewtwo / Deoxys / Super Rod, LeafGreen Articuno / Sweet Scent). All three frozen processes exited 0 with empty stderr; evidence is in ignored dist/packed-050-final2-*.log. These are offline checks, not native GUI rendering, radio, game-ROM or hardware acceptance.

The following records describe older versions. Their flat lists, additional catalog tools, R-alone behavior and Offset defaults are superseded by 0.5.0.

## 0.4.0 validation record

Date: 2026-10-25. Status: **software checks completed; physical-console acceptance pending**.

## 0.4.0 scope and checks

The current workflow has no player/object/script-wait gate. The player chooses the final decision point. All targets receive one A except Ho-Oh, which receives UP in both heldKeys and newKeys. Normal ReadKeys replaces these on the next loop. The synthetic driver now models that replacement; compiled checks verify UP with no A bit on all four builds and no repeated input. This verifies memory/input handling, not movement in a game ROM.

Sweet Scent / fishing / Unown / starter menu profiles draw the overlay and can wrap callback2 after map activation. Compiled checks decode the actual OBJ tile pixels in the synthetic menu and verify restoration, one-shot input, replacement-callback expiry, and battle / missing-callback refusal. Map-only profiles retain menu suppression. The plugin does not recognize which menu option is selected or automate earlier actions.

The wild predictor uses slot + level + nature, then PID rejection until the selected nature matches. Tanoby uses its room-specific slot letter and reversed PID halves instead of the nature roll. The guest resumes candidates after eight rejected pairs per interrupt without imposing a total reroll cap. Independent test arithmetic follows the decompilation's draw order and checks positive / negative IV and nature cases, shiny trainer XOR, all seven Unown tables, H1/H2/H4, reverse recovery and the pre-slot range boundary. Long-chain checks cross the interrupt budget. Substitute callbacks do not execute encounter animations or an actual game ROM.

Every target's conditional Offset field is exercised through the pinned host's real form-to-argument builder: only one applies, it shows its preset, and switching targets preserves separate custom values. Large defaults and the 65533 extra-advance boundary are packed into a 16-bit total; catch-up uses a precomputed LCG jump instead of an offset-length loop. New delay-table values remain uncalibrated references. No claim is made that the supplied video-frame counts equal measured wireless RNG advances.

Checks on the current sources: **821 pytest cases passed in 96.45 s**, Ruff passed, and GCC 15.2.1 reproduced the committed guest with build_guest.py --check. The image is **2200 / 2200 bytes** at the unchanged EWRAM reservation; every transfer stays within the 1024-byte protocol cap. Decimal-renderer carry tests cover indices through 9999999. These checks do not certify any newly listed encounter's physical timing.

The 0.4.0 package was installed into isolated data with the official frozen PokeLDN v0.39.1 Windows app, without local Python module fallback. Its reader verified 31 members, guest / source SHA-256, the 2200-byte layout and the package API; the host reported the plugin loaded at API 1.11. The installed copy passed the actual catalog argument checks and exported real gifts for FireRed Mewtwo / Deoxys / Super Rod and LeafGreen Articuno / Sweet Scent. All three frozen processes exited 0 with empty stderr. Evidence is retained in ignored dist/packed-040-*.log and the host export folder. These are offline package / host checks, not radio, native GUI or physical-console execution.

Earlier observations below are version-specific history; the 0.4.0 ungated workflow and prefilled Offset fields supersede their older UI / readiness descriptions.

## Earlier validation history

## Wireless generation timing (0.3.9)

The user confirmed initial seed **C76F**, intended Method-1 index **3351 / PID 1D138B25**, and actual **3354 / PID 4762A09B**, while the countdown remained green. Public LCG prediction reproduces both PIDs at those zero-based pre-PID advance indices; this screenshot's tool uses that same index convention. This is a three-advance miss, not evidence of three video frames or a parity-check arithmetic failure.

The 0.3.7/0.3.8 test callback wrongly assumed that generation followed immediately after its configured remaining draws. The actual [RunScriptCommand](https://github.com/pret/pokefirered/blob/c75f352304d529f6ba92d4f74b9cf8b5c3810788/src/script.c) returns for the current pass after a successful native function, even though it sets bytecode mode. The birds' [script](https://github.com/pret/pokefirered/blob/c75f352304d529f6ba92d4f74b9cf8b5c3810788/data/maps/SeafoamIslands_B4F/scripts.inc) first yields at `lock`, completes its stationary freeze task after the script pass, yields again at native completion, then runs `faceplayer` / `setwildbattle`. On the wireless branch, [RfuMain1](https://github.com/pret/pokefirered/blob/c75f352304d529f6ba92d4f74b9cf8b5c3810788/src/link_rfu_2.c) draws once before callbacks on **every** pass.

From the guest's post-VBlank sample to the state before the first PID draw, the source-based normal path is:

| Encounter | Script passes | RFU draws | Intervening VBlank draws | Total offset |
| --- | --- | --- | --- | --- |
| Mewtwo, already at native button wait | wait completes; bytecode resumes | 2 | 1 | 3 |
| Birds, talk press | lock; native completion; bytecode resumes | 3 | 2 | 5 |

This assumes stationary objects, no lag and no unrelated draws. No B, positioning or object gates were added. The shim still requires exactly one RFU draw before callback1. Mewtwo's script and selected-object checks now identify its encounter independently of the changed offset.

Before changing production profiles, the new C76F positive regression failed on all four builds. An isolated run of the committed 0.3.8 compiled guest with the source-phase fixture displays green, schedules at index 3349, and forecasts the reported actual PID at 3354. The corrected profile schedules at 3346 and forecasts 3351 / PID 1D138B25 with the same IVs as the public predictor. The new profile and colour check therefore select the parity of **target - 5**, instead of target - 2. It can skip a formerly selected candidate when that earlier press is unreachable; the requested generation index is unchanged.

`tests/encounter_timing.py` models individual script yields, RFU draws and intervening VBlanks without importing production offsets. It replaces the immediate remaining-draw assumption in the synthetic callback. These are source-based forecasts alongside real compiled guest execution, **not actual game-ROM execution**. The reported physical miss supports this mechanism, but no device trace was collected and the 0.3.9 correction remains unconfirmed on hardware. Development evidence is in ignored `dist/c76f-038-repro.json` and the C76F regression tests.

## Configurable extra Offset (0.3.9)

The visible numeric field and `--offset` accept 0..253 additional RNG advances relative to the previous baseline (birds 2 / Mewtwo 1). Blank selects birds 3 / Mewtwo 2, giving the corrected default totals 5 / 3. Installation reports retain the extra, baseline and total values. The packed guest uses that total for the press deadline, countdown and parity while retaining the requested generation target. Across all four builds, C76F tests exercise explicit bird offsets 0, 3 and 4: the script fixture forecasts actual indices 3354, 3351 and 3350 respectively for the same intended index 3351. CLI preview tests cover defaults, explicit zero, the upper bound and invalid values. Frozen-host smoke checks also verify that the field is visible and that an explicit value reaches the installer plan.

## Live tail PID display (0.3.8)

Hold L+R on the map to show the full live party-tail PID in white and its position (1..6), with priority over L's initial-seed display. R alone leaves the normal display. The PID is the unencrypted first word of a 100-byte party record; the fixed party / count addresses are taken from the pinned host's rom_map.py. This reads the current party, not the copy saved to SaveBlock1, and does not decrypt or change the record. Count 0 or greater than 6 is rejected before indexing, with FFFFFFFF / 00000000 shown instead.

Compiled-code checks decode both rows from the actual OBJ pixels across all four supported builds and all six party sizes, including leading zeros and PID 00000000 / FFFFFFFF. Independent host address fixtures populate the live records. Tests cover live PID / count changes, transitions between L+R, L, R alone and released keys, and memory-read boundaries for empty / invalid counts with nonzero adjacent bytes. The store-address allowlist is exercised while viewing. Viewing preserves hidden D notices and still sends one A at the exact predicted generation seed on every build / encounter; R alone does not hide or pause a visible D notice. Menu overlay suppression remains in place. These checks use synthetic memory and do not establish physical-console display reception or timing.

## D11 callback-phase correction (0.3.7)

The user reports repeatable D11 at reachable deadlines with matching parity on 0.3.6. The shim compared the live callback seed to an unchanged post-VBlank sample. This omitted a normal phase: [AgbMain](https://github.com/pret/pokefirered/blob/master/src/main.c) calls ReadKeys, then HandleLinkConnection, then callback1 / callback2; the wireless branch calls [RfuMain1](https://github.com/pret/pokefirered/blob/master/src/link_rfu_2.c), which passes Random() to the RFU manager even when it is shutting down. Thus the measured wireless path advances once between sampling and the shim.

The old synthetic main loop omitted that draw too. Before changing runtime.c or rebuilding guest.json, the corrected phase model failed the positive regression for all four builds and four encounters. An isolated comparison of the previous committed image and the rebuilt image records D11 / no A for 0.3.6 and one A for 0.3.7. This reproduces a source-supported mechanism consistent with the hardware report; no console RNG trace was collected to establish the cause on the device directly.

The shim requires exactly step(post-VBlank seed), and still rejects zero, two or three draws before callback1. It does not accept arbitrary changes or press an old target late. The 0.3.7 claim that total offsets 1 / 2 already covered the wireless path was incorrect: its generation fixture consumed 0 / 1 immediate remaining draws and omitted native-script yields. That assumption is superseded by the 0.3.9 per-pass fixture and offsets 3 / 5 above. A path without the expected RFU draw is deliberately rejected, because this profile requires that wireless branch.

The previous parity colours, 60 visible map frames of miss notice, original-range retries, and terminal success / exhaustion / invalid-epoch behavior remain covered. Neither the corrected source model nor these tests establish hardware input reception or exact bird generation timing after controls are released.

## Hardware observations

On 0.3.1 the user's English FireRed console displayed the current seed and a `B0008156` countdown in the Articuno room, followed by no A and `D0000000`. The user had released B. The sustained-B gate contradicted the requested hands-free countdown workflow; 0.3.2 only explained the gate and did not fix that design problem.

Version 0.3.3 removed all bird button, player, object, position, facing, movement, elevation and script-state gates. While the map callback and RNG timing remain valid, the selected deadline schedules one A regardless of those states. The user is responsible for positioning. Mewtwo retains its script-button-wait profile. Basic callback / RNG validation and no-late-press behavior remain in both paths.

Before changing production code, the new released-controls regression failed against the old compiled image with reason 1. After rebuilding, neutral-input tests pass for all four builds and all three birds. Deliberately invalid positioning and object states no longer suppress the scheduled A. These tests use substitute ROM callbacks and do not establish a physical-console A or generated result.

The user then reported repeated B countdowns reverting to A near the deadline on 0.3.3. The only FOUND-to-SEARCH branch predicted parity reachability from a single two-advance interval and discarded the current candidate. The exact hardware RNG trace was not recorded. A synthetic trace reproduces the mechanism: index 19990 shows `B0000008`, 19991 shows `B0000007`, then 19993 shows `A0020017`. Later indices 19994, 19996 and 19998 would have reached the original Articuno press deadline, but the target was already gone.

Version 0.3.4 keeps initial candidate qualification in A; once B is displayed, the selected target cannot be reselected. The same synthetic trace now shows B counts 8, 7, 5, 4, 2 and sends one A at index 19998, preserving the predicted generation state. An actually skipped deadline latches `D0000009` rather than silently searching or pressing late. New regressions failed against the 0.3.3 compiled image before the source fix.

The user rejected 0.3.4's terminal miss behavior. Version 0.3.5 shows the failed attempt's D reason, then automatically resumes from a strictly later candidate in the original range when the map / main loop is available. Search catches up from the live RNG, preserving the actual initial seed and all filters. The selected B target is kept until its deadline; only actual failure starts a new attempt. No late press of the old target is injected. C after the first sent A, E exhaustion and F epoch invalidation remain terminal. A stale shim can no longer turn FIRED back into a retryable state.

The new miss-to-retry regression failed against the 0.3.4 image before rebuilding. Software coverage includes four consecutive misses before a later one-shot A, recovery after busy frames / menu / Mewtwo script / object / changed RNG / expired callbacks, exact range-end candidates, exhaustion, and rejection of reseeds / rewinds. Positive shiny and nature / IV retries independently locate candidates with the public predictor and verify the eventual generated seed. None of these are new physical-console observations.

On 0.3.5 the user reported countdowns returning to A with no readable failure explanation, including after Teachy TV. Read-only checks of the installed manifest and latest installation report confirm 0.3.5, Articuno, shiny-only, and range 3000..200000. The user then confirmed that the TV case had actually advanced past the target. This establishes an inadequate notice, not a TV reseed or a demonstrated fix to automatic-A timing.

Version 0.3.6 holds the red D reason for 60 visible map frames before retrying; time spent in TV / menus does not consume it. The live RNG keeps advancing throughout. The new TV-burst / return-to-map regression fails against the previous compiled image, which switches directly to a new countdown without displaying the missed attempt on the map. The rebuilt image retains future targets, shows the overrun after returning, and resumes within the original range / epoch. Other recoverable failure reasons are checked through the same notice and subsequent one-shot A. Parity colour changes are checked against the automatic-A deadline, including the encounter offset, while retaining the same target. New colour assertions fail before rebuilding that change.

## Previous installer correction (0.3.1)

The user's English FireRed (BPRE) session connected through COM8 and executed the installer, but returned **`0xBAD00004`**, with host exit code 1 and no activated resident hook. Production version 0.3.0 had interpreted `english_names.BRACKETED` in the wrong direction: its keys are French addresses, and the stored offset must be added for English. The corrected Thumb targets are `0x0800059D` for English and `0x08000585` for French.

The old synthetic ROM fixture used the production profile to place the getter, so it repeated the same wrong assumption. It now obtains its ROM placement independently from the pinned upstream table. Four new direction checks were run against 0.3.0 and failed, before fixing production addresses. Additional machine-code tests reproduce the old address refusal without enabling the hook. These are regression checks, not a substitute for retrying the corrected version on the console.

## Reference environment

- PokeLDN **v0.39.1**, commit `4780dcaeac52479e6212483009f64f348581d7cc`, public plugin API **1.11**.
- The official Windows release was extracted into an isolated temporary directory. Release archive SHA-256: `eb704a26c8382ab39883bd21d51047c71724fa824ef5185974ddf1fbd41d46f8`.
- Windows, Python 3.13.15, pytest 9.1.1, Unicorn 2.1.4, Ruff 0.17.2, GNU Arm Embedded GCC 15.2.1.
- The user's upstream checkout and currently installed plugin were not used as test output directories.

## Automated checks

**500 tests passed.** The test suite executes the **actual compiled ARM/Thumb loader and resident code** in Unicorn against synthetic GBA memory. It also compares public host predictions, checks record conversion, and exercises CLI entry points and failure handling.

Coverage includes:

- All four supported build profiles and all four encounters; natural Method 1 PID / six-IV / nature predictions, positive shiny matches, single A, and callback restoration.
- A normal pre-callback link draw reaches the shim and preserves the exact target generation seed for every build / encounter. Missing or additional pre-callback draws still cancel A; the unchanged-seed comparison in the prior image is reproduced as D11.
- Title reseeding and absolute advances, including a first-map index of 3500, large intervening consumption and all 32 distance bits. Nothing resets the origin at first map entry.
- Missing transfer chunks, corrupt image, wrong revision / game / getter instructions, existing hooks and acknowledgement errors. Partial transfer does not publish the VBlank hook.
- Menu, lag, passed target, changed initial seed, rewind, changed RNG and expired callbacks. Failed timing conditions do not inject a late A; Mewtwo's script wait is rechecked after ReadKeys.
- Initial two-advance parity qualification before displaying B and multi-batch searching. After B starts, transient one / two-advance changes retain the same target and still produce the exact predicted generation seed across every build / encounter. Truly skipped deadlines report D09, then search a future candidate without a late A.
- All builds / encounters recover after repeated misses, preserve the original seed, and can send one A at an inclusive range endpoint. Exhaustion never extends the range. Callback failures retry after recovery; stale shims after success do not rearm the run. Shiny and nature / IV conditions survive large skips and rebasing from the live RNG.
- Store-address allowlist: no guest stores to RNG, Pokemon, save blocks or ROM. Overlay seed / decimal digits and final eight OAM entries are checked.
- Every encrypted Gen III substructure order, checksums, Bad Egg refusal, party slot ambiguity, saved-party size and the public gift parser.
- Capture verification inherits installation conditions, checks absolute advances when a seed is supplied, and does not claim that record matching measures actual input timing.
- Preview never starts a host; failed / missing acknowledgements and nonzero host exit codes never create an installed-success report. Launcher state is restored on host exit.
- Failure statuses are retained even when the host exits nonzero, including a final status line without a newline; the installer explains the console refusal.
- All four builds and all three birds produce exactly one A at the selected deadline with no held buttons, never before it, and restore callback1. Scheduled and sent C states are distinct.
- Bird direction input, active scripts, absent objects, movement, changed position, wrong facing and incompatible elevations do not gate A. Each condition is tested before scheduling and after scheduling / ReadKeys, covering both former validation points.
- Distinct D reasons are displayed before retrying timing failures, scene changes and Mewtwo's script / interaction-object requirements. Retired bird refusal codes are no longer generated.
- A D reason stays red for 60 visible map frames with no input injection before retrying. TV-sized 312-call animation bursts plus the substitute VBlank's one call retain a future target and catch up exactly; an actual overrun waits until map return to display its reason. TV time and the held-L seed view cannot consume the notice. This models RNG consumption and scene transitions, not actual TV ROM execution.
- Yellow / green countdown colours compare current advances to the automatic-A deadline, rather than the PID-generation index. Temporary parity changes never discard a visible B target.

`python -m ruff check .` passes. The checked-in resident rebuild matches its source with GCC 15.2.1; resident size **1940 / 2200 bytes**, with each transfer payload at most **1024 bytes**.

Windows' Unicorn native exception handler can generate first-chance diagnostics under pytest's faulthandler. The suite disables only that diagnostic plugin; emulation exceptions, instruction limits, return addresses and all assertions remain active.

## Official frozen-app smoke checks

Executed the official **v0.39.1 `pokeldn.exe`**, with separate temporary app data and plugin paths:

1. Plugin registration and installer preview: exit **0**, empty stderr; actual `.pokegift` and installation-preview JSON generated.
2. `scripts/release_smoke.py`: exit **0**, empty stderr. Public RNG prediction / recovery works without a separately installed Python runtime. The public catalog launcher reads the generated gift through the built-in Mystery Gift script and exports it without starting a radio session.
3. Both FireRed variants (BPRE/BPRF) and both LeafGreen variants (BPGE/BPGF) survive the built-in export, with the final `0x524E4703` expectation preserved.
4. Packed with the pinned host's official packer, checked by its package reader, and installed into isolated temporary app data. The frozen app reports `plugin API 1.11` and `frlg-rng-assist ... loaded` through `--module pokeldn --plugins`. Repeating the host-export smoke check from that extracted package passes, with the imported core path asserted to be the installed folder. The archive contains the guest source and build script, and excludes development output, tests, keys, saves and ROMs.

The smoke test uses paths with spaces and the app's existing child Python process; it does not launch another Python executable or import private host implementations in production code.

## What these checks do not prove

No retail / Switch ROM was run in the synthetic-memory tests. The model substitutes the original VBlank and callback code, includes the source-backed wireless link draw before callback1, and forecasts generation through native-script yields with RFU and VBlank on subsequent passes. Therefore this suite cannot establish real script timing, sprite availability, interrupt cycle budgets or console stability across the title transition.

No physical console / board session has been completed for this version. The new wireless offsets are three advances for Mewtwo and five for birds. The source-phase model explains the reported three-advance Articuno miss, but the corrected automatic-A / generation timing remains **unverified on hardware**. Follow `HARDWARE_TEST_ZH.md`; users who have already confirmed automatic battle entry can repeat their original shiny search with IVs unrestricted and compare the actual PID.

The package is a local test artifact. No upstream PR or release is part of this test handoff.
