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

EFFECTIVE_DATE = "<t:1793491200:F>"  # 1 November 2026 00:00 UTC

#: The owner's Discord account, credited on every legal page. Sends suppress
#: mentions, so opening /legal never pings them.
OWNER_MENTION = "<@1052690741874401360>"

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
    "owner_mention": OWNER_MENTION,
    "support_server": SUPPORT_SERVER,
    "important": get_emoji("important"),
    "user": get_emoji("user"),
}

msg = make_flat_msg(MESSAGES, _LEGAL_VALUES)


#: Discord caps a single TextDisplay at 4,000 characters, and the detailed
#: legal pages are longer than that, so a page is packed into several displays.
_TEXT_DISPLAY_LIMIT = 3800


def _chunks(text: str, limit: int = _TEXT_DISPLAY_LIMIT) -> list[str]:
    """Split markdown into paragraph-sized chunks that each fit a TextDisplay."""
    chunks: list[str] = []
    current = ""
    for block in text.split("\n\n"):
        candidate = f"{current}\n\n{block}" if current else block
        if len(candidate) <= limit:
            current = candidate
            continue
        if current:
            chunks.append(current)
        # A lone paragraph over the limit is cut at a bullet, then at a word.
        while len(block) > limit:
            window = block[:limit]
            cut = max(window.rfind("\n"), window.rfind(" "))
            cut = cut if cut > 0 else limit
            chunks.append(block[:cut].rstrip())
            block = block[cut:].lstrip()
        current = block
    if current:
        chunks.append(current)
    return chunks


def _send_legal(ctx: commands.Context, title_key: str, body_key: str):
    """Build a cv2 LayoutView for a legal document page."""
    title = msg(ctx, title_key)
    body  = msg(ctx, body_key)

    text = f"### {title}\n\n{body}\n\n-# {msg(ctx, 'updated_by')}"

    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        *(discord.ui.TextDisplay(content=chunk) for chunk in _chunks(text))
    ))
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
        await ctx.send(view=view, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())

    @legal.command(
        name="privacy",
        description=CMDS.text("legal.privacy.description"),
    )
    async def privacy(self, ctx: commands.Context):
        """Displays Niko's Privacy Policy."""
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer(ephemeral=True)
        view = _send_legal(ctx, "privacy_title", "privacy_body")
        await ctx.send(view=view, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())

    @legal.command(
        name="terms",
        description=CMDS.text("legal.terms.description"),
    )
    async def terms(self, ctx: commands.Context):
        """Displays Niko's Terms of Service."""
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer(ephemeral=True)
        view = _send_legal(ctx, "terms_title", "terms_body")
        await ctx.send(view=view, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())

    @legal.command(
        name="community",
        description=CMDS.text("legal.community.description"),
    )
    async def community(self, ctx: commands.Context):
        """Displays Niko's Community Policy."""
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer(ephemeral=True)
        view = _send_legal(ctx, "community_title", "community_body")
        await ctx.send(view=view, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())


async def setup(bot: commands.Bot):
    await bot.add_cog(LegalCog(bot))
