"""Zip-bomb screening for untrusted archives.

Any archive that arrives from a user — a link, an attachment, a forwarded
file — must pass :func:`scan_zip` *before* a member is opened.  The scan reads
the archive's central directory only: names, declared sizes and compressed
sizes.  A bomb is rejected while it is still a few kilobytes of metadata, so no
decompression ever runs on untrusted data.

Declared sizes are attacker-controlled, so a passing scan is not a licence to
trust ``ZipInfo.file_size`` while extracting.  Keep the streaming byte cap on
the write side as well (see ``_extract_zip_images`` in ``cogs/admin/emoji.py``).

Usage::

    from utils.archive_safety import scan_zip

    report = scan_zip(payload)
    if not report.ok:
        ...  # report.code is a machine-readable reason, report.detail is for logs
"""

from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass

#: Suffixes treated as an archive inside an archive.  Nesting is the classic
#: bomb shape (``42.zip``), so archives are refused inside archives by default.
ARCHIVE_SUFFIXES = (
    ".zip",
    ".zipx",
    ".7z",
    ".rar",
    ".tar",
    ".gz",
    ".tgz",
    ".bz2",
    ".xz",
    ".zst",
    ".jar",
)

#: The zip local-file flag marking an encrypted member.
_ENCRYPTED_FLAG = 0x1


@dataclass(frozen=True)
class ZipLimits:
    """Thresholds a single archive has to stay under."""

    #: Most members one archive may hold.
    max_entries: int = 500
    #: Most bytes the archive may declare once every member is unpacked.
    max_total_bytes: int = 64 * 1024 * 1024
    #: Most bytes one member may declare.
    max_entry_bytes: int = 32 * 1024 * 1024
    #: Most expansion (unpacked ÷ packed) a member may claim.
    max_compression_ratio: float = 120.0
    #: Members below this size skip the ratio check, so a tiny text file that
    #: happens to compress 1000× cannot fail an otherwise harmless archive.
    ratio_floor_bytes: int = 1024 * 1024
    #: Archives allowed inside the archive (nested bombs are the common trick).
    max_nested_archives: int = 0


DEFAULT_LIMITS = ZipLimits()


@dataclass(frozen=True)
class ZipScanReport:
    """Outcome of :func:`scan_zip`.

    ``code`` is empty for a safe archive.  Otherwise it is one of
    ``invalid``, ``encrypted``, ``too_many_entries``, ``entry_too_large``,
    ``too_large``, ``compression_ratio`` or ``nested_archive``, and ``detail``
    explains the refusal for the log.
    """

    entries: int = 0
    total_bytes: int = 0
    compressed_bytes: int = 0
    code: str = ""
    detail: str = ""

    @property
    def ok(self) -> bool:
        return not self.code

    def __bool__(self) -> bool:  # ``if scan_zip(...):`` reads naturally
        return self.ok


def scan_zip(data: bytes, limits: ZipLimits = DEFAULT_LIMITS) -> ZipScanReport:
    """Screen *data* for archive bombs without unpacking any member.

    Only the central directory is parsed, so the cost is proportional to the
    compressed payload.  Returns a :class:`ZipScanReport`; check ``.ok``.
    """
    if not data:
        return ZipScanReport(code="invalid", detail="empty payload")

    payload = data if isinstance(data, bytes) else bytes(data)
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            infos = archive.infolist()
    except (zipfile.BadZipFile, zipfile.LargeZipFile, EOFError, OSError, ValueError) as exc:
        return ZipScanReport(code="invalid", detail=f"{type(exc).__name__}: {exc}")

    entries = len(infos)
    if entries > limits.max_entries:
        return ZipScanReport(
            entries=entries,
            code="too_many_entries",
            detail=f"{entries} members exceeds the {limits.max_entries} limit",
        )

    total = 0
    compressed_total = 0
    nested = 0
    for info in infos:
        size = int(info.file_size)
        packed = int(info.compress_size)
        total += size
        compressed_total += packed

        if info.flag_bits & _ENCRYPTED_FLAG:
            return ZipScanReport(entries=entries, code="encrypted", detail=f"{info.filename!r} is encrypted")

        if size > limits.max_entry_bytes:
            return ZipScanReport(
                entries=entries,
                code="entry_too_large",
                detail=f"{info.filename!r} declares {size} bytes",
            )

        if total > limits.max_total_bytes:
            return ZipScanReport(
                entries=entries,
                code="too_large",
                detail=f"declares more than {limits.max_total_bytes} bytes unpacked",
            )

        if size >= limits.ratio_floor_bytes:
            ratio = size / packed if packed else float("inf")
            if ratio > limits.max_compression_ratio:
                shown = "infinite" if packed == 0 else f"{ratio:.0f}x"
                return ZipScanReport(
                    entries=entries,
                    code="compression_ratio",
                    detail=f"{info.filename!r} expands {shown}",
                )

        if info.filename.lower().endswith(ARCHIVE_SUFFIXES):
            nested += 1
            if nested > limits.max_nested_archives:
                return ZipScanReport(
                    entries=entries,
                    code="nested_archive",
                    detail=f"{info.filename!r} is an archive inside the archive",
                )

    return ZipScanReport(entries=entries, total_bytes=total, compressed_bytes=compressed_total)
