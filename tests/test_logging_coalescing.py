"""The 30-second retention window that merges rapid member log entries.

A role menu that toggles several roles fires one member update per click, so
the logs used to gain one message per role. An entry about a member now stays
open for 30 seconds and later changes edit it instead of posting again.
"""

import asyncio
import io
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import discord

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.logging import cog as logging_cog  # noqa: E402

GUILD_ID = 111
BOT_ID = 999
CHANNEL_ID = 555


def _runner(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


class _Message:
    """A sent log entry that records the edits it receives."""

    def __init__(self, view):
        self.view = view
        self.edits = []
        self.mentions = []
        self.deleted = False
        self.id = 1

    async def edit(self, *, view, allowed_mentions=None):
        self.edits.append(view)
        self.mentions.append(allowed_mentions)
        self.view = view

    async def delete(self):
        self.deleted = True


class _Channel:
    """A channel that cannot own a webhook, so entries post as the bot."""

    def __init__(self, channel_id=CHANNEL_ID):
        self.id = channel_id
        self.sent = []

    async def send(self, *, view, files, allowed_mentions):
        message = _Message(view)
        self.sent.append(message)
        return message


class _Guild:
    id = GUILD_ID
    name = "Test server"


def _texts(view):
    """The text lines of a log entry, in order."""
    container = view.children[0]
    return [
        item.content for item in container.children
        if isinstance(item, discord.ui.TextDisplay)
    ]


def _body(message):
    return "\n".join(_texts(message.view))


def _member_update(*changes):
    return "\n".join(["**Member:** <@42> (`tester` — ID: `42`)", *changes])


class _CogTestCase(unittest.TestCase):
    def setUp(self):
        # The real limiter is per (guild, channel) and would make a test wait.
        self.limiter = mock.patch.object(logging_cog, "log_channel_limiter")
        self.limiter.start()
        logging_cog.log_channel_limiter.acquire = mock.AsyncMock()
        self.addCleanup(self.limiter.stop)
        self.cog = logging_cog.ServerLogger(
            SimpleNamespace(user=SimpleNamespace(id=BOT_ID)))
        self.channel = _Channel()

    def send(self, body, *, title="Member Updated", target_id=42,
             category="members", channel=None, files=None):
        _runner(self.cog._send_entry(
            _Guild(), channel or self.channel, category, title, body,
            target_id=target_id, files=files,
            file_components=False if files else True))


class TestRetentionWindow(_CogTestCase):
    def test_a_second_role_change_edits_the_first_entry(self):
        self.send(_member_update("**Roles Added:** <@&1>"))
        self.send(_member_update("**Roles Added:** <@&2>"))

        self.assertEqual(len(self.channel.sent), 1)
        message = self.channel.sent[0]
        self.assertEqual(len(message.edits), 1)
        body = _body(message)
        # Both roles are in the one entry, and the heading did not duplicate.
        self.assertIn("<@&1>", body)
        self.assertIn("<@&2>", body)
        self.assertEqual(body.count("**Member:**"), 1)
        self.assertIn(logging_cog.COALESCED_NOTE, body)

    def test_every_merged_edit_suppresses_mentions(self):
        # The merged body mentions roles and members. An edit that omitted
        # allowed_mentions would ping every role named in the entry.
        self.send(_member_update("**Roles Added:** <@&1>"))
        self.send(_member_update("**Roles Added:** <@&2>"))
        self.send(_member_update("**Roles Added:** <@&3>"))

        mentions = self.channel.sent[0].mentions
        self.assertEqual(len(mentions), 2)
        for allowed in mentions:
            self.assertIs(allowed.roles, False)
            self.assertIs(allowed.users, False)
            self.assertIs(allowed.everyone, False)
            self.assertIs(allowed.replied_user, False)

    def test_added_and_removed_roles_are_kept_apart(self):
        self.send(_member_update("**Roles Added:** <@&1>"))
        self.send(_member_update("**Roles Removed:** <@&9>"))

        body = _body(self.channel.sent[0])
        self.assertIn("**Roles Added:** <@&1>", body)
        self.assertIn("**Roles Removed:** <@&9>", body)

    def test_the_same_role_is_not_listed_twice(self):
        self.send(_member_update("**Roles Added:** <@&1>"))
        self.send(_member_update("**Roles Added:** <@&1>"))

        self.assertEqual(_body(self.channel.sent[0]).count("<@&1>"), 1)

    def test_a_role_toggled_off_again_removes_the_entry(self):
        self.send(_member_update("**Roles Added:** <@&1>"))
        self.send(_member_update("**Roles Removed:** <@&1>"))

        # Nothing changed in the end, so neither message nor a new entry stays.
        self.assertEqual(len(self.channel.sent), 1)
        self.assertTrue(self.channel.sent[0].deleted)
        self.assertEqual(self.cog._pending_entries, {})

    def test_a_change_after_the_window_starts_a_new_entry(self):
        self.send(_member_update("**Roles Added:** <@&1>"))
        # Age the open entry past its 30-second window.
        pending = self.cog._pending_entries[
            (GUILD_ID, "members", "Member Updated", 42)]
        pending.expires_at = 0.0
        self.send(_member_update("**Roles Added:** <@&2>"))

        self.assertEqual(len(self.channel.sent), 2)
        self.assertEqual(self.channel.sent[0].edits, [])
        self.assertNotIn("<@&1>", _body(self.channel.sent[1]))

    def test_the_window_is_thirty_seconds(self):
        self.send(_member_update("**Roles Added:** <@&1>"))
        pending = self.cog._pending_entries[
            (GUILD_ID, "members", "Member Updated", 42)]

        self.assertEqual(logging_cog.ENTRY_RETENTION_SECONDS, 30.0)
        remaining = pending.expires_at - logging_cog.time.monotonic()
        self.assertGreater(remaining, 25)
        self.assertLessEqual(remaining, logging_cog.ENTRY_RETENTION_SECONDS)

    def test_a_different_member_gets_its_own_entry(self):
        self.send(_member_update("**Roles Added:** <@&1>"))
        self.send(_member_update("**Roles Added:** <@&2>"), target_id=43)

        self.assertEqual(len(self.channel.sent), 2)
        self.assertEqual(self.channel.sent[0].edits, [])

    def test_a_different_channel_gets_its_own_entry(self):
        self.send(_member_update("**Roles Added:** <@&1>"))
        other = _Channel(777)
        self.send(_member_update("**Roles Added:** <@&2>"), channel=other)

        self.assertEqual(len(other.sent), 1)
        self.assertEqual(self.channel.sent[0].edits, [])

    def test_titles_without_a_retention_window_always_post(self):
        self.send(_member_update("**Roles Added:** <@&1>"), title="Member Joined")
        self.send(_member_update("**Roles Added:** <@&2>"), title="Member Joined")

        self.assertEqual(len(self.channel.sent), 2)
        self.assertEqual(self.channel.sent[0].edits, [])

    def test_a_picture_change_is_never_merged_into_an_earlier_entry(self):
        files = [discord.File(io.BytesIO(b"\x89PNG-body"), filename="after.png")]
        self.send(
            _member_update("**Changed:** Global profile picture"), files=files)

        self.assertEqual(len(self.channel.sent), 1)
        self.assertEqual(self.cog._pending_entries, {})

    def test_a_deleted_entry_falls_back_to_a_fresh_message(self):
        self.send(_member_update("**Roles Added:** <@&1>"))
        message = self.channel.sent[0]

        async def _gone(*, view, allowed_mentions=None):
            raise discord.NotFound(
                SimpleNamespace(status=404, reason="Not Found"), "Unknown Message")

        message.edit = _gone
        self.send(_member_update("**Roles Added:** <@&2>"))

        self.assertEqual(len(self.channel.sent), 2)
        self.assertIn("<@&2>", _body(self.channel.sent[1]))

    def test_a_nickname_change_merges_its_latest_value(self):
        self.send(_member_update("**Old Nickname:** `a`\n**New Nickname:** `b`"),
                  title="Nickname Changed", category="moderation")
        self.send(_member_update("**Old Nickname:** `b`\n**New Nickname:** `c`"),
                  title="Nickname Changed", category="moderation")

        body = _body(self.channel.sent[0])
        self.assertEqual(body.count("**New Nickname:**"), 1)
        self.assertIn("**New Nickname:** `c`", body)

    def test_closed_entries_and_their_locks_are_forgotten(self):
        self.send(_member_update("**Roles Added:** <@&1>"), target_id=42)
        self.send(_member_update("**Roles Added:** <@&2>"), target_id=43)
        for pending in self.cog._pending_entries.values():
            pending.expires_at = 0.0

        # The next member entry sweeps the closed ones instead of a timer.
        self.send(_member_update("**Roles Added:** <@&3>"), target_id=44)

        self.assertEqual(
            list(self.cog._pending_entries),
            [(GUILD_ID, "members", "Member Updated", 44)],
        )
        self.assertEqual(len(self.cog._pending_locks), 1)


class TestBodyMerge(unittest.TestCase):
    def test_split_keeps_the_heading_whole(self):
        heading, details = logging_cog._split_entry_body(
            "**Member:** <@42> (`tester`)\n**Roles Added:** <@&1>")

        self.assertEqual(heading, "**Member:** <@42> (`tester`)")
        self.assertEqual(details, [("Roles Added", "<@&1>")])

    def test_single_valued_details_take_the_newest_value(self):
        merged = logging_cog._merge_entry_details(
            [("Reason", "first")], [("Reason", "second")])

        self.assertEqual(merged, [("Reason", "second")])

    def test_role_lists_union_without_duplicates(self):
        merged = logging_cog._merge_entry_details(
            [("Roles Added", "<@&1>")], [("Roles Added", "<@&2>, <@&1>")])

        self.assertEqual(merged, [("Roles Added", "<@&1>, <@&2>")])

    def test_a_role_granted_and_taken_back_cancels_out(self):
        merged = logging_cog._merge_entry_details(
            [("Roles Added", "<@&1>")], [("Roles Removed", "<@&1>")])

        self.assertEqual(merged, [])

    def test_a_role_removed_and_granted_back_also_cancels_out(self):
        merged = logging_cog._merge_entry_details(
            [("Roles Removed", "<@&1>")], [("Roles Added", "<@&1>")])

        self.assertEqual(merged, [])

    def test_a_role_toggled_three_times_keeps_the_net_change(self):
        merged = logging_cog._merge_entry_details([("Roles Added", "<@&1>")], [])
        merged = logging_cog._merge_entry_details(merged, [("Roles Removed", "<@&1>")])
        merged = logging_cog._merge_entry_details(merged, [("Roles Added", "<@&1>")])

        self.assertEqual(merged, [("Roles Added", "<@&1>")])
