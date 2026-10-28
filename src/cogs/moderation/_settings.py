"""
Moderation — server-settings commands (badwords, whitelist).
"""
import re

import discord
from discord.ext import commands
from ._messages import msg, _cv2

#: A user/role mention, or a bare snowflake.
_MENTION = re.compile(r"^<@[!&]?(\d+)>$")
_SNOWFLAKE = re.compile(r"^\d{15,20}$")


def _target_id(value) -> int | None:
    """Read a user or role id out of a mention or a bare id.

    Slash invocations hand us a plain string, and the synthetic context message
    carries no mentions, so the value itself has to be parsed — the old code
    peeked at ``ctx.message.mentions`` and therefore silently failed on slash
    commands while accepting mentions on prefix ones.
    """
    text = str(value or "").strip().strip("`")
    match = _MENTION.match(text)
    if match:
        return int(match.group(1))
    return int(text) if _SNOWFLAKE.match(text.lstrip("&")) else None


def _mention_text(kind: str, target_id: int) -> str:
    """How to refer to a whitelist entry, resolved or not."""
    return f"<@{target_id}>" if kind == "user" else f"<@&{target_id}>"


class SettingsMixin:
    """badwords and whitelist commands."""

    # ── BADWORDS ─────────────────────────────────────────────────────────────
    @commands.hybrid_group(name="badwords", invoke_without_command=True,
                           description="Manage the blocked word list",
                           help="{ 'en': 'Manage the blocked word list.', 'de': 'Verwalte die Liste blockierter Wörter.', 'es': 'Gestiona la lista de palabras bloqueadas.' }")
    @commands.has_permissions(manage_guild=True)
    async def badwords(self, ctx):
        """The interactive blocked-words panel: word list, preset filters,
        and the delete/censor response, all editable in place."""
        from ._badwords_panel import build_panel

        await ctx.send(
            view=build_panel(self.utils(), ctx.guild.id, "overview", ctx.guild),
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @badwords.command(name="add", description="Add a blocked word")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def badwords_add(self, ctx, *, word: str = commands.parameter(default=None, description="The word or phrase to block.")):
        utils = self.utils()
        if not word:
            return await ctx.send(msg(ctx, "no_word"))
        utils.add_blocked_word(ctx.guild.id, word)
        await ctx.send(msg(ctx, "badwords_added", word=word))
        await utils.log_action(
            ctx.guild, "Blocked Words",
            f"**Action:** Word added\n**Word:** `{word}`", moderator=ctx.author)

    @commands.has_permissions(manage_guild=True)
    @badwords.command(name="remove", description="Remove a blocked word")
    async def badwords_remove(self, ctx, *, word: str = commands.parameter(default=None, description="The blocked word or phrase to remove.")):
        utils = self.utils()
        if not word:
            return await ctx.send(msg(ctx, "no_word"))
        utils.remove_blocked_word(ctx.guild.id, word)
        await ctx.send(msg(ctx, "badwords_removed", word=word))
        await utils.log_action(
            ctx.guild, "Blocked Words",
            f"**Action:** Word removed\n**Word:** `{word}`", moderator=ctx.author)

    @commands.has_permissions(manage_guild=True)
    @badwords.command(name="clear", description="Clear all blocked words")
    async def badwords_clear(self, ctx):
        utils = self.utils()
        utils.clear_blocked_words(ctx.guild.id)
        await ctx.send(msg(ctx, "badwords_cleared"))
        await utils.log_action(
            ctx.guild, "Blocked Words",
            "**Action:** Every blocked word cleared", moderator=ctx.author)

    # ── WHITELIST ─────────────────────────────────────────────────────────────
    @commands.hybrid_group(name="whitelist", aliases=["wl"], invoke_without_command=True,
                           description="Manage the automod whitelist",
                           help="{ 'en': 'Manage the automod whitelist.', 'de': 'Verwalte die Automod-Whitelist.', 'es': 'Gestiona la lista blanca de automod.' }")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def whitelist(self, ctx):
        utils = self.utils()
        wl = utils.get_whitelist(ctx.guild.id)
        user_ids = wl.get("users", [])
        role_ids = wl.get("roles", [])

        if not user_ids and not role_ids:
            return await ctx.send(msg(ctx, "wl_empty"))

        users_text = "\n".join(
            ctx.guild.get_member(uid).mention if ctx.guild.get_member(uid) else f"<@{uid}>"
            for uid in user_ids
        ) or "*None*"
        roles_text = "\n".join(
            ctx.guild.get_role(rid).mention if ctx.guild.get_role(rid) else f"<@&{rid}>"
            for rid in role_ids
        ) or "*None*"

        text = (
            msg(ctx, "wl_title")
            + msg(ctx, "wl_users", users=users_text)
            + msg(ctx, "wl_roles", roles=roles_text)
        )
        await ctx.send(view=_cv2(text), allowed_mentions=discord.AllowedMentions.none())

    @whitelist.command(name="add", description="Exempt a user or role from automod")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def whitelist_add(
        self,
        ctx,
        target_type: str = commands.parameter(default=None, description="Whether the target is a user or a role."),
        target: str = commands.parameter(default=None, description="The user or role mention, or its numeric ID."),
    ):
        utils = self.utils()
        kind = str(target_type or "").strip().lower()
        if kind not in ("user", "role"):
            return await ctx.send(msg(ctx, "wl_invalid_type"))
        target_id = _target_id(target)
        if target_id is None:
            return await ctx.send(msg(ctx, "wl_bad_target", kind=kind))

        if kind == "user":
            mention = _mention_text(kind, target_id)
            user = ctx.guild.get_member(target_id)
            if user is None:
                # Someone who left the server can still be on the list; only an
                # id that resolves to nothing at all is refused.
                try:
                    user = await self.bot.fetch_user(target_id)
                except (discord.NotFound, discord.HTTPException):
                    return await ctx.send(msg(ctx, "no_user_found"))
            mention = user.mention
            utils.add_whitelist_user(ctx.guild.id, target_id)
        else:
            role = ctx.guild.get_role(target_id)
            if role is None:
                return await ctx.send(msg(ctx, "wl_role_missing"))
            mention = role.mention
            utils.add_whitelist_role(ctx.guild.id, target_id)

        key = "wl_user_added" if kind == "user" else "wl_role_added"
        await ctx.send(msg(ctx, key, target=mention), allowed_mentions=discord.AllowedMentions.none())
        await utils.log_action(
            ctx.guild, "AutoMod Whitelist",
            f"**Action:** Added {kind}\n**Target:** {mention}", moderator=ctx.author)

    @whitelist.command(name="remove", aliases=["rm"], description="Stop exempting a user or role from automod")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def whitelist_remove(
        self,
        ctx,
        target_type: str = commands.parameter(default=None, description="Whether the target is a user or a role."),
        target: str = commands.parameter(default=None, description="The user or role mention, or its numeric ID."),
    ):
        utils = self.utils()
        kind = str(target_type or "").strip().lower()
        if kind not in ("user", "role"):
            return await ctx.send(msg(ctx, "wl_invalid_type"))
        target_id = _target_id(target)
        if target_id is None:
            return await ctx.send(msg(ctx, "wl_bad_target", kind=kind))

        if kind == "user":
            member = ctx.guild.get_member(target_id)
            mention = member.mention if member else _mention_text(kind, target_id)
            utils.remove_whitelist_user(ctx.guild.id, target_id)
        else:
            role = ctx.guild.get_role(target_id)
            if role is None:
                return await ctx.send(msg(ctx, "wl_role_missing"))
            mention = role.mention
            utils.remove_whitelist_role(ctx.guild.id, target_id)

        key = "wl_user_removed" if kind == "user" else "wl_role_removed"
        await ctx.send(msg(ctx, key, target=mention), allowed_mentions=discord.AllowedMentions.none())
        await utils.log_action(
            ctx.guild, "AutoMod Whitelist",
            f"**Action:** Removed {kind}\n**Target:** {mention}", moderator=ctx.author)
