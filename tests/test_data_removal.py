"""Account and server deletion must never erase moderation records.

The public request form is a privacy tool, not a ban reset. These tests run the
real SQL in utils.data_removal against SQLite: account data disappears, server
configuration disappears, and warns, blacklists, giveaway bans, and abuse
records survive. They also pin the ownership record used after Niko is removed.
"""

import asyncio
import functools
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import utils.data_removal as removal  # noqa: E402
from webapp import app  # noqa: E402
from webapp.routes import privacy_routes as routes  # noqa: E402


class SqlitePool:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(
            """
            CREATE TABLE economy_users (user_id INTEGER PRIMARY KEY, balance INTEGER);
            CREATE TABLE levels (guild_id INTEGER, user_id INTEGER, xp INTEGER);
            CREATE TABLE afk_users (user_id INTEGER PRIMARY KEY, reason TEXT);
            CREATE TABLE donors (user_id INTEGER PRIMARY KEY, total_donated REAL);
            CREATE TABLE premium_users (user_id INTEGER PRIMARY KEY);
            CREATE TABLE roleplay_blocks (blocker_id INTEGER, blocked_id INTEGER);
            CREATE TABLE roleplay_actions (message_id INTEGER PRIMARY KEY, actor_id INTEGER, target_id INTEGER);
            CREATE TABLE poll_votes (message_id INTEGER, user_id INTEGER);
            CREATE TABLE participants (message_id INTEGER, user_id INTEGER);
            CREATE TABLE uwulock_config (guild_id INTEGER, channel_id INTEGER, user_id INTEGER);
            CREATE TABLE voicemaster_channels (channel_id INTEGER PRIMARY KEY, owner_id INTEGER, guild_id INTEGER);
            CREATE TABLE staff_application_submissions (application_id TEXT, user_id TEXT);
            CREATE TABLE staff_team_submissions (opening_id TEXT, user_id TEXT);
            CREATE TABLE suggestions (message_id INTEGER PRIMARY KEY, guild_id INTEGER, author_id INTEGER, voters TEXT);
            CREATE TABLE giveaways (message_id INTEGER PRIMARY KEY, guild_id INTEGER, host_id INTEGER);
            CREATE TABLE sticky_messages (channel_id INTEGER PRIMARY KEY, guild_id INTEGER, created_by INTEGER);
            CREATE TABLE premium_subscriptions (guild_id INTEGER PRIMARY KEY, gifted_by INTEGER, gifted_by_name TEXT);
            CREATE TABLE warns (id INTEGER PRIMARY KEY, guild_id INTEGER, user_id INTEGER, reason TEXT);
            CREATE TABLE mutes (id INTEGER PRIMARY KEY, guild_id INTEGER, user_id INTEGER);
            CREATE TABLE blacklist_users (id INTEGER PRIMARY KEY, reason TEXT);
            CREATE TABLE blacklist_guilds (id INTEGER PRIMARY KEY, reason TEXT);
            CREATE TABLE blacklist_appeals (appeal_id TEXT PRIMARY KEY, user_id INTEGER);
            CREATE TABLE giveaway_bans (guild_id INTEGER, user_id INTEGER);
            CREATE TABLE abuse_strikes (user_id INTEGER PRIMARY KEY, strikes INTEGER);
            CREATE TABLE mrbeast_scams (image_hash TEXT PRIMARY KEY);
            CREATE TABLE mrbeast_scam_reports (report_id TEXT PRIMARY KEY, guild_id INTEGER);
            CREATE TABLE transcripts (transcript_id TEXT PRIMARY KEY, guild_id INTEGER, opener_id INTEGER);
            CREATE TABLE guild_feature_locks (guild_id INTEGER, feature TEXT);
            CREATE TABLE guild_ownership (
                guild_id INTEGER PRIMARY KEY,
                owner_id INTEGER NOT NULL,
                guild_name TEXT,
                icon_url TEXT,
                first_seen_at REAL NOT NULL,
                last_checked_at REAL NOT NULL,
                removed_at REAL
            );
            CREATE TABLE ai_config (guild_id INTEGER PRIMARY KEY, personality TEXT);
            CREATE TABLE logging_config (guild_id INTEGER PRIMARY KEY, data TEXT);
            CREATE TABLE logging_webhooks (guild_id INTEGER, channel_id INTEGER, token TEXT);
            CREATE TABLE moderation_config (guild_id INTEGER PRIMARY KEY, data TEXT);
            CREATE TABLE ticket_config (guild_id INTEGER PRIMARY KEY, panel_title TEXT);
            CREATE TABLE starboard_config (guild_id INTEGER PRIMARY KEY, threshold INTEGER);
            CREATE TABLE birthday_guilds (guild_id INTEGER PRIMARY KEY, channel_id INTEGER);
            CREATE TABLE server_activity (guild_id INTEGER, activity_date TEXT);
            CREATE TABLE polls (message_id INTEGER PRIMARY KEY, guild_id INTEGER);
            CREATE TABLE staff_applications (id TEXT PRIMARY KEY, guild_id INTEGER);
            CREATE TABLE data_removal_requests (
                request_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                scope TEXT NOT NULL,
                guild_id INTEGER,
                guild_name TEXT,
                reason TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending',
                ownership_note TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                reviewed_by INTEGER,
                reviewed_at REAL,
                review_note TEXT,
                completed_at REAL,
                result TEXT
            );
            """
        )

    @staticmethod
    def _convert(query):
        return re.sub(r"\$\d+", "?", query)

    async def execute(self, query, *args):
        self.conn.execute(self._convert(query), args)
        self.conn.commit()

    async def fetch(self, query, *args):
        return [dict(row) for row in self.conn.execute(self._convert(query), args).fetchall()]

    async def fetchrow(self, query, *args):
        row = self.conn.execute(self._convert(query), args).fetchone()
        return dict(row) if row else None

    async def fetchval(self, query, *args):
        row = self.conn.execute(self._convert(query), args).fetchone()
        return row[0] if row else None


def async_test(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return asyncio.run(fn(*args, **kwargs))
    return wrapper


async def _no_music(_user_id, _errors):
    return None


def _seed_moderation(conn):
    conn.execute("INSERT INTO warns VALUES (1, 10, 99, 'spam')")
    conn.execute("INSERT INTO mutes VALUES (1, 10, 99)")
    conn.execute("INSERT INTO blacklist_users VALUES (99, 'ban evasion')")
    conn.execute("INSERT INTO blacklist_guilds VALUES (10, 'raid')")
    conn.execute("INSERT INTO blacklist_appeals VALUES ('a1', 99)")
    conn.execute("INSERT INTO giveaway_bans VALUES (10, 99)")
    conn.execute("INSERT INTO abuse_strikes VALUES (99, 2)")
    conn.execute("INSERT INTO mrbeast_scams VALUES ('hash')")
    conn.execute("INSERT INTO mrbeast_scam_reports VALUES ('r1', 10)")
    conn.execute("INSERT INTO transcripts VALUES ('t1', 10, 99)")
    conn.execute("INSERT INTO guild_feature_locks VALUES (10, 'polls')")
    conn.commit()


@async_test
async def test_account_deletion_removes_personal_data_and_keeps_moderation(monkeypatch):
    monkeypatch.setattr(removal, "_delete_music_data", _no_music)
    pool = SqlitePool()
    pool.conn.executescript(
        """
        INSERT INTO economy_users VALUES (99, 500);
        INSERT INTO levels VALUES (10, 99, 40);
        INSERT INTO afk_users VALUES (99, 'away');
        INSERT INTO donors VALUES (99, 25);
        INSERT INTO premium_users VALUES (99);
        INSERT INTO roleplay_blocks VALUES (99, 98);
        INSERT INTO roleplay_actions VALUES (1, 99, 98), (2, 98, 99);
        INSERT INTO poll_votes VALUES (5, 99);
        INSERT INTO participants VALUES (6, 99);
        INSERT INTO uwulock_config VALUES (10, 20, 99);
        INSERT INTO voicemaster_channels VALUES (30, 99, 10);
        INSERT INTO staff_application_submissions VALUES ('app', '99');
        INSERT INTO staff_team_submissions VALUES ('open', '99');
        INSERT INTO suggestions VALUES (7, 10, 99, '{"99": 1, "98": -1}');
        INSERT INTO giveaways VALUES (8, 10, 99);
        INSERT INTO sticky_messages VALUES (40, 10, 99);
        INSERT INTO premium_subscriptions VALUES (10, 99, 'Someone');
        """
    )
    _seed_moderation(pool.conn)

    result = await removal.execute_account_deletion(pool, 99)

    assert pool.conn.execute("SELECT COUNT(*) FROM economy_users").fetchone()[0] == 0
    assert pool.conn.execute("SELECT COUNT(*) FROM levels").fetchone()[0] == 0
    assert pool.conn.execute("SELECT COUNT(*) FROM roleplay_blocks").fetchone()[0] == 0
    assert pool.conn.execute("SELECT COUNT(*) FROM roleplay_actions").fetchone()[0] == 0
    assert pool.conn.execute("SELECT COUNT(*) FROM participants").fetchone()[0] == 0
    assert pool.conn.execute("SELECT COUNT(*) FROM voicemaster_channels").fetchone()[0] == 0
    assert pool.conn.execute("SELECT COUNT(*) FROM staff_application_submissions").fetchone()[0] == 0
    assert pool.conn.execute("SELECT author_id FROM suggestions").fetchone()[0] == 0
    assert pool.conn.execute("SELECT voters FROM suggestions").fetchone()[0] == '{"98": -1}'
    assert pool.conn.execute("SELECT voters FROM suggestions").fetchone()[0] == '{"98": -1}'
    assert pool.conn.execute("SELECT host_id FROM giveaways").fetchone()[0] == 0
    assert pool.conn.execute("SELECT created_by FROM sticky_messages").fetchone()[0] is None
    gifted = pool.conn.execute("SELECT gifted_by, gifted_by_name FROM premium_subscriptions").fetchone()
    assert tuple(gifted) == (None, None)

    assert pool.conn.execute("SELECT COUNT(*) FROM warns").fetchone()[0] == 1
    assert pool.conn.execute("SELECT COUNT(*) FROM mutes").fetchone()[0] == 1
    assert pool.conn.execute("SELECT COUNT(*) FROM blacklist_users").fetchone()[0] == 1
    assert pool.conn.execute("SELECT COUNT(*) FROM giveaway_bans").fetchone()[0] == 1
    assert pool.conn.execute("SELECT COUNT(*) FROM abuse_strikes").fetchone()[0] == 1
    assert pool.conn.execute("SELECT COUNT(*) FROM mrbeast_scams").fetchone()[0] == 1
    assert pool.conn.execute("SELECT COUNT(*) FROM transcripts").fetchone()[0] == 1
    assert result["scope"] == "account"
    assert "warns" not in result["removed"]
    assert result["errors"] == []


@async_test
async def test_server_deletion_removes_configuration_and_keeps_moderation(monkeypatch):
    monkeypatch.setattr(removal, "_delete_music_data", _no_music)
    pool = SqlitePool()
    pool.conn.executescript(
        """
        INSERT INTO ai_config VALUES (10, 'cafe');
        INSERT INTO logging_config VALUES (10, '{}');
        INSERT INTO logging_webhooks VALUES (10, 20, 'token');
        INSERT INTO moderation_config VALUES (10, '{}');
        INSERT INTO ticket_config VALUES (10, 'Support');
        INSERT INTO starboard_config VALUES (10, 3);
        INSERT INTO birthday_guilds VALUES (10, 20);
        INSERT INTO server_activity VALUES (10, '2026-10-20');
        INSERT INTO staff_applications VALUES ('app', 10);
        INSERT INTO staff_application_submissions VALUES ('app', '42');
        INSERT INTO giveaways VALUES (8, 10, 42);
        INSERT INTO participants VALUES (8, 99);
        INSERT INTO polls VALUES (9, 10);
        INSERT INTO poll_votes VALUES (9, 99);
        INSERT INTO suggestions VALUES (7, 10, 99, '{}');
        INSERT INTO warns VALUES (1, 10, 99, 'spam');
        INSERT INTO mutes VALUES (1, 10, 99);
        INSERT INTO giveaway_bans VALUES (10, 99);
        INSERT INTO blacklist_guilds VALUES (10, 'raid');
        INSERT INTO mrbeast_scams VALUES ('hash');
        INSERT INTO mrbeast_scam_reports VALUES ('r1', 10);
        INSERT INTO transcripts VALUES ('t1', 10, 99);
        INSERT INTO guild_feature_locks VALUES (10, 'polls');
        """
    )

    result = await removal.execute_guild_deletion(pool, 10)

    for table in ("ai_config", "logging_config", "logging_webhooks", "moderation_config",
                  "ticket_config", "starboard_config", "birthday_guilds", "server_activity",
                  "giveaways", "participants", "polls", "poll_votes", "suggestions",
                  "staff_applications", "staff_application_submissions"):
        assert pool.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0, table

    assert pool.conn.execute("SELECT COUNT(*) FROM warns").fetchone()[0] == 1
    assert pool.conn.execute("SELECT COUNT(*) FROM mutes").fetchone()[0] == 1
    assert pool.conn.execute("SELECT COUNT(*) FROM giveaway_bans").fetchone()[0] == 1
    assert pool.conn.execute("SELECT COUNT(*) FROM blacklist_guilds").fetchone()[0] == 1
    assert pool.conn.execute("SELECT COUNT(*) FROM mrbeast_scams").fetchone()[0] == 1
    assert pool.conn.execute("SELECT COUNT(*) FROM transcripts").fetchone()[0] == 1
    assert pool.conn.execute("SELECT COUNT(*) FROM guild_feature_locks").fetchone()[0] == 1
    assert result["scope"] == "server"
    assert "warns" not in result["removed"]
    assert result["errors"] == []


def test_no_preserved_record_table_is_ever_in_a_deletion_list():
    deleted = {table for table, _column in removal.USER_DELETIONS}
    deleted |= {table for table, _column, _replacement in removal.USER_ANONYMIZATIONS}
    deleted |= set(removal.GUILD_DELETIONS)
    for table in ("warns", "mutes", "blacklist_users", "blacklist_guilds", "blacklist_appeals",
                  "giveaway_bans", "abuse_strikes", "mrbeast_scams", "mrbeast_scam_reports",
                  "transcripts", "guild_feature_locks"):
        assert table not in deleted


def test_the_page_and_api_are_wired_together():
    root = ROOT
    router = (root / "web" / "src" / "router.ts").read_text(encoding="utf-8")
    app = (root / "web" / "src" / "App.tsx").read_text(encoding="utf-8")
    routes = (root / "src" / "webapp" / "routes" / "privacy_routes.py").read_text(encoding="utf-8")
    site = (root / "src" / "webapp" / "routes" / "site_routes.py").read_text(encoding="utf-8")
    page = (root / "web" / "src" / "pages" / "DataRemovalPage.tsx").read_text(encoding="utf-8")

    assert '"/data-removal"' in router
    assert "DataRemovalPage" in app
    assert "/data-removal" in site
    assert 'app.route("/api/privacy/data-removal"' in routes
    assert 'app.route("/api/staff/data-removal"' in routes
    assert "X-CSRF-Token" in page
    assert "No owner-verified servers were found" in page


class FakeGuild:
    def __init__(self, guild_id=10, owner_id=99, name="Test Server"):
        self.id = guild_id
        self.owner_id = owner_id
        self.name = name
        self.icon = None


class FakeBot:
    def __init__(self, pool, guilds):
        self.cxn = pool
        self.guilds = guilds

    def get_guild(self, guild_id):
        return next((guild for guild in self.guilds if guild.id == guild_id), None)


def _run_on_loop(awaitable, timeout=8):
    return asyncio.run(awaitable)


def _client():
    client = app.test_client()
    with client.session_transaction() as flask_session:
        flask_session["user"] = {"id": "99"}
        flask_session["csrf_token"] = "test-token"
    return client


def test_data_removal_routes_verify_ownership_and_allow_withdrawal(monkeypatch):
    pool = SqlitePool()
    bot = FakeBot(pool, [FakeGuild()])
    monkeypatch.setattr(routes, "_discord_bot", bot)
    monkeypatch.setattr(routes, "ensure_access_token", lambda: True)
    monkeypatch.setattr(routes, "run_on_bot_loop", _run_on_loop)

    client = _client()
    overview = client.get("/api/privacy/data-removal")
    assert overview.status_code == 200
    payload = overview.get_json()
    assert payload["servers"] == [{
        "id": "10",
        "name": "Test Server",
        "icon_url": None,
        "bot_present": True,
        "removed_at": None,
        "pending": False,
    }]

    rejected = client.post(
        "/api/privacy/data-removal",
        headers={"X-CSRF-Token": "test-token"},
        json={"scope": "server", "guild_id": "10", "reason": "This is a long enough reason.", "confirmation": "Wrong name"},
    )
    assert rejected.status_code == 400

    accepted = client.post(
        "/api/privacy/data-removal",
        headers={"X-CSRF-Token": "test-token"},
        json={"scope": "server", "guild_id": "10", "reason": "This is a long enough reason.", "confirmation": "Test Server"},
    )
    assert accepted.status_code == 201
    request_id = accepted.get_json()["request"]["id"]

    duplicate = client.post(
        "/api/privacy/data-removal",
        headers={"X-CSRF-Token": "test-token"},
        json={"scope": "server", "guild_id": "10", "reason": "This is a long enough reason.", "confirmation": "Test Server"},
    )
    assert duplicate.status_code == 409

    overview = client.get("/api/privacy/data-removal").get_json()
    assert overview["servers"][0]["pending"] is True

    withdrawn = client.delete(
        f"/api/privacy/data-removal/{request_id}",
        headers={"X-CSRF-Token": "test-token"},
    )
    assert withdrawn.status_code == 200
    assert pool.conn.execute(
        "SELECT status FROM data_removal_requests WHERE request_id = ?", (request_id,)
    ).fetchone()[0] == "withdrawn"


def test_owner_can_approve_a_request_and_moderation_survives(monkeypatch):
    pool = SqlitePool()
    pool.conn.executescript(
        """
        INSERT INTO economy_users VALUES (99, 500);
        INSERT INTO warns VALUES (1, 10, 99, 'spam');
        INSERT INTO giveaway_bans VALUES (10, 99);
        INSERT INTO blacklist_users VALUES (99, 'ban evasion');
        """
    )
    bot = FakeBot(pool, [FakeGuild()])
    monkeypatch.setattr(routes, "_discord_bot", bot)
    monkeypatch.setattr(routes, "ensure_access_token", lambda: True)
    monkeypatch.setattr(routes, "run_on_bot_loop", _run_on_loop)
    monkeypatch.setattr(routes, "_current_staff_role", lambda: "owner")
    monkeypatch.setattr(removal, "_delete_music_data", _no_music)

    client = _client()
    created = client.post(
        "/api/privacy/data-removal",
        headers={"X-CSRF-Token": "test-token"},
        json={"scope": "account", "reason": "I would like my personal data removed.", "confirmation": "DELETE MY DATA"},
    )
    assert created.status_code == 201
    request_id = created.get_json()["request"]["id"]

    reviewed = client.post(
        f"/api/staff/data-removal/{request_id}/review",
        headers={"X-CSRF-Token": "test-token"},
        json={"status": "approved", "note": "Verified account ownership."},
    )
    assert reviewed.status_code == 200, reviewed.get_json()
    assert reviewed.get_json()["status"] == "completed"
    assert pool.conn.execute("SELECT COUNT(*) FROM economy_users").fetchone()[0] == 0
    assert pool.conn.execute("SELECT COUNT(*) FROM warns").fetchone()[0] == 1
    assert pool.conn.execute("SELECT COUNT(*) FROM giveaway_bans").fetchone()[0] == 1
    assert pool.conn.execute("SELECT COUNT(*) FROM blacklist_users").fetchone()[0] == 1
    row = pool.conn.execute(
        "SELECT status, result FROM data_removal_requests WHERE request_id = ?", (request_id,)
    ).fetchone()
    assert row[0] == "completed"
    assert "preserved" in row[1]


@async_test
async def test_ownership_is_recorded_then_marked_removed():
    pool = SqlitePool()

    await removal.record_ownership(pool, 10, 99, "Server", None)
    row = pool.conn.execute("SELECT owner_id, removed_at FROM guild_ownership WHERE guild_id = 10").fetchone()
    assert row[0] == 99
    assert row[1] is None

    await removal.record_ownership(pool, 10, 42, "Renamed", None)
    row = pool.conn.execute("SELECT owner_id, guild_name FROM guild_ownership WHERE guild_id = 10").fetchone()
    assert tuple(row) == (42, "Renamed")

    await removal.record_ownership(pool, 10, 42, "Renamed", None, removed=True)
    assert pool.conn.execute("SELECT removed_at FROM guild_ownership WHERE guild_id = 10").fetchone()[0] is not None
