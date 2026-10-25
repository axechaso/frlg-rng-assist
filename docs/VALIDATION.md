# 0.3.8 validation record

Date: 2026-10-25. Status: **software checks completed; physical-console acceptance pending**.

## Live tail PID display (0.3.8)

Hold L+R on the map to show the full live party-tail PID in white and its position (1..6), with priority over L's initial-seed display. R alone leaves the normal display. The PID is the unencrypted first word of a 100-byte party record; the fixed party / count addresses are taken from the pinned host's rom_map.py. This reads the current party, not the copy saved to SaveBlock1, and does not decrypt or change the record. Count 0 or greater than 6 is rejected before indexing, with FFFFFFFF / 00000000 shown instead.

Compiled-code checks decode both rows from the actual OBJ pixels across all four supported builds and all six party sizes, including leading zeros and PID 00000000 / FFFFFFFF. Independent host address fixtures populate the live records. Tests cover live PID / count changes, transitions between L+R, L, R alone and released keys, and memory-read boundaries for empty / invalid counts with nonzero adjacent bytes. The store-address allowlist is exercised while viewing. Viewing preserves hidden D notices and still sends one A at the exact predicted generation seed on every build / encounter; R alone does not hide or pause a visible D notice. Menu overlay suppression remains in place. These checks use synthetic memory and do not establish physical-console display reception or timing.

## D11 callback-phase correction (0.3.7)

The user reports repeatable D11 at reachable deadlines with matching parity on 0.3.6. The shim compared the live callback seed to an unchanged post-VBlank sample. This omitted a normal phase: [AgbMain](https://github.com/pret/pokefirered/blob/master/src/main.c) calls ReadKeys, then HandleLinkConnection, then callback1 / callback2; the wireless branch calls [RfuMain1](https://github.com/pret/pokefirered/blob/master/src/link_rfu_2.c), which passes Random() to the RFU manager even when it is shutting down. Thus the measured wireless path advances once between sampling and the shim.

The old synthetic main loop omitted that draw too. Before changing runtime.c or rebuilding guest.json, the corrected phase model failed the positive regression for all four builds and four encounters. An isolated comparison of the previous committed image and the rebuilt image records D11 / no A for 0.3.6 and one A for 0.3.7. This reproduces a source-supported mechanism consistent with the hardware report; no console RNG trace was collected to establish the cause on the device directly.

The shim now requires exactly step(post-VBlank seed). It does not accept arbitrary changes or press the old target late. The measured total offsets stay Mewtwo 1 / birds 2: after the link draw, the synthetic generation callback consumes 0 / 1 remaining draws respectively. Those callback draws are independently specified by encounter, rather than copied from the production offset. Tests verify the exact generation state at absolute advance 20000, normal shiny / nature / IV results, one-shot A and callback restoration. Zero, two or three draws before the callback still produce D11 without A for every build / encounter. This profile covers the measured wireless path; a path without its expected draw is deliberately rejected, as its generation timing has not been calibrated here.

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

**469 tests passed.** The test suite executes the **actual compiled ARM/Thumb loader and resident code** in Unicorn against synthetic GBA memory. It also compares public host predictions, checks record conversion, and exercises CLI entry points and failure handling.

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

`python -m ruff check .` passes. The checked-in resident rebuild matches its source with GCC 15.2.1; resident size **1944 / 2200 bytes**, with each transfer payload at most **1024 bytes**.

Windows' Unicorn native exception handler can generate first-chance diagnostics under pytest's faulthandler. The suite disables only that diagnostic plugin; emulation exceptions, instruction limits, return addresses and all assertions remain active.

## Official frozen-app smoke checks

Executed the official **v0.39.1 `pokeldn.exe`**, with separate temporary app data and plugin paths:

1. Plugin registration and installer preview: exit **0**, empty stderr; actual `.pokegift` and installation-preview JSON generated.
2. `scripts/release_smoke.py`: exit **0**, empty stderr. Public RNG prediction / recovery works without a separately installed Python runtime. The public catalog launcher reads the generated gift through the built-in Mystery Gift script and exports it without starting a radio session.
3. Both FireRed variants (BPRE/BPRF) and both LeafGreen variants (BPGE/BPGF) survive the built-in export, with the final `0x524E4703` expectation preserved.
4. Packed with the pinned host's official packer, checked by its package reader, and installed into isolated temporary app data. The frozen app reports `plugin API 1.11` and `frlg-rng-assist ... loaded` through `--module pokeldn --plugins`. Repeating the host-export smoke check from that extracted package passes, with the imported core path asserted to be the installed folder. The archive contains the guest source and build script, and excludes development output, tests, keys, saves and ROMs.

The smoke test uses paths with spaces and the app's existing child Python process; it does not launch another Python executable or import private host implementations in production code.

## What these checks do not prove

No retail / Switch ROM was run in the synthetic-memory tests. The model substitutes the original VBlank and callback code, includes the source-backed wireless link draw before callback1, and models the remaining encounter draws separately. Therefore this suite cannot establish real script timing, sprite availability, interrupt cycle budgets or console stability across the title transition.

No physical console / board session has been completed for this version. The bird offset remains two advances, originally measured upstream with B held; the released-controls path and actual generated result remain **unverified on hardware**. Follow `HARDWARE_TEST_ZH.md`: first test unrestricted normal encounters, then shiny encounters. IV restrictions are not a first-round acceptance requirement.

The package is a local test artifact. No upstream PR or release is part of this test handoff.
