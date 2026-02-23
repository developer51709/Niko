# leveling.py
# This cog adds a functional leveling system to the bot.
# It tracks user messages and assigns XP based on how active a user is in the chat.
# Users can check their level and XP with the !level command.
# Users can also check the leaderboard with the !leaderboard command.

import discord
from discord.ext import commands
import random
import json
import os
from utils import logging as log

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = "data/levels.json"
        self.levels = self.load_levels()

    def load_levels(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                return json.load(f)
        return {}

    def save_levels(self):
        with open(self.data_path, "w") as f:
            json.dump(self.levels, f, indent=4)

    def get_xp_for_level(self, level):
        return 5 * (level ** 2) + (50 * level) + 100

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        guild_id = str(message.guild.id)
        user_id = str(message.author.id)

        if guild_id not in self.levels:
            self.levels[guild_id] = {}
        
        if user_id not in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {"xp": 0, "level": 0}

        # Add random XP between 15 and 25
        xp_gain = random.randint(15, 25)
        self.levels[guild_id][user_id]["xp"] += xp_gain
        
        current_xp = self.levels[guild_id][user_id]["xp"]
        current_level = self.levels[guild_id][user_id]["level"]
        
        next_level_xp = self.get_xp_for_level(current_level)
        
        if current_xp >= next_level_xp:
            self.levels[guild_id][user_id]["level"] += 1
            self.levels[guild_id][user_id]["xp"] = 0
            new_level = self.levels[guild_id][user_id]["level"]
            try:
                await message.channel.send(f"Congratulations {message.author.mention}, you leveled up to level {new_level}!")
                log.info("Leveling", f"User {message.author} leveled up to {new_level} in {message.guild.name}")
            except discord.Forbidden:
                pass
        
        self.save_levels()

    @commands.command(name="level", aliases=["rank"])
    async def level(self, ctx, member: discord.Member = None):
        """Check your current level and XP."""
        member = member or ctx.author
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id not in self.levels or user_id not in self.levels[guild_id]:
            await ctx.send(f"{member.display_name} hasn't earned any XP yet.")
            return

        user_data = self.levels[guild_id][user_id]
        current_level = user_data["level"]
        current_xp = user_data["xp"]
        next_level_xp = self.get_xp_for_level(current_level)

        embed = discord.Embed(title=f"Leveling Stats - {member.display_name}", color=discord.Color.blue())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Level", value=str(current_level), inline=True)
        embed.add_field(name="XP", value=f"{current_xp}/{next_level_xp}", inline=True)
        
        # Calculate rank
        sorted_users = sorted(self.levels[guild_id].items(), key=lambda x: (x[1]["level"], x[1]["xp"]), reverse=True)
        rank = 1
        for uid, data in sorted_users:
            if uid == user_id:
                break
            rank += 1
        
        embed.add_field(name="Rank", value=f"#{rank}", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="level-leaderboard", aliases=["lvl-lb"])
    async def leaderboard(self, ctx):
        """View the leveling leaderboard."""
        guild_id = str(ctx.guild.id)
        if guild_id not in self.levels or not self.levels[guild_id]:
            await ctx.send("No one has earned any XP in this server yet.")
            return

        sorted_users = sorted(self.levels[guild_id].items(), key=lambda x: (x[1]["level"], x[1]["xp"]), reverse=True)
        
        embed = discord.Embed(title=f"Leveling Leaderboard - {ctx.guild.name}", color=discord.Color.gold())
        
        description = ""
        for i, (user_id, data) in enumerate(sorted_users[:10], start=1):
            user = self.bot.get_user(int(user_id))
            name = user.display_name if user else f"User {user_id}"
            description += f"**{i}. {name}** - Level {data['level']} ({data['xp']} XP)\n"
        
        embed.description = description
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
