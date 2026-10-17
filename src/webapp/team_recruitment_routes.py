"""Owner-controlled API for Niko's official staff-team recruitment."""

import json
import logging
import re
import time
import uuid
from functools import wraps

import discord
import requests as req
from flask import jsonify, request, session

from config.ids import OWNER_IDS, SUPPORT_GUILD
from . import server as _server

app = _server.app
require_auth = _server.require_auth
require_csrf = _server.require_csrf
run_on_bot_loop = _server.run_on_bot_loop
get_runtime_member_metadata = _server.get_runtime_member_metadata
discord_request = _server.discord_request
DISCORD_API = _server.DISCORD_API
DISCORD_BOT_TOKEN = _server.DISCORD_BOT_TOKEN
_discord_bot = None
STAFF_GUILD_ID = str(SUPPORT_GUILD)
log = logging.getLogger(__name__)

APPROVAL_NEXT_STEPS = {
    "head_admin": [
        "Connect with the owner to align on moderation standards and team priorities.",
        "Review staff guidelines and escalation procedures before taking on cases.",
        "Help coordinate the team and support thoughtful decisions across roles.",
    ],
    "moderator": [
        "Read the moderation guidelines and escalation process.",
        "Meet the team and get familiar with the support server’s moderation channels.",
        "Ask a Head Admin when you need a second opinion on a difficult case.",
    ],
    "head_support": [
        "Connect with the owner to align on support priorities and team coverage.",
        "Review the help channels and current troubleshooting resources.",
        "Coordinate support teammates and help keep answers accurate and welcoming.",
    ],
    "support": [
        "Read the support guidelines and get familiar with the help channels.",
        "Start helping members with Niko questions and troubleshooting.",
        "Escalate anything unclear to the Head of Support or another teammate.",
    ],
    "graphic_designer": [
        "Connect with the team to review Niko’s visual style and current priorities.",
        "Share your preferred tools and availability for design requests.",
        "Coordinate with the owner before starting your first design brief.",
    ],
    "event_coordinator": [
        "Meet with the owner to review the upcoming event calendar and format.",
        "Coordinate event schedules and announcements with the team.",
        "Use the event channels to keep members informed and activities welcoming.",
    ],
    "partnerships_promotions_lead": [
        "Align with the owner on partnership goals and promotion standards.",
        "Coordinate partnership campaigns and review partner-server listings.",
        "Work with Partnership Managers to keep public promotions current and safe.",
    ],
    "partnership_manager": [
        "Review the partnership requirements and public listing guidelines.",
        "Coordinate with the Partnerships & Promotions Lead on partner enquiries.",
        "Keep partner-server advertisements accurate, active, and community-safe.",
    ],
}

# Fixed applications map directly to official roles defined in staff.py.
# Resolve Discord role IDs from the live support-guild roles; application IDs
# stay tied to the role key, not an editable owner-created role mapping.
TEAM_ROLE_APPLICATIONS = {
    "head_admin": {
        "title": "Head Admin",
        "description": "Help guide moderation standards, team operations, and difficult community decisions.",
        "questions": [
            {"id": "experience", "prompt": "Describe your experience leading moderation or community teams.", "type": "paragraph", "required": True},
            {"id": "judgement", "prompt": "How would you handle a disagreement between two staff members?", "type": "paragraph", "required": True},
            {"id": "priorities", "prompt": "What would you focus on improving first, and why?", "type": "paragraph", "required": True},
        ],
    },
    "moderator": {
        "title": "Moderator",
        "description": "Help keep Niko's support community welcoming, safe, and fair.",
        "questions": [
            {"id": "experience", "prompt": "What moderation experience or relevant strengths would you bring?", "type": "paragraph", "required": True},
            {"id": "scenario", "prompt": "How would you respond to a member repeatedly disrupting a help channel?", "type": "paragraph", "required": True},
            {"id": "availability", "prompt": "When are you generally available to help moderate?", "type": "short_text", "required": True},
        ],
    },
    "head_support": {
        "title": "Head of Support",
        "description": "Coordinate thoughtful, reliable help for the Niko community.",
        "questions": [
            {"id": "support_experience", "prompt": "Describe how you have organized or delivered community support.", "type": "paragraph", "required": True},
            {"id": "triage", "prompt": "How would you prioritize several unanswered support requests?", "type": "paragraph", "required": True},
            {"id": "quality", "prompt": "How would you help the team give consistent, accurate answers?", "type": "paragraph", "required": True},
        ],
    },
    "support": {
        "title": "Support Team",
        "description": "Help members troubleshoot Niko and find the right answers.",
        "questions": [
            {"id": "motivation", "prompt": "Why would you like to help the Niko community?", "type": "paragraph", "required": True},
            {"id": "troubleshooting", "prompt": "How would you help someone who cannot explain their issue clearly?", "type": "paragraph", "required": True},
            {"id": "experience", "prompt": "What languages, technical skills, or community experience could you contribute?", "type": "paragraph", "required": True},
        ],
    },
    "graphic_designer": {
        "title": "Graphic Designer",
        "description": "Shape clear, cohesive visuals for Niko and its community.",
        "questions": [
            {"id": "portfolio", "prompt": "Share links to examples of your design work or portfolio.", "type": "paragraph", "required": True},
            {"id": "process", "prompt": "Walk us through how you take a visual brief from idea to final design.", "type": "paragraph", "required": True},
            {"id": "tools", "prompt": "Which design tools and visual styles do you work with most?", "type": "short_text", "required": True},
        ],
    },
    "event_coordinator": {
        "title": "Event Coordinator",
        "description": "Plan and run welcoming events that bring the Niko community together.",
        "questions": [
            {"id": "event_experience", "prompt": "Describe an event or activity you have planned or helped run.", "type": "paragraph", "required": True},
            {"id": "event_idea", "prompt": "What is one event you would organize for the Niko community, and how would it work?", "type": "paragraph", "required": True},
            {"id": "event_support", "prompt": "How would you make sure an event stays welcoming and runs smoothly?", "type": "paragraph", "required": True},
        ],
    },
    "partnerships_promotions_lead": {
        "title": "Partnerships & Promotions Lead",
        "description": "Lead Niko’s partnership strategy, promotional standards, and partner-server relationships.",
        "questions": [
            {"id": "partnership_experience", "prompt": "Describe your experience managing partnerships or community promotions.", "type": "paragraph", "required": True},
            {"id": "partnership_standards", "prompt": "How would you evaluate whether a server is a good fit for a Niko partnership?", "type": "paragraph", "required": True},
            {"id": "partnership_campaign", "prompt": "How would you organize a mutually useful promotion between two communities?", "type": "paragraph", "required": True},
        ],
    },
    "partnership_manager": {
        "title": "Partnership Manager",
        "description": "Review partnership enquiries and maintain accurate, safe partner-server listings.",
        "questions": [
            {"id": "manager_experience", "prompt": "What experience do you have working with Discord communities or server partnerships?", "type": "paragraph", "required": True},
            {"id": "listing_review", "prompt": "What would you check before approving a server advertisement in our partners channel?", "type": "paragraph", "required": True},
            {"id": "enquiry_response", "prompt": "How would you respond to a partnership enquiry that does not meet our standards?", "type": "paragraph", "required": True},
        ],
    },
}


def _application_id(role_key):
    return f"team-{role_key}"


def _role_slug(role_name):
    return re.sub(r"[^a-z0-9]+", "", role_name.casefold())


def _support_role_id(role_key):
    expected_title = TEAM_ROLE_APPLICATIONS[role_key]["title"]
    guild = _discord_bot.get_guild(SUPPORT_GUILD) if _discord_bot is not None else None
    expected_slug = _role_slug(expected_title)
    role = next((role for role in getattr(guild, "roles", []) if _role_slug(role.name) == expected_slug), None)
    return str(role.id) if role else role_key


def _ensure_fixed_openings():
    for role_key in TEAM_ROLE_APPLICATIONS:
        definition = TEAM_ROLE_APPLICATIONS[role_key]
        run_on_bot_loop(_pool().execute(
            "INSERT OR IGNORE INTO staff_team_openings "
            "(id, role_id, title, description, questions, status, created_by) "
            "VALUES ($1, $2, $3, $4, $5, 'closed', 'system')",
            _application_id(role_key), _support_role_id(role_key), definition["title"],
            definition["description"], definition["questions"],
        ))
        run_on_bot_loop(_pool().execute(
            "UPDATE staff_team_openings SET role_id = $1 WHERE id = $2",
            _support_role_id(role_key), _application_id(role_key),
        ))


def _is_fixed_application(opening_id):
    return opening_id in {_application_id(role_key) for role_key in TEAM_ROLE_APPLICATIONS}


def _role_key_for_application(opening_id):
    return next((key for key in TEAM_ROLE_APPLICATIONS if _application_id(key) == opening_id), None)


def _eligibility_questions():
    return [
        {"id": "eligibility_guidelines", "prompt": "Can you follow the community and moderation guidelines consistently?", "type": "yes_no", "required": True},
        {"id": "eligibility_confidentiality", "prompt": "Can you keep private staff discussions and member information confidential?", "type": "yes_no", "required": True},
        {"id": "niko_age", "prompt": "What is your age?", "type": "short_text", "required": True},
        {"id": "eligibility_availability", "prompt": "Can you make time to contribute to your chosen role on a regular basis?", "type": "yes_no", "required": True},
    ]


def _valid_eligibility(raw_answers):
    try:
        age = int(str(raw_answers.get("niko_age", "")).strip())
    except (TypeError, ValueError):
        return False
    return 16 <= age <= 120 and all(
        raw_answers.get(question_id) == "yes"
        for question_id in ("eligibility_guidelines", "eligibility_confidentiality", "eligibility_availability")
    )


def _stored_eligibility_answers(raw_answers):
    age = str(int(str(raw_answers["niko_age"]).strip()))
    return [
        {"question_id": question["id"], "prompt": question["prompt"], "answer": age if question["id"] == "niko_age" else raw_answers[question["id"]]}
        for question in _eligibility_questions()
    ]


def _valid_application_answers(opening, raw_answers):
    answers = []
    role_key = _role_key_for_application(opening["id"])
    questions = TEAM_ROLE_APPLICATIONS[role_key]["questions"]
    if any(question["id"] not in raw_answers for question in questions):
        return None
    for question in questions:
        value = raw_answers.get(question["id"], "")
        if not isinstance(value, str):
            return None
        answer = value.strip()
        limit = 200 if question["type"] == "short_text" else 4000
        if not answer or len(answer) > limit:
            return None
        answers.append({"question_id": question["id"], "prompt": question["prompt"], "answer": answer})
    return answers


ELIGIBILITY_QUESTION_IDS = {question["id"] for question in _eligibility_questions()}


def _is_eligible_answer_set(raw_answers):
    return all(raw_answers.get(question_id) in {"yes", "no"} for question_id in ELIGIBILITY_QUESTION_IDS - {"niko_age"})


def _role_questions(role_key):
    return TEAM_ROLE_APPLICATIONS[role_key]["questions"]


def _opening_questions(role_key):
    return [*_eligibility_questions(), *_role_questions(role_key)]


def _role_label(role_key):
    return TEAM_ROLE_APPLICATIONS[role_key]["title"]


def _fixed_opening_payload(role_key, opening):
    definition = TEAM_ROLE_APPLICATIONS[role_key]
    guild = _discord_bot.get_guild(SUPPORT_GUILD) if _discord_bot is not None else None
    role_id = _support_role_id(role_key)
    role = guild.get_role(int(role_id)) if guild is not None and role_id.isdigit() else None
    opening.update(
        title=definition["title"], description=definition["description"],
        questions=_opening_questions(role_key), role_name=role.name if role else _role_label(role_key),
        link=f"/team/apply/{opening['id']}",
    )
    return opening


# The owner can change only opening status and review applications; the fixed
# application definitions above are not editable in the settings UI.




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


def _owner_only(view):
    """Authorize official team settings and decisions by bot-owner ID only."""
    @wraps(view)
    def checked(*args, **kwargs):
        try:
            user_id = int(session.get("user", {}).get("id", ""))
        except (TypeError, ValueError):
            user_id = None
        if user_id not in OWNER_IDS:
            return jsonify({"error": "Only the Niko owner can manage team recruitment."}), 403
        return view(*args, **kwargs)
    return checked


def _member_exists(user_id):
    """Verify membership in the configured Niko support server, not OAuth claims."""
    if DISCORD_BOT_TOKEN:
        try:
            # Through the bot's own egress: a bare requests client from a
            # datacenter IP is what Cloudflare challenges, and the membership
            # check is the first thing team applications depend on.
            response = discord_request(
                "GET",
                f"{DISCORD_API}/guilds/{SUPPORT_GUILD}/members/{user_id}",
                headers={"Authorization": f"Bot {DISCORD_BOT_TOKEN}"},
                timeout=8,
            )
        except req.RequestException as error:
            raise RuntimeError("Discord membership could not be verified right now.") from error
        if response.status_code == 404:
            return False
        if response.status_code != 200:
            raise RuntimeError("Discord membership could not be verified right now.")
        return True

    if _discord_bot is None:
        raise RuntimeError("The bot is not available to verify server membership.")

    async def fetch_member():
        guild = _discord_bot.get_guild(SUPPORT_GUILD)
        if guild is None:
            return False
        try:
            await guild.fetch_member(int(user_id))
            return True
        except Exception as error:
            if getattr(error, "status", None) == 404:
                return False
            raise

    try:
        return run_on_bot_loop(fetch_member())
    except RuntimeError:
        raise
    except Exception as error:
        raise RuntimeError("Discord membership could not be verified right now.") from error


def _opening(opening_id):
    row = run_on_bot_loop(_pool().fetchrow(
        "SELECT id, role_id, title, description, questions, status, created_at "
        "FROM staff_team_openings WHERE id = $1", opening_id,
    ))
    if row is None:
        return None
    opening = dict(row)
    opening["id"], opening["role_id"] = str(opening["id"]), str(row["role_id"])
    role_key = _role_key_for_application(opening["id"])
    if role_key is None:
        return None
    opening["questions"] = _opening_questions(role_key)
    return _fixed_opening_payload(role_key, opening)


def _submissions(rows):
    user_ids = {str(row.get("user_id")) for row in rows}
    metadata = get_runtime_member_metadata(STAFF_GUILD_ID, user_ids)
    return [{
        "user_id": str(row.get("user_id")),
        "display_name": metadata.get(str(row.get("user_id")), {}).get("display_name") or f"Discord user {row.get('user_id')}",
        "answers": _json_value(row.get("answers"), []),
        "submitted_at": row.get("submitted_at"),
        "review_status": row.get("review_status") or "pending",
        "reviewed_by": row.get("reviewed_by"),
        "reviewed_at": row.get("reviewed_at"),
    } for row in rows]


@app.route("/api/team-recruitment/membership")
@require_auth
def team_recruitment_membership():
    try:
        return jsonify({"member": _member_exists(session["user"].get("id", ""))})
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503


@app.route("/api/team-recruitment")
@require_auth
def team_recruitment_openings():
    user_id = str(session["user"].get("id", ""))
    try:
        if not _member_exists(user_id):
            return jsonify({"error": "Join the Niko support server to view team openings."}), 403
        _ensure_fixed_openings()
        rows = run_on_bot_loop(_pool().fetch(
            "SELECT id FROM staff_team_openings WHERE status = 'open' ORDER BY created_at DESC",
        ))
        openings = []
        for row in rows:
            opening = _opening(row["id"])
            if opening is None:
                continue
            exists = run_on_bot_loop(_pool().fetchrow(
                "SELECT user_id FROM staff_team_submissions WHERE opening_id = $1 AND user_id = $2",
                opening["id"], user_id,
            ))
            opening.update(already_submitted=exists is not None, eligible=True)
            openings.append(opening)
        return jsonify({"openings": openings})
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503
    except Exception:
        return jsonify({"error": "Niko team openings are temporarily unavailable."}), 503


@app.route("/api/team-recruitment/<opening_id>")
@require_auth
def team_recruitment_opening(opening_id):
    try:
        if not _member_exists(session["user"].get("id", "")):
            return jsonify({"error": "Join the Niko support server before applying."}), 403
        _ensure_fixed_openings()
        if not _is_fixed_application(opening_id):
            return jsonify({"error": "That Niko team opening could not be found."}), 404
        opening = _opening(opening_id)
        if opening is None:
            return jsonify({"error": "That Niko team opening could not be found."}), 404
        if opening["status"] != "open":
            return jsonify({"error": "This Niko team opening is closed."}), 410
        exists = run_on_bot_loop(_pool().fetchrow(
            "SELECT user_id FROM staff_team_submissions WHERE opening_id = $1 AND user_id = $2",
            opening_id, str(session["user"].get("id", "")),
        ))
        opening.update(already_submitted=exists is not None, eligible=True)
        return jsonify(opening)
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503
    except Exception:
        return jsonify({"error": "This Niko team opening is temporarily unavailable."}), 503


@app.route("/api/team-recruitment/<opening_id>/submit", methods=["POST"])
@require_auth
@require_csrf
def submit_team_recruitment(opening_id):
    user_id = str(session["user"].get("id", ""))
    try:
        if not _member_exists(user_id):
            return jsonify({"error": "Join the Niko support server before applying."}), 403
        _ensure_fixed_openings()
        if not _is_fixed_application(opening_id):
            return jsonify({"error": "That Niko team opening could not be found."}), 404
        opening = _opening(opening_id)
        if opening is None:
            return jsonify({"error": "That Niko team opening could not be found."}), 404
        if opening["status"] != "open":
            return jsonify({"error": "This Niko team opening is closed."}), 410
        raw_answers = (request.get_json(silent=True) or {}).get("answers")
        if not isinstance(raw_answers, dict):
            return jsonify({"error": "Please complete the application questions."}), 400
        if not _is_eligible_answer_set(raw_answers):
            return jsonify({"error": "Please complete every eligibility question with a valid response."}), 400
        if not _valid_eligibility(raw_answers):
            return jsonify({"error": "Your responses do not meet the eligibility requirements for this role."}), 403
        answers = _stored_eligibility_answers(raw_answers)
        role_answers = _valid_application_answers(opening, raw_answers)
        if role_answers is None:
            return jsonify({"error": "Please complete every required role question with a valid response."}), 400
        answers.extend(role_answers)
        receipt_id = uuid.uuid4().hex
        run_on_bot_loop(_pool().execute(
            "INSERT OR IGNORE INTO staff_team_submissions (opening_id, user_id, answers, receipt_id) "
            "VALUES ($1, $2, $3, $4)", opening_id, user_id, answers, receipt_id,
        ))
        stored = run_on_bot_loop(_pool().fetchrow(
            "SELECT receipt_id FROM staff_team_submissions WHERE opening_id = $1 AND user_id = $2",
            opening_id, user_id,
        ))
        if not stored or stored.get("receipt_id") != receipt_id:
            return jsonify({"error": "You have already submitted an application for this opening."}), 409
        return jsonify({"ok": True, "message": "Your Niko team application has been submitted."}), 201
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503
    except Exception:
        return jsonify({"error": "Your Niko team application could not be saved right now."}), 503


@app.route("/api/staff/team-recruitment", methods=["GET"])
@require_auth
@_owner_only
def staff_team_recruitment_settings():
    try:
        _ensure_fixed_openings()
        openings = []
        for role_key in TEAM_ROLE_APPLICATIONS:
            opening = _opening(_application_id(role_key))
            if opening is None:
                continue
            opening["submission_count"] = int(run_on_bot_loop(_pool().fetchval(
                "SELECT COUNT(*) FROM staff_team_submissions WHERE opening_id = $1", opening["id"],
            )) or 0)
            openings.append(opening)
        return jsonify({"openings": openings})
    except Exception:
        return jsonify({"error": "Team recruitment settings are temporarily unavailable."}), 503



@app.route("/api/staff/team-recruitment/<opening_id>/status", methods=["POST"])
@require_auth
@require_csrf
@_owner_only
def set_staff_team_opening_status(opening_id):
    try:
        _ensure_fixed_openings()
    except Exception:
        return jsonify({"error": "Team recruitment settings are temporarily unavailable."}), 503
    if not _is_fixed_application(opening_id):
        return jsonify({"error": "Team opening not found."}), 404
    status = (request.get_json(silent=True) or {}).get("status")
    if status not in {"open", "closed"}:
        return jsonify({"error": "Opening status must be open or closed."}), 400
    found = run_on_bot_loop(_pool().fetchrow("SELECT id FROM staff_team_openings WHERE id = $1", opening_id))
    if found is None:
        return jsonify({"error": "Team opening not found."}), 404
    run_on_bot_loop(_pool().execute(
        "UPDATE staff_team_openings SET status = $1, updated_at = datetime('now') WHERE id = $2",
        status, opening_id,
    ))
    return jsonify({"ok": True, "status": status})


@app.route("/api/staff/team-recruitment/<opening_id>/submissions")
@require_auth
@_owner_only
def staff_team_submissions(opening_id):
    try:
        _ensure_fixed_openings()
        if not _is_fixed_application(opening_id) or _opening(opening_id) is None:
            return jsonify({"error": "Team opening not found."}), 404
        rows = run_on_bot_loop(_pool().fetch(
            "SELECT user_id, answers, submitted_at, review_status, reviewed_by, reviewed_at "
            "FROM staff_team_submissions WHERE opening_id = $1 "
            "ORDER BY CASE WHEN review_status = 'pending' THEN 0 ELSE 1 END, submitted_at DESC",
            opening_id,
        ))
        return jsonify({"opening": _opening(opening_id), "submissions": _submissions(rows)})
    except Exception:
        return jsonify({"error": "Team application submissions are temporarily unavailable."}), 503


def _review_dm_view(role_key, status):
    role_title = _role_label(role_key)
    view = discord.ui.LayoutView(timeout=None)
    if status == "approved":
        steps = "\n".join(f"- {step}" for step in APPROVAL_NEXT_STEPS[role_key])
        content = (
            f"# 🎉 Welcome to the Niko team!\n"
            f"Your application for **{role_title}** has been approved. We’re excited to have you with us!\n\n"
            f"### Your next steps\n{steps}\n\n"
            "If you have any questions, just reply here or reach out in the support server."
        )
        accent = discord.Colour(0x65A884)
    else:
        content = (
            f"# Thanks for applying to Niko\n"
            f"We’ve reviewed your application for **{role_title}** and, unfortunately, we won’t be moving forward this time. "
            "We appreciate the time and thought you put into applying. Please don’t be discouraged—you're welcome to apply "
            "again when another opening interests you, and we wish you all the best."
        )
        accent = discord.Colour(0xC8A882)
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=content),
        accent_colour=accent,
    ))
    return view


async def _apply_team_role(user_id, role_key):
    if _discord_bot is None:
        raise RuntimeError("The Discord bot is not available to assign the team role.")
    guild = _discord_bot.get_guild(SUPPORT_GUILD)
    if guild is None:
        raise RuntimeError("The Niko support server is not available to assign the team role.")
    role_id = _support_role_id(role_key)
    if not role_id.isdigit():
        raise RuntimeError(f"The {TEAM_ROLE_APPLICATIONS[role_key]['title']} role is not configured in the support server.")
    role = guild.get_role(int(role_id))
    if role is None:
        raise RuntimeError(f"The {TEAM_ROLE_APPLICATIONS[role_key]['title']} role could not be found in the support server.")
    member = guild.get_member(int(user_id))
    if member is None:
        member = await guild.fetch_member(int(user_id))
    if role in member.roles:
        return member, role, False
    await member.add_roles(role, reason=f"Team application approved: {TEAM_ROLE_APPLICATIONS[role_key]['title']}")
    return member, role, True


async def _persist_staff_assignment(user_id, role_key, assigned_by):
    pool = _pool()
    if role_key not in _server.STAFF_ROLES:
        raise RuntimeError(f"{role_key} is not a staff role, so the roster cannot record it.")
    await pool.execute(
        "INSERT OR REPLACE INTO staff_members (user_id, role, assigned_by, assigned_at) VALUES ($1, $2, $3, $4)",
        int(user_id), role_key, int(assigned_by), int(time.time()),
    )


async def _clear_staff_assignment(user_id, role_key):
    await _pool().execute(
        "DELETE FROM staff_members WHERE user_id = $1 AND role = $2", int(user_id), role_key,
    )


async def _resolve_team_member(user_id, role_key):
    """Return the support-guild member and role for a team role key."""
    if _discord_bot is None:
        raise RuntimeError("The Discord bot is not available to update the team role.")
    guild = _discord_bot.get_guild(SUPPORT_GUILD)
    if guild is None:
        raise RuntimeError("The Niko support server is not available to update the team role.")
    role_id = _support_role_id(role_key)
    if not role_id.isdigit():
        raise RuntimeError(f"The {TEAM_ROLE_APPLICATIONS[role_key]['title']} role is not configured in the support server.")
    role = guild.get_role(int(role_id))
    if role is None:
        raise RuntimeError(f"The {TEAM_ROLE_APPLICATIONS[role_key]['title']} role could not be found in the support server.")
    member = guild.get_member(int(user_id))
    if member is None:
        member = await guild.fetch_member(int(user_id))
    return member, role


async def _revoke_team_role(user_id, role_key):
    """Take back the team role a reversed approval had granted."""
    member, role = await _resolve_team_member(user_id, role_key)
    if role not in member.roles:
        return False
    await member.remove_roles(
        role, reason=f"Team application decision reversed: {TEAM_ROLE_APPLICATIONS[role_key]['title']}",
    )
    return True


async def _remove_team_role(member, role, role_key):
    await member.remove_roles(role, reason=f"Team application approval rolled back: {TEAM_ROLE_APPLICATIONS[role_key]['title']}")


async def _send_review_dm(user_id, role_key, status):
    if _discord_bot is None:
        raise RuntimeError("The Discord bot is not available to send the application decision.")
    user = _discord_bot.get_user(int(user_id))
    if user is None:
        user = await _discord_bot.fetch_user(int(user_id))
    await user.send(view=_review_dm_view(role_key, status))


@app.route("/api/staff/team-recruitment/<opening_id>/submissions/<user_id>/review", methods=["POST"])
@require_auth
@require_csrf
@_owner_only
def review_staff_team_submission(opening_id, user_id):
    if not _is_fixed_application(opening_id):
        return jsonify({"error": "Team application response not found."}), 404
    status = (request.get_json(silent=True) or {}).get("status")
    if status not in {"approved", "denied"}:
        return jsonify({"error": "Review status must be approved or denied."}), 400
    found = run_on_bot_loop(_pool().fetchrow(
        "SELECT user_id, review_status FROM staff_team_submissions WHERE opening_id = $1 AND user_id = $2",
        opening_id, user_id,
    ))
    if found is None:
        return jsonify({"error": "Team application response not found."}), 404
    role_key = _role_key_for_application(opening_id)
    previous_status = found.get("review_status") or "pending"
    if previous_status == status:
        # Recording the same decision twice must not repeat the role change or
        # send the applicant a second decision DM.
        return jsonify({
            "ok": True,
            "review_status": status,
            "previous_status": previous_status,
            "unchanged": True,
            "dm_sent": None,
            "role_revoked": False,
        })
    # Denying an application that was already approved takes the granted role
    # back, so Discord and the staff roster agree with the recorded decision.
    revoke_role = status == "denied" and previous_status == "approved"
    assigned_member = None
    assigned_role = None
    role_was_added = False
    role_revoked = False
    try:
        if status == "approved":
            assigned_member, assigned_role, role_was_added = run_on_bot_loop(
                _apply_team_role(user_id, role_key)
            )
            run_on_bot_loop(_persist_staff_assignment(
                user_id, role_key, int(session["user"].get("id", 0))
            ))
        elif revoke_role:
            role_revoked = bool(run_on_bot_loop(_revoke_team_role(user_id, role_key)))
            run_on_bot_loop(_clear_staff_assignment(user_id, role_key))
        run_on_bot_loop(_pool().execute(
            "UPDATE staff_team_submissions SET review_status = $1, reviewed_by = $2, reviewed_at = datetime('now') "
            "WHERE opening_id = $3 AND user_id = $4",
            status, str(session["user"].get("id", "")), opening_id, user_id,
        ))
    except discord.Forbidden:
        if role_was_added:
            try:
                run_on_bot_loop(_remove_team_role(assigned_member, assigned_role, role_key))
            except Exception:
                log.exception("Could not roll back the %s role for applicant %s", role_key, user_id)
        return jsonify({"error": "The decision was not saved because Discord blocked the role assignment. Check the bot's role permissions."}), 502
    except Exception:
        if role_was_added:
            try:
                run_on_bot_loop(_remove_team_role(assigned_member, assigned_role, role_key))
            except Exception:
                log.exception("Could not roll back the %s role for applicant %s", role_key, user_id)
        log.exception("Could not assign role or save %s decision for team applicant %s for %s", status, user_id, opening_id)
        return jsonify({"error": "The decision could not be saved. The applicant was not notified."}), 502

    # Sending a DM is best-effort and must not undo a role or database decision
    # that has already been applied; Discord may reject DMs independently.
    dm_sent = True
    try:
        run_on_bot_loop(_send_review_dm(user_id, role_key, status))
    except Exception:
        dm_sent = False
        log.exception("Could not send %s decision DM to team applicant %s for %s", status, user_id, opening_id)
    return jsonify({
        "ok": True,
        "review_status": status,
        "previous_status": previous_status,
        "unchanged": False,
        "dm_sent": dm_sent,
        "role_revoked": role_revoked,
    })
