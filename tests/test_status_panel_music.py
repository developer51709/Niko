"""Regression checks for music health in the persistent status panel."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_status_collection_reads_live_music_node_state():
    source = (ROOT / "src/cogs/staff/owner.py").read_text(encoding="utf-8")
    assert 'bot.get_cog("MusicSystem")' in source
    assert 'status["music_nodes"] = len(node_labels)' in source
    assert 'status["music_ok"]' in source


def test_system_health_renders_active_music_node_count():
    source = (ROOT / "src/cogs/staff/owner.py").read_text(encoding="utf-8")
    assert 'music_nodes = int(status.get("music_nodes") or 0)' in source
    assert 'line(f"{state_emoji(music_ok)} **Music** — {state_of(music_ok)} · {music_nodes} active node' in source
    assert "music_nodes != 1" in source
