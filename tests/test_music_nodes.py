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


class _FakeResponse:
    def __init__(self, status, payload=None):
        self.status = status
        self._payload = payload

    async def json(self, content_type=None):
        if isinstance(self._payload, BaseException):
            raise self._payload
        return self._payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _FakeSession:
    """Answers like a Lavalink node that only serves /v4/info with a password."""

    def __init__(self, status, payload=None, *, password=None):
        self.status = status
        self.payload = payload
        self.password = password
        self.calls = []

    def get(self, url, headers=None, timeout=None):
        self.calls.append((url, dict(headers or {})))
        authorized = self.password is not None and (headers or {}).get(
            "Authorization"
        ) == self.password
        if self.password is not None and not authorized:
            return _FakeResponse(401, {"error": "Unauthorized"})
        return _FakeResponse(self.status, self.payload)


class NodeProbeTests(unittest.TestCase):
    """The probe decides which hardcoded nodes the pool is allowed to use.

    It used to call an unauthenticated ``/version`` and require a 200, which
    only the two serenetia twins answer: everything else — including nodes that
    serve the API fine with their password — was discarded as "failed" with no
    reason logged, leaving the pool on the one host with the tightest
    loadtracks rate limit.
    """

    def setUp(self):
        from utils.music import nodes as nodes_mod

        self.nodes = nodes_mod
        self.node = {
            "host": "lava2.kasawa.pro",
            "port": 2334,
            "password": "youshallnotpass",
            "secure": False,
            "version": "v4",
        }

    def _probe(self, session):
        return asyncio.run(
            self.nodes._probe_node(session, self.node, asyncio.Semaphore(1))
        )

    def test_probe_authenticates_against_the_v4_api(self):
        session = _FakeSession(200, {"version": {"semver": "4.2.2"}})

        result = self._probe(session)

        self.assertIsNotNone(result)
        url, headers = session.calls[0]
        self.assertTrue(url.endswith("/v4/info"), url)
        self.assertEqual(headers["Authorization"], "youshallnotpass")
        self.assertFalse(
            [u for u, _ in session.calls if "/version" in u],
            "the unauthenticated /version route must not decide the pool",
        )

    def test_a_node_that_401s_without_a_password_is_usable(self):
        # millohost and kasawa answer "Who are you??" to unauthenticated calls.
        session = _FakeSession(
            200, {"version": {"semver": "4.2.2"}}, password="youshallnotpass"
        )

        self.assertIsNotNone(self._probe(session))

    def test_a_wrong_password_is_rejected(self):
        session = _FakeSession(200, {"version": {}}, password="something-else")

        with mock.patch.object(self.nodes.log, "info") as log_info:
            self.assertIsNone(self._probe(session))

        logged = " ".join(str(c) for c in log_info.call_args_list)
        self.assertIn("Probe rejected lava2.kasawa.pro:2334", logged)
        self.assertIn("401", logged)

    def test_a_200_that_is_not_lavalink_is_rejected(self):
        session = _FakeSession(200, ValueError("not json"))

        self.assertIsNone(self._probe(session))

        session = _FakeSession(200, {"hello": "cloudflare"})
        with mock.patch.object(self.nodes.log, "info"):
            self.assertIsNone(self._probe(session))

    def test_every_rejection_is_logged_with_its_reason(self):
        with mock.patch.object(self.nodes.log, "info") as log_info:
            self.assertIsNone(self._probe(_FakeSession(530, {})))

        logged = " ".join(str(c) for c in log_info.call_args_list)
        self.assertIn("Probe rejected lava2.kasawa.pro:2334", logged)
        self.assertIn("530", logged)


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
