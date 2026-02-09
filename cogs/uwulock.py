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


class UwULock(commands.Cog):
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
        brief="uwulock someone lol",
        help="Locks a user so their messages become uwu‑ified",
    )
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    async def uwulock(self, ctx: commands.Context, *, user: discord.Member):
        guild_id = str(ctx.guild.id)
        channel_id = str(ctx.channel.id)
        user_id = str(user.id)

        # Ensure guild exists in JSON
        if guild_id not in self.data:
            self.data[guild_id] = {}

        # Check if user is already uwulocked
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
            return await ctx.send(f"Un‑uwulocked {user.mention}")

        # -----------------------------
        # UWULOCK
        # -----------------------------
        # Clear old uwulocks for this guild
        self.data[guild_id] = {}

        # Create webhook
        try:
            webhook = await ctx.channel.create_webhook(
                name=user.display_name,
                avatar=await user.display_avatar.read(),
                reason=f"uwulocked by {ctx.author}",
            )
        except Exception:
            # Clear old webhooks and retry
            for wh in await ctx.channel.webhooks():
                await wh.delete(reason="clearing unused webhooks")

            webhook = await ctx.channel.create_webhook(
                name=user.display_name,
                avatar=await user.display_avatar.read(),
                reason=f"uwulocked by {ctx.author}",
            )

        # Store in JSON
        self.data[guild_id][key] = {
            "user_id": user_id,
            "channel_id": channel_id,
            "webhook": webhook.url,
        }
        self.save_data()

        return await ctx.send(f"**Uwulocked** {user.mention}")

    # -----------------------------
    # Background task
    # -----------------------------
    @tasks.loop(seconds=3)
    async def process_uwu_queue(self):
        """Process queued uwu messages every 3 seconds."""
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

                except Exception as e:
                    print(f"Error processing uwu message: {e}")
                    self.uwu_queue[guild_id].pop(0)

                await asyncio.sleep(0.5)

        except Exception as e:
            print(f"Error in uwu queue processor: {e}")

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

        # Delete original message
        try:
            await message.delete()
        except discord.Forbidden:
            return

        # Queue uwu‑ified message
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
        # ---------------------------
        # Load safe-word filters
        # ---------------------------
        try:
            with open("blocked_words.json", "r") as f:
                filters = json.load(f)
        except Exception:
            filters = {"slurs": [], "threats": []}

        # Cute replacements for bad words
        slur_replacements = [
            "sweetie", "snugglebun", "fluffball", "cutie‑pie", "honeybee"
        ]

        threat_replacements = [
            "I need a hug…", 
            "I should calm down…", 
            "I’m feeling spicy but harmless…",
            "deep breaths…"
        ]

        # ---------------------------
        # Replace slurs safely
        # ---------------------------
        for bad in filters.get("slurs", []):
            pattern = re.compile(rf"\b{re.escape(bad)}\b", re.IGNORECASE)
            text = pattern.sub(random.choice(slur_replacements), text)

        # ---------------------------
        # Replace threats safely
        # ---------------------------
        for bad in filters.get("threats", []):
            pattern = re.compile(rf"\b{re.escape(bad)}\b", re.IGNORECASE)
            text = pattern.sub(random.choice(threat_replacements), text)

        # ---------------------------
        # Begin uwuification
        # ---------------------------
        text = text.replace("r", "w").replace("l", "w")
        text = text.replace("R", "W").replace("L", "W")

        interjections = [
            "owo", "uwu", "x3", ">w<", "^w^", "rawr~",
            "nya~", "teehee~", "(≧◡≦)", "(⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)",
            "(｡♥‿♥｡)", "(ᵘʷᵘ)", "(๑˃ᴗ˂)ﻭ"
        ]

        prefixes = [
            "uhh", "umm", "ahh", "oh~", "hehe", "teehee", "h‑hewwo"
        ]

        emojis = [
            "✨", "💖", "🥺", "👉👈", "🌸", "💞", "😳", "😼", "💗", "🌟"
        ]

        words = text.split()
        uwu_words = []

        # Optional prefix
        if random.random() < 0.35:
            uwu_words.append(random.choice(interjections))

        for w in words:
            base = w.lower()

            # Random prefix before word
            if random.random() < 0.20:
                uwu_words.append(random.choice(prefixes))

            # Random stutter
            if random.random() < 0.40:
                w = f"{w[0]}-{w}"

            # Strong stutter for emotional words
            if base in ["i", "to", "my", "we", "you"] and random.random() < 0.65:
                w = f"{w[0]}-{w}"

            # Dramatic stutter for "to"
            if base == "to" and random.random() < 0.45:
                w = f"{w[0]}-{w[0]}-{w}"

            # Cute replacements
            w = w.replace("no", "nyo")
            w = w.replace("has", "haz")
            w = w.replace("have", "haz")
            w = w.replace("you", "uu")

            uwu_words.append(w)

            # Random interjection between words
            if random.random() < 0.25:
                uwu_words.append(random.choice(interjections))

            # Random emoji between words
            if random.random() < 0.20:
                uwu_words.append(random.choice(emojis))

        return " ".join(uwu_words)

    async def cog_unload(self):
        self.process_uwu_queue.cancel()


async def setup(bot: commands.Bot):
    await bot.add_cog(UwULock(bot))