"""Last.fm scrobbling: signed writes, the play threshold and opt-in consent."""

import asyncio
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.lastfm.client import LastFmClient, api_signature  # noqa: E402


class SignedWriteTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.captured = {}

        async def fake_post(method, params):
            self.captured["method"] = method
            self.captured["params"] = params
            return {}

        self.client = LastFmClient("api-key", api_secret="shared-secret")
        self.client._post = fake_post  # type: ignore[assignment]

    async def test_now_playing_is_signed_over_the_method_and_its_parameters(self):
        await self.client.update_now_playing(
            "session-key", artist="Artist", title="Title", duration=215,
        )

        self.assertEqual(self.captured["method"], "track.updateNowPlaying")
        params = self.captured["params"]
        self.assertEqual(params["sk"], "session-key")
        self.assertEqual(params["duration"], "215")
        expected = api_signature(
            "shared-secret",
            {
                "method": "track.updateNowPlaying",
                "api_key": "api-key",
                **{k: v for k, v in params.items() if k != "api_sig"},
            },
        )
        self.assertEqual(params["api_sig"], expected)

    async def test_a_scrobble_carries_the_time_the_track_started(self):
        await self.client.scrobble(
            "session-key", artist="Artist", title="Title", timestamp=1_700_000_000,
        )

        self.assertEqual(self.captured["method"], "track.scrobble")
        params = self.captured["params"]
        self.assertEqual(params["timestamp"], "1700000000")
        self.assertEqual(
            params["api_sig"],
            api_signature(
                "shared-secret",
                {
                    "method": "track.scrobble",
                    "api_key": "api-key",
                    **{k: v for k, v in params.items() if k != "api_sig"},
                },
            ),
        )

    async def test_writes_need_the_shared_secret(self):
        client = LastFmClient("api-key")
        with self.assertRaises(Exception):
            await client.update_now_playing("session-key", artist="A", title="T")


class ScrobbleThresholdTests(unittest.TestCase):
    def test_a_track_under_thirty_seconds_never_counts(self):
        from cogs.music.cog import _scrobble_threshold_ms

        self.assertEqual(_scrobble_threshold_ms(29_999), 0)
        self.assertEqual(_scrobble_threshold_ms(30_000), 15_000)

    def test_half_the_track_is_capped_at_four_minutes(self):
        from cogs.music.cog import _scrobble_threshold_ms

        self.assertEqual(_scrobble_threshold_ms(180_000), 90_000)
        self.assertEqual(_scrobble_threshold_ms(600_000), 240_000)


class _Writer:
    def __init__(self):
        self.now_playing = []
        self.scrobbles = []

    async def update_now_playing(self, session_key, **kwargs):
        self.now_playing.append((session_key, kwargs))

    async def scrobble(self, session_key, **kwargs):
        self.scrobbles.append((session_key, kwargs))


async def _drain(cog):
    tasks = list(cog._scrobble_tasks)
    if tasks:
        await asyncio.gather(*tasks)


def _cog(*, consented=True):
    from cogs.music.cog import MusicSystem

    cog = object.__new__(MusicSystem)
    cog.bot = SimpleNamespace()
    cog._guild_states = {}
    cog._lastfm_writer = _Writer()
    cog._scrobble_tasks = set()

    async def session(user_id):
        return "session-key" if consented and user_id == 7 else None

    cog._scrobble_session = session
    return cog


def _track(requester_id=7, length=300_000):
    extras = {} if requester_id is None else {"requester_id": requester_id}
    return SimpleNamespace(
        title="Song", author="Artist", length=length, extras=extras,
    )


class ScrobblePathTests(unittest.IsolatedAsyncioTestCase):
    """Consent, requester and progress threshold, end to end through the cog."""

    def setUp(self):
        self.guild = SimpleNamespace(id=99)

    async def test_progress_below_the_threshold_never_scrobbles(self):
        cog = _cog()
        track = _track()
        player = SimpleNamespace(guild=self.guild, current=track)

        cog._scrobble_started(self.guild, track)
        await _drain(cog)
        self.assertEqual(len(cog._lastfm_writer.now_playing), 1)

        for position in (30_000, 90_000, 149_000):
            cog._scrobble_progress(player, position)
        cog._scrobble_finished(self.guild, track, "finished")
        await _drain(cog)

        self.assertEqual(cog._lastfm_writer.scrobbles, [])

    async def test_wavelinks_extras_namespace_still_finds_the_requester(self):
        from wavelink.utils import ExtrasNamespace

        cog = _cog()
        track = SimpleNamespace(
            title="Song", author="Artist", length=300_000,
            extras=ExtrasNamespace({"requester_id": 7}),
        )

        cog._scrobble_started(self.guild, track)

        candidate = cog._state(self.guild.id)["scrobble"]
        self.assertEqual(candidate["user_id"], 7)
        await _drain(cog)
        self.assertEqual(len(cog._lastfm_writer.now_playing), 1)

    async def test_a_pause_cannot_earn_a_scrobble_by_wall_clock(self):
        cog = _cog()
        track = _track()
        player = SimpleNamespace(guild=self.guild, current=track)

        cog._scrobble_started(self.guild, track)
        candidate = cog._state(self.guild.id)["scrobble"]
        # The track has been loaded for ten minutes, but only ten seconds of
        # audio actually played before the member paused it.
        candidate["started_at"] -= 600
        cog._scrobble_progress(player, 10_000)
        cog._scrobble_finished(self.guild, track, "finished")
        await _drain(cog)

        self.assertEqual(cog._lastfm_writer.scrobbles, [])

    async def test_enough_played_progress_scrobbles_for_the_requester(self):
        cog = _cog()
        track = _track()
        player = SimpleNamespace(guild=self.guild, current=track)

        cog._scrobble_started(self.guild, track)
        started_at = cog._state(self.guild.id)["scrobble"]["started_at"]
        cog._scrobble_progress(player, 200_000)
        cog._scrobble_finished(self.guild, track, "finished")
        await _drain(cog)

        self.assertEqual(len(cog._lastfm_writer.scrobbles), 1)
        session_key, params = cog._lastfm_writer.scrobbles[0]
        self.assertEqual(session_key, "session-key")
        self.assertEqual(params["artist"], "Artist")
        self.assertEqual(params["title"], "Song")
        self.assertEqual(params["duration"], 300)
        self.assertEqual(params["timestamp"], int(started_at))

    async def test_a_member_without_consent_scrobbles_nothing(self):
        cog = _cog(consented=False)
        track = _track()
        player = SimpleNamespace(guild=self.guild, current=track)

        cog._scrobble_started(self.guild, track)
        cog._scrobble_progress(player, 200_000)
        cog._scrobble_finished(self.guild, track, "finished")
        await _drain(cog)

        self.assertEqual(cog._lastfm_writer.now_playing, [])
        self.assertEqual(cog._lastfm_writer.scrobbles, [])

    async def test_a_track_nobody_requested_is_never_scrobbled(self):
        cog = _cog()
        track = _track(requester_id=None)
        player = SimpleNamespace(guild=self.guild, current=track)

        cog._scrobble_started(self.guild, track)
        cog._scrobble_progress(player, 200_000)
        cog._scrobble_finished(self.guild, track, "finished")
        await _drain(cog)

        self.assertIsNone(cog._state(self.guild.id)["scrobble"])
        self.assertEqual(cog._lastfm_writer.scrobbles, [])


class ScrobbleOptInTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import aiosqlite
        from database import SQLitePool
        from utils.music.database import MusicDatabase, _TABLE_SQL

        self.db = MusicDatabase()
        self._previous = (self.db.pool, self.db._ready)
        self.conn = await aiosqlite.connect(":memory:")
        self.db.pool = SQLitePool(self.conn)
        self.db._ready = True
        for sql in _TABLE_SQL:
            await self.db.pool.execute(sql)

    async def asyncTearDown(self):
        await self.conn.close()
        self.db.pool, self.db._ready = self._previous

    async def test_scrobbling_is_off_until_the_member_opts_in(self):
        self.assertFalse(await self.db.scrobble_enabled(42))
        await self.db.set_scrobble_enabled(42, True)
        self.assertTrue(await self.db.scrobble_enabled(42))
        await self.db.set_scrobble_enabled(42, False)
        self.assertFalse(await self.db.scrobble_enabled(42))

    async def test_one_members_choice_does_not_change_anothers(self):
        await self.db.set_scrobble_enabled(42, True)
        self.assertTrue(await self.db.scrobble_enabled(42))
        self.assertFalse(await self.db.scrobble_enabled(43))


if __name__ == "__main__":
    unittest.main()
