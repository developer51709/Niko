"""Flask routes for the dashboard notifications tab.

The Discord notifier and this tab manage the same rows in the ``follows``
table, so every read and write goes through ``utils.social.follows`` and every
account is validated with the very same platform helpers the slash commands
use (``cogs.notifier.cog``). That means an account added here behaves exactly
like one added from Discord — same stored name, same seeded last post.

Validation talks to third-party APIs, which takes a moment, so those handlers
use a longer ``run_on_bot_loop`` timeout than the usual 8 seconds.
"""

from . import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

_PLATFORM_META = None


def _notifier_platforms():
    """Platform metadata for the picker, imported once and cached."""
    global _PLATFORM_META
    if _PLATFORM_META is None:
        try:
            from cogs.notifier import cog as notifier
            _PLATFORM_META = notifier.platform_catalog()
        except Exception:
            _PLATFORM_META = []
    return _PLATFORM_META


def _notifier_cxn():
    """The bot's database pool, or a 503-style failure."""
    cxn = getattr(_discord_bot, "cxn", None) if _discord_bot is not None else None
    if cxn is None:
        raise RuntimeError("The Discord bot is not available.")
    return cxn


def _notifier_limits():
    from utils.social.follows import (
        MAX_FOLLOWS_PER_GUILD,
        MAX_FOLLOWS_PER_PLATFORM,
        MAX_TEMPLATE_LENGTH,
        TEMPLATE_PLACEHOLDERS,
    )

    return {
        "max_follows": MAX_FOLLOWS_PER_GUILD,
        "max_follows_per_platform": MAX_FOLLOWS_PER_PLATFORM,
        "max_template_length": MAX_TEMPLATE_LENGTH,
        "template_placeholders": list(TEMPLATE_PLACEHOLDERS),
    }


def _clean_channel(value, valid_ids):
    """Validate an optional channel id against the live guild."""
    if value in (None, ""):
        return None
    text = str(value)
    if not text.isdigit():
        raise ValueError("Channel must be a Discord channel ID.")
    if valid_ids is not None and text not in valid_ids:
        raise ValueError("That channel does not belong to this server.")
    return int(text)


def _clean_role(value, valid_ids):
    """Validate an optional role id against the live guild."""
    if value in (None, ""):
        return None
    text = str(value)
    if not text.isdigit():
        raise ValueError("Role must be a Discord role ID.")
    if valid_ids is not None and text not in valid_ids:
        raise ValueError("That role does not belong to this server.")
    return int(text)


@app.route("/api/guild/<guild_id>/notifier")
@require_auth
@require_guild_access
def api_guild_notifier(guild_id):
    """Return the notifier setup plus every account this server follows."""
    from utils.social.follows import get_notifier_config, list_follows

    try:
        guild_number = int(guild_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid guild ID."}), 400

    try:
        cxn = _notifier_cxn()
        config = run_on_bot_loop(get_notifier_config(cxn, guild_number))
        follows = run_on_bot_loop(list_follows(cxn, guild_number))
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503
    except Exception:
        return jsonify({"error": "Social notifications are unavailable right now."}), 503

    for follow in follows:
        follow.pop("guild_id", None)
    return jsonify({
        "config": config,
        "follows": follows,
        "platforms": _notifier_platforms(),
        "limits": _notifier_limits(),
    })


@app.route("/api/guild/<guild_id>/notifier/config", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_save_notifier_config(guild_id):
    """Update the per-server switch, default channel and default ping role."""
    from utils.social.follows import save_notifier_config

    try:
        guild_number = int(guild_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid guild ID."}), 400

    body = request.get_json(silent=True) or {}
    channel_ids, role_ids = _guild_resource_ids(guild_number)
    if channel_ids == set() and role_ids == set():
        return jsonify({"error": "The selected server is not available to the bot."}), 503

    try:
        enabled = body.get("enabled")
        # Only touch a field the request actually mentions, so the tab can save
        # one setting without disturbing the others. An explicit empty value
        # clears it, which is how "no default channel" is expressed.
        channel_arg = None
        if "default_channel_id" in body:
            channel = _clean_channel(body.get("default_channel_id"), channel_ids)
            channel_arg = "" if channel is None else channel
        role_arg = None
        if "ping_role_id" in body:
            role = _clean_role(body.get("ping_role_id"), role_ids)
            role_arg = "" if role is None else role
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    try:
        cxn = _notifier_cxn()
        config = run_on_bot_loop(
            save_notifier_config(
                cxn,
                guild_number,
                enabled=None if enabled is None else bool(enabled),
                default_channel_id=channel_arg,
                ping_role_id=role_arg,
            )
        )
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503
    except Exception:
        return jsonify({"error": "Those notification settings could not be saved."}), 503

    return jsonify({"ok": True, "config": config})


@app.route("/api/guild/<guild_id>/notifier/follows", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_add_notifier_follow(guild_id):
    """Follow a social account, or re-point an existing follow at a channel.

    The account is validated through the notifier's own platform helpers so a
    typo is reported here instead of silently never posting anything.
    """
    from utils.social.follows import (
        FollowError,
        MAX_FOLLOWS_PER_GUILD,
        MAX_FOLLOWS_PER_PLATFORM,
        create_follow,
        get_follow,
        get_notifier_config,
        list_follows,
        update_follow,
        validate_template,
    )
    from cogs.notifier import cog as notifier

    try:
        guild_number = int(guild_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid guild ID."}), 400

    body = request.get_json(silent=True) or {}
    platform = str(body.get("platform") or "").strip().lower()
    query = str(body.get("query") or "").strip()
    if platform not in notifier.PLATFORMS:
        return jsonify({"error": "Choose one of the supported platforms."}), 400
    if not query:
        return jsonify({"error": "Enter the account you want to follow."}), 400
    if len(query) > 200:
        return jsonify({"error": "That account name is too long."}), 400

    try:
        template = validate_template(body.get("template"))
    except FollowError as error:
        return jsonify({"error": str(error)}), 400

    channel_ids, role_ids = _guild_resource_ids(guild_number)
    if channel_ids == set() and role_ids == set():
        return jsonify({"error": "The selected server is not available to the bot."}), 503

    try:
        cxn = _notifier_cxn()
        config = run_on_bot_loop(get_notifier_config(cxn, guild_number))
        channel = _clean_channel(body.get("channel_id"), channel_ids) or (
            int(config["default_channel_id"]) if config.get("default_channel_id") else None
        )
        role = _clean_role(
            body.get("ping_role_id"), role_ids
        ) or (int(config["ping_role_id"]) if config.get("ping_role_id") else None)
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        return jsonify({"error": "Social notifications are unavailable right now."}), 503

    if channel is None:
        return jsonify({"error": "Pick a channel for announcements."}), 400

    try:
        ok, stored = run_on_bot_loop(notifier.validate_account(platform, query), timeout=30)
    except Exception:
        return jsonify({"error": "That account could not be checked right now. Try again."}), 503
    if not ok:
        label = notifier.PLATFORMS[platform]["label"]
        return jsonify({"error": f"Could not find **{query}** as a {label}."}), 400

    try:
        existing = run_on_bot_loop(get_follow(cxn, guild_number, platform, stored))
        if existing is None:
            follows = run_on_bot_loop(list_follows(cxn, guild_number))
            if len(follows) >= MAX_FOLLOWS_PER_GUILD:
                return jsonify({
                    "error": f"This server already follows {MAX_FOLLOWS_PER_GUILD} accounts. Remove one first."
                }), 409
            same_platform = sum(1 for follow in follows if follow["platform"] == platform)
            if same_platform >= MAX_FOLLOWS_PER_PLATFORM:
                return jsonify({
                    "error": (
                        f"This server already follows {MAX_FOLLOWS_PER_PLATFORM} accounts on that "
                        "platform. Remove one first."
                    )
                }), 409
            post = run_on_bot_loop(notifier.fetch_latest_post(platform, stored), timeout=20)
            follow = run_on_bot_loop(
                create_follow(
                    cxn,
                    guild_id=guild_number,
                    platform=platform,
                    username=stored,
                    channel_id=channel,
                    last_post_id=(post or {}).get("id"),
                    template=template,
                    ping_role_id=role,
                )
            )
            created = True
        else:
            follow = run_on_bot_loop(
                update_follow(
                    cxn,
                    guild_id=guild_number,
                    platform=platform,
                    username=stored,
                    channel_id=channel,
                    template=template,
                    ping_role_id=role,
                    enabled=True,
                )
            )
            created = False
    except FollowError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        return jsonify({"error": "That account could not be saved right now."}), 503

    return jsonify({"ok": True, "created": created, "follow": follow})


@app.route("/api/guild/<guild_id>/notifier/follows/update", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_update_notifier_follow(guild_id):
    """Edit one follow: channel, ping role, template or paused state."""
    from utils.social.follows import FollowError, get_follow, update_follow, validate_template

    try:
        guild_number = int(guild_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid guild ID."}), 400

    body = request.get_json(silent=True) or {}
    platform = str(body.get("platform") or "").strip().lower()
    username = str(body.get("username") or "")
    if not platform or not username:
        return jsonify({"error": "A follow is required."}), 400

    fields: dict = {}
    try:
        if "template" in body:
            fields["template"] = validate_template(body.get("template"))
        if "enabled" in body:
            fields["enabled"] = bool(body.get("enabled"))
        channel_ids, role_ids = _guild_resource_ids(guild_number)
        if channel_ids == set() and role_ids == set():
            return jsonify({"error": "The selected server is not available to the bot."}), 503
        if "channel_id" in body:
            channel = _clean_channel(body.get("channel_id"), channel_ids)
            if channel is None:
                return jsonify({"error": "Pick a channel for announcements."}), 400
            fields["channel_id"] = channel
        if "ping_role_id" in body:
            fields["ping_role_id"] = _clean_role(body.get("ping_role_id"), role_ids)
    except FollowError as error:
        return jsonify({"error": str(error)}), 400
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    if not fields:
        return jsonify({"error": "Nothing to update."}), 400

    try:
        cxn = _notifier_cxn()
        follow = run_on_bot_loop(
            update_follow(cxn, guild_id=guild_number, platform=platform, username=username, **fields)
        )
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503
    except Exception:
        return jsonify({"error": "That follow could not be updated."}), 503

    if follow is None:
        return jsonify({"error": "That account is no longer followed."}), 404
    return jsonify({"ok": True, "follow": follow})


@app.route(
    "/api/guild/<guild_id>/notifier/follows/<platform>/<path:username>",
    methods=["DELETE"],
)
@require_auth
@require_guild_access
@require_csrf
def api_delete_notifier_follow(guild_id, platform, username):
    """Stop following one account."""
    from utils.social.follows import delete_follow
    from cogs.notifier import cog as notifier

    try:
        guild_number = int(guild_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid guild ID."}), 400
    if platform not in notifier.PLATFORMS:
        return jsonify({"error": "Unsupported platform."}), 400

    try:
        cxn = _notifier_cxn()
        removed = run_on_bot_loop(
            delete_follow(cxn, guild_id=guild_number, platform=platform, username=username)
        )
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503
    except Exception:
        return jsonify({"error": "That account could not be removed."}), 503

    if not removed:
        return jsonify({"error": "That account is no longer followed."}), 404
    return jsonify({"ok": True})


async def _send_test_notification(guild_number: int, follow: dict) -> dict:
    """Post a real notification for one follow so an admin can see the result."""
    from cogs.notifier import cog as notifier

    bot = _discord_bot
    guild = bot.get_guild(guild_number) if bot is not None else None
    if guild is None:
        raise RuntimeError("The selected server is not available to the bot.")
    channel = guild.get_channel(int(follow["channel_id"])) if follow.get("channel_id") else None
    if channel is None:
        raise ValueError("That announcement channel no longer exists. Pick another one.")

    post = await notifier.fetch_latest_post(follow["platform"], follow["username"])
    if not post:
        return {
            "ok": True,
            "delivered": False,
            "message": "The account could not be read right now, so nothing was sent.",
        }

    role = guild.get_role(int(follow["ping_role_id"])) if follow.get("ping_role_id") else None
    content, allowed_mentions = notifier.build_notification_content(
        platform=follow["platform"],
        username=follow["username"],
        post=post,
        template=follow.get("template") or "",
        role=role,
    )
    await channel.send(
        content=content,
        view=notifier.build_notification_view(follow["platform"], follow["username"], post),
        allowed_mentions=allowed_mentions,
    )
    return {"ok": True, "delivered": True, "channel_id": str(channel.id), "channel": channel.name}


@app.route("/api/guild/<guild_id>/notifier/test", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_test_notifier_follow(guild_id):
    """Send a sample notification for one followed account."""
    from utils.social.follows import get_follow

    try:
        guild_number = int(guild_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid guild ID."}), 400

    body = request.get_json(silent=True) or {}
    platform = str(body.get("platform") or "").strip().lower()
    username = str(body.get("username") or "")
    if not platform or not username:
        return jsonify({"error": "A follow is required."}), 400

    try:
        cxn = _notifier_cxn()
        follow = run_on_bot_loop(get_follow(cxn, guild_number, platform, username))
        if follow is None:
            return jsonify({"error": "That account is no longer followed."}), 404
        result = run_on_bot_loop(_send_test_notification(guild_number, follow), timeout=25)
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        return jsonify({"error": "The test notification could not be sent."}), 503

    return jsonify(result)
