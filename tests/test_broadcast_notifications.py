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
    owner = (ROOT / "src/cogs/staff/owner.py").read_text(encoding="utf-8")

    assert '@commands.hybrid_command(name="notification-channel")' in notifier
    assert "INSERT OR REPLACE INTO notification_channels" in notifier
    assert '@commands.command(name="broadcast",' in owner
    staff = (ROOT / "src/cogs/staff/staff.py").read_text(encoding="utf-8")
    assert "self.staff.add_command(command)" in staff
    assert '"broadcast"' in staff.split("OWNER_ONLY_COMMANDS = {", 1)[1].split("}", 1)[0]
    assert "MediaGalleryItem" in owner
    assert "BroadcastEditModal" in owner
    assert "SELECT guild_id, channel_id FROM notification_channels" in owner
