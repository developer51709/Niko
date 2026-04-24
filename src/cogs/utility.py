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

    @commands.command(name="echo")
    @commands.has_permissions(manage_messages=True)
    async def echo(self, ctx, *, message: str):
        """Echoes the user's message."""
        try:
            await ctx.send(f"{message}\n-# Sent by {ctx.author.mention}", allowed_mentions=discord.AllowedMentions.none())
        except discord.Forbidden:
            pass

    @commands.command(name="partnership_request")
    async def partnership_request(self, ctx, invite: str = None):
        """Send a partnership request to the bot admins."""
        requester = ctx.author
        log_channel = self.bot.get_channel(1462614744052797683)
        if not invite:
            await ctx.send("Please provide an invite link for your server. Example: `!partnership_request https://discord.gg/yourinvite`")
            return
        if log_channel:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### 🤝 Partnership Request\n**Requested by:** {requester.display_name}\n**Invite:** {invite}"
                )
            ))
            await log_channel.send(view=view)
            await ctx.send("Partnership request sent successfully!")
        else:
            await ctx.send("Error: Log channel not found.")


async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
