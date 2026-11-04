"""Private Lavalink nodes: database storage, catalogue priority, owner API.

The pool no longer reads a public node list from the web. It is built from the
committed catalogue plus the private nodes the owner saves from the dashboard,
which live in the music database because their passwords must never be
committed.
"""

import asyncio
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.music import cog as music_cog  # noqa: E402
from utils.music import nodes as nodes_mod  # noqa: E402
from utils.music.database import MusicDatabase, _TABLE_SQL  # noqa: E402

NODES_SOURCE = (ROOT / "src/utils/music/nodes.py").read_text(encoding="utf-8")


def _private(**overrides):
    node = {
        "host": "lavalink.example.com",
        "port": 2333,
        "password": "private-secret",
        "secure": True,
        "version": "v4",
    }
    node.update(overrides)
    return node


class NodeCatalogTests(unittest.TestCase):
    def test_private_nodes_lead_the_catalogue(self):
        catalog = nodes_mod.node_catalog([_private()])

        self.assertEqual(catalog[0]["host"], "lavalink.example.com")
        self.assertTrue(catalog[0]["private"])
        self.assertTrue(all(not node.get("private") for node in catalog[1:]))

    def test_a_private_node_replaces_a_stale_public_entry(self):
        public = next(
            node for node in nodes_mod.node_catalog()
            if node["host"] == "lavalinkv4.serenetia.com" and node["port"] == 80
        )
        catalog = nodes_mod.node_catalog([
            _private(host=public["host"], port=public["port"], secure=False,
                     password="owner-password"),
        ])

        matches = [
            node for node in catalog
            if node["host"] == public["host"] and node["port"] == public["port"]
        ]
        self.assertEqual(len(matches), 1, "host:port must appear once")
        self.assertEqual(matches[0]["password"], "owner-password")
        self.assertTrue(matches[0]["private"])

    def test_nodelink_hosts_stay_out(self):
        catalog = nodes_mod.node_catalog([
            _private(host="nodelink.triniumhost.com", port=443),
        ])

        self.assertNotIn("nodelink.triniumhost.com", {node["host"] for node in catalog})

    def test_no_public_node_list_is_fetched(self):
        self.assertNotIn("raw.githubusercontent.com", NODES_SOURCE)
        self.assertNotIn("DarrenOfficial", NODES_SOURCE)
        self.assertNotIn("_parse_dn_markdown", NODES_SOURCE)


class PrivatePreferenceTests(unittest.IsolatedAsyncioTestCase):
    """Private nodes lead the pool even when a public node probes faster."""

    async def test_private_nodes_are_ordered_first(self):
        public = _private(host="public.example.com", password="public")
        private = _private(host="mine.example.com", private=True)
        latencies = {"public.example.com": 20.0, "mine.example.com": 300.0}

        async def fake_probe(session, node, sem):
            return (node, latencies[node["host"]])

        with mock.patch.object(nodes_mod, "_probe_node", fake_probe), \
                mock.patch.object(nodes_mod.aiohttp, "ClientSession"):
            ordered = await nodes_mod.find_responsive_nodes([public, private])

        self.assertEqual([node["host"] for node in ordered],
                         ["mine.example.com", "public.example.com"])

    async def test_the_private_twin_survives_host_dedupe(self):
        # The same physical host offered twice: the owner's entry is the one
        # kept, so their password is the one the pool connects with.
        public = _private(host="twin.example.com", port=443, password="public")
        private = _private(host="twin.example.com", port=80, secure=False, private=True)
        latencies = {"443": 10.0, "80": 220.0}

        async def fake_probe(session, node, sem):
            return (node, latencies[str(node["port"])])

        with mock.patch.object(nodes_mod, "_probe_node", fake_probe), \
                mock.patch.object(nodes_mod.aiohttp, "ClientSession"):
            ordered = await nodes_mod.find_responsive_nodes([public, private])

        self.assertEqual(len(ordered), 1)
        self.assertEqual(ordered[0]["port"], 80)
        self.assertTrue(ordered[0]["private"])


class PrivateNodeDatabaseTests(unittest.IsolatedAsyncioTestCase):
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

    async def test_a_saved_node_is_readable_and_the_password_is_kept(self):
        identifier = await self.db.save_lavalink_node(
            host="lavalink.example.com", port=2333, password="private-secret",
            secure=True, label="Home", added_by=42,
        )

        self.assertEqual(identifier, "lavalink.example.com:2333")
        rows = await self.db.lavalink_nodes()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["password"], "private-secret")
        self.assertTrue(rows[0]["secure"])
        self.assertEqual(rows[0]["label"], "Home")
        self.assertEqual(rows[0]["added_by"], 42)
        self.assertEqual(rows[0]["version"], "v4")

    async def test_saving_the_same_node_updates_it_instead_of_duplicating(self):
        for password in ("first", "second"):
            await self.db.save_lavalink_node(
                host="lavalink.example.com", port=2333, password=password,
            )

        rows = await self.db.lavalink_nodes()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["password"], "second")

    async def test_removing_a_node_only_drops_that_row(self):
        await self.db.save_lavalink_node(host="one.example.com", port=2333, password="a")
        await self.db.save_lavalink_node(host="two.example.com", port=2333, password="b")

        self.assertTrue(await self.db.remove_lavalink_node("one.example.com:2333"))
        remaining = await self.db.lavalink_nodes()
        self.assertEqual([row["host"] for row in remaining], ["two.example.com"])
        self.assertFalse(await self.db.remove_lavalink_node("one.example.com:2333"))

    async def test_the_table_is_part_of_the_music_schema(self):
        self.assertIn("music_lavalink_nodes", " ".join(_TABLE_SQL))


class OutdatedPoolNodeTests(unittest.TestCase):
    """A rescan must drop removed nodes and pick up a corrected password."""

    def test_a_removed_node_is_outdated(self):
        node = mock.Mock(identifier="gone.example.com:2333", password="x")
        self.assertTrue(music_cog._node_outdated(node, None))

    def test_a_changed_password_is_outdated(self):
        node = mock.Mock(identifier="mine.example.com:2333", password="old")
        entry = {"password": "new"}
        self.assertTrue(music_cog._node_outdated(node, entry))

    def test_a_matching_node_is_left_alone(self):
        node = mock.Mock(identifier="mine.example.com:2333", password="same")
        self.assertFalse(music_cog._node_outdated(node, {"password": "same"}))

    def test_an_unknown_pool_password_never_triggers_a_reconnect(self):
        # Nodes restored by a resumed session can report an empty password;
        # treating that as a change would disconnect players on every rescan.
        node = mock.Mock(identifier="mine.example.com:2333", password="")
        self.assertFalse(music_cog._node_outdated(node, {"password": "new"}))


class DashboardNodeApiTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        from webapp.routes import lavalink_routes

        self.routes = lavalink_routes

    def test_valid_nodes_are_accepted(self):
        host, port, password, secure, label = self.routes._parse_node({
            "host": " Lavalink.Example.com ", "port": "2333",
            "password": "secret", "secure": False, "label": " Home ",
        })

        self.assertEqual((host, port, secure, label),
                         ("lavalink.example.com", 2333, False, "Home"))
        self.assertEqual(password, "secret")

    def test_bad_nodes_are_rejected_with_a_reason(self):
        cases = [
            ({"host": "https://lavalink.example.com", "port": 1, "password": "x"}, "hostname"),
            ({"host": "", "port": 1, "password": "x"}, "hostname"),
            ({"host": "lavalink.example.com", "port": "abc", "password": "x"}, "port"),
            ({"host": "lavalink.example.com", "port": 70000, "password": "x"}, "port"),
            ({"host": "lavalink.example.com", "port": 2333, "password": ""}, "password"),
            ({"host": "lavalink.example.com", "port": 2333, "password": "bad\nvalue"}, "password"),
        ]
        for body, hint in cases:
            with self.subTest(body=body):
                with self.assertRaises(ValueError) as caught:
                    self.routes._parse_node(body)
                self.assertIn(hint, str(caught.exception).lower())

    async def test_pool_rows_merge_catalogue_and_live_status(self):
        class FakeDb:
            async def ensure(self, bot=None):
                return True

            async def lavalink_nodes(self):
                return [_private(host="mine.example.com", label="Home")]

        class FakeCog:
            def pool_snapshot(self):
                return {
                    "nodes": [
                        {"identifier": "mine.example.com:2333", "status": "connected",
                         "players": 2, "heartbeat": 41.5, "session": True},
                        {"identifier": "leftover.example.com:2333", "status": "disconnected",
                         "players": 0, "heartbeat": 0, "session": False},
                    ],
                    "connected": 1, "target": 3,
                }

        with mock.patch("utils.music.database.MusicDatabase", FakeDb), \
                mock.patch.object(self.routes, "_discord_bot", mock.Mock()), \
                mock.patch.object(self.routes, "_music_cog", lambda: FakeCog()):
            snapshot = await self.routes._load()

        rows = {row["identifier"]: row for row in snapshot["nodes"]}
        private_row = rows["mine.example.com:2333"]
        self.assertEqual(private_row["source"], "private")
        self.assertEqual(private_row["status"], "connected")
        self.assertEqual(private_row["players"], 2)
        self.assertEqual(private_row["label"], "Home")
        self.assertEqual(rows["leftover.example.com:2333"]["source"], "orphan")
        self.assertEqual(snapshot["private_count"], 1)
        # Every private node adds a slot on top of the public pool.
        self.assertEqual(snapshot["target"], 3 + 1)
        self.assertNotIn("password", private_row)


class StatusPoolPrivacyTests(unittest.TestCase):
    """The public /status page can show the pool, but never a private host."""

    def _pool(self, nodes, connected=2):
        from webapp import status

        class FakeCog:
            def pool_snapshot(self):
                return {"nodes": nodes, "connected": connected, "target": 3}

        class FakeBot:
            def get_cog(self, name):
                return FakeCog() if name == "MusicSystem" else None

        return status._lavalink_pool(FakeBot())

    def test_private_nodes_are_published_as_aliases_only(self):
        pool = self._pool([
            {"identifier": "lavalink.jirayu.net:443", "private": False,
             "status": "connected", "players": 1, "heartbeat": 30.0},
            {"identifier": "mine.example.com:2333", "private": True, "label": "Home box",
             "status": "connected", "players": 2, "heartbeat": 41.5},
            {"identifier": "backup.example.com:80", "private": True,
             "label": "backup.example.com",
             "status": "disconnected", "players": 0, "heartbeat": 0},
        ])

        blob = json.dumps(pool)
        # Neither the host, the port, nor a label an owner typed leaks out.
        for leaked in ("mine.example.com", "backup.example.com", "Home box", "2333"):
            self.assertNotIn(leaked, blob)

        rows = {row["id"]: row for row in pool["nodes"]}
        # Aliases are numbered by identifier, so they do not move between polls.
        self.assertEqual(rows["private-1"]["status"], "disconnected")
        self.assertEqual(rows["private-2"]["players"], 2)
        self.assertTrue(rows["private-1"]["private"])
        # A committed node is already public, so the page can name it.
        self.assertIn("lavalink.jirayu.net:443", rows)
        self.assertFalse(rows["lavalink.jirayu.net:443"]["private"])
        self.assertEqual(pool["connected"], 2)
        self.assertEqual(pool["pool"], 3)
        self.assertEqual(pool["private"], 2)

    def test_a_private_node_stays_private_after_it_leaves_the_database(self):
        # A deleted node is still connected until the rescan closes it. The
        # remembered set is a union, so the site cannot start naming its host in
        # that window — or after a failed database read.
        cog = object.__new__(music_cog.MusicSystem)
        cog.bot = mock.Mock()
        cog._private_nodes = {}

        class SavedDb:
            async def ensure(self, bot=None):
                return True

            async def lavalink_nodes(self):
                return [_private()]

        class EmptyDb:
            async def ensure(self, bot=None):
                return True

            async def lavalink_nodes(self):
                return []

        with mock.patch.object(music_cog, "MusicDatabase", SavedDb):
            asyncio.run(cog._node_catalog())
        self.assertIn("lavalink.example.com:2333", cog._private_nodes)

        with mock.patch.object(music_cog, "MusicDatabase", EmptyDb):
            asyncio.run(cog._node_catalog())
        self.assertIn("lavalink.example.com:2333", cog._private_nodes)

    def test_a_missing_music_system_reports_no_pool(self):
        from webapp import status

        class BareBot:
            def get_cog(self, name):
                return None

        self.assertIsNone(status._lavalink_pool(BareBot()))


if __name__ == "__main__":
    unittest.main()
