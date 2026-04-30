# utils/ai_openai.py
import datetime
from openai import OpenAI, NotFoundError, APIConnectionError, APIStatusError
import os
from utils.memory import (
    get_user_memory,
    get_conversation_history,
    get_favorability,
    update_user_memory,
    adjust_favorability
)

client = None

_FALLBACK_REPLIES = [
    "sorry, my mind went blank for a sec ☕ try again in a moment~",
    "hmm, i seem to be a little out of it right now... give me a moment ☕",
    "i didn't quite catch that — my thoughts are a bit fuzzy today 🌿 try again shortly!",
]
_fallback_idx = 0


def _get_client():
    global client
    if client is None:
        # Prefer a direct OpenAI API key when set; fall back to the Replit
        # AI integration proxy (AI_INTEGRATIONS_OPENAI_*) otherwise.
        direct_key = os.environ.get("OPENAI_API_KEY")
        integration_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
        integration_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")

        if direct_key:
            client = OpenAI(api_key=direct_key)
        elif integration_key and integration_url:
            client = OpenAI(api_key=integration_key, base_url=integration_url)
        else:
            client = OpenAI(api_key=integration_key)
    return client


def _reset_client():
    global client
    client = None

_AI_ACTIONS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_poll",
            "description": (
                "Create a poll in the current Discord channel. "
                "Call this when the user asks you to make a poll, vote, or survey."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The poll question to display."
                    },
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of 2–9 answer options for the poll.",
                        "minItems": 2,
                        "maxItems": 9,
                    },
                },
                "required": ["question", "options"],
            },
        },
    },
]


def generate_reply_openai(
    bot, user_id: int, server, message: str, username: str, SYSTEM_PROMPT: str,
    *,
    context_messages: str = None,
    replied_content: str = None,
    ai_actions_enabled: bool = False,
):
    import json as _json

    member_count = len(bot.users)
    server_name = server.name

    user_mem = get_user_memory(user_id)
    conv_history = get_conversation_history(user_id)
    favor = get_favorability(user_id)

    if favor > 15:
        fav_label = f"{username} is one of your absolute favorites on this server."
    elif favor > 8:
        fav_label = f"You like {username} a lot and consider them top-tier."
    elif favor > 3:
        fav_label = f"You have a good impression of {username}."
    elif favor > 0:
        fav_label = f"You are warming up to {username}."
    else:
        fav_label = f"You don't know {username} very well yet."

    # ── Build prompt ───────────────────────────────────────────────────
    prompt_parts = [
        SYSTEM_PROMPT,
        f"\nUser: {username}",
        f"Impression: {fav_label}",
        f"Server: {server_name}",
        f"Members: {member_count}",
        f"Time: {datetime.datetime.utcnow().strftime('%A, %B %d, %Y, %I:%M %p')} UTC",
    ]

    if replied_content:
        prompt_parts.append(f"\nThis message is a reply to:\n{replied_content}")

    if context_messages:
        prompt_parts.append(f"\nRecent channel messages (oldest → newest):\n{context_messages}")

    if conv_history:
        prompt_parts.append(f"\nYour conversation history with {username}:\n{conv_history}")

    prompt_parts.append(f"\nCurrent message from {username}:\n{message}")

    prompt = "\n".join(prompt_parts)

    global _fallback_idx
    try:
        create_kwargs = dict(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        if ai_actions_enabled:
            create_kwargs["tools"] = _AI_ACTIONS_TOOLS
            create_kwargs["tool_choice"] = "auto"

        response = _get_client().chat.completions.create(**create_kwargs)
    except (NotFoundError, APIConnectionError, APIStatusError) as e:
        _reset_client()
        print(f"OpenAI API error: {e}")
        reply = _FALLBACK_REPLIES[_fallback_idx % len(_FALLBACK_REPLIES)]
        _fallback_idx += 1
        return reply
    except Exception as e:
        _reset_client()
        print(f"Unexpected OpenAI error: {e}")
        reply = _FALLBACK_REPLIES[_fallback_idx % len(_FALLBACK_REPLIES)]
        _fallback_idx += 1
        return reply

    choice = response.choices[0]

    # ── Handle AI Actions tool call ────────────────────────────────────
    if ai_actions_enabled and choice.finish_reason == "tool_calls" and choice.message.tool_calls:
        tool_call = choice.message.tool_calls[0]
        fn_name = tool_call.function.name
        try:
            fn_args = _json.loads(tool_call.function.arguments)
        except Exception:
            fn_args = {}

        if fn_name == "create_poll":
            return {
                "action": "create_poll",
                "question": fn_args.get("question", "Poll"),
                "options": fn_args.get("options", []),
            }

    clean = (choice.message.content or "").strip()

    update_user_memory(user_id, message, role=username)
    update_user_memory(user_id, clean, role="Niko")
    adjust_favorability(user_id, delta=1)

    return clean
