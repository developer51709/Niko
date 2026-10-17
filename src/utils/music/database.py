"""
Music System — dedicated database.

The music feature deliberately does NOT use the bot's main database. It owns
a separate pool so heavy music features (liked songs, and future playlists)
never add load to the primary database:

  • SQLite   → data/music.db (separate file from data/database.db)
  • MongoDB  → same cluster as the main database, but a SEPARATE database
               within it (default: ``discord_bot_music`` — derived from
               MONGODB_DATABASE + "_music")

Every call site speaks the same pool API as the main database, so the
SQL ↔ MongoDB translation layer is reused as-is.
"""

import os

import aiosqlite

from database import MongoPool, SQLitePool
from utils import logging

MUSIC_DB_PATH = "data/music.db"

_TABLE_SQL = [
    """CREATE TABLE IF NOT EXISTS music_liked_songs (
        user_id    INTEGER NOT NULL,
        track_key  TEXT    NOT NULL,
        title      TEXT    NOT NULL,
        author     TEXT    DEFAULT '',
        uri        TEXT    DEFAULT '',
        artwork    TEXT    DEFAULT '',
        length_ms  INTEGER DEFAULT 0,
        source     TEXT    DEFAULT '',
        added_at   TEXT    NOT NULL DEFAULT (datetime('now')),
        PRIMARY KEY (user_id, track_key)
    )""",
    """CREATE TABLE IF NOT EXISTS music_playlists (
        user_id    INTEGER NOT NULL,
        name       TEXT    NOT NULL,
        created_at TEXT    NOT NULL DEFAULT (datetime('now')),
        PRIMARY KEY (user_id, name)
    )""",
    """CREATE TABLE IF NOT EXISTS music_playlist_tracks (
        user_id    INTEGER NOT NULL,
        name       TEXT    NOT NULL,
        track_key  TEXT    NOT NULL,
        position   INTEGER DEFAULT 0,
        title      TEXT    DEFAULT '',
        author     TEXT    DEFAULT '',
        uri        TEXT    DEFAULT '',
        artwork    TEXT    DEFAULT '',
        length_ms  INTEGER DEFAULT 0,
        source     TEXT    DEFAULT '',
        added_at   TEXT    NOT NULL DEFAULT (datetime('now')),
        PRIMARY KEY (user_id, name, track_key)
    )""",
]


def _track_key(track) -> str:
    """Stable identity for a wavelink track (URI preferred over video id)."""
    return (getattr(track, "uri", None) or getattr(track, "id", None) or
            f"{getattr(track, 'author', '')} - {getattr(track, 'title', '')}").strip() or "unknown"


class MusicDatabase:
    """Singleton wrapper around the music pool."""

    _instance: "MusicDatabase | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.pool = None
        return cls._instance

    # ────────────────────────────────────────────── setup ──
    @property
    def is_ready(self) -> bool:
        return self.pool is not None

    async def init(self, bot=None) -> None:
        """Create the music pool (called from startup, after the main DB)."""
        if self.pool is not None:
            return

        main = getattr(bot, "cxn", None) if bot is not None else None
        if main is not None and main.db_type == "mongodb":
            # Same cluster, separate database within it — reuses the main
            # pool's motor client so we don't open a second connection pool.
            try:
                client   = main.client
                base     = os.getenv("MONGODB_DATABASE", "discord_bot")
                self.pool = MongoPool(client, f"{base}_music")
            except Exception as e:
                logging.warning("MusicDB", f"Mongo music database failed ({e}); using SQLite.")
                self.pool = None

        if self.pool is None:
            conn = await aiosqlite.connect(MUSIC_DB_PATH)
            await conn.execute("PRAGMA journal_mode=WAL")
            await conn.execute("PRAGMA foreign_keys=ON")
            self.pool = SQLitePool(conn)

        for sql in _TABLE_SQL:
            await self.pool.execute(sql)

        logging.success(
            "MusicDB",
            f"Music database ready ({self.pool.db_type}, {len(_TABLE_SQL)} tables).",
        )

    async def ensure(self, bot=None) -> bool:
        """Lazy init for commands that run before/without the startup hook."""
        if self.pool is None:
            await self.init(bot)
        return self.pool is not None

    # ────────────────────────────────────────────── liked songs ──
    async def add_liked(self, user_id: int, track) -> bool:
        """Like a track. Returns True if it was newly added (False if it was
        already liked)."""
        if not await self.ensure():
            return False
        before = await self.is_liked(user_id, _track_key(track))
        await self.pool.execute(
            "INSERT OR IGNORE INTO music_liked_songs "
            "(user_id, track_key, title, author, uri, artwork, length_ms, source) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
            user_id,
            _track_key(track),
            getattr(track, "title", "") or "Unknown",
            getattr(track, "author", "") or "",
            getattr(track, "uri", "") or "",
            getattr(track, "artwork", "") or "",
            int(getattr(track, "length", 0) or 0),
            getattr(track, "source", "") or "",
        )
        return not before

    async def remove_liked(self, user_id: int, track) -> bool:
        """Unlike a track (accepts a track object or a track_key string)."""
        if not await self.ensure():
            return False
        key = track if isinstance(track, str) else _track_key(track)
        await self.pool.execute(
            "DELETE FROM music_liked_songs WHERE user_id = $1 AND track_key = $2",
            user_id,
            key,
        )
        return True

    async def is_liked(self, user_id: int, track) -> bool:
        if not await self.ensure():
            return False
        key = track if isinstance(track, str) else _track_key(track)
        row = await self.pool.fetchrow(
            "SELECT track_key FROM music_liked_songs "
            "WHERE user_id = $1 AND track_key = $2",
            user_id,
            key,
        )
        return row is not None

    async def toggle_liked(self, user_id: int, track) -> bool:
        """Toggle like state; returns True if the track is now liked."""
        if await self.is_liked(user_id, track):
            await self.remove_liked(user_id, track)
            return False
        await self.add_liked(user_id, track)
        return True

    async def get_liked(self, user_id: int, limit: int = 10, offset: int = 0) -> list:
        if not await self.ensure():
            return []
        return await self.pool.fetch(
            "SELECT user_id, track_key, title, author, uri, artwork, length_ms, source "
            "FROM music_liked_songs WHERE user_id = $1 "
            f"ORDER BY added_at DESC LIMIT {int(limit)} OFFSET {int(offset)}",
            user_id,
        )

    async def count_liked(self, user_id: int) -> int:
        if not await self.ensure():
            return 0
        return await self.pool.fetchval(
            "SELECT COUNT(*) FROM music_liked_songs WHERE user_id = $1",
            user_id,
        ) or 0

    async def clear_liked(self, user_id: int) -> int:
        if not await self.ensure():
            return 0
        count = await self.count_liked(user_id)
        await self.pool.execute(
            "DELETE FROM music_liked_songs WHERE user_id = $1",
            user_id,
        )
        return count

    # ────────────────────────────────────────────── playlists (room for future features) ──
    async def create_playlist(self, user_id: int, name: str) -> bool:
        if not await self.ensure():
            return False
        await self.pool.execute(
            "INSERT OR IGNORE INTO music_playlists (user_id, name) VALUES ($1, $2)",
            user_id,
            name,
        )
        return True

    async def delete_playlist(self, user_id: int, name: str) -> None:
        if not await self.ensure():
            return
        await self.pool.execute(
            "DELETE FROM music_playlists WHERE user_id = $1 AND name = $2",
            user_id,
            name,
        )
        await self.pool.execute(
            "DELETE FROM music_playlist_tracks WHERE user_id = $1 AND name = $2",
            user_id,
            name,
        )

    async def get_playlists(self, user_id: int) -> list:
        if not await self.ensure():
            return []
        return await self.pool.fetch(
            "SELECT user_id, name, created_at FROM music_playlists "
            "WHERE user_id = $1 ORDER BY created_at DESC",
            user_id,
        )

    async def add_playlist_track(self, user_id: int, name: str, track) -> bool:
        if not await self.ensure():
            return False
        position = 0
        row = await self.pool.fetchval(
            "SELECT COUNT(*) FROM music_playlist_tracks "
            "WHERE user_id = $1 AND name = $2",
            user_id,
            name,
        )
        position = int(row or 0)
        await self.pool.execute(
            "INSERT OR IGNORE INTO music_playlist_tracks "
            "(user_id, name, track_key, position, title, author, uri, artwork, length_ms, source) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
            user_id,
            name,
            _track_key(track),
            position,
            getattr(track, "title", "") or "Unknown",
            getattr(track, "author", "") or "",
            getattr(track, "uri", "") or "",
            getattr(track, "artwork", "") or "",
            int(getattr(track, "length", 0) or 0),
            getattr(track, "source", "") or "",
        )
        return True

    async def remove_playlist_track(self, user_id: int, name: str, track) -> None:
        if not await self.ensure():
            return
        key = track if isinstance(track, str) else _track_key(track)
        await self.pool.execute(
            "DELETE FROM music_playlist_tracks "
            "WHERE user_id = $1 AND name = $2 AND track_key = $3",
            user_id,
            name,
            key,
        )

    async def get_playlist_tracks(self, user_id: int, name: str) -> list:
        if not await self.ensure():
            return []
        return await self.pool.fetch(
            "SELECT user_id, name, track_key, title, author, uri, artwork, length_ms, source "
            "FROM music_playlist_tracks WHERE user_id = $1 AND name = $2 "
            "ORDER BY position ASC",
            user_id,
            name,
        )