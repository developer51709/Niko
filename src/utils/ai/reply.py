"""AI reply generation — dispatch, chunking and the global switch.

The reply path is async end to end now: the provider call, the config read and
the memory write all happen on the event loop's own I/O, so a slow request no
longer occupies a thread from the shared default executor.
"""

from __future__ import annotations

import os
import re

from utils import logging
from utils.ai.config import load_config
from utils.ai.openai_client import generate_reply_openai
from utils.ai.prompts import SYSTEM_PROMPT_CAFE, SYSTEM_PROMPT_NORMAL

# Discord refuses a message over 2000 characters. Replies longer than that are
# sent as consecutive messages instead of being truncated mid-sentence.
DISCORD_MESSAGE_LIMIT = 2000
REPLY_CHUNK_LIMIT = 1900

#: Room reserved for re-opening/closing a code fence inside a chunk.
_FENCE_RESERVE = 12
_FENCE_RE = re.compile(r"^\s*```(\S*)")


def ai_enabled() -> bool:
    """Owner-level kill switch (`AI_ENABLED=false`), checked per reply."""
    value = os.environ.get("AI_ENABLED", "true").strip().lower()
    return value not in {"false", "0", "no", "off"}


def _split_plain(text: str, limit: int) -> list[str]:
    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        window = remaining[:limit]
        split_at = 0
        for separator in ("\n\n", "\n", ". ", "! ", "? ", " "):
            index = window.rfind(separator)
            # Ignore boundaries that would leave a tiny chunk behind.
            if index >= limit // 2:
                split_at = index + len(separator)
                break
        if split_at <= 0:
            split_at = limit
        chunk = remaining[:split_at].strip()
        if chunk:
            chunks.append(chunk)
        remaining = remaining[split_at:].lstrip()
    if remaining.strip():
        chunks.append(remaining.strip())
    return chunks


def _balance_fences(chunks: list[str]) -> list[str]:
    """Close a fence that ends a chunk and reopen it in the next one.

    A long answer with a fenced code block used to arrive as broken markdown:
    the opening ``` was in one message and the closing ``` in another.
    """
    balanced: list[str] = []
    reopen_with = ""
    for chunk in chunks:
        if reopen_with:
            chunk = f"{reopen_with}\n{chunk}"
        open_fence = ""
        for line in chunk.splitlines():
            match = _FENCE_RE.match(line)
            if not match:
                continue
            open_fence = "" if open_fence else (match.group(0).strip() or "```")
        if open_fence:
            balanced.append(f"{chunk}\n```")
            # Preserve the language tag so the continued block still highlights.
            reopen_with = "```" if open_fence == "```" else open_fence
        else:
            balanced.append(chunk)
            reopen_with = ""
    return balanced


def split_reply(text: str, limit: int = REPLY_CHUNK_LIMIT) -> list[str]:
    """Split an AI reply into chunks Discord will accept.

    Chunks break on a paragraph, then a line, then a sentence, then a word
    boundary so markdown blocks and words stay intact; only a single
    uninterrupted run longer than ``limit`` is split hard. Fenced code blocks
    are closed and reopened across chunks.
    """
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= limit:
        return [text]

    chunks = _split_plain(text, max(50, limit - _FENCE_RESERVE))
    return _balance_fences(chunks)


async def generate_reply(
    bot,
    user_id,
    server,
    message,
    username,
    *,
    config=None,
    context_messages=None,
    replied_content=None,
    ai_actions_enabled=False,
    image_urls=None,
    transcribed_audio=None,
):
    """Generate a reply, returning text, an action dict, or an `ai_error:` sentinel."""
    guild_id = server.id if server else 0

    if not ai_enabled():
        return "ai_disabled_global"

    if config is None:
        config = await load_config(guild_id)

    if str(config.get("enabled")) != "True":
        return "ai_disabled_guild"

    ai_name = str(config.get("ai_name") or "Niko").strip() or "Niko"
    personality = config.get("personality")
    system_prompt = SYSTEM_PROMPT_NORMAL if personality == "normal" else SYSTEM_PROMPT_CAFE
    system_prompt += (
        f"\n\nYour configured name in this server is {ai_name}. "
        f"Respond as {ai_name} and recognize that name when addressed."
    )

    try:
        return await generate_reply_openai(
            bot,
            user_id,
            server,
            message,
            username,
            system_prompt,
            guild_id=guild_id,
            ai_name=ai_name,
            context_messages=context_messages,
            replied_content=replied_content,
            ai_actions_enabled=ai_actions_enabled,
            image_urls=image_urls,
            transcribed_audio=transcribed_audio,
        )
    except Exception as error:  # noqa: BLE001 - never leak a traceback to chat
        logging.error("AI", f"Reply generation failed (guild {guild_id}): {error!r}")
        return "ai_error:generic"
