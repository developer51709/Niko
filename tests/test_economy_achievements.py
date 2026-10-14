"""Regression tests for café achievements, their rewards and the dashboard payloads."""

import asyncio
import json
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app  # noqa: E402
from webapp.economy_routes import achievement_entries, economy_summary  # noqa: E402
from cogs.economy.data import (  # noqa: E402
    ACHIEVEMENTS,
    _check_achievements,
    _default_user,
    _migrate_user,
    _save_user_to_db,
    achievement_progress,
)
from cogs.economy.voting import apply_vote  # noqa: E402

VOTE_FIELDS = ("votes", "vote_streak", "best_vote_streak", "last_vote")


def account(**overrides):
    data = _default_user()
    data.update(overrides)
    return data


class AchievementCatalogueTests(unittest.TestCase):
    def test_every_badge_is_renderable_and_worth_coins(self):
        for achievement_id, meta in ACHIEVEMENTS.items():
            with self.subTest(achievement=achievement_id):
                self.assertEqual(achievement_id, achievement_id.strip())
                self.assertTrue(isinstance(meta.get("name"), str) and meta["name"].strip())
                self.assertTrue(isinstance(meta.get("emoji"), str) and meta["emoji"].strip())
                self.assertTrue(isinstance(meta.get("description"), str) and meta["description"].strip())
                self.assertGreater(int(meta["reward"]), 0)
                self.assertTrue(callable(meta["test"]))
                self.assertTrue(callable(meta["progress"]))

    def test_vote_badges_cover_both_total_votes_and_streaks(self):
        vote_badges = [name for name in ACHIEVEMENTS if name.startswith("voter_") or "vote_streak" in name]
        self.assertGreaterEqual(len(vote_badges), 5)
        self.assertIn("voter_first", ACHIEVEMENTS)
        self.assertIn("vote_streak_7", ACHIEVEMENTS)

    def test_progress_is_clamped_and_never_divides_by_zero(self):
        meta = {"progress": lambda d: (5, 3)}
        self.assertEqual(achievement_progress(meta, {}), (3, 3))

        broken = {"progress": lambda d: (_ for _ in ()).throw(RuntimeError("boom"))}
        self.assertEqual(achievement_progress(broken, {}), (0, 1))

        zero_target = {"progress": lambda d: (1, 0)}
        self.assertEqual(achievement_progress(zero_target, {}), (1, 1))

        negative = {"progress": lambda d: (-5, 10)}
        self.assertEqual(achievement_progress(negative, {}), (0, 10))

    def test_real_badges_report_progress_against_their_own_account(self):
        current, target = achievement_progress(ACHIEVEMENTS["voter_regular"], {"votes": 4})
        self.assertEqual((current, target), (4, 10))
        current, target = achievement_progress(ACHIEVEMENTS["voter_regular"], {"votes": 40})
        self.assertEqual((current, target), (10, 10))


class AchievementRewardTests(unittest.TestCase):
    def test_unlock_pays_once_and_is_logged(self):
        data = account(times_worked=1, total_earned=100)

        first = _check_achievements(data)

        self.assertTrue(any("First Paycheck" in item for item in first))
        self.assertIn("first_paycheck", data["achievements"])
        paid = int(ACHIEVEMENTS["first_paycheck"]["reward"])
        self.assertEqual(data["balance"], 100 + paid)
        self.assertEqual(data["total_earned"], 100 + paid)
        self.assertEqual(data["transactions"][0]["kind"], "achievement")
        self.assertEqual(data["transactions"][0]["amount"], paid)

        balance_after_first = data["balance"]
        second = _check_achievements(data)

        self.assertEqual(second, [])
        self.assertEqual(data["balance"], balance_after_first)
        self.assertEqual(data["achievements"].count("first_paycheck"), 1)

    def test_vote_counters_unlock_the_voting_badges(self):
        data = account(votes=10, best_vote_streak=7)
        _check_achievements(data)

        self.assertIn("voter_first", data["achievements"])
        self.assertIn("voter_regular", data["achievements"])
        self.assertIn("vote_streak_7", data["achievements"])
        self.assertNotIn("voter_devoted", data["achievements"])

    def test_a_vote_can_unlock_a_badge_in_the_same_transaction(self):
        data = account(votes=9, vote_streak=1, last_vote=0)
        result = apply_vote(data, now=1_800_000_000)

        self.assertIn("voter_regular", data["achievements"])
        self.assertTrue(any("Vote Regular" in item for item in result["unlocked"]))


class VoteColumnPersistenceTests(unittest.TestCase):
    def test_default_and_migrated_accounts_carry_the_vote_counters(self):
        defaults = _default_user()
        for field in VOTE_FIELDS:
            self.assertEqual(defaults[field], 0)

        legacy = {"user_id": 7, "balance": 50, "bank": 10}
        _migrate_user(legacy)
        for field in VOTE_FIELDS:
            self.assertEqual(legacy[field], 0)

    def test_save_writes_every_vote_column_with_a_matching_placeholder(self):
        calls = []

        class FakePool:
            async def execute(self, sql, *values):
                calls.append((sql, values))

        data = account(votes=7, vote_streak=4, best_vote_streak=8, last_vote=1_700_000_000)
        asyncio.run(_save_user_to_db(SimpleNamespace(cxn=FakePool()), 42, data))

        self.assertEqual(len(calls), 1)
        sql, values = calls[0]
        columns = [column.strip() for column in sql.split("(", 1)[1].split(")", 1)[0].split(",")]
        self.assertEqual(columns[-4:], list(VOTE_FIELDS))
        # INSERT OR REPLACE rewrites the whole row, so a column added without a
        # bound value silently drops or resets data.
        self.assertEqual(sql.count("?"), len(columns))
        self.assertEqual(len(values), len(columns))
        self.assertEqual(values[-4:], (7, 4, 8, 1_700_000_000))


class DashboardPayloadTests(unittest.TestCase):
    def test_achievement_entries_mark_state_and_put_unearned_first(self):
        entries = achievement_entries({"achievements": json.dumps(["first_paycheck"]), "times_worked": 12})

        self.assertEqual(len(entries), len(ACHIEVEMENTS))
        unlocked = [entry for entry in entries if entry["unlocked"]]
        self.assertEqual([entry["id"] for entry in unlocked], ["first_paycheck"])
        self.assertEqual(entries[0]["unlocked"], False)
        self.assertEqual(unlocked[0]["id"], entries[-1]["id"])
        for entry in entries:
            self.assertTrue(entry["name"] and entry["emoji"])
            self.assertGreater(entry["reward"], 0)
            self.assertEqual(entry["progress"]["target"], max(1, int(entry["progress"]["target"])))
            self.assertLessEqual(entry["progress"]["current"], entry["progress"]["target"])
            self.assertLessEqual(entry["progress"]["percent"], 100)
            self.assertGreaterEqual(entry["progress"]["percent"], 0)

    def test_achievement_entries_handle_an_unknown_id_and_no_account(self):
        entries = achievement_entries({"achievements": json.dumps(["deleted_badge"])})
        self.assertFalse(any(entry["unlocked"] for entry in entries))
        self.assertEqual(len(achievement_entries(None)), len(ACHIEVEMENTS))

    def test_economy_summary_reports_worth_ranks_and_vote_state(self):
        stored = account(
            user_id=99,
            balance=1_500,
            bank=8_500,
            level=12,
            job="manager",
            times_worked=31,
            total_earned=20_000,
            total_spent=5_000,
            daily_streak=6,
            achievements=json.dumps(["first_paycheck", "regular"]),
            transactions=json.dumps([
                {"kind": "vote", "amount": 550, "note": "top.gg vote · streak 2", "ts": 1_700_000_000},
                "not-a-dict",
            ]),
            votes=3,
            vote_streak=2,
            best_vote_streak=5,
            last_vote=1_700_000_000,
        )
        summary = economy_summary(stored, global_rank=4, account_count=900)

        self.assertEqual(summary["net_worth"], 10_000)
        self.assertEqual(summary["balance"], 1_500)
        self.assertEqual(summary["bank"], 8_500)
        self.assertEqual(summary["job"], "manager")
        self.assertEqual(summary["achievements_unlocked"], 2)
        self.assertEqual(summary["achievements_total"], len(ACHIEVEMENTS))
        self.assertEqual(
            summary["achievement_coins"],
            sum(int(ACHIEVEMENTS[name]["reward"]) for name in ("first_paycheck", "regular")),
        )
        self.assertEqual(summary["global_rank"], 4)
        self.assertEqual(summary["account_count"], 900)
        # The economy is global per account: a standing must never be scoped to
        # one server, so no server ranking may come back in the payload.
        for server_field in ("server_rank", "server_size", "server_profiles"):
            self.assertNotIn(server_field, summary)
        # The malformed ledger row is dropped rather than rendered as garbage.
        self.assertEqual(summary["transactions"], [{
            "kind": "vote", "amount": 550, "note": "top.gg vote · streak 2", "ts": 1_700_000_000,
        }])
        self.assertEqual(summary["vote"]["votes"], 3)
        self.assertEqual(summary["vote"]["streak"], 2)
        self.assertEqual(summary["vote"]["best_streak"], 5)
        self.assertIn("top.gg", summary["vote"]["vote_url"])

    def test_economy_summary_survives_an_empty_account(self):
        summary = economy_summary(None)
        self.assertEqual(summary["net_worth"], 0)
        self.assertEqual(summary["achievements_unlocked"], 0)
        self.assertEqual(summary["transactions"], [])
        self.assertIsNone(summary["account_count"])
        self.assertEqual(summary["vote"]["votes"], 0)
        self.assertEqual(summary["vote"]["reward_multiplier"], 1.0)


class PersonalEconomyRouteTests(unittest.TestCase):
    """The economy tabs are account tabs, so their routes are `/api/me/*`."""

    def test_the_personal_economy_tabs_reject_anonymous_reads(self):
        client = app.test_client()
        for path in ("/api/me/economy", "/api/me/achievements"):
            with self.subTest(path=path):
                response = client.get(path)
                self.assertEqual(response.status_code, 401)
                self.assertIn("Not authenticated", response.get_json()["error"])

    def test_the_economy_payload_matches_what_the_tab_renders(self):
        """The personal Economy tab reads these exact keys, with no server scoping."""
        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": "42", "username": "Tester"}
            session["access_token"] = "token"
            session["token_exp"] = time.time() + 3600

        response = client.get("/api/me/economy")
        self.assertEqual(response.status_code, 200)
        standing = response.get_json()
        for key in (
            "balance", "bank", "net_worth", "level", "job", "bank_tier",
            "daily_streak", "total_earned", "total_spent", "times_worked",
            "achievements_unlocked", "achievements_total", "achievement_coins",
            "global_rank", "account_count", "transactions", "vote",
        ):
            with self.subTest(key=key):
                self.assertIn(key, standing)
        for server_field in ("server_rank", "server_size", "server_profiles"):
            self.assertNotIn(server_field, standing)
        self.assertIsInstance(standing["transactions"], list)
        for vote_key in ("votes", "streak", "best_streak", "reward_multiplier", "earnings_multiplier", "vote_url"):
            self.assertIn(vote_key, standing["vote"])

    def test_the_achievements_payload_matches_what_the_tab_renders(self):
        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": "42", "username": "Tester"}
            session["access_token"] = "token"
            session["token_exp"] = time.time() + 3600

        response = client.get("/api/me/achievements")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(len(payload["achievements"]), len(ACHIEVEMENTS))
        self.assertEqual(payload["total"], len(ACHIEVEMENTS))
        for key in ("unlocked", "total", "coins_earned", "coins_available"):
            self.assertIn(key, payload)
        for entry in payload["achievements"]:
            with self.subTest(achievement=entry["id"]):
                for key in ("id", "name", "emoji", "description", "reward", "unlocked", "progress"):
                    self.assertIn(key, entry)
                for key in ("current", "target", "percent"):
                    self.assertIn(key, entry["progress"])
                self.assertLessEqual(entry["progress"]["percent"], 100)

    def test_the_economy_tabs_are_not_guild_routes(self):
        """A guild-scoped economy route would misrepresent a global feature."""
        client = app.test_client()
        for path in ("/api/guild/424242/economy", "/api/guild/424242/achievements"):
            with self.subTest(path=path):
                response = client.get(path)
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.get_json(), {"error": "Not found"})


if __name__ == "__main__":
    unittest.main()
