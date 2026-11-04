"""Flask routes for auth."""

from .. import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

def _oauth_destination(path: str) -> str:
    """Where a finished sign-in lands, on the host that started it.

    The hop through Discord happens on the site's canonical address, so a
    visitor who signed in on ``dash.`` would otherwise end up on the apex long
    form of the dashboard. The origin comes from ``PUBLIC_URL`` rather than from
    the request, so a crafted ``Host`` header can never aim this redirect at
    another site.
    """
    prefix = session.pop("oauth_return", "")
    origin = config.section_origins().get(prefix, "") if prefix else ""
    if not origin:
        return path
    return f"{origin}{config.public_path(prefix, path)}"


@app.route("/auth/login")
def auth_login():
    if not oauth_enabled():
        return jsonify({
            "error": "Discord OAuth is not configured.",
            "hint": "Add DISCORD_CLIENT_SECRET to your Replit secrets to enable login.",
        }), 503

    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    host = runtime.request_host()
    next_path = request.args.get("next", "/dashboard")
    if not (next_path.startswith("/") and not next_path.startswith("//")):
        next_path = "/dashboard"
    # A section host writes its paths short (``/staff`` on ``dash.``), while the
    # callback runs on the site's own address (``runtime.redirect_uri``), which
    # only knows the apex form: ``/dashboard/staff``. Without this a sign-in
    # started on the subdomain would come back to a page the apex does not have.
    session["oauth_next"] = config.apex_path(host, next_path)
    # Remember the section so the finished sign-in can be handed back to the
    # host it started on instead of the long form of the same page.
    session["oauth_return"] = config.subdomain_prefix(host)

    params = urlencode({
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": redirect_uri(),
        "response_type": "code",
        # ``guilds.join`` is what lets the site add a member to the support
        # server for a referral link (`/discord?ref=`), so the join is bound to
        # the account that authorized it instead of to an invite code.
        "scope": "identify guilds guilds.join",
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

    # Exchange code for access token. A blocked or unreachable Discord API is a
    # failed login, not a server error, so it stays a clean redirect.
    try:
        token_resp = discord_request(
            "POST",
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
        token_data = token_resp.json()
        access_token = token_data["access_token"]
        granted_scopes = str(token_data.get("scope") or "").split()
    except Exception:
        # A blocked or unreachable Discord API is a failed login, not a server
        # error, so it degrades to a friendly redirect instead of a 500 page.
        return redirect("/?error=token_exchange_failed")

    # Fetch user identity
    try:
        user = discord_get("/users/@me", access_token)
    except Exception:
        return redirect("/?error=user_fetch_failed")

    session["user"]         = user
    session["access_token"] = access_token
    session["refresh_token"] = token_data.get("refresh_token")
    session["token_exp"]    = time.time() + token_data.get("expires_in", 604800)
    # Which scopes this session actually holds. A referral join needs
    # ``guilds.join``, and a session that predates it has to re-authorize.
    session["oauth_scopes"] = granted_scopes

    return redirect(_oauth_destination(session.pop("oauth_next", "/dashboard")))

@app.route("/auth/logout")
def auth_logout():
    token = session.get("access_token")
    if token:
        try:
            discord_request(
                "POST",
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
    try:
        blacklist_entry = _current_user_blacklist_entry()
    except Exception:
        return jsonify({"error": "Account access could not be verified."}), 503
    return jsonify({
        "authenticated":   True,
        "oauth_available": True,
        "user":            session["user"],
        # Only decides whether the owner devtools button is rendered; every
        # devtools action it exposes is still a browser-local aid.
        "owner":           _is_owner(),
        "csrf_token":      session["csrf_token"],
        "blacklisted":     bool(blacklist_entry),
        "blacklist_reason": (blacklist_entry.get("reason") or "No reason provided.") if blacklist_entry else None,
    })
