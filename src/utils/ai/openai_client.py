"""Groq chat completions: prompt assembly, actions, retries and budgets.

Every call here is async (`AsyncOpenAI`), so a slow provider response no longer
holds a thread from the shared default executor and no memory/config read blocks
the event loop.
"""
from __future__ import annotations

import asyncio
import datetime
import io
import os
import re
import time

from openai import (
    APIConnectionError,
    APIStatusError,
    AsyncOpenAI,
    NotFoundError,
    RateLimitError,
)

from utils import logging
from utils.ai import memory as ai_memory

client: AsyncOpenAI | None = None

_FALLBACK_REPLIES = [
    "sorry, my mind went blank for a sec ☕ try again in a moment~",
    "hmm, i seem to be a little out of it right now... give me a moment ☕",
    "i didn't quite catch that — my thoughts are a bit fuzzy today 🌿 try again shortly!",
]
_fallback_idx = 0

# Groq exposes an OpenAI-compatible API, so the existing client and tool-call
# pipeline can stay unchanged while requests are routed through Groq.
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-20b"
GROQ_VISION_MODEL = "qwen/qwen3.8-27b"
GROQ_TRANSCRIPTION_MODEL = "whisper-large-v3-turbo"


def _model_setting(name: str, default: str) -> str:
    return os.environ.get(name, default).strip() or default


class AINotConfigured(RuntimeError):
    """The provider key is missing; callers get a clear card, not an apology."""


# ── Request limits ─────────────────────────────────────────────────────────────
#: Provider calls time out instead of holding a coroutine (and the typing
#: indicator) for the SDK's default of several minutes.
_REQUEST_TIMEOUT_SECS = 25.0

#: Groq rejects audio uploads above 25 MB; stay well below that and refuse
#: oversized attachments before reading/uploading them.
_MAX_AUDIO_BYTES = 10 * 1024 * 1024

# ── Rate-limit guard ───────────────────────────────────────────────────────────
# Maps user_id → monotonic timestamp when the cooldown expires.
# When the API returns 429, we stop accepting that user's requests for a while
# to avoid hammering the endpoint and making the rate limit worse.
_rl_cooldown: dict[int, float] = {}
_RL_COOLDOWN_SECS = 30  # seconds to pause per user after a 429
_RL_COOLDOWN_MAX_KEYS = 4096

# ── Per-guild budget ───────────────────────────────────────────────────────────
# One server must not be able to drain the shared key for every other server.
# A rolling hourly window is enough to bound spend without a persistence layer.
_guild_usage: dict[int, tuple[float, int]] = {}
_GUILD_WINDOW_SECS = 3600.0
_GUILD_HOURLY_DEFAULT = 200


def _guild_hourly_limit() -> int:
    return _int_setting("AI_GUILD_HOURLY_REQUESTS", _GUILD_HOURLY_DEFAULT, 1, 100_000)


def _consume_guild_budget(guild_id: int) -> bool:
    """Count one request against the guild's hourly allowance."""
    now = time.monotonic()
    start, used = _guild_usage.get(guild_id, (now, 0))
    if now - start >= _GUILD_WINDOW_SECS:
        start, used = now, 0
    if used >= _guild_hourly_limit():
        _guild_usage[guild_id] = (start, used)
        return False
    _guild_usage[guild_id] = (start, used + 1)
    if len(_guild_usage) > 4096:
        for key, (window_start, _count) in list(_guild_usage.items()):
            if now - window_start >= _GUILD_WINDOW_SECS:
                _guild_usage.pop(key, None)
    return True


def _prune_cooldowns(now: float) -> None:
    if len(_rl_cooldown) <= _RL_COOLDOWN_MAX_KEYS:
        return
    for key, until in list(_rl_cooldown.items()):
        if until <= now:
            _rl_cooldown.pop(key, None)


async def transcribe_audio(audio_bytes: bytes, filename: str = "voice_message.ogg") -> str:
    """Transcribe a Discord voice attachment using the configured AI client."""
    if not audio_bytes:
        return ""
    if len(audio_bytes) > _MAX_AUDIO_BYTES:
        raise ValueError(
            f"Voice message is larger than {_MAX_AUDIO_BYTES // (1024 * 1024)} MB."
        )
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename or "voice_message.ogg"
    result = await _get_client().audio.transcriptions.create(
        model=_model_setting("GROQ_TRANSCRIPTION_MODEL", GROQ_TRANSCRIPTION_MODEL),
        file=audio_file,
    )
    return (getattr(result, "text", "") or "").strip()

# ── Token budget constants ─────────────────────────────────────────────────────
_CONV_HISTORY_TURNS   = 3    # recent turns kept for short-term context
_USER_MEMORY_MAX      = 300  # chars kept from long-term memory string
_CTX_MSG_MAX_PER_LINE = 120  # chars per context-message line
_CTX_MSG_MAX_LINES    = 3    # max channel-history lines passed
_REPLIED_CONTENT_MAX  = 200  # chars for replied-message snippet

# ── Completion budget ─────────────────────────────────────────────────────────
# gpt-oss is a reasoning model and its reasoning tokens are billed against the
# completion budget, so a small cap gets spent on thinking and the visible reply
# is cut off mid-sentence.  Measured against the live API, the previous
# max_tokens=300 ended with finish_reason="length" after ~870 characters of an
# answer that needs ~3,300.  The budget, the reasoning effort, and the
# continuation loop below keep whole answers intact.
_COMPLETION_TOKENS     = 1024   # per request (override: GROQ_MAX_COMPLETION_TOKENS)
_COMPLETION_TOKENS_MIN = 256
_COMPLETION_TOKENS_MAX = 8192
_REASONING_EFFORT      = "low"  # override: GROQ_REASONING_EFFORT (low|medium|high)
_MAX_REPLY_REQUESTS    = 3      # the answer plus up to two continuations
_REQUEST_ATTEMPTS      = 3      # attempts per request on transient failures
_RETRY_BACKOFF_SECS    = 0.6
_CONTINUE_PROMPT = (
    "Continue your previous reply from exactly where it stopped. "
    "Do not repeat anything you already wrote."
)


def _int_setting(name: str, default: int, minimum: int, maximum: int) -> int:
    """Read a positive int from the environment, clamped to a sane range."""
    try:
        value = int(str(os.environ.get(name, "")).strip())
    except (TypeError, ValueError):
        return default
    return max(minimum, min(value, maximum))


def _reasoning_effort() -> str:
    value = os.environ.get("GROQ_REASONING_EFFORT", _REASONING_EFFORT).strip().lower()
    return value if value in {"low", "medium", "high"} else _REASONING_EFFORT


def _get_client() -> AsyncOpenAI:
    global client
    if client is None:
        groq_key = os.environ.get("GROQ_API_KEY", "").strip()
        if not groq_key:
            raise AINotConfigured("GROQ_API_KEY is not set.")

        # max_retries=0 — we handle retries ourselves so the SDK never
        # silently resends a request that already hit a rate limit.
        client = AsyncOpenAI(
            api_key=groq_key,
            base_url=os.environ.get("GROQ_BASE_URL", GROQ_BASE_URL),
            max_retries=0,
            timeout=_REQUEST_TIMEOUT_SECS,
        )
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
                # Required, not optional: an omitted value used to reset the nick.
                "required": ["user", "nickname"],
            },
        },
    },
]


# ── Action-intent keyword sets ─────────────────────────────────────────────────
# Tools are only attached to the API request when the incoming message clearly
# signals a moderation or server-management intent.  This avoids sending ~2,000
# extra tool-definition tokens on every casual chat message.

_ACTION_PHRASES = {
    # moderation verbs
    "ban", "unban", "kick", "mute", "unmute", "timeout", "untimeout",
    "warn", "warning", "strike",
    # message management
    "purge", "clear messages", "delete messages", "bulk delete",
    # channel management
    "create channel", "delete channel", "rename channel",
    "make a channel", "set topic", "channel topic",
    # role management
    "create role", "delete role", "make a role", "assign role",
    "give role", "remove role", "take role", "add role",
    # nickname
    "nickname", "change nick", "set nick", "rename",
    # polls
    "create poll", "make a poll", "start a poll",
}

# Single words that on their own strongly suggest an action request
_ACTION_KEYWORDS = {
    "ban", "unban", "kick", "mute", "unmute", "timeout",
    "untimeout", "warn", "purge", "poll",
}


# Word-boundary matcher: plain substring matching attached all 18 tool schemas
# to innocent messages such as "banana" or "urban" ("ban" is a substring).
_ACTION_RE = re.compile(
    r"\b("
    + "|".join(
        re.escape(phrase)
        for phrase in sorted(_ACTION_PHRASES | _ACTION_KEYWORDS, key=len, reverse=True)
    )
    + r")\b",
    re.IGNORECASE,
)


def _message_requests_action(message: str) -> bool:
    """Return True only if the message looks like an explicit action request.

    Keeps token usage low by skipping tool definitions for casual chat.
    """
    return bool(_ACTION_RE.search(message or ""))


async def _create_completion(*, model: str, messages: list, with_tools: bool = False):
    """Send one chat completion, retrying transient connection/5xx failures.

    Rate limits are re-raised so the caller can apply the per-user cooldown
    instead of hammering the endpoint, and 4xx answers are returned to the
    caller immediately because retrying a deterministic rejection cannot help.
    """
    last_error = None
    for attempt in range(_REQUEST_ATTEMPTS):
        kwargs = {
            "model": model,
            "messages": messages,
            # Current parameter name, with a budget the visible answer fits in.
            "max_completion_tokens": _int_setting(
                "GROQ_MAX_COMPLETION_TOKENS", _COMPLETION_TOKENS,
                _COMPLETION_TOKENS_MIN, _COMPLETION_TOKENS_MAX,
            ),
            "temperature": 0.7,
            "extra_body": {
                "reasoning_effort": _reasoning_effort(),
                "include_reasoning": False,
            },
        }
        if with_tools:
            kwargs["tools"]       = _AI_ACTIONS_TOOLS
            kwargs["tool_choice"] = "auto"
        try:
            return await _get_client().chat.completions.create(**kwargs)
        except RateLimitError:
            raise
        except (APIConnectionError, APIStatusError) as error:
            if isinstance(error, APIStatusError) and error.status_code < 500:
                raise
            last_error = error
            # The connection may be stale after a network hiccup; rebuild it.
            _reset_client()
            if attempt < _REQUEST_ATTEMPTS - 1:
                await asyncio.sleep(min(_RETRY_BACKOFF_SECS * (2 ** attempt), 2.0))
    raise last_error


def _action_payload(tool_call) -> dict:
    """Turn a tool call into the action dict the dispatcher expects."""
    import json

    try:
        arguments = json.loads(tool_call.function.arguments)
    except Exception:
        arguments = {}
    payload = {"action": tool_call.function.name}
    if isinstance(arguments, dict):
        payload.update(arguments)
    return payload


def _is_safety_error(error: Exception) -> bool:
    """Whether a provider 4xx is a content-policy rejection."""
    try:
        body = getattr(error, "body", None) or {}
        err_code = (body.get("error", {}) or {}).get("code", "") if isinstance(body, dict) else ""
        if err_code in {"content_filter", "content_policy_violation", "moderated"}:
            return True
        text = str(error).lower()
        return any(
            key in text
            for key in ("content_filter", "safety", "content_policy", "moderated")
        )
    except Exception:  # noqa: BLE001
        return False


async def generate_reply_openai(
    bot, user_id: int, server, message: str, username: str, SYSTEM_PROMPT: str,
    *,
    guild_id: int = 0,
    ai_name: str = "Niko",
    context_messages: str = None,
    replied_content: str = None,
    ai_actions_enabled: bool = False,
    image_urls: list[str] | None = None,
    transcribed_audio: str | None = None,
):
    server_name  = server.name if server else "DM"
    member_count = len(server.members) if server else 0

    # ── Pull memory for THIS guild — apply size caps to save tokens ────
    memory = await ai_memory.get_context(guild_id, user_id, limit=_CONV_HISTORY_TURNS)
    user_mem = memory.memory[-_USER_MEMORY_MAX:] if memory.memory else ""
    conv_history = memory.history

    # ── Trim context helpers if they arrived oversized ─────────────────
    if replied_content and len(replied_content) > _REPLIED_CONTENT_MAX:
        replied_content = replied_content[:_REPLIED_CONTENT_MAX]

    if context_messages:
        lines = context_messages.splitlines()[:_CTX_MSG_MAX_LINES]
        lines = [ln[:_CTX_MSG_MAX_PER_LINE] for ln in lines]
        context_messages = "\n".join(lines)

    # ── Build a compact user message (system prompt NOT repeated here) ─
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%a %d %b %Y %H:%M")
    user_parts = [
        f"[{timestamp} UTC | {server_name} | {member_count} members]",
        f"User: {username}",
    ]

    if user_mem:
        user_parts.append(f"Memory: {user_mem}")

    if replied_content:
        user_parts.append(f"Replying to: {replied_content}")

    if context_messages:
        user_parts.append(f"Recent chat:\n{context_messages}")

    if conv_history:
        user_parts.append(f"History:\n{conv_history}")

    if transcribed_audio:
        user_parts.append(f"Voice message transcription: {transcribed_audio[:2000]}")

    user_parts.append(f"\n{username}: {message}")

    user_content = "\n".join(user_parts)
    if image_urls:
        user_content = [
            {"type": "text", "text": user_content},
            *({"type": "image_url", "image_url": {"url": url}} for url in image_urls[:3]),
        ]

    global _fallback_idx

    # ── Short-circuit if this user is still in a rate-limit cooldown ──
    now = time.monotonic()
    _prune_cooldowns(now)
    cooldown_until = _rl_cooldown.get(user_id, 0)
    if now < cooldown_until:
        return f"ai_error:rate_limit:{int(cooldown_until - now) + 1}"

    if not _consume_guild_budget(guild_id):
        logging.warning("AI", f"Guild {guild_id} reached its hourly AI request limit")
        return "ai_error:budget"

    model = (
        _model_setting("GROQ_VISION_MODEL", GROQ_VISION_MODEL)
        if image_urls
        else _model_setting("GROQ_MODEL", GROQ_MODEL)
    )
    # Only attach tool definitions when the message actually requests an
    # action.  Sending 18 tool schemas on every casual chat message
    # burns ~2,000 input tokens per request with no benefit.
    wants_action = ai_actions_enabled and _message_requests_action(message)
    conversation = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_content},
    ]
    answers: list[str] = []
    started = time.monotonic()
    finish_reason = None

    try:
        # An answer that runs into the token budget comes back with
        # finish_reason="length".  Ask for the rest of it instead of serving a
        # reply that stops mid-sentence.
        for request_index in range(_MAX_REPLY_REQUESTS):
            response = await _create_completion(
                model=model,
                messages=conversation,
                with_tools=wants_action and request_index == 0,
            )
            choice = response.choices[0]
            finish_reason = choice.finish_reason

            # ── Safety filter: model declined via finish_reason ────────────
            if finish_reason == "content_filter":
                logging.warning("AI", f"Content filter blocked a reply for user {user_id}")
                return "ai_error:safety"

            # ── Handle AI Actions tool call ────────────────────────────────
            tool_calls = getattr(choice.message, "tool_calls", None)
            if wants_action and finish_reason == "tool_calls" and tool_calls:
                if len(tool_calls) > 1:
                    logging.warning(
                        "AI",
                        f"Model requested {len(tool_calls)} actions; running only the first",
                    )
                payload = _action_payload(tool_calls[0])
                logging.info(
                    "AI",
                    f"guild={guild_id} user={user_id} action={payload.get('action')} "
                    f"ms={int((time.monotonic() - started) * 1000)}",
                )
                return payload

            text = (choice.message.content or "").strip()
            if text:
                answers.append(text)

            if finish_reason != "length":
                break
            if text:
                conversation.append({"role": "assistant", "content": text})
                conversation.append({"role": "user", "content": _CONTINUE_PROMPT})

    except AINotConfigured:
        logging.error("AI", "GROQ_API_KEY is not configured — AI replies are disabled")
        return "ai_error:not_configured"

    except RateLimitError as error:
        # 429 — do NOT reset the client (it's fine), do NOT retry.
        # Apply a per-user cooldown so the next call returns immediately
        # instead of hitting the API again and worsening the rate limit.
        retry_after = _RL_COOLDOWN_SECS
        # Honour the Retry-After header if the API returned one
        try:
            header_val = getattr(error.response, "headers", {}).get("retry-after")
            if header_val:
                retry_after = max(int(float(header_val)), retry_after)
        except Exception:  # noqa: BLE001 - header parsing is best effort
            pass
        _rl_cooldown[user_id] = time.monotonic() + retry_after
        logging.warning(
            "AI", f"Rate limited — user {user_id} cooling down for {retry_after}s"
        )
        return f"ai_error:rate_limit:{retry_after}"

    except (NotFoundError, APIConnectionError, APIStatusError) as error:
        if _is_safety_error(error):
            logging.warning("AI", f"Safety filter triggered for user {user_id}")
            return "ai_error:safety"
        _reset_client()
        logging.error("AI", f"Provider error for guild {guild_id}: {error}")
        return "ai_error:generic"

    except asyncio.CancelledError:
        raise

    except Exception as error:  # noqa: BLE001 - one bad reply must not kill the handler
        _reset_client()
        logging.error("AI", f"Unexpected AI error for guild {guild_id}: {error!r}")
        return "ai_error:generic"

    clean = " ".join(answers).strip()
    if not clean:
        # The model returned no text at all.  Reasoning can consume the entire
        # budget (and an empty completion is not an error), so answer with the
        # canned line instead of leaving the user with nothing.
        reply = _FALLBACK_REPLIES[_fallback_idx % len(_FALLBACK_REPLIES)]
        _fallback_idx += 1
        logging.warning("AI", f"Empty completion for user {user_id} — fallback reply")
        return reply

    await ai_memory.record_turn(
        guild_id,
        user_id,
        message,
        clean,
        user_label=username,
        assistant_label=ai_name,
    )
    logging.info(
        "AI",
        f"guild={guild_id} user={user_id} model={model} finish={finish_reason} "
        f"chars={len(clean)} ms={int((time.monotonic() - started) * 1000)}",
    )
    return clean

