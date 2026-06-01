"""
Moderation — channel-management commands (slowmode, lock, unlock).
"""
import discord
from discord.ext import commands
from ._messages import msg


class ChannelsMixin:
    """slowmode, lock, unlock commands."""

    @commands.hybrid_command(description="Set slowmode in this channel (seconds)",
                             help="{ 'en': 'Set slowmode in this channel (seconds).', 'de': 'Langsammodus setzen.', 'es': 'Establece el modo lento en este canal (segundos).' }")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(msg(ctx, "slowmode_set", seconds=seconds))

    @commands.hybrid_command(description="Lock this channel",
                             help="{ 'en': 'Lock this channel.', 'de': 'Kanal sperren.', 'es': 'Bloquea este canal.' }")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(msg(ctx, "locked"))
        body = f"**Channel:** {ctx.channel.mention}\n**Moderator:** {ctx.author.mention}"
        await self.logger().log_event(ctx.guild, "channels", "Lock", body, channel_id=ctx.channel.id, action_key="Lock")

    @commands.hybrid_command(description="Unlock this channel",
                             help="{ 'en': 'Unlock this channel.', 'de': 'Kanal entsperren.', 'es': 'Desbloquea este canal.' }")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(msg(ctx, "unlocked"))
        body = f"**Channel:** {ctx.channel.mention}\n**Moderator:** {ctx.author.mention}"
        await self.logger().log_event(ctx.guild, "channels", "Unlock", body, channel_id=ctx.channel.id, action_key="Unlock")
