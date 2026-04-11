# utils/logging.py
# Configurable logging system for Niko.
#
# Environment variables:
#   LOG_LEVEL        – console log level: DEBUG / INFO / WARNING / ERROR  (default: INFO)
#   LOG_TO_FILE      – set to "true" to enable file logging                (default: false)
#   LOG_FILE         – path for the log file                               (default: logs/niko.log)
#   LOG_MAX_BYTES    – max size before rotation in bytes                   (default: 5242880 = 5 MB)
#   LOG_BACKUP_COUNT – number of rotated backups to keep                   (default: 3)

import os
import logging
import logging.handlers
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

# -----------------------------------
# Colors
# -----------------------------------
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

# -----------------------------------
# Register SUCCESS log level
# -----------------------------------
SUCCESS_LEVEL = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

def _success_method(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)

logging.Logger.success = _success_method


# -----------------------------------
# Console formatter (colourised)
# -----------------------------------
class ConsoleFormatter(logging.Formatter):
    def format(self, record):
        level = record.levelname.upper()
        module = record.name
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")

        padded_level = f"{level:<8}"
        level_color  = LEVEL_COLORS.get(level, "")
        level_str    = f"{level_color}[ {padded_level} ]{Style.RESET_ALL}"
        module_str   = f"{BOLD}{CYAN}[ {module} ]{Style.RESET_ALL}"
        timestamp_str = f"{GRAY}{timestamp}{Style.RESET_ALL}"

        return f"{level_str} {module_str} {timestamp_str}: {record.getMessage()}"


# -----------------------------------
# File formatter (plain text)
# -----------------------------------
class FileFormatter(logging.Formatter):
    def format(self, record):
        level = record.levelname.upper()
        return (
            f"[{level:<8}] [{record.name}] "
            f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S')}: {record.getMessage()}"
        )


# -----------------------------------
# Read config from environment
# -----------------------------------
def _parse_level(name: str, default: int) -> int:
    mapping = {
        "DEBUG":   logging.DEBUG,
        "INFO":    logging.INFO,
        "SUCCESS": SUCCESS_LEVEL,
        "WARNING": logging.WARNING,
        "ERROR":   logging.ERROR,
    }
    return mapping.get(name.upper(), default)


_console_level = _parse_level(os.getenv("LOG_LEVEL", "INFO"), logging.INFO)
_file_enabled  = os.getenv("LOG_TO_FILE", "false").lower() in ("1", "true", "yes")
_log_file      = os.getenv("LOG_FILE", "logs/niko.log")
_max_bytes     = int(os.getenv("LOG_MAX_BYTES", str(5 * 1024 * 1024)))
_backup_count  = int(os.getenv("LOG_BACKUP_COUNT", "3"))


# -----------------------------------
# Webhook logging handler
# -----------------------------------
import json
import requests

class WebhookHandler(logging.Handler):
    """
    Sends log records to a Discord webhook.
    Automatically censors the webhook URL in all logs.
    """

    def __init__(self, url: str):
        super().__init__(level=logging.INFO)
        self.webhook_url = url
        self.censored_url = self._censor(url)
        self.setFormatter(logging.Formatter())

    @staticmethod
    def _censor(url: str) -> str:
        # https://discord.com/api/webhooks/<id>/<token>
        parts = url.split("/")
        if len(parts) < 2:
            return "***"
        return "/".join(parts[:-1] + ["***"])

    def emit(self, record: logging.LogRecord):
        try:
            payload = self._build_payload(record)
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=5
            )

            if response.status_code >= 400:
                root.error(
                    "WebhookHandler",
                    f"Discord rejected webhook payload ({response.status_code}): "
                    f"{response.text}"
                )

        except Exception as exc:
            root.error(
                "WebhookHandler",
                f"Webhook logging failed: {exc}"
            )

    def _build_payload(self, record: logging.LogRecord) -> dict:
        level = record.levelname.upper()
        fmt = self.formatter or logging.Formatter()
        timestamp = fmt.formatTime(record, "%Y-%m-%d %H:%M:%S")

        color_map = {
            "DEBUG":   0x3498db,
            "INFO":    0x9b59b6,
            "SUCCESS": 0x2ecc71,
            "WARNING": 0xf1c40f,
            "ERROR":   0xe74c3c,
        }

        embed = {
            "title": f"{level} — {record.name}",
            "description": record.getMessage(),
            "color": color_map.get(level, 0x95a5a6),
            "footer": {"text": timestamp},
        }

        return {"embeds": [embed]}


# -----------------------------------
# Root logger setup
# -----------------------------------
root = logging.getLogger()
root.setLevel(logging.DEBUG)           # capture everything; handlers filter

# Console handler
_console_handler = logging.StreamHandler()
_console_handler.setLevel(_console_level)
_console_handler.setFormatter(ConsoleFormatter())
root.handlers = [_console_handler]

# Optional file handler
if _file_enabled:
    _log_dir = os.path.dirname(_log_file)
    if _log_dir:
        os.makedirs(_log_dir, exist_ok=True)
    _file_handler = logging.handlers.RotatingFileHandler(
        _log_file,
        maxBytes=_max_bytes,
        backupCount=_backup_count,
        encoding="utf-8",
    )
    _file_handler.setLevel(logging.DEBUG)
    _file_handler.setFormatter(FileFormatter())
    root.addHandler(_file_handler)

# Optional webhook logging
webhook_url = os.getenv("LOGGING_WEBHOOK")
if webhook_url:
    webhook_handler = WebhookHandler(webhook_url)
    root.addHandler(webhook_handler)


# -----------------------------------
# Runtime configuration helpers
# -----------------------------------
def set_console_level(level: str):
    """Dynamically change the console log level (e.g. 'DEBUG', 'WARNING')."""
    _console_handler.setLevel(_parse_level(level, logging.INFO))


def enable_file_logging(path: str = "logs/niko.log",
                        max_bytes: int = 5 * 1024 * 1024,
                        backup_count: int = 3):
    """Attach a rotating file handler at runtime."""
    log_dir = os.path.dirname(path)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    fh = logging.handlers.RotatingFileHandler(
        path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(FileFormatter())
    root.addHandler(fh)


# -----------------------------------
# Public logging API
# -----------------------------------
def debug(module: str, message: str):
    logging.getLogger(module).debug(message)

def info(module: str, message: str):
    logging.getLogger(module).info(message)

def success(module: str, message: str):
    logging.getLogger(module).success(message)

def warning(module: str, message: str):
    logging.getLogger(module).warning(message)

def error(module: str, message: str):
    logging.getLogger(module).error(message)
