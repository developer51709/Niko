"""The discovery listing copy and its cards stay in step with the bot's languages.

A listing is what a new server sees before it ever runs a command, so a missing
translation, a card that 404s, or a card whose artwork is stale next to its
description all advertise the wrong thing.
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PIL import Image  # noqa: E402

from utils.locales import SUPPORTED_LANGUAGES  # noqa: E402
from webapp import app  # noqa: E402

DOCS = ROOT / "docs" / "discovery"
PUBLIC = ROOT / "web" / "public" / "assets" / "discovery"
DIST = ROOT / "src" / "website" / "dist" / "assets" / "discovery"
CARD_URL = "https://niko.sryze.cc/assets/discovery"

LISTING_LINKS = (
    "https://discord.com/oauth2/authorize?client_id=1520558530472448170",
    "https://niko.sryze.cc/dashboard",
    "https://niko.sryze.cc/discord",
    "https://niko.sryze.cc/docs",
)


def _card_copy() -> dict[str, dict[str, object]]:
    """Load the generator without running its build entry point."""
    spec = importlib.util.spec_from_file_location(
        "generate_discovery_cards", ROOT / "scripts" / "generate_discovery_cards.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / "scripts"))
    spec.loader.exec_module(module)
    return module.CARD_COPY


def test_every_supported_language_has_one_description():
    descriptions = {path.stem for path in DOCS.glob("*.md")} - {"README"}

    assert descriptions == set(SUPPORTED_LANGUAGES)


def test_a_description_embeds_its_own_card_and_the_listing_links():
    for language in SUPPORTED_LANGUAGES:
        source = (DOCS / f"{language}.md").read_text(encoding="utf-8")

        assert f"]({CARD_URL}/{language}.png)" in source, language
        for link in LISTING_LINKS:
            assert link in source, f"{language} is missing {link}"


def test_the_card_artwork_matches_the_languages_it_is_generated_for():
    assert set(_card_copy()) == set(SUPPORTED_LANGUAGES)


def test_the_website_serves_a_generated_card_for_each_language():
    client = app.test_client()

    for language in SUPPORTED_LANGUAGES:
        source = PUBLIC / f"{language}.png"
        mirror = DIST / f"{language}.png"
        assert source.is_file(), source
        assert mirror.read_bytes() == source.read_bytes(), f"{mirror} is stale"

        response = client.get(f"/assets/discovery/{language}.png")
        assert response.status_code == 200
        assert response.mimetype == "image/png"


def test_cards_keep_their_corners_transparent():
    """The listing paints the card on its own background, dark or light."""
    for language in SUPPORTED_LANGUAGES:
        with Image.open(PUBLIC / f"{language}.png") as card:
            assert card.mode == "RGBA", language
            width, height = card.size
            alpha = card.getchannel("A").load()

            corners = ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1))
            assert [alpha[x, y] for x, y in corners] == [0, 0, 0, 0], language
            assert alpha[width // 2, height // 2] == 255, language
