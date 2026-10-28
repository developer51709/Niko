"""Regression checks for resilient Lavalink discovery, failover and rescans.

The music cog talks to a pool of *public* Lavalink nodes, so most of its
resilience lives in retries, failover and reconnect pacing. These tests pin
that behaviour down without a live node.
"""

import asyncio
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.music import cog as music_cog  # noqa: E402

COG_SOURCE = (ROOT / "src/cogs/music/cog.py").read_text(encoding="utf-8")


class _NodeDown(Exception):
    """Stand-in for a Lavalink 500 as wavelink surfaces it."""

    status = 500


class HardcodedCatalogTests(unittest.TestCase):
    def test_hardcoded_lavalink_catalog_is_available(self):
        source = (ROOT / "src/config/lavalink.py").read_text(encoding="utf-8")
        assert "LAVALINK_NODES" in source
        assert '"host":' in source
        assert '"password":' in source


class RescanBackoffTests(unittest.TestCase):
    """An empty pool must not wait an hour before trying again."""

    def test_full_pool_rescans_hourly(self):
        full = music_cog._MAX_CONNECT_NODES
        self.assertEqual(music_cog._next_rescan_delay(full, 0), 3600)
        self.assertEqual(music_cog._next_rescan_delay(full + 2, 45), 3600)

    def test_partial_pool_retries_sooner_than_a_full_one(self):
        partial = music_cog._MAX_CONNECT_NODES - 1
        self.assertEqual(
            music_cog._next_rescan_delay(partial, 0), music_cog._NODE_PARTIAL_INTERVAL
        )

    def test_empty_pool_starts_at_the_minimum(self):
        self.assertEqual(
            music_cog._next_rescan_delay(0, 0), music_cog._NODE_RETRY_MIN
        )

    def test_empty_pool_backs_off_then_caps(self):
        self.assertEqual(music_cog._next_rescan_delay(0, 30), 60)
        self.assertEqual(music_cog._next_rescan_delay(0, 120), 240)
        self.assertEqual(
            music_cog._next_rescan_delay(0, 3600), music_cog._NODE_RETRY_MAX
        )


class PlayerOpRetryTests(unittest.TestCase):
    """`_player_op` is the single retry/failover wrapper for player actions."""

    def test_retries_transient_500_with_failover(self):
        attempts = {"count": 0}
        failovers = {"count": 0}

        async def operation():
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise _NodeDown("status=500")
            return "played"

        async def failover():
            failovers["count"] += 1

        with mock.patch.object(music_cog, "_LAVELINK_500_DELAY", 0):
            result = asyncio.run(
                music_cog._player_op(operation, failover=failover)
            )

        self.assertEqual(result, "played")
        self.assertEqual(attempts["count"], 3)
        self.assertEqual(failovers["count"], 2)

    def test_gives_up_after_the_retry_budget(self):
        attempts = {"count": 0}

        async def operation():
            attempts["count"] += 1
            raise _NodeDown("status=500")

        with mock.patch.object(music_cog, "_LAVELINK_500_DELAY", 0):
            with self.assertRaises(_NodeDown):
                asyncio.run(music_cog._player_op(operation))

        self.assertEqual(attempts["count"], music_cog._LAVELINK_500_RETRIES)

    def test_non_transient_errors_are_not_retried(self):
        attempts = {"count": 0}

        async def operation():
            attempts["count"] += 1
            raise ValueError("bad track identifier")

        with self.assertRaises(ValueError):
            asyncio.run(music_cog._player_op(operation))

        self.assertEqual(attempts["count"], 1)

    def test_detects_the_wrapped_error_shapes(self):
        self.assertTrue(music_cog._is_lavalink_500(_NodeDown("status=500")))
        self.assertTrue(
            music_cog._is_lavalink_500(RuntimeError("500 Internal Server Error"))
        )
        self.assertFalse(music_cog._is_lavalink_500(ValueError("nope")))


class WavelinkApiTests(unittest.TestCase):
    """Guards against drifting back onto wavelink 2 API names."""

    def test_failover_uses_the_live_node_switch(self):
        self.assertIn("await player.switch_node(new_node)", COG_SOURCE)
        # `Player.node` is read-only in wavelink 3; assigning it raised
        # AttributeError, which silently disabled every failover path.
        self.assertNotIn("player.node = new_node", COG_SOURCE)

    def test_player_health_uses_the_connected_property(self):
        self.assertIn("bool(player.connected)", COG_SOURCE)
        self.assertNotIn('"is_connected"', COG_SOURCE)

    def test_full_pool_skips_discovery(self):
        self.assertIn("skipping discovery", COG_SOURCE)
        self.assertIn("if capacity <= 0:", COG_SOURCE)

    def test_lost_nodes_top_the_pool_back_up(self):
        self.assertIn("self.startup_connect(retry_delay=5)", COG_SOURCE)

    def test_inactive_and_external_disconnects_are_handled(self):
        self.assertIn("async def on_wavelink_inactive_player", COG_SOURCE)
        self.assertIn("async def on_voice_state_update", COG_SOURCE)

    def test_playlist_results_queue_every_track(self):
        self.assertIn("isinstance(results, wavelink.Playlist)", COG_SOURCE)
        self.assertIn("_MAX_TRACKS_PER_PLAY", COG_SOURCE)

    def test_only_play_is_exposed_as_a_slash_command(self):
        """Discord caps global application commands at 100.

        This bot already sits at that ceiling: exposing the music controls as
        hybrid commands pushed ``cogs.notifier`` over the limit and stopped it
        from loading. Only ``/play`` may be a slash command; the rest stay
        prefix commands (and buttons on the panel).
        """
        import re

        self.assertIn('@commands.hybrid_command(\n        name="play"', COG_SOURCE)
        for name in (
            "pause", "resume", "skip", "stop", "loop", "autoplay", "queue",
            "like", "liked", "unlike", "nowplaying", "volume", "disconnect",
            "musicstatus",
        ):
            pattern = re.compile(rf'@commands\.command\(\s*name="{name}"')
            self.assertTrue(pattern.search(COG_SOURCE), f"{name} should stay prefix-only")

    def test_slash_invocations_are_deferred(self):
        self.assertIn("async def cog_before_invoke", COG_SOURCE)
        self.assertIn("await interaction.response.defer()", COG_SOURCE)
