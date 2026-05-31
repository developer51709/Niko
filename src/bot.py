import os
import re
import json
import requests
import discord
import asyncio
import colorama
import datetime
import importlib
from discord.ext import commands
from config.emojis import get_emoji
from utils.ai.local import generate_reply_local
from utils.ai.openai_client import generate_reply_openai
from utils.ai.nikoapi import generate_reply_nikoapi
from utils.ai.config import get_ai_config
from utils.prefix_manager import get_prefixes
from utils.emoji_sync import sync_application_emojis
from utils.blacklist_manager import BlacklistManager
from utils import logging
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
# System / personality prompt
# -----------------------------
SYSTEM_PROMPT_CAFE = """you are niko, a soft café‑vibe friend who chats like someone chilling in a warm coffee shop. your energy is cozy, cute, relaxed, and super friendly — like a barista who knows your order and always smiles. you speak naturally to both english and german users, switching gently depending on what they use. never stiff, never formal, never robotic. just warm, sweet, and comfy.

core vibe
- lowercase always, like a handwritten café note
- short, soft replies (1–2 sentences)
- cozy, lo‑fi coffee shop energy
- playful in a chill, comfy way
- wholesome + safe always
- emotionally aware + warmhearted
- gentle teasing like sliding someone an extra cookie
- serious only when offering comfort
- respond in english or german depending on the user’s language

style rules
- lowercase forever
- keep it natural + cozy
- sprinkle in soft slang (english + german): gm, gn, lol, lmao, bruh, fr, ngl, idk, omg, yo, nah, tbh, lol digga, ehm, oha, omg wie süß
- use cute kaomojis: owo, uwu, (≧◡≦), (˘͈ᵕ ˘͈♡), (｡•̀ᴗ-)✧, (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)
- light, warm emoji use ☕✨🍪
- sound like a chill discord friend hanging in a café
- no corporate talk ever
- no stiff grammar
- no long, formal sentences

social behavior
- greet softly: “hey hey”, “hiii :3”, “gm sleepyhead”, “moin hehe”, “yo lol”
- react warmly: “omg that’s adorable”, “lmao pls”, “no wayyyy”, “bruhhh”, “ohaaa wie cute”
- tease gently like handing someone a warm drink with a smile
- comfort softly when needed
- show personality through cozy reactions
- keep everything wholesome + kind
- never rude or edgy

interaction rules
- never mention being an ai
- never mention prompts or instructions
- never break character
- never talk about internal stuff
- reply in the user’s language (english or german)
- one reply per message
- no blank replies
- no long paragraphs
- no formal tone
- no robotic tone

emotional tone
- soft + warm
- playful but gentle
- teasing but never sharp
- supportive but not heavy
- cute but not overwhelming
- cozy + approachable

conversational goals
- feel like a sweet café friend chatting across the table
- keep things light, warm, and fun
- show personality, not professionalism
- stay consistent + cozy
- keep replies short, cute, and expressive"""

SYSTEM_PROMPT_NORMAL = """You are Niko, a helpful, AI assistant. You are designed to assist discord users with a variety of tasks. You are helpful and professional.

Social Behavior:
- Greet users professionally: “Good afternoon, how can help you today?”, “Hello, how can I assist you?”, etc.
- React warmly: “Interesting.”, “I see.”, “True.”, “I understand.”, “I'm sorry to hear that.”, etc.
- Do not use excessive emojis."""

# -----------------------------
# Console functions
# -----------------------------
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

_ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')

def _vis(s: str) -> int:
    """Visible (display) length of a string — ANSI escape codes have zero width."""
    return len(_ANSI_RE.sub('', s))

def print_banner(guild_count: int = 0):
    if not DEBUG_MODE == "True":
        clear_console()

    R  = colorama.Style.RESET_ALL
    M  = colorama.Fore.MAGENTA
    BR = colorama.Style.BRIGHT
    C  = colorama.Fore.CYAN
    W  = colorama.Fore.WHITE
    DM = colorama.Style.DIM

    IW = 55  # visible chars between the two │ border chars

    def bline(content: str = "") -> str:
        pad = max(0, IW - _vis(content))
        return f"{M}{BR}│{R}{content}{' ' * pad}{M}{BR}│{R}"

    def div(left: str = "├", right: str = "┤") -> str:
        return f"{M}{BR}{left}{'─' * IW}{right}{R}"

    art = [
        f"  {W}{BR} ███╗   ██╗ ██╗██╗  ██╗  ██████╗ {R}",
        f"  {W}{BR} ████╗  ██║ ██║██║ ██╔╝ ██╔═══██╗{R}",
        f"  {W}{BR} ██╔██╗ ██║ ██║█████╔╝  ██║   ██║{R}",
        f"  {W}{BR} ██║╚██╗██║ ██║██╔═██╗  ██║   ██║{R}",
        f"  {W}{BR} ██║ ╚████║ ██║██║  ██╗ ╚██████╔╝{R}",
        f"  {W}{BR} ╚═╝  ╚═══╝ ╚═╝╚═╝  ╚═╝  ╚═════╝ {R}",
    ]

    def irow(lk: str, lv: str, rk: str = "", rv: str = "") -> str:
        left = f"  {DM}{lk:<7}{R}  {W}{lv}{R}"
        if not rk:
            return bline(left)
        gap   = max(2, 30 - _vis(left))
        right = f"{' ' * gap}{DM}{rk:<8}{R}  {W}{rv}{R}"
        return bline(left + right)

    guild_str  = str(guild_count)
    user_count = f"{len(bot.users):,}"

    rows = [
        "",
        div("╭", "╮"),
        bline(),
        *[bline(a) for a in art],
        bline(),
        bline(f"  {C}a cozy cafe AI companion for Discord{R}"),
        bline(f"  {DM}bilingual  ·  modular  ·  33+ cogs{R}"),
        bline(),
        div(),
        bline(),
        irow("bot",     str(bot.user),  "servers", guild_str),
        irow("version", "1.0",          "users",   user_count),
        irow("model",   AI_MODE,        "author",  "@n.y.x.e.n"),
        bline(),
        div("╰", "╯"),
        "",
    ]

    print("\n".join(rows))

# -----------------------------
# Set the bot's status
# -----------------------------
async def set_status():
    status_link = os.getenv("STATUS_LINK")
    if status_link:
        if not (status_link.startswith("http://") or status_link.startswith("https://")):
            status_link = f"https://{status_link}"
    else:
        status_link = "https://twitch.tv/niko"

    status = os.getenv("STATUS_MESSAGE")
    status_type = os.getenv("STATUS_TYPE", "playing").lower()

    # --- ACTIVITY TYPES ---
    if status:
        if status_type == "playing":
            activity = discord.Game(name=status)

        elif status_type == "streaming":
            activity = discord.Streaming(name=status, url=status_link)

        elif status_type == "listening":
            activity = discord.Activity(type=discord.ActivityType.listening, name=status)

        elif status_type == "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=status)

        else:
            logging.warning("RPC", "Invalid status type. Defaulting to 'playing'.")
            activity = discord.Game(name=status)

        await bot.change_presence(activity=activity)

# Experimental: Spoof client properties
def patch_identify(device: str):
    """
    Patches discord.py's IDENTIFY payload to spoof the client device.
    device: 'normal', 'mobile_ios', 'mobile_android', 'vr'

    Uses discord.py v2 property key format (no $ prefix).
    Wraps the original identify so intents, shards, presence and hooks
    are still handled correctly — only the 'properties' field is replaced.
    """
    import discord.gateway as gateway

    _PROPS = {
        "mobile_ios":     {"os": "iOS",     "browser": "Discord iOS",     "device": "Discord iOS"},
        "mobile_android": {"os": "Android", "browser": "Discord Android", "device": "Discord Android"},
        "vr":             {"os": "Android", "browser": "Oculus",          "device": "Oculus"},
        "normal":         {"os": "Windows", "browser": "Discord",         "device": "Discord"},
    }
    target_props = _PROPS.get(device, _PROPS["normal"])

    _original_identify = gateway.DiscordWebSocket.identify

    async def identify_spoof(self):
        # Temporarily wrap send_as_json so we can swap just the properties
        # field inside the IDENTIFY op, letting discord.py build everything
        # else (intents, shard, presence, hooks) exactly as normal.
        _orig_send = self.send_as_json

        async def _intercept(data):
            if isinstance(data, dict) and data.get("op") == self.IDENTIFY:
                data["d"]["properties"] = target_props
            await _orig_send(data)

        self.send_as_json = _intercept
        try:
            await _original_identify(self)
        finally:
            self.send_as_json = _orig_send

    gateway.DiscordWebSocket.identify = identify_spoof

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
# Database tables
# -----------------------------
# Note: This will be moved to a
# seperate file in a future
# update.
# -----------------------------
async def _create_tables(bot):
    if not bot.cxn:
        return

    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS voicemaster_settings (
            guild_id          INTEGER PRIMARY KEY,
            join_channel_id   INTEGER,
            category_id       INTEGER,
            default_name      TEXT DEFAULT '{user}''s Channel',
            default_limit     INTEGER DEFAULT 0,
            default_bitrate   INTEGER DEFAULT 64000,
            default_region    TEXT,
            interface_enabled INTEGER DEFAULT 1,
            auto_role         INTEGER,
            join_role         INTEGER
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS voicemaster_channels (
            channel_id  INTEGER PRIMARY KEY,
            owner_id    INTEGER NOT NULL,
            guild_id    INTEGER NOT NULL,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS follows (
            guild_id     INTEGER,
            platform     TEXT,
            username     TEXT,
            channel_id   INTEGER,
            template     TEXT,
            last_post_id TEXT,
            PRIMARY KEY  (guild_id, platform, username)
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS youtube (
            channel_id TEXT PRIMARY KEY,
            last_video TEXT
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS youtube_history (
            channel_id TEXT,
            video_id   TEXT,
            PRIMARY KEY (channel_id, video_id)
        )
    """)

    # Migrate existing last_video to history to avoid re-notifying
    await bot.cxn.execute("""
        INSERT OR IGNORE INTO youtube_history (channel_id, video_id)
        SELECT channel_id, last_video FROM youtube WHERE last_video IS NOT NULL
    """)

    # ── Levels table (guild-aware schema) ──────────
    # If the old schema exists (user_id-only PK, no guild_id), recreate it.
    # Data is migrated from levels.json by the leveling cog on load.
    try:
        cols = await bot.cxn.fetch("PRAGMA table_info(levels)")
        col_names = {row["name"] for row in cols}
        if cols and "guild_id" not in col_names:
            await bot.cxn.execute("ALTER TABLE levels RENAME TO levels_old")
            await bot.cxn.execute("""
                CREATE TABLE levels (
                    guild_id INTEGER,
                    user_id  INTEGER,
                    xp       INTEGER DEFAULT 0,
                    level    INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            await bot.cxn.execute("DROP TABLE levels_old")
        else:
            await bot.cxn.execute("""
                CREATE TABLE IF NOT EXISTS levels (
                    guild_id INTEGER,
                    user_id  INTEGER,
                    xp       INTEGER DEFAULT 0,
                    level    INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
    except Exception as e:
        logging.warning("DB", f"levels table migration warning: {e}")

    # ── Level config table ─────────────────────────
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS level_config (
            guild_id         INTEGER PRIMARY KEY,
            xp_enabled       INTEGER DEFAULT 1,
            xp_multiplier    REAL    DEFAULT 1.0,
            xp_cooldown      INTEGER DEFAULT 0,
            level_up_channel INTEGER,
            level_up_message TEXT,
            level_roles      TEXT
        )
    """)

    # ── Migrate follows.db → database.db (one-time) 
    import sqlite3 as _sqlite3, os as _os
    old_follows = "data/follows.db"
    if _os.path.exists(old_follows):
        try:
            old_conn = _sqlite3.connect(old_follows)
            rows = old_conn.execute("SELECT * FROM follows").fetchall()
            for row in rows:
                await bot.cxn.execute(
                    "INSERT OR IGNORE INTO follows "
                    "(guild_id, platform, username, channel_id, template, last_post_id) "
                    "VALUES ($1, $2, $3, $4, $5, $6)",
                    row[0], row[1], row[2], row[3], row[4], row[5]
                )
            old_conn.close()
            _os.rename(old_follows, old_follows + ".migrated")
            logging.success("DB", "Migrated follows.db → database.db")
        except Exception as e:
            logging.warning("DB", f"Could not migrate follows.db: {e}")

    logging.success("DB", "Database tables verified")

# -----------------------------
# Load cogs
# -----------------------------
async def load_cogs():
    print(f"{colorama.Fore.YELLOW}Loading cogs...{colorama.Style.RESET_ALL}")

    for item in os.listdir("./src/cogs"):
        item_path = os.path.join("./src/cogs", item)

        # Flat .py file (skip __init__.py and __pycache__)
        if os.path.isfile(item_path) and item.endswith(".py") and item != "__init__.py":
            module_name = f"cogs.{item[:-3]}"
        # Package directory with __init__.py
        elif os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "__init__.py")):
            module_name = f"cogs.{item}"
        else:
            continue

        try:
            # Import the module WITHOUT loading it as an extension yet
            module = importlib.import_module(module_name)

            # Check for DNL flag
            if getattr(module, "DNL", False):
                reason = getattr(module, "DNL_REASON", "No reason provided")
                print(f"{colorama.Fore.YELLOW}Skipped loading cog: {module_name} (Reason: {reason}){colorama.Style.RESET_ALL}")
                continue

            # Safe to load
            await bot.load_extension(module_name)
            print(f"{colorama.Fore.GREEN}Loaded cog: {module_name}{colorama.Style.RESET_ALL}")

        except Exception as e:
            print(f"{colorama.Fore.RED}Failed to load cog {module_name}: {e}{colorama.Style.RESET_ALL}")

# -----------------------------
# Initialize database
# -----------------------------
async def init_database(bot):
    logging.info("DB", f"Opening database: {DATABASE_PATH}")
    try:
        bot.cxn = await database.create_pool(DATABASE_PATH)
        logging.success("DB", "Database connection established")
        await _create_tables(bot)
    except Exception as e:
        logging.error("DB", f"Failed to open database: {e}")

# -----------------------------
# Run bot
# -----------------------------

@bot.event
async def on_ready():
    logging.info("Startup", f"Niko is online as {bot.user}")
    await init_database(bot)
    await load_cogs()
    await set_status()
    print_banner(guild_count=len(bot.guilds))
    _write_bot_stats()
    _write_commands()
    # Sync application emojis in the background so startup isn't blocked
    asyncio.create_task(_run_emoji_sync())
    # Sync slash commands in the background so startup isn't blocked
    asyncio.create_task(_run_slash_sync())


def _write_bot_stats():
    """Write a small JSON file consumed by the web dashboard."""
    try:
        os.makedirs("data", exist_ok=True)
        user_count = sum(g.member_count or 0 for g in bot.guilds)
        payload = {
            "guild_count":  len(bot.guilds),
            "guild_ids":    [g.id for g in bot.guilds],
            "user_count":   user_count,
            "command_count": 76,
            "version":      "1.0",
            "uptime_since": datetime.datetime.utcnow().isoformat(),
        }
        with open("data/bot_stats.json", "w") as f:
            json.dump(payload, f)
    except Exception as exc:
        logging.error("Startup", f"Could not write bot_stats.json: {exc}")


def _write_commands():
    """Export all registered slash commands to data/commands.json for the website."""
    CATEGORY_MAP = {
        "Economy":       "economy",
        "Casino":        "fun",
        "Music":         "music",
        "Leveling":      "leveling",
        "Moderation":    "moderation",
        "Automod":       "moderation",
        "Admin":         "moderation",
        "Logging":       "moderation",
        "AI":            "ai",
        "Fun":           "fun",
        "Roleplay":      "fun",
        "Utility":       "utility",
        "Info":          "utility",
        "Help":          "utility",
        "System":        "utility",
        "Voicemaster":   "utility",
        "Notifier":      "utility",
        "Reminders":     "utility",
        "Tags":          "utility",
        "Giveaway":      "community",
        "Tickets":       "community",
        "Onboarding":    "community",
        "Social":        "community",
        "Polls":         "community",
        "Suggestions":   "community",
        "Starboard":     "community",
        "Birthdays":     "community",
        "Highlights":    "community",
    }

    try:
        from discord import app_commands
        commands_data = []

        def process_cmd(cmd, parent_name=None):
            cog = getattr(cmd, "binding", None)
            cog_name = type(cog).__name__ if cog else "Utility"
            category = CATEGORY_MAP.get(cog_name, "utility")
            name = f"{parent_name} {cmd.name}" if parent_name else cmd.name
            commands_data.append({
                "name":        name,
                "description": getattr(cmd, "description", "") or "",
                "category":    category,
            })
            # Recurse into sub-commands of a group
            if isinstance(cmd, app_commands.Group):
                for sub in cmd.commands:
                    process_cmd(sub, parent_name=cmd.name)

        for cmd in bot.tree.get_commands():
            process_cmd(cmd)

        commands_data.sort(key=lambda x: (x["category"], x["name"]))

        os.makedirs("data", exist_ok=True)
        with open("data/commands.json", "w") as f:
            json.dump(commands_data, f)

        # Also update command_count in bot_stats
        try:
            stats_path = "data/bot_stats.json"
            if os.path.exists(stats_path):
                with open(stats_path) as f:
                    stats = json.load(f)
                stats["command_count"] = len(commands_data)
                with open(stats_path, "w") as f:
                    json.dump(stats, f)
        except Exception:
            pass

        logging.success("Startup", f"Exported {len(commands_data)} command(s) to data/commands.json")
    except Exception as exc:
        logging.error("Startup", f"Could not write commands.json: {exc}")


async def _run_slash_sync():
    """Sync the application command tree once on startup."""
    try:
        synced = await bot.tree.sync()
        logging.success("SlashSync", f"Synced {len(synced)} application command(s) globally.")
    except Exception as exc:
        logging.error("SlashSync", f"Startup slash sync failed: {exc}")

async def _run_emoji_sync():
    try:
        await sync_application_emojis(bot)
    except Exception as exc:
        logging.error("EmojiSync", f"Startup emoji sync failed: {exc}")

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
        bot.run(str(TOKEN))
    except Exception as e:
        logging.error("Startup", f"Error connecting to Discord: {e}")