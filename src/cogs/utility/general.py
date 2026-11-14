import discord
from discord.ext import commands
from config.emojis import get_emoji

from cogs.utility.echo import EchoReporter
from utils.command_locales import command_texts
from utils.i18n import make_flat_msg
from utils.locales import load_locales

CMDS = command_texts(__package__)
MESSAGES = load_locales(__package__, "misc")
msg = make_flat_msg(MESSAGES, {"pingpong": get_emoji("pingpong")})


class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.echo_reporter = EchoReporter(bot)

    @commands.hybrid_command(name="ping", description=CMDS.text("ping.description"))
    async def ping(self, ctx):
        """Check the bot's latency."""
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "pong")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=msg(ctx, "latency", ms=round(self.bot.latency * 1000))
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    @commands.hybrid_command(
        name="echo",
        description=CMDS.text("echo.description"),
        help=CMDS.help("echo"),
    )
    @commands.has_permissions(manage_messages=True)
    async def echo(self, ctx, *, message: str):
        """Echoes the user's message."""
        await self.echo_reporter.send(ctx, message)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        await self.echo_reporter.on_interaction(interaction)


async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
