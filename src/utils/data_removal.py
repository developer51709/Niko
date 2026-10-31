"""Scoped deletion of account and server data.

The deletion queue is deliberately conservative. Niko keeps moderation and
safety records (bot-level blacklists, warnings, mutes, giveaway bans, abuse
strikes, scam-image reports, and ticket transcripts) because they protect
communities from people who would otherwise use a deletion request to erase
the consequences of their actions. Those records are only released through the
formal legal process described at /data-removal.

Only the tables named in ``USER_DELETIONS``, ``USER_ANONYMIZATIONS``, and
``GUILD_DELETIONS`` are touched. A new table is therefore preserved by default
until someone deliberately classifies it here.
"""

from __future__ import annotations

import json
import re
import time

# ── Account deletion ────────────────────────────────────────────────────────
# (table, column) pairs removed for the requesting user.
USER_DELETIONS: tuple[tuple[str, str], ...] = (
    ("economy_users", "user_id"),
    ("levels", "user_id"),
    ("birthday_users", "user_id"),
    ("afk_users", "user_id"),
    ("donors", "user_id"),
    ("premium_users", "user_id"),
    ("roleplay_actions", "actor_id"),
    ("roleplay_actions", "target_id"),
    ("roleplay_blocks", "blocker_id"),
    ("roleplay_blocks", "blocked_id"),
    ("poll_votes", "user_id"),
    # Niko's per-server conversation memory is personal data (the deleted
    # ``memory.json`` equivalent), so an account request clears it everywhere.
    ("ai_memory", "user_id"),
    ("participants", "user_id"),
    ("uwulock_config", "user_id"),
    ("voicemaster_channels", "owner_id"),
    ("staff_application_submissions", "user_id"),
    ("staff_team_submissions", "user_id"),
)

# References that keep server content usable but no longer identify the user.
USER_ANONYMIZATIONS: tuple[tuple[str, str, str], ...] = (
    ("suggestions", "author_id", "0"),
    ("giveaways", "host_id", "0"),
    ("sticky_messages", "created_by", "NULL"),
)

# ── Server deletion ─────────────────────────────────────────────────────────
GUILD_DELETIONS: tuple[str, ...] = (
    "ai_config",
    "ai_memory",
    "notifier_config",
    "notification_channels",
    "follows",
    "suggestion_config",
    "suggestions",
    "levels",
    "level_config",
    "prefix_config",
    "guild_profiles",
    "triggers",
    "onboarding",
    "logging_config",
    "logging_webhooks",
    "moderation_config",
    "ticket_config",
    "sticky_messages",
    "birthday_guilds",
    "server_activity",
    "starboard_config",
    "starboard_messages",
    "uwulock_config",
    "uwulock_messages",
    "voicemaster_settings",
    "voicemaster_channels",
    "giveaways",
    "polls",
    "staff_applications",
)

# ── Never deleted by a standard request ─────────────────────────────────────
# Documented on /data-removal and in the Privacy Policy. These rows survive an
# account or server deletion unless a valid legal order is handled directly by
# the bot owner.
PRESERVED_USER_RECORDS: tuple[str, ...] = (
    "Bot-level blacklists and blacklist appeals",
    "Server warnings, mutes, and moderation cases",
    "Giveaway bans",
    "Abuse strikes and safety investigations",
    "Scam-image reports and confirmed scam-image fingerprints",
    "Ticket transcripts and moderation logs",
)

PRESERVED_GUILD_RECORDS: tuple[str, ...] = (
    "Server blacklists and active feature locks",
    "Warnings, mutes, and moderation cases",
    "Giveaway bans",
    "Abuse strikes and safety investigations",
    "Scam-image reports and confirmed scam-image fingerprints",
    "Ticket transcripts and moderation logs",
)

_MISSING_TABLE = re.compile(r"no such table|no such column|not found|does not exist", re.IGNORECASE)


async def record_ownership(
    pool, guild_id: int, owner_id: int, name: str | None = None,
    icon_url: str | None = None, *, removed: bool = False,
) -> None:
    """Store the owner of a server while the bot can still see the guild."""
    now = time.time()
    removed_at = now if removed else None
    # Two statements instead of a repeated-placeholder upsert: the SQLite pool
    # turns every `$n` into its own `?`, so a value reused in an ON CONFLICT
    # clause would need to be passed twice.
    await pool.execute(
        "UPDATE guild_ownership SET owner_id = $1, guild_name = $2, "
        "icon_url = $3, last_checked_at = $4, removed_at = $5 "
        "WHERE guild_id = $6",
        owner_id,
        name,
        icon_url,
        now,
        removed_at,
        guild_id,
    )
    await pool.execute(
        "INSERT OR IGNORE INTO guild_ownership "
        "(guild_id, owner_id, guild_name, icon_url, first_seen_at, "
        "last_checked_at, removed_at) VALUES ($1, $2, $3, $4, $5, $6, $7)",
        guild_id,
        owner_id,
        name,
        icon_url,
        now,
        now,
        removed_at,
    )


async def _run(pool, sql: str, *args, errors: list[str]) -> bool:
    try:
        await pool.execute(sql, *args)
        return True
    except Exception as exc:  # pragma: no cover - backend-specific wording
        if _MISSING_TABLE.search(str(exc)):
            return False
        errors.append(f"{sql.split()[0]} {sql.split()[2] if len(sql.split()) > 2 else ''}: {exc}")
        return False


async def _run_delete(pool, table: str, column: str, value, errors: list[str]) -> None:
    await _run(pool, f"DELETE FROM {table} WHERE {column} = $1", value, errors=errors)


async def _run_anonymize(
    pool, table: str, column: str, replacement: str, match_column: str, value, errors: list[str]
) -> None:
    await _run(
        pool,
        f"UPDATE {table} SET {column} = {replacement} WHERE {match_column} = $1",
        value,
        errors=errors,
    )


async def _delete_music_data(user_id: int, errors: list[str]) -> None:
    """Erase the dedicated music database's per-user rows when it is online."""
    try:
        from utils.music.database import MusicDatabase

        music = MusicDatabase()
        pool = music.pool
        if pool is None:
            await music.ensure()
            pool = music.pool
        if pool is None:
            return
        for table in ("music_playlist_tracks", "music_playlists", "music_liked_songs"):
            await _run_delete(pool, table, "user_id", user_id, errors)
    except Exception as exc:  # pragma: no cover - music is optional
        errors.append(f"music database: {exc}")


async def execute_account_deletion(pool, user_id: int) -> dict:
    """Remove personal account data while preserving safety records."""
    errors: list[str] = []
    removed: list[str] = []
    anonymized: list[str] = []

    for table, column in USER_DELETIONS:
        # These two tables store Discord ids as TEXT because staff application
        # records are written from the web app; everything else uses INTEGER.
        value = str(user_id) if table in {"staff_application_submissions", "staff_team_submissions"} else user_id
        if await _run_delete(pool, table, column, value, errors):
            removed.append(table)

    for table, column, replacement in USER_ANONYMIZATIONS:
        if await _run_anonymize(pool, table, column, replacement, column, user_id, errors):
            anonymized.append(table)

    # Suggestion votes are stored as a JSON map of user id to vote. Remove the
    # member's key so a removed account is not still visible in server content.
    try:
        rows = await pool.fetch("SELECT message_id, voters FROM suggestions")
        for row in rows:
            raw = row.get("voters")
            if isinstance(raw, str):
                try:
                    voters = json.loads(raw or "{}")
                except Exception:
                    continue
            elif isinstance(raw, dict):
                voters = raw
            else:
                continue
            if str(user_id) in voters:
                voters.pop(str(user_id), None)
                voters.pop(user_id, None)
                await _run(
                    pool,
                    "UPDATE suggestions SET voters = $1 WHERE message_id = $2",
                    json.dumps(voters),
                    row["message_id"],
                    errors=errors,
                )
    except Exception as exc:
        if not _MISSING_TABLE.search(str(exc)):
            errors.append(f"suggestion votes: {exc}")

    # Gift attribution is personal data; the subscription and payment records
    # themselves are financial records and stay.
    await _run(
        pool,
        "UPDATE premium_subscriptions SET gifted_by = NULL, gifted_by_name = NULL "
        "WHERE gifted_by = $1",
        user_id,
        errors=errors,
    )

    await _delete_music_data(user_id, errors)

    # The public staff profile is personal data, not a moderation record. Clear
    # every public field while leaving the internal role assignment and status
    # intact so the team can still account for a former or suspended member.
    if await _run(
        pool,
        "UPDATE staff_members SET public_name = NULL, public_bio = NULL, "
        "public_avatar_url = NULL, public_banner_url = NULL, "
        "public_links = NULL, public_visible = 0 WHERE user_id = $1",
        user_id,
        errors=errors,
    ):
        removed.append("staff_members:public_profile")

    return {
        "scope": "account",
        "user_id": str(user_id),
        "removed": sorted(set(removed)),
        "anonymized": sorted(set(anonymized)),
        "preserved": list(PRESERVED_USER_RECORDS),
        "errors": errors,
    }


async def _delete_child_rows(pool, guild_id: int, errors: list[str]) -> None:
    """Remove giveaway entries, poll votes, and staff submissions before parents."""
    try:
        rows = await pool.fetch("SELECT message_id FROM giveaways WHERE guild_id = $1", guild_id)
        for row in rows:
            await _run_delete(pool, "participants", "message_id", row["message_id"], errors)
    except Exception as exc:
        if not _MISSING_TABLE.search(str(exc)):
            errors.append(f"giveaway entries: {exc}")

    try:
        rows = await pool.fetch("SELECT message_id FROM polls WHERE guild_id = $1", guild_id)
        for row in rows:
            await _run_delete(pool, "poll_votes", "message_id", row["message_id"], errors)
    except Exception as exc:
        if not _MISSING_TABLE.search(str(exc)):
            errors.append(f"poll votes: {exc}")

    try:
        rows = await pool.fetch("SELECT id FROM staff_applications WHERE guild_id = $1", guild_id)
        for row in rows:
            await _run_delete(
                pool, "staff_application_submissions", "application_id", row["id"], errors
            )
    except Exception as exc:
        if not _MISSING_TABLE.search(str(exc)):
            errors.append(f"staff application submissions: {exc}")


async def execute_guild_deletion(pool, guild_id: int) -> dict:
    """Remove a server's configuration and content while preserving safety records."""
    errors: list[str] = []
    removed: list[str] = []

    await _delete_child_rows(pool, guild_id, errors)

    for table in GUILD_DELETIONS:
        if await _run_delete(pool, table, "guild_id", guild_id, errors):
            removed.append(table)

    return {
        "scope": "server",
        "guild_id": str(guild_id),
        "removed": sorted(set(removed)),
        "preserved": list(PRESERVED_GUILD_RECORDS),
        "errors": errors,
    }
