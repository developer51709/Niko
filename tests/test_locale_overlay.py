"""Beta's bot wording reaching a running bot without reloading a cog.

``webapp.locale_feed`` fetches bot catalogues from beta and calls
``utils.locales.apply_overlay``. The contract these tests pin down is the one
that matters in production: a table a module captured at import time must serve
the new wording, a cleared overlay must fall back to the files on disk, and a
catalogue from another machine must never be able to break a reply.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))


def _write_package(root: Path, catalogues: dict[str, dict[str, Any]]) -> str:
    package = root / "locale_overlay_pkg"
    (package / "locales").mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    for lang, data in catalogues.items():
        (package / "locales" / f"{lang}.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )
    sys.path.insert(0, str(root))
    importlib.invalidate_caches()
    sys.modules.pop(package.name, None)
    return package.name


@pytest.fixture()
def package(tmp_path):
    """A four-language package, cleaned up so no other test sees it."""
    from utils.locales import apply_overlay, reload_locales

    catalogues = {
        "en": {"messages": {"hello": "Hello", "bye": "Bye"}},
        "de": {"messages": {"hello": "Hallo", "bye": "Tschüss"}},
        "es": {"messages": {"hello": "Hola", "bye": "Adiós"}},
        "fr": {"messages": {"hello": "Salut", "bye": "Au revoir"}},
    }
    name = _write_package(tmp_path, catalogues)
    yield name, catalogues
    apply_overlay({})
    reload_locales()
    sys.path = [entry for entry in sys.path if entry != str(tmp_path)]
    sys.modules.pop(name, None)


def test_overlay_reaches_a_table_loaded_before_it(package):
    from utils.locales import apply_overlay, load_locales

    name, catalogues = package
    table = load_locales(name, "messages")
    assert table["de"]["hello"] == "Hallo"

    french = dict(catalogues["fr"]["messages"])
    french["hello"] = "Bonjour"
    apply_overlay({name: {"en": catalogues["en"], "fr": {"messages": french}}})

    # The table was captured before the overlay existed; no reload happens here.
    assert table["fr"]["hello"] == "Bonjour"
    assert table.get("fr", {}).get("hello") == "Bonjour"
    assert "hello" in table["fr"]
    # A language the overlay did not carry keeps its file copy.
    assert table["de"]["hello"] == "Hallo"


def test_clearing_the_overlay_restores_the_files(package):
    from utils.locales import apply_overlay, load_locales

    name, catalogues = package
    table = load_locales(name, "messages")
    french = dict(catalogues["fr"]["messages"])
    french["hello"] = "Bonjour"
    apply_overlay({name: {"en": catalogues["en"], "fr": {"messages": french}}})
    assert table["fr"]["hello"] == "Bonjour"

    apply_overlay({})
    assert table["fr"]["hello"] == "Salut"


def test_a_malformed_overlay_is_ignored(package):
    from utils.locales import apply_overlay, load_locales

    name, catalogues = package
    table = load_locales(name, "messages")

    # A nested object where a string belongs: refused, so the live bot keeps
    # rendering the copy it already had.
    apply_overlay({name: {"en": catalogues["en"], "fr": {"messages": {"hello": {"oops": 1}}}}})
    assert table["fr"]["hello"] == "Salut"

    # A package without English has no key list to measure against.
    apply_overlay({name: {"fr": {"messages": {"hello": "Bonjour"}}}})
    assert table["fr"]["hello"] == "Salut"
