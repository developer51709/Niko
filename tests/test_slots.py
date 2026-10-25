"""Slots: the paytable and the wager accounting.

The slots command used to move ``user_data["balance"]`` on its own, which kept
the spin out of the transaction ledger: the dashboard's recent activity card
never showed a spin, ``total_earned``/``total_spent`` ignored it, and a win
credited the payout while the stake was never recorded. These tests pin the
fixed behaviour: every spin settles as one net result through
``EconomyCog.record_gamble``, so a winning spin is ``payout - bet`` and a losing
spin is ``-bet``.

Run with:  python -m pytest tests/test_slots.py -v
"""

import asyncio
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.casino import slots as slots_module  # noqa: E402
from cogs.casino.slots import Slots, evaluate_grid  # noqa: E402
from cogs.economy.cog import EconomyCog  # noqa: E402
from utils.cooldown import cooldown_ready_at  # noqa: E402

BET = 100


def account(**overrides):
    data = {
        "balance": 1000,
        "total_earned": 0,
        "total_spent": 0,
        "transactions": [],
        "achievements": [],
        "last_slots": 0,
    }
    data.update(overrides)
    return data


def grid_of(symbol):
    return [[symbol for _ in range(3)] for _ in range(3)]


def mixed_grid():
    return [
        ["🍒", "🍋", "🍊"],
        ["🍎", "🍇", "🍐"],
        ["💎", "🔥", "🪙"],
    ]


def one_line_grid(symbol):
    """A grid whose only payline is the middle row."""
    return [
        ["🍋", "🍊", "🍎"],
        [symbol, symbol, symbol],
        ["🍇", "🍐", "💎"],
    ]


class FakeEconomy:
    """The economy surface the casino cogs use, backed by the real ledger.

    ``record_gamble``/``_credit`` are the real cog methods, so a test asserts on
    the same transaction-log and total bookkeeping the dashboard reads.
    """

    record_gamble = EconomyCog.record_gamble
    _credit = EconomyCog._credit

    def __init__(self, data):
        self.data = data
        self.saves = 0

    async def get_user_economy_data(self, user_id):
        return self.data

    async def save_user_economy_data(self, user_id):
        self.saves += 1


class FakeMessage:
    def __init__(self):
        self.edits = []

    async def edit(self, **kwargs):
        self.edits.append(kwargs)
        return self


class FakeCtx:
    def __init__(self, user_id=42):
        self.author = SimpleNamespace(id=user_id)
        self.sent = []

    async def send(self, *args, **kwargs):
        message = FakeMessage()
        self.sent.append((args, kwargs, message))
        return message


class FakeBot:
    def __init__(self, economy):
        self._economy = economy

    def get_cog(self, name):
        return self._economy if name == "EconomyCog" else None


def play(data, *, amount=BET, final_grid=None):
    """Run one ``slots play`` and return (ctx, economy) after the spin."""
    economy = FakeEconomy(data)
    ctx = FakeCtx()
    grids = [mixed_grid(), grid_of("🍒"), mixed_grid(), final_grid or mixed_grid()]
    with patch.object(slots_module, "spin_grid", side_effect=grids), \
         patch.object(slots_module.asyncio, "sleep", new=AsyncMock()), \
         patch("cogs.economy.cog._check_achievements", return_value=[]):
        asyncio.run(Slots.slots_play.callback(Slots(FakeBot(economy)), ctx, amount))
    return ctx, economy


class PaytableTests(unittest.TestCase):
    def test_no_matching_line_returns_nothing(self):
        self.assertEqual(evaluate_grid(mixed_grid(), BET), (0, []))

    def test_common_line_returns_twice_the_bet(self):
        self.assertEqual(evaluate_grid(one_line_grid("🍒"), BET), (BET * 2, [("🍒", "Common Line (2×)")]))

    def test_uncommon_line_returns_three_times_the_bet(self):
        self.assertEqual(evaluate_grid(one_line_grid("🍇"), BET)[0], BET * 3)

    def test_rare_line_returns_five_times_the_bet(self):
        self.assertEqual(evaluate_grid(one_line_grid("💎"), BET)[0], BET * 5)

    def test_jackpot_line_returns_twenty_five_times_the_bet(self):
        self.assertEqual(evaluate_grid(one_line_grid("🪙"), BET)[0], BET * 25)

    def test_full_board_pays_every_line_plus_the_board_jackpot(self):
        returned, hits = evaluate_grid(grid_of("🍒"), BET)
        # Five common lines at 2x, then the 100x board jackpot on top.
        self.assertEqual(returned, BET * (5 * 2 + 100))
        self.assertEqual(len(hits), 6)
        self.assertIn(("🍒", "FULL BOARD JACKPOT (100×)"), hits)

    def test_every_line_is_credited_once(self):
        grid = [
            ["💎", "💎", "💎"],   # top row
            ["🔥", "🔥", "🔥"],   # middle row
            ["🍎", "🍎", "🍎"],   # bottom row
        ]
        returned, hits = evaluate_grid(grid, BET)
        self.assertEqual(returned, BET * (5 + 5 + 3))
        # Lines are read middle, top, bottom, then the two diagonals.
        self.assertEqual([label for _, label in hits], [
            "Rare Line (5×)",
            "Rare Line (5×)",
            "Uncommon Line (3×)",
        ])


class SpinAccountingTests(unittest.TestCase):
    """A spin must settle as one net ledger entry through the economy cog."""

    def test_losing_spin_debits_the_bet_and_records_it(self):
        data = account()
        _, economy = play(data)

        self.assertEqual(data["balance"], 900)
        self.assertEqual(data["total_spent"], BET)
        self.assertEqual(data["total_earned"], 0)
        self.assertEqual(economy.saves, 1)
        entry = data["transactions"][0]
        self.assertEqual(entry["kind"], "slots_loss")
        self.assertEqual(entry["amount"], -BET)
        self.assertIn("no line", entry["note"])

    def test_winning_spin_credits_the_payout_minus_the_stake(self):
        data = account()
        _, _ = play(data, final_grid=one_line_grid("🍇"))

        # 3x returned on a 100 bet: the wallet gains 200, not 300.
        self.assertEqual(data["balance"], 1200)
        self.assertEqual(data["total_earned"], 200)
        self.assertEqual(data["total_spent"], 0)
        entry = data["transactions"][0]
        self.assertEqual(entry["kind"], "slots_win")
        self.assertEqual(entry["amount"], 200)
        self.assertIn("Uncommon Line (3×)", entry["note"])

    def test_even_money_win_profits_exactly_one_stake(self):
        data = account()
        play(data, final_grid=one_line_grid("🍒"))
        # 2x returned = even money: the wallet gains the stake, not the return.
        self.assertEqual(data["balance"], 1100)
        self.assertEqual(data["transactions"][0]["kind"], "slots_win")
        self.assertEqual(data["transactions"][0]["amount"], BET)

    def test_spin_goes_through_record_gamble(self):
        data = account()
        economy = FakeEconomy(data)
        record = MagicMock(return_value=[])
        economy.record_gamble = record
        with patch.object(slots_module, "spin_grid", side_effect=[mixed_grid()] * 4), \
             patch.object(slots_module.asyncio, "sleep", new=AsyncMock()):
            asyncio.run(Slots.slots_play.callback(Slots(FakeBot(economy)), FakeCtx(), BET))

        record.assert_called_once()
        args = record.call_args.args
        self.assertIs(args[0], data)
        self.assertEqual(args[1], -BET)
        self.assertEqual(args[2], "slots_loss")

    def test_wallet_cannot_go_below_the_bet(self):
        data = account(balance=50)
        ctx, economy = play(data)

        self.assertEqual(data["balance"], 50)
        self.assertEqual(data["transactions"], [])
        self.assertEqual(economy.saves, 0)
        self.assertIn("enough coins", ctx.sent[-1][0][0])


class CommandGuardTests(unittest.TestCase):
    def test_the_result_offers_a_persistent_play_again_button(self):
        ctx, _ = play(account())
        result_view = ctx.sent[0][2].edits[-1]["view"]

        self.assertIsNone(result_view.timeout)
        self.assertIn(f"casino:slots:again:42:{BET}", repr(result_view.to_components()))

    def test_cooldown_blocks_a_second_spin(self):
        started = time.time()
        data = account(last_slots=started)
        ctx, economy = play(data)

        self.assertEqual(data["balance"], 1000)
        self.assertEqual(economy.saves, 0)
        body = repr(ctx.sent[-1][1]["view"].to_components())
        self.assertIn("You can spin the slots again", body)
        ready = cooldown_ready_at(started, slots_module.slots_cooldown)
        self.assertIn(f"<t:{ready}:R>", body)

    def test_non_positive_bet_is_rejected(self):
        for amount in (0, -50):
            data = account()
            ctx, _ = play(data, amount=amount)
            self.assertEqual(data["balance"], 1000)
            self.assertIn("more than 0 coins", ctx.sent[-1][0][0])


if __name__ == "__main__":
    unittest.main()
