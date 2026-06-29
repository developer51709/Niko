"""
on_message event handler — extracted from bot.py.
Handles prefix commands, AI triggers, and blacklist gating.
"""
import os
import asyncio
import functools

import discord

from utils.prefix_manager import dynamic_prefix
from utils.blacklist import check_message_blacklist
from utils.ai.config import get_ai_config
from utils.ai.reply import generate_reply, ANSWER_REPLYS
from utils import logging


DEBUG_MODE = os.getenv("DEBUG_MODE", "").lower() in ("true", "1", "yes")


async def handle_message(bot, msg: discord.Message):
    if msg.author.bot:
        return

    content = msg.content.lower()
    guild   = msg.guild

    # ── 1. Load prefixes for this guild ──────────────────────────────────────
    prefixes       = dynamic_prefix(bot, msg)
    is_ai_command  = False
    used_prefix    = None

    # ── 2. Detect prefix usage ────────────────────────────────────────────────
    for p in prefixes:
        if content.startswith(p.lower()):
            used_prefix = p
            if await check_message_blacklist(msg):
                return
            if content.startswith(f"{p.lower()}ai "):
                is_ai_command = True
            else:
                return await bot.process_commands(msg)
            break

    # ── 3. Detect name / ping triggers ────────────────────────────────────────
    called_by_name = "niko" in content

    if ANSWER_REPLYS:
        called_by_ping = bot.user in msg.mentions
    else:
        called_by_ping = bot.user in msg.mentions and not msg.reference

    # ── 4. Nothing triggered AI → stop ────────────────────────────────────────
    if not (called_by_name or called_by_ping or is_ai_command):
        return

    # ── 5. Extract user input ─────────────────────────────────────────────────
    if is_ai_command:
        user_input = msg.content[len(f"{used_prefix}ai "):].strip()
    else:
        user_input = msg.content.strip()

    if not user_input:
        user_input = "Someone called your name or pinged you. Respond naturally."

    # ── 6. Blacklist gate (second check for non-prefix AI triggers) ───────────
    if await check_message_blacklist(msg):
        return

    # ── 7. Collect optional better-context payload ────────────────────────────
    replied_content    = None
    context_messages   = None
    ai_actions_enabled = False

    if guild:
        if get_ai_config(guild.id, "better_context_experiment") == "True":
            if msg.reference and msg.reference.message_id:
                try:
                    ref_msg = (
                        msg.reference.cached_message
                        or await msg.channel.fetch_message(msg.reference.message_id)
                    )
                    if ref_msg and ref_msg.content:
                        replied_content = f"{ref_msg.author.display_name}: {ref_msg.content[:300]}"
                except Exception:
                    pass
            try:
                history = []
                async for m in msg.channel.history(limit=6, before=msg):
                    if not m.author.bot:
                        history.append(f"{m.author.display_name}: {m.content[:200]}")
                    if len(history) >= 5:
                        break
                if history:
                    context_messages = "\n".join(reversed(history))
            except Exception:
                pass

        ai_actions_enabled = get_ai_config(guild.id, "ai_actions_experiment") == "True"

    # ── 8. Generate AI reply ──────────────────────────────────────────────────
    loop = asyncio.get_event_loop()

    async with msg.channel.typing():
        reply = await loop.run_in_executor(
            None,
            functools.partial(
                generate_reply,
                bot,
                msg.author.id,
                guild,
                user_input,
                msg.author.display_name,
                context_messages=context_messages,
                replied_content=replied_content,
                ai_actions_enabled=ai_actions_enabled,
            ),
        )

        # ── 9. Handle sentinel values ─────────────────────────────────────────
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

        # ── 10. AI error sentinels → CV2 error card ────────────────────────────
        if isinstance(reply, str) and reply.startswith("ai_error:"):
            from utils.ai.error_views import build_ai_error_view, parse_ai_error
            kind, cooldown = parse_ai_error(reply)
            error_view = build_ai_error_view(kind, cooldown)
            try:
                return await msg.reply(view=error_view, allowed_mentions=discord.AllowedMentions.none())
            except Exception:
                return await msg.channel.send(view=error_view)

        # ── 11. AI Actions: structured action response ─────────────────────────
        if isinstance(reply, dict):
            from utils.ai.actions import dispatch_ai_action
            await dispatch_ai_action(bot, msg, reply)
            return

        # ── 12. Plain text reply ───────────────────────────────────────────────
        if not isinstance(reply, str) or len(reply) < 1:
            reply = "An error occurred... 🥀"
            if DEBUG_MODE:
                logging.error("AIGeneration", "Empty response generated.")

        if len(reply) > 1800:
            reply = reply[:1800] + "..."

        mentions = discord.AllowedMentions.none()
        try:
            await msg.reply(reply, allowed_mentions=mentions)
        except Exception:
            await msg.channel.send(reply, allowed_mentions=mentions)
