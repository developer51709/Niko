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

``load_locales`` returns ``{lang: {key: text}}`` with every language filled in
from English for any key a translation has not caught up with yet, so a new
English string never crashes a guild that speaks another language. Keys may map
to a string or to a list of strings (roleplay keeps its sentence variants in
lists).

A language does not have to be finished, or even present, in every cog. The
website works that way — its pages fall back to English key by key — and the bot
follows it: ``en.json`` is the only file a cog must have, a language it has not
reached yet serves English there, and a language grows one catalogue at a time
without a deploy, a reload or a restart.

A translation written on the beta instance does not have to wait for a deploy.
:mod:`webapp.locale_feed` fetches beta's catalogues and calls
:func:`apply_overlay`; the tables returned here read through that overlay, so a
cog that captured its ``MESSAGES`` at import time serves the new wording on its
next reply. The files on disk remain the fallback and the source of the key
list, so an overlay can never add a key the code does not know about.
"""

from __future__ import annotations

import json
import logging
import sys
import threading
import time
from importlib import util as importlib_util
from pathlib import Path
from typing import Any, Iterator

#: Languages a server can pick, in the order the bot and the site show them.
#: English is the fallback for everything else. Adding a code here makes the
#: language selectable everywhere; its wording then arrives catalogue by
#: catalogue, and every key it does not carry yet is served in English.
SUPPORTED_LANGUAGES: tuple[str, ...] = ("en", "de", "es", "fr", "ru", "ja", "zh", "hi", "ar")
FALLBACK_LANGUAGE = "en"

#: Folder name inside a cog package.
LOCALES_DIRNAME = "locales"

#: locales folder → (file mtimes, raw catalogues keyed by language). Keyed by
#: the folder rather than the package name so two checkouts (or a test package
#: with the same name) cannot share a stale entry.
_CACHE: dict[str, tuple[tuple[float, ...], dict[str, dict[str, Any]]]] = {}

#: Live catalogues pulled from the beta instance: ``package → language → table``.
#: Replaced wholesale so a reader never sees a half-applied set of files.
_OVERLAY: dict[str, dict[str, dict[str, Any]]] = {}
_OVERLAY_REVISION = 0
_OVERLAY_LOCK = threading.Lock()

#: Resolved tables, keyed by everything that can change one: package, namespace,
#: language, overlay revision, and the mtimes of the files on disk.
_RESOLVED: dict[tuple[str, str | None, str, int, tuple[float, ...]], dict[str, Any]] = {}

#: The catalogue signature this process has already read, for the disk watcher:
#: a translator saving a file on this instance is what changes it.
_WATCH: dict = {"signature": None}


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
        if lang == FALLBACK_LANGUAGE:
            raise LocaleError(f"missing locale file: {path}")
        # Not translated here yet. The English copy covers every key, which is
        # how a language can be rolled out one cog at a time.
        return {}
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise LocaleError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise LocaleError(f"{path} must contain a JSON object")
    return data


#: How long a folder's mtime signature is reused.  Every string lookup asks for
#: the catalogues, so a fingerprint of ~300 commands used to stat nine files tens
#: of thousands of times and block the bot loop for half a minute on Render.  The
#: watcher reads a fresh signature (``catalogue_signature``), so an edit is still
#: noticed on its next tick; only a burst of lookups shares one stat round.
_SIGNATURE_TTL = 0.5
_SIGNATURES: dict[str, tuple[float, tuple[float, ...]]] = {}


def _signature(folder: Path, *, fresh: bool = False) -> tuple[float, ...]:
    """The mtimes of a folder's catalogue files, or ``-1`` when one is absent."""
    key = str(folder)
    if not fresh:
        cached = _SIGNATURES.get(key)
        if cached is not None and time.monotonic() - cached[0] < _SIGNATURE_TTL:
            return cached[1]
    mtimes = tuple(
        (folder / f"{lang}.json").stat().st_mtime if (folder / f"{lang}.json").is_file() else -1.0
        for lang in SUPPORTED_LANGUAGES
    )
    _SIGNATURES[key] = (time.monotonic(), mtimes)
    return mtimes


def _catalogues(package: str) -> dict[str, dict[str, Any]]:
    """Every language catalogue for ``package``, cached on file mtimes."""
    folder = locales_path(package)
    key = str(folder)
    mtimes = _signature(folder)
    cached = _CACHE.get(key)
    if cached and cached[0] == mtimes:
        return cached[1]
    raw: dict[str, dict[str, Any]] = {}
    for lang in SUPPORTED_LANGUAGES:
        try:
            table = _load_language(package, lang)
            _validate_language(package, lang, table)
            if lang == FALLBACK_LANGUAGE and not table:
                raise LocaleError(f"{package}: en.json is empty")
        except LocaleError as exc:
            # English is the key list and the fallback, so a broken one is fatal.
            # Anything else is a translation in progress: that language reads as
            # English rather than taking the whole cog down on a live instance.
            if lang == FALLBACK_LANGUAGE:
                raise
            logging.getLogger(__name__).warning("%s: serving %s in English — %s", package, lang, exc)
            table = {}
        raw[lang] = table
    _CACHE[key] = (mtimes, raw)
    return raw


def _validate_language(package: str, lang: str, data: dict[str, Any]) -> None:
    """One language's catalogue must be strings, string lists, or namespaces."""

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

    check(lang, data)


def _validate(package: str, raw: dict[str, dict[str, Any]]) -> None:
    """Every language of a catalogue, English first because it is the fallback."""
    english = raw.get(FALLBACK_LANGUAGE) or {}
    if not english:
        raise LocaleError(f"{package}: en.json is empty")
    for lang in SUPPORTED_LANGUAGES:
        _validate_language(package, lang, raw.get(lang) or {})


def apply_overlay(catalogues: dict[str, dict[str, dict[str, Any]]] | None) -> int:
    """Replace the live overlay with catalogues fetched from beta.

    ``catalogues`` is ``{package: {language: catalogue}}`` — the shape the feed
    publishes. Anything malformed is dropped rather than trusted, and a package
    without an English table is skipped because English is the key list every
    other language falls back to. Returns the new revision, which is what the
    resolved-table cache keys on.

    Call it with ``{}`` (or ``None``) to drop the overlay and go back to the
    files this deployment shipped.
    """
    global _OVERLAY, _OVERLAY_REVISION
    clean: dict[str, dict[str, dict[str, Any]]] = {}
    for package, sections in (catalogues or {}).items():
        if not isinstance(package, str) or not isinstance(sections, dict):
            continue
        languages = {
            lang: table
            for lang, table in sections.items()
            if lang in SUPPORTED_LANGUAGES and isinstance(table, dict) and table
        }
        if not languages.get(FALLBACK_LANGUAGE):
            continue
        try:
            # A catalogue from another machine must look like one of ours before
            # any cog is allowed to read it.
            _validate(package, {lang: languages.get(lang, {}) for lang in SUPPORTED_LANGUAGES})
        except LocaleError:
            continue
        clean[package] = languages
    with _OVERLAY_LOCK:
        _OVERLAY = clean
        _OVERLAY_REVISION += 1
        _RESOLVED.clear()
        return _OVERLAY_REVISION


def overlay_revision() -> int:
    """How many times the live overlay has been replaced in this process."""
    return _OVERLAY_REVISION


def _raw_language(package: str, lang: str) -> dict[str, Any]:
    """One language's catalogue: beta's copy when the overlay has it, else disk."""
    overlay = _OVERLAY.get(package)
    if overlay and lang in overlay:
        return overlay[lang]
    return _catalogues(package)[lang]


def _section(catalogue: dict[str, Any], namespace: str | None) -> dict[str, Any]:
    """The namespace slice of a catalogue, or the whole table for a flat one."""
    if namespace is None:
        return catalogue
    section = catalogue.get(namespace, {})
    return section if isinstance(section, dict) else {}


def _resolve(package: str, namespace: str | None, lang: str) -> dict[str, Any]:
    """One language's table, English-filled, from whichever copy is current."""
    key = (package, namespace, lang, _OVERLAY_REVISION, _signature(locales_path(package)))
    cached = _RESOLVED.get(key)
    if cached is not None:
        return cached
    table = dict(_section(_raw_language(package, FALLBACK_LANGUAGE), namespace))
    table.update(_section(_raw_language(package, lang), namespace))
    if len(_RESOLVED) > 2048:
        _RESOLVED.clear()
    _RESOLVED[key] = table
    return table


class LocaleTable(dict):
    """One language's strings, re-resolved when beta's overlay changes.

    A cog captures the table returned by :func:`load_locales` when it is
    imported. Making that table read through to the current overlay is what lets
    a translation land in a running bot: ``MESSAGES[lang][key]`` and
    ``MESSAGES.get(lang, {}).get(key)`` both see the new wording without the cog
    being reloaded. When nothing has changed, a lookup costs one integer compare.

    The reads resolve against a private table that is replaced whole, never
    mutated, so a reply being built on the bot's event loop can never see a
    half-applied catalogue while the feed swaps one in from its own thread.
    """

    __slots__ = ("_package", "_namespace", "_lang", "_revision", "_table")

    def __init__(self, package: str, namespace: str | None, lang: str) -> None:
        table = _resolve(package, namespace, lang)
        super().__init__(table)
        self._package = package
        self._namespace = namespace
        self._lang = lang
        self._revision = _OVERLAY_REVISION
        self._table = table

    def _current(self) -> dict[str, Any]:
        revision = _OVERLAY_REVISION
        if revision != self._revision:
            try:
                self._table = _resolve(self._package, self._namespace, self._lang)
                self._revision = revision
            except LocaleError:
                # The files moved under us; keep the last good table rather
                # than failing a reply that is already being built.
                pass
        return self._table

    def __getitem__(self, key: str) -> Any:
        return self._current()[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._current().get(key, default)

    def translated(self, key: str) -> bool:
        """Whether this language carries its own wording for ``key``.

        Lookups are English-filled, so a key that exists here may still be the
        English fallback. Callers that publish a translation — Discord's command
        localizations, the help menu's language map — use this to skip languages
        that would only echo English back.
        """
        if self._lang == FALLBACK_LANGUAGE:
            return key in self._current()
        return key in _section(_raw_language(self._package, self._lang), self._namespace)

    def __contains__(self, key: object) -> bool:
        return key in self._current()

    def items(self):
        return self._current().items()

    def keys(self):
        return self._current().keys()

    def values(self):
        return self._current().values()

    def __iter__(self):
        return iter(self._current())

    def __len__(self) -> int:
        return len(self._current())


def available_namespaces(package: str) -> tuple[str, ...]:
    """Namespace names present in ``en.json``; empty for a single-table cog."""
    raw = _catalogues(package)
    return tuple(
        key for key, value in raw[FALLBACK_LANGUAGE].items() if isinstance(value, dict)
    )


def load_locales(package: str, namespace: str | None = None) -> dict[str, dict[str, Any]]:
    """``{lang: {key: text}}`` for one cog (optionally one namespace of it).

    Every supported language is present; the keys a language has not been
    translated for fall back to the English wording, so a translator can lag
    behind — or not have reached this cog at all — without breaking a reply.
    ``namespace`` is required when a cog groups several modules' tables in one
    file.
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

    # Each table resolves lazily, so a catalogue fetched from beta while the
    # process is running is picked up without the caller reloading anything.
    return {lang: LocaleTable(package, namespace, lang) for lang in SUPPORTED_LANGUAGES}


def missing_translations(package: str) -> dict[str, list[str]]:
    """Keys still served from English, per language, for audits and tests.

    Namespaced cogs report ``"namespace.key"`` so a report points at the exact
    line a translator has to fill in.
    """
    _catalogues(package)  # validates the files even when the overlay is current
    english = _raw_language(package, FALLBACK_LANGUAGE)
    missing: dict[str, list[str]] = {}

    for lang in SUPPORTED_LANGUAGES:
        if lang == FALLBACK_LANGUAGE:
            continue
        translated_language = _raw_language(package, lang)
        gaps: list[str] = []
        for key, value in english.items():
            translated = translated_language.get(key)
            if isinstance(value, dict):
                translated = translated if isinstance(translated, dict) else {}
                for sub_key in value:
                    if sub_key not in translated:
                        gaps.append(f"{key}.{sub_key}")
            elif key not in translated_language:
                gaps.append(key)
        missing[lang] = gaps
    return missing


def reload_locales(package: str | None = None) -> None:
    """Drop cached catalogues (tests, and tools that edit JSON at runtime).

    The overlay is left in place on purpose: an update area may rewrite a cog's
    files, and any language the overlay already holds should keep being served
    until the feed replaces it. Bumping the revision makes every live table pick
    the new files up on its next read.
    """
    global _OVERLAY_REVISION
    if package is None:
        _CACHE.clear()
        _SIGNATURES.clear()
    else:
        key = str(locales_path(package))
        _CACHE.pop(key, None)
        _SIGNATURES.pop(key, None)
    with _OVERLAY_LOCK:
        _OVERLAY_REVISION += 1
        _RESOLVED.clear()


def catalogue_packages() -> Iterator[Path]:
    """Every ``locales`` folder under ``src/cogs`` and ``src/utils``."""
    root = Path(__file__).resolve().parent.parent
    for base in (root / "cogs", root / "utils"):
        if not base.is_dir():
            continue
        yield from sorted(base.glob(f"**/{LOCALES_DIRNAME}"))


def catalogue_signature() -> tuple:
    """Every catalogue file's identity, for noticing an edit on this machine."""
    return tuple(
        (str(folder), _signature(folder, fresh=True)) for folder in catalogue_packages()
    )


def refresh_from_disk() -> bool:
    """Re-read the catalogues when a file on this instance changed.

    Production serves beta's wording through the overlay, but beta itself reads
    its own files — and a table a cog captured at import time only re-resolves
    when the revision moves. This is what moves it: the translator saves a JSON
    file, the watcher notices the new mtime, and the next reply uses it. No
    restart, no cog reload. Returns whether anything changed.
    """
    signature = catalogue_signature()
    with _OVERLAY_LOCK:
        if _WATCH.get("signature") == signature:
            return False
        _WATCH["signature"] = signature
    reload_locales()
    return True
