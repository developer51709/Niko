"""Owner-controlled registration and telemetry for optional Discord proxy workers."""
from .. import server as _server

globals().update({name: value for name, value in vars(_server).items() if not name.startswith("__")})

import secrets
import time

import requests

from utils.discord_proxy import DiscordProxyManager, SERVICE, proxy_worker_token, verification_proof
from utils.proxy_worker_registry import (
    add_proxy_worker,
    init_proxy_worker_registry,
    list_proxy_workers,
    proxy_routing_enabled,
    remove_proxy_worker,
    set_proxy_routing_enabled,
)
from utils.standby_failover import standby_origin

# Management belongs to the primary exactly like standby management. A standby
# forwards these requests instead of storing a registry it cannot control.
from .standby_routes import (
    _forward_control_to_primary,
    _is_own_origin,
    _validate_public_https_origin,
)


def _owner_only():
    """Proxy-worker controls are owner-only, like standby controls."""
    if _current_staff_role() != "owner":
        return jsonify({"error": "Proxy worker management is restricted to the bot owner."}), 403
    return None


def _origin_error(error):
    """The standby validator owns URL safety; label its message for this page."""
    message = str(error)
    return message.replace("Standby", "Proxy worker").replace("standby", "proxy worker")


def _manager(bot, rows=None, enabled=None):
    manager = getattr(bot, "discord_proxy", None)
    if manager is None:
        manager = DiscordProxyManager()
        bot.discord_proxy = manager
    if rows is not None:
        manager.set_workers(rows, bool(enabled))
        manager.attach(bot)
    return manager


async def initialize_proxy_worker_registry(bot):
    """Load persisted workers and the routing switch before Discord login."""
    rows = await init_proxy_worker_registry(bot)
    enabled = await proxy_routing_enabled(bot)
    _manager(bot, rows, enabled)


def _merge_telemetry(rows, probes):
    latency_buckets = {}
    feed = []
    errors = []
    usage = {
        "requests": 0,
        "success": 0,
        "errors": 0,
        "bytes_in": 0,
        "bytes_out": 0,
        "latency_total": 0.0,
        "latency_count": 0,
        "p95_latency_ms": 0,
        "statuses": {},
    }
    for row in rows:
        worker_id, worker_name = str(row["id"]), row["name"]
        stats = probes.get(worker_id)
        row["health"] = "online" if stats else "offline"
        row["stats"] = stats
        if not stats:
            continue
        totals = stats.get("totals") or {}
        requests_count = int(totals.get("requests") or 0)
        usage["requests"] += requests_count
        usage["success"] += int(totals.get("success") or 0)
        usage["errors"] += int(totals.get("errors") or 0)
        usage["bytes_in"] += int(totals.get("bytes_in") or 0)
        usage["bytes_out"] += int(totals.get("bytes_out") or 0)
        average = float(totals.get("avg_latency_ms") or 0)
        usage["latency_total"] += average * requests_count
        usage["latency_count"] += requests_count
        usage["p95_latency_ms"] = max(usage["p95_latency_ms"], int(totals.get("p95_latency_ms") or 0))
        for status, count in (stats.get("statuses") or {}).items():
            key = str(status)
            usage["statuses"][key] = usage["statuses"].get(key, 0) + int(count or 0)
        for point in stats.get("latency") or []:
            try:
                bucket = latency_buckets.setdefault(int(point["t"]), {
                    "t": int(point["t"]), "count": 0, "total": 0.0, "p95": 0, "errors": 0,
                })
                count = int(point.get("count") or 0)
                bucket["count"] += count
                bucket["total"] += float(point.get("avg") or 0) * count
                bucket["p95"] = max(bucket["p95"], int(point.get("p95") or 0))
                bucket["errors"] += int(point.get("errors") or 0)
            except (KeyError, TypeError, ValueError):
                continue
        for item in stats.get("recent") or []:
            if isinstance(item, dict):
                feed.append({
                    **item,
                    "worker_id": worker_id,
                    "worker_name": worker_name,
                })
        for item in stats.get("errors") or []:
            if isinstance(item, dict):
                errors.append({
                    **item,
                    "worker_id": worker_id,
                    "worker_name": worker_name,
                })

    usage["avg_latency_ms"] = (
        round(usage.pop("latency_total") / usage["latency_count"], 1)
        if usage["latency_count"] else 0
    )
    usage.pop("latency_count", None)
    latency = [
        {
            "t": bucket["t"],
            "count": bucket["count"],
            "avg": round(bucket["total"] / bucket["count"], 1) if bucket["count"] else 0,
            "p95": bucket["p95"],
            "errors": bucket["errors"],
        }
        for bucket in sorted(latency_buckets.values(), key=lambda item: item["t"])
    ]
    feed.sort(key=lambda item: int(item.get("at") or 0), reverse=True)
    errors.sort(key=lambda item: int(item.get("at") or 0), reverse=True)
    return latency, feed[:60], errors[:30], usage


@app.route("/api/staff/proxy-workers", methods=["GET"])
@require_auth
def api_staff_proxy_workers():
    forwarded = _forward_control_to_primary()
    if forwarded is not None:
        return forwarded
    error = _owner_only()
    if error:
        return error
    try:
        rows = run_on_bot_loop(list_proxy_workers(_discord_bot))
        enabled = run_on_bot_loop(proxy_routing_enabled(_discord_bot))
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        return jsonify({"error": "Persistent proxy worker registry is unavailable."}), 503

    manager = _manager(_discord_bot, rows, enabled)
    routing = manager.status()
    try:
        health = run_on_bot_loop(manager.probe_all(), timeout=15)
    except Exception:
        # A slow or wedged worker must not turn the whole owner page into an
        # error; it is reported as offline until the next poll succeeds.
        health = {str(row["id"]): None for row in rows}
    for row in rows:
        row["active"] = bool(manager.enabled)
    latency, feed, errors, usage = _merge_telemetry(rows, health)
    routing["enabled"] = bool(manager.enabled)
    routing["worker_count"] = len(rows)
    routing["online_count"] = sum(1 for row in rows if row.get("health") == "online")
    # Local relay failures are not visible in a worker's own stats when the
    # worker is unreachable, so they belong in the same error list.
    for item in routing.get("recent_errors") or []:
        errors.append({
            "at": item.get("at"),
            "method": "RELAY",
            "path": "/internal/proxy",
            "status": 0,
            "message": item.get("message"),
            "worker_name": item.get("worker"),
        })
    errors.sort(key=lambda item: int(item.get("at") or 0), reverse=True)
    return jsonify({
        "workers": rows,
        "routing": routing,
        "usage": usage,
        "latency": latency,
        "feed": feed,
        "errors": errors[:30],
    })


@app.route("/api/staff/proxy-workers", methods=["POST"])
@require_auth
@require_csrf
def api_add_staff_proxy_worker():
    forwarded = _forward_control_to_primary()
    if forwarded is not None:
        return forwarded
    error = _owner_only()
    if error:
        return error
    token = proxy_worker_token()
    if not token:
        return jsonify({"error": "Set PROXY_WORKER_TOKEN on the bot and the same AUTH_TOKEN secret on the worker."}), 503
    body = request.get_json(silent=True) or {}
    name = str(body.get("name", "")).strip()
    if not name or len(name) > 60:
        return jsonify({"error": "Proxy worker name must be between 1 and 60 characters."}), 400
    try:
        url = standby_origin(_validate_public_https_origin(body.get("url")))
    except ValueError as exc:
        return jsonify({"error": _origin_error(exc)}), 400
    if _is_own_origin(url):
        return jsonify({"error": "A proxy worker cannot use this server's own origin."}), 400

    nonce = secrets.token_urlsafe(32)
    try:
        response = requests.post(
            f"{url}/internal/verify",
            json={"nonce": nonce},
            timeout=8,
            allow_redirects=False,
            headers={"Content-Type": "application/json"},
        )
        if response.status_code != 200:
            return jsonify({"error": "The worker did not pass credential verification. Check its AUTH_TOKEN secret."}), 400
        payload = response.json()
    except (requests.RequestException, ValueError, AttributeError):
        return jsonify({"error": "Could not verify the worker. Confirm its URL is reachable and AUTH_TOKEN matches PROXY_WORKER_TOKEN."}), 400
    if not isinstance(payload, dict) or payload.get("service") != SERVICE:
        return jsonify({"error": "That URL is not a Niko Discord proxy worker."}), 400
    proof = payload.get("proof", "")
    expected = verification_proof(token, nonce)
    if not isinstance(proof, str) or not secrets.compare_digest(proof, expected):
        return jsonify({"error": "PROXY_WORKER_TOKEN does not match the worker's AUTH_TOKEN secret."}), 400

    item = {
        "id": secrets.token_urlsafe(12),
        "name": name,
        "url": url,
        "created_at": int(time.time()),
    }
    try:
        rows = run_on_bot_loop(add_proxy_worker(_discord_bot, item))
        enabled = run_on_bot_loop(proxy_routing_enabled(_discord_bot))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        return jsonify({"error": "The verified proxy worker could not be persisted."}), 503
    _manager(_discord_bot, rows, enabled)
    return jsonify({"ok": True, "worker": item}), 201


@app.route("/api/staff/proxy-workers/<worker_id>", methods=["DELETE"])
@require_auth
@require_csrf
def api_remove_staff_proxy_worker(worker_id):
    forwarded = _forward_control_to_primary()
    if forwarded is not None:
        return forwarded
    error = _owner_only()
    if error:
        return error
    try:
        rows = run_on_bot_loop(remove_proxy_worker(_discord_bot, worker_id))
        enabled = run_on_bot_loop(proxy_routing_enabled(_discord_bot))
    except KeyError:
        return jsonify({"error": "Proxy worker not found."}), 404
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        return jsonify({"error": "Persistent proxy worker registry is unavailable."}), 503
    _manager(_discord_bot, rows, enabled)
    return jsonify({"ok": True})


@app.route("/api/staff/proxy-workers/routing", methods=["POST"])
@require_auth
@require_csrf
def api_control_staff_proxy_routing():
    forwarded = _forward_control_to_primary()
    if forwarded is not None:
        return forwarded
    error = _owner_only()
    if error:
        return error
    body = request.get_json(silent=True) or {}
    enabled = body.get("enabled")
    if not isinstance(enabled, bool):
        return jsonify({"error": "Choose whether proxy worker routing is enabled."}), 400
    if enabled and not proxy_worker_token():
        return jsonify({"error": "Set PROXY_WORKER_TOKEN before enabling proxy worker routing."}), 503
    try:
        rows = run_on_bot_loop(list_proxy_workers(_discord_bot))
        if enabled and not rows:
            return jsonify({"error": "Register at least one proxy worker before enabling routing."}), 400
        run_on_bot_loop(set_proxy_routing_enabled(_discord_bot, enabled))
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        return jsonify({"error": "The routing change could not be persisted."}), 503
    manager = _manager(_discord_bot, rows, enabled)
    return jsonify({"ok": True, "routing": manager.status()})
