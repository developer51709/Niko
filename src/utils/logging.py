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
import requests
import asyncio
import json
import logging
import logging.handlers
import threading
import uuid
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from console_format import ConsoleFormatter
from utils.ai.debugging import send_debug_report

LOG_LEVEL = {
    "AI_DEBUG": logging.ERROR,
    "FILE": logging.DEBUG,
    "WEBHOOK": logging.WARNING
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
# In-memory console buffer (owner live-logs page)
# -----------------------------------
#: Libraries whose DEBUG output is stored in a ring of its own. They can emit
#: far faster than a page reads, and sharing the main ring would push the bot's
#: own lines out of the panel even while the noisy source is hidden.
_NOISY_LOGGERS = ("pymongo", "urllib3", "wavelink")
_NOISE_CAPACITY = 2000


def _noisy_source(name: str) -> str | None:
    """The private ring a logger belongs to, or ``None`` for the main ring."""
    for library in _NOISY_LOGGERS:
        if name == library or name.startswith(f"{library}."):
            return library
    return None


class _QuietSuccessfulRequests(logging.Filter):
    """Drop routine 2xx/3xx Werkzeug access lines, keep request failures.

    The dashboard polls the owner log feed every 1.2 seconds, so logging every
    successful request would make the feed read as its own access log and push
    the bot's real output out of the ring.  The filter is installed on the
    ``werkzeug`` logger once here so every process that serves Flask (the bot
    child and the dashboard child) gets the same behaviour.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        args = getattr(record, "args", ())
        for value in args if isinstance(args, tuple) else ():
            try:
                status = int(value)
            except (TypeError, ValueError):
                continue
            return status >= 400
        return True


class LogBufferHandler(logging.Handler):
    """Keep the rendered console lines in memory for the owner's logs page.

    The lines are stored exactly as the terminal sees them, ANSI colour codes
    included, so the page can reproduce a coloured console instead of a plain
    list. The handler is attached at ``NOTSET``: ``LOG_LEVEL`` filters the
    terminal, not this buffer, and the page applies its own level filter to
    what it shows.

    ``pymongo`` and ``urllib3`` write to their own smaller rings (tagged with
    ``source``) instead of the main one. They remain available to the page
    when its switches are off, but their volume can never evict the bot's own
    lines from the 5,000-line main buffer.

    The buffers live for as long as this module does. A bot restart, or an
    in-place update that reloads ``utils/logging.py``, starts fresh ones, and
    that is the point the page reports as the first available line.
    """

    def __init__(self, capacity: int = 5000, noise_capacity: int = _NOISE_CAPACITY):
        super().__init__(level=logging.NOTSET)
        self.capacity = capacity
        self.noise_capacity = noise_capacity
        # Identifies this buffer to the page. Ids restart at 1 on every fresh
        # buffer, so a page needs this to notice a reload even when the new
        # buffer's head has already passed its old cursor.
        self.token = uuid.uuid4().hex
        self._lines: deque = deque(maxlen=capacity)
        self._noise = {library: deque(maxlen=noise_capacity) for library in _NOISY_LOGGERS}
        # Highest main-ring id evicted so far. The rings share one id sequence,
        # so a gap between ``since`` and the main ring's first id is not proof
        # of loss: the missing ids may simply belong to a noisy library.
        self._main_dropped = 0
        # One sequence across every ring: the page keeps a single cursor, and
        # entries from different rings still sort into the order they arrived.
        self._seq = 0
        self._lock = threading.Lock()
        self._formatter = ConsoleFormatter()
        # Supervised processes share one archive, split by process and level, so
        # the owner's page keeps its history across restarts and can read one
        # process's ERROR buffer without the others.  Unset in a direct run,
        # where the in-memory ring is enough.
        try:
            from log_store import store_from_environment

            self._store = store_from_environment()
        except Exception:
            self._store = None
        self.process = (os.getenv("NIKO_CHILD_NAME") or "bot").strip() or "bot"

    def emit(self, record: logging.LogRecord):
        try:
            line = self._formatter.format(record)
        except Exception:
            self.handleError(record)
            return
        source = _noisy_source(record.name) or "main"
        with self._lock:
            self._seq += 1
            entry = {
                "id": self._seq,
                "at": record.created,
                "level": record.levelname.upper(),
                # The logger that emitted the line, so the page can filter a
                # noisy library without parsing the rendered text.
                "logger": record.name,
                "source": source,
                "line": line,
            }
            if source == "main":
                if len(self._lines) == self._lines.maxlen:
                    self._main_dropped = self._lines[0]["id"]
                self._lines.append(entry)
            else:
                self._noise[source].append(entry)
        store = getattr(self, "_store", None)
        if store is not None:
            try:
                store.append(
                    level=record.levelname,
                    logger=record.name,
                    line=line,
                    process=self.process,
                    source=source,
                    at=record.created,
                )
            except Exception:
                # The console must never fail because the shared copy did.
                pass

    def snapshot(self, since: int = 0, limit: int = 2000) -> dict:
        """Return buffered lines after ``since``, oldest first.

        Entries from every ring are merged and sorted by their shared id, so a
        single cursor sees the whole stream. ``reset`` tells a page whose
        cursor belongs to an earlier buffer (the process restarted, or an
        update reloaded this module) to clear what it already shows and start
        again from the new buffer's first line.
        """
        with self._lock:
            head = self._seq
            pools = [self._lines, *self._noise.values()]
            firsts = [pool[0]["id"] for pool in pools if pool]
            main_dropped = self._main_dropped
            entries = [
                entry
                for pool in pools
                for entry in pool
                if entry["id"] > since
            ]
            entries.sort(key=lambda entry: entry["id"])
        first = min(firsts) if firsts else None
        # Only the main ring drives the warning: a noisy library rolling its
        # own private ring must not tell the owner that visible logs were lost.
        truncated = main_dropped > since
        returned = entries[:max(1, int(limit))]
        next_id = returned[-1]["id"] if returned else max(0, head)
        return {
            "lines": returned,
            "head": head,
            "next": next_id,
            "first": first,
            "token": self.token,
            "capacity": self.capacity,
            "noise_capacity": self.noise_capacity,
            "truncated": truncated,
            "reset": since > head,
        }


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
class WebhookHandler(logging.Handler):
    """
    Sends log records to a Discord webhook.
    Automatically censors the webhook URL in all logs.
    """

    _executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="webhook-log")

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

    def _send(self, payload: dict):
        try:
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

    def emit(self, record: logging.LogRecord):
        try:
            payload = self._build_payload(record)
            # Offload the network call so we never block the event loop
            self._executor.submit(self._send, payload)
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
# AI Debugging Handler
# -----------------------------------
class AIDebugHandler(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.ERROR)
        self.setFormatter(logging.Formatter())
        self.bot = None

    def emit(self, record: logging.LogRecord):
        if self.bot is None:
            from main import bot
            self.bot = bot
        try:
            # pass the full exception
            error = record.exc_info[1] if record.exc_info else record.getMessage
            asyncio.create_task(send_debug_report(self.bot, error))
        except Exception:
            pass



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

# The owner's live-logs page reads this buffer. It sits at NOTSET so a debug
# line the console's environment level hides is still available on the page.
log_buffer = LogBufferHandler()
root.addHandler(log_buffer)

# Werkzeug access lines: a successful request is not application output.  Keep
# failures (4xx/5xx), which are the ones worth seeing, and hide the rest before
# they reach the console, the shared store, or the owner's live feed.
_werkzeug_logger = logging.getLogger("werkzeug")
_werkzeug_logger.setLevel(logging.INFO)
if not any(isinstance(item, _QuietSuccessfulRequests) for item in _werkzeug_logger.filters):
    _werkzeug_logger.addFilter(_QuietSuccessfulRequests())

# AI debugging handler
# uses the send_debug_report function to send logs to the AI debug channel
ai_debug_handler = AIDebugHandler()
ai_debug_handler.setLevel(LOG_LEVEL["AI_DEBUG"])
ai_debug_handler.setFormatter(logging.Formatter())

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
    _file_handler.setLevel(LOG_LEVEL["FILE"])
    _file_handler.setFormatter(FileFormatter())
    root.addHandler(_file_handler)

# Optional webhook logging
webhook_url = os.getenv("LOGGING_WEBHOOK")
if webhook_url:
    webhook_handler = WebhookHandler(webhook_url)
    webhook_handler.setLevel(LOG_LEVEL["WEBHOOK"])
    root.addHandler(webhook_handler)

# ── Suppress discord.py's default log setup ─────────────────────────────────
# discord.py will try to add its own StreamHandler in bot.run() unless we pass
# log_handler=None.  We also quiet the internal loggers that generate routine
# noise (especially rate-limit warnings triggered by bulk operations) so the
# console only shows output from our own custom logging calls.
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("discord.client").setLevel(logging.WARNING)
logging.getLogger("discord.gateway").setLevel(logging.WARNING)
logging.getLogger("discord.voice_client").setLevel(logging.WARNING)
# discord.http logs a WARNING for every rate-limit hit (e.g. bulk-delete).
# Set to ERROR so routine bulk-operation throttling stays off the console.
logging.getLogger("discord.http").setLevel(logging.ERROR)
logging.getLogger("discord.player").setLevel(logging.WARNING)


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
