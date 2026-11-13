"""Moderation — the paginated warning-case panel.

Up to :data:`PAGE_SIZE` cases per page, each with buttons that rewrite its
reason or remove it, so a moderator fixes a record in place instead of scanning
a wall of text and then remembering which command clears it.

A warning that arrived through the developer API says so, and names the reviewed
application that added it: a server running several bots needs to know where a
case came from before it acts on it.
"""

from datetime import datetime

import discord

from config.emojis import get_emoji
from config.links import VERIFIED_APPLICATIONS_INFO
from utils.i18n import make_flat_msg
from utils.locales import load_locales

from ._messages import EMOJI

PANEL = load_locales(__package__, "warnings_panel")

#: The shared moderation emoji, plus the two only this panel draws.
EMOJI_PANEL = {
    **EMOJI,
    "notepad": get_emoji("notepad"),
    "edit": get_emoji("edit"),
    "trash": get_emoji("trash"),
    "question": get_emoji("question"),
}

_pmsg = make_flat_msg(PANEL, EMOJI_PANEL)

#: Cases shown per page. Four cards with their own buttons still leave room for
#: the header and the page arrows inside one message.
PAGE_SIZE = 4

#: Reasons are shortened on the panel, not in storage: four maximum-length
#: reasons plus their headers would pass Discord's 4000-character message
#: budget, and the edit modal still opens the whole stored reason.
REASON_CHARS = 650


def can_view_warnings(obj) -> bool:
    """Whether a member may read a member's warning history.

    Moderate Members is the permission warnings belong to; Manage Messages is
    accepted too, because a helper who can already clear this channel's messages
    should not need a second permission just to read the list.

    Reads ``permissions``, which both a Context and an Interaction expose as the
    member's resolved permissions, so one check covers prefix and slash.
    """
    permissions = getattr(obj, "permissions", None) or getattr(obj, "guild_permissions", None)
    return bool(permissions and (permissions.moderate_members or permissions.manage_messages))


def can_manage_warnings(obj) -> bool:
    """Whether a member may edit or remove a case.

    Deliberately narrower than :func:`can_view_warnings`: removing a warning is
    as destructive as `/clearwarnings`, which needs Moderate Members, so the
    panel's buttons need it too. Reading the list stays available to Manage
    Messages holders — the panel's whole point is that a helper can look a
    member's history up without being able to rewrite it.
    """
    permissions = getattr(obj, "permissions", None) or getattr(obj, "guild_permissions", None)
    return bool(permissions and permissions.moderate_members)


def _relative_time(value) -> str:
    """A Discord timestamp for a stored ISO time, in the bot's usual style.

    Warnings are stored as ISO strings; printing those raw (as this used to)
    showed the reader a UTC wall clock instead of their own time zone.
    """
    try:
        return f"<t:{int(datetime.fromisoformat(str(value)).timestamp())}:R>"
    except (TypeError, ValueError, OverflowError, OSError):
        return str(value) if value else "unknown"


def _notice(text: str) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return view


def warning_text(guild, warn: dict, *, index: int, ctx, reason_limit: int | None = None) -> str:
    """One case's card, with the API footer when another application added it."""
    moderator = guild.get_member(warn.get("mod")) if guild is not None else None
    by = moderator.mention if moderator else f"<@{warn.get('mod')}>"
    reason = warn.get("reason") or "—"
    if reason_limit is not None and len(reason) > reason_limit:
        reason = reason[: reason_limit - 1].rstrip() + "…"
    text = _pmsg(
        ctx, "warning_card",
        index=index,
        moderator=by,
        reason=reason,
        time=_relative_time(warn.get("time")),
    )
    source_bot_id = warn.get("source_bot_id")
    if source_bot_id:
        text += "\n" + _pmsg(
            ctx, "added_via",
            bot=f"<@{source_bot_id}>",
            link=VERIFIED_APPLICATIONS_INFO,
        )
    return text


class _EditWarningModal(discord.ui.Modal):
    """Rewrite one case's reason without touching its id, author, or time."""

    def __init__(self, panel: "WarningsView", warn: dict):
        super().__init__(title=_pmsg(panel.ctx, "edit_modal_title"))
        self.panel = panel
        self.warn = warn
        self.reason = discord.ui.TextInput(
            label=_pmsg(panel.ctx, "reason_label"),
            placeholder=_pmsg(panel.ctx, "reason_placeholder"),
            style=discord.TextStyle.paragraph,
            max_length=1000,
            default=warn.get("reason") or "",
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        panel = self.panel
        # A modal can outlive the permission it was opened with.
        if not can_manage_warnings(interaction):
            return await interaction.response.send_message(
                view=_notice(_pmsg(interaction, "need_edit_permission")), ephemeral=True)
        updated = await panel.utils.update_warning(
            panel.guild.id, self.warn["id"], str(self.reason.value))
        await panel.reload()
        panel._build()
        await interaction.response.edit_message(
            view=panel, allowed_mentions=discord.AllowedMentions.none())
        if updated is None:
            return await interaction.followup.send(
                view=_notice(_pmsg(interaction, "gone")), ephemeral=True)
        await panel.log(interaction, "Warning edited", updated)


class WarningsView(discord.ui.LayoutView):
    """Paginated moderation panel for one member's warning cases.

    Viewing needs Moderate Members or Manage Messages; editing and removing need
    Moderate Members on their own, because a removal is as destructive as
    `/clearwarnings`. The page arrows work for anyone who can view.
    """

    def __init__(self, *, utils, guild, member, ctx, warnings: list, cog, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.utils = utils
        self.guild = guild
        self.member = member
        self.ctx = ctx
        self.warnings = list(warnings or [])
        self.cog = cog
        self.current_page = 0
        #: Set by the command once the panel is posted, so the timeout can edit
        #: the message it belongs to.
        self.message = None
        self.timed_out = False
        self._build()

    # ── guard ────────────────────────────────────────────────────────────────

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if can_view_warnings(interaction):
            return True
        await interaction.response.send_message(
            view=_notice(_pmsg(interaction, "need_permission")), ephemeral=True)
        return False

    async def _require_manage(self, interaction: discord.Interaction) -> bool:
        """Gate the destructive buttons on Moderate Members alone."""
        if can_manage_warnings(interaction):
            return True
        await interaction.response.send_message(
            view=_notice(_pmsg(interaction, "need_edit_permission")), ephemeral=True)
        return False

    async def on_timeout(self) -> None:
        """Disable the panel and say why, so nobody presses a dead button."""
        self.timed_out = True
        self._build()
        if self.message is None:
            return
        try:
            await self.message.edit(
                view=self, allowed_mentions=discord.AllowedMentions.none())
        except discord.HTTPException:
            # The message may have been deleted; nothing left to disable.
            pass

    # ── state ────────────────────────────────────────────────────────────────

    def page_count(self) -> int:
        return max(1, -(-len(self.warnings) // PAGE_SIZE))

    def page_warnings(self) -> list:
        """The cases on the page being shown."""
        start = self.current_page * PAGE_SIZE
        return self.warnings[start:start + PAGE_SIZE]

    async def reload(self) -> None:
        """Re-read the member's cases and keep the page in range."""
        self.warnings = await self.utils.get_warnings(self.guild.id, self.member.id)
        self.current_page = min(self.current_page, self.page_count() - 1)

    async def log(self, interaction: discord.Interaction, action: str, warn: dict) -> None:
        """Record an edit or removal in the server's moderation log."""
        logger = self.cog.logger() if hasattr(self.cog, "logger") else None
        if logger is None:
            return
        body = (
            f"**User:** {self.member.mention} (`{self.member}` — ID: `{self.member.id}`)\n"
            f"**Action:** {action}\n**Reason:** {warn.get('reason') or '—'}\n"
            f"**Moderator:** {interaction.user.mention}"
        )
        try:
            await logger.log_event(
                self.guild, "moderation", action, body, target_id=self.member.id)
        except Exception:
            # The case was already changed; a missing log channel must not
            # make the moderator think the action failed.
            pass

    # ── actions ──────────────────────────────────────────────────────────────

    async def _on_edit(self, interaction: discord.Interaction, warn: dict):
        if not await self._require_manage(interaction):
            return
        await interaction.response.send_modal(_EditWarningModal(self, warn))

    async def _on_remove(self, interaction: discord.Interaction, warn: dict):
        if not await self._require_manage(interaction):
            return
        removed = await self.utils.delete_warning(self.guild.id, warn["id"])
        await self.reload()
        self._build()
        await interaction.response.edit_message(
            view=self, allowed_mentions=discord.AllowedMentions.none())
        if removed is None:
            return await interaction.followup.send(
                view=_notice(_pmsg(interaction, "gone")), ephemeral=True)
        await self.log(interaction, "Warning removed", removed)

    async def _on_prev(self, interaction: discord.Interaction):
        self.current_page = max(0, self.current_page - 1)
        self._build()
        await interaction.response.edit_message(
            view=self, allowed_mentions=discord.AllowedMentions.none())

    async def _on_next(self, interaction: discord.Interaction):
        self.current_page = min(self.page_count() - 1, self.current_page + 1)
        self._build()
        await interaction.response.edit_message(
            view=self, allowed_mentions=discord.AllowedMentions.none())

    # ── layout ───────────────────────────────────────────────────────────────

    def _build(self) -> None:
        self.clear_items()
        total = len(self.warnings)

        self.add_item(discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(content=_pmsg(
                    self.ctx, "panel_heading",
                    member=self.member.mention, count=total,
                )),
                accessory=discord.ui.Thumbnail(self.member.display_avatar.url),
            )
        ))

        page = self.page_warnings()
        if not page:
            self.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=_pmsg(self.ctx, "empty_state"))))
        else:
            first = self.current_page * PAGE_SIZE + 1
            cards = []
            for offset, warn in enumerate(page):
                if offset:
                    cards.append(discord.ui.Separator(
                        visible=True, spacing=discord.SeparatorSpacing.small))
                cards.append(discord.ui.TextDisplay(content=warning_text(
                    self.guild, warn, index=first + offset, ctx=self.ctx,
                    reason_limit=REASON_CHARS)))
                cards.append(self._case_actions(warn))
            self.add_item(discord.ui.Container(*cards))

        pages = self.page_count()
        footer_items = [
            discord.ui.TextDisplay(content=_pmsg(
                self.ctx, "footer_page",
                page=self.current_page + 1, total=pages,
            )),
        ]
        if pages > 1:
            prev = discord.ui.Button(
                label="◀", style=discord.ButtonStyle.secondary,
                disabled=self.timed_out or self.current_page == 0)
            prev.callback = self._on_prev
            label = discord.ui.Button(
                label=f"{self.current_page + 1} / {pages}",
                style=discord.ButtonStyle.secondary, disabled=True)
            label.callback = _noop
            nxt = discord.ui.Button(
                label="▶", style=discord.ButtonStyle.secondary,
                disabled=self.timed_out or self.current_page == pages - 1)
            nxt.callback = self._on_next
            footer_items.append(
                discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small))
            footer_items.append(discord.ui.ActionRow(prev, label, nxt))
        if self.timed_out:
            footer_items.append(discord.ui.TextDisplay(
                content=_pmsg(self.ctx, "timed_out")))
        self.add_item(discord.ui.Container(*footer_items))

    def _case_actions(self, warn: dict) -> discord.ui.ActionRow:
        """The edit and remove buttons for one case on the page."""
        edit = discord.ui.Button(
            label=_pmsg(self.ctx, "button_edit"),
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("edit"),
            disabled=self.timed_out,
        )
        edit.callback = lambda interaction, target=warn: self._on_edit(interaction, target)
        remove = discord.ui.Button(
            label=_pmsg(self.ctx, "button_remove"),
            style=discord.ButtonStyle.danger,
            emoji=get_emoji("trash"),
            disabled=self.timed_out,
        )
        remove.callback = lambda interaction, target=warn: self._on_remove(interaction, target)
        return discord.ui.ActionRow(edit, remove)


async def _noop(interaction: discord.Interaction):
    """The page label is a disabled button; this keeps its callback inert."""
    return None
