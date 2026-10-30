"""Feature lockdown for blacklisted guilds.

Blacklisting a server has to leave that server's own configuration exactly as it
was while making every Niko feature unusable: an appeal is approved with one
click, so a locked guild has to be able to come back the way it left. This
module owns that two-way switch.

The work is split into small, ordered, independent steps:

    database      the blacklist row itself (written by ``BlacklistManager``)
    social        the notifier's server-wide switch is turned off
    starboard     the saved starboard channel is cleared
    polls         open polls are locked, so votes are refused
    giveaways     active giveaways are locked: no entries, no draw
    notification  the guild owner is told the server was blacklisted

Every step records what the feature looked like beforehand in
``guild_feature_locks``, which is what ``restore_guild_features`` replays when
the blacklist is lifted. Steps never raise: the blacklist entry must stand even
when one feature cannot be switched off, so each result is reported to the
caller (the dashboard shows it in the summary) and logged here.

Nothing in this module depends on a running gateway: the bot is optional and a
step that needs it reports ``skipped`` when it is missing, which is also what
keeps the lockdown testable with a fake bot.
"""

import json
import time
from typing import Any, Iterable, Optional

import discord

import database as database_module
from utils import logging
from utils.i18n import make_flat_msg
from utils.social.follows import pause_guild_notifications
from utils.locales import load_locales

#: Ordered lockdown steps and the wording the dashboard shows while each one
#: runs. The keys are a contract with ``web/src/utils/guildBlacklist.ts``.
LOCKDOWN_STEPS: tuple[tuple[str, str], ...] = (
    ("database", "Saving to database…"),
    ("social", "Pausing social notifs…"),
    ("starboard", "Disabling starboard…"),
    ("polls", "Disabling polls…"),
    ("giveaways", "Disabling giveaways…"),
    ("notification", "Sending blacklist notification…"),
)

#: Step key -> dashboard wording.
LOCKDOWN_LABELS: dict[str, str] = dict(LOCKDOWN_STEPS)

#: The steps the dashboard drives one request at a time. ``database`` is the
#: blacklist write itself, which the caller has already performed.
FEATURE_STEPS: tuple[str, ...] = tuple(
    key for key, _ in LOCKDOWN_STEPS if key != "database"
)

PAUSED_MESSAGES = load_locales(__package__, "messages")

_paused = make_flat_msg(PAUSED_MESSAGES)


def paused_message(ctx) -> str:
    """Reply for a feature that a blacklist lockdown switched off.

    Used by the feature buttons that live outside the slash-command blacklist
    gate (poll votes, giveaway entries), so they answer in the member's language
    instead of silently doing nothing.
    """
    return _paused(ctx, "paused")


#: Features whose saved state is replayed when the blacklist is lifted. The
#: notifier and the owner notification are deliberately absent: a server turns
#: its own announcements back on, as the social-notifier docs describe.
RESTORABLE_FEATURES: tuple[str, ...] = ("starboard", "polls", "giveaways")

_STARBOARD_FALLBACK_THRESHOLD = 3
_STARBOARD_FALLBACK_EMOJI = "⭐"


def step_label(step: str) -> str:
    """Dashboard wording for a step key, falling back to the key itself."""
    return LOCKDOWN_LABELS.get(step, step)


def _result(step: str, status: str, detail: str) -> dict:
    return {"step": step, "label": step_label(step), "status": status, "detail": detail}


def _truthy(value: Any) -> bool:
    """Read a boolean that either backend may have stored as 0/False/'0'."""
    if isinstance(value, str):
        return value.strip().lower() not in {"", "0", "false", "none", "null"}
    return bool(value)


async def ensure_schema(pool) -> None:
    """Create the lockdown table and the ``locked`` columns, idempotently.

    Both backends are covered: SQLite gets the real DDL, and MongoDB ignores
    ``ALTER TABLE`` the same way the cogs' own migrations do.
    """
    if pool is None:
        return
    try:
        await pool.execute(
            "CREATE TABLE IF NOT EXISTS guild_feature_locks ("
            "guild_id INTEGER NOT NULL, "
            "feature TEXT NOT NULL, "
            "previous_state TEXT, "
            "note TEXT, "
            "locked_at TEXT, "
            "PRIMARY KEY (guild_id, feature))"
        )
    except Exception:
        pass
    for statement in (
        "ALTER TABLE polls ADD COLUMN locked INTEGER DEFAULT 0",
        "ALTER TABLE giveaways ADD COLUMN locked INTEGER DEFAULT 0",
    ):
        try:
            await pool.execute(statement)
        except Exception:
            # Column already exists on the current schema.
            pass


async def record_lock(
    pool,
    guild_id: int,
    feature: str,
    *,
    previous_state: Optional[dict] = None,
    note: Optional[str] = None,
) -> None:
    """Persist what a feature looked like before the lockdown switched it off."""
    if pool is None:
        return
    await pool.execute(
        "INSERT OR REPLACE INTO guild_feature_locks "
        "(guild_id, feature, previous_state, note, locked_at) VALUES ($1, $2, $3, $4, $5)",
        int(guild_id),
        feature,
        json.dumps(previous_state or {}),
        note,
        _utc_now(),
    )


async def clear_lock(pool, guild_id: int, feature: str) -> None:
    if pool is None:
        return
    await pool.execute(
        "DELETE FROM guild_feature_locks WHERE guild_id = $1 AND feature = $2",
        int(guild_id),
        feature,
    )


async def read_locks(pool, guild_id: int) -> list:
    """Every lockdown record for one guild, newest last."""
    if pool is None:
        return []
    try:
        rows = await pool.fetch(
            "SELECT feature, previous_state, note, locked_at "
            "FROM guild_feature_locks WHERE guild_id = $1",
            int(guild_id),
        )
    except Exception:
        return []
    locks = []
    for row in rows:
        raw = row.get("previous_state")
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except (TypeError, ValueError):
                raw = {}
        locks.append({
            "feature": row.get("feature"),
            "previous_state": raw if isinstance(raw, dict) else {},
            "note": row.get("note"),
            "locked_at": row.get("locked_at"),
        })
    return locks


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ── individual steps ─────────────────────────────────────────────────────────

async def _step_social(pool, guild_id: int) -> dict:
    """Turn the server's notifier switch off, keeping follows and channels."""
    try:
        paused = await pause_guild_notifications(pool, guild_id)
    except Exception as exc:
        return _result("social", "failed", f"Social notifications could not be paused: {exc}")
    if not paused:
        return _result("social", "skipped", "This server does not use social notifications.")
    await record_lock(
        pool,
        guild_id,
        "social",
        previous_state={"enabled": True},
        note="Notifier paused while the server is blacklisted.",
    )
    return _result("social", "done", "Social notification posts are paused.")


async def _step_starboard(pool, guild_id: int, bot=None) -> dict:
    """Clear the starboard channel, keeping the rest of its settings."""
    try:
        row = await pool.fetchrow(
            "SELECT channel_id, threshold, emoji, ignored_channels "
            "FROM starboard_config WHERE guild_id = $1",
            int(guild_id),
        )
    except Exception as exc:
        return _result("starboard", "failed", f"Starboard settings could not be read: {exc}")
    if not row or row.get("channel_id") in (None, ""):
        return _result("starboard", "skipped", "This server has no starboard channel configured.")

    channel_id = int(row["channel_id"])
    threshold = row.get("threshold") or _STARBOARD_FALLBACK_THRESHOLD
    emoji = row.get("emoji") or _STARBOARD_FALLBACK_EMOJI
    ignored = row.get("ignored_channels") or "[]"
    if isinstance(ignored, list):
        ignored = json.dumps(ignored)
    try:
        # The cleared channel is what the starboard cog reads as "off", so the
        # feature stays off after a restart without any new column.
        await pool.execute(
            "INSERT OR REPLACE INTO starboard_config "
            "(guild_id, channel_id, threshold, emoji, ignored_channels) "
            "VALUES ($1, $2, $3, $4, $5)",
            int(guild_id),
            None,
            threshold,
            emoji,
            ignored,
        )
        await record_lock(
            pool,
            guild_id,
            "starboard",
            previous_state={"channel_id": channel_id},
            note="Starboard channel saved and switched off.",
        )
    except Exception as exc:
        return _result("starboard", "failed", f"The starboard could not be switched off: {exc}")

    _forget_starboard_channel(bot, guild_id)
    return _result("starboard", "done", f"Starboard channel <#{channel_id}> saved and switched off.")


def _forget_starboard_channel(bot, guild_id: int) -> None:
    """Drop the cleared channel from the live cog so it stops posting at once."""
    cog = bot.get_cog("Starboard") if bot is not None and hasattr(bot, "get_cog") else None
    guilds = getattr(cog, "data", {}).get("guilds") if cog is not None else None
    if not isinstance(guilds, dict):
        return
    entry = guilds.get(str(int(guild_id)))
    if isinstance(entry, dict):
        entry["channel_id"] = None


async def _lock_rows(pool, guild_id: int, *, table: str, state_column: str, step: str) -> dict:
    """Lock every not-yet-finished row of ``table`` for one guild.

    Rows are read first and written one by one: the Mongo query layer only
    parses simple ``WHERE`` clauses, and a per-row update also keeps the report
    honest about how many records were touched.
    """
    try:
        rows = await pool.fetch(
            f"SELECT message_id, {state_column}, locked FROM {table} WHERE guild_id = $1",
            int(guild_id),
        )
    except Exception as exc:
        return _result(step, "failed", f"{table.capitalize()} could not be read: {exc}")

    locked_ids = [
        int(row["message_id"])
        for row in rows
        if not _truthy(row.get(state_column)) and not _truthy(row.get("locked"))
    ]
    if not locked_ids:
        return _result(step, "skipped", f"This server has no active {step} to pause.")

    for message_id in locked_ids:
        try:
            await pool.execute(
                f"UPDATE {table} SET locked = $1 WHERE message_id = $2",
                1,
                message_id,
            )
        except Exception as exc:
            return _result(step, "failed", f"{table.capitalize()} could not be paused: {exc}")
    await record_lock(
        pool,
        guild_id,
        step,
        previous_state={"message_ids": locked_ids, "count": len(locked_ids)},
        note=f"{len(locked_ids)} {step} paused while the server is blacklisted.",
    )
    return _result(step, "done", f"{len(locked_ids)} active {step} paused.")


async def _step_polls(pool, guild_id: int) -> dict:
    return await _lock_rows(
        pool, guild_id, table="polls", state_column="closed", step="polls"
    )


async def _step_giveaways(pool, guild_id: int) -> dict:
    return await _lock_rows(
        pool, guild_id, table="giveaways", state_column="ended", step="giveaways"
    )


def _owner_notice_view(reason: Optional[str], source=None) -> "discord.ui.LayoutView":
    """The DM a blacklisted server's owner receives, in the server's language."""
    text = lambda key, **kwargs: _paused(source, key, **kwargs)  # noqa: E731
    appeal_url = "https://niko.sryze.cc/appeals/blacklist"
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=text("blacklist_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=text("blacklist_from")),
        discord.ui.TextDisplay(content=(
            f"{text('blacklist_reason_title')}\n"
            f"{reason or text('blacklist_no_reason')}"
        )),
        discord.ui.TextDisplay(content=text("blacklist_body")),
        discord.ui.TextDisplay(content=text("blacklist_appeal", url=appeal_url)),
        accent_colour=discord.Colour.red(),
    ))
    return view


async def _step_notification(pool, guild_id: int, reason: Optional[str], bot=None) -> dict:
    """DM the guild owner so the blacklist never happens silently."""
    if bot is None or not hasattr(bot, "get_guild"):
        return _result("notification", "skipped", "The bot is not available to send the notification.")
    guild = bot.get_guild(int(guild_id))
    if guild is None:
        return _result("notification", "skipped", "The guild is not connected, so its owner could not be notified.")
    owner = getattr(guild, "owner", None)
    if owner is None:
        owner_id = getattr(guild, "owner_id", None)
        owner = guild.get_member(owner_id) if owner_id and hasattr(guild, "get_member") else None
    if owner is None:
        return _result("notification", "skipped", "The guild owner could not be resolved, so no notification was sent.")
    try:
        await owner.send(view=_owner_notice_view(reason, guild))
    except discord.Forbidden:
        return _result("notification", "failed", "The guild owner has direct messages closed.")
    except Exception as exc:
        return _result("notification", "failed", f"The notification could not be sent: {exc}")
    return _result("notification", "done", "The guild owner was notified by direct message.")


# ── orchestration ────────────────────────────────────────────────────────────

async def run_lockdown_step(bot, pool, guild_id: int, step: str, *, reason: Optional[str] = None) -> dict:
    """Run one lockdown step for one guild and report the outcome."""
    if step == "database":
        return _result("database", "done", "Blacklist entry saved.")
    if step == "social":
        return await _step_social(pool, guild_id)
    if step == "starboard":
        return await _step_starboard(pool, guild_id, bot)
    if step == "polls":
        return await _step_polls(pool, guild_id)
    if step == "giveaways":
        return await _step_giveaways(pool, guild_id)
    if step == "notification":
        return await _step_notification(pool, guild_id, reason, bot)
    return _result(step, "failed", f"Unknown lockdown step: {step}")


async def lock_guild(
    bot,
    pool,
    guild_id: int,
    *,
    reason: Optional[str] = None,
    steps: Optional[Iterable[str]] = None,
) -> list:
    """Run the lockdown steps for one guild and return their report.

    ``steps`` defaults to every feature step in the documented order. Steps are
    independent: one failing never stops the next, so the caller can show the
    dashboard exactly which feature is still switched on.
    """
    await ensure_schema(pool)
    report = []
    for step in (list(steps) if steps is not None else list(FEATURE_STEPS)):
        try:
            result = await run_lockdown_step(bot, pool, guild_id, step, reason=reason)
        except Exception as exc:
            result = _result(step, "failed", f"The step could not be completed: {exc}")
        if result["status"] == "failed":
            logging.warning("guild_lockdown", f"Guild {guild_id} step '{step}' failed: {result['detail']}")
        report.append(result)
    return report


async def restore_guild_features(bot, pool, guild_id: int) -> list:
    """Give a guild its saved features back after the blacklist is lifted.

    Only the features this module locked are restored, and only while their lock
    record still exists, so an admin who changed a setting during the blacklist
    does not have that change undone twice. Restoring is best effort: the
    blacklist removal stands even when a feature cannot be switched back on.
    """
    if pool is None:
        return []
    results = []
    for lock in await read_locks(pool, guild_id):
        feature = lock.get("feature")
        try:
            if feature not in RESTORABLE_FEATURES:
                # Nothing to replay for this feature — the notifier is switched
                # back on by the server itself — so its record is retired along
                # with the replayed ones instead of lingering as a stale lock
                # that would make a later blacklist look half-applied.
                await clear_lock(pool, guild_id, feature)
                continue
            if feature == "starboard":
                results.append(await _restore_starboard(bot, pool, guild_id, lock))
            else:
                results.append(await _restore_locked_rows(pool, guild_id, feature))
        except Exception as exc:
            logging.warning("guild_lockdown", f"Guild {guild_id} could not restore {feature}: {exc}")
            results.append(_result(feature, "failed", f"{feature.capitalize()} could not be restored: {exc}"))
    if results:
        logging.info(
            "guild_lockdown",
            f"Restored {sum(1 for item in results if item['status'] == 'done')}/{len(results)} locked feature(s) for guild {guild_id}.",
        )
    return results


async def _restore_starboard(bot, pool, guild_id: int, lock: dict) -> dict:
    channel_id = (lock.get("previous_state") or {}).get("channel_id")
    if not channel_id:
        await clear_lock(pool, guild_id, "starboard")
        return _result("starboard", "skipped", "No saved starboard channel to restore.")
    row = await pool.fetchrow(
        "SELECT channel_id, threshold, emoji, ignored_channels FROM starboard_config WHERE guild_id = $1",
        int(guild_id),
    )
    if row and row.get("channel_id") not in (None, ""):
        # Someone re-configured the starboard during the blacklist: keep theirs.
        await clear_lock(pool, guild_id, "starboard")
        return _result("starboard", "skipped", "The starboard was reconfigured during the blacklist, so its own channel was kept.")
    ignored = (row or {}).get("ignored_channels") or "[]"
    if isinstance(ignored, list):
        ignored = json.dumps(ignored)
    await pool.execute(
        "INSERT OR REPLACE INTO starboard_config "
        "(guild_id, channel_id, threshold, emoji, ignored_channels) VALUES ($1, $2, $3, $4, $5)",
        int(guild_id),
        int(channel_id),
        (row or {}).get("threshold") or _STARBOARD_FALLBACK_THRESHOLD,
        (row or {}).get("emoji") or _STARBOARD_FALLBACK_EMOJI,
        ignored,
    )
    _remember_starboard_channel(bot, guild_id, int(channel_id))
    await clear_lock(pool, guild_id, "starboard")
    return _result("starboard", "done", f"Starboard channel <#{int(channel_id)}> restored.")


def _remember_starboard_channel(bot, guild_id: int, channel_id: int) -> None:
    """Put the restored channel back into the live cog without a restart."""
    cog = bot.get_cog("Starboard") if bot is not None and hasattr(bot, "get_cog") else None
    guilds = getattr(cog, "data", {}).get("guilds") if cog is not None else None
    if not isinstance(guilds, dict):
        return
    entry = guilds.get(str(int(guild_id)))
    if isinstance(entry, dict):
        entry["channel_id"] = int(channel_id)


async def _restore_locked_rows(pool, guild_id: int, feature: str) -> dict:
    table = "polls" if feature == "polls" else "giveaways"
    rows = await pool.fetch(
        f"SELECT message_id, locked FROM {table} WHERE guild_id = $1",
        int(guild_id),
    )
    locked_ids = [int(row["message_id"]) for row in rows if _truthy(row.get("locked"))]
    if not locked_ids:
        await clear_lock(pool, guild_id, feature)
        return _result(feature, "skipped", f"No paused {feature} to restore.")
    for message_id in locked_ids:
        await pool.execute(
            f"UPDATE {table} SET locked = $1 WHERE message_id = $2",
            0,
            message_id,
        )
    await clear_lock(pool, guild_id, feature)
    return _result(feature, "done", f"{len(locked_ids)} {feature} resumed.")
