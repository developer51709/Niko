"""Compose and deliver official Niko staff broadcasts.

The composer lives in the staff workspace, so a broadcast is a database record
rather than a Discord view that only exists in one channel. Delivery is a
background job on the bot loop:

* every delivery snapshots the guilds that are eligible right now, which keeps
  a retry and a later edit deterministic;
* images are stored base64-encoded with the record and re-uploaded as real
  Discord file attachments (``attachment://`` references), so a copy does not
  break when an external CDN link expires;
* each send waits ``SEND_INTERVAL_SECONDS`` and retries once on a 429, keeping
  a large broadcast inside Discord's rate limits instead of stalling on one;
* the row's counters are written after every copy, which is what the dashboard
  progress bar polls while the job runs;
* a stored channel that a server deleted, or one left behind after the server
  removed Niko, is skipped and cleared instead of failing the run;
* a sent broadcast can be edited, and every message recorded in
  ``staff_broadcast_targets`` is updated in place.
"""

from __future__ import annotations

import asyncio
import base64
import io
import time

import discord
from discord import MediaGalleryItem, UnfurledMediaItem

from utils.blacklist_manager import BlacklistManager

DEFAULT_ACCENT = "C8A882"
DEFAULT_FOOTER = "Official Niko staff announcement"
MAX_TITLE = 160
MAX_BODY = 3800
MAX_FOOTER = 120
MAX_MEDIA_ITEMS = 10
MAX_MEDIA_BYTES = 8 * 1024 * 1024
SEND_INTERVAL_SECONDS = 0.4
SYNC_INTERVAL_SECONDS = 0.35

# Content types the dashboard accepts for upload. The extension is chosen from
# the bytes' reported type rather than the uploaded filename, so an attachment
# always gets a filename Discord recognises.
IMAGE_TYPES = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
}

ACTIVE_STATUSES = {"sending", "syncing"}

# Claims are serialised on the bot loop so two dashboard requests cannot both
# read a draft as sendable and queue the same announcement twice.
_delivery_lock = asyncio.Lock()


def normalise_accent(value: str | None) -> str:
    """Return a bare six-digit hex accent, falling back to the brand colour."""
    raw = str(value or "").strip().lstrip("#").upper()
    if len(raw) == 6 and all(character in "0123456789ABCDEF" for character in raw):
        return raw
    return DEFAULT_ACCENT


def accent_colour(value: str | None) -> discord.Colour:
    return discord.Colour(int(normalise_accent(value), 16))


def _media_url(filename: str) -> str:
    """Point a CV2 gallery item at the file uploaded with the same message."""
    return f"attachment://{filename}"


def build_broadcast_view(
    title: str,
    body: str,
    footer: str,
    accent: str,
    media: list[dict],
) -> discord.ui.LayoutView:
    """Build the Components v2 container shared by delivery and edits."""
    view = discord.ui.LayoutView()
    items: list = [
        discord.ui.TextDisplay(content=f"# {title}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=body),
    ]
    gallery = [row for row in media if row.get("filename")]
    if gallery:
        items.extend([
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.MediaGallery(*[
                MediaGalleryItem(media=UnfurledMediaItem(url=_media_url(str(row["filename"]))))
                for row in gallery[:MAX_MEDIA_ITEMS]
            ]),
        ])
    if footer:
        items.extend([
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"-# {footer}"),
        ])
    view.add_item(discord.ui.Container(*items, accent_colour=accent_colour(accent)))
    return view


def build_broadcast_files(media: list[dict]) -> list[discord.File]:
    """Return fresh attachment objects for one delivery or edit.

    A ``discord.File`` owns its stream and is uploaded once, so every target
    gets its own file objects instead of sharing one consumed buffer.
    """
    files: list[discord.File] = []
    for row in media[:MAX_MEDIA_ITEMS]:
        payload = row.get("payload")
        if not isinstance(payload, bytes):
            try:
                payload = base64.b64decode(str(row.get("data") or ""))
            except Exception:
                continue
        if not payload:
            continue
        files.append(discord.File(io.BytesIO(payload), filename=str(row["filename"])))
    return files


def split_targets(rows: list, is_blacklisted) -> tuple[list[dict], int]:
    """Separate deliverable guild channels from blacklisted servers.

    Official announcements are a Niko feature too: a blacklisted server stops
    receiving broadcasts until its appeal is approved. Rows with unusable IDs
    are ignored rather than failing the whole run.
    """
    eligible: list[dict] = []
    skipped = 0
    for row in rows:
        try:
            guild_id = int(row["guild_id"])
            channel_id = int(row["channel_id"])
        except (KeyError, TypeError, ValueError):
            continue
        if is_blacklisted(guild_id):
            skipped += 1
            continue
        eligible.append({"guild_id": guild_id, "channel_id": channel_id})
    return eligible, skipped


async def _load_media(cxn, broadcast_id: str) -> list[dict]:
    rows = await cxn.fetch(
        "SELECT media_id, filename, content_type, size, position, data "
        "FROM staff_broadcast_media WHERE broadcast_id = $1 ORDER BY position ASC",
        broadcast_id,
    )
    media: list[dict] = []
    for row in rows:
        item = dict(row)
        # Decode once per job: a broadcast can fan out to thousands of guilds
        # and re-decoding the same base64 per copy would dominate the run.
        try:
            item["payload"] = base64.b64decode(str(item.get("data") or ""))
        except Exception:
            item["payload"] = b""
        media.append(item)
    return media


def _retry_after(exc: Exception) -> float:
    value = getattr(exc, "retry_after", None)
    try:
        return max(0.0, min(float(value), 30.0))
    except (TypeError, ValueError):
        return 1.0


def _guild_gone(bot, guild_id: int) -> bool:
    """Whether the bot has left a guild, using the gateway cache only.

    A server that removes Niko leaves its announcement channel id behind in
    ``notification_channels``. Checking the cache costs no API call and cannot
    produce a false positive once the cache is ready, which is why the check
    is used both to prune those rows and to skip their copy.
    """
    get_guild = getattr(bot, "get_guild", None)
    if get_guild is None:
        return False
    is_ready = getattr(bot, "is_ready", None)
    try:
        if callable(is_ready) and not is_ready():
            return False
        return get_guild(int(guild_id)) is None
    except Exception:
        return False


async def _resolve_channel(bot, channel_id: int, guild_id: int | None = None) -> tuple:
    """Resolve a stored channel and report whether it can never work again.

    Returns ``(channel, stale)``. ``stale`` is only True when Discord proves the
    guild or channel is gone; a permission problem leaves the stored opt-in in
    place, so the owner can fix it instead of the server being forgotten.
    """
    if guild_id is not None and _guild_gone(bot, guild_id):
        return None, True
    channel = bot.get_channel(channel_id)
    if channel is not None:
        return channel, False
    try:
        return await bot.fetch_channel(channel_id), False
    except discord.NotFound:
        return None, True
    except (discord.Forbidden, discord.HTTPException):
        return None, False
    except Exception:
        return None, False


async def _forget_stale_channel(cxn, guild_id: int, channel_id: int) -> None:
    """Drop a stored announcement channel id that can no longer resolve.

    The row is the per-guild broadcast opt-in, so clearing it keeps a deleted
    channel or a server that removed the bot from failing every later run.
    """
    try:
        await cxn.execute(
            "DELETE FROM notification_channels WHERE guild_id = $1 AND channel_id = $2",
            int(guild_id), int(channel_id),
        )
    except Exception:
        pass


async def _send_copy(
    bot, channel_id: int, row: dict, media: list[dict], guild_id: int | None = None,
) -> tuple[str, int | None, str | None]:
    """Deliver one copy, returning ``(status, message_id, error)``.

    ``skipped`` is returned for a channel or guild that no longer exists: a
    stale stored id must never be counted as a delivery failure.
    """
    channel, stale = await _resolve_channel(bot, channel_id, guild_id)
    if channel is None:
        if stale:
            return "skipped", None, "The server or channel no longer exists."
        return "failed", None, "The channel could not be reached."

    for attempt in range(2):
        files = build_broadcast_files(media)
        view = build_broadcast_view(
            str(row["title"]), str(row["body"]), str(row["footer"] or ""),
            str(row["accent"] or DEFAULT_ACCENT), media,
        )
        try:
            if files:
                message = await channel.send(view=view, files=files)
            else:
                message = await channel.send(view=view)
            return "sent", message.id, None
        except discord.RateLimited as exc:
            if attempt == 0:
                await asyncio.sleep(_retry_after(exc))
                continue
            return "failed", None, "Discord's rate limit rejected the message."
        except discord.Forbidden:
            return "failed", None, "Niko is missing permission to post in that channel."
        except discord.NotFound:
            return "skipped", None, "The channel no longer exists."
        except discord.HTTPException as exc:
            return "failed", None, f"Discord rejected the message ({exc.status})."
        except Exception:
            return "failed", None, "The copy could not be delivered."
    return "failed", None, "The copy could not be delivered."


async def _write_progress(cxn, broadcast_id: str, sent: int, failed: int, skipped: int) -> None:
    await cxn.execute(
        "UPDATE staff_broadcasts SET sent_count = $1, failed_count = $2, "
        "skipped_count = $3, updated_at = $4 WHERE broadcast_id = $5",
        int(sent), int(failed), int(skipped), time.time(), broadcast_id,
    )


async def begin_delivery(bot, broadcast_id: str) -> str | None:
    """Reserve a broadcast for sending.

    This runs on the bot loop, so two dashboard requests cannot both claim the
    same draft. Returns an error message when the broadcast must not be sent.
    """
    cxn = getattr(bot, "cxn", None)
    if cxn is None:
        return "The Discord bot is not connected to its database."
    async with _delivery_lock:
        row = await cxn.fetchrow(
            "SELECT status, sent_count FROM staff_broadcasts WHERE broadcast_id = $1",
            broadcast_id,
        )
        if row is None:
            return "That broadcast no longer exists."
        if str(row["status"]) in ACTIVE_STATUSES:
            return "That broadcast is already being delivered."
        # A sent broadcast is edited rather than re-sent: re-sending would post a
        # duplicate copy in every server.
        # ``sent_count`` is absent on a MongoDB document that was never sent:
        # the column default only exists on the SQLite table.
        if str(row["status"]) == "sent" or int(row.get("sent_count") or 0) > 0:
            return "That broadcast was already sent. Edit it to update the delivered copies."
        await cxn.execute(
            "DELETE FROM staff_broadcast_targets WHERE broadcast_id = $1", broadcast_id,
        )
        await cxn.execute(
            "UPDATE staff_broadcasts SET status = 'sending', target_count = 0, "
            "sent_count = 0, failed_count = 0, skipped_count = 0, edited_count = 0, "
            "last_error = NULL, updated_at = $1 WHERE broadcast_id = $2",
            time.time(), broadcast_id,
        )
        return None


async def deliver_broadcast(bot, broadcast_id: str) -> None:
    """Deliver a prepared broadcast to every eligible guild."""
    cxn = getattr(bot, "cxn", None)
    if cxn is None:
        return
    sent = failed = skipped = 0
    try:
        row = await cxn.fetchrow(
            "SELECT * FROM staff_broadcasts WHERE broadcast_id = $1", broadcast_id,
        )
        if row is None:
            return
        media = await _load_media(cxn, broadcast_id)

        channels = await cxn.fetch("SELECT guild_id, channel_id FROM notification_channels")
        manager = BlacklistManager()
        if not getattr(manager, "_loaded", False):
            try:
                await manager.load()
            except Exception:
                pass
        eligible, skipped = split_targets(channels, manager.is_guild_blacklisted)
        # Servers that removed Niko keep a dead channel id in the database. Drop
        # those rows before snapshotting so the run skips them instead of
        # recording a failure for every stale opt-in.
        live: list[dict] = []
        for target in eligible:
            if _guild_gone(bot, target["guild_id"]):
                await _forget_stale_channel(
                    cxn, target["guild_id"], target["channel_id"],
                )
                skipped += 1
                continue
            live.append(target)
        eligible = live
        for target in eligible:
            await cxn.execute(
                "INSERT OR REPLACE INTO staff_broadcast_targets "
                "(broadcast_id, guild_id, channel_id, status) VALUES ($1, $2, $3, 'pending')",
                broadcast_id, target["guild_id"], target["channel_id"],
            )
        await cxn.execute(
            "UPDATE staff_broadcasts SET target_count = $1, skipped_count = $2, "
            "updated_at = $3 WHERE broadcast_id = $4",
            len(eligible), skipped, time.time(), broadcast_id,
        )

        pending = await cxn.fetch(
            "SELECT guild_id, channel_id FROM staff_broadcast_targets "
            "WHERE broadcast_id = $1 AND status = 'pending' ORDER BY guild_id ASC",
            broadcast_id,
        )
        for target in pending:
            # Paced sends keep the shared bot token under Discord's global
            # bucket, so a 400-server broadcast does not trip a 429 storm.
            await asyncio.sleep(SEND_INTERVAL_SECONDS)
            status, message_id, error = await _send_copy(
                bot, int(target["channel_id"]), row, media, int(target["guild_id"]),
            )
            if status == "sent":
                sent += 1
            elif status == "skipped":
                skipped += 1
                await _forget_stale_channel(
                    cxn, int(target["guild_id"]), int(target["channel_id"]),
                )
            else:
                failed += 1
            await cxn.execute(
                "UPDATE staff_broadcast_targets SET status = $1, message_id = $2, "
                "error = $3, updated_at = $4 WHERE broadcast_id = $5 AND guild_id = $6",
                status, message_id, error, time.time(), broadcast_id, int(target["guild_id"]),
            )
            await _write_progress(cxn, broadcast_id, sent, failed, skipped)

        await cxn.execute(
            "UPDATE staff_broadcasts SET status = 'sent', updated_at = $1 "
            "WHERE broadcast_id = $2",
            time.time(), broadcast_id,
        )
    except asyncio.CancelledError:
        await _finish_failed(cxn, broadcast_id, sent, failed, skipped, "Delivery was interrupted.")
        raise
    except Exception as exc:
        await _finish_failed(cxn, broadcast_id, sent, failed, skipped, str(exc)[:500])


async def _finish_failed(cxn, broadcast_id: str, sent: int, failed: int, skipped: int, error: str) -> None:
    try:
        await cxn.execute(
            "UPDATE staff_broadcasts SET status = 'failed', sent_count = $1, "
            "failed_count = $2, skipped_count = $3, last_error = $4, updated_at = $5 "
            "WHERE broadcast_id = $6",
            int(sent), int(failed), int(skipped), error, time.time(), broadcast_id,
        )
    except Exception:
        pass


async def sync_broadcast(bot, broadcast_id: str) -> None:
    """Update every delivered copy after the stored copy is edited."""
    cxn = getattr(bot, "cxn", None)
    if cxn is None:
        return
    edited = 0
    try:
        row = await cxn.fetchrow(
            "SELECT * FROM staff_broadcasts WHERE broadcast_id = $1", broadcast_id,
        )
        if row is None:
            return
        media = await _load_media(cxn, broadcast_id)
        await cxn.execute(
            "UPDATE staff_broadcasts SET status = 'syncing', edited_count = 0, "
            "last_error = NULL, updated_at = $1 WHERE broadcast_id = $2",
            time.time(), broadcast_id,
        )
        targets = await cxn.fetch(
            "SELECT guild_id, channel_id, message_id FROM staff_broadcast_targets "
            "WHERE broadcast_id = $1 AND message_id IS NOT NULL ORDER BY guild_id ASC",
            broadcast_id,
        )
        for target in targets:
            await asyncio.sleep(SYNC_INTERVAL_SECONDS)
            channel, stale = await _resolve_channel(
                bot, int(target["channel_id"]), int(target["guild_id"]),
            )
            if channel is None:
                if stale:
                    await _forget_stale_channel(
                        cxn, int(target["guild_id"]), int(target["channel_id"]),
                    )
                continue
            message_id = int(target["message_id"])
            try:
                message = channel.get_partial_message(message_id)
            except AttributeError:
                message = None
            if message is None:
                try:
                    message = await channel.fetch_message(message_id)
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    continue
            view = build_broadcast_view(
                str(row["title"]), str(row["body"]), str(row["footer"] or ""),
                str(row["accent"] or DEFAULT_ACCENT), media,
            )
            updated = False
            missing = False
            for attempt in range(2):
                try:
                    # An explicit attachment list clears images removed in the
                    # editor; leaving it out would keep the old files attached.
                    await message.edit(view=view, attachments=build_broadcast_files(media))
                    updated = True
                    break
                except discord.RateLimited as exc:
                    if attempt == 0:
                        await asyncio.sleep(_retry_after(exc))
                        continue
                    break
                except discord.NotFound:
                    missing = True
                    break
                except Exception:
                    break
            if missing:
                await cxn.execute(
                    "UPDATE staff_broadcast_targets SET error = $1, updated_at = $2 "
                    "WHERE broadcast_id = $3 AND guild_id = $4",
                    "The delivered message no longer exists.", time.time(),
                    broadcast_id, int(target["guild_id"]),
                )
                continue
            if not updated:
                continue
            edited += 1
            await cxn.execute(
                "UPDATE staff_broadcasts SET edited_count = $1, updated_at = $2 "
                "WHERE broadcast_id = $3",
                edited, time.time(), broadcast_id,
            )
        await cxn.execute(
            "UPDATE staff_broadcasts SET status = 'sent', updated_at = $1 "
            "WHERE broadcast_id = $2",
            time.time(), broadcast_id,
        )
    except asyncio.CancelledError:
        await _finish_sync(cxn, broadcast_id, edited)
        raise
    except Exception as exc:
        try:
            await cxn.execute(
                "UPDATE staff_broadcasts SET status = 'sent', last_error = $1, "
                "updated_at = $2 WHERE broadcast_id = $3",
                str(exc)[:500], time.time(), broadcast_id,
            )
        except Exception:
            pass


async def _finish_sync(cxn, broadcast_id: str, edited: int) -> None:
    try:
        await cxn.execute(
            "UPDATE staff_broadcasts SET status = 'sent', edited_count = $1, "
            "updated_at = $2 WHERE broadcast_id = $3",
            int(edited), time.time(), broadcast_id,
        )
    except Exception:
        pass
