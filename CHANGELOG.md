# Changes

## 0.6.0 — 2026-10-25

- Add wild species selection using 132 versioned FRLG encounter tables, exact floors / zones, surf / Rock Smash and individual rod slots. Encode the selected species' 100 percentile-roll buckets for filtering in the compiled resident before PID rejection. Invalid game / location / type combinations fail before gift creation; Any preserves previous behavior. Unown keeps its separate letter model.
- Combine species with existing shiny, nature and all six IV minimum / maximum conditions. Manual PID lookup uses the same table and reports predicted species. No automatic map detection or roamer-override simulation is added.
- Localize both tools' forms, names, steps, choices and normal output in Chinese, Japanese and English using the host display locale. Preserve stable command values and pass the display locale to subprocesses independently of trainer language. Unsupported locales use English; reload the plugin by restarting after a language change.
- Include attributed reproducible encounter / name snapshots. Keep the existing 2200-byte RAM reservation; the guest now uses all 2200 bytes. Hardware timing remains pending physical validation.

## 0.5.0 — 2026-10-25

- Replace the flat target list with Ten Lines-style categories and separate target / wild method / location selection. Stationary and gift configurations expose and accept only Method 1 / 4; wild configurations retain H1 / H2 / H4.
- Apply reference wild Offsets by FireRed / LeafGreen column. Add all supplied areas, including Viridian Forest 250 / unknown, Power Plant unknown / 263, Safari Zone 256 / 257 and Mansion 257 / 257. Unknown wild entries use 256. Preset values appear alongside the target / location; a blank manual Offset uses that preset, and explicit zero overrides it.
- Hold R for live tail IVs and Hidden Power type / power. Keep L for initial seed / advances and L+R for PID. Call the game's checksum-aware accessor on a stack copy, preserving the live party. Display two decimal pairs per stat; keep countdown and one-shot input running, and preserve hidden miss notices.
- Keep only two registered tools: live search / timed input, and manual initial-seed + PID lookup of actual hit advances. Recover wild rejection prefixes as well as stationary PID states, list ambiguity, and optionally calculate Offset correction against a planned advance. Predicted IVs are labeled as predictions.
- Patch the final eight hardware OAM slots after the original VBlank copy, preserving the game's OAM buffer. Compact the resident to 2192 / 2200 bytes without expanding the verified RAM reservation. Software checks do not replace physical-console acceptance.

## 0.4.0 — 2026-10-25

- Expand presets to stationary encounters, gifts, fossils, Game Corner, roamer initialization, Sweet Scent, all three fishing rods, Rock Smash and Tanoby Unown. Keep the player's workflow: reach the decision point, search and count down, then inject one input. Ho-Oh uses UP, including heldKeys for movement; other targets use A. No position, object, script-wait or held-B gate remains.
- Prefill and remember each target's extra Offset separately in the actual host form. Retain Mewtwo 2 / birds 3; populate supplied references for other encounters, and mark unmeasured defaults as reference / uncalibrated. Accept 0..65533 extra advances, including Deoxys 501 / Lugia 277 / Ho-Oh 379. A constant-time LCG jump replaces the offset-length catch-up loop.
- Add FRLG Method-H nature/PID rejection, H1/H2/H4 IV variants, and Tanoby's slot-specific letter rejection with reversed PID halves. Resume long rejection chains across interrupts instead of truncating candidates. Offline search and captured-result recovery use the same pre-slot boundary; generic wild capture defaults to the party tail.
- Enable the overlay and one-shot callback2 input in menus for Sweet Scent / fishing / starter profiles, after initial map activation. Restore the original callback and retain expiry / RNG validation. Map-only encounters still hide their overlay in menus. Do not automate fishing rounds or menu navigation.
- Lock a candidate as soon as it is displayed as B; parity changes affect colour and do not silently replace it. Keep visible miss notices, original-range retries and terminal one-shot behavior. The guest fits the existing 2200-byte reservation. Software and frozen-host checks do not certify any new encounter's physical timing.

## 0.3.9 — 2026-10-25

- Add a visible extra Offset field and CLI option, in RNG advances. Blank uses birds 3 / Mewtwo 2; 0 restores the old press timing, and 0..253 is accepted. Add it to the existing baseline of birds 2 / Mewtwo 1. Keep generation targets unchanged; pack the resulting deadline into the guest, use it for countdown / parity, and record all three values in installation reports. Test explicit offsets against the compiled guest and reject invalid values before transfer.
- Correct the wireless script-generation timing. A successful native-script wait still returns for that pass: Mewtwo resumes bytecode on the next pass, and birds yield first at lock and then at lock-wait completion. Counting RFU on every pass and VBlank between passes gives post-VBlank offsets 3 / 5, replacing 1 / 2. Keep Mewtwo's wait / object check keyed to its encounter, independent of the numerical offset.
- Reproduce the user's C76F case against the compiled 0.3.8 guest: a green target at 3351 / PID 1D138B25 presses at 3349 but the script-phase fixture produces 3354 / PID 4762A09B. The corrected profile presses at 3346 and the model produces the target. This changes the eligible candidate parity and the countdown to the press, not the requested generation index.
- Replace the immediate remaining-draw assumption in the test callback with an explicit source-based per-pass script fixture. Cover RFU and VBlank across lock / native completion for all encounters, the reported PID pair and the corrected compiled guest on all builds. Update earlier hardcoded deadlines. The fixture forecasts script completion; it does not execute a game ROM. Corrected hardware timing remains pending.

## 0.3.8 — 2026-10-25

- Hold L+R on the map to view the last current party member's full eight-digit hexadecimal PID in white, with its party position (1..6) below. Release R to return to L's existing initial-seed view, or release both for the normal overlay. R alone does not switch views. Continue RNG tracking, search and one-shot A while viewing; retain hidden D notices until the ordinary display is visible again.
- Read the live party's unencrypted personality word, not a saved-party copy. Read the party count as a byte, reject counts outside 1..6 before indexing, and show FFFFFFFF / 00000000 when no valid tail slot exists. Zero and FFFFFFFF remain valid PIDs when the displayed slot is 1..6. Viewing writes no party / save / RNG data.
- Cover every supported build and party size, visible PID digits including leading zeros, live changes, invalid-count read boundaries, L / L+R / R switching, hidden notices, menus and exact one-shot A during PID viewing. Hardware display and timing acceptance remain pending.

## 0.3.7 — 2026-10-25

The claim below that the total offsets already covered this draw was incorrect; 0.3.9 supersedes that timing assumption and the corresponding synthetic generation fixture.

- Fix repeated D11 cancellation at an otherwise valid deadline. On the measured wireless path, `HandleLinkConnection` calls `RfuMain1`, which draws `Random()` before callback1. The shim now requires the exact successor of the post-VBlank seed, rather than the unchanged seed. The existing overall Mewtwo / bird offsets already include that draw and remain 1 / 2 advances. Missing or additional draws still cancel the A.
- Correct the synthetic main loop to include the link draw. Model remaining generation draws separately from the configured offset, so accepting A cannot silently move the predicted PID seed by one. Reproduce all 16 build / encounter failures against 0.3.6 before rebuilding, then cover exact generation seeds, one-shot input, missing / extra draws, and existing retry / colour / notice behavior.
- Keep the hardware status explicit: software checks and frozen-host loading pass; actual released-controls encounters and resulting PID / IVs still require physical-console confirmation. Update the package and test instructions to 0.3.7.

## 0.3.6 — 2026-10-25

- Keep a failed attempt's D reason in red for 60 visible map frames (about one second) before resuming search. Television / menu time and the held-L seed view do not consume the notice, and no A is sent during it. Continue tracking the actual RNG throughout, then catch up within the original range and filters.
- Colour a locked countdown amber when the current index and the automatic-A deadline have different parity, green when they match and the callback is ready. Include the encounter's offset in that comparison; retain the target through colour changes rather than predicting future strides from a single sample.
- Reproduce 0.3.5's immediately disappearing TV-overrun notice in compiled-code tests. Cover TV-sized RNG bursts without losing future targets, notices after returning to the map, all timing / callback reasons, and unchanged one-shot input / range / epoch limits. Hardware feedback and automatic-A timing still need console confirmation.

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
