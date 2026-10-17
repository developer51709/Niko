"""`.dmpurge` — Niko's private DM housekeeping command.

Three properties are easy to break and expensive to notice: the command has to
stay invisible (help menu, `data/commands.json`, public commands page), it has
to stay DM-only, and a purge has to count what it could not delete instead of
reporting a clean run over a partial one.
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import discord
from discord.ext import commands

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.help import views as help_views  # noqa: E402
from cogs.utility import dm_purge  # noqa: E402
from cogs.utility.dm_purge import DMPurge, count_bot_messages, purge_bot_messages  # noqa: E402
from events.startup import writers  # noqa: E402

BOT_ID = 999
USER_ID = 111


def _http_error(status=500):
    return discord.HTTPException(SimpleNamespace(status=status, reason="Server Error"), "refused")


def _not_found():
    return discord.NotFound(SimpleNamespace(status=404, reason="Not Found"), "unknown message")


class FakeMessage:
    def __init__(self, message_id, author_id, *, refusal=None):
        self.id = message_id
        self.author = SimpleNamespace(id=author_id)
        self.deleted = False
        self._refusal = refusal

    async def delete(self):
        if self._refusal is not None:
            raise self._refusal
        self.deleted = True


class FakeChannel:
    """A DM channel: history only, because a DM has no bulk delete."""

    def __init__(self, messages, channel_id=4242):
        self.id = channel_id
        self.messages = list(messages)

    async def history(self, limit=None, oldest_first=False):
        for message in self.messages:
            yield message


class RecordingLimiter:
    """Stands in for the shared limiter so tests never sleep on pacing."""

    def __init__(self):
        self.keys = []

    async def acquire(self, key):
        self.keys.append(key)


class PurgeHelperTests(unittest.TestCase):
    def setUp(self):
        self.limiter = RecordingLimiter()
        patcher = mock.patch.object(dm_purge, "dm_purge_limiter", self.limiter)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_only_nikos_own_messages_are_deleted(self):
        channel = FakeChannel([
            FakeMessage(1, BOT_ID),
            FakeMessage(2, USER_ID),
            FakeMessage(3, BOT_ID),
        ])
        deleted, failed = asyncio.run(purge_bot_messages(channel, bot_id=BOT_ID))
        self.assertEqual((deleted, failed), (2, 0))
        self.assertEqual([message.deleted for message in channel.messages], [True, False, True])
        # One paced request per delete, keyed to the conversation.
        self.assertEqual(self.limiter.keys, [channel.id, channel.id])

    def test_skipped_ids_are_left_alone(self):
        channel = FakeChannel([FakeMessage(1, BOT_ID), FakeMessage(2, BOT_ID)])
        deleted, failed = asyncio.run(
            purge_bot_messages(channel, bot_id=BOT_ID, skip_ids={1})
        )
        self.assertEqual((deleted, failed), (1, 0))
        self.assertFalse(channel.messages[0].deleted)
        self.assertTrue(channel.messages[1].deleted)

    def test_a_message_discord_refuses_is_reported_not_hidden(self):
        channel = FakeChannel([
            FakeMessage(1, BOT_ID, refusal=_http_error()),
            FakeMessage(2, BOT_ID),
            FakeMessage(3, BOT_ID, refusal=_not_found()),
        ])
        deleted, failed = asyncio.run(purge_bot_messages(channel, bot_id=BOT_ID))
        # A message that vanished underneath us is not a failure; a refusal is.
        self.assertEqual((deleted, failed), (1, 1))

    def test_limit_bounds_how_many_messages_are_examined(self):
        channel = FakeChannel([FakeMessage(index, BOT_ID) for index in range(1, 6)])
        deleted, _ = asyncio.run(purge_bot_messages(channel, bot_id=BOT_ID, limit=2))
        self.assertEqual(deleted, 2)
        self.assertEqual(
            [message.deleted for message in channel.messages],
            [True, True, False, False, False],
        )

    def test_progress_is_reported_after_every_delete(self):
        channel = FakeChannel([FakeMessage(index, BOT_ID) for index in range(1, 4)])
        seen = []

        async def on_progress(deleted, failed):
            seen.append((deleted, failed))

        asyncio.run(purge_bot_messages(channel, bot_id=BOT_ID, on_progress=on_progress))
        self.assertEqual(seen, [(1, 0), (2, 0), (3, 0)])

    def test_counting_can_stop_after_the_requested_limit(self):
        """`.dmpurge 2` must not walk a full inbox before offering the prompt."""
        channel = FakeChannel([FakeMessage(index, BOT_ID) for index in range(1, 9)])
        self.assertEqual(
            asyncio.run(count_bot_messages(channel, bot_id=BOT_ID, limit=2)), 2
        )
        self.assertFalse(any(message.deleted for message in channel.messages))

    def test_counting_never_deletes(self):
        channel = FakeChannel([
            FakeMessage(1, BOT_ID),
            FakeMessage(2, USER_ID),
            FakeMessage(3, BOT_ID),
        ])
        self.assertEqual(asyncio.run(count_bot_messages(channel, bot_id=BOT_ID)), 2)
        self.assertEqual(
            asyncio.run(count_bot_messages(channel, bot_id=BOT_ID, skip_ids={1})), 1
        )
        self.assertFalse(any(message.deleted for message in channel.messages))


class FakeDmChannel:
    """Stands in for `discord.DMChannel`, which is what the command gates on."""

    id = 4242


async def _never_called(*args, **kwargs):
    raise AssertionError("a purge must not start without a bot user")


class CommandGateTests(unittest.TestCase):
    """"Only works in DMs with the bot" is the point of the command."""

    def _ctx(self, channel, replies):
        async def send(content=None, **kwargs):
            replies.append(content)

        return SimpleNamespace(channel=channel, send=send, author=SimpleNamespace(id=USER_ID))

    def test_it_refuses_to_run_outside_a_direct_message(self):
        replies = []
        ctx = self._ctx(SimpleNamespace(id=4242), replies)
        cog = DMPurge(SimpleNamespace(user=SimpleNamespace(id=BOT_ID)))

        asyncio.run(DMPurge.dmpurge.callback(cog, ctx, None))

        self.assertEqual(len(replies), 1)
        self.assertIn("direct message", replies[0])

    def test_a_still_starting_bot_is_reported_instead_of_crashing(self):
        replies = []
        ctx = self._ctx(FakeDmChannel(), replies)
        cog = DMPurge(SimpleNamespace(user=None))

        with mock.patch.object(dm_purge.discord, "DMChannel", FakeDmChannel), \
             mock.patch.object(dm_purge, "count_bot_messages", _never_called):
            asyncio.run(DMPurge.dmpurge.callback(cog, ctx, None))

        self.assertEqual(len(replies), 1)
        self.assertIn("starting up", replies[0])


class CommandVisibilityTests(unittest.TestCase):
    """The command must not be discoverable anywhere a member can look."""

    def _bot(self):
        bot = commands.Bot(command_prefix=".", intents=discord.Intents.none())
        asyncio.run(bot.add_cog(DMPurge(bot)))
        return bot

    def test_dmpurge_is_hidden_and_prefix_only(self):
        command = self._bot().get_command("dmpurge")
        self.assertIsNotNone(command)
        self.assertTrue(command.hidden)
        # A hybrid command would also register with Discord's slash-command tree.
        self.assertNotIsInstance(command, commands.HybridCommand)
        self.assertFalse(command.aliases)

    def test_the_help_menu_has_no_category_for_it(self):
        listed = {name for names in help_views.CATEGORY_COGS.values() for name in names}
        self.assertNotIn("DMPurge", listed)

    def test_a_hidden_command_is_filtered_out_of_a_category_listing(self):
        class FakeCog:
            def get_commands(self):
                return [
                    SimpleNamespace(name="visible", hidden=False, help="Shown.", aliases=[]),
                    SimpleNamespace(name="dmpurge", hidden=True, help="Hidden.", aliases=[]),
                ]

        bot = SimpleNamespace(get_cog=lambda name: FakeCog(), command_prefix=".")
        content, _ = asyncio.run(help_views._commands_text(["Utility"], bot, None, 1))
        self.assertIn("visible", content)
        self.assertNotIn("dmpurge", content)


class RegistryFixture(commands.Cog):
    """One visible command beside one hidden command, as the registry sees them."""

    @commands.command(name="visible", help="A visible command.")
    async def visible(self, ctx):
        """A visible command."""

    @commands.command(name="dmpurge", hidden=True, help="Operator tooling.")
    async def dmpurge(self, ctx):
        """Operator tooling."""


class CommandRegistryTests(unittest.TestCase):
    """`data/commands.json` feeds the public commands page and its counts."""

    def _bot(self):
        bot = commands.Bot(command_prefix=".", intents=discord.Intents.none())
        asyncio.run(bot.add_cog(RegistryFixture(bot)))
        return bot

    def test_hidden_commands_never_reach_the_public_registry(self):
        bot = self._bot()
        previous = os.getcwd()
        with tempfile.TemporaryDirectory() as directory:
            os.chdir(directory)
            try:
                writers.write_commands(bot)
                written = json.loads(
                    Path("data/commands.json").read_text(encoding="utf-8")
                )
            finally:
                os.chdir(previous)

        names = [record["name"] for record in written]
        self.assertIn("visible", names)
        self.assertNotIn("dmpurge", names)
        # The status panel's command count follows the same registry.
        self.assertEqual(bot._status_command_count, len(names))


if __name__ == "__main__":
    unittest.main()
