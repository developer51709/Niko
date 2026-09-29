"""Routes for server-managed staff applications."""

import json
import secrets
import sqlite3
import uuid

import requests as req
from flask import jsonify, request, session

from . import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})


def _pool():
    if _discord_bot is None or not getattr(_discord_bot, "cxn", None):
        raise RuntimeError("The bot database is unavailable.")
    return _discord_bot.cxn


def _json_value(value, fallback):
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            return fallback
    return value if isinstance(value, type(fallback)) else fallback


def _application_dict(row):
    application = dict(row)
    application["role_id"] = str(application.get("role_id", ""))
    application["guild_id"] = str(application.get("guild_id", ""))
    application["questions"] = _json_value(application.get("questions"), [])
    application["eligible_role_ids"] = [
        str(role_id) for role_id in _json_value(application.get("eligible_role_ids"), [])
    ]
    application["submission_count"] = 0
    application["link"] = f"/apply/{application['guild_id']}/{application['id']}"
    return application


def _application_questions(value):
    if not isinstance(value, list) or len(value) > 12:
        raise ValueError("Add between 1 and 12 application questions.")
    questions = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("Each question must include a prompt.")
        prompt = str(item.get("prompt", "")).strip()
        if not prompt or len(prompt) > 240:
            raise ValueError("Question prompts must be between 1 and 240 characters.")
        questions.append({
            "id": str(item.get("id") or uuid.uuid4().hex),
            "prompt": prompt,
            "required": bool(item.get("required", True)),
        })
    if not questions:
        raise ValueError("Add at least one application question.")
    return questions


def _member_role_ids(guild_id, user_id):
    """Use a bot-authenticated Discord membership lookup, never OAuth guild claims."""
    if DISCORD_BOT_TOKEN:
        try:
            response = req.get(
                f"{DISCORD_API}/guilds/{guild_id}/members/{user_id}",
                headers={"Authorization": f"Bot {DISCORD_BOT_TOKEN}"},
                timeout=8,
            )
        except req.RequestException as error:
            raise RuntimeError("Discord membership could not be verified right now.") from error
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise RuntimeError("Discord membership could not be verified right now.")
        member = response.json()
        return {str(role_id) for role_id in member.get("roles", [])}

    if _discord_bot is None:
        raise RuntimeError("The bot is not available to verify server membership.")

    async def fetch_member_roles():
        guild = _discord_bot.get_guild(int(guild_id))
        if guild is None:
            return None
        member = await guild.fetch_member(int(user_id))
        return {str(role.id) for role in member.roles if not role.is_default()}

    try:
        return run_on_bot_loop(fetch_member_roles())
    except Exception as error:
        if getattr(error, "status", None) == 404:
            return None
        raise RuntimeError("Discord membership could not be verified right now.") from error


def _public_application(guild_id, application_id):
    row = run_on_bot_loop(_pool().fetchrow(
        "SELECT id, guild_id, role_id, title, description, questions, eligible_role_ids, status "
        "FROM staff_applications WHERE id = $1 AND guild_id = $2",
        application_id, int(guild_id),
    ))
    if row is None:
        return None
    application = _application_dict(row)
    guild = _discord_bot.get_guild(int(guild_id)) if _discord_bot is not None else None
    role = guild.get_role(int(application["role_id"])) if guild is not None else None
    application["role_name"] = role.name if role is not None else None
    application["guild_name"] = guild.name if guild is not None else None
    return application


@app.route("/api/guild/<guild_id>/applications", methods=["GET"])
@require_auth
@require_guild_access
def api_staff_applications(guild_id):
    try:
        rows = run_on_bot_loop(_pool().fetch(
            "SELECT * FROM staff_applications WHERE guild_id = $1 ORDER BY created_at DESC",
            int(guild_id),
        ))
        applications = [_application_dict(row) for row in rows]
        for application in applications:
            count = run_on_bot_loop(_pool().fetchval(
                "SELECT COUNT(*) FROM staff_application_submissions WHERE application_id = $1",
                application["id"],
            ))
            application["submission_count"] = int(count or 0)
        return jsonify(applications)
    except Exception:
        return jsonify({"error": "Staff applications are temporarily unavailable."}), 503


@app.route("/api/guild/<guild_id>/applications", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_create_staff_application(guild_id):
    body = request.get_json(silent=True) or {}
    title = str(body.get("title", "")).strip()
    description = str(body.get("description", "")).strip()
    role_id = str(body.get("role_id", ""))
    if not title or len(title) > 100:
        return jsonify({"error": "Give this application a title (up to 100 characters)."}), 400
    if len(description) > 2000:
        return jsonify({"error": "The description must be 2,000 characters or fewer."}), 400
    if not role_id.isdigit():
        return jsonify({"error": "Choose a valid server role for this opening."}), 400
    try:
        questions = _application_questions(body.get("questions"))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    eligible_role_ids = body.get("eligible_role_ids", [])
    if not isinstance(eligible_role_ids, list) or len(eligible_role_ids) > 20:
        return jsonify({"error": "Choose up to 20 eligible roles."}), 400
    eligible_role_ids = list(dict.fromkeys(str(item) for item in eligible_role_ids))
    if any(not role_id_value.isdigit() for role_id_value in eligible_role_ids):
        return jsonify({"error": "Eligibility roles must be valid server roles."}), 400
    _, role_ids = _guild_resource_ids(int(guild_id))
    if role_ids is not None and (
        role_id not in role_ids or any(item not in role_ids for item in eligible_role_ids)
    ):
        return jsonify({"error": "The selected role does not belong to this server."}), 400

    application_id = secrets.token_urlsafe(12)
    try:
        run_on_bot_loop(_pool().execute(
            "INSERT INTO staff_applications "
            "(id, guild_id, role_id, title, description, questions, eligible_role_ids, status, created_by) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, 'open', $8)",
            application_id, int(guild_id), role_id, title, description,
            questions, eligible_role_ids, str(session["user"].get("id", "")),
        ))
    except Exception:
        return jsonify({"error": "This application could not be saved."}), 503
    return jsonify({
        "ok": True,
        "application": {
            "id": application_id,
            "guild_id": str(guild_id),
            "role_id": role_id,
            "title": title,
            "description": description,
            "questions": questions,
            "eligible_role_ids": eligible_role_ids,
            "status": "open",
            "submission_count": 0,
            "link": f"/apply/{guild_id}/{application_id}",
        },
    }), 201


@app.route("/api/guild/<guild_id>/applications/<application_id>/status", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_set_staff_application_status(guild_id, application_id):
    body = request.get_json(silent=True) or {}
    status = body.get("status")
    if status not in {"open", "closed"}:
        return jsonify({"error": "Application status must be open or closed."}), 400
    try:
        row = run_on_bot_loop(_pool().fetchrow(
            "SELECT id FROM staff_applications WHERE id = $1 AND guild_id = $2",
            application_id, int(guild_id),
        ))
        if row is None:
            return jsonify({"error": "Application not found."}), 404
        run_on_bot_loop(_pool().execute(
            "UPDATE staff_applications SET status = $1, updated_at = datetime('now') "
            "WHERE id = $2 AND guild_id = $3",
            status, application_id, int(guild_id),
        ))
        return jsonify({"ok": True, "status": status})
    except Exception:
        return jsonify({"error": "Application status could not be updated."}), 503


@app.route("/api/guild/<guild_id>/applications/<application_id>/submissions")
@require_auth
@require_guild_access
def api_staff_application_submissions(guild_id, application_id):
    try:
        application = _public_application(guild_id, application_id)
        if application is None:
            return jsonify({"error": "Application not found."}), 404
        rows = run_on_bot_loop(_pool().fetch(
            "SELECT user_id, answers, submitted_at FROM staff_application_submissions "
            "WHERE application_id = $1 ORDER BY submitted_at DESC",
            application_id,
        ))
        user_ids = {str(row.get("user_id")) for row in rows}
        metadata = get_runtime_member_metadata(guild_id, user_ids)
        submissions = []
        for row in rows:
            user_id = str(row.get("user_id"))
            submissions.append({
                "user_id": user_id,
                "display_name": metadata.get(user_id, {}).get("display_name") or f"Discord user {user_id}",
                "username": metadata.get(user_id, {}).get("username"),
                "avatar_url": metadata.get(user_id, {}).get("avatar_url"),
                "answers": _json_value(row.get("answers"), []),
                "submitted_at": row.get("submitted_at"),
            })
        return jsonify({"application": application, "submissions": submissions})
    except Exception:
        return jsonify({"error": "Application responses are temporarily unavailable."}), 503


@app.route("/api/applications/<guild_id>")
@require_auth
def api_public_staff_openings(guild_id):
    try:
        user_id = str(session["user"].get("id", ""))
        member_roles = _member_role_ids(guild_id, user_id)
        if member_roles is None:
            return jsonify({"error": "You must be a member of this server to apply."}), 403
        rows = run_on_bot_loop(_pool().fetch(
            "SELECT id, guild_id, role_id, title, description, questions, eligible_role_ids, status "
            "FROM staff_applications WHERE guild_id = $1 AND status = 'open' ORDER BY created_at DESC",
            int(guild_id),
        ))
        openings = []
        guild = _discord_bot.get_guild(int(guild_id)) if _discord_bot is not None else None
        for row in rows:
            opening = _application_dict(row)
            role = guild.get_role(int(opening["role_id"])) if guild is not None else None
            opening["role_name"] = role.name if role is not None else None
            opening["guild_name"] = guild.name if guild is not None else None
            eligible_roles = set(opening["eligible_role_ids"])
            if eligible_roles and not member_roles.intersection(eligible_roles):
                opening["eligible"] = False
                opening["already_submitted"] = False
            else:
                opening["eligible"] = True
                existing = run_on_bot_loop(_pool().fetchrow(
                    "SELECT user_id FROM staff_application_submissions "
                    "WHERE application_id = $1 AND user_id = $2",
                    opening["id"], user_id,
                ))
                opening["already_submitted"] = existing is not None
            openings.append(opening)
        return jsonify({"openings": openings})
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503
    except Exception:
        return jsonify({"error": "Openings are temporarily unavailable."}), 503


@app.route("/api/applications/<guild_id>/<application_id>")
@require_auth
def api_public_staff_application(guild_id, application_id):
    try:
        application = _public_application(guild_id, application_id)
    except Exception:
        return jsonify({"error": "This application is temporarily unavailable."}), 503
    if application is None:
        return jsonify({"error": "Application not found."}), 404
    if application["status"] != "open":
        return jsonify({"error": "This application is closed."}), 410

    user_id = str(session["user"].get("id", ""))
    try:
        member_roles = _member_role_ids(guild_id, user_id)
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503
    if member_roles is None:
        return jsonify({"error": "You must be a member of this server to apply."}), 403
    eligible_roles = set(application["eligible_role_ids"])
    if eligible_roles and not member_roles.intersection(eligible_roles):
        return jsonify({"error": "You do not have a role required to apply for this opening."}), 403

    try:
        existing = run_on_bot_loop(_pool().fetchrow(
            "SELECT user_id FROM staff_application_submissions "
            "WHERE application_id = $1 AND user_id = $2",
            application_id, user_id,
        ))
    except Exception:
        return jsonify({"error": "Application status is temporarily unavailable."}), 503
    application["already_submitted"] = existing is not None
    return jsonify(application)


@app.route("/api/applications/<guild_id>/<application_id>/submit", methods=["POST"])
@require_auth
@require_csrf
def api_submit_staff_application(guild_id, application_id):
    try:
        application = _public_application(guild_id, application_id)
    except Exception:
        return jsonify({"error": "This application is temporarily unavailable."}), 503
    if application is None:
        return jsonify({"error": "Application not found."}), 404
    if application["status"] != "open":
        return jsonify({"error": "This application is closed."}), 410

    user_id = str(session["user"].get("id", ""))
    try:
        member_roles = _member_role_ids(guild_id, user_id)
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503
    if member_roles is None:
        return jsonify({"error": "You must be a member of this server to apply."}), 403
    eligible_roles = set(application["eligible_role_ids"])
    if eligible_roles and not member_roles.intersection(eligible_roles):
        return jsonify({"error": "You do not have a role required to apply for this opening."}), 403

    body = request.get_json(silent=True) or {}
    raw_answers = body.get("answers")
    if not isinstance(raw_answers, dict):
        return jsonify({"error": "Please complete the application questions."}), 400
    answers = []
    for question in application["questions"]:
        question_id = str(question.get("id", ""))
        answer = str(raw_answers.get(question_id, "")).strip()
        if question.get("required", True) and not answer:
            return jsonify({"error": f"Please answer: {question.get('prompt', 'each required question')}"}), 400
        if len(answer) > 4000:
            return jsonify({"error": "Each answer must be 4,000 characters or fewer."}), 400
        answers.append({"question_id": question_id, "prompt": question.get("prompt", ""), "answer": answer})

    receipt_id = uuid.uuid4().hex
    try:
        run_on_bot_loop(_pool().execute(
            "INSERT OR IGNORE INTO staff_application_submissions "
            "(application_id, user_id, answers, receipt_id) VALUES ($1, $2, $3, $4)",
            application_id, user_id, answers, receipt_id,
        ))
        stored = run_on_bot_loop(_pool().fetchrow(
            "SELECT receipt_id FROM staff_application_submissions "
            "WHERE application_id = $1 AND user_id = $2",
            application_id, user_id,
        ))
        if not stored or stored.get("receipt_id") != receipt_id:
            return jsonify({"error": "You have already submitted an application for this opening."}), 409
    except Exception:
        try:
            stored = run_on_bot_loop(_pool().fetchrow(
                "SELECT receipt_id FROM staff_application_submissions "
                "WHERE application_id = $1 AND user_id = $2",
                application_id, user_id,
            ))
            if stored and stored.get("receipt_id") != receipt_id:
                return jsonify({"error": "You have already submitted an application for this opening."}), 409
        except Exception:
            pass
        return jsonify({"error": "Your application could not be saved right now."}), 503
    return jsonify({"ok": True, "message": "Your application has been submitted."}), 201
