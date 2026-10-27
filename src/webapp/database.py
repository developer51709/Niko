"""Readers for the bot's data: the economy, leveling standings, and cached
member identity."""

import json
import sqlite3
import time
from . import config, discord_api, runtime


_member_metadata_cache: dict[str, tuple[float, dict[str, dict]]] = {}


def sqlite_connect():
    """Open a short-lived read/write connection to the bot's SQLite database."""
    try:
        return sqlite3.connect(config.DATABASE_PATH, timeout=5)
    except Exception:
        return None


def _normalize_economy_row(row) -> dict:
    """Convert an economy database row into the dashboard response shape."""
    balance = int(row.get("balance", 0) or 0)
    bank = int(row.get("bank", 0) or 0)
    try:
        leaderboard_private = bool(int(row.get("leaderboard_private", 0) or 0))
    except (TypeError, ValueError):
        leaderboard_private = bool(row.get("leaderboard_private", False))
    achievements = row.get("achievements", [])
    if isinstance(achievements, str):
        try:
            achievements = json.loads(achievements or "[]")
        except (TypeError, ValueError):
            achievements = []
    return {
        "user_id": str(row.get("user_id")),
        "balance": balance,
        "bank": bank,
        "net_worth": balance + bank,
        "leaderboard_private": leaderboard_private,
        "level": int(row.get("level", 0) or 0),
        "job": row.get("job") or "barista",
        "daily_streak": int(row.get("daily_streak", 0) or 0),
        "achievements": len(achievements) if isinstance(achievements, (list, tuple, set, dict)) else 0,
        "total_earned": int(row.get("total_earned", 0) or 0),
    }


def _member_metadata_from_guild(guild, user_ids: set[str]) -> dict[str, dict]:
    """Build identity metadata without crossing the Discord event loop."""
    if guild is None or not user_ids:
        return {}
    metadata = {}
    for member in getattr(guild, "members", []):
        member_id = str(member.id)
        if member_id not in user_ids:
            continue
        avatar = getattr(member, "display_avatar", None)
        metadata[member_id] = {
            "display_name": getattr(member, "global_name", None) or getattr(getattr(member, "_user", None), "global_name", None) or getattr(member, "name", None),
            "username": getattr(member, "name", None),
            "avatar_url": str(avatar.url) if avatar is not None else None,
        }
    return metadata


def get_runtime_member_metadata(guild_id: str, user_ids: set[str]) -> dict[str, dict]:
    """Return display names and avatars for cached members in a guild."""
    if not user_ids or runtime._discord_bot is None:
        return {}

    async def read_members():
        return _member_metadata_from_guild(
            runtime._discord_bot.get_guild(int(guild_id)),
            user_ids,
        )

    try:
        return runtime.run_on_bot_loop(read_members())
    except Exception:
        return {}


def get_discord_member_metadata(guild_id: str, user_ids: set[str]) -> dict[str, dict]:
    """Fetch guild member identity data when Flask runs without the bot object."""
    if not user_ids or not config.DISCORD_BOT_TOKEN:
        return {}

    cached = _member_metadata_cache.get(str(guild_id))
    if cached and time.time() - cached[0] < 60:
        return {user_id: cached[1][user_id] for user_id in user_ids if user_id in cached[1]}

    members = {}
    after = None
    for _ in range(100):
        params = {"limit": 1000}
        if after:
            params["after"] = after
        try:
            response = discord_api.discord_request(
                "GET",
                f"{config.DISCORD_API}/guilds/{guild_id}/members",
                headers={"Authorization": f"Bot {config.DISCORD_BOT_TOKEN}"},
                params=params,
                timeout=8,
            )
            response.raise_for_status()
            batch = response.json()
        except Exception:
            break
        if not isinstance(batch, list):
            break

        for member in batch:
            discord_user = member.get("user", {})
            member_id = str(discord_user.get("id", ""))
            if not member_id:
                continue
            guild_avatar = member.get("avatar")
            user_avatar = discord_user.get("avatar")
            if guild_avatar:
                avatar_url = f"https://cdn.discordapp.com/guilds/{guild_id}/users/{member_id}/avatars/{guild_avatar}.png?size=64"
            elif user_avatar:
                extension = "gif" if str(user_avatar).startswith("a_") else "png"
                avatar_url = f"https://cdn.discordapp.com/avatars/{member_id}/{user_avatar}.{extension}?size=64"
            else:
                avatar_url = None
            members[member_id] = {
                "display_name": discord_user.get("global_name") or discord_user.get("username"),
                "username": discord_user.get("username"),
                "avatar_url": avatar_url,
            }

        if len(batch) < 1000:
            break
        after = str(batch[-1].get("user", {}).get("id", ""))
        if not after:
            break

    _member_metadata_cache[str(guild_id)] = (time.time(), members)
    return {user_id: members[user_id] for user_id in user_ids if user_id in members}


def get_member_metadata(guild_id: str, user_ids: set[str]) -> dict[str, dict]:
    """Use the live bot cache first, then the bot-token API fallback."""
    if runtime._discord_bot is not None:
        metadata = get_runtime_member_metadata(guild_id, user_ids)
        if metadata:
            return metadata
    return get_discord_member_metadata(guild_id, user_ids)


def get_runtime_economy_rows(guild_id: str | None = None) -> list[dict] | None:
    """Read economy data from the live bot database.

    Economy profiles are global by user ID, so guild pages intersect them with
    the selected guild's cached Discord members before calculating totals.
    """
    query = (
        "SELECT user_id, balance, bank, level, job, daily_streak, "
        "achievements, total_earned, leaderboard_private FROM economy_users"
    )
    if runtime._discord_bot is not None and hasattr(runtime._discord_bot, "cxn"):
        async def read_from_bot():
            rows = await runtime._discord_bot.cxn.fetch(query)
            normalized = [_normalize_economy_row(row) for row in rows]
            if guild_id is None:
                return normalized
            guild = runtime._discord_bot.get_guild(int(guild_id))
            if guild is None:
                return []
            member_ids = {str(member.id) for member in getattr(guild, "members", [])}
            scoped = [row for row in normalized if row["user_id"] in member_ids]
            metadata = _member_metadata_from_guild(
                guild,
                {row["user_id"] for row in scoped},
            )
            return [{**row, **metadata.get(row["user_id"], {})} for row in scoped]

        try:
            return runtime.run_on_bot_loop(read_from_bot())
        except Exception:
            pass

    conn = sqlite_connect()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        rows = [_normalize_economy_row(dict(zip(columns, raw))) for raw in cursor.fetchall()]
        if guild_id is not None:
            metadata = get_member_metadata(guild_id, {row["user_id"] for row in rows})
            return [
                {**row, **metadata[row["user_id"]]}
                for row in rows
                if row["user_id"] in metadata
            ]
        return rows
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def get_runtime_leaderboard_page(offset: int, limit: int) -> tuple[list[dict], int] | None:
    """Read one top-worth leaderboard page, with a strict database-side bound."""
    offset = max(0, int(offset))
    limit = max(1, min(int(limit), 100))
    pool = getattr(runtime._discord_bot, "cxn", None) if runtime._discord_bot is not None else None
    if pool is not None:
        async def read_page():
            page = await pool.fetch(
                "SELECT user_id, balance, bank, leaderboard_private "
                "FROM economy_users ORDER BY net_worth DESC, user_id ASC LIMIT $1 OFFSET $2",
                limit, offset,
            )
            count = await pool.fetchval("SELECT COUNT(*) FROM economy_users")
            return page, int(count or 0)
        try:
            rows, total = runtime.run_on_bot_loop(read_page())
            return [_normalize_economy_row(row) for row in rows], total
        except Exception:
            return None

    conn = sqlite_connect()
    if conn is None:
        return None
    try:
        cursor = conn.execute(
            "SELECT user_id, balance, bank, leaderboard_private FROM economy_users "
            "ORDER BY net_worth DESC, user_id ASC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        columns = [column[0] for column in cursor.description]
        rows = [_normalize_economy_row(dict(zip(columns, raw))) for raw in cursor.fetchall()]
        total = conn.execute("SELECT COUNT(*) FROM economy_users").fetchone()[0]
        return rows, int(total or 0)
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def get_runtime_guild_level_page(guild_id: str, offset: int, limit: int) -> tuple[list[dict], int] | None:
    """Read one page of a server's leveling standings, bounded in the database.

    Guild boards are small next to the global economy board, but the public
    page polls while it is open, so only the requested slice is read and the
    total is counted separately. Ranking is by level and then XP, the same
    order the server's `/leveling rank` position uses.
    """
    offset = max(0, int(offset))
    limit = max(1, min(int(limit), 100))
    numeric_guild_id = int(guild_id)

    def as_int(value) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            try:
                return int(float(value))
            except (TypeError, ValueError):
                return 0

    def normalize(rows) -> list[dict]:
        return [
            {
                "user_id": str(row.get("user_id")),
                "xp": as_int(row.get("xp")),
                "level": as_int(row.get("level")),
            }
            for row in rows
            if row.get("user_id") is not None
        ]

    pool = getattr(runtime._discord_bot, "cxn", None) if runtime._discord_bot is not None else None
    if pool is not None:
        async def read_page():
            if getattr(pool, "db_type", None) == "mongodb" and hasattr(pool, "collection"):
                # Older Mongo records may hold the guild id as text, and the
                # composite ``guild_user`` document id can be the only place the
                # guild is recorded, so both spellings are read before sorting.
                documents = await pool.collection("levels").find({
                    "$or": [
                        {"guild_id": numeric_guild_id},
                        {"guild_id": str(numeric_guild_id)},
                        {"_id": {"$regex": rf"^{numeric_guild_id}_"}},
                    ]
                }).to_list(length=None)
                rows = []
                for document in documents:
                    row = dict(document)
                    stored_guild_id = row.get("guild_id")
                    document_id = row.get("_id")
                    if isinstance(document_id, str) and "_" in document_id:
                        composite_guild_id, composite_user_id = document_id.split("_", 1)
                        if stored_guild_id is None:
                            stored_guild_id = composite_guild_id
                        if row.get("user_id") is None:
                            row["user_id"] = composite_user_id
                    if str(stored_guild_id) != str(numeric_guild_id):
                        continue
                    rows.append(row)
                rows.sort(
                    key=lambda row: (as_int(row.get("level")), as_int(row.get("xp"))),
                    reverse=True,
                )
                return rows[offset:offset + limit], len(rows)

            page = await pool.fetch(
                "SELECT user_id, xp, level FROM levels "
                "WHERE guild_id = $1 ORDER BY level DESC, xp DESC LIMIT $2 OFFSET $3",
                numeric_guild_id, limit, offset,
            )
            total = await pool.fetchval(
                "SELECT COUNT(*) FROM levels WHERE guild_id = $1", numeric_guild_id,
            )
            return page, int(total or 0)

        try:
            rows, total = runtime.run_on_bot_loop(read_page())
            return normalize(rows), total
        except Exception:
            return None

    conn = sqlite_connect()
    if conn is not None:
        try:
            cursor = conn.execute(
                "SELECT user_id, xp, level FROM levels "
                "WHERE guild_id = ? ORDER BY level DESC, xp DESC LIMIT ? OFFSET ?",
                (numeric_guild_id, limit, offset),
            )
            rows = [
                {"user_id": row[0], "xp": row[1], "level": row[2]}
                for row in cursor.fetchall()
            ]
            total = conn.execute(
                "SELECT COUNT(*) FROM levels WHERE guild_id = ?", (numeric_guild_id,),
            ).fetchone()[0]
            return normalize(rows), int(total or 0)
        except sqlite3.Error:
            return None
        finally:
            conn.close()

    # JSON fallback for a deployment still on the migrated snapshot.
    snapshot = runtime.load_json(config.LEVELS_JSON, {}).get(str(guild_id), {})
    rows = [
        {"user_id": user_id, "xp": value.get("xp", 0), "level": value.get("level", 0)}
        for user_id, value in snapshot.items()
    ]
    rows.sort(key=lambda row: (as_int(row["level"]), as_int(row["xp"])), reverse=True)
    return normalize(rows[offset:offset + limit]), len(rows)


def _serialize_level_config(config) -> dict:
    """Keep Discord snowflake IDs exact when sending leveling data to JS."""
    serialized = dict(config or {})
    channel_id = serialized.get("level_up_channel")
    if channel_id is not None:
        serialized["level_up_channel"] = str(channel_id)
    excluded = serialized.get("xp_excluded_channels") or []
    serialized["xp_excluded_channels"] = [str(cid) for cid in excluded]
    serialized["xp_vc_enabled"] = bool(serialized.get("xp_vc_enabled", False))
    # Level-role IDs are snowflakes as well: JSON numbers above 2^53 lose their
    # trailing digits in JavaScript, so both sides of the mapping go out as text.
    try:
        assigned_roles = dict(serialized.get("level_roles") or {})
    except (TypeError, ValueError):
        assigned_roles = {}
    serialized["level_roles"] = {
        str(level): str(role) for level, role in assigned_roles.items()
    }
    return serialized


def get_runtime_level_config(guild_id: str) -> dict:
    """Read leveling settings through the live leveling cog when available."""
    if runtime._discord_bot is not None:
        leveling = runtime._discord_bot.get_cog("Leveling")
        if leveling is not None and hasattr(leveling, "_guild_cfg"):
            try:
                return _serialize_level_config(runtime.run_on_bot_loop(leveling._guild_cfg(int(guild_id))))
            except Exception:
                pass

    # Fallback for a web-only process or a bot that is still starting.
    level_cfg = {}
    conn = sqlite_connect()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT xp_enabled, xp_multiplier, xp_cooldown, "
                "       level_up_channel, level_up_message, level_roles, "
                "       xp_excluded_channels, xp_vc_enabled, "
                "       card_accent, card_bg_top, card_bg_bottom "
                "FROM level_config WHERE guild_id = ?",
                (int(guild_id),),
            )
            row = cur.fetchone()
            if row:
                level_cfg = {
                    "xp_enabled": bool(row[0]),
                    "xp_multiplier": row[1],
                    "xp_cooldown": row[2],
                    "level_up_channel": str(row[3]) if row[3] else None,
                    "level_up_message": row[4],
                    "level_roles": json.loads(row[5] or "{}"),
                    "xp_excluded_channels": json.loads(row[6] or "[]"),
                    "xp_vc_enabled": bool(row[7]),
                    "card_accent": json.loads(row[8]) if row[8] else None,
                    "card_bg_top": json.loads(row[9]) if row[9] else None,
                    "card_bg_bottom": json.loads(row[10]) if row[10] else None,
                }
            conn.close()
        except Exception:
            conn.close()

    return _serialize_level_config(level_cfg or runtime.load_json(config.LEVELCFG_JSON, {}).get(guild_id, {}))


def get_open_team_openings(limit: int = 6) -> list[dict] | None:
    """The staff roles accepting applications right now.

    Used by the applications page's link preview, which has to name the open
    roles without the viewer opening the page. Only the columns the preview
    shows are read, and the same ``status = 'open'`` filter the page's own API
    uses applies, so a closed role never appears in a preview.

    Returns ``None`` when the table cannot be read, which the caller treats as
    "no openings to list" rather than an error.
    """
    limit = max(1, min(int(limit), 10))
    columns = "id, title, description"

    def normalize(rows) -> list[dict]:
        openings = []
        for row in rows:
            title = str(row.get("title") or "").strip()
            if not title:
                continue
            openings.append({
                "id": str(row.get("id") or ""),
                "title": title,
                "description": " ".join(str(row.get("description") or "").split()),
            })
        return openings[:limit]

    pool = getattr(runtime._discord_bot, "cxn", None) if runtime._discord_bot is not None else None
    if pool is not None:
        async def read_openings():
            return await pool.fetch(
                f"SELECT {columns} FROM staff_team_openings "
                "WHERE status = 'open' ORDER BY created_at DESC LIMIT $1",
                limit,
            )

        try:
            return normalize(runtime.run_on_bot_loop(read_openings()))
        except Exception:
            return None

    conn = sqlite_connect()
    if conn is not None:
        try:
            rows = conn.execute(
                f"SELECT {columns} FROM staff_team_openings "
                "WHERE status = 'open' ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            conn.close()
            return normalize([{"id": row[0], "title": row[1], "description": row[2]} for row in rows])
        except Exception:
            conn.close()

    return None


def level_xp_for_next(level: int) -> int:
    """XP a member needs to leave *level*, via the leveling cog's own curve.

    The public leaderboard draws a progress bar for every row, so it asks the
    cog that awards the XP instead of keeping a second copy of the formula.
    """
    leveling = runtime._discord_bot.get_cog("Leveling") if runtime._discord_bot is not None else None
    if leveling is not None and hasattr(leveling, "get_xp_for_level"):
        try:
            return max(1, int(leveling.get_xp_for_level(max(0, int(level)))))
        except Exception:
            pass
    return max(1, 5 * (int(level) ** 2) + 50 * int(level) + 100)


def _get_levels(guild_id: str) -> list:
    """Fetch level data from the bot's live database, regardless of backend."""
    if runtime._discord_bot is not None and hasattr(runtime._discord_bot, "cxn"):
        async def read_from_bot():
            pool = runtime._discord_bot.cxn
            numeric_guild_id = int(guild_id)

            if getattr(pool, "db_type", None) == "mongodb" and hasattr(pool, "collection"):
                # Older Mongo records may have received the guild ID as text.
                # Read both representations, then sort after coercion so mixed
                # BSON numeric/string values cannot hide real level data.
                documents = await pool.collection("levels").find({
                    "$or": [
                        {"guild_id": numeric_guild_id},
                        {"guild_id": str(numeric_guild_id)},
                        {"_id": {"$regex": rf"^{numeric_guild_id}_"}},
                    ]
                }).to_list(length=None)
                rows = []
                for document in documents:
                    row = dict(document)
                    stored_guild_id = row.get("guild_id")
                    document_id = row.get("_id")
                    if isinstance(document_id, str) and "_" in document_id:
                        composite_guild_id, composite_user_id = document_id.split("_", 1)
                        if stored_guild_id is None:
                            stored_guild_id = composite_guild_id
                        if row.get("user_id") is None:
                            row["user_id"] = composite_user_id
                    if str(stored_guild_id) != str(numeric_guild_id):
                        continue
                    rows.append(row)

                def as_int(value) -> int:
                    try:
                        return int(value or 0)
                    except (TypeError, ValueError):
                        try:
                            return int(float(value))
                        except (TypeError, ValueError):
                            return 0

                rows.sort(
                    key=lambda row: (as_int(row.get("level")), as_int(row.get("xp"))),
                    reverse=True,
                )
                rows = rows[:25]
            else:
                rows = await pool.fetch(
                    "SELECT user_id, xp, level FROM levels "
                    "WHERE guild_id = $1 ORDER BY level DESC, xp DESC LIMIT 25",
                    numeric_guild_id,
                )

            def as_int(value) -> int:
                try:
                    return int(value or 0)
                except (TypeError, ValueError):
                    try:
                        return int(float(value))
                    except (TypeError, ValueError):
                        return 0

            normalized = [
                {
                    "user_id": str(row.get("user_id")),
                    "xp": as_int(row.get("xp")),
                    "level": as_int(row.get("level")),
                }
                for row in rows
                if row.get("user_id") is not None
            ]
            guild = runtime._discord_bot.get_guild(numeric_guild_id)
            metadata = _member_metadata_from_guild(
                guild,
                {row["user_id"] for row in normalized},
            )
            return [{**row, **metadata.get(row["user_id"], {})} for row in normalized]

        try:
            return runtime.run_on_bot_loop(read_from_bot())
        except Exception:
            pass

    conn = sqlite_connect()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT user_id, xp, level FROM levels "
                "WHERE guild_id = ? ORDER BY level DESC, xp DESC LIMIT 25",
                (int(guild_id),),
            )
            rows = [
                {"user_id": str(row[0]), "xp": row[1], "level": row[2]}
                for row in cur.fetchall()
            ]
            conn.close()
            metadata = get_member_metadata(guild_id, {row["user_id"] for row in rows})
            rows = [{**row, **metadata.get(row["user_id"], {})} for row in rows]
            return rows
        except Exception:
            conn.close()

    # JSON fallback (migrated snapshot)
    data = runtime.load_json(config.LEVELS_JSON, {})
    guild = data.get(guild_id, {})
    rows  = [{"user_id": uid, "xp": v.get("xp", 0), "level": v.get("level", 0)}
             for uid, v in guild.items()]
    rows.sort(key=lambda x: x["xp"], reverse=True)
    metadata = get_member_metadata(guild_id, {row["user_id"] for row in rows})
    rows = [{**row, **metadata.get(row["user_id"], {})} for row in rows]
    return rows[:25]
