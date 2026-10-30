"""Bot-wide analytics: counters, language census, and the staff endpoint.

The staff tab is only useful if its numbers are real: these checks keep the
counters aggregate-per-day, keep a flush/restart from losing or doubling them,
and keep the endpoint staff-only with the shapes the dashboard expects.
"""

import asyncio
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import aiosqlite

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import database  # noqa: E402
import utils.analytics as analytics  # noqa: E402
from database import MongoPool, SQLitePool  # noqa: E402
from webapp import app, auth, runtime  # noqa: E402
from webapp.routes import staff_analytics_routes as routes  # noqa: E402


async def _memory_pool():
    # aiosqlite's connect() is awaitable rather than a coroutine.
    return SQLitePool(await aiosqlite.connect(":memory:"))


def _reset(monkeypatch, tmp_path):
    """Forget every layer of counter state, as on a fresh process."""
    monkeypatch.setattr(analytics, "_state", None)
    monkeypatch.setattr(analytics, "_active_guilds", {})
    monkeypatch.setattr(analytics, "_dirty", {})
    monkeypatch.setattr(analytics, "_ready", False)
    # No legacy file: the counters must come from the database.
    monkeypatch.setattr(analytics, "LEGACY_PATH", str(tmp_path / "absent.json"))


def _fresh(monkeypatch, tmp_path):
    """Point the counters at a throwaway database and clear every layer of state."""
    pool = asyncio.run(_memory_pool())
    monkeypatch.setattr(database, "_shared_pool", pool)
    _reset(monkeypatch, tmp_path)
    assert asyncio.run(analytics.prepare(pool)) is True
    routes._ECONOMY_CACHE.update({"at": 0.0, "value": None})
    return pool


class _Cursor:
    def __init__(self, rows):
        self.rows = rows

    async def to_list(self, length=None):
        return list(self.rows)


class _MongoCollection:
    """Just enough of a motor collection for the analytics row queries."""

    def __init__(self):
        self.docs: dict = {}

    @staticmethod
    def _matches(doc, filter_dict):
        for key, expected in filter_dict.items():
            value = doc.get(key)
            if isinstance(expected, dict):
                if "$lt" in expected and not (value is not None and str(value) < str(expected["$lt"])):
                    return False
                if "$gte" in expected and not (value is not None and str(value) >= str(expected["$gte"])):
                    return False
                if "$ne" in expected and value == expected["$ne"]:
                    return False
            elif value != expected:
                return False
        return True

    def find(self, filter_dict, projection=None):
        return _Cursor([dict(doc) for doc in self.docs.values() if self._matches(doc, filter_dict)])

    async def replace_one(self, filter_dict, document, upsert=False):
        self.docs[filter_dict["_id"]] = dict(document)

    async def delete_many(self, filter_dict):
        for key in [k for k, doc in self.docs.items() if self._matches(doc, filter_dict)]:
            self.docs.pop(key, None)


class _MongoDatabase(dict):
    def __getitem__(self, name):
        return self.setdefault(name, _MongoCollection())


class _MongoClient:
    def __init__(self):
        self.database = _MongoDatabase()

    def __getitem__(self, name):
        return self.database


def _guild(locale, members):
    return SimpleNamespace(preferred_locale=locale, member_count=members)


def test_commands_aggregate_per_day_kind_and_language(monkeypatch, tmp_path):
    _fresh(monkeypatch, tmp_path)
    analytics.record_command("help", "slash", "de", guild_id=1)
    analytics.record_command("help", "prefix", "de-DE", guild_id=2)
    analytics.record_command("play", "context", "en-US", guild_id=2)

    snapshot = analytics.snapshot(7)
    bucket = snapshot["days"][analytics.current_day()]

    assert bucket["total"] == 3
    assert bucket["commands"] == {"help": 2, "play": 1}
    assert bucket["kinds"] == {"slash": 1, "prefix": 1, "context": 1}
    # Locales collapse to their base language, so en-GB and en-US share a row.
    assert bucket["languages"] == {"de": 2, "en": 1}
    # Two distinct guilds, not three invocations.
    assert bucket["guilds"] == 2
    assert snapshot["lifetime"]["total"] == 3


def test_a_flush_survives_a_restart_without_double_counting(monkeypatch, tmp_path):
    _fresh(monkeypatch, tmp_path)
    analytics.record_command("daily", "slash", "es", guild_id=5)
    analytics.record_command("daily", "slash", "es", guild_id=5)
    assert asyncio.run(analytics.flush()) is True

    # Simulate a process restart: nothing in memory, everything from the database.
    monkeypatch.setattr(analytics, "_state", None)
    monkeypatch.setattr(analytics, "_active_guilds", {})
    monkeypatch.setattr(analytics, "_ready", False)
    assert asyncio.run(analytics.prepare()) is True
    restored = analytics.snapshot(7)

    assert restored["lifetime"]["total"] == 2
    assert restored["days"][analytics.current_day()]["commands"] == {"daily": 2}
    assert restored["days"][analytics.current_day()]["guilds"] == 1


def test_the_counters_persist_through_a_mongodb_pool(monkeypatch, tmp_path):
    # Production runs on MongoDB, where the same rows have to survive a restart.
    collection = _MongoCollection()
    client = _MongoClient()
    client.database["bot_analytics"] = collection
    pool = MongoPool(client, "test")
    monkeypatch.setattr(database, "_shared_pool", pool)
    _reset(monkeypatch, tmp_path)
    assert asyncio.run(analytics.prepare(pool)) is True

    analytics.record_command("help", "slash", "fr", guild_id=9)
    analytics.record_scale(80, 12000)
    assert asyncio.run(analytics.flush()) is True

    today = analytics.current_day()
    stored = {
        (doc["scope"], doc["bucket"], doc["name"]): int(doc["count"])
        for doc in collection.docs.values()
    }
    assert stored[(today, "command", "help")] == 1
    assert stored[(today, "scale", "users")] == 12000
    assert stored[("lifetime", "total", "all")] == 1

    # A restart reloads the same rows instead of starting from zero.
    monkeypatch.setattr(analytics, "_state", None)
    monkeypatch.setattr(analytics, "_ready", False)
    assert asyncio.run(analytics.prepare(pool)) is True
    restored = analytics.snapshot(7)
    assert restored["days"][today]["commands"] == {"help": 1}
    assert restored["lifetime"]["total"] == 1
    assert restored["scale"][today] == {"guilds": 80, "users": 12000}


def test_the_counters_are_rows_in_the_database_not_a_json_file(monkeypatch, tmp_path):
    # Production has no persistent disk, so a file-backed store would reset the
    # charts on every restart.
    pool = _fresh(monkeypatch, tmp_path)
    analytics.record_command("help", "slash", "de", guild_id=1)
    analytics.record_command("help", "prefix", "de", guild_id=1)
    analytics.record_scale(120, 45000)
    assert asyncio.run(analytics.flush()) is True

    rows = asyncio.run(pool.fetch(
        "SELECT scope, bucket, name, count FROM bot_analytics WHERE scope = $1",
        analytics.current_day(),
    ))
    stored = {(row["bucket"], row["name"]): int(row["count"]) for row in rows}
    assert stored[("total", "all")] == 2
    assert stored[("command", "help")] == 2
    assert stored[("kind", "prefix")] == 1
    assert stored[("language", "de")] == 2
    assert stored[("guilds", "active")] == 1
    assert stored[("scale", "users")] == 45000
    assert not list(tmp_path.glob("*.json"))


def test_the_language_census_ranks_guilds_and_marks_supported_locales(monkeypatch, tmp_path):
    _fresh(monkeypatch, tmp_path)
    census = analytics.language_census([
        _guild("de", 40),
        _guild("en-US", 200),
        _guild("en-GB", 60),
        _guild("fr", 30),
        _guild("ja", 10),
    ])

    assert census["guilds"] == 5
    assert census["members"] == 340
    assert [row["code"] for row in census["languages"]] == ["en", "de", "fr", "ja"]
    english = census["languages"][0]
    assert english["guilds"] == 2
    assert english["members"] == 260
    assert english["share"] == 0.4
    assert english["supported"] is True
    # French ships, Japanese does not, and the census says which is worth a
    # translation rollout.
    assert census["languages"][2]["supported"] is True
    assert census["languages"][3]["supported"] is False


def test_the_endpoint_is_staff_only(monkeypatch, tmp_path):
    _fresh(monkeypatch, tmp_path)
    monkeypatch.setattr(auth, "_current_user_blacklist_entry", lambda: None)
    monkeypatch.setattr(routes, "_current_staff_role", lambda: None)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user"] = {"id": "10", "username": "someone"}
            session["access_token"] = "token"
            session["token_exp"] = time.time() + 3600
        response = client.get("/api/staff/analytics")

    assert response.status_code == 403
    assert "restricted" in response.get_json()["error"]


def test_the_endpoint_returns_live_charts_for_staff(monkeypatch, tmp_path):
    _fresh(monkeypatch, tmp_path)
    bot = SimpleNamespace(
        guilds=[_guild("de", 40), _guild("en-US", 200), _guild("es-ES", 60)],
        latency=0.042,
        shards={},
        start_time=time.time() - 3600,
        is_ready=lambda: True,
    )
    monkeypatch.setattr(routes, "_discord_bot", bot)
    monkeypatch.setattr(runtime, "_discord_bot", bot)
    monkeypatch.setattr(auth, "_current_user_blacklist_entry", lambda: None)
    monkeypatch.setattr(routes, "_current_staff_role", lambda: "head_admin")
    monkeypatch.setattr(routes, "_command_categories", lambda: {"help": "utility", "play": "music"})
    monkeypatch.setattr(routes, "get_runtime_economy_rows", lambda: [
        {"user_id": "1", "balance": 100, "bank": 50, "net_worth": 150, "level": 4, "job": "barista", "daily_streak": 2},
        {"user_id": "2", "balance": 300, "bank": 0, "net_worth": 300, "level": 6, "job": "baker", "daily_streak": 0},
        {"user_id": "3", "balance": 0, "bank": 0, "net_worth": 0, "level": 0, "job": "baker", "daily_streak": 0},
    ])
    analytics.record_command("help", "slash", "de", guild_id=1)
    analytics.record_command("help", "prefix", "en", guild_id=2)
    analytics.record_command("play", "context", "es", guild_id=3)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user"] = {"id": "11", "username": "staff"}
            session["access_token"] = "token"
            session["token_exp"] = time.time() + 3600
        response = client.get("/api/staff/analytics?days=14")

    assert response.status_code == 200
    payload = response.get_json()

    assert payload["bot"]["guilds"] == 3
    assert payload["bot"]["members"] == 300
    assert payload["bot"]["latency_ms"] == 42

    usage = payload["usage"]
    # The chart window is zero-filled, so a quiet day still has a point.
    assert len(usage["days"]) == 14
    assert usage["days"][-1]["total"] == 3
    assert usage["totals"]["today"] == 3
    assert usage["by_kind"] == {"slash": 1, "prefix": 1, "context": 1}
    assert [row["name"] for row in usage["top_commands"]] == ["help", "play"]
    assert usage["top_commands"][0]["count"] == 2
    assert usage["top_commands"][0]["category"] == "utility"
    assert usage["top_commands"][1]["category"] == "music"

    assert [row["code"] for row in payload["languages"]["languages"]] == ["en", "es", "de"]
    assert payload["languages"]["languages"][0]["supported"] is True

    economy = payload["economy"]
    assert economy["profiles"] == 3
    assert economy["circulating"] == 400
    assert economy["banked"] == 50
    assert economy["average"] == 150
    assert economy["median"] == 150
    assert economy["top_jobs"][0] == {
        "id": "baker", "name": "Baker", "emoji": "🍞", "count": 2, "share": 0.6667,
    }

    # Today's live totals seed the growth series the tab draws.
    assert payload["growth"][-1]["guilds"] == 3
    assert payload["growth"][-1]["users"] == 300
