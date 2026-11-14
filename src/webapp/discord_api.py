"""Discord REST access that egresses the way the bot itself does."""

import base64
import logging
import os
import requests as req
from . import config, runtime
from utils.proxies.cloudflare import interstitial_signature


logger = logging.getLogger("webapp")

#: Loopback route the dashboard child posts to when it has no bot of its own.
#: ``webapp/routes/internal_routes.py`` answers it in the bot child, which owns
#: the bot's Discord client, its proxy failover and its proxy-worker routing.
RELAY_PATH = "/api/internal/discord"
RELAY_TOKEN_ENV = "NIKO_RELAY_TOKEN"
RELAY_TOKEN_HEADER = "X-Internal-Token"

#: The request options the relay carries. Anything else stays local to the
#: caller, because the bot child only reconstructs the call it is asked to make.
RELAYED_KWARGS = ("headers", "params", "timeout", "data", "json", "allow_redirects")

#: Resolved once and cached: the bot child reports a new port when it restarts.
_relay_route = None

#: A process with no bot and no bot child keeps its old direct path; saying so
#: once is a diagnostic, saying it on every polled request is noise.
_relay_fallback_logged = False


def _relay_route_object():
    global _relay_route
    if _relay_route is None:
        from web_bridge import BotRoute

        _relay_route = BotRoute()
    return _relay_route


def _relay_target():
    """The bot child's loopback port and the token, or None without a child.

    Only supervised children get the per-run credential, so a single-process
    deployment (or a dashboard running without a bot child at all) keeps the
    direct path it has always had.
    """
    token = (os.environ.get(RELAY_TOKEN_ENV) or "").strip()
    if not token:
        return None
    try:
        port = _relay_route_object().port()
    except Exception:
        return None
    if not isinstance(port, int) or not 0 < port < 65536:
        return None
    return port, token


def _relay_unavailable_reason() -> str:
    """Why the relay was skipped, for the one diagnostic that reports it.

    "No bot child" covers two very different deployments — a single process,
    which is fine, and a dashboard child the supervisor forgot to hand the
    credential, which silently sends every Discord call out of a banned
    address — so the log line has to tell them apart.
    """
    if not (os.environ.get(RELAY_TOKEN_ENV) or "").strip():
        return f"this process has no {RELAY_TOKEN_ENV}"
    try:
        port = _relay_route_object().port()
    except Exception as exc:
        return f"the bot child port could not be resolved ({type(exc).__name__}: {exc})"
    return f"the supervisor reports no bot child API port (got {port!r})"


def _relay_discord_request(method: str, url: str, kwargs: dict):
    """Have the bot child make one Discord call over the bot's own egress.

    Returns None when there is no bot child to ask, so the caller can keep its
    previous behaviour; raises ``requests.ConnectionError`` when the child was
    asked and could not answer, which is the same failure a direct request to
    an unreachable Discord has.
    """
    target = _relay_target()
    if target is None:
        return None
    port, token = target
    try:
        inner_timeout = float(kwargs.get("timeout") or 10)
    except (TypeError, ValueError):
        inner_timeout = 10.0
    # The bot child may have to retry once over the Webshare egress after the
    # direct attempt is challenged, so it needs more room than one request.
    outer_timeout = (2.0, inner_timeout + 20.0)
    payload = {
        "method": method,
        "url": url,
        "kwargs": {key: kwargs[key] for key in RELAYED_KWARGS if key in kwargs},
    }
    try:
        answer = req.post(
            f"http://127.0.0.1:{port}{RELAY_PATH}",
            json=payload,
            headers={RELAY_TOKEN_HEADER: token},
            timeout=outer_timeout,
        )
    except req.RequestException as exc:
        # A replaced bot child has a new port: drop the cache so the next call
        # asks the supervisor instead of retrying a dead address.
        try:
            _relay_route_object().invalidate()
        except Exception:
            pass
        raise req.ConnectionError(
            f"The bot child could not relay this Discord call ({type(exc).__name__})."
        ) from exc
    except (TypeError, ValueError) as exc:
        # A body the relay cannot carry is a caller bug, but the route handling
        # it expects an unreachable Discord, not a serialization error.
        raise req.ConnectionError(
            f"This Discord call cannot be relayed ({type(exc).__name__})."
        ) from exc

    if answer.status_code != 200:
        detail = ""
        try:
            body = answer.json()
            if isinstance(body, dict):
                detail = str(body.get("error") or "")
        except ValueError:
            detail = (answer.text or "")[:200]
        raise req.ConnectionError(
            detail or f"The bot child answered HTTP {answer.status_code} for this Discord call."
        )
    try:
        data = answer.json()
        status = int(data.get("status") or 0)
        content = base64.b64decode(str(data.get("body") or ""))
    except (ValueError, TypeError, AttributeError) as exc:
        raise req.ConnectionError(
            "The bot child returned an unreadable answer for this Discord call."
        ) from exc

    response = req.Response()
    response.status_code = status
    response.reason = str(data.get("reason") or "")
    response.headers.update(
        {str(key): str(value) for key, value in (data.get("headers") or {}).items()}
    )
    response._content = content
    response.url = url
    response.encoding = req.utils.get_encoding_from_headers(response.headers)
    return response


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
    is another datacenter IP the same edge also refuses. A direct attempt that
    comes back as a Cloudflare interstitial is retried over the bot's active
    proxy. Every browser path that touches Discord goes through here, so login,
    the dashboard and the membership checks all share the bot's egress instead of
    sending a bare client from this host.

    A process that has no bot — the dashboard child of the supervisor split —
    has no Discord client to borrow either, so the call is handed to the bot
    child, which makes it with its own client. That relay is what keeps the
    dashboard usable on a host whose address Cloudflare has banned for the
    Discord API: the bot child is answering Discord at the same moment, over the
    egress its failover armed, and this process cannot reach Discord at all on
    its own.

    A blocked response without a configured proxy is returned untouched, so the
    caller keeps its own error handling instead of surfacing a routing
    misconfiguration as a server error.
    """
    if runtime._discord_bot is None:
        relayed = _relay_discord_request(method, url, kwargs)
        if relayed is not None:
            return relayed
        global _relay_fallback_logged
        if not _relay_fallback_logged:
            _relay_fallback_logged = True
            logger.warning(
                "Discord calls are not being relayed to the bot child (%s); "
                "this dashboard process asks Discord directly, which a banned "
                "host cannot do.",
                _relay_unavailable_reason(),
            )
    http = getattr(runtime._discord_bot, "http", None) if runtime._discord_bot is not None else None
    headers = dict(kwargs.get("headers") or {})
    user_agent = getattr(http, "user_agent", None)
    if isinstance(user_agent, str) and user_agent:
        headers.setdefault("User-Agent", user_agent)
    if headers:
        kwargs["headers"] = headers
    proxy_workers = getattr(runtime._discord_bot, "discord_proxy", None) if runtime._discord_bot is not None else None
    if proxy_workers is not None and proxy_workers.can_relay(url):
        try:
            proxied = proxy_workers.request_via_worker(method, url, kwargs)
        except Exception as exc:
            logger.warning("Discord proxy worker failed for %s %s: %s", method, url, exc)
        else:
            if interstitial_signature(proxied) is None:
                return proxied
            proxied.close()
    response = getattr(req, method.lower())(url, **kwargs)
    if interstitial_signature(response) is None:
        return response

    proxies = _discord_egress_proxies(http)
    logger.warning(
        "Discord %s %s answered HTTP %s with Cloudflare signatures (proxy=%s): %.200s",
        method, url, getattr(response, "status_code", 0),
        bool(proxies), getattr(response, "text", "") or "",
    )
    # Browser paths have no failover of their own, so fall back to the egress
    # discord.py itself already switched to before reporting the block.
    if proxies is not None and "proxies" not in kwargs:
        try:
            proxied = getattr(req, method.lower())(url, proxies=proxies, **kwargs)
        except req.RequestException as exc:
            logger.warning("Discord %s %s failed over the Webshare egress: %s", method, url, exc)
        else:
            if interstitial_signature(proxied) is None:
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
