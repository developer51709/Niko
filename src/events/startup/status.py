"""
Startup — Discord presence / status setter.

Status configuration is read from src.config.status so it can be edited in one
place instead of via environment variables. Multi-message rotation is supported
when STATUS_ROTATE is enabled in that config.
"""

import asyncio

import discord
from utils import logging

from config import status as status_config


def _build_activity(text: str, status_type: str, status_link: str) -> discord.BaseActivity:
    status_type = status_type.lower()
    normalized_link = status_link.strip()
    if normalized_link and not (
        normalized_link.startswith("http://") or normalized_link.startswith("https://")
    ):
        normalized_link = f"https://{normalized_link}"

    if status_type == "playing":
        return discord.Game(name=text)
    if status_type == "streaming":
        return discord.Streaming(name=text, url=normalized_link)
    if status_type == "listening":
        return discord.Activity(type=discord.ActivityType.listening, name=text)
    if status_type == "watching":
        return discord.Activity(type=discord.ActivityType.watching, name=text)
    if status_type == "competing":
        return discord.Activity(type=discord.ActivityType.competing, name=text)

    logging.warning(
        "RPC",
        "Invalid status type %r. Defaulting to 'playing'.",
        status_type,
    )
    return discord.Game(name=text)


async def set_status(bot):
    status_link = status_config.STATUS_LINK
    status_type = status_config.STATUS_TYPE

    await bot.change_presence(
        activity=_build_activity(status_config.STATUS_MESSAGE, status_type, status_link),
        device_status=status_config.STATUS_DEVICE,
    )

    if status_config.STATUS_ROTATE:
        _start_rotation(bot, status_link)


def _start_rotation(bot, status_link: str) -> None:
    messages = status_config.STATUS_MESSAGES
    types = status_config.STATUS_TYPES
    if not messages:
        return

    interval = max(status_config.STATUS_INTERVAL, 5)
    idx = 0

    async def _rotate():
        nonlocal idx
        while True:
            text = messages[idx % len(messages)]
            kind = types[idx % len(types)] if types else status_config.STATUS_TYPE
            await bot.change_presence(
                activity=_build_activity(text, kind, status_link),
                device_status=status_config.STATUS_DEVICE,
            )
            idx += 1
            await asyncio.sleep(interval)

    asyncio.ensure_future(_rotate())
