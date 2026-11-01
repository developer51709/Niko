"""Hidden staff mailbox APIs: Niko's own-domain email.

The page behind these routes is never linked publicly. Reading is scoped by the
staff role and by the address itself (see ``webapp.staff_email``): the owner
holds every shared mailbox, a Head Admin the admin and support ones, the support
team ``support@``, and every staff member also holds a private address minted
from their Discord username that nobody else can read. Sending is CSRF-protected.
The inbound delivery and delivery-event webhooks are the two routes here that
answer a machine instead of a signed-in staff member, and both authenticate by
Mailgun's signature alone.
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
    user_id = str(session.get("user", {}).get("id") or "").strip()
    if not role:
        return None, None, (jsonify({"error": "The staff mailbox is restricted to Niko staff."}), 403)
    try:
        # Mint an address for a new staff member, and retire the one a
        # suspension, demotion, or rename left behind. A sync that fails must
        # not hide the shared mailboxes that already exist.
        staff_email.sync_addresses()
    except Exception:
        log.warning("StaffEmail: address sync failed before serving the mailbox", exc_info=True)
    if not staff_email.mailboxes_for(role, user_id):
        return None, None, (jsonify({"error": "No mailbox is assigned to your staff role."}), 403)
    return role, user_id, None


@app.route("/api/staff/email")
@require_auth
def api_staff_email_inbox():
    role, user_id, error = _require_mailbox_role()
    if error:
        return error
    mailboxes = staff_email.mailboxes_for(role, user_id)
    try:
        messages = staff_email.list_messages(role, user_id)
    except staff_email.StaffEmailError as exc:
        return jsonify({"error": str(exc)}), 503
    return jsonify({
        "role": role,
        "domain": staff_email.email_domain(),
        "mailboxes": mailboxes,
        "messages": messages,
        "configured": staff_email.provider_configured(),
        "missing": staff_email.missing_settings(),
        "support_address": staff_email.support_address(),
        "unread": sum(1 for message in messages if message["direction"] == "inbound" and not message["read"]),
    })


@app.route("/api/staff/email/<message_id>")
@require_auth
def api_staff_email_message(message_id):
    role, user_id, error = _require_mailbox_role()
    if error:
        return error
    try:
        message = staff_email.open_message(role, message_id, user_id)
    except staff_email.StaffEmailError as exc:
        return jsonify({"error": str(exc)}), 503
    if message is None:
        return jsonify({"error": "That message is not in your mailbox."}), 404
    return jsonify({"message": message})


@app.route("/api/staff/email/<message_id>/read", methods=["POST"])
@require_auth
@require_csrf
def api_staff_email_mark_read(message_id):
    role, user_id, error = _require_mailbox_role()
    if error:
        return error
    try:
        message = staff_email.open_message(role, message_id, user_id)
    except staff_email.StaffEmailError as exc:
        return jsonify({"error": str(exc)}), 503
    if message is None:
        return jsonify({"error": "That message is not in your mailbox."}), 404
    return jsonify({"ok": True, "read": True})


@app.route("/api/staff/email/send", methods=["POST"])
@require_auth
@require_csrf
def api_staff_email_send():
    """Send a composed mail, with formatting and optional attachments.

    An attachment makes this a multipart request, so the draft is read from
    whichever body shape arrived. The files are handed straight to the provider;
    only their names and sizes are kept with the copy in the inbox.
    """
    role, user_id, error = _require_mailbox_role()
    if error:
        return error
    if request.mimetype == "multipart/form-data":
        # The composer always sends multipart, with or without attached files.
        data = request.form
        uploads = [
            {
                "filename": upload.filename,
                "content": upload.read(staff_email.MAX_ATTACHMENT_BYTES + 1),
                "content_type": upload.mimetype,
            }
            for upload in request.files.getlist("attachments")
        ]
    else:
        data = request.get_json(silent=True) or {}
        uploads = []
    try:
        message = staff_email.send_message(
            role=role,
            mailbox=str(data.get("mailbox") or ""),
            recipient=str(data.get("to") or ""),
            subject=str(data.get("subject") or ""),
            body=str(data.get("body") or ""),
            html_body=str(data.get("html") or ""),
            attachments=uploads,
            staff_user_id=int(user_id) if user_id.isdigit() else None,
            thread_id=str(data.get("thread_id") or "").strip() or None,
        )
    except staff_email.StaffEmailUnavailable as exc:
        return jsonify({"error": str(exc)}), 503
    except staff_email.StaffEmailError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"ok": True, "message": message})


def _webhook_payload():
    """A provider post, whichever shape it arrives in.

    An inbound delivery is a form (multipart once attachments are involved) and
    a legacy event webhook is a form too, while the current events webhook posts
    JSON. Both carry the signature fields; only where they sit differs.
    """
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form if request.form else {}


@app.route("/api/staff/email/inbound", methods=["POST"])
def api_staff_email_inbound():
    """Mailgun route delivery. Signed by the provider, not by a session.

    A delivery to an address that is no longer able to receive mail still gets
    a ``200``: the sender has already been answered automatically, and asking
    the provider to retry would only send that answer again.
    """
    payload = _webhook_payload()
    if not staff_email.webhook_authorized(payload):
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


@app.route("/api/staff/email/events", methods=["POST"])
def api_staff_email_events():
    """Mailgun message events: delivered, opened, clicked, bounced, complained.

    This is the only source of a read receipt: Mailgun posts ``opened`` for each
    open, and the message it names moves to its delivered/opened state. The
    endpoint answers the provider rather than a staff member, so it authenticates
    by signature alone, and a post with no recognisable event is acknowledged
    instead of being retried forever.
    """
    payload = _webhook_payload()
    if not staff_email.webhook_authorized(payload):
        return jsonify({"error": "Invalid webhook signature."}), 403
    try:
        result = staff_email.record_events(payload)
    except staff_email.StaffEmailUnavailable as exc:
        # A 5xx asks the provider to try again later; the event is not lost.
        log.warning("StaffEmail: delivery event could not be stored: %s", exc)
        return jsonify({"error": str(exc)}), 503
    except staff_email.StaffEmailError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"ok": True, **result})
