"""Niko's owner MCP server.

The server is deliberately small and stateless: every POST is one JSON-RPC
request (or a batch), authenticated with the owner's MCP token.  It exposes
deployment, diagnostics, error-report and incident tools over the same Flask
application that serves the dashboard, so there is no second process to keep
alive and no beta instance to pull from.

Remote MCP clients connect to ``https://mcp.<site>/mcp`` with the owner key
generated on the MCP Server staff page.  Only a salted PBKDF2-SHA256 digest is
stored in the bot database, and the endpoint verifies that digest on every
request, so rotating the key takes effect immediately without a restart.
"""

from __future__ import annotations

import html
import json
import os
import secrets
from typing import Any

from flask import Response, has_request_context, jsonify, request

from utils import mcp_keys

from . import config, runtime, updates

LATEST_PROTOCOL = "2025-06-18"
SUPPORTED_PROTOCOLS = ("2025-06-18", "2025-03-26", "2024-11-05")
SERVER_NAME = "niko"
SERVER_VERSION = "1.0.0"
AUTH_HEADER = "Authorization: Bearer <MCP key>"


def key_summary() -> dict:
    """The current key metadata, read from the database without the key value."""
    bot = _bot()
    try:
        if bot is None:
            return mcp_keys.local_info()
        return _run(mcp_keys.info(bot), timeout=10)
    except Exception as exc:
        return {
            **mcp_keys.empty_info(),
            "error": f"{type(exc).__name__}: {exc}",
        }


def rotate_key(created_by: str | None, created_by_name: str | None) -> dict:
    """Generate a key and replace the stored hash immediately."""
    bot = _bot()
    if bot is None:
        return mcp_keys.local_rotate(created_by, created_by_name)
    return _run(
        mcp_keys.rotate(created_by, created_by_name, bot=bot),
        timeout=20,
    )


def endpoint() -> str:
    """The public URL a Freebuff integration should use."""
    explicit = (os.environ.get("MCP_ORIGIN") or "").strip().rstrip("/")
    if explicit.startswith(("http://", "https://")):
        return f"{explicit}/mcp"
    host = config.public_domain()
    if host:
        port = ""
        canonical = config.canonical_origin()
        if canonical:
            from urllib.parse import urlparse

            parsed = urlparse(canonical)
            if parsed.port:
                port = f":{parsed.port}"
        scheme = "http" if canonical.startswith("http://") else "https"
        return f"{scheme}://{config.MCP_SUBDOMAIN}.{host}{port}/mcp"
    if has_request_context():
        proto = (request.headers.get("X-Forwarded-Proto") or request.scheme or "https").split(",", 1)[0].strip()
        host = runtime.request_host()
        return f"{proto}://{host}/mcp"
    return ""


def _authorised(headers) -> bool:
    supplied = (headers.get("Authorization") or "").strip()
    if supplied.lower().startswith("bearer "):
        supplied = supplied[7:].strip()
    if not supplied:
        supplied = (headers.get("X-MCP-Key") or "").strip()
    if (
        not supplied
        or len(supplied) > 128
        or not supplied.startswith(mcp_keys.KEY_PREFIX)
    ):
        # Reject obvious junk before touching the database or running PBKDF2.
        # A public MCP host otherwise lets any caller spend a full KDF per
        # request with an arbitrary string.
        return False
    bot = _bot()
    try:
        if bot is None:
            return mcp_keys.local_verify(supplied)
        return bool(_run(mcp_keys.verify(supplied, bot), timeout=10))
    except Exception:
        # A database outage must fail closed: an unverified key can never be
        # treated as the owner because storage is temporarily unavailable.
        return False


def _empty_schema() -> dict:
    return {"type": "object", "properties": {}, "additionalProperties": False}


def _schema(properties: dict, required: list[str] | None = None) -> dict:
    value = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }
    if required:
        value["required"] = required
    return value


REPORT_STATUSES = (
    "awaiting_review",
    "under_review",
    "fix_needed",
    "investigating_fix",
    "developing_fix",
    "testing_fix",
    "resolved",
)

TOOLS: list[dict] = [
    {
        "name": "niko_status",
        "description": "Current bot, gateway, cog, incident and deployment state. Use this before debugging or deploying.",
        "inputSchema": _empty_schema(),
    },
    {
        "name": "niko_logs",
        "description": "Read the most recent bot/supervisor/dashboard log lines. The log store is read-only and never exposes environment secrets.",
        "inputSchema": _schema({
            "process": {"type": "string", "enum": ["all", "bot", "web", "dashboard", "db", "database", "supervisor"], "default": "all"},
            "level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "ALL"], "default": "INFO"},
            "lines": {"type": "integer", "minimum": 1, "maximum": 500, "default": 200},
        }),
    },
    {
        "name": "niko_error_reports",
        "description": "List recent error reports, optionally filtered by review status. Includes the full stored report document.",
        "inputSchema": _schema({
            "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 25},
            "status": {"type": "string", "enum": list(REPORT_STATUSES)},
        }),
    },
    {
        "name": "niko_error_report",
        "description": "Read one error report by its six-character code.",
        "inputSchema": _schema({
            "code": {"type": "string", "minLength": 6, "maxLength": 6},
        }, ["code"]),
    },
    {
        "name": "niko_set_error_report_status",
        "description": "Move an error report through its review workflow. This records the MCP server as the actor.",
        "inputSchema": _schema({
            "code": {"type": "string", "minLength": 6, "maxLength": 6},
            "status": {"type": "string", "enum": list(REPORT_STATUSES)},
        }, ["code", "status"]),
    },
    {
        "name": "niko_incidents",
        "description": "List incidents currently published on the public status page, including their public timeline and maintenance target.",
        "inputSchema": _schema({
            "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 20},
        }),
    },
    {
        "name": "niko_update_incident",
        "description": "Publish, update or resolve a public incident from an error report. Optionally pause or resume the report's linked API or command maintenance target.",
        "inputSchema": _schema({
            "code": {"type": "string", "minLength": 6, "maxLength": 6},
            "public_notice": {"type": "boolean"},
            "severity": {"type": "string", "enum": ["minor", "major", "critical"]},
            "maintenance_enabled": {"type": "boolean"},
            "maintenance_kind": {"type": "string", "enum": ["api", "command"]},
            "maintenance_key": {"type": "string", "maxLength": 160},
        }, ["code"]),
    },
    {
        "name": "niko_update_status",
        "description": "Inspect the last deployment, the live update progress and the update source configuration.",
        "inputSchema": _empty_schema(),
    },
    {
        "name": "niko_announce",
        "description": "Send an announcement to the support server's announcements channel and ping its announcements role. The title and message are supplied by the caller; no announcement text is built into the bot. Optional images are delivered as real Discord attachments in a media gallery, like staff broadcasts.",
        "inputSchema": _schema({
            "title": {"type": "string", "minLength": 1, "maxLength": 160},
            "body": {"type": "string", "minLength": 1, "maxLength": 3800},
            "footer": {"type": "string", "maxLength": 120},
            "ping": {"type": "boolean", "default": True},
            "images": {
                "type": "array",
                "maxItems": 10,
                "description": "Up to 10 PNG, JPEG, GIF, or WebP images. Each image is base64-encoded and uploaded as a Discord attachment, so the announcement keeps its images even if an external link expires.",
                "items": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string",
                            "minLength": 1,
                            "description": "Base64-encoded image bytes, or a base64 data URI. The image type is detected from the bytes.",
                        },
                        "filename": {
                            "type": "string",
                            "maxLength": 120,
                            "description": "Optional filename stem. Niko adds a unique suffix and the detected extension.",
                        },
                        "spoiler": {"type": "boolean", "default": False},
                    },
                    "required": ["data"],
                    "additionalProperties": False,
                },
            },
        }, ["title", "body"]),
    },
    {
        "name": "niko_deploy_commit",
        "description": "Deploy the files changed by a pushed GitHub commit. Prefer this over niko_deploy for normal updates and large files: the server fetches the changed files at the immutable commit SHA, verifies each blob hash, and applies only deployable areas. The commit must already be pushed to the Niko repository.",
        "inputSchema": _schema({
            "ref": {
                "type": "string",
                "pattern": "^[0-9a-fA-F]{40}$",
                "description": "Full 40-character commit SHA, from `git rev-parse HEAD`.",
            },
            "paths": {
                "type": "array",
                "maxItems": 250,
                "items": {"type": "string"},
                "description": "Optional exact paths to deploy from the commit. Omit to deploy every changed file in an updatable area.",
            },
        }, ["ref"]),
    },
    {
        "name": "niko_deploy",
        "description": "Deploy small file contents directly. Prefer niko_deploy_commit for normal updates: inline content has to fit in one JSON-RPC request and is unreliable for large files. Paths must be inside an updatable area; the server backs up, syntax-checks, reloads and restarts only the affected areas.",
        "inputSchema": _schema({
            "files": {
                "type": "array",
                "minItems": 1,
                "maxItems": 250,
                "items": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Repository-relative path, e.g. src/cogs/automod/foo.py or src/website/dist/index.html."},
                        "content": {"type": "string"},
                        "encoding": {"type": "string", "enum": ["utf-8", "base64"], "default": "utf-8"},
                        "status": {"type": "string", "enum": ["added", "modified", "removed"], "default": "modified"},
                    },
                    "required": ["path"],
                    "additionalProperties": False,
                },
            },
        }, ["files"]),
    },
]


def tool_catalog() -> list[dict]:
    """A safe public summary for the staff page and GET /mcp."""
    return [
        {"name": tool["name"], "description": tool["description"]}
        for tool in TOOLS
    ]


def _text_result(value: Any, *, error: bool = False) -> dict:
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, indent=2, ensure_ascii=False, default=str)
    return {"content": [{"type": "text", "text": text}], "isError": error}


def _bot():
    return runtime._discord_bot


def _run(coroutine, timeout: float = 20):
    if runtime._discord_bot is None:
        coroutine.close()
        raise RuntimeError("The Discord bot is not running.")
    try:
        return runtime.run_on_bot_loop(coroutine, timeout=timeout)
    except BaseException:
        coroutine.close()
        raise


def _status() -> dict:
    payload = {
        "server": {
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            **key_summary(),
            "process": os.environ.get("NIKO_WEB_ROLE") == "1" and "dashboard" or "bot",
        },
        "update": {
            "progress": updates.progress(),
            "last": updates.last_run(),
            "beta_configured": updates.configured(),
            "handoff": None,
        },
    }
    try:
        from utils.runtime import handoff

        payload["update"]["handoff"] = handoff.last()
    except Exception:
        pass
    bot = _bot()
    if bot is None:
        try:
            from .status import offline_status

            payload["status"] = offline_status("The Discord bot is not available in this process.")
        except Exception as exc:
            payload["status"] = {"online": False, "reason": str(exc)}
        return payload
    try:
        from .status import bot_status

        payload["status"] = _run(bot_status(bot), timeout=15)
    except Exception as exc:
        payload["status"] = {"online": False, "reason": f"{type(exc).__name__}: {exc}"}
    return payload


def _logs(args: dict) -> dict:
    limit = max(1, min(int(args.get("lines") or 200), 500))
    process = str(args.get("process") or "all").strip().lower()
    level = str(args.get("level") or "INFO").strip().upper()
    if level == "ALL":
        level = "DEBUG"
    try:
        from .routes import log_routes
        from log_store import LogArchive

        buffer = log_routes._log_buffer()
        if buffer is None:
            return {"lines": [], "unavailable": True, "reason": "No log buffer is available in this process."}
        if isinstance(buffer, LogArchive):
            return buffer.snapshot(processes=process, min_level=level, since="", limit=limit)
        return log_routes._memory_snapshot(buffer, "", limit, process, level)
    except Exception as exc:
        return {"lines": [], "unavailable": True, "error": f"{type(exc).__name__}: {exc}"}


def _reports(args: dict) -> dict:
    from utils.error_reports import list_error_reports

    limit = max(1, min(int(args.get("limit") or 25), 100))
    status = str(args.get("status") or "").strip().lower()
    reports = _run(list_error_reports(_bot(), limit=limit))
    if status:
        reports = [item for item in reports if item.get("status") == status]
    return {"reports": reports, "count": len(reports)}


def _report(args: dict) -> dict:
    from utils.error_reports import get_error_report_item

    code = str(args.get("code") or "").strip().upper()
    item = _run(get_error_report_item(code, _bot()))
    if item is None:
        raise LookupError(f"No error report exists with code {code}.")
    return item


def _set_report_status(args: dict) -> dict:
    from utils.error_reports import REPORT_STATUSES as STATUSES
    from utils.error_reports import set_error_report_status

    code = str(args.get("code") or "").strip().upper()
    status = str(args.get("status") or "").strip().lower()
    if status not in STATUSES:
        raise ValueError(f"status must be one of {', '.join(STATUSES)}.")
    item = _run(set_error_report_status(code, status, "mcp", "Niko MCP", _bot()))
    if item is None:
        raise LookupError(f"No error report exists with code {code}.")
    return item


def _incidents(args: dict) -> dict:
    from utils.error_reports import list_public_incidents

    limit = max(1, min(int(args.get("limit") or 20), 50))
    incidents = _run(list_public_incidents(_bot(), limit=limit))
    return {"incidents": incidents, "count": len(incidents)}


def _update_incident(args: dict) -> dict:
    from utils import maintenance
    from utils.error_reports import (
        DEFAULT_REPORT_SEVERITY,
        REPORT_SEVERITIES,
        get_error_report_item,
        public_incident_label,
        set_error_report_incident,
    )
    from .api_maintenance import api_targets

    code = str(args.get("code") or "").strip().upper()
    item = _run(get_error_report_item(code, _bot()))
    if item is None:
        raise LookupError(f"No error report exists with code {code}.")

    requested_public = args.get("public_notice")
    if requested_public is not None and not isinstance(requested_public, bool):
        raise ValueError("public_notice must be true or false.")
    severity = str(args.get("severity") or "").strip().lower()
    if severity and severity not in REPORT_SEVERITIES:
        raise ValueError("severity must be minor, major, or critical.")

    enabled = args.get("maintenance_enabled")
    if enabled is not None and not isinstance(enabled, bool):
        raise ValueError("maintenance_enabled must be true or false.")
    kind = str(args.get("maintenance_kind") or "").strip().lower() or None
    key = str(args.get("maintenance_key") or "").strip() or None
    if enabled and (kind not in {"api", "command"} or not key or len(key) > 160):
        raise ValueError("Enabling maintenance needs kind=api|command and a key up to 160 characters.")

    if item.get("report", {}).get("classification") == "user_error" and (
        enabled or requested_public
    ):
        raise ValueError("A user-error report cannot be published or put into maintenance.")

    resuming = enabled is False
    if requested_public is False and not resuming and item.get("maintenance_kind") and item.get("maintenance_key"):
        raise ValueError("Resume the linked maintenance target before removing the public notice.")

    if enabled:
        _run(maintenance.ensure_loaded(_bot()))
        # The route's validation is repeated here with the live snapshot; do it
        # inside the bot loop so command targets are the ones currently loaded.
        async def validate_and_pause():
            from .server import app as flask_app

            snapshot = maintenance.snapshot(_bot(), api_targets(flask_app))
            if kind == "command":
                if not any(row["name"] == key for row in snapshot["commands"]):
                    raise LookupError("That command does not exist on the bot.")
            elif not any(row["endpoint"] == key for row in snapshot["apis"]):
                raise LookupError("That API endpoint does not exist.")
            summary = str(item["report"].get("summary") or "").strip()
            exception = item["report"].get("exception") or {}
            reason = (summary or str(exception.get("name") or "Service incident"))[:maintenance.MAX_REASON]
            await maintenance.set_maintenance(
                kind, key, True, reason, "mcp", _bot(), report_code=code,
            )
            try:
                return await set_error_report_incident(
                    code,
                    public_notice=True,
                    severity=severity or item.get("severity") or DEFAULT_REPORT_SEVERITY,
                    maintenance_enabled=True,
                    maintenance_kind=kind,
                    maintenance_key=key,
                    staff_id="mcp",
                    staff_name="Niko MCP",
                    bot=_bot(),
                )
            except Exception:
                # Never leave an API or command paused without an incident.
                await maintenance.set_maintenance(
                    kind, key, False, actor="mcp", bot=_bot(),
                )
                raise

        result = _run(validate_and_pause(), timeout=30)
    elif enabled is False:
        async def resume():
            target_kind = item.get("maintenance_kind") or kind
            target_key = item.get("maintenance_key") or key
            if target_kind and target_key:
                await maintenance.set_maintenance(target_kind, target_key, False, actor="mcp", bot=_bot())
            return await set_error_report_incident(
                code,
                public_notice=item.get("public_notice") if requested_public is None else requested_public,
                severity=severity or item.get("severity") or DEFAULT_REPORT_SEVERITY,
                maintenance_enabled=False,
                maintenance_kind=target_kind,
                maintenance_key=target_key,
                staff_id="mcp",
                staff_name="Niko MCP",
                bot=_bot(),
            )

        result = _run(resume(), timeout=30)
    else:
        result = _run(set_error_report_incident(
            code,
            public_notice=requested_public if requested_public is not None else bool(item.get("public_notice")),
            severity=severity or item.get("severity") or DEFAULT_REPORT_SEVERITY,
            maintenance_enabled=None,
            staff_id="mcp",
            staff_name="Niko MCP",
            bot=_bot(),
        ))
    if result is None:
        raise LookupError(f"No error report exists with code {code}.")
    result["public_state"] = public_incident_label(result.get("status"))
    return result


def _update_status() -> dict:
    return {
        "progress": updates.progress(),
        "last": updates.last_run(),
        "beta_configured": updates.configured(),
    }


def _announce(args: dict) -> dict:
    from utils.announcements import send_support_announcement

    title = str(args.get("title") or "").strip()
    body = str(args.get("body") or "").strip()
    footer = str(args.get("footer") or "").strip()
    ping = args.get("ping", True)
    if not isinstance(ping, bool):
        raise ValueError("ping must be true or false.")
    images = args.get("images") or []
    if not isinstance(images, list):
        raise ValueError("images must be an array.")
    return _run(
        send_support_announcement(
            _bot(), title=title, body=body, footer=footer or None, ping=ping,
            images=images,
        ),
        timeout=60,
    )


def _deploy(args: dict) -> dict:
    from .mcp_deploy import apply_payloads

    files = args.get("files")
    return apply_payloads(files, _bot(), actor="MCP")


def _deploy_commit(args: dict) -> dict:
    from .mcp_deploy import apply_commit

    ref = str(args.get("ref") or "").strip().lower()
    paths = args.get("paths")
    return apply_commit(ref, paths=paths, bot=_bot(), actor="MCP commit")


def _call_tool(name: str, arguments: dict | None) -> dict:
    arguments = arguments if isinstance(arguments, dict) else {}
    if name == "niko_status":
        return _status()
    if name == "niko_logs":
        return _logs(arguments)
    if name == "niko_error_reports":
        return _reports(arguments)
    if name == "niko_error_report":
        return _report(arguments)
    if name == "niko_set_error_report_status":
        return _set_report_status(arguments)
    if name == "niko_incidents":
        return _incidents(arguments)
    if name == "niko_update_incident":
        return _update_incident(arguments)
    if name == "niko_update_status":
        return _update_status()
    if name == "niko_announce":
        return _announce(arguments)
    if name == "niko_deploy":
        return _deploy(arguments)
    if name == "niko_deploy_commit":
        return _deploy_commit(arguments)
    raise LookupError(f"Unknown tool: {name}")


def _error(message: str, code: int, request_id=None, data: Any = None) -> dict:
    error: dict = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


def _handle_one(message: dict) -> dict | None:
    if not isinstance(message, dict):
        return _error("Invalid JSON-RPC message.", -32600)
    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}
    if not isinstance(params, dict):
        params = {}
    if message.get("jsonrpc") not in (None, "2.0"):
        return _error("Unsupported JSON-RPC version.", -32600, request_id)
    if not isinstance(method, str):
        return _error("Missing method.", -32600, request_id)

    if method.startswith("notifications/"):
        return None
    if method == "initialize":
        requested = str(params.get("protocolVersion") or "")
        protocol = requested if requested in SUPPORTED_PROTOCOLS else LATEST_PROTOCOL
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": protocol,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                "instructions": (
                    "Niko owner tools. Inspect niko_status first. Push a commit, then "
                    "use niko_deploy_commit to apply its changed files; niko_deploy is "
                    "only for small inline hotfixes. Use niko_announce to post a "
                    "caller-authored announcement to the support server."
                ),
            },
        }
    if method == "ping":
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        name = params.get("name")
        if not isinstance(name, str) or not name:
            return _error("tools/call needs a tool name.", -32602, request_id)
        try:
            result = _call_tool(name, params.get("arguments"))
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": _text_result(f"{type(exc).__name__}: {exc}", error=True),
            }
        return {"jsonrpc": "2.0", "id": request_id, "result": _text_result(result)}
    if method == "resources/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"resources": []}}
    if method == "prompts/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"prompts": []}}
    if method == "logging/setLevel":
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}
    return _error(f"Method not found: {method}", -32601, request_id)


def handle_messages(payload) -> list[dict]:
    messages = payload if isinstance(payload, list) else [payload]
    responses = []
    for message in messages:
        response = _handle_one(message)
        if response is not None:
            responses.append(response)
    return responses


def _json_response(payload, status: int = 200):
    response = jsonify(payload)
    response.status_code = status
    response.headers["Cache-Control"] = "no-store"
    response.headers["MCP-Protocol-Version"] = LATEST_PROTOCOL
    return response


def handle_http():
    """Flask view for POST/GET /mcp."""
    if not _authorised(request.headers):
        response = _json_response({"error": "Unauthorized."}, 401)
        response.headers["WWW-Authenticate"] = "Bearer"
        return response
    if request.method == "DELETE":
        # The server is stateless, but Streamable HTTP clients may still end a
        # session explicitly. Accepting it keeps that client from treating the
        # endpoint as broken on shutdown.
        return Response(status=204)
    if request.method == "GET":
        return _json_response({
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "protocolVersion": LATEST_PROTOCOL,
            "tools": tool_catalog(),
        })
    payload = request.get_json(silent=True)
    if payload is None:
        return _json_response(_error("Parse error.", -32700), 400)
    responses = handle_messages(payload)
    if not responses:
        return Response(status=202)
    body = responses[0] if not isinstance(payload, list) else responses
    response = _json_response(body)
    if isinstance(payload, dict) and payload.get("method") == "initialize":
        response.headers["Mcp-Session-Id"] = secrets.token_hex(16)
    return response


def landing_response() -> Response:
    """The small page served at the root of the MCP subdomain."""
    tools = "".join(
        f"<li><code>{html.escape(tool['name'])}</code><span>{html.escape(tool['description'])}</span></li>"
        for tool in tool_catalog()
    )
    # This landing page is served by the dashboard child, which does not own the
    # bot database. Do not infer whether a key exists from that child's local
    # fallback; the staff page is the authoritative place to check key status.
    status = "Owner managed"
    status_class = "ok"
    body = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Niko MCP</title>
<style>
:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:#070a10;color:#e9edf4;font:15px/1.6 ui-sans-serif,system-ui,sans-serif}}
main{{width:min(760px,calc(100% - 40px));margin:0 auto;padding:64px 0 80px}}a{{color:#f0b49d}}h1{{margin:12px 0 8px;font-size:clamp(2rem,6vw,3.4rem);line-height:1.05;letter-spacing:-.05em}}
.eyebrow{{color:#858c96;font:700 11px/1 ui-monospace,monospace;letter-spacing:.16em;text-transform:uppercase}}
p{{color:#b5bdc9;max-width:62ch}}.status{{display:inline-flex;align-items:center;gap:7px;margin-top:22px;padding:6px 10px;border:1px solid #292b30;border-radius:999px;font:700 11px ui-monospace,monospace;text-transform:uppercase;letter-spacing:.08em}}
.status:before{{width:7px;height:7px;border-radius:50%;background:#e7a58d;content:""}}.status.ok:before{{background:#8bd5b1}}.status.off:before{{background:#d17c72}}
section{{margin-top:38px;padding-top:26px;border-top:1px solid #20242b}}h2{{font-size:15px;letter-spacing:.02em}}code{{color:#f4d3c7;font:13px ui-monospace,monospace;overflow-wrap:anywhere}}
pre{{padding:15px;background:#0f141c;border:1px solid #252b35;border-radius:9px;overflow:auto;color:#d6dce6}}
ul{{list-style:none;padding:0;display:grid;gap:10px}}li{{display:grid;gap:3px;padding:12px 14px;background:#0f141c;border:1px solid #202833;border-radius:8px}}li span{{color:#929ba8;font-size:13px}}
</style></head><body><main>
<span class="eyebrow">Niko · owner automation</span>
<h1>MCP Server.</h1>
<p>A direct, authenticated control surface for the Niko bot. Connect it as a remote MCP server in Freebuff to deploy files, inspect logs, triage error reports, manage public incidents and send support announcements.</p>
<span class="status {status_class}">{status}</span>
<section><h2>Connection</h2><pre>URL: {html.escape(endpoint())}
Header: {html.escape(AUTH_HEADER)}</pre><p>Generate or rotate the key on the owner's MCP Server staff page. Only a salted PBKDF2-SHA256 digest is stored, and rotation applies immediately without a restart.</p></section>
<section><h2>Tools</h2><ul>{tools}</ul></section>
</main></body></html>"""
    response = Response(body, mimetype="text/html")
    # The status dot reports whether the owner key exists, so never serve a
    # stale landing page from a cache after it is generated or rotated.
    response.headers["Cache-Control"] = "no-store"
    return response


def staff_payload() -> dict:
    """Owner-only configuration data for the staff workspace."""
    summary = key_summary()
    return {
        "configured": summary["configured"],
        "endpoint": endpoint(),
        "origin": endpoint().rsplit("/mcp", 1)[0],
        "auth_header": AUTH_HEADER,
        "key": summary,
        "tools": tool_catalog(),
        "beta_configured": updates.configured(),
        "last": updates.last_run(),
    }
