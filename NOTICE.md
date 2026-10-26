# Notices

FRLG RNG Assist is a third-party plugin by axechaso, distributed under AGPL-3.0.
It is not an official PokeLDN plugin and is not supported by PokeLDN's author.

The earlier FRLG RNG Assist offline model is reused here under the same license.
The Gen III record conversion in `frlg_rng_assist_core/pk3.py` is adapted from
[PokeLDN](https://github.com/Decryptu/pokeldn)'s `pokeldn/frlg/save/mon.py` and
`readout.py` (AGPL-3.0), copyright their respective contributors. The tests' GBA
memory setup follows `tests/test_shiny.py` from that project, under the same license.

The standalone GBA implementation in `guest/` originally used the encounter offsets and
memory layout documented by PokeLDN's `shiny.inc`, `follower.s`, `builds.py`,
`english_names.py` and `docs/frlg_rom.md`, with attribution to their respective
contributors. The font data is adapted from `asm/resident/overlay.inc`. The loader
follows the ARM-to-THUMB entry convention of `asm/install-resident.s`.

The wireless timing profile in 0.3.9 also accounts for native-script yields and
the RFU draw on each main-loop pass, using pret/pokefirered's `src/script.c`,
`src/scrcmd.c`, `src/event_object_lock.c`, `src/link_rfu_2.c`, `src/main.c` and
the legendary encounter scripts. `tests/encounter_timing.py` is a source-based
phase model, not bundled ROM code or a full game emulator.

Version 0.4.0's wild encounter model and Tanoby letter tables follow the random-call
order documented by pret/pokefirered's src/wild_encounter.c and src/pokemon.c.
The supplied encounter-delay reference values are editable presets, not measured
timing certifications. Ho-Oh's direction input follows NavelRock_Summit/map.json,
its coordinate-event script, and field_control_avatar.c's held-key handling.

This plugin uses documented API 1.11 and the public catalog launcher; it does not
bundle the PokeLDN host or any ROM, save, prod.keys, or private signing key.
Display-language selection additionally uses the non-private `i18n.locale()`
helper verified in v0.39.1; that helper is not in the guaranteed API table, so
its absence falls back to English without blocking either RNG tool.

Version 0.6.0's `data/wild_tables.json` is a national-dex-indexed conversion of
pret/pokefirered's `src/data/wild_encounters.json` at
`c75f352304d529f6ba92d4f74b9cf8b5c3810788`, with plugin-authored location labels.
`data/names.json` contains the first 386 species names and 25 nature names in
English, Japanese and Chinese from Admiral-Fish/PokeFinder's
`Source/Core/Resources/i18n` at `fddaee74e6e3a2cfebc59c7624ffca2f6d1c6b4b`,
copyright its contributors, under GPL-3.0. Its license is included in
`licenses/PokeFinder-GPL-3.0.txt`. The generator is `scripts/import_wild_data.py`;
the source commits are also embedded in the JSON snapshots. No Ten Lines
program code or encounter table is copied; the PokeFinder resource snapshot is
separately attributed here.

Source references:

- Version 0.7.0's fixed-threshold capture-band predicate follows the user-supplied
  `FRLGSwitchSeedFarmer/frlg_capture_engine_v24.py` (`check_capture_band`) and
  `frlg_easycon_capture_calibrator_v27g.py` (`verify_band`), supplied under GPL-3.0.
  Provenance hashes, the retained legacy vector and the independent native-input
  timing boundary are recorded in `docs/CAPTURE_MODEL.md`. The plugin keeps the
  combined work under AGPL-3.0-or-later; the supplied source's GPL text is included
  as `licenses/FRLGSwitchSeedFarmer-GPL-3.0.txt`. No SysBot client, credentials,
  logs, calibration records or complete source tool is bundled.
- [Capture's integer threshold and four Random checks](https://github.com/pret/pokefirered/blob/c75f352304d529f6ba92d4f74b9cf8b5c3810788/src/battle_script_commands.c).

- [Ten Lines static target categories](https://github.com/lincoln-lm/ten-lines/blob/main/src/components/StaticEncounterSelector.tsx)
  and [wild category / location selector](https://github.com/lincoln-lm/ten-lines/blob/main/src/components/WildEncounterSelector.tsx)
  inform the selection layout. No Ten Lines program code or encounter tables are bundled.
- Wild delay reference values and their FireRed / LeafGreen column meaning were supplied by the user;
  unknown values default to 256 and are not hardware measurements by this project.
- [GetMonData and encrypted-record checksum](https://github.com/pret/pokefirered/blob/c75f352304d529f6ba92d4f74b9cf8b5c3810788/src/pokemon.c)
  and [MON_DATA_IVS](https://github.com/pret/pokefirered/blob/c75f352304d529f6ba92d4f74b9cf8b5c3810788/include/constants/pokemon.h).

- [PokeLDN plugin API](https://github.com/Decryptu/pokeldn/blob/v0.39.1/docs/plugins.md)
- [Native shiny-press and measured offsets](https://github.com/Decryptu/pokeldn/blob/v0.39.1/docs/frlg_rom.md)
- [RNG and title-screen reseeding](https://github.com/Decryptu/pokeldn/blob/v0.39.1/docs/frlg_rng.md)
- [Gen III Pokemon structures](https://github.com/pret/pokefirered/blob/master/include/pokemon.h)
