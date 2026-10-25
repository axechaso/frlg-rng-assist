# 0.3.0 validation record

Date: 2026-10-25. Status: **software checks completed; physical-console acceptance pending**.

## Reference environment

- PokeLDN **v0.39.1**, commit `4780dcaeac52479e6212483009f64f348581d7cc`, public plugin API **1.11**.
- The official Windows release was extracted into an isolated temporary directory. Release archive SHA-256: `eb704a26c8382ab39883bd21d51047c71724fa824ef5185974ddf1fbd41d46f8`.
- Windows, Python 3.13.15, pytest 9.1.1, Unicorn 2.1.4, Ruff 0.17.2, GNU Arm Embedded GCC 15.2.1.
- The user's upstream checkout and currently installed plugin were not used as test output directories.

## Automated checks

**142 tests passed.** The test suite executes the **actual compiled ARM/Thumb loader and resident code** in Unicorn against synthetic GBA memory. It also compares public host predictions, checks record conversion, and exercises CLI entry points and failure handling.

Coverage includes:

- All four supported build profiles and all four encounters; natural Method 1 PID / six-IV / nature predictions, positive shiny matches, single A, and callback restoration.
- Title reseeding and absolute advances, including a first-map index of 3500, large intervening consumption and all 32 distance bits. Nothing resets the origin at first map entry.
- Missing transfer chunks, corrupt image, wrong revision / game / getter instructions, existing hooks and acknowledgement errors. Partial transfer does not publish the VBlank hook.
- Menu, lag, passed target, changed initial seed, rewind, changed position and released B. Failed conditions do not inject a late A.
- Two-advance stationary parity, multi-batch searching and future-candidate reselection.
- Store-address allowlist: no guest stores to RNG, Pokemon, save blocks or ROM. Overlay seed / decimal digits and final eight OAM entries are checked.
- Every encrypted Gen III substructure order, checksums, Bad Egg refusal, party slot ambiguity, saved-party size and the public gift parser.
- Capture verification inherits installation conditions, checks absolute advances when a seed is supplied, and does not claim that record matching measures actual input timing.
- Preview never starts a host; failed / missing acknowledgements and nonzero host exit codes never create an installed-success report. Launcher state is restored on host exit.

`python -m ruff check .` passes. The checked-in resident rebuild matches its source with GCC 15.2.1; resident size **1824 / 2200 bytes**, with each transfer payload at most **1024 bytes**.

Windows' Unicorn native exception handler can generate first-chance diagnostics under pytest's faulthandler. The suite disables only that diagnostic plugin; emulation exceptions, instruction limits, return addresses and all assertions remain active.

## Official frozen-app smoke checks

Executed the official **v0.39.1 `pokeldn.exe`**, with separate temporary app data and plugin paths:

1. Plugin registration and installer preview: exit **0**, empty stderr; actual `.pokegift` and installation-preview JSON generated.
2. `scripts/release_smoke.py`: exit **0**, empty stderr. Public RNG prediction / recovery works without a separately installed Python runtime. The public catalog launcher reads the generated gift through the built-in Mystery Gift script and exports it without starting a radio session.
3. Both FireRed variants (BPRE/BPRF) and both LeafGreen variants (BPGE/BPGF) survive the built-in export, with the final `0x524E4703` expectation preserved.
4. Packed with the pinned host's official packer, checked by its package reader, and installed into isolated temporary app data. The frozen app reports `plugin API 1.11` and `frlg-rng-assist ... loaded` through `--module pokeldn --plugins`. Repeating the host-export smoke check from that extracted package passes, with the imported core path asserted to be the installed folder. The archive contains the guest source and build script, and excludes development output, tests, keys, saves and ROMs.

The smoke test uses paths with spaces and the app's existing child Python process; it does not launch another Python executable or import private host implementations in production code.

## What these checks do not prove

No retail / Switch ROM was run in the synthetic-memory tests. The model substitutes the original VBlank and callback code and advances the RNG according to the measured upstream offsets. Therefore this suite cannot establish real script timing, sprite availability, interrupt cycle budgets or console stability across the title transition.

No physical console / board session has been completed for this version. The integrated Mewtwo and bird timing, overlay visibility and actual generated result remain **unverified on hardware**. Follow `HARDWARE_TEST_ZH.md`: first test unrestricted normal encounters, then shiny encounters. IV restrictions are not a first-round acceptance requirement.

The package is a local test artifact. No upstream PR or release is part of this test handoff.
