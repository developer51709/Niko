"""DJ role: stored per guild, enforced on commands and the now-playing panel.

The role is playback policy, so it lives in the dedicated music database. A
guild without one keeps the old behaviour: every member may control playback.
"""

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.music.cog import MusicSystem  # noqa: E402
from utils.music.database import MusicDatabase, _TABLE_SQL  # noqa: E402

GUILD_ID = 9001
DJ_ROLE_ID = 4242


def _member(*, role_ids=(), manage_guild=False, administrator=False):
    return SimpleNamespace(
        guild=SimpleNamespace(id=GUILD_ID),
        roles=[SimpleNamespace(id=role_id) for role_id in role_ids],
        guild_permissions=SimpleNamespace(
            manage_guild=manage_guild,
            administrator=administrator,
        ),
    )


def _cog(role_id=None):
    cog = object.__new__(MusicSystem)
    cog.bot = SimpleNamespace()
    cog._guild_states = {}
    cog._dj_roles = {GUILD_ID: role_id}
    return cog


class DjRoleDatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import aiosqlite
        from database import SQLitePool

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

    async def test_a_guild_without_a_role_stores_nothing(self):
        self.assertIsNone(await self.db.get_dj_role(GUILD_ID))

    async def test_a_role_round_trips_and_can_be_replaced(self):
        await self.db.set_dj_role(GUILD_ID, DJ_ROLE_ID)
        self.assertEqual(await self.db.get_dj_role(GUILD_ID), DJ_ROLE_ID)

        await self.db.set_dj_role(GUILD_ID, 5555)
        self.assertEqual(await self.db.get_dj_role(GUILD_ID), 5555)
        self.assertEqual(await self.db.pool.fetchval(
            "SELECT COUNT(*) FROM music_dj_roles WHERE guild_id = $1", GUILD_ID,
        ), 1)

    async def test_clearing_opens_controls_again(self):
        await self.db.set_dj_role(GUILD_ID, DJ_ROLE_ID)
        await self.db.clear_dj_role(GUILD_ID)
        self.assertIsNone(await self.db.get_dj_role(GUILD_ID))


class DjPermissionTests(unittest.IsolatedAsyncioTestCase):
    async def test_without_a_dj_role_everyone_may_control(self):
        cog = _cog(role_id=None)
        self.assertTrue(await cog.is_dj(_member()))

    async def test_the_dj_role_holder_may_control(self):
        cog = _cog(DJ_ROLE_ID)
        self.assertTrue(await cog.is_dj(_member(role_ids=[DJ_ROLE_ID])))

    async def test_managers_keep_control_even_without_the_role(self):
        cog = _cog(DJ_ROLE_ID)
        self.assertTrue(await cog.is_dj(_member(manage_guild=True)))
        self.assertTrue(await cog.is_dj(_member(administrator=True)))

    async def test_an_unrelated_member_is_refused(self):
        cog = _cog(DJ_ROLE_ID)
        self.assertFalse(await cog.is_dj(_member(role_ids=[9999])))

    async def test_the_dj_role_is_read_once_and_cached(self):
        cog = object.__new__(MusicSystem)
        cog.bot = SimpleNamespace()
        cog._dj_roles = {}
        db = SimpleNamespace(
            ensure=AsyncMock(),
            get_dj_role=AsyncMock(return_value=DJ_ROLE_ID),
        )
        music_cog_module = sys.modules["cogs.music.cog"]
        previous = music_cog_module.MusicDatabase
        music_cog_module.MusicDatabase = lambda: db
        try:
            self.assertEqual(await cog._dj_role(GUILD_ID), DJ_ROLE_ID)
            self.assertEqual(await cog._dj_role(GUILD_ID), DJ_ROLE_ID)
        finally:
            music_cog_module.MusicDatabase = previous
        db.get_dj_role.assert_awaited_once_with(GUILD_ID)


class DjGateTests(unittest.IsolatedAsyncioTestCase):
    async def test_a_refused_command_says_why_and_does_nothing_else(self):
        cog = _cog(DJ_ROLE_ID)
        cog._require_dj = AsyncMock(return_value=False)
        ctx = SimpleNamespace(send=AsyncMock())
        # ``skip`` is a Command descriptor, so run the callback itself.
        await cog.skip.callback(cog, ctx)
        cog._require_dj.assert_awaited_once()
        ctx.send.assert_not_awaited()

    async def test_the_require_helper_sends_the_refusal(self):
        cog = _cog(DJ_ROLE_ID)
        ctx = SimpleNamespace(
            author=_member(),
            send=AsyncMock(),
        )
        self.assertFalse(await cog._require_dj(ctx))
        sent = ctx.send.await_args.args[0]
        self.assertIn("DJ role", sent)

    async def test_a_panel_press_is_refused_ephemerally(self):
        cog = _cog(DJ_ROLE_ID)
        interaction = SimpleNamespace(
            user=_member(role_ids=[9999]),
            response=SimpleNamespace(send_message=AsyncMock()),
        )
        self.assertFalse(await cog.panel_allowed(interaction))
        interaction.response.send_message.assert_awaited_once()
        self.assertTrue(interaction.response.send_message.await_args.kwargs.get("ephemeral"))

    async def test_a_dj_panel_press_is_allowed_silently(self):
        cog = _cog(DJ_ROLE_ID)
        interaction = SimpleNamespace(
            user=_member(role_ids=[DJ_ROLE_ID]),
            response=SimpleNamespace(send_message=AsyncMock()),
        )
        self.assertTrue(await cog.panel_allowed(interaction))
        interaction.response.send_message.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
