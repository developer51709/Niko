"""Owner-controlled registration for non-gateway standby proxy instances."""
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

from utils.backup_proxy import backup_proxy_url, secret_key, verification_proof

from utils.backup_registry import add_backup, init_backup_registry, list_backups, remove_backup


def configure_backup_proxy():
    """Defer registry loading until the bot's shared database is initialized."""
    return None


def _sync_backup_proxy_manager(bot, rows):
    manager = getattr(bot, "proxy_manager", None)
    if manager is None:
        return
    key = _backup_key()
    manager.set_backup_proxies([backup_proxy_url(row["url"], key) for row in rows])
    manager.attach(bot)


async def initialize_backup_registry(bot):
    """Ensure the shared Mongo registry is ready and load standbys for failover."""
    try:
        rows = await init_backup_registry(bot)
        _sync_backup_proxy_manager(bot, rows)
    except Exception as exc:
        manager = getattr(bot, "proxy_manager", None)
        if manager is not None:
            manager.set_backup_proxies([])
        logging.warning("ProxyManager", f"Standby registry unavailable: {exc}")


def _refresh_backup_proxy_manager(rows):
    if _discord_bot is not None:
        _sync_backup_proxy_manager(_discord_bot, rows)


def _backup_key():
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
        raise ValueError("Enter a valid HTTPS backup origin.")
    parts = urlsplit(raw_url.strip().rstrip("/"))
    try:
        parsed_port = parts.port
    except ValueError as exc:
        raise ValueError("Backup URL has an invalid port.") from exc
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
        raise ValueError("Backup URL must be HTTPS and must not contain embedded credentials.")
    if parts.path or parts.query or parts.fragment:
        raise ValueError("Enter only the HTTPS origin, without a path or query string.")
    hostname = parts.hostname.rstrip(".").lower()
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith((".localhost", ".local", ".internal")):
        raise ValueError("Backup URL must use a public hostname.")
    try:
        addresses = [ipaddress.ip_address(hostname)]
    except ValueError:
        try:
            addresses = [ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(hostname, parsed_port or 443, type=socket.SOCK_STREAM)]
        except (OSError, ValueError) as exc:
            raise ValueError("Backup hostname could not be resolved.") from exc
    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("Backup URL must resolve only to public IP addresses.")
    if parsed_port is not None and not 1 <= parsed_port <= 65535:
        raise ValueError("Backup URL has an invalid port.")
    return f"https://{parts.netloc}"


def _owner_only():
    if _current_staff_role() != "owner":
        return jsonify({"error": "Backup instance management is restricted to the bot owner."}), 403
    return None


@app.route("/api/staff/backups", methods=["GET"])
@require_auth
def api_staff_backups():
    error = _owner_only()
    if error:
        return error
    try:
        rows = run_on_bot_loop(list_backups(_discord_bot))
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        return jsonify({"error": "Persistent backup registry is unavailable."}), 503
    return jsonify({"backups": rows})


@app.route("/api/staff/backups", methods=["POST"])
@require_auth
@require_csrf
def api_add_staff_backup():
    error = _owner_only()
    if error:
        return error
    body = request.get_json(silent=True) or {}
    name = str(body.get("name", "")).strip()
    if not name or len(name) > 60:
        return jsonify({"error": "Backup name must be between 1 and 60 characters."}), 400
    try:
        url = _validate_public_https_origin(body.get("url"))
        key = _backup_key()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503

    nonce = secrets.token_urlsafe(32)
    try:
        response = requests.post(
            f"{url}/internal/backup/verify",
            json={"nonce": nonce},
            timeout=8,
            allow_redirects=False,
            headers={"Content-Type": "application/json"},
        )
        if response.status_code != 200:
            return jsonify({"error": "The backup did not pass credential verification."}), 400
        proof = response.json().get("proof", "")
    except (requests.RequestException, ValueError, AttributeError):
        return jsonify({"error": "Could not verify the backup. Confirm it is running in BACKUP_MODE with matching production secrets."}), 400
    if not _verification_matches(key, nonce, proof):
        return jsonify({"error": "Bot token or session secret does not match production."}), 400

    item = {"id": secrets.token_urlsafe(12), "name": name, "url": url, "created_at": int(time.time())}
    try:
        rows = run_on_bot_loop(add_backup(_discord_bot, item))
    except ValueError as exc:
        if str(exc) == "This backup URL is already registered.":
            return jsonify({"error": str(exc)}), 409
        return jsonify({"error": "The verified backup could not be persisted."}), 503
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        return jsonify({"error": "Persistent backup registry is unavailable."}), 503
    _refresh_backup_proxy_manager(rows)
    return jsonify({"ok": True, "backup": item}), 201


@app.route("/api/staff/backups/<backup_id>", methods=["DELETE"])
@require_auth
@require_csrf
def api_remove_staff_backup(backup_id):
    error = _owner_only()
    if error:
        return error
    try:
        rows = run_on_bot_loop(remove_backup(_discord_bot, backup_id))
    except KeyError:
        return jsonify({"error": "Backup instance not found."}), 404
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        return jsonify({"error": "Persistent backup registry is unavailable."}), 503
    _refresh_backup_proxy_manager(rows)
    return jsonify({"ok": True})
