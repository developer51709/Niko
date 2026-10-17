import json
import os
import sqlite3
from typing import Optional, Union
from utils import logging

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AI_DATABASE_FILE = os.path.join(PROJECT_ROOT, "data", "database.db")
AI_CONFIG_FILE = os.path.join(PROJECT_ROOT, "data", "ai_config.json")

DEFAULT_CONFIG = {
    "personality": "cafe",
    "enabled": "True",
    "ai_name": "Niko",
    "ai_actions_experiment": "False",
    "better_context_experiment": "False",
    "multimodal_experiment": "False",
}
_BOOLEAN_FIELDS = {"enabled", "ai_actions_experiment", "better_context_experiment", "multimodal_experiment"}


def _connect():
    os.makedirs(os.path.dirname(AI_DATABASE_FILE), exist_ok=True)
    return sqlite3.connect(AI_DATABASE_FILE, timeout=5)


def _ensure_table(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS ai_config (
        guild_id INTEGER PRIMARY KEY,
        personality TEXT NOT NULL DEFAULT 'cafe',
        enabled INTEGER NOT NULL DEFAULT 1,
        ai_name TEXT NOT NULL DEFAULT 'Niko',
        ai_actions_experiment INTEGER NOT NULL DEFAULT 0,
        better_context_experiment INTEGER NOT NULL DEFAULT 0,
        multimodal_experiment INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    )""")
    for name, definition in (
        ("ai_name", "TEXT NOT NULL DEFAULT 'Niko'"),
        ("ai_actions_experiment", "INTEGER NOT NULL DEFAULT 0"),
        ("better_context_experiment", "INTEGER NOT NULL DEFAULT 0"),
        ("multimodal_experiment", "INTEGER NOT NULL DEFAULT 0"),
    ):
        try:
            conn.execute(f"ALTER TABLE ai_config ADD COLUMN {name} {definition}")
        except sqlite3.OperationalError:
            pass


def _as_bool(value) -> int:
    return int(value is True or str(value).lower() in {"true", "1", "yes", "on"})


def _migrate_legacy(conn):
    if not os.path.exists(AI_CONFIG_FILE):
        return
    try:
        with open(AI_CONFIG_FILE, encoding="utf-8") as file:
            legacy = json.load(file)
        if isinstance(legacy, dict):
            for guild_id, raw in legacy.items():
                if not str(guild_id).isdigit() or not isinstance(raw, dict):
                    continue
                values = {**DEFAULT_CONFIG, **raw}
                conn.execute("""INSERT OR IGNORE INTO ai_config
                    (guild_id, personality, enabled, ai_name, ai_actions_experiment,
                     better_context_experiment, multimodal_experiment)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""", (
                    int(guild_id),
                    values["personality"] if values["personality"] in {"cafe", "normal"} else "cafe",
                    _as_bool(values["enabled"]),
                    str(values["ai_name"] or "Niko").strip()[:32] or "Niko",
                    _as_bool(values["ai_actions_experiment"]),
                    _as_bool(values["better_context_experiment"]),
                    _as_bool(values["multimodal_experiment"]),
                ))
        os.replace(AI_CONFIG_FILE, AI_CONFIG_FILE + ".migrated")
    except Exception as error:
        logging.warning("ai_config", f"Legacy AI config migration failed: {error}")


def _row_to_config(row):
    return {
        "personality": row[1],
        "enabled": "True" if row[2] else "False",
        "ai_name": row[3] or "Niko",
        "ai_actions_experiment": "True" if row[4] else "False",
        "better_context_experiment": "True" if row[5] else "False",
        "multimodal_experiment": "True" if row[6] else "False",
    }


def get_ai_config(guild_id: int, key: Optional[str] = None) -> Union[dict, str, None]:
    conn = None
    try:
        conn = _connect()
        _ensure_table(conn)
        _migrate_legacy(conn)
        conn.execute("INSERT OR IGNORE INTO ai_config (guild_id) VALUES (?)", (int(guild_id),))
        conn.commit()
        row = conn.execute("""SELECT guild_id, personality, enabled, ai_name,
            ai_actions_experiment, better_context_experiment, multimodal_experiment
            FROM ai_config WHERE guild_id = ?""", (int(guild_id),)).fetchone()
        config = _row_to_config(row)
        return config if key is None else config.get(key)
    except Exception as error:
        logging.error("ai_config", f"Failed to read AI config: {error}")
        return DEFAULT_CONFIG.copy() if key is None else DEFAULT_CONFIG.get(key)
    finally:
        if conn is not None:
            conn.close()


def get_personality(ctx):
    return (get_ai_config(ctx.guild.id, "personality") if ctx and ctx.guild else None) or "normal"


def set_ai_config(guild_id: int, key: str, value: Union[str, bool, int, dict]) -> None:
    if key not in DEFAULT_CONFIG:
        raise ValueError(f"Unsupported AI config key: {key}")
    conn = None
    try:
        conn = _connect()
        _ensure_table(conn)
        _migrate_legacy(conn)
        conn.execute("INSERT OR IGNORE INTO ai_config (guild_id) VALUES (?)", (int(guild_id),))
        if key in _BOOLEAN_FIELDS:
            value = _as_bool(value)
        elif key == "personality":
            if value not in {"cafe", "normal"}:
                return
        elif key == "ai_name":
            value = str(value).strip()[:32] or "Niko"
        conn.execute(f"UPDATE ai_config SET {key} = ?, updated_at = datetime('now') WHERE guild_id = ?", (value, int(guild_id)))
        conn.commit()
    except Exception as error:
        logging.error("ai_config", f"Failed to save AI config: {error}")
        raise
    finally:
        if conn is not None:
            conn.close()
