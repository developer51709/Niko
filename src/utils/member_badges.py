"""Niko's own profile badges.

One module decides which Niko badges an account carries, so the bot's profile
card and the website's profile popovers can never disagree.

Every lookup is best effort: a missing database, guild or role means "no
badge", never an error, because the badges are decoration on top of whatever
the caller is actually doing.

Badge keys match the artwork names the popups own
(``web/public/assets/badges/niko_*.svg``); the bot's emoji names are mapped
from these keys in ``cogs/info/_badges.py``.
"""

from __future__ import annotations

from datetime import datetime, timezone

from config.ids import OWNER_IDS, SUPPORT_GUILD

#: Staff role key -> badge key, in the order Discord lists Niko's roles.
STAFF_BADGE_ROLES = (
    ("owner", "niko_owner"),
    ("head_admin", "niko_head_admin"),
    ("moderator", "niko_moderator"),
    ("head_support", "niko_head_support"),
    ("graphic_designer", "niko_graphic_designer"),
    ("support", "niko_support"),
    ("event_coordinator", "niko_event_coordinator"),
    ("partnerships_promotions_lead", "niko_partnerships_promotions_lead"),
    ("partnership_manager", "niko_partnership_manager"),
)

#: The server-boosting tiers Discord draws its own badge for, ascending.
BOOSTING_TIERS = (1, 2, 3, 6, 9, 12, 15, 18, 24)

#: Support-server community role key -> badge key.
COMMUNITY_BADGE_ROLES = (
    ("supporter", "niko_supporter"),
    ("bugbounty", "niko_bug_hunter"),
    ("partner", "niko_partner"),
)

#: Every badge key in the order the popups show them. ``niko_staff`` is the
#: umbrella role every staff member also holds, so it only shows up for a
#: member whose specific role was not resolved.
NIKO_BADGE_ORDER = (
    *(badge for _, badge in STAFF_BADGE_ROLES),
    "niko_staff",
    *(badge for _, badge in COMMUNITY_BADGE_ROLES),
)


def boosting_badge_key(premium_since) -> str | None:
    """The boosting badge key a boost streak has reached, or ``None``.

    Discord keeps the lower tier until the next one is reached, so a streak
    between two tiers keeps the lower badge. Shared by the bot's profile card
    and the website's profile popups so both always name the same badge.
    """
    if not hasattr(premium_since, "year"):
        return None
    today = datetime.now(timezone.utc)
    months = (today.year - premium_since.year) * 12 + (today.month - premium_since.month)
    if today.day < premium_since.day:
        months -= 1
    if months < BOOSTING_TIERS[0]:
        return None
    return f"boosting_{max(tier for tier in BOOSTING_TIERS if tier <= months)}_months"


def _role_ids(ids: dict, key: str) -> set[int]:
    """Read one configured support-server role id as an ``int``, if it is set."""
    value = (ids or {}).get(key)
    try:
        return {int(value)} if value else set()
    except (TypeError, ValueError):
        return set()


async def niko_badge_keys(bot, user_id: int) -> list[str]:
    """Return the Niko badge keys an account has, in display order."""
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return []
    if bot is None:
        return []

    # Imported here so the web app and the tests can import this module without
    # pulling in the whole cog tree.
    try:
        from cogs.staff.records import get_staff_role
        from cogs.staff.support_server import get_support_ids
        from utils.donations import is_supporter
    except Exception:
        return []

    found: set[str] = set()

    # 1. The bot owner, from the configured owner ids or a stored owner role.
    if user_id in OWNER_IDS:
        found.add("niko_owner")

    # 2. The stored staff role, which is what staff commands are gated on.
    staff_key = None
    try:
        staff_key = await get_staff_role(bot, user_id)
    except Exception:
        staff_key = None
    for role_key, badge in STAFF_BADGE_ROLES:
        if staff_key and role_key == staff_key:
            found.add(badge)

    # 3. A confirmed donation, which works even for someone who never joined
    #    the support server.
    try:
        if await is_supporter(bot, user_id):
            found.add("niko_supporter")
    except Exception:
        pass

    # 4. Support-server roles: community roles for everyone, the staff and
    #    specific roles for members the role sync has not reached yet.
    role_ids: set[int] = set()
    ids: dict = {}
    try:
        ids = (await get_support_ids(bot)).get("roles") or {}
    except Exception:
        ids = {}
    try:
        guild = bot.get_guild(SUPPORT_GUILD)
    except Exception:
        guild = None
    if guild is not None:
        try:
            member = guild.get_member(user_id) or await guild.fetch_member(user_id)
        except Exception:
            member = None
        role_ids = {role.id for role in getattr(member, "roles", ()) or ()}

    for role_key, badge in COMMUNITY_BADGE_ROLES:
        if _role_ids(ids, role_key) & role_ids:
            found.add(badge)
    # Every staff member also holds the umbrella role, so the specific role
    # badge wins and the umbrella only shows when it is all we can resolve.
    specific_staff = {
        badge
        for role_key, badge in STAFF_BADGE_ROLES
        if _role_ids(ids, role_key) & role_ids
    }
    found |= specific_staff
    if not specific_staff and _role_ids(ids, "staff") & role_ids:
        found.add("niko_staff")

    return [badge for badge in NIKO_BADGE_ORDER if badge in found]
