"""Staff README cards: the SVG document, its settings, and its avatar rules.

The card is fetched by GitHub inside an ``<img>``, so it must be a single,
well-formed SVG with no external references. These tests pin that contract:
the document parses, the name/role/live status are rendered from the roster
row, saved presentation settings are honoured, and only Discord avatars are
inlined.

Run with:  python -m pytest tests/test_staff_card.py -v
"""

import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import staff_card  # noqa: E402
from webapp.routes import team_routes  # noqa: E402
from webapp.server import app  # noqa: E402


def member(**overrides):
    data = {
        "id": "42",
        "name": "Nova Example",
        "username": "nova",
        "role": "moderator",
        "role_label": "Moderator",
        "status": "idle",
        "status_label": "Idle",
        "activities": [],
        "custom_status": None,
        "card": {"theme": "dark", "accent": "C8A882", "show_status": True},
    }
    data.update(overrides)
    return data


def card_height(svg: str) -> int:
    return int(re.search(r'<svg[^>]*height="(\d+)"', svg).group(1))


SPOTIFY_ACTIVITY = {
    "kind": "spotify",
    "type": "listening",
    "name": "Spotify",
    "details": "Midnight City",
    "state": "M83",
    "image_url": "https://i.scdn.co/image/cover",
}

GAME_ACTIVITY = {
    "kind": "activity",
    "type": "playing",
    "name": "Visual Studio Code",
    "details": "Editing card.svg",
    "state": None,
    "image_url": None,
}


class FakeResponse:
    def __init__(self, content=b"\x89PNG\r\n", content_type="image/png", ok=True):
        self.content = content
        self.headers = {"Content-Type": content_type}
        self.ok = ok


class CardSvgTests(unittest.TestCase):
    def render(self, member_data, **kwargs):
        kwargs.setdefault("avatar_data_url", None)
        svg = staff_card.render_staff_card(member_data, **kwargs)
        # The document must parse on its own: GitHub renders it without a page.
        ElementTree.fromstring(svg)
        return svg

    def test_card_shows_the_name_role_and_live_status(self):
        svg = self.render(member())
        self.assertIn("Nova Example", svg)
        self.assertIn("NIKO STAFF \u00b7 MODERATOR", svg)
        # The website's status art replaces the coloured dot and its label, and
        # it is drawn on the avatar only.
        icon = staff_card.status_icon_data_url("idle")
        self.assertEqual(svg.count(icon), 1)
        self.assertNotIn(">Idle<", svg)
        self.assertNotIn(staff_card.STATUS_COLORS["idle"], svg)
        # The card carries no footer label or profile URL.
        self.assertNotIn("NIKO STAFF CARD", svg)
        self.assertNotIn("/team/42", svg)

    def test_custom_status_replaces_the_activity_line(self):
        svg = self.render(member(custom_status={"text": "building cards", "emoji": None}))
        self.assertIn("building cards", svg)
        # The status art stays on the avatar; the text line adds no second icon.
        self.assertEqual(svg.count(staff_card.status_icon_data_url("idle")), 1)

    def test_first_activity_is_used_without_a_custom_status(self):
        svg = self.render(member(activities=[{
            "kind": "activity",
            "name": "Visual Studio Code",
            "details": "Editing card.svg",
        }]))
        self.assertIn("Visual Studio Code", svg)
        self.assertIn("Editing card.svg", svg)
        self.assertEqual(svg.count(staff_card.status_icon_data_url("idle")), 1)

    def test_status_can_be_hidden(self):
        svg = self.render(member(custom_status={"text": "building cards", "emoji": None}), show_status=False)
        self.assertNotIn("data:image/png", svg)
        self.assertNotIn("building cards", svg)
        self.assertIn("Nova Example", svg)

    def test_saved_show_status_setting_is_used(self):
        svg = self.render(member(card={"theme": "dark", "accent": None, "show_status": False}))
        self.assertNotIn("data:image/png", svg)

    def test_theme_and_accent_override_the_saved_settings(self):
        svg = self.render(member(), theme="light", accent="#ff0066")
        self.assertIn("#FF0066", svg)
        self.assertIn("#FBF8F3", svg)  # light background gradient

    def test_default_accent_is_the_brand_colour(self):
        svg = self.render(member(card={"theme": "dark", "accent": None, "show_status": True}))
        self.assertIn(f"#{staff_card.DEFAULT_ACCENT}", svg)

    def test_missing_avatar_falls_back_to_the_name_initial(self):
        svg = self.render(member())
        self.assertIn(">N</text>", svg)

    def test_hidden_profile_renders_a_neutral_card(self):
        svg = self.render(None)
        self.assertIn("This profile is not public right now.", svg)
        self.assertNotIn("Nova Example", svg)

    def test_unknown_status_falls_back_to_the_offline_icon(self):
        svg = self.render(member(status="invisible"))
        self.assertIn(staff_card.status_icon_data_url("offline"), svg)
        self.assertNotIn(staff_card.status_icon_data_url("online"), svg)

    def test_text_is_xml_escaped(self):
        svg = self.render(member(name="<script>alert(1)</script>", username="a&b"))
        self.assertNotIn("<script>", svg)
        self.assertIn("&lt;script&gt;", svg)
        self.assertIn("a&amp;b", svg)

    def test_no_external_references_are_emitted(self):
        svg = self.render(member(), avatar_data_url="data:image/png;base64,AAAA")
        self.assertNotIn("<style", svg)
        self.assertNotIn("@import", svg)
        self.assertIn('href="data:image/png;base64,AAAA"', svg)


class ActivityCardTests(unittest.TestCase):
    def test_spotify_activity_renders_art_track_and_artist(self):
        with patch.object(staff_card, "activity_art_data_url",
                          return_value="data:image/jpeg;base64,QUJD") as art:
            svg = staff_card.render_staff_card(member(activities=[SPOTIFY_ACTIVITY]))
        art.assert_called_once_with("https://i.scdn.co/image/cover")
        self.assertEqual(card_height(svg), staff_card.CARD_HEIGHT_WITH_ACTIVITY)
        self.assertIn("LISTENING ON SPOTIFY", svg)
        self.assertIn("Midnight City", svg)
        self.assertIn("M83", svg)
        self.assertIn('href="data:image/jpeg;base64,QUJD"', svg)
        # The little Spotify glyph is the website asset, inlined as a path.
        self.assertTrue(staff_card._spotify_mark_path())
        self.assertIn(staff_card.SPOTIFY_GREEN, svg)

    def test_spotify_without_cover_art_falls_back_to_a_glyph_tile(self):
        with patch.object(staff_card, "activity_art_data_url", return_value=None):
            svg = staff_card.render_staff_card(member(activities=[SPOTIFY_ACTIVITY]))
        self.assertEqual(card_height(svg), staff_card.CARD_HEIGHT_WITH_ACTIVITY)
        self.assertNotIn("data:image/jpeg", svg)
        self.assertIn(staff_card.SPOTIFY_GREEN, svg)
        self.assertIn("Midnight City", svg)

    def test_game_activity_renders_its_name_and_details(self):
        svg = staff_card.render_staff_card(member(activities=[GAME_ACTIVITY]))
        self.assertEqual(card_height(svg), staff_card.CARD_HEIGHT_WITH_ACTIVITY)
        self.assertIn("PLAYING", svg)
        self.assertIn("Visual Studio Code", svg)
        self.assertIn("Editing card.svg", svg)
        self.assertNotIn(staff_card.SPOTIFY_GREEN, svg)

    def test_card_stays_short_without_an_activity(self):
        svg = staff_card.render_staff_card(member())
        self.assertEqual(card_height(svg), staff_card.CARD_HEIGHT)
        self.assertNotIn("LISTENING ON SPOTIFY", svg)

    def test_activity_follows_the_show_status_setting(self):
        svg = staff_card.render_staff_card(member(activities=[GAME_ACTIVITY]), show_status=False)
        self.assertEqual(card_height(svg), staff_card.CARD_HEIGHT)
        self.assertNotIn("Visual Studio Code", svg)

    def test_custom_status_and_activity_both_render(self):
        svg = staff_card.render_staff_card(member(
            activities=[SPOTIFY_ACTIVITY],
            custom_status={"text": "building cards", "emoji": None},
        ))
        self.assertIn("building cards", svg)
        self.assertIn("Midnight City", svg)
        self.assertEqual(card_height(svg), staff_card.CARD_HEIGHT_WITH_ACTIVITY)


class CardRouteTests(unittest.TestCase):
    def setUp(self):
        staff_card._avatar_cache.clear()

    def get(self, path, rows):
        with patch.object(team_routes, "_load_staff_rows", return_value=rows), \
             patch.object(team_routes, "avatar_data_url", return_value=None):
            return app.test_client().get(path)

    def test_route_serves_a_public_svg_card(self):
        response = self.get("/staff/42/card.svg", [member(status="online")])
        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/svg+xml")
        # Presence is live: no proxy or browser may reuse a rendered card.
        self.assertIn("no-store", response.headers["Cache-Control"])
        self.assertEqual(response.headers["Pragma"], "no-cache")
        ElementTree.fromstring(body)
        self.assertIn("Nova Example", body)

    def test_activity_changes_between_requests(self):
        first_member = member(activities=[SPOTIFY_ACTIVITY])
        second_member = member(activities=[GAME_ACTIVITY])
        with patch.object(team_routes, "_load_staff_rows", side_effect=[[first_member], [second_member]]), \
             patch.object(team_routes, "avatar_data_url", return_value=None), \
             patch.object(staff_card, "activity_art_data_url", return_value=None):
            client = app.test_client()
            first = client.get("/staff/42/card.svg").get_data(as_text=True)
            second = client.get("/staff/42/card.svg").get_data(as_text=True)

        self.assertIn("Midnight City", first)
        self.assertNotIn("Visual Studio Code", first)
        self.assertIn("Visual Studio Code", second)
        self.assertNotIn("Midnight City", second)

    def test_each_request_reads_the_roster_again(self):
        online = member(status="online")
        offline = member(status="offline")
        with patch.object(team_routes, "_load_staff_rows", side_effect=[[online], [offline]]) as roster, \
             patch.object(team_routes, "avatar_data_url", return_value=None):
            client = app.test_client()
            first = client.get("/staff/42/card.svg").get_data(as_text=True)
            second = client.get("/staff/42/card.svg").get_data(as_text=True)

        self.assertEqual(roster.call_count, 2)
        self.assertIn(staff_card.status_icon_data_url("online"), first)
        self.assertNotIn(staff_card.status_icon_data_url("online"), second)
        self.assertIn(staff_card.status_icon_data_url("offline"), second)

    def test_missing_or_hidden_profile_gets_the_neutral_card(self):
        response = self.get("/staff/42/card.svg", [])
        self.assertEqual(response.status_code, 200)
        self.assertIn("This profile is not public right now.", response.get_data(as_text=True))

    def test_preview_overrides_match_the_dashboard_draft(self):
        response = self.get("/staff/42/card.svg?theme=light&accent=FF0066&status=0", [member()])
        body = response.get_data(as_text=True)
        self.assertIn("#FF0066", body)
        self.assertIn("#FBF8F3", body)
        self.assertNotIn(">Idle<", body)


class StatusIconTests(unittest.TestCase):
    def setUp(self):
        staff_card._status_icon_cache.clear()

    def test_every_discord_status_icon_is_inlined(self):
        for status in ("online", "idle", "dnd", "offline"):
            icon = staff_card.status_icon_data_url(status)
            self.assertTrue(icon.startswith("data:image/png;base64,"), status)

    def test_unknown_status_uses_the_offline_icon(self):
        self.assertEqual(
            staff_card.status_icon_data_url("invisible"),
            staff_card.status_icon_data_url("offline"),
        )

    def test_icons_are_cached(self):
        first = staff_card.status_icon_data_url("online")
        self.assertIs(first, staff_card.status_icon_data_url("online"))

    def test_the_card_prints_no_status_words(self):
        for status in ("online", "idle", "dnd", "offline"):
            svg = staff_card.render_staff_card(member(status=status))
            for word in ("Online", "Idle", "Do Not Disturb", "Offline"):
                self.assertNotIn(f">{word}<", svg, status)


class CardSettingTests(unittest.TestCase):
    def test_validate_accent_accepts_both_hex_forms(self):
        self.assertEqual(staff_card.validate_accent("#c8a882"), "C8A882")
        self.assertEqual(staff_card.validate_accent("C8A882"), "C8A882")

    def test_validate_accent_resets_when_empty(self):
        self.assertEqual(staff_card.validate_accent(""), "")
        self.assertEqual(staff_card.validate_accent(None), "")

    def test_validate_accent_rejects_anything_else(self):
        self.assertIsNone(staff_card.validate_accent("brown"))
        self.assertIsNone(staff_card.validate_accent("#12345"))
        self.assertIsNone(staff_card.validate_accent("#12345678"))

    def test_normalize_theme_falls_back_to_dark(self):
        self.assertEqual(staff_card.normalize_theme("light"), "light")
        self.assertEqual(staff_card.normalize_theme("LIGHT"), "light")
        self.assertEqual(staff_card.normalize_theme("neon"), "dark")
        self.assertEqual(staff_card.normalize_theme(None), "dark")


class ActivityArtInliningTests(unittest.TestCase):
    def setUp(self):
        staff_card._art_cache.clear()

    def test_spotify_album_art_is_inlined_as_a_data_uri(self):
        with patch.object(staff_card.req, "get", return_value=FakeResponse()) as fetch:
            url = staff_card.activity_art_data_url("https://i.scdn.co/image/abc")
        fetch.assert_called_once()
        self.assertTrue(url.startswith("data:image/png;base64,"))

    def test_other_hosts_are_never_fetched(self):
        with patch.object(staff_card.req, "get") as fetch:
            self.assertIsNone(staff_card.activity_art_data_url("https://example.com/cover.jpg"))
        fetch.assert_not_called()

    def test_album_art_is_cached(self):
        with patch.object(staff_card.req, "get", return_value=FakeResponse()) as fetch:
            staff_card.activity_art_data_url("https://i.scdn.co/image/def")
            staff_card.activity_art_data_url("https://i.scdn.co/image/def")
        self.assertEqual(fetch.call_count, 1)


class AvatarInliningTests(unittest.TestCase):
    def setUp(self):
        staff_card._avatar_cache.clear()

    def test_discord_avatars_are_inlined_as_data_uris(self):
        with patch.object(staff_card.req, "get", return_value=FakeResponse()) as fetch:
            url = staff_card.avatar_data_url("https://cdn.discordapp.com/avatars/1/a.png")
        fetch.assert_called_once()
        self.assertTrue(url.startswith("data:image/png;base64,"))

    def test_other_hosts_are_never_fetched(self):
        with patch.object(staff_card.req, "get") as fetch:
            self.assertIsNone(staff_card.avatar_data_url("https://example.com/avatar.png"))
        fetch.assert_not_called()

    def test_non_image_responses_are_rejected(self):
        with patch.object(staff_card.req, "get", return_value=FakeResponse(b"<html>", "text/html")):
            self.assertIsNone(staff_card.avatar_data_url("https://media.discordapp.net/a.png"))

    def test_failed_fetches_are_rejected(self):
        with patch.object(staff_card.req, "get", side_effect=OSError("boom")):
            self.assertIsNone(staff_card.avatar_data_url("https://cdn.discordapp.com/a.png"))

    def test_inlined_avatars_are_cached(self):
        with patch.object(staff_card.req, "get", return_value=FakeResponse()) as fetch:
            staff_card.avatar_data_url("https://cdn.discordapp.com/avatars/2/b.png")
            staff_card.avatar_data_url("https://cdn.discordapp.com/avatars/2/b.png")
        self.assertEqual(fetch.call_count, 1)


if __name__ == "__main__":
    unittest.main()
