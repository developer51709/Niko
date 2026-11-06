"""Developer portal routes for reviewed bot applications and webhooks."""

from __future__ import annotations

import json

from flask import jsonify, request, send_file

from .. import developer_applications, developer_portal, developer_webhooks, runtime
from .. import server as _server
from ..api_errors import error_response

app = _server.app
require_auth = _server.require_auth
require_csrf = _server.require_csrf


def _current_user_id() -> str:
    return developer_portal.session_user_id()


def _owner() -> bool:
    return bool(_server._is_owner())


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


def _request_scopes() -> list[str]:
    """Read repeated form fields or a single JSON array from multipart input."""
    raw = request.form.getlist("scopes")
    if len(raw) == 1:
        try:
            parsed = json.loads(raw[0])
        except (TypeError, ValueError):
            parsed = None
        if isinstance(parsed, list):
            raw = [str(item) for item in parsed]
    return [str(item).strip() for item in raw if str(item).strip()]


def _form_text(name: str) -> str:
    return str(request.form.get(name) or "").strip()


def _bot_identity(bot_user_id: str) -> dict:
    niko_bot = runtime._discord_bot
    try:
        if niko_bot is not None and str(getattr(niko_bot.user, "id", "")) == str(bot_user_id):
            raise ValueError("Niko itself cannot be registered as a third-party application.")
    except ValueError:
        raise
    except Exception:
        pass
    return developer_portal.resolve_identity(bot_user_id)


def _app_for_current_user(application_id: str):
    application = developer_applications.get_application(application_id)
    if not isinstance(application, dict):
        return None, error_response(
            "APPLICATION_NOT_FOUND",
            "Application not found.",
            404,
            docs="/developers/applications",
        )
    if str(application.get("owner_id")) != _current_user_id() and not _owner():
        return None, error_response(
            "APPLICATION_FORBIDDEN",
            "This application belongs to another developer.",
            403,
            docs="/developers/applications",
        )
    return application, None


@app.route("/api/developer/applications")
@require_auth
def api_developer_applications():
    access, error = _portal_access()
    if error:
        return error
    standard = [
        scope for scope in developer_portal.scope_options()
        if not scope.get("restricted") and scope["key"] in access["scopes"]
    ]
    return jsonify({
        "applications": developer_applications.applications_for_user(_current_user_id()),
        "scopes": standard,
        "restricted_scopes": [
            scope for scope in developer_portal.scope_options()
            if scope.get("restricted")
        ],
        "events": [
            {"key": key, **value}
            for key, value in developer_applications.WEBHOOK_EVENTS.items()
        ],
        "policy_accepted": bool(access["policy_accepted"]),
    })


@app.route("/api/developer/applications", methods=["POST"])
@require_auth
@require_csrf
def api_developer_create_application():
    access, error = _portal_access()
    if error:
        return error
    if not access["policy_accepted"]:
        return error_response(
            "POLICY_REQUIRED",
            "Accept the developer guidelines before submitting an application.",
            403,
            docs="/developers/policies",
        )
    upload = request.files.get("screenshot")
    if upload is None:
        return error_response(
            "SCREENSHOT_REQUIRED",
            "Upload a screenshot of the Discord application overview page.",
            400,
            docs="/developers/applications",
        )
    raw = upload.stream.read(developer_applications.MAX_SCREENSHOT_BYTES + 1)
    if len(raw) > developer_applications.MAX_SCREENSHOT_BYTES:
        return error_response("SCREENSHOT_TOO_LARGE", "Screenshots must be 8 MB or smaller.", 413, docs="/developers/applications")
    content_type = developer_applications.detect_image_type(raw, upload.mimetype)
    if content_type is None:
        return error_response(
            "SCREENSHOT_INVALID",
            "Upload a PNG, JPEG, GIF, or WebP screenshot.",
            400,
            docs="/developers/applications",
        )
    standard = [
        scope["key"] for scope in developer_portal.scope_options()
        if not scope.get("restricted") and scope["key"] in access["scopes"]
    ]
    requested = _request_scopes()
    try:
        bot_identity = _bot_identity(_form_text("bot_user_id"))
    except ValueError as error_value:
        return error_response("INVALID_BOT_ID", str(error_value), 400, docs="/developers/applications")
    try:
        application = developer_applications.create_or_resubmit(
            _current_user_id(),
            name=_form_text("name"),
            description=_form_text("description"),
            bot_user_id=_form_text("bot_user_id"),
            requested_scopes=requested,
            allowed_scopes=standard,
            bot_identity=bot_identity,
            owner_identity=developer_portal.resolve_identity(_current_user_id()),
            screenshot=raw,
            screenshot_content_type=content_type,
        )
    except FileExistsError as error_value:
        return error_response("APPLICATION_EXISTS", str(error_value), 409, docs="/developers/applications")
    except ValueError as error_value:
        return error_response("INVALID_APPLICATION", str(error_value), 400, docs="/developers/applications")
    return jsonify({"ok": True, "application": application}), 201


@app.route("/api/developer/applications/<application_id>", methods=["DELETE"])
@require_auth
@require_csrf
def api_developer_delete_application(application_id):
    _access, error = _portal_access()
    if error:
        return error
    try:
        removed = developer_applications.delete_application(application_id, _current_user_id())
    except ValueError as error_value:
        return error_response("APPLICATION_LOCKED", str(error_value), 409, docs="/developers/applications")
    if not removed:
        return error_response("APPLICATION_NOT_FOUND", "Application not found.", 404, docs="/developers/applications")
    return jsonify({"ok": True})


@app.route("/api/developer/applications/<application_id>/screenshot")
@require_auth
def api_developer_application_screenshot(application_id):
    application, error = _app_for_current_user(application_id)
    if error:
        return error
    shot = developer_applications.screenshot_path(application_id)
    if shot is None:
        return error_response("SCREENSHOT_NOT_FOUND", "Screenshot not found.", 404, docs="/developers/applications")
    path, content_type = shot
    return send_file(path, mimetype=content_type, max_age=0, conditional=True)


@app.route("/api/developer/applications/<application_id>/webhook", methods=["PUT"])
@require_auth
@require_csrf
def api_developer_configure_webhook(application_id):
    access, error = _portal_access()
    if error:
        return error
    application = developer_applications.get_application(application_id)
    if not isinstance(application, dict):
        return error_response("APPLICATION_NOT_FOUND", "Application not found.", 404, docs="/developers/applications")
    if str(application.get("owner_id")) != _current_user_id():
        return error_response("APPLICATION_FORBIDDEN", "This application belongs to another developer.", 403, docs="/developers/applications")
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response("INVALID_BODY", "A JSON object is required.", 400, docs="/developers/applications")
    try:
        webhook = developer_applications.configure_webhook(
            application_id,
            _current_user_id(),
            url=payload.get("url"),
            enabled=bool(payload.get("enabled", True)),
            events=payload.get("events"),
        )
    except PermissionError as error_value:
        return error_response("APPLICATION_NOT_APPROVED", str(error_value), 403, docs="/developers/applications")
    except LookupError as error_value:
        return error_response("APPLICATION_NOT_FOUND", str(error_value), 404, docs="/developers/applications")
    except ValueError as error_value:
        return error_response("INVALID_WEBHOOK", str(error_value), 400, docs="/developers/applications")
    return jsonify({"ok": True, "webhook": webhook})


@app.route("/api/developer/applications/<application_id>/webhook/test", methods=["POST"])
@require_auth
@require_csrf
def api_developer_test_webhook(application_id):
    _access, error = _portal_access()
    if error:
        return error
    application = developer_applications.get_application(application_id)
    if not isinstance(application, dict):
        return error_response("APPLICATION_NOT_FOUND", "Application not found.", 404, docs="/developers/applications")
    if str(application.get("owner_id")) != _current_user_id():
        return error_response("APPLICATION_FORBIDDEN", "This application belongs to another developer.", 403, docs="/developers/applications")
    ok, status, message = developer_webhooks.send_test_event(application_id)
    if not ok:
        return error_response(
            "WEBHOOK_DELIVERY_FAILED",
            message or "The test delivery failed.",
            502,
            docs="/developers/applications",
            details={"status": status},
        )
    return jsonify({"ok": True, "status": status})


@app.route("/api/developer/applications/review")
@require_auth
def api_developer_application_review_queue():
    if not _owner():
        return error_response("OWNER_ONLY", "Only the bot owner can review applications.", 403, docs="/developers/applications")
    rows = []
    for application in developer_applications.review_rows():
        rows.append({
            **application,
            "shared_guild_count": developer_applications.shared_guild_count(application),
        })
    return jsonify({
        "applications": rows,
        "scopes": developer_portal.scope_options(),
        "events": [
            {"key": key, **value}
            for key, value in developer_applications.WEBHOOK_EVENTS.items()
        ],
    })


@app.route("/api/developer/applications/<application_id>/review", methods=["POST"])
@require_auth
@require_csrf
def api_developer_review_application(application_id):
    if not _owner():
        return error_response("OWNER_ONLY", "Only the bot owner can review applications.", 403, docs="/developers/applications")
    application = developer_applications.get_application(application_id)
    if not isinstance(application, dict):
        return error_response("APPLICATION_NOT_FOUND", "Application not found.", 404, docs="/developers/applications")
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response("INVALID_BODY", "A JSON object is required.", 400, docs="/developers/applications")
    status = str(payload.get("status") or "").strip().lower()
    if status not in {"approved", "denied"}:
        return error_response("INVALID_DECISION", "Choose approved or denied.", 400, docs="/developers/applications")
    owner_access = developer_portal.developer_access(str(application.get("owner_id") or ""))
    try:
        reviewed = developer_applications.review_application(
            application_id,
            status,
            scopes=payload.get("scopes"),
            note=str(payload.get("note") or ""),
            actor_id=_current_user_id(),
            allowed_scopes=owner_access["scopes"],
        )
    except ValueError as error_value:
        return error_response("INVALID_APPLICATION_REVIEW", str(error_value), 400, docs="/developers/applications")
    if reviewed is None:
        return error_response("APPLICATION_NOT_FOUND", "Application not found.", 404, docs="/developers/applications")
    return jsonify({"ok": True, "application": reviewed})
