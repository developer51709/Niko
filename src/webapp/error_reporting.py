"""Report unhandled website and API exceptions to the staff report store.

The bot's command and gateway handlers already call ``save_error_report``.
This module is the web equivalent: Flask hands every otherwise-unhandled
exception to one handler, which captures the request context (with credentials
and tokens removed), stores the report through the bot loop, and answers the
visitor without exposing the traceback.
"""

from __future__ import annotations

import asyncio
import traceback
from urllib.parse import urlsplit, urlunsplit

from flask import Response, jsonify, make_response, request, session
from werkzeug.exceptions import HTTPException

from utils import logging
from utils.error_reports import save_error_report
from . import runtime, social


#: Query, form, and JSON keys whose values must never reach the report
#: database.  The exact list catches short names such as ``code`` and ``state``
#: that are credentials in an OAuth callback; the fragments catch variants such
#: as ``access_token`` or ``client_secret``.
_SENSITIVE_EXACT = {
    "authorization", "code", "cookie", "csrf", "csrf_token", "passwd",
    "password", "secret", "session", "state", "token",
}
_SENSITIVE_FRAGMENTS = (
    "apikey", "api_key", "credential", "csrf", "passwd", "password",
    "private_key", "secret", "token",
)

_MAX_DEPTH = 5
_MAX_ITEMS = 40
_MAX_STRING = 600


def _is_sensitive(key: str) -> bool:
    lowered = str(key or "").strip().lower()
    return lowered in _SENSITIVE_EXACT or any(
        fragment in lowered for fragment in _SENSITIVE_FRAGMENTS
    )


def _redact_value(value, depth: int = 0):
    """Return a bounded, JSON-safe copy of request data with secrets removed."""
    if depth > _MAX_DEPTH:
        return "…"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value[:_MAX_STRING] + ("…" if len(value) > _MAX_STRING else "")
    if isinstance(value, dict):
        result = {}
        for index, (key, item) in enumerate(value.items()):
            if index >= _MAX_ITEMS:
                result["…"] = f"{len(value) - _MAX_ITEMS} more field(s)"
                break
            name = str(key)[:120]
            result[name] = "<redacted>" if _is_sensitive(name) else _redact_value(item, depth + 1)
        return result
    if isinstance(value, (list, tuple, set, frozenset)):
        items = list(value)
        result = [_redact_value(item, depth + 1) for item in items[:_MAX_ITEMS]]
        if len(items) > _MAX_ITEMS:
            result.append(f"… {len(items) - _MAX_ITEMS} more item(s)")
        return result
    return repr(value)[:300]


def _strip_query(url: str | None) -> str | None:
    """Keep a referrer useful without copying its query string into a report."""
    if not url:
        return None
    try:
        parts = urlsplit(str(url))
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))[:_MAX_STRING]
    except Exception:
        return str(url).split("?", 1)[0][:_MAX_STRING]


def _request_body():
    """The submitted JSON or form data, bounded and redacted."""
    if request.is_json:
        try:
            return _redact_value(request.get_json(silent=True))
        except Exception:
            return None
    if request.form:
        return _redact_value(dict(request.form.lists()))
    return None


def _request_context() -> dict:
    """Everything useful about the failing request, minus sensitive values."""
    rule = getattr(request, "url_rule", None)
    context = {
        "request": {
            "method": request.method,
            "path": request.path[:_MAX_STRING],
            "endpoint": request.endpoint,
            "route": getattr(rule, "rule", None),
            "query": _redact_value(dict(request.args.lists())),
            "content_type": request.content_type,
            "user_agent": (request.user_agent.string or "")[:_MAX_STRING] or None,
            "remote_addr": request.remote_addr,
            "referer": _strip_query(request.referrer),
            "body": _request_body(),
            "form_fields": list(request.form.keys())[:_MAX_ITEMS] or None,
            "file_fields": list(request.files.keys())[:_MAX_ITEMS] or None,
        },
    }
    user = session.get("user") or {}
    if user:
        # The signed-in identity comes from the session, so reporting never has
        # to schedule another query on the bot loop while it is handling a
        # failure.  A staff-role lookup would risk delaying the error page.
        context["user"] = {
            "id": str(user.get("id") or ""),
            "name": str(user.get("global_name") or user.get("username") or ""),
            "username": str(user.get("username") or ""),
        }
    return context


def _persist(error: BaseException, context: dict, source: str, summary: str) -> str | None:
    """Save a web report on the bot loop when it is available.

    The Flask request runs in a worker thread while the report database lives on
    the bot's event loop.  If the bot is not running, the report is still worth
    trying on a private loop rather than dropping it.
    """
    bot = runtime._discord_bot
    coroutine = save_error_report(
        error, context, bot, source=source, summary=summary
    )
    loop = getattr(bot, "loop", None) if bot is not None else None
    if loop is not None and loop.is_running():
        code, _ = runtime.run_on_bot_loop(coroutine, timeout=10)
    else:
        code, _ = asyncio.run(coroutine)
    return code


def _fallback_page(report_code: str | None) -> str:
    code_line = (
        f"<p>Reference: <code>{report_code}</code></p>"
        if report_code else ""
    )
    return (
        "<!doctype html><html lang=\"en\"><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>Something went wrong · Niko</title>"
        "<body style=\"margin:0;min-height:100vh;display:grid;place-items:center;"
        "background:#111315;color:#e8e3da;font:15px/1.7 system-ui,sans-serif\">"
        "<main style=\"max-width:560px;padding:32px\">"
        "<p style=\"color:#c8a882;font-size:11px;letter-spacing:.16em;"
        "text-transform:uppercase\">Niko</p>"
        "<h1 style=\"font-size:28px;letter-spacing:-.04em\">Something went wrong.</h1>"
        "<p style=\"color:#a5a29c\">The error was recorded for the staff team. "
        "Try again in a moment, or include the reference below in a support request.</p>"
        f"{code_line}</main></body></html>"
    )


def _error_response(source: str, report_code: str | None):
    if source == "api":
        return jsonify({
            "error": "An unexpected server error occurred.",
            "report_code": report_code,
        }), 500
    try:
        response = make_response(social.render_site_shell())
        response.status_code = 500
    except Exception:
        return Response(_fallback_page(report_code), status=500, mimetype="text/html")
    if report_code:
        response.headers["X-Error-Report"] = report_code
    return response


def register_error_reporting(app) -> None:
    """Install the website/API unhandled-exception reporter on ``app``."""
    if getattr(app, "_error_reporting_installed", False):
        return
    app._error_reporting_installed = True

    @app.errorhandler(Exception)
    def handle_unhandled_error(error):
        # Handled HTTP responses (404, 405, an intentional abort) are not
        # incidents; Flask's own handlers should keep answering them.
        if isinstance(error, HTTPException):
            return error

        source = "api" if request.path.startswith("/api/") else "website"
        summary = (
            f"{request.method} {request.path} · "
            f"{type(error).__name__}: {error}"
        )[:600]
        report_code = None
        try:
            report_code = _persist(error, _request_context(), source, summary)
        except Exception as storage_error:
            logging.error(
                "WebErrors",
                f"Could not create a {source} error report: {storage_error}",
            )
        logging.error(
            "WebErrors",
            f"Unhandled {source} error"
            f"{f' (report {report_code})' if report_code else ''}: "
            f"{type(error).__name__}: {error}",
        )
        traceback.print_exception(type(error), error, error.__traceback__)
        return _error_response(source, report_code)
