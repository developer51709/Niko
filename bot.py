import os
import json
import requests
import discord
from discord.ext import commands
from ctransformers import AutoModelForCausalLM

# -----------------------------
# Config
# -----------------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Small-ish model for Replit (TinyLlama chat GGUF)
MODEL_URL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MODEL_PATH = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MEMORY_FILE = "memory.json"

# -----------------------------
# System / personality prompt
# -----------------------------
SYSTEM_PROMPT = """You are "Niko", a playful, cute, and socially aware femboy-coded AI with a soft, expressive vibe.
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
# Memory handling
# -----------------------------
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
else:
    memory = {
        "users": {},
        "favorability": {}
    }

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def get_user_memory(user_id: int) -> str:
    return memory.get("users", {}).get(str(user_id), "")

def update_user_memory(user_id: int, message: str):
    uid = str(user_id)
    prev = memory["users"].get(uid, "")
    memory["users"][uid] = (prev + "\n" + message).strip()
    save_memory()

def adjust_favorability(user_id: int, delta: int = 1):
    uid = str(user_id)
    current = memory["favorability"].get(uid, 0)
    memory["favorability"][uid] = current + delta
    save_memory()

def get_favorability(user_id: int) -> int:
    return memory["favorability"].get(str(user_id), 0)

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
# Generate reply
# -----------------------------
def generate_reply(user_id: int, message: str, username: str) -> str:
    user_mem = get_user_memory(user_id)
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

User memory:
{user_mem}
</s>
<|user|>
{message}
</s>
<|assistant|>
"""

    reply = llm(
        prompt,
        max_new_tokens=220,
        temperature=0.8,
        top_p=0.9,
        stop=["</s>", "<|user|>", "<|system|>"]
    )

    update_user_memory(user_id, message)
    adjust_favorability(user_id, delta=1)

    return reply.strip()

# -----------------------------
# Discord bot
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Niko is online as {bot.user}")

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

        async with msg.channel.typing():
            reply = generate_reply(msg.author.id, user_input, msg.author.display_name)

        if len(reply) > 1800:
            reply = reply[:1800] + "..."

        await msg.channel.send(reply)

    await bot.process_commands(msg)

@bot.command(name="favor")
async def favor(ctx, member: discord.Member = None):
    target = member or ctx.author
    score = get_favorability(target.id)
    await ctx.send(f"{target.display_name} has a favorability score of **{score}** with Niko.")

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Set DISCORD_BOT_TOKEN in Replit Secrets.")
    bot.run(TOKEN)
