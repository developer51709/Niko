"""Persistence for echoed messages and their staff reports.

Echo messages are ordinary channel messages, so their content and author are
not available from Discord once the message is deleted. A row is written when
the command sends the message; the info button and the staff report both read
that row instead of trusting values supplied by a click.

Reports and warnings are intentionally separate tables. A report can be marked
invalid without creating a warning, and a valid report creates exactly one
warning (enforced by the unique report id on ``echo_warnings``).
"""

from __future__ import annotations

import time
import uuid
from typing import Any


def _row(row) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


async def record_echo_message(
    pool,
    *,
    echo_id: str,
    message_id: int,
    guild_id: int,
    channel_id: int,
    author_id: int,
    content: str,
    truncated: bool,
) -> dict[str, Any]:
    """Store the message details needed by the info and report views."""
    created_at = time.time()
    await pool.execute(
        "INSERT INTO echo_messages "
        "(echo_id, message_id, guild_id, channel_id, author_id, content, truncated, created_at) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
        str(echo_id), int(message_id), int(guild_id), int(channel_id),
        int(author_id), str(content), 1 if truncated else 0, created_at,
    )
    return {
        "echo_id": str(echo_id),
        "message_id": int(message_id),
        "guild_id": int(guild_id),
        "channel_id": int(channel_id),
        "author_id": int(author_id),
        "content": str(content),
        "truncated": bool(truncated),
        "created_at": created_at,
        "removed_at": None,
    }


async def get_echo_message(pool, echo_id: str) -> dict[str, Any] | None:
    row = await pool.fetchrow(
        "SELECT echo_id, message_id, guild_id, channel_id, author_id, content, "
        "truncated, created_at, removed_at FROM echo_messages WHERE echo_id = $1",
        str(echo_id),
    )
    return _row(row)


async def mark_echo_removed(pool, echo_id: str) -> None:
    await pool.execute(
        "UPDATE echo_messages SET removed_at = $1 WHERE echo_id = $2",
        time.time(), str(echo_id),
    )


async def report_count(pool, echo_id: str) -> int:
    value = await pool.fetchval(
        "SELECT COUNT(*) FROM echo_reports WHERE echo_id = $1",
        str(echo_id),
    )
    return int(value or 0)


async def create_echo_report(
    pool,
    *,
    echo_id: str,
    reporter_id: int,
    reason: str = "",
) -> tuple[dict[str, Any], bool]:
    """Create a pending report, or return the reporter's existing pending one."""
    existing = await pool.fetchrow(
        "SELECT report_id, echo_id, reporter_id, reason, status, created_at, "
        "reviewed_by, reviewed_at FROM echo_reports "
        "WHERE echo_id = $1 AND reporter_id = $2 AND status = 'pending'",
        str(echo_id), int(reporter_id),
    )
    if existing is not None:
        return dict(existing), False

    report_id = uuid.uuid4().hex
    created_at = time.time()
    await pool.execute(
        "INSERT INTO echo_reports "
        "(report_id, echo_id, reporter_id, reason, status, created_at) "
        "VALUES ($1, $2, $3, $4, 'pending', $5)",
        report_id, str(echo_id), int(reporter_id), str(reason or "")[:1000], created_at,
    )
    return {
        "report_id": report_id,
        "echo_id": str(echo_id),
        "reporter_id": int(reporter_id),
        "reason": str(reason or "")[:1000],
        "status": "pending",
        "created_at": created_at,
        "reviewed_by": None,
        "reviewed_at": None,
    }, True


async def get_echo_report(pool, report_id: str) -> dict[str, Any] | None:
    row = await pool.fetchrow(
        "SELECT report_id, echo_id, reporter_id, reason, status, created_at, "
        "reviewed_by, reviewed_at FROM echo_reports WHERE report_id = $1",
        str(report_id),
    )
    return _row(row)


async def resolve_echo_report(
    pool,
    report_id: str,
    *,
    status: str,
    reviewer_id: int,
) -> dict[str, Any] | None:
    """Resolve a pending report once; returns the updated row or ``None``."""
    if status not in {"valid", "invalid"}:
        raise ValueError("A report can only be resolved as valid or invalid.")
    current = await get_echo_report(pool, report_id)
    if current is None or current.get("status") != "pending":
        return None
    reviewed_at = time.time()
    await pool.execute(
        "UPDATE echo_reports SET status = $1, reviewed_by = $2, reviewed_at = $3 "
        "WHERE report_id = $4 AND status = 'pending'",
        status, int(reviewer_id), reviewed_at, str(report_id),
    )
    current.update({
        "status": status,
        "reviewed_by": int(reviewer_id),
        "reviewed_at": reviewed_at,
    })
    return current


async def add_echo_warning(
    pool,
    *,
    user_id: int,
    report_id: str,
    reason: str,
) -> int:
    """Add one warning per valid report and return the user's total."""
    existing = await pool.fetchrow(
        "SELECT warning_id FROM echo_warnings WHERE report_id = $1",
        str(report_id),
    )
    if existing is None:
        await pool.execute(
            "INSERT INTO echo_warnings (warning_id, user_id, report_id, reason, created_at) "
            "VALUES ($1, $2, $3, $4, $5)",
            uuid.uuid4().hex, int(user_id), str(report_id),
            str(reason or "")[:1000], time.time(),
        )
    return await warning_count(pool, user_id)


async def warning_count(pool, user_id: int) -> int:
    value = await pool.fetchval(
        "SELECT COUNT(*) FROM echo_warnings WHERE user_id = $1",
        int(user_id),
    )
    return int(value or 0)


async def delete_echo_report(pool, report_id: str) -> None:
    """Discard a pending report when its staff message could not be posted."""
    await pool.execute(
        "DELETE FROM echo_reports WHERE report_id = $1 AND status = 'pending'",
        str(report_id),
    )
