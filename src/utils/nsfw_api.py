"""
NSFW Image Filter — fal.ai client.

Models: https://fal.ai/models/fal-ai/imageutils/nsfw

Only guilds with an active premium subscription run this filter (see
``utils.premium``); AutoMod checks the entitlement before calling in, so a
free guild never spends the API credits.

The key comes from ``FAL_KEY`` (``FAL_API_KEY`` is accepted as an alias). The
module fails open: a missing key, a slow request, or a provider error returns
"no verdict" so a message is never blocked by an outage.
"""

import asyncio
import os

import aiohttp
import discord

import utils.logging as logging

log = logging

# Attachment content types we're willing to check.
SUPPORTED_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"}
SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".gif")

# Max attachment size we'll classify (10 MB) and max images per message.
MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024
MAX_IMAGES_PER_MESSAGE = 2

# Local request timeout so a slow model never stalls on_message handling.
REQUEST_TIMEOUT_SECONDS = 12

DEFAULT_MODEL_URL = "https://fal.run/fal-ai/imageutils/nsfw"
DEFAULT_THRESHOLD = 0.85


def get_api_key() -> str:
    """fal.ai key ('' when unset)."""
    return (os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY") or "").strip()


def get_model_url() -> str:
    """Sync inference URL for the NSFW model."""
    return (os.getenv("FAL_NSFW_URL") or DEFAULT_MODEL_URL).strip()


def get_threshold() -> float:
    """Score at or above which an image is treated as NSFW."""
    try:
        value = float(os.getenv("NSFW_THRESHOLD", DEFAULT_THRESHOLD))
    except (TypeError, ValueError):
        return DEFAULT_THRESHOLD
    return min(1.0, max(0.0, value))


def api_configured() -> bool:
    """True when a fal.ai key is set — otherwise the filter fails open."""
    return bool(get_api_key())


def score_from_payload(payload) -> float | None:
    """Read the NSFW confidence out of a fal.ai response.

    The hosted model returns ``{"nsfw_probability": 0.97}``; the older
    ``nsfw_score`` alias and boolean forms are accepted too, so a model swap
    does not silently disable filtering.
    """
    if not isinstance(payload, dict):
        return None
    for key in ("nsfw_probability", "nsfw_score", "score", "nsfw", "NSFW"):
        if key not in payload:
            continue
        value = payload[key]
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        try:
            return min(1.0, max(0.0, float(value)))
        except (TypeError, ValueError):
            continue
    return None


def _is_hit(score: float | None, threshold: float | None = None) -> bool:
    if score is None:
        return False
    return score >= (get_threshold() if threshold is None else threshold)


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


async def classify_image(session: aiohttp.ClientSession, image_url: str, key: str | None = None) -> float | None:
    """Score one image URL with fal.ai, returning None when no verdict exists."""
    api_key = key or get_api_key()
    if not api_key or not image_url:
        return None
    try:
        async with session.post(
            get_model_url(),
            json={"image_url": image_url},
            headers={"Authorization": f"Key {api_key}"},
        ) as resp:
            if resp.status != 200:
                log.warning("fal.ai NSFW returned HTTP %s", resp.status)
                return None
            payload = await resp.json(content_type=None)
    except (aiohttp.ClientError, asyncio.TimeoutError) as error:
        log.warning("fal.ai NSFW request failed: %s", error)
        return None
    return score_from_payload(payload)


async def check_message_images(message: discord.Message):
    """
    Check a message's image attachments with fal.ai.

    Returns (hit, score, filename):
      hit      — True when at least one image is classified NSFW
      score    — confidence of the offending verdict (0.0 when no hit)
      filename — name of the offending attachment (or None)

    Discord attachments are passed to the model by URL, so the image bytes are
    never copied through this process. Fail-open on every error path.
    """
    if not api_configured():
        return (False, 0.0, None)

    attachments = _pick_attachments(message)
    if not attachments:
        return (False, 0.0, None)

    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for att in attachments:
                url = getattr(att, "url", None)
                if not url:
                    continue
                score = await classify_image(session, str(url))
                if _is_hit(score):
                    return (True, float(score or 1.0), att.filename)
    except Exception as error:  # never break message handling on filter errors
        log.warning("NSFW filter error (failing open): %s", error)

    return (False, 0.0, None)
