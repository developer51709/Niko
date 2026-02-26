# utils/logging.py
# This module contains the logging functions for the bot.
# It is called by other modules to log messages to the the console and handles the log levels and formatting.
# Can be called using the following function:
# log.info(module, message)

import logging
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

# ------------------------------------
# Colors
# ------------------------------------
GRAY = Fore.LIGHTBLACK_EX
CYAN = Fore.CYAN
BOLD = Style.BRIGHT

LEVEL_COLORS = {
    "INFO": Fore.MAGENTA,
    "SUCCESS": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "DEBUG": Fore.CYAN,
}

# ------------------------------------
# Register SUCCESS log level
# ------------------------------------
SUCCESS_LEVEL = 25  # Between WARNING (30) and INFO (20)
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)

logging.Logger.success = success


# ------------------------------------
# Custom Formatter
# ------------------------------------
class CleanFormatter(logging.Formatter):
    def format(self, record):
        level = record.levelname.upper()
        module = record.name
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")

        # Pad level names to fixed width (8 chars)
        padded_level = f"{level:<8}"

        # Colorize level
        level_color = LEVEL_COLORS.get(level, "")
        level_str = f"{level_color}[ {padded_level} ]{Style.RESET_ALL}"

        # Bold cyan module name
        module_str = f"{BOLD}{CYAN}[ {module} ]{Style.RESET_ALL}"

        # Gray timestamp
        timestamp_str = f"{GRAY}{timestamp}{Style.RESET_ALL}"

        return f"{level_str} {module_str} {timestamp_str}: {record.getMessage()}"


# ------------------------------------
# Logger Setup
# ------------------------------------
handler = logging.StreamHandler()
handler.setFormatter(CleanFormatter())

root = logging.getLogger()
root.setLevel(logging.INFO)
root.handlers = [handler]


# ------------------------------------
# Public Logging API
# ------------------------------------
def info(module: str, message: str):
    logging.getLogger(module).info(message)

def success(module: str, message: str):
    logging.getLogger(module).success(message)

def warning(module: str, message: str):
    logging.getLogger(module).warning(message)

def error(module: str, message: str):
    logging.getLogger(module).error(message)

def debug(module: str, message: str):
    logging.getLogger(module).debug(message)