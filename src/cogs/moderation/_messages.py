"""
Moderation i18n — MESSAGES table, msg() helper, and shared view/purge utilities.
"""
import discord
from utils.i18n import make_flat_msg
from utils.ratelimit import purge_limiter

MESSAGES = {
    "en": {
        "no_member":        "Please specify a member to {action}.",
        "no_user_id":       "Please provide a user ID to unban.",
        "no_amount":        "Please specify an amount of messages to delete.",
        "no_duration":      "Please specify a duration in seconds.",
        "no_nickname":      "Please specify a new nickname.",
        "no_word":          "Please specify a word.",
        "no_channel":       "Please specify a member whose messages to purge.",
        "kicked":           "### 👟 User Kicked\n**{member}** has been kicked.\n**Reason:** {reason}",
        "banned":           "### 🔨 User Banned\n**{member}** has been banned.\n**Reason:** {reason}",
        "unbanned":         "### ✅ User Unbanned\n**{user}** has been unbanned.",
        "warned":           "### ⚠️ User Warned\n**{member}** has been warned.\n**Reason:** {reason}",
        "no_warnings":      "{member} has no warnings.",
        "warnings_title":   "### ⚠️ Warnings for {member}\n",
        "warnings_cleared": "✅ Cleared warnings for {member}.",
        "no_member_warns":  "Please specify a member to clear warnings for.",
        "muted":            "🔇 Muted **{member}** | Reason: {reason}",
        "tempmuted":        "⏳ Muted **{member}** for `{duration}s` | Reason: {reason}",
        "unmuted":          "🔊 Unmuted **{member}**.",
        "cleared":          "🧹 Deleted `{count}` messages.",
        "purged":           "🧹 Deleted `{count}` messages from **{member}**.",
        "slowmode_set":     "🐢 Slowmode set to `{seconds}` seconds.",
        "locked":           "🔒 Channel locked.",
        "unlocked":         "🔓 Channel unlocked.",
        "nick_changed":     "✏️ Changed nickname for **{member}** to `{nickname}`.",
        "badwords_none":    "No blocked words set for this server.",
        "badwords_added":   "Added `{word}` to the blocked words list.",
        "badwords_removed": "Removed `{word}` from the blocked words list.",
        "badwords_cleared": "Cleared all blocked words for this server.",
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
        "no_member":        "Bitte gib einen Benutzer an, den du {action} möchtest.",
        "no_user_id":       "Bitte gib eine Benutzer-ID zum Entbannen an.",
        "no_amount":        "Bitte gib eine Anzahl von Nachrichten zum Löschen an.",
        "no_duration":      "Bitte gib eine Dauer in Sekunden an.",
        "no_nickname":      "Bitte gib einen neuen Spitznamen an.",
        "no_word":          "Bitte gib ein Wort an.",
        "no_channel":       "Bitte gib ein Mitglied an, dessen Nachrichten gelöscht werden sollen.",
        "kicked":           "### 👟 Benutzer gekickt\n**{member}** wurde gekickt.\n**Grund:** {reason}",
        "banned":           "### 🔨 Benutzer gebannt\n**{member}** wurde gebannt.\n**Grund:** {reason}",
        "unbanned":         "### ✅ Benutzer entbannt\n**{user}** wurde entbannt.",
        "warned":           "### ⚠️ Benutzer verwarnt\n**{member}** wurde verwarnt.\n**Grund:** {reason}",
        "no_warnings":      "{member} hat keine Verwarnungen.",
        "warnings_title":   "### ⚠️ Verwarnungen für {member}\n",
        "warnings_cleared": "✅ Verwarnungen für {member} gelöscht.",
        "no_member_warns":  "Bitte gib ein Mitglied an, dessen Verwarnungen gelöscht werden sollen.",
        "muted":            "🔇 **{member}** stummgeschaltet | Grund: {reason}",
        "tempmuted":        "⏳ **{member}** für `{duration}s` stummgeschaltet | Grund: {reason}",
        "unmuted":          "🔊 **{member}** entstummt.",
        "cleared":          "🧹 `{count}` Nachrichten gelöscht.",
        "purged":           "🧹 `{count}` Nachrichten von **{member}** gelöscht.",
        "slowmode_set":     "🐢 Langsamodus auf `{seconds}` Sekunden gesetzt.",
        "locked":           "🔒 Kanal gesperrt.",
        "unlocked":         "🔓 Kanal entsperrt.",
        "nick_changed":     "✏️ Spitzname von **{member}** zu `{nickname}` geändert.",
        "badwords_none":    "Keine gesperrten Wörter für diesen Server.",
        "badwords_added":   "`{word}` zur Sperrliste hinzugefügt.",
        "badwords_removed": "`{word}` aus der Sperrliste entfernt.",
        "badwords_cleared": "Alle gesperrten Wörter für diesen Server gelöscht.",
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
        "no_member":        "Por favor especifica un miembro al que {action}.",
        "no_user_id":       "Por favor proporciona un ID de usuario para desbanear.",
        "no_amount":        "Por favor especifica una cantidad de mensajes a borrar.",
        "no_duration":      "Por favor especifica una duración en segundos.",
        "no_nickname":      "Por favor especifica un nuevo apodo.",
        "no_word":          "Por favor especifica una palabra.",
        "no_channel":       "Por favor especifica un miembro cuyos mensajes borrar.",
        "kicked":           "### 👟 Usuario Expulsado\n**{member}** ha sido expulsado.\n**Razón:** {reason}",
        "banned":           "### 🔨 Usuario Baneado\n**{member}** ha sido baneado.\n**Razón:** {reason}",
        "unbanned":         "### ✅ Usuario Desbaneado\n**{user}** ha sido desbaneado.",
        "warned":           "### ⚠️ Usuario Advertido\n**{member}** ha sido advertido.\n**Razón:** {reason}",
        "no_warnings":      "{member} no tiene advertencias.",
        "warnings_title":   "### ⚠️ Advertencias de {member}\n",
        "warnings_cleared": "✅ Advertencias borradas para {member}.",
        "no_member_warns":  "Por favor especifica un miembro cuyas advertencias borrar.",
        "muted":            "🔇 **{member}** silenciado | Razón: {reason}",
        "tempmuted":        "⏳ **{member}** silenciado por `{duration}s` | Razón: {reason}",
        "unmuted":          "🔊 **{member}** desilenciado.",
        "cleared":          "🧹 Borrados `{count}` mensajes.",
        "purged":           "🧹 Borrados `{count}` mensajes de **{member}**.",
        "slowmode_set":     "🐢 Modo lento ajustado a `{seconds}` segundos.",
        "locked":           "🔒 Canal bloqueado.",
        "unlocked":         "🔓 Canal desbloqueado.",
        "nick_changed":     "✏️ Apodo de **{member}** cambiado a `{nickname}`.",
        "badwords_none":    "No hay palabras bloqueadas configuradas para este servidor.",
        "badwords_added":   "Se añadió `{word}` a la lista de palabras bloqueadas.",
        "badwords_removed": "Se eliminó `{word}` de la lista de palabras bloqueadas.",
        "badwords_cleared": "Se eliminaron todas las palabras bloqueadas para este servidor.",
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

msg = make_flat_msg(MESSAGES)


def _cv2(text: str) -> discord.ui.LayoutView:
    """Wrap plain text in a cv2 Container."""
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return view


async def _chunked_purge(channel, limit: int, check=None) -> list:
    """
    Delete messages in chunks of 100, acquiring purge_limiter between each
    batch to stay below Discord's bulk-delete rate limit.
    """
    deleted  = []
    remaining = limit
    while remaining > 0:
        chunk = min(remaining, 100)
        await purge_limiter.acquire(channel.id)
        kwargs = {"limit": chunk}
        if callable(check):
            kwargs["check"] = check
        batch = await channel.purge(**kwargs)
        deleted.extend(batch)
        remaining -= chunk
        if len(batch) < chunk:
            break
    return deleted
