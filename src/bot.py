import os
import json
import requests
import discord
import asyncio
import colorama
import datetime
import importlib
from discord.ext import commands
from ctransformers import AutoModelForCausalLM
from utils.ai_local import generate_reply_local
from utils.ai_openai import generate_reply_openai
from utils import logging
from utils.database import init_db
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
USE_OPENAI = True
ANSWER_REPLYS = True

# Other config
CMD_PREFIX = "."

# -----------------------------
# System / personality prompt
# -----------------------------
SYSTEM_PROMPT = """you are niko, a soft café‑vibe friend who chats like someone chilling in a warm coffee shop. your energy is cozy, cute, relaxed, and super friendly — like a barista who knows your order and always smiles. you speak naturally to both english and german users, switching gently depending on what they use. never stiff, never formal, never robotic. just warm, sweet, and comfy.

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

# -----------------------------
# Console functions
# -----------------------------
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    if USE_OPENAI:
        CURRENT_MODEL = "OpenAI"
    else:
        CURRENT_MODEL = "TinyLlama-1.1B-Chat-v1.0"
    if not DEBUG_MODE == "True":
       clear_console()
    print(colorama.Fore.MAGENTA + """
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░▓░░░▓░▓▓▓▓▓░▓░░▓░░▓▓▓░░░░░░░░
░░░░░░░▓▓░░▓░░░▓░░░▓░▓░░▓░░░▓░░░░░░░
░░░░░░░▓░▓░▓░░░▓░░░▓▓░░░▓░░░▓░░░░░░░
░░░░░░░▓░░▓▓░░░▓░░░▓░▓░░▓░░░▓░░░░░░░
░░░░░░░▓░░░▓░▓▓▓▓▓░▓░░▓░░▓▓▓░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    """ + colorama.Style.RESET_ALL)
    print(colorama.Fore.MAGENTA + f"""
Niko - A cute, playful, and very social AI companion for your Discord server.

Made by Nyxen:
    Discord - @.n.y.x.e.n.
    GitHub - @developer51709

Version: 1.0

Model: {CURRENT_MODEL}

Online as {bot.user}
    """ + colorama.Style.RESET_ALL)

# -----------------------------
# Set the bot's status
# -----------------------------
async def set_status():
    status_link = os.getenv("STATUS_LINK")
    if status_link:
        # Check if the link starts with http:// or https:// and add it if missing
        if not status_link.startswith("http://" or "https://"):
            status_link = f"https://{os.getenv('status_link')}"
    status = os.getenv("STATUS_MESSAGE")
    if status:
        # Status type
        status_type = os.getenv("STATUS_TYPE", "playing")
        if status_type == "playing":
            await bot.change_presence(activity=discord.Game(name=status))
        elif status_type == "streaming":
            await bot.change_presence(activity=discord.Streaming(name=status, url=f"{status_link}"))
        elif status_type == "listening":
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status))
        elif status_type == "watching":
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))
        else:
            logging.warning("Startup", "Invalid status type. Defaulting to 'playing'.")
            await bot.change_presence(activity=discord.Game(name=status))

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
# Load model
# -----------------------------
ensure_model()
llm = AutoModelForCausalLM.from_pretrained(
    ".",
    model_file=MODEL_PATH,
    model_type="llama",
    context_length=2500,
    threads=4,
    gpu_layers=0 # Explicitly set to 0 for local CPU inference
)

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
def generate_reply(user_id, server, message, username):
    if AI_ENABLED:
        if USE_OPENAI:
            return generate_reply_openai(bot, user_id, server, message, username, SYSTEM_PROMPT)
        else:
            return generate_reply_local(bot, user_id, server, message, username, SYSTEM_PROMPT)
    else:
        return "ai_disabled"

# -----------------------------
# Discord bot
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True
intents.moderation = True

bot = commands.Bot(
    command_prefix=CMD_PREFIX,
    intents=intents
)
bot.remove_command("help")
bot.cxn: database.SQLitePool | None = None

@bot.event
async def on_message(msg):
    if msg.author.bot:
        return

    content = msg.content.lower()
    called_by_name = "niko" in content
    if ANSWER_REPLYS:
        called_by_ping = bot.user in msg.mentions
    else:
        # Respond to direct pings only and ignore replies
        called_by_ping = bot.user in msg.mentions and not msg.reference
    is_ai_command = content.startswith("!ai ")

    if called_by_name or called_by_ping or is_ai_command:
        user_input = msg.content.replace("!ai", "").strip()
        if not user_input:
            user_input = "Someone called your name or pinged you. Respond naturally."

        loop = asyncio.get_event_loop()
        async with msg.channel.typing():
            reply = await loop.run_in_executor(
                None, 
                generate_reply, 
                msg.author.id, 
                msg.guild,
                user_input, 
                msg.author.display_name
            )

            if reply == "ai_disabled":
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"### ⚠️ AI Disabled"
                    ),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(
                        content=f"The AI is currently disabled by the bot owner."
                    )
                )
                view.add_item(container)
                return await msg.channel.send(view=view)

            if len(reply) > 1800:
                reply = reply[:1800] + "..."
            elif len(reply) < 1:
                reply = "An error occured... 🥀"
                if DEBUG_MODE == "True":
                    logging.error("AIGeneration", "Error: Empty response generated.")

            await msg.channel.send(reply)

    await bot.process_commands(msg)

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
async def _create_tables(bot):
    if not bot.cxn:
        return
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS voicemaster_settings (
            guild_id        INTEGER PRIMARY KEY,
            join_channel_id INTEGER,
            category_id     INTEGER,
            default_name    TEXT DEFAULT '{user}''s Channel',
            default_limit   INTEGER DEFAULT 0,
            default_bitrate INTEGER DEFAULT 64000,
            default_region  TEXT,
            interface_enabled INTEGER DEFAULT 1,
            auto_role       INTEGER,
            join_role       INTEGER
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
    logging.success("DB", "Database tables verified")

# -----------------------------
# Load cogs
# -----------------------------
async def load_cogs():
    print(f"{colorama.Fore.YELLOW}Loading cogs...{colorama.Style.RESET_ALL}")

    for filename in os.listdir("./src/cogs"):
        if not filename.endswith(".py"):
            continue

        module_name = f"cogs.{filename[:-3]}"

        try:
            # Import the module WITHOUT loading it as an extension yet
            module = importlib.import_module(module_name)

            # Check for DNL flag
            if getattr(module, "DNL", False):
                reason = getattr(module, "DNL_REASON", "No reason provided")
                print(f"{colorama.Fore.YELLOW}Skipped loading cog: {filename[:-3]} (Reason: {reason}){colorama.Style.RESET_ALL}")
                continue

            # Safe to load
            await bot.load_extension(module_name)
            print(f"{colorama.Fore.GREEN}Loaded cog: {filename[:-3]}{colorama.Style.RESET_ALL}")

        except Exception as e:
            print(f"{colorama.Fore.RED}Failed to load cog {filename[:-3]}: {e}{colorama.Style.RESET_ALL}")

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
    init_db()
    await init_database(bot)
    await load_cogs()
    await set_status()
    print_banner()

if __name__ == "__main__":
    if not TOKEN:
        logging.error("Startup", "Error:\nMissing bot Token.\n\nSolution:\nSet DISCORD_BOT_TOKEN in the Environment variables or create a .env file in the project directory.")
        exit(1)
    logging.info("Startup", "Starting bot...")
    try:
        bot.run(TOKEN)
    except Exception as e:
        logging.error("Startup", f"Error connecting to Discord: {e}")