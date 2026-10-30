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
from utils.blacklist_manager import BlacklistManager
from utils.command_locales import command_texts
from utils.i18n import make_flat_msg
from utils.locales import load_locales
from utils.prefix_manager import resolve_prefix

CMDS = command_texts(__package__)
MESSAGES = load_locales(__package__, "messages")
msg = make_flat_msg(MESSAGES, {
    "tick": get_emoji("tick"),
    "cross": get_emoji("cross"),
    "loading": get_emoji("loading"),
    "danger": get_emoji("danger"),
    "megaphone": get_emoji("megaphone"),
    "link": get_emoji("link"),
})
from utils.social.youtube import (
    fetch_latest_youtube,
    validate_youtube_channel,
    channel_exists as youtube_channel_exists,
    make_stored,
    display_name as yt_display,
    channel_id_of,
)
from utils.social.twitch import (
    fetch_latest_twitch,
    normalize_login as twitch_login,
    validate_twitch_login,
    channel_exists as twitch_channel_exists,
    credentials_configured as twitch_configured,
)
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


async def account_exists(platform: str, username: str) -> bool:
    """Whether the platform still knows this account, posts or not.

    A channel with no uploads, or one that is simply offline with no videos to
    show, is healthy — only an account the platform reports as gone is a failed
    check. Without this distinction every quiet channel is paused after a few
    polls, which is exactly the "random" pausing servers saw on YouTube and
    Twitch.
    """
    try:
        if platform == "youtube":
            return await youtube_channel_exists(username)
        if platform == "twitch":
            # Helix access is synchronous, like the fetcher that uses it.
            return await asyncio.to_thread(twitch_channel_exists, username)
        ok, _ = await _validate(platform, username)
        return ok
    except Exception:
        # An unanswerable check is no evidence the account is gone.
        return True


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


def validation_hint(platform: str) -> str:
    """Explain a verification failure that is about configuration, not input.

    Twitch is the one platform with app credentials, and without them no login
    can ever be confirmed. Saying so beats "could not find" for an account the
    owner knows exists.
    """
    if platform == "twitch" and not twitch_configured():
        return msg("en", "twitch_hint")
    return ""


def _t(locale, key: str, **kwargs) -> str:
    """Translated string for a guild, interaction or context.

    Accepts anything :func:`utils.i18n.get_lang` understands (a context, an
    interaction, a guild) so views built away from a command still follow the
    server's language. ``None`` yields English.
    """
    return msg(locale, key, **kwargs)


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
    *,
    locale=None,
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
        header = _t(locale, "notif_youtube_title", icon=icon)
        body   = _t(locale, "notif_youtube_body", name=dname)
    elif platform == "twitch":
        if str(post.get("id", "")).startswith("stream:"):
            header = _t(locale, "notif_twitch_stream_title", icon=icon)
            body   = _t(locale, "notif_twitch_stream_body", name=dname)
        else:
            header = _t(locale, "notif_twitch_broadcast_title", icon=icon)
            body   = _t(locale, "notif_twitch_broadcast_body", name=dname)
    elif platform == "twitter":
        header = _t(locale, "notif_twitter_title", icon=icon)
        body   = _t(locale, "notif_twitter_body", name=dname)
    elif platform == "tiktok":
        header = _t(locale, "notif_tiktok_title", icon=icon)
        body   = _t(locale, "notif_tiktok_body", name=dname)
    elif platform == "bluesky":
        header = _t(locale, "notif_bluesky_title", icon=icon)
        body   = _t(locale, "notif_bluesky_body", name=dname)
    elif platform == "reddit":
        header = _t(locale, "notif_reddit_title", icon=icon, name=dname)
        body   = ""
    else:
        header = _t(locale, "notif_generic_title", icon=icon)
        body   = _t(locale, "notif_generic_body", name=dname)

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

    link_key = "notif_link_video" if platform == "youtube" else "notif_link_post"
    body += "\n\n" + _t(locale, link_key, url=url)

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
        return False, msg(guild, "limit_guild", max=MAX_FOLLOWS_PER_GUILD)
    same_platform = sum(1 for follow in follows if follow["platform"] == platform)
    if same_platform >= MAX_FOLLOWS_PER_PLATFORM:
        label = PLATFORMS.get(platform, {}).get("label", platform.capitalize())
        return False, msg(
            guild, "limit_platform", max=MAX_FOLLOWS_PER_PLATFORM, label=label
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
        super().__init__(title=msg(guild, "modal_title", label=meta["label"]))
        self.platform        = platform
        self.guild           = guild
        self.default_channel = default_channel

        self.username_input = TextInput(
            label=meta["field_label"],
            placeholder=meta["field_placeholder"],
            max_length=100,
        )
        self.channel_input = TextInput(
            label=msg(guild, "modal_channel_label"),
            placeholder=msg(guild, "modal_channel_placeholder"),
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
                    msg(interaction, "channel_not_found"),
                    ephemeral=True,
                )
                return
        else:
            channel = self.default_channel

        # Show checking status
        checking = discord.ui.LayoutView()
        checking.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(self.guild, "checking_title")),
            discord.ui.TextDisplay(content=msg(self.guild, "checking_body")),
            accent_colour=discord.Colour(0xFEE75C),
        ))
        message = await interaction.followup.send(view=checking, ephemeral=True)

        ok, stored = await _validate(self.platform, raw)

        if not ok:
            meta = PLATFORMS[self.platform]
            fail = discord.ui.LayoutView()
            fail.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=msg(self.guild, "not_found_title")),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=(
                        msg(self.guild, "not_found_as", query=raw, label=meta["label"])
                        + "\n"
                        + (validation_hint(self.platform) or msg(self.guild, "not_found_hint"))
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
                discord.ui.TextDisplay(content=msg(self.guild, "not_added_title")),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=save_error),
                accent_colour=discord.Colour(0xED4245),
            ))
            await interaction.followup.edit_message(view=limited, message_id=message.id)
            return

        dname = _display(self.platform, stored)
        if moved:
            summary = msg(
                self.guild,
                "moved_body",
                name=dname,
                channel=channel.mention,
            )
        else:
            summary = msg(
                self.guild,
                "added_body",
                name=dname,
                platform=self.platform.capitalize(),
                channel=channel.mention,
            )
        success = discord.ui.LayoutView()
        success.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(self.guild, "added_title")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=summary),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=msg(self.guild, "added_footer")),
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
                discord.ui.TextDisplay(content=msg(interaction, "need_permission")),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        await interaction.response.send_modal(
            AddFollowModal(self.platform, self.guild, self.channel)
        )


class _ViewFollowsBtn(discord.ui.Button):
    def __init__(self, guild_id: int, label: str):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, emoji="📋")
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=msg(interaction, "need_permission")),
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

def _follow_option(row, *, verb: str, locale=None) -> discord.SelectOption:
    platform = row["platform"]
    state = msg(locale, "state_active" if row["enabled"] else "state_paused")
    return discord.SelectOption(
        label=f"{row['display']} ({platform.capitalize()})",
        description=msg(
            locale, "option_body", channel=row["channel_id"], state=state, verb=verb
        ),
        value=f"{platform}:{row['username']}",
        emoji=PLATFORMS.get(platform, {}).get("icon", get_emoji("megaphone")),
    )


class _ToggleFollowSelect(discord.ui.Select):
    """Pause or resume follows straight from the Discord panel."""

    def __init__(self, guild_id: int, follows: list, *, locale=None):
        self.guild_id = guild_id
        self.locale = locale
        self.state = {f"{row['platform']}:{row['username']}": bool(row["enabled"]) for row in follows[:25]}
        options = [
            _follow_option(
                row,
                verb=msg(locale, "verb_pause" if row["enabled"] else "verb_resume"),
                locale=locale,
            )
            for row in follows[:25]
        ]
        super().__init__(placeholder=msg(locale, "toggle_placeholder"), options=options)

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
                msg(interaction, "toggle_gone"), ephemeral=True
            )
        state = msg(interaction, "word_active_again" if updated["enabled"] else "word_paused")
        await interaction.response.send_message(
            msg(interaction, "toggle_changed", name=updated["display"], state=state),
            ephemeral=True,
        )


class _RemoveFollowSelect(discord.ui.Select):
    def __init__(self, guild_id: int, follows: list, *, locale=None):
        self.guild_id = guild_id
        super().__init__(
            placeholder=msg(locale, "remove_placeholder"),
            options=[
                _follow_option(row, verb=msg(locale, "verb_remove"), locale=locale)
                for row in follows[:25]
            ],
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
        if removed:
            title = msg(interaction, "removed_title")
            body = msg(
                interaction, "removed_body", name=dname, platform=platform.capitalize()
            )
        else:
            title = msg(interaction, "already_gone_title")
            body = msg(interaction, "already_gone_body", name=dname)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=title),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=body),
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


def _follow_summary(follows: list, locale=None) -> str:
    """One-line health summary for the setup panel."""
    active = sum(1 for row in follows if row["enabled"])
    paused = len(follows) - active
    unhealthy = [row for row in follows if row["enabled"] and int(row["failures"] or 0) > 0]
    summary = msg(locale, "summary_active", count=active)
    if paused:
        summary += msg(locale, "summary_paused", count=paused)
    if unhealthy:
        summary += msg(locale, "summary_unhealthy", count=len(unhealthy))
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
        discord.ui.ActionRow(_ViewFollowsBtn(guild.id, msg(guild, "btn_view_follows"))),
    ]
    if has_unhealthy:
        rows.insert(0, discord.ui.ActionRow(_ToggleFollowSelect(
            guild.id,
            [row for row in follows if row["enabled"]],
            locale=guild,
        )))

    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=msg(guild, "panel_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                msg(guild, "panel_body", icons=icons)
                + "\n\n"
                + _follow_summary(follows, guild)
            )
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        *rows,
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                msg(guild, "panel_footer_command", prefix=prefix)
                + "\n"
                + msg(guild, "panel_footer_dashboard")
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
    parts = [msg(
        guild,
        "line_main",
        icon=icon,
        name=follow["display"],
        platform=platform.capitalize(),
        channel=ch_text,
    )]
    if not follow["enabled"]:
        parts.append(msg(guild, "line_paused"))
    elif int(follow["failures"] or 0) > 0:
        parts.append(msg(guild, "line_failures", count=follow["failures"]))
    if follow["ping_role_id"]:
        parts.append(msg(guild, "line_pings", role_id=follow["ping_role_id"]))
    if follow["template"]:
        parts.append(msg(guild, "line_custom"))
    return " · ".join(parts)


def _build_follows_list_view(guild: discord.Guild, follows: list) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()

    if not follows:
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(guild, "list_title")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=msg(guild, "list_empty")),
            accent_colour=discord.Colour(0x5865F2),
        ))
        return view

    items: list = [
        discord.ui.TextDisplay(content=msg(guild, "list_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="\n".join(_follow_line(guild, follow) for follow in follows)),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(guild, "list_footer")),
        discord.ui.ActionRow(_ToggleFollowSelect(guild.id, follows, locale=guild)),
        discord.ui.ActionRow(_RemoveFollowSelect(guild.id, follows, locale=guild)),
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

    @commands.hybrid_command(
        name="notification-channel",
        help=CMDS.help("notification-channel"),
        description=CMDS.text("notification-channel.description"),
    )
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
            discord.ui.TextDisplay(content=msg(ctx, "channel_title")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=msg(ctx, "channel_body", channel=channel.mention)
            ),
            accent_colour=discord.Colour(0x57F287),
        ))
        await ctx.send(view=view)

    # ── Command group ─────────────────────

    @commands.group(
        name="notifier",
        aliases=["notify"],
        invoke_without_command=True,
        help=CMDS.help("notifier"),
    )
    @commands.has_permissions(manage_guild=True)
    async def notifier(self, ctx: commands.Context):
        """Open the social media notifier setup panel."""
        prefix  = await resolve_prefix(self.bot, ctx)
        follows = await list_follows(self.bot.cxn, ctx.guild.id)
        view = build_setup_view(ctx.guild, ctx.channel, follows, prefix)
        await ctx.send(view=view)

    @notifier.command(name="list", help=CMDS.help("notifier.list"))
    @commands.has_permissions(manage_guild=True)
    async def notifier_list(self, ctx: commands.Context):
        """List all followed accounts for this server."""
        follows = await list_follows(self.bot.cxn, ctx.guild.id)
        view = _build_follows_list_view(ctx.guild, follows)
        await ctx.send(view=view)

    @notifier.command(name="pause", help=CMDS.help("notifier.pause"))
    @commands.has_permissions(manage_guild=True)
    async def notifier_pause(self, ctx: commands.Context, platform: str, *, query: str):
        """Pause announcements for one followed account."""
        await self._set_follow_state(ctx, platform, query, enabled=False)

    @notifier.command(name="resume", help=CMDS.help("notifier.resume"))
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
                msg(ctx, "unknown_platform", options="`, `".join(ALL_PLATFORMS))
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
                msg(
                    ctx,
                    "no_follow",
                    query=query,
                    platform=platform.capitalize(),
                    prefix=ctx.clean_prefix,
                )
            )
        updated = await update_follow(
            self.bot.cxn,
            guild_id=ctx.guild.id,
            platform=platform,
            username=target["username"],
            enabled=enabled,
        )
        state = msg(ctx, "word_active_again" if enabled else "word_paused")
        title = msg(ctx, "state_active_title" if enabled else "state_paused_title")
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "state_title", state=title)),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=msg(
                    ctx,
                    "state_body",
                    name=updated["display"] if updated else target["display"],
                    platform=platform.capitalize(),
                    state=state,
                )
            ),
            accent_colour=discord.Colour(0x57F287),
        ))
        await ctx.send(view=view)

    @notifier.command(name="test", help=CMDS.help("notifier.test"))
    @commands.has_permissions(manage_guild=True)
    async def notifier_test(self, ctx: commands.Context, platform: str, *, query: str):
        """Test-fetch a platform account to verify it works."""
        platform = platform.lower()
        if platform not in PLATFORMS:
            return await ctx.send(
                msg(ctx, "unknown_platform", options="`, `".join(ALL_PLATFORMS))
            )

        status = discord.ui.LayoutView()
        status.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "testing_title")),
            discord.ui.TextDisplay(
                content=msg(ctx, "testing_body", platform=platform, query=query)
            ),
            accent_colour=discord.Colour(0xFEE75C),
        ))
        status_msg = await ctx.send(view=status)

        ok, stored = await _validate(platform, query)
        if not ok:
            hint = validation_hint(platform)
            fail = discord.ui.LayoutView()
            fail.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=msg(ctx, "account_not_found_title")),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=(
                        msg(
                            ctx,
                            "account_not_found_body",
                            query=query,
                            platform=platform.capitalize(),
                        )
                        + (f"\n{hint}" if hint else "")
                    )
                ),
                accent_colour=discord.Colour(0xED4245),
            ))
            await status_msg.edit(view=fail)
            return

        post = await _fetch(platform, stored)
        if not post:
            # The account itself is fine, there is just nothing to announce yet
            # (no uploads, or offline with no VODs). That is not a failure.
            quiet = discord.ui.LayoutView()
            quiet.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=msg(ctx, "verified_title")),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=msg(ctx, "verified_body", name=_display(platform, stored))
                ),
                accent_colour=discord.Colour(0x57F287),
            ))
            await status_msg.edit(view=quiet)
            return

        dname   = _display(platform, stored)
        preview = (post.get("text") or post.get("title") or "")[:200]
        result  = discord.ui.LayoutView()
        result.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "fetch_title", name=dname)),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=msg(ctx, "fetch_body", preview=preview, url=post["url"])
            ),
            accent_colour=discord.Colour(0x57F287),
        ))
        await status_msg.edit(view=result)

    # ── Shortcut commands ─────────────────

    @commands.command(name="follow", help=CMDS.help("follow"))
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
                msg(ctx, "unknown_platform", options="`, `".join(ALL_PLATFORMS))
            )

        channel = channel or ctx.channel

        status = discord.ui.LayoutView()
        status.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "checking_title")),
            discord.ui.TextDisplay(content=msg(ctx, "validating_body")),
            accent_colour=discord.Colour(0xFEE75C),
        ))
        status_msg = await ctx.send(view=status)
        ok, stored = await _validate(platform, username)
        if not ok:
            hint = validation_hint(platform)
            fail = discord.ui.LayoutView()
            fail.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=msg(ctx, "not_found_title")),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=(
                        msg(
                            ctx,
                            "not_found_on",
                            query=username,
                            platform=platform.capitalize(),
                        )
                        + (f"\n{hint}" if hint else "")
                    )
                ),
                accent_colour=discord.Colour(0xED4245),
            ))
            await status_msg.edit(view=fail)
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
                discord.ui.TextDisplay(content=msg(ctx, "not_added_title")),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=save_error),
                accent_colour=discord.Colour(0xED4245),
            ))
            await status_msg.edit(view=fail)
            return

        dname = _display(platform, stored)
        if moved:
            summary = msg(ctx, "moved_body_short", name=dname, channel=channel.mention)
        else:
            summary = msg(
                ctx,
                "added_body_short",
                name=dname,
                platform=platform.capitalize(),
                channel=channel.mention,
            )
        success = discord.ui.LayoutView()
        success.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "added_title")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=summary),
            accent_colour=discord.Colour(0x57F287),
        ))
        await status_msg.edit(view=success)

    @commands.command(name="unfollow", help=CMDS.help("unfollow"))
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
                discord.ui.TextDisplay(content=msg(ctx, "not_found_title")),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=msg(
                        ctx,
                        "no_follow_plain",
                        query=username,
                        platform=platform.capitalize(),
                    )
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
            discord.ui.TextDisplay(content=msg(ctx, "removed_title")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=msg(
                    ctx, "removed_body", name=dname, platform=platform.capitalize()
                )
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

    async def _record_success(self, follow: dict, checked_at: str) -> None:
        """Mark a check as healthy and clear any failures it had collected.

        A stale count is what made a resumed follow pause again on its first
        hiccup and kept the dashboard warning about an account that had been
        readable for days.
        """
        await record_check(
            self.bot.cxn,
            guild_id=follow["guild_id"],
            platform=follow["platform"],
            username=follow["username"],
            failures=0,
            last_checked_at=checked_at,
        )

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
        locale = follow.get("guild") or getattr(channel, "guild", None)
        notice = discord.ui.LayoutView()
        notice.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(locale, "autopause_title", name=follow["display"])
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=msg(
                    locale,
                    "autopause_body",
                    name=follow["display"],
                    platform=follow["platform"].capitalize(),
                    limit=FAILURE_LIMIT,
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
            await self._record_success(follow, checked_at)
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
            # The account was read fine; only the announcement channel is gone.
            # That is a server-side problem, not a failed check on the account.
            await self._record_success(follow, checked_at)
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
                view=build_notification_view(
                    platform, username, post, locale=follow["guild"]
                ),
                allowed_mentions=allowed_mentions,
            )
        except Exception:
            # Missing permissions or a Discord outage: keep the old id so it
            # retries later, but do not blame the account for it.
            await self._record_success(follow, checked_at)
            return False
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

        # A blacklisted server is cut off from Niko, so it must not receive
        # announcements either — its own switch may still read "on" from before
        # the blacklist was applied.
        blacklist = BlacklistManager()

        queue: list[dict] = []
        for follow in follows:
            if not follow["enabled"]:
                continue
            # A server can switch the whole notifier off from the dashboard.
            if (configs.get(follow["guild_id"]) or {}).get("enabled") is False:
                continue
            if blacklist.is_guild_blacklisted(int(follow["guild_id"])):
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
                    if post is None:
                        # Nothing new to announce is not a failure. Confirm the
                        # account itself still exists; only then is a check lost.
                        if await account_exists(platform, username):
                            await self._record_success(follow, checked_at)
                        else:
                            await self._record_failure(follow, checked_at)
                        continue
                    posted = await self._deliver(follow, post, checked_at)
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
