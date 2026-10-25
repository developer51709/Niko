"""The pfp command offers only male/female and reads bundled pfp assets.

The gender pickers and the owner upload commands used to offer a non-binary
option that had no image folder behind it.  The male and female pools are also
much larger now: pictures from the piccdn library are downloaded into
``src/assets/pfps/genders`` instead of being fetched at command time.
"""

import asyncio
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import discord

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.social import pfps  # noqa: E402

GENDER_FOLDER = ROOT / "src" / "assets" / "pfps" / "genders"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}


def _ctx():
    return SimpleNamespace(author=SimpleNamespace(id=1))


def _images(gender: str):
    return [path for path in (GENDER_FOLDER / gender).iterdir() if path.suffix.lower() in IMAGE_SUFFIXES]


class PfpOptionTests(unittest.TestCase):
    def test_the_gender_select_offers_only_male_and_female(self):
        select = pfps.GenderSelect(_ctx())
        self.assertEqual([option.value for option in select.options], ["male", "female"])
        self.assertEqual([option.label for option in select.options], ["Male", "Female"])

    def test_both_couple_selects_offer_only_male_and_female(self):
        for select_cls in (pfps.CoupleGenderSelect, pfps.CoupleGenderSelect2):
            with self.subTest(select=select_cls.__name__):
                select = select_cls(_ctx())
                self.assertEqual([option.value for option in select.options], ["male", "female"])

    def test_the_supported_genders_and_couple_folders_are_explicit(self):
        self.assertEqual(list(pfps.GENDERS), ["male", "female"])
        self.assertEqual(
            list(pfps.COUPLE_SUBFOLDERS),
            ["male-male", "male-female", "female-female"],
        )


class PfpCopyTests(unittest.TestCase):
    def test_the_couple_panel_has_no_development_note(self):
        view = pfps.CouplesGenderSelect(_ctx())
        text = "\n".join(
            child.content
            for container in view.children
            for child in getattr(container, "children", [])
            if isinstance(getattr(child, "content", None), str)
        )
        self.assertIn("Couple Profile Pictures", text)
        for marker in ("development", "developers", "nyxen", "contribute"):
            self.assertNotIn(marker, text.lower())

    def test_no_developer_note_text_is_left_in_the_module(self):
        source = (ROOT / "src" / "cogs" / "social" / "pfps.py").read_text(encoding="utf-8").lower()
        for marker in ("note from developers", "still in development", "nyxen"):
            self.assertNotIn(marker, source)


class BulkUploadTests(unittest.TestCase):
    def test_the_image_suffix_comes_from_the_file_signature(self):
        self.assertEqual(pfps._image_suffix(b"\x89PNG\r\n\x1a\nrest"), ".png")
        self.assertEqual(pfps._image_suffix(b"\xff\xd8\xffrest"), ".jpg")
        self.assertEqual(pfps._image_suffix(b"GIF89arest"), ".gif")
        self.assertEqual(pfps._image_suffix(b"RIFF\x00\x00\x00\x00WEBPVP8 "), ".webp")
        self.assertIsNone(pfps._image_suffix(b"not an image"))

    def test_a_bulk_upload_saves_every_image_after_the_existing_ones(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "1.png").write_bytes(b"\x89PNG\r\n\x1a\nold")
            images = [
                io.BytesIO(b"\x89PNG\r\n\x1a\nnew1"),
                io.BytesIO(b"\xff\xd8\xffnew2"),
                io.BytesIO(b"GIF89anew3"),
            ]
            self.assertEqual(pfps.save_pfp_images(str(folder), images), 3)
            self.assertEqual(
                sorted(path.name for path in folder.iterdir()),
                ["1.png", "2.png", "3.jpg", "4.gif"],
            )
            self.assertEqual((folder / "2.png").read_bytes(), b"\x89PNG\r\n\x1a\nnew1")

    def test_non_image_attachments_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            images = [io.BytesIO(b"PK\x03\x04zip"), io.BytesIO(b"\x89PNG\r\n\x1a\nok")]
            self.assertEqual(pfps.save_pfp_images(str(folder), images), 1)
            self.assertEqual([path.name for path in folder.iterdir()], ["1.png"])

    def test_an_empty_batch_writes_nothing_and_creates_no_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "purple"
            self.assertEqual(pfps.save_pfp_images(str(folder), []), 0)
            self.assertFalse(folder.exists())


class _Attachment:
    def __init__(self, data: bytes):
        self._data = data

    async def read(self) -> bytes:
        return self._data


class _Message:
    def __init__(self, *payloads: bytes):
        self.attachments = [_Attachment(payload) for payload in payloads]
        self.embeds = []
        self.stickers = []
        self.content = ""
        self.reference = None


class _Ctx:
    def __init__(self, *payloads: bytes):
        self.message = _Message(*payloads)
        self.sent = []

    async def send(self, **kwargs):
        self.sent.append(kwargs)


def _view_text(view: discord.ui.LayoutView) -> str:
    return "\n".join(
        child.content
        for container in view.children
        for child in getattr(container, "children", [])
        if isinstance(getattr(child, "content", None), str)
    )


class UploadCommandTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.folder = Path(self._tmp.name)
        patcher = mock.patch.object(pfps, "PFPS_FOLDER", str(self.folder))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_upload_color_saves_every_attachment_in_one_command(self):
        ctx = _Ctx(
            b"\x89PNG\r\n\x1a\nfirst",
            b"\xff\xd8\xffsecond",
            b"\x89PNG\r\n\x1a\nthird",
        )
        asyncio.run(pfps.PfpCog.upload_color.callback(None, ctx, "Purple"))
        saved = sorted(path.name for path in (self.folder / "colors" / "purple").iterdir())
        self.assertEqual(saved, ["1.png", "2.jpg", "3.png"])
        self.assertIn("Uploaded 3 profile pictures", _view_text(ctx.sent[-1]["view"]))

    def test_upload_gender_saves_a_batch_and_reports_the_count(self):
        ctx = _Ctx(b"\x89PNG\r\n\x1a\none", b"\x89PNG\r\n\x1a\ntwo")
        asyncio.run(pfps.PfpCog.upload_gender.callback(None, ctx, "female"))
        saved = sorted(path.name for path in (self.folder / "genders" / "female").iterdir())
        self.assertEqual(saved, ["1.png", "2.png"])
        self.assertIn("Uploaded 2 profile pictures", _view_text(ctx.sent[-1]["view"]))

    def test_upload_gender_still_rejects_an_unsupported_gender(self):
        ctx = _Ctx(b"\x89PNG\r\n\x1a\none")
        asyncio.run(pfps.PfpCog.upload_gender.callback(None, ctx, "non-binary"))
        self.assertFalse((self.folder / "genders" / "non-binary").exists())
        self.assertIn("not supported", _view_text(ctx.sent[-1]["view"]))

    def test_upload_color_reports_when_nothing_is_attached(self):
        ctx = _Ctx()
        asyncio.run(pfps.PfpCog.upload_color.callback(None, ctx, "purple"))
        self.assertFalse((self.folder / "colors" / "purple").exists())
        self.assertIn("No image found", _view_text(ctx.sent[-1]["view"]))


class GenderAssetTests(unittest.TestCase):
    def test_both_gender_folders_hold_a_bundled_library(self):
        for gender in pfps.GENDERS:
            with self.subTest(gender=gender):
                self.assertGreaterEqual(len(_images(gender)), 50)

    def test_the_selector_counts_the_bundled_images(self):
        counts = dict(pfps.get_gender_image_counts())
        self.assertEqual(list(counts), ["male", "female"])
        for gender, count in counts.items():
            with self.subTest(gender=gender):
                self.assertEqual(count, len(_images(gender)))

    def test_a_gender_pfp_is_served_from_the_bundled_folder(self):
        for gender in pfps.GENDERS:
            with self.subTest(gender=gender):
                picture = asyncio.run(pfps.get_gender_pfp(_ctx(), gender))
                self.addCleanup(picture.close)
                self.assertIsInstance(picture, discord.File)
                path = Path(picture.fp.name)
                self.assertEqual(path.parent.name, gender)
                self.assertEqual(path.parent.parent.name, "genders")
                self.assertIn(path.suffix.lower(), IMAGE_SUFFIXES)


if __name__ == "__main__":
    unittest.main()
