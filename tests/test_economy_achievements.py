"""Regression tests for café achievements, their rewards and the dashboard payloads."""

import asyncio
import datetime as dt
import json
import re
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import aiosqlite

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from database import SQLitePool  # noqa: E402
from events.startup import database as database_setup  # noqa: E402
from webapp import app  # noqa: E402
from webapp.routes.economy_routes import (  # noqa: E402
    TOPGG_LOGO_URL,
    achievement_entries,
    economy_summary,
    transaction_label,
)
from cogs.economy.seasons import season_status, season_window  # noqa: E402
from cogs.economy.data import (  # noqa: E402
    ACHIEVEMENTS,
    _check_achievements,
    _default_user,
    _get_user_from_db,
    _migrate_user,
    _save_user_to_db,
    achievement_progress,
    ensure_season_baselines,
    seasonal_progress,
)
from cogs.economy.voting import apply_vote  # noqa: E402
from utils.economy_jobs import (  # noqa: E402
    LOTTERY_BASE_POT,
    LOTTERY_DRAW_INTERVAL,
    LOTTERY_TICKET_PRICE,
)
from webapp.routes import economy_routes as economy_routes_module  # noqa: E402

VOTE_FIELDS = ("votes", "vote_streak", "best_vote_streak", "last_vote")


def is_voting_badge(achievement_id: str) -> bool:
    return achievement_id.startswith("voter_") or "vote_streak" in achievement_id


class ZeroAccount(dict):
    """A stand-in account where every counter reads as zero.

    Progress functions then report ``(0, target)``, which is the only way to ask
    a badge what its threshold is without duplicating the number in the test.
    """

    def __missing__(self, key):
        return 0

    def get(self, key, default=None):
        return 0


def threshold(achievement_id: str) -> int:
    """The target a badge's progress bar climbs towards."""
    return achievement_progress(ACHIEVEMENTS[achievement_id], ZeroAccount())[1]


def seasonal_badges() -> dict[str, dict]:
    return {name: meta for name, meta in ACHIEVEMENTS.items() if meta.get("season")}


def dashboard_rule(selector: str) -> str:
    """Return the declaration block ``selector`` declares in the dashboard CSS."""
    css = (ROOT / "web" / "src" / "styles.css").read_text(encoding="utf-8")
    match = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    if match is None:
        raise AssertionError(f"{selector} has no rule in web/src/styles.css")
    return match.group(1)


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
        vote_badges = [name for name in ACHIEVEMENTS if is_voting_badge(name)]
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


class TopggLogoIconTests(unittest.TestCase):
    """The voting badges draw the listing site's logo instead of an emoji."""

    def test_exactly_the_voting_badges_carry_the_logo_icon(self):
        logo_badges = {name for name, meta in ACHIEVEMENTS.items() if meta.get("icon") == "topgg"}
        vote_badges = {name for name in ACHIEVEMENTS if is_voting_badge(name)}

        self.assertEqual(logo_badges, vote_badges)
        self.assertTrue(vote_badges)
        # A badge still needs its unicode emoji as the pre-sync fallback.
        for name in logo_badges:
            with self.subTest(achievement=name):
                self.assertTrue(ACHIEVEMENTS[name]["emoji"].strip())

    def test_the_logo_is_configured_with_the_asset_the_startup_sync_uploads(self):
        """Startup sync (``utils/emoji_sync.py``) parses the emoji config, then
        uploads ``src/assets/emojis/<name>.png`` as the application emoji."""
        config = (ROOT / "src" / "config" / "emojis.py").read_text(encoding="utf-8")
        entry = re.search(
            r'if emoji_name == "topgg":\s*\n\s*return "<(?P<animated>a?):(?P<name>[A-Za-z0-9_]+):(?P<id>\d+)>"',
            config,
        )
        self.assertIsNotNone(entry, "emojis.py has no topgg entry for the startup sync to register")
        self.assertEqual(entry.group("name"), "topgg")
        self.assertEqual(entry.group("animated"), "", "a .gif asset would be needed to match an animated entry")

        asset = ROOT / "src" / "assets" / "emojis" / "topgg.png"
        self.assertTrue(asset.is_file(), f"{asset} is what the sync uploads for :topgg:")
        self.assertGreater(asset.stat().st_size, 0)
        # Discord rejects an application emoji above 256 KB.
        self.assertLess(asset.stat().st_size, 256 * 1024)

    def test_the_dashboard_logo_asset_ships_with_the_web_build(self):
        logo = ROOT / "web" / "public" / "topgg.svg"
        self.assertTrue(logo.is_file(), f"{logo} is served as {TOPGG_LOGO_URL}")
        self.assertIn("top.gg", logo.read_text(encoding="utf-8"))

    def test_unlock_announcements_use_the_registered_logo(self):
        with mock.patch("cogs.economy.data.get_emoji", lambda name: "<:topgg:1234>"):
            labels = _check_achievements(account(votes=1, total_earned=100))

        announcement = next(label for label in labels if "First Upvote" in label)
        self.assertIn("<:topgg:1234>", announcement)
        self.assertNotIn("🗳️", announcement)

    def test_unlock_announcements_fall_back_until_the_logo_is_registered(self):
        # A fresh checkout holds a placeholder id until the first startup sync
        # rewrites it; printing that would leave a broken mention in chat.
        for placeholder in ("<:topgg:0>", ""):
            with self.subTest(placeholder=placeholder):
                with mock.patch("cogs.economy.data.get_emoji", lambda name, value=placeholder: value):
                    labels = _check_achievements(account(votes=1, total_earned=100))
                self.assertIn("🗳️", next(label for label in labels if "First Upvote" in label))


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
        # The tab renders the display name, never the raw stored job id.
        self.assertEqual(summary["job_name"], "Shift Manager")
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
            "kind": "vote", "label": "top.gg vote", "amount": 550,
            "note": "top.gg vote · streak 2", "ts": 1_700_000_000,
        }])
        self.assertEqual(summary["vote"]["votes"], 3)
        self.assertEqual(summary["vote"]["streak"], 2)
        self.assertEqual(summary["vote"]["best_streak"], 5)
        self.assertIn("top.gg", summary["vote"]["vote_url"])

    def test_achievement_entries_hand_the_dashboard_the_logo_url(self):
        entries = {entry["id"]: entry for entry in achievement_entries({"achievements": json.dumps([])})}

        self.assertEqual(entries["voter_first"]["icon_url"], TOPGG_LOGO_URL)
        self.assertEqual(entries["vote_streak_100"]["icon_url"], TOPGG_LOGO_URL)
        self.assertIsNone(entries["first_paycheck"]["icon_url"])
        # Every badge still carries the emoji the dashboard falls back to.
        self.assertTrue(entries["voter_first"]["emoji"])

    def test_achievement_entries_carry_the_season_window(self):
        in_season = {entry["id"]: entry for entry in achievement_entries(
            {"achievements": json.dumps([])}, now=dt.datetime(2026, 10, 25),
        )}
        out_of_season = {entry["id"]: entry for entry in achievement_entries(
            {"achievements": json.dumps([])}, now=dt.datetime(2026, 6, 1),
        )}

        self.assertIsNone(in_season["first_paycheck"]["season"])
        self.assertTrue(in_season["spooky_vault"]["season"]["active"])
        self.assertEqual(in_season["spooky_vault"]["season"]["label"], "Halloween")
        self.assertFalse(out_of_season["spooky_vault"]["season"]["active"])
        for entry in out_of_season.values():
            with self.subTest(achievement=entry["id"]):
                if entry["season"]:
                    self.assertGreater(entry["season"]["starts_at"], entry["season"]["ends_at"] - 400 * 86_400)
                    self.assertGreater(entry["season"]["ends_at"], entry["season"]["starts_at"])

    def test_economy_summary_carries_the_lottery_card(self):
        summary = economy_summary(account(lottery_tickets=3))
        lottery = summary["lottery"]

        # The card shows the member's own entries, so the viewer's ticket count
        # comes from the account rather than from the round totals.
        self.assertEqual(lottery["your_tickets"], 3)
        self.assertEqual(lottery["ticket_price"], LOTTERY_TICKET_PRICE)
        self.assertIsInstance(lottery["open"], bool)
        self.assertIn("last_winner", lottery)
        for field in ("pot", "participants", "tickets", "next_draw", "last_pot"):
            self.assertIsInstance(lottery[field], int, field)
            self.assertGreaterEqual(lottery[field], 0, field)

    def test_economy_summary_passes_through_a_supplied_round(self):
        # The route reads the round once and hands it in, so the summary must
        # not re-read the lottery state and disagree with the card it renders.
        supplied = {
            "pot": 5_000, "participants": 2, "tickets": 4, "your_tickets": 1,
            "ticket_price": 250, "next_draw": 1_800_000_000,
            "last_winner": "Niko", "last_pot": 9_000, "open": True,
        }
        summary = economy_summary(account(), lottery=supplied)
        self.assertEqual(summary["lottery"], supplied)

    def test_casino_ledger_kinds_get_a_readable_label(self):
        # A casino result is written by the casino cogs, not by the economy
        # mixins, so the card has to name each kind explicitly: a raw
        # "roulette_loss" would read as an unlabelled row.
        for kind, label in {
            "slots_win": "Slots won",
            "slots_loss": "Slots lost",
            "blackjack_win": "Blackjack won",
            "blackjack_loss": "Blackjack lost",
            "blackjack": "Blackjack push",
            "roulette_win": "Roulette won",
            "roulette_loss": "Roulette lost",
        }.items():
            self.assertEqual(transaction_label(kind), label)
        self.assertEqual(transaction_label("some_new_kind"), "Some new kind")

    def test_economy_summary_survives_an_empty_account(self):
        summary = economy_summary(None)
        self.assertEqual(summary["net_worth"], 0)
        self.assertEqual(summary["job_name"], "Cashier")
        self.assertEqual(summary["achievements_unlocked"], 0)
        self.assertEqual(summary["transactions"], [])
        self.assertIsNone(summary["account_count"])
        self.assertEqual(summary["vote"]["votes"], 0)
        self.assertEqual(summary["vote"]["reward_multiplier"], 1.0)


class CatalogueCoverageTests(unittest.TestCase):
    """Every counter the economy keeps should have more than one rung."""

    def test_badge_ladders_climb_without_repeating_a_threshold(self):
        ladders = {
            "shifts": ("times_worked", ["first_paycheck", "regular", "shift_50", "shift_lead"]),
            "career level": ("level", ["level_5", "level_15", "level_30"]),
            "daily streak": ("daily_streak", ["streak_7", "streak_14", "streak_30", "streak_60", "streak_90"]),
            "spending": ("total_spent", ["spend_10k", "gambler", "whale"]),
            "vault tier": ("bank_tier", ["bank_tier_2", "bank_tier_top"]),
            "net worth": ("net_worth", ["worth_1k", "worth_250k", "millionaire"]),
            "votes": ("votes", ["voter_first", "voter_regular", "voter_25", "voter_devoted", "voter_legend"]),
            "vote streak": ("best_vote_streak", ["vote_streak_7", "vote_streak_30", "vote_streak_100"]),
            "lottery tickets": ("lottery_tickets_bought", ["lottery_first_ticket", "lottery_tickets_25",
                                                          "lottery_tickets_100", "lottery_tickets_500"]),
            "lottery wins": ("lottery_wins", ["lottery_win_first", "lottery_wins_3", "lottery_wins_10"]),
        }
        for family, (_, ordered) in ladders.items():
            with self.subTest(family=family):
                targets = [threshold(achievement_id) for achievement_id in ordered]
                self.assertEqual(targets, sorted(set(targets)), f"{family} thresholds must climb strictly")

    def test_the_new_tiers_are_worth_their_place_on_the_ladder(self):
        for achievement_id in ("shift_50", "level_5", "level_15", "level_30", "bank_tier_2",
                               "bank_tier_top", "worth_1k", "worth_250k", "spend_10k", "streak_14", "voter_25"):
            with self.subTest(achievement=achievement_id):
                self.assertIn(achievement_id, ACHIEVEMENTS)
                self.assertGreater(int(ACHIEVEMENTS[achievement_id]["reward"]), 0)

    def test_the_top_vault_badge_follows_the_bank_table(self):
        from utils.economy_jobs import max_bank_tier

        self.assertEqual(threshold("bank_tier_top"), max_bank_tier())
        self.assertLess(threshold("bank_tier_2"), threshold("bank_tier_top"))


class SeasonalCalendarTests(unittest.TestCase):
    """Seasonal badges keep their own window, so nobody has to edit dates."""

    def test_every_seasonal_badge_declares_a_labelled_month_day_window(self):
        badges = seasonal_badges()
        self.assertGreaterEqual(len(badges), 5)
        for achievement_id, meta in badges.items():
            with self.subTest(achievement=achievement_id):
                season = meta["season"]
                self.assertTrue(str(season.get("label") or "").strip())
                for bound in ("start", "end"):
                    self.assertRegex(str(season[bound]), r"^\d{2}-\d{2}$")
                # It has to actually open: a window nobody can reach is a dead badge.
                self.assertIsNotNone(season_window(meta, dt.datetime(2026, 6, 1)))
                self.assertIsNotNone(season_window(meta, dt.datetime(2027, 1, 1)))
        labels = {meta["season"]["label"] for meta in badges.values()}
        self.assertEqual(
            labels,
            {"Halloween", "Winter", "New Year", "Valentine's", "Summer"},
        )

    def test_in_between_dates_open_and_close_inclusively(self):
        halloween = ACHIEVEMENTS["spooky_vault"]
        # Once the window closes, the badge reports next year's opening.
        for moment, expected, year in (
            (dt.datetime(2026, 10, 23, 23, 59), False, 2026),
            (dt.datetime(2026, 10, 24, 0, 0), True, 2026),
            (dt.datetime(2026, 11, 1, 23, 59), True, 2026),
            (dt.datetime(2026, 11, 2, 0, 0), False, 2027),
        ):
            with self.subTest(moment=moment):
                status = season_status(halloween, moment)
                self.assertEqual(status["active"], expected)
                self.assertEqual(dt.datetime.fromtimestamp(status["starts_at"]), dt.datetime(year, 10, 24))

    def test_a_window_may_wrap_the_new_year(self):
        winter = ACHIEVEMENTS["winter_streak"]
        status = season_status(winter, dt.datetime(2027, 1, 1))

        self.assertTrue(status["active"])
        # Open today because it started in December of the previous year.
        self.assertEqual(dt.datetime.fromtimestamp(status["starts_at"]), dt.datetime(2026, 12, 15))
        self.assertEqual(dt.datetime.fromtimestamp(status["ends_at"]), dt.datetime(2027, 1, 2, 23, 59, 59))

    def test_a_closed_window_reports_the_next_opening(self):
        halloween = ACHIEVEMENTS["spooky_vault"]
        status = season_status(halloween, dt.datetime(2026, 11, 5))

        self.assertFalse(status["active"])
        self.assertEqual(dt.datetime.fromtimestamp(status["starts_at"]), dt.datetime(2027, 10, 24))
        self.assertGreater(status["starts_at"], int(dt.datetime(2026, 11, 5).timestamp()))
        # A window may also be reported before it opens this year.
        upcoming = season_status(halloween, dt.datetime(2027, 3, 1))
        self.assertEqual(dt.datetime.fromtimestamp(upcoming["starts_at"]), dt.datetime(2027, 10, 24))

    def test_always_available_badges_carry_no_window(self):
        self.assertIsNone(season_status(ACHIEVEMENTS["first_paycheck"], dt.datetime(2026, 6, 1)))
        self.assertIsNone(season_window(ACHIEVEMENTS["shift_50"]))


class SeasonalUnlockTests(unittest.TestCase):
    def test_a_seasonal_badge_only_unlocks_inside_its_window(self):
        qualifying = dict(bank=30_000)

        out_of_season = account(**qualifying)
        _check_achievements(out_of_season, now=dt.datetime(2026, 6, 1))
        self.assertNotIn("spooky_vault", out_of_season["achievements"])

        in_season = account(**qualifying)
        labels = _check_achievements(in_season, now=dt.datetime(2026, 10, 25))
        self.assertIn("spooky_vault", in_season["achievements"])
        self.assertTrue(any("Pumpkin Vault" in label for label in labels))

    def test_season_windows_do_not_gate_regular_badges(self):
        for moment in (dt.datetime(2026, 6, 1), dt.datetime(2026, 10, 25)):
            with self.subTest(moment=moment):
                data = account(times_worked=51, level=6)
                _check_achievements(data, now=moment)
                self.assertIn("shift_50", data["achievements"])
                self.assertIn("level_5", data["achievements"])

    def test_a_seasonal_badge_already_earned_is_never_repaid_off_season(self):
        # A list, not the stored JSON column: this is what the cog hands over.
        data = account(bank=30_000, achievements=["spooky_vault"], total_earned=500)

        for moment in (dt.datetime(2026, 10, 25), dt.datetime(2026, 6, 1)):
            with self.subTest(moment=moment):
                labels = _check_achievements(data, now=moment)
                self.assertNotIn("Pumpkin Vault", "|".join(labels))
        # Other badges this account does qualify for may pay, but the seasonal
        # one must not pay twice — and never outside its window.
        self.assertEqual(data["achievements"].count("spooky_vault"), 1)
        self.assertEqual(
            [tx for tx in data["transactions"] if tx.get("note") == "Pumpkin Vault"],
            [],
        )


class SeasonalProgressTests(unittest.TestCase):
    """A seasonal badge cannot be advanced, or prepared, off-season.

    The badge table used to measure lifetime counters (``total_spent``, ``level``)
    and read them as-is once the window opened, so a spending spree in July or a
    level reached in March collected the Halloween and New Year badges for free.
    """

    HALLOWEEN = dt.datetime(2026, 10, 25)
    OFF_SEASON = dt.datetime(2026, 6, 1)

    def test_every_seasonal_badge_declares_how_it_is_measured(self):
        for achievement_id, meta in seasonal_badges().items():
            with self.subTest(achievement=achievement_id):
                self.assertIn(meta.get("season_measure"), ("hold", "gain", "reach"))
        for achievement_id, meta in ACHIEVEMENTS.items():
            if meta.get("season"):
                continue
            with self.subTest(achievement=achievement_id):
                self.assertNotIn("season_measure", meta)

    def test_off_season_progress_is_zero_and_nothing_unlocks(self):
        for achievement_id, meta in seasonal_badges().items():
            with self.subTest(achievement=achievement_id):
                data = account(bank=10_000_000, balance=10_000_000, level=99, daily_streak=99,
                               total_spent=10_000_000)
                _, target = achievement_progress(meta, data, now=self.OFF_SEASON,
                                                 achievement_id=achievement_id)
                self.assertEqual(
                    achievement_progress(meta, data, now=self.OFF_SEASON,
                                         achievement_id=achievement_id),
                    (0, target),
                )
                _check_achievements(data, now=self.OFF_SEASON)
                self.assertNotIn(achievement_id, data["achievements"])
                # Nothing is even recorded to build on when the window opens.
                self.assertEqual(data["season_progress"], {})

    def test_old_spending_cannot_bank_the_halloween_badge(self):
        data = account(total_spent=100_000)

        _check_achievements(data, now=self.HALLOWEEN)

        self.assertNotIn("spooky_spender", data["achievements"])
        self.assertEqual(
            achievement_progress(ACHIEVEMENTS["spooky_spender"], data, now=self.HALLOWEEN,
                                 achievement_id="spooky_spender"),
            (0, 5_000),
        )
        # The baseline is the value the window opened with, not zero.
        self.assertEqual(data["season_progress"]["spooky_spender"]["value"], 100_000)

        data["total_spent"] += 5_000
        _check_achievements(data, now=self.HALLOWEEN)

        self.assertIn("spooky_spender", data["achievements"])

    def test_a_milestone_must_be_crossed_inside_the_window(self):
        # Already past the target: one more step during the event earns it, so a
        # long-standing member's badge is never permanently dead.
        veteran = account(level=40)
        _check_achievements(veteran, now=dt.datetime(2027, 1, 1))
        self.assertNotIn("new_year_level", veteran["achievements"])
        self.assertEqual(
            achievement_progress(ACHIEVEMENTS["new_year_level"], veteran, now=dt.datetime(2027, 1, 1),
                                 achievement_id="new_year_level"),
            (0, 1),
        )
        veteran["level"] = 41
        _check_achievements(veteran, now=dt.datetime(2027, 1, 2))
        self.assertIn("new_year_level", veteran["achievements"])

        # Below the target: the climb to 25 has to happen inside the window.
        climber = account(level=10)
        _check_achievements(climber, now=dt.datetime(2027, 1, 1))
        climber["level"] = 24
        _check_achievements(climber, now=dt.datetime(2027, 1, 2))
        self.assertNotIn("new_year_level", climber["achievements"])
        self.assertEqual(
            achievement_progress(ACHIEVEMENTS["new_year_level"], climber, now=dt.datetime(2027, 1, 2),
                                 achievement_id="new_year_level"),
            (14, 15),
        )
        climber["level"] = 25
        _check_achievements(climber, now=dt.datetime(2027, 1, 3))
        self.assertIn("new_year_level", climber["achievements"])

    def test_a_hold_badge_reads_the_live_state_inside_the_window(self):
        data = account(bank=30_000)

        # Out of season the same account shows no progress and collects nothing.
        self.assertEqual(
            achievement_progress(ACHIEVEMENTS["spooky_vault"], data, now=self.OFF_SEASON,
                                 achievement_id="spooky_vault"),
            (0, 25_000),
        )
        _check_achievements(data, now=self.OFF_SEASON)
        self.assertNotIn("spooky_vault", data["achievements"])

        # Holding the state while the event is on is what the badge asks for.
        _check_achievements(data, now=self.HALLOWEEN)
        self.assertIn("spooky_vault", data["achievements"])
        # A "hold" badge reads the live state, so it stores no baseline of its
        # own — only the window measures do.
        self.assertNotIn("spooky_vault", data["season_progress"])

    def test_a_new_occurrence_starts_from_a_fresh_baseline(self):
        data = account(total_spent=106_000)
        data["season_progress"] = {"spooky_spender": {"window": "2026-10-24", "value": 100_000}}

        _check_achievements(data, now=dt.datetime(2027, 10, 25))

        # Last year's window cannot be spent again this year.
        self.assertNotIn("spooky_spender", data["achievements"])
        self.assertEqual(
            data["season_progress"]["spooky_spender"],
            {"window": "2027-10-24", "value": 106_000},
        )

    def test_a_window_with_no_baseline_claims_no_in_window_gain(self):
        """An account that has not acted inside the window has nothing to claim."""
        meta = ACHIEVEMENTS["spooky_spender"]
        data = account(total_spent=500_000)

        self.assertEqual(
            seasonal_progress(meta, data, now=self.HALLOWEEN, achievement_id="spooky_spender"),
            (0, 5_000),
        )

    def test_loading_an_account_records_its_baseline_before_the_command_acts(self):
        """The baseline has to predate the action, or the first in-window spend
        of a cached account would be swallowed by its own baseline."""

        class FakePool:
            async def fetchrow(self, sql, *values):
                return {
                    "user_id": 42,
                    "balance": 100,
                    "total_spent": 7_000,
                    "achievements": "[]",
                    "season_progress": "{}",
                }

        windows = mock.patch("cogs.economy.data.season_open_key", lambda meta, now=None: "2026-10-24")
        with windows:
            data = asyncio.run(_get_user_from_db(SimpleNamespace(cxn=FakePool()), 42))
            self.assertEqual(data["season_progress"]["spooky_spender"]["value"], 7_000)

            # A spend made by the command that loaded the account still counts.
            data["total_spent"] += 5_000
            _check_achievements(data)

        self.assertIn("spooky_spender", data["achievements"])

    def test_a_window_baseline_is_recorded_once_per_occurrence(self):
        data = account(total_spent=1_000)
        ensure_season_baselines(data, now=self.HALLOWEEN)
        first = dict(data["season_progress"]["spooky_spender"])

        data["total_spent"] = 4_000
        ensure_season_baselines(data, now=self.HALLOWEEN)

        self.assertEqual(data["season_progress"]["spooky_spender"], first)

    def test_the_dashboard_measures_seasonal_bars_inside_the_window(self):
        stored = account(
            total_spent=100_000,
            achievements=json.dumps([]),
            season_progress={"spooky_spender": {"window": "2026-10-24", "value": 100_000}},
        )

        def entry(moment, value):
            account_row = dict(stored)
            account_row["total_spent"] = value
            entries = {item["id"]: item for item in achievement_entries(account_row, now=moment)}
            return entries["spooky_spender"]

        out_of_season = entry(self.OFF_SEASON, 250_000)
        self.assertFalse(out_of_season["season"]["active"])
        self.assertEqual(out_of_season["progress"]["current"], 0)

        in_season = entry(self.HALLOWEEN, 102_500)
        self.assertTrue(in_season["season"]["active"])
        self.assertEqual(in_season["progress"]["current"], 2_500)
        self.assertEqual(in_season["progress"]["target"], 5_000)

    def test_a_raw_sqlite_row_still_carries_the_season_baselines(self):
        """The dashboard reads SQLite rows, where the blob is still a string."""
        row = account(
            total_spent=100_000,
            achievements=json.dumps([]),
            season_progress=json.dumps({"spooky_spender": {"window": "2026-10-24", "value": 100_000}}),
        )
        row["total_spent"] = 104_000

        entries = {item["id"]: item for item in achievement_entries(row, now=self.HALLOWEEN)}

        self.assertEqual(entries["spooky_spender"]["progress"]["current"], 4_000)

    def test_saving_writes_the_season_baselines_and_still_binds_every_column(self):
        calls = []

        class FakePool:
            async def execute(self, sql, *values):
                calls.append((sql, values))

        data = account(season_progress={"spooky_spender": {"window": "2026-10-24", "value": 12_345}})
        asyncio.run(_save_user_to_db(SimpleNamespace(cxn=FakePool()), 42, data))

        sql, values = calls[0]
        self.assertIn("season_progress", sql)
        self.assertIn(json.dumps({"spooky_spender": {"window": "2026-10-24", "value": 12_345}}), values)
        columns = [column.strip() for column in sql.split("(", 1)[1].split(")", 1)[0].split(",")]
        self.assertEqual(sql.count("?"), len(columns))
        self.assertEqual(len(values), len(columns))


class SeasonalPersistenceTests(unittest.TestCase):
    """The window baselines have to survive the real schema and a real save.

    ``_save_user_to_db`` logs and gives up when the statement fails, so a column
    that the schema does not have would silently drop every baseline — the
    badge would then look unsatisfied forever instead of reporting an error.
    """

    def test_the_season_column_exists_and_a_baseline_round_trips(self):
        async def scenario():
            connection = await aiosqlite.connect(":memory:")
            try:
                pool = SQLitePool(connection)
                bot = SimpleNamespace(cxn=pool)
                await database_setup._create_tables(bot)

                async def columns():
                    rows = await pool.fetch("PRAGMA table_info(economy_users)")
                    return [str(row["name"]) for row in rows]

                self.assertIn("season_progress", await columns())

                # An installation that predates the column: the stored shape is
                # the same table without it, so the migration has to add it
                # while every other column is already present.
                old = [name for name in await columns() if name != "season_progress"]
                await connection.execute(
                    "CREATE TABLE economy_users_old AS SELECT " + ", ".join(old) + " FROM economy_users"
                )
                await connection.execute("DROP TABLE economy_users")
                await connection.execute("ALTER TABLE economy_users_old RENAME TO economy_users")
                await connection.commit()
                self.assertNotIn("season_progress", await columns())
                await database_setup._create_tables(bot)
                self.assertIn("season_progress", await columns())

                data = account(total_spent=100_000)
                ensure_season_baselines(data, now=dt.datetime(2026, 10, 25))
                await _save_user_to_db(bot, 42, data)
                return await _get_user_from_db(bot, 42)
            finally:
                await connection.close()

        stored = asyncio.run(scenario())
        self.assertEqual(stored["season_progress"]["spooky_spender"]["value"], 100_000)
        # The stored baseline travels with the account, so the badge still
        # cannot be collected from spending that happened before the window.
        _check_achievements(stored, now=dt.datetime(2026, 10, 25))
        self.assertNotIn("spooky_spender", stored["achievements"])


class LotteryCardTests(unittest.TestCase):
    """The economy tab's lottery card has to render the round it is given."""

    def setUp(self):
        self.view = (ROOT / "web" / "src" / "components" / "dashboard" / "EconomyView.tsx").read_text(encoding="utf-8")

    def test_the_card_renders_every_field_of_the_round(self):
        self.assertIn("standing.lottery", self.view)
        for field in ("pot", "participants", "tickets", "your_tickets",
                      "ticket_price", "next_draw", "last_winner", "last_pot"):
            with self.subTest(field=field):
                self.assertIn(f"lottery.{field}", self.view)

    def test_the_card_says_how_to_buy_a_ticket_and_where_the_draw_is_posted(self):
        self.assertIn("/lottery buy", self.view)
        self.assertIn("#lottery", self.view)

    def test_without_a_saved_round_the_card_shows_the_bot_s_seed(self):
        # A deployment with no live bot and no lottery row must describe the
        # round the bot would open, not an empty closed lottery.
        with mock.patch.object(economy_routes_module, "_discord_bot", None), \
             mock.patch.object(economy_routes_module, "sqlite_connect", return_value=None):
            state = economy_routes_module._lottery_state()

        self.assertEqual(state["pot"], LOTTERY_BASE_POT)
        self.assertGreater(state["next_draw"], int(time.time()))
        self.assertLessEqual(state["next_draw"], int(time.time()) + LOTTERY_DRAW_INTERVAL)
        self.assertEqual((state["participants"], state["tickets"]), (0, 0))

    def test_the_entered_state_uses_the_dashboard_accent_not_a_new_colour(self):
        card = dashboard_rule(".dashboard-layout .lottery-card")
        entered = dashboard_rule(".dashboard-layout .lottery-card.is-entered")
        self.assertIn("var(--line-soft)", card)
        self.assertIn("var(--filter-border)", entered)
        self.assertIn("var(--filter-active)", entered)


class AchievementProgressBarStyleTests(unittest.TestCase):
    """The bar has to draw the badge's real progress, not just its grey track.

    The fill is a ``<span>`` with an inline percentage width, and the browser
    ignores ``width``/``height`` on an inline element — without a block-level
    display the fill vanishes and every badge shows an empty bar.
    """

    def test_the_fill_is_laid_out_so_its_percentage_width_applies(self):
        track = dashboard_rule(".dashboard-layout .achievement-bar")
        fill = dashboard_rule(".dashboard-layout .achievement-bar-fill")

        # Either the fill is laid out itself or the track blockifies its children.
        blockifies_children = bool(re.search(r"display:\s*(flex|grid|block)", track))
        self.assertTrue(
            blockifies_children
            or bool(re.search(r"display:\s*(block|flex|grid)|position:\s*absolute|float:\s*\w", fill)),
            "an inline fill ignores the width and height the bar sets on it",
        )
        # A second rule could quietly override the layout again.
        css = (ROOT / "web" / "src" / "styles.css").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"\.achievement-bar-fill\s*\{", css)), 1)
        # The filled portion is the accent colour, never the grey track colour.
        self.assertIn("var(--sage)", fill)
        self.assertNotIn("var(--toggle-off)", fill)

    def test_the_bar_binds_the_payload_percent_to_the_fill_width(self):
        view = (ROOT / "web" / "src" / "components" / "dashboard" / "AchievementsView.tsx").read_text(encoding="utf-8")
        self.assertIn("progress.percent", view)
        self.assertRegex(view, r'className="achievement-bar-fill"[^>]*width:\s*`\$\{[^}]+\}%`')


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
            "balance", "bank", "net_worth", "level", "job", "job_name", "bank_tier",
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
                for key in ("id", "name", "emoji", "icon_url", "season", "description", "reward", "unlocked", "progress"):
                    self.assertIn(key, entry)
                self.assertEqual(entry["icon_url"], TOPGG_LOGO_URL if is_voting_badge(entry["id"]) else None)
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
