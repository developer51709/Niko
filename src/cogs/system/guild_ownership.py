"""Record which member owned each server when Niko was present or removed.

Deletion requests for a server must remain possible after Niko has left it, but
only for the member who was the owner at the time. Discord no longer exposes a
guild object after removal, so the owner is captured here while the bot can
still see it.
"""

import discord
from discord.ext import commands

from utils import logging
from utils.data_removal import record_ownership


class GuildOwnership(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _record(self, guild: discord.Guild, *, removed: bool) -> None:
        pool = getattr(self.bot, "cxn", None)
        if pool is None:
            return
        icon_url = str(guild.icon.url) if guild.icon else None
        try:
            await record_ownership(
                pool, guild.id, guild.owner_id, guild.name, icon_url, removed=removed
            )
        except Exception as exc:
            logging.warning("GuildOwnership", f"Could not record {guild.id}: {exc}")

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self._record(guild, removed=False)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self._record(guild, removed=False)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        await self._record(guild, removed=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(GuildOwnership(bot))
