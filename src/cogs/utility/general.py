import discord
from discord.ext import commands
from config.emojis import get_emoji


class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Check the bot's latency")
    async def ping(self, ctx):
        """Check the bot's latency."""
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### 🏓 Pong!"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"**Latency:** {round(self.bot.latency * 1000)}ms"
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    @commands.hybrid_command(
        name="echo",
        description="Echoes the user's message"
    )
    @commands.has_permissions(manage_messages=True)
    async def echo(self, ctx, *, message: str):
        """Echoes the user's message."""
        MAX_LEN = 1950

        if len(message) > MAX_LEN:
            await ctx.send(
                f"{message[:MAX_LEN]}...\n-# Sent by {ctx.author.mention}",
                allowed_mentions=discord.AllowedMentions.none()
            )
        else:
            await ctx.send(
                f"{message}\n-# Sent by {ctx.author.mention}",
                allowed_mentions=discord.AllowedMentions.none()
            )


async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
