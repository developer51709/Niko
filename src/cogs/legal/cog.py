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

EFFECTIVE_DATE = "<t:1794614400:F>"  # 14 November 2026 00:00 UTC

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


#: Discord counts every displayable character in one message — all components
#: together — against a 4,000 cap, not per TextDisplay. The detailed legal
#: pages are about twice that, so each page is one display and the reader moves
#: between them instead of the whole document going out at once.
_TEXT_DISPLAY_LIMIT = 3800


def _chunks(text: str, limit: int = _TEXT_DISPLAY_LIMIT) -> list[str]:
    """Split markdown into page-sized chunks, each fit to one message.

    A paragraph over the limit is first cut at a bullet or a word so no block
    is larger than a page, and the pieces are then packed greedily. Packing
    afterwards is what keeps a short heading with the text that follows it
    instead of sending the heading alone on a page of its own.
    """
    blocks: list[str] = []
    for block in text.split("\n\n"):
        while len(block) > limit:
            window = block[:limit]
            cut = max(window.rfind("\n"), window.rfind(" "))
            cut = cut if cut > 0 else limit
            blocks.append(block[:cut].rstrip())
            block = block[cut:].lstrip()
        blocks.append(block)

    chunks: list[str] = []
    current = ""
    for block in blocks:
        while block:
            room = limit - (len(current) + 2 if current else 0)
            # A sliver of room is not worth ending a page on, so the page is
            # closed and the block starts the next one whole.
            if room < 200 and current:
                chunks.append(current)
                current = ""
                continue
            if len(block) <= room:
                current = f"{current}\n\n{block}" if current else block
                break
            window = block[:room]
            cut = max(window.rfind("\n"), window.rfind(" "))
            cut = cut if cut > 0 else room
            piece = block[:cut].rstrip()
            chunks.append(f"{current}\n\n{piece}" if current else piece)
            current = ""
            block = block[cut:].lstrip()
    if current:
        chunks.append(current)
    return chunks


class LegalPager(discord.ui.LayoutView):
    """A legal document split into pages the reader can move between.

    One page is one TextDisplay, because Discord's 4,000 character budget
    covers the whole message. The buttons swap the page in place, and the view
    disables them when it expires so a dead card looks dead.
    """

    TIMEOUT = 300

    def __init__(self, pages: list[str], author_id: int, prev_label: str, next_label: str, locked_notice: str):
        super().__init__(timeout=self.TIMEOUT)
        self.pages         = pages
        self.author_id     = author_id
        self.prev_label    = prev_label
        self.next_label    = next_label
        self.locked_notice = locked_notice
        self.page          = 0
        #: Set after ``ctx.send`` so a timeout can grey the card out.
        self.message: discord.Message | None = None
        self.nav_buttons: list[discord.ui.Button] = []
        self._render()

    def _render(self):
        self.clear_items()
        container = discord.ui.Container(discord.ui.TextDisplay(content=self.pages[self.page]))
        if len(self.pages) > 1:
            row = discord.ui.ActionRow()
            previous = discord.ui.Button(
                label=self.prev_label,
                style=discord.ButtonStyle.secondary,
                disabled=self.page == 0,
            )
            previous.callback = self._previous
            row.add_item(previous)
            # The page counter is a disabled button so it sits in the same row;
            # "1/3" reads the same in every language.
            row.add_item(discord.ui.Button(
                label=f"{self.page + 1}/{len(self.pages)}",
                style=discord.ButtonStyle.secondary,
                disabled=True,
            ))
            following = discord.ui.Button(
                label=self.next_label,
                style=discord.ButtonStyle.secondary,
                disabled=self.page == len(self.pages) - 1,
            )
            following.callback = self._next
            row.add_item(following)
            self.nav_buttons = [previous, following]
            container.add_item(row)
        self.add_item(container)

    async def _turn(self, interaction: discord.Interaction, step: int):
        # An ephemeral message can only be edited by the person it was sent to,
        # so another member's click is answered instead of silently failing.
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(self.locked_notice, ephemeral=True)
            return
        self.page = min(max(self.page + step, 0), len(self.pages) - 1)
        self._render()
        # Discord notifies a mentioned member when an edit introduces the
        # mention, so the owner credited in the footer would be pinged on the
        # page that first shows it unless every page turn suppresses them too.
        await interaction.response.edit_message(view=self, allowed_mentions=discord.AllowedMentions.none())

    async def _previous(self, interaction: discord.Interaction):
        await self._turn(interaction, -1)

    async def _next(self, interaction: discord.Interaction):
        await self._turn(interaction, 1)

    async def on_timeout(self):
        for button in self.nav_buttons:
            button.disabled = True
        if self.message is not None:
            try:
                # The page on screen may be the one carrying the owner credit,
                # and an edit that first introduces a mention notifies them.
                await self.message.edit(view=self, allowed_mentions=discord.AllowedMentions.none())
            except discord.HTTPException:
                pass


def _send_legal(ctx: commands.Context, title_key: str, body_key: str) -> LegalPager:
    """Build the paged view for a legal document."""
    title = msg(ctx, title_key)
    body  = msg(ctx, body_key)

    text = f"### {title}\n\n{body}\n\n-# {msg(ctx, 'updated_by')}"

    return LegalPager(
        _chunks(text),
        ctx.author.id,
        msg(ctx, "page_prev"),
        msg(ctx, "page_next"),
        msg(ctx, "page_locked"),
    )


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
        view.message = await ctx.send(view=view, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())

    @legal.command(
        name="terms",
        description=CMDS.text("legal.terms.description"),
    )
    async def terms(self, ctx: commands.Context):
        """Displays Niko's Terms of Service."""
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer(ephemeral=True)
        view = _send_legal(ctx, "terms_title", "terms_body")
        view.message = await ctx.send(view=view, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())

    @legal.command(
        name="community",
        description=CMDS.text("legal.community.description"),
    )
    async def community(self, ctx: commands.Context):
        """Displays Niko's Community Policy."""
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer(ephemeral=True)
        view = _send_legal(ctx, "community_title", "community_body")
        view.message = await ctx.send(view=view, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())


async def setup(bot: commands.Bot):
    await bot.add_cog(LegalCog(bot))
