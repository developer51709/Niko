"""Dedicated database storage for staff-retrievable command error reports."""

from __future__ import annotations

import os
import secrets
import string
import traceback
from datetime import datetime, timezone
from pathlib import Path
import asyncio

import aiosqlite

from database import MongoPool, SQLitePool
from utils import logging


_CODE_ALPHABET = string.ascii_uppercase + string.digits
_REPORT_DB_PATH = "data/error_reports.db"
_LEGACY_REPORT_DIR = Path(__file__).resolve().parents[2] / "data" / "error_reports"
_INIT_LOCK = asyncio.Lock()
_REPORT_CACHE: dict[str, str] = {}


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
                    client = main.client
                    base = os.getenv("MONGODB_DATABASE", "discord_bot")
                    self.pool = MongoPool(client, f"{base}_error_reports")
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
                """CREATE TABLE IF NOT EXISTS error_reports (
                    code TEXT PRIMARY KEY,
                    report TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )"""
            )
            await self._import_legacy_reports()
            logging.success(
                "ErrorReports",
                f"Error report database ready ({self.pool.db_type}).",
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
                report = path.read_text(encoding="utf-8")
                created_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
                await self.pool.execute(
                    "INSERT OR IGNORE INTO error_reports (code, report, created_at) "
                    "VALUES ($1, $2, $3)",
                    code,
                    report,
                    created_at,
                )
            except Exception as error:
                logging.warning("ErrorReports", f"Could not import legacy report {code}: {error}")

    async def ensure(self, bot=None) -> bool:
        if self.pool is None:
            await self.init(bot)
        return self.pool is not None

    async def save(self, report: str, created_at: str, bot=None) -> str:
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
            body = report.replace("Error code: pending", f"Error code: {code}")
            await self.pool.execute(
                "INSERT OR IGNORE INTO error_reports (code, report, created_at) "
                "VALUES ($1, $2, $3)",
                code,
                body,
                created_at,
            )
            saved = await self.pool.fetchrow(
                "SELECT report FROM error_reports WHERE code = $1", code
            )
            if saved and str(saved["report"]) == body:
                _REPORT_CACHE[code] = body
                return code

    async def get(self, code: str, bot=None) -> str | None:
        await self.ensure(bot)
        if self.pool is None:
            return _REPORT_CACHE.get(code)
        row = await self.pool.fetchrow(
            "SELECT report FROM error_reports WHERE code = $1", code
        )
        if row:
            report = str(row["report"])
            _REPORT_CACHE[code] = report
            return report
        return _REPORT_CACHE.get(code)


_REPORT_DATABASE = ErrorReportDatabase()


def _format_report(error: BaseException, details: str, occurred_at: str) -> str:
    formatted_traceback = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    ).rstrip()
    return (
        "Niko Bot Error Report\n"
        "=====================\n"
        "Error code: pending\n"
        f"Occurred (UTC): {occurred_at}\n\n"
        f"{details.rstrip()}\n\n"
        "Exception\n"
        "---------\n"
        f"Type: {type(error).__module__}.{type(error).__qualname__}\n"
        f"Message: {error}\n\n"
        "Traceback\n"
        "---------\n"
        f"{formatted_traceback or '(traceback unavailable)'}\n"
    )


async def save_error_report(
    error: BaseException, details: str, bot=None
) -> tuple[str, str]:
    """Format and persist a report, returning its code and full contents."""
    occurred_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    report = _format_report(error, details, occurred_at)
    try:
        code = await _REPORT_DATABASE.save(report, occurred_at, bot)
        report = report.replace("Error code: pending", f"Error code: {code}")
        return code, report
    except Exception as storage_error:
        # A database outage must never hide the original Discord error. Keep
        # the report available to staff for this process and log the loss of
        # durable storage so it can be investigated.
        code = "".join(secrets.choice(_CODE_ALPHABET) for _ in range(6))
        report = report.replace("Error code: pending", f"Error code: {code}")
        _REPORT_CACHE[code] = report
        logging.error("ErrorReports", f"Could not persist report {code}: {storage_error}")
        return code, report


def _valid_code(code: str) -> str | None:
    normalized = code.strip().upper()
    if len(normalized) != 6 or any(char not in _CODE_ALPHABET for char in normalized):
        return None
    return normalized


async def get_error_report(code: str, bot=None) -> str | None:
    """Retrieve a report by code, case-insensitively."""
    normalized = _valid_code(code)
    if normalized is None:
        return None
    try:
        return await _REPORT_DATABASE.get(normalized, bot)
    except Exception as storage_error:
        logging.warning("ErrorReports", f"Could not retrieve report {normalized}: {storage_error}")
        return _REPORT_CACHE.get(normalized)
