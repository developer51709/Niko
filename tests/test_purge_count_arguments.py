"""Regression tests for count-only purge and clear command invocations."""

import asyncio
import inspect
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.moderation._msg_commands import MessagesMixin


class PurgeCountArgumentTests(unittest.TestCase):
    def test_clear_requires_count_then_accepts_optional_user(self):
        command = MessagesMixin.clear
        parameters = list(inspect.signature(command.callback).parameters.values())
        self.assertEqual([parameter.name for parameter in parameters[2:]], ["count", "user"])
        self.assertTrue(parameters[2].default.required)
        self.assertEqual(parameters[2].default.description, "How many recent messages to delete (1–1000).")
        self.assertFalse(parameters[3].default.required)
        self.assertIsNone(parameters[3].default.default)
        self.assertEqual(
            parameters[3].default.description,
            "Optionally limit deletion to this member's messages.",
        )

    def test_purge_is_an_alias_of_clear(self):
        self.assertIn("purge", MessagesMixin.clear.aliases)
        self.assertFalse(hasattr(MessagesMixin, "purge"))

    def test_count_only_invocation_uses_count_and_no_user(self):
        async def check():
            ctx = SimpleNamespace()
            cog = SimpleNamespace(_purge_messages=AsyncMock())

            # Direct callback calls bypass discord.py's argument parser, so
            # supply the optional converter result explicitly as None.
            await MessagesMixin.clear.callback(cog, ctx, 25, None)
            cog._purge_messages.assert_awaited_once_with(ctx, None, 25)

        asyncio.run(check())

    def test_count_and_user_invocation_preserves_argument_order(self):
        async def check():
            ctx = SimpleNamespace()
            user = object()
            cog = SimpleNamespace(_purge_messages=AsyncMock())

            await MessagesMixin.clear.callback(cog, ctx, 25, user)
            cog._purge_messages.assert_awaited_once_with(ctx, user, 25)

        asyncio.run(check())


if __name__ == "__main__":
    unittest.main()
