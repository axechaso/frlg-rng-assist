"""Plugin-owned UI text; the host locale selects English, Japanese or Chinese."""

from contextvars import ContextVar
from dataclasses import replace
import re

from .wild_tables import names, table_at
from .translations import TEXT

_language = ContextVar("rng_assist_language", default="zh")


def normalize(language):
    tag = str(language).lower().replace("_", "-").split("-")[0]
    return tag if tag in ("zh", "ja") else "en"


def host_language():
    # Optional display-locale helper present in the pinned host. It is not part
    # of the guaranteed API table; an absent helper leaves English usable.
    try:
        from pokeldn.app.i18n import locale
        return normalize(locale())
    except ImportError:
        return "en"


def set_language(language):
    _language.set(normalize(language))


def tr(text, language=None, **values):
    language = normalize(language or _language.get())
    translated = text if language == "zh" else TEXT.get(text, (text, text))[language == "ja"]
    return translated.format(**values) if values else translated


def species_name(species, language=None):
    language = normalize(language or _language.get())
    return names()[language][species] if species else tr("不限", language)


def nature_name(index, language=None):
    return names()["natures"][normalize(language or _language.get())][index]


def location_name(location, fallback, language):
    row = table_at(location)
    if row:
        return row["labels"][language]
    route = re.fullmatch(r"route-(\d+)", location)
    if route:
        return {"zh": f"{route[1]} 号道路", "en": f"Route {route[1]}", "ja": f"{route[1]}ばんどうろ"}[language]
    return tr(fallback, language)


DETAILS = {
    "bulbasaur": "御三家", "charmander": "御三家", "squirtle": "御三家", "magikarp": "购买",
    "eevee": "玉虹市礼物", "hitmonlee": "格斗道场", "hitmonchan": "格斗道场",
    "snorlax12": "12 号道路", "snorlax16": "16 号道路", "hypno": "树果森林", "togepi": "赠蛋",
    **{key: "游走个体初始化" for key in ("raikou", "entei", "suicune")},
    **{key: "化石" for key in ("omanyte", "kabuto", "aerodactyl")},
    **{key: "游戏厅" for key in ("abra", "clefairy", "scyther", "pinsir", "dratini", "porygon")},
    "electrode": "发电厂，两处通用", "lapras": "西尔佛公司",
}


def target_name(key, language=None):
    from .encounters import ENCOUNTERS

    language = normalize(language or _language.get())
    encounter = ENCOUNTERS[key]
    if language == "zh":
        return encounter.name
    if not encounter.species or key == "unown":
        return tr(encounter.name, language)
    label = species_name(386 if key == "deoxys" else encounter.species, language)
    return label + (f" ({tr(DETAILS[key], language)})" if key in DETAILS else "")


def localized_tool(tool, language):
    from .encounters import default_offset

    fields = []
    for field in tool.fields:
        choices = tuple((value, tr(label, language)) for value, label in field.choices)
        if field.flag.startswith("--target-"):
            wild = field.flag in ("--target-wild", "--target-unown")
            choices = tuple((key, target_name(key, language) + ("" if wild else f" · Offset {default_offset(key)}"))
                            for key, _ in field.choices)
        elif field.flag == "--location":
            choices = tuple((key, location_name(key, label.split(" · ")[0], language) +
                             f" · {default_offset('sweet-land', 'firered', key)} / "
                             f"{default_offset('sweet-land', 'leafgreen', key)}")
                            for key, label in field.choices)
        elif field.flag == "--species":
            choices = tuple((value, f"#{int(value):03d} {species_name(int(value), language)}" if int(value)
                             else tr("不限", language)) for value, _ in field.choices)
        elif field.flag == "--nature":
            choices = tuple((value, nature_name(int(value), language) if value else tr("不限", language))
                            for value, _ in field.choices)
        fields.append(replace(field, label=tr(field.label, language), help=tr(field.help, language), choices=choices,
                              choice_help=tuple((key, tr(help, language)) for key, help in field.choice_help)))
    return replace(tool, name=tr(tool.name, language), summary=tr(tool.summary, language),
                   steps=tuple(tr(step, language) for step in tool.steps), fields=tuple(fields),
                   fixed=(*tool.fixed, "--ui-language", language))
