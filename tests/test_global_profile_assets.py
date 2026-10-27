"""Niko's global avatar/banner, which the customization tab shows per server.

A server that has not set its own profile images has to keep *inheriting* Niko's
global identity, so the server config carries them separately from
`server.profile`. Each image is resolved on its own: the cached bot user is
authoritative, and the REST read fills in whatever the gateway user object does
not carry (it only includes a banner when one is set). Getting that wrong is
silent — the preview just shows the letter placeholder forever.
"""

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from webapp import server  # noqa: E402
from webapp import discord_api  # noqa: E402
from webapp import discord_api, guilds, runtime  # noqa: E402
from webapp import config as webapp_config  # noqa: E402

AVATAR_URL = "https://cdn.discordapp.com/avatars/7/a_hash.png"
BANNER_URL = "https://cdn.discordapp.com/banners/7/b_hash.png?size=1024"


def _response(payload, status_code=200):
    return SimpleNamespace(status_code=status_code, json=lambda: payload)


def _user(*, avatar_url=AVATAR_URL, banner_url=BANNER_URL):
    return SimpleNamespace(
        id=7,
        display_avatar=SimpleNamespace(url=avatar_url) if avatar_url else None,
        banner=SimpleNamespace(url=banner_url) if banner_url else None,
    )


class GlobalProfileAssetTests(unittest.TestCase):
    def setUp(self):
        self._bot = runtime._discord_bot
        self._token = webapp_config.DISCORD_BOT_TOKEN
        webapp_config.DISCORD_BOT_TOKEN = "test-token"

    def tearDown(self):
        runtime._discord_bot = self._bot
        webapp_config.DISCORD_BOT_TOKEN = self._token

    def test_both_images_come_from_the_cached_bot_user(self):
        runtime._discord_bot = SimpleNamespace(user=_user())

        def no_rest(*args, **kwargs):
            raise AssertionError("a complete cached user must not cost a REST call")

        with mock.patch.object(discord_api, "discord_request", no_rest):
            self.assertEqual(
                guilds._global_profile_assets(),
                {"avatar_url": AVATAR_URL, "banner_url": BANNER_URL},
            )

    def test_a_cached_user_without_a_banner_fills_it_in_from_rest(self):
        runtime._discord_bot = SimpleNamespace(user=_user(banner_url=None))

        with mock.patch.object(
            discord_api,
            "discord_request",
            lambda *args, **kwargs: _response({"id": "7", "avatar": "a_hash", "banner": "b_hash"}),
        ):
            assets = guilds._global_profile_assets()

        self.assertEqual(assets["avatar_url"], AVATAR_URL)
        self.assertEqual(assets["banner_url"], "https://cdn.discordapp.com/banners/7/b_hash.png?size=1024")

    def test_an_animated_banner_keeps_its_extension(self):
        runtime._discord_bot = None

        with mock.patch.object(
            discord_api,
            "discord_request",
            lambda *args, **kwargs: _response({"id": "7", "avatar": "static_hash", "banner": "a_animated"}),
        ):
            assets = guilds._global_profile_assets()

        self.assertEqual(assets["avatar_url"], "https://cdn.discordapp.com/avatars/7/static_hash.png?size=512")
        self.assertEqual(assets["banner_url"], "https://cdn.discordapp.com/banners/7/a_animated.gif?size=1024")

    def test_a_refused_rest_read_leaves_the_missing_image_empty(self):
        runtime._discord_bot = SimpleNamespace(user=_user(banner_url=None))

        with mock.patch.object(discord_api, "discord_request", lambda *args, **kwargs: _response({}, 403)):
            self.assertEqual(
                guilds._global_profile_assets(),
                {"avatar_url": AVATAR_URL, "banner_url": None},
            )

    def test_a_raising_rest_read_never_breaks_the_config(self):
        runtime._discord_bot = SimpleNamespace(user=_user(banner_url=None))

        def boom(*args, **kwargs):
            raise RuntimeError("network down")

        with mock.patch.object(discord_api, "discord_request", boom):
            self.assertEqual(guilds._global_profile_assets()["banner_url"], None)

    def test_without_a_token_or_a_bot_the_assets_are_empty(self):
        runtime._discord_bot = None
        webapp_config.DISCORD_BOT_TOKEN = ""

        with mock.patch.object(discord_api, "discord_request", lambda *args, **kwargs: _response({})):
            self.assertEqual(
                guilds._global_profile_assets(),
                {"avatar_url": None, "banner_url": None},
            )

    def test_the_server_config_exposes_the_global_assets(self):
        """The customization tab reads `config.server.global_profile`."""
        runtime._discord_bot = SimpleNamespace(user=_user())

        def fake_loop(value, timeout=None):
            # The real loaders would need a database; nothing here asserts their
            # output, only that the global assets reach the config payload.
            close = getattr(value, "close", None)
            if callable(close):
                close()
            return None

        with mock.patch.object(runtime, "run_on_bot_loop", fake_loop), \
             mock.patch.object(guilds, "_get_runtime_guild_profile", lambda guild_id: {}), \
             mock.patch.object(guilds, "_serialize_onboarding_config", lambda config: {}), \
             mock.patch.object(guilds, "_serialize_ticket_config", lambda config: {}), \
             mock.patch("cogs.logging.formatters._load_log_config", lambda: {}), \
             mock.patch("cogs.logging.formatters._guild_config", lambda data, guild_id: {}):
            config = guilds._get_runtime_server_config("111")

        self.assertEqual(
            config["global_profile"],
            {"avatar_url": AVATAR_URL, "banner_url": BANNER_URL},
        )


if __name__ == "__main__":
    unittest.main()
