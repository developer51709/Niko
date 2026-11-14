"""Owner-triggered updates pulled from the beta instance.

Production is normally updated by deploying a new build from git, which costs
the whole process: the gateway reconnects, every cog reloads, the dashboard is
unreachable. Most updates do not need that. A cog fix needs one extension
reloaded; a website change is just files in ``src/website/dist``; a route change
needs the Flask app rebuilt and nothing else.

This module stages files from beta and then applies them area by area:

===========  ==================================================================
``support``  shared ``src/config/*.py`` modules — a module the areas below
             import must exist before they reload. Existing config files keep
             this deployment's own ids and copy, except ``config/links.py``,
             which always carries production URLs and is replaced in full
``website``  copied into ``src/website/dist``; Flask serves that folder from
             disk, so the next request is the new site. Nothing restarts.
``cogs``     the changed ``cogs/<package>`` modules are dropped from
             ``sys.modules`` (the cached import) and the affected extensions are
             reloaded, so the new file is what imports — no restart.
``utils``    the changed ``utils.*`` modules are dropped, every loaded extension
             is reloaded on top of them, and the dashboard is rebuilt.
``database`` ``src/events/startup/database.py`` only: re-imported and its
             ``init_database`` run again, which creates missing tables, adds
             missing columns and repeats the idempotent migrations on the live
             pool, so code applied later in the same run can use them. The
             process keeps running.
``webapp``   every ``webapp.*`` module is re-imported and the new Flask app is
             swapped into the running server, so the API keeps its socket and
             its thread while the routes change underneath it.
``events``   the gateway event modules (``src/events/on_*.py``) are re-imported and
             the name ``bot.py``'s callbacks look up is rebound, so the next
             message runs the new handler. Nothing restarts; most of the startup
             chain under ``src/events/startup/`` is not part of this area,
             because it runs once and reloading it would change nothing.
``startup``  ``src/events/startup/writers.py`` only: re-imported, its exports
             refreshed on the startup package, ``on_ready`` rebound and the
             writers run again. It is called from the ready handler rather than
             the bot core, so a writers change needs neither a process restart
             nor a cog reload.
``bot``      ``src/bot.py`` and the remaining startup chain: the only area Python cannot
             reload into the same process, so the process replaces its own image
             with ``execve``, keeping its PID and its listening socket (see
             :mod:`utils.runtime.handoff`). The port is never closed and a supervisor
             never sees an exit, which is what keeps a hosted deployment from
             recreating the instance and discarding the files just written. It
             also carries ``src/database/`` and ``src/db_child.py``; the restart
             names the database child beside the bot so both halves of the
             database API load the same files.

Every area is optional and applied in the order above, so selecting a cog fix
and a website tweak does not touch the process at all.

Safety:

- Files are hashed against beta's manifest before they are written, and a bad
  download leaves the previous file in place. A Python file that does not
  compile is refused the same way.
- The bot core is imported in a throwaway interpreter before the process is
  restarted on it, so an update that cannot load is rolled back while the
  running process is still serving.
- Whatever is replaced is copied to ``data/updates/backups/<run>/`` first, and a
  failed reload restores that area's files from it.
- Without ``BETA_INSTANCE_URL`` and ``BETA_UPDATE_TOKEN`` the page reports the
  update feed as unavailable and no endpoint can serve source files.
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import requests

from utils.runtime import supervisor_control

from . import locale_feed

#: Repository root: ``src/webapp/updates.py`` → three levels up.
ROOT = Path(__file__).resolve().parents[2]

#: Where backups and the last run are kept.
DATA_DIR = ROOT / "data" / "updates"

#: Areas in apply order. A file belongs to the first area whose path it is under.
AREAS: dict[str, dict] = {
    "support": {
        "label": "Shared modules",
        # ``src/config`` mostly holds each deployment's own ids and status copy,
        # so those files are additions only: a module that already exists here is
        # never replaced and one beta dropped is never deleted. A *new* module
        # has nothing to overwrite, and leaving it behind is what makes an update
        # import something this deployment does not have — ``ModuleNotFoundError:
        # No module named 'config.version'``. It applies before every other area
        # for that reason.
        #
        # ``links.py`` is the exception. It is only ever written with the
        # production URLs (beta reads PUBLIC_URL from its environment instead),
        # so beta's copy is safe to replace here and saves a manual pull plus a
        # full deployment restart for a link change.
        "paths": ("src/config/",),
        "additive": True,
        "replace_paths": ("src/config/links.py",),
    },
    "website": {"label": "Website build", "paths": ("src/website/dist/",)},
    "cogs": {"label": "Cog extensions", "paths": ("src/cogs/",)},
    "utils": {"label": "Utilities", "paths": ("src/utils/",)},
    "webapp": {"label": "API & dashboard", "paths": ("src/webapp/",)},
    "database": {
        "label": "Database schema",
        # The one file in the startup chain whose work can be repeated: its
        # ``init_database`` creates tables with ``IF NOT EXISTS`` and adds only
        # missing columns, so importing the new file and running it again applies
        # a new table, column or backfill to the live pool. The rest of
        # ``src/events/startup/`` only runs once and stays with the bot core.
        "paths": ("src/events/startup/database.py",),
    },
    "startup": {
        "label": "Startup writers",
        # The writers are imported by ``events.on_ready`` and called on every
        # READY, so the new module can be re-imported and the ready handler
        # rebound without a restart. The rest of the startup chain only runs at
        # boot and stays with the bot core.
        "paths": ("src/events/startup/writers.py",),
    },
    "events": {
        "label": "Gateway events",
        # ``bot.py`` imports these at start-up and calls them from the callbacks
        # it registered, so they can be re-imported and the callback's global
        # rebound without touching the process. The startup chain under
        # ``src/events/startup/`` runs once and is not here: it belongs to the
        # bot core, because reloading it would change nothing until a restart.
        "paths": ("src/events/",),
        "except_paths": ("src/events/startup/",),
    },
    "bot": {
        "label": "Bot core",
        # ``src/database/`` is the translation layer and ``src/db_child.py`` is
        # the process that owns it.  They have to change together: shipping a
        # new client while the database child still runs the old server would
        # leave the two halves of one API disagreeing, so the child script
        # travels with the area whose restart replaces that child.
        "paths": (
            "src/bot.py",
            "src/api_server.py",
            "src/db_child.py",
            "src/events/startup/",
            "src/database/",
        ),
        "except_paths": ("src/events/startup/database.py",),
    },
}

#: Apply order. The schema runs after the utilities it imports and before the
#: code that reads the tables it creates.
AREA_ORDER = ("support", "website", "cogs", "utils", "database", "webapp", "events", "startup", "bot")

#: Files that never travel: bytecode, editor state, and the update's own data.
SKIPPED_PARTS = {"__pycache__", ".pytest_cache", ".git", "node_modules"}
SKIPPED_SUFFIXES = {".pyc", ".pyo", ".swp", ".tmp"}

_MANIFEST_TTL = 10.0
_manifest_cache: dict = {"at": 0.0, "document": None, "error": None}
_lock = threading.Lock()
#: One apply at a time, including between the owner page and a beta push.  The
#: contention check used to sit after ``plan()``, so two callers that both
#: started planning before either set ``_running`` could apply concurrently.
_apply_gate = threading.Lock()
_running = {
    "active": False,
    "areas": [],
    "started_at": None,
    "area": None,
    "index": 0,
    "total": 0,
    "done": [],
    "phase": "",
}


def _set_progress(**changes) -> None:
    """Record where the run in flight has got to, for the page's live bar."""
    _running.update(changes)


def _progress_reset() -> None:
    _running.update({
        "active": False,
        "areas": [],
        "started_at": None,
        "area": None,
        "index": 0,
        "total": 0,
        "done": [],
        "phase": "",
    })


def progress() -> dict:
    """A snapshot of the update currently running, or an idle record."""
    return {
        "active": _running["active"],
        "areas": list(_running["areas"]),
        "area": _running["area"],
        "index": _running["index"],
        "total": _running["total"],
        "done": list(_running["done"]),
        "phase": _running["phase"],
        "started_at": _running["started_at"],
    }


# ──────────────────────────────────────────────────────────────────────────────
# Beta
# ──────────────────────────────────────────────────────────────────────────────
def beta_base() -> str:
    return locale_feed.BETA_INSTANCE_URL


def token() -> str:
    return (os.environ.get("BETA_UPDATE_TOKEN") or "").strip()


def configured() -> bool:
    return bool(beta_base() and token())


def production_base() -> str:
    """Origin of the production instance, as configured on beta."""
    return (os.environ.get("PRODUCTION_INSTANCE_URL") or "").strip().rstrip("/")


def push_to_production(areas=None) -> dict:
    """Ask production's supervisor to apply an update, even if its site is down.

    Beta is the only side that knows both the production origin and the shared
    token, so this is the recovery action when the owner cannot open production's
    dashboard.  The update itself still runs on production and still pulls from
    beta; the request only tells it to run now.
    """
    base = production_base()
    secret = token()
    if not base:
        return {
            "ok": False,
            "configured": False,
            "error": "PRODUCTION_INSTANCE_URL is not set on this instance.",
        }
    if not secret:
        return {
            "ok": False,
            "configured": False,
            "error": "BETA_UPDATE_TOKEN is not set on this instance.",
        }

    payload: dict = {}
    if areas is not None:
        if isinstance(areas, str):
            areas = [areas]
        if not isinstance(areas, list) or not areas or not all(
            isinstance(name, str) for name in areas
        ):
            return {"ok": False, "error": "areas must be a non-empty list of area names."}
        unknown = [name for name in areas if name not in set(AREA_ORDER)]
        if unknown:
            return {"ok": False, "error": f"Unknown areas: {', '.join(unknown)}"}
        payload["areas"] = list(areas)

    try:
        response = requests.post(
            f"{base}/supervisor/update",
            json=payload,
            headers={"X-Update-Token": secret, "Accept": "application/json"},
            # Do not follow a redirect with the shared token attached; the
            # configured origin is the only host that may receive it.
            allow_redirects=False,
            # Applying a bot-core change can take minutes; a lost response does
            # not mean production stopped, so the timeout is reported as such.
            timeout=(5.0, 600.0),
        )
    except requests.Timeout:
        return {
            "ok": False,
            "sent": True,
            "production": base,
            "error": "production did not answer within 10 minutes; the update may still be running there.",
        }
    except requests.RequestException as exc:
        return {
            "ok": False,
            "production": base,
            "error": f"could not reach production: {type(exc).__name__}: {exc}",
        }

    try:
        data = response.json()
    except ValueError:
        data = {"error": response.text[:300]}
    return {
        "ok": response.status_code == 200 and isinstance(data, dict) and bool(data.get("ok")),
        "status": response.status_code,
        "production": base,
        "result": data,
    }


def area_for_path(relative: str) -> str | None:
    """Which area owns a repository-relative path, or ``None`` outside them."""
    if not relative or relative.startswith("/") or ".." in Path(relative).parts:
        return None
    for name in AREA_ORDER:
        matched = False
        for prefix in AREAS[name]["paths"]:
            if prefix.endswith("/"):
                if relative.startswith(prefix):
                    matched = True
                    break
            elif relative == prefix:
                matched = True
                break
        if not matched:
            continue
        # An area can hand part of its tree to another one: the gateway events
        # live in ``src/events/`` but their startup chain is bot-core only.
        if any(relative.startswith(prefix) for prefix in AREAS[name].get("except_paths", ())):
            continue
        return name
    return None


def _replaceable(area: str, relative: str) -> bool:
    """Whether an additive area still replaces this exact file in full."""
    return relative in set(AREAS[area].get("replace_paths", ()))


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
            # Ownership, not the prefix, decides: an area with an ``except_paths``
            # must not list a file another area owns.
            if not _ignored(relative) and area_for_path(relative) == area:
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
        published = document.get("areas", {}).get(name)
        if published is None:
            # Beta does not publish this area at all — an older build, or a
            # feature it does not have yet. That is *not* "every file here was
            # deleted": reading it that way offered to remove this deployment's
            # ``src/events/on_*.py`` and then failed to re-import the modules it
            # had just deleted (ModuleNotFoundError: No module named
            # 'events.on_message').
            result[name] = {
                "label": AREAS[name]["label"],
                "changed": 0,
                "bytes": 0,
                "files": [],
                "truncated": 0,
                "available": False,
            }
            continue
        remote = (published or {}).get("files") or {}
        # An additive area normally only ever adds: beta's copy of a file this
        # deployment already has is a difference in configuration, not in code.
        # ``replace_paths`` opts a file back into the ordinary diff.
        additive = bool(AREAS[name].get("additive"))
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
            elif not additive or _replaceable(name, relative):
                try:
                    current = _sha(path)
                except OSError:
                    current = None
                if current != sha:
                    changes.append({"path": relative, "status": "modified", "bytes": size, "sha": sha})
        if not additive:
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
            "available": True,
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


def _pending_file() -> Path:
    """Where a supervised restart records what it replaced.

    Written just before the restart request. If the replacement child never
    becomes ready, the supervisor reads this and restores those files, so a
    release that cannot boot is not a dead end.
    """
    return DATA_DIR / "pending.json"


def _mark_pending(run_id: str, area: str, changes: list[dict]) -> None:
    """Record the files a supervised restart is about to boot from."""
    payload = {
        "run_id": run_id,
        "area": area,
        "requested_at": int(time.time()),
        "backup_dir": str(Path("data/updates/backups") / run_id),
        "changes": [
            {"path": change["path"], "status": change.get("status") or "modified"}
            for change in changes
        ],
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    pending = _pending_file()
    temporary = pending.with_name(f".{pending.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(temporary, pending)


def _clear_pending() -> None:
    """Forget a pending restart after this process rolled the update back."""
    try:
        _pending_file().unlink()
    except FileNotFoundError:
        pass


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


def _python_check(relative: str, body: bytes) -> None:
    """Refuse a Python file that cannot compile, before it reaches the disk.

    A reloaded module with a syntax error is caught by its area's rollback, but
    the bot core has nothing to roll back to once the process has restarted: the
    file would be live and the next boot would die before it could serve. Checking
    the bytes first turns that into an ordinary failed download.
    """
    if Path(relative).suffix != ".py":
        return
    try:
        compile(body, relative, "exec")
    except SyntaxError as exc:
        raise ValueError(f"{relative} has a syntax error: {exc.msg} (line {exc.lineno})") from exc


def _drop_bytecode(relative: str) -> None:
    """Forget the compiled copy of a file that is about to be replaced.

    ``importlib.invalidate_caches`` clears the finders' directory listings, not
    a ``.pyc`` whose recorded source stamp still matches the file on disk. A
    replaced module that arrives with the same size and an unchanged timestamp —
    a copy that keeps its mtime, or a filesystem with coarse ones — would then
    be imported from the previous build's bytecode until the process restarts,
    which is exactly the "the update only shows up after a restart" report. The
    source is what has to be compiled next, so the compiled copy goes.
    """
    _drop_bytecode_path(ROOT / relative)


def _drop_bytecode_path(path: Path) -> None:
    if path.suffix != ".py":
        return
    try:
        cached = Path(importlib.util.cache_from_source(str(path)))
    except (NotImplementedError, ValueError):
        return
    try:
        if cached.is_file():
            cached.unlink()
    except OSError:
        pass


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
            _drop_bytecode(relative)
            if change["status"] == "removed":
                if path.is_file():
                    path.unlink()
                    removed += 1
                continue
            body = _download(relative, change["sha"])
            _python_check(relative, body)
            _write(relative, body)
            written += 1
    except Exception:
        _restore_area(name, changes, run_id)
        raise
    return {"written": written, "removed": removed, "backup": str(_backup_path(run_id, ".").parent)}


#: Environment markers that describe *this* image, so a fresh child must start
#: without them: the inherited fds, and the ``NIKO_HANDOFF_*`` / supervisor
#: variables the predecessor set (stripped for a process that has not reloaded
#: the module that names them).
PROCESS_ENV_MARKERS = (
    "NIKO_RESTART_FD",
    "NIKO_HANDOFF_",
    "NIKO_SUPERVISOR_",
    "NIKO_SUPERVISED",
)
#: Set in the probe child so ``src/bot.py`` stops right after its imports.
PROBE_ENV = "NIKO_IMPORT_PROBE"
#: Module the restart runs from. Reloaded from disk before it is used.
HANDOFF_MODULE = "utils.runtime.handoff"


def _split_web() -> bool:
    """Whether the supervisor runs the dashboard as its own child.

    Under ``NIKO_SPLIT_WEB=1`` a webapp update has two halves: this process
    (where the updater runs) rebuilds its Flask app, and the dashboard child is
    restarted by the supervisor so it loads the new modules too.  The bot child
    is never restarted for a dashboard-only change.
    """
    return (os.environ.get("NIKO_SPLIT_WEB") or "").strip() == "1"


def _split_db() -> bool:
    """Whether the database runs in its own child.

    Database code (``src/database/``) and the ``src/db_child.py`` script that
    serves it are bot-core code, so a bot restart picks them up.  The database
    child imported those modules at its own boot, so it has to be restarted
    with the bot for the new translation layer to take effect.
    """
    return _split_web() and (os.environ.get("NIKO_SPLIT_DB") or "").strip() == "1"


def _set_package_attribute(name: str, module) -> None:
    """Re-attach a module to its parent package after :func:`_purge` dropped it."""
    parent_name, _, child = name.rpartition(".")
    parent = sys.modules.get(parent_name) if parent_name else None
    if parent is not None and module is not None:
        setattr(parent, child, module)


def _inplace_handoff():
    """The handoff module the restart will run, loaded from the file on disk.

    A process that has been up since before the in-place restart still holds the
    predecessor's ``utils.runtime.handoff`` in memory: its ``schedule`` takes a bot and
    hands the port to a successor, which is the arrangement that closes the
    dashboard. The file on disk is imported before anything is probed, so the
    restart runs the code the update is actually shipping, and a copy that still
    cannot restart in place is refused with something the owner can act on instead
    of an ``AttributeError``.
    """
    previous = sys.modules.get(HANDOFF_MODULE)
    source = getattr(previous, "__file__", None)
    if source:
        _drop_bytecode_path(Path(source))
    _purge([HANDOFF_MODULE])
    importlib.invalidate_caches()
    try:
        # ``import_module``, not ``from utils.runtime import handoff``: the package
        # attribute can still point at the copy that was in memory before the
        # purge, and reading it would silently keep the stale module.
        handoff = importlib.import_module(HANDOFF_MODULE)
    except Exception:
        if previous is not None:
            sys.modules[HANDOFF_MODULE] = previous
            _set_package_attribute(HANDOFF_MODULE, previous)
        raise
    if not getattr(handoff, "INHERITED_FD_ENV", None) or not callable(getattr(handoff, "adopt", None)):
        if previous is not None:
            sys.modules[HANDOFF_MODULE] = previous
            _set_package_attribute(HANDOFF_MODULE, previous)
        raise RuntimeError(
            "This process is still running the previous successor handoff, and "
            "utils/runtime/handoff.py on disk is that copy too. The bot core restarts in place "
            "only with the current handoff: apply the Utilities area first (ticking it "
            "together with the bot core in one run is fine), then retry."
        )
    return handoff


def _serving(api_server) -> bool:
    """Whether this process holds the dashboard's listening socket.

    ``serving()`` is the current API. A process that booted before it existed
    still has ``listening_socket_fd``, which is the same fact and what the restart
    actually needs.
    """
    check = getattr(api_server, "serving", None)
    if callable(check):
        return bool(check())
    try:
        fd = api_server.listening_socket_fd()
    except Exception:
        return False
    os.close(fd)
    return True


def _probe_bot() -> None:
    """Import the bot core the update just wrote, in a throwaway interpreter.

    The bot area is the one area without a fallback: it replaces the process
    image, so a startup chain that cannot import takes the dashboard's port with
    it. This runs ``src/bot.py`` in a child that stops right after its imports
    (see ``NIKO_IMPORT_PROBE`` there) and raises if it cannot get that far, which
    rolls the area back while the old process is still serving.

    The child never inherits this process's restart markers — ``NIKO_RESTART_FD``
    above all, or it would adopt the socket this process is answering on. They are
    matched by prefix rather than read from ``utils.runtime.handoff``: a process that has
    not reloaded that module yet still holds the predecessor's copy, which names
    its variables differently (``NIKO_HANDOFF_*``) and has no
    ``INHERITED_FD_ENV`` at all, and that staleness must not fail the update.
    """
    environment = {
        name: value
        for name, value in os.environ.items()
        if not name.startswith(PROCESS_ENV_MARKERS)
    }
    environment[PROBE_ENV] = "1"
    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "src" / "bot.py")],
            cwd=str(ROOT),
            env=environment,
            capture_output=True,
            text=True,
            timeout=90,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("The new bot core did not finish importing within 90 seconds.") from exc
    if result.returncode != 0:
        detail = [line for line in (result.stderr or result.stdout or "").strip().splitlines() if line.strip()]
        raise RuntimeError(f"The new bot core cannot import: {detail[-1] if detail else f'exit {result.returncode}'}")


def _restore_area(name: str, changes: list[dict], run_id: str) -> None:
    for change in changes:
        relative = change["path"]
        backup = _backup_path(run_id, relative)
        path = ROOT / relative
        try:
            # ``copy2`` keeps the backup's timestamp, which is exactly what makes
            # a stale ``.pyc`` look current: the restored module would then be
            # imported from the cancelled update's bytecode.
            _drop_bytecode(relative)
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
def _forget_package_attribute(name: str, module) -> None:
    """Drop the attribute a purged module leaves on its parent package.

    ``from utils import maintenance`` does not consult ``sys.modules``: it reads
    the ``maintenance`` attribute of the ``utils`` package and only imports the
    file when that attribute is missing. Dropping the module alone therefore
    left the attribute in place, so a rebuilt route kept the *old* module — which
    is how a pulled update to ``utils.maintenance`` could keep answering with
    the previous snapshot until the process was restarted.
    """
    parent_name, _, child = name.rpartition(".")
    if not parent_name or module is None:
        return
    parent = sys.modules.get(parent_name)
    if parent is not None and getattr(parent, child, None) is module:
        try:
            delattr(parent, child)
        except AttributeError:
            pass


def _purge(prefixes) -> list[str]:
    """Drop cached imports so the next import reads the file on disk."""
    dropped = []
    for name in list(sys.modules):
        if not isinstance(name, str):
            continue
        for prefix in prefixes:
            if name == prefix or name.startswith(prefix + "."):
                module = sys.modules.pop(name, None)
                _forget_package_attribute(name, module)
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


def _run(coroutine, timeout: float = 60):
    """Run one coroutine on the bot loop from this worker thread."""
    from .runtime import run_on_bot_loop

    return run_on_bot_loop(coroutine, timeout=timeout)


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


def _event_modules(files) -> list[str]:
    """``src/events/on_message.py`` → ``events.on_message``.

    Only the modules that sit directly in the package: ``bot.py`` imports those
    and calls them per event. ``events.startup`` is the oneshot startup chain and
    is applied by the bot core instead.
    """
    names = set()
    for relative in files or ():
        if not isinstance(relative, str):
            continue
        parts = Path(relative).parts
        if len(parts) == 3 and parts[:2] == ("src", "events") and parts[2].endswith(".py"):
            module = parts[2][:-3]
            if module != "__init__":
                names.add(f"events.{module}")
    return sorted(names)


#: The startup module that owns the schema. Applied live by re-running it.
SCHEMA_MODULE = "events.startup.database"

#: The startup module that exports the data writers. It is called from the ready
#: handler, not the bot core, so it can be re-imported live.
STARTUP_WRITERS_MODULE = "events.startup.writers"
STARTUP_WRITERS_FILE = "src/events/startup/writers.py"
#: ``banner`` reads ``VERSION`` from the writers at import time, so a writers
#: change has to re-import it too rather than leave the old version cached.
STARTUP_WRITER_DEPENDENTS = ("events.startup.banner",)
_STARTUP_WRITER_MODULES = (STARTUP_WRITERS_MODULE, *STARTUP_WRITER_DEPENDENTS)


def _module_source(name: str) -> Path:
    return ROOT / "src" / Path(*name.split(".")).with_suffix(".py")


def _import_schema_module():
    """Re-import ``events.startup.database``, leaving the old module on failure."""
    previous = sys.modules.get(SCHEMA_MODULE)
    source = getattr(previous, "__file__", None)
    if source:
        _drop_bytecode_path(Path(source))
    _purge([SCHEMA_MODULE])
    try:
        module = importlib.import_module(SCHEMA_MODULE)
        init = getattr(module, "init_database", None)
        if not callable(init):
            raise RuntimeError("The new database module has no init_database().")
    except Exception:
        # The process must keep the module it was running, so the update can roll
        # the file back onto working code.
        if previous is not None:
            sys.modules[SCHEMA_MODULE] = previous
        raise
    importlib.invalidate_caches()
    # ``events.startup`` re-exports it: refresh that binding too, or a ready-time
    # caller would still hold the old function.
    package = sys.modules.get("events.startup")
    if package is not None:
        package.init_database = init
    return module, init


def reload_database(bot) -> dict:
    """Re-import the schema module and run its setup against the live pool.

    ``init_database`` is written to be run again: tables are created with ``IF
    NOT EXISTS``, column migrations add only what is missing, and a pool is only
    opened when there is none. Importing the new file and calling it is therefore
    what makes a new table, a new column or a backfill live — the same function a
    restart would run, without the restart. The music and error-report databases
    are untouched because their own ``init`` returns early once ready.

    The rest of the startup chain is still bot-core: it has no live entry point,
    so reloading it would report an apply that changed nothing.
    """
    if bot is None:
        raise RuntimeError("The bot is not running.")
    if not _module_source(SCHEMA_MODULE).exists():
        # A build that deleted it would break the next boot (bot.py imports it).
        raise RuntimeError(
            "src/events/startup/database.py was removed on beta; this deployment still imports it."
        )
    _module, init = _import_schema_module()
    # Migrations touch every guild's rows, so this is given more room than a
    # command-path call: a big database can take longer than a minute.
    _run(init(bot), timeout=180)
    return {}


def _import_startup_writers() -> dict:
    """Re-import the writers and their dependants, keeping the old copy on failure."""
    previous = {name: sys.modules.get(name) for name in _STARTUP_WRITER_MODULES}
    package = sys.modules.get("events.startup")
    package_before = dict(vars(package)) if package is not None else {}
    for module in previous.values():
        source = getattr(module, "__file__", None)
        if source:
            _drop_bytecode_path(Path(source))
    _purge(_STARTUP_WRITER_MODULES)
    fresh = {}
    try:
        for name in _STARTUP_WRITER_MODULES:
            fresh[name] = importlib.import_module(name)
        # ``on_ready`` imports through the package, not the module: refresh the
        # re-exports before it is re-imported below.
        if package is not None:
            for module in fresh.values():
                for attribute, value in vars(module).items():
                    if not attribute.startswith("_") and attribute in package_before:
                        setattr(package, attribute, value)
    except Exception:
        for name, module in previous.items():
            if module is not None:
                sys.modules[name] = module
        if package is not None:
            for attribute, value in package_before.items():
                if not attribute.startswith("__"):
                    setattr(package, attribute, value)
        raise
    importlib.invalidate_caches()
    return fresh


def _run_startup_writers(bot, module) -> list[str]:
    """Run the re-imported writers, keeping the process uptime marker intact."""
    stats_path = ROOT / "data" / "bot_stats.json"
    try:
        before = json.loads(stats_path.read_text(encoding="utf-8")).get("uptime_since")
    except Exception:
        before = None
    ran = []
    for name in ("write_commands", "write_bot_stats"):
        writer = getattr(module, name, None)
        if not callable(writer):
            continue
        try:
            writer(bot)
        except Exception:
            # The writers log their own failures; a write must not undo an
            # otherwise successful module reload.
            continue
        ran.append(name)
    # ``write_bot_stats`` stamps a fresh uptime because it normally runs during
    # startup. This process did not restart, so a live writers update must keep
    # the uptime the running bot has been reporting.
    if before:
        try:
            payload = json.loads(stats_path.read_text(encoding="utf-8"))
            if payload.get("uptime_since") != before:
                payload["uptime_since"] = before
                stats_path.write_text(json.dumps(payload), encoding="utf-8")
        except Exception:
            pass
    return ran


def reload_startup_writers(bot=None, files=None, run_writers=True) -> dict:
    """Apply a writers change without restarting the process or reloading cogs.

    ``events.on_ready`` imports the writers through ``events.startup``. Purging
    the writers, refreshing that package's exports and re-importing ``on_ready``
    is enough for the next ready event to run the new code; running the writers
    once here also refreshes ``data/bot_stats.json`` and ``data/commands.json``
    immediately, so an update does not sit on disk until the next restart.
    """
    if files is not None and not any(
        str(path).replace("\\", "/") == STARTUP_WRITERS_FILE for path in files
    ):
        return {"reloaded": [], "rebound": [], "failed": []}
    if not _module_source(STARTUP_WRITERS_MODULE).exists():
        return {
            "reloaded": [],
            "rebound": [],
            "failed": [
                f"{STARTUP_WRITERS_MODULE}: the file was removed on beta; the loaded module stays until the next restart"
            ],
        }
    try:
        fresh = _import_startup_writers()
    except Exception as exc:
        return {
            "reloaded": [],
            "rebound": [],
            "failed": [f"{STARTUP_WRITERS_MODULE}: {type(exc).__name__}: {exc}"],
        }

    ready = reload_events(["src/events/on_ready.py"])
    summary = {
        "reloaded": list(fresh),
        "rebound": list(ready.get("rebound") or []),
        "failed": list(ready.get("failed") or []),
    }
    if run_writers and bot is not None and not summary["failed"]:
        summary["ran"] = _run_startup_writers(bot, fresh.get(STARTUP_WRITERS_MODULE))
    return summary


def _rebind_event_handlers(previous: dict, fresh: dict) -> list[str]:
    """Point the running callbacks at the functions the new files define.

    ``bot.py`` registers its Discord callbacks as closures over module-level
    names, and the closure reads that name from ``bot.py``'s globals on every
    dispatch. Re-importing ``events.on_message`` therefore only takes effect when
    the global it calls is replaced — which is what this does, without touching
    the gateway, the cogs or the dashboard. Any callable a host module imported
    from a reloaded event module is refreshed, not just the two entry points, so
    a new ``events/on_*.py`` helper is covered by the same rule.
    """
    owners = {}
    for module in previous.values():
        if module is None:
            continue
        for attribute, value in vars(module).items():
            if callable(value) and getattr(value, "__module__", None) == module.__name__:
                owners[id(value)] = (module.__name__, attribute)
    if not owners:
        return []
    rebound = []
    # ``python src/bot.py`` runs the entry point as ``__main__``; the module name
    # is used by tests and embedders that import it.
    for host_name in ("__main__", "bot"):
        host = sys.modules.get(host_name)
        if host is None:
            continue
        for attribute, value in list(vars(host).items()):
            owner = owners.get(id(value))
            if owner is None:
                continue
            module_name, source = owner
            module = fresh.get(module_name)
            if module is None:
                continue
            replacement = getattr(module, source, None)
            if replacement is None or replacement is value:
                continue
            setattr(host, attribute, replacement)
            rebound.append(f"{module_name}.{source}")
    return rebound


def reload_events(files=None) -> dict:
    """Re-import the gateway event modules and rebind the callbacks onto them.

    ``files`` is the area's changed paths, or ``None`` to re-import every event
    module this process already holds (the rollback path). The modules are purged
    only, never the process: an in-flight handler keeps its own frame and module
    dictionary, and the next event is dispatched through the rebound name.

    Module-level state in an event module starts again at its initial value
    (``on_message``'s per-channel locks and AI semaphore), which is why those
    values are limits rather than counters.
    """
    if files is None:
        names = sorted(
            name
            for name in sys.modules
            if isinstance(name, str)
            and name.startswith("events.")
            and not name.startswith("events.startup")
        )
    else:
        names = _event_modules(files)
    if not names:
        return {"reloaded": [], "rebound": [], "failed": []}

    # A file beta removed cannot be imported, and a module ``bot.py`` imports at
    # boot cannot be unloaded: keep the loaded handler and say why. (This is the
    # pathological case; an area beta simply does not publish is handled in
    # :func:`plan`, which never offers the files as deletions.)
    removed = [name for name in names if not _module_source(name).exists()]
    failed = [f"{name}: the file was removed on beta; the loaded module stays until the next restart" for name in removed]
    names = [name for name in names if name not in removed]
    if not names:
        return {"reloaded": [], "rebound": [], "failed": failed}

    previous = {name: sys.modules.get(name) for name in names}
    # A rewritten event file can arrive with the same size and timestamp as the
    # one it replaces, and then the import below would run the previous build's
    # compiled copy. Staging already drops it; this keeps the reload correct on
    # its own and covers the rollback path, which restores files without staging.
    for module in previous.values():
        source = getattr(module, "__file__", None)
        if source:
            _drop_bytecode_path(Path(source))
    _purge(names)
    fresh, reloaded = {}, []
    for name in names:
        try:
            fresh[name] = importlib.import_module(name)
            reloaded.append(name)
        except Exception as exc:
            failed.append(f"{name}: {type(exc).__name__}: {exc}")
            # Keep running the code this process already has: a file that does
            # not import must not leave the gateway without its handler.
            old = previous.get(name)
            if old is not None:
                sys.modules[name] = old
    importlib.invalidate_caches()
    return {"reloaded": reloaded, "rebound": _rebind_event_handlers(previous, fresh), "failed": failed}


#: What the feed owns rather than defines: carried across a reload so an update
#: never blanks the site or drops the bot back to its own files.
_FEED_STATE = ("_lock", "_beta", "_local", "_catalogues", "_bot_files", "_bot", "_loop", "_settings")


def reload_locale_feed() -> bool:
    """Re-read ``webapp.locale_feed`` from disk, keeping its caches.

    The feed is kept out of the purge in :func:`reload_webapp` so the site does
    not fall back to its own files in the middle of an update. Keeping it there
    pins its *code* as well, and a rebuilt route then calls functions the running
    module does not have — which is how a new ``coverage_rows`` argument once
    500'd ``/api/owner/locales`` on a process that had just updated itself.

    Reloading in place fixes that without losing the manifest, the fetched
    catalogues or the bot overlay: ``importlib.reload`` re-executes the file in
    this module's own namespace (so the poller thread, whose function globals are
    that namespace, runs the new code on its next pass) and the state below is
    put back afterwards.
    """
    module = sys.modules.get("webapp.locale_feed")
    if module is None:
        return False
    carried = {name: getattr(module, name) for name in _FEED_STATE if hasattr(module, name)}
    try:
        importlib.reload(module)
    except Exception:
        # A broken feed file must not leave a half-executed module behind: drop
        # it and let the rebuild import it from disk like any other module.
        sys.modules.pop("webapp.locale_feed", None)
        return False
    for name, value in carried.items():
        setattr(module, name, value)
    importlib.invalidate_caches()
    return True


def _webapp_modules() -> dict:
    """The ``webapp.*`` modules this process is running right now."""
    return {
        name: module
        for name, module in list(sys.modules.items())
        if isinstance(name, str) and (name == "webapp" or name.startswith("webapp."))
    }


def _restore_modules(snapshot: dict) -> None:
    """Put a module snapshot back, dropping whatever the rebuild left behind."""
    for name in list(sys.modules):
        if isinstance(name, str) and (name == "webapp" or name.startswith("webapp.")):
            if name not in snapshot:
                sys.modules.pop(name, None)
    sys.modules.update(snapshot)
    importlib.invalidate_caches()


def reload_webapp(bot) -> dict:
    """Rebuild the Flask application and swap it into the running server.

    Werkzeug reads ``server.app`` per request, so replacing it changes every
    route at once while the listening socket, its thread and every open
    connection stay exactly where they are. This module is deliberately kept
    alive across the purge: it is the code executing this call.

    The rebuild is transactional. Dropping ``webapp.*`` before importing the new
    copy is what makes the next import read the files on disk, but it also means
    a new file that fails to import leaves the process with no modules to serve
    from: the app object the server still points at keeps working, while any
    request that imports a route module lazily re-executes the broken file and
    answers 500 — the site is down until a restart even though the update was
    rolled back. So the modules the server is using are snapshotted first and put
    back when the rebuild raises, which is what keeps a bad API update from
    taking the API down at all.
    """
    # Kept alive across the purge: this module is executing the call, and the
    # locale feed owns the caches the rebuilt routes read on the first request.
    keep = {__name__, "webapp.locale_feed"}
    previous = _webapp_modules()
    for name in list(previous):
        if name in keep:
            continue
        sys.modules.pop(name, None)
    importlib.invalidate_caches()
    reload_locale_feed()

    serving = None
    try:
        fresh = importlib.import_module("webapp")
        fresh.configure_bot(bot)
        import api_server

        # What is answering right now, so a failed swap can put it back exactly
        # as it was instead of leaving the server on a half-built app.
        serving = api_server._server.app if api_server._server is not None else None
        api_server.replace_app(fresh.app)
        if api_server._server.app is not fresh.app:
            raise RuntimeError("The rebuilt dashboard was not installed on the running server.")
        # Installing it is half the claim; a route answering from the new modules
        # is the other half. The app can import cleanly and still fail a request,
        # and reporting the area as applied when it does is how an update ends up
        # looking like it needs a restart.
        probe = fresh.app.test_client().get("/api/health")
        if probe.status_code != 200:
            raise RuntimeError(f"The rebuilt dashboard answered {probe.status_code} for /api/health.")
    except Exception:
        # Either nothing was swapped, or it was swapped and cannot answer: in
        # both cases the server goes back to the app and the modules it was
        # serving before, and the caller rolls the files back. The API never
        # stops answering during any of this.
        if serving is not None:
            try:
                import api_server

                api_server.replace_app(serving)
            except Exception:
                pass
        _restore_modules(previous)
        raise
    return {"swapped": True, "routes": len(fresh.app.url_map._rules)}


#: What the updater owns rather than defines: a reload must not forget a run in
#: flight, the lock that guards it, or the beta manifest it just read.
_UPDATER_STATE = ("_lock", "_running", "_manifest_cache")


def reload_updates_module() -> bool:
    """Re-read this module from disk, so an update to the updater lands too.

    ``webapp`` is rebuilt from the files an update just wrote, but the module
    running the rebuild cannot be re-imported with it: it is the code executing
    the call. Reloading it in place afterwards is what stops a change to this
    file — or to anything else the API routes import from it — from sitting on
    disk until the next restart. Callers must do it as the last thing they do,
    because the frame in flight keeps executing its own code and its globals are
    this module's dictionary, which the reload replaces.
    """
    module = sys.modules.get(__name__)
    if module is None:
        return False
    carried = {name: getattr(module, name) for name in _UPDATER_STATE if hasattr(module, name)}
    try:
        importlib.reload(module)
    except Exception:
        # A broken updater must not take the update path down with it: the run
        # already finished and was recorded, and the next restart re-reads it.
        return False
    for name, value in carried.items():
        setattr(module, name, value)
    importlib.invalidate_caches()
    return True


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
    """Stage and apply the selected areas, or refuse if one is already running."""
    # Keep the lock in a local: a webapp/utils update reloads this module at the
    # end of the run, so the module-level name would point at a new lock by the
    # time the finally block releases it.
    gate = _apply_gate
    if not gate.acquire(blocking=False):
        return {
            "ok": False,
            "configured": configured(),
            "error": "An update is already being applied.",
            "areas": {},
            "total_changed": 0,
            "last": last_run(),
        }
    try:
        return _apply_locked(areas, bot)
    finally:
        gate.release()


def _apply_locked(areas, bot=None) -> dict:
    """Stage and apply the selected areas, then report what each one did."""
    chosen = _selected(areas)
    # A new shared module is a precondition for the areas that import it, not a
    # choice: applying a route that imports ``config.version`` without writing
    # ``config/version.py`` is precisely the ModuleNotFoundError this prevents. So
    # a pending support module rides along with any run, before anything reloads.
    if chosen and "support" not in chosen:
        pending = (plan(["support"])["areas"].get("support") or {}).get("changed")
        if pending:
            chosen = ["support", *chosen]
    current = plan(chosen)
    if not current["ok"]:
        return current
    if _running["active"]:
        return {**current, "ok": False, "error": "An update is already being applied."}

    _running.update({
        "active": True,
        "areas": list(chosen),
        "started_at": int(time.time()),
        "area": chosen[0] if chosen else None,
        "index": 0,
        "total": len(chosen),
        "done": [],
        "phase": "starting",
    })
    run_id = time.strftime("%Y%m%d-%H%M%S")
    started = int(time.time())
    results: dict[str, dict] = {}
    handoff_needed = False
    supervised_restart_needed = False
    # A split deployment serves the dashboard from its own child, so new webapp
    # code needs that child replaced.  The bot keeps running.
    web_restart_needed = False

    try:
        for index, name in enumerate(chosen):
            _set_progress(area=name, index=index, phase="pulling")
            changes = (current["areas"].get(name) or {}).get("changed", 0)
            if not changes:
                results[name] = {"changed": 0, "strategy": "nothing to do"}
                _running["done"].append(name)
                _set_progress(phase="skipped")
                continue
            try:
                staged = _stage_area(name, current["areas"][name]["files"], run_id)
            except Exception as exc:
                results[name] = {"ok": False, "error": f"{type(exc).__name__}: {exc}", "rolled_back": True}
                _set_progress(phase="failed")
                _record({"id": run_id, "started_at": started, "finished_at": int(time.time()), "areas": results})
                return {**current, "ok": False, "run": run_id, "areas": results, "last": last_run()}

            _set_progress(phase="applying")
            outcome = {"ok": True, "changed": changes, **staged}
            try:
                if name == "support":
                    # Written before the areas below reload on top of them. New
                    # modules are not imported yet; ``links.py`` is safe to pull
                    # because every deployment uses the production URL.
                    replaced = any(
                        _replaceable(name, change["path"])
                        for change in current["areas"][name]["files"]
                    )
                    outcome["strategy"] = (
                        "updated shared modules" if replaced
                        else "added new shared modules"
                    )
                elif name == "cogs":
                    if bot is None:
                        raise RuntimeError("The bot is not running.")
                    names = _extensions_for([change["path"] for change in current["areas"][name]["files"]])
                    outcome.update(_reload_summary(reload_cogs(bot, names)))
                    outcome["strategy"] = "reloaded extensions"
                elif name == "utils":
                    if bot is None:
                        raise RuntimeError("The bot is not running.")
                    # Each entry is a change record, not a path: the prefix
                    # helper reads ``path`` off it like the extension one does.
                    prefixes = _utils_prefixes(
                        [change["path"] for change in current["areas"][name]["files"]]
                    )
                    outcome["purged"] = _purge(prefixes)
                    outcome.update(_reload_summary(reload_extensions(bot)))
                    outcome.update({"dashboard": reload_webapp(bot)})
                    outcome["strategy"] = "reloaded modules, extensions and the dashboard"
                elif name == "webapp":
                    # Rebuilding the Flask app needs the gateway only for the
                    # routes that read it, so an API update is not held back by
                    # a bot that is still connecting — or absent entirely.
                    outcome["dashboard"] = reload_webapp(bot)
                    if _split_web() and supervisor_control.is_supervised():
                        web_restart_needed = True
                        outcome["strategy"] = "rebuilt the dashboard app; the dashboard child will restart"
                    else:
                        outcome["strategy"] = "rebuilt the dashboard app"
                elif name == "database":
                    # Import the new schema module and run it against the live
                    # pool: tables are created with IF NOT EXISTS and migrations
                    # only add what is missing, so re-running is how a change
                    # takes effect without a restart.
                    outcome.update(reload_database(bot))
                    outcome["strategy"] = "re-ran the database schema setup"
                elif name == "events":
                    outcome.update(_reload_summary(reload_events(
                        [change["path"] for change in current["areas"][name]["files"]]
                    )))
                    outcome["strategy"] = "re-imported the gateway event handlers"
                elif name == "startup":
                    # The startup package imports this file at boot, so a beta
                    # that deleted it cannot be applied: roll the removal back
                    # rather than leave a deployment that fails its next start.
                    if any(change["status"] == "removed" for change in current["areas"][name]["files"]):
                        raise RuntimeError(
                            "src/events/startup/writers.py was removed on beta; this deployment still imports it."
                        )
                    outcome.update(reload_startup_writers(
                        bot, [change["path"] for change in current["areas"][name]["files"]]
                    ))
                    outcome["strategy"] = "re-imported the startup writers"
                elif name == "website":
                    outcome["strategy"] = "served from disk on the next request"
                elif name == "bot":
                    # The files are in place; prove they import before the old
                    # process is stopped.  A supervised child must not run the
                    # in-place handoff: the supervisor owns the public socket
                    # and is the only component allowed to replace this child.
                    _probe_bot()
                    import api_server

                    if not _serving(api_server):
                        # Restarting onto a process that is not serving would
                        # trade the old bot for a site with no socket: refuse
                        # instead, so the area rolls back and says why.
                        raise RuntimeError("The dashboard is not serving; a bot-core restart would leave the site down.")
                    if supervisor_control.is_supervised():
                        if not supervisor_control.socket_path():
                            raise RuntimeError(
                                "This is a supervised child but no supervisor control socket is configured."
                            )
                        outcome["strategy"] = "requesting a supervised restart"
                        supervised_restart_needed = True
                    else:
                        # Resolve the restart code from disk for the direct-run
                        # fallback; this process may hold the predecessor's.
                        _inplace_handoff()
                        outcome["strategy"] = "restarting this process in place"
                        handoff_needed = True
            except Exception as exc:
                _restore_area(name, current["areas"][name]["files"], run_id)
                outcome = {"ok": False, "error": f"{type(exc).__name__}: {exc}", "rolled_back": True}
                _rebuild_after_rollback(name, bot)
                _set_progress(phase="failed")
            results[name] = outcome
            _running["done"].append(name)
            _set_progress(phase="applied")
    finally:
        _progress_reset()

    run = {
        "id": run_id,
        "started_at": started,
        "finished_at": int(time.time()),
        "areas": results,
        "handoff": handoff_needed,
        "supervised_restart": supervised_restart_needed,
    }
    _record(run)

    if handoff_needed:
        from utils.runtime import handoff

        handoff.schedule()
    elif supervised_restart_needed:
        # Ask after the run is persisted.  The supervisor answers immediately
        # and stops this child after a short delay, leaving time for this HTTP
        # response to flush; a rejection is rolled back while the old process is
        # still healthy.
        try:
            # The supervisor needs to know what this restart replaced: if the
            # replacement never becomes ready, it restores these files and
            # boots the last-good release instead of restarting into a crash.
            _mark_pending(run_id, "bot", current["areas"]["bot"]["files"])
            supervisor_control.request_restart(
                reason="bot update applied",
                delay=float(os.environ.get("NIKO_SUPERVISED_RESTART_DELAY", "2.0") or 2.0),
                # With split children this must name the bot: restarting the
                # dashboard as well would be the interference this split exists
                # to remove.  The database child is restarted with it because
                # it holds the freshly updated database modules.
                child=(
                    ["bot", "db"]
                    if _split_db()
                    else ("bot" if _split_web() else None)
                ),
            )
        except Exception as exc:
            _clear_pending()
            _restore_area("bot", current["areas"]["bot"]["files"], run_id)
            _rebuild_after_rollback("bot", bot)
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
            _record(run)

    if web_restart_needed and not handoff_needed:
        try:
            supervisor_control.request_restart(
                reason="webapp update applied",
                delay=float(os.environ.get("NIKO_SUPERVISED_RESTART_DELAY", "2.0") or 2.0),
                child="web",
            )
        except Exception as exc:
            # The new code is on disk and the bot child already reloaded it;
            # only the dashboard child is still serving the previous modules.
            # Say so rather than claiming the update fully applied.
            results["webapp"].update({
                "ok": False,
                "error": f"the dashboard child was not restarted: {type(exc).__name__}: {exc}",
            })

    result = {**current, "ok": all(item.get("ok", True) for item in results.values()), "run": run_id, "areas": results, "last": last_run()}
    # Last, and only when this run replaced API code: the rebuilt modules read
    # the new files, and this module — pinned while it was executing — now does
    # too. Nothing below this point may use a module-level name, because the
    # reload swaps this module's dictionary under the frame returning the result.
    if any(name in results for name in ("utils", "webapp")):
        reload_updates_module()
    return result


def _reload_summary(result: dict) -> dict:
    summary = {}
    if result.get("reloaded"):
        summary["reloaded"] = result["reloaded"]
    if result.get("rebound"):
        summary["rebound"] = result["rebound"]
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
        if not isinstance(relative, str):
            continue
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
        elif name == "events":
            # Re-import from the files the rollback just restored and put the
            # callbacks back on the code they were running.
            reload_events(None)
        elif name == "startup":
            # Same for the ready handler: put the writers and its imports back
            # on the restored files. The data files were already written; the
            # next ready or the next apply refreshes them.
            reload_startup_writers(None, run_writers=False)
        elif name == "database":
            # The schema work already ran and is idempotent; put the module back
            # on the code the files were restored to.
            _import_schema_module()
        elif name == "cogs" and bot is not None:
            for extension in list(getattr(bot, "extensions", {}) or {}):
                if extension.startswith("cogs."):
                    _purge([extension])
                    _run(bot.reload_extension(extension))
    except Exception:
        pass
