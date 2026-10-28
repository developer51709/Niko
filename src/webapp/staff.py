"""Staff presence, identity, roster rows, and the public profile links shown on
the team pages."""

from urllib.parse import urlparse
import json
import sqlite3
import time
from cogs.staff.staff import STAFF_ROLES
from config.ids import OWNER_IDS
from flask import session
from . import database, runtime


_staff_user_identity_cache: dict[str, tuple[float, dict[str, str | None]]] = {}

_STAFF_USER_IDENTITY_CACHE_TTL = 600

STAFF_PRIORITY = {"owner": 100, "head_admin": 90, "graphic_designer": 80, "head_support": 70, "moderator": 60, "support": 50}


def _presence_members(user_id: str, bot=None) -> list:
    """Every cached member for a user, richest live presence first.

    Discord presence is cached on each ``Member`` and can differ by guild. The
    first guild in ``bot.guilds`` is not guaranteed to be the guild where a
    member's activity was received, which previously made some roles (notably
    Head Admins) appear without Spotify/custom status data. Both the staff cards
    and the Discord profile popups read presence through this one list so the
    two surfaces always agree. Route modules that snapshot their own bot pass it
    explicitly.
    """
    bot = runtime._discord_bot if bot is None else bot
    members = []
    if bot is not None:
        for guild in getattr(bot, "guilds", ()) or ():
            try:
                candidate = guild.get_member(int(user_id))
            except (AttributeError, TypeError, ValueError):
                continue
            if candidate is not None:
                members.append(candidate)

    def presence_score(candidate) -> tuple[int, int, int]:
        raw_status = getattr(candidate, "status", "offline")
        status = getattr(raw_status, "name", None) or str(raw_status)
        status = status.rsplit(".", 1)[-1].lower()
        try:
            activities = getattr(candidate, "activities", ()) or ()
        except Exception:
            activities = ()
        has_custom = any(type(item).__name__.lower() == "customactivity" for item in activities)
        # Prefer activity/custom-status data, then an active presence, and keep
        # the guild order as a stable tie-breaker.
        return (int(bool(activities)), int(has_custom), int(status != "offline"))

    return sorted(members, key=presence_score, reverse=True)


def _presence_member(user_id: str, bot=None):
    """The cached member carrying a user's richest live presence, or ``None``."""
    members = _presence_members(user_id, bot)
    return members[0] if members else None

_CUSTOM_STATUS_PLACEHOLDER = "custom status"


def custom_status_text(activity) -> str | None:
    """The text of a custom status, or ``None`` when it only carries an emoji.

    Discord omits ``state`` from an emoji-only custom status, and discord.py
    then fills both ``state`` and ``name`` with the literal placeholder
    "Custom Status". Rendering either one as the text wrote that placeholder
    into the profile popup beside the emoji instead of showing the emoji alone.
    """
    for attribute in ("state", "name"):
        value = getattr(activity, attribute, None)
        text = str(value).strip() if value is not None else ""
        if text and text.casefold() != _CUSTOM_STATUS_PLACEHOLDER:
            return text
    return None


def _staff_identity(user_id: str) -> dict:
    """Resolve a staff member's global identity and the richest live presence."""
    ordered_members = _presence_members(user_id)
    member = ordered_members[0] if ordered_members else None
    user = member or (runtime._discord_bot.get_user(int(user_id)) if runtime._discord_bot is not None else None)
    cached_identity = None
    if user is None:
        cached_identity_entry = _staff_user_identity_cache.get(str(user_id))
        if cached_identity_entry and time.time() - cached_identity_entry[0] < _STAFF_USER_IDENTITY_CACHE_TTL:
            cached_identity = cached_identity_entry[1]
        elif runtime._discord_bot is not None:
            try:
                # The gateway user cache can be empty right after a restart.
                # Resolve identity through Discord REST instead, then cache it
                # to avoid polling Discord every 5s.
                user = runtime.run_on_bot_loop(runtime._discord_bot.fetch_user(int(user_id)))
                avatar = getattr(user, "display_avatar", None)
                cached_identity = {
                    "name": getattr(user, "global_name", None) or getattr(user, "name", None),
                    "username": getattr(user, "name", None),
                    "avatar_url": str(avatar.url) if avatar is not None else None,
                }
                _staff_user_identity_cache[str(user_id)] = (time.time(), cached_identity)
            except Exception:
                user = None
    activities = []
    custom_status = None
    seen_activities = set()
    def serialize_emoji(emoji):
        if emoji is None:
            return None
        emoji_id = getattr(emoji, "id", None)
        emoji_name = getattr(emoji, "name", None) or str(emoji)
        return {
            "kind": "custom" if emoji_id else "unicode",
            "value": str(emoji_id) if emoji_id else emoji_name,
            "name": emoji_name,
            "animated": bool(getattr(emoji, "animated", False)),
        }

    for presence_member in ordered_members:
        for activity in getattr(presence_member, "activities", ()) or ():
            activity_type = getattr(getattr(activity, "type", None), "name", None) or str(getattr(activity, "type", "")).rsplit(".", 1)[-1].lower()
            class_name = type(activity).__name__.lower()

            if class_name == "customactivity" or activity_type in {"custom", "customstatus", "custom_activity"}:
                if custom_status is None:
                    custom_status = {
                        "text": custom_status_text(activity),
                        "emoji": serialize_emoji(getattr(activity, "emoji", None)),
                    }
                continue

            # discord.py exposes Spotify and Streaming as dedicated activity
            # classes with attributes that differ from the generic Activity class.
            activity_key = (class_name, getattr(activity, "name", None), getattr(activity, "title", None), getattr(activity, "state", None), getattr(activity, "url", None))
            if activity_key in seen_activities:
                continue
            seen_activities.add(activity_key)

            if class_name == "spotify":
                # The track window drives the progress bar on the profile card.
                # discord.py raises when the presence omits timestamps, so both
                # bounds are read defensively.
                try:
                    track_start = getattr(activity, "start", None)
                    track_end = getattr(activity, "end", None)
                except KeyError:
                    track_start = track_end = None
                activities.append({
                    "kind": "spotify",
                    "type": "listening",
                    "name": "Spotify",
                    "details": getattr(activity, "title", None),
                    "state": getattr(activity, "artist", None),
                    "url": getattr(activity, "track_url", None),
                    "platform": "Spotify",
                    "image_url": getattr(activity, "album_cover_url", None),
                    "start": track_start.isoformat() if track_start else None,
                    "end": track_end.isoformat() if track_end else None,
                })
                continue
            if class_name == "streaming":
                activities.append({
                    "kind": "streaming",
                    "type": "streaming",
                    "name": getattr(activity, "game", None) or getattr(activity, "name", None) or "Live stream",
                    "details": getattr(activity, "platform", None),
                    "state": None,
                    "url": getattr(activity, "url", None),
                    "platform": getattr(activity, "platform", None),
                    "image_url": None,
                })
                continue

            name = getattr(activity, "name", None)
            if name:
                activities.append({
                    "kind": "activity",
                    "type": activity_type,
                    "name": name,
                    "details": getattr(activity, "details", None),
                    "state": getattr(activity, "state", None),
                    "url": getattr(activity, "url", None),
                    "platform": None,
                    "image_url": None,
                })
    raw_status = getattr(member, "status", "offline") if member is not None else "offline"
    # discord.py may expose this as a Status enum (``Status.online``) or a
    # string depending on the cached object/version. Keep the API stable for
    # the frontend by returning the normalized enum value.
    status = getattr(raw_status, "name", None) or str(raw_status)
    status = status.rsplit(".", 1)[-1].lower()
    return {
        "id": str(user_id),
        # Use the global Discord display name, never a guild nickname from
        # whichever guild was checked first.
        "name": getattr(member, "global_name", None) or getattr(getattr(member, "_user", None), "global_name", None) or getattr(user, "global_name", None) or getattr(user, "name", None) or (cached_identity or {}).get("name") or f"Staff member {user_id}",
        "username": getattr(user, "name", None) or (cached_identity or {}).get("username"),
        "avatar_url": str(getattr(getattr(user, "display_avatar", None), "url", "")) or (cached_identity or {}).get("avatar_url"),
        "status": status,
        "status_label": {"online": "Online", "idle": "Idle", "dnd": "Do Not Disturb", "offline": "Offline"}.get(status, status.title()),
        "activities": activities,
        "custom_status": custom_status,
        # Keep the first activity for older clients while the richer fields
        # above are consumed by the current Team page.
        "activity": activities[0]["name"] if activities else None,
    }


def _staff_role_label(role: str) -> str:
    """Turn the persisted role key into the public label without frontend role logic."""
    return STAFF_ROLES.get(role, role.replace("_", " ").strip().title() or "Staff")


def _normalize_public_links(raw) -> list[dict]:
    """Return safe public profile links from the stored JSON value."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (TypeError, ValueError):
            return []
    if not isinstance(raw, list):
        return []
    links = []
    for link in raw[:10]:
        if not isinstance(link, dict):
            continue
        link_type = str(link.get("type", "")).strip()
        url = str(link.get("url", "")).strip()
        parsed = urlparse(url)
        if link_type and parsed.scheme in {"http", "https"} and parsed.netloc:
            links.append({"type": link_type, "label": str(link.get("label") or link_type.title()), "url": url})
    return links

STAFF_STATUS_LABELS = {
    "active": "Active",
    "suspended": "Suspended",
    "former": "Former staff",
}

_STAFF_CARD_COLUMNS = ("card_theme", "card_accent", "card_show_status")

_STAFF_ROW_COLUMNS = (
    "user_id", "role", "public_name", "public_bio", "public_avatar_url",
    "public_banner_url", "public_links", "public_visible", "staff_status",
    "status_reason", "status_changed_by", "status_changed_at",
    *_STAFF_CARD_COLUMNS,
)

# Card presentation is the newest addition, so a database that has not run its
# migration yet is read without those columns first — losing them is harmless,
# while losing the lifecycle columns would make a suspended profile public.
_STAFF_PROFILE_ROW_COLUMNS = tuple(
    column for column in _STAFF_ROW_COLUMNS if column not in _STAFF_CARD_COLUMNS
)

_STAFF_LEGACY_ROW_COLUMNS = _STAFF_ROW_COLUMNS[:8]

_STAFF_READ_COLUMN_SETS = (
    _STAFF_ROW_COLUMNS, _STAFF_PROFILE_ROW_COLUMNS, _STAFF_LEGACY_ROW_COLUMNS,
)


def _staff_status(row) -> str:
    value = str(row.get("staff_status") or "active").strip().lower()
    return value if value in STAFF_STATUS_LABELS else "active"


def _staff_row(row) -> dict:
    role = str(row.get("role"))
    identity = _staff_identity(str(row.get("user_id")))
    status = _staff_status(row)
    profile_visible = bool(row.get("public_visible", 1))
    return {
        **identity,
        "role": role,
        "role_label": "Owner" if role == "owner" else _staff_role_label(role),
        "bio": row.get("public_bio"),
        # Names and avatars always come from Discord; profile presentation is
        # staff-customizable on the website.
        "public_banner_url": row.get("public_banner_url"),
        "public_links": _normalize_public_links(row.get("public_links")),
        "visible": profile_visible and status == "active",
        "profile_visible": profile_visible,
        # Presentation for the GitHub README card (`/staff/<id>/card.svg`).
        "card": {
            "theme": "light" if str(row.get("card_theme") or "").strip().lower() == "light" else "dark",
            "accent": str(row.get("card_accent") or "").strip().lstrip("#").upper() or None,
            "show_status": row.get("card_show_status") is None or bool(row.get("card_show_status")),
        },
        "staff_status": status,
        "staff_status_label": STAFF_STATUS_LABELS[status],
        "status_reason": row.get("status_reason"),
        "status_changed_by": str(row["status_changed_by"]) if row.get("status_changed_by") is not None else None,
        "status_changed_at": row.get("status_changed_at"),
    }


def _load_staff_records(*, include_inactive: bool = False) -> list[dict]:
    """Load persisted staff records and enrich them with live Discord data.

    Staff roles live in the bot's active database pool. Do not fall back to
    SQLite only when the pool returns an empty list: a web process can have a
    local SQLite file with only the owner seed row while the active deployment
    stores the other roles elsewhere. We also isolate malformed rows so one
    legacy record cannot hide the rest of the roster.
    """
    by_id: dict[str, dict] = {}

    def add_raw(raw, *, overwrite: bool = True) -> None:
        try:
            row = dict(raw)
            user_id = str(row.get("user_id", "")).strip()
            role = str(row.get("role", "")).strip()
            if not user_id or not role:
                return
            # The live bot database is authoritative. A stale local SQLite
            # copy must never make a suspended profile public again.
            if not overwrite and user_id in by_id:
                return
            numeric_user_id = int(user_id)
            if numeric_user_id in OWNER_IDS:
                row["role"] = role = "owner"
                row["staff_status"] = "active"
            # Only configured staff roles should appear. Keep the owner seed in
            # the same roster as database-backed roles.
            if role not in STAFF_ROLES and role != "owner":
                return
            status = _staff_status(row)
            if not include_inactive and status != "active":
                return
            item = _staff_row({**row, "user_id": user_id, "role": role})
            by_id[user_id] = item
        except (TypeError, ValueError, KeyError):
            # A single old/incomplete record must not suppress other roles.
            return

    bot_pool = bool(runtime._discord_bot is not None and getattr(runtime._discord_bot, "cxn", None))
    bot_read_ok = True
    if bot_pool:
        async def read_staff():
            last_error = None
            for columns in _STAFF_READ_COLUMN_SETS:
                try:
                    return await runtime._discord_bot.cxn.fetch(
                        f"SELECT {', '.join(columns)} FROM staff_members"
                    )
                except Exception as exc:
                    # Only a pre-migration schema may fall back to a narrower
                    # column set. A transient database failure must not make a
                    # suspended record look active.
                    message = str(exc).lower()
                    if "card_" not in message and "staff_status" not in message:
                        raise
                    last_error = exc
            raise last_error
        try:
            for row in runtime.run_on_bot_loop(read_staff()):
                add_raw(row)
        except Exception:
            # The live roster is authoritative for staff privacy. If it cannot
            # be read, do not substitute a stale local row that may still say
            # a suspended member is active.
            bot_read_ok = False

    # Also read the local store and merge it instead of using it as an
    # all-or-nothing fallback. This covers web-only processes and prevents the
    # owner seed row from masking other staff roles.
    conn = database.sqlite_connect() if (not bot_pool or bot_read_ok) else None
    try:
        if conn:
            raw_rows = None
            columns = None
            for candidates in _STAFF_READ_COLUMN_SETS:
                try:
                    raw_rows = conn.execute(
                        f"SELECT {', '.join(candidates)} FROM staff_members"
                    ).fetchall()
                    columns = candidates
                    break
                except sqlite3.Error as exc:
                    message = str(exc).lower()
                    if "card_" not in message and "staff_status" not in message:
                        raise
            for raw in raw_rows or ():
                add_raw(dict(zip(columns, raw)), overwrite=False)
    except sqlite3.Error:
        pass
    finally:
        if conn:
            conn.close()

    for user_id in OWNER_IDS:
        user_id = str(user_id)
        if user_id not in by_id:
            add_raw({"user_id": user_id, "role": "owner", "public_visible": 1})

    if include_inactive:
        status_order = {"active": 0, "suspended": 1, "former": 2}
        return sorted(
            by_id.values(),
            key=lambda item: (
                status_order.get(item["staff_status"], 3),
                -STAFF_PRIORITY.get(item["role"], 40),
                (item.get("name") or "").casefold(),
            ),
        )
    return sorted(
        (row for row in by_id.values() if row["visible"]),
        key=lambda item: -STAFF_PRIORITY.get(item["role"], 40),
    )


def _load_staff_rows() -> list[dict]:
    """Public team roster: active staff with a visible profile only."""
    return _load_staff_records()


def _load_staff_management_rows() -> list[dict]:
    """Owner roster including suspended and former staff profiles."""
    return _load_staff_records(include_inactive=True)


def _current_staff_role() -> str | None:
    user_id = str(session.get("user", {}).get("id", ""))
    if not user_id:
        return None
    try:
        numeric_user_id = int(user_id)
        if numeric_user_id in OWNER_IDS:
            return "owner"
    except (TypeError, ValueError):
        return None

    # Staff authorization must use the same live database as the bot. The
    # previous SQLite-only lookup denied valid staff on Mongo/live-pool setups.
    if runtime._discord_bot is not None and getattr(runtime._discord_bot, "cxn", None):
        async def read_role():
            try:
                return await runtime._discord_bot.cxn.fetchrow(
                    "SELECT role, staff_status FROM staff_members WHERE user_id = $1",
                    int(user_id),
                )
            except Exception as exc:
                if "staff_status" not in str(exc).lower():
                    raise
                return await runtime._discord_bot.cxn.fetchrow(
                    "SELECT role FROM staff_members WHERE user_id = $1", int(user_id)
                )
        try:
            row = runtime.run_on_bot_loop(read_role())
            if row and row.get("role"):
                if _staff_status(row) != "active":
                    return None
                return str(row["role"])
        except Exception:
            # The live database is the authority for staff access. Failing
            # closed is safer than a stale local role during an outage.
            return None

    conn = database.sqlite_connect()
    try:
        if not conn:
            return None
        try:
            row = conn.execute(
                "SELECT role, staff_status FROM staff_members WHERE user_id = ?",
                (int(user_id),),
            ).fetchone()
        except sqlite3.Error as exc:
            if "staff_status" not in str(exc).lower():
                raise
            row = conn.execute(
                "SELECT role FROM staff_members WHERE user_id = ?", (int(user_id),)
            ).fetchone()
        if not row:
            return None
        if len(row) > 1 and str(row[1] or "active").strip().lower() != "active":
            return None
        return str(row[0]) if row[0] else None
    except (TypeError, ValueError, sqlite3.Error):
        return None
    finally:
        if conn:
            conn.close()
