# gambling.py cog
# This cog let's users gamble away there money to ruin the bot's economy even further cus who doesn't love gambling?
# It includes commands for slots, blackjack, roulette, and more.
# I will also add a gambling leaderboard later on.

import discord
from discord.ext import commands
import random
import json
import os
import time
import asyncio
import math
from discord.ui import Button, View

# Cooldowns
slots_cooldown = os.getenv("SLOTS_COOLDOWN") or 60
blackjack_cooldown = os.getenv("BLACKJACK_COOLDOWN") or 60
roulette_cooldown = os.getenv("ROULETTE_COOLDOWN") or 60

class GamblingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.economy_data = self.load_economy_data()

    # Create a directory for economy data if it doesn't exist
    if not os.path.exists("economy_data"):
        print("economy_data directory not found. Creating directory...")
        os.makedirs("economy_data")
        print("economy_data directory created successfully. Continuing...")

    # Load economy data from economy_data directory
    def load_economy_data(self):
        economy_data = {}
        if os.path.exists("economy_data"):
            for filename in os.listdir("economy_data"):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join("economy_data", filename), "r") as f:
                            user_id = filename[:-5]
                            economy_data[user_id] = json.load(f)
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
        return economy_data

    # Save economy data to economy_data directory per user
    def save_economy_data(self):
        if not os.path.exists("economy_data"):
            os.makedirs("economy_data")
        for user_id, data in self.economy_data.items():
            with open(os.path.join("economy_data", f"{user_id}.json"), "w") as f:
                json.dump(data, f, indent=4)

    # Get user economy data
    def get_user_economy_data(self, user_id):
        uid = str(user_id)
        if uid not in self.economy_data:
            self.economy_data[uid] = {"balance": 0, "inventory": [], "bank": 0, "net_worth": 0, "daily_streak": 0, "last_daily": 0, "last_work": 0, "last_crime": 0, "last_rob": 0, "last_heist": 0, "last_slots": 0, "last_blackjack": 0, "last_roulette": 0, "last_casino": 0, "last_gamble": 0, "last_bet": 0, "last_race": 0, "last_fight": 0, "last_duel": 0}
        return self.economy_data[uid]

    # -------------------------------
    # Gambling Commands
    # -------------------------------

    # !slots command
        # moved to slots.py cog


async def setup(bot):
    await bot.add_cog(GamblingCog(bot))