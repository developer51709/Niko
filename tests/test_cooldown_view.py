"""The gambling cooldowns share one Components V2 notice with live timestamps.

Every gambling command used to answer a blocked attempt with either a plain
string or a pre-rendered "2m 15s" duration that went stale immediately. They now
all render ``utils.cooldown.cooldown_view``, which uses Discord's dynamic
``<t:…:R>`` timestamp so the countdown stays correct for each viewer.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.cooldown import cooldown_ready_at, cooldown_view  # noqa: E402

GAMBLING_SOURCES = (
    "src/cogs/economy/commands/gambling.py",
    "src/cogs/casino/slots.py",
    "src/cogs/casino/blackjack.py",
    "src/cogs/casino/roulette.py",
)

STALE_STRINGS = (
    "You can only play slots once every",
    "You can only play roulette once every",
    "You're on cooldown for blackjack.",
    "Try again in **",
)


def _rendered(view) -> str:
    return repr(view.to_components())


def test_ready_timestamp_is_last_used_plus_cooldown():
    assert cooldown_ready_at(1_000, 60) == 1_060
    assert cooldown_ready_at("1000", 90) == 1_090
    assert cooldown_ready_at(None, 60) == 60


def test_notice_uses_dynamic_timestamps_instead_of_a_fixed_duration():
    view = cooldown_view("spin the slots", 1_760_000_000, title="🎰 Slow down")
    rendered = _rendered(view)
    assert "<t:1760000000:R>" in rendered
    assert "You can spin the slots again" in rendered
    # The notice is a single line: no separate "Ready <date>" footer.
    assert "<t:1760000000:f>" not in rendered
    assert "Ready" not in rendered
    # No pre-rendered countdown should sneak back in.
    assert "seconds." not in rendered.split("<t:1760000000:R>")[1]


def test_notice_is_a_brand_coloured_container_with_a_note():
    view = cooldown_view(
        "play blackjack",
        1_760_000_000,
        title="🃏 Slow down",
        note="Blackjack allows one hand every **60** seconds.",
    )
    container = view.to_components()[0]
    assert container["type"] == 17
    assert container["accent_color"] == 0xC8A882
    assert [child["type"] for child in container["components"]] == [
        10,  # TextDisplay: title
        14,  # Separator
        10,  # TextDisplay: note + timestamps
    ]
    body = container["components"][2]["content"]
    assert body.startswith("Blackjack allows one hand every **60** seconds.")
    assert "You can play blackjack again" in body
    assert body.rstrip().endswith("<t:1760000000:R>.")


def test_every_gambling_command_renders_the_shared_notice():
    for relative in GAMBLING_SOURCES:
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert "cooldown_view(" in source, relative
        for stale in STALE_STRINGS:
            assert stale not in source, f"{relative} still sends {stale!r}"
