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

import hashlib
import json
import math
import os
import platform
import re
import threading
import time
from pathlib import Path

try:
    import psutil
except Exception:  # pragma: no cover - psutil is a hard dependency of the bot
    psutil = None

from utils import maintenance
from utils.error_reports import list_public_incidents
from utils.locales import SUPPORTED_LANGUAGES

from .commands import (
    _LEGACY_INTERNAL_COMMAND_NAMES,
    _is_internal_command,
    _live_internal_command_names,
)

#: Every language the bot can be set to, in the order the site shows them.
#: Taken from the bot's own list rather than copied, so a language added there
#: is counted here (and published in the feed) without a second edit.
LANGUAGES = SUPPORTED_LANGUAGES
#: Names for the language codes the website can carry. Wider than :data:`LANGUAGES`
#: on purpose: the site's landing page ships more languages than the bot speaks,
#: and the feed labels whatever catalogue files it finds. A code without an entry
#: still works — it is shown upper-cased.
LANGUAGE_LABELS = {
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
    "fr": "Français",
    "ru": "Русский",
    "ja": "日本語",
    "zh": "中文",
    "hi": "हिन्दी",
    "ar": "العربية",
}

#: The website's own per-page catalogues (``web/src/locales/<page>/<lang>.json``,
#: or ``<page>/<sub>/<lang>.json`` for a page made of sub pages).
SITE_LOCALES = Path("web/src/locales")

#: How long the translation scan is reused, in seconds. Short, because
#: :mod:`webapp.locale_feed` may be reading a beta instance that is being edited
#: right now; the scan itself is cached for longer inside the feed.
_LOCALE_TTL = 15.0
_locale_cache: dict = {"at": 0.0, "payload": None}
_locale_cache_lock = threading.Lock()


def _digest(raw: bytes) -> str:
    """A short content hash, the same shape the website feed uses for a page."""
    return hashlib.sha1(raw).hexdigest()[:12]


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


def site_language_files(folder: Path, code: str) -> list[Path]:
    """Every file that carries one page's copy in one language.

    A page keeps its chrome in ``<page>/<code>.json`` and, when it is large
    enough to have sub pages, each one's strings in ``<page>/<sub>/<code>.json``.
    The page-level file comes first so it wins if a key is defined twice, then
    the subfolders in name order, because a merge has to be deterministic.
    """
    paths: list[Path] = []
    root = folder / f"{code}.json"
    if root.is_file():
        paths.append(root)
    paths.extend(sorted(path for path in folder.glob(f"*/{code}.json") if path.is_file()))
    return paths


def site_page_languages(folder: Path) -> list[str]:
    """Language codes a page ships, at its root or in any of its subfolders."""
    codes = {path.stem for path in folder.glob("*.json")}
    codes.update(path.stem for path in folder.glob("*/*.json"))
    return sorted(codes)


def site_catalogue(folder: Path, code: str) -> tuple[dict, bytes]:
    """One page's catalogue in one language, merged across its files.

    Returns the merged strings and the bytes that identify that merge, so a
    catalogue's hash covers every file that went into it — editing only the
    moderation tab's copy has to change the hash the browser caches against.
    """
    merged: dict = {}
    chunks: list[bytes] = []
    for path in site_language_files(folder, code):
        try:
            raw = path.read_bytes()
            strings = json.loads(raw)
        except Exception:
            # One unreadable subfolder file must not take the page's copy with it.
            continue
        if isinstance(strings, dict):
            chunks.append(raw)
            merged.update(strings)
    return merged, b"".join(chunks)


def _locale_dirs() -> list[Path]:
    """Every folder that holds a shipped ``<lang>.json`` catalogue."""
    found = [path for path in Path("src").glob("**/locales") if path.is_dir()]
    return sorted(found)


#: A bot catalogue is addressed by the package that owns it, never by a path:
#: ``cogs.music`` is ``src/cogs/music/locales``. The feed carries this name over
#: HTTP, so it has to be both stable and safe to put in a URL.
_BOT_NAME = re.compile(r"^[a-z0-9_]+(?:\.[a-z0-9_]+){0,4}$")


def bot_catalogue_name(folder: Path) -> str | None:
    """``"cogs.music"`` for ``src/cogs/music/locales``, or ``None`` elsewhere."""
    try:
        relative = folder.resolve().relative_to(Path("src").resolve())
    except Exception:
        return None
    parts = relative.parts[:-1]
    if not parts:
        return None
    name = ".".join(parts)
    return name if _BOT_NAME.match(name) else None


def _bot_catalogue_dirs() -> dict[str, Path]:
    """Every bot catalogue folder, keyed by the package name the bot calls it by."""
    found: dict[str, Path] = {}
    for folder in _locale_dirs():
        if not (folder / "en.json").is_file():
            continue
        name = bot_catalogue_name(folder)
        if name is not None:
            found[name] = folder
    return found


def bot_catalogue(name: str, code: str) -> tuple[dict, bytes]:
    """One bot catalogue file, for an instance serving it to its successor.

    Returns the decoded strings and the exact bytes they came from, so the hash
    a consumer verifies against is the hash of what was actually published.
    """
    if not _BOT_NAME.match(name or "") or code not in LANGUAGES:
        return {}, b""
    folder = _bot_catalogue_dirs().get(name)
    if folder is None:
        return {}, b""
    try:
        raw = (folder / f"{code}.json").read_bytes()
        strings = json.loads(raw)
    except Exception:
        return {}, b""
    return (strings, raw) if isinstance(strings, dict) else ({}, b"")


#: The bot catalogue manifest changes when a translator saves a file, so it is
#: cached for the same few seconds as the website scan.
_bot_cache: dict = {"at": 0.0, "payload": None}


def bot_catalogues(force: bool = False) -> dict[str, dict]:
    """Every bot catalogue, with its English key count and per-language hashes.

    The website's feed publishes this so a production instance can fetch bot
    wording from beta the same way it fetches page copy: one entry per
    catalogue, a hash per language, and only the files that changed. Coverage is
    counted per catalogue rather than by leaf key, because two cogs both have an
    ``error`` key and they are different strings.
    """
    now = time.monotonic()
    with _locale_cache_lock:
        cached = _bot_cache["payload"]
        if cached is not None and not force and now - _bot_cache["at"] < _LOCALE_TTL:
            return cached

    catalogues: dict[str, dict] = {}
    for name, folder in _bot_catalogue_dirs().items():
        try:
            english_raw = (folder / "en.json").read_bytes()
            english_keys = set(_leaf_keys(json.loads(english_raw)))
        except Exception:
            continue
        if not english_keys:
            continue
        entry: dict = {"keys": len(english_keys), "langs": {}}
        for code in LANGUAGES:
            path = folder / f"{code}.json"
            if not path.is_file():
                continue
            try:
                raw = path.read_bytes()
                strings = json.loads(raw)
            except Exception:
                continue
            if not isinstance(strings, dict):
                continue
            keys = set(_leaf_keys(strings))
            translated = len(english_keys) if code == "en" else len(english_keys & keys)
            entry["langs"][code] = {"translated": translated, "hash": _digest(raw)}
        if "en" in entry["langs"]:
            catalogues[name] = entry

    with _locale_cache_lock:
        _bot_cache.update({"at": now, "payload": catalogues})
    return catalogues


def _bot_locale_status() -> list[dict]:
    """Per-language coverage of the bot's own wording, rolled up by catalogue."""
    catalogues = bot_catalogues()
    total = sum(entry["keys"] for entry in catalogues.values())
    rows = []
    for code in LANGUAGES:
        translated = sum(entry["langs"].get(code, {}).get("translated", 0) for entry in catalogues.values())
        rows.append(_coverage_row(code, translated, total, extra={"catalogues": len(catalogues)}))
    return rows


def _website_locale_status() -> list[dict]:
    """Per-language coverage of the website's own page catalogues.

    Every page ships a catalogue folder (``web/src/locales/<page>``), the same
    way it ships an Open Graph card, and the English copy inside it is the
    source. A page with sub pages spreads that copy over subfolders, so the files
    are read through :func:`site_catalogue` and counted as the one page they are.
    Measuring the bot's command descriptions here was what made the website look
    fully translated while none of its own copy was: those strings belong to the
    command catalogue, not to the site's interface.

    A page is only counted as done (``complete_pages``) when its copy for that
    language covers every English key it has — a translation someone started and
    stopped is still partial, however many keys it filled in.
    """
    total = 0
    # The site can carry more languages than the bot speaks — the landing page
    # ships Russian, Japanese, Chinese, Hindi and Arabic — so the rows follow the
    # files on disk and the bot's four are only the starting order.
    codes = list(LANGUAGES)
    translated: dict[str, int] = {}
    complete: dict[str, int] = {}
    pages = 0

    if SITE_LOCALES.is_dir():
        for folder in sorted(path for path in SITE_LOCALES.iterdir() if path.is_dir()):
            english, _ = site_catalogue(folder, "en")
            if not english:
                continue
            english_keys = set(_leaf_keys(english))
            pages += 1
            total += len(english_keys)
            translated["en"] = translated.get("en", 0) + len(english_keys)
            # English is the source copy, so a page that has any at all is
            # translated into English by definition.
            complete["en"] = complete.get("en", 0) + 1
            for code in site_page_languages(folder):
                if code not in codes:
                    codes.append(code)
                if code == "en":
                    continue
                catalogue, _ = site_catalogue(folder, code)
                if not catalogue:
                    continue
                keys = set(_leaf_keys(catalogue))
                translated[code] = translated.get(code, 0) + len(english_keys & keys)
                if english_keys <= keys:
                    complete[code] = complete.get(code, 0) + 1

    return [
        _coverage_row(
            code,
            translated.get(code, 0),
            total,
            extra={"pages": pages, "complete_pages": complete.get(code, 0)},
        )
        for code in codes
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
    """Bot and website translation coverage, cached for a few seconds.

    The rows are built from this deployment's files and then handed to
    :func:`webapp.locale_feed.decorate`, which swaps in the beta instance's
    catalogues when ``BETA_INSTANCE_URL`` is set — so a translation written on beta
    shows up here without a deploy, and ``source`` always says which copy the
    figures describe.
    """
    from . import locale_feed

    now = time.monotonic()
    if not force and _locale_cache["payload"] and now - _locale_cache["at"] < _LOCALE_TTL:
        return _locale_cache["payload"]
    payload = {
        "languages": list(LANGUAGES),
        "bot": _bot_locale_status(),
        "website": _website_locale_status(),
        "scanned_at": int(time.time()),
    }
    payload = locale_feed.decorate(payload)
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


def _lavalink_pool(bot) -> dict | None:
    """The music node pool for the public page, with private hosts withheld.

    Lavalink nodes come from two places: the catalogue committed in
    ``config/lavalink.py``, whose hosts are already in the repository, and the
    private nodes the owner saves from the dashboard. A private node is the
    owner's own server, so nothing identifying it may reach a public payload —
    not its host, its port, or the label, which an owner is free to type as the
    hostname. Those rows are published as ``private-<n>`` instead, ordered by
    identifier so the alias for a given node does not move between polls.

    Returns ``None`` when the music system is not loaded, which the page shows
    as a missing section rather than a pool of zero nodes.
    """
    getter = getattr(bot, "get_cog", None)
    cog = getter("MusicSystem") if getter else None
    snapshot = getattr(cog, "pool_snapshot", None)
    if not callable(snapshot):
        return None
    try:
        pool = snapshot()
    except Exception:
        return None
    if not isinstance(pool, dict):
        return None

    rows = sorted(pool.get("nodes") or [], key=lambda row: str(row.get("identifier") or ""))
    nodes = []
    private_index = 0
    for row in rows:
        identifier = str(row.get("identifier") or "")
        private = bool(row.get("private"))
        node = {
            "id": identifier,
            "private": False,
            "index": None,
            "status": str(row.get("status") or "disconnected"),
            "players": int(row.get("players") or 0),
            "heartbeat": float(row.get("heartbeat") or 0),
        }
        if private:
            private_index += 1
            node.update({"id": f"private-{private_index}", "private": True, "index": private_index})
        nodes.append(node)

    return {
        "connected": sum(1 for node in nodes if node["status"] == "connected"),
        "pool": len(nodes),
        "private": private_index,
        "nodes": nodes,
    }


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


def _overall_state(bot, cogs: list[dict], notices: dict | None = None,
                   incidents: list[dict] | None = None) -> str:
    """One word for the page's headline badge.

    ``starting`` is its own state: a bot that has connected but has not finished
    its first sync is up, and calling that offline would contradict ``online``.
    """
    if not bot.is_ready():
        return "starting"
    states = {cog["state"] for cog in cogs}
    if "failed" in states:
        return "degraded"
    if any(incident.get("state") != "resolved" for incident in incidents or ()):
        return "degraded"
    if "maintenance" in states or any((notices or {}).get(kind) for kind in ("cogs", "commands", "apis")):
        return "maintenance"
    return "operational"


async def bot_status(bot) -> dict:
    """The live half of the payload. Runs on the bot's own event loop."""
    guilds = list(bot.guilds)
    cogs = _cog_rows(bot)
    notices = maintenance.public_snapshot(bot)
    try:
        incidents = await list_public_incidents(bot)
    except Exception:
        incidents = []
    incident_states = {item.get("code"): item for item in incidents}
    for group in notices.values():
        for notice in group:
            linked = incident_states.get(notice.get("report_code"))
            if linked:
                notice["incident_state"] = linked.get("state")
                notice["incident_label"] = linked.get("state_label")
    for incident in incidents:
        target = incident.get("maintenance") or {}
        incident["maintenance_active"] = bool(
            target.get("kind") and target.get("key")
            and maintenance.entry(target["kind"], target["key"])
        )
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
        "state": _overall_state(bot, cogs, notices, incidents),
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
        "lavalink": _lavalink_pool(bot),
        "cogs": cogs,
        "api_maintenance": notices.get("apis", []),
        "command_maintenance": notices.get("commands", []),
        "incidents": incidents,
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
        "lavalink": None,
        "cogs": [],
        "api_maintenance": maintenance.public_snapshot().get("apis", []),
        "command_maintenance": maintenance.public_snapshot().get("commands", []),
        "incidents": [],
        "cog_counts": {"loaded": 0, "disabled": 0, "maintenance": 0, "failed": 0},
    }
