"""Regression checks for the persistent status panel health checks."""

import asyncio
from pathlib import Path
from types import SimpleNamespace

from cogs.staff.panels import status as owner


ROOT = Path(__file__).resolve().parents[1]


def test_status_collection_reads_live_music_node_state():
    source = (ROOT / "src/cogs/staff/panels/status.py").read_text(encoding="utf-8")
    assert 'bot.get_cog("MusicSystem")' in source
    assert 'status["music_nodes"] = len(node_labels)' in source
    assert 'status["music_ok"]' in source


def test_system_health_renders_active_music_node_count():
    source = (ROOT / "src/cogs/staff/panels/status.py").read_text(encoding="utf-8")
    assert 'music_nodes = int(status.get("music_nodes") or 0)' in source
    assert 'line(f"{state_emoji(music_ok)} **Music** — {state_of(music_ok)} · {music_nodes} active node' in source
    assert "music_nodes != 1" in source


def test_public_website_health_uses_configured_public_url():
    source = (ROOT / "src/cogs/staff/panels/status.py").read_text(encoding="utf-8")
    assert 'os.environ.get("PUBLIC_URL", "").strip().rstrip("/")' in source
    assert 'await _probe_http(f"{public_url}/")' in source
    assert 'await _probe_http(f"{local_base}/")' not in source
    assert 'status["website_ok"] = False' in source
    assert 'status["website_note"] = "PUBLIC_URL not configured"' in source


def test_website_health_is_independent_of_local_api_health():
    source = (ROOT / "src/cogs/staff/panels/status.py").read_text(encoding="utf-8")
    assert 'status["api_ok"] = await _probe_http(f"{local_base}/api/health")' in source
    assert 'if api_ok:' not in source
    assert "**Website** — {website_text}" in source


def test_status_collection_probes_public_domain_even_if_local_api_is_down(monkeypatch):
    calls = []

    async def probe(url):
        calls.append(url)
        return url == "https://public.example/"

    async def database(_bot):
        return "mongodb", True

    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("PUBLIC_URL", "https://public.example")
    monkeypatch.setattr(owner, "_probe_http", probe)
    monkeypatch.setattr(owner, "_check_database", database)
    monkeypatch.setattr(owner, "_load_bot_stats_file", lambda: {})
    bot = SimpleNamespace(
        guilds=[],
        shard_count=1,
        tree=SimpleNamespace(get_commands=lambda **_kwargs: []),
        commands=[],
        is_closed=lambda: False,
        is_ready=lambda: True,
        latencies=[],
        latency=None,
        get_cog=lambda _name: None,
    )

    status = asyncio.run(owner._collect_status(bot))

    assert calls == [
        "http://127.0.0.1:9000/api/health",
        "https://public.example/",
    ]
    assert status["api_ok"] is False
    assert status["website_ok"] is True


def test_status_collection_reports_missing_public_url_as_down(monkeypatch):
    calls = []

    async def probe(url):
        calls.append(url)
        return True

    async def database(_bot):
        return "mongodb", True

    monkeypatch.delenv("PUBLIC_URL", raising=False)
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setattr(owner, "_probe_http", probe)
    monkeypatch.setattr(owner, "_check_database", database)
    monkeypatch.setattr(owner, "_load_bot_stats_file", lambda: {})
    bot = SimpleNamespace(
        guilds=[],
        shard_count=1,
        tree=SimpleNamespace(get_commands=lambda **_kwargs: []),
        commands=[],
        is_closed=lambda: False,
        is_ready=lambda: True,
        latencies=[],
        latency=None,
        get_cog=lambda _name: None,
    )

    status = asyncio.run(owner._collect_status(bot))

    assert calls == ["http://127.0.0.1:9000/api/health"]
    assert status["website_ok"] is False
    assert status["website_note"] == "PUBLIC_URL not configured"
