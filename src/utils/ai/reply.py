"""
AI reply generation — thin dispatcher that routes to the configured backend.
"""
from utils.ai.local import generate_reply_local
from utils.ai.openai_client import generate_reply_openai
from utils.ai.nikoapi import generate_reply_nikoapi
from utils.ai.config import get_ai_config
from utils.ai.prompts import SYSTEM_PROMPT_CAFE, SYSTEM_PROMPT_NORMAL

AI_ENABLED = True
AI_MODE = "GROQ"
ANSWER_REPLYS = True

# Discord refuses a message over 2000 characters. Replies longer than that are
# sent as consecutive messages instead of being truncated mid-sentence.
DISCORD_MESSAGE_LIMIT = 2000
REPLY_CHUNK_LIMIT = 1900


def split_reply(text: str, limit: int = REPLY_CHUNK_LIMIT) -> list[str]:
    """Split an AI reply into chunks Discord will accept.

    Chunks break on a paragraph, then a line, then a sentence, then a word
    boundary so markdown blocks and words stay intact; only a single
    uninterrupted run longer than ``limit`` is split hard.
    """
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= limit:
        return [text]

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


def generate_reply(
    bot,
    user_id,
    server,
    message,
    username,
    *,
    context_messages=None,
    replied_content=None,
    ai_actions_enabled=False,
    image_urls=None,
    transcribed_audio=None,
):
    """
    Generate an AI reply string.  Runs synchronously (call via run_in_executor
    from async context).  Returns a plain str or a dict for AI Actions.
    """
    guild_id = server.id if server else 0
    ai_status = get_ai_config(guild_id, "enabled")
    ai_name = str(get_ai_config(guild_id, "ai_name") or "Niko").strip() or "Niko"

    if ai_status == "True":
        if not AI_ENABLED:
            return "ai_disabled_global"

        personality = get_ai_config(guild_id, "personality")
        system_prompt = SYSTEM_PROMPT_NORMAL if personality == "normal" else SYSTEM_PROMPT_CAFE
        system_prompt += f"\n\nYour configured name in this server is {ai_name}. Respond as {ai_name} and recognize that name when addressed."
        try:
            if AI_MODE == "NIKOAPI":
                return generate_reply_nikoapi(bot, user_id, server, message, username, system_prompt)
            if AI_MODE in {"GROQ", "OPENAI"}:
                return generate_reply_openai(
                    bot, user_id, server, message, username, system_prompt,
                    context_messages=context_messages,
                    replied_content=replied_content,
                    ai_actions_enabled=ai_actions_enabled,
                    image_urls=image_urls,
                    transcribed_audio=transcribed_audio,
                )
            return generate_reply_local(bot, user_id, server, message, username, system_prompt)
        except Exception:
            return "sorry, something went wrong on my end ☕ please try again in a moment~"

    return "ai_disabled_guild"
