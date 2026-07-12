"""
Startup — Discord presence / status setter.
"""

import os

import discord
from utils import logging


async def set_status(bot):
    status_link = os.getenv("STATUS_LINK")
    if status_link:
        if not (status_link.startswith("http://") or status_link.startswith("https://")):
            status_link = f"https://{status_link}"
    else:
        status_link = "https://twitch.tv/niko"

    status = os.getenv("STATUS_MESSAGE")
    status_type = os.getenv("STATUS_TYPE", "playing").lower()

    if status:
        if status_type == "playing":
            activity = discord.Game(name=status)
        elif status_type == "streaming":
            activity = discord.Streaming(name=status, url=status_link)
        elif status_type == "listening":
            activity = discord.Activity(type=discord.ActivityType.listening, name=status)
        elif status_type == "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=status)
        else:
            logging.warning("RPC", "Invalid status type. Defaulting to 'playing'.")
            activity = discord.Game(name=status)

        await bot.change_presence(activity=activity)
