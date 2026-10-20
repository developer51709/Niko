"""Giveaway bans: the commands, the Join guard and the draw.

A giveaway ban has to do three things to be worth the command: refuse the
member on the Join button, drop the entries they already hold, and keep them
out of the draw even when an entry survives. These tests run the real cog
against a real SQLite pool so the schema, the statements and the replies are
all exercised.

Run with:  .venv/bin/python -m pytest tests/test_giveaway_bans.py -v
"""

import asyncio
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import aiosqlite

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.giveaway import views as giveaway_views  # noqa: E402
from cogs.giveaway.cog import Giveaway  # noqa: E402
from cogs.giveaway.views import _GiveawayJoinBtn, _MgmtSelectBtn  # noqa: E402
from database import PRIMARY_KEYS, SQLitePool  # noqa: E402
from events.startup import database as database_setup  # noqa: E402

GUILD = 111
OTHER_GUILD = 222
ADMIN = 900
BANNED = 901
MEMBER = 902
CHANNEL_ID = 500
FUTURE = "2999-01-01T00:00:00+00:00"


class FakeResponse:
    def __init__(self):
        self.messages = []
        self.ephemeral = []
        self.edited = []

    async def send_message(self, content=None, *, ephemeral=False, **kwargs):
        self.messages.append(content)
        self.ephemeral.append(ephemeral)

    async def edit_message(self, *, view=None, **kwargs):
        self.edited.append(view)
        return view


def view_text(view) -> str:
    """Every TextDisplay rendered by a Components v2 view."""
    parts = []

    def walk(item):
        content = getattr(item, "content", None)
        if isinstance(content, str):
            parts.append(content)
        for child in getattr(item, "children", None) or []:
            walk(child)

    walk(view)
    return "\n".join(parts)


class FakeUser:
    def __init__(self, user_id, *, bot=False):
        self.id = user_id
        self.bot = bot
        self.display_name = f"user{user_id}"


class FakeInteraction:
    def __init__(self, *, guild_id, user, message_id):
        self.guild_id = guild_id
        self.guild = SimpleNamespace(id=guild_id, preferred_locale="en-US")
        self.user = user
        self.message = SimpleNamespace(id=message_id)
        self.response = FakeResponse()


class FakeCtx:
    def __init__(self, *, guild_id=GUILD, author_id=ADMIN):
        self.guild = SimpleNamespace(id=guild_id, preferred_locale="en-US")
        self.author = FakeUser(author_id)
        self.clean_prefix = "."
        self.sent = []
        self.views = []

    async def send(self, content=None, *, view=None, **kwargs):
        self.sent.append(content)
        if view is not None:
            self.views.append(view)
        return content


class FakeChannel:
    def __init__(self):
        self.sent = []

    async def fetch_message(self, message_id):
        raise RuntimeError("the giveaway message is gone")

    async def send(self, content=None, **kwargs):
        self.sent.append(content)


# The message catalogue reads the server's AI personality from the config
# database; the ban behaviour does not depend on it, so keep these tests off
# the config store and assert on the English copy.
def _personality(obj):
    return "normal"


async def _memory_connection():
    # aiosqlite's connect() is awaitable rather than a coroutine, so it cannot
    # be handed straight to asyncio.run().
    return await aiosqlite.connect(":memory:")


class GiveawayBanTests(unittest.TestCase):
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

    # ── helpers ──────────────────────────────────────────────

    def _add_giveaway(self, message_id, *, guild_id=GUILD, ended=0):
        asyncio.run(self.pool.execute(
            "INSERT INTO giveaways (message_id, channel_id, guild_id, prize, winners_count, "
            "end_time, ended, host_id, requirements) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)",
            message_id, CHANNEL_ID, guild_id, "Nitro", 1, FUTURE, ended, ADMIN, "{}",
        ))

    def _add_participant(self, message_id, user_id):
        asyncio.run(self.pool.execute(
            "INSERT INTO participants (message_id, user_id) VALUES ($1, $2)",
            message_id, user_id,
        ))

    def _participants(self, message_id):
        rows = asyncio.run(self.pool.fetch(
            "SELECT user_id FROM participants WHERE message_id = $1", message_id
        ))
        return sorted(int(row["user_id"]) for row in rows)

    def _ban_rows(self, guild_id=GUILD):
        return asyncio.run(self.pool.fetch(
            "SELECT * FROM giveaway_bans WHERE guild_id = $1", guild_id
        ))

    def _ban(self, member_id=BANNED, *, guild_id=GUILD):
        ctx = FakeCtx(guild_id=guild_id)
        with patch.object(giveaway_views, "get_personality", _personality):
            asyncio.run(Giveaway.ban.callback(self.cog, ctx, FakeUser(member_id)))
        return ctx

    def _unban(self, member_id=BANNED, *, guild_id=GUILD):
        ctx = FakeCtx(guild_id=guild_id)
        with patch.object(giveaway_views, "get_personality", _personality):
            asyncio.run(Giveaway.unban.callback(self.cog, ctx, FakeUser(member_id)))
        return ctx

    def _join(self, member_id, *, message_id=1000, guild_id=GUILD, bot=False):
        button = _GiveawayJoinBtn(self.bot, message_id)
        interaction = FakeInteraction(
            guild_id=guild_id, user=FakeUser(member_id, bot=bot), message_id=message_id
        )
        with patch.object(giveaway_views, "get_personality", _personality):
            asyncio.run(button.callback(interaction))
        return interaction

    def _end(self, message_id=1000, *, guild_id=GUILD):
        with patch.object(giveaway_views, "get_personality", _personality):
            asyncio.run(Giveaway.end_giveaway(
                self.cog, message_id, CHANNEL_ID, guild_id, "Nitro", 1, ADMIN,
            ))

    # ── command behaviour ────────────────────────────────────

    def test_both_commands_are_registered_on_the_giveaway_group(self):
        self.assertEqual(
            {command.name for command in Giveaway.giveaway.commands},
            {"start", "reroll", "ban", "unban"},
        )

    def test_the_help_card_names_the_ban_commands(self):
        ctx = FakeCtx()
        asyncio.run(Giveaway.giveaway.callback(self.cog, ctx))

        text = view_text(ctx.views[-1])
        self.assertIn("giveaway ban", text)
        self.assertIn("giveaway unban", text)

    def test_the_ban_table_is_part_of_the_mongo_primary_key_map(self):
        # The bans table is written through the same pool as the giveaways, so
        # MongoDB needs to know how a ban row is identified.
        self.assertEqual(PRIMARY_KEYS["giveaway_bans"], ("guild_id", "user_id"))

    def test_ban_records_the_ban_and_who_set_it(self):
        ctx = self._ban()

        rows = self._ban_rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(int(rows[0]["user_id"]), BANNED)
        self.assertEqual(int(rows[0]["banned_by"]), ADMIN)
        self.assertTrue(rows[0]["created_at"])
        self.assertIn("can no longer join giveaways", ctx.sent[-1])

    def test_ban_clears_the_entries_the_member_already_holds(self):
        self._add_giveaway(1000)
        self._add_giveaway(1001)
        self._add_participant(1000, BANNED)
        self._add_participant(1001, BANNED)
        self._add_participant(1000, MEMBER)

        ctx = self._ban()

        self.assertEqual(self._participants(1000), [MEMBER])
        self.assertEqual(self._participants(1001), [])
        # The reply has to say what the ban actually did.
        self.assertIn("**2**", ctx.sent[-1])

    def test_ban_leaves_ended_giveaways_and_other_servers_alone(self):
        self._add_giveaway(1002, ended=1)
        self._add_participant(1002, BANNED)
        self._add_giveaway(2000, guild_id=OTHER_GUILD)
        self._add_participant(2000, BANNED)

        ctx = self._ban()

        self.assertEqual(self._participants(1002), [BANNED])
        self.assertEqual(self._participants(2000), [BANNED])
        self.assertEqual(self._ban_rows(OTHER_GUILD), [])
        self.assertIn("**0**", ctx.sent[-1])

    def test_banning_twice_does_not_duplicate_the_row(self):
        self._ban()
        ctx = self._ban()

        self.assertEqual(len(self._ban_rows()), 1)
        self.assertIn("already banned", ctx.sent[-1])

    def test_a_bot_cannot_be_banned_from_giveaways(self):
        ctx = FakeCtx()
        with patch.object(giveaway_views, "get_personality", _personality):
            asyncio.run(Giveaway.ban.callback(self.cog, ctx, FakeUser(MEMBER, bot=True)))

        self.assertEqual(self._ban_rows(), [])
        self.assertIn("Bots cannot participate", ctx.sent[-1])

    def test_unban_lifts_the_ban(self):
        self._ban()
        ctx = self._unban()

        self.assertEqual(self._ban_rows(), [])
        self.assertIn("can join giveaways in this server again", ctx.sent[-1])

    def test_unbanning_a_member_who_is_not_banned_says_so(self):
        ctx = self._unban()

        self.assertIn("is not banned", ctx.sent[-1])

    # ── Join button ──────────────────────────────────────────

    def test_a_banned_member_cannot_join(self):
        self._add_giveaway(1000)
        self._ban()

        interaction = self._join(BANNED)

        self.assertEqual(self._participants(1000), [])
        self.assertIn("banned from joining giveaways", interaction.response.messages[0])
        self.assertTrue(interaction.response.ephemeral[0])

    def test_an_unbanned_member_can_join_again(self):
        self._add_giveaway(1000)
        self._ban()
        self._unban()

        self._join(BANNED)

        self.assertEqual(self._participants(1000), [BANNED])

    def test_a_ban_in_another_server_does_not_block_this_one(self):
        self._add_giveaway(1000)
        self._ban(guild_id=OTHER_GUILD)

        self._join(BANNED)

        self.assertEqual(self._participants(1000), [BANNED])

    # ── draws ────────────────────────────────────────────────

    def test_the_draw_never_picks_a_banned_member(self):
        self._add_giveaway(1000)
        self._add_participant(1000, BANNED)
        self._add_participant(1000, MEMBER)
        self._ban()

        self._end()

        announcement = self.channel.sent[-1]
        self.assertIn(f"<@{MEMBER}>", announcement)
        self.assertNotIn(f"<@{BANNED}>", announcement)

    def test_a_manual_selection_cannot_pick_a_banned_member(self):
        self._add_giveaway(1000)
        self._add_participant(1000, BANNED)
        self._add_participant(1000, MEMBER)
        self._ban()

        button = _MgmtSelectBtn(self.bot, 1000)
        interaction = FakeInteraction(guild_id=GUILD, user=FakeUser(ADMIN), message_id=1000)
        with patch.object(giveaway_views, "get_personality", _personality):
            asyncio.run(button.callback(interaction))

        text = view_text(interaction.response.edited[-1])
        self.assertIn(f"<@{MEMBER}>", text)
        self.assertNotIn(f"<@{BANNED}>", text)

    def test_a_manual_selection_with_only_banned_entries_reports_no_entries(self):
        self._add_giveaway(1000)
        self._add_participant(1000, BANNED)
        # The entry survives on purpose: only the filter stands between a
        # banned member and a manually selected win.
        asyncio.run(self.pool.execute(
            "INSERT INTO giveaway_bans (guild_id, user_id, banned_by, created_at) "
            "VALUES ($1, $2, $3, $4)",
            GUILD, BANNED, ADMIN, "2026-10-20T00:00:00+00:00",
        ))

        button = _MgmtSelectBtn(self.bot, 1000)
        interaction = FakeInteraction(guild_id=GUILD, user=FakeUser(ADMIN), message_id=1000)
        with patch.object(giveaway_views, "get_personality", _personality):
            asyncio.run(button.callback(interaction))

        text = view_text(interaction.response.edited[-1])
        self.assertIn("Nobody has entered", text)
        self.assertNotIn(f"<@{BANNED}>", text)

    def test_an_entry_that_survives_the_ban_still_cannot_win(self):
        """Ban stamped while the giveaway was ending: the draw must still skip it."""
        self._add_giveaway(1000)
        self._add_participant(1000, BANNED)
        # Written straight to the pool on purpose — this is the race where the
        # entry exists even though the ban already does.
        asyncio.run(self.pool.execute(
            "INSERT INTO giveaway_bans (guild_id, user_id, banned_by, created_at) "
            "VALUES ($1, $2, $3, $4)",
            GUILD, BANNED, ADMIN, "2026-10-20T00:00:00+00:00",
        ))

        self._end()

        self.assertIn("nobody participated", self.channel.sent[-1])
        self.assertNotIn(f"<@{BANNED}>", self.channel.sent[-1])


if __name__ == "__main__":
    unittest.main()
