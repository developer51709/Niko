import discord
from discord.ext import commands, tasks
from discord.ui import Modal, TextInput

from utils.twitter import fetch_latest_tweet, validate_twitter_username
from utils.tiktok import fetch_latest_tiktok, validate_tiktok_username

PLATFORM_COLOR = {
    "twitter": discord.Colour(0x1DA1F2),
    "tiktok":  discord.Colour(0xFF0050),
}
PLATFORM_ICON = {
    "twitter": "🐦",
    "tiktok":  "🎵",
}


# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────

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


def build_notification_view(platform: str, username: str, url: str, text: str) -> discord.ui.LayoutView:
    color = PLATFORM_COLOR.get(platform, discord.Colour(0x5865F2))
    icon  = PLATFORM_ICON.get(platform, "📢")

    body = f"**@{username}** just posted something new!"
    if text:
        preview = text[:200] + ("…" if len(text) > 200 else "")
        body += f"\n\n> {preview}"
    body += f"\n\n🔗 [View Post]({url})"

    view = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {icon} New {platform.capitalize()} Post"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=body),
        accent_colour=color
    )
    view.add_item(container)
    return view


# ─────────────────────────────────────────
#  VIEW BUILDERS  (accept pre-fetched rows)
# ─────────────────────────────────────────

def build_setup_view(guild: discord.Guild, channel: discord.TextChannel,
                     follows: list, prefix: str = ".") -> discord.ui.LayoutView:
    count = len(follows)

    view = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content="### 📢 Social Media Notifier"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                "Get notified when your favourite Twitter or TikTok accounts post something new.\n\n"
                f"**Currently tracking:** {count} account{'s' if count != 1 else ''}"
            )
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            FollowTwitterBtn(guild, channel),
            FollowTikTokBtn(guild, channel),
            ViewFollowsBtn(guild.id),
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                f"-# You can also use `{prefix}follow <twitter/tiktok> <username> [#channel]`\n"
                f"-# and `{prefix}unfollow <twitter/tiktok> <username>` directly."
            )
        ),
        accent_colour=discord.Colour(0x5865F2)
    )
    view.add_item(container)
    return view


def _build_follows_list_view(guild: discord.Guild, follows: list) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()

    if not follows:
        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### 📋 Followed Accounts"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="No accounts are being tracked yet. Use the setup panel to add some!"),
            accent_colour=discord.Colour(0x5865F2)
        )
        view.add_item(container)
        return view

    lines = []
    for row in follows:
        platform   = row["platform"]
        username   = row["username"]
        channel_id = row["channel_id"]
        icon = PLATFORM_ICON.get(platform, "📢")
        channel = guild.get_channel(channel_id)
        ch_text = channel.mention if channel else f"<#{channel_id}>"
        lines.append(f"{icon} **@{username}** ({platform.capitalize()}) → {ch_text}")

    container = discord.ui.Container(
        discord.ui.TextDisplay(content="### 📋 Followed Accounts"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="\n".join(lines)),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="-# Select an account below to unfollow it."),
        discord.ui.ActionRow(RemoveFollowSelect(guild.id, follows)),
        accent_colour=discord.Colour(0x5865F2)
    )
    view.add_item(container)
    return view


# ─────────────────────────────────────────
#  MODALS
# ─────────────────────────────────────────

class AddFollowModal(Modal):
    def __init__(self, platform: str, guild: discord.Guild, default_channel: discord.TextChannel):
        super().__init__(title=f"Follow a {platform.capitalize()} Account")
        self.platform        = platform
        self.guild           = guild
        self.default_channel = default_channel

        self.username_input = TextInput(
            label="Username",
            placeholder=f"e.g. {'elonmusk' if platform == 'twitter' else 'charlidamelio'}",
            max_length=50,
        )
        self.channel_input = TextInput(
            label="Notification Channel",
            placeholder="Leave blank to use the current channel",
            required=False,
            max_length=100,
        )
        self.add_item(self.username_input)
        self.add_item(self.channel_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        username = self.username_input.value.strip().lstrip("@")

        channel_text = self.channel_input.value.strip()
        if channel_text:
            channel = _resolve_channel(self.guild, channel_text)
            if channel is None:
                await interaction.followup.send(
                    "Couldn't find that channel. Try a #mention or channel name.", ephemeral=True
                )
                return
        else:
            channel = self.default_channel

        status_view = discord.ui.LayoutView()
        status_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### ⏳ Checking @{username}..."),
            discord.ui.TextDisplay(content="Verifying the account exists. This may take a moment."),
            accent_colour=discord.Colour(0xFEE75C)
        ))
        await interaction.followup.send(view=status_view, ephemeral=True)

        if self.platform == "twitter":
            valid = await validate_twitter_username(username)
        else:
            valid = await validate_tiktok_username(username)

        if not valid:
            fail_view = discord.ui.LayoutView()
            fail_view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content="### ❌ Account Not Found"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"Could not find **@{username}** on **{self.platform.capitalize()}**.\n"
                            f"Double-check the username and try again."
                ),
                accent_colour=discord.Colour(0xED4245)
            ))
            await interaction.edit_original_response(view=fail_view)
            return

        await interaction.client.cxn.execute(
            "INSERT OR REPLACE INTO follows "
            "(guild_id, platform, username, channel_id, template, last_post_id) "
            "VALUES ($1, $2, $3, $4, $5, $6)",
            self.guild.id, self.platform, username, channel.id, "", None
        )

        success_view = discord.ui.LayoutView()
        success_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="### ✅ Now Following"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"Now tracking **@{username}** on **{self.platform.capitalize()}**.\n"
                        f"New posts will be sent to {channel.mention}."
            ),
            accent_colour=discord.Colour(0x57F287)
        ))
        await interaction.edit_original_response(view=success_view)


# ─────────────────────────────────────────
#  SETUP VIEW BUTTONS
# ─────────────────────────────────────────

class FollowTwitterBtn(discord.ui.Button):
    def __init__(self, guild: discord.Guild, channel: discord.TextChannel):
        super().__init__(label="Follow Twitter Account", style=discord.ButtonStyle.blurple, emoji="🐦")
        self.guild   = guild
        self.channel = channel

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AddFollowModal("twitter", self.guild, self.channel))


class FollowTikTokBtn(discord.ui.Button):
    def __init__(self, guild: discord.Guild, channel: discord.TextChannel):
        super().__init__(label="Follow TikTok Account", style=discord.ButtonStyle.red, emoji="🎵")
        self.guild   = guild
        self.channel = channel

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AddFollowModal("tiktok", self.guild, self.channel))


class ViewFollowsBtn(discord.ui.Button):
    def __init__(self, guild_id: int):
        super().__init__(label="View Follows", style=discord.ButtonStyle.gray, emoji="📋")
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        follows = await interaction.client.cxn.fetch(
            "SELECT * FROM follows WHERE guild_id = $1", self.guild_id
        )
        view = _build_follows_list_view(interaction.guild, follows)
        await interaction.response.send_message(view=view, ephemeral=True)


# ─────────────────────────────────────────
#  FOLLOWS LIST — REMOVE SELECT
# ─────────────────────────────────────────

class RemoveFollowSelect(discord.ui.Select):
    def __init__(self, guild_id: int, follows: list):
        self.guild_id = guild_id
        options = []
        for row in follows[:25]:
            platform   = row["platform"]
            username   = row["username"]
            channel_id = row["channel_id"]
            icon = PLATFORM_ICON.get(platform, "📢")
            options.append(discord.SelectOption(
                label=f"@{username} ({platform.capitalize()})",
                description=f"Notifications → #{channel_id}",
                value=f"{platform}:{username}",
                emoji=icon,
            ))
        super().__init__(placeholder="Select an account to unfollow…", options=options)

    async def callback(self, interaction: discord.Interaction):
        platform, username = self.values[0].split(":", 1)
        await interaction.client.cxn.execute(
            "DELETE FROM follows WHERE guild_id = $1 AND platform = $2 AND username = $3",
            self.guild_id, platform, username
        )

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="### ✅ Unfollowed"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"No longer tracking **@{username}** on **{platform.capitalize()}**."),
            accent_colour=discord.Colour(0x57F287)
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


# ─────────────────────────────────────────
#  NOTIFIER COG
# ─────────────────────────────────────────

class Notifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_posts.start()

    # ─── COMMAND GROUP ───────────────────

    @commands.group(name="notifier", aliases=["notify"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def notifier(self, ctx: commands.Context):
        """Social media notifier setup panel."""
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
    async def notifier_test(self, ctx: commands.Context, platform: str, username: str):
        """Test if an account can be fetched."""
        platform = platform.lower()
        if platform not in ("twitter", "tiktok"):
            return await ctx.send("Platform must be `twitter` or `tiktok`.")

        username = username.lstrip("@")

        status_view = discord.ui.LayoutView()
        status_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### ⏳ Testing @{username}…"),
            discord.ui.TextDisplay(content="Fetching the latest post. This may take a moment."),
            accent_colour=discord.Colour(0xFEE75C)
        ))
        msg = await ctx.send(view=status_view)

        if platform == "twitter":
            post = await fetch_latest_tweet(username)
        else:
            post = await fetch_latest_tiktok(username)

        if post:
            result_view = discord.ui.LayoutView()
            result_view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### ✅ Successfully Fetched @{username}"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"**Latest post:** {post.get('text', '(no text)') or '(no text)'}\n**Link:** {post['url']}"
                ),
                accent_colour=discord.Colour(0x57F287)
            ))
            await msg.edit(view=result_view)
        else:
            fail_view = discord.ui.LayoutView()
            fail_view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### ❌ Could Not Fetch @{username}"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=(
                        f"Unable to retrieve posts for **@{username}** on **{platform.capitalize()}**.\n\n"
                        "This could mean the account doesn't exist, is private, or the service is temporarily unavailable."
                    )
                ),
                accent_colour=discord.Colour(0xED4245)
            ))
            await msg.edit(view=fail_view)

    # ─── SHORTCUT COMMANDS ───────────────

    @commands.command(name="follow")
    @commands.has_permissions(manage_guild=True)
    async def follow(self, ctx, platform: str, username: str, channel: discord.TextChannel = None):
        """Follow a Twitter or TikTok account."""
        platform = platform.lower()
        if platform not in ("twitter", "tiktok"):
            return await ctx.reply("Platform must be `twitter` or `tiktok`.")

        username = username.lstrip("@")
        if channel is None:
            channel = ctx.channel

        await self.bot.cxn.execute(
            "INSERT OR REPLACE INTO follows "
            "(guild_id, platform, username, channel_id, template, last_post_id) "
            "VALUES ($1, $2, $3, $4, $5, $6)",
            ctx.guild.id, platform, username, channel.id, "", None
        )

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="### ✅ Now Following"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"Now tracking **@{username}** on **{platform.capitalize()}**.\nNew posts → {channel.mention}"
            ),
            accent_colour=discord.Colour(0x57F287)
        ))
        await ctx.send(view=view)

    @commands.command(name="unfollow")
    @commands.has_permissions(manage_guild=True)
    async def unfollow(self, ctx, platform: str, username: str):
        """Unfollow a tracked account."""
        await self.bot.cxn.execute(
            "DELETE FROM follows WHERE guild_id = $1 AND platform = $2 AND username = $3",
            ctx.guild.id, platform.lower(), username.lstrip("@")
        )
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="### ✅ Unfollowed"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"No longer tracking **@{username}** on **{platform.capitalize()}**."),
            accent_colour=discord.Colour(0x57F287)
        ))
        await ctx.send(view=view)

    # ─── BACKGROUND TASK ─────────────────

    @tasks.loop(minutes=5)
    async def check_posts(self):
        follows = await self.bot.cxn.fetch("SELECT * FROM follows")

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

            try:
                if platform == "twitter":
                    post = await fetch_latest_tweet(username)
                else:
                    post = await fetch_latest_tiktok(username)
            except Exception:
                continue

            if not post:
                continue

            if post["id"] != last_post:
                view = build_notification_view(platform, username, post["url"], post.get("text", ""))
                try:
                    await channel.send(view=view)
                    await self.bot.cxn.execute(
                        "UPDATE follows SET last_post_id = $1 "
                        "WHERE guild_id = $2 AND platform = $3 AND username = $4",
                        post["id"], guild_id, platform, username
                    )
                except Exception:
                    pass

    @check_posts.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Notifier(bot))
