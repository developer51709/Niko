"""Live status data for the website's ``/status`` page.

Three kinds of reading live here, and they are collected differently:

- **Bot and shards** have to be read on the Discord event loop, so the route
  hands :func:`bot_status` to ``run_on_bot_loop``. Nothing here touches SQLite
  or Discord's REST API, so the snapshot stays cheap enough for a page that
  polls it every few seconds.
- **Host** figures come from ``psutil`` in whichever thread asks, and cost
  microseconds.
- **Locale coverage** walks every ``locales`` folder and ``data/commands.json``.
  That is a hundred-odd small JSON reads, so the result is cached for a minute:
  translation files change when someone edits them, not between two polls.

Cog states come from ``bot.cog_status``, which the startup loader writes as each
extension is loaded, skipped or fails.
"""

from __future__ import annotations

import json
import math
import os
import platform
import time
from pathlib import Path

try:
    import psutil
except Exception:  # pragma: no cover - psutil is a hard dependency of the bot
    psutil = None

from .commands import (
    _LEGACY_INTERNAL_COMMAND_NAMES,
    _is_internal_command,
    _live_internal_command_names,
)

#: Every language the bot ships, in the order the site shows them.
LANGUAGES = ("en", "de", "es", "fr")
LANGUAGE_LABELS = {"en": "English", "de": "German", "es": "Spanish", "fr": "French"}

#: The website's own per-page catalogues (``web/src/locales/<page>/<lang>.json``).
SITE_LOCALES = Path("web/src/locales")

#: How long the translation scan is reused, in seconds.
_LOCALE_TTL = 60.0
_locale_cache: dict = {"at": 0.0, "payload": None}


# ──────────────────────────────────────────────────────────────────────────────
# Locale coverage
# ──────────────────────────────────────────────────────────────────────────────
def _leaf_keys(value, prefix: str = "") -> list[str]:
    """Flatten a locale table into leaf keys.

    A locale value is a string or a list of strings (roleplay keeps its sentence
    variants in lists); both count as one translation. Empty strings count as
    missing, because an empty reply is what a translator leaves behind.
    """
    keys: list[str] = []
    if isinstance(value, dict):
        for name, child in value.items():
            keys.extend(_leaf_keys(child, f"{prefix}.{name}" if prefix else str(name)))
    elif isinstance(value, list):
        if any(isinstance(item, str) and item.strip() for item in value):
            keys.append(prefix)
    elif isinstance(value, str):
        if value.strip():
            keys.append(prefix)
    return keys


def _locale_dirs() -> list[Path]:
    """Every folder that holds a shipped ``<lang>.json`` catalogue."""
    found = [path for path in Path("src").glob("**/locales") if path.is_dir()]
    return sorted(found)


def _bot_locale_status() -> list[dict]:
    """Per-language coverage of the bot's own wording.

    Counted per catalogue, not by leaf key: two cogs both have an ``error`` key
    and they are different strings, so a set of bare keys across the whole bot
    would undercount the English total and could report more than 100% covered.
    """
    total = 0
    translated: dict[str, int] = {code: 0 for code in LANGUAGES}
    catalogues = 0

    for folder in _locale_dirs():
        english_file = folder / "en.json"
        if not english_file.exists():
            continue
        try:
            english_keys = set(_leaf_keys(json.loads(english_file.read_text(encoding="utf-8"))))
        except Exception:
            continue
        catalogues += 1
        total += len(english_keys)
        translated["en"] += len(english_keys)
        for code in LANGUAGES:
            if code == "en":
                continue
            path = folder / f"{code}.json"
            if not path.exists():
                continue
            try:
                keys = set(_leaf_keys(json.loads(path.read_text(encoding="utf-8"))))
            except Exception:
                continue
            translated[code] += len(english_keys & keys)

    return [
        _coverage_row(code, translated[code], total, extra={"catalogues": catalogues})
        for code in LANGUAGES
    ]


def _website_locale_status() -> list[dict]:
    """Per-language coverage of the website's own page catalogues.

    Every page ships a catalogue folder (``web/src/locales/<page>``), the same
    way it ships an Open Graph card, and ``en.json`` inside it is the source
    copy. Measuring the bot's command descriptions here was what made the website
    look fully translated while none of its own copy was: those strings belong to
    the command catalogue, not to the site's interface.

    A page is only counted as done (``complete_pages``) when its file for that
    language covers every key its ``en.json`` has — a translation someone started
    and stopped is still partial, however many keys it filled in.
    """
    total = 0
    translated: dict[str, int] = {code: 0 for code in LANGUAGES}
    complete: dict[str, int] = {code: 0 for code in LANGUAGES}
    pages = 0

    if SITE_LOCALES.is_dir():
        for folder in sorted(path for path in SITE_LOCALES.iterdir() if path.is_dir()):
            english_file = folder / "en.json"
            if not english_file.exists():
                continue
            try:
                english_keys = set(_leaf_keys(json.loads(english_file.read_text(encoding="utf-8"))))
            except Exception:
                continue
            pages += 1
            total += len(english_keys)
            translated["en"] += len(english_keys)
            # ``en.json`` is the source copy, so a page that has any at all is
            # translated into English by definition.
            if english_keys:
                complete["en"] += 1
            for code in LANGUAGES:
                if code == "en":
                    continue
                path = folder / f"{code}.json"
                if not path.exists():
                    continue
                try:
                    keys = set(_leaf_keys(json.loads(path.read_text(encoding="utf-8"))))
                except Exception:
                    continue
                translated[code] += len(english_keys & keys)
                if english_keys and english_keys <= keys:
                    complete[code] += 1

    return [
        _coverage_row(
            code,
            translated[code],
            total,
            extra={"pages": pages, "complete_pages": complete[code]},
        )
        for code in LANGUAGES
    ]


def _coverage_row(code: str, done: int, total: int, extra: dict | None = None) -> dict:
    percent = round((done / total) * 100, 1) if total else 0.0
    row = {
        "code": code,
        "label": LANGUAGE_LABELS.get(code, code.upper()),
        "translated": done,
        "total": total,
        "missing": max(total - done, 0),
        "percent": percent,
    }
    if extra:
        row.update(extra)
    return row


def locale_status(force: bool = False) -> dict:
    """Bot and website translation coverage, cached for a minute."""
    now = time.monotonic()
    if not force and _locale_cache["payload"] and now - _locale_cache["at"] < _LOCALE_TTL:
        return _locale_cache["payload"]
    payload = {
        "languages": list(LANGUAGES),
        "bot": _bot_locale_status(),
        "website": _website_locale_status(),
        "scanned_at": int(time.time()),
    }
    _locale_cache.update({"at": now, "payload": payload})
    return payload


# ──────────────────────────────────────────────────────────────────────────────
# Host
# ──────────────────────────────────────────────────────────────────────────────
def _latency_ms(value) -> int | None:
    """A gateway latency in whole milliseconds, or ``None`` when not measured.

    discord.py reports ``inf`` until a shard has completed a heartbeat and ``nan``
    in a few reconnect paths, and ``round`` raises on ``inf``. The page draws an
    unknown latency as an em dash, so both become ``None``.
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return round(number * 1000) if math.isfinite(number) else None


def _gb(value: int) -> float:
    return round(value / (1024 ** 3), 2)


def _registry_commands() -> list:
    """The exported command registry the commands page renders."""
    try:
        data = json.loads(Path("data/commands.json").read_text(encoding="utf-8"))
    except Exception:
        return []
    return data if isinstance(data, list) else []


def _live_command_count(bot) -> int:
    """Every command the running bot registers, subcommands included."""
    count = 0
    try:
        count += sum(1 for _ in bot.walk_commands())
    except Exception:
        pass

    def visit(command) -> None:
        nonlocal count
        count += 1
        for child in getattr(command, "commands", ()) or ():
            visit(child)

    try:
        for command in bot.tree.get_commands():
            visit(command)
    except Exception:
        pass
    return count


def _public_command_count(bot) -> int:
    """The command total the landing page and the commands page show.

    Those pages count the exported registry, which lists nested slash commands
    and user/message context menus as their own commands and drops the private
    owner and development cogs. ``bot.commands`` only holds top-level prefix
    and hybrid commands, so counting it here would under-report the same bot.
    """
    cached = getattr(bot, "_status_command_count", None)
    if isinstance(cached, int) and cached > 0:
        return cached

    registry = _registry_commands()
    if registry:
        internal_names = _live_internal_command_names()
        return sum(
            1 for command in registry
            if isinstance(command, dict)
            and command.get("name")
            and not _is_internal_command(command.get("cog"), command.get("module"))
            and str(command["name"]) not in internal_names
            and str(command["name"]).lower() not in _LEGACY_INTERNAL_COMMAND_NAMES
        )

    try:
        saved = json.loads(Path("data/bot_stats.json").read_text(encoding="utf-8")).get("command_count")
    except Exception:
        saved = None
    if isinstance(saved, int) and saved > 0:
        return saved
    # Before the first registry export, count what the bot has loaded so the
    # page shows a real figure instead of a stale one.
    return _live_command_count(bot)


def host_stats() -> dict:
    """CPU, memory, disk and process figures for the machine running the bot."""
    data: dict = {
        "platform": f"{platform.system()} {platform.release()}",
        "python": platform.python_version(),
        "pid": os.getpid(),
        "cores": os.cpu_count(),
    }
    if psutil is None:
        return data

    try:
        memory = psutil.virtual_memory()
        data["memory"] = {
            "used_gb": _gb(memory.total - memory.available),
            "total_gb": _gb(memory.total),
            "percent": memory.percent,
        }
    except Exception:
        pass
    try:
        disk = psutil.disk_usage(os.getcwd())
        data["disk"] = {
            "used_gb": _gb(disk.used),
            "total_gb": _gb(disk.total),
            "percent": disk.percent,
        }
    except Exception:
        pass
    try:
        process = psutil.Process(os.getpid())
        # cpu_percent is sampled between calls, so the first read is a zero.
        data["cpu_percent"] = psutil.cpu_percent(interval=None)
        data["process"] = {
            "cpu_percent": process.cpu_percent(interval=None),
            "memory_mb": round(process.memory_info().rss / (1024 ** 2), 1),
            "threads": process.num_threads(),
            "started_at": int(process.create_time()),
        }
        with process.oneshot():
            data["process"]["connections"] = len(process.net_connections(kind="inet"))
    except Exception:
        pass
    try:
        load = os.getloadavg()
        data["load"] = [round(value, 2) for value in load]
    except Exception:
        pass
    return data


# ──────────────────────────────────────────────────────────────────────────────
# Bot, shards and cogs
# ──────────────────────────────────────────────────────────────────────────────
#: The page calls a shard slow above this figure; a reading that high before the
#: bot is ready is the startup sync, not a slow socket.
SLOW_LATENCY_MS = 600


def _shard_rows(bot) -> list[dict]:
    """One row per shard, with the guilds and members it carries.

    A small bot has one shard and discord.py still fills ``bot.shards``, so the
    rows are built from ``shard_count`` and the shard is read only for its
    latency: a missing entry means that connection is down, which the page shows
    as an unknown latency rather than a zero.
    """
    guilds: dict[int, int] = {}
    members: dict[int, int] = {}
    for guild in bot.guilds:
        shard_id = getattr(guild, "shard_id", 0) or 0
        guilds[shard_id] = guilds.get(shard_id, 0) + 1
        members[shard_id] = members.get(shard_id, 0) + (guild.member_count or 0)

    shard_map = getattr(bot, "shards", None) or {}
    total = getattr(bot, "shard_count", None) or 1
    # A shard that is connected while the bot is still syncing its guilds is
    # starting, not slow: its first heartbeat ACK arrives late only because the
    # event loop is busy caching members, and reporting that as latency would
    # show a healthy boot as a 5 s warning.
    ready = bool(bot.is_ready())
    slow_ms = SLOW_LATENCY_MS
    rows = []
    for shard_id in range(total):
        shard = shard_map.get(shard_id)
        connected = True
        try:
            # Between reconnects a shard has no open socket to ask about at all.
            connected = shard is not None and not shard.is_closed()
            ratelimited = bool(shard is not None and shard.is_ws_ratelimited())
            latency = shard.latency if shard is not None else None
        except Exception:
            connected = False
            ratelimited = False
            latency = None
        measured = _latency_ms(latency) if connected else None
        # No heartbeat yet, or a high reading taken during the initial sync: both
        # mean the shard is still coming up rather than answering slowly.
        starting = bool(connected and (measured is None or (not ready and measured > slow_ms)))
        rows.append({
            "id": shard_id,
            # No latency is published while a shard is still starting, so the page
            # shows an em dash with the starting state instead of a fake figure.
            "latency_ms": None if starting else measured,
            "connected": connected,
            "starting": starting,
            "guilds": guilds.get(shard_id, 0),
            "members": members.get(shard_id, 0),
            "ratelimited": ratelimited,
        })
    return rows


def _cog_rows(bot) -> list[dict]:
    """Every cog with its load outcome and, when it is not running, why."""
    recorded = list(getattr(bot, "cog_status", None) or [])
    if recorded:
        return recorded
    # A process started before the loader recorded outcomes still has its cogs.
    return [
        {"name": f"cogs.{name.lower()}", "label": name, "state": "loaded", "reason": None, "commands": 0}
        for name in sorted(bot.cogs)
    ]


def _build_version() -> str | None:
    """The version string the bot writes into its startup snapshot."""
    try:
        return json.loads(Path("data/bot_stats.json").read_text(encoding="utf-8")).get("version")
    except Exception:
        return None


def _overall_state(bot, cogs: list[dict]) -> str:
    """One word for the page's headline badge.

    ``starting`` is its own state: a bot that has connected but has not finished
    its first sync is up, and calling that offline would contradict ``online``.
    """
    if not bot.is_ready():
        return "starting"
    states = {cog["state"] for cog in cogs}
    if "failed" in states:
        return "degraded"
    if "maintenance" in states:
        return "maintenance"
    return "operational"


async def bot_status(bot) -> dict:
    """The live half of the payload. Runs on the bot's own event loop."""
    guilds = list(bot.guilds)
    cogs = _cog_rows(bot)
    user = getattr(bot, "user", None)
    started = getattr(bot, "start_time", None)
    uptime = int(time.time() - started) if started else None
    shards = _shard_rows(bot)
    try:
        latency = _latency_ms(bot.latency)
    except Exception:
        latency = None

    return {
        "online": True,
        "state": _overall_state(bot, cogs),
        "bot": {
            "name": getattr(user, "name", "Niko"),
            "id": str(getattr(user, "id", "")) or None,
            "avatar_url": str(user.display_avatar.url) if user else None,
            "ready": bot.is_ready(),
            "latency_ms": latency,
            "guild_count": len(guilds),
            "user_count": sum(guild.member_count or 0 for guild in guilds),
            "command_count": _public_command_count(bot),
            "voice_clients": len(getattr(bot, "voice_clients", []) or []),
            "uptime_seconds": uptime,
            "started_at": int(started) if started else None,
            "version": _build_version(),
        },
        "shards": shards,
        "shard_count": len(shards),
        "cogs": cogs,
        "cog_counts": {
            state: sum(1 for cog in cogs if cog["state"] == state)
            for state in ("loaded", "disabled", "maintenance", "failed")
        },
    }


def offline_status(reason: str | None = None) -> dict:
    """The payload when the bot process is not connected or not running."""
    return {
        "online": False,
        "state": "offline",
        "reason": reason,
        "bot": None,
        "shards": [],
        "shard_count": 0,
        "cogs": [],
        "cog_counts": {"loaded": 0, "disabled": 0, "maintenance": 0, "failed": 0},
    }
