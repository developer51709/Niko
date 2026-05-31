import os
import re
import json
import requests
import discord
import asyncio
import datetime
import importlib
from discord.ext import commands
from config.emojis import get_emoji
from utils.ai.local import generate_reply_local
from utils.ai.openai_client import generate_reply_openai
from utils.ai.nikoapi import generate_reply_nikoapi
from utils.ai.config import get_ai_config
from utils.ai.prompts import SYSTEM_PROMPT_CAFE, SYSTEM_PROMPT_NORMAL
from utils.prefix_manager import get_prefixes
from utils.blacklist_manager import BlacklistManager
from utils import logging
from events.on_ready import handle_ready
import database

# -----------------------------
# Config
# -----------------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DATABASE_PATH = "data/database.db"

if not os.getenv("DEBUG_MODE"):
    DEBUG_MODE = False
else:
    DEBUG_MODE = os.getenv("DEBUG_MODE")

# AI model (TinyLlama chat GGUF)
MODEL_URL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MODEL_PATH = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MEMORY_FILE = "memory.json"

# AI config
AI_ENABLED = True
# LOCAL, OPENAI, or NIKOAPI
AI_MODE = "OPENAI"
ANSWER_REPLYS = True

# Other config
# CMD_PREFIX = "." # Replaced with dynamic prefixes


# -----------------------------
# Model download
# -----------------------------
def ensure_model():
    if os.path.exists(MODEL_PATH):
        return

    logging.warning("Startup", "Downloading model... this may take a while.")
    try:
        r = requests.get(MODEL_URL, stream=True)
        r.raise_for_status()

        with open(MODEL_PATH, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logging.success("Startup", "Model downloaded successfully.")
    except Exception as e:
        if "401" in str(e):
            logging.error("Startup", "Error 401: Unauthorized. The resource may require authentication.")
        elif "403" in str(e):
            logging.error("Startup", "Error 403: Forbidden. You don't have permission to access this resource.")
        elif "404" in str(e):
            logging.error("Startup", "Error 404: Model not found. Please check the MODEL_URL.")
        else:
            logging.error("Startup", f"Failed to download model: {e}")

# -----------------------------
# Memory handling
# -----------------------------
_memory_data = {
    "users": {},
    "favorability": {},
    "conversations": {}  # short-term conversation memory
}

if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        _memory_data = json.load(f)

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(_memory_data, f, indent=4)

def get_user_memory(user_id: int) -> str:
    return _memory_data.get("users", {}).get(str(user_id), "")

def get_conversation_history(user_id: int, limit: int = 5) -> str:
    history = _memory_data.get("conversations", {}).get(str(user_id), [])
    return "\n".join([f"{h['role']}: {h['content']}" for h in history[-limit:]])

def update_user_memory(user_id: int, message: str, role: str = "User"):
    uid = str(user_id)
    # Update persistent character profile
    prev = _memory_data["users"].get(uid, "")
    _memory_data["users"][uid] = (prev + "\n" + message).strip()

    # Update short-term conversation history
    if "conversations" not in _memory_data:
        _memory_data["conversations"] = {}

    if uid not in _memory_data["conversations"]:
        _memory_data["conversations"][uid] = []

    _memory_data["conversations"][uid].append({"role": role, "content": message})
    # Keep only last 10 exchanges to prevent context bloat
    _memory_data["conversations"][uid] = _memory_data["conversations"][uid][-10:]

    save_memory()

def adjust_favorability(user_id: int, delta: int = 1):
    uid = str(user_id)
    current = _memory_data["favorability"].get(uid, 0)
    _memory_data["favorability"][uid] = current + delta
    save_memory()

def get_favorability(user_id: int) -> int:
    return _memory_data["favorability"].get(str(user_id), 0)

# -----------------------------
# Generate reply
# -----------------------------
def generate_reply(user_id, server, message, username, *,
                   context_messages=None, replied_content=None, ai_actions_enabled=False):
    ai_status = get_ai_config(server.id, "enabled")
    if ai_status == "True":
        if AI_ENABLED:
            personality = get_ai_config(server.id, "personality")
            SYSTEM_PROMPT = SYSTEM_PROMPT_NORMAL if personality == "normal" else SYSTEM_PROMPT_CAFE
            try:
                if AI_MODE == "NIKOAPI":
                    return generate_reply_nikoapi(bot, user_id, server, message, username, SYSTEM_PROMPT)
                if AI_MODE == "OPENAI":
                    return generate_reply_openai(
                        bot, user_id, server, message, username, SYSTEM_PROMPT,
                        context_messages=context_messages,
                        replied_content=replied_content,
                        ai_actions_enabled=ai_actions_enabled,
                    )
                else:
                    return generate_reply_local(bot, user_id, server, message, username, SYSTEM_PROMPT)
            except Exception:
                return "sorry, something went wrong on my end ☕ please try again in a moment~"
        else:
            return "ai_disabled_global"
    else:
        return "ai_disabled_guild"

# -----------------------------
# Get prefix
# -----------------------------
def dynamic_prefix(bot, message):
    if not message.guild:
        return ["."]  # fallback for DMs

    return get_prefixes(message.guild.id)

# -----------------------------
# Blacklist check
# -----------------------------
async def blacklist_check(msg):
    blacklist_manager = BlacklistManager()
    user_entry = blacklist_manager.get_user_entry(msg.author.id)
    if user_entry:
        reason = user_entry.get("reason") or "No reason provided."
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_danger')} Blacklisted"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"You are blacklisted from using this bot.\n**Reason:** {reason}\n\nIf you believe this is a mistake, please open a ticket in the support server."
            ),
            accent_colour=discord.Color.red()
        )
        view.add_item(container)
        await msg.channel.send(view=view)
        return True
    if msg.guild:
        guild_entry = blacklist_manager.get_guild_entry(msg.guild.id)
        if guild_entry:
            reason = guild_entry.get("reason") or "No reason provided."
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_danger')} Blacklisted"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"This server is blacklisted from using this bot.\n**Reason:** {reason}\n\nIf you believe this is a mistake, please open a ticket in the support server."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            await msg.channel.send(view=view)
            return True
    return False

# -----------------------------
# Discord bot
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True
intents.moderation = True

bot = commands.Bot(
    command_prefix=dynamic_prefix,
    intents=intents
)
bot.remove_command("help")
bot.cxn: database.SQLitePool | None = None


# ── Slash-command blacklist check (runs before every slash/context command) ──
@bot.tree.interaction_check
async def _slash_blacklist_check(interaction: discord.Interaction) -> bool:
    bm = BlacklistManager()
    user_entry = bm.get_user_entry(interaction.user.id)
    if user_entry:
        reason = user_entry.get("reason") or "No reason provided."
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_danger')} Blacklisted"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"You are blacklisted from using this bot.\n**Reason:** {reason}\n\nIf you believe this is a mistake, please open a ticket in the support server."),
            accent_colour=discord.Color.red()
        ))
        try:
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception:
            pass
        return False
    if interaction.guild:
        guild_entry = bm.get_guild_entry(interaction.guild.id)
        if guild_entry:
            reason = guild_entry.get("reason") or "No reason provided."
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('icon_danger')} Blacklisted"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=f"This server is blacklisted from using this bot.\n**Reason:** {reason}\n\nIf you believe this is a mistake, please open a ticket in the support server."),
                accent_colour=discord.Color.red()
            ))
            try:
                await interaction.response.send_message(view=view, ephemeral=True)
            except Exception:
                pass
            return False
    return True


@bot.event
async def on_message(msg: discord.Message):
    if msg.author.bot:
        return

    content = msg.content.lower()
    guild = msg.guild

    # -----------------------------
    # 1. Load prefixes for this guild
    # -----------------------------
    prefixes = dynamic_prefix(bot, msg)  # returns list
    is_ai_command = False
    used_prefix = None

    # -----------------------------
    # 2. Detect prefix usage
    # -----------------------------
    for p in prefixes:
        if content.startswith(p.lower()):
            used_prefix = p
            # blacklist check
            bl = await blacklist_check(msg)
            if bl:
                return
            # Check if it's an AI command
            if content.startswith(f"{p.lower()}ai "):
                is_ai_command = True
            else:
                # Normal command → let discord.py handle it
                return await bot.process_commands(msg)
            break

    # -----------------------------
    # 3. Detect name or ping triggers
    # -----------------------------
    called_by_name = "niko" in content

    if ANSWER_REPLYS:
        called_by_ping = bot.user in msg.mentions
    else:
        # Only respond to direct pings, not replies
        called_by_ping = bot.user in msg.mentions and not msg.reference

    # -----------------------------
    # 4. If nothing triggered the AI, stop
    # -----------------------------
    if not (called_by_name or called_by_ping or is_ai_command):
        return

    # -----------------------------
    # 5. Extract user input
    # -----------------------------
    if is_ai_command:
        # Remove ONLY the prefix+ai part
        user_input = msg.content[len(f"{used_prefix}ai "):].strip()
    else:
        user_input = msg.content.strip()

    if not user_input:
        user_input = "Someone called your name or pinged you. Respond naturally."

    # -----------------------------
    # 6. Generate AI reply
    # -----------------------------
    loop = asyncio.get_event_loop()

    # blacklist check
    bl = await blacklist_check(msg)
    if bl:
        return

    # ── Better Context experiment ──────────────────────────────────────
    replied_content = None
    context_messages = None
    ai_actions_enabled = False

    if guild:
        better_ctx = get_ai_config(guild.id, "better_context_experiment") == "True"
        if better_ctx:
            # Grab replied-to message
            if msg.reference and msg.reference.message_id:
                try:
                    ref_msg = msg.reference.cached_message or await msg.channel.fetch_message(msg.reference.message_id)
                    if ref_msg and ref_msg.content:
                        replied_content = f"{ref_msg.author.display_name}: {ref_msg.content[:300]}"
                except Exception:
                    pass
            # Grab last 5 channel messages (excluding the triggering message)
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

    async with msg.channel.typing():
        import functools
        reply = await loop.run_in_executor(
            None,
            functools.partial(
                generate_reply,
                msg.author.id,
                guild,
                user_input,
                msg.author.display_name,
                context_messages=context_messages,
                replied_content=replied_content,
                ai_actions_enabled=ai_actions_enabled,
            )
        )

        if reply == "ai_disabled_global":
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content="### ⚠️ AI Disabled"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content="The AI is currently disabled by the bot owner.")
            ))
            return await msg.channel.send(view=view)

        if reply == "ai_disabled_guild":
            return

        # ── AI Actions: handle structured action responses ─────────────
        if isinstance(reply, dict):
            from utils.ai.actions import dispatch_ai_action
            self = bot
            await dispatch_ai_action(self, msg, reply)
            return

        if not isinstance(reply, str) or len(reply) < 1:
            reply = "An error occured... 🥀"
            if DEBUG_MODE == "True":
                logging.error("AIGeneration", "Error: Empty response generated.")

        if len(reply) > 1800:
            reply = reply[:1800] + "..."

        mentions = discord.AllowedMentions.none()
        try:
            await msg.reply(reply, allowed_mentions=mentions)
        except Exception:
            await msg.channel.send(reply, allowed_mentions=mentions)

# -----------------------------
# AI State Access (for Cogs)
# -----------------------------
def get_favorability_score(user_id: int) -> int:
    return get_favorability(user_id)

def get_memory_content(user_id: int) -> str:
    return get_user_memory(user_id)

# -----------------------------
# Gateway IDENTIFY patcher
# -----------------------------
def patch_identify(device: str):
    """
    Patches discord.py's IDENTIFY payload to spoof the client device.
    device: 'normal', 'mobile_ios', 'mobile_android', 'vr', 'embedded'
    """
    import discord.gateway as gateway

    _DEVICES: dict[str, tuple[dict, dict]] = {
        "mobile_ios": (
            {"os": "iOS", "browser": "Discord iOS", "device": "Discord iOS",
             "system_locale": "en-US", "browser_version": "", "os_version": "",
             "referrer": "", "referring_domain": "",
             "referrer_current": "", "referring_domain_current": "",
             "release_channel": "stable", "client_build_number": 0,
             "native_build_number": None, "client_event_source": None},
            {"capabilities": 30717},
        ),
        "mobile_android": (
            {"os": "Android", "browser": "Discord Android", "device": "Discord Android",
             "system_locale": "en-US", "browser_version": "", "os_version": "",
             "referrer": "", "referring_domain": "",
             "referrer_current": "", "referring_domain_current": "",
             "release_channel": "stable", "client_build_number": 0,
             "native_build_number": None, "client_event_source": None},
            {"capabilities": 30717},
        ),
        "vr": (
            {"os": "Android", "browser": "Quest", "device": "Quest",
             "system_locale": "en-US", "browser_version": "", "os_version": "12",
             "referrer": "", "referring_domain": "",
             "referrer_current": "", "referring_domain_current": "",
             "release_channel": "stable", "client_build_number": 0,
             "native_build_number": None, "client_event_source": None},
            {"capabilities": 125},
        ),
        "embedded": (
            {"os": "Linux", "browser": "Discord Embedded", "device": "",
             "system_locale": "en-US", "browser_version": "", "os_version": "",
             "referrer": "", "referring_domain": "",
             "referrer_current": "", "referring_domain_current": "",
             "release_channel": "stable", "client_build_number": 0,
             "native_build_number": None, "client_event_source": None},
            {"capabilities": 8189},
        ),
        "normal": (
            {"os": "Windows", "browser": "Discord", "device": "",
             "system_locale": "en-US", "browser_version": "", "os_version": "",
             "referrer": "", "referring_domain": "",
             "referrer_current": "", "referring_domain_current": "",
             "release_channel": "stable", "client_build_number": 0,
             "native_build_number": None, "client_event_source": None},
            {"capabilities": 16381},
        ),
    }

    if device not in _DEVICES:
        logging.warning("DeviceSpoof", f"Unknown STATUS_DEVICE '{device}', falling back to 'normal'.")

    target_props, target_extra = _DEVICES.get(device, _DEVICES["normal"])
    logging.info("DeviceSpoof", f"Patching gateway IDENTIFY — device={device!r}, capabilities={target_extra.get('capabilities')}")

    _original_identify = gateway.DiscordWebSocket.identify

    async def identify_spoof(self):
        _orig_send = self.send_as_json

        async def _intercept(data):
            if isinstance(data, dict) and data.get("op") == self.IDENTIFY:
                data["d"]["properties"] = target_props
                data["d"].update(target_extra)
            await _orig_send(data)

        self.send_as_json = _intercept
        try:
            await _original_identify(self)
        finally:
            self.send_as_json = _orig_send

    gateway.DiscordWebSocket.identify = identify_spoof


# -----------------------------
# Run bot
# -----------------------------

@bot.event
async def on_ready():
    await handle_ready(bot)


if __name__ == "__main__":
    if not TOKEN:
        logging.error("Startup", "Error:\nMissing bot Token.\n\nSolution:\nSet DISCORD_BOT_TOKEN in the Environment variables or create a .env file in the project directory.")
        exit(1)
    logging.info("Startup", "Starting bot...")
    # Patch the gateway IDENTIFY method before connecting so Discord receives
    # the spoofed device on the very first handshake (affects visible status).
    device_choice = os.getenv("STATUS_DEVICE", "normal").lower()
    patch_identify(device_choice)
    try:
        bot.run(str(TOKEN), log_handler=None)
    except Exception as e:
        logging.error("Startup", f"Error connecting to Discord: {e}")