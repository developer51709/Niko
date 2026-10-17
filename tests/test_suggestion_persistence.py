"""Regression checks for database-backed suggestion persistence."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_main_database_has_suggestion_config_and_message_tables():
    source = (ROOT / "src/events/startup/database.py").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS suggestion_config" in source
    assert "CREATE TABLE IF NOT EXISTS suggestions" in source
    assert "message_id INTEGER PRIMARY KEY" in source
    assert "channel_id INTEGER NOT NULL" in source


def test_suggestions_load_database_before_registering_views():
    source = (ROOT / "src/cogs/social/suggestions.py").read_text(encoding="utf-8")
    assert "async def cog_load(self)" in source
    assert "await self._load_database()" in source
    assert "await self._register_persistent_views()" in source
    assert "SELECT guild_id, channel_id, next_id FROM suggestion_config" in source
    assert "SELECT * FROM suggestions" in source
    assert "self.bot.add_view(_build_view(suggestion, None), message_id=suggestion[\"message_id\"])" in source


def test_suggestion_changes_write_to_main_database():
    source = (ROOT / "src/cogs/social/suggestions.py").read_text(encoding="utf-8")
    assert "INSERT OR REPLACE INTO suggestion_config" in source
    assert "INSERT OR REPLACE INTO suggestions" in source
    assert "await self._persist_suggestion(gid, s)" in source
