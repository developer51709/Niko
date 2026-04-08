# this cog will allow server admins to configure the AI settings for their server

import discord
from discord.ext import commands
from config.emojis import get_emoji


class AIConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ai_config(self, ctx: commands.Context):
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_settings')} AI Configuration"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="This feature is currently under development. Please feel free to check back later for updates or send some suggestions in the support server."
            )
        )
        view.add_item(container)
        await ctx.send(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(AIConfig(bot))