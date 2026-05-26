"""
Social Media Notifier
─────────────────────
Tracks new posts / videos / uploads from:
  • YouTube   (RSS feed — channel ID or @handle)
  • Twitter/X (Nitter scraping — concurrent instance check)
  • TikTok    (web scraping)
  • Bluesky   (AT Protocol public API)
  • Reddit    (Reddit JSON API — subreddits)

All notifications use Discord cv2 containers.
YouTube and Reddit notifications include a thumbnail preview.
"""

import asyncio
import discord
from discord import MediaGalleryItem, UnfurledMediaItem
from discord.ext import commands, tasks
from discord.ui import Modal, TextInput

from config.emojis import get_emoji
from utils.youtube  import fetch_latest_youtube, validate_youtube_channel, make_stored, display_name as yt_display, channel_id_of
from utils.twitter  import fetch_latest_tweet, validate_twitter_username
from utils.tiktok   import fetch_latest_tiktok, validate_tiktok_username
from utils.bluesky  import fetch_latest_bluesky, validate_bluesky_handle
from utils.reddit   import fetch_latest_reddit, validate_reddit

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
        "icon":    "🦋",
        "color":   discord.Colour(0x0085FF),
        "label":   "Bluesky Account",
        "btn_style": discord.ButtonStyle.primary,
        "field_label": "@Handle",
        "field_placeholder": "bsky.bsky.team",
    },
    "reddit": {
        "icon":    "🟠",
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
#  Display helpers
# ─────────────────────────────────────────

def _display(platform: str, username: str) -> str:
    """Human-readable name for a follow entry."""
    if platform == "youtube":
        return yt_display(username)
    if platform == "reddit":
        return f"r/{username}"
    return f"@{username}"


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
    icon      = meta.get("icon", get_emoji("icon_megaphone"))
    color     = meta.get("color", discord.Colour(0x5865F2))
    dname     = _display(platform, username)
    url       = post.get("url", "")
    text      = post.get("text") or post.get("title") or ""
    thumbnail = post.get("thumbnail")

    # Header line
    if platform == "youtube":
        header = f"### {icon} New YouTube Video"
        body   = f"**{dname}** just uploaded a new video!"
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
        if body:
            body += f"\n\n> {preview}"
        else:
            body = f"> {preview}"

    body += f"\n\n{get_emoji('icon_link')} [View{'  Video' if platform == 'youtube' else ' Post'}]({url})"

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
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_loading')} Checking…"),
            discord.ui.TextDisplay(content=f"Verifying this account exists. One moment…"),
            accent_colour=discord.Colour(0xFEE75C),
        ))
        message = await interaction.followup.send(view=checking, ephemeral=True)

        ok, stored = await _validate(self.platform, raw)

        if not ok:
            meta = PLATFORMS[self.platform]
            fail = discord.ui.LayoutView()
            fail.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('icon_cross')} Not Found"),
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

        await interaction.client.cxn.execute(
            "INSERT OR REPLACE INTO follows "
            "(guild_id, platform, username, channel_id, template, last_post_id) "
            "VALUES ($1, $2, $3, $4, $5, $6)",
            self.guild.id, self.platform, stored, channel.id, "", seed_id,
        )

        dname = _display(self.platform, stored)
        success = discord.ui.LayoutView()
        success.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_tick')} Now Following"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"Now tracking **{dname}** on **{self.platform.capitalize()}**.\n"
                    f"New posts will be announced in {channel.mention}."
                )
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
                    content=f"{get_emoji('icon_cross')} You need **Manage Server** permissions to do that."
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
                    content=f"{get_emoji('icon_cross')} You need **Manage Server** permissions to do that."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        follows = await interaction.client.cxn.fetch(
            "SELECT * FROM follows WHERE guild_id = $1", self.guild_id
        )
        view = _build_follows_list_view(interaction.guild, follows)
        await interaction.response.send_message(view=view, ephemeral=True)


# ─────────────────────────────────────────
#  Remove-follow select
# ─────────────────────────────────────────

class _RemoveFollowSelect(discord.ui.Select):
    def __init__(self, guild_id: int, follows: list):
        self.guild_id = guild_id
        options = []
        for row in follows[:25]:
            platform   = row["platform"]
            username   = row["username"]
            channel_id = row["channel_id"]
            icon = PLATFORMS.get(platform, {}).get("icon", get_emoji("icon_megaphone"))
            dname = _display(platform, username)
            options.append(discord.SelectOption(
                label=f"{dname} ({platform.capitalize()})",
                description=f"→ #{channel_id}",
                value=f"{platform}:{username}",
                emoji=icon,
            ))
        super().__init__(placeholder="Select an account to unfollow…", options=options)

    async def callback(self, interaction: discord.Interaction):
        platform, username = self.values[0].split(":", 1)
        await interaction.client.cxn.execute(
            "DELETE FROM follows WHERE guild_id = $1 AND platform = $2 AND username = $3",
            self.guild_id, platform, username,
        )
        dname = _display(platform, username)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_tick')} Unfollowed"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"Stopped tracking **{dname}** on **{platform.capitalize()}**."
            ),
            accent_colour=discord.Colour(0x57F287),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


# ─────────────────────────────────────────
#  View builders
# ─────────────────────────────────────────

def build_setup_view(
    guild: discord.Guild,
    channel: discord.TextChannel,
    follows: list,
    prefix: str = ".",
) -> discord.ui.LayoutView:
    count = len(follows)
    icons = " · ".join(m["icon"] for m in PLATFORMS.values())

    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {get_emoji('icon_megaphone')} Social Media Notifier"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                f"Get notified when your favourite creators post new content.\n"
                f"Supports: {icons}\n\n"
                f"**Currently tracking:** {count} account{'s' if count != 1 else ''}"
            )
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            _AddFollowBtn("youtube",  guild, channel),
            _AddFollowBtn("twitter",  guild, channel),
            _AddFollowBtn("tiktok",   guild, channel),
        ),
        discord.ui.ActionRow(
            _AddFollowBtn("bluesky",  guild, channel),
            _AddFollowBtn("reddit",   guild, channel),
            _ViewFollowsBtn(guild.id),
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                f"-# You can also use `{prefix}follow <platform> <name> [#channel]`\n"
                f"-# Platforms: youtube · twitter · tiktok · bluesky · reddit"
            )
        ),
        accent_colour=discord.Colour(0x5865F2),
    ))
    return view


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

    lines = []
    for row in follows:
        platform   = row["platform"]
        username   = row["username"]
        channel_id = row["channel_id"]
        icon  = PLATFORMS.get(platform, {}).get("icon", get_emoji("icon_megaphone"))
        dname = _display(platform, username)
        ch    = guild.get_channel(channel_id)
        ch_text = ch.mention if ch else f"<#{channel_id}>"
        lines.append(f"{icon} **{dname}** ({platform.capitalize()}) → {ch_text}")

    items: list = [
        discord.ui.TextDisplay(content="### 📋 Followed Accounts"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="\n".join(lines)),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="-# Select an account below to remove it."),
        discord.ui.ActionRow(_RemoveFollowSelect(guild.id, follows)),
    ]
    view.add_item(discord.ui.Container(*items, accent_colour=discord.Colour(0x5865F2)))
    return view


# ─────────────────────────────────────────
#  Notifier Cog
# ─────────────────────────────────────────

class Notifier(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_posts.start()

    def cog_unload(self):
        self.check_posts.cancel()

    # ── Command group ─────────────────────

    @commands.group(name="notifier", aliases=["notify"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def notifier(self, ctx: commands.Context):
        """Open the social media notifier setup panel."""
        prefix  = self.bot.command_prefix if isinstance(self.bot.command_prefix, str) else "."
        follows = await self.bot.cxn.fetch(
            "SELECT * FROM follows WHERE guild_id = $1", ctx.guild.id
        )
        view = build_setup_view(ctx.guild, ctx.channel, follows, prefix)
        await ctx.send(view=view)

    @notifier.command(name="list")
    @commands.has_permissions(manage_guild=True)
    async def notifier_list(self, ctx: commands.Context):
        """List all followed accounts for this server."""
        follows = await self.bot.cxn.fetch(
            "SELECT * FROM follows WHERE guild_id = $1", ctx.guild.id
        )
        view = _build_follows_list_view(ctx.guild, follows)
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
                discord.ui.TextDisplay(content=f"### {get_emoji('icon_cross')} Account Not Found"),
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
                discord.ui.TextDisplay(content=f"### {get_emoji('icon_danger')} No Posts Found"),
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
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_tick')} Fetch Successful — {dname}"),
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
        """Follow a social media account. Platforms: youtube twitter tiktok bluesky reddit"""
        platform = platform.lower()
        if platform not in PLATFORMS:
            return await ctx.reply(
                f"Unknown platform. Valid options: `{'`, `'.join(ALL_PLATFORMS)}`"
            )

        channel = channel or ctx.channel

        status = discord.ui.LayoutView()
        status.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_loading')} Checking…"),
            discord.ui.TextDisplay(content="Validating the account, one moment…"),
            accent_colour=discord.Colour(0xFEE75C),
        ))
        msg = await ctx.send(view=status)

        ok, stored = await _validate(platform, username)
        if not ok:
            fail = discord.ui.LayoutView()
            fail.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('icon_cross')} Not Found"),
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

        await self.bot.cxn.execute(
            "INSERT OR REPLACE INTO follows "
            "(guild_id, platform, username, channel_id, template, last_post_id) "
            "VALUES ($1, $2, $3, $4, $5, $6)",
            ctx.guild.id, platform, stored, channel.id, "", seed_id,
        )

        dname   = _display(platform, stored)
        success = discord.ui.LayoutView()
        success.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_tick')} Now Following"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"Now tracking **{dname}** on **{platform.capitalize()}**.\n"
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
        # Try to match exactly (including stored YouTube format)
        rows = await self.bot.cxn.fetch(
            "SELECT username FROM follows WHERE guild_id = $1 AND platform = $2",
            ctx.guild.id, platform,
        )
        # Find the best matching row
        target = None
        needle = username.strip().lstrip("@").lower()
        for row in rows:
            stored = row["username"]
            dname  = _display(platform, stored).lower().lstrip("@r/")
            if needle == stored.lower() or needle == dname:
                target = stored
                break

        if target is None:
            fail = discord.ui.LayoutView()
            fail.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('icon_cross')} Not Found"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"No follow found for **{username}** on **{platform.capitalize()}**."
                ),
                accent_colour=discord.Colour(0xED4245),
            ))
            await ctx.send(view=fail)
            return

        await self.bot.cxn.execute(
            "DELETE FROM follows WHERE guild_id = $1 AND platform = $2 AND username = $3",
            ctx.guild.id, platform, target,
        )
        dname = _display(platform, target)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_tick')} Unfollowed"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"Stopped tracking **{dname}** on **{platform.capitalize()}**."
            ),
            accent_colour=discord.Colour(0x57F287),
        ))
        await ctx.send(view=view)

    # ── Background polling task ───────────

    @tasks.loop(minutes=5)
    async def check_posts(self):
        try:
            follows = await self.bot.cxn.fetch("SELECT * FROM follows")
        except Exception:
            return

        for row in follows:
            guild_id   = row["guild_id"]
            platform   = row["platform"]
            username   = row["username"]
            channel_id = row["channel_id"]
            last_post  = row["last_post_id"]

            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
            channel = guild.get_channel(channel_id)
            if not channel:
                continue

            post = await _fetch(platform, username)
            if not post:
                continue

            post_id = post.get("id")
            if not post_id:
                continue

            # Seed if first run — no notification
            if last_post is None:
                try:
                    await self.bot.cxn.execute(
                        "UPDATE follows SET last_post_id = $1 "
                        "WHERE guild_id = $2 AND platform = $3 AND username = $4",
                        post_id, guild_id, platform, username,
                    )
                except Exception:
                    pass
                continue

            if post_id == last_post:
                continue

            # New post — send notification
            view = build_notification_view(platform, username, post)
            try:
                await channel.send(view=view)
                await self.bot.cxn.execute(
                    "UPDATE follows SET last_post_id = $1 "
                    "WHERE guild_id = $2 AND platform = $3 AND username = $4",
                    post_id, guild_id, platform, username,
                )
            except Exception:
                pass

            # Brief pause between sends to avoid rate limits
            await asyncio.sleep(1)

    @check_posts.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Notifier(bot))
