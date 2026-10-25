"""Roulette: the bet table and the wager accounting.

The roulette command credited ``payout`` on a win and debited the stake on a
loss, but the payout already included the stake and the stake was never taken.
Every winner therefore collected one extra stake, and the spin never reached the
transaction ledger. These tests pin both halves of the fix: ``resolve_bet`` owns
the whole bet table, and a spin settles as one net entry through
``EconomyCog.record_gamble``.

Run with:  python -m pytest tests/test_roulette.py -v
"""

import asyncio
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.casino import roulette as roulette_module  # noqa: E402
from cogs.casino.roulette import Roulette, resolve_bet  # noqa: E402
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
        "last_roulette": 0,
    }
    data.update(overrides)
    return data


class FakeEconomy:
    """The economy surface roulette uses, backed by the real ledger methods."""

    record_gamble = EconomyCog.record_gamble
    _credit = EconomyCog._credit

    def __init__(self, data):
        self.data = data
        self.saves = 0

    async def get_user_economy_data(self, user_id):
        return self.data

    async def save_user_economy_data(self, user_id):
        self.saves += 1


class FakeView:
    """Stand-in for an interactive LayoutView the command would await."""

    def __init__(self, choice=None, amount=None):
        self.choice = choice
        self.amount = amount
        self.edits = []

    async def wait(self):
        return True


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


def spin(data, *, result, bet_type="red", numbers=None, amount=BET):
    """Run one roulette round with the wheel forced to ``result``.

    Returns ``(ctx, economy, result_card)``, where ``result_card`` holds the
    arguments the result view was built with.
    """
    economy = FakeEconomy(data)
    ctx = FakeCtx()
    card = []
    category = "inside" if numbers else "color"
    with patch.object(roulette_module, "build_bet_type_view", lambda ctx: FakeView(category)), \
         patch.object(roulette_module, "build_color_view", lambda ctx: FakeView(bet_type)), \
         patch.object(roulette_module, "build_inside_view", lambda ctx: FakeView(bet_type)), \
         patch.object(roulette_module, "build_number_view", lambda ctx, count: FakeView(choice=numbers)), \
         patch.object(roulette_module, "build_chip_view", lambda ctx: FakeView(amount=amount)), \
         patch.object(roulette_module, "build_spinning_view", lambda: FakeView()), \
         patch.object(roulette_module, "build_result_view",
                      lambda *args: card.append(args) or FakeView()), \
         patch.object(roulette_module.random, "choice", lambda wheel: result), \
         patch.object(roulette_module.asyncio, "sleep", new=AsyncMock()), \
         patch("cogs.economy.cog._check_achievements", return_value=[]):
        asyncio.run(Roulette.roulette.callback(Roulette(FakeBot(economy)), ctx))
    return ctx, economy, card


class BetTableTests(unittest.TestCase):
    def test_even_money_bets_return_the_stake_plus_one(self):
        for bet_type, winning in [("red", 7), ("black", 8), ("odd", 7), ("even", 8),
                                  ("low", 5), ("high", 30)]:
            self.assertEqual(resolve_bet(bet_type, None, winning, BET), (True, BET * 2), bet_type)

    def test_even_money_bets_lose_outside_their_range(self):
        self.assertEqual(resolve_bet("red", None, 8, BET), (False, 0))
        self.assertEqual(resolve_bet("black", None, 7, BET), (False, 0))
        self.assertEqual(resolve_bet("low", None, 19, BET), (False, 0))
        self.assertEqual(resolve_bet("high", None, 18, BET), (False, 0))

    def test_green_zero_loses_every_outside_bet(self):
        for bet_type in ("red", "black", "odd", "even", "low", "high"):
            self.assertEqual(resolve_bet(bet_type, None, 0, BET), (False, 0), bet_type)

    def test_dozens_and_columns_pay_two_to_one(self):
        self.assertEqual(resolve_bet("dozen1", None, 12, BET), (True, BET * 3))
        self.assertEqual(resolve_bet("dozen2", None, 24, BET), (True, BET * 3))
        self.assertEqual(resolve_bet("dozen3", None, 36, BET), (True, BET * 3))
        self.assertEqual(resolve_bet("column1", None, 34, BET), (True, BET * 3))
        self.assertEqual(resolve_bet("column2", None, 35, BET), (True, BET * 3))
        self.assertEqual(resolve_bet("column3", None, 36, BET), (True, BET * 3))

    def test_zero_is_in_no_column(self):
        self.assertEqual(resolve_bet("column3", None, 0, BET), (False, 0))

    def test_dozens_and_columns_lose_outside_their_range(self):
        self.assertEqual(resolve_bet("dozen1", None, 13, BET), (False, 0))
        self.assertEqual(resolve_bet("column1", None, 35, BET), (False, 0))

    def test_inside_bets_pay_their_multiplier(self):
        self.assertEqual(resolve_bet("straight", [7], 7, BET), (True, BET * 35))
        self.assertEqual(resolve_bet("split", [7, 8], 8, BET), (True, BET * 17))
        self.assertEqual(resolve_bet("street", [7, 8, 9], 9, BET), (True, BET * 11))
        self.assertEqual(resolve_bet("corner", [7, 8, 10, 11], 11, BET), (True, BET * 8))
        self.assertEqual(resolve_bet("line", [7, 8, 9, 10, 11, 12], 12, BET), (True, BET * 5))

    def test_inside_bets_need_a_covered_number(self):
        self.assertEqual(resolve_bet("straight", [7], 8, BET), (False, 0))
        self.assertEqual(resolve_bet("straight", [7], 0, BET), (False, 0))
        self.assertEqual(resolve_bet("corner", None, 7, BET), (False, 0))

    def test_unknown_bet_type_pays_nothing(self):
        self.assertEqual(resolve_bet("bogus", None, 7, BET), (False, 0))


class SpinAccountingTests(unittest.TestCase):
    def test_winning_spin_gains_the_profit_only(self):
        data = account()
        _, economy, _ = spin(data, result=7, bet_type="red")

        # 2x returned on a 100 bet: the wallet gains 100, not 200.
        self.assertEqual(data["balance"], 1100)
        self.assertEqual(data["total_earned"], 100)
        self.assertEqual(data["total_spent"], 0)
        self.assertEqual(economy.saves, 1)
        entry = data["transactions"][0]
        self.assertEqual(entry["kind"], "roulette_win")
        self.assertEqual(entry["amount"], 100)
        self.assertEqual(entry["note"], "red · 7 (🔴 Red)")

    def test_losing_spin_debits_the_stake_and_records_it(self):
        data = account()
        _, economy, _ = spin(data, result=0, bet_type="red")

        self.assertEqual(data["balance"], 900)
        self.assertEqual(data["total_spent"], 100)
        self.assertEqual(data["total_earned"], 0)
        self.assertEqual(economy.saves, 1)
        entry = data["transactions"][0]
        self.assertEqual(entry["kind"], "roulette_loss")
        self.assertEqual(entry["amount"], -100)
        self.assertEqual(entry["note"], "red · 0 (🟢 Green)")

    def test_result_card_shows_the_net_win(self):
        data = account()
        _, _, card = spin(data, result=7, bet_type="red")
        # build_result_view(ctx, win, result, colour, bet_type, amount, winnings)
        ctx, win, result, colour, reported_type, stake, winnings = card[0]
        self.assertTrue(win)
        self.assertEqual((result, colour), (7, "🔴 Red"))
        self.assertEqual((reported_type, stake, winnings), ("red", BET, 100))

    def test_inside_win_credits_multiplier_minus_the_stake(self):
        data = account()
        _, _, _ = spin(data, result=7, bet_type="straight", numbers=[7])
        # A straight pays 35x returned, so the net gain is 34 stakes.
        self.assertEqual(data["balance"], 1000 + BET * 34)
        self.assertEqual(data["transactions"][0]["amount"], BET * 34)

    def test_spin_goes_through_record_gamble(self):
        data = account()
        economy = FakeEconomy(data)
        record = MagicMock(return_value=[])
        economy.record_gamble = record
        ctx = FakeCtx()
        with patch.object(roulette_module, "build_bet_type_view", lambda ctx: FakeView("color")), \
             patch.object(roulette_module, "build_color_view", lambda ctx: FakeView("red")), \
             patch.object(roulette_module, "build_chip_view", lambda ctx: FakeView(amount=BET)), \
             patch.object(roulette_module, "build_spinning_view", lambda: FakeView()), \
             patch.object(roulette_module, "build_result_view", lambda *args: FakeView()), \
             patch.object(roulette_module.random, "choice", lambda wheel: 7), \
             patch.object(roulette_module.asyncio, "sleep", new=AsyncMock()):
            asyncio.run(Roulette.roulette.callback(Roulette(FakeBot(economy)), ctx))

        record.assert_called_once()
        args = record.call_args.args
        self.assertIs(args[0], data)
        self.assertEqual(args[1], BET)
        self.assertEqual(args[2], "roulette_win")


class CommandGuardTests(unittest.TestCase):
    def test_cooldown_blocks_a_second_spin(self):
        started = time.time()
        data = account(last_roulette=started)
        ctx, economy, _ = spin(data, result=7)

        self.assertEqual(data["balance"], 1000)
        self.assertEqual(economy.saves, 0)
        body = repr(ctx.sent[-1][1]["view"].to_components())
        self.assertIn("You can spin the wheel again", body)
        ready = cooldown_ready_at(started, roulette_module.ROULETTE_COOLDOWN)
        self.assertIn(f"<t:{ready}:R>", body)

    def test_bet_larger_than_the_wallet_is_rejected(self):
        data = account()
        ctx, economy, _ = spin(data, result=7, amount=5000)

        self.assertEqual(data["balance"], 1000)
        self.assertEqual(data["transactions"], [])
        self.assertEqual(economy.saves, 0)
        self.assertIn("enough coins", ctx.sent[-1][0][0])


if __name__ == "__main__":
    unittest.main()
