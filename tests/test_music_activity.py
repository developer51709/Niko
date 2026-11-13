"""The experimental music Activity: panel routing, sessions and controls.

The panel is served on its own subdomain root because Discord's Activity URL
mapping only supports the root prefix. Its API is token-authenticated and
resolves the guild and voice channel through the bot on every call.
"""

import asyncio
import sys
import time
import unittest
from collections import deque
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.music.cog import MusicSystem  # noqa: E402
from webapp import app  # noqa: E402
from webapp import config, runtime  # noqa: E402
from webapp.music_activity import (  # noqa: E402
    issue_artwork_token,
    issue_session,
    read_artwork_token,
    read_session,
)

GUILD_ID = 4242
USER_ID = 777
CHANNEL_ID = 99
DJ_ROLE_ID = 1234


class ActivitySessionTests(unittest.TestCase):
    def test_a_session_round_trips(self):
        with app.app_context():
            token = issue_session(USER_ID)
            self.assertEqual(read_session(token), USER_ID)

    def test_a_tampered_session_is_rejected(self):
        with app.app_context():
            token = issue_session(USER_ID)
            encoded, _, signature = token.partition(".")
            self.assertIsNone(read_session(f"{encoded}x.{signature}"))

    def test_an_expired_session_is_rejected(self):
        with app.app_context():
            with mock.patch("webapp.music_activity.time.time", return_value=time.time() - 100_000):
                token = issue_session(USER_ID)
            self.assertIsNone(read_session(token))

    def test_an_artwork_token_round_trips_member_and_guild(self):
        with app.app_context():
            token = issue_artwork_token(USER_ID, GUILD_ID)
            self.assertEqual(read_artwork_token(token), (USER_ID, GUILD_ID))

    def test_a_tampered_artwork_token_is_rejected(self):
        with app.app_context():
            token = issue_artwork_token(USER_ID, GUILD_ID)
            encoded, _, signature = token.partition(".")
            self.assertIsNone(read_artwork_token(f"{encoded}x.{signature}"))

    def test_an_expired_artwork_token_is_rejected(self):
        with app.app_context():
            token = issue_artwork_token(
                USER_ID, GUILD_ID, issued_at=int(time.time()) - 2 * 60 * 60,
            )
            self.assertIsNone(read_artwork_token(token))


class ActivityPageTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_the_panel_is_served_on_its_own_subdomain_root(self):
        response = self.client.get("/", headers={"Host": "activities.example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Niko Player", response.data)
        self.assertIn(b"/activity/assets/", response.data)

    def test_the_panel_is_also_reachable_by_path_for_local_use(self):
        with mock.patch.object(runtime, "oauth_enabled", return_value=True):
            response = self.client.get("/activity")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Niko Player", response.data)

    def test_the_apex_root_still_serves_the_site(self):
        response = self.client.get("/", headers={"Host": "example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"/activity/assets/", response.data)

    def test_the_activity_host_is_not_an_unknown_subdomain(self):
        self.assertTrue(config.is_activity_host("activities.example.com"))
        self.assertFalse(config.unknown_subdomain("activities.example.com"))

    def test_the_api_refuses_requests_without_a_session(self):
        response = self.client.get(f"/api/activity/state?guild_id={GUILD_ID}")
        self.assertEqual(response.status_code, 401)

    def test_the_playlist_route_refuses_a_request_without_a_token(self):
        response = self.client.get(
            f"/api/activity/playlist?guild_id={GUILD_ID}&name=Chill",
        )
        self.assertEqual(response.status_code, 401)

    def test_the_api_refuses_a_forged_session(self):
        response = self.client.get(
            f"/api/activity/state?guild_id={GUILD_ID}",
            headers={"Authorization": "Bearer not-a-real-session"},
        )
        self.assertEqual(response.status_code, 401)

    def test_the_artwork_route_refuses_a_request_without_a_token(self):
        response = self.client.get("/api/activity/artwork")
        self.assertEqual(response.status_code, 401)

    def test_the_legacy_artwork_path_still_answers(self):
        response = self.client.get("/activity/artwork")
        self.assertEqual(response.status_code, 401)

    def test_the_brand_fonts_are_served_from_this_origin(self):
        response = self.client.get("/activity/fonts/plus-jakarta-sans.woff2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "font/woff2")

    def test_the_state_serves_artwork_from_this_origin(self):
        """Discord's proxy cannot load YouTube/Spotify art directly."""

        class FakeCog:
            async def activity_snapshot(self, guild_id, user_id, channel_id):
                return {
                    "ok": True,
                    "track": {
                        "title": "song",
                        "uri": "https://example.test/watch?v=abc",
                        "artwork": "https://i.ytimg.com/vi/abc/hqdefault.jpg",
                    },
                }

            async def activity_artwork(self, guild_id, user_id, channel_id):
                return {"ok": True, "data": b"\xff\xd8\xff\xe0art", "content_type": "image/jpeg"}

        def run(coro, timeout=None):
            return asyncio.run(coro)

        with app.app_context():
            token = issue_session(USER_ID)
        bot = SimpleNamespace(get_cog=lambda _name: FakeCog())
        with mock.patch.object(runtime, "_discord_bot", bot), \
             mock.patch.object(runtime, "run_on_bot_loop", side_effect=run):
            state = self.client.get(
                f"/api/activity/state?guild_id={GUILD_ID}",
                headers={"Authorization": f"Bearer {token}"},
            )
            body = state.get_json()
            self.assertTrue(body["artwork_url"].startswith("/api/activity/artwork?token="))
            # The version keeps Discord and the browser from reusing the
            # previous song's cover for this signed URL.
            self.assertIn("&v=", body["artwork_url"])

            artwork = self.client.get(body["artwork_url"])

        self.assertEqual(artwork.status_code, 200)
        self.assertEqual(artwork.mimetype, "image/jpeg")
        self.assertTrue(artwork.data.startswith(b"\xff\xd8"))


class ArtworkUrlTests(unittest.TestCase):
    def test_only_public_https_artwork_is_fetched(self):
        from cogs.music.cog import _safe_artwork_url

        self.assertTrue(_safe_artwork_url("https://i.ytimg.com/vi/abc/hqdefault.jpg"))
        self.assertFalse(_safe_artwork_url("http://i.ytimg.com/vi/abc/hqdefault.jpg"))
        self.assertFalse(_safe_artwork_url("https://localhost/art.jpg"))
        self.assertFalse(_safe_artwork_url("https://127.0.0.1/art.jpg"))
        self.assertFalse(_safe_artwork_url("https://192.168.1.5/art.jpg"))
        self.assertFalse(_safe_artwork_url("not a url"))


class FakeQueue(list):
    def put_at(self, index, value):
        self.insert(index, value)

    def peek(self, index=0):
        return self[index]

    def delete(self, index):
        del self[index]

    def shuffle(self):
        pass


class ActivityControlTests(unittest.IsolatedAsyncioTestCase):
    def _cog(self, *, is_dj: bool):
        track = SimpleNamespace(
            source="youtube", author="artist", title="song", length=200_000,
            uri="https://example.test/watch?v=abc123", artwork=None,
        )
        member = SimpleNamespace(id=USER_ID)
        player = SimpleNamespace(
            current=track,
            position=1_000,
            playing=True,
            paused=False,
            volume=50,
            queue=FakeQueue([
                SimpleNamespace(title="next", author="artist", length=100_000),
            ]),
            channel=SimpleNamespace(
                id=CHANNEL_ID,
                name="Music",
                members=[member, SimpleNamespace(id=1, bot=True)],
            ),
            pause=AsyncMock(),
            skip=AsyncMock(),
            stop=AsyncMock(),
            play=AsyncMock(),
            set_volume=AsyncMock(),
        )
        guild = SimpleNamespace(
            id=GUILD_ID,
            name="Test Server",
            voice_client=object(),
            get_member=lambda member_id: member if member_id == USER_ID else None,
        )
        cog = object.__new__(MusicSystem)
        cog.bot = SimpleNamespace(get_guild=lambda guild_id: guild if guild_id == GUILD_ID else None)
        cog._guild_states = {
            GUILD_ID: {
                "loop": False,
                "autoplay": False,
                "history": deque(),
                "current_track": track,
                "ghost_queue": deque(),
            }
        }
        cog._dj_roles = {GUILD_ID: DJ_ROLE_ID if not is_dj else None}
        cog._lastfm_key = "key"
        cog._player_for_guild = MagicMock(return_value=player)
        cog.is_dj = AsyncMock(return_value=is_dj)
        cog._update_np_message = AsyncMock()
        cog._schedule_ghost_refill = MagicMock()
        cog._clear_ghost = MagicMock()
        return cog, player

    async def test_the_snapshot_describes_the_current_track(self):
        cog, _ = self._cog(is_dj=True)
        cog.bot.user = SimpleNamespace(
            display_avatar=SimpleNamespace(url="https://cdn.discordapp.com/avatars/1/niko.png"),
        )
        snapshot = await cog.activity_snapshot(GUILD_ID, USER_ID, CHANNEL_ID)

        self.assertTrue(snapshot["ok"])
        self.assertEqual(
            snapshot["bot_avatar_url"],
            "https://cdn.discordapp.com/avatars/1/niko.png",
        )
        self.assertEqual(snapshot["track"]["title"], "song")
        self.assertEqual(snapshot["channel"]["name"], "Music")
        self.assertEqual(snapshot["queue_count"], 1)
        self.assertEqual(snapshot["listeners"], 1)
        self.assertTrue(snapshot["user"]["is_dj"])
        self.assertEqual(snapshot["autoplay_queue"], [])

    async def test_autoplay_suggestions_reach_the_snapshot_when_enabled(self):
        cog, _ = self._cog(is_dj=True)
        state = cog._state(GUILD_ID)
        state["autoplay"] = True
        state["ghost_queue"].append(
            SimpleNamespace(title="similar song", author="similar artist", length=120_000),
        )

        snapshot = await cog.activity_snapshot(GUILD_ID, USER_ID, CHANNEL_ID)

        self.assertEqual(snapshot["autoplay_queue"], [{
            "title": "similar song",
            "author": "similar artist",
            "length": 120_000,
        }])

    async def test_a_non_dj_cannot_skip(self):
        cog, player = self._cog(is_dj=False)
        result = await cog.activity_control(GUILD_ID, USER_ID, "skip")

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "dj_only")
        player.skip.assert_not_awaited()

    async def test_pause_is_open_to_everyone(self):
        cog, player = self._cog(is_dj=False)
        result = await cog.activity_control(GUILD_ID, USER_ID, "toggle_pause")

        self.assertTrue(result["ok"])
        player.pause.assert_awaited_once_with(True)
        cog._update_np_message.assert_awaited_once()

    async def test_a_dj_can_change_the_volume(self):
        cog, player = self._cog(is_dj=True)
        result = await cog.activity_control(GUILD_ID, USER_ID, "volume", 140)

        self.assertTrue(result["ok"])
        player.set_volume.assert_awaited_once_with(100)

    async def test_the_artwork_is_fetched_for_the_current_track(self):
        cog, _ = self._cog(is_dj=True)
        fetch = AsyncMock(return_value=(b"\x89PNG\r\n\x1a\nart", "image/png"))

        with mock.patch("cogs.music.cog._fetch_artwork", fetch):
            result = await cog.activity_artwork(GUILD_ID, USER_ID, CHANNEL_ID)

        self.assertTrue(result["ok"])
        self.assertEqual(result["content_type"], "image/png")
        fetch.assert_awaited_once()
        self.assertIn("i.ytimg.com", fetch.await_args.args[0])

    async def test_artwork_for_an_unknown_guild_is_refused(self):
        cog, _ = self._cog(is_dj=True)

        result = await cog.activity_artwork(GUILD_ID + 1, USER_ID, CHANNEL_ID)

        self.assertEqual(result["error"], "guild_unavailable")

    async def test_a_non_dj_cannot_remove_a_queued_track(self):
        cog, player = self._cog(is_dj=False)

        result = await cog.activity_control(GUILD_ID, USER_ID, "queue_remove", 0)

        self.assertEqual(result["error"], "dj_only")
        self.assertEqual(len(player.queue), 1)

    async def test_a_dj_can_remove_a_queued_track(self):
        cog, _ = self._cog(is_dj=True)

        result = await cog.activity_control(GUILD_ID, USER_ID, "queue_remove", 0)

        self.assertTrue(result["ok"])
        self.assertEqual(result["queue_count"], 0)
        self.assertEqual(result["queue"], [])

    async def test_a_queued_track_can_be_moved(self):
        cog, player = self._cog(is_dj=True)
        first = player.queue[0]
        player.queue.append(SimpleNamespace(title="third", author="artist", length=90_000))

        result = await cog.activity_control(
            GUILD_ID, USER_ID, "queue_move", {"from": 1, "to": 0},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["queue"][0]["title"], "third")
        self.assertIs(player.queue[1], first)

    async def test_jumping_plays_the_queued_track_and_keeps_the_old_one(self):
        cog, player = self._cog(is_dj=True)
        queued = player.queue[0]
        current = player.current

        result = await cog.activity_control(GUILD_ID, USER_ID, "queue_jump", 0)

        self.assertTrue(result["ok"])
        player.play.assert_awaited_once_with(queued)
        self.assertEqual(len(player.queue), 1)
        self.assertIs(player.queue[0], current)

    async def test_clearing_the_queue_keeps_the_current_track(self):
        cog, player = self._cog(is_dj=True)

        result = await cog.activity_control(GUILD_ID, USER_ID, "queue_clear")

        self.assertTrue(result["ok"])
        self.assertEqual(result["queue_count"], 0)
        self.assertIsNotNone(player.current)

    async def test_a_bad_queue_index_is_refused(self):
        cog, _ = self._cog(is_dj=True)

        result = await cog.activity_control(GUILD_ID, USER_ID, "queue_remove", 99)

        self.assertEqual(result["error"], "bad_index")

    async def test_the_snapshot_lists_shared_playlists(self):
        cog, _ = self._cog(is_dj=True)

        class FakeDB:
            async def ensure(self, bot=None):
                return True

            async def shared_playlists(self, guild_id):
                return [{
                    "playlist_id": "p1", "name": "Chill",
                    "track_count": 3, "owner_id": USER_ID,
                }]

            async def is_playlist_editor(self, playlist_id, user_id):
                return True

        with mock.patch("cogs.music.cog.MusicDatabase", FakeDB):
            snapshot = await cog.activity_snapshot(GUILD_ID, USER_ID, CHANNEL_ID)

        self.assertEqual(snapshot["playlists"], [{
            "id": "p1", "name": "Chill", "count": 3,
            "owner_id": str(USER_ID), "can_edit": True,
        }])

    async def test_a_playlist_card_lists_its_tracks_and_adders(self):
        cog, _ = self._cog(is_dj=True)
        adder = SimpleNamespace(
            id=USER_ID + 1,
            display_name="Ada",
            global_name="Ada Global",
            name="ada",
        )
        guild = cog.bot.get_guild(GUILD_ID)
        guild.get_member = lambda member_id: (
            cog._member if member_id == USER_ID else adder if member_id == adder.id else None
        )
        cog._member = SimpleNamespace(id=USER_ID)

        class FakeDB:
            async def ensure(self, bot=None):
                return True

            async def shared_playlist(self, guild_id, name):
                return {"playlist_id": "p1", "name": name, "owner_id": USER_ID}

            async def shared_tracks(self, playlist_id):
                return [{
                    "title": "Song **One**",
                    "author": "Artist",
                    "uri": "https://example.test/one",
                    "length_ms": 123_000,
                    "added_by": adder.id,
                }]

        with mock.patch("cogs.music.cog.MusicDatabase", FakeDB):
            result = await cog.activity_playlist(GUILD_ID, USER_ID, CHANNEL_ID, "Chill")

        self.assertTrue(result["ok"])
        self.assertEqual(result["playlist"]["name"], "Chill")
        self.assertEqual(result["tracks"], [{
            "title": "Song **One**",
            "author": "Artist",
            "uri": "https://example.test/one",
            "length": 123_000,
            "added_by": str(adder.id),
            "added_by_name": "Ada",
        }])

    async def test_a_playlist_editor_can_add_the_current_track(self):
        cog, _ = self._cog(is_dj=False)
        add = AsyncMock(return_value=True)

        class FakeDB:
            async def ensure(self, bot=None):
                return True

            async def shared_playlist(self, guild_id, name):
                return {"playlist_id": "p1", "name": name}

            async def is_playlist_editor(self, playlist_id, user_id):
                return True

            async def add_shared_track(self, playlist_id, track, user_id):
                return await add(playlist_id, track, user_id)

        with mock.patch("cogs.music.cog.MusicDatabase", FakeDB):
            result = await cog.activity_control(
                GUILD_ID, USER_ID, "playlist_add", "Chill",
            )

        self.assertTrue(result["ok"])
        add.assert_awaited_once()
        self.assertEqual(add.await_args.args[0], "p1")

    async def test_add_to_a_playlist_still_needs_editor_rights(self):
        cog, _ = self._cog(is_dj=False)

        class FakeDB:
            async def ensure(self, bot=None):
                return True

            async def shared_playlist(self, guild_id, name):
                return {"playlist_id": "p1", "name": name}

            async def is_playlist_editor(self, playlist_id, user_id):
                return False

        with mock.patch("cogs.music.cog.MusicDatabase", FakeDB):
            result = await cog.activity_control(
                GUILD_ID, USER_ID, "playlist_add", "Chill",
            )

        self.assertEqual(result["error"], "playlist_editor_only")

    async def test_a_member_outside_the_activity_channel_is_refused(self):
        cog, _ = self._cog(is_dj=True)
        other = SimpleNamespace(id=CHANNEL_ID + 1)
        member = SimpleNamespace(
            id=USER_ID,
            voice=SimpleNamespace(channel=other),
        )
        cog.bot.get_guild(GUILD_ID).get_member = lambda _id: member

        result = await cog.activity_snapshot(GUILD_ID, USER_ID, CHANNEL_ID)
        self.assertEqual(result["error"], "not_in_channel")


if __name__ == "__main__":
    unittest.main()
