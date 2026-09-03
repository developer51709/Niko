import discord
from discord.ext import commands
import json
import os
import asyncio
from datetime import datetime, timedelta, timezone

DATA_DIR = "data"
CONFIG_FILE = os.path.join(DATA_DIR, "modconfig.json")

# Moderation/automod config is stored in the main database (moderation_config),
# migrated at startup from the legacy modconfig.json by events.startup.database.
_MOD_COLLECTION = "moderation_config"


def _pool():
    import database as database_module
    return getattr(database_module, "_shared_pool", None)


async def _load_all_moderation_configs() -> dict:
    """Load every guild's moderation config from the database."""
    pool = _pool()
    configs: dict = {}
    if pool is None:
        return configs
    try:
        if pool.db_type == "mongodb":
            async for doc in pool.collection(_MOD_COLLECTION).find({}):
                gid = doc.get("guild_id")
                if gid is None:
                    try:
                        gid = int(str(doc.get("_id")))
                    except (TypeError, ValueError):
                        continue
                raw = {k: v for k, v in doc.items() if k not in ("_id", "guild_id")}
                if isinstance(raw, str):
                    try:
                        raw = json.loads(raw)
                    except Exception:
                        raw = {}
                if isinstance(raw, dict) and raw:
                    configs[str(gid)] = raw
        else:
            rows = await pool.fetch("SELECT guild_id, data FROM moderation_config")
            for row in rows:
                try:
                    raw = row["data"]
                    if isinstance(raw, str):
                        raw = json.loads(raw)
                    if isinstance(raw, dict) and raw:
                        configs[str(row["guild_id"])] = raw
                except Exception:
                    continue
    except Exception as e:
        from utils import logging
        logging.warning("Moderation", f"Failed to load moderation configs: {e}")
    return configs


async def _save_guild_moderation_config(guild_id: int, cfg: dict):
    """Persist one guild's moderation config to the database."""
    pool = _pool()
    if pool is None:
        raise RuntimeError("Database pool is not available.")
    payload = json.dumps(cfg)
    if pool.db_type == "mongodb":
        await pool.collection(_MOD_COLLECTION).replace_one(
            {"_id": str(guild_id)},
            {"_id": str(guild_id), "guild_id": int(guild_id), **json.loads(payload)},
            upsert=True,
        )
    else:
        await pool.execute(
            "INSERT OR REPLACE INTO moderation_config (guild_id, data) VALUES ($1, $2)",
            int(guild_id), payload,
        )

DEFAULT_GUILD_CONFIG = {
    "automod": {
        "antispam":     False,
        "antilink":     False,
        "badwords":     True,
        "massmention":  False,
        "antinuke":     False,
        "antiraid":     False,
        "antiraid_ext": False,
    },
    "spam_threshold": 6,
    "spam_interval": 7,
    "max_mentions": 5,
    "blocked_words": [],
    "whitelist_users": [],
    "whitelist_roles": [],
    "antinuke": {
        "ban_threshold": 3,
        "kick_threshold": 3,
        "channel_delete_threshold": 3,
        "role_delete_threshold": 3,
        "interval": 10,
        "action": "strip",
    },
    "antiraid": {
        "join_threshold": 10,
        "join_interval": 10,
        "action": "kick",
    },
    "antiraid_ext": {
        "interaction_threshold": 5,
        "interaction_window": 30,
        "join_age_limit": 120,
        "raider_action": "kick",
        "operator_action": "notify",
        "ext_app_detection": True,
        "ext_app_threshold": 3,
        "ext_app_window": 15,
        "ext_app_action": "kick",
    },
}


def ensure_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({}, f, indent=4)


def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def _migrate_guild_config(cfg: dict) -> dict:
    """Ensure all required keys exist, adding defaults for new fields."""
    am = cfg.setdefault("automod", {})
    for key, val in DEFAULT_GUILD_CONFIG["automod"].items():
        am.setdefault(key, val)

    for key in ("spam_threshold", "spam_interval", "max_mentions", "blocked_words",
                "whitelist_users", "whitelist_roles"):
        cfg.setdefault(key, DEFAULT_GUILD_CONFIG[key])

    cfg.setdefault("antinuke", dict(DEFAULT_GUILD_CONFIG["antinuke"]))
    for k, v in DEFAULT_GUILD_CONFIG["antinuke"].items():
        cfg["antinuke"].setdefault(k, v)

    cfg.setdefault("antiraid", dict(DEFAULT_GUILD_CONFIG["antiraid"]))
    for k, v in DEFAULT_GUILD_CONFIG["antiraid"].items():
        cfg["antiraid"].setdefault(k, v)

    cfg.setdefault("antiraid_ext", dict(DEFAULT_GUILD_CONFIG["antiraid_ext"]))
    for k, v in DEFAULT_GUILD_CONFIG["antiraid_ext"].items():
        cfg["antiraid_ext"].setdefault(k, v)

    return cfg


class ModerationUtils(commands.Cog):
    """Backend utilities for moderation and automod."""

    def __init__(self, bot):
        self.bot = bot
        ensure_files()
        self.config: dict = {}
        self.bot.loop.create_task(self._load_config_task())
        self.bot.loop.create_task(self.mute_watcher())

    async def _load_config_task(self):
        """Populate the moderation config from the database once ready."""
        self.config = await _load_all_moderation_configs()

    # ---------- CONFIG HELPERS ----------

    def get_guild_config(self, guild_id: int) -> dict:
        gid = str(guild_id)
        if gid not in self.config:
            import copy
            self.config[gid] = copy.deepcopy(DEFAULT_GUILD_CONFIG)
            self.save_config()
        else:
            _migrate_guild_config(self.config[gid])
        return self.config[gid]

    def get_mod_config(self, guild_id: int) -> dict:
        return self.get_guild_config(guild_id)

    def save_mod_config(self):
        self.save_config()

    def save_config(self, guild_id: int | None = None):
        """Write the config cache through to the database (fire-and-forget).

        Pass guild_id to persist one guild, or omit to persist every cached
        guild. Safe to call from the bot loop or from Flask worker threads.
        """
        targets = [guild_id] if guild_id is not None else [
            int(gid) for gid in self.config if str(gid).isdigit()
        ]
        if not targets:
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        for gid in targets:
            coro = self._persist_config(gid)
            if loop is not None and not loop.is_closed():
                loop.create_task(coro)
            else:
                bot_loop = self.bot.loop
                if bot_loop is not None and not bot_loop.is_closed():
                    asyncio.run_coroutine_threadsafe(coro, bot_loop)
                else:
                    coro.close()

    async def _persist_config(self, guild_id: int):
        cfg = self.config.get(str(guild_id))
        if cfg is None:
            return
        try:
            await _save_guild_moderation_config(guild_id, cfg)
        except Exception as e:
            from utils import logging
            logging.error("Moderation", f"Failed to persist moderation config: {e}")

    # ---------- MODLOG ----------

    async def log_action(
        self,
        guild: discord.Guild,
        title: str,
        description: str,
        target: discord.Member | discord.User | None = None,
        moderator: discord.Member | None = None,
    ):
        """Delegate to the ServerLogger cog for structured, categorised logging."""
        logger = self.bot.get_cog("ServerLogger")
        if logger:
            await logger.log_action(guild, title, description, target=target, moderator=moderator)

    # ---------- WARN SYSTEM (DATABASE) ----------

    async def add_warn(self, guild_id: int, user_id: int, moderator_id: int, reason: str):
        """Insert a warning into the database."""
        pool = _pool()
        if pool is None:
            return
        try:
            if pool.db_type == "mongodb":
                await pool.collection("warns").insert_one({
                    "guild_id": guild_id,
                    "user_id": user_id,
                    "moderator_id": moderator_id,
                    "reason": reason,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                })
            else:
                await pool.execute(
                    "INSERT INTO warns (guild_id, user_id, moderator_id, reason, created_at) "
                    "VALUES ($1, $2, $3, $4, $5)",
                    guild_id, user_id, moderator_id, reason,
                    datetime.now(timezone.utc).isoformat(),
                )
        except Exception as e:
            from utils import logging
            logging.error("Moderation", f"Failed to add warn for {user_id} in {guild_id}: {e}")

    async def get_warnings(self, guild_id: int, user_id: int) -> list:
        """Fetch all warnings for a user in a guild from the database."""
        pool = _pool()
        if pool is None:
            return []
        try:
            if pool.db_type == "mongodb":
                results = []
                async for doc in pool.collection("warns").find(
                    {"guild_id": guild_id, "user_id": user_id}
                ):
                    results.append({
                        "mod": doc.get("moderator_id", 0),
                        "reason": doc.get("reason", ""),
                        "time": doc.get("created_at", ""),
                    })
                return results
            else:
                rows = await pool.fetch(
                    "SELECT moderator_id, reason, created_at FROM warns "
                    "WHERE guild_id = $1 AND user_id = $2 "
                    "ORDER BY id ASC",
                    guild_id, user_id,
                )
                return [
                    {"mod": row["moderator_id"], "reason": row["reason"], "time": row["created_at"]}
                    for row in rows
                ]
        except Exception as e:
            from utils import logging
            logging.error("Moderation", f"Failed to get warnings for {user_id} in {guild_id}: {e}")
            return []

    async def clear_warnings(self, guild_id: int, user_id: int):
        """Delete all warnings for a user in a guild from the database."""
        pool = _pool()
        if pool is None:
            return
        try:
            if pool.db_type == "mongodb":
                await pool.collection("warns").delete_many(
                    {"guild_id": guild_id, "user_id": user_id}
                )
            else:
                await pool.execute(
                    "DELETE FROM warns WHERE guild_id = $1 AND user_id = $2",
                    guild_id, user_id,
                )
        except Exception as e:
            from utils import logging
            logging.error("Moderation", f"Failed to clear warnings for {user_id} in {guild_id}: {e}")

    # ---------- MUTE SYSTEM (DATABASE) ----------

    async def ensure_mute_role(self, guild: discord.Guild, *, verify_perms: bool = False) -> discord.Role:
        role = discord.utils.get(guild.roles, name="Muted")
        created = False
        if not role:
            perms = discord.Permissions(send_messages=False, speak=False, add_reactions=False)
            role = await guild.create_role(name="Muted", permissions=perms, reason="Create mute role")
            created = True
        if created or verify_perms:
            for channel in guild.channels:
                try:
                    await channel.set_permissions(
                        role,
                        send_messages=False,
                        speak=False,
                        add_reactions=False,
                        use_application_commands=False,
                        use_external_apps=False,
                        reason="Verify mute role permissions",
                    )
                except Exception:
                    continue
        return role

    async def mute_member(self, guild: discord.Guild, member: discord.Member, duration=None, reason=None):
        role = await self.ensure_mute_role(guild)
        try:
            await member.add_roles(role, reason=reason or "Muted")
        except Exception:
            try:
                member = guild.get_member(member.id)
                await member.add_roles(role, reason=reason or "Muted")
            except Exception:
                pass

        until = None
        if duration:
            until = (datetime.now(timezone.utc) + timedelta(seconds=duration)).isoformat()

        pool = _pool()
        if pool is not None:
            try:
                if pool.db_type == "mongodb":
                    await pool.collection("mutes").insert_one({
                        "guild_id": guild.id,
                        "user_id": member.id,
                        "reason": reason,
                        "until": until,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    })
                else:
                    await pool.execute(
                        "INSERT INTO mutes (guild_id, user_id, reason, until) "
                        "VALUES ($1, $2, $3, $4)",
                        guild.id, member.id, reason, until,
                    )
            except Exception as e:
                from utils import logging
                logging.error("Moderation", f"Failed to save mute for {member.id}: {e}")

    async def unmute_member(self, member: discord.Member, reason=None):
        role = await self.ensure_mute_role(member.guild)
        await member.remove_roles(role, reason=reason or "Unmuted")

        pool = _pool()
        if pool is not None:
            try:
                if pool.db_type == "mongodb":
                    await pool.collection("mutes").delete_many({
                        "guild_id": member.guild.id,
                        "user_id": member.id,
                    })
                else:
                    await pool.execute(
                        "DELETE FROM mutes WHERE guild_id = $1 AND user_id = $2",
                        member.guild.id, member.id,
                    )
            except Exception as e:
                from utils import logging
                logging.error("Moderation", f"Failed to remove mute for {member.id}: {e}")

    async def mute_watcher(self):
        """Periodically check for expired mutes and unmute users."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            now = datetime.now(timezone.utc)
            pool = _pool()
            if pool is not None:
                try:
                    if pool.db_type == "mongodb":
                        expired = []
                        async for doc in pool.collection("mutes").find({"until": {"$ne": None}}):
                            until_str = doc.get("until")
                            if until_str:
                                try:
                                    until_dt = datetime.fromisoformat(until_str)
                                except Exception:
                                    continue
                                if now >= until_dt:
                                    expired.append(doc)
                        for doc in expired:
                            guild = self.bot.get_guild(int(doc["guild_id"]))
                            if not guild:
                                continue
                            member = guild.get_member(int(doc["user_id"]))
                            if member:
                                try:
                                    await self.unmute_member(member, reason="Mute expired")
                                except Exception:
                                    pass
                    else:
                        rows = await pool.fetch(
                            "SELECT id, guild_id, user_id, until FROM mutes WHERE until IS NOT NULL"
                        )
                        for row in rows:
                            try:
                                until_dt = datetime.fromisoformat(row["until"])
                            except Exception:
                                continue
                            if now >= until_dt:
                                guild = self.bot.get_guild(int(row["guild_id"]))
                                if not guild:
                                    continue
                                member = guild.get_member(int(row["user_id"]))
                                if member:
                                    try:
                                        await self.unmute_member(member, reason="Mute expired")
                                    except Exception:
                                        pass
                except Exception as e:
                    from utils import logging
                    logging.error("Moderation", f"Mute watcher error: {e}")
            await asyncio.sleep(15)

    # ---------- BLOCKED WORDS ----------

    def get_blocked_words(self, guild_id: int):
        return self.get_guild_config(guild_id).get("blocked_words", [])

    def add_blocked_word(self, guild_id: int, word: str):
        cfg = self.get_guild_config(guild_id)
        w = word.lower()
        cfg["blocked_words"] = list(cfg.get("blocked_words", []))
        if w not in cfg["blocked_words"]:
            cfg["blocked_words"].append(w)
        self.save_config()

    def remove_blocked_word(self, guild_id: int, word: str):
        cfg = self.get_guild_config(guild_id)
        w = word.lower()
        if w in cfg.get("blocked_words", []):
            cfg["blocked_words"].remove(w)
        self.save_config()

    def clear_blocked_words(self, guild_id: int):
        self.get_guild_config(guild_id)["blocked_words"] = []
        self.save_config()

    def contains_blocked_word(self, guild_id: int, content: str):
        words = self.get_guild_config(guild_id).get("blocked_words", [])
        lowered = content.lower()
        return any(w in lowered for w in words)

    # ---------- WHITELIST ----------

    def is_whitelisted(self, guild_id: int, member) -> bool:
        """Return True if member is on the automod whitelist (by user ID or role)."""
        cfg = self.get_guild_config(guild_id)
        if member.id in cfg.get("whitelist_users", []):
            return True
        roles = getattr(member, "roles", [])
        member_role_ids = {r.id for r in roles}
        for rid in cfg.get("whitelist_roles", []):
            if rid in member_role_ids:
                return True
        return False

    def add_whitelist_user(self, guild_id: int, user_id: int):
        cfg = self.get_guild_config(guild_id)
        wl = cfg.setdefault("whitelist_users", [])
        if user_id not in wl:
            wl.append(user_id)
        self.save_config()

    def remove_whitelist_user(self, guild_id: int, user_id: int):
        cfg = self.get_guild_config(guild_id)
        wl = cfg.get("whitelist_users", [])
        if user_id in wl:
            wl.remove(user_id)
        self.save_config()

    def add_whitelist_role(self, guild_id: int, role_id: int):
        cfg = self.get_guild_config(guild_id)
        wl = cfg.setdefault("whitelist_roles", [])
        if role_id not in wl:
            wl.append(role_id)
        self.save_config()

    def remove_whitelist_role(self, guild_id: int, role_id: int):
        cfg = self.get_guild_config(guild_id)
        wl = cfg.get("whitelist_roles", [])
        if role_id in wl:
            wl.remove(role_id)
        self.save_config()

    def get_whitelist(self, guild_id: int) -> dict:
        cfg = self.get_guild_config(guild_id)
        return {
            "users": cfg.get("whitelist_users", []),
            "roles": cfg.get("whitelist_roles", []),
        }


async def setup(bot):
    await bot.add_cog(ModerationUtils(bot))
