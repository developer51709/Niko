"""Prefix resolution for command help text.

The bot's ``command_prefix`` is :func:`utils.prefix_manager.dynamic_prefix`, an
async callable that reads the guild's configured prefixes. Cog help text used
to call it without awaiting, so every page fell back to ``!``/``.`` and the
dropped coroutine warned on collection:

    RuntimeWarning: coroutine 'dynamic_prefix' was never awaited

``utils.prefix_manager.resolve_prefix`` now owns that logic, and each cog's
``_resolve_prefix`` delegates to it. These tests pin the behaviour: a guild
prefix reaches the help text, sync and async prefix callables both work, and
nothing is left un-awaited.

Run with:  python -m pytest tests/test_prefix_resolution.py -v
"""

import asyncio
import gc
import importlib
import json
import os
import sys
import unittest
import warnings
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils import prefix_manager  # noqa: E402
from utils.prefix_manager import (  # noqa: E402
    DEFAULT_PREFIXES,
    FALLBACK_PREFIX,
    dynamic_prefix,
    resolve_prefix,
)

GUILD_ID = 424242

# Every cog module with a help-text prefix helper. Each one must agree on the
# guild's prefix, not a hard-coded fallback.
COG_MODULES = [
    "cogs.admin.emoji",
    "cogs.casino.blackjack",
    "cogs.casino.slots",
    "cogs.economy.data",
    "cogs.fun.general",
    "cogs.help.views",
    "cogs.onboarding.views",
    "cogs.social.pfps",
    "cogs.staff.development",
    "cogs.staff.owner",
    "cogs.system.introduction",
]


class PrefixPool:
    """A prefix_config table holding one row for the test guild."""

    def __init__(self, prefixes):
        self.prefixes = prefixes
        self.queries = []
        self.writes = []

    async def fetchrow(self, sql, *values):
        self.queries.append((sql, values))
        guild_id = values[0]
        if guild_id != GUILD_ID:
            return None
        stored = self.prefixes if isinstance(self.prefixes, str) else json.dumps(self.prefixes)
        return {"prefixes": stored}

    async def execute(self, sql, *values):
        self.writes.append((sql, values))


def bot_with(command_prefix, pool=None):
    return SimpleNamespace(command_prefix=command_prefix, cxn=pool)


def ctx_for(guild_id=GUILD_ID):
    """A message context from the guild."""
    return SimpleNamespace(
        guild=SimpleNamespace(id=guild_id),
        message=SimpleNamespace(guild=SimpleNamespace(id=guild_id)),
    )


def resolve(command_prefix, target=None, pool=None):
    return asyncio.run(resolve_prefix(bot_with(command_prefix, pool), target or ctx_for()))


def unawaited_warnings(coro_factory):
    """The RuntimeWarnings left behind by running ``coro_factory``."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        coro_factory()
        # A dropped coroutine only warns when it is collected.
        gc.collect()
    return [str(item.message) for item in caught if "was never awaited" in str(item.message)]


class DynamicPrefixTest(unittest.TestCase):
    def setUp(self):
        self.pool = PrefixPool(["&", "?"])
        self.bot = bot_with(dynamic_prefix, self.pool)

    def test_guild_prefix_is_resolved_and_awaited(self):
        prefix = asyncio.run(resolve_prefix(self.bot, ctx_for()))
        self.assertEqual(prefix, "&")
        self.assertEqual(self.pool.queries[0][1], (GUILD_ID,))

    def test_no_coroutine_is_left_unawaited(self):
        self.assertEqual(
            unawaited_warnings(lambda: asyncio.run(resolve_prefix(self.bot, ctx_for()))),
            [],
        )

    def test_stored_prefixes_are_accepted_as_json_text_or_list(self):
        for stored in (["&", "?"], json.dumps(["&", "?"])):
            self.assertEqual(
                asyncio.run(resolve_prefix(bot_with(dynamic_prefix, PrefixPool(stored)), ctx_for())),
                "&",
            )

    def test_guild_passed_straight_in_resolves_its_prefix(self):
        """``on_guild_join`` hands over the guild, not a message."""
        prefix = asyncio.run(
            resolve_prefix(self.bot, SimpleNamespace(id=GUILD_ID, guild=None, members=[]))
        )
        self.assertEqual(prefix, "&")

    def test_dm_falls_back_to_the_default_prefix(self):
        dm = SimpleNamespace(guild=None, message=SimpleNamespace(guild=None))
        self.assertEqual(asyncio.run(resolve_prefix(self.bot, dm)), DEFAULT_PREFIXES[0])

    def test_unreadable_target_falls_back(self):
        self.assertEqual(asyncio.run(resolve_prefix(self.bot, SimpleNamespace())), FALLBACK_PREFIX)


class DevelopmentDefaultPrefixTests(unittest.TestCase):
    def tearDown(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DEVELOPMENT", None)
            importlib.reload(prefix_manager)

    def test_development_uses_bang_for_unspecified_guild_and_dm_prefixes(self):
        with patch.dict(os.environ, {"DEVELOPMENT": "true"}):
            config = importlib.reload(prefix_manager)
            self.assertEqual(config.DEFAULT_PREFIXES, ["!"])
            self.assertEqual(config.FALLBACK_PREFIX, "!")
            self.assertEqual(
                asyncio.run(config.dynamic_prefix(bot_with(config.dynamic_prefix), SimpleNamespace(guild=None))),
                ["!"],
            )
            self.assertEqual(
                asyncio.run(config.dynamic_prefix(
                    bot_with(config.dynamic_prefix),
                    SimpleNamespace(guild=SimpleNamespace(id=GUILD_ID)),
                )),
                ["!"],
            )

    def test_production_default_remains_period(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DEVELOPMENT", None)
            config = importlib.reload(prefix_manager)
        self.assertEqual(config.DEFAULT_PREFIXES, ["."])
        self.assertEqual(config.FALLBACK_PREFIX, ".")

class PrefixOverrideWriteGuardTest(unittest.TestCase):
    """A beta/COMMAND_PREFIX run must never write prefixes to the database."""

    def setUp(self):
        self.env = patch.dict(os.environ, {"DEVELOPMENT": "true"})
        self.env.start()
        self.config = importlib.reload(prefix_manager)
        self.pool = PrefixPool([".", "?"])

    def tearDown(self):
        self.env.stop()
        os.environ.pop("DEVELOPMENT", None)
        importlib.reload(prefix_manager)

    def test_override_is_what_commands_use(self):
        self.assertEqual(self.config.PREFIX_OVERRIDE, "!")
        self.assertEqual(
            asyncio.run(self.config.get_prefixes(GUILD_ID, self.pool)), ["!"]
        )

    def test_every_write_path_is_a_no_op(self):
        calls = (
            ("set", lambda: self.config.set_prefixes(GUILD_ID, ["!"], self.pool)),
            ("add", lambda: self.config.add_prefix(GUILD_ID, "!", self.pool)),
            ("remove", lambda: self.config.remove_prefix(GUILD_ID, ".", self.pool)),
            ("reset", lambda: self.config.reset_prefixes(GUILD_ID, self.pool)),
        )
        for name, call in calls:
            with self.subTest(call=name):
                self.assertEqual(asyncio.run(call()), ["!"])
        self.assertEqual(self.pool.writes, [])
        self.assertEqual(self.pool.prefixes, [".", "?"])


class PrefixStoreTest(unittest.TestCase):
    """Without an override the stored prefixes are still written normally."""

    def tearDown(self):
        importlib.reload(prefix_manager)

    def test_production_still_writes_prefixes(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DEVELOPMENT", None)
            config = importlib.reload(prefix_manager)
        self.assertEqual(config.PREFIX_OVERRIDE, "")
        pool = PrefixPool([])
        self.assertEqual(
            asyncio.run(config.set_prefixes(GUILD_ID, ["!", "?"], pool)), ["!", "?"]
        )
        self.assertEqual(len(pool.writes), 1)


class StaticPrefixTest(unittest.TestCase):
    def test_string_prefix(self):
        self.assertEqual(resolve("?"), "?")

    def test_list_prefix(self):
        self.assertEqual(resolve([">", "?"]), ">")

    def test_empty_list_falls_back(self):
        self.assertEqual(resolve([]), FALLBACK_PREFIX)

    def test_missing_prefix_falls_back(self):
        bot = SimpleNamespace(cxn=None)
        self.assertEqual(asyncio.run(resolve_prefix(bot, ctx_for())), FALLBACK_PREFIX)


class PrefixCallableTest(unittest.TestCase):
    def test_sync_callable(self):
        self.assertEqual(resolve(lambda bot, message: [">"]), ">")

    def test_sync_callable_returning_a_string(self):
        self.assertEqual(resolve(lambda bot, message: ">"), ">")

    def test_async_callable_is_awaited(self):
        async def prefix(_bot, _message):
            return ["~"]

        self.assertEqual(resolve(prefix), "~")

    def test_raising_callable_falls_back(self):
        def broken(_bot, _message):
            raise RuntimeError("no prefix table")

        self.assertEqual(resolve(broken), FALLBACK_PREFIX)


class CogHelperTest(unittest.TestCase):
    """Every cog helper must show the guild's prefix, not a hard-coded one."""

    def test_helpers_resolve_the_guild_prefix(self):
        pool = PrefixPool(["&"])
        bot = bot_with(dynamic_prefix, pool)
        for name in COG_MODULES:
            with self.subTest(cog=name):
                module = importlib.import_module(name)
                helper = getattr(module, "_resolve_prefix")
                self.assertEqual(asyncio.run(helper(bot, ctx_for())), "&")

    def test_helpers_leave_no_coroutine_unawaited(self):
        bot = bot_with(dynamic_prefix, PrefixPool(["&"]))
        for name in COG_MODULES:
            with self.subTest(cog=name):
                module = importlib.import_module(name)
                helper = getattr(module, "_resolve_prefix")

                def run(helper=helper):
                    asyncio.run(helper(bot, ctx_for()))

                self.assertEqual(unawaited_warnings(run), [])

    def test_helpers_accept_an_interaction(self):
        bot = bot_with(dynamic_prefix, PrefixPool(["&"]))
        interaction = SimpleNamespace(
            guild=SimpleNamespace(id=GUILD_ID),
            message=SimpleNamespace(guild=SimpleNamespace(id=GUILD_ID)),
        )
        module = importlib.import_module("cogs.casino.slots")
        self.assertEqual(asyncio.run(module._resolve_prefix(bot, interaction)), "&")

    def test_slots_help_shows_the_guild_prefix(self):
        """The reported warning came from the slots help page."""
        module = importlib.import_module("cogs.casino.slots")
        bot = bot_with(dynamic_prefix, PrefixPool(["&"]))
        self.assertEqual(asyncio.run(module._resolve_prefix(bot, ctx_for())), "&")

    def test_notifier_panel_shows_the_guild_prefix(self):
        """The setup panel's follow instructions use the same resolver."""
        module = importlib.import_module("cogs.notifier.cog")
        bot = bot_with(dynamic_prefix, PrefixPool(["&"]))
        captured = {}

        def build(guild, channel, follows, prefix="."):
            captured["prefix"] = prefix
            return object()

        ctx = SimpleNamespace(guild=SimpleNamespace(id=GUILD_ID), channel=object(), send=AsyncMock())
        cog = SimpleNamespace(bot=bot, cxn=None)
        with patch.object(module, "list_follows", AsyncMock(return_value=[])), patch.object(
            module, "build_setup_view", build
        ):
            asyncio.run(module.Notifier.notifier.callback(cog, ctx))
        self.assertEqual(captured["prefix"], "&")


if __name__ == "__main__":
    unittest.main()
