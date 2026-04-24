import discord
from discord.ext import commands
from utils import logging as log
from utils.logging import info, success, warning, error, debug
from config.emojis import get_emoji

# ───────────────────────────────────────────────────
#  BILINGUAL MESSAGE TABLE
# ───────────────────────────────────────────────────

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
    "es": {
        # generic
        "no_member":        "Por favor especifica un miembro al que {action}.",
        "no_user_id":       "Por favor proporciona un ID de usuario para desbanear.",
        "no_amount":        "Por favor especifica una cantidad de mensajes a borrar.",
        "no_duration":      "Por favor especifica una duración en segundos.",
        "no_nickname":      "Por favor especifica un nuevo apodo.",
        "no_word":          "Por favor especifica una palabra.",
        "no_channel":       "Por favor especifica un miembro cuyos mensajes borrar.",

        # kick / ban / unban
        "kicked":           "### 👟 Usuario Expulsado\n**{member}** ha sido expulsado.\n**Razón:** {reason}",
        "banned":           "### 🔨 Usuario Baneado\n**{member}** ha sido baneado.\n**Razón:** {reason}",
        "unbanned":         "### ✅ Usuario Desbaneado\n**{user}** ha sido desbaneado.",

        # warn
        "warned":           "### ⚠️ Usuario Advertido\n**{member}** ha sido advertido.\n**Razón:** {reason}",
        "no_warnings":      "{member} no tiene advertencias.",
        "warnings_title":   "### ⚠️ Advertencias de {member}\n",
        "warnings_cleared": "✅ Advertencias borradas para {member}.",
        "no_member_warns":  "Por favor especifica un miembro cuyas advertencias borrar.",

        # mute / unmute
        "muted":            "🔇 **{member}** silenciado | Razón: {reason}",
        "tempmuted":        "⏳ **{member}** silenciado por `{duration}s` | Razón: {reason}",
        "unmuted":          "🔊 **{member}** desilenciado.",

        # clear / purge
        "cleared":          "🧹 Borrados `{count}` mensajes.",
        "purged":           "🧹 Borrados `{count}` mensajes de **{member}**.",

        # slowmode / lock / unlock
        "slowmode_set":     "🐢 Modo lento ajustado a `{seconds}` segundos.",
        "locked":           "🔒 Canal bloqueado.",
        "unlocked":         "🔓 Canal desbloqueado.",

        # nick
        "nick_changed":     "✏️ Apodo de **{member}** cambiado a `{nickname}`.",

        # badwords
        "badwords_none":    "No hay palabras bloqueadas configuradas para este servidor.",
        "badwords_added":   "Se añadió `{word}` a la lista de palabras bloqueadas.",
        "badwords_removed": "Se eliminó `{word}` de la lista de palabras bloqueadas.",
        "badwords_cleared": "Se eliminaron todas las palabras bloqueadas para este servidor.",

        # whitelist
        "wl_user_added":    "✅ {target} añadido a la lista blanca de automod.",
        "wl_user_removed":  "✅ {target} eliminado de la lista blanca de automod.",
        "wl_role_added":    "✅ {target} añadido a la lista blanca de automod.",
        "wl_role_removed":  "✅ {target} eliminado de la lista blanca de automod.",
        "wl_invalid_type":  "Tipo inválido. Usa `user` o `role`.",
        "wl_empty":         "No hay usuarios ni roles en la lista blanca.",
        "wl_title":         "### 🔓 Lista Blanca de AutoMod\n",
        "wl_users":         "**Usuarios en Lista Blanca**\n{users}\n\n",
        "wl_roles":         "**Roles en Lista Blanca**\n{roles}",
    },
}


def get_lang(ctx: commands.Context) -> str:
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
        if str(ctx.guild.preferred_locale).lower().startswith("es"):
            return "es"
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


# ───────────────────────────────────────────────────
#  MODERATION COG
# ───────────────────────────────────────────────────

class Moderation(commands.Cog):
    """Staff-facing moderation commands."""

    def __init__(self, bot):
        self.bot = bot

    def utils(self):
        return self.bot.get_cog("ModerationUtils")

    def logger(self):
        return self.bot.get_cog("ServerLogger")

    # ──── KICK / BAN / UNBAN ───────────────────────
    # help command uses json for multilangual help
    @commands.hybrid_command(description="Kick a member from the server", help="{ 'en': 'Kick a member from the server.', 'de': 'Mitglied kicken.', 'es': 'Expulsa a un miembro del servidor.' }")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="kick"))
        await member.kick(reason=reason)
        await ctx.send(view=_cv2(msg(ctx, "kicked", member=member, reason=reason)))
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Action:** Kick\n"
            f"**Reason:** {reason}\n"
            f"**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(
            ctx.guild, "moderation", "Kick", body,
            target_id=member.id, action_key="Kick"
        )

    @commands.hybrid_command(description="Ban a member from the server", help="{ 'en': 'Ban a member from the server.', 'de': 'Mitglied bannen.', 'es': 'Banea a un miembro del servidor.' }")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.User = None, *, reason: str = "No reason provided"):
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="ban"))
                
        await ctx.guild.ban(member, reason=reason, delete_message_days=7)
        await ctx.send(view=_cv2(msg(ctx, "banned", member=member, reason=reason)))
        guild = ctx.guild
        moderator = ctx.author
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Action:** Ban\n"
            f"**Reason:** {reason or 'No reason provided'}\n"
            f"**Moderator:** {moderator.mention if moderator else 'Unknown'}"
        )
        await self.logger().log_event(
            guild, "moderation", "Ban", body, 
            target_id=member.id, action_key="Ban"
        )

    @commands.hybrid_command(description="Unban a user by ID", help="{ 'en': 'Unban a member from the server.', 'de': 'Mitglied entbannen.', 'es': 'Desbanea a un miembro del servidor.' }")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id = None, reason = None):
        if not user_id:
            return await ctx.send(msg(ctx, "no_user_id"))
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(view=_cv2(msg(ctx, "unbanned", user=user)))
        guild = ctx.guild
        moderator = ctx.author
        body = (
            f"**User:** {user.mention} (`{user}` — ID: `{user.id}`)\n"
            f"**Action:** Unban\n"
            f"**Reason:** {reason or 'No reason provided'}\n"
            f"**Moderator:** {moderator.mention if moderator else 'Unknown'}"
        )
        await self.logger().log_event(
            guild, "moderation", "Unban", body, 
            target_id=user.id, action_key="Unban"
        )

    # ──── WARN ─────────────────────────────────────

    @commands.hybrid_command(description="Warn a member", help="{ 'en': 'Warn a member.', 'de': 'Mitglied verwarnen.', 'es': 'Advierte a un miembro.' }")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="warn"))
        utils.add_warn(ctx.guild.id, member.id, ctx.author.id, reason)
        await ctx.send(view=_cv2(msg(ctx, "warned", member=member, reason=reason)))
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Action:** Warn\n"
            f"**Reason:** {reason}\n"
            f"**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(
            ctx.guild, "moderation", "Warn", body,
            target_id=member.id, action_key="Warn"
        )

    @commands.hybrid_command(description="View a member's warnings", help="{ 'en': 'View a members warnings.', 'de': 'Verwarnungen anzeigen.', 'es': 'Ver las advertencias de un miembro.' }")
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

    @commands.hybrid_command(description="Clear all warnings for a member", help="{ 'en': 'Clear all warnings for a member.', 'de': 'Verwarnungen löschen.', 'es': 'Borra todas las advertencias de un miembro.' }")
    @commands.has_permissions(moderate_members=True)
    async def clearwarnings(self, ctx, member: discord.Member = None):
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member_warns"))
        utils.clear_warnings(ctx.guild.id, member.id)
        await ctx.send(msg(ctx, "warnings_cleared", member=member))
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Action:** Clear Warnings\n"
            f"**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(
            ctx.guild, "moderation", "Clear Warnings", body,
            target_id=member.id
        )

    # ──── MUTE / UNMUTE / TEMPMUTE ─────────────────

    @commands.hybrid_command(description="Mute a member", help="{ 'en': 'Mute a member.', 'de': 'Mitglied stummschalten.', 'es': 'Silencia a un miembro.' }")
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
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Action:** Mute\n"
            f"**Reason:** {reason}\n"
            f"**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(
            ctx.guild, "moderation", "Mute", body,
            target_id=member.id, action_key="Mute"
        )

    @commands.hybrid_command(description="Temporarily mute a member (seconds)", help="{ 'en': 'Temporarily mute a member (seconds).', 'de': 'Zeitlich stummschalten.', 'es': 'Silencia temporalmente a un miembro (segundos).' }")
    @commands.has_permissions(moderate_members=True)
    async def tempmute(self, ctx, member: discord.Member = None, duration = None, *, reason: str = "No reason provided"):
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
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Action:** Tempmute\n"
            f"**Duration:** {duration}s\n"
            f"**Reason:** {reason}\n"
            f"**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(
            ctx.guild, "moderation", "Tempmute", body,
            target_id=member.id, action_key="Tempmute"
        )

    @commands.hybrid_command(description="Unmute a member", help="{ 'en': 'Unmute a member.', 'de': 'Stummschaltung aufheben.', 'es': 'Quita el silencio a un miembro.' }")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member = None):
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="unmute"))
        await utils.unmute_member(member, reason=f"Unmuted by {ctx.author}")
        await ctx.send(msg(ctx, "unmuted", member=member))
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Action:** Unmute\n"
            f"**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(
            ctx.guild, "moderation", "Unmute", body,
            target_id=member.id
        )

    # ──── CLEAR / PURGE ────────────────────────────

    @commands.hybrid_command(description="Clear messages in this channel", help="{ 'en': 'Clear messages in this channel.', 'de': 'Nachrichten löschen.', 'es': 'Borra mensajes en este canal.' }")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount = None):
        if not amount:
            return await ctx.send(msg(ctx, "no_amount"))
        amount = int(amount)
        try:
            await ctx.message.delete()
        except (discord.HTTPException, AttributeError):
            pass
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(msg(ctx, "cleared", count=len(deleted)), delete_after=5)
        body = (
            f"**Channel:** {ctx.channel.mention}\n"
            f"**Messages Deleted:** {len(deleted)}\n"
            f"**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(
            ctx.guild, "moderation", "Clear", body,
            action_key="Clear"
        )

    @commands.hybrid_command(description="Purge messages from a specific user", help="{ 'en': 'Purge messages from a specific user.', 'de': 'Nachrichten eines Nutzers löschen.', 'es': 'Elimina mensajes de un usuario específico.' }")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, member: discord.Member = None, amount: int = 100):
        if not member:
            return await ctx.send(msg(ctx, "no_channel"))
        def check(m):
            return m.author.id == member.id
        try:
            await ctx.message.delete()
        except (discord.HTTPException, AttributeError):
            pass
        deleted = await ctx.channel.purge(limit=amount, check=check)
        await ctx.send(msg(ctx, "purged", count=len(deleted), member=member), delete_after=5)
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Channel:** {ctx.channel.mention}\n"
            f"**Messages Deleted:** {len(deleted)}\n"
            f"**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(
            ctx.guild, "messages", "Purge", body,
            target_id=member.id, action_key="Purge"
        )

    # ──── SLOWMODE / LOCK / UNLOCK ─────────────────

    @commands.hybrid_command(description="Set slowmode in this channel (seconds)", help="{ 'en': 'Set slowmode in this channel (seconds).', 'de': 'Langsammodus setzen.', 'es': 'Establece el modo lento en este canal (segundos).' }")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(msg(ctx, "slowmode_set", seconds=seconds))

    @commands.hybrid_command(description="Lock this channel", help="{ 'en': 'Lock this channel.', 'de': 'Kanal sperren.', 'es': 'Bloquea este canal.' }")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(msg(ctx, "locked"))
        body = (
            f"**Channel:** {ctx.channel.mention}\n"
            f"**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(
            ctx.guild, "channels", "Lock", body,
            channel_id=ctx.channel.id, action_key="Lock"
        )

    @commands.hybrid_command(description="Unlock this channel", help="{ 'en': 'Unlock this channel.', 'de': 'Kanal entsperren.', 'es': 'Desbloquea este canal.' }")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(msg(ctx, "unlocked"))
        body = (
            f"**Channel:** {ctx.channel.mention}\n"
            f"**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(
            ctx.guild, "channels", "Unlock", body,
            channel_id=ctx.channel.id, action_key="Unlock"
        )

    # ──── NICKNAME ─────────────────────────────────

    @commands.hybrid_command(description="Change a member's nickname", help="{ 'en': 'Change a members nickname.', 'de': 'Spitznamen ändern.', 'es': 'Cambia el apodo de un miembro.' }")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member = None, *, nickname = None):
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="rename"))
        if not nickname:
            return await ctx.send(msg(ctx, "no_nickname"))
        await member.edit(nick=nickname)
        await ctx.send(msg(ctx, "nick_changed", member=member, nickname=nickname))
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**New Nickname:** `{nickname}`\n"
            f"**Changed By:** {ctx.author.mention}"
        )
        await self.logger().log_event(
            ctx.guild, "moderation", "Nickname Changed", body,
            target_id=member.id
        )

    # ──── BLOCKED WORD LIST ────────────────────────

    @commands.hybrid_group(name="badwords", invoke_without_command=True, description="Manage the blocked word list", help="{ 'en': 'Manage the blocked word list.', 'de': 'Verwalte die Liste blockierter Wörter.', 'es': 'Gestiona la lista de palabras bloqueadas.' }")
    @commands.has_permissions(manage_guild=True)
    async def badwords(self, ctx):
        """Show the blocked word list."""
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

    @badwords.command(name="remove", description="Remove a blocked word")
    @commands.has_permissions(manage_guild=True)
    async def badwords_remove(self, ctx, *, word: str = None):
        utils = self.utils()
        if not word:
            return await ctx.send(msg(ctx, "no_word"))
        utils.remove_blocked_word(ctx.guild.id, word)
        await ctx.send(msg(ctx, "badwords_removed", word=word))

    @badwords.command(name="clear", description="Clear all blocked words")
    @commands.has_permissions(manage_guild=True)
    async def badwords_clear(self, ctx):
        utils = self.utils()
        utils.clear_blocked_words(ctx.guild.id)
        await ctx.send(msg(ctx, "badwords_cleared"))

    # ──── WHITELIST ────────────────────────────────

    @commands.hybrid_group(name="whitelist", aliases=["wl"], invoke_without_command=True, description="Manage the automod whitelist", help="{ 'en': 'Manage the automod whitelist.', 'de': 'Verwalte die Automod-Whitelist.', 'es': 'Gestiona la lista blanca de automod.' }")
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
        await ctx.send(view=_cv2(text), allowed_mentions=discord.AllowedMentions.none())

    @whitelist.command(name="add", description="Add a user or role to the automod whitelist")
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
            await ctx.send(msg(ctx, "wl_user_added", target=member.mention), allowed_mentions=discord.AllowedMentions.none())

        else:  # role
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
            await ctx.send(msg(ctx, "wl_user_removed", target=member.mention), allowed_mentions=discord.AllowedMentions.none())

        else:  # role
            role = None
            if ctx.message.role_mentions:
                role = ctx.message.role_mentions[0]
            elif target and target.isdigit():
                role = ctx.guild.get_role(int(target))
            if not role:
                return await ctx.send("Could not find that role.")
            utils.remove_whitelist_role(ctx.guild.id, role.id)
            await ctx.send(msg(ctx, "wl_role_removed", target=role.mention), allowed_mentions=discord.AllowedMentions.none())

    @commands.hybrid_command(name="setmodlog", description="Set the moderation log channel (deprecated)", help="{ 'en': 'Set the moderation log channel.', 'de': 'Moderationslog-Kanal setzen.', 'es': 'Establece el canal de registro de moderación.' }")
    async def setmodlog(self, ctx):
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content="### Important Notice"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="This command has been moved to the new logging system and is scheduled for removal in a future update. Please use `.logging` instead."
            )
        )
        view.add_item(container)
        await ctx.reply(view=view)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
