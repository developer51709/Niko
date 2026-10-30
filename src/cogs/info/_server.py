"""Info — the commands about a server: /serverinfo, /servericon, /serverbanner,
/booststats and /roleinfo."""

import discord
from discord.ext import commands

from config.emojis import get_emoji
from ._messages import _divider, cv2_image, cv2_text, key_permission_names, msg

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

# Discord's verification levels, in the order they escalate. The translated
# label comes from the catalogue, the level itself is the key.
_VERIFICATION_KEYS = {
    discord.VerificationLevel.none: "verification_none",
    discord.VerificationLevel.low: "verification_low",
    discord.VerificationLevel.medium: "verification_medium",
    discord.VerificationLevel.high: "verification_high",
    discord.VerificationLevel.highest: "verification_highest",
}

# Guild features worth naming on the card. Discord ships far more of them than
# fit on a card, so anything not listed falls back to its title-cased name.
_FEATURE_LABELS = {
    "COMMUNITY": "Community",
    "PARTNERED": "Partnered",
    "VERIFIED": "Verified",
    "DISCOVERABLE": "Discoverable",
    "NEWS": "Announcement Channels",
    "ANIMATED_ICON": "Animated Icon",
    "BANNER": "Banner",
    "INVITE_SPLASH": "Invite Splash",
    "VANITY_URL": "Vanity URL",
    "MORE_EMOJI": "More Emoji",
    "ROLE_ICONS": "Role Icons",
    "SOUNDBOARD": "Soundboard",
    "THREADS_ENABLED": "Threads",
    "MONETIZATION_ENABLED": "Monetization",
    "TICKETED_EVENTS_ENABLED": "Ticketed Events",
    "WELCOME_SCREEN_ENABLED": "Welcome Screen",
    "MEMBER_VERIFICATION_GATE_ENABLED": "Membership Screening",
    "AUTO_MODERATION": "AutoMod",
    "GUILD_ONBOARDING": "Onboarding",
    "HAS_DIRECTORY_ENTRY": "Directory Entry",
    "LINKED_TO_DIRECTORY": "Linked To Directory",
}

# How many features the card names before it summarises the rest.
_FEATURE_LIMIT = 8


def _feature_label(feature: str) -> str:
    """The human-readable name of a guild feature."""
    return _FEATURE_LABELS.get(feature, feature.replace("_", " ").title())


def _shorten(text: str, limit: int) -> str:
    """Trim a free-text field so a long description cannot swamp the card."""
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


class ServerMixin:
    """Commands that describe the server a command was run in."""

    # -------------------------------
    # SERVER INFO
    # -------------------------------
    @commands.hybrid_command(
        name="serverinfo",
        aliases=["si", "server"],
        description=CMDS.text("serverinfo.description"),
        help=CMDS.help("serverinfo"),
    )
    async def serverinfo(self, ctx):
        server = ctx.guild
        icon_url = server.icon.url if server.icon else None

        members = list(server.members)
        humans = sum(1 for m in members if not m.bot)
        bots = len(members) - humans
        online = sum(1 for m in members if m.status is not discord.Status.offline)

        channels = list(server.channels)
        text_channels = sum(
            1 for c in channels
            if c.type in (discord.ChannelType.text, discord.ChannelType.news)
        )
        voice_channels = sum(
            1 for c in channels
            if c.type in (discord.ChannelType.voice, discord.ChannelType.stage_voice)
        )
        categories = sum(1 for c in channels if c.type is discord.ChannelType.category)

        # ── Identity ──────────────────────────────────────────────────────
        created = int(server.created_at.timestamp())
        owner = server.owner.mention if server.owner else "—"
        verification = msg(
            ctx, _VERIFICATION_KEYS.get(server.verification_level, "verification_none")
        )

        identity = [
            f"**{msg(ctx, 'serverinfo_owner')}:** {owner}",
            f"**{msg(ctx, 'serverinfo_id')}:** `{server.id}`",
            f"**{msg(ctx, 'serverinfo_created')}:** <t:{created}:f> (<t:{created}:R>)",
            f"**{msg(ctx, 'serverinfo_verification')}:** `{verification}`",
        ]
        if server.description:
            identity.append(
                f"**{msg(ctx, 'serverinfo_description')}:** "
                f"{_shorten(server.description, 180)}"
            )

        # ── Community ─────────────────────────────────────────────────────
        community = [
            f"**{msg(ctx, 'serverinfo_members')}:** `{server.member_count}` "
            f"(`{humans}` {msg(ctx, 'serverinfo_humans')} · "
            f"`{bots}` {msg(ctx, 'serverinfo_bots')})",
            f"**{msg(ctx, 'serverinfo_online')}:** `{online}`",
            f"**{msg(ctx, 'serverinfo_roles')}:** `{len(server.roles)}`",
            f"**{msg(ctx, 'serverinfo_channels')}:** `{len(channels)}` "
            f"(`{text_channels}` {msg(ctx, 'serverinfo_text_channels')} · "
            f"`{voice_channels}` {msg(ctx, 'serverinfo_voice_channels')} · "
            f"`{categories}` {msg(ctx, 'serverinfo_categories')})",
            f"**{msg(ctx, 'serverinfo_emojis')}:** `{len(server.emojis)}`  ·  "
            f"**{msg(ctx, 'serverinfo_stickers')}:** `{len(server.stickers)}`",
        ]

        # ── Boosts ────────────────────────────────────────────────────────
        boost_lines = []
        if server.premium_subscription_count or server.premium_tier:
            boost_lines.append(
                f"**{msg(ctx, 'booststats_count')}:** `{server.premium_subscription_count}`  ·  "
                f"**{msg(ctx, 'booststats_tier')}:** `{server.premium_tier}`"
            )
            if server.premium_subscribers:
                boost_lines.append(
                    f"**{msg(ctx, 'booststats_boosters')}:** `{len(server.premium_subscribers)}`"
                )

        # ── Features ──────────────────────────────────────────────────────
        feature_lines = []
        labels = sorted(_feature_label(f) for f in server.features)
        if labels:
            shown = labels[:_FEATURE_LIMIT]
            if len(labels) > _FEATURE_LIMIT:
                shown.append(f"+{len(labels) - _FEATURE_LIMIT}")
            feature_lines.append(
                f"**{msg(ctx, 'serverinfo_features')}:** " + " · ".join(shown)
            )

        # A card that reads like the userinfo one: a header with the icon, then
        # the server's own facts, its community, and — when it has them — its
        # boosts and features, each block under a rule.
        heading = discord.ui.TextDisplay(
            content=(
                f"## {server.name}\n"
                f"{get_emoji('participants')} **{server.member_count}** "
                f"{msg(ctx, 'serverinfo_members_word')}  ·  "
                f"{get_emoji('status_online')} **{online}** "
                f"{msg(ctx, 'serverinfo_online_word')}"
            )
        )
        if icon_url:
            children = [
                discord.ui.Section(heading, accessory=discord.ui.Thumbnail(icon_url))
            ]
        else:
            children = [heading]

        children += [
            _divider(),
            discord.ui.TextDisplay(content="\n".join(identity)),
            _divider(),
            discord.ui.TextDisplay(content="\n".join(community)),
        ]
        if boost_lines:
            children += [_divider(), discord.ui.TextDisplay(content="\n".join(boost_lines))]
        if feature_lines:
            children += [_divider(), discord.ui.TextDisplay(content="\n".join(feature_lines))]

        view = discord.ui.LayoutView(timeout=None)
        view.add_item(discord.ui.Container(*children))
        await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    # -------------------------------
    # ROLE INFO
    # -------------------------------
    @commands.hybrid_command(
        name="roleinfo",
        description=CMDS.text("roleinfo.description"),
        help=CMDS.help("roleinfo"),
    )
    async def roleinfo(self, ctx, role: discord.Role = None):
        if role is None:
            return await ctx.send(msg(ctx, "roleinfo_need_role"))

        yes, no = msg(ctx, "roleinfo_yes"), msg(ctx, "roleinfo_no")
        created = int(role.created_at.timestamp())
        # A role without an explicit colour is Discord's default grey, which is
        # worth naming instead of printing #000000.
        color_text = (
            f"`#{role.color.value:06X}`"
            if role.color.value
            else f"*{msg(ctx, 'roleinfo_color_default')}*"
        )
        # Counted, never listed: a popular role can be held by tens of thousands
        # of members, so the card names only how many there are.
        member_count = len(role.members)

        # ── Identity ──────────────────────────────────────────────
        identity = [
            f"**{msg(ctx, 'roleinfo_id')}:** `{role.id}`",
            f"**{msg(ctx, 'roleinfo_color')}:** {color_text}",
            f"**{msg(ctx, 'roleinfo_position')}:** `#{role.position}` / `{len(ctx.guild.roles)}`",
            f"**{msg(ctx, 'roleinfo_created')}:** <t:{created}:f> (<t:{created}:R>)",
            f"**{msg(ctx, 'roleinfo_mentionable')}:** {yes if role.mentionable else no}  ·  "
            f"**{msg(ctx, 'roleinfo_hoisted')}:** {yes if role.hoist else no}",
        ]
        # Integration roles cannot be edited by hand, so only they say so.
        if role.managed:
            identity.append(f"**{msg(ctx, 'roleinfo_managed')}:** {yes}")

        # ── Permissions ──────────────────────────────────────────────
        permissions = key_permission_names(role.permissions)
        permission_lines = [
            f"**{msg(ctx, 'roleinfo_permissions')}:** "
            + (", ".join(permissions) if permissions else f"*{msg(ctx, 'roleinfo_permissions_none')}*")
        ]

        # The role's own colour becomes the container's accent, and its icon (if
        # it has one) the thumbnail, so the card reads as that role.
        icon = role.display_icon
        icon_url = getattr(icon, "url", None)
        icon_prefix = f"{icon} " if isinstance(icon, str) else ""
        heading = discord.ui.TextDisplay(
            content=(
                f"## {icon_prefix}{role.name}\n"
                f"{get_emoji('participants')} **{member_count}** "
                f"{msg(ctx, 'roleinfo_members_word')}  ·  {role.mention}"
            )
        )
        if icon_url:
            children = [
                discord.ui.Section(heading, accessory=discord.ui.Thumbnail(icon_url))
            ]
        else:
            children = [heading]

        children += [
            _divider(),
            discord.ui.TextDisplay(content="\n".join(identity)),
            _divider(),
            discord.ui.TextDisplay(content="\n".join(permission_lines)),
        ]

        view = discord.ui.LayoutView(timeout=None)
        view.add_item(
            discord.ui.Container(
                *children,
                accent_color=role.color if role.color.value else None,
            )
        )
        await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    # -------------------------------
    # SERVER ICON
    # -------------------------------
    @commands.hybrid_command(
        name="servericon",
        description=CMDS.text("servericon.description"),
        help=CMDS.help("servericon"),
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
        description=CMDS.text("serverbanner.description"),
        help=CMDS.help("serverbanner"),
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
        description=CMDS.text("booststats.description"),
        help=CMDS.help("booststats"),
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
