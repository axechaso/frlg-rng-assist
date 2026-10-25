"""Rebuild our small data snapshots from pret/pokefirered and PokeFinder sources."""

import argparse
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent

# Canonical Offset regions and localized map stems. Floors / rooms stay explicit.
STEMS = {
    "VIRIDIAN_FOREST": ("viridian-forest", "常青森林", "Viridian Forest", "トキワのもり"),
    "MT_MOON": ("mt-moon", "月见山", "Mt. Moon", "おつきみやま"),
    "SSANNE_EXTERIOR": ("ss-anne", "圣特安努号外侧", "S.S. Anne exterior", "サント・アンヌごう 外側"),
    "DIGLETTS_CAVE": ("diglett-cave", "地鼠洞穴", "Diglett's Cave", "ディグダのあな"),
    "VICTORY_ROAD": ("victory-road", "冠军之路", "Victory Road", "チャンピオンロード"),
    "POKEMON_MANSION": ("pokemon-mansion", "宝可梦屋", "Pokémon Mansion", "ポケモンやしき"),
    "SAFARI_ZONE": ("safari-zone", "狩猎地带", "Safari Zone", "サファリゾーン"),
    "CERULEAN_CAVE": ("cerulean-cave", "华蓝洞窟", "Cerulean Cave", "ハナダのどうくつ"),
    "ROCK_TUNNEL": ("rock-tunnel", "岩山隧道", "Rock Tunnel", "イワヤマトンネル"),
    "SEAFOAM_ISLANDS": ("seafoam-islands", "双子岛", "Seafoam Islands", "ふたごじま"),
    "POKEMON_TOWER": ("pokemon-tower", "宝可梦塔", "Pokémon Tower", "ポケモンタワー"),
    "POWER_PLANT": ("power-plant", "无人发电厂", "Power Plant", "むじんはつでんしょ"),
    "MT_EMBER": ("mt-ember", "灯火山", "Mt. Ember", "ともしびやま"),
    "THREE_ISLAND_BERRY_FOREST": ("berry-forest", "树果森林", "Berry Forest", "きのみのもり"),
    "FOUR_ISLAND_ICEFALL_CAVE": ("icefall-cave", "冻瀑洞窟", "Icefall Cave", "いてだきのどうくつ"),
    "SIX_ISLAND_PATTERN_BUSH": ("pattern-bush", "标志之林", "Pattern Bush", "しるしのはやし"),
    "FIVE_ISLAND_LOST_CAVE": ("lost-cave", "不归之穴", "Lost Cave", "かえらずのあな"),
    "ONE_ISLAND_KINDLE_ROAD": ("kindle-road", "热气之路", "Kindle Road", "ほてりのみち"),
    "ONE_ISLAND_TREASURE_BEACH": ("treasure-beach", "宝物海滩", "Treasure Beach", "たからのはま"),
    "TWO_ISLAND_CAPE_BRINK": ("cape-brink", "边缘海岬", "Cape Brink", "きわのみさき"),
    "THREE_ISLAND_BOND_BRIDGE": ("bond-bridge", "索桥", "Bond Bridge", "きずなばし"),
    "THREE_ISLAND_PORT": ("three-island-port", "第 3 岛码头", "Three Island Port", "３のしま みなと"),
    "FIVE_ISLAND_RESORT_GORGEOUS": ("resort-gorgeous", "豪华度假区", "Resort Gorgeous", "ゴージャスリゾート"),
    "FIVE_ISLAND_WATER_LABYRINTH": ("water-labyrinth", "水之迷宫", "Water Labyrinth", "みずのめいろ"),
    "FIVE_ISLAND_MEADOW": ("five-island-meadow", "第 5 岛空地", "Five Isle Meadow", "５のしま あきち"),
    "FIVE_ISLAND_MEMORIAL_PILLAR": ("memorial-pillar", "回忆之塔", "Memorial Pillar", "おもいでのとう"),
    "SIX_ISLAND_OUTCAST_ISLAND": ("outcast-island", "外岛", "Outcast Island", "はずれのしま"),
    "SIX_ISLAND_GREEN_PATH": ("green-path", "绿之步道", "Green Path", "みどりのさんぽみち"),
    "SIX_ISLAND_WATER_PATH": ("water-path", "水之步道", "Water Path", "みずのさんぽみち"),
    "SIX_ISLAND_RUIN_VALLEY": ("ruin-valley", "遗迹山谷", "Ruin Valley", "いせきのたに"),
    "SEVEN_ISLAND_TRAINER_TOWER": ("trainer-tower", "训练家塔", "Trainer Tower", "トレーナータワー"),
    "SEVEN_ISLAND_SEVAULT_CANYON": ("sevault-canyon", "七宝溪谷", "Sevault Canyon", "しっぽうけいこく"),
    "SEVEN_ISLAND_TANOBY_RUINS": ("tanoby-ruins", "阿斯卡纳遗迹", "Tanoby Ruins", "アスカナいせき"),
    "SIX_ISLAND_ALTERING_CAVE": ("altering-cave", "变幻洞窟", "Altering Cave", "へんげのどうくつ"),
    "PALLET_TOWN": ("pallet-town", "真新镇", "Pallet Town", "マサラタウン"),
    "VIRIDIAN_CITY": ("viridian-city", "常青市", "Viridian City", "トキワシティ"),
    "CERULEAN_CITY": ("cerulean-city", "华蓝市", "Cerulean City", "ハナダシティ"),
    "VERMILION_CITY": ("vermilion-city", "枯叶市", "Vermilion City", "クチバシティ"),
    "CELADON_CITY": ("celadon-city", "玉虹市", "Celadon City", "タマムシシティ"),
    "FUCHSIA_CITY": ("fuchsia-city", "浅红市", "Fuchsia City", "セキチクシティ"),
    "CINNABAR_ISLAND": ("cinnabar-island", "红莲镇", "Cinnabar Island", "グレンタウン"),
    "ONE_ISLAND": ("one-island", "第 1 岛", "One Island", "１のしま"),
    "FOUR_ISLAND": ("four-island", "第 4 岛", "Four Island", "４のしま"),
    "FIVE_ISLAND": ("five-island", "第 5 岛", "Five Island", "５のしま"),
}
SUFFIX = {
    "CENTER": ("中心区", "Center", "中央"), "EAST": ("东区", "East", "東"),
    "NORTH": ("北区", "North", "北"), "SOUTH": ("南区", "South", "南"),
    "WEST": ("西区", "West", "西"), "EXTERIOR": ("外侧", "Exterior", "外側"),
    "ENTRANCE": ("入口", "Entrance", "入口"), "BACK": ("深处", "Back", "奥"),
    "SUMMIT_PATH": ("山顶通道", "Summit Path", "頂上への道"),
    "RUBY_PATH": ("红宝石通道", "Ruby Path", "ルビーへの道"),
    "STAIRS": ("楼梯", "Stairs", "階段"), "CHAMBER": ("石室", "Chamber", "せきしつ"),
}


def map_identity(map_name, variant):
    raw = map_name.removeprefix("MAP_")
    route = re.fullmatch(r"ROUTE(\d+)(.*)", raw)
    if route:
        number, tail = route.groups()
        region, labels = f"route-{number}", (f"{number} 号道路", f"Route {number}", f"{number}ばんどうろ")
    else:
        stem = next(s for s in sorted(STEMS, key=len, reverse=True) if raw == s or raw.startswith(s + "_"))
        region, *labels = STEMS[stem]
        tail = raw[len(stem):]
    # Tower 3F has its own supplied delay; other floors remain unknown.
    offset_region = "pokemon-tower-3f" if raw == "POKEMON_TOWER_3F" else region
    suffixes = []
    raw_tail = tail = tail.strip("_")
    while tail:
        key = next((s for s in sorted(SUFFIX, key=len, reverse=True)
                    if tail == s or tail.startswith(s + "_")), None)
        if key:
            suffixes.append(SUFFIX[key])
            tail = tail[len(key):].strip("_")
        else:
            key, _, tail = tail.partition("_")
            room = re.fullmatch(r"ROOM(\d+)", key)
            suffixes.append((f"房间 {room[1]}", f"Room {room[1]}", f"部屋 {room[1]}") if room
                            else (key.title(),) * 3)
    table_id = region + ("-" + raw_tail.lower().replace("_", "-") if raw_tail else "")
    if table_id == "diglett-cave-b1f":
        table_id = "diglett-cave"
    if variant != 1:
        table_id += f"-event-{variant}"
        suffixes.append((f"事件表 {variant}", f"Event table {variant}", f"イベント表 {variant}"))
    labels = {language: " · ".join([labels[i], *(s[i] for s in suffixes)])
              for i, language in enumerate(("zh", "en", "ja"))}
    return table_id, offset_region, labels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decomp", type=Path, required=True)
    parser.add_argument("--pokefinder", type=Path, required=True)
    args = parser.parse_args()
    dex = re.findall(r"\bNATIONAL_DEX_([A-Z0-9_]+)\s*,", (args.decomp / "include/constants/pokedex.h").read_text())
    dex = {name: index for index, name in enumerate(dex[:387])}
    rows = json.loads((args.decomp / "src/data/wild_encounters.json").read_text())["wild_encounter_groups"][0]["encounters"]
    tables = {}
    for row in rows:
        game = "firered" if row["base_label"].endswith("_FireRed") else "leafgreen"
        variant = re.search(r"_(\d+)_(?:FireRed|LeafGreen)$", row["base_label"])
        table_id, region, labels = map_identity(row["map"], int(variant[1]) if variant else 1)
        table = tables.setdefault(table_id, {"map": row["map"], "region": region, "labels": labels})
        assert game not in table, (table_id, game)
        table[game] = {field: [[dex[mon["species"].removeprefix("SPECIES_")], mon["min_level"], mon["max_level"]]
                              for mon in row[field]["mons"]]
                       for field in ("land_mons", "water_mons", "rock_smash_mons", "fishing_mons") if field in row}
    decomp_commit = subprocess.check_output(["git", "-C", str(args.decomp), "rev-parse", "HEAD"], text=True).strip()
    pf_commit = subprocess.check_output(["git", "-C", str(args.pokefinder), "rev-parse", "HEAD"], text=True).strip()
    output = ROOT / "frlg_rng_assist_core/data"
    output.mkdir(exist_ok=True)
    (output / "wild_tables.json").write_text(json.dumps({"source": "pret/pokefirered", "commit": decomp_commit,
                                                        "tables": tables}, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    names = {}
    for language in ("en", "ja", "zh"):
        folder = args.pokefinder / f"Source/Core/Resources/i18n/{language}"
        names[language] = [""] + (folder / f"species_{language}.txt").read_text(encoding="utf-8-sig").splitlines()[:386]
    names["natures"] = {language: (args.pokefinder / f"Source/Core/Resources/i18n/{language}/natures_{language}.txt").read_text(encoding="utf-8-sig").splitlines()[:25]
                        for language in ("en", "ja", "zh")}
    names.update(source="Admiral-Fish/PokeFinder", commit=pf_commit)
    (output / "names.json").write_text(json.dumps(names, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Imported {len(tables)} encounter tables in both games; 386 species names in three languages")


if __name__ == "__main__":
    main()
