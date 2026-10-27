"""Owner-only API for the staff broadcast studio.

The Discord ``.broadcast`` command used to compose announcements in a channel.
The composer now lives in the staff workspace:

* drafts and their images are stored in the database;
* images are uploaded here and delivered as real Discord attachments;
* sending and editing run on the bot loop and report their progress through the
  stored counters the dashboard polls;
* editing a delivered broadcast updates every recorded copy in the background.
"""

import base64
import logging
import os
import re
import time
import uuid

from flask import jsonify, request, session

from .. import server as _server

app = _server.app
require_auth = _server.require_auth
require_csrf = _server.require_csrf
run_on_bot_loop = _server.run_on_bot_loop
schedule_on_bot_loop = _server.schedule_on_bot_loop
_current_staff_role = _server._current_staff_role
_discord_bot = None
log = logging.getLogger(__name__)

MAX_TITLE = 160
MAX_BODY = 3800
MAX_FOOTER = 120
MAX_MEDIA_ITEMS = 10
MAX_MEDIA_BYTES = 8 * 1024 * 1024
# Discord caps the combined attachments on one message; staying below it here
# means a large gallery never fails for every guild at delivery time.
MAX_TOTAL_BYTES = 20 * 1024 * 1024
DEFAULT_ACCENT = "C8A882"
DEFAULT_FOOTER = "Official Niko staff announcement"

_IMAGE_TYPES = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
}
_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


def _require_owner():
    if _current_staff_role() != "owner":
        return jsonify({"error": "Broadcasts are restricted to the bot owner."}), 403
    if _discord_bot is None or not getattr(_discord_bot, "cxn", None):
        return jsonify({"error": "The Discord bot is not available."}), 503
    return None


def _accent(value) -> str:
    raw = str(value or "").strip().lstrip("#").upper()
    if len(raw) == 6 and all(character in "0123456789ABCDEF" for character in raw):
        return raw
    return DEFAULT_ACCENT


def _detect_image_type(raw: bytes, reported: str) -> str | None:
    """Trust the bytes when a browser sends a generic content type."""
    reported = (reported or "").split(";")[0].strip().lower()
    if reported in _IMAGE_TYPES:
        return reported
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if raw.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if raw.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    return None


def _media_filename(original: str, content_type: str) -> str:
    stem = os.path.splitext(os.path.basename(original or ""))[0]
    stem = _SAFE_NAME.sub("-", stem).strip("-._")[:40] or "broadcast"
    return f"{stem}-{uuid.uuid4().hex[:8]}.{_IMAGE_TYPES[content_type]}"


def _media_url(broadcast_id: str, media_id: str) -> str:
    return f"/api/staff/broadcasts/{broadcast_id}/media/{media_id}"


def _serialise(row, media) -> dict:
    """Turn a stored broadcast into the JSON the studio reads.

    Every field uses ``.get``: the MongoDB backend stores only the columns a
    statement wrote, so the counters and ``last_error`` that SQL defaults fill
    in on SQLite are simply absent there. Reading them positionally raised a
    ``KeyError`` that the list route reported as "Broadcasts could not be
    loaded.", which broke the whole tab on production.
    """
    broadcast_id = str(row["broadcast_id"])
    return {
        "id": broadcast_id,
        "title": row.get("title") or "",
        "body": row.get("body") or "",
        "accent": row.get("accent") or DEFAULT_ACCENT,
        "footer": row.get("footer") or "",
        "status": row.get("status") or "draft",
        "created_by": str(row.get("created_by")),
        "created_at": float(row.get("created_at") or 0),
        "updated_at": float(row.get("updated_at") or 0),
        "target_count": int(row.get("target_count") or 0),
        "sent_count": int(row.get("sent_count") or 0),
        "failed_count": int(row.get("failed_count") or 0),
        "skipped_count": int(row.get("skipped_count") or 0),
        "edited_count": int(row.get("edited_count") or 0),
        "last_error": row.get("last_error"),
        "media": [
            {
                "id": str(item["media_id"]),
                "filename": item.get("filename"),
                "content_type": item.get("content_type"),
                "size": int(item.get("size") or 0),
                "url": _media_url(broadcast_id, str(item["media_id"])),
            }
            for item in media
        ],
    }


async def _read_payload(cxn, broadcast_id: str) -> dict | None:
    row = await cxn.fetchrow(
        "SELECT * FROM staff_broadcasts WHERE broadcast_id = $1", broadcast_id,
    )
    if row is None:
        return None
    media = await cxn.fetch(
        "SELECT media_id, filename, content_type, size, position "
        "FROM staff_broadcast_media WHERE broadcast_id = $1 ORDER BY position ASC",
        broadcast_id,
    )
    return _serialise(row, media)


def _payload(broadcast_id: str) -> dict | None:
    cxn = _discord_bot.cxn

    async def read():
        return await _read_payload(cxn, broadcast_id)

    return run_on_bot_loop(read())


def _json_error(message: str, status: int = 400):
    return jsonify({"error": message}), status


def _clean_fields(body: dict, current: dict | None = None) -> tuple[dict | None, str | None]:
    current = current or {}
    title = str(body.get("title", current.get("title", "")) or "").strip()
    content = str(body.get("body", current.get("body", "")) or "").strip()
    footer = str(body.get("footer", current.get("footer", DEFAULT_FOOTER)) or "").strip()
    accent = _accent(body.get("accent", current.get("accent", DEFAULT_ACCENT)))
    if len(title) > MAX_TITLE:
        return None, f"The title must be {MAX_TITLE} characters or fewer."
    if len(content) > MAX_BODY:
        return None, f"The message must be {MAX_BODY} characters or fewer."
    if len(footer) > MAX_FOOTER:
        return None, f"The footer must be {MAX_FOOTER} characters or fewer."
    return {"title": title, "body": content, "footer": footer, "accent": accent}, None


def _start_sync(broadcast_id: str) -> bool:
    """Queue an edit of every delivered copy, if any were recorded.

    The status flips to ``syncing`` here, before the request returns, so the
    dashboard's progress poll can never observe a stale ``sent`` status and
    stop watching before the background edit starts.
    """
    cxn = _discord_bot.cxn

    async def prepare():
        count = int(await cxn.fetchval(
            "SELECT COUNT(*) FROM staff_broadcast_targets "
            "WHERE broadcast_id = $1 AND message_id IS NOT NULL",
            broadcast_id,
        ) or 0)
        if count == 0:
            return 0
        await cxn.execute(
            "UPDATE staff_broadcasts SET status = 'syncing', edited_count = 0, "
            "last_error = NULL, updated_at = $1 WHERE broadcast_id = $2",
            time.time(), broadcast_id,
        )
        return count

    async def job():
        from utils.broadcast import sync_broadcast
        await sync_broadcast(_discord_bot, broadcast_id)

    try:
        if run_on_bot_loop(prepare(), timeout=15) == 0:
            return False
        schedule_on_bot_loop(job())
        return True
    except RuntimeError:
        return False
    except Exception:
        log.exception("Could not start the copy update for broadcast %s", broadcast_id)
        return False


@app.route("/api/staff/broadcasts")
@require_auth
def api_staff_broadcasts():
    error = _require_owner()
    if error:
        return error
    cxn = _discord_bot.cxn

    async def load():
        rows = await cxn.fetch(
            "SELECT * FROM staff_broadcasts ORDER BY updated_at DESC LIMIT 50"
        )
        payloads = []
        for row in rows:
            media = await cxn.fetch(
                "SELECT media_id, filename, content_type, size, position "
                "FROM staff_broadcast_media WHERE broadcast_id = $1 "
                "ORDER BY position ASC",
                row["broadcast_id"],
            )
            payloads.append(_serialise(row, media))
        return payloads

    try:
        broadcasts = run_on_bot_loop(load(), timeout=15)
    except Exception:
        log.exception("Could not load staff broadcasts")
        return _json_error("Broadcasts could not be loaded.", 503)
    return jsonify({"broadcasts": broadcasts})


@app.route("/api/staff/broadcasts", methods=["POST"])
@require_auth
@require_csrf
def api_create_staff_broadcast():
    error = _require_owner()
    if error:
        return error
    body = request.get_json(silent=True) or {}
    fields, message = _clean_fields(body)
    if message:
        return _json_error(message)
    broadcast_id = uuid.uuid4().hex
    now = time.time()
    author_id = int(session["user"]["id"])
    cxn = _discord_bot.cxn

    async def create():
        await cxn.execute(
            "INSERT INTO staff_broadcasts (broadcast_id, title, body, accent, footer, "
            "status, created_by, created_at, updated_at) "
            "VALUES ($1, $2, $3, $4, $5, 'draft', $6, $7, $8)",
            broadcast_id, fields["title"], fields["body"], fields["accent"],
            fields["footer"], author_id, now, now,
        )
        return await _read_payload(cxn, broadcast_id)

    try:
        payload = run_on_bot_loop(create())
    except Exception:
        log.exception("Could not create staff broadcast")
        return _json_error("The broadcast could not be created.", 503)
    return jsonify({"broadcast": payload}), 201


@app.route("/api/staff/broadcasts/<broadcast_id>")
@require_auth
def api_staff_broadcast(broadcast_id):
    error = _require_owner()
    if error:
        return error
    try:
        payload = _payload(broadcast_id)
    except Exception:
        log.exception("Could not load staff broadcast %s", broadcast_id)
        return _json_error("The broadcast could not be loaded.", 503)
    if payload is None:
        return _json_error("That broadcast no longer exists.", 404)
    return jsonify({"broadcast": payload})


@app.route("/api/staff/broadcasts/<broadcast_id>", methods=["PUT"])
@require_auth
@require_csrf
def api_update_staff_broadcast(broadcast_id):
    error = _require_owner()
    if error:
        return error
    body = request.get_json(silent=True) or {}
    cxn = _discord_bot.cxn

    async def update():
        row = await cxn.fetchrow(
            "SELECT * FROM staff_broadcasts WHERE broadcast_id = $1", broadcast_id,
        )
        if row is None:
            return None, "That broadcast no longer exists."
        if str(row["status"]) in {"sending", "syncing"}:
            return None, "Wait for the current delivery to finish before editing."
        fields, message = _clean_fields(body, {
            "title": row["title"],
            "body": row["body"],
            "footer": row["footer"],
            "accent": row["accent"],
        })
        if message:
            return None, message
        delivered = str(row["status"]) == "sent" or int(row.get("sent_count") or 0) > 0
        if delivered and (not fields["title"] or not fields["body"]):
            return None, "A delivered broadcast still needs a title and a message."
        await cxn.execute(
            "UPDATE staff_broadcasts SET title = $1, body = $2, accent = $3, "
            "footer = $4, updated_at = $5 WHERE broadcast_id = $6",
            fields["title"], fields["body"], fields["accent"], fields["footer"],
            time.time(), broadcast_id,
        )
        return await _read_payload(cxn, broadcast_id), None

    try:
        payload, message = run_on_bot_loop(update(), timeout=15)
    except Exception:
        log.exception("Could not save staff broadcast %s", broadcast_id)
        return _json_error("The broadcast could not be saved.", 503)
    if message:
        return _json_error(message, 404 if "no longer exists" in message else 409)
    syncing = _start_sync(broadcast_id)
    return jsonify({"broadcast": payload, "syncing": syncing})


@app.route("/api/staff/broadcasts/<broadcast_id>", methods=["DELETE"])
@require_auth
@require_csrf
def api_delete_staff_broadcast(broadcast_id):
    error = _require_owner()
    if error:
        return error
    cxn = _discord_bot.cxn

    async def remove():
        row = await cxn.fetchrow(
            "SELECT status, sent_count FROM staff_broadcasts WHERE broadcast_id = $1",
            broadcast_id,
        )
        if row is None:
            return "That broadcast no longer exists."
        if str(row["status"]) == "sent" or int(row.get("sent_count") or 0) > 0:
            return "Delivered broadcasts are kept so their copies can still be edited."
        if str(row["status"]) in {"sending", "syncing"}:
            return "Wait for the current delivery to finish before deleting."
        await cxn.execute("DELETE FROM staff_broadcast_media WHERE broadcast_id = $1", broadcast_id)
        await cxn.execute("DELETE FROM staff_broadcast_targets WHERE broadcast_id = $1", broadcast_id)
        await cxn.execute("DELETE FROM staff_broadcasts WHERE broadcast_id = $1", broadcast_id)
        return None

    try:
        message = run_on_bot_loop(remove())
    except Exception:
        log.exception("Could not delete staff broadcast %s", broadcast_id)
        return _json_error("The broadcast could not be deleted.", 503)
    if message:
        return _json_error(message, 409)
    return jsonify({"ok": True})


@app.route("/api/staff/broadcasts/<broadcast_id>/media", methods=["POST"])
@require_auth
@require_csrf
def api_upload_staff_broadcast_media(broadcast_id):
    error = _require_owner()
    if error:
        return error
    upload = request.files.get("file")
    if upload is None:
        return _json_error("Choose an image to upload.")
    # Read one byte past the limit so an oversized upload is rejected without
    # pulling an unbounded body into the worker's memory.
    raw = upload.stream.read(MAX_MEDIA_BYTES + 1)
    if not raw:
        return _json_error("That image is empty.")
    if len(raw) > MAX_MEDIA_BYTES:
        return _json_error("Images must be 8 MB or smaller.")
    content_type = _detect_image_type(raw, upload.mimetype)
    if content_type is None:
        return _json_error("Upload a PNG, JPEG, GIF, or WebP image.")
    filename = _media_filename(upload.filename or "broadcast", content_type)
    media_id = uuid.uuid4().hex
    encoded = base64.b64encode(raw).decode("ascii")
    cxn = _discord_bot.cxn

    async def store():
        row = await cxn.fetchrow(
            "SELECT status FROM staff_broadcasts WHERE broadcast_id = $1", broadcast_id,
        )
        if row is None:
            return None, "That broadcast no longer exists."
        if str(row["status"]) in {"sending", "syncing"}:
            return None, "Wait for the current delivery to finish before adding images."
        count = int(await cxn.fetchval(
            "SELECT COUNT(*) FROM staff_broadcast_media WHERE broadcast_id = $1",
            broadcast_id,
        ) or 0)
        if count >= MAX_MEDIA_ITEMS:
            return None, f"A broadcast can carry up to {MAX_MEDIA_ITEMS} images."
        stored_total = int(await cxn.fetchval(
            "SELECT COALESCE(SUM(size), 0) FROM staff_broadcast_media "
            "WHERE broadcast_id = $1",
            broadcast_id,
        ) or 0)
        if stored_total + len(raw) > MAX_TOTAL_BYTES:
            return None, "Images can total 20 MB per broadcast so Discord accepts every copy."
        position = int(await cxn.fetchval(
            "SELECT COALESCE(MAX(position), -1) + 1 FROM staff_broadcast_media "
            "WHERE broadcast_id = $1",
            broadcast_id,
        ) or 0)
        await cxn.execute(
            "INSERT INTO staff_broadcast_media (media_id, broadcast_id, filename, "
            "content_type, size, position, data, created_at) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
            media_id, broadcast_id, filename, content_type, len(raw), position,
            encoded, time.time(),
        )
        return await _read_payload(cxn, broadcast_id), None

    try:
        payload, message = run_on_bot_loop(store(), timeout=15)
    except Exception:
        log.exception("Could not store broadcast image for %s", broadcast_id)
        return _json_error("The image could not be saved.", 503)
    if message:
        return _json_error(message, 404 if "no longer exists" in message else 409)
    syncing = _start_sync(broadcast_id)
    return jsonify({"broadcast": payload, "syncing": syncing})


@app.route("/api/staff/broadcasts/<broadcast_id>/media/<media_id>", methods=["DELETE"])
@require_auth
@require_csrf
def api_delete_staff_broadcast_media(broadcast_id, media_id):
    error = _require_owner()
    if error:
        return error
    cxn = _discord_bot.cxn

    async def remove():
        row = await cxn.fetchrow(
            "SELECT status FROM staff_broadcasts WHERE broadcast_id = $1", broadcast_id,
        )
        if row is None:
            return None, "That broadcast no longer exists."
        if str(row["status"]) in {"sending", "syncing"}:
            return None, "Wait for the current delivery to finish before removing images."
        await cxn.execute(
            "DELETE FROM staff_broadcast_media WHERE broadcast_id = $1 AND media_id = $2",
            broadcast_id, media_id,
        )
        return await _read_payload(cxn, broadcast_id), None

    try:
        payload, message = run_on_bot_loop(remove(), timeout=15)
    except Exception:
        log.exception("Could not remove broadcast image %s", media_id)
        return _json_error("The image could not be removed.", 503)
    if message:
        return _json_error(message, 404 if "no longer exists" in message else 409)
    syncing = _start_sync(broadcast_id)
    return jsonify({"broadcast": payload, "syncing": syncing})


@app.route("/api/staff/broadcasts/<broadcast_id>/media/<media_id>")
@require_auth
def api_staff_broadcast_media(broadcast_id, media_id):
    error = _require_owner()
    if error:
        return error
    cxn = _discord_bot.cxn

    async def read():
        return await cxn.fetchrow(
            "SELECT content_type, data FROM staff_broadcast_media "
            "WHERE broadcast_id = $1 AND media_id = $2",
            broadcast_id, media_id,
        )

    try:
        row = run_on_bot_loop(read())
    except Exception:
        log.exception("Could not read broadcast image %s", media_id)
        return _json_error("The image could not be loaded.", 503)
    if row is None:
        return _json_error("That image no longer exists.", 404)
    try:
        payload = base64.b64decode(str(row["data"] or ""))
    except Exception:
        return _json_error("The image could not be loaded.", 500)
    return _server.Response(
        payload,
        mimetype=str(row["content_type"] or "application/octet-stream"),
        headers={"Cache-Control": "private, max-age=300"},
    )


@app.route("/api/staff/broadcasts/<broadcast_id>/send", methods=["POST"])
@require_auth
@require_csrf
def api_send_staff_broadcast(broadcast_id):
    error = _require_owner()
    if error:
        return error
    cxn = _discord_bot.cxn

    async def prepare():
        row = await cxn.fetchrow(
            "SELECT title, body, status FROM staff_broadcasts WHERE broadcast_id = $1",
            broadcast_id,
        )
        if row is None:
            return None, "That broadcast no longer exists."
        if not str(row["title"] or "").strip() or not str(row["body"] or "").strip():
            return None, "Add a title and message before sending."
        if str(row["status"]) in {"sending", "syncing"}:
            return None, "That broadcast is already being delivered."
        if str(row["status"]) == "sent":
            return None, "That broadcast was already sent. Edit it to update the delivered copies."
        from utils.broadcast import begin_delivery
        message = await begin_delivery(_discord_bot, broadcast_id)
        if message:
            return None, message
        return await _read_payload(cxn, broadcast_id), None

    try:
        payload, message = run_on_bot_loop(prepare(), timeout=15)
    except Exception:
        log.exception("Could not start staff broadcast %s", broadcast_id)
        return _json_error("The broadcast could not be started.", 503)
    if message:
        return _json_error(message, 409 if "already" in message or "Add a title" in message else 404)

    async def job():
        from utils.broadcast import deliver_broadcast
        await deliver_broadcast(_discord_bot, broadcast_id)

    try:
        schedule_on_bot_loop(job())
    except RuntimeError:
        # Leave nothing stuck in "sending" when the bot loop is unavailable.
        async def reset():
            await cxn.execute(
                "UPDATE staff_broadcasts SET status = 'failed', "
                "last_error = 'The Discord bot is not running.', updated_at = $1 "
                "WHERE broadcast_id = $2",
                time.time(), broadcast_id,
            )

        try:
            run_on_bot_loop(reset())
        except Exception:
            pass
        return _json_error("The Discord bot is not running.", 503)
    return jsonify({"broadcast": payload})
