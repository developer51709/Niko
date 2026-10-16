"""
Social Media Notifier
─────────────────────
Tracks new posts / videos / uploads from:
  • YouTube   (RSS feed — channel ID or @handle)
  • Twitch    (Helix API — application client-credentials)
  • Twitter/X (public syndication/oEmbed — no API key)
  • TikTok    (web scraping)
  • Bluesky   (AT Protocol public API)
  • Reddit    (Reddit JSON API — subreddits)

All notifications use Discord cv2 containers.
YouTube, Twitch and Reddit notifications include a thumbnail preview.

Follows are stored through ``utils.social.follows`` rather than with inline SQL,
because the dashboard's notifications tab (``webapp/notifier_routes.py``) writes
the very same rows. That module is also the source of the per-follow limits,
template rendering and health columns used here.

The poll loop fetches each account once per cycle even when several servers
follow it, keeps a bounded number of requests in flight, and pauses an account
automatically after repeated failures instead of retrying it forever.
"""

import asyncio
import discord
from discord import MediaGalleryItem, UnfurledMediaItem
from discord.ext import commands, tasks
from discord.ui import Modal, TextInput

from config.emojis import get_emoji
from utils.social.youtube import fetch_latest_youtube, validate_youtube_channel, make_stored, display_name as yt_display, channel_id_of
from utils.social.twitch import fetch_latest_twitch, normalize_login as twitch_login, validate_twitch_login
from utils.social.twitter import fetch_latest_tweet, validate_twitter_username
from utils.social.tiktok import fetch_latest_tiktok, validate_tiktok_username
from utils.social.bluesky import fetch_latest_bluesky, validate_bluesky_handle
from utils.social.reddit import fetch_latest_reddit, validate_reddit
from utils.social.follows import (
    FAILURE_LIMIT,
    FETCH_CONCURRENCY,
    MAX_FOLLOWS_PER_GUILD,
    MAX_FOLLOWS_PER_PLATFORM,
    create_follow,
    delete_follow,
    get_follow,
    get_notifier_config,
    list_follows,
    record_check,
    rename_follow,
    render_template,
    update_follow,
    utc_now,
)
from utils.social.follows import display_name as _display

# ─────────────────────────────────────────
#  Platform registry
# ─────────────────────────────────────────

PLATFORMS: dict[str, dict] = {
    "youtube": {
        "icon":    get_emoji("youtube"),
        "color":   discord.Colour(0xFF0000),
        "label":   "YouTube Channel",
        "btn_style": discord.ButtonStyle.danger,
        "field_label": "Channel @Handle or ID",
        "field_placeholder": "@MKBHD  or  UCBcRF18a7Qf58cCRy5xuWwQ",
    },
    "twitch": {
        "icon":    get_emoji("twitch"),
        "color":   discord.Colour(0x9146FF),
        "label":   "Twitch Channel",
        "btn_style": discord.ButtonStyle.primary,
        "field_label": "Channel name or URL",
        "field_placeholder": "shroud  or  https://twitch.tv/shroud",
    },
    "twitter": {
        "icon":    get_emoji("twitterx"),
        "color":   discord.Colour(0x1DA1F2),
        "label":   "Twitter/X Account",
        "btn_style": discord.ButtonStyle.primary,
        "field_label": "Username",
        "field_placeholder": "elonmusk",
    },
    "tiktok": {
        "icon":    get_emoji("tiktok"),
        "color":   discord.Colour(0xFF0050),
        "label":   "TikTok Account",
        "btn_style": discord.ButtonStyle.danger,
        "field_label": "Username",
        "field_placeholder": "charlidamelio",
    },
    "bluesky": {
        "icon":    get_emoji("bluesky"),
        "color":   discord.Colour(0x0085FF),
        "label":   "Bluesky Account",
        "btn_style": discord.ButtonStyle.primary,
        "field_label": "@Handle",
        "field_placeholder": "bsky.bsky.team",
    },
    "reddit": {
        "icon":    get_emoji("reddit"),
        "color":   discord.Colour(0xFF4500),
        "label":   "Reddit Subreddit",
        "btn_style": discord.ButtonStyle.secondary,
        "field_label": "Subreddit name",
        "field_placeholder": "programming  (no r/ needed)",
    },
}

ALL_PLATFORMS = list(PLATFORMS.keys())


# ─────────────────────────────────────────
#  Fetch dispatcher
# ─────────────────────────────────────────

async def _fetch(platform: str, username: str) -> dict | None:
    try:
        if platform == "youtube":
            return await fetch_latest_youtube(username)
        if platform == "twitch":
            # Helix access is synchronous (and shared with the web profile
            # cards), so it runs off the event loop.
            return await asyncio.to_thread(fetch_latest_twitch, username)
        if platform == "twitter":
            return await fetch_latest_tweet(username)
        if platform == "tiktok":
            return await fetch_latest_tiktok(username)
        if platform == "bluesky":
            return await fetch_latest_bluesky(username)
        if platform == "reddit":
            return await fetch_latest_reddit(username)
    except Exception:
        pass
    return None


async def _validate(platform: str, raw: str) -> tuple[bool, str]:
    """
    Validate the user input for a given platform.
    Returns (success, stored_username).
    For YouTube, stored_username = 'DisplayName|ChannelID'.
    """
    if platform == "youtube":
        result = await validate_youtube_channel(raw)
        if result is None:
            return False, ""
        d_name, cid = result
        return True, make_stored(d_name, cid)

    if platform == "twitch":
        login = twitch_login(raw)
        if not login:
            return False, ""
        ok = await asyncio.to_thread(validate_twitch_login, login)
        return ok, login

    if platform == "twitter":
        ok = await validate_twitter_username(raw.lstrip("@"))
        return ok, raw.lstrip("@")

    if platform == "tiktok":
        ok = await validate_tiktok_username(raw.lstrip("@"))
        return ok, raw.lstrip("@")

    if platform == "bluesky":
        ok = await validate_bluesky_handle(raw)
        return ok, raw.lstrip("@")

    if platform == "reddit":
        sub = raw.strip().lstrip("r/").strip()
        ok = await validate_reddit(sub)
        return ok, sub

    return False, ""


# ─────────────────────────────────────────
#  Public helpers for the web dashboard
# ─────────────────────────────────────────

def platform_catalog() -> list[dict]:
    """JSON-safe platform metadata for the dashboard's notifications tab."""
    return [
        {
            "id": platform,
            "label": meta["label"],
            "field_label": meta["field_label"],
            "field_placeholder": meta["field_placeholder"],
        }
        for platform, meta in PLATFORMS.items()
    ]


async def validate_account(platform: str, raw: str) -> tuple[bool, str]:
    """Validate an account for the dashboard and return (ok, stored value).

    Thin public wrapper around :func:`_validate` so the web layer reuses the
    exact input handling the Discord commands use.
    """
    if platform not in PLATFORMS:
        return False, ""
    return await _validate(platform, raw)


async def fetch_latest_post(platform: str, username: str) -> dict | None:
    """Fetch an account's newest post (dashboard wrapper for :func:`_fetch`)."""
    if platform not in PLATFORMS:
        return None
    return await _fetch(platform, username)


def _resolve_channel(guild: discord.Guild, text: str):
    text = text.strip()
    if text.startswith("<#") and text.endswith(">"):
        try:
            return guild.get_channel(int(text[2:-1]))
        except ValueError:
            return None
    if text.isdigit():
        return guild.get_channel(int(text))
    return discord.utils.get(guild.text_channels, name=text.lstrip("#"))


# ─────────────────────────────────────────
#  Notification cv2 container builder
# ─────────────────────────────────────────

def build_notification_view(
    platform: str,
    username: str,
    post: dict,
) -> discord.ui.LayoutView:
    meta      = PLATFORMS.get(platform, {})
    icon      = meta.get("icon", get_emoji("megaphone"))
    color     = meta.get("color", discord.Colour(0x5865F2))
    dname     = _display(platform, username)
    url       = post.get("url", "")
    text      = post.get("text") or post.get("title") or ""
    thumbnail = post.get("thumbnail")

    # Header line
    if platform == "youtube":
        header = f"### {icon} New YouTube Video"
        body   = f"**{dname}** just uploaded a new video!"
    elif platform == "twitch":
        if str(post.get("id", "")).startswith("stream:"):
            header = f"### {icon} New Twitch Stream"
            body   = f"**{dname}** is live right now!"
        else:
            header = f"### {icon} New Twitch Broadcast"
            body   = f"**{dname}** just uploaded a new broadcast!"
    elif platform == "twitter":
        header = f"### {icon} New Tweet"
        body   = f"**{dname}** just posted on Twitter/X!"
    elif platform == "tiktok":
        header = f"### {icon} New TikTok"
        body   = f"**{dname}** just posted a new TikTok!"
    elif platform == "bluesky":
        header = f"### {icon} New Bluesky Post"
        body   = f"**{dname}** just posted on Bluesky!"
    elif platform == "reddit":
        header = f"### {icon} New Reddit Post — {dname}"
        body   = ""
    else:
        header = f"### {icon} New Post"
        body   = f"**{dname}** just posted!"

    if text:
        preview = text[:280] + ("…" if len(text) > 280 else "")
        # Quote every line so multi-line posts stay inside the blockquote —
        # prefixing only the first line makes the rest render as plain text.
        # Empty lines become a bare `> ` to keep the quote contiguous.
        quoted = "\n".join(f"> {line}" if line else "> " for line in preview.rstrip().splitlines())
        if body:
            body += f"\n\n{quoted}"
        else:
            body = quoted

    body += f"\n\n{get_emoji('link')} [View{'  Video' if platform == 'youtube' else ' Post'}]({url})"

    # Build container items
    items: list = [
        discord.ui.TextDisplay(content=header),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=body),
    ]

    if thumbnail:
        items.append(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        items.append(discord.ui.MediaGallery(
            MediaGalleryItem(media=UnfurledMediaItem(url=thumbnail))
        ))

    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(*items, accent_colour=color))
    return view


def build_notification_content(
    *,
    platform: str,
    username: str,
    post: dict,
    template: str = "",
    role: discord.Role | None = None,
) -> tuple[str | None, discord.AllowedMentions]:
    """Build the plain-content part of a notification (role ping + template).

    A cv2 ``LayoutView`` cannot carry mentions, so the optional role ping and
    the server's custom template are sent as message content next to the view.
    Mentions are always restricted to the configured role, which means neither a
    template nor a creator's post text can accidentally ping @everyone.
    """
    parts: list[str] = []
    if role is not None:
        parts.append(role.mention)

    rendered = render_template(
        template,
        account=_display(platform, username),
        platform=platform,
        title=post.get("title") or post.get("text") or "",
        url=post.get("url") or "",
    )
    if rendered:
        parts.append(rendered)

    allowed_mentions = discord.AllowedMentions(roles=[role] if role is not None else [])
    return ("\n".join(parts) if parts else None), allowed_mentions


async def _save_follow(
    cxn,
    *,
    guild: discord.Guild,
    platform: str,
    stored: str,
    channel: discord.TextChannel,
    seed_id: str | None,
) -> tuple[bool, str]:
    """Create a follow, or move an existing one to ``channel``.

    Per-server limits are enforced here rather than only in the dashboard, so a
    server cannot slip past them with the slash commands. Returns
    ``(moved, error)`` — ``moved`` is true when the account was already followed.
    """
    existing = await get_follow(cxn, guild.id, platform, stored)
    if existing is not None:
        await update_follow(
            cxn,
            guild_id=guild.id,
            platform=platform,
            username=stored,
            channel_id=channel.id,
            enabled=True,
        )
        return True, ""

    follows = await list_follows(cxn, guild.id)
    if len(follows) >= MAX_FOLLOWS_PER_GUILD:
        return False, (
            f"This server already follows {MAX_FOLLOWS_PER_GUILD} accounts. "
            "Remove one before adding another."
        )
    same_platform = sum(1 for follow in follows if follow["platform"] == platform)
    if same_platform >= MAX_FOLLOWS_PER_PLATFORM:
        label = PLATFORMS.get(platform, {}).get("label", platform.capitalize())
        return False, (
            f"This server already follows {MAX_FOLLOWS_PER_PLATFORM} {label}s. "
            "Remove one before adding another."
        )

    await create_follow(
        cxn,
        guild_id=guild.id,
        platform=platform,
        username=stored,
        channel_id=channel.id,
        last_post_id=seed_id,
    )
    return False, ""


# ─────────────────────────────────────────
#  Add-follow modal
# ─────────────────────────────────────────

class AddFollowModal(Modal):
    def __init__(self, platform: str, guild: discord.Guild, default_channel: discord.TextChannel):
        meta = PLATFORMS[platform]
        super().__init__(title=f"Follow a {meta['label']}")
        self.platform        = platform
        self.guild           = guild
        self.default_channel = default_channel

        self.username_input = TextInput(
            label=meta["field_label"],
            placeholder=meta["field_placeholder"],
            max_length=100,
        )
        self.channel_input = TextInput(
            label="Notification Channel",
            placeholder="Leave blank to use this channel",
            required=False,
            max_length=100,
        )
        self.add_item(self.username_input)
        self.add_item(self.channel_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        raw = self.username_input.value.strip()

        channel_text = self.channel_input.value.strip()
        if channel_text:
            channel = _resolve_channel(self.guild, channel_text)
            if channel is None:
                await interaction.followup.send(
                    "Couldn't find that channel. Try a #mention or channel name.",
                    ephemeral=True,
                )
                return
        else:
            channel = self.default_channel

        # Show checking status
        checking = discord.ui.LayoutView()
        checking.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('loading')} Checking…"),
            discord.ui.TextDisplay(content=f"Verifying this account exists. One moment…"),
            accent_colour=discord.Colour(0xFEE75C),
        ))
        message = await interaction.followup.send(view=checking, ephemeral=True)

        ok, stored = await _validate(self.platform, raw)

        if not ok:
            meta = PLATFORMS[self.platform]
            fail = discord.ui.LayoutView()
            fail.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('cross')} Not Found"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=(
                        f"Could not find **{raw}** as a {meta['label']}.\n"
                        f"Double-check the name and try again."
                    )
                ),
                accent_colour=discord.Colour(0xED4245),
            ))
            # edit the ephemeral response
            await interaction.followup.edit_message(view=fail, message_id=message.id)
            return

        # Seed last_post_id so we don't notify for the current latest post
        seed_post = await _fetch(self.platform, stored)
        seed_id   = seed_post["id"] if seed_post else None

        moved, save_error = await _save_follow(
            interaction.client.cxn,
            guild=self.guild,
            platform=self.platform,
            stored=stored,
            channel=channel,
            seed_id=seed_id,
        )
        if save_error:
            limited = discord.ui.LayoutView()
            limited.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('cross')} Not Added"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=save_error),
                accent_colour=discord.Colour(0xED4245),
            ))
            await interaction.followup.edit_message(view=limited, message_id=message.id)
            return

        dname = _display(self.platform, stored)
        summary = (
            f"Now tracking **{dname}** on **{self.platform.capitalize()}**.\n"
            f"New posts will be announced in {channel.mention}."
        )
        if moved:
            summary = (
                f"**{dname}** was already followed, so it now posts in {channel.mention} "
                "instead of its previous channel."
            )
        success = discord.ui.LayoutView()
        success.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('tick')} Now Following"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=summary),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="-# Pause, ping a role, or write a custom message from the dashboard notifications tab."
            ),
            accent_colour=discord.Colour(0x57F287),
        ))
        await interaction.followup.edit_message(view=success, message_id=message.id)


# ─────────────────────────────────────────
#  Setup-panel buttons
# ─────────────────────────────────────────

class _AddFollowBtn(discord.ui.Button):
    def __init__(self, platform: str, guild: discord.Guild, channel: discord.TextChannel):
        meta = PLATFORMS[platform]
        super().__init__(
            label=meta["label"],
            style=meta["btn_style"],
            emoji=meta["icon"],
        )
        self.platform = platform
        self.guild    = guild
        self.channel  = channel

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} You need **Manage Server** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        await interaction.response.send_modal(
            AddFollowModal(self.platform, self.guild, self.channel)
        )


class _ViewFollowsBtn(discord.ui.Button):
    def __init__(self, guild_id: int):
        super().__init__(label="View Follows", style=discord.ButtonStyle.secondary, emoji="📋")
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} You need **Manage Server** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        follows = await list_follows(interaction.client.cxn, self.guild_id)
        view = _build_follows_list_view(interaction.guild, follows)
        await interaction.response.send_message(view=view, ephemeral=True)


# ─────────────────────────────────────────
#  Follow management selects
# ─────────────────────────────────────────

def _follow_option(row, *, verb: str) -> discord.SelectOption:
    platform = row["platform"]
    return discord.SelectOption(
        label=f"{row['display']} ({platform.capitalize()})",
        description=f"#{row['channel_id']} · {'paused' if not row['enabled'] else 'active'} · {verb}",
        value=f"{platform}:{row['username']}",
        emoji=PLATFORMS.get(platform, {}).get("icon", get_emoji("megaphone")),
    )


class _ToggleFollowSelect(discord.ui.Select):
    """Pause or resume follows straight from the Discord panel."""

    def __init__(self, guild_id: int, follows: list):
        self.guild_id = guild_id
        self.state = {f"{row['platform']}:{row['username']}": bool(row["enabled"]) for row in follows[:25]}
        options = [
            _follow_option(row, verb="pause it" if row["enabled"] else "resume it")
            for row in follows[:25]
        ]
        super().__init__(placeholder="Pause or resume an account…", options=options)

    async def callback(self, interaction: discord.Interaction):
        platform, username = self.values[0].split(":", 1)
        current = self.state.get(self.values[0], True)
        updated = await update_follow(
            interaction.client.cxn,
            guild_id=self.guild_id,
            platform=platform,
            username=username,
            enabled=not current,
        )
        if updated is None:
            return await interaction.response.send_message(
                f"{get_emoji('cross')} That account is no longer followed.", ephemeral=True
            )
        verb = "paused" if not updated["enabled"] else "active again"
        await interaction.response.send_message(
            f"{get_emoji('tick')} **{updated['display']}** is {verb}.", ephemeral=True
        )


class _RemoveFollowSelect(discord.ui.Select):
    def __init__(self, guild_id: int, follows: list):
        self.guild_id = guild_id
        super().__init__(
            placeholder="Select an account to unfollow…",
            options=[_follow_option(row, verb="remove it") for row in follows[:25]],
        )

    async def callback(self, interaction: discord.Interaction):
        platform, username = self.values[0].split(":", 1)
        removed = await delete_follow(
            interaction.client.cxn,
            guild_id=self.guild_id,
            platform=platform,
            username=username,
        )
        dname = _display(platform, username)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('tick') if removed else get_emoji('cross')} "
                f"{'Unfollowed' if removed else 'Already gone'}"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"Stopped tracking **{dname}** on **{platform.capitalize()}**."
                    if removed
                    else f"**{dname}** was not being followed any more."
                )
            ),
            accent_colour=discord.Colour(0x57F287),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


# ─────────────────────────────────────────
#  View builders
# ─────────────────────────────────────────

def _follow_channel(follow: dict) -> discord.TextChannel | None:
    """Resolve a follow's target channel, or ``None`` when it is gone."""
    guild = follow.get("guild")
    channel_id = follow.get("channel_id")
    if guild is None or not channel_id:
        return None
    return guild.get_channel(int(channel_id))


def _follow_summary(follows: list) -> str:
    """One-line health summary for the setup panel."""
    active = sum(1 for row in follows if row["enabled"])
    paused = len(follows) - active
    unhealthy = [row for row in follows if row["enabled"] and int(row["failures"] or 0) > 0]
    summary = f"**Currently tracking:** {active} active"
    if paused:
        summary += f" · {paused} paused"
    if unhealthy:
        summary += f"\n**Needs a look:** {len(unhealthy)} account(s) failed the last check"
    return summary


def build_setup_view(
    guild: discord.Guild,
    channel: discord.TextChannel,
    follows: list,
    prefix: str = ".",
) -> discord.ui.LayoutView:
    icons = " · ".join(m["icon"] for m in PLATFORMS.values())
    has_unhealthy = any(int(row["failures"] or 0) > 0 for row in follows)

    rows = [
        discord.ui.ActionRow(
            _AddFollowBtn("youtube",  guild, channel),
            _AddFollowBtn("twitch",   guild, channel),
            _AddFollowBtn("twitter",  guild, channel),
        ),
        discord.ui.ActionRow(
            _AddFollowBtn("tiktok",   guild, channel),
            _AddFollowBtn("bluesky",  guild, channel),
            _AddFollowBtn("reddit",   guild, channel),
        ),
        discord.ui.ActionRow(_ViewFollowsBtn(guild.id)),
    ]
    if has_unhealthy:
        rows.insert(0, discord.ui.ActionRow(_ToggleFollowSelect(guild.id, [row for row in follows if row["enabled"]])))

    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {get_emoji('megaphone')} Social Media Notifier"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                f"Get notified when your favourite creators post new content.\n"
                f"Supports: {icons}\n\n"
                f"{_follow_summary(follows)}"
            )
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        *rows,
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                f"-# You can also use `{prefix}follow <platform> <name> [#channel]`\n"
                f"-# Pause, ping a role, or write a custom message on the dashboard → Notifications"
            )
        ),
        accent_colour=discord.Colour(0x5865F2),
    ))
    return view


def _follow_line(guild: discord.Guild, follow: dict) -> str:
    """Render one followed account with its channel, state and health."""
    platform = follow["platform"]
    icon = PLATFORMS.get(platform, {}).get("icon", get_emoji("megaphone"))
    channel = guild.get_channel(int(follow["channel_id"])) if follow["channel_id"] else None
    ch_text = channel.mention if channel else f"<#{follow['channel_id']}>"
    parts = [f"{icon} **{follow['display']}** ({platform.capitalize()}) → {ch_text}"]
    if not follow["enabled"]:
        parts.append("⏸ paused")
    elif int(follow["failures"] or 0) > 0:
        parts.append(f"⚠️ {follow['failures']} failed check(s)")
    if follow["ping_role_id"]:
        parts.append(f"pings <@&{follow['ping_role_id']}>")
    if follow["template"]:
        parts.append("custom message")
    return " · ".join(parts)


def _build_follows_list_view(guild: discord.Guild, follows: list) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()

    if not follows:
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="### 📋 Followed Accounts"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="Nothing is being tracked yet. Open the setup panel to add accounts!"
            ),
            accent_colour=discord.Colour(0x5865F2),
        ))
        return view

    items: list = [
        discord.ui.TextDisplay(content="### 📋 Followed Accounts"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="\n".join(_follow_line(guild, follow) for follow in follows)),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="-# Pause or resume an account below, or remove it entirely."),
        discord.ui.ActionRow(_ToggleFollowSelect(guild.id, follows)),
        discord.ui.ActionRow(_RemoveFollowSelect(guild.id, follows)),
    ]
    view.add_item(discord.ui.Container(*items, accent_colour=discord.Colour(0x5865F2)))
    return view


# ─────────────────────────────────────────
#  Notifier Cog
# ─────────────────────────────────────────

class Notifier(commands.Cog):
    #: Seconds to wait between consecutive announcements in one poll.
    send_pacing = 0.5

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_posts.start()

    def cog_unload(self):
        self.check_posts.cancel()

    # ── Official staff notification channel ───────────────────────────────

    @commands.hybrid_command(name="notification-channel")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def notification_channel(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel | None = None,
    ):
        """Choose where official Niko staff broadcasts are delivered."""
        if ctx.interaction is not None:
            await ctx.defer(ephemeral=True)
        channel = channel or ctx.channel
        await self.bot.cxn.execute(
            "INSERT OR REPLACE INTO notification_channels (guild_id, channel_id, updated_at) "
            "VALUES ($1, $2, datetime('now'))",
            ctx.guild.id,
            channel.id,
        )
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('tick')} Notifications configured"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"Official staff announcements will now be posted in {channel.mention}.\n"
                    "You can run this command again to move them."
                )
            ),
            accent_colour=discord.Colour(0x57F287),
        ))
        await ctx.send(view=view)

    # ── Command group ─────────────────────

    @commands.group(name="notifier", aliases=["notify"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def notifier(self, ctx: commands.Context):
        """Open the social media notifier setup panel."""
        prefix  = self.bot.command_prefix if isinstance(self.bot.command_prefix, str) else "."
        follows = await list_follows(self.bot.cxn, ctx.guild.id)
        view = build_setup_view(ctx.guild, ctx.channel, follows, prefix)
        await ctx.send(view=view)

    @notifier.command(name="list")
    @commands.has_permissions(manage_guild=True)
    async def notifier_list(self, ctx: commands.Context):
        """List all followed accounts for this server."""
        follows = await list_follows(self.bot.cxn, ctx.guild.id)
        view = _build_follows_list_view(ctx.guild, follows)
        await ctx.send(view=view)

    @notifier.command(name="pause")
    @commands.has_permissions(manage_guild=True)
    async def notifier_pause(self, ctx: commands.Context, platform: str, *, query: str):
        """Pause announcements for one followed account."""
        await self._set_follow_state(ctx, platform, query, enabled=False)

    @notifier.command(name="resume")
    @commands.has_permissions(manage_guild=True)
    async def notifier_resume(self, ctx: commands.Context, platform: str, *, query: str):
        """Resume announcements for one paused account."""
        await self._set_follow_state(ctx, platform, query, enabled=True)

    async def _set_follow_state(
        self, ctx: commands.Context, platform: str, query: str, *, enabled: bool
    ) -> None:
        """Shared implementation for the pause/resume subcommands."""
        platform = platform.lower()
        if platform not in PLATFORMS:
            return await ctx.send(
                f"Unknown platform. Valid options: `{'`, `'.join(ALL_PLATFORMS)}`"
            )
        follows = await list_follows(self.bot.cxn, ctx.guild.id)
        needle = query.strip().lstrip("@").lower()
        target = next(
            (
                row for row in follows
                if row["platform"] == platform
                and needle in (
                    row["username"].lower(),
                    row["display"].lower().lstrip("@r/"),
                )
            ),
            None,
        )
        if target is None:
            return await ctx.send(
                f"{get_emoji('cross')} No follow found for **{query}** on "
                f"**{platform.capitalize()}**. Try `{ctx.clean_prefix}notifier list`."
            )
        updated = await update_follow(
            self.bot.cxn,
            guild_id=ctx.guild.id,
            platform=platform,
            username=target["username"],
            enabled=enabled,
        )
        state = "active again" if enabled else "paused"
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('tick')} {state.capitalize()}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"**{updated['display'] if updated else target['display']}** on "
                    f"**{platform.capitalize()}** is {state}."
                )
            ),
            accent_colour=discord.Colour(0x57F287),
        ))
        await ctx.send(view=view)

    @notifier.command(name="test")
    @commands.has_permissions(manage_guild=True)
    async def notifier_test(self, ctx: commands.Context, platform: str, *, query: str):
        """Test-fetch a platform account to verify it works."""
        platform = platform.lower()
        if platform not in PLATFORMS:
            return await ctx.send(
                f"Unknown platform. Valid options: `{'`, `'.join(ALL_PLATFORMS)}`"
            )

        status = discord.ui.LayoutView()
        status.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### ⏳ Testing…"),
            discord.ui.TextDisplay(content=f"Fetching from **{platform}** for `{query}`…"),
            accent_colour=discord.Colour(0xFEE75C),
        ))
        msg = await ctx.send(view=status)

        ok, stored = await _validate(platform, query)
        if not ok:
            fail = discord.ui.LayoutView()
            fail.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('cross')} Account Not Found"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"Could not validate **{query}** on **{platform.capitalize()}**."
                ),
                accent_colour=discord.Colour(0xED4245),
            ))
            await msg.edit(view=fail)
            return

        post = await _fetch(platform, stored)
        if not post:
            fail = discord.ui.LayoutView()
            fail.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('danger')} No Posts Found"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"Account found but couldn't retrieve any posts for **{stored}**."
                ),
                accent_colour=discord.Colour(0xFEE75C),
            ))
            await msg.edit(view=fail)
            return

        dname   = _display(platform, stored)
        preview = (post.get("text") or post.get("title") or "")[:200]
        result  = discord.ui.LayoutView()
        result.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('tick')} Fetch Successful — {dname}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"**Latest:** {preview}\n**Link:** {post['url']}"
            ),
            accent_colour=discord.Colour(0x57F287),
        ))
        await msg.edit(view=result)

    # ── Shortcut commands ─────────────────

    @commands.command(name="follow")
    @commands.has_permissions(manage_guild=True)
    async def follow(
        self,
        ctx: commands.Context,
        platform: str,
        username: str,
        channel: discord.TextChannel = None,
    ):
        """Follow a social media account. Platforms: youtube twitch twitter tiktok bluesky reddit"""
        platform = platform.lower()
        if platform not in PLATFORMS:
            return await ctx.reply(
                f"Unknown platform. Valid options: `{'`, `'.join(ALL_PLATFORMS)}`"
            )

        channel = channel or ctx.channel

        status = discord.ui.LayoutView()
        status.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('loading')} Checking…"),
            discord.ui.TextDisplay(content="Validating the account, one moment…"),
            accent_colour=discord.Colour(0xFEE75C),
        ))
        msg = await ctx.send(view=status)

        ok, stored = await _validate(platform, username)
        if not ok:
            fail = discord.ui.LayoutView()
            fail.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('cross')} Not Found"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"Could not find **{username}** on **{platform.capitalize()}**."
                ),
                accent_colour=discord.Colour(0xED4245),
            ))
            await msg.edit(view=fail)
            return

        # Seed last_post_id
        seed_post = await _fetch(platform, stored)
        seed_id   = seed_post["id"] if seed_post else None

        moved, save_error = await _save_follow(
            self.bot.cxn,
            guild=ctx.guild,
            platform=platform,
            stored=stored,
            channel=channel,
            seed_id=seed_id,
        )
        if save_error:
            fail = discord.ui.LayoutView()
            fail.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('cross')} Not Added"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=save_error),
                accent_colour=discord.Colour(0xED4245),
            ))
            await msg.edit(view=fail)
            return

        dname   = _display(platform, stored)
        success = discord.ui.LayoutView()
        success.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('tick')} Now Following"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"**{dname}** was already followed, now posting in {channel.mention}."
                    if moved
                    else f"Now tracking **{dname}** on **{platform.capitalize()}**.\n"
                    f"New posts → {channel.mention}"
                )
            ),
            accent_colour=discord.Colour(0x57F287),
        ))
        await msg.edit(view=success)

    @commands.command(name="unfollow")
    @commands.has_permissions(manage_guild=True)
    async def unfollow(self, ctx: commands.Context, platform: str, *, username: str):
        """Stop tracking a social media account."""
        platform = platform.lower()
        # Match exactly first (including the stored YouTube format), then by the
        # friendly display name so people can use what they see in the panel.
        rows = [row for row in await list_follows(self.bot.cxn, ctx.guild.id) if row["platform"] == platform]
        target = None
        needle = username.strip().lstrip("@").lower()
        for row in rows:
            stored = row["username"]
            dname  = row["display"].lower().lstrip("@r/")
            if needle == stored.lower() or needle == dname:
                target = stored
                break

        if target is None:
            fail = discord.ui.LayoutView()
            fail.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('cross')} Not Found"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"No follow found for **{username}** on **{platform.capitalize()}**."
                ),
                accent_colour=discord.Colour(0xED4245),
            ))
            await ctx.send(view=fail)
            return

        await delete_follow(
            self.bot.cxn,
            guild_id=ctx.guild.id,
            platform=platform,
            username=target,
        )
        dname = _display(platform, target)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('tick')} Unfollowed"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"Stopped tracking **{dname}** on **{platform.capitalize()}**."
            ),
            accent_colour=discord.Colour(0x57F287),
        ))
        await ctx.send(view=view)

    # ── Background polling task ───────────

    async def _repair_youtube_username(self, follow: dict) -> str:
        """Fix stale YouTube display names (e.g. "Home" or a bare channel ID)."""
        from utils.social.youtube import _parse_stored

        username = follow["username"]
        display, _ = _parse_stored(username)
        if "|" in username and display and display != "Home":
            return username
        ok, corrected = await _validate("youtube", username)
        if not ok or corrected == username:
            return username
        renamed = await rename_follow(
            self.bot.cxn,
            guild_id=follow["guild_id"],
            platform="youtube",
            username=username,
            new_username=corrected,
        )
        return corrected if renamed else username

    async def _record_failure(self, follow: dict, checked_at: str) -> None:
        """Track a failed check and pause the follow once it keeps failing.

        Without this an account a platform keeps refusing (deleted channel,
        renamed handle, blocked IP) is retried every cycle forever with no
        signal to the server that its feed has gone quiet.
        """
        cxn = self.bot.cxn
        failures = int(follow["failures"] or 0) + 1
        await record_check(
            cxn,
            guild_id=follow["guild_id"],
            platform=follow["platform"],
            username=follow["username"],
            failures=failures,
            last_checked_at=checked_at,
        )
        if failures < FAILURE_LIMIT:
            return

        await update_follow(
            cxn,
            guild_id=follow["guild_id"],
            platform=follow["platform"],
            username=follow["username"],
            enabled=False,
            failures=failures,
            last_checked_at=checked_at,
        )
        channel = _follow_channel(follow)
        if channel is None:
            return
        notice = discord.ui.LayoutView()
        notice.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('danger')} Paused {follow['display']}"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"Niko could not read **{follow['display']}** "
                    f"({follow['platform'].capitalize()}) for {FAILURE_LIMIT} checks in a row, "
                    "so this follow is paused to stop pointless requests.\n"
                    f"Use `/notifier resume {follow['platform']} {follow['display'].lstrip('@')}` "
                    "once it is reachable again."
                )
            ),
            accent_colour=discord.Colour(0xFEE75C),
        ))
        try:
            await channel.send(view=notice)
        except Exception:
            pass

    async def _deliver(self, follow: dict, post: dict, checked_at: str) -> bool:
        """Announce one post to one follow and store the new post id.

        Returns ``True`` only when something was actually posted, so the caller
        can pace real sends without waiting on bookkeeping.
        """
        cxn = self.bot.cxn
        platform = follow["platform"]
        username = follow["username"]
        post_id = post.get("id")
        if not post_id:
            return False

        async def remember(post_id=post_id) -> None:
            await update_follow(
                cxn,
                guild_id=follow["guild_id"],
                platform=platform,
                username=username,
                last_post_id=post_id,
                failures=0,
                last_checked_at=checked_at,
            )

        # First sight of an account: remember its newest post silently so a new
        # follow never dumps the whole back catalogue into the channel.
        if follow["last_post_id"] is None:
            await remember()
            return False
        if post_id == follow["last_post_id"]:
            await remember()
            return False

        channel = _follow_channel(follow)
        if channel is None:
            return False

        role = None
        if follow["ping_role_id"]:
            role = follow["guild"].get_role(int(follow["ping_role_id"]))
        content, allowed_mentions = build_notification_content(
            platform=platform,
            username=username,
            post=post,
            template=follow["template"],
            role=role,
        )
        try:
            await channel.send(
                content=content,
                view=build_notification_view(platform, username, post),
                allowed_mentions=allowed_mentions,
            )
        except Exception:
            return False  # missing permissions — keep the old id so it retries later
        await remember()
        return True

    @tasks.loop(minutes=5)
    async def check_posts(self):
        await self.poll_once()

    async def poll_once(self):
        """One full poll cycle, split out so it can be tested without a gateway."""
        cxn = getattr(self.bot, "cxn", None)
        if cxn is None:
            return
        try:
            follows = await list_follows(cxn)
            configs = {
                guild_id: await get_notifier_config(cxn, guild_id)
                for guild_id in {follow["guild_id"] for follow in follows}
            }
        except Exception:
            return

        queue: list[dict] = []
        for follow in follows:
            if not follow["enabled"]:
                continue
            # A server can switch the whole notifier off from the dashboard.
            if (configs.get(follow["guild_id"]) or {}).get("enabled") is False:
                continue
            guild = self.bot.get_guild(int(follow["guild_id"]))
            if guild is None:
                continue
            follow["guild"] = guild
            if follow["platform"] == "youtube":
                follow["username"] = await self._repair_youtube_username(follow)
            queue.append(follow)

        if not queue:
            return

        # Several servers often follow the same creator, and one poll should
        # never send the same request twice.
        accounts: dict[tuple[str, str], list[dict]] = {}
        for follow in queue:
            accounts.setdefault((follow["platform"], follow["username"]), []).append(follow)

        semaphore = asyncio.Semaphore(FETCH_CONCURRENCY)

        async def fetch_account(account: tuple[str, str]) -> dict | None:
            async with semaphore:
                return await _fetch(account[0], account[1])

        posts = await asyncio.gather(*(fetch_account(account) for account in accounts))
        checked_at = utc_now()

        for (platform, username), post in zip(accounts, posts):
            for follow in accounts[(platform, username)]:
                follow["platform"] = platform
                try:
                    posted = await self._deliver(follow, post, checked_at) if post else False
                    if post is None:
                        await self._record_failure(follow, checked_at)
                except Exception:
                    continue
                # Brief pause between real sends, never on pure bookkeeping.
                if posted:
                    await asyncio.sleep(self.send_pacing)

    @check_posts.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Notifier(bot))
