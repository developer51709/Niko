"""Flask routes for public."""

from config import links as bot_links
from . import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
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
    return jsonify({
        "application_id": DISCORD_CLIENT_ID,
        "bot_avatar_url": bot_avatar_url,
        "invite_url": (
            f"https://discord.com/oauth2/authorize?"
            f"{urlencode({'client_id': DISCORD_CLIENT_ID, 'permissions': '8', 'scope': 'bot applications.commands'})}"
        ),
        "oauth_available": oauth_enabled(),
        "support_server_url": (
            getattr(bot_links, "SUPPORT_SERVER", "").strip() or None
            if isinstance(getattr(bot_links, "SUPPORT_SERVER", ""), str)
            else None
        ),
    })

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
