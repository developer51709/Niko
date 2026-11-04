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


#: How long a sign-in link may take to come back from Discord.
_OAUTH_STATE_MAX_AGE = 900


def _secret() -> bytes:
    """The key the state signature and the session cookie share."""
    key = app.secret_key
    return key if isinstance(key, bytes) else str(key or "").encode()


def _sign(payload: str) -> str:
    return hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()


def _encode_oauth_state(next_path: str, prefix: str, host: str) -> str:
    """The ``state`` parameter: where the sign-in goes back to, signed.

    Everything the callback needs travels in the parameter itself, so the sign-in
    never depends on a cookie coming back with it. That is not paranoia: the site
    once shared its session cookie on the whole domain, browsers kept sending the
    old host-only copy alongside the new one, and the server read the stale one,
    which is what made every callback report an expired link. A value the client
    cannot alter needs no cookie at all — the signature is the check, and it is
    what makes the response provably belong to a sign-in this site started.
    """
    payload = json.dumps(
        {"n": next_path, "r": prefix, "h": host, "t": int(time.time())},
        separators=(",", ":"),
    )
    encoded = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
    return f"{encoded}.{_sign(encoded)}"


def _decode_oauth_state(value: str) -> dict:
    """The sign-in a returned ``state`` describes, or {} when it is not ours."""
    encoded, _, signature = (value or "").partition(".")
    if not encoded or not signature:
        return {}
    if not hmac.compare_digest(_sign(encoded), signature):
        return {}
    try:
        payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    if int(payload.get("t") or 0) + _OAUTH_STATE_MAX_AGE < time.time():
        return {}
    next_path = str(payload.get("n") or "")
    # The same rule ``/auth/login`` applies to ``next=``: a path on this site.
    if not next_path.startswith("/") or next_path.startswith("//"):
        return {}
    return payload


def _drop_legacy_session_cookie(response):
    """Remove the pre-rename ``session`` cookie, in both of its forms.

    Leaving it behind costs nothing on the server (it is never read again) but it
    is dead weight in every request, and its host-only and domain copies are what
    shadowed each other in the first place.
    """
    response.delete_cookie("session", path="/")
    domain = app.config.get("SESSION_COOKIE_DOMAIN") or None
    if domain:
        response.delete_cookie("session", path="/", domain=domain)
    return response


def _oauth_destination(prefix: str, path: str) -> str:
    """Where a finished sign-in lands, on the host that started it.

    The hop through Discord happens on the site's canonical address, so a
    visitor who signed in on ``dash.`` would otherwise end up on the apex long
    form of the dashboard. The origin comes from ``PUBLIC_URL`` rather than from
    the request, so a crafted ``Host`` header can never aim this redirect at
    another site.
    """
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
    # Discord sends the visitor back to the address in the registered callback,
    # so a sign-in started on some other site has to continue there: the session
    # it ends in belongs to the callback's site, and a visitor who finished it
    # elsewhere would arrive signed out.
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

    # A section host writes its paths short (``/staff`` on ``dash.``) while the
    # callback runs on the site's own address (``runtime.redirect_uri``), which
    # only knows the apex form: ``/dashboard/staff``. The section is remembered
    # too, so the finished sign-in goes back to the host it started on.
    callback = redirect_uri()
    state = _encode_oauth_state(config.apex_path(host, next_path), config.subdomain_prefix(host), host)
    # One line per sign-in so a failed return can be traced: which address it
    # started on, which address Discord will send it back to, and where it was
    # headed.
    logging.info("Auth", f"Sign-in started on {_request_origin()} for {config.apex_path(host, next_path)} (callback {callback}).")

    params = urlencode({
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": callback,
        "response_type": "code",
        # ``guilds.join`` is what lets the site add a member to the support
        # server for a referral link (`/discord?ref=`), so the join is bound to
        # the account that authorized it instead of to an invite code.
        "scope": "identify guilds guilds.join",
        "state": state,
    })
    return _drop_legacy_session_cookie(redirect(f"https://discord.com/oauth2/authorize?{params}"))

@app.route("/auth/callback")
def auth_callback():
    error = request.args.get("error")
    if error:
        return _drop_legacy_session_cookie(redirect("/?error=oauth_denied"))

    returned = runtime.request_host()
    requested_state = request.args.get("state", "")
    sign_in = _decode_oauth_state(requested_state)
    if not sign_in:
        # No state at all usually means the callback was opened directly; a state
        # that is present but does not verify is an old or altered link. Either
        # way the address and the cookies that arrived are worth naming: that is
        # how a duplicate session cookie was finally caught shadowing the real
        # one, which no amount of guessing from the browser could have shown.
        reason = "invalid_state" if requested_state else "no_state"
        logging.warning(
            "Auth",
            f"Discord sign-in could not be verified ({reason}): returned to {returned}; "
            f"cookies sent: {', '.join(sorted(request.cookies.keys())) or 'none'}.",
        )
        response = redirect(f"/?{urlencode({'error': reason, 'to': returned})}")
        return _drop_legacy_session_cookie(response)

    code = request.args.get("code", "")
    if not code:
        return _drop_legacy_session_cookie(redirect("/?error=no_code"))

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
            return _drop_legacy_session_cookie(redirect("/?error=token_exchange_failed"))
        token_data = token_resp.json()
        access_token = token_data["access_token"]
        granted_scopes = str(token_data.get("scope") or "").split()
    except Exception:
        # A blocked or unreachable Discord API is a failed login, not a server
        # error, so it degrades to a friendly redirect instead of a 500 page.
        return _drop_legacy_session_cookie(redirect("/?error=token_exchange_failed"))

    # Fetch user identity
    try:
        user = discord_get("/users/@me", access_token)
    except Exception:
        return _drop_legacy_session_cookie(redirect("/?error=user_fetch_failed"))

    session["user"]         = user
    session["access_token"] = access_token
    session["refresh_token"] = token_data.get("refresh_token")
    session["token_exp"]    = time.time() + token_data.get("expires_in", 604800)
    # Which scopes this session actually holds. A referral join needs
    # ``guilds.join``, and a session that predates it has to re-authorize.
    session["oauth_scopes"] = granted_scopes

    response = redirect(_oauth_destination(str(sign_in.get("r") or ""), str(sign_in.get("n") or "/dashboard")))
    return _drop_legacy_session_cookie(response)

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
    return _drop_legacy_session_cookie(redirect("/"))

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
