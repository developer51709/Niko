"""Flask routes for site."""

from utils import logging

from .. import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

@app.route("/")
def root():
    # The home page's own Open Graph card and Discord component embed, rendered
    # from the build manifest at request time.
    return render_site_shell("/")

@app.route("/dashboard")
def dashboard_redirect():
    return send_from_directory(WEB_DIST_DIR, "index.html")

@app.route("/llms.txt")
def llms_index():
    return send_from_directory(WEB_DIST_DIR, "llms.txt", mimetype="text/plain")

@app.route("/docs/<slug>.md")
def docs_markdown(slug):
    return send_from_directory(WEB_DIST_DIR, f"docs/{slug}.md", mimetype="text/markdown")

@app.route("/changelog/<slug>.md")
def changelog_markdown(slug):
    return send_from_directory(WEB_DIST_DIR, f"changelog/{slug}.md", mimetype="text/markdown")

def _support_invite(bot) -> str | None:
    """The one public support-server invite, shared by everybody."""
    from cogs.staff.support_server import get_support_invite

    try:
        return run_on_bot_loop(get_support_invite(bot))
    except Exception as exc:
        logging.warning("PublicConfig", f"Could not load the support invite: {exc}")
        return None


def _referral_login():
    """Send the visitor through Discord, remembering where they were going."""
    # ``full_path`` keeps ``?ref=`` (which is the whole point) and appends a bare
    # "?" when there is no query, hence the strip.
    next_path = (request.full_path if request.query_string else request.path).rstrip("?")
    return redirect(f"/auth/login?next={quote(next_path, safe='')}")


def _referral_join(bot, referrer_id: int):
    """Join the support server through the visitor's own Discord account.

    This is what makes a referral checkable: Discord adds the account that
    authorized Niko, so the join is bound to a real identity instead of an
    invite-use counter. No invite is created for the visitor. A signed-in member
    is added and sent straight on; an anonymous visitor is asked to authorize
    first, because an invite carries no identity to attribute.
    """
    member_id = str(session.get("user", {}).get("id") or "")
    if not member_id.isdigit() or not ensure_access_token():
        return _referral_login()
    # A session authorized before referrals existed cannot add anybody until the
    # ``guilds.join`` scope is granted, so it goes back through Discord once.
    if "guilds.join" not in (session.get("oauth_scopes") or []):
        return _referral_login()

    from cogs.staff.support_referrals import join_with_referral

    try:
        result = run_on_bot_loop(
            join_with_referral(bot, int(member_id), referrer_id, session.get("access_token", ""))
        )
    except Exception as exc:
        logging.warning("Referrals", f"Could not complete the referral join for {member_id}: {exc}")
        result = {"status": "unavailable"}

    # Whatever happened, the visitor wanted the support server: hand them the
    # public invite. A refusal (Niko missing Create Invite, a revoked token) means
    # no credit, never a loop back through Discord.
    return redirect(_support_invite(bot) or "/discord")


@app.route("/discord")
def discord_invite_redirect():
    """The support server, with a referral join when the link carries one.

    ``/discord?ref=<user id>`` is the link a member shares. A request without
    ``ref`` — including Discord's own link-preview crawler — gets the page
    itself, so the preview keeps working.
    """
    ref = (request.args.get("ref") or "").strip()
    bot = _discord_bot
    if ref.isdigit() and bot is not None and getattr(bot, "cxn", None) is not None:
        return _referral_join(bot, int(ref))
    return serve_spa_shell()

@app.route("/discord/partnership")
def partnership_page():
    """The partnership ad: the page a partner pastes into their own server."""
    return serve_spa_shell()

@app.route("/commands")
@app.route("/leaderboard")
@app.route("/levels")
@app.route("/docs")
@app.route("/team")
@app.route("/support")
@app.route("/changelog")
@app.route("/community")
@app.route("/privacy")
@app.route("/terms")
@app.route("/data-removal")
@app.route("/donate")
@app.route("/billing")
@app.route("/transcript/<path:path>")
@app.route("/transcript")
def public_spa_route(path=None):
    return serve_spa_shell()

@app.route("/commands/<path:path>")
@app.route("/levels/<path:path>")
@app.route("/docs/<path:path>")
@app.route("/team/<path:path>")
@app.route("/changelog/<path:path>")
@app.route("/privacy/<path:path>")
@app.route("/terms/<path:path>")
@app.route("/data-removal/<path:path>")
@app.route("/community/<path:path>")
@app.route("/donate/<path:path>")
@app.route("/billing/<path:path>")
@app.route("/dashboard/<path:path>")
def nested_spa_route(path):
    return serve_spa_shell()

@app.route("/dashboard.html")
def legacy_dashboard_redirect():
    return redirect("/dashboard")
