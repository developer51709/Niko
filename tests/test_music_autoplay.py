import asyncio
import contextlib
import sys
import unittest
from collections import deque
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from aiohttp import ClientTimeout

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cogs.music.cog as music_cog
from cogs.music.cog import MusicSystem, _search_tracks
from utils.music import autoplay
from utils.music.autoplay import clean_seed, lastfm_similar


class _Response:
    def __init__(self, status=200, payload=None, text=""):
        self.status = status
        self._payload = payload
        self._text = text

    async def json(self, content_type=None):
        return self._payload

    async def text(self):
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _Session:
    """Stands in for aiohttp.ClientSession, serving canned responses in order."""

    def __init__(self, *responses):
        self._responses = list(responses)
        self.requests: list[dict] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def get(self, url, params=None, timeout=None):
        self.requests.append(params or {})
        return self._responses.pop(0) if self._responses else _Response(200, {})


def _similar(*names) -> dict:
    return {
        "similartracks": {
            "track": [
                {"name": name, "artist": {"name": artist}} for artist, name in names
            ]
        }
    }


class AutoplayHelperTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        autoplay._last_failure = None

    def _patch_session(self, session):
        return patch.object(
            autoplay,
            "aiohttp",
            SimpleNamespace(ClientSession=lambda: session, ClientTimeout=ClientTimeout),
        )

    # ── seed cleanup ──────────────────────────────────────────────

    def test_upload_noise_is_stripped_from_the_seed(self):
        self.assertEqual(
            clean_seed("Rick Astley - Topic", "Rick Astley - Never Gonna Give You Up (Official Video)"),
            ("Rick Astley", "Never Gonna Give You Up"),
        )
        self.assertEqual(
            clean_seed("Daft Punk", "Daft Punk - One More Time [Official Audio]"),
            ("Daft Punk", "One More Time"),
        )
        # VEVO channels carry the artist name with no separator at all.
        self.assertEqual(
            clean_seed("RickAstleyVEVO", "Never Gonna Give You Up (Official Music Video)"),
            ("RickAstley", "Never Gonna Give You Up"),
        )

    def test_track_qualifiers_survive_the_cleanup(self):
        self.assertEqual(
            clean_seed("Radiohead", "Creep (Live)"),
            ("Radiohead", "Creep (Live)"),
        )
        self.assertEqual(
            clean_seed("Adele", "Hello (Remix)"),
            ("Adele", "Hello (Remix)"),
        )

    def test_featured_artists_are_dropped_from_the_title(self):
        self.assertEqual(clean_seed("Calvin Harris", "This Is What You Came For (feat. Rihanna)"),
                         ("Calvin Harris", "This Is What You Came For"))

    # ── Last.fm calls ─────────────────────────────────────────────

    async def test_similar_tracks_are_parsed_from_the_response(self):
        session = _Session(_Response(200, _similar(("Muse", "Starlight"), ("Keane", "Somewhere Only We Know"))))
        with self._patch_session(session):
            pairs = await lastfm_similar("key", "Coldplay - Topic", "Coldplay - Viva La Vida (Official Video)")

        self.assertEqual(pairs, [("Muse", "Starlight"), ("Keane", "Somewhere Only We Know")])
        # The lookup must use the cleaned seed, not YouTube's raw metadata.
        self.assertEqual(session.requests[0]["artist"], "Coldplay")
        self.assertEqual(session.requests[0]["track"], "Viva La Vida")
        self.assertEqual(session.requests[0]["api_key"], "key")

    async def test_a_rejected_key_is_reported_and_returns_nothing(self):
        session = _Session(_Response(403, text='{"error":10,"message":"Invalid API key"}'))
        with self._patch_session(session), patch.object(autoplay, "log") as fake_log:
            pairs = await lastfm_similar("wrong-key", "Radiohead", "Creep")

        self.assertEqual(pairs, [])
        fake_log.warning.assert_called_once()
        self.assertIn("403", fake_log.warning.call_args[0][1])
        # A credential failure must not be retried against the raw seed.
        self.assertEqual(len(session.requests), 1)

    async def test_an_error_body_is_not_a_crash(self):
        session = _Session(_Response(200, {"error": 6, "message": "Track not found"}))
        with self._patch_session(session), patch.object(autoplay, "log") as fake_log:
            pairs = await lastfm_similar("key", "Nobody", "Nothing")

        self.assertEqual(pairs, [])
        fake_log.warning.assert_called_once()

    async def test_the_raw_seed_is_retried_when_the_cleaned_one_misses(self):
        session = _Session(
            _Response(200, {"similartracks": {"track": []}}),
            _Response(200, _similar(("Blur", "Song 2"))),
        )
        with self._patch_session(session):
            pairs = await lastfm_similar("key", "Pulp", "Pulp - Common People (Official Video)")

        self.assertEqual(pairs, [("Blur", "Song 2")])
        self.assertEqual(len(session.requests), 2)
        self.assertEqual(session.requests[0]["track"], "Common People")
        self.assertEqual(session.requests[1]["track"], "Pulp - Common People (Official Video)")

    async def test_a_persistent_failure_is_logged_once(self):
        session = _Session(_Response(500, text="boom"), _Response(500, text="boom"))
        with self._patch_session(session), patch.object(autoplay, "log") as fake_log:
            await lastfm_similar("key", "Radiohead", "Creep")
            await lastfm_similar("key", "Radiohead", "Creep")

        self.assertEqual(fake_log.warning.call_count, 1)


class SearchPrefixTests(unittest.IsolatedAsyncioTestCase):
    """Searches must not end up as ``ytmsearch:ytsearch:<song>``."""

    async def test_a_prefixed_query_is_sent_unchanged(self):
        with patch.object(music_cog.wavelink.Pool, "fetch_tracks", new=AsyncMock(return_value=[])) as fetch:
            await _search_tracks("ytsearch:Radiohead - Creep")
        self.assertEqual(fetch.await_args[0][0], "ytsearch:Radiohead - Creep")

    async def test_a_bare_query_gets_the_default_prefix(self):
        with patch.object(music_cog.wavelink.Pool, "fetch_tracks", new=AsyncMock(return_value=[])) as fetch:
            await _search_tracks("Radiohead - Creep")
        self.assertEqual(fetch.await_args[0][0], "ytmsearch:Radiohead - Creep")

    async def test_a_url_is_not_prefixed(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        with patch.object(music_cog.wavelink.Pool, "fetch_tracks", new=AsyncMock(return_value=[])) as fetch:
            await _search_tracks(url)
        self.assertEqual(fetch.await_args[0][0], url)


class _Queue:
    def __init__(self, items=()):
        self._items = list(items)

    @property
    def is_empty(self):
        return not self._items

    def get(self):
        return self._items.pop(0)

    def clear(self):
        self._items.clear()

    def put_at(self, index, item):
        self._items.insert(index, item)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __iter__(self):
        return iter(self._items)


class _Player:
    def __init__(self, track):
        self.guild = SimpleNamespace(id=1)
        self.guild.voice_client = self
        self.current = track
        self.queue = _Queue()
        self.node = SimpleNamespace(identifier="node-1")
        self.playing = False
        self.paused = False
        self.connected = True
        self.channel = SimpleNamespace(id=99)
        self.played = []

    async def play(self, track, **kwargs):
        self.played.append(track)
        self.current = track
        self.playing = True

    async def disconnect(self):
        self.connected = False


def _build_cog(ghost=()):
    seed = SimpleNamespace(
        title="Seed Song", author="Seed Artist", encoded="enc-seed",
        uri="", source="youtube", length=1, artwork=None,
    )
    player = _Player(seed)
    cog = object.__new__(MusicSystem)
    cog._lastfm_key = "key"
    cog._guild_states = {1: {
        "loop": False, "autoplay": True, "history": deque(), "np_message": None,
        "last_track": None, "current_track": seed, "failed_track_retry": None,
        "stuck_track": None, "ghost_queue": deque(ghost, maxlen=5),
        "ghost_seed": None, "ghost_task": None,
    }}
    cog.bot = SimpleNamespace(
        get_guild=lambda _gid: player.guild,
        http=SimpleNamespace(edit_voice_channel_status=AsyncMock()),
    )
    cog._update_np_message = AsyncMock()
    return cog, player, seed


async def _end_track(cog, player, seed, reason="finished"):
    await asyncio.wait_for(
        cog.on_wavelink_track_end(
            SimpleNamespace(player=player, track=seed, reason=reason)
        ),
        timeout=3,
    )
    # The drain path schedules a background refill; stop it so it cannot leak
    # into the next test (or log after the loop closes).
    task = cog._guild_states[1].get("ghost_task")
    if task and not task.done():
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


class AutoplayDrainTests(unittest.IsolatedAsyncioTestCase):
    """When the manual queue drains, autoplay has to actually start a track."""

    async def test_a_pending_ghost_track_continues_playback(self):
        ghost = SimpleNamespace(title="Ghost Track", author="Other Artist", encoded="enc-ghost")
        cog, player, seed = _build_cog([ghost])

        with patch.object(music_cog, "_lastfm_similar", new=AsyncMock(return_value=[])):
            await _end_track(cog, player, seed)

        self.assertEqual([track.title for track in player.played], ["Ghost Track"])

    async def test_an_empty_ghost_queue_falls_back_to_last_fm(self):
        found = SimpleNamespace(title="Fresh Track", author="Fresh Artist", encoded="enc-new")
        cog, player, seed = _build_cog()

        with patch.object(music_cog, "_lastfm_similar", new=AsyncMock(return_value=[("Fresh Artist", "Fresh Track")])), \
                patch.object(music_cog, "_search_tracks", new=AsyncMock(return_value=[found])):
            await _end_track(cog, player, seed)

        self.assertEqual([track.title for track in player.played], ["Fresh Track"])

    async def test_a_stopped_player_does_not_start_autoplay(self):
        cog, player, seed = _build_cog()
        ghost = SimpleNamespace(title="Ghost Track", author="Other Artist", encoded="enc-ghost")
        cog._guild_states[1]["ghost_queue"].append(ghost)

        with patch.object(music_cog, "IDLE_TIMEOUT", 0):
            await _end_track(cog, player, seed, reason="stopped")

        self.assertEqual(player.played, [])
        self.assertEqual(list(cog._guild_states[1]["ghost_queue"]), [])


if __name__ == "__main__":
    unittest.main()
