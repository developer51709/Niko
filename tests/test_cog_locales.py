"""The cog layout: translated strings live in ``locales/<lang>.json``.

Every cog keeps its wording next to its code, one JSON file per language. These
checks keep that structure honest: the three files always exist, they always
cover the same keys with the same shapes, no module sneaks a language table back
into Python, and every ``load_locales`` call actually resolves.
"""

from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
LANGS = ("en", "de", "es")

#: A dict key that is a language code, at the start of a line — the shape of the
#: old inline tables. Command decorators carry their translations inside a
#: single-line ``help="…"`` string, so an anchored match ignores them.
LANGUAGE_KEY_LINE = re.compile(r'^\s*"(?P<lang>[a-z]{2})"\s*:\s*\{', re.MULTILINE)
#: Any language dict literal, e.g. ``MESSAGES = {…}`` or ``_UI: dict = {…}``.
DICT_ASSIGNMENT = re.compile(
    r"^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*(?::[^=]+)?=\s*\{", re.MULTILINE
)
#: ``CMDS.help("slots")`` / ``CMDS.text("slots.description")`` /
#: ``CMDS.arg("slots", "amount")``.
CMDS_CALL = re.compile(r'CMDS\.(help|text|arg)\(\s*"([^"]+)"(?:\s*,\s*"([^"]+)")?')
#: ``load_locales("cogs.social", "polls")``.
LOAD_CALL = re.compile(
    r"""load_locales\(\s*["'](?P<package>[^"']+)["'](?:\s*,\s*["'](?P<namespace>[^"']+)["'])?"""
)


def _catalogue_folders() -> list[Path]:
    """Every ``locales`` folder in a cog or a utils package."""
    return sorted((SRC / "cogs").glob("*/locales")) + sorted((SRC / "utils").glob("*/locales"))


def _catalogue_folder_ids() -> list[str]:
    return [str(folder.relative_to(ROOT)) for folder in _catalogue_folders()]


def _read_catalogues(folder: Path) -> dict[str, dict]:
    return {
        lang: json.loads((folder / f"{lang}.json").read_text(encoding="utf-8"))
        for lang in LANGS
    }


def test_every_catalogue_ships_english_german_and_spanish():
    folders = _catalogue_folders()
    assert folders, "no locales folders found"
    for folder in folders:
        present = {lang for lang in LANGS if (folder / f"{lang}.json").is_file()}
        assert present == set(LANGS), f"{folder} is missing {sorted(set(LANGS) - present)}"


@pytest.mark.parametrize("relative", _catalogue_folder_ids())
def test_translations_cover_the_same_namespaces_and_keys(relative):
    catalogues = _read_catalogues(ROOT / relative)
    english = catalogues["en"]
    assert english, f"{relative}/en.json is empty"

    for lang, data in catalogues.items():
        assert set(data) == set(english), (
            f"{relative}/{lang}.json has different namespaces: "
            f"{sorted(set(data) ^ set(english))}"
        )
        for namespace, table in english.items():
            assert set(data[namespace]) == set(table), (
                f"{relative}: {lang}/{namespace} does not translate "
                f"{sorted(set(table) - set(data[namespace]))}"
            )
            for key, value in table.items():
                translated = data[namespace][key]
                assert isinstance(translated, type(value)), (
                    f"{relative}: {lang}/{namespace}.{key} should be "
                    f"{type(value).__name__}, not {type(translated).__name__}"
                )


@pytest.mark.parametrize("relative", _catalogue_folder_ids())
def test_catalogue_trees_are_strings_or_lists_of_strings(relative):
    for lang, data in _read_catalogues(ROOT / relative).items():
        for namespace, table in data.items():
            assert isinstance(table, dict) and table, f"{relative}/{lang}: {namespace} is empty"
            for key, value in table.items():
                leaves = value if isinstance(value, list) else [value]
                assert all(isinstance(item, str) for item in leaves), (
                    f"{relative}/{lang}: {namespace}.{key} must be text"
                )


def test_no_cog_defines_a_language_table_in_python():
    offenders = []
    for path in sorted((SRC / "cogs").rglob("*.py")) + sorted((SRC / "utils").rglob("*.py")):
        if path.name == "i18n.py" or path.name == "locales.py":
            continue
        text = path.read_text(encoding="utf-8")
        for match in LANGUAGE_KEY_LINE.finditer(text):
            offenders.append(f"{path.relative_to(ROOT)}:{match.group('lang')}")
    assert not offenders, (
        "these modules still define an inline language table; move the strings "
        f"into locales/*.json and load them with load_locales(): {offenders}"
    )


def test_message_tables_are_loaded_not_literal():
    offenders = []
    for path in sorted((SRC / "cogs").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for match in DICT_ASSIGNMENT.finditer(text):
            name = match.group("name")
            if name.isupper() and name.endswith("MESSAGES"):
                offenders.append(f"{path.relative_to(ROOT)}:{name}")
    assert not offenders, f"message tables must come from locales/*.json: {offenders}"


def test_every_command_text_reference_resolves():
    """A decorator's CMDS key must exist in its cog's ``commands`` namespace."""
    from utils.command_locales import command_texts

    offenders = []
    for path in sorted((SRC / "cogs").rglob("*.py")):
        relative = path.relative_to(SRC)
        if len(relative.parts) < 3:
            continue
        package = ".".join(relative.parts[:2])
        texts = command_texts(package)
        for match in CMDS_CALL.finditer(path.read_text(encoding="utf-8")):
            kind, key, parameter = match.groups()
            if kind == "help":
                flat = f"{key}.help"
            elif kind == "arg":
                flat = f"{key}.args.{parameter}"
            else:
                flat = key
            if not texts.english(flat):
                offenders.append(f"{relative}: CMDS.{kind}({key!r}) -> {flat!r}")
    assert not offenders, "command text keys missing from locales: " + ", ".join(offenders)


def test_command_text_entries_are_never_empty():
    for folder in _catalogue_folders():
        for lang, data in _read_catalogues(folder).items():
            for key, value in data.get("commands", {}).items():
                assert isinstance(value, str) and value.strip(), (
                    f"{folder.relative_to(ROOT)}/{lang}.json: commands.{key} is empty"
                )


def test_every_load_locales_call_resolves():
    calls = []
    for path in sorted(SRC.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for match in LOAD_CALL.finditer(text):
            calls.append((str(path.relative_to(ROOT)), match.group("package"), match.group("namespace")))
    assert calls, "no load_locales() calls found"

    from utils.locales import load_locales

    for path, package, namespace in calls:
        table = load_locales(package, namespace or None)
        assert set(table) == set(LANGS), f"{path}: {package} is missing a language"
        assert table["en"], f"{path}: {package}/{namespace or ''} is empty"


def _write_package(root: Path, english: dict, german: dict, spanish: dict) -> str:
    package = root / "locale_contract_pkg"
    (package / "locales").mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    for lang, data in (("en", english), ("de", german), ("es", spanish)):
        (package / "locales" / f"{lang}.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )
    name = package.name
    sys.path.insert(0, str(root))
    importlib.invalidate_caches()
    sys.modules.pop(name, None)
    return name


@pytest.fixture()
def temporary_package(tmp_path, monkeypatch):
    created: list[str] = []

    def make(english: dict, german: dict | None = None, spanish: dict | None = None) -> str:
        name = _write_package(
            tmp_path,
            english,
            english if german is None else german,
            english if spanish is None else spanish,
        )
        created.append(name)
        return name

    yield make
    # Keep sys.path clean for the other tests in the session.
    sys.path = [entry for entry in sys.path if entry != str(tmp_path)]
    for name in created:
        sys.modules.pop(name, None)


def test_a_missing_translation_falls_back_to_english(temporary_package):
    from utils.locales import load_locales, reload_locales

    package = temporary_package(
        {"messages": {"hello": "Hello", "bye": "Bye"}},
        {"messages": {"hello": "Hallo"}},
        {"messages": {"hello": "Hola"}},
    )
    table = load_locales(package, "messages")
    assert table["de"]["hello"] == "Hallo"
    assert table["de"]["bye"] == "Bye"
    assert table["es"]["bye"] == "Bye"
    reload_locales(package)


def test_a_flat_catalogue_is_read_without_a_namespace(temporary_package):
    from utils.locales import load_locales

    package = temporary_package({"hello": "Hello"})
    assert load_locales(package)["en"]["hello"] == "Hello"


def test_a_namespaced_catalogue_requires_its_namespace(temporary_package):
    from utils.locales import LocaleError, load_locales

    package = temporary_package({"views": {"hello": "Hello"}})
    with pytest.raises(LocaleError):
        load_locales(package)
    with pytest.raises(LocaleError):
        load_locales(package, "missing")
