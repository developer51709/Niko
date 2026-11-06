"""Developer portal routes and the versioned, keyed public API.

Two surfaces live here:

* ``/api/developer/...`` — the signed-in developer portal. Access grants and
  the roster are owner-only; keys and usage are scoped to the signed-in account.
* ``/api/v1/...`` (also ``/v1/...`` on the API subdomain) — the public developer
  API. Every endpoint requires a bearer key and the scopes named on its route.
"""

from __future__ import annotations

import time

from flask import g, jsonify, request

from .. import developer_applications, developer_portal, leaderboard_cache
from .. import server as _server
from ..api_errors import error_response
from ..database import (
    get_runtime_economy_rows,
    get_runtime_guild_level_page,
    get_runtime_leaderboard_page,
    get_runtime_member_metadata,
    level_xp_for_next,
    sqlite_connect,
)

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})


# ── Portal helpers ────────────────────────────────────────────────────────────

def _current_user_id() -> str:
    return developer_portal.session_user_id()


def _portal_access():
    user_id = _current_user_id()
    access = developer_portal.developer_access(user_id)
    if access["suspended"]:
        return None, error_response(
            "ACCESS_SUSPENDED",
            "Developer access is suspended. Submit an appeal through the DM Niko sent you.",
            403,
            docs="/developers/rate-limits",
            details={"suspension": access.get("suspension"), "appeal": access.get("appeal")},
        )
    if not access["enabled"]:
        return None, error_response(
            "ACCESS_NOT_GRANTED",
            "Developer access has not been granted for this account.",
            403,
            docs="/developers/quickstart",
        )
    return access, None


def _owner_error():
    if not _is_owner():
        return error_response(
            "OWNER_ONLY",
            "Only the bot owner can manage developer access.",
            403,
            docs="/developers/authentication",
        )
    return None


def _page_args(default_size: int = 20, max_size: int = 100):
    try:
        page = int(request.args.get("page", "1"))
        page_size = int(request.args.get("page_size", str(default_size)))
    except (TypeError, ValueError):
        return None, None, None
    if page < 1 or page_size < 1:
        return None, None, None
    page_size = min(page_size, max_size)
    return page, page_size, (page - 1) * page_size


def _guild(guild_id: str):
    try:
        numeric = int(guild_id)
    except (TypeError, ValueError):
        return None
    if _discord_bot is None:
        return None
    try:
        return _discord_bot.get_guild(numeric)
    except Exception:
        return None


def _identity(user_id: str) -> dict:
    return developer_portal.resolve_identity(user_id)


# ── Portal: the signed-in developer ──────────────────────────────────────────

@app.route("/api/developer/me")
@require_auth
def api_developer_me():
    user_id = _current_user_id()
    access = developer_portal.developer_access(user_id)
    keys = developer_portal.list_keys(user_id) if access["enabled"] else []
    return jsonify({
        "access": access,
        "appeal": access.get("appeal") or developer_portal.appeal_for_user(user_id),
        "suspension": access.get("suspension"),
        "policy_version": developer_portal.POLICY_VERSION,
        "policy_updated": developer_portal.POLICY_UPDATED,
        "scopes": developer_portal.scope_options(),
        "key_count": len([key for key in keys if not key.get("revoked_at")]),
        "base_url": "/api/v1",
        "rate_limit": {
            "limit": developer_portal.IP_RATE_LIMIT,
            "window_seconds": int(developer_portal.IP_RATE_WINDOW),
            "scope": "ip",
        },
    })


@app.route("/api/developer/agree", methods=["POST"])
@require_auth
@require_csrf
def api_developer_agree():
    try:
        access = developer_portal.accept_policy(_current_user_id())
    except PermissionError as error:
        return error_response(
            "ACCESS_SUSPENDED" if "suspended" in str(error).lower() else "ACCESS_NOT_GRANTED",
            str(error),
            403,
            docs="/developers/policies",
        )
    return jsonify({"ok": True, "access": access})


@app.route("/api/developer/keys")
@require_auth
def api_developer_keys():
    _access, error = _portal_access()
    if error:
        return error
    return jsonify({"keys": developer_portal.list_keys(_current_user_id())})


@app.route("/api/developer/keys", methods=["POST"])
@require_auth
@require_csrf
def api_developer_create_key():
    _access, error = _portal_access()
    if error:
        return error
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response("INVALID_BODY", "A JSON object is required.", 400, docs="/developers/authentication")
    try:
        key, raw_key = developer_portal.create_key(
            _current_user_id(),
            str(payload.get("name") or ""),
            payload.get("scopes"),
            application_id=str(payload.get("application_id") or ""),
        )
    except PermissionError as error:
        return error_response(
            "ACCESS_SUSPENDED" if "suspended" in str(error).lower() else "ACCESS_NOT_GRANTED",
            str(error),
            403,
            docs="/developers/policies",
        )
    except ValueError as error:
        return error_response("INVALID_KEY", str(error), 400, docs="/developers/authentication")
    return jsonify({"ok": True, "key": key, "secret": raw_key}), 201


def _moderation_warn_utils():
    if _discord_bot is None:
        return None
    return _discord_bot.get_cog("ModerationUtils")


def _warn_guild_or_error(guild_id: str, auth: dict):
    """Warning data always needs a reviewed app and a guild both bots share.

    A generic key cannot prove which bot will use the data, so it is rejected
    even if an old grant still lists a warn scope. An app key adds the bot's
    membership: a reviewed app cannot ask for another guild's warnings merely by
    changing a path parameter. ``guilds:cross_server`` is the owner-granted
    exception for highly trusted apps.
    """
    application = auth.get("application")
    if not application:
        return None, error_response(
            "APPLICATION_REQUIRED",
            "Warning access requires a key bound to an approved application.",
            403,
            docs="/developers/applications",
        )
    guild = _guild(guild_id)
    if guild is None:
        return None, error_response(
            "GUILD_NOT_FOUND",
            "Niko is not in this server, or it is unavailable.",
            404,
            docs="/developers/endpoints/warnings",
        )
    if "guilds:cross_server" not in (auth.get("scopes") or []):
        full_app = developer_applications.get_application(str(application.get("id") or ""))
        if not developer_applications.application_in_guild(full_app or {}, guild_id):
            return None, error_response(
                "GUILD_NOT_SHARED",
                "This application's bot does not share that server with Niko.",
                404,
                docs="/developers/endpoints/warnings",
            )
    return guild, None


def _warn_page_args(default_size: int = 100, max_size: int = 500):
    page, page_size, offset = _page_args(default_size=default_size, max_size=max_size)
    if page is None:
        return None, None, None
    return page, page_size, offset


@app.route("/api/v1/guilds/<guild_id>/warns")
@app.route("/v1/guilds/<guild_id>/warns")
@developer_portal.require_api_key("warns:read")
def api_v1_guild_warns(guild_id):
    auth = g.developer_api
    _guild_obj, error = _warn_guild_or_error(guild_id, auth)
    if error:
        return error
    page, page_size, offset = _warn_page_args()
    if page is None:
        return error_response("INVALID_PAGINATION", "Page and page_size must be positive integers.", 400, docs="/developers/endpoints/warnings")
    user_id = (request.args.get("user_id") or "").strip() or None
    if user_id is not None and not user_id.isdigit():
        return error_response("INVALID_USER_ID", "user_id must be a numeric Discord ID.", 400, docs="/developers/endpoints/warnings")
    utils = _moderation_warn_utils()
    if utils is None:
        return error_response(
            "STORAGE_UNAVAILABLE",
            "Warning storage is unavailable.",
            503,
            report=True,
            summary="Moderation cog unavailable while serving /api/v1/guilds/<id>/warns",
            docs="/developers/endpoints/warnings",
        )
    try:
        result = run_on_bot_loop(
            utils.list_warnings(
                int(guild_id),
                user_id=int(user_id) if user_id else None,
                offset=offset,
                limit=page_size,
            )
        )
    except Exception as error_value:
        return error_response(
            "STORAGE_UNAVAILABLE",
            "Warning storage is unavailable.",
            503,
            report=True,
            exception=error_value,
            summary="Warning list failed",
            docs="/developers/endpoints/warnings",
        )
    warns, total = result
    if warns is None:
        return error_response(
            "STORAGE_UNAVAILABLE",
            "Warning storage is unavailable.",
            503,
            report=True,
            summary="Warning list returned no storage",
            docs="/developers/endpoints/warnings",
        )
    return jsonify({
        "guild_id": str(guild_id),
        "warns": warns,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": (total + page_size - 1) // page_size if total else 0,
    })


@app.route("/api/v1/guilds/<guild_id>/members/<user_id>/warns")
@app.route("/v1/guilds/<guild_id>/members/<user_id>/warns")
@developer_portal.require_api_key("warns:read")
def api_v1_member_warns(guild_id, user_id):
    auth = g.developer_api
    _guild_obj, error = _warn_guild_or_error(guild_id, auth)
    if error:
        return error
    if not str(guild_id).isdigit() or not str(user_id).isdigit():
        return error_response("INVALID_ID", "Guild and user IDs must be numeric.", 400, docs="/developers/endpoints/warnings")
    utils = _moderation_warn_utils()
    if utils is None:
        return error_response(
            "STORAGE_UNAVAILABLE",
            "Warning storage is unavailable.",
            503,
            report=True,
            summary="Moderation cog unavailable while serving member warns",
            docs="/developers/endpoints/warnings",
        )
    try:
        warns, total = run_on_bot_loop(
            utils.list_warnings(int(guild_id), user_id=int(user_id), offset=0, limit=500)
        )
    except Exception as error_value:
        return error_response(
            "STORAGE_UNAVAILABLE",
            "Warning storage is unavailable.",
            503,
            report=True,
            exception=error_value,
            summary="Member warning list failed",
            docs="/developers/endpoints/warnings",
        )
    if warns is None:
        return error_response("STORAGE_UNAVAILABLE", "Warning storage is unavailable.", 503, report=True, docs="/developers/endpoints/warnings")
    return jsonify({"guild_id": str(guild_id), "user_id": str(user_id), "warns": warns, "total": total})


@app.route("/api/v1/guilds/<guild_id>/members/<user_id>/warns", methods=["POST"])
@app.route("/v1/guilds/<guild_id>/members/<user_id>/warns", methods=["POST"])
@developer_portal.require_api_key("warns:write")
def api_v1_create_warn(guild_id, user_id):
    auth = g.developer_api
    _guild_obj, error = _warn_guild_or_error(guild_id, auth)
    if error:
        return error
    if not str(guild_id).isdigit() or not str(user_id).isdigit():
        return error_response("INVALID_ID", "Guild and user IDs must be numeric.", 400, docs="/developers/endpoints/warnings")
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response("INVALID_BODY", "A JSON object is required.", 400, docs="/developers/endpoints/warnings")
    reason = " ".join(str(payload.get("reason") or "").split()).strip()
    if not reason:
        return error_response("INVALID_REASON", "A reason is required.", 400, docs="/developers/endpoints/warnings")
    if len(reason) > 1000:
        return error_response("INVALID_REASON", "Reasons must be 1,000 characters or fewer.", 400, docs="/developers/endpoints/warnings")
    application = auth.get("application") or {}
    default_moderator = application.get("bot_user_id") or auth.get("user_id") or "0"
    moderator_raw = str(payload.get("moderator_id") or default_moderator).strip()
    if not moderator_raw.isdigit():
        return error_response("INVALID_MODERATOR_ID", "moderator_id must be a numeric Discord ID.", 400, docs="/developers/endpoints/warnings")
    utils = _moderation_warn_utils()
    if utils is None:
        return error_response("STORAGE_UNAVAILABLE", "Warning storage is unavailable.", 503, report=True, docs="/developers/endpoints/warnings")
    try:
        warn = run_on_bot_loop(utils.add_warn(int(guild_id), int(user_id), int(moderator_raw), reason))
    except Exception as error_value:
        return error_response(
            "WRITE_FAILED",
            "The warning could not be saved.",
            503,
            report=True,
            exception=error_value,
            summary="v1 warning write failed",
            docs="/developers/endpoints/warnings",
        )
    if warn is None:
        return error_response("WRITE_FAILED", "The warning could not be saved.", 503, report=True, docs="/developers/endpoints/warnings")
    return jsonify({"ok": True, "warn": warn}), 201


@app.route("/api/v1/guilds/<guild_id>/warns/<warn_id>", methods=["DELETE"])
@app.route("/v1/guilds/<guild_id>/warns/<warn_id>", methods=["DELETE"])
@developer_portal.require_api_key("warns:write")
def api_v1_delete_warn(guild_id, warn_id):
    auth = g.developer_api
    _guild_obj, error = _warn_guild_or_error(guild_id, auth)
    if error:
        return error
    if not str(guild_id).isdigit() or not str(warn_id).isdigit():
        return error_response("INVALID_ID", "Guild and warning IDs must be numeric.", 400, docs="/developers/endpoints/warnings")
    utils = _moderation_warn_utils()
    if utils is None:
        return error_response("STORAGE_UNAVAILABLE", "Warning storage is unavailable.", 503, report=True, docs="/developers/endpoints/warnings")
    try:
        warn = run_on_bot_loop(utils.delete_warning(int(guild_id), int(warn_id)))
    except Exception as error_value:
        return error_response(
            "WRITE_FAILED",
            "The warning could not be deleted.",
            503,
            report=True,
            exception=error_value,
            summary="v1 warning delete failed",
            docs="/developers/endpoints/warnings",
        )
    if warn is None:
        return error_response("WARN_NOT_FOUND", "Warning not found in that server.", 404, docs="/developers/endpoints/warnings")
    return jsonify({"ok": True, "warn": warn})


@app.route("/api/v1/guilds/<guild_id>/members/<user_id>/warns", methods=["DELETE"])
@app.route("/v1/guilds/<guild_id>/members/<user_id>/warns", methods=["DELETE"])
@developer_portal.require_api_key("warns:write")
def api_v1_clear_warns(guild_id, user_id):
    auth = g.developer_api
    _guild_obj, error = _warn_guild_or_error(guild_id, auth)
    if error:
        return error
    if not str(guild_id).isdigit() or not str(user_id).isdigit():
        return error_response("INVALID_ID", "Guild and user IDs must be numeric.", 400, docs="/developers/endpoints/warnings")
    utils = _moderation_warn_utils()
    if utils is None:
        return error_response("STORAGE_UNAVAILABLE", "Warning storage is unavailable.", 503, report=True, docs="/developers/endpoints/warnings")
    try:
        cleared = run_on_bot_loop(utils.clear_warnings(int(guild_id), int(user_id)))
    except Exception as error_value:
        return error_response(
            "WRITE_FAILED",
            "The warnings could not be cleared.",
            503,
            report=True,
            exception=error_value,
            summary="v1 warning clear failed",
            docs="/developers/endpoints/warnings",
        )
    return jsonify({"ok": True, "guild_id": str(guild_id), "user_id": str(user_id), "cleared": int(cleared or 0)})


@app.route("/api/developer/keys/<key_id>", methods=["DELETE"])
@require_auth
@require_csrf
def api_developer_revoke_key(key_id):
    access, error = _portal_access()
    if error:
        return error
    if not developer_portal.revoke_key(_current_user_id(), key_id, allow_any=access["is_owner"]):
        return error_response("KEY_NOT_FOUND", "Key not found.", 404, docs="/developers/authentication")
    return jsonify({"ok": True})


@app.route("/api/developer/logs")
@require_auth
def api_developer_logs():
    access, error = _portal_access()
    if error:
        return error
    all_users = access["is_owner"] and request.args.get("all") == "1"
    limit = request.args.get("limit", "100")
    return jsonify({
        "entries": developer_portal.usage_rows(
            _current_user_id(),
            limit=limit,
            all_users=all_users,
        ),
        "scope": "all" if all_users else "self",
    })


# ── Portal: owner access management ──────────────────────────────────────────

@app.route("/api/developer/access")
@require_auth
def api_developer_access():
    error = _owner_error()
    if error:
        return error
    return jsonify(developer_portal.access_rows())


@app.route("/api/developer/access/<user_id>", methods=["PUT"])
@require_auth
@require_csrf
def api_developer_grant_access(user_id):
    error = _owner_error()
    if error:
        return error
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response("INVALID_BODY", "A JSON object is required.", 400, docs="/developers/authentication")
    try:
        access = developer_portal.grant_access(
            user_id,
            payload.get("scopes"),
            enabled=bool(payload.get("enabled", True)),
            notes=str(payload.get("notes") or ""),
            actor_id=_current_user_id(),
            identity=_identity(user_id),
        )
    except ValueError as error:
        return error_response("INVALID_ACCESS_GRANT", str(error), 400, docs="/developers/authentication")
    return jsonify({"ok": True, "access": access})


@app.route("/api/developer/access/<user_id>", methods=["DELETE"])
@require_auth
@require_csrf
def api_developer_revoke_access(user_id):
    error = _owner_error()
    if error:
        return error
    try:
        removed = developer_portal.revoke_access(user_id, actor_id=_current_user_id())
    except ValueError as error:
        return error_response("INVALID_ACCESS_GRANT", str(error), 400, docs="/developers/authentication")
    if not removed:
        return error_response("ACCESS_NOT_FOUND", "Developer access not found.", 404, docs="/developers/authentication")
    return jsonify({"ok": True})


# ── Portal: owner appeal review ──────────────────────────────────────────────

@app.route("/api/developer/appeals")
@require_auth
def api_developer_appeals():
    error = _owner_error()
    if error:
        return error
    return jsonify({"appeals": developer_portal.appeal_rows()})


@app.route("/api/developer/appeals/<appeal_id>/review", methods=["POST"])
@require_auth
@require_csrf
def api_developer_review_appeal(appeal_id):
    error = _owner_error()
    if error:
        return error
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response("INVALID_BODY", "A JSON object is required.", 400, docs="/developers/policies")
    status = str(payload.get("status") or "").strip().lower()
    if status not in {"approved", "denied"}:
        return error_response("INVALID_APPEAL_DECISION", "Choose approved or denied.", 400, docs="/developers/policies")
    try:
        appeal = developer_portal.review_appeal(
            appeal_id,
            status,
            note=str(payload.get("note") or ""),
            actor_id=_current_user_id(),
        )
    except ValueError as error_value:
        return error_response("INVALID_APPEAL_DECISION", str(error_value), 400, docs="/developers/policies")
    if appeal is None:
        return error_response("APPEAL_NOT_PENDING", "This appeal is no longer pending.", 409, docs="/developers/policies")
    return jsonify({
        "ok": True,
        "appeal": appeal,
        "access": developer_portal.developer_access(appeal.get("user_id") or ""),
    })


# ── Versioned public API ─────────────────────────────────────────────────────

def _economy_leaderboard():
    page, page_size, offset = _page_args()
    if page is None:
        return error_response("INVALID_PAGINATION", "Page and page_size must be positive integers.", 400)
    result = get_runtime_leaderboard_page(offset, page_size)
    if result is None:
        return error_response(
            "UPSTREAM_UNAVAILABLE",
            "The economy leaderboard is temporarily unavailable.",
            503,
            report=True,
            summary="Economy leaderboard unavailable while serving /api/v1/economy/leaderboard",
        )
    rows, total = result
    public_ids = {row["user_id"] for row in rows if not row.get("leaderboard_private")}
    identities = _resolve_leaderboard_identities(public_ids)
    entries = []
    for rank, row in enumerate(rows, start=offset + 1):
        user_id = row["user_id"]
        visible = user_id in public_ids
        identity = identities.get(user_id) if visible else None
        entries.append({
            "key": leaderboard_cache.profile_key(user_id),
            **({"user_id": user_id} if visible else {}),
            "rank": rank,
            "net_worth": row["net_worth"],
            "private": bool(row.get("leaderboard_private")),
            "username": identity.get("username") if identity else None,
            "display_name": identity.get("display_name") if identity else None,
            "avatar_url": identity.get("avatar_url") if identity else None,
        })
    return jsonify({
        "entries": entries,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": (total + page_size - 1) // page_size,
    })


@app.route("/api/v1/economy/leaderboard")
@app.route("/v1/economy/leaderboard")
@developer_portal.require_api_key("economy:read")
def api_v1_economy_leaderboard():
    return _economy_leaderboard()


def _guild_leaderboard(guild_id: str):
    guild = _guild(guild_id)
    if guild is None:
        return error_response("GUILD_NOT_FOUND", "Niko is not in this server, or it is unavailable.", 404)
    page, page_size, offset = _page_args(default_size=25, max_size=100)
    if page is None:
        return error_response("INVALID_PAGINATION", "Page and page_size must be positive integers.", 400)
    result = get_runtime_guild_level_page(guild_id, offset, page_size)
    if result is None:
        return error_response(
            "UPSTREAM_UNAVAILABLE",
            "This server's leaderboard is temporarily unavailable.",
            503,
            report=True,
            summary="Guild level leaderboard unavailable while serving /api/v1/guilds/<id>/levels",
        )
    rows, total = result
    user_ids = {row["user_id"] for row in rows}
    identities = get_runtime_member_metadata(guild_id, user_ids)
    missing = user_ids - set(identities)
    if missing:
        identities.update(_resolve_leaderboard_identities(missing))
    icon = getattr(guild, "icon", None)
    entries = []
    for rank, row in enumerate(rows, start=offset + 1):
        identity = identities.get(row["user_id"]) or {}
        entries.append({
            "key": leaderboard_cache.profile_key(row["user_id"]),
            "user_id": row["user_id"],
            "rank": rank,
            "level": row["level"],
            "xp": row["xp"],
            "xp_for_next": level_xp_for_next(row["level"]),
            "username": identity.get("username"),
            "display_name": identity.get("display_name"),
            "avatar_url": identity.get("avatar_url"),
        })
    return jsonify({
        "guild": {
            "id": str(guild.id),
            "name": guild.name,
            "icon_url": str(icon.url) if icon is not None else None,
            "member_count": int(getattr(guild, "member_count", 0) or len(getattr(guild, "members", []) or [])),
        },
        "leveling_enabled": bool(get_runtime_level_config(guild_id).get("xp_enabled", True)),
        "entries": entries,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": (total + page_size - 1) // page_size,
    })


@app.route("/api/v1/guilds/<guild_id>/levels")
@app.route("/api/v1/levels/<guild_id>")
@app.route("/v1/guilds/<guild_id>/levels")
@app.route("/v1/levels/<guild_id>")
@developer_portal.require_api_key("levels:read")
def api_v1_guild_levels(guild_id):
    return _guild_leaderboard(guild_id)


@app.route("/api/v1/users/<user_id>")
@app.route("/v1/users/<user_id>")
@developer_portal.require_api_key("users:read")
def api_v1_user(user_id):
    if not str(user_id).isdigit() or len(str(user_id)) > 22:
        return error_response("INVALID_USER_ID", "A valid Discord user ID is required.", 400)
    if _discord_bot is None:
        return error_response(
            "UPSTREAM_UNAVAILABLE",
            "Discord profile lookup is unavailable.",
            503,
            report=True,
            summary="Discord bot unavailable while serving /api/v1/users/<id>",
        )
    identity = _identity(user_id)
    if not identity.get("username") and not identity.get("display_name"):
        return error_response("USER_NOT_FOUND", "Discord user not found.", 404)
    return jsonify({"user": {"id": str(user_id), **identity}})


@app.route("/api/v1/users/<user_id>/economy")
@app.route("/v1/users/<user_id>/economy")
@developer_portal.require_api_key("economy:read")
def api_v1_user_economy(user_id):
    if not str(user_id).isdigit() or len(str(user_id)) > 22:
        return error_response("INVALID_USER_ID", "A valid Discord user ID is required.", 400)
    rows = get_runtime_economy_rows()
    if rows is None:
        return error_response(
            "UPSTREAM_UNAVAILABLE",
            "Economy data is temporarily unavailable.",
            503,
            report=True,
            summary="Economy rows unavailable while serving /api/v1/users/<id>/economy",
        )
    row = next((item for item in rows if str(item.get("user_id")) == str(user_id)), None)
    if row is None:
        return error_response("RECORD_NOT_FOUND", "No economy profile exists for that user.", 404)
    return jsonify({
        "user_id": str(user_id),
        "balance": row.get("balance", 0),
        "bank": row.get("bank", 0),
        "net_worth": row.get("net_worth", 0),
        "level": row.get("level", 0),
        "job": row.get("job"),
        "daily_streak": row.get("daily_streak", 0),
        "achievements": row.get("achievements", 0),
        "total_earned": row.get("total_earned", 0),
        "leaderboard_private": bool(row.get("leaderboard_private")),
    })


def _read_level(guild_id: str, user_id: str) -> dict | None:
    if _discord_bot is not None and getattr(_discord_bot, "cxn", None) is not None:
        async def read():
            return await _discord_bot.cxn.fetchrow(
                "SELECT xp, level FROM levels WHERE guild_id = $1 AND user_id = $2",
                int(guild_id),
                int(user_id),
            )

        try:
            row = run_on_bot_loop(read())
        except Exception:
            return None
    else:
        conn = sqlite_connect()
        if conn is None:
            return None
        try:
            cursor = conn.execute(
                "SELECT xp, level FROM levels WHERE guild_id = ? AND user_id = ?",
                (int(guild_id), int(user_id)),
            )
            row = cursor.fetchone()
        except Exception:
            return None
        finally:
            conn.close()
        if row is None:
            return None
        return {"xp": int(row[0] or 0), "level": int(row[1] or 0)}
    if row is None:
        return None
    return {"xp": int(row.get("xp") or 0), "level": int(row.get("level") or 0)}


@app.route("/api/v1/guilds/<guild_id>/members/<user_id>/level")
@app.route("/v1/guilds/<guild_id>/members/<user_id>/level")
@developer_portal.require_api_key("levels:read")
def api_v1_member_level(guild_id, user_id):
    if not str(guild_id).isdigit() or not str(user_id).isdigit():
        return error_response("INVALID_ID", "Guild and user IDs must be numeric.", 400)
    if _guild(guild_id) is None:
        return error_response("GUILD_NOT_FOUND", "Niko is not in this server, or it is unavailable.", 404)
    row = _read_level(guild_id, user_id)
    if row is None:
        return jsonify({"guild_id": str(guild_id), "user_id": str(user_id), "xp": 0, "level": 0})
    return jsonify({
        "guild_id": str(guild_id),
        "user_id": str(user_id),
        "xp": row["xp"],
        "level": row["level"],
        "xp_for_next": level_xp_for_next(row["level"]),
    })


@app.route("/api/v1/guilds/<guild_id>/members/<user_id>/level", methods=["PUT"])
@app.route("/v1/guilds/<guild_id>/members/<user_id>/level", methods=["PUT"])
@developer_portal.require_api_key("levels:write")
def api_v1_write_member_level(guild_id, user_id):
    if not str(guild_id).isdigit() or not str(user_id).isdigit():
        return error_response("INVALID_ID", "Guild and user IDs must be numeric.", 400)
    if _guild(guild_id) is None:
        return error_response("GUILD_NOT_FOUND", "Niko is not in this server, or it is unavailable.", 404)
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response("INVALID_BODY", "A JSON object is required.", 400, docs="/developers/endpoints/leveling")
    try:
        xp = int(payload.get("xp"))
        level = int(payload.get("level"))
    except (TypeError, ValueError):
        return error_response("INVALID_BODY", "xp and level must be integers.", 400, docs="/developers/endpoints/leveling")
    if xp < 0 or level < 0 or xp > 10**15 or level > 10**9:
        return error_response("INVALID_RANGE", "xp and level are out of range.", 400, docs="/developers/endpoints/leveling")

    leveling = _discord_bot.get_cog("Leveling") if _discord_bot is not None else None
    try:
        if leveling is not None and hasattr(leveling, "_save_user_data"):
            run_on_bot_loop(leveling._save_user_data(guild_id, user_id, xp, level))
        elif _discord_bot is not None and getattr(_discord_bot, "cxn", None) is not None:
            async def write():
                await _discord_bot.cxn.execute(
                    "INSERT OR REPLACE INTO levels (guild_id, user_id, xp, level) VALUES ($1, $2, $3, $4)",
                    int(guild_id),
                    int(user_id),
                    xp,
                    level,
                )

            run_on_bot_loop(write())
        else:
            return error_response(
                "STORAGE_UNAVAILABLE",
                "Leveling storage is unavailable.",
                503,
                report=True,
                summary="Leveling storage unavailable while handling a v1 level write",
                docs="/developers/endpoints/leveling",
            )
    except Exception as error:
        return error_response(
            "WRITE_FAILED",
            "The level could not be saved.",
            503,
            report=True,
            exception=error,
            summary="v1 level write failed",
            docs="/developers/endpoints/leveling",
        )
    return jsonify({
        "ok": True,
        "guild_id": str(guild_id),
        "user_id": str(user_id),
        "xp": xp,
        "level": level,
        "xp_for_next": level_xp_for_next(level),
    })


@app.route("/api/v1/blacklist")
@app.route("/v1/blacklist")
@developer_portal.require_api_key("blacklist:read")
def api_v1_blacklist():
    auth = g.developer_api
    if not auth.get("application"):
        return error_response(
            "APPLICATION_REQUIRED",
            "Blacklist access requires a key bound to a trusted application.",
            403,
            docs="/developers/endpoints/blacklist",
        )
    try:
        manager = _load_blacklist_manager()
    except Exception as error:
        return error_response(
            "UPSTREAM_UNAVAILABLE",
            "Blacklist data is temporarily unavailable.",
            503,
            report=True,
            exception=error,
            summary="Blacklist manager unavailable while serving /api/v1/blacklist",
            docs="/developers/endpoints/blacklist",
        )
    kind = (request.args.get("type") or "all").strip().lower()
    if kind not in {"all", "users", "guilds"}:
        return error_response("INVALID_TYPE", "type must be users, guilds, or all.", 400, docs="/developers/endpoints/blacklist")
    payload = {}
    if kind in {"all", "users"}:
        payload["users"] = [
            {
                "id": str(entry.get("id")),
                "reason": entry.get("reason"),
                "added_by": str(entry["added_by"]) if entry.get("added_by") else None,
                "timestamp": entry.get("timestamp"),
                "expires_at": entry.get("expires_at"),
            }
            for entry in manager.blacklist.get("users", [])
        ]
    if kind in {"all", "guilds"}:
        payload["guilds"] = [
            {
                "id": str(entry.get("id")),
                "reason": entry.get("reason"),
                "added_by": str(entry["added_by"]) if entry.get("added_by") else None,
                "timestamp": entry.get("timestamp"),
            }
            for entry in manager.blacklist.get("guilds", [])
        ]
    return jsonify(payload)


@app.route("/api/v1/blacklist", methods=["POST"])
@app.route("/v1/blacklist", methods=["POST"])
@developer_portal.require_api_key("blacklist:write")
def api_v1_write_blacklist():
    auth = g.developer_api
    if not auth.get("application"):
        return error_response(
            "APPLICATION_REQUIRED",
            "Blacklist access requires a key bound to a trusted application.",
            403,
            docs="/developers/endpoints/blacklist",
        )
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response("INVALID_BODY", "A JSON object is required.", 400, docs="/developers/endpoints/blacklist")
    kind = str(payload.get("type") or "").strip().lower()
    action = str(payload.get("action") or "").strip().lower()
    entry_id = str(payload.get("id") or "").strip()
    if kind not in {"user", "guild"}:
        return error_response("INVALID_TYPE", "type must be user or guild.", 400, docs="/developers/endpoints/blacklist")
    if action not in {"add", "remove"}:
        return error_response("INVALID_ACTION", "action must be add or remove.", 400, docs="/developers/endpoints/blacklist")
    if not entry_id.isdigit():
        return error_response("INVALID_ID", "The blacklist id must be a numeric Discord ID.", 400, docs="/developers/endpoints/blacklist")
    reason = " ".join(str(payload.get("reason") or "").split()).strip()
    if action == "add" and not reason:
        return error_response("INVALID_REASON", "A reason is required when adding a blacklist entry.", 400, docs="/developers/endpoints/blacklist")
    if len(reason) > 1000:
        return error_response("INVALID_REASON", "Reasons must be 1,000 characters or fewer.", 400, docs="/developers/endpoints/blacklist")
    expires_at = payload.get("expires_at")
    if expires_at is not None:
        try:
            expires_at = float(expires_at)
        except (TypeError, ValueError):
            return error_response("INVALID_EXPIRY", "expires_at must be a Unix timestamp.", 400, docs="/developers/endpoints/blacklist")
        if expires_at <= time.time():
            return error_response("INVALID_EXPIRY", "expires_at must be in the future.", 400, docs="/developers/endpoints/blacklist")
    try:
        manager = _load_blacklist_manager()
    except Exception as error_value:
        return error_response(
            "UPSTREAM_UNAVAILABLE",
            "Blacklist data is temporarily unavailable.",
            503,
            report=True,
            exception=error_value,
            summary="Blacklist manager unavailable while serving a blacklist write",
            docs="/developers/endpoints/blacklist",
        )
    application = auth.get("application") or {}
    actor_raw = application.get("bot_user_id") or auth.get("user_id") or "0"
    try:
        actor_id = int(actor_raw)
    except (TypeError, ValueError):
        actor_id = None
    try:
        if kind == "user":
            if action == "add":
                changed = run_on_bot_loop(manager.add_user(int(entry_id), reason=reason, added_by=actor_id, expires_at=expires_at))
            else:
                changed = run_on_bot_loop(manager.remove_user(int(entry_id)))
        else:
            if action == "add":
                # An API write records the entry; destructive per-feature
                # lockdown stays a deliberate owner action in the dashboard.
                changed = run_on_bot_loop(manager.add_guild(int(entry_id), reason=reason, added_by=actor_id, bot=_discord_bot, lockdown=False))
            else:
                changed = run_on_bot_loop(manager.remove_guild(int(entry_id), bot=_discord_bot, restore=True))
    except Exception as error_value:
        return error_response(
            "WRITE_FAILED",
            "The blacklist entry could not be saved.",
            503,
            report=True,
            exception=error_value,
            summary="v1 blacklist write failed",
            docs="/developers/endpoints/blacklist",
        )
    return jsonify({"ok": True, "changed": bool(changed), "type": kind, "action": action, "id": entry_id})


# Imported lazily so importing the route module never reaches into public
# routes' snapshot before they are loaded.
def _resolve_leaderboard_identities(user_ids):
    from .public_routes import _resolve_leaderboard_identities as resolve

    return resolve(user_ids)
