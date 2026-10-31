"""The bot owner can never be blacklisted.

Anti-abuse used to treat the owner like any other account: three strikes and
the account that runs the bot was blacklisted, which took the owner's own
dashboard and staff commands away from them. Recovering meant editing the
database by hand and restarting so the cached entry was dropped — with no way
back in while it lasted. These tests pin the exemption:

* the owner is never counted, struck or written to the blacklist,
* an entry that already targets the owner is cleared from the database and the
  cache the next time the cache loads, so no manual edit or restart is needed,
* a cache that still holds an owner entry cannot lock them out,
* everyone else is unaffected.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import database
from config.ids import OWNER_IDS, is_owner_id
from utils import abuse_detection
from utils.blacklist_manager import BlacklistManager

OWNER = next(iter(OWNER_IDS))
OTHER = 424242424242424242


def _row(user_id, reason="spam"):
    return {
        "id": user_id,
        "reason": reason,
        "timestamp": 1.0,
        "added_by": None,
        "expires_at": None,
        "status": "active",
    }


class _Pool:
    """Records the SQL a fake pool is asked to run."""

    def __init__(self, user_rows=(), guild_rows=()):
        self.user_rows = list(user_rows)
        self.guild_rows = list(guild_rows)
        self.statements = []

    async def execute(self, sql, *args):
        self.statements.append((" ".join(sql.split()), args))

    async def fetch(self, sql, *args):
        self.statements.append((" ".join(sql.split()), args))
        if "blacklist_users" in sql:
            return list(self.user_rows)
        if "blacklist_guilds" in sql:
            return list(self.guild_rows)
        return []

    async def fetchrow(self, sql, *args):
        self.statements.append((" ".join(sql.split()), args))
        return None

    def ran(self, fragment):
        return [args for sql, args in self.statements if fragment in sql]


class OwnerExemptionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._previous_pool = database._shared_pool
        self._previous_manager = BlacklistManager._instance
        BlacklistManager._instance = None
        abuse_detection._requests.clear()
        self.addCleanup(self._restore)

    def _restore(self):
        database._shared_pool = self._previous_pool
        BlacklistManager._instance = self._previous_manager
        abuse_detection._requests.clear()

    def _install(self, pool):
        database._shared_pool = pool
        BlacklistManager._instance = None
        return pool

    async def test_the_owner_is_never_counted_by_anti_abuse(self):
        pool = self._install(_Pool())

        for _ in range(20):
            result = await abuse_detection.record_request(OWNER, reason="spamming commands")

        self.assertFalse(result["abuse"])
        self.assertFalse(result["blacklisted"])
        self.assertEqual(pool.statements, [], "the owner path must not touch the database")
        self.assertNotIn(OWNER, abuse_detection._requests)

    async def test_the_owner_cannot_be_added_to_the_blacklist(self):
        pool = self._install(_Pool())
        manager = BlacklistManager()

        self.assertFalse(await manager.add_user(OWNER, reason="test", added_by=OWNER))
        self.assertEqual(pool.ran("INSERT INTO blacklist_users"), [])
        self.assertIsNone(manager.get_user_entry(OWNER))
        self.assertFalse(manager.is_user_blacklisted(OWNER))

    async def test_an_owner_strike_is_skipped(self):
        pool = self._install(_Pool())

        result = await BlacklistManager().register_abuse_strike(OWNER, reason="spamming")

        self.assertEqual(result, {"strikes": 0, "blacklisted": False,
                                  "permanent": False, "expires_at": None})
        self.assertEqual(pool.ran("abuse_strikes"), [])
        self.assertEqual(pool.ran("INSERT INTO blacklist_users"), [])

    async def test_an_existing_owner_row_is_cleared_when_the_cache_loads(self):
        pool = self._install(_Pool(
            user_rows=[_row(OWNER, "Automated anti-abuse: spamming commands (strike 3/3)."),
                       _row(OTHER)],
        ))
        manager = BlacklistManager()

        await manager.load()

        self.assertIsNone(manager.get_user_entry(OWNER))
        self.assertIsNotNone(manager.get_user_entry(OTHER))
        self.assertIn((OWNER,), pool.ran("DELETE FROM blacklist_users"))
        self.assertNotIn((OTHER,), pool.ran("DELETE FROM blacklist_users"))

    async def test_existing_owner_strikes_are_cleared_too(self):
        pool = self._install(_Pool())

        await BlacklistManager().load()

        self.assertIn((OWNER,), pool.ran("DELETE FROM abuse_strikes"))

    async def test_a_cached_owner_entry_cannot_lock_them_out(self):
        self._install(_Pool())
        manager = BlacklistManager()
        manager.blacklist["users"] = [_row(OWNER, "stale")]

        self.assertIsNone(manager.get_user_entry(OWNER))
        self.assertFalse(manager.is_user_blacklisted(OWNER))

    async def test_everyone_else_still_gets_struck(self):
        self._install(_Pool())

        with patch.object(abuse_detection, "MAX_REQUESTS_PER_WINDOW", 2):
            results = [
                await abuse_detection.record_request(OTHER, reason="spamming commands")
                for _ in range(3)
            ]

        self.assertFalse(results[0]["abuse"])
        self.assertTrue(results[-1]["abuse"])
        self.assertTrue(results[-1]["blacklisted"])
        self.assertEqual(results[-1]["strikes"], 1)

    def test_the_helper_matches_the_configured_owners(self):
        self.assertTrue(is_owner_id(OWNER))
        self.assertTrue(is_owner_id(str(OWNER)))
        self.assertFalse(is_owner_id(OTHER))
        self.assertFalse(is_owner_id(None))


if __name__ == "__main__":
    unittest.main()
