"""A command's help line is a JSON map of translations — read it without damage.

The menu used to un-serialise it with ``json.loads(raw.replace("'", '"'))``,
which rewrites every apostrophe inside the text. French ``d'objets`` became
``d"objets``, the parse failed, and the menu printed the raw map instead of the
sentence — first noticed on ``.use`` and ``.inventory``.
"""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.help.views import get_command_help  # noqa: E402
from utils.command_locales import command_texts, help_mapping  # noqa: E402
from utils.locales import available_namespaces, load_locales  # noqa: E402

SRC = Path(__file__).resolve().parents[1] / "src"
ECONOMY = "cogs.economy"
LOCALES = ("en", "de", "es", "fr")


def guild(preferred_locale: str):
    return SimpleNamespace(guild=SimpleNamespace(preferred_locale=preferred_locale))


def test_the_use_and_inventory_help_lines_keep_their_french_apostrophes():
    texts = command_texts(ECONOMY)

    for key in ("use", "inventory"):
        mapping = help_mapping(texts.help(key))
        expected = texts.language_map(f"{key}.help")

        assert set(mapping) == set(LOCALES)
        assert mapping == expected
        assert "'" in mapping["fr"], "this is the case that used to break the parser"


def test_the_menu_shows_the_translated_sentence_not_the_serialised_map():
    raw = command_texts(ECONOMY).help("use")
    command = SimpleNamespace(help=raw)

    french = get_command_help(guild("fr"), command)
    english = get_command_help(guild("en"), command)
    fallback = get_command_help(guild("pl"), command)

    assert french.startswith("Utiliser un consommable")
    assert english.startswith("Use a consumable")
    assert fallback == english
    for text in (french, english):
        assert "{" not in text and "en" != text[:3]


def test_a_python_literal_map_still_reads_back():
    assert help_mapping("{'en': 'Reset XP.', 'de': 'XP zurücksetzen.'}") == {
        "en": "Reset XP.",
        "de": "XP zurücksetzen.",
    }


def test_values_that_are_not_a_map_are_left_alone():
    assert help_mapping("Reset XP.") == {}
    assert help_mapping("") == {}
    assert help_mapping(None) == {}
    assert help_mapping("[1, 2]") == {}


def test_every_command_help_line_survives_serialisation():
    """Round-trip every help entry in every cog, in every language."""
    checked = 0
    for catalogue in sorted((SRC / "cogs").glob("**/locales/en.json")):
        package = ".".join(catalogue.parent.parent.relative_to(SRC).parts)
        if "commands" not in available_namespaces(package):
            continue
        tables = load_locales(package, "commands")
        for key, english in tables["en"].items():
            if not key.endswith(".help"):
                continue
            expected = {
                lang: tables[lang][key] for lang in LOCALES if tables[lang].get(key)
            }
            assert help_mapping(json.dumps(expected, ensure_ascii=False)) == expected, key
            checked += 1

    assert checked > 100


def test_the_dashboard_reads_the_same_map():
    from webapp.commands import _description_value

    mapping = _description_value(command_texts(ECONOMY).help("inventory"))

    assert isinstance(mapping, dict)
    assert mapping["fr"].startswith("Consulter ta collection d'objets")
    # Plain text is still passed through untouched.
    assert _description_value("Reset XP.") == "Reset XP."
