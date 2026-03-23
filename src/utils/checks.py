import discord
from discord.ext import commands


def guild_only():
    return commands.guild_only()


def has_perms(**perms):
    return commands.has_permissions(**perms)


def bot_has_perms(**perms):
    return commands.bot_has_permissions(**perms)


def cooldown(rate=1, per=3.0, bucket=commands.BucketType.user):
    return commands.cooldown(rate, per, bucket)


async def role_priv(ctx, role: discord.Role):
    if role.managed:
        return f"Role {role.mention} is managed by an integration and cannot be assigned."
    if role >= ctx.guild.me.top_role:
        return f"Role {role.mention} is above my highest role and cannot be managed."
    if role >= ctx.author.top_role and ctx.guild.owner_id != ctx.author.id:
        return f"Role {role.mention} is above your highest role."
    return None