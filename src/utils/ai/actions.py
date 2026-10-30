"""AI Actions dispatcher.

Handles structured action requests returned by the AI integration when the AI
Actions experiment is enabled. Every destructive action goes through the same
pipeline before it can affect the server:

1.  **Permission check** — the invoker *and* Niko must hold the Discord
    permission required for that action, evaluated in the affected channel so
    channel overwrites (not just guild-level permissions) are honoured.
2.  **Hierarchy check** — the target member or role must sit below the
    invoker's highest role as well as below Niko's, so the AI cannot be used to
    grant a role above the invoker or to moderate someone they outrank-check
    away. The server owner bypasses the invoker check.
3.  **Confirmation** — a CV2 LayoutView describes exactly what is about to
    happen. Only the requesting user can confirm or cancel, and the card
    expires. The same card is then edited into the outcome, so a request never
    leaves a spent prompt behind with a separate result message under it.

``create_poll`` is the one non-destructive action: it skips the confirmation but
still requires Send Messages in the channel.

Every completed action is also written to Niko's own moderation/channel logs;
those log entries stay in English because the logging cog translates their
titles and field labels when it renders them.

All wording shown in the requesting channel lives in ``locales/`` next to this
package, one file per shipped language, and is resolved through the guild's
locale at the moment it is sent.
"""

from __future__ import annotations

import asyncio
import re
from typing import Optional

import discord

from config.emojis import get_emoji
from utils import logging
from utils.i18n import make_flat_msg
from utils.locales import load_locales

#: ``{lang: {key: text}}`` for this package, namespace ``actions``.
MESSAGES = load_locales("utils.ai", "actions")
t = make_flat_msg(MESSAGES)

#: Keys the confirmation view needs; resolved once per request so a guild that
#: switches language mid-prompt still gets the wording it started with.
_CONFIRM_TEXT_KEYS = (
    "confirm_footer",
    "button_confirm",
    "button_cancel",
    "confirm_author_only",
    "cancel_title",
    "cancel_body",
    "expired_title",
    "expired_body",
)


# ────────────────────────────────────────────────────────────────────
#  Helpers — resolution of natural-language targets the AI gives us
# ────────────────────────────────────────────────────────────────────

_MENTION_RE = re.compile(r"<@!?(\d+)>")
_CHANNEL_MENTION_RE = re.compile(r"<#(\d+)>")
_ROLE_MENTION_RE = re.compile(r"<@&(\d+)>")


def _coerce_id(value) -> Optional[int]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    m = _MENTION_RE.fullmatch(s) or _CHANNEL_MENTION_RE.fullmatch(s) or _ROLE_MENTION_RE.fullmatch(s)
    if m:
        s = m.group(1)
    if s.isdigit():
        try:
            return int(s)
        except ValueError:
            return None
    return None


async def _resolve_member(guild: discord.Guild, value) -> Optional[discord.Member]:
    if value is None:
        return None
    uid = _coerce_id(value)
    if uid:
        m = guild.get_member(uid)
        if m:
            return m
        try:
            return await guild.fetch_member(uid)
        except discord.HTTPException:
            return None
    name = str(value).strip().lstrip("@")
    if not name:
        return None
    lowered = name.lower()
    for m in guild.members:
        if m.name.lower() == lowered or m.display_name.lower() == lowered:
            return m
    # Ambiguous partial names used to pick whichever member happened to come
    # first; require a unique match instead.
    partial = [
        m for m in guild.members
        if lowered in m.name.lower() or lowered in m.display_name.lower()
    ]
    return partial[0] if len(partial) == 1 else None


async def _resolve_user(bot: discord.Client, value) -> Optional[discord.User]:
    uid = _coerce_id(value)
    if not uid:
        return None
    user = bot.get_user(uid)
    if user:
        return user
    try:
        return await bot.fetch_user(uid)
    except discord.HTTPException:
        return None


def _normalise_name(value) -> str:
    """Lowercase a name and strip mentions, decoration and separators."""
    name = re.sub(r"<[#@!&]*\d+>", "", str(value or ""))
    return name.strip().lstrip("#@").strip().lower()


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def _unique_match(name: str, items, key):
    """Exact match, then a unique prefix, then a unique substring.

    The model shortens names the way people speak — "memes" for
    "memes-and-gifs" — and an exact-only lookup used to fail those, leaving the
    action to report that the channel did not exist. A shortened name is only
    accepted when it picks out one item, so nothing is changed by guesswork.
    """
    if not name:
        return None
    for item in items:
        if key(item).lower() == name:
            return item
    prefixed = [item for item in items if key(item).lower().startswith(name)]
    if len(prefixed) == 1:
        return prefixed[0]
    partial = [item for item in items if name in key(item).lower()]
    return partial[0] if len(partial) == 1 else None


def _resolve_channel(guild: discord.Guild, value) -> Optional[discord.abc.GuildChannel]:
    if value is None:
        return None
    cid = _coerce_id(value)
    if cid:
        ch = guild.get_channel(cid)
        if ch:
            return ch
    name = _normalise_name(value)
    if not name:
        return None
    channel = _unique_match(name, guild.channels, lambda c: c.name)
    if channel is not None:
        return channel
    slug = _slugify(name)
    if slug and slug != name:
        return _unique_match(slug, guild.channels, lambda c: c.name)
    return None


def _resolve_role(guild: discord.Guild, value) -> Optional[discord.Role]:
    if value is None:
        return None
    rid = _coerce_id(value)
    if rid:
        r = guild.get_role(rid)
        if r:
            return r
    name = _normalise_name(value)
    if not name:
        return None
    role = _unique_match(name, guild.roles, lambda r: r.name)
    if role is not None:
        return role
    slug = _slugify(name)
    if slug and slug != name:
        return _unique_match(slug, guild.roles, lambda r: r.name)
    return None


def _as_category(channel) -> Optional[discord.CategoryChannel]:
    """The category itself, or the category a channel belongs to.

    A category is the channel flavour that owns children, so anything without
    children is treated as a channel whose parent category is meant.
    """
    if channel is None:
        return None
    if getattr(channel, "channels", None) is not None:
        return channel
    return getattr(channel, "category", None)


def _resolve_category(guild: discord.Guild, value) -> Optional[discord.CategoryChannel]:
    """Resolve a category by id/name, or the category a named channel is in."""
    if value is None:
        return None
    cid = _coerce_id(value)
    if cid:
        category = _as_category(guild.get_channel(cid))
        if category is not None:
            return category
    name = _normalise_name(value)
    if not name:
        return None
    category = _unique_match(name, guild.categories, lambda c: c.name)
    if category is not None:
        return category
    slug = _slugify(name)
    if slug and slug != name:
        category = _unique_match(slug, guild.categories, lambda c: c.name)
        if category is not None:
            return category
    # "put it next to #general" — use the category that channel lives in.
    return _as_category(_resolve_channel(guild, value))


def _perm_label(ctx, perm: str) -> str:
    """The permission's name in the guild's language.

    A permission with no translation falls back to its Discord name, which is
    better than showing the raw catalogue key.
    """
    key = f"perm_{perm}"
    label = t(ctx, key)
    return label if label != key else perm.replace("_", " ").title()


# ────────────────────────────────────────────────────────────────────
#  CV2 helpers — confirmation view, success/error notifications
# ────────────────────────────────────────────────────────────────────

def _info_view(
    ctx,
    title: str,
    body: str,
    *,
    colour: discord.Colour = discord.Colour.blurple(),
) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {title}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=body),
        accent_colour=colour,
    ))
    return view


def _error_view(ctx, body: str) -> discord.ui.LayoutView:
    return _info_view(
        ctx, f"{get_emoji('danger')} {t(ctx, 'error_title')}", body, colour=discord.Colour.red()
    )


def _success_view(ctx, body: str) -> discord.ui.LayoutView:
    return _info_view(
        ctx, f"{get_emoji('tick')} {t(ctx, 'success_title')}", body, colour=discord.Colour.green()
    )


class AIActionConfirmView(discord.ui.LayoutView):
    """LayoutView with Confirm + Cancel buttons gated to the invoker."""

    def __init__(self, title: str, body: str, *, invoker_id: int, text: dict, timeout: float = 45.0):
        super().__init__(timeout=timeout)
        self.invoker_id = invoker_id
        self.confirmed: bool | None = None
        self.message: discord.Message | None = None
        self.text = text
        self._event = asyncio.Event()

        self._confirm = discord.ui.Button(
            label=text["button_confirm"],
            style=discord.ButtonStyle.danger,
            emoji=get_emoji("tick") or "✅",
        )
        self._cancel = discord.ui.Button(
            label=text["button_cancel"],
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("cross") or "❌",
        )
        self._confirm.callback = self._on_confirm
        self._cancel.callback = self._on_cancel

        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('ai')} {title}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=body),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"-# {text['confirm_footer']}"),
            discord.ui.ActionRow(self._confirm, self._cancel),
            accent_colour=discord.Colour.orange(),
        ))

    async def _gate(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.invoker_id:
            await interaction.response.send_message(
                view=_error_view(interaction, self.text["confirm_author_only"]),
                ephemeral=True,
            )
            return False
        return True

    async def _disable_buttons(self):
        self._confirm.disabled = True
        self._cancel.disabled = True

    async def _on_confirm(self, interaction: discord.Interaction):
        if not await self._gate(interaction):
            return
        self.confirmed = True
        # The decision is made — cancel the countdown so it cannot later replace
        # the card with the expiry notice.
        self.stop()
        await self._disable_buttons()
        await interaction.response.edit_message(view=self)
        self._event.set()

    async def _on_cancel(self, interaction: discord.Interaction):
        if not await self._gate(interaction):
            return
        self.confirmed = False
        self.stop()
        await self._disable_buttons()
        await interaction.response.edit_message(
            view=_info_view(
                interaction,
                f"{get_emoji('cross')} {self.text['cancel_title']}",
                self.text["cancel_body"],
                colour=discord.Colour.greyple(),
            ),
        )
        self._event.set()

    async def on_timeout(self):
        if self.confirmed is not None:
            # Already confirmed or cancelled: the card has been (or is about to
            # be) replaced by the outcome, so it must never read as expired.
            return
        self.confirmed = False
        self._event.set()
        # A timed-out card used to keep its buttons, which then failed when
        # clicked. Replace it with an explicit expiry notice.
        if self.message is not None:
            try:
                await self.message.edit(
                    view=_info_view(
                        self.message,
                        self.text["expired_title"],
                        self.text["expired_body"],
                        colour=discord.Colour.greyple(),
                    )
                )
            except discord.HTTPException:
                pass

    async def wait_for_response(self) -> bool:
        await self._event.wait()
        return bool(self.confirmed)


class _Confirmation:
    """The confirm card, which turns into the result card.

    One message per request: the card the user pressed is edited into the
    outcome instead of a second message being posted underneath it.
    """

    def __init__(self, message: discord.Message | None, accepted: bool):
        self.message = message
        self.accepted = bool(accepted)
        self._done = False

    def __bool__(self) -> bool:
        return self.accepted

    async def finish(self, view: discord.ui.LayoutView, *, channel=None) -> None:
        """Replace the card with the outcome, falling back to a new message."""
        if self._done:
            return
        self._done = True
        if self.message is not None:
            try:
                await self.message.edit(view=view)
                return
            except discord.HTTPException as error:
                logging.warning("AI", f"Could not update the AI action card: {error!r}")
        if channel is not None:
            try:
                await channel.send(view=view)
            except discord.HTTPException:
                pass


async def _confirm(msg: discord.Message, *, title: str, body: str) -> _Confirmation:
    view = AIActionConfirmView(
        title,
        body,
        invoker_id=msg.author.id,
        text={key: t(msg, key) for key in _CONFIRM_TEXT_KEYS},
    )
    view.message = await msg.channel.send(view=view)
    return _Confirmation(view.message, await view.wait_for_response())


# ────────────────────────────────────────────────────────────────────
#  Permission + hierarchy checks
# ────────────────────────────────────────────────────────────────────

def _permissions(member: discord.Member, channel=None) -> discord.Permissions:
    """Permissions in a specific channel when one is given, else guild-level."""
    if channel is not None:
        try:
            return channel.permissions_for(member)
        except Exception:  # noqa: BLE001 - fall back to guild-level permissions
            pass
    return member.guild_permissions


def _has_perm(member: discord.Member, perm: str, *, channel=None) -> bool:
    perms = _permissions(member, channel)
    return bool(getattr(perms, perm, False) or getattr(perms, "administrator", False))


def _check_perms(msg: discord.Message, perm: str, *, channel=None):
    """Return None if both invoker and bot have ``perm``, else an error view."""
    me = getattr(msg.guild, "me", None) if msg.guild else None
    if me is None:
        return _error_view(msg, t(msg, "guild_only"))

    scope = t(msg, "perm_scope", channel=channel.mention) if channel is not None else ""
    label = _perm_label(msg, perm)
    if not _has_perm(msg.author, perm, channel=channel):
        return _error_view(msg, t(msg, "perm_user", perm=label, scope=scope))
    if not _has_perm(me, perm, channel=channel):
        return _error_view(msg, t(msg, "perm_bot", perm=label, scope=scope))
    return None


def _invoker_outranks(author: discord.Member, member: discord.Member) -> bool:
    guild = member.guild
    if author.id == guild.owner_id:
        return True
    if member.id == guild.owner_id:
        return False
    return author.top_role > member.top_role


def _member_hierarchy_error(msg: discord.Message, member: discord.Member):
    """Refuse a member action the invoker or Niko is not senior enough for."""
    guild = msg.guild
    if member.id == guild.me.id:
        return _error_view(msg, t(msg, "hierarchy_self"))
    if member.id == msg.author.id:
        return _error_view(msg, t(msg, "hierarchy_author"))
    if member.id == guild.owner_id:
        return _error_view(msg, t(msg, "hierarchy_owner"))
    if member.top_role >= guild.me.top_role:
        return _error_view(msg, t(msg, "hierarchy_member_above_bot"))
    if not _invoker_outranks(msg.author, member):
        return _error_view(msg, t(msg, "hierarchy_member_above_invoker", member=member))
    return None


def _invoker_outranks_role(author: discord.Member, role: discord.Role) -> bool:
    if author.id == author.guild.owner_id:
        return True
    return author.top_role > role


def _role_hierarchy_error(msg: discord.Message, role: discord.Role):
    guild = msg.guild
    if role.is_default():
        return _error_view(msg, t(msg, "hierarchy_everyone"))
    if role.managed:
        return _error_view(msg, t(msg, "hierarchy_role_managed", role=role.name))
    if role >= guild.me.top_role:
        return _error_view(msg, t(msg, "hierarchy_role_above_bot", role=role.name))
    if not _invoker_outranks_role(msg.author, role):
        return _error_view(msg, t(msg, "hierarchy_role_above_invoker", role=role.name))
    return None


async def _log_action(
    bot,
    msg: discord.Message,
    *,
    category: str,
    title: str,
    detail: str,
    target_id: int | None = None,
    channel_id: int | None = None,
) -> None:
    """Write an AI-performed action into Niko's own server logs.

    Log bodies stay in English: the logging cog translates the title and field
    labels when it renders an entry for a guild.
    """
    logger = bot.get_cog("ServerLogger") if bot is not None else None
    if logger is None or msg.guild is None:
        return
    body = (
        f"**Actor:** {msg.author.mention} (`{msg.author}` — ID: `{msg.author.id}`)\n"
        f"**Via:** AI Action\n"
        f"{detail}"
    )
    try:
        await logger.log_event(
            msg.guild,
            category,
            title,
            body,
            target_id=target_id,
            action_key=title,
            channel_id=channel_id,
        )
    except Exception as error:  # noqa: BLE001 - logging must not fail the action
        logging.warning("AI", f"Could not log AI action '{title}': {error}")


async def _fail(
    msg: discord.Message,
    action: str,
    error: Exception,
    *,
    card: _Confirmation | None = None,
) -> None:
    logging.error(
        "AI",
        f"AI action '{action}' failed in guild {getattr(msg.guild, 'id', None)}: {error!r}",
    )
    # "generic" is the dispatcher's catch-all: it has no action label of its
    # own, so it uses the wording that names no action.
    if action == "generic":
        view = _error_view(msg, t(msg, "fail_generic"))
    else:
        view = _error_view(msg, t(msg, "fail", label=t(msg, f"{action}.label")))
    if card is not None:
        await card.finish(view, channel=msg.channel)
    else:
        await msg.channel.send(view=view)


# ────────────────────────────────────────────────────────────────────
#  Per-action handlers
# ────────────────────────────────────────────────────────────────────

async def _do_create_poll(bot, msg: discord.Message, args: dict) -> None:
    import datetime

    err = _check_perms(msg, "send_messages", channel=msg.channel)
    if err:
        await msg.channel.send(view=err)
        return

    question = (args.get("question") or t(msg, "poll.label")).strip()[:300]
    options = [str(o).strip() for o in (args.get("options") or []) if str(o).strip()][:10]
    if len(options) < 2:
        await msg.channel.send(view=_error_view(msg, t(msg, "poll.needs_options")))
        return

    poll = discord.Poll(
        question=question,
        duration=datetime.timedelta(hours=24),
        multiple=False,
    )
    for opt in options:
        poll.add_answer(text=opt[:55])

    try:
        await msg.channel.send(poll=poll)
    except discord.HTTPException:
        # Fallback: legacy reaction poll (for channels that don't support native polls)
        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        lines = [f"**📊 {question}**\n"]
        for i, opt in enumerate(options[:9]):
            lines.append(f"{number_emojis[i]} {opt}")
        poll_msg = await msg.channel.send("\n".join(lines))
        for i in range(min(len(options), 9)):
            try:
                await poll_msg.add_reaction(number_emojis[i])
            except Exception:  # noqa: BLE001
                pass


# ── Moderation actions ──────────────────────────────────────────────

async def _do_kick_member(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "kick_members")
    if err:
        await msg.channel.send(view=err)
        return
    member = await _resolve_member(msg.guild, args.get("user"))
    if not member:
        await msg.channel.send(view=_error_view(msg, t(msg, "member_missing", query=args.get("user"))))
        return
    err = _member_hierarchy_error(msg, member)
    if err:
        await msg.channel.send(view=err)
        return

    reason = (args.get("reason") or t(msg, "no_reason")).strip()[:400]
    body = t(msg, "kick.confirm", member=member, id=member.id, reason=reason)
    card = await _confirm(msg, title=t(msg, "kick.confirm_title"), body=body)
    if not card:
        return
    try:
        await member.kick(reason=f"AI Action by {msg.author}: {reason}")
    except discord.HTTPException as error:
        await _fail(msg, "kick", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="moderation", title="Kick",
        detail=f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n**Reason:** {reason}",
        target_id=member.id,
    )
    await card.finish(_success_view(msg, t(msg, "kick.done", member=member, reason=reason)))


async def _do_ban_member(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "ban_members")
    if err:
        await msg.channel.send(view=err)
        return
    target = await _resolve_member(msg.guild, args.get("user"))
    if not target:
        target = await _resolve_user(bot, args.get("user"))
    if not target:
        await msg.channel.send(view=_error_view(msg, t(msg, "user_missing", query=args.get("user"))))
        return
    if isinstance(target, discord.Member):
        err = _member_hierarchy_error(msg, target)
        if err:
            await msg.channel.send(view=err)
            return

    reason = (args.get("reason") or t(msg, "no_reason")).strip()[:400]
    try:
        delete_days = max(0, min(7, int(args.get("delete_message_days") or 0)))
    except (TypeError, ValueError):
        delete_days = 0
    body = t(msg, "ban.confirm", target=target, id=target.id, reason=reason, days=delete_days)
    card = await _confirm(msg, title=t(msg, "ban.confirm_title"), body=body)
    if not card:
        return
    try:
        await msg.guild.ban(
            target,
            reason=f"AI Action by {msg.author}: {reason}",
            delete_message_seconds=delete_days * 86400,
        )
    except discord.HTTPException as error:
        await _fail(msg, "ban", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="moderation", title="Ban",
        detail=(
            f"**User:** {target.mention} (`{target}` — ID: `{target.id}`)\n"
            f"**Reason:** {reason}\n**Messages deleted:** {delete_days}d"
        ),
        target_id=target.id,
    )
    await card.finish(_success_view(msg, t(msg, "ban.done", target=target, reason=reason)))


async def _do_unban_user(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "ban_members")
    if err:
        await msg.channel.send(view=err)
        return
    user = await _resolve_user(bot, args.get("user"))
    if not user:
        await msg.channel.send(view=_error_view(msg, t(msg, "unban.needs_id")))
        return
    reason = (args.get("reason") or t(msg, "no_reason")).strip()[:400]
    body = t(msg, "unban.confirm", user=user, id=user.id, reason=reason)
    card = await _confirm(msg, title=t(msg, "unban.confirm_title"), body=body)
    if not card:
        return
    try:
        await msg.guild.unban(user, reason=f"AI Action by {msg.author}: {reason}")
    except discord.NotFound:
        await card.finish(_error_view(msg, t(msg, "unban.not_banned")), channel=msg.channel)
        return
    except discord.HTTPException as error:
        await _fail(msg, "unban", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="moderation", title="Unban",
        detail=f"**User:** {user.mention} (`{user}` — ID: `{user.id}`)\n**Reason:** {reason}",
        target_id=user.id,
    )
    await card.finish(_success_view(msg, t(msg, "unban.done", user=user, reason=reason)))


async def _do_timeout_member(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "moderate_members")
    if err:
        await msg.channel.send(view=err)
        return
    member = await _resolve_member(msg.guild, args.get("user"))
    if not member:
        await msg.channel.send(view=_error_view(msg, t(msg, "member_missing", query=args.get("user"))))
        return
    try:
        seconds = int(args.get("duration_seconds") or 0)
    except (TypeError, ValueError):
        seconds = 0
    if seconds <= 0 or seconds > 60 * 60 * 24 * 28:
        await msg.channel.send(view=_error_view(msg, t(msg, "timeout.bad_duration")))
        return
    err = _member_hierarchy_error(msg, member)
    if err:
        await msg.channel.send(view=err)
        return

    reason = (args.get("reason") or t(msg, "no_reason")).strip()[:400]
    body = t(msg, "timeout.confirm", member=member, seconds=seconds, reason=reason)
    card = await _confirm(msg, title=t(msg, "timeout.confirm_title"), body=body)
    if not card:
        return
    import datetime as _dt

    until = discord.utils.utcnow() + _dt.timedelta(seconds=seconds)
    try:
        await member.edit(timed_out_until=until, reason=f"AI Action by {msg.author}: {reason}")
    except discord.HTTPException as error:
        await _fail(msg, "timeout", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="moderation", title="Timeout",
        detail=(
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Duration:** {seconds}s\n**Reason:** {reason}"
        ),
        target_id=member.id,
    )
    await card.finish(
        _success_view(msg, t(msg, "timeout.done", member=member, seconds=seconds, reason=reason))
    )


async def _do_remove_timeout(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "moderate_members")
    if err:
        await msg.channel.send(view=err)
        return
    member = await _resolve_member(msg.guild, args.get("user"))
    if not member:
        await msg.channel.send(view=_error_view(msg, t(msg, "member_missing", query=args.get("user"))))
        return
    body = t(msg, "timeout_remove.confirm", member=member, id=member.id)
    card = await _confirm(msg, title=t(msg, "timeout_remove.confirm_title"), body=body)
    if not card:
        return
    try:
        await member.edit(timed_out_until=None, reason=f"AI Action by {msg.author}: remove timeout")
    except discord.HTTPException as error:
        await _fail(msg, "timeout_remove", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="moderation", title="Timeout Removed",
        detail=f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)",
        target_id=member.id,
    )
    await card.finish(_success_view(msg, t(msg, "timeout_remove.done", member=member)))


async def _do_warn_member(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "moderate_members")
    if err:
        await msg.channel.send(view=err)
        return
    member = await _resolve_member(msg.guild, args.get("user"))
    if not member:
        await msg.channel.send(view=_error_view(msg, t(msg, "member_missing", query=args.get("user"))))
        return
    utils_cog = bot.get_cog("ModerationUtils")
    if utils_cog is None or not hasattr(utils_cog, "add_warn"):
        # This used to report success without recording anything.
        await msg.channel.send(view=_error_view(msg, t(msg, "warn.storage_unavailable")))
        return
    reason = (args.get("reason") or t(msg, "no_reason")).strip()[:400]
    body = t(msg, "warn.confirm", member=member, id=member.id, reason=reason)
    card = await _confirm(msg, title=t(msg, "warn.confirm_title"), body=body)
    if not card:
        return
    try:
        await utils_cog.add_warn(msg.guild.id, member.id, msg.author.id, reason)
    except Exception as error:  # noqa: BLE001
        await _fail(msg, "warn", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="moderation", title="Warn",
        detail=f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n**Reason:** {reason}",
        target_id=member.id,
    )
    await card.finish(_success_view(msg, t(msg, "warn.done", member=member, reason=reason)))


async def _do_purge_messages(bot, msg: discord.Message, args: dict) -> None:
    try:
        amount = int(args.get("amount") or 0)
    except (TypeError, ValueError):
        amount = 0
    if amount < 1 or amount > 100:
        await msg.channel.send(view=_error_view(msg, t(msg, "purge.bad_amount")))
        return
    channel = _resolve_channel(msg.guild, args.get("channel")) or msg.channel
    if not isinstance(channel, (discord.TextChannel, discord.Thread)):
        await msg.channel.send(view=_error_view(msg, t(msg, "purge.not_text")))
        return
    err = _check_perms(msg, "manage_messages", channel=channel)
    if err:
        await msg.channel.send(view=err)
        return
    body = t(msg, "purge.confirm", amount=amount, channel=channel.mention)
    card = await _confirm(msg, title=t(msg, "purge.confirm_title"), body=body)
    if not card:
        return
    try:
        deleted = await channel.purge(limit=amount, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "purge", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="messages", title="Purge",
        detail=f"**Channel:** {channel.mention}\n**Messages deleted:** `{len(deleted)}`",
        channel_id=channel.id,
    )
    await card.finish(
        _success_view(msg, t(msg, "purge.done", count=len(deleted), channel=channel.mention))
    )


# ── Server management actions ───────────────────────────────────────

async def _do_create_channel(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "manage_channels")
    if err:
        await msg.channel.send(view=err)
        return
    # The model often echoes how the user wrote it — "#memes", "<#123>",
    # "announcements and news" — and Discord rejects those raw. Normalise
    # before validating so a good request does not fail on formatting.
    name = (args.get("name") or "").strip()
    name = _CHANNEL_MENTION_RE.sub("", name).strip().lstrip("#").strip()
    name = re.sub(r"[^\w\- ]+", "", name, flags=re.UNICODE)
    name = re.sub(r"[\s_]+", "-", name.lower()).strip("-")[:90]
    if not name:
        await msg.channel.send(view=_error_view(msg, t(msg, "channel_create.needs_name")))
        return
    ch_type = (args.get("type") or "text").strip().lower()
    if ch_type not in {"text", "voice"}:
        await msg.channel.send(view=_error_view(msg, t(msg, "channel_create.bad_type")))
        return
    topic = (args.get("topic") or "").strip()[:1024] or None
    # A category the model named but that does not exist would otherwise drop
    # the channel at the top level, silently ignoring the requested layout.
    category = _resolve_category(msg.guild, args.get("category"))
    if args.get("category") and category is None:
        known = ", ".join(f"**{c.name}**" for c in list(msg.guild.categories)[:10]) or t(
            msg, "none_listed"
        )
        await msg.channel.send(view=_error_view(
            msg,
            t(msg, "category_missing_list", query=args.get("category"), categories=known),
        ))
        return
    where = (
        t(msg, "channel_create.where_category", category=category.name)
        if category
        else t(msg, "channel_create.where_top")
    )
    body = t(
        msg, "channel_create.confirm",
        type=t(msg, f"channel_create.type_{ch_type}"),
        name=name,
        where=where,
        topic=t(msg, "channel_create.topic_line", topic=topic) if topic else "",
    )
    card = await _confirm(msg, title=t(msg, "channel_create.confirm_title"), body=body)
    if not card:
        return
    try:
        if ch_type == "voice":
            new_ch = await msg.guild.create_voice_channel(
                name=name, category=category, reason=f"AI Action by {msg.author}"
            )
        else:
            new_ch = await msg.guild.create_text_channel(
                name=name, category=category, topic=topic, reason=f"AI Action by {msg.author}"
            )
    except discord.HTTPException as error:
        await _fail(msg, "channel_create", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="channels", title="Channel Created",
        detail=f"**Channel:** {new_ch.mention} (`{name}`)\n**Type:** {ch_type}"
        + (f"\n**Category:** {category.name}" if category else ""),
        channel_id=new_ch.id,
    )
    await card.finish(
        _success_view(msg, t(msg, "channel_create.done", channel=new_ch.mention))
    )


async def _do_delete_channel(bot, msg: discord.Message, args: dict) -> None:
    channel = _resolve_channel(msg.guild, args.get("channel"))
    if not channel:
        await msg.channel.send(view=_error_view(msg, t(msg, "channel_missing", query=args.get("channel"))))
        return
    err = _check_perms(msg, "manage_channels", channel=channel)
    if err:
        await msg.channel.send(view=err)
        return
    if channel == msg.channel:
        await msg.channel.send(view=_error_view(msg, t(msg, "channel_delete.not_here")))
        return
    body = t(msg, "channel_delete.confirm", name=channel.name, id=channel.id)
    card = await _confirm(msg, title=t(msg, "channel_delete.confirm_title"), body=body)
    if not card:
        return
    try:
        await channel.delete(reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "channel_delete", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="channels", title="Channel Deleted",
        detail=f"**Channel:** `#{channel.name}` (ID: `{channel.id}`)",
        channel_id=channel.id,
    )
    await card.finish(_success_view(msg, t(msg, "channel_delete.done", name=channel.name)))


async def _do_rename_channel(bot, msg: discord.Message, args: dict) -> None:
    channel = _resolve_channel(msg.guild, args.get("channel")) or msg.channel
    err = _check_perms(msg, "manage_channels", channel=channel)
    if err:
        await msg.channel.send(view=err)
        return
    new_name = (args.get("name") or "").strip().lower().replace(" ", "-")[:90]
    if not new_name:
        await msg.channel.send(view=_error_view(msg, t(msg, "channel_rename.needs_name")))
        return
    body = t(msg, "channel_rename.confirm", old=channel.name, new=new_name)
    card = await _confirm(msg, title=t(msg, "channel_rename.confirm_title"), body=body)
    if not card:
        return
    try:
        await channel.edit(name=new_name, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "channel_rename", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="channels", title="Channel Updated",
        detail=f"**Channel:** {channel.mention}\n**Name:** `{new_name}`",
        channel_id=channel.id,
    )
    await card.finish(_success_view(msg, t(msg, "channel_rename.done", name=new_name)))


async def _do_set_channel_topic(bot, msg: discord.Message, args: dict) -> None:
    channel = _resolve_channel(msg.guild, args.get("channel")) or msg.channel
    if not isinstance(channel, discord.TextChannel):
        await msg.channel.send(view=_error_view(msg, t(msg, "topic.text_only")))
        return
    err = _check_perms(msg, "manage_channels", channel=channel)
    if err:
        await msg.channel.send(view=err)
        return
    topic = (args.get("topic") or "").strip()[:1024]
    body = t(
        msg, "topic.confirm",
        name=channel.name,
        topic=topic or t(msg, "empty"),
    )
    card = await _confirm(msg, title=t(msg, "topic.confirm_title"), body=body)
    if not card:
        return
    try:
        await channel.edit(topic=topic, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "topic", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="channels", title="Channel Updated",
        detail=f"**Channel:** {channel.mention}\n**Topic:** {topic or '*(cleared)*'}",
        channel_id=channel.id,
    )
    await card.finish(_success_view(msg, t(msg, "topic.done", name=channel.name)))


def _parse_colour(value) -> Optional[discord.Colour]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    if s.startswith("#"):
        s = s[1:]
    try:
        colour = discord.Colour(int(s, 16))
    except ValueError:
        return None
    return colour


async def _do_create_role(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "manage_roles")
    if err:
        await msg.channel.send(view=err)
        return
    name = (args.get("name") or "").strip()[:90]
    if not name:
        await msg.channel.send(view=_error_view(msg, t(msg, "role_create.needs_name")))
        return
    colour = _parse_colour(args.get("colour") or args.get("color"))
    hoist = bool(args.get("hoist"))
    mentionable = bool(args.get("mentionable"))
    # Discord appends new roles at the bottom; "above" lets the model put the
    # role where it belongs in the hierarchy the user can see.
    anchor = _resolve_role(msg.guild, args.get("above")) if args.get("above") else None
    if args.get("above") and anchor is None:
        await msg.channel.send(
            view=_error_view(msg, t(msg, "role_create.above_missing", query=args.get("above")))
        )
        return
    if anchor is not None:
        err = _role_hierarchy_error(msg, anchor)
        if err:
            await msg.channel.send(view=err)
            return
    details = ""
    if colour:
        details += t(msg, "role_create.detail_colour", colour=f"{colour.value:06x}")
    if hoist:
        details += t(msg, "role_create.detail_hoist")
    if mentionable:
        details += t(msg, "role_create.detail_mentionable")
    if anchor is not None:
        body = t(msg, "role_create.confirm_above", name=name, details=details, role=anchor.name)
    else:
        body = t(msg, "role_create.confirm", name=name, details=details)
    card = await _confirm(msg, title=t(msg, "role_create.confirm_title"), body=body)
    if not card:
        return
    try:
        kwargs = {
            "name": name,
            "hoist": hoist,
            "mentionable": mentionable,
            "reason": f"AI Action by {msg.author}",
        }
        if colour is not None:
            kwargs["colour"] = colour
        new_role = await msg.guild.create_role(**kwargs)
        if anchor is not None:
            await new_role.edit(position=anchor.position, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "role_create", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="roles", title="Role Created",
        detail=f"**Role:** {new_role.mention} (`{name}`)"
        + (f"\n**Placed above:** {anchor.name}" if anchor else ""),
    )
    await card.finish(_success_view(msg, t(msg, "role_create.done", role=new_role.mention)))


async def _do_delete_role(bot, msg: discord.Message, args: dict) -> None:
    role = _resolve_role(msg.guild, args.get("role"))
    if not role:
        await msg.channel.send(view=_error_view(msg, t(msg, "role_missing", query=args.get("role"))))
        return
    err = _check_perms(msg, "manage_roles")
    if err:
        await msg.channel.send(view=err)
        return
    err = _role_hierarchy_error(msg, role)
    if err:
        await msg.channel.send(view=err)
        return
    body = t(msg, "role_delete.confirm", name=role.name, id=role.id)
    card = await _confirm(msg, title=t(msg, "role_delete.confirm_title"), body=body)
    if not card:
        return
    try:
        await role.delete(reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "role_delete", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="roles", title="Role Deleted",
        detail=f"**Role:** `{role.name}` (ID: `{role.id}`)",
    )
    await card.finish(_success_view(msg, t(msg, "role_delete.done", name=role.name)))


def _hex_colour(ctx, colour) -> str:
    return f"#{colour.value:06x}" if getattr(colour, "value", 0) else t(ctx, "colour_default")


async def _do_edit_role(bot, msg: discord.Message, args: dict) -> None:
    role = _resolve_role(msg.guild, args.get("role"))
    if not role:
        await msg.channel.send(view=_error_view(msg, t(msg, "role_missing", query=args.get("role"))))
        return
    err = _check_perms(msg, "manage_roles")
    if err:
        await msg.channel.send(view=err)
        return
    err = _role_hierarchy_error(msg, role)
    if err:
        await msg.channel.send(view=err)
        return

    # Only the properties the model actually sent are compared, so an edit that
    # matches the current role does nothing instead of re-writing it.
    changes: dict = {}
    lines: list[str] = []
    if "name" in args:
        new_name = (args.get("name") or "").strip()[:90]
        if not new_name:
            await msg.channel.send(view=_error_view(msg, t(msg, "role_edit.empty_name")))
            return
        if new_name != role.name:
            changes["name"] = new_name
            lines.append(t(msg, "role_edit.line_name", old=role.name, new=new_name))
    if "colour" in args or "color" in args:
        raw = args["colour"] if "colour" in args else args["color"]
        colour = _parse_colour(raw)
        if colour is None and str(raw or "").strip().lower() not in {"", "default", "none", "clear"}:
            await msg.channel.send(
                view=_error_view(msg, t(msg, "role_edit.bad_colour", value=raw))
            )
            return
        new_colour = colour or discord.Colour.default()
        if new_colour != role.colour:
            changes["colour"] = new_colour
            lines.append(t(
                msg, "role_edit.line_colour",
                old=_hex_colour(msg, role.colour),
                new=_hex_colour(msg, new_colour),
            ))
    for flag, label_key in (("hoist", "role_edit.flag_hoist"), ("mentionable", "role_edit.flag_mentionable")):
        if flag in args:
            value = bool(args.get(flag))
            if value != getattr(role, flag):
                changes[flag] = value
                lines.append(t(
                    msg, "role_edit.line_flag",
                    flag=t(msg, label_key),
                    value=t(msg, "yes") if value else t(msg, "no"),
                ))
    if not changes:
        await msg.channel.send(view=_info_view(
            msg,
            t(msg, "nothing_to_change_title"),
            t(msg, "nothing_to_change_body", role=role.name),
            colour=discord.Colour.greyple(),
        ))
        return

    body = t(msg, "role_edit.confirm", role=role.name, changes="\n".join(lines))
    card = await _confirm(msg, title=t(msg, "role_edit.confirm_title"), body=body)
    if not card:
        return
    try:
        await role.edit(**changes, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "role_edit", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="roles", title="Role Updated",
        detail=f"**Role:** {role.mention} (`{role.name}`)\n" + "\n".join(lines),
    )
    await card.finish(_success_view(msg, t(msg, "role_edit.done", role=role.mention)))


async def _do_assign_role(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "manage_roles")
    if err:
        await msg.channel.send(view=err)
        return
    member = await _resolve_member(msg.guild, args.get("user"))
    role = _resolve_role(msg.guild, args.get("role"))
    if not member or not role:
        await msg.channel.send(view=_error_view(msg, t(msg, "role_assign.missing")))
        return
    err = _role_hierarchy_error(msg, role)
    if err:
        await msg.channel.send(view=err)
        return
    body = t(msg, "role_assign.confirm", role=role.name, member=member)
    card = await _confirm(msg, title=t(msg, "role_assign.confirm_title"), body=body)
    if not card:
        return
    try:
        await member.add_roles(role, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "role_assign", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="roles", title="Role Assigned",
        detail=f"**Member:** {member.mention} (`{member.id}`)\n**Role:** {role.mention}",
        target_id=member.id,
    )
    await card.finish(
        _success_view(msg, t(msg, "role_assign.done", role=role.name, member=member))
    )


async def _do_remove_role(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "manage_roles")
    if err:
        await msg.channel.send(view=err)
        return
    member = await _resolve_member(msg.guild, args.get("user"))
    role = _resolve_role(msg.guild, args.get("role"))
    if not member or not role:
        await msg.channel.send(view=_error_view(msg, t(msg, "role_remove.missing")))
        return
    err = _role_hierarchy_error(msg, role)
    if err:
        await msg.channel.send(view=err)
        return
    body = t(msg, "role_remove.confirm", role=role.name, member=member)
    card = await _confirm(msg, title=t(msg, "role_remove.confirm_title"), body=body)
    if not card:
        return
    try:
        await member.remove_roles(role, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "role_remove", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="roles", title="Role Removed",
        detail=f"**Member:** {member.mention} (`{member.id}`)\n**Role:** {role.mention}",
        target_id=member.id,
    )
    await card.finish(
        _success_view(msg, t(msg, "role_remove.done", role=role.name, member=member))
    )


async def _do_change_nickname(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "manage_nicknames")
    if err:
        await msg.channel.send(view=err)
        return
    member = await _resolve_member(msg.guild, args.get("user"))
    if not member:
        await msg.channel.send(view=_error_view(msg, t(msg, "member_missing", query=args.get("user"))))
        return
    if "nickname" not in args:
        # The tool schema requires it now; an omitted value used to silently
        # reset the member's nickname.
        await msg.channel.send(view=_error_view(msg, t(msg, "nickname.needs_value")))
        return
    nickname = args.get("nickname")
    nickname = nickname.strip()[:32] if isinstance(nickname, str) else None
    if nickname == "":
        nickname = None
    body = t(
        msg, "nickname.confirm",
        member=member,
        nickname=nickname or t(msg, "nickname.reset_placeholder"),
    )
    card = await _confirm(msg, title=t(msg, "nickname.confirm_title"), body=body)
    if not card:
        return
    try:
        await member.edit(nick=nickname, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "nickname", error, card=card)
        return
    await _log_action(
        bot, msg,
        category="moderation", title="Nickname Changed",
        detail=f"**Member:** {member.mention} (`{member.id}`)\n**New nickname:** `{nickname or '(reset)'}`",
        target_id=member.id,
    )
    await card.finish(_success_view(msg, t(msg, "nickname.done", member=member)))


# ────────────────────────────────────────────────────────────────────
#  Dispatcher
# ────────────────────────────────────────────────────────────────────

_HANDLERS = {
    # Non-destructive (no confirmation, still permission-checked)
    "create_poll": _do_create_poll,

    # Moderation
    "kick_member": _do_kick_member,
    "ban_member": _do_ban_member,
    "unban_user": _do_unban_user,
    "timeout_member": _do_timeout_member,
    "remove_timeout": _do_remove_timeout,
    "warn_member": _do_warn_member,
    "purge_messages": _do_purge_messages,

    # Server management
    "create_channel": _do_create_channel,
    "delete_channel": _do_delete_channel,
    "rename_channel": _do_rename_channel,
    "set_channel_topic": _do_set_channel_topic,
    "create_role": _do_create_role,
    "edit_role": _do_edit_role,
    "delete_role": _do_delete_role,
    "assign_role": _do_assign_role,
    "remove_role": _do_remove_role,
    "change_nickname": _do_change_nickname,
}


async def dispatch_ai_action(bot, msg: discord.Message, action: dict) -> None:
    """Route a structured AI Action dict to its handler.

    Handlers own their CV2 responses: the confirmation card is edited into the
    success, error or cancelled state, so the caller doesn't need to do
    anything else after awaiting this.
    """
    name = (action.get("action") or "").strip()
    handler = _HANDLERS.get(name)
    if handler is None:
        logging.warning("AI", f"Model requested an unknown action '{name}'")
        await msg.channel.send(view=_error_view(msg, t(msg, "unknown_action")))
        return

    try:
        await handler(bot, msg, action)
    except discord.Forbidden as error:
        await _fail(msg, "generic", error)
    except Exception as error:  # noqa: BLE001
        await _fail(msg, "generic", error)
