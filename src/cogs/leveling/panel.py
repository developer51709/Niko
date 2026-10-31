import discord
from discord.ext import commands
import random
import json
import os
import time
from utils import logging as log
from utils.paginator import PaginatedView, paginate
from utils.i18n import make_flat_msg
from config.emojis import get_emoji
from utils.locales import load_locales

# The brand accent shared by every Niko view, used when a guild has not picked
# custom card colours.
ACCENT_BRAND = 0xC8A882

# Discord's hard limit for both the option list and ``max_values`` of a select.
MAX_SELECT_OPTIONS = 25

# ───────────────────────────────────────────────────
#  MESSAGE TABLE
# ───────────────────────────────────────────────────

MESSAGES = load_locales("cogs.leveling", "panel")


msg = make_flat_msg(MESSAGES, {
    "tick": get_emoji("tick"),
    "cross": get_emoji("cross"),
})


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


def _fill(template: str, **values) -> str:
    """Substitute ``{token}`` placeholders without ``str.format``.

    A panel body pastes member-authored text into the sentence — a custom
    level-up message, a role name — and that text may itself contain braces
    (the level-up template legitimately holds ``{mention}`` and ``{level}``).
    Running the result through ``str.format`` would raise on those, so the
    tokens are replaced literally instead.
    """
    for name, value in values.items():
        template = template.replace("{" + name + "}", str(value))
    return template


def _colour_hex(rgb):
    """Convert an RGB tuple to a Discord colour integer or None."""
    if not rgb:
        return None
    return (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]


def _lv_role_mention(guild: discord.Guild, role_id) -> str:
    """Mention a configured level role, or name it plainly once it is gone.

    A deleted role must never break the panel: ``discord.Object`` has no
    ``mention``, so rendering one directly used to raise and take the whole
    section down with it.
    """
    try:
        role = guild.get_role(int(role_id))
    except (TypeError, ValueError):
        role = None
    return role.mention if role else msg(guild, "panel_deleted_role", role_id=role_id)


def _lv_overview_text(cfg: dict, guild: discord.Guild) -> str:
    lu_ch   = guild.get_channel(cfg.get("level_up_channel") or 0)
    lu_ch_s = lu_ch.mention if lu_ch else msg(guild, "panel_same_channel")
    lr      = cfg.get("level_roles", {})
    role_line = msg(guild, "panel_overview_role_line")
    lr_s    = "\n".join(
        _fill(role_line, level=lvl, role=_lv_role_mention(guild, rid))
        for lvl, rid in sorted(lr.items(), key=lambda x: int(x[0]))
    ) or msg(guild, "panel_no_roles")
    custom_msg = cfg.get("level_up_message")
    msg_s = f"`{custom_msg}`" if custom_msg else msg(guild, "panel_default_message")

    # Card style summary
    accent = cfg.get("card_accent")
    accent_s = f"#{accent[0]:02x}{accent[1]:02x}{accent[2]:02x}" if accent else msg(guild, "panel_default_gold")

    excluded = cfg.get("xp_excluded_channels") or []
    return _fill(
        msg(guild, "panel_overview"),
        xp_state=_lv_icon(cfg.get("xp_enabled", True)),
        multiplier=cfg.get("xp_multiplier", 1.0),
        cooldown=cfg.get("xp_cooldown", 0),
        excluded=len(excluded),
        voice_state=_lv_icon(cfg.get("xp_vc_enabled", False)),
        levelup_channel=lu_ch_s,
        custom_message=msg_s,
        roles=lr_s,
        accent=accent_s,
    )


def _lv_xp_text(cfg: dict, guild: discord.Guild) -> str:
    cd = cfg.get("xp_cooldown", 0)
    cd_s = _fill(msg(guild, "panel_xp_cooldown_on"), seconds=cd) if cd > 0 \
        else msg(guild, "panel_xp_cooldown_off")
    return _fill(
        msg(guild, "panel_xp"),
        state=get_emoji('enabled') if cfg.get('xp_enabled', True) else get_emoji('disabled'),
        multiplier=cfg.get('xp_multiplier', 1.0),
        cooldown=cd_s,
    )


def _lv_announcements_text(cfg: dict, guild: discord.Guild) -> str:
    lu_ch      = guild.get_channel(cfg.get("level_up_channel") or 0)
    lu_ch_s    = lu_ch.mention if lu_ch else msg(guild, "panel_announcement_same_channel")
    custom_msg = cfg.get("level_up_message")
    msg_display = custom_msg if custom_msg else msg(guild, "level_up")
    return _fill(
        msg(guild, "panel_announcements"),
        channel=lu_ch_s,
        message=msg_display,
    )


def _lv_roles_text(cfg: dict, guild: discord.Guild) -> str:
    lr = cfg.get("level_roles", {})
    if lr:
        lines = []
        for lvl, rid in sorted(lr.items(), key=lambda x: int(x[0])):
            lines.append(_fill(
                msg(guild, "panel_role_line"),
                level=lvl,
                role=_lv_role_mention(guild, rid),
            ))
        roles_body = "\n".join(lines)
    else:
        roles_body = msg(guild, "panel_no_level_roles_body")

    return _fill(
        msg(guild, "panel_roles"),
        roles=roles_body,
        plus=get_emoji("plus"),
    )


def _lv_channels_text(cfg: dict, guild: discord.Guild) -> str:
    excluded_ids = cfg.get("xp_excluded_channels") or []
    if excluded_ids:
        lines = []
        for cid in excluded_ids:
            channel = guild.get_channel(int(cid))
            lines.append(
                _fill(msg(guild, "panel_channel_line"), channel=channel.mention)
                if channel else
                _fill(msg(guild, "panel_deleted_channel"), cid=cid)
            )
        excluded_body = "\n".join(lines)
    else:
        excluded_body = msg(guild, "panel_no_excluded_body")

    vc_enabled = bool(cfg.get("xp_vc_enabled", False))
    return _fill(
        msg(guild, "panel_channels"),
        excluded=excluded_body,
        voice=_lv_icon(vc_enabled),
    )


def _lv_cardstyle_text(cfg: dict, guild: discord.Guild) -> str:
    def _fmt_rgb(rgb):
        if not rgb:
            return msg(guild, "panel_default_colour")
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    return _fill(
        msg(guild, "panel_cardstyle"),
        accent=_fmt_rgb(cfg.get("card_accent")),
        bg_top=_fmt_rgb(cfg.get("card_bg_top")),
        bg_bottom=_fmt_rgb(cfg.get("card_bg_bottom")),
    )


def _lv_section_text(cfg: dict, section: str, guild: discord.Guild) -> str:
    if section == "xp":            return _lv_xp_text(cfg, guild)
    if section == "channels":      return _lv_channels_text(cfg, guild)
    if section == "announcements": return _lv_announcements_text(cfg, guild)
    if section == "level_roles":   return _lv_roles_text(cfg, guild)
    if section == "card_style":    return _lv_cardstyle_text(cfg, guild)
    return _lv_overview_text(cfg, guild)


# ───────────────────────────────────────────────────
#  PANEL INTERACTIVE COMPONENTS
# ───────────────────────────────────────────────────

class _LevelPanelView(discord.ui.LayoutView):
    """The panel itself, guarded for everyone except Manage Server holders.

    The panel is posted in the channel instead of as an ephemeral message, so
    without this check any member able to see the channel could flip XP off or
    reconfigure the server. Every control on the panel goes through here.
    """

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        permissions = getattr(interaction.user, "guild_permissions", None)
        if permissions is not None and permissions.manage_guild:
            return True

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(interaction, "panel_permission_error")
            ),
            accent_colour=discord.Color.red(),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)
        return False


class _LvSectionSelect(discord.ui.Select):
    def __init__(self, cog, guild_id: int, current: str, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        options = [
            discord.SelectOption(
                label=msg(ctx, "panel_nav_overview"), value="overview", emoji="📋",
                description=msg(ctx, "panel_nav_overview_description"),
                default=(current == "overview")),
            discord.SelectOption(
                label=msg(ctx, "panel_nav_xp"), value="xp", emoji="📊",
                description=msg(ctx, "panel_nav_xp_description"),
                default=(current == "xp")),
            discord.SelectOption(
                label=msg(ctx, "panel_nav_channels"), value="channels", emoji="📡",
                description=msg(ctx, "panel_nav_channels_description"),
                default=(current == "channels")),
            discord.SelectOption(
                label=msg(ctx, "panel_nav_announcements"), value="announcements", emoji="📣",
                description=msg(ctx, "panel_nav_announcements_description"),
                default=(current == "announcements")),
            discord.SelectOption(
                label=msg(ctx, "panel_nav_roles"), value="level_roles", emoji="🎖️",
                description=msg(ctx, "panel_nav_roles_description"),
                default=(current == "level_roles")),
            discord.SelectOption(
                label=msg(ctx, "panel_nav_card"), value="card_style", emoji="🎨",
                description=msg(ctx, "panel_nav_card_description"),
                default=(current == "card_style")),
        ]
        super().__init__(
            placeholder=msg(ctx, "panel_nav_placeholder"), options=options,
            min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        panel = await _build_level_panel(self._cog, self._guild_id, self.values[0], interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvXPToggleBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, cfg: dict, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        enabled = cfg.get("xp_enabled", True)
        super().__init__(
            label=msg(ctx, "panel_btn_xp_tracking"),
            style=discord.ButtonStyle.green if enabled else discord.ButtonStyle.red,
            emoji=_lv_icon(enabled),
        )

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["xp_enabled"] = not cfg.get("xp_enabled", True)
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "xp", interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvXPSettingsModal(discord.ui.Modal):
    def __init__(self, cog, guild_id: int, cfg: dict, ctx):
        super().__init__(title=msg(ctx, "panel_xp_modal_title"))
        self._cog      = cog
        self._guild_id = guild_id
        self.multiplier = discord.ui.TextInput(
            label=msg(ctx, "panel_xp_multiplier_label"), placeholder="1.0")
        self.cooldown = discord.ui.TextInput(
            label=msg(ctx, "panel_xp_cooldown_label"), placeholder="0")
        self.multiplier.default = str(cfg.get("xp_multiplier", 1.0))
        self.cooldown.default   = str(cfg.get("xp_cooldown", 0))
        self.add_item(self.multiplier)
        self.add_item(self.cooldown)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            mult = round(max(0.1, float(self.multiplier.value)), 2)
            cd   = max(0, int(self.cooldown.value))
        except ValueError:
            return await interaction.response.send_message(
                msg(interaction, "panel_invalid_numbers"), ephemeral=True)
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["xp_multiplier"] = mult
        cfg["xp_cooldown"]   = cd
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "xp", interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvEditXPBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(
            label=msg(ctx, "panel_btn_edit_xp"), style=discord.ButtonStyle.blurple,
            emoji=get_emoji("settings"))

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        await interaction.response.send_modal(
            _LvXPSettingsModal(self._cog, self._guild_id, cfg, interaction))


# ── Channels & Voice ─────────────────────────────

class _LvExcludedChannelsSelect(discord.ui.ChannelSelect):
    def __init__(self, cog, guild_id: int, cfg: dict, ctx):
        super().__init__(
            placeholder=msg(ctx, "panel_select_exclude_add"),
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
    def __init__(self, cog, guild_id: int, options: list, message: discord.Message, ctx):
        # Discord caps a select at 25 options and 25 max_values. Clamping both
        # together matters: a guild with more exclusions than that used to hand
        # ``max_values`` a value the select refuses to accept.
        options = list(options)[:MAX_SELECT_OPTIONS]
        super().__init__(
            placeholder=msg(ctx, "panel_select_exclude_remove"),
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
                content=msg(interaction, "panel_removed_channels", count=len(removed))
            ),
            accent_colour=discord.Color.green(),
        ))
        await interaction.response.edit_message(view=view)
        panel = await _build_level_panel(self._cog, self._guild_id, "channels", interaction.guild)
        await self.message.edit(view=panel)


class _LvRemoveExcludedBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, has_excluded: bool, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(
            label=msg(ctx, "panel_btn_remove_exclusion"),
            style=discord.ButtonStyle.red, disabled=not has_excluded)

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        options = []
        for cid in cfg.get("xp_excluded_channels") or []:
            channel = interaction.guild.get_channel(int(cid))
            name = f"#{channel.name}" if channel else msg(
                interaction, "panel_channel_name", cid=cid)
            options.append(discord.SelectOption(
                label=name[:100],
                value=str(cid),
                description=msg(interaction, "panel_channel_id", cid=cid),
            ))
        if not options:
            return await interaction.response.send_message(
                msg(interaction, "panel_no_excluded"), ephemeral=True)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(interaction, "panel_select_award")),
            discord.ui.ActionRow(
                _LvRemoveExcludedSelect(
                    self._cog, self._guild_id, options, interaction.message, interaction)
            ),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class _LvVCToggleBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, cfg: dict, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        enabled = bool(cfg.get("xp_vc_enabled", False))
        super().__init__(
            label=msg(ctx, "panel_btn_voice_xp"),
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
    def __init__(self, cog, guild_id: int, has_excluded: bool, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(
            label=msg(ctx, "panel_btn_clear_exclusions"),
            style=discord.ButtonStyle.red, disabled=not has_excluded)

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["xp_excluded_channels"] = []
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "channels", interaction.guild)
        await interaction.response.edit_message(view=panel)


# ── Announcements ──────────────────────────────────

class _LvChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, cog, guild_id: int, ctx):
        super().__init__(
            placeholder=msg(ctx, "panel_select_channel"),
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
            content=msg(interaction, "panel_levelup_channel_set", channel=channel.mention), view=None)


class _LvClearChannelBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(
            label=msg(ctx, "panel_btn_clear_channel"), style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["level_up_channel"] = None
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        await interaction.response.edit_message(
            content=msg(interaction, "panel_levelup_same_channel"), view=None)


class _LvSetChannelBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label=msg(ctx, "panel_btn_set_channel"), style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        view = discord.ui.View(timeout=60)
        view.add_item(_LvChannelSelect(self._cog, self._guild_id, interaction))
        view.add_item(_LvClearChannelBtn(self._cog, self._guild_id, interaction))
        await interaction.response.send_message(
            msg(interaction, "panel_choose_levelup_channel"),
            view=view, ephemeral=True)


class _LvMessageModal(discord.ui.Modal):
    def __init__(self, cog, guild_id: int, cfg: dict, ctx):
        super().__init__(title=msg(ctx, "panel_message_modal_title"))
        self._cog      = cog
        self._guild_id = guild_id
        self.message = discord.ui.TextInput(
            label=msg(ctx, "panel_message_label"),
            placeholder=msg(ctx, "panel_message_placeholder"),
            style=discord.TextStyle.paragraph,
            max_length=400,
        )
        self.message.default = cfg.get("level_up_message") or ""
        self.add_item(self.message)

    async def on_submit(self, interaction: discord.Interaction):
        val = self.message.value.strip()
        if not val:
            return await interaction.response.send_message(
                msg(interaction, "panel_message_empty"),
                ephemeral=True)
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["level_up_message"] = val
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "announcements", interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvEditMessageBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label=msg(ctx, "panel_btn_edit_message"), style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        await interaction.response.send_modal(
            _LvMessageModal(self._cog, self._guild_id, cfg, interaction))


class _LvResetMessageBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, has_custom: bool, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(
            label=msg(ctx, "panel_btn_reset_message"),
            style=discord.ButtonStyle.red, disabled=not has_custom)

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["level_up_message"] = None
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "announcements", interaction.guild)
        await interaction.response.edit_message(view=panel)


# ── Level Roles ────────────────────────────────────

class _LvRoleAssignSelect(discord.ui.RoleSelect):
    def __init__(self, cog, guild_id: int, level: int, message: discord.Message | None, ctx):
        super().__init__(placeholder=msg(ctx, "panel_select_role"), min_values=1, max_values=1)
        self._cog      = cog
        self._guild_id = guild_id
        self._level    = level
        self.message   = message

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        cfg  = await self._cog._guild_cfg(self._guild_id)
        previous = dict(cfg.setdefault("level_roles", {}))
        cfg.setdefault("level_roles", {})[str(self._level)] = role.id
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        # Members who already passed this level get the reward now, and a role
        # moved here from another level is taken back from those below it.
        self._cog._queue_level_role_sync(
            interaction.guild, cfg["level_roles"], previous)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(
                    interaction,
                    "panel_level_reward",
                    level=self._level,
                    role=role.mention,
                )
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)
        if self.message is not None:
            panel = await _build_level_panel(self._cog, self._guild_id, "level_roles", interaction.guild)
            await self.message.edit(view=panel)


class _LvAddRoleModal(discord.ui.Modal):
    def __init__(self, cog, guild_id: int, ctx,
                 panel_message: discord.Message | None = None):
        super().__init__(title=msg(ctx, "panel_add_role_modal_title"))
        self._cog          = cog
        self._guild_id     = guild_id
        self.level_num = discord.ui.TextInput(
            label=msg(ctx, "panel_level_number_label"),
            placeholder=msg(ctx, "panel_level_number_ph"),
            min_length=1, max_length=4,
        )
        self.add_item(self.level_num)
        # Carried over from the button instead of read off the modal submit
        # interaction, which does not reliably include the panel message.
        self._panel_message = panel_message

    async def on_submit(self, interaction: discord.Interaction):
        try:
            lvl = max(1, int(self.level_num.value))
        except ValueError:
            return await interaction.response.send_message(
                msg(interaction, "panel_invalid_level"), ephemeral=True)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(interaction, "panel_pick_role_for_level", level=lvl)
            ),
            discord.ui.ActionRow(
                _LvRoleAssignSelect(
                    self._cog, self._guild_id, lvl, self._panel_message, interaction)
            )
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


class _LvAddRoleBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(
            label=msg(ctx, "panel_btn_add_role"),
            style=discord.ButtonStyle.green, emoji=get_emoji("plus"))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(
            _LvAddRoleModal(self._cog, self._guild_id, interaction,
                            panel_message=interaction.message)
        )


class _LvRemoveRoleSelect(discord.ui.Select):
    def __init__(self, cog, guild_id: int, options: list, message: discord.Message, ctx):
        # See _LvRemoveExcludedSelect: options and max_values share Discord's
        # hard limit of 25.
        options = list(options)[:MAX_SELECT_OPTIONS]
        super().__init__(
            placeholder=msg(ctx, "panel_select_roles_remove_placeholder"),
            min_values=1, max_values=len(options),
            options=options,
        )
        self._cog      = cog
        self._guild_id = guild_id
        self.message   = message

    async def callback(self, interaction: discord.Interaction):
        cfg = await self._cog._guild_cfg(self._guild_id)
        lr  = cfg.setdefault("level_roles", {})
        previous = dict(lr)
        for val in self.values:
            lr.pop(val, None)
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        # A removed reward is taken off the members who had earned it.
        self._cog._queue_level_role_sync(interaction.guild, lr, previous)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(interaction, "panel_removed_level_roles", count=len(self.values))
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)
        panel = await _build_level_panel(self._cog, self._guild_id, "level_roles", interaction.guild)
        await self.message.edit(view=panel)


class _LvRemoveRoleBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, has_roles: bool, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(
            label=msg(ctx, "panel_btn_remove_role"),
            style=discord.ButtonStyle.red, disabled=not has_roles)

    async def callback(self, interaction: discord.Interaction):
        cfg   = await self._cog._guild_cfg(self._guild_id)
        lr    = cfg.get("level_roles", {})
        guild = interaction.guild
        options = []
        for lvl, rid in sorted(lr.items(), key=lambda x: int(x[0])):
            role  = guild.get_role(int(rid))
            rname = role.name if role else msg(interaction, "panel_role_name", rid=rid)
            options.append(discord.SelectOption(
                label=_fill(msg(interaction, "panel_role_option"),
                            level=lvl, role=rname[:80]),
                value=str(lvl),
                description=msg(interaction, "panel_role_id", rid=rid),
            ))
        if not options:
            return await interaction.response.send_message(
                msg(interaction, "panel_no_level_roles"), ephemeral=True)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(interaction, "panel_select_roles_remove")
            ),
            discord.ui.ActionRow(
                _LvRemoveRoleSelect(
                    self._cog, self._guild_id, options, interaction.message, interaction)
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


class _LvAccentColourModal(discord.ui.Modal):
    def __init__(self, cog, guild_id: int, ctx):
        super().__init__(title=msg(ctx, "panel_accent_modal_title"))
        self._cog      = cog
        self._guild_id = guild_id
        self.hex_colour = discord.ui.TextInput(
            label=msg(ctx, "panel_accent_label"),
            placeholder=msg(ctx, "panel_accent_ph"),
            min_length=1, max_length=7,
        )
        self.add_item(self.hex_colour)

    async def on_submit(self, interaction: discord.Interaction):
        rgb = _parse_colour(self.hex_colour.value)
        if rgb is None:
            return await interaction.response.send_message(
                msg(interaction, "panel_invalid_hex_accent"), ephemeral=True)
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["card_accent"] = list(rgb)
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "card_style", interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvBgTopModal(discord.ui.Modal):
    def __init__(self, cog, guild_id: int, ctx):
        super().__init__(title=msg(ctx, "panel_bg_top_modal_title"))
        self._cog      = cog
        self._guild_id = guild_id
        self.hex_colour = discord.ui.TextInput(
            label=msg(ctx, "panel_bg_top_label"), placeholder="261a16",
            min_length=1, max_length=7,
        )
        self.add_item(self.hex_colour)

    async def on_submit(self, interaction: discord.Interaction):
        rgb = _parse_colour(self.hex_colour.value)
        if rgb is None:
            return await interaction.response.send_message(
                msg(interaction, "panel_invalid_hex_top"), ephemeral=True)
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["card_bg_top"] = list(rgb)
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "card_style", interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvBgBottomModal(discord.ui.Modal):
    def __init__(self, cog, guild_id: int, ctx):
        super().__init__(title=msg(ctx, "panel_bg_bottom_modal_title"))
        self._cog      = cog
        self._guild_id = guild_id
        self.hex_colour = discord.ui.TextInput(
            label=msg(ctx, "panel_bg_bottom_label"), placeholder="120c0a",
            min_length=1, max_length=7,
        )
        self.add_item(self.hex_colour)

    async def on_submit(self, interaction: discord.Interaction):
        rgb = _parse_colour(self.hex_colour.value)
        if rgb is None:
            return await interaction.response.send_message(
                msg(interaction, "panel_invalid_hex_bottom"), ephemeral=True)
        cfg = await self._cog._guild_cfg(self._guild_id)
        cfg["card_bg_bottom"] = list(rgb)
        await self._cog._save_guild_cfg(self._guild_id, cfg)
        panel = await _build_level_panel(self._cog, self._guild_id, "card_style", interaction.guild)
        await interaction.response.edit_message(view=panel)


class _LvEditAccentBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label=msg(ctx, "panel_btn_accent"), style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(
            _LvAccentColourModal(self._cog, self._guild_id, interaction))


class _LvEditBgTopBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label=msg(ctx, "panel_btn_bg_top"), style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(
            _LvBgTopModal(self._cog, self._guild_id, interaction))


class _LvEditBgBottomBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label=msg(ctx, "panel_btn_bg_bottom"), style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(
            _LvBgBottomModal(self._cog, self._guild_id, interaction))


class _LvResetColoursBtn(discord.ui.Button):
    def __init__(self, cog, guild_id: int, ctx):
        self._cog      = cog
        self._guild_id = guild_id
        super().__init__(label=msg(ctx, "panel_btn_reset_colours"), style=discord.ButtonStyle.red)

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

    view      = _LevelPanelView(timeout=300)

    # Card accent for the CV2 container
    accent_rgb = cfg.get("card_accent")
    accent_colour = discord.Colour.from_rgb(*accent_rgb) if accent_rgb else discord.Colour(ACCENT_BRAND)

    container = discord.ui.Container(
        discord.ui.TextDisplay(content=text),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        accent_colour=accent_colour,
    )
    container.add_item(discord.ui.ActionRow(_LvSectionSelect(cog, guild_id, section, guild)))

    if section == "xp":
        container.add_item(discord.ui.ActionRow(
            _LvXPToggleBtn(cog, guild_id, cfg, guild),
            _LvEditXPBtn(cog, guild_id, guild),
        ))

    elif section == "channels":
        container.add_item(discord.ui.ActionRow(
            _LvExcludedChannelsSelect(cog, guild_id, cfg, guild),
        ))
        container.add_item(discord.ui.ActionRow(
            _LvVCToggleBtn(cog, guild_id, cfg, guild),
            _LvRemoveExcludedBtn(cog, guild_id, bool(cfg.get("xp_excluded_channels")), guild),
            _LvClearExcludedBtn(cog, guild_id, bool(cfg.get("xp_excluded_channels")), guild),
        ))

    elif section == "announcements":
        has_custom = bool(cfg.get("level_up_message"))
        container.add_item(discord.ui.ActionRow(
            _LvSetChannelBtn(cog, guild_id, guild),
        ))
        container.add_item(discord.ui.ActionRow(
            _LvEditMessageBtn(cog, guild_id, guild),
            _LvResetMessageBtn(cog, guild_id, has_custom, guild),
        ))

    elif section == "level_roles":
        has_roles = bool(cfg.get("level_roles"))
        container.add_item(discord.ui.ActionRow(
            _LvAddRoleBtn(cog, guild_id, guild),
            _LvRemoveRoleBtn(cog, guild_id, has_roles, guild),
        ))

    elif section == "card_style":
        container.add_item(discord.ui.ActionRow(
            _LvEditAccentBtn(cog, guild_id, guild),
            _LvEditBgTopBtn(cog, guild_id, guild),
        ))
        container.add_item(discord.ui.ActionRow(
            _LvEditBgBottomBtn(cog, guild_id, guild),
            _LvResetColoursBtn(cog, guild_id, guild),
        ))

    view.add_item(container)
    return view


# ───────────────────────────────────────────────────

__all__ = [k for k in list(globals()) if not k.startswith("__")]
