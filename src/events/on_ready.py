"""
Startup handler for the Discord bot.

Orchestrates all startup tasks via modular imports from events.startup.
Each startup step is executed and reported independently so a single failure
does not prevent the remaining startup work from running.
"""

import asyncio
import sys
import traceback
from typing import Any

from utils import logging
from events.startup import (
    init_database,
    load_cogs,
    set_status,
    print_banner,
    run_slash_sync,
    run_emoji_sync,
    write_bot_stats,
    write_commands,
)


async def handle_ready(bot):
    """Entry point called by discord.py once the bot has connected and synced.

    Each startup step is wrapped individually so one failure is logged with
    enough detail to diagnose it, while the remaining steps still run.
    """
    logging.info("Startup", f"Niko is online as {bot.user}")

    startup_steps: list[
        tuple[str, str, Any]
    ] = [
        ("init_database", "Initializing the database", init_database),
        ("load_cogs", "Loading cogs", load_cogs),
        ("set_status", "Setting bot status / presence", set_status),
        ("print_banner", "Printing startup banner", print_banner),
        ("write_bot_stats", "Writing bot stats", write_bot_stats),
        ("write_commands", "Writing command data", write_commands),
        ("run_emoji_sync", "Scheduling emoji sync", run_emoji_sync),
        ("run_slash_sync", "Scheduling slash command sync", run_slash_sync),
    ]

    failed_steps: list[str] = []
    last_error: BaseException | None = None

    for step_name, description, step in startup_steps:
        try:
            await _run_startup_step(bot, step_name, description, step)
        except Exception as exc:
            failed_steps.append(step_name)
            last_error = exc
            _log_step_failure(step_name, exc)

    if failed_steps:
        logging.warning(
            "Startup",
            "on_ready finished with %d failed step(s): %s",
            len(failed_steps),
            ", ".join(failed_steps),
        )
    else:
        logging.info("Startup", "on_ready startup tasks completed.")

    _maybe_schedule_rotation_safely(bot)

    if last_error is not None:
        _record_last_startup_error(bot, last_error)


async def _run_startup_step(bot, step_name: str, description: str, step: Any) -> None:
    """Run one startup step and surface its outcome clearly.

    Synchronous startup helpers are called directly. Async helpers are awaited.
    Background-only steps are scheduled as tasks and are not treated as failures
    if scheduling succeeds.
    """
    if step_name in {"run_emoji_sync", "run_slash_sync"}:
        try:
            task = asyncio.create_task(step(bot))
            task.add_done_callback(_make_startup_task_callback(step_name))
        except Exception as exc:
            raise StartupTaskSchedulingError(step_name, description) from exc
        return

    if asyncio.iscoroutinefunction(step):
        await step(bot)
    else:
        step(bot)


def _make_startup_task_callback(step_name: str):
    """Create a done callback that logs unexpected failures for background tasks."""

    def callback(task: asyncio.Task[Any]) -> None:
        if task.cancelled():
            return

        error = task.exception()
        if error is None:
            return

        logging.error(
            "Startup",
            "Background startup step %s failed: %s",
            step_name,
            error,
            exc_info=True,
        )

    return callback


class StartupTaskSchedulingError(Exception):
    """Raised when a background startup task could not be scheduled."""

    def __init__(self, step_name: str, description: str) -> None:
        super().__init__(
            f"Failed to schedule startup step '{step_name}': {description}"
        )
        self.step_name = step_name
        self.description = description


def _log_step_failure(step_name: str, exc: Exception) -> None:
    """Log a single failed startup step with a readable traceback."""
    logging.error(
        "Startup",
        "Startup step %r failed: %s",
        step_name,
        exc,
    )
    _emit_traceback(exc)


def _emit_traceback(exc: BaseException) -> None:
    """Write the exception traceback to the same place discord.py would use."""
    traceback.print_exception(
        type(exc),
        exc,
        exc.__traceback__,
        file=sys.stderr,
    )


def _record_last_startup_error(bot, exc: BaseException) -> None:
    """Attach the last startup error to the bot for later inspection.

    Other parts of the bot can read ``bot.last_startup_error`` to decide
    whether startup completed cleanly or not.
    """
    bot.last_startup_error = exc


def _maybe_schedule_rotation_safely(bot) -> None:
    """Best-effort fallback that schedules rotation only when nothing else did.

    This keeps the legacy ``on_ready`` path from leaving an unconsumed coroutine
    in the event loop if ``set_status`` was changed later.
    """
    if getattr(bot, "_status_rotation_task", None) is None:
        try:
            from events.startup.status import start_status_rotation as _start_rotation_sync
            if callable(_start_rotation_sync):
                _start_rotation_sync(bot)
        except Exception as exc:
            logging.debug(
                "Startup",
                "Fallback status rotation scheduling did not apply: %s",
                exc,
            )
