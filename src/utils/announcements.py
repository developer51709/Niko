"""Send official announcements to the support server.

Announcement content is supplied by the caller (the MCP tool), so no release
text or policy notice lives in the bot. Delivery always targets the support
server's ``announcements`` channel and can mention its ``announcements_ping``
role. Optional images travel as base64 bytes and are uploaded as real Discord
attachments, matching the staff broadcast gallery.
"""

from __future__ import annotations

import asyncio
import base64
import os
import re
import uuid
from urllib.parse import urlparse

import aiohttp
import discord

from config.ids import SUPPORT_GUILD
from cogs.staff.support_server import get_support_ids
from utils.broadcast import (
    IMAGE_TYPES,
    MAX_BODY,
    MAX_FOOTER,
    MAX_MEDIA_BYTES,
    MAX_MEDIA_ITEMS,
    MAX_TITLE,
    build_broadcast_files,
    build_broadcast_view,
)

# Discord's combined attachment limit for one message. The broadcast studio
# uses the same ceiling so a gallery cannot fail only at send time.
MAX_TOTAL_MEDIA_BYTES = 20 * 1024 * 1024
_SAFE_STEM = re.compile(r"[^A-Za-z0-9._-]+")


def _image_content_type(raw: bytes) -> str | None:
    """Identify an uploaded image from its bytes, not a caller-supplied label."""
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if raw.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if raw.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    return None


def _media_stem(value: str | None) -> str:
    stem = os.path.splitext(os.path.basename(str(value or "").strip()))[0]
    return _SAFE_STEM.sub("-", stem).strip("-._")[:60]


async def _download_image(url: str, index: int) -> bytes:
    """Fetch one caller-supplied image with a hard size and time limit."""
    url = str(url or "").strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"Image {index} URL must be an http or https URL.")

    timeout = aiohttp.ClientTimeout(total=20)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ValueError(
                        f"Image {index} could not be downloaded (HTTP {response.status})."
                    )
                chunks: list[bytes] = []
                size = 0
                async for chunk in response.content.iter_chunked(64 * 1024):
                    size += len(chunk)
                    if size > MAX_MEDIA_BYTES:
                        raise ValueError(
                            f"Image {index} is larger than {MAX_MEDIA_BYTES // (1024 * 1024)} MiB."
                        )
                    chunks.append(chunk)
    except ValueError:
        raise
    except asyncio.TimeoutError as exc:
        raise ValueError(f"Image {index} timed out while downloading.") from exc
    except aiohttp.ClientError as exc:
        raise ValueError(f"Image {index} could not be downloaded.") from exc
    return b"".join(chunks)


async def _prepare_images(images) -> list[dict]:
    """Validate caller images and turn them into broadcast-style media rows.

    Each image accepts either inline base64 ``data`` or a public ``url``. URL
    images are downloaded here and then uploaded as ordinary attachments, so
    the delivered message does not depend on the source URL staying alive.
    """
    if images is None:
        return []
    if not isinstance(images, list):
        raise ValueError("Images must be an array.")
    if len(images) > MAX_MEDIA_ITEMS:
        raise ValueError(f"An announcement can carry up to {MAX_MEDIA_ITEMS} images.")

    media: list[dict] = []
    total = 0
    for index, item in enumerate(images, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Image {index} must be an object.")
        encoded = str(item.get("data") or "").strip()
        url = str(item.get("url") or "").strip()
        if bool(encoded) == bool(url):
            raise ValueError(f"Image {index} needs exactly one of data or url.")
        if url:
            payload = await _download_image(url, index)
        else:
            if encoded.startswith("data:"):
                _, separator, encoded = encoded.partition(",")
                if not separator:
                    raise ValueError(f"Image {index} has an invalid data URI.")
            encoded = "".join(encoded.split())
            # Base64 is 4 bytes for every 3 image bytes. Reject an obviously
            # large payload before decoding it, rather than allocating it all.
            if len(encoded) > 4 * ((MAX_MEDIA_BYTES + 2) // 3):
                raise ValueError(f"Image {index} is larger than {MAX_MEDIA_BYTES // (1024 * 1024)} MiB.")
            try:
                payload = base64.b64decode(encoded, validate=True)
            except Exception as exc:
                raise ValueError(f"Image {index} is not valid base64.") from exc
        if not payload:
            raise ValueError(f"Image {index} is empty.")
        if len(payload) > MAX_MEDIA_BYTES:
            raise ValueError(f"Image {index} is larger than {MAX_MEDIA_BYTES // (1024 * 1024)} MiB.")
        total += len(payload)
        if total > MAX_TOTAL_MEDIA_BYTES:
            raise ValueError(
                f"Announcement images must total {MAX_TOTAL_MEDIA_BYTES // (1024 * 1024)} MiB or less."
            )
        content_type = _image_content_type(payload)
        if content_type is None:
            raise ValueError(f"Image {index} must be a PNG, JPEG, GIF, or WebP image.")
        spoiler = item.get("spoiler", False)
        if not isinstance(spoiler, bool):
            raise ValueError(f"Image {index} spoiler must be true or false.")
        stem_source = item.get("filename")
        if not stem_source and url:
            stem_source = os.path.basename(urlparse(url).path)
        stem = _media_stem(stem_source) or "announcement"
        media.append({
            "filename": f"{stem}-{uuid.uuid4().hex[:8]}.{IMAGE_TYPES[content_type]}",
            "content_type": content_type,
            "size": len(payload),
            "spoiler": spoiler,
            "payload": payload,
        })
    return media


async def send_support_announcement(
    bot,
    *,
    title: str,
    body: str,
    footer: str | None = None,
    ping: bool = True,
    accent: str | None = None,
    images: list[dict] | None = None,
) -> dict:
    """Post one CV2 announcement in the configured support announcements channel.

    ``ping`` defaults to the support server's announcements role. The role is
    looked up from the persisted support configuration rather than a hardcoded
    ID, and a missing channel or role raises an actionable error instead of
    posting silently without the expected ping.
    """
    title = str(title or "").strip()
    body = str(body or "").strip()
    footer = str(footer or "").strip()
    if not title:
        raise ValueError("Announcements need a title.")
    if len(title) > MAX_TITLE:
        raise ValueError(f"The title must be {MAX_TITLE} characters or fewer.")
    if not body:
        raise ValueError("Announcements need a message.")
    if len(body) > MAX_BODY:
        raise ValueError(f"The message must be {MAX_BODY} characters or fewer.")
    if len(footer) > MAX_FOOTER:
        raise ValueError(f"The footer must be {MAX_FOOTER} characters or fewer.")
    media = await _prepare_images(images)

    ids = await get_support_ids(bot)
    channel_id = (ids.get("channels") or {}).get("announcements")
    if not channel_id:
        raise RuntimeError(
            "The support announcements channel is not configured. "
            "Run `.staff supportupdate` in the support server."
        )

    role_id = (ids.get("roles") or {}).get("announcements_ping")
    if ping and not role_id:
        raise RuntimeError(
            "The announcements ping role is not configured. "
            "Run `.staff supportupdate` in the support server."
        )

    channel = bot.get_channel(int(channel_id))
    if channel is None:
        channel = await bot.fetch_channel(int(channel_id))

    mention = f"<@&{int(role_id)}>" if ping else None
    # Components V2 messages cannot carry a separate ``content`` field, so the
    # role ping belongs in the footer subtext rather than the message body.
    view_footer = f"{mention} {footer}".strip() if mention else footer
    kwargs = {
        "view": build_broadcast_view(title, body, view_footer, accent, media),
        "allowed_mentions": (
            discord.AllowedMentions(
                roles=[discord.Object(id=int(role_id))], everyone=False, users=False,
            )
            if ping else discord.AllowedMentions.none()
        ),
    }
    if media:
        kwargs["files"] = build_broadcast_files(media)
    message = await channel.send(**kwargs)
    return {
        "message_id": message.id,
        "channel_id": int(channel_id),
        "guild_id": SUPPORT_GUILD,
        "pinged_role_id": int(role_id) if ping else None,
        "image_count": len(media),
        "url": getattr(message, "jump_url", None),
    }
