"""A node can forget a player while the client still thinks it is healthy.

A Lavalink node that reconnects without resuming starts a fresh session and
drops every player, and a node can also clean a player up on its own. The
wavelink ``Player`` object survives all of that, so ``Player.connected`` stays
True and the node answers ``404 Not Found`` on
``/v4/sessions/<id>/players/<guild>`` for every control.

That is what the now-playing panel used to report as "the music server didn't
respond — try again in a moment" (see the preview log for guild state at
02:29:19), which is wrong twice over: the server did answer, and retrying never
works. These tests pin the replacement behaviour — the dead session is dropped,
so the next ``/play`` reconnects, and the panel says what actually happened.
"""

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import wavelink

from cogs.music.cog import MusicSystem, _player_gone
from cogs.music.views import _report_failure
from utils.music.messages import MESSAGES


def _lavalink_error(status: int, error: str = "Not Found"):
    """The exception wavelink raises for a JSON error body (a real 404)."""
    return wavelink.LavalinkException(data={
        "timestamp": 0,
        "status": status,
        "error": error,
        "path": "/v4/sessions/r9nwnf09z7kr0y1j/players/1552111524573749258",
    })


class _Panel:
    def __init__(self):
        self.deleted = False

    async def delete(self):
        self.deleted = True


class _Node:
    def __init__(self, info="present", error=None, session_id="r9nwnf09z7kr0y1j"):
        self.identifier = "lavalinkv4.serenetia.com:80"
        self.session_id = session_id
        self._info = info
        self._error = error
        self.lookups = 0

    async def fetch_player_info(self, guild_id):
        self.lookups += 1
        if self._error is not None:
            raise self._error
        return self._info


class _Player:
    def __init__(self):
        self.node = _Node()
        self.guild = SimpleNamespace(id=1)
        self.disconnected = False

    async def disconnect(self):
        self.disconnected = True


class PlayerGoneTests(unittest.TestCase):
    def test_a_missing_player_is_recognised_from_the_status(self):
        self.assertTrue(_player_gone(_lavalink_error(404)))
        self.assertTrue(_player_gone(_lavalink_error(410, "Gone")))
        self.assertTrue(_player_gone(wavelink.NodeException(status=404)))

    def test_other_failures_are_not_a_missing_player(self):
        self.assertFalse(_player_gone(_lavalink_error(500, "Internal Server Error")))
        self.assertFalse(_player_gone(wavelink.NodeException(status=429)))
        self.assertFalse(_player_gone(ValueError("bad identifier")))


class DropDeadSessionTests(unittest.IsolatedAsyncioTestCase):
    def _cog(self, panel=None):
        cog = object.__new__(MusicSystem)
        cog._guild_states = {
            1: {
                "current_track": object(),
                "last_track": object(),
                "np_message": panel,
                "ghost_queue": [object()],
                "ghost_seed": ("artist", "title"),
                "ghost_task": None,
            }
        }
        return cog

    async def test_a_404_drops_the_player_and_its_panel(self):
        panel = _Panel()
        cog   = self._cog(panel)
        player = _Player()

        self.assertTrue(await cog.drop_dead_session(player.guild, player, _lavalink_error(404)))

        self.assertTrue(player.disconnected)
        self.assertTrue(panel.deleted)
        state = cog._guild_states[1]
        self.assertIsNone(state["current_track"])
        self.assertIsNone(state["last_track"])
        self.assertIsNone(state["np_message"])
        self.assertEqual(list(state["ghost_queue"]), [])

    async def test_a_transient_error_keeps_the_session(self):
        panel  = _Panel()
        cog    = self._cog(panel)
        player = _Player()

        self.assertFalse(
            await cog.drop_dead_session(player.guild, player, _lavalink_error(500))
        )

        self.assertFalse(player.disconnected)
        self.assertFalse(panel.deleted)
        self.assertIsNotNone(cog._guild_states[1]["current_track"])

    async def test_a_player_without_guild_state_is_still_dropped(self):
        cog    = self._cog()
        player = _Player()

        self.assertTrue(await cog.drop_dead_session(player.guild, player, _lavalink_error(404)))
        self.assertTrue(player.disconnected)


class RecoverStalePlayerTests(unittest.IsolatedAsyncioTestCase):
    async def test_a_player_the_node_still_has_is_kept(self):
        cog    = object.__new__(MusicSystem)
        cog._guild_states = {}
        player = _Player()
        fresh  = _Player()
        cog.get_player = AsyncMock(return_value=fresh)

        self.assertIs(await cog._recover_stale_player(SimpleNamespace(), player), player)
        cog.get_player.assert_not_awaited()

    async def test_a_player_the_node_lost_is_replaced(self):
        cog    = object.__new__(MusicSystem)
        cog._guild_states = {}
        player = _Player()
        player.node = _Node(info=None)          # the node answers 404
        fresh  = _Player()
        cog.get_player = AsyncMock(return_value=fresh)

        result = await cog._recover_stale_player(SimpleNamespace(), player)

        self.assertIs(result, fresh)
        self.assertTrue(player.disconnected)
        cog.get_player.assert_awaited_once()

    async def test_a_node_between_sessions_is_not_asked(self):
        cog    = object.__new__(MusicSystem)
        cog._guild_states = {}
        player = _Player()
        player.node = _Node(info=None, session_id=None)
        cog.get_player = AsyncMock()

        self.assertIs(await cog._recover_stale_player(SimpleNamespace(), player), player)
        self.assertEqual(player.node.lookups, 0)
        self.assertFalse(player.disconnected)

    async def test_an_unreachable_node_never_drops_the_player(self):
        cog    = object.__new__(MusicSystem)
        cog._guild_states = {}
        player = _Player()
        player.node = _Node(error=ConnectionResetError("boom"))
        cog.get_player = AsyncMock()

        self.assertIs(await cog._recover_stale_player(SimpleNamespace(), player), player)
        self.assertFalse(player.disconnected)
        cog.get_player.assert_not_awaited()


class _WavelinkPlayerStub(wavelink.Player):
    """isinstance target for the panel; never initialised as a real player."""


def _stub_player():
    """A player the panel accepts, with the node side stubbed out."""
    player = object.__new__(_WavelinkPlayerStub)
    player._node    = _Node()
    player._guild   = SimpleNamespace(id=1)
    player.disconnect = AsyncMock()
    return player


class _Interaction:
    def __init__(self, cog, player):
        self.guild  = SimpleNamespace(id=1, preferred_locale="en-US", voice_client=player)
        self.client = SimpleNamespace(get_cog=lambda name: cog)
        self.sent: list[str] = []
        self.followup = SimpleNamespace(send=self._send)

    async def _send(self, content=None, **kwargs):
        self.sent.append(content)


class PanelFailureTests(unittest.IsolatedAsyncioTestCase):
    def _cog(self):
        cog = object.__new__(MusicSystem)
        cog._guild_states = {1: {"current_track": object(), "last_track": None,
                                 "np_message": None, "ghost_task": None,
                                 "ghost_queue": [], "ghost_seed": None}}
        return cog

    async def test_the_panel_reports_a_dropped_session_instead_of_a_retry(self):
        cog    = self._cog()
        player = _stub_player()
        interaction = _Interaction(cog, player)

        await _report_failure(interaction, _lavalink_error(404))

        self.assertEqual(interaction.sent, [MESSAGES["en"]["panel_session_expired"]])
        player.disconnect.assert_awaited_once()

    async def test_other_failures_still_report_the_generic_message(self):
        cog    = self._cog()
        player = _stub_player()
        interaction = _Interaction(cog, player)

        await _report_failure(interaction, _lavalink_error(500, "Internal Server Error"))

        self.assertEqual(interaction.sent, [MESSAGES["en"]["panel_action_failed"]])
        player.disconnect.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
