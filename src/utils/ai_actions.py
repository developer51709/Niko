"""AI Actions dispatcher.

Handles structured action requests returned by the OpenAI integration when
the AI Actions experiment is enabled. Every action goes through the same
two-stage pipeline before it can affect the server:

1.  **Permission check** — the user who triggered the AI must hold the
    Discord permission required for that action *and* the bot must hold the
    permission too. If either is missing the action is refused with a CV2
    error container.
2.  **Confirmation** — a CV2 LayoutView is sent describing exactly what the
    AI is about to do (target, scope, reason). Only the requesting user can
    confirm or cancel. The action only executes after an explicit confirm.

A small number of AI Actions (currently only ``create_poll``) are considered
non-destructive and skip the confirmation step.
"""

from __future__ import annotations

import asyncio
import re
from typing import Optional

import discord

from config.emojis import get_emoji


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
    for m in guild.members:
        if lowered in m.name.lower() or lowered in m.display_name.lower():
            return m
    return None


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
#  CV2 helpers — confirmation view & error/success notifications
# ────────────────────────────────────────────────────────────────────

def _info_view(title: str, body: str, *, colour: discord.Colour = discord.Colour.blurple()) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {title}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=body),
        accent_colour=colour,
    ))
    return view


def _error_view(body: str) -> discord.ui.LayoutView:
    return _info_view(f"{get_emoji('icon_danger')} AI Action Refused", body, colour=discord.Colour.red())


def _success_view(body: str) -> discord.ui.LayoutView:
    return _info_view(f"{get_emoji('icon_tick')} AI Action Completed", body, colour=discord.Colour.green())


class AIActionConfirmView(discord.ui.LayoutView):
    """LayoutView with Confirm + Cancel buttons gated to the invoker."""

    def __init__(self, title: str, body: str, *, invoker_id: int, timeout: float = 45.0):
        super().__init__(timeout=timeout)
        self.invoker_id = invoker_id
        self.confirmed: bool | None = None
        self._event = asyncio.Event()

        self._confirm = discord.ui.Button(
            label="Confirm",
            style=discord.ButtonStyle.danger,
            emoji=get_emoji("icon_tick") or "✅",
        )
        self._cancel = discord.ui.Button(
            label="Cancel",
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("icon_cross") or "❌",
        )
        self._confirm.callback = self._on_confirm
        self._cancel.callback = self._on_cancel

        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_ai')} {title}"),
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
                f"{get_emoji('icon_cross')} Cancelled",
                "Niko didn't do anything.",
                colour=discord.Colour.greyple(),
            ),
        )
        self._event.set()

    async def on_timeout(self):
        if self.confirmed is None:
            self.confirmed = False
            self._event.set()

    async def wait_for_response(self) -> bool:
        await self._event.wait()
        return bool(self.confirmed)


async def _confirm(channel, *, title: str, body: str, invoker_id: int) -> bool:
    view = AIActionConfirmView(title, body, invoker_id=invoker_id)
    await channel.send(view=view)
    return await view.wait_for_response()


# ────────────────────────────────────────────────────────────────────
#  Permission checks (user + bot must both hold the perm)
# ────────────────────────────────────────────────────────────────────

def _has_perm(member: discord.Member, perm: str) -> bool:
    perms = member.guild_permissions
    return getattr(perms, perm, False) or perms.administrator


def _check_perms(msg: discord.Message, perm: str, *, action_label: str):
    """Return None if both invoker and bot have ``perm``, else an error view."""
    me = msg.guild.me if msg.guild else None
    if not msg.guild or not isinstance(msg.author, discord.Member) or me is None:
        return _error_view("AI Actions can only run inside a server.")
    if not _has_perm(msg.author, perm):
        return _error_view(
            f"You need the **{perm.replace('_', ' ').title()}** permission to ask Niko to {action_label}."
        )
    if not _has_perm(me, perm):
        return _error_view(
            f"Niko doesn't have the **{perm.replace('_', ' ').title()}** permission needed to {action_label}."
        )
    return None


# ────────────────────────────────────────────────────────────────────
#  Per-action handlers
# ────────────────────────────────────────────────────────────────────

async def _do_create_poll(bot, msg: discord.Message, args: dict) -> None:
    question = (args.get("question") or "Poll").strip()[:256]
    options = [str(o).strip() for o in (args.get("options") or []) if str(o).strip()][:9]
    if len(options) < 2:
        await msg.channel.send(view=_error_view("A poll needs at least two options."))
        return
    number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    lines = [f"**📊 {question}**\n"]
    for i, opt in enumerate(options):
        lines.append(f"{number_emojis[i]} {opt}")
    poll_msg = await msg.channel.send("\n".join(lines))
    for i in range(len(options)):
        try:
            await poll_msg.add_reaction(number_emojis[i])
        except Exception:
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
    if member == msg.guild.me or member == msg.author:
        await msg.channel.send(view=_error_view("I won't kick that member."))
        return
    if member.top_role >= msg.guild.me.top_role:
        await msg.channel.send(view=_error_view("That member's role is higher than or equal to mine — I can't kick them."))
        return
    reason = (args.get("reason") or "No reason provided").strip()[:400]
    body = f"Kick **{member}** (`{member.id}`)?\n**Reason:** {reason}"
    if not await _confirm(msg.channel, title="Confirm Kick", body=body, invoker_id=msg.author.id):
        return
    try:
        await member.kick(reason=f"AI Action by {msg.author}: {reason}")
    except discord.HTTPException as e:
        await msg.channel.send(view=_error_view(f"Failed to kick: {e}"))
        return
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
        if target == msg.guild.me or target == msg.author:
            await msg.channel.send(view=_error_view("I won't ban that user."))
            return
        if target.top_role >= msg.guild.me.top_role:
            await msg.channel.send(view=_error_view("That member's role is higher than or equal to mine — I can't ban them."))
            return
    reason = (args.get("reason") or "No reason provided").strip()[:400]
    delete_days = max(0, min(7, int(args.get("delete_message_days") or 0)))
    body = f"Ban **{target}** (`{target.id}`)?\n**Reason:** {reason}\n**Delete messages from last:** {delete_days}d"
    if not await _confirm(msg.channel, title="Confirm Ban", body=body, invoker_id=msg.author.id):
        return
    try:
        await msg.guild.ban(target, reason=f"AI Action by {msg.author}: {reason}", delete_message_days=delete_days)
    except discord.HTTPException as e:
        await msg.channel.send(view=_error_view(f"Failed to ban: {e}"))
        return
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
    except discord.HTTPException as e:
        await msg.channel.send(view=_error_view(f"Failed to unban: {e}"))
        return
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
    if member.top_role >= msg.guild.me.top_role:
        await msg.channel.send(view=_error_view("That member's role is higher than or equal to mine — I can't time them out."))
        return
    reason = (args.get("reason") or "No reason provided").strip()[:400]
    body = f"Time out **{member}** for **{seconds}s**?\n**Reason:** {reason}"
    if not await _confirm(msg.channel, title="Confirm Timeout", body=body, invoker_id=msg.author.id):
        return
    import datetime as _dt
    until = discord.utils.utcnow() + _dt.timedelta(seconds=seconds)
    try:
        await member.edit(timed_out_until=until, reason=f"AI Action by {msg.author}: {reason}")
    except discord.HTTPException as e:
        await msg.channel.send(view=_error_view(f"Failed to time out: {e}"))
        return
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
    except discord.HTTPException as e:
        await msg.channel.send(view=_error_view(f"Failed to remove timeout: {e}"))
        return
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
    reason = (args.get("reason") or "No reason provided").strip()[:400]
    body = f"Warn **{member}** (`{member.id}`)?\n**Reason:** {reason}"
    if not await _confirm(msg.channel, title="Confirm Warn", body=body, invoker_id=msg.author.id):
        return
    utils_cog = bot.get_cog("ModerationUtils")
    if utils_cog and hasattr(utils_cog, "add_warn"):
        try:
            utils_cog.add_warn(msg.guild.id, member.id, msg.author.id, reason)
        except Exception as e:
            await msg.channel.send(view=_error_view(f"Failed to record warning: {e}"))
            return
    await msg.channel.send(view=_success_view(f"Warned **{member}** — {reason}"))


async def _do_purge_messages(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "manage_messages", action_label="purge messages")
    if err:
        await msg.channel.send(view=err)
        return
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
    body = f"Delete the last **{amount}** messages in {channel.mention}?"
    if not await _confirm(msg.channel, title="Confirm Purge", body=body, invoker_id=msg.author.id):
        return
    try:
        deleted = await channel.purge(limit=amount, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as e:
        await msg.channel.send(view=_error_view(f"Failed to purge: {e}"))
        return
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
            new_ch = await msg.guild.create_voice_channel(name=name, category=category, reason=f"AI Action by {msg.author}")
        else:
            new_ch = await msg.guild.create_text_channel(name=name, category=category, topic=topic, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as e:
        await msg.channel.send(view=_error_view(f"Failed to create channel: {e}"))
        return
    await msg.channel.send(view=_success_view(f"Created {new_ch.mention}."))


async def _do_delete_channel(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "manage_channels", action_label="delete a channel")
    if err:
        await msg.channel.send(view=err)
        return
    channel = _resolve_channel(msg.guild, args.get("channel"))
    if not channel:
        await msg.channel.send(view=_error_view(f"I couldn't find a channel matching `{args.get('channel')}`."))
        return
    if channel == msg.channel:
        await msg.channel.send(view=_error_view("I won't delete the channel this conversation is happening in — run the command from a different channel if you really want to."))
        return
    body = f"Delete the channel **#{channel.name}** (`{channel.id}`)?\n*This cannot be undone.*"
    if not await _confirm(msg.channel, title="Confirm Delete Channel", body=body, invoker_id=msg.author.id):
        return
    try:
        await channel.delete(reason=f"AI Action by {msg.author}")
    except discord.HTTPException as e:
        await msg.channel.send(view=_error_view(f"Failed to delete channel: {e}"))
        return
    await msg.channel.send(view=_success_view(f"Deleted channel **#{channel.name}**."))


async def _do_rename_channel(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "manage_channels", action_label="rename a channel")
    if err:
        await msg.channel.send(view=err)
        return
    channel = _resolve_channel(msg.guild, args.get("channel")) or msg.channel
    new_name = (args.get("name") or "").strip().lower().replace(" ", "-")[:90]
    if not new_name:
        await msg.channel.send(view=_error_view("New channel name is required."))
        return
    body = f"Rename **#{channel.name}** → **#{new_name}**?"
    if not await _confirm(msg.channel, title="Confirm Rename Channel", body=body, invoker_id=msg.author.id):
        return
    try:
        await channel.edit(name=new_name, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as e:
        await msg.channel.send(view=_error_view(f"Failed to rename channel: {e}"))
        return
    await msg.channel.send(view=_success_view(f"Renamed channel to **#{new_name}**."))


async def _do_set_channel_topic(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "manage_channels", action_label="change a channel topic")
    if err:
        await msg.channel.send(view=err)
        return
    channel = _resolve_channel(msg.guild, args.get("channel")) or msg.channel
    if not isinstance(channel, discord.TextChannel):
        await msg.channel.send(view=_error_view("Topics can only be set on text channels."))
        return
    topic = (args.get("topic") or "").strip()[:1024]
    body = f"Set topic of **#{channel.name}** to:\n> {topic or '(empty)'}"
    if not await _confirm(msg.channel, title="Confirm Set Topic", body=body, invoker_id=msg.author.id):
        return
    try:
        await channel.edit(topic=topic, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as e:
        await msg.channel.send(view=_error_view(f"Failed to set topic: {e}"))
        return
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
        return discord.Colour(int(s, 16))
    except ValueError:
        return None


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
        kwargs = {"name": name, "hoist": hoist, "mentionable": mentionable, "reason": f"AI Action by {msg.author}"}
        if colour is not None:
            kwargs["colour"] = colour
        new_role = await msg.guild.create_role(**kwargs)
    except discord.HTTPException as e:
        await msg.channel.send(view=_error_view(f"Failed to create role: {e}"))
        return
    await msg.channel.send(view=_success_view(f"Created role {new_role.mention}."))


async def _do_delete_role(bot, msg: discord.Message, args: dict) -> None:
    err = _check_perms(msg, "manage_roles", action_label="delete a role")
    if err:
        await msg.channel.send(view=err)
        return
    role = _resolve_role(msg.guild, args.get("role"))
    if not role:
        await msg.channel.send(view=_error_view(f"I couldn't find a role matching `{args.get('role')}`."))
        return
    if role >= msg.guild.me.top_role or role.is_default() or role.managed:
        await msg.channel.send(view=_error_view("I can't delete that role (it's higher than mine, the @everyone role, or managed by an integration)."))
        return
    body = f"Delete the role **{role.name}** (`{role.id}`)?\n*This cannot be undone.*"
    if not await _confirm(msg.channel, title="Confirm Delete Role", body=body, invoker_id=msg.author.id):
        return
    try:
        await role.delete(reason=f"AI Action by {msg.author}")
    except discord.HTTPException as e:
        await msg.channel.send(view=_error_view(f"Failed to delete role: {e}"))
        return
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
    if role >= msg.guild.me.top_role or role.is_default() or role.managed:
        await msg.channel.send(view=_error_view("I can't assign that role (it's higher than mine, @everyone, or managed)."))
        return
    body = f"Give the role **{role.name}** to **{member}**?"
    if not await _confirm(msg.channel, title="Confirm Assign Role", body=body, invoker_id=msg.author.id):
        return
    try:
        await member.add_roles(role, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as e:
        await msg.channel.send(view=_error_view(f"Failed to assign role: {e}"))
        return
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
    if role >= msg.guild.me.top_role or role.is_default() or role.managed:
        await msg.channel.send(view=_error_view("I can't remove that role (higher than mine, @everyone, or managed)."))
        return
    body = f"Remove the role **{role.name}** from **{member}**?"
    if not await _confirm(msg.channel, title="Confirm Remove Role", body=body, invoker_id=msg.author.id):
        return
    try:
        await member.remove_roles(role, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as e:
        await msg.channel.send(view=_error_view(f"Failed to remove role: {e}"))
        return
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
    nickname = args.get("nickname")
    nickname = nickname.strip()[:32] if isinstance(nickname, str) else None
    if nickname == "":
        nickname = None
    body = f"Change **{member}**'s nickname to **{nickname or '(reset to username)'}**?"
    if not await _confirm(msg.channel, title="Confirm Change Nickname", body=body, invoker_id=msg.author.id):
        return
    try:
        await member.edit(nick=nickname, reason=f"AI Action by {msg.author}")
    except discord.HTTPException as e:
        await msg.channel.send(view=_error_view(f"Failed to change nickname: {e}"))
        return
    await msg.channel.send(view=_success_view(f"Updated nickname for **{member}**."))


# ────────────────────────────────────────────────────────────────────
#  Dispatcher
# ────────────────────────────────────────────────────────────────────

_HANDLERS = {
    # Non-destructive (skip permission gate; no confirmation)
    "create_poll": (_do_create_poll, False),

    # Moderation
    "kick_member":     (_do_kick_member,    True),
    "ban_member":      (_do_ban_member,     True),
    "unban_user":      (_do_unban_user,     True),
    "timeout_member":  (_do_timeout_member, True),
    "remove_timeout":  (_do_remove_timeout, True),
    "warn_member":     (_do_warn_member,    True),
    "purge_messages":  (_do_purge_messages, True),

    # Server management
    "create_channel":   (_do_create_channel,    True),
    "delete_channel":   (_do_delete_channel,    True),
    "rename_channel":   (_do_rename_channel,    True),
    "set_channel_topic":(_do_set_channel_topic, True),
    "create_role":      (_do_create_role,       True),
    "delete_role":      (_do_delete_role,       True),
    "assign_role":      (_do_assign_role,       True),
    "remove_role":      (_do_remove_role,       True),
    "change_nickname":  (_do_change_nickname,   True),
}


async def dispatch_ai_action(bot, msg: discord.Message, action: dict) -> None:
    """Route a structured AI Action dict to its handler.

    All handlers send their own CV2 responses (success / error / cancelled),
    so the caller doesn't need to do anything else after awaiting this.
    """
    name = (action.get("action") or "").strip()
    handler_entry = _HANDLERS.get(name)
    if handler_entry is None:
        await msg.channel.send(view=_error_view(f"Niko doesn't know how to do `{name}` yet."))
        return

    handler, _gated = handler_entry
    try:
        await handler(bot, msg, action)
    except discord.Forbidden:
        await msg.channel.send(view=_error_view("Discord refused the action — I'm missing permissions."))
    except Exception as e:  # noqa: BLE001
        await msg.channel.send(view=_error_view(f"Something went wrong: `{e}`"))
