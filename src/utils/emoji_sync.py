"""
Application Emoji Sync
======================
Ensures all emojis used by Niko are registered as Application Emojis
(attached to the bot itself, not any guild).

Flow on startup:
  1. Parse src/config/emojis.py — collect every <:name:id> / <a:name:id>
  2. Download each one to src/assets/emojis/ (skips if file already exists)
  3. Fetch the bot's existing application emojis from Discord
  4. Upload any that are missing (by name)
  5. Rewrite src/config/emojis.py with the live application-emoji IDs, and hand
     them to the running process so nothing has to be restarted

Dev command .syncemojis triggers this manually and shows a report.
``.staff replaceemojis`` runs the same flow with ``replace=True``: it deletes
every application emoji so the whole set is re-uploaded from the local art.
Discord cannot replace an emoji's image, so regenerated PNGs only reach Discord
through a delete-and-re-upload cycle, which changes every id.
"""

from __future__ import annotations

import asyncio
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Awaitable, Callable, Dict, List, Optional, Tuple

import aiohttp
import discord

from config.emojis import apply_live_emoji_ids, swap_emoji_ids
from utils import logging
import socket

#: How long to wait between application-emoji API calls. Uploads and deletes
#: share the route's bucket, so one pause between every call keeps a full
#: replacement from spending its time backing off.
_API_PAUSE = 0.5

#: Progress is reported every this many processed emojis, and always at phase
#: changes, so a multi-minute replacement can show where it is.
_PROGRESS_EVERY = 25

#: The project's own packages. Module-level constants from these are the ones
#: that cache emoji strings at import time; see :func:`refresh_snapshot_strings`.
_PROJECT_PACKAGES = ("cogs", "config", "events", "utils", "webapp")

#: How deep to walk those constants. Message tables like
#: ``MESSAGES[lang][key][field]`` sit four or five levels down.
_SNAPSHOT_DEPTH = 8

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
EMOJIS_CONFIG = Path("src/config/emojis.py")
EMOJI_ASSETS  = Path("src/assets/emojis")
CDN_BASE      = "https://cdn.discordapp.com/emojis/{id}.{ext}"

EMOJI_RE = re.compile(r"<(?P<animated>a?):(?P<name>[A-Za-z0-9_]+):(?P<id>\d+)>")

# ──────────────────────────────────────────────────────────────────────────────
# Data model
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class ParsedEmoji:
    discord_name: str   # exact name Discord stores (case-sensitive)
    emoji_id:     int
    animated:     bool

    @property
    def ext(self) -> str:
        return "gif" if self.animated else "png"

    @property
    def cdn_url(self) -> str:
        return CDN_BASE.format(id=self.emoji_id, ext=self.ext)

    @property
    def asset_path(self) -> Path:
        return EMOJI_ASSETS / f"{self.discord_name}.{self.ext}"

    @property
    def discord_str(self) -> str:
        a = "a" if self.animated else ""
        return f"<{a}:{self.discord_name}:{self.emoji_id}>"


# ──────────────────────────────────────────────────────────────────────────────
# Parse config
# ──────────────────────────────────────────────────────────────────────────────
def parse_config() -> List[ParsedEmoji]:
    """Return one ParsedEmoji per unique (discord_name, id) pair in emojis.py."""
    text = EMOJIS_CONFIG.read_text(encoding="utf-8")
    seen: dict[int, ParsedEmoji] = {}
    for m in EMOJI_RE.finditer(text):
        eid = int(m.group("id"))
        if eid not in seen:
            seen[eid] = ParsedEmoji(
                discord_name=m.group("name"),
                emoji_id=eid,
                animated=bool(m.group("animated")),
            )
    return list(seen.values())


# ──────────────────────────────────────────────────────────────────────────────
# Download
# ──────────────────────────────────────────────────────────────────────────────
async def download_emojis(emojis: List[ParsedEmoji], session: aiohttp.ClientSession) -> Dict[int, bool]:
    """Download emoji images to src/assets/emojis/. Returns {id: success}."""
    EMOJI_ASSETS.mkdir(parents=True, exist_ok=True)
    results: Dict[int, bool] = {}

    async def _fetch(pe: ParsedEmoji) -> Tuple[int, bool]:
        if pe.asset_path.exists():
            return pe.emoji_id, True            # already cached
        try:
            async with session.get(pe.cdn_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    pe.asset_path.write_bytes(await resp.read())
                    return pe.emoji_id, True
                return pe.emoji_id, False
        except Exception as exc:
            if isinstance(exc, socket.gaierror):
                logging.error("EmojiSync", f"DNS resolution failed for {pe.cdn_url}: {exc}")
            else:
                logging.error("EmojiSync", f"Failed to download {pe.discord_name} from {pe.cdn_url}: {exc}")
            return pe.emoji_id, False

    tasks = [_fetch(pe) for pe in emojis]
    for eid, ok in await asyncio.gather(*tasks):
        results[eid] = ok
    return results


async def _retry_rate_limited(call, *, label: str, attempts: int = 4):
    """Run one emoji API call, waiting out buckets discord.py will not wait for.

    A full replacement is hundreds of calls on a single bucket. discord.py gives
    up after 30 seconds and raises :class:`discord.RateLimited`, which would
    abandon the second half of the set; a bulk operation has to sit out the
    reset instead. The wait is repeated only a few times, so a genuinely
    forbidden call still fails fast and is counted like any other failure.
    """
    for attempt in range(1, attempts + 1):
        try:
            return await call()
        except discord.RateLimited as exc:
            if attempt == attempts:
                raise
            logging.warning(
                "EmojiSync",
                f"Rate limited on {label}; waiting {exc.retry_after:.0f}s before retrying",
            )
            await asyncio.sleep(exc.retry_after)


# ──────────────────────────────────────────────────────────────────────────────
# Upload & sync
# ──────────────────────────────────────────────────────────────────────────────
async def sync_application_emojis(
    bot: discord.Client,
    *,
    session: Optional[aiohttp.ClientSession] = None,
    replace: bool = False,
    on_progress: Optional[Callable[[str], Awaitable[None]]] = None,
) -> dict:
    """
    Full sync cycle. Returns a status dict:
    {
        "parsed":    int,   # emojis found in config
        "downloaded": int,  # successfully downloaded / already cached
        "already":   int,   # already existed as application emojis
        "uploaded":  int,   # newly uploaded
        "failed":    int,   # upload / download failures
        "deleted":   int,   # application emojis deleted (``replace`` only)
        "delete_failed": int,
        "config_updated": bool,
        "live_ids":  int,   # ids the running process now uses instead of the
                            # ones written in the config when it started
    }

    ``replace=True`` deletes every application emoji and rebuilds the set from
    the local art. The download step runs first, while the old ids still
    resolve, so art that is missing locally cannot be lost with the emojis it
    belongs to. Every id changes, which is why the config is rewritten and the
    running process is handed the new ids.
    """
    own_session = session is None
    if own_session:
        session = aiohttp.ClientSession()

    stats = dict(
        parsed=0, downloaded=0, already=0, uploaded=0, failed=0,
        deleted=0, delete_failed=0, config_updated=False, live_ids=0,
    )

    async def report(message: str) -> None:
        if on_progress is not None:
            try:
                await on_progress(message)
            except Exception as exc:  # a progress edit must never fail the sync
                logging.warning("EmojiSync", f"Progress update failed: {exc}")

    try:
        emojis = parse_config()
        stats["parsed"] = len(emojis)
        logging.info("EmojiSync", f"Found {len(emojis)} unique emojis in config")

        # ── 1. Download images ──────────────────────────────────────────────
        dl_results = await download_emojis(emojis, session)
        stats["downloaded"] = sum(1 for ok in dl_results.values() if ok)
        logging.info("EmojiSync", f"Downloaded/cached {stats['downloaded']}/{len(emojis)} emoji images")

        # ── 2. Delete the existing set, when rebuilding from local art ────
        if replace:
            stats["deleted"], stats["delete_failed"] = await delete_all_application_emojis(
                bot, on_progress=report,
            )

        # ── 3. Fetch existing application emojis ──────────────────────────
        try:
            app_emojis: list[discord.Emoji] = await bot.fetch_application_emojis()
        except Exception as exc:
            logging.error("EmojiSync", f"Could not fetch application emojis: {exc}")
            return stats

        # Map: lowercase name → application emoji
        app_by_name: Dict[str, discord.Emoji] = {e.name.lower(): e for e in app_emojis}
        logging.info("EmojiSync", f"Bot has {len(app_emojis)} existing application emojis")

        # ── 4. Upload missing emojis ───────────────────────────────────────
        if replace:
            await report(f"Deleted {stats['deleted']} emojis — uploading {len(emojis)} from the local art…")

        # Map: old_id → new application emoji (for config rewrite)
        id_remap: Dict[int, ParsedEmoji] = {}

        for index, pe in enumerate(emojis, start=1):
            name_lower = pe.discord_name.lower()

            if name_lower in app_by_name:
                # Already registered — remap to current app emoji ID
                app_e = app_by_name[name_lower]
                remapped = ParsedEmoji(
                    discord_name=app_e.name,
                    emoji_id=app_e.id,
                    animated=app_e.animated,
                )
                id_remap[pe.emoji_id] = remapped
                stats["already"] += 1
                continue

            if not pe.asset_path.exists():
                logging.warning("EmojiSync", f"Skipping {pe.discord_name} — image not available")
                stats["failed"] += 1
                continue

            try:
                image_data = pe.asset_path.read_bytes()
                new_emoji = await _retry_rate_limited(
                    lambda: bot.create_application_emoji(
                        name=pe.discord_name,
                        image=image_data,
                    ),
                    label=f":{pe.discord_name}:",
                )
                remapped = ParsedEmoji(
                    discord_name=new_emoji.name,
                    emoji_id=new_emoji.id,
                    animated=new_emoji.animated,
                )
                id_remap[pe.emoji_id] = remapped
                stats["uploaded"] += 1
                logging.success("EmojiSync", f"Uploaded application emoji :{pe.discord_name}:")
                await asyncio.sleep(_API_PAUSE)   # rate-limit courtesy
            except discord.HTTPException as exc:
                logging.error("EmojiSync", f"Failed to upload {pe.discord_name}: {exc}")
                stats["failed"] += 1

            if index % _PROGRESS_EVERY == 0:
                await report(
                    f"Uploading from the local art… {index}/{len(emojis)} "
                    f"({stats['uploaded']} uploaded, {stats['failed']} failed)"
                )

        # ── 5. Rewrite config with new IDs ────────────────────────────────
        if id_remap:
            stats["config_updated"] = _rewrite_config(id_remap)
            # The file on disk is only read at import, so hand the new ids to
            # the process that is already running: every later get_emoji call
            # uses them, and the constants that cached the old strings at import
            # are rewritten. Without this the bot would keep sending ids that
            # no longer exist until it was restarted.
            remap = {old_id: new.discord_str for old_id, new in id_remap.items()}
            stats["live_ids"] = apply_live_emoji_ids(remap)
            refreshed = refresh_snapshot_strings(remap)
            logging.success(
                "EmojiSync",
                f"Applied {len(remap)} live emoji ids (no restart needed); "
                f"refreshed {refreshed} cached string(s)",
            )
            await report(
                f"Adopted {len(remap)} new emoji ids in the running bot "
                f"({refreshed} cached strings refreshed)."
            )

    finally:
        if own_session:
            await session.close()

    logging.success(
        "EmojiSync",
        f"Sync complete — {stats['uploaded']} uploaded, "
        f"{stats['already']} already present, {stats['failed']} failed"
        + (f", {stats['deleted']} deleted" if replace else ""),
    )
    return stats


# ──────────────────────────────────────────────────────────────────────────────
# Deleting the existing set
# ──────────────────────────────────────────────────────────────────────────────
async def delete_all_application_emojis(
    bot: discord.Client,
    *,
    on_progress: Optional[Callable[[str], Awaitable[None]]] = None,
) -> Tuple[int, int]:
    """Delete every application emoji; returns ``(deleted, failed)``.

    Discord has no way to replace an emoji's image, so this is the only route
    for regenerated art to reach Discord: drop the emoji and re-upload the PNG.
    A failure is logged and counted rather than raised — a half-deleted set is
    still recoverable by running the sync again, whereas aborting mid-way would
    leave the bot sending ids that were already removed.
    """
    try:
        app_emojis = await bot.fetch_application_emojis()
    except Exception as exc:
        logging.error("EmojiSync", f"Could not fetch application emojis: {exc}")
        return 0, 0

    total = len(app_emojis)
    deleted = failed = 0
    logging.info("EmojiSync", f"Deleting {total} application emojis")

    for index, emoji in enumerate(app_emojis, start=1):
        try:
            await _retry_rate_limited(emoji.delete, label=f":{emoji.name}:")
            deleted += 1
            await asyncio.sleep(_API_PAUSE)   # rate-limit courtesy
        except discord.HTTPException as exc:
            failed += 1
            logging.error("EmojiSync", f"Failed to delete :{emoji.name}: ({emoji.id}): {exc}")

        if on_progress is not None and index % _PROGRESS_EVERY == 0:
            await on_progress(f"Deleting application emojis… {index}/{total} ({failed} failed)")

    logging.success("EmojiSync", f"Deleted {deleted}/{total} application emojis ({failed} failed)")
    return deleted, failed


# ──────────────────────────────────────────────────────────────────────────────
# Live ids in the running process
# ──────────────────────────────────────────────────────────────────────────────
def refresh_snapshot_strings(remap: Dict[int, str]) -> int:
    """Rewrite emoji strings the bot's own modules cached at import time.

    Plenty of panels build their labels once, at import — the automod nuke
    labels, the notifier platform list, the voicemaster interface legend, the
    Connect Four board, the localised message tables — so those strings keep
    whichever id the config had when the process started. A snapshot holding a
    deleted id renders as raw ``<:tick:123>`` text, which is exactly the mess a
    replacement would leave behind if it only rewrote the config file.

    Only strings that contain a replaced emoji are touched: ``"<:tick:123>"``
    and ``"<:tick:123> Enabled"`` are emoji references by definition, and no
    other project constant looks like one. Returns how many were rewritten.
    """
    if not remap:
        return 0

    rewritten = 0
    for module in list(sys.modules.values()):
        name = getattr(module, "__name__", None)
        if not name or name.split(".")[0] not in _PROJECT_PACKAGES:
            continue
        for attribute, value in list(vars(module).items()):
            if attribute.startswith("__"):   # __builtins__, __annotations__, …
                continue
            replaced = _swap_snapshot(value, remap, _SNAPSHOT_DEPTH)
            if replaced is None:
                continue
            rewritten += 1
            if replaced is not value:
                setattr(module, attribute, replaced)
    return rewritten


def _swap_snapshot(value, remap: Dict[int, str], depth: int):
    """Swap ids inside one cached value; ``None`` when there is nothing to do.

    Lists and dicts are emptied and refilled in place so anything that already
    holds a reference to them — the usual ``from x import TABLE`` — sees the new
    strings too. Tuples and plain strings cannot be changed in place, so those
    come back as replacements for the caller to assign.
    """
    if isinstance(value, str):
        swapped = swap_emoji_ids(value, remap)
        return swapped if swapped != value else None
    if depth <= 0 or isinstance(value, (bytes, bytearray)):
        return None
    if isinstance(value, list):
        items = [_swap_snapshot(item, remap, depth - 1) for item in value]
        if not any(item is not None for item in items):
            return None
        for index, item in enumerate(items):
            if item is not None:
                value[index] = item
        return value
    if isinstance(value, tuple):
        items = [_swap_snapshot(item, remap, depth - 1) for item in value]
        if not any(item is not None for item in items):
            return None
        return tuple(value[i] if item is None else item for i, item in enumerate(items))
    if isinstance(value, dict):
        changed = False
        for key in list(value):
            old_value = value[key]
            new_key = _swap_snapshot(key, remap, depth - 1)
            new_value = _swap_snapshot(old_value, remap, depth - 1)
            if new_key is None and new_value is None:
                continue
            changed = True
            value[new_key if new_key is not None else key] = (
                old_value if new_value is None else new_value
            )
            if new_key is not None:
                del value[key]
        return value if changed else None
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Config rewrite
# ──────────────────────────────────────────────────────────────────────────────
def _rewrite_config(id_remap: Dict[int, ParsedEmoji]) -> bool:
    """
    Replace every <a?:name:old_id> in emojis.py where old_id is in id_remap
    with the new application emoji string.  Returns True on success.
    """
    text = EMOJIS_CONFIG.read_text(encoding="utf-8")
    original = text

    def replacer(m: re.Match) -> str:
        eid = int(m.group("id"))
        if eid in id_remap:
            return id_remap[eid].discord_str
        return m.group(0)  # unchanged

    text = EMOJI_RE.sub(replacer, text)
    if text == original:
        return False  # nothing changed

    EMOJIS_CONFIG.write_text(text, encoding="utf-8")
    logging.success("EmojiSync", "emojis.py updated with application emoji IDs")
    return True


# ──────────────────────────────────────────────────────────────────────────────
# Convenience: list application emojis
# ──────────────────────────────────────────────────────────────────────────────
async def list_application_emojis(bot: discord.Client) -> list[discord.Emoji]:
    """Return the bot's current application emojis."""
    return await bot.fetch_application_emojis()
