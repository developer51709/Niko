"""Flask routes for public."""

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
    })

@app.route("/api/botstats")
def api_botstats():
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
