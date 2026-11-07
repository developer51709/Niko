import discord
from discord.ext import commands
import json
import os
import re
import secrets
import time
import asyncio
import unicodedata
from datetime import datetime, timedelta, timezone

from ._presets import (
    PRESETS_BY_KEY,
    PRESET_KEYS,
    build_preset_regex,
    normalize_presets,
    preset_catalog,
)

DATA_DIR = "data"
CONFIG_FILE = os.path.join(DATA_DIR, "modconfig.json")

# Moderation/automod config is stored in the main database (moderation_config),
# migrated at startup from the legacy modconfig.json by events.startup.database.
_MOD_COLLECTION = "moderation_config"

#: Discord refuses a timeout longer than 28 days, so this is the longest a mute
#: can run. A regular mute records it as the expiry; the watcher then logs the
#: expiry with a button to reapply the mute.
_MAX_TIMEOUT_SECONDS = 28 * 24 * 60 * 60

#: How long after the bot writes a mute role or timeout its own gateway events
#: are still recognised as its own, so a moderator's audit entry is not confused
#: with the bot answering itself.
_SELF_WRITE_TTL = 8.0

#: The name the bot gives a mute role it has to create. Only used to recognise
#: the role it is provisioning; an existing role is found by its pinned id.
MUTE_ROLE_NAME = "Muted"

#: How long a mute role's channel deny is still recognised as this bot's own
#: write. The deny is written channel by channel, and each channel's gateway
#: event has to be told apart from a moderator editing the same overwrite.
_OVERWRITE_WRITE_TTL = 6.0


def _parse_mute_until(value):
    """A stored mute expiry as an aware datetime, or ``None``."""
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value))
        except (TypeError, ValueError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed



def _pool():
    import database as database_module
    return getattr(database_module, "_shared_pool", None)


def _warn_row(row) -> dict:
    return {
        "id": int(row["id"]),
        "guild_id": str(row["guild_id"]),
        "user_id": str(row["user_id"]),
        "moderator_id": str(row["moderator_id"]),
        "reason": str(row["reason"] or ""),
        "created_at": str(row["created_at"] or ""),
    }


def _publish_warn_event(event_type: str, guild_id: int, data: dict) -> None:
    """Fan out a warning event without ever failing the database operation."""
    try:
        from webapp.developer.webhooks import dispatch_guild_event

        dispatch_guild_event(event_type, str(guild_id), data)
    except Exception as error:
        from utils import logging
        logging.warning("Moderation", f"Could not queue {event_type} webhook: {error}")


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
        "antispam":          False,
        "antilink":          False,
        "badwords":          True,
        "massmention":       False,
        "scam_image_filter": False,
        "nsfw_image_filter": False,
        "antinuke":          False,
        "antiraid":          False,
        "antiraid_ext":      False,
    },
    "spam_threshold": 6,
    "spam_interval": 7,
    "max_mentions": 5,
    "blocked_words": [],
    # Curated regex filters (see cogs/moderation/_presets.py) switched on for
    # this server, by key. They catch the leet, spaced-out and look-alike
    # spellings that a plain keyword entry cannot.
    "badwords_presets": [],
    # What happens to a message that trips the blocked-word filter: "delete"
    # removes it, "censor" reposts it through a webhook as the author with the
    # matching words replaced by ``badwords_mask``.
    "badwords_action": "delete",
    "badwords_mask": "*",
    "whitelist_users": [],
    "whitelist_roles": [],
    # The role this guild's mutes use, pinned the first time one is handed out.
    # Storing the id keeps a role that merely happens to be called "Muted" from
    # being adopted — and having its channel permissions rewritten — later on.
    "mute_role_id": None,
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
    # if not os.path.exists(CONFIG_FILE):
    #     with open(CONFIG_FILE, "w") as f:
    #         json.dump({}, f, indent=4)


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
                "badwords_presets", "badwords_action", "badwords_mask",
                "whitelist_users", "whitelist_roles", "mute_role_id"):
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


# ---------- BLOCKED WORDS ----------
# Entries follow Discord's keyword rules: a plain word matches whole words only,
# a trailing "*" also matches longer words starting with it ("fuck*" catches
# "fucking"), and a leading "*" drops the word-start requirement ("*ass*"
# matches anywhere). Substring matching used to delete innocent messages
# (blocking "ass" removed "class", "grass" and "assistant") while spaced-out or
# punctuated words slipped straight through. Discord's own limits are 1000 terms
# of up to 60 characters each.
MAX_BLOCKED_WORDS = 1000
MAX_BLOCKED_WORD_LENGTH = 60
MAX_BADWORDS_MASK_LENGTH = 16
BADWORDS_ACTIONS = ("delete", "censor")
DEFAULT_BADWORDS_ACTION = "delete"
DEFAULT_BADWORDS_MASK = "*"
MAX_CACHED_GUILD_PATTERNS = 64
_ZERO_WIDTH_CHARS = ("\u200b", "\u200c", "\u200d", "\u2060", "\ufeff")
# At most three separator characters may sit between two letters: enough for
# "a.s.s" or "a s s", without letting a stray letter match one much further on.
_MAX_INNER_SEPARATORS = 3


def normalize_blocked_word(word) -> str | None:
    """Lowercase/strip a blocked word, or None when nothing usable is left.

    Returning None for blanks matters: an empty string in the list matches every
    message, which would delete every message in the server.
    """
    if not isinstance(word, str):
        return None
    cleaned = " ".join(unicodedata.normalize("NFKC", word).strip().lower().split())
    if not cleaned or len(cleaned) > MAX_BLOCKED_WORD_LENGTH:
        return None
    return cleaned


def normalize_badwords_action(value) -> str:
    """The configured blocked-word response, defaulting to a plain delete."""
    text = str(value if value is not None else "").strip().lower()
    return text if text in BADWORDS_ACTIONS else DEFAULT_BADWORDS_ACTION


def normalize_badwords_mask(value) -> str:
    """The text that replaces a blocked word in a censored message.

    ``None`` keeps the default; an explicitly blank mask removes the word
    entirely. A one-character mask is repeated to cover the whole match, so a
    censored word keeps its shape.
    """
    if value is None:
        return DEFAULT_BADWORDS_MASK
    return " ".join(str(value).split())[:MAX_BADWORDS_MASK_LENGTH]


def normalize_message_content(content: str) -> str:
    """Fold away the tricks used to smuggle a filtered word past matching."""
    text = unicodedata.normalize("NFKC", content)
    for char in _ZERO_WIDTH_CHARS:
        if char in text:
            text = text.replace(char, "")
    return text


def _blocked_word_alternative(word: str) -> str | None:
    """One regex alternative for a blocked entry, following Discord's rules.

    Separators between letters are tolerated, so "a.s.s" and "a s s" are caught
    even though the entry is just "ass".
    """
    matches_anywhere = word.startswith("*")
    prefix_match = word.endswith("*")
    tokens = [token for token in re.split(r"[\W_]+", word.strip("*")) if token]
    if not tokens:
        return None
    gap = r"[\W_]{0,%d}" % _MAX_INNER_SEPARATORS
    spaced = [gap.join(re.escape(char) for char in token) for token in tokens]
    source = r"[\W_]+".join(spaced)
    if prefix_match:
        source += r"\w*"
    start = "" if matches_anywhere else r"(?<!\w)"
    return start + r"(?:" + source + r")(?!\w)"


def build_blocked_word_regex(words):
    """Compile blocked words into one case-insensitive pattern."""
    alternatives = []
    for entry in words if isinstance(words, (list, tuple, set)) else ():
        normalized = normalize_blocked_word(entry)
        if not normalized:
            continue
        alternative = _blocked_word_alternative(normalized)
        if alternative:
            alternatives.append(alternative)
    if not alternatives:
        return None
    return re.compile("|".join(alternatives), re.IGNORECASE)


def _mask_substitution(replacement: str):
    """A regex replacement callable that applies the censor mask.

    A one-character mask is repeated to cover the match, so a censored word
    keeps the shape it had; anything longer replaces the whole match.
    """
    if len(replacement) == 1:
        return lambda match: replacement * max(1, len(match.group(0)))
    # A replacement function (rather than a template string) keeps backslashes
    # in the mask literal instead of being read as regex escapes.
    return lambda match: replacement


class ModerationUtils(commands.Cog):
    """Backend utilities for moderation and automod."""

    def __init__(self, bot):
        self.bot = bot
        ensure_files()
        self.config: dict = {}
        # Guild IDs whose config was created in-memory before the initial
        # database load finished; reconciled once the load completes.
        self._stale_entries: set = set()
        # Blocked-word regexes keyed by the guild's word tuple, so the filter
        # does not recompile a pattern for every message.
        self._blocked_patterns: dict = {}
        # Gate for the initial database load. Until it completes, new guild
        # entries must NOT be persisted — otherwise a message arriving before
        # the load finishes would write DEFAULT_GUILD_CONFIG over the real
        # stored config and every toggle would "reset" on next restart.
        self._initial_load_done = asyncio.Event()
        # (guild_id, user_id) -> monotonic time of a role/timeout write this bot
        # just made. The logging cog reads it so its own changes are not treated
        # as a moderator muting or unmuting the member a second time.
        self._self_writes: dict = {}
        self.bot.loop.create_task(self._load_config_task())
        self.bot.loop.create_task(self.mute_watcher())

    async def _load_config_task(self):
        """Populate the moderation config from the database once ready."""
        try:
            loaded = await _load_all_moderation_configs()
            # Merge instead of replace: guilds created in the meantime keep
            # their in-memory state, everything else comes from the database.
            for gid, cfg in loaded.items():
                self.config.setdefault(gid, cfg)
            # Reconcile entries created before the load finished: replace the
            # placeholder defaults with the real stored config when one exists.
            for gid in list(self._stale_entries):
                stored = loaded.get(gid)
                if isinstance(stored, dict) and stored:
                    self.config[gid] = stored
                _migrate_guild_config(self.config[gid])
            self._stale_entries.clear()
        finally:
            self._initial_load_done.set()

    def _mark_stale_entry(self, gid: str):
        """Track cache entries created before the initial DB load finished.

        Their DB-backed state is unknown, so they are re-merged from the
        database once the load completes instead of being trusted as-is.
        """
        self._stale_entries.add(gid)

    # ---------- CONFIG HELPERS ----------

    def get_guild_config(self, guild_id: int) -> dict:
        gid = str(guild_id)
        if gid not in self.config:
            import copy
            self.config[gid] = copy.deepcopy(DEFAULT_GUILD_CONFIG)
            if not self._initial_load_done.is_set():
                # The database may still contain real settings for this guild
                # that haven't been read yet — do NOT persist defaults now.
                self._mark_stale_entry(gid)
            else:
                self.save_config(guild_id)
        else:
            _migrate_guild_config(self.config[gid])

        return self.config[gid]

    def get_mod_config(self, guild_id: int) -> dict:
        return self.get_guild_config(guild_id)

    def save_mod_config(self):
        self.save_config()

    def save_config(self, guild_id: int | None = None):
        """Write the config cache through to the database (fire-and-forget).

        Pass guild_id to persist the guild that was just edited. Omitting it
        persists *every* cached guild, which is a deliberate bulk write for
        migrations and the dashboard — never for a single settings change, since
        one toggle would then rewrite the config of every guild the bot is in.
        Safe to call from the bot loop or from Flask worker threads.
        """
        targets = [guild_id] if guild_id is not None else [
            int(gid) for gid in self.config
            if str(gid).isdigit() and str(gid) not in self._stale_entries
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
        display_title: str | None = None,
    ):
        """Delegate to the ServerLogger cog for structured, categorised logging.

        ``display_title`` is the translated heading; ``title`` stays the
        English key that picks the log category.
        """
        logger = self.bot.get_cog("ServerLogger")
        if logger:
            await logger.log_action(
                guild, title, description,
                target=target, moderator=moderator, display_title=display_title,
            )

    # ---------- WARN SYSTEM (DATABASE) ----------

    async def add_warn(self, guild_id: int, user_id: int, moderator_id: int, reason: str):
        """Insert a warning and return its API representation.

        The explicit id matters on both backends: SQLite normally allocates it,
        while the MongoDB adapter needs the primary key before it can store a
        document. It also lets the created event carry a stable id that a bot
        can use to reconcile the warning later.
        """
        pool = _pool()
        if pool is None:
            return None
        warn_id = secrets.randbits(48) or 1
        created_at = datetime.now(timezone.utc).isoformat()
        record = {
            "id": warn_id,
            "guild_id": int(guild_id),
            "user_id": int(user_id),
            "moderator_id": int(moderator_id),
            "reason": str(reason or ""),
            "created_at": created_at,
        }
        try:
            await pool.execute(
                "INSERT INTO warns (id, guild_id, user_id, moderator_id, reason, created_at) "
                "VALUES ($1, $2, $3, $4, $5, $6)",
                warn_id, int(guild_id), int(user_id), int(moderator_id),
                str(reason or ""), created_at,
            )
        except Exception as e:
            from utils import logging
            logging.error("Moderation", f"Failed to add warn for {user_id} in {guild_id}: {e}")
            return None
        _publish_warn_event("warn.created", guild_id, {"warn": record})
        return record

    async def list_warnings(
        self,
        guild_id: int,
        *,
        user_id: int | None = None,
        offset: int = 0,
        limit: int = 100,
    ):
        """Read warning cases for a guild, optionally filtered to one member."""
        pool = _pool()
        if pool is None:
            return None, 0
        offset = max(0, int(offset))
        limit = max(1, min(int(limit), 500))
        where = "guild_id = $1"
        args = [int(guild_id)]
        if user_id is not None:
            where += " AND user_id = $2"
            args.append(int(user_id))
        try:
            total = int(await pool.fetchval(f"SELECT COUNT(*) FROM warns WHERE {where}", *args) or 0)
            rows = await pool.fetch(
                "SELECT id, guild_id, user_id, moderator_id, reason, created_at "
                f"FROM warns WHERE {where} ORDER BY id ASC LIMIT ? OFFSET ?",
                *args, limit, offset,
            )
        except Exception as e:
            from utils import logging
            logging.error("Moderation", f"Failed to list warnings for {guild_id}: {e}")
            return None, 0
        return [_warn_row(row) for row in rows], total

    async def delete_warning(self, guild_id: int, warn_id: int):
        """Delete one warning case, scoped to its guild, and publish the event."""
        pool = _pool()
        if pool is None:
            return None
        try:
            row = await pool.fetchrow(
                "SELECT id, guild_id, user_id, moderator_id, reason, created_at "
                "FROM warns WHERE id = $1 AND guild_id = $2",
                int(warn_id), int(guild_id),
            )
            if row is None:
                return None
            await pool.execute(
                "DELETE FROM warns WHERE id = $1 AND guild_id = $2",
                int(warn_id), int(guild_id),
            )
        except Exception as e:
            from utils import logging
            logging.error("Moderation", f"Failed to delete warn {warn_id} in {guild_id}: {e}")
            return None
        record = _warn_row(row)
        _publish_warn_event("warn.deleted", guild_id, {"warn": record})
        return record

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
        """Delete all warnings for a user in a guild and publish one event."""
        pool = _pool()
        if pool is None:
            return 0
        try:
            rows = await pool.fetch(
                "SELECT id, guild_id, user_id, moderator_id, reason, created_at "
                "FROM warns WHERE guild_id = $1 AND user_id = $2 ORDER BY id ASC",
                int(guild_id), int(user_id),
            )
            await pool.execute(
                "DELETE FROM warns WHERE guild_id = $1 AND user_id = $2",
                int(guild_id), int(user_id),
            )
        except Exception as e:
            from utils import logging
            logging.error("Moderation", f"Failed to clear warnings for {user_id} in {guild_id}: {e}")
            return 0
        removed = [_warn_row(row) for row in rows]
        if removed:
            _publish_warn_event("warns.cleared", guild_id, {
                "user_id": str(user_id),
                "count": len(removed),
                "warn_ids": [item["id"] for item in removed],
            })
        return len(removed)

    # ---------- MUTE SYSTEM (DATABASE) ----------

    def find_mute_role(self, guild: discord.Guild) -> discord.Role | None:
        """The guild's mute role, or None — this never creates one.

        The pinned id wins; the name lookup is only the one-time adoption path
        for servers whose role predates the stored id.
        """
        stored = self.get_guild_config(guild.id).get("mute_role_id")
        if stored:
            role = guild.get_role(int(stored))
            if role is not None:
                return role
        return discord.utils.get(guild.roles, name=MUTE_ROLE_NAME)

    def is_mute_role(self, role: discord.Role) -> bool:
        """Whether this role is the guild's mute role, by pin or by adoption."""
        cfg = self.get_guild_config(role.guild.id)
        pinned = cfg.get("mute_role_id")
        if pinned:
            return int(pinned) == role.id
        return role.name == MUTE_ROLE_NAME

    def _remember_mute_role(self, guild: discord.Guild, role: discord.Role) -> None:
        """Pin the role used for mutes, so later lookups never guess by name."""
        cfg = self.get_guild_config(guild.id)
        if cfg.get("mute_role_id") != role.id:
            cfg["mute_role_id"] = role.id
            self.save_config(guild.id)

    def _mute_needs_deny(self, channel: discord.abc.GuildChannel, role: discord.Role) -> bool:
        """Whether this channel still needs the mute role's deny.

        A role-level permission is only the starting point, so the deny has to
        live on the channel. It holds in channels that grant the member's other
        roles nothing; the timeout applied first covers the rest.
        """
        try:
            overwrite = channel.overwrites_for(role)
        except Exception:
            return False
        return overwrite.send_messages is not False or overwrite.speak is not False

    async def _deny_mute_in_channels(self, guild: discord.Guild, role: discord.Role,
                                     *, reason: str) -> list:
        """Deny sending and speaking to the mute role on every channel.

        Channels that already deny it are skipped, so a repeat mute costs no
        API calls; only a newly created channel, or a mute role that predates
        this check (adopted by name, or created by another bot), is written. A
        channel allow for another of the member's roles still beats this deny —
        the timeout applied before it is what makes the mute hold there.

        The channels written are returned so the whole batch is logged as one
        entry once it is done, rather than one entry per channel.
        """
        repaired = []
        for channel in guild.channels:
            if not self._mute_needs_deny(channel, role):
                continue
            # Marked per channel so the logger can tell this bot's bulk write
            # from a moderator editing the same overwrite right after it.
            self._mark_self_write(guild.id, channel.id, f"overwrite:{role.id}")
            try:
                await channel.set_permissions(
                    role,
                    send_messages=False,
                    speak=False,
                    add_reactions=False,
                    use_application_commands=False,
                    use_external_apps=False,
                    reason=reason,
                )
                repaired.append(channel)
            except Exception:
                continue
        return repaired

    async def ensure_mute_role(self, guild: discord.Guild) -> discord.Role:
        """The guild's mute role, created (and pinned) only when it has none.

        A role that has to be created is logged straight away, so the channel
        denies written right after can update that one entry instead of adding
        a second message to the log.
        """
        role = self.find_mute_role(guild)
        if role is not None:
            self._remember_mute_role(guild, role)
            return role
        perms = discord.Permissions(send_messages=False, speak=False, add_reactions=False)
        role = await guild.create_role(name=MUTE_ROLE_NAME, permissions=perms, reason="Create mute role")
        self._remember_mute_role(guild, role)
        # The role-create listener leaves this one entry to us, so creating the
        # role and denying it in every channel is one message, not many.
        self._mark_self_write(guild.id, role.id, "role_create")
        logger = self.bot.get_cog("ServerLogger") if hasattr(self.bot, "get_cog") else None
        if logger is not None:
            try:
                await logger.log_mute_role_setup(guild, role, created=True)
            except Exception as e:
                from utils import logging
                logging.error("Moderation", f"Could not log the mute role in {guild.id}: {e}")
        return role

    def _mark_self_write(self, guild_id: int, user_id: int, kind: str) -> None:
        """Remember that this bot is the one changing the member's mute state."""
        now = time.monotonic()
        for key, at in list(self._self_writes.items()):
            if now - at > _SELF_WRITE_TTL:
                del self._self_writes[key]
        self._self_writes[(int(guild_id), int(user_id), kind)] = now

    def is_self_write(self, guild_id: int, user_id: int, kind: str, *,
                      ttl: float | None = None) -> bool:
        """Whether this bot wrote the member's mute role or timeout just now.

        The two are tracked apart: a role a moderator hands out right after the
        bot applied the timeout is still theirs to take off again.
        """
        at = self._self_writes.get((int(guild_id), int(user_id), kind))
        window = _SELF_WRITE_TTL if ttl is None else ttl
        return at is not None and time.monotonic() - at <= window

    def is_own_overwrite(self, guild_id: int, channel_id: int, role_id: int) -> bool:
        """Whether this bot just wrote the role's permission overwrite here."""
        return self.is_self_write(
            guild_id, channel_id, f"overwrite:{int(role_id)}",
            ttl=_OVERWRITE_WRITE_TTL,
        )

    async def _apply_mute_role(self, guild: discord.Guild, member: discord.Member,
                              *, reason: str) -> discord.Role | None:
        """Add the mute role and repair its channel denies, best effort.

        The timeout is what holds the mute, so a hierarchy or permission problem
        here must not turn a working mute into an error message: it is logged
        and the mute carries on without the badge.
        """
        try:
            role = await self.ensure_mute_role(guild)
        except Exception as e:
            from utils import logging
            logging.error("Moderation", f"Could not create the mute role in {guild.id}: {e}")
            return None
        # A moderator who handed out the role themselves has already added it;
        # adding it again would only write a pointless audit entry.
        if role not in member.roles:
            self._mark_self_write(guild.id, member.id, "role")
            try:
                await member.add_roles(role, reason=reason)
            except Exception:
                fresh = guild.get_member(member.id)
                if fresh is not None:
                    try:
                        await fresh.add_roles(role, reason=reason)
                    except Exception as e:
                        from utils import logging
                        logging.error("Moderation", f"Could not add the mute role to {member.id} in {guild.id}: {e}")
                        return None
                else:
                    from utils import logging
                    logging.error("Moderation", f"Could not add the mute role to {member.id} in {guild.id}: member not in guild")
                    return None
        changed = await self._deny_mute_in_channels(guild, role, reason=reason)
        logger = self.bot.get_cog("ServerLogger") if hasattr(self.bot, "get_cog") else None
        if logger is not None:
            try:
                await logger.log_mute_role_setup(guild, role, channels=changed)
            except Exception as e:
                from utils import logging
                logging.error("Moderation", f"Could not log the mute role in {guild.id}: {e}")
        return role

    async def _record_mute(self, guild_id: int, user_id: int, until,
                           reason=None) -> None:
        """Store the mute row the watcher, rejoin and role logic all read."""
        pool = _pool()
        if pool is None:
            return
        if isinstance(until, datetime):
            until = until.isoformat()
        try:
            if pool.db_type == "mongodb":
                await pool.collection("mutes").replace_one(
                    {"guild_id": int(guild_id), "user_id": int(user_id)},
                    {
                        "guild_id": int(guild_id),
                        "user_id": int(user_id),
                        "reason": reason,
                        "until": until,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    },
                    upsert=True,
                )
            else:
                # One row per member: re-muting or adopting a timeout replaces
                # the expiry instead of stacking a second row on top of it.
                await pool.execute(
                    "DELETE FROM mutes WHERE guild_id = $1 AND user_id = $2",
                    int(guild_id), int(user_id),
                )
                await pool.execute(
                    "INSERT INTO mutes (guild_id, user_id, reason, until) "
                    "VALUES ($1, $2, $3, $4)",
                    int(guild_id), int(user_id), reason, until,
                )
        except Exception as e:
            from utils import logging
            logging.error("Moderation", f"Failed to save mute for {user_id}: {e}")

    async def get_mute_record(self, guild_id: int, user_id: int):
        """The stored mute row for a member, or ``None``."""
        pool = _pool()
        if pool is None:
            return None
        try:
            if pool.db_type == "mongodb":
                return await pool.collection("mutes").find_one({
                    "guild_id": int(guild_id), "user_id": int(user_id),
                })
            rows = await pool.fetch(
                "SELECT id, reason, until FROM mutes WHERE guild_id = $1 AND user_id = $2",
                int(guild_id), int(user_id),
            )
            return rows[0] if rows else None
        except Exception as e:
            from utils import logging
            logging.error("Moderation", f"Failed to read mute for {user_id}: {e}")
            return None

    async def has_mute(self, guild_id: int, user_id: int) -> bool:
        """Whether this member is on record as muted."""
        return await self.get_mute_record(guild_id, user_id) is not None

    async def log_mute(self, guild: discord.Guild, member, title: str, action: str, *,
                       method: str, actor=None, reason=None, until=None,
                       duration=None) -> None:
        """Write the one entry a mute change produces, however it happened.

        Every way of muting or unmuting — the command, the role, a timeout put
        on or cleared in Discord, automod, expiry, a returning member — lands in
        the moderation log as this entry, so a change never also shows up as a
        separate timeout or role entry. ``method`` is the line that says which
        of them was used.
        """
        get_cog = getattr(self.bot, "get_cog", None)
        logger = get_cog("ServerLogger") if get_cog else None
        if logger is None:
            return
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Action:** {action}\n"
            f"**Method:** {method}"
        )
        if duration is not None:
            body += f"\n**Duration:** {duration}s"
        if until is not None:
            stamp = int(until.timestamp())
            body += f"\n**Expires:** <t:{stamp}:F> (<t:{stamp}:R>)"
        if actor is not None:
            body += f"\n**Moderator:** {actor.mention}"
        body += f"\n**Reason:** {reason or 'No reason provided'}"
        await logger.log_event(
            guild, "moderation", title, body,
            target_id=member.id, action_key=title,
        )

    async def mute_member(self, guild: discord.Guild, member: discord.Member,
                          duration=None, reason=None, *, method: str = "Command",
                          actor=None) -> bool:
        """Silence a member with Discord's timeout, backed by the mute role.

        The timeout is what makes the mute hold: a role's permissions are only a
        starting point, because a channel overwrite that allows another of the
        member's roles (the verified role in a server behind a verification
        gate) grants the permission straight back. A timeout ignores channel
        permissions entirely, so it cannot be talked around.

        The mute role goes on as well, so channels whose denies do hold keep the
        member quiet too, but it is not what the mute depends on.

        Every mute records an expiry at the timeout's own end, including a
        regular mute: Discord caps a timeout at 28 days, so that is where it
        ends. The watcher lifts it there and logs the expiry with a button to
        reapply it.

        ``False`` means the timeout itself was refused — the one failure a
        moderator must not be told succeeded.
        """
        seconds = min(int(duration), _MAX_TIMEOUT_SECONDS) if duration else _MAX_TIMEOUT_SECONDS
        self._mark_self_write(guild.id, member.id, "timeout")
        try:
            await member.timeout(timedelta(seconds=seconds), reason=reason or "Muted")
        except (discord.Forbidden, discord.HTTPException) as e:
            from utils import logging
            logging.error("Moderation", f"Failed to time out {member.id} in {guild.id}: {e}")
            return False

        await self._apply_mute_role(guild, member, reason=reason or "Muted")

        # Recorded at the timeout's own end so the watcher can lift the mute
        # there and log it; a regular mute has no other expiry to go by.
        until = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        await self._record_mute(guild.id, member.id, until, reason)

        title = "Tempmute" if duration else "Mute"
        await self.log_mute(
            guild, member, title, title, method=method, actor=actor,
            reason=reason, until=until,
            duration=seconds if duration else None,
        )
        return True

    async def _remove_mute_role(self, member: discord.Member, reason: str = "Unmuted") -> None:
        """Take the mute role off, without provisioning one when none exists."""
        role = self.find_mute_role(member.guild)
        if role is not None and role in member.roles:
            self._mark_self_write(member.guild.id, member.id, "role")
            try:
                await member.remove_roles(role, reason=reason)
            except discord.HTTPException:
                pass

    async def _delete_mute_record(self, guild_id: int, user_id: int) -> None:
        pool = _pool()
        if pool is None:
            return
        try:
            if pool.db_type == "mongodb":
                await pool.collection("mutes").delete_many({
                    "guild_id": int(guild_id),
                    "user_id": int(user_id),
                })
            else:
                await pool.execute(
                    "DELETE FROM mutes WHERE guild_id = $1 AND user_id = $2",
                    int(guild_id), int(user_id),
                )
        except Exception as e:
            from utils import logging
            logging.error("Moderation", f"Failed to remove mute for {user_id}: {e}")

    async def unmute_member(self, member: discord.Member, reason=None, *,
                            method: str = "Command", actor=None) -> None:
        """Clear a member's timeout and take the mute role off.

        Both halves are undone: mutes are enforced by the timeout, and members
        muted by an older build (or by the role alone) only need the role gone.
        Deliberately never provisions a role: unmuting someone in a server that
        has never muted anybody used to create a "Muted" role and rewrite every
        channel's permissions for it.
        """
        audit_reason = reason or (f"Unmuted by {actor}" if actor else "Unmuted")
        was_muted = await self.has_mute(member.guild.id, member.id)
        self._mark_self_write(member.guild.id, member.id, "timeout")
        try:
            await member.timeout(None, reason=audit_reason)
        except (discord.Forbidden, discord.HTTPException):
            pass

        await self._remove_mute_role(member, audit_reason)
        await self._delete_mute_record(member.guild.id, member.id)
        if was_muted:
            await self.log_mute(
                member.guild, member, "Unmute", "Unmute",
                method=method, actor=actor, reason=reason,
            )

    async def release_mute(self, guild: discord.Guild, member: discord.Member, *,
                           actor=None, reason=None, expired: bool = False) -> bool:
        """Lift a mute whose timeout has already ended.

        Only for this bot's own mutes, which the record identifies: Discord
        removes the timeout itself, so there is nothing to clear here, and the
        role comes off with the record. A timeout a moderator cleared by hand is
        an unmute; one that ran out is the mute expiring, and its entry keeps the
        Mute quick action. A timeout this bot never applied is not a mute and
        must be left to whoever applied it.
        """
        if not await self.has_mute(guild.id, member.id):
            return False

        await self._remove_mute_role(member, "Mute expired" if expired else "Unmuted")
        await self._delete_mute_record(guild.id, member.id)

        if expired:
            await self.log_mute(
                guild, member, "Mute Expired", "Mute expired",
                method="Timeout ran out", reason=reason,
            )
        else:
            await self.log_mute(
                guild, member, "Unmute", "Unmute",
                method="Timeout", actor=actor, reason=reason,
            )
        return True

    async def adopt_role_mute(self, guild: discord.Guild, member: discord.Member,
                              actor=None, reason=None) -> bool:
        """Treat the Muted role being handed out as a mute.

        Staff can use the role itself as the mute control: putting it on applies
        the timeout and records the mute, so the role doubles as the visible
        indicator that somebody is muted.
        """
        if await self.has_mute(guild.id, member.id):
            return False

        return await self.mute_member(
            guild, member, duration=None, reason=reason,
            method="Muted role", actor=actor,
        )

    async def adopt_role_unmute(self, guild: discord.Guild, member: discord.Member,
                                actor=None, reason=None) -> bool:
        """Treat the Muted role coming off as an unmute."""
        if not await self.has_mute(guild.id, member.id):
            return False

        await self.unmute_member(
            member, reason=reason, method="Muted role", actor=actor,
        )
        return True

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Put a still-running mute back on a member who comes back.

        Somebody who left while muted keeps their record: the role Discord
        stripped with them is only the badge, and the record is what says the
        mute was never lifted. Rejoining inside the remaining time restores the
        role and the rest of the timeout; coming back after it has run out just
        clears the record.
        """
        record = await self.get_mute_record(member.guild.id, member.id)
        if not record:
            return
        until = _parse_mute_until(record.get("until"))
        now = datetime.now(timezone.utc)
        if until is None or until <= now:
            await self._delete_mute_record(member.guild.id, member.id)
            return

        remaining = int((until - now).total_seconds())
        self._mark_self_write(member.guild.id, member.id, "timeout")
        try:
            await member.timeout(timedelta(seconds=remaining), reason="Mute still active")
        except (discord.Forbidden, discord.HTTPException):
            pass
        await self._apply_mute_role(member.guild, member, reason="Mute still active")
        await self.log_mute(
            member.guild, member, "Mute", "Mute",
            method="Rejoined server", reason=record.get("reason"), until=until,
        )

    async def mute_watcher(self):
        """Periodically check for expired mutes and unmute users."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            now = datetime.now(timezone.utc)
            pool = _pool()
            if pool is not None:
                try:
                    if pool.db_type == "mongodb":
                        records = [
                            doc async for doc in pool.collection("mutes").find({"until": {"$ne": None}})
                        ]
                    else:
                        records = await pool.fetch(
                            "SELECT id, guild_id, user_id, until, reason FROM mutes WHERE until IS NOT NULL"
                        )
                    for record in records:
                        until = _parse_mute_until(record.get("until"))
                        if until is None or now < until:
                            continue
                        guild = self.bot.get_guild(int(record["guild_id"]))
                        if not guild:
                            continue
                        member = guild.get_member(int(record["user_id"]))
                        if member is None:
                            # They left while muted. Discord cleared the timeout
                            # with them, there is no role to take off, and the
                            # mute has run out — nobody can rejoin inside it now,
                            # so the record is finished.
                            await self._delete_mute_record(guild.id, record["user_id"])
                            continue
                        try:
                            await self.release_mute(
                                guild, member, reason=record.get("reason"), expired=True
                            )
                        except Exception:
                            pass
                except Exception as e:
                    from utils import logging
                    logging.error("Moderation", f"Mute watcher error: {e}")
            await asyncio.sleep(15)

    # ---------- BLOCKED WORDS ----------

    def get_blocked_words(self, guild_id: int) -> list:
        """The guild's blocked words, normalized and de-duplicated.

        Entries are sanitised on read, so a word stored by an older version
        (with stray whitespace, mixed case, or an empty string) starts working
        as soon as this runs instead of silently never matching.
        """
        raw = self.get_guild_config(guild_id).get("blocked_words", [])
        if not isinstance(raw, (list, tuple)):
            return []
        words: list = []
        for entry in raw:
            word = normalize_blocked_word(entry)
            if word and word not in words:
                words.append(word)
        return words

    def blocked_word_pattern(self, guild_id: int):
        """Compiled whole-word pattern for the guild, or None when none is set."""
        words = tuple(self.get_blocked_words(guild_id))
        if not words:
            return None
        if words in self._blocked_patterns:
            return self._blocked_patterns[words]
        pattern = build_blocked_word_regex(words)
        if len(self._blocked_patterns) >= MAX_CACHED_GUILD_PATTERNS:
            self._blocked_patterns.clear()
        self._blocked_patterns[words] = pattern
        return pattern

    def add_blocked_word(self, guild_id: int, word: str):
        """Add a blocked word. Blank or oversized input is ignored rather than
        stored, because an empty entry would match every message."""
        word = normalize_blocked_word(word)
        if word is None:
            return
        cfg = self.get_guild_config(guild_id)
        current = self.get_blocked_words(guild_id)
        if word in current or len(current) >= MAX_BLOCKED_WORDS:
            return
        cfg["blocked_words"] = current + [word]
        self.save_config(guild_id)

    def remove_blocked_word(self, guild_id: int, word: str):
        cfg = self.get_guild_config(guild_id)
        word = normalize_blocked_word(word)
        if word is None:
            return
        cfg["blocked_words"] = [entry for entry in self.get_blocked_words(guild_id) if entry != word]
        self.save_config(guild_id)

    def clear_blocked_words(self, guild_id: int):
        self.get_guild_config(guild_id)["blocked_words"] = []
        self.save_config(guild_id)

    # ---------- BLOCKED WORD PRESET FILTERS ----------

    def get_badwords_presets(self, guild_id: int) -> list:
        """Preset filter keys enabled for this guild, in catalog order."""
        return normalize_presets(self.get_guild_config(guild_id).get("badwords_presets"))

    def set_badwords_preset(self, guild_id: int, key: str, enabled: bool = True) -> bool:
        """Switch one preset filter on or off. Returns whether anything changed."""
        key = str(key if key is not None else "").strip().lower()
        if key not in PRESET_KEYS:
            return False
        current = self.get_badwords_presets(guild_id)
        if bool(enabled):
            if key in current:
                return False
            updated = [preset for preset in PRESET_KEYS if preset in current or preset == key]
        else:
            if key not in current:
                return False
            updated = [preset for preset in current if preset != key]
        self.get_guild_config(guild_id)["badwords_presets"] = updated
        self.save_config(guild_id)
        return True

    def set_badwords_presets(self, guild_id: int, keys) -> list:
        """Replace the whole enabled set at once (one save, one config write)."""
        presets = normalize_presets(keys)
        self.get_guild_config(guild_id)["badwords_presets"] = presets
        self.save_config(guild_id)
        return presets

    def toggle_badwords_preset(self, guild_id: int, key: str) -> bool | None:
        """Flip one preset filter, returning its new state (None if unknown)."""
        key = str(key if key is not None else "").strip().lower()
        if key not in PRESET_KEYS:
            return None
        enabled = not (key in self.get_badwords_presets(guild_id))
        self.set_badwords_preset(guild_id, key, enabled)
        return enabled

    def badwords_patterns(self, guild_id: int) -> list:
        """Every pattern a message is checked against for this guild.

        The custom word list and the preset filters are independent, so a
        server can run either, both, or neither.
        """
        patterns = []
        custom = self.blocked_word_pattern(guild_id)
        if custom is not None:
            patterns.append(custom)
        presets = self.get_badwords_presets(guild_id)
        if presets:
            preset_pattern = build_preset_regex(presets)
            if preset_pattern is not None:
                patterns.append(preset_pattern)
        return patterns

    def get_badwords_action(self, guild_id: int) -> str:
        return normalize_badwords_action(self.get_guild_config(guild_id).get("badwords_action"))

    def get_badwords_mask(self, guild_id: int) -> str:
        return normalize_badwords_mask(self.get_guild_config(guild_id).get("badwords_mask"))

    def censor_blocked_words(self, guild_id: int, content, mask=None) -> str:
        """Return ``content`` with every blocked word replaced by ``mask``.

        Uses the same matchers as :meth:`contains_blocked_word` — the custom
        whole-word list and the preset regex filters — so what gets masked is
        exactly what would have triggered a delete, including words spaced or
        punctuated out, the wildcard forms, and preset spellings like "n1gg3r".
        """
        text = normalize_message_content(content) if isinstance(content, str) else ""
        if not text:
            return text
        patterns = self.badwords_patterns(guild_id)
        if not patterns:
            return text
        replacement = self.get_badwords_mask(guild_id) if mask is None else normalize_badwords_mask(mask)
        substitute = _mask_substitution(replacement)
        for pattern in patterns:
            text = pattern.sub(substitute, text)
        return text

    def contains_blocked_word(self, guild_id: int, content) -> bool:
        """Whether ``content`` trips the guild's blocked-word or preset filter.

        Custom words match whole-word, so blocking "ass" no longer deletes
        "class", "grass" or "assistant" — but separators between the letters
        are tolerated, so "a.s.s" and "a s s" are still caught. Preset filters
        add leet substitutions, repeated letters and unicode look-alikes.
        """
        if not isinstance(content, str) or not content:
            return False
        text = normalize_message_content(content)
        return any(pattern.search(text) for pattern in self.badwords_patterns(guild_id))

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
        self.save_config(guild_id)

    def remove_whitelist_user(self, guild_id: int, user_id: int):
        cfg = self.get_guild_config(guild_id)
        wl = cfg.get("whitelist_users", [])
        if user_id in wl:
            wl.remove(user_id)
        self.save_config(guild_id)

    def add_whitelist_role(self, guild_id: int, role_id: int):
        cfg = self.get_guild_config(guild_id)
        wl = cfg.setdefault("whitelist_roles", [])
        if role_id not in wl:
            wl.append(role_id)
        self.save_config(guild_id)

    def remove_whitelist_role(self, guild_id: int, role_id: int):
        cfg = self.get_guild_config(guild_id)
        wl = cfg.get("whitelist_roles", [])
        if role_id in wl:
            wl.remove(role_id)
        self.save_config(guild_id)

    def get_whitelist(self, guild_id: int) -> dict:
        cfg = self.get_guild_config(guild_id)
        return {
            "users": cfg.get("whitelist_users", []),
            "roles": cfg.get("whitelist_roles", []),
        }


async def setup(bot):
    await bot.add_cog(ModerationUtils(bot))
