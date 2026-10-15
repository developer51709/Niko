"""Economy — the seasonal calendar behind the time-limited badges.

A seasonal badge carries its own window instead of a hard-coded date check::

    "season": {"label": "Halloween", "start": "10-24", "end": "11-01"}

Dates are ``MM-DD`` in local time with both ends inclusive, which keeps the
badge table readable and lets the same badge come back every year without anyone
editing it. Windows may wrap the new year (winter starts in December and ends in
January), so the arithmetic lives here rather than in every caller.

:func:`season_status` is the single entry point. It answers whether the window is
open right now and, when it is not, when it opens next: the bot needs the first
answer to decide whether a badge may unlock, and both the bot and the dashboard
need the second to explain why a badge is out of reach today.
"""

from __future__ import annotations

import calendar
import datetime as dt


def _as_datetime(now=None) -> dt.datetime:
    """Accept ``None`` (now), a ``datetime``/``date``, or unix seconds."""
    if now is None:
        return dt.datetime.now()
    if isinstance(now, dt.datetime):
        return now
    if isinstance(now, dt.date):
        return dt.datetime(now.year, now.month, now.day)
    try:
        return dt.datetime.fromtimestamp(float(now))
    except (TypeError, ValueError):
        return dt.datetime.now()


def _month_day(value) -> tuple[int, int]:
    """Parse an ``MM-DD`` string, rejecting anything a calendar cannot hold."""
    month, _, day = str(value).partition("-")
    try:
        month, day = int(month), int(day)
    except ValueError:
        raise ValueError(f"{value!r} is not an MM-DD date") from None
    if not 1 <= month <= 12 or not 1 <= day <= calendar.monthrange(2000, month)[1]:
        raise ValueError(f"{value!r} is not an MM-DD date")
    return month, day


def _boundary(year: int, month: int, day: int, *, end_of_day: bool = False) -> dt.datetime:
    """Midnight on ``month/day`` in ``year``, or the last second of that day.

    The day is clamped to the month's real length so a 29 February window is
    valid in a leap year and still parses in a common one.
    """
    moment = dt.datetime(year, month, min(day, calendar.monthrange(year, month)[1]))
    if end_of_day:
        moment += dt.timedelta(days=1, seconds=-1)
    return moment


def _window(season: dict, year: int) -> tuple[dt.datetime, dt.datetime]:
    """The window that starts in ``year`` — its end rolls over if it wraps."""
    start_month, start_day = _month_day(season["start"])
    end_month, end_day = _month_day(season["end"])
    wraps = (end_month, end_day) < (start_month, start_day)
    start = _boundary(year, start_month, start_day)
    end = _boundary(year + 1 if wraps else year, end_month, end_day, end_of_day=True)
    return start, end


def season_window(meta: dict, now=None) -> tuple[dt.datetime, dt.datetime] | None:
    """The open window for a badge, else the next one to open.

    ``None`` means the badge has no season and is always available.
    """
    season = meta.get("season")
    if not season:
        return None

    moment = _as_datetime(now)
    # A window that wraps the new year and is open today started last year.
    for year in (moment.year, moment.year - 1):
        start, end = _window(season, year)
        if start <= moment <= end:
            return (start, end)

    start, end = _window(season, moment.year)
    if start <= moment:
        return _window(season, moment.year + 1)
    return (start, end)


def season_status(meta: dict, now=None) -> dict | None:
    """Describe a badge's season, or ``None`` when it has no window.

    ``starts_at`` / ``ends_at`` are unix seconds for whichever occurrence is
    relevant: the one open now, or the next one to open.
    """
    window = season_window(meta, now)
    if window is None:
        return None

    start, end = window
    moment = _as_datetime(now)
    return {
        "label": str(meta["season"].get("label") or "Seasonal"),
        "active": start <= moment <= end,
        "starts_at": int(start.timestamp()),
        "ends_at": int(end.timestamp()),
    }


def season_open(meta: dict, now=None) -> bool:
    """Whether a badge may unlock right now. Always true without a season."""
    status = season_status(meta, now)
    return status is None or bool(status["active"])
