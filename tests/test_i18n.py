"""Exercise translated forms through the released host's real command builder."""

from dataclasses import replace
import json
from pathlib import Path
import re
from types import SimpleNamespace

import pytest

import install
import lookup
import plugin
from frlg_rng_assist_core.arguments import nature
from frlg_rng_assist_core.i18n import host_language, set_language, tr
from frlg_rng_assist_core.selection import normalize_selection
from frlg_rng_assist_core.translations import TEXT
from frlg_rng_assist_core.wild_tables import names


@pytest.fixture(autouse=True)
def reset_language():
    set_language("zh")
    yield
    set_language("zh")


def catalog(monkeypatch, locale):
    from pokeldn.app import i18n

    monkeypatch.setattr(i18n, "locale", lambda: locale)
    tools = []
    plugin.register(SimpleNamespace(add_tool=lambda game, tool: tools.append(tool)))
    return tools


@pytest.mark.parametrize("locale,language,title", [
    ("zh-Hans", "zh", "RNG：搜索与到点按键"),
    ("ja", "ja", "RNG：検索と時刻指定入力"),
    ("en", "en", "RNG: search and timed input"),
    ("fr", "en", "RNG: search and timed input"),
])
def test_host_display_language_selects_the_entire_catalog(monkeypatch, locale, language, title):
    tools = catalog(monkeypatch, locale)
    assert host_language() == language
    assert [t.key for t in tools] == ["frlg-rng-assist-install", "frlg-rng-assist-lookup"]
    assert tools[0].name == title
    for tool in tools:
        assert tool.fixed[-2:] == ("--ui-language", language)
        text = [tool.name, tool.summary, *tool.steps]
        for field in tool.fields:
            text.extend((field.label, field.help))
            text.extend(label for _, label in field.choices)
            text.extend(help for _, help in field.choice_help)
        if language == "en":
            assert not any(re.search(r"[\u3400-\u9fff\u3040-\u30ff]", s) for s in text)
        fields = {f.flag: f for f in tool.fields}
        assert fields["--species"].when == ("--category", "wild")
        assert fields["--offset"].default == ""
        assert dict(fields["--species"].choices)["25"] == f"#025 {names()[language][25]}"


@pytest.mark.parametrize("language", ["zh", "en", "ja"])
def test_real_forms_keep_values_and_rom_language_independent_of_display(monkeypatch, language):
    from pokeldn.app import command

    tools = catalog(monkeypatch, language)
    root = Path(plugin.__file__).parent
    settings = SimpleNamespace(received="", keys="", capture=False, language=2, gender=0,
                               ids=lambda game: (12345, 2791), name=lambda game: "TEST")
    for tool in tools:
        tool = replace(tool, script=str(root / tool.script))
        values = {"--game": "leafgreen", "--category": "wild", "--target-wild": "fish-super",
                  "--location": "safari-zone-center", "--species": "147", "--nature": "15",
                  "--method-wild": "4", "--initial-seed": "C76F", "--pid": "4762A09B"}
        assert not command.problems(tool, values)
        parser = install.build_parser() if tool.key.endswith("install") else lookup.build_parser()
        parsed = normalize_selection(parser.parse_args(command.build(tool, values, {}, settings)))
        assert (parsed.game, parsed.target, parsed.location, parsed.species, parsed.method, parsed.ui_language) == (
            "leafgreen", "fish-super", "safari-zone-center", 147, 4, language)
        if tool.key.endswith("install"):
            assert parsed.nature == 15
        else:
            assert parsed.initial_seed == 0xC76F and parsed.pid == 0x4762A09B


def test_all_nature_names_are_accepted_in_all_three_languages():
    for language in ("en", "ja", "zh"):
        for index, name in enumerate(names()["natures"][language]):
            assert nature(name) == index


def test_translations_preserve_every_named_placeholder():
    from string import Formatter

    def fields(template):
        return {name for _, name, _, _ in Formatter().parse(template) if name is not None}

    for original, translations in TEXT.items():
        assert len(translations) == 2
        assert all(fields(original) == fields(text) for text in translations)


@pytest.mark.parametrize("language,expected", [
    ("zh", "实际 advance 3354"), ("en", "Actual advance 3354"), ("ja", "実際の消費数 3354"),
])
def test_manual_pid_output_uses_selected_language_and_identical_results(language, expected, tmp_path, capsys):
    assert lookup.main(["--initial-seed", "C76F", "--pid", "4762A09B", "--target", "articuno",
                        "--target-advance", "3351", "--ui-language", language,
                        "--output", str(tmp_path / "hit.json")]) == 0
    output = capsys.readouterr().out
    assert expected in output and "6" in output
    if language == "en":
        assert not re.search(r"[\u3400-\u9fff]", output)
    saved = json.loads((tmp_path / "hit.json").read_text(encoding="utf-8"))
    assert saved["candidates"][0]["actual_advance"] == 3354
    assert saved["candidates"][0]["suggested_offset"] == 6


def test_preview_changes_text_without_changing_console_payload(tmp_path, capsys):
    gifts = []
    for language in ("zh", "en", "ja"):
        folder = tmp_path / language
        folder.mkdir()
        report = folder / "install.json"
        assert install.main(["--preview", "--category", "wild", "--location", "viridian-forest", "--species", "25",
                             "--ui-language", language, "--output", str(report)]) == 0
        output = capsys.readouterr().out
        assert names()[language][25] in output
        if language == "en":
            assert not re.search(r"[\u3400-\u9fff]", output)
        plan = json.loads(report.read_text(encoding="utf-8"))
        gifts.append(Path(plan["gift"]["path"]).read_bytes())
    assert gifts[0] == gifts[1] == gifts[2]


@pytest.mark.parametrize("language", ["zh", "en", "ja"])
def test_iv_validation_is_translated_before_export(language, tmp_path, capsys):
    with pytest.raises(SystemExit) as error:
        install.main(["--preview", "--iv-min", "31,0,0,0,0,0", "--iv-max", "0,31,31,31,31,31",
                      "--ui-language", language, "--output", str(tmp_path / "bad.json")])
    assert error.value.code == 2 and not list(tmp_path.iterdir())
    assert tr("每项 IV 下限必须不大于上限", language) in capsys.readouterr().err
