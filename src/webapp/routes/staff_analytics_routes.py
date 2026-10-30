"""Bot-wide analytics for the staff workspace.

The payload joins three sources:

* live gateway state — guilds, members, shards, latency, uptime;
* the aggregate counters in ``utils.analytics`` — what ran, how it was invoked,
  and in which language, already zero-filled per day for charting;
* the economy table — how many profiles exist and where the currency sits.

Everything is aggregate. No user ID, guild ID, or message content is returned,
so the tab can be shown to any staff role without exposing member data.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

from .. import server as _server
from utils.analytics import (
    SUPPORTED_LANGUAGES,
    current_day,
    language_census,
    language_label,
    record_scale,
    snapshot,
)
from utils.economy_jobs import JOBS

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

_KINDS = ("slash", "prefix", "context")
_ECONOMY_CACHE: dict = {"at": 0.0, "value": None}
_ECONOMY_CACHE_SECONDS = 60


def _live_overview() -> dict:
    """Live gateway numbers, falling back to the startup snapshot."""
    bot = _discord_bot
    saved = load_json(BOT_STATS, {})
    guilds = list(getattr(bot, "guilds", []) or []) if bot is not None else []
    ready = bool(bot is not None and getattr(bot, "is_ready", lambda: False)())

    latency_ms = None
    if ready:
        try:
            latency_ms = round(float(bot.latency) * 1000)
        except Exception:
            latency_ms = None

    uptime_seconds = None
    start_time = getattr(bot, "start_time", None) if bot is not None else None
    if isinstance(start_time, (int, float)) and start_time > 0:
        uptime_seconds = max(0, int(time.time() - start_time))
    else:
        since = saved.get("uptime_since")
        if since:
            try:
                uptime_seconds = max(0, int(time.time() - datetime.fromisoformat(since).timestamp()))
            except (TypeError, ValueError):
                uptime_seconds = None

    member_count = sum(int(getattr(guild, "member_count", 0) or 0) for guild in guilds)
    if not guilds and not ready:
        # The gateway cache is empty until the first READY, which is also when a
        # dashboard restart happens; the startup file keeps the tab populated.
        return {
            "online": False,
            "source": "snapshot",
            "guilds": int(saved.get("guild_count") or 0),
            "members": int(saved.get("user_count") or 0),
            "latency_ms": None,
            "uptime_seconds": uptime_seconds,
            "shard_count": 0,
            "shards": [],
        }

    shards = []
    for shard_id, shard in sorted(dict(getattr(bot, "shards", {}) or {}).items()):
        try:
            shard_latency = round(float(shard.latency) * 1000)
        except Exception:
            shard_latency = None
        shards.append({"id": shard_id, "latency_ms": shard_latency})

    return {
        "online": ready,
        "source": "live",
        "guilds": len(guilds),
        "members": member_count,
        "latency_ms": latency_ms,
        "uptime_seconds": uptime_seconds,
        "shard_count": len(shards) or int(saved.get("shard_count") or 0),
        "shards": shards,
    }


def _command_categories() -> dict[str, str]:
    """Map a command's qualified name to its public catalogue category."""
    registry = load_json("data/commands.json", [])
    categories: dict[str, str] = {}
    if isinstance(registry, list):
        for entry in registry:
            if isinstance(entry, dict) and entry.get("name"):
                categories[str(entry["name"]).lower()] = str(entry.get("category") or "utility")
    return categories


def _usage_payload(counters: dict) -> dict:
    """Zero-fill the window's days and summarise the all-time counters."""
    window = counters["window_days"]
    stored_days = counters["days"]
    now = datetime.now(timezone.utc)

    days = []
    for offset in range(window - 1, -1, -1):
        date = current_day(now - timedelta(days=offset))
        bucket = stored_days.get(date) or {}
        kinds = bucket.get("kinds") or {}
        days.append({
            "date": date,
            "total": int(bucket.get("total") or 0),
            "slash": int(kinds.get("slash") or 0),
            "prefix": int(kinds.get("prefix") or 0),
            "context": int(kinds.get("context") or 0),
            "guilds": int(bucket.get("guilds") or 0),
            "languages": bucket.get("languages") or {},
        })

    today = days[-1] if days else {"total": 0, "slash": 0, "prefix": 0, "context": 0, "guilds": 0, "languages": {}}
    lifetime = counters["lifetime"]
    lifetime_total = int(lifetime.get("total") or 0)
    categories = _command_categories()

    top_commands = []
    for name, count in sorted(
        lifetime.get("commands", {}).items(),
        key=lambda item: (-item[1], item[0]),
    )[:10]:
        top_commands.append({
            "name": name,
            "count": int(count),
            "share": round(count / lifetime_total, 4) if lifetime_total else 0.0,
            "category": categories.get(str(name).lower(), "internal"),
        })

    languages = [
        {
            "code": code,
            "label": language_label(code),
            "count": int(count),
            "share": round(count / lifetime_total, 4) if lifetime_total else 0.0,
            "supported": code in SUPPORTED_LANGUAGES,
        }
        for code, count in sorted(
            lifetime.get("languages", {}).items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]

    return {
        "days": days,
        "window_days": window,
        "today": {
            "total": int(today["total"]),
            "slash": int(today["slash"]),
            "prefix": int(today["prefix"]),
            "context": int(today["context"]),
            "guilds": int(today["guilds"]),
        },
        "totals": {
            "today": int(today["total"]),
            "last_7_days": sum(day["total"] for day in days[-7:]),
            "last_30_days": sum(day["total"] for day in days[-30:]),
            "lifetime": lifetime_total,
        },
        "by_kind": {
            kind: int(lifetime.get("kinds", {}).get(kind) or 0)
            for kind in _KINDS
        },
        "top_commands": top_commands,
        "by_language": languages,
    }


def _economy_payload() -> dict | None:
    """Aggregate economy usage; cached so the poll never rescans the table."""
    now = time.time()
    cached = _ECONOMY_CACHE.get("value")
    if cached is not None and now - float(_ECONOMY_CACHE.get("at") or 0) < _ECONOMY_CACHE_SECONDS:
        return cached

    rows = get_runtime_economy_rows()
    if rows is None:
        return None

    profiles = len(rows)
    if not profiles:
        payload = {
            "profiles": 0,
            "circulating": 0,
            "banked": 0,
            "average": 0,
            "median": 0,
            "average_level": 0,
            "active_streaks": 0,
            "top_jobs": [],
        }
    else:
        wallets = sum(int(row.get("balance") or 0) for row in rows)
        banked = sum(int(row.get("bank") or 0) for row in rows)
        worths = sorted(int(row.get("net_worth") or 0) for row in rows)
        middle = len(worths) // 2
        median = worths[middle] if len(worths) % 2 else (worths[middle - 1] + worths[middle]) // 2
        job_counts: dict[str, int] = {}
        for row in rows:
            job = str(row.get("job") or "barista").lower()
            job_counts[job] = job_counts.get(job, 0) + 1
        top_jobs = []
        for job_id, count in sorted(job_counts.items(), key=lambda item: (-item[1], item[0]))[:5]:
            job = JOBS.get(job_id, {})
            top_jobs.append({
                "id": job_id,
                "name": job.get("name") or job_id.title(),
                "emoji": job.get("emoji") or "",
                "count": count,
                "share": round(count / profiles, 4),
            })
        payload = {
            "profiles": profiles,
            "circulating": wallets,
            "banked": banked,
            "average": int(sum(worths) / profiles),
            "median": median,
            "average_level": round(sum(int(row.get("level") or 0) for row in rows) / profiles, 1),
            "active_streaks": sum(1 for row in rows if int(row.get("daily_streak") or 0) > 0),
            "top_jobs": top_jobs,
        }

    _ECONOMY_CACHE["at"] = now
    _ECONOMY_CACHE["value"] = payload
    return payload


@app.route("/api/staff/analytics")
@require_auth
def api_staff_analytics():
    """Everything the staff analytics tab charts, in one live payload."""
    if not _current_staff_role():
        return jsonify({"error": "This area is restricted to Niko staff."}), 403

    try:
        requested_days = int(request.args.get("days", "30"))
    except (TypeError, ValueError):
        requested_days = 30
    requested_days = max(7, min(requested_days, 90))

    overview = _live_overview()
    if overview.get("source") == "live":
        # Keep the growth series populated even when no staff member is looking.
        record_scale(overview["guilds"], overview["members"])

    counters = snapshot(requested_days)
    growth = [
        {
            "date": day,
            "guilds": int(entry.get("guilds") or 0),
            "users": int(entry.get("users") or 0),
        }
        for day, entry in sorted(counters["scale"].items())
    ]

    census = language_census(getattr(_discord_bot, "guilds", []) or [])

    return jsonify({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "bot": overview,
        "usage": _usage_payload(counters),
        "languages": census,
        "economy": _economy_payload(),
        "growth": growth,
    })
