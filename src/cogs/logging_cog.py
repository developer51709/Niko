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
from config.emojis import get_emoji

# ── Constants ──────────────────────────────────────

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


# ── Config helpers ─────────────────────────────────

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


# ── Quick-action buttons ───────────────────────────

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
        super().__init__(label="Ban", style=discord.ButtonStyle.danger, emoji="🔨", row=0)
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
        super().__init__(label="Unban", style=discord.ButtonStyle.success, emoji="✅", row=0)
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
        super().__init__(label="Unlock Channel", style=discord.ButtonStyle.success, emoji="🔓", row=0)
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


# ── Log entry view builder ─────────────────────────

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
    # set join and leave emojis
    if title == "Member Joined":
        emoji = get_emoji("icon_join")
    if title == "Member Left":
        emoji = get_emoji("icon_leave")

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


# ── Settings Panel ─────────────────────────────────

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
                await interaction.response.send_message(
                    f"{get_emoji('icon_settings')} Category **{label}** selected. Now use the buttons below to configure it.",
                    ephemeral=True,
                )

        class _SetChannelBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(label="Set Channel Here", style=discord.ButtonStyle.primary, emoji=get_emoji("icon_plus"))
                s._author = author
                s._guild_id = guild_id

            async def callback(s, interaction: discord.Interaction):
                if interaction.user != s._author:
                    return await interaction.response.send_message("Only the command invoker can use these buttons.", ephemeral=True)
                cat = _sel[0]
                if not cat:
                    return await interaction.response.send_message("Please select a category from the dropdown first.", ephemeral=True)
                d = _load_log_config()
                gc = _guild_config(d, s._guild_id)
                gc[cat] = interaction.channel.id
                _save_log_config(d)
                await interaction.response.send_message(
                    f"{get_emoji('icon_tick')} **{CATEGORIES[cat]['label']}** logs → {interaction.channel.mention}", ephemeral=True
                )
                # update the panel
                await interaction.message.edit(view=LoggingSetupView(s._guild_id, s._author, cat))

        class _ClearChannelBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(label="Clear Channel", style=discord.ButtonStyle.secondary, emoji=get_emoji("icon_cross"))
                s._author = author
                s._guild_id = guild_id

            async def callback(s, interaction: discord.Interaction):
                if interaction.user != s._author:
                    return await interaction.response.send_message("Only the command invoker can use these buttons.", ephemeral=True)
                cat = _sel[0]
                if not cat:
                    return await interaction.response.send_message("Please select a category from the dropdown first.", ephemeral=True)
                d = _load_log_config()
                gc = _guild_config(d, s._guild_id)
                gc[cat] = None
                _save_log_config(d)
                await interaction.response.send_message(
                    f"{get_emoji('icon_cross')} Cleared channel for **{CATEGORIES[cat]['label']}** logs.", ephemeral=True
                )
                # update the panel
                await interaction.message.edit(view=LoggingSetupView(s._guild_id, s._author, cat))

        class _ToggleBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(label="Toggle Enable/Disable", style=discord.ButtonStyle.secondary, emoji="🔄")
                s._author = author
                s._guild_id = guild_id

            async def callback(s, interaction: discord.Interaction):
                if interaction.user != s._author:
                    return await interaction.response.send_message("Only the command invoker can use these buttons.", ephemeral=True)
                cat = _sel[0]
                if not cat:
                    return await interaction.response.send_message("Please select a category from the dropdown first.", ephemeral=True)
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
                await interaction.response.send_message(
                    f"{e} **{CATEGORIES[cat]['label']}** logging {state}.", ephemeral=True
                )
                # update the panel
                await interaction.message.edit(view=LoggingSetupView(s._guild_id, s._author, cat))

        class _SetAllBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(label="Set All to This Channel", style=discord.ButtonStyle.secondary, emoji="📌")
                s._author = author
                s._guild_id = guild_id

            async def callback(s, interaction: discord.Interaction):
                if interaction.user != s._author:
                    return await interaction.response.send_message("Only the command invoker can use these buttons.", ephemeral=True)
                d = _load_log_config()
                gc = _guild_config(d, s._guild_id)
                for cat in CATEGORIES:
                    gc[cat] = interaction.channel.id
                _save_log_config(d)
                await interaction.response.send_message(
                    f"{get_emoji('icon_tick')} All log categories → {interaction.channel.mention}", ephemeral=True
                )
                # update the panel
                await interaction.message.edit(view=LoggingSetupView(s._guild_id, s._author, cat))

        class _ClearAllBtn(discord.ui.Button):
            def __init__(s):
                super().__init__(label="Clear All Channels", style=discord.ButtonStyle.danger, emoji="🗑️")
                s._author = author
                s._guild_id = guild_id

            async def callback(s, interaction: discord.Interaction):
                if interaction.user != s._author:
                    return await interaction.response.send_message("Only the command invoker can use these buttons.", ephemeral=True)
                d = _load_log_config()
                gc = _guild_config(d, s._guild_id)
                for cat in CATEGORIES:
                    gc[cat] = None
                _save_log_config(d)
                await interaction.response.send_message(
                    f"{get_emoji('icon_cross')} Cleared all logging channels.", ephemeral=True
                )
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
                content="-# **Need help?** Ask in the [support server](https://dsc.gg/astral-haven) or check the [documentation](https://developer51709.github.io/Niko/docs)"
            ),
            accent_colour=discord.Colour(0x5865F2),
        )
        self.add_item(container)


# ── The Cog ────────────────────────────────────────

class ServerLogger(commands.Cog):
    """Multi-channel server event logging."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._config: dict = _load_log_config()
        # guild_id → {invite_code: uses_count}
        self._invite_cache: dict[int, dict[str, int]] = {}

    @commands.Cog.listener()
    async def on_ready(self):
        """Populate invite cache for all guilds on startup."""
        for guild in self.bot.guilds:
            try:
                invites = await guild.invites()
                self._invite_cache[guild.id] = {inv.code: inv.uses for inv in invites}
            except (discord.Forbidden, discord.HTTPException):
                pass

    def _get_cfg(self, guild_id: int) -> dict:
        return _guild_config(self._config, guild_id)

    def _reload(self):
        self._config = _load_log_config()

    # ── Core logging method ────────────────────────

    async def log_event(
        self,
        guild: discord.Guild,
        category: str,
        title: str,
        body: str,
        target_id: int | None = None,
        action_key: str | None = None,
        channel_id: int | None = None,
    ):
        """Send a structured log entry to the configured channel for the given category."""
        self._reload()
        cfg = self._get_cfg(guild.id)

        if category in cfg.get("disabled", []):
            return

        log_channel_id = cfg.get(category)
        if not log_channel_id:
            return

        channel = guild.get_channel(log_channel_id)
        if not channel:
            return

        view = _build_log_view(
            category=category,
            title=title,
            body=body,
            guild_id=guild.id,
            target_id=target_id,
            action_key=action_key or title,
            channel_id=channel_id,
        )
        try:
            await channel.send(view=view, allowed_mentions=discord.AllowedMentions.none())
        except Exception as e:
            logging.error("logging_cog", f"Failed to send log message to {channel} in {guild}: {e}")
            pass

    #Backward-compat wrapper used by moderation_utils

    async def log_action(
        self,
        guild: discord.Guild,
        title: str,
        description: str,
        target: discord.Member | discord.User | None = None,
        moderator: discord.Member | None = None,
    ):
        """Drop-in replacement for the old ModerationUtils.log_action."""
        # Determine category from title
        category = _TITLE_CATEGORY.get(title)
        if not category:
            if any(s in title for s in _AUTOMOD_SUBSTRINGS):
                category = "automod"
            else:
                category = "moderation"

        body = description
        if moderator and f"{moderator}" not in description:
            body += f"\n**Moderator:** {moderator.mention}"

        target_id = target.id if target else None
        await self.log_event(guild, category, title, body, target_id=target_id, action_key=title)

    # ── Gateway event listeners ────────────────────

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        created = member.created_at.strftime("%Y-%m-%d")
        account_age = (datetime.now(timezone.utc) - member.created_at).days
        age_warn = f"\n-# ⚠️ New account — only **{account_age}d** old" if account_age < 7 else ""

        # ── Detect which invite was used ───────────
        used_invite = None
        try:
            current_invites = await guild.invites()
            cached = self._invite_cache.get(guild.id, {})
            for inv in current_invites:
                if inv.uses > cached.get(inv.code, 0):
                    used_invite = inv
                    break
            self._invite_cache[guild.id] = {inv.code: inv.uses for inv in current_invites}
        except (discord.Forbidden, discord.HTTPException):
            pass

        # Log invite usage to the invites category
        if used_invite:
            inv_body = (
                f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Invite Code:** `{used_invite.code}`\n"
                f"**Created By:** {used_invite.inviter.mention if used_invite.inviter else 'Unknown'}\n"
                f"**Total Uses:** {used_invite.uses}"
            )
            await self.log_event(
                guild, "invites", "Invite Used", inv_body,
                target_id=member.id
            )

        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Account Created:** {created} ({account_age} days ago){age_warn}"
        )
        await self.log_event(
            guild, "members", "Member Joined", body,
            target_id=member.id, action_key="member_join"
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild

        # ── Check audit log for an external kick ──
        kick_entry = None
        try:
            async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.kick):
                if entry.target.id == member.id:
                    kick_entry = entry
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

        if kick_entry and kick_entry.user != self.bot.user:
            kick_body = (
                f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Action:** Kick\n"
                f"**Reason:** {kick_entry.reason or 'No reason provided'}\n"
                f"**Moderator:** {kick_entry.user.mention if kick_entry.user else 'Unknown'}"
            )
            await self.log_event(
                guild, "moderation", "Kick", kick_body,
                target_id=member.id, action_key="Kick"
            )

        roles = [r.mention for r in member.roles if r != guild.default_role]
        roles_text = ", ".join(roles) if roles else "None"
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Roles:** {roles_text}"
        )
        await self.log_event(guild, "members", "Member Left", body)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        guild = after.guild
        before_roles = set(before.roles)
        after_roles = set(after.roles)

        added = after_roles - before_roles
        removed = before_roles - after_roles

        changes = []
        if added:
            changes.append(f"**Roles Added:** {', '.join(r.mention for r in added)}")
        if removed:
            changes.append(f"**Roles Removed:** {', '.join(r.mention for r in removed)}")

        # ── Nick change — attribute to moderator via audit log ──
        if before.nick != after.nick:
            nick_moderator = None
            try:
                async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                    if entry.target.id == after.id:
                        nick_moderator = entry.user
                        break
            except (discord.Forbidden, discord.HTTPException):
                pass

            if nick_moderator and nick_moderator != self.bot.user:
                nick_body = (
                    f"**Member:** {after.mention} (`{after}` — ID: `{after.id}`)\n"
                    f"**Old Nickname:** `{before.nick or before.name}`\n"
                    f"**New Nickname:** `{after.nick or after.name}`\n"
                    f"**Changed By:** {nick_moderator.mention}"
                )
                await self.log_event(
                    guild, "moderation", "Nickname Changed", nick_body,
                    target_id=after.id
                )

            changes.append(f"**Nickname:** `{before.nick or before.name}` → `{after.nick or after.name}`")

        # ── Discord native timeout detection ──────
        before_timeout = getattr(before, "timed_out_until", None)
        after_timeout = getattr(after, "timed_out_until", None)
        if before_timeout != after_timeout:
            timeout_mod = None
            try:
                async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                    if entry.target.id == after.id:
                        timeout_mod = entry.user
                        break
            except (discord.Forbidden, discord.HTTPException):
                pass

            if timeout_mod and timeout_mod != self.bot.user:
                if after_timeout:
                    timeout_body = (
                        f"**User:** {after.mention} (`{after}` — ID: `{after.id}`)\n"
                        f"**Action:** Timeout applied\n"
                        f"**Until:** <t:{int(after_timeout.timestamp())}:F> (<t:{int(after_timeout.timestamp())}:R>)\n"
                        f"**Moderator:** {timeout_mod.mention}"
                    )
                    await self.log_event(
                        guild, "moderation", "Timeout", timeout_body,
                        target_id=after.id, action_key="Timeout"
                    )
                else:
                    timeout_body = (
                        f"**User:** {after.mention} (`{after}` — ID: `{after.id}`)\n"
                        f"**Action:** Timeout removed\n"
                        f"**Moderator:** {timeout_mod.mention}"
                    )
                    await self.log_event(
                        guild, "moderation", "Timeout Removed", timeout_body,
                        target_id=after.id
                    )

        if not changes:
            return

        body = f"**Member:** {after.mention} (`{after}`)\n" + "\n".join(changes)
        await self.log_event(guild, "members", "Member Updated", body, target_id=after.id)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return
        content = message.content or "*No text content*"
        if len(content) > 900:
            content = content[:900] + "…"
        body = (
            f"**Author:** {message.author.mention} (`{message.author}`)\n"
            f"**Channel:** {message.channel.mention}\n"
            f"**Content:**\n{content}"
        )
        await self.log_event(message.guild, "messages", "Message Deleted", body, target_id=message.author.id)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not after.guild or after.author.bot:
            return
        if before.content == after.content:
            return
        before_content = before.content or "*empty*"
        after_content = after.content or "*empty*"
        if len(before_content) > 450:
            before_content = before_content[:450] + "…"
        if len(after_content) > 450:
            after_content = after_content[:450] + "…"
        body = (
            f"**Author:** {after.author.mention} (`{after.author}`)\n"
            f"**Channel:** {after.channel.mention}\n"
            f"**Before:**\n{before_content}\n"
            f"**After:**\n{after_content}\n"
            f"-# [Jump to message]({after.jump_url})"
        )
        await self.log_event(after.guild, "messages", "Message Edited", body, target_id=after.author.id)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Cache invites when the bot joins a new guild."""
        try:
            invites = await guild.invites()
            self._invite_cache[guild.id] = {inv.code: inv.uses for inv in invites}
        except (discord.Forbidden, discord.HTTPException):
            pass

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        guild = invite.guild
        if not guild:
            return
        # Update cache
        cached = self._invite_cache.setdefault(guild.id, {})
        cached[invite.code] = invite.uses

        expires_text = (
            f"<t:{int(invite.expires_at.timestamp())}:R>" if invite.expires_at else "Never"
        )
        max_uses_text = str(invite.max_uses) if invite.max_uses else "Unlimited"
        body = (
            f"**Invite Code:** `{invite.code}`\n"
            f"**Created By:** {invite.inviter.mention if invite.inviter else 'Unknown'}\n"
            f"**Channel:** {invite.channel.mention if invite.channel else 'Unknown'}\n"
            f"**Max Uses:** {max_uses_text}\n"
            f"**Expires:** {expires_text}"
        )
        await self.log_event(guild, "invites", "Invite Created", body)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        guild = invite.guild
        if not guild:
            return
        # Remove from cache
        cached = self._invite_cache.get(guild.id, {})
        cached.pop(invite.code, None)

        body = (
            f"**Invite Code:** `{invite.code}`\n"
            f"**Channel:** {invite.channel.mention if invite.channel else 'Unknown'}"
        )
        await self.log_event(guild, "invites", "Invite Deleted", body)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        responsible = None
        try:
            async for entry in channel.guild.audit_logs(limit=3, action=discord.AuditLogAction.channel_create):
                if entry.target.id == channel.id:
                    responsible = entry.user
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

        body = (
            f"**Channel:** {channel.mention} (`{channel.name}`)\n"
            f"**Type:** {str(channel.type).replace('_', ' ').title()}\n"
            f"**Created By:** {responsible.mention if responsible else 'Unknown'}"
        )
        await self.log_event(channel.guild, "channels", "Channel Created", body)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        responsible = None
        try:
            async for entry in channel.guild.audit_logs(limit=3, action=discord.AuditLogAction.channel_delete):
                if entry.target.id == channel.id:
                    responsible = entry.user
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

        body = (
            f"**Channel:** `#{channel.name}`\n"
            f"**Type:** {str(channel.type).replace('_', ' ').title()}\n"
            f"**Deleted By:** {responsible.mention if responsible else 'Unknown'}"
        )
        await self.log_event(channel.guild, "channels", "Channel Deleted", body)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        changes = []

        if before.name != after.name:
            changes.append(f"**Name:** `{before.name}` → `{after.name}`")

        if isinstance(after, discord.TextChannel) or isinstance(after, discord.ForumChannel):
            if getattr(before, "topic", None) != getattr(after, "topic", None):
                b_topic = getattr(before, "topic", None) or "*None*"
                a_topic = getattr(after, "topic", None) or "*None*"
                changes.append(f"**Topic:** {b_topic} → {a_topic}")
            if getattr(before, "slowmode_delay", 0) != getattr(after, "slowmode_delay", 0):
                changes.append(f"**Slowmode:** `{getattr(before, 'slowmode_delay', 0)}s` → `{getattr(after, 'slowmode_delay', 0)}s`")
            if getattr(before, "nsfw", False) != getattr(after, "nsfw", False):
                changes.append(f"**NSFW:** `{getattr(before, 'nsfw', False)}` → `{getattr(after, 'nsfw', False)}`")

        if isinstance(after, discord.VoiceChannel):
            if getattr(before, "bitrate", None) != getattr(after, "bitrate", None):
                changes.append(f"**Bitrate:** `{getattr(before, 'bitrate', 0) // 1000}kbps` → `{getattr(after, 'bitrate', 0) // 1000}kbps`")
            if getattr(before, "user_limit", 0) != getattr(after, "user_limit", 0):
                b_lim = getattr(before, "user_limit", 0) or "Unlimited"
                a_lim = getattr(after, "user_limit", 0) or "Unlimited"
                changes.append(f"**User Limit:** `{b_lim}` → `{a_lim}`")

        if not changes:
            return

        responsible = None
        try:
            async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_update):
                if entry.target.id == after.id:
                    responsible = entry.user
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

        body = (
            f"**Channel:** {after.mention} (`{after.name}`)\n"
            f"**Updated By:** {responsible.mention if responsible else 'Unknown'}\n"
            + "\n".join(changes)
        )
        await self.log_event(after.guild, "channels", "Channel Updated", body)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        responsible = None
        try:
            async for entry in role.guild.audit_logs(limit=3, action=discord.AuditLogAction.role_create):
                if entry.target.id == role.id:
                    responsible = entry.user
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

        color_text = str(role.color) if role.color.value else "Default"
        body = (
            f"**Role:** {role.mention} (`{role.name}`)\n"
            f"**Color:** `{color_text}`\n"
            f"**Hoisted:** `{role.hoist}` | **Mentionable:** `{role.mentionable}`\n"
            f"**Created By:** {responsible.mention if responsible else 'Unknown'}"
        )
        await self.log_event(role.guild, "roles", "Role Created", body)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        responsible = None
        try:
            async for entry in role.guild.audit_logs(limit=3, action=discord.AuditLogAction.role_delete):
                if entry.target.id == role.id:
                    responsible = entry.user
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

        body = (
            f"**Role:** `{role.name}` (ID: `{role.id}`)\n"
            f"**Deleted By:** {responsible.mention if responsible else 'Unknown'}"
        )
        await self.log_event(role.guild, "roles", "Role Deleted", body)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        changes = []

        if before.name != after.name:
            changes.append(f"**Name:** `{before.name}` → `{after.name}`")
        if before.color != after.color:
            changes.append(f"**Color:** `{before.color}` → `{after.color}`")
        if before.hoist != after.hoist:
            changes.append(f"**Hoisted:** `{before.hoist}` → `{after.hoist}`")
        if before.mentionable != after.mentionable:
            changes.append(f"**Mentionable:** `{before.mentionable}` → `{after.mentionable}`")
        if before.permissions != after.permissions:
            perm_changes = []
            for perm, value in iter(after.permissions):
                if getattr(before.permissions, perm) != value:
                    symbol = "✅" if value else "❌"
                    perm_changes.append(f"{symbol} `{perm.replace('_', ' ').title()}`")
            if perm_changes:
                changes.append("**Permissions Changed:**\n" + " ".join(perm_changes))

        if not changes:
            return

        responsible = None
        try:
            async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.role_update):
                if entry.target.id == after.id:
                    responsible = entry.user
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

        body = (
            f"**Role:** {after.mention} (`{after.name}`)\n"
            f"**Updated By:** {responsible.mention if responsible else 'Unknown'}\n"
            + "\n".join(changes)
        )
        await self.log_event(after.guild, "roles", "Role Updated", body)

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        changes = []

        if before.name != after.name:
            changes.append(f"**Name:** `{before.name}` → `{after.name}`")
        if before.description != after.description:
            b_desc = before.description or "*None*"
            a_desc = after.description or "*None*"
            changes.append(f"**Description:** {b_desc} → {a_desc}")
        if before.verification_level != after.verification_level:
            changes.append(f"**Verification Level:** `{before.verification_level}` → `{after.verification_level}`")
        if before.explicit_content_filter != after.explicit_content_filter:
            changes.append(f"**Explicit Content Filter:** `{before.explicit_content_filter}` → `{after.explicit_content_filter}`")
        if before.default_notifications != after.default_notifications:
            changes.append(f"**Default Notifications:** `{before.default_notifications}` → `{after.default_notifications}`")
        if before.afk_channel != after.afk_channel:
            b_afk = before.afk_channel.name if before.afk_channel else "None"
            a_afk = after.afk_channel.name if after.afk_channel else "None"
            changes.append(f"**AFK Channel:** `{b_afk}` → `{a_afk}`")
        if before.icon != after.icon:
            changes.append("**Server Icon:** changed")
        if before.banner != after.banner:
            changes.append("**Server Banner:** changed")

        if not changes:
            return

        responsible = None
        try:
            async for entry in after.audit_logs(limit=5, action=discord.AuditLogAction.guild_update):
                responsible = entry.user
                break
        except (discord.Forbidden, discord.HTTPException):
            pass

        body = (
            f"**Updated By:** {responsible.mention if responsible else 'Unknown'}\n"
            + "\n".join(changes)
        )
        await self.log_event(after, "server", "Server Updated", body)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild: discord.Guild, before: list, after: list):
        before_ids = {e.id for e in before}
        after_ids = {e.id for e in after}

        added = [e for e in after if e.id not in before_ids]
        removed = [e for e in before if e.id not in after_ids]

        if not added and not removed:
            return

        lines = []
        if added:
            lines.append("**Added:** " + ", ".join(f"`:{e.name}:`" for e in added))
        if removed:
            lines.append("**Removed:** " + ", ".join(f"`:{e.name}:`" for e in removed))

        responsible = None
        try:
            action = discord.AuditLogAction.emoji_create if added else discord.AuditLogAction.emoji_delete
            async for entry in guild.audit_logs(limit=3, action=action):
                responsible = entry.user
                break
        except (discord.Forbidden, discord.HTTPException):
            pass

        body = (
            f"**Updated By:** {responsible.mention if responsible else 'Unknown'}\n"
            + "\n".join(lines)
        )
        await self.log_event(guild, "server", "Emoji Updated", body)

    @commands.Cog.listener()
    async def on_guild_stickers_update(self, guild: discord.Guild, before: list, after: list):
        before_ids = {s.id for s in before}
        after_ids = {s.id for s in after}

        added = [s for s in after if s.id not in before_ids]
        removed = [s for s in before if s.id not in after_ids]

        if not added and not removed:
            return

        lines = []
        if added:
            lines.append("**Added:** " + ", ".join(f"`{s.name}`" for s in added))
        if removed:
            lines.append("**Removed:** " + ", ".join(f"`{s.name}`" for s in removed))

        body = "\n".join(lines)
        await self.log_event(guild, "server", "Sticker Updated", body)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild

        if before.channel is None and after.channel is not None:
            body = (
                f"**Member:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Joined:** {after.channel.mention}"
            )
            await self.log_event(guild, "voice", "Voice Join", body, target_id=member.id)

        elif before.channel is not None and after.channel is None:
            body = (
                f"**Member:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Left:** {before.channel.mention}"
            )
            await self.log_event(guild, "voice", "Voice Leave", body, target_id=member.id)

        elif (
            before.channel is not None
            and after.channel is not None
            and before.channel.id != after.channel.id
        ):
            body = (
                f"**Member:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**From:** {before.channel.mention}\n"
                f"**To:** {after.channel.mention}"
            )
            await self.log_event(guild, "voice", "Voice Move", body, target_id=member.id)

    @commands.Cog.listener()
    # update: discord.py does not support the moderator parameter so we must use the audit log to get the moderator.
    async def on_member_ban(self, guild: discord.Guild, user: discord.User, reason: str | None = None):
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            moderator = entry.user
        if moderator == self.bot.user:
            return
        body = (
            f"**User:** {user.mention} (`{user}` — ID: `{user.id}`)\n"
            f"**Action:** Ban\n"
            f"**Reason:** {reason or 'No reason provided'}\n"
            f"**Moderator:** {moderator.mention if moderator else 'Unknown'}"
        )
        await self.log_event(
            guild, "moderation", "Ban", body, 
            target_id=user.id, action_key="Ban"
        )

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User, reason: str | None = None):
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
            moderator = entry.user
        if moderator == self.bot.user:
            return
        body = (
            f"**User:** {user.mention} (`{user}` — ID: `{user.id}`)\n"
            f"**Action:** Unban\n"
            f"**Reason:** {reason or 'No reason provided'}\n"
            f"**Moderator:** {moderator.mention if moderator else 'Unknown'}"
        )
        await self.log_event(
            guild, "moderation", "Unban", body,
            target_id=user.id, action_key="Unban"
        )

    # ── Commands ───────────────────────────────────

    @commands.group(name="logging", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def logging_cmd(self, ctx: commands.Context):
        """Open the server logging configuration panel."""
        await ctx.send(view=LoggingSetupView(ctx.guild.id, ctx.author))

    @logging_cmd.command(name="status")
    @commands.has_permissions(manage_guild=True)
    async def logging_status(self, ctx: commands.Context):
        """Show the current logging configuration."""
        self._reload()
        cfg = self._get_cfg(ctx.guild.id)
        icon = get_emoji("icon_settings")

        lines = []
        for key, info in CATEGORIES.items():
            ch_id = cfg.get(key)
            ch_text = f"<#{ch_id}>" if ch_id else "`Not set`"
            disabled = key in cfg.get("disabled", [])
            status = get_emoji("disabled") if disabled else get_emoji("enabled")
            lines.append(f"{status} **{info['label']}** — {ch_text}")

        body = "\n".join(lines)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {icon} Logging Status"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=body),
            accent_colour=discord.Colour(0x5865F2),
        ))
        await ctx.send(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerLogger(bot))
