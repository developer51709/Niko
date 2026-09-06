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
    status_type = (status_type or "").strip().lower()
    if not text or not text.strip():
        text = "Niko"

    normalized_link = (status_link or "").strip()
    if normalized_link and not (
        normalized_link.startswith("http://") or normalized_link.startswith("https://")
    ):
        normalized_link = f"https://{normalized_link}"

    if status_type == "playing":
        return discord.Game(name=text)
    if status_type == "streaming":
        return discord.Streaming(name=text, url=normalized_link or "https://twitch.tv/niko")
    if status_type == "listening":
        return discord.Activity(type=discord.ActivityType.listening, name=text)
    if status_type == "watching":
        return discord.Activity(type=discord.ActivityType.watching, name=text)
    if status_type == "competing":
        return discord.Activity(type=discord.ActivityType.competing, name=text)

    logging.warning(
        "status",
        "Invalid status type %r. Defaulting to 'playing'.",
        status_type,
    )
    return discord.Game(name=text)


async def set_status(bot):
    status_link = status_config.STATUS_LINK
    status_type = status_config.STATUS_TYPE

    try:
        await bot.change_presence(
            activity=_build_activity(status_config.STATUS_MESSAGE, status_type, status_link),
            device_status=status_config.STATUS_DEVICE,
        )
    except Exception as exc:
        logging.error(
            "status",
            "Failed to set initial bot status: %s",
            exc,
        )

    if status_config.STATUS_ROTATE:
        _start_rotation(bot, status_link)


async def _start_rotation(bot, status_link: str, *, start_idx: int = 0) -> None:
    """Start a background task that rotates the bot presence.

    The task is stored on the bot so it can be cancelled cleanly when status
    rotation is toggled off. If rotation is already running it is replaced so
    config changes take effect immediately.
    """
    messages = status_config.STATUS_MESSAGES
    types = status_config.STATUS_TYPES
    if not messages:
        logging.warning(
            "status",
            "STATUS_ROTATE is enabled but STATUS_MESSAGES is empty. "
            "Disabling rotation until messages are configured.",
        )
        return

    messages = [m for m in messages if isinstance(m, str) and m.strip()]
    if not messages:
        logging.warning(
            "status",
            "STATUS_ROTATE is enabled but STATUS_MESSAGES contained no usable entries. "
            "Disabling rotation.",
        )
        return

    if types is not None:
        types = [t for t in types if isinstance(t, str) and t.strip()]
    else:
        types = []

    interval = max(status_config.STATUS_INTERVAL, 5)
    idx = start_idx

    async def _rotate():
        nonlocal idx
        last_error_at = 0.0
        backoff = interval

        while True:
            try:
                text = messages[idx % len(messages)]
                kind = (
                    types[idx % len(types)]
                    if types
                    else status_config.STATUS_TYPE
                )

                activity = _build_activity(text, kind, status_link)
                await bot.change_presence(
                    activity=activity,
                    device_status=status_config.STATUS_DEVICE,
                )
                idx += 1
                backoff = max(interval, backoff / 2)
                last_error_at = 0.0
            except Exception as exc:
                now = asyncio.get_event_loop().time()
                if now - last_error_at >= 60:
                    logging.warning(
                        "status",
                        "Status rotation step failed (backoff %ss): %s",
                        round(backoff, 1),
                        exc,
                    )
                    last_error_at = now
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 300)
                continue

            await asyncio.sleep(interval)

    existing = getattr(bot, "_status_rotation_task", None)
    if existing is not None and not existing.done():
        existing.cancel()

    task: asyncio.Task[None] = asyncio.ensure_future(_rotate())
    task.add_done_callback(_rotation_task_cleared)
    task.add_done_callback(_rotation_task_done)
    bot._status_rotation_task = task




def _rotation_task_cleared(task: asyncio.Task[None]) -> None:
    """Clean up the stored rotation task once the task wrapper has resolved."""
    bot = getattr(task, "_rotation_bot", None)
    if bot is not None:
        setattr(bot, "_status_rotation_task", None)


def _rotation_task_done(task: asyncio.Task[None]) -> None:
    """Log when the rotation task ends and clean up the bot attribute.

    Cancelled tasks are treated as intentional shutdowns (for example when the
    bot stops or rotation is toggled off) and are not logged as failures.
    """
    if task.cancelled():
        return

    if task.exception() is not None:
        logging.error(
            "status",
            "Status rotation task exited with an unhandled error: %s",
            task.exception(),
        )
    else:
        logging.info("status", "Status rotation task exited.")


def stop_status_rotation(bot) -> None:
    """Cancel any running status rotation task.

    This is safe to call even when rotation is not active or has already
    stopped. It exists so other parts of the bot can cleanly tear down status
    rotation without reaching into private internals.
    """
    existing = getattr(bot, "_status_rotation_task", None)
    if existing is None or existing.done():
        return

    existing.cancel()


def _start_rotation(bot, status_link: str) -> None:
    """Legacy entrypoint kept for direct callers that do not pass start_idx.

    Delegates to the full implementation in :func:`_start_rotation` so existing
    callers still receive the improved error handling and task management.
    """
    _start_rotation(bot, status_link, start_idx=0)
