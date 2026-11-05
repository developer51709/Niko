import discord
from discord import app_commands
from discord.ext import commands
from config.emojis import get_emoji
from utils import logging as log
from utils.i18n import make_flat_msg
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

MESSAGES = load_locales("cogs.ai", "chat")

msg = make_flat_msg(MESSAGES)


def _cv(text: str, *, colour: discord.Colour | None = None) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    kwargs: dict = {}
    if colour:
        kwargs["accent_colour"] = colour
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text), **kwargs))
    return view


class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Right-click a message → Niko answers it. The menu belongs with the
        # rest of the chat surface, not with the bot's system plumbing.
        self._ask_menu = app_commands.ContextMenu(
            name="☕ Ask Niko",
            callback=self.ask_niko,
        )
        self.bot.tree.add_command(self._ask_menu)

    async def cog_unload(self):
        self.bot.tree.remove_command(self._ask_menu.name, type=self._ask_menu.type)

    # ── Context menu: Ask Niko ─────────────────────

    async def ask_niko(
        self,
        interaction: discord.Interaction,
        message: discord.Message,
    ) -> None:
        """Right-click a message → Niko responds to it."""
        await interaction.response.defer(ephemeral=True)

        content = message.content or msg(interaction, "ask_no_text")
        if len(content) > 500:
            content = content[:500] + "…"

        prompt = f'Someone shared this message with you:\n\n"{content}"\n\nWhat do you think?'

        # Share the same config, memory and sentinel handling as the normal AI
        # path, so this menu obeys the server's own settings.
        from utils.ai.config import load_config
        from utils.ai.error_views import build_ai_error_view, parse_ai_error
        from utils.ai.reply import generate_reply

        config = await load_config(interaction.guild.id) if interaction.guild else None
        reply = await generate_reply(
            self.bot,
            interaction.user.id,
            interaction.guild,
            prompt,
            interaction.user.display_name,
            config=config,
        )

        if isinstance(reply, str) and reply.startswith("ai_error:"):
            kind, cooldown = parse_ai_error(reply)
            await interaction.followup.send(
                view=build_ai_error_view(kind, cooldown),
                ephemeral=True,
            )
        elif reply == "ai_disabled_global":
            await interaction.followup.send(
                msg(interaction, "ai_disabled_global"), ephemeral=True
            )
        elif reply == "ai_disabled_guild":
            await interaction.followup.send(
                msg(interaction, "ai_disabled_guild"), ephemeral=True
            )
        elif isinstance(reply, str) and reply:
            await interaction.followup.send(
                view=_cv(
                    f"### ☕ {msg(interaction, 'ask_title')}\n{reply}",
                    colour=discord.Colour(0xc8a882),
                ),
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                view=_cv(
                    f"☕ {msg(interaction, 'ask_empty')}",
                    colour=discord.Colour(0xfee75c),
                ),
                ephemeral=True,
            )
        log.info("AI", f"Ask Niko reply requested by {interaction.user.id}")

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
