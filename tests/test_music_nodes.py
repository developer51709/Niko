"""Regression checks for resilient Lavalink discovery and rescans."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_hardcoded_lavalink_catalog_is_available():
    source = (ROOT / "src/config/lavalink.py").read_text(encoding="utf-8")
    assert "LAVALINK_NODES" in source
    assert '"host":' in source
    assert '"password":' in source


def test_music_cog_merges_static_candidates_and_rescans_hourly():
    source = (ROOT / "src/cogs/music/cog.py").read_text(encoding="utf-8")
    assert "from config.lavalink import LAVALINK_NODES" in source
    assert "async def _node_rescan_loop" in source
    assert "await asyncio.sleep(0 if first_run else 3600)" in source
    assert "_dedupe_nodes(list(LAVALINK_NODES) + list(discovered or []))" in source
    assert "capacity = max(0, int(_MAX_CONNECT_NODES) - len(connected))" in source


def test_music_connection_has_bounded_voice_and_search_failures():
    source = (ROOT / "src/cogs/music/cog.py").read_text(encoding="utf-8")
    assert "timeout=15" in source
    assert "Lavalink search timed out" in source
    assert "Node top-up failed" in source
