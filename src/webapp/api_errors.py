"""Shared error envelope for the versioned developer API.

Every public API failure answers with the same top-level shape:

``{"error": "...", "code": "STABLE_CODE", "docs": "/developers/errors"}``

The ``error`` string stays compatible with the portal client and older
integrations, while ``code`` is the stable value an integration can branch on
or quote in a support ticket. Server-side failures that are recorded through
the staff error-report store also carry the six-character ``report_code``.
"""

from __future__ import annotations

from flask import jsonify

ERROR_DOCS = "/developers/errors"


def error_response(
    code: str,
    message: str,
    status: int,
    *,
    docs: str | None = None,
    details: dict | None = None,
    headers: dict | None = None,
    report: bool = False,
    exception: BaseException | None = None,
    summary: str | None = None,
):
    """Build one JSON API error, optionally storing it as a staff report.

    ``report`` is reserved for unexpected or backend failures. Expected client
    mistakes (bad input, invalid keys, 429s) get a stable code but do not create
    error reports, so a noisy or malicious caller cannot flood the staff store.
    """
    payload = {
        "error": str(message),
        "code": str(code),
        "docs": docs or ERROR_DOCS,
    }
    if isinstance(details, dict):
        payload.update(details)
    if report:
        try:
            from .error_reporting import record_api_error

            report_code = record_api_error(
                exception or RuntimeError(f"{code}: {message}"),
                code=code,
                summary=summary or message,
                extra=details,
            )
            if report_code:
                payload["report_code"] = report_code
        except Exception:
            # Reporting must never replace the API's own error response.
            pass
    response = jsonify(payload)
    response.status_code = int(status)
    response.headers["X-Error-Code"] = str(code)
    if payload.get("report_code"):
        response.headers["X-Error-Report"] = str(payload["report_code"])
    if headers:
        for name, value in headers.items():
            response.headers[str(name)] = str(value)
    return response
