"""`/play` reports a whole playlist through one message.

A Spotify playlist used to produce a resolving card, a deletion, a separate
"added N" card and then the now-playing panel. Every stage is now an edit of
the same message, and the Lavalink searches behind it are spaced out so the
node does not answer 429 for the rest of the playlist.
"""

import asyncio
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import discord

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cogs.music.cog as music_cog
from cogs.music.cog import MusicSystem, _next_search_delay


def _view_text(view) -> str:
    """Flatten a LayoutView into the text it would display."""
    texts: list[str] = []

    def walk(item):
        content = getattr(item, "content", None)
        if isinstance(content, str):
            texts.append(content)
        for child in getattr(item, "children", None) or ():
            walk(child)

    walk(view)
    return "\n".join(texts)


class _Message:
    def __init__(self, ctx, content=None, view=None):
        self.ctx = ctx
        self.id = ctx.next_id()
        self.initial = _view_text(view) if view is not None else content
        self.edits: list[str] = []
        self.deleted = False
        self.edit_raises = False

    async def edit(self, **kwargs):
        if self.edit_raises:
            raise discord.NotFound(Mock(status=404), "gone")
        self.edits.append(_view_text(kwargs.get("view")))
        return self

    async def delete(self):
        self.deleted = True


class _Ctx:
    def __init__(self):
        self._ids = 0
        self.sent: list[_Message] = []
        self.guild = SimpleNamespace(id=1, preferred_locale="en-US")
        self.author = SimpleNamespace(voice=SimpleNamespace(channel=object()))
        self.channel = SimpleNamespace(id=5)

    def next_id(self):
        self._ids += 1
        return self._ids

    async def send(self, content=None, view=None, **kwargs):
        message = _Message(self, content, view)
        self.sent.append(message)
        return message


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
    def __init__(self, cog, guild_id):
        self.cog = cog
        self.guild_id = guild_id
        self.playing = False
        self.paused = False
        self.current = None
        self.queue = _Queue()
        self.node = None
        self.volume = 100
        self.position = 0
        self.channel = None

    async def play(self, track):
        self.playing = True
        self.current = track
        event = self.cog._track_start_events.get(self.guild_id)
        if event is not None:
            event.set()


def _build_cog(searches, *, tracks=("Track A", "Track B")):
    cog = object.__new__(MusicSystem)
    cog.bot = SimpleNamespace(command_prefix=".")
    cog._guild_states = {}
    cog._track_start_events = {}
    cog._lastfm_key = None
    cog._schedule_ghost_refill = Mock()
    cog._resolve_query = AsyncMock(return_value=searches)
    player = _Player(cog, 1)
    cog.get_player = AsyncMock(return_value=player)
    return cog, player


def _fake_search(titles, seen=None):
    """Stands in for a Lavalink search returning the next canned title."""
    pending = list(titles)

    async def search(query, node=None):
        if seen is not None:
            seen.append(time.monotonic())
        title = pending.pop(0) if pending else None
        return [] if title is None else [_Track(title)]

    return search


def _patch_view(marker="NP PANEL"):
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.TextDisplay(content=marker))
    return lambda *args, **kwargs: view


class PlayStatusMessageTests(unittest.IsolatedAsyncioTestCase):
    async def test_a_playlist_reports_every_stage_by_editing_one_message(self):
        ctx = _Ctx()
        cog, _ = _build_cog(["ytsearch:a", "ytsearch:b"])
        search = _fake_search(["Track A", "Track B"])

        with (
            patch.object(music_cog, "_search_tracks", new=search),
            patch.object(music_cog, "_build_np_view", new=_patch_view()),
            patch.object(music_cog, "_PLAY_RESOLVE_DELAY", 0.0),
            patch.object(music_cog, "_STATUS_EDIT_INTERVAL", 0.0),
            patch.object(music_cog, "_ADDED_CARD_HOLD", 0.0),
        ):
            await cog.play.callback(cog, ctx, search="https://open.spotify.com/playlist/abc")

        self.assertEqual(len(ctx.sent), 1, "a playlist must leave one message behind")
        status = ctx.sent[0]
        self.assertFalse(status.deleted, "the status message is reused, not deleted")
        self.assertIn("Resolving Spotify link", status.initial)
        self.assertTrue(
            any("tracks ready" in text for text in status.edits),
            f"expected a progress update, got {status.edits}",
        )
        self.assertTrue(
            any("Added 1 track(s)" in text for text in status.edits),
            f"expected the added confirmation, got {status.edits}",
        )
        self.assertEqual(status.edits[-1], "NP PANEL", "the card becomes the panel")

    async def test_a_single_track_link_turns_the_card_into_the_panel(self):
        ctx = _Ctx()
        cog, _ = _build_cog(["ytsearch:a"])

        with (
            patch.object(music_cog, "_search_tracks", new=_fake_search(["Only Track"])),
            patch.object(music_cog, "_build_np_view", new=_patch_view()),
            patch.object(music_cog, "_PLAY_RESOLVE_DELAY", 0.0),
        ):
            await cog.play.callback(cog, ctx, search="spotify:track:abc")

        self.assertEqual(len(ctx.sent), 1)
        self.assertEqual(ctx.sent[0].edits[-1], "NP PANEL")

    async def test_an_unresolvable_link_is_reported_in_the_same_message(self):
        ctx = _Ctx()
        cog, _ = _build_cog(None)

        await cog.play.callback(cog, ctx, search="https://open.spotify.com/playlist/abc")

        self.assertEqual(len(ctx.sent), 1)
        self.assertIn("Couldn't resolve that Spotify link", ctx.sent[0].edits[-1])

    async def test_a_plain_search_still_gets_its_own_panel(self):
        ctx = _Ctx()
        cog, _ = _build_cog(["ytsearch:a"])

        with (
            patch.object(music_cog, "_search_tracks", new=_fake_search(["Song"])),
            patch.object(music_cog, "_build_np_view", new=_patch_view()),
            patch.object(music_cog, "_PLAY_RESOLVE_DELAY", 0.0),
        ):
            await cog.play.callback(cog, ctx, search="some song")

        self.assertEqual(len(ctx.sent), 1, "status card + panel would be two messages")
        self.assertEqual(ctx.sent[0].edits, [], "a plain search has no card to edit")


class SearchPacingTests(unittest.IsolatedAsyncioTestCase):
    async def test_playlist_searches_are_spaced_out(self):
        ctx = _Ctx()
        searches = ["ytsearch:a", "ytsearch:b", "ytsearch:c"]
        cog, _ = _build_cog(searches)
        seen: list[float] = []

        with (
            patch.object(music_cog, "_search_tracks", new=_fake_search(["A", "B", "C"], seen)),
            patch.object(music_cog, "_build_np_view", new=_patch_view()),
            patch.object(music_cog, "_PLAY_RESOLVE_DELAY", 0.05),
            patch.object(music_cog, "_STATUS_EDIT_INTERVAL", 10.0),
            patch.object(music_cog, "_ADDED_CARD_HOLD", 0.0),
        ):
            await cog.play.callback(cog, ctx, search="https://open.spotify.com/playlist/abc")

        self.assertEqual(len(seen), 3)
        gaps = [b - a for a, b in zip(seen, seen[1:])]
        for gap in gaps:
            self.assertGreaterEqual(gap, 0.04, f"searches were not spaced: {gaps}")

    async def test_a_429_widens_the_gap_and_a_success_narrows_it_again(self):
        self.assertAlmostEqual(_next_search_delay(0.35, Exception("429")), 0.7)
        self.assertAlmostEqual(
            _next_search_delay(2.5, Exception("429 Too Many Requests")),
            music_cog._PLAY_RESOLVE_DELAY_MAX,
        )
        self.assertAlmostEqual(_next_search_delay(1.0), 0.5)
        # Never below the base gap, never above the cap.
        self.assertAlmostEqual(_next_search_delay(0.0), music_cog._PLAY_RESOLVE_DELAY)
        self.assertAlmostEqual(_next_search_delay(999.0), 999.0 / 2)


class SendNpReuseTests(unittest.IsolatedAsyncioTestCase):
    async def test_a_status_message_that_cannot_be_edited_still_yields_a_panel(self):
        ctx = _Ctx()
        cog, player = _build_cog(["ytsearch:a"])
        status = _Message(ctx, "Resolving…")
        status.edit_raises = True

        with patch.object(music_cog, "_build_np_view", new=_patch_view()):
            await cog._send_np(ctx, player, edit=status)

        self.assertEqual(len(ctx.sent), 1, "a fresh panel must be sent as a fallback")
        self.assertIs(cog._guild_states[1]["np_message"], ctx.sent[0])
