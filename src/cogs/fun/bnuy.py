import discord
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta

GIF_URL = "https://tenor.com/view/essica-monthly-bnuy-31st-gif-10238723221179923657"
TARGET_CHANNEL_ID = 1488677833357262988


class Monthly31st(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_bnuy.start()

    def cog_unload(self):
        self.send_bnuy.cancel()

    @tasks.loop(time=time(hour=9, minute=0))  
    async def send_bnuy(self):
        """Runs every day at 9:00 AM server time."""
        now = datetime.now()

        # Only run on the 31st
        if now.day != 31:
            return

        channel = self.bot.get_channel(TARGET_CHANNEL_ID)
        if channel is None:
            print(f"Channel {TARGET_CHANNEL_ID} not found.")
            return

        try:
            await channel.send(GIF_URL)
            print("Sent monthly bnuy GIF.")
        except Exception as e:
            print(f"Failed to send GIF: {e}")

    @send_bnuy.before_loop
    async def before_send_bnuy(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Monthly31st(bot))