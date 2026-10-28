"""
Moderation i18n — MESSAGES table, msg() helper, and shared view/purge utilities.

The strings carry ``{kick}``/``{warn}``-style placeholders instead of raw
Unicode emoji, and :data:`EMOJI` fills them with the bot's own art, so a
moderation reply draws the same neutral icons as every other Niko surface
rather than Discord's colourful built-ins.
"""
import discord
from config.emojis import get_emoji
from utils.i18n import make_flat_msg
from utils.ratelimit import purge_limiter

#: Filled into every message below by :func:`msg`. Module level on purpose:
#: the emoji sync rewrites these in place when an emoji is re-uploaded, so a
#: replacement reaches these replies without a restart.
EMOJI = {
    "kick":     get_emoji("log_kick"),
    "ban":      get_emoji("log_ban"),
    "unban":    get_emoji("log_unban"),
    "warn":     get_emoji("log_warn"),
    "tick":     get_emoji("tick"),
    "mute":     get_emoji("log_mute"),
    "tempmute": get_emoji("log_tempmute"),
    "unmute":   get_emoji("log_unmute"),
    "slowmode": get_emoji("pause"),
    "lock":     get_emoji("lock"),
    "unlock":   get_emoji("unlock"),
    "nick":     get_emoji("log_nickname"),
    "cross":    get_emoji("cross"),
}

MESSAGES = {
    "en": {
        "no_member":        "Please specify a member to {action}.",
        "no_user_id":       "Please provide a user ID to unban.",
        "no_duration":      "Please specify a duration in seconds.",
        "no_nickname":      "Please specify a new nickname.",
        "no_word":          "Please specify a word.",
        "kicked":           "### {kick} User Kicked\n**{member}** has been kicked.\n**Reason:** {reason}",
        "banned":           "### {ban} User Banned\n**{member}** has been banned.\n**Reason:** {reason}",
        "unbanned":         "### {unban} User Unbanned\n**{user}** has been unbanned.",
        "warned":           "### {warn} User Warned\n**{member}** has been warned.\n**Reason:** {reason}",
        "no_warnings":      "{member} has no warnings.",
        "warnings_title":   "### {warn} Warnings for {member}\n",
        "warnings_cleared": "{tick} Cleared warnings for {member}.",
        "no_member_warns":  "Please specify a member to clear warnings for.",
        "muted":            "{mute} Muted **{member}** | Reason: {reason}",
        "tempmuted":        "{tempmute} Muted **{member}** for `{duration}s` | Reason: {reason}",
        "unmuted":          "{unmute} Unmuted **{member}**.",
        "cleared":          "Deleted `{count}` messages.",
        "purged":           "Deleted `{count}` messages from **{member}**.",
        "slowmode_set":     "{slowmode} Slowmode set to `{seconds}` seconds.",
        "locked":           "{lock} Channel locked.",
        "unlocked":         "{unlock} Channel unlocked.",
        "nick_changed":     "{nick} Changed nickname for **{member}** to `{nickname}`.",
        "badwords_none":    "No blocked words set for this server.",
        "badwords_added":   "Added `{word}` to the blocked words list.",
        "badwords_removed": "Removed `{word}` from the blocked words list.",
        "badwords_cleared": "Cleared all blocked words for this server.",
        "wl_user_added":    "{tick} Added {target} to the automod whitelist.",
        "wl_user_removed":  "{tick} Removed {target} from the automod whitelist.",
        "wl_role_added":    "{tick} Added {target} to the automod whitelist.",
        "wl_role_removed":  "{tick} Removed {target} from the automod whitelist.",
        "wl_invalid_type":  "Invalid type. Use `user` or `role`.",
        "wl_bad_target":    "{cross} Give the {kind}'s ID or a mention — for example `.whitelist add {kind} 123456789012345678`.",
        "wl_role_missing":  "{cross} No role in this server has that ID.",
        "wl_empty":         "No users or roles are whitelisted.",
        "wl_title":         "### {unlock} AutoMod Whitelist\n",
        "wl_users":         "**Whitelisted Users**\n{users}\n\n",
        "wl_roles":         "**Whitelisted Roles**\n{roles}",
        # Confirmation prompts and the failures a moderation action can report.
        "confirm_kick":     "### {kick} Confirm Kick\nAre you sure you want to kick **{member}** (`{id}`)?\n**Reason:** {reason}",
        "confirm_ban":      "### {ban} Confirm Ban\nAre you sure you want to ban **{user}** (`{id}`)?\n-# Messages from the last **{days}** days are deleted too.\n**Reason:** {reason}",
        "cancelled":        "{cross} Action cancelled.",
        "timed_out":        "{cross} Confirmation timed out — nothing was done.",
        "invoker_only":     "{cross} Only the command invoker can use these buttons.",
        "bad_user_id":      "{cross} `{value}` is not a user ID. Give the numeric ID or a mention of the banned user.",
        "no_user_found":    "{cross} Could not find a user with that ID.",
        "not_banned":       "{cross} **{user}** is not banned in this server.",
        "cannot_kick":      "{cross} I don't have permission to kick that member.",
        "cannot_ban":       "{cross} I don't have permission to ban that user.",
        "cannot_unban":     "{cross} I don't have permission to unban that user.",
        "cannot_slowmode":  "{cross} I can't set slowmode here — check that I have **Manage Channels**.",
        "cannot_manage_channel": "{cross} I can't change this channel's permissions — check that I have **Manage Channels**.",
        "slowmode_limit":   "{cross} Slowmode can be at most `{max}` seconds ({hours} hours).",
        "nick_failed":      "{cross} I can't change that member's nickname — they may outrank me.",
        "warnings_perms":   "{cross} You need **Moderate Members** or **Manage Messages** to read warnings.",
        "cannot_purge":     "{cross} I couldn't delete messages here — check that I have **Manage Messages** and **Read Message History**.",
        "action_failed":    "{cross} That failed: {error}",
    },
    "de": {
        "no_member":        "Bitte gib einen Benutzer an, den du {action} möchtest.",
        "no_user_id":       "Bitte gib eine Benutzer-ID zum Entbannen an.",
        "no_duration":      "Bitte gib eine Dauer in Sekunden an.",
        "no_nickname":      "Bitte gib einen neuen Spitznamen an.",
        "no_word":          "Bitte gib ein Wort an.",
        "kicked":           "### {kick} Benutzer gekickt\n**{member}** wurde gekickt.\n**Grund:** {reason}",
        "banned":           "### {ban} Benutzer gebannt\n**{member}** wurde gebannt.\n**Grund:** {reason}",
        "unbanned":         "### {unban} Benutzer entbannt\n**{user}** wurde entbannt.",
        "warned":           "### {warn} Benutzer verwarnt\n**{member}** wurde verwarnt.\n**Grund:** {reason}",
        "no_warnings":      "{member} hat keine Verwarnungen.",
        "warnings_title":   "### {warn} Verwarnungen für {member}\n",
        "warnings_cleared": "{tick} Verwarnungen für {member} gelöscht.",
        "no_member_warns":  "Bitte gib ein Mitglied an, dessen Verwarnungen gelöscht werden sollen.",
        "muted":            "{mute} **{member}** stummgeschaltet | Grund: {reason}",
        "tempmuted":        "{tempmute} **{member}** für `{duration}s` stummgeschaltet | Grund: {reason}",
        "unmuted":          "{unmute} **{member}** entstummt.",
        "cleared":          "`{count}` Nachrichten gelöscht.",
        "purged":           "`{count}` Nachrichten von **{member}** gelöscht.",
        "slowmode_set":     "{slowmode} Langsamodus auf `{seconds}` Sekunden gesetzt.",
        "locked":           "{lock} Kanal gesperrt.",
        "unlocked":         "{unlock} Kanal entsperrt.",
        "nick_changed":     "{nick} Spitzname von **{member}** zu `{nickname}` geändert.",
        "badwords_none":    "Keine gesperrten Wörter für diesen Server.",
        "badwords_added":   "`{word}` zur Sperrliste hinzugefügt.",
        "badwords_removed": "`{word}` aus der Sperrliste entfernt.",
        "badwords_cleared": "Alle gesperrten Wörter für diesen Server gelöscht.",
        "wl_user_added":    "{tick} {target} zur AutoMod-Whitelist hinzugefügt.",
        "wl_user_removed":  "{tick} {target} aus der AutoMod-Whitelist entfernt.",
        "wl_role_added":    "{tick} {target} zur AutoMod-Whitelist hinzugefügt.",
        "wl_role_removed":  "{tick} {target} aus der AutoMod-Whitelist entfernt.",
        "wl_invalid_type":  "Ungültiger Typ. Verwende `user` oder `role`.",
        "wl_bad_target":    "{cross} Gib die ID oder eine Erwähnung des Ziels an — zum Beispiel `.whitelist add role 123456789012345678`.",
        "wl_role_missing":  "{cross} Keine Rolle auf diesem Server hat diese ID.",
        "wl_empty":         "Keine Benutzer oder Rollen auf der Whitelist.",
        "wl_title":         "### {unlock} AutoMod-Whitelist\n",
        "wl_users":         "**Benutzer auf Whitelist**\n{users}\n\n",
        "wl_roles":         "**Rollen auf Whitelist**\n{roles}",
        "confirm_kick":     "### {kick} Kick bestätigen\nWillst du **{member}** (`{id}`) wirklich kicken?\n**Grund:** {reason}",
        "confirm_ban":      "### {ban} Ban bestätigen\nWillst du **{user}** (`{id}`) wirklich bannen?\n-# Nachrichten der letzten **{days}** Tage werden dabei gelöscht.\n**Grund:** {reason}",
        "cancelled":        "{cross} Aktion abgebrochen.",
        "timed_out":        "{cross} Bestätigung abgelaufen — es wurde nichts geändert.",
        "invoker_only":     "{cross} Nur die Person, die den Befehl ausgeführt hat, kann diese Buttons benutzen.",
        "bad_user_id":      "{cross} `{value}` ist keine Benutzer-ID. Gib die numerische ID oder eine Erwähnung an.",
        "no_user_found":    "{cross} Es wurde kein Benutzer mit dieser ID gefunden.",
        "not_banned":       "{cross} **{user}** ist auf diesem Server nicht gebannt.",
        "cannot_kick":      "{cross} Ich habe keine Berechtigung, dieses Mitglied zu kicken.",
        "cannot_ban":       "{cross} Ich habe keine Berechtigung, diesen Benutzer zu bannen.",
        "cannot_unban":     "{cross} Ich habe keine Berechtigung, diesen Benutzer zu entbannen.",
        "cannot_slowmode":  "{cross} Ich kann hier keinen Langsammodus setzen — prüfe, ob ich **Kanäle verwalten** darf.",
        "cannot_manage_channel": "{cross} Ich kann die Berechtigungen dieses Kanals nicht ändern — prüfe, ob ich **Kanäle verwalten** darf.",
        "slowmode_limit":   "{cross} Der Langsammodus kann höchstens `{max}` Sekunden ({hours} Stunden) betragen.",
        "nick_failed":      "{cross} Ich kann den Spitznamen nicht ändern — das Mitglied ist vielleicht höher als ich.",
        "warnings_perms":   "{cross} Du brauchst **Mitglieder moderieren** oder **Nachrichten verwalten**, um Verwarnungen zu lesen.",
        "cannot_purge":     "{cross} Ich konnte hier keine Nachrichten löschen — prüfe, ob ich **Nachrichten verwalten** und **Nachrichtenverlauf lesen** darf.",
        "action_failed":    "{cross} Das ist fehlgeschlagen: {error}",
    },
    "es": {
        "no_member":        "Por favor especifica un miembro al que {action}.",
        "no_user_id":       "Por favor proporciona un ID de usuario para desbanear.",
        "no_duration":      "Por favor especifica una duración en segundos.",
        "no_nickname":      "Por favor especifica un nuevo apodo.",
        "no_word":          "Por favor especifica una palabra.",
        "kicked":           "### {kick} Usuario Expulsado\n**{member}** ha sido expulsado.\n**Razón:** {reason}",
        "banned":           "### {ban} Usuario Baneado\n**{member}** ha sido baneado.\n**Razón:** {reason}",
        "unbanned":         "### {unban} Usuario Desbaneado\n**{user}** ha sido desbaneado.",
        "warned":           "### {warn} Usuario Advertido\n**{member}** ha sido advertido.\n**Razón:** {reason}",
        "no_warnings":      "{member} no tiene advertencias.",
        "warnings_title":   "### {warn} Advertencias de {member}\n",
        "warnings_cleared": "{tick} Advertencias borradas para {member}.",
        "no_member_warns":  "Por favor especifica un miembro cuyas advertencias borrar.",
        "muted":            "{mute} **{member}** silenciado | Razón: {reason}",
        "tempmuted":        "{tempmute} **{member}** silenciado por `{duration}s` | Razón: {reason}",
        "unmuted":          "{unmute} **{member}** desilenciado.",
        "cleared":          "Borrados `{count}` mensajes.",
        "purged":           "Borrados `{count}` mensajes de **{member}**.",
        "slowmode_set":     "{slowmode} Modo lento ajustado a `{seconds}` segundos.",
        "locked":           "{lock} Canal bloqueado.",
        "unlocked":         "{unlock} Canal desbloqueado.",
        "nick_changed":     "{nick} Apodo de **{member}** cambiado a `{nickname}`.",
        "badwords_none":    "No hay palabras bloqueadas configuradas para este servidor.",
        "badwords_added":   "Se añadió `{word}` a la lista de palabras bloqueadas.",
        "badwords_removed": "Se eliminó `{word}` de la lista de palabras bloqueadas.",
        "badwords_cleared": "Se eliminaron todas las palabras bloqueadas para este servidor.",
        "wl_user_added":    "{tick} {target} añadido a la lista blanca de automod.",
        "wl_user_removed":  "{tick} {target} eliminado de la lista blanca de automod.",
        "wl_role_added":    "{tick} {target} añadido a la lista blanca de automod.",
        "wl_role_removed":  "{tick} {target} eliminado de la lista blanca de automod.",
        "wl_invalid_type":  "Tipo inválido. Usa `user` o `role`.",
        "wl_bad_target":    "{cross} Indica el ID o una mención del destino — por ejemplo `.whitelist add role 123456789012345678`.",
        "wl_role_missing":  "{cross} Ningún rol de este servidor tiene ese ID.",
        "wl_empty":         "No hay usuarios ni roles en la lista blanca.",
        "wl_title":         "### {unlock} Lista Blanca de AutoMod\n",
        "wl_users":         "**Usuarios en Lista Blanca**\n{users}\n\n",
        "wl_roles":         "**Roles en Lista Blanca**\n{roles}",
        "confirm_kick":     "### {kick} Confirmar expulsión\n¿Seguro que quieres expulsar a **{member}** (`{id}`)?\n**Razón:** {reason}",
        "confirm_ban":      "### {ban} Confirmar baneo\n¿Seguro que quieres banear a **{user}** (`{id}`)?\n-# También se borrarán los mensajes de los últimos **{days}** días.\n**Razón:** {reason}",
        "cancelled":        "{cross} Acción cancelada.",
        "timed_out":        "{cross} La confirmación caducó — no se hizo nada.",
        "invoker_only":     "{cross} Solo quien ejecutó el comando puede usar estos botones.",
        "bad_user_id":      "{cross} `{value}` no es un ID de usuario. Indica el ID numérico o una mención.",
        "no_user_found":    "{cross} No se encontró ningún usuario con ese ID.",
        "not_banned":       "{cross} **{user}** no está baneado en este servidor.",
        "cannot_kick":      "{cross} No tengo permiso para expulsar a ese miembro.",
        "cannot_ban":       "{cross} No tengo permiso para banear a ese usuario.",
        "cannot_unban":     "{cross} No tengo permiso para desbanear a ese usuario.",
        "cannot_slowmode":  "{cross} No puedo activar el modo lento aquí — revisa que tenga **Gestionar canales**.",
        "cannot_manage_channel": "{cross} No puedo cambiar los permisos de este canal — revisa que tenga **Gestionar canales**.",
        "slowmode_limit":   "{cross} El modo lento puede ser como máximo `{max}` segundos ({hours} horas).",
        "nick_failed":      "{cross} No puedo cambiar ese apodo — puede que ese miembro esté por encima de mí.",
        "warnings_perms":   "{cross} Necesitas **Moderar miembros** o **Gestionar mensajes** para leer advertencias.",
        "cannot_purge":     "{cross} No pude borrar mensajes aquí — revisa que tenga **Gestionar mensajes** y **Leer historial de mensajes**.",
        "action_failed":    "{cross} Eso falló: {error}",
    },
}

_flat_msg = make_flat_msg(MESSAGES)


def msg(ctx, key: str, **kwargs) -> str:
    """One localised reply with the bot's own emojis filled in."""
    return _flat_msg(ctx, key, **EMOJI, **kwargs)


def _cv2(text: str) -> discord.ui.LayoutView:
    """Wrap plain text in a cv2 Container."""
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return view


async def _delete_messages(channel, messages: list) -> list:
    """Delete a batch, falling back to one call each when bulk delete refuses.

    Discord only bulk-deletes messages younger than two weeks, so the batch
    call is tried first and anything it rejects is deleted individually.
    """
    if not messages:
        return []
    try:
        await channel.delete_messages(messages)
        return list(messages)
    except (discord.HTTPException, discord.Forbidden):
        pass
    deleted = []
    for message in messages:
        try:
            await message.delete()
            deleted.append(message)
        except (discord.HTTPException, discord.Forbidden):
            continue
    return deleted


async def _chunked_purge(channel, limit: int, check=None) -> list:
    """Delete messages in chunks of 100, up to ``limit`` messages scanned.

    Without a ``check`` this deletes ``limit`` messages. With one, ``limit``
    messages are *scanned* and every match among them is deleted — the meaning
    ``clear <amount> [member]`` has everywhere else. Stopping at the first page
    that happened to hold fewer matches, as this used to, left older messages
    from that member behind even though they were inside the requested range.
    """
    if check is None:
        deleted = []
        remaining = limit
        while remaining > 0:
            chunk = min(remaining, 100)
            await purge_limiter.acquire(channel.id)
            batch = await channel.purge(limit=chunk)
            deleted.extend(batch)
            remaining -= chunk
            if len(batch) < chunk:
                break
        return deleted

    deleted = []
    scanned = 0
    before = None
    while scanned < limit:
        chunk = min(limit - scanned, 100)
        await purge_limiter.acquire(channel.id)
        page = [message async for message in channel.history(limit=chunk, before=before)]
        if not page:
            break
        scanned += len(page)
        before = page[-1]  # newest-first: the last entry is the oldest scanned
        targets = [message for message in page if check(message)]
        deleted.extend(await _delete_messages(channel, targets))
    return deleted
