"""
Moderation — server-settings commands (badwords, whitelist, setmodlog).
"""
import discord
from discord.ext import commands
from config.emojis import get_emoji
from ._messages import msg, _cv2


class SettingsMixin:
    """badwords, whitelist, and setmodlog commands."""

    # ── BADWORDS ─────────────────────────────────────────────────────────────
    @commands.hybrid_group(name="badwords", invoke_without_command=True,
                           description="Manage the blocked word list",
                           help="{ 'en': 'Manage the blocked word list.', 'de': 'Verwalte die Liste blockierter Wörter.', 'es': 'Gestiona la lista de palabras bloqueadas.' }")
    @commands.has_permissions(manage_guild=True)
    async def badwords(self, ctx):
        utils = self.utils()
        words = utils.get_blocked_words(ctx.guild.id)
        if not words:
            return await ctx.send(f"{msg(ctx, 'badwords_none')}\n-# Use `{ctx.prefix}badwords add <word>` to add a word.")
        text = "### 🚫 Blocked Words\n" + "\n".join(f"- {w}" for w in words)
        text += f"\n\n-# Use `{ctx.prefix}badwords add <word>` to add a word."
        await ctx.send(view=_cv2(text))

    @badwords.command(name="add", description="Add a blocked word")
    @commands.has_permissions(manage_guild=True)
    async def badwords_add(self, ctx, *, word: str = None):
        utils = self.utils()
        if not word:
            return await ctx.send(msg(ctx, "no_word"))
        utils.add_blocked_word(ctx.guild.id, word)
        await ctx.send(msg(ctx, "badwords_added", word=word))

    @commands.has_permissions(manage_guild=True)
    @badwords.command(name="remove", description="Remove a blocked word")
    async def badwords_remove(self, ctx, *, word: str = None):
        utils = self.utils()
        if not word:
            return await ctx.send(msg(ctx, "no_word"))
        utils.remove_blocked_word(ctx.guild.id, word)
        await ctx.send(msg(ctx, "badwords_removed", word=word))

    @commands.has_permissions(manage_guild=True)
    @badwords.command(name="clear", description="Clear all blocked words")
    async def badwords_clear(self, ctx):
        utils = self.utils()
        utils.clear_blocked_words(ctx.guild.id)
        await ctx.send(msg(ctx, "badwords_cleared"))

    # ── WHITELIST ─────────────────────────────────────────────────────────────
    @commands.hybrid_group(name="whitelist", aliases=["wl"], invoke_without_command=True,
                           description="Manage the automod whitelist",
                           help="{ 'en': 'Manage the automod whitelist.', 'de': 'Verwalte die Automod-Whitelist.', 'es': 'Gestiona la lista blanca de automod.' }")
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

    @whitelist.command(name="add", description="Add a user or role to the automod whitelist")
    @commands.has_permissions(manage_guild=True)
    async def whitelist_add(self, ctx, target_type: str = None, target: str = None):
        utils = self.utils()
        if not target_type or target_type.lower() not in ("user", "role"):
            return await ctx.send(msg(ctx, "wl_invalid_type"))

        if target_type.lower() == "user":
            member = None
            if ctx.message.mentions:
                member = ctx.message.mentions[0]
            elif target and target.isdigit():
                member = ctx.guild.get_member(int(target))
            if not member:
                return await ctx.send(msg(ctx, "no_member", action="whitelist"))
            utils.add_whitelist_user(ctx.guild.id, member.id)
            await ctx.send(msg(ctx, "wl_user_added", target=member.mention), allowed_mentions=discord.AllowedMentions.none())
        else:
            role = None
            if ctx.message.role_mentions:
                role = ctx.message.role_mentions[0]
            elif target and target.isdigit():
                role = ctx.guild.get_role(int(target))
            if not role:
                return await ctx.send("Could not find that role.")
            utils.add_whitelist_role(ctx.guild.id, role.id)
            await ctx.send(msg(ctx, "wl_role_added", target=role.mention), allowed_mentions=discord.AllowedMentions.none())

    @whitelist.command(name="remove", aliases=["rm"], description="Remove a user or role from the automod whitelist")
    @commands.has_permissions(manage_guild=True)
    async def whitelist_remove(self, ctx, target_type: str = None, target: str = None):
        utils = self.utils()
        if not target_type or target_type.lower() not in ("user", "role"):
            return await ctx.send(msg(ctx, "wl_invalid_type"))

        if target_type.lower() == "user":
            member = None
            if ctx.message.mentions:
                member = ctx.message.mentions[0]
            elif target and target.isdigit():
                member = ctx.guild.get_member(int(target))
            if not member:
                return await ctx.send(msg(ctx, "no_member", action="remove from whitelist"))
            utils.remove_whitelist_user(ctx.guild.id, member.id)
            await ctx.send(msg(ctx, "wl_user_removed", target=member.mention), allowed_mentions=discord.AllowedMentions.none())
        else:
            role = None
            if ctx.message.role_mentions:
                role = ctx.message.role_mentions[0]
            elif target and target.isdigit():
                role = ctx.guild.get_role(int(target))
            if not role:
                return await ctx.send("Could not find that role.")
            utils.remove_whitelist_role(ctx.guild.id, role.id)
            await ctx.send(msg(ctx, "wl_role_removed", target=role.mention), allowed_mentions=discord.AllowedMentions.none())

    # ── SETMODLOG (deprecated redirect) ──────────────────────────────────────
    @commands.hybrid_command(name="setmodlog",
                             description="Set the moderation log channel (deprecated)",
                             help="{ 'en': 'Set the moderation log channel.', 'de': 'Moderationslog-Kanal setzen.', 'es': 'Establece el canal de registro de moderación.' }")
    async def setmodlog(self, ctx):
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="### Important Notice"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="This command has been moved to the new logging system and is scheduled for removal. "
                        "Please use `.logging` instead."
            ),
        ))
        await ctx.reply(view=view)
