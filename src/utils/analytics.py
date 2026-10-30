"""Bot-wide usage analytics.

Every slash, prefix, and context command reports itself here. Counters live in
memory and are folded into the bot's database on a timer, so a busy bot never
writes per invocation while the staff dashboard can still chart accurate daily
totals — including the commands that ran seconds ago.

The counters are stored as rows in the database the bot already uses (MongoDB in
production, SQLite locally) rather than in ``data/analytics.json``: a deployment
without a persistent disk loses files on every restart, which would silently
wipe the charts. Reads are served from the counters loaded at startup, so the
dashboard never waits on the database.

Only aggregate numbers are kept: command names, how they were invoked, the
guild's language, a distinct-guild count, and daily guild/member totals. No
message content, user ID, or guild ID is stored.
"""

from __future__ import annotations

import asyncio
import copy
import json
import os
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

import database as database_module
from utils.locales import SUPPORTED_LANGUAGES

TABLE = "bot_analytics"
#: Where the previous file-backed version kept its counters; imported once.
LEGACY_PATH = os.path.join("data", "analytics.json")
HISTORY_DAYS = 90
FLUSH_SECONDS = 60
KINDS = ("slash", "prefix", "context")
#: Row bucket → the key it fills inside a day or lifetime total.
_BUCKETS = {"command": "commands", "kind": "kinds", "language": "languages"}

LANGUAGE_LABELS = {
    "en": "English",
    "de": "German",
    "es": "Spanish",
    "fr": "French",
    "pt": "Portuguese",
    "it": "Italian",
    "nl": "Dutch",
    "pl": "Polish",
    "ru": "Russian",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "sv": "Swedish",
    "da": "Danish",
    "fi": "Finnish",
    "nb": "Norwegian",
    "cs": "Czech",
    "el": "Greek",
    "hu": "Hungarian",
    "ro": "Romanian",
    "bg": "Bulgarian",
    "hr": "Croatian",
    "lt": "Lithuanian",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
}

_LOCK = threading.Lock()
_state: dict | None = None
#: Per-day distinct guilds, kept in memory because a set is not a count.
_active_guilds: dict[str, set[str]] = {}
#: Rows changed since the last successful flush: ``(scope, bucket, name)`` →
#: the write counter they changed at, so a flush can tell whether a row moved
#: again while it was being written.
_dirty: dict[tuple[str, str, str], int] = {}
_version = 0
_flush_task: asyncio.Task | None = None
_ready = False


# ── Date and language helpers ────────────────────────────────────────────────

def current_day(moment: datetime | None = None) -> str:
    """The UTC calendar day a counter belongs to."""
    return (moment or datetime.now(timezone.utc)).strftime("%Y-%m-%d")


def _cutoff(days: int = HISTORY_DAYS) -> str:
    """The oldest day still worth keeping."""
    return current_day(datetime.now(timezone.utc) - timedelta(days=days - 1))


def language_code(locale) -> str:
    """``en-GB`` → ``en``; an empty locale counts as English."""
    raw = str(locale or "").strip().lower()
    if not raw:
        return "en"
    return raw.split("-")[0] or "en"


def language_label(code: str) -> str:
    code = str(code or "").lower()
    return LANGUAGE_LABELS.get(code, code.upper() if code else "Unknown")


# ── In-memory state ─────────────────────────────────────────────────────────

def _empty_day() -> dict:
    return {"total": 0, "commands": {}, "kinds": {}, "languages": {}, "guilds": 0}


def _new_state() -> dict:
    return {
        "days": {},
        "lifetime": {"total": 0, "commands": {}, "kinds": {}, "languages": {}},
        "scale": {},
        "version": 1,
    }


def _count_map(value) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    cleaned = {}
    for key, count in value.items():
        try:
            cleaned[str(key)] = int(count or 0)
        except (TypeError, ValueError):
            continue
    return cleaned


def _ensure_state() -> dict:
    """The live counters, created empty until the database load fills them."""
    global _state
    if _state is None:
        _state = _new_state()
    return _state


def _has_counters(state: dict) -> bool:
    return bool(state["days"]) or state["lifetime"]["total"] > 0 or bool(state["scale"])


def _touch(key: tuple[str, str, str]) -> None:
    """Remember that a row changed; the next flush writes it."""
    global _version
    _version += 1
    _dirty[key] = _version


# ── Database plumbing ───────────────────────────────────────────────────────

def _pool():
    """The pool the bot is already using, or None before startup finished."""
    return getattr(database_module, "_shared_pool", None)


def _warn(message: str) -> None:
    try:
        from utils import logging as bot_logging

        bot_logging.warning("Analytics", message)
    except Exception:  # noqa: BLE001 - logging must never break analytics
        pass


def _normalise(loaded) -> dict:
    """Coerce a counters payload (from the database or the legacy file)."""
    state = loaded if isinstance(loaded, dict) else {}
    days = state.get("days")
    if not isinstance(days, dict):
        days = {}
    for day, bucket in list(days.items()):
        if not isinstance(bucket, dict):
            days.pop(day, None)
            continue
        bucket["total"] = int(bucket.get("total") or 0)
        bucket["guilds"] = int(bucket.get("guilds") or 0)
        for key in ("commands", "kinds", "languages"):
            bucket[key] = _count_map(bucket.get(key))

    lifetime = state.get("lifetime")
    if not isinstance(lifetime, dict):
        lifetime = {}
    lifetime["total"] = int(lifetime.get("total") or 0)
    for key in ("commands", "kinds", "languages"):
        lifetime[key] = _count_map(lifetime.get(key))

    scale = state.get("scale")
    if not isinstance(scale, dict):
        scale = {}
    for day, entry in list(scale.items()):
        if not isinstance(entry, dict):
            scale.pop(day, None)
            continue
        entry["guilds"] = int(entry.get("guilds") or 0)
        entry["users"] = int(entry.get("users") or 0)

    return {"days": days, "lifetime": lifetime, "scale": scale, "version": 1}


def _absorb(target: dict, extra: dict) -> None:
    """Fold counters into ``target``: totals add up, point-in-time values peak."""
    target["lifetime"]["total"] += extra["lifetime"]["total"]
    for key in _BUCKETS.values():
        bucket = target["lifetime"][key]
        for name, count in extra["lifetime"][key].items():
            bucket[name] = bucket.get(name, 0) + count

    for day, extra_day in extra["days"].items():
        bucket = target["days"].setdefault(day, _empty_day())
        bucket["total"] += extra_day["total"]
        bucket["guilds"] = max(bucket["guilds"], extra_day["guilds"])
        for key in _BUCKETS.values():
            for name, count in extra_day[key].items():
                bucket[key][name] = bucket[key].get(name, 0) + count

    for day, entry in extra["scale"].items():
        target_entry = target["scale"].setdefault(day, {"guilds": 0, "users": 0})
        target_entry["guilds"] = max(target_entry["guilds"], entry.get("guilds", 0))
        target_entry["users"] = max(target_entry["users"], entry.get("users", 0))


def _keys_of(state: dict) -> list[tuple[str, str, str]]:
    """Every row the given counters occupy."""
    keys: list[tuple[str, str, str]] = [("lifetime", "total", "all")]
    for bucket_name, field in _BUCKETS.items():
        keys.extend(("lifetime", bucket_name, name) for name in state["lifetime"][field])
    for day, bucket in state["days"].items():
        keys.append((day, "total", "all"))
        keys.append((day, "guilds", "active"))
        for bucket_name, field in _BUCKETS.items():
            keys.extend((day, bucket_name, name) for name in bucket[field])
    for day in state["scale"]:
        keys.append((day, "scale", "guilds"))
        keys.append((day, "scale", "users"))
    return keys


def _row_value(state: dict, key: tuple[str, str, str]):
    """The count a row currently holds, or None when its day was trimmed."""
    scope, bucket_name, name = key
    if scope == "lifetime":
        if bucket_name == "total":
            return state["lifetime"]["total"]
        field = _BUCKETS.get(bucket_name)
        return state["lifetime"][field].get(name, 0) if field else None

    if bucket_name == "scale":
        entry = state["scale"].get(scope)
        return None if entry is None else int(entry.get(name) or 0)

    bucket = state["days"].get(scope)
    if bucket is None:
        return None
    if bucket_name == "total":
        return bucket["total"]
    if bucket_name == "guilds":
        return bucket["guilds"]
    field = _BUCKETS.get(bucket_name)
    return bucket[field].get(name, 0) if field else None


async def _create_table(pool) -> None:
    await pool.execute(
        f"""CREATE TABLE IF NOT EXISTS {TABLE} (
            scope  TEXT NOT NULL,
            bucket TEXT NOT NULL,
            name   TEXT NOT NULL,
            count  INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (scope, bucket, name)
        )"""
    )


async def _load(pool) -> None:
    """Replace the in-memory counters with the persisted rows."""
    rows = await pool.fetch(f"SELECT scope, bucket, name, count FROM {TABLE}")
    loaded = _new_state()
    for row in rows:
        try:
            scope = str(row["scope"])
            bucket_name = str(row["bucket"])
            name = str(row["name"])
            count = int(row["count"] or 0)
        except (KeyError, TypeError, ValueError):
            continue
        if scope == "lifetime":
            if bucket_name == "total":
                loaded["lifetime"]["total"] = count
            elif bucket_name in _BUCKETS:
                loaded["lifetime"][_BUCKETS[bucket_name]][name] = count
            continue
        if bucket_name == "scale":
            entry = loaded["scale"].setdefault(scope, {"guilds": 0, "users": 0})
            if name in entry:
                entry[name] = count
            continue
        day = loaded["days"].setdefault(scope, _empty_day())
        if bucket_name == "total":
            day["total"] = count
        elif bucket_name == "guilds":
            day["guilds"] = max(day["guilds"], count)
        elif bucket_name in _BUCKETS:
            day[_BUCKETS[bucket_name]][name] = count

    global _state
    with _LOCK:
        current = _state
        if current is None or not _has_counters(current):
            _state = loaded
            return
        # A command was recorded while the load was in flight; keep both.
        _absorb(current, loaded)
        for key in _keys_of(loaded):
            _touch(key)


async def _import_legacy(pool) -> None:
    """Bring forward counters written by the previous file-backed version."""
    path = Path(LEGACY_PATH)
    if not path.is_file():
        return
    with _LOCK:
        if _has_counters(_ensure_state()):
            return  # the database already has its own history
    try:
        loaded = _normalise(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return

    with _LOCK:
        state = _ensure_state()
        _absorb(state, loaded)
        for key in _keys_of(state):
            _touch(key)

    if await flush(pool):
        try:
            path.replace(path.with_suffix(".json.migrated"))
        except OSError:
            pass


async def prepare(pool=None) -> bool:
    """Create the table and load the persisted counters, once per process."""
    global _ready
    if _ready:
        return True
    pool = pool or _pool()
    if pool is None:
        return False
    try:
        await _create_table(pool)
        await _load(pool)
        await _import_legacy(pool)
    except Exception as error:  # noqa: BLE001 - counters are best-effort telemetry
        _warn(f"Could not load bot analytics from the database: {error}")
        return False
    _ready = True
    return True


# ── Recording ───────────────────────────────────────────────────────────────

def record_command(name, kind="slash", lang="en", guild_id=None) -> None:
    """Count one completed command invocation.

    Called from bot event hooks, so a failure here must never surface into the
    command path: the counters are best-effort telemetry.
    """
    command = str(name or "").strip()
    if not command:
        return
    kind = kind if kind in KINDS else "slash"
    lang = language_code(lang)
    day = current_day()
    try:
        with _LOCK:
            state = _ensure_state()
            bucket = state["days"].setdefault(day, _empty_day())
            bucket["total"] += 1
            bucket["commands"][command] = bucket["commands"].get(command, 0) + 1
            bucket["kinds"][kind] = bucket["kinds"].get(kind, 0) + 1
            bucket["languages"][lang] = bucket["languages"].get(lang, 0) + 1
            if guild_id is not None:
                _active_guilds.setdefault(day, set()).add(str(guild_id))

            lifetime = state["lifetime"]
            lifetime["total"] += 1
            lifetime["commands"][command] = lifetime["commands"].get(command, 0) + 1
            lifetime["kinds"][kind] = lifetime["kinds"].get(kind, 0) + 1
            lifetime["languages"][lang] = lifetime["languages"].get(lang, 0) + 1

            _touch((day, "total", "all"))
            _touch((day, "command", command))
            _touch((day, "kind", kind))
            _touch((day, "language", lang))
            if guild_id is not None:
                _touch((day, "guilds", "active"))
            _touch(("lifetime", "total", "all"))
            _touch(("lifetime", "command", command))
            _touch(("lifetime", "kind", kind))
            _touch(("lifetime", "language", lang))
            _trim(state)
    except Exception:
        # Telemetry is not worth a failed command.
        pass


def record_scale(guild_count, user_count) -> None:
    """Remember today's guild and member totals for the growth series."""
    try:
        guilds = int(guild_count or 0)
        users = int(user_count or 0)
    except (TypeError, ValueError):
        return
    day = current_day()
    try:
        with _LOCK:
            state = _ensure_state()
            entry = state["scale"].setdefault(day, {"guilds": 0, "users": 0})
            entry["guilds"] = max(int(entry.get("guilds") or 0), guilds)
            entry["users"] = max(int(entry.get("users") or 0), users)
            _touch((day, "scale", "guilds"))
            _touch((day, "scale", "users"))
            _trim(state)
    except Exception:
        pass


def _trim(state: dict) -> None:
    """Keep the history window from growing without bound."""
    cutoff = _cutoff()
    for key in ("days", "scale"):
        for day in [day for day in state[key] if day < cutoff]:
            state[key].pop(day, None)
    for day in [day for day in _active_guilds if day < cutoff]:
        _active_guilds.pop(day, None)
    for key in [key for key in _dirty if key[0] != "lifetime" and key[0] < cutoff]:
        _dirty.pop(key, None)


def _apply_guild_counts(state: dict) -> None:
    """Fold each day's distinct-guild set into its stored count."""
    for day, guild_ids in _active_guilds.items():
        bucket = state["days"].setdefault(day, _empty_day())
        bucket["guilds"] = max(int(bucket.get("guilds") or 0), len(guild_ids))


# ── Reading and persistence ─────────────────────────────────────────────────

async def flush(pool=None) -> bool:
    """Write the changed counters to the database."""
    pool = pool or _pool()
    if pool is None:
        return False

    with _LOCK:
        state = _ensure_state()
        _apply_guild_counts(state)
        _trim(state)
        captured = dict(_dirty)
        rows = []
        for key in captured:
            value = _row_value(state, key)
            if value is not None:
                rows.append((key, int(value)))
        oldest = _cutoff()

    try:
        for (scope, bucket_name, name), count in rows:
            await pool.execute(
                f"REPLACE INTO {TABLE} (scope, bucket, name, count) "
                "VALUES ($1, $2, $3, $4)",
                scope,
                bucket_name,
                name,
                count,
            )
        # Rows older than the history window ("lifetime" sorts after every
        # day) are dropped in the same pass.
        await pool.execute(f"DELETE FROM {TABLE} WHERE scope < $1", oldest)
    except Exception as error:  # noqa: BLE001 - the next flush retries
        _warn(f"Could not write bot analytics: {error}")
        return False

    with _LOCK:
        for key, version in captured.items():
            if _dirty.get(key) == version:
                _dirty.pop(key, None)
    return True


def snapshot(days: int = 30) -> dict:
    """A consistent copy of the last ``days`` of counters plus all-time totals."""
    try:
        window = int(days or 30)
    except (TypeError, ValueError):
        window = 30
    window = max(1, min(window, HISTORY_DAYS))

    with _LOCK:
        state = _ensure_state()
        _apply_guild_counts(state)
        cutoff = current_day(datetime.now(timezone.utc) - timedelta(days=window - 1))
        days_out = {
            day: copy.deepcopy(bucket)
            for day, bucket in state["days"].items()
            if day >= cutoff
        }
        scale_out = {
            day: copy.deepcopy(entry)
            for day, entry in state["scale"].items()
            if day >= cutoff
        }
        lifetime = copy.deepcopy(state["lifetime"])

    return {
        "days": days_out,
        "scale": scale_out,
        "lifetime": lifetime,
        "window_days": window,
        "today": current_day(),
    }


def language_census(guilds) -> dict:
    """Count guilds and members per Discord language across the live gateway."""
    buckets: dict[str, dict] = {}
    total_guilds = 0
    total_members = 0
    for guild in list(guilds or []):
        code = language_code(getattr(guild, "preferred_locale", None))
        entry = buckets.setdefault(code, {"guilds": 0, "members": 0})
        entry["guilds"] += 1
        entry["members"] += int(getattr(guild, "member_count", 0) or 0)
        total_guilds += 1
    for entry in buckets.values():
        total_members += entry["members"]

    rows = [
        {
            "code": code,
            "label": language_label(code),
            "guilds": entry["guilds"],
            "members": entry["members"],
            "share": round(entry["guilds"] / total_guilds, 4) if total_guilds else 0.0,
            "supported": code in SUPPORTED_LANGUAGES,
        }
        for code, entry in buckets.items()
    ]
    rows.sort(key=lambda row: (-row["guilds"], -row["members"], row["code"]))
    return {"guilds": total_guilds, "members": total_members, "languages": rows}


# ── Background flush ────────────────────────────────────────────────────────

async def _flush_loop(bot, interval: int) -> None:
    while True:
        # Loading before the first write means a reconnect never overwrites
        # persisted history with an empty in-memory state. The database pool
        # can still be starting up when on_ready fires, so this is retried.
        if not _ready:
            await prepare()
        await asyncio.sleep(interval)
        if bot is not None:
            guilds = list(getattr(bot, "guilds", []) or [])
            record_scale(len(guilds), sum(int(getattr(guild, "member_count", 0) or 0) for guild in guilds))
        await flush()


def start_flush_task(bot=None, interval: int = FLUSH_SECONDS) -> asyncio.Task | None:
    """Start the periodic writer once, on the bot's event loop."""
    global _flush_task
    if _flush_task is not None and not _flush_task.done():
        return _flush_task
    try:
        _flush_task = asyncio.get_running_loop().create_task(_flush_loop(bot, max(5, int(interval))))
    except RuntimeError:
        _flush_task = None
    return _flush_task


async def stop_flush_task() -> None:
    """Cancel the writer and persist whatever is still in memory."""
    global _flush_task
    task, _flush_task = _flush_task, None
    if task is not None and not task.done():
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):  # noqa: BLE001 - shutting down
            pass
    await flush()
