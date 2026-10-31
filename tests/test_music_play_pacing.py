"""A playlist expands into one Lavalink search per track.

Firing them back to back makes the public nodes answer ``429 Too Many
Requests``: the pool's first node blocks after a handful of ``loadtracks``
calls. These tests pin the handling — the first search (the one that starts
playback) is never delayed, the rest are spaced, and a rate-limited entry is
retried (on another node when one is available) instead of being dropped.
"""

import asyncio
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import wavelink

import cogs.music.cog as music_cog
from cogs.music.cog import MusicSystem, _is_rate_limited, _next_search_delay

# Exactly what a serenetia 429 raises: the body is plain text, so wavelink
# builds NodeException(msg=None, status=429) and str(exc) is "None".
RATE_LIMIT = wavelink.NodeException(status=429)
RATE_LIMIT_TEXT = "429 Too Many Requests, message='Too many loadtrack requests'"


class _Track:
    def __init__(self, title):
        self.title = title
        self.author = "Artist"
        self.encoded = "enc"
        self.uri = ""
        self.source = "youtube"
        self.length = 1000
        self.artwork = None


class _Queue:
    def __init__(self):
        self.items = []

    def put(self, track):
        self.items.append(track)


class _Player:
    def __init__(self, cog):
        self.cog = cog
        self.playing = False
        self.current = None
        self.queue = _Queue()
        self.node = SimpleNamespace(identifier="primary")
        self.guild = SimpleNamespace(id=1)

    async def play(self, track):
        self.playing = True
        self.current = track
        event = self.cog._track_start_events.get(1)
        if event is not None:
            event.set()


class _Ctx:
    def __init__(self):
        self.sent = []
        self.guild = SimpleNamespace(id=1, preferred_locale="en-US")
        self.author = SimpleNamespace(voice=SimpleNamespace(channel=object()))

    async def send(self, content=None, view=None, **kwargs):
        message = SimpleNamespace(content=content, deleted=False)
        self.sent.append(message)
        return message


def _build_cog(searches, alt_node=None):
    cog = object.__new__(MusicSystem)
    cog.bot = SimpleNamespace(command_prefix=".")
    cog._guild_states = {}
    cog._track_start_events = {}
    cog._lastfm_key = None
    cog._schedule_ghost_refill = Mock()
    cog._resolve_query = AsyncMock(return_value=searches)
    cog._get_alt_node = Mock(return_value=alt_node)
    player = _Player(cog)
    cog.get_player = AsyncMock(return_value=player)
    return cog, player


def _fake_search(seen, nodes=None, *, rate_limit_once=None):
    """Records each search; ``rate_limit_once`` 429s on its first attempt."""
    attempts: dict[str, int] = {}

    async def search(query, node=None):
        seen.append(time.monotonic())
        if nodes is not None:
            nodes.append(getattr(node, "identifier", None))
        attempts[query] = attempts.get(query, 0) + 1
        if query == rate_limit_once and attempts[query] == 1:
            raise RATE_LIMIT
        return [_Track(f"Track {len(seen)}")]

    return search


class RateLimitDetectionTests(unittest.TestCase):
    def test_a_429_without_a_message_is_still_a_429(self):
        self.assertEqual(str(RATE_LIMIT), "None")
        self.assertTrue(_is_rate_limited(RATE_LIMIT))
        self.assertAlmostEqual(_next_search_delay(0.35, RATE_LIMIT), 0.7)

    def test_a_textual_429_is_detected_too(self):
        self.assertTrue(_is_rate_limited(Exception(RATE_LIMIT_TEXT)))
        self.assertTrue(_is_rate_limited(Exception("Too many requests")))

    def test_other_failures_are_not_rate_limits(self):
        self.assertFalse(_is_rate_limited(Exception("Track not found")))
        self.assertFalse(_is_rate_limited(ValueError("bad identifier")))


class SearchDelayTests(unittest.TestCase):
    def test_a_429_doubles_the_gap_up_to_the_cap(self):
        self.assertAlmostEqual(_next_search_delay(0.35, RATE_LIMIT), 0.7)
        self.assertAlmostEqual(
            _next_search_delay(2.5, Exception("429 Too Many Requests")),
            music_cog._PLAY_RESOLVE_DELAY_MAX,
        )

    def test_a_clean_answer_eases_the_gap_back_to_the_base(self):
        self.assertAlmostEqual(_next_search_delay(2.0), 1.0)
        self.assertAlmostEqual(_next_search_delay(0.0), music_cog._PLAY_RESOLVE_DELAY)

    def test_a_non_rate_limit_error_does_not_widen_the_gap(self):
        self.assertAlmostEqual(_next_search_delay(0.35, Exception("boom")), 0.35)


class PlaylistPacingTests(unittest.IsolatedAsyncioTestCase):
    async def test_the_first_search_is_immediate_and_the_rest_are_spaced(self):
        ctx = _Ctx()
        cog, _ = _build_cog(["q1", "q2", "q3"])
        seen: list[float] = []

        with (
            patch.object(music_cog, "_search_tracks", new=_fake_search(seen)),
            patch.object(music_cog, "_PLAY_RESOLVE_DELAY", 0.05),
        ):
            started = time.monotonic()
            await cog.play.callback(cog, ctx, search="some playlist")

        self.assertEqual(len(seen), 3)
        self.assertLess(
            seen[0] - started, 0.04, "the search that starts playback must not wait"
        )
        for gap in (b - a for a, b in zip(seen, seen[1:])):
            self.assertGreaterEqual(gap, 0.04, f"searches were not spaced: {seen}")

    async def test_a_rate_limited_track_is_retried_not_dropped(self):
        # No alternative node here: the retry has to wait out the backoff.
        ctx = _Ctx()
        cog, player = _build_cog(["q1", "q2", "q3"])
        seen: list[float] = []

        with (
            patch.object(
                music_cog, "_search_tracks", new=_fake_search(seen, rate_limit_once="q2")
            ),
            patch.object(music_cog, "_PLAY_RESOLVE_DELAY", 0.05),
        ):
            await cog.play.callback(cog, ctx, search="some playlist")

        self.assertEqual(len(seen), 4, "q2 must be attempted twice, not skipped")
        self.assertEqual(player.current.title, "Track 1")
        self.assertEqual(
            [t.title for t in player.queue.items],
            ["Track 3", "Track 4"],
            "the throttled track and the one after it must still be queued",
        )
        self.assertGreaterEqual(seen[2] - seen[1], 0.04, "the retry must back off")

    async def test_a_rate_limited_search_hops_to_another_node_and_stays_there(self):
        ctx = _Ctx()
        alt = SimpleNamespace(identifier="alt-node")
        cog, player = _build_cog(["q1", "q2", "q3"], alt_node=alt)
        seen: list[float] = []
        nodes: list[str | None] = []

        with (
            patch.object(
                music_cog,
                "_search_tracks",
                new=_fake_search(seen, nodes, rate_limit_once="q2"),
            ),
            patch.object(music_cog, "_PLAY_RESOLVE_DELAY", 0.05),
        ):
            await cog.play.callback(cog, ctx, search="some playlist")

        self.assertEqual(
            nodes, ["primary", "primary", "alt-node", "alt-node"],
            "the retry and every later search must avoid the throttled node",
        )
        self.assertEqual(len(player.queue.items), 2)

    async def test_every_track_of_a_22_track_playlist_survives_a_throttled_node(self):
        """The reported failure: 22 Spotify entries, seven songs queued."""
        ctx = _Ctx()
        alt = SimpleNamespace(identifier="alt-node")
        searches = [f"spotify track {n}" for n in range(22)]
        cog, player = _build_cog(searches, alt_node=alt)
        nodes: list[str | None] = []

        async def search(query, node=None):
            nodes.append(getattr(node, "identifier", None))
            # The primary node is blocked, exactly like the pool's first node.
            if getattr(node, "identifier", None) == "primary":
                raise RATE_LIMIT
            return [_Track(query)]

        with (
            patch.object(music_cog, "_search_tracks", new=search),
            patch.object(music_cog, "_PLAY_RESOLVE_DELAY", 0.0),
        ):
            await cog.play.callback(cog, ctx, search="https://open.spotify.com/playlist/x")

        self.assertEqual(player.current.title, "spotify track 0")
        self.assertEqual(len(player.queue.items), 21)

    async def test_a_hung_node_is_retried_on_another_one(self):
        ctx = _Ctx()
        alt = SimpleNamespace(identifier="alt-node")
        cog, player = _build_cog(["q1", "q2"], alt_node=alt)
        nodes: list[str | None] = []

        async def search(query, node=None):
            nodes.append(getattr(node, "identifier", None))
            if getattr(node, "identifier", None) == "primary":
                raise asyncio.TimeoutError()
            return [_Track(query)]

        with (
            patch.object(music_cog, "_search_tracks", new=search),
            patch.object(music_cog, "_PLAY_RESOLVE_DELAY", 0.0),
        ):
            await cog.play.callback(cog, ctx, search="some playlist")

        self.assertEqual(nodes, ["primary", "alt-node", "alt-node"])
        self.assertEqual(len(player.queue.items), 1)

    async def test_a_single_search_is_not_delayed_at_all(self):
        ctx = _Ctx()
        cog, _ = _build_cog(["q1"])
        seen: list[float] = []
        cog._send_np = AsyncMock()

        with (
            patch.object(music_cog, "_search_tracks", new=_fake_search(seen)),
            patch.object(music_cog, "_PLAY_RESOLVE_DELAY", 1.0),
        ):
            began = time.monotonic()
            await asyncio.wait_for(
                cog.play.callback(cog, ctx, search="a single song"), timeout=3
            )

        self.assertEqual(len(seen), 1)
        self.assertLess(seen[0] - began, 0.2, "a plain search must not be paced")
