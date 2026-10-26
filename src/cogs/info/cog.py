# info.py
# Fully rewritten to use the message dictionary for all text.
# Bilingual EN/DE, cv2 LayoutView responses.

import discord
from discord.ext import commands
import time
import platform
import psutil
import os
from config.emojis import get_emoji
from utils.i18n import make_msg
from utils.paginator import PaginatedView, paginate
from config import links
from utils.member_badges import boosting_badge_key, niko_badge_keys
from utils.image.economy_card import fetch_avatar_bytes
from utils.image.spotify_card import render_spotify_card

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

}


# The animated placeholder shown while the Spotify card renders. Generated by
# `scripts/generate_spotify_loading_card.py` and served from the public site,
# so the loading state costs no attachment and appears instantly.
SPOTIFY_LOADING_CARD_TYPES = frozenset({"nowplaying"})

# The Spotify placeholder shares the loading-cards folder with the economy and
# leveling sets, so it is a single file rather than its own directory.
SPOTIFY_LOADING_CARD_FILE = "spotify.gif"


def _spotify_loading_cards_base() -> str:
    """Origin that serves the generated Spotify loading card.

    ``PUBLIC_URL`` names the site a deployment is reachable on, so a beta
    instance loads its own copy of the GIF instead of production's. The
    canonical website is the fallback when the variable is unset or blank.
    """
    origin = os.environ.get("PUBLIC_URL", "").strip().rstrip("/")
    return f"{origin or links.WEBSITE}/assets/loading-cards"


def _spotify_loading_card_view(card_type: str) -> discord.ui.LayoutView:
    """A remote animated loading card for *card_type*."""
    card_type = str(card_type).lower()
    if card_type not in SPOTIFY_LOADING_CARD_TYPES:
        raise ValueError(f"Unknown Spotify loading card type: {card_type!r}")
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.MediaGallery(discord.MediaGalleryItem(
            media=f"{_spotify_loading_cards_base()}/{SPOTIFY_LOADING_CARD_FILE}",
        )),
        accent_colour=discord.Colour(0x1DB954),
    ))
    return view


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


# Niko badge key (utils.member_badges.NIKO_BADGE_ORDER) -> emoji name in
# config/emojis.py. Both lists are checked against each other in the tests, so a
# new role badge needs its PNG art and its emoji entry, nothing else.
_NIKO_BADGE_EMOJIS = {
    "niko_owner": "badge_owner",
    "niko_staff": "badge_staff",
    "niko_head_admin": "badge_head_admin",
    "niko_moderator": "badge_moderator",
    "niko_head_support": "badge_head_support",
    "niko_support": "badge_support",
    "niko_graphic_designer": "badge_graphic_designer",
    "niko_event_coordinator": "badge_event_coordinator",
    # Discord emoji names are capped at 32 characters, hence the short name.
    "niko_partnerships_promotions_lead": "badge_partnership_lead",
    "niko_partnership_manager": "badge_partnership_manager",
    "niko_supporter": "badge_supporter_role",
    "niko_bug_hunter": "badge_bug_hunter_role",
    "niko_partner": "badge_partner_role",
}


async def _get_badges(bot: commands.Bot, user_id: int) -> list[str]:
    """Return the Niko badge emojis earned by user_id, in display order.

    Which badges an account carries is decided in utils.member_badges, so this
    card and the website's profile popovers can never disagree. Members who are
    not in the support server still get every badge that does not need it.
    """
    try:
        keys = await niko_badge_keys(bot, user_id)
    except Exception:
        return []
    return [
        get_emoji(_NIKO_BADGE_EMOJIS[key])
        for key in keys
        if key in _NIKO_BADGE_EMOJIS
    ]


# The avatar panel's buttons carry the target's user id in their custom id, so
# they resolve the right person after a restart without any message state.
_AVATAR_SERVER_TEMPLATE = r"avatar:server:(?P<user_id>\d+)"
_AVATAR_BANNER_TEMPLATE = r"avatar:banner:(?P<user_id>\d+)"


def _avatar_image_view(title: str, image_url: str) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {title}"),
        discord.ui.MediaGallery(discord.MediaGalleryItem(media=image_url)),
    ))
    return view


async def _avatar_member(interaction: discord.Interaction, user_id: int):
    """Resolve the target as a member, wherever the interaction happens."""
    guild = interaction.guild
    if guild is not None:
        member = guild.get_member(user_id)
        if member is not None:
            return member
        try:
            return await guild.fetch_member(user_id)
        except discord.HTTPException:
            return None
    # DMs have no guild of their own, so fall back to a cached server avatar.
    fallback = None
    for shared in interaction.client.guilds:
        member = shared.get_member(user_id)
        if member is None:
            continue
        if member.guild_avatar:
            return member
        fallback = fallback or member
    return fallback


class _ServerAvatarButton(discord.ui.DynamicItem[discord.ui.Button], template=_AVATAR_SERVER_TEMPLATE):
    def __init__(self, user_id: int):
        super().__init__(discord.ui.Button(
            label="Server Avatar",
            style=discord.ButtonStyle.success,
            custom_id=f"avatar:server:{int(user_id)}",
        ))
        self.user_id = int(user_id)

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item, match, /):
        return cls(int(match["user_id"]))

    async def callback(self, interaction: discord.Interaction):
        member = await _avatar_member(interaction, self.user_id)
        if member is None:
            return await interaction.response.send_message(
                "This user is no longer in this server.", ephemeral=True
            )
        if not member.guild_avatar:
            return await interaction.response.send_message(
                "This user doesn't have a different server avatar.", ephemeral=True
            )
        await interaction.response.send(
            view=_avatar_image_view("Server Avatar", member.guild_avatar.url), ephemeral=True
        )


class _UserBannerButton(discord.ui.DynamicItem[discord.ui.Button], template=_AVATAR_BANNER_TEMPLATE):
    def __init__(self, user_id: int):
        super().__init__(discord.ui.Button(
            label="User Banner",
            style=discord.ButtonStyle.success,
            custom_id=f"avatar:banner:{int(user_id)}",
        ))
        self.user_id = int(user_id)

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item, match, /):
        return cls(int(match["user_id"]))

    async def callback(self, interaction: discord.Interaction):
        user = interaction.client.get_user(self.user_id)
        if user is None:
            try:
                user = await interaction.client.fetch_user(self.user_id)
            except discord.HTTPException:
                user = None
        if user is None:
            return await interaction.response.send_message(
                "I couldn't find that user anymore.", ephemeral=True
            )
        if not user.banner:
            return await interaction.response.send_message(
                "This user doesn't have a banner.", ephemeral=True
            )
        await interaction.response.send(
            view=_avatar_image_view("User Banner", user.banner.url), ephemeral=True
        )


class AvatarButtons(discord.ui.ActionRow):
    """Avatar panel controls, keyed to the user the panel is showing."""

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = int(user_id)
        self.add_item(_ServerAvatarButton(self.user_id))
        self.add_item(_UserBannerButton(self.user_id))


def register_avatar_persistent_views(bot) -> None:
    """Register both avatar custom-id patterns so the buttons keep responding
    after a restart for panels posted before it."""
    registry = discord.ui.LayoutView(timeout=None)
    registry.add_item(discord.ui.Container(discord.ui.ActionRow(
        _ServerAvatarButton(0),
        _UserBannerButton(0),
    )))
    bot.add_view(registry)


class InfoCog(commands.Cog):
    """Bilingual server and user info commands."""

    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot, "start_time"):
            self.bot.start_time = time.time()

    async def cog_load(self):
        register_avatar_persistent_views(self.bot)

    # -------------------------------
    # SERVER INFO
    # -------------------------------
    @commands.hybrid_command(
        name="serverinfo",
        aliases=["si", "server"],
        description="View server info",
        help="{ 'en': 'show server stats', 'de': 'zeigt server-infos', 'es': 'muestra la información del servidor' }"
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
        aliases=["ui", "user"],
        description="View user info",
        help="{ 'en': 'see user details', 'de': 'benutzer-infos anzeigen', 'es': 'mira los detalles del usuario' }"
    )
    async def userinfo(self, ctx, member: discord.Member = None):
        if ctx.interaction:
            await ctx.defer()

        target = member or ctx.author
        avatar_url = target.avatar.url if target.avatar else None

        # ── Status ────────────────────────────────────────────────────────
        is_streaming = any(isinstance(a, discord.Streaming) for a in target.activities)
        if is_streaming:
            status_emoji = get_emoji("status_streaming")
            status_text  = "Streaming"
        else:
            _status_map = {
                discord.Status.online:  ("status_online",  "Online"),
                discord.Status.idle:    ("status_idle",    "Idle"),
                discord.Status.dnd:     ("status_dnd",     "Do Not Disturb"),
                discord.Status.offline: ("status_offline", "Offline"),
            }
            sk, status_text = _status_map.get(target.status, ("status_offline", "Offline"))
            status_emoji = get_emoji(sk)

        # ── Discord badges ────────────────────────────────────────────────
        # One entry per badge art in src/assets/emojis; the flag names are tried
        # in order because discord.py renamed a few of them across versions.
        pf = target.public_flags
        _disc_flag_map = [
            (("staff",),                                      "staff_badge"),
            (("partner",),                                    "partner_badge"),
            (("hypesquad_events",),                           "hypesquad_events"),
            (("bug_hunter_level_1", "bug_hunter"),            "bug_hunter_badge"),
            (("hypesquad_bravery",),                          "hypesquad_bravery"),
            (("hypesquad_brilliance",),                       "hypesquad_briliance"),
            (("hypesquad_balance",),                          "hypesquad_balance"),
            (("early_supporter",),                            "early_supporter_badge"),
            (("bug_hunter_level_2",),                         "bug_hunter_gold_badge"),
            (("verified_bot_developer", "early_verified_developer"), "verified_developer_badge"),
            (("certified_moderator",),                        "certified_moderator_badge"),
            (("supports_commands",),                          "supports_commands_badge"),
            (("active_developer",),                           "active_developer_badge"),
        ]
        disc_badges = []
        seen_disc = set()
        for flags, ekey in _disc_flag_map:
            if ekey in seen_disc or not any(getattr(pf, flag, False) for flag in flags):
                continue
            seen_disc.add(ekey)
            disc_badges.append(get_emoji(ekey))
        # Discord draws the boosting badge last, for any active boost streak,
        # and every tier has its own artwork, so the streak picks the badge.
        boosting = boosting_badge_key(getattr(target, "premium_since", None))
        if boosting and boosting not in seen_disc:
            seen_disc.add(boosting)
            disc_badges.append(get_emoji(boosting))

        # ── Niko badges ───────────────────────────────────────────────────
        niko_badges = await _get_badges(self.bot, target.id)

        badges_section = ""
        if disc_badges:
            badges_section += f"\n**Discord Badges:** {' '.join(disc_badges)}"
        if niko_badges:
            badges_section += f"\n**Niko Badges:** {' '.join(niko_badges)}"

        # ── Server info ───────────────────────────────────────────────────
        joined = (
            f"<t:{int(target.joined_at.timestamp())}:f> "
            f"(<t:{int(target.joined_at.timestamp())}:R>)"
            if target.joined_at else "N/A"
        )

        sorted_members = sorted(
            [m for m in ctx.guild.members if m.joined_at],
            key=lambda m: m.joined_at,
        )
        join_pos = next(
            (i + 1 for i, m in enumerate(sorted_members) if m.id == target.id), "?"
        )

        roles = [r.mention for r in reversed(target.roles) if r.name != "@everyone"]
        role_display = " ".join(roles[:12])
        if len(roles) > 12:
            role_display += f" *+{len(roles) - 12} more*"

        nickname = f"`{target.nick}`" if target.nick else "*none*"

        boost_line = ""
        if target.premium_since:
            boost_line = (
                f"\n**Boosting Since:** "
                f"<t:{int(target.premium_since.timestamp())}:R>"
            )

        bot_tag = f" {get_emoji('bot')}" if target.bot else ""

        text = (
            f"## {target.display_name}{bot_tag}\n"
            f"{status_emoji} **{status_text}**  ·  `@{target.name}`\n"
            f"**User ID:** `{target.id}`\n"
            f"**Account Created:** <t:{int(target.created_at.timestamp())}:f>"
            f" (<t:{int(target.created_at.timestamp())}:R>)\n"
            f"\n"
            f"**Joined Server:** {joined}\n"
            f"**Join Position:** `#{join_pos}` of `{len(ctx.guild.members)}`\n"
            f"**Nickname:** {nickname}\n"
            f"**Top Role:** {target.top_role.mention}\n"
            f"**Roles ({len(roles)}):** {role_display if roles else '*none*'}"
            f"{boost_line}"
            f"{badges_section}"
        )
        await ctx.send(view=cv2_text(text, thumbnail_url=avatar_url), allowed_mentions=discord.AllowedMentions.none())

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
        avatar_url = target.avatar.url if target.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"
        # timeout=None keeps the buttons live for as long as the message exists;
        # they are resolved from their custom ids, so no state is kept here.
        view = discord.ui.LayoutView(timeout=None)
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {msg(ctx, 'avatar_title', user=target.display_name)}"
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=avatar_url
                )
            ),
            AvatarButtons(target.id)
        )
        view.add_item(container)
        await ctx.send(view=view)

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
        help="{ 'en': 'learn about Niko', 'de': 'über Niko', 'es': 'aprende sobre Niko' }"
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
                accessory=discord.ui.Thumbnail(avatar_url) if avatar_url else discord.ui.TextDisplay(content=" ")
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
                    url=links.WEBSITE
                ),
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
        help="{ 'en': 'meet Nikos creator', 'de': 'entwickler-infos', 'es': 'conoce al creador de Niko' }"
    )
    async def creator(self, ctx):
        creator = await self.bot.fetch_user(1052690741874401360)
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
                accessory=discord.ui.Thumbnail(avatar_url) if avatar_url else discord.ui.TextDisplay(content=" ")
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
                    url="https://soren.is-a.dev"),
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
        help="{ 'en': 'see role details', 'de': 'rollen-infos anzeigen', 'es': 'mira los detalles del rol' }"
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
        help="{ 'en': 'see the boost stats of this server', 'de': 'boost-infos anzeigen', 'es': 'mira las estadísticas de boost del servidor' }"
    )
    async def booststats(self, ctx):
        server = ctx.guild
        text = (
            f"### {get_emoji('boost')} {msg(ctx, 'booststats_title')}\n"
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

        # Show the card-shaped placeholder first, then edit it into the render
        # so a slow cover download never leaves a bare "thinking" state.
        if ctx.interaction:
            await ctx.interaction.response.defer()
        loading = _spotify_loading_card_view("nowplaying")
        message = await (
            ctx.interaction.edit_original_response(view=loading)
            if ctx.interaction
            else ctx.send(view=loading)
        )

        elapsed = None
        if spotify.start and spotify.end:
            elapsed = (discord.utils.utcnow() - spotify.start).total_seconds()

        cover_bytes = await fetch_avatar_bytes(spotify.album_cover_url, size=640)
        buf = await render_spotify_card(
            cover_bytes=cover_bytes,
            title=spotify.title,
            artist=spotify.artist,
            album=spotify.album,
            duration=spotify.duration.total_seconds(),
            elapsed=elapsed,
            footer=msg(ctx, "spotify_title", user=target.display_name),
        )

        track_url = (
            f"https://open.spotify.com/track/{spotify.track_id}"
            if spotify.track_id
            else "https://open.spotify.com"
        )

        container = discord.ui.Container(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(media="attachment://spotify.png")
            ),
            discord.ui.Separator(visible=True),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Open in Spotify",
                    style=discord.ButtonStyle.link,
                    emoji=get_emoji("spotify"),
                    url=track_url,
                )
            ),
            accent_colour=discord.Colour(0x1DB954),
        )

        view = discord.ui.LayoutView()
        view.add_item(container)
        await message.edit(
            view=view,
            attachments=[discord.File(buf, "spotify.png")],
        )

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
        try:
            cpu_usage = psutil.cpu_percent()
        except Exception:
            cpu_usage = "N/A"
        try:
            memory_usage = round(psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024), 2)
        except Exception:
            memory_usage = "N/A"

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
        try:
            ram = round(psutil.virtual_memory().total / (1024**3), 2)
        except Exception:
            ram = "N/A"

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
            return await ctx.send(f"{get_emoji('cross')} Bot is not sharded.")

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
            title=f"{get_emoji('host')} {msg(ctx, 'shardinfo_title')}\n-# {msg(ctx, 'shardinfo_total')}: {self.bot.shard_count}",
            pages=pages
        )
        await ctx.send(view=view)

    # -------------------------------
    # INVITE
    # -------------------------------
    @commands.hybrid_command(
        name="invite",
        description="Get Niko's invite link",
        help="{ 'en': 'get the Niko invite link', 'de': 'einladungslink für Niko', 'es': 'obtén el enlace de invitación de Niko' }"
    )
    async def invite(self, ctx):
        bot_user = self.bot.user
        invite_link = f"https://discord.com/oauth2/authorize?client_id={bot_user.id}&permissions=8&scope=bot%20applications.commands"
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('invite')} {msg(ctx, 'invite_title')}\n[{msg(ctx, 'invite_link')}]({invite_link})"
            )
        )
        view.add_item(container)
        await ctx.send(view=view)


async def setup(bot):
    await bot.add_cog(InfoCog(bot))
