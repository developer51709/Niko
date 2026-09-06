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
    print_banner,
    run_slash_sync,
    run_emoji_sync,
    write_bot_stats,
    write_commands,
)

from events.startup.status import (
    set_status,
    start_status_rotation,
)



async def handle_ready(bot):
    """Entry point called by discord.py once the bot has connected and synced.

    Each startup step is wrapped individually so one failure is logged with
    enough detail to diagnose it, while the remaining steps still run.

    This function always returns cleanly to discord.py. If any step fails,
    the failure is captured and recorded on the bot object so it can be
    inspected later without raising back into the gateway.
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

    failed_step_names: list[str] = []
    step_errors: list[tuple[str, BaseException]] = []

    for step_name, description, step in startup_steps:
        try:
            await _run_startup_step(bot, step_name, description, step)
        except BaseException as exc:
            failed_step_names.append(step_name)
            step_errors.append((step_name, exc))
            _log_step_failure(step_name, exc)

    if failed_step_names:
        logging.warning("Startup", f"on_ready finished with {len(failed_step_names)} failed step(s): {', '.join(failed_step_names)}")
    else:
        logging.info("Startup", "on_ready startup tasks completed.")

    _maybe_schedule_rotation_safely(bot)

    if step_errors:
        _record_all_startup_errors(bot, step_errors)
        _emit_summary_traceback(step_errors)
    else:
        # On a fully successful startup, clear any leftover error state from a
        # previous failed run so other code can trust the bot object.
        try:
            bot.startup_errors = []
            bot.last_startup_error = None
        except Exception:
            pass


def _emit_summary_traceback(step_errors: list[tuple[str, BaseException]]) -> None:
    """Print a combined traceback block for all failed startup steps.

    This is intentionally separate from the per-step logging above so the full
    failure picture is written exactly once at the end of startup.
    """
    for step_name, exc in step_errors:
        print(
            f"\n{'=' * 72}\n"
            f"on_ready startup step '{step_name}' failed:\n"
            f"{'=' * 72}\n",
            file=sys.stderr,
        )
        _emit_one_traceback(exc)


def _emit_one_traceback(exc: BaseException) -> None:
    """Write a single exception traceback to stderr."""
    traceback.print_exception(
        type(exc),
        exc,
        exc.__traceback__,
        file=sys.stderr,
    )


def _record_all_startup_errors(bot, step_errors: list[tuple[str, BaseException]]) -> None:
    """Record the first and the last startup error so both are inspectable.

    Callers that only want the most recent failure can look at
    ``bot.last_startup_error``. Callers that want the full list can look at
    ``bot.startup_errors``.
    """
    if not step_errors:
        return

    bot.startup_errors = [error for _, error in step_errors]
    bot.last_startup_error = step_errors[-1][1]


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

        logging.error("Startup", f"Background startup step {step_name} failed: {error}")

    return callback


class StartupTaskSchedulingError(Exception):
    """Raised when a background startup task could not be scheduled."""

    def __init__(self, step_name: str, description: str) -> None:
        super().__init__(
            f"Failed to schedule startup step '{step_name}': {description}"
        )
        self.step_name = step_name
        self.description = description


def _log_step_failure(step_name: str, exc: BaseException) -> None:
    """Log a single failed startup step with a readable traceback."""
    if isinstance(exc, Exception):
        logging.error("Startup", f"Startup step {step_name} failed: {exc}")
        _emit_traceback(exc)
    elif isinstance(exc, BaseException):
        logging.error("Startup", f"Startup step {step_name} failed with a non-Exception BaseException: {exc.__class__.__name__}")
        traceback.print_stack(file=sys.stderr)


def _emit_traceback(exc: BaseException) -> None:
    """Write the exception traceback to the same place discord.py would use."""
    traceback.print_exception(
        type(exc),
        exc,
        exc.__traceback__,
        file=sys.stderr,
    )


def _emit_one_traceback(exc: BaseException) -> None:
    """Write a single exception traceback to stderr."""
    traceback.print_exception(
        type(exc),
        exc,
        exc.__traceback__,
        file=sys.stderr,
    )


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
            logging.debug("Startup", f"Fallback status rotation scheduling did not apply: {exc}")
