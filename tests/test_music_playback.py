import sys
import unittest
from collections import deque
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import discord

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.music import views
from cogs.music.cog import MusicSystem
from config.emojis import get_emoji


def _panel_buttons() -> dict:
    """Build a real now-playing panel and index its buttons by label."""
    track = SimpleNamespace(
        source="youtube", author="artist", title="song", length=200_000,
        uri="https://example.test/watch?v=abc123", artwork=None,
    )
    player = SimpleNamespace(
        current=track, paused=False, volume=50, position=1_000, playing=True, queue=[],
    )
    cog = SimpleNamespace(
        _state=lambda _gid: {
            "current_track": track,
            "history": deque(),
            "loop": False,
            "autoplay": False,
            "ghost_queue": deque(),
        },
        _lastfm_key=None,
    )
    view = views._build_np_view(player, SimpleNamespace(id=1), cog)
    return {
        child.label: child
        for child in view.walk_children()
        if isinstance(child, discord.ui.Button)
    }


class NowPlayingPanelEmojiTests(unittest.TestCase):
    """The panel's controls use the bot's own emoji set, not unicode glyphs."""

    def test_queue_and_volume_buttons_use_custom_emojis(self):
        buttons = _panel_buttons()
        for label, key in (
            ("Queue", "queue"),
            ("Vol -", "volume_down"),
            ("Vol +", "volume_up"),
            ("Autoplay", "autoplay"),
        ):
            emoji = buttons[label].emoji
            self.assertIsNotNone(emoji, f"{label} has no emoji")
            self.assertEqual(str(emoji), get_emoji(key), f"{label} uses the wrong emoji")

    def test_like_button_uses_the_custom_heart(self):
        emoji = _panel_buttons()["Like"].emoji
        self.assertIsNotNone(emoji)
        self.assertEqual(str(emoji), get_emoji("heart"))
        self.assertNotEqual(str(emoji), "♥")


class MusicPlaybackTests(unittest.IsolatedAsyncioTestCase):
    async def test_stale_track_end_does_not_idle_a_newer_track(self):
        old_track = SimpleNamespace(title="old", encoded="old", author="artist")
        active_track = SimpleNamespace(title="new", encoded="new", author="artist")
        player = SimpleNamespace(
            guild=SimpleNamespace(id=123),
            current=active_track,
        )
        cog = object.__new__(MusicSystem)
        cog._guild_states = {
            123: {"current_track": active_track, "history": []}
        }
        cog._update_np_message = AsyncMock()

        await cog.on_wavelink_track_end(
            SimpleNamespace(player=player, track=old_track, reason="replaced")
        )

        self.assertIs(cog._guild_states[123]["current_track"], active_track)
        self.assertEqual(cog._guild_states[123]["history"], [])
        cog._update_np_message.assert_not_awaited()

    async def test_stuck_track_is_skipped_and_marked(self):
        track = SimpleNamespace(title="stalled", encoded="enc", author="artist")
        player = SimpleNamespace(
            guild=SimpleNamespace(id=789),
            skip=AsyncMock(),
        )
        cog = object.__new__(MusicSystem)
        cog._guild_states = {
            789: {"current_track": track, "history": [], "stuck_track": None}
        }

        await cog.on_wavelink_track_stuck(
            SimpleNamespace(player=player, track=track, threshold=10_000)
        )

        player.skip.assert_awaited_once_with(force=True)
        self.assertEqual(cog._guild_states[789]["stuck_track"], "enc")

    async def test_load_failure_retries_track_on_an_alternate_node(self):
        track = SimpleNamespace(title="song", encoded="encoded", author="artist")
        player = SimpleNamespace(
            guild=SimpleNamespace(id=456),
            current=track,
            node=SimpleNamespace(identifier="node-a"),
        )
        cog = object.__new__(MusicSystem)
        cog.bot = SimpleNamespace()
        cog._guild_states = {
            456: {"current_track": track, "history": []}
        }
        cog._update_np_message = AsyncMock()
        cog._failover_player = AsyncMock(return_value=True)

        await cog.on_wavelink_track_end(
            SimpleNamespace(player=player, track=track, reason="loadFailed")
        )

        cog._failover_player.assert_awaited_once_with(player, track)
        cog._update_np_message.assert_awaited_once_with(player.guild)
        self.assertIs(cog._guild_states[456]["current_track"], track)
        self.assertEqual(cog._guild_states[456]["history"], [])


if __name__ == "__main__":
    unittest.main()
