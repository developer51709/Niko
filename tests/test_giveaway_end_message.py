"""The end-of-giveaway message has to hand the host a copy-ready reroll command.

Most members do not know how to copy a message id, so the draw announcement ends
with `.giveaway reroll <message_id>` already spelled out — using the server's own
prefix, because a hint with the wrong prefix is as useless as no hint.

Run with:  .venv/bin/python -m pytest tests/test_giveaway_end_message.py -v
"""

import asyncio
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import aiosqlite

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.giveaway import cog as giveaway_cog  # noqa: E402
from cogs.giveaway import views as giveaway_views  # noqa: E402
from cogs.giveaway.cog import Giveaway  # noqa: E402
from database import SQLitePool  # noqa: E402
from events.startup import database as database_setup  # noqa: E402

GUILD = 111
ADMIN = 900
MEMBER = 902
CHANNEL_ID = 500
MESSAGE_ID = 1234567890123456789
FUTURE = "2999-01-01T00:00:00+00:00"


class FakeChannel:
    def __init__(self):
        self.sent = []

    async def fetch_message(self, message_id):
        raise RuntimeError("the giveaway message is gone")

    async def send(self, content=None, **kwargs):
        self.sent.append(content)


def _personality(obj):
    return "normal"


async def _memory_connection():
    return await aiosqlite.connect(":memory:")


class GiveawayEndMessageTests(unittest.TestCase):
    def setUp(self):
        self.connection = asyncio.run(_memory_connection())
        self.pool = SQLitePool(self.connection)
        self.channel = FakeChannel()
        self.bot = SimpleNamespace(
            cxn=self.pool,
            get_channel=lambda channel_id: self.channel,
            get_guild=lambda guild_id: SimpleNamespace(id=guild_id, preferred_locale="en-US"),
            add_view=lambda *args, **kwargs: None,
        )
        asyncio.run(database_setup._create_tables(self.bot))
        self.cog = Giveaway.__new__(Giveaway)
        self.cog.bot = self.bot
        asyncio.run(Giveaway.cog_load(self.cog))

    def tearDown(self):
        asyncio.run(self.connection.close())

    def _add_giveaway(self):
        asyncio.run(self.pool.execute(
            "INSERT INTO giveaways (message_id, channel_id, guild_id, prize, winners_count, "
            "end_time, ended, host_id, requirements) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)",
            MESSAGE_ID, CHANNEL_ID, GUILD, "Nitro", 1, FUTURE, 0, ADMIN, "{}",
        ))

    def _add_participant(self, user_id=MEMBER):
        asyncio.run(self.pool.execute(
            "INSERT INTO participants (message_id, user_id) VALUES ($1, $2)",
            MESSAGE_ID, user_id,
        ))

    def _set_prefixes(self, prefixes):
        asyncio.run(self.pool.execute(
            "INSERT OR REPLACE INTO prefix_config (guild_id, prefixes) VALUES ($1, $2)",
            GUILD, json.dumps(prefixes),
        ))

    def _end(self):
        with patch.object(giveaway_views, "get_personality", _personality):
            asyncio.run(Giveaway.end_giveaway(
                self.cog, MESSAGE_ID, CHANNEL_ID, GUILD, "Nitro", 1, ADMIN,
            ))
        return self.channel.sent[-1]

    def test_the_announcement_carries_the_copy_ready_reroll_command(self):
        self._add_giveaway()
        self._add_participant()

        announcement = self._end()

        self.assertIn(f"`.giveaway reroll {MESSAGE_ID}`", announcement)
        self.assertIn(f"<@{MEMBER}>", announcement)

    def test_the_hint_uses_the_servers_own_prefix(self):
        self._add_giveaway()
        self._add_participant()
        self._set_prefixes(["!", "?"])

        announcement = self._end()

        self.assertIn(f"`!giveaway reroll {MESSAGE_ID}`", announcement)
        self.assertNotIn(f"`.giveaway reroll {MESSAGE_ID}`", announcement)

    def test_a_prefix_lookup_failure_falls_back_to_the_default(self):
        self._add_giveaway()
        self._add_participant()

        with patch.object(giveaway_cog, "get_prefixes", side_effect=RuntimeError("db down")):
            announcement = self._end()

        # The draw still announces, with a hint that works on a stock install.
        self.assertIn(f"`.giveaway reroll {MESSAGE_ID}`", announcement)

    def test_a_giveaway_nobody_entered_gets_no_reroll_hint(self):
        self._add_giveaway()

        announcement = self._end()

        self.assertIn("nobody", announcement.lower())
        self.assertNotIn("reroll", announcement.lower())


if __name__ == "__main__":
    unittest.main()
