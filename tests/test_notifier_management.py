"""Regression tests for social-notifier management.

Covers the three pieces the dashboard's notifications tab depends on:

* ``utils.social.follows`` — the shared store both the cog and the web routes
  use, including the column migration for databases created before the
  management features existed,
* ``webapp.notifier_routes`` — the JSON API behind the dashboard tab,
* ``Notifier.poll_once`` — one poll cycle: per-account fetch deduplication,
  silent seeding of a brand-new follow, and auto-pausing an account that keeps
  failing instead of hammering a platform that no longer answers.
"""

import asyncio
import sqlite3
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app
from webapp import notifier_routes as routes
from webapp import server as server_routes

from cogs.notifier import cog as notifier
import database
from database import _convert_query, _make_row, _serialize_args
from events.startup.database import _migrate_follows
from utils.blacklist_manager import BlacklistManager
from utils.social import follows

GUILD = 555
OTHER_GUILD = 777

#: The ``follows`` table exactly as it existed before notify management.
LEGACY_FOLLOWS_DDL = """
    CREATE TABLE follows (
        guild_id     INTEGER,
        platform     TEXT,
        username     TEXT,
        channel_id   INTEGER,
        template     TEXT,
        last_post_id TEXT,
        PRIMARY KEY  (guild_id, platform, username)
    )
"""

NOTIFIER_CONFIG_DDL = """
    CREATE TABLE notifier_config (
        guild_id           INTEGER PRIMARY KEY,
        enabled            INTEGER NOT NULL DEFAULT 1,
        default_channel_id INTEGER,
        ping_role_id       INTEGER,
        updated_at         TEXT NOT NULL DEFAULT (datetime('now'))
    )
"""

#: The blacklist tables, so the real manager can run against the notifier store.
BLACKLIST_DDL = (
    """
    CREATE TABLE blacklist_guilds (
        id        INTEGER PRIMARY KEY,
        reason    TEXT,
        timestamp REAL,
        added_by  INTEGER,
        status    TEXT,
        appeal_id TEXT
    )
    """,
    """
    CREATE TABLE blacklist_users (
        id         INTEGER PRIMARY KEY,
        reason     TEXT,
        timestamp  REAL,
        added_by   INTEGER,
        expires_at REAL,
        status     TEXT,
        appeal_id  TEXT
    )
    """,
)


class LocalPool:
    """The bot's async pool API over a plain in-process sqlite3 connection.

    ``database.SQLitePool`` trades on an aiosqlite worker thread bound to a
    single event loop, which a Flask test client (several short-lived loops)
    cannot share. This keeps the same SQL surface — including the ``$1``
    placeholder numbering the bot writes — without the loop affinity.
    """

    db_type = "sqlite"

    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        for statement in (LEGACY_FOLLOWS_DDL, NOTIFIER_CONFIG_DDL):
            self.db.execute(statement)
        self.db.commit()

    async def execute(self, query, *args):
        self.db.execute(_convert_query(query), _serialize_args(list(args)))
        self.db.commit()

    async def fetch(self, query, *args):
        cursor = self.db.execute(_convert_query(query), _serialize_args(list(args)))
        return [_make_row(cursor, row) for row in cursor.fetchall()]

    async def fetchrow(self, query, *args):
        cursor = self.db.execute(_convert_query(query), _serialize_args(list(args)))
        return _make_row(cursor, cursor.fetchone())

    async def fetchval(self, query, *args):
        cursor = self.db.execute(_convert_query(query), _serialize_args(list(args)))
        row = cursor.fetchone()
        return None if row is None else row[0]


class BlacklistPool(LocalPool):
    """The notifier store plus the blacklist tables the real manager writes."""

    def __init__(self):
        super().__init__()
        for statement in BLACKLIST_DDL:
            self.db.execute(statement)
        self.db.commit()


def legacy_pool() -> LocalPool:
    """A store as it exists before the management columns were added."""
    return LocalPool()


def migrated_pool() -> LocalPool:
    """A store after the startup migration, as production runs it."""
    pool = LocalPool()
    asyncio.run(_migrate_follows(SimpleNamespace(cxn=pool)))
    return pool


def follow(pool, platform="twitch", username="shroud", channel_id=10, **fields):
    """Insert a follow for test setup and return the stored row."""
    return asyncio.run(
        follows.create_follow(
            pool,
            guild_id=fields.pop("guild_id", GUILD),
            platform=platform,
            username=username,
            channel_id=channel_id,
            **fields,
        )
    )


class FollowsMigrationTests(unittest.TestCase):
    def test_legacy_table_gains_management_columns(self):
        pool = legacy_pool()
        asyncio.run(
            pool.execute(
                "INSERT INTO follows (guild_id, platform, username, channel_id, template, last_post_id) "
                "VALUES ($1, $2, $3, $4, $5, $6)",
                GUILD,
                "twitch",
                "shroud",
                123,
                "",
                "stream:1",
            )
        )
        asyncio.run(_migrate_follows(SimpleNamespace(cxn=pool)))

        rows = asyncio.run(follows.list_follows(pool, GUILD))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        # A row created before the migration stays active with a clean record.
        self.assertTrue(row["enabled"])
        self.assertEqual(row["failures"], 0)
        self.assertIsNone(row["last_checked_at"])
        self.assertEqual(row["channel_id"], "123")
        self.assertEqual(row["display"], "@shroud")

    def test_migration_is_idempotent(self):
        pool = migrated_pool()
        asyncio.run(_migrate_follows(SimpleNamespace(cxn=pool)))
        self.assertEqual(asyncio.run(follows.list_follows(pool)), [])


class FollowsStoreTests(unittest.TestCase):
    def test_create_read_update_delete_round_trip(self):
        pool = migrated_pool()
        created = follow(
            pool,
            last_post_id="stream:1",
            template="Go watch {account}",
            ping_role_id=456,
        )
        updated = asyncio.run(
            follows.update_follow(
                pool,
                guild_id=GUILD,
                platform="twitch",
                username="shroud",
                channel_id=789,
                enabled=False,
            )
        )
        removed = asyncio.run(
            follows.delete_follow(pool, guild_id=GUILD, platform="twitch", username="shroud")
        )
        missing = asyncio.run(
            follows.delete_follow(pool, guild_id=GUILD, platform="twitch", username="shroud")
        )

        self.assertEqual(created["channel_id"], "10")
        self.assertEqual(created["ping_role_id"], "456")
        self.assertEqual(created["template"], "Go watch {account}")
        self.assertTrue(created["enabled"])
        self.assertEqual(updated["channel_id"], "789")
        self.assertFalse(updated["enabled"])
        # A partial edit never clears the fields it does not mention.
        self.assertEqual(updated["template"], "Go watch {account}")
        self.assertIs(removed, True)
        self.assertIs(missing, False)
        self.assertEqual(asyncio.run(follows.list_follows(pool)), [])

    def test_partial_edit_can_clear_a_ping_role(self):
        pool = migrated_pool()
        follow(pool, platform="reddit", username="programming", ping_role_id=456)
        updated = asyncio.run(
            follows.update_follow(
                pool,
                guild_id=GUILD,
                platform="reddit",
                username="programming",
                ping_role_id=None,
            )
        )
        self.assertIsNone(updated["ping_role_id"])

    def test_templates_are_validated_before_they_are_stored(self):
        pool = migrated_pool()
        for template in ("hi {nope}", "x" * (follows.MAX_TEMPLATE_LENGTH + 1)):
            with self.subTest(template=template[:20]):
                with self.assertRaises(follows.FollowError):
                    follow(pool, template=template)
        self.assertEqual(asyncio.run(follows.list_follows(pool)), [])

    def test_rename_follow_repoints_stale_youtube_names(self):
        pool = migrated_pool()
        follow(pool, platform="youtube", username="Home|UC123", channel_id=1)
        renamed = asyncio.run(
            follows.rename_follow(
                pool,
                guild_id=GUILD,
                platform="youtube",
                username="Home|UC123",
                new_username="Real Name|UC123",
            )
        )
        # A rename onto an account already followed is refused.
        follow(pool, platform="youtube", username="Other|UC999", channel_id=1)
        refused = asyncio.run(
            follows.rename_follow(
                pool,
                guild_id=GUILD,
                platform="youtube",
                username="Other|UC999",
                new_username="Real Name|UC123",
            )
        )
        stored = [row["username"] for row in asyncio.run(follows.list_follows(pool, GUILD))]

        self.assertTrue(renamed)
        self.assertFalse(refused)
        self.assertIn("Real Name|UC123", stored)
        self.assertNotIn("Home|UC123", stored)

    def test_platform_counts_and_check_records(self):
        pool = migrated_pool()
        follow(pool, username="a", channel_id=1)
        follow(pool, username="b", channel_id=1)
        follow(pool, platform="bluesky", username="c.bsky.social", channel_id=1)
        asyncio.run(
            follows.record_check(
                pool,
                guild_id=GUILD,
                platform="twitch",
                username="a",
                failures=3,
                last_checked_at="2026-10-16 12:00:00",
            )
        )

        self.assertEqual(
            asyncio.run(follows.platform_counts(pool, GUILD)), {"twitch": 2, "bluesky": 1}
        )
        checked = asyncio.run(follows.get_follow(pool, GUILD, "twitch", "a"))
        self.assertEqual(checked["failures"], 3)
        self.assertEqual(checked["last_checked_at"], "2026-10-16 12:00:00")

    def test_server_config_defaults_and_partial_updates(self):
        pool = migrated_pool()
        defaults = asyncio.run(follows.get_notifier_config(pool, GUILD))
        enabled = asyncio.run(follows.save_notifier_config(pool, GUILD, enabled=False))
        channel = asyncio.run(follows.save_notifier_config(pool, GUILD, default_channel_id=999))
        cleared = asyncio.run(follows.save_notifier_config(pool, GUILD, default_channel_id=""))

        self.assertEqual(defaults, dict(follows.DEFAULT_NOTIFIER_CONFIG))
        self.assertFalse(enabled["enabled"])
        # Saving a channel leaves the switch and the role alone.
        self.assertFalse(channel["enabled"])
        self.assertEqual(channel["default_channel_id"], "999")
        self.assertIsNone(cleared["default_channel_id"])


class FollowFormattingTests(unittest.TestCase):
    def test_detect_platform_reads_links_and_handles(self):
        cases = {
            "https://www.youtube.com/@MrBeast": "youtube",
            "youtu.be/abc": "youtube",
            "https://www.twitch.tv/Shroud?x=1": "twitch",
            "https://twitter.com/jack": "twitter",
            "x.com/jack": "twitter",
            "tiktok.com/@user": "tiktok",
            "bsky.app/profile/bsky.app": "bluesky",
            "someone.bsky.social": "bluesky",
            "https://www.reddit.com/r/programming/": "reddit",
            "r/programming": "reddit",
            "notyoutube.com/@nope": None,
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(follows.detect_platform(value), expected)

    def test_ambiguous_handles_are_left_for_the_user_to_pick(self):
        for value in ("@handle", "shroud", ""):
            with self.subTest(value=value):
                self.assertIsNone(follows.detect_platform(value))

    def test_render_template_fills_only_known_placeholders(self):
        rendered = follows.render_template(
            "New {platform} post from {account}: {title} {url}",
            account="@shroud",
            platform="twitch",
            title="Ranked grind",
            url="https://twitch.tv/shroud",
        )
        self.assertEqual(
            rendered,
            "New Twitch post from @shroud: Ranked grind https://twitch.tv/shroud",
        )
        self.assertEqual(follows.render_template("", account="@x", platform="twitch"), "")


class FakeChannel:
    def __init__(self, channel_id, name="announcements"):
        self.id = channel_id
        self.name = name
        self.mention = f"<#{channel_id}>"
        self.sent = []

    async def send(self, *, content=None, view=None, allowed_mentions=None):
        self.sent.append({"content": content, "view": view, "allowed_mentions": allowed_mentions})


class FakeGuild:
    def __init__(self, guild_id, channels=(), roles=()):
        self.id = guild_id
        self._channels = {channel.id: channel for channel in channels}
        self._roles = {role.id: role for role in roles}

    def get_channel(self, channel_id):
        return self._channels.get(int(channel_id))

    def get_role(self, role_id):
        return self._roles.get(int(role_id))


class FakeBot:
    def __init__(self, pool, guilds=()):
        self.cxn = pool
        self._guilds = {guild.id: guild for guild in guilds}

    def get_guild(self, guild_id):
        return self._guilds.get(int(guild_id))


def cog_for(bot):
    """A Notifier instance with no gateway and no inter-message pacing."""
    instance = notifier.Notifier.__new__(notifier.Notifier)
    instance.bot = bot
    instance.send_pacing = 0
    return instance


def view_text(component):
    """Every TextDisplay string in a components-v2 tree."""
    found = []
    content = getattr(component, "content", None)
    if isinstance(content, str):
        found.append(content)
    for child in getattr(component, "children", None) or []:
        found.extend(view_text(child))
    return found


class PollLoopTests(unittest.TestCase):
    def test_one_account_is_fetched_once_for_several_servers(self):
        pool = migrated_pool()
        first, second = FakeChannel(10), FakeChannel(20)
        bot = FakeBot(
            pool,
            [FakeGuild(GUILD, [first]), FakeGuild(OTHER_GUILD, [second])],
        )
        follow(pool, last_post_id="stream:1", channel_id=first.id)
        follow(pool, guild_id=OTHER_GUILD, last_post_id="stream:1", channel_id=second.id)
        calls = []

        async def fake_fetch(platform, username):
            calls.append((platform, username))
            return {"id": "stream:2", "url": "https://twitch.tv/shroud", "title": "Live"}

        with patch.object(notifier, "_fetch", fake_fetch):
            asyncio.run(cog_for(bot).poll_once())

        # One creator followed by two servers costs exactly one request.
        self.assertEqual(calls, [("twitch", "shroud")])
        self.assertEqual(len(first.sent), 1)
        self.assertEqual(len(second.sent), 1)

    def test_first_check_seeds_the_post_id_without_notifying(self):
        pool = migrated_pool()
        channel = FakeChannel(10)
        bot = FakeBot(pool, [FakeGuild(GUILD, [channel])])
        follow(pool, last_post_id=None)

        async def fake_fetch(platform, username):
            return {"id": "stream:9", "url": "https://twitch.tv/shroud", "title": "Live"}

        with patch.object(notifier, "_fetch", fake_fetch):
            asyncio.run(cog_for(bot).poll_once())

        row = asyncio.run(follows.get_follow(pool, GUILD, "twitch", "shroud"))
        self.assertEqual(channel.sent, [])
        self.assertEqual(row["last_post_id"], "stream:9")

    def test_unchanged_post_is_not_re_announced(self):
        pool = migrated_pool()
        channel = FakeChannel(10)
        bot = FakeBot(pool, [FakeGuild(GUILD, [channel])])
        follow(pool, last_post_id="stream:1")

        async def fake_fetch(platform, username):
            return {"id": "stream:1", "url": "https://twitch.tv/shroud", "title": "Live"}

        with patch.object(notifier, "_fetch", fake_fetch):
            asyncio.run(cog_for(bot).poll_once())

        row = asyncio.run(follows.get_follow(pool, GUILD, "twitch", "shroud"))
        self.assertEqual(channel.sent, [])
        self.assertEqual(row["failures"], 0)

    def test_repeated_failures_pause_the_follow_and_explain_once(self):
        pool = migrated_pool()
        channel = FakeChannel(10)
        bot = FakeBot(pool, [FakeGuild(GUILD, [channel])])
        follow(pool, last_post_id="stream:1")

        async def failing_fetch(platform, username):
            return None

        instance = cog_for(bot)
        with patch.object(notifier, "_fetch", failing_fetch):
            for _ in range(notifier.FAILURE_LIMIT):
                asyncio.run(instance.poll_once())

        row = asyncio.run(follows.get_follow(pool, GUILD, "twitch", "shroud"))
        self.assertEqual(row["failures"], notifier.FAILURE_LIMIT)
        self.assertFalse(row["enabled"])
        self.assertIsNotNone(row["last_checked_at"])
        # The pause is announced once, not on every failed check.
        self.assertEqual(len(channel.sent), 1)
        self.assertIn("Paused @shroud", "".join(view_text(channel.sent[0]["view"])))

    def test_paused_follows_and_disabled_servers_are_never_fetched(self):
        pool = migrated_pool()
        channel = FakeChannel(10)
        bot = FakeBot(pool, [FakeGuild(GUILD, [channel])])
        follow(pool, username="paused-one", last_post_id="stream:1", enabled=False)
        follow(pool, username="muted-server", last_post_id="stream:1")
        asyncio.run(follows.save_notifier_config(pool, GUILD, enabled=False))
        calls = []

        async def fake_fetch(platform, username):
            calls.append((platform, username))
            return {"id": "stream:2"}

        with patch.object(notifier, "_fetch", fake_fetch):
            asyncio.run(cog_for(bot).poll_once())

        self.assertEqual(calls, [])
        self.assertEqual(channel.sent, [])

    def test_role_ping_and_template_ride_along_with_the_notification(self):
        pool = migrated_pool()
        channel = FakeChannel(10)
        role = SimpleNamespace(id=900, mention="<@&900>")
        bot = FakeBot(pool, [FakeGuild(GUILD, [channel], [role])])
        follow(
            pool,
            last_post_id="stream:1",
            template="New from {account}: {title}",
            ping_role_id=role.id,
        )

        async def fake_fetch(platform, username):
            return {"id": "stream:2", "url": "https://twitch.tv/shroud", "title": "Ranked"}

        with patch.object(notifier, "_fetch", fake_fetch):
            asyncio.run(cog_for(bot).poll_once())

        self.assertEqual(len(channel.sent), 1)
        sent = channel.sent[0]
        self.assertEqual(sent["content"], "<@&900>\nNew from @shroud: Ranked")
        # Only the configured role may be mentioned, never anything a post says.
        self.assertEqual(sent["allowed_mentions"].roles, [role])
        self.assertIsNotNone(sent["view"])

    def test_missing_channel_keeps_the_old_post_id(self):
        pool = migrated_pool()
        bot = FakeBot(pool, [FakeGuild(GUILD, [])])
        follow(pool, last_post_id="stream:1")

        async def fake_fetch(platform, username):
            return {"id": "stream:2"}

        with patch.object(notifier, "_fetch", fake_fetch):
            asyncio.run(cog_for(bot).poll_once())

        row = asyncio.run(follows.get_follow(pool, GUILD, "twitch", "shroud"))
        self.assertEqual(row["last_post_id"], "stream:1")


class BlacklistedGuildNotifierTests(unittest.TestCase):
    """A blacklisted server must stop posting, not just lose its dashboard."""

    def test_blacklisting_a_guild_switches_its_notifier_off(self):
        pool = BlacklistPool()
        asyncio.run(_migrate_follows(SimpleNamespace(cxn=pool)))
        follow(pool, last_post_id="stream:1")
        asyncio.run(
            follows.save_notifier_config(pool, GUILD, default_channel_id=20, ping_role_id=900)
        )
        previous_pool, previous_instance = database._shared_pool, BlacklistManager._instance
        database._shared_pool = pool
        BlacklistManager._instance = None
        try:
            manager = BlacklistManager()
            self.assertTrue(asyncio.run(manager.add_guild(GUILD, reason="abuse", added_by=1)))
            config = asyncio.run(follows.get_notifier_config(pool, GUILD))
            # The server-wide switch is what pauses every account, and only that
            # switch flips: the saved channel and ping role are kept.
            self.assertFalse(config["enabled"])
            self.assertEqual(config["default_channel_id"], "20")
            self.assertEqual(config["ping_role_id"], "900")
            # The follow rows themselves stay untouched, so lifting the blacklist
            # later only needs the switch turned back on by the server admin.
            rows = asyncio.run(follows.list_follows(pool, GUILD))
            self.assertEqual([row["enabled"] for row in rows], [True])
        finally:
            database._shared_pool = previous_pool
            BlacklistManager._instance = previous_instance

    def test_pausing_leaves_a_server_that_never_used_the_notifier_alone(self):
        pool = BlacklistPool()
        asyncio.run(_migrate_follows(SimpleNamespace(cxn=pool)))

        # No follows means nothing to pause, so no config row is created either.
        self.assertFalse(asyncio.run(follows.pause_guild_notifications(pool, OTHER_GUILD)))
        self.assertEqual(asyncio.run(pool.fetch("SELECT guild_id FROM notifier_config")), [])

        follow(pool, last_post_id="stream:1")
        self.assertTrue(asyncio.run(follows.pause_guild_notifications(pool, GUILD)))
        # Already paused is not a change, so callers can log a real switch-off.
        self.assertFalse(asyncio.run(follows.pause_guild_notifications(pool, GUILD)))

    def test_poll_skips_a_guild_blacklisted_before_the_switch_was_flipped(self):
        pool = migrated_pool()
        channel = FakeChannel(10)
        bot = FakeBot(pool, [FakeGuild(GUILD, [channel])])
        follow(pool, last_post_id="stream:1")
        manager = BlacklistManager()
        previous_loaded, previous_entries = manager._loaded, manager.blacklist["guilds"]
        manager._loaded = True
        manager.blacklist["guilds"] = [
            {
                "id": GUILD,
                "reason": "abuse",
                "timestamp": time.time(),
                "added_by": 1,
                "expires_at": None,
                "status": "active",
            }
        ]
        calls = []

        async def fake_fetch(platform, username):
            calls.append((platform, username))
            return post("stream:2")

        try:
            with patch.object(notifier, "_fetch", fake_fetch):
                asyncio.run(cog_for(bot).poll_once())
        finally:
            manager._loaded = previous_loaded
            manager.blacklist["guilds"] = previous_entries

        self.assertEqual(calls, [])
        self.assertEqual(channel.sent, [])
        row = asyncio.run(follows.get_follow(pool, GUILD, "twitch", "shroud"))
        self.assertEqual(row["last_post_id"], "stream:1")


class UnblacklistedGuildResumesOnlyWhenSwitchedBackOn(unittest.TestCase):
    def test_removing_the_blacklist_does_not_re_enable_announcements(self):
        """Lifting a blacklist must not silently resume posting for a server."""
        pool = BlacklistPool()
        asyncio.run(_migrate_follows(SimpleNamespace(cxn=pool)))
        follow(pool, last_post_id="stream:1")
        asyncio.run(follows.pause_guild_notifications(pool, GUILD))
        previous_pool, previous_instance = database._shared_pool, BlacklistManager._instance
        database._shared_pool = pool
        BlacklistManager._instance = None
        try:
            manager = BlacklistManager()
            self.assertTrue(asyncio.run(manager.add_guild(GUILD, reason="abuse", added_by=1)))
            self.assertTrue(asyncio.run(manager.remove_guild(GUILD)))
            self.assertFalse(asyncio.run(follows.get_notifier_config(pool, GUILD))["enabled"])
        finally:
            database._shared_pool = previous_pool
            BlacklistManager._instance = previous_instance


def run_awaitable(awaitable, timeout=8):
    """Stand-in for ``server.run_on_bot_loop`` without a gateway loop."""
    return asyncio.run(awaitable)


def notifier_client(pool, guild_id=GUILD, *, bot=None, allowed=True, csrf="test-csrf"):
    """A signed-in client with guild access, a store and a fake gateway."""
    client = app.test_client()
    with client.session_transaction() as session:
        session["user"] = {"id": "1", "username": "tester"}
        session["access_token"] = "test-token"
        session["token_exp"] = time.time() + 3600
        session["csrf_token"] = csrf
    fake_bot = bot or SimpleNamespace(cxn=pool, get_guild=lambda guild_number: None)
    manager = SimpleNamespace(
        get_user_entry=lambda user_id: None,
        get_guild_entry=lambda guild_number: None,
    )
    patches = [
        patch.object(routes, "_discord_bot", fake_bot),
        patch.object(routes, "run_on_bot_loop", side_effect=run_awaitable),
        patch.object(routes, "_guild_resource_ids", return_value=({"10", "20"}, {"900"})),
        patch.object(
            server_routes,
            "managed_guild_ids",
            return_value={str(guild_id)} if allowed else set(),
        ),
        patch.object(server_routes, "_load_blacklist_manager", return_value=manager),
    ]
    for active_patch in patches:
        active_patch.start()
    return client, patches


def stop_patches(patches):
    for active_patch in reversed(patches):
        active_patch.stop()


def ok_twitch(query):
    return True, "shroud"


def post(post_id):
    return {"id": post_id, "url": "https://twitch.tv/shroud", "title": "Live"}


class NotifierRouteTests(unittest.TestCase):
    def test_snapshot_lists_follows_config_and_platforms(self):
        pool = migrated_pool()
        follow(pool, last_post_id="stream:1")
        asyncio.run(follows.save_notifier_config(pool, GUILD, default_channel_id=20))
        client, patches = notifier_client(pool)
        try:
            response = client.get(f"/api/guild/{GUILD}/notifier")
        finally:
            stop_patches(patches)

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["config"]["default_channel_id"], "20")
        self.assertEqual([row["username"] for row in payload["follows"]], ["shroud"])
        self.assertNotIn("guild_id", payload["follows"][0])
        self.assertIn("twitch", [platform["id"] for platform in payload["platforms"]])
        self.assertEqual(payload["limits"]["max_follows"], follows.MAX_FOLLOWS_PER_GUILD)
        self.assertIn("account", payload["limits"]["template_placeholders"])

    def test_snapshot_requires_manage_server_access(self):
        pool = migrated_pool()
        client, patches = notifier_client(pool, allowed=False)
        try:
            response = client.get(f"/api/guild/{GUILD}/notifier")
        finally:
            stop_patches(patches)
        self.assertEqual(response.status_code, 403)

    def test_config_save_validates_resources_and_csrf(self):
        pool = migrated_pool()
        client, patches = notifier_client(pool)
        try:
            rejected = client.post(
                f"/api/guild/{GUILD}/notifier/config",
                json={"default_channel_id": "999"},
                headers={"X-CSRF-Token": "test-csrf"},
            )
            missing_csrf = client.post(
                f"/api/guild/{GUILD}/notifier/config",
                json={"enabled": False},
            )
            saved = client.post(
                f"/api/guild/{GUILD}/notifier/config",
                json={"enabled": False, "default_channel_id": "20", "ping_role_id": "900"},
                headers={"X-CSRF-Token": "test-csrf"},
            )
        finally:
            stop_patches(patches)

        self.assertEqual(rejected.status_code, 400)
        self.assertIn("does not belong", rejected.get_json()["error"])
        self.assertEqual(missing_csrf.status_code, 403)
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(
            saved.get_json()["config"],
            {"enabled": False, "default_channel_id": "20", "ping_role_id": "900"},
        )

    def test_add_follow_stores_the_seeded_post_and_rejects_bad_input(self):
        pool = migrated_pool()
        client, patches = notifier_client(pool)
        try:
            with patch.object(
                notifier, "validate_account", side_effect=lambda platform, query: ok_twitch(query)
            ), patch.object(
                notifier,
                "fetch_latest_post",
                side_effect=lambda platform, username: post("stream:1"),
            ):
                added = client.post(
                    f"/api/guild/{GUILD}/notifier/follows",
                    json={
                        "platform": "twitch",
                        "query": "https://twitch.tv/shroud",
                        "channel_id": "10",
                    },
                    headers={"X-CSRF-Token": "test-csrf"},
                )
                duplicate = client.post(
                    f"/api/guild/{GUILD}/notifier/follows",
                    json={"platform": "twitch", "query": "shroud", "channel_id": "20"},
                    headers={"X-CSRF-Token": "test-csrf"},
                )
            invalid = client.post(
                f"/api/guild/{GUILD}/notifier/follows",
                json={"platform": "myspace", "query": "x", "channel_id": "10"},
                headers={"X-CSRF-Token": "test-csrf"},
            )
            blocked = client.post(
                f"/api/guild/{GUILD}/notifier/follows",
                json={"platform": "twitch", "query": "shroud", "channel_id": "999"},
                headers={"X-CSRF-Token": "test-csrf"},
            )
            rows = asyncio.run(follows.list_follows(pool, GUILD))
        finally:
            stop_patches(patches)

        self.assertEqual(added.status_code, 200)
        self.assertTrue(added.get_json()["created"])
        # The current post is stored, so following never dumps the back catalogue.
        self.assertEqual(added.get_json()["follow"]["last_post_id"], "stream:1")
        # Re-adding the same account moves it instead of duplicating it.
        self.assertEqual(duplicate.status_code, 200)
        self.assertFalse(duplicate.get_json()["created"])
        self.assertEqual(duplicate.get_json()["follow"]["channel_id"], "20")
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(blocked.status_code, 400)
        self.assertEqual(len(rows), 1)

    def test_add_follow_reports_platform_limits(self):
        pool = migrated_pool()
        for index in range(follows.MAX_FOLLOWS_PER_PLATFORM):
            follow(pool, username=f"streamer{index}")
        client, patches = notifier_client(pool)
        try:
            with patch.object(
                notifier, "validate_account", side_effect=lambda platform, query: ok_twitch(query)
            ):
                response = client.post(
                    f"/api/guild/{GUILD}/notifier/follows",
                    json={"platform": "twitch", "query": "onemore", "channel_id": "10"},
                    headers={"X-CSRF-Token": "test-csrf"},
                )
        finally:
            stop_patches(patches)

        self.assertEqual(response.status_code, 409)
        self.assertIn("already follows", response.get_json()["error"])

    def test_update_and_delete_follows(self):
        pool = migrated_pool()
        follow(pool, last_post_id="stream:1")
        client, patches = notifier_client(pool)
        try:
            updated = client.post(
                f"/api/guild/{GUILD}/notifier/follows/update",
                json={
                    "platform": "twitch",
                    "username": "shroud",
                    "enabled": False,
                    "template": "Hi {account}",
                },
                headers={"X-CSRF-Token": "test-csrf"},
            )
            bad_template = client.post(
                f"/api/guild/{GUILD}/notifier/follows/update",
                json={"platform": "twitch", "username": "shroud", "template": "Hi {nope}"},
                headers={"X-CSRF-Token": "test-csrf"},
            )
            removed = client.delete(
                f"/api/guild/{GUILD}/notifier/follows/twitch/shroud",
                headers={"X-CSRF-Token": "test-csrf"},
            )
            again = client.delete(
                f"/api/guild/{GUILD}/notifier/follows/twitch/shroud",
                headers={"X-CSRF-Token": "test-csrf"},
            )
        finally:
            stop_patches(patches)

        self.assertEqual(updated.status_code, 200)
        self.assertFalse(updated.get_json()["follow"]["enabled"])
        self.assertEqual(updated.get_json()["follow"]["template"], "Hi {account}")
        self.assertEqual(bad_template.status_code, 400)
        self.assertEqual(removed.status_code, 200)
        self.assertEqual(again.status_code, 404)

    def test_test_notification_posts_to_the_followed_channel(self):
        pool = migrated_pool()
        follow(pool, last_post_id="stream:1")
        channel = FakeChannel(10)
        guild = FakeGuild(GUILD, [channel])
        bot = SimpleNamespace(cxn=pool, get_guild=lambda guild_number: guild)
        client, patches = notifier_client(pool, bot=bot)
        try:
            with patch.object(
                notifier,
                "fetch_latest_post",
                side_effect=lambda platform, username: post("stream:2"),
            ):
                response = client.post(
                    f"/api/guild/{GUILD}/notifier/test",
                    json={"platform": "twitch", "username": "shroud"},
                    headers={"X-CSRF-Token": "test-csrf"},
                )
        finally:
            stop_patches(patches)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["delivered"])
        self.assertEqual(len(channel.sent), 1)

    def test_test_notification_reports_an_unreachable_account(self):
        pool = migrated_pool()
        follow(pool, last_post_id="stream:1")
        channel = FakeChannel(10)
        guild = FakeGuild(GUILD, [channel])
        bot = SimpleNamespace(cxn=pool, get_guild=lambda guild_number: guild)
        client, patches = notifier_client(pool, bot=bot)
        try:
            with patch.object(
                notifier, "fetch_latest_post", side_effect=lambda platform, username: None
            ):
                response = client.post(
                    f"/api/guild/{GUILD}/notifier/test",
                    json={"platform": "twitch", "username": "shroud"},
                    headers={"X-CSRF-Token": "test-csrf"},
                )
        finally:
            stop_patches(patches)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.get_json()["delivered"])
        self.assertEqual(channel.sent, [])


class BotHandoffTests(unittest.TestCase):
    """The tab has to work through the real ``configure_bot`` hand-off.

    Reported bug: while a proxy was handling Discord's global rate limits the
    Notifications tab only ever showed "Couldn't load social notifications. The
    Discord bot is not available." — ``webapp.notifier_routes`` snapshots the
    shared names at import time, and ``server.configure_bot`` used to update a
    hand-kept list of route modules that did not include it, so this module kept
    the ``_discord_bot = None`` from before the bot existed and every notifier
    endpoint answered 503 with exactly that message. The other notifier tests
    patch ``routes._discord_bot`` directly, which is why none of them caught it.
    """

    def setUp(self):
        self.previous = {
            name: getattr(module, "_discord_bot", None)
            for name, module in list(sys.modules.items())
            if name.startswith("webapp.")
        }

    def tearDown(self):
        for name, value in self.previous.items():
            module = sys.modules.get(name)
            if module is not None and hasattr(module, "_discord_bot"):
                module._discord_bot = value

    def test_every_route_module_that_holds_a_bot_receives_the_live_one(self):
        bot = SimpleNamespace(cxn=None)

        server_routes.configure_bot(bot)

        self.assertIs(server_routes._discord_bot, bot)
        holders = [
            name
            for name, module in sys.modules.items()
            if name.startswith("webapp.")
            and module is not None
            and hasattr(module, "_discord_bot")
        ]
        self.assertIn("webapp.notifier_routes", holders)
        self.assertIn("webapp.dashboard_routes", holders)
        for name in holders:
            with self.subTest(module=name):
                self.assertIs(sys.modules[name]._discord_bot, bot)

    def test_the_snapshot_loads_through_the_real_hand_off_while_proxied(self):
        """No ``routes._discord_bot`` patch, and Discord egress is off-limits.

        ``WebshareProxyManager`` writes ``bot.http.proxy`` while it rides out a
        global rate limit, so the tab has to load without a single Discord REST
        call. Anything Discord-facing is poisoned here to prove it.
        """
        pool = migrated_pool()
        follow(pool, last_post_id="stream:1")
        bot = SimpleNamespace(
            cxn=pool,
            get_guild=lambda guild_number: None,
            http=SimpleNamespace(
                proxy="http://webshare:secret@127.0.0.1:8080",
                user_agent="DiscordBot (https://discord.com, 2.7.1)",
            ),
            standby_failover=SimpleNamespace(active_origin=None),
        )
        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": "1", "username": "tester"}
            session["access_token"] = "test-token"
            session["token_exp"] = time.time() + 3600
        manager = SimpleNamespace(
            get_user_entry=lambda user_id: None,
            get_guild_entry=lambda guild_number: None,
        )

        def offline(*args, **kwargs):
            raise AssertionError("loading the notifications tab must not call Discord")

        patches = [
            patch.object(routes, "run_on_bot_loop", side_effect=run_awaitable),
            patch.object(server_routes, "managed_guild_ids", return_value={str(GUILD)}),
            patch.object(server_routes, "_load_blacklist_manager", return_value=manager),
            patch.object(server_routes, "discord_request", side_effect=offline),
            patch.object(server_routes, "discord_get", side_effect=offline),
            patch.object(routes, "discord_request", side_effect=offline),
            patch.object(routes, "discord_get", side_effect=offline),
        ]
        for active_patch in patches:
            active_patch.start()
        server_routes.configure_bot(bot)
        try:
            response = client.get(f"/api/guild/{GUILD}/notifier")
        finally:
            stop_patches(patches)

        self.assertEqual(response.status_code, 200, response.get_json())
        payload = response.get_json()
        self.assertEqual([row["username"] for row in payload["follows"]], ["shroud"])
        self.assertIn("twitch", [platform["id"] for platform in payload["platforms"]])


if __name__ == "__main__":
    unittest.main()
