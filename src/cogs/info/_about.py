"""Info — the commands about Niko itself: /about, /creator, /invite."""

import time
from urllib.parse import quote

import aiohttp
import discord
from discord.ext import commands

from config import links
from config.emojis import get_emoji
from config.ids import OWNER_IDS
from ._messages import msg

from utils.command_locales import command_texts
from utils.prefix_alias import is_prefix_alias

CMDS = command_texts(__package__)

#: The account both cards describe. The id is read from the owner set, so the
#: name on /about is always the same person /creator opens, and changing the
#: owner does not leave one of the two cards pointing at somebody else.
CREATOR_ID = sorted(OWNER_IDS)[0] if OWNER_IDS else 1052690741874401360


#: How long one fetched profile is reused. /creator is a popular card, not a
#: dashboard, so a few minutes of staleness keeps it off the public API without
#: anyone noticing a profile change in the same breath as saving it.
_STAFF_PROFILE_TTL = 300
_staff_profile_cache: dict[int, tuple[float, dict | None]] = {}


def _profile_accent(profile: dict | None) -> discord.Colour | None:
    """The staff profile card's accent colour, or ``None`` for the default."""
    accent = str(((profile or {}).get("card") or {}).get("accent") or "").strip().lstrip("#")
    if len(accent) != 6:
        return None
    try:
        return discord.Colour(int(accent, 16))
    except ValueError:
        return None


def _profile_url(profile: dict) -> str:
    """The public team page for a profile: its handle, or the permanent id."""
    handle = quote(str(profile.get("handle") or CREATOR_ID), safe="._-~")
    return f"{links.WEBSITE}/team/{handle}"


async def _fetch_staff_profile(user_id: int) -> dict | None:
    """The member's public staff profile, exactly as the team page shows it.

    The website already owns the roster, the role labels and the privacy rules,
    so the card reads the same public endpoint a visitor's browser does instead
    of guessing at the database or hardcoding a second copy of the profile.
    """
    timeout = aiohttp.ClientTimeout(total=4)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{links.WEBSITE}/api/team/{int(user_id)}") as response:
                if response.status != 200:
                    return None
                profile = await response.json(content_type=None)
    except Exception:
        # A slow or unreachable site must not break a command about the bot.
        return None
    return profile if isinstance(profile, dict) else None


async def resolve_staff_profile(user_id: int) -> dict | None:
    """The creator's staff profile, reused briefly so every call is not a request.

    A missing profile is cached too: when a member has hidden theirs, the
    command should not ask the website again on every invocation.
    """
    now = time.monotonic()
    cached = _staff_profile_cache.get(int(user_id))
    if cached and now - cached[0] < _STAFF_PROFILE_TTL:
        return cached[1]
    profile = await _fetch_staff_profile(int(user_id))
    _staff_profile_cache[int(user_id)] = (now, profile)
    return profile


def _human_uptime(seconds: float, ctx) -> str:
    """``3d 4h 12m``-style uptime for the about card, in the guild's units."""
    seconds = int(max(0, seconds))
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60
    if days:
        return msg(ctx, "uptime_days", days=days, hours=hours, minutes=minutes)
    if hours:
        return msg(ctx, "uptime_hours", hours=hours, minutes=minutes)
    return msg(ctx, "uptime_minutes", minutes=minutes)


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
        description=CMDS.text("about.description"),
        help=CMDS.help("about"),
    )
    async def about(self, ctx):
        bot_user = self.bot.user
        avatar_url = bot_user.avatar.url if bot_user.avatar else None

        creator = await resolve_creator(self.bot)
        creator_line = creator.display_name if creator else msg(ctx, 'about_dev_unknown')

        servers = len(self.bot.guilds)
        members = sum(guild.member_count or 0 for guild in self.bot.guilds)
        commands = (
            getattr(self.bot, "_status_command_count", None)
            or sum(
                1 for command in self.bot.commands
                if not is_prefix_alias(command)
            )
        )
        started = getattr(self.bot, "start_time", None)
        uptime = _human_uptime(time.time() - started, ctx) if started else "\u2014"

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

        invite_url = links.invite_url(bot_user.id)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(content=text),
                accessory=discord.ui.Thumbnail(avatar_url) if avatar_url else discord.ui.TextDisplay(content=" ")
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label=msg(ctx, "link_invite"),
                    style=discord.ButtonStyle.link,
                    emoji=get_emoji("discord"),
                    url=invite_url
                ),
                discord.ui.Button(
                    label=msg(ctx, "link_github"),
                    style=discord.ButtonStyle.link,
                    emoji=get_emoji("github"),
                    url=links.GITHUB
                ),
                discord.ui.Button(
                    label=msg(ctx, "link_website"),
                    style=discord.ButtonStyle.link,
                    emoji=get_emoji("website"),
                    url=links.WEBSITE
                ),
            ),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label=msg(ctx, "link_tos"),
                    style=discord.ButtonStyle.link,
                    url=links.TOS
                ),
                discord.ui.Button(
                    label=msg(ctx, "link_privacy"),
                    style=discord.ButtonStyle.link,
                    url=links.PRIVACY
                ),
            )
        )
        view.add_item(container)
        await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    # -------------------------------
    # CREATOR
    # -------------------------------
    @commands.hybrid_command(
        name="creator",
        description=CMDS.text("creator.description"),
        help=CMDS.help("creator"),
    )
    async def creator(self, ctx):
        creator = await resolve_creator(self.bot)
        profile = await resolve_staff_profile(CREATOR_ID)

        # The staff profile repeats Discord's identity, so either source can
        # name the card; only when both are missing is there nothing to show.
        name = (creator.display_name if creator else None) or (profile or {}).get("name")
        if not name:
            return await ctx.send(msg(ctx, "creator_unavailable"))

        avatar_url = (
            (creator.avatar.url if creator and creator.avatar else None)
            or (profile or {}).get("avatar_url")
        )
        # A hidden profile has no public page to link to, and its bio and role
        # are private, so the card falls back to just the introduction.
        listed = bool(profile and profile.get("visible"))
        role_label = str(profile.get("role_label") or "").strip() if listed else ""
        bio = str(profile.get("bio") or "").strip() if listed else ""

        lines = [
            f"### {msg(ctx, 'creator_title')}",
            msg(ctx, "creator_desc", creator=name),
        ]
        if bio:
            # Quoting keeps the profile's own words distinct from the card's.
            lines.append("\n".join(f"> {line}".rstrip() for line in bio.splitlines()))
        if role_label:
            lines.append(f"**{msg(ctx, 'creator_role')}:** {role_label}")

        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(content="\n\n".join(lines)),
                accessory=discord.ui.Thumbnail(avatar_url) if avatar_url else discord.ui.TextDisplay(content=" "),
            ),
            accent_colour=_profile_accent(profile) if listed else None,
        )
        if listed:
            container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            container.add_item(discord.ui.TextDisplay(
                content=f"-# [{msg(ctx, 'creator_profile')}]({_profile_url(profile)})"
            ))

        view = discord.ui.LayoutView()
        view.add_item(container)
        # A bio is free text, so a mention typed into it must never ping.
        await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    # -------------------------------
    # INVITE
    # -------------------------------
    @commands.hybrid_command(
        name="invite",
        description=CMDS.text("invite.description"),
        help=CMDS.help("invite"),
    )
    async def invite(self, ctx):
        bot_user = self.bot.user
        invite_link = links.invite_url(bot_user.id)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('invite')} {msg(ctx, 'invite_title')}\n[{msg(ctx, 'invite_link')}]({invite_link})"
            )
        )
        view.add_item(container)
        await ctx.send(view=view)
