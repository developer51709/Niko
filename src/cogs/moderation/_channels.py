"""
Moderation — channel-management commands (slowmode, lock, unlock).
"""
import discord
from discord.ext import commands
from ._messages import ALLOWED_MENTIONS, msg, _cv2

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

#: Discord's ceiling for ``rate_limit_per_user`` (6 hours). A larger value is
#: rejected by the API, which used to surface as a raw HTTP error.
MAX_SLOWMODE_SECONDS = 21600


async def set_everyone_send_messages(channel: discord.abc.GuildChannel,
                                     guild: discord.Guild,
                                     value: bool | None,
                                     *, reason: str) -> None:
    """Write the @everyone ``send_messages`` overwrite for a channel.

    This goes through the channel *permission* endpoint (what
    :meth:`~discord.abc.GuildChannel.set_permissions` calls), which Discord
    covers with **Manage Roles**. Editing the channel itself instead would need
    **Manage Channels**, and a bot that asks for Manage Channels just to lock a
    channel is one of the most common reasons a bot review — top.gg's included —
    is rejected. Keep the overwrite route here, never ``channel.edit(...)``.

    ``value=None`` restores inheritance, which is what unlocking does; the rest
    of the @everyone overwrite is preserved either way.

    Threads have no overwrites of their own; they go through
    :func:`set_thread_locked` instead.
    """
    overwrite = channel.overwrites_for(guild.default_role)
    overwrite.send_messages = value
    await channel.set_permissions(
        guild.default_role, overwrite=overwrite, reason=reason)


async def set_thread_locked(thread: discord.Thread, locked: bool, *, reason: str) -> None:
    """Lock or unlock a single thread, which includes a forum post.

    A thread carries its own ``locked`` flag rather than permission overwrites:
    while it is set, only members with **Manage Threads** can send messages in
    that one conversation, and everyone else keeps posting in the rest of the
    server. That is exactly the per-post lock a forum needs, so `lock`/`unlock`
    take this path whenever the target is a thread. Unlocking clears the flag and
    normal permissions apply again.

    Editing a thread this way is covered by **Manage Threads**, not Manage Roles.
    """
    await thread.edit(locked=locked, reason=reason)


class ChannelsMixin:
    """slowmode, lock, unlock commands."""

    def _lockable_channel(self, ctx):
        """The channel or thread `lock`/`unlock` should act on, or None.

        Threads are accepted — a forum post is a thread — and lock through their
        own ``locked`` flag. Channels and categories go through the @everyone
        overwrite.
        """
        channel = ctx.channel
        if isinstance(channel, discord.Thread):
            return channel
        return channel if isinstance(channel, discord.abc.GuildChannel) else None

    def _lock_permission(self, ctx, channel):
        """The denial message key for this target, or None to go ahead.

        The two paths need different permissions, so this is checked per target
        instead of in the decorator: an overwrite needs **Manage Roles**, a
        thread needs **Manage Threads**. Neither path needs Manage Channels.
        """
        permissions = getattr(ctx, "permissions", None) or getattr(ctx, "guild_permissions", None)
        if isinstance(channel, discord.Thread):
            return None if getattr(permissions, "manage_threads", False) else "need_manage_threads"
        return None if getattr(permissions, "manage_roles", False) else "need_manage_roles"

    @commands.hybrid_command(description=CMDS.text("slowmode.description"),
                             help=CMDS.help("slowmode"))
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = commands.parameter(default=0, description=CMDS.arg("slowmode", "seconds"))):
        if seconds < 0 or seconds > MAX_SLOWMODE_SECONDS:
            return await ctx.send(view=_cv2(msg(
                ctx, "slowmode_limit", max=MAX_SLOWMODE_SECONDS, hours=MAX_SLOWMODE_SECONDS // 3600)),
                allowed_mentions=ALLOWED_MENTIONS)
        try:
            await ctx.channel.edit(slowmode_delay=seconds)
        except discord.Forbidden:
            return await ctx.send(view=_cv2(msg(ctx, "cannot_slowmode")), allowed_mentions=ALLOWED_MENTIONS)
        except discord.HTTPException as e:
            return await ctx.send(view=_cv2(msg(ctx, "action_failed", error=e)), allowed_mentions=ALLOWED_MENTIONS)
        await ctx.send(msg(ctx, "slowmode_set", seconds=seconds), allowed_mentions=ALLOWED_MENTIONS)

    async def _set_locked(self, ctx, locked: bool):
        """Lock or unlock whatever the command was run in.

        Channels and categories take the @everyone overwrite; a thread or forum
        post takes its own ``locked`` flag. The rest — the permission that
        applies, the card, the audit-log reason and the log entry — is identical
        either way, so both commands share this path.
        """
        channel = self._lockable_channel(ctx)
        if channel is None:
            return await ctx.send(view=_cv2(msg(ctx, "cannot_manage_channel")), allowed_mentions=ALLOWED_MENTIONS)
        denial = self._lock_permission(ctx, channel)
        if denial:
            return await ctx.send(view=_cv2(msg(ctx, denial)), allowed_mentions=ALLOWED_MENTIONS)

        thread = isinstance(channel, discord.Thread)
        action = "Lock" if locked else "Unlock"
        state = "locked" if locked else "unlocked"
        reason = f"{'Locked' if locked else 'Unlocked'} by {ctx.author} ({ctx.author.id})"
        try:
            if thread:
                await set_thread_locked(channel, locked, reason=reason)
            else:
                await set_everyone_send_messages(
                    channel, ctx.guild, False if locked else None, reason=reason)
        except discord.Forbidden:
            key = "cannot_lock_thread" if thread else "cannot_manage_channel"
            return await ctx.send(view=_cv2(msg(ctx, key)), allowed_mentions=ALLOWED_MENTIONS)
        except discord.HTTPException as e:
            return await ctx.send(view=_cv2(msg(ctx, "action_failed", error=e)), allowed_mentions=ALLOWED_MENTIONS)

        await ctx.send(
            view=_cv2(msg(
                ctx, f"{state}_thread" if thread else state,
                channel=channel.mention, moderator=ctx.author.mention,
            )),
            allowed_mentions=ALLOWED_MENTIONS,
        )
        body = f"**{'Thread' if thread else 'Channel'}:** {channel.mention}\n**Moderator:** {ctx.author.mention}"
        await self.logger().log_event(
            ctx.guild, "channels", action, body, channel_id=channel.id, action_key=action)

    @commands.hybrid_command(description=CMDS.text("lock.description"),
                             help=CMDS.help("lock"))
    @commands.guild_only()
    # Either permission can run it, because the target decides which one matters:
    # a channel overwrite needs Manage Roles, a thread needs Manage Threads. The
    # body then re-checks the one that applies and explains the mismatch. What
    # matters for review is that neither path needs Manage Channels.
    @commands.check_any(commands.has_permissions(manage_roles=True),
                        commands.has_permissions(manage_threads=True))
    async def lock(self, ctx):
        await self._set_locked(ctx, True)

    @commands.hybrid_command(description=CMDS.text("unlock.description"),
                             help=CMDS.help("unlock"))
    @commands.guild_only()
    @commands.check_any(commands.has_permissions(manage_roles=True),
                        commands.has_permissions(manage_threads=True))
    async def unlock(self, ctx):
        await self._set_locked(ctx, False)
