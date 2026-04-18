import discord
from discord.ext import commands
import random


async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """
    Resolve the primary prefix for the current context/interaction.

    Supports:
    - Static string prefix
    - Static list/tuple of prefixes
    - Dynamic prefix function: command_prefix(bot, message) -> list[str]
    """
    raw = bot.command_prefix

    # Static prefix (string)
    if isinstance(raw, str):
        return raw

    # Static list/tuple of prefixes
    if isinstance(raw, (list, tuple)):
        return raw[0]

    # Dynamic prefix function
    try:
        # Context: has .message
        msg = getattr(ctx_or_interaction, "message", None)

        # Interaction: use the original message if present
        if msg is None and isinstance(ctx_or_interaction, discord.Interaction):
            msg = ctx_or_interaction.message

        if msg is None:
            return "!"

        prefixes = raw(bot, msg)
        if isinstance(prefixes, (list, tuple)) and prefixes:
            return prefixes[0]
    except Exception:
        pass

    # Fallback prefix if everything else fails
    return "."


class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(name="boring")
    async def boring(self, ctx):
        """A boring command."""
        prefix = await _resolve_prefix(self.bot, ctx)
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
                content=f"-# Maybe try `{prefix}notboring`?"
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
    await bot.add_cog(FunCog(bot))