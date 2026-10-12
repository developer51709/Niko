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
    def test_count_is_first_optional_argument_for_prefix_commands(self):
        for name in ("purge", "clear"):
            with self.subTest(command=name):
                parameters = list(inspect.signature(getattr(MessagesMixin, name).callback).parameters)
                self.assertEqual(parameters[2:], ["amount", "member"])

    def test_count_only_invocation_does_not_bind_count_as_member(self):
        async def check():
            ctx = SimpleNamespace()
            cog = SimpleNamespace(_purge_messages=AsyncMock())

            for name in ("purge", "clear"):
                with self.subTest(command=name):
                    command = getattr(MessagesMixin, name)
                    await command.callback(cog, ctx, 25)
                    cog._purge_messages.assert_awaited_with(ctx, None, 25)
                    cog._purge_messages.reset_mock()

        asyncio.run(check())


if __name__ == "__main__":
    unittest.main()
