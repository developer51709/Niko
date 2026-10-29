"""Niko's own README profile card: the live snapshot and the SVG document.

The card is fetched by GitHub inside an ``<img>`` and has to look like the staff
profile cards while showing the running bot's real figures. These tests pin the
contract: the document parses on its own, the live counts are rendered from the
bot (not a stored snapshot), and the route never lets a proxy reuse an old card.

Run with:  python -m pytest tests/test_bot_card.py -v
"""

import asyncio
import re
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import bot_card  # noqa: E402
from webapp.routes import public_routes  # noqa: E402
from webapp.server import app  # noqa: E402

AVATAR = "https://cdn.discordapp.com/avatars/1/avatar.png"


def profile(**overrides):
    data = {
        "name": "Niko",
        "handle": "niko",
        "avatar_url": AVATAR,
        "online": True,
        "guild_count": 12345,
        "user_count": 987654,
        "command_count": 323,
        "latency_ms": 42,
        "uptime_seconds": 3 * 86400 + 4 * 3600 + 12 * 60,
        "version": "1.0",
    }
    data.update(overrides)
    return data


class BotCardSvgTests(unittest.TestCase):
    def render(self, data, **kwargs):
        kwargs.setdefault("avatar_data_url", None)
        svg = bot_card.render_bot_card(data, **kwargs)
        ElementTree.fromstring(svg)
        return svg

    def test_card_shows_the_bot_and_its_live_figures(self):
        svg = self.render(profile())
        self.assertIn("Niko", svg)
        self.assertIn("@niko", svg)
        self.assertIn(bot_card.CHIP_LABEL, svg)
        self.assertIn("12.3k", svg)   # servers
        self.assertIn("987.7k", svg)  # members
        self.assertIn("323", svg)     # commands
        self.assertIn("42 ms", svg)
        self.assertIn("3d 4h", svg)
        for label in ("SERVERS", "MEMBERS", "COMMANDS", "PING", "UPTIME"):
            self.assertIn(label, svg)

    def test_a_small_server_stays_readable(self):
        svg = self.render(profile(guild_count=2, user_count=9, command_count=76,
                                  latency_ms=8, uptime_seconds=12 * 60))
        self.assertIn(">2<", svg)
        self.assertIn(">9<", svg)
        self.assertIn("8 ms", svg)
        self.assertIn("12m", svg)

    def test_offline_bot_uses_the_offline_status_and_unknown_figures(self):
        svg = self.render(profile(online=False, latency_ms=None, uptime_seconds=None))
        offline = bot_card.status_icon_data_url("offline")
        online = bot_card.status_icon_data_url("online")
        self.assertEqual(svg.count(offline), 1)
        self.assertNotIn(online, svg)
        self.assertIn("\u2014", svg)

    def test_theme_and_accent_override_the_defaults(self):
        svg = self.render(profile(), theme="light", accent="#ff0066")
        self.assertIn("#FF0066", svg)
        self.assertIn("#FBF8F3", svg)  # light gradient
        self.assertIn(f"#{bot_card.DEFAULT_ACCENT}", self.render(profile()))

    def test_text_is_xml_escaped(self):
        svg = self.render(profile(name="<script>alert(1)</script>", handle="a&b"))
        self.assertNotIn("<script>", svg)
        self.assertIn("&lt;script&gt;", svg)
        self.assertIn("a&amp;b", svg)

    def test_no_external_references_are_emitted(self):
        svg = self.render(profile(), avatar_data_url="data:image/png;base64,AAAA")
        self.assertNotIn("<style", svg)
        self.assertNotIn("@import", svg)
        self.assertIn('href="data:image/png;base64,AAAA"', svg)

    def test_missing_avatar_falls_back_to_the_brand_letter(self):
        svg = self.render(profile())
        self.assertIn(">n</text>", svg)


class BotProfileSnapshotTests(unittest.TestCase):
    """``_bot_card_profile`` reads the running bot rather than the old snapshot."""

    def setUp(self):
        self.previous = public_routes._discord_bot
        self.bot = SimpleNamespace(
            guilds=[SimpleNamespace(member_count=10), SimpleNamespace(member_count=5)],
            user=SimpleNamespace(
                display_name="Niko",
                name="niko",
                display_avatar=SimpleNamespace(url=AVATAR),
            ),
            latency=0.042,
            start_time=time.time() - 90,
            _status_command_count=76,
            is_ready=lambda: True,
        )
        public_routes._discord_bot = self.bot

    def tearDown(self):
        public_routes._discord_bot = self.previous

    def test_live_counts_identity_and_metrics_are_merged(self):
        with patch.object(public_routes, "run_on_bot_loop",
                          side_effect=lambda coro, timeout=8: asyncio.run(coro)):
            snapshot = public_routes._bot_card_profile()

        self.assertTrue(snapshot["online"])
        self.assertEqual(snapshot["name"], "Niko")
        self.assertEqual(snapshot["handle"], "niko")
        self.assertEqual(snapshot["avatar_url"], AVATAR)
        self.assertEqual(snapshot["guild_count"], 2)
        self.assertEqual(snapshot["user_count"], 15)
        self.assertEqual(snapshot["command_count"], 76)
        self.assertEqual(snapshot["latency_ms"], 42)
        self.assertGreaterEqual(snapshot["uptime_seconds"], 89)

    def test_a_stopped_gateway_falls_back_to_the_snapshot(self):
        public_routes._discord_bot = None
        snapshot = public_routes._bot_card_profile()
        self.assertFalse(snapshot["online"])
        self.assertIsNone(snapshot["latency_ms"])
        self.assertEqual(snapshot["name"], "Niko")
        self.assertIsInstance(snapshot["guild_count"], int)


class BotCardRouteTests(unittest.TestCase):
    def get(self, path, data):
        with patch.object(public_routes, "_bot_card_profile", return_value=data), \
             patch.object(public_routes, "avatar_data_url", return_value=None):
            return app.test_client().get(path)

    def test_route_serves_a_public_svg_card(self):
        response = self.get("/bot/card.svg", profile())
        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/svg+xml")
        # The figures are live: no proxy or browser may reuse a rendered card.
        self.assertIn("no-store", response.headers["Cache-Control"])
        self.assertEqual(response.headers["Pragma"], "no-cache")
        ElementTree.fromstring(body)
        self.assertIn("Niko", body)
        self.assertIn("12.3k", body)

    def test_the_card_follows_the_live_figures(self):
        client = app.test_client()
        with patch.object(public_routes, "_bot_card_profile",
                          side_effect=[profile(guild_count=10), profile(guild_count=4200)]), \
             patch.object(public_routes, "avatar_data_url", return_value=None):
            first = client.get("/bot/card.svg").get_data(as_text=True)
            second = client.get("/bot/card.svg").get_data(as_text=True)

        self.assertIn(">10<", first)
        self.assertIn(">4,200<", second)
        self.assertNotIn(">4,200<", first)

    def test_preview_overrides_match_the_card_customisation(self):
        body = self.get("/bot/card.svg?theme=light&accent=FF0066", profile()).get_data(as_text=True)
        self.assertIn("#FF0066", body)
        self.assertIn("#FBF8F3", body)

    def test_the_readme_uses_the_custom_banner_and_the_live_card(self):
        readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
        self.assertIn('src="docs/assets/niko_banner.svg"', readme)
        self.assertIn('src="https://niko.sryze.cc/bot/card.svg"', readme)
        self.assertNotIn("niko_banner_2.png", readme)

    def test_the_banner_is_a_self_contained_svg(self):
        banner = (Path(__file__).resolve().parents[1] / "docs" / "assets" / "niko_banner.svg")
        source = banner.read_text(encoding="utf-8")
        ElementTree.fromstring(source)
        self.assertNotIn("<style", source)
        self.assertNotIn("@import", source)
        self.assertIsNone(re.search(r'href="https?://', source))

    def test_the_banner_corners_are_cut_out_rather_than_painted(self):
        """A rounded hairline over a square fill shows dark square corners."""
        banner = (Path(__file__).resolve().parents[1] / "docs" / "assets" / "niko_banner.svg")
        source = banner.read_text(encoding="utf-8")
        self.assertIn('<clipPath id="niko-banner-frame">', source)
        self.assertIn('clip-path="url(#niko-banner-frame)"', source)
        self.assertIn('<rect x="0" y="0" width="1200" height="400" rx="28"/>', source)
        # Every painted layer sits inside the clip; only the hairline is outside.
        clip = source.split('<g clip-path="url(#niko-banner-frame)">', 1)[1]
        outside = clip.split("</g>", 1)[1]
        self.assertNotIn("fill=\"url(#niko-banner-bg)\"", outside)
        self.assertLess(outside.count("<rect"), 2)


if __name__ == "__main__":
    unittest.main()
