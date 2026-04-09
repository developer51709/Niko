import discord
from discord.ext import commands, tasks
import re
import datetime
import random
import asyncio

class JoinGiveawayView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Join", style=discord.ButtonStyle.primary, emoji="🎉", custom_id="giveaway_system:join")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        message_id = interaction.message.id
        user_id = interaction.user.id

        giveaway = await self.bot.cxn.fetchone("SELECT host_id, ended FROM giveaways WHERE message_id = $1", message_id)

        if not giveaway:
            return await interaction.response.send_message("❌ This giveaway doesn't exist anymore.", ephemeral=True)

        host_id = giveaway["host_id"]
        ended = giveaway["ended"]

        if ended:
            return await interaction.response.send_message("❌ This giveaway has already ended!", ephemeral=True)

        if user_id == host_id:
            return await interaction.response.send_message("❌ You cannot join your own giveaway!", ephemeral=True)

        if interaction.user.bot:
            return await interaction.response.send_message("❌ Bots cannot participate in giveaways!", ephemeral=True)

        existing = await self.bot.cxn.fetchone("SELECT 1 FROM participants WHERE message_id = $1 AND user_id = $2", message_id, user_id)
        if existing:
            return await interaction.response.send_message("✅ You have already joined this giveaway!", ephemeral=True)

        await self.bot.cxn.execute("INSERT INTO participants (message_id, user_id) VALUES ($1, $2)", message_id, user_id)

        await interaction.response.send_message("🎉 You have successfully joined the giveaway! Good luck!", ephemeral=True)

    @discord.ui.button(label="End", style=discord.ButtonStyle.danger, emoji="🛑", custom_id="giveaway_system:end")
    async def end_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        giveaway = await self.bot.cxn.fetchone("SELECT host_id, ended, prize, winners_count FROM giveaways WHERE message_id = $1", interaction.message.id)

        if not giveaway:
            return await interaction.response.send_message("❌ This giveaway doesn't exist anymore.", ephemeral=True)

        host_id = giveaway["host_id"]
        ended = giveaway["ended"]
        prize = giveaway["prize"]
        winners_count = giveaway["winners_count"]

        if interaction.user.id != host_id and (not self.bot.owner_ids or interaction.user.id not in self.bot.owner_ids):
            return await interaction.response.send_message("❌ Only the giveaway host or a bot owner can end this giveaway early.", ephemeral=True)

        if ended:
            return await interaction.response.send_message("❌ This giveaway has already ended!", ephemeral=True)

        await interaction.response.send_message("✅ Ending giveaway early...", ephemeral=True)

        giveaway_cog = self.bot.get_cog("Giveaway")
        if giveaway_cog:
            await giveaway_cog.end_giveaway(interaction.message.id, interaction.channel.id, interaction.guild.id, prize, winners_count, host_id)

    @discord.ui.button(label="Select", style=discord.ButtonStyle.secondary, emoji="🎲", custom_id="giveaway_system:select")
    async def select_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        giveaway = await self.bot.cxn.fetchone("SELECT host_id FROM giveaways WHERE message_id = $1", interaction.message.id)

        if not giveaway:
            return await interaction.response.send_message("❌ This giveaway doesn't exist anymore.", ephemeral=True)

        host_id = giveaway["host_id"]

        if interaction.user.id != host_id and (not self.bot.owner_ids or interaction.user.id not in self.bot.owner_ids):
            return await interaction.response.send_message("❌ Only the giveaway host or a bot owner can select users.", ephemeral=True)

        rows = await self.bot.cxn.fetch("SELECT user_id FROM participants WHERE message_id = $1", interaction.message.id)
        participants = [row["user_id"] for row in rows]

        if not participants:
            return await interaction.response.send_message("❌ Nobody has joined the giveaway yet!", ephemeral=True)

        winner = random.choice(participants)
        await interaction.response.send_message(f"🎲 Randomly selected user: <@{winner}>")


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    async def cog_load(self):
        self.bot.add_view(JoinGiveawayView(self.bot))

        await self.bot.cxn.execute('''
            CREATE TABLE IF NOT EXISTS giveaways (
                message_id INTEGER PRIMARY KEY,
                channel_id INTEGER,
                guild_id INTEGER,
                prize TEXT,
                winners_count INTEGER,
                end_time TEXT,
                ended BOOLEAN,
                host_id INTEGER
            )
        ''')
        await self.bot.cxn.execute('''
            CREATE TABLE IF NOT EXISTS participants (
                message_id INTEGER,
                user_id INTEGER,
                PRIMARY KEY (message_id, user_id)
            )
        ''')

        # Clean up any rows with invalid end_time values left over from previous bugs
        await self.bot.cxn.execute(
            "UPDATE giveaways SET ended = 1 WHERE ended = 0 AND end_time NOT LIKE '____-%'"
        )

    async def cog_unload(self):
        self.check_giveaways.cancel()

    def parse_duration(self, duration_str: str) -> int:
        matches = re.match(r"([\d\.]+)([smhd])", duration_str.lower())
        if not matches:
            return -1
        try:
            value = float(matches.group(1))
            unit = matches.group(2)
            multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
            return int(value * multipliers[unit])
        except ValueError:
            return -1

    @commands.group(name="giveaway", aliases=["g"], invoke_without_command=True)
    async def giveaway(self, ctx):
        """Manage giveaways. Subcommands: start, reroll."""
        await ctx.send_help(ctx.command)

    @giveaway.command(name="start")
    @commands.is_owner()
    async def start(self, ctx, duration: str, winners: str, *, prize: str):
        """Start a new giveaway."""
        seconds = self.parse_duration(duration)
        if seconds <= 0:
            return await ctx.send("❌ Invalid duration! Use numbers followed by `s`, `m`, `h`, or `d` (e.g., 30s, 10m, 2h, 1d).")

        winners_clean = ''.join(filter(str.isdigit, winners))
        if not winners_clean:
            return await ctx.send("❌ Invalid winners count! Must be a number (e.g., 2).")

        winners_count = int(winners_clean)
        if winners_count < 1:
            return await ctx.send("❌ You must have at least 1 winner!")

        end_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=seconds)
        end_timestamp = int(end_time.timestamp())

        embed = discord.Embed(title="🎉 Giveaway", color=discord.Color.purple())
        embed.add_field(name="Prize", value=prize, inline=False)
        embed.add_field(name="Ends in", value=f"<t:{end_timestamp}:R> (<t:{end_timestamp}:f>)", inline=False)
        embed.add_field(name="Hosted by", value=ctx.author.mention, inline=False)
        embed.set_footer(text=f"{winners_count} Winner{'s' if winners_count > 1 else ''} | Ends at")
        embed.timestamp = end_time

        view = JoinGiveawayView(self.bot)
        msg = await ctx.send(embed=embed, view=view)

        await self.bot.cxn.execute(
            '''INSERT INTO giveaways (message_id, channel_id, guild_id, prize, winners_count, end_time, ended, host_id)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)''',
            msg.id, ctx.channel.id, ctx.guild.id, prize, winners_count, end_time.isoformat(), False, ctx.author.id
        )

    @giveaway.command(name="reroll")
    @commands.is_owner()
    async def reroll(self, ctx, message_id: int):
        """Reroll a specific giveaway to pick new winners."""
        giveaway = await self.bot.cxn.fetchone("SELECT prize, winners_count, ended FROM giveaways WHERE message_id = $1", message_id)

        if not giveaway:
            return await ctx.send("❌ Could not find a giveaway with that message ID. Make sure it's correct.")

        prize = giveaway["prize"]
        ended = giveaway["ended"]

        if not ended:
            return await ctx.send("❌ This giveaway hasn't ended yet! You can only reroll ended giveaways.")

        rows = await self.bot.cxn.fetch("SELECT user_id FROM participants WHERE message_id = $1", message_id)
        participants = [row["user_id"] for row in rows]

        if not participants:
            return await ctx.send("❌ Nobody participated in this giveaway, so no one can be rerolled!")

        new_winners = random.sample(participants, min(1, len(participants)))
        winner_mentions = ", ".join(f"<@{w}>" for w in new_winners)

        await ctx.send(f"🎉 **Giveaway Reroll!**\nThe new winner for **{prize}** is: {winner_mentions}! Congratulations!")

    @tasks.loop(seconds=15)
    async def check_giveaways(self):
        """Background task checking for ended giveaways."""
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            giveaways = await self.bot.cxn.fetch(
                "SELECT message_id, channel_id, guild_id, prize, winners_count, end_time, host_id FROM giveaways WHERE ended = 0"
            )

            for row in giveaways:
                message_id = row["message_id"]
                end_time_str = row["end_time"]
                try:
                    end_time = datetime.datetime.fromisoformat(str(end_time_str))
                except (TypeError, ValueError):
                    print(f"[Giveaway] Skipping {message_id}: bad end_time value {end_time_str!r}")
                    await self.bot.cxn.execute("UPDATE giveaways SET ended = 1 WHERE message_id = $1", message_id)
                    continue

                if now >= end_time:
                    await self.end_giveaway(
                        message_id,
                        row["channel_id"],
                        row["guild_id"],
                        row["prize"],
                        row["winners_count"],
                        row["host_id"],
                    )
                    await asyncio.sleep(0.1)
        except Exception as e:
            print(f"[Giveaway Task Error] Processing failed: {e}")

    async def end_giveaway(self, message_id, channel_id, guild_id, prize, winners_count, host_id):
        """Ends the giveaway by choosing a winner, modifying embed, and announcing it."""
        await self.bot.cxn.execute("UPDATE giveaways SET ended = 1 WHERE message_id = $1", message_id)

        channel = self.bot.get_channel(channel_id)
        if not channel:
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except Exception:
                return

        try:
            msg = await channel.fetch_message(message_id)
        except Exception:
            msg = None

        rows = await self.bot.cxn.fetch("SELECT user_id FROM participants WHERE message_id = $1", message_id)
        participants = [row["user_id"] for row in rows]

        if len(participants) == 0:
            if msg and len(msg.embeds) > 0:
                embed = msg.embeds[0]
                embed.description = f"**{prize}**\n\n*Nobody participated.*"
                embed.color = discord.Color.dark_grey()
                await msg.edit(embed=embed, view=None)
            await channel.send(f"The giveaway for **{prize}** has ended, but unfortunately nobody participated! 😢")
            return

        winner_count = min(winners_count, len(participants))
        winners = random.sample(participants, winner_count)
        winner_mentions = ", ".join(f"<@{w}>" for w in winners)

        if msg and len(msg.embeds) > 0:
            embed = msg.embeds[0]
            embed.title = "🎉 Giveaway Ended! 🎉"
            embed.color = discord.Color.gold()
            embed.clear_fields()
            embed.add_field(name="Prize", value=prize, inline=False)
            embed.add_field(name="🏆 Winners", value=winner_mentions, inline=False)
            embed.add_field(name="Hosted by", value=f"<@{host_id}>", inline=False)
            await msg.edit(embed=embed, view=None)

        msg_url = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
        await channel.send(f"🎉 Congratulations {winner_mentions}! You won **{prize}**!\n{msg_url}")

    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Giveaway(bot))
