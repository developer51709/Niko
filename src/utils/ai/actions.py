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
    happen. Only the requesting user can confirm or cancel, and the card expires.

``create_poll`` is the one non-destructive action: it skips the confirmation but
still requires Send Messages in the channel.

Every completed action is also written to Niko's own moderation/channel logs.
"""

from __future__ import annotations

import asyncio
import re
from typing import Optional

import discord

from config.emojis import get_emoji
from utils import logging


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


def _resolve_channel(guild: discord.Guild, value) -> Optional[discord.abc.GuildChannel]:
    if value is None:
        return None
    cid = _coerce_id(value)
    if cid:
        ch = guild.get_channel(cid)
        if ch:
            return ch
    name = str(value).strip().lstrip("#").lower()
    if not name:
        return None
    for ch in guild.channels:
        if ch.name.lower() == name:
            return ch
    return None


def _resolve_role(guild: discord.Guild, value) -> Optional[discord.Role]:
    if value is None:
        return None
    rid = _coerce_id(value)
    if rid:
        r = guild.get_role(rid)
        if r:
            return r
    name = str(value).strip().lstrip("@").lower()
    if not name:
        return None
    for r in guild.roles:
        if r.name.lower() == name:
            return r
    return None


# ────────────────────────────────────────────────────────────────────
#  CV2 helpers — confirmation view, success/error notifications
# ────────────────────────────────────────────────────────────────────

def _info_view(
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


def _error_view(body: str) -> discord.ui.LayoutView:
    return _info_view(f"{get_emoji('danger')} AI Action Refused", body, colour=discord.Colour.red())


def _success_view(body: str) -> discord.ui.LayoutView:
    return _info_view(f"{get_emoji('tick')} AI Action Completed", body, colour=discord.Colour.green())


class AIActionConfirmView(discord.ui.LayoutView):
    """LayoutView with Confirm + Cancel buttons gated to the invoker."""

    def __init__(self, title: str, body: str, *, invoker_id: int, timeout: float = 45.0):
        super().__init__(timeout=timeout)
        self.invoker_id = invoker_id
        self.confirmed: bool | None = None
        self.message: discord.Message | None = None
        self._event = asyncio.Event()

        self._confirm = discord.ui.Button(
            label="Confirm",
            style=discord.ButtonStyle.danger,
            emoji=get_emoji("tick") or "✅",
        )
        self._cancel = discord.ui.Button(
            label="Cancel",
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
            discord.ui.TextDisplay(content="-# Niko will only proceed if you confirm. This prompt expires in 45s."),
            discord.ui.ActionRow(self._confirm, self._cancel),
            accent_colour=discord.Colour.orange(),
        ))

    async def _gate(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.invoker_id:
            await interaction.response.send_message(
                view=_error_view("Only the person who asked Niko to do this can confirm or cancel."),
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
        await self._disable_buttons()
        await interaction.response.edit_message(view=self)
        self._event.set()

    async def _on_cancel(self, interaction: discord.Interaction):
        if not await self._gate(interaction):
            return
        self.confirmed = False
        await self._disable_buttons()
        await interaction.response.edit_message(
            view=_info_view(
                f"{get_emoji('cross')} Cancelled",
                "Niko didn't do anything.",
                colour=discord.Colour.greyple(),
            ),
        )
        self._event.set()

    async def on_timeout(self):
        if self.confirmed is None:
            self.confirmed = False
        self._event.set()
        # A timed-out card used to keep its buttons, which then failed when
        # clicked. Replace it with an explicit expiry notice.
        if self.message is not None:
            try:
                await self.message.edit(
                    view=_info_view(
                        "Request expired",
                        "Nobody confirmed this action in time, so Niko did nothing.",
                        colour=discord.Colour.greyple(),
                    )
                )
            except discord.HTTPException:
                pass

    async def wait_for_response(self) -> bool:
        await self._event.wait()
        return bool(self.confirmed)


async def _confirm(channel, *, title: str, body: str, invoker_id: int) -> bool:
    view = AIActionConfirmView(title, body, invoker_id=invoker_id)
    view.message = await channel.send(view=view)
    return await view.wait_for_response()


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


def _check_perms(msg: discord.Message, perm: str, *, action_label: str, channel=None):
    """Return None if both invoker and bot have ``perm``, else an error view."""
    me = getattr(msg.guild, "me", None) if msg.guild else None
    if me is None:
        return _error_view("AI Actions can only run inside a server.")

    scope = f" in {channel.mention}" if channel is not None else ""
    label = perm.replace("_", " ").title()
    if not _has_perm(msg.author, perm, channel=channel):
        return _error_view(
            f"You need the **{label}** permission{scope} to ask Niko to {action_label}."
        )
    if not _has_perm(me, perm, channel=channel):
        return _error_view(
            f"Niko doesn't have the **{label}** permission{scope} needed to {action_label}."
        )
    return None


def _invoker_outranks(author: discord.Member, member: discord.Member) -> bool:
    guild = member.guild
    if author.id == guild.owner_id:
        return True
    if member.id == guild.owner_id:
        return False
    return author.top_role > member.top_role


def _member_hierarchy_error(msg: discord.Message, member: discord.Member, *, action_label: str):
    """Refuse a member action the invoker or Niko is not senior enough for."""
    guild = msg.guild
    if member.id == guild.me.id:
        return _error_view(f"I won't {action_label} myself.")
    if member.id == msg.author.id:
        return _error_view(f"I won't {action_label} you.")
    if member.id == guild.owner_id:
        return _error_view(f"I can't {action_label} the server owner.")
    if member.top_role >= guild.me.top_role:
        return _error_view(
            f"That member's role is higher than or equal to mine — I can't {action_label} them."
        )
    if not _invoker_outranks(msg.author, member):
        return _error_view(
            f"You can't {action_label} **{member}** — their role is equal to or above your highest role."
        )
    return None


def _invoker_outranks_role(author: discord.Member, role: discord.Role) -> bool:
    if author.id == author.guild.owner_id:
        return True
    return author.top_role > role


def _role_hierarchy_error(msg: discord.Message, role: discord.Role, *, action_label: str):
    guild = msg.guild
    if role.is_default():
        return _error_view(f"I can't {action_label} the @everyone role.")
    if role.managed:
        return _error_view(f"I can't {action_label} **{role.name}** — it's managed by an integration.")
    if role >= guild.me.top_role:
        return _error_view(
            f"I can't {action_label} **{role.name}** — it's equal to or above my highest role."
        )
    if not _invoker_outranks_role(msg.author, role):
        return _error_view(
            f"You can't {action_label} **{role.name}** — it's equal to or above your highest role."
        )
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
    """Write an AI-performed action into Niko's own server logs."""
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


async def _fail(msg: discord.Message, action: str, error: Exception) -> None:
    logging.error(
        "AI",
        f"AI action '{action}' failed in guild {getattr(msg.guild, 'id', None)}: {error!r}",
    )
    await msg.channel.send(
        view=_error_view(
            f"I couldn't {action}. Check that I still have the required permissions and try again."
        )
    )


# ────────────────────────────────────────────────────────────────────
#  Per-action handlers
# ────────────────────────────────────────────────────────────────────

async def _do_create_poll(bot, msg: discord.Message, args: dict) -> None:
    import datetime

    err = _check_perms(
        msg, "send_messages", action_label="post a poll", channel=msg.channel
    )
    if err:
        await msg.channel.send(view=err)
        return

    question = (args.get("question") or "Poll").strip()[:300]
    options = [str(o).strip() for o in (args.get("options") or []) if str(o).strip()][:10]
    if len(options) < 2:
        await msg.channel.send(view=_error_view("A poll needs at least two options."))
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
    err = _check_perms(msg, "kick_members", action_label="kick a member")
    if err:
        await msg.channel.send(view=err)
        return
    member = await _resolve_member(msg.guild, args.get("user"))
    if not member:
        await msg.channel.send(view=_error_view(f"I couldn't find a member matching `{args.get('user')}`."))
        return
    err = _member_hierarchy_error(msg, member, action_label="kick")
    if err:
        await msg.channel.send(view=err)
        return

    reason = (args.get("reason") or "No reason provided").strip()[:400]
    body = f"Kick **{member}** (`{member.id}`)?\n**Reason:** {reason}"
    if not await _confirm(msg.channel, title="Confirm Kick", body=body, invoker_id=msg.author.id):
        return
    try:
        await member.kick(reason=f"AI Action by {msg.author}: {reason}")
    except discord.HTTPException as error:
        await _fail(msg, "kick that member", error)
        return
    await _log_action(
        bot, msg,
        category="moderation", title="Kick",
        detail=f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n**Reason:** {reason}",
        target_id=member.id,
    )
    await msg.channel.send(view=_success_view(f"Kicked **{member}** — {reason}"))


async def _do_ban_member(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "ban_members", action_label="ban a member")
    if err:
        await msg.channel.send(view=err)
        return
    target = await _resolve_member(msg.guild, args.get("user"))
    if not target:
        target = await _resolve_user(bot, args.get("user"))
    if not target:
        await msg.channel.send(view=_error_view(f"I couldn't find a user matching `{args.get('user')}`."))
        return
    if isinstance(target, discord.Member):
        err = _member_hierarchy_error(msg, target, action_label="ban")
        if err:
            await msg.channel.send(view=err)
            return

    reason = (args.get("reason") or "No reason provided").strip()[:400]
    try:
        delete_days = max(0, min(7, int(args.get("delete_message_days") or 0)))
    except (TypeError, ValueError):
        delete_days = 0
    body = (
        f"Ban **{target}** (`{target.id}`)?\n"
        f"**Reason:** {reason}\n"
        f"**Delete messages from last:** {delete_days}d"
    )
    if not await _confirm(msg.channel, title="Confirm Ban", body=body, invoker_id=msg.author.id):
        return
    try:
        await msg.guild.ban(
            target,
            reason=f"AI Action by {msg.author}: {reason}",
            delete_message_seconds=delete_days * 86400,
        )
    except discord.HTTPException as error:
        await _fail(msg, "ban that user", error)
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
    await msg.channel.send(view=_success_view(f"Banned **{target}** — {reason}"))


async def _do_unban_user(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "ban_members", action_label="unban a user")
    if err:
        await msg.channel.send(view=err)
        return
    user = await _resolve_user(bot, args.get("user"))
    if not user:
        await msg.channel.send(view=_error_view("Provide a user ID to unban."))
        return
    reason = (args.get("reason") or "No reason provided").strip()[:400]
    body = f"Unban **{user}** (`{user.id}`)?\n**Reason:** {reason}"
    if not await _confirm(msg.channel, title="Confirm Unban", body=body, invoker_id=msg.author.id):
        return
    try:
        await msg.guild.unban(user, reason=f"AI Action by {msg.author}: {reason}")
    except discord.NotFound:
        await msg.channel.send(view=_error_view("That user is not banned."))
        return
    except discord.HTTPException as error:
        await _fail(msg, "unban that user", error)
        return
    await _log_action(
        bot, msg,
        category="moderation", title="Unban",
        detail=f"**User:** {user.mention} (`{user}` — ID: `{user.id}`)\n**Reason:** {reason}",
        target_id=user.id,
    )
    await msg.channel.send(view=_success_view(f"Unbanned **{user}** — {reason}"))


async def _do_timeout_member(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "moderate_members", action_label="time-out a member")
    if err:
        await msg.channel.send(view=err)
        return
    member = await _resolve_member(msg.guild, args.get("user"))
    if not member:
        await msg.channel.send(view=_error_view(f"I couldn't find a member matching `{args.get('user')}`."))
        return
    try:
        seconds = int(args.get("duration_seconds") or 0)
    except (TypeError, ValueError):
        seconds = 0
    if seconds <= 0 or seconds > 60 * 60 * 24 * 28:
        await msg.channel.send(view=_error_view("Duration must be between 1 second and 28 days."))
        return
    err = _member_hierarchy_error(msg, member, action_label="time out")
    if err:
        await msg.channel.send(view=err)
        return

    reason = (args.get("reason") or "No reason provided").strip()[:400]
    body = f"Time out **{member}** for **{seconds}s**?\n**Reason:** {reason}"
    if not await _confirm(msg.channel, title="Confirm Timeout", body=body, invoker_id=msg.author.id):
        return
    import datetime as _dt

    until = discord.utils.utcnow() + _dt.timedelta(seconds=seconds)
    try:
        await member.edit(timed_out_until=until, reason=f"AI Action by {msg.author}: {reason}")
    except discord.HTTPException as error:
        await _fail(msg, "time out that member", error)
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
    await msg.channel.send(view=_success_view(f"Timed out **{member}** for {seconds}s — {reason}"))


async def _do_remove_timeout(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "moderate_members", action_label="remove a member's time-out")
    if err:
        await msg.channel.send(view=err)
        return
    member = await _resolve_member(msg.guild, args.get("user"))
    if not member:
        await msg.channel.send(view=_error_view(f"I couldn't find a member matching `{args.get('user')}`."))
        return
    body = f"Remove the time-out on **{member}** (`{member.id}`)?"
    if not await _confirm(msg.channel, title="Confirm Remove Timeout", body=body, invoker_id=msg.author.id):
        return
    try:
        await member.edit(timed_out_until=None, reason=f"AI Action by {msg.author}: remove timeout")
    except discord.HTTPException as error:
        await _fail(msg, "remove that time-out", error)
        return
    await _log_action(
        bot, msg,
        category="moderation", title="Timeout Removed",
        detail=f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)",
        target_id=member.id,
    )
    await msg.channel.send(view=_success_view(f"Removed time-out on **{member}**."))


async def _do_warn_member(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "moderate_members", action_label="warn a member")
    if err:
        await msg.channel.send(view=err)
        return
    member = await _resolve_member(msg.guild, args.get("user"))
    if not member:
        await msg.channel.send(view=_error_view(f"I couldn't find a member matching `{args.get('user')}`."))
        return
    utils_cog = bot.get_cog("ModerationUtils")
    if utils_cog is None or not hasattr(utils_cog, "add_warn"):
        # This used to report success without recording anything.
        await msg.channel.send(view=_error_view("Warning storage is unavailable right now."))
        return
    reason = (args.get("reason") or "No reason provided").strip()[:400]
    body = f"Warn **{member}** (`{member.id}`)?\n**Reason:** {reason}"
    if not await _confirm(msg.channel, title="Confirm Warn", body=body, invoker_id=msg.author.id):
        return
    try:
        await utils_cog.add_warn(msg.guild.id, member.id, msg.author.id, reason)
    except Exception as error:  # noqa: BLE001
        await _fail(msg, "record that warning", error)
        return
    await _log_action(
        bot, msg,
        category="moderation", title="Warn",
        detail=f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n**Reason:** {reason}",
        target_id=member.id,
    )
    await msg.channel.send(view=_success_view(f"Warned **{member}** — {reason}"))


async def _do_purge_messages(bot, msg: discord.Message, args: dict) -> None:
    try:
        amount = int(args.get("amount") or 0)
    except (TypeError, ValueError):
        amount = 0
    if amount < 1 or amount > 100:
        await msg.channel.send(view=_error_view("Amount must be between 1 and 100."))
        return
    channel = _resolve_channel(msg.guild, args.get("channel")) or msg.channel
    if not isinstance(channel, (discord.TextChannel, discord.Thread)):
        await msg.channel.send(view=_error_view("I can only purge messages from text channels or threads."))
        return
    err = _check_perms(msg, "manage_messages", action_label="purge messages", channel=channel)
    if err:
        await msg.channel.send(view=err)
        return
    body = f"Delete the last **{amount}** messages in {channel.mention}?"
    if not await _confirm(msg.channel, title="Confirm Purge", body=body, invoker_id=msg.author.id):
        return
    try:
        deleted = await channel.purge(limit=amount, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "purge those messages", error)
        return
    await _log_action(
        bot, msg,
        category="messages", title="Purge",
        detail=f"**Channel:** {channel.mention}\n**Messages deleted:** `{len(deleted)}`",
        channel_id=channel.id,
    )
    await msg.channel.send(view=_success_view(f"Deleted **{len(deleted)}** message(s) in {channel.mention}."))


# ── Server management actions ───────────────────────────────────────

async def _do_create_channel(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "manage_channels", action_label="create a channel")
    if err:
        await msg.channel.send(view=err)
        return
    name = (args.get("name") or "").strip().lower().replace(" ", "-")[:90]
    if not name:
        await msg.channel.send(view=_error_view("Channel name is required."))
        return
    ch_type = (args.get("type") or "text").strip().lower()
    if ch_type not in {"text", "voice"}:
        await msg.channel.send(view=_error_view("Channel type must be `text` or `voice`."))
        return
    topic = (args.get("topic") or "").strip()[:1024] or None
    category_val = args.get("category")
    category = _resolve_channel(msg.guild, category_val) if category_val else None
    if category and not isinstance(category, discord.CategoryChannel):
        category = None
    body = (
        f"Create a new **{ch_type}** channel named **#{name}**"
        + (f" in category **{category.name}**" if category else "")
        + (f"\n**Topic:** {topic}" if topic else "")
        + "?"
    )
    if not await _confirm(msg.channel, title="Confirm Create Channel", body=body, invoker_id=msg.author.id):
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
        await _fail(msg, "create that channel", error)
        return
    await _log_action(
        bot, msg,
        category="channels", title="Channel Created",
        detail=f"**Channel:** {new_ch.mention} (`{name}`)\n**Type:** {ch_type}",
        channel_id=new_ch.id,
    )
    await msg.channel.send(view=_success_view(f"Created {new_ch.mention}."))


async def _do_delete_channel(bot, msg: discord.Message, args: dict) -> None:
    channel = _resolve_channel(msg.guild, args.get("channel"))
    if not channel:
        await msg.channel.send(view=_error_view(f"I couldn't find a channel matching `{args.get('channel')}`."))
        return
    err = _check_perms(msg, "manage_channels", action_label="delete a channel", channel=channel)
    if err:
        await msg.channel.send(view=err)
        return
    if channel == msg.channel:
        await msg.channel.send(view=_error_view(
            "I won't delete the channel this conversation is happening in — run the request from a different channel if you really want to."
        ))
        return
    body = f"Delete the channel **#{channel.name}** (`{channel.id}`)?\n*This cannot be undone.*"
    if not await _confirm(msg.channel, title="Confirm Delete Channel", body=body, invoker_id=msg.author.id):
        return
    try:
        await channel.delete(reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "delete that channel", error)
        return
    await _log_action(
        bot, msg,
        category="channels", title="Channel Deleted",
        detail=f"**Channel:** `#{channel.name}` (ID: `{channel.id}`)",
        channel_id=channel.id,
    )
    await msg.channel.send(view=_success_view(f"Deleted channel **#{channel.name}**."))


async def _do_rename_channel(bot, msg: discord.Message, args: dict) -> None:
    channel = _resolve_channel(msg.guild, args.get("channel")) or msg.channel
    err = _check_perms(msg, "manage_channels", action_label="rename a channel", channel=channel)
    if err:
        await msg.channel.send(view=err)
        return
    new_name = (args.get("name") or "").strip().lower().replace(" ", "-")[:90]
    if not new_name:
        await msg.channel.send(view=_error_view("New channel name is required."))
        return
    body = f"Rename **#{channel.name}** → **#{new_name}**?"
    if not await _confirm(msg.channel, title="Confirm Rename Channel", body=body, invoker_id=msg.author.id):
        return
    try:
        await channel.edit(name=new_name, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "rename that channel", error)
        return
    await _log_action(
        bot, msg,
        category="channels", title="Channel Updated",
        detail=f"**Channel:** {channel.mention}\n**Name:** `{new_name}`",
        channel_id=channel.id,
    )
    await msg.channel.send(view=_success_view(f"Renamed channel to **#{new_name}**."))


async def _do_set_channel_topic(bot, msg: discord.Message, args: dict) -> None:
    channel = _resolve_channel(msg.guild, args.get("channel")) or msg.channel
    if not isinstance(channel, discord.TextChannel):
        await msg.channel.send(view=_error_view("Topics can only be set on text channels."))
        return
    err = _check_perms(msg, "manage_channels", action_label="change a channel topic", channel=channel)
    if err:
        await msg.channel.send(view=err)
        return
    topic = (args.get("topic") or "").strip()[:1024]
    body = f"Set topic of **#{channel.name}** to:\n> {topic or '(empty)'}"
    if not await _confirm(msg.channel, title="Confirm Set Topic", body=body, invoker_id=msg.author.id):
        return
    try:
        await channel.edit(topic=topic, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "set that topic", error)
        return
    await _log_action(
        bot, msg,
        category="channels", title="Channel Updated",
        detail=f"**Channel:** {channel.mention}\n**Topic:** {topic or '*(cleared)*'}",
        channel_id=channel.id,
    )
    await msg.channel.send(view=_success_view(f"Updated topic for **#{channel.name}**."))


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
    err = _check_perms(msg, "manage_roles", action_label="create a role")
    if err:
        await msg.channel.send(view=err)
        return
    name = (args.get("name") or "").strip()[:90]
    if not name:
        await msg.channel.send(view=_error_view("Role name is required."))
        return
    colour = _parse_colour(args.get("colour") or args.get("color"))
    hoist = bool(args.get("hoist"))
    mentionable = bool(args.get("mentionable"))
    body = (
        f"Create role **{name}**"
        + (f" (colour `#{colour.value:06x}`)" if colour else "")
        + (" *hoisted*" if hoist else "")
        + (" *mentionable*" if mentionable else "")
        + "?"
    )
    if not await _confirm(msg.channel, title="Confirm Create Role", body=body, invoker_id=msg.author.id):
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
    except discord.HTTPException as error:
        await _fail(msg, "create that role", error)
        return
    await _log_action(
        bot, msg,
        category="roles", title="Role Created",
        detail=f"**Role:** {new_role.mention} (`{name}`)",
    )
    await msg.channel.send(view=_success_view(f"Created role {new_role.mention}."))


async def _do_delete_role(bot, msg: discord.Message, args: dict) -> None:
    role = _resolve_role(msg.guild, args.get("role"))
    if not role:
        await msg.channel.send(view=_error_view(f"I couldn't find a role matching `{args.get('role')}`."))
        return
    err = _check_perms(msg, "manage_roles", action_label="delete a role")
    if err:
        await msg.channel.send(view=err)
        return
    err = _role_hierarchy_error(msg, role, action_label="delete")
    if err:
        await msg.channel.send(view=err)
        return
    body = f"Delete the role **{role.name}** (`{role.id}`)?\n*This cannot be undone.*"
    if not await _confirm(msg.channel, title="Confirm Delete Role", body=body, invoker_id=msg.author.id):
        return
    try:
        await role.delete(reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "delete that role", error)
        return
    await _log_action(
        bot, msg,
        category="roles", title="Role Deleted",
        detail=f"**Role:** `{role.name}` (ID: `{role.id}`)",
    )
    await msg.channel.send(view=_success_view(f"Deleted role **{role.name}**."))


async def _do_assign_role(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "manage_roles", action_label="assign a role")
    if err:
        await msg.channel.send(view=err)
        return
    member = await _resolve_member(msg.guild, args.get("user"))
    role = _resolve_role(msg.guild, args.get("role"))
    if not member or not role:
        await msg.channel.send(view=_error_view("I couldn't resolve both the member and the role."))
        return
    err = _role_hierarchy_error(msg, role, action_label="assign")
    if err:
        await msg.channel.send(view=err)
        return
    body = f"Give the role **{role.name}** to **{member}**?"
    if not await _confirm(msg.channel, title="Confirm Assign Role", body=body, invoker_id=msg.author.id):
        return
    try:
        await member.add_roles(role, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "assign that role", error)
        return
    await _log_action(
        bot, msg,
        category="roles", title="Role Assigned",
        detail=f"**Member:** {member.mention} (`{member.id}`)\n**Role:** {role.mention}",
        target_id=member.id,
    )
    await msg.channel.send(view=_success_view(f"Gave **{role.name}** to **{member}**."))


async def _do_remove_role(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "manage_roles", action_label="remove a role")
    if err:
        await msg.channel.send(view=err)
        return
    member = await _resolve_member(msg.guild, args.get("user"))
    role = _resolve_role(msg.guild, args.get("role"))
    if not member or not role:
        await msg.channel.send(view=_error_view("I couldn't resolve both the member and the role."))
        return
    err = _role_hierarchy_error(msg, role, action_label="remove")
    if err:
        await msg.channel.send(view=err)
        return
    body = f"Remove the role **{role.name}** from **{member}**?"
    if not await _confirm(msg.channel, title="Confirm Remove Role", body=body, invoker_id=msg.author.id):
        return
    try:
        await member.remove_roles(role, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "remove that role", error)
        return
    await _log_action(
        bot, msg,
        category="roles", title="Role Removed",
        detail=f"**Member:** {member.mention} (`{member.id}`)\n**Role:** {role.mention}",
        target_id=member.id,
    )
    await msg.channel.send(view=_success_view(f"Removed **{role.name}** from **{member}**."))


async def _do_change_nickname(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "manage_nicknames", action_label="change a nickname")
    if err:
        await msg.channel.send(view=err)
        return
    member = await _resolve_member(msg.guild, args.get("user"))
    if not member:
        await msg.channel.send(view=_error_view(f"I couldn't find a member matching `{args.get('user')}`."))
        return
    if "nickname" not in args:
        # The tool schema requires it now; an omitted value used to silently
        # reset the member's nickname.
        await msg.channel.send(view=_error_view("Tell me the new nickname (an empty string resets it)."))
        return
    nickname = args.get("nickname")
    nickname = nickname.strip()[:32] if isinstance(nickname, str) else None
    if nickname == "":
        nickname = None
    body = f"Change **{member}**'s nickname to **{nickname or '(reset to username)'}**?"
    if not await _confirm(msg.channel, title="Confirm Change Nickname", body=body, invoker_id=msg.author.id):
        return
    try:
        await member.edit(nick=nickname, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as error:
        await _fail(msg, "change that nickname", error)
        return
    await _log_action(
        bot, msg,
        category="moderation", title="Nickname Changed",
        detail=f"**Member:** {member.mention} (`{member.id}`)\n**New nickname:** `{nickname or '(reset)'}`",
        target_id=member.id,
    )
    await msg.channel.send(view=_success_view(f"Updated nickname for **{member}**."))


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
    "delete_role": _do_delete_role,
    "assign_role": _do_assign_role,
    "remove_role": _do_remove_role,
    "change_nickname": _do_change_nickname,
}


async def dispatch_ai_action(bot, msg: discord.Message, action: dict) -> None:
    """Route a structured AI Action dict to its handler.

    All handlers send their own CV2 responses (success / error / cancelled),
    so the caller doesn't need to do anything else after awaiting this.
    """
    name = (action.get("action") or "").strip()
    handler = _HANDLERS.get(name)
    if handler is None:
        logging.warning("AI", f"Model requested an unknown action '{name}'")
        await msg.channel.send(view=_error_view("Niko doesn't know how to do that yet."))
        return

    try:
        await handler(bot, msg, action)
    except discord.Forbidden as error:
        await _fail(msg, "do that", error)
    except Exception as error:  # noqa: BLE001
        await _fail(msg, "do that", error)
