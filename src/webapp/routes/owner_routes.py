"""Owner-only controls: the beta locale sync, the update page, and the handoff door.

Three kinds of endpoint live here, and only one of them is for the browser:

* ``/api/owner/...`` — signed-in owner only. What the staff workspace's Locales
  and Updates tabs read and trigger.
* ``/api/updates/...`` — the same instance acting as beta, serving its source
  files to a production instance that is pulling an update. Guarded by
  ``BETA_UPDATE_TOKEN``; with no token configured these answer 404, so an
  instance without the feature is indistinguishable from one without the route.
* ``/api/handoff/ready`` — called by a successor process to tell this one it is
  live. Localhost and a one-run token only.
"""

import hmac
import logging
import threading
import time

from flask import jsonify, request, send_from_directory

from utils import handoff

from .. import locale_feed, updates
from .. import server as _server

app = _server.app
require_auth = _server.require_auth
require_csrf = _server.require_csrf
_current_staff_role = _server._current_staff_role
_discord_bot = None
log = logging.getLogger(__name__)

#: Beta hashes a few thousand files to answer a manifest; reuse it briefly.
_source_cache: dict = {"at": 0.0, "document": None}
_source_lock = threading.Lock()


# ──────────────────────────────────────────────────────────────────────────────
# Locales
# ──────────────────────────────────────────────────────────────────────────────
def _locale_rows(entries: dict) -> list[dict]:
    """One row per page or bot catalogue, with the keys each language covers."""
    rows = []
    for name, entry in sorted(entries.items()):
        languages = entry.get("langs") or {}
        rows.append({
            "page": name,
            "keys": entry.get("keys", 0),
            "languages": {code: info.get("translated", 0) for code, info in languages.items()},
        })
    return rows


def _locale_payload() -> dict:
    document = locale_feed.manifest()
    pages = _locale_rows(document["pages"])
    # The bot keeps its wording in each cog's own ``locales`` folder, so it has
    # its own catalogue list. The page shows the two side by side because a
    # translation pass usually touches one and then the other.
    bot = _locale_rows(document.get("bot_pages") or {})
    return {
        "configured": bool(locale_feed.BETA_INSTANCE_URL),
        "origin": locale_feed.BETA_INSTANCE_URL or None,
        "source": document.get("source"),
        "generated_at": document.get("generated_at"),
        "languages": document.get("languages", []),
        "coverage": locale_feed.coverage_rows(document),
        "pages": pages,
        "total_keys": sum(entry.get("keys", 0) for entry in document["pages"].values()),
        "bot": bot,
        "bot_total_keys": sum(entry.get("keys", 0) for entry in (document.get("bot_pages") or {}).values()),
        "bot_sync": locale_feed.bot_sync_state(),
    }


def _require_owner():
    if _current_staff_role() != "owner":
        return jsonify({"error": "Only the bot owner can use this page."}), 403
    if _discord_bot is None:
        return jsonify({"error": "The Discord bot is not available."}), 503
    return None


@app.route("/api/owner/locales")
@require_auth
def api_owner_locales():
    """Which languages the live site can render, and where they came from."""
    error = _require_owner()
    if error:
        return error
    return jsonify(_locale_payload())


@app.route("/api/owner/locales/sync", methods=["POST"])
@require_auth
@require_csrf
def api_owner_locales_sync():
    """Read beta's catalogues now instead of waiting for the next poll."""
    error = _require_owner()
    if error:
        return error
    locale_feed.sync()
    payload = _locale_payload()
    payload["synced_at"] = int(time.time())
    return jsonify(payload)


# ──────────────────────────────────────────────────────────────────────────────
# Updates (owner side)
# ──────────────────────────────────────────────────────────────────────────────
@app.route("/api/owner/updates")
@require_auth
def api_owner_updates():
    """What beta has that this deployment does not, area by area."""
    error = _require_owner()
    if error:
        return error
    payload = updates.plan()
    payload["handoff"] = handoff.last()
    payload["token_set"] = bool(updates.token())
    return jsonify(payload)


@app.route("/api/owner/updates/progress")
@require_auth
def api_owner_updates_progress():
    """Where the update in flight has got to, polled by the page's live bar."""
    error = _require_owner()
    if error:
        return error
    return jsonify(updates.progress())


@app.route("/api/owner/updates/apply", methods=["POST"])
@require_auth
@require_csrf
def api_owner_updates_apply():
    """Stage and apply the selected areas, reloading only what changed."""
    error = _require_owner()
    if error:
        return error
    body = request.get_json(silent=True) or {}
    areas = body.get("areas")
    if not isinstance(areas, list) or not areas:
        return jsonify({"error": "Select at least one area to update."}), 400
    known = set(updates.AREA_ORDER)
    unknown = [name for name in areas if name not in known]
    if unknown:
        return jsonify({"error": f"Unknown areas: {', '.join(unknown)}"}), 400
    result = updates.apply(areas, _discord_bot)
    result["handoff"] = handoff.last()
    return jsonify(result), (200 if result.get("ok") else 409)


# ──────────────────────────────────────────────────────────────────────────────
# Updates (beta side)
# ──────────────────────────────────────────────────────────────────────────────
def _token_ok() -> bool:
    expected = updates.token()
    if not expected:
        return False
    supplied = request.headers.get("X-Update-Token", "")
    return hmac.compare_digest(supplied, expected)


def _source_manifest() -> dict:
    now = time.monotonic()
    with _source_lock:
        cached = _source_cache["document"]
        if cached and now - _source_cache["at"] < 20:
            return cached
    areas = {}
    for name in updates.AREA_ORDER:
        files = {}
        for relative in updates.area_files(name):
            path = updates.ROOT / relative
            try:
                files[relative] = {"sha": updates.file_sha(path), "size": path.stat().st_size}
            except OSError:
                continue
        areas[name] = {"files": files}
    document = {"generated_at": int(time.time()), "areas": areas}
    with _source_lock:
        _source_cache.update({"document": document, "at": now})
    return document


@app.route("/api/updates/manifest.json")
def api_updates_manifest():
    """This instance's updatable files, for a production instance pulling them."""
    if not _token_ok():
        return jsonify({"error": "Not found"}), 404
    return jsonify(_source_manifest())


@app.route("/api/updates/file")
def api_updates_file():
    """One file's bytes, inside the areas an update may touch."""
    if not _token_ok():
        return jsonify({"error": "Not found"}), 404
    relative = request.args.get("path", "")
    if updates.area_for_path(relative) is None:
        return jsonify({"error": "Not an updatable path."}), 400
    target = updates.ROOT / relative
    if not target.is_file():
        return jsonify({"error": "No such file."}), 404
    if target.suffix in updates.SKIPPED_SUFFIXES:
        return jsonify({"error": "Not an updatable path."}), 400
    response = send_from_directory(str(updates.ROOT), relative)
    response.headers["Cache-Control"] = "no-store"
    return response


# ──────────────────────────────────────────────────────────────────────────────
# Handoff
# ──────────────────────────────────────────────────────────────────────────────
@app.route("/api/handoff/ready", methods=["POST"])
def api_handoff_ready():
    """A successor says it is live. The predecessor lets go and exits."""
    if handoff.is_candidate():
        # The successor shares the listening socket, so its own app can receive
        # this request; it is the predecessor that has to act on it.
        return jsonify({"handoff": False, "role": "candidate"})
    supplied = request.headers.get("X-Handoff-Token", "")
    expected = handoff.token()
    if not expected or not hmac.compare_digest(supplied, expected):
        return jsonify({"error": "Forbidden"}), 403
    if request.remote_addr not in {"127.0.0.1", "::1"}:
        return jsonify({"error": "Forbidden"}), 403
    threading.Thread(target=handoff.complete, args=(_discord_bot,), name="niko-retire", daemon=True).start()
    return jsonify({"handoff": True})
