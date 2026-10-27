"""Regression checks for the dashboard broadcast studio.

The composer moved out of Discord into the owner-only staff tab, so these
checks pin the promises the web editor relies on:

* the announcement channel opt-in is still persistent and per guild,
* the old ``.broadcast`` command is gone and the website owns composition,
* images travel as real attachments (``attachment://``), never as links,
* delivery is paced and reports progress the dashboard can poll,
* editing a delivered broadcast updates every recorded copy.
"""

import asyncio
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import discord


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import database  # noqa: E402
from utils import broadcast  # noqa: E402


def test_notification_channel_schema_is_persistent_and_per_guild():
    source = (ROOT / "src/events/startup/database.py").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS notification_channels" in source
    assert "guild_id   INTEGER PRIMARY KEY" in source
    assert "channel_id INTEGER NOT NULL" in source


def test_broadcast_schema_keeps_media_targets_and_progress():
    source = (ROOT / "src/events/startup/database.py").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS staff_broadcasts" in source
    assert "CREATE TABLE IF NOT EXISTS staff_broadcast_media" in source
    assert "CREATE TABLE IF NOT EXISTS staff_broadcast_targets" in source
    # Progress the dashboard progress bar polls while the job runs.
    assert "sent_count   INTEGER NOT NULL DEFAULT 0" in source
    assert "target_count INTEGER NOT NULL DEFAULT 0" in source
    assert "edited_count INTEGER NOT NULL DEFAULT 0" in source
    # The base64 payload is what lets every copy upload its own attachment.
    assert "data         TEXT NOT NULL" in source


def test_old_channel_command_is_replaced_by_the_staff_tab():
    owner = (ROOT / "src/cogs/staff/owner.py").read_text(encoding="utf-8")
    staff = (ROOT / "src/cogs/staff/staff.py").read_text(encoding="utf-8")
    init = (ROOT / "src/webapp/__init__.py").read_text(encoding="utf-8")

    assert '@commands.command(name="broadcast"' not in owner
    assert "BroadcastBuilder" not in owner
    assert '"broadcast"' not in staff.split("OWNER_ONLY_COMMANDS = {", 1)[1].split("}", 1)[0]
    assert "staff_broadcast_routes" in init


def test_broadcast_routes_are_owner_only_and_csrf_guarded():
    routes = (ROOT / "src/webapp/routes/staff_broadcast_routes.py").read_text(encoding="utf-8")
    assert '"/api/staff/broadcasts"' in routes
    assert "def _require_owner" in routes
    assert '!= "owner"' in routes
    assert routes.count("@require_csrf") >= 5
    # Uploads are multipart and validated by content, not by the filename.
    assert 'request.files.get("file")' in routes
    assert "_detect_image_type" in routes
    assert "MAX_MEDIA_BYTES" in routes
    assert '"/api/staff/broadcasts/<broadcast_id>/send"' in routes
    assert "schedule_on_bot_loop" in routes


def test_broadcast_row_without_mongo_defaults_still_serialises():
    """A stored draft must load on MongoDB, which has no column defaults.

    The create route writes only the fields it lists, so ``target_count`` and
    the other counters — SQLite column defaults — are absent from the document.
    Reading them positionally failed the whole list request, and the studio
    showed "Broadcasts could not be loaded." instead of the editor.
    """
    from webapp.routes import staff_broadcast_routes as routes

    row = database.Row({
        "broadcast_id": "abc123",
        "title": "Maintenance",
        "body": "Back at 20:00",
        "accent": "C8A882",
        "footer": "Official Niko staff announcement",
        "status": "draft",
        "created_by": 1,
        "created_at": 1700000000.0,
        "updated_at": 1700000000.0,
    })

    payload = routes._serialise(row, [])

    assert payload["id"] == "abc123"
    assert payload["target_count"] == 0
    assert payload["sent_count"] == 0
    assert payload["failed_count"] == 0
    assert payload["skipped_count"] == 0
    assert payload["edited_count"] == 0
    assert payload["last_error"] is None


def test_unsent_broadcast_without_a_counter_column_can_be_sent():
    """A draft read back from MongoDB has no ``sent_count`` to compare."""

    class Pool:
        async def fetchrow(self, query, *args):
            return database.Row({"status": "draft"})

        async def execute(self, query, *args):
            return None

    bot = SimpleNamespace(cxn=Pool())

    assert asyncio.run(broadcast.begin_delivery(bot, "abc123")) is None


def test_delivery_uses_real_file_attachments_and_paced_sends():
    source = (ROOT / "src/utils/broadcast.py").read_text(encoding="utf-8")
    assert "attachment://" in source
    assert "discord.File(io.BytesIO" in source
    assert "SEND_INTERVAL_SECONDS" in source
    assert "await asyncio.sleep(SEND_INTERVAL_SECONDS)" in source
    assert "discord.RateLimited" in source
    # The stored gallery never falls back to a remote URL.
    assert "UnfurledMediaItem(url=_media_url" in source
    assert "MediaGalleryItem" in source


def test_progress_and_edits_are_persisted():
    source = (ROOT / "src/utils/broadcast.py").read_text(encoding="utf-8")
    assert "sent_count = $1" in source
    assert "target_count = $1" in source
    assert "async def sync_broadcast" in source
    # Editing must only touch messages that were actually recorded.
    assert "message_id IS NOT NULL" in source
    assert "await message.edit(" in source
    assert "edited_count" in source


def test_blacklisted_servers_are_skipped_at_snapshot_time():
    source = (ROOT / "src/utils/broadcast.py").read_text(encoding="utf-8")
    assert "def split_targets" in source
    assert "is_blacklisted(guild_id)" in source
    assert "SELECT guild_id, channel_id FROM notification_channels" in source


# ── The document backend needs a primary key for every broadcast table ──
# MongoDB is preferred whenever MONGODB_URL is set. An unmapped table cannot
# resolve an _id, so the very first draft insert failed and the studio only
# showed "The broadcast could not be created."


def test_broadcast_tables_are_registered_with_the_database_adapter():
    assert database.PRIMARY_KEYS["staff_broadcasts"] == "broadcast_id"
    assert database.PRIMARY_KEYS["staff_broadcast_media"] == "media_id"
    assert database.PRIMARY_KEYS["staff_broadcast_targets"] == ("broadcast_id", "guild_id")
    assert database.PRIMARY_KEYS["notification_channels"] == "guild_id"


class _FakeCursor:
    def __init__(self, docs):
        self.docs = list(docs)

    def sort(self, *_args):
        return self

    def skip(self, count):
        self.docs = self.docs[count:]
        return self

    def limit(self, count):
        self.docs = self.docs[:count]
        return self

    async def to_list(self, length=None):
        return list(self.docs)

    def __aiter__(self):
        self._iterator = iter(self.docs)
        return self

    async def __anext__(self):
        try:
            return next(self._iterator)
        except StopIteration:
            raise StopAsyncIteration


class _FakeCollection:
    def __init__(self):
        self.docs = {}

    async def replace_one(self, filter_doc, doc, upsert=True):
        self.docs[filter_doc["_id"]] = doc

    def find(self, filter_dict, projection=None):
        return _FakeCursor(
            doc for doc in self.docs.values()
            if all(doc.get(key) == value for key, value in filter_dict.items())
        )


class _FakeDB:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name):
        return self.collections.setdefault(name, _FakeCollection())


class _FakeClient:
    def __init__(self):
        self.databases = {}

    def __getitem__(self, name):
        return self.databases.setdefault(name, _FakeDB())


def test_a_draft_can_be_created_on_the_document_backend():
    pool = database.MongoPool(_FakeClient(), "niko")
    asyncio.run(pool.execute(
        "INSERT INTO staff_broadcasts (broadcast_id, title, body, accent, footer, "
        "status, created_by, created_at, updated_at) "
        "VALUES ($1, $2, $3, $4, $5, 'draft', $6, $7, $8)",
        "abc123", "", "", "C8A882", "Official Niko staff announcement", 42, 1.0, 1.0,
    ))
    row = asyncio.run(pool.fetchrow(
        "SELECT * FROM staff_broadcasts WHERE broadcast_id = $1", "abc123",
    ))
    assert row is not None
    assert row["broadcast_id"] == "abc123"
    assert row["status"] == "draft"
    assert row["created_by"] == 42


def test_broadcast_media_bytes_are_totaled_on_the_document_backend():
    # The upload route refuses anything over 20 MB, so it sums the stored sizes.
    client = _FakeClient()
    collection = client["niko"]["staff_broadcast_media"]
    collection.docs = {
        "m1": {"_id": "m1", "broadcast_id": "bc1", "size": 3},
        "m2": {"_id": "m2", "broadcast_id": "bc1", "size": 4},
        "m3": {"_id": "m3", "broadcast_id": "bc1", "size": None},
    }
    pool = database.MongoPool(client, "niko")
    total = asyncio.run(pool.fetchval(
        "SELECT COALESCE(SUM(size), 0) FROM staff_broadcast_media "
        "WHERE broadcast_id = $1",
        "bc1",
    ))
    assert total == 7


# ── A stale stored channel id must never fail a broadcast ──


def _not_found():
    return discord.NotFound(SimpleNamespace(status=404, reason="Not Found"), "Unknown Channel")


class _Cxn:
    """Just enough of the pool API for one delivery run."""

    def __init__(self, guilds):
        self.guilds = dict(guilds)
        self.targets = {}
        self.broadcast = {
            "broadcast_id": "bc1", "title": "Title", "body": "Body",
            "footer": "", "accent": "C8A882", "status": "sending",
            "target_count": 0, "sent_count": 0, "failed_count": 0,
            "skipped_count": 0, "edited_count": 0, "last_error": None,
        }

    async def fetchrow(self, query, *args):
        assert "FROM staff_broadcasts" in query, query
        return dict(self.broadcast)

    async def fetch(self, query, *args):
        text = " ".join(query.split())
        if "FROM notification_channels" in text:
            return [
                {"guild_id": guild, "channel_id": channel}
                for guild, channel in self.guilds.items()
            ]
        if "FROM staff_broadcast_media" in text:
            return []
        if "FROM staff_broadcast_targets" in text:
            return [t for t in self.targets.values() if t["status"] == "pending"]
        raise AssertionError(text)

    async def execute(self, query, *args):
        text = " ".join(query.split())
        if text.startswith("DELETE FROM notification_channels"):
            guild_id, channel_id = args
            if self.guilds.get(guild_id) == channel_id:
                self.guilds.pop(guild_id)
            return
        if text.startswith("INSERT OR REPLACE INTO staff_broadcast_targets"):
            _broadcast_id, guild_id, channel_id = args
            self.targets[guild_id] = {
                "guild_id": guild_id, "channel_id": channel_id, "status": "pending",
            }
            return
        if text.startswith("UPDATE staff_broadcast_targets"):
            status, message_id, error, _updated, _broadcast, guild_id = args
            self.targets[guild_id].update(status=status, message_id=message_id, error=error)
            return
        if text.startswith("UPDATE staff_broadcasts"):
            set_clause = text.split(" SET ", 1)[1].split(" WHERE ", 1)[0]
            for assignment in set_clause.split(","):
                column, value = (part.strip() for part in assignment.split("=", 1))
                placeholder = re.search(r"\$(\d+)", value)
                if placeholder:
                    self.broadcast[column] = args[int(placeholder.group(1)) - 1]
                elif value.startswith("'"):
                    self.broadcast[column] = value[1:-1]
                else:
                    self.broadcast[column] = float(value) if "." in value else int(value)
            return
        raise AssertionError(text)


class _Bot:
    def __init__(self, cxn, guild_ids):
        self.cxn = cxn
        self.guild_ids = set(guild_ids)
        self.loop = SimpleNamespace(is_running=lambda: True)

    def is_ready(self):
        return True

    def get_guild(self, guild_id):
        return SimpleNamespace(id=guild_id) if guild_id in self.guild_ids else None

    def get_channel(self, channel_id):
        return None

    async def fetch_channel(self, channel_id):
        raise _not_found()


def test_removed_server_and_deleted_channel_are_skipped_not_failed():
    # Guild 10 removed Niko, guild 20 deleted the announcement channel.
    cxn = _Cxn({10: 100, 20: 200})
    bot = _Bot(cxn, guild_ids=[20])
    interval = broadcast.SEND_INTERVAL_SECONDS
    broadcast.SEND_INTERVAL_SECONDS = 0
    try:
        asyncio.run(broadcast.deliver_broadcast(bot, "bc1"))
    finally:
        broadcast.SEND_INTERVAL_SECONDS = interval

    assert cxn.broadcast["status"] == "sent"
    assert cxn.broadcast["failed_count"] == 0
    assert cxn.broadcast["sent_count"] == 0
    assert cxn.broadcast["skipped_count"] == 2
    # The dead opt-ins are cleared so the next run is clean too.
    assert cxn.guilds == {}


def test_a_permission_error_still_reports_a_failure():
    class _ForbiddenBot(_Bot):
        async def fetch_channel(self, channel_id):
            raise discord.Forbidden(
                SimpleNamespace(status=403, reason="Forbidden"), "Missing Access",
            )

    status, message_id, error = asyncio.run(broadcast._send_copy(
        _ForbiddenBot(_Cxn({}), guild_ids=[20]), 200,
        {"title": "t", "body": "b", "footer": "", "accent": "C8A882"}, [], 20,
    ))
    assert (status, message_id) == ("failed", None)
    assert "could not be reached" in error
