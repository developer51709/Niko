"""Flask routes for auth."""

from utils import logging

from .. import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

def _request_origin() -> str:
    """The address the visitor is on, honouring a proxy's forwarded scheme."""
    proto = (request.headers.get("X-Forwarded-Proto") or request.scheme).split(",")[0].strip() or request.scheme
    return f"{proto}://{runtime.request_host()}"


def _callback_origin() -> str:
    """The address Discord will send the visitor back to."""
    parts = urlparse(redirect_uri())
    return f"{parts.scheme}://{parts.netloc}" if parts.netloc else ""


def _same_site(first: str, second: str) -> bool:
    """Whether two origins sit under the same name, so cookies can be shared.

    ``dash.example.com`` and ``example.com`` are one site (the session cookie is
    set on the parent), while a preview host and the site it previews are not.
    """
    def host_of(origin: str) -> str:
        return (urlparse(origin).hostname or "").lower().strip(".")

    one, other = host_of(first), host_of(second)
    if not one or not other:
        return False
    return one == other or one.endswith("." + other) or other.endswith("." + one)


def _oauth_destination(path: str) -> str:
    """Where a finished sign-in lands, on the host that started it.

    The hop through Discord happens on the site's canonical address, so a
    visitor who signed in on ``dash.`` would otherwise end up on the apex long
    form of the dashboard. The origin comes from ``PUBLIC_URL`` rather than from
    the request, so a crafted ``Host`` header can never aim this redirect at
    another site.
    """
    prefix = session.pop("oauth_return", "")
    session.pop("oauth_start_host", None)
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

    host = runtime.request_host()
    next_path = request.args.get("next", "/dashboard")
    if not (next_path.startswith("/") and not next_path.startswith("//")):
        next_path = "/dashboard"
    # The OAuth state is a cookie on the host that starts the sign-in, and Discord
    # sends the visitor back to the host in the registered callback. When those
    # are different sites the cookie never comes back: the state check fails and
    # the sign-in ends as "link expired" with no clue why. Starting on the
    # address that receives the callback is the one place both halves meet.
    landing = _callback_origin()
    site = config.canonical_origin()
    if landing and not _same_site(landing, _request_origin()) and site and _same_site(landing, site):
        logging.warning(
            "Auth",
            f"Sign-in started on {_request_origin()} but the callback is {landing}; continuing on {landing}.",
        )
        target = f"{landing}/auth/login?next={quote(config.apex_path(host, next_path), safe='')}"
        return redirect(target)
    # A callback that names some other address is a configuration problem, not
    # something to follow: the visitor stays here and the callback says which
    # two addresses were involved when it arrives.

    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    # Where this started, so a failed return can say which two addresses were
    # involved instead of only "the link expired".
    session["oauth_start_host"] = host
    # A section host writes its paths short (``/staff`` on ``dash.``), while the
    # callback runs on the site's own address (``runtime.redirect_uri``), which
    # only knows the apex form: ``/dashboard/staff``. Without this a sign-in
    # started on the subdomain would come back to a page the apex does not have.
    session["oauth_next"] = config.apex_path(host, next_path)
    # Remember the section so the finished sign-in can be handed back to the
    # host it started on instead of the long form of the same page.
    session["oauth_return"] = config.subdomain_prefix(host)
    # One line per sign-in so a failed return can be traced: which address it
    # started on, which address Discord will send it back to, and where it was
    # headed.
    logging.info("Auth", f"Sign-in started on {_request_origin()} for {session['oauth_next']} (callback {redirect_uri()}).")

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

    expected = session.pop("oauth_state", None)
    if request.args.get("state") != expected:
        started = session.pop("oauth_start_host", "") or ""
        returned = runtime.request_host()
        # No state in the session at all means the cookie never came back with
        # this request — a different address, a blocked cookie, or a callback
        # that a previous visit already used. A state that is present but
        # different is a link that is not this session's.
        reason = "invalid_state" if expected else "no_state"
        logging.warning(
            "Auth",
            f"Discord sign-in could not be verified ({reason}): started on {started or 'unknown address'}, "
            f"returned to {returned}; session cookie domain "
            f"{app.config.get('SESSION_COOKIE_DOMAIN') or 'host-only'}, "
            f"secure {app.config.get('SESSION_COOKIE_SECURE')}.",
        )
        return redirect(f"/?{urlencode({'error': reason, 'from': started, 'to': returned})}")

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
