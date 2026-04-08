import discord
from discord.ext import commands, tasks
import feedparser
import aiohttp

import os

CHANNELS = {
    "UCWOMTp0BLi41FTn6ouh_mdg": int(os.getenv("YT_CHANNEL_1", 0)),
    "UCCYq8CHiJR3Y8IEME0SgNUQ": int(os.getenv("YT_CHANNEL_2", 0)),
    "UCKK4jwSOaKBSTqQjNRbndng": int(os.getenv("YT_CHANNEL_3", 0))
}

class YouTube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check.start()

    def cog_unload(self):
        self.check.cancel()

    @tasks.loop(minutes=5)
    async def check(self):
        for yt_id, discord_channel_id in CHANNELS.items():
            channel = self.bot.get_channel(discord_channel_id)
            if not channel:
                continue

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://www.youtube.com/feeds/videos.xml?channel_id={yt_id}", timeout=15) as response:
                        if response.status != 200:
                            continue
                        content = await response.read()
            except Exception as e:
                print(f"Error fetching YouTube feed for {yt_id}: {e}")
                continue

            feed = feedparser.parse(content)

            if not feed.entries:
                continue

            latest_entry = feed.entries[0]
            video_id = latest_entry.get("yt_videoid")

            async with self.bot.cxn.execute(
                "SELECT channel_id FROM youtube_history WHERE channel_id = ?",
                (yt_id,)
            ) as cursor:
                has_history = await cursor.fetchone()

            async with self.bot.cxn.execute(
                "SELECT video_id FROM youtube_history WHERE channel_id = ? AND video_id = ?",
                (yt_id, video_id)
            ) as cursor:
                row = await cursor.fetchone()

            if row is None:
                await self.bot.cxn.execute(
                    "INSERT INTO youtube_history (channel_id, video_id) VALUES (?, ?)",
                    (yt_id, video_id)
                )
                await self.bot.cxn.execute(
                    "INSERT OR REPLACE INTO youtube (channel_id, last_video) VALUES (?, ?)",
                    (yt_id, video_id)
                )

                if has_history is None:
                    continue

                embed = discord.Embed(
                    title=f"🎥 {latest_entry.author} just posted a video! Go check it out!",
                    description=f"**[{latest_entry.title}](https://www.youtube.com/watch?v={video_id})**",
                    color=discord.Color.red()
                )
                embed.set_image(url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg")

                await channel.send(content="New YouTube upload!", embed=embed)

    @check.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(YouTube(bot))