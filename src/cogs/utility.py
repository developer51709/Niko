import discord
from discord.ext import commands


class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Pong!"""
        await ctx.send("Pong!")

    @commands.command(name="echo")
    async def echo(self, ctx, *, message: str):
        """Echoes the user's message."""
        await ctx.send(f"{message}\n-# Sent by {ctx.author.display_name}")

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
