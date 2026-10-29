"""Info — the commands about Niko itself: /about, /creator, /invite."""

import time

import discord
from discord.ext import commands

from config import links
from config.emojis import get_emoji
from config.ids import OWNER_IDS
from ._messages import msg

#: The account both cards describe. The id is read from the owner set, so the
#: name on /about is always the same person /creator opens, and changing the
#: owner does not leave one of the two cards pointing at somebody else.
CREATOR_ID = sorted(OWNER_IDS)[0] if OWNER_IDS else 1052690741874401360


def _human_uptime(seconds: float) -> str:
    """``3d 4h 12m``-style uptime for the about card."""
    seconds = int(max(0, seconds))
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60
    if days:
        return f"{days}d {hours}h {minutes}m"
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


async def resolve_creator(bot):
    """The creator account, from the same id both cards read.

    The cached user is used first so a command costs nothing; Discord is only
    asked when the account is not cached, and a failed lookup still lets the
    card answer instead of raising.
    """
    user = bot.get_user(CREATOR_ID)
    if user is not None:
        return user
    try:
        return await bot.fetch_user(CREATOR_ID)
    except (discord.NotFound, discord.HTTPException):
        return None


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

        creator = await resolve_creator(self.bot)
        creator_line = (
            f"{creator.display_name} ({creator.mention})" if creator
            else f"<@{CREATOR_ID}>"
        )

        servers = len(self.bot.guilds)
        members = sum(guild.member_count or 0 for guild in self.bot.guilds)
        commands = (
            getattr(self.bot, "_status_command_count", None)
            or len(self.bot.commands)
        )
        started = getattr(self.bot, "start_time", None)
        uptime = _human_uptime(time.time() - started) if started else "\u2014"

        text = (
            f"### {get_emoji('bot')} {msg(ctx, 'about_title')}\n"
            f"{msg(ctx, 'about_desc')}\n\n"
            f"**{msg(ctx, 'about_dev')}:** {creator_line}\n"
            f"**{msg(ctx, 'about_lib')}:** discord.py 2.7\n"
            f"**{msg(ctx, 'about_servers')}:** {servers:,}  \u00b7  "
            f"**{msg(ctx, 'about_members')}:** {members:,}\n"
            f"**{msg(ctx, 'about_commands')}:** {commands:,}  \u00b7  "
            f"**{msg(ctx, 'about_uptime')}:** {uptime}\n\n"
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
        creator = await resolve_creator(self.bot)
        if creator is None:
            return await ctx.send(msg(ctx, "creator_unavailable"))
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
