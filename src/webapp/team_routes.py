"""Flask routes for team."""

from . import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

@app.route("/api/team")
def api_team():
    return jsonify(_load_staff_rows())

@app.route("/api/team/<user_id>")
def api_team_member(user_id):
    member = next((item for item in _load_staff_rows() if item["id"] == str(user_id)), None)
    if not member:
        return jsonify({"error": "Team member not found."}), 404
    return jsonify(member)

@app.route("/api/staff/me")
@require_auth
def api_staff_me():
    role = _current_staff_role()
    if not role:
        return jsonify({"error": "This area is restricted to Niko staff."}), 403
    member = next((item for item in _load_staff_rows() if item["id"] == str(session["user"]["id"])), None)
    return jsonify({"role": role, "role_label": "Owner" if role == "owner" else _staff_role_label(role), "profile": member or _staff_row({"user_id": session["user"]["id"], "role": role})})


@app.route("/api/staff/error-reports")
@require_auth
def api_staff_error_reports():
    role = _current_staff_role()
    if not role:
        return jsonify({"error": "This area is restricted to Niko staff."}), 403
    if _discord_bot is None:
        return jsonify({"error": "The Discord bot is not available."}), 503
    try:
        from utils.error_reports import list_error_reports
        reports = run_on_bot_loop(list_error_reports(_discord_bot, limit=100))
        return jsonify({"reports": reports, "count": len(reports)})
    except Exception:
        return jsonify({"error": "Error reports are temporarily unavailable."}), 503


_GUILD_MANAGEMENT_ROLES = {"owner", "developer", "head_admin"}


def _require_guild_management_role():
    role = _current_staff_role()
    if role not in _GUILD_MANAGEMENT_ROLES:
        return None, (jsonify({"error": "Guild management is restricted to the owner, developers, and Head Admins."}), 403)
    if _discord_bot is None:
        return None, (jsonify({"error": "The Discord bot is not available."}), 503)
    return role, None


@app.route("/api/staff/guilds")
@require_auth
def api_staff_guilds():
    role, error = _require_guild_management_role()
    if error:
        return error
    try:
        from utils.blacklist_manager import BlacklistManager
        manager = BlacklistManager()
        if not manager._loaded:
            run_on_bot_loop(manager.load())
        blacklisted = {str(entry["id"]): entry for entry in manager.get_guild_entries()}
        result = []
        for guild in sorted(_discord_bot.guilds, key=lambda item: item.name.casefold()):
            owner_id = str(getattr(guild, "owner_id", "") or "")
            bot_member = getattr(guild, "me", None)
            avatar_asset = getattr(bot_member, "guild_avatar", None) if bot_member else None
            banner_asset = getattr(bot_member, "guild_banner", None) if bot_member else None
            entry = blacklisted.get(str(guild.id))
            icon = getattr(guild, "icon", None)
            result.append({
                "id": str(guild.id),
                "name": guild.name,
                "icon_url": str(icon.url) if icon else None,
                "owner_id": owner_id or None,
                "owner_name": (getattr(guild.owner, "global_name", None) or getattr(guild.owner, "name", None)) if getattr(guild, "owner", None) else f"User {owner_id}" if owner_id else "Unknown owner",
                "member_count": int(getattr(guild, "member_count", 0) or 0),
                "channel_count": len(getattr(guild, "channels", ()) or ()),
                "created_at": guild.created_at.isoformat() if getattr(guild, "created_at", None) else None,
                "bot_avatar_url": str(avatar_asset.url) if avatar_asset else None,
                "bot_banner_url": str(banner_asset.url) if banner_asset else None,
                "profile_name": getattr(bot_member, "display_name", None) if bot_member else None,
                "blacklisted": entry is not None,
                "blacklist_reason": entry.get("reason") if entry else None,
                "bot_permissions": [
                    {"name": flag, "label": flag.replace("_", " ").title(), "granted": bool(getattr(getattr(bot_member, "guild_permissions", None), flag, False))}
                    for flag in __import__("discord").Permissions.VALID_FLAGS
                ] if bot_member else [],
                "role_count": len(getattr(guild, "roles", ()) or ()),
                "category_count": sum(1 for channel in getattr(guild, "channels", ()) if getattr(channel, "type", None) == __import__("discord").ChannelType.category),
            })
        return jsonify({"guilds": result, "count": len(result), "role": role})
    except Exception:
        return jsonify({"error": "Guild information is temporarily unavailable."}), 503


@app.route("/api/staff/guilds/<guild_id>/blacklist", methods=["POST"])
@require_auth
@require_csrf
def api_staff_guild_blacklist(guild_id):
    role, error = _require_guild_management_role()
    if error:
        return error
    if not guild_id.isdigit() or _discord_bot.get_guild(int(guild_id)) is None:
        return jsonify({"error": "That guild is not currently available to the bot."}), 404
    body = request.get_json(silent=True) or {}
    action = body.get("action")
    reason = str(body.get("reason", "")).strip()
    if action not in {"add", "remove"}:
        return jsonify({"error": "Choose add or remove for the blacklist action."}), 400
    if action == "add" and not reason:
        return jsonify({"error": "Enter a reason before blacklisting this guild."}), 400
    if len(reason) > 1000:
        return jsonify({"error": "Blacklist reason must be 1,000 characters or fewer."}), 400
    try:
        from utils.blacklist_manager import BlacklistManager
        manager = BlacklistManager()
        changed = run_on_bot_loop(
            manager.add_guild(int(guild_id), reason=reason, added_by=int(session["user"]["id"]))
            if action == "add" else manager.remove_guild(int(guild_id))
        )
        if not changed:
            return jsonify({"error": "The guild blacklist could not be changed."}), 409
        return jsonify({"ok": True, "blacklisted": action == "add"})
    except Exception:
        return jsonify({"error": "The guild blacklist could not be changed."}), 503


@app.route("/api/staff/guilds/<guild_id>/profile/reset", methods=["POST"])
@require_auth
@require_csrf
def api_staff_reset_guild_profile(guild_id):
    role, error = _require_guild_management_role()
    if error:
        return error
    if not guild_id.isdigit() or _discord_bot.get_guild(int(guild_id)) is None:
        return jsonify({"error": "That guild is not currently available to the bot."}), 404
    if not DISCORD_BOT_TOKEN:
        return jsonify({"error": "The Discord bot token is not configured."}), 503
    response = req.patch(
        f"{DISCORD_API}/guilds/{int(guild_id)}/members/@me",
        headers={"Authorization": f"Bot {DISCORD_BOT_TOKEN}", "Content-Type": "application/json"},
        json={"nick": None, "bio": None, "avatar": None, "banner": None, "display_name_font_id": None, "display_name_effect_id": None, "display_name_colors": None},
        timeout=10,
    )
    if response.status_code not in (200, 204):
        return jsonify({"error": "Discord rejected the guild profile reset.", "details": response.text[:250]}), 502
    try:
        if getattr(_discord_bot, "cxn", None):
            run_on_bot_loop(_discord_bot.cxn.execute("DELETE FROM guild_profiles WHERE guild_id = $1", int(guild_id)))
        conn = sqlite_connect()
        try:
            if conn:
                conn.execute("DELETE FROM guild_profiles WHERE guild_id = ?", (int(guild_id),))
                conn.commit()
        finally:
            if conn:
                conn.close()
    except Exception:
        return jsonify({"error": "Discord profile was reset, but stored style settings could not be cleared."}), 503
    return jsonify({"ok": True})


@app.route("/api/staff/guilds/<guild_id>/moderation-notice", methods=["POST"])
@require_auth
@require_csrf
def api_staff_moderation_notice(guild_id):
    role, error = _require_guild_management_role()
    if error:
        return error
    if not guild_id.isdigit():
        return jsonify({"error": "Invalid guild ID."}), 400
    guild = _discord_bot.get_guild(int(guild_id))
    if guild is None:
        return jsonify({"error": "That guild is not currently available to the bot."}), 404
    body = request.get_json(silent=True) or {}
    notice = str(body.get("message", "")).strip()
    if not notice or len(notice) > 1500:
        return jsonify({"error": "A moderation notice is required (up to 1,500 characters)."}), 400
    async def send_notice():
        owner = guild.owner or await _discord_bot.fetch_user(int(guild.owner_id))
        view = discord.ui.LayoutView(timeout=None)
        container = discord.ui.Container(
            discord.ui.TextDisplay(content="# Official moderation notice\n**Niko Moderation Team** · Formal server communication"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"### Server\n**{guild.name}** · `{guild.id}`"),
            discord.ui.TextDisplay(content=f"### Notice\n{notice}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="Please review this notice and contact the Niko support team if you need clarification."),
            accent_colour=discord.Colour(0xC8A882),
        )
        view.add_item(container)
        await owner.send(view=view, allowed_mentions=discord.AllowedMentions.none())
        return str(owner.id)
    try:
        import discord
        owner_id = run_on_bot_loop(send_notice())
        return jsonify({"ok": True, "recipient_id": owner_id})
    except Exception:
        return jsonify({"error": "The moderation notice could not be delivered to the guild owner."}), 502


@app.route("/api/staff/guilds/<guild_id>/invite", methods=["POST"])
@require_auth
@require_csrf
def api_staff_guild_invite(guild_id):
    role, error = _require_guild_management_role()
    if error:
        return error
    if not guild_id.isdigit():
        return jsonify({"error": "Invalid guild ID."}), 400
    guild = _discord_bot.get_guild(int(guild_id))
    if guild is None:
        return jsonify({"error": "That guild is not currently available to the bot."}), 404
    async def create_invite():
        channels = sorted(guild.text_channels, key=lambda channel: (not channel.permissions_for(guild.me).create_instant_invite, channel.position))
        channel = next((item for item in channels if item.permissions_for(guild.me).create_instant_invite), None)
        if channel is None:
            raise PermissionError("The bot does not have permission to create an invite in any text channel.")
        invite = await channel.create_invite(max_age=600, max_uses=1, unique=True, reason="Temporary staff operations invite")
        return {"url": invite.url, "channel": channel.name, "expires_in": 600, "max_uses": 1}
    try:
        return jsonify({"ok": True, **run_on_bot_loop(create_invite())})
    except PermissionError as error:
        return jsonify({"error": str(error)}), 403
    except Exception:
        return jsonify({"error": "Could not create a one-use invite for this guild."}), 502


@app.route("/api/staff/guilds/<guild_id>/leave", methods=["POST"])
@require_auth
@require_csrf
def api_staff_leave_guild(guild_id):
    role, error = _require_guild_management_role()
    if error:
        return error
    if not guild_id.isdigit():
        return jsonify({"error": "Invalid guild ID."}), 400
    guild = _discord_bot.get_guild(int(guild_id))
    if guild is None:
        return jsonify({"error": "That guild is not currently available to the bot."}), 404
    try:
        run_on_bot_loop(guild.leave())
        return jsonify({"ok": True})
    except Exception:
        return jsonify({"error": "The bot could not leave this guild."}), 502


@app.route("/api/staff/blacklist", methods=["GET", "POST"])
@require_auth
def api_staff_blacklist():
    if request.method == "POST":
        if not session.get("csrf_token") or request.headers.get("X-CSRF-Token") != session["csrf_token"]:
            return jsonify({"error": "Invalid request token. Refresh the dashboard and try again."}), 403
    role, error = _require_guild_management_role()
    if error:
        return error
    from utils.blacklist_manager import BlacklistManager
    manager = BlacklistManager()
    if not manager._loaded:
        run_on_bot_loop(manager.load())
    if request.method == "GET":
        def serialize_entries(entries):
            return [
                {**entry, "id": str(entry["id"]), "added_by": str(entry["added_by"]) if entry.get("added_by") is not None else None}
                for entry in entries
            ]
        return jsonify({
            "users": serialize_entries(manager.get_user_entries()),
            "guilds": serialize_entries(manager.get_guild_entries()),
        })
    body = request.get_json(silent=True) or {}
    entry_type = body.get("type")
    action = body.get("action")
    raw_id = str(body.get("id", ""))
    reason = str(body.get("reason", "")).strip()
    if entry_type not in {"user", "guild"} or action not in {"add", "remove", "update"} or not raw_id.isdigit():
        return jsonify({"error": "Choose a valid user or guild, action, and numeric ID."}), 400
    if len(reason) > 1000 or (action in {"add", "update"} and not reason):
        return jsonify({"error": "A reason of 1,000 characters or fewer is required."}), 400
    if entry_type == "guild" and action in {"add", "update"} and _discord_bot.get_guild(int(raw_id)) is None:
        return jsonify({"error": "Guild entries can only target guilds currently connected to the bot."}), 404
    try:
        if entry_type == "user":
            changed = run_on_bot_loop(manager.add_user(int(raw_id), reason=reason, added_by=int(session["user"]["id"]))) if action == "add" else run_on_bot_loop(manager.remove_user(int(raw_id))) if action == "remove" else run_on_bot_loop(manager.update_user_reason(int(raw_id), reason))
        else:
            changed = run_on_bot_loop(manager.add_guild(int(raw_id), reason=reason, added_by=int(session["user"]["id"]))) if action == "add" else run_on_bot_loop(manager.remove_guild(int(raw_id))) if action == "remove" else run_on_bot_loop(manager.update_guild_reason(int(raw_id), reason))
        if not changed:
            return jsonify({"error": "No blacklist change was made. Check whether the entry already exists."}), 409
        return jsonify({"ok": True})
    except Exception:
        return jsonify({"error": "The blacklist could not be updated."}), 503

@app.route("/api/staff/profile", methods=["POST"])
@require_auth
@require_csrf
def api_save_staff_profile():
    role = _current_staff_role()
    if not role:
        return jsonify({"error": "This area is restricted to Niko staff."}), 403
    body = request.get_json(silent=True) or {}
    allowed = {"public_bio", "public_banner_url", "public_links", "public_visible"}
    values = {key: body[key] for key in allowed if key in body}
    if "public_bio" in values and len(str(values["public_bio"] or "")) > 1200:
        return jsonify({"error": "Your public bio must be 1200 characters or fewer."}), 400
    if "public_links" in values:
        raw_links = values["public_links"]
        if not isinstance(raw_links, list) or len(raw_links) > 10:
            return jsonify({"error": "Add no more than 10 profile links."}), 400
        allowed_link_types = {
            "website": "Website", "github": "GitHub", "instagram": "Instagram",
            "x": "X", "tiktok": "TikTok", "youtube": "YouTube",
            "twitch": "Twitch", "bluesky": "Bluesky", "linkedin": "LinkedIn",
            "reddit": "Reddit", "mastodon": "Mastodon", "facebook": "Facebook",
            "discord": "Discord", "other": "Other",
        }
        links = []
        for link in raw_links:
            if not isinstance(link, dict):
                return jsonify({"error": "Each profile link needs a type and URL."}), 400
            link_type = str(link.get("type", "")).strip()
            url = str(link.get("url", "")).strip()
            if link_type not in allowed_link_types:
                return jsonify({"error": "Choose a valid type for each profile link."}), 400
            parsed_url = urlparse(url)
            if not url or len(url) > 2048 or parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
                return jsonify({"error": f"Enter a valid http:// or https:// URL for your {allowed_link_types[link_type]} link."}), 400
            links.append({"type": link_type, "label": allowed_link_types[link_type], "url": url})
        values["public_links"] = json.dumps(links)
    user_id = int(session["user"]["id"])
    if values and _discord_bot is not None and getattr(_discord_bot, "cxn", None):
        async def save_to_bot():
            # Owners can be exposed through OWNER_IDS without having a row in
            # staff_members. Seed that row before applying the profile update.
            await _discord_bot.cxn.execute(
                "INSERT OR IGNORE INTO staff_members (user_id, role, assigned_by, assigned_at) VALUES ($1, $2, $3, $4)",
                user_id, role, user_id, int(time.time()),
            )
            assignments = ", ".join(f"{key} = ${index + 1}" for index, key in enumerate(values))
            params = [*values.values(), user_id]
            await _discord_bot.cxn.execute(
                f"UPDATE staff_members SET {assignments} WHERE user_id = ${len(params)}",
                *params,
            )
            try:
                from cogs.staff.staff import sync_member_staff_roles
                guild = _discord_bot.get_guild(SUPPORT_GUILD)
                member = guild.get_member(user_id) if guild else None
                if member:
                    current_role = await _discord_bot.cxn.fetchrow("SELECT role FROM staff_members WHERE user_id = $1", user_id)
                    await sync_member_staff_roles(_discord_bot, member, str(current_role["role"]) if current_role else None)
            except Exception:
                pass
        try:
            run_on_bot_loop(save_to_bot())
            return jsonify({"ok": True})
        except Exception:
            pass

    conn = sqlite_connect()
    try:
        assignments = ", ".join(f"{key} = ?" for key in values)
        if assignments and conn:
            conn.execute(
                "INSERT OR IGNORE INTO staff_members (user_id, role, assigned_by, assigned_at) VALUES (?, ?, ?, ?)",
                (user_id, role, user_id, int(time.time())),
            )
            conn.execute(f"UPDATE staff_members SET {assignments} WHERE user_id = ?", (*values.values(), user_id))
            conn.commit()
    finally:
        if conn:
            conn.close()
    return jsonify({"ok": True})

@app.route("/api/staff/global-profile", methods=["POST"])
@require_auth
@require_csrf
def api_save_global_profile():
    role = _current_staff_role()
    if STAFF_PRIORITY.get(role or "", 0) < STAFF_PRIORITY["graphic_designer"]:
        return jsonify({"error": "Only the Graphic Designer, Head Admin, or owner can change Niko's global profile."}), 403
    body = request.get_json(silent=True) or {}
    avatar_url, banner_url = body.get("avatar_url"), body.get("banner_url")
    if not avatar_url and not banner_url:
        return jsonify({"error": "Provide an avatar or banner URL."}), 400
    conn = sqlite_connect()
    try:
        if conn:
            conn.execute("INSERT OR REPLACE INTO global_profile (id, avatar_url, banner_url, updated_by, updated_at) VALUES (1, COALESCE(?, (SELECT avatar_url FROM global_profile WHERE id = 1)), COALESCE(?, (SELECT banner_url FROM global_profile WHERE id = 1)), ?, ?)", (avatar_url, banner_url, int(session["user"]["id"]), time.time()))
            conn.commit()
    finally:
        if conn:
            conn.close()
    # Apply remote media to Discord when the live bot is available.
    if _discord_bot is not None and getattr(_discord_bot, "user", None) is not None:
        try:
            media = {}
            for field, url in (("avatar", avatar_url), ("banner", banner_url)):
                if url:
                    response = req.get(str(url), timeout=12)
                    response.raise_for_status()
                    media[field] = response.content
            awaitable = _discord_bot.user.edit(**media)
            run_on_bot_loop(awaitable)
        except Exception as error:
            return jsonify({"error": f"Profile saved, but Discord rejected the media: {error}"}), 502
    return jsonify({"ok": True})
