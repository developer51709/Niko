"""The console line style shared by the bot and the supervisor.

Both processes write to the same terminal, so they render through the same
formatter: a dim clock, a right-padded level label in the level's colour, and a
right-padded module name.  Kept standalone (no app imports) so the supervisor
can use it without configuring the bot's logging handlers.
"""

from __future__ import annotations

import logging

from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

GRAY = Fore.LIGHTBLACK_EX
CYAN = Fore.CYAN
BOLD = Style.BRIGHT

LEVEL_COLORS = {
    "DEBUG":   Fore.CYAN,
    "INFO":    Fore.MAGENTA,
    "SUCCESS": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR":   Fore.RED,
}

LEVEL_LABELS = {
    "DEBUG":   "DEBUG",
    "INFO":    "INFO",
    "SUCCESS": "SUCCESS",
    "WARNING": "WARNING",
    "ERROR":   "ERROR",
}


class ConsoleFormatter(logging.Formatter):
    _LEVEL_WIDTH  = 7    # longest label is "WARNING" / "SUCCESS" = 7
    _MODULE_WIDTH = 18   # module name column

    def format(self, record):
        level  = record.levelname.upper()
        module = record.name
        time   = self.formatTime(record, "%H:%M:%S")

        level_color = LEVEL_COLORS.get(level, "")
        label       = LEVEL_LABELS.get(level, level)

        time_part   = f"{GRAY}{time}{Style.RESET_ALL}"
        level_part  = f"{level_color}{Style.BRIGHT}{label:<{self._LEVEL_WIDTH}}{Style.RESET_ALL}"
        module_part = f"{BOLD}{CYAN}{module:<{self._MODULE_WIDTH}}{Style.RESET_ALL}"
        msg_part    = f"{level_color}{record.getMessage()}{Style.RESET_ALL}"

        line = f"  {time_part}  {level_part}  {module_part}  {msg_part}"
        # Tracebacks are part of the message. A formatter that returns only the
        # first line turns every "Ignoring exception" into an unreadable rumour.
        detail = self.formatException(record.exc_info) if record.exc_info else record.exc_text
        if detail:
            line = f"{line}\n{GRAY}{detail}{Style.RESET_ALL}"
        if record.stack_info:
            line = f"{line}\n{GRAY}{self.formatStack(record.stack_info)}{Style.RESET_ALL}"
        return line
