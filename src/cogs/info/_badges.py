"""Info — the Discord and Niko badge emojis shown on the userinfo card.

Which badges an account carries is decided in utils.member_badges, so the
userinfo card and the website's profile popovers can never disagree.
"""

from discord.ext import commands

from config.emojis import get_emoji
from utils.member_badges import boosting_badge_key, niko_badge_keys

# Niko badge key (utils.member_badges.NIKO_BADGE_ORDER) -> emoji name in
# config/emojis.py. Both lists are checked against each other in the tests, so a
# new role badge needs its PNG art and its emoji entry, nothing else.
_NIKO_BADGE_EMOJIS = {
    "niko_owner": "badge_owner",
    "niko_staff": "badge_staff",
    "niko_head_admin": "badge_head_admin",
    "niko_moderator": "badge_moderator",
    "niko_head_support": "badge_head_support",
    "niko_support": "badge_support",
    "niko_graphic_designer": "badge_graphic_designer",
    "niko_event_coordinator": "badge_event_coordinator",
    # Discord emoji names are capped at 32 characters, hence the short name.
    "niko_partnerships_promotions_lead": "badge_partnership_lead",
    "niko_partnership_manager": "badge_partnership_manager",
    "niko_supporter": "badge_supporter_role",
    "niko_bug_hunter": "badge_bug_hunter_role",
    "niko_partner": "badge_partner_role",
}

# One entry per Discord badge art in src/assets/emojis; the flag names are tried
# in order because discord.py renamed a few of them across versions.
_DISCORD_BADGE_FLAGS = (
    (("staff",), "staff_badge"),
    (("partner",), "partner_badge"),
    (("hypesquad_events",), "hypesquad_events"),
    (("bug_hunter_level_1", "bug_hunter"), "bug_hunter_badge"),
    (("hypesquad_bravery",), "hypesquad_bravery"),
    (("hypesquad_brilliance",), "hypesquad_briliance"),
    (("hypesquad_balance",), "hypesquad_balance"),
    (("early_supporter",), "early_supporter_badge"),
    (("bug_hunter_level_2",), "bug_hunter_gold_badge"),
    (("verified_bot_developer", "early_verified_developer"), "verified_developer_badge"),
    (("certified_moderator",), "certified_moderator_badge"),
    (("supports_commands",), "supports_commands_badge"),
    (("active_developer",), "active_developer_badge"),
)


async def _get_badges(bot: commands.Bot, user_id: int) -> list[str]:
    """Return the Niko badge emojis earned by user_id, in display order.

    Members who are not in the support server still get every badge that does
    not need it.
    """
    try:
        keys = await niko_badge_keys(bot, user_id)
    except Exception:
        return []
    return [
        get_emoji(_NIKO_BADGE_EMOJIS[key])
        for key in keys
        if key in _NIKO_BADGE_EMOJIS
    ]


def _get_discord_badges(target) -> list[str]:
    """Return the emojis for a member's Discord badges, in Discord's order."""
    pf = target.public_flags
    badges: list[str] = []
    seen: set[str] = set()
    for flags, ekey in _DISCORD_BADGE_FLAGS:
        if ekey in seen or not any(getattr(pf, flag, False) for flag in flags):
            continue
        seen.add(ekey)
        badges.append(get_emoji(ekey))
    # Discord draws the boosting badge last, for any active boost streak, and
    # every tier has its own artwork, so the streak picks the badge.
    boosting = boosting_badge_key(getattr(target, "premium_since", None))
    if boosting and boosting not in seen:
        seen.add(boosting)
        badges.append(get_emoji(boosting))
    return badges
