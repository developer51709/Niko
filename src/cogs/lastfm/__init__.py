"""Last.fm cog — /fm listening commands, cards and server boards."""

from discord.ext import commands

from .cog import LastfmCog


async def setup(bot: commands.Bot):
    await bot.add_cog(LastfmCog(bot))
