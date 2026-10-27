"""Flask routes for data removal requests and their owner-only review queue.

Deletion is never executed by the public form. A signed-in member submits a
scoped request, ownership is checked against the live guild (or the recorded
owner at the time Niko was removed), and the bot owner reviews it before the
conservative deletion engine runs. See utils/data_removal.py for the exact
allow-list and the records that are always preserved.
"""

from .. import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

import json
import time
import uuid
from functools import wraps

from utils import logging

from flask import jsonify, request, session

from utils.data_removal import (
    execute_account_deletion,
    execute_guild_deletion,
    record_ownership,
)

ACCOUNT_CONFIRMATION = "DELETE MY DATA"
MIN_REASON_LENGTH = 20
MAX_REASON_LENGTH = 2000
MAX_REQUESTS_PER_DAY = 3


def _user_id() -> int | None:
    raw = str(session.get("user", {}).get("id", "")).strip()
    return int(raw) if raw.isdigit() else None


def _require_signed_in(f):
    """Require Discord OAuth without hiding this route from blacklisted users.

    Privacy rights do not disappear because a moderation record exists. The
    request still preserves every safety record, so allowing the submission
    cannot be used to bypass a ban.
    """
    @wraps(f)
    def _inner(*args, **kwargs):
        if not ensure_access_token():
            return jsonify({"error": "Sign in with Discord to continue.", "login_url": "/auth/login"}), 401
        return f(*args, **kwargs)
    return _inner


def _require_owner(f):
    @wraps(f)
    def _inner(*args, **kwargs):
        if _current_staff_role() != "owner":
            return jsonify({"error": "This area is restricted to the bot owner."}), 403
        return f(*args, **kwargs)
    return _inner


def _require_bot():
    if _discord_bot is None or not getattr(_discord_bot, "cxn", None):
        return None
    return _discord_bot


def _request_json(row) -> dict:
    return {
        "id": row.get("request_id"),
        "scope": row.get("scope"),
        "guild_id": str(row["guild_id"]) if row.get("guild_id") is not None else None,
        "guild_name": row.get("guild_name"),
        "reason": row.get("reason") or "",
        "status": row.get("status") or "pending",
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "review_note": row.get("review_note"),
        "completed_at": row.get("completed_at"),
        "reviewed_by": str(row["reviewed_by"]) if row.get("reviewed_by") is not None else None,
    }


async def _owned_targets(bot, user_id: int) -> list[dict]:
    """Refresh and return every server this member can prove they own."""
    pool = bot.cxn
    for guild in bot.guilds:
        if guild.owner_id == user_id:
            await record_ownership(
                pool, guild.id, user_id, guild.name,
                str(guild.icon.url) if guild.icon else None,
            )

    rows = await pool.fetch(
        "SELECT guild_id, owner_id, guild_name, icon_url, removed_at "
        "FROM guild_ownership WHERE owner_id = $1",
        user_id,
    )
    targets: list[dict] = []
    for row in rows:
        guild_id = int(row["guild_id"])
        guild = bot.get_guild(guild_id)
        if guild is not None and guild.owner_id != user_id:
            # Ownership was transferred while Niko was still present. The new
            # owner is the only member who can request that server's deletion.
            await record_ownership(
                pool, guild.id, guild.owner_id, guild.name,
                str(guild.icon.url) if guild.icon else None,
            )
            continue
        if guild is None and row.get("removed_at") is None:
            # The bot was removed while it was offline, so no on_guild_remove
            # event marked the row. The absence of the guild from the gateway is
            # itself proof that Niko is no longer there; freeze the recorded
            # owner now so the deletion option remains available.
            await record_ownership(
                pool, guild_id, int(row["owner_id"]), row.get("guild_name"),
                row.get("icon_url"), removed=True,
            )
            row = {**dict(row), "removed_at": time.time()}
        targets.append({
            "id": str(guild_id),
            "name": row.get("guild_name") or f"Server {guild_id}",
            "icon_url": str(guild.icon.url) if guild is not None and guild.icon else row.get("icon_url"),
            "bot_present": guild is not None,
            "removed_at": row.get("removed_at"),
        })
    targets.sort(key=lambda item: (not item["bot_present"], (item["name"] or "").lower()))
    return targets


def _pending_keys(rows) -> set[tuple[str, str | None]]:
    return {
        (row["scope"], str(row["guild_id"]) if row.get("guild_id") is not None else None)
        for row in rows
        if row.get("status") == "pending"
    }


@app.route("/api/privacy/data-removal")
@_require_signed_in
def api_data_removal_overview():
    user_id = _user_id()
    bot = _require_bot()
    if user_id is None or bot is None:
        return jsonify({"error": "Data requests are unavailable while the bot is offline."}), 503
    try:
        targets = run_on_bot_loop(_owned_targets(bot, user_id), timeout=20)
        rows = run_on_bot_loop(
            bot.cxn.fetch(
                "SELECT request_id, scope, guild_id, guild_name, reason, status, "
                "created_at, updated_at, review_note, completed_at, reviewed_by "
                "FROM data_removal_requests WHERE user_id = $1 "
                "ORDER BY created_at DESC",
                user_id,
            ),
            timeout=10,
        )
    except Exception as exc:
        logging.warning("DataRemoval", f"Could not load requests: {exc}")
        return jsonify({"error": "Your data requests could not be loaded right now."}), 503

    pending = _pending_keys(rows)
    return jsonify({
        "requests": [_request_json(row) for row in rows],
        "account": {"pending": ("account", None) in pending},
        "servers": [
            {**target, "pending": ("server", target["id"]) in pending}
            for target in targets
        ],
        "confirmations": {
            "account": ACCOUNT_CONFIRMATION,
            "min_reason_length": MIN_REASON_LENGTH,
        },
    })


@app.route("/api/privacy/data-removal", methods=["POST"])
@_require_signed_in
@require_csrf
def api_data_removal_submit():
    user_id = _user_id()
    bot = _require_bot()
    if user_id is None or bot is None:
        return jsonify({"error": "Data requests are unavailable while the bot is offline."}), 503

    data = request.get_json(silent=True) or {}
    scope = str(data.get("scope") or "").strip().lower()
    reason = str(data.get("reason") or "").strip()
    confirmation = str(data.get("confirmation") or "")

    if scope not in {"account", "server"}:
        return jsonify({"error": "Choose either account data or server data."}), 400
    if len(reason) < MIN_REASON_LENGTH:
        return jsonify({"error": f"Please explain your request in at least {MIN_REASON_LENGTH} characters."}), 400
    if len(reason) > MAX_REASON_LENGTH:
        return jsonify({"error": "Your explanation is too long."}), 400

    guild_id = None
    guild_name = None
    if scope == "server":
        raw_guild_id = str(data.get("guild_id") or "").strip()
        if not raw_guild_id.isdigit():
            return jsonify({"error": "Choose a server."}), 400
        guild_id = int(raw_guild_id)
        try:
            targets = run_on_bot_loop(_owned_targets(bot, user_id), timeout=20)
        except Exception:
            return jsonify({"error": "Ownership could not be verified right now."}), 503
        target = next((item for item in targets if item["id"] == raw_guild_id), None)
        if target is None:
            return jsonify({
                "error": "Only the member who owns this server, or owned it when Niko was removed, can request its deletion."
            }), 403
        guild_name = target["name"]
        if confirmation != guild_name:
            return jsonify({"error": "Type the server name exactly to confirm."}), 400
    else:
        if confirmation != ACCOUNT_CONFIRMATION:
            return jsonify({"error": f'Type "{ACCOUNT_CONFIRMATION}" to confirm.'}), 400

    try:
        rows = run_on_bot_loop(
            bot.cxn.fetch(
                "SELECT request_id, scope, guild_id, status FROM data_removal_requests "
                "WHERE user_id = $1 AND created_at > $2",
                user_id,
                time.time() - 86400,
            ),
            timeout=10,
        )
    except Exception:
        return jsonify({"error": "Your existing requests could not be checked."}), 503

    pending = _pending_keys(rows)
    if (scope, str(guild_id) if guild_id is not None else None) in pending:
        return jsonify({"error": "You already have a pending request for this target."}), 409
    if len(rows) >= MAX_REQUESTS_PER_DAY:
        return jsonify({"error": "Too many requests in the last 24 hours. Contact the bot owner if this is urgent."}), 429

    now = time.time()
    request_id = uuid.uuid4().hex
    try:
        run_on_bot_loop(
            bot.cxn.execute(
                "INSERT INTO data_removal_requests "
                "(request_id, user_id, scope, guild_id, guild_name, reason, status, "
                "created_at, updated_at) "
                "VALUES ($1, $2, $3, $4, $5, $6, 'pending', $7, $8)",
                request_id,
                user_id,
                scope,
                guild_id,
                guild_name,
                reason,
                now,
                now,
            ),
            timeout=10,
        )
    except Exception as exc:
        logging.warning("DataRemoval", f"Could not save request: {exc}")
        return jsonify({"error": "Your request could not be saved. Please try again."}), 503

    return jsonify({
        "ok": True,
        "request": {
            "id": request_id,
            "scope": scope,
            "guild_id": str(guild_id) if guild_id is not None else None,
            "guild_name": guild_name,
            "reason": reason,
            "status": "pending",
            "created_at": now,
            "updated_at": now,
            "review_note": None,
            "completed_at": None,
            "reviewed_by": None,
        },
    }), 201


@app.route("/api/privacy/data-removal/<request_id>", methods=["DELETE"])
@_require_signed_in
@require_csrf
def api_data_removal_withdraw(request_id: str):
    user_id = _user_id()
    bot = _require_bot()
    if user_id is None or bot is None:
        return jsonify({"error": "Data requests are unavailable while the bot is offline."}), 503
    try:
        row = run_on_bot_loop(
            bot.cxn.fetchrow(
                "SELECT request_id FROM data_removal_requests "
                "WHERE request_id = $1 AND user_id = $2 AND status = 'pending'",
                request_id,
                user_id,
            ),
            timeout=10,
        )
        if row is None:
            return jsonify({"error": "That request is not pending."}), 404
        run_on_bot_loop(
            bot.cxn.execute(
                "UPDATE data_removal_requests SET status = 'withdrawn', updated_at = $1 "
                "WHERE request_id = $2 AND user_id = $3",
                time.time(),
                request_id,
                user_id,
            ),
            timeout=10,
        )
    except Exception:
        return jsonify({"error": "The request could not be withdrawn right now."}), 503
    return jsonify({"ok": True, "status": "withdrawn"})


@app.route("/api/staff/data-removal")
@_require_signed_in
@_require_owner
def api_staff_data_removal():
    bot = _require_bot()
    if bot is None:
        return jsonify({"error": "The bot database is unavailable."}), 503
    try:
        rows = run_on_bot_loop(
            bot.cxn.fetch(
                "SELECT request_id, user_id, scope, guild_id, guild_name, reason, "
                "status, created_at, updated_at, review_note, completed_at, reviewed_by, result "
                "FROM data_removal_requests ORDER BY created_at DESC"
            ),
            timeout=20,
        )
    except Exception as exc:
        logging.warning("DataRemoval", f"Owner queue failed: {exc}")
        return jsonify({"error": "The request queue could not be loaded."}), 503

    requests = []
    for row in rows:
        item = _request_json(row)
        item["user_id"] = str(row["user_id"])
        item["result"] = json.loads(row["result"]) if row.get("result") else None
        requests.append(item)
    return jsonify({
        "requests": requests,
        "pending": sum(1 for item in requests if item["status"] == "pending"),
    })


@app.route("/api/staff/data-removal/<request_id>/review", methods=["POST"])
@_require_signed_in
@_require_owner
@require_csrf
def api_staff_data_removal_review(request_id: str):
    bot = _require_bot()
    if bot is None:
        return jsonify({"error": "The bot database is unavailable."}), 503

    data = request.get_json(silent=True) or {}
    decision = str(data.get("status") or "").strip().lower()
    note = str(data.get("note") or "").strip()
    if decision not in {"approved", "denied"}:
        return jsonify({"error": "Choose approve or deny."}), 400
    if decision == "denied" and len(note) < 5:
        return jsonify({"error": "Add a short note explaining the decision."}), 400
    if len(note) > 2000:
        return jsonify({"error": "The note is too long."}), 400

    try:
        row = run_on_bot_loop(
            bot.cxn.fetchrow(
                "SELECT request_id, user_id, scope, guild_id, guild_name, status "
                "FROM data_removal_requests WHERE request_id = $1",
                request_id,
            ),
            timeout=10,
        )
    except Exception:
        return jsonify({"error": "The request could not be loaded."}), 503
    if row is None:
        return jsonify({"error": "That request does not exist."}), 404
    if row.get("status") != "pending":
        return jsonify({"error": "That request has already been handled."}), 409

    now = time.time()
    reviewer = _user_id()
    result = None

    if decision == "approved":
        if row.get("scope") == "server":
            guild_id = int(row["guild_id"])
            guild = bot.get_guild(guild_id)
            if guild is not None and guild.owner_id != int(row["user_id"]):
                return jsonify({"error": "The member is no longer the owner of that server."}), 409
            if guild is None:
                ownership = run_on_bot_loop(
                    bot.cxn.fetchrow(
                        "SELECT owner_id, removed_at FROM guild_ownership WHERE guild_id = $1",
                        guild_id,
                    ),
                    timeout=10,
                )
                if ownership is None or int(ownership["owner_id"]) != int(row["user_id"]):
                    return jsonify({"error": "The recorded owner does not match this request."}), 409
                if ownership.get("removed_at") is None:
                    return jsonify({"error": "The bot is not in that server and its removal was not recorded."}), 409
            try:
                result = run_on_bot_loop(
                    execute_guild_deletion(bot.cxn, guild_id), timeout=60
                )
            except Exception as exc:
                logging.warning("DataRemoval", f"Server deletion failed: {exc}")
                return jsonify({"error": "Deletion failed; the request remains pending."}), 500
        else:
            try:
                result = run_on_bot_loop(
                    execute_account_deletion(bot.cxn, int(row["user_id"])), timeout=60
                )
            except Exception as exc:
                logging.warning("DataRemoval", f"Account deletion failed: {exc}")
                return jsonify({"error": "Deletion failed; the request remains pending."}), 500

        try:
            run_on_bot_loop(
                bot.cxn.execute(
                "UPDATE data_removal_requests SET status = 'completed', "
                "reviewed_by = $1, reviewed_at = $2, review_note = $3, "
                "completed_at = $4, updated_at = $5, result = $6 "
                "WHERE request_id = $7 AND status = 'pending'",
                reviewer,
                now,
                note,
                now,
                now,
                json.dumps(result),
                request_id,
            ),
                timeout=10,
            )
        except Exception:
            return jsonify({"error": "Deletion ran, but the request could not be marked complete."}), 503
        return jsonify({"ok": True, "status": "completed", "result": result})

    try:
        run_on_bot_loop(
            bot.cxn.execute(
                "UPDATE data_removal_requests SET status = 'denied', reviewed_by = $1, "
                "reviewed_at = $2, review_note = $3, updated_at = $4 "
                "WHERE request_id = $5 AND status = 'pending'",
                reviewer,
                now,
                note,
                now,
                request_id,
            ),
            timeout=10,
        )
    except Exception:
        return jsonify({"error": "The decision could not be saved."}), 503
    return jsonify({"ok": True, "status": "denied"})
