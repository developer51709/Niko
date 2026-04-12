import discord
from discord.ext import commands
import time
import re
import asyncio
from utils import logging as log
from config.emojis import get_emoji

INVITE_REGEX = re.compile(r"(discord\.gg/|discord\.com/invite/)", re.IGNORECASE)

# this will be used to prevent the bot from pinging every whitelisted user on the server every single time the automod command is used 🫩
ALLOWED_MENTIONS = discord.AllowedMentions.none()

# AppInstallationType integer keys used in _integration_owners
_GUILD_INSTALL = 0
_USER_INSTALL  = 1


def _is_user_installed_app(meta) -> bool:
    """
    Return True when a MessageInteractionMetadata came from a user-installed
    application (not a guild-installed bot).

    Discord's `_integration_owners` dict uses integer keys:
      0 = guild install  →  normal server bot
      1 = user install   →  user-installed app (potential raid tool)

    A genuine user-installed-only command has key 1 present and key 0 absent.
    """
    try:
        owners = meta._integration_owners
    except AttributeError:
        return False
    return _USER_INSTALL in owners and _GUILD_INSTALL not in owners


# ──────────────────────────────────────────────────
#  SECTION TEXT BUILDERS
# ──────────────────────────────────────────────────

def _icon(enabled: bool) -> str:
    return get_emoji("icon_tick") if enabled else get_emoji("icon_cross")


def _build_overview_text(cfg: dict) -> str:
    am = cfg["automod"]
    an = cfg["antinuke"]
    ar = cfg["antiraid"]
    are = cfg["antiraid_ext"]
    wu = len(cfg.get("whitelist_users", []))
    wr = len(cfg.get("whitelist_roles", []))
    return (
        f"### {get_emoji('automod')} AutoMod Dashboard\n"
        "Here's a full snapshot of your server's protection ☕\n\n"
        "**💬 Message Filter**\n"
        f"{_icon(am.get('antispam'))} Anti-Spam  •  "
        f"{_icon(am.get('antilink'))} Anti-Link\n"
        f"{_icon(am.get('badwords'))} Bad Words  •  "
        f"{_icon(am.get('massmention'))} Mass Mention\n\n"
        "**💣 Anti-Nuke**\n"
        f"{_icon(am.get('antinuke'))} Enabled  •  "
        f"Action: `{an.get('action', 'strip')}`  •  "
        f"Interval: `{an.get('interval', 10)}s`\n\n"
        "**🌊 Anti-Raid** *(join flood)*\n"
        f"{_icon(am.get('antiraid'))} Enabled  •  "
        f"Action: `{ar.get('action', 'kick')}`\n"
        f"Threshold: `{ar.get('join_threshold', 10)}` joins / `{ar.get('join_interval', 10)}s`\n\n"
        "**🤖 Ext. App Raid**\n"
        f"{_icon(am.get('antiraid_ext'))} Interaction flood  •  "
        f"{_icon(are.get('ext_app_detection', True))} User-installed apps\n"
        f"Raider: `{are.get('raider_action', 'kick')}`  •  "
        f"Operator: `{are.get('operator_action', 'notify')}`  •  "
        f"App abuse: `{are.get('ext_app_action', 'kick')}`\n\n"
        "**🔓 Whitelist**\n"
        f"`{wu}` whitelisted user(s)  •  `{wr}` whitelisted role(s)\n\n"
        "-# Use the dropdown below to navigate and configure each section."
    )


def _build_filter_text(cfg: dict) -> str:
    am = cfg["automod"]
    return (
        "### 💬 Message Filter Settings\n"
        "Toggle each protection and adjust the thresholds below.\n\n"
        f"{_icon(am.get('antispam'))} **Anti-Spam** — mutes members who send messages too fast\n"
        f"  Threshold: `{cfg.get('spam_threshold', 6)}` msgs / `{cfg.get('spam_interval', 7)}s`\n\n"
        f"{_icon(am.get('antilink'))} **Anti-Link** — deletes Discord invite links\n\n"
        f"{_icon(am.get('badwords'))} **Bad Words** — deletes blocked words (manage with `!badwords`)\n\n"
        f"{_icon(am.get('massmention'))} **Mass Mention** — mutes members who mass-mention\n"
        f"  Max mentions: `{cfg.get('max_mentions', 5)}`"
    )


def _build_antinuke_text(cfg: dict) -> str:
    am = cfg["automod"]
    an = cfg["antinuke"]
    return (
        "### 💣 Anti-Nuke Settings\n"
        "Protects your server against rogue moderators performing mass actions.\n\n"
        f"{_icon(am.get('antinuke'))} **Anti-Nuke** — currently {'active 🟢' if am.get('antinuke') else 'inactive 🔴'}\n\n"
        "**Tracked Actions & Thresholds** *(within interval)*\n"
        f"🔨 Bans: ≥ `{an.get('ban_threshold', 3)}`\n"
        f"👟 Kicks: ≥ `{an.get('kick_threshold', 3)}`\n"
        f"🗑️ Channel Deletes: ≥ `{an.get('channel_delete_threshold', 3)}`\n"
        f"🗑️ Role Deletes: ≥ `{an.get('role_delete_threshold', 3)}`\n\n"
        f"**Interval:** `{an.get('interval', 10)}s`\n"
        f"**Action on trigger:** `{an.get('action', 'strip')}`\n"
        "-# Actions: `strip` (remove dangerous roles), `kick`, `ban`"
    )


def _build_antiraid_text(cfg: dict) -> str:
    am = cfg["automod"]
    ar = cfg["antiraid"]
    return (
        "### 🌊 Anti-Raid Settings *(Join Flood)*\n"
        "Detects and responds to mass member join events.\n\n"
        f"{_icon(am.get('antiraid'))} **Anti-Raid** — currently {'active 🟢' if am.get('antiraid') else 'inactive 🔴'}\n\n"
        f"**Join Threshold:** `{ar.get('join_threshold', 10)}` members\n"
        f"**Time Window:** `{ar.get('join_interval', 10)}` seconds\n"
        f"**Action on trigger:** `{ar.get('action', 'kick')}`\n\n"
        "-# Actions: `kick` (kick all recent joiners), `lockdown` (lock all channels)"
    )


def _build_ext_raid_text(cfg: dict) -> str:
    am = cfg["automod"]
    are = cfg["antiraid_ext"]
    return (
        "### 🤖 External App Raid Protection\n\n"

        "**Mode 1 — Interaction Flood Detection**\n"
        "Detects raids driven by external tools by tracking how many recently-joined "
        "members fire bot interactions in quick succession, then identifies the operator "
        "via invite-use diff.\n\n"
        f"{_icon(am.get('antiraid_ext'))} **Enabled**\n"
        f"Threshold: `{are.get('interaction_threshold', 5)}` unique new members / "
        f"`{are.get('interaction_window', 30)}s`\n"
        f"'New member' = joined within `{are.get('join_age_limit', 120)}s`\n"
        f"Raider action: `{are.get('raider_action', 'kick')}`  •  "
        f"Operator action: `{are.get('operator_action', 'notify')}`\n\n"

        "**Mode 2 — User-Installed App Detection**\n"
        "Detects slash commands fired by apps that are installed on a **user's account** "
        "rather than the server. This catches raid bots that never join the server and "
        "that most anti-raid tools miss. The triggering user is identified from the "
        "message's `interaction_metadata` and actioned directly.\n\n"
        f"{_icon(are.get('ext_app_detection', True))} **Enabled**\n"
        f"Threshold: `{are.get('ext_app_threshold', 3)}` commands / "
        f"`{are.get('ext_app_window', 15)}s`\n"
        f"Action: `{are.get('ext_app_action', 'kick')}`\n\n"
        "-# Raider/operator actions: `kick`, `ban`\n"
        "-# Operator-only: `notify` (log + DM owner)\n"
        "-# User-app action: `kick`, `ban`, `warn`, `log`"
    )


def _build_whitelist_text(cfg: dict, guild: discord.Guild) -> str:
    user_ids = cfg.get("whitelist_users", [])
    role_ids = cfg.get("whitelist_roles", [])

    user_lines = [
        f"• {(guild.get_member(uid) or discord.Object(uid))}"
        for uid in user_ids
    ]
    role_lines = [
        f"• {(guild.get_role(rid) or discord.Object(rid))}"
        for rid in role_ids
    ]

    return (
        "### 🔓 AutoMod Whitelist\n"
        "Whitelisted users and roles bypass all automod checks.\n\n"
        "**Whitelisted Users**\n"
        f"{chr(10).join(user_lines) or '*None*'}\n\n"
        "**Whitelisted Roles**\n"
        f"{chr(10).join(role_lines) or '*None*'}\n\n"
        "-# Use `.whitelist add user @user` or `.whitelist add role @role` to manage."
    )


def _section_text(cfg: dict, section: str, guild: discord.Guild = None) -> str:
    if section == "filter":
        return _build_filter_text(cfg)
    if section == "antinuke":
        return _build_antinuke_text(cfg)
    if section == "antiraid":
        return _build_antiraid_text(cfg)
    if section == "ext_raid":
        return _build_ext_raid_text(cfg)
    if section == "whitelist":
        return _build_whitelist_text(cfg, guild)
    return _build_overview_text(cfg)


# ──────────────────────────────────────────────────
#  INTERACTIVE COMPONENTS
# ──────────────────────────────────────────────────

class SectionSelect(discord.ui.Select):
    def __init__(self, automod_cog, guild_id: int, current_section: str):
        self._cog = automod_cog
        self._guild_id = guild_id
        options = [
            discord.SelectOption(
                label="Overview", 
                value="overview", 
                emoji=get_emoji("automod"),
                description="Full snapshot of all protections",
                default=(current_section == "overview")
            ),
            discord.SelectOption(
                label="Message Filter", 
                value="filter", 
                emoji="💬",
                description="Spam, links, bad words, mass mention",
                default=(current_section == "filter")
            ),
            discord.SelectOption(
                label="Anti-Nuke", 
                value="antinuke", 
                emoji="💣",
                description="Stop rogue mods from mass-deleting",
                default=(current_section == "antinuke")
            ),
            discord.SelectOption(
                label="Anti-Raid", 
                value="antiraid", 
                emoji="🌊",
                description="Stop mass member join attacks",
                default=(current_section == "antiraid")
            ),
            discord.SelectOption(
                label="Ext. App Raid", 
                value="ext_raid", 
                emoji="🤖",
                description="User-installed app abuse & interaction floods",
                default=(current_section == "ext_raid")
            ),
            discord.SelectOption(
                label="Whitelist", 
                value="whitelist", 
                emoji="🔓",
                description="Users and roles exempt from automod",
                default=(current_section == "whitelist")
            ),
        ]
        super().__init__(placeholder="Navigate sections...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        new_panel = _build_panel(self._cog, self._guild_id, self.values[0], interaction.guild)
        await interaction.response.edit_message(view=new_panel, allowed_mentions=ALLOWED_MENTIONS)


class ToggleButton(discord.ui.Button):
    def __init__(self, label: str, key: str, automod_cog, guild_id: int, section: str):
        self._cog = automod_cog
        self._guild_id = guild_id
        self._key = key
        self._section = section
        cfg = automod_cog.utils().get_guild_config(guild_id)
        enabled = cfg["automod"].get(key, False)
        super().__init__(
            label=f"{label}",
            style=discord.ButtonStyle.green if enabled else discord.ButtonStyle.red,
            emoji=_icon(enabled)
        )

    async def callback(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        cfg["automod"][self._key] = not cfg["automod"].get(self._key, False)
        utils.save_config()
        new_panel = _build_panel(self._cog, self._guild_id, self._section, interaction.guild)
        await interaction.response.edit_message(view=new_panel, allowed_mentions=ALLOWED_MENTIONS)


class SubToggleButton(discord.ui.Button):
    """Toggles a boolean inside a sub-config dict (e.g. antiraid_ext.ext_app_detection)."""
    def __init__(self, label: str, sub_cfg_key: str, field: str, automod_cog, guild_id: int, section: str):
        self._cog = automod_cog
        self._guild_id = guild_id
        self._sub_cfg = sub_cfg_key
        self._field = field
        self._section = section
        cfg = automod_cog.utils().get_guild_config(guild_id)
        enabled = cfg.get(sub_cfg_key, {}).get(field, True)
        super().__init__(
            label=f"{label}",
            style=discord.ButtonStyle.green if enabled else discord.ButtonStyle.red,
            emoji=_icon(enabled)
        )

    async def callback(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        cfg[self._sub_cfg][self._field] = not cfg[self._sub_cfg].get(self._field, True)
        utils.save_config()
        new_panel = _build_panel(self._cog, self._guild_id, self._section, interaction.guild)
        await interaction.response.edit_message(view=new_panel, allowed_mentions=ALLOWED_MENTIONS)


class EditThresholdsButton(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int, section: str, label: str = "Edit Thresholds"):
        self._cog = automod_cog
        self._guild_id = guild_id
        self._section = section
        super().__init__(label=label, style=discord.ButtonStyle.blurple, emoji=get_emoji("icon_settings"))

    async def callback(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        modal = _build_threshold_modal(cfg, self._cog, self._guild_id, self._section)
        await interaction.response.send_modal(modal)


class EditExtAppButton(discord.ui.Button):
    """Opens the modal for user-installed app detection settings."""
    def __init__(self, automod_cog, guild_id: int):
        self._cog = automod_cog
        self._guild_id = guild_id
        super().__init__(
            label="Edit App Detection", 
            style=discord.ButtonStyle.blurple,
            emoji=get_emoji("icon_settings")
        )

    async def callback(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        await interaction.response.send_modal(ExtAppThresholdModal(self._cog, self._guild_id, cfg))


# ──────────────────────────────────────────────────
#  THRESHOLD MODALS
# ──────────────────────────────────────────────────

class FilterThresholdModal(discord.ui.Modal, title="Message Filter Thresholds"):
    spam_msgs = discord.ui.TextInput(label="Spam: max messages", placeholder="e.g. 6")
    spam_secs = discord.ui.TextInput(label="Spam: within seconds", placeholder="e.g. 7")
    max_ment = discord.ui.TextInput(label="Mass Mention: max mentions", placeholder="e.g. 5")

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        self.spam_msgs.default = str(cfg.get("spam_threshold", 6))
        self.spam_secs.default = str(cfg.get("spam_interval", 7))
        self.max_ment.default = str(cfg.get("max_mentions", 5))

    async def on_submit(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["spam_threshold"] = max(1, int(self.spam_msgs.value))
            cfg["spam_interval"] = max(1, int(self.spam_secs.value))
            cfg["max_mentions"] = max(1, int(self.max_ment.value))
            utils.save_config()
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "filter", interaction.guild))
        except ValueError:
            await interaction.response.send_message("Please enter valid whole numbers.", ephemeral=True)


class AntiNukeThresholdModal(discord.ui.Modal, title="Anti-Nuke Thresholds"):
    ban_t = discord.ui.TextInput(label="Ban threshold", placeholder="e.g. 3")
    kick_t = discord.ui.TextInput(label="Kick threshold", placeholder="e.g. 3")
    chan_t = discord.ui.TextInput(label="Channel delete threshold", placeholder="e.g. 3")
    role_t = discord.ui.TextInput(label="Role delete threshold", placeholder="e.g. 3")
    interval = discord.ui.TextInput(label="Interval (seconds)", placeholder="e.g. 10")

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        an = cfg.get("antinuke", {})
        self.ban_t.default = str(an.get("ban_threshold", 3))
        self.kick_t.default = str(an.get("kick_threshold", 3))
        self.chan_t.default = str(an.get("channel_delete_threshold", 3))
        self.role_t.default = str(an.get("role_delete_threshold", 3))
        self.interval.default = str(an.get("interval", 10))

    async def on_submit(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antinuke"]["ban_threshold"] = max(1, int(self.ban_t.value))
            cfg["antinuke"]["kick_threshold"] = max(1, int(self.kick_t.value))
            cfg["antinuke"]["channel_delete_threshold"] = max(1, int(self.chan_t.value))
            cfg["antinuke"]["role_delete_threshold"] = max(1, int(self.role_t.value))
            cfg["antinuke"]["interval"] = max(1, int(self.interval.value))
            utils.save_config()
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "antinuke", interaction.guild))
        except ValueError:
            await interaction.response.send_message("Please enter valid whole numbers.", ephemeral=True)


class AntiNukeActionModal(discord.ui.Modal, title="Anti-Nuke Response Action"):
    action = discord.ui.TextInput(label="Action (strip / kick / ban)", placeholder="strip", max_length=10)

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        self.action.default = cfg.get("antinuke", {}).get("action", "strip")

    async def on_submit(self, interaction: discord.Interaction):
        val = self.action.value.lower().strip()
        if val not in ("strip", "kick", "ban"):
            return await interaction.response.send_message(
                "Invalid action. Choose: `strip`, `kick`, or `ban`.", ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        cfg["antinuke"]["action"] = val
        utils.save_config()
        await interaction.response.edit_message(
            view=_build_panel(self._cog, self._guild_id, "antinuke", interaction.guild))


class AntiRaidThresholdModal(discord.ui.Modal, title="Anti-Raid Settings"):
    join_t = discord.ui.TextInput(label="Join threshold (members)", placeholder="e.g. 10")
    join_i = discord.ui.TextInput(label="Time window (seconds)", placeholder="e.g. 10")
    action = discord.ui.TextInput(label="Action (kick / lockdown)", placeholder="kick", max_length=10)

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        ar = cfg.get("antiraid", {})
        self.join_t.default = str(ar.get("join_threshold", 10))
        self.join_i.default = str(ar.get("join_interval", 10))
        self.action.default = ar.get("action", "kick")

    async def on_submit(self, interaction: discord.Interaction):
        val = self.action.value.lower().strip()
        if val not in ("kick", "lockdown"):
            return await interaction.response.send_message(
                "Invalid action. Choose: `kick` or `lockdown`.", ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antiraid"]["join_threshold"] = max(1, int(self.join_t.value))
            cfg["antiraid"]["join_interval"] = max(1, int(self.join_i.value))
            cfg["antiraid"]["action"] = val
            utils.save_config()
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "antiraid", interaction.guild))
        except ValueError:
            await interaction.response.send_message("Please enter valid whole numbers.", ephemeral=True)


class ExtRaidThresholdModal(discord.ui.Modal, title="Ext. Raid — Interaction Flood Settings"):
    int_threshold = discord.ui.TextInput(label="Interaction threshold (unique users)", placeholder="e.g. 5")
    int_window = discord.ui.TextInput(label="Detection window (seconds)", placeholder="e.g. 30")
    join_age = discord.ui.TextInput(label="Max member age to count (seconds)", placeholder="e.g. 120")
    raider_act = discord.ui.TextInput(label="Raider action (kick / ban)", placeholder="kick", max_length=10)
    operator_act = discord.ui.TextInput(label="Operator action (notify / kick / ban)", placeholder="notify", max_length=10)

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        are = cfg.get("antiraid_ext", {})
        self.int_threshold.default = str(are.get("interaction_threshold", 5))
        self.int_window.default = str(are.get("interaction_window", 30))
        self.join_age.default = str(are.get("join_age_limit", 120))
        self.raider_act.default = are.get("raider_action", "kick")
        self.operator_act.default = are.get("operator_action", "notify")

    async def on_submit(self, interaction: discord.Interaction):
        raider_val = self.raider_act.value.lower().strip()
        operator_val = self.operator_act.value.lower().strip()
        if raider_val not in ("kick", "ban"):
            return await interaction.response.send_message(
                "Invalid raider action. Choose: `kick` or `ban`.", ephemeral=True)
        if operator_val not in ("notify", "kick", "ban"):
            return await interaction.response.send_message(
                "Invalid operator action. Choose: `notify`, `kick`, or `ban`.", ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antiraid_ext"]["interaction_threshold"] = max(1, int(self.int_threshold.value))
            cfg["antiraid_ext"]["interaction_window"] = max(5, int(self.int_window.value))
            cfg["antiraid_ext"]["join_age_limit"] = max(10, int(self.join_age.value))
            cfg["antiraid_ext"]["raider_action"] = raider_val
            cfg["antiraid_ext"]["operator_action"] = operator_val
            utils.save_config()
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "ext_raid", interaction.guild))
        except ValueError:
            await interaction.response.send_message("Please enter valid whole numbers.", ephemeral=True)


class ExtAppThresholdModal(discord.ui.Modal, title="Ext. Raid — User-Installed App Settings"):
    threshold = discord.ui.TextInput(label="Commands per user before action", placeholder="e.g. 3")
    window = discord.ui.TextInput(label="Time window (seconds)", placeholder="e.g. 15")
    action = discord.ui.TextInput(label="Action (kick / ban / warn / log)", placeholder="kick", max_length=10)

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        are = cfg.get("antiraid_ext", {})
        self.threshold.default = str(are.get("ext_app_threshold", 3))
        self.window.default = str(are.get("ext_app_window", 15))
        self.action.default = are.get("ext_app_action", "kick")

    async def on_submit(self, interaction: discord.Interaction):
        val = self.action.value.lower().strip()
        if val not in ("kick", "ban", "warn", "log"):
            return await interaction.response.send_message(
                "Invalid action. Choose: `kick`, `ban`, `warn`, or `log`.", ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antiraid_ext"]["ext_app_threshold"] = max(1, int(self.threshold.value))
            cfg["antiraid_ext"]["ext_app_window"] = max(5, int(self.window.value))
            cfg["antiraid_ext"]["ext_app_action"] = val
            utils.save_config()
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "ext_raid", interaction.guild))
        except ValueError:
            await interaction.response.send_message("Please enter valid whole numbers.", ephemeral=True)


def _build_threshold_modal(cfg, automod_cog, guild_id, section):
    if section == "antinuke":
        return AntiNukeThresholdModal(automod_cog, guild_id, cfg)
    if section == "antiraid":
        return AntiRaidThresholdModal(automod_cog, guild_id, cfg)
    if section == "ext_raid":
        return ExtRaidThresholdModal(automod_cog, guild_id, cfg)
    return FilterThresholdModal(automod_cog, guild_id, cfg)


# ──────────────────────────────────────────────────
#  WHITELIST EPHEMERAL SELECTS & VIEWS
# ──────────────────────────────────────────────────
class _WLUserSelect(discord.ui.UserSelect):
    """Ephemeral select — add members to whitelist."""
    def __init__(self, automod_cog, guild_id: int):
        super().__init__(
            placeholder="Choose member(s) to whitelist…",
            min_values=1, max_values=10,
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        for user in self.values:
            utils.add_whitelist_user(self._guild_id, user.id)
        utils.save_config()
        names = " ".join(u.mention for u in self.values)
        await interaction.response.edit_message(
            content=f"{get_emoji('icon_tick')} Added {names} to the automod whitelist.", view=None,
        )


class _WLRoleSelect(discord.ui.RoleSelect):
    """Ephemeral select — add roles to whitelist."""
    def __init__(self, automod_cog, guild_id: int):
        super().__init__(
            placeholder="Choose role(s) to whitelist…",
            min_values=1, max_values=10,
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        for role in self.values:
            utils.add_whitelist_role(self._guild_id, role.id)
        utils.save_config()
        names = " ".join(r.mention for r in self.values)
        await interaction.response.edit_message(
            content=f"{get_emoji('icon_tick')} Added {names} to the automod whitelist.", view=None,
        )


class _WLUserRemoveSelect(discord.ui.Select):
    """Ephemeral select — remove users from whitelist."""
    def __init__(self, automod_cog, guild_id: int, options: list):
        super().__init__(
            placeholder="Choose member(s) to remove…",
            min_values=1, max_values=len(options),
            options=options,
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        for uid_str in self.values:
            utils.remove_whitelist_user(self._guild_id, int(uid_str))
        utils.save_config()
        await interaction.response.edit_message(
            content=f"{get_emoji('icon_tick')} Removed `{len(self.values)}` user(s) from the whitelist.", view=None,
        )


class _WLRoleRemoveSelect(discord.ui.Select):
    """Ephemeral select — remove roles from whitelist."""
    def __init__(self, automod_cog, guild_id: int, options: list):
        super().__init__(
            placeholder="Choose role(s) to remove…",
            min_values=1, max_values=len(options),
            options=options,
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        for rid_str in self.values:
            utils.remove_whitelist_role(self._guild_id, int(rid_str))
        utils.save_config()
        await interaction.response.edit_message(
            content=f"{get_emoji('icon_tick')} Removed `{len(self.values)}` role(s) from the whitelist.", view=None,
        )


class _WLAddUserBtn(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int):
        super().__init__(
            label="Add User", 
            style=discord.ButtonStyle.green,
            emoji=get_emoji("icon_plus")
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        view = discord.ui.View(timeout=60)
        view.add_item(_WLUserSelect(self._cog, self._guild_id))
        await interaction.response.send_message(
            "Select the members you want to exempt from automod:",
            view=view, ephemeral=True,
        )


class _WLAddRoleBtn(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int):
        super().__init__(
            label="Add Role", 
            style=discord.ButtonStyle.green,
            emoji=get_emoji("icon_plus")
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        view = discord.ui.View(timeout=60)
        view.add_item(_WLRoleSelect(self._cog, self._guild_id))
        await interaction.response.send_message(
            "Select the roles you want to exempt from automod:",
            view=view, ephemeral=True,
        )


class _WLRemoveUserBtn(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int, has_users: bool):
        super().__init__(
            label="➖ Remove User",
            style=discord.ButtonStyle.red,
            disabled=not has_users,
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        user_ids = cfg.get("whitelist_users", [])
        options = []
        for uid in user_ids:
            member = interaction.guild.get_member(uid)
            label = member.display_name if member else f"User {uid}"
            options.append(discord.SelectOption(
                label=label[:100], value=str(uid),
                description=f"ID: {uid}",
            ))
        if not options:
            return await interaction.response.send_message(
                "No users are currently whitelisted.", ephemeral=True,
            )
        view = discord.ui.View(timeout=60)
        view.add_item(_WLUserRemoveSelect(self._cog, self._guild_id, options))
        await interaction.response.send_message(
            "Select the members to remove from the whitelist:",
            view=view, ephemeral=True,
        )


class _WLRemoveRoleBtn(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int, has_roles: bool):
        super().__init__(
            label="➖ Remove Role",
            style=discord.ButtonStyle.red,
            disabled=not has_roles,
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        role_ids = cfg.get("whitelist_roles", [])
        options = []
        for rid in role_ids:
            role = interaction.guild.get_role(rid)
            label = role.name if role else f"Role {rid}"
            options.append(discord.SelectOption(
                label=label[:100], value=str(rid),
                description=f"ID: {rid}",
            ))
        if not options:
            return await interaction.response.send_message(
                "No roles are currently whitelisted.", ephemeral=True,
            )
        view = discord.ui.View(timeout=60)
        view.add_item(_WLRoleRemoveSelect(self._cog, self._guild_id, options))
        await interaction.response.send_message(
            "Select the roles to remove from the whitelist:",
            view=view, ephemeral=True,
        )


# ──────────────────────────────────────────────────
#  PANEL BUILDER
# ──────────────────────────────────────────────────

def _build_panel(self, guild_id: int, section: str = "overview", guild: discord.Guild = None) -> discord.ui.LayoutView:
    utils = self.utils()
    cfg = utils.get_guild_config(guild_id)

    view = discord.ui.LayoutView(timeout=300)
    text = _section_text(cfg, section, guild)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=text),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
    )
    container.add_item(discord.ui.ActionRow(SectionSelect(self, guild_id, section)))

    if section == "filter":
        container.add_item(discord.ui.ActionRow(
            ToggleButton("Anti-Spam", "antispam", self, guild_id, section),
            ToggleButton("Anti-Link", "antilink", self, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            ToggleButton("Bad Words", "badwords", self, guild_id, section),
            ToggleButton("Mass Mention", "massmention", self, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(self, guild_id, section),
        ))

    elif section == "antinuke":
        container.add_item(discord.ui.ActionRow(
            ToggleButton("Anti-Nuke", "antinuke", self, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(self, guild_id, section),
            _NukeActionButton(self, guild_id),
        ))

    elif section == "antiraid":
        container.add_item(discord.ui.ActionRow(
            ToggleButton("Anti-Raid", "antiraid", self, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(self, guild_id, section),
        ))

    elif section == "ext_raid":
        container.add_item(discord.ui.ActionRow(
            ToggleButton("Interaction Flood", "antiraid_ext", self, guild_id, section),
            SubToggleButton("User-App Detection", "antiraid_ext", "ext_app_detection", self, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(self, guild_id, section, label="Flood Thresholds"),
            EditExtAppButton(self, guild_id),
        ))

    elif section == "whitelist":
        wl_cfg = cfg
        has_u = bool(wl_cfg.get("whitelist_users", []))
        has_r = bool(wl_cfg.get("whitelist_roles", []))
        container.add_item(discord.ui.ActionRow(
            _WLAddUserBtn(self, guild_id),
            _WLAddRoleBtn(self, guild_id),
        ))
        container.add_item(discord.ui.ActionRow(
            _WLRemoveUserBtn(self, guild_id, has_u),
            _WLRemoveRoleBtn(self, guild_id, has_r),
        ))

    view.add_item(container)
    return view


class _NukeActionButton(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int):
        super().__init__(label="🎯 Set Action", style=discord.ButtonStyle.gray)
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        await interaction.response.send_modal(AntiNukeActionModal(self._cog, self._guild_id, cfg))


# ──────────────────────────────────────────────────
#  AUTOMOD COG
# ──────────────────────────────────────────────────

class AutoMod(commands.Cog):
    """Automatic moderation: spam, links, badwords, mass mention,
    anti-nuke, anti-raid, interaction-flood, and user-installed app abuse."""

    def __init__(self, bot):
        self.bot = bot
        self._msg_history = {}  # guild_id -> user_id -> [timestamps]
        self._nuke_history = {}  # guild_id -> user_id -> {action_key: [ts]}
        self._join_history = {}  # guild_id -> [timestamps]
        self._interaction_history = {}  # guild_id -> [(user_id, timestamp)]
        self._ext_app_history = {}  # guild_id -> user_id -> [timestamps]
        self._invite_cache = {}  # guild_id -> {invite_code: uses}
        self._missing_perms_warned = set()  # guild_ids where we've already logged a missing-perm warning

    def utils(self):
        return self.bot.get_cog("ModerationUtils")

    def get_cfg(self, guild_id: int):
        return self.utils().get_guild_config(guild_id)

    # ─── INVITE CACHE ─────────────────────────────

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self._snapshot_invites(guild)

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        if invite.guild:
            await self._snapshot_invites(invite.guild)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        if invite.guild:
            await self._snapshot_invites(invite.guild)

    async def _snapshot_invites(self, guild: discord.Guild):
        try:
            invites = await guild.invites()
            self._invite_cache[guild.id] = {inv.code: inv.uses for inv in invites}
        except (discord.Forbidden, discord.HTTPException):
            pass

    async def _identify_operator(self, guild: discord.Guild):
        cached = self._invite_cache.get(guild.id, {})
        try:
            current_invites = await guild.invites()
        except (discord.Forbidden, discord.HTTPException):
            return None
        best_invite = None
        best_delta = 0
        for inv in current_invites:
            delta = inv.uses - cached.get(inv.code, 0)
            if delta > best_delta:
                best_delta = delta
                best_invite = inv
        self._invite_cache[guild.id] = {inv.code: inv.uses for inv in current_invites}
        if best_invite and best_delta >= 2 and best_invite.inviter:
            return guild.get_member(best_invite.inviter.id)
        return None

    # ─── MESSAGE TRACKING ─────────────────────────

    def _track_message(self, message: discord.Message) -> int:
        gid, uid = message.guild.id, message.author.id
        now = time.time()
        cfg = self.get_cfg(gid)
        interval = cfg.get("spam_interval", 7)
        cutoff = now - interval
        bucket = self._msg_history.setdefault(gid, {}).setdefault(uid, [])
        bucket.append(now)
        self._msg_history[gid][uid] = [t for t in bucket if t >= cutoff]
        return len(self._msg_history[gid][uid])

    # ─── MESSAGE FILTER + USER-APP DETECTION ──────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return
        if not message.guild:
            return

        utils = self.utils()
        cfg = self.get_cfg(message.guild.id)

        if utils.is_whitelisted(message.guild.id, message.author):
            return

        # ── User-installed app abuse detection ────
        # Must run before content filters because the message author here is the
        # external app (a webhook/system user), not the human attacker.
        if (cfg["automod"].get("antiraid_ext", False)
                and cfg["antiraid_ext"].get("ext_app_detection", True)):
            await self._check_user_installed_app(message, cfg, utils)

        content = message.content or ""

        if cfg["automod"].get("antispam", True):
            count = self._track_message(message)
            if count >= cfg.get("spam_threshold", 6):
                try:
                    await message.delete()
                except Exception:
                    pass
                await utils.log_action(
                    message.guild, "Anti-Spam",
                    f"{message.author.mention} triggered anti-spam in {message.channel.mention}.")
                try:
                    user = message.guild.get_member(message.author.id)
                    await utils.mute_member(message.guild, user, duration=60, reason="Auto-mute: spam")
                except discord.Forbidden:
                    if message.guild.id not in self._missing_perms_warned:
                        self._missing_perms_warned.add(message.guild.id)
                        log.warning("Anti-Spam",
                                    f"Missing permissions to mute in {message.guild.name} — mute skipped silently.")
                except discord.HTTPException:
                    pass
                return

        if cfg["automod"].get("antilink", True):
            if INVITE_REGEX.search(content):
                try:
                    await message.delete()
                except Exception:
                    pass
                await utils.log_action(
                    message.guild, "Anti-Link",
                    f"{message.author.mention} posted an invite link in {message.channel.mention}.\n\n"
                    f"**Message:**\n{content}")
                return

        if cfg["automod"].get("badwords", True):
            if utils.contains_blocked_word(message.guild.id, content):
                try:
                    await message.delete()
                except Exception:
                    pass
                await utils.log_action(
                    message.guild, "Bad Word Filter",
                    f"{message.author.mention} used a blocked word in {message.channel.mention}.\n\n"
                    f"**Message:**\n{content}")
                return

        if cfg["automod"].get("massmention", True):
            mentions = len(message.mentions) + int(message.mention_everyone)
            if mentions >= cfg.get("max_mentions", 5):
                try:
                    await message.delete()
                except Exception:
                    pass
                await utils.log_action(
                    message.guild, "Mass Mention",
                    f"{message.author.mention} mass-mentioned `{mentions}` users in {message.channel.mention}.")
                try:
                    await utils.mute_member(message.guild, message.author, duration=120, reason="Auto-mute: mass mention")
                except discord.Forbidden:
                    if message.guild.id not in self._missing_perms_warned:
                        self._missing_perms_warned.add(message.guild.id)
                        log.warning("AutoMod",
                                    f"Missing permissions to mute in {message.guild.name} — mute skipped silently.")
                except discord.HTTPException:
                    pass
                return

    # ─── USER-INSTALLED APP ABUSE ─────────────────

    async def _check_user_installed_app(self, message: discord.Message, cfg: dict, utils):
        """
        Detect messages created by user-installed applications (external apps)
        triggered via slash commands.

        Detection criteria:
        1. message.application_id is set and != our bot's application_id
        2. message.interaction_metadata exists (discord.py MessageInteractionMetadata)
        3. _is_user_installed_app() returns True (key 1 in _integration_owners, key 0 absent)
        4. triggering user = interaction_metadata.user
        """

        # Must be an application-generated message that isn't our own bot
        if not message.application_id:
            return
        if message.application_id == self.bot.application_id:
            return

        # Requires interaction metadata (only present on app-command responses)
        meta = getattr(message, "interaction_metadata", None)
        if meta is None:
            return

        # Only flag user-installed apps (integration_owners key 1 present, key 0 absent)
        if not _is_user_installed_app(meta):
            return

        # The user who triggered the app
        triggering_user = getattr(meta, "user", None)
        if not triggering_user:
            return

        # Skip whitelisted users
        if utils.is_whitelisted(message.guild.id, triggering_user):
            return

        # Config
        are = cfg.get("antiraid_ext", {})
        threshold = are.get("ext_app_threshold", 3)
        window = are.get("ext_app_window", 15)
        action = are.get("ext_app_action", "kick")

        now = time.time()
        bucket = self._ext_app_history \
            .setdefault(message.guild.id, {}) \
            .setdefault(triggering_user.id, [])

        bucket.append(now)

        # Keep only timestamps within the window
        self._ext_app_history[message.guild.id][triggering_user.id] = [
            t for t in bucket if now - t <= window
        ]
        count = len(self._ext_app_history[message.guild.id][triggering_user.id])

        # Log first detection
        if count == 1:
            log.warning(
                "Ext-App",
                f"{triggering_user} used a user-installed app (ID {message.application_id}) "
                f"in {message.guild.name}."
            )
            await utils.log_action(
                message.guild,
                "🤖 User-Installed App Detected",
                f"{triggering_user.mention} used a **user-installed** external application "
                f"command in {message.channel.mention}.\n"
                f"App ID: `{message.application_id}`\n"
                f"-# Count: {count}/{threshold} before action is taken."
            )

        # Threshold reached → take action
        if count >= threshold:
            self._ext_app_history[message.guild.id][triggering_user.id] = []
            member = message.guild.get_member(triggering_user.id)

            log.warning(
                "Ext-App",
                f"Threshold reached for {triggering_user} in {message.guild.name} — "
                f"action: {action}"
            )
            await utils.log_action(
                message.guild,
                "🚫 User-Installed App Action Taken",
                f"**{triggering_user.mention}** fired `{count}` user-installed app commands "
                f"within `{window}s`.\n"
                f"App ID: `{message.application_id}`\n"
                f"Action taken: `{action}`"
            )

            if member:
                try:
                    if action == "ban":
                        await message.guild.ban(
                            member,
                            reason="AutoMod: user-installed app raid abuse"
                        )
                    elif action == "kick":
                        await member.kick(reason="AutoMod: user-installed app raid abuse")
                    elif action == "warn":
                        utils.add_warn(
                            message.guild.id, member.id, self.bot.user.id,
                            "AutoMod: user-installed app raid abuse"
                        )
                except Exception as e:
                    log.error("Ext-App", f"Failed to action {triggering_user}: {e}")

    # ─── INTERACTION FLOOD DETECTION ──────────────

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """
        Track interactions from recently-joined members.
        When multiple new members fire interactions simultaneously, it indicates
        an external automation tool is coordinating them.
        """
        if not interaction.guild:
            return

        guild = interaction.guild
        member = interaction.user

        cfg = self.get_cfg(guild.id)
        if not cfg["automod"].get("antiraid_ext", False):
            return

        if member.bot:
            return
        if self.utils().is_whitelisted(guild.id, member):
            return

        are = cfg.get("antiraid_ext", {})
        join_age_limit = are.get("join_age_limit", 120)

        joined_at = getattr(member, "joined_at", None)
        if not joined_at:
            return
        now = time.time()
        if now - joined_at.timestamp() > join_age_limit:
            return

        bucket = self._interaction_history.setdefault(guild.id, [])
        bucket.append((member.id, now))

        window = are.get("interaction_window", 30)
        self._interaction_history[guild.id] = [
            (uid, t) for uid, t in bucket if now - t <= window
        ]

        unique_users = len({uid for uid, _ in self._interaction_history[guild.id]})
        threshold = are.get("interaction_threshold", 5)

        if unique_users >= threshold:
            raider_ids = list({uid for uid, _ in self._interaction_history[guild.id]})
            self._interaction_history[guild.id] = []
            log.warning(
                "Ext-Raid",
                f"Interaction flood in {guild.name}: {unique_users} new members "
                f"in {window}s."
            )
            await self._handle_ext_raid(guild, cfg, raider_ids)

    async def _handle_ext_raid(self, guild: discord.Guild, cfg: dict, raider_ids: list):
        are = cfg.get("antiraid_ext", {})
        raider_action = are.get("raider_action", "kick")
        op_action = are.get("operator_action", "notify")

        operator = await self._identify_operator(guild)

        op_mention = operator.mention if operator else "*could not be determined*"
        raider_mentions = ", ".join(f"<@{uid}>" for uid in raider_ids)
        await self.utils().log_action(
            guild,
            "🤖 Interaction Flood Raid Detected",
            f"**{len(raider_ids)}** recently-joined members fired bot interactions "
            f"simultaneously — consistent with an external raid tool.\n\n"
            f"**Suspected Operator:** {op_mention}\n"
            f"**Raiding Accounts:** {raider_mentions}\n\n"
            f"Raider action: `{raider_action}`  •  Operator action: `{op_action}`"
        )

        for uid in raider_ids:
            member = guild.get_member(uid)
            if not member:
                continue
            try:
                if raider_action == "ban":
                    await guild.ban(member, reason="Ext. App Raid: interaction flood")
                else:
                    await member.kick(reason="Ext. App Raid: interaction flood")
                await asyncio.sleep(0.4)
            except Exception:
                pass

        if operator:
            try:
                if op_action == "ban":
                    await guild.ban(operator, reason="Ext. App Raid: suspected operator")
                elif op_action == "kick":
                    await operator.kick(reason="Ext. App Raid: suspected operator")
            except Exception:
                pass

        try:
            await guild.owner.send(
                f"{get_emoji('icon_danger')} **Interaction Flood Raid** detected in **{guild.name}**!\n"
                f"`{len(raider_ids)}` newly-joined members fired bot interactions at once.\n"
                f"Suspected operator: {operator or 'unknown'}\n"
                f"Raider action: `{raider_action}`  •  Operator action: `{op_action}`"
            )
        except Exception:
            pass

    # ─── ANTI-RAID (JOIN FLOOD) ───────────────────

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        await self._snapshot_invites(guild)

        cfg = self.get_cfg(guild.id)
        if not cfg["automod"].get("antiraid", False):
            return

        ar = cfg.get("antiraid", {})
        threshold = ar.get("join_threshold", 10)
        interval = ar.get("join_interval", 10)
        action = ar.get("action", "kick")

        now = time.time()
        cutoff = now - interval
        bucket = self._join_history.setdefault(guild.id, [])
        bucket.append(now)
        self._join_history[guild.id] = [t for t in bucket if t >= cutoff]

        if len(self._join_history[guild.id]) >= threshold:
            self._join_history[guild.id] = []
            log.warning("Anti-Raid", f"Join flood in {guild.name} — action: {action}")
            await self.utils().log_action(
                guild, "🌊 Anti-Raid Triggered",
                f"**{len(bucket)}** members joined within `{interval}s`. Executing `{action}`.")

            if action == "kick":
                for m in list(guild.members):
                    joined = m.joined_at
                    if joined and (now - joined.timestamp()) <= interval + 2:
                        try:
                            await m.kick(reason="Anti-Raid: mass join")
                            await asyncio.sleep(0.5)
                        except Exception:
                            pass
            elif action == "lockdown":
                for channel in guild.text_channels:
                    try:
                        overwrite = channel.overwrites_for(guild.default_role)
                        overwrite.send_messages = False
                        await channel.set_permissions(
                            guild.default_role, overwrite=overwrite,
                            reason="Anti-Raid lockdown")
                    except Exception:
                        pass
            try:
                await guild.owner.send(
                    f"{get_emoji('icon_danger')} **Anti-Raid** in **{guild.name}**!\n"
                    f"{len(bucket)} joins in {interval}s. Action: `{action}`.")
            except Exception:
                pass

    # ─── ANTI-NUKE ────────────────────────────────

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        guild = entry.guild
        if not guild:
            return

        cfg = self.get_cfg(guild.id)
        if not cfg["automod"].get("antinuke", False):
            return
        if entry.user == self.bot.user or guild.owner:
            return

        an = cfg.get("antinuke", {})
        interval = an.get("interval", 10)

        action_map = {
            discord.AuditLogAction.ban: ("ban", an.get("ban_threshold", 3)),
            discord.AuditLogAction.kick: ("kick", an.get("kick_threshold", 3)),
            discord.AuditLogAction.channel_delete: ("channel_delete", an.get("channel_delete_threshold", 3)),
            discord.AuditLogAction.role_delete: ("role_delete", an.get("role_delete_threshold", 3)),
        }
        if entry.action not in action_map:
            return

        action_key, threshold = action_map[entry.action]
        now = time.time()
        cutoff = now - interval
        uid = entry.user.id

        user_history = self._nuke_history.setdefault(guild.id, {}).setdefault(uid, {})
        bucket       = user_history.setdefault(action_key, [])
        bucket.append(now)
        user_history[action_key] = [t for t in bucket if t >= cutoff]

        if len(user_history[action_key]) >= threshold:
            user_history[action_key] = []
            offender    = entry.user
            nuke_action = an.get("action", "strip")

            log.warning("Anti-Nuke",
                        f"Nuke by {offender} in {guild.name} — action: {nuke_action}")
            await self.utils().log_action(
                guild, "💣 Anti-Nuke Triggered",
                f"**{offender.mention}** performed `{threshold}` `{action_key}` actions "
                f"within `{interval}s`. Action: `{nuke_action}`.")

            member = guild.get_member(uid)
            if member:
                if nuke_action == "strip":
                    await self._strip_dangerous_roles(member)
                elif nuke_action == "kick":
                    try:
                        await member.kick(reason="Anti-Nuke: suspicious mass action")
                    except Exception:
                        pass
                elif nuke_action == "ban":
                    try:
                        await guild.ban(member, reason="Anti-Nuke: suspicious mass action")
                    except Exception:
                        pass
            try:
                await guild.owner.send(
                    f"{get_emoji('icon_danger')} **Anti-Nuke** in **{guild.name}**!\n"
                    f"{offender} did `{threshold}` `{action_key}` in `{interval}s`.\n"
                    f"Action: `{nuke_action}`.")
            except Exception:
                pass

    async def _strip_dangerous_roles(self, member: discord.Member):
        dangerous = (
            discord.Permissions.administrator,
            discord.Permissions.ban_members,
            discord.Permissions.kick_members,
            discord.Permissions.manage_guild,
            discord.Permissions.manage_channels,
            discord.Permissions.manage_roles,
        )
        roles_to_remove = []
        for role in member.roles:
            if role.managed or role == member.guild.default_role:
                continue
            for perm in dangerous:
                if role.permissions >= perm:
                    roles_to_remove.append(role)
                    break
        if roles_to_remove:
            try:
                await member.remove_roles(
                    *roles_to_remove, reason="Anti-Nuke: dangerous roles stripped")
            except Exception:
                pass

    # ─── SETTINGS COMMAND ─────────────────────────

    @commands.command(name="automod",
                      help="Open the AutoMod settings panel ☕🛡️ | AutoMod-Einstellungen")
    @commands.has_permissions(manage_guild=True)
    async def automod_settings(self, ctx):
        panel = _build_panel(self, ctx.guild.id, "overview", ctx.guild)
        await ctx.send(view=panel, allowed_mentions=ALLOWED_MENTIONS)


async def setup(bot):
    await bot.add_cog(AutoMod(bot))
