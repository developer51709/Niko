import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
import json
import os
import re
import random
from typing import Dict, List, Any

DATA_FILE = "uwulock.json"

# personality mode: "normal" or "cafe"
PERSONALITY = "cafe"

# -----------------------------
# MESSAGE DICTIONARY
# -----------------------------
MESSAGES = {
    "normal": {
        "en": {
            "uwu_locked": "Uwulocked {mention}.",
            "uwu_unlocked": "Un‑uwulocked {mention}.",
            "fetch_fail": "Couldn't process uwu message.",
            "no_permission": "You need administrator permissions.",
        },
        "de": {
            "uwu_locked": "{mention} wurde uwugelockt.",
            "uwu_unlocked": "{mention} wurde ent‑uwugelockt.",
            "fetch_fail": "Konnte die uwu‑Nachricht nicht verarbeiten.",
            "no_permission": "Du benötigst Administratorrechte.",
        },
    },

    "cafe": {
        "en": {
            "uwu_locked": "okay bestie… {mention} is now uwu‑locked ☕💖",
            "uwu_unlocked": "un‑uwu’d {mention} — they’re free again ☕🌿",
            "fetch_fail": "aww i couldn’t process that uwu message rn 😭☕",
            "no_permission": "you need admin perms for this sweetie ☕💛",
        },
        "de": {
            "uwu_locked": "okay liebchen… {mention} ist jetzt uwu‑gelockt ☕💖",
            "uwu_unlocked": "{mention} wurde ent‑uwu’t — wieder frei ☕🌿",
            "fetch_fail": "aww ich konnte die uwu‑nachricht gerade nicht verarbeiten 😭☕",
            "no_permission": "du brauchst admin‑rechte dafür ☕💛",
        },
    },

    # future personalities can be added here
}

# -----------------------------
# LANGUAGE + PERSONALITY HELPERS
# -----------------------------
def get_lang(ctx):
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"


def get_personality():
    return PERSONALITY if PERSONALITY in MESSAGES else "normal"


def msg(ctx, key, **kwargs):
    personality = get_personality()
    lang = get_lang(ctx)

    block = MESSAGES.get(personality, {}).get(lang, {})
    text = block.get(key)

    if text is None:
        text = MESSAGES.get(personality, {}).get("en", {}).get(key)

    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key)

    if text is None:
        text = MESSAGES["normal"]["en"].get(key, key)

    return text.format(**kwargs) if kwargs else text


# -----------------------------
# UWU LOCK COG
# -----------------------------
class UwULock(commands.Cog):
    """UwU‑lock system with cozy café personality + bilingual support."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.uwu_queue: Dict[int, List[dict]] = {}
        self.data = self.load_data()
        self.process_uwu_queue.start()

    # -----------------------------
    # JSON helpers
    # -----------------------------
    def load_data(self) -> dict:
        if not os.path.exists(DATA_FILE):
            return {}
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    # -----------------------------
    # uwulock command
    # -----------------------------
    @commands.command(
        name="uwulock",
        help="uwu‑lock a user so their messages become uwu‑ified ☕ | uwu‑lockt einen nutzer"
    )
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    async def uwulock(self, ctx: commands.Context, *, user: discord.Member):
        guild_id = str(ctx.guild.id)
        channel_id = str(ctx.channel.id)
        user_id = str(user.id)

        if guild_id not in self.data:
            self.data[guild_id] = {}

        key = f"{user_id}:{channel_id}"
        existing = self.data[guild_id].get(key)

        # -----------------------------
        # UN‑UWULOCK
        # -----------------------------
        if existing:
            webhook_url = existing["webhook"]

            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(webhook_url, session=session)
                try:
                    await webhook.delete(reason=f"unuwulocked by {ctx.author.name}")
                except Exception:
                    pass

            del self.data[guild_id][key]
            self.save_data()
            return await ctx.send(msg(ctx, "uwu_unlocked", mention=user.mention))

        # -----------------------------
        # UWULOCK
        # -----------------------------
        self.data[guild_id] = {}

        try:
            webhook = await ctx.channel.create_webhook(
                name=user.display_name,
                avatar=await user.display_avatar.read(),
                reason=f"uwulocked by {ctx.author}",
            )
        except Exception:
            for wh in await ctx.channel.webhooks():
                await wh.delete(reason="clearing unused webhooks")

            webhook = await ctx.channel.create_webhook(
                name=user.display_name,
                avatar=await user.display_avatar.read(),
                reason=f"uwulocked by {ctx.author}",
            )

        self.data[guild_id][key] = {
            "user_id": user_id,
            "channel_id": channel_id,
            "webhook": webhook.url,
        }
        self.save_data()

        return await ctx.send(msg(ctx, "uwu_locked", mention=user.mention))

    # -----------------------------
    # Background task
    # -----------------------------
    @tasks.loop(seconds=3)
    async def process_uwu_queue(self):
        try:
            for guild_id, messages in list(self.uwu_queue.items()):
                if not messages:
                    continue

                message_data = messages[0]

                try:
                    async with aiohttp.ClientSession() as session:
                        webhook = discord.Webhook.from_url(
                            message_data["webhook_url"], session=session
                        )
                        await webhook.send(
                            content=message_data["content"],
                            username=message_data["username"],
                            avatar_url=message_data["avatar_url"],
                        )

                    self.uwu_queue[guild_id].pop(0)

                except Exception:
                    self.uwu_queue[guild_id].pop(0)

                await asyncio.sleep(0.5)

        except Exception:
            pass

    @process_uwu_queue.before_loop
    async def before_uwu_processor(self):
        await self.bot.wait_until_ready()

    # -----------------------------
    # Listener
    # -----------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        guild_id = str(message.guild.id)
        channel_id = str(message.channel.id)
        user_id = str(message.author.id)

        if guild_id not in self.data:
            return

        key = f"{user_id}:{channel_id}"
        entry = self.data[guild_id].get(key)

        if not entry:
            return

        try:
            await message.delete()
        except discord.Forbidden:
            return

        if message.guild.id not in self.uwu_queue:
            self.uwu_queue[message.guild.id] = []

        self.uwu_queue[message.guild.id].append(
            {
                "webhook_url": entry["webhook"],
                "content": self.uwuify(message.content),
                "username": message.author.display_name,
                "avatar_url": message.author.display_avatar.url,
            }
        )

    # -----------------------------
    # uwuify helper
    # -----------------------------
    def uwuify(self, text: str) -> str:
        try:
            with open("blocked_words.json", "r") as f:
                filters = json.load(f)
        except Exception:
            filters = {"slurs": [], "threats": []}

        slur_replacements = ["sweetie", "snugglebun", "fluffball", "cutie‑pie", "honeybee"]
        threat_replacements = [
            "I need a hug…",
            "I should calm down…",
            "I’m feeling spicy but harmless…",
            "deep breaths…"
        ]

        for bad in filters.get("slurs", []):
            pattern = re.compile(rf"\b{re.escape(bad)}\b", re.IGNORECASE)
            text = pattern.sub(random.choice(slur_replacements), text)

        for bad in filters.get("threats", []):
            pattern = re.compile(rf"\b{re.escape(bad)}\b", re.IGNORECASE)
            text = pattern.sub(random.choice(threat_replacements), text)

        text = text.replace("r", "w").replace("l", "w")
        text = text.replace("R", "W").replace("L", "W")

        interjections = [
            "owo", "uwu", "x3", ">w<", "^w^", "rawr~",
            "nya~", "teehee~", "(≧◡≦)", "(⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)",
            "(｡♥‿♥｡)", "(ᵘʷᵘ)", "(๑˃ᴗ˂)ﻭ"
        ]

        prefixes = ["uhh", "umm", "ahh", "oh~", "hehe", "teehee", "h‑hewwo"]

        emojis = ["✨", "💖", "🥺", "👉👈", "🌸", "💞", "😳", "😼", "💗", "🌟"]

        words = text.split()
        uwu_words = []

        if random.random() < 0.35:
            uwu_words.append(random.choice(interjections))

        for w in words:
            base = w.lower()

            if random.random() < 0.20:
                uwu_words.append(random.choice(prefixes))

            if random.random() < 0.40:
                w = f"{w[0]}-{w}"

            if base in ["i", "to", "my", "we", "you"] and random.random() < 0.65:
                w = f"{w[0]}-{w}"

            if base == "to" and random.random() < 0.45:
                w = f"{w[0]}-{w[0]}-{w}"

            w = w.replace("no", "nyo")
            w = w.replace("has", "haz")
            w = w.replace("have", "haz")
            w = w.replace("you", "uu")
            w = w.replace("love", "wuv")

            uwu_words.append(w)

            if random.random() < 0.25:
                uwu_words.append(random.choice(interjections))

            if random.random() < 0.20:
                uwu_words.append(random.choice(emojis))

        return " ".join(uwu_words)

    async def cog_unload(self):
        self.process_uwu_queue.cancel()


async def setup(bot: commands.Bot):
    await bot.add_cog(UwULock(bot))