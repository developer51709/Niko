import discord
from discord.ext import commands
import random

from config.links import WEBSITE
from utils.prefix_manager import resolve_prefix

from utils.command_locales import command_texts
from utils.i18n import make_flat_msg
from utils.locales import load_locales

CMDS = command_texts(__package__)
MESSAGES = load_locales(__package__, "general")
msg = make_flat_msg(MESSAGES)

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

    def __init__(self, label: str | None = None) -> None:
        super().__init__(discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label=label or msg("en", "nitro_accept"),
            custom_id="isitnitro",
        ))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls()

    async def callback(self, interaction: discord.Interaction) -> None:
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(interaction, "nitro_none")),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(media=RICKROLL_GIF_URL),
            ),
        ))
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(view=view, ephemeral=True)


async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """Return the primary prefix for this context, honouring a dynamic prefix."""
    return await resolve_prefix(bot, ctx_or_interaction)


class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Persistent isitnitro button — survives restarts (static custom id).
        bot.add_dynamic_items(NitroAcceptButton)

    async def cog_unload(self) -> None:
        self.bot.remove_dynamic_items(NitroAcceptButton)

    @commands.hybrid_command(name="nitro", description=CMDS.text("nitro.description"), help=CMDS.help("nitro"),
    )
    async def nitro(self, ctx):
        """FREE NITRO!!!"""
        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(content=msg(ctx, "nitro_card")),
                accessory=discord.ui.Thumbnail(
                    media=NITRO_GIF_URL,
                ),
            ),
            discord.ui.ActionRow(
                NitroAcceptButton(msg(ctx, "nitro_accept")),
            ),
        )
        view = discord.ui.LayoutView()
        view.add_item(container)
        await ctx.send(view=view)

    @commands.hybrid_command(name="boring", description=CMDS.text("boring.description"), help=CMDS.help("boring"),
    )
    async def boring(self, ctx):
        """A boring command."""
        prefix = await _resolve_prefix(self.bot, ctx)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "boring_title")),
            discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=msg(ctx, "boring_body")),
            discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=msg(ctx, "boring_hint", prefix=prefix))
        ))
        await ctx.send(view=view)

    @commands.hybrid_command(name="notboring", description=CMDS.text("notboring.description"), help=CMDS.help("notboring"),
    )
    async def notboring(self, ctx):
        """A not boring command."""
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "notboring_title")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=msg(ctx, "notboring_body")),
            discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=msg(ctx, "notboring_footer"))
        ))
        await ctx.send(view=view)

    @commands.hybrid_command(name="crazy", description=CMDS.text("crazy.description"), help=CMDS.help("crazy"),
    )
    async def crazy(self, ctx):
        """Crazy? I was crazy once..."""
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "crazy_body"))
        ))
        await ctx.send(view=view)


async def setup(bot):
    await bot.add_cog(FunCog(bot))