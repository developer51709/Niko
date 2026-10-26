"""Archives from users are screened for zip bombs before a member is opened.

``utils.archive_safety.scan_zip`` reads only the central directory, so the
emoji stealer can refuse a bomb while it is still harmless metadata.
"""

import io
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.archive_safety import DEFAULT_LIMITS, ZipLimits, scan_zip  # noqa: E402


def _zip(entries: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as archive:
        for name, payload in entries.items():
            archive.writestr(name, payload)
    return buffer.getvalue()


def _deflated_zip(name: str, payload: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(name, payload)
    return buffer.getvalue()


def test_a_normal_archive_passes():
    report = scan_zip(_zip({"a.png": b"png-a", "nested/b.gif": b"gif-b"}))

    assert report.ok
    assert bool(report) is True
    assert report.entries == 2
    assert report.total_bytes == 10
    assert report.code == ""


def test_garbage_is_rejected_as_invalid():
    assert scan_zip(b"definitely not a zip").code == "invalid"
    assert scan_zip(b"").code == "invalid"


def test_a_bomb_is_rejected_by_compression_ratio():
    limits = ZipLimits(ratio_floor_bytes=64 * 1024)
    report = scan_zip(_deflated_zip("bomb.bin", b"\0" * (1024 * 1024)), limits)

    assert report.code == "compression_ratio"
    assert "expands" in report.detail


def test_a_bomb_is_rejected_by_expanded_size():
    # Two incompressible 800-byte members stay under the ratio floor, so only
    # the declared total unpacked size can catch them.
    limits = ZipLimits(max_total_bytes=1000)
    report = scan_zip(_zip({"a.bin": os.urandom(800), "b.bin": os.urandom(800)}), limits)

    assert report.code == "too_large"


def test_an_oversized_member_is_rejected():
    report = scan_zip(_zip({"big.png": b"x" * 200}), ZipLimits(max_entry_bytes=100))

    assert report.code == "entry_too_large"


def test_too_many_members_are_rejected():
    entries = {f"{index}.png": b"x" for index in range(4)}

    assert scan_zip(_zip(entries), ZipLimits(max_entries=3)).code == "too_many_entries"


def test_an_archive_inside_an_archive_is_rejected():
    nested = _zip({"inner.png": b"x"})
    report = scan_zip(_zip({"pack.zip": nested, "a.png": b"x"}))

    assert report.code == "nested_archive"


def test_scanning_never_opens_a_member(monkeypatch):
    payload = _zip({"a.png": b"x"})

    def _fail(*_args, **_kwargs):
        raise AssertionError("scan_zip decompressed a member")

    monkeypatch.setattr(zipfile.ZipFile, "open", _fail)

    assert scan_zip(payload).ok


def test_limits_are_conservative_by_default():
    assert DEFAULT_LIMITS.max_nested_archives == 0
    assert DEFAULT_LIMITS.max_compression_ratio < 1000


def test_the_emoji_stealer_screens_before_extracting():
    source = (ROOT / "src/cogs/admin/emoji.py").read_text(encoding="utf-8")

    assert "report = await asyncio.to_thread(scan_zip, data)" in source
    assert source.index("to_thread(scan_zip, data)") < source.index(
        "to_thread(_extract_zip_images, data, target_dir)"
    )
    assert "ZIP_SCAN_REASONS.get(report.code" in source
