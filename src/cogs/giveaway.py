import asyncio
import datetime

import discord
from discord.ext import commands, tasks


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    async def end_giveaway(self, message_id, channel_id, guild_id, prize, winners_count, host_id):
        """Ends the giveaway by choosing a winner, modifying embed, and announcing it."""
        await self.bot.cxn.execute("UPDATE giveaways SET ended = 1 WHERE message_id = ?", message_id)

        channel = self.bot.get_channel(channel_id)
        if not channel:
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except Exception:
                return

        try:
            msg = await channel.fetch_message(message_id)
        except Exception:
            return

        try:
            entrants = [u async for u in msg.reactions[0].users()] if msg.reactions else []
        except Exception:
            entrants = []

    @tasks.loop(seconds=15)
    async def check_giveaways(self):
        """Background task checking for ended giveaways."""
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            giveaways = await self.bot.cxn.fetch("SELECT message_id, channel_id, guild_id, prize, winners_count, end_time, host_id FROM giveaways WHERE ended = 0")

            for message_id, channel_id, guild_id, prize, winners_count, end_time_str, host_id in giveaways:
                try:
                    end_time = datetime.datetime.fromisoformat(str(end_time_str))
                except (TypeError, ValueError):
                    print(f"[Giveaway Task Error] Skipping giveaway {message_id}: invalid end_time {end_time_str!r}")
                    await self.bot.cxn.execute("UPDATE giveaways SET ended = 1 WHERE message_id = ?", message_id)
                    continue

                if now >= end_time:
                    await self.end_giveaway(message_id, channel_id, guild_id, prize, winners_count, host_id)
                    await asyncio.sleep(0.1)
        except Exception as e:
            print(f"[Giveaway Task Error] Processing failed: {e}")


async def setup(bot):
    await bot.add_cog(Giveaway(bot))
