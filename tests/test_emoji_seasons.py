"""Seasonal emoji selection.

The variants are uploaded once under suffixed names. These tests pin the date
windows and prove that ``get_emoji`` switches the lookup without changing a
Discord emoji or rewriting the asset tree.
"""

from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import config.emojis as emoji_config  # noqa: E402
from config.emojis import get_emoji  # noqa: E402
from utils.emoji_seasons import SEASONAL_BASES, active_season, seasonal_variant  # noqa: E402


def test_season_windows_are_inclusive_and_short():
    assert active_season(date(2026, 10, 1)) == "halloween"
    assert active_season(date(2026, 10, 31)) == "halloween"
    assert active_season(date(2026, 11, 2)) == "halloween"
    assert active_season(date(2026, 11, 3)) is None

    assert active_season(date(2026, 12, 1)) == "christmas"
    assert active_season(date(2026, 12, 31)) == "christmas"
    assert active_season(date(2027, 1, 6)) == "christmas"
    assert active_season(date(2027, 1, 7)) is None

    assert active_season(date(2027, 2, 1)) == "valentine"
    assert active_season(date(2027, 2, 15)) == "valentine"
    assert active_season(date(2027, 2, 16)) is None
    assert active_season(date(2027, 7, 4)) is None


def test_general_purpose_emojis_get_a_variant_but_state_icons_do_not():
    assert seasonal_variant("heart", date(2026, 12, 24)) == "heart_christmas"
    assert seasonal_variant("gift", date(2026, 10, 31)) == "gift_halloween"
    assert seasonal_variant("trophy", date(2027, 2, 14)) == "trophy_valentine"
    assert seasonal_variant("arrow_left", date(2026, 12, 24)) == "arrow_left_christmas"
    assert seasonal_variant("bot", date(2027, 2, 14)) == "bot_valentine"
    for name in SEASONAL_BASES:
        assert seasonal_variant(name, date(2026, 7, 4)) is None
    # State colours and per-event log marks keep one meaning all year.
    assert seasonal_variant("tick", date(2026, 12, 24)) is None
    assert seasonal_variant("log_kick", date(2026, 12, 24)) is None


def test_get_emoji_switches_to_the_active_variant(monkeypatch):
    monkeypatch.setattr(
        emoji_config,
        "seasonal_variant",
        lambda name: "heart_christmas" if name == "heart" else None,
    )

    assert get_emoji("heart") == "<:heart_christmas:9100001>"
    # A name that is not seasonal keeps its base id.
    assert get_emoji("tick") == "<:tick:1564762582282280990>"
    # Callers can still ask for a specific variant explicitly.
    assert get_emoji("heart_halloween") == "<:heart_halloween:9100011>"
    assert get_emoji("arrow_left_christmas") == "<:arrow_left_christmas:9100047>"
    assert get_emoji("bot_valentine") == "<:bot_valentine:9100184>"
