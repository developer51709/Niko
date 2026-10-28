"""The economy and leveling cards must follow the website theme.

These tests pin the card palettes to the CSS custom properties in
``web/src/styles.css``, so a future theme change that forgets the card
renderers fails here instead of shipping mismatched images.  They also guard
against the old café palette creeping back in.
"""

import os
import re
import sys
import unittest
from io import BytesIO
from pathlib import Path
from unittest import mock

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.image import blackjack  # noqa: E402
from utils.image import economy_card as ec  # noqa: E402
from utils.image import level_card  # noqa: E402
from config.links import WEBSITE  # noqa: E402
from cogs.economy.data import (  # noqa: E402
    ACCENT_BROWN,
    LOADING_CARD_TYPES,
    _loading_card_view,
    _shop_loading_file,
)
from utils.economy_jobs import shop_loading_row_counts  # noqa: E402
from cogs.leveling.cog import (  # noqa: E402
    LEVELING_LOADING_CARD_TYPES,
    _loading_card_view as _leveling_loading_card_view,
)
from cogs.casino import blackjack as casino_blackjack  # noqa: E402
from cogs.tickets import views as ticket_views  # noqa: E402
from utils.tickets.config import TicketConfig  # noqa: E402

# Every colour the pre-theme café cards drew with.
CAFE_RGB = (
    (38, 26, 22),    # espresso canvas top
    (18, 12, 10),    # espresso canvas bottom
    (50, 36, 30),    # café panel
    (110, 78, 50),   # café panel border
    (255, 196, 92),  # gold
    (255, 220, 140), # bright gold
    (180, 124, 72),  # coffee
    (245, 232, 210), # cream
    (200, 188, 168), # cream dim
    (200, 162, 255), # rank purple
)

# The same palette as it appears in source: hex strings, CSS rgb() values and
# the old café wordmarks.
CAFE_SOURCE_LITERALS = (
    "FFC45C", "261A16", "120C0A", "F5E8D2", "C8BBA8", "8C918E", "6E4E32", "FFDC8C",
    "0xC8853F", "rgba(50,36,30", "rgba(40,28,22", "rgba(110,78,50",
    "CAFÉ ECONOMY", "CAFÉ LEVELING", "CAFE ECONOMY", "CAFE CASINO",
    "(38, 26, 22)", "(18, 12, 10)", "(50, 36, 30)", "(110, 78, 50)",
    "(255, 196, 92)", "(255, 220, 140)", "(180, 124, 72)", "(245, 232, 210)",
    "(200, 188, 168)", "(200, 162, 255)",
    # The blackjack table's pre-theme chrome: felt green, gold, blue card back.
    "(22, 70, 44)", "(8, 36, 22)", "(255, 215, 0)", "(24, 50, 110)",
)


def site_tokens() -> dict[str, tuple[int, int, int]]:
    """Read the website's ``:root`` colour custom properties."""
    css = (ROOT / "web" / "src" / "styles.css").read_text(encoding="utf-8")
    root = css.split(":root {", 1)[1].split("}", 1)[0]
    tokens = {}
    for match in re.finditer(r"--([a-z-]+):\s*#([0-9a-fA-F]{6})", root):
        value = match.group(2)
        tokens[match.group(1)] = tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    return tokens


def colours_in(buf: BytesIO) -> dict[tuple[int, int, int], int]:
    image = Image.open(buf).convert("RGB")
    return {rgb: count for count, rgb in image.getcolors(maxcolors=1_000_000)}


class PaletteMatchesWebsiteTests(unittest.TestCase):
    def test_card_palette_is_the_site_theme(self):
        tokens = site_tokens()
        self.assertEqual(ec.CANVAS_TOP, tokens["surface"])
        self.assertEqual(ec.CANVAS_BOT, tokens["canvas"])
        self.assertEqual(ec.INK, tokens["ink"])
        self.assertEqual(ec.MUTED, tokens["muted"])
        self.assertEqual(ec.DIM, tokens["dim"])
        self.assertEqual(ec.ACCENT, tokens["accent"])
        self.assertEqual(ec.ACCENT_BRIGHT, tokens["accent-dark"])
        self.assertEqual(ec.SAGE, tokens["sage"])
        self.assertEqual(ec.SURFACE_MUTED, tokens["surface-muted"])
        self.assertEqual(ec.LINE_SOFT, tokens["line-soft"])

    def test_panels_use_the_surface_and_line_tokens(self):
        tokens = site_tokens()
        self.assertEqual(ec.PANEL_BG[:3], tokens["surface-raised"])
        self.assertEqual(ec.PANEL_BORDER[:3], tokens["line"])
        self.assertEqual(len(ec.PANEL_BG), 4)
        self.assertEqual(len(ec.PANEL_BORDER), 4)

    def test_money_accents_follow_the_site_gain_and_loss_colours(self):
        self.assertEqual(ec.ACCENT_GOLD, ec.SAGE)
        self.assertEqual(ec.ACCENT_GREEN, ec.SAGE)
        self.assertEqual(ec.ACCENT_RED, ec.DANGER)

    def test_level_card_defaults_come_from_the_shared_palette(self):
        self.assertEqual(
            level_card._resolve_colours(),
            (ec.ACCENT_BRIGHT, ec.CANVAS_TOP, ec.CANVAS_BOT),
        )


class RenderedCardTests(unittest.TestCase):
    def test_balance_card_draws_only_theme_colours(self):
        buf = ec._render_balance_sync(
            None, "Test User", 1200, 3400, 20_000, "Vault I", 4_600, 4, 120, 400,
            "Barista", "", 3, 12,
        )
        counts = colours_in(buf)

        for rgb in CAFE_RGB:
            with self.subTest(colour=rgb):
                self.assertLess(counts.get(rgb, 0), 25, f"café colour {rgb} still drawn")

        themed = sum(counts.get(rgb, 0) for rgb in (ec.INK, ec.MUTED, ec.DIM, ec.ACCENT, ec.ACCENT_BRIGHT, ec.SAGE))
        self.assertGreater(themed, 500, "the card does not use the theme palette")

    def test_reward_card_draws_only_theme_colours(self):
        buf = ec._render_reward_sync(
            None, "Test User", "Daily treats", "Streak 3", 750, 5_350, ec.ACCENT_GOLD, "Come back tomorrow",
        )
        counts = colours_in(buf)

        for rgb in CAFE_RGB:
            with self.subTest(colour=rgb):
                self.assertLess(counts.get(rgb, 0), 25, f"café colour {rgb} still drawn")
        self.assertGreater(counts.get(ec.SAGE, 0), 100, "the reward amount is not drawn in sage")

    def test_leaderboard_shop_and_inventory_render(self):
        rows = [{"rank": i, "name": f"User {i}", "total": 1_000 * i, "avatar": None} for i in range(1, 4)]
        for buf in (
            ec._render_leaderboard_sync("Test Leaderboard", rows, 1, 2),
            ec._render_shop_sync([{"emoji": "", "name": "Item", "description": "desc", "price": 100, "sell": 30}], 500, None),
            ec._render_inventory_sync(None, "Test User", 500, [{"label": "Consumables", "items": [{"emoji": "", "name": "Item", "count": 2, "desc": "d"}]}]),
        ):
            with self.subTest(card=buf.getvalue()[:8]):
                counts = colours_in(buf)
                for rgb in CAFE_RGB:
                    self.assertLess(counts.get(rgb, 0), 25, f"café colour {rgb} still drawn")

    def test_blackjack_table_uses_the_theme_chrome(self):
        buf = blackjack._render_table_sync(
            [{"cards": ["AH", "KS"], "bet": 100, "label": "Hand 1"}],
            ["7D", "2C"], False, 0, "Blackjack", "Your turn", blackjack.TEXT_GOLD,
        )
        counts = colours_in(buf)

        for rgb, label in (((22, 70, 44), "felt top"), ((8, 36, 22), "felt bottom"), ((255, 215, 0), "gold"), ((24, 50, 110), "card back")):
            with self.subTest(chrome=label):
                self.assertLess(counts.get(rgb, 0), 25, f"the {label} colour is still drawn")
        self.assertEqual(blackjack.TABLE_BG_TOP, ec.SURFACE_MUTED)
        self.assertEqual(blackjack.TABLE_BG_BOT, ec.CANVAS_BOT)
        self.assertEqual(blackjack.ACTIVE_HALO, ec.ACCENT_BRIGHT)

    def test_avatar_fallback_is_neutral_not_a_coffee_cup(self):
        avatar = ec._circle_avatar(None, 96)
        counts = {rgb: count for count, rgb in avatar.convert("RGB").getcolors(maxcolors=1_000_000)}
        self.assertEqual(avatar.size, (96, 96))
        for rgb in CAFE_RGB:
            with self.subTest(colour=rgb):
                self.assertEqual(counts.get(rgb, 0), 0, f"café colour {rgb} in the placeholder avatar")


class EconomyLoadingCardTests(unittest.TestCase):
    """The bot's loading state and the generated GIFs must stay in step."""

    def test_every_loading_card_type_has_an_animated_gif(self):
        folder = ROOT / "web" / "public" / "assets" / "loading-cards" / "economy"
        for card_type in sorted(LOADING_CARD_TYPES):
            with self.subTest(card_type=card_type):
                path = folder / f"{card_type}.gif"
                self.assertTrue(
                    path.is_file(),
                    f"{path} is missing — run scripts/generate_economy_loading_cards.py",
                )
                image = Image.open(path)
                self.assertEqual(image.format, "GIF")
                self.assertGreater(getattr(image, "n_frames", 1), 1)
                image.close()

    def test_loading_view_uses_the_public_gif_url(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PUBLIC_URL", None)
            for card_type in sorted(LOADING_CARD_TYPES):
                with self.subTest(card_type=card_type):
                    view = _loading_card_view(card_type)
                    gallery = view.children[0].children[0]
                    self.assertEqual(
                        str(gallery.items[0].media.url),
                        f"{WEBSITE}/assets/loading-cards/economy/{card_type}.gif",
                    )

    def test_loading_view_follows_public_url_for_beta_instances(self):
        with mock.patch.dict(
            os.environ, {"PUBLIC_URL": "https://beta.example.com/"}, clear=False,
        ):
            for card_type in sorted(LOADING_CARD_TYPES):
                with self.subTest(card_type=card_type):
                    view = _loading_card_view(card_type)
                    gallery = view.children[0].children[0]
                    self.assertEqual(
                        str(gallery.items[0].media.url),
                        f"https://beta.example.com/assets/loading-cards/economy/{card_type}.gif",
                    )


class CardTransparencyTests(unittest.TestCase):
    """The corner cut-outs of a rounded card must stay transparent."""

    def test_level_card_keeps_its_rounded_corners_transparent(self):
        buffer = level_card._render_level_sync(None, "Alice", 5, 100, 250, 2)
        image = Image.open(buffer)
        self.assertEqual(image.mode, "RGBA")
        for xy in (
            (0, 0),
            (level_card.RANK_W - 1, 0),
            (0, level_card.RANK_H - 1),
            (level_card.RANK_W - 1, level_card.RANK_H - 1),
        ):
            with self.subTest(corner=xy):
                self.assertEqual(image.getpixel(xy)[3], 0)
        with self.subTest(corner="mid-top stays opaque"):
            self.assertEqual(image.getpixel((level_card.RANK_W // 2, 2))[3], 255)
        image.close()


class ShopLoadingCardSizeTests(unittest.TestCase):
    """The shop placeholder must be exactly as tall as the card it becomes."""

    def test_every_row_count_has_a_gif_the_size_of_the_card(self):
        folder = ROOT / "web" / "public" / "assets" / "loading-cards" / "economy"
        for rows in shop_loading_row_counts():
            with self.subTest(rows=rows):
                path = folder / _shop_loading_file(rows)
                self.assertTrue(
                    path.is_file(),
                    f"{path} is missing — run scripts/generate_economy_loading_cards.py",
                )
                image = Image.open(path)
                self.assertEqual(image.size, (ec.SHOP_W, ec.shop_card_height(rows)))
                image.close()

    def test_loading_view_uses_the_matching_size_and_disabled_controls(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PUBLIC_URL", None)
            view = _loading_card_view("shop", rows=3, shop_controls=True)
        container = view.children[0]
        gallery = container.children[0]
        self.assertEqual(
            str(gallery.items[0].media.url),
            f"{WEBSITE}/assets/loading-cards/economy/{_shop_loading_file(3)}",
        )
        self.assertEqual([type(item).__name__ for item in container.children], [
            "MediaGallery", "TextDisplay", "ActionRow",
        ])
        buttons = container.children[2].children
        self.assertEqual([button.label for button in buttons], ["Buy", "Sell"])
        self.assertTrue(all(button.disabled for button in buttons))


class LevelingLoadingCardTests(unittest.TestCase):
    """The leveling loading state and the generated GIFs must stay in step."""

    def test_every_loading_card_type_has_an_animated_gif(self):
        folder = ROOT / "web" / "public" / "assets" / "loading-cards" / "leveling"
        for card_type in sorted(LEVELING_LOADING_CARD_TYPES):
            with self.subTest(card_type=card_type):
                path = folder / f"{card_type}.gif"
                self.assertTrue(
                    path.is_file(),
                    f"{path} is missing — run scripts/generate_leveling_loading_cards.py",
                )
                image = Image.open(path)
                self.assertEqual(image.format, "GIF")
                self.assertGreater(getattr(image, "n_frames", 1), 1)
                image.close()

    def test_loading_view_uses_the_public_gif_url(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PUBLIC_URL", None)
            for card_type in sorted(LEVELING_LOADING_CARD_TYPES):
                with self.subTest(card_type=card_type):
                    view = _leveling_loading_card_view(card_type)
                    gallery = view.children[0].children[0]
                    self.assertEqual(
                        str(gallery.items[0].media.url),
                        f"{WEBSITE}/assets/loading-cards/leveling/{card_type}.gif",
                    )

    def test_loading_view_follows_public_url_for_beta_instances(self):
        with mock.patch.dict(
            os.environ, {"PUBLIC_URL": "https://beta.example.com/"}, clear=False,
        ):
            for card_type in sorted(LEVELING_LOADING_CARD_TYPES):
                with self.subTest(card_type=card_type):
                    view = _leveling_loading_card_view(card_type)
                    gallery = view.children[0].children[0]
                    self.assertEqual(
                        str(gallery.items[0].media.url),
                        f"https://beta.example.com/assets/loading-cards/leveling/{card_type}.gif",
                    )


class OldCafeThemeRemovedTests(unittest.TestCase):
    FILES = (
        "src/utils/image/economy_card.py",
        "src/utils/image/level_card.py",
        "src/utils/image/blackjack.py",
        "src/webapp/server.py",
        "src/cogs/economy/data.py",
        "src/cogs/economy/commands/shop.py",
        "src/cogs/leveling/panel.py",
        "src/cogs/leveling/cog.py",
        "src/cogs/casino/blackjack.py",
    )

    def test_no_cafe_palette_or_wordmark_literals_remain(self):
        for relative in self.FILES:
            text = (ROOT / relative).read_text(encoding="utf-8")
            hits = [literal for literal in CAFE_SOURCE_LITERALS if literal in text]
            with self.subTest(path=relative):
                self.assertEqual(hits, [], f"{relative} still contains café theme values: {hits}")

    def test_economy_containers_use_the_brand_accent(self):
        self.assertEqual(ACCENT_BROWN.value, 0xC8A882)
        shop = (ROOT / "src/cogs/economy/commands/shop.py").read_text(encoding="utf-8")
        self.assertNotIn("0xC8853F", shop)

    def test_casino_table_status_colours_are_theme_colours(self):
        self.assertEqual(casino_blackjack.ACCENT_BRAND.value, 0xC8A882)
        self.assertEqual(casino_blackjack.STATUS_NEUTRAL, ec.ACCENT_BRIGHT)
        self.assertEqual(casino_blackjack.STATUS_WIN, ec.SAGE)
        self.assertEqual(casino_blackjack.STATUS_LOSS, ec.DANGER)

    def test_the_ticket_system_has_no_cafe_voice_left(self):
        for relative in ("src/cogs/tickets/views.py", "src/cogs/tickets/cog.py"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            hits = [
                literal for literal in ("\"cafe\"", "☕", "cozy", "booth", "staff lounge", "sweet bean")
                if literal in text
            ]
            with self.subTest(path=relative):
                self.assertEqual(hits, [], f"{relative} still ships the café ticket voice: {hits}")

    def test_a_new_ticket_panel_uses_the_standard_defaults(self):
        view = ticket_views.TicketPanelView(999, TicketConfig(guild_id=999))
        text = "\n".join(
            child.content
            for container in view.children
            for child in getattr(container, "children", [])
            if isinstance(getattr(child, "content", None), str)
        )
        self.assertIn("Open a Ticket", text)
        self.assertNotIn("☕", text)

    def test_no_cog_ships_a_cafe_message_catalogue(self):
        offenders = []
        for path in sorted((ROOT / "src").rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            if re.search(r'^[ \t]*"cafe":\s*\{', text, re.MULTILINE) or 'MESSAGES["cafe"]' in text:
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [], f"café message catalogues are back: {offenders}")

    def test_the_shop_dropped_the_cafe_branding(self):
        files = {
            "src/cogs/economy/commands/shop.py": ("boutique", "Boutique"),
            "src/utils/image/economy_card.py": ("Boutique", "Treats", "\U0001F950"),
        }
        for relative, literals in files.items():
            text = (ROOT / relative).read_text(encoding="utf-8")
            for literal in literals:
                with self.subTest(path=relative, literal=literal):
                    self.assertNotIn(literal, text, f"{relative} still carries the café shop branding: {literal}")
        self.assertIn("Niko's Shop", (ROOT / "src/utils/image/economy_card.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
