"""Persist lightweight daily activity totals for each Discord server."""

from collections import defaultdict
from datetime import datetime, timezone

from discord.ext import commands, tasks

from utils import logging


class ServerStats(commands.Cog):
    """Record message and membership activity for dashboard visualisations."""

    def __init__(self, bot):
        self.bot = bot
        self.pending: dict[tuple[int, str], dict[str, int]] = defaultdict(
            lambda: {"messages": 0, "joins": 0, "leaves": 0}
        )
        self.flush_activity.start()

    def cog_unload(self):
        self.flush_activity.cancel()

    def _record(self, guild_id: int, **increments: int) -> None:
        today = datetime.now(timezone.utc).date().isoformat()
        bucket = self.pending[(int(guild_id), today)]
        for key, amount in increments.items():
            if key in bucket:
                bucket[key] += int(amount)

    @tasks.loop(seconds=30)
    async def flush_activity(self):
        pool = getattr(self.bot, "cxn", None)
        if pool is None or not self.pending:
            return

        # Snapshot and remove only after each successful upsert so a transient
        # database error leaves the buffered increments available to retry.
        for (guild_id, activity_date), increments in list(self.pending.items()):
            if not any(increments.values()):
                self.pending.pop((guild_id, activity_date), None)
                continue
            snapshot = increments.copy()
            try:
                await pool.execute(
                    "INSERT INTO server_activity "
                    "(activity_id, guild_id, activity_date, messages, joins, leaves) "
                    "VALUES ($1, $2, $3, $4, $5, $6) "
                    "ON CONFLICT (activity_id) DO UPDATE SET "
                    "messages = messages + $7, joins = joins + $8, leaves = leaves + $9",
                    f"{guild_id}_{activity_date}",
                    guild_id,
                    activity_date,
                    snapshot["messages"],
                    snapshot["joins"],
                    snapshot["leaves"],
                    snapshot["messages"],
                    snapshot["joins"],
                    snapshot["leaves"],
                )
                current = self.pending.get((guild_id, activity_date))
                if current is not None:
                    for key, amount in snapshot.items():
                        current[key] -= amount
                    if not any(current.values()):
                        self.pending.pop((guild_id, activity_date), None)
            except Exception as exc:
                logging.warning("ServerStats", f"Could not persist activity for guild {guild_id}: {exc}")

    @flush_activity.before_loop
    async def before_flush_activity(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author.bot:
            return
        self._record(message.guild.id, messages=1)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self._record(member.guild.id, joins=1)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self._record(member.guild.id, leaves=1)


async def setup(bot):
    await bot.add_cog(ServerStats(bot))
