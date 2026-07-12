"""
AI reply generation — thin dispatcher that routes to the configured backend.
"""
from utils.ai.local import generate_reply_local
from utils.ai.openai_client import generate_reply_openai
from utils.ai.nikoapi import generate_reply_nikoapi
from utils.ai.config import get_ai_config
from utils.ai.prompts import SYSTEM_PROMPT_CAFE, SYSTEM_PROMPT_NORMAL

AI_ENABLED = True
AI_MODE = "OPENAI"
ANSWER_REPLYS = True


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
):
    """
    Generate an AI reply string.  Runs synchronously (call via run_in_executor
    from async context).  Returns a plain str or a dict for AI Actions.
    """
    guild_id = server.id if server else 0
    ai_status = get_ai_config(guild_id, "enabled")

    if ai_status == "True":
        if not AI_ENABLED:
            return "ai_disabled_global"

        personality = get_ai_config(guild_id, "personality")
        system_prompt = SYSTEM_PROMPT_NORMAL if personality == "normal" else SYSTEM_PROMPT_CAFE
        try:
            if AI_MODE == "NIKOAPI":
                return generate_reply_nikoapi(bot, user_id, server, message, username, system_prompt)
            if AI_MODE == "OPENAI":
                return generate_reply_openai(
                    bot, user_id, server, message, username, system_prompt,
                    context_messages=context_messages,
                    replied_content=replied_content,
                    ai_actions_enabled=ai_actions_enabled,
                )
            return generate_reply_local(bot, user_id, server, message, username, system_prompt)
        except Exception:
            return "sorry, something went wrong on my end ☕ please try again in a moment~"

    return "ai_disabled_guild"
