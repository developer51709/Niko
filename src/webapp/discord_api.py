"""Discord REST access that egresses the way the bot itself does."""

import logging
import requests as req
from . import config, runtime


logger = logging.getLogger("webapp")


def _discord_egress_proxies(http) -> dict | None:
    """The proxy the bot's HTTP client egresses through, mapped for ``requests``.

    discord.py applies ``HTTPClient.proxy`` to every REST call (Webshare proxy
    failover sets it), so a request made from the web process has to use the
    same route or it can be blocked while the bot itself stays responsive.
    """
    proxy = getattr(http, "proxy", None)
    if not isinstance(proxy, str) or not proxy:
        return None
    return {"http": proxy, "https": proxy}


def discord_request(method: str, url: str, **kwargs):
    """Make Discord REST calls the way the bot itself does.

    Discord answers every request through Cloudflare, and that edge challenges
    plain ``python-requests`` traffic from a datacenter IP — the OAuth token
    exchange is a POST, so it is challenged before any dashboard call. The bot's
    own ``User-Agent`` therefore travels with every call. When proxy workers are
    enabled they are the first attempt, followed by the deployment's own egress;
    that is the identity Discord answers for this bot, while the Webshare proxy
    is another datacenter IP the same edge also refuses. When a direct attempt
    comes back as a Cloudflare interstitial the call is relayed to a standby
    when one is configured, then retried over the bot's active proxy. Every
    browser path that touches Discord goes through here, so login, the dashboard
    and the membership checks all share the bot's egress instead of sending a
    bare client from this host.

    A blocked response is only relayed when a signed relay can actually be sent.
    Without an active standby origin and the relay secrets, the Discord response is
    returned untouched so the caller keeps its own error handling instead of
    surfacing a relay misconfiguration as a server error.
    """
    http = getattr(runtime._discord_bot, "http", None) if runtime._discord_bot is not None else None
    headers = dict(kwargs.get("headers") or {})
    user_agent = getattr(http, "user_agent", None)
    if isinstance(user_agent, str) and user_agent:
        headers.setdefault("User-Agent", user_agent)
    if headers:
        kwargs["headers"] = headers
    manager = getattr(runtime._discord_bot, "standby_failover", None) if runtime._discord_bot is not None else None
    proxy_workers = getattr(runtime._discord_bot, "discord_proxy", None) if runtime._discord_bot is not None else None
    if proxy_workers is not None and proxy_workers.can_relay(url):
        try:
            proxied = proxy_workers.request_via_worker(method, url, kwargs)
        except Exception as exc:
            logger.warning("Discord proxy worker failed for %s %s: %s", method, url, exc)
        else:
            if manager is None or manager.cloudflare_interstitial(proxied) is None:
                return proxied
            proxied.close()
    response = getattr(req, method.lower())(url, **kwargs)
    if manager is None or manager.cloudflare_interstitial(response) is None:
        return response

    proxies = _discord_egress_proxies(http)
    logger.warning(
        "Discord %s %s answered HTTP %s with Cloudflare signatures (relay_configured=%s proxy=%s): %.200s",
        method, url, getattr(response, "status_code", 0), manager.relay_configured(),
        bool(proxies), getattr(response, "text", "") or "",
    )
    # A standby owns this instance's egress while it holds the gateway, so the
    # signed relay keeps its precedence.
    if manager.relay_configured():
        try:
            relayed = manager.request_via_standby(method, url, kwargs)
        except Exception as exc:
            manager.last_error = f"Standby API relay failed ({type(exc).__name__})."
            logger.warning("Standby relay failed for %s %s: %s", method, url, exc)
        else:
            response.close()
            return relayed
    # Browser paths have no failover of their own, so fall back to the egress
    # discord.py itself already switched to before reporting the block.
    if proxies is not None and "proxies" not in kwargs:
        try:
            proxied = getattr(req, method.lower())(url, proxies=proxies, **kwargs)
        except req.RequestException as exc:
            logger.warning("Discord %s %s failed over the Webshare egress: %s", method, url, exc)
        else:
            if manager.cloudflare_interstitial(proxied) is None:
                response.close()
                return proxied
            proxied.close()
    return response


def discord_get(endpoint: str, token: str):
    """GET a Discord API endpoint using a Bearer token."""
    r = discord_request(
        "GET",
        f"{config.DISCORD_API}{endpoint}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=8,
    )
    r.raise_for_status()
    return r.json()
