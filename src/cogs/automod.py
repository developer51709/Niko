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
    am = cfg["automod"]
    an = cfg["antinuke"]
    ar = cfg["antiraid"]
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
        f"Interval: `{an.get('interval', 10)}s`\n"
        f"Ban ≥`{an.get('ban_threshold', 3)}`  •  "
        f"Kick ≥`{an.get('kick_threshold', 3)}`  •  "
        f"Del-Channel ≥`{an.get('channel_delete_threshold', 3)}`  •  "
        f"Del-Role ≥`{an.get('role_delete_threshold', 3)}`\n\n"
        "**🌊 Anti-Raid**\n"
        f"{_icon(am.get('antiraid'))} Enabled  •  "
        f"Action: `{ar.get('action', 'kick')}`\n"
        f"Threshold: `{ar.get('join_threshold', 10)}` joins / `{ar.get('join_interval', 10)}s`\n\n"
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
        f"-# Actions: `strip` (remove dangerous roles), `kick`, `ban`"
    )


def _build_antiraid_text(cfg: dict) -> str:
    am = cfg["automod"]
    ar = cfg["antiraid"]
    return (
        "### 🌊 Anti-Raid Settings\n"
        "Detects and responds to mass member join events.\n\n"
        f"{_icon(am.get('antiraid'))} **Anti-Raid** — currently {'active 🟢' if am.get('antiraid') else 'inactive 🔴'}\n\n"
        f"**Join Threshold:** `{ar.get('join_threshold', 10)}` members\n"
        f"**Time Window:** `{ar.get('join_interval', 10)}` seconds\n"
        f"**Action on trigger:** `{ar.get('action', 'kick')}`\n\n"
        "-# Actions: `kick` (kick all recent joiners), `lockdown` (lock all channels)"
    )


def _section_text(cfg: dict, section: str) -> str:
    if section == "filter":
        return _build_filter_text(cfg)
    if section == "antinuke":
        return _build_antinuke_text(cfg)
    if section == "antiraid":
        return _build_antiraid_text(cfg)
    return _build_overview_text(cfg)


# ─────────────────────────────────────────────────────────────
#  INTERACTIVE COMPONENTS
# ─────────────────────────────────────────────────────────────

class SectionSelect(discord.ui.Select):
    def __init__(self, automod_cog, guild_id: int, current_section: str):
        self._cog = automod_cog
        self._guild_id = guild_id
        options = [
            discord.SelectOption(label="Overview", value="overview", emoji="🛡️",
                                 description="Full snapshot of all protections",
                                 default=(current_section == "overview")),
            discord.SelectOption(label="Message Filter", value="filter", emoji="💬",
                                 description="Spam, links, bad words, mass mention",
                                 default=(current_section == "filter")),
            discord.SelectOption(label="Anti-Nuke", value="antinuke", emoji="💣",
                                 description="Stop rogue mods from mass-deleting",
                                 default=(current_section == "antinuke")),
            discord.SelectOption(label="Anti-Raid", value="antiraid", emoji="🌊",
                                 description="Stop mass member join attacks",
                                 default=(current_section == "antiraid")),
        ]
        super().__init__(placeholder="Navigate sections...", options=options,
                         min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        new_panel = _build_panel(self._cog, self._guild_id, self.values[0])
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
        new_panel = _build_panel(self._cog, self._guild_id, self._section)
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
            new_panel = _build_panel(self._cog, self._guild_id, "filter")
            await interaction.response.edit_message(view=new_panel)
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
            new_panel = _build_panel(self._cog, self._guild_id, "antinuke")
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
        new_panel = _build_panel(self._cog, self._guild_id, "antinuke")
        await interaction.response.edit_message(view=new_panel)


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
            await interaction.response.send_message(
                "Invalid action. Choose: `kick` or `lockdown`.", ephemeral=True
            )
            return
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antiraid"]["join_threshold"] = max(1, int(self.join_t.value))
            cfg["antiraid"]["join_interval"] = max(1, int(self.join_i.value))
            cfg["antiraid"]["action"] = val
            utils.save_config()
            new_panel = _build_panel(self._cog, self._guild_id, "antiraid")
            await interaction.response.edit_message(view=new_panel)
        except ValueError:
            await interaction.response.send_message("Please enter valid whole numbers.", ephemeral=True)


def _build_threshold_modal(cfg, automod_cog, guild_id, section):
    if section == "antinuke":
        return AntiNukeThresholdModal(automod_cog, guild_id, cfg)
    if section == "antiraid":
        return AntiRaidThresholdModal(automod_cog, guild_id, cfg)
    return FilterThresholdModal(automod_cog, guild_id, cfg)


# ─────────────────────────────────────────────────────────────
#  PANEL FACTORY
# ─────────────────────────────────────────────────────────────

def _build_panel(automod_cog, guild_id: int, section: str = "overview") -> discord.ui.LayoutView:
    utils = automod_cog.utils()
    cfg = utils.get_guild_config(guild_id)

    view = discord.ui.LayoutView(timeout=300)

    # Content container
    text = _section_text(cfg, section)
    container = discord.ui.Container(
        discord.ui.TextDisplay(
            content=text
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
    )

    # Section navigation dropdown
    container.add_item(
        discord.ui.ActionRow(
            SectionSelect(automod_cog, guild_id, section)
        )
    )

    # Toggle buttons for each section
    if section == "filter":
        container.add_item(
            discord.ui.ActionRow(
            
                ToggleButton("Anti-Spam", "antispam", automod_cog, guild_id, section),
                ToggleButton("Anti-Link", "antilink", automod_cog, guild_id, section),
            )
        )
        container.add_item(
            discord.ui.ActionRow(
                ToggleButton("Bad Words", "badwords", automod_cog, guild_id, section),
                ToggleButton("Mass Mention", "massmention", automod_cog, guild_id, section),
            )
        )
        container.add_item(
            discord.ui.ActionRow(
                EditThresholdsButton(automod_cog, guild_id, section),
            )
        )

    elif section == "antinuke":
        container.add_item(
            discord.ui.ActionRow(
                ToggleButton("Anti-Nuke", "antinuke", automod_cog, guild_id, section),
            )
        )
        container.add_item(
            discord.ui.ActionRow(
                EditThresholdsButton(automod_cog, guild_id, section),
                _NukeActionButton(automod_cog, guild_id),
            )
        )

    elif section == "antiraid":
        container.add_item(
            discord.ui.ActionRow(
                ToggleButton("Anti-Raid", "antiraid", automod_cog, guild_id, section),
            )
        )
        container.add_item(
            discord.ui.ActionRow(
                EditThresholdsButton(automod_cog, guild_id, section),
            )
        )
    view.add_item(container)
    return view


class _NukeActionButton(discord.ui.Button):
    """Sets the anti-nuke response action via modal."""
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
    """Automatic moderation: spam, links, badwords, mass mention, anti-nuke, anti-raid."""

    def __init__(self, bot):
        self.bot = bot
        self._msg_history = {}        # guild_id -> user_id -> [timestamps]
        self._nuke_history = {}       # guild_id -> user_id -> {action_key: [timestamps]}
        self._join_history = {}       # guild_id -> [timestamps]

    def utils(self):
        return self.bot.get_cog("ModerationUtils")

    def get_cfg(self, guild_id: int):
        return self.utils().get_guild_config(guild_id)

    # ─── MESSAGE TRACKING ───────────────────────────────────

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
        if not message.guild or message.author.bot:
            return
        utils = self.utils()
        cfg = self.get_cfg(message.guild.id)
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
                    f"{message.author.mention} posted an invite link in {message.channel.mention}."
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

    # ─── ANTI-RAID ───────────────────────────────────────────

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
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
            self._join_history[guild.id] = []  # reset to avoid repeated triggers
            log.warning("Anti-Raid", f"Raid detected in {guild.name} — action: {action}")
            await self.utils().log_action(
                guild, "🌊 Anti-Raid Triggered",
                f"**{len(bucket)}** members joined within `{interval}s`. Executing `{action}`."
            )
            if action == "kick":
                # Kick all members who joined in the raid window
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

            # DM server owner
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

        # Don't track bot or guild owner actions
        if not entry.user or entry.user.bot:
            return
        if entry.user.id == guild.owner_id:
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
        bucket = user_history.setdefault(action_key, [])
        bucket.append(now)
        user_history[action_key] = [t for t in bucket if t >= cutoff]

        if len(user_history[action_key]) >= threshold:
            # Reset to avoid repeat triggers
            user_history[action_key] = []

            offender = entry.user
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

            # DM owner
            try:
                await guild.owner.send(
                    f"⚠️ **Anti-Nuke triggered** in **{guild.name}**!\n"
                    f"{offender} performed `{threshold}` `{action_key}` actions in `{interval}s`.\n"
                    f"Action taken: `{nuke_action}`."
                )
            except Exception:
                pass

    async def _strip_dangerous_roles(self, member: discord.Member):
        """Remove all roles that grant dangerous permissions from a member."""
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
        panel = _build_panel(self, ctx.guild.id, "overview")
        await ctx.send(view=panel)


async def setup(bot):
    await bot.add_cog(AutoMod(bot))
