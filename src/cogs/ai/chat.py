import discord
from discord.ext import commands
from config.emojis import get_emoji
from utils.i18n import make_flat_msg
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

MESSAGES = load_locales("cogs.ai", "chat")

msg = make_flat_msg(MESSAGES)


class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="memory", help=CMDS.help("memory"),
    )
    async def memory(self, ctx, member: discord.Member = None):
        """Display this server's memory content for a user."""
        from utils.ai.memory import get_memory_text

        if ctx.guild is None:
            return await ctx.send(msg(ctx, "guild_only"))

        target = member or ctx.author
        mem = await get_memory_text(ctx.guild.id, target.id)
        if not mem:
            return await ctx.send(msg(ctx, "no_memory", name=target.display_name))

        mem = mem[-3000:]
        title = msg(ctx, "memory_title", name=target.display_name)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {title}\n```\n{mem}\n```")
        ))
        await ctx.send(view=view)

    @commands.hybrid_command(
        name="clearhistory",
        description=CMDS.text("clearhistory.description"),
        aliases=["clearchat", "resetmemory"],
        help=CMDS.help("clearhistory"))
    async def clearhistory(self, ctx: commands.Context):
        """Wipe your own short-term history and memory with Niko in this server."""
        from utils.ai.memory import clear_user, has_memory

        if ctx.guild is None:
            return await ctx.send(msg(ctx, "guild_only"), ephemeral=True)

        if not await has_memory(ctx.guild.id, ctx.author.id):
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=msg(ctx, "history_empty")),
            ))
            return await ctx.send(view=view, ephemeral=True)

        await clear_user(ctx.guild.id, ctx.author.id)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"{get_emoji('tick')} {msg(ctx, 'history_cleared')}"),
        ))
        await ctx.send(view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(AICog(bot))
