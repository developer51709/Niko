"""Short-lived caches that keep the live economy leaderboard cheap to poll.

The public leaderboard refreshes itself while it is open, which means the same
twenty rows are requested every few seconds. Two parts of that response are
expensive to rebuild each time and change slowly:

* Discord identities (username, display name, avatar) for the visible rows.
* The signed-in viewer's own guild list, used to decide whether a private
  profile shares a server with them.

Both are cached here for a few seconds, so a poll costs two small database
queries and no Discord API traffic. Standings themselves are never cached --
net worth is read from the database on every request, so the board stays live.

Privacy stays intact: the per-profile ``leaderboard_private`` flag is always
read fresh, and a viewer who stops sharing a guild loses that visibility within
:data:`GUILD_TTL` seconds. Row keys are salted hashes of the user id, stable for
the lifetime of the process but not reversible or comparable across restarts, so
the browser can animate a row that moves without the API revealing who a private
profile is.
"""

import hashlib
import secrets
import threading
import time

IDENTITY_TTL = 60.0
GUILD_TTL = 30.0
_MAX_ENTRIES = 4096

_lock = threading.Lock()
_salt = secrets.token_hex(16)
_identities: dict[str, tuple[float, dict]] = {}
_viewer_guilds: dict[str, tuple[float, frozenset[str]]] = {}


def _prune(store: dict, now: float, ttl: float) -> None:
    """Drop expired entries, then enforce the size cap for long-lived processes."""
    expired = [key for key, (stored_at, _value) in store.items() if now - stored_at > ttl]
    for key in expired:
        store.pop(key, None)
    if len(store) > _MAX_ENTRIES:
        for key in sorted(store, key=lambda item: store[item][0])[: len(store) - _MAX_ENTRIES]:
            store.pop(key, None)


def profile_key(user_id: str) -> str:
    """Return a stable, opaque row key for ``user_id``.

    The browser needs the same key on every poll to animate a row that moves
    rank. A salted digest gives it that without exposing -- or even linking --
    the underlying Discord id.
    """
    return hashlib.sha256(f"{_salt}:{user_id}".encode("utf-8")).hexdigest()[:16]


def cached_identities(user_ids: set[str]) -> dict[str, dict]:
    """Return the identities already cached for ``user_ids``."""
    now = time.monotonic()
    found = {}
    with _lock:
        _prune(_identities, now, IDENTITY_TTL)
        for user_id in user_ids:
            entry = _identities.get(user_id)
            if entry is not None:
                found[user_id] = dict(entry[1])
    return found


def store_identities(identities: dict[str, dict]) -> None:
    """Remember freshly resolved identities for :data:`IDENTITY_TTL` seconds."""
    if not identities:
        return
    now = time.monotonic()
    with _lock:
        for user_id, identity in identities.items():
            _identities[user_id] = (now, dict(identity))
        _prune(_identities, now, IDENTITY_TTL)


def cached_viewer_guilds(viewer_id: str) -> set[str] | None:
    """Return the cached guild ids for a viewer, or ``None`` when unknown."""
    now = time.monotonic()
    with _lock:
        _prune(_viewer_guilds, now, GUILD_TTL)
        entry = _viewer_guilds.get(viewer_id)
        return set(entry[1]) if entry is not None else None


def store_viewer_guilds(viewer_id: str, guild_ids: set[str]) -> None:
    """Remember a viewer's guild ids for :data:`GUILD_TTL` seconds."""
    now = time.monotonic()
    with _lock:
        _viewer_guilds[viewer_id] = (now, frozenset(guild_ids))
        _prune(_viewer_guilds, now, GUILD_TTL)


def reset() -> None:
    """Clear every cache — used by tests so poll assertions are deterministic."""
    with _lock:
        _identities.clear()
        _viewer_guilds.clear()
