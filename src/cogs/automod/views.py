import discord
from discord.ext import commands
import time
import re
import asyncio
from utils import logging as log
from config.emojis import get_emoji
from utils.i18n import get_lang
from utils.locales import load_locales

# Every invite host Discord hands out: discord.gg short links plus the two
# long forms. discordapp.com was missing, so those invites walked past
# anti-link.
INVITE_REGEX = re.compile(
    r"(discord\.gg/|discord\.com/invite/|discordapp\.com/invite/)",
    re.IGNORECASE,
)

# Used so the panel never pings every whitelisted member in the list.
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
#  BILINGUAL MESSAGE TABLE
# ──────────────────────────────────────────────────

MESSAGES = load_locales("cogs.automod", "views")


# Niko's own emojis, filled into the panel strings by _t(). Declared once here
# instead of being pasted into every translation: MESSAGES carries `{tick}`-style
# placeholders, and the emoji sync rewrites this dictionary in place after a
# re-upload, so these replies never point at a retired id.
EMOJI = {
    "danger":  get_emoji("danger"),
    "warning": get_emoji("warning"),
    "image":   get_emoji("image"),
    "tick":    get_emoji("tick"),
    "cross":   get_emoji("cross"),
}


def _t(lang: str, key: str, **kwargs) -> str:
    """Look up a localised string, filling in Niko's emojis and any kwargs."""
    text = MESSAGES.get(lang, {}).get(key) or MESSAGES["en"].get(key, key)
    return text.format(**EMOJI, **kwargs)


#: Audit-log wording. An entry's *title* stays an English key — it routes the
#: entry to a category channel and the revert buttons match on it — so this
#: table carries the heading a member reads and the body lines next to it.
LOG_MESSAGES = load_locales("cogs.automod", "logs")


def _log_t(lang: str, key: str, **kwargs) -> str:
    """Look up an audit-log string, filling in Niko's emojis and any kwargs."""
    text = LOG_MESSAGES.get(lang, {}).get(key) or LOG_MESSAGES["en"].get(key, key)
    return text.format(**EMOJI, **kwargs)


# ──────────────────────────────────────────────────
#  PERMISSIONS
# ──────────────────────────────────────────────────

def _may_manage(interaction: discord.Interaction) -> bool:
    """Whether the member may edit this server's AutoMod settings.

    Manage Server, like the `/automod` command itself, the `/badwords` panel and
    the dashboard's automod API all use. Every control in this panel used to demand
    Administrator instead, so a Manage Server holder could open it and then be
    refused on every button.
    """
    permissions = getattr(interaction.user, "guild_permissions", None)
    return bool(permissions is not None and getattr(permissions, "manage_guild", False))


async def _deny(interaction: discord.Interaction):
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=_t(get_lang(interaction.guild), "no_permission")),
    ))
    return await interaction.response.send_message(view=view, ephemeral=True)


async def _log(cog, interaction: discord.Interaction, title: str, body: str,
               display_title: str | None = None) -> None:
    """Record an AutoMod settings change in the server's log.

    Discord surfaces used to change these settings silently; only the dashboard
    kept any record at all. ``title`` is the English routing key and
    ``display_title`` the translated heading.
    """
    try:
        await cog.utils().log_action(
            interaction.guild, title, body, moderator=interaction.user,
            display_title=display_title,
        )
    except Exception:  # logging must never break a settings change
        pass


# ──────────────────────────────────────────────────
#  SECTION TEXT BUILDERS
# ──────────────────────────────────────────────────

def _icon(enabled: bool) -> str:
    return get_emoji("tick") if enabled else get_emoji("cross")


def _build_overview_text(cfg: dict, lang: str = "en") -> str:
    am = cfg["automod"]
    an = cfg["antinuke"]
    ar = cfg["antiraid"]
    are = cfg["antiraid_ext"]
    wu = len(cfg.get("whitelist_users", []))
    wr = len(cfg.get("whitelist_roles", []))
    return (
        f"{_t(lang, 'overview_title', emoji=get_emoji('automod'))}\n"
        f"{_t(lang, 'overview_desc')}\n\n"
        f"{get_emoji('message')} {_t(lang, 'section_msgfilter')}\n"
        f"{_icon(am.get('antispam'))} {_t(lang, 'ov_antispam')}  •  "
        f"{_icon(am.get('antilink'))} {_t(lang, 'ov_antilink')}\n"
        f"{_icon(am.get('badwords'))} {_t(lang, 'ov_badwords')}  •  "
        f"{_icon(am.get('massmention'))} {_t(lang, 'ov_massmention')}\n\n"
        f"{_t(lang, 'section_images')}\n"
        f"{_icon(am.get('nsfw_image_filter'))} {_t(lang, 'ov_nsfw')}  •  "
        f"{_icon(am.get('scam_image_filter'))} {_t(lang, 'ov_scam')}\n\n"
        f"{_t(lang, 'section_antinuke')}\n"
        f"{_icon(am.get('antinuke'))} {_t(lang, 'ov_enabled')}  •  "
        f"{_t(lang, 'ov_action')} `{an.get('action', 'strip')}`  •  "
        f"{_t(lang, 'ov_interval')} `{an.get('interval', 10)}s`\n\n"
        f"{_t(lang, 'section_antiraid')}\n"
        f"{_icon(am.get('antiraid'))} {_t(lang, 'ov_enabled')}  •  "
        f"{_t(lang, 'ov_action')} `{ar.get('action', 'kick')}`\n"
        f"{_t(lang, 'ov_raid_line', t=ar.get('join_threshold', 10), w=ar.get('join_interval', 10))}\n\n"
        f"{get_emoji('bot')} {_t(lang, 'section_extraid')}\n"
        f"{_icon(am.get('antiraid_ext'))} {_t(lang, 'ov_interaction_flood')}  •  "
        f"{_icon(are.get('ext_app_detection', True))} {_t(lang, 'ov_user_apps')}\n"
        f"{_t(lang, 'ov_raider')} `{are.get('raider_action', 'kick')}`  •  "
        f"{_t(lang, 'ov_operator')} `{are.get('operator_action', 'notify')}`  •  "
        f"{_t(lang, 'ov_app_abuse')} `{are.get('ext_app_action', 'kick')}`\n\n"
        f"{get_emoji('unlock')} {_t(lang, 'section_whitelist')}\n"
        f"{_t(lang, 'wl_summary', wu=wu, wr=wr)}\n\n"
        f"{_t(lang, 'nav_hint')}"
    )


def _badwords_mode_label(cfg: dict, lang: str = "en") -> str:
    """How the blocked-word filter responds, as translated panel text."""
    action = str(cfg.get("badwords_action", "delete") or "delete").strip().lower()
    key = "badwords_action_censor" if action == "censor" else "badwords_action_delete"
    return _t(lang, key)


def _build_filter_text(cfg: dict, lang: str = "en") -> str:
    am = cfg["automod"]
    return (
        f"### {get_emoji('message')} {_t(lang, 'filter_title')}\n"
        f"{_t(lang, 'filter_desc')}\n\n"
        f"{_icon(am.get('antispam'))} {_t(lang, 'antispam_desc')}\n"
        f"{_t(lang, 'antispam_thresh', msgs=cfg.get('spam_threshold', 6), secs=cfg.get('spam_interval', 7))}\n\n"
        f"{_icon(am.get('antilink'))} {_t(lang, 'antilink_desc')}\n\n"
        f"{_icon(am.get('badwords'))} {_t(lang, 'badwords_desc')}\n"
        f"{_t(lang, 'badwords_mode', mode=_badwords_mode_label(cfg, lang))}\n\n"
        f"{_icon(am.get('massmention'))} {_t(lang, 'massmention_desc')}\n"
        f"{_t(lang, 'massmention_max', max=cfg.get('max_mentions', 5))}"
    )


def _build_image_filter_text(cfg: dict, lang: str = "en") -> str:
    am = cfg["automod"]
    return (
        f"### {get_emoji('message')} {_t(lang, 'images_title')}\n"
        f"{_t(lang, 'images_desc')}\n\n"
        f"{_icon(am.get('nsfw_image_filter'))} {_t(lang, 'nsfwimg_desc')}\n"
        f"{_t(lang, 'nsfwimg_note')}\n\n"
        f"{_icon(am.get('scam_image_filter'))} {_t(lang, 'scamimg_desc')}\n"
        f"{_t(lang, 'scamimg_note')}"
    )


def _build_antinuke_text(cfg: dict, lang: str = "en") -> str:
    am = cfg["automod"]
    an = cfg["antinuke"]
    status = _t(lang, "nuke_status_on") if am.get("antinuke") else _t(lang, "nuke_status_off")
    return (
        f"{_t(lang, 'nuke_title')}\n"
        f"{_t(lang, 'nuke_desc')}\n\n"
        f"{_t(lang, 'nuke_state_line', icon=_icon(am.get('antinuke')), status=status)}\n\n"
        f"{_t(lang, 'nuke_thresholds')}\n"
        f"{get_emoji('ban')} {_t(lang, 'nuke_bans',      t=an.get('ban_threshold', 3))}\n"
        f"{get_emoji('cross')} {_t(lang, 'nuke_kicks',     t=an.get('kick_threshold', 3))}\n"
        f"{get_emoji('trash')} {_t(lang, 'nuke_chandel',   t=an.get('channel_delete_threshold', 3))}\n"
        f"{get_emoji('trash')} {_t(lang, 'nuke_roledel',   t=an.get('role_delete_threshold', 3))}\n"
        f"{get_emoji('plus')} {_t(lang, 'nuke_chancreate',t=an.get('channel_create_threshold', 5))}\n"
        f"{get_emoji('link')} {_t(lang, 'nuke_webhookdel',t=an.get('webhook_delete_threshold', 3))}\n\n"
        f"{_t(lang, 'nuke_interval',  t=an.get('interval', 10))}\n"
        f"{_t(lang, 'nuke_action',    action=an.get('action', 'strip'))}\n"
        f"{_t(lang, 'nuke_actions_hint')}"
    )


def _build_antiraid_text(cfg: dict, lang: str = "en") -> str:
    am = cfg["automod"]
    ar = cfg["antiraid"]
    status = _t(lang, "raid_status_on") if am.get("antiraid") else _t(lang, "raid_status_off")
    new_days = ar.get("new_account_days", 0)
    acct_line = (
        _t(lang, "raid_newacct", days=new_days) if new_days > 0
        else _t(lang, "raid_newacct_off")
    )
    return (
        f"{_t(lang, 'raid_title')}\n"
        f"{_t(lang, 'raid_desc')}\n\n"
        f"{_t(lang, 'raid_state_line', icon=_icon(am.get('antiraid')), status=status)}\n\n"
        f"{_t(lang, 'raid_threshold', t=ar.get('join_threshold', 10))}\n"
        f"{_t(lang, 'raid_window',    t=ar.get('join_interval', 10))}\n"
        f"{_t(lang, 'raid_action',    action=ar.get('action', 'kick'))}\n"
        f"{acct_line}\n\n"
        f"{_t(lang, 'raid_actions_hint')}"
    )


def _build_ext_raid_text(cfg: dict, lang: str = "en") -> str:
    am = cfg["automod"]
    are = cfg["antiraid_ext"]
    return (
        f"### {get_emoji('bot')} {_t(lang, 'ext_title')}\n\n"
        f"{_t(lang, 'ext_mode1')}\n"
        f"{_t(lang, 'ext_mode1_desc')}\n\n"
        f"{_t(lang, 'ext_enabled_line', icon=_icon(am.get('antiraid_ext')))}\n"
        f"{_t(lang, 'ext_threshold', t=are.get('interaction_threshold', 5), w=are.get('interaction_window', 30))}\n"
        f"{_t(lang, 'ext_newmember', s=are.get('join_age_limit', 120))}\n"
        f"{_t(lang, 'ext_raiderop', ra=are.get('raider_action', 'kick'), oa=are.get('operator_action', 'notify'))}\n\n"
        f"{_t(lang, 'ext_mode2')}\n"
        f"{_t(lang, 'ext_mode2_desc')}\n\n"
        f"{_t(lang, 'ext_enabled_line', icon=_icon(are.get('ext_app_detection', True)))}\n"
        f"{_t(lang, 'ext_app_threshold', t=are.get('ext_app_threshold', 3), w=are.get('ext_app_window', 15))}\n"
        f"{_t(lang, 'ext_app_action', a=are.get('ext_app_action', 'kick'))}\n\n"
        f"{_t(lang, 'ext_hint')}"
    )


#: The whitelist itself is uncapped; the panel renders a page of it so the
#: container can never exceed Discord's per-component text limit.
_WL_RENDER_LIMIT = 40


def _wl_lines(entries: list, resolve, lang: str) -> str:
    """One mention per line, with a count for the entries that did not fit."""
    shown = entries[:_WL_RENDER_LIMIT]
    lines = [f"・ {resolve(entry)}" for entry in shown]
    if len(entries) > len(shown):
        lines.append(_t(lang, "wl_and_more", count=len(entries) - len(shown)))
    return chr(10).join(lines) or _t(lang, "wl_none")


def _build_whitelist_text(cfg: dict, guild: discord.Guild, lang: str = "en") -> str:
    user_ids = cfg.get("whitelist_users", [])
    role_ids = cfg.get("whitelist_roles", [])

    user_lines = _wl_lines(
        user_ids, lambda uid: guild.get_member(uid) or discord.Object(uid), lang)
    role_lines = _wl_lines(
        role_ids, lambda rid: guild.get_role(rid) or discord.Object(rid), lang)

    return (
        f"### {get_emoji('unlock')} {_t(lang, 'wl_title')}\n"
        f"{_t(lang, 'wl_desc')}\n\n"
        f"{_t(lang, 'wl_users_hdr')}\n"
        f"{user_lines}\n\n"
        f"{_t(lang, 'wl_roles_hdr')}\n"
        f"{role_lines}\n\n"
        f"{_t(lang, 'wl_hint')}"
    )


def _section_text(cfg: dict, section: str, guild: discord.Guild = None, lang: str = "en") -> str:
    if section == "filter":
        return _build_filter_text(cfg, lang)
    if section == "image_filter":
        return _build_image_filter_text(cfg, lang)
    if section == "antinuke":
        return _build_antinuke_text(cfg, lang)
    if section == "antiraid":
        return _build_antiraid_text(cfg, lang)
    if section == "ext_raid":
        return _build_ext_raid_text(cfg, lang)
    if section == "whitelist":
        return _build_whitelist_text(cfg, guild, lang)
    return _build_overview_text(cfg, lang)


# ──────────────────────────────────────────────────────────────────────────────
#  OWNER DM — ANTI-NUKE  (cv2 LayoutView)
# ──────────────────────────────────────────────────────────────────────────────

#: The emoji that heads each tracked action in the owner DM. The wording
#: itself lives in locales/views (``nuke_label_*``), so the alert reads in the
#: server's language instead of carrying its own inline translations.
_NUKE_ACTION_EMOJI = {
    "ban":            "ban",
    "kick":           "cross",
    "channel_delete": "trash",
    "role_delete":    "trash",
    "channel_create": "plus",
    "webhook_delete": "link",
}


def _build_nuke_dm_view(
    guild:       discord.Guild,
    offender:    discord.User,
    action_key:  str,
    threshold:   int,
    interval:    int,
    nuke_action: str,
    lang:        str,
) -> discord.ui.LayoutView:
    """
    Build a cv2 LayoutView for the single owner DM sent when anti-nuke fires.
    Red-accented container with title, details, and a timestamp footer.
    """
    ts = int(time.time())

    emoji_key = _NUKE_ACTION_EMOJI.get(action_key)
    trigger = f"{get_emoji(emoji_key)} {_t(lang, f'nuke_label_{action_key}')}" if emoji_key \
        else _t(lang, f"nuke_label_{action_key}")
    taken = _t(lang, f"nuke_taken_{nuke_action}") if nuke_action in ("strip", "kick", "ban") \
        else nuke_action
    title = _t(lang, "nuke_dm_title")
    body = _t(
        lang, "nuke_dm_body",
        server=guild.name,
        offender=offender,
        id=offender.id,
        trigger=trigger,
        count=threshold,
        interval=interval,
        action=taken,
    )
    footer = _t(lang, "nuke_dm_footer", ts=ts)

    view = discord.ui.LayoutView()
    view.add_item(
        discord.ui.Container(
            discord.ui.TextDisplay(content=title),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=body),
            discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=footer),
            accent_colour=discord.Colour(0xED4245),
        )
    )
    return view


# ──────────────────────────────────────────────────
#  INTERACTIVE COMPONENTS
# ──────────────────────────────────────────────────

class SectionSelect(discord.ui.Select):
    def __init__(self, automod_cog, guild_id: int, current_section: str, lang: str):
        self._cog = automod_cog
        self._guild_id = guild_id
        options = [
            discord.SelectOption(
                label=_t(lang, "sec_overview"),
                value="overview",
                emoji=get_emoji("automod"),
                description=_t(lang, "sec_overview_desc"),
                default=(current_section == "overview")
            ),
            discord.SelectOption(
                label=_t(lang, "sec_filter"),
                value="filter",
                emoji=get_emoji("message"),
                description=_t(lang, "sec_filter_desc"),
                default=(current_section == "filter")
            ),
            discord.SelectOption(
                label=_t(lang, "sec_images"),
                value="image_filter",
                emoji=get_emoji("image"),
                description=_t(lang, "sec_images_desc"),
                default=(current_section == "image_filter")
            ),
            discord.SelectOption(
                label=_t(lang, "sec_nuke"),
                value="antinuke",
                emoji=get_emoji("danger"),
                description=_t(lang, "sec_nuke_desc"),
                default=(current_section == "antinuke")
            ),
            discord.SelectOption(
                label=_t(lang, "sec_raid"),
                value="antiraid",
                emoji=get_emoji("warning"),
                description=_t(lang, "sec_raid_desc"),
                default=(current_section == "antiraid")
            ),
            discord.SelectOption(
                label=_t(lang, "sec_ext"),
                value="ext_raid",
                emoji=get_emoji("bot"),
                description=_t(lang, "sec_ext_desc"),
                default=(current_section == "ext_raid")
            ),
            discord.SelectOption(
                label=_t(lang, "sec_whitelist"),
                value="whitelist",
                emoji=get_emoji("unlock"),
                description=_t(lang, "sec_whitelist_desc"),
                default=(current_section == "whitelist")
            ),
        ]
        super().__init__(placeholder=_t(lang, "sec_nav"), options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        new_panel = _build_panel(self._cog, self._guild_id, self.values[0], interaction.guild)
        await interaction.response.edit_message(view=new_panel, allowed_mentions=ALLOWED_MENTIONS)




class ToggleButton(discord.ui.Button):
    def __init__(self, label: str, key: str, automod_cog, guild_id: int, section: str):
        self._cog = automod_cog
        self._guild_id = guild_id
        self._key = key
        self._section = section
        self._label = label
        cfg = automod_cog.utils().get_guild_config(guild_id)
        enabled = cfg["automod"].get(key, False)
        super().__init__(
            label=f"{label}",
            style=discord.ButtonStyle.green if enabled else discord.ButtonStyle.red,
            emoji=_icon(enabled)
        )

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        turning_on = not cfg["automod"].get(self._key, False)
        # The dashboard already refuses to switch NSFW image filtering on
        # without premium, because the fal.ai scan is billed per image. The
        # panel used to let anyone enable it here and the config then sat
        # inert, so the two surfaces disagreed about what was configured.
        if turning_on and self._key == "nsfw_image_filter":
            if not await self._cog._premium_active(self._guild_id):
                lang = get_lang(interaction.guild)
                view = discord.ui.LayoutView()
                view.add_item(discord.ui.Container(
                    discord.ui.TextDisplay(content=_t(lang, "nsfw_premium")),
                ))
                return await interaction.response.send_message(view=view, ephemeral=True)
        cfg["automod"][self._key] = turning_on
        utils.save_config()
        lang = get_lang(interaction.guild)
        await _log(
            self._cog, interaction, "AutoMod Settings",
            _log_t(
                lang, "settings_toggled",
                label=self._label,
                state=_log_t(lang, "state_on" if turning_on else "state_off"),
            ),
            _log_t(lang, "title_settings"),
        )
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
        self._label = label
        cfg = automod_cog.utils().get_guild_config(guild_id)
        enabled = cfg.get(sub_cfg_key, {}).get(field, True)
        super().__init__(
            label=f"{label}",
            style=discord.ButtonStyle.green if enabled else discord.ButtonStyle.red,
            emoji=_icon(enabled)
        )

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        enabled = not cfg[self._sub_cfg].get(self._field, True)
        cfg[self._sub_cfg][self._field] = enabled
        utils.save_config()
        lang = get_lang(interaction.guild)
        await _log(
            self._cog, interaction, "AutoMod Settings",
            _log_t(
                lang, "settings_toggled",
                label=self._label,
                state=_log_t(lang, "state_on" if enabled else "state_off"),
            ),
            _log_t(lang, "title_settings"),
        )
        new_panel = _build_panel(self._cog, self._guild_id, self._section, interaction.guild)
        await interaction.response.edit_message(view=new_panel, allowed_mentions=ALLOWED_MENTIONS)


class EditThresholdsButton(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int, section: str, label: str = None, lang: str = "en"):
        self._cog = automod_cog
        self._guild_id = guild_id
        self._section = section
        super().__init__(
            label=label or _t(lang, "btn_edit_thresholds"),
            style=discord.ButtonStyle.blurple, emoji=get_emoji("settings"),
        )

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        modal = _build_threshold_modal(
            cfg, self._cog, self._guild_id, self._section, get_lang(interaction.guild))
        await interaction.response.send_modal(modal)


class EditExtAppButton(discord.ui.Button):
    """Opens the modal for user-installed app detection settings."""
    def __init__(self, automod_cog, guild_id: int, lang: str = "en"):
        self._cog = automod_cog
        self._guild_id = guild_id
        super().__init__(
            label=_t(lang, "btn_edit_app_detection"),
            style=discord.ButtonStyle.blurple,
            emoji=get_emoji("settings")
        )

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        await interaction.response.send_modal(
            ExtAppThresholdModal(self._cog, self._guild_id, cfg, get_lang(interaction.guild))
        )


# ──────────────────────────────────────────────────
#  THRESHOLD MODALS
# ──────────────────────────────────────────────────

class FilterThresholdModal(discord.ui.Modal, title="Message Filter Thresholds"):
    spam_msgs = discord.ui.TextInput(label="Spam: max messages", placeholder="e.g. 6")
    spam_secs = discord.ui.TextInput(label="Spam: within seconds", placeholder="e.g. 7")
    max_ment = discord.ui.TextInput(label="Mass Mention: max mentions", placeholder="e.g. 5")

    def __init__(self, automod_cog, guild_id: int, cfg: dict, lang: str = "en"):
        super().__init__()
        self.title = _t(lang, "th_filter_title")
        self.spam_msgs.label = _t(lang, "th_spam_msgs")
        self.spam_msgs.placeholder = _t(lang, "th_example", value=6)
        self.spam_secs.label = _t(lang, "th_spam_secs")
        self.spam_secs.placeholder = _t(lang, "th_example", value=7)
        self.max_ment.label = _t(lang, "th_max_mentions")
        self.max_ment.placeholder = _t(lang, "th_example", value=5)
        self._cog = automod_cog
        self._guild_id = guild_id
        self.spam_msgs.default = str(cfg.get("spam_threshold", 6))
        self.spam_secs.default = str(cfg.get("spam_interval", 7))
        self.max_ment.default = str(cfg.get("max_mentions", 5))

    async def on_submit(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["spam_threshold"] = max(1, int(self.spam_msgs.value))
            cfg["spam_interval"] = max(1, int(self.spam_secs.value))
            cfg["max_mentions"] = max(1, int(self.max_ment.value))
            utils.save_config()
            await _log(
                self._cog, interaction, "AutoMod Settings",
                _log_t(
                    lang, "settings_filter",
                    msgs=cfg["spam_threshold"],
                    secs=cfg["spam_interval"],
                    max=cfg["max_mentions"],
                ),
                _log_t(lang, "title_settings"),
            )
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "filter", interaction.guild))
        except ValueError:
            await interaction.response.send_message(_t(lang, "invalid_numbers"), ephemeral=True)


class AntiNukeThresholdModal(discord.ui.Modal, title="Anti-Nuke Thresholds"):
    ban_t = discord.ui.TextInput(label="Ban threshold", placeholder="e.g. 3")
    kick_t = discord.ui.TextInput(label="Kick threshold", placeholder="e.g. 3")
    chan_t = discord.ui.TextInput(label="Channel delete threshold", placeholder="e.g. 3")
    role_t = discord.ui.TextInput(label="Role delete threshold", placeholder="e.g. 3")
    interval = discord.ui.TextInput(label="Interval (seconds)", placeholder="e.g. 10")

    def __init__(self, automod_cog, guild_id: int, cfg: dict, lang: str = "en"):
        super().__init__()
        self.title = _t(lang, "th_nuke_title")
        self.ban_t.label = _t(lang, "th_ban")
        self.ban_t.placeholder = _t(lang, "th_example", value=3)
        self.kick_t.label = _t(lang, "th_kick")
        self.kick_t.placeholder = _t(lang, "th_example", value=3)
        self.chan_t.label = _t(lang, "th_chandel")
        self.chan_t.placeholder = _t(lang, "th_example", value=3)
        self.role_t.label = _t(lang, "th_roledel")
        self.role_t.placeholder = _t(lang, "th_example", value=3)
        self.interval.label = _t(lang, "th_interval")
        self.interval.placeholder = _t(lang, "th_example", value=10)
        self._cog = automod_cog
        self._guild_id = guild_id
        an = cfg.get("antinuke", {})
        self.ban_t.default = str(an.get("ban_threshold", 3))
        self.kick_t.default = str(an.get("kick_threshold", 3))
        self.chan_t.default = str(an.get("channel_delete_threshold", 3))
        self.role_t.default = str(an.get("role_delete_threshold", 3))
        self.interval.default = str(an.get("interval", 10))

    async def on_submit(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antinuke"]["ban_threshold"] = max(1, int(self.ban_t.value))
            cfg["antinuke"]["kick_threshold"] = max(1, int(self.kick_t.value))
            cfg["antinuke"]["channel_delete_threshold"] = max(1, int(self.chan_t.value))
            cfg["antinuke"]["role_delete_threshold"] = max(1, int(self.role_t.value))
            cfg["antinuke"]["interval"] = max(1, int(self.interval.value))
            utils.save_config()
            an = cfg["antinuke"]
            await _log(
                self._cog, interaction, "AutoMod Settings",
                _log_t(
                    lang, "settings_nuke",
                    ban=an["ban_threshold"],
                    kick=an["kick_threshold"],
                    chandel=an["channel_delete_threshold"],
                    roledel=an["role_delete_threshold"],
                    interval=an["interval"],
                ),
                _log_t(lang, "title_settings"),
            )
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "antinuke", interaction.guild))
        except ValueError:
            await interaction.response.send_message(_t(lang, "invalid_numbers"), ephemeral=True)


class AntiNukeActionModal(discord.ui.Modal, title="Anti-Nuke Response Action"):
    action = discord.ui.TextInput(label="Action (strip / kick / ban)", placeholder="strip", max_length=10)

    def __init__(self, automod_cog, guild_id: int, cfg: dict, lang: str = "en"):
        super().__init__()
        self.title = _t(lang, "th_nuke_action_title")
        self.action.label = _t(lang, "th_nuke_action_field")
        self._cog = automod_cog
        self._guild_id = guild_id
        self.action.default = cfg.get("antinuke", {}).get("action", "strip")

    async def on_submit(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        val = self.action.value.lower().strip()
        lang = get_lang(interaction.guild)
        if val not in ("strip", "kick", "ban"):
            return await interaction.response.send_message(
                _t(lang, "invalid_nuke_action"), ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        cfg["antinuke"]["action"] = val
        utils.save_config()
        await _log(
            self._cog, interaction, "AutoMod Settings",
            _log_t(lang, "settings_nuke_action", action=val),
            _log_t(lang, "title_settings"),
        )
        await interaction.response.edit_message(
            view=_build_panel(self._cog, self._guild_id, "antinuke", interaction.guild))


class AntiRaidThresholdModal(discord.ui.Modal, title="Anti-Raid Settings"):
    join_t = discord.ui.TextInput(label="Join threshold (members)", placeholder="e.g. 10")
    join_i = discord.ui.TextInput(label="Time window (seconds)", placeholder="e.g. 10")
    action = discord.ui.TextInput(
        label="Action: kick/ban/softban/lockdown",
        placeholder="kick", max_length=10)
    new_days  = discord.ui.TextInput(
        label="New account filter (days, 0 = off)",
        placeholder="e.g. 7",
        required=False)
    slow_secs = discord.ui.TextInput(
        label="Slowmode seconds",
        placeholder="e.g. 30", required=False)

    def __init__(self, automod_cog, guild_id: int, cfg: dict, lang: str = "en"):
        super().__init__()
        self.title = _t(lang, "th_raid_title")
        self.join_t.label = _t(lang, "th_join")
        self.join_t.placeholder = _t(lang, "th_example", value=10)
        self.join_i.label = _t(lang, "th_window")
        self.join_i.placeholder = _t(lang, "th_example", value=10)
        self.action.label = _t(lang, "th_raid_action")
        self.new_days.label = _t(lang, "th_newacct")
        self.new_days.placeholder = _t(lang, "th_example", value=7)
        self.slow_secs.label = _t(lang, "th_slowmode")
        self.slow_secs.placeholder = _t(lang, "th_example", value=30)
        self._cog = automod_cog
        self._guild_id = guild_id
        ar = cfg.get("antiraid", {})
        self.join_t.default    = str(ar.get("join_threshold", 10))
        self.join_i.default    = str(ar.get("join_interval", 10))
        self.action.default    = ar.get("action", "kick")
        self.new_days.default  = str(ar.get("new_account_days", 0))
        self.slow_secs.default = str(ar.get("lockdown_slowmode", 30))

    async def on_submit(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        val = self.action.value.lower().strip()
        lang = get_lang(interaction.guild)
        if val not in ("kick", "ban", "softban", "slowmode", "lockdown"):
            return await interaction.response.send_message(
                _t(lang, "invalid_raid_action"), ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antiraid"]["join_threshold"]   = max(1, int(self.join_t.value))
            cfg["antiraid"]["join_interval"]    = max(1, int(self.join_i.value))
            cfg["antiraid"]["action"]           = val
            cfg["antiraid"]["new_account_days"] = max(0, int(self.new_days.value or 0))
            cfg["antiraid"]["lockdown_slowmode"]= max(1, int(self.slow_secs.value or 30))
            utils.save_config()
            ar = cfg["antiraid"]
            await _log(
                self._cog, interaction, "AutoMod Settings",
                _log_t(
                    lang, "settings_raid",
                    joins=ar["join_threshold"],
                    interval=ar["join_interval"],
                    action=ar["action"],
                    days=ar["new_account_days"],
                ),
                _log_t(lang, "title_settings"),
            )
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "antiraid", interaction.guild))
        except ValueError:
            await interaction.response.send_message(_t(lang, "invalid_numbers"), ephemeral=True)


class ExtRaidThresholdModal(discord.ui.Modal, title="Ext. Raid — Interaction Flood Settings"):
    int_threshold = discord.ui.TextInput(label="Interaction threshold (unique users)", placeholder="e.g. 5")
    int_window = discord.ui.TextInput(label="Detection window (seconds)", placeholder="e.g. 30")
    join_age = discord.ui.TextInput(label="Max member age to count (seconds)", placeholder="e.g. 120")
    raider_act = discord.ui.TextInput(label="Raider action (kick / ban)", placeholder="kick", max_length=10)
    operator_act = discord.ui.TextInput(label="Operator action (notify / kick / ban)", placeholder="notify", max_length=10)

    def __init__(self, automod_cog, guild_id: int, cfg: dict, lang: str = "en"):
        super().__init__()
        self.title = _t(lang, "th_ext_title")
        self.int_threshold.label = _t(lang, "th_interactions")
        self.int_threshold.placeholder = _t(lang, "th_example", value=5)
        self.int_window.label = _t(lang, "th_detect_window")
        self.int_window.placeholder = _t(lang, "th_example", value=30)
        self.join_age.label = _t(lang, "th_join_age")
        self.join_age.placeholder = _t(lang, "th_example", value=120)
        self.raider_act.label = _t(lang, "th_raider_action")
        self.operator_act.label = _t(lang, "th_operator_action")
        self._cog = automod_cog
        self._guild_id = guild_id
        are = cfg.get("antiraid_ext", {})
        self.int_threshold.default = str(are.get("interaction_threshold", 5))
        self.int_window.default = str(are.get("interaction_window", 30))
        self.join_age.default = str(are.get("join_age_limit", 120))
        self.raider_act.default = are.get("raider_action", "kick")
        self.operator_act.default = are.get("operator_action", "notify")

    async def on_submit(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        raider_val = self.raider_act.value.lower().strip()
        operator_val = self.operator_act.value.lower().strip()
        lang = get_lang(interaction.guild)
        if raider_val not in ("kick", "ban"):
            return await interaction.response.send_message(
                _t(lang, "invalid_raider_action"), ephemeral=True)
        if operator_val not in ("notify", "kick", "ban"):
            return await interaction.response.send_message(
                _t(lang, "invalid_operator_action"), ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antiraid_ext"]["interaction_threshold"] = max(1, int(self.int_threshold.value))
            cfg["antiraid_ext"]["interaction_window"] = max(5, int(self.int_window.value))
            cfg["antiraid_ext"]["join_age_limit"] = max(10, int(self.join_age.value))
            cfg["antiraid_ext"]["raider_action"] = raider_val
            cfg["antiraid_ext"]["operator_action"] = operator_val
            utils.save_config()
            are = cfg["antiraid_ext"]
            await _log(
                self._cog, interaction, "AutoMod Settings",
                _log_t(
                    lang, "settings_flood",
                    threshold=are["interaction_threshold"],
                    window=are["interaction_window"],
                    raider=are["raider_action"],
                    operator=are["operator_action"],
                ),
                _log_t(lang, "title_settings"),
            )
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "ext_raid", interaction.guild))
        except ValueError:
            await interaction.response.send_message(_t(lang, "invalid_numbers"), ephemeral=True)


class ExtAppThresholdModal(discord.ui.Modal, title="Ext. Raid — User-Installed App Settings"):
    threshold = discord.ui.TextInput(label="Commands per user before action", placeholder="e.g. 3")
    window = discord.ui.TextInput(label="Time window (seconds)", placeholder="e.g. 15")
    action = discord.ui.TextInput(label="Action (kick / ban / warn / log)", placeholder="kick", max_length=10)

    def __init__(self, automod_cog, guild_id: int, cfg: dict, lang: str = "en"):
        super().__init__()
        self.title = _t(lang, "th_extapp_title")
        self.threshold.label = _t(lang, "th_app_threshold")
        self.threshold.placeholder = _t(lang, "th_example", value=3)
        self.window.label = _t(lang, "th_window")
        self.window.placeholder = _t(lang, "th_example", value=15)
        self.action.label = _t(lang, "th_app_action")
        self._cog = automod_cog
        self._guild_id = guild_id
        are = cfg.get("antiraid_ext", {})
        self.threshold.default = str(are.get("ext_app_threshold", 3))
        self.window.default = str(are.get("ext_app_window", 15))
        self.action.default = are.get("ext_app_action", "kick")

    async def on_submit(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        val = self.action.value.lower().strip()
        lang = get_lang(interaction.guild)
        if val not in ("kick", "ban", "warn", "log"):
            return await interaction.response.send_message(
                _t(lang, "invalid_ext_action"), ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antiraid_ext"]["ext_app_threshold"] = max(1, int(self.threshold.value))
            cfg["antiraid_ext"]["ext_app_window"] = max(5, int(self.window.value))
            cfg["antiraid_ext"]["ext_app_action"] = val
            utils.save_config()
            are = cfg["antiraid_ext"]
            await _log(
                self._cog, interaction, "AutoMod Settings",
                _log_t(
                    lang, "settings_app",
                    threshold=are["ext_app_threshold"],
                    window=are["ext_app_window"],
                    action=are["ext_app_action"],
                ),
                _log_t(lang, "title_settings"),
            )
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "ext_raid", interaction.guild))
        except ValueError:
            await interaction.response.send_message(_t(lang, "invalid_numbers"), ephemeral=True)


def _build_threshold_modal(cfg, automod_cog, guild_id, section, lang: str = "en"):
    if section == "antinuke":
        return AntiNukeThresholdModal(automod_cog, guild_id, cfg, lang)
    if section == "antiraid":
        return AntiRaidThresholdModal(automod_cog, guild_id, cfg, lang)
    if section == "ext_raid":
        return ExtRaidThresholdModal(automod_cog, guild_id, cfg, lang)
    return FilterThresholdModal(automod_cog, guild_id, cfg, lang)


class AntiNukeExtThresholdModal(discord.ui.Modal, title="Anti-Nuke — Extended Thresholds"):
    chan_create = discord.ui.TextInput(label="Channel create threshold", placeholder="e.g. 5")
    webhook_del = discord.ui.TextInput(label="Webhook delete threshold", placeholder="e.g. 3")

    def __init__(self, automod_cog, guild_id: int, cfg: dict, lang: str = "en"):
        super().__init__()
        self.title = _t(lang, "th_nuke_ext_title")
        self.chan_create.label = _t(lang, "th_chan_create")
        self.chan_create.placeholder = _t(lang, "th_example", value=5)
        self.webhook_del.label = _t(lang, "th_webhook_del")
        self.webhook_del.placeholder = _t(lang, "th_example", value=3)
        self._cog = automod_cog
        self._guild_id = guild_id
        an = cfg.get("antinuke", {})
        self.chan_create.default = str(an.get("channel_create_threshold", 5))
        self.webhook_del.default = str(an.get("webhook_delete_threshold", 3))

    async def on_submit(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antinuke"]["channel_create_threshold"] = max(1, int(self.chan_create.value))
            cfg["antinuke"]["webhook_delete_threshold"] = max(1, int(self.webhook_del.value))
            utils.save_config()
            an = cfg["antinuke"]
            await _log(
                self._cog, interaction, "AutoMod Settings",
                _log_t(
                    lang, "settings_nuke_ext",
                    create=an["channel_create_threshold"],
                    delete=an["webhook_delete_threshold"],
                ),
                _log_t(lang, "title_settings"),
            )
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "antinuke", interaction.guild))
        except ValueError:
            await interaction.response.send_message(_t(lang, "invalid_numbers"), ephemeral=True)


class _NukeExtThresholdButton(discord.ui.Button):
    """Opens extended nuke threshold modal (channel_create, webhook_delete)."""
    def __init__(self, automod_cog, guild_id: int, lang: str = "en"):
        super().__init__(label=_t(lang, "btn_ext_thresholds"), style=discord.ButtonStyle.gray,
                         emoji=get_emoji("settings"))
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        await interaction.response.send_modal(
            AntiNukeExtThresholdModal(
                self._cog, self._guild_id, cfg, get_lang(interaction.guild))
        )


# ──────────────────────────────────────────────────
#  WHITELIST EPHEMERAL SELECTS & VIEWS
# ──────────────────────────────────────────────────

#: Discord allows 25 options (and 25 values) in one select. The whitelist is
#: uncapped, so a long list has to be shown in part rather than crashing the
#: picker with a ValueError.
_WL_MAX_OPTIONS = 25


class _WLUserSelect(discord.ui.UserSelect):
    """Ephemeral select — add members to whitelist."""
    def __init__(self, automod_cog, guild_id: int, message, lang: str = "en"):
        super().__init__(
            placeholder=_t(lang, "wl_add_user_ph"),
            min_values=1, max_values=10,
        )
        self._cog = automod_cog
        self._guild_id = guild_id
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        for user in self.values:
            utils.add_whitelist_user(self._guild_id, user.id)
        utils.save_config()
        names = " ".join(u.mention for u in self.values)
        await _log(
            self._cog, interaction, "AutoMod Whitelist",
            _log_t(lang, "wl_added", names=names),
            _log_t(lang, "title_whitelist"),
        )
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(lang, "wl_added_users", emoji=get_emoji("tick"), names=names)
            )
        )
        view.add_item(container)
        await interaction.response.edit_message(
            view=view, allowed_mentions=ALLOWED_MENTIONS
        )
        await self.message.edit(
            view=_build_panel(self._cog, self._guild_id, "whitelist", interaction.guild)
        )


class _WLRoleSelect(discord.ui.RoleSelect):
    """Ephemeral select — add roles to whitelist."""
    def __init__(self, automod_cog, guild_id: int, message, lang: str = "en"):
        super().__init__(
            placeholder=_t(lang, "wl_add_role_ph"),
            min_values=1, max_values=10,
        )
        self._cog = automod_cog
        self._guild_id = guild_id
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        for role in self.values:
            utils.add_whitelist_role(self._guild_id, role.id)
        utils.save_config()
        names = " ".join(r.mention for r in self.values)
        await _log(
            self._cog, interaction, "AutoMod Whitelist",
            _log_t(lang, "wl_added", names=names),
            _log_t(lang, "title_whitelist"),
        )
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(lang, "wl_added_roles", emoji=get_emoji("tick"), names=names)
            )
        )
        view.add_item(container)
        await interaction.response.edit_message(
            view=view, allowed_mentions=ALLOWED_MENTIONS
        )
        await self.message.edit(
            view=_build_panel(self._cog, self._guild_id, "whitelist", interaction.guild)
        )


class _WLUserRemoveSelect(discord.ui.Select):
    """Ephemeral select — remove users from whitelist."""
    def __init__(self, automod_cog, guild_id: int, options: list, message, lang: str = "en"):
        super().__init__(
            placeholder=_t(lang, "wl_remove_user_ph"),
            min_values=1, max_values=min(len(options), _WL_MAX_OPTIONS),
            options=options[:_WL_MAX_OPTIONS],
        )
        self._cog = automod_cog
        self._guild_id = guild_id
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        for uid_str in self.values:
            utils.remove_whitelist_user(self._guild_id, int(uid_str))
        utils.save_config()
        await _log(
            self._cog, interaction, "AutoMod Whitelist",
            _log_t(lang, "wl_removed_users", count=len(self.values)),
            _log_t(lang, "title_whitelist"),
        )
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(lang, "wl_removed_users", emoji=get_emoji("tick"), count=len(self.values))
            )
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)
        await self.message.edit(
            view=_build_panel(self._cog, self._guild_id, "whitelist", interaction.guild)
        )


class _WLRoleRemoveSelect(discord.ui.Select):
    """Ephemeral select — remove roles from whitelist."""
    def __init__(self, automod_cog, guild_id: int, options: list, message, lang: str = "en"):
        super().__init__(
            placeholder=_t(lang, "wl_remove_role_ph"),
            min_values=1, max_values=min(len(options), _WL_MAX_OPTIONS),
            options=options[:_WL_MAX_OPTIONS],
        )
        self._cog = automod_cog
        self._guild_id = guild_id
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        for rid_str in self.values:
            utils.remove_whitelist_role(self._guild_id, int(rid_str))
        utils.save_config()
        await _log(
            self._cog, interaction, "AutoMod Whitelist",
            _log_t(lang, "wl_removed_roles", count=len(self.values)),
            _log_t(lang, "title_whitelist"),
        )
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(lang, "wl_removed_roles", emoji=get_emoji("tick"), count=len(self.values))
            )
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)
        await self.message.edit(
            view=_build_panel(self._cog, self._guild_id, "whitelist", interaction.guild)
        )


class _WLAddUserBtn(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int, lang: str = "en"):
        super().__init__(
            label=_t(lang, "btn_add_user"),
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("plus")
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        lang = get_lang(interaction.guild)
        message = interaction.message
        view = discord.ui.LayoutView(timeout=60)
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(lang, "wl_add_user_prompt")
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _WLUserSelect(self._cog, self._guild_id, message, lang)
            )
        )
        view.add_item(container)
        await interaction.response.send_message(
            view=view, ephemeral=True,
        )


class _WLAddRoleBtn(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int, lang: str = "en"):
        super().__init__(
            label=_t(lang, "btn_add_role"),
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("plus")
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        lang = get_lang(interaction.guild)
        message = interaction.message
        view = discord.ui.LayoutView(timeout=60)
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(lang, "wl_add_role_prompt")
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _WLRoleSelect(self._cog, self._guild_id, message, lang)
            )
        )
        view.add_item(container)
        await interaction.response.send_message(
            view=view, ephemeral=True,
        )


class _WLRemoveUserBtn(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int, has_users: bool, lang: str = "en"):
        super().__init__(
            label=_t(lang, "btn_remove_user"),
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("trash"),
            disabled=not has_users,
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        user_ids = cfg.get("whitelist_users", [])
        options = []
        for uid in user_ids:
            member = interaction.guild.get_member(uid)
            label = member.display_name if member else _t(lang, "wl_unknown_user", id=uid)
            options.append(discord.SelectOption(
                label=label[:100], value=str(uid),
                description=f"ID: {uid}",
            ))
        if not options:
            return await interaction.response.send_message(
                _t(lang, "wl_no_users"), ephemeral=True,
            )
        prompt = _t(lang, "wl_remove_user_prompt")
        if len(options) > _WL_MAX_OPTIONS:
            prompt += f"\n{_t(lang, 'wl_more')}"
        message = interaction.message
        view = discord.ui.LayoutView(timeout=60)
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=prompt),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _WLUserRemoveSelect(self._cog, self._guild_id, options, message, lang)
            )
        )
        view.add_item(container)
        await interaction.response.send_message(
            view=view, ephemeral=True,
        )


class _WLRemoveRoleBtn(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int, has_roles: bool, lang: str = "en"):
        super().__init__(
            label=_t(lang, "btn_remove_role"),
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("trash"),
            disabled=not has_roles,
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        role_ids = cfg.get("whitelist_roles", [])
        options = []
        for rid in role_ids:
            role = interaction.guild.get_role(rid)
            label = role.name if role else _t(lang, "wl_unknown_role", id=rid)
            options.append(discord.SelectOption(
                label=label[:100], value=str(rid),
                description=f"ID: {rid}",
            ))
        if not options:
            return await interaction.response.send_message(
                _t(lang, "wl_no_roles"), ephemeral=True,
            )
        prompt = _t(lang, "wl_remove_role_prompt")
        if len(options) > _WL_MAX_OPTIONS:
            prompt += f"\n{_t(lang, 'wl_more')}"
        message = interaction.message
        view = discord.ui.LayoutView(timeout=60)
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=prompt),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _WLRoleRemoveSelect(self._cog, self._guild_id, options, message, lang)
            )
        )
        view.add_item(container)
        await interaction.response.send_message(
            view=view, ephemeral=True,
        )


# ──────────────────────────────────────────────────
#  PANEL BUILDER
# ──────────────────────────────────────────────────

def _build_panel(self, guild_id: int, section: str = "overview", guild: discord.Guild = None) -> discord.ui.LayoutView:
    utils = self.utils()
    cfg = utils.get_guild_config(guild_id)
    lang = get_lang(guild)

    view = discord.ui.LayoutView(timeout=300)
    text = _section_text(cfg, section, guild, lang)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=text),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
    )
    container.add_item(discord.ui.ActionRow(SectionSelect(self, guild_id, section, lang)))

    if section == "filter":
        container.add_item(discord.ui.ActionRow(
            ToggleButton(_t(lang, "btn_anti_spam"), "antispam", self, guild_id, section),
            ToggleButton(_t(lang, "btn_anti_link"), "antilink", self, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            ToggleButton(_t(lang, "btn_bad_words"), "badwords", self, guild_id, section),
            ToggleButton(_t(lang, "btn_mass_mention"), "massmention", self, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(self, guild_id, section, lang=lang),
            BadWordsActionButton(self, guild_id, section, lang),
        ))

    elif section == "image_filter":
        container.add_item(discord.ui.ActionRow(
            ToggleButton(_t(lang, "btn_nsfw_filter"), "nsfw_image_filter", self, guild_id, section),
            ToggleButton(_t(lang, "btn_scam_images"), "scam_image_filter", self, guild_id, section),
        ))

    elif section == "antinuke":
        container.add_item(discord.ui.ActionRow(
            ToggleButton(_t(lang, "btn_anti_nuke"), "antinuke", self, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(self, guild_id, section, lang=lang),
            _NukeActionButton(self, guild_id, lang),
            _NukeExtThresholdButton(self, guild_id, lang),
        ))

    elif section == "antiraid":
        container.add_item(discord.ui.ActionRow(
            ToggleButton(_t(lang, "btn_anti_raid"), "antiraid", self, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(self, guild_id, section, lang=lang),
        ))

    elif section == "ext_raid":
        container.add_item(discord.ui.ActionRow(
            ToggleButton(_t(lang, "btn_interaction_flood"), "antiraid_ext", self, guild_id, section),
            SubToggleButton(
                _t(lang, "btn_user_app_detection"), "antiraid_ext", "ext_app_detection",
                self, guild_id, section,
            ),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(
                self, guild_id, section, label=_t(lang, "btn_flood_thresholds"), lang=lang,
            ),
            EditExtAppButton(self, guild_id, lang),
        ))

    elif section == "whitelist":
        wl_cfg = cfg
        has_u = bool(wl_cfg.get("whitelist_users", []))
        has_r = bool(wl_cfg.get("whitelist_roles", []))
        container.add_item(discord.ui.ActionRow(
            _WLAddUserBtn(self, guild_id, lang),
            _WLAddRoleBtn(self, guild_id, lang),
        ))
        container.add_item(discord.ui.ActionRow(
            _WLRemoveUserBtn(self, guild_id, has_u, lang),
            _WLRemoveRoleBtn(self, guild_id, has_r, lang),
        ))

    view.add_item(container)
    return view


class AntiNukeActionSelect(discord.ui.Select):
    def __init__(self, automod_cog, guild_id: int, cfg: dict, message, lang: str = "en"):
        self._cog = automod_cog
        self._guild_id = guild_id
        self.message = message
        options = [
            discord.SelectOption(
                label=_t(lang, "nuke_action_strip"), value="strip",
                description=_t(lang, "nuke_action_strip_desc"),
            ),
            discord.SelectOption(
                label=_t(lang, "nuke_action_kick"), value="kick",
                description=_t(lang, "nuke_action_kick_desc"),
            ),
            discord.SelectOption(
                label=_t(lang, "nuke_action_ban"), value="ban",
                description=_t(lang, "nuke_action_ban_desc"),
            )
        ]
        super().__init__(
            placeholder=_t(lang, "nuke_action_placeholder"),
            options=options,
            min_values=1, max_values=1
        )


    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        
        val = self.values[0]
        lang = get_lang(interaction.guild)
        if val not in ("strip", "kick", "ban"):
            return await interaction.response.send_message(
                _t(lang, "invalid_nuke_action"), ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        cfg["antinuke"]["action"] = val
        utils.save_config()
        await _log(
            self._cog, interaction, "AutoMod Settings",
            _log_t(lang, "settings_nuke_action", action=val),
            _log_t(lang, "title_settings"),
        )
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('tick')} "
                + _t(lang, "nuke_action_set", action=_t(lang, f"nuke_action_{val}"))
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)
        await self.message.edit(
            view=_build_panel(self._cog, self._guild_id, "antinuke", interaction.guild))


class BadWordsActionSelect(discord.ui.Select):
    """Chooses whether blocked words are deleted or censored and reposted."""

    def __init__(self, automod_cog, guild_id: int, message, lang: str = "en"):
        self._cog = automod_cog
        self._guild_id = guild_id
        self.message = message
        options = [
            discord.SelectOption(
                label=_t(lang, "bw_delete_label"), value="delete",
                description=_t(lang, "bw_delete_desc")),
            discord.SelectOption(
                label=_t(lang, "bw_censor_label"), value="censor",
                description=_t(lang, "bw_censor_desc")),
        ]
        super().__init__(
            placeholder=_t(lang, "bw_placeholder"),
            options=options, min_values=1, max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)

        val = self.values[0]
        lang = get_lang(interaction.guild)
        if val not in ("delete", "censor"):
            return await interaction.response.send_message(
                _t(lang, "badwords_action_invalid"), ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        cfg["badwords_action"] = val
        utils.save_config()
        await _log(
            self._cog, interaction, "AutoMod Settings",
            _log_t(lang, "settings_badwords", action=val),
            _log_t(lang, "title_settings"),
        )
        mode = _t(lang, "badwords_action_censor" if val == "censor" else "badwords_action_delete")
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('tick')} {_t(lang, 'bw_set', mode=mode)}"
            ),
            accent_colour=discord.Color.green(),
        ))
        await interaction.response.edit_message(view=view)
        await self.message.edit(view=_build_panel(self._cog, self._guild_id, "filter", interaction.guild))


class BadWordsActionButton(discord.ui.Button):
    """Opens the blocked-word response picker from the filter section."""

    def __init__(self, automod_cog, guild_id: int, section: str, lang: str = "en"):
        super().__init__(
            label=_t(lang, "badwords_action"), style=discord.ButtonStyle.gray,
            emoji=get_emoji("utility"),
        )
        self._cog = automod_cog
        self._guild_id = guild_id
        self._section = section

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        lang = get_lang(interaction.guild)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=_t(lang, "badwords_action_prompt")),
            discord.ui.ActionRow(BadWordsActionSelect(
                self._cog, self._guild_id, interaction.message, lang,
            )),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class _NukeActionButton(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int, lang: str = "en"):
        super().__init__(
            label=_t(lang, "btn_set_action"),
            style=discord.ButtonStyle.gray,
            emoji=get_emoji("utility")
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        lang = get_lang(interaction.guild)
        message = interaction.message
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=_t(lang, "nuke_action_prompt")),
            discord.ui.ActionRow(
                AntiNukeActionSelect(self._cog, self._guild_id, cfg, message, lang)
            )
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)
        # await interaction.response.send_modal(AntiNukeActionModal(self._cog, self._guild_id, cfg))


# ──────────────────────────────────────────────────
#  AUTOMOD COG
# ──────────────────────────────────────────────────


__all__ = [k for k in list(globals()) if not k.startswith("__")]
