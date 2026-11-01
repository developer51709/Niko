"""Hidden staff mailbox APIs: the owner's and Head Admins' own-domain email.

The page behind these routes is never linked publicly. Reading is scoped by the
staff role (see ``webapp.staff_email.MAILBOXES``); sending is CSRF-protected and
the inbound webhook is the one route here that answers a machine instead of a
signed-in staff member.
"""

import logging

from flask import jsonify, request, session

from .. import server as _server
from .. import staff_email

app = _server.app
require_auth = _server.require_auth
require_csrf = _server.require_csrf
_current_staff_role = _server._current_staff_role
_discord_bot = None
log = logging.getLogger(__name__)


def _require_mailbox_role():
    role = _current_staff_role()
    if not role or not staff_email.mailboxes_for(role):
        return None, (jsonify({"error": "The staff mailbox is restricted to the owner and Head Admins."}), 403)
    return role, None


@app.route("/api/staff/email")
@require_auth
def api_staff_email_inbox():
    role, error = _require_mailbox_role()
    if error:
        return error
    mailboxes = staff_email.mailboxes_for(role)
    try:
        messages = staff_email.list_messages(role)
    except staff_email.StaffEmailError as exc:
        return jsonify({"error": str(exc)}), 503
    return jsonify({
        "role": role,
        "domain": staff_email.email_domain(),
        "mailboxes": mailboxes,
        "messages": messages,
        "configured": staff_email.provider_configured(),
        "missing": staff_email.missing_settings(),
        "unread": sum(1 for message in messages if message["direction"] == "inbound" and not message["read"]),
    })


@app.route("/api/staff/email/<message_id>")
@require_auth
def api_staff_email_message(message_id):
    role, error = _require_mailbox_role()
    if error:
        return error
    try:
        message = staff_email.open_message(role, message_id)
    except staff_email.StaffEmailError as exc:
        return jsonify({"error": str(exc)}), 503
    if message is None:
        return jsonify({"error": "That message is not in your mailbox."}), 404
    return jsonify({"message": message})


@app.route("/api/staff/email/<message_id>/read", methods=["POST"])
@require_auth
@require_csrf
def api_staff_email_mark_read(message_id):
    role, error = _require_mailbox_role()
    if error:
        return error
    try:
        message = staff_email.open_message(role, message_id)
    except staff_email.StaffEmailError as exc:
        return jsonify({"error": str(exc)}), 503
    if message is None:
        return jsonify({"error": "That message is not in your mailbox."}), 404
    return jsonify({"ok": True, "read": True})


@app.route("/api/staff/email/send", methods=["POST"])
@require_auth
@require_csrf
def api_staff_email_send():
    role, error = _require_mailbox_role()
    if error:
        return error
    data = request.get_json(silent=True) or {}
    try:
        user_id = session.get("user", {}).get("id")
        message = staff_email.send_message(
            role=role,
            mailbox=str(data.get("mailbox") or ""),
            recipient=str(data.get("to") or ""),
            subject=str(data.get("subject") or ""),
            body=str(data.get("body") or ""),
            staff_user_id=int(user_id) if str(user_id or "").isdigit() else None,
        )
    except staff_email.StaffEmailUnavailable as exc:
        return jsonify({"error": str(exc)}), 503
    except staff_email.StaffEmailError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"ok": True, "message": message})


@app.route("/api/staff/email/inbound", methods=["POST"])
def api_staff_email_inbound():
    """Mailgun route delivery. Signed by the provider, not by a session.

    Mailgun posts a form (multipart once attachments are involved), so the
    message and the signature fields arrive together in ``request.form``.
    """
    payload = request.form if request.form else (request.get_json(silent=True) or {})
    if not staff_email.inbound_authorized(payload):
        return jsonify({"error": "Invalid delivery signature."}), 403
    try:
        result = staff_email.receive_webhook(payload)
    except staff_email.StaffEmailUnavailable as exc:
        # The provider retries, and the mail is not lost at its end.
        log.warning("StaffEmail: inbound delivery could not be stored: %s", exc)
        return jsonify({"error": str(exc)}), 503
    except staff_email.StaffEmailError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"ok": True, **result})
