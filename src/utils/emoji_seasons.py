"""Which seasonal emoji variant, if any, is active today.

Seasonal art is uploaded once per variant under a suffixed name
(``heart_christmas``), so switching seasons is a lookup change in
``config.emojis`` rather than a Discord delete-and-re-upload. Outside a
season window the unsuffixed emoji is used, which is the generic set.

The windows are inclusive and deliberately short: the generic set should be
the default for almost the whole year. A Christmas window that spans New
Year's Day needs the year-boundary branch below.
"""

from __future__ import annotations

from datetime import date

#: General-purpose emojis with seasonal variants. State indicators (ticks,
#: crosses, warnings, locks, plus/minus, thumbs and verification), machine
#: stats and per-event log marks are kept static so their colour still means
#: the same thing all year. Keep this in step with SEASONAL_EMOJIS in
#: scripts/build-emoji-icons.mjs.
SEASONAL_BASES = frozenset(
    {
        # Celebration and rewards.
        "heart",
        "gift",
        "star",
        "welcome",
        "giveaway",
        "premium",
        "ticket",
        "trophy",
        "economy",
        "games",
        # Navigation and structure.
        "home",
        "general",
        "categories",
        "settings",
        "docs",
        "website",
        "notepad",
        "scroll",
        "stats",
        "support",
        "arrow_left",
        "arrow_right",
        # People and identity.
        "user",
        "join",
        "leave",
        "invite",
        "participants",
        "ai",
        "bot",
        "bug",
        "sad",
        # Content and utility.
        "message",
        "image",
        "link",
        "megaphone",
        "lightbulb",
        "edit",
        "trash",
        "broom",
        "moderation",
        "automod",
        "utility",
        # Media controls.
        "play",
        "pause",
        "stop",
        "skip",
        "rewind",
        "shuffle",
        "loop",
        "queue",
        "volume_down",
        "volume_up",
        "autoplay",
        "refresh",
        "music",
        "voicemaster",
        "disconnect",
        # Progression and activities.
        "leveling",
        "gambling",
        "paint",
        "reminder",
        "duration",
    }
)

#: season -> ((start month, start day), (end month, end day)), inclusive.
SEASON_WINDOWS = {
    "halloween": ((10, 1), (11, 2)),
    "christmas": ((12, 1), (1, 6)),
    "valentine": ((2, 1), (2, 15)),
}


def active_season(day: date | None = None) -> str | None:
    """Return ``"christmas"``, ``"halloween"``, ``"valentine"`` or ``None``.

    ``day`` is injectable so the rotation can be tested without freezing the
    clock. Christmas wraps the year boundary; the other windows do not.
    """
    current = day or date.today()
    month_day = (current.month, current.day)

    for season, ((start_month, start_day), (end_month, end_day)) in SEASON_WINDOWS.items():
        start = (start_month, start_day)
        end = (end_month, end_day)
        if start <= end:
            if start <= month_day <= end:
                return season
        elif month_day >= start or month_day <= end:
            return season
    return None


def seasonal_variant(name: str, day: date | None = None) -> str | None:
    """The active suffixed name for ``name``, or ``None`` outside its season."""
    season = active_season(day)
    if season is None or name not in SEASONAL_BASES:
        return None
    return f"{name}_{season}"
