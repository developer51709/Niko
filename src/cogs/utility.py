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

    
    @commands.command(name="nitro")
    async def nitro(self, ctx):
        """FREE NITRO!!!"""
        rickroll_gif = "https://csyn.me/assets/rickroll.gif"
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content="### No nitro here! ☕"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(media=rickroll_gif)
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

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

    @commands.command(name="boring")
    async def boring(self, ctx):
        """A boring command."""
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### ☕ What did you expect?"
            ),
            discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"I bet you thought this command would do something cool, but no. It's just boring. 😔"
            ),
            discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"-# Maybe try `{self.bot.command_prefix}notboring`?"
            )
        ))
        await ctx.send(view=view)

    @commands.command(name="notboring")
    async def notboring(self, ctx):
        """A not boring command."""
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content="### ☕ I lied."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"This command is actually in fact quite boring."
            ),
            discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"-# Please forgive me 😭"
            )
        ))
        await ctx.send(view=view)

    @commands.command(name="crazy")
    async def crazy(self, ctx):
        """Crazy? I was crazy once..."""
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    "### ☕ Crazy?\n"
                    "Crazy? I was crazy once. They locked me in a room. A rubber room. "
                    "A rubber room with rats. And rats make me crazy.\n\n"
                    "Crazy? I was crazy once. They locked me in a room. A rubber room. "
                    "A rubber room with rats. And rats make me crazy.\n\n"
                    "Crazy? I was crazy once..."
                )
            )
        ))
        await ctx.send(view=view)


async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
