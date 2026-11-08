"""The ``.spotify`` card and its animated loading state must stay in step.

The command sends a generated GIF placeholder from the public website while the
PNG renders, then edits the message into the card. These tests pin the card's
shape, the cover-art fallback, and the GIF the loading view points at, so a
rename or a forgotten generator run fails here instead of shipping a blank card.
"""

import asyncio
import datetime
import hashlib
import os
import sys
import types
import unittest
from io import BytesIO
from pathlib import Path
from unittest import mock

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import discord  # noqa: E402

from config.links import WEBSITE  # noqa: E402
from cogs.info import cog as info_cog  # noqa: E402
from cogs.info._spotify import (  # noqa: E402
    SPOTIFY_LOADING_CARD_TYPES,
    _spotify_loading_card_view,
)
from utils.image.spotify_card import (  # noqa: E402
    ART_RADIUS,
    CARD_H,
    CARD_W,
    HEADER_MARK,
    _logo_asset_path,
    _logo_subpaths,
    _render_spotify_sync,
    _spotify_logo,
    render_spotify_card,
)


def _loading_gif_url(base: str, file_name: str) -> str:
    """A loading-card URL with the short hash of the generated GIF."""
    path = ROOT / "web" / "public" / "assets" / "loading-cards" / file_name
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:8]
    return f"{base}/{file_name}?hash={digest}"


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

    def test_card_is_taller_than_the_other_command_cards(self):
        # The Spotify card is deliberately its own shape: a tall artwork-driven
        # card rather than the wide graphite one the other commands share.
        self.assertEqual((CARD_W, CARD_H), (820, 470))

    def test_artwork_uses_the_guideline_corner_radius(self):
        # Spotify asks for an 8 px radius on large surfaces.
        self.assertEqual(ART_RADIUS, 8)

    def test_backdrop_takes_its_colour_from_the_cover_art(self):
        def backdrop_tint(colour):
            buffer = _render_spotify_sync(
                _cover_bytes(colour), "Track", "Artist", "Album", 180.0, 30.0, ""
            )
            image = Image.open(buffer).convert("RGB")
            # Below the title block and above the progress bar: backdrop only.
            return ImageStat.Stat(image.crop((660, 340, 720, 360))).mean

        red = backdrop_tint((230, 30, 30))
        blue = backdrop_tint((30, 30, 230))
        self.assertGreater(red[0], red[2])
        self.assertGreater(blue[2], blue[0])

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

    def test_card_keeps_its_rounded_corners_transparent(self):
        buffer = _render_spotify_sync(None, "Track", "Artist", "Album", 180.0, 30.0, "")
        image = Image.open(buffer)
        self.assertEqual(image.mode, "RGBA")
        with self.subTest(corner="top-left"):
            self.assertEqual(image.getpixel((0, 0))[3], 0)
        with self.subTest(corner="top-right"):
            self.assertEqual(image.getpixel((CARD_W - 1, 0))[3], 0)
        with self.subTest(corner="bottom-left"):
            self.assertEqual(image.getpixel((0, CARD_H - 1))[3], 0)
        with self.subTest(corner="mid-top stays opaque"):
            self.assertEqual(image.getpixel((CARD_W // 2, 2))[3], 255)
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


class SpotifyLogoAssetTests(unittest.TestCase):
    """The mark is the website's own ``spotify.svg``, not a hand-drawn lookalike."""

    def test_logo_is_loadable_from_the_website_asset(self):
        path = _logo_asset_path()
        self.assertIsNotNone(path)
        self.assertEqual(path.name, "spotify.svg")
        self.assertIn(path.parent.name, {"public", "dist"})

    def test_the_asset_is_a_disc_plus_three_arc_cutouts(self):
        subpaths = _logo_subpaths()
        self.assertEqual(len(subpaths), 4)
        for subpath in subpaths:
            self.assertEqual(subpath[0], subpath[-1], "every subpath must be closed")
        xs = [point[0] for point in subpaths[0]]
        ys = [point[1] for point in subpaths[0]]
        self.assertEqual((round(min(xs)), round(min(ys))), (0, 0))
        self.assertEqual((round(max(xs)), round(max(ys))), (24, 24))

    def test_the_mark_is_rasterised_from_the_asset_in_monochrome(self):
        # The green colourway is only allowed on black or white, so on the
        # artwork-tinted card the icon is white.
        mark = _spotify_logo(60)
        self.assertEqual(mark.getpixel((30, 52)), (255, 255, 255, 255))
        self.assertEqual(mark.getpixel((0, 0))[3], 0)      # outside the disc
        self.assertLess(mark.getpixel((30, 19))[3], 128)   # one of the cut-outs

    def test_the_icon_is_large_enough_to_stay_above_the_minimum(self):
        # 21 px digital minimum, and Discord scales the attachment down.
        self.assertGreaterEqual(HEADER_MARK, 21)
        self.assertGreaterEqual(HEADER_MARK * 0.6, 21)


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
        with mock.patch.object(discord, "Member", _Member), \
                mock.patch.object(discord, "Spotify", _Spotify):
            asyncio.run(info_cog.InfoCog.spotify.callback(cog, ctx, _Member()))
        return interaction, ctx

    def test_prefix_command_shows_the_loading_card_then_the_render(self):
        interaction, ctx = self._run(slash=False)
        self.assertIsNone(interaction)
        gallery = ctx.sent_view.children[0].children[0]
        self.assertRegex(
            str(gallery.items[0].media.url),
            r"/assets/loading-cards/spotify\.gif\?hash=[0-9a-f]{8}$",
        )

        attachments = ctx.message.edit_kwargs["attachments"]
        self.assertEqual(attachments[0].filename, "spotify.png")
        # The PNG is handed back as soon as Discord has it: the card is never
        # reused, so keeping the buffer would only cost the host memory.
        self.assertTrue(attachments[0].fp.closed)
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
                        _loading_gif_url(f"{WEBSITE}/assets/loading-cards", "spotify.gif"),
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
                        _loading_gif_url(
                            "https://beta.example.com/assets/loading-cards", "spotify.gif"
                        ),
                    )
