# Notices

FRLG RNG Assist is a third-party plugin by axechaso, distributed under AGPL-3.0.
It is not an official PokeLDN plugin and is not supported by PokeLDN's author.

The earlier FRLG RNG Assist offline model is reused here under the same license.
The Gen III record conversion in `frlg_rng_assist_core/pk3.py` is adapted from
[PokeLDN](https://github.com/Decryptu/pokeldn)'s `pokeldn/frlg/save/mon.py` and
`readout.py` (AGPL-3.0), copyright their respective contributors. The tests' GBA
memory setup follows `tests/test_shiny.py` from that project, under the same license.

The standalone GBA implementation in `guest/` uses the encounter offsets and
memory layout documented by PokeLDN's `shiny.inc`, `follower.s`, `builds.py`,
`english_names.py` and `docs/frlg_rom.md`, with attribution to their respective
contributors. The font data is adapted from `asm/resident/overlay.inc`. The loader
follows the ARM-to-THUMB entry convention of `asm/install-resident.s`.

This plugin uses documented API 1.11 and the public catalog launcher; it does not
bundle the PokeLDN host or any ROM, save, prod.keys, or private signing key.

Source references:

- [PokeLDN plugin API](https://github.com/Decryptu/pokeldn/blob/v0.39.1/docs/plugins.md)
- [Native shiny-press and measured offsets](https://github.com/Decryptu/pokeldn/blob/v0.39.1/docs/frlg_rom.md)
- [RNG and title-screen reseeding](https://github.com/Decryptu/pokeldn/blob/v0.39.1/docs/frlg_rng.md)
- [Gen III Pokemon structures](https://github.com/pret/pokefirered/blob/master/include/pokemon.h)
