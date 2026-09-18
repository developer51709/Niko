"""Regression checks for official broadcast configuration and CV2 delivery."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_notification_channel_schema_is_persistent_and_per_guild():
    source = (ROOT / "src/events/startup/database.py").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS notification_channels" in source
    assert "guild_id   INTEGER PRIMARY KEY" in source
    assert "channel_id INTEGER NOT NULL" in source


def test_public_setup_and_owner_broadcast_are_wired():
    notifier = (ROOT / "src/cogs/notifier/cog.py").read_text(encoding="utf-8")
    owner = (ROOT / "src/cogs/admin/owner.py").read_text(encoding="utf-8")

    assert '@commands.hybrid_command(name="notification-channel")' in notifier
    assert "INSERT OR REPLACE INTO notification_channels" in notifier
    assert '@commands.command(name="broadcast")' in owner
    assert "MediaGalleryItem" in owner
    assert "BroadcastEditModal" in owner
    assert "SELECT guild_id, channel_id FROM notification_channels" in owner
