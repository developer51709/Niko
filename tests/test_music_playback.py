import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.music.cog import MusicSystem


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
