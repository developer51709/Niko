"""
Premium ticket system — single `ticket` group with admin + in-ticket sub-commands.

Admin sub-commands (manage_guild required):
    ticket setup              — open the configuration panel
    ticket panel              — post the public ticket panel here
    ticket category add/remove/list
    ticket support add/remove/list

In-ticket sub-commands (must be used inside a ticket channel,
support roles or manage_channels):
    ticket add <user>         — grant the user access
    ticket remove <user>      — revoke the user's access
    ticket rename <name>      — rename the channel
    ticket claim              — mark the ticket as claimed by you
    ticket transcript         — generate a text transcript
    ticket close              — soft-close (lock) the ticket
    ticket delete             — delete the ticket channel
"""

from __future__ import annotations

import asyncio
import io
import time
from datetime import datetime, timezone
from typing import Optional

import discord
from discord.ext import commands
from discord.ui import Modal, TextInput

from utils.tickets.utils import (
    get_ticket_config,
    update_ticket_config,
    async_update_ticket_config,
    get_all_ticket_configs,
    find_open_ticket,
)
from utils.tickets.config import TicketConfig
from utils.ai.config import get_personality
from config.emojis import get_emoji


# ───────────────────────────────────────────────────
#  TRILINGUAL MESSAGE TABLE
# ───────────────────────────────────────────────────

MESSAGES = {
    "normal": {
        "en": {
            "panel_default_title":  "Open a Ticket",
            "panel_default_desc":   "Select a category or press the button below to open a ticket.",
            "open_btn":             "Create Ticket",
            "select_category":      "### Select a Category",
            "select_placeholder":   "Select category...",
            "ticket_welcome":       "### {icon} {category} Ticket\nWelcome {mention}! A staff member will be with you shortly.",
            "ticket_created":       "✅ Your ticket has been created: {channel}",
            "panel_updated":        "✅ Ticket panel updated.",
            "panel_posted":         "✅ Ticket panel posted in {channel}.",
            "category_added":       "✅ Added category **{name}**.",
            "category_removed":     "✅ Removed category **{name}**.",
            "category_exists":      "⚠️ Category **{name}** already exists.",
            "category_missing":     "⚠️ Category **{name}** doesn't exist.",
            "categories_empty":     "No categories configured. Tickets will be opened with a single 'General' category.",
            "categories_list":      "### Ticket Categories\n{list}",
            "support_added":        "✅ Added {role} as a support role.",
            "support_removed":      "✅ Removed {role} from support roles.",
            "support_exists":       "⚠️ {role} is already a support role.",
            "support_missing":      "⚠️ {role} is not a support role.",
            "support_empty":        "No support roles configured.",
            "support_list":         "### Support Roles\n{list}",
            "not_in_ticket":        "❌ This command can only be used inside a ticket channel.",
            "no_perm_close":        "❌ You don't have permission to close tickets.",
            "no_perm_delete":       "❌ You don't have permission to delete tickets.",
            "no_perm_manage":       "❌ You don't have permission to manage this ticket.",
            "user_added":           "✅ {user} has been added to the ticket.",
            "user_removed":         "✅ {user} has been removed from the ticket.",
            "user_already_added":   "⚠️ {user} already has access to this ticket.",
            "user_not_in_ticket":   "⚠️ {user} doesn't have access to this ticket.",
            "renamed":              "✅ Ticket renamed to **{name}**.",
            "claimed":              "✅ Ticket claimed by {user}.",
            "already_claimed":      "⚠️ This ticket is already claimed by {user}.",
            "transcript_built":     "📝 Transcript generated.",
            "closing":              "{loading} Closing ticket…",
            "closed":               "🔒 This ticket has been closed by {user}.",
            "deleting":             "🗑️ Deleting this ticket in {seconds}s…",
            "setup_title":          "### {icon} Ticket System Setup",
            "setup_desc":           "Configure your ticket system below. Add categories, set up support roles, then post the panel.",
            "btn_add":              "Add User",
            "btn_cancel":           "Cancel",
            "btn_claim":            "Claim",
            "btn_close":            "Close",
            "btn_confirm_delete":   "Delete Ticket",
            "btn_delete":           "Delete",
            "btn_remove":           "Remove User",
            "btn_staff":            "Staff Panel",
            "btn_transfer":         "Transfer",
            "deleting_panel":       "🗑️ Deleting this ticket…",
            "header_details":       "### {icon} Ticket Details\n**Category:** {category}\n**Opener:** {opener}\n**Channel:** {channel}\n**Opened:** {opened}\n**Status:** {status}\n**Claimed by:** {claim}",
            "no_users_added":       "⚠️ Everyone you picked already had access to this ticket.",
            "no_users_removed":     "⚠️ Nobody you picked had access to this ticket.",
            "not_support_target":   "⚠️ {user} isn't a support member — transfer cancelled.",
            "panel_title":          "### {icon} Staff Panel — {channel}",
            "prompt_add":           "Who should be able to view **{channel}**? You can pick several users.",
            "prompt_delete":        "Are you sure you want to delete **{channel}**? This can't be undone.",
            "prompt_remove":        "Who should lose access to **{channel}**?",
            "prompt_transfer":      "Transfer the claim of **{channel}** to which support member?",
            "sel_staff":            "Choose a support member…",
            "sel_user":             "Choose user(s)…",
            "staff_panel_only":     "❌ Only support staff can use this panel.",
            "status_closed":        "Closed",
            "status_open":          "Open",
            "transferred":          "✅ Ticket transferred to {user}.",
            "unclaimed":            "Unclaimed",
            "users_added":          "✅ {users} can now view this ticket.",
            "users_removed":        "✅ {users} lost access to this ticket.",
        },
        "de": {
            "panel_default_title":  "Ticket öffnen",
            "panel_default_desc":   "Wähle eine Kategorie oder drücke den Button unten, um ein Ticket zu öffnen.",
            "open_btn":             "Ticket erstellen",
            "select_category":      "### Wähle eine Kategorie",
            "select_placeholder":   "Kategorie wählen...",
            "ticket_welcome":       "### {icon} {category} Ticket\nWillkommen {mention}! Ein Mitarbeiter ist gleich für dich da.",
            "ticket_created":       "✅ Dein Ticket wurde erstellt: {channel}",
            "panel_updated":        "✅ Ticket-Panel aktualisiert.",
            "panel_posted":         "✅ Ticket-Panel in {channel} gepostet.",
            "category_added":       "✅ Kategorie **{name}** hinzugefügt.",
            "category_removed":     "✅ Kategorie **{name}** entfernt.",
            "category_exists":      "⚠️ Kategorie **{name}** existiert bereits.",
            "category_missing":     "⚠️ Kategorie **{name}** existiert nicht.",
            "categories_empty":     "Keine Kategorien konfiguriert. Tickets werden mit einer einzigen Kategorie 'Allgemein' geöffnet.",
            "categories_list":      "### Ticket-Kategorien\n{list}",
            "support_added":        "✅ {role} als Support-Rolle hinzugefügt.",
            "support_removed":      "✅ {role} aus Support-Rollen entfernt.",
            "support_exists":       "⚠️ {role} ist bereits eine Support-Rolle.",
            "support_missing":      "⚠️ {role} ist keine Support-Rolle.",
            "support_empty":        "Keine Support-Rollen konfiguriert.",
            "support_list":         "### Support-Rollen\n{list}",
            "not_in_ticket":        "❌ Dieser Befehl kann nur in einem Ticket-Kanal verwendet werden.",
            "no_perm_close":        "❌ Du hast keine Berechtigung, Tickets zu schließen.",
            "no_perm_delete":       "❌ Du hast keine Berechtigung, Tickets zu löschen.",
            "no_perm_manage":       "❌ Du hast keine Berechtigung, dieses Ticket zu verwalten.",
            "user_added":           "✅ {user} wurde dem Ticket hinzugefügt.",
            "user_removed":         "✅ {user} wurde aus dem Ticket entfernt.",
            "user_already_added":   "⚠️ {user} hat bereits Zugriff auf dieses Ticket.",
            "user_not_in_ticket":   "⚠️ {user} hat keinen Zugriff auf dieses Ticket.",
            "renamed":              "✅ Ticket umbenannt zu **{name}**.",
            "claimed":              "✅ Ticket beansprucht von {user}.",
            "already_claimed":      "⚠️ Dieses Ticket ist bereits von {user} beansprucht.",
            "transcript_built":     "📝 Transkript erstellt.",
            "closing":              "{loading} Ticket wird geschlossen…",
            "closed":               "🔒 Dieses Ticket wurde von {user} geschlossen.",
            "deleting":             "🗑️ Ticket wird in {seconds}s gelöscht…",
            "setup_title":          "### {icon} Ticketsystem-Einrichtung",
            "setup_desc":           "Konfiguriere dein Ticketsystem unten. Füge Kategorien hinzu, richte Support-Rollen ein und poste dann das Panel.",
            "btn_add":              "Benutzer hinzufügen",
            "btn_cancel":           "Abbrechen",
            "btn_claim":            "Übernehmen",
            "btn_close":            "Schließen",
            "btn_confirm_delete":   "Ticket löschen",
            "btn_delete":           "Löschen",
            "btn_remove":           "Benutzer entfernen",
            "btn_staff":            "Staff-Panel",
            "btn_transfer":         "Übertragen",
            "deleting_panel":       "🗑️ Ticket wird gelöscht…",
            "header_details":       "### {icon} Ticket-Details\n**Kategorie:** {category}\n**Ersteller:** {opener}\n**Kanal:** {channel}\n**Geöffnet:** {opened}\n**Status:** {status}\n**Übernommen von:** {claim}",
            "no_users_added":       "⚠️ Alle ausgewählten Benutzer hatten bereits Zugriff auf dieses Ticket.",
            "no_users_removed":     "⚠️ Keiner der ausgewählten Benutzer hatte Zugriff auf dieses Ticket.",
            "not_support_target":   "⚠️ {user} ist kein Support-Mitglied – Übertragung abgebrochen.",
            "panel_title":          "### {icon} Staff-Panel – {channel}",
            "prompt_add":           "Wer soll **{channel}** sehen können? Du kannst mehrere Benutzer auswählen.",
            "prompt_delete":        "Möchtest du **{channel}** wirklich löschen? Das kann nicht rückgängig gemacht werden.",
            "prompt_remove":        "Wer soll den Zugriff auf **{channel}** verlieren?",
            "prompt_transfer":      "Auf welches Support-Mitglied soll die Übernahme von **{channel}** übertragen werden?",
            "sel_staff":            "Support-Mitglied wählen…",
            "sel_user":             "Benutzer wählen…",
            "staff_panel_only":     "❌ Nur Support-Mitarbeiter können dieses Panel nutzen.",
            "status_closed":        "Geschlossen",
            "status_open":          "Offen",
            "transferred":          "✅ Ticket an {user} übertragen.",
            "unclaimed":            "Nicht übernommen",
            "users_added":          "✅ {users} kann dieses Ticket nun sehen.",
            "users_removed":        "✅ {users} hat keinen Zugriff mehr auf dieses Ticket.",
        },
        "es": {
            "panel_default_title":  "Abrir un Ticket",
            "panel_default_desc":   "Selecciona una categoría o pulsa el botón a continuación para abrir un ticket.",
            "open_btn":             "Crear Ticket",
            "select_category":      "### Selecciona una categoría",
            "select_placeholder":   "Selecciona categoría...",
            "ticket_welcome":       "### {icon} Ticket de {category}\n¡Bienvenido {mention}! Un miembro del staff estará contigo en breve.",
            "ticket_created":       "✅ Tu ticket ha sido creado: {channel}",
            "panel_updated":        "✅ Panel de tickets actualizado.",
            "panel_posted":         "✅ Panel de tickets publicado en {channel}.",
            "category_added":       "✅ Se añadió la categoría **{name}**.",
            "category_removed":     "✅ Se eliminó la categoría **{name}**.",
            "category_exists":      "⚠️ La categoría **{name}** ya existe.",
            "category_missing":     "⚠️ La categoría **{name}** no existe.",
            "categories_empty":     "No hay categorías configuradas. Los tickets se abrirán con una única categoría 'General'.",
            "categories_list":      "### Categorías de Tickets\n{list}",
            "support_added":        "✅ Se añadió {role} como rol de soporte.",
            "support_removed":      "✅ Se eliminó {role} de los roles de soporte.",
            "support_exists":       "⚠️ {role} ya es un rol de soporte.",
            "support_missing":      "⚠️ {role} no es un rol de soporte.",
            "support_empty":        "No hay roles de soporte configurados.",
            "support_list":         "### Roles de Soporte\n{list}",
            "not_in_ticket":        "❌ Este comando solo se puede usar dentro de un canal de ticket.",
            "no_perm_close":        "❌ No tienes permiso para cerrar tickets.",
            "no_perm_delete":       "❌ No tienes permiso para eliminar tickets.",
            "no_perm_manage":       "❌ No tienes permiso para gestionar este ticket.",
            "user_added":           "✅ {user} ha sido añadido al ticket.",
            "user_removed":         "✅ {user} ha sido eliminado del ticket.",
            "user_already_added":   "⚠️ {user} ya tiene acceso a este ticket.",
            "user_not_in_ticket":   "⚠️ {user} no tiene acceso a este ticket.",
            "renamed":              "✅ Ticket renombrado a **{name}**.",
            "claimed":              "✅ Ticket reclamado por {user}.",
            "already_claimed":      "⚠️ Este ticket ya está reclamado por {user}.",
            "transcript_built":     "📝 Transcripción generada.",
            "closing":              "{loading} Cerrando ticket…",
            "closed":               "🔒 Este ticket ha sido cerrado por {user}.",
            "deleting":             "🗑️ Eliminando este ticket en {seconds}s…",
            "setup_title":          "### {icon} Configuración del Sistema de Tickets",
            "setup_desc":           "Configura tu sistema de tickets a continuación. Añade categorías, configura roles de soporte y luego publica el panel.",
            "btn_add":              "Añadir usuario",
            "btn_cancel":           "Cancelar",
            "btn_claim":            "Reclamar",
            "btn_close":            "Cerrar",
            "btn_confirm_delete":   "Eliminar ticket",
            "btn_delete":           "Eliminar",
            "btn_remove":           "Quitar usuario",
            "btn_staff":            "Panel del staff",
            "btn_transfer":         "Transferir",
            "deleting_panel":       "🗑️ Eliminando este ticket…",
            "header_details":       "### {icon} Detalles del ticket\n**Categoría:** {category}\n**Creador:** {opener}\n**Canal:** {channel}\n**Abierto:** {opened}\n**Estado:** {status}\n**Reclamado por:** {claim}",
            "no_users_added":       "⚠️ Todos los seleccionados ya tenían acceso a este ticket.",
            "no_users_removed":     "⚠️ Ninguno de los seleccionados tenía acceso a este ticket.",
            "not_support_target":   "⚠️ {user} no es miembro del soporte; transferencia cancelada.",
            "panel_title":          "### {icon} Panel del staff — {channel}",
            "prompt_add":           "¿Quién debería ver **{channel}**? Puedes elegir varios usuarios.",
            "prompt_delete":        "¿Seguro que quieres eliminar **{channel}**? Esto no se puede deshacer.",
            "prompt_remove":        "¿Quién debería perder el acceso a **{channel}**?",
            "prompt_transfer":      "¿A qué miembro del soporte quieres transferir el reclamo de **{channel}**?",
            "sel_staff":            "Elige un miembro del soporte…",
            "sel_user":             "Elige usuario(s)…",
            "staff_panel_only":     "❌ Solo el staff de soporte puede usar este panel.",
            "status_closed":        "Cerrado",
            "status_open":          "Abierto",
            "transferred":          "✅ Ticket transferido a {user}.",
            "unclaimed":            "Sin reclamar",
            "users_added":          "✅ {users} ya puede ver este ticket.",
            "users_removed":        "✅ {users} perdió el acceso a este ticket.",
        },
    },
    "cafe": {
        "en": {
            "panel_default_title":  "open a cozy ticket ☕",
            "panel_default_desc":   "pick a category or tap the button below — we'll grab a chair for you ✨",
            "open_btn":             "create ticket",
            "select_category":      "### pick a flavor ☕",
            "select_placeholder":   "choose category...",
            "ticket_welcome":       "### {icon} {category} ticket\nhey {mention} ☕ pull up a chair, the staff will be with you in a moment ✨",
            "ticket_created":       "✅ your cozy ticket is ready over at {channel} ☕",
            "panel_updated":        "✅ ticket panel polished and updated ✨",
            "panel_posted":         "✅ ticket panel served fresh in {channel} ☕",
            "category_added":       "✅ added **{name}** to the menu ☕",
            "category_removed":     "✅ took **{name}** off the menu",
            "category_exists":      "⚠️ **{name}** is already on the menu ☕",
            "category_missing":     "⚠️ no **{name}** on the menu hun~",
            "categories_empty":     "no categories yet — tickets will open under a default 'General' tag ☕",
            "categories_list":      "### ticket menu ☕\n{list}",
            "support_added":        "✅ welcome {role} to the staff lounge ☕",
            "support_removed":      "✅ removed {role} from the staff lounge",
            "support_exists":       "⚠️ {role} is already in the staff lounge ☕",
            "support_missing":      "⚠️ {role} isn't in the staff lounge",
            "support_empty":        "the staff lounge is empty for now ☕",
            "support_list":         "### staff lounge ☕\n{list}",
            "not_in_ticket":        "❌ this only works inside a ticket booth, sweet bean ☕",
            "no_perm_close":        "❌ you can't close tickets, sorry ☕",
            "no_perm_delete":       "❌ you can't delete tickets, sorry ☕",
            "no_perm_manage":       "❌ you can't manage this ticket, sorry ☕",
            "user_added":           "✅ pulled up a chair for {user} ☕",
            "user_removed":         "✅ {user} stepped out of the booth",
            "user_already_added":   "⚠️ {user} is already in the booth ☕",
            "user_not_in_ticket":   "⚠️ {user} isn't in this booth",
            "renamed":              "✅ ticket renamed to **{name}** ✨",
            "claimed":              "✅ {user} grabbed this ticket ☕",
            "already_claimed":      "⚠️ {user} already grabbed this one ☕",
            "transcript_built":     "📝 transcript brewed and ready ☕",
            "closing":              "{loading} closing the booth gently…",
            "closed":               "🔒 closed by {user} — see ya next time ☕",
            "deleting":             "🗑️ wiping the table in {seconds}s…",
            "setup_title":          "### {icon} ticket system setup ☕",
            "setup_desc":           "set up your ticket booth below — add menu items, invite staff, then post the cute panel ✨",
            "btn_add":              "invite more friends ☕",
            "btn_cancel":           "nevermind",
            "btn_claim":            "grab it ☕",
            "btn_close":            "close the booth",
            "btn_confirm_delete":   "yes, wipe the table",
            "btn_delete":           "delete",
            "btn_remove":           "ask someone to leave",
            "btn_staff":            "staff panel",
            "btn_transfer":         "pass it on",
            "deleting_panel":       "🗑️ wiping the table…",
            "header_details":       "### {icon} booth details ☕\n**menu pick:** {category}\n**guest:** {opener}\n**booth:** {channel}\n**opened:** {opened}\n**status:** {status}\n**grabbed by:** {claim}",
            "no_users_added":       "⚠️ everyone you picked already had a seat ☕",
            "no_users_removed":     "⚠️ none of those folks were in the booth ☕",
            "not_support_target":   "⚠️ {user} isn't on the team, sorry — transfer cancelled ☕",
            "panel_title":          "### {icon} staff panel — {channel} ☕",
            "prompt_add":           "who should get a seat in **{channel}**? you can pick a few ☕",
            "prompt_delete":        "sure you want to wipe **{channel}**? there's no coming back from this one ☕",
            "prompt_remove":        "who should step out of **{channel}**?",
            "prompt_transfer":      "who should take over the booth **{channel}**?",
            "sel_staff":            "pick a staffie…",
            "sel_user":             "pick your guests…",
            "staff_panel_only":     "❌ sorry, only the staff can peek at the panel ☕",
            "status_closed":        "closed",
            "status_open":          "open",
            "transferred":          "✅ booth passed to {user} ☕",
            "unclaimed":            "up for grabs",
            "users_added":          "✅ pulled up a seat for {users} ☕",
            "users_removed":        "✅ asked {users} to step out ☕",
        },
        "de": {
            "panel_default_title":  "ein gemütliches ticket öffnen ☕",
            "panel_default_desc":   "wähle eine kategorie oder tippe den button unten — wir holen dir nen stuhl ✨",
            "open_btn":             "ticket erstellen",
            "select_category":      "### wähl ne sorte ☕",
            "select_placeholder":   "kategorie wählen...",
            "ticket_welcome":       "### {icon} {category} ticket\nhey {mention} ☕ mach's dir gemütlich, jemand vom team kommt gleich ✨",
            "ticket_created":       "✅ dein gemütliches ticket wartet drüben in {channel} ☕",
            "panel_updated":        "✅ ticket-panel poliert und aktualisiert ✨",
            "panel_posted":         "✅ ticket-panel frisch serviert in {channel} ☕",
            "category_added":       "✅ **{name}** zur karte hinzugefügt ☕",
            "category_removed":     "✅ **{name}** von der karte genommen",
            "category_exists":      "⚠️ **{name}** steht schon auf der karte ☕",
            "category_missing":     "⚠️ kein **{name}** auf der karte~",
            "categories_empty":     "noch keine kategorien — tickets öffnen sich mit standard 'Allgemein' ☕",
            "categories_list":      "### ticket-karte ☕\n{list}",
            "support_added":        "✅ willkommen {role} im personal-lounge ☕",
            "support_removed":      "✅ {role} aus der personal-lounge entfernt",
            "support_exists":       "⚠️ {role} ist schon in der personal-lounge ☕",
            "support_missing":      "⚠️ {role} ist nicht in der personal-lounge",
            "support_empty":        "die personal-lounge ist noch leer ☕",
            "support_list":         "### personal-lounge ☕\n{list}",
            "not_in_ticket":        "❌ das geht nur in einer ticket-nische, süßer ☕",
            "no_perm_close":        "❌ du kannst keine tickets schließen, sorry ☕",
            "no_perm_delete":       "❌ du kannst keine tickets löschen, sorry ☕",
            "no_perm_manage":       "❌ du kannst dieses ticket nicht verwalten, sorry ☕",
            "user_added":           "✅ einen stuhl für {user} rangezogen ☕",
            "user_removed":         "✅ {user} ist aus der nische gegangen",
            "user_already_added":   "⚠️ {user} ist schon in der nische ☕",
            "user_not_in_ticket":   "⚠️ {user} ist nicht in dieser nische",
            "renamed":              "✅ ticket umbenannt zu **{name}** ✨",
            "claimed":              "✅ {user} hat dieses ticket übernommen ☕",
            "already_claimed":      "⚠️ {user} hat das schon übernommen ☕",
            "transcript_built":     "📝 transkript frisch aufgebrüht ☕",
            "closing":              "{loading} schließe die nische sanft…",
            "closed":               "🔒 geschlossen von {user} — bis bald ☕",
            "deleting":             "🗑️ tisch wird in {seconds}s abgewischt…",
            "setup_title":          "### {icon} ticketsystem-setup ☕",
            "setup_desc":           "richte deine ticket-nische ein — kategorien hinzufügen, personal einladen, dann das süße panel posten ✨",
            "btn_add":              "gäste reinholen ☕",
            "btn_cancel":           "doch nicht",
            "btn_claim":            "übernehmen ☕",
            "btn_close":            "nische schließen",
            "btn_confirm_delete":   "ja, tisch abwischen",
            "btn_delete":           "löschen",
            "btn_remove":           "gast rausbitten",
            "btn_staff":            "personal-panel",
            "btn_transfer":         "weiterreichen",
            "deleting_panel":       "🗑️ tisch wird abgewischt…",
            "header_details":       "### {icon} nischen-details ☕\n**auswahl:** {category}\n**gast:** {opener}\n**nische:** {channel}\n**geöffnet:** {opened}\n**status:** {status}\n**übernommen von:** {claim}",
            "no_users_added":       "⚠️ alle ausgewählten hatten schon einen platz ☕",
            "no_users_removed":     "⚠️ keiner davon war in der nische ☕",
            "not_support_target":   "⚠️ {user} gehört nicht zum team, sorry — übertragung abgebrochen ☕",
            "panel_title":          "### {icon} personal-panel — {channel} ☕",
            "prompt_add":           "wer soll in **{channel}** einen platz bekommen? du kannst ein paar wählen ☕",
            "prompt_delete":        "wirklich **{channel}** abwischen? das gibt's nicht zurück ☕",
            "prompt_remove":        "wer soll aus **{channel}** raus?",
            "prompt_transfer":      "wer soll die nische **{channel}** übernehmen?",
            "sel_staff":            "team-mitglied wählen…",
            "sel_user":             "gäste wählen…",
            "staff_panel_only":     "❌ sorry, nur das personal darf ins panel ☕",
            "status_closed":        "geschlossen",
            "status_open":          "offen",
            "transferred":          "✅ nische an {user} übergeben ☕",
            "unclaimed":            "zu haben",
            "users_added":          "✅ stuhl für {users} rangezogen ☕",
            "users_removed":        "✅ {users} rausgebeten ☕",
        },
        "es": {
            "panel_default_title":  "abre un ticket acogedor ☕",
            "panel_default_desc":   "elige una categoría o pulsa el botón — te traemos una silla ✨",
            "open_btn":             "crear ticket",
            "select_category":      "### elige un sabor ☕",
            "select_placeholder":   "elegir categoría...",
            "ticket_welcome":       "### {icon} ticket de {category}\nholi {mention} ☕ acomódate, el staff vendrá enseguida ✨",
            "ticket_created":       "✅ tu ticket acogedor te espera en {channel} ☕",
            "panel_updated":        "✅ panel de tickets pulido y actualizado ✨",
            "panel_posted":         "✅ panel de tickets servido fresquito en {channel} ☕",
            "category_added":       "✅ **{name}** añadida al menú ☕",
            "category_removed":     "✅ **{name}** quitada del menú",
            "category_exists":      "⚠️ **{name}** ya está en el menú ☕",
            "category_missing":     "⚠️ no hay **{name}** en el menú~",
            "categories_empty":     "aún no hay categorías — los tickets abren con la categoría 'General' por defecto ☕",
            "categories_list":      "### menú de tickets ☕\n{list}",
            "support_added":        "✅ bienvenida {role} a la sala del staff ☕",
            "support_removed":      "✅ {role} retirada de la sala del staff",
            "support_exists":       "⚠️ {role} ya está en la sala del staff ☕",
            "support_missing":      "⚠️ {role} no está en la sala del staff",
            "support_empty":        "la sala del staff está vacía por ahora ☕",
            "support_list":         "### sala del staff ☕\n{list}",
            "not_in_ticket":        "❌ esto solo funciona dentro de un cubículo de ticket, cariño ☕",
            "no_perm_close":        "❌ no puedes cerrar tickets, lo siento ☕",
            "no_perm_delete":       "❌ no puedes eliminar tickets, lo siento ☕",
            "no_perm_manage":       "❌ no puedes gestionar este ticket, lo siento ☕",
            "user_added":           "✅ acerqué una silla para {user} ☕",
            "user_removed":         "✅ {user} salió del cubículo",
            "user_already_added":   "⚠️ {user} ya está en el cubículo ☕",
            "user_not_in_ticket":   "⚠️ {user} no está en este cubículo",
            "renamed":              "✅ ticket renombrado a **{name}** ✨",
            "claimed":              "✅ {user} tomó este ticket ☕",
            "already_claimed":      "⚠️ {user} ya tomó este ☕",
            "transcript_built":     "📝 transcripción recién hecha ☕",
            "closing":              "{loading} cerrando el cubículo con cuidado…",
            "closed":               "🔒 cerrado por {user} — nos vemos pronto ☕",
            "deleting":             "🗑️ limpiando la mesa en {seconds}s…",
            "setup_title":          "### {icon} configuración del sistema de tickets ☕",
            "setup_desc":           "configura tu cubículo de tickets — añade categorías, invita staff y luego publica el panel adorable ✨",
            "btn_add":              "traer más amigos ☕",
            "btn_cancel":           "mejor no",
            "btn_claim":            "tomarlo ☕",
            "btn_close":            "cerrar el cubículo",
            "btn_confirm_delete":   "sí, limpiar la mesa",
            "btn_delete":           "eliminar",
            "btn_remove":           "pedir que salga",
            "btn_staff":            "panel del staff",
            "btn_transfer":         "pasarlo",
            "deleting_panel":       "🗑️ limpiando la mesa…",
            "header_details":       "### {icon} detalles del cubículo ☕\n**selección:** {category}\n**invitado:** {opener}\n**cubículo:** {channel}\n**abierto:** {opened}\n**estado:** {status}\n**tomado por:** {claim}",
            "no_users_added":       "⚠️ todos los elegidos ya tenían asiento ☕",
            "no_users_removed":     "⚠️ ninguno de esos estaba en el cubículo ☕",
            "not_support_target":   "⚠️ {user} no es del equipo, lo siento — transferencia cancelada ☕",
            "panel_title":          "### {icon} panel del staff — {channel} ☕",
            "prompt_add":           "¿quién merece un asiento en **{channel}**? puedes elegir a varios ☕",
            "prompt_delete":        "¿seguro que quieres limpiar **{channel}**? no hay vuelta atrás ☕",
            "prompt_remove":        "¿quién debería salir de **{channel}**?",
            "prompt_transfer":      "¿quién se hace cargo del cubículo **{channel}**?",
            "sel_staff":            "elige a alguien del equipo…",
            "sel_user":             "elige invitados…",
            "staff_panel_only":     "❌ lo siento, solo el staff puede ver el panel ☕",
            "status_closed":        "cerrado",
            "status_open":          "abierto",
            "transferred":          "✅ cubículo pasado a {user} ☕",
            "unclaimed":            "disponible",
            "users_added":          "✅ trajimos silla para {users} ☕",
            "users_removed":        "✅ {users} salió del cubículo ☕",
        },
    },
}


def _ctx_lang(ctx_or_int) -> str:
    guild = None
    if isinstance(ctx_or_int, commands.Context):
        guild = ctx_or_int.guild
    elif isinstance(ctx_or_int, discord.Interaction):
        guild = ctx_or_int.guild
    elif isinstance(ctx_or_int, discord.Guild):
        guild = ctx_or_int
    if guild and guild.preferred_locale:
        loc = str(guild.preferred_locale).lower()
        if loc.startswith("de"):
            return "de"
        if loc.startswith("es"):
            return "es"
    return "en"


def _ctx_personality(ctx_or_int) -> str:
    if isinstance(ctx_or_int, commands.Context):
        return get_personality(ctx_or_int)
    # interaction-like
    class _Shim:
        guild = ctx_or_int.guild if hasattr(ctx_or_int, "guild") else None
    return get_personality(_Shim())


def msg(ctx_or_int, key: str, **kwargs) -> str:
    p = _ctx_personality(ctx_or_int)
    lang = _ctx_lang(ctx_or_int)
    table = MESSAGES.get(p, MESSAGES["normal"])
    text = (
        table.get(lang, {}).get(key)
        or table.get("en", {}).get(key)
        or MESSAGES["normal"].get(lang, {}).get(key)
        or MESSAGES["normal"]["en"].get(key, key)
    )
    return text.format(**kwargs) if kwargs else text


def _cv2(text: str) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return view


# ───────────────────────────────────────────────────
#  HELPERS
# ───────────────────────────────────────────────────

def parse_hex_color(text: str) -> Optional[int]:
    text = text.strip().replace("#", "")
    try:
        return int(text, 16)
    except ValueError:
        return None


def color_to_markdown(color: Optional[int]) -> str:
    if color is None:
        return ""
    return f"`#{color:06X}`"


def is_ticket_channel(ctx: commands.Context) -> Optional[dict]:
    if not ctx.guild:
        return None
    return find_open_ticket(ctx.guild.id, ctx.channel.id)


def has_support_perms(member: discord.Member, cfg: TicketConfig) -> bool:
    if member.guild_permissions.manage_channels:
        return True
    role_ids = {r.id for r in member.roles}
    return any(rid in role_ids for rid in cfg.support_roles)


# ───────────────────────────────────────────────────
#  MODALS — admin setup
# ───────────────────────────────────────────────────

class TicketPanelModal(Modal, title="Configure Ticket Panel"):
    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id

        cfg = get_ticket_config(guild_id)
        self.title_input = TextInput(
            label="Panel Title", required=False, default=cfg.panel_title or ""
        )
        self.desc_input = TextInput(
            label="Panel Description", style=discord.TextStyle.long,
            required=False, default=cfg.panel_description or ""
        )
        self.color_input = TextInput(
            label="Color (hex)", required=False,
            default=f"#{cfg.panel_color:06X}" if cfg.panel_color else ""
        )
        self.image_input = TextInput(
            label="Image URL", required=False, default=cfg.panel_image or ""
        )

        self.add_item(self.title_input)
        self.add_item(self.desc_input)
        self.add_item(self.color_input)
        self.add_item(self.image_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = get_ticket_config(self.guild_id)
        if self.title_input.value:
            cfg.panel_title = self.title_input.value
        if self.desc_input.value:
            cfg.panel_description = self.desc_input.value
        if self.color_input.value:
            parsed = parse_hex_color(self.color_input.value)
            if parsed is not None:
                cfg.panel_color = parsed
        cfg.panel_image = self.image_input.value or None
        await async_update_ticket_config(self.guild_id, cfg)

        # update existing posted panel if present
        if cfg.panel_message_id and cfg.panel_channel_id:
            channel = interaction.guild.get_channel(cfg.panel_channel_id)
            if channel:
                try:
                    m = await channel.fetch_message(cfg.panel_message_id)
                    await m.edit(view=TicketPanelView(self.guild_id, cfg))
                except Exception:
                    pass

        await interaction.response.send_message(msg(interaction, "panel_updated"), ephemeral=True)


# ───────────────────────────────────────────────────
#  USER-FACING PANEL
# ───────────────────────────────────────────────────

class OpenTicketBtn(discord.ui.Button):
    def __init__(self, guild_id: int, label: str = "Create Ticket"):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.green,
            custom_id=f"open_ticket_{guild_id}",
        )
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        cfg = get_ticket_config(self.guild_id)
        categories = cfg.panel_categories
        if categories:
            view = discord.ui.LayoutView(timeout=None)
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=msg(interaction, "select_category")),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                CategorySelectRow(self.guild_id, categories, msg(interaction, "select_placeholder")),
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        await create_ticket(interaction, "General")


class CategorySelect(discord.ui.Select):
    def __init__(self, guild_id: int, categories: list[str], placeholder: str):
        self.guild_id = guild_id
        options = [
            discord.SelectOption(label=c, value=c) for c in categories
        ]
        super().__init__(placeholder=placeholder, options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await create_ticket(interaction, self.values[0])


class CategorySelectRow(discord.ui.ActionRow):
    def __init__(self, guild_id: int, categories: list[str], placeholder: str):
        super().__init__()
        self.add_item(CategorySelect(guild_id, categories, placeholder))


class TicketPanelView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, cfg: Optional[TicketConfig] = None):
        super().__init__(timeout=None)
        cfg = cfg or get_ticket_config(guild_id)
        guild = None  # we don't have a context here; localise with default fallback
        # Default fallback to english panel labels — admins can override via the modal
        title = cfg.panel_title or MESSAGES["cafe"]["en"]["panel_default_title"]
        desc = cfg.panel_description or MESSAGES["cafe"]["en"]["panel_default_desc"]
        color_md = color_to_markdown(cfg.panel_color)

        header = f"### {get_emoji('icon_ticket')} {title}"
        if color_md:
            header += f" {color_md}"

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=header),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=desc),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        if cfg.panel_image:
            container.add_item(
                discord.ui.MediaGallery(discord.MediaGalleryItem(media=cfg.panel_image))
            )
        container.add_item(
            discord.ui.ActionRow(
                OpenTicketBtn(guild_id, label=MESSAGES["cafe"]["en"]["open_btn"])
            )
        )
        self.add_item(container)


def _ticket_status_text(ctx_or_int, status: str) -> str:
    return msg(ctx_or_int, "status_closed" if status == "closed" else "status_open")


def build_ticket_header_view(
    ctx_or_int,
    *,
    category: str,
    opener_id: int,
    channel: discord.TextChannel,
    claimed_by: Optional[int] = None,
    status: str = "open",
) -> discord.ui.LayoutView:
    """The pinned card shown at the top of every ticket.

    Displays the ticket details and carries the persistent Staff Panel
    button that opens the ephemeral management panel.
    """
    icon = get_emoji("icon_ticket")
    guild = channel.guild
    opener = guild.get_member(opener_id)
    opener_ref = opener.mention if opener else f"<@{opener_id}>"

    if claimed_by:
        claimer = guild.get_member(claimed_by)
        claim_ref = claimer.mention if claimer else f"<@{claimed_by}>"
    else:
        claim_ref = msg(ctx_or_int, "unclaimed")

    opened_ts = int(channel.created_at.timestamp()) if channel.created_at else int(time.time())
    welcome = msg(
        ctx_or_int, "ticket_welcome",
        icon=icon, category=category, mention=opener_ref,
    )
    details = msg(
        ctx_or_int, "header_details",
        icon=icon,
        category=category,
        opener=opener_ref,
        channel=channel.mention,
        opened=f"<t:{opened_ts}:f>",
        status=_ticket_status_text(ctx_or_int, status),
        claim=claim_ref,
    )

    accent = discord.Color.red() if status == "closed" else discord.Color.green()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=welcome),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=details),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(StaffPanelButton(label=msg(ctx_or_int, "btn_staff"))),
        accent_colour=accent,
    )
    view = discord.ui.LayoutView(timeout=None)
    view.add_item(container)
    return view


async def refresh_ticket_header(
    ctx_or_int,
    guild: discord.Guild,
    channel: discord.TextChannel,
    ticket: dict,
    cfg: Optional[TicketConfig] = None,
) -> None:
    """Re-render the pinned header message of an existing ticket (best effort)."""
    cfg = cfg or get_ticket_config(guild.id)
    mid = ticket.get("message_id")
    if not mid:
        return
    try:
        header_msg = await channel.fetch_message(int(mid))
    except Exception:
        return
    try:
        await header_msg.edit(
            view=build_ticket_header_view(
                ctx_or_int,
                category=ticket.get("category", "General"),
                opener_id=ticket.get("opener_id", 0),
                channel=channel,
                claimed_by=ticket.get("claimed_by"),
                status=ticket.get("status", "open"),
            )
        )
    except Exception:
        pass


# ───────────────────────────────────────────────────
#  CREATE TICKET
# ───────────────────────────────────────────────────

async def create_ticket(interaction: discord.Interaction, category: str):
    guild = interaction.guild
    user = interaction.user

    cfg = get_ticket_config(guild.id)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, embed_links=True),
        guild.me: discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True,
            # needed so the bot can auto-pin the ticket header and quietly
            # delete the pin system-notice afterwards
            manage_messages=True,
        ),
    }
    for rid in cfg.support_roles:
        role = guild.get_role(rid)
        if role:
            overwrites[role] = discord.PermissionOverwrite(
                read_messages=True, send_messages=True, manage_messages=True
            )

    channel = await guild.create_text_channel(
        name=f"ticket-{user.name}",
        overwrites=overwrites,
        reason=f"Ticket opened by {user}",
    )

    entry = {
        "channel_id": channel.id,
        "message_id": None,
        "category": category,
        "opener_id": user.id,
        "claimed_by": None,
        "status": "open",
    }
    header_view = build_ticket_header_view(
        interaction,
        category=category,
        opener_id=user.id,
        channel=channel,
        claimed_by=None,
        status="open",
    )
    msg_obj = await channel.send(view=header_view)
    entry["message_id"] = msg_obj.id
    cfg.open_tickets.append(entry)
    await async_update_ticket_config(guild.id, cfg)

    # Pin the header so the ticket details + Staff Panel button stay on top,
    # then quietly remove the automated "pinned a message" system notice.
    try:
        await msg_obj.pin(reason=f"Ticket header for {user}")
        async for m in channel.history(limit=3):
            if m.id != msg_obj.id and m.type == discord.MessageType.pins_add:
                try:
                    await m.delete()
                except Exception:
                    pass
                break
    except Exception:
        pass

    text = msg(interaction, "ticket_created", channel=channel.mention)
    if interaction.response.is_done():
        await interaction.followup.send(text, ephemeral=True)
    else:
        await interaction.response.send_message(text, ephemeral=True)


# ───────────────────────────────────────────────────
#  TICKET STAFF PANEL (ephemeral per-ticket controls)
#  The pinned header card carries one persistent "Staff Panel" button.
#  Every custom id below is stable so views keep working across restarts
#  (see register_ticket_persistent_views, called from the cog setup).
# ───────────────────────────────────────────────────

_TICKET_HEADER_ID       = "ticket:header:staff"
_TICKET_CLAIM_ID        = "ticket:panel:claim"
_TICKET_TRANSFER_ID     = "ticket:panel:transfer"
_TICKET_CLOSE_ID        = "ticket:panel:close"
_TICKET_DELETE_ID       = "ticket:panel:delete"
_TICKET_DELETE_YES_ID   = "ticket:panel:delete_yes"
_TICKET_CANCEL_ID       = "ticket:panel:cancel"
_TICKET_ADD_ID          = "ticket:panel:add"
_TICKET_REMOVE_ID       = "ticket:panel:remove"
_TICKET_SEL_ADD_ID      = "ticket:panel:sel_add"
_TICKET_SEL_REMOVE_ID   = "ticket:panel:sel_remove"
_TICKET_SEL_TRANSFER_ID = "ticket:panel:sel_transfer"


def build_staff_panel_view(
    ctx_or_int,
    channel: discord.TextChannel,
    ticket: dict,
    cfg: TicketConfig,
    *,
    confirm: Optional[str] = None,
) -> discord.ui.LayoutView:
    """The ephemeral staff panel shown after pressing the header button."""
    view = discord.ui.LayoutView(timeout=None)
    icon = get_emoji("icon_ticket")
    title = msg(ctx_or_int, "panel_title", icon=icon, channel=channel.mention)

    if ticket.get("claimed_by"):
        claimer = channel.guild.get_member(ticket["claimed_by"])
        claim_ref = claimer.mention if claimer else f"<@{ticket['claimed_by']}>"
    else:
        claim_ref = msg(ctx_or_int, "unclaimed")
    status_line = f"**{_ticket_status_text(ctx_or_int, ticket.get('status', 'open'))}** — {claim_ref}"

    children: list = []
    if confirm:
        children.append(discord.ui.TextDisplay(content=confirm))
    children.extend([
        discord.ui.TextDisplay(content=title),
        discord.ui.TextDisplay(content=status_line),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
    ])

    claim_button = (
        _TicketTransferButton(label=msg(ctx_or_int, "btn_transfer"))
        if ticket.get("claimed_by")
        else _TicketClaimButton(label=msg(ctx_or_int, "btn_claim"))
    )
    children.append(discord.ui.ActionRow(
        claim_button,
        _TicketCloseButton(label=msg(ctx_or_int, "btn_close")),
        _TicketDeleteButton(label=msg(ctx_or_int, "btn_delete")),
    ))
    children.append(discord.ui.ActionRow(
        _TicketAddButton(label=msg(ctx_or_int, "btn_add")),
        _TicketRemoveButton(label=msg(ctx_or_int, "btn_remove")),
    ))
    view.add_item(discord.ui.Container(*children))
    return view


def _panel_text_view(content: str) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView(timeout=None)
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=content)))
    return view


async def _panel_context(interaction: discord.Interaction):
    """Resolve (ticket, cfg) for the interaction's channel.

    Replies with an ephemeral denial and returns (None, None) when the
    user isn't support staff or the channel isn't an open ticket.
    """
    if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel):
        return None, None
    cfg = get_ticket_config(interaction.guild.id)
    if not has_support_perms(interaction.user, cfg):
        await interaction.response.send_message(msg(interaction, "staff_panel_only"), ephemeral=True)
        return None, None
    ticket = find_open_ticket(interaction.guild.id, interaction.channel.id)
    if ticket is None:
        await interaction.response.send_message(msg(interaction, "not_in_ticket"), ephemeral=True)
        return None, None
    return ticket, cfg


async def _show_panel(
    interaction: discord.Interaction,
    ticket: dict,
    cfg: TicketConfig,
    *,
    confirm: Optional[str] = None,
) -> None:
    view = build_staff_panel_view(interaction, interaction.channel, ticket, cfg, confirm=confirm)
    await interaction.response.edit_message(view=view)


async def _persist_and_refresh(
    interaction: discord.Interaction,
    cfg: TicketConfig,
    ticket: dict,
) -> None:
    """Save config changes and re-render the pinned header card."""
    await async_update_ticket_config(interaction.guild.id, cfg)
    await refresh_ticket_header(
        interaction, interaction.guild, interaction.channel, ticket, cfg
    )


async def _member_has_access(channel: discord.TextChannel, member: discord.Member) -> bool:
    try:
        return bool(channel.overwrites_for(member).read_messages)
    except Exception:
        return False


def _ticket_member_options(channel: discord.TextChannel) -> list:
    """Member options (max 25) for the 'remove user' picker."""
    options: list = []
    for target, perms in list(channel.overwrites.items()):
        if isinstance(target, discord.Role) or target == channel.guild.me:
            continue
        if not (perms.read_messages or perms.view_channel):
            continue
        name = (getattr(target, "display_name", None) or str(target))[:90] or "Member"
        options.append(discord.SelectOption(
            label=name, value=str(target.id), description="Ticket member",
        ))
        if len(options) >= 25:
            break
    return options


# ── buttons ────────────────────────────────────────

class StaffPanelButton(discord.ui.Button):
    """Persistent 'Staff Panel' button pinned at the top of every ticket."""
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Staff Panel",
            style=discord.ButtonStyle.secondary,
            custom_id=_TICKET_HEADER_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel):
            return
        cfg = get_ticket_config(interaction.guild.id)
        if not has_support_perms(interaction.user, cfg):
            return await interaction.response.send_message(
                msg(interaction, "staff_panel_only"), ephemeral=True
            )
        ticket = find_open_ticket(interaction.guild.id, interaction.channel.id)
        if ticket is None:
            return await interaction.response.send_message(
                msg(interaction, "not_in_ticket"), ephemeral=True
            )
        view = build_staff_panel_view(interaction, interaction.channel, ticket, cfg)
        await interaction.response.send_message(view=view, ephemeral=True)


class _TicketClaimButton(discord.ui.Button):
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Claim",
            style=discord.ButtonStyle.success,
            custom_id=_TICKET_CLAIM_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        existing = ticket.get("claimed_by")
        if existing:
            other = interaction.guild.get_member(existing)
            who = other.mention if other else f"<@{existing}>"
            return await interaction.response.send_message(
                msg(interaction, "already_claimed", user=who), ephemeral=True
            )
        ticket["claimed_by"] = interaction.user.id
        await _persist_and_refresh(interaction, cfg, ticket)
        await _show_panel(
            interaction, ticket, cfg,
            confirm=msg(interaction, "claimed", user=interaction.user.mention),
        )


class _TicketTransferButton(discord.ui.Button):
    """Shown once the ticket has been claimed — hands the claim to another member."""
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Transfer",
            style=discord.ButtonStyle.primary,
            custom_id=_TICKET_TRANSFER_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        # No claim (anymore)? treat it like a claim instead.
        if not ticket.get("claimed_by"):
            ticket["claimed_by"] = interaction.user.id
            await _persist_and_refresh(interaction, cfg, ticket)
            return await _show_panel(
                interaction, ticket, cfg,
                confirm=msg(interaction, "claimed", user=interaction.user.mention),
            )
        prompt = msg(interaction, "prompt_transfer", channel=interaction.channel.mention)
        view = discord.ui.LayoutView(timeout=None)
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=prompt),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _TicketTransferUserSelect(placeholder=msg(interaction, "sel_staff")),
            ),
            discord.ui.ActionRow(
                _TicketCancelButton(label=msg(interaction, "btn_cancel")),
            ),
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)


class _TicketCloseButton(discord.ui.Button):
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Close",
            style=discord.ButtonStyle.secondary,
            custom_id=_TICKET_CLOSE_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return

        channel = interaction.channel
        ow = channel.overwrites
        for target, perms in list(ow.items()):
            if isinstance(target, (discord.Member, discord.User)) and target != channel.guild.me:
                perms.send_messages = False
                ow[target] = perms
        try:
            await channel.edit(
                overwrites=ow,
                name=f"closed-{channel.name}"[:95],
                reason=f"Closed by {interaction.user}",
            )
        except Exception:
            pass

        ticket["status"] = "closed"
        await _persist_and_refresh(interaction, cfg, ticket)
        await _show_panel(
            interaction, ticket, cfg,
            confirm=msg(interaction, "closed", user=interaction.user.mention),
        )


class _TicketDeleteButton(discord.ui.Button):
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Delete",
            style=discord.ButtonStyle.danger,
            custom_id=_TICKET_DELETE_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        prompt = msg(interaction, "prompt_delete", channel=interaction.channel.mention)
        view = discord.ui.LayoutView(timeout=None)
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=prompt),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _TicketDeleteYesButton(label=msg(interaction, "btn_confirm_delete")),
                _TicketCancelButton(label=msg(interaction, "btn_cancel")),
            ),
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)


class _TicketDeleteYesButton(discord.ui.Button):
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Delete Ticket",
            style=discord.ButtonStyle.danger,
            custom_id=_TICKET_DELETE_YES_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return

        cfg.open_tickets = [
            t for t in cfg.open_tickets
            if t.get("channel_id") != interaction.channel.id
        ]
        await async_update_ticket_config(interaction.guild.id, cfg)

        deleting = _panel_text_view(msg(interaction, "deleting_panel"))
        await interaction.response.edit_message(view=deleting)
        await asyncio.sleep(3)
        try:
            await interaction.channel.delete(reason=f"Ticket deleted by {interaction.user}")
        except Exception:
            pass


class _TicketAddButton(discord.ui.Button):
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Add User",
            style=discord.ButtonStyle.primary,
            custom_id=_TICKET_ADD_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        prompt = msg(interaction, "prompt_add", channel=interaction.channel.mention)
        view = discord.ui.LayoutView(timeout=None)
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=prompt),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _TicketAddUserSelect(placeholder=msg(interaction, "sel_user")),
            ),
            discord.ui.ActionRow(
                _TicketCancelButton(label=msg(interaction, "btn_cancel")),
            ),
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)


class _TicketRemoveButton(discord.ui.Button):
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Remove User",
            style=discord.ButtonStyle.secondary,
            custom_id=_TICKET_REMOVE_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        options = _ticket_member_options(interaction.channel)
        if not options:
            return await _show_panel(
                interaction, ticket, cfg,
                confirm=msg(interaction, "no_users_removed"),
            )
        prompt = msg(interaction, "prompt_remove", channel=interaction.channel.mention)
        view = discord.ui.LayoutView(timeout=None)
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=prompt),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _TicketRemoveUserSelect(options, placeholder=msg(interaction, "sel_user")),
            ),
            discord.ui.ActionRow(
                _TicketCancelButton(label=msg(interaction, "btn_cancel")),
            ),
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)


class _TicketCancelButton(discord.ui.Button):
    def __init__(self, label: Optional[str] = None):
        super().__init__(
            label=label or "Cancel",
            style=discord.ButtonStyle.secondary,
            custom_id=_TICKET_CANCEL_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        await _show_panel(interaction, ticket, cfg)


# ── pickers (ephemeral select menus) ──────────────

class _TicketAddUserSelect(discord.ui.UserSelect):
    def __init__(self, placeholder: Optional[str] = None):
        super().__init__(
            custom_id=_TICKET_SEL_ADD_ID,
            placeholder=placeholder or "Choose user(s)…",
            min_values=1, max_values=5,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        added: list = []
        for member in self.values:
            if await _member_has_access(interaction.channel, member):
                continue
            try:
                await interaction.channel.set_permissions(
                    member,
                    read_messages=True, send_messages=True,
                    attach_files=True, embed_links=True,
                    reason=f"Added by {interaction.user}",
                )
                added.append(member)
            except Exception:
                continue
        if not added:
            confirm = msg(interaction, "no_users_added")
        else:
            confirm = msg(
                interaction, "users_added",
                users=", ".join(m.mention for m in added),
            )
        await _show_panel(interaction, ticket, cfg, confirm=confirm)


class _TicketRemoveUserSelect(discord.ui.Select):
    def __init__(self, options: list, placeholder: Optional[str] = None):
        super().__init__(
            custom_id=_TICKET_SEL_REMOVE_ID,
            placeholder=placeholder or "Choose user(s)…",
            options=options,
            min_values=1, max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        removed: list = []
        for uid_str in self.values:
            target = interaction.guild.get_member(int(uid_str)) or discord.Object(id=int(uid_str))
            try:
                await interaction.channel.set_permissions(
                    target, overwrite=None,
                    reason=f"Removed by {interaction.user}",
                )
                removed.append(f"<@{uid_str}>")
            except Exception:
                continue
        if not removed:
            confirm = msg(interaction, "no_users_removed")
        else:
            confirm = msg(interaction, "users_removed", users=", ".join(removed))
        await _show_panel(interaction, ticket, cfg, confirm=confirm)


class _TicketTransferUserSelect(discord.ui.UserSelect):
    def __init__(self, placeholder: Optional[str] = None):
        super().__init__(
            custom_id=_TICKET_SEL_TRANSFER_ID,
            placeholder=placeholder or "Choose a support member…",
            min_values=1, max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket, cfg = await _panel_context(interaction)
        if ticket is None:
            return
        target = self.values[0]
        if not has_support_perms(target, cfg):
            return await _show_panel(
                interaction, ticket, cfg,
                confirm=msg(interaction, "not_support_target", user=target.mention),
            )
        ticket["claimed_by"] = target.id
        await _persist_and_refresh(interaction, cfg, ticket)
        await _show_panel(
            interaction, ticket, cfg,
            confirm=msg(interaction, "transferred", user=target.mention),
        )


# ── persistence helper (called from the cog setup) ─

def register_ticket_persistent_views(bot) -> None:
    """Register every persistent custom id used by ticket headers and staff
    panels so the buttons keep working after a bot restart."""
    registry = discord.ui.LayoutView(timeout=None)
    registry.add_item(discord.ui.Container(
        discord.ui.ActionRow(
            StaffPanelButton(),
            _TicketClaimButton(),
            _TicketTransferButton(),
            _TicketCloseButton(),
            _TicketDeleteButton(),
        ),
        discord.ui.ActionRow(
            _TicketAddButton(),
            _TicketRemoveButton(),
            _TicketDeleteYesButton(),
            _TicketCancelButton(),
        ),
        # one select per row — v2 action rows are weight-limited
        discord.ui.ActionRow(_TicketAddUserSelect()),
        discord.ui.ActionRow(
            _TicketRemoveUserSelect(options=[discord.SelectOption(label="\u200b", value="-")])
        ),
        discord.ui.ActionRow(_TicketTransferUserSelect()),
    ))
    bot.add_view(registry)


# ───────────────────────────────────────────────────
#  COG
# ───────────────────────────────────────────────────


__all__ = [k for k in list(globals()) if not k.startswith("__")]
