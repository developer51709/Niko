"""Dashboard API for boost announcements and booster-role settings."""

import discord

from .. import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})


def _booster_pool():
    pool = getattr(_discord_bot, "cxn", None) if _discord_bot is not None else None
    if pool is None:
        raise RuntimeError("The Discord bot database is unavailable.")
    return pool


def _serialize_booster_config(config):
    return {
        "notifications_enabled": bool(config.get("notifications_enabled")),
        "roles_enabled": bool(config.get("roles_enabled")),
        "channel_id": str(config["channel_id"]) if config.get("channel_id") else "",
        "boost_message": str(config.get("boost_message") or ""),
        "unboost_message": str(config.get("unboost_message") or ""),
    }


@app.route("/api/guild/<guild_id>/boosters")
@require_auth
@require_guild_access
def api_guild_boosters(guild_id):
    from cogs.system.boosters import get_booster_config

    try:
        numeric_guild_id = int(guild_id)
        config = run_on_bot_loop(
            get_booster_config(_booster_pool(), numeric_guild_id)
        )
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid guild ID."}), 400
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503
    except Exception:
        app.logger.exception("Could not load booster settings for guild %s", guild_id)
        return jsonify({"error": "Booster settings are unavailable right now."}), 503

    return jsonify({
        "config": _serialize_booster_config(config),
        "placeholders": ["{user}", "{name}", "{server}", "{boost_count}", "{boost_level}"],
    })


@app.route("/api/guild/<guild_id>/boosters", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_save_guild_boosters(guild_id):
    from cogs.system.boosters import (
        DEFAULT_BOOST_MESSAGE,
        DEFAULT_UNBOOST_MESSAGE,
        get_booster_config,
    )

    try:
        numeric_guild_id = int(guild_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid guild ID."}), 400

    body = request.get_json(silent=True) or {}
    if not isinstance(body, dict):
        return jsonify({"error": "Send booster settings as a JSON object."}), 400
    allowed = {
        "notifications_enabled",
        "roles_enabled",
        "channel_id",
        "boost_message",
        "unboost_message",
    }
    unsupported = set(body) - allowed
    if unsupported:
        return jsonify({"error": f"Unsupported booster setting: {sorted(unsupported)[0]}"}), 400

    try:
        pool = _booster_pool()
        current = run_on_bot_loop(get_booster_config(pool, numeric_guild_id))
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503
    except Exception:
        app.logger.exception("Could not read booster settings for guild %s", guild_id)
        return jsonify({"error": "Booster settings are unavailable right now."}), 503

    config = dict(current)
    for key in ("notifications_enabled", "roles_enabled"):
        if key in body:
            if not isinstance(body[key], bool):
                return jsonify({"error": f"{key} must be true or false."}), 400
            config[key] = body[key]

    for key in ("boost_message", "unboost_message"):
        if key in body:
            value = body[key]
            if not isinstance(value, str) or len(value) > 2000:
                return jsonify({"error": f"{key} must be text of at most 2,000 characters."}), 400
            default = DEFAULT_BOOST_MESSAGE if key == "boost_message" else DEFAULT_UNBOOST_MESSAGE
            config[key] = value.strip() or default

    if "channel_id" in body:
        value = body["channel_id"]
        if value in (None, ""):
            config["channel_id"] = None
        elif isinstance(value, (str, int)) and str(value).isdigit():
            config["channel_id"] = int(value)
        else:
            return jsonify({"error": "Choose a valid text channel."}), 400

    if config["notifications_enabled"] and not config["channel_id"]:
        return jsonify({"error": "Choose a channel before enabling boost notifications."}), 400
    if config["notifications_enabled"] and (
        not config["boost_message"] or not config["unboost_message"]
    ):
        return jsonify({"error": "Boost and unboost messages cannot be blank while notifications are enabled."}), 400

    async def save():
        guild = _discord_bot.get_guild(numeric_guild_id)
        if guild is None:
            raise RuntimeError("The selected server is not available to the bot.")
        channel = (
            guild.get_channel(int(config["channel_id"]))
            if config["channel_id"]
            else None
        )
        if config["notifications_enabled"] and not isinstance(
            channel, discord.TextChannel
        ):
            raise ValueError("That announcement channel is not a text channel in this server.")
        if config["roles_enabled"]:
            bot_member = guild.get_member(_discord_bot.user.id) if _discord_bot.user else None
            if not bot_member or not bot_member.guild_permissions.manage_roles:
                raise ValueError("Niko needs Manage Roles in this server to create booster roles.")

        await pool.execute(
            "INSERT OR REPLACE INTO booster_config "
            "(guild_id, notifications_enabled, roles_enabled, channel_id, boost_message, unboost_message) "
            "VALUES ($1, $2, $3, $4, $5, $6)",
            numeric_guild_id,
            int(config["notifications_enabled"]),
            int(config["roles_enabled"]),
            config["channel_id"],
            config["boost_message"] or DEFAULT_BOOST_MESSAGE,
            config["unboost_message"] or DEFAULT_UNBOOST_MESSAGE,
        )

        if current["roles_enabled"] != config["roles_enabled"]:
            cog = _discord_bot.get_cog("BoosterRoles")
            if cog is not None:
                import asyncio
                asyncio.create_task(cog.sync_guild(guild))

    try:
        run_on_bot_loop(save())
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503
    except Exception:
        app.logger.exception("Could not save booster settings for guild %s", guild_id)
        return jsonify({"error": "Those booster settings could not be saved."}), 503

    return jsonify({"ok": True, "config": _serialize_booster_config(config)})
