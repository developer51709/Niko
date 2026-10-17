"""
NSFW Image Filter — bot-side client for the externally hosted
Cloudflare Workers AI API (see nsfw-api/README.md).

The API base URL comes from the ``NSFW_API_URL`` environment variable;
an optional ``NSFW_API_TOKEN`` is sent as a Bearer token when set.
"""

import asyncio
import base64
import os

import aiohttp
import discord

import utils.logging as logging

log = logging

# Attachment content types we're willing to check.
SUPPORTED_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"}
SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".gif")

# Max attachment size we'll download (10 MB) and max images per message.
MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024
MAX_IMAGES_PER_MESSAGE = 2

# Local request timeout so a slow API never stalls on_message handling.
REQUEST_TIMEOUT_SECONDS = 12


def get_api_url() -> str:
    """Base URL of the NSFW API, without a trailing slash (or '' if unset)."""
    return (os.getenv("NSFW_API_URL") or "").strip().rstrip("/")


def get_api_token() -> str:
    """Optional bearer token for the NSFW API ('' when unset)."""
    return (os.getenv("NSFW_API_TOKEN") or "").strip()


def api_configured() -> bool:
    """True when NSFW_API_URL is set — otherwise the filter fails open."""
    return bool(get_api_url())


def _pick_attachments(message: discord.Message):
    """Select up to MAX_IMAGES_PER_MESSAGE supported image attachments."""
    picked = []
    for att in message.attachments:
        ctype = (att.content_type or "").split(";")[0].strip().lower()
        looks_like_image = ctype in SUPPORTED_TYPES or (
            not ctype and att.filename.lower().endswith(SUPPORTED_EXTENSIONS)
        )
        if looks_like_image and att.size <= MAX_ATTACHMENT_BYTES:
            picked.append(att)
        if len(picked) >= MAX_IMAGES_PER_MESSAGE:
            break
    return picked


async def check_message_images(message: discord.Message):
    """
    Check a message's image attachments against the NSFW API.

    Returns (hit, score, filename):
      hit      — True when at least one image is classified NSFW
      score    — confidence of the offending verdict (0.0 when no hit)
      filename — name of the offending attachment (or None)

    Fail-open: any error (missing env var, network, API error) returns
    (False, 0.0, None) so the message is never blocked by an outage.
    """
    url = get_api_url()
    if not url:
        return (False, 0.0, None)

    attachments = _pick_attachments(message)
    if not attachments:
        return (False, 0.0, None)

    headers = {"Content-Type": "application/json"}
    token = get_api_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for att in attachments:
                data = await att.read()
                payload = {"image": base64.b64encode(data).decode("ascii")}
                try:
                    async with session.post(
                        f"{url}/check", json=payload, headers=headers
                    ) as resp:
                        if resp.status != 200:
                            log.warning(
                                "NSFW API returned HTTP %s for %s",
                                resp.status, att.filename,
                            )
                            continue
                        result = await resp.json()
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    log.warning("NSFW API request failed: %s", e)
                    continue

                if result.get("nsfw"):
                    return (True, float(result.get("score", 1.0)), att.filename)
    except Exception as e:  # never break message handling on filter errors
        log.warning("NSFW filter error (failing open): %s", e)

    return (False, 0.0, None)
