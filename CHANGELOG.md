# Changes

## 0.3.1 — 2026-10-25

- Fix the initial-seed getter addresses. Upstream `english_names.py` is keyed by **French** ROM addresses; French `0x08000584` plus `0x18` gives English `0x0800059C` (add the Thumb bit when calling). Version 0.3.0 interpreted that mapping backwards, so the first English FireRed hardware attempt returned `0xBAD00004` and did not enable the hook.
- Build the simulated ROM getter placement from the pinned upstream table, independently of production profiles. Reproduce the old address failure and verify every corrected build.
- Preserve the console's refusal statuses when the built-in host exits nonzero, and explain the refusal in the plugin output instead of showing only exit code 1.

The user's 0.3.0 log establishes that radio communication and the refusal path work on English FireRed. It does **not** establish countdown or automatic-A behavior. Version 0.3.1 still needs the installation and field test repeated.
