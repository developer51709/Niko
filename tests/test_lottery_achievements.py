"""Lottery badges: tickets bought and draws won.

``lottery_tickets`` is reset by every weekly draw, so the badges cannot read it.
These tests pin the lifetime counters that back them, from the purchase and the
draw that move the counters through to the persisted row and the dashboard
catalogue.

Run with:  .venv/bin/python -m pytest tests/test_lottery_achievements.py -v
"""

import asyncio
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import aiosqlite

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.economy.cog import EconomyCog  # noqa: E402
from cogs.economy.data import (  # noqa: E402
    ACHIEVEMENTS,
    _default_user,
    _get_user_from_db,
    _migrate_user,
    _save_user_to_db,
    achievement_progress,
)
from database import SQLitePool  # noqa: E402
from events.startup import database as database_setup  # noqa: E402
from utils.economy_jobs import LOTTERY_HOUSE_RAKE, LOTTERY_TICKET_PRICE  # noqa: E402
from webapp.economy_routes import _ACCOUNT_COLUMNS, achievement_entries  # noqa: E402

USER = 42
POT = 10_000


def view_text(view) -> str:
    """Every TextDisplay rendered by a Components v2 view."""
    parts = []

    def walk(component):
        content = getattr(component, "content", None)
        if isinstance(content, str):
            parts.append(content)
        for child in getattr(component, "children", None) or []:
            walk(child)

    walk(view)
    return "\n".join(parts)


class FakeCtx:
    def __init__(self, user_id=USER):
        self.author = SimpleNamespace(id=user_id, display_name="tester", bot=False)
        self.guild = SimpleNamespace(id=1, preferred_locale="en-US")
        self.clean_prefix = "."
        self.interaction = None
        self.sent = []

    async def send(self, content=None, *, view=None, **kwargs):
        self.sent.append(view if view is not None else content)
        return self


async def _memory_connection():
    return await aiosqlite.connect(":memory:")


class LotteryBadgeTests(unittest.TestCase):
    def setUp(self):
        self.connection = asyncio.run(_memory_connection())
        self.pool = SQLitePool(self.connection)
        self.bot = SimpleNamespace(cxn=self.pool, get_user=lambda user_id: None)
        asyncio.run(database_setup._create_tables(self.bot))
        self.cog = EconomyCog.__new__(EconomyCog)
        self.cog.bot = self.bot
        self.cog.economy_data = {}
        self.cog.lottery = {"pot": POT, "next_draw": 0, "last_winner": None, "last_pot": 0}

    def tearDown(self):
        asyncio.run(self.connection.close())

    # ── helpers ──────────────────────────────────────────────

    def _account(self, **overrides):
        data = _migrate_user(_default_user())
        data.update(overrides)
        asyncio.run(_save_user_to_db(self.bot, USER, data))
        return data

    def _load(self):
        return asyncio.run(_get_user_from_db(self.bot, USER))

    def _buy(self, count):
        ctx = FakeCtx()
        asyncio.run(EconomyCog.lottery_buy.callback(self.cog, ctx, count))
        return ctx

    def _draw(self):
        asyncio.run(self.pool.execute(
            "UPDATE economy_lottery SET pot = $1, next_draw = $2 WHERE id = 1", POT, 1
        ))
        asyncio.run(EconomyCog._maybe_draw_lottery(self.cog))

    # ── the badges exist and measure the counters ────────────

    def test_the_lottery_badges_measure_lifetime_counters(self):
        for achievement_id, counter, target in (
            ("lottery_first_ticket", "lottery_tickets_bought", 1),
            ("lottery_tickets_25", "lottery_tickets_bought", 25),
            ("lottery_tickets_100", "lottery_tickets_bought", 100),
            ("lottery_tickets_500", "lottery_tickets_bought", 500),
            ("lottery_win_first", "lottery_wins", 1),
            ("lottery_wins_3", "lottery_wins", 3),
            ("lottery_wins_10", "lottery_wins", 10),
        ):
            with self.subTest(achievement=achievement_id):
                meta = ACHIEVEMENTS[achievement_id]
                current, reported_target = achievement_progress(meta, {counter: target // 2 if target > 1 else 0})
                self.assertEqual(reported_target, target)
                self.assertLess(current, target)
                self.assertTrue(meta["test"]({counter: target}))
                self.assertFalse(meta["test"]({counter: target - 1}))

    def test_a_ticket_reset_does_not_erase_badge_progress(self):
        # A draw zeroes the weekly ticket count but not the lifetime counter.
        data = self._account(balance=1_000, lottery_tickets=0, lottery_tickets_bought=24)
        self.assertEqual(achievement_progress(ACHIEVEMENTS["lottery_tickets_25"], data)[0], 24)

    # ── buying ───────────────────────────────────────────────

    def test_buying_a_ticket_moves_the_counter_and_pays_the_badge(self):
        self._account(balance=500)

        ctx = self._buy(1)

        data = self._load()
        self.assertEqual(data["lottery_tickets"], 1)
        self.assertEqual(data["lottery_tickets_bought"], 1)
        self.assertIn("lottery_first_ticket", data["achievements"])
        # Price paid, then the badge reward on the same save.
        self.assertEqual(
            data["balance"],
            500 - LOTTERY_TICKET_PRICE + int(ACHIEVEMENTS["lottery_first_ticket"]["reward"]),
        )
        self.assertIn("New achievements", view_text(ctx.sent[-1]))

    def test_a_bonus_ticket_does_not_count_as_a_purchased_ticket(self):
        self._account(balance=5_000, effects={"lottery_boost": 1})

        self._buy(2)

        data = self._load()
        self.assertEqual(data["lottery_tickets"], 4)      # paid for 2, held 4
        self.assertEqual(data["lottery_tickets_bought"], 2)

    def test_buying_enough_tickets_reaches_the_next_rung(self):
        self._account(balance=100_000, lottery_tickets_bought=24)

        self._buy(1)

        data = self._load()
        self.assertEqual(data["lottery_tickets_bought"], 25)
        self.assertIn("lottery_tickets_25", data["achievements"])

    # ── winning ──────────────────────────────────────────────

    def test_winning_a_draw_moves_the_win_counter_and_pays_the_badge(self):
        # worth_1k is pre-earned so the only new badge at the draw is the win.
        data = self._account(balance=100, lottery_tickets=3, achievements=["worth_1k"])
        asyncio.run(self.pool.execute(
            "UPDATE economy_users SET lottery_tickets = $1 WHERE user_id = $2", 3, USER
        ))

        self._draw()

        after = self._load()
        payout = int(POT * (1 - LOTTERY_HOUSE_RAKE))
        self.assertEqual(after["lottery_wins"], 1)
        self.assertIn("lottery_win_first", after["achievements"])
        self.assertEqual(
            after["balance"],
            100 + payout + int(ACHIEVEMENTS["lottery_win_first"]["reward"]),
        )
        # The weekly tickets the draw consumed are gone; the lifetime counters stay.
        self.assertEqual(after["lottery_tickets"], 0)
        self.assertGreaterEqual(after["lottery_tickets_bought"], 0)

    def test_the_draw_announcement_names_the_badges_the_winner_earned(self):
        sent = []

        class Channel:
            async def send(self, view=None, **kwargs):
                sent.append(view_text(view))

        async def channel():
            return Channel()

        self.cog._lottery_channel = channel
        asyncio.run(EconomyCog._announce_lottery_draw(
            self.cog, winner_name="tester", payout=9_000, tickets=3, entrants=1,
            unlocked=["Lucky Winner 🍀 (+2,500 🪙)"],
        ))

        self.assertTrue(sent)
        self.assertIn("tester", sent[0])
        self.assertIn("Lucky Winner", sent[0])

    # ── persistence ──────────────────────────────────────────

    def test_the_counters_round_trip_through_the_database(self):
        columns = [str(row["name"]) for row in asyncio.run(self.pool.fetch("PRAGMA table_info(economy_users)"))]
        self.assertIn("lottery_tickets_bought", columns)
        self.assertIn("lottery_wins", columns)

        self._account(lottery_tickets_bought=17, lottery_wins=4)
        data = self._load()

        self.assertEqual(data["lottery_tickets_bought"], 17)
        self.assertEqual(data["lottery_wins"], 4)

    def test_an_existing_database_gains_the_counter_columns(self):
        """Upgrading must add the counters to a table that predates them."""

        async def scenario():
            connection = await _memory_connection()
            try:
                pool = SQLitePool(connection)
                bot = SimpleNamespace(cxn=pool)
                await database_setup._create_tables(bot)
                await connection.execute("ALTER TABLE economy_users DROP COLUMN lottery_tickets_bought")
                await connection.execute("ALTER TABLE economy_users DROP COLUMN lottery_wins")
                await connection.commit()

                await database_setup._create_tables(bot)
                rows = await pool.fetch("PRAGMA table_info(economy_users)")
                return [str(row["name"]) for row in rows]
            finally:
                await connection.close()

        columns = asyncio.run(scenario())
        self.assertIn("lottery_tickets_bought", columns)
        self.assertIn("lottery_wins", columns)

    def test_a_legacy_account_without_the_counters_starts_at_zero(self):
        data = _migrate_user({"balance": 100})

        self.assertEqual(data["lottery_tickets_bought"], 0)
        self.assertEqual(data["lottery_wins"], 0)

    # ── dashboard ────────────────────────────────────────────

    def test_the_dashboard_reads_the_counters_for_the_bars(self):
        self.assertIn("lottery_tickets_bought", _ACCOUNT_COLUMNS)
        self.assertIn("lottery_wins", _ACCOUNT_COLUMNS)

        entries = {entry["id"]: entry for entry in achievement_entries(
            {"achievements": [], "lottery_tickets_bought": 30, "lottery_wins": 0}
        )}
        self.assertEqual(entries["lottery_tickets_25"]["progress"]["percent"], 100)
        self.assertEqual(entries["lottery_tickets_100"]["progress"]["current"], 30)
        self.assertEqual(entries["lottery_win_first"]["progress"]["current"], 0)


if __name__ == "__main__":
    unittest.main()
