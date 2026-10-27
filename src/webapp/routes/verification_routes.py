"""Human verification completed in the browser.

A member presses Verify in Discord, the bot replies with a single-use link, and
that link lands here. The page is deliberately outside the React site (see
``webapp/verification_page.py``): it is the only page in the deployment that
carries advertising, and it has to load as one small document.

The challenge is stored server-side, so this route never trusts anything the
browser sends except the token and the typed code. The token is the only thing
that identifies the member — there is no session — and it is deleted the moment
it is answered, so a link cannot be replayed to re-run the role changes.
"""

from .. import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

import utils.onboarding.captcha as captcha_image
from flask import Response, request
from utils.onboarding.config import load_config
from utils.verification import ip_intel, modes, service, store
from .. import verification_page


def _pool():
    """The bot's database pool, or None when the bot is not running."""
    return getattr(_discord_bot, "cxn", None)


def _await(coroutine, timeout: float = 8):
    """Run a coroutine on the bot loop, closing it if it is never scheduled."""
    try:
        return run_on_bot_loop(coroutine, timeout=timeout)
    except Exception:
        coroutine.close()
        raise


def _respond(rendered, *, status: int | None = None) -> Response:
    html, default_status = rendered
    response = Response(html, mimetype="text/html", status=status or default_status)
    # The page is personal to one member and its captcha must never be cached
    # by a shared proxy, so it is explicitly unstoreable.
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return response


def _unavailable() -> tuple[str, int]:
    """The bot loop or database is unreachable: a 503, not a silent 200."""
    return verification_page.notice_page(
        "Verification is unavailable",
        "Niko could not reach the server right now. Let a staff member know, then try again in a few minutes.",
        ad=False, status=503,
    )


def _expired() -> tuple[str, int]:
    return verification_page.notice_page(
        "This link has expired",
        "Open Discord and press <strong>Verify</strong> again to get a fresh link. Links last 30 minutes.",
        tone="expired", ad=False,
    )


def _refusal(cfg) -> str | None:
    """Whether this connection may verify at all, per the server's settings."""
    return ip_intel.refusal(
        ip_intel.client_ip(request.remote_addr, request.headers.get("X-Forwarded-For")),
        bool(cfg.captcha_block_proxies),
        bool(cfg.captcha_block_vpn),
    )


def _blocked(reason: str) -> tuple[str, int]:
    if reason == "proxy":
        message = (
            "This server asks members to verify without a proxy, VPN, or Tor. "
            "Turn it off for this site, then reload this page."
        )
    else:
        message = (
            "This server asks members to verify from a normal connection. "
            "This one looks like a hosting or VPN address — try a different network, then reload."
        )
    return verification_page.notice_page("Verification blocked", message, tone="blocked", ad=False)


def _challenge(token: str):
    """The live challenge and its guild's config, or an error response.

    Returns ``(challenge, cfg, None)`` or ``(None, None, rendered_error)``.
    """
    try:
        challenge = _await(store.get(_pool(), token))
    except Exception:
        return None, None, _unavailable()
    if challenge is None:
        return None, None, _expired()
    try:
        cfg = _await(load_config(challenge["guild_id"]))
    except Exception:
        return None, None, _unavailable()
    # The server can switch method (or switch verification off) while a link is
    # outstanding; the link must not outlive that decision.
    if not cfg.captcha_enabled or modes.normalize_mode(cfg.captcha_mode) != modes.WEB:
        return None, None, verification_page.notice_page(
            "Verification is off",
            "This server is no longer using the website verification method. Press <strong>Verify</strong> in Discord instead.",
            tone="expired", ad=False,
        )
    return challenge, cfg, None


def _guild_name(guild_id: int) -> str:
    guild = service.get_guild(_discord_bot, guild_id)
    return getattr(guild, "name", "") or "this server"


@app.route("/verify")
@app.route("/verify/")
def verification_entry_page():
    """The stable verification page, and the only always-on ad surface.

    A-ADS requires one page to carry the ad unit permanently at a fixed URL, so
    this route deliberately depends on nothing: no token, no session, no bot, no
    database. Register ``<site>/verify`` as the ad unit's page in the A-ADS
    dashboard — a challenge link, which expires, cannot satisfy that requirement.
    The trailing-slash spelling is an alias rather than a redirect, so a checker
    that normalises the URL still lands on the page with the unit in the HTML.
    """
    return _respond(verification_page.entry_page())


@app.route("/verify/<token>")
def verification_challenge_page(token: str):
    """The captcha form for one challenge."""
    challenge, cfg, error = _challenge(token)
    if error is not None:
        return _respond(error)
    reason = _refusal(cfg)
    if reason:
        return _respond(_blocked(reason))
    return _respond(verification_page.challenge_page(
        token=token,
        guild_name=_guild_name(challenge["guild_id"]),
        attempts_left=max(0, store.MAX_ATTEMPTS - int(challenge.get("attempts") or 0)),
        attempt=int(challenge.get("attempts") or 0),
    ))


@app.route("/verify/<token>/captcha.png")
def verification_captcha_image(token: str):
    """The code image, drawn from the stored answer.

    Re-rendered per request rather than stored: the row holds the code, and the
    image is the only place that code is shown, so there is nothing to leak by
    keeping it. Drawn dark to match the page it sits on.
    """
    try:
        challenge = _await(store.get(_pool(), token))
    except Exception:
        return Response(status=503)
    if challenge is None:
        return Response(status=404)
    try:
        image = captcha_image.render_captcha(challenge["code"], dark=True)
    except Exception:
        return Response(status=503)
    response = Response(image.getvalue(), mimetype="image/png")
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.route("/verify/<token>", methods=["POST"])
def verification_submit(token: str):
    """Check the typed code and, on success, apply the server's roles."""
    challenge, cfg, error = _challenge(token)
    if error is not None:
        return _respond(error)
    reason = _refusal(cfg)
    if reason:
        return _respond(_blocked(reason))

    # An empty submission is not a wrong answer — pressing Enter in an empty
    # field should re-prompt, not spend one of the three attempts.
    answer = (request.form.get("answer") or "").strip()
    if not answer:
        return _respond(verification_page.challenge_page(
            token=token,
            guild_name=_guild_name(challenge["guild_id"]),
            attempts_left=max(0, store.MAX_ATTEMPTS - int(challenge.get("attempts") or 0)),
            attempt=int(challenge.get("attempts") or 0),
            error="Type the characters shown in the image.",
        ))

    guild_id = challenge["guild_id"]
    user_id = challenge["user_id"]

    if answer.upper() == str(challenge["code"]).upper():
        try:
            _await(store.consume(_pool(), token))
        except Exception:
            return _respond(_unavailable())
        try:
            result = _await(service.complete(
                _discord_bot, guild_id, user_id,
                source=modes.LABELS[modes.WEB],
            ))
        except Exception:
            return _respond(_unavailable())
        return _respond(_verified_page(result))

    try:
        attempts = _await(store.record_failure(_pool(), token, captcha_image.new_captcha_code()))
    except Exception:
        return _respond(_unavailable())

    if attempts >= store.MAX_ATTEMPTS:
        try:
            _await(store.consume(_pool(), token))
            outcome = _await(service.fail(
                _discord_bot, guild_id, user_id,
                kick=bool(cfg.captcha_kick_on_fail),
                source=modes.LABELS[modes.WEB],
            ))
        except Exception:
            return _respond(_unavailable())
        return _respond(_failed_page(outcome))

    return _respond(verification_page.challenge_page(
        token=token,
        guild_name=_guild_name(guild_id),
        attempts_left=max(0, store.MAX_ATTEMPTS - attempts),
        attempt=attempts,
        error="That was not the code in the image.",
    ))


def _verified_page(result: dict) -> tuple[str, int]:
    """What a verified member sees, including the roles that were applied."""
    if result.get("problem") == "guild":
        return verification_page.notice_page(
            "Verified",
            "You are verified, but Niko is no longer in that server, so no roles could be added.",
            ad=False,
        )
    if result.get("problem") == "member":
        return verification_page.notice_page(
            "Verified",
            "You are verified, but Niko could not find you in that server. Rejoin and press Verify again.",
        )
    parts = ["You are verified — you can close this tab and return to Discord."]
    applied = result.get("applied") or []
    if applied:
        parts.append(f"Roles added: {', '.join(applied)}.")
    return verification_page.notice_page("You are verified", " ".join(parts))


def _failed_page(outcome: dict) -> tuple[str, int]:
    if outcome.get("kicked"):
        message = (
            "That was the last attempt, and this server removes members who fail verification. "
            "You can rejoin and try again."
        )
    else:
        message = (
            "That was the last attempt. Return to Discord and press <strong>Verify</strong> "
            "again for a new challenge."
        )
    return verification_page.notice_page("Verification failed", message, tone="expired", ad=False)
