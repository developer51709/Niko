"""Owner-triggered updates pulled from the beta instance.

Production is normally updated by deploying a new build from git, which costs
the whole process: the gateway reconnects, every cog reloads, the dashboard is
unreachable. Most updates do not need that. A cog fix needs one extension
reloaded; a website change is just files in ``src/website/dist``; a route change
needs the Flask app rebuilt and nothing else.

This module stages files from beta and then applies them area by area:

===========  ==================================================================
``website``  copied into ``src/website/dist``; Flask serves that folder from
             disk, so the next request is the new site. Nothing restarts.
``cogs``     the changed ``cogs/<package>`` modules are dropped from
             ``sys.modules`` (the cached import) and the affected extensions are
             reloaded, so the new file is what imports — no restart.
``utils``    the changed ``utils.*`` modules are dropped, every loaded extension
             is reloaded on top of them, and the dashboard is rebuilt.
``webapp``   every ``webapp.*`` module is re-imported and the new Flask app is
             swapped into the running server, so the API keeps its socket and
             its thread while the routes change underneath it.
``bot``      ``src/bot.py`` and the startup chain: the only area Python cannot
             reload into the same process, so it is handed to a successor (see
             :mod:`utils.handoff`) while the gateway stays connected.

Every area is optional and applied in the order above, so selecting a cog fix
and a website tweak does not touch the process at all.

Safety:

- Files are hashed against beta's manifest before they are written, and a bad
  download leaves the previous file in place.
- Whatever is replaced is copied to ``data/updates/backups/<run>/`` first, and a
  failed reload restores that area's files from it.
- Without ``BETA_INSTANCE_URL`` and ``BETA_UPDATE_TOKEN`` the page reports the
  update feed as unavailable and no endpoint can serve source files.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import shutil
import sys
import threading
import time
from pathlib import Path

import requests

from . import locale_feed

#: Repository root: ``src/webapp/updates.py`` → three levels up.
ROOT = Path(__file__).resolve().parents[2]

#: Where backups and the last run are kept.
DATA_DIR = ROOT / "data" / "updates"

#: Areas in apply order. A file belongs to the first area whose path it is under.
AREAS: dict[str, dict] = {
    "website": {"label": "Website build", "paths": ("src/website/dist/",)},
    "cogs": {"label": "Cog extensions", "paths": ("src/cogs/",)},
    "utils": {"label": "Utilities", "paths": ("src/utils/",)},
    "webapp": {"label": "API & dashboard", "paths": ("src/webapp/",)},
    "bot": {
        "label": "Bot core",
        # ``src/config`` stays out on purpose: it holds the guild ids, links and
        # status copy this deployment was configured with, which beta must not
        # overwrite just because the bot code changed.
        "paths": ("src/bot.py", "src/api_server.py", "src/events/", "src/database/"),
    },
}

AREA_ORDER = ("website", "cogs", "utils", "webapp", "bot")

#: Files that never travel: bytecode, editor state, and the update's own data.
SKIPPED_PARTS = {"__pycache__", ".pytest_cache", ".git", "node_modules"}
SKIPPED_SUFFIXES = {".pyc", ".pyo", ".swp", ".tmp"}

_MANIFEST_TTL = 10.0
_manifest_cache: dict = {"at": 0.0, "document": None, "error": None}
_lock = threading.Lock()
_running = {"active": False, "areas": [], "started_at": None}


# ──────────────────────────────────────────────────────────────────────────────
# Beta
# ──────────────────────────────────────────────────────────────────────────────
def beta_base() -> str:
    return locale_feed.BETA_INSTANCE_URL


def token() -> str:
    return (os.environ.get("BETA_UPDATE_TOKEN") or "").strip()


def configured() -> bool:
    return bool(beta_base() and token())


def area_for_path(relative: str) -> str | None:
    """Which area owns a repository-relative path, or ``None`` outside them."""
    if not relative or relative.startswith("/") or ".." in Path(relative).parts:
        return None
    for name in AREA_ORDER:
        for prefix in AREAS[name]["paths"]:
            if prefix.endswith("/"):
                if relative.startswith(prefix):
                    return name
            elif relative == prefix:
                return name
    return None


def _ignored(relative: str) -> bool:
    parts = Path(relative).parts
    if any(part in SKIPPED_PARTS for part in parts):
        return True
    return Path(relative).suffix in SKIPPED_SUFFIXES


def _files(area: str, root: Path = ROOT) -> list[str]:
    """Every updatable file in one area, repository-relative."""
    found: list[str] = []
    for prefix in AREAS[area]["paths"]:
        target = root / prefix
        if target.is_file():
            found.append(prefix)
            continue
        if not target.is_dir():
            continue
        for path in target.rglob("*"):
            if not path.is_file():
                continue
            relative = str(path.relative_to(root))
            if not _ignored(relative):
                found.append(relative)
    return sorted(set(found))


def area_files(area: str) -> list[str]:
    """Public name for :func:`_files`, used by the beta-side manifest."""
    return _files(area)


def file_sha(path) -> str:
    return _sha(Path(path))


def _sha(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def beta_manifest(force: bool = False) -> dict | None:
    """Read beta's file list, or ``None`` when the feed is not usable."""
    if not configured():
        return None
    now = time.monotonic()
    with _lock:
        cached = _manifest_cache["document"]
        if cached and not force and now - _manifest_cache["at"] < _MANIFEST_TTL:
            return cached
    try:
        response = requests.get(
            f"{beta_base()}/api/updates/manifest.json",
            headers={"X-Update-Token": token(), "Accept": "application/json"},
            timeout=(2.0, 8.0),
        )
        if response.status_code != 200:
            raise ValueError(f"beta answered {response.status_code}")
        document = response.json()
        if not isinstance(document, dict) or not isinstance(document.get("areas"), dict):
            raise ValueError("beta returned no file list")
        with _lock:
            _manifest_cache.update({"document": document, "at": now, "error": None})
        return document
    except Exception as exc:
        with _lock:
            _manifest_cache.update({"error": f"{type(exc).__name__}: {exc}", "document": cached})
            return cached


def manifest_error() -> str | None:
    return _manifest_cache["error"]


# ──────────────────────────────────────────────────────────────────────────────
# Plans
# ──────────────────────────────────────────────────────────────────────────────
def _selected(areas) -> list[str]:
    """``None`` means every area; an empty list means none of them."""
    if areas is None:
        return list(AREA_ORDER)
    if isinstance(areas, str):
        areas = [areas]
    return [name for name in AREA_ORDER if name in set(areas)]


def plan(areas=None) -> dict:
    """What beta has that this deployment does not, area by area."""
    chosen = _selected(areas)
    document = beta_manifest()
    if document is None:
        return {
            "ok": False,
            "configured": configured(),
            "beta": beta_base() or None,
            "error": (
                manifest_error()
                or "Set BETA_INSTANCE_URL and BETA_UPDATE_TOKEN to read updates from beta."
            ),
            "areas": {},
            "total_changed": 0,
            "total_bytes": 0,
            "running": _running["active"],
            "last": last_run(),
        }

    result: dict[str, dict] = {}
    total_changed = 0
    total_bytes = 0
    for name in chosen:
        remote = (document.get("areas", {}).get(name) or {}).get("files") or {}
        local_files = set(_files(name))
        changes = []
        for relative, info in sorted(remote.items()):
            if area_for_path(relative) != name:
                continue
            sha = (info or {}).get("sha")
            size = int((info or {}).get("size") or 0)
            if not isinstance(sha, str) or not sha:
                continue
            path = ROOT / relative
            if not path.exists():
                changes.append({"path": relative, "status": "added", "bytes": size, "sha": sha})
            else:
                try:
                    current = _sha(path)
                except OSError:
                    current = None
                if current != sha:
                    changes.append({"path": relative, "status": "modified", "bytes": size, "sha": sha})
        for relative in sorted(local_files - set(remote)):
            changes.append({"path": relative, "status": "removed", "bytes": 0, "sha": None})

        count = len(changes)
        size = sum(change["bytes"] for change in changes if change["status"] != "removed")
        total_changed += count
        total_bytes += size
        result[name] = {
            "label": AREAS[name]["label"],
            "changed": count,
            "bytes": size,
            "files": changes[:60],
            "truncated": max(0, count - 60),
        }

    return {
        "ok": True,
        "configured": True,
        "beta": beta_base(),
        "generated_at": int(document.get("generated_at") or 0),
        "areas": result,
        "total_changed": total_changed,
        "total_bytes": total_bytes,
        "running": _running["active"],
        "last": last_run(),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Staging files
# ──────────────────────────────────────────────────────────────────────────────
def _backup_path(run_id: str, relative: str) -> Path:
    return DATA_DIR / "backups" / run_id / relative


def _download(relative: str, expected: str) -> bytes:
    response = requests.get(
        f"{beta_base()}/api/updates/file",
        params={"path": relative},
        headers={"X-Update-Token": token()},
        timeout=(2.0, 20.0),
    )
    if response.status_code != 200:
        raise ValueError(f"beta answered {response.status_code} for {relative}")
    body = response.content
    if hashlib.sha1(body).hexdigest() != expected:
        raise ValueError(f"hash mismatch for {relative}")
    return body


def _write(relative: str, body: bytes) -> None:
    """Replace a file in one step, so a crash can never leave half of it."""
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.niko-update")
    temporary.write_bytes(body)
    os.replace(temporary, path)


def _stage_area(name: str, changes: list[dict], run_id: str) -> dict:
    """Write one area's changed files, keeping a backup of what was there."""
    written = 0
    removed = 0
    try:
        for change in changes:
            relative = change["path"]
            path = ROOT / relative
            backup = _backup_path(run_id, relative)
            if path.is_file():
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, backup)
            if change["status"] == "removed":
                if path.is_file():
                    path.unlink()
                    removed += 1
                continue
            _write(relative, _download(relative, change["sha"]))
            written += 1
    except Exception:
        _restore_area(name, changes, run_id)
        raise
    return {"written": written, "removed": removed, "backup": str(_backup_path(run_id, ".").parent)}


def _restore_area(name: str, changes: list[dict], run_id: str) -> None:
    for change in changes:
        relative = change["path"]
        backup = _backup_path(run_id, relative)
        path = ROOT / relative
        try:
            if backup.is_file():
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup, path)
            elif path.is_file() and change["status"] == "added":
                path.unlink()
        except OSError:
            continue


# ──────────────────────────────────────────────────────────────────────────────
# Reloading
# ──────────────────────────────────────────────────────────────────────────────
def _purge(prefixes) -> list[str]:
    """Drop cached imports so the next import reads the file on disk."""
    dropped = []
    for name in list(sys.modules):
        if not isinstance(name, str):
            continue
        for prefix in prefixes:
            if name == prefix or name.startswith(prefix + "."):
                sys.modules.pop(name, None)
                dropped.append(name)
                break
    importlib.invalidate_caches()
    return dropped


def _extensions_for(files) -> set[str]:
    """``src/cogs/ai/chat.py`` → ``cogs.ai``."""
    found = set()
    for relative in files:
        parts = Path(relative).parts
        if len(parts) >= 4 and parts[0] == "src" and parts[1] == "cogs":
            found.add(f"cogs.{parts[2]}")
        elif len(parts) == 3 and parts[:2] == ("src", "cogs") and parts[2].endswith(".py"):
            found.add(f"cogs.{parts[2][:-3]}")
    return found


def _run(coroutine):
    """Run one coroutine on the bot loop from this worker thread."""
    from .runtime import run_on_bot_loop

    return run_on_bot_loop(coroutine, timeout=60)


def reload_cogs(bot, extensions) -> dict:
    """Reload only the extensions whose files changed, from freshly imported code."""
    loaded = set(getattr(bot, "extensions", {}) or {})
    reloaded, loaded_new, unloaded, failed = [], [], [], []
    for name in sorted(extensions):
        package = ROOT / "src" / Path(*name.split(".")) / "__init__.py"
        _purge([name])
        try:
            if not package.is_file():
                # Deleted on beta: stop running it. Anything never loaded here is
                # simply skipped, since unloading it would raise.
                if name in loaded:
                    _run(bot.unload_extension(name))
                    unloaded.append(name)
            elif name in loaded:
                _run(bot.reload_extension(name))
                reloaded.append(name)
            else:
                _run(bot.load_extension(name))
                loaded_new.append(name)
        except Exception as exc:
            failed.append(f"{name}: {type(exc).__name__}: {exc}")
    return {"reloaded": reloaded, "loaded": loaded_new, "unloaded": unloaded, "failed": failed}


def reload_extensions(bot, names=None) -> dict:
    """Reload every loaded extension, for a change they all import (utils)."""
    loaded = sorted(getattr(bot, "extensions", {}) or {})
    if names is not None:
        loaded = [name for name in loaded if name in set(names)]
    reloaded, failed = [], []
    for name in loaded:
        try:
            _run(bot.reload_extension(name))
            reloaded.append(name)
        except Exception as exc:
            failed.append(f"{name}: {type(exc).__name__}: {exc}")
    return {"reloaded": reloaded, "failed": failed}


def reload_webapp(bot) -> dict:
    """Rebuild the Flask application and swap it into the running server.

    Werkzeug reads ``server.app`` per request, so replacing it changes every
    route at once while the listening socket, its thread and every open
    connection stay exactly where they are. This module is deliberately kept
    alive across the purge: it is the code executing this call.
    """
    # Kept alive across the purge: this module is executing the call, and the
    # locale feed owns the caches the rebuilt routes read on the first request.
    keep = {__name__, "webapp.locale_feed"}
    for name in list(sys.modules):
        if name == "webapp" or name.startswith("webapp."):
            if name in keep:
                continue
            sys.modules.pop(name, None)
    importlib.invalidate_caches()

    fresh = importlib.import_module("webapp")
    fresh.configure_bot(bot)
    from api_server import replace_app

    replace_app(fresh.app)
    return {"swapped": True, "routes": len(fresh.app.url_map._rules)}


# ──────────────────────────────────────────────────────────────────────────────
# Applying
# ──────────────────────────────────────────────────────────────────────────────
def _record(run: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary = DATA_DIR / "last.json.tmp"
    temporary.write_text(json.dumps(run, indent=2), encoding="utf-8")
    os.replace(temporary, DATA_DIR / "last.json")


def last_run() -> dict | None:
    try:
        return json.loads((DATA_DIR / "last.json").read_text(encoding="utf-8"))
    except Exception:
        return None


def apply(areas, bot=None) -> dict:
    """Stage and apply the selected areas, then report what each one did."""
    chosen = _selected(areas)
    current = plan(chosen)
    if not current["ok"]:
        return current
    if _running["active"]:
        return {**current, "ok": False, "error": "An update is already being applied."}

    _running.update({"active": True, "areas": chosen, "started_at": int(time.time())})
    run_id = time.strftime("%Y%m%d-%H%M%S")
    started = int(time.time())
    results: dict[str, dict] = {}
    handoff_needed = False

    try:
        for name in chosen:
            changes = (current["areas"].get(name) or {}).get("changed", 0)
            if not changes:
                results[name] = {"changed": 0, "strategy": "nothing to do"}
                continue
            try:
                staged = _stage_area(name, current["areas"][name]["files"], run_id)
            except Exception as exc:
                results[name] = {"ok": False, "error": f"{type(exc).__name__}: {exc}", "rolled_back": True}
                _record({"id": run_id, "started_at": started, "finished_at": int(time.time()), "areas": results})
                return {**current, "ok": False, "run": run_id, "areas": results, "last": last_run()}

            outcome = {"ok": True, "changed": changes, **staged}
            try:
                if name == "cogs":
                    if bot is None:
                        raise RuntimeError("The bot is not running.")
                    names = _extensions_for([change["path"] for change in current["areas"][name]["files"]])
                    outcome.update(_reload_summary(reload_cogs(bot, names)))
                    outcome["strategy"] = "reloaded extensions"
                elif name == "utils":
                    if bot is None:
                        raise RuntimeError("The bot is not running.")
                    prefixes = _utils_prefixes(current["areas"][name]["files"])
                    outcome["purged"] = _purge(prefixes)
                    outcome.update(_reload_summary(reload_extensions(bot)))
                    outcome.update({"dashboard": reload_webapp(bot)})
                    outcome["strategy"] = "reloaded modules, extensions and the dashboard"
                elif name == "webapp":
                    if bot is None:
                        raise RuntimeError("The bot is not running.")
                    outcome["dashboard"] = reload_webapp(bot)
                    outcome["strategy"] = "rebuilt the dashboard app"
                elif name == "website":
                    outcome["strategy"] = "served from disk on the next request"
                elif name == "bot":
                    # The successor process imports everything afresh; the files
                    # are already in place before it starts.
                    outcome["strategy"] = "handing the process over"
                    handoff_needed = True
            except Exception as exc:
                _restore_area(name, current["areas"][name]["files"], run_id)
                outcome = {"ok": False, "error": f"{type(exc).__name__}: {exc}", "rolled_back": True}
                _rebuild_after_rollback(name, bot)
            results[name] = outcome
    finally:
        _running.update({"active": False, "areas": [], "started_at": None})

    run = {
        "id": run_id,
        "started_at": started,
        "finished_at": int(time.time()),
        "areas": results,
        "handoff": handoff_needed,
    }
    _record(run)

    if handoff_needed:
        from utils import handoff

        handoff.schedule(bot)

    return {**current, "ok": all(item.get("ok", True) for item in results.values()), "run": run_id, "areas": results, "last": last_run()}


def _reload_summary(result: dict) -> dict:
    summary = {}
    if result.get("reloaded"):
        summary["reloaded"] = result["reloaded"]
    if result.get("loaded"):
        summary["loaded"] = result["loaded"]
    if result.get("unloaded"):
        summary["unloaded"] = result["unloaded"]
    if result.get("failed"):
        summary["failed"] = result["failed"]
    return summary


def _utils_prefixes(files) -> list[str]:
    """``src/utils/ai/config.py`` → ``utils.ai`` so the whole package reloads."""
    prefixes = set()
    for relative in files:
        parts = Path(relative).parts
        if len(parts) >= 4 and parts[0] == "src" and parts[1] == "utils":
            prefixes.add(f"utils.{parts[2]}")
        elif len(parts) == 3 and parts[:2] == ("src", "utils") and parts[2].endswith(".py"):
            prefixes.add(f"utils.{parts[2][:-3]}")
    return sorted(prefixes)


def _rebuild_after_rollback(name: str, bot) -> None:
    """Put the running process back on the code it was executing before."""
    try:
        if name in {"utils", "webapp"} and bot is not None:
            reload_webapp(bot)
        elif name == "cogs" and bot is not None:
            for extension in list(getattr(bot, "extensions", {}) or {}):
                if extension.startswith("cogs."):
                    _purge([extension])
                    _run(bot.reload_extension(extension))
    except Exception:
        pass
