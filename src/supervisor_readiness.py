"""Readiness checks for a supervised bot child.

The supervisor must not call a child "ready" just because Discord dispatched
READY.  Before proxying user traffic to it, the child checks the parts that
actually serve requests: the database, the cogs that must be loaded, every
gateway shard, and the startup steps whose failure makes the rest unreliable.

The result is intentionally a small dictionary of facts.  The child reports it
as a lifecycle event, and the supervisor (or an operator reading the status
file) can see *why* a process is not ready without scraping its logs.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

#: A small, conservative set of cogs without which slash commands and the
#: error/maintenance path are not usable.  Deployments can extend or replace it
#: with ``NIKO_CRITICAL_COGS`` (comma-separated module names).
DEFAULT_CRITICAL_COGS = ("cogs.system", "cogs.admin", "cogs.utility")

#: Startup steps whose failure is fatal to readiness.  The optional steps
#: (banner, stats writers, background syncs) only degrade the process.
DEFAULT_CRITICAL_STEPS = ("init_database", "load_cogs", "preload_economy_cache")

_LOADED_COG_STATES = {"loaded", "maintenance"}


def _comma_list(value: str | None, default: tuple[str, ...]) -> tuple[str, ...]:
    if value is None:
        return default
    return tuple(item.strip() for item in value.split(",") if item.strip())


def critical_cogs() -> tuple[str, ...]:
    return _comma_list(os.environ.get("NIKO_CRITICAL_COGS"), DEFAULT_CRITICAL_COGS)


def critical_steps() -> tuple[str, ...]:
    return _comma_list(os.environ.get("NIKO_CRITICAL_STARTUP_STEPS"), DEFAULT_CRITICAL_STEPS)


def strict_backend() -> bool:
    """Whether this deployment refuses to run on anything but MongoDB.

    ``database.create_pool`` refuses the fallback at startup; this check also
    covers a pool that was created before the flag was set or replaced by a
    hot-reloaded module.  A backend mismatch is fatal to readiness, because
    serving traffic from an empty SQLite file looks like an outage with data
    loss rather than a database problem.
    """
    return (os.environ.get("NIKO_STRICT_DB") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _startup_error_rows(bot) -> list[tuple[str, str]]:
    """Normalise the two startup error formats the bot has used over time."""
    rows: list[tuple[str, str]] = []
    recorded = getattr(bot, "startup_step_errors", None)
    if isinstance(recorded, dict):
        for step, error in recorded.items():
            rows.append((str(step), str(error)))
    elif isinstance(recorded, (list, tuple)):
        for item in recorded:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                rows.append((str(item[0]), str(item[1])))
            else:
                rows.append(("<unknown>", str(item)))

    # A process that recorded errors with an older on_ready still has the error
    # objects but not the step names.  Treat those as non-critical degradation:
    # inventing a fatal step would make an optional failure look like an outage.
    if not rows:
        for error in getattr(bot, "startup_errors", None) or ():
            rows.append(("<unknown>", str(error)))
    return rows


async def _ping_database(bot) -> tuple[bool, str]:
    pool = getattr(bot, "cxn", None)
    if pool is None:
        return False, "database pool is not attached"

    backend = getattr(pool, "db_type", "unknown")
    if strict_backend() and backend != "mongodb":
        return False, f"{backend} (NIKO_STRICT_DB requires mongodb)"
    try:
        if backend == "mongodb":
            client = getattr(pool, "client", None)
            if client is None:
                raise RuntimeError("MongoDB pool has no client")
            await client.admin.command("ping")
        else:
            # Both the SQLite pool and a test double expose fetchval; the SQLite
            # backend naturally accepts this statement.
            await pool.fetchval("SELECT 1")
    except Exception as exc:
        return False, f"database ping failed ({backend}): {type(exc).__name__}: {exc}"
    return True, backend


def _check_gateway(bot) -> tuple[bool, str]:
    is_ready = getattr(bot, "is_ready", None)
    try:
        if not callable(is_ready) or not is_ready():
            return False, "gateway is not ready"
    except Exception as exc:
        return False, f"gateway readiness check failed: {type(exc).__name__}: {exc}"

    shards = getattr(bot, "shards", None) or {}
    expected = int(getattr(bot, "shard_count", 0) or 0)
    if shards and expected and len(shards) < expected:
        return False, f"only {len(shards)}/{expected} gateway shards are connected"
    for shard_id, shard in shards.items():
        try:
            if shard is None or shard.is_closed():
                return False, f"gateway shard {shard_id} is closed"
        except Exception as exc:
            return False, f"gateway shard {shard_id} check failed: {type(exc).__name__}: {exc}"
    return True, f"{expected or len(shards) or 1} shard(s)"


def _check_cogs(bot) -> tuple[list[str], dict[str, str]]:
    required = critical_cogs()
    records = list(getattr(bot, "cog_status", None) or ())
    by_name: dict[str, dict[str, Any]] = {}
    for record in records:
        if isinstance(record, dict):
            name = str(record.get("name") or "").strip()
            if name:
                by_name[name] = record

    missing: list[str] = []
    failed: dict[str, str] = {}
    for name in required:
        record = by_name.get(name)
        if record is None:
            missing.append(name)
            continue
        state = str(record.get("state") or "").lower()
        if state not in _LOADED_COG_STATES:
            failed[name] = str(record.get("reason") or state or "not loaded")
    return missing, failed


async def evaluate(bot) -> dict[str, Any]:
    """Return a readiness snapshot: ``ready``, ``degraded`` or ``not_ready``.

    ``not_ready`` is reserved for the checks that make the process unsafe to
    receive traffic (no database, no gateway, a missing critical cog).  An
    optional startup failure only produces ``degraded`` so the bot can still
    serve while it says what is wrong.
    """
    reasons: list[str] = []
    critical: list[str] = []
    checks: dict[str, Any] = {}

    ok, backend = await _ping_database(bot)
    checks["database"] = {"ok": ok, "detail": backend}
    if not ok:
        critical.append(backend)

    ok, detail = _check_gateway(bot)
    checks["gateway"] = {"ok": ok, "detail": detail}
    if not ok:
        critical.append(detail)

    try:
        missing, failed_cogs = _check_cogs(bot)
    except Exception as exc:
        missing, failed_cogs = list(critical_cogs()), {"<checker>": str(exc)}
    checks["critical_cogs"] = {
        "ok": not missing and not failed_cogs,
        "missing": missing,
        "failed": failed_cogs,
    }
    if missing:
        critical.append("critical cogs missing: " + ", ".join(missing))
    for name, error in failed_cogs.items():
        critical.append(f"critical cog {name} is not loaded: {error}")

    # A public key is only required for HTTP-delivered interactions.  A gateway
    # deployment can still answer them, so a missing key degrades the process
    # instead of taking it out of rotation.
    try:
        from utils.runtime.interaction_endpoint import public_key_configured

        interactions_ok = bool(public_key_configured())
    except Exception:
        interactions_ok = False
    checks["interactions_endpoint"] = {"ok": interactions_ok}
    if not interactions_ok:
        reasons.append("interactions endpoint has no public key")

    startup_errors = _startup_error_rows(bot)
    checks["startup_errors"] = [{"step": step, "error": error} for step, error in startup_errors]
    fatal_steps = set(critical_steps())
    for step, error in startup_errors:
        if step in fatal_steps:
            critical.append(f"critical startup step {step} failed: {error}")
        else:
            reasons.append(f"startup step {step} failed: {error}")

    state = "not_ready" if critical else ("degraded" if reasons else "ready")
    return {
        "state": state,
        "ready": state != "not_ready",
        "reasons": [*critical, *reasons],
        "critical": critical,
        "checks": checks,
    }
