import asyncio
import dataclasses
import secrets
from dataclasses import dataclass, fields

import database as database_module

COLLECTION = "onboarding"

# ── Role menu types ──────────────────────────────────────────────────────────
MENU_TYPE_LABELS = {
    "select_multi":  "Dropdown — Multiple Roles",
    "select_single": "Dropdown — Single Role",
    "button_multi":  "Buttons — Multiple Roles",
    "button_single": "Buttons — Single Role",
}
DEFAULT_MENU_TYPE = "select_multi"
BUTTON_STYLE_NAMES = ("primary", "secondary", "success", "danger")


def new_menu_id() -> str:
    """Short unique id used to key a role menu within a guild's config."""
    return secrets.token_hex(4)


@dataclass
class OnboardingConfig:
    # Welcome
    welcome_channel: int | None = None
    welcome_title: str | None = None
    welcome_description: str | None = None
    welcome_color: int | None = 0x5865F2
    welcome_image: str | None = None

    # Rules
    rules_channel: int | None = None
    rules_message_id: int | None = None
    rules_text: str | None = None
    rules_role_id: int | None = None  # role to assign on acknowledgment

    # Role menus — menu_id -> menu dict (see docs in the original JSON model)
    role_menus: dict[str, dict] | None = None

    # Autoroles — assigned immediately when a member joins
    autorole_ids: list[int] | None = None

    # Captcha verification
    captcha_enabled: bool = False
    captcha_channel_id: int | None = None
    captcha_panel_message_id: int | None = None
    captcha_add_role_ids: list[int] | None = None
    captcha_remove_role_ids: list[int] | None = None
    captcha_kick_on_fail: bool = False


_KNOWN_FIELDS = {f.name for f in fields(OnboardingConfig)}

# Serialise/deserialise between OnboardingConfig instances and Mongo documents.
_INT_FIELDS = {
    "welcome_channel", "welcome_color", "rules_channel", "rules_message_id",
    "rules_role_id", "captcha_channel_id", "captcha_panel_message_id",
}


def _to_doc(guild_id: int, cfg: OnboardingConfig) -> dict:
    doc = {"_id": str(guild_id), "guild_id": int(guild_id)}
    for f in fields(cfg):
        value = getattr(cfg, f.name)
        if f.name == "role_menus" and isinstance(value, dict):
            doc[f.name] = {str(k): v for k, v in value.items()}
        elif f.name in ("autorole_ids", "captcha_add_role_ids", "captcha_remove_role_ids"):
            doc[f.name] = [int(r) for r in (value or [])]
        elif f.name in _INT_FIELDS and value is not None:
            doc[f.name] = int(value)
        elif value is not None:
            doc[f.name] = value
        else:
            doc[f.name] = None
    return doc


def _from_doc(doc: dict) -> OnboardingConfig:
    known = {k: v for k, v in doc.items() if k in _KNOWN_FIELDS}
    return OnboardingConfig(**known)


def _pool():
    """The bot's shared pool; None until events.startup.database ran."""
    pool = getattr(database_module, "_shared_pool", None)
    return pool


async def load_config(guild_id: int) -> OnboardingConfig:
    """Load a guild's onboarding config from the database."""
    pool = _pool()
    if pool is None:
        return OnboardingConfig()
    if pool.db_type == "mongodb":
        doc = await pool.collection(COLLECTION).find_one({"_id": str(guild_id)})
        if not doc:
            return OnboardingConfig()
        cfg = _from_doc(doc)
    else:
        row = await pool.fetchrow(
            "SELECT data FROM onboarding WHERE guild_id = $1", int(guild_id)
        )
        if not row:
            return OnboardingConfig()
        try:
            doc = row["data"]
            if isinstance(doc, str):
                import json as _json
                doc = _json.loads(doc)
        except Exception:
            return OnboardingConfig()
        cfg = _from_doc(doc)
    return _normalize(cfg)


def _normalize(cfg: OnboardingConfig) -> OnboardingConfig:
    """Migrate any legacy single role-menu shape into the role_menus map."""
    if not cfg.role_menus and getattr(cfg, "_legacy_role_menu_options", None):
        cfg.role_menus = {
            new_menu_id(): {
                "name": "default",
                "title": "Role Selection",
                "description": "Choose your roles below.",
                "color": 0x57F287,
                "menu_type": DEFAULT_MENU_TYPE,
                "max_values": None,
                "channel_id": getattr(cfg, "_legacy_channel", None),
                "message_id": getattr(cfg, "_legacy_message_id", None),
                "options": cfg._legacy_role_menu_options,
            }
        }
    return cfg


async def save_config(guild_id: int, cfg: OnboardingConfig):
    """Persist a guild's onboarding config to the database."""
    pool = _pool()
    if pool is None:
        return
    if pool.db_type == "mongodb":
        await pool.collection(COLLECTION).replace_one(
            {"_id": str(guild_id)}, _to_doc(int(guild_id), cfg), upsert=True
        )
    else:
        import json as _json
        data = _json.dumps(dataclasses.asdict(cfg))
        await pool.execute(
            "INSERT OR REPLACE INTO onboarding (guild_id, data) VALUES ($1, $2)",
            int(guild_id), data,
        )


async def load_all_configs() -> list[tuple[int, OnboardingConfig]]:
    """Return a list of (guild_id, config) for every saved guild."""
    pool = _pool()
    results: list[tuple[int, OnboardingConfig]] = []
    if pool is None:
        return results
    if pool.db_type == "mongodb":
        async for doc in pool.collection(COLLECTION).find({}):
            gid = doc.get("guild_id")
            if gid is None:
                try:
                    gid = int(str(doc.get("_id")))
                except (TypeError, ValueError):
                    continue
            results.append((int(gid), _from_doc(doc)))
    else:
        rows = await pool.fetch("SELECT guild_id, data FROM onboarding")
        import json as _json
        for row in rows:
            try:
                doc = row["data"]
                if isinstance(doc, str):
                    doc = _json.loads(doc)
                results.append((int(row["guild_id"]), _from_doc(doc)))
            except Exception:
                continue
    return results


def _migrate_legacy_json_dict(data: dict) -> OnboardingConfig:
    """Convert a legacy JSON config dict (pre-database) into a config object."""
    known = {k: v for k, v in data.items() if k in _KNOWN_FIELDS}
    cfg = OnboardingConfig(**known)

    # Legacy single role-menu fields → role_menus map
    if not cfg.role_menus and data.get("role_menu_options"):
        cfg.role_menus = {
            new_menu_id(): {
                "name": "default",
                "title": "Role Selection",
                "description": "Choose your roles below.",
                "color": 0x57F287,
                "menu_type": DEFAULT_MENU_TYPE,
                "max_values": None,
                "channel_id": data.get("role_menu_channel"),
                "message_id": data.get("role_menu_message_id"),
                "options": data.get("role_menu_options") or [],
            }
        }
    return cfg


# ── Migration from legacy JSON files ────────────────────────────────────────
_LEGACY_DIR = "data/onboarding"


async def migrate_json_files(bot) -> int:
    """One-time migration of data/onboarding/*.json into the database.

    Returns the number of guild configs imported. Renames each JSON file to
    ``.migrated`` so it is never imported twice.
    """
    import json as _json
    import os

    if not os.path.isdir(_LEGACY_DIR):
        return 0

    migrated = 0
    for fname in os.listdir(_LEGACY_DIR):
        if not fname.endswith(".json"):
            continue
        try:
            gid = int(fname[:-5])
        except ValueError:
            continue
        path = os.path.join(_LEGACY_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = _json.load(f)
            cfg = _migrate_legacy_json_dict(data)
            await save_config(gid, cfg)
            os.rename(path, path + ".migrated")
            migrated += 1
        except Exception as e:
            from utils import logging
            logging.warning("Onboarding", f"Could not migrate {fname}: {e}")
    if migrated:
        from utils import logging
        logging.success(
            "Onboarding", f"Migrated {migrated} onboarding configs from JSON to database"
        )
    return migrated


# Kept for backwards compatibility with any code importing these names.
def get_sync_config(guild_id: int) -> OnboardingConfig:
    raise RuntimeError(
        "Synchronous onboarding config access was removed; await load_config()."
    )
