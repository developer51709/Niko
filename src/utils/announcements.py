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
from datetime import timedelta
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
# Keep correction tools scoped to recent posts instead of allowing arbitrary
# edits to the support server's announcement history.
ANNOUNCEMENT_MANAGE_WINDOW = timedelta(days=7)
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


def _validated_content(title, body, footer) -> tuple[str, str, str]:
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
    return title, body, footer


async def _support_announcement_channel(bot):
    ids = await get_support_ids(bot)
    channel_id = (ids.get("channels") or {}).get("announcements")
    if not channel_id:
        raise RuntimeError(
            "The support announcements channel is not configured. "
            "Run `.staff supportupdate` in the support server."
        )
    channel = bot.get_channel(int(channel_id))
    if channel is None:
        channel = await bot.fetch_channel(int(channel_id))
    return channel, ids


def _announcement_options(*, title, body, footer, ping, role_id, media) -> dict:
    mention = f"<@&{int(role_id)}>" if ping else None
    # Components V2 messages cannot carry a separate ``content`` field, so the
    # role ping belongs in the footer subtext rather than the message body.
    view_footer = f"{mention} {footer}".strip() if mention else footer
    return {
        "view": build_broadcast_view(title, body, view_footer, None, media),
        "allowed_mentions": (
            discord.AllowedMentions(
                roles=[discord.Object(id=int(role_id))], everyone=False, users=False,
            )
            if ping else discord.AllowedMentions.none()
        ),
    }


def _message_children(message):
    for component in getattr(message, "components", []) or []:
        yield from (getattr(component, "children", None) or [component])


def _existing_ping(message, role_id) -> bool:
    """Read the announcements role mention from the existing footer."""
    if not role_id:
        return False
    mention = f"<@&{int(role_id)}>"
    found = False
    for child in _message_children(message):
        content = getattr(child, "content", None)
        if isinstance(content, str) and content.startswith("-# "):
            found = mention in content
    return found


def _existing_media(message) -> list[dict]:
    """Rebuild preserved images from the existing gallery in display order."""
    attachments = {
        attachment.id: attachment
        for attachment in getattr(message, "attachments", []) or []
        if getattr(attachment, "id", None) is not None
    }
    media: list[dict] = []
    seen: set = set()
    for child in _message_children(message):
        for item in getattr(child, "items", []) or []:
            media_item = getattr(item, "media", None)
            media_url = str(getattr(media_item, "url", "") or "")
            attachment = attachments.get(getattr(media_item, "attachment_id", None))
            filename = str(getattr(attachment, "filename", "") or "")
            if not filename:
                filename = (
                    media_url.removeprefix("attachment://")
                    if media_url.startswith("attachment://")
                    else os.path.basename(urlparse(media_url).path)
                )
            if not filename or filename in seen:
                continue
            if attachment is None:
                attachment = next(
                    (a for a in attachments.values() if a.filename == filename), None,
                )
            seen.add(filename)
            media.append({
                "filename": filename,
                "url": f"attachment://{filename}" if attachment else media_url,
                "spoiler": bool(getattr(item, "spoiler", False)),
            })
    if media:
        return media

    # A legacy text-only or unparseable message has no gallery to recover.
    return [
        {"filename": attachment.filename, "spoiler": False}
        for attachment in getattr(message, "attachments", []) or []
        if getattr(attachment, "filename", None)
    ]


async def _recent_announcement(bot, message_id: int):
    """Resolve one recent bot-authored message in the announcements channel."""
    try:
        parsed_id = int(message_id)
    except (TypeError, ValueError) as exc:
        raise ValueError("message_id must be a positive integer.") from exc
    if parsed_id <= 0:
        raise ValueError("message_id must be a positive integer.")

    channel, ids = await _support_announcement_channel(bot)
    try:
        message = await channel.fetch_message(parsed_id)
    except discord.NotFound as exc:
        raise ValueError(
            "No announcement exists with that message ID in the announcements channel."
        ) from exc
    except discord.Forbidden as exc:
        raise RuntimeError("Niko cannot read messages in the announcements channel.") from exc

    bot_user_id = getattr(getattr(bot, "user", None), "id", None)
    author_id = getattr(getattr(message, "author", None), "id", None)
    if bot_user_id is None or author_id != bot_user_id:
        raise ValueError("Only Niko's own announcements can be edited or deleted.")

    created_at = getattr(message, "created_at", None)
    if created_at is not None and discord.utils.utcnow() - created_at > ANNOUNCEMENT_MANAGE_WINDOW:
        raise ValueError(
            f"Only announcements from the last {ANNOUNCEMENT_MANAGE_WINDOW.days} days "
            "can be edited or deleted."
        )
    return message, ids


async def send_support_announcement(
    bot,
    *,
    title: str,
    body: str,
    footer: str | None = None,
    ping: bool = True,
    images: list[dict] | None = None,
) -> dict:
    """Post one CV2 announcement in the configured support announcements channel.

    ``ping`` defaults to the support server's announcements role. The role is
    looked up from the persisted support configuration rather than a hardcoded
    ID, and a missing channel or role raises an actionable error instead of
    posting silently without the expected ping.
    """
    title, body, footer = _validated_content(title, body, footer)
    media = await _prepare_images(images)
    channel, ids = await _support_announcement_channel(bot)
    channel_id = (ids.get("channels") or {}).get("announcements")

    role_id = (ids.get("roles") or {}).get("announcements_ping")
    if ping and not role_id:
        raise RuntimeError(
            "The announcements ping role is not configured. "
            "Run `.staff supportupdate` in the support server."
        )

    kwargs = _announcement_options(
        title=title, body=body, footer=footer, ping=ping, role_id=role_id, media=media,
    )
    if media:
        kwargs["files"] = build_broadcast_files(media)
    message = await channel.send(**kwargs)
    jump_url = getattr(message, "jump_url", None)
    return {
        "message_id": message.id,
        "channel_id": int(channel_id),
        "guild_id": SUPPORT_GUILD,
        "pinged_role_id": int(role_id) if ping else None,
        "image_count": len(media),
        "message_url": jump_url,
        "url": jump_url,
    }


async def edit_support_announcement(
    bot,
    *,
    message_id: int,
    title: str,
    body: str,
    footer: str | None = None,
    ping: bool | None = None,
    images: list[dict] | None = None,
) -> dict:
    """Edit a recent Niko announcement in place.

    Omit ``images`` to keep the current attachments and their spoiler flags.
    Pass a list to replace them, including an empty list to remove all images.
    Omit ``ping`` to keep the existing footer role mention.
    """
    message, ids = await _recent_announcement(bot, message_id)
    title, body, footer = _validated_content(title, body, footer)

    role_id = (ids.get("roles") or {}).get("announcements_ping")
    if ping is None:
        ping = _existing_ping(message, role_id)
    if ping and not role_id:
        raise RuntimeError(
            "The announcements ping role is not configured. "
            "Run `.staff supportupdate` in the support server."
        )

    if images is None:
        media = _existing_media(message)
        attachments = list(getattr(message, "attachments", []) or [])
    elif isinstance(images, list):
        media = await _prepare_images(images)
        attachments = build_broadcast_files(media)
    else:
        raise ValueError("Images must be an array.")

    kwargs = _announcement_options(
        title=title, body=body, footer=footer, ping=ping, role_id=role_id, media=media,
    )
    # A Components V2 edit must explicitly clear the legacy content/embed
    # fields. Passing the existing Attachment objects keeps preserved images.
    edited = await message.edit(
        content=None, embed=None, attachments=attachments, **kwargs,
    )
    jump_url = getattr(edited, "jump_url", None) or getattr(message, "jump_url", None)
    return {
        "edited": True,
        "message_id": edited.id,
        "channel_id": int((ids.get("channels") or {}).get("announcements")),
        "guild_id": SUPPORT_GUILD,
        "pinged_role_id": int(role_id) if ping else None,
        "image_count": len(media),
        "message_url": jump_url,
    }


async def delete_support_announcement(bot, *, message_id: int) -> dict:
    """Delete a recent Niko announcement from the announcements channel."""
    message, ids = await _recent_announcement(bot, message_id)
    jump_url = getattr(message, "jump_url", None)
    await message.delete()
    return {
        "deleted": True,
        "message_id": message.id,
        "channel_id": int((ids.get("channels") or {}).get("announcements")),
        "guild_id": SUPPORT_GUILD,
        "message_url": jump_url,
    }
