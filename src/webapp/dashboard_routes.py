"""Flask routes for dashboard."""

from . import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

@app.route("/api/me")
@require_auth
def api_me():
    return jsonify(session["user"])

@app.route("/api/me/overview")
@require_auth
def api_me_overview():
    """Return the signed-in user's personal Niko profile and economy snapshot."""
    user_id = str(session["user"].get("id", ""))
    profiles = get_runtime_economy_rows()
    if profiles is None:
        # Compatibility for older web-only installs while the DB is unavailable.
        profiles = []
        for filepath in glob.glob(os.path.join(ECONOMY_DIR, "[0-9]*.json")):
            data = load_json(filepath, {})
            if isinstance(data, dict):
                profiles.append(_normalize_economy_row({
                    "user_id": os.path.basename(filepath).replace(".json", ""),
                    **data,
                }))

    profiles.sort(key=lambda row: row["net_worth"], reverse=True)
    rank = next(
        (index + 1 for index, row in enumerate(profiles) if row["user_id"] == user_id),
        None,
    )
    profile = next((row for row in profiles if row["user_id"] == user_id), {})

    return jsonify({
        "balance": profile.get("balance", 0),
        "bank": profile.get("bank", 0),
        "net_worth": profile.get("net_worth", 0),
        "level": profile.get("level", 0),
        "job": profile.get("job", "barista"),
        "daily_streak": profile.get("daily_streak", 0),
        "achievements": profile.get("achievements", 0),
        "total_earned": profile.get("total_earned", 0),
        "economy_rank": rank,
        "economy_profiles": len(profiles),
    })

@app.route("/api/guilds")
@require_auth
def api_guilds():
    """Guilds the user can manage, annotated with Niko's install state."""
    token = session.get("access_token", "")
    try:
        all_guilds = discord_get("/users/@me/guilds", token)
    except Exception:
        return jsonify([])

    present = bot_guild_ids()
    result  = []
    for g in all_guilds:
        try:
            perms = int(g.get("permissions", 0))
        except (TypeError, ValueError):
            perms = 0
        is_admin = bool(perms & (MANAGE_GUILD_PERM | ADMINISTRATOR_PERM)) or bool(g.get("owner"))
        if is_admin:
            icon_hash = g.get("icon")
            icon_url  = (
                f"https://cdn.discordapp.com/icons/{g['id']}/{icon_hash}.webp?size=64"
                if icon_hash else None
            )
            installed = str(g["id"]) in present
            result.append({
                "id":       g["id"],
                "name":     g["name"],
                "icon_url": icon_url,
                "owner":    bool(g.get("owner")),
                "permissions": perms,
                "installed": installed,
                "invite_url": (
                    f"https://discord.com/oauth2/authorize?"
                    f"{urlencode({'client_id': DISCORD_CLIENT_ID, 'permissions': '8', 'scope': 'bot applications.commands', 'guild_id': g['id']})}"
                    if not installed else None
                ),
            })
    session["managed_guild_ids"] = [guild["id"] for guild in result if guild["installed"]]
    session["managed_guilds_at"] = time.time()
    return jsonify(result)

@app.route("/api/guild/<guild_id>/overview")
@require_auth
@require_guild_access
def api_guild_overview(guild_id):
    # ── Warnings ──────────────────────────────────────────────
    warns      = load_json("data/warns.json", {})
    guild_warns = warns.get(guild_id, {})
    warn_count = sum(len(v) for v in guild_warns.values())

    # ── Automod quick status ──────────────────────────────────
    modcfg   = get_runtime_moderation_config(guild_id)
    automod  = modcfg.get("automod", {})
    automod_on = any(automod.values()) if isinstance(automod, dict) else False

    # ── Level leaderboard (quick top-5) ──────────────────────
    top_levels = _get_levels(guild_id)[:5]

    # ── Server activity (persisted daily by the bot's ServerStats cog) ──
    from datetime import datetime, timedelta, timezone

    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=13)
    activity_by_date = {}
    guild = _discord_bot.get_guild(int(guild_id)) if _discord_bot is not None else None
    if _discord_bot is not None and getattr(_discord_bot, "cxn", None):
        async def read_server_activity():
            pool = _discord_bot.cxn
            if getattr(pool, "db_type", None) == "mongodb" and hasattr(pool, "collection"):
                documents = await pool.collection("server_activity").find({
                    "$or": [
                        {"guild_id": int(guild_id)},
                        {"guild_id": str(guild_id)},
                        {"_id": {"$regex": rf"^{guild_id}_"}},
                    ],
                    "activity_date": {"$gte": start_date.isoformat()},
                }).to_list(length=None)
                rows = []
                for document in documents:
                    if str(document.get("guild_id", guild_id)) != str(guild_id):
                        continue
                    rows.append(document)
                return rows
            return await pool.fetch(
                "SELECT activity_date, messages, joins, leaves FROM server_activity "
                "WHERE guild_id = $1 AND activity_date >= $2 ORDER BY activity_date ASC",
                int(guild_id), start_date.isoformat(),
            )

        try:
            activity_rows = run_on_bot_loop(read_server_activity())
            activity_by_date = {str(row.get("activity_date")): row for row in activity_rows}
        except Exception:
            activity_by_date = {}

    activity = []
    for offset in range(14):
        activity_date = start_date + timedelta(days=offset)
        row = activity_by_date.get(activity_date.isoformat(), {})
        def safe_count(key):
            try:
                return max(0, int(row.get(key, 0) or 0))
            except (TypeError, ValueError):
                return 0
        activity.append({
            "date": activity_date.isoformat(),
            "messages": safe_count("messages"),
            "joins": safe_count("joins"),
            "leaves": safe_count("leaves"),
        })

    return jsonify({
        "server": {
            "member_count": int(getattr(guild, "member_count", 0) or 0),
            "channel_count": len(getattr(guild, "channels", []) or []) if guild else 0,
            "role_count": len(getattr(guild, "roles", []) or []) if guild else 0,
            "created_at": guild.created_at.isoformat() if guild else None,
            "activity": activity,
        },
        "moderation": {
            "warn_count":     warn_count,
            "automod_active": automod_on,
        },
        "leveling": {
            "top": top_levels,
        },
    })

@app.route("/api/guild/<guild_id>/levels")
@require_auth
@require_guild_access
def api_guild_levels(guild_id):
    return jsonify(_get_levels(guild_id))

@app.route("/api/guild/<guild_id>/config")
@require_auth
@require_guild_access
def api_guild_config(guild_id):
    modcfg  = get_runtime_moderation_config(guild_id)
    aicfg   = get_ai_config(int(guild_id))
    level_cfg = get_runtime_level_config(guild_id)

    try:
        server_cfg = _get_runtime_server_config(guild_id)
    except Exception as error:
        return jsonify({"error": f"Server settings are unavailable: {error}"}), 503

    return jsonify({
        "moderation": modcfg,
        "ai":         aicfg,
        "leveling":   level_cfg,
        "server":     server_cfg,
    })

@app.route("/api/guild/<guild_id>/resources")
@require_auth
@require_guild_access
def api_guild_resources(guild_id):
    guild = _discord_bot.get_guild(int(guild_id)) if _discord_bot is not None else None
    if guild is not None:
        cached_channels = list(guild.text_channels)
        channels = cached_channels
        if _discord_bot.loop.is_running():
            try:
                fetched_channels = run_on_bot_loop(guild.fetch_channels())
                channels = [
                    channel for channel in fetched_channels
                    if getattr(getattr(channel, "type", None), "name", "") in {"text", "news"}
                ]
            except Exception:
                pass
        channels = [
            {"id": str(channel.id), "name": str(channel.name)}
            for channel in channels
        ]
        roles = [
            {"id": str(role.id), "name": role.name}
            for role in guild.roles
            if not role.is_default()
        ]
        # A cached guild can exist briefly before its channels are populated.
        # Let the Discord API fallback below resolve names during that window.
        if channels:
            return jsonify({"channels": channels, "roles": roles})

    # The web process can briefly start before the gateway cache is ready. Use
    # Discord's bot endpoint in that case so saved channel IDs still resolve to
    # their real names instead of leaving the selectors empty.
    if DISCORD_BOT_TOKEN:
        try:
            response = req.get(
                f"{DISCORD_API}/guilds/{guild_id}/channels",
                headers={"Authorization": f"Bot {DISCORD_BOT_TOKEN}"},
                timeout=8,
            )
            response.raise_for_status()
            channels = response.json()
            if isinstance(channels, list):
                return jsonify({
                    "channels": [
                        {"id": str(channel["id"]), "name": str(channel.get("name") or "")}
                        for channel in channels
                        if channel.get("id") and channel.get("type") in {0, 5, 10, 11, 12}
                    ],
                    "roles": [],
                })
        except Exception:
            pass
    return jsonify({"channels": [], "roles": []})

@app.route("/api/guild/<guild_id>/config/automod", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_save_automod(guild_id):
    body = request.get_json(silent=True) or {}
    moderation = _discord_bot.get_cog("ModerationUtils") if _discord_bot is not None else None
    if moderation is not None:
        guild_config = moderation.get_guild_config(int(guild_id))
    else:
        guild_config = _read_moderation_config_sync(guild_id)
        if not guild_config:
            guild_config = {}

    allowed_flags = {
        "antispam", "antilink", "badwords", "massmention",
        "antinuke", "antiraid", "antiraid_ext",
    }
    existing = guild_config.get("automod", {})
    for key in allowed_flags:
        if key in body.get("automod", {}):
            existing[key] = bool(body["automod"][key])
    guild_config["automod"] = existing

    integer_fields = {
        "spam_threshold": (1, 100),
        "spam_interval": (1, 3600),
        "max_mentions": (1, 100),
    }
    for key, (minimum, maximum) in integer_fields.items():
        if key in body:
            try:
                value = int(body[key])
            except (TypeError, ValueError):
                return jsonify({"error": f"{key} must be a whole number."}), 400
            if not minimum <= value <= maximum:
                return jsonify({"error": f"{key} must be between {minimum} and {maximum}."}), 400
            guild_config[key] = value

    nested_fields = {
        "antinuke": {
            "ban_threshold": (1, 100), "kick_threshold": (1, 100),
            "channel_delete_threshold": (1, 100), "role_delete_threshold": (1, 100),
            "interval": (1, 3600),
        },
        "antiraid": {"join_threshold": (1, 1000), "join_interval": (1, 3600)},
        "antiraid_ext": {
            "interaction_threshold": (1, 1000), "interaction_window": (1, 3600),
            "join_age_limit": (1, 86400), "ext_app_threshold": (1, 1000),
            "ext_app_window": (1, 3600),
        },
    }
    for section, fields in nested_fields.items():
        incoming = body.get(section)
        if not isinstance(incoming, dict):
            continue
        target = guild_config.setdefault(section, {})
        for key, (minimum, maximum) in fields.items():
            if key in incoming:
                try:
                    value = int(incoming[key])
                except (TypeError, ValueError):
                    return jsonify({"error": f"{section}.{key} must be a whole number."}), 400
                if not minimum <= value <= maximum:
                    return jsonify({"error": f"{section}.{key} must be between {minimum} and {maximum}."}), 400
                target[key] = value
        for key, choices in {
            "action": {"strip", "kick", "ban"},
            "raider_action": {"kick", "ban", "softban", "slowmode", "lockdown"},
            "operator_action": {"notify", "kick", "ban"},
            "ext_app_action": {"kick", "ban", "warn"},
        }.items():
            if key in incoming and incoming[key] in choices:
                target[key] = incoming[key]
        if section == "antiraid_ext" and "ext_app_detection" in incoming:
            target["ext_app_detection"] = bool(incoming["ext_app_detection"])

    if moderation is not None:
        moderation.config[str(guild_id)] = guild_config
        moderation.save_config(int(guild_id))
    else:
        # No live bot: persist through the SQLite dashboard connection.
        conn = sqlite_connect()
        if conn is None:
            return jsonify({"error": "The bot database is unavailable."}), 503
        try:
            conn.execute(
                "INSERT OR REPLACE INTO moderation_config (guild_id, data) VALUES (?, ?)",
                (int(guild_id), json.dumps(guild_config)),
            )
            conn.commit()
        except sqlite3.Error:
            conn.rollback()
            return jsonify({"error": "The moderation settings could not be saved."}), 500
        finally:
            conn.close()
    return jsonify({"ok": True, "config": guild_config})

@app.route("/api/guild/<guild_id>/config/server", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_save_server(guild_id):
    """Persist prefixes, onboarding, logging, and ticket settings."""
    body = request.get_json(silent=True) or {}
    from utils.prefix_manager import add_prefix, reset_prefixes
    from utils.onboarding.config import load_config, save_config
    from cogs.logging.formatters import _load_log_config, _guild_config, _save_guild_log_config, CATEGORIES
    from utils.tickets.utils import get_ticket_config, update_ticket_config

    try:
        numeric_guild_id = int(guild_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid guild ID."}), 400

    prefixes = body.get("prefixes")
    if prefixes is not None:
        if not isinstance(prefixes, list):
            return jsonify({"error": "Prefixes must be a list."}), 400
        cleaned = []
        for prefix in prefixes:
            if not isinstance(prefix, str) or not prefix.strip() or len(prefix) > 10:
                return jsonify({"error": "Each prefix must be 1 to 10 characters."}), 400
            value = prefix.strip()
            if value not in cleaned:
                cleaned.append(value)
        if not cleaned:
            return jsonify({"error": "At least one prefix is required."}), 400
        reset_prefixes(numeric_guild_id)
        for prefix in cleaned:
            if prefix != ".":
                add_prefix(numeric_guild_id, prefix)

    channel_ids, role_ids = _guild_resource_ids(numeric_guild_id)
    if channel_ids == set() and role_ids == set():
        return jsonify({"error": "The selected server is not available to the bot."}), 503

    onboarding_data = body.get("onboarding")
    if onboarding_data is not None:
        if not isinstance(onboarding_data, dict):
            return jsonify({"error": "Onboarding settings must be an object."}), 400
        onboarding = run_on_bot_loop(load_config(numeric_guild_id))
        allowed = {
            "welcome_channel", "welcome_title", "welcome_description",
            "welcome_color", "welcome_image", "rules_channel", "rules_text",
            "rules_role_id", "autorole_ids", "captcha_enabled",
            "captcha_channel_id", "captcha_add_role_ids", "captcha_remove_role_ids",
            "captcha_kick_on_fail",
        }
        for key in set(onboarding_data) - allowed:
            return jsonify({"error": f"Unsupported onboarding field: {key}"}), 400
        id_fields = {
            "welcome_channel", "rules_channel", "rules_role_id",
            "captcha_channel_id",
        }
        for key, value in onboarding_data.items():
            if key in id_fields:
                if value in (None, ""):
                    setattr(onboarding, key, None)
                elif str(value).isdigit():
                    resource_ids = role_ids if key == "rules_role_id" else channel_ids
                    current_value = getattr(onboarding, key, None)
                    if (
                        resource_ids is not None
                        and str(value) not in resource_ids
                        and str(value) != str(current_value)
                    ):
                        return jsonify({"error": f"{key} does not belong to this server."}), 400
                    setattr(onboarding, key, int(value))
                else:
                    return jsonify({"error": f"{key} must be a valid Discord ID."}), 400
            elif key == "welcome_color":
                try:
                    color = int(str(value).replace("#", ""), 16) if value not in (None, "") else None
                except ValueError:
                    return jsonify({"error": "Welcome color must be a hexadecimal value."}), 400
                if color is not None and not 0 <= color <= 0xFFFFFF:
                    return jsonify({"error": "Welcome color must be a valid hexadecimal color."}), 400
                onboarding.welcome_color = color
            elif key in {"autorole_ids", "captcha_add_role_ids", "captcha_remove_role_ids"}:
                if not isinstance(value, list) or any(not str(item).isdigit() for item in value):
                    return jsonify({"error": f"{key} must contain valid Discord IDs."}), 400
                existing_role_ids = {str(item) for item in (getattr(onboarding, key, None) or [])}
                if role_ids is not None and any(
                    str(item) not in role_ids and str(item) not in existing_role_ids
                    for item in value
                ):
                    return jsonify({"error": f"{key} contains a role from another server."}), 400
                setattr(onboarding, key, [int(item) for item in value])
            elif key in {"captcha_enabled", "captcha_kick_on_fail"}:
                setattr(onboarding, key, bool(value))
            else:
                if value is not None and len(str(value)) > (2000 if key in {"welcome_description", "rules_text"} else 200):
                    return jsonify({"error": f"{key} is too long."}), 400
                setattr(onboarding, key, value or None)
        run_on_bot_loop(save_config(numeric_guild_id, onboarding))

    logging_data = body.get("logging")
    if logging_data is not None:
        if not isinstance(logging_data, dict):
            return jsonify({"error": "Logging settings must be an object."}), 400
        current = run_on_bot_loop(_load_log_config())
        logging_cfg = _guild_config(current, numeric_guild_id)
        for category, value in logging_data.items():
            if category == "disabled":
                if not isinstance(value, list) or any(item not in CATEGORIES for item in value):
                    return jsonify({"error": "Logging disabled categories are invalid."}), 400
                logging_cfg[category] = list(dict.fromkeys(value))
            elif category in CATEGORIES:
                if value in (None, ""):
                    logging_cfg[category] = None
                elif str(value).isdigit():
                    current_value = logging_cfg.get(category)
                    if (
                        channel_ids is not None
                        and str(value) not in channel_ids
                        and str(value) != str(current_value)
                    ):
                        return jsonify({"error": f"{category} does not belong to this server."}), 400
                    logging_cfg[category] = int(value)
                else:
                    return jsonify({"error": f"{category} must be a valid channel ID."}), 400
            else:
                return jsonify({"error": f"Unsupported logging category: {category}"}), 400
        run_on_bot_loop(_save_guild_log_config(numeric_guild_id, logging_cfg))

    tickets_data = body.get("tickets")
    if tickets_data is not None:
        if not isinstance(tickets_data, dict):
            return jsonify({"error": "Ticket settings must be an object."}), 400
        tickets = get_ticket_config(numeric_guild_id)
        allowed = {
            "panel_title", "panel_description", "panel_color", "panel_image",
            "panel_categories", "panel_channel_id", "support_roles",
        }
        unknown = set(tickets_data) - allowed
        if unknown:
            return jsonify({"error": f"Unsupported ticket fields: {', '.join(sorted(unknown))}"}), 400
        if "panel_title" in tickets_data:
            value = tickets_data["panel_title"]
            if value is not None and len(str(value)) > 200:
                return jsonify({"error": "Ticket panel title is too long."}), 400
            tickets.panel_title = str(value).strip() if value else None
        if "panel_description" in tickets_data:
            value = tickets_data["panel_description"]
            if value is not None and len(str(value)) > 2000:
                return jsonify({"error": "Ticket panel description is too long."}), 400
            tickets.panel_description = str(value).strip() if value else None
        if "panel_color" in tickets_data:
            value = tickets_data["panel_color"]
            try:
                tickets.panel_color = int(str(value).replace("#", ""), 16) if value not in (None, "") else None
            except ValueError:
                return jsonify({"error": "Ticket panel color must be hexadecimal."}), 400
        if "panel_image" in tickets_data:
            value = tickets_data["panel_image"]
            tickets.panel_image = str(value).strip() if value else None
        if "panel_categories" in tickets_data:
            categories = tickets_data["panel_categories"]
            if not isinstance(categories, list) or any(not isinstance(item, str) or not item.strip() for item in categories):
                return jsonify({"error": "Ticket categories must be a list of names."}), 400
            tickets.panel_categories = list(dict.fromkeys(item.strip()[:80] for item in categories))[:25]
        if "panel_channel_id" in tickets_data:
            value = tickets_data["panel_channel_id"]
            if value in (None, ""):
                tickets.panel_channel_id = None
            elif str(value).isdigit():
                current_value = tickets.panel_channel_id
                if (
                    channel_ids is not None
                    and str(value) not in channel_ids
                    and str(value) != str(current_value)
                ):
                    return jsonify({"error": "Ticket panel channel does not belong to this server."}), 400
                tickets.panel_channel_id = int(value)
            else:
                return jsonify({"error": "Ticket panel channel must be a valid channel ID."}), 400
        if "support_roles" in tickets_data:
            roles = tickets_data["support_roles"]
            if not isinstance(roles, list) or any(not str(item).isdigit() for item in roles):
                return jsonify({"error": "Support roles must contain valid Discord IDs."}), 400
            existing_role_ids = {str(item) for item in (tickets.support_roles or [])}
            if role_ids is not None and any(
                str(item) not in role_ids and str(item) not in existing_role_ids
                for item in roles
            ):
                return jsonify({"error": "Support roles contains a role from another server."}), 400
            tickets.support_roles = list(dict.fromkeys(int(item) for item in roles))
        update_ticket_config(numeric_guild_id, tickets)
        if _discord_bot is not None:
            try:
                run_on_bot_loop(_refresh_ticket_panel(numeric_guild_id))
            except Exception:
                pass

    try:
        config = _get_runtime_server_config(guild_id)
    except Exception as error:
        return jsonify({"error": f"Settings saved, but could not reload them: {error}"}), 503
    return jsonify({"ok": True, "config": config})

@app.route("/api/guild/<guild_id>/config/profile", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_save_profile(guild_id):
    """Apply and persist the bot's per-server Discord profile."""
    body = request.get_json(silent=True) or {}
    allowed = {"display_name", "bio", "avatar_url", "banner_url"}
    unknown = set(body) - allowed
    if unknown:
        return jsonify({"error": f"Unsupported profile fields: {', '.join(sorted(unknown))}"}), 400
    try:
        numeric_guild_id = int(guild_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid guild ID."}), 400

    current = _get_runtime_guild_profile(guild_id)
    profile = {**current}
    for key in allowed:
        if key in body:
            value = body[key]
            if value is not None and not isinstance(value, str):
                return jsonify({"error": f"{key} must be text or empty."}), 400
            profile[key] = value.strip() if isinstance(value, str) else None

    if profile["display_name"] and len(profile["display_name"]) > 32:
        return jsonify({"error": "Display name must be 32 characters or fewer."}), 400
    if profile["bio"] and len(profile["bio"]) > 190:
        return jsonify({"error": "Bio must be 190 characters or fewer."}), 400

    image_payload = {}
    for key in ("avatar_url", "banner_url"):
        value = profile[key]
        if not value:
            image_payload[key.removesuffix("_url")] = None
            continue
        parsed = urlparse(value)
        if parsed.scheme != "https" or not parsed.netloc:
            return jsonify({"error": f"{key} must be an HTTPS image URL."}), 400
        try:
            image_response = req.get(value, timeout=10, allow_redirects=False)
            image_response.raise_for_status()
            content_type = image_response.headers.get("Content-Type", "").split(";", 1)[0].lower()
            if not content_type.startswith("image/"):
                return jsonify({"error": f"{key} must point to an image."}), 400
            image_bytes = image_response.content
            if len(image_bytes) > 8 * 1024 * 1024:
                return jsonify({"error": f"{key} must be 8 MB or smaller."}), 400
            image_payload[key.removesuffix("_url")] = (
                f"data:{content_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
            )
        except Exception as error:
            return jsonify({"error": f"Could not fetch {key}: {error}"}), 400

    token = DISCORD_BOT_TOKEN
    if not token:
        return jsonify({"error": "The Discord bot token is not configured."}), 503
    patch_body = {
        "nick": profile["display_name"] or None,
        "bio": profile["bio"] or None,
        "avatar": image_payload["avatar"],
        "banner": image_payload["banner"],
    }
    response = req.patch(
        f"{DISCORD_API}/guilds/{numeric_guild_id}/members/@me",
        headers={"Authorization": f"Bot {token}", "Content-Type": "application/json"},
        json=patch_body,
        timeout=10,
    )
    if response.status_code not in (200, 204):
        return jsonify({"error": "Discord rejected the profile update.", "details": response.text[:300]}), 502

    try:
        _save_runtime_guild_profile(numeric_guild_id, profile)
    except Exception as error:
        return jsonify({"error": f"Profile applied, but could not persist it: {error}"}), 503
    return jsonify({"ok": True, "profile": profile})

@app.route("/api/guild/<guild_id>/config/ai", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_save_ai(guild_id):
    """Persist all AI settings through the database-backed config helper."""
    body = request.get_json(silent=True) or {}
    allowed = {
        "personality", "enabled", "ai_name",
        "ai_actions_experiment", "better_context_experiment",
        "multimodal_experiment",
    }
    unknown = set(body) - allowed
    if unknown:
        return jsonify({"error": f"Unsupported AI fields: {', '.join(sorted(unknown))}"}), 400
    if "personality" in body and body["personality"] not in {"cafe", "normal"}:
        return jsonify({"error": "Personality must be cafe or normal."}), 400
    if "ai_name" in body and len(str(body["ai_name"]).strip()) > 32:
        return jsonify({"error": "AI name must be 32 characters or fewer."}), 400

    guild_int = int(guild_id)
    for key in allowed:
        if key in body:
            set_ai_config(guild_int, key, body[key])
    return jsonify({"ok": True, "config": get_ai_config(guild_int)})

@app.route("/api/guild/<guild_id>/config/leveling", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_save_leveling(guild_id):
    body = request.get_json(silent=True) or {}
    allowed_actions = {"xp_enabled", "xp_multiplier", "xp_cooldown", "level_up_channel", "level_up_message"}
    unknown = set(body) - allowed_actions
    if unknown:
        return jsonify({"error": f"Unsupported leveling fields: {', '.join(sorted(unknown))}"}), 400
    try:
        multiplier = float(body.get("xp_multiplier", 1.0))
        cooldown = int(body.get("xp_cooldown", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "XP multiplier and cooldown must be valid numbers."}), 400
    if not 0.1 <= multiplier <= 10:
        return jsonify({"error": "XP multiplier must be between 0.1 and 10."}), 400
    if not 0 <= cooldown <= 86400:
        return jsonify({"error": "XP cooldown must be between 0 and 86400 seconds."}), 400
    channel = body.get("level_up_channel") or None
    if channel is not None and not str(channel).isdigit():
        return jsonify({"error": "Level-up channel must be a valid channel ID."}), 400
    message = body.get("level_up_message")
    if message is not None and len(str(message)) > 1000:
        return jsonify({"error": "Level-up message must be 1000 characters or fewer."}), 400

    leveling = _discord_bot.get_cog("Leveling") if _discord_bot is not None else None
    if leveling is not None and hasattr(leveling, "_guild_cfg") and hasattr(leveling, "_save_guild_cfg"):
        try:
            current = run_on_bot_loop(leveling._guild_cfg(int(guild_id)))
            current.update({
                "xp_enabled": bool(body.get("xp_enabled", current.get("xp_enabled", True))),
                "xp_multiplier": multiplier,
                "xp_cooldown": cooldown,
                "level_up_channel": int(channel) if channel else None,
                "level_up_message": message,
            })
            run_on_bot_loop(leveling._save_guild_cfg(int(guild_id), current))
            return jsonify({"ok": True, "config": current})
        except Exception:
            return jsonify({"error": "The leveling settings could not be saved through the live bot."}), 503

    conn = sqlite_connect()
    if conn is None:
        return jsonify({"error": "The bot database is unavailable."}), 503
    try:
        conn.execute(
            "INSERT OR REPLACE INTO level_config "
            "(guild_id, xp_enabled, xp_multiplier, xp_cooldown, level_up_channel, level_up_message, level_roles) "
            "VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT level_roles FROM level_config WHERE guild_id = ?), '{}'))",
            (
                int(guild_id), int(bool(body.get("xp_enabled", True))),
                multiplier, cooldown, int(channel) if channel else None, message,
                int(guild_id),
            ),
        )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        return jsonify({"error": "The leveling settings could not be saved."}), 500
    finally:
        conn.close()
    return jsonify({"ok": True, "config": get_runtime_level_config(guild_id)})
