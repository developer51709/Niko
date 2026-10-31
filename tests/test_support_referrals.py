"""Support-server referrals: the OAuth join, attribution and the payout.

A referral link is ``/discord?ref=<id>``; the site adds the visitor to the
support server through their own Discord account, and Discord reports the add
back to the bot. That is what makes the join checkable without minting an invite
per member — Discord caps how many invites a guild may hold, and an invite carry
no identity to attribute.

These tests drive the real schema (an in-memory SQLite pool with the tables the
bot creates at startup), so a column the payout writes has to exist for the
reward to land.
"""

import asyncio
import json
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import aiosqlite
import discord

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from database import SQLitePool  # noqa: E402
from events.startup import database as database_setup  # noqa: E402
from cogs.economy.data import ACHIEVEMENTS  # noqa: E402
from cogs.economy.referrals import REFERRAL_REWARD, pay_referral  # noqa: E402
from cogs.staff import support_referrals  # noqa: E402
from webapp import app as webapp_app  # noqa: E402
from webapp.routes import referral_routes, site_routes  # noqa: E402

# The guild the referral module is hard-wired to: the support server.
SUPPORT_GUILD = support_referrals.SUPPORT_GUILD
SUPPORT_INVITE = "https://discord.gg/niko"


def not_found() -> discord.NotFound:
    """The error Discord returns for a user who is not in the guild."""
    return discord.NotFound(
        SimpleNamespace(status=404, reason="Not Found"),
        {"code": 10007, "message": "Unknown Member"},
    )


class FakeGuild:
    def __init__(self):
        self.id = SUPPORT_GUILD
        self.members = {}

    def get_member(self, user_id):
        return self.members.get(int(user_id))

    async def fetch_member(self, user_id):
        member = self.members.get(int(user_id))
        if member is None:
            raise not_found()
        return member


class FakeBot:
    """A bot whose add-member call can succeed, refuse, or actually add."""

    def __init__(self, pool, guild, error=None, add_to_guild=False):
        self.cxn = pool
        self._guild = guild
        self._error = error
        self._add_to_guild = add_to_guild
        self.http = SimpleNamespace(request=mock.AsyncMock(side_effect=self._request))

    async def _request(self, route, json=None):
        if self._error is not None:
            raise self._error
        if self._add_to_guild:
            user_id = int(route.url.rsplit("/", 1)[-1])
            self._guild.members[user_id] = SimpleNamespace(id=user_id)
        return None

    def get_guild(self, guild_id):
        return self._guild if int(guild_id) == SUPPORT_GUILD else None


class ReferralTestCase(unittest.TestCase):
    def run_scenario(self, scenario):
        """Run *scenario* against a fresh in-memory database and a fake guild."""

        async def wrapper():
            connection = await aiosqlite.connect(":memory:")
            try:
                pool = SQLitePool(connection)
                return await scenario(pool)
            finally:
                await connection.close()

        return asyncio.run(wrapper())


class JoinTests(ReferralTestCase):
    def test_a_referral_join_adds_the_member_with_their_token_and_pays(self):
        async def scenario(pool):
            guild = FakeGuild()
            bot = FakeBot(pool, guild)
            await database_setup._create_tables(bot)

            result = await support_referrals.join_with_referral(bot, 500, 100, "user-token")
            account = await pool.fetchrow("SELECT * FROM economy_users WHERE user_id = ?", 100)
            joins = await pool.fetch("SELECT * FROM support_referral_joins")
            return result, account, joins, bot.http.request.await_args

        result, account, joins, call = self.run_scenario(scenario)
        self.assertEqual(result["status"], "joined")
        self.assertTrue(result["credited"])
        self.assertEqual(result["referrer_id"], 100)
        self.assertEqual(result["reward"], REFERRAL_REWARD)

        # The member is added by Discord using *their* token, and no invite is
        # created for them.
        route = call.args[0]
        self.assertEqual(route.method, "PUT")
        self.assertEqual(
            route.url, f"https://discord.com/api/v10/guilds/{SUPPORT_GUILD}/members/500"
        )
        self.assertEqual(call.kwargs["json"], {"access_token": "user-token"})

        self.assertEqual(int(account["referral_count"]), 1)
        stored = json.loads(account["achievements"]) if isinstance(account["achievements"], str) else account["achievements"]
        self.assertIn("referral_first", stored)
        # The referral pays, and the badge it unlocks pays its own reward on top.
        self.assertEqual(
            int(account["balance"]),
            100 + REFERRAL_REWARD + ACHIEVEMENTS["referral_first"]["reward"],
        )
        self.assertEqual(len(joins), 1)
        self.assertEqual(int(joins[0]["reward"]), REFERRAL_REWARD)

    def test_a_member_is_added_once_and_a_second_click_pays_nothing(self):
        async def scenario(pool):
            guild = FakeGuild()
            bot = FakeBot(pool, guild, add_to_guild=True)
            await database_setup._create_tables(bot)
            first = await support_referrals.join_with_referral(bot, 500, 100, "user-token")
            second = await support_referrals.join_with_referral(bot, 500, 100, "user-token")
            account = await pool.fetchrow("SELECT * FROM economy_users WHERE user_id = ?", 100)
            joins = await pool.fetch("SELECT * FROM support_referral_joins")
            return first, second, account, joins

        first, second, account, joins = self.run_scenario(scenario)
        self.assertTrue(first["credited"])
        # They are in the server now, so the second click has nothing to add.
        self.assertEqual(second["status"], "already_member")
        self.assertNotIn("credited", second)
        self.assertEqual(int(account["referral_count"]), 1)
        self.assertEqual(len(joins), 1)

    def test_somebody_already_in_the_server_earns_the_referrer_nothing(self):
        async def scenario(pool):
            guild = FakeGuild()
            guild.members[500] = SimpleNamespace(id=500)
            bot = FakeBot(pool, guild)
            await database_setup._create_tables(bot)
            result = await support_referrals.join_with_referral(bot, 500, 100, "user-token")
            joins = await pool.fetch("SELECT * FROM support_referral_joins")
            return result, joins, bot

        result, joins, bot = self.run_scenario(scenario)
        self.assertEqual(result["status"], "already_member")
        self.assertEqual(joins, [])
        # Nothing was attempted, so an existing member can never be back-credited
        # by clicking a friend's link.
        bot.http.request.assert_not_awaited()

    def test_a_self_referral_still_joins_but_pays_nobody(self):
        async def scenario(pool):
            guild = FakeGuild()
            bot = FakeBot(pool, guild)
            await database_setup._create_tables(bot)
            result = await support_referrals.join_with_referral(bot, 500, 500, "user-token")
            joins = await pool.fetch("SELECT * FROM support_referral_joins")
            account = await pool.fetchrow("SELECT * FROM economy_users WHERE user_id = ?", 500)
            return result, joins, account

        result, joins, account = self.run_scenario(scenario)
        self.assertEqual(result["status"], "joined")
        self.assertNotIn("credited", result)
        self.assertEqual(joins, [])
        self.assertIsNone(account)

    def test_a_refused_add_credits_nobody(self):
        async def scenario(pool):
            guild = FakeGuild()
            bot = FakeBot(
                pool, guild,
                error=discord.Forbidden(SimpleNamespace(status=403, reason="Forbidden"), {
                    "code": 50001, "message": "Missing Access",
                }),
            )
            await database_setup._create_tables(bot)
            result = await support_referrals.join_with_referral(bot, 500, 100, "stale-token")
            joins = await pool.fetch("SELECT * FROM support_referral_joins")
            return result, joins

        result, joins = self.run_scenario(scenario)
        self.assertEqual(result["status"], "not_added")
        self.assertEqual(joins, [])

    def test_a_member_already_in_the_ledger_is_never_paid_twice(self):
        async def scenario(pool):
            guild = FakeGuild()
            bot = FakeBot(pool, guild)
            await database_setup._create_tables(bot)
            await pool.execute(
                "INSERT INTO support_referral_joins (member_id, referrer_id, joined_at, reward) "
                "VALUES (?, ?, ?, ?)",
                500, 100, 1_700_000_000, REFERRAL_REWARD,
            )
            result = await support_referrals.join_with_referral(bot, 500, 777, "user-token")
            joins = await pool.fetch("SELECT * FROM support_referral_joins")
            return result, joins

        result, joins = self.run_scenario(scenario)
        self.assertEqual(result["status"], "joined")
        self.assertNotIn("credited", result)
        self.assertEqual(len(joins), 1)
        # The first referrer keeps the credit; a later link cannot steal it.
        self.assertEqual(int(joins[0]["referrer_id"]), 100)

    def test_without_a_guild_or_database_nothing_happens(self):
        async def scenario(pool):
            await database_setup._create_tables(FakeBot(pool, FakeGuild()))
            no_guild = FakeBot(pool, None)
            no_env = SimpleNamespace(cxn=None, get_guild=lambda gid: FakeGuild())
            return (
                await support_referrals.join_with_referral(no_guild, 500, 100, "token"),
                await support_referrals.join_with_referral(no_env, 500, 100, "token"),
                await support_referrals.join_with_referral(FakeBot(pool, FakeGuild()), "x", 100, "t"),
            )

        self.assertEqual([item["status"] for item in self.run_scenario(scenario)], ["unavailable"] * 3)

    def test_the_referral_badges_read_the_stored_counter(self):
        async def scenario(pool):
            bot = FakeBot(pool, FakeGuild())
            await database_setup._create_tables(bot)
            for member_id in range(1, 6):
                await pay_referral(bot, 700, member_id)
            return await pool.fetchrow("SELECT * FROM economy_users WHERE user_id = ?", 700)

        account = self.run_scenario(scenario)
        self.assertEqual(int(account["referral_count"]), 5)
        stored = json.loads(account["achievements"]) if isinstance(account["achievements"], str) else account["achievements"]
        unlocked = {name for name in stored if name.startswith("referral_")}
        self.assertEqual(unlocked, {"referral_first", "referral_5"})

    def test_the_badge_table_has_a_referral_set(self):
        badges = [name for name in ACHIEVEMENTS if name.startswith("referral_")]
        self.assertEqual(badges, ["referral_first", "referral_5", "referral_15", "referral_50"])
        for name in badges:
            with self.subTest(badge=name):
                self.assertTrue(ACHIEVEMENTS[name]["description"])
                self.assertGreater(ACHIEVEMENTS[name]["reward"], 0)

    def test_the_standing_counts_only_paid_referrals(self):
        async def scenario(pool):
            bot = FakeBot(pool, FakeGuild())
            await database_setup._create_tables(bot)
            await pool.execute(
                "INSERT INTO support_referral_joins (member_id, referrer_id, joined_at, reward) "
                "VALUES (?, ?, ?, ?)",
                1, 900, 100, REFERRAL_REWARD,
            )
            await pool.execute(
                "INSERT INTO support_referral_joins (member_id, referrer_id, joined_at, reward) "
                "VALUES (?, ?, ?, ?)",
                2, 900, 200, REFERRAL_REWARD,
            )
            return await support_referrals.referral_standing(bot, 900)

        standing = self.run_scenario(scenario)
        self.assertEqual(standing["invited"], 2)
        self.assertEqual(standing["coins"], REFERRAL_REWARD * 2)
        self.assertEqual([entry["member_id"] for entry in standing["recent"]], ["2", "1"])


class ReferralRouteTests(unittest.TestCase):
    """The dashboard card is fed by ``/api/me/referrals``."""

    def signed_in_client(self):
        client = webapp_app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": "42", "username": "Tester"}
            session["access_token"] = "token"
            session["token_exp"] = time.time() + 3600
        return client

    def test_the_route_rejects_anonymous_reads(self):
        response = webapp_app.test_client().get("/api/me/referrals")
        self.assertEqual(response.status_code, 401)

    def test_without_a_live_bot_the_link_is_still_shareable(self):
        client = self.signed_in_client()
        with mock.patch.object(referral_routes, "_discord_bot", None):
            payload = client.get("/api/me/referrals").get_json()
        self.assertEqual(payload["link"], "https://niko.sryze.cc/discord?ref=42")
        self.assertEqual(payload["invited"], 0)
        self.assertEqual(payload["coins"], 0)
        self.assertEqual(payload["reward"], REFERRAL_REWARD)
        self.assertEqual(payload["recent"], [])

    def test_the_route_reports_the_standing_the_bot_holds(self):
        client = self.signed_in_client()
        bot = FakeBot(SimpleNamespace(), FakeGuild())

        async def standing(_bot, _user_id):
            return {
                "invited": 2,
                "coins": REFERRAL_REWARD * 2,
                "recent": [{"member_id": "500", "joined_at": 1_700_000_000, "reward": REFERRAL_REWARD}],
            }

        with mock.patch.object(referral_routes, "_discord_bot", bot), \
             mock.patch.object(referral_routes, "run_on_bot_loop", side_effect=lambda task: asyncio.run(task)), \
             mock.patch.object(referral_routes, "referral_standing", new=standing):
            payload = client.get("/api/me/referrals").get_json()
        self.assertEqual(payload["invited"], 2)
        self.assertEqual(payload["coins"], REFERRAL_REWARD * 2)
        self.assertEqual(payload["recent"][0]["member_id"], "500")
        # A member the bot no longer shares a guild with keeps their row.
        self.assertIsNone(payload["recent"][0]["name"])


class DiscordReferralLinkTests(unittest.TestCase):
    """``/discord?ref=<id>`` has to run the join, not hand out an invite."""

    def client_with_session(self, scopes=("identify", "guilds", "guilds.join")):
        client = webapp_app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": "42", "username": "Tester"}
            session["access_token"] = "user-token"
            session["refresh_token"] = "refresh"
            session["token_exp"] = time.time() + 3600
            session["oauth_scopes"] = list(scopes)
        return client

    def test_an_anonymous_visitor_is_asked_to_authorize_first(self):
        client = webapp_app.test_client()
        bot = FakeBot(SimpleNamespace(), FakeGuild())
        with mock.patch.object(site_routes, "_discord_bot", bot):
            response = client.get("/discord?ref=42")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/auth/login?next=%2Fdiscord%3Fref%3D42",
        )

    def test_a_session_without_the_join_scope_is_sent_through_discord_once(self):
        client = self.client_with_session(scopes=("identify", "guilds"))
        bot = FakeBot(SimpleNamespace(), FakeGuild())
        with mock.patch.object(site_routes, "_discord_bot", bot):
            response = client.get("/discord?ref=42")
        self.assertEqual(response.headers["Location"], "/auth/login?next=%2Fdiscord%3Fref%3D42")

    def test_a_signed_in_click_joins_through_the_bot_and_lands_on_the_invite(self):
        client = self.client_with_session()
        bot = FakeBot(SimpleNamespace(), FakeGuild())
        join = mock.AsyncMock(return_value={"status": "joined", "credited": True})
        with mock.patch.object(site_routes, "_discord_bot", bot), \
             mock.patch.object(site_routes, "run_on_bot_loop", side_effect=lambda task: asyncio.run(task)), \
             mock.patch.object(support_referrals, "join_with_referral", new=join), \
             mock.patch("cogs.staff.support_server.get_support_invite", new=mock.AsyncMock(return_value=SUPPORT_INVITE)):
            response = client.get("/discord?ref=42")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], SUPPORT_INVITE)
        join.assert_awaited_once_with(bot, 42, 42, "user-token")

    def test_a_refused_join_still_sends_the_visitor_to_the_server(self):
        client = self.client_with_session()
        bot = FakeBot(SimpleNamespace(), FakeGuild())
        join = mock.AsyncMock(return_value={"status": "not_added"})
        with mock.patch.object(site_routes, "_discord_bot", bot), \
             mock.patch.object(site_routes, "run_on_bot_loop", side_effect=lambda task: asyncio.run(task)), \
             mock.patch.object(support_referrals, "join_with_referral", new=join), \
             mock.patch("cogs.staff.support_server.get_support_invite", new=mock.AsyncMock(return_value=SUPPORT_INVITE)):
            response = client.get("/discord?ref=42")
        # No loop back through Discord: they get the public invite.
        self.assertEqual(response.headers["Location"], SUPPORT_INVITE)

    def test_the_plain_link_serves_the_page(self):
        client = webapp_app.test_client()
        bot = FakeBot(SimpleNamespace(), FakeGuild())
        with mock.patch.object(site_routes, "_discord_bot", bot):
            for path in ("/discord", "/discord?ref=not-a-snowflake"):
                with self.subTest(path=path):
                    response = client.get(path)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b"Niko support server", response.data)


if __name__ == "__main__":
    unittest.main()
