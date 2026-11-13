"""Every moderation string the code asks for exists in the catalogue.

``msg()`` and the panel lookups fall back to the key itself, so a renamed or
mistyped key shows up in Discord as raw text like ``wl_role_missing``. This
walks the moderation modules and checks every key they reference — including the
ones assembled at runtime from fixed vocabularies (whitelist kinds, massrole
actions, panel sections), which a plain text search would miss.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COG = ROOT / "src" / "cogs" / "moderation"
LANGS = ("en", "de", "es", "fr")

#: Lookup helper -> catalogue namespace it reads.
HELPERS = {
    "msg": "messages",
    "_massmsg": "massrole",
    "_pmsg": "warnings_panel",
    "_t": "badwords_panel",
}

#: Keys built from a fixed vocabulary at the call site rather than written out.
DYNAMIC = {
    "messages": (
        "locked", "unlocked", "locked_thread", "unlocked_thread",
        "need_manage_roles", "need_manage_threads",
        "cannot_manage_channel", "cannot_lock_thread",
        "wl_user_added", "wl_role_added", "wl_user_removed", "wl_role_removed",
    ),
    "massrole": (
        "action_add", "action_remove",
        "target_all", "target_bots", "target_humans",
    ),
    "badwords_panel": (
        "mode_censor", "mode_delete",
        "section_overview", "section_words", "section_presets", "section_response",
    ),
}


def _catalogues() -> dict[str, dict]:
    return {
        lang: json.loads((COG / "locales" / f"{lang}.json").read_text(encoding="utf-8"))
        for lang in LANGS
    }


def _referenced_keys() -> dict[str, set]:
    found: dict[str, set] = {namespace: set() for namespace in HELPERS.values()}
    for path in sorted(COG.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            namespace = HELPERS.get(node.func.id)
            if namespace is None or len(node.args) < 2:
                continue
            key = node.args[1]
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                found[namespace].add(key.value)
    for namespace, keys in DYNAMIC.items():
        found[namespace].update(keys)
    return found


def test_every_message_key_the_moderation_cog_asks_for_exists():
    catalogues = _catalogues()
    missing: dict[str, dict[str, list[str]]] = {}

    for namespace, keys in _referenced_keys().items():
        assert keys, f"no {namespace} keys were found; the scan itself broke"
        for lang, data in catalogues.items():
            absent = sorted(set(keys) - set(data.get(namespace, {})))
            if absent:
                missing.setdefault(namespace, {})[lang] = absent

    assert not missing, f"strings the moderation cog asks for are missing: {missing}"
