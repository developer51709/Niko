"""
Startup — background sync tasks.
Runs slash-command sync and emoji sync as fire-and-forget tasks.

The slash sync only talks to Discord when the command tree actually changed.
Discord caps global-command bulk overwrites at 200 per day per application,
so syncing on every boot — especially during a crash/restart loop — can trip
Discord's rate limiter and make the whole bot appear globally rate limited.
A fingerprint of the tree is compared against the last successful sync.

The fingerprint lives in the main database (sync_state table) so it survives
restarts and redeploys — local files on hosts like Render are ephemeral and
are wiped on every deployment.
"""

import hashlib
import json
import os

from utils import logging
from utils.emoji_sync import sync_application_emojis

_FINGERPRINT_KEY = "slash_command_fingerprint"
_LEGACY_FINGERPRINT_FILE = "data/slash_command_fingerprint.json"


def _command_fingerprint(bot) -> str:
    """Deterministic hash of the current global application-command tree."""
    payload = [
        command.to_dict()
        for command in sorted(bot.tree.get_commands(), key=lambda command: command.name)
    ]
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


async def _db_stored_fingerprint(bot) -> str | None:
    """Return the fingerprint of the last successful sync from the database.

    Falls back to the legacy JSON file once (migrating it into the database)
    so the first boot after this change does not force a redundant sync.
    """
    if bot.cxn is None:
        logging.warning("SlashSync", "Database unavailable — fingerprint lookup skipped.")
        return None
    try:
        stored = await bot.cxn.fetchval(
            "SELECT value FROM sync_state WHERE key = $1", _FINGERPRINT_KEY
        )
        if stored:
            return stored

        # One-time migration of the legacy local fingerprint file.
        if os.path.exists(_LEGACY_FINGERPRINT_FILE):
            try:
                with open(_LEGACY_FINGERPRINT_FILE) as file:
                    legacy = json.load(file).get("fingerprint")
                if legacy:
                    await bot.cxn.execute(
                        "INSERT INTO sync_state (key, value) VALUES ($1, $2) "
                        "ON CONFLICT (key) DO UPDATE SET value = $3",
                        _FINGERPRINT_KEY, legacy, legacy,
                    )
                    os.rename(
                        _LEGACY_FINGERPRINT_FILE,
                        _LEGACY_FINGERPRINT_FILE + ".migrated",
                    )
                    logging.info("SlashSync", "Migrated legacy fingerprint file into database.")
                    return legacy
            except Exception as exc:
                logging.warning(
                    "SlashSync", f"Could not migrate legacy fingerprint file: {exc}"
                )
        return None
    except Exception as exc:
        logging.warning("SlashSync", f"Could not read fingerprint from database: {exc}")
        return None


async def _db_store_fingerprint(bot, fingerprint: str) -> None:
    if bot.cxn is None:
        return
    try:
        await bot.cxn.execute(
            "INSERT INTO sync_state (key, value) VALUES ($1, $2) "
            "ON CONFLICT (key) DO UPDATE SET value = $3",
            _FINGERPRINT_KEY, fingerprint, fingerprint,
        )
    except Exception as exc:
        logging.warning("SlashSync", f"Could not store command fingerprint: {exc}")


async def run_slash_sync(bot):
    fingerprint = _command_fingerprint(bot)
    command_count = len(bot.tree.get_commands())
    try:
        if await _db_stored_fingerprint(bot) == fingerprint:
            logging.info(
                "SlashSync",
                f"No command changes — skipped global sync "
                f"({command_count} command(s)).",
            )
            return
        synced = await bot.tree.sync()
        # Persist only after Discord accepted the sync so a rate-limited
        # attempt is retried on the next boot instead of being skipped.
        await _db_store_fingerprint(bot, fingerprint)
        logging.success("SlashSync", f"Synced {len(synced)} application command(s) globally.")
    except Exception as exc:
        logging.error("SlashSync", f"Startup slash sync failed: {exc}")


async def run_emoji_sync(bot):
    try:
        await sync_application_emojis(bot)
    except Exception as exc:
        logging.error("EmojiSync", f"Startup emoji sync failed: {exc}")
