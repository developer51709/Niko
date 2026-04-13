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

# ── Constants ────────────────────────────────────────────────────────────────

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
    "Nickname Changed": "moderation",
    "Clear": "moderation",
    "Purge": "messages",
    "Lock": "channels",
    "Unlock": "channels",
    "Anti-Spam": "automod",
    "Anti-Link": "automod",
    "Bad Word Filter": "automod",
    "Mass Mention": "automod",
}
_AUTOMOD_SUBSTRINGS = ("Anti-Nuke", "Anti-Raid", "User-Installed", "Interaction Flood", "Nuke", "Raid")

# Which action titles get quick-action buttons and which button set
_ACTION_BUTTONS: dict[str, list[str]] = {
    "Kick": ["ban"],
    "Ban": ["unban"],
    "Warn": ["kick", "ban"],
    "Mute": ["unmute"],
    "Tempmute": ["unmute"],
    "Anti-Spam": ["kick", "ban"],
    "Anti-Link": ["kick", "ban"],
    "Bad Word Filter": ["kick", "ban"],
    "Mass Mention": ["kick", "ban"],
    "member_join": ["kick", "ban"],
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
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    buttons = _build_action_buttons(action_key or title, guild_id, target_id, channel_id)

    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {emoji} {title}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=body),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=f"-# {timestamp}"),
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
        if before.nick != after.nick:
            changes.append(f"**Nickname:** `{before.nick or before.name}` → `{after.nick or after.name}`")

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
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        body = (
            f"**Channel:** {channel.mention} (`{channel.name}`)\n"
            f"**Type:** {str(channel.type).replace('_', ' ').title()}"
        )
        await self.log_event(channel.guild, "channels", "Channel Created", body)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        body = (
            f"**Channel:** `#{channel.name}`\n"
            f"**Type:** {str(channel.type).replace('_', ' ').title()}"
        )
        await self.log_event(channel.guild, "channels", "Channel Deleted", body)

    # ── Commands ──────────────────────────────────────────────────────────

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
