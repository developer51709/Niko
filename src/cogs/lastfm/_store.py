"""Last.fm — stored account links and the per-guild artist index.

Two tables only, and both exist to keep the commands fast and honest:

``lastfm_users``
    one row per member, holding the Last.fm handle they linked. Nothing else
    about a member is stored here — their library is read from Last.fm on
    demand. A link made through last.fm's web auth also keeps the session key
    Last.fm returned, which is the proof the member owns the account (and the
    credential a write action such as loving a track would need).

``lastfm_artist_index``
    one row per (guild, member, artist) with that member's playcount. Last.fm
    cannot answer "who in this server listens to this artist", so fmbot and
    this cog both keep their own index. Rows are written from data the member
    already fetched (their own top artists), which is why the index fills up
    naturally: the first time somebody runs ``/fm`` in a server, their top
    artists become queryable for everyone there.

Artist names are matched through :func:`artist_key`, a casefolded, whitespace
folded form. Last.fm is inconsistent about punctuation and casing between
endpoints, and a leaderboard that misses a member because they scrobbled
"The Beatles" instead of "the beatles" is a bug, not a feature.
"""

from __future__ import annotations

import re
import time
from typing import Iterable, Sequence

#: Rows written by one index pass. ``/fm update`` asks Last.fm for 100 artists
#: per page and walks a few pages; this caps the write burst so a first-time
#: index of a huge library stays a couple of seconds, not thirty.
INDEX_BATCH = 100

#: How long an index row is trusted before ``whoknows`` refreshes it.
INDEX_TTL = 6 * 60 * 60

_SPACE_RE = re.compile(r"\s+")


def artist_key(name: str) -> str:
    """The comparison key for an artist name (``The Beatles `` → ``the beatles``)."""
    return _SPACE_RE.sub(" ", str(name or "").casefold()).strip()


def now() -> float:
    return time.time()


# ── Account links ──────────────────────────────────────────────────────────

async def get_account(pool, user_id: int) -> str | None:
    """The Last.fm handle this member linked, if any."""
    row = await pool.fetchrow(
        "SELECT username, checked_at FROM lastfm_users WHERE user_id = $1",
        int(user_id),
    )
    return row["username"] if row else None


async def get_account_row(pool, user_id: int) -> dict | None:
    """The link row (handle, timestamps and whether it was OAuth-verified)."""
    row = await pool.fetchrow(
        "SELECT user_id, username, session_key, linked_at, checked_at "
        "FROM lastfm_users WHERE user_id = $1",
        int(user_id),
    )
    return dict(row) if row else None


async def get_accounts(pool, user_ids: Iterable[int]) -> dict[int, str]:
    """Map member id → handle for the members that have linked an account."""
    ids = [int(uid) for uid in user_ids]
    if not ids:
        return {}
    found: dict[int, str] = {}
    for start in range(0, len(ids), 90):
        chunk = ids[start:start + 90]
        placeholders = ", ".join("$%d" % (index + 1) for index in range(len(chunk)))
        rows = await pool.fetch(
            f"SELECT user_id, username FROM lastfm_users WHERE user_id IN ({placeholders})",
            *chunk,
        )
        for row in rows:
            found[int(row["user_id"])] = row["username"]
    return found


async def set_account(
    pool, user_id: int, username: str, *, session_key: str | None = None
) -> None:
    """Link (or relink) a member's Last.fm handle.

    ``session_key`` is only present for a link made through last.fm's web auth.
    When it is omitted the stored key is left alone: typing a handle again does
    not prove ownership, so it must not erase the proof an earlier approval
    gave. In the other direction a fresh approval always replaces it.

    Typing a *different* handle is the one case that clears the key. The
    approval described the old account, and keeping it would attach a valid
    session for one member's Last.fm account to somebody else's row.
    """
    stamp = now()
    if session_key is None:
        existing = None
        try:
            existing = await get_account_row(pool, int(user_id))
        except Exception:
            existing = None
        if existing and str(existing.get("session_key") or ""):
            previous = str(existing.get("username") or "").casefold()
            if previous and previous != str(username).casefold():
                await pool.execute(
                    "UPDATE lastfm_users SET session_key = NULL WHERE user_id = $1",
                    int(user_id),
                )
        await pool.execute(
            "INSERT INTO lastfm_users (user_id, username, linked_at, checked_at) "
            "VALUES ($1, $2, $3, $4) "
            "ON CONFLICT (user_id) DO UPDATE SET username = $5, checked_at = $6",
            int(user_id), str(username), stamp, stamp, str(username), stamp,
        )
        return
    await pool.execute(
        "INSERT INTO lastfm_users (user_id, username, session_key, linked_at, checked_at) "
        "VALUES ($1, $2, $3, $4, $5) "
        "ON CONFLICT (user_id) DO UPDATE SET username = $6, session_key = $7, "
        "checked_at = $8",
        int(user_id), str(username), str(session_key), stamp, stamp,
        str(username), str(session_key), stamp,
    )


async def remove_account(pool, user_id: int) -> None:
    """Forget a member's link. Index rows are left alone on purpose: they are
    other members' ranking data too, and a relink should not rewrite a server."""
    await pool.execute("DELETE FROM lastfm_users WHERE user_id = $1", int(user_id))


async def touch_account(pool, user_id: int, checked_at: float | None = None) -> None:
    """Record that the linked handle was seen to exist on Last.fm."""
    await pool.execute(
        "UPDATE lastfm_users SET checked_at = $1 WHERE user_id = $2",
        float(checked_at if checked_at is not None else now()),
        int(user_id),
    )


# ── Guild artist index ─────────────────────────────────────────────────────

async def user_index(pool, guild_id: int, user_id: int) -> dict[str, int]:
    """This member's indexed playcounts in one guild, keyed by artist key."""
    rows = await pool.fetch(
        "SELECT artist_key, playcount FROM lastfm_artist_index "
        "WHERE guild_id = $1 AND user_id = $2 LIMIT $3",
        int(guild_id), int(user_id), 2000,
    )
    return {str(row["artist_key"]): int(row["playcount"] or 0) for row in rows or []}


async def index_artists(
    pool,
    guild_id: int | None,
    user_id: int,
    entries: Iterable[tuple[str, int]],
    *,
    limit: int = INDEX_BATCH,
    merge: bool = True,
) -> int:
    """Upsert one member's artist playcounts into the guild's index.

    Entries are ``(artist name, playcount)``. Returns how many rows were
    written. A DM has no guild to index into, so the write is skipped.

    With ``merge`` (the default) a stored count is only ever raised: an
    overview fetched for "Last 7 days" carries a period count, and writing it
    over the member's all-time row would quietly shrink their crowns. The
    compare-and-skip also means a repeat visit writes nothing at all.
    """
    if guild_id is None:
        return 0
    candidates = [
        (str(name).strip(), int(playcount or 0))
        for name, playcount in list(entries)[:limit]
        if str(name or "").strip()
    ]
    existing = await user_index(pool, guild_id, user_id) if merge else {}
    stamp = now()
    written = 0
    for name, playcount in candidates:
        key = artist_key(name)
        if not key:
            continue
        if merge and existing.get(key, -1) >= playcount:
            continue
        await pool.execute(
            "INSERT INTO lastfm_artist_index "
            "(guild_id, user_id, artist_key, artist_name, playcount, updated_at) "
            "VALUES ($1, $2, $3, $4, $5, $6) "
            "ON CONFLICT (guild_id, user_id, artist_key) "
            "DO UPDATE SET artist_name = $7, playcount = $8, updated_at = $9",
            int(guild_id), int(user_id), key, name, playcount, stamp,
            name, playcount, stamp,
        )
        written += 1
    return written


async def artist_listeners(pool, guild_id: int, name: str, *, limit: int = 10) -> list[dict]:
    """The guild's ranked listeners of one artist, strongest first."""
    rows = await pool.fetch(
        "SELECT user_id, artist_name, playcount, updated_at FROM lastfm_artist_index "
        "WHERE guild_id = $1 AND artist_key = $2 "
        "ORDER BY playcount DESC LIMIT $3",
        int(guild_id), artist_key(name), int(limit),
    )
    return [dict(row) for row in rows or []]


async def user_artist_row(pool, guild_id: int, user_id: int, name: str) -> dict | None:
    """This member's indexed playcount for one artist, if the index has it."""
    row = await pool.fetchrow(
        "SELECT playcount, updated_at FROM lastfm_artist_index "
        "WHERE guild_id = $1 AND user_id = $2 AND artist_key = $3",
        int(guild_id), int(user_id), artist_key(name),
    )
    return dict(row) if row else None


async def guild_index(pool, guild_id: int, *, limit: int = 4000) -> list[dict]:
    """Every indexed row for a guild, capped so one huge server cannot stall a card."""
    rows = await pool.fetch(
        "SELECT user_id, artist_key, artist_name, playcount, updated_at "
        "FROM lastfm_artist_index WHERE guild_id = $1 LIMIT $2",
        int(guild_id), int(limit),
    )
    return [dict(row) for row in rows or []]


async def indexed_user_ids(pool, guild_id: int) -> set[int]:
    """Members with at least one indexed row in this guild."""
    rows = await pool.fetch(
        "SELECT user_id FROM lastfm_artist_index WHERE guild_id = $1 LIMIT $2",
        int(guild_id), 4000,
    )
    return {int(row["user_id"]) for row in rows or []}


def crowns(rows: Sequence[dict], *, min_plays: int = 1) -> dict[int, list[dict]]:
    """Group guild index rows into crowns: who has the most plays of each artist.

    A crown needs at least two listeners to mean anything — a single listener
    is just a member who scrobbled something, and a server where everybody
    holds every crown is not a leaderboard. Ties go to the earliest indexed
    row so the answer is stable between commands.
    """
    by_artist: dict[str, list[dict]] = {}
    for row in rows:
        key = str(row.get("artist_key") or "")
        if key:
            by_artist.setdefault(key, []).append(row)

    held: dict[int, list[dict]] = {}
    for key, group in by_artist.items():
        if len(group) < 2:
            continue
        group = sorted(group, key=lambda row: (-int(row.get("playcount") or 0), int(row.get("user_id") or 0)))
        top, runner_up = group[0], group[1]
        plays = int(top.get("playcount") or 0)
        if plays < min_plays:
            continue
        holder = int(top.get("user_id") or 0)
        held.setdefault(holder, []).append({
            "artist": top.get("artist_name") or key,
            "plays": plays,
            "runner_up": int(runner_up.get("playcount") or 0),
            "runner_up_id": int(runner_up.get("user_id") or 0),
            "lead": plays - int(runner_up.get("playcount") or 0),
        })
    for crown_list in held.values():
        crown_list.sort(key=lambda crown: (-crown["plays"], crown["artist"].casefold()))
    return held

