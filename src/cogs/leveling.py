import discord
from discord.ext import commands
import random
import json
import os
import time
from utils import logging as log
from utils.paginator import PaginatedView, paginate
from utils.ai_config import get_personality
from config.emojis import get_emoji

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
    "cafe": {
        "en": {
            "level_up":          "congratulations {mention}, you leveled up to level **{level}**! ☕✨",
            "no_xp":             "{name} hasn't brewed any XP yet ☕😔",
            "stats_title":       "☕ cozy level stats for {name}",
            "stats_level":       "vibe-level",
            "stats_xp":          "xp brewed",
            "stats_rank":        "café rank",
            "leaderboard_title": "☕ cozy leaderboard — {guild}",
            "leaderboard_empty": "no one has brewed any xp in this café yet 😭",
            "xp_disabled":       "xp tracking is off for this server ☕",
            "cfg_updated":       "✅ setting updated~",
            "cfg_show":          "### ☕ cozy level config — {guild}\n{body}",
        },
        "de": {
            "level_up":          "glückwunsch {mention}, du bist auf level **{level}** aufgestiegen! ☕✨",
            "no_xp":             "{name} hat noch keine XP aufgebrüht ☕😔",
            "stats_title":       "☕ gemütliche level-statistiken für {name}",
            "stats_level":       "vibe-level",
            "stats_xp":          "aufgebrühte xp",
            "stats_rank":        "café-rang",
            "leaderboard_title": "☕ gemütliche bestenliste — {guild}",
            "leaderboard_empty": "niemand hat hier bisher xp aufgebrüht 😭",
            "xp_disabled":       "xp-tracking ist für diesen server deaktiviert ☕",
            "cfg_updated":       "✅ einstellung aktualisiert~",
            "cfg_show":          "### ☕ gemütliche level-config — {guild}\n{body}",
        },
        "es": {
            "level_up":          "¡felicidades {mention}, subiste al nivel **{level}**! ☕✨",
            "no_xp":             "{name} aún no ha preparado nada de xp ☕😔",
            "stats_title":       "☕ estadísticas acogedoras de nivel para {name}",
            "stats_level":       "nivel-vibe",
            "stats_xp":          "xp preparada",
            "stats_rank":        "rango del café",
            "leaderboard_title": "☕ tabla acogedora — {guild}",
            "leaderboard_empty": "nadie ha preparado xp en este café todavía 😭",
            "xp_disabled":       "el sistema de xp está apagado en este servidor ☕",
            "cfg_updated":       "✅ configuración actualizada~",
            "cfg_show":          "### ☕ config acogedora de niveles — {guild}\n{body}",
        },
    },
}


def get_lang(ctx):
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
        if str(ctx.guild.preferred_locale).lower().startswith("es"):
            return "es"
    return "en"


def msg(ctx, key, **kwargs):
    personality = get_personality(ctx)
    lang = get_lang(ctx)
    block = MESSAGES.get(personality, {}).get(lang, {})
    text = block.get(key)
    if text is None:
        text = MESSAGES.get(personality, {}).get("en", {}).get(key)
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key)
    if text is None:
        text = MESSAGES["normal"]["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text


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
}


# ───────────────────────────────────────────────────
#  PANEL TEXT BUILDERS  (purely sync, receive cfg dict)
# ───────────────────────────────────────────────────

def _lv_icon(val) -> str:
    return get_emoji("icon_tick") if val else get_emoji("icon_cross")


def _lv_overview_text(cfg: dict, guild: discord.Guild) -> str:
    lu_ch   = guild.get_channel(cfg.get("level_up_channel") or 0)
    lu_ch_s = lu_ch.mention if lu_ch else "*(same channel)*"
    lr      = cfg.get("level_roles", {})
    lr_s    = ", ".join(
        f"Lv.{lvl}→{(guild.get_role(int(rid)) or discord.Object(rid)).mention}"
        for lvl, rid in sorted(lr.items(), key=lambda x: int(x[0]))
    ) or "*none*"
    custom_msg = cfg.get("level_up_message")
    msg_s = f"`{custom_msg}`" if custom_msg else "*(default café message)*"

    return (
        "### ☕ Leveling Management Panel\n"
        "Manage all your server's leveling settings from one cozy place.\n\n"
        "**📊 XP Settings**\n"
        f"{_lv_icon(cfg.get('xp_enabled', True))} XP enabled  •  "
        f"Multiplier: `{cfg.get('xp_multiplier', 1.0)}x`  •  "
        f"Cooldown: `{cfg.get('xp_cooldown', 0)}s`\n\n"
        "**📣 Announcements**\n"
        f"Level-up channel: {lu_ch_s}\n"
        f"Custom message: {msg_s}\n\n"
        "**🎖️ Level Roles** *(automatically awarded on level-up)*\n"
        f"{lr_s}\n\n"
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
        "Minimum time between XP gains per member (0 = every message)."
    )


def _lv_announcements_text(cfg: dict, guild: discord.Guild) -> str:
    lu_ch      = guild.get_channel(cfg.get("level_up_channel") or 0)
    lu_ch_s    = lu_ch.mention if lu_ch else "*(same channel as the message)*"
    custom_msg = cfg.get("level_up_message")
    default_msg = "congratulations {mention}, you leveled up to level **{level}**! ☕✨"
    msg_display = custom_msg if custom_msg else default_msg
    return (
        "### 📣 Announcement Settings\n"
        "Configure where and how level-ups are announced.\n\n"
        f"**Level-Up Channel:** {lu_ch_s}\n"
        "-# Select a channel below or clear it to announce in the message's channel.\n\n"
        "**Level-Up Message:**\n"
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
        f"-# Click **{get_emoji('icon_plus')} Add Role** to assign a role to a level.\n"
        "-# Click **➖ Remove Role** to remove an assignment."
    )


def _lv_section_text(cfg: dict, section: str, guild: discord.Guild) -> str:
    if section == "xp":            return _lv_xp_text(cfg)
    if section == "announcements": return _lv_announcements_text(cfg, guild)
    if section == "level_roles":   return _lv_roles_text(cfg, guild)
    return _lv_overview_text(cfg, guild)


# ───────────────────────────────────────────────────
#  PANEL INTERACTIVE COMPONENTS  (all receive cfg where needed)
# ───────────────────────────────────────────────────

class _LvSectionSelect(discord.ui.Select):
    def __init__(self, cog, guild_id: int, current: str):
        self._cog      = cog
        self._guild_id = guild_id
        options = [
            discord.SelectOption(
                label="Overview",       value="overview",      emoji="☕",
                description="All leveling settings at a glance",
                default=(current == "overview")),
            discord.SelectOption(
                label="XP Settings",    value="xp",            emoji="📊",
                description="Toggle XP, multiplier, cooldown",
                default=(current == "xp")),
            discord.SelectOption(
                label="Announcements",  value="announcements", emoji="📣",
                description="Level-up channel and custom message",
                default=(current == "announcements")),
            discord.SelectOption(
                label="Level Roles",    value="level_roles",   emoji="🎖️",
                description="Roles awarded on level-up",
                default=(current == "level_roles")),
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
            emoji=get_emoji("icon_settings"))

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        await interaction.response.send_modal(_LvXPSettingsModal(self._cog, self._guild_id, cfg))


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
            content=f"{get_emoji('icon_tick')} Level-up announcements will now go to {channel.mention}.", view=None)


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
            content=f"{get_emoji('icon_tick')} Level-up announcements will now appear in the same channel as the message.",
            view=None)


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
        placeholder="congratulations {mention}, you reached level **{level}**! ☕",
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
                "Message cannot be empty. Use the Reset button to restore the default.", ephemeral=True)
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
                content=f"{get_emoji('icon_tick')} **Level {self._level}** → {role.mention}"
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
        super().__init__(label="Add Role", style=discord.ButtonStyle.green, emoji=get_emoji("icon_plus"))

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
                content=f"{get_emoji('icon_tick')} Removed `{len(self.values)}` level role assignment(s)."
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


# ───────────────────────────────────────────────────
#  PANEL FACTORY  (async — fetches cfg from DB)
# ───────────────────────────────────────────────────
async def _build_level_panel(cog, guild_id: int, section: str = "overview",
                              guild: discord.Guild = None) -> discord.ui.LayoutView:
    cfg  = await cog._guild_cfg(guild_id)
    text = _lv_section_text(cfg, section, guild)

    view      = discord.ui.LayoutView(timeout=300)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=text),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
    )
    container.add_item(discord.ui.ActionRow(_LvSectionSelect(cog, guild_id, section)))

    if section == "xp":
        container.add_item(discord.ui.ActionRow(
            _LvXPToggleBtn(cog, guild_id, cfg),
            _LvEditXPBtn(cog, guild_id),
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

    view.add_item(container)
    return view


# ───────────────────────────────────────────────────
#  LEVELING COG
# ───────────────────────────────────────────────────

class Leveling(commands.Cog):
    """Cozy bilingual leveling system with guild config support."""

    def __init__(self, bot):
        self.bot = bot
        self._cooldown_cache: dict = {}

    async def cog_load(self):
        """Migrate legacy JSON data into the central database (one-time)."""
        await self._migrate_levels_json()
        await self._migrate_level_config_json()

    # ── DB HELPERS ─────────────────────────────────

    async def _guild_cfg(self, guild_id) -> dict:
        """Return the level config dict for a guild, falling back to defaults."""
        gid = int(guild_id)
        row = await self.bot.cxn.fetchrow(
            "SELECT * FROM level_config WHERE guild_id = $1", gid
        )
        cfg = dict(DEFAULT_GUILD_LEVEL_CONFIG)
        if row:
            cfg["xp_enabled"]       = bool(row["xp_enabled"])
            cfg["xp_multiplier"]    = row["xp_multiplier"]
            cfg["xp_cooldown"]      = row["xp_cooldown"]
            cfg["level_up_channel"] = row["level_up_channel"]
            cfg["level_up_message"] = row["level_up_message"]
            try:
                cfg["level_roles"] = json.loads(row["level_roles"] or "{}")
            except Exception:
                cfg["level_roles"] = {}
        return cfg

    async def _save_guild_cfg(self, guild_id, cfg: dict):
        gid = int(guild_id)
        await self.bot.cxn.execute(
            "INSERT OR REPLACE INTO level_config "
            "(guild_id, xp_enabled, xp_multiplier, xp_cooldown, "
            " level_up_channel, level_up_message, level_roles) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7)",
            gid,
            int(cfg.get("xp_enabled", True)),
            cfg.get("xp_multiplier", 1.0),
            cfg.get("xp_cooldown", 0),
            cfg.get("level_up_channel"),
            cfg.get("level_up_message"),
            json.dumps(cfg.get("level_roles", {})),
        )

    async def _get_user_data(self, guild_id, user_id) -> dict:
        row = await self.bot.cxn.fetchrow(
            "SELECT xp, level FROM levels WHERE guild_id = $1 AND user_id = $2",
            int(guild_id), int(user_id)
        )
        return {"xp": row["xp"], "level": row["level"]} if row else {"xp": 0, "level": 0}

    async def _save_user_data(self, guild_id, user_id, xp: int, level: int):
        await self.bot.cxn.execute(
            "INSERT OR REPLACE INTO levels (guild_id, user_id, xp, level) VALUES ($1, $2, $3, $4)",
            int(guild_id), int(user_id), xp, level
        )

    async def _get_guild_leaderboard(self, guild_id) -> list:
        return await self.bot.cxn.fetch(
            "SELECT user_id, xp, level FROM levels "
            "WHERE guild_id = $1 ORDER BY level DESC, xp DESC",
            int(guild_id)
        )

    async def _get_user_rank(self, guild_id, user_id) -> int:
        rows = await self.bot.cxn.fetch(
            "SELECT user_id FROM levels WHERE guild_id = $1 ORDER BY level DESC, xp DESC",
            int(guild_id)
        )
        for i, row in enumerate(rows, 1):
            if row["user_id"] == int(user_id):
                return i
        return len(rows) or 1

    # ── MIGRATION HELPERS ──────────────────────────

    async def _migrate_levels_json(self):
        path = "data/levels.json"
        if not os.path.exists(path):
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
            count = 0
            for guild_id, users in data.items():
                for user_id, ud in users.items():
                    existing = await self.bot.cxn.fetchval(
                        "SELECT 1 FROM levels WHERE guild_id = $1 AND user_id = $2",
                        int(guild_id), int(user_id)
                    )
                    if not existing:
                        await self._save_user_data(guild_id, user_id,
                                                   ud.get("xp", 0), ud.get("level", 0))
                        count += 1
            if count:
                log.info("Leveling", f"Migrated {count} records from levels.json → database.db")
            os.rename(path, path + ".migrated")
        except Exception as e:
            log.warning("Leveling", f"Could not migrate levels.json: {e}")

    async def _migrate_level_config_json(self):
        path = "data/level_config.json"
        if not os.path.exists(path):
            return
        try:
            with open(path, "r") as f:
                configs = json.load(f)
            count = 0
            for guild_id, cfg in configs.items():
                existing = await self.bot.cxn.fetchval(
                    "SELECT 1 FROM level_config WHERE guild_id = $1", int(guild_id)
                )
                if not existing:
                    await self._save_guild_cfg(guild_id, cfg)
                    count += 1
            if count:
                log.info("Leveling", f"Migrated {count} guild configs from level_config.json → database.db")
            os.rename(path, path + ".migrated")
        except Exception as e:
            log.warning("Leveling", f"Could not migrate level_config.json: {e}")

    # ── XP FORMULA ─────────────────────────────────

    def get_xp_for_level(self, level: int) -> int:
        return 5 * (level ** 2) + (50 * level) + 100

    # ── XP EVENT ───────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id
        user_id  = message.author.id
        cfg      = await self._guild_cfg(guild_id)

        if not cfg.get("xp_enabled", True):
            return

        # Cooldown check (in-memory)
        cooldown = cfg.get("xp_cooldown", 0)
        if cooldown > 0:
            cache_key = f"{guild_id}:{user_id}"
            last_xp   = self._cooldown_cache.get(cache_key, 0)
            now       = time.time()
            if now - last_xp < cooldown:
                return
            self._cooldown_cache[cache_key] = now

        user_data     = await self._get_user_data(guild_id, user_id)
        multiplier    = cfg.get("xp_multiplier", 1.0)
        xp_gain       = int(random.randint(15, 25) * multiplier)
        current_xp    = user_data["xp"] + xp_gain
        current_level = user_data["level"]
        next_level_xp = self.get_xp_for_level(current_level)

        if current_xp >= next_level_xp:
            current_level += 1
            current_xp     = 0
            await self._save_user_data(guild_id, user_id, current_xp, current_level)

            lu_channel_id = cfg.get("level_up_channel")
            lu_channel    = (
                message.guild.get_channel(lu_channel_id) if lu_channel_id else message.channel
            )

            try:
                custom_template = cfg.get("level_up_message")
                if custom_template:
                    lu_text = custom_template.format(
                        mention=message.author.mention,
                        level=current_level,
                        name=message.author.display_name,
                        guild=message.guild.name,
                    )
                else:
                    lu_text = msg(message, "level_up",
                                  mention=message.author.mention, level=current_level)
                view = discord.ui.LayoutView()
                view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=lu_text)))
                if lu_channel:
                    await lu_channel.send(view=view)
                log.debug("Leveling", f"User {message.author} leveled up to {current_level} in {message.guild.name}")
            except discord.Forbidden:
                pass

            # Assign level roles
            level_roles = cfg.get("level_roles", {})
            role_id = level_roles.get(str(current_level))
            if role_id:
                role = message.guild.get_role(int(role_id))
                if role:
                    try:
                        await message.author.add_roles(role, reason=f"Level-up reward: level {current_level}")
                    except Exception:
                        pass
        else:
            await self._save_user_data(guild_id, user_id, current_xp, current_level)

    # ── RANK COMMAND ───────────────────────────────

    @commands.hybrid_command(
        name="level",
        aliases=["rank"],
        description="Check your cozy level stats",
        help="{ 'en': 'Check your cozy level stats ☕', 'de': 'Zeigt deine Level-Statistiken.', 'es': 'Consulta tus estadísticas de nivel ☕' }"
    )
    async def level(self, ctx, member: discord.Member = None):
        member   = member or ctx.author
        guild_id = ctx.guild.id
        user_id  = member.id

        cfg = await self._guild_cfg(guild_id)
        if not cfg.get("xp_enabled", True):
            return await ctx.send(msg(ctx, "xp_disabled"))

        user_data = await self._get_user_data(guild_id, user_id)
        if user_data["xp"] == 0 and user_data["level"] == 0:
            existing = await self.bot.cxn.fetchval(
                "SELECT 1 FROM levels WHERE guild_id = $1 AND user_id = $2",
                int(guild_id), int(user_id)
            )
            if not existing:
                return await ctx.send(msg(ctx, "no_xp", name=member.display_name))

        current_level = user_data["level"]
        current_xp    = user_data["xp"]
        next_level_xp = self.get_xp_for_level(current_level)
        rank          = await self._get_user_rank(guild_id, user_id)

        text = (
            f"### {msg(ctx, 'stats_title', name=member.display_name)}\n"
            f"**{msg(ctx, 'stats_level')}:** {current_level}\n"
            f"**{msg(ctx, 'stats_xp')}:** {current_xp}/{next_level_xp}\n"
            f"**{msg(ctx, 'stats_rank')}:** #{rank}"
        )

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(content=text),
                accessory=discord.ui.Thumbnail(member.display_avatar.url)
            )
        ))
        await ctx.send(view=view)

    # ── LEADERBOARD ────────────────────────────────

    @commands.command(
        name="level-leaderboard",
        aliases=["lvl-lb"],
        help="{ 'en': 'View the cozy leaderboard ☕', 'de': 'Zeigt die Level-Bestenliste.' }"
    )
    async def leaderboard(self, ctx):
        guild_id = ctx.guild.id

        cfg = await self._guild_cfg(guild_id)
        if not cfg.get("xp_enabled", True):
            return await ctx.send(msg(ctx, "xp_disabled"))

        rows = await self._get_guild_leaderboard(guild_id)
        if not rows:
            return await ctx.send(msg(ctx, "leaderboard_empty"))

        lines = []
        for i, row in enumerate(rows, start=1):
            user  = self.bot.get_user(row["user_id"])
            name  = user.display_name if user else f"User {row['user_id']}"
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"**{i}.**")
            lines.append(f"{medal} {name} — Level {row['level']} ({row['xp']} XP)")

        pages = paginate(lines, per_page=10)
        view  = PaginatedView(
            title=msg(ctx, "leaderboard_title", guild=ctx.guild.name),
            pages=pages,
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None,
        )
        await ctx.send(view=view)

    # ── LEVELCONFIG COMMAND GROUP ──────────────────

    @commands.group(
        name="levelconfig",
        aliases=["lvlcfg"],
        invoke_without_command=True,
        help="{ 'en': 'View or configure the leveling system.', 'de': 'Level-Einstellungen anzeigen / bearbeiten.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig(self, ctx):
        guild_id = ctx.guild.id
        cfg      = await self._guild_cfg(guild_id)

        lu_ch     = ctx.guild.get_channel(cfg.get("level_up_channel") or 0)
        lu_ch_str = lu_ch.mention if lu_ch else "*(same channel)*"
        lr        = cfg.get("level_roles", {})
        lr_lines  = "\n".join(
            f"  Level {lvl}: {ctx.guild.get_role(int(rid)).mention if ctx.guild.get_role(int(rid)) else rid}"
            for lvl, rid in sorted(lr.items(), key=lambda x: int(x[0]))
        ) or "  *(none)*"

        body = (
            f"**XP Enabled:** {get_emoji('icon_tick') if cfg.get('xp_enabled', True) else get_emoji('icon_cross')}\n"
            f"**XP Multiplier:** `{cfg.get('xp_multiplier', 1.0)}x`\n"
            f"**XP Cooldown:** `{cfg.get('xp_cooldown', 0)}s`\n"
            f"**Level-Up Channel:** {lu_ch_str}\n"
            f"**Level Roles:**\n{lr_lines}"
        )

        text = msg(ctx, "cfg_show", guild=ctx.guild.name, body=body)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
        await ctx.send(view=view)

    @levelconfig.command(
        name="toggle", 
        help="{ 'en': 'Enable or disable XP for this server.', 'de': 'XP für diesen Server aktivieren/deaktivieren.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_toggle(self, ctx):
        cfg = await self._guild_cfg(ctx.guild.id)
        cfg["xp_enabled"] = not cfg.get("xp_enabled", True)
        await self._save_guild_cfg(ctx.guild.id, cfg)
        state = f"{get_emoji('icon_tick')} enabled" if cfg["xp_enabled"] else f"{get_emoji('icon_cross')} disabled"
        await ctx.send(f"XP tracking is now **{state}** for this server.")

    @levelconfig.command(
        name="multiplier", 
        aliases=["xpmultiplier"],
        help="{ 'en': 'Set XP gain multiplier (e.g. 2.0).', 'de': 'XP-Verstärkung einstellen (z.B. 2.0).' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_multiplier(self, ctx, value: float = None):
        if value is None or value <= 0:
            return await ctx.send("Please provide a positive multiplier (e.g. `1.5`).")
        cfg = await self._guild_cfg(ctx.guild.id)
        cfg["xp_multiplier"] = round(value, 2)
        await self._save_guild_cfg(ctx.guild.id, cfg)
        await ctx.send(msg(ctx, "cfg_updated") + f" XP multiplier → `{cfg['xp_multiplier']}x`")

    @levelconfig.command(
        name="cooldown",
        help="{ 'en': 'Set XP cooldown between gains in seconds (0 = off).', 'de': 'XP-Cooldown in Sekunden einstellen (0 = aus).' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_cooldown(self, ctx, seconds: int = None):
        if seconds is None or seconds < 0:
            return await ctx.send("Please provide a non-negative number of seconds.")
        cfg = await self._guild_cfg(ctx.guild.id)
        cfg["xp_cooldown"] = seconds
        await self._save_guild_cfg(ctx.guild.id, cfg)
        status = f"`{seconds}s`" if seconds > 0 else "off"
        await ctx.send(msg(ctx, "cfg_updated") + f" XP cooldown → {status}")

    @levelconfig.command(
        name="levelupchannel", 
        aliases=["luchannel"],
        help="{ 'en': 'Set the level-up announcement channel.', 'de': 'Level-Up-Benachrichtigungs-Kanal einstellen.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_channel(self, ctx, channel: discord.TextChannel = None):
        cfg = await self._guild_cfg(ctx.guild.id)
        cfg["level_up_channel"] = channel.id if channel else None
        await self._save_guild_cfg(ctx.guild.id, cfg)
        dest = channel.mention if channel else "*(same channel)*"
        await ctx.send(msg(ctx, "cfg_updated") + f" Level-up channel → {dest}")

    @levelconfig.command(
        name="levelrole", 
        aliases=["role"],
        help="{ 'en': 'Assign a role when a level is reached.', 'de': 'Rolle bei Erreichen eines Levels zuweisen.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_levelrole(self, ctx, level: int = None, role: discord.Role = None):
        if level is None or level < 1:
            return await ctx.send("Please specify a valid level (e.g. `5`).")
        cfg = await self._guild_cfg(ctx.guild.id)
        lr  = cfg.setdefault("level_roles", {})
        if role is None:
            lr.pop(str(level), None)
            await self._save_guild_cfg(ctx.guild.id, cfg)
            await ctx.send(msg(ctx, "cfg_updated") + f" Removed level role for level {level}.")
        else:
            lr[str(level)] = role.id
            await self._save_guild_cfg(ctx.guild.id, cfg)
            await ctx.send(msg(ctx, "cfg_updated") + f" Level {level} → {role.mention}")

    @levelconfig.command(
        name="resetuser", 
        help="{ 'en': 'Reset XP and level for a member.', 'de': 'XP und Level eines Mitglieds zurücksetzen.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_resetuser(self, ctx, member: discord.Member = None):
        if not member:
            return await ctx.send("Please specify a member.")
        await self._save_user_data(ctx.guild.id, member.id, 0, 0)
        await ctx.send(f"{get_emoji('icon_tick')} Reset XP and level for **{member.display_name}**.")

    # ── LEVELING PANEL ─────────────────────────────

    @commands.command(
        name="levelpanel",
        aliases=["lvlpanel", "lp"],
        help="{ 'en': 'Open the interactive leveling management panel ☕', 'de': 'Leveling-Dashboard öffnen.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelpanel(self, ctx):
        panel = await _build_level_panel(self, ctx.guild.id, "overview", ctx.guild)
        await ctx.send(view=panel)


async def setup(bot):
    await bot.add_cog(Leveling(bot))
