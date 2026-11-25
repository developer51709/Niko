"""Info — the commands about a person: /userinfo, /avatar, /banner."""

import re

import discord
from discord.ext import commands

from config.emojis import get_emoji
from ._avatars import AvatarButtons, UserInfoButtons
from ._badges import _get_badges, _get_discord_badges
from ._messages import _divider, cv2_image, key_permission_names, msg

from utils.command_locales import command_texts
from utils.presence import is_mobile_presence

CMDS = command_texts(__package__)

_STATUS_TEXT = {
    discord.Status.online:  ("status_online",  "Online"),
    discord.Status.idle:    ("status_idle",    "Idle"),
    discord.Status.dnd:     ("status_dnd",     "Do Not Disturb"),
    discord.Status.offline: ("status_offline", "Offline"),
}

#: An emoji reference whose id is shorter than a snowflake. The config holds one
#: of these for art the emoji sync has not uploaded yet, and sending it draws
#: the raw ``<:name:1>`` text instead of an emoji.
_STUB_EMOJI = re.compile(r"<a?:[A-Za-z0-9_]+:\d{1,14}>")


def _ready_emoji(emoji_name: str):
    """The emoji for ``emoji_name``, or ``None`` while it is still a stub."""
    emoji = get_emoji(emoji_name)
    if emoji is None or _STUB_EMOJI.fullmatch(emoji):
        return None
    return emoji


def _presence_source(ctx, target):
    """The copy of ``target`` that carries presence.

    A slash interaction's member payload has no presence fields, so the member
    it hands over reads as offline even while the user is online on their
    phone. The guild cache holds the statuses the gateway last sent.
    """
    guild = getattr(ctx, "guild", None)
    cached = guild.get_member(getattr(target, "id", 0)) if guild is not None else None
    return cached or target


def _status_line(ctx, target) -> tuple[str | None, str]:
    """The status emoji and label to draw for ``target``.

    Only online, idle and DND have a phone-shaped counterpart, and a phone-only
    presence is the only case Discord swaps the dot for it. The phone art is
    optional: without it the round dot is drawn rather than nothing at all.
    """
    presence = _presence_source(ctx, target)
    if any(isinstance(activity, discord.Streaming) for activity in presence.activities):
        return _ready_emoji("status_streaming"), "Streaming"
    key, text = _STATUS_TEXT.get(presence.status, ("status_offline", "Offline"))
    if is_mobile_presence(presence) and key != "status_offline":
        mobile = _ready_emoji(f"{key}_mobile")
        if mobile is not None:
            return mobile, text
    return _ready_emoji(key), text


class UserMixin:
    """Commands that describe a member or a user account."""

    # -------------------------------
    # USER INFO
    # -------------------------------
    @commands.hybrid_command(
        name="userinfo",
        aliases=["ui", "user"],
        description=CMDS.text("userinfo.description"),
        help=CMDS.help("userinfo"),
    )
    async def userinfo(self, ctx, member: discord.Member = None):
        if ctx.interaction:
            await ctx.defer()

        target = member or ctx.author
        # display_avatar is always set, so a member who never uploaded a picture
        # still has one to draw in the header.
        avatar_url = target.display_avatar.url

        # ── Status ────────────────────────────────────────────────────────
        status_emoji, status_text = _status_line(ctx, target)

        # ── Badges ────────────────────────────────────────────────────────
        disc_badges = _get_discord_badges(target)
        niko_badges = await _get_badges(self.bot, target.id)

        badge_lines = []
        if disc_badges:
            badge_lines.append(
                f"**{msg(ctx, 'userinfo_discord_badges')}:** {' '.join(disc_badges)}"
            )
        if niko_badges:
            badge_lines.append(
                f"**{msg(ctx, 'userinfo_niko_badges')}:** {' '.join(niko_badges)}"
            )

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

        # The permissions worth naming; Administrator implies all the others,
        # so it is the only one shown when it is set.
        key_perms = key_permission_names(target.guild_permissions)

        bot_tag = f" {get_emoji('bot')}" if target.bot else ""
        created = int(target.created_at.timestamp())

        # The account's own facts, then its facts in this server: two blocks
        # with a rule between them read as a profile instead of one wall of
        # bold labels.
        identity = (
            f"**{msg(ctx, 'userinfo_id')}:** `{target.id}`\n"
            f"**{msg(ctx, 'userinfo_username')}:** `@{target.name}`\n"
            f"**{msg(ctx, 'userinfo_created')}:** <t:{created}:f> (<t:{created}:R>)"
        )

        membership = [
            f"**{msg(ctx, 'userinfo_nickname')}:** {nickname}",
            f"**{msg(ctx, 'userinfo_joined')}:** {joined}",
            f"**{msg(ctx, 'userinfo_position')}:** `#{join_pos}` / `{len(ctx.guild.members)}`",
            f"**{msg(ctx, 'userinfo_toprole')}:** {target.top_role.mention}",
            f"**{msg(ctx, 'userinfo_roles')} ({len(roles)}):** {role_display if roles else '*none*'}",
        ]
        if target.premium_since:
            membership.append(
                f"**{msg(ctx, 'userinfo_boosting')}:** "
                f"<t:{int(target.premium_since.timestamp())}:R>"
            )
        if key_perms:
            membership.append(
                f"**{msg(ctx, 'userinfo_permissions')}:** {', '.join(key_perms)}"
            )

        children = [
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=(
                        f"## {target.display_name}{bot_tag}\n"
                        f"{status_emoji} **{status_text}**  ·  `@{target.name}`"
                    )
                ),
                accessory=discord.ui.Thumbnail(avatar_url),
            ),
            _divider(),
            discord.ui.TextDisplay(content=identity),
            _divider(),
            discord.ui.TextDisplay(content="\n".join(membership)),
        ]
        if badge_lines:
            children.append(_divider())
            children.append(discord.ui.TextDisplay(content="\n".join(badge_lines)))
        children.append(UserInfoButtons(target.id, ctx))

        # No accent colour: normal command responses stay on Discord's neutral
        # container, so the card is not the odd one out.
        view = discord.ui.LayoutView(timeout=None)
        view.add_item(discord.ui.Container(*children))
        await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    # -------------------------------
    # AVATAR
    # -------------------------------
    @commands.hybrid_command(
        name="avatar",
        description=CMDS.text("avatar.description"),
        help=CMDS.help("avatar"),
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
            AvatarButtons(target.id, ctx)
        )
        view.add_item(container)
        await ctx.send(view=view)

    # -------------------------------
    # BANNER
    # -------------------------------
    @commands.hybrid_command(
        name="banner",
        description=CMDS.text("banner.description"),
        help=CMDS.help("banner"),
    )
    async def banner(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        target = await self.bot.fetch_user(target.id)
        banner_url = target.banner.url if target.banner else None
        if not banner_url:
            return await ctx.send(msg(ctx, "banner_none", user=target.display_name))
        text = f"### {msg(ctx, 'banner_title', user=target.display_name)}"
        await ctx.send(view=cv2_image(text, image_url=banner_url))
