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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from webapp import app  # noqa: E402
from webapp.economy_routes import TOPGG_LOGO_URL, achievement_entries, economy_summary  # noqa: E402
from cogs.economy.seasons import season_status, season_window  # noqa: E402
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
            "kind": "vote", "amount": 550, "note": "top.gg vote · streak 2", "ts": 1_700_000_000,
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
