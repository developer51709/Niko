# info.py
# Fully rewritten to use the message dictionary for all embed text.
# Bilingual EN/DE, personality-aware, clean and consistent with the other cogs.

import discord
from discord.ext import commands
from discord.ui import View, Button
import time
import platform
import psutil
import os

# personality mode: "normal" or "cafe"
PERSONALITY = "cafe"

MESSAGES = {
    "normal": {
        "en": {
            # SERVER INFO
            "serverinfo_title": "Server Info",
            "serverinfo_name": "Server Name",
            "serverinfo_id": "Server ID",
            "serverinfo_members": "Member Count",
            "serverinfo_users": "User Count",
            "serverinfo_bots": "Bot Count",
            "serverinfo_roles": "Role Count",
            "serverinfo_created": "Server Created",
            "serverinfo_owner": "Server Owner",

            # USER INFO
            "userinfo_title": "User Info",
            "userinfo_username": "Username",
            "userinfo_id": "User ID",
            "userinfo_created": "Account Created",
            "userinfo_joined": "Joined Server",
            "userinfo_toprole": "Top Role",
            "userinfo_roles": "Roles",

            # AVATAR
            "avatar_title": "{user}'s Avatar",

            # ABOUT
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

            # CREATOR
            "creator_title": "Creator",
            "creator_desc": "Niko was created by **{creator}**.",
            "creator_tag": "Creator Tag",
            "creator_id": "User ID",
            "creator_project": "Project",

            # ROLE INFO
            "roleinfo_title": "Role Info",
            "roleinfo_name": "Role Name",
            "roleinfo_id": "Role ID",
            "roleinfo_color": "Role Color",
            "roleinfo_position": "Role Position",
            "roleinfo_members": "Role Members",
            "roleinfo_need_role": "Please specify a role! Example: `!roleinfo @Role`",

            # SERVER ICON
            "servericon_title": "Server Icon",

            # SERVER BANNER
            "serverbanner_title": "Server Banner",
            "serverbanner_none": "This server does not have a banner.",

            # BOOST STATS
            "booststats_title": "Boost Stats",
            "booststats_count": "Boost Count",
            "booststats_tier": "Boost Tier",
            "booststats_boosters": "Boosters",

            # SPOTIFY
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

            # DEBUG INFO
            "debuginfo_title": "Debug Info",
            "debuginfo_uptime": "Uptime",
            "debuginfo_model": "AI Model",
            "debuginfo_commands": "Command Count",
            "debuginfo_ping": "Ping Latency",
            "debuginfo_cpu": "CPU Usage",
            "debuginfo_ram": "Memory Usage",

            # HOST INFO
            "hostinfo_title": "Host Info",
            "hostinfo_hostname": "Hostname",
            "hostinfo_os": "OS",
            "hostinfo_cpu": "CPU",
            "hostinfo_ram": "RAM",
        },

        "de": {
            # SERVER INFO
            "serverinfo_title": "Server‑Informationen",
            "serverinfo_name": "Servername",
            "serverinfo_id": "Server‑ID",
            "serverinfo_members": "Mitglieder",
            "serverinfo_users": "Benutzer",
            "serverinfo_bots": "Bots",
            "serverinfo_roles": "Rollen",
            "serverinfo_created": "Erstellt am",
            "serverinfo_owner": "Server‑Besitzer",

            # USER INFO
            "userinfo_title": "Benutzer‑Informationen",
            "userinfo_username": "Benutzername",
            "userinfo_id": "Benutzer‑ID",
            "userinfo_created": "Account erstellt",
            "userinfo_joined": "Beigetreten",
            "userinfo_toprole": "Höchste Rolle",
            "userinfo_roles": "Rollen",

            # AVATAR
            "avatar_title": "{user}s Avatar",

            # ABOUT
            "about_title": "Über Niko",
            "about_desc": (
                "Niko ist ein freundlicher, verspielter und sehr sozialer KI‑Begleiter, "
                "der deinen Discord‑Server lebendiger macht."
            ),
            "about_dev": "Entwickler",
            "about_lib": "Bibliothek",
            "about_servers": "Server",
            "about_footer": "Danke, dass du Niko benutzt!",

            # CREATOR
            "creator_title": "Ersteller",
            "creator_desc": "Niko wurde von **{creator}** erstellt.",
            "creator_tag": "Ersteller‑Tag",
            "creator_id": "Benutzer‑ID",
            "creator_project": "Projekt",

            # ROLE INFO
            "roleinfo_title": "Rollen‑Informationen",
            "roleinfo_name": "Rollenname",
            "roleinfo_id": "Rollen‑ID",
            "roleinfo_color": "Farbe",
            "roleinfo_position": "Position",
            "roleinfo_members": "Mitglieder",
            "roleinfo_need_role": "Bitte gib eine Rolle an! Beispiel: `!roleinfo @Rolle`",

            # SERVER ICON
            "servericon_title": "Server‑Icon",

            # SERVER BANNER
            "serverbanner_title": "Server‑Banner",
            "serverbanner_none": "Dieser Server hat kein Banner.",

            # BOOST STATS
            "booststats_title": "Boost‑Statistiken",
            "booststats_count": "Boosts",
            "booststats_tier": "Boost‑Stufe",
            "booststats_boosters": "Booster",

            # SPOTIFY
            "spotify_not_member": "Ich kann Spotify‑Aktivität nur für Server‑Mitglieder prüfen.",
            "spotify_not_listening": "{user} hört gerade kein Spotify.",
            "spotify_title": "{user} hört Spotify",
            "spotify_track": "Titel",
            "spotify_artist": "Künstler",
            "spotify_album": "Album",
            "spotify_duration": "Dauer",
            "spotify_started": "Gestartet",
            "spotify_ends": "Endet",
            "spotify_footer": "Spotify‑Status aktualisiert sich in Echtzeit.",

            # DEBUG INFO
            "debuginfo_title": "Debug‑Informationen",
            "debuginfo_uptime": "Laufzeit",
            "debuginfo_model": "KI‑Modell",
            "debuginfo_commands": "Befehle",
            "debuginfo_ping": "Ping",
            "debuginfo_cpu": "CPU‑Auslastung",
            "debuginfo_ram": "Speicherverbrauch",

            # HOST INFO
            "hostinfo_title": "Host‑Informationen",
            "hostinfo_hostname": "Hostname",
            "hostinfo_os": "Betriebssystem",
            "hostinfo_cpu": "CPU",
            "hostinfo_ram": "RAM",
        },
    },

    # -----------------------------
    # CAFE PERSONALITY
    # -----------------------------
    "cafe": {
        "en": {
            # SERVER INFO
            "serverinfo_title": "☕ cozy server info",
            "serverinfo_name": "server name",
            "serverinfo_id": "server id",
            "serverinfo_members": "members",
            "serverinfo_users": "humans",
            "serverinfo_bots": "bots",
            "serverinfo_roles": "roles",
            "serverinfo_created": "born on",
            "serverinfo_owner": "server barista",

            # USER INFO
            "userinfo_title": "☕ cozy user info",
            "userinfo_username": "username",
            "userinfo_id": "user id",
            "userinfo_created": "account brewed on",
            "userinfo_joined": "joined café",
            "userinfo_toprole": "fanciest role",
            "userinfo_roles": "roles",

            # AVATAR
            "avatar_title": "{user}'s cute lil avatar ☕",

            # ABOUT
            "about_title": "☕ about niko",
            "about_desc": (
                "Niko is your cozy café companion — warm, social, and always ready to chat "
                "or help out around the server."
            ),
            "about_dev": "barista",
            "about_lib": "library",
            "about_servers": "cafés",
            "about_footer": "thanks for hanging out with niko ☕",

            # CREATOR
            "creator_title": "☕ niko’s creator",
            "creator_desc": "niko was lovingly brewed by **{creator}** ☕",
            "creator_tag": "creator tag",
            "creator_id": "user id",
            "creator_project": "project",

            # ROLE INFO
            "roleinfo_title": "☕ cozy role info",
            "roleinfo_name": "role name",
            "roleinfo_id": "role id",
            "roleinfo_color": "role color",
            "roleinfo_position": "role position",
            "roleinfo_members": "members with this vibe",
            "roleinfo_need_role": "pls specify a role cutie ☕ example: `!roleinfo @Role`",

            # SERVER ICON
            "servericon_title": "☕ server icon",

            # SERVER BANNER
            "serverbanner_title": "☕ server banner",
            "serverbanner_none": "aww this café doesn’t have a banner yet ☕",

            # BOOST STATS
            "booststats_title": "☕ boost vibes",
            "booststats_count": "boost count",
            "booststats_tier": "boost tier",
            "booststats_boosters": "boosters",

            # SPOTIFY
            "spotify_not_member": "i can only check spotify for café members ☕",
            "spotify_not_listening": "{user} isn’t vibing to spotify right now ☕",
            "spotify_title": "{user} is vibing to spotify ☕",
            "spotify_track": "track",
            "spotify_artist": "artist",
            "spotify_album": "album",
            "spotify_duration": "duration",
            "spotify_started": "started",
            "spotify_ends": "ends",
            "spotify_footer": "spotify vibes update in real time ☕",

            # DEBUG INFO
            "debuginfo_title": "☕ debug vibes",
            "debuginfo_uptime": "uptime",
            "debuginfo_model": "ai model",
            "debuginfo_commands": "commands",
            "debuginfo_ping": "latency",
            "debuginfo_cpu": "cpu usage",
            "debuginfo_ram": "memory usage",

            # HOST INFO
            "hostinfo_title": "☕ host info",
            "hostinfo_hostname": "hostname",
            "hostinfo_os": "os",
            "hostinfo_cpu": "cpu",
            "hostinfo_ram": "ram",
        },

        "de": {
            # SERVER INFO
            "serverinfo_title": "☕ gemütliche server‑infos",
            "serverinfo_name": "servername",
            "serverinfo_id": "server‑id",
            "serverinfo_members": "mitglieder",
            "serverinfo_users": "menschen",
            "serverinfo_bots": "bots",
            "serverinfo_roles": "rollen",
            "serverinfo_created": "geboren am",
            "serverinfo_owner": "server‑barista",

            # USER INFO
            "userinfo_title": "☕ gemütliche benutzer‑infos",
            "userinfo_username": "benutzername",
            "userinfo_id": "benutzer‑id",
            "userinfo_created": "account aufgebrüht am",
            "userinfo_joined": "dem café beigetreten",
            "userinfo_toprole": "schickste rolle",
            "userinfo_roles": "rollen",

            # AVATAR
            "avatar_title": "{user}s süßer avatar ☕",

            # ABOUT
            "about_title": "☕ über niko",
            "about_desc": (
                "Niko ist dein gemütlicher café‑begleiter — warm, sozial und immer bereit "
                "zu plaudern oder zu helfen."
            ),
            "about_dev": "barista",
            "about_lib": "bibliothek",
            "about_servers": "cafés",
            "about_footer": "danke fürs vorbeischauen ☕",

            # CREATOR
            "creator_title": "☕ nikos ersteller",
            "creator_desc": "niko wurde liebevoll von **{creator}** aufgebrüht ☕",
            "creator_tag": "ersteller‑tag",
            "creator_id": "benutzer‑id",
            "creator_project": "projekt",

            # ROLE INFO
            "roleinfo_title": "☕ gemütliche rollen‑infos",
            "roleinfo_name": "rollenname",
            "roleinfo_id": "rollen‑id",
            "roleinfo_color": "farbe",
            "roleinfo_position": "position",
            "roleinfo_members": "mitglieder mit diesem vibe",
            "roleinfo_need_role": "bitte gib eine rolle an ☕ beispiel: `!roleinfo @Rolle`",

            # SERVER ICON
            "servericon_title": "☕ server‑icon",

            # SERVER BANNER
            "serverbanner_title": "☕ server‑banner",
            "serverbanner_none": "aww dieses café hat noch kein banner ☕",

            # BOOST STATS
            "booststats_title": "☕ boost‑vibes",
            "booststats_count": "boosts",
            "booststats_tier": "boost‑stufe",
            "booststats_boosters": "booster",

            # SPOTIFY
            "spotify_not_member": "ich kann spotify nur für café‑mitglieder prüfen ☕",
            "spotify_not_listening": "{user} hört gerade kein spotify ☕",
            "spotify_title": "{user} hört spotify ☕",
            "spotify_track": "titel",
            "spotify_artist": "künstler",
            "spotify_album": "album",
            "spotify_duration": "dauer",
            "spotify_started": "gestartet",
            "spotify_ends": "endet",
            "spotify_footer": "spotify‑vibes aktualisieren sich in echtzeit ☕",

            # DEBUG INFO
            "debuginfo_title": "☕ debug‑infos",
            "debuginfo_uptime": "laufzeit",
            "debuginfo_model": "ki‑modell",
            "debuginfo_commands": "befehle",
            "debuginfo_ping": "latenz",
            "debuginfo_cpu": "cpu‑auslastung",
            "debuginfo_ram": "speicherverbrauch",

            # HOST INFO
            "hostinfo_title": "☕ host‑infos",
            "hostinfo_hostname": "hostname",
            "hostinfo_os": "betriebssystem",
            "hostinfo_cpu": "cpu",
            "hostinfo_ram": "ram",
        },
    },
}

# -----------------------------------
# LANGUAGE + PERSONALITY HELPERS
# -----------------------------------
def get_lang(ctx):
    """Return 'en' or 'de' based on server locale."""
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"

def get_personality():
    return PERSONALITY if PERSONALITY in ("normal", "cafe") else "normal"

def msg(ctx, key, **kwargs):
    """Fetch a message from the dictionary with fallback logic."""
    personality = get_personality()
    lang = get_lang(ctx)

    # Try personality + lang
    block = MESSAGES.get(personality, {}).get(lang, {})
    text = block.get(key)

    # Fallback personality + EN
    if text is None:
        text = MESSAGES.get(personality, {}).get("en", {}).get(key)

    # Fallback normal + lang
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key)

    # Fallback normal + EN
    if text is None:
        text = MESSAGES["normal"]["en"].get(key, key)

    return text.format(**kwargs) if kwargs else text

def embed_color():
    """Consistent embed color based on personality."""
    return discord.Color.gold() if get_personality() == "cafe" else discord.Color.blue()


# -----------------------------------
# INFO COG
# -----------------------------------
class InfoCog(commands.Cog):
    """Cozy bilingual info commands with personality support."""

    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot, "start_time"):
            self.bot.start_time = time.time()

    # -------------------------------
    # SERVER INFO
    # -------------------------------
    @commands.command(
        name="serverinfo",
        help="peek at cozy server stats ☕ | zeigt server‑infos"
    )
    async def serverinfo(self, ctx):
        server = ctx.guild

        embed = discord.Embed(
            title=msg(ctx, "serverinfo_title"),
            color=embed_color()
        )

        embed.set_thumbnail(url=server.icon.url if server.icon else None)

        embed.add_field(name=msg(ctx, "serverinfo_name"), value=f"`{server.name}`", inline=True)
        embed.add_field(name=msg(ctx, "serverinfo_id"), value=f"`{server.id}`", inline=True)
        embed.add_field(name=msg(ctx, "serverinfo_members"), value=f"`{server.member_count}`", inline=True)
        embed.add_field(name=msg(ctx, "serverinfo_users"), value=f"`{len([m for m in server.members if not m.bot])}`", inline=True)
        embed.add_field(name=msg(ctx, "serverinfo_bots"), value=f"`{len([m for m in server.members if m.bot])}`", inline=True)
        embed.add_field(name=msg(ctx, "serverinfo_roles"), value=f"`{len(server.roles)}`", inline=True)
        embed.add_field(name=msg(ctx, "serverinfo_created"), value=f"`{server.created_at:%Y-%m-%d %H:%M:%S}`", inline=False)
        embed.add_field(name=msg(ctx, "serverinfo_owner"), value=f"`{server.owner}`", inline=False)

        await ctx.send(embed=embed)

    # -------------------------------
    # USER INFO
    # -------------------------------
    @commands.command(
        name="userinfo",
        help="see cute lil user details ☕ | benutzer‑infos anzeigen"
    )
    async def userinfo(self, ctx, member: discord.Member = None):
        target = member or ctx.author

        embed = discord.Embed(
            title=msg(ctx, "userinfo_title"),
            color=embed_color()
        )

        embed.set_thumbnail(url=target.avatar.url if target.avatar else None)

        embed.add_field(name=msg(ctx, "userinfo_username"), value=f"`{target.display_name}`", inline=True)
        embed.add_field(name=msg(ctx, "userinfo_id"), value=f"`{target.id}`", inline=True)
        embed.add_field(name=msg(ctx, "userinfo_created"), value=f"`{target.created_at:%Y-%m-%d %H:%M:%S}`", inline=False)
        embed.add_field(
            name=msg(ctx, "userinfo_joined"),
            value=f"`{target.joined_at:%Y-%m-%d %H:%M:%S}`" if target.joined_at else "`N/A`",
            inline=False
        )
        embed.add_field(name=msg(ctx, "userinfo_toprole"), value=f"`{target.top_role.name}`", inline=False)

        roles = [r.name for r in target.roles if r.name != "@everyone"]
        embed.add_field(name=msg(ctx, "userinfo_roles"), value=f"`{', '.join(roles)}`" if roles else "`None`", inline=False)

        await ctx.send(embed=embed)

    # -------------------------------
    # AVATAR
    # -------------------------------
    @commands.command(
        name="avatar",
        help="peek at someone's cute avatar 👤 | avatar anzeigen"
    )
    async def avatar(self, ctx, member: discord.Member = None):
        target = member or ctx.author

        embed = discord.Embed(
            title=msg(ctx, "avatar_title", user=target.display_name),
            color=embed_color()
        )
        embed.set_image(url=target.avatar.url if target.avatar else None)

        await ctx.send(embed=embed)

    # -------------------------------
    # ABOUT
    # -------------------------------
    @commands.command(
        name="about",
        help="learn about Niko ☕ | über Niko"
    )
    async def about(self, ctx):
        bot_user = self.bot.user

        embed = discord.Embed(
            title=msg(ctx, "about_title"),
            description=msg(ctx, "about_desc"),
            color=embed_color()
        )

        embed.set_author(
            name=bot_user.name,
            icon_url=bot_user.avatar.url if bot_user.avatar else None
        )

        embed.add_field(name=msg(ctx, "about_dev"), value="Nyxen", inline=True)
        embed.add_field(name=msg(ctx, "about_lib"), value="discord.py", inline=True)
        embed.add_field(name=msg(ctx, "about_servers"), value=f"{len(self.bot.guilds)}", inline=True)

        embed.set_footer(text=msg(ctx, "about_footer"))

        view = View()
        view.add_item(Button(
            label="Invite Niko",
            style=discord.ButtonStyle.link,
            url=f"https://discord.com/oauth2/authorize?client_id={bot_user.id}&permissions=8&scope=bot%20applications.commands",
            row=0
        ))
        view.add_item(Button(
            label="GitHub",
            style=discord.ButtonStyle.link,
            url="https://github.com/developer51709/Niko",
            row=0
        ))
        view.add_item(Button(
            label="Website",
            style=discord.ButtonStyle.link,
            url="https://developer51709.github.io/Niko",
            row=0
        ))
        view.add_item(Button(
            label="ToS",
            style=discord.ButtonStyle.link,
            url="https://developer51709.github.io/Niko/tos.html",
            row=1
        ))
        view.add_item(Button(
            label="Privacy Policy",
            style=discord.ButtonStyle.link,
            url="https://developer51709.github.io/Niko/privacy.html",
            row=1
        ))

        await ctx.send(embed=embed, view=view)

    # -------------------------------
    # CREATOR
    # -------------------------------
    @commands.command(
        name="creator",
        help="meet Niko’s creator ☕ | entwickler‑infos"
    )
    async def creator(self, ctx):
        creator = await self.bot.fetch_user(1435974392810307604)
        bot_user = self.bot.user

        embed = discord.Embed(
            title=msg(ctx, "creator_title"),
            description=msg(ctx, "creator_desc", creator=creator.display_name),
            color=embed_color()
        )

        embed.set_author(
            name=bot_user.name,
            icon_url=bot_user.avatar.url if bot_user.avatar else None
        )

        embed.set_thumbnail(url=creator.avatar.url if creator.avatar else None)

        embed.add_field(name=msg(ctx, "creator_tag"), value=str(creator), inline=False)
        embed.add_field(name=msg(ctx, "creator_id"), value=creator.id, inline=False)
        embed.add_field(name=msg(ctx, "creator_project"), value="Niko All-In-One Discord Bot", inline=False)

        embed.set_footer(text=msg(ctx, "about_footer"))

        view = View()
        view.add_item(Button(
            label="Discord Profile",
            style=discord.ButtonStyle.link,
            url=f"https://discord.com/users/{creator.id}"
        ))
        view.add_item(Button(
            label="GitHub",
            style=discord.ButtonStyle.link,
            url="https://github.com/developer51709"
        ))
        view.add_item(Button(
            label="Website",
            style=discord.ButtonStyle.link,
            url="https://developer51709.github.io"
        ))

        await ctx.send(embed=embed, view=view)

    # -------------------------------
    # ROLE INFO
    # -------------------------------
    @commands.command(
        name="roleinfo",
        help="see cozy role details ☕ | rollen‑infos anzeigen"
    )
    async def roleinfo(self, ctx, role: discord.Role = None):
        if role is None:
            return await ctx.send(msg(ctx, "roleinfo_need_role"))

        embed = discord.Embed(
            title=msg(ctx, "roleinfo_title"),
            color=embed_color()
        )

        embed.add_field(name=msg(ctx, "roleinfo_name"), value=f"`{role.name}`", inline=True)
        embed.add_field(name=msg(ctx, "roleinfo_id"), value=f"`{role.id}`", inline=True)
        embed.add_field(name=msg(ctx, "roleinfo_color"), value=f"`{role.color}`", inline=True)
        embed.add_field(name=msg(ctx, "roleinfo_position"), value=f"`{role.position}`", inline=True)
        embed.add_field(name=msg(ctx, "roleinfo_members"), value=f"`{len(role.members)}`", inline=True)

        await ctx.send(embed=embed)

    # -------------------------------
    # SERVER ICON
    # -------------------------------
    @commands.command(
        name="servericon",
        help="show the server’s cute icon 📍 | server‑icon anzeigen"
    )
    async def servericon(self, ctx):
        server = ctx.guild

        embed = discord.Embed(
            title=msg(ctx, "servericon_title"),
            color=embed_color()
        )
        embed.set_image(url=server.icon.url if server.icon else None)

        await ctx.send(embed=embed)

    # -------------------------------
    # SERVER BANNER
    # -------------------------------
    @commands.command(
        name="serverbanner",
        help="show the server’s banner 🖼 | server‑banner anzeigen"
    )
    async def serverbanner(self, ctx):
        server = ctx.guild

        if not server.banner:
            return await ctx.send(msg(ctx, "serverbanner_none"))

        embed = discord.Embed(
            title=msg(ctx, "serverbanner_title"),
            color=embed_color()
        )
        embed.set_image(url=server.banner.url)

        await ctx.send(embed=embed)

    # -------------------------------
    # BOOST STATS
    # -------------------------------
    @commands.command(
        name="booststats",
        help="see the server’s boost vibes ☕ | boost‑infos anzeigen"
    )
    async def booststats(self, ctx):
        server = ctx.guild

        embed = discord.Embed(
            title=msg(ctx, "booststats_title"),
            color=embed_color()
        )

        embed.add_field(name=msg(ctx, "booststats_count"), value=f"`{server.premium_subscription_count}`", inline=True)
        embed.add_field(name=msg(ctx, "booststats_tier"), value=f"`{server.premium_tier}`", inline=True)
        embed.add_field(name=msg(ctx, "booststats_boosters"), value=f"`{len(server.premium_subscribers)}`", inline=True)

        await ctx.send(embed=embed)

    # -------------------------------
    # SPOTIFY
    # -------------------------------
    @commands.command(
        name="spotify",
        help="see what someone is vibing to on Spotify 🎧 | spotify‑infos anzeigen"
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

        embed = discord.Embed(
            title=msg(ctx, "spotify_title", user=target.display_name),
            color=0x1DB954
        )

        embed.set_thumbnail(url=spotify.album_cover_url)

        duration = spotify.duration.total_seconds()
        embed.add_field(name=msg(ctx, "spotify_track"), value=spotify.title, inline=False)
        embed.add_field(name=msg(ctx, "spotify_artist"), value=spotify.artist, inline=False)
        embed.add_field(name=msg(ctx, "spotify_album"), value=spotify.album, inline=False)
        embed.add_field(
            name=msg(ctx, "spotify_duration"),
            value=f"{int(duration//60)}:{int(duration%60):02d}",
            inline=True
        )

        if spotify.start and spotify.end:
            embed.add_field(name=msg(ctx, "spotify_started"), value=f"<t:{int(spotify.start.timestamp())}:t>", inline=True)
            embed.add_field(name=msg(ctx, "spotify_ends"), value=f"<t:{int(spotify.end.timestamp())}:t>", inline=True)

        embed.set_footer(text=msg(ctx, "spotify_footer"))

        view = View()
        view.add_item(Button(
            label="Open in Spotify",
            style=discord.ButtonStyle.link,
            url=f"https://open.spotify.com/track/{spotify.track_id}"
        ))

        await ctx.send(embed=embed, view=view)

    # -------------------------------
    # DEBUG INFO
    # -------------------------------
    @commands.command(
        name="debuginfo",
        help="view debug info 👾 | debug‑infos anzeigen"
    )
    async def debuginfo(self, ctx):
        uptime_seconds = int(time.time() - self.bot.start_time)
        uptime = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s"
        ai_model = os.getenv("AI_MODEL", "Unknown")
        command_count = len(self.bot.commands)
        ping_latency = round(self.bot.latency * 1000)
        cpu_usage = psutil.cpu_percent()
        memory_usage = round(psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024), 2)

        embed = discord.Embed(
            title=msg(ctx, "debuginfo_title"),
            color=embed_color()
        )

        embed.add_field(name=msg(ctx, "debuginfo_uptime"), value=f"`{uptime}`", inline=True)
        embed.add_field(name=msg(ctx, "debuginfo_model"), value=f"`{ai_model}`", inline=True)
        embed.add_field(name=msg(ctx, "debuginfo_commands"), value=f"`{command_count}`", inline=True)
        embed.add_field(name=msg(ctx, "debuginfo_ping"), value=f"`{ping_latency}ms`", inline=True)
        embed.add_field(name=msg(ctx, "debuginfo_cpu"), value=f"`{cpu_usage}%`", inline=True)
        embed.add_field(name=msg(ctx, "debuginfo_ram"), value=f"`{memory_usage}MB`", inline=True)

        await ctx.send(embed=embed)

    # -------------------------------
    # HOST INFO
    # -------------------------------
    @commands.command(
        name="hostinfo",
        help="view host info 💻 | host‑infos anzeigen"
    )
    async def hostinfo(self, ctx):
        hostname = platform.node()
        os_info = f"{platform.system()} {platform.release()}"
        cpu = platform.processor() or "N/A"
        ram = round(psutil.virtual_memory().total / (1024**3), 2)

        embed = discord.Embed(
            title=msg(ctx, "hostinfo_title"),
            color=embed_color()
        )

        embed.add_field(name=msg(ctx, "hostinfo_hostname"), value=f"`{hostname}`", inline=True)
        embed.add_field(name=msg(ctx, "hostinfo_os"), value=f"`{os_info}`", inline=True)
        embed.add_field(name=msg(ctx, "hostinfo_cpu"), value=f"`{cpu}`", inline=True)
        embed.add_field(name=msg(ctx, "hostinfo_ram"), value=f"`{ram}GB`", inline=True)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(InfoCog(bot))