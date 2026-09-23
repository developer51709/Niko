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
