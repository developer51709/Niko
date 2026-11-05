"""Regression checks for the team profile cards and Twitch app credentials.

Covers the pieces that make the staff profile cards and the Discord profile
popups work:

* public profile lookups only ever contact a platform's own hosts,
* Twitch reuses one cached application (client-credentials) token,
* a Spotify presence keeps the track window the progress bar needs,
* an open Discord profile popup keeps polling its live presence.
"""

import asyncio
import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from webapp import app
from webapp import runtime, staff  # noqa: E402

from utils.social import profiles, twitch

ROOT = Path(__file__).resolve().parents[1]


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
        previous = runtime._discord_bot
        runtime._discord_bot = bot
        try:
            identity = staff._staff_identity("42")
        finally:
            runtime._discord_bot = previous

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
        previous = runtime._discord_bot
        runtime._discord_bot = SimpleNamespace(guilds=[guild])
        try:
            identity = staff._staff_identity("43")
        finally:
            runtime._discord_bot = previous

        activity = identity["activities"][0]
        self.assertIsNone(activity["start"])
        self.assertIsNone(activity["end"])


class AvatarDecorationTests(unittest.TestCase):
    """Discord's avatar decoration reaches the Team pages with the identity."""

    def setUp(self):
        self.previous = runtime._discord_bot

    def tearDown(self):
        runtime._discord_bot = self.previous

    def _identity(self, decoration):
        member = SimpleNamespace(
            status="online",
            activities=[],
            global_name="Staffer",
            name="staffer",
            display_avatar=SimpleNamespace(url="https://example.test/avatar.png"),
            avatar_decoration=decoration,
            _user=None,
        )
        runtime._discord_bot = SimpleNamespace(guilds=[SimpleNamespace(get_member=lambda user_id: member)])
        return staff._staff_identity("44")

    def test_an_animated_decoration_is_served_as_its_animated_png(self):
        """Discord's preset is an APNG, and asking it for a gif answers 415."""
        decoration = SimpleNamespace(
            url="https://cdn.discordapp.com/avatar-decoration-presets/a.png?size=96",
            is_animated=lambda: True,
            with_format=lambda fmt: self.fail("a decoration preset must not be fetched as another format"),
        )

        identity = self._identity(decoration)

        # The one URL Discord serves is the animation itself.
        self.assertEqual(identity["avatar_decoration_url"], "https://cdn.discordapp.com/avatar-decoration-presets/a.png?size=96")
        self.assertNotIn("avatar_decoration_animated_url", identity)

    def test_the_decoration_url_is_passed_through_untouched(self):
        decoration = SimpleNamespace(url="https://cdn.discordapp.com/avatar-decoration-presets/b.png?size=96")

        identity = self._identity(decoration)

        self.assertEqual(identity["avatar_decoration_url"], "https://cdn.discordapp.com/avatar-decoration-presets/b.png?size=96")

    def test_a_member_without_a_decoration_reports_none(self):
        identity = self._identity(None)

        self.assertIsNone(identity["avatar_decoration_url"])
        self.assertNotIn("avatar_decoration_animated_url", identity)


class ProfilePopupPresenceTests(unittest.TestCase):
    """The web profile popup shows live presence, the way the staff cards do."""

    def setUp(self):
        self.source = (ROOT / "web" / "src" / "components" / "DiscordMarkdown.tsx").read_text(encoding="utf-8")

    def test_the_popup_reads_the_same_public_presence_endpoint(self):
        self.assertIn("fetch(`/api/discord/users/${encodeURIComponent(userId)}`)", self.source)

    def test_the_popup_refreshes_presence_while_it_is_open(self):
        # A popup does not freeze at the moment it was opened: the open profile
        # is re-read on a 5s timer, and again as soon as the tab is visible.
        self.assertIn("PROFILE_REFRESH_INTERVAL = 5000", self.source)
        self.assertIn("}, PROFILE_REFRESH_INTERVAL);", self.source)
        self.assertIn('if (document.visibilityState === "visible") refresh();', self.source)
        self.assertIn('document.addEventListener("visibilitychange", handleVisibility)', self.source)
        # Closing the popup tears both the timer and its listener down.
        self.assertIn("window.clearInterval(interval)", self.source)
        self.assertIn('document.removeEventListener("visibilitychange", handleVisibility)', self.source)
        # A poll that fails keeps the last known presence instead of blanking the
        # card or flashing a loading state.
        self.assertIn(".catch(() => {});", self.source)
        self.assertIn("setProfile((current) => (current && current.id === next.id ? next : current))", self.source)

    def test_the_custom_status_bubble_matches_discords_layout(self):
        """The bubble keeps Discord's shape: square for an emoji, clamped text."""
        styles = (ROOT / "web" / "src" / "styles.css").read_text(encoding="utf-8")
        self.assertIn('className="discord-profile-status is-emoji-only"', self.source)
        self.assertIn(".discord-profile-status.is-emoji-only {", styles)
        # The bubble is Discord's flat surface-high card, hung off the avatar's
        # bottom edge.
        self.assertIn("align-self: flex-end", styles)
        self.assertIn("background: #2b2d31; border-radius: 10px; font-size: 14px; line-height: 1.35;", styles)
        # A default emoji is Twemoji's image, the artwork Discord draws.
        self.assertIn("src={twemojiUrl(status.emoji_name)}", self.source)
        # The tail is a thought bubble: a round bump merged into the top edge and
        # a smaller round dot floating clear of it up and to the left.
        self.assertIn("top: -11px; left: 8px; width: 26px; height: 26px; background: inherit; border-radius: 50%; content: \"\";", styles)
        # Both circles are painted behind the bubble's content, so the part of
        # the bump inside the card never covers the status emoji or its text.
        self.assertIn("isolation: isolate;", styles)
        self.assertIn(".discord-profile-status::before { position: absolute; z-index: -1;", styles)
        self.assertIn(".discord-profile-status::after { position: absolute; z-index: -1;", styles)
        self.assertIn(".discord-profile-status::after { position: absolute; z-index: -1; top: -23px; left: -3px; width: 12px; height: 12px; background: inherit; border-radius: 50%; content: \"\"; }", styles)
        # Long text shows two lines, then opens in full when the bubble is clicked.
        self.assertIn("-webkit-line-clamp: 2;", styles)
        self.assertIn(".discord-profile-status.is-expanded .discord-profile-status-text", styles)
        self.assertIn("setExpanded((current) => !current)", self.source)

    def test_the_popup_dot_uses_the_live_status(self):
        # The popup passes the mobile flag through, so the avatar picks the
        # phone-shaped icon when the phone holds the presence.
        self.assertIn("<DiscordStatusAvatar status={profileStatusKey(profile.status)} mobile={profile.is_mobile}", self.source)
        self.assertIn("label={profileStatusLabel(profile.status, t)}", self.source)
        # Discord can report the status enum or a plain string; anything unknown
        # reads as offline rather than as an empty dot. The wording lives in the
        # catalogues, so this side only pins the key each status maps to.
        for status, key in (("online", "status.online"), ("idle", "status.idle"), ("dnd", "status.dnd"), ("offline", "status.offline"), ("streaming", "status.streaming")):
            with self.subTest(status=status):
                self.assertIn(f'{status}: "{key}"', self.source)

    def test_the_popup_dot_and_banner_cutout_match_discords_sizing(self):
        styles = (ROOT / "web" / "src" / "styles.css").read_text(encoding="utf-8")
        # Discord's dot sits a touch smaller than its cutout: 19px in the 26px
        # notch, i.e. a 3.5px ring of card around it on the 76px avatar.
        self.assertIn(".discord-status-avatar.discord-profile-avatar-wrap-status-wrap { --status-icon-size: 19px; --status-gap: 3.5px; }", styles)
        self.assertIn("--status-notch-size: calc(var(--status-icon-size) + 2 * var(--status-gap))", styles)
        # The banner is cut away around the avatar: the hole is centred on it
        # (16px padding + 38px radius, on the banner's bottom edge) and is the
        # avatar's radius plus 4px of the popout's own background.
        self.assertIn("radial-gradient(circle at 54px 100%, transparent calc(42px - .5px), #000 42px)", styles)
        self.assertIn("mask-image: var(--profile-avatar-cutout)", styles)
        # The row keeps the avatar's height, so a taller emoji-only bubble cannot
        # push the picture out of the cutout.
        self.assertIn("align-items: center; gap: 8px; height: 76px; margin-top: -38px;", styles)

    def test_the_spotify_card_matches_discords_activity_card(self):
        styles = (ROOT / "web" / "src" / "styles.css").read_text(encoding="utf-8")
        # Discord's card: its own padding and radius, a 60px sleeve and the track
        # line beside it with the label above.
        self.assertIn(".discord-profile-spotify { margin-top: 14px; padding: 10px 12px 12px; background: #232428; border-radius: 10px;", styles)
        self.assertIn(".discord-profile-spotify-art { width: 60px; height: 60px; flex: 0 0 auto; border-radius: 8px; object-fit: cover; }", styles)
        self.assertIn(".discord-profile-spotify-head { display: flex; align-items: center; gap: 5px; color: #dbdee1; font-size: 13px; font-weight: 600; }", styles)
        self.assertIn("color: #f2f3f5; font-size: 14px; font-weight: 700;", styles)
        # The card is set in Discord's face, not the site's Plus Jakarta Sans.
        self.assertIn('font-family: "gg sans", "Segoe UI", system-ui, -apple-system, sans-serif;', styles)
        # The played part of the bar is the card's light grey, not Spotify green.
        self.assertIn("left: 0; background: #dbdee1; border-radius: 999px; transition: width .95s linear;", styles)
        # The times are set in the monospaced face the devtools header uses.
        self.assertIn('color: #b5bac1; font-family: "Space Mono", monospace; font-size: 12px;', styles)
        # The mark follows the wording, the way Discord reads it.
        self.assertIn('<span>Listening to Spotify</span><img src="/spotify.svg" alt="" />', self.source)


def test_the_team_profile_page_shows_the_popup_status_bubble():
    source = (ROOT / "web" / "src" / "pages" / "TeamPage.tsx").read_text(encoding="utf-8")
    markdown = (ROOT / "web" / "src" / "components" / "DiscordMarkdown.tsx").read_text(encoding="utf-8")

    # The bubble and its status shape are shared with the user popups rather than
    # redrawn for the team page.
    assert "export function ProfileCustomStatus" in markdown
    assert "export type DiscordCustomStatus" in markdown
    assert 'import { ProfileCustomStatus, type DiscordCustomStatus } from "../components/DiscordMarkdown";' in source
    # It sits in the avatar's row, bottom-aligned with it, exactly where the
    # popups put it: avatar, then the bubble, then the name below.
    header = source[source.index('<div className="team-profile-header">'):source.index('<div className="team-profile-identity">')]
    assert '<StatusAvatar member={member} className="team-profile-avatar" />' in header
    assert "<ProfileStatusBubble member={member} />" in header
    assert ".team-profile-header{display:flex;align-items:flex-end;justify-content:flex-start;gap:8px;" in source
    # A unicode emoji carries only its character; a custom one its id and name.
    assert 'emoji.kind === "custom" ? emoji.name || null : emoji.value' in source
    assert 'emoji_id: emoji?.kind === "custom" ? emoji.value : null' in source
    # The old labelled status card is gone, so a status is never drawn twice.
    assert '<div className="profile-custom-status">' not in source


async def _no_niko_badges(*args, **kwargs):
    return []


class BotAppTagTests(unittest.TestCase):
    """A bot's display name carries Discord's APP pill, tick included if verified."""

    def setUp(self):
        from webapp.routes import discord_text_routes

        self.routes = discord_text_routes
        self.previous = discord_text_routes._discord_bot

    def tearDown(self):
        self.routes._discord_bot = self.previous

    def _profile(self, *, bot: bool, verified: bool, discriminator: str = "0071") -> dict:
        user = SimpleNamespace(
            name="app",
            global_name="App Name",
            bot=bot,
            discriminator=discriminator,
            # VERIFIED_BOT is the public flag Discord turns into the tick.
            public_flags=SimpleNamespace(value=(1 << 16) if verified else 0),
            display_avatar=SimpleNamespace(url="https://cdn.example/avatar.png"),
            banner=None,
            accent_color=None,
            primary_guild=None,
            avatar_decoration=None,
            avatar_decoration_sku_id=None,
        )
        member = SimpleNamespace(
            status=SimpleNamespace(name="online"),
            activities=[],
            _user=user,
            guild=None,
            nick=None,
            premium_since=None,
        )
        self.routes._discord_bot = SimpleNamespace(guilds=[SimpleNamespace(get_member=lambda user_id: member)])
        with patch.object(self.routes, "_presence_member", lambda user_id, bot: member), \
                patch.object(self.routes, "niko_badge_keys", _no_niko_badges):
            return asyncio.run(self.routes._fetch_discord_user_profile(None, "5"))

    def test_a_bot_reports_itself_and_a_verified_bot_reports_the_tick(self):
        verified = self._profile(bot=True, verified=True)
        self.assertTrue(verified["bot"])
        self.assertTrue(verified["verified_bot"])
        # The tick rides inside the pill, never the square badge row.
        self.assertNotIn("verified_bot", verified["badges"])

    def test_an_unverified_bot_and_a_human_report_no_tick(self):
        for bot in (True, False):
            with self.subTest(bot=bot):
                profile = self._profile(bot=bot, verified=False)
                self.assertEqual(profile["bot"], bot)
                self.assertFalse(profile["verified_bot"])

    def test_a_bot_reports_its_four_digit_tag(self):
        self.assertEqual(self._profile(bot=True, verified=True)["discriminator"], "0071")
        # Discord writes "0" for a migrated account with no tag at all.
        self.assertIsNone(self._profile(bot=False, verified=False, discriminator="0")["discriminator"])

    def test_the_site_popup_draws_one_pill_with_the_tick_inside(self):
        source = (ROOT / "web" / "src" / "components" / "DiscordMarkdown.tsx").read_text(encoding="utf-8")
        styles = (ROOT / "web" / "src" / "styles.css").read_text(encoding="utf-8")

        self.assertIn('{profile.bot && <span className="discord-bot-tag"', source)
        self.assertIn('{profile.verified_bot && <svg className="discord-bot-tag-check"', source)
        self.assertIn(".discord-bot-tag {", styles)
        self.assertIn(".discord-bot-tag-check {", styles)
        # The tag rides inside the handle, so it never picks up the row's gap.
        self.assertIn("{profile.bot && profile.discriminator && <span className=\"discord-profile-discriminator\">#{profile.discriminator}</span>}", source)


if __name__ == "__main__":
    unittest.main()
