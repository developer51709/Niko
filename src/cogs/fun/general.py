import discord
from discord.ext import commands
import random

from config.links import WEBSITE

# Nitro gift prank — the thumbnail on the gift card and the rickroll in the
# ephemeral "accept" response.
NITRO_GIF_URL = "https://c.tenor.com/ARL3mp1NaXYAAAAd/tenor.gif"
RICKROLL_GIF_URL = f"{WEBSITE}/assets/rick.gif"


class NitroAcceptButton(discord.ui.DynamicItem[discord.ui.Button], template=r"isitnitro"):
    """Persistent ``Accept`` button on the nitro gift card.

    The custom id is static, so registering this DynamicItem at startup keeps
    the button working on every gift card — including ones sent before a
    restart. Clicking it answers with the (very honest) rickroll.
    """

    def __init__(self) -> None:
        super().__init__(discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Accept",
            custom_id="isitnitro",
        ))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls()

    async def callback(self, interaction: discord.Interaction) -> None:
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="## No nitro here!"),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(media=RICKROLL_GIF_URL),
            ),
        ))
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(view=view, ephemeral=True)


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

        # Persistent isitnitro button — survives restarts (static custom id).
        bot.add_dynamic_items(NitroAcceptButton)

    async def cog_unload(self) -> None:
        self.bot.remove_dynamic_items(NitroAcceptButton)

    @commands.hybrid_command(name="nitro", description="Free Nitro!!!", help="{ 'en': 'free nitro!!! 🎁', 'de': 'kostenloses Nitro!!! 🎁', 'es': '¡¡¡nitro gratis!!! 🎁' }")
    async def nitro(self, ctx):
        """FREE NITRO!!!"""
        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(content="## A WILD GIFT APPEARS!\n\n**Nitro**\nExpires in 47 hours"),
                accessory=discord.ui.Thumbnail(
                    media=NITRO_GIF_URL,
                ),
            ),
            discord.ui.ActionRow(
                NitroAcceptButton(),
            ),
        )
        view = discord.ui.LayoutView()
        view.add_item(container)
        await ctx.send(view=view)

    @commands.hybrid_command(name="boring", description="A boring command", help="{ 'en': 'a boring command 😴', 'de': 'ein langweiliger Befehl 😴', 'es': 'un comando aburrido 😴' }")
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

    @commands.hybrid_command(name="notboring", description="A not boring command", help="{ 'en': 'a not boring command 🎉', 'de': 'ein nicht langweiliger Befehl 🎉', 'es': 'un comando no aburrido 🎉' }")
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

    @commands.hybrid_command(name="crazy", description="Crazy? I was crazy once...", help="{ 'en': 'crazy? I was crazy once... 🤪', 'de': 'verrückt? Ich war mal verrückt... 🤪', 'es': '¿loco? estuve loco una vez... 🤪' }")
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