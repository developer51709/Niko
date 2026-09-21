import asyncio
import sys

import discord
from discord.ext import commands

sys.path.insert(0, "src")

from cogs.admin.staff import STAFF_ROLES, StaffCog  # noqa: E402


async def _check_staff_cog():
    bot = commands.Bot(command_prefix=".", intents=discord.Intents.none())
    await bot.add_cog(StaffCog(bot))
    root = bot.get_command("staff")
    assert root is not None
    assert root.hidden is True
    names = {command.name for command in root.commands}
    assert {"help", "manage", "ping", "latency", "dev01"} <= names
    assert "devhelp" not in names
    assert "ownerhelp" not in names
    assert len(names) == len(root.commands)
    assert all(command.hidden for command in root.commands)
    assert set(STAFF_ROLES) == {"head_admin", "moderator", "head_support", "support"}


if __name__ == "__main__":
    asyncio.run(_check_staff_cog())
    print("staff cog regression checks passed")
