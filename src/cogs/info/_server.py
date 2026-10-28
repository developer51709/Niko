"""Info — the commands about a server: /serverinfo, /servericon, /serverbanner,
/booststats and /roleinfo."""

import discord
from discord.ext import commands

from config.emojis import get_emoji
from ._messages import cv2_image, cv2_text, msg


class ServerMixin:
    """Commands that describe the server a command was run in."""

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
