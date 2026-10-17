"""Regression tests for the top.gg vote rewards, streaks and webhook."""

import asyncio
import inspect
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import discord

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app  # noqa: E402
from webapp import economy_routes as routes  # noqa: E402
from cogs.economy.data import ACHIEVEMENTS  # noqa: E402
from cogs.economy.voting import apply_vote, vote_standing, vote_dm_view  # noqa: E402
from utils.economy_jobs import (  # noqa: E402
    VOTE_BASE_REWARD,
    VOTE_COOLDOWN,
    VOTE_STREAK_WINDOW,
    VOTE_WEEKEND_MULTIPLIER,
    vote_earnings_multiplier,
    vote_reward_multiplier,
)

START = 1_800_000_000
WEBHOOK_TOKEN = "topgg-webhook-secret"


def account(**overrides):
    data = {"balance": 100, "total_earned": 100, "votes": 0, "vote_streak": 0, "best_vote_streak": 0, "last_vote": 0, "achievements": [], "transactions": []}
    data.update(overrides)
    return data


class VoteRewardTests(unittest.TestCase):
    def test_first_vote_pays_the_streak_one_reward_and_increments_counters(self):
        data = account()
        result = apply_vote(data, now=START)

        self.assertEqual(result["status"], "recorded")
        self.assertEqual(result["streak"], 1)
        self.assertEqual(result["reward"], int(VOTE_BASE_REWARD * vote_reward_multiplier(1)))
        self.assertEqual(data["votes"], 1)
        self.assertEqual(data["vote_streak"], 1)
        self.assertEqual(data["best_vote_streak"], 1)
        self.assertEqual(data["last_vote"], START)
        # The vote payout is credited, plus the "First Upvote" badge it unlocked.
        badge_reward = int(ACHIEVEMENTS["voter_first"]["reward"])
        self.assertEqual(data["balance"], 100 + result["reward"] + badge_reward)
        self.assertEqual(data["total_earned"], 100 + result["reward"] + badge_reward)
        self.assertTrue(any(entry["kind"] == "vote" for entry in data["transactions"]))
        self.assertIn("voter_first", data["achievements"])
        self.assertTrue(any("First Upvote" in item for item in result["unlocked"]))

    def test_duplicate_webhook_inside_the_cooldown_pays_nothing(self):
        data = account()
        apply_vote(data, now=START)
        balance_after_first = data["balance"]
        transactions_after_first = len(data["transactions"])

        duplicate = apply_vote(data, now=START + VOTE_COOLDOWN - 60)

        self.assertEqual(duplicate["status"], "already_voted")
        self.assertEqual(duplicate["reward"], 0)
        self.assertEqual(data["balance"], balance_after_first)
        self.assertEqual(data["votes"], 1)
        self.assertEqual(data["vote_streak"], 1)
        self.assertEqual(len(data["transactions"]), transactions_after_first)
        self.assertEqual(duplicate["next_vote_at"], START + VOTE_COOLDOWN)

    def test_vote_inside_the_streak_window_extends_the_streak_and_raises_the_reward(self):
        data = account()
        first = apply_vote(data, now=START)
        second = apply_vote(data, now=START + VOTE_COOLDOWN + 1)

        self.assertEqual(second["streak"], 2)
        self.assertGreater(second["reward"], first["reward"])
        self.assertEqual(second["reward"], int(VOTE_BASE_REWARD * vote_reward_multiplier(2)))
        self.assertEqual(data["best_vote_streak"], 2)

    def test_missing_a_day_restarts_the_streak_at_one(self):
        data = account(votes=9, vote_streak=6, best_vote_streak=6)
        result = apply_vote(data, now=START + VOTE_STREAK_WINDOW + VOTE_COOLDOWN)

        self.assertEqual(result["streak"], 1)
        self.assertEqual(data["vote_streak"], 1)
        self.assertEqual(data["best_vote_streak"], 6)

    def test_weekend_votes_pay_double(self):
        weekday = account()
        weekend = account()
        plain = apply_vote(weekday, now=START)
        doubled = apply_vote(weekend, now=START, weekend=True)

        self.assertEqual(doubled["reward"], int(plain["reward"] * VOTE_WEEKEND_MULTIPLIER))
        self.assertTrue(doubled["weekend"])

    def test_multipliers_are_capped_at_ten_streak_steps(self):
        self.assertEqual(vote_reward_multiplier(0), 1)
        self.assertEqual(vote_reward_multiplier(10), 2)
        self.assertEqual(vote_reward_multiplier(500), 2)
        self.assertEqual(vote_earnings_multiplier(0), 1)
        self.assertEqual(vote_earnings_multiplier(10), 1.5)
        self.assertEqual(vote_earnings_multiplier(-3), 1)

    def test_reward_multiplier_scales_the_payout(self):
        data = account(vote_streak=5, last_vote=START - VOTE_STREAK_WINDOW, votes=5)
        result = apply_vote(data, now=START)

        self.assertEqual(result["streak"], 6)
        self.assertEqual(result["reward"], int(VOTE_BASE_REWARD * vote_reward_multiplier(6)))
        self.assertEqual(result["reward_multiplier"], vote_reward_multiplier(6))

    def test_vote_standing_reports_the_link_and_cooldown(self):
        data = account(votes=3, vote_streak=3, best_vote_streak=4, last_vote=START)
        standing = vote_standing(data)

        self.assertEqual(standing["votes"], 3)
        self.assertEqual(standing["streak"], 3)
        self.assertEqual(standing["best_streak"], 4)
        self.assertEqual(standing["next_vote_at"], START + VOTE_COOLDOWN)
        self.assertIn("top.gg/bot/", standing["vote_url"])
        self.assertIsInstance(standing["reward_multiplier"], float)
        self.assertFalse(standing["can_vote"])

    def test_vote_dm_view_mentions_the_reward_and_the_link(self):
        data = account()
        result = apply_vote(data, now=START)
        view = vote_dm_view(result)

        text = "\n".join(
            component.content
            for component in view.walk_children()
            if isinstance(component, discord.ui.TextDisplay)
        )
        self.assertIn("top.gg", text)
        self.assertIn(f"{result['reward']:,}", text)
        self.assertIn("streak", text.lower())

    def test_the_vote_card_is_headed_by_the_topgg_logo(self):
        """The listing site's own logo heads its cards, once it is registered."""
        data = account()
        result = apply_vote(data, now=START)

        with patch("cogs.economy.voting.topgg_emoji", lambda: "<:topgg:1234>"):
            self.assertIn("<:topgg:1234>", self._view_text(vote_dm_view(result)))
        # Before the first startup sync registers it, the ballot emoji holds.
        with patch("cogs.economy.voting.topgg_emoji", lambda: None):
            self.assertIn("🗳️", self._view_text(vote_dm_view(result)))

    @staticmethod
    def _view_text(view) -> str:
        return "\n".join(
            component.content
            for component in view.walk_children()
            if isinstance(component, discord.ui.TextDisplay)
        )


def _run_immediately(value):
    """Stand in for the bot's loop: run an awaitable, pass through a plain value."""
    return asyncio.run(value) if inspect.isawaitable(value) else value


class TopggWebhookTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.patches = [
            patch.object(routes, "TOPGG_WEBHOOK_TOKEN", WEBHOOK_TOKEN),
            patch.object(routes, "run_on_bot_loop", new=_run_immediately),
        ]
        for active in self.patches:
            active.start()
        self.addCleanup(self._stop)

    def _stop(self):
        for active in reversed(self.patches):
            active.stop()

    def post(self, body, token=WEBHOOK_TOKEN):
        headers = {"Authorization": token} if token is not None else {}
        return self.client.post("/api/topgg/webhook", json=body, headers=headers)

    def test_missing_or_wrong_token_is_rejected_before_any_payout(self):
        with patch.object(routes, "_record_vote") as record:
            missing = self.post({"type": "upvote", "user": "424242"}, token=None)
            wrong = self.post({"type": "upvote", "user": "424242"}, token="nope")
        self.assertEqual(missing.status_code, 401)
        self.assertEqual(wrong.status_code, 401)
        record.assert_not_called()

    def test_unconfigured_token_closes_the_endpoint(self):
        with patch.object(routes, "TOPGG_WEBHOOK_TOKEN", ""), patch.object(routes, "_record_vote") as record:
            response = self.post({"type": "upvote", "user": "424242"}, token="anything")
        self.assertEqual(response.status_code, 401)
        record.assert_not_called()

    def test_test_event_does_not_pay_out(self):
        with patch.object(routes, "_record_vote") as record:
            response = self.post({"type": "test", "user": "424242"})
        self.assertEqual(response.status_code, 200)
        record.assert_not_called()

    def test_recorded_vote_rewards_the_user_and_sends_the_thanks_dm(self):
        result = {"status": "recorded", "reward": 550, "streak": 1}
        with patch.object(routes, "_record_vote", new=AsyncMock(return_value=result)) as record, \
             patch.object(routes, "_send_vote_thanks", new=AsyncMock(return_value=True)) as thanks:
            response = self.post({"type": "upvote", "user": "424242", "isWeekend": True})

        self.assertEqual(response.status_code, 200)
        record.assert_called_once()
        self.assertEqual(record.call_args.args[1], "424242")
        self.assertTrue(record.call_args.kwargs["weekend"])
        thanks.assert_called_once()

    def test_duplicate_vote_skips_the_dm(self):
        result = {"status": "already_voted", "reward": 0, "streak": 1}
        with patch.object(routes, "_record_vote", new=AsyncMock(return_value=result)), \
             patch.object(routes, "_send_vote_thanks", new=AsyncMock(return_value=True)) as thanks:
            response = self.post({"type": "upvote", "user": "424242"})

        self.assertEqual(response.status_code, 200)
        thanks.assert_not_called()

    def test_a_failed_dm_does_not_fail_the_delivery(self):
        result = {"status": "recorded", "reward": 550, "streak": 1}
        with patch.object(routes, "_record_vote", new=AsyncMock(return_value=result)), \
             patch.object(routes, "_send_vote_thanks", new=AsyncMock(side_effect=RuntimeError("closed dms"))):
            response = self.post({"type": "upvote", "user": "424242"})

        self.assertEqual(response.status_code, 200)

    def test_reward_failure_asks_topgg_to_retry(self):
        with patch.object(routes, "_record_vote", new=AsyncMock(side_effect=RuntimeError("bot down"))):
            response = self.post({"type": "upvote", "user": "424242"})
        self.assertEqual(response.status_code, 503)

    def test_malformed_payloads_are_rejected(self):
        with patch.object(routes, "_record_vote") as record:
            bad_user = self.post({"type": "upvote", "user": "not-a-snowflake"})
            no_body = self.client.post(
                "/api/topgg/webhook",
                data=b"not json",
                headers={"Authorization": WEBHOOK_TOKEN, "Content-Type": "application/json"},
            )
        self.assertEqual(bad_user.status_code, 400)
        self.assertEqual(no_body.status_code, 400)
        record.assert_not_called()


if __name__ == "__main__":
    unittest.main()
