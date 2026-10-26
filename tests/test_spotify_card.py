"""The ``.spotify`` card and its animated loading state must stay in step.

The command sends a generated GIF placeholder from the public website while the
PNG renders, then edits the message into the card. These tests pin the card's
shape, the cover-art fallback, and the GIF the loading view points at, so a
rename or a forgotten generator run fails here instead of shipping a blank card.
"""

import asyncio
import datetime
import os
import sys
import types
import unittest
from io import BytesIO
from pathlib import Path
from unittest import mock

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config.links import WEBSITE  # noqa: E402
from cogs.info import cog as info_cog  # noqa: E402
from cogs.info.cog import (  # noqa: E402
    SPOTIFY_LOADING_CARD_TYPES,
    _spotify_loading_card_view,
)
from utils.image.spotify_card import (  # noqa: E402
    CARD_H,
    CARD_W,
    _render_spotify_sync,
    render_spotify_card,
)


def _cover_bytes(colour=(32, 120, 70)) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (300, 300), colour).save(buffer, format="PNG")
    return buffer.getvalue()


class SpotifyCardRenderTests(unittest.TestCase):
    def test_card_is_a_png_of_the_expected_size(self):
        buffer = _render_spotify_sync(
            _cover_bytes(),
            "Starboy",
            "The Weeknd",
            "Starboy",
            230.0,
            92.0,
            "Alice is listening to Spotify",
        )
        image = Image.open(buffer)
        self.assertEqual(image.format, "PNG")
        self.assertEqual(image.size, (CARD_W, CARD_H))
        image.close()

    def test_missing_cover_art_still_renders_a_card(self):
        buffer = _render_spotify_sync(
            None,
            "Solo",
            "Frank Ocean",
            "Blonde",
            0,
            None,
            "",
        )
        image = Image.open(buffer)
        self.assertEqual(image.size, (CARD_W, CARD_H))
        image.close()

    def test_public_renderer_returns_a_png_buffer(self):
        buffer = asyncio.run(
            render_spotify_card(
                cover_bytes=None,
                title="Track",
                artist="Artist",
                album="Album",
                duration=180.0,
                elapsed=60.0,
                footer="Listening to Spotify",
            )
        )
        image = Image.open(buffer)
        self.assertEqual(image.format, "PNG")
        image.close()


class _Member:
    display_name = "Alice"

    def __init__(self):
        self.activities = [_Spotify()]


class _Spotify:
    title = "Starboy"
    artist = "The Weeknd"
    album = "Starboy"
    duration = datetime.timedelta(seconds=230)
    start = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
    end = start + duration
    album_cover_url = ""
    track_id = "abc123"


class _Message:
    def __init__(self):
        self.edit_kwargs = None

    async def edit(self, **kwargs):
        self.edit_kwargs = kwargs


class _Response:
    def __init__(self):
        self.deferred = False

    async def defer(self):
        self.deferred = True


class _Interaction:
    def __init__(self):
        self.response = _Response()
        self.message = _Message()
        self.loading_view = None

    async def edit_original_response(self, view):
        self.loading_view = view
        return self.message


class _Context:
    def __init__(self, interaction=None):
        self.interaction = interaction
        self.guild = types.SimpleNamespace(preferred_locale="en-US")
        self.message = _Message()
        self.sent_view = None

    async def send(self, **kwargs):
        self.sent_view = kwargs.get("view")
        return self.message


class SpotifyCommandFlowTests(unittest.TestCase):
    """The command shows the GIF placeholder, then edits in the rendered card."""

    def _run(self, *, slash: bool):
        interaction = _Interaction() if slash else None
        ctx = _Context(interaction)
        cog = info_cog.InfoCog(bot=types.SimpleNamespace(start_time=0))
        with mock.patch.object(info_cog.discord, "Member", _Member), \
                mock.patch.object(info_cog.discord, "Spotify", _Spotify):
            asyncio.run(info_cog.InfoCog.spotify.callback(cog, ctx, _Member()))
        return interaction, ctx

    def test_prefix_command_shows_the_loading_card_then_the_render(self):
        interaction, ctx = self._run(slash=False)
        self.assertIsNone(interaction)
        gallery = ctx.sent_view.children[0].children[0]
        self.assertTrue(str(gallery.items[0].media.url).endswith("/assets/loading-cards/spotify.gif"))

        attachments = ctx.message.edit_kwargs["attachments"]
        self.assertEqual(attachments[0].filename, "spotify.png")
        card = ctx.message.edit_kwargs["view"].children[0]
        self.assertEqual(str(card.children[0].items[0].media.url), "attachment://spotify.png")

    def test_slash_command_reuses_the_deferred_response(self):
        interaction, ctx = self._run(slash=True)
        self.assertTrue(interaction.response.deferred)
        self.assertIsNotNone(interaction.loading_view)
        self.assertIsNone(ctx.sent_view)
        self.assertEqual(
            interaction.message.edit_kwargs["attachments"][0].filename,
            "spotify.png",
        )


class SpotifyLoadingCardTests(unittest.TestCase):
    def test_every_loading_card_type_has_an_animated_gif(self):
        folder = ROOT / "web" / "public" / "assets" / "loading-cards"
        for card_type in sorted(SPOTIFY_LOADING_CARD_TYPES):
            with self.subTest(card_type=card_type):
                path = folder / "spotify.gif"
                self.assertTrue(
                    path.is_file(),
                    f"{path} is missing — run scripts/generate_spotify_loading_card.py",
                )
                image = Image.open(path)
                self.assertEqual(image.format, "GIF")
                self.assertEqual(image.size, (CARD_W, CARD_H))
                self.assertGreater(getattr(image, "n_frames", 1), 1)
                image.close()

    def test_loading_view_uses_the_public_gif_url(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PUBLIC_URL", None)
            for card_type in sorted(SPOTIFY_LOADING_CARD_TYPES):
                with self.subTest(card_type=card_type):
                    view = _spotify_loading_card_view(card_type)
                    gallery = view.children[0].children[0]
                    self.assertEqual(
                        str(gallery.items[0].media.url),
                        f"{WEBSITE}/assets/loading-cards/spotify.gif",
                    )

    def test_loading_view_follows_public_url_for_beta_instances(self):
        with mock.patch.dict(
            os.environ, {"PUBLIC_URL": "https://beta.example.com/"}, clear=False,
        ):
            for card_type in sorted(SPOTIFY_LOADING_CARD_TYPES):
                with self.subTest(card_type=card_type):
                    view = _spotify_loading_card_view(card_type)
                    gallery = view.children[0].children[0]
                    self.assertEqual(
                        str(gallery.items[0].media.url),
                        f"https://beta.example.com/assets/loading-cards/spotify.gif",
                    )
