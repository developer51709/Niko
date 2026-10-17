import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.onboarding.config import format_hex_color, normalize_hex_color


def test_normalize_hex_color_accepts_hash_and_returns_discord_integer():
    assert normalize_hex_color("#5865F2") == 0x5865F2
    assert normalize_hex_color("5865f2") == 0x5865F2


def test_normalize_hex_color_rejects_invalid_values():
    assert normalize_hex_color("5865F") is None
    assert normalize_hex_color("5865FG") is None
    assert normalize_hex_color(0x5865F2) is None


def test_format_hex_color_round_trips_stored_integer():
    assert format_hex_color(0x5865F2) == "5865F2"
    assert format_hex_color(None) is None
    assert format_hex_color(0x1000000) is None
