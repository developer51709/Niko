"""
Legal cog — /legal privacy, /legal terms, /legal community
Trilingual EN/DE/ES, cv2 LayoutView.
Content mirrors the public website's /privacy, /terms and /community pages
(web/src/pages/LegalPage.tsx) and must be kept in sync with them.
"""

import discord
from discord.ext import commands
from config.emojis import get_emoji
from config.links import SUPPORT_SERVER, PRIVACY, TOS, COMMUNITY, WEBSITE, DATA_REMOVAL, OWNER_CONTACT
from utils.i18n import make_flat_msg
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

EFFECTIVE_DATE = "<t:1793318400:F>"  # 30 October 2026

MESSAGES = load_locales("cogs.legal", "cog")

#: Tokens the catalogue may use. They are filled when a page is opened, so a
#: link change or an emoji re-upload reaches the legal text without editing
#: three JSON files.
_LEGAL_VALUES = {
    "effective_date": EFFECTIVE_DATE,
    "privacy": PRIVACY,
    "tos": TOS,
    "community": COMMUNITY,
    "website": WEBSITE,
    "data_removal": DATA_REMOVAL,
    "owner_contact": OWNER_CONTACT,
    "support_server": SUPPORT_SERVER,
    "important": get_emoji("important"),
    "user": get_emoji("user"),
}

msg = make_flat_msg(MESSAGES, _LEGAL_VALUES)


def _send_legal(ctx: commands.Context, title_key: str, body_key: str):
    """Build a cv2 LayoutView for a legal document page."""
    title = msg(ctx, title_key)
    body  = msg(ctx, body_key)

    text = f"### {title}\n\n{body}"

    view      = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=text)
    )
    view.add_item(container)
    return view


class LegalCog(commands.Cog, name="Legal"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_group(
        name="legal",
        description=CMDS.text("legal.description"),
        invoke_without_command=True,
    )
    async def legal(self, ctx: commands.Context):
        """Shows an overview pointing to the sub-commands."""
        icon = get_emoji("important")
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"### {icon} Legal\n"
                    + msg(ctx, "legal_overview")
                )
            )
        ))
        await ctx.send(view=view, ephemeral=True)

    @legal.command(
        name="privacy",
        description=CMDS.text("legal.privacy.description"),
    )
    async def privacy(self, ctx: commands.Context):
        """Displays Niko's Privacy Policy."""
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer(ephemeral=True)
        view = _send_legal(ctx, "privacy_title", "privacy_body")
        await ctx.send(view=view, ephemeral=True)

    @legal.command(
        name="terms",
        description=CMDS.text("legal.terms.description"),
    )
    async def terms(self, ctx: commands.Context):
        """Displays Niko's Terms of Service."""
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer(ephemeral=True)
        view = _send_legal(ctx, "terms_title", "terms_body")
        await ctx.send(view=view, ephemeral=True)

    @legal.command(
        name="community",
        description=CMDS.text("legal.community.description"),
    )
    async def community(self, ctx: commands.Context):
        """Displays Niko's Community Policy."""
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer(ephemeral=True)
        view = _send_legal(ctx, "community_title", "community_body")
        await ctx.send(view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(LegalCog(bot))
