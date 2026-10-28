"""
on_message event handler — extracted from bot.py.
Handles prefix commands, AI triggers, and blacklist gating.
"""
import os
import re
import asyncio

import discord

from utils.prefix_manager import dynamic_prefix
from utils.blacklist import check_message_blacklist
from utils.abuse_detection import record_request, strike_notice
from utils.ai.config import load_config, MIN_AI_NAME_LENGTH
from utils.ai.reply import generate_reply, split_reply
from utils.ratelimit import reply_limiter
from utils import logging


DEBUG_MODE = os.getenv("DEBUG_MODE", "").lower() in ("true", "1", "yes")

#: One reply at a time per channel: a burst of mentions used to start a reply
#: per mention, all typing at once and answering each other's context.
_channel_locks: dict[int, asyncio.Lock] = {}

#: Process-wide cap on concurrent generations.
_ai_semaphore: asyncio.Semaphore | None = None
AI_MAX_CONCURRENT = 8


def _channel_lock(channel_id: int) -> asyncio.Lock:
    lock = _channel_locks.get(channel_id)
    if lock is None:
        lock = asyncio.Lock()
        _channel_locks[channel_id] = lock
        if len(_channel_locks) > 2048:
            for key, candidate in list(_channel_locks.items()):
                if not candidate.locked():
                    _channel_locks.pop(key, None)
    return lock


def _limiter() -> asyncio.Semaphore:
    global _ai_semaphore
    if _ai_semaphore is None:
        _ai_semaphore = asyncio.Semaphore(AI_MAX_CONCURRENT)
    return _ai_semaphore


def mentions_ai_name(content: str, ai_name: str) -> bool:
    """Whether the message addresses the AI by name.

    Whole-word matching: the old substring check answered "Nikon", "harmoniko"
    and similar. Names shorter than MIN_AI_NAME_LENGTH never trigger, because a
    one-character name would wake the AI on every message in the server.
    """
    name = (ai_name or "").strip()
    if len(name) < MIN_AI_NAME_LENGTH:
        return False
    return re.search(rf"(?<!\w){re.escape(name)}(?!\w)", content, re.IGNORECASE) is not None


def replies_to_bot(bot, msg: discord.Message) -> bool:
    """Whether this message is a Discord reply to one of Niko's messages."""
    reference = getattr(msg, "reference", None)
    if reference is None:
        return False
    resolved = getattr(reference, "resolved", None) or getattr(reference, "cached_message", None)
    author = getattr(resolved, "author", None)
    return bool(author is not None and author.id == getattr(bot.user, "id", None))


async def _collect_context(msg: discord.Message) -> tuple[str | None, str | None]:
    """Recent channel history and the replied-to message, when opted in."""
    replied_content = None
    context_messages = None

    if msg.reference and msg.reference.message_id:
        try:
            ref_msg = (
                msg.reference.cached_message
                or msg.reference.resolved
                or await msg.channel.fetch_message(msg.reference.message_id)
            )
            if ref_msg and ref_msg.content:
                replied_content = f"{ref_msg.author.display_name}: {ref_msg.content[:300]}"
        except Exception:  # noqa: BLE001 - context is best effort
            pass

    try:
        history = []
        async for item in msg.channel.history(limit=6, before=msg):
            if not item.author.bot and item.content:
                history.append(f"{item.author.display_name}: {item.content[:200]}")
            if len(history) >= 5:
                break
        if history:
            context_messages = "\n".join(reversed(history))
    except Exception:  # noqa: BLE001
        pass

    return replied_content, context_messages


async def handle_message(bot, msg: discord.Message):
    if msg.author.bot:
        return

    content = msg.content.lower()
    guild = msg.guild

    # ── 1. Load prefixes for this guild ──────────────────────────────────────
    prefixes = await dynamic_prefix(bot, msg)
    is_ai_command = False
    used_prefix = None

    # ── 2. Detect prefix usage ────────────────────────────────────────────────
    is_command_request = any(content.startswith(p.lower()) for p in prefixes)
    for p in prefixes:
        if content.startswith(p.lower()):
            used_prefix = p
            if await check_message_blacklist(msg):
                return
            if content.startswith(f"{p.lower()}ai "):
                is_ai_command = True
            else:
                abuse = await record_request(msg.author.id, reason="spamming commands")
                if abuse.get("abuse"):
                    await msg.channel.send(strike_notice(abuse))
                    return
                if abuse.get("blacklisted"):
                    await check_message_blacklist(msg)
                    return
                return await bot.process_commands(msg)
            break

    # ── 3. UwU lock transformation ───────────────────────────────────────────
    # Run locked-message handling before AI triggers so a locked user's
    # message is reposted/deleted rather than also generating an AI reply.
    if not is_ai_command:
        uwulock = bot.get_cog("UwULock")
        if uwulock is not None and await uwulock.process_message(msg):
            return

    # ── 4. Detect name / ping / reply / media triggers ───────────────────────
    config = None
    if guild:
        config = await load_config(guild.id)

    multimodal_enabled = bool(
        guild and config and config.get("multimodal_experiment") == "True"
    )
    image_attachments = []
    voice_attachments = []
    if multimodal_enabled:
        for attachment in msg.attachments:
            content_type = (attachment.content_type or "").lower()
            filename = (attachment.filename or "").lower()
            if content_type.startswith("image/"):
                image_attachments.append(attachment)
            elif content_type.startswith("audio/") or filename.endswith(
                (".ogg", ".opus", ".wav", ".mp3", ".m4a", ".webm")
            ):
                voice_attachments.append(attachment)
        if getattr(getattr(msg, "flags", None), "voice", False) and msg.attachments:
            voice_attachments = [msg.attachments[0]]

    ai_name = str((config or {}).get("ai_name") or "Niko").strip() or "Niko"
    called_by_name = mentions_ai_name(content, ai_name)
    called_by_ping = bot.user in msg.mentions
    called_by_reply = replies_to_bot(bot, msg)

    # ── 5. Nothing triggered AI → stop ────────────────────────────────────────
    # Attachments alone never start a conversation — they only carry extra
    # context when the AI was already triggered by name, ping, reply, or command.
    if not (called_by_name or called_by_ping or called_by_reply or is_ai_command):
        return

    if not is_ai_command and is_command_request:
        return

    if await check_message_blacklist(msg):
        return

    abuse = await record_request(
        msg.author.id,
        reason="spamming AI requests",
    )
    if abuse.get("abuse"):
        await msg.channel.send(strike_notice(abuse))
        return
    if abuse.get("blacklisted"):
        await check_message_blacklist(msg)
        return

    # ── 6. Extract user input ─────────────────────────────────────────────────
    if is_ai_command:
        user_input = msg.content[len(f"{used_prefix}ai "):].strip()
    else:
        user_input = msg.content.strip()

    if not user_input:
        user_input = "Someone called your name or pinged you. Respond naturally."

    # ── 7. Collect optional context and multimodal payload ────────────────────
    replied_content = None
    context_messages = None
    ai_actions_enabled = False
    image_urls = [attachment.url for attachment in image_attachments[:3]]
    transcribed_audio = None

    if guild and config:
        if config.get("better_context_experiment") == "True":
            replied_content, context_messages = await _collect_context(msg)
        ai_actions_enabled = config.get("ai_actions_experiment") == "True"

    # Voice messages are downloaded only for the opt-in experiment. A failed
    # transcription never blocks the normal text/image conversation path.
    if voice_attachments:
        try:
            audio = await voice_attachments[0].read()
            from utils.ai.openai_client import transcribe_audio

            transcribed_audio = await transcribe_audio(audio, voice_attachments[0].filename)
        except Exception as exc:  # noqa: BLE001
            logging.warning("AI", f"Voice transcription failed: {exc}")

    # ── 8. Generate AI reply ──────────────────────────────────────────────────
    # One reply per channel at a time, and a bounded number of generations
    # overall: ten people mentioning Niko at once used to start ten requests.
    lock = _channel_lock(msg.channel.id)
    if lock.locked():
        logging.debug("AI", f"Skipping trigger in {msg.channel.id}: a reply is already in flight")
        return

    semaphore = _limiter()
    try:
        await asyncio.wait_for(semaphore.acquire(), timeout=5)
    except asyncio.TimeoutError:
        logging.warning("AI", "Too many concurrent AI requests; skipping a trigger")
        return

    try:
        async with lock:
            async with msg.channel.typing():
                reply = await generate_reply(
                    bot,
                    msg.author.id,
                    guild,
                    user_input,
                    msg.author.display_name,
                    config=config,
                    context_messages=context_messages,
                    replied_content=replied_content,
                    ai_actions_enabled=ai_actions_enabled,
                    image_urls=image_urls,
                    transcribed_audio=transcribed_audio,
                )
    finally:
        semaphore.release()

    # ── 9. Handle sentinel values ─────────────────────────────────────────────
    if reply == "ai_disabled_global":
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="### ⚠️ AI Disabled"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="The AI is currently disabled by the bot owner."),
        ))
        return await msg.channel.send(view=view)

    if reply == "ai_disabled_guild":
        return

    # ── 10. AI error sentinels → CV2 error card ────────────────────────────────
    if isinstance(reply, str) and reply.startswith("ai_error:"):
        from utils.ai.error_views import build_ai_error_view, parse_ai_error

        kind, cooldown = parse_ai_error(reply)
        error_view = build_ai_error_view(kind, cooldown)
        try:
            return await msg.reply(view=error_view, allowed_mentions=discord.AllowedMentions.none())
        except Exception:  # noqa: BLE001
            return await msg.channel.send(view=error_view)

    # ── 11. AI Actions: structured action response ─────────────────────────────
    if isinstance(reply, dict):
        from utils.ai.actions import dispatch_ai_action

        await dispatch_ai_action(bot, msg, reply)
        return

    # ── 12. Plain text reply ───────────────────────────────────────────────────
    if not isinstance(reply, str) or len(reply) < 1:
        reply = "An error occurred... 🥀"
        if DEBUG_MODE:
            logging.error("AIGeneration", "Empty response generated.")

    # Discord caps a message at 2000 characters: a long answer is posted as
    # consecutive messages rather than cut off.
    chunks = split_reply(reply) or ["An error occurred... 🥀"]
    mentions = discord.AllowedMentions.none()
    try:
        await msg.reply(chunks[0], allowed_mentions=mentions)
    except Exception:  # noqa: BLE001
        await msg.channel.send(chunks[0], allowed_mentions=mentions)

    for chunk in chunks[1:]:
        try:
            await reply_limiter.acquire(msg.channel.id)
            await msg.channel.send(chunk, allowed_mentions=mentions)
        except Exception as error:  # noqa: BLE001
            logging.warning("AIGeneration", f"Could not send reply continuation: {error}")
            break
