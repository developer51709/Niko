"""Regression checks for the team profile cards and Twitch app credentials.

Covers the three pieces that make the staff profile cards work:

* public profile lookups only ever contact a platform's own hosts,
* Twitch reuses one cached application (client-credentials) token,
* a Spotify presence keeps the track window the progress bar needs.
"""

import asyncio
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from webapp import app
from webapp import server as server_routes

from utils.social import profiles, twitch


def _response(payload, status_code=200):
    return SimpleNamespace(
        status_code=status_code,
        json=lambda: payload,
        raise_for_status=lambda: None,
    )


class ProfileLinkParsingTests(unittest.TestCase):
    def test_every_supported_platform_parses_its_own_url_shape(self):
        cases = {
            ("github", "https://github.com/torvalds"): "torvalds",
            ("bluesky", "https://bsky.app/profile/bsky.app"): "bsky.app",
            # Bluesky handles are domains, so a member's own handle URL counts.
            ("bluesky", "https://sorenthedev.bsky.social"): "sorenthedev.bsky.social",
            ("twitch", "https://www.twitch.tv/shroud"): "shroud",
            ("youtube", "https://www.youtube.com/@MrBeast"): "@MrBeast",
            ("youtube", "https://www.youtube.com/channel/UCX6OQ3DkcsbYNE6H8uQQuVA"): "UCX6OQ3DkcsbYNE6H8uQQuVA",
            ("reddit", "https://www.reddit.com/user/spez"): "u/spez",
            ("reddit", "https://www.reddit.com/r/programming"): "r/programming",
            ("x", "https://twitter.com/jack"): "jack",
        }
        for (platform, url), identifier in cases.items():
            with self.subTest(url=url):
                self.assertEqual(profiles.parse_link(platform, url), (platform, identifier))

    def test_foreign_hosts_and_unknown_platforms_are_rejected(self):
        for platform, url in (
            ("github", "https://github.evil.example/torvalds"),
            ("banana", "https://github.com/torvalds"),
            ("github", "not-a-url"),
        ):
            with self.subTest(url=url):
                with self.assertRaises(profiles.ProfileLookupError):
                    profiles.parse_link(platform, url)

    def test_video_shortlinks_are_not_profiles(self):
        with self.assertRaises(profiles.ProfileLookupError):
            profiles.parse_link("youtube", "https://youtu.be/dQw4w9WgXcQ")


class ProfileCardRouteTests(unittest.TestCase):
    def setUp(self):
        profiles._CACHE.clear()

    def test_route_returns_the_normalised_card(self):
        card = {
            "platform": "github",
            "display_name": "Test User",
            "handle": "test-user",
            "url": "https://github.com/test-user",
            "avatar_url": None,
            "bio": None,
            "stats": [{"label": "Repos", "value": "3"}],
            "status": None,
        }
        with patch.dict(profiles._LOADERS, {"github": lambda identifier: {**card, "handle": identifier}}):
            response = app.test_client().get(
                "/api/team/profile-card",
                query_string={"type": "github", "url": "https://github.com/test-user"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["card"]["handle"], "test-user")

    def test_route_rejects_links_that_do_not_belong_to_the_platform(self):
        response = app.test_client().get(
            "/api/team/profile-card",
            query_string={"type": "twitch", "url": "https://example.com/shroud"},
        )
        self.assertEqual(response.status_code, 400)

    def test_unavailable_profile_returns_a_clear_error(self):
        with patch.dict(profiles._LOADERS, {"github": lambda identifier: None}):
            response = app.test_client().get(
                "/api/team/profile-card",
                query_string={"type": "github", "url": "https://github.com/missing-profile"},
            )
        self.assertEqual(response.status_code, 404)
        self.assertIn("could not be loaded", response.get_json()["error"])


class TwitchApplicationCredentialTests(unittest.TestCase):
    def setUp(self):
        twitch._TOKEN_CACHE.update({"value": "", "expires_at": 0.0})

    def test_channel_lookup_mints_one_cached_app_token(self):
        users = _response({"data": [{
            "id": "1",
            "login": "shroud",
            "display_name": "shroud",
            "description": "hi",
            "profile_image_url": "https://example.test/avatar.png",
            "view_count": 1234,
            "created_at": "2012-01-01T00:00:00Z",
        }]})
        token = _response({"access_token": "app-token", "expires_in": 3600})
        with patch.dict(os.environ, {"TWITCH_CLIENT_ID": "cid", "TWITCH_CLIENT_SECRET": "secret"}), \
                patch("utils.social.twitch.requests.post", return_value=token) as post, \
                patch("utils.social.twitch.requests.get", side_effect=[users, users]) as get:
            first = twitch.fetch_channel("shroud")
            second = twitch.fetch_channel("shroud")

        self.assertEqual(first["login"], "shroud")
        self.assertEqual(second["login"], "shroud")
        # One token for both lookups, requested as an application credential.
        self.assertEqual(post.call_count, 1)
        self.assertEqual(post.call_args.kwargs["params"]["grant_type"], "client_credentials")
        self.assertEqual(get.call_count, 2)
        self.assertEqual(get.call_args_list[0].kwargs["headers"]["Client-Id"], "cid")
        self.assertEqual(get.call_args_list[0].kwargs["headers"]["Authorization"], "Bearer app-token")
        self.assertEqual(get.call_args_list[0].args[0], "https://api.twitch.tv/helix/users")

    def test_profile_card_reports_live_status(self):
        users = _response({"data": [{
            "id": "1",
            "login": "shroud",
            "display_name": "shroud",
            "description": "",
            "profile_image_url": None,
            "view_count": 10,
            "created_at": "2012-01-01T00:00:00Z",
        }]})
        streams = _response({"data": [{"id": "9", "game_name": "VALORANT", "title": "Ranked"}]})
        with patch.dict(os.environ, {"TWITCH_CLIENT_ID": "cid", "TWITCH_CLIENT_SECRET": "secret"}), \
                patch("utils.social.twitch.requests.post", return_value=_response({"access_token": "t", "expires_in": 3600})), \
                patch("utils.social.twitch.requests.get", side_effect=[users, streams]):
            card = profiles._twitch("shroud")

        self.assertEqual(card["platform"], "twitch")
        self.assertEqual(card["status"], "Live now · VALORANT")
        self.assertEqual(card["url"], "https://www.twitch.tv/shroud")

    def test_credentials_are_optional(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(twitch.credentials_configured())
            self.assertIsNone(twitch.access_token())
            self.assertIsNone(twitch.fetch_latest_twitch("shroud"))

    def test_notifier_uses_the_same_twitch_credentials(self):
        from cogs.notifier import cog as notifier

        self.assertIn("twitch", notifier.PLATFORMS)
        with patch.object(notifier, "validate_twitch_login", return_value=True):
            ok, stored = asyncio.run(notifier._validate("twitch", "https://www.twitch.tv/Shroud"))
        self.assertTrue(ok)
        self.assertEqual(stored, "Shroud")

        post = {"id": "stream:9", "url": "https://www.twitch.tv/shroud", "title": "Ranked"}
        with patch.object(notifier, "fetch_latest_twitch", return_value=post):
            self.assertEqual(asyncio.run(notifier._fetch("twitch", "shroud")), post)


class SpotifyPresenceTests(unittest.TestCase):
    def test_spotify_activity_keeps_the_track_window(self):
        class Spotify:
            type = SimpleNamespace(name="listening")
            title = "Song"
            artist = "Artist"
            track_url = "https://open.spotify.com/track/abc"
            album_cover_url = "https://example.test/cover.png"
            start = SimpleNamespace(isoformat=lambda: "2026-10-16T12:00:00+00:00")
            end = SimpleNamespace(isoformat=lambda: "2026-10-16T12:03:00+00:00")

        member = SimpleNamespace(
            status=SimpleNamespace(name="online"),
            activities=[Spotify()],
            global_name="Staffer",
            name="staffer",
            display_avatar=SimpleNamespace(url="https://example.test/avatar.png"),
            _user=None,
        )
        guild = SimpleNamespace(get_member=lambda user_id: member)
        bot = SimpleNamespace(guilds=[guild])
        previous = server_routes._discord_bot
        server_routes._discord_bot = bot
        try:
            identity = server_routes._staff_identity("42")
        finally:
            server_routes._discord_bot = previous

        self.assertEqual(len(identity["activities"]), 1)
        activity = identity["activities"][0]
        self.assertEqual(activity["kind"], "spotify")
        self.assertEqual(activity["start"], "2026-10-16T12:00:00+00:00")
        self.assertEqual(activity["end"], "2026-10-16T12:03:00+00:00")

    def test_presence_without_timestamps_still_serialises(self):
        class Spotify:
            type = SimpleNamespace(name="listening")
            title = "Song"
            artist = "Artist"
            track_url = None
            album_cover_url = None

            @property
            def start(self):
                raise KeyError("start")

            @property
            def end(self):
                raise KeyError("end")

        member = SimpleNamespace(
            status="online",
            activities=[Spotify()],
            global_name="Staffer",
            name="staffer",
            display_avatar=SimpleNamespace(url=""),
            _user=None,
        )
        guild = SimpleNamespace(get_member=lambda user_id: member)
        previous = server_routes._discord_bot
        server_routes._discord_bot = SimpleNamespace(guilds=[guild])
        try:
            identity = server_routes._staff_identity("43")
        finally:
            server_routes._discord_bot = previous

        activity = identity["activities"][0]
        self.assertIsNone(activity["start"])
        self.assertIsNone(activity["end"])


if __name__ == "__main__":
    unittest.main()
