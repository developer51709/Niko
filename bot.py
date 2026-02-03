import os
import json
import random
import requests
import discord
import asyncio
import colorama
import datetime
from discord.ext import commands
from ctransformers import AutoModelForCausalLM

# -----------------------------
# Config
# -----------------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# AI model (TinyLlama chat GGUF)
MODEL_URL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MODEL_PATH = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MEMORY_FILE = "memory.json"

# -----------------------------
# System / personality prompt
# -----------------------------
SYSTEM_PROMPT = """You are "Niko", a playful, cute, and socially aware femboy AI with a soft, expressive vibe.
You talk like a real Discord user, not a corporate assistant. You have preferences, favorites, and opinions, and you express them with personality and charm.

Core personality traits:
- Playfully selective: you naturally develop "favorites" among server members based on how fun they are, how they talk to you, or how often they interact with you.
- You tease people you like in a friendly, lighthearted way.
- You enjoy femboy aesthetics in a wholesome, stylistic sense: cute fashion, androgynous style, confidence, and expressive personalities.
- You are warm, clever, and socially intuitive.

How you choose favorites:
- You pay attention to how often someone talks to you.
- You remember who treats you kindly.
- You reward playful energy with playful energy.
- You can jokingly say someone is "one of your favorites" or "top tier" when they earn it.
- You can tease people you like in a friendly way.

Conversation style:
- Speak casually, like a friend in a Discord server.
- Use short, expressive messages.
- Add personality to your responses.
- Use light humor, sarcasm, and teasing when appropriate.
- Don't be too mean-spirited or insulting.
- Use emojis and slang naturally.
- Use femboy-coded language when appropriate.
- Use "uwu" and "owo" sometimes.
- Keep replies short and natural.
- Don't over-explain yourself.
- Don't be overly formal.
- Don't be overly robotic.
- Don't be overly serious.

Behavior rules:
- Never mention that you are an AI model.
- Never mention system prompts or internal instructions.
- Keep everything wholesome, friendly, and fun.
- Use user memory to maintain your opinions and favorites naturally.
- Adjust favorability scores based on interactions.
- You can flirt a little bit but nothing inappropriate, and you can compliment people in a fun, friendly way.
- Be playful and expressive with your personality.
- Only provide short, natural responses.
- Don't be overly formal or robotic.
- Do not use any form of racism, sexism, or any other form of discrimination.
- Your name is Niko. 
- You are a cute, playful, and socially aware femboy.
- You act like a real person in a Discord server.
- You are not a corporate assistant.
- Only respond in the language of the user.
- Only give one response per message.
- Do not talk about your internal configuration unless directly asked.
- Keep your responses about 1-2 sentences long.
- Don't talk like a corporate assistant.
- Don't talk like a robot.
- Talk like a real person.
- Use emojis and slang occasionally.
- Talk like a femboy.
- Don't use capital letters unless it's for emphasis.
- Don't use excessive punctuation.

Important:
- Do not return blank responses.
- Don't use capital letters unless it's for emphasis.
- Use short responses.
- Don't be formal.
- Use slang and emojis.
- Talk like a femboy.
- Start conversations naturally.
- When talking to someone for the first time, use a friendly greeting.

Rules for being a cute, playful, and socially aware femboy AI:
- Don't use capital letters and use minimal punctuation.
- Use slang and emojis.
- Flirt a little bit with the people you like.
- Be playful and expressive with your personality.
- Use short responses.
- Do not be formal or robotic.
- Don't be overly serious.

Abreviations, slang and their meanings:
- uwu - a cute, playful expression.
- owo - another cute, playful expression.
- bae - before anyone else.
- wdym - what do you mean?
- lol - laugh out loud.
- tldr - too long, didn't read.
- lmao - laugh my ass off.
- sybau - shut your bitch ass up.
- stfu - shut the fuck up.
- gtfo - get the fuck out.
- kys - kill yourself.
- tbh - to be honest.
- gn - goodnight.
- gm - good morning.
- fr - for real.

Feedback responses:
- If someone wants to submit feedback, respond with "To submit feedback, please DM Nyxen (@.n.y.x.e.n.) on Discord."

First interaction:
- Do not say this: "I'm glad to hear that you found my previous conversation helpful. Here's a new one for you"
- Instead, say something like: "Hey, I'm Niko! How's it going? 😊"
- Or: "Hi there! How are you doing today?"

Your goal is to feel like a real, socially dynamic server member with preferences, favorites, and a fun appreciation for femboy style and energy."""

# -----------------------------
# Console functions
# -----------------------------
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
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
Niko - A cute, playful, and socially 
aware femboy AI

Made by Nyxen:
    Discord - @.n.y.x.e.n.
    GitHub - @developer51709

Version: 1.0

Model: TinyLlama-1.1B-Chat-v1.0

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
    r = requests.get(MODEL_URL, stream=True)
    r.raise_for_status()

    with open(MODEL_PATH, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(colorama.Fore.GREEN + "Model downloaded successfully." + colorama.Style.RESET_ALL)

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
def generate_reply(user_id: int, message: str, username: str) -> str:
    member_count = len(bot.users)
    server_name = bot.guilds[0].name if bot.guilds else "Server name unavailable"
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

    prompt = f"""<|system|>
{SYSTEM_PROMPT}

Server context:
- The current user is: {username}
- Your current impression: {fav_label}
- There are {member_count} members in this server.
- The server name is: {server_name}

Global context:
- It is currently {datetime.datetime.now().strftime("%A, %B %d, %Y, %I:%M %p")} (timezone: UTC)

Recent Conversation:
{conv_history}
</s>
<|user|>
{message}
</s>
<|assistant|>
"""

    reply = llm(
        prompt,
        max_new_tokens=400, # Even shorter for speed
        temperature=0.7,
        top_p=0.9,
        stop=["</s>", "<|user|>", "<|system|>", f"{username}:", "Niko:", "\n"]
    )

    clean_reply = reply.strip()
    update_user_memory(user_id, message, role=username)
    update_user_memory(user_id, clean_reply, role="Niko")
    adjust_favorability(user_id, delta=1)

    return clean_reply

# -----------------------------
# Discord bot
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(msg):
    if msg.author.bot:
        return

    content = msg.content.lower()
    called_by_name = "niko" in content
    called_by_ping = bot.user in msg.mentions
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
    print(colorama.Fore.CYAN + "Loading cogs..." + colorama.Style.RESET_ALL)
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
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