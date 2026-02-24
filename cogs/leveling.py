# leveling.py
# Fully rewritten to match the music cog’s personality + language system
# Includes bilingual EN/DE support, café personality, clean embeds, and future expansion.

import discord
from discord.ext import commands
import random
import json
import os
from utils import logging as log

# personality mode: "normal" or "cafe"
PERSONALITY = "cafe"

# -----------------------------
# MESSAGE DICTIONARY
# -----------------------------
MESSAGES = {
    "normal": {
        "en": {
            "level_up": "Congratulations {mention}, you leveled up to level **{level}**!",
            "no_xp": "{name} hasn't earned any XP yet.",
            "stats_title": "Level Stats — {name}",
            "stats_level": "Level",
            "stats_xp": "XP",
            "stats_rank": "Rank",
            "leaderboard_title": "Leveling Leaderboard — {guild}",
            "leaderboard_empty": "No one has earned any XP in this server yet.",
        },
        "de": {
            "level_up": "Glückwunsch {mention}, du bist auf Level **{level}** aufgestiegen!",
            "no_xp": "{name} hat noch keine XP gesammelt.",
            "stats_title": "Level-Statistiken — {name}",
            "stats_level": "Level",
            "stats_xp": "XP",
            "stats_rank": "Rang",
            "leaderboard_title": "Leveling-Bestenliste — {guild}",
            "leaderboard_empty": "Noch niemand hat XP auf diesem Server gesammelt.",
        },
    },

    "cafe": {
        "en": {
            "level_up": "omg {mention}, you leveled up to **{level}** — look at you growing like a lil coffee bean ☕🌱",
            "no_xp": "{name} hasn’t brewed any XP yet ☕😔",
            "stats_title": "☕ cozy level stats for {name}",
            "stats_level": "vibe‑level",
            "stats_xp": "xp brewed",
            "stats_rank": "café rank",
            "leaderboard_title": "☕ cozy leaderboard — {guild}",
            "leaderboard_empty": "no one has brewed any xp in this café yet 😭",
        },
        "de": {
            "level_up": "omg {mention}, du bist auf **{level}** gestiegen — wie eine kleine kaffeebohne die wächst ☕🌱",
            "no_xp": "{name} hat noch keine XP aufgebrüht ☕😔",
            "stats_title": "☕ gemütliche level‑statistiken für {name}",
            "stats_level": "vibe‑level",
            "stats_xp": "aufgebrühte xp",
            "stats_rank": "café‑rang",
            "leaderboard_title": "☕ gemütliche bestenliste — {guild}",
            "leaderboard_empty": "niemand hat hier bisher xp aufgebrüht 😭",
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

    # try personality + lang
    block = MESSAGES.get(personality, {}).get(lang, {})
    text = block.get(key)

    # fallback personality + en
    if text is None:
        text = MESSAGES.get(personality, {}).get("en", {}).get(key)

    # fallback normal + lang
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key)

    # fallback normal + en
    if text is None:
        text = MESSAGES["normal"]["en"].get(key, key)

    return text.format(**kwargs) if kwargs else text


# -----------------------------
# LEVELING COG
# -----------------------------
class Leveling(commands.Cog):
    """Cozy bilingual leveling system with personality support."""

    def __init__(self, bot):
        self.bot = bot
        self.data_path = "data/levels.json"
        self.levels = self.load_levels()

    def load_levels(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                return json.load(f)
        return {}

    def save_levels(self):
        with open(self.data_path, "w") as f:
            json.dump(self.levels, f, indent=4)

    def get_xp_for_level(self, level):
        return 5 * (level ** 2) + (50 * level) + 100

    # -----------------------------
    # XP GAIN + LEVEL UP
    # -----------------------------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        guild_id = str(message.guild.id)
        user_id = str(message.author.id)

        if guild_id not in self.levels:
            self.levels[guild_id] = {}

        if user_id not in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {"xp": 0, "level": 0}

        # Add random XP
        xp_gain = random.randint(15, 25)
        self.levels[guild_id][user_id]["xp"] += xp_gain

        current_xp = self.levels[guild_id][user_id]["xp"]
        current_level = self.levels[guild_id][user_id]["level"]
        next_level_xp = self.get_xp_for_level(current_level)

        if current_xp >= next_level_xp:
            self.levels[guild_id][user_id]["level"] += 1
            self.levels[guild_id][user_id]["xp"] = 0
            new_level = self.levels[guild_id][user_id]["level"]

            try:
                await message.channel.send(
                    msg(message, "level_up", mention=message.author.mention, level=new_level)
                )
                log.info("Leveling", f"User {message.author} leveled up to {new_level} in {message.guild.name}")
            except discord.Forbidden:
                pass

        self.save_levels()

    # -----------------------------
    # LEVEL COMMAND
    # -----------------------------
    @commands.command(
        name="level",
        aliases=["rank"],
        help="check your cozy level stats ☕ | zeigt deine level‑statistiken"
    )
    async def level(self, ctx, member: discord.Member = None):
        """Check your current level and XP."""
        member = member or ctx.author
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id not in self.levels or user_id not in self.levels[guild_id]:
            return await ctx.send(msg(ctx, "no_xp", name=member.display_name))

        user_data = self.levels[guild_id][user_id]
        current_level = user_data["level"]
        current_xp = user_data["xp"]
        next_level_xp = self.get_xp_for_level(current_level)

        # rank calculation
        sorted_users = sorted(
            self.levels[guild_id].items(),
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            reverse=True
        )
        rank = 1
        for uid, _ in sorted_users:
            if uid == user_id:
                break
            rank += 1

        # embed styling based on personality
        personality = get_personality()
        lang = get_lang(ctx)

        title = msg(ctx, "stats_title", name=member.display_name)
        embed = discord.Embed(
            title=title,
            color=discord.Color.gold() if personality == "cafe" else discord.Color.blue()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name=msg(ctx, "stats_level"), value=str(current_level), inline=True)
        embed.add_field(name=msg(ctx, "stats_xp"), value=f"{current_xp}/{next_level_xp}", inline=True)
        embed.add_field(name=msg(ctx, "stats_rank"), value=f"#{rank}", inline=True)

        await ctx.send(embed=embed)

    # -----------------------------
    # LEADERBOARD COMMAND
    # -----------------------------
    @commands.command(
        name="level-leaderboard",
        aliases=["lvl-lb"],
        help="view the cozy leaderboard ☕ | zeigt die level‑bestenliste"
    )
    async def leaderboard(self, ctx):
        """View the leveling leaderboard."""
        guild_id = str(ctx.guild.id)

        if guild_id not in self.levels or not self.levels[guild_id]:
            return await ctx.send(msg(ctx, "leaderboard_empty"))

        sorted_users = sorted(
            self.levels[guild_id].items(),
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            reverse=True
        )

        title = msg(ctx, "leaderboard_title", guild=ctx.guild.name)
        personality = get_personality()

        embed = discord.Embed(
            title=title,
            color=discord.Color.gold() if personality == "cafe" else discord.Color.blue()
        )

        description = ""
        for i, (user_id, data) in enumerate(sorted_users[:10], start=1):
            user = self.bot.get_user(int(user_id))
            name = user.display_name if user else f"User {user_id}"
            description += f"**{i}. {name}** — Level {data['level']} ({data['xp']} XP)\n"

        embed.description = description
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Leveling(bot))