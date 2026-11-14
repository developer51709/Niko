"""Direct file deployment for the owner MCP server.

The normal update path pulls from a running beta instance.  The MCP server is
the replacement for that source: an authenticated MCP client sends the files it
changed, this module writes them with the same backups, syntax checks and
area reloads as the beta path, and the bot/deployment picks the change up
without a git push or a staff-page pull.

Files are limited to the areas :mod:`webapp.updates` can safely reload.  A
path outside those areas is rejected rather than written, and deployment-owned
config files keep the same additive rule the beta path uses: an existing config
module is never replaced except for ``config/links.py``.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import os
import shutil
import time
from pathlib import Path

from utils.runtime import handoff, supervisor_control

from . import updates

MAX_FILES = 250
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 40 * 1024 * 1024


def _text(value, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    return value


def _bytes_for(entry: dict) -> tuple[bytes | None, str]:
    """Decode one payload and return its bytes plus the status we should record."""
    status = str(entry.get("status") or "modified").strip().lower()
    if status not in {"added", "modified", "removed"}:
        raise ValueError("Each file status must be added, modified, or removed.")
    if status == "removed":
        return None, status

    encoding = str(entry.get("encoding") or "utf-8").strip().lower()
    content = entry.get("content")
    if not isinstance(content, str):
        raise ValueError("Each file needs string content, or status=removed.")
    if encoding in {"utf-8", "utf8", "text"}:
        body = content.encode("utf-8")
    elif encoding in {"base64", "b64"}:
        try:
            body = base64.b64decode(content, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("A base64 file payload is not valid base64.") from exc
    else:
        raise ValueError("encoding must be utf-8 or base64.")
    if len(body) > MAX_FILE_BYTES:
        raise ValueError(f"{entry.get('path')} is larger than the 8 MiB file limit.")
    return body, status


def _normalise(files) -> list[dict]:
    if not isinstance(files, list) or not files:
        raise ValueError("files must be a non-empty list.")
    if len(files) > MAX_FILES:
        raise ValueError(f"At most {MAX_FILES} files may be pushed at once.")

    entries: list[dict] = []
    total = 0
    seen: set[str] = set()
    for raw in files:
        if not isinstance(raw, dict):
            raise ValueError("Each file must be an object.")
        relative = _text(raw.get("path"), "path").replace("\\", "/")
        if relative.startswith("/") or ".." in Path(relative).parts:
            raise ValueError(f"{relative!r} is not a repository-relative path.")
        if relative in seen:
            raise ValueError(f"{relative} was sent more than once.")
        area = updates.area_for_path(relative)
        if area is None:
            raise ValueError(
                f"{relative!r} is outside the deployable areas "
                f"({', '.join(updates.AREA_ORDER)})."
            )
        if updates._ignored(relative):
            raise ValueError(f"{relative!r} is a generated or temporary file.")
        body, status = _bytes_for(raw)
        target = updates.ROOT / relative
        if status != "removed":
            # Rollback treats an add and a replace differently, so record the
            # state the disk is actually in rather than trusting the caller.
            status = "modified" if target.is_file() else "added"
        if status == "removed" and updates.AREAS[area].get("additive"):
            # The beta path never offers deletions from an additive area: an
            # existing config module belongs to this deployment, not to the
            # upstream source. A direct MCP push must follow the same rule, or
            # it could delete config/ids.py and take the next bot boot with it.
            raise ValueError(
                f"{relative} is in an additive area and cannot be removed by an update."
            )
        if body is not None:
            if updates.area_for_path(relative) == "support" and target.is_file():
                if not updates._replaceable("support", relative):
                    raise ValueError(
                        f"{relative} is deployment-specific configuration and is "
                        "never replaced by an update."
                    )
            if relative.endswith(".py"):
                try:
                    compile(body, relative, "exec")
                except SyntaxError as exc:
                    raise ValueError(
                        f"{relative} has a syntax error: {exc.msg} (line {exc.lineno})"
                    ) from exc
            total += len(body)
            if total > MAX_TOTAL_BYTES:
                raise ValueError("The push is larger than the 40 MiB total limit.")
        seen.add(relative)
        entries.append({
            "path": relative,
            "area": area,
            "status": status,
            "body": body,
            "bytes": len(body or b""),
            "sha": hashlib.sha1(body).hexdigest() if body is not None else None,
        })
    return entries


def _stage(area: str, changes: list[dict], run_id: str) -> dict:
    written = 0
    removed = 0
    for change in changes:
        relative = change["path"]
        path = updates.ROOT / relative
        backup = updates._backup_path(run_id, relative)
        if path.is_file():
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup)
        updates._drop_bytecode(relative)
        if change["status"] == "removed":
            if path.is_file():
                path.unlink()
                removed += 1
            continue
        updates._python_check(relative, change["body"])
        updates._write(relative, change["body"])
        written += 1
    return {
        "written": written,
        "removed": removed,
        "backup": str(updates._backup_path(run_id, ".").parent),
    }


def _reload(area: str, changes: list[dict], bot, current: dict) -> dict:
    outcome: dict = {"ok": True}
    if area == "support":
        outcome["strategy"] = "wrote shared modules"
    elif area == "website":
        outcome["strategy"] = "served from disk on the next request"
    elif area == "cogs":
        if bot is None:
            raise RuntimeError("The bot is not running.")
        names = updates._extensions_for([change["path"] for change in changes])
        outcome.update(updates._reload_summary(updates.reload_cogs(bot, names)))
        outcome["strategy"] = "reloaded extensions"
    elif area == "utils":
        if bot is None:
            raise RuntimeError("The bot is not running.")
        prefixes = updates._utils_prefixes([change["path"] for change in changes])
        outcome["purged"] = updates._purge(prefixes)
        outcome.update(updates._reload_summary(updates.reload_extensions(bot)))
        outcome["dashboard"] = updates.reload_webapp(bot)
        outcome["strategy"] = "reloaded modules, extensions and the dashboard"
    elif area == "webapp":
        outcome["dashboard"] = updates.reload_webapp(bot)
        outcome["strategy"] = "rebuilt the dashboard app"
    elif area == "database":
        outcome.update(updates.reload_database(bot))
        outcome["strategy"] = "re-ran the database schema setup"
    elif area == "events":
        outcome.update(updates._reload_summary(updates.reload_events(
            [change["path"] for change in changes]
        )))
        outcome["strategy"] = "re-imported the gateway event handlers"
    elif area == "startup":
        if any(change["status"] == "removed" for change in changes):
            raise RuntimeError("The startup writers file cannot be removed.")
        outcome.update(updates.reload_startup_writers(
            bot, [change["path"] for change in changes]
        ))
        outcome["strategy"] = "re-imported the startup writers"
    elif area == "bot":
        updates._probe_bot()
        import api_server

        if not updates._serving(api_server):
            raise RuntimeError("The dashboard is not serving; a bot restart would leave the site down.")
        outcome["strategy"] = "restarting the bot"
    else:
        raise RuntimeError(f"{area} has no reload strategy.")
    return outcome


def apply_payloads(files, bot=None, actor: str = "MCP") -> dict:
    """Write files from an MCP push and reload the areas they belong to.

    The response is deliberately shaped like ``updates.apply`` so the staff page
    and MCP clients can read the same fields.
    """
    entries = _normalise(files)
    gate = updates._apply_gate
    if not gate.acquire(blocking=False):
        return {
            "ok": False,
            "error": "An update is already being applied.",
            "areas": {},
            "last": updates.last_run(),
        }

    chosen = [name for name in updates.AREA_ORDER if any(item["area"] == name for item in entries)]
    run_id = time.strftime("%Y%m%d-%H%M%S") + "-mcp"
    started = int(time.time())
    results: dict[str, dict] = {}
    handoff_needed = False
    supervised_restart_needed = False
    web_restart_needed = False
    current = {
        "ok": True,
        "configured": True,
        "source": "mcp",
        "areas": {
            name: {
                "label": updates.AREAS[name]["label"],
                "changed": sum(1 for item in entries if item["area"] == name),
                "bytes": sum(item["bytes"] for item in entries if item["area"] == name),
                "files": [
                    {"path": item["path"], "status": item["status"], "bytes": item["bytes"]}
                    for item in entries if item["area"] == name
                ],
                "truncated": 0,
                "available": True,
            }
            for name in chosen
        },
        "total_changed": len(entries),
        "total_bytes": sum(item["bytes"] for item in entries),
        "running": True,
        "last": updates.last_run(),
    }

    updates._running.update({
        "active": True,
        "areas": list(chosen),
        "started_at": started,
        "area": chosen[0] if chosen else None,
        "index": 0,
        "total": len(chosen),
        "done": [],
        "phase": "starting",
    })

    try:
        for index, name in enumerate(chosen):
            changes = [item for item in entries if item["area"] == name]
            updates._set_progress(area=name, index=index, phase="applying")
            try:
                staged = _stage(name, changes, run_id)
                outcome = {"ok": True, "changed": len(changes), **staged}
                outcome.update(_reload(name, changes, bot, current))
                if name == "bot":
                    if supervisor_control.is_supervised():
                        if not supervisor_control.socket_path():
                            raise RuntimeError(
                                "This is a supervised child but no supervisor control socket is configured."
                            )
                        outcome["strategy"] = "requesting a supervised restart"
                        supervised_restart_needed = True
                    else:
                        updates._inplace_handoff()
                        outcome["strategy"] = "restarting this process in place"
                        handoff_needed = True
                if name == "webapp" and updates._split_web() and supervisor_control.is_supervised():
                    web_restart_needed = True
            except Exception as exc:
                updates._restore_area(name, changes, run_id)
                updates._rebuild_after_rollback(name, bot)
                outcome = {
                    "ok": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "rolled_back": True,
                }
                updates._set_progress(phase="failed")
            results[name] = outcome
            updates._running["done"].append(name)
            updates._set_progress(phase="applied")
    finally:
        updates._progress_reset()

    # Keep the gate for the bookkeeping and restart request too. Releasing it as
    # soon as the file loop ended let a second MCP push write bot files while the
    # first restart was still pending, so the restarted process could load a mix
    # of both runs. The outer finally still releases on any failure here.
    try:
        run = {
            "id": run_id,
            "started_at": started,
            "finished_at": int(time.time()),
            "source": "mcp",
            "actor": actor,
            "areas": results,
            "handoff": handoff_needed,
            "supervised_restart": supervised_restart_needed,
        }
        updates._record(run)

        if handoff_needed:
            handoff.schedule()
        elif supervised_restart_needed:
            try:
                updates._mark_pending(run_id, "bot", [
                    {"path": item["path"], "status": item["status"]}
                    for item in entries if item["area"] == "bot"
                ])
                supervisor_control.request_restart(
                    reason="MCP bot update",
                    delay=float(os.environ.get("NIKO_SUPERVISED_RESTART_DELAY", "2.0") or 2.0),
                    child=(
                        ["bot", "db"]
                        if updates._split_db()
                        else ("bot" if updates._split_web() else None)
                    ),
                )
            except Exception as exc:
                updates._clear_pending()
                updates._restore_area("bot", [
                    {"path": item["path"], "status": item["status"]}
                    for item in entries if item["area"] == "bot"
                ], run_id)
                updates._rebuild_after_rollback("bot", bot)
                results["bot"].update({
                    "ok": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "rolled_back": True,
                })
                run.update({
                    "ok": False,
                    "error": f"supervised restart was not requested: {type(exc).__name__}: {exc}",
                    "finished_at": int(time.time()),
                })
                updates._record(run)

        if web_restart_needed and not handoff_needed:
            try:
                supervisor_control.request_restart(
                    reason="MCP webapp update",
                    delay=float(os.environ.get("NIKO_SUPERVISED_RESTART_DELAY", "2.0") or 2.0),
                    child="web",
                )
            except Exception as exc:
                results["webapp"].update({
                    "ok": False,
                    "error": f"the dashboard child was not restarted: {type(exc).__name__}: {exc}",
                })

        return {
            **current,
            "ok": all(item.get("ok", True) for item in results.values()),
            "run": run_id,
            "areas": results,
            "last": updates.last_run(),
        }
    finally:
        gate.release()
