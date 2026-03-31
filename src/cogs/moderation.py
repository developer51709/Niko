import discord
from discord.ext import commands
from utils import logging as log
from utils.logging import info, success, warning, error, debug
from config.emojis import get_emoji

# ─────────────────────────────────────────────────────────────
#  BILINGUAL MESSAGE TABLE
# ─────────────────────────────────────────────────────────────

MESSAGES = {
    "en": {
        # generic
        "no_member":        "Please specify a member to {action}.",
        "no_user_id":       "Please provide a user ID to unban.",
        "no_amount":        "Please specify an amount of messages to delete.",
        "no_duration":      "Please specify a duration in seconds.",
        "no_nickname":      "Please specify a new nickname.",
        "no_word":          "Please specify a word.",
        "no_channel":       "Please specify a member whose messages to purge.",

        # kick / ban / unban
        "kicked":           "### 👟 User Kicked\n**{member}** has been kicked.\n**Reason:** {reason}",
        "banned":           "### 🔨 User Banned\n**{member}** has been banned.\n**Reason:** {reason}",
        "unbanned":         "### ✅ User Unbanned\n**{user}** has been unbanned.",

        # warn
        "warned":           "### ⚠️ User Warned\n**{member}** has been warned.\n**Reason:** {reason}",
        "no_warnings":      "{member} has no warnings.",
        "warnings_title":   "### ⚠️ Warnings for {member}\n",
        "warnings_cleared": "✅ Cleared warnings for {member}.",
        "no_member_warns":  "Please specify a member to clear warnings for.",

        # mute / unmute
        "muted":            "🔇 Muted **{member}** | Reason: {reason}",
        "tempmuted":        "⏳ Muted **{member}** for `{duration}s` | Reason: {reason}",
        "unmuted":          "🔊 Unmuted **{member}**.",

        # clear / purge
        "cleared":          "🧹 Deleted `{count}` messages.",
        "purged":           "🧹 Deleted `{count}` messages from **{member}**.",

        # slowmode / lock / unlock
        "slowmode_set":     "🐢 Slowmode set to `{seconds}` seconds.",
        "locked":           "🔒 Channel locked.",
        "unlocked":         "🔓 Channel unlocked.",

        # nick
        "nick_changed":     "✏️ Changed nickname for **{member}** to `{nickname}`.",

        # modlog
        "modlog_set":       "### {emoji} Mod-Log Channel Set\nMod-Log channel set to {channel}",
        "modlog_removed":   "### {emoji} Mod-Log Channel Removed\nTo set a mod-log channel, use `{prefix}setmodlog #channel`",

        # badwords
        "badwords_none":    "No blocked words set for this server.",
        "badwords_added":   "Added `{word}` to the blocked words list.",
        "badwords_removed": "Removed `{word}` from the blocked words list.",
        "badwords_cleared": "Cleared all blocked words for this server.",

        # whitelist
        "wl_user_added":    "✅ Added {target} to the automod whitelist.",
        "wl_user_removed":  "✅ Removed {target} from the automod whitelist.",
        "wl_role_added":    "✅ Added {target} to the automod whitelist.",
        "wl_role_removed":  "✅ Removed {target} from the automod whitelist.",
        "wl_invalid_type":  "Invalid type. Use `user` or `role`.",
        "wl_empty":         "No users or roles are whitelisted.",
        "wl_title":         "### 🔓 AutoMod Whitelist\n",
        "wl_users":         "**Whitelisted Users**\n{users}\n\n",
        "wl_roles":         "**Whitelisted Roles**\n{roles}",
    },
    "de": {
        # generic
        "no_member":        "Bitte gib einen Benutzer an, den du {action} möchtest.",
        "no_user_id":       "Bitte gib eine Benutzer-ID zum Entbannen an.",
        "no_amount":        "Bitte gib eine Anzahl von Nachrichten zum Löschen an.",
        "no_duration":      "Bitte gib eine Dauer in Sekunden an.",
        "no_nickname":      "Bitte gib einen neuen Spitznamen an.",
        "no_word":          "Bitte gib ein Wort an.",
        "no_channel":       "Bitte gib ein Mitglied an, dessen Nachrichten gelöscht werden sollen.",

        # kick / ban / unban
        "kicked":           "### 👟 Benutzer gekickt\n**{member}** wurde gekickt.\n**Grund:** {reason}",
        "banned":           "### 🔨 Benutzer gebannt\n**{member}** wurde gebannt.\n**Grund:** {reason}",
        "unbanned":         "### ✅ Benutzer entbannt\n**{user}** wurde entbannt.",

        # warn
        "warned":           "### ⚠️ Benutzer verwarnt\n**{member}** wurde verwarnt.\n**Grund:** {reason}",
        "no_warnings":      "{member} hat keine Verwarnungen.",
        "warnings_title":   "### ⚠️ Verwarnungen für {member}\n",
        "warnings_cleared": "✅ Verwarnungen für {member} gelöscht.",
        "no_member_warns":  "Bitte gib ein Mitglied an, dessen Verwarnungen gelöscht werden sollen.",

        # mute / unmute
        "muted":            "🔇 **{member}** stummgeschaltet | Grund: {reason}",
        "tempmuted":        "⏳ **{member}** für `{duration}s` stummgeschaltet | Grund: {reason}",
        "unmuted":          "🔊 **{member}** entstummt.",

        # clear / purge
        "cleared":          "🧹 `{count}` Nachrichten gelöscht.",
        "purged":           "🧹 `{count}` Nachrichten von **{member}** gelöscht.",

        # slowmode / lock / unlock
        "slowmode_set":     "🐢 Langsamodus auf `{seconds}` Sekunden gesetzt.",
        "locked":           "🔒 Kanal gesperrt.",
        "unlocked":         "🔓 Kanal entsperrt.",

        # nick
        "nick_changed":     "✏️ Spitzname von **{member}** zu `{nickname}` geändert.",

        # modlog
        "modlog_set":       "### {emoji} Mod-Log-Kanal gesetzt\nMod-Log-Kanal wurde auf {channel} gesetzt.",
        "modlog_removed":   "### {emoji} Mod-Log-Kanal entfernt\nVerwende `{prefix}setmodlog #kanal`, um einen Kanal zu setzen.",

        # badwords
        "badwords_none":    "Keine gesperrten Wörter für diesen Server.",
        "badwords_added":   "`{word}` zur Sperrliste hinzugefügt.",
        "badwords_removed": "`{word}` aus der Sperrliste entfernt.",
        "badwords_cleared": "Alle gesperrten Wörter für diesen Server gelöscht.",

        # whitelist
        "wl_user_added":    "✅ {target} zur AutoMod-Whitelist hinzugefügt.",
        "wl_user_removed":  "✅ {target} aus der AutoMod-Whitelist entfernt.",
        "wl_role_added":    "✅ {target} zur AutoMod-Whitelist hinzugefügt.",
        "wl_role_removed":  "✅ {target} aus der AutoMod-Whitelist entfernt.",
        "wl_invalid_type":  "Ungültiger Typ. Verwende `user` oder `role`.",
        "wl_empty":         "Keine Benutzer oder Rollen auf der Whitelist.",
        "wl_title":         "### 🔓 AutoMod-Whitelist\n",
        "wl_users":         "**Benutzer auf Whitelist**\n{users}\n\n",
        "wl_roles":         "**Rollen auf Whitelist**\n{roles}",
    },
}


def get_lang(ctx: commands.Context) -> str:
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"


def msg(ctx: commands.Context, key: str, **kwargs) -> str:
    lang = get_lang(ctx)
    text = MESSAGES.get(lang, {}).get(key) or MESSAGES["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text


def _cv2(text: str) -> discord.ui.LayoutView:
    """Shorthand: wrap plain text in a cv2 container."""
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return view


# ─────────────────────────────────────────────────────────────
#  MODERATION COG
# ─────────────────────────────────────────────────────────────

class Moderation(commands.Cog):
    """Staff-facing moderation commands."""

    def __init__(self, bot):
        self.bot = bot

    def utils(self):
        return self.bot.get_cog("ModerationUtils")

    # ──── KICK / BAN / UNBAN ────────────────────────────────

    @commands.command(help="Kick a member from the server. | Mitglied kicken.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="kick"))
        await member.kick(reason=reason)
        await ctx.send(view=_cv2(msg(ctx, "kicked", member=member, reason=reason)))
        await self.utils().log_action(ctx.guild, "Kick", f"{member} was kicked by {ctx.author}.\nReason: {reason}")

    @commands.command(help="Ban a member from the server. | Mitglied bannen.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="ban"))
        await member.ban(reason=reason)
        try:
            await ctx.send(view=_cv2(msg(ctx, "banned", member=member, reason=reason)))
        except Exception as e:
            error("moderation", f"Error sending ban message: {e}")
            await ctx.send(f"{get_emoji('icon_tick')} Banned {member} | Reason: {reason}")
        await self.utils().log_action(ctx.guild, "Ban", f"{member} was banned by {ctx.author}.\nReason: {reason}")

    @commands.command(help="Unban a user by ID. | Benutzer per ID entbannen.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int = None):
        if not user_id:
            return await ctx.send(msg(ctx, "no_user_id"))
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(view=_cv2(msg(ctx, "unbanned", user=user)))
        await self.utils().log_action(ctx.guild, "Unban", f"{user} was unbanned by {ctx.author}.")

    # ──── WARN ──────────────────────────────────────────────

    @commands.command(help="Warn a member. | Mitglied verwarnen.")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="warn"))
        utils.add_warn(ctx.guild.id, member.id, ctx.author.id, reason)
        await ctx.send(view=_cv2(msg(ctx, "warned", member=member, reason=reason)))
        await utils.log_action(ctx.guild, "Warn", f"{member} was warned by {ctx.author}.\nReason: {reason}")

    @commands.command(help="View a member's warnings. | Verwarnungen anzeigen.")
    @commands.has_permissions(moderate_members=True)
    async def warnings(self, ctx, member: discord.Member = None):
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="view warnings for"))
        warns = utils.get_warnings(ctx.guild.id, member.id)
        if not warns:
            return await ctx.send(msg(ctx, "no_warnings", member=member))

        lines = msg(ctx, "warnings_title", member=member)
        for i, w in enumerate(warns, start=1):
            mod = ctx.guild.get_member(w["mod"])
            lines += f"**#{i}** by {mod or w['mod']}\nReason: {w['reason']}\nTime: {w['time']}\n\n"

        await ctx.send(view=_cv2(lines))

    @commands.command(help="Clear all warnings for a member. | Verwarnungen löschen.")
    @commands.has_permissions(moderate_members=True)
    async def clearwarnings(self, ctx, member: discord.Member = None):
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member_warns"))
        utils.clear_warnings(ctx.guild.id, member.id)
        await ctx.send(msg(ctx, "warnings_cleared", member=member))
        await utils.log_action(ctx.guild, "Clear Warnings", f"{ctx.author} cleared warnings for {member}.")

    # ──── MUTE / UNMUTE / TEMPMUTE ──────────────────────────

    @commands.command(help="Mute a member. | Mitglied stummschalten.")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="mute"))
        await utils.mute_member(ctx.guild, member, duration=None, reason=reason)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(ctx, "muted", member=member, reason=reason)
            )
        )
        view.add_item(container)
        await ctx.send(view=view)
        await utils.log_action(ctx.guild, "Mute", f"{member} was muted by {ctx.author}.\nReason: {reason}")

    @commands.command(help="Temporarily mute a member (seconds). | Zeitlich stummschalten.")
    @commands.has_permissions(moderate_members=True)
    async def tempmute(self, ctx, member: discord.Member = None, duration: int = None, *, reason: str = "No reason provided"):
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="tempmute"))
        if not duration:
            return await ctx.send(msg(ctx, "no_duration"))
        await utils.mute_member(ctx.guild, member, duration=duration, reason=reason)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(ctx, "tempmuted", member=member, duration=duration, reason=reason)
            )
        )
        view.add_item(container)
        await ctx.send(view=view)
        await utils.log_action(ctx.guild, "Tempmute", f"{member} was tempmuted by {ctx.author} for {duration}s.\nReason: {reason}")

    @commands.command(help="Unmute a member. | Stummschaltung aufheben.")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member = None):
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="unmute"))
        await utils.unmute_member(member, reason=f"Unmuted by {ctx.author}")
        await ctx.send(msg(ctx, "unmuted", member=member))
        await utils.log_action(ctx.guild, "Unmute", f"{member} was unmuted by {ctx.author}.")

    # ──── CLEAR / PURGE ─────────────────────────────────────

    @commands.command(help="Clear messages in this channel. | Nachrichten löschen.")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = None):
        if not amount:
            return await ctx.send(msg(ctx, "no_amount"))
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(msg(ctx, "cleared", count=len(deleted)), delete_after=5)
        await self.utils().log_action(ctx.guild, "Clear", f"{ctx.author} deleted {len(deleted)} messages in {ctx.channel.mention}.")

    @commands.command(help="Purge messages from a specific user. | Nachrichten eines Nutzers löschen.")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, member: discord.Member = None, amount: int = 100):
        if not member:
            return await ctx.send(msg(ctx, "no_channel"))
        def check(m):
            return m.author.id == member.id
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, check=check)
        await ctx.send(msg(ctx, "purged", count=len(deleted), member=member), delete_after=5)
        await self.utils().log_action(ctx.guild, "Purge", f"{ctx.author} purged {len(deleted)} messages from {member} in {ctx.channel.mention}.")

    # ──── SLOWMODE / LOCK / UNLOCK ──────────────────────────

    @commands.command(help="Set slowmode in this channel (seconds). | Langsammodus setzen.")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(msg(ctx, "slowmode_set", seconds=seconds))

    @commands.command(help="Lock this channel. | Kanal sperren.")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(msg(ctx, "locked"))
        await self.utils().log_action(ctx.guild, "Lock", f"{ctx.author} locked {ctx.channel.mention}.")

    @commands.command(help="Unlock this channel. | Kanal entsperren.")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(msg(ctx, "unlocked"))
        await self.utils().log_action(ctx.guild, "Unlock", f"{ctx.author} unlocked {ctx.channel.mention}.")

    # ──── NICKNAME ───────────────────────────────────────────

    @commands.command(help="Change a member's nickname. | Spitznamen ändern.")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member = None, *, nickname: str = None):
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="rename"))
        if not nickname:
            return await ctx.send(msg(ctx, "no_nickname"))
        await member.edit(nick=nickname)
        await ctx.send(msg(ctx, "nick_changed", member=member, nickname=nickname))
        await self.utils().log_action(ctx.guild, "Nickname Changed", f"{ctx.author} changed {member}'s nickname to `{nickname}`")

    # ──── MODLOG CONFIG ──────────────────────────────────────

    @commands.command(help="Set the mod-log channel. | Mod-Log-Kanal setzen.")
    @commands.has_permissions(manage_guild=True)
    async def setmodlog(self, ctx, channel: discord.TextChannel = None):
        prefix = self.bot.command_prefix
        utils = self.utils()
        cid = channel.id if channel else None
        utils.set_modlog_channel(ctx.guild.id, cid)
        if channel:
            emoji = get_emoji("icon_tick")
            text = msg(ctx, "modlog_set", channel=channel.mention, emoji=emoji)
        else:
            emoji = get_emoji("icon_cross")
            text = msg(ctx, "modlog_removed", prefix=prefix, emoji=emoji)
        await ctx.send(view=_cv2(text))

    # ──── BLOCKED WORD LIST ──────────────────────────────────

    @commands.group(name="badwords", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def badwords(self, ctx):
        """Show the blocked word list."""
        utils = self.utils()
        words = utils.get_blocked_words(ctx.guild.id)
        if not words:
            return await ctx.send(msg(ctx, "badwords_none"))
        text = "### 🚫 Blocked Words\n" + "\n".join(f"- {w}" for w in words)
        text += f"\n\n-# Use `{ctx.prefix}badwords add <word>` to add a word."
        await ctx.send(view=_cv2(text))

    @badwords.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def badwords_add(self, ctx, *, word: str = None):
        utils = self.utils()
        if not word:
            return await ctx.send(msg(ctx, "no_word"))
        utils.add_blocked_word(ctx.guild.id, word)
        await ctx.send(msg(ctx, "badwords_added", word=word))

    @badwords.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def badwords_remove(self, ctx, *, word: str = None):
        utils = self.utils()
        if not word:
            return await ctx.send(msg(ctx, "no_word"))
        utils.remove_blocked_word(ctx.guild.id, word)
        await ctx.send(msg(ctx, "badwords_removed", word=word))

    @badwords.command(name="clear")
    @commands.has_permissions(manage_guild=True)
    async def badwords_clear(self, ctx):
        utils = self.utils()
        utils.clear_blocked_words(ctx.guild.id)
        await ctx.send(msg(ctx, "badwords_cleared"))

    # ──── WHITELIST ──────────────────────────────────────────

    @commands.group(name="whitelist", aliases=["wl"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def whitelist(self, ctx):
        """Show the automod whitelist."""
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
        await ctx.send(view=_cv2(text))

    @whitelist.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def whitelist_add(self, ctx, target_type: str = None, target: str = None):
        """Add a user or role to the automod whitelist.
        Usage: .whitelist add user @member | .whitelist add role @role
        """
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
            await ctx.send(msg(ctx, "wl_user_added", target=member.mention))

        else:  # role
            role = None
            if ctx.message.role_mentions:
                role = ctx.message.role_mentions[0]
            elif target and target.isdigit():
                role = ctx.guild.get_role(int(target))
            if not role:
                return await ctx.send("Could not find that role.")
            utils.add_whitelist_role(ctx.guild.id, role.id)
            await ctx.send(msg(ctx, "wl_role_added", target=role.mention))

    @whitelist.command(name="remove", aliases=["rm"])
    @commands.has_permissions(manage_guild=True)
    async def whitelist_remove(self, ctx, target_type: str = None, target: str = None):
        """Remove a user or role from the automod whitelist.
        Usage: .whitelist remove user @member | .whitelist remove role @role
        """
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
            await ctx.send(msg(ctx, "wl_user_removed", target=member.mention))

        else:  # role
            role = None
            if ctx.message.role_mentions:
                role = ctx.message.role_mentions[0]
            elif target and target.isdigit():
                role = ctx.guild.get_role(int(target))
            if not role:
                return await ctx.send("Could not find that role.")
            utils.remove_whitelist_role(ctx.guild.id, role.id)
            await ctx.send(msg(ctx, "wl_role_removed", target=role.mention))


async def setup(bot):
    await bot.add_cog(Moderation(bot))
