"""Birthday commands that need a server must reject DMs cleanly.

`birthday config` used to dereference `ctx.guild.id` in a DM and report an
`AttributeError`. The guild-bound subcommands now carry the normal guild-only
check, so discord.py raises `NoPrivateMessage` and the shared error handler
answers with the server-only notice.
"""

import asyncio
from pathlib import Path
import sys
from types import SimpleNamespace

from discord.ext import commands

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.social.birthdays import Birthdays  # noqa: E402


SERVER_COMMANDS = (
    "birthday_today",
    "birthday_upcoming",
    "birthday_channel",
    "birthday_role",
    "birthday_config",
)
PERSONAL_COMMANDS = ("birthday_set", "birthday_remove", "birthday_show")


def _prefix_checks_reject_dm(command) -> bool:
    """Whether a prefix invocation with no guild is stopped by a check."""
    ctx = SimpleNamespace(guild=None, author=SimpleNamespace(), channel=SimpleNamespace())

    async def run() -> bool:
        for check in command.checks:
            try:
                await check(ctx)
            except commands.NoPrivateMessage:
                return True
            except Exception:
                continue
        return False

    return asyncio.run(run())


def test_server_only_birthday_commands_are_guild_only():
    for name in SERVER_COMMANDS:
        command = getattr(Birthdays, name)
        assert command.with_app_command, name
        assert command.app_command.guild_only, name
        assert _prefix_checks_reject_dm(command), name


def test_personal_birthday_commands_still_work_in_dms():
    for name in PERSONAL_COMMANDS:
        command = getattr(Birthdays, name)
        assert command.with_app_command, name
        assert not command.app_command.guild_only, name
        assert not _prefix_checks_reject_dm(command), name
