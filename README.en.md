# FRLG RNG Assist 0.7.3

[简体中文](README.md) | [日本語](README.ja.md) | [English](README.en.md)

An independent, third-party PokeLDN plugin. Set an RNG advance range and filters, then watch the seed and countdown on the console. The plugin sends one input at the selected time. Move to the final decision point yourself: **Up for Ho-Oh, A for every other target**. Holding B is not required.

This is a hardware-test build. Software tests and offline host checks do not replace timing verification on a console. See the [validation record](docs/VALIDATION.md) and [hardware test steps (Chinese)](docs/HARDWARE_TEST_ZH.md).

## Installation and interface

Use PokeLDN v0.39.1 / API 1.11. Open Plugins → Add a plugin and select **frlg-rng-assist-0.7.3.pokeplugin**. An existing installation can be updated from its plugin card. Supported game builds are Switch English / French rev 0A: BPRE, BPGE, BPRF and BPGF. Wireless firmware 1.8.0 remains compatible. The package includes compiled code; users do not need Python or an ARM compiler.

Tool names, descriptions, categories, locations, species, natures and output support **Chinese / Japanese / English**, following PokeLDN's App language. Restart PokeLDN after changing its language to reload the plugin. Other interface languages fall back to English. Chinese and Japanese require the corresponding PokeLDN language packs. These translations affect the interface; supported game builds remain the English / French builds listed above. The installation card uses a shared trilingual description.

There are two tools under Games → FireRed & LeafGreen:

1. **RNG: search and timed input**: inject the search settings, find a target, show a countdown and send one input.
2. **RNG: find actual hit from PID**: manually enter the run's initial seed and actual PID to find the encounter advance. No console connection or IV entry is required.

Targets are grouped into starters, fossils, gifts / purchases, Game Corner, ordinary stationary encounters, legendary stationary encounters, event encounters, roamer initialization, wild encounters, Unown and other stationary encounters. Stationary / gift targets offer **Method 1 / 4**; wild targets offer **H1 / H2 / H4**. For wild encounters, also choose Sweet Scent, a fishing rod or Rock Smash and a location. Unown has a separate room selection.

## One attempt

1. Save near the target. Set OPTIONS → BUTTON MODE to **L/R**, then restart the game to clear other boosts.
2. On the PC, select the game, category, target or wild location, and search range. For the first test, allow non-shiny results and leave nature / IV filters unrestricted. Target and location choices show their preset Offset; leave the manual Offset blank to use it.
3. Click Start on the PC. On the console, select Mystery Gift → Wonder Cards → Friend → POKELDN and wait for installation acknowledgement **0x524E4703**.
4. Exit normally to the title screen, then continue the game. Advance 0 is the actual initial seed established at the title screen; the count is usually already above 0 when the overworld appears.
5. Move to the final decision point yourself, release the controls and wait. For the Kanto birds, stand in front of the target. For Mewtwo, wait at the final button prompt in its dialogue. For Sweet Scent, stop on that option in the party menu. For fishing, complete the earlier prompts yourself. For Ho-Oh, stand one tile south of its trigger tile and face up.
6. Check whether the input actually triggered the encounter. After catching the Pokémon, hold R to read its actual IVs or L+R to read the last party member's PID, then use the second tool for a manual lookup.

The plugin does not check your position, facing direction, interaction target or script wait. It does not walk, navigate menus or repeat fishing attempts. Generation sends one input. With capture search preloaded, you can enable a throw later in the same battle. A soft reset or closing the game clears the injection; install it again for the next run. A new save cannot normally access Mystery Gift before choosing a starter. This plugin does not unlock it early or preserve an injection across New Game.

## Throwing after a shiny encounter

1. **Before injection**, enable **Preload capture search after the encounter**; it is enabled by default. Select the capture ball: Poké Ball is the default and Ultra Ball is also available. An existing 0.6.0 RAM injection cannot be extended during battle. After updating the plugin, a new injection is required.
2. After generation starts the battle, choose a ball yourself and stop at the final **Use** confirmation. Hold R, tap SELECT once, then release both buttons.
3. The lower row shows **8** while searching and **9** during the throw countdown. At the deadline, the plugin sends **A** once. Capture search groups adjacent successful candidates and prefers the centre of the run; a three-candidate run uses its middle candidate. **Green means the current advance and the A-input deadline have matching parity; yellow means they differ.** Parity is only reported here and can be adjusted manually. The capture Offset is included in this comparison. Ho-Oh still uses Up for generation; every capture uses A. This continues on the console after the PC installation session ends, without returning to Mystery Gift or reseeding.
4. Press **R+SELECT** again to cancel; the display changes to E. You can start another search from E, or from C after one throw. Holding the buttons does not repeatedly enable it. Cancellation stops the automatic throw.
5. Once displayed, the target stays fixed. A missed deadline, changed callback or failed RNG check shows a red D notice for about one second before searching again. The plugin does not send a late input for the old target. After a throw, C means an input was sent; check the game for the actual capture result.

The capture model follows the user-provided v24 / v27g verification logic: the Poké Ball threshold is **16643**, while Ultra Ball uses **19784**; all four strict checks must pass at every possible start in the Offset band. The menu currently distinguishes these two balls and has no HP or status filters. This applies to ordinary catchable wild battles. Safari Zone, Trainer battles and uncatchable targets do not use this menu flow.

**Capture Offset and generation Offset are independent**, both measured in RNG advances. Capture Offset counts from the seed at the actual A-input callback to the state before the first shake Random call. The resident code separately includes the single RFU advance before that callback. The default **241** is a reference awaiting calibration. A blank upper bound equals the lower bound; supplying an upper bound requires success throughout the band. The v24 range of 242–245 was measured on the older SysBot path and does not establish a verified Offset for this plugin.

The original Python model has been verified on hardware by the user. **This plugin's throw entry point, one-shot input timing, capture display and Offset still need hardware acceptance testing.** Verify them in ordinary, non-shiny test runs first, then keep the validated capture Offset fixed for shiny runs. See the [capture model notes (Chinese)](docs/CAPTURE_MODEL.md) for provenance and coordinate definitions.

## Offset

The unit is **RNG advances**, rather than video frames or seconds. Presets and manual values are additional lead advances: Mewtwo has a base of 1, the Kanto birds / other stationary targets a base of 2, and wild encounters a base of 1. Articuno's preset is 3, giving a total lead of 5. Mewtwo's preset is 2, giving a total lead of 3.

Presets appear beside the target / location choices. A blank manual Offset uses the preset; entering **0** explicitly overrides it. The accepted range is 0..65533. The selected game determines which column applies. **Unknown wild Offsets default to 256.**

| Wild location | FireRed | LeafGreen |
| --- | ---: | ---: |
| Routes 1, 2, 3, 4, 5, 6, 11, 18, 24 and 25 | 256 | 256 (unknown default) |
| Viridian Forest | 250 | 256 (unknown default) |
| Mt. Moon, Diglett's Cave | 263 | 256 (unknown default) |
| Power Plant | 256 (unknown default) | 263 |
| Pokémon Tower 3F | 259 | 256 (unknown default) |
| Safari Zone | 256 | 257 |
| Pokémon Mansion | 257 | 257 |
| Victory Road, Icefall Cave, Cerulean Cave | 263 | 256 (unknown default) |
| Mt. Ember | 256 | 256 |
| Other / no reference data | 256 | 256 |

Stationary reference values include 3 for starters / Magikarp / Snorlax / Togepi / roamer initialization / fossils / Game Corner, 4 for Eevee, 6 for the Fighting Dojo, 86 for Hypno, 501 for Deoxys, 277 for Lugia and 379 for Ho-Oh. Electrode, Lapras and custom targets have no reference value yet and retain 0.

The reference table was supplied by the user. It has not been tested for every trigger, language or scene, and reference video-frame delays have not been established as measured advances. If the actual result is 3 advances later than the original target, add 3 to the current additional Offset; if it is 3 earlier, subtract 3. The second tool can suggest this correction. Confirm it over multiple hardware runs.

Search ranges include both endpoints and allow a maximum of 9999999. A stationary index is the state before the first PID draw. A wild index is the state before encounter-slot selection, followed by level, nature and PID rerolls. Re-encountering an already initialized roamer does not generate a new individual. Fixed-PID trades and ordinary bred eggs are outside these models.

## Wild species and IV filters

Choose **game → wild category → encounter type → exact location / floor → wild Pokémon**. Species defaults to Any. The data includes 132 FireRed / LeafGreen encounter tables, separating grass / caves, water, Rock Smash and all three rods. Floors, Safari areas and version-exclusive species are handled separately. For example, choosing Pikachu in Viridian Forest accepts only Pikachu slots from that table. Power Plant Electabuzz is FireRed-only.

The species dropdown lists all included wild species and does not shrink dynamically with the other fields. Check the game, location and encounter type before installing; invalid combinations are rejected. Species filtering requires an exact floor / area, rather than Other / Unknown or a combined-floor location. Without a species filter, the broader locations and their Offsets remain available. Altering Cave's event table must match the game state. Unown has its own category and room model, separate from ordinary nature rerolls. The filter does not read the console's current map or handle a roamer replacing an ordinary Sweet Scent encounter.

**Lower and upper bounds for all six IVs are active in the console search** and can be combined with species, nature and shiny filters. Input order is HP, Attack, Defense, Sp. Atk, Sp. Def, Speed. For at least 25 Sp. Atk and Speed, use lower bounds `0,0,0,25,0,25` and keep upper bounds at `31,31,31,31,31,31`. For exactly 0 Speed, set both Speed bounds to 0. Stricter conditions can leave no result in the range. The filter does not modify Pokémon data or guarantee a hit. Start with non-shiny results allowed and unrestricted IVs, check species and Offset, then add conditions gradually.

## Console display and controls

Normally, the upper row shows the current seed as eight hexadecimal digits. The lower row contains a status marker and seven decimal digits.

| Lower row | Meaning |
| --- | --- |
| Axxxxxxx | Generation search position |
| Bxxxxxxx | Advances remaining until the input deadline; yellow for different parity, green for matching parity with an available callback |
| 8xxxxxxx | Capture search position |
| 9xxxxxxx | Advances remaining until the throw's A-input deadline; yellow for different parity, green for matching parity with an available callback |
| C0000001 / C0000000 | Waiting for this callback / one input sent |
| D00000xx | Reason for a missed deadline or failed input; shown in red for about one second before retrying within the active range |
| E0000000 / F0000000 | Range exhausted (or capture cancelled) / advance tracking invalid |

A visible B or 9 target stays fixed; a colour change does not select a new target. Generation search still filters for a reachable parity. Capture search prefers the centre of its successful run, while its parity colour only reports the current state and does not move that centre. Parity is checked against the input deadline after applying the corresponding Offset. Green does not establish that the Offset is calibrated. An actual miss shows D before retrying, without a late input. Sending an input stops automatic searching. C records that an input was sent; observe the game to check its effect. Capture can be manually rearmed with R+SELECT.

| Hold | Upper row | Lower row |
| --- | --- | --- |
| L | Initial seed | Absolute advances |
| R | HP, Attack, Defense, Speed; two decimal digits each | Sp. Atk, Sp. Def, Hidden Power type number, power; two decimal digits each |
| L+R | Full PID of the last party member, in hexadecimal | Party position, 1..6 |

For example, all 31 IVs with Dark-type Hidden Power 70 display **31313131 / 31311670** while holding R. Type numbers 01..16 are Fighting, Flying, Poison, Ground, Rock, Bug, Ghost, Steel, Fire, Water, Grass, Electric, Psychic, Ice, Dragon and Dark.

R reads the current last party member, rather than a saved copy. An empty party, invalid record or checksum failure displays FFFFFFFF / FFFFFFFF. L+R with an empty party displays FFFFFFFF / 00000000. These views do not pause the countdown or scheduled input. A hidden D notice continues its visible duration after the buttons are released. The plugin does not distinguish ZL / ZR as separate inputs.

During generation, overworld profiles display on the overworld. Sweet Scent, fishing, Unown and starter profiles also display and run in menus; each first needs to return to the overworld to establish the actual seed. A menu profile can send input at its deadline, so stop at the correct decision point yourself. Generation does not send input to recognized battle callbacks. Manually enabling capture allows battle / bag callbacks and the capture display.

D reason codes: 04 = callback unavailable or changed; 09 = input deadline passed; 10 = main loop busy; 11 = callback RNG did not match the expected single wireless advance; 12 = input callback expired. If an overworld profile misses its target while Teachy TV is open, its notice appears and starts counting down after returning to the overworld.

## Manual PID lookup

In the second tool, **manually enter** the initial seed shown by L and the actual PID shown by L+R, both in hexadecimal. Choose the same category, target, method and range as the run. Optionally enter the original target advance and the Offset used to see the error and a suggested new Offset.

For initial seed **C76F**, PID **4762A09B** and Articuno, the actual advance is **3354**. With original target 3351 and additional Offset 3, the difference is +3 and the suggested additional Offset is 6.

Wild PID rerolls can make several encounter starts share a PID. The tool lists all candidates; narrow the actual range or compare against the IVs shown by R. The report's IVs / Hidden Power are **predictions for the selected method**. A lookup alone does not prove input success or capture provenance.

## Development and distribution

Source: [axechaso/frlg-rng-assist](https://github.com/axechaso/frlg-rng-assist). Development and distribution are independent. Pushes run GitHub Actions and produce a test package. The development host is pinned to v0.39.1 / 4780dcaeac52479e6212483009f64f348581d7cc, with Python 3.13 and GCC 15.2.1.

```powershell
python -m pip install -r requirements-dev.txt
$env:POKELDN_SOURCE = 'D:\path\to\pokeldn-v0.39.1'
python -m ruff check .
python -m pytest -q
python scripts/build_guest.py --check
python D:\path\to\pokeldn-v0.39.1\scripts\pack_plugin.py . -o dist\frlg-rng-assist-0.7.3.pokeplugin
```

To rebuild, set ARM_TOOLCHAIN to the ARM tool directory, including its trailing separator, then run scripts/build_guest.py. The resident reservation remains 2200 bytes. The ordinary resident uses 2152 bytes; capture-enabled stationary / wild / Unown variants use 2068 / 2188 / 2200 bytes. Installation selects one complete variant for the model; do not combine it with other resident hooks. After initialization, three RAM words holding first / initial jump parameters are reused as scratch state without enlarging the reservation. Species are still encoded as a 100-bit slot mask. The plugin does not write RNG, Pokémon, save or ROM data. The game's decryption accessor receives only a stack copy.

To update static encounter data, run `python scripts/import_wild_data.py --decomp PATH --pokefinder PATH`. Committed data records its source commits. Users do not need these development dependencies. See NOTICE for species / nature translation sources and licences.

Reports are stored in PokeLDN's FRLG RNG Assist library without overwriting existing files. Licensed under AGPL-3.0-or-later; see [NOTICE](NOTICE.md) for sources. The PokeLDN author does not review or support this third-party plugin.
