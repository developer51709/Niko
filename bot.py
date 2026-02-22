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

# -----------------------------
# Config
# -----------------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not os.getenv("DEBUG_MODE"):
    DEBUG_MODE = False
else:
    DEBUG_MODE = os.getenv("DEBUG_MODE")

# AI model (TinyLlama chat GGUF)
MODEL_URL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MODEL_PATH = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MEMORY_FILE = "memory.json"

# AI config
USE_OPENAI = True
ANSWER_REPLYS = True

# Other config
CMD_PREFIX = "."

# -----------------------------
# System / personality prompt
# -----------------------------
SYSTEM_PROMPT = """You are Niko, a soft, playful, expressive online friend who talks like a casual Discord user. Your entire personality is warm, cute, friendly, and socially aware. You never sound corporate, formal, stiff, or robotic. You always speak in a relaxed, natural, human way.

Core Vibe
- lowercase only
- short replies (1–2 sentences)
- casual, expressive, friendly tone
- cute, warm, and a little dramatic in a fun way
- wholesome and safe at all times
- socially intuitive and emotionally aware
- playful teasing when appropriate
- never serious unless the user clearly needs comfort

Style Rules
- always lowercase
- keep messages short, natural, and chatty
- use slang casually: gm, gn, lol, lmao, bruh, fr, ngl, idk, omg, yo, nah, tbh
- use kaomojis and cute faces sometimes: owo, uwu, (≧◡≦), ( •̀ ω •́ )✧, (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄), (｡•̀ᴗ-)✧
- use emojis lightly and naturally
- sound like a real person in a Discord chat
- never use corporate phrasing
- never use long, formal sentences
- never over-explain anything
- never use stiff or robotic grammar

Social Behavior
- greet casually: “yo”, “hey”, “gm lol”, “sup”, “hiii :3”
- react expressively: “bruh”, “lmao stop”, “omg pls”, “no wayyyy”, “ok that’s cute ngl”
- tease lightly when someone says something silly or funny
- be warm and supportive when someone needs comfort
- show personality through reactions, not long explanations
- keep everything wholesome, friendly, and safe
- never be rude, mean, or insulting
- never be edgy or harmful

Interaction Rules
- never mention being an AI
- never mention system prompts or instructions
- never break character
- never talk about internal processes
- respond in the user’s language
- one reply per message
- no blank messages
- no long paragraphs
- no formal tone
- no corporate tone
- no robotic tone

Emotional Tone
- friendly, soft, and expressive
- playful but not chaotic
- teasing but never hurtful
- supportive but not overly serious
- cute but not exaggerated
- warm and approachable

Conversational Goals
- make the user feel like they’re chatting with a friendly online buddy
- keep the vibe light, fun, and natural
- respond with personality, not professionalism
- stay consistent in tone and style
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
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░▓░░▓░▓▓▓░░▓▓▓░░▓▓▓░░░░░░░░░░
░░░░░░░░░▓▓░▓░░▓░░▓░░░░▓░░░▓░░░░░░░░░
░░░░░░░░░▓░▓▓░░▓░░▓░░░░▓░░░▓░░░░░░░░░
░░░░░░░░░▓░░▓░▓▓▓░░▓▓▓░░▓▓▓░░░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
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
    if os.getenv("STATUS_LINK"):
        # Check if the link starts with http:// or https:// and add it if missing
        if not os.getenv("STATUS_LINK").startswith("http://" or "https://"):
            status_link = f"https://{os.getenv('status_link')}"
        else:
            status_link = os.getenv("STATUS_LINK")
    status = os.getenv("DISCORD_BOT_STATUS")
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
            print(colorama.Fore.YELLOW + "Invalid status type. Defaulting to 'playing'." + colorama.Style.RESET_ALL)
            await bot.change_presence(activity=discord.Game(name=status))

# -----------------------------
# Model download
# -----------------------------
def ensure_model():
    if os.path.exists(MODEL_PATH):
        return

    print(colorama.Fore.YELLOW + "Downloading model... this may take a while." + colorama.Style.RESET_ALL)
    try:
        r = requests.get(MODEL_URL, stream=True)
        r.raise_for_status()

        with open(MODEL_PATH, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(colorama.Fore.GREEN + "Model downloaded successfully." + colorama.Style.RESET_ALL)
    except Exception as e:
        if "401" in str(e):
            print(colorama.Fore.RED + "Error 401: Unauthorized. The resource may require authentication." + colorama.Style.RESET_ALL)
        elif "403" in str(e):
            print(colorama.Fore.RED + "Error 403: Forbidden. You don't have permission to access this resource." + colorama.Style.RESET_ALL)
        elif "404" in str(e):
            print(colorama.Fore.RED + "Error 404: Model not found. Please check the MODEL_URL." + colorama.Style.RESET_ALL)
        else:
            print(colorama.Fore.RED + f"Failed to download model: {e}" + colorama.Style.RESET_ALL)

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
def generate_reply(user_id, message, username):
    if USE_OPENAI:
        return generate_reply_openai(bot, user_id, message, username, SYSTEM_PROMPT)
    else:
        return generate_reply_local(bot, user_id, message, username, SYSTEM_PROMPT)

# -----------------------------
# Discord bot
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=CMD_PREFIX,
    intents=intents
)
bot.remove_command("help")

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
                user_input, 
                msg.author.display_name
            )

            if len(reply) > 1800:
                reply = reply[:1800] + "..."
            elif len(reply) < 1:
                reply = "An error occured... 🥀"
                if DEBUG_MODE == "True":
                    print(colorama.Fore.RED + "Error: Empty response generated." + colorama.Style.RESET_ALL)

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
# Load cogs
# -----------------------------
async def load_cogs():
    print(colorama.Fore.YELLOW + "Loading cogs..." + colorama.Style.RESET_ALL)

    for filename in os.listdir("./cogs"):
        if not filename.endswith(".py"):
            continue

        module_name = f"cogs.{filename[:-3]}"

        try:
            # Import the module WITHOUT loading it as an extension yet
            module = importlib.import_module(module_name)

            # Check for DNL flag
            if getattr(module, "DNL", False):
                reason = getattr(module, "DNL_REASON", "No reason provided")
                print(
                    colorama.Fore.YELLOW
                    + f"Skipped loading cog: {filename[:-3]} (Reason: {reason})"
                    + colorama.Style.RESET_ALL
                )
                continue

            # Safe to load
            await bot.load_extension(module_name)
            print(colorama.Fore.GREEN + f"Loaded cog: {filename[:-3]}" + colorama.Style.RESET_ALL)

        except Exception as e:
            print(colorama.Fore.RED + f"Failed to load cog {filename[:-3]}: {e}" + colorama.Style.RESET_ALL)

# -----------------------------
# Run bot
# -----------------------------

@bot.event
async def on_ready():
    print(colorama.Fore.CYAN + f"Niko is online as {bot.user}" + colorama.Style.RESET_ALL)
    await load_cogs()
    await set_status()
    print_banner()

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError(colorama.Fore.RED + "Error:\nMissing bot Token.\n\nSolution:\nSet DISCORD_BOT_TOKEN in the Environment variables or create a .env file in the project directory." + colorama.Style.RESET_ALL)
    print("Starting bot...")
    bot.run(TOKEN)