"""
Moderation — message-management commands (clear, purge).
"""
import discord
from discord.ext import commands
from ._messages import msg, _cv2, _chunked_purge
from config.emojis import get_emoji

from utils.command_locales import command_texts

CMDS = command_texts(__package__)


class MessagesMixin:
    """clear and purge commands."""

    async def _purge_messages(self, ctx, member: discord.Member = None, amount: int = 100):
        amount = max(1, min(int(amount), 1000))
        if ctx.interaction is not None:
            await ctx.defer(ephemeral=True)
        else:
            try:
                await ctx.message.delete()
            except (discord.HTTPException, AttributeError):
                pass

        check = (lambda message: message.author.id == member.id) if member else None
        try:
            deleted = await _chunked_purge(ctx.channel, amount, check=check)
        except discord.Forbidden:
            return await ctx.send(view=_cv2(msg(ctx, "cannot_purge")), ephemeral=True)
        except discord.HTTPException as e:
            return await ctx.send(view=_cv2(msg(ctx, "action_failed", error=e)), ephemeral=True)
        if member:
            message = msg(ctx, "purged", count=len(deleted), member=member)
            category, action = "messages", "Purge"
            body = (
                f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Channel:** {ctx.channel.mention}\n"
                f"**Messages Deleted:** {len(deleted)}\n"
                f"**Moderator:** {ctx.author.mention}"
            )
            target_id = member.id
        else:
            message = msg(ctx, "cleared", count=len(deleted))
            category, action = "moderation", "Clear"
            body = (
                f"**Channel:** {ctx.channel.mention}\n"
                f"**Messages Deleted:** {len(deleted)}\n"
                f"**Moderator:** {ctx.author.mention}"
            )
            target_id = None

        # ephemeral matters: the purge itself was deferred privately, so the
        # confirmation must not land in the channel for everyone to read.
        await ctx.send(f"{get_emoji('broom')} {message}", delete_after=5, ephemeral=True)
        await self.logger().log_event(ctx.guild, category, action, body, target_id=target_id, action_key=action)

    @commands.hybrid_command(name="clear", aliases=["purge"], description=CMDS.text("clear.description"),
                             help=CMDS.help("clear"))
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def clear(
        self,
        ctx,
        count: int = commands.parameter(description=CMDS.arg("clear", "count")),
        user: discord.Member = commands.parameter(default=None, description=CMDS.arg("clear", "user")),
    ):
        await self._purge_messages(ctx, user, count)
