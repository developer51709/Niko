"""
Server Logging Cog — multi-channel, categorised event logging with
CV2 containers and quick-action buttons.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import discord
from discord.ext import commands
from discord.ui.media_gallery import MediaGalleryItem

from utils import logging
from config import links
from utils.ratelimit import log_channel_limiter
from config.emojis import get_emoji
from .revert import RestoreChannelButton, RestoreRoleButton, RevertChannelButton

# ── Constants ─────────────────────────────────────

LOG_CONFIG_FILE = "data/logging_config.json"

# Each category owns a distinct emoji and accent colour, so a log channel
# carrying several categories is scannable: the icon identifies the category
# before a single word is read. They used to collide (captcha shared
# moderation's icon, channels/invites/roles/voice shared utility, and three
# pairs shared a colour), which made both cues useless.
CATEGORIES: dict[str, dict] = {
    "moderation": {
        "label": "Moderation",
        "description": "Kicks, bans, warns, mutes, unbans, nickname changes",
        "emoji_key": "moderation",
        "color": 0xED4245,
    },
    "automod": {
        "label": "AutoMod",
        "description": "Anti-spam, anti-link, bad words, mass mention, anti-nuke, anti-raid",
        "emoji_key": "automod",
        "color": 0xFEE75C,
    },
    "messages": {
        "label": "Messages",
        "description": "Message deletions, edits, bulk clears and purges",
        "emoji_key": "edit",
        "color": 0x5865F2,
    },
    "channels": {
        "label": "Channels",
        "description": "Channel and thread create/delete, lock/unlock, permission and webhook changes",
        "emoji_key": "utility",
        "color": 0x57F287,
    },
    "members": {
        "label": "Members",
        "description": "Member joins, leaves, role changes, boosts and avatar updates",
        "emoji_key": "welcome",
        "color": 0x9B59B6,
    },
    "captcha": {
        "label": "Captcha",
        "description": "Captcha verifications — passes, failures, and kicks",
        "emoji_key": "verified",
        "color": 0x1ABC9C,
    },
    "invites": {
        "label": "Invites",
        "description": "Invite creation, deletion, and usage tracking",
        "emoji_key": "invite",
        "color": 0xEB459E,
    },
    "roles": {
        "label": "Roles",
        "description": "Role creation, deletion, and permission/name updates",
        "emoji_key": "badge_staff",
        "color": 0xE67E22,
    },
    "server": {
        "label": "Server",
        "description": "Server settings, emoji, sticker, integration and event changes",
        "emoji_key": "settings",
        "color": 0x95A5A6,
    },
    "voice": {
        "label": "Voice",
        "description": "Voice joins, leaves, moves and mute/deafen changes",
        "emoji_key": "music",
        "color": 0x3498DB,
    },
}

# Map log action titles to categories (used by the backward-compat log_action wrapper)
_TITLE_CATEGORY: dict[str, str] = {
    "Kick": "moderation",
    "Ban": "moderation",
    "Unban": "moderation",
    "Warn": "moderation",
    "Clear Warnings": "moderation",
    "Mute": "moderation",
    "Tempmute": "moderation",
    "Unmute": "moderation",
    "Timeout": "moderation",
    "Timeout Removed": "moderation",
    "Nickname Changed": "moderation",
    "Clear": "moderation",
    "Purge": "messages",
    "Lock": "channels",
    "Unlock": "channels",
    "Anti-Spam": "automod",
    "Anti-Link": "automod",
    "Bad Word Filter": "automod",
    "Blocked Words": "automod",
    "AutoMod Settings": "automod",
    "AutoMod Whitelist": "automod",
    "Mass Mention": "automod",
    "NSFW Filter": "automod",
    "User-Installed App Detected": "automod",
    "User-Installed App Action Taken": "automod",
    "Interaction Flood Raid Detected": "automod",
    "Anti-Nuke Triggered": "automod",
    "Anti-Raid Triggered": "automod",
    "Captcha Passed": "captcha",
    "Captcha Failed": "captcha",
    "Captcha Kicked": "captcha",
    "Invite Created": "invites",
    "Invite Deleted": "invites",
    "Invite Used": "invites",
    "Vanity Invite Used": "invites",
    "Unknown Join Method": "invites",
    "Channel Created": "channels",
    "Channel Deleted": "channels",
    "Channel Updated": "channels",
    "Channel Restored": "channels",
    "Channel Reverted": "channels",
    "Channel Permissions Updated": "channels",
    "Thread Created": "channels",
    "Thread Deleted": "channels",
    "Thread Updated": "channels",
    "Webhook Created": "channels",
    "Webhook Deleted": "channels",
    "Webhook Updated": "channels",
    "Pins Updated": "channels",
    "Role Created": "roles",
    "Role Deleted": "roles",
    "Role Updated": "roles",
    "Role Restored": "roles",
    "Server Updated": "server",
    "Emoji Updated": "server",
    "Sticker Updated": "server",
    "Integration Updated": "server",
    "Scheduled Event Created": "server",
    "Scheduled Event Updated": "server",
    "Scheduled Event Deleted": "server",
    "Logging Updated": "server",
    "Member Joined": "members",
    "Member Left": "members",
    "Member Updated": "members",
    "Avatar Updated": "members",
    "Server Avatar Updated": "members",
    "Profile Banner Updated": "members",
    "Username Updated": "members",
    "Member Boosted": "members",
    "Boost Removed": "members",
    "Bulk Messages Deleted": "messages",
    "Message Deleted": "messages",
    "Message Edited": "messages",
    "Discord AutoMod Action": "automod",
    "Voice Join": "voice",
    "Voice Leave": "voice",
    "Voice Move": "voice",
    "Voice State Updated": "voice",
}
# One emoji per log message type. Two entries in a log channel never share an
# icon, so the icon alone tells a moderator what happened, and a new log type
# adds one line here rather than another branch in the view builder. The
# artwork is the generated Lucide set in src/assets/emojis (see
# scripts/build-emoji-icons.mjs); a title that is missing here falls back to its
# category emoji, so an unmapped log type still renders.
LOG_EMOJI_KEYS: dict[str, str] = {
    # Moderation
    "Kick": "log_kick",
    "Ban": "log_ban",
    "Unban": "log_unban",
    "Warn": "log_warn",
    "Clear Warnings": "log_clear_warnings",
    "Mute": "log_mute",
    "Tempmute": "log_tempmute",
    "Unmute": "log_unmute",
    "Nickname Changed": "log_nickname",
    "Timeout": "log_timeout",
    "Timeout Removed": "log_timeout_removed",
    "Clear": "log_clear",
    "Purge": "log_purge",
    # AutoMod
    "Anti-Spam": "log_anti_spam",
    "Anti-Link": "log_anti_link",
    "Bad Word Filter": "log_bad_words",
    # Settings changes rather than filter hits, so they get their own icons: a
    # moderator reading a log channel can tell a config edit from a caught
    # message at a glance.
    "Blocked Words": "notepad",
    "AutoMod Settings": "settings",
    "AutoMod Whitelist": "unlock",
    "Mass Mention": "log_mass_mention",
    "NSFW Filter": "log_nsfw_filter",
    "User-Installed App Detected": "log_app_detected",
    "User-Installed App Action Taken": "log_app_action",
    "Interaction Flood Raid Detected": "log_interaction_flood",
    "Anti-Nuke Triggered": "log_anti_nuke",
    "Anti-Raid Triggered": "log_anti_raid",
    # Messages
    "Message Deleted": "log_message_deleted",
    "Message Edited": "log_message_edited",
    "Bulk Messages Deleted": "broom",
    # Channels
    "Channel Created": "log_channel_created",
    "Channel Deleted": "log_channel_deleted",
    "Channel Updated": "log_channel_updated",
    "Channel Restored": "unhide",
    "Channel Reverted": "arrow_left",
    "Channel Permissions Updated": "lock",
    "Thread Created": "plus",
    "Thread Deleted": "minus",
    "Thread Updated": "edit",
    "Webhook Created": "link",
    "Webhook Deleted": "trash",
    "Webhook Updated": "refresh",
    "Pins Updated": "important",
    "Lock": "log_lock",
    "Unlock": "log_unlock",
    # Members
    "Member Joined": "log_member_join",
    "Member Left": "log_member_leave",
    "Member Updated": "log_member_updated",
    "Avatar Updated": "log_avatar",
    "Server Avatar Updated": "image",
    # A banner is neither a picture attachment nor a name, so it keeps the
    # members category emoji rather than borrowing an icon that means something
    # else in the same list.
    "Username Updated": "user",
    "Member Boosted": "boost",
    "Boost Removed": "star",
    # Captcha
    "Captcha Passed": "log_captcha_passed",
    "Captcha Failed": "log_captcha_failed",
    "Captcha Kicked": "log_captcha_kicked",
    # Invites
    "Invite Created": "log_invite_created",
    "Invite Deleted": "log_invite_deleted",
    "Invite Used": "log_invite_used",
    "Vanity Invite Used": "log_vanity_invite",
    "Unknown Join Method": "log_unknown_join",
    # Roles
    "Role Created": "log_role_created",
    "Role Deleted": "log_role_deleted",
    "Role Updated": "log_role_updated",
    "Role Restored": "rewind",
    # Server
    "Server Updated": "log_server_updated",
    "Emoji Updated": "log_emoji_updated",
    "Sticker Updated": "log_sticker_updated",
    "Integration Updated": "bot",
    "Scheduled Event Created": "reminder",
    "Scheduled Event Updated": "loop",
    "Scheduled Event Deleted": "stop",
    "Logging Updated": "scroll",
    # Voice
    "Voice Join": "log_voice_join",
    "Voice Leave": "log_voice_leave",
    "Voice Move": "log_voice_move",
    "Voice State Updated": "pause",
    # Discord runs its own AutoMod outside Niko, so its actions are reported
    # here rather than performed by this bot.
    "Discord AutoMod Action": "automod",
}

_AUTOMOD_SUBSTRINGS = ("Anti-Nuke", "Anti-Raid", "User-Installed", "Interaction Flood", "Nuke", "Raid")

# Which action titles get quick-action buttons and which button set
_ACTION_BUTTONS: dict[str, list[str]] = {
    "Kick": ["ban"],
    "Ban": ["unban"],
    "Unban": ["ban"],
    "Warn": ["kick", "ban"],
    "Mute": ["unmute"],
    "Tempmute": ["unmute"],
    "Timeout": ["kick", "ban"],
    "Anti-Spam": ["kick", "ban"],
    "Anti-Link": ["kick", "ban"],
    "Bad Word Filter": ["kick", "ban"],
    "Mass Mention": ["kick", "ban"],
    "member_join": ["kick", "ban"],
    "Captcha Failed": ["kick", "ban"],
    "Captcha Kicked": ["ban"],
}
_AUTOMOD_DEFAULT_BUTTONS = ["kick", "ban"]


# ── Config helpers (database-backed; migrated from logging_config.json) ──

LOG_COLLECTION = "logging_config"


def _default_guild_cfg() -> dict:
    return {**{cat: None for cat in CATEGORIES}, "disabled": []}


def _normalize_cfg(raw) -> dict:
    """Coerce a stored config (JSON string or dict) into the full shape."""
    import json as _json

    if isinstance(raw, str):
        try:
            raw = _json.loads(raw)
        except Exception:
            raw = {}
    if not isinstance(raw, dict):
        return _default_guild_cfg()
    cfg = _default_guild_cfg()
    for cat in CATEGORIES:
        cfg[cat] = raw.get(cat)
    disabled = raw.get("disabled") or []
    cfg["disabled"] = [d for d in disabled if d in CATEGORIES]
    return cfg


def _guild_config(data: dict, guild_id: int) -> dict:
    """In-memory shape used by the panel; creates a default entry on demand."""
    gid = str(guild_id)
    if gid not in data:
        data[gid] = _default_guild_cfg()
    else:
        for cat in CATEGORIES:
            data[gid].setdefault(cat, None)
        data[gid].setdefault("disabled", [])
    return data[gid]


def _pool():
    import database as database_module
    return getattr(database_module, "_shared_pool", None)


class LogConfigUnavailable(RuntimeError):
    """Raised when the stored logging config could not be read at all."""


async def _load_log_config(*, raise_on_error: bool = False) -> dict:
    """Load every guild's logging config from the database.

    ``raise_on_error`` lets the live cog tell a failed read from an empty one:
    returning ``{}`` for both used to make a transient database error look like
    "no category configured", so every event was dropped without a trace. The
    dashboard keeps the lenient default because it renders the result.
    """
    pool = _pool()
    data: dict = {}
    if pool is None:
        if raise_on_error:
            raise LogConfigUnavailable("Database pool is not available.")
        return data
    try:
        if pool.db_type == "mongodb":
            async for doc in pool.collection(LOG_COLLECTION).find({}):
                gid = doc.get("guild_id")
                if gid is None:
                    try:
                        gid = int(str(doc.get("_id")))
                    except (TypeError, ValueError):
                        continue
                cfg = {k: v for k, v in doc.items() if k not in ("_id", "guild_id")}
                data[str(gid)] = _normalize_cfg(cfg)
        else:
            rows = await pool.fetch("SELECT guild_id, data FROM logging_config")
            for row in rows:
                data[str(row["guild_id"])] = _normalize_cfg(row["data"])
    except Exception as e:
        from utils import logging
        logging.warning("logging_cog", f"Failed to load logging configs: {e}")
        if raise_on_error:
            raise LogConfigUnavailable(str(e)) from e
    return data


async def _save_guild_log_config(guild_id: int, cfg: dict):
    """Persist one guild's logging config to the database."""
    import json as _json

    pool = _pool()
    if pool is None:
        raise RuntimeError("Database pool is not available.")
    payload = _json.dumps(_normalize_cfg(cfg))
    if pool.db_type == "mongodb":
        await pool.collection(LOG_COLLECTION).replace_one(
            {"_id": str(guild_id)},
            {"_id": str(guild_id), "guild_id": int(guild_id), **_normalize_cfg(cfg)},
            upsert=True,
        )
    else:
        await pool.execute(
            "INSERT OR REPLACE INTO logging_config (guild_id, data) VALUES ($1, $2)",
            int(guild_id), payload,
        )


# ── Quick-action buttons ──────────────────────────

class KickButton(discord.ui.Button):
    def __init__(self, guild_id: int, target_id: int):
        super().__init__(label="Kick", style=discord.ButtonStyle.danger, emoji=get_emoji("log_kick"), row=0)
        self.guild_id = guild_id
        self.target_id = target_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.kick_members:
            return await interaction.response.send_message("You don't have permission to kick members.", ephemeral=True)
        guild = interaction.client.get_guild(self.guild_id)
        if not guild:
            return await interaction.response.send_message("Could not find the server.", ephemeral=True)
        member = guild.get_member(self.target_id)
        if not member:
            return await interaction.response.send_message("Member not found (they may have already left).", ephemeral=True)
        try:
            await member.kick(reason=f"Quick action by {interaction.user}")
            await interaction.response.send_message(f"{get_emoji('tick')} Kicked **{member}**.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to kick that member.", ephemeral=True)


class BanButton(discord.ui.Button):
    def __init__(self, guild_id: int, target_id: int):
        super().__init__(label="Ban", style=discord.ButtonStyle.danger, emoji=get_emoji('ban'), row=0)
        self.guild_id = guild_id
        self.target_id = target_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.ban_members:
            return await interaction.response.send_message("You don't have permission to ban members.", ephemeral=True)
        guild = interaction.client.get_guild(self.guild_id)
        if not guild:
            return await interaction.response.send_message("Could not find the server.", ephemeral=True)
        member = guild.get_member(self.target_id)
        if not member:
            try:
                user = await interaction.client.fetch_user(self.target_id)
                await guild.ban(user, reason=f"Quick action by {interaction.user}")
                await interaction.response.send_message(f"{get_emoji('tick')} Banned **{user}**.", ephemeral=True)
            except Exception:
                await interaction.response.send_message("Could not ban that user.", ephemeral=True)
            return
        try:
            await member.ban(reason=f"Quick action by {interaction.user}")
            await interaction.response.send_message(f"{get_emoji('tick')} Banned **{member}**.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to ban that member.", ephemeral=True)


class UnbanButton(discord.ui.Button):
    def __init__(self, guild_id: int, target_id: int):
        super().__init__(label="Unban", style=discord.ButtonStyle.success, emoji=get_emoji('tick'), row=0)
        self.guild_id = guild_id
        self.target_id = target_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.ban_members:
            return await interaction.response.send_message("You don't have permission to unban members.", ephemeral=True)
        guild = interaction.client.get_guild(self.guild_id)
        if not guild:
            return await interaction.response.send_message("Could not find the server.", ephemeral=True)
        try:
            user = await interaction.client.fetch_user(self.target_id)
            await guild.unban(user, reason=f"Quick action by {interaction.user}")
            await interaction.response.send_message(f"{get_emoji('tick')} Unbanned **{user}**.", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("That user isn't banned.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to unban.", ephemeral=True)


class UnmuteButton(discord.ui.Button):
    def __init__(self, guild_id: int, target_id: int):
        super().__init__(label="Unmute", style=discord.ButtonStyle.success, emoji=get_emoji("log_unmute"), row=0)
        self.guild_id = guild_id
        self.target_id = target_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.moderate_members:
            return await interaction.response.send_message("You don't have permission to unmute members.", ephemeral=True)
        guild = interaction.client.get_guild(self.guild_id)
        if not guild:
            return await interaction.response.send_message("Could not find the server.", ephemeral=True)
        member = guild.get_member(self.target_id)
        if not member:
            return await interaction.response.send_message("Member not found.", ephemeral=True)
        mod_utils = interaction.client.get_cog("ModerationUtils")
        if not mod_utils:
            return await interaction.response.send_message("Moderation system unavailable.", ephemeral=True)
        try:
            await mod_utils.unmute_member(member, reason=f"Quick action by {interaction.user}")
            await interaction.response.send_message(f"{get_emoji('tick')} Unmuted **{member}**.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to unmute: {e}", ephemeral=True)


class UnlockButton(discord.ui.Button):
    def __init__(self, guild_id: int, channel_id: int):
        super().__init__(label="Unlock Channel", style=discord.ButtonStyle.success, emoji=get_emoji('unlock'), row=0)
        self.guild_id = guild_id
        self.channel_id = channel_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("You don't have permission to unlock channels.", ephemeral=True)
        guild = interaction.client.get_guild(self.guild_id)
        if not guild:
            return await interaction.response.send_message("Could not find the server.", ephemeral=True)
        channel = guild.get_channel(self.channel_id)
        if not channel:
            return await interaction.response.send_message("Channel not found.", ephemeral=True)
        try:
            await channel.set_permissions(guild.default_role, send_messages=None, reason=f"Quick action by {interaction.user}")
            await interaction.response.send_message(f"{get_emoji('tick')} Unlocked {channel.mention}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to unlock that channel.", ephemeral=True)


#: A snapshot-carrying button per revertable log type. The snapshot id is all
#: the button stores, so the entry keeps working after a restart.
_REVERT_BUTTONS = {
    "role": RestoreRoleButton,
    "channel": RestoreChannelButton,
    "channel-update": RevertChannelButton,
}


def _build_action_buttons(action_key: str, guild_id: int, target_id: int | None, channel_id: int | None = None,
                          revert: tuple[str, str] | None = None) -> list[discord.ui.Button]:
    btns: list[discord.ui.Button] = []
    # The revert button reads first: undoing the event beats acting on the person
    # or channel afterwards, and it is the reason the entry is actionable.
    if revert:
        builder = _REVERT_BUTTONS.get(revert[0])
        if builder is not None:
            btns.append(builder(revert[1]))
    wanted = _ACTION_BUTTONS.get(action_key, [])
    if not wanted and any(s in action_key for s in _AUTOMOD_SUBSTRINGS):
        wanted = _AUTOMOD_DEFAULT_BUTTONS
    for b in wanted:
        if b == "kick" and target_id:
            btns.append(KickButton(guild_id, target_id))
        elif b == "ban" and target_id:
            btns.append(BanButton(guild_id, target_id))
        elif b == "unban" and target_id:
            btns.append(UnbanButton(guild_id, target_id))
        elif b == "unmute" and target_id:
            btns.append(UnmuteButton(guild_id, target_id))
        elif b == "unlock" and channel_id:
            btns.append(UnlockButton(guild_id, channel_id))
    return btns


# ── Log entry view builder ────────────────────────

def _build_log_view(
    category: str,
    title: str,
    body: str,
    guild_id: int,
    target_id: int | None = None,
    action_key: str | None = None,
    channel_id: int | None = None,
    media_urls: list[str | tuple[str, str]] | None = None,
    thumbnail_url: str | None = None,
    files: list[discord.File] | None = None,
    file_components: bool = True,
    revert: tuple[str, str] | None = None,
) -> discord.ui.LayoutView:
    cat_info = CATEGORIES.get(category, CATEGORIES["moderation"])
    color = discord.Colour(cat_info["color"])
    # discord timestamp types
    # relative: <t:1711234567:R> → "2 months ago"
    # full: <t:1711234567:F> → "March 23, 2024 12:36 AM"
    # The footer names the category: servers commonly point several categories
    # at one channel, and a bare timestamp left the reader guessing which
    # category had fired.
    timestamp = (
        f"-# {cat_info['label']} • <t:{int(datetime.now(timezone.utc).timestamp())}:F>\n"
        f"-# <t:{int(datetime.now(timezone.utc).timestamp())}:R>"
    )
    # The message type's own emoji, keyed by the title the caller logged (the
    # action key too, for the callers that pass a shorter one such as
    # "member_join"). A type without an entry keeps its category emoji.
    emoji = get_emoji(LOG_EMOJI_KEYS.get(title) or LOG_EMOJI_KEYS.get(action_key or ""))
    if not emoji:
        emoji = get_emoji(cat_info["emoji_key"])

    buttons = _build_action_buttons(
        action_key or title, guild_id, target_id, channel_id, revert)

    children: list[discord.ui.Item] = [
        discord.ui.TextDisplay(content=f"### {emoji} {title}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
    ]

    if thumbnail_url:
        # Member avatar changes render the body in a section with the new pfp
        # as a thumbnail accessory.
        children.append(
            discord.ui.Section(
                discord.ui.TextDisplay(content=body),
                accessory=discord.ui.Thumbnail(thumbnail_url),
            )
        )
    else:
        children.append(discord.ui.TextDisplay(content=body))

    children.append(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))

    if media_urls:
        # Deleted-message image attachments render inline in a media gallery; a
        # re-uploaded asset (a replaced avatar) passes its attachment URI with a
        # caption saying which side of the change it is. Discord caps a gallery
        # at ten items, so a mass delete of images cannot make the send fail.
        items = []
        for entry in media_urls[:10]:
            url, caption = entry if isinstance(entry, (tuple, list)) else (entry, None)
            if caption:
                items.append(MediaGalleryItem(media=url, description=str(caption)[:256]))
            else:
                items.append(MediaGalleryItem(media=url))
        children.append(discord.ui.MediaGallery(*items))
        children.append(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))

    if files and file_components:
        # Deleted-message file attachments render inline as file components.
        # The bytes are uploaded via send(files=...) — the components reference
        # them through their attachment:// URI.
        for f in files:
            children.append(discord.ui.File(media=f))
        children.append(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))

    children.append(discord.ui.TextDisplay(content=timestamp))

    container = discord.ui.Container(*children, accent_colour=color)

    if buttons:
        container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        button_row = discord.ui.ActionRow()
        for btn in buttons:
            button_row.add_item(btn)
        container.add_item(button_row)

    view = discord.ui.LayoutView(timeout=None)
    view.add_item(container)
    return view


# ── Settings Panel ────────────────────────────────

# The panel is rebuilt after every click, so it only has to outlive a single
# configuration session. Expiring it means a message left in a channel never
# sits there with components that quietly stopped working after a restart.
PANEL_TIMEOUT = 300.0

MESSAGES: dict[str, dict[str, str]] = {
    "en": {
        "panel_title":        "Server Logging",
        "panel_desc":         "Pick a category below, then set, clear or toggle its channel. Each category can go to its own channel.",
        "panel_selected":     "**Configuring:** {category}",
        "panel_unselected":   "**Configuring:** nothing yet — pick a category below.",
        "select_placeholder": "Select a category to configure…",
        "opt_set":            "Channel set",
        "opt_unset":          "No channel",
        "opt_off":            "Disabled",
        "btn_set_channel":    "Set Channel",
        "btn_clear_channel":  "Clear Channel",
        "btn_toggle":         "Enable / Disable",
        "btn_set_all":        "Set All → This Channel",
        "btn_clear_all":      "Clear All Channels",
        "invoker_only":       "{cross} Only the person who opened this panel can use it.",
        "no_permission":      "{cross} You need **Manage Server** to change logging settings.",
        "no_category":        "{cross} Pick a category from the dropdown first.",
        "channel_saved":      "{tick} **{category}** logs → {channel}",
        "channel_cleared":    "{cross} Cleared the channel for **{category}** logs.",
        "toggled_on":         "{tick} **{category}** logging enabled.",
        "toggled_off":        "{cross} **{category}** logging disabled.",
        "all_set":            "{tick} Every category now logs to {channel}.",
        "all_cleared":        "{cross} Cleared every logging channel.",
        "save_failed":        "{cross} The change could not be saved: {error}",
        "confirm_set_all":    "Send **all {count} categories** to {channel}? Existing channels are replaced.",
        "confirm_clear_all":  "Remove the channel from **every category**? Logging stops until you set one again.",
        "confirm_yes":        "Yes, apply",
        "confirm_no":         "Cancel",
        "cancelled":          "{cross} Nothing was changed.",
        "expired_title":      "### {settings} Logging panel expired",
        "expired_body":       "Open it again with `.logging` to keep configuring. Nothing was changed.",
        "picker_title":       "Select a channel for **{category}**",
        "picker_placeholder": "Select a channel…",
        "picker_save":        "Save Channel",
        "picker_no_channel":  "{cross} Select a channel first.",
        "status_title":       "Logging Status",
        "status_not_set":     "`Not set`",
        "status_hint":        "Run `.logging` to change these channels.",
    },
    "de": {
        "panel_title":        "Server-Logging",
        "panel_desc":         "Wähle unten eine Kategorie und setze, lösche oder schalte ihren Kanal. Jede Kategorie kann einen eigenen Kanal haben.",
        "panel_selected":     "**Ausgewählt:** {category}",
        "panel_unselected":   "**Ausgewählt:** noch nichts — wähle unten eine Kategorie.",
        "select_placeholder": "Kategorie zum Einrichten wählen…",
        "opt_set":            "Kanal gesetzt",
        "opt_unset":          "Kein Kanal",
        "opt_off":            "Deaktiviert",
        "btn_set_channel":    "Kanal setzen",
        "btn_clear_channel":  "Kanal entfernen",
        "btn_toggle":         "Ein / Aus",
        "btn_set_all":        "Alle → dieser Kanal",
        "btn_clear_all":      "Alle Kanäle leeren",
        "invoker_only":       "{cross} Nur die Person, die dieses Panel geöffnet hat, kann es benutzen.",
        "no_permission":      "{cross} Du brauchst **Server verwalten**, um die Log-Einstellungen zu ändern.",
        "no_category":        "{cross} Wähle zuerst eine Kategorie aus dem Menü.",
        "channel_saved":      "{tick} **{category}**-Logs → {channel}",
        "channel_cleared":    "{cross} Kanal für **{category}**-Logs entfernt.",
        "toggled_on":         "{tick} **{category}**-Logging aktiviert.",
        "toggled_off":        "{cross} **{category}**-Logging deaktiviert.",
        "all_set":            "{tick} Alle Kategorien loggen jetzt in {channel}.",
        "all_cleared":        "{cross} Alle Log-Kanäle entfernt.",
        "save_failed":        "{cross} Die Änderung konnte nicht gespeichert werden: {error}",
        "confirm_set_all":    "**Alle {count} Kategorien** in {channel} senden? Bestehende Kanäle werden ersetzt.",
        "confirm_clear_all":  "Den Kanal aus **allen Kategorien** entfernen? Bis du wieder einen setzt, wird nichts geloggt.",
        "confirm_yes":        "Ja, anwenden",
        "confirm_no":         "Abbrechen",
        "cancelled":          "{cross} Es wurde nichts geändert.",
        "expired_title":      "### {settings} Logging-Panel abgelaufen",
        "expired_body":       "Öffne es mit `.logging` erneut, um weiter einzurichten. Es wurde nichts geändert.",
        "picker_title":       "Kanal für **{category}** wählen",
        "picker_placeholder": "Kanal wählen…",
        "picker_save":        "Kanal speichern",
        "picker_no_channel":  "{cross} Wähle zuerst einen Kanal.",
        "status_title":       "Logging-Status",
        "status_not_set":     "`Nicht gesetzt`",
        "status_hint":        "Nutze `.logging`, um diese Kanäle zu ändern.",
    },
    "es": {
        "panel_title":        "Registro del servidor",
        "panel_desc":         "Elige una categoría abajo y define, borra o activa su canal. Cada categoría puede tener su propio canal.",
        "panel_selected":     "**Configurando:** {category}",
        "panel_unselected":   "**Configurando:** nada todavía — elige una categoría abajo.",
        "select_placeholder": "Elige una categoría para configurar…",
        "opt_set":            "Canal definido",
        "opt_unset":          "Sin canal",
        "opt_off":            "Desactivado",
        "btn_set_channel":    "Definir canal",
        "btn_clear_channel":  "Borrar canal",
        "btn_toggle":         "Activar / Desactivar",
        "btn_set_all":        "Todos → este canal",
        "btn_clear_all":      "Borrar todos los canales",
        "invoker_only":       "{cross} Solo quien abrió este panel puede usarlo.",
        "no_permission":      "{cross} Necesitas **Gestionar servidor** para cambiar el registro.",
        "no_category":        "{cross} Elige primero una categoría del menú.",
        "channel_saved":      "{tick} Registro de **{category}** → {channel}",
        "channel_cleared":    "{cross} Canal borrado para el registro de **{category}**.",
        "toggled_on":         "{tick} Registro de **{category}** activado.",
        "toggled_off":        "{cross} Registro de **{category}** desactivado.",
        "all_set":            "{tick} Todas las categorías se registran ahora en {channel}.",
        "all_cleared":        "{cross} Se borraron todos los canales de registro.",
        "save_failed":        "{cross} No se pudo guardar el cambio: {error}",
        "confirm_set_all":    "¿Enviar **las {count} categorías** a {channel}? Se reemplazan los canales actuales.",
        "confirm_clear_all":  "¿Quitar el canal de **todas las categorías**? Hasta que definas uno no se registrará nada.",
        "confirm_yes":        "Sí, aplicar",
        "confirm_no":         "Cancelar",
        "cancelled":          "{cross} No se cambió nada.",
        "expired_title":      "### {settings} El panel de registro caducó",
        "expired_body":       "Ábrelo de nuevo con `.logging` para seguir configurando. No se cambió nada.",
        "picker_title":       "Elige un canal para **{category}**",
        "picker_placeholder": "Elige un canal…",
        "picker_save":        "Guardar canal",
        "picker_no_channel":  "{cross} Elige primero un canal.",
        "status_title":       "Estado del registro",
        "status_not_set":     "`Sin definir`",
        "status_hint":        "Usa `.logging` para cambiar estos canales.",
    },
}


def _t(lang: str, key: str, **kwargs) -> str:
    """Look up a panel string, filling in the bot's emojis and any kwargs."""
    text = MESSAGES.get(lang, {}).get(key) or MESSAGES["en"].get(key, key)
    return text.format(
        tick=get_emoji("tick"), cross=get_emoji("cross"),
        settings=get_emoji("settings"), **kwargs,
    )


def _panel_lang(guild) -> str:
    """The panel's language, from the guild locale."""
    locale = str(getattr(guild, "preferred_locale", None) or "").lower()
    if locale.startswith("de"):
        return "de"
    if locale.startswith("es"):
        return "es"
    return "en"


def _may_manage(interaction: discord.Interaction) -> bool:
    """Manage Server, the same permission `/logging` itself requires."""
    permissions = getattr(interaction.user, "guild_permissions", None)
    return bool(permissions is not None and getattr(permissions, "manage_guild", False))


def _notice(text: str) -> discord.ui.LayoutView:
    """A one-line LayoutView with no accent colour and no components."""
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return view


def _expired_view(lang: str) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=_t(lang, "expired_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=_t(lang, "expired_body")),
    ))
    return view


async def _refuse(interaction: discord.Interaction, text: str):
    return await interaction.response.send_message(view=_notice(text), ephemeral=True)


async def _guard(interaction: discord.Interaction, invoker_id: int, lang: str) -> bool:
    """The panel's single gate: the invoker, and Manage Server *now*.

    Every callback used to repeat an invoker check and none re-checked the
    permission, so a member who lost Manage Server could keep editing logging.
    """
    if interaction.user.id != invoker_id:
        await _refuse(interaction, _t(lang, "invoker_only"))
        return False
    if not _may_manage(interaction):
        await _refuse(interaction, _t(lang, "no_permission"))
        return False
    return True


async def _load_cfg(cog) -> dict:
    """The logging config, through the cog's cache when there is one."""
    if cog is not None:
        try:
            return dict(await cog.config())
        except Exception:
            return {}
    return await _load_log_config()


async def _save_cfg(guild, cfg: dict, cog, *, actor=None, summary: str = "",
                   before: dict | None = None):
    """Persist a change, invalidate the cache and audit it.

    The audit entry goes to the channels that were configured *before* the
    change, so redirecting or clearing a category cannot hide the change from
    the people watching the old channel.
    """
    if cog is not None:
        await cog.save_config(guild, cfg, actor=actor, summary=summary, before=before)
    else:
        await _save_guild_log_config(guild.id, cfg)


async def _apply_all(interaction: discord.Interaction, *, guild_id: int, cog, lang: str,
                     category: str | None, panel_message, channel_id: int | None):
    """Point every category at one channel (or clear them all).

    Shared by the two bulk actions, both of which now sit behind an ephemeral
    confirmation: they used to apply ten silent changes in one click, and the
    rebuild afterwards read a loop variable instead of the user's selection.
    """
    data = await _load_cfg(cog)
    cfg = _guild_config(data, guild_id)
    before = dict(cfg)
    for key in CATEGORIES:
        cfg[key] = channel_id
    try:
        await _save_cfg(
            interaction.guild, cfg, cog, actor=interaction.user,
            summary=("every category → this channel" if channel_id
                     else "every category cleared"),
            before=before,
        )
    except Exception as error:
        return await interaction.response.edit_message(
            view=_notice(_t(lang, "save_failed", error=error)))
    await interaction.response.edit_message(view=_notice(_t(
        lang,
        "all_set" if channel_id else "all_cleared",
        channel=getattr(interaction.channel, "mention", "") if channel_id else "",
    )))
    if panel_message is not None:
        try:
            await panel_message.edit(view=LoggingSetupView(
                guild_id, interaction.user, category,
                await _load_cfg(cog), cog, lang))
        except discord.HTTPException:
            pass


class _ConfirmYes(discord.ui.Button):
    def __init__(self, view: "LoggingConfirmView"):
        super().__init__(label=_t(view.lang, "confirm_yes"),
                         style=discord.ButtonStyle.danger, emoji=get_emoji("tick"))
        self._view = view

    async def callback(self, interaction: discord.Interaction):
        view = self._view
        if not await _guard(interaction, view.invoker_id, view.lang):
            return
        view.stop()
        await view.apply_action(interaction)


class _ConfirmNo(discord.ui.Button):
    def __init__(self, view: "LoggingConfirmView"):
        super().__init__(label=_t(view.lang, "confirm_no"),
                         style=discord.ButtonStyle.secondary, emoji=get_emoji("cross"))
        self._view = view

    async def callback(self, interaction: discord.Interaction):
        view = self._view
        if not await _guard(interaction, view.invoker_id, view.lang):
            return
        view.stop()
        await interaction.response.edit_message(view=_notice(_t(view.lang, "cancelled")))


class LoggingConfirmView(discord.ui.LayoutView):
    """Ephemeral yes/no gate for the panel's two bulk actions."""

    def __init__(self, prompt: str, *, invoker_id: int, lang: str, apply_action):
        super().__init__(timeout=60)
        self.invoker_id = invoker_id
        self.lang = lang
        self.apply_action = apply_action
        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=prompt),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(_ConfirmYes(self), _ConfirmNo(self)),
        ))


class SelectChannelView(discord.ui.LayoutView):
    """Ephemeral channel picker for one category."""

    def __init__(self, guild_id: int, category: str, author, panel_message,
                 cog=None, lang: str | None = None):
        effective_lang = lang or _panel_lang(getattr(author, "guild", None))
        super().__init__(timeout=PANEL_TIMEOUT)
        self.guild_id = guild_id
        self.category = category
        self.author = author
        self.invoker_id = author.id
        self.panel_message = panel_message
        self.cog = cog
        self.lang = effective_lang
        self.selected_channel: int | None = None

        # --- COMPONENTS ---

        class _ChannelSelect(discord.ui.ChannelSelect):
            def __init__(s):
                super().__init__(
                    channel_types=[discord.ChannelType.text],
                    placeholder=_t(effective_lang, "picker_placeholder"),
                    min_values=1,
                    max_values=1
                )

            async def callback(s, interaction: discord.Interaction):
                if not await _guard(interaction, self.invoker_id, effective_lang):
                    return
                self.selected_channel = s.values[0].id
                await interaction.response.defer()

        class _SaveBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(
                    label=_t(effective_lang, "picker_save"),
                    style=discord.ButtonStyle.primary,
                    emoji=get_emoji("tick")
                )

            async def callback(s, interaction: discord.Interaction):
                if not await _guard(interaction, self.invoker_id, effective_lang):
                    return
                if not self.selected_channel:
                    return await _refuse(
                        interaction, _t(effective_lang, "picker_no_channel"))

                d = await _load_cfg(cog)
                gc = _guild_config(d, guild_id)
                before = dict(gc)
                gc[self.category] = self.selected_channel
                label = CATEGORIES[self.category]["label"]
                try:
                    await _save_cfg(
                        interaction.guild, gc, cog,
                        actor=interaction.user,
                        summary=f"{label} → <#{self.selected_channel}>",
                        before=before,
                    )
                except Exception as error:
                    return await _refuse(
                        interaction, _t(effective_lang, "save_failed", error=error))

                await interaction.response.edit_message(view=_notice(_t(
                    effective_lang, "channel_saved",
                    category=label, channel=f"<#{self.selected_channel}>")))

                # Return to main panel
                if panel_message is not None:
                    try:
                        await panel_message.edit(view=LoggingSetupView(
                            guild_id, interaction.user, self.category,
                            await _load_cfg(cog), cog, effective_lang,
                        ), allowed_mentions=discord.AllowedMentions.none())
                    except discord.HTTPException:
                        pass

        # --- BUILD CONTAINER ---

        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"### {get_emoji('settings')} "
                    + _t(effective_lang, "picker_title",
                         category=CATEGORIES[category]["label"])
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(_ChannelSelect()),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(_SaveBtn())
        )

        self.add_item(container)
        

class LoggingSetupView(discord.ui.LayoutView):
    """The configuration panel: one message, rebuilt after every change."""

    def __init__(self, guild_id: int, author, category: str | None = None,
                 data: dict | None = None, cog=None, lang: str | None = None,
                 timeout: float = PANEL_TIMEOUT):
        effective_lang = lang or _panel_lang(getattr(author, "guild", None))
        super().__init__(timeout=timeout)
        self.guild_id = guild_id
        self.author = author
        self.invoker_id = author.id
        self.cog = cog
        self.lang = effective_lang
        self.category = category if category in CATEGORIES else None

        if data is None:
            # Fallback to an in-memory default when no config was preloaded;
            # async callers should always pass the freshly loaded config dict.
            data = {}
        cfg = _guild_config(data, guild_id)

        lines = []
        for key, info in CATEGORIES.items():
            ch_id = cfg.get(key)
            ch_text = f"<#{ch_id}>" if ch_id else _t(effective_lang, "status_not_set")
            # `enabled`/`disabled` are two-part toggle graphics; a status line
            # needs one icon, so the panel uses the plain tick/cross pair.
            disabled = key in cfg.get("disabled", [])
            status = get_emoji("cross") if disabled else get_emoji("tick")
            lines.append(f"{status} **{info['label']}** — {ch_text}")
        summary = "\n".join(lines)
        icon = get_emoji("settings")
        # The panel used to keep its selection in a closure, so nothing on the
        # message said which category the buttons would act on.
        selected = (
            _t(effective_lang, "panel_selected",
               category=CATEGORIES[self.category]["label"])
            if self.category
            else _t(effective_lang, "panel_unselected")
        )

        # The dropdown doubles as the state display: its icon says whether a
        # channel is set, so the summary and the menu never disagree.
        select_options = []
        for key, info in CATEGORIES.items():
            ch_id = cfg.get(key)
            disabled = key in cfg.get("disabled", [])
            description = _t(effective_lang, "opt_set" if ch_id else "opt_unset")
            if disabled:
                description = f"{description} · {_t(effective_lang, 'opt_off')}"
            select_options.append(discord.SelectOption(
                label=info["label"],
                description=description,
                value=key,
                emoji=(
                    get_emoji("tick") if ch_id and not disabled
                    else get_emoji("cross")
                ),
                default=(key == self.category),
            ))

        class _CategorySelect(discord.ui.Select):
            def __init__(s):
                super().__init__(
                    placeholder=_t(effective_lang, "select_placeholder"),
                    options=select_options,
                    min_values=1,
                    max_values=1,
                )

            async def callback(s, interaction: discord.Interaction):
                if not await _guard(interaction, self.invoker_id, effective_lang):
                    return
                # Re-render the panel itself, so the selection is visible and
                # the buttons act on what the message says they act on.
                await interaction.response.edit_message(
                    view=LoggingSetupView(
                        guild_id, interaction.user, s.values[0],
                        await _load_cfg(cog), cog, effective_lang),
                    allowed_mentions=discord.AllowedMentions.none(),
                )

        class _SetChannelBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(
                    label=_t(effective_lang, "btn_set_channel"),
                    style=discord.ButtonStyle.primary,
                    emoji=get_emoji("plus")
                )
                s._author = author
                s._guild_id = guild_id

            async def callback(s, interaction: discord.Interaction):
                if not await _guard(interaction, self.invoker_id, effective_lang):
                    return
                cat = self.category
                if not cat:
                    return await _refuse(
                        interaction, _t(effective_lang, "no_category"))

                # get the settings panel message
                panel_message = interaction.message
                await interaction.response.send_message(
                    view=SelectChannelView(
                        s._guild_id, cat, s._author, panel_message,
                        cog, effective_lang),
                    ephemeral=True
                )

        class _ClearChannelBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(label=_t(effective_lang, "btn_clear_channel"),
                                 style=discord.ButtonStyle.secondary,
                                 emoji=get_emoji("cross"))
                s._author = author
                s._guild_id = guild_id

            async def callback(s, interaction: discord.Interaction):
                if not await _guard(interaction, self.invoker_id, effective_lang):
                    return
                cat = self.category
                if not cat:
                    return await _refuse(
                        interaction, _t(effective_lang, "no_category"))
                d = await _load_cfg(cog)
                gc = _guild_config(d, s._guild_id)
                before = dict(gc)
                gc[cat] = None
                label = CATEGORIES[cat]["label"]
                try:
                    await _save_cfg(
                        interaction.guild, gc, cog, actor=interaction.user,
                        summary=f"{label} → cleared", before=before)
                except Exception as error:
                    return await _refuse(
                        interaction, _t(effective_lang, "save_failed", error=error))
                await interaction.response.edit_message(
                    view=_notice(_t(effective_lang, "channel_cleared", category=label)))
                # update the panel
                try:
                    await interaction.message.edit(view=LoggingSetupView(
                        s._guild_id, interaction.user, cat,
                        await _load_cfg(cog), cog, effective_lang))
                except discord.HTTPException:
                    pass

        class _ToggleBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(label=_t(effective_lang, "btn_toggle"),
                                 style=discord.ButtonStyle.secondary,
                                 emoji=get_emoji('refresh'))
                s._author = author
                s._guild_id = guild_id

            async def callback(s, interaction: discord.Interaction):
                if not await _guard(interaction, self.invoker_id, effective_lang):
                    return
                cat = self.category
                if not cat:
                    return await _refuse(
                        interaction, _t(effective_lang, "no_category"))
                d = await _load_cfg(cog)
                gc = _guild_config(d, s._guild_id)
                before = dict(gc)
                dis = gc.setdefault("disabled", [])
                if cat in dis:
                    dis.remove(cat)
                    state_key = "toggled_on"
                else:
                    dis.append(cat)
                    state_key = "toggled_off"
                label = CATEGORIES[cat]["label"]
                try:
                    await _save_cfg(
                        interaction.guild, gc, cog, actor=interaction.user,
                        summary=f"{label} → {state_key}", before=before)
                except Exception as error:
                    return await _refuse(
                        interaction, _t(effective_lang, "save_failed", error=error))
                await interaction.response.edit_message(
                    view=_notice(_t(effective_lang, state_key, category=label)))
                # update the panel
                try:
                    await interaction.message.edit(view=LoggingSetupView(
                        s._guild_id, interaction.user, cat,
                        await _load_cfg(cog), cog, effective_lang))
                except discord.HTTPException:
                    pass

        class _SetAllBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(label=_t(effective_lang, "btn_set_all"),
                                 style=discord.ButtonStyle.secondary,
                                 emoji=get_emoji("megaphone"))
                s._author = author
                s._guild_id = guild_id

            async def callback(s, interaction: discord.Interaction):
                if not await _guard(interaction, s._author.id, effective_lang):
                    return
                channel = interaction.channel
                await interaction.response.send_message(
                    view=LoggingConfirmView(
                        _t(effective_lang, "confirm_set_all",
                           count=len(CATEGORIES),
                           channel=getattr(channel, "mention", "this channel")),
                        invoker_id=self.invoker_id, lang=effective_lang,
                        apply_action=lambda i: _apply_all(
                            i, guild_id=guild_id, cog=cog, lang=effective_lang,
                            category=self.category,
                            panel_message=interaction.message, channel_id=channel.id),
                    ),
                    ephemeral=True,
                )

        class _ClearAllBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(label=_t(effective_lang, "btn_clear_all"),
                                 style=discord.ButtonStyle.danger,
                                 emoji=get_emoji('trash'))
                s._author = author
                s._guild_id = guild_id

            async def callback(s, interaction: discord.Interaction):
                if not await _guard(interaction, s._author.id, effective_lang):
                    return
                await interaction.response.send_message(
                    view=LoggingConfirmView(
                        _t(effective_lang, "confirm_clear_all"),
                        invoker_id=self.invoker_id, lang=effective_lang,
                        apply_action=lambda i: _apply_all(
                            i, guild_id=guild_id, cog=cog, lang=effective_lang,
                            category=self.category,
                            panel_message=interaction.message, channel_id=None),
                    ),
                    ephemeral=True,
                )

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {icon} {_t(effective_lang, 'panel_title')}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=_t(effective_lang, "panel_desc")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=summary),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(_CategorySelect()),
            discord.ui.TextDisplay(content=selected),
            discord.ui.ActionRow(_SetChannelBtn(), _ClearChannelBtn(), _ToggleBtn()),
            discord.ui.ActionRow(_SetAllBtn(), _ClearAllBtn()),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"-# **Need help?** Ask in the [support server]({links.SUPPORT_SERVER}) or check the [documentation]({links.DOCS})"
            ),
        )
        self.add_item(container)

    async def on_timeout(self):
        """Replace the components so the panel never keeps dead buttons."""
        try:
            if self.message is not None:
                await self.message.edit(view=_expired_view(self.lang))
        except discord.HTTPException:
            pass


# ── Main Cog ──────────────────────────────────────


__all__ = [k for k in list(globals()) if not k.startswith("__")]
