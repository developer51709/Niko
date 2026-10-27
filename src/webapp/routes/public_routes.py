"""Flask routes for public."""

from config import links as bot_links
from .. import leaderboard_cache
from .. import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})


async def _current_support_invite():
    """Resolve the currently valid invite from the support configuration table."""
    if _discord_bot is None or getattr(_discord_bot, "cxn", None) is None:
        return None
    from cogs.staff.support_server import get_support_invite
    return await get_support_invite(_discord_bot)


def _resolve_leaderboard_identities(user_ids):
    """Resolve Discord identities for ``user_ids``, reusing cached lookups.

    The board re-polls while it is open; without this cache every poll would
    re-fetch the same avatars and display names from Discord.
    """
    if not user_ids or _discord_bot is None:
        return {}
    identities = leaderboard_cache.cached_identities(user_ids)
    missing = {user_id for user_id in user_ids if user_id not in identities}
    if not missing:
        return identities

    async def read_identities():
        found = {}
        for user_id in missing:
            user = _discord_bot.get_user(int(user_id))
            if user is None:
                for guild in _discord_bot.guilds:
                    member = guild.get_member(int(user_id))
                    if member is not None:
                        user = member
                        break
            if user is None:
                try:
                    user = await _discord_bot.fetch_user(int(user_id))
                except Exception:
                    continue
            avatar = getattr(user, "display_avatar", None)
            found[user_id] = {
                "username": getattr(user, "name", None),
                "display_name": getattr(user, "global_name", None) or getattr(user, "display_name", None) or getattr(user, "name", None),
                "avatar_url": str(avatar.url) if avatar is not None else None,
            }
        return found

    try:
        fresh = run_on_bot_loop(read_identities())
    except Exception:
        fresh = {}
    if fresh:
        leaderboard_cache.store_identities(fresh)
    identities.update(fresh)
    return identities


@app.route("/api/economy/leaderboard")
def api_economy_leaderboard():
    """Return one ranked page of global economy standings.

    Ranks every economy profile by net worth, keeping each profile's identity
    private unless the viewer is the account owner, an official Niko staff
    member, or someone who shares a mutual server with that profile.
    """
    try:
        page = int(request.args.get("page", "1"))
        if page < 1:
            raise ValueError("page must be positive")
    except (TypeError, ValueError):
        return jsonify({"error": "Page must be a positive integer."}), 400
    page_size = 20
    offset = (page - 1) * page_size
    result = get_runtime_leaderboard_page(offset, page_size)
    if result is None:
        return jsonify({"error": "The economy leaderboard is temporarily unavailable."}), 503
    rows, total = result
    viewer_id = str((session.get("user") or {}).get("id", ""))
    official_staff = False
    if viewer_id:
        official_staff = _current_staff_role() is not None
    private_ids = {row["user_id"] for row in rows if row.get("leaderboard_private")}
    mutual_ids = set()
    if private_ids and viewer_id and not official_staff:
        resolved = get_mutual_leaderboard_identity_ids(private_ids - {viewer_id})
        if resolved is None:
            return jsonify({"error": "Private profile access could not be verified."}), 503
        mutual_ids = resolved
    visible_ids = {
        row["user_id"] for row in rows
        if not row.get("leaderboard_private")
        or row["user_id"] == viewer_id
        or official_staff
        or row["user_id"] in mutual_ids
    }
    identities = _resolve_leaderboard_identities(visible_ids)

    entries = []
    for rank, row in enumerate(rows, start=offset + 1):
        user_id = row["user_id"]
        identity = identities.get(user_id) if user_id in visible_ids else None
        entries.append({
            # Stable across polls, so the browser can animate a row that moves
            # rank. It is a salted digest, never the Discord id itself.
            "key": leaderboard_cache.profile_key(user_id),
            "rank": rank,
            "net_worth": row["net_worth"],
            "private": bool(row.get("leaderboard_private")),
            "username": identity.get("username") if identity else None,
            "display_name": identity.get("display_name") if identity else None,
            "avatar_url": identity.get("avatar_url") if identity else None,
        })
    response = jsonify({"entries": entries, "page": page, "page_size": page_size, "total": total, "pages": (total + page_size - 1) // page_size})
    # Polled standings must never be answered from a stale copy; the app-wide
    # after_request hook already marks every /api/ response no-store, so this
    # route only has to stay under that prefix.
    return response


@app.route("/api/levels/<guild_id>")
def api_public_guild_levels(guild_id):
    """Return one live page of a server's leveling standings.

    The page is public: a server's own board is already visible to everyone in
    it, and `/leveling leaderboard` now links here instead of rendering a
    static image. The bot must still be in the guild, so a server Niko has left
    reports its unknown-server state rather than showing stale standings.
    """
    try:
        numeric_guild_id = int(guild_id)
        page = int(request.args.get("page", "1"))
        if page < 1:
            raise ValueError("page must be positive")
    except (TypeError, ValueError):
        return jsonify({"error": "Server and page must be positive integers."}), 400

    guild = None
    if _discord_bot is not None:
        try:
            guild = _discord_bot.get_guild(numeric_guild_id)
        except Exception:
            guild = None
    if guild is None:
        return jsonify({
            "error": "Niko isn't in this server, or it is not available right now.",
            "unknown_guild": True,
        }), 404

    page_size = 25
    result = get_runtime_guild_level_page(guild_id, (page - 1) * page_size, page_size)
    if result is None:
        return jsonify({"error": "This server's leaderboard is temporarily unavailable."}), 503
    rows, total = result

    user_ids = {row["user_id"] for row in rows}
    identities = get_runtime_member_metadata(guild_id, user_ids)
    missing = user_ids - set(identities)
    if missing:
        # Members who left the guild still own their XP, so their identity is
        # resolved from the bot's user cache, which skips the guild member list.
        identities.update(_resolve_leaderboard_identities(missing))

    icon = getattr(guild, "icon", None)
    entries = []
    for rank, row in enumerate(rows, start=(page - 1) * page_size + 1):
        identity = identities.get(row["user_id"]) or {}
        entries.append({
            # Opaque, stable per process so the browser can animate a row that
            # changes rank without the API handing out Discord user ids.
            "key": leaderboard_cache.profile_key(row["user_id"]),
            "rank": rank,
            "level": row["level"],
            "xp": row["xp"],
            "xp_for_next": level_xp_for_next(row["level"]),
            "username": identity.get("username"),
            "display_name": identity.get("display_name"),
            "avatar_url": identity.get("avatar_url"),
        })

    return jsonify({
        "guild": {
            "id": str(guild.id),
            "name": guild.name,
            "icon_url": str(icon.url) if icon is not None else None,
            "member_count": int(
                getattr(guild, "member_count", 0) or len(getattr(guild, "members", []) or [])
            ),
        },
        "leveling_enabled": bool(get_runtime_level_config(guild_id).get("xp_enabled", True)),
        "entries": entries,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": (total + page_size - 1) // page_size,
    })


@app.route("/api/commands")
def api_commands():
    """Public endpoint — returns public bot commands from the startup registry."""
    raw_commands = load_json("data/commands.json", [])
    valid_types = {"slash", "prefix", "hybrid", "context"}
    internal_names = _live_internal_command_names()
    cmds = []
    for command in raw_commands if isinstance(raw_commands, list) else []:
        if not isinstance(command, dict) or not command.get("name"):
            continue
        if _is_internal_command(command.get("cog"), command.get("module")):
            continue
        command_name = str(command["name"])
        if command_name in internal_names or command_name.lower() in _LEGACY_INTERNAL_COMMAND_NAMES:
            continue
        normalized = {
            "name": str(command["name"]),
            "description": _description_value(command.get("description")),
            "category": str(command.get("category") or "utility"),
            "type": command.get("type") if command.get("type") in valid_types else "slash",
            "aliases": [str(item) for item in command.get("aliases", []) if item],
            "parameters": [
                {
                    "name": str(item.get("name") or ""),
                    "description": str(item.get("description") or ""),
                    "required": bool(item.get("required", False)),
                    "type": str(item.get("type") or "string"),
                }
                for item in command.get("parameters", [])
                if isinstance(item, dict) and item.get("name")
            ],
            "permissions": [str(item) for item in command.get("permissions", []) if item],
            "usage": str(command.get("usage") or ""),
            "subcommands": [str(item) for item in command.get("subcommands", []) if item],
        }
        if command.get("context_type") in {"user", "message"}:
            normalized["context_type"] = command["context_type"]
        cmds.append(normalized)
    category = request.args.get("category", "").strip().lower()
    if category:
        cmds = [c for c in cmds if c.get("category") == category]
    return jsonify(cmds)

@app.route("/api/health")
def api_health():
    return jsonify({"ok": True, "service": "niko-api", "static_build": os.path.exists(os.path.join(WEB_DIST_DIR, "index.html"))})

@app.route("/api/config")
def api_public_config():
    bot_avatar_url = None
    if _discord_bot is not None and getattr(_discord_bot, "user", None) is not None:
        try:
            bot_avatar_url = str(_discord_bot.user.display_avatar.url)
        except Exception:
            bot_avatar_url = None
    config = {
        "application_id": DISCORD_CLIENT_ID,
        "bot_avatar_url": bot_avatar_url,
        "invite_url": (
            f"https://discord.com/oauth2/authorize?"
            f"{urlencode({'client_id': DISCORD_CLIENT_ID, 'permissions': '8', 'scope': 'bot applications.commands'})}"
        ),
        "oauth_available": oauth_enabled(),
    }
    if _discord_bot is not None and getattr(_discord_bot, "loop", None) is not None and _discord_bot.loop.is_running():
        try:
            config["support_server_url"] = run_on_bot_loop(_current_support_invite())
        except Exception as exc:
            logging.warning("PublicConfig", f"Could not load current support invite: {exc}")
            config["support_server_url"] = None
    else:
        config["support_server_url"] = None
    return jsonify(config)

@app.route("/api/botstats")
def api_botstats():
    # Prefer live values from the running bot so the numbers are realtime
    # instead of the startup snapshot in data/bot_stats.json.
    if _discord_bot is not None and getattr(_discord_bot, "loop", None) is not None:
        try:
            live = run_on_bot_loop(_live_bot_stats(), timeout=5)
            if live:
                return jsonify(live)
        except Exception:
            pass

    stats = load_json(BOT_STATS, {})
    econ_count = len(glob.glob(os.path.join(ECONOMY_DIR, "[0-9]*.json")))
    return jsonify({
        "guild_count":   stats.get("guild_count", 0),
        "user_count":    stats.get("user_count", 0),
        "command_count": stats.get("command_count", 76),
        "uptime_since":  stats.get("uptime_since", None),
        "version":       stats.get("version", "1.0"),
        "economy_users": econ_count,
    })


async def _live_bot_stats():
    """Collect stats directly from the connected bot (runs on the bot loop)."""
    bot = _discord_bot
    if bot is None or not getattr(bot, "is_ready", lambda: False)():
        return None
    guilds = list(bot.guilds)
    user_count = sum(g.member_count or 0 for g in guilds)
    command_count = getattr(bot, "_status_command_count", None)
    if command_count is None:
        # The public registry uses the same filtering and deduplication as the
        # commands page, including nested slash commands and context menus.
        command_registry = load_json("data/commands.json", None)
        if isinstance(command_registry, list):
            command_count = sum(
                1 for command in command_registry
                if isinstance(command, dict)
                and command.get("name")
                and not _is_internal_command(command.get("cog"), command.get("module"))
                and str(command["name"]).lower() not in _LEGACY_INTERNAL_COMMAND_NAMES
                and str(command["name"]) not in _live_internal_command_names()
            )
        else:
            command_count = load_json(BOT_STATS, {}).get("command_count", 76)
    if not command_count:
        command_count = load_json(BOT_STATS, {}).get("command_count", 76)
    return {
        "guild_count":   len(guilds),
        "user_count":    user_count,
        "command_count": command_count,
        "uptime_since":  load_json(BOT_STATS, {}).get("uptime_since"),
        "version":       load_json(BOT_STATS, {}).get("version", "1.0"),
        "economy_users": len(glob.glob(os.path.join(ECONOMY_DIR, "[0-9]*.json"))),
    }
