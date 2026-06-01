"""
Moderation — message-management commands (clear, purge).
"""
import discord
from discord.ext import commands
from ._messages import msg, _chunked_purge


class MessagesMixin:
    """clear and purge commands."""

    @commands.hybrid_command(description="Clear messages in this channel",
                             help="{ 'en': 'Clear messages in this channel.', 'de': 'Nachrichten löschen.', 'es': 'Borra mensajes en este canal.' }")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=None):
        if not amount:
            return await ctx.send(msg(ctx, "no_amount"))
        amount = int(amount)
        if ctx.interaction is not None:
            await ctx.defer(ephemeral=True)
        else:
            try:
                await ctx.message.delete()
            except (discord.HTTPException, AttributeError):
                pass
        deleted = await _chunked_purge(ctx.channel, amount)
        await ctx.send(msg(ctx, "cleared", count=len(deleted)), delete_after=5)
        body = (
            f"**Channel:** {ctx.channel.mention}\n"
            f"**Messages Deleted:** {len(deleted)}\n"
            f"**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(ctx.guild, "moderation", "Clear", body, action_key="Clear")

    @commands.hybrid_command(description="Purge messages from a specific user",
                             help="{ 'en': 'Purge messages from a specific user.', 'de': 'Nachrichten eines Nutzers löschen.', 'es': 'Elimina mensajes de un usuario específico.' }")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, member: discord.Member = None, amount: int = 100):
        if not member:
            return await ctx.send(msg(ctx, "no_channel"))
        def check(m):
            return m.author.id == member.id
        if ctx.interaction is not None:
            await ctx.defer(ephemeral=True)
        else:
            try:
                await ctx.message.delete()
            except (discord.HTTPException, AttributeError):
                pass
        deleted = await _chunked_purge(ctx.channel, amount, check=check)
        await ctx.send(msg(ctx, "purged", count=len(deleted), member=member), delete_after=5)
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Channel:** {ctx.channel.mention}\n"
            f"**Messages Deleted:** {len(deleted)}\n"
            f"**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(ctx.guild, "messages", "Purge", body, target_id=member.id, action_key="Purge")
