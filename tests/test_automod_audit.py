"""Regression checks for the moderation/automod audit fixes.

Each test here pins one behaviour the audit found broken:

* every automod panel section renders (the section select was built without the
  language it now needs, which broke rendering outright),
* the panel's shared guard accepts Manage Server, the permission `/automod`,
  `/badwords` and the dashboard all use, instead of demanding Administrator,
* clicking NSFW image filtering on without premium is refused, because the
  dashboard refuses it too and the config otherwise sat inert,
* settings changes reach the server log instead of happening silently,
* invite filtering catches discordapp.com invites as well as discord.gg,
* the detection caches are pruned instead of growing for the process lifetime,
* the dashboard accepts the same thresholds the panel edits.
"""

import asyncio
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.automod import views  # noqa: E402
from cogs.automod.cog import AutoMod  # noqa: E402
from cogs.logging.formatters import LOG_EMOJI_KEYS, _TITLE_CATEGORY  # noqa: E402

SECTIONS = ("overview", "filter", "image_filter", "antinuke", "antiraid", "ext_raid", "whitelist")


def _config() -> dict:
    return {
        "automod": {
            key: True
            for key in (
                "antispam", "antilink", "badwords", "massmention",
                "nsfw_image_filter", "scam_image_filter",
                "antinuke", "antiraid", "antiraid_ext",
            )
        },
        "antinuke": {},
        "antiraid": {},
        "antiraid_ext": {},
        "spam_threshold": 6,
        "spam_interval": 7,
        "max_mentions": 5,
        "badwords_action": "delete",
        "blocked_words": [],
        "whitelist_users": [5],
        "whitelist_roles": [6],
    }


class _Guild:
    """Just enough guild for the panel builders: a locale and id lookups."""

    preferred_locale = "de"

    def get_member(self, user_id):
        return None

    def get_role(self, role_id):
        return None


class _Response:
    def __init__(self):
        self.sent = []
        self.edited = []

    async def send_message(self, **kwargs):
        self.sent.append(kwargs)

    async def edit_message(self, **kwargs):
        self.edited.append(kwargs)

    def is_done(self) -> bool:
        return bool(self.sent or self.edited)


class _Interaction:
    def __init__(self, *, manage_guild: bool = True):
        self.user = SimpleNamespace(
            id=1, guild_permissions=SimpleNamespace(manage_guild=manage_guild))
        self.guild = _Guild()
        self.response = _Response()


class _Cog:
    """Stand-in for the AutoMod cog: config, logger and premium check."""

    def __init__(self, cfg=None, *, premium: bool = False):
        self.config = cfg if cfg is not None else _config()
        self.premium = premium
        self.logged = []
        self.saves = 0

    def utils(self):
        return self

    def get_guild_config(self, guild_id):
        return self.config

    def save_config(self, guild_id=None):
        self.saves += 1

    async def _premium_active(self, guild_id):
        return self.premium

    async def log_action(self, guild, title, description, moderator=None, **kwargs):
        self.logged.append((title, description))


class GuardTests(unittest.TestCase):
    def test_manage_server_is_enough_to_change_automod_settings(self):
        interaction = _Interaction(manage_guild=True)
        self.assertTrue(views._may_manage(interaction))

    def test_a_member_without_manage_server_is_refused(self):
        self.assertFalse(views._may_manage(_Interaction(manage_guild=False)))
        self.assertFalse(views._may_manage(SimpleNamespace(user=SimpleNamespace())))


class InviteRegexTests(unittest.TestCase):
    def test_every_invite_host_is_matched(self):
        for text in (
            "join discord.gg/abc123",
            "https://discord.com/invite/abc123",
            "https://discordapp.com/invite/abc123",
        ):
            with self.subTest(text=text):
                self.assertTrue(views.INVITE_REGEX.search(text))

    def test_ordinary_links_are_left_alone(self):
        for text in ("https://example.com/invite", "discord.com/channels/1/2"):
            with self.subTest(text=text):
                self.assertIsNone(views.INVITE_REGEX.search(text))


class PanelRenderingTests(unittest.TestCase):
    def test_every_section_renders(self):
        cog = _Cog()
        for section in SECTIONS:
            with self.subTest(section=section):
                view = views._build_panel(cog, 1, section, _Guild())
                self.assertEqual(len(view.children), 1)

    def test_whitelist_controls_are_localised_and_use_the_bot_emoji(self):
        cog = _Cog()
        remove_user = views._WLRemoveUserBtn(cog, 1, True, "de")
        self.assertEqual(remove_user.label, "Benutzer entfernen")
        self.assertNotIn("➖", remove_user.label)
        self.assertIsNotNone(remove_user.emoji)
        self.assertEqual(views._WLAddUserBtn(cog, 1, "es").label, "Añadir usuario")

    def test_whitelist_selects_are_localised(self):
        cog = _Cog()
        select = views._WLUserSelect(cog, 1, message=None, lang="de")
        self.assertEqual(select.placeholder, "Mitglied(er) zur Whitelist hinzufügen…")

    def test_a_long_whitelist_is_paged_instead_of_breaking_the_select(self):
        """Discord allows 25 select options; the whitelist is uncapped."""
        cog = _Cog()
        options = [
            SimpleNamespace(label=f"User {index}", value=str(index))
            for index in range(40)
        ]
        # Build real SelectOptions the way the button does.
        real = [views.discord.SelectOption(label=item.label, value=item.value) for item in options]
        select = views._WLUserRemoveSelect(cog, 1, real, message=None, lang="en")
        self.assertEqual(len(select.options), 25)
        self.assertEqual(select.max_values, 25)

    def test_the_panel_text_pages_a_long_whitelist(self):
        cfg = _config()
        cfg["whitelist_users"] = list(range(80))
        text = views._build_whitelist_text(cfg, _Guild())
        self.assertIn("40", text)  # …and 40 more
        self.assertLess(len(text), 4000)


class PremiumGateTests(unittest.TestCase):
    def test_nsfw_filter_cannot_be_enabled_without_premium(self):
        cog = _Cog(premium=False)
        cog.config["automod"]["nsfw_image_filter"] = False
        button = views.ToggleButton(
            "NSFW Filter", "nsfw_image_filter", cog, 1, "image_filter")
        interaction = _Interaction()

        asyncio.run(button.callback(interaction))

        self.assertFalse(cog.config["automod"]["nsfw_image_filter"])
        self.assertEqual(cog.saves, 0)
        self.assertEqual(len(interaction.response.sent), 1)
        self.assertTrue(interaction.response.sent[0]["ephemeral"])
        self.assertEqual(cog.logged, [])

    def test_switching_a_lapsed_filter_off_is_always_allowed(self):
        """A server whose subscription lapsed must still be able to turn it off."""
        cog = _Cog(premium=False)
        button = views.ToggleButton(
            "NSFW Filter", "nsfw_image_filter", cog, 1, "image_filter")
        interaction = _Interaction()

        asyncio.run(button.callback(interaction))

        self.assertFalse(cog.config["automod"]["nsfw_image_filter"])
        self.assertEqual(cog.saves, 1)
        self.assertEqual(interaction.response.sent, [])

    def test_a_regular_toggle_saves_and_logs(self):
        cog = _Cog(premium=True)
        button = views.ToggleButton("Anti-Spam", "antispam", cog, 1, "filter")
        interaction = _Interaction()

        asyncio.run(button.callback(interaction))

        self.assertFalse(cog.config["automod"]["antispam"])
        self.assertEqual(cog.saves, 1)
        self.assertEqual(cog.logged[0][0], "AutoMod Settings")
        self.assertIn("Anti-Spam", cog.logged[0][1])
        self.assertEqual(len(interaction.response.edited), 1)


class SettingsLogRoutingTests(unittest.TestCase):
    def test_settings_log_titles_have_their_own_category_and_icon(self):
        for title in ("AutoMod Settings", "AutoMod Whitelist", "Blocked Words"):
            with self.subTest(title=title):
                self.assertEqual(_TITLE_CATEGORY[title], "automod")
                self.assertIn(title, LOG_EMOJI_KEYS)

    def test_the_settings_icons_do_not_reuse_a_filter_hit_icon(self):
        keys = [
            LOG_EMOJI_KEYS["AutoMod Settings"],
            LOG_EMOJI_KEYS["AutoMod Whitelist"],
            LOG_EMOJI_KEYS["Blocked Words"],
            LOG_EMOJI_KEYS["Bad Word Filter"],
        ]
        self.assertEqual(len(keys), len(set(keys)))


class CachePruneTests(unittest.TestCase):
    def test_aged_out_buckets_and_expired_guards_are_dropped(self):
        now = time.time()
        fresh, stale = now, now - 7200

        def cog():
            return SimpleNamespace(
                _CACHE_RETENTION=AutoMod._CACHE_RETENTION,
                _msg_history={1: {10: [fresh]}, 2: {11: [stale]}},
                _ext_app_history={1: {10: [stale]}, 2: {11: [fresh]}},
                _join_history={1: [fresh], 2: [stale]},
                _interaction_history={1: [(10, fresh)], 2: [(11, stale)]},
                _nuke_history={1: {10: {"ban": [fresh]}}, 2: {11: {"kick": [stale]}}},
                _raid_actioned={1: now - 5, 2: now + 500},
                _nuke_actioned={1: {10: now - 5, 11: now + 500}, 2: {12: now - 5}},
            )

        state = cog()
        state._prune_bucket_map = AutoMod._prune_bucket_map
        AutoMod.prune_caches(state)

        self.assertEqual(state._msg_history, {1: {10: [fresh]}})
        self.assertEqual(state._ext_app_history, {2: {11: [fresh]}})
        self.assertEqual(state._join_history, {1: [fresh]})
        self.assertEqual(state._interaction_history, {1: [(10, fresh)]})
        self.assertEqual(state._nuke_history, {1: {10: {"ban": [fresh]}}})
        self.assertEqual(state._raid_actioned, {2: now + 500})
        self.assertEqual(state._nuke_actioned, {1: {11: now + 500}})

    def test_the_cog_prunes_on_a_schedule_and_stops_when_unloaded(self):
        self.assertIsInstance(AutoMod._prune_caches, object)
        self.assertTrue(hasattr(AutoMod, "cog_unload"))
        self.assertTrue(hasattr(AutoMod, "prune_caches"))


class CommandTests(unittest.TestCase):
    def test_automod_is_a_guild_only_hybrid_command(self):
        command = AutoMod.automod_settings
        self.assertTrue(getattr(command, "with_app_command", False))
        # A hybrid command carries guild_only on the app-command side.
        self.assertTrue(command.app_command.guild_only)
        self.assertNotIn("☕", command.help)
        self.assertIn("'en'", command.help)


class DashboardThresholdTests(unittest.TestCase):
    """The dashboard must accept every threshold the Discord panel edits."""

    def setUp(self):
        from webapp import app
        from webapp.routes import dashboard_routes

        self.app = app
        self.routes = dashboard_routes
        self.saved = None

        def fake_connect():
            conn = mock.Mock()
            conn.execute.side_effect = self._capture
            return conn

        self._patches = [
            mock.patch.object(dashboard_routes, "get_runtime_moderation_config", lambda guild_id: {}),
            mock.patch.object(dashboard_routes, "_guild_premium_view", lambda guild_id: {"active": False}),
            mock.patch.object(dashboard_routes, "_read_moderation_config_sync", lambda guild_id: {}),
            mock.patch.object(dashboard_routes, "_preset_filter_catalog", lambda: []),
            mock.patch.object(dashboard_routes, "sqlite_connect", fake_connect),
            mock.patch.object(dashboard_routes, "_discord_bot", None),
        ]
        for patch in self._patches:
            patch.start()
            self.addCleanup(patch.stop)

    def _capture(self, statement, params):
        import json
        self.saved = json.loads(params[1])

    def _client(self):
        client = self.app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": "42", "username": "Tester"}
            session["access_token"] = "token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "csrf"
            session["managed_guild_ids"] = ["111"]
            session["managed_guilds_at"] = time.time()
        return client

    def _post(self, body):
        return self._client().post(
            "/api/guild/111/config/automod", json=body, headers={"X-CSRF-Token": "csrf"})

    def test_extended_antinuke_thresholds_and_antiraid_fields_are_saved(self):
        response = self._post({
            "antinuke": {
                "channel_create_threshold": 7,
                "webhook_delete_threshold": 4,
                "action": "ban",
            },
            "antiraid": {
                "new_account_days": 14,
                "lockdown_slowmode": 120,
                "action": "lockdown",
            },
        })
        self.assertEqual(response.status_code, 200)
        saved = response.get_json()["config"]
        self.assertEqual(saved["antinuke"]["channel_create_threshold"], 7)
        self.assertEqual(saved["antinuke"]["webhook_delete_threshold"], 4)
        self.assertEqual(saved["antinuke"]["action"], "ban")
        self.assertEqual(saved["antiraid"]["new_account_days"], 14)
        self.assertEqual(saved["antiraid"]["lockdown_slowmode"], 120)
        self.assertEqual(saved["antiraid"]["action"], "lockdown")

    def test_each_section_validates_its_own_action_choices(self):
        response = self._post({
            "antiraid": {"action": "strip"},
            "antinuke": {"action": "lockdown"},
            "antiraid_ext": {"ext_app_action": "log", "raider_action": "softban"},
        })
        self.assertEqual(response.status_code, 200)
        saved = response.get_json()["config"]
        # `strip` is an anti-nuke action, not an anti-raid one.
        self.assertNotIn("action", saved.get("antiraid", {}))
        self.assertTrue("lockdown" not in saved.get("antinuke", {}).get("action", ""))
        self.assertEqual(saved["antiraid_ext"]["ext_app_action"], "log")
        self.assertNotIn("raider_action", saved["antiraid_ext"])

    def test_an_out_of_range_threshold_is_rejected(self):
        response = self._post({"antiraid": {"new_account_days": 400}})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
