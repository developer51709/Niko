"""Append-only console logs shared by the supervisor and its children.

The owner's live-log page used to read a ring buffer inside the process that
happened to render it, so every restart started an empty console and the
supervisor's own lines were never visible.  This module keeps the same rendered
lines on disk instead.

The archive is split twice, so one process can never push another's lines out
of the buffer and a burst at DEBUG cannot push the ERROR lines away either:

    data/run/logs/<process>/<LEVEL>.jsonl

Each leaf is an independent :class:`LogStore`: its own file, lock, byte cursor,
rotation and backups.  :class:`LogArchive` writes a record to its process and
level file, and reads a view back by merging the requested leaf files.

Only the standard library is used.  The supervisor imports this module, so it
must stay importable without Discord, Flask, or the application's log setup.

Cursors are byte offsets per leaf file, which is what makes ``next`` survive a
restart: line ids do not reset when a process is replaced.  When a file is
rotated (or replaced by a fresh deployment) the offset no longer exists, so a
reader whose cursor is past the end is told to reset.  A page's cursor is a
composite string (one offset per leaf) because one view can span several files.
"""

from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import os
import re
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Iterable

#: A single rendered line longer than this is cut; the store must not let one
#: traceback with a huge payload grow the file without bound.
MAX_LINE_CHARS = 8192


def _default_token(path: Path) -> str:
    """A stable id for this store, kept beside it and created once."""
    token_path = path.with_name(path.name + ".token")
    try:
        existing = token_path.read_text(encoding="utf-8").strip()
        if existing:
            return existing
    except OSError:
        pass
    token = uuid.uuid4().hex
    try:
        token_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = token_path.with_name(token_path.name + ".tmp")
        temporary.write_text(token, encoding="utf-8")
        os.replace(temporary, token_path)
    except OSError:
        pass
    return token


class LogStore:
    """One rotated JSONL console stream.

    ``append`` is safe from several processes: the file is opened ``O_APPEND``
    and a tiny lock (an adjacent ``.lock`` file) serializes the write with a
    rotation check.  Writes are one ``os.write`` of a complete line, so a reader
    never sees half a record.
    """

    def __init__(
        self,
        path: str | os.PathLike[str],
        max_bytes: int = 5 * 1024 * 1024,
        backups: int = 3,
    ) -> None:
        self.path = Path(path)
        self.max_bytes = max(64 * 1024, int(max_bytes))
        self.backups = max(1, int(backups))
        self.token = _default_token(self.path)
        self._lock = threading.Lock()
        self._fd: int | None = None
        self._lock_fd: int | None = None
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    # ── Writing ───────────────────────────────────────────────────────────

    def append(
        self,
        *,
        level: str,
        logger: str,
        line: str,
        process: str = "bot",
        source: str = "main",
        at: float | None = None,
    ) -> None:
        if not isinstance(line, str) or not line:
            return
        if len(line) > MAX_LINE_CHARS:
            line = line[:MAX_LINE_CHARS] + "…[truncated]"
        entry = {
            "at": time.time() if at is None else float(at),
            "level": str(level or "INFO").upper(),
            "logger": str(logger or ""),
            "process": str(process or "bot"),
            "source": str(source or "main"),
            "line": line,
        }
        data = (
            json.dumps(entry, separators=(",", ":"), sort_keys=True) + "\n"
        ).encode("utf-8", errors="replace")

        with self._lock:
            lock_fd = self._open_lock()
            if lock_fd is None:
                return
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX)
                try:
                    fd = self._open_data()
                    if fd is None:
                        return
                    os.write(fd, data)
                    if os.fstat(fd).st_size >= self.max_bytes:
                        self._rotate_locked()
                finally:
                    with contextlib.suppress(OSError):
                        fcntl.flock(lock_fd, fcntl.LOCK_UN)
            except OSError:
                self._close_data()

    def _open_lock(self) -> int | None:
        if self._lock_fd is not None:
            return self._lock_fd
        try:
            self._lock_fd = os.open(
                self.path.with_name(self.path.name + ".lock"),
                os.O_CREAT | os.O_RDWR,
                0o600,
            )
            return self._lock_fd
        except OSError:
            return None

    def _open_data(self) -> int | None:
        if self._fd is not None:
            return self._fd
        try:
            self._fd = os.open(
                self.path,
                os.O_WRONLY | os.O_CREAT | os.O_APPEND,
                0o600,
            )
            return self._fd
        except OSError:
            return None

    def _close_data(self) -> None:
        if self._fd is not None:
            with contextlib.suppress(OSError):
                os.close(self._fd)
        self._fd = None

    def _close_locked(self) -> None:
        self._close_data()
        if self._lock_fd is not None:
            with contextlib.suppress(OSError):
                os.close(self._lock_fd)
        self._lock_fd = None

    def _rotate_locked(self) -> None:
        """Rename the data file while holding the cross-process lock."""
        self._close_data()
        for index in range(self.backups, 0, -1):
            source = (
                self.path
                if index == 1
                else self.path.with_name(f"{self.path.name}.{index - 1}")
            )
            target = self.path.with_name(f"{self.path.name}.{index}")
            if source.exists():
                with contextlib.suppress(OSError):
                    os.replace(source, target)

    # ── Reading ───────────────────────────────────────────────────────────

    def snapshot(self, since: int = 0, limit: int = 2000) -> dict[str, Any]:
        """Return records after the byte offset ``since``.

        The response shape matches the in-memory buffer's so the owner page does
        not need to know which one answered.  ``id`` is the record's byte
        offset, ``next`` is the offset to send back, and ``head`` is the current
        end of the file.
        """
        try:
            since = max(0, int(since))
        except (TypeError, ValueError):
            since = 0
        limit = max(1, min(int(limit), 5000))

        try:
            size = self.path.stat().st_size
        except OSError:
            return {
                "lines": [],
                "head": 0,
                "next": 0,
                "first": None,
                "token": self.token,
                "capacity": 0,
                "noise_capacity": 0,
                "truncated": False,
                "reset": since > 0,
            }

        reset = since > size
        start = 0 if reset else since
        if start == 0:
            # A first poll should not wait for a 5 MB file to scroll: read the
            # tail window and let the page keep the newest rows.
            start = max(0, size - 512 * 1024)
            while start > 0 and self._byte_at(start - 1) != b"\n":
                start -= 1
                if size - start > 512 * 1024:
                    # A single record larger than the window: start after it.
                    start = self._next_newline(start)
                    break

        entries: list[dict[str, Any]] = []
        first_offset: int | None = None
        stream = None
        try:
            stream = self.path.open("rb")
            stream.seek(start)
            offset = start
            while len(entries) < limit:
                raw = stream.readline()
                if not raw:
                    break
                line_start = offset
                offset += len(raw)
                if not raw.strip():
                    continue
                if first_offset is None:
                    first_offset = line_start
                try:
                    entry = json.loads(raw.decode("utf-8", errors="replace"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                if not isinstance(entry, dict):
                    continue
                entry["id"] = line_start
                # Where the next read starts after this record.  The archive
                # needs it to advance only the streams it actually returned.
                entry["_end"] = offset
                entries.append(entry)
            next_offset = offset if entries else start
        except OSError:
            return {
                "lines": [],
                "head": size,
                "next": since,
                "first": None,
                "token": self.token,
                "capacity": 0,
                "noise_capacity": 0,
                "truncated": False,
                "reset": reset,
            }
        finally:
            if stream is not None:
                stream.close()

        return {
            "lines": entries,
            "head": size,
            "next": next_offset,
            "first": first_offset,
            "token": self.token,
            "capacity": 0,
            "noise_capacity": 0,
            "truncated": reset,
            "reset": reset,
        }

    def _byte_at(self, offset: int) -> bytes:
        try:
            with self.path.open("rb") as stream:
                stream.seek(offset)
                return stream.read(1)
        except OSError:
            return b""

    def _next_newline(self, offset: int) -> int:
        try:
            with self.path.open("rb") as stream:
                stream.seek(offset)
                remainder = stream.read(64 * 1024)
        except OSError:
            return offset
        newline = remainder.find(b"\n")
        return offset + newline + 1 if newline >= 0 else offset + len(remainder)

    def close(self) -> None:
        with self._lock:
            self._close_locked()


#: The levels the archive is asked for, in increasing severity.  A level a
#: library adds for itself (``SUCCESS`` is the bot's) is not in this list; its
#: file is still read whenever the requested threshold is at or below INFO.
LEVEL_WEIGHTS = {
    "DEBUG": 10,
    "INFO": 20,
    "SUCCESS": 25,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}
DEFAULT_LEVEL_WEIGHT = LEVEL_WEIGHTS["INFO"]
_LEVEL_ALIASES = {"WARN": "WARNING", "FATAL": "CRITICAL", "EXCEPTION": "ERROR"}
# Nothing outside these alphabets may reach a path: both names come from a
# log record, and the archive is written by several processes.
_PROCESS_JUNK = re.compile(r"[^a-z0-9_-]+")
_LEVEL_JUNK = re.compile(r"[^A-Z0-9_]+")


def level_weight(level: str | None) -> int:
    """How severe ``level`` is, for choosing which level files a view reads."""
    name = str(level or "").strip().upper()
    return LEVEL_WEIGHTS.get(_LEVEL_ALIASES.get(name, name), DEFAULT_LEVEL_WEIGHT)


def _process_dir_name(process: str | None) -> str:
    name = _PROCESS_JUNK.sub("-", str(process or "bot").strip().lower()).strip("-")
    return name or "bot"


def _level_name(level: str | None) -> str:
    name = str(level or "INFO").strip().upper()
    name = _LEVEL_ALIASES.get(name, name)
    name = _LEVEL_JUNK.sub("_", name).strip("_")
    return name or "INFO"


def _encode_cursor(token: str, offsets: dict[str, int]) -> str:
    body = ";".join(f"{key}={int(offsets[key])}" for key in sorted(offsets))
    return f"v1|{token}|{body}"


def _decode_cursor(raw: str, token: str) -> tuple[dict[str, int], bool]:
    """Offsets from a page's cursor, and whether it belongs to another archive."""
    raw = raw.strip() if isinstance(raw, str) else ""
    if not raw:
        return {}, False
    if raw.isdigit():
        # A page loaded before the archive sent one byte offset, which cannot
        # name a leaf file.  Only its reset is honoured, so a long-open tab
        # starts over once instead of polling `reset` forever.
        return {}, raw != "0"
    parts = raw.split("|")
    if len(parts) != 3 or parts[0] != "v1" or parts[1] != token:
        return {}, True
    offsets: dict[str, int] = {}
    for item in parts[2].split(";"):
        if not item:
            continue
        key, separator, value = item.rpartition("=")
        if not separator or not key:
            return {}, True
        try:
            offsets[key] = max(0, int(value))
        except ValueError:
            return {}, True
    return offsets, False


class LogArchive:
    """Per-process, per-level console files with independent buffers.

    ``append`` picks the file from the record's process and level; a write to
    ``bot`` at ``ERROR`` can only ever rotate ``bot/ERROR.jsonl``.  ``snapshot``
    merges the requested process/level files into one chronological batch and
    returns a composite cursor, so the owner page can ask for a single process
    or a minimum level without downloading the rest.
    """

    def __init__(
        self,
        root: str | os.PathLike[str],
        max_bytes: int = 5 * 1024 * 1024,
        backups: int = 3,
    ) -> None:
        self.root = Path(root)
        self.max_bytes = max(64 * 1024, int(max_bytes))
        self.backups = max(1, int(backups))
        # Stable for the life of this directory: a page cursor that names a
        # different archive is stale even if its byte offsets happen to fit.
        self.token = hashlib.sha256(
            str(self.root.resolve()).encode("utf-8", "replace")
        ).hexdigest()[:16]
        self._streams: dict[tuple[str, str], LogStore] = {}
        self._lock = threading.Lock()
        with contextlib.suppress(OSError):
            self.root.mkdir(parents=True, exist_ok=True, mode=0o700)

    # ── Writing ───────────────────────────────────────────────────────────

    def append(
        self,
        *,
        level: str,
        logger: str,
        line: str,
        process: str = "bot",
        source: str = "main",
        at: float | None = None,
    ) -> None:
        name = _level_name(level)
        self._stream(process, name).append(
            level=name,
            logger=logger,
            line=line,
            process=_process_dir_name(process),
            source=source,
            at=at,
        )

    def _stream(self, process: str, level: str) -> LogStore:
        key = (_process_dir_name(process), _level_name(level))
        with self._lock:
            store = self._streams.get(key)
            if store is None:
                store = LogStore(
                    self.root / key[0] / f"{key[1]}.jsonl",
                    max_bytes=self.max_bytes,
                    backups=self.backups,
                )
                self._streams[key] = store
            return store

    # ── Reading ───────────────────────────────────────────────────────────

    def processes(self) -> list[str]:
        """Processes that have written at least one level file."""
        try:
            names = [
                entry.name
                for entry in self.root.iterdir()
                if entry.is_dir() and not entry.name.startswith(".")
            ]
        except OSError:
            return []
        return sorted(names)

    def _selected(
        self, processes: str | Iterable[str], min_level: str
    ) -> list[tuple[str, LogStore]]:
        threshold = level_weight(min_level)
        if isinstance(processes, str):
            wanted = [processes]
        else:
            wanted = list(processes)
        names = [
            _process_dir_name(name)
            for name in wanted
            if str(name or "").strip() and str(name).strip().lower() != "all"
        ]
        if not names:
            names = self.processes()

        selected: list[tuple[str, LogStore]] = []
        seen: set[str] = set()
        for name in names:
            if name in seen:
                continue
            seen.add(name)
            directory = self.root / name
            if not directory.is_dir():
                continue
            try:
                paths = sorted(directory.glob("*.jsonl"))
            except OSError:
                continue
            for path in paths:
                level = path.name[: -len(".jsonl")]
                if not level or level_weight(level) < threshold:
                    continue
                selected.append((f"{name}/{level}", self._stream(name, level)))
        return selected

    def snapshot(
        self,
        *,
        processes: str | Iterable[str] = "all",
        min_level: str = "DEBUG",
        since: str = "",
        limit: int = 2000,
    ) -> dict[str, Any]:
        """Merge the selected level files, newest last, after ``since``.

        ``since`` is the composite cursor from the previous response (an empty
        string on the first poll).  ``next`` and ``head`` are the same kind of
        string, so a page never has to know which files the view spans.
        """
        try:
            limit = max(1, min(int(limit), 5000))
        except (TypeError, ValueError):
            limit = 2000

        streams = self._selected(processes, min_level)
        keys = {key for key, _ in streams}
        offsets, reset = _decode_cursor(since, self.token)
        # A filter change drops the offsets of buffers the page no longer sees;
        # keeping them would leave the cursor carrying unknown streams.
        offsets = {key: value for key, value in offsets.items() if key in keys}
        next_offsets = dict(offsets)
        heads: dict[str, int] = {}
        collected: list[tuple[float, str, int, dict[str, Any]]] = []

        for key, store in streams:
            snapshot = store.snapshot(offsets.get(key, 0), limit)
            heads[key] = int(snapshot.get("head") or 0)
            if snapshot.get("reset"):
                reset = True
            for entry in snapshot.get("lines", []):
                end = int(entry.pop("_end", 0) or 0)
                offset = int(entry.get("id") or 0)
                entry["id"] = f"{key}:{offset}"
                entry.setdefault("process", key.split("/", 1)[0])
                collected.append((float(entry.get("at") or 0), key, end, entry))

        collected.sort(key=lambda item: (item[0], item[1], item[2]))
        chosen = collected[:limit]
        for _, key, end, _ in chosen:
            next_offsets[key] = end

        has_more = any(
            next_offsets.get(key, 0) < head for key, head in heads.items()
        )
        return {
            "lines": [entry for _, _, _, entry in chosen],
            "head": _encode_cursor(self.token, heads),
            "next": _encode_cursor(self.token, next_offsets),
            "first": None,
            "token": self.token,
            "capacity": 0,
            "noise_capacity": 0,
            "truncated": bool(reset),
            "reset": bool(reset),
            "has_more": has_more,
        }

    def close(self) -> None:
        with self._lock:
            streams = list(self._streams.values())
            self._streams.clear()
        for store in streams:
            store.close()


def store_from_environment() -> LogArchive | None:
    """The log archive directory this process was told about, if any."""
    path = (os.environ.get("NIKO_LOG_STORE") or "").strip()
    if not path:
        return None
    try:
        max_bytes = int(os.environ.get("NIKO_LOG_STORE_BYTES") or 5 * 1024 * 1024)
    except ValueError:
        max_bytes = 5 * 1024 * 1024
    try:
        backups = int(os.environ.get("NIKO_LOG_STORE_BACKUPS") or 3)
    except ValueError:
        backups = 3
    try:
        return LogArchive(path, max_bytes=max_bytes, backups=backups)
    except OSError:
        return None
