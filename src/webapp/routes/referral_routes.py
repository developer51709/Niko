"""Referral links for the support server.

``GET /api/me/referrals`` backs the dashboard's referral card: the link a member
shares and the members it has brought in so far.

The link itself is the website's ``/discord?ref=<user id>`` page, so it can be
shared anywhere a URL fits. Opening it joins the visitor through their own
Discord account (never through an invite, so no invite is created for the
member), and that is where attribution and the payout happen
(``cogs/staff/support_referrals`` and ``cogs/economy/referrals``); this module
only reads.
"""

from cogs.economy.referrals import REFERRAL_REWARD
from cogs.staff.support_referrals import referral_standing

from .. import server as _server
from .. import social_preview

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})


def _recent_referrals(entries: list[dict]) -> list[dict]:
    """Annotate the newest referrals with whatever identity the bot still holds.

    A member who has since left is still a counted referral, so a missing name
    falls back to the raw id instead of dropping the row.
    """
    get_user = getattr(_discord_bot, "get_user", None) if _discord_bot is not None else None
    annotated = []
    for entry in entries:
        member_id = str(entry.get("member_id") or "")
        name = None
        avatar_url = None
        if callable(get_user) and member_id.isdigit():
            user = get_user(int(member_id))
            if user is not None:
                name = getattr(user, "display_name", None) or getattr(user, "name", None)
                avatar = getattr(user, "display_avatar", None)
                avatar_url = str(avatar.url) if avatar is not None else None
        annotated.append({
            "member_id": member_id,
            "name": name,
            "avatar_url": avatar_url,
            "joined_at": int(entry.get("joined_at") or 0),
            "reward": int(entry.get("reward") or 0),
        })
    return annotated


@app.route("/api/me/referrals")
@require_auth
def api_me_referrals():
    """The signed-in member's referral link and its results."""
    user_id = str(session["user"].get("id", "")).strip()
    if not user_id.isdigit():
        return jsonify({"error": "Referral links need a Discord account."}), 400

    # The website link is always available, even when the bot is between
    # restarts: it resolves to the invite at click time, not at read time.
    payload = {
        "link": f"{social_preview.SITE_URL}/discord?ref={user_id}",
        "invited": 0,
        "coins": 0,
        "reward": REFERRAL_REWARD,
        "recent": [],
    }

    bot = _discord_bot
    if bot is None or getattr(bot, "cxn", None) is None:
        return jsonify(payload)

    try:
        standing = run_on_bot_loop(referral_standing(bot, int(user_id)))
    except Exception:
        standing = None
    if standing:
        payload["invited"] = int(standing.get("invited") or 0)
        payload["coins"] = int(standing.get("coins") or 0)
        payload["recent"] = _recent_referrals(standing.get("recent") or [])
    return jsonify(payload)
