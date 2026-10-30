"""Per-cog JSON message catalogues.

Every cog keeps its user-facing strings in ``locales/`` next to its package::

    cogs/social/
        __init__.py
        birthdays.py
        locales/
            en.json
            de.json
            es.json

A catalogue is one JSON object per language. A cog with a single table stores
its keys at the root; a cog whose modules each keep their own table groups them
under a namespace::

    {
      "birthdays": {"saved": "…"},
      "polls": {"created": "…"}
    }

Modules load their slice with::

    from utils.locales import load_locales
    MESSAGES = load_locales(__package__, "birthdays")

``load_locales`` returns ``{lang: {key: text}}`` with German and Spanish filled
in from English for any key a translation has not caught up with yet, so a new
English string never crashes a guild that speaks another language. Keys may map
to a string or to a list of strings (roleplay keeps its sentence variants in
lists).
"""

from __future__ import annotations

import json
import sys
from importlib import util as importlib_util
from pathlib import Path
from typing import Any, Iterator

#: Languages the bot ships. English is the fallback for everything else.
SUPPORTED_LANGUAGES: tuple[str, ...] = ("en", "de", "es")
FALLBACK_LANGUAGE = "en"

#: Folder name inside a cog package.
LOCALES_DIRNAME = "locales"

#: locales folder → (file mtimes, raw catalogues keyed by language). Keyed by
#: the folder rather than the package name so two checkouts (or a test package
#: with the same name) cannot share a stale entry.
_CACHE: dict[str, tuple[tuple[float, ...], dict[str, dict[str, Any]]]] = {}


class LocaleError(RuntimeError):
    """A catalogue is missing, unreadable, or not shaped like a catalogue."""


def locales_path(package: str) -> Path:
    """The ``locales`` folder inside ``package`` (``"cogs.social"``).

    Catalogues always live in a package folder, never beside a single module,
    so a ``locales`` folder can never shadow this module's own name.
    """
    module = sys.modules.get(package)
    spec = getattr(module, "__spec__", None)
    if spec is None or not spec.submodule_search_locations:
        spec = importlib_util.find_spec(package)
    if spec is None:
        raise LocaleError(f"unknown package: {package}")
    locations = list(spec.submodule_search_locations or ())
    if not locations:
        raise LocaleError(
            f"{package} is a module, not a package; move it into a package folder "
            f"with a {LOCALES_DIRNAME}/ directory to give it a catalogue"
        )
    return Path(locations[0]) / LOCALES_DIRNAME


def _load_language(package: str, lang: str) -> dict[str, Any]:
    path = locales_path(package) / f"{lang}.json"
    if not path.is_file():
        raise LocaleError(f"missing locale file: {path}")
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise LocaleError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise LocaleError(f"{path} must contain a JSON object")
    return data


def _catalogues(package: str) -> dict[str, dict[str, Any]]:
    """Every language catalogue for ``package``, cached on file mtimes."""
    folder = locales_path(package)
    key = str(folder)
    mtimes = tuple(
        (folder / f"{lang}.json").stat().st_mtime if (folder / f"{lang}.json").is_file() else -1.0
        for lang in SUPPORTED_LANGUAGES
    )
    cached = _CACHE.get(key)
    if cached and cached[0] == mtimes:
        return cached[1]
    raw = {lang: _load_language(package, lang) for lang in SUPPORTED_LANGUAGES}
    _validate(package, raw)
    _CACHE[key] = (mtimes, raw)
    return raw


def _validate(package: str, raw: dict[str, dict[str, Any]]) -> None:
    english = raw[FALLBACK_LANGUAGE]
    if not english:
        raise LocaleError(f"{package}: en.json is empty")

    def is_leaf(value: Any) -> bool:
        if isinstance(value, str):
            return True
        return isinstance(value, list) and all(isinstance(item, str) for item in value)

    def check(lang: str, data: dict[str, Any], parent: str = "") -> None:
        for key, value in data.items():
            name = f"{parent}{key}"
            if is_leaf(value):
                continue
            if isinstance(value, dict) and value:
                if parent == "":
                    check(lang, value, f"{key}.")
                    continue
            raise LocaleError(
                f"{package}/{lang}.json: {name!r} must be a string, a list of strings, "
                "or a namespace object"
            )

    for lang in SUPPORTED_LANGUAGES:
        check(lang, raw[lang])


def available_namespaces(package: str) -> tuple[str, ...]:
    """Namespace names present in ``en.json``; empty for a single-table cog."""
    raw = _catalogues(package)
    return tuple(
        key for key, value in raw[FALLBACK_LANGUAGE].items() if isinstance(value, dict)
    )


def load_locales(package: str, namespace: str | None = None) -> dict[str, dict[str, Any]]:
    """``{lang: {key: text}}`` for one cog (optionally one namespace of it).

    Missing German/Spanish keys fall back to the English wording, so a
    translator can lag behind without breaking a reply. ``namespace`` is
    required when a cog groups several modules' tables in one file.
    """
    raw = _catalogues(package)
    english = raw[FALLBACK_LANGUAGE]

    if namespace is not None:
        if namespace not in english:
            raise LocaleError(f"{package}: en.json has no {namespace!r} namespace")
        if not isinstance(english[namespace], dict):
            raise LocaleError(f"{package}: {namespace!r} is not a namespace object")
        english = english[namespace]
    elif any(isinstance(value, dict) for value in english.values()):
        names = ", ".join(available_namespaces(package))
        raise LocaleError(
            f"{package} splits its strings into namespaces ({names}); "
            "pass one to load_locales()"
        )

    table: dict[str, dict[str, Any]] = {}
    for lang in SUPPORTED_LANGUAGES:
        section = raw[lang]
        if namespace is not None:
            section = section.get(namespace, {})
            if not isinstance(section, dict):
                section = {}
        merged = dict(english)
        merged.update(section)
        table[lang] = merged
    return table


def missing_translations(package: str) -> dict[str, list[str]]:
    """Keys still served from English, per language, for audits and tests.

    Namespaced cogs report ``"namespace.key"`` so a report points at the exact
    line a translator has to fill in.
    """
    raw = _catalogues(package)
    english = raw[FALLBACK_LANGUAGE]
    missing: dict[str, list[str]] = {}

    for lang in SUPPORTED_LANGUAGES:
        if lang == FALLBACK_LANGUAGE:
            continue
        gaps: list[str] = []
        for key, value in english.items():
            translated = raw[lang].get(key)
            if isinstance(value, dict):
                translated = translated if isinstance(translated, dict) else {}
                for sub_key in value:
                    if sub_key not in translated:
                        gaps.append(f"{key}.{sub_key}")
            elif key not in raw[lang]:
                gaps.append(key)
        missing[lang] = gaps
    return missing


def reload_locales(package: str | None = None) -> None:
    """Drop cached catalogues (tests, and tools that edit JSON at runtime)."""
    if package is None:
        _CACHE.clear()
    else:
        _CACHE.pop(str(locales_path(package)), None)


def catalogue_packages() -> Iterator[Path]:
    """Every ``locales`` folder under ``src/cogs`` and ``src/utils``."""
    root = Path(__file__).resolve().parent.parent
    for base in (root / "cogs", root / "utils"):
        if not base.is_dir():
            continue
        yield from sorted(base.glob(f"**/{LOCALES_DIRNAME}"))
