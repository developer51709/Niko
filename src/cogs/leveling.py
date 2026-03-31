# leveling.py
# Bilingual EN/DE, café personality, cv2 LayoutView responses.
# Supports per-guild config: XP toggle, multiplier, cooldown, level-up channel, level roles.

import discord
from discord.ext import commands
import random
import json
import os
import time
from utils import logging as log
from utils.paginator import PaginatedView, paginate
from config.emojis import get_emoji

PERSONALITY = "cafe"

# ─────────────────────────────────────────────────────────────
#  MESSAGE TABLE
# ─────────────────────────────────────────────────────────────

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
    },
}


def get_lang(ctx):
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"


def get_personality():
    return PERSONALITY if PERSONALITY in MESSAGES else "normal"


def msg(ctx, key, **kwargs):
    personality = get_personality()
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


# ─────────────────────────────────────────────────────────────
#  GUILD CONFIG
# ─────────────────────────────────────────────────────────────

LEVEL_CONFIG_PATH = "data/level_config.json"

DEFAULT_GUILD_LEVEL_CONFIG = {
    "xp_enabled":       True,
    "xp_multiplier":    1.0,
    "xp_cooldown":      0,
    "level_up_channel": None,
    "level_up_message": None,
    "level_roles":      {},
}


def _load_level_config() -> dict:
    if os.path.exists(LEVEL_CONFIG_PATH):
        try:
            with open(LEVEL_CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_level_config(data: dict):
    os.makedirs("data", exist_ok=True)
    with open(LEVEL_CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)


def _get_guild_level_cfg(configs: dict, guild_id: str) -> dict:
    if guild_id not in configs:
        import copy
        configs[guild_id] = copy.deepcopy(DEFAULT_GUILD_LEVEL_CONFIG)
    else:
        for k, v in DEFAULT_GUILD_LEVEL_CONFIG.items():
            configs[guild_id].setdefault(k, v)
    return configs[guild_id]


# ─────────────────────────────────────────────────────────────
#  PANEL TEXT BUILDERS
# ─────────────────────────────────────────────────────────────

def _lv_icon(val) -> str:
    return get_emoji("icon_tick") if val else get_emoji("icon_cross")


def _lv_overview_text(cfg: dict, guild: discord.Guild) -> str:
    lu_ch    = guild.get_channel(cfg.get("level_up_channel") or 0)
    lu_ch_s  = lu_ch.mention if lu_ch else "*(same channel)*"
    lr       = cfg.get("level_roles", {})
    lr_s     = ", ".join(
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
    lu_ch   = guild.get_channel(cfg.get("level_up_channel") or 0)
    lu_ch_s = lu_ch.mention if lu_ch else "*(same channel as the message)*"
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
    if section == "xp":             return _lv_xp_text(cfg)
    if section == "announcements":  return _lv_announcements_text(cfg, guild)
    if section == "level_roles":    return _lv_roles_text(cfg, guild)
    return _lv_overview_text(cfg, guild)


# ─────────────────────────────────────────────────────────────
#  PANEL INTERACTIVE COMPONENTS
# ─────────────────────────────────────────────────────────────

class _LvSectionSelect(discord.ui.Select):
    def __init__(self, cog, guild_id: int, current: str):
        self._cog      = cog
        self._guild_id = guild_id
        options = [
            discord.SelectOption(label="Overview",        value="overview",       emoji="☕",
                                 description="All leveling settings at a glance",
                                 default=(current == "overview")),
            discord.SelectOption(label="XP Settings",     value="xp",             emoji="📊",
                                 description="Toggle XP, multiplier, cooldown",
                                 default=(current == "xp")),
            discord.SelectOption(label="Announcements",   value="announcements",  emoji="📣",
                                 description="Level-up channel and custom message",
                                 default=(current == "announcements")),
            discord.SelectOption(label="Level Roles",     value="level_roles",    emoji="🎖️",
                                 description="Roles awarded on level-up",
                                 default=(current == "level_roles")),
        ]
        super().__init__(placeholder="Navigate sections…", options=options,
                         min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        panel = _build_level_panel(self._cog, self._guild_id, self.values[0], interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvXPToggleBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int):
        self._cog      = cog
        self._guild_id = guild_id
        cfg     = cog._guild_cfg(str(guild_id))
        enabled = cfg.get("xp_enabled", True)
        super().__init__(
            label=f"XP Tracking",
            style=discord.ButtonStyle.green if enabled else discord.ButtonStyle.red,
            emoji=_lv_icon(enabled)
        )

    async def callback(self, interaction: discord.Interaction):
        cfg = self._cog._guild_cfg(str(self._guild_id))
        cfg["xp_enabled"] = not cfg.get("xp_enabled", True)
        self._cog._save_configs()
        await interaction.response.edit_message(
            view=_build_level_panel(self._cog, self._guild_id, "xp", interaction.guild))


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
            return await interaction.response.send_message(
                "Please enter valid numbers.", ephemeral=True)
        cfg = self._cog._guild_cfg(str(self._guild_id))
        cfg["xp_multiplier"] = mult
        cfg["xp_cooldown"]   = cd
        self._cog._save_configs()
        await interaction.response.edit_message(
            view=_build_level_panel(self._cog, self._guild_id, "xp", interaction.guild))


class _LvEditXPBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(
            label="Edit XP Values", 
            style=discord.ButtonStyle.blurple, 
            emoji=get_emoji("icon_settings")
        )

    async def callback(self, interaction: discord.Interaction):
        cfg = self._cog._guild_cfg(str(self._guild_id))
        await interaction.response.send_modal(_LvXPSettingsModal(self._cog, self._guild_id, cfg))


# ── Announcements ──────────────────────────────────────────

class _LvChannelSelect(discord.ui.ChannelSelect):
    """Ephemeral select — set the level-up channel."""
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
        cfg     = self._cog._guild_cfg(str(self._guild_id))
        cfg["level_up_channel"] = channel.id
        self._cog._save_configs()
        await interaction.response.edit_message(
            content=f"{get_emoji('icon_tick')} Level-up announcements will now go to {channel.mention}.", view=None)


class _LvClearChannelBtn(discord.ui.Button):
    """Inside the ephemeral channel picker — resets to same-channel."""
    def __init__(self, cog, guild_id: int):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label="Clear (use same channel)", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        cfg = self._cog._guild_cfg(str(self._guild_id))
        cfg["level_up_channel"] = None
        self._cog._save_configs()
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
        current = cfg.get("level_up_message") or ""
        self.message.default = current

    async def on_submit(self, interaction: discord.Interaction):
        val = self.message.value.strip()
        if not val:
            return await interaction.response.send_message(
                "Message cannot be empty. Use the Reset button to restore the default.", ephemeral=True)
        cfg = self._cog._guild_cfg(str(self._guild_id))
        cfg["level_up_message"] = val
        self._cog._save_configs()
        await interaction.response.edit_message(
            view=_build_level_panel(self._cog, self._guild_id, "announcements", interaction.guild))


class _LvEditMessageBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label="✏️ Edit Message", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        cfg = self._cog._guild_cfg(str(self._guild_id))
        await interaction.response.send_modal(_LvMessageModal(self._cog, self._guild_id, cfg))


class _LvResetMessageBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, has_custom: bool):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(
            label="↩️ Reset Message",
            style=discord.ButtonStyle.red,
            disabled=not has_custom,
        )

    async def callback(self, interaction: discord.Interaction):
        cfg = self._cog._guild_cfg(str(self._guild_id))
        cfg["level_up_message"] = None
        self._cog._save_configs()
        await interaction.response.edit_message(
            view=_build_level_panel(self._cog, self._guild_id, "announcements", interaction.guild))


# ── Level Roles ─────────────────────────────────────────────

class _LvRoleAssignSelect(discord.ui.RoleSelect):
    """Step 2 of adding a level role — picks the role after the level was entered."""
    def __init__(self, cog, guild_id: int, level: int):
        super().__init__(placeholder="Choose a role to award…", min_values=1, max_values=1)
        self._cog      = cog
        self._guild_id = guild_id
        self._level    = level

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        cfg  = self._cog._guild_cfg(str(self._guild_id))
        cfg.setdefault("level_roles", {})[str(self._level)] = role.id
        self._cog._save_configs()
        await interaction.response.edit_message(
            content=f"{get_emoji('icon_tick')} **Level {self._level}** → {role.mention}", view=None)


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
        view = discord.ui.View(timeout=60)
        view.add_item(_LvRoleAssignSelect(self._cog, self._guild_id, lvl))
        await interaction.response.send_message(
            f"Now select the role to award at **Level {lvl}**:",
            view=view, ephemeral=True)


class _LvAddRoleBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(
            label="Add Role", 
            style=discord.ButtonStyle.green, 
            emoji=get_emoji("icon_plus")
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(_LvAddRoleModal(self._cog, self._guild_id))


class _LvRemoveRoleSelect(discord.ui.Select):
    """Ephemeral select — remove a level role assignment."""
    def __init__(self, cog, guild_id: int, options: list):
        super().__init__(
            placeholder="Choose level role(s) to remove…",
            min_values=1, max_values=len(options),
            options=options,
        )
        self._cog      = cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        cfg = self._cog._guild_cfg(str(self._guild_id))
        lr  = cfg.setdefault("level_roles", {})
        for val in self.values:
            lr.pop(val, None)
        self._cog._save_configs()
        await interaction.response.edit_message(
            content=f"{get_emoji('icon_tick')} Removed `{len(self.values)}` level role assignment(s).", view=None)


class _LvRemoveRoleBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, has_roles: bool):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(
            label="➖ Remove Role",
            style=discord.ButtonStyle.red,
            disabled=not has_roles,
        )

    async def callback(self, interaction: discord.Interaction):
        cfg = self._cog._guild_cfg(str(self._guild_id))
        lr  = cfg.get("level_roles", {})
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
        view = discord.ui.View(timeout=60)
        view.add_item(_LvRemoveRoleSelect(self._cog, self._guild_id, options))
        await interaction.response.send_message(
            "Select the level role assignments to remove:",
            view=view, ephemeral=True)


# ─────────────────────────────────────────────────────────────
#  PANEL FACTORY
# ─────────────────────────────────────────────────────────────

def _build_level_panel(cog, guild_id: int, section: str = "overview",
                       guild: discord.Guild = None) -> discord.ui.LayoutView:
    cfg  = cog._guild_cfg(str(guild_id))
    text = _lv_section_text(cfg, section, guild)

    view      = discord.ui.LayoutView(timeout=300)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=text),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
    )
    container.add_item(discord.ui.ActionRow(_LvSectionSelect(cog, guild_id, section)))

    if section == "xp":
        container.add_item(discord.ui.ActionRow(
            _LvXPToggleBtn(cog, guild_id),
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


# ─────────────────────────────────────────────────────────────
#  LEVELING COG
# ─────────────────────────────────────────────────────────────

class Leveling(commands.Cog):
    """Cozy bilingual leveling system with guild config support."""

    def __init__(self, bot):
        self.bot = bot
        self.data_path = "data/levels.json"
        self.levels = self._load_levels()
        self.level_configs = _load_level_config()
        self._cooldown_cache: dict[str, float] = {}

    def _load_levels(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                return json.load(f)
        return {}

    def _save_levels(self):
        with open(self.data_path, "w") as f:
            json.dump(self.levels, f, indent=4)

    def _save_configs(self):
        _save_level_config(self.level_configs)

    def _guild_cfg(self, guild_id: str) -> dict:
        return _get_guild_level_cfg(self.level_configs, guild_id)

    def get_xp_for_level(self, level: int) -> int:
        return 5 * (level ** 2) + (50 * level) + 100

    # ─── XP EVENT ────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        guild_id = str(message.guild.id)
        user_id  = str(message.author.id)
        cfg      = self._guild_cfg(guild_id)

        if not cfg.get("xp_enabled", True):
            return

        # Cooldown check
        cooldown = cfg.get("xp_cooldown", 0)
        if cooldown > 0:
            cache_key = f"{guild_id}:{user_id}"
            last_xp = self._cooldown_cache.get(cache_key, 0)
            now = time.time()
            if now - last_xp < cooldown:
                return
            self._cooldown_cache[cache_key] = now

        if guild_id not in self.levels:
            self.levels[guild_id] = {}
        if user_id not in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {"xp": 0, "level": 0}

        multiplier = cfg.get("xp_multiplier", 1.0)
        xp_gain = int(random.randint(15, 25) * multiplier)
        self.levels[guild_id][user_id]["xp"] += xp_gain

        current_xp    = self.levels[guild_id][user_id]["xp"]
        current_level = self.levels[guild_id][user_id]["level"]
        next_level_xp = self.get_xp_for_level(current_level)

        if current_xp >= next_level_xp:
            self.levels[guild_id][user_id]["level"] += 1
            self.levels[guild_id][user_id]["xp"] = 0
            new_level = self.levels[guild_id][user_id]["level"]

            # Determine level-up channel
            lu_channel_id = cfg.get("level_up_channel")
            lu_channel = (
                message.guild.get_channel(lu_channel_id)
                if lu_channel_id
                else message.channel
            )

            try:
                custom_template = cfg.get("level_up_message")
                if custom_template:
                    lu_text = custom_template.format(
                        mention=message.author.mention,
                        level=new_level,
                        name=message.author.display_name,
                        guild=message.guild.name,
                    )
                else:
                    lu_text = msg(message, "level_up",
                                  mention=message.author.mention, level=new_level)
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(content=lu_text)
                )
                view.add_item(container)
                if lu_channel:
                    await lu_channel.send(view=view)
                log.info("Leveling", f"User {message.author} leveled up to {new_level} in {message.guild.name}")
            except discord.Forbidden:
                pass

            # Assign level roles if configured
            level_roles = cfg.get("level_roles", {})
            role_id = level_roles.get(str(new_level))
            if role_id:
                role = message.guild.get_role(int(role_id))
                if role:
                    try:
                        await message.author.add_roles(role, reason=f"Level-up reward: level {new_level}")
                    except Exception:
                        pass

        self._save_levels()

    # ─── RANK COMMAND ────────────────────────────────────────

    @commands.command(
        name="level",
        aliases=["rank"],
        help="Check your cozy level stats ☕ | Zeigt deine Level-Statistiken."
    )
    async def level(self, ctx, member: discord.Member = None):
        member   = member or ctx.author
        guild_id = str(ctx.guild.id)
        user_id  = str(member.id)

        cfg = self._guild_cfg(guild_id)
        if not cfg.get("xp_enabled", True):
            return await ctx.send(msg(ctx, "xp_disabled"))

        if guild_id not in self.levels or user_id not in self.levels[guild_id]:
            return await ctx.send(msg(ctx, "no_xp", name=member.display_name))

        user_data     = self.levels[guild_id][user_id]
        current_level = user_data["level"]
        current_xp    = user_data["xp"]
        next_level_xp = self.get_xp_for_level(current_level)

        sorted_users = sorted(
            self.levels[guild_id].items(),
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            reverse=True
        )
        rank = next((i for i, (uid, _) in enumerate(sorted_users, 1) if uid == user_id), 1)

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

    # ─── LEADERBOARD COMMAND ──────────────────────────────────

    @commands.command(
        name="level-leaderboard",
        aliases=["lvl-lb"],
        help="View the cozy leaderboard ☕ | Zeigt die Level-Bestenliste."
    )
    async def leaderboard(self, ctx):
        guild_id = str(ctx.guild.id)

        cfg = self._guild_cfg(guild_id)
        if not cfg.get("xp_enabled", True):
            return await ctx.send(msg(ctx, "xp_disabled"))

        if guild_id not in self.levels or not self.levels[guild_id]:
            return await ctx.send(msg(ctx, "leaderboard_empty"))

        sorted_users = sorted(
            self.levels[guild_id].items(),
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            reverse=True
        )

        lines = []
        for i, (user_id, data) in enumerate(sorted_users, start=1):
            user   = self.bot.get_user(int(user_id))
            name   = user.display_name if user else f"User {user_id}"
            medal  = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"**{i}.**")
            lines.append(f"{medal} {name} — Level {data['level']} ({data['xp']} XP)")

        pages = paginate(lines, per_page=10)
        view = PaginatedView(
            title=msg(ctx, "leaderboard_title", guild=ctx.guild.name),
            pages=pages,
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None,
        )
        await ctx.send(view=view)

    # ─── LEVELCONFIG COMMAND GROUP ────────────────────────────

    @commands.group(
        name="levelconfig",
        aliases=["lvlcfg"],
        invoke_without_command=True,
        help="View or configure the leveling system. | Level-Einstellungen anzeigen / bearbeiten."
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig(self, ctx):
        """Show current leveling config for this server."""
        guild_id = str(ctx.guild.id)
        cfg = self._guild_cfg(guild_id)

        lu_ch = ctx.guild.get_channel(cfg.get("level_up_channel") or 0)
        lu_ch_str = lu_ch.mention if lu_ch else "*(same channel)*"

        lr = cfg.get("level_roles", {})
        lr_lines = "\n".join(
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

    @levelconfig.command(name="toggle", help="Enable or disable XP for this server.")
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_toggle(self, ctx):
        guild_id = str(ctx.guild.id)
        cfg = self._guild_cfg(guild_id)
        cfg["xp_enabled"] = not cfg.get("xp_enabled", True)
        self._save_configs()
        state = f"{get_emoji('icon_tick')} enabled" if cfg["xp_enabled"] else f"{get_emoji('icon_cross')} disabled"
        await ctx.send(f"XP tracking is now **{state}** for this server.")

    @levelconfig.command(name="multiplier", aliases=["xpmultiplier"], help="Set XP gain multiplier (e.g. 2.0).")
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_multiplier(self, ctx, value: float = None):
        if value is None or value <= 0:
            return await ctx.send("Please provide a positive multiplier (e.g. `1.5`).")
        guild_id = str(ctx.guild.id)
        cfg = self._guild_cfg(guild_id)
        cfg["xp_multiplier"] = round(value, 2)
        self._save_configs()
        await ctx.send(msg(ctx, "cfg_updated") + f" XP multiplier → `{cfg['xp_multiplier']}x`")

    @levelconfig.command(name="cooldown", help="Set XP cooldown between gains in seconds (0 = off).")
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_cooldown(self, ctx, seconds: int = None):
        if seconds is None or seconds < 0:
            return await ctx.send("Please provide a non-negative number of seconds.")
        guild_id = str(ctx.guild.id)
        cfg = self._guild_cfg(guild_id)
        cfg["xp_cooldown"] = seconds
        self._save_configs()
        status = f"`{seconds}s`" if seconds > 0 else "off"
        await ctx.send(msg(ctx, "cfg_updated") + f" XP cooldown → {status}")

    @levelconfig.command(name="levelupchannel", aliases=["luchannel"], help="Set the level-up announcement channel.")
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_channel(self, ctx, channel: discord.TextChannel = None):
        guild_id = str(ctx.guild.id)
        cfg = self._guild_cfg(guild_id)
        cfg["level_up_channel"] = channel.id if channel else None
        self._save_configs()
        dest = channel.mention if channel else "*(same channel)*"
        await ctx.send(msg(ctx, "cfg_updated") + f" Level-up channel → {dest}")

    @levelconfig.command(name="levelrole", aliases=["role"], help="Assign a role when a level is reached. Usage: .levelconfig levelrole <level> @role")
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_levelrole(self, ctx, level: int = None, role: discord.Role = None):
        if level is None or level < 1:
            return await ctx.send("Please specify a valid level (e.g. `5`).")
        guild_id = str(ctx.guild.id)
        cfg = self._guild_cfg(guild_id)
        lr = cfg.setdefault("level_roles", {})
        if role is None:
            lr.pop(str(level), None)
            self._save_configs()
            await ctx.send(msg(ctx, "cfg_updated") + f" Removed level role for level {level}.")
        else:
            lr[str(level)] = role.id
            self._save_configs()
            await ctx.send(msg(ctx, "cfg_updated") + f" Level {level} → {role.mention}")

    @levelconfig.command(name="resetuser", help="Reset XP and level for a member.")
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_resetuser(self, ctx, member: discord.Member = None):
        if not member:
            return await ctx.send("Please specify a member.")
        guild_id = str(ctx.guild.id)
        user_id  = str(member.id)
        if guild_id in self.levels and user_id in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {"xp": 0, "level": 0}
            self._save_levels()
        await ctx.send(f"{get_emoji('icon_tick')} Reset XP and level for **{member.display_name}**.")

    # ─── LEVELING PANEL ──────────────────────────────────────

    @commands.command(
        name="levelpanel",
        aliases=["lvlpanel", "lp"],
        help="Open the interactive leveling management panel ☕ | Leveling-Dashboard öffnen."
    )
    @commands.has_permissions(manage_guild=True)
    async def levelpanel(self, ctx):
        """Open the interactive leveling management panel."""
        panel = _build_level_panel(self, ctx.guild.id, "overview", ctx.guild)
        await ctx.send(view=panel)


async def setup(bot):
    await bot.add_cog(Leveling(bot))
