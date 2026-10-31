"""Session and OAuth guards, plus the signed-in member's guild list (kept here
rather than in ``discord_api`` because it needs the token refresh below)."""

import asyncio
import json
import time
from functools import wraps

from flask import jsonify, request, session

from . import config, discord_api, leaderboard_cache, runtime


def _load_blacklist_manager():
    """Load the shared blacklist cache on the bot loop when needed."""
    from utils.blacklist_manager import BlacklistManager

    manager = BlacklistManager()
    if not manager._loaded and runtime._discord_bot is not None:
        runtime.run_on_bot_loop(manager._ensure_loaded())
    return manager


def _current_user_blacklist_entry():
    user_id = session.get("user", {}).get("id")
    if not user_id:
        return None
    return _load_blacklist_manager().get_user_entry(int(user_id))


def require_auth(f):
    """Require a signed-in, non-blacklisted user for dashboard API access."""
    @wraps(f)
    def _inner(*args, **kwargs):
        if not ensure_access_token():
            return jsonify({
                "error": "Not authenticated",
                "login_url": "/auth/login",
            }), 401
        try:
            entry = _current_user_blacklist_entry()
        except Exception:
            return jsonify({"error": "Account access could not be verified."}), 503
        if entry:
            return jsonify({
                "error": "This Discord account is blacklisted from the dashboard.",
                "blacklisted": True,
                "scope": "user",
                "reason": entry.get("reason") or "No reason provided.",
            }), 403
        return f(*args, **kwargs)
    return _inner


def require_dashboard_auth(f):
    """Authenticate a dashboard status check while allowing it to report a ban."""
    @wraps(f)
    def _inner(*args, **kwargs):
        if not ensure_access_token():
            return jsonify({"error": "Not authenticated", "login_url": "/auth/login"}), 401
        try:
            entry = _current_user_blacklist_entry()
        except Exception:
            return jsonify({"error": "Account access could not be verified."}), 503
        return jsonify({
            "blacklisted": bool(entry),
            "reason": (entry.get("reason") or "No reason provided.") if entry else None,
        })
    return _inner


def ensure_access_token(force: bool = False) -> bool:
    """Keep the OAuth session usable across Discord's short-lived access token.

    ``force`` skips the still-fresh shortcut: a 401 from Discord is the only
    reliable signal that the token was revoked, because the stored expiry can
    still be hours away when another session refreshed it first.
    """
    if "user" not in session:
        return False
    expires_at = float(session.get("token_exp", 0))
    if not force and session.get("access_token") and time.time() < expires_at - 30:
        return True

    refresh_token = session.get("refresh_token")
    if not refresh_token or not runtime.oauth_enabled():
        session.clear()
        return False
    try:
        response = discord_api.discord_request(
            "POST",
            f"{config.DISCORD_API}/oauth2/token",
            data={
                "client_id": config.DISCORD_CLIENT_ID,
                "client_secret": config.DISCORD_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        response.raise_for_status()
        token_data = response.json()
        session["access_token"] = token_data["access_token"]
        session["refresh_token"] = token_data.get("refresh_token", refresh_token)
        session["token_exp"] = time.time() + token_data.get("expires_in", 604800)
        # A refresh can add a scope that was granted since (``guilds.join`` for
        # referral links), so the stored list follows the token.
        if token_data.get("scope"):
            session["oauth_scopes"] = str(token_data["scope"]).split()
        return True
    except Exception:
        session.clear()
        return False


def require_csrf(f):
    """Require the token issued with auth status for browser mutations."""
    @wraps(f)
    def _inner(*args, **kwargs):
        if not session.get("csrf_token") or request.headers.get("X-CSRF-Token") != session["csrf_token"]:
            return jsonify({"error": "Invalid request token. Refresh the dashboard and try again."}), 403
        return f(*args, **kwargs)
    return _inner


def managed_guild_ids() -> set[str]:
    """Return manageable mutual guilds, cached briefly in the signed session."""
    cached_at = session.get("managed_guilds_at", 0)
    cached_ids = session.get("managed_guild_ids")
    if cached_ids is not None and time.time() - cached_at < 300:
        # This cache is populated from OAuth-manageable guilds that were
        # confirmed mutual when /api/guilds ran. Do not intersect it with the
        # gateway cache again here: guilds can populate asynchronously and
        # temporarily disappear from that cache while the owner switches tabs.
        return {str(guild_id) for guild_id in cached_ids}

    if not ensure_access_token():
        return set()
    token = session.get("access_token", "")
    if not token:
        return set()
    try:
        # Same egress as /api/guilds, so a guild page stays reachable while the
        # bot is egressing over its proxy and this host's own IP is blocked.
        all_guilds = member_guilds(token)
    except Exception:
        # Keep a recently OAuth-verified authorization decision through a
        # transient Discord API failure instead of turning it into a false 403.
        cached_ids = session.get("managed_guild_ids")
        if cached_ids is not None and time.time() - session.get("managed_guilds_at", 0) < 300:
            return {str(guild_id) for guild_id in cached_ids}
        return set()

    present = runtime.bot_guild_ids()
    manageable = []
    for guild in all_guilds:
        try:
            permissions = int(guild.get("permissions", 0))
        except (TypeError, ValueError):
            permissions = 0
        if (
            bool(permissions & (config.MANAGE_GUILD_PERM | config.ADMINISTRATOR_PERM))
            or bool(guild.get("owner"))
        ) and str(guild["id"]) in present:
            manageable.append(str(guild["id"]))
    session["managed_guild_ids"] = manageable
    session["managed_guilds_at"] = time.time()
    return set(manageable)


def require_guild_access(f):
    """Protect a guild route from cross-server reads and writes."""
    @wraps(f)
    def _inner(guild_id, *args, **kwargs):
        if str(guild_id) not in managed_guild_ids():
            return jsonify({"error": "You do not have Manage Server access to this guild."}), 403
        try:
            guild_entry = _load_blacklist_manager().get_guild_entry(int(guild_id))
        except Exception:
            return jsonify({"error": "Guild access could not be verified."}), 503
        if guild_entry:
            return jsonify({
                "error": "This server is blacklisted from using the dashboard.",
                "blacklisted": True,
                "scope": "guild",
                "guild_id": str(guild_id),
                "reason": guild_entry.get("reason") or "No reason provided.",
            }), 403
        return f(guild_id, *args, **kwargs)
    return _inner


def _force_token_refresh() -> bool:
    """Refresh the session's OAuth token even though its clock says it is fresh."""
    try:
        return ensure_access_token(force=True)
    except Exception:
        return False


def get_mutual_leaderboard_identity_ids(target_user_ids: set[str]) -> set[str] | None:
    """Resolve target identities visible to the signed-in viewer via mutual guilds.

    Fail closed on membership uncertainty: unavailable Discord auth or guild
    data never makes private profiles visible to a broader audience.
    """
    viewer = session.get("user") or {}
    if not viewer.get("id") or not target_user_ids:
        return set()
    if not ensure_access_token():
        return set()
    # The leaderboard polls, so the viewer's guild list is reused for a few
    # seconds instead of spending a Discord OAuth call on every refresh.
    viewer_guild_ids = leaderboard_cache.cached_viewer_guilds(str(viewer["id"]))
    if viewer_guild_ids is None:
        try:
            viewer_guild_ids = {
                str(guild["id"])
                for guild in discord_api.discord_get("/users/@me/guilds", session.get("access_token", ""))
                if guild.get("id")
            }
        except Exception:
            return None
        leaderboard_cache.store_viewer_guilds(str(viewer["id"]), viewer_guild_ids)
    if not viewer_guild_ids or runtime._discord_bot is None:
        return set()

    async def find_mutual_members():
        visible = set()
        for guild in runtime._discord_bot.guilds:
            if str(guild.id) not in viewer_guild_ids:
                continue
            for user_id in target_user_ids - visible:
                try:
                    if guild.get_member(int(user_id)) is not None:
                        visible.add(user_id)
                except (TypeError, ValueError):
                    continue
        return visible

    try:
        return runtime.run_on_bot_loop(find_mutual_members())
    except Exception:
        return None


class DiscordEgressError(RuntimeError):
    """Discord could not be reached over the bot's own REST egress.

    ``status`` carries Discord's HTTP answer when there was one, so a caller can
    tell a rejected token (401) apart from an egress that could not connect.
    """

    def __init__(self, message: str, status: int = 0) -> None:
        super().__init__(message)
        self.status = status

# One guild-list fetch has to fit inside a dashboard request, so the retry only
# exists to pick up the proxy the rate-limit hook has just armed.
_MEMBER_GUILDS_REQUEST_TIMEOUT = 6

_MEMBER_GUILDS_ATTEMPTS = 2

_MEMBER_GUILDS_RETRY_CAP = 3.0


def _member_guilds_retry_delay(body: str) -> float:
    """How long a limited guild-list request should wait before retrying."""
    try:
        payload = json.loads(body)
    except (TypeError, ValueError):
        return 1.0
    retry_after = payload.get("retry_after") if isinstance(payload, dict) else None
    try:
        delay = float(retry_after)
    except (TypeError, ValueError):
        return 1.0
    return min(max(delay, 0.5), _MEMBER_GUILDS_RETRY_CAP)


async def _member_guilds_via_bot(token: str) -> list:
    """Ask Discord for the member's guilds over the bot's own REST session.

    The session is the one discord.py uses for the bot's own calls, so the
    request inherits its egress: the active Webshare proxy after a global limit,
    the proxy-worker hook installed on the session, and the rate-limit monitor
    that arms that proxy. The member's OAuth token travels as the bearer instead
    of the bot token, because this lists the servers *they* can manage.
    """
    http = getattr(runtime._discord_bot, "http", None) if runtime._discord_bot is not None else None
    session = getattr(http, "_HTTPClient__session", None) if http is not None else None
    if session is None:
        raise DiscordEgressError("The bot's Discord connection is not ready yet.")

    url = f"{config.DISCORD_API}/users/@me/guilds"
    user_agent = getattr(http, "user_agent", None)
    last_status = 0

    for attempt in range(_MEMBER_GUILDS_ATTEMPTS):
        headers = {"Authorization": f"Bearer {token}"}
        if isinstance(user_agent, str) and user_agent:
            headers["User-Agent"] = user_agent
        kwargs = {"headers": headers, "timeout": _MEMBER_GUILDS_REQUEST_TIMEOUT}

        # Read the proxy on every attempt: the rate-limit hook arms Webshare
        # while a blocked response is being handled, so the retry leaves over
        # the new egress instead of the IP Discord just refused.
        proxy = getattr(http, "proxy", None)
        if isinstance(proxy, str) and proxy:
            kwargs["proxy"] = proxy
        proxy_auth = getattr(http, "proxy_auth", None)
        if proxy_auth is not None:
            kwargs["proxy_auth"] = proxy_auth

        try:
            async with session.get(url, **kwargs) as response:
                status = int(getattr(response, "status", 0) or 0)
                body = await response.text()
        except OSError as exc:
            # A proxy that refuses the connection is rotated by the request
            # hook, so one retry leaves over the replacement egress.
            if attempt + 1 >= _MEMBER_GUILDS_ATTEMPTS:
                raise DiscordEgressError(
                    f"The server list request failed ({type(exc).__name__})."
                ) from exc
            await asyncio.sleep(1.0)
            continue

        if 300 > status >= 200:
            try:
                guilds = json.loads(body)
            except ValueError as exc:
                raise DiscordEgressError("Discord returned an unreadable server list.") from exc
            if not isinstance(guilds, list):
                raise DiscordEgressError("Discord returned an unexpected server list.")
            return guilds

        last_status = status
        # A refused or limited response is what the failover is for; anything
        # else (an expired token, a 500) will not improve on a retry.
        if status not in {403, 429} or attempt + 1 >= _MEMBER_GUILDS_ATTEMPTS:
            break
        await asyncio.sleep(_member_guilds_retry_delay(body))

    raise DiscordEgressError(
        f"Discord answered HTTP {last_status or 'no status'} for the server list.",
        status=last_status,
    )


def _member_guilds_once(token: str) -> list:
    bot = runtime._discord_bot
    loop = getattr(bot, "loop", None) if bot is not None else None
    if bot is None or loop is None or not loop.is_running():
        # A web-only process has no bot loop or session to borrow. Report the
        # HTTP answer the same way the proxied path does, so a rejected token
        # is refreshed here too instead of shown as a Discord outage.
        try:
            return discord_api.discord_get("/users/@me/guilds", token)
        except Exception as exc:
            status = getattr(getattr(exc, "response", None), "status_code", 0) or 0
            raise DiscordEgressError(
                f"Discord answered HTTP {status or 'no status'} for the server list.",
                status=status,
            ) from exc
    return runtime.run_on_bot_loop(_member_guilds_via_bot(token), timeout=18)


def member_guilds(token: str) -> list:
    """The guilds the signed-in member can manage, read the way the bot reads.

    ``/dashboard/servers`` used to ask Discord from this Flask thread with a bare
    ``requests`` client, so the call left over the deployment's own IP - the very
    address that was limited or Cloudflare-challenged when Webshare failover
    armed. The list came back empty and the page listed no servers at all while
    the bot itself was healthy.

    Fetching on the bot's event loop over its REST session puts the call on the
    bot's egress instead of a separate one, which is what "proxied with the bot"
    means: whichever route the bot's own REST calls take, this list takes too.
    """
    try:
        return _member_guilds_once(token)
    except DiscordEgressError as exc:
        # A 401 while the session clock still says the token is valid means
        # Discord no longer accepts it - another tab, another worker, or a
        # rotation refreshed the session and revoked this value. Refresh once
        # and retry over the new token instead of reporting the dashboard broken.
        if getattr(exc, "status", 0) != 401 or not _force_token_refresh():
            raise
    return _member_guilds_once(session.get("access_token", ""))
