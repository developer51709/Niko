"""The pfp command offers only male/female and reads bundled pfp assets.

The gender pickers and the owner upload commands used to offer a non-binary
option that had no image folder behind it.  The male and female pools are also
much larger now: pictures from the piccdn library are downloaded into
``src/assets/pfps/genders`` instead of being fetched at command time.
"""

import asyncio
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

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
