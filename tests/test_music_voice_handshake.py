"""The Discord voice handshake must not depend on one node's voice path.

The preview log showed the bot joining a channel and leaving again within a
second while every node reported connected: the player PATCH that carries
Discord's voice credentials was sent to a node whose Lavalink could not open
the voice socket, wavelink swallowed the failure and disconnected the player,
and the only trace was a 20 second connect timeout followed by "not connected
to any music servers".

These tests pin the replacement: the handshake is bounded, a node that refuses
it is logged and skipped, the next node is asked instead, and a pool that is up
is never described as empty.
"""

import asyncio
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import discord
import wavelink

from cogs.music import cog as music_cog
from cogs.music.cog import (
    MusicPlayer,
    VoiceHandshakeError,
    _voice_blocked_identifiers,
    _voice_candidates,
)
from utils.music.messages import MESSAGES


def _lavalink_error(status: int, error: str = "Internal Server Error"):
    return wavelink.LavalinkException(data={
        "timestamp": 0,
        "status": status,
        "error": error,
        "path": "/v4/sessions/r9nwnf09z7kr0y1j/players/1",
    })


class _Node:
    """Just enough of a wavelink Node for the handshake code."""

    def __init__(self, identifier, *, players=0, update=None):
        self.identifier = identifier
        self.status = wavelink.NodeStatus.CONNECTED
        self._players = {index: object() for index in range(players)}
        self._update = update
        self.destroyed = 0

    @property
    def players(self):
        return self._players

    async def _update_player(self, guild_id, *, data):
        assert data["voice"]["token"] == "voice-token"
        if self._update is not None:
            return await self._update(guild_id, data)
        self._players[guild_id] = "accepted"
        return {"guildId": str(guild_id)}

    async def _destroy_player(self, guild_id):
        self.destroyed += 1
        self._players.pop(guild_id, None)


def _player(node, *, guild_id=1):
    """A MusicPlayer with only the attributes the handshake touches."""
    player = object.__new__(MusicPlayer)
    player._node = node
    player._guild = SimpleNamespace(id=guild_id)
    player._connected = False
    player._connection_event = asyncio.Event()
    player._voice_failure = asyncio.Event()
    player._voice_dispatch = asyncio.Event()
    player._voice_error = None
    player._voice_state = {
        "voice": {"session_id": "voice-session", "token": "voice-token",
                  "endpoint": "discord.example:50000"},
        "channel_id": "4242",
    }
    return player


async def _refuse(guild_id, data):
    raise _lavalink_error(500)


async def _hang(guild_id, data):
    await asyncio.sleep(30)


class HandshakeFailoverTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        music_cog._voice_backoff_until.clear()
        self.addCleanup(music_cog._voice_backoff_until.clear)

    async def test_a_closed_voice_port_is_skipped_for_a_node_that_takes_it(self):
        dead  = _Node("private.example:443", update=_refuse)
        alive = _Node("lava2.kasawa.pro:2334")
        player = _player(dead)

        with patch.object(music_cog, "_connected_nodes", return_value=[dead, alive]):
            await player._dispatch_voice_update()

        self.assertTrue(player._connection_event.is_set())
        self.assertTrue(player._connected)
        self.assertIs(player.node, alive)
        self.assertIs(alive._players[1], player)
        self.assertEqual(dead._players, {})
        self.assertIn(dead.identifier, _voice_blocked_identifiers())
        self.assertNotIn(alive.identifier, _voice_blocked_identifiers())

    async def test_a_silent_node_times_out_instead_of_hanging_the_handshake(self):
        silent = _Node("private.example:443", update=_hang)
        alive  = _Node("lavalinkv4.serenetia.com:80")
        player = _player(silent)

        with patch.object(music_cog, "_VOICE_HANDSHAKE_TIMEOUT", 0.05), \
             patch.object(music_cog, "_connected_nodes", return_value=[silent, alive]):
            await player._dispatch_voice_update()

        self.assertTrue(player._connection_event.is_set())
        self.assertIs(player.node, alive)
        self.assertIn(silent.identifier, _voice_blocked_identifiers())

    async def test_every_node_failing_reports_the_real_reason(self):
        first  = _Node("private.example:443", update=_refuse)
        second = _Node("lava2.kasawa.pro:2334", update=_hang)
        player = _player(first)

        with patch.object(music_cog, "_VOICE_HANDSHAKE_TIMEOUT", 0.05), \
             patch.object(music_cog, "_connected_nodes", return_value=[first, second]):
            await player._dispatch_voice_update()

        self.assertFalse(player._connection_event.is_set())
        self.assertTrue(player._voice_failure.is_set())
        self.assertIn("HTTP 500", player._voice_error)
        self.assertIn("did not answer", player._voice_error)
        self.assertEqual(_voice_blocked_identifiers(), {first.identifier, second.identifier})

    async def test_a_node_that_starts_working_again_is_cleared(self):
        node = _Node("private.example:443", update=_refuse)
        player = _player(node)

        with patch.object(music_cog, "_connected_nodes", return_value=[node]):
            await player._dispatch_voice_update()
        self.assertIn(node.identifier, _voice_blocked_identifiers())

        node._update = None
        await player._dispatch_voice_update()

        self.assertNotIn(node.identifier, _voice_blocked_identifiers())


class CandidateOrderTests(unittest.TestCase):
    def setUp(self):
        music_cog._voice_backoff_until.clear()
        self.addCleanup(music_cog._voice_backoff_until.clear)

    def test_a_blocked_node_is_tried_last(self):
        blocked = _Node("private.example:443")
        busy    = _Node("a.example:2333", players=3)
        quiet   = _Node("b.example:2333")
        music_cog._mark_voice_blocked(blocked)

        ordered = _voice_candidates(blocked, nodes=[blocked, busy, quiet])

        self.assertEqual([node.identifier for node in ordered],
                         ["b.example:2333", "a.example:2333", "private.example:443"])

    def test_the_players_current_node_keeps_priority(self):
        current = _Node("a.example:2333", players=2)
        other   = _Node("b.example:2333")

        ordered = _voice_candidates(current, nodes=[other, current])

        self.assertIs(ordered[0], current)


class ConnectTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        music_cog._voice_backoff_until.clear()
        self.addCleanup(music_cog._voice_backoff_until.clear)

    def _connectable(self, node):
        player = _player(node)
        player.channel = SimpleNamespace(guild=player._guild)
        player._guild.change_voice_state = AsyncMock()
        player.disconnect = AsyncMock()
        return player

    async def test_a_failed_handshake_fails_fast_and_leaves_the_channel(self):
        node = _Node("private.example:443")
        player = self._connectable(node)
        player._voice_error = "private.example:443 refused it (HTTP 500)"
        player._voice_failure.set()

        started = time.monotonic()
        with patch.object(music_cog, "_connected_nodes", return_value=[node]):
            with self.assertRaises(VoiceHandshakeError) as caught:
                await player.connect(timeout=20, reconnect=False)

        self.assertLess(time.monotonic() - started, 1.0, "must not wait out the timeout")
        self.assertIn("HTTP 500", str(caught.exception))
        player.disconnect.assert_awaited_once()

    async def test_the_next_player_avoids_a_node_that_refused_the_handshake(self):
        dead  = _Node("private.example:443")
        alive = _Node("lava2.kasawa.pro:2334")
        music_cog._mark_voice_blocked(dead)
        player = self._connectable(dead)
        player._voice_failure.set()

        with patch.object(music_cog, "_connected_nodes", return_value=[dead, alive]):
            with self.assertRaises(VoiceHandshakeError):
                await player.connect(timeout=20, reconnect=False)

        self.assertIs(player.node, alive)
        player._guild.change_voice_state.assert_awaited_once()


class NudgeTests(unittest.IsolatedAsyncioTestCase):
    def _player(self, node, *, dispatched=False):
        player = _player(node)
        player.channel = SimpleNamespace(guild=player._guild)
        player._guild.change_voice_state = AsyncMock()
        if dispatched:
            player._voice_dispatch.set()
        return player

    async def test_a_missing_voice_update_is_asked_for_again(self):
        player = self._player(_Node("a.example:2333"))

        with patch.object(music_cog, "_VOICE_NUDGE_DELAY", 0.05):
            await player._nudge_voice_state(self_mute=False, self_deaf=False)

        player._guild.change_voice_state.assert_awaited_once()

    async def test_a_delivered_voice_update_is_not_asked_for_again(self):
        player = self._player(_Node("a.example:2333"), dispatched=True)

        with patch.object(music_cog, "_VOICE_NUDGE_DELAY", 0.05):
            await player._nudge_voice_state(self_mute=False, self_deaf=False)

        player._guild.change_voice_state.assert_not_awaited()

    async def test_the_dispatch_marks_the_voice_update_as_arrived(self):
        node = _Node("a.example:2333")
        player = _player(node)

        with patch.object(music_cog, "_connected_nodes", return_value=[node]):
            await player._dispatch_voice_update()

        self.assertTrue(player._voice_dispatch.is_set())


class LostPlayerQuarantineTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        music_cog._voice_backoff_until.clear()
        self.addCleanup(music_cog._voice_backoff_until.clear)

    async def test_a_node_that_lost_the_player_leaves_the_voice_rotation(self):
        cog = object.__new__(music_cog.MusicSystem)
        cog._guild_states = {}
        node = _Node("private.example:443")
        player = _player(node)
        player.disconnect = AsyncMock()

        self.assertTrue(await cog.drop_dead_session(player.guild, player))

        self.assertIn(node.identifier, _voice_blocked_identifiers())
        player.disconnect.assert_awaited_once()


class SearchFailoverTests(unittest.IsolatedAsyncioTestCase):
    async def test_a_node_side_lookup_fault_is_retried_on_another_node(self):
        cog      = object.__new__(music_cog.MusicSystem)
        primary  = _Node("private.example:443")
        backup   = _Node("lava2.kasawa.pro:2334")
        calls    = []
        cog._get_alt_node = lambda exclude=None: backup if exclude is primary else None

        async def search(query, node=None):
            calls.append(node.identifier if node is not None else None)
            if node is primary:
                raise RuntimeError("Something went wrong while looking up the track.")
            return ["track"]

        with patch.object(music_cog, "_search_tracks", search):
            results, _delay, node = await cog._search_for_play("ytsearch:test", primary, 0)

        self.assertEqual(results, ["track"])
        self.assertIs(node, backup)
        self.assertEqual(calls, [primary.identifier, backup.identifier])


class VoiceFailureMessageTests(unittest.TestCase):
    def test_the_new_message_exists_in_every_locale(self):
        for lang in ("en", "de", "es", "fr"):
            self.assertIn("music_voice_failed", MESSAGES[lang])


if __name__ == "__main__":
    unittest.main()
