"""
Startup — database initialisation.
Handles connection, table creation, and legacy migrations.
"""

import os
import sqlite3 as _sqlite3

import database
from utils import logging


DATABASE_PATH = "data/database.db"


async def _create_tables(bot):
    if not bot.cxn:
        return

    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS voicemaster_settings (
            guild_id          INTEGER PRIMARY KEY,
            join_channel_id   INTEGER,
            category_id       INTEGER,
            default_name      TEXT DEFAULT '{user}''s Channel',
            default_limit     INTEGER DEFAULT 0,
            default_bitrate   INTEGER DEFAULT 64000,
            default_region    TEXT,
            interface_enabled INTEGER DEFAULT 1,
            auto_role         INTEGER,
            join_role         INTEGER
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS voicemaster_channels (
            channel_id  INTEGER PRIMARY KEY,
            owner_id    INTEGER NOT NULL,
            guild_id    INTEGER NOT NULL,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS follows (
            guild_id     INTEGER,
            platform     TEXT,
            username     TEXT,
            channel_id   INTEGER,
            template     TEXT,
            last_post_id TEXT,
            PRIMARY KEY  (guild_id, platform, username)
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS youtube (
            channel_id TEXT PRIMARY KEY,
            last_video TEXT
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS youtube_history (
            channel_id TEXT,
            video_id   TEXT,
            PRIMARY KEY (channel_id, video_id)
        )
    """)

    await bot.cxn.execute("""
        INSERT OR IGNORE INTO youtube_history (channel_id, video_id)
        SELECT channel_id, last_video FROM youtube WHERE last_video IS NOT NULL
    """)

    try:
        cols = await bot.cxn.fetch("PRAGMA table_info(levels)")
        col_names = {row["name"] for row in cols}
        if cols and "guild_id" not in col_names:
            await bot.cxn.execute("ALTER TABLE levels RENAME TO levels_old")
            await bot.cxn.execute("""
                CREATE TABLE levels (
                    guild_id INTEGER,
                    user_id  INTEGER,
                    xp       INTEGER DEFAULT 0,
                    level    INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            await bot.cxn.execute("DROP TABLE levels_old")
        else:
            await bot.cxn.execute("""
                CREATE TABLE IF NOT EXISTS levels (
                    guild_id INTEGER,
                    user_id  INTEGER,
                    xp       INTEGER DEFAULT 0,
                    level    INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
    except Exception as e:
        logging.warning("DB", f"levels table migration warning: {e}")

    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS level_config (
            guild_id         INTEGER PRIMARY KEY,
            xp_enabled       INTEGER DEFAULT 1,
            xp_multiplier    REAL    DEFAULT 1.0,
            xp_cooldown      INTEGER DEFAULT 0,
            level_up_channel INTEGER,
            level_up_message TEXT,
            level_roles      TEXT
        )
    """)

    old_follows = "data/follows.db"
    if os.path.exists(old_follows):
        try:
            old_conn = _sqlite3.connect(old_follows)
            rows = old_conn.execute("SELECT * FROM follows").fetchall()
            for row in rows:
                await bot.cxn.execute(
                    "INSERT OR IGNORE INTO follows "
                    "(guild_id, platform, username, channel_id, template, last_post_id) "
                    "VALUES ($1, $2, $3, $4, $5, $6)",
                    row[0], row[1], row[2], row[3], row[4], row[5]
                )
            old_conn.close()
            os.rename(old_follows, old_follows + ".migrated")
            logging.success("DB", "Migrated follows.db → database.db")
        except Exception as e:
            logging.warning("DB", f"Could not migrate follows.db: {e}")

    logging.success("DB", "Database tables verified")


async def init_database(bot):
    logging.info("DB", f"Opening database: {DATABASE_PATH}")
    try:
        bot.cxn = await database.create_pool(DATABASE_PATH)
        logging.success("DB", "Database connection established")
        await _create_tables(bot)
    except Exception as e:
        logging.error("DB", f"Failed to open database: {e}")
