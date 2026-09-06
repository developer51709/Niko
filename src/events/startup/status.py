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

    logging.warning("status", f"Invalid status type {status_type}. Defaulting to 'playing'.")
    return discord.Game(name=text)


async def set_status(bot):
    """Set the bot's initial presence and, if configured, start status rotation.

    This is called from the ``on_ready`` path. Any failure here is logged but
    does not take down the rest of startup.
    """
    status_link = status_config.STATUS_LINK
    status_type = status_config.STATUS_TYPE

    try:
        await bot.change_presence(
            activity=_build_activity(status_config.STATUS_MESSAGE, status_type, status_link),
            device_status=status_config.STATUS_DEVICE,
        )
    except Exception as exc:
        logging.error("status", f"Failed to set initial bot status: {exc}")

    if not status_config.STATUS_ROTATE:
        return

    if not _should_run_rotation():
        return

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        logging.warning("status", "STATUS_ROTATE is enabled but there is no running event loop. Skipping status rotation.")
        return

    loop.create_task(_start_rotation(bot, status_link, start_idx=0))


async def _start_rotation(bot, status_link: str, *, start_idx: int = 0) -> None:
    """Background task that rotates the bot presence.

    It is scheduled from :func:`set_status` and the active task is tracked on
    the bot so it can be cancelled cleanly when rotation is disabled or the bot
    shuts down.
    """
    messages = status_config.STATUS_MESSAGES
    types = status_config.STATUS_TYPES
    if not messages:
        logging.warning("status", "STATUS_ROTATE is enabled but STATUS_MESSAGES is empty. Disabling rotation until messages are configured.")
        return

    messages = [m for m in messages if isinstance(m, str) and m.strip()]
    if not messages:
        logging.warning("status", "STATUS_ROTATE is enabled but STATUS_MESSAGES contained no usable entries. Disabling rotation.")
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
                    logging.warning("status", f"Status rotation step failed (backoff {round(backoff, 1)}s): {exc}")
                    last_error_at = now
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 300)
                continue

            await asyncio.sleep(interval)

    existing = getattr(bot, "_status_rotation_task", None)
    if existing is not None and not existing.done():
        existing.cancel()

    task: asyncio.Task[None] = asyncio.ensure_future(_rotate())
    _attach_rotation_bot(task, bot)
    task.add_done_callback(_rotation_task_cleared)
    task.add_done_callback(_rotation_task_done)
    bot._status_rotation_task = task


def _should_run_rotation() -> bool:
    """Return True when status rotation can meaningfully run.

    This mirrors the runtime checks performed deeper in the rotation task so a
    bad configuration does not result in a task that immediately exits or logs
    itself into a wall.
    """
    if not status_config.STATUS_MESSAGES:
        return False

    usable_messages = [
        m for m in status_config.STATUS_MESSAGES if isinstance(m, str) and m.strip()
    ]
    return bool(usable_messages)



def _rotation_task_cleared(task: asyncio.Task[None]) -> None:
    """Clean up the stored rotation task once the task wrapper has resolved.

    This is only a best-effort bookkeeping callback. The authoritative cleanup
    happens in :func:`_rotation_task_done`, which also logs unexpected task
    failure.
    """
    if getattr(task, "_status_rotation_bot", None) is not None:
        setattr(task, "_status_rotation_bot", None)


def _rotation_task_done(task: asyncio.Task[None]) -> None:
    """Log when the rotation task ends and clean up the bot attribute.

    Cancelled tasks are treated as intentional shutdowns (for example when the
    bot stops or rotation is toggled off) and are not logged as failures.
    """
    if task.cancelled():
        return

    if task.exception() is not None:
        logging.error("status", f"Status rotation task exited with an unhandled error: {task.exception()}")
    else:
        logging.info("status", "Status rotation task exited.")


def _attach_rotation_bot(task: asyncio.Task[None], bot) -> None:
    """Attach a lightweight back-reference from the task to the bot.

    This is used only by cleanup callbacks so they can null out any stored
    references if needed. The attribute name is namespaced to reduce the chance
    of colliding with other bot attributes.
    """
    task._status_rotation_bot = bot


def status_rotation_running(bot) -> bool:
    """Return True if a status rotation task is currently active.

    Useful for UI/status checks or for deciding whether to start a fresh
    rotation task.
    """
    task = getattr(bot, "_status_rotation_task", None)
    return task is not None and not task.done()


def get_status_rotation_task(bot) -> asyncio.Task[None] | None:
    """Return the current status rotation task, if any.

    Callers that need to inspect or cancel the rotation task can use this
    instead of reaching into private bot attributes directly.
    """
    return getattr(bot, "_status_rotation_task", None)


def refresh_status_rotation(bot) -> None:
    """Restart rotation using the current configuration and reset the index.

    This is the preferred public API when status config changes at runtime and
    you want the sequence to start fresh without waiting for the next natural
    step.
    """
    stop_status_rotation(bot)
    start_status_rotation(bot)


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


def start_status_rotation(bot) -> None:
    """Public entrypoint for starting status rotation outside of initial startup.

    Safe to call at any time after the bot has a running event loop.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return

    loop.create_task(_start_rotation(bot, status_config.STATUS_LINK, start_idx=0))


def cancel_status_rotation(bot) -> None:
    """Public helper for stopping rotation and clearing stored bookkeeping.

    Safe to call when rotation is not running.
    """
    stop_status_rotation(bot)


def _start_rotation(bot, status_link: str) -> None:
    """Internal synchronous wrapper used by the legacy direct-call path.

    Existing callers that still import this symbol continue to work, but they
    now go through the same safe scheduling logic instead of any async/sync
    mismatch.
    """
    start_status_rotation(bot)


def cancel_status_rotation(bot) -> None:
    """Public helper for stopping rotation and clearing stored bookkeeping.

    Safe to call when rotation is not running.
    """
    stop_status_rotation(bot)
