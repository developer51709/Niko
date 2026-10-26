"""Regression tests for the blacklist feature lockdown.

``utils.guild_lockdown`` is the two-way switch a guild blacklist flips: it
switches every Niko feature off while saving what the server looked like, and
replays that saved state once the blacklist is lifted. These tests pin the
promises the dashboard's step flow and the runtime guards depend on:

* the ordered step contract shared with ``web/src/utils/guildBlacklist.ts``,
* each step switching one feature off *and* recording how to bring it back,
* the disabled state living in the database, so it survives a restart,
* unblacklisting (or an approved appeal) restoring exactly the saved state,
* the component guards and the official-broadcast skip.
"""

import asyncio
import re
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import database
from database import _convert_query, _make_row, _serialize_args
from utils import guild_lockdown
from utils.blacklist_manager import BlacklistManager

GUILD = 4242
OTHER_GUILD = 4343
STARBOARD_CHANNEL = 900
INVITE_CHANNEL = 901
OPEN_POLL = 1001
CLOSED_POLL = 1002
UNLOCKED_POLL = 1003
LATE_POLL = 1004
OPEN_GIVEAWAY = 2001
ENDED_GIVEAWAY = 2002

#: The tables the lockdown touches, deliberately without the ``locked`` columns
#: so the migration that adds them is exercised the way an older bot would.
SCHEMA = (
    "CREATE TABLE IF NOT EXISTS blacklist_guilds (id INTEGER PRIMARY KEY, reason TEXT, timestamp REAL, added_by INTEGER, status TEXT, appeal_id TEXT)",
    "CREATE TABLE IF NOT EXISTS blacklist_users (id INTEGER PRIMARY KEY, reason TEXT, timestamp REAL, added_by INTEGER, expires_at REAL, status TEXT, appeal_id TEXT)",
    "CREATE TABLE IF NOT EXISTS abuse_strikes (user_id INTEGER PRIMARY KEY, strikes INTEGER NOT NULL DEFAULT 0, updated_at REAL NOT NULL)",
    "CREATE TABLE IF NOT EXISTS follows (guild_id INTEGER, platform TEXT, username TEXT, channel_id INTEGER, template TEXT, last_post_id TEXT, enabled INTEGER DEFAULT 1, ping_role_id INTEGER, failures INTEGER DEFAULT 0, last_checked_at TEXT, PRIMARY KEY (guild_id, platform, username))",
    "CREATE TABLE IF NOT EXISTS notifier_config (guild_id INTEGER PRIMARY KEY, enabled INTEGER NOT NULL DEFAULT 1, default_channel_id INTEGER, ping_role_id INTEGER, updated_at TEXT NOT NULL DEFAULT (datetime('now')))",
    "CREATE TABLE IF NOT EXISTS starboard_config (guild_id INTEGER PRIMARY KEY, channel_id INTEGER, threshold INTEGER NOT NULL DEFAULT 3, emoji TEXT NOT NULL DEFAULT '⭐', ignored_channels TEXT NOT NULL DEFAULT '[]')",
    "CREATE TABLE IF NOT EXISTS polls (message_id INTEGER PRIMARY KEY, guild_id INTEGER, channel_id INTEGER, author_id INTEGER, question TEXT, options TEXT, closed INTEGER DEFAULT 0, created_at TEXT)",
    "CREATE TABLE IF NOT EXISTS poll_votes (message_id INTEGER, user_id INTEGER, option_idx INTEGER, PRIMARY KEY (message_id, user_id))",
    "CREATE TABLE IF NOT EXISTS giveaways (message_id INTEGER PRIMARY KEY, channel_id INTEGER, guild_id INTEGER, prize TEXT, winners_count INTEGER, end_time TEXT, ended BOOLEAN DEFAULT 0, host_id INTEGER, requirements TEXT)",
    "CREATE TABLE IF NOT EXISTS participants (message_id INTEGER, user_id INTEGER, PRIMARY KEY (message_id, user_id))",
    "CREATE TABLE IF NOT EXISTS notification_channels (guild_id INTEGER PRIMARY KEY, channel_id INTEGER NOT NULL)",
)


class FakePool:
    """The bot's async pool API over an in-process sqlite3 connection.

    Mirrors the ``LocalPool`` the notifier tests use: same SQL surface, including
    the ``$1`` placeholder numbering the bot writes, but with a real file behind
    it so a test can reopen the same database as a fresh process would.
    """

    db_type = "sqlite"

    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        for statement in SCHEMA:
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

    def value(self, query, *args):
        """Read one cell synchronously, for assertions."""
        cursor = self.db.execute(_convert_query(query), _serialize_args(list(args)))
        row = cursor.fetchone()
        return None if row is None else row[0]

    def count(self, table, where="", *args):
        return int(self.value(f"SELECT COUNT(*) FROM {table} {where}", *args))


class FakeResponse:
    def __init__(self, recorder=None):
        self.messages = recorder if recorder is not None else []

    async def send_message(self, content=None, **kwargs):
        self.messages.append(content)

    async def send(self, content=None, **kwargs):
        self.messages.append(content)

    async def defer(self, **kwargs):
        return None

    async def edit_message(self, **kwargs):
        return None


class FakeMember:
    def __init__(self):
        self.views = []

    async def send(self, view=None, **kwargs):
        self.views.append(view)


class FakeGuild:
    def __init__(self, guild_id, owner=None):
        self.id = guild_id
        self.owner = owner


class FakeChannel:
    def __init__(self, channel_id):
        self.id = channel_id
        self.views = []

    async def send(self, view=None, **kwargs):
        self.views.append(view)


class FakeStarboardCog:
    def __init__(self, channel_id):
        self.data = {"guilds": {str(GUILD): {"channel_id": channel_id}}}


class FakeMessage:
    def __init__(self, message_id):
        self.id = message_id

    async def edit(self, **kwargs):
        return None


class FakeInteraction:
    def __init__(self, guild_id=GUILD, user_id=99, message_id=OPEN_POLL, locale="en"):
        self.guild_id = guild_id
        self.user = SimpleNamespace(id=user_id, bot=False)
        self.guild = SimpleNamespace(id=guild_id, preferred_locale=locale)
        self.message = FakeMessage(message_id)
        self.sent = []
        self.response = FakeResponse(self.sent)
        self.followup = FakeResponse(self.sent)


class FakeBot:
    """Enough of a bot for the lockdown: the pool, guild lookup, and channels."""

    def __init__(self, pool, owner=None, channels=None, starboard_channel=None):
        self.cxn = pool
        self.owner = owner
        self.guild = FakeGuild(GUILD, owner)
        self.channels = {int(key): value for key, value in (channels or {}).items()}
        self.starboard = FakeStarboardCog(starboard_channel) if starboard_channel is not None else None

    def get_guild(self, guild_id):
        return self.guild if int(guild_id) == GUILD else None

    def get_cog(self, name):
        return self.starboard if name == "Starboard" else None

    def get_channel(self, channel_id):
        return self.channels.get(int(channel_id))


class LockdownTestCase(unittest.TestCase):
    def setUp(self):
        self.previous_pool = database._shared_pool
        self.previous_manager = BlacklistManager._instance
        BlacklistManager._instance = None
        self.pool = FakePool()
        database._shared_pool = self.pool
        self.seed(self.pool)
        self.owner = FakeMember()
        self.bot = FakeBot(
            self.pool,
            owner=self.owner,
            channels={STARBOARD_CHANNEL: FakeChannel(STARBOARD_CHANNEL)},
            starboard_channel=STARBOARD_CHANNEL,
        )

    def tearDown(self):
        database._shared_pool = self.previous_pool
        BlacklistManager._instance = self.previous_manager

    @staticmethod
    def seed(pool):
        """A server that uses the notifier, starboard, polls, and giveaways."""
        asyncio.run(pool.execute(
            "INSERT OR REPLACE INTO starboard_config (guild_id, channel_id, threshold, emoji, ignored_channels) VALUES ($1, $2, $3, $4, $5)",
            GUILD, STARBOARD_CHANNEL, 5, "⭐", "[111]",
        ))
        asyncio.run(pool.execute(
            "INSERT OR REPLACE INTO follows (guild_id, platform, username, channel_id, template, last_post_id, enabled, ping_role_id, failures, last_checked_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
            GUILD, "twitch", "shroud", 321, "", "stream:1", 1, None, 0, None,
        ))
        asyncio.run(pool.execute(
            "INSERT OR REPLACE INTO notifier_config (guild_id, enabled, default_channel_id, ping_role_id) VALUES ($1, $2, $3, $4)",
            GUILD, 1, 321, None,
        ))
        for message_id, closed in ((OPEN_POLL, 0), (CLOSED_POLL, 1), (UNLOCKED_POLL, 0)):
            asyncio.run(pool.execute(
                "INSERT OR REPLACE INTO polls (message_id, guild_id, channel_id, author_id, question, options, closed, created_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
                message_id, GUILD, 500, 99, "Tea or coffee?", '["Tea", "Coffee"]', closed, "2026-01-01 00:00:00",
            ))
        for message_id, ended in ((OPEN_GIVEAWAY, 0), (ENDED_GIVEAWAY, 1)):
            asyncio.run(pool.execute(
                "INSERT OR REPLACE INTO giveaways (message_id, channel_id, guild_id, prize, winners_count, end_time, ended, host_id, requirements) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
                message_id, 505, GUILD, "Nitro", 1, "2026-01-02 00:00:00", ended, 99, "{}",
            ))

    def blacklist(self, bot=None, lockdown=True):
        manager = BlacklistManager()
        added = asyncio.run(
            manager.add_guild(
                GUILD,
                reason="abuse",
                added_by=7,
                bot=self.bot if bot is None else bot,
                lockdown=lockdown,
            )
        )
        self.assertTrue(added)
        return manager


class LockdownStepContractTests(LockdownTestCase):
    def test_step_keys_and_labels_match_the_dashboard_helper(self):
        source = (ROOT / "web/src/utils/guildBlacklist.ts").read_text(encoding="utf-8")
        block = source.split("export const LOCKDOWN_STEPS = [", 1)[1].split("] as const;", 1)[0]
        pairs = [tuple(match) for match in re.findall(r'\["([a-z_]+)",\s*"([^"]+)"\]', block)]

        self.assertEqual(pairs, list(guild_lockdown.LOCKDOWN_STEPS))
        # The API runs every step but the blacklist write itself.
        self.assertEqual(list(guild_lockdown.FEATURE_STEPS), [key for key, _ in pairs[1:]])
        self.assertEqual(guild_lockdown.step_label("polls"), "Disabling polls…")


class LockdownStepTests(LockdownTestCase):
    def test_lockdown_switches_every_feature_off_and_saves_its_state(self):
        manager = BlacklistManager()
        self.assertTrue(asyncio.run(manager.add_guild(GUILD, reason="abuse", added_by=7, bot=self.bot, lockdown=False)))

        report = asyncio.run(manager.lockdown(GUILD, bot=self.bot))

        self.assertEqual([item["step"] for item in report], list(guild_lockdown.FEATURE_STEPS))
        self.assertEqual([item["label"] for item in report], [guild_lockdown.step_label(step) for step in guild_lockdown.FEATURE_STEPS])
        self.assertEqual({item["status"] for item in report}, {"done"})

        # Starboard: the channel is cleared, everything else is kept.
        self.assertIsNone(self.pool.value("SELECT channel_id FROM starboard_config WHERE guild_id = $1", GUILD))
        self.assertEqual(self.pool.value("SELECT threshold FROM starboard_config WHERE guild_id = $1", GUILD), 5)
        self.assertEqual(self.pool.value("SELECT ignored_channels FROM starboard_config WHERE guild_id = $1", GUILD), "[111]")
        self.assertIsNone(self.bot.starboard.data["guilds"][str(GUILD)]["channel_id"])

        # Social notifications: the server switch is off, the follows are kept.
        self.assertEqual(self.pool.value("SELECT enabled FROM notifier_config WHERE guild_id = $1", GUILD), 0)
        self.assertEqual(self.pool.count("follows", "WHERE guild_id = $1", GUILD), 1)
        self.assertEqual(self.pool.value("SELECT enabled FROM follows WHERE guild_id = $1", GUILD), 1)

        # Polls and giveaways: only the live rows are locked.
        self.assertEqual(self.pool.value("SELECT locked FROM polls WHERE message_id = $1", OPEN_POLL), 1)
        self.assertEqual(self.pool.value("SELECT locked FROM polls WHERE message_id = $1", CLOSED_POLL), 0)
        self.assertEqual(self.pool.value("SELECT locked FROM giveaways WHERE message_id = $1", OPEN_GIVEAWAY), 1)
        self.assertEqual(self.pool.value("SELECT locked FROM giveaways WHERE message_id = $1", ENDED_GIVEAWAY), 0)

        # The owner is told, and the saved state is recorded for the appeal.
        self.assertEqual(len(self.owner.views), 1)
        locks = {lock["feature"]: lock for lock in asyncio.run(guild_lockdown.read_locks(self.pool, GUILD))}
        self.assertEqual(set(locks), {"social", "starboard", "polls", "giveaways"})
        self.assertEqual(locks["starboard"]["previous_state"]["channel_id"], STARBOARD_CHANNEL)
        self.assertEqual(locks["polls"]["previous_state"]["message_ids"], [OPEN_POLL, UNLOCKED_POLL])
        self.assertEqual(locks["giveaways"]["previous_state"]["message_ids"], [OPEN_GIVEAWAY])

    def test_steps_without_anything_to_pause_report_skipped(self):
        # An empty server: no starboard channel, no notifier, no active polls.
        empty = FakePool()
        asyncio.run(empty.execute("INSERT OR REPLACE INTO blacklist_guilds (id, reason, timestamp, added_by, status, appeal_id) VALUES ($1, $2, $3, $4, 'active', NULL)", OTHER_GUILD, "spam", 1.0, 7))
        database._shared_pool = empty
        BlacklistManager._instance = None
        manager = BlacklistManager()
        asyncio.run(manager.load())

        report = asyncio.run(manager.lockdown(OTHER_GUILD, bot=None))

        self.assertEqual({item["status"] for item in report}, {"skipped"})

    def test_a_failed_step_is_reported_and_does_not_stop_the_others(self):
        manager = BlacklistManager()

        async def failing_social(pool, guild_id):
            raise RuntimeError("notifier store is down")

        with patch.object(guild_lockdown, "_step_social", failing_social):
            self.assertTrue(asyncio.run(manager.add_guild(GUILD, reason="abuse", added_by=7, bot=self.bot)))

        self.assertTrue(manager.is_guild_blacklisted(GUILD))
        self.assertEqual(self.pool.value("SELECT feature FROM guild_feature_locks WHERE guild_id = $1 AND feature = $2", GUILD, "social"), None)
        # Every other step still ran: a feature that cannot be switched off never
        # leaves the server blacklisted-but-active.
        self.assertIsNone(self.pool.value("SELECT channel_id FROM starboard_config WHERE guild_id = $1", GUILD))
        self.assertEqual(self.pool.value("SELECT locked FROM polls WHERE message_id = $1", OPEN_POLL), 1)
        self.assertEqual(self.pool.value("SELECT locked FROM giveaways WHERE message_id = $1", OPEN_GIVEAWAY), 1)
        self.assertEqual(len(self.owner.views), 1)


class LockdownPersistenceTests(LockdownTestCase):
    def test_disabled_features_survive_a_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "niko.db")
            first = FakePool(path)
            self.seed(first)
            database._shared_pool = first
            BlacklistManager._instance = None
            bot = FakeBot(first, owner=FakeMember(), starboard_channel=STARBOARD_CHANNEL)
            self.assertTrue(asyncio.run(BlacklistManager().add_guild(GUILD, reason="abuse", bot=bot)))

            # A restart drops every in-memory object: new pool, new cache.
            BlacklistManager._instance = None
            restarted = FakePool(path)
            database._shared_pool = restarted
            manager = BlacklistManager()
            asyncio.run(manager.load())

            self.assertTrue(manager.is_guild_blacklisted(GUILD))
            self.assertIsNone(restarted.value("SELECT channel_id FROM starboard_config WHERE guild_id = $1", GUILD))
            self.assertEqual(restarted.value("SELECT enabled FROM notifier_config WHERE guild_id = $1", GUILD), 0)
            self.assertEqual(restarted.value("SELECT locked FROM polls WHERE message_id = $1", OPEN_POLL), 1)
            self.assertEqual(restarted.value("SELECT locked FROM giveaways WHERE message_id = $1", OPEN_GIVEAWAY), 1)

    def test_lockdown_schema_is_created_and_migrated_idempotently(self):
        asyncio.run(guild_lockdown.ensure_schema(self.pool))
        asyncio.run(guild_lockdown.ensure_schema(self.pool))

        poll_columns = {row[1] for row in self.pool.db.execute("PRAGMA table_info(polls)")}
        giveaway_columns = {row[1] for row in self.pool.db.execute("PRAGMA table_info(giveaways)")}
        self.assertIn("locked", poll_columns)
        self.assertIn("locked", giveaway_columns)
        self.assertEqual(
            self.pool.value("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'guild_feature_locks'"),
            1,
        )

    def test_cogs_migrate_the_locked_column_for_older_databases(self):
        polls = (ROOT / "src/cogs/social/polls.py").read_text(encoding="utf-8")
        giveaway = (ROOT / "src/cogs/giveaway/cog.py").read_text(encoding="utf-8")
        self.assertIn("ALTER TABLE polls ADD COLUMN locked", polls)
        self.assertIn("ALTER TABLE giveaways ADD COLUMN locked", giveaway)


class LockdownRestoreTests(LockdownTestCase):
    def test_unblacklisting_restores_the_saved_features(self):
        manager = self.blacklist()
        self.assertIsNone(self.pool.value("SELECT channel_id FROM starboard_config WHERE guild_id = $1", GUILD))

        self.assertTrue(asyncio.run(manager.remove_guild(GUILD, bot=self.bot)))

        self.assertFalse(manager.is_guild_blacklisted(GUILD))
        self.assertEqual(self.pool.value("SELECT channel_id FROM starboard_config WHERE guild_id = $1", GUILD), STARBOARD_CHANNEL)
        self.assertEqual(self.bot.starboard.data["guilds"][str(GUILD)]["channel_id"], STARBOARD_CHANNEL)
        self.assertEqual(self.pool.value("SELECT locked FROM polls WHERE message_id = $1", OPEN_POLL), 0)
        self.assertEqual(self.pool.value("SELECT locked FROM giveaways WHERE message_id = $1", OPEN_GIVEAWAY), 0)
        self.assertEqual(self.pool.count("guild_feature_locks", "WHERE guild_id = $1", GUILD), 0)
        # The notifier is the documented exception: the server turns it back on.
        self.assertEqual(self.pool.value("SELECT enabled FROM notifier_config WHERE guild_id = $1", GUILD), 0)

    def test_restore_keeps_a_starboard_reconfigured_during_the_blacklist(self):
        manager = self.blacklist()
        asyncio.run(self.pool.execute(
            "UPDATE starboard_config SET channel_id = $1 WHERE guild_id = $2",
            INVITE_CHANNEL, GUILD,
        ))

        report = asyncio.run(manager.restore(GUILD, bot=self.bot))

        starboard = [item for item in report if item["step"] == "starboard"][0]
        self.assertEqual(starboard["status"], "skipped")
        self.assertEqual(self.pool.value("SELECT channel_id FROM starboard_config WHERE guild_id = $1", GUILD), INVITE_CHANNEL)
        self.assertEqual(self.pool.count("guild_feature_locks", "WHERE guild_id = $1 AND feature = 'starboard'", GUILD), 0)

    def test_approved_appeal_restores_features(self):
        # The appeal route is the one place a locked guild is released without a
        # staff member visiting the blacklist tab, so it must call restore.
        source = (ROOT / "src/webapp/appeal_routes.py").read_text(encoding="utf-8")
        # The last branch is the handler itself; the earlier ones are the
        # database write inside `review()`.
        block = source.split("if status == \"approved\":")[-1].split("return jsonify", 1)[0]
        self.assertIn("manager.reload()", block)
        self.assertIn("manager.restore(guild_id", block)

        manager = self.blacklist()
        asyncio.run(manager.reload())
        report = asyncio.run(manager.restore(GUILD, bot=self.bot))
        self.assertEqual({item["step"] for item in report}, {"starboard", "polls", "giveaways"})
        self.assertEqual(self.pool.value("SELECT channel_id FROM starboard_config WHERE guild_id = $1", GUILD), STARBOARD_CHANNEL)


class LockdownGuardTests(LockdownTestCase):
    def test_poll_votes_are_refused_while_the_poll_is_locked(self):
        from cogs.social.polls import PollVoteButton

        manager = self.blacklist()
        bot = SimpleNamespace(cxn=self.pool)

        frozen = FakeInteraction(message_id=OPEN_POLL)
        asyncio.run(PollVoteButton(bot, OPEN_POLL, 0, False).callback(frozen))
        self.assertEqual(self.pool.count("poll_votes"), 0)
        self.assertEqual(frozen.sent, [guild_lockdown.paused_message(frozen)])

        # A poll that appeared after the lockdown ran (unlocked row) is still
        # refused: the blacklist itself closes the door on votes.
        self.assertTrue(manager.is_guild_blacklisted(GUILD))
        asyncio.run(self.pool.execute(
            "INSERT OR REPLACE INTO polls (message_id, guild_id, channel_id, author_id, question, options, closed, created_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
            LATE_POLL, GUILD, 500, 99, "New poll", '["Yes", "No"]', 0, "2026-01-01 00:00:00",
        ))
        blocked = FakeInteraction(message_id=LATE_POLL)
        asyncio.run(PollVoteButton(bot, LATE_POLL, 0, False).callback(blocked))
        self.assertEqual(self.pool.count("poll_votes"), 0)
        self.assertEqual(blocked.sent, [guild_lockdown.paused_message(blocked)])

    def test_giveaway_entries_are_refused_while_the_giveaway_is_frozen(self):
        from cogs.giveaway.views import _GiveawayJoinBtn, _giveaway_paused

        manager = self.blacklist()
        bot = SimpleNamespace(cxn=self.pool)

        frozen = FakeInteraction(message_id=OPEN_GIVEAWAY)
        asyncio.run(_GiveawayJoinBtn(bot, OPEN_GIVEAWAY).callback(frozen))
        self.assertEqual(self.pool.count("participants"), 0)
        self.assertEqual(frozen.sent, [guild_lockdown.paused_message(frozen)])

        row = asyncio.run(self.pool.fetchrow("SELECT ended, locked FROM giveaways WHERE message_id = $1", OPEN_GIVEAWAY))
        self.assertTrue(_giveaway_paused(row, GUILD))
        # A row that stayed unlocked is still frozen while the guild is blacklisted.
        self.assertTrue(_giveaway_paused({"ended": 0, "locked": 0}, GUILD))
        manager.blacklist["guilds"] = []
        self.assertFalse(_giveaway_paused({"ended": 0, "locked": 0}, GUILD))

    def test_starboard_ignores_reactions_from_a_blacklisted_guild(self):
        source = (ROOT / "src/cogs/social/starboard.py").read_text(encoding="utf-8")
        block = source.split("async def _on_reaction", 1)[1].split("\n    async def ", 1)[0]
        self.assertIn("is_guild_blacklisted", block)

    def test_official_broadcasts_skip_blacklisted_servers(self):
        from utils.broadcast import split_targets

        manager = BlacklistManager()
        manager.blacklist["guilds"] = [{"id": GUILD, "reason": "abuse", "timestamp": 0.0, "added_by": None}]
        rows = [
            {"guild_id": GUILD, "channel_id": STARBOARD_CHANNEL},
            {"guild_id": OTHER_GUILD, "channel_id": INVITE_CHANNEL},
        ]

        eligible, skipped = split_targets(rows, manager.is_guild_blacklisted)

        # The blacklisted guild never reaches the delivery queue, and the run
        # reports it as skipped instead of silently dropping the server.
        self.assertEqual([row["guild_id"] for row in eligible], [OTHER_GUILD])
        self.assertEqual(skipped, 1)


class LockdownRouteTests(LockdownTestCase):
    """The staff routes the dashboard drives, through a Flask test client."""

    def setUp(self):
        super().setUp()
        import time

        from webapp import app as flask_app
        from webapp import team_routes

        self.routes = team_routes
        self.client = flask_app.test_client()
        with self.client.session_transaction() as session:
            session["user"] = {"id": "1", "username": "tester"}
            session["access_token"] = "test-token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "test-csrf"
        self.patches = [
            patch.object(team_routes, "_discord_bot", self.bot),
            patch.object(team_routes, "run_on_bot_loop", side_effect=lambda awaitable, timeout=8: asyncio.run(awaitable)),
            patch.object(team_routes, "_require_guild_management_role", return_value=("owner", None)),
        ]
        for active_patch in self.patches:
            active_patch.start()

    def tearDown(self):
        for active_patch in reversed(self.patches):
            active_patch.stop()
        super().tearDown()

    def post(self, path, payload):
        return self.client.post(path, json=payload, headers={"X-CSRF-Token": "test-csrf"})

    def test_adding_then_running_each_step_pauses_the_features(self):
        added = self.post(f"/api/staff/guilds/{GUILD}/blacklist", {"action": "add", "reason": "abuse"})
        self.assertEqual(added.status_code, 200)
        self.assertTrue(added.get_json()["blacklisted"])
        # Adding writes only the entry: nothing is paused until the steps run, so
        # the dashboard can report each feature while it is switched off.
        self.assertEqual(self.pool.value("SELECT channel_id FROM starboard_config WHERE guild_id = $1", GUILD), STARBOARD_CHANNEL)

        for step in guild_lockdown.FEATURE_STEPS:
            response = self.post(f"/api/staff/guilds/{GUILD}/blacklist/lockdown", {"step": step})
            self.assertEqual(response.status_code, 200)
            payload = response.get_json()
            self.assertEqual((payload["step"], payload["status"]), (step, "done"))
            self.assertTrue(payload["label"])
            self.assertTrue(payload["detail"])
            self.assertTrue(payload["blacklisted"])

        self.assertIsNone(self.pool.value("SELECT channel_id FROM starboard_config WHERE guild_id = $1", GUILD))
        self.assertEqual(self.pool.value("SELECT locked FROM polls WHERE message_id = $1", OPEN_POLL), 1)
        self.assertEqual(len(self.owner.views), 1)

    def test_a_step_needs_a_blacklist_and_a_known_key(self):
        blocked = self.post(f"/api/staff/guilds/{GUILD}/blacklist/lockdown", {"step": "polls"})
        self.assertEqual(blocked.status_code, 409)

        self.post(f"/api/staff/guilds/{GUILD}/blacklist", {"action": "add", "reason": "abuse"})
        # `database` is the blacklist write the caller already performed, and an
        # unknown key is refused rather than silently reported as done.
        self.assertEqual(self.post(f"/api/staff/guilds/{GUILD}/blacklist/lockdown", {"step": "database"}).status_code, 400)
        self.assertEqual(self.post(f"/api/staff/guilds/{GUILD}/blacklist/lockdown", {"step": "everything"}).status_code, 400)


if __name__ == "__main__":
    unittest.main()
