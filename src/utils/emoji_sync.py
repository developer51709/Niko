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
  5. Rewrite src/config/emojis.py with the live application-emoji IDs

Dev command .syncemojis triggers this manually and shows a report.
"""

from __future__ import annotations

import asyncio
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiohttp
import discord

from utils import logging
import socket

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


# ──────────────────────────────────────────────────────────────────────────────
# Upload & sync
# ──────────────────────────────────────────────────────────────────────────────
async def sync_application_emojis(
    bot: discord.Client,
    *,
    session: Optional[aiohttp.ClientSession] = None,
) -> dict:
    """
    Full sync cycle. Returns a status dict:
    {
        "parsed":    int,   # emojis found in config
        "downloaded": int,  # successfully downloaded / already cached
        "already":   int,   # already existed as application emojis
        "uploaded":  int,   # newly uploaded
        "failed":    int,   # upload / download failures
        "config_updated": bool,
    }
    """
    own_session = session is None
    if own_session:
        session = aiohttp.ClientSession()

    stats = dict(parsed=0, downloaded=0, already=0, uploaded=0, failed=0, config_updated=False)

    try:
        emojis = parse_config()
        stats["parsed"] = len(emojis)
        logging.info("EmojiSync", f"Found {len(emojis)} unique emojis in config")

        # ── 1. Download images ──────────────────────────────────────────────
        dl_results = await download_emojis(emojis, session)
        stats["downloaded"] = sum(1 for ok in dl_results.values() if ok)
        logging.info("EmojiSync", f"Downloaded/cached {stats['downloaded']}/{len(emojis)} emoji images")

        # ── 2. Fetch existing application emojis ──────────────────────────
        try:
            app_emojis: list[discord.Emoji] = await bot.fetch_application_emojis()
        except Exception as exc:
            logging.error("EmojiSync", f"Could not fetch application emojis: {exc}")
            return stats

        # Map: lowercase name → application emoji
        app_by_name: Dict[str, discord.Emoji] = {e.name.lower(): e for e in app_emojis}
        logging.info("EmojiSync", f"Bot has {len(app_emojis)} existing application emojis")

        # ── 3. Upload missing emojis ───────────────────────────────────────
        # Map: old_id → new application emoji (for config rewrite)
        id_remap: Dict[int, ParsedEmoji] = {}

        for pe in emojis:
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
                new_emoji = await bot.create_application_emoji(
                    name=pe.discord_name,
                    image=image_data,
                )
                remapped = ParsedEmoji(
                    discord_name=new_emoji.name,
                    emoji_id=new_emoji.id,
                    animated=new_emoji.animated,
                )
                id_remap[pe.emoji_id] = remapped
                stats["uploaded"] += 1
                logging.success("EmojiSync", f"Uploaded application emoji :{pe.discord_name}:")
                await asyncio.sleep(0.5)   # rate-limit courtesy
            except discord.HTTPException as exc:
                logging.error("EmojiSync", f"Failed to upload {pe.discord_name}: {exc}")
                stats["failed"] += 1

        # ── 4. Rewrite config with new IDs ────────────────────────────────
        if id_remap:
            stats["config_updated"] = _rewrite_config(id_remap)

    finally:
        if own_session:
            await session.close()

    logging.success(
        "EmojiSync",
        f"Sync complete — {stats['uploaded']} uploaded, "
        f"{stats['already']} already present, {stats['failed']} failed",
    )
    return stats


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
