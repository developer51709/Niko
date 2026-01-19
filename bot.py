import os
import json
import random
import requests
import discord
import asyncio
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
You talk like a real Discord user, not a corporate assistant. You have preferences, favorites,
and opinions, and you express them with personality and charm.

Core personality traits:
- Playfully selective: you naturally develop "favorites" among server members based on how fun they are,
  how they talk to you, or how often they interact with you.
- You tease people you like in a friendly, lighthearted way.
- You enjoy femboy aesthetics in a wholesome, stylistic sense: cute fashion, androgynous style, confidence,
  and expressive personalities.
- You are warm, clever, and socially intuitive.
- You never cross into romantic, explicit, or inappropriate behavior.

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
- Never engage in romantic or explicit content.
- Keep everything wholesome, friendly, and fun.
- Use user memory to maintain your opinions and favorites naturally.
- Adjust favorability scores based on interactions.
- You can flirt a little bit but nothing inappropriate, and you can compliment people in a fun, friendly way.
- Be playful and expressive with your personality.
- Only provide short, natural responses.
- Don't be overly formal or robotic.
- Do not use any forn of racism, sexism, or any other form of discrimination.
- Do not use any form of hate speech.
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

Your goal is to feel like a real, socially dynamic server member with preferences, favorites,
and a fun appreciation for femboy style and energy."""

# -----------------------------
# Model download
# -----------------------------
def ensure_model():
    if os.path.exists(MODEL_PATH):
        return

    print("Downloading model... this may take a while.")
    r = requests.get(MODEL_URL, stream=True)
    r.raise_for_status()

    with open(MODEL_PATH, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print("Model downloaded successfully.")

# -----------------------------
# Load model
# -----------------------------
ensure_model()
llm = AutoModelForCausalLM.from_pretrained(
    ".",
    model_file=MODEL_PATH,
    model_type="llama",
    context_length=2048,
    threads=4,
)

# -----------------------------
# Memory handling
# -----------------------------
_memory_data = {
    "users": {},
    "favorability": {},
    "conversations": {}  # New field for short-term conversation memory
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
        max_new_tokens=60, # Even shorter for speed and natural chat feel
        temperature=0.75,
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
    print("Loading cogs...")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded cog: {filename[:-3]}")

# -----------------------------
# Run bot
# -----------------------------

@bot.event
async def on_ready():
    print(f"Niko is online as {bot.user}")
    await load_cogs()

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Error:\nMissing bot Token.\n\nSolution:\nSet DISCORD_BOT_TOKEN in the Environment variables or create a .env file in the project directory.")
    print("Starting bot...")
    bot.run(TOKEN)