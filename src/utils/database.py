import sqlite3
from typing import Optional, List, Tuple

DB_PATH = "follows.db"


# -----------------------------------
#  DATABASE INITIALIZATION
# -----------------------------------

def init_db():
    """Initialize the database and create tables if missing."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS follows (
                guild_id INTEGER,
                platform TEXT,
                username TEXT,
                channel_id INTEGER,
                template TEXT,
                last_post_id TEXT,
                PRIMARY KEY (guild_id, platform, username)
            )
        """)
        conn.commit()


# -----------------------------------
#  FOLLOW MANAGEMENT
# -----------------------------------

def add_follow(
    guild_id: int,
    platform: str,
    username: str,
    channel_id: int,
    template: str
):
    """Add or update a follow entry."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO follows
            (guild_id, platform, username, channel_id, template, last_post_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (guild_id, platform, username, channel_id, template, None))
        conn.commit()


def remove_follow(guild_id: int, platform: str, username: str):
    """Remove a follow entry."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            DELETE FROM follows
            WHERE guild_id = ? AND platform = ? AND username = ?
        """, (guild_id, platform, username))
        conn.commit()


# -----------------------------------
#  RETRIEVAL
# -----------------------------------

def get_all_follows() -> List[Tuple]:
    """Return all follow entries."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM follows")
        return c.fetchall()


def get_follows_for_guild(guild_id: int) -> List[Tuple]:
    """Return all follows for a specific guild."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM follows WHERE guild_id = ?", (guild_id,))
        return c.fetchall()


# -----------------------------------
#  UPDATE LAST POST
# -----------------------------------

def update_last_post(
    guild_id: int,
    platform: str,
    username: str,
    post_id: str
):
    """Update the last seen post ID for a follow entry."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE follows
            SET last_post_id = ?
            WHERE guild_id = ? AND platform = ? AND username = ?
        """, (post_id, guild_id, platform, username))
        conn.commit()