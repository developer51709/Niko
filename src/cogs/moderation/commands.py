"""
Moderation cog — composes all moderation command mixins.
"""
from discord.ext import commands
from ._members import MembersMixin
from ._msg_commands import MessagesMixin
from ._channels import ChannelsMixin
from ._settings import SettingsMixin


class Moderation(MembersMixin, MessagesMixin, ChannelsMixin, SettingsMixin, commands.Cog):
    """Staff-facing moderation commands."""

    def __init__(self, bot):
        self.bot = bot

    def utils(self):
        return self.bot.get_cog("ModerationUtils")

    def logger(self):
        return self.bot.get_cog("ServerLogger")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
