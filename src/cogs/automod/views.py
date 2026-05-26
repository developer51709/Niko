import discord
from discord.ext import commands
import time
import re
import asyncio
from utils import logging as log
from config.emojis import get_emoji

INVITE_REGEX = re.compile(r"(discord\.gg/|discord\.com/invite/)", re.IGNORECASE)

# this will be used to prevent the bot from pinging every whitelisted user on the server every single time the automod command is used 🫩
ALLOWED_MENTIONS = discord.AllowedMentions.none()

# AppInstallationType integer keys used in _integration_owners
_GUILD_INSTALL = 0
_USER_INSTALL  = 1


def _is_user_installed_app(meta) -> bool:
    """
    Return True when a MessageInteractionMetadata came from a user-installed
    application (not a guild-installed bot).

    Discord's `_integration_owners` dict uses integer keys:
      0 = guild install  →  normal server bot
      1 = user install   →  user-installed app (potential raid tool)

    A genuine user-installed-only command has key 1 present and key 0 absent.
    """
    try:
        owners = meta._integration_owners
    except AttributeError:
        return False
    return _USER_INSTALL in owners and _GUILD_INSTALL not in owners


# ──────────────────────────────────────────────────
#  BILINGUAL MESSAGE TABLE
# ──────────────────────────────────────────────────

MESSAGES = {
    "en": {
        # ── Overview panel ──
        "overview_title":    "### {emoji} AutoMod Dashboard",
        "overview_desc":     "Here's a full snapshot of your server's protection ☕",
        "section_msgfilter": "**Message Filter**",
        "section_antinuke":  "**💣 Anti-Nuke**",
        "section_antiraid":  "**🌊 Anti-Raid** *(join flood)*",
        "section_extraid":   "**Ext. App Raid**",
        "section_whitelist": "**Whitelist**",
        "wl_summary":        "`{wu}` whitelisted user(s)  •  `{wr}` whitelisted role(s)",
        "nav_hint":          "-# Use the dropdown below to navigate and configure each section.",
        # ── Filter panel ──
        "filter_title":      "Message Filter Settings",
        "filter_desc":       "Toggle each protection and adjust the thresholds below.",
        "antispam_desc":     "**Anti-Spam** — mutes members who send messages too fast",
        "antispam_thresh":   "  Threshold: `{msgs}` msgs / `{secs}s`",
        "antilink_desc":     "**Anti-Link** — deletes Discord invite links",
        "badwords_desc":     "**Bad Words** — deletes blocked words (manage with `!badwords`)",
        "massmention_desc":  "**Mass Mention** — mutes members who mass-mention",
        "massmention_max":   "  Max mentions: `{max}`",
        # ── Anti-Nuke panel ──
        "nuke_title":        "### 💣 Anti-Nuke Settings",
        "nuke_desc":         "Protects your server against rogue moderators performing mass destructive actions.",
        "nuke_status_on":    "active 🟢",
        "nuke_status_off":   "inactive 🔴",
        "nuke_thresholds":   "**Tracked Actions & Thresholds** *(within interval)*",
        "nuke_bans":         "Bans: ≥ `{t}`",
        "nuke_kicks":        "Kicks: ≥ `{t}`",
        "nuke_chandel":      "Channel Deletes: ≥ `{t}`",
        "nuke_roledel":      "Role Deletes: ≥ `{t}`",
        "nuke_chancreate":   "Channel Creates: ≥ `{t}`",
        "nuke_webhookdel":   "Webhook Deletes: ≥ `{t}`",
        "nuke_interval":     "**Interval:** `{t}s`",
        "nuke_action":       "**Action on trigger:** `{action}`",
        "nuke_actions_hint": "-# Actions: `strip` (remove dangerous roles), `kick`, `ban`",
        # ── Anti-Raid panel ──
        "raid_title":        "### 🌊 Anti-Raid Settings *(Join Flood)*",
        "raid_desc":         "Detects and responds to mass member join events.",
        "raid_status_on":    "active 🟢",
        "raid_status_off":   "inactive 🔴",
        "raid_threshold":    "**Join Threshold:** `{t}` members",
        "raid_window":       "**Time Window:** `{t}` seconds",
        "raid_action":       "**Action on trigger:** `{action}`",
        "raid_newacct":      "**New Account Filter:** accounts < `{days}` day(s) old get actioned first",
        "raid_newacct_off":  "**New Account Filter:** disabled (all recent joiners actioned)",
        "raid_actions_hint": "-# Actions: `kick`, `ban`, `softban` (ban+unban), `slowmode`, `lockdown`",
        # ── Ext. Raid panel ──
        "ext_title":         "External App Raid Protection",
        "ext_mode1":         "**Mode 1 — Interaction Flood Detection**",
        "ext_mode1_desc":    ("Detects raids driven by external tools by tracking how many recently-joined "
                              "members fire bot interactions in quick succession, then identifies the operator "
                              "via invite-use diff."),
        "ext_mode2":         "**Mode 2 — User-Installed App Detection**",
        "ext_mode2_desc":    ("Detects slash commands fired by apps installed on a **user's account** "
                              "rather than the server. Catches raid bots that never join the server and "
                              "that most anti-raid tools miss."),
        "ext_threshold":     "Threshold: `{t}` unique new members / `{w}s`",
        "ext_newmember":     "'New member' = joined within `{s}s`",
        "ext_raiderop":      "Raider action: `{ra}`  •  Operator action: `{oa}`",
        "ext_app_threshold": "Threshold: `{t}` commands / `{w}s`",
        "ext_app_action":    "Action: `{a}`",
        "ext_hint":          ("-# Raider/operator actions: `kick`, `ban`\n"
                              "-# Operator-only: `notify` (log + DM owner)\n"
                              "-# User-app action: `kick`, `ban`, `warn`, `log`"),
        # ── Whitelist panel ──
        "wl_title":          "AutoMod Whitelist",
        "wl_desc":           "Whitelisted users and roles bypass all automod checks.",
        "wl_users_hdr":      "**Whitelisted Users**",
        "wl_roles_hdr":      "**Whitelisted Roles**",
        "wl_hint":           "-# Use `.whitelist add user @user` or `.whitelist add role @role` to manage.",
        # ── Modal validation errors ──
        "invalid_nuke_action":     "Invalid action. Choose: `strip`, `kick`, or `ban`.",
        "invalid_raid_action":     "Invalid action. Choose: `kick`, `ban`, `softban`, `slowmode`, or `lockdown`.",
        "invalid_raider_action":   "Invalid raider action. Choose: `kick` or `ban`.",
        "invalid_operator_action": "Invalid operator action. Choose: `notify`, `kick`, or `ban`.",
        "invalid_ext_action":      "Invalid action. Choose: `kick`, `ban`, `warn`, or `log`.",
        "invalid_numbers":         "Please enter valid whole numbers.",
        # ── DM alerts to server owner ──
        "raid_dm":    ("🚨 **Anti-Raid** in **{guild}**!\n"
                       "`{count}` joins in `{interval}s`. Action: `{action}`."),
        "nuke_dm":    ("🚨 **Anti-Nuke** in **{guild}**!\n"
                       "`{offender}` performed `{threshold}` `{action_key}` within `{interval}s`.\n"
                       "Action: `{action}`."),
        "extraid_dm": ("🚨 **Interaction Flood Raid** detected in **{guild}**!\n"
                       "`{count}` newly-joined members fired bot interactions simultaneously.\n"
                       "Suspected operator: {operator}\n"
                       "Raider action: `{ra}`  •  Operator action: `{oa}`"),
        # ── WL ephemeral prompts ──
        "wl_add_user_prompt":    "Select the members you want to exempt from automod:",
        "wl_add_role_prompt":    "Select the roles you want to exempt from automod:",
        "wl_remove_user_prompt": "Select the members to remove from the whitelist:",
        "wl_remove_role_prompt": "Select the roles to remove from the whitelist:",
        "wl_added_users":        "{emoji} Added {names} to the automod whitelist.",
        "wl_added_roles":        "{emoji} Added {names} to the automod whitelist.",
        "wl_removed_users":      "{emoji} Removed `{count}` user(s) from the whitelist.",
        "wl_removed_roles":      "{emoji} Removed `{count}` role(s) from the whitelist.",
        "wl_no_users":           "No users are currently whitelisted.",
        "wl_no_roles":           "No roles are currently whitelisted.",
    },
    "de": {
        # ── Overview panel ──
        "overview_title":    "### {emoji} AutoMod-Dashboard",
        "overview_desc":     "Hier ist eine vollständige Übersicht des Serverschutzes ☕",
        "section_msgfilter": "**Nachrichtenfilter**",
        "section_antinuke":  "**💣 Anti-Nuke**",
        "section_antiraid":  "**🌊 Anti-Raid** *(Beitrittsflut)*",
        "section_extraid":   "**Ext. App-Raid**",
        "section_whitelist": "**Whitelist**",
        "wl_summary":        "`{wu}` befreite(r) Nutzer  •  `{wr}` befreite(r) Rolle(n)",
        "nav_hint":          "-# Nutze das Dropdown unten zur Navigation und Konfiguration.",
        # ── Filter panel ──
        "filter_title":      "Nachrichtenfilter-Einstellungen",
        "filter_desc":       "Aktiviere/deaktiviere jeden Schutz und passe die Schwellenwerte an.",
        "antispam_desc":     "**Anti-Spam** — stummt Mitglieder, die zu schnell Nachrichten senden",
        "antispam_thresh":   "  Schwellenwert: `{msgs}` Nachrichten / `{secs}s`",
        "antilink_desc":     "**Anti-Link** — löscht Discord-Einladungslinks",
        "badwords_desc":     "**Verbotene Wörter** — löscht gesperrte Wörter (verwalten mit `!badwords`)",
        "massmention_desc":  "**Massen-Erwähnung** — stummt Mitglieder bei Massen-Mentions",
        "massmention_max":   "  Max. Erwähnungen: `{max}`",
        # ── Anti-Nuke panel ──
        "nuke_title":        "### 💣 Anti-Nuke-Einstellungen",
        "nuke_desc":         "Schützt deinen Server vor böswilligen Moderatoren, die Massenaktionen durchführen.",
        "nuke_status_on":    "aktiv 🟢",
        "nuke_status_off":   "inaktiv 🔴",
        "nuke_thresholds":   "**Überwachte Aktionen & Schwellenwerte** *(innerhalb des Intervalls)*",
        "nuke_bans":         "Bans: ≥ `{t}`",
        "nuke_kicks":        "Kicks: ≥ `{t}`",
        "nuke_chandel":      "Kanal-Löschungen: ≥ `{t}`",
        "nuke_roledel":      "Rollen-Löschungen: ≥ `{t}`",
        "nuke_chancreate":   "Kanal-Erstellungen: ≥ `{t}`",
        "nuke_webhookdel":   "Webhook-Löschungen: ≥ `{t}`",
        "nuke_interval":     "**Intervall:** `{t}s`",
        "nuke_action":       "**Aktion bei Auslösung:** `{action}`",
        "nuke_actions_hint": "-# Aktionen: `strip` (gefährliche Rollen entfernen), `kick`, `ban`",
        # ── Anti-Raid panel ──
        "raid_title":        "### 🌊 Anti-Raid-Einstellungen *(Beitrittsflut)*",
        "raid_desc":         "Erkennt Massen-Beitritte und reagiert darauf.",
        "raid_status_on":    "aktiv 🟢",
        "raid_status_off":   "inaktiv 🔴",
        "raid_threshold":    "**Beitritts-Schwellenwert:** `{t}` Mitglieder",
        "raid_window":       "**Zeitfenster:** `{t}` Sekunden",
        "raid_action":       "**Aktion bei Auslösung:** `{action}`",
        "raid_newacct":      "**Neukonto-Filter:** Konten < `{days}` Tag(e) alt werden bevorzugt behandelt",
        "raid_newacct_off":  "**Neukonto-Filter:** deaktiviert (alle aktuellen Beitritte werden behandelt)",
        "raid_actions_hint": "-# Aktionen: `kick`, `ban`, `softban` (ban+unban), `slowmode`, `lockdown`",
        # ── Ext. Raid panel ──
        "ext_title":         "Schutz vor externen App-Raids",
        "ext_mode1":         "**Modus 1 — Interaktionsflut-Erkennung**",
        "ext_mode1_desc":    ("Erkennt Raids durch externe Tools, indem verfolgt wird, wie viele kürzlich "
                              "beigetretene Mitglieder gleichzeitig Bot-Interaktionen auslösen, und identifiziert "
                              "den Operator über Einladungs-Diffs."),
        "ext_mode2":         "**Modus 2 — Nutzer-installierte App-Erkennung**",
        "ext_mode2_desc":    ("Erkennt Slash-Commands, die von Apps auf dem **Nutzerkonto** (nicht dem Server) "
                              "ausgeführt werden. Erfasst Raid-Bots, die dem Server nie beitreten."),
        "ext_threshold":     "Schwellenwert: `{t}` neue Mitglieder / `{w}s`",
        "ext_newmember":     "'Neues Mitglied' = beigetreten innerhalb `{s}s`",
        "ext_raiderop":      "Raider-Aktion: `{ra}`  •  Operator-Aktion: `{oa}`",
        "ext_app_threshold": "Schwellenwert: `{t}` Befehle / `{w}s`",
        "ext_app_action":    "Aktion: `{a}`",
        "ext_hint":          ("-# Raider/Operator-Aktionen: `kick`, `ban`\n"
                              "-# Nur Operator: `notify` (Protokoll + DM an Eigentümer)\n"
                              "-# Nutzer-App-Aktion: `kick`, `ban`, `warn`, `log`"),
        # ── Whitelist panel ──
        "wl_title":          "AutoMod-Whitelist",
        "wl_desc":           "Befreite Nutzer und Rollen umgehen alle AutoMod-Prüfungen.",
        "wl_users_hdr":      "**Befreite Nutzer**",
        "wl_roles_hdr":      "**Befreite Rollen**",
        "wl_hint":           "-# Nutze `.whitelist add user @user` oder `.whitelist add role @role` zur Verwaltung.",
        # ── Modal validation errors ──
        "invalid_nuke_action":     "Ungültige Aktion. Wähle: `strip`, `kick` oder `ban`.",
        "invalid_raid_action":     "Ungültige Aktion. Wähle: `kick`, `ban`, `softban`, `slowmode` oder `lockdown`.",
        "invalid_raider_action":   "Ungültige Raider-Aktion. Wähle: `kick` oder `ban`.",
        "invalid_operator_action": "Ungültige Operator-Aktion. Wähle: `notify`, `kick` oder `ban`.",
        "invalid_ext_action":      "Ungültige Aktion. Wähle: `kick`, `ban`, `warn` oder `log`.",
        "invalid_numbers":         "Bitte gib gültige ganze Zahlen ein.",
        # ── DM alerts to server owner ──
        "raid_dm":    ("🚨 **Anti-Raid** in **{guild}**!\n"
                       "`{count}` Beitritte in `{interval}s`. Aktion: `{action}`."),
        "nuke_dm":    ("🚨 **Anti-Nuke** in **{guild}**!\n"
                       "`{offender}` hat `{threshold}` `{action_key}` in `{interval}s` ausgeführt.\n"
                       "Aktion: `{action}`."),
        "extraid_dm": ("🚨 **Interaktionsflut-Raid** in **{guild}**!\n"
                       "`{count}` kürzlich beigetretene Mitglieder lösten gleichzeitig Bot-Interaktionen aus.\n"
                       "Vermuteter Operator: {operator}\n"
                       "Raider-Aktion: `{ra}`  •  Operator-Aktion: `{oa}`"),
        # ── WL ephemeral prompts ──
        "wl_add_user_prompt":    "Wähle die Mitglieder aus, die von AutoMod ausgenommen werden sollen:",
        "wl_add_role_prompt":    "Wähle die Rollen aus, die von AutoMod ausgenommen werden sollen:",
        "wl_remove_user_prompt": "Wähle die Mitglieder aus, die von der Whitelist entfernt werden sollen:",
        "wl_remove_role_prompt": "Wähle die Rollen aus, die von der Whitelist entfernt werden sollen:",
        "wl_added_users":        "{emoji} {names} zur AutoMod-Whitelist hinzugefügt.",
        "wl_added_roles":        "{emoji} {names} zur AutoMod-Whitelist hinzugefügt.",
        "wl_removed_users":      "{emoji} `{count}` Nutzer von der Whitelist entfernt.",
        "wl_removed_roles":      "{emoji} `{count}` Rolle(n) von der Whitelist entfernt.",
        "wl_no_users":           "Aktuell sind keine Nutzer auf der Whitelist.",
        "wl_no_roles":           "Aktuell sind keine Rollen auf der Whitelist.",
    },
    "es": {
        # ── Overview panel ──
        "overview_title":    "### {emoji} Panel de AutoMod",
        "overview_desc":     "Aquí tienes una vista completa de la protección de tu servidor ☕",
        "section_msgfilter": "**Filtro de Mensajes**",
        "section_antinuke":  "**💣 Anti-Nuke**",
        "section_antiraid":  "**🌊 Anti-Raid** *(avalancha de ingresos)*",
        "section_extraid":   "**Raid de Apps Externas**",
        "section_whitelist": "**Lista Blanca**",
        "wl_summary":        "`{wu}` usuario(s) en lista blanca  •  `{wr}` rol(es) en lista blanca",
        "nav_hint":          "-# Usa el desplegable de abajo para navegar y configurar cada sección.",
        # ── Filter panel ──
        "filter_title":      "Configuración del Filtro de Mensajes",
        "filter_desc":       "Activa cada protección y ajusta los umbrales abajo.",
        "antispam_desc":     "**Anti-Spam** — silencia a miembros que envían mensajes muy rápido",
        "antispam_thresh":   "  Umbral: `{msgs}` msgs / `{secs}s`",
        "antilink_desc":     "**Anti-Link** — borra enlaces de invitación de Discord",
        "badwords_desc":     "**Palabras Prohibidas** — borra palabras bloqueadas (gestiona con `!badwords`)",
        "massmention_desc":  "**Menciones Masivas** — silencia a quien hace menciones masivas",
        "massmention_max":   "  Máx menciones: `{max}`",
        # ── Anti-Nuke panel ──
        "nuke_title":        "### 💣 Configuración Anti-Nuke",
        "nuke_desc":         "Protege tu servidor contra moderadores corruptos que realizan acciones destructivas masivas.",
        "nuke_status_on":    "activo 🟢",
        "nuke_status_off":   "inactivo 🔴",
        "nuke_thresholds":   "**Acciones Monitorizadas y Umbrales** *(dentro del intervalo)*",
        "nuke_bans":         "Baneos: ≥ `{t}`",
        "nuke_kicks":        "Expulsiones: ≥ `{t}`",
        "nuke_chandel":      "Canales Borrados: ≥ `{t}`",
        "nuke_roledel":      "Roles Borrados: ≥ `{t}`",
        "nuke_chancreate":   "Canales Creados: ≥ `{t}`",
        "nuke_webhookdel":   "Webhooks Borrados: ≥ `{t}`",
        "nuke_interval":     "**Intervalo:** `{t}s`",
        "nuke_action":       "**Acción al activarse:** `{action}`",
        "nuke_actions_hint": "-# Acciones: `strip` (quitar roles peligrosos), `kick`, `ban`",
        # ── Anti-Raid panel ──
        "raid_title":        "### 🌊 Configuración Anti-Raid *(Avalancha de Ingresos)*",
        "raid_desc":         "Detecta y responde ante ingresos masivos de miembros.",
        "raid_status_on":    "activo 🟢",
        "raid_status_off":   "inactivo 🔴",
        "raid_threshold":    "**Umbral de Ingresos:** `{t}` miembros",
        "raid_window":       "**Ventana de Tiempo:** `{t}` segundos",
        "raid_action":       "**Acción al activarse:** `{action}`",
        "raid_newacct":      "**Filtro de Cuentas Nuevas:** cuentas con menos de `{days}` día(s) reciben acción primero",
        "raid_newacct_off":  "**Filtro de Cuentas Nuevas:** desactivado (todos los recién llegados reciben acción)",
        "raid_actions_hint": "-# Acciones: `kick`, `ban`, `softban` (ban+unban), `slowmode`, `lockdown`",
        # ── Ext. Raid panel ──
        "ext_title":         "Protección contra Raid de Apps Externas",
        "ext_mode1":         "**Modo 1 — Detección de Avalancha de Interacciones**",
        "ext_mode1_desc":    ("Detecta raids impulsados por herramientas externas rastreando cuántos miembros recién "
                              "ingresados disparan interacciones del bot en sucesión rápida, e identifica al operador "
                              "mediante el diff de invitaciones usadas."),
        "ext_mode2":         "**Modo 2 — Detección de Apps Instaladas por el Usuario**",
        "ext_mode2_desc":    ("Detecta comandos slash disparados por apps instaladas en la **cuenta de un usuario** "
                              "en vez del servidor. Atrapa bots de raid que nunca se unen al servidor y que la "
                              "mayoría de herramientas anti-raid no detectan."),
        "ext_threshold":     "Umbral: `{t}` miembros nuevos únicos / `{w}s`",
        "ext_newmember":     "'Miembro nuevo' = se unió en los últimos `{s}s`",
        "ext_raiderop":      "Acción raider: `{ra}`  •  Acción operador: `{oa}`",
        "ext_app_threshold": "Umbral: `{t}` comandos / `{w}s`",
        "ext_app_action":    "Acción: `{a}`",
        "ext_hint":          ("-# Acciones raider/operador: `kick`, `ban`\n"
                              "-# Solo operador: `notify` (log + DM al dueño)\n"
                              "-# Acción para apps de usuario: `kick`, `ban`, `warn`, `log`"),
        # ── Whitelist panel ──
        "wl_title":          "Lista Blanca de AutoMod",
        "wl_desc":           "Los usuarios y roles en lista blanca se saltan todas las verificaciones de automod.",
        "wl_users_hdr":      "**Usuarios en Lista Blanca**",
        "wl_roles_hdr":      "**Roles en Lista Blanca**",
        "wl_hint":           "-# Usa `.whitelist add user @user` o `.whitelist add role @role` para gestionar.",
        # ── Modal validation errors ──
        "invalid_nuke_action":     "Acción inválida. Elige: `strip`, `kick` o `ban`.",
        "invalid_raid_action":     "Acción inválida. Elige: `kick`, `ban`, `softban`, `slowmode` o `lockdown`.",
        "invalid_raider_action":   "Acción raider inválida. Elige: `kick` o `ban`.",
        "invalid_operator_action": "Acción operador inválida. Elige: `notify`, `kick` o `ban`.",
        "invalid_ext_action":      "Acción inválida. Elige: `kick`, `ban`, `warn` o `log`.",
        "invalid_numbers":         "Por favor introduce números enteros válidos.",
        # ── DM alerts to server owner ──
        "raid_dm":    ("🚨 ¡**Anti-Raid** en **{guild}**!\n"
                       "`{count}` ingresos en `{interval}s`. Acción: `{action}`."),
        "nuke_dm":    ("🚨 ¡**Anti-Nuke** en **{guild}**!\n"
                       "`{offender}` realizó `{threshold}` `{action_key}` en `{interval}s`.\n"
                       "Acción: `{action}`."),
        "extraid_dm": ("🚨 ¡**Raid de Avalancha de Interacciones** detectado en **{guild}**!\n"
                       "`{count}` miembros recién ingresados dispararon interacciones del bot simultáneamente.\n"
                       "Operador sospechoso: {operator}\n"
                       "Acción raider: `{ra}`  •  Acción operador: `{oa}`"),
        # ── WL ephemeral prompts ──
        "wl_add_user_prompt":    "Selecciona los miembros que quieres eximir del automod:",
        "wl_add_role_prompt":    "Selecciona los roles que quieres eximir del automod:",
        "wl_remove_user_prompt": "Selecciona los miembros a quitar de la lista blanca:",
        "wl_remove_role_prompt": "Selecciona los roles a quitar de la lista blanca:",
        "wl_added_users":        "{emoji} Añadidos {names} a la lista blanca de automod.",
        "wl_added_roles":        "{emoji} Añadidos {names} a la lista blanca de automod.",
        "wl_removed_users":      "{emoji} Eliminados `{count}` usuario(s) de la lista blanca.",
        "wl_removed_roles":      "{emoji} Eliminados `{count}` rol(es) de la lista blanca.",
        "wl_no_users":           "Actualmente no hay usuarios en la lista blanca.",
        "wl_no_roles":           "Actualmente no hay roles en la lista blanca.",
    },
}


def get_lang(ctx_or_guild=None) -> str:
    """Return 'de' when the guild's preferred locale is German, else 'en'."""
    guild = None
    if isinstance(ctx_or_guild, commands.Context):
        guild = ctx_or_guild.guild
    elif isinstance(ctx_or_guild, discord.Guild):
        guild = ctx_or_guild
    if guild and guild.preferred_locale:
        if str(guild.preferred_locale).lower().startswith("de"):
            return "de"
        if str(guild.preferred_locale).lower().startswith("es"):
            return "es"
    return "en"


def _t(lang: str, key: str, **kwargs) -> str:
    """Look up a localised string and apply format kwargs."""
    text = MESSAGES.get(lang, {}).get(key) or MESSAGES["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text


# ──────────────────────────────────────────────────
#  SECTION TEXT BUILDERS
# ──────────────────────────────────────────────────

def _icon(enabled: bool) -> str:
    return get_emoji("icon_tick") if enabled else get_emoji("icon_cross")


def _build_overview_text(cfg: dict, lang: str = "en") -> str:
    am = cfg["automod"]
    an = cfg["antinuke"]
    ar = cfg["antiraid"]
    are = cfg["antiraid_ext"]
    wu = len(cfg.get("whitelist_users", []))
    wr = len(cfg.get("whitelist_roles", []))
    return (
        f"{_t(lang, 'overview_title', emoji=get_emoji('automod'))}\n"
        f"{_t(lang, 'overview_desc')}\n\n"
        f"{get_emoji('icon_message')} {_t(lang, 'section_msgfilter')}\n"
        f"{_icon(am.get('antispam'))} Anti-Spam  •  "
        f"{_icon(am.get('antilink'))} Anti-Link\n"
        f"{_icon(am.get('badwords'))} Bad Words  •  "
        f"{_icon(am.get('massmention'))} Mass Mention\n\n"
        f"{_t(lang, 'section_antinuke')}\n"
        f"{_icon(am.get('antinuke'))} Enabled  •  "
        f"Action: `{an.get('action', 'strip')}`  •  "
        f"Interval: `{an.get('interval', 10)}s`\n\n"
        f"{_t(lang, 'section_antiraid')}\n"
        f"{_icon(am.get('antiraid'))} Enabled  •  "
        f"Action: `{ar.get('action', 'kick')}`\n"
        f"Threshold: `{ar.get('join_threshold', 10)}` joins / `{ar.get('join_interval', 10)}s`\n\n"
        f"{get_emoji('icon_bot')} {_t(lang, 'section_extraid')}\n"
        f"{_icon(am.get('antiraid_ext'))} Interaction flood  •  "
        f"{_icon(are.get('ext_app_detection', True))} User-installed apps\n"
        f"Raider: `{are.get('raider_action', 'kick')}`  •  "
        f"Operator: `{are.get('operator_action', 'notify')}`  •  "
        f"App abuse: `{are.get('ext_app_action', 'kick')}`\n\n"
        f"{get_emoji('vm_unlock')} {_t(lang, 'section_whitelist')}\n"
        f"{_t(lang, 'wl_summary', wu=wu, wr=wr)}\n\n"
        f"{_t(lang, 'nav_hint')}"
    )


def _build_filter_text(cfg: dict, lang: str = "en") -> str:
    am = cfg["automod"]
    return (
        f"### {get_emoji('icon_message')} {_t(lang, 'filter_title')}\n"
        f"{_t(lang, 'filter_desc')}\n\n"
        f"{_icon(am.get('antispam'))} {_t(lang, 'antispam_desc')}\n"
        f"{_t(lang, 'antispam_thresh', msgs=cfg.get('spam_threshold', 6), secs=cfg.get('spam_interval', 7))}\n\n"
        f"{_icon(am.get('antilink'))} {_t(lang, 'antilink_desc')}\n\n"
        f"{_icon(am.get('badwords'))} {_t(lang, 'badwords_desc')}\n\n"
        f"{_icon(am.get('massmention'))} {_t(lang, 'massmention_desc')}\n"
        f"{_t(lang, 'massmention_max', max=cfg.get('max_mentions', 5))}"
    )


def _build_antinuke_text(cfg: dict, lang: str = "en") -> str:
    am = cfg["automod"]
    an = cfg["antinuke"]
    status = _t(lang, "nuke_status_on") if am.get("antinuke") else _t(lang, "nuke_status_off")
    return (
        f"{_t(lang, 'nuke_title')}\n"
        f"{_t(lang, 'nuke_desc')}\n\n"
        f"{_icon(am.get('antinuke'))} **Anti-Nuke** — currently {status}\n\n"
        f"{_t(lang, 'nuke_thresholds')}\n"
        f"{get_emoji('icon_ban')} {_t(lang, 'nuke_bans',      t=an.get('ban_threshold', 3))}\n"
        f"{get_emoji('icon_cross')} {_t(lang, 'nuke_kicks',     t=an.get('kick_threshold', 3))}\n"
        f"{get_emoji('icon_trash')} {_t(lang, 'nuke_chandel',   t=an.get('channel_delete_threshold', 3))}\n"
        f"{get_emoji('icon_trash')} {_t(lang, 'nuke_roledel',   t=an.get('role_delete_threshold', 3))}\n"
        f"{get_emoji('icon_plus')} {_t(lang, 'nuke_chancreate',t=an.get('channel_create_threshold', 5))}\n"
        f"{get_emoji('icon_link')} {_t(lang, 'nuke_webhookdel',t=an.get('webhook_delete_threshold', 3))}\n\n"
        f"{_t(lang, 'nuke_interval',  t=an.get('interval', 10))}\n"
        f"{_t(lang, 'nuke_action',    action=an.get('action', 'strip'))}\n"
        f"{_t(lang, 'nuke_actions_hint')}"
    )


def _build_antiraid_text(cfg: dict, lang: str = "en") -> str:
    am = cfg["automod"]
    ar = cfg["antiraid"]
    status = _t(lang, "raid_status_on") if am.get("antiraid") else _t(lang, "raid_status_off")
    new_days = ar.get("new_account_days", 0)
    acct_line = (
        _t(lang, "raid_newacct", days=new_days) if new_days > 0
        else _t(lang, "raid_newacct_off")
    )
    return (
        f"{_t(lang, 'raid_title')}\n"
        f"{_t(lang, 'raid_desc')}\n\n"
        f"{_icon(am.get('antiraid'))} **Anti-Raid** — currently {status}\n\n"
        f"{_t(lang, 'raid_threshold', t=ar.get('join_threshold', 10))}\n"
        f"{_t(lang, 'raid_window',    t=ar.get('join_interval', 10))}\n"
        f"{_t(lang, 'raid_action',    action=ar.get('action', 'kick'))}\n"
        f"{acct_line}\n\n"
        f"{_t(lang, 'raid_actions_hint')}"
    )


def _build_ext_raid_text(cfg: dict, lang: str = "en") -> str:
    am = cfg["automod"]
    are = cfg["antiraid_ext"]
    return (
        f"### {get_emoji('icon_bot')} {_t(lang, 'ext_title')}\n\n"
        f"{_t(lang, 'ext_mode1')}\n"
        f"{_t(lang, 'ext_mode1_desc')}\n\n"
        f"{_icon(am.get('antiraid_ext'))} **Enabled**\n"
        f"{_t(lang, 'ext_threshold', t=are.get('interaction_threshold', 5), w=are.get('interaction_window', 30))}\n"
        f"{_t(lang, 'ext_newmember', s=are.get('join_age_limit', 120))}\n"
        f"{_t(lang, 'ext_raiderop', ra=are.get('raider_action', 'kick'), oa=are.get('operator_action', 'notify'))}\n\n"
        f"{_t(lang, 'ext_mode2')}\n"
        f"{_t(lang, 'ext_mode2_desc')}\n\n"
        f"{_icon(are.get('ext_app_detection', True))} **Enabled**\n"
        f"{_t(lang, 'ext_app_threshold', t=are.get('ext_app_threshold', 3), w=are.get('ext_app_window', 15))}\n"
        f"{_t(lang, 'ext_app_action', a=are.get('ext_app_action', 'kick'))}\n\n"
        f"{_t(lang, 'ext_hint')}"
    )


def _build_whitelist_text(cfg: dict, guild: discord.Guild, lang: str = "en") -> str:
    user_ids = cfg.get("whitelist_users", [])
    role_ids = cfg.get("whitelist_roles", [])

    user_lines = [
        f"・ {(guild.get_member(uid) or discord.Object(uid))}"
        for uid in user_ids
    ]
    role_lines = [
        f"・ {(guild.get_role(rid) or discord.Object(rid))}"
        for rid in role_ids
    ]

    return (
        f"### {get_emoji('vm_unlock')} {_t(lang, 'wl_title')}\n"
        f"{_t(lang, 'wl_desc')}\n\n"
        f"{_t(lang, 'wl_users_hdr')}\n"
        f"{chr(10).join(user_lines) or '*None*'}\n\n"
        f"{_t(lang, 'wl_roles_hdr')}\n"
        f"{chr(10).join(role_lines) or '*None*'}\n\n"
        f"{_t(lang, 'wl_hint')}"
    )


def _section_text(cfg: dict, section: str, guild: discord.Guild = None, lang: str = "en") -> str:
    if section == "filter":
        return _build_filter_text(cfg, lang)
    if section == "antinuke":
        return _build_antinuke_text(cfg, lang)
    if section == "antiraid":
        return _build_antiraid_text(cfg, lang)
    if section == "ext_raid":
        return _build_ext_raid_text(cfg, lang)
    if section == "whitelist":
        return _build_whitelist_text(cfg, guild, lang)
    return _build_overview_text(cfg, lang)


# ──────────────────────────────────────────────────────────────────────────────
#  OWNER DM — ANTI-NUKE  (cv2 LayoutView)
# ──────────────────────────────────────────────────────────────────────────────

_NUKE_ACTION_LABELS = {
    "ban":            f"{get_emoji('icon_ban')} Mass Bans",
    "kick":           f"{get_emoji('icon_cross')} Mass Kicks",
    "channel_delete": f"{get_emoji('icon_trash')} Mass Channel Deletes",
    "role_delete":    f"{get_emoji('icon_trash')} Mass Role Deletes",
    "channel_create": f"{get_emoji('icon_plus')} Mass Channel Creates",
    "webhook_delete": f"{get_emoji('icon_link')} Mass Webhook Deletes",
}
_NUKE_ACTION_LABELS_DE = {
    "ban":            f"{get_emoji('icon_ban')} Massen-Bans",
    "kick":           f"{get_emoji('icon_cross')} Massen-Kicks",
    "channel_delete": f"{get_emoji('icon_trash')} Massen-Kanal-Löschungen",
    "role_delete":    f"{get_emoji('icon_trash')} Massen-Rollen-Löschungen",
    "channel_create": f"{get_emoji('icon_plus')} Massen-Kanal-Erstellungen",
    "webhook_delete": f"{get_emoji('icon_link')} Massen-Webhook-Löschungen",
}
_NUKE_ACTION_LABELS_ES = {
    "ban":            f"{get_emoji('icon_ban')} Baneos Masivos",
    "kick":           f"{get_emoji('icon_cross')} Expulsiones Masivas",
    "channel_delete": f"{get_emoji('icon_trash')} Borrado Masivo de Canales",
    "role_delete":    f"{get_emoji('icon_trash')} Borrado Masivo de Roles",
    "channel_create": f"{get_emoji('icon_plus')} Creación Masiva de Canales",
    "webhook_delete": f"{get_emoji('icon_link')} Borrado Masivo de Webhooks",
}
_NUKE_TAKEN_EN = {"strip": "Dangerous roles stripped", "kick": "Offender kicked",  "ban": "Offender banned"}
_NUKE_TAKEN_DE = {"strip": "Gefährliche Rollen entfernt", "kick": "Täter gekickt", "ban": "Täter gebannt"}
_NUKE_TAKEN_ES = {"strip": "Roles peligrosos retirados", "kick": "Infractor expulsado", "ban": "Infractor baneado"}


def _build_nuke_dm_view(
    guild:       discord.Guild,
    offender:    discord.User,
    action_key:  str,
    threshold:   int,
    interval:    int,
    nuke_action: str,
    lang:        str,
) -> discord.ui.LayoutView:
    """
    Build a cv2 LayoutView for the single owner DM sent when anti-nuke fires.
    Red-accented container with title, details, and a timestamp footer.
    """
    ts = int(time.time())

    if lang == "de":
        labels  = _NUKE_ACTION_LABELS_DE
        taken   = _NUKE_TAKEN_DE
        title   = "### 🚨 Anti-Nuke ausgelöst"
        lines   = [
            f"**Server:** {guild.name}",
            f"**Täter:** {offender} (`{offender.id}`)",
            f"**Auslöser:** {labels.get(action_key, action_key)}",
            f"**Anzahl:** {threshold} Aktionen in `{interval}s`",
            f"**Aktion:** {taken.get(nuke_action, nuke_action)}",
        ]
        footer  = f"-# Ausgelöst um <t:{ts}:T> • Niko Anti-Nuke"
    elif lang == "es":
        labels  = _NUKE_ACTION_LABELS_ES
        taken   = _NUKE_TAKEN_ES
        title   = "### 🚨 Anti-Nuke Activado"
        lines   = [
            f"**Servidor:** {guild.name}",
            f"**Infractor:** {offender} (`{offender.id}`)",
            f"**Activado por:** {labels.get(action_key, action_key)}",
            f"**Cantidad:** {threshold} acciones en `{interval}s`",
            f"**Acción tomada:** {taken.get(nuke_action, nuke_action)}",
        ]
        footer  = f"-# Activado a las <t:{ts}:T> • Niko Anti-Nuke"
    else:
        labels  = _NUKE_ACTION_LABELS
        taken   = _NUKE_TAKEN_EN
        title   = "### 🚨 Anti-Nuke Triggered"
        lines   = [
            f"**Server:** {guild.name}",
            f"**Offender:** {offender} (`{offender.id}`)",
            f"**Triggered by:** {labels.get(action_key, action_key)}",
            f"**Count:** {threshold} actions within `{interval}s`",
            f"**Action taken:** {taken.get(nuke_action, nuke_action)}",
        ]
        footer  = f"-# Triggered at <t:{ts}:T> • Niko Anti-Nuke"

    view = discord.ui.LayoutView()
    view.add_item(
        discord.ui.Container(
            discord.ui.TextDisplay(content=title),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="\n".join(lines)),
            discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=footer),
            accent_colour=discord.Colour(0xED4245),
        )
    )
    return view


# ──────────────────────────────────────────────────
#  INTERACTIVE COMPONENTS
# ──────────────────────────────────────────────────

class SectionSelect(discord.ui.Select):
    def __init__(self, automod_cog, guild_id: int, current_section: str):
        self._cog = automod_cog
        self._guild_id = guild_id
        options = [
            discord.SelectOption(
                label="Overview", 
                value="overview", 
                emoji=get_emoji("automod"),
                description="Full snapshot of all protections",
                default=(current_section == "overview")
            ),
            discord.SelectOption(
                label="Message Filter", 
                value="filter", 
                emoji=get_emoji("icon_message"),
                description="Spam, links, bad words, mass mention",
                default=(current_section == "filter")
            ),
            discord.SelectOption(
                label="Anti-Nuke", 
                value="antinuke", 
                emoji="💣",
                description="Stop rogue mods from mass-deleting",
                default=(current_section == "antinuke")
            ),
            discord.SelectOption(
                label="Anti-Raid", 
                value="antiraid", 
                emoji="🌊",
                description="Stop mass member join attacks",
                default=(current_section == "antiraid")
            ),
            discord.SelectOption(
                label="Ext. App Raid", 
                value="ext_raid", 
                emoji=get_emoji("icon_bot"),
                description="User-installed app abuse & interaction floods",
                default=(current_section == "ext_raid")
            ),
            discord.SelectOption(
                label="Whitelist", 
                value="whitelist", 
                emoji=get_emoji("vm_unlock"),
                description="Users and roles exempt from automod",
                default=(current_section == "whitelist")
            ),
        ]
        super().__init__(placeholder="Navigate sections...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        new_panel = _build_panel(self._cog, self._guild_id, self.values[0], interaction.guild)
        await interaction.response.edit_message(view=new_panel, allowed_mentions=ALLOWED_MENTIONS)




class ToggleButton(discord.ui.Button):
    def __init__(self, label: str, key: str, automod_cog, guild_id: int, section: str):
        self._cog = automod_cog
        self._guild_id = guild_id
        self._key = key
        self._section = section
        cfg = automod_cog.utils().get_guild_config(guild_id)
        enabled = cfg["automod"].get(key, False)
        super().__init__(
            label=f"{label}",
            style=discord.ButtonStyle.green if enabled else discord.ButtonStyle.red,
            emoji=_icon(enabled)
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        cfg["automod"][self._key] = not cfg["automod"].get(self._key, False)
        utils.save_config()
        new_panel = _build_panel(self._cog, self._guild_id, self._section, interaction.guild)
        await interaction.response.edit_message(view=new_panel, allowed_mentions=ALLOWED_MENTIONS)


class SubToggleButton(discord.ui.Button):
    """Toggles a boolean inside a sub-config dict (e.g. antiraid_ext.ext_app_detection)."""
    def __init__(self, label: str, sub_cfg_key: str, field: str, automod_cog, guild_id: int, section: str):
        self._cog = automod_cog
        self._guild_id = guild_id
        self._sub_cfg = sub_cfg_key
        self._field = field
        self._section = section
        cfg = automod_cog.utils().get_guild_config(guild_id)
        enabled = cfg.get(sub_cfg_key, {}).get(field, True)
        super().__init__(
            label=f"{label}",
            style=discord.ButtonStyle.green if enabled else discord.ButtonStyle.red,
            emoji=_icon(enabled)
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        cfg[self._sub_cfg][self._field] = not cfg[self._sub_cfg].get(self._field, True)
        utils.save_config()
        new_panel = _build_panel(self._cog, self._guild_id, self._section, interaction.guild)
        await interaction.response.edit_message(view=new_panel, allowed_mentions=ALLOWED_MENTIONS)


class EditThresholdsButton(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int, section: str, label: str = "Edit Thresholds"):
        self._cog = automod_cog
        self._guild_id = guild_id
        self._section = section
        super().__init__(label=label, style=discord.ButtonStyle.blurple, emoji=get_emoji("icon_settings"))

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        modal = _build_threshold_modal(cfg, self._cog, self._guild_id, self._section)
        await interaction.response.send_modal(modal)


class EditExtAppButton(discord.ui.Button):
    """Opens the modal for user-installed app detection settings."""
    def __init__(self, automod_cog, guild_id: int):
        self._cog = automod_cog
        self._guild_id = guild_id
        super().__init__(
            label="Edit App Detection", 
            style=discord.ButtonStyle.blurple,
            emoji=get_emoji("icon_settings")
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        await interaction.response.send_modal(ExtAppThresholdModal(self._cog, self._guild_id, cfg))


# ──────────────────────────────────────────────────
#  THRESHOLD MODALS
# ──────────────────────────────────────────────────

class FilterThresholdModal(discord.ui.Modal, title="Message Filter Thresholds"):
    spam_msgs = discord.ui.TextInput(label="Spam: max messages", placeholder="e.g. 6")
    spam_secs = discord.ui.TextInput(label="Spam: within seconds", placeholder="e.g. 7")
    max_ment = discord.ui.TextInput(label="Mass Mention: max mentions", placeholder="e.g. 5")

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        self.spam_msgs.default = str(cfg.get("spam_threshold", 6))
        self.spam_secs.default = str(cfg.get("spam_interval", 7))
        self.max_ment.default = str(cfg.get("max_mentions", 5))

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["spam_threshold"] = max(1, int(self.spam_msgs.value))
            cfg["spam_interval"] = max(1, int(self.spam_secs.value))
            cfg["max_mentions"] = max(1, int(self.max_ment.value))
            utils.save_config()
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "filter", interaction.guild))
        except ValueError:
            await interaction.response.send_message(_t(lang, "invalid_numbers"), ephemeral=True)


class AntiNukeThresholdModal(discord.ui.Modal, title="Anti-Nuke Thresholds"):
    ban_t = discord.ui.TextInput(label="Ban threshold", placeholder="e.g. 3")
    kick_t = discord.ui.TextInput(label="Kick threshold", placeholder="e.g. 3")
    chan_t = discord.ui.TextInput(label="Channel delete threshold", placeholder="e.g. 3")
    role_t = discord.ui.TextInput(label="Role delete threshold", placeholder="e.g. 3")
    interval = discord.ui.TextInput(label="Interval (seconds)", placeholder="e.g. 10")

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        an = cfg.get("antinuke", {})
        self.ban_t.default = str(an.get("ban_threshold", 3))
        self.kick_t.default = str(an.get("kick_threshold", 3))
        self.chan_t.default = str(an.get("channel_delete_threshold", 3))
        self.role_t.default = str(an.get("role_delete_threshold", 3))
        self.interval.default = str(an.get("interval", 10))

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antinuke"]["ban_threshold"] = max(1, int(self.ban_t.value))
            cfg["antinuke"]["kick_threshold"] = max(1, int(self.kick_t.value))
            cfg["antinuke"]["channel_delete_threshold"] = max(1, int(self.chan_t.value))
            cfg["antinuke"]["role_delete_threshold"] = max(1, int(self.role_t.value))
            cfg["antinuke"]["interval"] = max(1, int(self.interval.value))
            utils.save_config()
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "antinuke", interaction.guild))
        except ValueError:
            await interaction.response.send_message(_t(lang, "invalid_numbers"), ephemeral=True)


class AntiNukeActionModal(discord.ui.Modal, title="Anti-Nuke Response Action"):
    action = discord.ui.TextInput(label="Action (strip / kick / ban)", placeholder="strip", max_length=10)

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        self.action.default = cfg.get("antinuke", {}).get("action", "strip")

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        val = self.action.value.lower().strip()
        lang = get_lang(interaction.guild)
        if val not in ("strip", "kick", "ban"):
            return await interaction.response.send_message(
                _t(lang, "invalid_nuke_action"), ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        cfg["antinuke"]["action"] = val
        utils.save_config()
        await interaction.response.edit_message(
            view=_build_panel(self._cog, self._guild_id, "antinuke", interaction.guild))


class AntiRaidThresholdModal(discord.ui.Modal, title="Anti-Raid Settings"):
    join_t = discord.ui.TextInput(label="Join threshold (members)", placeholder="e.g. 10")
    join_i = discord.ui.TextInput(label="Time window (seconds)", placeholder="e.g. 10")
    action = discord.ui.TextInput(
        label="Action (kick / ban / softban / slowmode / lockdown)",
        placeholder="kick", max_length=10)
    new_days  = discord.ui.TextInput(
        label="New account filter (days, 0 = off)",
        placeholder="e.g. 7",
        required=False)
    slow_secs = discord.ui.TextInput(
        label="Slowmode seconds",
        placeholder="e.g. 30", required=False)

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        ar = cfg.get("antiraid", {})
        self.join_t.default    = str(ar.get("join_threshold", 10))
        self.join_i.default    = str(ar.get("join_interval", 10))
        self.action.default    = ar.get("action", "kick")
        self.new_days.default  = str(ar.get("new_account_days", 0))
        self.slow_secs.default = str(ar.get("lockdown_slowmode", 30))

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        val = self.action.value.lower().strip()
        lang = get_lang(interaction.guild)
        if val not in ("kick", "ban", "softban", "slowmode", "lockdown"):
            return await interaction.response.send_message(
                _t(lang, "invalid_raid_action"), ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antiraid"]["join_threshold"]   = max(1, int(self.join_t.value))
            cfg["antiraid"]["join_interval"]    = max(1, int(self.join_i.value))
            cfg["antiraid"]["action"]           = val
            cfg["antiraid"]["new_account_days"] = max(0, int(self.new_days.value or 0))
            cfg["antiraid"]["lockdown_slowmode"]= max(1, int(self.slow_secs.value or 30))
            utils.save_config()
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "antiraid", interaction.guild))
        except ValueError:
            await interaction.response.send_message(_t(lang, "invalid_numbers"), ephemeral=True)


class ExtRaidThresholdModal(discord.ui.Modal, title="Ext. Raid — Interaction Flood Settings"):
    int_threshold = discord.ui.TextInput(label="Interaction threshold (unique users)", placeholder="e.g. 5")
    int_window = discord.ui.TextInput(label="Detection window (seconds)", placeholder="e.g. 30")
    join_age = discord.ui.TextInput(label="Max member age to count (seconds)", placeholder="e.g. 120")
    raider_act = discord.ui.TextInput(label="Raider action (kick / ban)", placeholder="kick", max_length=10)
    operator_act = discord.ui.TextInput(label="Operator action (notify / kick / ban)", placeholder="notify", max_length=10)

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        are = cfg.get("antiraid_ext", {})
        self.int_threshold.default = str(are.get("interaction_threshold", 5))
        self.int_window.default = str(are.get("interaction_window", 30))
        self.join_age.default = str(are.get("join_age_limit", 120))
        self.raider_act.default = are.get("raider_action", "kick")
        self.operator_act.default = are.get("operator_action", "notify")

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        raider_val = self.raider_act.value.lower().strip()
        operator_val = self.operator_act.value.lower().strip()
        lang = get_lang(interaction.guild)
        if raider_val not in ("kick", "ban"):
            return await interaction.response.send_message(
                _t(lang, "invalid_raider_action"), ephemeral=True)
        if operator_val not in ("notify", "kick", "ban"):
            return await interaction.response.send_message(
                _t(lang, "invalid_operator_action"), ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antiraid_ext"]["interaction_threshold"] = max(1, int(self.int_threshold.value))
            cfg["antiraid_ext"]["interaction_window"] = max(5, int(self.int_window.value))
            cfg["antiraid_ext"]["join_age_limit"] = max(10, int(self.join_age.value))
            cfg["antiraid_ext"]["raider_action"] = raider_val
            cfg["antiraid_ext"]["operator_action"] = operator_val
            utils.save_config()
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "ext_raid", interaction.guild))
        except ValueError:
            await interaction.response.send_message(_t(lang, "invalid_numbers"), ephemeral=True)


class ExtAppThresholdModal(discord.ui.Modal, title="Ext. Raid — User-Installed App Settings"):
    threshold = discord.ui.TextInput(label="Commands per user before action", placeholder="e.g. 3")
    window = discord.ui.TextInput(label="Time window (seconds)", placeholder="e.g. 15")
    action = discord.ui.TextInput(label="Action (kick / ban / warn / log)", placeholder="kick", max_length=10)

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        are = cfg.get("antiraid_ext", {})
        self.threshold.default = str(are.get("ext_app_threshold", 3))
        self.window.default = str(are.get("ext_app_window", 15))
        self.action.default = are.get("ext_app_action", "kick")

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        val = self.action.value.lower().strip()
        lang = get_lang(interaction.guild)
        if val not in ("kick", "ban", "warn", "log"):
            return await interaction.response.send_message(
                _t(lang, "invalid_ext_action"), ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antiraid_ext"]["ext_app_threshold"] = max(1, int(self.threshold.value))
            cfg["antiraid_ext"]["ext_app_window"] = max(5, int(self.window.value))
            cfg["antiraid_ext"]["ext_app_action"] = val
            utils.save_config()
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "ext_raid", interaction.guild))
        except ValueError:
            await interaction.response.send_message(_t(lang, "invalid_numbers"), ephemeral=True)


def _build_threshold_modal(cfg, automod_cog, guild_id, section):
    if section == "antinuke":
        return AntiNukeThresholdModal(automod_cog, guild_id, cfg)
    if section == "antiraid":
        return AntiRaidThresholdModal(automod_cog, guild_id, cfg)
    if section == "ext_raid":
        return ExtRaidThresholdModal(automod_cog, guild_id, cfg)
    return FilterThresholdModal(automod_cog, guild_id, cfg)


class AntiNukeExtThresholdModal(discord.ui.Modal, title="Anti-Nuke — Extended Thresholds"):
    chan_create = discord.ui.TextInput(label="Channel create threshold", placeholder="e.g. 5")
    webhook_del = discord.ui.TextInput(label="Webhook delete threshold", placeholder="e.g. 3")

    def __init__(self, automod_cog, guild_id: int, cfg: dict):
        super().__init__()
        self._cog = automod_cog
        self._guild_id = guild_id
        an = cfg.get("antinuke", {})
        self.chan_create.default = str(an.get("channel_create_threshold", 5))
        self.webhook_del.default = str(an.get("webhook_delete_threshold", 3))

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        try:
            cfg["antinuke"]["channel_create_threshold"] = max(1, int(self.chan_create.value))
            cfg["antinuke"]["webhook_delete_threshold"] = max(1, int(self.webhook_del.value))
            utils.save_config()
            await interaction.response.edit_message(
                view=_build_panel(self._cog, self._guild_id, "antinuke", interaction.guild))
        except ValueError:
            await interaction.response.send_message(_t(lang, "invalid_numbers"), ephemeral=True)


class _NukeExtThresholdButton(discord.ui.Button):
    """Opens extended nuke threshold modal (channel_create, webhook_delete)."""
    def __init__(self, automod_cog, guild_id: int):
        super().__init__(label="Extended Thresholds", style=discord.ButtonStyle.gray,
                         emoji=get_emoji("icon_settings"))
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        await interaction.response.send_modal(AntiNukeExtThresholdModal(self._cog, self._guild_id, cfg))


# ──────────────────────────────────────────────────
#  WHITELIST EPHEMERAL SELECTS & VIEWS
# ──────────────────────────────────────────────────
class _WLUserSelect(discord.ui.UserSelect):
    """Ephemeral select — add members to whitelist."""
    def __init__(self, automod_cog, guild_id: int, message):
        super().__init__(
            placeholder="Choose member(s) to whitelist…",
            min_values=1, max_values=10,
        )
        self._cog = automod_cog
        self._guild_id = guild_id
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        for user in self.values:
            utils.add_whitelist_user(self._guild_id, user.id)
        utils.save_config()
        names = " ".join(u.mention for u in self.values)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(lang, "wl_added_users", emoji=get_emoji("icon_tick"), names=names)
            )
        )
        view.add_item(container)
        await interaction.response.edit_message(
            view=view, allowed_mentions=ALLOWED_MENTIONS
        )
        await self.message.edit(
            view=_build_panel(self._cog, self._guild_id, "whitelist", interaction.guild)
        )


class _WLRoleSelect(discord.ui.RoleSelect):
    """Ephemeral select — add roles to whitelist."""
    def __init__(self, automod_cog, guild_id: int, message):
        super().__init__(
            placeholder="Choose role(s) to whitelist…",
            min_values=1, max_values=10,
        )
        self._cog = automod_cog
        self._guild_id = guild_id
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        for role in self.values:
            utils.add_whitelist_role(self._guild_id, role.id)
        utils.save_config()
        names = " ".join(r.mention for r in self.values)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(lang, "wl_added_roles", emoji=get_emoji("icon_tick"), names=names)
            )
        )
        view.add_item(container)
        await interaction.response.edit_message(
            view=view, allowed_mentions=ALLOWED_MENTIONS
        )
        await self.message.edit(
            view=_build_panel(self._cog, self._guild_id, "whitelist", interaction.guild)
        )


class _WLUserRemoveSelect(discord.ui.Select):
    """Ephemeral select — remove users from whitelist."""
    def __init__(self, automod_cog, guild_id: int, options: list, message):
        super().__init__(
            placeholder="Choose member(s) to remove…",
            min_values=1, max_values=len(options),
            options=options,
        )
        self._cog = automod_cog
        self._guild_id = guild_id
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        for uid_str in self.values:
            utils.remove_whitelist_user(self._guild_id, int(uid_str))
        utils.save_config()
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(lang, "wl_removed_users", emoji=get_emoji("icon_tick"), count=len(self.values))
            )
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)
        await self.message.edit(
            view=_build_panel(self._cog, self._guild_id, "whitelist", interaction.guild)
        )


class _WLRoleRemoveSelect(discord.ui.Select):
    """Ephemeral select — remove roles from whitelist."""
    def __init__(self, automod_cog, guild_id: int, options: list, message):
        super().__init__(
            placeholder="Choose role(s) to remove…",
            min_values=1, max_values=len(options),
            options=options,
        )
        self._cog = automod_cog
        self._guild_id = guild_id
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        for rid_str in self.values:
            utils.remove_whitelist_role(self._guild_id, int(rid_str))
        utils.save_config()
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(lang, "wl_removed_roles", emoji=get_emoji("icon_tick"), count=len(self.values))
            )
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)
        await self.message.edit(
            view=_build_panel(self._cog, self._guild_id, "whitelist", interaction.guild)
        )


class _WLAddUserBtn(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int):
        super().__init__(
            label="Add User", 
            style=discord.ButtonStyle.green,
            emoji=get_emoji("icon_plus")
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        lang = get_lang(interaction.guild)
        message = interaction.message
        view = discord.ui.LayoutView(timeout=60)
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(lang, "wl_add_user_prompt")
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _WLUserSelect(self._cog, self._guild_id, message)
            )
        )
        view.add_item(container)
        await interaction.response.send_message(
            view=view, ephemeral=True,
        )


class _WLAddRoleBtn(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int):
        super().__init__(
            label="Add Role", 
            style=discord.ButtonStyle.green,
            emoji=get_emoji("icon_plus")
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        lang = get_lang(interaction.guild)
        message = interaction.message
        view = discord.ui.LayoutView(timeout=60)
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(lang, "wl_add_role_prompt")
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _WLRoleSelect(self._cog, self._guild_id, message)
            )
        )
        view.add_item(container)
        await interaction.response.send_message(
            view=view, ephemeral=True,
        )


class _WLRemoveUserBtn(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int, has_users: bool):
        super().__init__(
            label="➖ Remove User",
            style=discord.ButtonStyle.red,
            disabled=not has_users,
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        user_ids = cfg.get("whitelist_users", [])
        options = []
        for uid in user_ids:
            member = interaction.guild.get_member(uid)
            label = member.display_name if member else f"User {uid}"
            options.append(discord.SelectOption(
                label=label[:100], value=str(uid),
                description=f"ID: {uid}",
            ))
        if not options:
            return await interaction.response.send_message(
                _t(lang, "wl_no_users"), ephemeral=True,
            )
        message = interaction.message
        view = discord.ui.LayoutView(timeout=60)
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(lang, "wl_remove_user_prompt")
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _WLUserRemoveSelect(self._cog, self._guild_id, options, message)
            )
        )
        view.add_item(container)
        await interaction.response.send_message(
            view=view, ephemeral=True,
        )


class _WLRemoveRoleBtn(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int, has_roles: bool):
        super().__init__(
            label="➖ Remove Role",
            style=discord.ButtonStyle.red,
            disabled=not has_roles,
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        lang = get_lang(interaction.guild)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        role_ids = cfg.get("whitelist_roles", [])
        options = []
        for rid in role_ids:
            role = interaction.guild.get_role(rid)
            label = role.name if role else f"Role {rid}"
            options.append(discord.SelectOption(
                label=label[:100], value=str(rid),
                description=f"ID: {rid}",
            ))
        if not options:
            return await interaction.response.send_message(
                _t(lang, "wl_no_roles"), ephemeral=True,
            )
        message = interaction.message
        view = discord.ui.LayoutView(timeout=60)
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(lang, "wl_remove_role_prompt")
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _WLRoleRemoveSelect(self._cog, self._guild_id, options, message)
            )
        )
        view.add_item(container)
        await interaction.response.send_message(
            view=view, ephemeral=True,
        )


# ──────────────────────────────────────────────────
#  PANEL BUILDER
# ──────────────────────────────────────────────────

def _build_panel(self, guild_id: int, section: str = "overview", guild: discord.Guild = None) -> discord.ui.LayoutView:
    utils = self.utils()
    cfg = utils.get_guild_config(guild_id)
    lang = get_lang(guild)

    view = discord.ui.LayoutView(timeout=300)
    text = _section_text(cfg, section, guild, lang)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=text),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
    )
    container.add_item(discord.ui.ActionRow(SectionSelect(self, guild_id, section)))

    if section == "filter":
        container.add_item(discord.ui.ActionRow(
            ToggleButton("Anti-Spam", "antispam", self, guild_id, section),
            ToggleButton("Anti-Link", "antilink", self, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            ToggleButton("Bad Words", "badwords", self, guild_id, section),
            ToggleButton("Mass Mention", "massmention", self, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(self, guild_id, section),
        ))

    elif section == "antinuke":
        container.add_item(discord.ui.ActionRow(
            ToggleButton("Anti-Nuke", "antinuke", self, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(self, guild_id, section),
            _NukeActionButton(self, guild_id),
            _NukeExtThresholdButton(self, guild_id),
        ))

    elif section == "antiraid":
        container.add_item(discord.ui.ActionRow(
            ToggleButton("Anti-Raid", "antiraid", self, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(self, guild_id, section),
        ))

    elif section == "ext_raid":
        container.add_item(discord.ui.ActionRow(
            ToggleButton("Interaction Flood", "antiraid_ext", self, guild_id, section),
            SubToggleButton("User-App Detection", "antiraid_ext", "ext_app_detection", self, guild_id, section),
        ))
        container.add_item(discord.ui.ActionRow(
            EditThresholdsButton(self, guild_id, section, label="Flood Thresholds"),
            EditExtAppButton(self, guild_id),
        ))

    elif section == "whitelist":
        wl_cfg = cfg
        has_u = bool(wl_cfg.get("whitelist_users", []))
        has_r = bool(wl_cfg.get("whitelist_roles", []))
        container.add_item(discord.ui.ActionRow(
            _WLAddUserBtn(self, guild_id),
            _WLAddRoleBtn(self, guild_id),
        ))
        container.add_item(discord.ui.ActionRow(
            _WLRemoveUserBtn(self, guild_id, has_u),
            _WLRemoveRoleBtn(self, guild_id, has_r),
        ))

    view.add_item(container)
    return view


class AntiNukeActionSelect(discord.ui.Select):
    def __init__(self, automod_cog, guild_id: int, cfg: dict, message):
        self._cog = automod_cog
        self._guild_id = guild_id
        self.message = message
        options = [
            discord.SelectOption(
                label="Strip Dangerous Roles", value="strip",
                description="Remove roles with dangerous permissions",
            ),
            discord.SelectOption(
                label="Kick Offender", value="kick",
                description="Kick the member who triggered the action",
            ),
            discord.SelectOption(
                label="Ban Offender", value="ban",
                description="Ban the member who triggered the action",
            )
        ]
        super().__init__(
            placeholder="Choose action…",
            options=options,
            min_values=1, max_values=1
        )


    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        
        val = self.values[0]
        lang = get_lang(interaction.guild)
        if val not in ("strip", "kick", "ban"):
            return await interaction.response.send_message(
                _t(lang, "invalid_nuke_action"), ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        cfg["antinuke"]["action"] = val
        utils.save_config()
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_tick')} Anti-Nuke action set to **{val}**"
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)
        await self.message.edit(
            view=_build_panel(self._cog, self._guild_id, "antinuke", interaction.guild))


class _NukeActionButton(discord.ui.Button):
    def __init__(self, automod_cog, guild_id: int):
        super().__init__(
            label="Set Action", 
            style=discord.ButtonStyle.gray,
            emoji=get_emoji("icon_utility")
        )
        self._cog = automod_cog
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You need **Administrator** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        utils = self._cog.utils()
        cfg = utils.get_guild_config(self._guild_id)
        message = interaction.message
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content="Choose the action to take when anti-nuke is triggered:"
            ),
            discord.ui.ActionRow(
                AntiNukeActionSelect(self._cog, self._guild_id, cfg, message)
            )
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)
        # await interaction.response.send_modal(AntiNukeActionModal(self._cog, self._guild_id, cfg))


# ──────────────────────────────────────────────────
#  AUTOMOD COG
# ──────────────────────────────────────────────────


__all__ = [k for k in list(globals()) if not k.startswith("__")]
