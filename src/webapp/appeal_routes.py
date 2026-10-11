"""Public submission and staff review routes for blacklist appeals."""

from . import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

import asyncio
import time
import uuid

_APPEAL_LOCKS = {}


def _appeal_pool():
    if _discord_bot is None or not getattr(_discord_bot, "cxn", None):
        return None
    return _discord_bot.cxn


def _appeal_staff_role():
    role = _current_staff_role()
    if role not in {"owner", "head_admin"}:
        return None, (jsonify({"error": "Appeal review is restricted to the bot owner and Head Admins."}), 403)
    if _appeal_pool() is None:
        return None, (jsonify({"error": "The appeal database is temporarily unavailable."}), 503)
    return role, None


@app.route("/api/appeals/blacklist", methods=["GET", "POST"])
def api_blacklist_appeal():
    return _handle_blacklist_appeal()


@app.route("/api/appeals/guild/<guild_id>", methods=["GET", "POST"])
def api_guild_blacklist_appeal(guild_id):
    if not str(guild_id).isdigit():
        return jsonify({"error": "Invalid guild ID."}), 400
    return _handle_blacklist_appeal(guild_id=int(guild_id))


def _handle_blacklist_appeal(guild_id=None):
    if not ensure_access_token():
        return jsonify({"error": "Sign in with Discord to submit a blacklist appeal."}), 401
    session.setdefault("csrf_token", secrets.token_urlsafe(24))
    pool = _appeal_pool()
    if pool is None:
        return jsonify({"error": "The appeal service is temporarily unavailable."}), 503
    user_id = int(session["user"]["id"])
    if request.method == "GET":
        try:
            if guild_id is not None:
                if str(guild_id) not in managed_guild_ids():
                    return jsonify({"error": "You do not have Manage Server access to this guild."}), 403
                manager = _load_blacklist_manager()
                entry = manager.get_guild_entry(guild_id)

                async def read_guild_status():
                    return await pool.fetchrow(
                        "SELECT appeal_id, status, appeal_text, blacklist_reason, created_at, reviewed_at, staff_note FROM blacklist_appeals WHERE guild_id = $1 ORDER BY created_at DESC LIMIT 1",
                        guild_id,
                    )
                row = run_on_bot_loop(read_guild_status())
                if row:
                    result = dict(row)
                    if result["status"] == "approved" and entry and entry.get("status") == "active":
                        return jsonify({
                            "status": "eligible",
                            "can_appeal": True,
                            "reason": entry.get("reason") or "No reason recorded.",
                            "previous_appeal": result,
                        })
                    result["can_appeal"] = False
                    result["reason"] = entry.get("reason") if entry else result.get("blacklist_reason")
                    return jsonify(result)
                if not entry:
                    return jsonify({"status": "not_blacklisted", "can_appeal": False})
                if entry.get("status") != "active":
                    return jsonify({"status": "not_eligible", "can_appeal": False})
                return jsonify({"status": "eligible", "can_appeal": True, "reason": entry.get("reason") or "No reason recorded."})

            async def read_status():
                return await pool.fetchrow(
                    "SELECT appeal_id, status, appeal_text, blacklist_reason, created_at, reviewed_at, staff_note FROM blacklist_appeals WHERE user_id = $1 AND guild_id IS NULL ORDER BY created_at DESC LIMIT 1",
                    user_id,
                )
            row = run_on_bot_loop(read_status())
            if not row:
                entry = _current_user_blacklist_entry()
                if not entry:
                    return jsonify({"status": "not_blacklisted", "can_appeal": False})
                return jsonify({"status": "eligible", "can_appeal": True, "reason": entry.get("reason") or "No reason recorded."})
            result = dict(row)
            entry = _current_user_blacklist_entry()
            if result["status"] == "approved" and entry:
                active_appeal = None
                if entry.get("appeal_id"):
                    async def read_active_appeal():
                        return await pool.fetchrow(
                            "SELECT appeal_id, status, appeal_text, blacklist_reason, created_at, reviewed_at, staff_note FROM blacklist_appeals WHERE appeal_id = $1",
                            entry["appeal_id"],
                        )
                    active_appeal = run_on_bot_loop(read_active_appeal())
                if active_appeal and active_appeal["status"] in {"pending", "denied"}:
                    result = dict(active_appeal)
                    result["can_appeal"] = False
                    return jsonify(result)
                return jsonify({"status": "eligible", "can_appeal": True, "reason": entry.get("reason") or "No reason recorded.", "previous_appeal": result})
            result["can_appeal"] = False
            return jsonify(result)
        except Exception:
            return jsonify({"error": "Your appeal status could not be loaded."}), 503

    csrf_token = session.get("csrf_token")
    if not csrf_token or request.headers.get("X-CSRF-Token") != csrf_token:
        return jsonify({"error": "Invalid request token. Refresh the page and try again."}), 403
    body = request.get_json(silent=True) or {}
    appeal_text = str(body.get("appeal", "")).strip()
    if not appeal_text or len(appeal_text) > 4000:
        return jsonify({"error": "Write an appeal between 1 and 4,000 characters."}), 400
    try:
        if guild_id is not None:
            if str(guild_id) not in managed_guild_ids():
                return jsonify({"error": "You do not have Manage Server access to this guild."}), 403
            manager = _load_blacklist_manager()
            entry = manager.get_guild_entry(guild_id)
            if not entry or entry.get("status") != "active":
                return jsonify({"error": "This guild blacklist is not eligible for an appeal."}), 403
            lock_key = ("guild", guild_id)
        else:
            entry = _current_user_blacklist_entry()
            if not entry:
                return jsonify({"error": "Only users with an active blacklist can appeal."}), 403
            lock_key = ("user", user_id)

        async def create_appeal():
            lock = _APPEAL_LOCKS.setdefault(lock_key, asyncio.Lock())
            async with lock:
                previous_query = "SELECT status FROM blacklist_appeals WHERE guild_id = $1 ORDER BY created_at DESC LIMIT 1" if guild_id is not None else "SELECT status FROM blacklist_appeals WHERE user_id = $1 AND guild_id IS NULL ORDER BY created_at DESC LIMIT 1"
                previous = await pool.fetchrow(previous_query, guild_id if guild_id is not None else user_id)
                if previous and previous["status"] in {"pending", "denied"}:
                    return "blocked"
                if guild_id is not None:
                    active = await pool.fetchrow(
                        "SELECT id FROM blacklist_guilds WHERE id = $1 AND status = 'active'",
                        guild_id,
                    )
                else:
                    active = await pool.fetchrow(
                        "SELECT id FROM blacklist_users WHERE id = $1 AND status = 'active'",
                        user_id,
                    )
                if not active:
                    return "no_active_blacklist"
                appeal_id = uuid.uuid4().hex
                created_at = time.time()
                await pool.execute(
                    "INSERT INTO blacklist_appeals (appeal_id, user_id, guild_id, username, appeal_text, blacklist_reason, blacklist_timestamp, blacklist_added_by, blacklist_expires_at, status, created_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'pending', $10)",
                    appeal_id, user_id, guild_id,
                    session.get("user", {}).get("global_name") or session.get("user", {}).get("username"),
                    appeal_text, entry.get("reason"), entry.get("timestamp"), entry.get("added_by"), entry.get("expires_at"), created_at,
                )
                return appeal_id

        result = run_on_bot_loop(create_appeal())
        if result not in {"blocked", "no_active_blacklist"}:
            from utils.blacklist_manager import BlacklistManager
            run_on_bot_loop(BlacklistManager().reload())
        if result == "blocked":
            return jsonify({"error": "A pending appeal is already under review, or a previous appeal was denied. No further appeal can be submitted."}), 409
        if result == "no_active_blacklist":
            message = "This guild blacklist is not eligible for an appeal." if guild_id is not None else "Only users with an active blacklist can appeal."
            return jsonify({"error": message}), 403
        return jsonify({"ok": True, "appeal_id": result, "status": "pending"}), 201
    except Exception:
        return jsonify({"error": "Your appeal could not be submitted."}), 503


@app.route("/api/staff/blacklist-appeals", methods=["GET"])
@require_auth
def api_staff_blacklist_appeals():
    _, error = _appeal_staff_role()
    if error:
        return error
    try:
        async def fetch_appeals():
            rows = await _appeal_pool().fetch(
                "SELECT appeal_id, user_id, guild_id, username, appeal_text, blacklist_reason, blacklist_timestamp, status, created_at, reviewed_by, reviewed_at, staff_note FROM blacklist_appeals ORDER BY created_at DESC LIMIT 300"
            )
            appeals = [dict(row) for row in rows]
            appeals.sort(key=lambda appeal: (appeal.get("status") != "pending", -(appeal.get("created_at") or 0)))
            return appeals
        return jsonify({"appeals": run_on_bot_loop(fetch_appeals())})
    except Exception:
        return jsonify({"error": "Blacklist appeals could not be loaded."}), 503


@app.route("/api/staff/blacklist-appeals/<appeal_id>/review", methods=["POST"])
@require_auth
@require_csrf
def api_review_blacklist_appeal(appeal_id):
    _, error = _appeal_staff_role()
    if error:
        return error
    body = request.get_json(silent=True) or {}
    status = body.get("status")
    note = str(body.get("note", "")).strip()
    if status not in {"approved", "denied"}:
        return jsonify({"error": "Choose approve or deny."}), 400
    if len(note) > 2000:
        return jsonify({"error": "Staff notes must be 2,000 characters or fewer."}), 400
    reviewer_id = int(session["user"]["id"])
    reviewed_at = time.time()
    try:
        async def review():
            pool = _appeal_pool()
            appeal = await pool.fetchrow("SELECT * FROM blacklist_appeals WHERE appeal_id = $1", appeal_id)
            if not appeal:
                return False
            lock_key = ("guild", int(appeal["guild_id"])) if appeal.get("guild_id") is not None else ("user", int(appeal["user_id"]))
            lock = _APPEAL_LOCKS.setdefault(lock_key, asyncio.Lock())
            async with lock:
                appeal = await pool.fetchrow("SELECT * FROM blacklist_appeals WHERE appeal_id = $1", appeal_id)
                if not appeal or appeal["status"] != "pending":
                    return False
                if status == "approved":
                    guild_id = appeal.get("guild_id")
                    if guild_id is not None:
                        await pool.execute(
                            "UPDATE blacklist_guilds SET status = 'appealed', appeal_id = $1 WHERE id = $2 AND status = 'active'",
                            appeal_id, int(guild_id),
                        )
                        blacklist_row = await pool.fetchrow("SELECT status FROM blacklist_guilds WHERE id = $1", int(guild_id))
                    else:
                        await pool.execute(
                            "UPDATE blacklist_users SET status = 'appealed', appeal_id = $1 WHERE id = $2 AND status = 'active'",
                            appeal_id, int(appeal["user_id"]),
                        )
                        blacklist_row = await pool.fetchrow("SELECT status FROM blacklist_users WHERE id = $1", int(appeal["user_id"]))
                    if blacklist_row and blacklist_row["status"] != "appealed":
                        raise RuntimeError("The active blacklist could not be marked as appealed.")
                await pool.execute(
                    "UPDATE blacklist_appeals SET status = $1, reviewed_by = $2, reviewed_at = $3, staff_note = $4 WHERE appeal_id = $5 AND status = 'pending'",
                    status, reviewer_id, reviewed_at, note or None, appeal_id,
                )
                saved = await pool.fetchrow("SELECT status, reviewed_by FROM blacklist_appeals WHERE appeal_id = $1", appeal_id)
                if not saved or saved["status"] != status or str(saved["reviewed_by"]) != str(reviewer_id):
                    return False
                return True
        if not run_on_bot_loop(review()):
            return jsonify({"error": "This appeal is no longer pending."}), 409
        if status == "approved":
            from utils.blacklist_manager import BlacklistManager
            run_on_bot_loop(BlacklistManager().reload())
        return jsonify({"ok": True, "status": status})
    except Exception:
        return jsonify({"error": "The appeal review could not be saved."}), 503
