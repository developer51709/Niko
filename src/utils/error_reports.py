"""Dedicated database storage for staff-retrievable error reports.

A report is stored as one versioned JSON document in the existing
``error_reports.report`` column.  Keeping the document in that column means the
SQLite and Mongo backends, the review-state columns, and every existing report
keep working while the report itself becomes structured data instead of a blob
of text that the dashboard has to scrape.

Older rows contain the plain-text format from the previous version of this
module.  They are parsed on read (and rewritten as JSON on startup), so staff do
not lose the tracebacks collected before the change.
"""

from __future__ import annotations

import asyncio
import json
import os
import platform
import secrets
import string
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite

from database import SQLitePool, named_pool
from utils import logging


#: The review states a report can be in, in the order the dashboard offers
#: them: triage first, then the fix moving from investigation to testing.
REPORT_STATUSES = {
    "awaiting_review": "Awaiting review",
    "under_review": "Under review",
    "fix_needed": "Fix needed",
    "investigating_fix": "Investigating fix",
    "developing_fix": "Developing fix",
    "testing_fix": "Testing fix",
    "resolved": "Resolved",
}
DEFAULT_REPORT_STATUS = "awaiting_review"

#: The owner-picked size of a public incident.  A report stays private until an
#: owner publishes it, so these labels never imply automatic publication.
REPORT_SEVERITIES = {
    "minor": "Minor",
    "major": "Major",
    "critical": "Critical",
}
DEFAULT_REPORT_SEVERITY = "minor"

#: How a review state reads to someone looking at the public status page.  The
#: review workflow is internal; the incident only has to say what is happening.
PUBLIC_INCIDENT_STATES = {
    "investigating": "Investigating",
    "identified": "Identified",
    "fixing": "Fixing",
    "monitoring": "Monitoring",
    "resolved": "Resolved",
}

_STATUS_TO_PUBLIC = {
    "awaiting_review": "investigating",
    "under_review": "investigating",
    "fix_needed": "identified",
    "investigating_fix": "investigating",
    "developing_fix": "fixing",
    "testing_fix": "monitoring",
    "resolved": "resolved",
}

#: Exceptions that are the member's mistake, not something the bot can fix by
#: being paused.  They are kept as support context and never become incidents.
_USER_ERROR_NAMES = {
    "PermissionError",
    "Forbidden",
    "NotFound",
    "Unauthorized",
    "BadRequest",
    "MethodNotAllowed",
    "HTTPException",
    "MissingPermissions",
    "BotMissingPermissions",
    "MissingRole",
    "MissingAnyRole",
    "CheckFailure",
    "CommandOnCooldown",
    "MaxConcurrencyReached",
    "MissingRequiredArgument",
    "BadArgument",
    "BadUnionArgument",
    "BadLiteralArgument",
    "ExpectedClosingQuoteError",
}

#: The schema version written by this module.  Parsers must keep accepting
#: version 0 (and the old plain-text format) so old reports stay readable.
REPORT_VERSION = 1

#: Added to databases created before reports had a review state or an incident.
_REPORT_STATUS_COLUMNS = (
    ("status", f"TEXT NOT NULL DEFAULT '{DEFAULT_REPORT_STATUS}'"),
    ("status_by", "TEXT"),
    ("status_by_name", "TEXT"),
    ("status_at", "TEXT"),
    ("public_notice", "INTEGER NOT NULL DEFAULT 0"),
    ("severity", f"TEXT NOT NULL DEFAULT '{DEFAULT_REPORT_SEVERITY}'"),
    ("incident_events", "TEXT"),
    ("maintenance_kind", "TEXT"),
    ("maintenance_key", "TEXT"),
)

_CODE_ALPHABET = string.ascii_uppercase + string.digits
_REPORT_DB_PATH = "data/error_reports.db"
_LEGACY_REPORT_DIR = Path(__file__).resolve().parents[2] / "data" / "error_reports"
_INIT_LOCK = asyncio.Lock()
_REPORT_CACHE: dict[str, dict] = {}

#: Where a report came from.  Unknown values are displayed as-is.
REPORT_SOURCE_LABELS = {
    "prefix": "Prefix command",
    "slash": "Slash command",
    "event": "Gateway event",
    "website": "Website",
    "api": "API",
    "legacy": "Legacy report",
    "unknown": "Unknown",
}

_LEGACY_SOURCES = {
    "prefix command": "prefix",
    "slash command": "slash",
    "gateway event": "event",
    "website": "website",
    "api": "api",
}


class ErrorReportDatabase:
    """Singleton pool for error reports, isolated like the music database."""

    _instance: "ErrorReportDatabase | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.pool = None
        return cls._instance

    @property
    def is_ready(self) -> bool:
        return self.pool is not None

    async def init(self, bot=None) -> None:
        if self.pool is not None:
            return

        async with _INIT_LOCK:
            if self.pool is not None:
                return

            main = getattr(bot, "cxn", None) if bot is not None else None
            if main is not None and getattr(main, "db_type", None) == "mongodb":
                try:
                    base = os.getenv("MONGODB_DATABASE", "discord_bot")
                    self.pool = named_pool(main, f"{base}_error_reports")
                except Exception as error:
                    logging.warning(
                        "ErrorReports",
                        f"Mongo error-report database failed ({error}); using SQLite.",
                    )
                    self.pool = None

            if self.pool is None:
                connection = await aiosqlite.connect(_REPORT_DB_PATH)
                await connection.execute("PRAGMA journal_mode=WAL")
                await connection.execute("PRAGMA foreign_keys=ON")
                self.pool = SQLitePool(connection)

            await self.pool.execute(
                f"""CREATE TABLE IF NOT EXISTS error_reports (
                    code TEXT PRIMARY KEY,
                    report TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT '{DEFAULT_REPORT_STATUS}',
                    status_by TEXT,
                    status_by_name TEXT,
                    status_at TEXT,
                    public_notice INTEGER NOT NULL DEFAULT 0,
                    severity TEXT NOT NULL DEFAULT '{DEFAULT_REPORT_SEVERITY}',
                    incident_events TEXT,
                    maintenance_kind TEXT,
                    maintenance_key TEXT
                )"""
            )
            await self.ensure_status_columns()
            await self._migrate_legacy_rows()
            await self._import_legacy_reports()
            logging.success(
                "ErrorReports",
                f"Error report database ready ({self.pool.db_type}).",
            )

    async def ensure_status_columns(self) -> None:
        """Add the review columns to a table created before they existed."""
        for column, definition in _REPORT_STATUS_COLUMNS:
            try:
                await self.pool.execute(
                    f"ALTER TABLE error_reports ADD COLUMN {column} {definition}"
                )
            except Exception:
                pass  # The column is already there.

    async def _migrate_legacy_rows(self) -> None:
        """Rewrite plain-text rows from the old version as JSON documents.

        Reading already parses them, so this is a storage migration rather than
        a correctness requirement.  A broken row is left exactly as it was and
        the read path still handles it.
        """
        try:
            rows = await self.pool.fetch(
                "SELECT code, report, created_at FROM error_reports"
            )
        except Exception as error:
            logging.warning("ErrorReports", f"Could not inspect legacy rows: {error}")
            return
        migrated = 0
        for row in rows:
            body = str(row.get("report") or "")
            try:
                parsed = json.loads(body)
                if isinstance(parsed, dict):
                    continue
            except (TypeError, ValueError):
                pass
            try:
                report = normalise_error_report(
                    body,
                    code=str(row.get("code") or ""),
                    created_at=str(row.get("created_at") or ""),
                )
                await self.pool.execute(
                    "UPDATE error_reports SET report = $1 WHERE code = $2",
                    _encode_report(report),
                    str(row.get("code")),
                )
                migrated += 1
            except Exception as error:
                logging.warning(
                    "ErrorReports",
                    f"Could not migrate legacy row {row.get('code')}: {error}",
                )
        if migrated:
            logging.info(
                "ErrorReports", f"Converted {migrated} legacy report(s) to JSON."
            )

    async def _import_legacy_reports(self) -> None:
        """Bring forward reports created by the previous file-backed version."""
        if not _LEGACY_REPORT_DIR.is_dir():
            return
        for path in _LEGACY_REPORT_DIR.glob("*.txt"):
            code = path.stem.upper()
            if len(code) != 6 or any(char not in _CODE_ALPHABET for char in code):
                continue
            try:
                report_text = path.read_text(encoding="utf-8")
                created_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
                report = normalise_error_report(
                    report_text, code=code, created_at=created_at
                )
                await self.pool.execute(
                    "INSERT OR IGNORE INTO error_reports (code, report, created_at) "
                    "VALUES ($1, $2, $3)",
                    code,
                    _encode_report(report),
                    created_at,
                )
            except Exception as error:
                logging.warning("ErrorReports", f"Could not import legacy report {code}: {error}")

    async def ensure(self, bot=None) -> bool:
        if self.pool is None:
            await self.init(bot)
        return self.pool is not None

    async def save(self, report: dict, created_at: str, bot=None) -> tuple[str, dict]:
        """Persist one JSON report and return its code and final document."""
        await self.ensure(bot)
        if self.pool is None:
            raise RuntimeError("Error report database is unavailable")

        while True:
            code = "".join(secrets.choice(_CODE_ALPHABET) for _ in range(6))
            existing = await self.pool.fetchrow(
                "SELECT code FROM error_reports WHERE code = $1", code
            )
            if existing:
                continue
            payload = dict(report)
            payload["version"] = REPORT_VERSION
            payload["code"] = code
            payload["created_at"] = created_at
            body = _encode_report(payload)
            await self.pool.execute(
                "INSERT OR IGNORE INTO error_reports (code, report, created_at, incident_events) "
                "VALUES ($1, $2, $3, $4)",
                code,
                body,
                created_at,
                _encode_events([{
                    "type": "created",
                    "at": created_at,
                    "status": DEFAULT_REPORT_STATUS,
                }]),
            )
            saved = await self.pool.fetchrow(
                "SELECT report FROM error_reports WHERE code = $1", code
            )
            if saved and str(saved["report"]) == body:
                _REPORT_CACHE[code] = payload
                return code, payload

    async def get(self, code: str, bot=None) -> dict | None:
        await self.ensure(bot)
        if self.pool is None:
            return _REPORT_CACHE.get(code)
        row = await self.pool.fetchrow(
            "SELECT report, created_at FROM error_reports WHERE code = $1", code
        )
        if row:
            report = normalise_error_report(
                row["report"],
                code=code,
                created_at=str(row.get("created_at") or ""),
            )
            _REPORT_CACHE[code] = report
            return report
        return _REPORT_CACHE.get(code)

    async def list_reports(self, bot=None, limit: int = 100) -> list[dict]:
        """Return a bounded, newest-first index for the staff dashboard."""
        await self.ensure(bot)
        reports = []
        bounded_limit = max(1, min(int(limit), 100))
        if self.pool is not None:
            rows = await self.pool.fetch(
                "SELECT code, report, created_at, status, status_by, status_by_name, status_at, "
                "public_notice, severity, incident_events, maintenance_kind, maintenance_key "
                f"FROM error_reports ORDER BY created_at DESC LIMIT {bounded_limit}"
            )
            for row in rows:
                reports.append(_report_item(row))
        known_codes = {item["code"] for item in reports}
        for code, report in _REPORT_CACHE.items():
            if code not in known_codes:
                reports.append({
                    "code": code,
                    "report": report,
                    "created_at": str(report.get("created_at") or ""),
                    "summary": report.get("summary") or "",
                    "source": report.get("source") or "unknown",
                    "status": DEFAULT_REPORT_STATUS,
                    "status_by": None,
                    "status_by_name": None,
                    "status_at": None,
                    "public_notice": False,
                    "severity": DEFAULT_REPORT_SEVERITY,
                    "incident_events": [],
                    "maintenance_kind": None,
                    "maintenance_key": None,
                })
        reports.sort(key=lambda item: item["created_at"], reverse=True)
        return reports[:bounded_limit]

    async def set_status(self, code: str, status: str, staff_id=None,
                         staff_name: str | None = None, bot=None) -> dict | None:
        """Move one report to a review state and append it to the timeline."""
        normalized = str(status or "").strip().lower()
        if normalized not in REPORT_STATUSES:
            raise ValueError(f"Unknown report status: {status!r}")
        await self.ensure(bot)
        if self.pool is None:
            return None
        existing = await self.pool.fetchrow(
            "SELECT status, incident_events, created_at FROM error_reports WHERE code = $1", code
        )
        if existing is None:
            return None
        events = _row_events(existing, code=code, created_at=str(existing.get("created_at") or ""))
        previous = str(existing.get("status") or DEFAULT_REPORT_STATUS)
        at = _utcnow()
        if previous != normalized:
            events.append({
                "type": "status",
                "at": at,
                "from": previous,
                "status": normalized,
                "by": str(staff_id) if staff_id is not None else None,
                "by_name": staff_name,
            })
        await self.pool.execute(
            "UPDATE error_reports SET status = $1, status_by = $2, status_by_name = $3, "
            "status_at = $4, incident_events = $5 WHERE code = $6",
            normalized,
            str(staff_id) if staff_id is not None else None,
            staff_name,
            at,
            _encode_events(events),
            code,
        )
        row = await self.pool.fetchrow(
            "SELECT code, status, status_by, status_by_name, status_at "
            "FROM error_reports WHERE code = $1",
            code,
        )
        return {"code": str(row["code"]), **_status_fields(row)}

    async def set_public_incident(self, code: str, public_notice: bool, severity: str,
                                  staff_id=None, staff_name: str | None = None,
                                  bot=None) -> dict | None:
        """Publish or unpublish a report and record it on its timeline."""
        normalized = str(severity or "").strip().lower()
        if normalized not in REPORT_SEVERITIES:
            raise ValueError(f"Unknown report severity: {severity!r}")
        await self.ensure(bot)
        if self.pool is None:
            return None
        existing = await self.pool.fetchrow(
            "SELECT public_notice, severity, incident_events, created_at "
            "FROM error_reports WHERE code = $1", code
        )
        if existing is None:
            return None
        previous = bool(existing.get("public_notice"))
        previous_severity = str(existing.get("severity") or DEFAULT_REPORT_SEVERITY)
        if previous != bool(public_notice):
            events = _row_events(existing, code=code, created_at=str(existing.get("created_at") or ""))
            events.append({
                "type": "public_notice",
                "at": _utcnow(),
                "enabled": bool(public_notice),
                "severity": normalized,
                "by": str(staff_id) if staff_id is not None else None,
                "by_name": staff_name,
            })
            await self.pool.execute(
                "UPDATE error_reports SET public_notice = $1, severity = $2, incident_events = $3 "
                "WHERE code = $4",
                1 if public_notice else 0, normalized, _encode_events(events), code,
            )
        elif previous_severity != normalized:
            events = _row_events(existing, code=code, created_at=str(existing.get("created_at") or ""))
            events.append({
                "type": "severity",
                "at": _utcnow(),
                "severity": normalized,
                "by": str(staff_id) if staff_id is not None else None,
                "by_name": staff_name,
            })
            await self.pool.execute(
                "UPDATE error_reports SET severity = $1, incident_events = $2 WHERE code = $3",
                normalized, _encode_events(events), code,
            )
        return await self.get_item(code, bot)

    async def set_report_maintenance(self, code: str, enabled: bool, kind: str | None,
                                     key: str | None, staff_id=None,
                                     staff_name: str | None = None,
                                     bot=None) -> dict | None:
        """Remember which target a report paused, and append that to its timeline."""
        await self.ensure(bot)
        if self.pool is None:
            return None
        existing = await self.pool.fetchrow(
            "SELECT maintenance_kind, maintenance_key, incident_events, created_at "
            "FROM error_reports WHERE code = $1", code
        )
        if existing is None:
            return None
        events = _row_events(existing, code=code, created_at=str(existing.get("created_at") or ""))
        target_kind = str(kind or "").strip().lower() or None
        target_key = str(key or "").strip() or None
        events.append({
            "type": "maintenance",
            "at": _utcnow(),
            "enabled": bool(enabled),
            "kind": target_kind,
            "key": target_key,
            "by": str(staff_id) if staff_id is not None else None,
            "by_name": staff_name,
        })
        await self.pool.execute(
            "UPDATE error_reports SET maintenance_kind = $1, maintenance_key = $2, "
            "incident_events = $3 WHERE code = $4",
            target_kind if enabled else None,
            target_key if enabled else None,
            _encode_events(events),
            code,
        )
        return await self.get_item(code, bot)

    async def get_item(self, code: str, bot=None) -> dict | None:
        """One report in the same flat shape ``list_reports`` returns."""
        await self.ensure(bot)
        if self.pool is None:
            report = _REPORT_CACHE.get(code)
            return None if report is None else {
                "code": code,
                "report": report,
                "created_at": str(report.get("created_at") or ""),
                "summary": report.get("summary") or "",
                "source": report.get("source") or "unknown",
                "status": DEFAULT_REPORT_STATUS,
                "status_by": None,
                "status_by_name": None,
                "status_at": None,
                "public_notice": False,
                "severity": DEFAULT_REPORT_SEVERITY,
                "incident_events": [],
                "maintenance_kind": None,
                "maintenance_key": None,
            }
        row = await self.pool.fetchrow(
            "SELECT code, report, created_at, status, status_by, status_by_name, status_at, "
            "public_notice, severity, incident_events, maintenance_kind, maintenance_key "
            "FROM error_reports WHERE code = $1", code,
        )
        return None if row is None else _report_item(row)

    async def delete(self, code: str, bot=None) -> bool:
        """Remove a report for good; False when there was nothing to remove."""
        await self.ensure(bot)
        if self.pool is None:
            return False
        existing = await self.pool.fetchrow(
            "SELECT code FROM error_reports WHERE code = $1", code
        )
        if existing is None:
            return False
        await self.pool.execute("DELETE FROM error_reports WHERE code = $1", code)
        _REPORT_CACHE.pop(code, None)
        return True


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _status_fields(row) -> dict:
    """The review columns of a row, with the default for pre-status rows."""
    return {
        "status": str(row.get("status") or DEFAULT_REPORT_STATUS),
        "status_by": row.get("status_by"),
        "status_by_name": row.get("status_by_name"),
        "status_at": row.get("status_at"),
    }


def _incident_fields(row) -> dict:
    return {
        "public_notice": bool(row.get("public_notice")),
        "severity": str(row.get("severity") or DEFAULT_REPORT_SEVERITY),
        # Reports saved before timelines existed still get a created entry, so
        # every report opens with at least the initial state in its history.
        "incident_events": _row_events(
            row,
            code=str(row.get("code") or ""),
            created_at=str(row.get("created_at") or ""),
        ),
        "maintenance_kind": row.get("maintenance_kind") or None,
        "maintenance_key": row.get("maintenance_key") or None,
    }


def _report_item(row) -> dict:
    """Build the flat row the dashboard and owner endpoints exchange."""
    code = str(row["code"])
    created_at = str(row.get("created_at") or "")
    report = normalise_error_report(row.get("report"), code=code, created_at=created_at)
    _REPORT_CACHE[code] = report
    return {
        "code": code,
        "report": report,
        "created_at": created_at or report.get("created_at", ""),
        "summary": report.get("summary") or "",
        "source": report.get("source") or "unknown",
        **_status_fields(row),
        **_incident_fields(row),
    }


def _encode_events(events: list[dict]) -> str:
    return json.dumps(events, ensure_ascii=False, separators=(",", ":"), default=str)


def _decode_events(value) -> list[dict]:
    if isinstance(value, list):
        return [event for event in value if isinstance(event, dict)]
    if not value:
        return []
    try:
        parsed = json.loads(str(value))
    except (TypeError, ValueError):
        return []
    return [event for event in parsed if isinstance(event, dict)] if isinstance(parsed, list) else []


def _row_events(row, *, code: str, created_at: str) -> list[dict]:
    """The stored timeline, with a synthetic first entry for older reports."""
    events = _decode_events(row.get("incident_events"))
    if not events:
        events = [{
            "type": "created",
            "at": created_at or str(row.get("created_at") or ""),
            "status": str(row.get("status") or DEFAULT_REPORT_STATUS),
        }]
    return events


def _public_timeline(events: list[dict], status: str) -> list[dict]:
    """A public-only view of the report timeline."""
    timeline: list[dict] = []
    for event in events:
        kind = str(event.get("type") or "")
        at = str(event.get("at") or "")
        if kind == "created":
            timeline.append({"at": at, "state": "investigating", "label": "Reported"})
        elif kind == "status":
            value = public_incident_state(event.get("status"))
            timeline.append({"at": at, "state": value, "label": PUBLIC_INCIDENT_STATES[value]})
        elif kind == "public_notice":
            timeline.append({
                "at": at,
                "state": "investigating" if event.get("enabled") else "resolved",
                "label": "Published" if event.get("enabled") else "Unpublished",
            })
        elif kind == "maintenance":
            if event.get("enabled"):
                timeline.append({"at": at, "state": "identified", "label": "Maintenance started"})
            else:
                timeline.append({"at": at, "state": public_incident_state(status), "label": "Maintenance ended"})
        elif kind == "severity":
            severity = str(event.get("severity") or "").strip().lower()
            if severity in REPORT_SEVERITIES:
                timeline.append({"at": at, "state": "investigating", "label": f"Severity set to {REPORT_SEVERITIES[severity]}"})
    if not timeline:
        timeline.append({"at": "", "state": public_incident_state(status), "label": public_incident_label(status)})
    return timeline


async def list_error_reports(bot=None, limit: int = 100) -> list[dict]:
    """Return recent error reports for staff tooling."""
    return await _REPORT_DATABASE.list_reports(bot, limit)


async def get_error_report_item(code: str, bot=None) -> dict | None:
    """One full report item for an owner action's response."""
    return await _REPORT_DATABASE.get_item(str(code or "").strip().upper(), bot)


async def list_public_incidents(bot=None, limit: int = 20) -> list[dict]:
    """Reports an owner explicitly published to the public status page.

    Nothing from the traceback or request context leaves this function.  The
    public timeline carries states and times only, never staff names or IDs.
    """
    await _REPORT_DATABASE.ensure(bot)
    pool = _REPORT_DATABASE.pool
    if pool is None:
        return []
    bounded = max(1, min(int(limit), 50))
    try:
        rows = await pool.fetch(
            "SELECT code, report, created_at, status, status_at, severity, incident_events, "
            "maintenance_kind, maintenance_key FROM error_reports "
            f"WHERE public_notice = 1 ORDER BY created_at DESC LIMIT {bounded}"
        )
    except Exception as error:
        logging.warning("ErrorReports", f"Could not read public incidents: {error}")
        return []
    incidents = []
    from utils.maintenance import api_label

    for row in rows:
        code = str(row.get("code") or "")
        created_at = str(row.get("created_at") or "")
        report = normalise_error_report(row.get("report"), code=code, created_at=created_at)
        status = str(row.get("status") or DEFAULT_REPORT_STATUS)
        state = public_incident_state(status)
        events = _row_events(row, code=code, created_at=created_at)
        timeline = _public_timeline(events, status)
        kind = str(row.get("maintenance_kind") or "") or None
        key = str(row.get("maintenance_key") or "") or None
        label = None
        if key:
            label = api_label(key) if kind == "api" else key
        exception = report.get("exception") or {}
        incidents.append({
            "code": code,
            "title": str(exception.get("name") or "Service incident"),
            "summary": str(report.get("summary") or ""),
            "source": str(report.get("source") or "unknown"),
            "severity": str(row.get("severity") or DEFAULT_REPORT_SEVERITY),
            "status": status,
            "state": state,
            "state_label": PUBLIC_INCIDENT_STATES[state],
            "started_at": created_at,
            "updated_at": timeline[-1]["at"] if timeline else str(row.get("status_at") or created_at),
            "maintenance": {"kind": kind, "key": key, "label": label} if kind and key else None,
            "timeline": timeline,
        })
    return incidents


def public_incident_state(status: str | None) -> str:
    """Map the internal review state onto the public incident vocabulary."""
    return _STATUS_TO_PUBLIC.get(str(status or "").strip().lower(), "investigating")


def public_incident_label(status: str | None) -> str:
    return PUBLIC_INCIDENT_STATES[public_incident_state(status)]


async def set_error_report_status(code: str, status: str, staff_id=None,
                                  staff_name: str | None = None, bot=None) -> dict | None:
    """Set the review state of one report; None when the code is unknown."""
    return await _REPORT_DATABASE.set_status(
        str(code or "").strip().upper(), status, staff_id, staff_name, bot
    )


async def set_error_report_maintenance(
    code: str,
    enabled: bool,
    kind: str | None = None,
    key: str | None = None,
    staff_id=None,
    staff_name: str | None = None,
    bot=None,
) -> dict | None:
    """Clear or record the maintenance target linked to one report."""
    return await _REPORT_DATABASE.set_report_maintenance(
        str(code or "").strip().upper(),
        enabled,
        kind,
        key,
        staff_id,
        staff_name,
        bot,
    )


async def set_error_report_incident(
    code: str,
    *,
    public_notice: bool,
    severity: str,
    maintenance_enabled: bool | None,
    maintenance_kind: str | None = None,
    maintenance_key: str | None = None,
    staff_id=None,
    staff_name: str | None = None,
    bot=None,
) -> dict | None:
    """Apply a public-notice change and, optionally, its maintenance link.

    The separate operations are intentional: a report can be published without
    pausing anything, and a pause can be cleared while the incident remains on
    the status page until the owner unpublishes or resolves it.
    """
    normalized = str(code or "").strip().upper()
    item = await _REPORT_DATABASE.set_public_incident(
        normalized, public_notice, severity, staff_id, staff_name, bot
    )
    if item is None:
        return None
    if maintenance_enabled is not None:
        item = await _REPORT_DATABASE.set_report_maintenance(
            normalized,
            maintenance_enabled,
            maintenance_kind,
            maintenance_key,
            staff_id,
            staff_name,
            bot,
        )
    return item


async def delete_error_report(code: str, bot=None) -> bool:
    """Delete one report by code; False when it was already gone."""
    return await _REPORT_DATABASE.delete(str(code or "").strip().upper(), bot)


_REPORT_DATABASE = ErrorReportDatabase()


def _json_safe(value: Any, depth: int = 0) -> Any:
    """Make arbitrary context JSON-serialisable without raising.

    Callers are expected to pass plain data, but an exception while building a
    report must never be replaced by a different exception just because one
    value was not serialisable.
    """
    if depth > 8:
        return repr(value)[:500]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return {str(key)[:120]: _json_safe(item, depth + 1) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_json_safe(item, depth + 1) for item in value]
    return repr(value)[:2000]


def _classify_exception(error: BaseException) -> str:
    """Whether a failure is user error or something maintenance can address.

    Permission and validation failures are saved so support can cite the exact
    request later, but they are not service incidents: putting a command in
    maintenance would punish every other member for one person's mistake.
    """
    seen: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        # A response status is the most reliable signal: an HTTPException with
        # status 500 is still a service failure even though its class name is in
        # the 4xx family's base class.
        status = getattr(current, "status", None)
        if status is None:
            status = getattr(current, "code", None)
        try:
            if 400 <= int(status) < 500:
                return "user_error"
        except (TypeError, ValueError):
            pass
        name = type(current).__name__
        if name in _USER_ERROR_NAMES:
            return "user_error"
        current = getattr(current, "original", None) or current.__cause__
    return "system"


def _classify_type(type_name: str | None) -> str:
    """Classify a legacy report from its stored exception type name."""
    pieces = str(type_name or "").split(".")
    name = pieces[-1] if pieces else ""
    return "user_error" if name in _USER_ERROR_NAMES else "system"


def _exception_document(error: BaseException) -> dict:
    """The exception fields every report carries."""
    error_type = type(error)
    qualified = f"{error_type.__module__}.{error_type.__qualname__}"
    try:
        formatted_traceback = "".join(
            traceback.format_exception(error_type, error, error.__traceback__)
        ).rstrip()
    except Exception:
        formatted_traceback = ""
    try:
        message = str(error)
    except Exception:
        message = "(message unavailable)"
    return {
        "type": qualified,
        "name": error_type.__name__,
        "message": message[:4000],
        "traceback": formatted_traceback,
    }


def _environment(bot=None) -> dict:
    environment = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "implementation": platform.python_implementation(),
    }
    user = getattr(bot, "user", None) if bot is not None else None
    if user is not None:
        environment["bot_user"] = {
            "id": str(getattr(user, "id", "") or ""),
            "name": str(user),
        }
    return environment


def build_error_report(
    error: BaseException,
    *,
    source: str = "unknown",
    context: dict | None = None,
    summary: str | None = None,
    occurred_at: str | None = None,
    bot=None,
) -> dict:
    """Build the JSON document for one failure."""
    occurred_at = occurred_at or _utcnow()
    exception = _exception_document(error)
    if not summary:
        summary = (
            f"{exception['name']}: {exception['message']}"
            if exception.get("message")
            else exception["name"]
        )
    return {
        "version": REPORT_VERSION,
        "code": "pending",
        "created_at": occurred_at,
        "source": str(source or "unknown").strip().lower() or "unknown",
        "classification": _classify_exception(error),
        "summary": str(summary).strip()[:600],
        "exception": exception,
        "context": _json_safe(context or {}),
        "environment": _json_safe(_environment(bot)),
    }


def _legacy_source(value: str | None) -> str:
    return _LEGACY_SOURCES.get(str(value or "").strip().lower(), "legacy")


def _read_label_value(lines: list[str], label: str) -> str:
    """Read ``Label: value`` from legacy text, including a value on the next line."""
    prefix = f"{label}:"
    for index, line in enumerate(lines):
        if not line.startswith(prefix):
            continue
        value = line[len(prefix):].strip()
        if value:
            return value
        for following in lines[index + 1:]:
            if following.strip():
                return following.strip()
        return ""
    return ""


def _parse_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in lines:
        if not line.strip() or set(line.strip()) <= {"-"}:
            continue
        key, separator, value = line.partition(":")
        if not separator:
            continue
        fields[key.strip()] = value.strip()
    return fields


def _parse_legacy_text(
    text: str, *, code: str | None = None, created_at: str | None = None
) -> dict:
    """Turn the old human-readable report into structured fields.

    The old format was deliberately line-based, so parsing it is preferable to
    discarding the context staff relied on.  The original text is also kept in
    ``raw`` so nothing is lost if a line does not match.
    """
    lines = text.splitlines()
    header_lines = lines[:]
    section_indexes: dict[str, int] = {}
    for name in ("Invocation context", "Exception", "Traceback"):
        try:
            section_indexes[name] = next(
                index for index, line in enumerate(lines) if line.strip() == name
            )
        except StopIteration:
            section_indexes[name] = -1

    invocation_index = section_indexes["Invocation context"]
    exception_index = section_indexes["Exception"]
    traceback_index = section_indexes["Traceback"]

    invocation_lines: list[str] = []
    if invocation_index >= 0:
        end = exception_index if exception_index > invocation_index else len(lines)
        invocation_lines = lines[invocation_index + 1:end]

    exception_lines: list[str] = []
    if exception_index >= 0:
        end = traceback_index if traceback_index > exception_index else len(lines)
        exception_lines = lines[exception_index + 1:end]

    traceback_lines: list[str] = []
    if traceback_index >= 0:
        traceback_lines = lines[traceback_index + 1:]
        if traceback_lines and set(traceback_lines[0].strip()) <= {"-"}:
            traceback_lines = traceback_lines[1:]

    fields = _parse_fields(invocation_lines)
    exception_fields = _parse_fields(exception_lines)
    found_code = code or _read_label_value(header_lines, "Error code") or ""
    occurred = created_at or _read_label_value(header_lines, "Occurred (UTC)") or ""
    source = _legacy_source(fields.get("Source"))
    error_type = exception_fields.get("Type") or "Exception"
    name = error_type.rsplit(".", 1)[-1] or "Exception"
    message = exception_fields.get("Message") or ""
    traceback_text = "\n".join(traceback_lines).strip()
    if set(traceback_text) <= {"-"}:
        traceback_text = ""

    context: dict[str, Any] = {
        key.lower().replace(" ", "_").replace("(", "").replace(")", ""): value
        for key, value in fields.items()
    }
    # Keep the old text visible as context too; a report can contain a line the
    # parser did not understand, and staff should still be able to read it.
    raw_details = "\n".join(invocation_lines).strip()
    if raw_details:
        context["legacy_details"] = raw_details
    exception_section = "\n".join(exception_lines).strip()
    if exception_section:
        context["legacy_exception"] = exception_section

    summary = f"{name}: {message}" if message else name
    return {
        "version": 0,
        "code": found_code,
        "created_at": occurred,
        "source": source,
        "summary": summary,
        "classification": _classify_type(error_type),
        "exception": {
            "type": error_type,
            "name": name,
            "message": message,
            "traceback": traceback_text,
        },
        "context": context,
        "environment": {},
        "raw": text,
    }


def normalise_error_report(
    value: Any, *, code: str | None = None, created_at: str | None = None
) -> dict:
    """Return a JSON report document from stored JSON or legacy plain text.

    This function is intentionally forgiving: the dashboard calls it for every
    row, and one old or hand-edited row must not break the whole list.
    """
    if isinstance(value, dict):
        raw = value
    elif isinstance(value, (str, bytes)):
        text = value.decode("utf-8", "replace") if isinstance(value, bytes) else value
        try:
            parsed = json.loads(text)
        except (TypeError, ValueError):
            return _parse_legacy_text(text, code=code, created_at=created_at)
        if not isinstance(parsed, dict):
            return _parse_legacy_text(text, code=code, created_at=created_at)
        raw = parsed
    else:
        return _parse_legacy_text(str(value or ""), code=code, created_at=created_at)

    raw_exception = raw.get("exception")
    if isinstance(raw_exception, dict):
        exception = dict(raw_exception)
    elif raw_exception:
        exception = {"message": str(raw_exception)}
    else:
        exception = {}
    error_type = str(exception.get("type") or "Exception")
    name = str(exception.get("name") or error_type.rsplit(".", 1)[-1] or "Exception")
    message = str(exception.get("message") or "")
    traceback_text = str(exception.get("traceback") or "")
    summary = str(raw.get("summary") or "")
    if not summary:
        summary = f"{name}: {message}" if message else name

    raw_context = raw.get("context")
    if isinstance(raw_context, dict):
        context = raw_context
    elif raw_context:
        context = {"details": raw_context}
    else:
        context = {}

    environment = raw.get("environment")
    if not isinstance(environment, dict):
        environment = {}

    classification = str(raw.get("classification") or "").strip().lower()
    if classification not in {"user_error", "system"}:
        classification = _classify_type(error_type)

    result = {
        "version": int(raw.get("version") or 0) if str(raw.get("version") or "0").isdigit() else 0,
        "code": str(raw.get("code") or code or ""),
        "created_at": str(raw.get("created_at") or created_at or ""),
        "source": str(raw.get("source") or "unknown").strip().lower() or "unknown",
        "classification": classification,
        "summary": summary,
        "exception": {
            "type": error_type,
            "name": name,
            "message": message,
            "traceback": traceback_text,
        },
        "context": _json_safe(context),
        "environment": _json_safe(environment),
    }
    if isinstance(raw.get("raw"), str):
        result["raw"] = raw["raw"]
    return result


def _encode_report(report: dict) -> str:
    return json.dumps(report, ensure_ascii=False, separators=(",", ":"), default=str)


def _source_from_details(details: str) -> str:
    for line in str(details or "").splitlines():
        if line.startswith("Source:"):
            return _legacy_source(line.partition(":")[2])
    return "unknown"


async def save_error_report(
    error: BaseException,
    context: dict | str | None = None,
    bot=None,
    *,
    source: str | None = None,
    summary: str | None = None,
) -> tuple[str, dict]:
    """Build and persist a structured report, returning its code and document.

    ``context`` may still be the old preformatted ``details`` string for any
    caller that has not been migrated; it is wrapped as ``{"details": ...}``
    and its ``Source:`` line determines the report source.
    """
    if isinstance(context, str):
        inferred_source = source or _source_from_details(context)
        context = {"details": context}
    else:
        inferred_source = source or "unknown"
        context = context or {}
    occurred_at = _utcnow()
    report = build_error_report(
        error,
        source=inferred_source,
        context=context,
        summary=summary,
        occurred_at=occurred_at,
        bot=bot,
    )
    try:
        code, saved = await _REPORT_DATABASE.save(report, occurred_at, bot)
        return code, saved
    except Exception as storage_error:
        # A database outage must never hide the original Discord or web error.
        # Keep the report available to staff for this process and log the loss
        # of durable storage so it can be investigated.
        code = "".join(secrets.choice(_CODE_ALPHABET) for _ in range(6))
        report["code"] = code
        report["created_at"] = occurred_at
        _REPORT_CACHE[code] = report
        logging.error("ErrorReports", f"Could not persist report {code}: {storage_error}")
        return code, report


def _valid_code(code: str) -> str | None:
    normalized = code.strip().upper()
    if len(normalized) != 6 or any(char not in _CODE_ALPHABET for char in normalized):
        return None
    return normalized


async def get_error_report(code: str, bot=None) -> dict | None:
    """Retrieve a parsed report by code, case-insensitively."""
    normalized = _valid_code(code)
    if normalized is None:
        return None
    try:
        return await _REPORT_DATABASE.get(normalized, bot)
    except Exception as storage_error:
        logging.warning("ErrorReports", f"Could not retrieve report {normalized}: {storage_error}")
        return _REPORT_CACHE.get(normalized)


def report_source_label(source: str | None) -> str:
    """A human-readable label for a report's ``source`` field."""
    key = str(source or "unknown").strip().lower()
    return REPORT_SOURCE_LABELS.get(key, key.replace("_", " ").title() or "Unknown")
