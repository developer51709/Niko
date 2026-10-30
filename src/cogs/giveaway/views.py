import discord
from discord.ext import commands, tasks
import re
import json
import datetime
import random
import asyncio

from config.emojis import get_emoji
from utils.paginator import PaginatedView, paginate
from utils.blacklist_manager import BlacklistManager
from utils.guild_lockdown import paused_message
from utils.locales import load_locales


# ─────────────────────────────────────────────────────────────
#  BLACKLIST LOCKDOWN GUARDS
# ─────────────────────────────────────────────────────────────


def _guild_paused(guild_id) -> bool:
    """True while the guild is blacklisted.

    Giveaway buttons are component interactions, so they never pass through the
    slash-command blacklist gate; a blacklisted server's saved giveaway stays
    visible but stops accepting entries and management.
    """
    if guild_id is None:
        return False
    try:
        return BlacklistManager().is_guild_blacklisted(int(guild_id))
    except (TypeError, ValueError):
        return False


def _giveaway_paused(giveaway, guild_id) -> bool:
    """True when this giveaway row is locked or its guild is blacklisted."""
    if giveaway is not None and giveaway.get("locked"):
        return True
    return _guild_paused(guild_id)


async def _giveaway_banned(bot, guild_id, user_id) -> bool:
    """True when the member is banned from this server's giveaways.

    The ban lives in its own table and is scoped to the guild, so the same
    member can still enter giveaways in another server Niko is in.
    """
    if guild_id is None:
        return False
    row = await bot.cxn.fetchval(
        "SELECT 1 FROM giveaway_bans WHERE guild_id = $1 AND user_id = $2",
        int(guild_id), int(user_id),
    )
    return row is not None


# ─────────────────────────────────────────────────────────────
#  REQUIREMENT HELPERS
# ─────────────────────────────────────────────────────────────

DEFAULT_REQUIREMENTS = {
    "account_age_days": 0,   # minimum Discord account age (days)
    "server_age_days":  0,   # minimum time the user has been in the guild (days)
    "role_ids":         [],  # all of these role IDs must be held
    "boost_required":   False,
}


def _load_reqs(raw) -> dict:
    """Return a fully-populated requirements dict from a raw DB value."""
    out = dict(DEFAULT_REQUIREMENTS)
    if not raw:
        return out
    try:
        data = json.loads(raw) if isinstance(raw, str) else dict(raw)
    except (ValueError, TypeError):
        return out
    for key, default in DEFAULT_REQUIREMENTS.items():
        if key in data and data[key] is not None:
            out[key] = data[key]
    if not isinstance(out["role_ids"], list):
        out["role_ids"] = []
    out["account_age_days"] = max(0, int(out["account_age_days"] or 0))
    out["server_age_days"]  = max(0, int(out["server_age_days"] or 0))
    out["boost_required"]   = bool(out["boost_required"])
    return out


def _dump_reqs(reqs: dict) -> str:
    return json.dumps({k: reqs.get(k, v) for k, v in DEFAULT_REQUIREMENTS.items()})


def _requirements_summary(reqs: dict, guild: discord.Guild | None = None, locale=None) -> str:
    """Human-readable bullet list of the current requirements (or 'None')."""
    locale = locale if locale is not None else guild
    parts: list[str] = []
    if reqs["account_age_days"] > 0:
        parts.append(msg(locale, "req_account_age", days=reqs["account_age_days"]))
    if reqs["server_age_days"] > 0:
        parts.append(msg(locale, "req_server_age", days=reqs["server_age_days"]))
    if reqs["role_ids"]:
        if guild:
            mentions = []
            for rid in reqs["role_ids"]:
                role = guild.get_role(rid)
                mentions.append(role.mention if role else f"<@&{rid}>")
            parts.append(msg(locale, "req_roles", roles=", ".join(mentions)))
        else:
            parts.append(
                msg(locale, "req_roles", roles=", ".join(f"<@&{rid}>" for rid in reqs["role_ids"]))
            )
    if reqs["boost_required"]:
        parts.append(msg(locale, "req_boost"))
    return "\n".join(parts) if parts else msg(locale, "req_none")


def _check_member_meets_reqs(member: discord.Member, reqs: dict, locale=None) -> str | None:
    """Return ``None`` if ``member`` meets every requirement, else a reason string."""
    now = datetime.datetime.now(datetime.timezone.utc)
    locale = locale if locale is not None else getattr(member, "guild", None)

    if reqs["account_age_days"] > 0:
        age = (now - member.created_at).days
        if age < reqs["account_age_days"]:
            return msg(
                locale,
                "join_req_account_age",
                days=reqs["account_age_days"],
                age=age,
            )

    if reqs["server_age_days"] > 0:
        joined_at = getattr(member, "joined_at", None)
        if joined_at is None:
            return msg(locale, "join_req_server_unknown")
        days_in = (now - joined_at).days
        if days_in < reqs["server_age_days"]:
            return msg(
                locale,
                "join_req_server_age",
                days=reqs["server_age_days"],
                joined=days_in,
            )

    if reqs["role_ids"]:
        member_role_ids = {r.id for r in member.roles}
        missing = [rid for rid in reqs["role_ids"] if rid not in member_role_ids]
        if missing:
            mentions = ", ".join(f"<@&{rid}>" for rid in missing)
            return msg(locale, "join_req_roles", roles=mentions)

    if reqs["boost_required"] and getattr(member, "premium_since", None) is None:
        return msg(locale, "join_req_boost")

    return None

# ─────────────────────────────────────────────────────────────
#  MESSAGE TABLE
# ─────────────────────────────────────────────────────────────

MESSAGES = load_locales("cogs.giveaway", "views")


def _get_lang(obj) -> str:
    """The language of a prompt, of an interaction, or of a guild itself.

    A modal is assembled from a view that only holds ``guild``, so a caller
    with no context to hand passes the guild directly; without this it would
    quietly fall back to English.
    """
    guild = getattr(obj, "guild", None)
    if guild is None and getattr(obj, "preferred_locale", None):
        guild = obj
    if guild and getattr(guild, "preferred_locale", None):
        if str(guild.preferred_locale).lower().startswith("de"):
            return "de"
        if str(guild.preferred_locale).lower().startswith("es"):
            return "es"
    return "en"


#: Emoji tokens a message may carry as ``{name}``.
#:
#: The table is translated per language, so an emoji that only lives inside a
#: translated sentence cannot be swapped at the call site. Each language keeps
#: the token and this resolves it, which keeps one icon set across all three.
_EMOJI_FIELDS = (
    "giveaway", "tick", "cross", "settings", "gambling", "participants", "sad",
    "trash", "duration",
)


def msg(obj, key: str, **kwargs) -> str:
    """Resolve a giveaway message: guild language, then English, then the key."""
    lang = _get_lang(obj)
    text = MESSAGES.get(lang, {}).get(key)
    if text is None:
        text = MESSAGES["en"].get(key, key)
    for name in _EMOJI_FIELDS:
        token = "{" + name + "}"
        if token in text:
            text = text.replace(token, get_emoji(name))
    return text.format(**kwargs) if kwargs else text


def _guild_msg(guild, key: str, **kwargs) -> str:
    class _Wrap:
        pass
    w = _Wrap()
    w.guild = guild
    return msg(w, key, **kwargs)


# ─────────────────────────────────────────────────────────────
#  MAIN MESSAGE BUTTONS  (per-giveaway custom_id for isolation)
# ─────────────────────────────────────────────────────────────

class _GiveawayJoinBtn(discord.ui.Button):
    """Join button — custom_id encodes the giveaway message_id."""

    def __init__(self, bot, message_id: int, guild=None):
        super().__init__(
            label=_guild_msg(guild, "btn_join"),
            style=discord.ButtonStyle.primary,
            emoji=f"{get_emoji('giveaway')}",
            custom_id=f"giveaway_join_{message_id}",
        )
        self._bot = bot

    async def callback(self, interaction: discord.Interaction):
        message_id = interaction.message.id
        user_id    = interaction.user.id

        giveaway = await self._bot.cxn.fetchrow(
            "SELECT host_id, ended, requirements, locked FROM giveaways WHERE message_id = $1",
            message_id,
        )
        if not giveaway:
            return await interaction.response.send_message(f"{get_emoji('cross')} {msg(interaction, 'no_exist')}", ephemeral=True)
        if giveaway["ended"]:
            return await interaction.response.send_message(f"{get_emoji('cross')} {msg(interaction, 'join_ended')}", ephemeral=True)
        # Blacklisted servers keep their giveaway rows but cannot take entries.
        if _giveaway_paused(giveaway, interaction.guild_id):
            return await interaction.response.send_message(paused_message(interaction), ephemeral=True)
        if user_id == giveaway["host_id"]:
            return await interaction.response.send_message(f"{get_emoji('cross')} {msg(interaction, 'join_host')}", ephemeral=True)
        if interaction.user.bot:
            return await interaction.response.send_message(f"{get_emoji('cross')} {msg(interaction, 'join_bot')}", ephemeral=True)
        # A giveaway ban is set by the server's managers and wins over every
        # other check, so a banned member is told why instead of being asked to
        # meet requirements they will never satisfy.
        if await _giveaway_banned(self._bot, interaction.guild_id, user_id):
            return await interaction.response.send_message(f"{get_emoji('cross')} {msg(interaction, 'join_banned')}", ephemeral=True)

        # Enforce host-configured requirements (account age, server age, roles, boost).
        reqs = _load_reqs(giveaway["requirements"])
        if isinstance(interaction.user, discord.Member):
            failure = _check_member_meets_reqs(interaction.user, reqs)
            if failure:
                return await interaction.response.send_message(failure, ephemeral=True)

        existing = await self._bot.cxn.fetchval(
            "SELECT 1 FROM participants WHERE message_id = $1 AND user_id = $2",
            message_id, user_id
        )
        if existing:
            return await interaction.response.send_message(msg(interaction, 'join_already'), ephemeral=True)

        await self._bot.cxn.execute(
            "INSERT INTO participants (message_id, user_id) VALUES ($1, $2)", message_id, user_id
        )
        await interaction.response.send_message(msg(interaction, 'join_success'), ephemeral=True)


class _GiveawayManageBtn(discord.ui.Button):
    """Manage button — opens ephemeral panel for host / server admins."""

    def __init__(self, bot, message_id: int, guild=None):
        super().__init__(
            label=_guild_msg(guild, "btn_manage"),
            style=discord.ButtonStyle.secondary,
            emoji=f"{get_emoji('settings')}",
            custom_id=f"giveaway_manage_{message_id}",
        )
        self._bot = bot

    async def callback(self, interaction: discord.Interaction):
        message_id = interaction.message.id

        giveaway = await self._bot.cxn.fetchrow(
            "SELECT message_id, channel_id, guild_id, prize, winners_count, host_id, ended "
            "FROM giveaways WHERE message_id = $1", message_id
        )
        if not giveaway:
            return await interaction.response.send_message(msg(interaction, "no_exist"), ephemeral=True)
        if giveaway["ended"]:
            return await interaction.response.send_message(msg(interaction, "join_ended"), ephemeral=True)
        if _giveaway_paused(None, giveaway.get("guild_id")):
            return await interaction.response.send_message(paused_message(interaction), ephemeral=True)

        is_host  = interaction.user.id == giveaway["host_id"]
        is_admin = interaction.user.guild_permissions.manage_guild
        if not (is_host or is_admin):
            return await interaction.response.send_message(
                msg(interaction, "no_perm_manage"), ephemeral=True
            )

        panel = _build_manage_panel(self._bot, giveaway, interaction.guild)
        await interaction.response.send_message(view=panel, ephemeral=True)


def _make_persistent_view(bot, message_id: int, guild=None) -> discord.ui.View:
    """
    A timeout=None View registered with bot.add_view(view, message_id=...).
    Each active giveaway gets its own registered view, keyed by message_id,
    so button interactions from different giveaway messages never interfere.
    """
    view = discord.ui.View(timeout=None)
    view.add_item(_GiveawayJoinBtn(bot, message_id, guild))
    view.add_item(_GiveawayManageBtn(bot, message_id, guild))
    return view


# ─────────────────────────────────────────────────────────────
#  MANAGEMENT PANEL BUTTONS  (ephemeral — no persistence needed)
# ─────────────────────────────────────────────────────────────

class _MgmtEndBtn(discord.ui.Button):
    def __init__(self, bot, message_id, prize, winners_count, channel_id, guild_id, host_id,
                 guild=None):
        super().__init__(
            label=_guild_msg(guild, "btn_end"),
            style=discord.ButtonStyle.danger,
            emoji=get_emoji("stop"),
        )
        self._bot           = bot
        self._message_id    = message_id
        self._prize         = prize
        self._winners_count = winners_count
        self._channel_id    = channel_id
        self._guild_id      = guild_id
        self._host_id       = host_id

    async def callback(self, interaction: discord.Interaction):
        confirm_view = discord.ui.LayoutView()
        confirm_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(interaction, "end_confirmed")),
            accent_colour=discord.Color.green()
        ))
        await interaction.response.edit_message(view=confirm_view)

        giveaway_cog = self._bot.get_cog("Giveaway")
        if giveaway_cog:
            await giveaway_cog.end_giveaway(
                self._message_id, self._channel_id, self._guild_id,
                self._prize, self._winners_count, self._host_id,
            )


class _MgmtSelectBtn(discord.ui.Button):
    def __init__(self, bot, message_id, guild=None):
        super().__init__(
            label=_guild_msg(guild, "btn_select_random"),
            style=discord.ButtonStyle.secondary, emoji=f"{get_emoji('gambling')}")
        self._bot        = bot
        self._message_id = message_id

    async def callback(self, interaction: discord.Interaction):
        rows = await self._bot.cxn.fetch(
            "SELECT user_id FROM participants WHERE message_id = $1", self._message_id
        )
        participants = [row["user_id"] for row in rows]
        # A manual selection is still a draw, so a banned member cannot be
        # picked here either.
        if participants:
            banned = await self._bot.cxn.fetch(
                "SELECT user_id FROM giveaway_bans WHERE guild_id = $1",
                interaction.guild_id,
            )
            banned_ids = {int(row["user_id"]) for row in banned}
            participants = [uid for uid in participants if int(uid) not in banned_ids]

        if not participants:
            empty_view = discord.ui.LayoutView()
            empty_view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=msg(interaction, "select_no_entries")),
                accent_colour=discord.Color.orange()
            ))
            return await interaction.response.edit_message(view=empty_view)

        winner      = random.choice(participants)
        result_view = discord.ui.LayoutView()
        result_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(interaction, "select_result", mention=f"<@{winner}>")),
            accent_colour=discord.Color.green()
        ))
        await interaction.response.edit_message(view=result_view)


class _MgmtParticipantsBtn(discord.ui.Button):
    def __init__(self, bot, message_id, guild=None):
        super().__init__(
            label=_guild_msg(guild, "btn_participants"),
            style=discord.ButtonStyle.blurple,
            emoji=get_emoji("participants"),
        )
        self._bot        = bot
        self._message_id = message_id

    async def callback(self, interaction: discord.Interaction):
        rows = await self._bot.cxn.fetch(
            "SELECT user_id FROM participants WHERE message_id = $1", self._message_id
        )
        if not rows:
            empty_view = discord.ui.LayoutView()
            empty_view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {msg(interaction, 'participants_title')}\n"
                            f"{msg(interaction, 'participants_empty')}"
                ),
                accent_colour=discord.Color.blurple()
            ))
            return await interaction.response.edit_message(view=empty_view)

        lines             = [f"**{i}.** <@{row['user_id']}>" for i, row in enumerate(rows, 1)]
        pages             = paginate(lines, per_page=15)
        participants_view = PaginatedView(
            title=msg(interaction, "participants_title"),
            pages=pages,
            icon_url=interaction.guild.icon.url if interaction.guild and interaction.guild.icon else None,
        )
        await interaction.response.edit_message(view=participants_view)


# ─────────────────────────────────────────────────────────────
#  VIEW BUILDERS
# ─────────────────────────────────────────────────────────────

def _build_content_view(prize: str, end_timestamp: int, winners_count: int,
                        author_mention: str, guild=None) -> discord.ui.LayoutView:
    """
    Layout-only view (no buttons).  Sent first so we can obtain the message_id,
    then immediately edited to add interactive buttons.
    """
    s      = "s" if winners_count > 1 else ""
    footer = _guild_msg(guild, "footer_active", count=winners_count, s=s)

    view      = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {get_emoji('giveaway')} {_guild_msg(guild, 'giveaway_title')}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                f"**{_guild_msg(guild, 'label_prize')}:** {prize}\n"
                f"**{_guild_msg(guild, 'label_ends')}:** <t:{end_timestamp}:R> (<t:{end_timestamp}:f>)\n"
                f"**{_guild_msg(guild, 'label_hosted_by')}:** {author_mention}"
            )
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=f"-# {footer} <t:{end_timestamp}:f>"),
        accent_colour=discord.Color.purple()
    )
    view.add_item(container)
    return view


def _build_active_view(bot, message_id: int, prize: str, end_timestamp: int,
                       winners_count: int, author_mention: str,
                       guild=None) -> discord.ui.LayoutView:
    """Full active giveaway view with interactive Join + Manage buttons."""
    s      = "s" if winners_count > 1 else ""
    footer = _guild_msg(guild, "footer_active", count=winners_count, s=s)

    view      = discord.ui.LayoutView(timeout=None)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {get_emoji('giveaway')} {_guild_msg(guild, 'giveaway_title')}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                f"**{_guild_msg(guild, 'label_prize')}:** {prize}\n"
                f"**{_guild_msg(guild, 'label_ends')}:** <t:{end_timestamp}:R> (<t:{end_timestamp}:f>)\n"
                f"**{_guild_msg(guild, 'label_hosted_by')}:** {author_mention}"
            )
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            _GiveawayJoinBtn(bot, message_id, guild),
            _GiveawayManageBtn(bot, message_id, guild),
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=f"-# {footer} <t:{end_timestamp}:f>"),
        accent_colour=discord.Color.purple()
    )
    view.add_item(container)
    return view


def _build_ended_view(guild, prize: str, host_id: int,
                      winners: list = None) -> discord.ui.LayoutView:
    if winners:
        winner_mentions = ", ".join(f"<@{w}>" for w in winners)
        result_text = (
            f"**{_guild_msg(guild, 'label_prize')}:** {prize}\n"
            f"**{_guild_msg(guild, 'label_hosted_by')}:** <@{host_id}>\n"
            f"**{_guild_msg(guild, 'label_winner')}:** {winner_mentions}"
        )
    else:
        result_text = (
            f"**{_guild_msg(guild, 'label_prize')}:** {prize}\n"
            f"**{_guild_msg(guild, 'label_hosted_by')}:** <@{host_id}>\n"
            f"**{_guild_msg(guild, 'label_no_participants')}**"
        )

    view      = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {get_emoji('giveaway')} {_guild_msg(guild, 'giveaway_ended_title')}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=result_text),
        accent_colour=discord.Color.gold()
    )
    view.add_item(container)
    return view


def _build_manage_panel(bot, giveaway_row, guild=None) -> discord.ui.LayoutView:
    message_id    = giveaway_row["message_id"]
    prize         = giveaway_row["prize"]
    winners_count = giveaway_row["winners_count"]
    channel_id    = giveaway_row["channel_id"]
    guild_id      = giveaway_row["guild_id"]
    host_id       = giveaway_row["host_id"]

    view      = discord.ui.LayoutView(timeout=180)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {_guild_msg(guild, 'manage_title')}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                f"**{_guild_msg(guild, 'label_prize')}:** {prize}\n"
                f"**{_guild_msg(guild, 'label_hosted_by')}:** <@{host_id}>\n\n"
                f"{_guild_msg(guild, 'manage_info')}"
            )
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            _MgmtEndBtn(bot, message_id, prize, winners_count, channel_id, guild_id, host_id,
                        guild),
            _MgmtSelectBtn(bot, message_id, guild),
            _MgmtParticipantsBtn(bot, message_id, guild),
        ),
        accent_colour=discord.Color.purple()
    )
    view.add_item(container)
    return view


# ─────────────────────────────────────────────────────────────
#  INTERACTIVE SETUP — `.giveaway start` panel
# ─────────────────────────────────────────────────────────────

def _parse_duration_str(value: str) -> int:
    """Mirror of ``Giveaway.parse_duration`` but free-standing for the setup view."""
    m = re.match(r"\s*([\d\.]+)\s*([smhd])\s*$", value.lower())
    if not m:
        return -1
    try:
        amount = float(m.group(1))
        unit   = m.group(2)
        return int(amount * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit])
    except ValueError:
        return -1


def _format_duration(seconds: int) -> str:
    if seconds <= 0:
        return "—"
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    bits = []
    if days:    bits.append(f"{days}d")
    if hours:   bits.append(f"{hours}h")
    if minutes: bits.append(f"{minutes}m")
    if secs:    bits.append(f"{secs}s")
    return " ".join(bits) if bits else "—"


class _SetupState:
    """Mutable state held by an in-flight giveaway-setup view."""
    __slots__ = ("prize", "duration_s", "winners", "channel_id", "requirements")

    def __init__(self, channel_id: int):
        self.prize: str | None         = None
        self.duration_s: int           = 0
        self.winners: int              = 1
        self.channel_id: int           = channel_id
        self.requirements: dict        = dict(DEFAULT_REQUIREMENTS)
        self.requirements["role_ids"] = []


def _build_setup_view(bot, ctx_or_inter, state: _SetupState, host_id: int) -> "_GiveawaySetupView":
    return _GiveawaySetupView(bot, ctx_or_inter, state, host_id)


# ── Modals ──────────────────────────────────────────────────

class _PrizeModal(discord.ui.Modal, title="Set Prize"):
    def __init__(self, parent: "_GiveawaySetupView"):
        super().__init__(title=_guild_msg(parent.guild, "modal_prize_title"))
        self._setup_view = parent
        # Built per interaction so the label can carry the guild's language.
        self.prize = discord.ui.TextInput(
            label=_guild_msg(parent.guild, "modal_prize_label"),
            placeholder=_guild_msg(parent.guild, "modal_prize_ph"),
            max_length=200, required=True, style=discord.TextStyle.short,
            default=parent.state.prize or None,
        )
        self.add_item(self.prize)

    async def on_submit(self, interaction: discord.Interaction):
        self._setup_view.state.prize = self.prize.value.strip()
        await self._setup_view.refresh(interaction)


class _DurationModal(discord.ui.Modal, title="Set Duration"):
    def __init__(self, parent: "_GiveawaySetupView"):
        super().__init__(title=_guild_msg(parent.guild, "modal_duration_title"))
        self._setup_view = parent
        self.duration = discord.ui.TextInput(
            label=_guild_msg(parent.guild, "modal_duration_label"),
            placeholder=_guild_msg(parent.guild, "modal_duration_ph"),
            max_length=20, required=True, style=discord.TextStyle.short,
        )
        self.add_item(self.duration)

    async def on_submit(self, interaction: discord.Interaction):
        seconds = _parse_duration_str(self.duration.value)
        if seconds <= 0:
            return await interaction.response.send_message(
                msg(interaction, "invalid_duration"), ephemeral=True
            )
        self._setup_view.state.duration_s = seconds
        await self._setup_view.refresh(interaction)


class _WinnersModal(discord.ui.Modal, title="Set Winners"):
    def __init__(self, parent: "_GiveawaySetupView"):
        super().__init__(title=_guild_msg(parent.guild, "modal_winners_title"))
        self._setup_view = parent
        self.winners = discord.ui.TextInput(
            label=_guild_msg(parent.guild, "modal_winners_label"),
            placeholder=_guild_msg(parent.guild, "modal_winners_ph"),
            max_length=4, required=True, style=discord.TextStyle.short,
            default=str(parent.state.winners),
        )
        self.add_item(self.winners)

    async def on_submit(self, interaction: discord.Interaction):
        digits = "".join(ch for ch in self.winners.value if ch.isdigit())
        if not digits or int(digits) < 1:
            return await interaction.response.send_message(
                msg(interaction, "min_one_winner"), ephemeral=True
            )
        self._setup_view.state.winners = int(digits)
        await self._setup_view.refresh(interaction)


class _AccountAgeModal(discord.ui.Modal, title="Minimum Account Age"):
    def __init__(self, parent: "_GiveawaySetupView"):
        super().__init__(title=_guild_msg(parent.guild, "modal_account_age_title"))
        self._setup_view = parent
        self.days = discord.ui.TextInput(
            label=_guild_msg(parent.guild, "modal_account_age_label"),
            placeholder=_guild_msg(parent.guild, "modal_account_age_ph"),
            max_length=5, required=True, style=discord.TextStyle.short,
            default=str(parent.state.requirements["account_age_days"]),
        )
        self.add_item(self.days)

    async def on_submit(self, interaction: discord.Interaction):
        digits = "".join(ch for ch in self.days.value if ch.isdigit())
        value = int(digits) if digits else 0
        self._setup_view.state.requirements["account_age_days"] = max(0, min(value, 3650))
        await self._setup_view.refresh(interaction)


class _ServerAgeModal(discord.ui.Modal, title="Minimum Time in Server"):
    def __init__(self, parent: "_GiveawaySetupView"):
        super().__init__(title=_guild_msg(parent.guild, "modal_server_age_title"))
        self._setup_view = parent
        self.days = discord.ui.TextInput(
            label=_guild_msg(parent.guild, "modal_server_age_label"),
            placeholder=_guild_msg(parent.guild, "modal_server_age_ph"),
            max_length=5, required=True, style=discord.TextStyle.short,
            default=str(parent.state.requirements["server_age_days"]),
        )
        self.add_item(self.days)

    async def on_submit(self, interaction: discord.Interaction):
        digits = "".join(ch for ch in self.days.value if ch.isdigit())
        value = int(digits) if digits else 0
        self._setup_view.state.requirements["server_age_days"] = max(0, min(value, 3650))
        await self._setup_view.refresh(interaction)


# ── Buttons ─────────────────────────────────────────────────

class _SetupBtn(discord.ui.Button):
    def __init__(self, label: str, style, emoji, parent: "_GiveawaySetupView", action: str,
                 *, row: int = 0):
        super().__init__(label=label, style=style, emoji=emoji)
        self._setup_view = parent
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self._setup_view.host_id:
            return await interaction.response.send_message(
                msg(interaction, "setup_host_only"),
                ephemeral=True,
            )
        action = self.action
        if action == "prize":
            return await interaction.response.send_modal(_PrizeModal(self._setup_view))
        if action == "duration":
            return await interaction.response.send_modal(_DurationModal(self._setup_view))
        if action == "winners":
            return await interaction.response.send_modal(_WinnersModal(self._setup_view))
        if action == "account_age":
            return await interaction.response.send_modal(_AccountAgeModal(self._setup_view))
        if action == "server_age":
            return await interaction.response.send_modal(_ServerAgeModal(self._setup_view))
        if action == "boost":
            self._setup_view.state.requirements["boost_required"] = (
                not self._setup_view.state.requirements["boost_required"]
            )
            return await self._setup_view.refresh(interaction)
        if action == "clear_roles":
            self._setup_view.state.requirements["role_ids"] = []
            return await self._setup_view.refresh(interaction)
        if action == "cancel":
            cancelled = discord.ui.LayoutView()
            cancelled.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=msg(interaction, "setup_cancelled")),
                accent_colour=discord.Color.red(),
            ))
            return await interaction.response.edit_message(view=cancelled)
        if action == "start":
            return await self._setup_view.launch(interaction)


class _SetupChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, parent: "_GiveawaySetupView"):
        super().__init__(
            placeholder=msg(parent.guild, "select_channel"),
            channel_types=[discord.ChannelType.text, discord.ChannelType.news],
            min_values=1, max_values=1,
        )
        self._setup_view = parent

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self._setup_view.host_id:
            return await interaction.response.send_message(
                msg(interaction, "setup_host_only"), ephemeral=True
            )
        self._setup_view.state.channel_id = self.values[0].id
        await self._setup_view.refresh(interaction)


class _SetupRoleSelect(discord.ui.RoleSelect):
    def __init__(self, parent: "_GiveawaySetupView"):
        super().__init__(
            placeholder=msg(parent.guild, "select_roles"),
            min_values=0, max_values=10,
        )
        self._setup_view = parent

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self._setup_view.host_id:
            return await interaction.response.send_message(
                msg(interaction, "setup_host_only"), ephemeral=True
            )
        self._setup_view.state.requirements["role_ids"] = [r.id for r in self.values]
        await self._setup_view.refresh(interaction)


# ── Setup view ─────────────────────────────────────────────

class _GiveawaySetupView(discord.ui.LayoutView):
    """Interactive panel returned by ``.giveaway start``."""

    def __init__(self, bot, ctx_or_inter, state: _SetupState, host_id: int):
        super().__init__(timeout=600)
        self.bot       = bot
        self.state     = state
        self.host_id   = host_id
        self.guild     = getattr(ctx_or_inter, "guild", None)
        self.message: discord.Message | None = None  # set after the first send
        self._build()

    # ── building ───────────────────────────────────────

    def _build(self):
        self.clear_items()
        s = self.state
        guild = self.guild

        channel_disp = f"<#{s.channel_id}>" if s.channel_id else "—"
        prize_disp   = s.prize if s.prize else msg(guild, "setup_not_set")
        dur_disp     = _format_duration(s.duration_s)

        summary = msg(
            guild,
            "setup_summary",
            prize=prize_disp,
            duration=dur_disp,
            winners=s.winners,
            channel=channel_disp,
        )
        reqs_text = _requirements_summary(s.requirements, guild, guild)

        boost_label = msg(
            guild,
            "btn_boost_on" if s.requirements["boost_required"] else "btn_boost_off",
        )
        boost_style = (
            discord.ButtonStyle.success if s.requirements["boost_required"]
            else discord.ButtonStyle.secondary
        )

        ready = bool(s.prize) and s.duration_s > 0 and s.channel_id
        start_style = discord.ButtonStyle.success if ready else discord.ButtonStyle.secondary

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=msg(guild, "setup_title")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=summary),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=msg(guild, "setup_requirements", requirements=reqs_text)),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _SetupBtn(msg(guild, "btn_prize"),    discord.ButtonStyle.primary,   f"{get_emoji('gift')}", self, "prize"),
                _SetupBtn(msg(guild, "btn_duration"), discord.ButtonStyle.primary,   f"{get_emoji('duration')}", self, "duration"),
                _SetupBtn(msg(guild, "btn_winners"),  discord.ButtonStyle.primary,   f"{get_emoji('trophy')}", self, "winners"),
            ),
            discord.ui.ActionRow(_SetupChannelSelect(self)),
            discord.ui.ActionRow(_SetupRoleSelect(self)),
            discord.ui.ActionRow(
                _SetupBtn(msg(guild, "btn_account_age"), discord.ButtonStyle.secondary, f"{get_emoji('welcome')}", self, "account_age"),
                _SetupBtn(msg(guild, "btn_server_age"), discord.ButtonStyle.secondary, f"{get_emoji('home')}",    self, "server_age"),
                _SetupBtn(boost_label,   boost_style,                   f"{get_emoji('premium')}", self, "boost"),
                _SetupBtn(msg(guild, "btn_clear_roles"), discord.ButtonStyle.secondary, f"{get_emoji('broom')}",        self, "clear_roles"),
            ),
            discord.ui.ActionRow(
                _SetupBtn(msg(guild, "btn_start"), start_style,                f"{get_emoji('giveaway')}", self, "start"),
                _SetupBtn(msg(guild, "btn_cancel"),         discord.ButtonStyle.danger, f"{get_emoji('trash')}",         self, "cancel"),
            ),
            accent_colour=discord.Color.purple(),
        )
        self.add_item(container)

    async def refresh(self, interaction: discord.Interaction):
        self._build()
        await interaction.response.edit_message(view=self)

    async def on_timeout(self):
        if self.message is None:
            return
        try:
            timeout_view = discord.ui.LayoutView()
            timeout_view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=msg(self.guild, "setup_timeout")),
                accent_colour=discord.Color.greyple(),
            ))
            await self.message.edit(view=timeout_view)
        except discord.HTTPException:
            pass

    # ── launching the giveaway from setup state ─────────

    async def launch(self, interaction: discord.Interaction):
        s = self.state
        problems = []
        if not s.prize:
            problems.append(msg(interaction, "launch_missing_prize"))
        if s.duration_s <= 0:
            problems.append(msg(interaction, "launch_missing_duration"))
        if not s.channel_id:
            problems.append(msg(interaction, "launch_missing_channel"))
        if problems:
            return await interaction.response.send_message(
                msg(interaction, "launch_problems", problems="\n".join(problems)),
                ephemeral=True,
            )

        guild   = interaction.guild
        channel = guild.get_channel(s.channel_id) if guild else None
        if channel is None:
            return await interaction.response.send_message(
                msg(interaction, "launch_no_channel"), ephemeral=True
            )
        me = guild.me if guild else None
        if me and not channel.permissions_for(me).send_messages:
            return await interaction.response.send_message(
                msg(interaction, "launch_cant_send", channel=channel.mention), ephemeral=True
            )

        end_time      = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=s.duration_s)
        end_timestamp = int(end_time.timestamp())
        author_mention = f"<@{self.host_id}>"

        # Step 1: send a stub message in the chosen channel to obtain its ID.
        content_view = _build_content_view(
            s.prize, end_timestamp, s.winners, author_mention, guild
        )
        sent = await channel.send(view=content_view)

        # Step 2: register persistent buttons + edit them in.
        active_view = _build_active_view(
            self.bot, sent.id, s.prize, end_timestamp, s.winners,
            author_mention, guild,
        )
        persistent_view = _make_persistent_view(self.bot, sent.id, guild)
        self.bot.add_view(persistent_view, message_id=sent.id)
        await sent.edit(view=active_view)

        # Step 3: persist everything to the DB, including requirements.
        await self.bot.cxn.execute(
            "INSERT INTO giveaways "
            "(message_id, channel_id, guild_id, prize, winners_count, end_time, ended, host_id, requirements) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
            sent.id, channel.id, guild.id,
            s.prize, s.winners, end_time.isoformat(), False, self.host_id,
            _dump_reqs(s.requirements),
        )

        # Step 4: collapse the setup panel.
        done_view = discord.ui.LayoutView()
        reqs_line = _requirements_summary(s.requirements, guild, guild)
        done_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(
                    guild,
                    "launch_done",
                    prize=s.prize,
                    channel=channel.mention,
                    ends=end_timestamp,
                    requirements=reqs_line,
                )
            ),
            accent_colour=discord.Color.green(),
        ))
        await interaction.response.edit_message(view=done_view)


# ─────────────────────────────────────────────────────────────
#  GIVEAWAY COG
# ─────────────────────────────────────────────────────────────


__all__ = [k for k in list(globals()) if not k.startswith("__")]
