"""Translations for the VoiceMaster cog.

Every user-facing string — the control panel, the setup prompts, the channel
info card and every command reply — resolves through this table. ``msg`` takes
a command context *or* an interaction, because both expose
``guild.preferred_locale`` (that is what :func:`utils.i18n.get_lang` reads);
the panel's button callbacks therefore localize without a context object.
Views that are built from an already-resolved language use ``text``.

English is the fallback for a missing key or a language without a translation,
and the command names themselves (``lock``, ``claim``, …) stay English because
they are literal commands, not prose.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

from utils.i18n import get_lang, make_flat_msg

MESSAGES = {
    "en": {
        # ── Control panel ─────────────────────────────────────────────
        "interface_title": "VoiceMaster | Interface",
        "interface_lock": "the voice channel",
        "interface_unlock": "the voice channel",
        "interface_hide": "the voice channel",
        "interface_reveal": "the voice channel",
        "interface_claim": "the voice channel",
        "interface_disconnect": "a member",
        "interface_view": "channel information",
        "interface_increase": "the user limit",
        "interface_decrease": "the user limit",
        "interface_not_in_voice": "You must be in a voice channel.",
        "interface_unavailable": "VoiceMaster is not available.",
        "interface_not_owner": "You don't own this voice channel.",
        "interface_no_members_to_disconnect": "No members to disconnect.",
        "action_locked": "Voice channel locked.",
        "action_unlocked": "Voice channel unlocked.",
        "action_hidden": "Voice channel hidden.",
        "action_revealed": "Voice channel revealed.",
        "action_claimed": "Voice channel claimed.",
        "action_claim_failed": "Cannot claim this channel.",
        "action_limit_increased": "User limit increased.",
        "action_limit_decreased": "User limit decreased.",
        "error_generic": "An error occurred.",
        "disconnect_placeholder": "Choose members to disconnect...",
        "disconnect_option": "Disconnect {user}",
        "disconnect_done": "Disconnected: {users}",
        "disconnect_failed": "Failed: {users}",
        "disconnect_none": "No members were disconnected.",
        # ── Help panel ────────────────────────────────────────────────
        "help_body": (
            "Create and manage temporary voice channels in your server.\n\n"
            "**Getting Started**\n"
            "-# Use `voicemaster setup` to configure VoiceMaster for your server\n\n"
            "**Popular Commands**\n"
            "-# `voicemaster lock` — Lock your channel\n"
            "-# `voicemaster claim` — Claim an inactive channel\n"
            "-# `voicemaster limit <number>` — Set user limit"
        ),
        "help_support_button": "Support",
        # ── Setup ─────────────────────────────────────────────────────
        "setup_title": "VoiceMaster Setup",
        "setup_body": (
            "VoiceMaster gives every member their own temporary voice channel. "
            "When someone joins your **hub** channel, Niko creates a channel for them "
            "and deletes it once it is empty.\n\n"
            "Would you like Niko to create a hub channel for you, or would you like to "
            "use a channel you already have?"
        ),
        "setup_current_hub": (
            "VoiceMaster is currently using {channel}. Running setup again replaces "
            "that choice."
        ),
        "setup_create_channel": "Create a new channel",
        "setup_use_existing": "Use an existing channel",
        "setup_only_author": "Only {user} can use this setup prompt.",
        "setup_needs_manage": (
            "You need the **Manage Server** permission to configure VoiceMaster."
        ),
        "setup_failed": "Failed to set up VoiceMaster. Please check my permissions.",
        "setup_no_voice_channels": (
            "This server has no voice channels yet. Choose **Create a new channel** "
            "instead."
        ),
        "setup_success_title": "VoiceMaster Setup Complete",
        "setup_success_body": (
            "**Join Channel:** {channel}\n"
            "**Category:** {category}\n\n"
            "-# Use `{prefix}voicemaster sendinterface` to send the control panel."
        ),
        "setup_no_category": "No category",
        "channel_select_title": "Choose a hub channel",
        "channel_select_body": (
            "Pick the voice channel members should join to get their own temporary "
            "channel. New channels are created in that channel's category.\n\n"
            "-# Run `{prefix}voicemaster setup` again to have Niko create a new one "
            "instead."
        ),
        "channel_select_placeholder": "Select the voice channel to use...",
        "channel_select_category": "Category: {category}",
        "channel_select_unavailable": "That voice channel is no longer available.",
        "channel_select_save_failed": (
            "Failed to save that channel. Please check my permissions."
        ),
        # ── Defaults ──────────────────────────────────────────────────
        "defaults_title": "Default Settings",
        "defaults_name": "Default Name",
        "defaults_limit": "Default Limit",
        "defaults_bitrate": "Default Bitrate",
        "no_limit": "No limit",
        "default_name_set": "Default channel name set to: **{name}**",
        "default_name_too_long": "Default name must be 100 characters or less.",
        "default_name_failed": "Failed to set default name.",
        "default_limit_set": "Default user limit set to: **{value}**",
        "default_limit_invalid": "Limit must be between 0 and 99.",
        "default_limit_failed": "Failed to set default limit.",
        "default_bitrate_set": "Default bitrate set to: **{value} kbps**",
        "default_bitrate_invalid": "Bitrate must be between 8 and 384 kbps.",
        "default_bitrate_failed": "Failed to set default bitrate.",
        "default_region_set": "Default region set to: **{value}**",
        "default_region_invalid": "Invalid region. Valid options: {regions}",
        "default_region_failed": "Failed to set default region.",
        "default_not_set_up": (
            "VoiceMaster is not set up. Use `voicemaster setup` first."
        ),
        # ── Category & reset ──────────────────────────────────────────
        "category_set": "Voice channels will be created in: **{category}**",
        "category_cleared": (
            "Voice channels will be created without a specific category."
        ),
        "category_failed": "Failed to set category.",
        "reset_success": "VoiceMaster has been reset.",
        "reset_failed": "Failed to reset VoiceMaster.",
        # ── Commands ──────────────────────────────────────────────────
        "not_in_voice": "You must be in a voice channel to use this command.",
        "not_owner": "You don't own this voice channel.",
        "locked": "Voice channel locked.",
        "lock_failed": "Failed to lock the voice channel.",
        "unlocked": "Voice channel unlocked.",
        "unlock_failed": "Failed to unlock the voice channel.",
        "hidden": "Voice channel hidden.",
        "ghost_failed": "Failed to hide the voice channel.",
        "revealed": "Voice channel revealed.",
        "unghost_failed": "Failed to reveal the voice channel.",
        "claimed": "Voice channel claimed.",
        "claim_failed": "Cannot claim this channel. The owner may still be present.",
        "limit_set": "User limit set to {limit}.",
        "limit_removed": "User limit removed.",
        "limit_invalid": "Limit must be between 0 and 99.",
        "limit_failed": "Failed to set user limit.",
        "renamed": "Channel renamed to **{name}**.",
        "name_too_long": "Channel name must be 100 characters or less.",
        "rename_failed": "Failed to rename the voice channel.",
        "bitrate_set": "Bitrate set to {value} kbps.",
        "bitrate_invalid": "Bitrate must be between 8 and 384 kbps.",
        "bitrate_failed": "Failed to set bitrate.",
        "transferred": "Ownership transferred to **{user}**.",
        "transfer_self": "You cannot transfer ownership to yourself.",
        "transfer_not_in_channel": "That member must be in your voice channel.",
        "transfer_failed": "Failed to transfer ownership.",
        "permitted": "**{target}** can now join your voice channel.",
        "permit_role": "Members with this role",
        "permit_failed": "Failed to permit access.",
        "rejected": "**{target}** can no longer join your voice channel.",
        "reject_failed": "Failed to reject access.",
        "status_set": "Channel status set to: **{status}**",
        "status_cleared": "Channel status cleared.",
        "status_failed": "Failed to set channel status.",
        "disconnected": "**{user}** has been disconnected.",
        "disconnect_not_in_channel": "That member is not in your voice channel.",
        "disconnect_member_failed": "Failed to disconnect the member.",
        "role_configured": "Role management for **{role}** configured.",
        # ── Channel info card ─────────────────────────────────────────
        "info_owner": "Owner",
        "info_members": "Members",
        "info_limit": "Limit",
        "info_bitrate": "Bitrate",
        "info_region": "Region",
        "info_status": "Status",
        "info_no_limit": "No limit",
        "info_automatic": "Automatic",
        "info_open": "Open",
        "info_locked": "Locked",
        "info_hidden": "Hidden",
    },
    "de": {
        "interface_title": "VoiceMaster | Interface",
        "interface_lock": "den Sprachkanal",
        "interface_unlock": "den Sprachkanal",
        "interface_hide": "den Sprachkanal",
        "interface_reveal": "den Sprachkanal",
        "interface_claim": "den Sprachkanal",
        "interface_disconnect": "ein Mitglied",
        "interface_view": "Kanalinformationen",
        "interface_increase": "das Nutzerlimit",
        "interface_decrease": "das Nutzerlimit",
        "interface_not_in_voice": "Du musst dich in einem Sprachkanal befinden.",
        "interface_unavailable": "VoiceMaster ist nicht verfügbar.",
        "interface_not_owner": "Du besitzt diesen Sprachkanal nicht.",
        "interface_no_members_to_disconnect": "Es sind keine Mitglieder zu trennen.",
        "action_locked": "Sprachkanal gesperrt.",
        "action_unlocked": "Sprachkanal entsperrt.",
        "action_hidden": "Sprachkanal verborgen.",
        "action_revealed": "Sprachkanal wieder sichtbar.",
        "action_claimed": "Sprachkanal übernommen.",
        "action_claim_failed": "Dieser Kanal kann nicht übernommen werden.",
        "action_limit_increased": "Nutzerlimit erhöht.",
        "action_limit_decreased": "Nutzerlimit verringert.",
        "error_generic": "Ein Fehler ist aufgetreten.",
        "disconnect_placeholder": "Mitglieder zum Trennen auswählen...",
        "disconnect_option": "{user} trennen",
        "disconnect_done": "Getrennt: {users}",
        "disconnect_failed": "Fehlgeschlagen: {users}",
        "disconnect_none": "Es wurden keine Mitglieder getrennt.",
        "help_body": (
            "Erstelle und verwalte temporäre Sprachkanäle auf deinem Server.\n\n"
            "**Erste Schritte**\n"
            "-# Verwende `voicemaster setup`, um VoiceMaster für deinen Server "
            "einzurichten\n\n"
            "**Beliebte Befehle**\n"
            "-# `voicemaster lock` — Sperre deinen Kanal\n"
            "-# `voicemaster claim` — Übernimm einen inaktiven Kanal\n"
            "-# `voicemaster limit <number>` — Lege das Nutzerlimit fest"
        ),
        "help_support_button": "Support",
        "setup_title": "VoiceMaster Einrichtung",
        "setup_body": (
            "VoiceMaster gibt jedem Mitglied einen eigenen temporären Sprachkanal. "
            "Wenn jemand deinen **Hub**-Kanal betritt, erstellt Niko einen Kanal für "
            "dieses Mitglied und löscht ihn, sobald er leer ist.\n\n"
            "Soll Niko einen Hub-Kanal für dich erstellen oder möchtest du einen "
            "vorhandenen Kanal verwenden?"
        ),
        "setup_current_hub": (
            "VoiceMaster verwendet derzeit {channel}. Eine erneute Einrichtung "
            "ersetzt diese Auswahl."
        ),
        "setup_create_channel": "Neuen Kanal erstellen",
        "setup_use_existing": "Vorhandenen Kanal verwenden",
        "setup_only_author": "Nur {user} kann diese Einrichtung verwenden.",
        "setup_needs_manage": (
            "Du benötigst die Berechtigung **Server verwalten**, um VoiceMaster "
            "einzurichten."
        ),
        "setup_failed": (
            "VoiceMaster konnte nicht eingerichtet werden. Bitte prüfe meine "
            "Berechtigungen."
        ),
        "setup_no_voice_channels": (
            "Dieser Server hat noch keine Sprachkanäle. Wähle stattdessen "
            "**Neuen Kanal erstellen**."
        ),
        "setup_success_title": "VoiceMaster Einrichtung abgeschlossen",
        "setup_success_body": (
            "**Beitrittskanal:** {channel}\n"
            "**Kategorie:** {category}\n\n"
            "-# Verwende `{prefix}voicemaster sendinterface`, um das Bedienfeld zu "
            "senden."
        ),
        "setup_no_category": "Keine Kategorie",
        "channel_select_title": "Hub-Kanal auswählen",
        "channel_select_body": (
            "Wähle den Sprachkanal, dem Mitglieder beitreten sollen, um einen eigenen "
            "temporären Kanal zu erhalten. Neue Kanäle werden in der Kategorie dieses "
            "Kanals erstellt.\n\n"
            "-# Führe `{prefix}voicemaster setup` erneut aus, damit Niko stattdessen "
            "einen neuen erstellt."
        ),
        "channel_select_placeholder": "Sprachkanal zum Verwenden auswählen...",
        "channel_select_category": "Kategorie: {category}",
        "channel_select_unavailable": (
            "Dieser Sprachkanal ist nicht mehr verfügbar."
        ),
        "channel_select_save_failed": (
            "Der Kanal konnte nicht gespeichert werden. Bitte prüfe meine "
            "Berechtigungen."
        ),
        "defaults_title": "Standardeinstellungen",
        "defaults_name": "Standardname",
        "defaults_limit": "Standardlimit",
        "defaults_bitrate": "Standard-Bitrate",
        "no_limit": "Kein Limit",
        "default_name_set": "Standard-Kanalname festgelegt auf: **{name}**",
        "default_name_too_long": (
            "Der Standardname darf höchstens 100 Zeichen lang sein."
        ),
        "default_name_failed": "Der Standardname konnte nicht festgelegt werden.",
        "default_limit_set": "Standard-Nutzerlimit festgelegt auf: **{value}**",
        "default_limit_invalid": "Das Limit muss zwischen 0 und 99 liegen.",
        "default_limit_failed": "Das Standardlimit konnte nicht festgelegt werden.",
        "default_bitrate_set": "Standard-Bitrate festgelegt auf: **{value} kbps**",
        "default_bitrate_invalid": (
            "Die Bitrate muss zwischen 8 und 384 kbps liegen."
        ),
        "default_bitrate_failed": (
            "Die Standard-Bitrate konnte nicht festgelegt werden."
        ),
        "default_region_set": "Standardregion festgelegt auf: **{value}**",
        "default_region_invalid": "Ungültige Region. Gültige Optionen: {regions}",
        "default_region_failed": (
            "Die Standardregion konnte nicht festgelegt werden."
        ),
        "default_not_set_up": (
            "VoiceMaster ist nicht eingerichtet. Verwende zuerst "
            "`voicemaster setup`."
        ),
        "category_set": "Sprachkanäle werden erstellt in: **{category}**",
        "category_cleared": (
            "Sprachkanäle werden ohne bestimmte Kategorie erstellt."
        ),
        "category_failed": "Die Kategorie konnte nicht festgelegt werden.",
        "reset_success": "VoiceMaster wurde zurückgesetzt.",
        "reset_failed": "VoiceMaster konnte nicht zurückgesetzt werden.",
        "not_in_voice": (
            "Du musst dich in einem Sprachkanal befinden, um diesen Befehl zu "
            "verwenden."
        ),
        "not_owner": "Du besitzt diesen Sprachkanal nicht.",
        "locked": "Sprachkanal gesperrt.",
        "lock_failed": "Der Sprachkanal konnte nicht gesperrt werden.",
        "unlocked": "Sprachkanal entsperrt.",
        "unlock_failed": "Der Sprachkanal konnte nicht entsperrt werden.",
        "hidden": "Sprachkanal verborgen.",
        "ghost_failed": "Der Sprachkanal konnte nicht verborgen werden.",
        "revealed": "Sprachkanal wieder sichtbar.",
        "unghost_failed": (
            "Der Sprachkanal konnte nicht wieder sichtbar gemacht werden."
        ),
        "claimed": "Sprachkanal übernommen.",
        "claim_failed": (
            "Dieser Kanal kann nicht übernommen werden. Der Besitzer ist "
            "möglicherweise noch anwesend."
        ),
        "limit_set": "Nutzerlimit auf {limit} festgelegt.",
        "limit_removed": "Nutzerlimit entfernt.",
        "limit_invalid": "Das Limit muss zwischen 0 und 99 liegen.",
        "limit_failed": "Das Nutzerlimit konnte nicht festgelegt werden.",
        "renamed": "Kanal umbenannt in **{name}**.",
        "name_too_long": "Der Kanalname darf höchstens 100 Zeichen lang sein.",
        "rename_failed": "Der Sprachkanal konnte nicht umbenannt werden.",
        "bitrate_set": "Bitrate auf {value} kbps festgelegt.",
        "bitrate_invalid": "Die Bitrate muss zwischen 8 und 384 kbps liegen.",
        "bitrate_failed": "Die Bitrate konnte nicht festgelegt werden.",
        "transferred": "Besitz übertragen an **{user}**.",
        "transfer_self": (
            "Du kannst den Besitz nicht an dich selbst übertragen."
        ),
        "transfer_not_in_channel": (
            "Dieses Mitglied muss sich in deinem Sprachkanal befinden."
        ),
        "transfer_failed": "Der Besitz konnte nicht übertragen werden.",
        "permitted": "**{target}** kann jetzt deinem Sprachkanal beitreten.",
        "permit_role": "Mitglieder mit dieser Rolle",
        "permit_failed": "Der Zugriff konnte nicht erlaubt werden.",
        "rejected": (
            "**{target}** kann deinem Sprachkanal nicht mehr beitreten."
        ),
        "reject_failed": "Der Zugriff konnte nicht verweigert werden.",
        "status_set": "Kanalstatus festgelegt auf: **{status}**",
        "status_cleared": "Kanalstatus entfernt.",
        "status_failed": "Der Kanalstatus konnte nicht festgelegt werden.",
        "disconnected": "**{user}** wurde getrennt.",
        "disconnect_not_in_channel": (
            "Dieses Mitglied befindet sich nicht in deinem Sprachkanal."
        ),
        "disconnect_member_failed": "Das Mitglied konnte nicht getrennt werden.",
        "role_configured": "Rollenverwaltung für **{role}** eingerichtet.",
        "info_owner": "Besitzer",
        "info_members": "Mitglieder",
        "info_limit": "Limit",
        "info_bitrate": "Bitrate",
        "info_region": "Region",
        "info_status": "Status",
        "info_no_limit": "Kein Limit",
        "info_automatic": "Automatisch",
        "info_open": "Offen",
        "info_locked": "Gesperrt",
        "info_hidden": "Verborgen",
    },
    "es": {
        "interface_title": "VoiceMaster | Interfaz",
        "interface_lock": "el canal de voz",
        "interface_unlock": "el canal de voz",
        "interface_hide": "el canal de voz",
        "interface_reveal": "el canal de voz",
        "interface_claim": "el canal de voz",
        "interface_disconnect": "un miembro",
        "interface_view": "la información del canal",
        "interface_increase": "el límite de usuarios",
        "interface_decrease": "el límite de usuarios",
        "interface_not_in_voice": "Debes estar en un canal de voz.",
        "interface_unavailable": "VoiceMaster no está disponible.",
        "interface_not_owner": "No eres el propietario de este canal de voz.",
        "interface_no_members_to_disconnect": "No hay miembros para desconectar.",
        "action_locked": "Canal de voz bloqueado.",
        "action_unlocked": "Canal de voz desbloqueado.",
        "action_hidden": "Canal de voz oculto.",
        "action_revealed": "Canal de voz visible de nuevo.",
        "action_claimed": "Canal de voz reclamado.",
        "action_claim_failed": "No se puede reclamar este canal.",
        "action_limit_increased": "Límite de usuarios aumentado.",
        "action_limit_decreased": "Límite de usuarios reducido.",
        "error_generic": "Se produjo un error.",
        "disconnect_placeholder": "Elige los miembros a desconectar...",
        "disconnect_option": "Desconectar a {user}",
        "disconnect_done": "Desconectados: {users}",
        "disconnect_failed": "Fallidos: {users}",
        "disconnect_none": "No se desconectó a ningún miembro.",
        "help_body": (
            "Crea y gestiona canales de voz temporales en tu servidor.\n\n"
            "**Primeros pasos**\n"
            "-# Usa `voicemaster setup` para configurar VoiceMaster en tu servidor\n\n"
            "**Comandos populares**\n"
            "-# `voicemaster lock` — Bloquea tu canal\n"
            "-# `voicemaster claim` — Reclama un canal inactivo\n"
            "-# `voicemaster limit <number>` — Establece el límite de usuarios"
        ),
        "help_support_button": "Soporte",
        "setup_title": "Configuración de VoiceMaster",
        "setup_body": (
            "VoiceMaster da a cada miembro su propio canal de voz temporal. Cuando "
            "alguien entra en tu canal **hub**, Niko crea un canal para esa persona y "
            "lo elimina cuando queda vacío.\n\n"
            "¿Quieres que Niko cree un canal hub para ti o prefieres usar un canal "
            "que ya tengas?"
        ),
        "setup_current_hub": (
            "VoiceMaster está usando actualmente {channel}. Ejecutar la configuración "
            "de nuevo reemplaza esa elección."
        ),
        "setup_create_channel": "Crear un canal nuevo",
        "setup_use_existing": "Usar un canal existente",
        "setup_only_author": "Solo {user} puede usar este aviso de configuración.",
        "setup_needs_manage": (
            "Necesitas el permiso **Gestionar servidor** para configurar VoiceMaster."
        ),
        "setup_failed": (
            "No se pudo configurar VoiceMaster. Comprueba mis permisos."
        ),
        "setup_no_voice_channels": (
            "Este servidor aún no tiene canales de voz. Elige **Crear un canal "
            "nuevo**."
        ),
        "setup_success_title": "Configuración de VoiceMaster completada",
        "setup_success_body": (
            "**Canal de entrada:** {channel}\n"
            "**Categoría:** {category}\n\n"
            "-# Usa `{prefix}voicemaster sendinterface` para enviar el panel de "
            "control."
        ),
        "setup_no_category": "Sin categoría",
        "channel_select_title": "Elige un canal hub",
        "channel_select_body": (
            "Elige el canal de voz al que deben entrar los miembros para obtener su "
            "propio canal temporal. Los canales nuevos se crean en la categoría de "
            "ese canal.\n\n"
            "-# Ejecuta `{prefix}voicemaster setup` de nuevo para que Niko cree uno "
            "nuevo."
        ),
        "channel_select_placeholder": "Selecciona el canal de voz a usar...",
        "channel_select_category": "Categoría: {category}",
        "channel_select_unavailable": "Ese canal de voz ya no está disponible.",
        "channel_select_save_failed": (
            "No se pudo guardar ese canal. Comprueba mis permisos."
        ),
        "defaults_title": "Ajustes predeterminados",
        "defaults_name": "Nombre predeterminado",
        "defaults_limit": "Límite predeterminado",
        "defaults_bitrate": "Bitrate predeterminado",
        "no_limit": "Sin límite",
        "default_name_set": (
            "Nombre de canal predeterminado establecido en: **{name}**"
        ),
        "default_name_too_long": (
            "El nombre predeterminado debe tener 100 caracteres o menos."
        ),
        "default_name_failed": (
            "No se pudo establecer el nombre predeterminado."
        ),
        "default_limit_set": (
            "Límite de usuarios predeterminado establecido en: **{value}**"
        ),
        "default_limit_invalid": "El límite debe estar entre 0 y 99.",
        "default_limit_failed": (
            "No se pudo establecer el límite predeterminado."
        ),
        "default_bitrate_set": (
            "Bitrate predeterminado establecido en: **{value} kbps**"
        ),
        "default_bitrate_invalid": "El bitrate debe estar entre 8 y 384 kbps.",
        "default_bitrate_failed": (
            "No se pudo establecer el bitrate predeterminado."
        ),
        "default_region_set": (
            "Región predeterminada establecida en: **{value}**"
        ),
        "default_region_invalid": "Región no válida. Opciones válidas: {regions}",
        "default_region_failed": (
            "No se pudo establecer la región predeterminada."
        ),
        "default_not_set_up": (
            "VoiceMaster no está configurado. Usa primero `voicemaster setup`."
        ),
        "category_set": "Los canales de voz se crearán en: **{category}**",
        "category_cleared": (
            "Los canales de voz se crearán sin una categoría específica."
        ),
        "category_failed": "No se pudo establecer la categoría.",
        "reset_success": "VoiceMaster se ha restablecido.",
        "reset_failed": "No se pudo restablecer VoiceMaster.",
        "not_in_voice": "Debes estar en un canal de voz para usar este comando.",
        "not_owner": "No eres el propietario de este canal de voz.",
        "locked": "Canal de voz bloqueado.",
        "lock_failed": "No se pudo bloquear el canal de voz.",
        "unlocked": "Canal de voz desbloqueado.",
        "unlock_failed": "No se pudo desbloquear el canal de voz.",
        "hidden": "Canal de voz oculto.",
        "ghost_failed": "No se pudo ocultar el canal de voz.",
        "revealed": "Canal de voz visible de nuevo.",
        "unghost_failed": "No se pudo volver a mostrar el canal de voz.",
        "claimed": "Canal de voz reclamado.",
        "claim_failed": (
            "No se puede reclamar este canal. El propietario aún puede estar "
            "presente."
        ),
        "limit_set": "Límite de usuarios establecido en {limit}.",
        "limit_removed": "Límite de usuarios eliminado.",
        "limit_invalid": "El límite debe estar entre 0 y 99.",
        "limit_failed": "No se pudo establecer el límite de usuarios.",
        "renamed": "Canal renombrado a **{name}**.",
        "name_too_long": "El nombre del canal debe tener 100 caracteres o menos.",
        "rename_failed": "No se pudo renombrar el canal de voz.",
        "bitrate_set": "Bitrate establecido en {value} kbps.",
        "bitrate_invalid": "El bitrate debe estar entre 8 y 384 kbps.",
        "bitrate_failed": "No se pudo establecer el bitrate.",
        "transferred": "Propiedad transferida a **{user}**.",
        "transfer_self": "No puedes transferir la propiedad a ti mismo.",
        "transfer_not_in_channel": "Ese miembro debe estar en tu canal de voz.",
        "transfer_failed": "No se pudo transferir la propiedad.",
        "permitted": "**{target}** ahora puede unirse a tu canal de voz.",
        "permit_role": "Miembros con este rol",
        "permit_failed": "No se pudo permitir el acceso.",
        "rejected": "**{target}** ya no puede unirse a tu canal de voz.",
        "reject_failed": "No se pudo denegar el acceso.",
        "status_set": "Estado del canal establecido en: **{status}**",
        "status_cleared": "Estado del canal borrado.",
        "status_failed": "No se pudo establecer el estado del canal.",
        "disconnected": "**{user}** ha sido desconectado.",
        "disconnect_not_in_channel": "Ese miembro no está en tu canal de voz.",
        "disconnect_member_failed": "No se pudo desconectar al miembro.",
        "role_configured": "Gestión de roles para **{role}** configurada.",
        "info_owner": "Propietario",
        "info_members": "Miembros",
        "info_limit": "Límite",
        "info_bitrate": "Bitrate",
        "info_region": "Región",
        "info_status": "Estado",
        "info_no_limit": "Sin límite",
        "info_automatic": "Automática",
        "info_open": "Abierto",
        "info_locked": "Bloqueado",
        "info_hidden": "Oculto",
    },
}

# Command help strings shown by the help menu and on the dashboard commands page.
# They are stored per command name (the decorator key) and serialised by
# ``command_help`` into the ``{ 'en': …, 'de': …, 'es': … }`` format the help
# system and the website registry already parse. Keep apostrophes out of these
# lines: both readers normalise single quotes before parsing the JSON.
COMMAND_HELP = {
    "en": {
        "group": "Create and manage temporary voice channels in your server.",
        "setup": "Set up VoiceMaster and its hub channel",
        "sendinterface": "Send the VoiceMaster control panel",
        "reset": "Delete every temporary channel and clear the configuration",
        "category": "Choose the category new voice channels are created in",
        "default": "Configure defaults for new voice channels",
        "default_name": "Set the default name for new voice channels",
        "default_limit": "Set the default user limit for new voice channels",
        "default_bitrate": "Set the default bitrate for new voice channels",
        "default_region": "Set the default voice region for new voice channels",
        "configuration": "Show the settings of your voice channel",
        "lock": "Lock your voice channel so nobody else can join",
        "unlock": "Unlock your voice channel again",
        "ghost": "Hide your voice channel from the channel list",
        "unghost": "Make your hidden voice channel visible again",
        "claim": "Take ownership of an inactive voice channel",
        "limit": "Set the user limit of your voice channel",
        "name": "Rename your voice channel",
        "bitrate": "Set the bitrate of your voice channel",
        "transfer": "Give ownership of your voice channel to another member",
        "permit": "Allow a member or role to join your voice channel",
        "reject": "Block a member or role from joining your voice channel",
        "status": "Set or clear the status text of your voice channel",
        "disconnect": "Disconnect a member from your voice channel",
        "role": "Configure a role for the members of your voice channel",
    },
    "de": {
        "group": "Erstellt und verwaltet temporäre Sprachkanäle auf deinem Server.",
        "setup": "Richtet VoiceMaster und den Hub-Kanal ein",
        "sendinterface": "Sendet das VoiceMaster-Bedienfeld",
        "reset": "Löscht alle temporären Kanäle und die Konfiguration",
        "category": "Wählt die Kategorie für neue Sprachkanäle",
        "default": "Legt Standardwerte für neue Sprachkanäle fest",
        "default_name": "Legt den Standardnamen für neue Sprachkanäle fest",
        "default_limit": "Legt das Standard-Limit für neue Sprachkanäle fest",
        "default_bitrate": "Legt die Standard-Bitrate für neue Sprachkanäle fest",
        "default_region": "Legt die Standard-Region für neue Sprachkanäle fest",
        "configuration": "Zeigt die Einstellungen deines Sprachkanals",
        "lock": "Sperrt deinen Sprachkanal für andere",
        "unlock": "Entsperrt deinen Sprachkanal wieder",
        "ghost": "Verbirgt deinen Sprachkanal in der Kanalliste",
        "unghost": "Macht deinen verborgenen Sprachkanal wieder sichtbar",
        "claim": "Übernimmt einen inaktiven Sprachkanal",
        "limit": "Setzt das Nutzerlimit deines Sprachkanals",
        "name": "Benennt deinen Sprachkanal um",
        "bitrate": "Setzt die Bitrate deines Sprachkanals",
        "transfer": "Übergibt deinen Sprachkanal an ein anderes Mitglied",
        "permit": "Erlaubt einem Mitglied oder einer Rolle den Beitritt",
        "reject": "Blockiert ein Mitglied oder eine Rolle für den Beitritt",
        "status": "Setzt oder löscht den Statustext deines Sprachkanals",
        "disconnect": "Trennt ein Mitglied von deinem Sprachkanal",
        "role": "Konfiguriert eine Rolle für die Mitglieder deines Kanals",
    },
    "es": {
        "group": "Crea y gestiona canales de voz temporales en tu servidor.",
        "setup": "Configura VoiceMaster y su canal central",
        "sendinterface": "Envía el panel de control de VoiceMaster",
        "reset": "Elimina todos los canales temporales y la configuración",
        "category": "Elige la categoría donde se crean los canales de voz nuevos",
        "default": "Configura los valores por defecto de los canales nuevos",
        "default_name": "Establece el nombre por defecto de los canales nuevos",
        "default_limit": "Establece el límite de usuarios por defecto",
        "default_bitrate": "Establece el bitrate por defecto de los canales nuevos",
        "default_region": "Establece la región de voz por defecto",
        "configuration": "Muestra la configuración de tu canal de voz",
        "lock": "Bloquea tu canal de voz para que nadie pueda entrar",
        "unlock": "Desbloquea tu canal de voz de nuevo",
        "ghost": "Oculta tu canal de voz de la lista de canales",
        "unghost": "Vuelve a mostrar tu canal de voz oculto",
        "claim": "Reclama un canal de voz inactivo",
        "limit": "Establece el límite de usuarios de tu canal",
        "name": "Cambia el nombre de tu canal de voz",
        "bitrate": "Establece el bitrate de tu canal de voz",
        "transfer": "Transfiere tu canal de voz a otro miembro",
        "permit": "Permite que un miembro o rol entre en tu canal",
        "reject": "Bloquea a un miembro o rol para que no entre",
        "status": "Establece o borra el estado de tu canal de voz",
        "disconnect": "Desconecta a un miembro de tu canal de voz",
        "role": "Configura un rol para los miembros de tu canal",
    },
}


# ``msg(ctx_or_interaction, key, **values)`` resolves through the guild's locale.
msg = make_flat_msg(MESSAGES)


def text(lang: str, key: str, **values) -> str:
    """Resolve ``key`` for an already-known language code.

    Views that are constructed once per language (the control panel) cannot use
    ``msg`` because they have no context to read a locale from, so they pass the
    language they were built for.
    """
    template = MESSAGES.get(lang, {}).get(key) or MESSAGES["en"].get(key, key)
    return template.format(**values) if values else template


def command_help(key: str) -> str:
    """The localised help for one VoiceMaster command, as the registry stores it.

    Command decorators take a plain string, so the three translations are
    serialised into the same ``{ 'en': …, 'de': …, 'es': … }`` literal the
    other cogs use. The help menu and the dashboard parse it back into a map,
    the bot falls back to English when the guild language is not covered.
    """
    entries = {
        lang: COMMAND_HELP.get(lang, {}).get(key) or COMMAND_HELP["en"][key]
        for lang in ("en", "de", "es")
    }
    return json.dumps(entries, ensure_ascii=False)


def language_of(context) -> str:
    """The language code for a context, an interaction, or a raw guild.

    Panels posted outside a command (the support server's seeded panels) only
    have the guild to read from, and a guild carries the locale directly while
    ``get_lang`` expects something that holds a ``guild``.
    """
    if context is not None and hasattr(context, "preferred_locale"):
        context = SimpleNamespace(guild=context)
    return get_lang(context)


__all__ = ["COMMAND_HELP", "MESSAGES", "command_help", "msg", "text", "language_of"]
