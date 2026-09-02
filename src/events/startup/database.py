"""
Startup — database initialisation.
Handles connection, table creation, and legacy migrations.
"""

import os
import sqlite3 as _sqlite3
import time

import database
from utils import logging


DATABASE_PATH = "data/database.db"


async def _create_tables(bot):
    if not bot.cxn:
        return

    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS voicemaster_settings (
            guild_id          INTEGER PRIMARY KEY,
            join_channel_id   INTEGER,
            category_id       INTEGER,
            default_name      TEXT DEFAULT '{user}''s Channel',
            default_limit     INTEGER DEFAULT 0,
            default_bitrate   INTEGER DEFAULT 64000,
            default_region    TEXT,
            interface_enabled INTEGER DEFAULT 1,
            auto_role         INTEGER,
            join_role         INTEGER
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS voicemaster_channels (
            channel_id  INTEGER PRIMARY KEY,
            owner_id    INTEGER NOT NULL,
            guild_id    INTEGER NOT NULL,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS follows (
            guild_id     INTEGER,
            platform     TEXT,
            username     TEXT,
            channel_id   INTEGER,
            template     TEXT,
            last_post_id TEXT,
            PRIMARY KEY  (guild_id, platform, username)
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS youtube (
            channel_id TEXT PRIMARY KEY,
            last_video TEXT
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS youtube_history (
            channel_id TEXT,
            video_id   TEXT,
            PRIMARY KEY (channel_id, video_id)
        )
    """)

    await bot.cxn.execute("""
        INSERT OR IGNORE INTO youtube_history (channel_id, video_id)
        SELECT channel_id, last_video FROM youtube WHERE last_video IS NOT NULL
    """)

    try:
        cols = await bot.cxn.fetch("PRAGMA table_info(levels)")
        col_names = {row["name"] for row in cols}
        if cols and "guild_id" not in col_names:
            await bot.cxn.execute("ALTER TABLE levels RENAME TO levels_old")
            await bot.cxn.execute("""
                CREATE TABLE levels (
                    guild_id INTEGER,
                    user_id  INTEGER,
                    xp       INTEGER DEFAULT 0,
                    level    INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            await bot.cxn.execute("DROP TABLE levels_old")
        else:
            await bot.cxn.execute("""
                CREATE TABLE IF NOT EXISTS levels (
                    guild_id INTEGER,
                    user_id  INTEGER,
                    xp       INTEGER DEFAULT 0,
                    level    INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
    except Exception as e:
        logging.warning("DB", f"levels table migration warning: {e}")

    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS level_config (
            guild_id         INTEGER PRIMARY KEY,
            xp_enabled       INTEGER DEFAULT 1,
            xp_multiplier    REAL    DEFAULT 1.0,
            xp_cooldown      INTEGER DEFAULT 0,
            level_up_channel INTEGER,
            level_up_message TEXT,
            level_roles      TEXT
        )
    """)

    old_follows = "data/follows.db"
    if os.path.exists(old_follows):
        try:
            old_conn = _sqlite3.connect(old_follows)
            rows = old_conn.execute("SELECT * FROM follows").fetchall()
            for row in rows:
                await bot.cxn.execute(
                    "INSERT OR IGNORE INTO follows "
                    "(guild_id, platform, username, channel_id, template, last_post_id) "
                    "VALUES ($1, $2, $3, $4, $5, $6)",
                    row[0], row[1], row[2], row[3], row[4], row[5]
                )
            old_conn.close()
            os.rename(old_follows, old_follows + ".migrated")
            logging.success("DB", "Migrated follows.db → database.db")
        except Exception as e:
            logging.warning("DB", f"Could not migrate follows.db: {e}")

    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            user_id        INTEGER PRIMARY KEY,
            total_donated  REAL    DEFAULT 0,
            last_donation  TEXT,
            last_track_id  TEXT
        )
    """)

    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS triggers (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id   INTEGER NOT NULL,
            trigger    TEXT    NOT NULL,
            response   TEXT    NOT NULL,
            match_type TEXT    NOT NULL DEFAULT 'contains',
            enabled    INTEGER NOT NULL DEFAULT 1,
            created_at TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Economy tables
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS economy_users (
            user_id          INTEGER PRIMARY KEY,
            balance          INTEGER DEFAULT 100,
            bank             INTEGER DEFAULT 0,
            net_worth        INTEGER DEFAULT 100,
            total_earned     INTEGER DEFAULT 100,
            total_spent      INTEGER DEFAULT 0,
            xp               INTEGER DEFAULT 0,
            level            INTEGER DEFAULT 0,
            job              TEXT    DEFAULT 'barista',
            times_worked     INTEGER DEFAULT 0,
            bank_tier        INTEGER DEFAULT 0,
            last_interest    INTEGER DEFAULT 0,
            last_interest_day TEXT,
            daily_streak     INTEGER DEFAULT 0,
            last_daily       INTEGER DEFAULT 0,
            last_work        INTEGER DEFAULT 0,
            last_crime       INTEGER DEFAULT 0,
            last_rob         INTEGER DEFAULT 0,
            last_heist       INTEGER DEFAULT 0,
            last_slots       INTEGER DEFAULT 0,
            last_blackjack   INTEGER DEFAULT 0,
            last_roulette    INTEGER DEFAULT 0,
            last_casino      INTEGER DEFAULT 0,
            last_gamble      INTEGER DEFAULT 0,
            last_bet         INTEGER DEFAULT 0,
            last_race        INTEGER DEFAULT 0,
            last_fight       INTEGER DEFAULT 0,
            last_duel        INTEGER DEFAULT 0,
            inventory        TEXT    DEFAULT '{}',
            effects          TEXT    DEFAULT '{}',
            lottery_tickets  INTEGER DEFAULT 0,
            transactions     TEXT    DEFAULT '[]',
            achievements     TEXT    DEFAULT '[]'
        )
    """)

    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS economy_lottery (
            id          INTEGER PRIMARY KEY DEFAULT 1,
            pot         INTEGER DEFAULT 1000,
            next_draw   INTEGER DEFAULT 0,
            last_winner INTEGER,
            last_pot    INTEGER DEFAULT 0
        )
    """)

    # Insert default lottery state if not exists
    await bot.cxn.execute("""
        INSERT OR IGNORE INTO economy_lottery (id, pot, next_draw, last_winner, last_pot)
        VALUES (1, 1000, ?, NULL, 0)
    """, int(time.time()) + 604800)  # 7 days from now

    # Migrate economy data from JSON files to database
    await _migrate_economy_data(bot)

    # ── New tables: onboarding, logging config, moderation config ──────────
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS onboarding (
            guild_id INTEGER PRIMARY KEY,
            data     TEXT
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS logging_config (
            guild_id INTEGER PRIMARY KEY,
            data     TEXT
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS moderation_config (
            guild_id INTEGER PRIMARY KEY,
            data     TEXT
        )
    """)

    # Migrate legacy modlog / moderation JSON stores into the database
    await _migrate_logging_config(bot)
    await _migrate_moderation_config(bot)

    # Migrate legacy onboarding JSON files (data/onboarding/*.json)
    from utils.onboarding.config import migrate_json_files
    try:
        await migrate_json_files(bot)
    except Exception as e:
        logging.warning("DB", f"Onboarding JSON migration failed: {e}")

    logging.success("DB", "Database tables verified")


async def _migrate_economy_data(bot):
    """Migrate economy data from JSON files to the database."""
    import json
    
    economy_data_dir = "data/economy_data"
    lottery_file = "data/economy_data/_lottery.json"
    
    # Check if economy data directory exists
    if not os.path.exists(economy_data_dir):
        return
    
    # Check if we've already migrated (create a marker file)
    migration_marker = "data/economy_data/.migrated_to_db"
    if os.path.exists(migration_marker):
        return
    
    migrated_count = 0
    
    try:
        # Migrate user data
        for filename in os.listdir(economy_data_dir):
            if not filename.endswith(".json") or filename.startswith("_"):
                continue
            
            try:
                file_path = os.path.join(economy_data_dir, filename)
                with open(file_path, "r") as f:
                    data = json.load(f)
                
                user_id = int(filename[:-5])
                
                # Check if user already exists in database
                existing = await bot.cxn.fetchrow(
                    "SELECT user_id FROM economy_users WHERE user_id = ?",
                    user_id
                )
                
                if existing:
                    continue  # Skip if already migrated
                
                # Serialize complex fields
                inventory_json = json.dumps(data.get("inventory", {}))
                effects_json = json.dumps(data.get("effects", {}))
                transactions_json = json.dumps(data.get("transactions", []))
                achievements_json = json.dumps(data.get("achievements", []))
                
                await bot.cxn.execute("""
                    INSERT INTO economy_users (
                        user_id, balance, bank, net_worth, total_earned, total_spent,
                        xp, level, job, times_worked, bank_tier, last_interest,
                        last_interest_day, daily_streak, last_daily, last_work,
                        last_crime, last_rob, last_heist, last_slots, last_blackjack,
                        last_roulette, last_casino, last_gamble, last_bet, last_race,
                        last_fight, last_duel, inventory, effects, lottery_tickets,
                        transactions, achievements
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    user_id,
                    data.get("balance", 100),
                    data.get("bank", 0),
                    data.get("net_worth", 100),
                    data.get("total_earned", 100),
                    data.get("total_spent", 0),
                    data.get("xp", 0),
                    data.get("level", 0),
                    data.get("job", "barista"),
                    data.get("times_worked", 0),
                    data.get("bank_tier", 0),
                    data.get("last_interest", 0),
                    data.get("last_interest_day"),
                    data.get("daily_streak", 0),
                    data.get("last_daily", 0),
                    data.get("last_work", 0),
                    data.get("last_crime", 0),
                    data.get("last_rob", 0),
                    data.get("last_heist", 0),
                    data.get("last_slots", 0),
                    data.get("last_blackjack", 0),
                    data.get("last_roulette", 0),
                    data.get("last_casino", 0),
                    data.get("last_gamble", 0),
                    data.get("last_bet", 0),
                    data.get("last_race", 0),
                    data.get("last_fight", 0),
                    data.get("last_duel", 0),
                    inventory_json,
                    effects_json,
                    data.get("lottery_tickets", 0),
                    transactions_json,
                    achievements_json
                )
                
                migrated_count += 1
                
            except Exception as e:
                logging.warning("DB", f"Could not migrate {filename}: {e}")
        
        # Migrate lottery state
        if os.path.exists(lottery_file):
            try:
                with open(lottery_file, "r") as f:
                    lottery_data = json.load(f)
                
                await bot.cxn.execute("""
                    UPDATE economy_lottery
                    SET pot = ?, next_draw = ?, last_winner = ?, last_pot = ?
                    WHERE id = 1
                """,
                    lottery_data.get("pot", 1000),
                    lottery_data.get("next_draw", int(time.time()) + 604800),
                    lottery_data.get("last_winner"),
                    lottery_data.get("last_pot", 0)
                )
                
                logging.info("DB", "Migrated lottery state from JSON to database")
                
            except Exception as e:
                logging.warning("DB", f"Could not migrate lottery state: {e}")
        
        if migrated_count > 0:
            logging.success("DB", f"Migrated {migrated_count} economy users from JSON to database")
            
            # Create marker file to prevent re-migration
            try:
                with open(migration_marker, "w") as f:
                    f.write("Migration completed at " + str(int(time.time())))
            except Exception:
                pass
    
    except Exception as e:
        logging.warning("DB", f"Economy migration failed: {e}")



async def _migrate_logging_config(bot):
    """Migrate data/logging_config.json (modlog channel config) → database."""
    import json

    path = "data/logging_config.json"
    if not os.path.exists(path):
        return

    try:
        with open(path, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict) or not data:
            os.rename(path, path + ".migrated")
            return

        migrated = 0
        for gid, cfg in data.items():
            try:
                guild_id = int(gid)
            except (TypeError, ValueError):
                continue
            await bot.cxn.execute(
                "INSERT OR REPLACE INTO logging_config (guild_id, data) VALUES ($1, $2)",
                guild_id, json.dumps(cfg),
            )
            migrated += 1

        os.rename(path, path + ".migrated")
        logging.success("DB", f"Migrated {migrated} logging configs (modlog) from JSON to database")
    except Exception as e:
        logging.warning("DB", f"Could not migrate logging_config.json: {e}")


async def _migrate_moderation_config(bot):
    """Migrate data/modconfig.json (moderation + automod config) → database."""
    import json

    for path in ("data/modconfig.json", "data/mod_config.json"):
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r") as f:
                data = json.load(f)
            if not isinstance(data, dict) or not data:
                os.rename(path, path + ".migrated")
                continue

            migrated = 0
            for gid, cfg in data.items():
                try:
                    guild_id = int(gid)
                except (TypeError, ValueError):
                    continue
                await bot.cxn.execute(
                    "INSERT OR REPLACE INTO moderation_config (guild_id, data) VALUES ($1, $2)",
                    guild_id, json.dumps(cfg),
                )
                migrated += 1

            os.rename(path, path + ".migrated")
            logging.success("DB", f"Migrated {migrated} moderation configs from JSON to database")
        except Exception as e:
            logging.warning("DB", f"Could not migrate {path}: {e}")


async def init_database(bot):
    logging.info("DB", f"Opening database: {DATABASE_PATH}")
    try:
        bot.cxn = await database.create_pool(DATABASE_PATH)
        logging.success("DB", "Database connection established")
        await _create_tables(bot)
    except Exception as e:
        logging.error("DB", f"Failed to open database: {e}")
