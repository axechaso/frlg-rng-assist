# Changes

## 0.3.5 — 2026-10-25

- Automatically search a later candidate after an actual miss, busy frame, scene / Mewtwo wait mismatch, changed pending RNG or expired callback. Briefly show the D reason, resume when the normal map / main loop is available, and preserve the original seed, configured range and filters. Do not discard B targets early or press an old deadline late.
- End the run after one injected A, range exhaustion or epoch invalidation. Ignore stale shim invocations after success so they cannot rearm a second A.
- Add compiled-code regressions for four consecutive misses followed by success, every supported build / encounter, recoverable callback failures, range-end success, exhaustion, reseed / rewind refusal and positive shiny / nature / IV retries. The new retry check fails against 0.3.4 before rebuilding. Hardware acceptance remains pending.

## 0.3.4 — 2026-10-25

- Fix the B countdown reverting to A because a single two-advance interval caused premature parity reselection. A future interval can restore reachability; the old code had already discarded that target. Initial candidate qualification now happens while A is displayed; once B starts, the target stays fixed.
- Keep exact-deadline, one-shot input and RNG validation. A deadline that is actually skipped reports latched `D0000009`, without a silent search restart or late A.
- Add compiled-code regressions for transient one / two-advance intervals and actual skipped deadlines across all four builds and encounters. Reproduce the old premature reselection before rebuilding; software checks pass, hardware confirmation remains pending.

## 0.3.3 — 2026-10-25

- Remove the bird profile's held-B, direction, position, facing, movement, elevation, object and script checks. The requested workflow is to walk into place, release all buttons and receive one A at the RNG deadline. Earlier versions imposed an unnecessary arming gate; positioning is now the user's responsibility.
- Keep basic map-callback / RNG timing checks, one-shot injection and no late retries. Mewtwo retains its separate script-button-wait profile. Green on birds now describes the timer, not verified positioning. Retire bird-specific D codes without renumbering timing reasons.
- Run released-controls regressions against the old image before rebuilding, then cover all four builds / three birds and state changes before both scheduling and sending. Software checks do not prove hardware timing; the two-advance bird offset still needs verification with controls released.
- Update tool steps and test instructions. Explain OPTIONS → BUTTON MODE → L/R for the L seed display, no separate ZL handling, and injection loss on soft reset or game closure.

## 0.3.2 — 2026-10-25

- Explain the user's 0.3.1 bird test: the seed and countdown appeared, but B was not held continuously. The bird profile requires B to arm A; the old countdown did not indicate that it was unarmed and ended in the generic `D0000000`.
- Colour the found-candidate overlay amber while position / button conditions are unmet and green when they are met. Make the sustained-B requirement explicit in the tool steps, switch help and installation output. The countdown still runs while unarmed; no late A is injected.
- Latch a decimal reason code in D, distinguishing missing B, direction input, script / scene / object / movement / facing / elevation refusal, a passed target, a busy loop, changed RNG and an expired callback. Distinguish a scheduled `C0000001` from an injected `C0000000`.
- Match the game's zero-elevation wildcard rule when comparing player and bird object elevations; continue refusing incompatible nonzero elevations.
- Add compiled-guest regressions for missing B, arming before the deadline, one-shot A and refusal diagnostics. No console acceptance is claimed for this update.

## 0.3.1 — 2026-10-25

- Fix the initial-seed getter addresses. Upstream `english_names.py` is keyed by **French** ROM addresses; French `0x08000584` plus `0x18` gives English `0x0800059C` (add the Thumb bit when calling). Version 0.3.0 interpreted that mapping backwards, so the first English FireRed hardware attempt returned `0xBAD00004` and did not enable the hook.
- Build the simulated ROM getter placement from the pinned upstream table, independently of production profiles. Reproduce the old address failure and verify every corrected build.
- Preserve the console's refusal statuses when the built-in host exits nonzero, and explain the refusal in the plugin output instead of showing only exit code 1.

The user's 0.3.0 log establishes that radio communication and the refusal path work on English FireRed. It does **not** establish countdown or automatic-A behavior. Version 0.3.1 still needs the installation and field test repeated.
