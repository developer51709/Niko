import discord
from discord.ext import commands
import random
import json
import os
import time
from utils import logging as log
from utils.paginator import PaginatedView, paginate
from utils.i18n import make_msg
from config.emojis import get_emoji

# The brand accent shared by every Niko view, used when a guild has not picked
# custom card colours.
ACCENT_BRAND = 0xC8A882

# ───────────────────────────────────────────────────
#  MESSAGE TABLE
# ───────────────────────────────────────────────────

MESSAGES = {
    "normal": {
        "en": {
            "level_up":          "Congratulations {mention}, you leveled up to level **{level}**!",
            "no_xp":             "{name} hasn't earned any XP yet.",
            "stats_title":       "Level Stats — {name}",
            "stats_level":       "Level",
            "stats_xp":          "XP",
            "stats_rank":        "Rank",
            "leaderboard_title": "Leveling Leaderboard — {guild}",
            "leaderboard_empty": "No one has earned any XP in this server yet.",
            "xp_disabled":       "XP tracking is currently disabled for this server.",
            "cfg_updated":       "✅ Setting updated.",
            "cfg_show":          "### Level Config — {guild}\n{body}",
        },
        "de": {
            "level_up":          "Glückwunsch {mention}, du bist auf Level **{level}** aufgestiegen!",
            "no_xp":             "{name} hat noch keine XP gesammelt.",
            "stats_title":       "Level-Statistiken — {name}",
            "stats_level":       "Level",
            "stats_xp":          "XP",
            "stats_rank":        "Rang",
            "leaderboard_title": "Leveling-Bestenliste — {guild}",
            "leaderboard_empty": "Noch niemand hat XP auf diesem Server gesammelt.",
            "xp_disabled":       "XP-Tracking ist für diesen Server deaktiviert.",
            "cfg_updated":       "✅ Einstellung aktualisiert.",
            "cfg_show":          "### Level-Konfiguration — {guild}\n{body}",
        },
        "es": {
            "level_up":          "¡Felicidades {mention}, has subido al nivel **{level}**!",
            "no_xp":             "{name} aún no ha ganado XP.",
            "stats_title":       "Estadísticas de Nivel — {name}",
            "stats_level":       "Nivel",
            "stats_xp":          "XP",
            "stats_rank":        "Rango",
            "leaderboard_title": "Tabla de Niveles — {guild}",
            "leaderboard_empty": "Nadie ha ganado XP en este servidor todavía.",
            "xp_disabled":       "El sistema de XP está desactivado en este servidor.",
            "cfg_updated":       "✅ Configuración actualizada.",
            "cfg_show":          "### Configuración de Niveles — {guild}\n{body}",
        },
    },
}


msg = make_msg(MESSAGES)


# ───────────────────────────────────────────────────
#  DEFAULTS
# ───────────────────────────────────────────────────

DEFAULT_GUILD_LEVEL_CONFIG = {
    "xp_enabled":       True,
    "xp_multiplier":    1.0,
    "xp_cooldown":      0,
    "level_up_channel": None,
    "level_up_message": None,
    "level_roles":      {},
    # Channels that never award XP. Ticket channels are excluded separately.
    "xp_excluded_channels": [],
    # Voice XP is opt-in: members earn XP for time spent in voice channels.
    "xp_vc_enabled":    False,
    # Card customization
    "card_accent":      None,   # RGB tuple or None for the default theme accent
    "card_bg_top":      None,   # RGB tuple or None for the default graphite
    "card_bg_bottom":   None,   # RGB tuple or None for default dark
}


# ───────────────────────────────────────────────────
#  PANEL TEXT BUILDERS
# ───────────────────────────────────────────────────

def _lv_icon(val) -> str:
    return get_emoji("tick") if val else get_emoji("cross")


def _colour_hex(rgb):
    """Convert an RGB tuple to a Discord colour integer or None."""
    if not rgb:
        return None
    return (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]


def _lv_overview_text(cfg: dict, guild: discord.Guild) -> str:
    lu_ch   = guild.get_channel(cfg.get("level_up_channel") or 0)
    lu_ch_s = lu_ch.mention if lu_ch else "*(same channel)*"
    lr      = cfg.get("level_roles", {})
    lr_s    = ", \n".join(
        f"  Level {lvl} → {(guild.get_role(int(rid)) or discord.Object(rid)).mention}"
        for lvl, rid in sorted(lr.items(), key=lambda x: int(x[0]))
    ) or "  *(none)*"
    custom_msg = cfg.get("level_up_message")
    msg_s = f"`{custom_msg}`" if custom_msg else "*(default message)*"

    # Card style summary
    accent = cfg.get("card_accent")
    accent_s = f"#{accent[0]:02x}{accent[1]:02x}{accent[2]:02x}" if accent else "*(default gold)*"

    excluded = cfg.get("xp_excluded_channels") or []
    return (
        "### Leveling Management Panel\n"
        "Manage all your server's leveling settings from one place.\n\n"
        "**📊 XP Settings**\n"
        f"{_lv_icon(cfg.get('xp_enabled', True))} XP enabled  •  "
        f"Multiplier: `{cfg.get('xp_multiplier', 1.0)}x`  •  "
        f"Cooldown: `{cfg.get('xp_cooldown', 0)}s`\n\n"
        "**📡 Channels & Voice**\n"
        f"Channels excluded from XP: `{len(excluded)}`  •  "
        f"Voice XP: {_lv_icon(cfg.get('xp_vc_enabled', False))}\n"
        "-# Ticket channels never award XP.\n\n"
        "**📣 Announcements**\n"
        f"Level-up channel: {lu_ch_s}\n"
        f"Custom message: {msg_s}\n\n"
        "**🎖️ Level Roles** *(automatically awarded on level-up)*\n"
        f"{lr_s}\n\n"
        "**🎨 Card Style**\n"
        f"Accent colour: `{accent_s}`\n\n"
        "-# Use the dropdown below to navigate and configure each section."
    )


def _lv_xp_text(cfg: dict) -> str:
    cd = cfg.get("xp_cooldown", 0)
    cd_s = f"`{cd}s`" if cd > 0 else "`off`"
    return (
        "### 📊 XP Settings\n"
        "Control how members earn experience in your server.\n\n"
        f"{get_emoji('enabled') if cfg.get('xp_enabled', True) else get_emoji('disabled')} — **XP Tracking**\n\n"
        f"**XP Multiplier:** `{cfg.get('xp_multiplier', 1.0)}x`\n"
        f"Each message earns `15–25 × multiplier` XP at random.\n\n"
        f"**XP Cooldown:** {cd_s}\n"
        "Minimum time between XP gains per member (0 = every message).\n\n"
        "-# Use **Channels & Voice** to exclude channels from XP or enable passive voice XP."
    )


def _lv_announcements_text(cfg: dict, guild: discord.Guild) -> str:
    lu_ch      = guild.get_channel(cfg.get("level_up_channel") or 0)
    lu_ch_s    = lu_ch.mention if lu_ch else "*(same channel as the message)*"
    custom_msg = cfg.get("level_up_message")
    default_msg = "Congratulations {mention}, you leveled up to level **{level}**!"
    msg_display = custom_msg if custom_msg else default_msg
    return (
        "### 📣 Announcement Settings\n"
        "Configure where and how level-ups are announced.\n\n"
        f"**Level-Up Channel:** {lu_ch_s}\n"
        "-# Select a channel below or clear it to announce in the message's channel.\n\n"
        f"**Level-Up Message:**\n"
        f"> {msg_display}\n\n"
        "-# Available placeholders: `{mention}` `{level}` `{name}` `{guild}`\n"
        "-# Click **Edit Message** to customise, or **Reset Message** to restore the default."
    )


def _lv_roles_text(cfg: dict, guild: discord.Guild) -> str:
    lr = cfg.get("level_roles", {})
    if lr:
        lines = []
        for lvl, rid in sorted(lr.items(), key=lambda x: int(x[0])):
            role  = guild.get_role(int(rid))
            rname = role.mention if role else f"*(unknown role {rid})*"
            lines.append(f"**Level {lvl}** → {rname}")
        roles_body = "\n".join(lines)
    else:
        roles_body = "*No level roles configured yet.*"

    return (
        "### 🎖️ Level Roles\n"
        "Roles automatically awarded when a member reaches a certain level.\n\n"
        f"{roles_body}\n\n"
        f"-# Click **{get_emoji('plus')} Add Role** to assign a role to a level.\n"
        "-# Click **➖ Remove Role** to remove an assignment."
    )


def _lv_channels_text(cfg: dict, guild: discord.Guild) -> str:
    excluded_ids = cfg.get("xp_excluded_channels") or []
    if excluded_ids:
        lines = []
        for cid in excluded_ids:
            channel = guild.get_channel(int(cid))
            lines.append(f"• {channel.mention}" if channel else f"• *(deleted channel `{cid}`)*")
        excluded_body = "\n".join(lines)
    else:
        excluded_body = "*No channels excluded — every channel can award XP.*"

    vc_enabled = bool(cfg.get("xp_vc_enabled", False))
    return (
        "### 📡 Channels & Voice\n"
        "Control where members can earn XP.\n\n"
        "**Excluded Channels**\n"
        f"{excluded_body}\n"
        "-# Messages and time spent in these channels never award XP.\n"
        "-# Ticket channels are always excluded automatically.\n\n"
        f"**Voice XP:** {_lv_icon(vc_enabled)}\n"
        "-# When enabled, members earn XP for every minute they spend in a voice channel. "
        "AFK channels never award XP.\n\n"
        "-# Use the selector below to change the excluded channels."
    )


def _lv_cardstyle_text(cfg: dict) -> str:
    accent = cfg.get("card_accent")
    bg_top = cfg.get("card_bg_top")
    bg_bot = cfg.get("card_bg_bottom")

    def _fmt_rgb(rgb):
        if not rgb:
            return "*(default)*"
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    accent_s = _fmt_rgb(accent)
    bg_top_s = _fmt_rgb(bg_top)
    bg_bot_s = _fmt_rgb(bg_bot)

    return (
        "### 🎨 Card Style\n"
        "Customise the colours used in level cards and the leaderboard.\n\n"
        f"**Accent Colour:** `{accent_s}`\n"
        "Used for borders, level numbers, and the progress bar.\n\n"
        f"**Background Top:** `{bg_top_s}`\n"
        f"**Background Bottom:** `{bg_bot_s}`\n"
        "The gradient fills the card background.\n\n"
        "-# Use the buttons below to edit each colour.\n"
        "-# Enter hex codes like `#d96545` or `ff5500`.\n"
        "-# Click **Reset Colours** to restore the default colours."
    )


def _lv_section_text(cfg: dict, section: str, guild: discord.Guild) -> str:
    if section == "xp":            return _lv_xp_text(cfg)
    if section == "channels":      return _lv_channels_text(cfg, guild)
    if section == "announcements": return _lv_announcements_text(cfg, guild)
    if section == "level_roles":   return _lv_roles_text(cfg, guild)
    if section == "card_style":    return _lv_cardstyle_text(cfg)
    return _lv_overview_text(cfg, guild)


# ───────────────────────────────────────────────────
#  PANEL INTERACTIVE COMPONENTS
# ───────────────────────────────────────────────────

class _LvSectionSelect(discord.ui.Select):
    def __init__(self, cog, guild_id: int, current: str):
        self._cog      = cog
        self._guild_id = guild_id
        options = [
            discord.SelectOption(
                label="Overview",       value="overview",      emoji="📋",
                description="All leveling settings at a glance",
                default=(current == "overview")),
            discord.SelectOption(
                label="XP Settings",    value="xp",            emoji="📊",
                description="Toggle XP, multiplier, cooldown",
                default=(current == "xp")),
            discord.SelectOption(
                label="Channels & Voice", value="channels",     emoji="📡",
                description="Exclude channels from XP, enable voice XP",
                default=(current == "channels")),
            discord.SelectOption(
                label="Announcements",  value="announcements", emoji="📣",
                description="Level-up channel and custom message",
                default=(current == "announcements")),
            discord.SelectOption(
                label="Level Roles",    value="level_roles",   emoji="🎖️",
                description="Roles awarded on level-up",
                default=(current == "level_roles")),
            discord.SelectOption(
                label="Card Style",     value="card_style",    emoji="🎨",
                description="Customise level card colours",
                default=(current == "card_style")),
        ]
        super().__init__(
            placeholder="Navigate sections…", options=options,
            min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        panel = await _build_level_panel(self._cog, self._guild_id, self.values[0], interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvXPToggleBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, cfg: dict):
        self._cog      = cog
        self._guild_id = guild_id
        enabled = cfg.get("xp_enabled", True)
        super().__init__(
            label="XP Tracking",
            style=discord.ButtonStyle.green if enabled else discord.ButtonStyle.red,
            emoji=_lv_icon(enabled),
        )

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["xp_enabled"] = not cfg.get("xp_enabled", True)
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "xp", interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvXPSettingsModal(discord.ui.Modal, title="XP Settings"):
    multiplier = discord.ui.TextInput(label="XP Multiplier (e.g. 1.5)", placeholder="1.0")
    cooldown   = discord.ui.TextInput(label="Cooldown in seconds (0 = off)", placeholder="0")

    def __init__(self, cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog      = cog
        self._guild_id = guild_id
        self.multiplier.default = str(cfg.get("xp_multiplier", 1.0))
        self.cooldown.default   = str(cfg.get("xp_cooldown", 0))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            mult = round(max(0.1, float(self.multiplier.value)), 2)
            cd   = max(0, int(self.cooldown.value))
        except ValueError:
            return await interaction.response.send_message("Please enter valid numbers.", ephemeral=True)
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["xp_multiplier"] = mult
        cfg["xp_cooldown"]   = cd
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "xp", interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvEditXPBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(
            label="Edit XP Values", style=discord.ButtonStyle.blurple,
            emoji=get_emoji("settings"))

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        await interaction.response.send_modal(_LvXPSettingsModal(self._cog, self._guild_id, cfg))


# ── Channels & Voice ─────────────────────────────

class _LvExcludedChannelsSelect(discord.ui.ChannelSelect):
    def __init__(self, cog, guild_id: int, cfg: dict):
        super().__init__(
            placeholder="Add channels to exclude from XP…",
            channel_types=[
                discord.ChannelType.text,
                discord.ChannelType.voice,
                discord.ChannelType.news,
                discord.ChannelType.forum,
                discord.ChannelType.stage_voice,
            ],
            min_values=1, max_values=25,
        )
        self._cog      = cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        current = {int(cid) for cid in cfg.get("xp_excluded_channels") or []}
        current.update({int(channel.id) for channel in self.values})
        cfg["xp_excluded_channels"] = sorted(current)
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "channels", interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvRemoveExcludedSelect(discord.ui.Select):
    def __init__(self, cog, guild_id: int, options: list, message: discord.Message):
        super().__init__(
            placeholder="Choose channels to include again…",
            min_values=1, max_values=len(options),
            options=options,
        )
        self._cog      = cog
        self._guild_id = guild_id
        self.message   = message

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        removed = {int(value) for value in self.values}
        cfg["xp_excluded_channels"] = [
            cid for cid in cfg.get("xp_excluded_channels") or []
            if int(cid) not in removed
        ]
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('tick')} Removed `{len(removed)}` channel(s) from the XP exclusion list."
            ),
            accent_colour=discord.Color.green(),
        ))
        await interaction.response.edit_message(view=view)
        panel = await _build_level_panel(self._cog, self._guild_id, "channels", interaction.guild)
        await self.message.edit(view=panel)


class _LvRemoveExcludedBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, has_excluded: bool):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label="Remove Exclusion", style=discord.ButtonStyle.red, disabled=not has_excluded)

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        options = []
        for cid in cfg.get("xp_excluded_channels") or []:
            channel = interaction.guild.get_channel(int(cid))
            name = f"#{channel.name}" if channel else f"Channel {cid}"
            options.append(discord.SelectOption(
                label=name[:100],
                value=str(cid),
                description=f"Channel ID: {cid}",
            ))
        if not options:
            return await interaction.response.send_message(
                "No channels are excluded from XP.", ephemeral=True)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="Select the channels that should award XP again:"),
            discord.ui.ActionRow(
                _LvRemoveExcludedSelect(self._cog, self._guild_id, options[:25], interaction.message)
            ),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class _LvVCToggleBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, cfg: dict):
        self._cog      = cog
        self._guild_id = guild_id
        enabled = bool(cfg.get("xp_vc_enabled", False))
        super().__init__(
            label="Voice XP",
            style=discord.ButtonStyle.green if enabled else discord.ButtonStyle.red,
            emoji=_lv_icon(enabled),
        )

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["xp_vc_enabled"] = not bool(cfg.get("xp_vc_enabled", False))
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "channels", interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvClearExcludedBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, has_excluded: bool):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label="Clear Exclusions", style=discord.ButtonStyle.red, disabled=not has_excluded)

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["xp_excluded_channels"] = []
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "channels", interaction.guild)
        await interaction.response.edit_message(view=panel)


# ── Announcements ──────────────────────────────────

class _LvChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, cog, guild_id: int):
        super().__init__(
            placeholder="Choose a text channel…",
            channel_types=[discord.ChannelType.text],
            min_values=1, max_values=1,
        )
        self._cog      = cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0]
        cfg     = await self._cog._guild_cfg(self._guild_id)
        cfg["level_up_channel"] = channel.id
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        await interaction.response.edit_message(
            content=f"{get_emoji('tick')} Level-up announcements will now go to {channel.mention}.", view=None)


class _LvClearChannelBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label="Clear (use same channel)", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["level_up_channel"] = None
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        await interaction.response.edit_message(
            content=f"{get_emoji('tick')} Level-up announcements will now appear in the same channel as the message.", view=None)


class _LvSetChannelBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label="📺 Set Channel", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        view = discord.ui.View(timeout=60)
        view.add_item(_LvChannelSelect(self._cog, self._guild_id))
        view.add_item(_LvClearChannelBtn(self._cog, self._guild_id))
        await interaction.response.send_message(
            "Select the channel where level-up messages should appear:",
            view=view, ephemeral=True)


class _LvMessageModal(discord.ui.Modal, title="Custom Level-Up Message"):
    message = discord.ui.TextInput(
        label="Level-up message template",
        placeholder="Congratulations {mention}, you reached level **{level}**!",
        style=discord.TextStyle.paragraph,
        max_length=400,
    )

    def __init__(self, cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog      = cog
        self._guild_id = guild_id
        self.message.default = cfg.get("level_up_message") or ""

    async def on_submit(self, interaction: discord.Interaction):
        val = self.message.value.strip()
        if not val:
            return await interaction.response.send_message(
                "Message cannot be empty. Use the Reset button to restore the default.",
                ephemeral=True)
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["level_up_message"] = val
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "announcements", interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvEditMessageBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label="✏️ Edit Message", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        await interaction.response.send_modal(_LvMessageModal(self._cog, self._guild_id, cfg))


class _LvResetMessageBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, has_custom: bool):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label="↩️ Reset Message", style=discord.ButtonStyle.red, disabled=not has_custom)

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["level_up_message"] = None
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "announcements", interaction.guild)
        await interaction.response.edit_message(view=panel)


# ── Level Roles ────────────────────────────────────

class _LvRoleAssignSelect(discord.ui.RoleSelect):
    def __init__(self, cog, guild_id: int, level: int, message: discord.Message):
        super().__init__(placeholder="Choose a role to award…", min_values=1, max_values=1)
        self._cog      = cog
        self._guild_id = guild_id
        self._level    = level
        self.message   = message

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        cfg  = await self._cog._guild_cfg(self._guild_id)
        cfg.setdefault("level_roles", {})[str(self._level)] = role.id
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('tick')} **Level {self._level}** → {role.mention}"
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)
        panel = await _build_level_panel(self._cog, self._guild_id, "level_roles", interaction.guild)
        await self.message.edit(view=panel)


class _LvAddRoleModal(discord.ui.Modal, title="Add Level Role — Step 1/2"):
    level_num = discord.ui.TextInput(
        label="Level number", placeholder="e.g. 5",
        min_length=1, max_length=4,
    )

    def __init__(self, cog, guild_id: int):
        super().__init__()
        self._cog      = cog
        self._guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            lvl = max(1, int(self.level_num.value))
        except ValueError:
            return await interaction.response.send_message(
                "Please enter a valid whole number for the level.", ephemeral=True)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"Now select the role to award at **Level {lvl}**"
            ),
            discord.ui.ActionRow(
                _LvRoleAssignSelect(self._cog, self._guild_id, lvl, interaction.message)
            )
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


class _LvAddRoleBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label="Add Role", style=discord.ButtonStyle.green, emoji=get_emoji("plus"))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(_LvAddRoleModal(self._cog, self._guild_id))


class _LvRemoveRoleSelect(discord.ui.Select):
    def __init__(self, cog, guild_id: int, options: list, message: discord.Message):
        super().__init__(
            placeholder="Choose level role(s) to remove…",
            min_values=1, max_values=len(options),
            options=options,
        )
        self._cog      = cog
        self._guild_id = guild_id
        self.message   = message

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        lr  = cfg.setdefault("level_roles", {})
        for val in self.values:
            lr.pop(val, None)
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('tick')} Removed `{len(self.values)}` level role assignment(s)."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)
        panel = await _build_level_panel(self._cog, self._guild_id, "level_roles", interaction.guild)
        await self.message.edit(view=panel)


class _LvRemoveRoleBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, has_roles: bool):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label="➖ Remove Role", style=discord.ButtonStyle.red, disabled=not has_roles)

    async def callback(self, interaction: discord.Interaction):
        cfg   = await self._cog._guild_cfg(self._guild_id)
        lr    = cfg.get("level_roles", {})
        guild = interaction.guild
        options = []
        for lvl, rid in sorted(lr.items(), key=lambda x: int(x[0])):
            role  = guild.get_role(int(rid))
            rname = role.name if role else f"Role {rid}"
            options.append(discord.SelectOption(
                label=f"Level {lvl} — {rname[:80]}",
                value=str(lvl),
                description=f"Role ID: {rid}",
            ))
        if not options:
            return await interaction.response.send_message(
                "No level roles are configured.", ephemeral=True)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content="Select the level role assignments to remove:"
            ),
            discord.ui.ActionRow(
                _LvRemoveRoleSelect(self._cog, self._guild_id, options, interaction.message)
            )
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


# ── Card Style Colour Editor ──────────────────────

def _parse_colour(text: str) -> tuple[int, int, int] | None:
    """Parse a hex colour string like ``#d96545`` or ``ff5500`` into an RGB tuple, or None on failure."""
    text = text.strip().lstrip("#")
    if len(text) != 6:
        return None
    try:
        r, g, b = int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)
        return (r, g, b)
    except ValueError:
        return None


class _LvAccentColourModal(discord.ui.Modal, title="Accent Colour"):
    hex_colour = discord.ui.TextInput(
        label="Hex colour (e.g. #d96545 or ff5500)", placeholder="d96545",
        min_length=1, max_length=7,
    )

    def __init__(self, cog, guild_id: int):
        super().__init__()
        self._cog      = cog
        self._guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        rgb = _parse_colour(self.hex_colour.value)
        if rgb is None:
            return await interaction.response.send_message(
                "Invalid hex colour. Use format `#d96545` or `ff5500`.", ephemeral=True)
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["card_accent"] = list(rgb)
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "card_style", interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvBgTopModal(discord.ui.Modal, title="Background Top Colour"):
    hex_colour = discord.ui.TextInput(
        label="Hex colour (e.g. #261a16)", placeholder="261a16",
        min_length=1, max_length=7,
    )

    def __init__(self, cog, guild_id: int):
        super().__init__()
        self._cog      = cog
        self._guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        rgb = _parse_colour(self.hex_colour.value)
        if rgb is None:
            return await interaction.response.send_message(
                "Invalid hex colour. Use format `#261a16` or `261a16`.", ephemeral=True)
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["card_bg_top"] = list(rgb)
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "card_style", interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvBgBottomModal(discord.ui.Modal, title="Background Bottom Colour"):
    hex_colour = discord.ui.TextInput(
        label="Hex colour (e.g. #120c0a)", placeholder="120c0a",
        min_length=1, max_length=7,
    )

    def __init__(self, cog, guild_id: int):
        super().__init__()
        self._cog      = cog
        self._guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        rgb = _parse_colour(self.hex_colour.value)
        if rgb is None:
            return await interaction.response.send_message(
                "Invalid hex colour. Use format `#120c0a` or `120c0a`.", ephemeral=True)
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["card_bg_bottom"] = list(rgb)
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "card_style", interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvEditAccentBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label="✏️ Accent Colour", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(_LvAccentColourModal(self._cog, self._guild_id))


class _LvEditBgTopBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label="🌄 Background Top", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(_LvBgTopModal(self._cog, self._guild_id))


class _LvEditBgBottomBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label="🌅 Background Bottom", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(_LvBgBottomModal(self._cog, self._guild_id))


class _LvResetColoursBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label="↩️ Reset Colours", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["card_accent"]    = None
        cfg["card_bg_top"]    = None
        cfg["card_bg_bottom"] = None
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "card_style", interaction.guild)
        await interaction.response.edit_message(view=panel)


# ───────────────────────────────────────────────────
#  PANEL FACTORY
# ───────────────────────────────────────────────────

async def _build_level_panel(cog, guild_id: int, section: str = "overview",
                              guild: discord.Guild = None) -> discord.ui.LayoutView:
    cfg  = await cog._guild_cfg(guild_id)
    text = _lv_section_text(cfg, section, guild)

    view      = discord.ui.LayoutView(timeout=300)

    # Card accent for the CV2 container
    accent_rgb = cfg.get("card_accent")
    accent_colour = discord.Colour.from_rgb(*accent_rgb) if accent_rgb else discord.Colour(ACCENT_BRAND)

    container = discord.ui.Container(
        discord.ui.TextDisplay(content=text),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        accent_colour=accent_colour,
    )
    container.add_item(discord.ui.ActionRow(_LvSectionSelect(cog, guild_id, section)))

    if section == "xp":
        container.add_item(discord.ui.ActionRow(
            _LvXPToggleBtn(cog, guild_id, cfg),
            _LvEditXPBtn(cog, guild_id),
        ))

    elif section == "channels":
        container.add_item(discord.ui.ActionRow(
            _LvExcludedChannelsSelect(cog, guild_id, cfg),
        ))
        container.add_item(discord.ui.ActionRow(
            _LvVCToggleBtn(cog, guild_id, cfg),
            _LvRemoveExcludedBtn(cog, guild_id, bool(cfg.get("xp_excluded_channels"))),
            _LvClearExcludedBtn(cog, guild_id, bool(cfg.get("xp_excluded_channels"))),
        ))

    elif section == "announcements":
        has_custom = bool(cfg.get("level_up_message"))
        container.add_item(discord.ui.ActionRow(
            _LvSetChannelBtn(cog, guild_id),
        ))
        container.add_item(discord.ui.ActionRow(
            _LvEditMessageBtn(cog, guild_id),
            _LvResetMessageBtn(cog, guild_id, has_custom),
        ))

    elif section == "level_roles":
        has_roles = bool(cfg.get("level_roles"))
        container.add_item(discord.ui.ActionRow(
            _LvAddRoleBtn(cog, guild_id),
            _LvRemoveRoleBtn(cog, guild_id, has_roles),
        ))

    elif section == "card_style":
        container.add_item(discord.ui.ActionRow(
            _LvEditAccentBtn(cog, guild_id),
            _LvEditBgTopBtn(cog, guild_id),
        ))
        container.add_item(discord.ui.ActionRow(
            _LvEditBgBottomBtn(cog, guild_id),
            _LvResetColoursBtn(cog, guild_id),
        ))

    view.add_item(container)
    return view


# ───────────────────────────────────────────────────

__all__ = [k for k in list(globals()) if not k.startswith("__")]
