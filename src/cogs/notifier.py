import discord
from discord.ext import commands, tasks

from utils.database import (
    add_follow, remove_follow, get_all_follows, update_last_post
)
from utils.twitter import fetch_latest_tweet
from utils.tiktok import fetch_latest_tiktok

PLATFORM_COLOR = {
    "twitter": discord.Colour(0x1DA1F2),
    "tiktok": discord.Colour(0x010101),
}


def build_notification_view(platform: str, username: str, url: str, message: str) -> discord.ui.LayoutView:
    color = PLATFORM_COLOR.get(platform, discord.Colour(0x5865F2))
    icon = "🐦" if platform == "twitter" else "🎵"

    view = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {icon} New {platform.capitalize()} Post"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=message),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=f"**User:** {username}\n**Link:** {url}"),
        accent_colour=color
    )
    view.add_item(container)
    return view


class Notifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_posts.start()

    # -------------------------------
    #  PREFIX COMMANDS
    # -------------------------------

    @commands.command(name="follow")
    @commands.has_permissions(manage_guild=True)
    async def follow(
        self, ctx,
        platform: str,
        username: str,
        channel: discord.TextChannel = None,
        *, template: str = "{username} posted something new!"
    ):
        """Follow a TikTok or Twitter user for new posts."""
        platform = platform.lower()
        if platform not in ["twitter", "tiktok"]:
            return await ctx.reply("Platform must be `twitter` or `tiktok`.")

        if channel is None:
            channel = ctx.channel

        add_follow(ctx.guild.id, platform, username, channel.id, template)
        await ctx.reply(
            f"Now following **{username}** on **{platform}**.\n"
            f"Notifications will be sent to {channel.mention}."
        )

    @commands.command(name="unfollow")
    @commands.has_permissions(manage_guild=True)
    async def unfollow(self, ctx, platform: str, username: str):
        """Unfollow a user."""
        remove_follow(ctx.guild.id, platform.lower(), username)
        await ctx.reply(f"Stopped following **{username}** on **{platform}**.")

    # -------------------------------
    #  BACKGROUND TASK
    # -------------------------------

    @tasks.loop(minutes=2)
    async def check_posts(self):
        follows = get_all_follows()

        for guild_id, platform, username, channel_id, template, last_post in follows:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue

            channel = guild.get_channel(channel_id)
            if not channel:
                continue

            if platform == "twitter":
                post = await fetch_latest_tweet(username)
            else:
                post = await fetch_latest_tiktok(username)

            if not post:
                continue

            if post["id"] != last_post:
                message = template.format(
                    username=username,
                    url=post["url"],
                    text=post.get("text", "")
                )
                view = build_notification_view(platform, username, post["url"], message)
                await channel.send(view=view)
                update_last_post(guild_id, platform, username, post["id"])

    @check_posts.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Notifier(bot))
