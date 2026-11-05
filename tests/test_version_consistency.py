"""The version the bot reports has to be the version the changelog announces."""

import asyncio
import json
import re
from pathlib import Path
from types import SimpleNamespace

from events.startup import writers
from events.startup.writers import VERSION


ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "web/src/data/changelog.ts"


def _changelog_versions() -> list[str]:
    text = CHANGELOG.read_text(encoding="utf-8")
    return re.findall(r'^\s+version: "([^"]+)",$', text, re.MULTILINE)


def _newest_first(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def test_the_bot_reports_the_newest_changelog_version():
    versions = _changelog_versions()

    assert versions, "the changelog should carry version numbers"
    # Entries are newest first, so the first one is the release this build is
    # part of, and nothing may be numbered above it.
    assert versions[0] == VERSION
    assert VERSION == max(versions, key=_newest_first)


def test_the_dashboard_package_matches_the_changelog():
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))

    assert package["version"] == VERSION
    assert lock["version"] == VERSION
    assert lock["packages"][""]["version"] == VERSION


def test_the_startup_snapshot_writes_the_constant(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    bot = SimpleNamespace(
        guilds=[],
        walk_commands=lambda: [],
        tree=SimpleNamespace(get_commands=lambda: []),
    )

    writers.write_bot_stats(bot)

    written = json.loads((tmp_path / "data/bot_stats.json").read_text(encoding="utf-8"))
    assert written["version"] == VERSION


def test_the_status_panel_reports_the_constant(monkeypatch):
    from cogs.staff.panels import status as panel

    async def database(_bot):
        return "mongodb", True

    async def probe(_url):
        return True

    monkeypatch.setattr(panel, "_check_database", database)
    monkeypatch.setattr(panel, "_probe_http", probe)
    monkeypatch.setattr(panel, "_load_bot_stats_file", lambda: {"version": VERSION})
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

    snapshot = asyncio.run(panel._collect_status(bot))

    assert snapshot["version"] == VERSION


def test_the_panel_footer_drops_the_version_until_the_bot_has_written_one(monkeypatch):
    from cogs.staff.panels import status as panel

    async def database(_bot):
        return "mongodb", True

    async def probe(_url):
        return True

    monkeypatch.setattr(panel, "_check_database", database)
    monkeypatch.setattr(panel, "_probe_http", probe)
    # No snapshot yet, as on a build that has just been updated and not handed
    # over: the footer says nothing rather than printing an invented version.
    monkeypatch.setattr(panel, "_load_bot_stats_file", lambda: {})
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

    snapshot = asyncio.run(panel._collect_status(bot))
    view = panel._build_status_panel(bot, snapshot)
    footer = view.children[-1].children[0].content

    assert snapshot["version"] is None
    assert "Shards 1" in footer
    assert "vNone" not in footer
