"""Flask routes for auth."""

from . import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

@app.route("/auth/login")
def auth_login():
    if not oauth_enabled():
        return jsonify({
            "error": "Discord OAuth is not configured.",
            "hint": "Add DISCORD_CLIENT_SECRET to your Replit secrets to enable login.",
        }), 503

    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    next_path = request.args.get("next", "/dashboard")
    session["oauth_next"] = next_path if next_path.startswith("/") and not next_path.startswith("//") else "/dashboard"

    params = urlencode({
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": redirect_uri(),
        "response_type": "code",
        "scope": "identify guilds",
        "state": state,
    })
    return redirect(f"https://discord.com/oauth2/authorize?{params}")

@app.route("/auth/callback")
def auth_callback():
    error = request.args.get("error")
    if error:
        return redirect("/?error=oauth_denied")

    if request.args.get("state") != session.pop("oauth_state", None):
        return redirect("/?error=invalid_state")

    code = request.args.get("code", "")
    if not code:
        return redirect("/?error=no_code")

    # Exchange code for access token
    token_resp = req.post(
        "https://discord.com/api/oauth2/token",
        data={
            "client_id":     DISCORD_CLIENT_ID,
            "client_secret": DISCORD_CLIENT_SECRET,
            "grant_type":    "authorization_code",
            "code":          code,
            "redirect_uri":  redirect_uri(),
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    if not token_resp.ok:
        return redirect("/?error=token_exchange_failed")

    token_data   = token_resp.json()
    access_token = token_data["access_token"]

    # Fetch user identity
    try:
        user = discord_get("/users/@me", access_token)
    except Exception:
        return redirect("/?error=user_fetch_failed")

    session["user"]         = user
    session["access_token"] = access_token
    session["refresh_token"] = token_data.get("refresh_token")
    session["token_exp"]    = time.time() + token_data.get("expires_in", 604800)

    return redirect(session.pop("oauth_next", "/dashboard"))

@app.route("/auth/logout")
def auth_logout():
    token = session.get("access_token")
    if token:
        try:
            req.post(
                f"{DISCORD_API}/oauth2/token/revoke",
                data={"client_id": DISCORD_CLIENT_ID, "client_secret": DISCORD_CLIENT_SECRET, "token": token},
                timeout=5,
            )
        except Exception:
            pass
    session.clear()
    return redirect("/")

@app.route("/auth/status")
def auth_status():
    if not ensure_access_token():
        return jsonify({
            "authenticated":   False,
            "oauth_available": oauth_enabled(),
        })
    session.setdefault("csrf_token", secrets.token_urlsafe(24))
    return jsonify({
        "authenticated":   True,
        "oauth_available": True,
        "user":            session["user"],
        "csrf_token":      session["csrf_token"],
    })
