"""Info — the commands about Niko itself: /about, /creator, /invite."""

import discord
from discord.ext import commands

from config import links
from config.emojis import get_emoji
from ._messages import msg


class AboutMixin:
    """Introductory cards: what Niko is, who made him, and how to invite him."""

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
