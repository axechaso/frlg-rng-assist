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

Source references:

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
