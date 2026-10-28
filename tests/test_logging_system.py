"""Behaviour of the server logging cog and its rate limiter.

Covers the fixes made after the logging audit: audit-log attribution that used
to blame the wrong moderator, a banned member being logged twice, the config
cache never being invalidated from the dashboard, unbound moderators in the
ban/unban listeners, and the unbounded per-key maps in `RateLimiter`.
"""

import asyncio
import sys
import time
import unittest
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import discord

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.logging import cog as logging_cog  # noqa: E402
from cogs.logging import formatters  # noqa: E402
from utils import ratelimit  # noqa: E402
from webapp.routes import dashboard_routes  # noqa: E402

GUILD_ID = 111
BOT_ID = 999


class _AsyncIter:
    def __init__(self, entries):
        self._entries = list(entries)

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        if self._index >= len(self._entries):
            raise StopAsyncIteration
        entry = self._entries[self._index]
        self._index += 1
        return entry


class FakeAuditEntry:
    def __init__(self, action, target, user, *, age=1.0, reason=None):
        self.action = action
        self.target = target
        self.user = user
        self.reason = reason
        self.created_at = discord.utils.utcnow() - timedelta(seconds=age)


class FakeGuild:
    def __init__(self, entries=()):
        self.id = GUILD_ID
        self.name = "Test server"
        self.entries = list(entries)
        self.audit_calls = []
        self.default_role = SimpleNamespace(id=1, mention="@everyone")
        self.premium_subscription_count = 3
        self.premium_tier = 1

    def audit_logs(self, *, limit=None, action=None):
        self.audit_calls.append(action)
        entries = [entry for entry in self.entries if action is None or entry.action == action]
        return _AsyncIter(entries[: limit or len(entries)])

    def get_channel(self, channel_id):
        return SimpleNamespace(id=channel_id, send=unittest.mock.AsyncMock())


def _bot():
    return SimpleNamespace(
        user=SimpleNamespace(
            id=BOT_ID,
            display_avatar=SimpleNamespace(url="https://cdn.example/bot.png"),
        )
    )


def _member(member_id=42, guild=None):
    return SimpleNamespace(
        id=member_id,
        name="tester",
        mention=f"<@{member_id}>",
        guild=guild,
        roles=[SimpleNamespace(id=5, mention="<@&5>")],
        joined_at=discord.utils.utcnow() - timedelta(days=10),
        display_avatar=SimpleNamespace(url="https://cdn.example/member.png"),
    )


def _runner(coroutine):
    return asyncio.run(coroutine)


class AuditAttributionTests(unittest.TestCase):
    def test_the_entry_matches_the_target_and_the_recency(self):
        cog = logging_cog.ServerLogger(_bot())
        target = SimpleNamespace(id=42)
        other = SimpleNamespace(id=43)
        moderator = SimpleNamespace(mention="<@7>")
        guild = FakeGuild([
            # Newest entry belongs to somebody else: it must not be attributed.
            FakeAuditEntry(discord.AuditLogAction.kick, other, moderator),
            FakeAuditEntry(discord.AuditLogAction.kick, target, moderator, reason="spam"),
        ])

        entry = _runner(cog._audit_entry(guild, discord.AuditLogAction.kick, 42))

        self.assertIsNotNone(entry)
        self.assertIs(entry.target, target)
        self.assertEqual(entry.reason, "spam")

    def test_a_stale_entry_is_not_used(self):
        cog = logging_cog.ServerLogger(_bot())
        target = SimpleNamespace(id=42)
        moderator = SimpleNamespace(mention="<@7>")
        guild = FakeGuild([
            FakeAuditEntry(discord.AuditLogAction.kick, target, moderator, age=600),
        ])

        self.assertIsNone(_runner(cog._audit_entry(guild, discord.AuditLogAction.kick, 42)))


class MemberRemovalTests(unittest.TestCase):
    def setUp(self):
        self.cog = logging_cog.ServerLogger(_bot())
        self.cog.log_event = mock.AsyncMock()

    def test_a_kick_is_logged_once_as_a_kick(self):
        guild = FakeGuild([
            FakeAuditEntry(
                discord.AuditLogAction.kick,
                SimpleNamespace(id=42),
                SimpleNamespace(mention="<@7>"),
                reason="rule breaking",
            )
        ])
        member = _member(guild=guild)

        _runner(self.cog.on_member_remove(member))

        self.cog.log_event.assert_awaited_once()
        args, kwargs = self.cog.log_event.call_args
        self.assertEqual(args[1], "moderation")
        self.assertEqual(args[2], "Kick")
        self.assertIn("rule breaking", args[3])
        self.assertEqual(kwargs["target_id"], 42)

    def test_a_banned_member_is_not_also_logged_as_leaving(self):
        guild = FakeGuild([
            FakeAuditEntry(
                discord.AuditLogAction.ban,
                SimpleNamespace(id=42),
                SimpleNamespace(mention="<@7>"),
            )
        ])
        member = _member(guild=guild)

        _runner(self.cog.on_member_remove(member))

        # The Ban listener owns that entry; a second "Member Left" would be noise.
        self.cog.log_event.assert_not_awaited()

    def test_a_plain_leave_lists_roles_tenure_and_the_avatar(self):
        guild = FakeGuild()
        member = _member(guild=guild)

        _runner(self.cog.on_member_remove(member))

        self.cog.log_event.assert_awaited_once()
        args, kwargs = self.cog.log_event.call_args
        self.assertEqual(args[2], "Member Left")
        self.assertIn("<@&5>", args[3])
        self.assertIn("Joined:", args[3])
        self.assertEqual(kwargs["thumbnail_url"], "https://cdn.example/member.png")


class BanListenerTests(unittest.TestCase):
    def setUp(self):
        self.cog = logging_cog.ServerLogger(_bot())
        self.cog.log_event = mock.AsyncMock()

    def test_a_ban_without_an_audit_entry_does_not_raise(self):
        guild = FakeGuild([])
        user = SimpleNamespace(id=42, mention="<@42>", __str__=lambda _self: "user#0001")

        _runner(self.cog.on_member_ban(guild, user))

        self.cog.log_event.assert_awaited_once()
        body = self.cog.log_event.call_args.args[3]
        self.assertIn("Unknown", body)

    def test_an_unban_reports_the_audit_reason(self):
        guild = FakeGuild([
            FakeAuditEntry(
                discord.AuditLogAction.unban,
                SimpleNamespace(id=42),
                SimpleNamespace(mention="<@7>"),
                reason="appealed",
            )
        ])
        user = SimpleNamespace(id=42, mention="<@42>", __str__=lambda _self: "user#0001")

        _runner(self.cog.on_member_unban(guild, user))

        body = self.cog.log_event.call_args.args[3]
        self.assertIn("appealed", body)
        self.assertIn("<@7>", body)


class ConfigCacheTests(unittest.TestCase):
    def setUp(self):
        self.cog = logging_cog.ServerLogger(_bot())
        self.loader = mock.AsyncMock(return_value={"111": {"members": 5}})
        self._patch = mock.patch.object(logging_cog, "_load_log_config", self.loader)
        self._patch.start()
        self.addCleanup(self._patch.stop)

    def test_the_config_is_reused_within_the_ttl(self):
        _runner(self.cog.config())
        _runner(self.cog.config())
        self.assertEqual(self.loader.await_count, 1)

    def test_invalidate_forces_a_fresh_read(self):
        _runner(self.cog.config())
        self.cog.invalidate()
        _runner(self.cog.config())
        self.assertEqual(self.loader.await_count, 2)

    def test_a_failed_read_keeps_the_last_good_copy(self):
        _runner(self.cog.config())
        self.loader.side_effect = RuntimeError("database offline")
        self.cog.invalidate()

        config = _runner(self.cog.config())

        self.assertEqual(config, {"111": {"members": 5}})

    def test_an_empty_read_never_wipes_a_populated_config(self):
        _runner(self.cog.config())
        self.loader.return_value = {}
        self.cog.invalidate()

        config = _runner(self.cog.config())

        self.assertEqual(config, {"111": {"members": 5}})


class LogEventTests(unittest.TestCase):
    def setUp(self):
        self.cog = logging_cog.ServerLogger(_bot())
        self.cog._config = {"111": {"members": 5, "disabled": ["voice"]}}
        self.cog._config_at = time.monotonic()
        self.cog._send_entry = mock.AsyncMock()
        self.guild = FakeGuild()
        self.guild.get_channel = lambda channel_id: SimpleNamespace(id=channel_id)

    def test_a_disabled_category_sends_nothing(self):
        _runner(self.cog.log_event(self.guild, "voice", "Voice Join", "body"))
        self.cog._send_entry.assert_not_awaited()

    def test_an_unconfigured_category_sends_nothing(self):
        _runner(self.cog.log_event(self.guild, "invites", "Invite Created", "body"))
        self.cog._send_entry.assert_not_awaited()

    def test_a_configured_category_is_sent(self):
        _runner(self.cog.log_event(self.guild, "members", "Member Joined", "body"))
        self.cog._send_entry.assert_awaited_once()


class DashboardLoggingSyncTests(unittest.TestCase):
    def test_the_dashboard_save_invalidates_and_announces(self):
        cog = SimpleNamespace(
            invalidate=mock.Mock(), _audit_logging_change=mock.AsyncMock())
        guild = SimpleNamespace(id=GUILD_ID)
        bot = SimpleNamespace(
            get_cog=lambda name: cog if name == "ServerLogger" else None,
            get_guild=lambda guild_id: guild,
        )

        with mock.patch.object(dashboard_routes, "_discord_bot", bot):
            _runner(dashboard_routes._notify_logging_change(GUILD_ID, {"members": 5}))

        cog.invalidate.assert_called_once()
        cog._audit_logging_change.assert_awaited_once()
        args = cog._audit_logging_change.await_args.args
        self.assertEqual(args[0], guild)
        self.assertEqual(args[1], {"members": 5})

    def test_the_categories_served_to_the_dashboard_match_the_cog(self):
        from webapp import guilds

        served = guilds._serialize_logging_categories()
        self.assertEqual([item["key"] for item in served], list(formatters.CATEGORIES))
        self.assertEqual(
            {item["key"]: item["label"] for item in served},
            {key: info["label"] for key, info in formatters.CATEGORIES.items()},
        )


class RateLimiterTests(unittest.TestCase):
    def test_the_key_maps_stay_bounded(self):
        limiter = ratelimit.RateLimiter(rate=100, per=0.001, max_keys=8)

        async def run():
            for index in range(50):
                await limiter.acquire(("guild", index))

        _runner(run())

        self.assertLessEqual(len(limiter._timestamps), 8)
        self.assertLessEqual(len(limiter._locks), 8)

    def test_an_active_key_is_not_evicted(self):
        limiter = ratelimit.RateLimiter(rate=100, per=0.001, max_keys=8)

        async def run():
            for index in range(20):
                await limiter.acquire("hot")
                await limiter.acquire(("cold", index))

        _runner(run())
        self.assertIn("hot", limiter._timestamps)

    def test_the_rate_is_still_enforced(self):
        limiter = ratelimit.RateLimiter(rate=2, per=0.2)

        async def run():
            started = time.monotonic()
            for _ in range(3):
                await limiter.acquire("key")
            return time.monotonic() - started

        self.assertGreaterEqual(_runner(run()), 0.2)


if __name__ == "__main__":
    unittest.main()
