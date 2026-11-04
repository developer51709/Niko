"""The owner's translation card switch on the support servers' status panel."""

import asyncio
import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from cogs.staff.panels import status as panel
from utils import panel_settings


ROOT = Path(__file__).resolve().parents[1]


class FakePool:
    """Records the statements a real pool would receive."""

    def __init__(self, rows=None):
        self.rows = list(rows or [])
        self.executed = []

    async def fetch(self, query, *args):
        return [dict(row) for row in self.rows]

    async def execute(self, query, *args):
        self.executed.append((" ".join(query.split()), args))


def bot_with(pool):
    return SimpleNamespace(cxn=pool)


def test_the_card_is_off_until_the_owner_turns_it_on():
    pool = FakePool()
    bot = bot_with(pool)
    asyncio.run(panel_settings.load(bot))

    assert panel_settings.show_translation_card() is False

    asyncio.run(panel_settings.set_translation_card(True, "owner-1", bot))

    assert panel_settings.show_translation_card() is True
    assert [statement for statement, _args in pool.executed] == [
        "DELETE FROM panel_settings WHERE key = $1",
        "INSERT INTO panel_settings (key, value) VALUES ($1, $2)",
    ]
    assert pool.executed[0][1] == ("status_panel_translation_card",)
    assert pool.executed[1][1] == ("status_panel_translation_card", "1")

    asyncio.run(panel_settings.set_translation_card(False, "owner-1", bot))

    assert panel_settings.show_translation_card() is False
    assert pool.executed[-1][0] == "DELETE FROM panel_settings WHERE key = $1"


def test_startup_reads_a_stored_switch():
    pool = FakePool(rows=[{"key": "status_panel_translation_card", "value": "1"}])

    asyncio.run(panel_settings.load(bot_with(pool)))

    assert panel_settings.show_translation_card() is True
    assert panel_settings.snapshot() == {"status_panel_translation_card": True}


def test_a_missing_or_unreadable_database_leaves_the_card_off():
    asyncio.run(panel_settings.load(SimpleNamespace(cxn=None)))

    assert panel_settings.show_translation_card() is False

    class BrokenPool:
        async def fetch(self, *_args):
            raise RuntimeError("no route to host")

    asyncio.run(panel_settings.load(bot_with(BrokenPool())))

    assert panel_settings.show_translation_card() is False


def test_an_unknown_setting_is_refused_before_any_write():
    pool = FakePool()
    bot = bot_with(pool)

    with pytest.raises(ValueError):
        asyncio.run(panel_settings.set_flag("status_panel_everything", True, "owner-1", bot))

    assert pool.executed == []


def test_a_switch_without_a_pool_fails_instead_of_lying_to_the_dashboard():
    with pytest.raises(RuntimeError):
        asyncio.run(panel_settings.set_translation_card(True, "owner-1", SimpleNamespace(cxn=None)))


def _locale_payload():
    return {
        "languages": ["en", "de", "fr", "ru"],
        "scanned_at": 1_700_000_000,
        "source": {"mode": "beta", "age_seconds": 12},
        "bot": [
            {"code": "en", "label": "English", "translated": 100, "total": 100, "percent": 100.0},
            {"code": "de", "label": "German", "translated": 50, "total": 100, "percent": 50.0},
            {"code": "fr", "label": "French", "translated": 80, "total": 100, "percent": 80.0},
            {"code": "ru", "label": "Russian", "translated": 20, "total": 100, "percent": 20.0},
        ],
        "website": [
            {"code": "en", "label": "English", "translated": 100, "total": 100, "percent": 100.0},
            {"code": "de", "label": "German", "translated": 100, "total": 100, "percent": 100.0},
            {"code": "fr", "label": "French", "translated": 40, "total": 100, "percent": 40.0},
            {"code": "ru", "label": "Russian", "translated": 10, "total": 100, "percent": 10.0},
        ],
    }


def test_the_snapshot_counts_the_other_languages_and_never_english(monkeypatch):
    module = importlib.import_module("webapp.status")
    monkeypatch.setattr(module, "locale_status", _locale_payload)

    snapshot = panel._translation_snapshot()

    # Three languages besides English, counted over every key of every language
    # rather than over English's permanent 100%.
    assert snapshot["languages"] == 4
    assert snapshot["bot"] == 50.0
    assert snapshot["site"] == 50.0
    # Most translated on the website first: that is what a reader wants to see.
    assert [row["label"] for row in snapshot["rows"]] == ["German", "French", "Russian"]
    assert snapshot["mode"] == "beta"
    assert snapshot["age_seconds"] == 12
    assert snapshot["scanned_at"] == 1_700_000_000


def test_the_snapshot_drops_the_card_when_webapp_cannot_answer(monkeypatch):
    module = importlib.import_module("webapp.status")

    def broken():
        raise RuntimeError("webapp is not up yet")

    monkeypatch.setattr(module, "locale_status", broken)

    assert panel._translation_snapshot() is None


def _status_bot():
    return SimpleNamespace(
        guilds=[],
        shard_count=1,
        tree=SimpleNamespace(get_commands=lambda **_kwargs: []),
        commands=[],
        is_closed=lambda: False,
        is_ready=lambda: True,
        latencies=[],
        latency=None,
        get_cog=lambda _name: None,
    )


def test_collection_only_reads_coverage_while_the_switch_is_on(monkeypatch):
    async def probe(_url):
        return True

    async def database(_bot):
        return "mongodb", True

    calls = []

    def snapshot():
        calls.append(True)
        return {"languages": 4, "bot": 50.0, "site": 50.0, "rows": [], "mode": "local", "age_seconds": 0, "scanned_at": 0}

    monkeypatch.setattr(panel, "_probe_http", probe)
    monkeypatch.setattr(panel, "_check_database", database)
    monkeypatch.setattr(panel, "_load_bot_stats_file", lambda: {})
    monkeypatch.setattr(panel, "_translation_snapshot", snapshot)
    monkeypatch.setenv("PUBLIC_URL", "https://public.example")

    monkeypatch.setitem(panel_settings._read(), "status_panel_translation_card", False)
    off = asyncio.run(panel._collect_status(_status_bot()))
    assert off["translations"] is None
    assert calls == []

    monkeypatch.setitem(panel_settings._read(), "status_panel_translation_card", True)
    on = asyncio.run(panel._collect_status(_status_bot()))
    assert on["translations"]["languages"] == 4
    assert calls == [True]


def test_the_panel_draws_the_card_between_the_health_block_and_the_footer():
    source = (ROOT / "src/cogs/staff/panels/status.py").read_text(encoding="utf-8")

    assert 'translations = status.get("translations")' in source
    assert '"### Translation Coverage"' in source
    assert 'view.add_item(discord.ui.Container(*contents, accent_colour=0x2E3440))' in source
    # The heading is drawn only for an owner who switched the card on.
    assert source.index("Translation Coverage") > source.index("if translations:")


def test_the_switch_is_reachable_from_the_locale_page():
    routes = (ROOT / "src/webapp/routes/owner_routes.py").read_text(encoding="utf-8")
    view = (ROOT / "web/src/components/staff/LocaleSyncView.tsx").read_text(encoding="utf-8")

    assert '@app.route("/api/owner/locales/panel", methods=["POST"])' in routes
    assert '"status_panel": {"translation_card": panel_settings.show_translation_card()}' in routes
    assert 'role="switch"' in view
    assert "setOwnerLocaleTranslationCard" in view
