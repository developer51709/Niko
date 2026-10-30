"""Bot-wide usage analytics.

Every slash, prefix, and context command reports itself here. Counters live in
memory and are folded into ``data/analytics.json`` on a timer, so a busy bot
never writes to disk per command while the staff dashboard can still chart
accurate daily totals — including the commands that ran seconds ago.

Only aggregate numbers are kept: command names, how they were invoked, the
guild's language, a distinct-guild count, and daily guild/member totals. No
message content, user ID, or guild ID is written to the file.
"""

from __future__ import annotations

import asyncio
import copy
import json
import os
import threading
from datetime import datetime, timedelta, timezone

ANALYTICS_PATH = os.path.join("data", "analytics.json")
HISTORY_DAYS = 90
FLUSH_SECONDS = 60
KINDS = ("slash", "prefix", "context")
SUPPORTED_LANGUAGES = ("en", "de", "es")

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
#: Per-day distinct guilds, kept in memory because a set is not JSON-friendly.
_active_guilds: dict[str, set[str]] = {}
_flush_task: asyncio.Task | None = None


# ── Date and language helpers ────────────────────────────────────────────────

def current_day(moment: datetime | None = None) -> str:
    """The UTC calendar day a counter belongs to."""
    return (moment or datetime.now(timezone.utc)).strftime("%Y-%m-%d")


def language_code(locale) -> str:
    """``en-GB`` → ``en``; an empty locale counts as English."""
    raw = str(locale or "").strip().lower()
    if not raw:
        return "en"
    return raw.split("-")[0] or "en"


def language_label(code: str) -> str:
    code = str(code or "").lower()
    return LANGUAGE_LABELS.get(code, code.upper() if code else "Unknown")


# ── Persistent state ────────────────────────────────────────────────────────

def _empty_day() -> dict:
    return {"total": 0, "commands": {}, "kinds": {}, "languages": {}, "guilds": 0}


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
    """Load (once) and normalise the persisted counters."""
    global _state
    if _state is not None:
        return _state

    try:
        with open(ANALYTICS_PATH, "r", encoding="utf-8") as handle:
            loaded = json.load(handle)
    except (OSError, ValueError):
        loaded = None

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
    state["days"] = days

    lifetime = state.get("lifetime")
    if not isinstance(lifetime, dict):
        lifetime = {}
    lifetime["total"] = int(lifetime.get("total") or 0)
    for key in ("commands", "kinds", "languages"):
        lifetime[key] = _count_map(lifetime.get(key))
    state["lifetime"] = lifetime

    scale = state.get("scale")
    if not isinstance(scale, dict):
        scale = {}
    for day, entry in list(scale.items()):
        if not isinstance(entry, dict):
            scale.pop(day, None)
            continue
        entry["guilds"] = int(entry.get("guilds") or 0)
        entry["users"] = int(entry.get("users") or 0)
    state["scale"] = scale

    state["version"] = 1
    _state = state
    return state


def _trim(state: dict) -> None:
    """Keep the history window from growing without bound."""
    cutoff = current_day(datetime.now(timezone.utc) - timedelta(days=HISTORY_DAYS - 1))
    for key in ("days", "scale"):
        for day in [day for day in state[key] if day < cutoff]:
            state[key].pop(day, None)
    for day in [day for day in _active_guilds if day < cutoff]:
        _active_guilds.pop(day, None)


def _apply_guild_counts(state: dict) -> None:
    """Fold each day's distinct-guild set into its stored count."""
    for day, guild_ids in _active_guilds.items():
        bucket = state["days"].setdefault(day, _empty_day())
        bucket["guilds"] = max(int(bucket.get("guilds") or 0), len(guild_ids))


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
            _trim(state)
    except Exception:
        pass


# ── Reading and persistence ─────────────────────────────────────────────────

def flush() -> bool:
    """Write the counters to disk. Safe to call from any thread."""
    with _LOCK:
        state = _ensure_state()
        _apply_guild_counts(state)
        _trim(state)
        payload = json.dumps(state, separators=(",", ":"), sort_keys=True)

    try:
        directory = os.path.dirname(os.path.abspath(ANALYTICS_PATH))
        os.makedirs(directory, exist_ok=True)
        temporary = f"{ANALYTICS_PATH}.tmp"
        with open(temporary, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.replace(temporary, ANALYTICS_PATH)
    except OSError:
        return False
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
        await asyncio.sleep(interval)
        if bot is not None:
            guilds = list(getattr(bot, "guilds", []) or [])
            record_scale(len(guilds), sum(int(getattr(guild, "member_count", 0) or 0) for guild in guilds))
        flush()


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


def stop_flush_task() -> None:
    """Cancel the writer and persist whatever is still in memory."""
    global _flush_task
    task, _flush_task = _flush_task, None
    if task is not None and not task.done():
        task.cancel()
    flush()
