"""Bundled fonts must cover the scripts display names actually use.

A member's display name such as ``ᥒꪗ᥊ꫀᥒ`` mixes Tai Le (U+1952), Tai Viet
(U+AA97, U+AAC0) and Limbu (U+194A). None of those are in the Latin face, so
without the matching Noto script faces the leveling card draws tofu boxes — and
only machines that happen to have unifont installed would look right.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

FONTS_DIR = ROOT / "src/assets/fonts"

# The display name from the bug report, plus one glyph per script it uses.
DISPLAY_NAME = "ᥒꪗ᥊ꫀᥒ"
REQUIRED_CODEPOINTS = {
    0x1952: "TAI LE LETTER NGA",
    0x194A: "LIMBU DIGIT FOUR",
    0xAA97: "TAI VIET LETTER HIGH THO",
    0xAAC0: "TAI VIET TONE MAI NUENG",
}


def _bundled_codepoints() -> set[int]:
    from fontTools.ttLib import TTFont

    covered: set[int] = set()
    for path in FONTS_DIR.glob("*.ttf"):
        font = TTFont(path, lazy=True, ignoreDecompileErrors=True)
        try:
            for table in font["cmap"].tables:
                if table.isUnicode():
                    covered.update(table.cmap)
        finally:
            font.close()
    return covered


class BundledFontCoverageTests(unittest.TestCase):
    def setUp(self):
        self.covered = _bundled_codepoints()

    def test_every_glyph_of_the_display_name_has_a_bundled_face(self):
        missing = [
            f"U+{cp:04X} {name}"
            for cp, name in REQUIRED_CODEPOINTS.items()
            if cp not in self.covered
        ]
        self.assertEqual(missing, [], f"no bundled font covers: {missing}")

    def test_the_resolver_picks_script_faces_per_glyph(self):
        from utils.image import _font_resolver as resolver

        family = resolver.get_font_family(bold=True, size=28)
        chosen = {}
        for char in DISPLAY_NAME:
            font = next((face for face in family if resolver._supports(face, char)), family[0])
            chosen[char] = Path(resolver._font_path(font)).name

        self.assertEqual(
            {name for name in chosen.values()},
            {"NotoSansTaiLe-Regular.ttf", "NotoSansTaiViet-Regular.ttf", "NotoSansLimbu-Regular.ttf"},
        )

    def test_no_glyph_renders_as_the_missing_glyph_box(self):
        """A tofu box is what the font draws for a codepoint it lacks."""
        from PIL import Image, ImageDraw

        from utils.image import _font_resolver as resolver

        family = resolver.get_font_family(bold=True, size=28)

        def render(font, char):
            image = Image.new("L", (64, 64), 0)
            ImageDraw.Draw(image).text((4, 4), char, font=font, fill=255)
            return image.tobytes()

        tofu = {id(face): render(face, "\ue000") for face in family}  # private use
        for char in DISPLAY_NAME:
            font = next((face for face in family if resolver._supports(face, char)), family[0])
            self.assertNotEqual(render(font, char), tofu[id(font)], f"U+{ord(char):04X} is tofu")


if __name__ == "__main__":
    unittest.main()
