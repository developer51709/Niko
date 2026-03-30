import discord
from discord.ext import commands
import time
import re
import asyncio
from utils import logging as log

INVITE_REGEX = re.compile(r"(discord\.gg/|discord\.com/invite/)", re.IGNORECASE)

# ─────────────────────────────────────────────────────────────
#  SECTION TEXT BUILDERS
# ─────────────────────────────────────────────────────────────

def _icon(enabled: bool) -> str:
    return "✅" if enabled else "❌"


def _build_overview_text(cfg: dict) -> str:
    am  = cfg["automod"]
    an  = cfg["antinuke"]
    ar  = cfg["antiraid"]
    are = cfg["antiraid_ext"]
    wu  = len(cfg.get("whitelist_users", []))
    wr  = len(cfg.get("whitelist_roles", []))
    return (
        "### 🛡️ AutoMod Dashboard\n"
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
        "**🤖 Ext. App Raid** *(interaction flood)*\n"
        f"{_icon(am.get('antiraid_ext'))} Enabled  •  "
        f"Raider action: `{are.get('raider_action', 'kick')}`  •  "
        f"Operator action: `{are.get('operator_action', 'notify')}`\n"
        f"Threshold: `{are.get('interaction_threshold', 5)}` interactions / `{are.get('interaction_window', 30)}s`  •  "
        f"Join age limit: `{are.get('join_age_limit', 120)}s`\n\n"
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
    am  = cfg["automod"]
    are = cfg["antiraid_ext"]
    return (
        "### 🤖 External App Raid Protection\n"
        "Detects raids controlled via external tools (selfbots, raid apps) by tracking "
        "how many recently-joined members fire bot interactions in quick succession.\n"
        "Also attempts to **identify the operator** behind the raid via invite audit logs.\n\n"
        f"{_icon(am.get('antiraid_ext'))} **Ext. App Raid** — currently {'active 🟢' if am.get('antiraid_ext') else 'inactive 🔴'}\n\n"
        "**Detection Settings**\n"
        f"Interaction threshold: `{are.get('interaction_threshold', 5)}` unique new members\n"
        f"Detection window: `{are.get('interaction_window', 30)}s`\n"
        f"'New member' = joined within last `{are.get('join_age_limit', 120)}s`\n\n"
        "**Response Actions**\n"
        f"Raiders: `{are.get('raider_action', 'kick')}`\n"
        f"Operator (if identified): `{are.get('operator_action', 'notify')}`\n\n"
        "-# Raider actions: `kick`, `ban`\n"
        "-# Operator actions: `notify` (log + DM owner), `kick`, `ban`"
    )


def _build_whitelist_text(cfg: dict, guild: discord.Guild) -> str:
    user_ids = cfg.get("whitelist_users", [])
    role_ids = cfg.get("whitelist_roles", [])

    user_lines = []
    for uid in user_ids:
        member = guild.get_member(uid) if guild else None
        user_lines.append(f"• {member.mention if member else f'<@{uid}>'}")

    role_lines = []
    for rid in role_ids:
        role = guild.get_role(rid) if guild else None
        role_lines.append(f"• {role.mention if role else f'<@&{rid}>'}")

    users_text = "\n".join(user_lines) if user_lines else "*None*"
    roles_text = "\n".join(role_lines) if role_lines else "*None*"

    return (
        "### 🔓 AutoMod Whitelist\n"
        "Whitelisted users and roles bypass all automod checks.\n\n"
        "**Whitelisted Users**\n"
        f"{users_text}\n\n"
        "**Whitelisted Roles**\n"
        f"{roles_text}\n\n"
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


# ─────────────────────────────────────────────────────────────
#  INTERACTIVE COMPONENTS
# ─────────────────────────────────────────────────────────────

class SectionSelect(discord.ui.Select):
    def __init__(self, automod_cog, guild_id: int, current_section: str):
        self._cog = automod_cog
        self._guild_id = guild_id
        options = [
            discord.SelectOption(label="Overview",       value="overview",  emoji="🛡️",
                                 description="Full snapshot of all protections",
                                 default=(current_section == "overview")),
            discord.SelectOption(label="Message Filter", value="filter",    emoji="💬",
                                 description="Spam, links, bad words, mass mention",
                                 default=(current_section == "filter")),
            discord.SelectOption(label="Anti-Nuke",      value="antinuke",  emoji="💣",
                                 description="Stop rogue mods from mass-deleting",
                                 default=(current_section == "antinuke")),
            discord.SelectOption(label="Anti-Raid",      value="antiraid",  emoji="🌊",
                                 description="Stop mass member join attacks",
                                 default=(current_section == "antiraid")),
            discord.SelectOption(label="Ext. App Raid",  value="ext_raid",  emoji="🤖",
                                 description="Detect raids via external apps / bots",
                                 default=(current_section == "ext_raid")),
            discord.SelectOption(label="Whitelist",      value="whitelist", emoji="🔓",
                                 description="Users and roles exempt from automod",
                                 default=(current_section == "whitelist")),
        ]
        super().__init__(placeholder="Navigate sections...", options=options,
                         min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        new_panel = _build_panel(self._cog, self._guild_id, self.values[0], interaction.guild)
        await interaction.response.edit_message(view=new_panel)


class ToggleButton(discord.ui.Button):
    def __init__(self, label: str, key: str, automod_cog, guild_id: int, section: str):
        self._cog = automod_cog
        self._guild_id = guild_id
        self._key = key
        self._section = section
        cfg = automod_cog.utils().get_guild_config(guild_id)
        enabled = cfg["automod"].get(key, False)
        super().__init__(
            label=f"{_icon(enabled)} {label}",
            style=discord.ButtonStyle.green if enabled else discord.ButtonStyle.red,
        )

    async def callback(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        cfg["automod"][self._key] = not cfg["automod"].get(self._key, False)
        utils.save_config()
        new_panel = _build_panel(self._cog, self._guild_id, self._section, interaction.guild)
        await interaction.response.edit_message(view=new_panel)


class EditThresholdsButton(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int, section: str):
        self._cog = automod_cog
        self._guild_id = guild_id
        self._section = section
        super().__init__(label="⚙️ Edit Thresholds", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        modal = _build_threshold_modal(cfg, self._cog, self._guild_id, self._section)
        await interaction.response.send_modal(modal)


# ─────────────────────────────────────────────────────────────
#  THRESHOLD MODALS
# ─────────────────────────────────────────────────────────────

class FilterThresholdModal(discord.ui.Modal, title="Message Filter Thresholds"):
    spam_msgs = discord.ui.TextInput(label="Spam: max messages",         placeholder="e.g. 6")
    spam_secs = discord.ui.TextInput(label="Spam: within seconds",       placeholder="e.g. 7")
    max_ment  = discord.ui.TextInput(label="Mass Mention: max mentions", placeholder="e.g. 5")

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        self.spam_msgs.default = str(cfg.get("spam_threshold", 6))
        self.spam_secs.default = str(cfg.get("spam_interval", 7))
        self.max_ment.default  = str(cfg.get("max_mentions", 5))

    async def on_submit(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["spam_threshold"] = max(1, int(self.spam_msgs.value))
            cfg["spam_interval"]  = max(1, int(self.spam_secs.value))
            cfg["max_mentions"]   = max(1, int(self.max_ment.value))
            utils.save_config()
            new_panel = _build_panel(self._cog, self._guild_id, "filter", interaction.guild)
            await interaction.response.edit_message(view=new_panel)
        except ValueError:
            await interaction.response.send_message("Please enter valid whole numbers.", ephemeral=True)


class AntiNukeThresholdModal(discord.ui.Modal, title="Anti-Nuke Thresholds"):
    ban_t    = discord.ui.TextInput(label="Ban threshold",            placeholder="e.g. 3")
    kick_t   = discord.ui.TextInput(label="Kick threshold",           placeholder="e.g. 3")
    chan_t   = discord.ui.TextInput(label="Channel delete threshold", placeholder="e.g. 3")
    role_t   = discord.ui.TextInput(label="Role delete threshold",    placeholder="e.g. 3")
    interval = discord.ui.TextInput(label="Interval (seconds)",       placeholder="e.g. 10")

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        an = cfg.get("antinuke", {})
        self.ban_t.default    = str(an.get("ban_threshold", 3))
        self.kick_t.default   = str(an.get("kick_threshold", 3))
        self.chan_t.default   = str(an.get("channel_delete_threshold", 3))
        self.role_t.default   = str(an.get("role_delete_threshold", 3))
        self.interval.default = str(an.get("interval", 10))

    async def on_submit(self, interaction: discord.Interaction):
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antinuke"]["ban_threshold"]            = max(1, int(self.ban_t.value))
            cfg["antinuke"]["kick_threshold"]           = max(1, int(self.kick_t.value))
            cfg["antinuke"]["channel_delete_threshold"] = max(1, int(self.chan_t.value))
            cfg["antinuke"]["role_delete_threshold"]    = max(1, int(self.role_t.value))
            cfg["antinuke"]["interval"]                 = max(1, int(self.interval.value))
            utils.save_config()
            new_panel = _build_panel(self._cog, self._guild_id, "antinuke", interaction.guild)
            await interaction.response.edit_message(view=new_panel)
        except ValueError:
            await interaction.response.send_message("Please enter valid whole numbers.", ephemeral=True)


class AntiNukeActionModal(discord.ui.Modal, title="Anti-Nuke Response Action"):
    action = discord.ui.TextInput(
        label="Action (strip / kick / ban)",
        placeholder="strip",
        max_length=10,
    )

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        self.action.default = cfg.get("antinuke", {}).get("action", "strip")

    async def on_submit(self, interaction: discord.Interaction):
        val = self.action.value.lower().strip()
        if val not in ("strip", "kick", "ban"):
            await interaction.response.send_message(
                "Invalid action. Choose: `strip`, `kick`, or `ban`.", ephemeral=True
            )
            return
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        cfg["antinuke"]["action"] = val
        utils.save_config()
        new_panel = _build_panel(self._cog, self._guild_id, "antinuke", interaction.guild)
        await interaction.response.edit_message(view=new_panel)


class AntiRaidThresholdModal(discord.ui.Modal, title="Anti-Raid Settings"):
    join_t = discord.ui.TextInput(label="Join threshold (members)", placeholder="e.g. 10")
    join_i = discord.ui.TextInput(label="Time window (seconds)",    placeholder="e.g. 10")
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
            await interaction.response.send_message(
                "Invalid action. Choose: `kick` or `lockdown`.", ephemeral=True
            )
            return
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antiraid"]["join_threshold"] = max(1, int(self.join_t.value))
            cfg["antiraid"]["join_interval"]  = max(1, int(self.join_i.value))
            cfg["antiraid"]["action"]         = val
            utils.save_config()
            new_panel = _build_panel(self._cog, self._guild_id, "antiraid", interaction.guild)
            await interaction.response.edit_message(view=new_panel)
        except ValueError:
            await interaction.response.send_message("Please enter valid whole numbers.", ephemeral=True)


class ExtRaidThresholdModal(discord.ui.Modal, title="Ext. App Raid Settings"):
    int_threshold = discord.ui.TextInput(label="Interaction threshold (unique users)", placeholder="e.g. 5")
    int_window    = discord.ui.TextInput(label="Detection window (seconds)",          placeholder="e.g. 30")
    join_age      = discord.ui.TextInput(label="Max member age to count (seconds)",   placeholder="e.g. 120")
    raider_act    = discord.ui.TextInput(label="Raider action (kick / ban)",          placeholder="kick",   max_length=10)
    operator_act  = discord.ui.TextInput(label="Operator action (notify / kick / ban)", placeholder="notify", max_length=10)

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        are = cfg.get("antiraid_ext", {})
        self.int_threshold.default = str(are.get("interaction_threshold", 5))
        self.int_window.default    = str(are.get("interaction_window", 30))
        self.join_age.default      = str(are.get("join_age_limit", 120))
        self.raider_act.default    = are.get("raider_action", "kick")
        self.operator_act.default  = are.get("operator_action", "notify")

    async def on_submit(self, interaction: discord.Interaction):
        raider_val   = self.raider_act.value.lower().strip()
        operator_val = self.operator_act.value.lower().strip()
        if raider_val not in ("kick", "ban"):
            return await interaction.response.send_message(
                "Invalid raider action. Choose: `kick` or `ban`.", ephemeral=True
            )
        if operator_val not in ("notify", "kick", "ban"):
            return await interaction.response.send_message(
                "Invalid operator action. Choose: `notify`, `kick`, or `ban`.", ephemeral=True
            )
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antiraid_ext"]["interaction_threshold"] = max(1, int(self.int_threshold.value))
            cfg["antiraid_ext"]["interaction_window"]    = max(5, int(self.int_window.value))
            cfg["antiraid_ext"]["join_age_limit"]        = max(10, int(self.join_age.value))
            cfg["antiraid_ext"]["raider_action"]         = raider_val
            cfg["antiraid_ext"]["operator_action"]       = operator_val
            utils.save_config()
            new_panel = _build_panel(self._cog, self._guild_id, "ext_raid", interaction.guild)
            await interaction.response.edit_message(view=new_panel)
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


# ─────────────────────────────────────────────────────────────
#  PANEL FACTORY
# ─────────────────────────────────────────────────────────────

def _build_panel(automod_cog, guild_id: int, section: str = "overview",
                 guild: discord.Guild = None) -> discord.ui.LayoutView:
    utils = automod_cog.utils()
    cfg = utils.get_guild_config(guild_id)

    view = discord.ui.LayoutView(timeout=300)
    text = _section_text(cfg, section, guild)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=text),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
    )
    container.add_item(
        discord.ui.ActionRow(SectionSelect(automod_cog, guild_id, section))
    )

    if section == "filter":
        container.add_item(discord.ui.ActionRow(
            ToggleButton("Anti-Spam",    "antispam",    automod_cog, guild_id, section),
            ToggleButton("Anti-Link",    "antilink",    automod_cog, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            ToggleButton("Bad Words",    "badwords",    automod_cog, guild_id, section),
            ToggleButton("Mass Mention", "massmention", automod_cog, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(automod_cog, guild_id, section),
        ))

    elif section == "antinuke":
        container.add_item(discord.ui.ActionRow(
            ToggleButton("Anti-Nuke", "antinuke", automod_cog, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(automod_cog, guild_id, section),
            _NukeActionButton(automod_cog, guild_id),
        ))

    elif section == "antiraid":
        container.add_item(discord.ui.ActionRow(
            ToggleButton("Anti-Raid", "antiraid", automod_cog, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(automod_cog, guild_id, section),
        ))

    elif section == "ext_raid":
        container.add_item(discord.ui.ActionRow(
            ToggleButton("Ext. App Raid", "antiraid_ext", automod_cog, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(automod_cog, guild_id, section),
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


# ─────────────────────────────────────────────────────────────
#  AUTOMOD COG
# ─────────────────────────────────────────────────────────────

class AutoMod(commands.Cog):
    """Automatic moderation: spam, links, badwords, mass mention, anti-nuke, anti-raid, ext-raid."""

    def __init__(self, bot):
        self.bot = bot
        self._msg_history         = {}   # guild_id -> user_id -> [timestamps]
        self._nuke_history        = {}   # guild_id -> user_id -> {action_key: [timestamps]}
        self._join_history        = {}   # guild_id -> [timestamps]
        self._interaction_history = {}   # guild_id -> [(user_id, timestamp)]
        self._invite_cache        = {}   # guild_id -> {invite_code: uses}

    def utils(self):
        return self.bot.get_cog("ModerationUtils")

    def get_cfg(self, guild_id: int):
        return self.utils().get_guild_config(guild_id)

    # ─── INVITE CACHE (for operator identification) ──────────

    @commands.Cog.listener()
    async def on_ready(self):
        """Snapshot invite use counts for all guilds on startup."""
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

    async def _identify_operator(self, guild: discord.Guild) -> discord.Member | None:
        """
        Try to find the account that orchestrated the raid by comparing current
        invite use counts against the cached snapshot taken before the raid.
        Returns the invite creator with the biggest jump in uses, or None.
        """
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

        if best_invite and best_delta >= 2 and best_invite.inviter:
            # Update cache now that we've used it
            self._invite_cache[guild.id] = {inv.code: inv.uses for inv in current_invites}
            return guild.get_member(best_invite.inviter.id)

        # Update cache regardless
        self._invite_cache[guild.id] = {inv.code: inv.uses for inv in current_invites}
        return None

    # ─── MESSAGE TRACKING ────────────────────────────────────

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

    # ─── MESSAGE FILTER ──────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return
        if not message.guild:
            return

        utils = self.utils()
        cfg = self.get_cfg(message.guild.id)
        content = message.content or ""

        if utils.is_whitelisted(message.guild.id, message.author):
            return

        if cfg["automod"].get("antispam", True):
            count = self._track_message(message)
            if count >= cfg.get("spam_threshold", 6):
                try:
                    await message.delete()
                except Exception:
                    pass
                await utils.log_action(
                    message.guild, "Anti-Spam",
                    f"{message.author.mention} triggered anti-spam in {message.channel.mention}."
                )
                await utils.mute_member(message.author, duration=60, reason="Auto-mute: spam")
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
                    f"**Message:**\n{content}"
                )
                return

        if cfg["automod"].get("badwords", True):
            if utils.contains_blocked_word(message.guild.id, content):
                try:
                    await message.delete()
                except Exception:
                    pass
                await utils.log_action(
                    message.guild, "Bad Word Filter",
                    f"{message.author.mention} used a blocked word in {message.channel.mention}."
                )
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
                    f"{message.author.mention} mass-mentioned `{mentions}` users in {message.channel.mention}."
                )
                await utils.mute_member(message.author, duration=120, reason="Auto-mute: mass mention")
                return

    # ─── EXTERNAL APP RAID DETECTION ─────────────────────────

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """
        Track interactions from recently-joined members.
        When enough unique new members fire interactions within the configured
        window, it indicates an external app is controlling those accounts.
        """
        if not interaction.guild:
            return

        guild  = interaction.guild
        member = interaction.user

        cfg = self.get_cfg(guild.id)
        if not cfg["automod"].get("antiraid_ext", False):
            return

        # Skip bots and whitelisted accounts
        if member.bot:
            return
        if self.utils().is_whitelisted(guild.id, member):
            return

        are = cfg.get("antiraid_ext", {})
        join_age_limit = are.get("join_age_limit", 120)

        # Only count members who joined very recently
        joined_at = getattr(member, "joined_at", None)
        if not joined_at:
            return
        now = time.time()
        if now - joined_at.timestamp() > join_age_limit:
            return

        # Record the interaction
        bucket = self._interaction_history.setdefault(guild.id, [])
        bucket.append((member.id, now))

        # Prune old entries
        window = are.get("interaction_window", 30)
        self._interaction_history[guild.id] = [
            (uid, t) for uid, t in bucket if now - t <= window
        ]

        unique_users = len({uid for uid, _ in self._interaction_history[guild.id]})
        threshold    = are.get("interaction_threshold", 5)

        if unique_users >= threshold:
            # Reset to prevent repeated triggers
            raider_ids = list({uid for uid, _ in self._interaction_history[guild.id]})
            self._interaction_history[guild.id] = []

            log.warning(
                "Ext-Raid",
                f"External-app raid detected in {guild.name} — "
                f"{unique_users} new members fired interactions within {window}s."
            )
            await self._handle_ext_raid(guild, cfg, raider_ids)

    async def _handle_ext_raid(self, guild: discord.Guild, cfg: dict, raider_ids: list[int]):
        """Punish raiding accounts and attempt to identify the operator."""
        are           = cfg.get("antiraid_ext", {})
        raider_action = are.get("raider_action", "kick")
        op_action     = are.get("operator_action", "notify")

        # ── Identify the operator via invite delta ──
        operator = await self._identify_operator(guild)

        # ── Log the event ──
        op_mention = operator.mention if operator else "*could not be determined*"
        raider_mentions = ", ".join(f"<@{uid}>" for uid in raider_ids)
        await self.utils().log_action(
            guild,
            "🤖 External App Raid Detected",
            f"**{len(raider_ids)}** recently-joined member(s) fired bot interactions in rapid "
            f"succession — consistent with an external raid tool.\n\n"
            f"**Suspected Operator:** {op_mention}\n"
            f"**Raiding Accounts:** {raider_mentions}\n\n"
            f"Raider action: `{raider_action}` | Operator action: `{op_action}`"
        )

        # ── Act on raiders ──
        for uid in raider_ids:
            member = guild.get_member(uid)
            if not member:
                continue
            try:
                if raider_action == "ban":
                    await guild.ban(member, reason="Ext. App Raid: automated interaction flood")
                else:
                    await member.kick(reason="Ext. App Raid: automated interaction flood")
                await asyncio.sleep(0.4)
            except Exception:
                pass

        # ── Act on operator ──
        if operator:
            try:
                if op_action == "ban":
                    await guild.ban(operator, reason="Ext. App Raid: suspected raid orchestrator")
                elif op_action == "kick":
                    await operator.kick(reason="Ext. App Raid: suspected raid orchestrator")
            except Exception:
                pass

        # ── DM the server owner ──
        try:
            await guild.owner.send(
                f"⚠️ **External App Raid detected** in **{guild.name}**!\n"
                f"`{len(raider_ids)}` recently-joined members fired bot interactions simultaneously.\n"
                f"**Suspected operator:** {operator or 'unknown'}\n"
                f"Raider action: `{raider_action}` | Operator action: `{op_action}`"
            )
        except Exception:
            pass

    # ─── ANTI-RAID (JOIN FLOOD) ───────────────────────────────

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild

        # Snapshot invites on every join for operator identification
        await self._snapshot_invites(guild)

        cfg = self.get_cfg(guild.id)
        if not cfg["automod"].get("antiraid", False):
            return

        ar        = cfg.get("antiraid", {})
        threshold = ar.get("join_threshold", 10)
        interval  = ar.get("join_interval", 10)
        action    = ar.get("action", "kick")

        now    = time.time()
        cutoff = now - interval
        bucket = self._join_history.setdefault(guild.id, [])
        bucket.append(now)
        self._join_history[guild.id] = [t for t in bucket if t >= cutoff]

        if len(self._join_history[guild.id]) >= threshold:
            self._join_history[guild.id] = []
            log.warning("Anti-Raid", f"Raid detected in {guild.name} — action: {action}")
            await self.utils().log_action(
                guild, "🌊 Anti-Raid Triggered",
                f"**{len(bucket)}** members joined within `{interval}s`. Executing `{action}`."
            )
            if action == "kick":
                for m in list(guild.members):
                    joined = m.joined_at
                    if joined and (now - joined.timestamp()) <= interval + 2:
                        try:
                            await m.kick(reason="Anti-Raid: mass join detected")
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
                            reason="Anti-Raid lockdown"
                        )
                    except Exception:
                        pass
            try:
                await guild.owner.send(
                    f"⚠️ **Anti-Raid triggered** in **{guild.name}**!\n"
                    f"{len(bucket)} members joined in {interval}s. Action taken: `{action}`."
                )
            except Exception:
                pass

    # ─── ANTI-NUKE ───────────────────────────────────────────

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        guild = entry.guild
        if not guild:
            return

        cfg = self.get_cfg(guild.id)
        if not cfg["automod"].get("antinuke", False):
            return

        if entry.user.id == self.bot.user.id or guild.owner_id:
            return

        an       = cfg.get("antinuke", {})
        interval = an.get("interval", 10)

        action_map = {
            discord.AuditLogAction.ban:            ("ban",            an.get("ban_threshold", 3)),
            discord.AuditLogAction.kick:           ("kick",           an.get("kick_threshold", 3)),
            discord.AuditLogAction.channel_delete: ("channel_delete", an.get("channel_delete_threshold", 3)),
            discord.AuditLogAction.role_delete:    ("role_delete",    an.get("role_delete_threshold", 3)),
        }

        if entry.action not in action_map:
            return

        action_key, threshold = action_map[entry.action]
        now    = time.time()
        cutoff = now - interval
        uid    = entry.user.id

        user_history = self._nuke_history.setdefault(guild.id, {}).setdefault(uid, {})
        bucket       = user_history.setdefault(action_key, [])
        bucket.append(now)
        user_history[action_key] = [t for t in bucket if t >= cutoff]

        if len(user_history[action_key]) >= threshold:
            user_history[action_key] = []
            offender    = entry.user
            nuke_action = an.get("action", "strip")

            log.warning("Anti-Nuke", f"Nuke detected by {offender} in {guild.name} — action: {nuke_action}")
            await self.utils().log_action(
                guild, "💣 Anti-Nuke Triggered",
                f"**{offender.mention}** performed `{threshold}` `{action_key}` actions "
                f"within `{interval}s`. Action taken: `{nuke_action}`."
            )

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
                    f"⚠️ **Anti-Nuke triggered** in **{guild.name}**!\n"
                    f"{offender} performed `{threshold}` `{action_key}` actions in `{interval}s`.\n"
                    f"Action taken: `{nuke_action}`."
                )
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
                await member.remove_roles(*roles_to_remove, reason="Anti-Nuke: dangerous roles stripped")
            except Exception:
                pass

    # ─── SETTINGS COMMAND ────────────────────────────────────

    @commands.command(name="automod", help="Open the AutoMod settings panel ☕🛡️ | AutoMod-Einstellungen")
    @commands.has_permissions(manage_guild=True)
    async def automod_settings(self, ctx):
        """Open the interactive AutoMod settings dashboard."""
        panel = _build_panel(self, ctx.guild.id, "overview", ctx.guild)
        await ctx.send(view=panel)


async def setup(bot):
    await bot.add_cog(AutoMod(bot))
