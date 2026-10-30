"""
Moderation — channel-management commands (slowmode, lock, unlock).
"""
import discord
from discord.ext import commands
from ._messages import msg, _cv2

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

#: Discord's ceiling for ``rate_limit_per_user`` (6 hours). A larger value is
#: rejected by the API, which used to surface as a raw HTTP error.
MAX_SLOWMODE_SECONDS = 21600


class ChannelsMixin:
    """slowmode, lock, unlock commands."""

    def _lockable_channel(self, ctx):
        """A channel that can carry an @everyone overwrite, or None.

        Threads take slowmode but no permission overwrites, so `lock` and
        `unlock` have to say so rather than raising AttributeError.
        """
        channel = ctx.channel
        return channel if isinstance(channel, discord.abc.GuildChannel) else None

    @commands.hybrid_command(description=CMDS.text("slowmode.description"),
                             help=CMDS.help("slowmode"))
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = commands.parameter(default=0, description=CMDS.arg("slowmode", "seconds"))):
        if seconds < 0 or seconds > MAX_SLOWMODE_SECONDS:
            return await ctx.send(view=_cv2(msg(
                ctx, "slowmode_limit", max=MAX_SLOWMODE_SECONDS, hours=MAX_SLOWMODE_SECONDS // 3600)))
        try:
            await ctx.channel.edit(slowmode_delay=seconds)
        except discord.Forbidden:
            return await ctx.send(view=_cv2(msg(ctx, "cannot_slowmode")))
        except discord.HTTPException as e:
            return await ctx.send(view=_cv2(msg(ctx, "action_failed", error=e)))
        await ctx.send(msg(ctx, "slowmode_set", seconds=seconds))

    @commands.hybrid_command(description=CMDS.text("lock.description"),
                             help=CMDS.help("lock"))
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        channel = self._lockable_channel(ctx)
        if channel is None:
            return await ctx.send(view=_cv2(msg(ctx, "cannot_manage_channel")))
        try:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        except discord.Forbidden:
            return await ctx.send(view=_cv2(msg(ctx, "cannot_manage_channel")))
        except discord.HTTPException as e:
            return await ctx.send(view=_cv2(msg(ctx, "action_failed", error=e)))
        await ctx.send(msg(ctx, "locked"))
        body = f"**Channel:** {channel.mention}\n**Moderator:** {ctx.author.mention}"
        await self.logger().log_event(ctx.guild, "channels", "Lock", body, channel_id=channel.id, action_key="Lock")

    @commands.hybrid_command(description=CMDS.text("unlock.description"),
                             help=CMDS.help("unlock"))
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        channel = self._lockable_channel(ctx)
        if channel is None:
            return await ctx.send(view=_cv2(msg(ctx, "cannot_manage_channel")))
        try:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = None
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        except discord.Forbidden:
            return await ctx.send(view=_cv2(msg(ctx, "cannot_manage_channel")))
        except discord.HTTPException as e:
            return await ctx.send(view=_cv2(msg(ctx, "action_failed", error=e)))
        await ctx.send(msg(ctx, "unlocked"))
        body = f"**Channel:** {channel.mention}\n**Moderator:** {ctx.author.mention}"
        await self.logger().log_event(ctx.guild, "channels", "Unlock", body, channel_id=channel.id, action_key="Unlock")
