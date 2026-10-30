"""
Premium ticket system — single `ticket` group with admin + in-ticket sub-commands.

Admin sub-commands (manage_guild required):
    ticket setup              — open the configuration panel
    ticket panel              — post the public ticket panel here
    ticket category add/remove/list
    ticket support add/remove/list

In-ticket sub-commands (must be used inside a ticket channel,
support roles or manage_channels):
    ticket add <user>         — grant the user access
    ticket remove <user>      — revoke the user's access
    ticket rename <name>      — rename the channel
    ticket claim              — mark the ticket as claimed by you
    ticket transcript         — generate a text transcript
    ticket close              — soft-close (lock) the ticket
    ticket delete             — delete the ticket channel
"""

from __future__ import annotations

import asyncio
import io
import time
from datetime import datetime, timezone
from typing import Optional

import discord
from discord.ext import commands
from discord.ui import Modal, TextInput

from utils.tickets.utils import (
    get_ticket_config,
    update_ticket_config,
    async_update_ticket_config,
    get_all_ticket_configs,
    find_open_ticket,
)
from utils.tickets.config import TicketConfig
from config.emojis import get_emoji
from utils.i18n import get_lang
from utils.locales import load_locales


# ───────────────────────────────────────────────────
#  TRILINGUAL MESSAGE TABLE
# ───────────────────────────────────────────────────

MESSAGES = load_locales("cogs.tickets", "views")


def msg(ctx_or_int, key: str, **kwargs) -> str:
    """Resolve a ticket message in the guild's language.

    The café voice was retired, so every guild gets the same wording; only the
    language changes.
    """
    lang = get_lang(ctx_or_int)
    text = (
        MESSAGES.get(lang, {}).get(key)
        or MESSAGES["en"].get(key, key)
    )
    return text.format(**kwargs) if kwargs else text


def _cv2(text: str) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return view


# ───────────────────────────────────────────────────
#  HELPERS
# ───────────────────────────────────────────────────

def parse_hex_color(text: str) -> Optional[int]:
    text = text.strip().replace("#", "")
    try:
        return int(text, 16)
    except ValueError:
        return None


def panel_accent_colour(color: Optional[int]) -> Optional[discord.Colour]:
    """Translate a stored panel color into the container's accent bar.

    The color is a `0xRRGGBB` integer (the dashboard converts the hex input to
    one, the setup modal uses `parse_hex_color`); a hex string is accepted too,
    because a config row written before that conversion can still hold one.
    Anything missing or out of range means "no accent", which is why this
    returns `None` rather than a fallback color or, worse, a string that would
    end up in the panel text.
    """
    if color is None or isinstance(color, bool):
        return None
    if isinstance(color, str):
        value = parse_hex_color(color)
        if value is None:
            return None
    else:
        try:
            value = int(color)
        except (TypeError, ValueError):
            return None
    if not 0 <= value <= 0xFFFFFF:
        return None
    return discord.Colour(value)


def is_ticket_channel(ctx: commands.Context) -> Optional[dict]:
    if not ctx.guild:
        return None
    return find_open_ticket(ctx.guild.id, ctx.channel.id)


def has_support_perms(member: discord.Member, cfg: TicketConfig) -> bool:
    if member.guild_permissions.manage_channels:
        return True
    role_ids = {r.id for r in member.roles}
    return any(rid in role_ids for rid in cfg.support_roles)


# ───────────────────────────────────────────────────
#  MODALS — admin setup
# ───────────────────────────────────────────────────

class TicketPanelModal(Modal):
    def __init__(self, guild_id: int, ctx=None):
        super().__init__(title=msg(ctx, "panel_modal_title"))
        self.guild_id = guild_id

        cfg = get_ticket_config(guild_id)
        self.title_input = TextInput(
            label=msg(ctx, "panel_title_label"), required=False,
            default=cfg.panel_title or ""
        )
        self.desc_input = TextInput(
            label=msg(ctx, "panel_description_label"), style=discord.TextStyle.long,
            required=False, default=cfg.panel_description or ""
        )
        self.color_input = TextInput(
            label=msg(ctx, "panel_colour_label"), required=False,
            default=f"#{cfg.panel_color:06X}" if cfg.panel_color else ""
        )
        self.image_input = TextInput(
            label=msg(ctx, "panel_image_label"), required=False,
            default=cfg.panel_image or ""
        )

        self.add_item(self.title_input)
        self.add_item(self.desc_input)
        self.add_item(self.color_input)
        self.add_item(self.image_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = get_ticket_config(self.guild_id)
        if self.title_input.value:
            cfg.panel_title = self.title_input.value
        if self.desc_input.value:
            cfg.panel_description = self.desc_input.value
        if self.color_input.value:
            parsed = parse_hex_color(self.color_input.value)
            if parsed is not None:
                cfg.panel_color = parsed
        cfg.panel_image = self.image_input.value or None
        await async_update_ticket_config(self.guild_id, cfg)

        # update existing posted panel if present
        if cfg.panel_message_id and cfg.panel_channel_id:
            channel = interaction.guild.get_channel(cfg.panel_channel_id)
            if channel:
                try:
                    m = await channel.fetch_message(cfg.panel_message_id)
                    await m.edit(view=TicketPanelView(self.guild_id, cfg))
                except Exception:
                    pass

        await interaction.response.send_message(msg(interaction, "panel_updated"), ephemeral=True)


# ───────────────────────────────────────────────────
#  USER-FACING PANEL
# ───────────────────────────────────────────────────

class OpenTicketBtn(discord.ui.Button):
    def __init__(self, guild_id: int, label: str = "Create Ticket"):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.green,
            custom_id=f"open_ticket_{guild_id}",
        )
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        cfg = get_ticket_config(self.guild_id)
        categories = cfg.panel_categories
        if categories:
            view = discord.ui.LayoutView(timeout=None)
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=msg(interaction, "select_category")),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                CategorySelectRow(self.guild_id, categories, msg(interaction, "select_placeholder")),
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        await create_ticket(interaction, "General")


class CategorySelect(discord.ui.Select):
    def __init__(self, guild_id: int, categories: list[str], placeholder: str):
        self.guild_id = guild_id
        options = [
            discord.SelectOption(label=c, value=c) for c in categories
        ]
        super().__init__(placeholder=placeholder, options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await create_ticket(interaction, self.values[0])


class CategorySelectRow(discord.ui.ActionRow):
    def __init__(self, guild_id: int, categories: list[str], placeholder: str):
        super().__init__()
        self.add_item(CategorySelect(guild_id, categories, placeholder))


class TicketPanelView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, cfg: Optional[TicketConfig] = None):
        super().__init__(timeout=None)
        cfg = cfg or get_ticket_config(guild_id)
        guild = None  # we don't have a context here; localise with default fallback
        # Default fallback to english panel labels — admins can override via the modal
        title = cfg.panel_title or MESSAGES["en"]["panel_default_title"]
        desc = cfg.panel_description or MESSAGES["en"]["panel_default_desc"]

        # The configured color is the container's accent bar. It used to be
        # appended to the title as a literal `#RRGGBB` code, which is why an
        # accent color saved from the dashboard showed up as text instead.
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('ticket')} {title}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=desc),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            accent_colour=panel_accent_colour(cfg.panel_color),
        )
        if cfg.panel_image:
            container.add_item(
                discord.ui.MediaGallery(discord.MediaGalleryItem(media=cfg.panel_image))
            )
        container.add_item(
            discord.ui.ActionRow(
                OpenTicketBtn(guild_id, label=MESSAGES["en"]["open_btn"])
            )
        )
        self.add_item(container)


def _ticket_status_text(ctx_or_int, status: str) -> str:
    return msg(ctx_or_int, "status_closed" if status == "closed" else "status_open")


def build_ticket_header_view(
    ctx_or_int,
    *,
    category: str,
    opener_id: int,
    channel: discord.TextChannel,
    claimed_by: Optional[int] = None,
    status: str = "open",
) -> discord.ui.LayoutView:
    """The pinned card shown at the top of every ticket.

    Displays the ticket details and carries the persistent Staff Panel
    button that opens the ephemeral management panel.
    """
    icon = get_emoji("ticket")
    guild = channel.guild
    opener = guild.get_member(opener_id)
    opener_ref = opener.mention if opener else f"<@{opener_id}>"

    if claimed_by:
        claimer = guild.get_member(claimed_by)
        claim_ref = claimer.mention if claimer else f"<@{claimed_by}>"
    else:
        claim_ref = msg(ctx_or_int, "unclaimed")

    opened_ts = int(channel.created_at.timestamp()) if channel.created_at else int(time.time())
    welcome = msg(
        ctx_or_int, "ticket_welcome",
        icon=icon, category=category, mention=opener_ref,
    )
    details = msg(
        ctx_or_int, "header_details",
        icon=icon,
        category=category,
        opener=opener_ref,
        channel=channel.mention,
        opened=f"<t:{opened_ts}:f>",
        status=_ticket_status_text(ctx_or_int, status),
        claim=claim_ref,
    )

    accent = discord.Color.red() if status == "closed" else discord.Color.green()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=welcome),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=details),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(StaffPanelButton(label=msg(ctx_or_int, "btn_staff"))),
        accent_colour=accent,
    )
    view = discord.ui.LayoutView(timeout=None)
    view.add_item(container)
    return view


async def refresh_ticket_header(
    ctx_or_int,
    guild: discord.Guild,
    channel: discord.TextChannel,
    ticket: dict,
    cfg: Optional[TicketConfig] = None,
) -> None:
    """Re-render the pinned header message of an existing ticket (best effort)."""
    cfg = cfg or get_ticket_config(guild.id)
    mid = ticket.get("message_id")
    if not mid:
        return
    try:
        header_msg = await channel.fetch_message(int(mid))
    except Exception:
        return
    try:
        await header_msg.edit(
            view=build_ticket_header_view(
                ctx_or_int,
                category=ticket.get("category", "General"),
                opener_id=ticket.get("opener_id", 0),
                channel=channel,
                claimed_by=ticket.get("claimed_by"),
                status=ticket.get("status", "open"),
            )
        )
    except Exception:
        pass


# ───────────────────────────────────────────────────
#  CREATE TICKET
# ───────────────────────────────────────────────────

async def create_ticket(interaction: discord.Interaction, category: str):
    guild = interaction.guild
    user = interaction.user

    cfg = get_ticket_config(guild.id)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, embed_links=True),
        guild.me: discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True,
            # needed so the bot can auto-pin the ticket header and quietly
            # delete the pin system-notice afterwards
            manage_messages=True,
        ),
    }
    for rid in cfg.support_roles:
        role = guild.get_role(rid)
        if role:
            overwrites[role] = discord.PermissionOverwrite(
                read_messages=True, send_messages=True, manage_messages=True
            )

    channel = await guild.create_text_channel(
        name=f"ticket-{user.name}",
        overwrites=overwrites,
        reason=f"Ticket opened by {user}",
    )

    entry = {
        "channel_id": channel.id,
        "message_id": None,
        "category": category,
        "opener_id": user.id,
        "claimed_by": None,
        "status": "open",
    }
    header_view = build_ticket_header_view(
        interaction,
        category=category,
        opener_id=user.id,
        channel=channel,
        claimed_by=None,
        status="open",
    )
    msg_obj = await channel.send(view=header_view)
    entry["message_id"] = msg_obj.id
    cfg.open_tickets.append(entry)
    await async_update_ticket_config(guild.id, cfg)

    # Pin the header so the ticket details + Staff Panel button stay on top,
    # then quietly remove the automated "pinned a message" system notice.
    try:
        await msg_obj.pin(reason=f"Ticket header for {user}")
        async for m in channel.history(limit=3):
            if m.id != msg_obj.id and m.type == discord.MessageType.pins_add:
                try:
                    await m.delete()
                except Exception:
                    pass
                break
    except Exception:
        pass

    text = msg(interaction, "ticket_created", channel=channel.mention)
    if interaction.response.is_done():
        await interaction.followup.send(text, ephemeral=True)
    else:
        await interaction.response.send_message(text, ephemeral=True)


# ───────────────────────────────────────────────────
#  TICKET STAFF PANEL (ephemeral per-ticket controls)
#  The pinned header card carries one persistent "Staff Panel" button.
#  Every custom id below is stable so views keep working across restarts
#  (see register_ticket_persistent_views, called from the cog setup).
# ───────────────────────────────────────────────────

_TICKET_HEADER_ID       = "ticket:header:staff"
_TICKET_CLAIM_ID        = "ticket:panel:claim"
_TICKET_TRANSFER_ID     = "ticket:panel:transfer"
_TICKET_CLOSE_ID        = "ticket:panel:close"
_TICKET_DELETE_ID       = "ticket:panel:delete"
_TICKET_DELETE_YES_ID   = "ticket:panel:delete_yes"
_TICKET_CANCEL_ID       = "ticket:panel:cancel"
_TICKET_ADD_ID          = "ticket:panel:add"
_TICKET_REMOVE_ID       = "ticket:panel:remove"
_TICKET_SEL_ADD_ID      = "ticket:panel:sel_add"
_TICKET_SEL_REMOVE_ID   = "ticket:panel:sel_remove"
_TICKET_SEL_TRANSFER_ID = "ticket:panel:sel_transfer"


def build_staff_panel_view(
    ctx_or_int,
    channel: discord.TextChannel,
    ticket: dict,
    cfg: TicketConfig,
    *,
    confirm: Optional[str] = None,
) -> discord.ui.LayoutView:
    """The ephemeral staff panel shown after pressing the header button."""
    view = discord.ui.LayoutView(timeout=None)
    icon = get_emoji("ticket")
    title = msg(ctx_or_int, "panel_title", icon=icon, channel=channel.mention)

    if ticket.get("claimed_by"):
        claimer = channel.guild.get_member(ticket["claimed_by"])
        claim_ref = claimer.mention if claimer else f"<@{ticket['claimed_by']}>"
    else:
        claim_ref = msg(ctx_or_int, "unclaimed")
    status_line = f"**{_ticket_status_text(ctx_or_int, ticket.get('status', 'open'))}** — {claim_ref}"

    children: list = []
    if confirm:
        children.append(discord.ui.TextDisplay(content=confirm))
    children.extend([
        discord.ui.TextDisplay(content=title),
        discord.ui.TextDisplay(content=status_line),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
    ])

    claim_button = (
        _TicketTransferButton(label=msg(ctx_or_int, "btn_transfer"))
        if ticket.get("claimed_by")
        else _TicketClaimButton(label=msg(ctx_or_int, "btn_claim"))
    )
    children.append(discord.ui.ActionRow(
        claim_button,
        _TicketCloseButton(label=msg(ctx_or_int, "btn_close")),
        _TicketDeleteButton(label=msg(ctx_or_int, "btn_delete")),
    ))
    children.append(discord.ui.ActionRow(
        _TicketAddButton(label=msg(ctx_or_int, "btn_add")),
        _TicketRemoveButton(label=msg(ctx_or_int, "btn_remove")),
    ))
    view.add_item(discord.ui.Container(*children))
    return view


def _panel_text_view(content: str) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView(timeout=None)
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=content)))
    return view


async def _panel_context(interaction: discord.Interaction):
    """Resolve (ticket, cfg) for the interaction's channel.

    Replies with an ephemeral denial and returns (None, None) when the
    user isn't support staff or the channel isn't an open ticket.
    """
    if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel):
        return None, None
    cfg = get_ticket_config(interaction.guild.id)
    if not has_support_perms(interaction.user, cfg):
        await interaction.response.send_message(msg(interaction, "staff_panel_only"), ephemeral=True)
        return None, None
    ticket = find_open_ticket(interaction.guild.id, interaction.channel.id)
    if ticket is None:
        await interaction.response.send_message(msg(interaction, "not_in_ticket"), ephemeral=True)
        return None, None
    return ticket, cfg


async def _show_panel(
    interaction: discord.Interaction,
    ticket: dict,
    cfg: TicketConfig,
    *,
    confirm: Optional[str] = None,
) -> None:
    view = build_staff_panel_view(interaction, interaction.channel, ticket, cfg, confirm=confirm)
    await interaction.response.edit_message(view=view)


async def _persist_and_refresh(
    interaction: discord.Interaction,
    cfg: TicketConfig,
    ticket: dict,
) -> None:
    """Save config changes and re-render the pinned header card."""
    await async_update_ticket_config(interaction.guild.id, cfg)
    await refresh_ticket_header(
        interaction, interaction.guild, interaction.channel, ticket, cfg
    )


async def _member_has_access(channel: discord.TextChannel, member: discord.Member) -> bool:
    try:
        return bool(channel.overwrites_for(member).read_messages)
    except Exception:
        return False


def _ticket_member_options(channel: discord.TextChannel, ctx=None) -> list:
    """Member options (max 25) for the 'remove user' picker."""
    options: list = []
    for target, perms in list(channel.overwrites.items()):
        if isinstance(target, discord.Role) or target == channel.guild.me:
            continue
        if not (perms.read_messages or perms.view_channel):
            continue
        name = (getattr(target, "display_name", None) or str(target))[:90] \
            or msg(ctx, "member_fallback")
        options.append(discord.SelectOption(
            label=name, value=str(target.id),
            description=msg(ctx, "member_option_description"),
        ))
        if len(options) >= 25:
            break
    return options


# ── buttons ────────────────────────────────────────

class StaffPanelButton(discord.ui.Button):
    """Persistent 'Staff Panel' button pinned at the top of every ticket."""
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Staff Panel",
            style=discord.ButtonStyle.secondary,
            custom_id=_TICKET_HEADER_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel):
            return
        cfg = get_ticket_config(interaction.guild.id)
        if not has_support_perms(interaction.user, cfg):
            return await interaction.response.send_message(
                msg(interaction, "staff_panel_only"), ephemeral=True
            )
        ticket = find_open_ticket(interaction.guild.id, interaction.channel.id)
        if ticket is None:
            return await interaction.response.send_message(
                msg(interaction, "not_in_ticket"), ephemeral=True
            )
        view = build_staff_panel_view(interaction, interaction.channel, ticket, cfg)
        await interaction.response.send_message(view=view, ephemeral=True)


class _TicketClaimButton(discord.ui.Button):
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Claim",
            style=discord.ButtonStyle.success,
            custom_id=_TICKET_CLAIM_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        existing = ticket.get("claimed_by")
        if existing:
            other = interaction.guild.get_member(existing)
            who = other.mention if other else f"<@{existing}>"
            return await interaction.response.send_message(
                msg(interaction, "already_claimed", user=who), ephemeral=True
            )
        ticket["claimed_by"] = interaction.user.id
        await _persist_and_refresh(interaction, cfg, ticket)
        await _show_panel(
            interaction, ticket, cfg,
            confirm=msg(interaction, "claimed", user=interaction.user.mention),
        )


class _TicketTransferButton(discord.ui.Button):
    """Shown once the ticket has been claimed — hands the claim to another member."""
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Transfer",
            style=discord.ButtonStyle.primary,
            custom_id=_TICKET_TRANSFER_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        # No claim (anymore)? treat it like a claim instead.
        if not ticket.get("claimed_by"):
            ticket["claimed_by"] = interaction.user.id
            await _persist_and_refresh(interaction, cfg, ticket)
            return await _show_panel(
                interaction, ticket, cfg,
                confirm=msg(interaction, "claimed", user=interaction.user.mention),
            )
        prompt = msg(interaction, "prompt_transfer", channel=interaction.channel.mention)
        view = discord.ui.LayoutView(timeout=None)
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=prompt),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _TicketTransferUserSelect(placeholder=msg(interaction, "sel_staff")),
            ),
            discord.ui.ActionRow(
                _TicketCancelButton(label=msg(interaction, "btn_cancel")),
            ),
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)


class _TicketCloseButton(discord.ui.Button):
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Close",
            style=discord.ButtonStyle.secondary,
            custom_id=_TICKET_CLOSE_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return

        channel = interaction.channel
        ow = channel.overwrites
        for target, perms in list(ow.items()):
            if isinstance(target, (discord.Member, discord.User)) and target != channel.guild.me:
                perms.send_messages = False
                ow[target] = perms
        try:
            await channel.edit(
                overwrites=ow,
                name=f"closed-{channel.name}"[:95],
                reason=f"Closed by {interaction.user}",
            )
        except Exception:
            pass

        ticket["status"] = "closed"
        await _persist_and_refresh(interaction, cfg, ticket)
        await _show_panel(
            interaction, ticket, cfg,
            confirm=msg(interaction, "closed", user=interaction.user.mention),
        )


class _TicketDeleteButton(discord.ui.Button):
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Delete",
            style=discord.ButtonStyle.danger,
            custom_id=_TICKET_DELETE_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        prompt = msg(interaction, "prompt_delete", channel=interaction.channel.mention)
        view = discord.ui.LayoutView(timeout=None)
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=prompt),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _TicketDeleteYesButton(label=msg(interaction, "btn_confirm_delete")),
                _TicketCancelButton(label=msg(interaction, "btn_cancel")),
            ),
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)


class _TicketDeleteYesButton(discord.ui.Button):
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Delete Ticket",
            style=discord.ButtonStyle.danger,
            custom_id=_TICKET_DELETE_YES_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return

        cfg.open_tickets = [
            t for t in cfg.open_tickets
            if t.get("channel_id") != interaction.channel.id
        ]
        await async_update_ticket_config(interaction.guild.id, cfg)

        deleting = _panel_text_view(msg(interaction, "deleting_panel"))
        await interaction.response.edit_message(view=deleting)
        await asyncio.sleep(3)
        try:
            await interaction.channel.delete(reason=f"Ticket deleted by {interaction.user}")
        except Exception:
            pass


class _TicketAddButton(discord.ui.Button):
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Add User",
            style=discord.ButtonStyle.primary,
            custom_id=_TICKET_ADD_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        prompt = msg(interaction, "prompt_add", channel=interaction.channel.mention)
        view = discord.ui.LayoutView(timeout=None)
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=prompt),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _TicketAddUserSelect(placeholder=msg(interaction, "sel_user")),
            ),
            discord.ui.ActionRow(
                _TicketCancelButton(label=msg(interaction, "btn_cancel")),
            ),
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)


class _TicketRemoveButton(discord.ui.Button):
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Remove User",
            style=discord.ButtonStyle.secondary,
            custom_id=_TICKET_REMOVE_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        options = _ticket_member_options(interaction.channel, interaction)
        if not options:
            return await _show_panel(
                interaction, ticket, cfg,
                confirm=msg(interaction, "no_users_removed"),
            )
        prompt = msg(interaction, "prompt_remove", channel=interaction.channel.mention)
        view = discord.ui.LayoutView(timeout=None)
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=prompt),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _TicketRemoveUserSelect(options, placeholder=msg(interaction, "sel_user")),
            ),
            discord.ui.ActionRow(
                _TicketCancelButton(label=msg(interaction, "btn_cancel")),
            ),
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)


class _TicketCancelButton(discord.ui.Button):
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Cancel",
            style=discord.ButtonStyle.secondary,
            custom_id=_TICKET_CANCEL_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        await _show_panel(interaction, ticket, cfg)


# ── pickers (ephemeral select menus) ──────────────

class _TicketAddUserSelect(discord.ui.UserSelect):
    def __init__(self, placeholder: Optional[str] = None):
        super().__init__(
            custom_id=_TICKET_SEL_ADD_ID,
            placeholder=placeholder or "Choose user(s)…",
            min_values=1, max_values=5,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        added: list = []
        for member in self.values:
            if await _member_has_access(interaction.channel, member):
                continue
            try:
                await interaction.channel.set_permissions(
                    member,
                    read_messages=True, send_messages=True,
                    attach_files=True, embed_links=True,
                    reason=f"Added by {interaction.user}",
                )
                added.append(member)
            except Exception:
                continue
        if not added:
            confirm = msg(interaction, "no_users_added")
        else:
            confirm = msg(
                interaction, "users_added",
                users=", ".join(m.mention for m in added),
            )
        await _show_panel(interaction, ticket, cfg, confirm=confirm)


class _TicketRemoveUserSelect(discord.ui.Select):
    def __init__(self, options: list, placeholder: Optional[str] = None):
        super().__init__(
            custom_id=_TICKET_SEL_REMOVE_ID,
            placeholder=placeholder or "Choose user(s)…",
            options=options,
            min_values=1, max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        removed: list = []
        for uid_str in self.values:
            target = interaction.guild.get_member(int(uid_str)) or discord.Object(id=int(uid_str))
            try:
                await interaction.channel.set_permissions(
                    target, overwrite=None,
                    reason=f"Removed by {interaction.user}",
                )
                removed.append(f"<@{uid_str}>")
            except Exception:
                continue
        if not removed:
            confirm = msg(interaction, "no_users_removed")
        else:
            confirm = msg(interaction, "users_removed", users=", ".join(removed))
        await _show_panel(interaction, ticket, cfg, confirm=confirm)


class _TicketTransferUserSelect(discord.ui.UserSelect):
    def __init__(self, placeholder: Optional[str] = None):
        super().__init__(
            custom_id=_TICKET_SEL_TRANSFER_ID,
            placeholder=placeholder or "Choose a support member…",
            min_values=1, max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        target = self.values[0]
        if not has_support_perms(target, cfg):
            return await _show_panel(
                interaction, ticket, cfg,
                confirm=msg(interaction, "not_support_target", user=target.mention),
            )
        ticket["claimed_by"] = target.id
        await _persist_and_refresh(interaction, cfg, ticket)
        await _show_panel(
            interaction, ticket, cfg,
            confirm=msg(interaction, "transferred", user=target.mention),
        )


# ── persistence helper (called from the cog setup) ─

def register_ticket_persistent_views(bot) -> None:
    """Register every persistent custom id used by ticket headers and staff
    panels so the buttons keep working after a bot restart."""
    registry = discord.ui.LayoutView(timeout=None)
    registry.add_item(discord.ui.Container(
        discord.ui.ActionRow(
            StaffPanelButton(),
            _TicketClaimButton(),
            _TicketTransferButton(),
            _TicketCloseButton(),
            _TicketDeleteButton(),
        ),
        discord.ui.ActionRow(
            _TicketAddButton(),
            _TicketRemoveButton(),
            _TicketDeleteYesButton(),
            _TicketCancelButton(),
        ),
        # one select per row — v2 action rows are weight-limited
        discord.ui.ActionRow(_TicketAddUserSelect()),
        discord.ui.ActionRow(
            _TicketRemoveUserSelect(options=[discord.SelectOption(label="\u200b", value="-")])
        ),
        discord.ui.ActionRow(_TicketTransferUserSelect()),
    ))
    bot.add_view(registry)


# ───────────────────────────────────────────────────
#  COG
# ───────────────────────────────────────────────────


__all__ = [k for k in list(globals()) if not k.startswith("__")]
