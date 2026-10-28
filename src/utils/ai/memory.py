"""Per-guild, per-user AI memory stored in the bot's shared database.

This replaced a process-wide ``memory.json`` keyed only by user id. That file
mixed every server and DM together (so one server could see a conversation held
in another), appended forever while only the last few hundred characters were
ever read, and was rewritten twice per reply. It also held the favorability
score, which has been removed entirely.
"""

from __future__ import annotations

import json
from typing import NamedTuple, Optional

#: Long-term notes kept per (guild, user). Older lines are dropped at a line
#: boundary so a stored note never starts mid-sentence.
MAX_MEMORY_CHARS = 600
#: Conversation turns kept per (guild, user).
MAX_HISTORY_TURNS = 10
#: Characters kept from a single turn.
MAX_TURN_CHARS = 500

_TABLE = "ai_memory"
_table_pool = None


class MemoryContext(NamedTuple):
    """What the prompt needs: long-term notes plus the recent turns."""

    memory: str
    history: str


_EMPTY = MemoryContext("", "")


def _pool():
    import database as database_module

    return getattr(database_module, "_shared_pool", None)


async def _ensure_table(pool) -> None:
    global _table_pool
    if _table_pool is pool:
        return
    await pool.execute(
        "CREATE TABLE IF NOT EXISTS ai_memory ("
        " guild_id INTEGER NOT NULL,"
        " user_id INTEGER NOT NULL,"
        " memory TEXT NOT NULL DEFAULT '',"
        " history TEXT NOT NULL DEFAULT '[]',"
        " updated_at TEXT NOT NULL DEFAULT (datetime('now')),"
        " PRIMARY KEY (guild_id, user_id)"
        ")"
    )
    _table_pool = pool


async def _read(guild_id: int, user_id: int):
    pool = _pool()
    if pool is None:
        return None
    await _ensure_table(pool)
    return await pool.fetchrow(
        "SELECT memory, history FROM ai_memory WHERE guild_id = $1 AND user_id = $2",
        int(guild_id),
        int(user_id),
    )


def _decode_history(raw) -> list[dict]:
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (TypeError, ValueError):
            return []
    if not isinstance(raw, list):
        return []
    return [turn for turn in raw if isinstance(turn, dict) and turn.get("content")]


def _format_history(turns: list[dict], limit: int) -> str:
    return "\n".join(
        f"{turn.get('role') or 'User'}: {turn.get('content', '')}"
        for turn in turns[-limit:]
    )


async def get_context(guild_id: int, user_id: int, *, limit: int = 3) -> MemoryContext:
    """Long-term notes and the last ``limit`` turns for this guild and user."""
    try:
        row = await _read(guild_id, user_id)
    except Exception:  # noqa: BLE001 - memory is optional context, never fatal
        return _EMPTY
    if row is None:
        return _EMPTY
    memory = row["memory"] or ""
    history = _format_history(_decode_history(row["history"]), limit)
    return MemoryContext(memory if isinstance(memory, str) else "", history)


def _trim_memory(memory: str) -> str:
    """Keep the newest complete lines that fit inside the cap."""
    memory = (memory or "").strip()
    if len(memory) <= MAX_MEMORY_CHARS:
        return memory
    tail = memory[-MAX_MEMORY_CHARS:]
    newline = tail.find("\n")
    if newline != -1:
        tail = tail[newline + 1:]
    return tail.strip()


def build_turn(
    memory: str,
    turns: list[dict],
    user_message: str,
    assistant_message: str,
    *,
    user_label: str,
    assistant_label: str,
) -> tuple[str, list[dict]]:
    """Pure update step, split out so it can be tested without a database."""
    user_message = str(user_message or "").strip()[:MAX_TURN_CHARS]
    assistant_message = str(assistant_message or "").strip()[:MAX_TURN_CHARS]

    lines = [line for line in (memory or "").splitlines() if line.strip()]
    if user_message:
        lines.append(f"{user_label}: {user_message}")
    if assistant_message:
        lines.append(f"{assistant_label}: {assistant_message}")
    new_memory = _trim_memory("\n".join(lines))

    history = list(turns)
    if user_message:
        history.append({"role": user_label, "content": user_message})
    if assistant_message:
        history.append({"role": assistant_label, "content": assistant_message})
    return new_memory, history[-MAX_HISTORY_TURNS:]


async def record_turn(
    guild_id: int,
    user_id: int,
    user_message: str,
    assistant_message: str,
    *,
    user_label: str,
    assistant_label: str,
) -> None:
    """Store one exchange, in a single write."""
    pool = _pool()
    if pool is None:
        return
    try:
        await _ensure_table(pool)
        row = await _read(guild_id, user_id)
        memory = row["memory"] if row is not None and isinstance(row["memory"], str) else ""
        turns = _decode_history(row["history"]) if row is not None else []
        memory, turns = build_turn(
            memory,
            turns,
            user_message,
            assistant_message,
            user_label=user_label,
            assistant_label=assistant_label,
        )
        await pool.execute(
            "INSERT OR REPLACE INTO ai_memory (guild_id, user_id, memory, history)"
            " VALUES ($1, $2, $3, $4)",
            int(guild_id),
            int(user_id),
            memory,
            json.dumps(turns),
        )
    except Exception:  # noqa: BLE001 - a failed memory write must not lose the reply
        return


async def has_memory(guild_id: int, user_id: int) -> bool:
    try:
        row = await _read(guild_id, user_id)
    except Exception:  # noqa: BLE001
        return False
    if row is None:
        return False
    return bool((row["memory"] or "").strip() or _decode_history(row["history"]))


async def get_memory_text(guild_id: int, user_id: int) -> str:
    try:
        row = await _read(guild_id, user_id)
    except Exception:  # noqa: BLE001
        return ""
    if row is None or not isinstance(row["memory"], str):
        return ""
    return row["memory"]


async def clear_user(guild_id: int, user_id: int) -> None:
    """Erase this user's memory and history with Niko in this server."""
    pool = _pool()
    if pool is None:
        return
    await _ensure_table(pool)
    await pool.execute(
        "DELETE FROM ai_memory WHERE guild_id = $1 AND user_id = $2",
        int(guild_id),
        int(user_id),
    )


async def clear_user_everywhere(user_id: int) -> None:
    """Erase a user's AI memory in every server (data-removal requests)."""
    pool = _pool()
    if pool is None:
        return
    await _ensure_table(pool)
    await pool.execute("DELETE FROM ai_memory WHERE user_id = $1", int(user_id))


async def clear_guild(guild_id: int) -> None:
    """Erase all AI memory for a server."""
    pool = _pool()
    if pool is None:
        return
    await _ensure_table(pool)
    await pool.execute("DELETE FROM ai_memory WHERE guild_id = $1", int(guild_id))
