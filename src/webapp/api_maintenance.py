"""Stop an API endpoint while its owner-controlled maintenance notice is active.

The toggle lives in :mod:`utils.maintenance` beside cogs and commands, so the
dashboard, status page, and request gate all read the same cache.  Public API
responses stay JSON: a paused endpoint answers 503 with the reason and the same
``maintenance`` shape the status page renders.

``/api/status`` and the auth/health endpoints are never gated.  The status page
has to be able to report an API outage, and an owner must still be able to sign
in and clear the pause.
"""

from __future__ import annotations

from flask import request

from utils import maintenance

from .api_errors import error_response
from .staff import _current_staff_role, _is_owner

_EXEMPT_PATHS = (
    "/api/status",
    "/api/health",
    "/api/auth/",
)


def _is_exempt(path: str) -> bool:
    return path in _EXEMPT_PATHS or path.startswith(_EXEMPT_PATHS[-1])


def api_targets(app) -> list[dict]:
    """Every maintainable API endpoint in one Flask application.

    The gate keys on the endpoint, so a route with a variable path still needs
    only one row.  The status/auth/health routes are excluded because they must
    keep answering while an API is paused.
    """
    rows: dict[str, dict] = {}
    for rule in app.url_map.iter_rules():
        path = str(rule.rule or "")
        if not path.startswith("/api/") or _is_exempt(path):
            continue
        endpoint = str(rule.endpoint or "")
        if not endpoint or endpoint == "static":
            continue
        methods = sorted(method for method in (rule.methods or ()) if method not in {"HEAD", "OPTIONS"})
        row = rows.setdefault(endpoint, {"endpoint": endpoint, "path": path, "methods": methods})
        if not row.get("path"):
            row.update(path=path, methods=methods)
    return list(rows.values())


def register_api_maintenance(app) -> None:
    """Install the API maintenance gate once on the Flask application."""
    if getattr(app, "_api_maintenance_installed", False):
        return
    app._api_maintenance_installed = True

    @app.before_request
    def gate_api_maintenance():
        path = request.path or ""
        if not path.startswith(("/api/", "/v1/")) or _is_exempt(path):
            return None
        found = maintenance.find_api_block(request.endpoint, path)
        if found is None:
            return None
        # Owners keep access to anything they pause, matching the Discord gate.
        # Check the configured owner first; only an actual paused request pays
        # for the live staff-role lookup.
        if _is_owner():
            return None
        try:
            if _current_staff_role() == "owner":
                return None
        except Exception:
            pass
        _kind, key, entry = found
        details = {
            "maintenance": {
                "kind": "api",
                "key": key,
                "label": maintenance.api_label(key),
                "reason": entry.get("reason"),
                "since": entry.get("since"),
            },
        }
        if entry.get("report_code"):
            details["report_code"] = entry["report_code"]
        return error_response(
            "API_MAINTENANCE",
            "This API is in maintenance mode.",
            503,
            docs="/developers/maintenance",
            details=details,
            headers={"Retry-After": "300"},
        )
