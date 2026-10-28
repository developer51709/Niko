"""AI guild config reads: partial rows, defaults and cache warm-up.

MongoDB is schemaless, so an ``ai_config`` document created by the bootstrap
``INSERT OR IGNORE ... (guild_id)`` holds only ``guild_id``.  Reading it used to
raise ``KeyError: 'personality'``, which took down ``cogs.ai`` at load and the
startup cache warm-up with it.
"""

import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import utils.ai.config as ai_config  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_cache():
    ai_config._cache.clear()
    ai_config._cache_at.clear()
    ai_config._table_pool = None
    yield
    ai_config._cache.clear()
    ai_config._cache_at.clear()
    ai_config._table_pool = None


class _FakePool:
    def __init__(self, row=None, rows=None):
        self.row = row
        self.rows = list(rows or [])
        self.executed = []

    async def execute(self, query, *args):
        self.executed.append((query, args))

    async def fetchrow(self, query, *args):
        return self.row

    async def fetch(self, query, *args):
        return self.rows


def _use_pool(monkeypatch, pool):
    monkeypatch.setattr(ai_config, "_pool", lambda: pool)
    return pool


# ── Partial rows ──────────────────────────────────────────────────────────────

def test_a_document_with_only_a_guild_id_reads_as_defaults():
    config = ai_config._row_to_config({"guild_id": 1558362495444582462})
    assert config == ai_config.DEFAULT_CONFIG


def test_a_completely_empty_row_reads_as_defaults():
    assert ai_config._row_to_config({}) == ai_config.DEFAULT_CONFIG


def test_present_columns_override_the_defaults():
    config = ai_config._row_to_config({
        "guild_id": 1,
        "personality": "normal",
        "enabled": 0,
        "ai_name": "Nikki",
        "ai_actions_experiment": 1,
        "better_context_experiment": True,
        "multimodal_experiment": "true",
    })
    assert config == {
        "personality": "normal",
        "enabled": "False",
        "ai_name": "Nikki",
        "ai_actions_experiment": "True",
        "better_context_experiment": "True",
        "multimodal_experiment": "True",
    }


@pytest.mark.parametrize("value", [True, 1, "1", "true", "on", "yes"])
def test_boolean_columns_normalise_from_every_storage_form(value):
    assert ai_config._row_to_config({"ai_actions_experiment": value})["ai_actions_experiment"] == "True"


@pytest.mark.parametrize("value", [False, 0, "0", "false", "off", "no"])
def test_false_values_stay_false(value):
    assert ai_config._row_to_config({"enabled": value})["enabled"] == "False"


def test_an_unknown_personality_falls_back_to_cafe():
    assert ai_config._row_to_config({"personality": "verbose"})["personality"] == "cafe"


def test_a_null_personality_falls_back_to_cafe():
    assert ai_config._row_to_config({"personality": None})["personality"] == "cafe"


# ── First-read bootstrap ──────────────────────────────────────────────────────

def test_a_missing_row_is_inserted_with_every_default_column(monkeypatch):
    pool = _use_pool(monkeypatch, _FakePool(row=None))

    config = asyncio.run(ai_config._read_or_default(42))

    assert config == ai_config.DEFAULT_CONFIG
    query, args = pool.executed[-1]
    for column in ("personality", "enabled", "ai_name", "ai_actions_experiment"):
        assert column in query
    # guild_id + the six configured values, so MongoDB gets a complete document.
    assert len(args) == 7
    assert args[0] == 42


def test_saving_a_setting_heals_a_partial_row(monkeypatch):
    pool = _use_pool(monkeypatch, _FakePool(row={"guild_id": 42}))

    config = asyncio.run(ai_config.save_config(42, "personality", "normal"))

    assert config["personality"] == "normal"
    query, args = pool.executed[-1]
    assert query.startswith("INSERT OR REPLACE INTO ai_config")
    # Every column is written, so the document is complete from now on.
    assert len(args) == 7
    assert args[1] == "normal"


# ── Cache warm-up ─────────────────────────────────────────────────────────────

def test_preload_keeps_going_after_a_malformed_row(monkeypatch):
    pool = _use_pool(monkeypatch, _FakePool(rows=[
        {"guild_id": 1, "personality": "normal", "ai_name": "Nikki"},
        {"guild_id": "not-a-number"},
        {"guild_id": 2},
    ]))

    loaded = asyncio.run(ai_config.preload_all())

    assert loaded == 2
    assert ai_config.cached_config(1)["personality"] == "normal"
    assert ai_config.cached_config(1)["ai_name"] == "Nikki"
    # Partial document: defaults, not a crash.
    assert ai_config.cached_config(2) == ai_config.DEFAULT_CONFIG
