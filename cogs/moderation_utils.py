import discord
from discord.ext import commands
import json
import os
import asyncio
from datetime import datetime, timedelta

DATA_DIR = "data"
WARN_FILE = os.path.join(DATA_DIR, "warns.json")
MUTE_FILE = os.path.join(DATA_DIR, "mutes.json")
CONFIG_FILE = os.path.join(DATA_DIR, "modconfig.json")


def ensure_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    for path, default in [
        (WARN_FILE, {}),
        (MUTE_FILE, {}),
        (CONFIG_FILE, {}),
    ]:
        if not os.path.exists(path):
            with open(path, "w") as f:
                json.dump(default, f, indent=4)


def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


class ModerationUtils(commands.Cog):
    """Backend utilities for moderation and automod."""

    def __init__(self, bot):
        self.bot = bot
        ensure_files()
        self.warns = load_json(WARN_FILE, {})
        self.mutes = load_json(MUTE_FILE, {})
        self.config = load_json(CONFIG_FILE, {})
        self.bot.loop.create_task(self.mute_watcher())

    # ---------- CONFIG HELPERS ----------

    def get_guild_config(self, guild_id: int):
        gid = str(guild_id)
        if gid not in self.config:
            self.config[gid] = {
                "modlog_channel": None,
                "automod": {
                    "antispam": True,
                    "antilink": True,
                    "badwords": True,
                    "massmention": True,
                },
                "spam_threshold": 6,
                "spam_interval": 7,
                "max_mentions": 5,
                "blocked_words": [],
            }
            self.save_config()
        return self.config[gid]

    def save_config(self):
        save_json(CONFIG_FILE, self.config)

    def set_modlog_channel(self, guild_id: int, channel_id: int | None):
        cfg = self.get_guild_config(guild_id)
        cfg["modlog_channel"] = channel_id
        self.save_config()

    # ---------- LOGGING ----------

    async def log_action(self, guild: discord.Guild, title: str, description: str):
        cfg = self.get_guild_config(guild.id)
        channel_id = cfg.get("modlog_channel")
        if not channel_id:
            return
        channel = guild.get_channel(channel_id)
        if not channel:
            return
        embed = discord.Embed(title=title, description=description, color=discord.Color.red())
        embed.timestamp = discord.utils.utcnow()
        await channel.send(embed=embed)

    # ---------- WARN SYSTEM ----------

    def add_warn(self, guild_id: int, user_id: int, moderator_id: int, reason: str):
        gid = str(guild_id)
        uid = str(user_id)
        if gid not in self.warns:
            self.warns[gid] = {}
        if uid not in self.warns[gid]:
            self.warns[gid][uid] = []
        self.warns[gid][uid].append({
            "mod": moderator_id,
            "reason": reason,
            "time": datetime.utcnow().isoformat()
        })
        save_json(WARN_FILE, self.warns)

    def get_warnings(self, guild_id: int, user_id: int):
        return self.warns.get(str(guild_id), {}).get(str(user_id), [])

    def clear_warnings(self, guild_id: int, user_id: int):
        gid = str(guild_id)
        uid = str(user_id)
        if gid in self.warns and uid in self.warns[gid]:
            self.warns[gid][uid] = []
            save_json(WARN_FILE, self.warns)

    # ---------- MUTE SYSTEM ----------

    async def ensure_mute_role(self, guild: discord.Guild) -> discord.Role:
        role = discord.utils.get(guild.roles, name="Muted")
        if role:
            return role
        perms = discord.Permissions(send_messages=False, speak=False, add_reactions=False)
        role = await guild.create_role(name="Muted", permissions=perms, reason="Create mute role")
        for channel in guild.channels:
            try:
                await channel.set_permissions(role, send_messages=False, speak=False, add_reactions=False)
            except:
                continue
        return role

    async def mute_member(self, member: discord.Member, duration: int | None, reason: str | None):
        role = await self.ensure_mute_role(member.guild)
        await member.add_roles(role, reason=reason or "Muted")
        gid = str(member.guild.id)
        uid = str(member.id)
        until = None
        if duration:
            until = (datetime.utcnow() + timedelta(seconds=duration)).isoformat()
        self.mutes.setdefault(gid, {})[uid] = {
            "until": until,
            "reason": reason,
        }
        save_json(MUTE_FILE, self.mutes)

    async def unmute_member(self, member: discord.Member, reason: str | None = None):
        role = await self.ensure_mute_role(member.guild)
        await member.remove_roles(role, reason=reason or "Unmuted")
        gid = str(member.guild.id)
        uid = str(member.id)
        if gid in self.mutes and uid in self.mutes[gid]:
            del self.mutes[gid][uid]
            save_json(MUTE_FILE, self.mutes)

    async def mute_watcher(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            now = datetime.utcnow()
            changed = False
            for gid, users in list(self.mutes.items()):
                guild = self.bot.get_guild(int(gid))
                if not guild:
                    continue
                for uid, data in list(users.items()):
                    until = data.get("until")
                    if until:
                        try:
                            until_dt = datetime.fromisoformat(until)
                        except:
                            continue
                        if now >= until_dt:
                            member = guild.get_member(int(uid))
                            if member:
                                try:
                                    await self.unmute_member(member, reason="Mute expired")
                                except:
                                    pass
                            changed = True
            if changed:
                save_json(MUTE_FILE, self.mutes)
            await asyncio.sleep(15)

    # ---------- BLOCKED WORDS MANAGEMENT ----------

    def get_blocked_words(self, guild_id: int):
        cfg = self.get_guild_config(guild_id)
        return cfg.get("blocked_words", [])

    def add_blocked_word(self, guild_id: int, word: str):
        cfg = self.get_guild_config(guild_id)
        if "blocked_words" not in cfg:
            cfg["blocked_words"] = []
        w = word.lower()
        if w not in cfg["blocked_words"]:
            cfg["blocked_words"].append(w)
        self.save_config()

    def remove_blocked_word(self, guild_id: int, word: str):
        cfg = self.get_guild_config(guild_id)
        w = word.lower()
        if "blocked_words" in cfg and w in cfg["blocked_words"]:
            cfg["blocked_words"].remove(w)
        self.save_config()

    def clear_blocked_words(self, guild_id: int):
        cfg = self.get_guild_config(guild_id)
        cfg["blocked_words"] = []
        self.save_config()

    def contains_blocked_word(self, guild_id: int, content: str):
        cfg = self.get_guild_config(guild_id)
        words = cfg.get("blocked_words", [])
        lowered = content.lower()
        return any(w in lowered for w in words)


async def setup(bot):
    await bot.add_cog(ModerationUtils(bot))