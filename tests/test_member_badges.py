"""Niko's own profile badges, from role to rendered artwork.

The bot's profile card, the website's profile popovers and the exported
transcript each draw the same badges, so these tests pin the shared badge keys
and prove every key has art behind it on all three surfaces.
"""

import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config.emojis import get_emoji  # noqa: E402
from utils import member_badges  # noqa: E402
from utils.member_badges import NIKO_BADGE_ORDER, niko_badge_keys  # noqa: E402

SUPPORT_ROLES = {
    "staff": 10,
    "head_admin": 11,
    "moderator": 12,
    "support": 13,
    "supporter": 20,
    "bugbounty": 21,
    "partner": 22,
}


def _bot(guild=None):
    """A bot stub: no database pool, and only the support guild cached."""
    return SimpleNamespace(cxn=None, get_guild=lambda guild_id: guild)


def _guild(role_ids):
    member = SimpleNamespace(roles=[SimpleNamespace(id=role_id) for role_id in role_ids])
    return SimpleNamespace(get_member=lambda user_id: member)


def _info_cards_source() -> str:
    """Every module of the info cog: its cards are split by subject."""
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "src" / "cogs" / "info").glob("*.py"))
    )


@pytest.fixture
def support_roles(monkeypatch):
    """Wire the configured support-server role ids without a database."""
    from cogs.staff import support_server

    async def fake_get_support_ids(bot):
        return {"roles": {key: str(value) for key, value in SUPPORT_ROLES.items()}, "channels": {}}

    monkeypatch.setattr(support_server, "get_support_ids", fake_get_support_ids)
    return SUPPORT_ROLES


@pytest.fixture
def staff_role(monkeypatch):
    """Set the stored staff role the DB-backed lookup would return."""
    from cogs.staff import records as staff_cog

    async def set_role(bot, user_id):
        return set_role.value

    set_role.value = None
    monkeypatch.setattr(staff_cog, "get_staff_role", set_role)
    return set_role


@pytest.fixture
def supporter(monkeypatch):
    """Control the confirmed-donation lookup."""
    from utils import donations

    async def is_supporter(bot, user_id):
        return is_supporter.value

    is_supporter.value = False
    monkeypatch.setattr(donations, "is_supporter", is_supporter)
    return is_supporter


def test_no_bot_and_no_guild_means_no_badges():
    import asyncio

    assert asyncio.run(niko_badge_keys(None, 456)) == []
    assert asyncio.run(niko_badge_keys(_bot(), 456)) == []


def test_support_server_community_roles_map_to_their_badges(support_roles):
    import asyncio

    badges = asyncio.run(
        niko_badge_keys(_bot(_guild([SUPPORT_ROLES["supporter"], SUPPORT_ROLES["bugbounty"]])), 456)
    )

    assert badges == ["niko_supporter", "niko_bug_hunter"]


def test_a_specific_staff_role_replaces_the_umbrella_badge(support_roles):
    import asyncio

    support = asyncio.run(niko_badge_keys(_bot(_guild([SUPPORT_ROLES["staff"], SUPPORT_ROLES["support"]])), 456))
    umbrella = asyncio.run(niko_badge_keys(_bot(_guild([SUPPORT_ROLES["staff"]])), 456))

    # The umbrella role rides along with every staff role, so it must not show
    # up next to a badge that already says which role it is.
    assert support == ["niko_support"]
    assert umbrella == ["niko_staff"]


def test_the_stored_staff_role_is_authoritative(staff_role):
    import asyncio

    staff_role.value = "head_admin"

    assert asyncio.run(niko_badge_keys(_bot(), 456)) == ["niko_head_admin"]


def test_the_owner_badge_comes_from_the_configured_owner_ids(monkeypatch):
    import asyncio

    monkeypatch.setattr(member_badges, "OWNER_IDS", {456})

    assert asyncio.run(niko_badge_keys(_bot(), 456)) == ["niko_owner"]


def test_a_donation_is_a_badge_without_the_support_server(supporter):
    import asyncio

    supporter.value = True

    assert asyncio.run(niko_badge_keys(_bot(), 456)) == ["niko_supporter"]


def test_badges_come_back_in_display_order(support_roles, supporter, staff_role):
    import asyncio

    supporter.value = True
    staff_role.value = "moderator"
    guild = _guild([SUPPORT_ROLES["staff"], SUPPORT_ROLES["moderator"], SUPPORT_ROLES["partner"]])

    badges = asyncio.run(niko_badge_keys(_bot(guild), 456))

    assert badges == ["niko_moderator", "niko_supporter", "niko_partner"]
    assert badges == [key for key in NIKO_BADGE_ORDER if key in badges]


def test_every_badge_key_has_emoji_art_and_a_web_asset():
    from cogs.info._badges import _NIKO_BADGE_EMOJIS

    # The bot's card maps each badge key to an emoji name, and no key is lost.
    assert set(_NIKO_BADGE_EMOJIS) == set(NIKO_BADGE_ORDER)
    for badge, emoji_name in _NIKO_BADGE_EMOJIS.items():
        token = get_emoji(emoji_name)
        assert token and f":{emoji_name}:" in token, f"{badge} has no emoji entry"
        # Discord only accepts PNG/JPEG/GIF emoji images, so the sync uploads
        # the rasterised art next to the config entry.
        assert (ROOT / "src" / "assets" / "emojis" / f"{emoji_name}.png").exists(), emoji_name

    # The popups own the SVG artwork, one file per badge and no orphans.
    badge_art = {path.stem for path in (ROOT / "web" / "public" / "assets" / "badges").glob("niko_*.svg")}
    assert badge_art == set(NIKO_BADGE_ORDER)


def test_the_bot_cards_emoji_names_all_resolve():
    """A typo here means a missing emoji in the middle of a profile card."""
    source = _info_cards_source()
    names = set(re.findall(r'get_emoji\("([A-Za-z0-9_]+)"\)', source))

    assert names
    assert sorted(name for name in names if not get_emoji(name)) == []


def test_every_emoji_name_fits_discords_limit():
    """Discord rejects names over 32 characters.

    A too-long name is uploaded by nobody: the sync skips it, the placeholder id
    in the config stays, and every card that uses that emoji shows a broken one.
    """
    source = (ROOT / "src" / "config" / "emojis.py").read_text(encoding="utf-8")
    names = set(re.findall(r'emoji_name == "([A-Za-z0-9_]+)"', source))

    assert names
    assert sorted(name for name in names if len(name) > 32) == []


def _months_before(now, count):
    """The same day ``count`` months before ``now``, capped to a safe day."""
    from datetime import datetime

    year, month = divmod(now.year * 12 + now.month - 1 - count, 12)
    return datetime(year, month + 1, min(now.day, 28), tzinfo=now.tzinfo)


def test_the_boosting_badge_picks_the_tier_the_streak_has_reached():
    from datetime import datetime, timezone

    from utils.member_badges import BOOSTING_TIERS, boosting_badge_key

    now = datetime.now(timezone.utc)
    assert BOOSTING_TIERS == (1, 2, 3, 6, 9, 12, 15, 18, 24)
    assert boosting_badge_key(None) is None
    # A boost that started this month has no tier yet.
    assert boosting_badge_key(now) is None
    assert boosting_badge_key(_months_before(now, 1)) == "boosting_1_months"
    # Discord keeps the lower tier until the next one is reached.
    assert boosting_badge_key(_months_before(now, 8)) == "boosting_6_months"
    assert boosting_badge_key(_months_before(now, 40)) == "boosting_24_months"


def test_every_boosting_tier_has_its_own_emoji_and_art():
    """A tier the bot cannot render would show a broken badge on the card."""
    from utils.member_badges import BOOSTING_TIERS

    for months in BOOSTING_TIERS:
        name = f"boosting_{months}_months"
        token = get_emoji(name)
        assert token and f":{name}:" in token, name
        assert (ROOT / "src" / "assets" / "emojis" / f"{name}.png").exists(), name
        assert (ROOT / "web" / "public" / "assets" / "badges" / f"{name}.svg").exists(), name


def test_the_bot_card_and_the_web_api_share_one_boosting_lookup():
    """One tier helper, so the card and the popups can never disagree."""
    cog = _info_cards_source()
    routes = (ROOT / "src" / "webapp" / "routes" / "discord_text_routes.py").read_text(encoding="utf-8")

    assert "boosting_badge_key(" in cog
    assert "boosting_badge_key(" in routes
    # The one hardcoded badge the card used to draw for every streak is gone.
    assert 'get_emoji("boosting_badge")' not in cog


#: The Discord keys in web/src/data/profileBadges.ts that are not generated from
#: the boosting tier loop.
_WEB_DISCORD_BADGE_KEYS = {
    "staff", "partner", "hypesquad_events", "bug_hunter_level_1", "hypesquad_bravery",
    "hypesquad_brilliance", "hypesquad_balance", "early_supporter", "bug_hunter_level_2",
    "early_verified_developer", "certified_moderator", "supports_commands", "active_developer",
}


def test_every_popup_surface_knows_the_same_badges():
    """The website popup, the transcript popup and the render lab draw one set."""
    from utils.member_badges import BOOSTING_TIERS
    from utils.tickets.transcripts import _PROFILE_BADGE_FILES

    catalog = (ROOT / "web" / "src" / "data" / "profileBadges.ts").read_text(encoding="utf-8")
    lab = (ROOT / "web" / "src" / "pages" / "RenderLabPage.tsx").read_text(encoding="utf-8")
    popup = (ROOT / "web" / "src" / "components" / "DiscordBadgeList.tsx").read_text(encoding="utf-8")
    markdown = (ROOT / "web" / "src" / "components" / "DiscordMarkdown.tsx").read_text(encoding="utf-8")

    entries = {
        key: (src, label, description)
        for key, src, label, description in re.findall(
            r'"([a-z_0-9]+)": \{ src: "([^"]+)", label: "([^"]+)", description: "([^"]+)" \},',
            catalog,
        )
    }
    assert set(entries) == _WEB_DISCORD_BADGE_KEYS | set(NIKO_BADGE_ORDER)

    niko_block = re.search(r"NIKO_BADGE_KEYS = \[(.*?)\];", catalog, re.S)
    assert niko_block
    assert re.findall(r'"([a-z_]+)"', niko_block.group(1)) == list(NIKO_BADGE_ORDER)
    assert "BOOSTING_TIER_MONTHS = [1, 2, 3, 6, 9, 12, 15, 18, 24]" in catalog
    assert "boosting_${months}_months.svg" in catalog

    for key, (src, label, description) in entries.items():
        assert label and description, key
        # The art is shipped with the web app, and the transcript export inlines
        # the same file under the same key with the same name and description.
        assert (ROOT / "web" / "public" / src.lstrip("/")).exists(), key
        assert key in _PROFILE_BADGE_FILES, f"{key} is missing from the transcript popup"
        assert _PROFILE_BADGE_FILES[key][1] == label, key
        assert _PROFILE_BADGE_FILES[key][2] == description, key
    for months in BOOSTING_TIERS:
        assert f"boosting_{months}_months" in _PROFILE_BADGE_FILES

    # Both web popups own a badge click that opens the art + name + description
    # popup, and the render lab shows every badge through the same component.
    assert "DiscordBadgeList" in markdown
    assert "discord-badge-popup-art" in popup and "discord-badge-popup-copy" in popup
    styles = (ROOT / "web" / "src" / "styles.css").read_text(encoding="utf-8")
    assert "discord-badge-popup" in styles
    # The badge popup is portalled to the page and fixed above the profile
    # popup, so opening one never stretches the profile card to fit it.
    assert "createPortal" in popup and "document.body" in popup
    assert ":has(.discord-badge-popup)" not in styles
    # A click in that floating popup is outside the profile card, so the profile
    # popup has to know about it or every badge click would close the card.
    assert '!target.closest(".discord-badge-popup")' in markdown
    assert "<DiscordBadgeList" in lab and "BADGE_GROUPS" in lab
