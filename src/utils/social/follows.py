"""Shared storage and formatting for the social notifier.

A "follow" is one social account a server wants announced in one channel. The
same rows are read and written from two places:

* ``src/cogs/notifier/cog.py`` — the poll loop that looks for new posts and the
  Discord setup panel,
* ``src/webapp/notifier_routes.py`` — the dashboard tab that manages the same
  rows over HTTP.

Both go through this module so the SQL lives in exactly one place and the
dashboard can never drift from what the poll loop expects.

``bot.cxn`` speaks a small SQL dialect that is translated into MongoDB when a
Mongo connection is configured, so statements here stay inside the shapes that
translator supports:

* ``INSERT OR REPLACE`` always lists every column, because the Mongo backend
  replaces the whole document — a partial insert would silently drop a follow's
  paused state.
* partial edits use ``UPDATE … SET`` with an explicit column list, whose
  placeholders are numbered before the ``WHERE`` ones.

Everything that is not storage is pure Python, so the dashboard can render a
follow without a Discord client.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

PLATFORM_ORDER = ("youtube", "twitch", "twitter", "tiktok", "bluesky", "reddit")

# ── Limits ───────────────────────────────────────────────────────────────────

#: Follows per server. Chosen so one server cannot monopolise the poll loop.
MAX_FOLLOWS_PER_GUILD = 25
#: Follows of the same platform per server, so a server keeps a varied feed.
MAX_FOLLOWS_PER_PLATFORM = 10
#: Characters allowed in a custom notification template.
MAX_TEMPLATE_LENGTH = 300
#: Consecutive failed checks before a follow is paused automatically.
FAILURE_LIMIT = 5
#: Accounts fetched at the same time inside one poll.
FETCH_CONCURRENCY = 4

TEMPLATE_PLACEHOLDERS = ("account", "platform", "title", "url")

#: Every column of the ``follows`` table, in insert order.
FOLLOW_COLUMNS = (
    "guild_id",
    "platform",
    "username",
    "channel_id",
    "template",
    "last_post_id",
    "enabled",
    "ping_role_id",
    "failures",
    "last_checked_at",
)

#: Columns the dashboard may edit after a follow exists.
EDITABLE_COLUMNS = ("channel_id", "template", "enabled", "ping_role_id")

#: Columns the poll loop writes back.
STATE_COLUMNS = ("last_post_id", "failures", "last_checked_at")

#: Every column ``update_follow`` accepts.
UPDATABLE_COLUMNS = EDITABLE_COLUMNS + STATE_COLUMNS


class FollowError(Exception):
    """Raised when a follow cannot be validated or stored."""


def utc_now() -> str:
    """Timestamp in the same format SQLite's ``datetime('now')`` produces."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# ── Parsing helpers ──────────────────────────────────────────────────────────

#: ``(?:^|[/.])`` matches a bare host, a scheme-qualified URL and a ``www.``
#: prefix, while still refusing a lookalike domain like ``notyoutube.com``.
_HOST_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"(?:^|[/.])(?:youtube\.com|youtu\.be)/", "youtube"),
    (r"(?:^|[/.])twitch\.tv/", "twitch"),
    (r"(?:^|[/.])(?:x\.com|twitter\.com)/", "twitter"),
    (r"(?:^|[/.])tiktok\.com/", "tiktok"),
    (r"(?:^|[/.])bsky\.app/|\.bsky\.social(?:$|/)", "bluesky"),
    (r"(?:^|[/.])reddit\.com/r/", "reddit"),
)


#: A bare domain is only ever a Bluesky handle — no other supported platform
#: names accounts that way.
_BARE_HANDLE_RE = re.compile(r"[a-z0-9][a-z0-9_.-]*\.[a-z]{2,}")


def detect_platform(raw: str) -> str | None:
    """Guess a platform from a pasted profile URL or handle.

    Only used to pre-fill the platform picker in the dashboard; the account is
    still validated by the platform's own API before anything is saved, so a
    wrong guess costs the user one click and never a bad row.
    """
    lowered = (raw or "").strip().lower()
    if not lowered:
        return None
    if lowered.startswith("r/"):
        return "reddit"
    for pattern, platform in _HOST_PATTERNS:
        if re.search(pattern, lowered):
            return platform
    if _BARE_HANDLE_RE.fullmatch(lowered):
        return "bluesky"
    # A bare @handle or plain name is ambiguous (YouTube, Twitch, TikTok and
    # Bluesky all use handles), so the caller picks instead of guessing.
    return None


def display_name(platform: str, username: str) -> str:
    """Human-readable name for a stored follow row."""
    if platform == "youtube":
        # Stored as 'DisplayName|ChannelID'; import lazily so this module keeps
        # working even if the YouTube helper is unavailable at import time.
        from utils.social.youtube import display_name as youtube_display

        return youtube_display(username)
    if platform == "reddit":
        return f"r/{username}"
    return f"@{username}"


def sanitize_username(value: str, limit: int = 100) -> str:
    """Trim a stored account name and reject anything unusably long."""
    cleaned = (value or "").strip()
    if not cleaned or len(cleaned) > limit:
        raise FollowError("That account name is not valid.")
    return cleaned


# ── Templates ────────────────────────────────────────────────────────────────

_PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")


def template_placeholders(template: str) -> set[str]:
    """Return the ``{placeholder}`` names used by a template."""
    return set(_PLACEHOLDER_RE.findall(template or ""))


def validate_template(template: str | None) -> str:
    """Check a custom announcement template and return it trimmed.

    Unknown placeholders are rejected instead of being left in the message, so
    a typo is reported in the dashboard rather than posted to Discord.
    """
    text = (template or "").strip()
    if len(text) > MAX_TEMPLATE_LENGTH:
        raise FollowError(f"Templates are limited to {MAX_TEMPLATE_LENGTH} characters.")
    unknown = template_placeholders(text) - set(TEMPLATE_PLACEHOLDERS)
    if unknown:
        allowed = ", ".join(f"{{{name}}}" for name in TEMPLATE_PLACEHOLDERS)
        raise FollowError(f"Unknown template placeholder(s): {sorted(unknown)}. Use {allowed}.")
    return text


def render_template(
    template: str,
    *,
    account: str,
    platform: str,
    title: str = "",
    url: str = "",
) -> str:
    """Fill a validated template for one post."""
    if not template:
        return ""
    values = {
        "account": account,
        "platform": platform.capitalize(),
        "title": title or "",
        "url": url or "",
    }
    return _PLACEHOLDER_RE.sub(lambda match: values.get(match.group(1), ""), template)


# ── Row helpers ──────────────────────────────────────────────────────────────

def _as_text(value) -> str | None:
    if value is None or value == "":
        return None
    return str(value)


def _as_bool(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() not in ("0", "false", "no", "")
    return bool(value)


def row_to_follow(row) -> dict:
    """Normalise a ``follows`` row (SQLite or MongoDB) for JSON and the cog."""
    data = dict(row)
    platform = str(data.get("platform") or "")
    username = str(data.get("username") or "")
    return {
        "platform": platform,
        "username": username,
        "display": display_name(platform, username) if platform and username else username,
        "channel_id": _as_text(data.get("channel_id")),
        "template": str(data.get("template") or ""),
        "ping_role_id": _as_text(data.get("ping_role_id")),
        "enabled": _as_bool(data.get("enabled")),
        "last_post_id": _as_text(data.get("last_post_id")),
        "failures": int(data.get("failures") or 0),
        "last_checked_at": _as_text(data.get("last_checked_at")),
    }


# ── Queries ──────────────────────────────────────────────────────────────────

async def list_follows(cxn, guild_id=None) -> list[dict]:
    """Return every follow, optionally limited to one server."""
    if guild_id is None:
        rows = await cxn.fetch(
            "SELECT guild_id, platform, username, channel_id, template, "
            "last_post_id, enabled, ping_role_id, failures, last_checked_at FROM follows"
        )
    else:
        rows = await cxn.fetch(
            "SELECT guild_id, platform, username, channel_id, template, "
            "last_post_id, enabled, ping_role_id, failures, last_checked_at "
            "FROM follows WHERE guild_id = $1",
            int(guild_id),
        )
    follows = []
    for row in rows:
        follow = row_to_follow(row)
        follow["guild_id"] = _as_text(dict(row).get("guild_id"))
        follows.append(follow)
    follows.sort(key=lambda item: (PLATFORM_ORDER.index(item["platform"]) if item["platform"] in PLATFORM_ORDER else 99, item["display"].lower()))
    return follows


async def get_follow(cxn, guild_id, platform: str, username: str) -> dict | None:
    """Return one follow row, or ``None``."""
    row = await cxn.fetchrow(
        "SELECT guild_id, platform, username, channel_id, template, last_post_id, "
        "enabled, ping_role_id, failures, last_checked_at FROM follows "
        "WHERE guild_id = $1 AND platform = $2 AND username = $3",
        int(guild_id),
        platform,
        username,
    )
    return row_to_follow(row) if row else None


async def platform_counts(cxn, guild_id) -> dict[str, int]:
    """Count follows per platform for one server."""
    follows = await list_follows(cxn, guild_id)
    counts: dict[str, int] = {}
    for follow in follows:
        counts[follow["platform"]] = counts.get(follow["platform"], 0) + 1
    return counts


async def create_follow(
    cxn,
    *,
    guild_id,
    platform: str,
    username: str,
    channel_id,
    last_post_id=None,
    template: str = "",
    ping_role_id=None,
    enabled: bool = True,
) -> dict:
    """Insert a new follow, seeding the current post so nothing old is posted."""
    await cxn.execute(
        "INSERT OR REPLACE INTO follows "
        "(guild_id, platform, username, channel_id, template, last_post_id, enabled, ping_role_id, failures, last_checked_at) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
        int(guild_id),
        platform,
        sanitize_username(username),
        int(channel_id),
        validate_template(template),
        last_post_id,
        1 if enabled else 0,
        int(ping_role_id) if ping_role_id else None,
        0,
        None,
    )
    created = await get_follow(cxn, guild_id, platform, username)
    if created is None:
        raise FollowError("That follow could not be saved.")
    return created


async def update_follow(cxn, *, guild_id, platform: str, username: str, **fields) -> dict | None:
    """Apply a partial edit to an existing follow and return the new row."""
    updates = {key: value for key, value in fields.items() if key in UPDATABLE_COLUMNS}
    if not updates:
        return await get_follow(cxn, guild_id, platform, username)
    if bool(updates.get("enabled")) and "failures" not in updates:
        # Switching a follow back on starts its health record over. Keeping the
        # count that paused it would pause it again on the very next hiccup, and
        # the panel would keep showing stale failed checks on a working account.
        updates["failures"] = 0
    assignments = []
    args: list = []
    for column, value in updates.items():
        if column in ("channel_id", "ping_role_id"):
            value = int(value) if value not in (None, "") else None
        elif column == "enabled":
            value = 1 if value else 0
        elif column == "template":
            value = validate_template(value)
        elif column == "failures":
            value = int(value or 0)
        assignments.append(f"{column} = ${len(args) + 1}")
        args.append(value)
    where_start = len(args)
    args.extend([int(guild_id), platform, username])
    await cxn.execute(
        f"UPDATE follows SET {', '.join(assignments)} "
        f"WHERE guild_id = ${where_start + 1} AND platform = ${where_start + 2} AND username = ${where_start + 3}",
        *args,
    )
    return await get_follow(cxn, guild_id, platform, username)


async def delete_follow(cxn, *, guild_id, platform: str, username: str) -> bool:
    """Remove a follow. Returns ``False`` when it was not there."""
    existing = await get_follow(cxn, guild_id, platform, username)
    if existing is None:
        return False
    await cxn.execute(
        "DELETE FROM follows WHERE guild_id = $1 AND platform = $2 AND username = $3",
        int(guild_id),
        platform,
        username,
    )
    return True


async def rename_follow(cxn, *, guild_id, platform: str, username: str, new_username: str) -> bool:
    """Re-point a follow at a corrected account name.

    Used by the poll loop to repair stale YouTube display names. A rename that
    would collide with an already-followed account is skipped, because the
    account is already tracked under its stored name.
    """
    if not new_username or new_username == username:
        return False
    if await get_follow(cxn, guild_id, platform, new_username) is not None:
        return False
    await cxn.execute(
        "UPDATE follows SET username = $1 WHERE guild_id = $2 AND platform = $3 AND username = $4",
        new_username,
        int(guild_id),
        platform,
        username,
    )
    return await get_follow(cxn, guild_id, platform, new_username) is not None


async def record_check(
    cxn,
    *,
    guild_id,
    platform: str,
    username: str,
    failures: int,
    last_checked_at: str,
) -> None:
    """Store a poll result so the dashboard can show per-account health."""
    await update_follow(
        cxn,
        guild_id=guild_id,
        platform=platform,
        username=username,
        failures=failures,
        last_checked_at=last_checked_at,
    )


# ── Per-server settings ──────────────────────────────────────────────────────

DEFAULT_NOTIFIER_CONFIG = {
    "enabled": True,
    "default_channel_id": None,
    "ping_role_id": None,
}


def _config_from_row(row) -> dict:
    data = dict(row) if row else {}
    return {
        "enabled": _as_bool(data.get("enabled", 1)),
        "default_channel_id": _as_text(data.get("default_channel_id")),
        "ping_role_id": _as_text(data.get("ping_role_id")),
    }


async def get_notifier_config(cxn, guild_id) -> dict:
    """Read one server's notifier settings, falling back to defaults."""
    try:
        row = await cxn.fetchrow(
            "SELECT enabled, default_channel_id, ping_role_id FROM notifier_config WHERE guild_id = $1",
            int(guild_id),
        )
    except Exception:
        return dict(DEFAULT_NOTIFIER_CONFIG)
    if row is None:
        return dict(DEFAULT_NOTIFIER_CONFIG)
    return _config_from_row(row)


async def save_notifier_config(
    cxn,
    guild_id,
    *,
    enabled=None,
    default_channel_id=None,
    ping_role_id=None,
) -> dict:
    """Persist one server's notifier settings.

    ``None`` means "leave unchanged"; pass ``""`` to clear a channel or role.
    """
    current = await get_notifier_config(cxn, guild_id)

    def resolve(value, previous):
        if value is None:
            return previous
        if value == "":
            return None
        return str(value)

    next_enabled = current["enabled"] if enabled is None else bool(enabled)
    next_channel = resolve(default_channel_id, current["default_channel_id"])
    next_role = resolve(ping_role_id, current["ping_role_id"])

    await cxn.execute(
        "INSERT OR REPLACE INTO notifier_config "
        "(guild_id, enabled, default_channel_id, ping_role_id, updated_at) "
        "VALUES ($1, $2, $3, $4, datetime('now'))",
        int(guild_id),
        1 if next_enabled else 0,
        int(next_channel) if next_channel else None,
        int(next_role) if next_role else None,
    )
    return await get_notifier_config(cxn, guild_id)


async def pause_guild_notifications(cxn, guild_id) -> bool:
    """Switch one server's social notifications off, preserving its settings.

    Used when a guild is blacklisted: announcements are a Niko feature, so a
    blocked server must stop posting. The server-wide switch is the single flag
    the poll loop honours for every account, and the saved default channel and
    ping role are left in place for the day the blacklist is lifted.

    Returns ``True`` only when something was actually paused, so a caller can
    tell a real change from a no-op. A server with no follows is left alone
    rather than given a config row it never had.
    """
    follows = await list_follows(cxn, guild_id)
    if not follows:
        return False
    config = await get_notifier_config(cxn, guild_id)
    if config["enabled"] is False:
        return False
    await save_notifier_config(cxn, guild_id, enabled=False)
    return True
