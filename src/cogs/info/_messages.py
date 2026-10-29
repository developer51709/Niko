"""Info — shared message catalogue and the card builders every info command uses."""

import discord

from utils.i18n import make_msg

MESSAGES = {
    "normal": {
        "en": {
            "serverinfo_title": "Server Info",
            "serverinfo_name": "Server Name",
            "serverinfo_id": "Server ID",
            "serverinfo_members": "Members",
            "serverinfo_members_word": "members",
            "serverinfo_users": "User Count",
            "serverinfo_humans": "humans",
            "serverinfo_bots": "bots",
            "serverinfo_roles": "Roles",
            "serverinfo_created": "Created",
            "serverinfo_owner": "Owner",
            "serverinfo_online": "Online Now",
            "serverinfo_online_word": "online",
            "serverinfo_channels": "Channels",
            "serverinfo_text_channels": "text",
            "serverinfo_voice_channels": "voice",
            "serverinfo_categories": "categories",
            "serverinfo_emojis": "Emojis",
            "serverinfo_stickers": "Stickers",
            "serverinfo_verification": "Verification",
            "serverinfo_description": "Description",
            "serverinfo_features": "Features",
            "verification_none": "None",
            "verification_low": "Low",
            "verification_medium": "Medium",
            "verification_high": "High",
            "verification_highest": "Highest",

            "userinfo_title": "User Info",
            "userinfo_username": "Username",
            "userinfo_id": "User ID",
            "userinfo_created": "Account Created",
            "userinfo_joined": "Joined Server",
            "userinfo_position": "Join Position",
            "userinfo_nickname": "Nickname",
            "userinfo_toprole": "Top Role",
            "userinfo_roles": "Roles",
            "userinfo_boosting": "Boosting Since",
            "userinfo_permissions": "Key Permissions",
            "userinfo_discord_badges": "Discord Badges",
            "userinfo_niko_badges": "Niko Badges",

            "avatar_title": "{user}'s Avatar",

            "banner_title": "{user}'s Banner",
            "banner_none": "{user} does not have a banner.",

            "about_title": "About Niko",
            "about_desc": (
                "Niko is a warm, all-in-one Discord companion: moderation and AutoMod, music, "
                "leveling and economy, tickets, giveaways, social feeds, and an AI that remembers "
                "your server \u2014 with a full web dashboard for everything behind it."
            ),
            "about_dev": "Developer",
            "about_dev_unknown": "Unavailable",
            "about_lib": "Library",
            "about_servers": "Servers",
            "about_members": "Members",
            "about_commands": "Commands",
            "about_uptime": "Uptime",
            "about_footer": "Thanks for using Niko!",

            "creator_title": "Creator",
            "creator_desc": "Niko was created by **{creator}**.",
            "creator_tag": "Creator Tag",
            "creator_id": "User ID",
            "creator_project": "Project",
            "creator_unavailable": "Could not load the creator profile right now. Please try again in a moment.",

            "roleinfo_title": "Role Info",
            "roleinfo_name": "Role Name",
            "roleinfo_id": "Role ID",
            "roleinfo_color": "Role Color",
            "roleinfo_color_default": "Default",
            "roleinfo_position": "Position",
            "roleinfo_members_word": "members",
            "roleinfo_created": "Created",
            "roleinfo_mentionable": "Mentionable",
            "roleinfo_hoisted": "Hoisted",
            "roleinfo_managed": "Managed",
            "roleinfo_permissions": "Key Permissions",
            "roleinfo_permissions_none": "none",
            "roleinfo_yes": "Yes",
            "roleinfo_no": "No",
            "roleinfo_need_role": "Please specify a role! Example: `!roleinfo @Role`",

            "servericon_title": "Server Icon",

            "serverbanner_title": "Server Banner",
            "serverbanner_none": "This server does not have a banner.",

            "booststats_title": "Boost Stats",
            "booststats_count": "Boost Count",
            "booststats_tier": "Boost Tier",
            "booststats_boosters": "Boosters",

            "spotify_not_member": "I can only check Spotify activity for server members.",
            "spotify_not_listening": "{user} is not listening to Spotify.",
            "spotify_title": "{user} is listening to Spotify",
            "spotify_track": "Track",
            "spotify_artist": "Artist",
            "spotify_album": "Album",
            "spotify_duration": "Duration",
            "spotify_started": "Started",
            "spotify_ends": "Ends",
            "spotify_footer": "Spotify status updates in real time.",

            "debuginfo_title": "Debug Info",
            "debuginfo_uptime": "Uptime",
            "debuginfo_model": "AI Model",
            "debuginfo_commands": "Command Count",
            "debuginfo_ping": "Ping Latency",
            "debuginfo_cpu": "CPU Usage",
            "debuginfo_ram": "Memory Usage",

            "hostinfo_title": "Host Info",
            "hostinfo_hostname": "Hostname",
            "hostinfo_os": "OS",
            "hostinfo_cpu": "CPU",
            "hostinfo_ram": "RAM",
            "invite_title": "Invite Niko",
            "invite_link": "Click here to invite Niko to your server",

            "shardinfo_title": "Shard Information",
            "shardinfo_total": "Total Shards",
            "shardinfo_guild_count": "Guilds",
            "shardinfo_member_count": "Members",
            "shardinfo_latency": "Latency"
        },

        "de": {
            "serverinfo_title": "Server-Informationen",
            "serverinfo_name": "Servername",
            "serverinfo_id": "Server-ID",
            "serverinfo_members": "Mitglieder",
            "serverinfo_members_word": "Mitglieder",
            "serverinfo_users": "Benutzer",
            "serverinfo_humans": "Menschen",
            "serverinfo_bots": "Bots",
            "serverinfo_roles": "Rollen",
            "serverinfo_created": "Erstellt am",
            "serverinfo_owner": "Besitzer",
            "serverinfo_online": "Gerade online",
            "serverinfo_online_word": "online",
            "serverinfo_channels": "Kanäle",
            "serverinfo_text_channels": "Text",
            "serverinfo_voice_channels": "Sprache",
            "serverinfo_categories": "Kategorien",
            "serverinfo_emojis": "Emojis",
            "serverinfo_stickers": "Sticker",
            "serverinfo_verification": "Verifizierung",
            "serverinfo_description": "Beschreibung",
            "serverinfo_features": "Funktionen",
            "verification_none": "Keine",
            "verification_low": "Niedrig",
            "verification_medium": "Mittel",
            "verification_high": "Hoch",
            "verification_highest": "Höchste",

            "userinfo_title": "Benutzer-Informationen",
            "userinfo_username": "Benutzername",
            "userinfo_id": "Benutzer-ID",
            "userinfo_created": "Account erstellt",
            "userinfo_joined": "Beigetreten",
            "userinfo_position": "Beitrittsposition",
            "userinfo_nickname": "Spitzname",
            "userinfo_toprole": "Höchste Rolle",
            "userinfo_roles": "Rollen",
            "userinfo_boosting": "Boostet seit",
            "userinfo_permissions": "Wichtige Berechtigungen",
            "userinfo_discord_badges": "Discord-Abzeichen",
            "userinfo_niko_badges": "Niko-Abzeichen",

            "avatar_title": "{user}s Avatar",

            "banner_title": "{user}s Banner",
            "banner_none": "{user} hat kein Banner.",

            "about_title": "Über Niko",
            "about_desc": (
                "Niko ist ein warmer All-in-One-Begleiter für Discord: Moderation und AutoMod, "
                "Musik, Leveling und Wirtschaft, Tickets, Giveaways, Social-Feeds und eine KI, "
                "die sich an deinen Server erinnert \u2014 mit einem vollständigen Web-Dashboard "
                "für alles dahinter."
            ),
            "about_dev": "Entwickler",
            "about_dev_unknown": "Nicht verfügbar",
            "about_lib": "Bibliothek",
            "about_servers": "Server",
            "about_members": "Mitglieder",
            "about_commands": "Befehle",
            "about_uptime": "Laufzeit",
            "about_footer": "Danke, dass du Niko benutzt!",

            "creator_title": "Ersteller",
            "creator_desc": "Niko wurde von **{creator}** erstellt.",
            "creator_tag": "Ersteller-Tag",
            "creator_id": "Benutzer-ID",
            "creator_project": "Projekt",
            "creator_unavailable": "Das Ersteller-Profil konnte gerade nicht geladen werden. Bitte versuche es gleich noch einmal.",

            "roleinfo_title": "Rollen-Informationen",
            "roleinfo_name": "Rollenname",
            "roleinfo_id": "Rollen-ID",
            "roleinfo_color": "Farbe",
            "roleinfo_color_default": "Standard",
            "roleinfo_position": "Position",
            "roleinfo_members_word": "Mitglieder",
            "roleinfo_created": "Erstellt am",
            "roleinfo_mentionable": "Erwähnbar",
            "roleinfo_hoisted": "Separat angezeigt",
            "roleinfo_managed": "Verwaltet",
            "roleinfo_permissions": "Wichtige Berechtigungen",
            "roleinfo_permissions_none": "keine",
            "roleinfo_yes": "Ja",
            "roleinfo_no": "Nein",
            "roleinfo_need_role": "Bitte gib eine Rolle an! Beispiel: `!roleinfo @Rolle`",

            "servericon_title": "Server-Icon",

            "serverbanner_title": "Server-Banner",
            "serverbanner_none": "Dieser Server hat kein Banner.",

            "booststats_title": "Boost-Statistiken",
            "booststats_count": "Boosts",
            "booststats_tier": "Boost-Stufe",
            "booststats_boosters": "Booster",

            "spotify_not_member": "Ich kann Spotify-Aktivität nur für Server-Mitglieder prüfen.",
            "spotify_not_listening": "{user} hört gerade kein Spotify.",
            "spotify_title": "{user} hört Spotify",
            "spotify_track": "Titel",
            "spotify_artist": "Künstler",
            "spotify_album": "Album",
            "spotify_duration": "Dauer",
            "spotify_started": "Gestartet",
            "spotify_ends": "Endet",
            "spotify_footer": "Spotify-Status aktualisiert sich in Echtzeit.",

            "debuginfo_title": "Debug-Informationen",
            "debuginfo_uptime": "Laufzeit",
            "debuginfo_model": "KI-Modell",
            "debuginfo_commands": "Befehle",
            "debuginfo_ping": "Ping",
            "debuginfo_cpu": "CPU-Auslastung",
            "debuginfo_ram": "Speicherverbrauch",

            "hostinfo_title": "Host-Informationen",
            "hostinfo_hostname": "Hostname",
            "hostinfo_os": "Betriebssystem",
            "hostinfo_cpu": "CPU",
            "hostinfo_ram": "RAM",
            "invite_title": "Niko einladen",
            "invite_link": "Klicke hier, um Niko auf deinen Server einzuladen",

            "shardinfo_title": "Shard-Informationen",
            "shardinfo_total": "Gesamtshards",
            "shardinfo_guild_count": "Server",
            "shardinfo_member_count": "Mitglieder",
            "shardinfo_latency": "Latenz"
        },
        "es": {
            "serverinfo_title": "Información del Servidor",
            "serverinfo_name": "Nombre del Servidor",
            "serverinfo_id": "ID del Servidor",
            "serverinfo_members": "Miembros",
            "serverinfo_members_word": "miembros",
            "serverinfo_users": "Cantidad de Usuarios",
            "serverinfo_humans": "humanos",
            "serverinfo_bots": "bots",
            "serverinfo_roles": "Roles",
            "serverinfo_created": "Creado",
            "serverinfo_owner": "Dueño",
            "serverinfo_online": "En Línea Ahora",
            "serverinfo_online_word": "en línea",
            "serverinfo_channels": "Canales",
            "serverinfo_text_channels": "texto",
            "serverinfo_voice_channels": "voz",
            "serverinfo_categories": "categorías",
            "serverinfo_emojis": "Emojis",
            "serverinfo_stickers": "Stickers",
            "serverinfo_verification": "Verificación",
            "serverinfo_description": "Descripción",
            "serverinfo_features": "Funciones",
            "verification_none": "Ninguna",
            "verification_low": "Baja",
            "verification_medium": "Media",
            "verification_high": "Alta",
            "verification_highest": "Máxima",

            "userinfo_title": "Información del Usuario",
            "userinfo_username": "Nombre de Usuario",
            "userinfo_id": "ID de Usuario",
            "userinfo_created": "Cuenta Creada",
            "userinfo_joined": "Se Unió al Servidor",
            "userinfo_position": "Posición de Ingreso",
            "userinfo_nickname": "Apodo",
            "userinfo_toprole": "Rol Más Alto",
            "userinfo_roles": "Roles",
            "userinfo_boosting": "Impulsando Desde",
            "userinfo_permissions": "Permisos Clave",
            "userinfo_discord_badges": "Insignias de Discord",
            "userinfo_niko_badges": "Insignias de Niko",

            "avatar_title": "Avatar de {user}",

            "banner_title": "Banner de {user}",
            "banner_none": "{user} no tiene banner.",

            "about_title": "Acerca de Niko",
            "about_desc": (
                "Niko es un compañero cálido y todo-en-uno para Discord: moderación y AutoMod, "
                "música, nivelación y economía, tickets, sorteos, redes sociales y una IA que "
                "recuerda tu servidor \u2014 con un panel web completo para todo lo demás."
            ),
            "about_dev": "Desarrollador",
            "about_dev_unknown": "No disponible",
            "about_lib": "Librería",
            "about_servers": "Servidores",
            "about_members": "Miembros",
            "about_commands": "Comandos",
            "about_uptime": "Tiempo activo",
            "about_footer": "¡Gracias por usar a Niko!",

            "creator_title": "Creador",
            "creator_desc": "Niko fue creado por **{creator}**.",
            "creator_tag": "Tag del Creador",
            "creator_id": "ID de Usuario",
            "creator_project": "Proyecto",
            "creator_unavailable": "No se pudo cargar el perfil del creador ahora mismo. Inténtalo de nuevo en un momento.",

            "roleinfo_title": "Información del Rol",
            "roleinfo_name": "Nombre del Rol",
            "roleinfo_id": "ID del Rol",
            "roleinfo_color": "Color",
            "roleinfo_color_default": "Predeterminado",
            "roleinfo_position": "Posición",
            "roleinfo_members_word": "miembros",
            "roleinfo_created": "Creado",
            "roleinfo_mentionable": "Mencionable",
            "roleinfo_hoisted": "Mostrado Aparte",
            "roleinfo_managed": "Gestionado",
            "roleinfo_permissions": "Permisos Clave",
            "roleinfo_permissions_none": "ninguno",
            "roleinfo_yes": "Sí",
            "roleinfo_no": "No",
            "roleinfo_need_role": "¡Por favor especifica un rol! Ejemplo: `!roleinfo @Rol`",

            "servericon_title": "Icono del Servidor",

            "serverbanner_title": "Banner del Servidor",
            "serverbanner_none": "Este servidor no tiene banner.",

            "booststats_title": "Estadísticas de Boost",
            "booststats_count": "Cantidad de Boosts",
            "booststats_tier": "Nivel de Boost",
            "booststats_boosters": "Boosters",

            "spotify_not_member": "Solo puedo ver la actividad de Spotify de los miembros del servidor.",
            "spotify_not_listening": "{user} no está escuchando Spotify.",
            "spotify_title": "{user} está escuchando Spotify",
            "spotify_track": "Canción",
            "spotify_artist": "Artista",
            "spotify_album": "Álbum",
            "spotify_duration": "Duración",
            "spotify_started": "Empezó",
            "spotify_ends": "Termina",
            "spotify_footer": "El estado de Spotify se actualiza en tiempo real.",

            "debuginfo_title": "Información de Depuración",
            "debuginfo_uptime": "Tiempo Activo",
            "debuginfo_model": "Modelo de IA",
            "debuginfo_commands": "Cantidad de Comandos",
            "debuginfo_ping": "Latencia",
            "debuginfo_cpu": "Uso de CPU",
            "debuginfo_ram": "Uso de Memoria",

            "hostinfo_title": "Información del Host",
            "hostinfo_hostname": "Nombre del Host",
            "hostinfo_os": "SO",
            "hostinfo_cpu": "CPU",
            "hostinfo_ram": "RAM",
            "invite_title": "Invitar a Niko",
            "invite_link": "Haz clic aquí para invitar a Niko a tu servidor",

            "shardinfo_title": "Información de Shard",
            "shardinfo_total": "Shards Totales",
            "shardinfo_guild_count": "Servidores",
            "shardinfo_member_count": "Miembros",
            "shardinfo_latency": "Latencia"
        },
    },

}

msg = make_msg(MESSAGES)


# ===================================================
#  SHARED CARD HELPERS
# ===================================================

# The permissions worth naming on the user and role cards, in the order they
# read best. Anyone without them gets no permissions line at all, so an
# ordinary member or role does not carry a row of "none".
_KEY_PERMISSIONS = (
    "administrator",
    "manage_guild",
    "manage_roles",
    "manage_channels",
    "kick_members",
    "ban_members",
    "moderate_members",
    "manage_messages",
    "mention_everyone",
)


def key_permission_names(permissions) -> list[str]:
    """The notable permission names held by a member's or a role's permissions.

    Administrator implies every other permission, so it is the only name
    returned when it is set; otherwise the names come in display order.
    """
    if getattr(permissions, "administrator", False):
        return ["Administrator"]
    return [
        name.replace("_", " ").title()
        for name in _KEY_PERMISSIONS
        if getattr(permissions, name, False)
    ]


def cv2_text(text, thumbnail_url=None):
    """Build a LayoutView with a container. Optionally include a thumbnail accessory."""
    view = discord.ui.LayoutView()
    if thumbnail_url:
        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(content=text),
                accessory=discord.ui.Thumbnail(thumbnail_url)
            )
        )
    else:
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=text)
        )
    view.add_item(container)
    return view


def _divider() -> discord.ui.Separator:
    """The thin rule the info cards put between their blocks."""
    return discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)


def cv2_image(text, image_url):
    """Build a LayoutView with text container + MediaGallery image."""
    view = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(
            content=text
        )
    )
    if image_url:
        container.add_item(discord.ui.MediaGallery(
            discord.MediaGalleryItem(media=image_url)
        ))
    view.add_item(container)
    return view
