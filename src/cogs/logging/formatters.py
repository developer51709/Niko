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

from utils import logging
from config import links
from utils.ratelimit import log_channel_limiter
from config.emojis import get_emoji

# ── Constants ─────────────────────────────────────

LOG_CONFIG_FILE = "data/logging_config.json"

CATEGORIES: dict[str, dict] = {
    "moderation": {
        "label": "Moderation",
        "description": "Kicks, bans, warns, mutes, unbans, nickname changes",
        "emoji_key": "icon_moderation",
        "color": 0xED4245,
    },
    "automod": {
        "label": "AutoMod",
        "description": "Anti-spam, anti-link, bad words, mass mention, anti-nuke, anti-raid",
        "emoji_key": "icon_automod",
        "color": 0xFEE75C,
    },
    "messages": {
        "label": "Messages",
        "description": "Message deletions, edits, bulk clears and purges",
        "emoji_key": "icon_edit",
        "color": 0x5865F2,
    },
    "channels": {
        "label": "Channels",
        "description": "Channel lock/unlock, channel create/delete",
        "emoji_key": "icon_utility",
        "color": 0x57F287,
    },
    "members": {
        "label": "Members",
        "description": "Member joins, leaves and role changes",
        "emoji_key": "icon_welcome",
        "color": 0x9B59B6,
    },
    "captcha": {
        "label": "Captcha",
        "description": "Captcha verifications — passes, failures, and kicks",
        "emoji_key": "icon_moderation",
        "color": 0x57F287,
    },
    "invites": {
        "label": "Invites",
        "description": "Invite creation, deletion, and usage tracking",
        "emoji_key": "icon_utility",
        "color": 0x5865F2,
    },
    "roles": {
        "label": "Roles",
        "description": "Role creation, deletion, and permission/name updates",
        "emoji_key": "icon_utility",
        "color": 0xFEE75C,
    },
    "server": {
        "label": "Server",
        "description": "Server settings, emoji, and sticker changes",
        "emoji_key": "icon_settings",
        "color": 0xEB459E,
    },
    "voice": {
        "label": "Voice",
        "description": "Voice channel joins, leaves, and moves",
        "emoji_key": "icon_utility",
        "color": 0x1ABC9C,
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
    "Mass Mention": "automod",
    "Captcha Passed": "captcha",
    "Captcha Failed": "captcha",
    "Captcha Kicked": "captcha",
    "Invite Created": "invites",
    "Invite Deleted": "invites",
    "Invite Used": "invites",
    "Channel Updated": "channels",
    "Role Created": "roles",
    "Role Deleted": "roles",
    "Role Updated": "roles",
    "Server Updated": "server",
    "Emoji Updated": "server",
    "Sticker Updated": "server",
    "Voice Join": "voice",
    "Voice Leave": "voice",
    "Voice Move": "voice",
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


# ── Config helpers ────────────────────────────────

def _load_log_config() -> dict:
    if not os.path.exists(LOG_CONFIG_FILE):
        return {}
    try:
        with open(LOG_CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_log_config(data: dict):
    os.makedirs("data", exist_ok=True)
    with open(LOG_CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


def _guild_config(data: dict, guild_id: int) -> dict:
    gid = str(guild_id)
    if gid not in data:
        data[gid] = {cat: None for cat in CATEGORIES}
        data[gid]["disabled"] = []
    else:
        for cat in CATEGORIES:
            data[gid].setdefault(cat, None)
        data[gid].setdefault("disabled", [])
    return data[gid]


# ── Quick-action buttons ──────────────────────────

class KickButton(discord.ui.Button):
    def __init__(self, guild_id: int, target_id: int):
        super().__init__(label="Kick", style=discord.ButtonStyle.danger, emoji="👢", row=0)
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
            await interaction.response.send_message(f"{get_emoji('icon_tick')} Kicked **{member}**.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to kick that member.", ephemeral=True)


class BanButton(discord.ui.Button):
    def __init__(self, guild_id: int, target_id: int):
        super().__init__(label="Ban", style=discord.ButtonStyle.danger, emoji=get_emoji('icon_ban'), row=0)
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
                await interaction.response.send_message(f"{get_emoji('icon_tick')} Banned **{user}**.", ephemeral=True)
            except Exception:
                await interaction.response.send_message("Could not ban that user.", ephemeral=True)
            return
        try:
            await member.ban(reason=f"Quick action by {interaction.user}")
            await interaction.response.send_message(f"{get_emoji('icon_tick')} Banned **{member}**.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to ban that member.", ephemeral=True)


class UnbanButton(discord.ui.Button):
    def __init__(self, guild_id: int, target_id: int):
        super().__init__(label="Unban", style=discord.ButtonStyle.success, emoji=get_emoji('icon_tick'), row=0)
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
            await interaction.response.send_message(f"{get_emoji('icon_tick')} Unbanned **{user}**.", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("That user isn't banned.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to unban.", ephemeral=True)


class UnmuteButton(discord.ui.Button):
    def __init__(self, guild_id: int, target_id: int):
        super().__init__(label="Unmute", style=discord.ButtonStyle.success, emoji="🔊", row=0)
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
            await interaction.response.send_message(f"{get_emoji('icon_tick')} Unmuted **{member}**.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to unmute: {e}", ephemeral=True)


class UnlockButton(discord.ui.Button):
    def __init__(self, guild_id: int, channel_id: int):
        super().__init__(label="Unlock Channel", style=discord.ButtonStyle.success, emoji=get_emoji('icon_unlock'), row=0)
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
            await interaction.response.send_message(f"{get_emoji('icon_tick')} Unlocked {channel.mention}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to unlock that channel.", ephemeral=True)


def _build_action_buttons(action_key: str, guild_id: int, target_id: int | None, channel_id: int | None = None) -> list[discord.ui.Button]:
    btns = []
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
) -> discord.ui.LayoutView:
    cat_info = CATEGORIES.get(category, CATEGORIES["moderation"])
    emoji = get_emoji(cat_info["emoji_key"])
    color = discord.Colour(cat_info["color"])
    # discord timestamp types
    # relative: <t:1711234567:R> → "2 months ago"
    # full: <t:1711234567:F> → "March 23, 2024 12:36 AM"
    timestamp = f"-# <t:{int(datetime.now(timezone.utc).timestamp())}:F>\n-# <t:{int(datetime.now(timezone.utc).timestamp())}:R>"
    # set type specific emojis
    if title == "Member Joined":
        emoji = get_emoji("icon_join")
    if title == "Member Left":
        emoji = get_emoji("icon_leave")
    if action_key == "Ban":
        emoji = get_emoji("icon_ban")

    buttons = _build_action_buttons(action_key or title, guild_id, target_id, channel_id)

    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {emoji} {title}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=body),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=timestamp),
        accent_colour=color,
    )

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

class SelectChannelView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, category: str, author: discord.Member, panel_message):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.category = category
        self.author = author
        self.selected_channel: int | None = None

        # --- COMPONENTS ---

        class _ChannelSelect(discord.ui.ChannelSelect):
            def __init__(s):
                super().__init__(
                    channel_types=[discord.ChannelType.text],
                    placeholder="Select a channel…",
                    min_values=1,
                    max_values=1
                )

            async def callback(s, interaction: discord.Interaction):
                if interaction.user != author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} Only the command invoker can use this menu."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(
                        view=view,
                        ephemeral=True
                    )

                ch = s.values[0]
                self.selected_channel = ch.id

                await interaction.response.defer()

        class _SaveBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(
                    label="Save Channel",
                    style=discord.ButtonStyle.primary,
                    emoji=get_emoji("icon_tick")
                )

            async def callback(s, interaction: discord.Interaction):
                if interaction.user != author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} Only the command invoker can use this button."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(
                        view=view,
                        ephemeral=True
                    )

                if not self.selected_channel:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} Please select a channel first."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)

                d = _load_log_config()
                gc = _guild_config(d, guild_id)
                gc[self.category] = self.selected_channel
                _save_log_config(d)

                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_tick')} **{CATEGORIES[self.category]['label']}** logs → <#{self.selected_channel}>"
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await interaction.response.edit_message(view=view)

                # Return to main panel
                await panel_message.edit(
                    view=LoggingSetupView(guild_id, author, self.category)
                )

        # --- BUILD CONTAINER ---

        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_settings')} Select a channel for **{CATEGORIES[category]['label']}**"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(_ChannelSelect()),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(_SaveBtn())
        )

        self.add_item(container)
        

class LoggingSetupView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, author: discord.Member, category: str | None = None):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.author = author

        data = _load_log_config()
        cfg = _guild_config(data, guild_id)

        # shared mutable state — the currently-selected category
        _sel: list[str | None] = [None]
        if category and category in CATEGORIES:
            _sel[0] = category

        lines = []
        for key, info in CATEGORIES.items():
            ch_id = cfg.get(key)
            ch_text = f"<#{ch_id}>" if ch_id else "`Not set`"
            disabled = key in cfg.get("disabled", [])
            status = get_emoji("disabled") if disabled else get_emoji("enabled")
            lines.append(f"{status} **{info['label']}** — {ch_text}")
        summary = "\n".join(lines)
        icon = get_emoji("icon_settings")

        # Build select options
        select_options = []
        for key, info in CATEGORIES.items():
            ch_id = cfg.get(key)
            ch_text = f"set" if ch_id else "not set"
            dis_mark = " ✗" if key in cfg.get("disabled", []) else ""
            select_options.append(discord.SelectOption(
                label=f"{info['label']}{dis_mark}",
                description=f"Channel: {ch_text}",
                value=key,
            ))

        class _CategorySelect(discord.ui.Select):
            def __init__(s):
                super().__init__(
                    placeholder="Select a category to configure…",
                    options=select_options,
                    min_values=1,
                    max_values=1,
                )

            async def callback(s, interaction: discord.Interaction):
                _sel[0] = s.values[0]
                label = CATEGORIES[_sel[0]]["label"]
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_settings')} Category **{label}** selected. Now use the buttons below to configure it."
                    )
                )
                view.add_item(container)
                await interaction.response.send_message(
                    view=view,
                    ephemeral=True,
                )

        class _SetChannelBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(
                    label="Set Channel",
                    style=discord.ButtonStyle.primary,
                    emoji=get_emoji("icon_plus")
                )
                s._author = author
                s._guild_id = guild_id

            async def callback(s, interaction: discord.Interaction):
                if interaction.user != s._author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} Only the command invoker can use these button."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(
                        view=view,
                        ephemeral=True
                    )

                cat = _sel[0]
                if not cat:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} Please select a category from the dropdown first."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(
                        view=view,
                        ephemeral=True
                    )

                # get the settings panel message
                panel_message = interaction.message
                await interaction.response.send_message(
                    view=SelectChannelView(s._guild_id, cat, s._author, panel_message),
                    ephemeral=True
                )

        class _ClearChannelBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(label="Clear Channel", style=discord.ButtonStyle.secondary, emoji=get_emoji("icon_cross"))
                s._author = author
                s._guild_id = guild_id

            async def callback(s, interaction: discord.Interaction):
                if interaction.user != s._author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} Only the command invoker can use these button."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(
                        view=view,
                        ephemeral=True
                    )
                cat = _sel[0]
                if not cat:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} Please select a category from the dropdown first."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(
                        view=view,
                        ephemeral=True
                    )
                d = _load_log_config()
                gc = _guild_config(d, s._guild_id)
                gc[cat] = None
                _save_log_config(d)
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_cross')} Cleared channel for **{CATEGORIES[cat]['label']}** logs."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                await interaction.response.send_message(
                    view=view, ephemeral=True
                )
                # update the panel
                await interaction.message.edit(view=LoggingSetupView(s._guild_id, s._author, cat))

        class _ToggleBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(label="Toggle Enable/Disable", style=discord.ButtonStyle.secondary, emoji=get_emoji('icon_refresh'))
                s._author = author
                s._guild_id = guild_id

            async def callback(s, interaction: discord.Interaction):
                if interaction.user != s._author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} Only the command invoker can use these button."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(
                        view=view,
                        ephemeral=True
                    )
                cat = _sel[0]
                if not cat:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} Please select a category from the dropdown first."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(
                        view=view,
                        ephemeral=True
                    )
                d = _load_log_config()
                gc = _guild_config(d, s._guild_id)
                dis = gc.setdefault("disabled", [])
                if cat in dis:
                    dis.remove(cat)
                    state, e = "enabled", get_emoji("icon_tick")
                else:
                    dis.append(cat)
                    state, e = "disabled", get_emoji("icon_cross")
                _save_log_config(d)
                color = discord.Color.green() if state == "enabled" else discord.Color.red()
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{e} **{CATEGORIES[cat]['label']}** logging {state}."
                    ),
                    accent_colour=color
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)
                # update the panel
                await interaction.message.edit(view=LoggingSetupView(s._guild_id, s._author, cat))

        class _SetAllBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(label="Set All to This Channel", style=discord.ButtonStyle.secondary, emoji="📌")
                s._author = author
                s._guild_id = guild_id

            async def callback(s, interaction: discord.Interaction):
                if interaction.user != s._author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} Only the command invoker can use these button."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(
                        view=view,
                        ephemeral=True
                    )
                d = _load_log_config()
                gc = _guild_config(d, s._guild_id)
                for cat in CATEGORIES:
                    gc[cat] = interaction.channel.id
                _save_log_config(d)
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_tick')} All log categories → {interaction.channel.mention}"
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)
                # update the panel
                await interaction.message.edit(view=LoggingSetupView(s._guild_id, s._author, cat))

        class _ClearAllBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(label="Clear All Channels", style=discord.ButtonStyle.danger, emoji=get_emoji('icon_trash'))
                s._author = author
                s._guild_id = guild_id

            async def callback(s, interaction: discord.Interaction):
                if interaction.user != s._author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} Only the command invoker can use these button."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(
                        view=view,
                        ephemeral=True
                    )
                d = _load_log_config()
                gc = _guild_config(d, s._guild_id)
                for cat in CATEGORIES:
                    gc[cat] = None
                _save_log_config(d)
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_cross')} Cleared all logging channels."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)
                # update the panel
                await interaction.message.edit(view=LoggingSetupView(s._guild_id, s._author, cat))

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {icon} Server Logging"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    "Configure which channel each log category is sent to. "
                    "Select a category from the dropdown, then use the buttons to set or clear its channel and toggle it on or off."
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=summary),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(_CategorySelect()),
            discord.ui.ActionRow(_SetChannelBtn(), _ClearChannelBtn(), _ToggleBtn()),
            discord.ui.ActionRow(_SetAllBtn(), _ClearAllBtn()),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"-# **Need help?** Ask in the [support server]({links.SUPPORT_SERVER}) or check the [documentation]({links.DOCS})"
            ),
            accent_colour=discord.Colour(0x5865F2),
        )
        self.add_item(container)


# ── Main Cog ──────────────────────────────────────


__all__ = [k for k in list(globals()) if not k.startswith("__")]
