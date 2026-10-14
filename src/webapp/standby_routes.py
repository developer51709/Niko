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

from utils.standby_failover import standby_origin, secret_key, verification_proof
from utils.standby_manager import StandbyFailoverManager

from utils.standby_registry import add_standby, init_standby_registry, list_standbys, remove_standby


def _sync_standby_manager(bot, rows):
    manager = getattr(bot, "standby_failover", None)
    if manager is None:
        manager = StandbyFailoverManager()
        bot.standby_failover = manager
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
    return os.environ.get("STANDBY_MODE", "").strip().lower() in {"1", "true", "yes"}


@app.route("/api/staff/standbys", methods=["GET"])
@require_auth
def api_staff_standbys():
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
            # A standby only accepts signed handoff commands, so re-arming
            # automatic failover on it would let a blocked request promote it.
            if mode == "auto" and _standby_mode():
                return jsonify({"error": "A standby instance never initiates failover; manage routing from the primary."}), 403
            # Mode selection only flips flags on the manager, so it runs on the
            # request thread; dispatching a bool to the bot-loop coroutine
            # runner would fail every mode change.
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
    return jsonify({"ok": True, "standby": item}), 201


@app.route("/api/staff/standbys/<standby_id>", methods=["DELETE"])
@require_auth
@require_csrf
def api_remove_staff_standby(standby_id):
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
