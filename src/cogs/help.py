"""
Help System — fully trilingual (EN / DE / ES)
─────────────────────────────────────────────
All UI strings, category descriptions, category headers, pagination labels,
and command detail labels are localised to the guild's preferred locale.
Command help strings use the existing { 'en': '…', 'de': '…', 'es': '…' } JSON format.
"""

from typing import List, Tuple
import json

import discord
from discord.ext import commands

from config.emojis import get_emoji

PAGE_SIZE = 8


# ===================================================
#  LANGUAGE UTILITIES
# ===================================================

def get_lang(ctx_or_guild=None) -> str:
    """Return 'de' when the guild's preferred locale is German, else 'en'."""
    guild = None
    if isinstance(ctx_or_guild, commands.Context):
        guild = ctx_or_guild.guild
    elif isinstance(ctx_or_guild, discord.Interaction):
        guild = ctx_or_guild.guild
    elif isinstance(ctx_or_guild, discord.Guild):
        guild = ctx_or_guild
    if guild and guild.preferred_locale:
        if str(guild.preferred_locale).lower().startswith("de"):
            return "de"
        if str(guild.preferred_locale).lower().startswith("es"):
            return "es"
    return "en"


def get_command_help(ctx_or_interaction, cmd: commands.Command) -> str:
    """
    Return the localised help string for a command.
    Commands store help as JSON: { 'en': '…', 'de': '…' }
    Falls back to the raw help string if it isn't JSON.
    """
    lang = get_lang(ctx_or_interaction)
    if cmd.help:
        try:
            help_dict = json.loads(cmd.help.replace("'", '"'))
            text = help_dict.get(lang) or help_dict.get("en")
            return text or cmd.help
        except (json.JSONDecodeError, AttributeError):
            return cmd.help
    return ""


def _ui(lang: str, key: str, **kwargs) -> str:
    """Shorthand for pulling a UI string in the given language."""
    text = _UI_STRINGS.get(lang, _UI_STRINGS["en"]).get(key)
    if text is None:
        text = _UI_STRINGS["en"][key]
    return text.format(**kwargs) if kwargs else text


# ===================================================
#  LOCALISED UI STRINGS
# ===================================================

_UI_STRINGS: dict[str, dict] = {
    "en": {
        "dropdown_placeholder": "☕ Pick a category…",
        "no_commands":          "*No commands found.*",
        "no_desc":              "No description provided.",
        "cmd_not_found_title":  "Command Not Found",
        "cmd_not_found_body":   "No command named `{name}` exists.\nUse the help menu to browse available commands.",
        "detail_description":   "Description",
        "detail_usage":         "Usage",
        "detail_aliases":       "Aliases",
        "detail_subcommands":   "Subcommands",
        "detail_category":      "Category",
        "btn_prev":             "◀ Prev",
        "btn_next":             "Next ▶",
        "btn_page":             "Page {page}/{total}",
        "general_title":        "### 🌸 Welcome to Niko's Help Menu",
        "general_intro":        "Use the dropdown below to browse commands by category.",
        "general_about_title":  "**About Niko**",
        "general_about_body": (
            "Niko is a cozy, AI-powered Discord bot with a café personality — "
            "bilingual (EN/DE), packed with economy, leveling, music, moderation, and more!"
        ),
        "general_links_title":  "**{icon} Links**",
    },
    "es": {
        "dropdown_placeholder": "☕ Elige una categoría…",
        "no_commands":          "*No se encontraron comandos.*",
        "no_desc":              "Sin descripción.",
        "cmd_not_found_title":  "Comando no encontrado",
        "cmd_not_found_body":   "No existe un comando llamado `{name}`.\nUsa el menú de ayuda para ver los comandos disponibles.",
        "detail_description":   "Descripción",
        "detail_usage":         "Uso",
        "detail_aliases":       "Alias",
        "detail_subcommands":   "Subcomandos",
        "detail_category":      "Categoría",
        "btn_prev":             "◀ Anterior",
        "btn_next":             "Siguiente ▶",
        "btn_page":             "Página {page}/{total}",
        "general_title":        "### 🌸 Bienvenido al menú de ayuda de Niko",
        "general_intro":        "Usa el menú desplegable para explorar los comandos por categoría.",
        "general_about_title":  "**Sobre Niko**",
        "general_about_body": (
            "Niko es un bot de Discord acogedor con personalidad de café e impulsado por IA — "
            "trilingüe (EN/DE/ES), repleto de economía, niveles, música, moderación y más!"
        ),
        "general_links_title":  "**{icon} Enlaces**",
    },
    "de": {
        "dropdown_placeholder": "☕ Kategorie auswählen…",
        "no_commands":          "*Keine Befehle gefunden.*",
        "no_desc":              "Keine Beschreibung verfügbar.",
        "cmd_not_found_title":  "Befehl nicht gefunden",
        "cmd_not_found_body":   "Kein Befehl namens `{name}` gefunden.\nNutze das Hilfemenü, um Befehle zu durchsuchen.",
        "detail_description":   "Beschreibung",
        "detail_usage":         "Verwendung",
        "detail_aliases":       "Aliase",
        "detail_subcommands":   "Unterbefehle",
        "detail_category":      "Kategorie",
        "btn_prev":             "◀ Zurück",
        "btn_next":             "Weiter ▶",
        "btn_page":             "Seite {page}/{total}",
        "general_title":        "### 🌸 Willkommen bei Nikos Hilfemenü",
        "general_intro":        "Nutze das Dropdown unten, um Befehle nach Kategorie zu durchsuchen.",
        "general_about_title":  "**Über Niko**",
        "general_about_body": (
            "Niko ist ein gemütlicher, KI-gestützter Discord-Bot mit Café-Persönlichkeit — "
            "zweisprachig (DE/EN), vollgepackt mit Wirtschaft, Leveling, Musik, Moderation und mehr!"
        ),
        "general_links_title":  "**{icon} Links**",
    },
}


# ===================================================
#  CATEGORY DEFINITIONS
# ===================================================

# (label, emoji) — descriptions are pulled from CATEGORY_DESCS per lang
_CATEGORY_LIST: List[Tuple[str, str]] = [
    ("General",        f"{get_emoji('icon_general')}"),
    ("Fun",            f"{get_emoji('icon_games')}"),
    ("Gambling",       f"{get_emoji('icon_gambling')}"),
    ("Economy",        f"{get_emoji('icon_economy')}"),
    ("Roleplay",       f"{get_emoji('icon_roleplay')}"),
    ("Info",           f"{get_emoji('icon_stats')}"),
    ("Utility",        f"{get_emoji('icon_utility')}"),
    ("AI",             f"{get_emoji('icon_ai')}"),
    ("Moderation",     f"{get_emoji('icon_moderation')}"),
    ("AutoMod",        f"{get_emoji('icon_automod')}"),
    ("EmojiManager",   f"{get_emoji('icon_paint')}"),
    ("Onboarding",     f"{get_emoji('icon_welcome')}"),
    ("NSFW",           f"{get_emoji('icon_nsfw')}"),
    ("Music",          f"{get_emoji('music')}"),
    ("Leveling",       f"{get_emoji('icon_leveling')}"),
    ("Notifier",       f"{get_emoji('icon_megaphone')}"),
    ("VoiceMaster",    f"{get_emoji('icon_voicemaster')}"),
    ("Ticket",         f"{get_emoji('icon_ticket')}"),
    ("Image Tools",    f"{get_emoji('icon_image')}"),
    ("Giveaway",       f"{get_emoji('icon_giveaway')}"),
    ("Customization",  f"{get_emoji('icon_edit')}"),
]

CATEGORY_DESCS: dict[str, dict[str, str]] = {
    "en": {
        "General":       "General bot information",
        "Fun":           "Fun commands",
        "Gambling":      "Blackjack, Slots, Roulette",
        "Economy":       "Balance, daily, work, etc.",
        "Roleplay":      "RP commands",
        "Info":          "User/server info commands",
        "Utility":       "Misc tools and utilities",
        "AI":            "AI commands",
        "Moderation":    "Moderation commands",
        "AutoMod":       "AutoMod commands",
        "EmojiManager":  "Emoji manager commands",
        "Onboarding":    "Onboarding commands",
        "NSFW":          "NSFW commands",
        "Music":         "Music commands",
        "Leveling":      "Leveling commands",
        "Notifier":      "Social media notifier",
        "VoiceMaster":   "Voice channel management",
        "Ticket":        "Ticket commands",
        "Image Tools":   "Image manipulation commands",
        "Giveaway":      "Giveaway commands",
        "Customization": "Customization commands",
    },
    "de": {
        "General":       "Allgemeine Bot-Informationen",
        "Fun":           "Spaßbefehle",
        "Gambling":      "Blackjack, Slots, Roulette",
        "Economy":       "Guthaben, tägl. Belohnung, Arbeit usw.",
        "Roleplay":      "Rollenspiel-Befehle",
        "Info":          "Nutzer-/Server-Informationen",
        "Utility":       "Nützliche Hilfswerkzeuge",
        "AI":            "KI-Befehle",
        "Moderation":    "Moderationsbefehle",
        "AutoMod":       "Automatische Moderation",
        "EmojiManager":  "Emoji-Verwaltung",
        "Onboarding":    "Willkommens-Einrichtung",
        "NSFW":          "NSFW-Befehle",
        "Music":         "Musikbefehle",
        "Leveling":      "Leveling-Befehle",
        "Notifier":      "Social-Media-Benachrichtigungen",
        "VoiceMaster":   "Sprachkanal-Verwaltung",
        "Ticket":        "Ticket-Befehle",
        "Image Tools":   "Bildbearbeitungsbefehle",
        "Giveaway":      "Gewinnspiel-Befehle",
        "Customization": "Anpassungsbefehle",
    },
    "es": {
        "General":       "Información general del bot",
        "Fun":           "Comandos divertidos",
        "Gambling":      "Blackjack, tragamonedas, ruleta",
        "Economy":       "Saldo, diario, trabajo, etc.",
        "Roleplay":      "Comandos de rol",
        "Info":          "Info de usuario/servidor",
        "Utility":       "Herramientas y utilidades varias",
        "AI":            "Comandos de IA",
        "Moderation":    "Comandos de moderación",
        "AutoMod":       "Comandos de automoderación",
        "EmojiManager":  "Gestión de emojis",
        "Onboarding":    "Bienvenida a nuevos miembros",
        "NSFW":          "Comandos NSFW",
        "Music":         "Comandos de música",
        "Leveling":      "Comandos de niveles",
        "Notifier":      "Notificaciones de redes sociales",
        "VoiceMaster":   "Gestión de canales de voz",
        "Ticket":        "Comandos de tickets",
        "Image Tools":   "Manipulación de imágenes",
        "Giveaway":      "Comandos de sorteos",
        "Customization": "Comandos de personalización",
    },
}

# Category header strings shown above the command list — localised.
# Keyed by lang → category label → header markdown string.
CATEGORY_HEADERS: dict[str, dict[str, str]] = {
    "en": {
        "General": "",
        "Fun": (
            f"{get_emoji('icon_games')} **Fun Commands**\n"
            "> Commands for fun and games!"
        ),
        "Gambling": (
            f"{get_emoji('icon_gambling')} **Casino Commands**\n"
            "> Play games of chance!"
        ),
        "Economy": (
            f"{get_emoji('icon_economy')} **Economy Commands**\n"
            "> Earn and spend virtual currency!"
        ),
        "Roleplay": (
            f"{get_emoji('icon_roleplay')} **Roleplay Commands**\n"
            "> Fun roleplay commands!"
        ),
        "Info": (
            f"{get_emoji('icon_stats')} **Information Commands**\n"
            "> Get info about users, servers, and more!"
        ),
        "Utility": (
            f"{get_emoji('icon_utility')} **Utility Commands**\n"
            "> Useful tools and utilities."
        ),
        "AI": (
            f"{get_emoji('icon_ai')} **AI Commands**\n"
            "> Interact with Niko's AI features!"
        ),
        "Moderation": (
            f"{get_emoji('icon_moderation')} **Moderation Commands**\n"
            "> Moderation tools for server management."
        ),
        "AutoMod": (
            f"{get_emoji('icon_automod')} **AutoMod Commands**\n"
            "> Automated moderation to keep your server safe."
        ),
        "EmojiManager": (
            f"{get_emoji('icon_paint')} **Emoji Manager Commands**\n"
            "> Manage custom emojis in your server."
        ),
        "Onboarding": (
            f"{get_emoji('icon_welcome')} **Onboarding Commands**\n"
            "> Set up welcome messages and roles for new members."
        ),
        "NSFW": (
            f"{get_emoji('icon_nsfw')} **NSFW Commands**\n"
            "> These commands only work in NSFW-marked channels."
        ),
        "Music": (
            f"{get_emoji('music')} **Music Commands**\n"
            "> Play music in your voice channel!"
        ),
        "Leveling": (
            f"{get_emoji('icon_leveling')} **Leveling Commands**\n"
            "> Level up by chatting and earning XP!"
        ),
        "Notifier": (
            f"{get_emoji('icon_megaphone')} **Notifier Commands**\n"
            "> Get notified about new posts from your favourite creators!"
        ),
        "VoiceMaster": (
            f"{get_emoji('icon_voicemaster')} **VoiceMaster Commands**\n"
            "> Create and manage temporary voice channels!"
        ),
        "Ticket": (
            f"{get_emoji('icon_ticket')} **Ticket Commands**\n"
            "> Create and manage support tickets."
        ),
        "Image Tools": (
            f"{get_emoji('icon_image')} **Image Tools**\n"
            "> Manipulate images with these commands!"
        ),
        "Giveaway": (
            f"{get_emoji('icon_giveaway')} **Giveaway Commands**\n"
            "> Host and manage giveaways in your server!"
        ),
        "Customization": (
            f"{get_emoji('icon_edit')} **Customization Commands**\n"
            "> Customize Niko's pfp, banner, and more!"
        ),
    },
    "de": {
        "General": "",
        "Fun": (
            f"{get_emoji('icon_games')} **Spaßbefehle**\n"
            "> Befehle für Spaß und Spiele!"
        ),
        "Gambling": (
            f"{get_emoji('icon_gambling')} **Casino-Befehle**\n"
            "> Spiele Glücksspiele!"
        ),
        "Economy": (
            f"{get_emoji('icon_economy')} **Wirtschaftsbefehle**\n"
            "> Verdiene und gib virtuelle Währung aus!"
        ),
        "Roleplay": (
            f"{get_emoji('icon_roleplay')} **Rollenspiel-Befehle**\n"
            "> Spaßige Rollenspiel-Befehle!"
        ),
        "Info": (
            f"{get_emoji('icon_stats')} **Informationsbefehle**\n"
            "> Informationen zu Nutzern, Servern und mehr!"
        ),
        "Utility": (
            f"{get_emoji('icon_utility')} **Hilfswerkzeuge**\n"
            "> Nützliche Tools und Dienstprogramme."
        ),
        "AI": (
            f"{get_emoji('icon_ai')} **KI-Befehle**\n"
            "> Interagiere mit Nikos KI-Funktionen!"
        ),
        "Moderation": (
            f"{get_emoji('icon_moderation')} **Moderationsbefehle**\n"
            "> Moderationstools für die Serververwaltung."
        ),
        "AutoMod": (
            f"{get_emoji('icon_automod')} **AutoMod-Befehle**\n"
            "> Automatische Moderation für deinen Server."
        ),
        "EmojiManager": (
            f"{get_emoji('icon_paint')} **Emoji-Manager-Befehle**\n"
            "> Verwalte benutzerdefinierte Emojis auf deinem Server."
        ),
        "Onboarding": (
            f"{get_emoji('icon_welcome')} **Onboarding-Befehle**\n"
            "> Richte Willkommensnachrichten und Rollen für neue Mitglieder ein."
        ),
        "NSFW": (
            f"{get_emoji('icon_nsfw')} **NSFW-Befehle**\n"
            "> Diese Befehle funktionieren nur in als NSFW markierten Kanälen."
        ),
        "Music": (
            f"{get_emoji('music')} **Musikbefehle**\n"
            "> Musik in deinem Sprachkanal abspielen!"
        ),
        "Leveling": (
            f"{get_emoji('icon_leveling')} **Leveling-Befehle**\n"
            "> Steige durch Chatten und XP-Sammeln auf!"
        ),
        "Notifier": (
            f"{get_emoji('icon_megaphone')} **Benachrichtigungs-Befehle**\n"
            "> Werde über neue Beiträge deiner Lieblings-Ersteller benachrichtigt!"
        ),
        "VoiceMaster": (
            f"{get_emoji('icon_voicemaster')} **VoiceMaster-Befehle**\n"
            "> Temporäre Sprachkanäle erstellen und verwalten!"
        ),
        "Ticket": (
            f"{get_emoji('icon_ticket')} **Ticket-Befehle**\n"
            "> Support-Tickets erstellen und verwalten."
        ),
        "Image Tools": (
            f"{get_emoji('icon_image')} **Bildbearbeitungs-Befehle**\n"
            "> Bilder mit diesen Befehlen bearbeiten!"
        ),
        "Giveaway": (
            f"{get_emoji('icon_giveaway')} **Gewinnspiel-Befehle**\n"
            "> Gewinnspiele auf deinem Server veranstalten und verwalten!"
        ),
        "Customization": (
            f"{get_emoji('icon_edit')} **Anpassungsbefehle**\n"
            "> Nikos Profilbild, Banner und mehr anpassen!"
        ),
    },
    "es": {
        "General": "",
        "Fun": (
            f"{get_emoji('icon_games')} **Comandos Divertidos**\n"
            "> ¡Comandos para diversión y juegos!"
        ),
        "Gambling": (
            f"{get_emoji('icon_gambling')} **Comandos del Casino**\n"
            "> ¡Juega juegos de azar!"
        ),
        "Economy": (
            f"{get_emoji('icon_economy')} **Comandos de Economía**\n"
            "> ¡Gana y gasta moneda virtual!"
        ),
        "Roleplay": (
            f"{get_emoji('icon_roleplay')} **Comandos de Rol**\n"
            "> ¡Comandos divertidos de rol!"
        ),
        "Info": (
            f"{get_emoji('icon_stats')} **Comandos de Información**\n"
            "> ¡Obtén info sobre usuarios, servidores y más!"
        ),
        "Utility": (
            f"{get_emoji('icon_utility')} **Comandos de Utilidad**\n"
            "> Herramientas útiles y utilidades."
        ),
        "AI": (
            f"{get_emoji('icon_ai')} **Comandos de IA**\n"
            "> ¡Interactúa con las funciones de IA de Niko!"
        ),
        "Moderation": (
            f"{get_emoji('icon_moderation')} **Comandos de Moderación**\n"
            "> Herramientas de moderación para gestionar el servidor."
        ),
        "AutoMod": (
            f"{get_emoji('icon_automod')} **Comandos de AutoMod**\n"
            "> Moderación automática para mantener tu servidor seguro."
        ),
        "EmojiManager": (
            f"{get_emoji('icon_paint')} **Comandos del Gestor de Emojis**\n"
            "> Gestiona emojis personalizados en tu servidor."
        ),
        "Onboarding": (
            f"{get_emoji('icon_welcome')} **Comandos de Bienvenida**\n"
            "> Configura mensajes de bienvenida y roles para nuevos miembros."
        ),
        "NSFW": (
            f"{get_emoji('icon_nsfw')} **Comandos NSFW**\n"
            "> Estos comandos solo funcionan en canales marcados como NSFW."
        ),
        "Music": (
            f"{get_emoji('music')} **Comandos de Música**\n"
            "> ¡Reproduce música en tu canal de voz!"
        ),
        "Leveling": (
            f"{get_emoji('icon_leveling')} **Comandos de Niveles**\n"
            "> ¡Sube de nivel chateando y ganando XP!"
        ),
        "Notifier": (
            f"{get_emoji('icon_megaphone')} **Comandos de Notificaciones**\n"
            "> ¡Recibe notificaciones sobre nuevas publicaciones de tus creadores favoritos!"
        ),
        "VoiceMaster": (
            f"{get_emoji('icon_voicemaster')} **Comandos de VoiceMaster**\n"
            "> ¡Crea y gestiona canales de voz temporales!"
        ),
        "Ticket": (
            f"{get_emoji('icon_ticket')} **Comandos de Tickets**\n"
            "> Crea y gestiona tickets de soporte."
        ),
        "Image Tools": (
            f"{get_emoji('icon_image')} **Herramientas de Imagen**\n"
            "> ¡Manipula imágenes con estos comandos!"
        ),
        "Giveaway": (
            f"{get_emoji('icon_giveaway')} **Comandos de Sorteos**\n"
            "> ¡Organiza y gestiona sorteos en tu servidor!"
        ),
        "Customization": (
            f"{get_emoji('icon_edit')} **Comandos de Personalización**\n"
            "> ¡Personaliza la foto de perfil, banner y más de Niko!"
        ),
    },
}

# Map category label → list of cog names that contribute to it.
CATEGORY_COGS: dict[str, List[str]] = {
    "General":       [],
    "Fun":           ["UwULock", "Meme", "tictactoe", "CuteAnimals", "FunCog", "ConnectFourCog"],
    "Gambling":      ["Blackjack", "Roulette", "Slots", "GamblingCog"],
    "Economy":       ["EconomyCog"],
    "Roleplay":      ["RolePlayCog"],
    "Info":          ["InfoCog"],
    "Utility":       ["UtilityCog", "Snipe", "Define", "AFKCog"],
    "AI":            ["AICog", "AIConfig"],
    "Moderation":    ["Moderation"],
    "AutoMod":       ["AutoMod"],
    "EmojiManager":  ["EmojiManagerCog"],
    "Onboarding":    ["Onboarding"],
    "NSFW":          ["NSFW"],
    "Music":         ["MusicSystem"],
    "Leveling":      ["Leveling"],
    "Notifier":      ["Notifier", "YouTube"],
    "VoiceMaster":   ["VoiceMaster"],
    "Ticket":        ["Tickets"],
    "Image Tools":   ["ImageTools", "AiImageTools"],
    "Giveaway":      ["Giveaway"],
    "Customization": ["Customization", "PrefixConfig"],
}


def _category_header(lang: str, category: str) -> str:
    return CATEGORY_HEADERS.get(lang, CATEGORY_HEADERS["en"]).get(
        category,
        CATEGORY_HEADERS["en"].get(category, ""),
    )


def _category_desc(lang: str, category: str) -> str:
    return CATEGORY_DESCS.get(lang, CATEGORY_DESCS["en"]).get(
        category,
        CATEGORY_DESCS["en"].get(category, ""),
    )


# ===================================================
#  PREFIX RESOLVER
# ===================================================

async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    raw = bot.command_prefix
    if isinstance(raw, str):
        return raw
    if isinstance(raw, (list, tuple)):
        return raw[0]
    try:
        msg = getattr(ctx_or_interaction, "message", None)
        if msg is None and isinstance(ctx_or_interaction, discord.Interaction):
            msg = ctx_or_interaction.message
        if msg is None:
            return "."
        prefixes = raw(bot, msg)
        if isinstance(prefixes, (list, tuple)) and prefixes:
            return prefixes[0]
    except Exception:
        pass
    return "."


# ===================================================
#  CONTENT BUILDERS
# ===================================================

def _general_text(bot: commands.Bot, lang: str) -> str:
    invite = f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=8"
    return (
        f"{_ui(lang, 'general_title')}\n"
        f"{_ui(lang, 'general_intro')}\n\n"
        f"{_ui(lang, 'general_about_title')}\n"
        f"{_ui(lang, 'general_about_body')}\n\n"
        f"{_ui(lang, 'general_links_title', icon=get_emoji('icon_link'))}\n"
        f"-# [GitHub](https://github.com/developer51709/Niko) • "
        f"[Invite]({invite}) • "
        f"[Website](https://developer51709.github.io/Niko) • "
        f"[Support Server](https://dsc.gg/astral-haven)"
    )


async def _commands_text(
    cog_names: List[str],
    bot: commands.Bot,
    ctx_or_interaction,
    page: int,
) -> Tuple[str, int]:
    """
    Build a paginated markdown string listing commands from one or more cogs.
    Returns (content, total_pages).
    """
    lang   = get_lang(ctx_or_interaction)
    prefix = await _resolve_prefix(bot, ctx_or_interaction)

    commands_list: List[commands.Command] = []
    for cog_name in cog_names:
        cog = bot.get_cog(cog_name)
        if cog:
            commands_list.extend(cog.get_commands())

    if not commands_list:
        return _ui(lang, "no_commands"), 1

    total       = len(commands_list)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page        = max(1, min(page, total_pages))

    start         = (page - 1) * PAGE_SIZE
    page_commands = commands_list[start: start + PAGE_SIZE]

    no_desc = _ui(lang, "no_desc")
    lines   = []
    for cmd in page_commands:
        desc = get_command_help(ctx_or_interaction, cmd) or no_desc
        lines.append(f"**`{prefix}{cmd.name}`**\n-# {desc}")

    return "\n".join(lines), total_pages


async def _command_detail_text(
    bot: commands.Bot,
    cmd: commands.Command,
    ctx_or_interaction,
) -> str:
    lang   = get_lang(ctx_or_interaction)
    prefix = await _resolve_prefix(bot, ctx_or_interaction)

    if hasattr(cmd, "parent") and cmd.parent:
        parent = cmd.parent.name
        usage  = f"{prefix}{parent} {cmd.name} {cmd.signature or ''}"
    else:
        parent = None
        usage  = f"{prefix}{cmd.name} {cmd.signature or ''}"

    no_desc = _ui(lang, "no_desc")
    lines   = [
        f"### 📘 `{cmd.name}`",
        "",
        f"**{_ui(lang, 'detail_description')}**\n"
        f"{get_command_help(ctx_or_interaction, cmd) or no_desc}",
        "",
        f"**{_ui(lang, 'detail_usage')}**\n```\n{usage.strip()}\n```",
    ]

    if cmd.aliases:
        lines.append(
            f"\n**{_ui(lang, 'detail_aliases')}**\n"
            + ", ".join(f"`{a}`" for a in cmd.aliases)
        )

    if hasattr(cmd, "commands"):
        lines.append(f"\n**{_ui(lang, 'detail_subcommands')}**")
        for sub in cmd.commands:
            sub_desc = get_command_help(ctx_or_interaction, sub) or no_desc
            if parent:
                sub_usage = f"`{prefix}{parent} {cmd.name} {sub.name}`"
            else:
                sub_usage = f"`{prefix}{cmd.name} {sub.name}`"
            lines.append(f"{sub_usage}\n-# {sub_desc}")

    if cmd.cog_name:
        lines.append(f"\n**{_ui(lang, 'detail_category')}**\n{cmd.cog_name}")

    return "\n".join(lines)


# ===================================================
#  DROPDOWN
# ===================================================

class HelpDropdown(discord.ui.Select):
    """Category dropdown — options are localised per guild locale."""

    def __init__(self, bot: commands.Bot, lang: str = "en"):
        self.bot  = bot
        self.lang = lang
        options   = [
            discord.SelectOption(
                label=label,
                description=_category_desc(lang, label),
                emoji=emoji,
            )
            for label, emoji in _CATEGORY_LIST
        ]
        super().__init__(
            placeholder=_ui(lang, "dropdown_placeholder"),
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        lang     = get_lang(interaction)
        category = self.values[0]
        cog_names = CATEGORY_COGS.get(category, [])

        if category == "General":
            content = _general_text(self.bot, lang)
            view    = _make_layout(self.bot, content, lang, include_dropdown=True, general_page=True)
            return await interaction.response.edit_message(view=view)

        page                      = 1
        commands_content, total_pages = await _commands_text(
            cog_names, self.bot, interaction, page
        )
        header = _category_header(lang, category)

        view = HelpPagination(
            bot=self.bot,
            category=category,
            cog_names=cog_names,
            lang=lang,
            ctx_or_interaction=interaction,
            page=page,
            total_pages=total_pages,
        )
        view.header_display.content   = header
        view.commands_display.content = commands_content

        await interaction.response.edit_message(view=view)


# ===================================================
#  PAGINATION VIEW
# ===================================================

class HelpPagination(discord.ui.LayoutView):
    """
    Paginated category view.

    Container:
      TextDisplay (header — persists across pages)
      TextDisplay (commands list — updates on page change)
      ActionRow   (Prev · Page X/Y · Next) — only if total_pages > 1
      Separator
      ActionRow   (HelpDropdown)
    """

    def __init__(
        self,
        bot: commands.Bot,
        category: str,
        cog_names: List[str],
        lang: str,
        ctx_or_interaction,
        page: int = 1,
        total_pages: int = 1,
    ):
        super().__init__(timeout=None)
        self.bot                = bot
        self.category           = category
        self.cog_names          = cog_names
        self.lang               = lang
        self.page               = page
        self.total_pages        = total_pages
        self.ctx_or_interaction = ctx_or_interaction

        self.header_display:   discord.ui.TextDisplay
        self.commands_display: discord.ui.TextDisplay
        self.prev_button:      discord.ui.Button | None = None
        self.next_button:      discord.ui.Button | None = None
        self.page_indicator:   discord.ui.Button | None = None

        self._build_layout()

    def _build_layout(self):
        container = discord.ui.Container()

        self.header_display = discord.ui.TextDisplay(content="")
        container.add_item(self.header_display)

        self.commands_display = discord.ui.TextDisplay(content="")
        container.add_item(self.commands_display)

        if self.total_pages > 1:
            row = discord.ui.ActionRow()

            self.prev_button = discord.ui.Button(
                label=_ui(self.lang, "btn_prev"),
                style=discord.ButtonStyle.secondary,
                disabled=(self.page <= 1),
            )
            self.prev_button.callback = self._prev_page
            row.add_item(self.prev_button)

            self.page_indicator = discord.ui.Button(
                label=_ui(self.lang, "btn_page", page=self.page, total=self.total_pages),
                style=discord.ButtonStyle.secondary,
                disabled=True,
            )
            row.add_item(self.page_indicator)

            self.next_button = discord.ui.Button(
                label=_ui(self.lang, "btn_next"),
                style=discord.ButtonStyle.secondary,
                disabled=(self.page >= self.total_pages),
            )
            self.next_button.callback = self._next_page
            row.add_item(self.next_button)

            container.add_item(row)

        container.add_item(
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)
        )
        container.add_item(discord.ui.ActionRow(HelpDropdown(self.bot, self.lang)))
        self.add_item(container)

    async def _update_content(self, interaction: discord.Interaction):
        lang = get_lang(interaction)
        commands_content, total_pages = await _commands_text(
            self.cog_names, self.bot, interaction, self.page
        )
        self.total_pages                = total_pages
        self.commands_display.content   = commands_content

        if self.total_pages > 1 and self.prev_button and self.next_button and self.page_indicator:
            self.prev_button.disabled    = self.page <= 1
            self.next_button.disabled    = self.page >= self.total_pages
            self.prev_button.label       = _ui(lang, "btn_prev")
            self.next_button.label       = _ui(lang, "btn_next")
            self.page_indicator.label    = _ui(lang, "btn_page", page=self.page, total=self.total_pages)

        await interaction.response.edit_message(view=self)

    async def _prev_page(self, interaction: discord.Interaction):
        if self.page > 1:
            self.page -= 1
        await self._update_content(interaction)

    async def _next_page(self, interaction: discord.Interaction):
        if self.page < self.total_pages:
            self.page += 1
        await self._update_content(interaction)


# ===================================================
#  LAYOUT BUILDER (GENERAL + DETAIL PAGES)
# ===================================================

def _make_layout(
    bot: commands.Bot,
    content_text: str,
    lang: str = "en",
    include_dropdown: bool = True,
    general_page: bool = False,
) -> discord.ui.LayoutView:
    view      = discord.ui.LayoutView()
    container = discord.ui.Container()

    if general_page:
        section = discord.ui.Section(
            discord.ui.TextDisplay(content=content_text),
            accessory=discord.ui.Thumbnail(bot.user.avatar.url),
        )
        container.add_item(section)
    else:
        container.add_item(discord.ui.TextDisplay(content=content_text))

    if include_dropdown:
        container.add_item(
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)
        )
        container.add_item(discord.ui.ActionRow(HelpDropdown(bot, lang)))

    view.add_item(container)
    return view


# ===================================================
#  HELP COG
# ===================================================

class HelpCog(commands.Cog):
    """Custom help system — fully trilingual (EN / DE / ES)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="help",
        description="Show the help menu",
        help="{ 'en': 'show the help menu 📘☕', 'de': 'zeige das Hilfemenü 📘☕', 'es': 'muestra el menú de ayuda 📘☕' }",
    )
    async def help(self, ctx: commands.Context, *, command_name: str = None):
        lang = get_lang(ctx)

        if command_name:
            cmd = self.bot.get_command(command_name)
            if not cmd:
                content = (
                    f"### {get_emoji('icon_cross')} {_ui(lang, 'cmd_not_found_title')}\n"
                    f"{_ui(lang, 'cmd_not_found_body', name=command_name)}"
                )
                view = _make_layout(self.bot, content, lang, include_dropdown=False)
                return await ctx.send(view=view)

            content = await _command_detail_text(self.bot, cmd, ctx)
            view    = _make_layout(self.bot, content, lang, include_dropdown=False)
            return await ctx.send(view=view)

        content = _general_text(self.bot, lang)
        view    = _make_layout(self.bot, content, lang, include_dropdown=True, general_page=True)
        await ctx.send(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
