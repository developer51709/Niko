"""Collaborative playlists: guild-scoped, owner-backed editor lists."""

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.music.database import MusicDatabase, _TABLE_SQL  # noqa: E402

GUILD_ID = 1234
OWNER_ID = 11
EDITOR_ID = 22
STRANGER_ID = 33


def _track(title, uri):
    return SimpleNamespace(
        title=title, author="artist", uri=uri, artwork="",
        length=120_000, source="youtube", id=uri,
    )


class SharedPlaylistKeyTests(unittest.TestCase):
    def test_the_mongo_backend_has_primary_keys_for_collaborative_tables(self):
        """Without these, MongoDB rejects every collaborative-playlist insert."""
        from database import PRIMARY_KEYS

        self.assertEqual(PRIMARY_KEYS["music_shared_playlists"], "playlist_id")
        self.assertEqual(
            PRIMARY_KEYS["music_shared_playlist_tracks"],
            ("playlist_id", "track_key"),
        )
        self.assertEqual(
            PRIMARY_KEYS["music_shared_playlist_editors"],
            ("playlist_id", "user_id"),
        )


class SharedPlaylistTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import aiosqlite
        from database import SQLitePool

        self.db = MusicDatabase()
        self._previous = (self.db.pool, self.db._ready)
        self.conn = await aiosqlite.connect(":memory:")
        self.db.pool = SQLitePool(self.conn)
        self.db._ready = True
        for sql in _TABLE_SQL:
            await self.db.pool.execute(sql)

    async def asyncTearDown(self):
        await self.conn.close()
        self.db.pool, self.db._ready = self._previous

    async def test_a_playlist_is_unique_per_name_not_case(self):
        created = await self.db.create_shared_playlist(GUILD_ID, "Chill", OWNER_ID)
        self.assertIsNotNone(created)
        duplicate = await self.db.create_shared_playlist(GUILD_ID, "chill", OWNER_ID)
        self.assertIsNone(duplicate)

    async def test_the_owner_starts_as_an_editor_and_others_do_not(self):
        playlist = await self.db.create_shared_playlist(GUILD_ID, "Chill", OWNER_ID)
        playlist_id = playlist["playlist_id"]

        self.assertTrue(await self.db.is_playlist_editor(playlist_id, OWNER_ID))
        self.assertFalse(await self.db.is_playlist_editor(playlist_id, STRANGER_ID))

        await self.db.add_playlist_editor(playlist_id, EDITOR_ID)
        self.assertTrue(await self.db.is_playlist_editor(playlist_id, EDITOR_ID))

    async def test_tracks_keep_their_order_and_do_not_repeat(self):
        playlist = await self.db.create_shared_playlist(GUILD_ID, "Chill", OWNER_ID)
        playlist_id = playlist["playlist_id"]
        first = _track("First", "https://example.test/1")
        second = _track("Second", "https://example.test/2")

        self.assertTrue(await self.db.add_shared_track(playlist_id, first, OWNER_ID))
        self.assertTrue(await self.db.add_shared_track(playlist_id, second, EDITOR_ID))
        self.assertFalse(await self.db.add_shared_track(playlist_id, first, STRANGER_ID))

        rows = await self.db.shared_tracks(playlist_id)
        self.assertEqual([row["title"] for row in rows], ["First", "Second"])
        self.assertEqual([row["added_by"] for row in rows], [OWNER_ID, EDITOR_ID])

    async def test_removing_a_track_reports_whether_it_was_there(self):
        playlist = await self.db.create_shared_playlist(GUILD_ID, "Chill", OWNER_ID)
        playlist_id = playlist["playlist_id"]
        track = _track("First", "https://example.test/1")
        await self.db.add_shared_track(playlist_id, track, OWNER_ID)
        key = (await self.db.shared_tracks(playlist_id))[0]["track_key"]

        self.assertTrue(await self.db.remove_shared_track(playlist_id, key))
        self.assertFalse(await self.db.remove_shared_track(playlist_id, key))
        self.assertEqual(await self.db.shared_tracks(playlist_id), [])

    async def test_deleting_a_playlist_forgets_its_tracks_and_editors(self):
        playlist = await self.db.create_shared_playlist(GUILD_ID, "Chill", OWNER_ID)
        playlist_id = playlist["playlist_id"]
        await self.db.add_shared_track(playlist_id, _track("First", "https://example.test/1"), OWNER_ID)
        await self.db.add_playlist_editor(playlist_id, EDITOR_ID)

        await self.db.delete_shared_playlist(playlist_id)

        self.assertIsNone(await self.db.shared_playlist(GUILD_ID, "Chill"))
        self.assertEqual(await self.db.shared_tracks(playlist_id), [])
        self.assertFalse(await self.db.is_playlist_editor(playlist_id, EDITOR_ID))

    async def test_the_list_reports_its_track_count(self):
        playlist = await self.db.create_shared_playlist(GUILD_ID, "Chill", OWNER_ID)
        await self.db.add_shared_track(
            playlist["playlist_id"], _track("First", "https://example.test/1"), OWNER_ID,
        )

        rows = await self.db.shared_playlists(GUILD_ID)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "Chill")
        self.assertEqual(int(rows[0]["track_count"]), 1)


if __name__ == "__main__":
    unittest.main()
