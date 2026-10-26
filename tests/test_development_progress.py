"""Development instances must not write shared XP or message activity.

Production and beta can point at the same MongoDB database, so a development
instance that kept awarding XP or buffering message activity would overwrite
live levels and double-count the dashboard's daily totals.

Run with:  python -m pytest tests/test_development_progress.py -v
"""

import asyncio
import importlib
import os
import sys
import unittest
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import environment  # noqa: E402
from cogs.leveling.cog import Leveling  # noqa: E402
from cogs.system.server_stats import ServerStats  # noqa: E402


class ExplodingBot:
    """A database read or write in development is the failure being guarded."""

    @property
    def cxn(self):
        raise AssertionError("a development instance touched the shared database")


class RecordingCxn:
    """Capture writes so the production path can be asserted without a database."""

    def __init__(self):
        self.executed = []

    async def fetchrow(self, *args, **kwargs):
        return None

    async def fetchval(self, *args, **kwargs):
        return None

    async def fetch(self, *args, **kwargs):
        return []

    async def execute(self, sql, *args):
        self.executed.append((sql, args))


def message():
    return SimpleNamespace(
        author=SimpleNamespace(bot=False, id=7, display_name="tester"),
        guild=SimpleNamespace(id=1, name="guild"),
        channel=None,
        content="hello",
    )


def make_leveling(bot):
    cog = Leveling.__new__(Leveling)
    cog.bot = bot
    cog._cooldown_cache = {}
    return cog


def make_stats(bot):
    cog = ServerStats.__new__(ServerStats)
    cog.bot = bot
    cog.pending = defaultdict(lambda: {"messages": 0, "joins": 0, "leaves": 0})
    return cog


class DevelopmentProgressTests(unittest.TestCase):
    def tearDown(self):
        os.environ.pop("DEVELOPMENT", None)
        importlib.reload(environment)

    def test_development_message_awards_no_xp(self):
        cog = make_leveling(ExplodingBot())
        with patch("config.environment.DEVELOPMENT", True):
            asyncio.run(Leveling.on_message(cog, message()))

    def test_production_message_still_awards_xp(self):
        cxn = RecordingCxn()
        cog = make_leveling(SimpleNamespace(cxn=cxn))
        with patch("config.environment.DEVELOPMENT", False):
            asyncio.run(Leveling.on_message(cog, message()))
        self.assertTrue(
            any("INSERT OR REPLACE INTO levels" in sql for sql, _ in cxn.executed),
            cxn.executed,
        )

    def test_development_message_records_no_activity(self):
        cog = make_stats(ExplodingBot())
        with patch("config.environment.DEVELOPMENT", True):
            asyncio.run(ServerStats.on_message(cog, message()))
        self.assertEqual(dict(cog.pending), {})

    def test_production_message_buffers_activity(self):
        cog = make_stats(ExplodingBot())
        with patch("config.environment.DEVELOPMENT", False):
            asyncio.run(ServerStats.on_message(cog, message()))
        buckets = list(cog.pending.values())
        self.assertEqual(len(buckets), 1)
        self.assertEqual(buckets[0]["messages"], 1)


class DevelopmentFlagTests(unittest.TestCase):
    def tearDown(self):
        os.environ.pop("DEVELOPMENT", None)
        importlib.reload(environment)

    def test_true_values_enable_development(self):
        for value in ("1", "true", "yes", "on", "TRUE"):
            with self.subTest(value=value), patch.dict(os.environ, {"DEVELOPMENT": value}):
                self.assertTrue(importlib.reload(environment).DEVELOPMENT)

    def test_false_values_keep_production_behaviour(self):
        for value in ("", "0", "false", "no", "off"):
            with self.subTest(value=value), patch.dict(os.environ, {"DEVELOPMENT": value}):
                self.assertFalse(importlib.reload(environment).DEVELOPMENT)


if __name__ == "__main__":
    unittest.main()
