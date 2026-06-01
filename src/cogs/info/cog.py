# info.py
# Fully rewritten to use the message dictionary for all text.
# Bilingual EN/DE, personality-aware, cv2 LayoutView responses.

import discord
from discord.ext import commands
import time
import platform
import psutil
import os
from config.emojis import get_emoji
from utils.ai.config import get_personality
from utils.i18n import make_msg
from config import links

MESSAGES = {
    "normal": {
        "en": {
            "serverinfo_title": "Server Info",
            "serverinfo_name": "Server Name",
            "serverinfo_id": "Server ID",
            "serverinfo_members": "Member Count",
            "serverinfo_users": "User Count",
            "serverinfo_bots": "Bot Count",
            "serverinfo_roles": "Role Count",
            "serverinfo_created": "Server Created",
            "serverinfo_owner": "Server Owner",

            "userinfo_title": "User Info",
            "userinfo_username": "Username",
            "userinfo_id": "User ID",
            "userinfo_created": "Account Created",
            "userinfo_joined": "Joined Server",
            "userinfo_toprole": "Top Role",
            "userinfo_roles": "Roles",

            "avatar_title": "{user}'s Avatar",

            "banner_title": "{user}'s Banner",
            "banner_none": "{user} does not have a banner.",

            "about_title": "About Niko",
            "about_desc": (
                "Niko is a friendly, playful, and very social AI designed to be an engaging "
                "companion in your Discord server. He loves chatting, helping out, and making "
                "your community feel more alive."
            ),
            "about_dev": "Developer",
            "about_lib": "Library",
            "about_servers": "Servers",
            "about_footer": "Thanks for using Niko!",

            "creator_title": "Creator",
            "creator_desc": "Niko was created by **{creator}**.",
            "creator_tag": "Creator Tag",
            "creator_id": "User ID",
            "creator_project": "Project",

            "roleinfo_title": "Role Info",
            "roleinfo_name": "Role Name",
            "roleinfo_id": "Role ID",
            "roleinfo_color": "Role Color",
            "roleinfo_position": "Role Position",
            "roleinfo_members": "Role Members",
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
            "serverinfo_users": "Benutzer",
            "serverinfo_bots": "Bots",
            "serverinfo_roles": "Rollen",
            "serverinfo_created": "Erstellt am",
            "serverinfo_owner": "Server-Besitzer",

            "userinfo_title": "Benutzer-Informationen",
            "userinfo_username": "Benutzername",
            "userinfo_id": "Benutzer-ID",
            "userinfo_created": "Account erstellt",
            "userinfo_joined": "Beigetreten",
            "userinfo_toprole": "Höchste Rolle",
            "userinfo_roles": "Rollen",

            "avatar_title": "{user}s Avatar",

            "banner_title": "{user}s Banner",
            "banner_none": "{user} hat kein Banner.",

            "about_title": "Über Niko",
            "about_desc": (
                "Niko ist ein freundlicher, verspielter und sehr sozialer KI-Begleiter, "
                "der deinen Discord-Server lebendiger macht."
            ),
            "about_dev": "Entwickler",
            "about_lib": "Bibliothek",
            "about_servers": "Server",
            "about_footer": "Danke, dass du Niko benutzt!",

            "creator_title": "Ersteller",
            "creator_desc": "Niko wurde von **{creator}** erstellt.",
            "creator_tag": "Ersteller-Tag",
            "creator_id": "Benutzer-ID",
            "creator_project": "Projekt",

            "roleinfo_title": "Rollen-Informationen",
            "roleinfo_name": "Rollenname",
            "roleinfo_id": "Rollen-ID",
            "roleinfo_color": "Farbe",
            "roleinfo_position": "Position",
            "roleinfo_members": "Mitglieder",
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
            "serverinfo_members": "Cantidad de Miembros",
            "serverinfo_users": "Cantidad de Usuarios",
            "serverinfo_bots": "Cantidad de Bots",
            "serverinfo_roles": "Cantidad de Roles",
            "serverinfo_created": "Servidor Creado",
            "serverinfo_owner": "Dueño del Servidor",

            "userinfo_title": "Información del Usuario",
            "userinfo_username": "Nombre de Usuario",
            "userinfo_id": "ID de Usuario",
            "userinfo_created": "Cuenta Creada",
            "userinfo_joined": "Se Unió al Servidor",
            "userinfo_toprole": "Rol Más Alto",
            "userinfo_roles": "Roles",

            "avatar_title": "Avatar de {user}",

            "banner_title": "Banner de {user}",
            "banner_none": "{user} no tiene banner.",

            "about_title": "Acerca de Niko",
            "about_desc": (
                "Niko es una IA amigable, juguetona y muy social diseñada para ser un compañero "
                "entretenido en tu servidor de Discord. Le encanta charlar, ayudar y hacer que "
                "tu comunidad se sienta más viva."
            ),
            "about_dev": "Desarrollador",
            "about_lib": "Librería",
            "about_servers": "Servidores",
            "about_footer": "¡Gracias por usar a Niko!",

            "creator_title": "Creador",
            "creator_desc": "Niko fue creado por **{creator}**.",
            "creator_tag": "Tag del Creador",
            "creator_id": "ID de Usuario",
            "creator_project": "Proyecto",

            "roleinfo_title": "Información del Rol",
            "roleinfo_name": "Nombre del Rol",
            "roleinfo_id": "ID del Rol",
            "roleinfo_color": "Color del Rol",
            "roleinfo_position": "Posición del Rol",
            "roleinfo_members": "Miembros con el Rol",
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

    "cafe": {
        "en": {
            "serverinfo_title": "☕ cozy server info",
            "serverinfo_name": "server name",
            "serverinfo_id": "server id",
            "serverinfo_members": "members",
            "serverinfo_users": "humans",
            "serverinfo_bots": "bots",
            "serverinfo_roles": "roles",
            "serverinfo_created": "born on",
            "serverinfo_owner": "server barista",

            "userinfo_title": "☕ cozy user info",
            "userinfo_username": "username",
            "userinfo_id": "user id",
            "userinfo_created": "account brewed on",
            "userinfo_joined": "joined café",
            "userinfo_toprole": "fanciest role",
            "userinfo_roles": "roles",

            "avatar_title": "{user}'s cute lil avatar ☕",

            "banner_title": "{user}'s banner ✨️",
            "banner_none": "{user} doesn't have a banner yet 😔",

            "about_title": "☕ about niko",
            "about_desc": (
                "Niko is your cozy café companion — warm, social, and always ready to chat "
                "or help out around the server."
            ),
            "about_dev": "barista",
            "about_lib": "library",
            "about_servers": "cafés",
            "about_footer": "thanks for hanging out with niko ☕",

            "creator_title": "☕ niko's creator",
            "creator_desc": "niko was lovingly brewed by **{creator}** ☕",
            "creator_tag": "creator tag",
            "creator_id": "user id",
            "creator_project": "project",

            "roleinfo_title": "☕ cozy role info",
            "roleinfo_name": "role name",
            "roleinfo_id": "role id",
            "roleinfo_color": "role color",
            "roleinfo_position": "role position",
            "roleinfo_members": "members with this vibe",
            "roleinfo_need_role": "pls specify a role cutie ☕ example: `!roleinfo @Role`",

            "servericon_title": "☕ server icon",

            "serverbanner_title": "☕ server banner",
            "serverbanner_none": "aww this café doesn't have a banner yet ☕",

            "booststats_title": "boost vibes",
            "booststats_count": "boost count",
            "booststats_tier": "boost tier",
            "booststats_boosters": "boosters",

            "spotify_not_member": "i can only check spotify for café members ☕",
            "spotify_not_listening": "{user} isn't vibing to spotify right now ☕",
            "spotify_title": "{user} is vibing to spotify ☕",
            "spotify_track": "track",
            "spotify_artist": "artist",
            "spotify_album": "album",
            "spotify_duration": "duration",
            "spotify_started": "started",
            "spotify_ends": "ends",
            "spotify_footer": "spotify vibes update in real time ☕",

            "debuginfo_title": "☕ debug vibes",
            "debuginfo_uptime": "uptime",
            "debuginfo_model": "ai model",
            "debuginfo_commands": "commands",
            "debuginfo_ping": "latency",
            "debuginfo_cpu": "cpu usage",
            "debuginfo_ram": "memory usage",

            "hostinfo_title": "☕ host info",
            "hostinfo_hostname": "hostname",
            "hostinfo_os": "os",
            "hostinfo_cpu": "cpu",
            "hostinfo_ram": "ram",
            "invite_title": "invite niko",
            "invite_link": "click here to invite niko to your café",

            "shardinfo_title": "☕ shard vibes",
            "shardinfo_total": "total shards",
            "shardinfo_guild_count": "cafés",
            "shardinfo_member_count": "cozy folks",
            "shardinfo_latency": "latency"
        },

        "de": {
            "serverinfo_title": "☕ gemütliche server-infos",
            "serverinfo_name": "servername",
            "serverinfo_id": "server-id",
            "serverinfo_members": "mitglieder",
            "serverinfo_users": "menschen",
            "serverinfo_bots": "bots",
            "serverinfo_roles": "rollen",
            "serverinfo_created": "geboren am",
            "serverinfo_owner": "server-barista",

            "userinfo_title": "☕ gemütliche benutzer-infos",
            "userinfo_username": "benutzername",
            "userinfo_id": "benutzer-id",
            "userinfo_created": "account aufgebrüht am",
            "userinfo_joined": "dem café beigetreten",
            "userinfo_toprole": "schickste rolle",
            "userinfo_roles": "rollen",

            "avatar_title": "{user}s süßer avatar ☕",

            "banner_title": "{user}s banner ✨️",
            "banner_none": "{user} hat noch kein banner 😔",

            "about_title": "☕ über niko",
            "about_desc": (
                "Niko ist dein gemütlicher café-begleiter — warm, sozial und immer bereit "
                "zu plaudern oder zu helfen."
            ),
            "about_dev": "barista",
            "about_lib": "bibliothek",
            "about_servers": "cafés",
            "about_footer": "danke fürs vorbeischauen ☕",

            "creator_title": "☕ nikos ersteller",
            "creator_desc": "niko wurde liebevoll von **{creator}** aufgebrüht ☕",
            "creator_tag": "ersteller-tag",
            "creator_id": "benutzer-id",
            "creator_project": "projekt",

            "roleinfo_title": "☕ gemütliche rollen-infos",
            "roleinfo_name": "rollenname",
            "roleinfo_id": "rollen-id",
            "roleinfo_color": "farbe",
            "roleinfo_position": "position",
            "roleinfo_members": "mitglieder mit diesem vibe",
            "roleinfo_need_role": "bitte gib eine rolle an ☕ beispiel: `!roleinfo @Rolle`",

            "servericon_title": "☕ server-icon",

            "serverbanner_title": "☕ server-banner",
            "serverbanner_none": "aww dieses café hat noch kein banner ☕",

            "booststats_title": "boost-vibes",
            "booststats_count": "boosts",
            "booststats_tier": "boost-stufe",
            "booststats_boosters": "booster",

            "spotify_not_member": "ich kann spotify nur für café-mitglieder prüfen ☕",
            "spotify_not_listening": "{user} hört gerade kein spotify ☕",
            "spotify_title": "{user} hört spotify ☕",
            "spotify_track": "titel",
            "spotify_artist": "künstler",
            "spotify_album": "album",
            "spotify_duration": "dauer",
            "spotify_started": "gestartet",
            "spotify_ends": "endet",
            "spotify_footer": "spotify-vibes aktualisieren sich in echtzeit ☕",

            "debuginfo_title": "☕ debug-infos",
            "debuginfo_uptime": "laufzeit",
            "debuginfo_model": "ki-modell",
            "debuginfo_commands": "befehle",
            "debuginfo_ping": "latenz",
            "debuginfo_cpu": "cpu-auslastung",
            "debuginfo_ram": "speicherverbrauch",

            "hostinfo_title": "☕ host-infos",
            "hostinfo_hostname": "hostname",
            "hostinfo_os": "betriebssystem",
            "hostinfo_cpu": "cpu",
            "hostinfo_ram": "ram",
            "invite_title": "niko einladen",
            "invite_link": "klicke hier, um niko in dein café einzuladen",

            "shardinfo_title": "☕ shard-gefühle",
            "shardinfo_total": "gesamt-shards",
            "shardinfo_guild_count": "cafés",
            "shardinfo_member_count": "gemütliche leute",
            "shardinfo_latency": "latenz"
        },
    },
}


msg = make_msg(MESSAGES)


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


class InfoCog(commands.Cog):
    """Cozy bilingual info commands with personality support."""

    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot, "start_time"):
            self.bot.start_time = time.time()

    # -------------------------------
    # SERVER INFO
    # -------------------------------
    @commands.hybrid_command(
        name="serverinfo",
        aliases=["si", "server"],
        description="View server info",
        help="{ 'en': 'peek at cozy server stats ☕', 'de': 'zeigt server-infos', 'es': 'mira info del servidor ☕' }"
    )
    async def serverinfo(self, ctx):
        server = ctx.guild
        icon_url = server.icon.url if server.icon else None
        humans = len([m for m in server.members if not m.bot])
        bots = len([m for m in server.members if m.bot])

        text = (
            f"### {msg(ctx, 'serverinfo_title')}\n"
            f"**{msg(ctx, 'serverinfo_name')}:** {server.name}\n"
            f"**{msg(ctx, 'serverinfo_id')}:** `{server.id}`\n"
            f"**{msg(ctx, 'serverinfo_members')}:** `{server.member_count}`\n"
            f"**{msg(ctx, 'serverinfo_users')}:** `{humans}`\n"
            f"**{msg(ctx, 'serverinfo_bots')}:** `{bots}`\n"
            f"**{msg(ctx, 'serverinfo_roles')}:** `{len(server.roles)}`\n"
            f"**{msg(ctx, 'serverinfo_created')}:** <t:{int(server.created_at.timestamp())}:f> (<t:{int(server.created_at.timestamp())}:R>)\n"
            f"**{msg(ctx, 'serverinfo_owner')}:** {server.owner}"
        )
        await ctx.send(view=cv2_text(text, thumbnail_url=icon_url))

    # -------------------------------
    # USER INFO
    # -------------------------------
    @commands.hybrid_command(
        name="userinfo",
        description="View user info",
        help="{ 'en': 'see cute lil user details ☕', 'de': 'benutzer-infos anzeigen', 'es': 'mira detalles del usuario ☕' }"
    )
    async def userinfo(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        avatar_url = target.avatar.url if target.avatar else None

        roles = [r.name for r in target.roles if r.name != "@everyone"]
        joined = f"<t:{int(target.joined_at.timestamp())}:f> (<t:{int(target.joined_at.timestamp())}:R>)" if target.joined_at else "`N/A`"

        text = (
            f"### {msg(ctx, 'userinfo_title')}\n"
            f"**{msg(ctx, 'userinfo_username')}:** `{target.display_name}`\n"
            f"**{msg(ctx, 'userinfo_id')}:** `{target.id}`\n"
            f"**{msg(ctx, 'userinfo_created')}:** <t:{int(target.created_at.timestamp())}:f> (<t:{int(target.created_at.timestamp())}:R>)\n"
            f"**{msg(ctx, 'userinfo_joined')}:** {joined}\n"
            f"**{msg(ctx, 'userinfo_toprole')}:** `{target.top_role.name}`\n"
            f"**{msg(ctx, 'userinfo_roles')}:** `{', '.join(roles) if roles else 'None'}`"
        )
        await ctx.send(view=cv2_text(text, thumbnail_url=avatar_url))

    # -------------------------------
    # AVATAR
    # -------------------------------
    @commands.hybrid_command(
        name="avatar",
        description="View someone's avatar",
        help="{ 'en': 'peek at someones cute avatar 👤', 'de': 'avatar anzeigen', 'es': 'mira el avatar de alguien 👤' }"
    )
    async def avatar(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        avatar_url = target.avatar.url if target.avatar else None
        text = f"### {msg(ctx, 'avatar_title', user=target.display_name)}"
        await ctx.send(view=cv2_image(text, image_url=avatar_url))

    # -------------------------------
    # BANNER
    # -------------------------------
    @commands.hybrid_command(
        name="banner",
        description="View someone's banner",
        help="{ 'en': 'see someones banner 🖼', 'de': 'banner anzeigen', 'es': 'mira el banner de alguien 🖼' }"
    )
    async def banner(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        target = await self.bot.fetch_user(target.id)
        banner_url = target.banner.url if target.banner else None
        if not banner_url:
            return await ctx.send(msg(ctx, "banner_none", user=target.display_name))
        text = f"### {msg(ctx, 'banner_title', user=target.display_name)}"
        await ctx.send(view=cv2_image(text, image_url=banner_url))

    # -------------------------------
    # ABOUT
    # -------------------------------
    @commands.hybrid_command(
        name="about",
        description="Learn about Niko",
        help="{ 'en': 'learn about Niko ☕', 'de': 'über Niko', 'es': 'aprende sobre Niko ☕' }"
    )
    async def about(self, ctx):
        bot_user = self.bot.user
        avatar_url = bot_user.avatar.url if bot_user.avatar else None

        text = (
            f"### {msg(ctx, 'about_title')}\n"
            f"{msg(ctx, 'about_desc')}\n\n"
            f"**{msg(ctx, 'about_dev')}:** Nyxen\n"
            f"**{msg(ctx, 'about_lib')}:** discord.py\n"
            f"**{msg(ctx, 'about_servers')}:** {len(self.bot.guilds)}\n\n"
            f"-# {msg(ctx, 'about_footer')}"
        )

        invite_url = f"https://discord.com/oauth2/authorize?client_id={bot_user.id}&permissions=8&scope=bot%20applications.commands"
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(content=text),
                accessory=discord.ui.Thumbnail(avatar_url) if avatar_url else discord.ui.TextDisplay(content="")
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Invite Niko", 
                    style=discord.ButtonStyle.link, 
                    emoji=get_emoji("discord"), 
                    url=invite_url
                ),
                discord.ui.Button(
                    label="GitHub", 
                    style=discord.ButtonStyle.link, 
                    emoji=get_emoji("github"), 
                    url=links.GITHUB
                ),
                discord.ui.Button(
                    label="Website", 
                    style=discord.ButtonStyle.link, 
                    emoji=get_emoji("website"),
                    url=links.WEBSITE),
            ),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="ToS", 
                    style=discord.ButtonStyle.link, 
                    url=links.TOS
                ),
                discord.ui.Button(
                    label="Privacy Policy", 
                    style=discord.ButtonStyle.link, 
                    url=links.PRIVACY
                ),
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    # -------------------------------
    # CREATOR
    # -------------------------------
    @commands.hybrid_command(
        name="creator",
        description="Meet Niko's creator",
        help="{ 'en': 'meet Nikos creator ☕', 'de': 'entwickler-infos', 'es': 'conoce al creador de Niko ☕' }"
    )
    async def creator(self, ctx):
        creator = await self.bot.fetch_user(1479968201319125013)
        bot_user = self.bot.user
        avatar_url = creator.avatar.url if creator.avatar else None

        text = (
            f"### {msg(ctx, 'creator_title')}\n"
            f"{msg(ctx, 'creator_desc', creator=creator.display_name)}\n\n"
            f"**{msg(ctx, 'creator_tag')}:** {creator}\n"
            f"**{msg(ctx, 'creator_id')}:** `{creator.id}`\n"
            f"**{msg(ctx, 'creator_project')}:** Niko All-In-One Discord Bot"
        )

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(content=text),
                accessory=discord.ui.Thumbnail(avatar_url) if avatar_url else discord.ui.TextDisplay(content="")
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Discord Profile", 
                    style=discord.ButtonStyle.link, 
                    emoji=get_emoji("discord"), 
                    url=f"https://discord.com/users/{creator.id}"
                ),
                discord.ui.Button(
                    label="GitHub", 
                    style=discord.ButtonStyle.link, 
                    emoji=get_emoji("github"), 
                    url="https://github.com/developer51709"
                ),
                discord.ui.Button(
                    label="Website", 
                    style=discord.ButtonStyle.link, 
                    emoji=get_emoji("website"), 
                    url="https://nyxen.is-a.dev"),
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    # -------------------------------
    # ROLE INFO
    # -------------------------------
    @commands.hybrid_command(
        name="roleinfo",
        description="View role info",
        help="{ 'en': 'see cozy role details ☕', 'de': 'rollen-infos anzeigen', 'es': 'mira detalles del rol ☕' }"
    )
    async def roleinfo(self, ctx, role: discord.Role = None):
        if role is None:
            return await ctx.send(msg(ctx, "roleinfo_need_role"))

        text = (
            f"### {msg(ctx, 'roleinfo_title')}\n"
            f"**{msg(ctx, 'roleinfo_name')}:** `{role.name}`\n"
            f"**{msg(ctx, 'roleinfo_id')}:** `{role.id}`\n"
            f"**{msg(ctx, 'roleinfo_color')}:** `{role.color}`\n"
            f"**{msg(ctx, 'roleinfo_position')}:** `{role.position}`\n"
            f"**{msg(ctx, 'roleinfo_members')}:** `{len(role.members)}`"
        )
        await ctx.send(view=cv2_text(text))

    # -------------------------------
    # SERVER ICON
    # -------------------------------
    @commands.hybrid_command(
        name="servericon",
        description="Show the server's icon",
        help="{ 'en': 'show the servers cute icon 📍', 'de': 'server-icon anzeigen', 'es': 'muestra el icono del servidor 📍' }"
    )
    async def servericon(self, ctx):
        server = ctx.guild
        icon_url = server.icon.url if server.icon else None
        text = f"### {msg(ctx, 'servericon_title')}"
        await ctx.send(view=cv2_image(text, image_url=icon_url))

    # -------------------------------
    # SERVER BANNER
    # -------------------------------
    @commands.hybrid_command(
        name="serverbanner",
        description="Show the server's banner",
        help="{ 'en': 'show the servers banner 🖼', 'de': 'server-banner anzeigen', 'es': 'muestra el banner del servidor 🖼' }"
    )
    async def serverbanner(self, ctx):
        server = ctx.guild
        if not server.banner:
            return await ctx.send(msg(ctx, "serverbanner_none"))
        text = f"### {msg(ctx, 'serverbanner_title')}"
        await ctx.send(view=cv2_image(text, image_url=server.banner.url))

    # -------------------------------
    # BOOST STATS
    # -------------------------------
    @commands.hybrid_command(
        name="booststats",
        description="View the server's boost stats",
        help="{ 'en': 'see the servers boost vibes ☕', 'de': 'boost-infos anzeigen', 'es': 'mira las estadísticas de boost del servidor ☕' }"
    )
    async def booststats(self, ctx):
        server = ctx.guild
        text = (
            f"### {get_emoji('icon_boost')} {msg(ctx, 'booststats_title')}\n"
            f"**{msg(ctx, 'booststats_count')}:** `{server.premium_subscription_count}`\n"
            f"**{msg(ctx, 'booststats_tier')}:** `{server.premium_tier}`\n"
            f"**{msg(ctx, 'booststats_boosters')}:** `{len(server.premium_subscribers)}`"
        )
        await ctx.send(view=cv2_text(text))

    # -------------------------------
    # SPOTIFY
    # -------------------------------
    @commands.hybrid_command(
        name="spotify",
        description="See what someone's listening to on Spotify",
        help="{ 'en': 'see what someone is vibing to on Spotify 🎧', 'de': 'spotify-infos anzeigen', 'es': 'mira qué escucha alguien en Spotify 🎧' }"
    )
    async def spotify(self, ctx, member: discord.Member = None):
        target = member or ctx.author

        if not isinstance(target, discord.Member):
            return await ctx.send(msg(ctx, "spotify_not_member"))

        activities = getattr(target, "activities", None)
        if not activities:
            return await ctx.send(msg(ctx, "spotify_not_listening", user=target.display_name))

        spotify = next((a for a in activities if isinstance(a, discord.Spotify)), None)
        if not spotify:
            return await ctx.send(msg(ctx, "spotify_not_listening", user=target.display_name))

        duration = spotify.duration.total_seconds()
        dur_str = f"{int(duration//60)}:{int(duration%60):02d}"

        time_fields = ""
        if spotify.start and spotify.end:
            time_fields = (
                f"**{msg(ctx, 'spotify_started')}:** <t:{int(spotify.start.timestamp())}:t>\n"
                f"**{msg(ctx, 'spotify_ends')}:** <t:{int(spotify.end.timestamp())}:t>\n"
            )

        text = (
            f"### {msg(ctx, 'spotify_title', user=target.display_name)}\n"
            f"**{msg(ctx, 'spotify_track')}:** {spotify.title}\n"
            f"**{msg(ctx, 'spotify_artist')}:** {spotify.artist}\n"
            f"**{msg(ctx, 'spotify_album')}:** {spotify.album}\n"
            f"**{msg(ctx, 'spotify_duration')}:** {dur_str}\n"
            f"{time_fields}"
            f"-# {msg(ctx, 'spotify_footer')}"
        )

        album_cover = spotify.album_cover_url
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(content=text),
                accessory=discord.ui.Thumbnail(album_cover) if album_cover else discord.ui.TextDisplay(content="")
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Open in Spotify",
                    style=discord.ButtonStyle.link,
                    emoji=get_emoji("spotify"),
                    url=f"https://open.spotify.com/track/{spotify.track_id}"
                )
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await ctx.send(view=view)

    # -------------------------------
    # DEBUG INFO
    # -------------------------------
    @commands.hybrid_command(
        name="debuginfo",
        description="View bot debug info",
        help="{ 'en': 'view debug info 👾', 'de': 'debug-infos anzeigen', 'es': 'mira info de depuración 👾' }"
    )
    async def debuginfo(self, ctx):
        uptime_seconds = int(time.time() - self.bot.start_time)
        uptime = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s"
        ai_model = os.getenv("AI_MODEL", "Unknown")
        command_count = len(self.bot.commands)
        ping_latency = round(self.bot.latency * 1000)
        cpu_usage = psutil.cpu_percent()
        memory_usage = round(psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024), 2)

        text = (
            f"### {msg(ctx, 'debuginfo_title')}\n"
            f"**{msg(ctx, 'debuginfo_uptime')}:** `{uptime}`\n"
            f"**{msg(ctx, 'debuginfo_model')}:** `{ai_model}`\n"
            f"**{msg(ctx, 'debuginfo_commands')}:** `{command_count}`\n"
            f"**{msg(ctx, 'debuginfo_ping')}:** `{ping_latency}ms`\n"
            f"{get_emoji('cpu')} **{msg(ctx, 'debuginfo_cpu')}:** `{cpu_usage}%`\n"
            f"{get_emoji('ram')} **{msg(ctx, 'debuginfo_ram')}:** `{memory_usage}MB`"
        )
        await ctx.send(view=cv2_text(text))

    # -------------------------------
    # HOST INFO
    # -------------------------------
    @commands.hybrid_command(
        name="hostinfo",
        description="View bot host info",
        help="{ 'en': 'view host info 💻', 'de': 'host-infos anzeigen', 'es': 'mira info del host 💻' }"
    )
    async def hostinfo(self, ctx):
        hostname = platform.node()
        os_info = f"{platform.system()} {platform.release()}"
        cpu = platform.processor() or "N/A"
        ram = round(psutil.virtual_memory().total / (1024**3), 2)

        text = (
            f"### {msg(ctx, 'hostinfo_title')}\n"
            f"**{msg(ctx, 'hostinfo_hostname')}:** `{hostname}`\n"
            f"**{msg(ctx, 'hostinfo_os')}:** `{os_info}`\n"
            f"{get_emoji('cpu')} **{msg(ctx, 'hostinfo_cpu')}:** `{cpu}`\n"
            f"{get_emoji('ram')} **{msg(ctx, 'hostinfo_ram')}:** `{ram}GB`"
        )
        await ctx.send(view=cv2_text(text))

    # -------------------------------
    # SHARDS
    # -------------------------------
    @commands.hybrid_command(
        name="shards",
        description="View information about the bot's shards",
        help="{ 'en': 'view bot shard information', 'de': 'shard-informationen ansehen', 'es': 'ver información de shards' }"
    )
    async def shards_command(self, ctx):
        """Display current shard information."""
        if not self.bot.shards:
            return await ctx.send(f"{get_emoji('icon_cross')} Bot is not sharded.")

        shard_guilds = {}
        shard_members = {}
        total_guilds = 0
        total_members = 0

        # Count guilds and members per shard
        for guild in self.bot.guilds:
            shard_id = guild.shard_id or 0
            shard_guilds[shard_id] = shard_guilds.get(shard_id, 0) + 1
            total_guilds += 1
            if guild.member_count:
                shard_members[shard_id] = shard_members.get(shard_id, 0) + guild.member_count
                total_members += guild.member_count

        lines = []
        for shard_id in range(self.bot.shard_count):
            guild_count = shard_guilds.get(shard_id, 0)
            member_count = shard_members.get(shard_id, 0)
            shard = self.bot.shards.get(shard_id)
            latency = f"{round(shard.latency * 1000)}ms" if shard else "N/A"
            lines.append(
                f"**Shard {shard_id}**\n"
                f"-# {msg(ctx, 'shardinfo_guild_count')}: {guild_count} · "
                f"{msg(ctx, 'shardinfo_member_count')}: {member_count:,} · "
                f"{msg(ctx, 'shardinfo_latency')}: {latency}"
            )

        pages = paginate(lines, per_page=8)
        view = PaginatedView(
            title=f"🔀 {msg(ctx, 'shardinfo_title')}\n-# {msg(ctx, 'shardinfo_total')}: {self.bot.shard_count}",
            pages=pages
        )
        await ctx.send(view=view)

    # -------------------------------
    # INVITE
    # -------------------------------
    @commands.hybrid_command(
        name="invite",
        description="Get Niko's invite link",
        help="{ 'en': 'get Nikos invite link ☕️', 'de': 'einladungslink für Niko', 'es': 'obtén el enlace de invitación de Niko ☕️' }"
    )
    async def invite(self, ctx):
        bot_user = self.bot.user
        invite_link = f"https://discord.com/oauth2/authorize?client_id={bot_user.id}&permissions=8&scope=bot%20applications.commands"
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_invite')} {msg(ctx, 'invite_title')}\n[{msg(ctx, 'invite_link')}]({invite_link})"
            )
        )
        view.add_item(container)
        await ctx.send(view=view)


async def setup(bot):
    await bot.add_cog(InfoCog(bot))
