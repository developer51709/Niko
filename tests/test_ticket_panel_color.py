"""The ticket panel's configured color is an accent bar, not panel text.

Reported bug: updating the ticket panel from the dashboard put the accent color's
hex code into the panel title instead of colouring the panel. The stored value is
a `0xRRGGBB` integer, so the panel has to hand it to the components-v2 container
as `accent_colour` — a `#RRGGBB` string is never text a member should read.
"""

import asyncio
import re
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

import discord

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.tickets import views as ticket_views  # noqa: E402
from utils.tickets import utils as ticket_utils  # noqa: E402
from utils.tickets.config import TicketConfig  # noqa: E402
from webapp import app  # noqa: E402
from webapp import dashboard_routes  # noqa: E402
from webapp import server  # noqa: E402

BLURPLE = 0x5865F2
HEX_CODE = re.compile(r"#[0-9A-Fa-f]{6}")


def _panel_text(view) -> str:
    """Every text string the panel renders, across its containers."""
    parts = []
    for container in view.children:
        for child in getattr(container, "children", []):
            content = getattr(child, "content", None)
            if isinstance(content, str):
                parts.append(content)
    return "\n".join(parts)


def _config(**overrides) -> TicketConfig:
    values = {
        "guild_id": 111,
        "panel_title": "Open a Ticket",
        "panel_description": "Select a category to get help.",
        "panel_color": BLURPLE,
    }
    values.update(overrides)
    return TicketConfig(**values)


class TicketPanelColorTests(unittest.TestCase):
    def test_the_stored_color_becomes_the_container_accent(self):
        view = ticket_views.TicketPanelView(111, _config())
        container = view.children[0]
        self.assertIsInstance(container, discord.ui.Container)
        self.assertEqual(container.accent_colour.value, BLURPLE)

    def test_the_hex_code_is_not_written_into_the_panel_text(self):
        view = ticket_views.TicketPanelView(111, _config())
        text = _panel_text(view)
        self.assertIn("Open a Ticket", text)
        self.assertIn("Select a category to get help.", text)
        self.assertNotIn("5865F2", text.upper())
        self.assertIsNone(HEX_CODE.search(text))

    def test_a_panel_without_a_color_gets_no_accent_and_no_text(self):
        view = ticket_views.TicketPanelView(111, _config(panel_color=None))
        self.assertIsNone(view.children[0].accent_colour)
        self.assertIsNone(HEX_CODE.search(_panel_text(view)))

    def test_an_out_of_range_or_unparsable_color_never_reaches_the_panel(self):
        for value in (0x1000000, -1, "not-a-color", ""):
            with self.subTest(color=value):
                self.assertIsNone(ticket_views.panel_accent_colour(value))
                view = ticket_views.TicketPanelView(111, _config(panel_color=value))
                self.assertIsNone(view.children[0].accent_colour)
                self.assertNotIn("NOT-A-COLOR", _panel_text(view).upper())

    def test_a_hex_string_from_an_older_row_still_colors_the_panel(self):
        """A config row written before the dashboard's int conversion."""
        for value in ("#5865F2", "5865f2"):
            with self.subTest(color=value):
                self.assertEqual(
                    ticket_views.panel_accent_colour(value),
                    discord.Colour(BLURPLE),
                )


class TicketPanelColorRouteTests(unittest.TestCase):
    """The dashboard save is where the reported bug entered.

    POST /api/guild/<id>/config/server is what the website calls with the hex
    string from the color picker; the saved 0xRRGGBB integer is what the panel
    view then has to render as an accent bar.
    """

    def setUp(self):
        self._saved_configs = dict(ticket_utils._ticket_configs)
        ticket_utils._ticket_configs.clear()
        self._patches = [
            mock.patch.object(dashboard_routes, "_guild_resource_ids", lambda guild_id: ({"5"}, {"9"})),
            mock.patch.object(dashboard_routes, "_get_runtime_server_config", lambda guild_id: {}),
            mock.patch.object(
                dashboard_routes,
                "_load_blacklist_manager",
                lambda: mock.Mock(get_guild_entry=lambda guild_id: None),
            ),
            mock.patch.object(dashboard_routes, "run_on_bot_loop", self._no_bot_loop),
            mock.patch.object(server, "run_on_bot_loop", self._no_bot_loop),
        ]
        for patch in self._patches:
            patch.start()
            self.addCleanup(patch.stop)

    def tearDown(self):
        ticket_utils._ticket_configs.clear()
        ticket_utils._ticket_configs.update(self._saved_configs)

    @staticmethod
    def _no_bot_loop(awaitable, timeout=8):
        """Stand in for the bot loop: the panel refresh is asserted separately."""
        if hasattr(awaitable, "close"):
            awaitable.close()
        return None

    def _client(self):
        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": "42", "username": "Tester"}
            session["access_token"] = "token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "csrf"
            session["managed_guild_ids"] = ["111"]
            session["managed_guilds_at"] = time.time()
        return client

    def _post_color(self, value):
        return self._client().post(
            "/api/guild/111/config/server",
            json={"tickets": {"panel_color": value}},
            headers={"X-CSRF-Token": "csrf"},
        )

    def test_a_picker_hex_value_is_stored_as_an_int_and_not_kept_as_text(self):
        response = self._post_color("#5865f2")
        self.assertEqual(response.status_code, 200)
        saved = ticket_utils.get_ticket_config(111)
        self.assertEqual(saved.panel_color, BLURPLE)
        view = ticket_views.TicketPanelView(111, saved)
        self.assertEqual(view.children[0].accent_colour.value, BLURPLE)
        self.assertIsNone(HEX_CODE.search(_panel_text(view)))

    def test_the_saved_color_survives_the_website_round_trip(self):
        """Read back what the Tickets tab and the panel would see."""
        self._post_color("#c8a882")
        response = self._client().get("/api/guild/111/tickets")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.get_json()["config"]["panel_color"]), 0xC8A882)
        view = ticket_views.TicketPanelView(111, ticket_utils.get_ticket_config(111))
        self.assertEqual(view.children[0].accent_colour.value, 0xC8A882)

    def test_the_dashboard_refresh_edits_the_panel_with_the_accent(self):
        """The website's save schedule ends in this exact edit call."""
        edited = {}

        class _Message:
            async def edit(self, *, view):
                edited["view"] = view

        class _Channel:
            async def fetch_message(self, message_id):
                return _Message()

        class _Guild:
            def get_channel(self, channel_id):
                return _Channel()

        bot = mock.Mock(get_guild=lambda guild_id: _Guild(), standby_failover=None)
        # The same handoff the bot process performs on startup, so every route
        # module sees this bot exactly as it would in production.
        server.configure_bot(bot)
        self.addCleanup(server.configure_bot, None)
        ticket_utils._ticket_configs[111] = TicketConfig(
            guild_id=111, panel_title="Open a Ticket", panel_channel_id=5, panel_message_id=6
        )

        with mock.patch.object(dashboard_routes, "run_on_bot_loop", self._run_now):
            response = self._client().post(
                "/api/guild/111/config/server",
                json={"tickets": {"panel_color": "#5865f2"}},
                headers={"X-CSRF-Token": "csrf"},
            )

        self.assertEqual(response.status_code, 200)
        view = edited["view"]
        self.assertEqual(view.children[0].accent_colour.value, BLURPLE)
        text = _panel_text(view)
        self.assertIn("Open a Ticket", text)
        self.assertIsNone(HEX_CODE.search(text))

    @staticmethod
    def _run_now(awaitable, timeout=8):
        return asyncio.run(awaitable)

    def test_a_malformed_color_is_rejected_instead_of_becoming_text(self):
        response = self._post_color("not-a-color")
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(ticket_utils.get_ticket_config(111).panel_color)


if __name__ == "__main__":
    unittest.main()
