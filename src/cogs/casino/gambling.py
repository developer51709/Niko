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

    # Legacy methods for compatibility - now use database
    def load_economy_data(self):
        # This cog now uses the main economy cog's database
        return {}

    def save_economy_data(self):
        # This cog now uses the main economy cog's database
        pass

    async def get_user_economy_data(self, user_id):
        # Use the main economy cog
        economy = self.bot.get_cog("EconomyCog")
        if economy:
            return await economy.get_user_economy_data(user_id)
        return {"balance": 0, "inventory": [], "bank": 0, "net_worth": 0, "daily_streak": 0, "last_daily": 0, "last_work": 0, "last_crime": 0, "last_rob": 0, "last_heist": 0, "last_slots": 0, "last_blackjack": 0, "last_roulette": 0, "last_casino": 0, "last_gamble": 0, "last_bet": 0, "last_race": 0, "last_fight": 0, "last_duel": 0}

    # -------------------------------
    # Gambling Commands
    # -------------------------------

    # !slots command
        # moved to slots.py cog


async def setup(bot):
    await bot.add_cog(GamblingCog(bot))