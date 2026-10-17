"""Owner-controlled registration and failover controls for standby instances."""
from . import server as _server

globals().update({name: value for name, value in vars(_server).items() if not name.startswith("__")})

import ipaddress
import os
import secrets
import socket
import time
from urllib.parse import urlsplit

import requests
from utils import logging

from utils.standby_failover import configured_public_origin, standby_mode, standby_origin, secret_key, verification_proof
from utils.standby_manager import StandbyFailoverManager

from utils.standby_registry import (
    add_standby,
    announced_primary_origin,
    init_standby_registry,
    list_standbys,
    record_primary_origin,
    remove_standby,
)

# A forwarded management request carries this marker so a misconfigured standby
# cannot bounce it to another standby in a loop. The marker also names the
# header set aside from the request when it is relayed to the main instance.
_STANDBY_FORWARD_HEADER = "X-Niko-Standby-Control"
_STANDBY_FORWARD_REQUEST_HEADERS = {
    "connection", "content-length", "transfer-encoding", "proxy-authorization", "proxy-connection", "host",
}
_STANDBY_FORWARD_RESPONSE_HEADERS = {
    "connection", "content-encoding", "content-length", "keep-alive", "proxy-authenticate",
    "proxy-authorization", "te", "trailer", "transfer-encoding", "upgrade", "set-cookie",
}


def _sync_standby_manager(bot, rows):
    manager = getattr(bot, "standby_failover", None)
    if manager is None:
        manager = StandbyFailoverManager()
        bot.standby_failover = manager
    if _standby_mode():
        # Only the main instance owns failover routing. A standby that installed
        # these targets could relay Discord REST traffic to itself or to another
        # standby, so its own manager stays empty.
        manager.set_standbys([], [])
        return
    origins, ids = [], []
    for row in rows:
        try:
            standby_id, origin = str(row["id"]), standby_origin(row["url"])
        except (KeyError, TypeError, ValueError):
            # One unreadable row in the shared registry must not disable every
            # remaining instance or fail the request that triggered the sync.
            logging.warning("StandbyFailover", "Ignoring an unreadable standby registry entry.")
            continue
        ids.append(standby_id)
        origins.append(origin)
    manager.set_standbys(origins, ids)
    manager.attach(bot)


def _origin_key(value):
    """Normalize a host or origin to ``host:port`` so defaults cannot differ."""
    parts = urlsplit(value)
    if not parts.hostname:
        parts = urlsplit(f"https://{value}")
    try:
        port = parts.port
    except ValueError:
        port = None
    return f"{(parts.hostname or '').lower()}:{port or (443 if parts.scheme != 'http' else 80)}"


def _is_own_origin(url):
    """Reject registering this server's own origin, which would proxy to itself."""
    try:
        own_origins = {_origin_key(public_base_url())}
    except (TypeError, ValueError):
        own_origins = set()
    own_origins.add(_origin_key(request.host))
    return _origin_key(url) in own_origins


async def initialize_standby_registry(bot):
    """Ensure registry ready and load public standby origins."""
    try:
        rows = await init_standby_registry(bot)
        _sync_standby_manager(bot, rows)
        origin = configured_public_origin()
        if origin:
            await record_primary_origin(bot, origin)
        else:
            logging.warning(
                "StandbyFailover",
                "No public origin is configured; registered standbys must set STANDBY_PRIMARY_URL.",
            )
    except Exception as exc:
        logging.warning("StandbyFailover", f"Standby registry unavailable: {exc}")


def _refresh_standby_manager(rows):
    if _discord_bot is not None:
        _sync_standby_manager(_discord_bot, rows)


def _standby_key():
    token = os.environ.get("DISCORD_BOT_TOKEN", "")
    session_secret = os.environ.get("SESSION_SECRET", "")
    if not token or not session_secret:
        raise RuntimeError("Production DISCORD_BOT_TOKEN and SESSION_SECRET must both be configured.")
    return secret_key(token, session_secret)


def _verification_matches(key, nonce, proof):
    expected = verification_proof(key, nonce)
    return isinstance(proof, str) and secrets.compare_digest(proof, expected)


def _validate_public_https_origin(raw_url):
    if not isinstance(raw_url, str) or len(raw_url) > 300:
        raise ValueError("Enter a valid HTTPS standby origin.")
    parts = urlsplit(raw_url.strip().rstrip("/"))
    try:
        parsed_port = parts.port
    except ValueError as exc:
        raise ValueError("Standby URL has an invalid port.") from exc
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
        raise ValueError("Standby URL must be HTTPS and must not contain embedded credentials.")
    if parts.path or parts.query or parts.fragment:
        raise ValueError("Enter only the HTTPS origin, without a path or query string.")
    hostname = parts.hostname.rstrip(".").lower()
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith((".localhost", ".local", ".internal")):
        raise ValueError("Standby URL must use a public hostname.")
    try:
        addresses = [ipaddress.ip_address(hostname)]
    except ValueError:
        try:
            addresses = [ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(hostname, parsed_port or 443, type=socket.SOCK_STREAM)]
        except (OSError, ValueError) as exc:
            raise ValueError("Standby hostname could not be resolved.") from exc
    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("Standby URL must resolve only to public IP addresses.")
    if parsed_port is not None and not 1 <= parsed_port <= 65535:
        raise ValueError("Standby URL has an invalid port.")
    return f"https://{parts.netloc}"


def _owner_only():
    if _current_staff_role() != "owner":
        return jsonify({"error": "Standby instance management is restricted to the bot owner."}), 403
    return None


def _standby_mode():
    """Report whether this process runs as a standby backend."""
    return standby_mode()


def _primary_origin():
    """Return the main instance's public origin, or None when it is unknown.

    Only the main instance owns the standby registry and the failover control
    plane, so a standby that is asked to change either has to send the request
    on. The origin comes from ``STANDBY_PRIMARY_URL``/``PUBLIC_URL`` or from the
    announcement the main instance writes into the shared registry.

    It is never taken from request headers: a request that arrived through the
    main instance is still addressed by its registered origin, and trusting a
    forwarded host here would let a crafted header make this standby ship its
    session to an attacker-chosen origin.
    """
    confirmed = [_usable_origin(os.environ.get("STANDBY_PRIMARY_URL", "")),
                 _usable_origin(os.environ.get("PUBLIC_URL", ""))]
    for origin in confirmed:
        if origin:
            return origin

    # The registry announcement is the only self-configuring source, so it is
    # read after the cheap local ones and never when they already answered.
    if _discord_bot is not None:
        try:
            return _usable_origin(run_on_bot_loop(announced_primary_origin(_discord_bot)))
        except Exception:
            return None
    return None


def _usable_origin(candidate):
    """Normalize a configured or announced origin, or None when it is unusable."""
    if not isinstance(candidate, str) or not candidate.strip():
        return None
    try:
        origin = standby_origin(candidate.strip())
    except (TypeError, ValueError):
        return None
    # This instance is never its own upstream.
    return None if _is_own_origin(origin) else origin


def _forward_control_to_primary():
    """Send a standby management request to the main instance that owns it.

    Returns the forwarded response, or a JSON error when the main instance
    cannot be reached. Standby management never runs on a standby: applying it
    there would install this instance (or another standby) as a routing target
    and would leave the main instance's failover state stale.
    """
    if not _standby_mode():
        return None
    if request.headers.get(_STANDBY_FORWARD_HEADER):
        return jsonify({"error": "Standby management is already being forwarded; a standby never handles it."}), 503
    origin = _primary_origin()
    if origin is None:
        return jsonify({
            "error": "This standby does not know the main instance. Set STANDBY_PRIMARY_URL to the production origin.",
        }), 503

    target = f"{origin}{request.path}"
    if request.query_string:
        target += f"?{request.query_string.decode('latin-1')}"
    headers = {
        name: value
        for name, value in request.headers.items()
        if name.lower() not in _STANDBY_FORWARD_REQUEST_HEADERS
    }
    headers[_STANDBY_FORWARD_HEADER] = "1"
    # The browser's host names this standby, and the main instance has to see its
    # own so registry checks resolve against the production origin.
    headers["X-Forwarded-Host"] = urlsplit(origin).netloc
    headers["X-Forwarded-Proto"] = "https"
    try:
        upstream = requests.request(
            request.method,
            target,
            headers=headers,
            data=request.get_data(cache=True),
            timeout=(3, 20),
            allow_redirects=False,
        )
    except requests.RequestException:
        return jsonify({"error": "The main instance is unavailable; the change was not applied."}), 503

    response = Response(upstream.content, status=upstream.status_code)
    raw_headers = getattr(getattr(upstream, "raw", None), "headers", None)
    set_cookies = raw_headers.getlist("Set-Cookie") if raw_headers is not None else []
    for name, value in upstream.headers.items():
        if name.lower() not in _STANDBY_FORWARD_RESPONSE_HEADERS:
            response.headers[name] = value
    for cookie in set_cookies:
        response.headers.add("Set-Cookie", cookie)
    close_upstream = getattr(upstream, "close", None)
    if close_upstream is not None:
        close_upstream()
    return response


def _announce_primary_origin():
    """Keep the announced main-instance origin current for standby instances."""
    if _standby_mode() or _discord_bot is None:
        return
    try:
        origin = standby_origin(public_base_url())
    except (RuntimeError, ValueError):
        return
    try:
        run_on_bot_loop(record_primary_origin(_discord_bot, origin))
    except Exception:
        pass


@app.route("/api/staff/standbys", methods=["GET"])
@require_auth
def api_staff_standbys():
    forwarded = _forward_control_to_primary()
    if forwarded is not None:
        return forwarded
    error = _owner_only()
    if error:
        return error
    try:
        rows = run_on_bot_loop(list_standbys(_discord_bot))
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        return jsonify({"error": "Persistent standby registry is unavailable."}), 503
    manager = getattr(_discord_bot, "standby_failover", None)
    state = manager.status() if manager is not None else {}
    health = run_on_bot_loop(manager.probe_all()) if manager is not None else {}
    for row in rows:
        stats = health.get(row["id"])
        row["health"] = "online" if stats else "offline"
        row["stats"] = stats
        row["active"] = state.get("active_standby_id") == row["id"]
    return jsonify({"standbys": rows, "failover": state})


@app.route("/api/staff/standbys/failover", methods=["POST"])
@require_auth
@require_csrf
def api_control_staff_standby_failover():
    forwarded = _forward_control_to_primary()
    if forwarded is not None:
        return forwarded
    error = _owner_only()
    if error:
        return error
    manager = getattr(_discord_bot, "standby_failover", None)
    if manager is None:
        return jsonify({"error": "Standby failover manager is unavailable."}), 503
    body = request.get_json(silent=True) or {}
    action = body.get("action")
    try:
        if action == "mode":
            mode = body.get("mode")
            if mode not in {"auto", "off"}:
                return jsonify({"error": "Choose auto or off mode."}), 400
            # Mode selection only flips flags on the manager, so it runs on the
            # request thread; dispatching a bool to the bot-loop coroutine
            # runner would fail every mode change. A standby never reaches this
            # branch: it forwards failover control to the main instance instead
            # of letting a blocked request promote itself.
            changed = manager.select_failover(mode)
        elif action == "activate":
            standby_id = str(body.get("standby_id", ""))
            changed = run_on_bot_loop(manager.activate_standby(standby_id))
        elif action == "rotate":
            changed = run_on_bot_loop(manager.rotate_standby())
        else:
            return jsonify({"error": "Unknown failover action."}), 400
    except Exception:
        return jsonify({"error": "Failover control could not be completed."}), 503
    if not changed:
        return jsonify({"error": manager.status().get("last_error") or "The selected route is unavailable."}), 503
    return jsonify({"ok": True, "failover": manager.status()})


@app.route("/api/staff/standbys", methods=["POST"])
@require_auth
@require_csrf
def api_add_staff_standby():
    forwarded = _forward_control_to_primary()
    if forwarded is not None:
        return forwarded
    error = _owner_only()
    if error:
        return error
    body = request.get_json(silent=True) or {}
    name = str(body.get("name", "")).strip()
    if not name or len(name) > 60:
        return jsonify({"error": "Standby name must be between 1 and 60 characters."}), 400
    try:
        url = standby_origin(_validate_public_https_origin(body.get("url")))
        key = _standby_key()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    if _is_own_origin(url):
        return jsonify({"error": "A standby cannot use this server's own origin."}), 400

    nonce = secrets.token_urlsafe(32)
    try:
        response = requests.post(
            f"{url}/internal/standby/verify",
            json={"nonce": nonce},
            timeout=8,
            allow_redirects=False,
            headers={"Content-Type": "application/json"},
        )
        if response.status_code != 200:
            return jsonify({"error": "The standby did not pass credential verification."}), 400
        proof = response.json().get("proof", "")
    except (requests.RequestException, ValueError, AttributeError):
        return jsonify({"error": "Could not verify the standby. Confirm it is running in STANDBY_MODE with matching production secrets."}), 400
    if not _verification_matches(key, nonce, proof):
        return jsonify({"error": "Bot token or session secret does not match production."}), 400

    item = {"id": secrets.token_urlsafe(12), "name": name, "url": url, "created_at": int(time.time())}
    try:
        rows = run_on_bot_loop(add_standby(_discord_bot, item))
    except ValueError as exc:
        if str(exc) == "This standby URL is already registered.":
            return jsonify({"error": str(exc)}), 409
        return jsonify({"error": "The verified standby could not be persisted."}), 503
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        return jsonify({"error": "Persistent standby registry is unavailable."}), 503
    _refresh_standby_manager(rows)
    _announce_primary_origin()
    return jsonify({"ok": True, "standby": item}), 201


@app.route("/api/staff/standbys/<standby_id>", methods=["DELETE"])
@require_auth
@require_csrf
def api_remove_staff_standby(standby_id):
    forwarded = _forward_control_to_primary()
    if forwarded is not None:
        return forwarded
    error = _owner_only()
    if error:
        return error
    try:
        rows = run_on_bot_loop(remove_standby(_discord_bot, standby_id))
    except KeyError:
        return jsonify({"error": "Standby instance not found."}), 404
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        return jsonify({"error": "Persistent standby registry is unavailable."}), 503
    _refresh_standby_manager(rows)
    return jsonify({"ok": True})
