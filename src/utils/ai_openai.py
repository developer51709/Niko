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

_USER_ARG = {
    "type": "string",
    "description": (
        "The target user. Prefer a numeric Discord user ID. A raw mention "
        "like <@123> or a plain username are also accepted."
    ),
}
_CHANNEL_ARG = {
    "type": "string",
    "description": (
        "The target channel. Prefer a numeric channel ID. A channel "
        "mention like <#123> or a plain channel name are also accepted."
    ),
}
_ROLE_ARG = {
    "type": "string",
    "description": (
        "The target role. Prefer a numeric role ID. A role mention like "
        "<@&123> or a plain role name are also accepted."
    ),
}
_REASON_ARG = {
    "type": "string",
    "description": "Short audit-log reason. Defaults to 'No reason provided'.",
}


_AI_ACTIONS_TOOLS = [
    # ── Non-destructive ────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "create_poll",
            "description": "Create a poll in the current channel when the user asks for one.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The poll question."},
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of 2–9 answer options.",
                        "minItems": 2,
                        "maxItems": 9,
                    },
                },
                "required": ["question", "options"],
            },
        },
    },

    # ── Moderation ─────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "kick_member",
            "description": "Kick a member from the server. Requires Kick Members permission.",
            "parameters": {
                "type": "object",
                "properties": {"user": _USER_ARG, "reason": _REASON_ARG},
                "required": ["user"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ban_member",
            "description": "Ban a user from the server. Requires Ban Members permission.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user": _USER_ARG,
                    "reason": _REASON_ARG,
                    "delete_message_days": {
                        "type": "integer",
                        "description": "Days of recent messages to delete (0–7). Defaults to 0.",
                        "minimum": 0,
                        "maximum": 7,
                    },
                },
                "required": ["user"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "unban_user",
            "description": "Unban a user. Provide their numeric user ID. Requires Ban Members.",
            "parameters": {
                "type": "object",
                "properties": {"user": _USER_ARG, "reason": _REASON_ARG},
                "required": ["user"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "timeout_member",
            "description": "Time-out (mute) a member for a duration in seconds. Requires Moderate Members.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user": _USER_ARG,
                    "duration_seconds": {
                        "type": "integer",
                        "description": "Duration in seconds (1 to 2,419,200 = 28 days).",
                        "minimum": 1,
                        "maximum": 2419200,
                    },
                    "reason": _REASON_ARG,
                },
                "required": ["user", "duration_seconds"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_timeout",
            "description": "Remove an active time-out from a member. Requires Moderate Members.",
            "parameters": {
                "type": "object",
                "properties": {"user": _USER_ARG},
                "required": ["user"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "warn_member",
            "description": "Add a warning to a member's record. Requires Moderate Members.",
            "parameters": {
                "type": "object",
                "properties": {"user": _USER_ARG, "reason": _REASON_ARG},
                "required": ["user", "reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "purge_messages",
            "description": "Bulk-delete the most recent N messages (1–100) in a channel. Requires Manage Messages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "integer", "minimum": 1, "maximum": 100},
                    "channel": _CHANNEL_ARG,
                },
                "required": ["amount"],
            },
        },
    },

    # ── Server management ──────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "create_channel",
            "description": "Create a new text or voice channel. Requires Manage Channels.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Channel name (lowercase, dashes preferred)."},
                    "type": {"type": "string", "enum": ["text", "voice"], "description": "Channel type."},
                    "topic": {"type": "string", "description": "Optional topic for text channels."},
                    "category": {"type": "string", "description": "Optional category ID or name to create the channel in."},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_channel",
            "description": "Delete a channel. Requires Manage Channels.",
            "parameters": {
                "type": "object",
                "properties": {"channel": _CHANNEL_ARG},
                "required": ["channel"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rename_channel",
            "description": "Rename a channel. Requires Manage Channels.",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": _CHANNEL_ARG,
                    "name": {"type": "string", "description": "New channel name."},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_channel_topic",
            "description": "Set the topic of a text channel. Requires Manage Channels.",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": _CHANNEL_ARG,
                    "topic": {"type": "string", "description": "New topic (max 1024 chars). Empty string clears it."},
                },
                "required": ["topic"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_role",
            "description": "Create a new role. Requires Manage Roles.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Role name."},
                    "colour": {"type": "string", "description": "Optional hex colour like #ff8800."},
                    "hoist": {"type": "boolean", "description": "Display members with this role separately."},
                    "mentionable": {"type": "boolean", "description": "Allow @-mentioning the role."},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_role",
            "description": "Delete a role. Requires Manage Roles.",
            "parameters": {
                "type": "object",
                "properties": {"role": _ROLE_ARG},
                "required": ["role"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "assign_role",
            "description": "Give a role to a member. Requires Manage Roles.",
            "parameters": {
                "type": "object",
                "properties": {"user": _USER_ARG, "role": _ROLE_ARG},
                "required": ["user", "role"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_role",
            "description": "Remove a role from a member. Requires Manage Roles.",
            "parameters": {
                "type": "object",
                "properties": {"user": _USER_ARG, "role": _ROLE_ARG},
                "required": ["user", "role"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "change_nickname",
            "description": "Change a member's nickname. Empty string resets to their username. Requires Manage Nicknames.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user": _USER_ARG,
                    "nickname": {"type": "string", "description": "New nickname (max 32 chars). Empty string resets."},
                },
                "required": ["user"],
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

        # Return a generic action dict — the bot dispatches it through
        # ai_actions.dispatch_ai_action which handles permission checks
        # and CV2 confirmations for every supported action.
        action_payload = {"action": fn_name}
        if isinstance(fn_args, dict):
            action_payload.update(fn_args)
        return action_payload

    clean = (choice.message.content or "").strip()

    update_user_memory(user_id, message, role=username)
    update_user_memory(user_id, clean, role="Niko")
    adjust_favorability(user_id, delta=1)

    return clean
