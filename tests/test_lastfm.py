"""Last.fm — the client, the store and the listening cards.

These tests never touch the network. The API is replaced by a ``transport``
callable that returns the payload shapes Last.fm actually sends (including its
annoying single-item-as-an-object shape), the database by a pool that records
the SQL it was given, and the artwork downloads by ``None``.
"""

import asyncio
import hashlib
import json
import re
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from cogs.lastfm import _store
from utils.lastfm import api_signature, auth_url
from utils.lastfm.client import LastFmClient, LastFmError, period_label
from utils.image import lastfm_card

from config import links

ROOT = Path(__file__).resolve().parents[1]
LOADING_CARDS_FOLDER = ROOT / "web" / "public" / "assets" / "loading-cards" / "lastfm"


# ── A fake Last.fm ─────────────────────────────────────────────────────────

def _client(payloads, calls=None):
    """A client whose transport answers from ``payloads`` by method name."""

    async def transport(method, params):
        if calls is not None:
            calls.append((method, params))
        reply = payloads[method]
        return reply(params) if callable(reply) else reply

    client = LastFmClient("key", transport=transport)
    client.MIN_INTERVAL = 0  # the tests do not need the rate limiter's sleep
    return client


USER = {
    "user": {
        "name": "soren",
        "realname": "Soren",
        "url": "https://www.last.fm/user/soren",
        "image": [
            {"size": "small", "#text": "https://img/small.png"},
            {"size": "mega", "#text": "https://img/mega.png"},
        ],
        "playcount": "48213",
        "artist_count": "1204",
        "album_count": "3000",
        "track_count": "8932",
        "registered": {"unixtime": "1425168000"},
        "country": "GB",
    }
}


def test_user_info_normalises_numbers_and_images():
    client = _client({"user.getinfo": USER})
    info = asyncio.run(client.user_info("soren"))
    assert info["playcount"] == 48213
    assert info["artist_count"] == 1204
    assert info["image"] == "https://img/mega.png"
    assert info["username"] == "soren"


def test_a_placeholder_cover_is_treated_as_no_artwork():
    payload = {
        "user": {
            **USER["user"],
            "image": [
                {"size": "mega", "#text": "https://lastfm.freetls.fastly.net/i/u/2a96cbd8b46e442fc41c2b86b821562f.png"}
            ],
        }
    }
    client = _client({"user.getinfo": payload})
    assert asyncio.run(client.user_info("soren"))["image"] is None


def test_recent_tracks_separates_now_playing_from_scrobbles():
    payload = {
        "recenttracks": {
            "@attr": {"total": "48213"},
            "track": [
                {
                    "name": "Everything In Its Right Place",
                    "artist": {"#text": "Radiohead"},
                    "album": {"#text": "Kid A"},
                    "image": [{"size": "mega", "#text": "https://img/kida.png"}],
                    "@attr": {"nowplaying": "true"},
                },
                {
                    "name": "Kid A",
                    "artist": {"#text": "Radiohead"},
                    "date": {"uts": "1770000000"},
                },
            ],
        }
    }
    client = _client({"user.getrecenttracks": payload})
    data = asyncio.run(client.recent_tracks("soren"))

    assert data["now_playing"]["title"] == "Everything In Its Right Place"
    assert data["now_playing"]["album"] == "Kid A"
    assert [row["title"] for row in data["tracks"]] == ["Kid A"]
    assert data["tracks"][0]["played_at"] == 1770000000
    assert data["total"] == 48213


def test_a_single_result_sent_as_an_object_is_still_a_row():
    # Last.fm sends ``{"artist": {...}}`` instead of a one-item list, and the
    # artist object itself contains a list (``image``) that must not be read as
    # the rows.
    payload = {
        "topartists": {
            "artist": {
                "name": "Björk",
                "playcount": "2910",
                "image": [{"size": "large", "#text": "https://img/bjork.png"}],
                "@attr": {"rank": "1"},
            }
        }
    }
    client = _client({"user.gettopartists": payload})
    rows = asyncio.run(client.top_artists("soren", limit=1))

    assert len(rows) == 1
    assert rows[0] == {
        "rank": 1,
        "name": "Björk",
        "artist": "",
        "playcount": 2910,
        "image": "https://img/bjork.png",
        "url": "",
    }


def test_artist_info_carries_the_members_own_playcount():
    payload = {
        "artist": {
            "name": "Radiohead",
            "url": "https://www.last.fm/music/Radiohead",
            "image": [{"size": "mega", "#text": "https://img/rh.png"}],
            "stats": {"listeners": "8900000", "playcount": "1200000000"},
            "userplaycount": "4812",
            "tags": {"tag": [{"name": "art rock"}, {"name": "alternative"}]},
            "bio": {"summary": "Radiohead are an English rock band. <a href='x'>Read more</a>"},
        }
    }
    client = _client({"artist.getinfo": payload})
    info = asyncio.run(client.artist_info("radiohead", "soren"))

    assert info["name"] == "Radiohead"
    assert info["user_playcount"] == 4812
    assert info["listeners"] == 8900000
    assert info["tags"] == ["art rock", "alternative"]
    assert info["summary"] == "Radiohead are an English rock band."


def test_album_info_counts_its_tracks():
    payload = {
        "album": {
            "name": "In Rainbows",
            "artist": "Radiohead",
            "image": [{"size": "mega", "#text": "https://img/ir.png"}],
            "playcount": 1234,
            "listeners": 567,
            "userplaycount": "902",
            "tracks": {"track": [{"name": "15 Step"}, {"name": "Bodysnatchers"}]},
        }
    }
    client = _client({"album.getinfo": payload})
    info = asyncio.run(client.album_info("Radiohead", "In Rainbows", "soren"))

    assert info["track_count"] == 2
    assert info["user_playcount"] == 902
    assert info["artist"] == "Radiohead"


def test_lastfm_error_codes_map_to_readable_failures():
    client = _client({"user.getinfo": {"error": 6, "message": "User not found"}})
    with pytest.raises(LastFmError) as caught:
        asyncio.run(client.user_info("nobody"))
    assert caught.value.code == 6
    assert caught.value.unknown_user


def test_a_rate_limit_is_not_retried():
    calls = []
    client = _client({"user.getinfo": {"error": 29, "message": "Rate limit exceeded"}}, calls)
    with pytest.raises(LastFmError):
        asyncio.run(client.user_info("soren"))
    assert len(calls) == 1


def test_answers_are_cached_between_calls():
    calls = []
    client = _client({"user.getinfo": USER}, calls)
    asyncio.run(client.user_info("soren"))
    asyncio.run(client.user_info("soren"))
    assert len(calls) == 1


def test_a_client_without_a_key_says_so_instead_of_calling_out():
    client = LastFmClient("")
    with pytest.raises(LastFmError) as caught:
        asyncio.run(client.user_info("soren"))
    assert "LASTFM_API_KEY" in caught.value.message
    assert not client.has_key


def test_period_labels_are_readable():
    assert period_label("overall") == "All time"
    assert period_label("7day") == "Last 7 days"
    assert period_label("nonsense") == "All time"


# ── Web auth ───────────────────────────────────────────────────────────────

def test_the_api_signature_sorts_the_pairs_and_appends_the_secret():
    import hashlib

    one = api_signature("secret", {"method": "auth.getSession", "api_key": "k", "token": "t"})
    two = api_signature("secret", {"token": "t", "api_key": "k", "method": "auth.getSession"})

    assert one == two
    assert one == hashlib.md5(b"api_keykmethodauth.getSessiontokentsecret").hexdigest()


def test_the_approval_page_carries_the_callback_uri():
    url = auth_url("key", "https://example.com/api/lastfm/callback")
    assert url.startswith("https://www.last.fm/api/auth/?")
    assert "api_key=key" in url
    assert "cb=https%3A%2F%2Fexample.com%2Fapi%2Flastfm%2Fcallback" in url


def test_get_session_signs_the_token_and_returns_the_handle():
    calls = []

    async def transport(method, params):
        calls.append((method, params))
        return {"session": {"name": "soren", "key": "session-key", "subscriber": 1}}

    client = LastFmClient("key", api_secret="secret", transport=transport)
    client.MIN_INTERVAL = 0
    data = asyncio.run(client.get_session("token"))

    assert data["username"] == "soren"
    assert data["session_key"] == "session-key"
    assert data["url"] == "https://www.last.fm/user/soren"
    method, params = calls[0]
    assert method == "auth.getSession"
    assert params["token"] == "token"
    # The signature must cover the key and the method, or Last.fm refuses it.
    assert params["api_sig"] == api_signature(
        "secret", {"api_key": "key", "method": "auth.getSession", "token": "token"}
    )


def test_get_session_needs_the_shared_secret():
    async def transport(method, params):  # never reached
        raise AssertionError("no request should be made")

    client = LastFmClient("key", transport=transport)
    client.MIN_INTERVAL = 0
    assert client.has_secret is False
    with pytest.raises(LastFmError):
        asyncio.run(client.get_session("token"))


def test_an_expired_approval_is_reported_as_such():
    async def transport(method, params):
        return {"error": 14, "message": "Unauthorized Token"}

    client = LastFmClient("key", api_secret="secret", transport=transport)
    client.MIN_INTERVAL = 0
    with pytest.raises(LastFmError) as caught:
        asyncio.run(client.get_session("token"))
    assert caught.value.auth_failed


# ── The guild index ────────────────────────────────────────────────────────

class _Pool:
    """A pool that records statements and answers the one read the index needs."""

    def __init__(self, rows=None, row=None):
        self.rows = rows or []
        self.row = row
        self.executed = []
        self.fetched = []

    async def fetch(self, query, *args):
        self.fetched.append((query, args))
        return self.rows

    async def fetchrow(self, query, *args):
        self.fetched.append((query, args))
        return self.row

    async def execute(self, query, *args):
        self.executed.append((query, args))


def test_artist_keys_fold_case_and_whitespace():
    assert _store.artist_key("  The   Beatles ") == "the beatles"
    assert _store.artist_key("BJÖRK") == "björk"
    assert _store.artist_key("") == ""


def test_indexing_never_lowers_a_stored_playcount():
    pool = _Pool(rows=[{"artist_key": "radiohead", "playcount": 500}])
    written = asyncio.run(
        _store.index_artists(
            pool, 1, 2, [("Radiohead", 20), ("Björk", 30)]
        )
    )

    # A "last 7 days" overview must not overwrite an all-time number.
    assert written == 1
    assert len(pool.executed) == 1
    assert "Björk" in pool.executed[0][1]


def test_indexing_raises_a_count_when_the_member_listened_more():
    pool = _Pool(rows=[{"artist_key": "radiohead", "playcount": 500}])
    asyncio.run(_store.index_artists(pool, 1, 2, [("Radiohead", 900)]))
    assert len(pool.executed) == 1
    assert 900 in pool.executed[0][1]


def test_an_approval_stores_the_session_key_and_a_typed_link_keeps_it():
    pool = _Pool()
    asyncio.run(_store.set_account(pool, 1, "soren", session_key="abc123"))
    query, args = pool.executed[0]
    assert "session_key" in query
    assert "abc123" in args

    # Typing a handle does not prove ownership, so it must not erase the proof
    # an earlier approval stored.
    asyncio.run(_store.set_account(pool, 1, "soren"))
    assert "session_key" not in pool.executed[1][0]


def test_typing_a_different_handle_drops_the_old_approval():
    # The approval described "old"; keeping its key would attach a session for
    # one Last.fm account to a row that now names another.
    pool = _Pool(row={"user_id": 1, "username": "Old", "session_key": "abc"})
    asyncio.run(_store.set_account(pool, 1, "new"))
    assert any("session_key = NULL" in query for query, _ in pool.executed)

    # The same handle in different casing is the same account: keep it.
    same = _Pool(row={"user_id": 1, "username": "Soren", "session_key": "abc"})
    asyncio.run(_store.set_account(same, 1, "soren"))
    assert not any("NULL" in query for query, _ in same.executed)


def test_a_dm_has_no_index_to_write_to():
    pool = _Pool()
    assert asyncio.run(_store.index_artists(pool, None, 2, [("Radiohead", 20)])) == 0
    assert pool.executed == []


def test_crowns_need_two_listeners_and_go_to_the_top_one():
    rows = [
        {"artist_key": "radiohead", "artist_name": "Radiohead", "user_id": 1, "playcount": 900},
        {"artist_key": "radiohead", "artist_name": "Radiohead", "user_id": 2, "playcount": 400},
        {"artist_key": "bjork", "artist_name": "Björk", "user_id": 2, "playcount": 30},
    ]
    held = _store.crowns(rows)

    assert held[1][0]["artist"] == "Radiohead"
    assert held[1][0]["lead"] == 500
    assert held[1][0]["runner_up_id"] == 2
    # One listener is not a crown.
    assert 2 not in held


def test_crowns_of_one_member_are_ordered_by_plays():
    rows = [
        {"artist_key": "a", "artist_name": "A", "user_id": 1, "playcount": 10},
        {"artist_key": "a", "artist_name": "A", "user_id": 2, "playcount": 5},
        {"artist_key": "b", "artist_name": "B", "user_id": 1, "playcount": 40},
        {"artist_key": "b", "artist_name": "B", "user_id": 2, "playcount": 7},
    ]
    held = _store.crowns(rows)
    assert [crown["artist"] for crown in held[1]] == ["B", "A"]


# ── Cards ──────────────────────────────────────────────────────────────────

def _png_size(buffer):
    from PIL import Image

    buffer.seek(0)
    with Image.open(buffer) as image:
        return image.size, image.mode


def test_the_overview_card_has_the_documented_shape():
    buffer = asyncio.run(
        lastfm_card.render_overview_card(
            avatar_bytes=None,
            display_name="soren",
            handle="@soren",
            period="All time",
            scrobbles=48213,
            artists=[{"rank": 1, "name": "Radiohead", "value": "4,812"}],
            albums=[{"rank": 1, "name": "In Rainbows", "subtitle": "Radiohead", "value": "902"}],
            tracks=[{"rank": 1, "name": "Weird Fishes", "subtitle": "Radiohead", "value": "210"}],
        )
    )
    size, mode = _png_size(buffer)
    assert size == (lastfm_card.OVERVIEW_W, lastfm_card.OVERVIEW_H)
    # The rounded corners have to stay transparent, or Discord shows black.
    assert mode == "RGBA"


def test_a_long_artist_name_stays_inside_the_card():
    buffer = asyncio.run(
        lastfm_card.render_detail_card(
            image_bytes=None,
            kind="Artist",
            title="The Very Long Artist Name That Would Otherwise Overflow The Card Edge Forever",
            subtitle="a subtitle that is also rather long and should be clipped nicely",
            playcount=12,
            chips=[("listeners", "8.9M"), ("scrobbles", "1.2B")],
        )
    )
    assert _png_size(buffer)[0] == (lastfm_card.DETAIL_W, lastfm_card.DETAIL_H)


def test_a_board_grows_with_its_rows():
    few = asyncio.run(lastfm_card.render_board_card(title="Who knows", entries=[]))
    many = asyncio.run(
        lastfm_card.render_board_card(
            title="Who knows",
            entries=[{"rank": i + 1, "name": f"member {i}", "value": str(10 - i), "bar": 10 - i} for i in range(6)],
        )
    )
    assert _png_size(few)[0][1] == lastfm_card.board_height(1)
    assert _png_size(many)[0][1] == lastfm_card.board_height(6)
    assert _png_size(many)[0][0] == lastfm_card.BOARD_W


def _avatar_png(colour, size=256):
    from io import BytesIO

    from PIL import Image

    buffer = BytesIO()
    Image.new("RGB", (size, size), colour).save(buffer, format="PNG")
    return buffer.getvalue()


def test_the_board_bar_never_runs_through_a_listener_avatar():
    """The proportion bar sits below the avatar, not across the bottom of it.

    Whitelist boards (``whoknows``) put a 44px circle in every row, and the bar
    used to be drawn two pixels inside that circle.
    """
    buffer = asyncio.run(
        lastfm_card.render_board_card(
            title="Who knows Radiohead",
            entries=[{"rank": 1, "name": "soren", "value": "12", "bar": 12, "avatar": _avatar_png((0, 255, 0))}],
            show_images=False,
        )
    )
    assert _png_size(buffer)[0][0] == lastfm_card.BOARD_W

    from PIL import Image

    buffer.seek(0)
    with Image.open(buffer) as image:
        card = image.convert("RGBA")

    row_y = lastfm_card.BOARD_HEADER_H
    media_top = row_y + lastfm_card.BOARD_MEDIA_Y
    media_bottom = media_top + lastfm_card.BOARD_MEDIA - 1
    bar_top = row_y + lastfm_card.BOARD_BAR_Y
    bar_bottom = bar_top + lastfm_card.BOARD_BAR_H - 1
    centre = lastfm_card.PAD + 74 + lastfm_card.BOARD_MEDIA // 2

    def is_avatar(y):
        red, green, _blue, _alpha = card.getpixel((centre, y))
        return green > 200 and red < 60

    assert is_avatar(media_top + 6), "the avatar should be drawn in its band"
    assert is_avatar(media_bottom - 6)
    assert not any(is_avatar(y) for y in range(media_bottom, bar_bottom + 1))
    assert bar_top >= media_bottom, "the bar must start at or below the avatar"
    # The bar is still there, inside the row panel rather than on its edge.
    assert card.getpixel((lastfm_card.PAD + 40, bar_top))[0] > 150
    assert bar_bottom <= row_y + lastfm_card.BOARD_ROW_H - 10


def test_the_masthead_carries_the_site_wordmark():
    # The lockup ships as a site SVG, so a missing file would silently fall back
    # to the icon tile and no one would notice the brand had quietly changed.
    assert any(path.is_file() for path in lastfm_card._WORDMARK_SVG)

    mark = lastfm_card._wordmark()
    assert mark is not None
    assert mark.height == lastfm_card.WORDMARK_H
    # A 360:91 lockup: the header is wider than it is tall, not a square badge.
    assert mark.width > mark.height * 3

    histogram = mark.getchannel("A").histogram()
    coverage = sum(histogram[201:]) / (mark.width * mark.height)
    assert 0.15 < coverage < 0.6


def test_the_fallback_header_tile_is_the_brand_red():
    assert lastfm_card._LOGO_ASSET.is_file()

    pixels = lastfm_card._logo(30).load()
    red = sum(
        1
        for x in range(30)
        for y in range(30)
        if pixels[x, y][0] > 170 and pixels[x, y][1] < 90
    )
    assert red > 100


def test_the_now_playing_card_has_the_documented_shape():
    buffer = asyncio.run(
        lastfm_card.render_now_playing_card(
            image_bytes=None,
            title="Weird Fishes / Arpeggi",
            artist="Radiohead",
            album="In Rainbows",
            live=True,
            handle="soren",
            footer="Soren · scrobbling right now",
        )
    )
    size, mode = _png_size(buffer)
    assert size == (lastfm_card.NOW_W, lastfm_card.NOW_H)
    assert mode == "RGBA"


def test_nothing_playing_still_draws_a_card():
    buffer = asyncio.run(
        lastfm_card.render_now_playing_card(
            image_bytes=None,
            title="",
            artist="",
            empty_text="Nothing playing, and no scrobbles yet.",
        )
    )
    assert _png_size(buffer)[0] == (lastfm_card.NOW_W, lastfm_card.NOW_H)


def test_the_recent_card_marks_the_now_playing_row():
    buffer = asyncio.run(
        lastfm_card.render_recent_card(
            avatar_bytes=None,
            display_name="soren",
            handle="@soren",
            entries=[
                {"title": "Kid A", "subtitle": "Radiohead", "when": "now", "now_playing": True},
                {"title": "15 Step", "subtitle": "Radiohead", "when": "4m ago"},
            ],
        )
    )
    assert _png_size(buffer)[0][0] == lastfm_card.RECENT_W


# ── The cog ────────────────────────────────────────────────────────────────

class _Member:
    def __init__(self, user_id=1, name="Soren", guild_id=7):
        self.id = user_id
        self.display_name = name
        self.guild = types.SimpleNamespace(id=guild_id)
        self.display_avatar = types.SimpleNamespace(url="https://cdn/avatar.png")


def _select_row(view):
    """The action row holding the period picker (a select must sit alone)."""
    import discord

    for row in view.children[0].children:
        children = getattr(row, "children", [])
        if any(isinstance(child, discord.ui.Select) for child in children):
            return row
    raise AssertionError("the card has no period picker")


def _cog(pool, payloads):
    from cogs.lastfm.cog import LastfmCog

    cog = LastfmCog(bot=types.SimpleNamespace(cxn=pool))
    cog.client = _client(payloads)
    return cog


def _overview_payloads():
    ordered = {
        "user.getinfo": USER,
        "user.getrecenttracks": {
            "recenttracks": {
                "track": [
                    {"name": "Kid A", "artist": {"#text": "Radiohead"}, "date": {"uts": "1770000000"}},
                ]
            }
        },
        "user.gettopartists": {
            "topartists": {
                "artist": [
                    {"name": "Radiohead", "playcount": "4812", "@attr": {"rank": "1"}},
                    {"name": "Björk", "playcount": "2910", "@attr": {"rank": "2"}},
                ]
            }
        },
        "user.gettopalbums": {
            "topalbums": {"album": [{"name": "In Rainbows", "artist": {"name": "Radiohead"}, "playcount": "902"}]}
        },
        "user.gettoptracks": {
            "toptracks": {"track": [{"name": "Weird Fishes", "artist": {"name": "Radiohead"}, "playcount": "210"}]}
        },
    }
    return ordered


def test_the_overview_renders_a_card_and_indexes_what_it_saw(monkeypatch):
    import cogs.lastfm.cog as cog_module

    async def no_artwork(url, size=256):
        return None

    monkeypatch.setattr(cog_module, "fetch_avatar_bytes", no_artwork)

    pool = _Pool(row={"username": "soren", "checked_at": 1})
    cog = _cog(pool, _overview_payloads())
    view, file = asyncio.run(cog.render_card("overview", _Member(), "6month"))

    assert file.filename == cog_module.CARD_FILE
    gallery = view.children[0].children[0]
    assert str(gallery.items[0].media.url) == f"attachment://{cog_module.CARD_FILE}"

    # The period picker is its own action row, as Discord requires for selects.
    select_row = _select_row(view)
    assert select_row.children[0].placeholder == "Change the time period"
    assert len(select_row.children) == 1

    # The artists the member just paid for are now queryable in their server.
    indexed = [args for query, args in pool.executed if "lastfm_artist_index" in query]
    assert indexed, "the overview should index the member's top artists"
    assert any("Radiohead" in args for args in indexed)


def test_a_period_switch_re_renders_the_card(monkeypatch):
    import cogs.lastfm.cog as cog_module

    async def no_artwork(url, size=256):
        return None

    monkeypatch.setattr(cog_module, "fetch_avatar_bytes", no_artwork)

    pool = _Pool(row={"username": "soren", "checked_at": 1})
    cog = _cog(pool, _overview_payloads())
    view, _ = asyncio.run(cog.render_card("overview", _Member(), "overall"))
    select = _select_row(view).children[0]

    class _Response:
        def __init__(self):
            self.deferred = False

        async def defer(self):
            self.deferred = True

    class _Interaction:
        def __init__(self):
            self.response = _Response()
            self.edited = None

        async def edit_original_response(self, **kwargs):
            self.edited = kwargs

    select._values = ["7day"]
    interaction = _Interaction()
    asyncio.run(select.callback(interaction))

    assert interaction.response.deferred
    assert interaction.edited["attachments"][0].filename == cog_module.CARD_FILE
    assert str(
        interaction.edited["view"].children[0].children[0].items[0].media.url
    ) == f"attachment://{cog_module.CARD_FILE}"


def _error_text(cog, exc, **kwargs):
    view = cog.error_view(_Ctx(_Member()), exc, **kwargs)
    return view.children[0].children[0].content


def test_a_missing_key_answers_with_a_configuration_notice():
    from cogs.lastfm.cog import LastfmCog

    cog = LastfmCog(bot=types.SimpleNamespace(cxn=_Pool()))
    cog.client = LastFmClient("")
    assert "LASTFM_API_KEY" in _error_text(cog, LastFmError("missing key"))


def test_an_unknown_account_gets_its_own_notice():
    from cogs.lastfm.cog import LastfmCog

    cog = LastfmCog(bot=types.SimpleNamespace(cxn=_Pool()))
    text = _error_text(cog, LastFmError("User not found", code=6))
    assert "couldn't find that account" in text


def test_unknown_answers_name_what_the_member_asked_for():
    """Code 6 covers a bad handle, artist and album — each needs a different fix."""
    cog = _cog(_Pool(), {})

    account = _error_text(cog, LastFmError("Invalid username", code=6), kind="account")
    artist = _error_text(cog, LastFmError("Invalid artist", code=6), kind="artist")
    album = _error_text(cog, LastFmError("Invalid album", code=6), kind="album")

    assert "/fm link" in account and "renamed or deleted" in account
    assert "artist by that name" in artist
    assert "doesn't know that album" in album
    # The API's own text is a log line, not something a member can act on.
    for text in (account, artist, album):
        assert "Invalid" not in text


def test_each_failure_gets_copy_that_matches_what_went_wrong():
    cog = _cog(_Pool(), {})

    busy = _error_text(cog, LastFmError("slow down", code=29))
    unreachable = _error_text(cog, LastFmError("Last.fm did not answer (ClientConnectorError)"))
    refused = _error_text(cog, LastFmError("Operation failed", code=8))
    unexpected = _error_text(cog, ValueError("boom"))

    assert "rate limiting" in busy
    assert "isn't answering" in unreachable
    assert "turned that request down" in refused
    assert "on us, not on you" in unexpected
    # Raw transport details stay in the log instead of the member's message.
    for text in (unreachable, refused, unexpected):
        assert "ClientConnectorError" not in text
        assert "boom" not in text
        assert "Operation failed" not in text


def test_copies_use_the_bots_own_emoji_instead_of_discords():
    """Notices carry the configured emoji, not Discord's stock ❌/✅/⚙️/⏳."""
    import cogs.lastfm.cog as cog_module
    from config.emojis import get_emoji

    stock = "❌✅⚙⏳"
    for language in ("en", "de", "es", "fr"):
        copy = json.loads(
            (ROOT / "src" / "cogs" / "lastfm" / "locales" / f"{language}.json")
            .read_text(encoding="utf-8")
        )["lastfm"]
        for key, text in copy.items():
            assert not any(char in text for char in stock), f"{language}/{key} keeps a stock emoji"

    # The render substitutes the catalogues' tokens with the live emoji strings.
    assert cog_module.msg(None, "unlinked").startswith(get_emoji("tick"))
    assert cog_module.msg(None, "need_artist").startswith(get_emoji("cross"))
    assert cog_module.msg(None, "err_busy").startswith(get_emoji("warning"))
    assert cog_module.msg(None, "err_key").startswith(get_emoji("settings"))


def test_notice_copy_links_the_command_instead_of_inline_code():
    """Messages carry ``</fm artist:id>`` chips; the catalogues stay readable."""
    from utils import command_ids

    names = ("fm", "fm link", "fm artist", "fm album", "fm chart", "fm taste")
    command_ids.remember({name: 900 + index for index, name in enumerate(names)})
    keys = ("fm_link_usage", "need_artist", "need_album", "chart_usage", "taste_self")
    try:
        cog = _cog(_Pool(), {})
        for language in ("en", "de", "es", "fr"):
            copy = json.loads(
                (ROOT / "src" / "cogs" / "lastfm" / "locales" / f"{language}.json")
                .read_text(encoding="utf-8")
            )["lastfm"]
            for key in keys:
                content = cog.notice_view(copy[key]).children[0].children[0].content
                assert "`/" not in content, f"{language}/{key} still renders inline code"
        album = cog.notice_view(copy["need_album"]).children[0].children[0].content
        assert "</fm album:" in album
        assert "Radiohead - In Rainbows" in album
    finally:
        command_ids.remember({})


# ── Command wiring ─────────────────────────────────────────────────────────

class _SentMessage:
    def __init__(self, kwargs, created_at=None):
        self.kwargs = kwargs
        self.edited = None
        # The real message carries a snowflake timestamp; ``None`` here keeps a
        # command test from waiting out the placeholder's minimum on-screen time.
        self.created_at = created_at

    async def edit(self, **kwargs):
        self.edited = kwargs
        return self


class _Ctx:
    """A prefix-command context: no interaction, messages are sent directly."""

    interaction = None

    def __init__(self, member, guild_id=7):
        self.author = member
        self.guild = types.SimpleNamespace(id=guild_id)
        self.sent = []

    async def send(self, **kwargs):
        message = _SentMessage(kwargs)
        self.sent.append(message)
        return message


def _now_playing_payloads():
    return {
        "user.getrecenttracks": {
            "recenttracks": {
                "track": [
                    {
                        "name": "Kid A",
                        "artist": {"#text": "Radiohead"},
                        "album": {"#text": "Kid A"},
                        "image": [{"size": "mega", "#text": "https://img/kida.png"}],
                        "@attr": {"nowplaying": "true"},
                        "url": "https://www.last.fm/music/Radiohead/_/Kid+A",
                    }
                ],
                "@attr": {"total": "48213"},
            }
        }
    }


def test_dot_fm_answers_with_now_playing_behind_a_loading_card(monkeypatch):
    import cogs.lastfm.cog as cog_module

    async def no_artwork(url, size=256):
        return None

    monkeypatch.setattr(cog_module, "fetch_avatar_bytes", no_artwork)

    pool = _Pool(row={"username": "soren", "checked_at": 1})
    cog = _cog(pool, _now_playing_payloads())
    ctx = _Ctx(_Member())

    asyncio.run(cog.fm.callback(cog, ctx, None))

    # The placeholder goes up first, so a slow artwork download never leaves the
    # member looking at a bare "thinking" state.
    loading = ctx.sent[0]
    media = loading.kwargs["view"].children[0].children[0].items[0].media.url
    # The placeholder is a remote GIF, cached by Discord's proxy by URL — so the
    # URL carries the same ?hash= anti-cache suffix the Spotify card uses.
    assert re.search(
        r"/assets/loading-cards/lastfm/nowplaying\.gif\?hash=[0-9a-f]{8}$", str(media)
    ), media

    # ...and the finished card edits that same message.
    final = loading.edited
    assert final["attachments"][0].filename == cog_module.CARD_FILE
    assert str(
        final["view"].children[0].children[0].items[0].media.url
    ) == f"attachment://{cog_module.CARD_FILE}"


def _hashed_loading_url(file_name: str, base: str = f"{links.WEBSITE}/assets/loading-cards") -> str:
    """The URL a placeholder should carry: origin, path and the GIF's hash."""
    digest = hashlib.sha256((LOADING_CARDS_FOLDER / file_name).read_bytes()).hexdigest()[:8]
    return f"{base}/lastfm/{file_name}?hash={digest}"


def test_every_lastfm_loading_shape_carries_the_asset_hash(monkeypatch):
    """A regenerated placeholder has to be a new URL, exactly as for Spotify."""
    import cogs.lastfm.cog as cog_module

    monkeypatch.delenv("PUBLIC_URL", raising=False)

    for card, file_name in sorted(cog_module.LOADING_CARD_FILES.items()):
        view = cog_module._loading_view(card)
        path = LOADING_CARDS_FOLDER / file_name
        assert path.is_file(), f"{path} is missing — run scripts/generate_lastfm_loading_cards.py"
        url = str(view.children[0].children[0].items[0].media.url)
        assert url == _hashed_loading_url(file_name), card


def test_the_server_boards_wait_on_the_chart_placeholder(monkeypatch):
    """There is one GIF per shape, so the ten-row boards reuse the chart one."""
    import cogs.lastfm.cog as cog_module

    monkeypatch.setenv("PUBLIC_URL", "https://beta.example.com/")

    board = cog_module._loading_view("board")
    assert str(board.children[0].children[0].items[0].media.url) == _hashed_loading_url(
        "chart.gif", base="https://beta.example.com/assets/loading-cards"
    )


def test_unknown_lastfm_loading_shapes_show_no_placeholder():
    import cogs.lastfm.cog as cog_module

    assert cog_module._loading_view("taste") is None


def _fm_with_a_placeholder_created_at(monkeypatch, created_at):
    """Run ``.fm`` once, with the placeholder stamped as *created_at*."""
    import cogs.lastfm.cog as cog_module

    async def no_artwork(url, size=256):
        return None

    monkeypatch.setattr(cog_module, "fetch_avatar_bytes", no_artwork)

    waits = []

    async def record_wait(seconds):
        waits.append(seconds)

    monkeypatch.setattr(cog_module, "_wait", record_wait)

    pool = _Pool(row={"username": "soren", "checked_at": 1})
    cog = _cog(pool, _now_playing_payloads())
    ctx = _Ctx(_Member())

    async def send(**kwargs):
        message = _SentMessage(kwargs, created_at=created_at)
        ctx.sent.append(message)
        return message

    ctx.send = send
    asyncio.run(cog.fm.callback(cog, ctx, None))
    return waits, ctx.sent[0]


def test_a_fast_render_waits_out_the_placeholder_before_editing(monkeypatch):
    """Two edits fired back to back can land in either order, so space them."""
    import cogs.lastfm.cog as cog_module

    waits, loading = _fm_with_a_placeholder_created_at(
        monkeypatch, datetime.now(timezone.utc)
    )

    assert waits, "a render this fast must not edit straight over the placeholder"
    assert 0 < waits[0] <= cog_module.PLACEHOLDER_MIN_SECONDS
    # ...and the card still lands, on that same message.
    assert loading.edited["attachments"][0].filename == cog_module.CARD_FILE


def test_a_slow_render_edits_straight_away(monkeypatch):
    """A placeholder that has already been up never delays the card."""
    waits, loading = _fm_with_a_placeholder_created_at(
        monkeypatch, datetime.now(timezone.utc) - timedelta(seconds=5)
    )

    assert waits == []
    assert loading.edited is not None


def test_an_unknown_placeholder_age_does_not_block_the_card(monkeypatch):
    waits, loading = _fm_with_a_placeholder_created_at(monkeypatch, None)

    assert waits == []
    assert loading.edited is not None


class _Interaction:
    """A slash interaction: the original response is its only surface."""

    def __init__(self, created_at=None):
        self.deferred = False
        self.responded = []
        self.original = []
        self._created_at = created_at

    @property
    def response(self):
        return self

    def is_done(self):
        return self.deferred

    async def defer(self):
        self.deferred = True

    async def send_message(self, **kwargs):
        # The initial response, spent on a view instead of Discord's "thinking"
        # bubble; the message it creates is what ``edit_original_response``
        # later targets.
        self.responded.append(kwargs)
        self.deferred = True
        return _SentMessage(kwargs, created_at=self._created_at)

    async def edit_original_response(self, **kwargs):
        self.original.append(kwargs)
        return _SentMessage(kwargs, created_at=self._created_at)


class _SlashCtx:
    """A slash-command context: it must never post a message of its own."""

    def __init__(self, member, created_at=None, guild_id=7):
        self.author = member
        self.guild = types.SimpleNamespace(id=guild_id)
        self.sent = []
        self.interaction = _Interaction(created_at)

    async def send(self, **kwargs):
        message = _SentMessage(kwargs)
        self.sent.append(message)
        return message


def test_a_slash_command_swaps_the_placeholder_on_the_same_route(monkeypatch):
    """Both halves edit @original, so the card cannot be applied out of order."""
    import cogs.lastfm.cog as cog_module

    async def no_artwork(url, size=256):
        return None

    async def no_wait(seconds):
        return None

    monkeypatch.setattr(cog_module, "fetch_avatar_bytes", no_artwork)
    monkeypatch.setattr(cog_module, "_wait", no_wait)

    pool = _Pool(row={"username": "soren", "checked_at": 1})
    cog = _cog(pool, _now_playing_payloads())
    ctx = _SlashCtx(_Member(), created_at=datetime.now(timezone.utc))

    asyncio.run(cog.fm_nowplaying.callback(cog, ctx, None))

    assert ctx.sent == [], "a slash command should only edit its deferred reply"
    assert len(ctx.interaction.original) == 2
    placeholder = (
        ctx.interaction.original[0]["view"].children[0].children[0].items[0].media.url
    )
    assert "/assets/loading-cards/lastfm/nowplaying.gif" in str(placeholder)
    card = ctx.interaction.original[1]["attachments"][0]
    assert card.filename == cog_module.CARD_FILE
    # The card is not kept after it is sent: the PNG stream is closed, so the
    # listing's megabytes go back to the host instead of waiting on a GC pass.
    assert card.fp.closed


def test_fm_recent_hands_the_card_downloaded_album_artwork(monkeypatch):
    import cogs.lastfm.cog as cog_module

    requested = []

    async def fake_bytes(url, size=300):
        requested.append(url)
        return b"sleeve"

    captured = {}

    async def capture_card(**kwargs):
        captured.update(kwargs)
        from io import BytesIO

        return BytesIO(b"png")

    monkeypatch.setattr(cog_module, "fetch_avatar_bytes", fake_bytes)
    monkeypatch.setattr(cog_module.lastfm_card, "render_recent_card", capture_card)

    payload = {
        "user.getrecenttracks": {
            "recenttracks": {
                "track": [
                    {
                        "name": "Kid A",
                        "artist": {"#text": "Radiohead"},
                        "image": [{"size": "mega", "#text": "https://img/kid-a.png"}],
                        "@attr": {"nowplaying": "true"},
                    },
                    {
                        "name": "15 Step",
                        "artist": {"#text": "Radiohead"},
                        "image": [{"size": "mega", "#text": "https://img/15-step.png"}],
                        "date": {"uts": "1770000000"},
                    },
                ],
                "@attr": {"total": "48213"},
            }
        }
    }
    cog = _cog(_Pool(row={"username": "soren", "checked_at": 1}), payload)
    ctx = _Ctx(_Member())

    asyncio.run(cog.fm_recent.callback(cog, ctx, None))

    # Every row carries downloaded bytes, not the URL the API handed back.
    entries = captured["entries"]
    assert len(entries) == 2
    assert [entry["image"] for entry in entries] == [b"sleeve", b"sleeve"]
    assert "https://img/kid-a.png" in requested
    assert "https://img/15-step.png" in requested


def test_slash_commands_get_nowplaying_and_overview_beside_dot_fm():
    cog = _cog(_Pool(), {})

    names = {command.name for command in cog.fm.commands}
    # Discord does not register a group with subcommands as a slash command, so
    # the now-playing card needs a subcommand of its own.
    assert {"nowplaying", "overview", "artist", "album", "recent", "chart"} <= names


def _link_button(view):
    """The connect button, wherever the container puts its row."""
    import discord

    for child in view.children[0].children:
        for item in getattr(child, "children", []):
            if isinstance(item, discord.ui.Button):
                return item
    raise AssertionError("the link view has no button")


def _link_body(view) -> str:
    return "\n".join(
        child.content
        for child in view.children[0].children
        if isinstance(getattr(child, "content", None), str)
    )


def test_link_offers_the_website_approval_button():
    cog = _cog(_Pool(), {})
    cog.client.api_secret = "secret"

    view = cog._link_view(_Ctx(_Member()))
    button = _link_button(view)
    assert button.url.endswith("/api/lastfm/link")
    assert button.style is __import__("discord").ButtonStyle.link
    assert button.label == "Connect Last.fm"
    # The button wears Niko's Last.fm mark, like the rest of the bot's panels.
    assert button.emoji.name == "lastfm"

    # The message says what linking does, how, and what is stored — before the
    # member has to press anything.
    body = _link_body(view)
    assert "Link your Last.fm account" in body
    assert "every player counts" in body
    assert "No password" in body
    assert "/fm unlink" in body


def test_an_already_linked_member_is_told_which_account_and_offered_a_reconnect():
    pool = _Pool(row={"username": "soren", "checked_at": 1})
    cog = _cog(pool, {})
    cog.client.api_secret = "secret"
    ctx = _Ctx(_Member())

    asyncio.run(cog.fm_link.callback(cog, ctx))

    view = ctx.sent[0].kwargs["view"]
    body = _link_body(view)
    assert "@soren" in body
    assert "Reconnecting" in body
    assert "/fm unlink" in body
    assert _link_button(view).label == "Reconnect Last.fm"


def test_link_and_unlink_replace_set_and_unset():
    cog = _cog(_Pool(), {})

    names = {command.name: command for command in cog.fm.commands}
    assert {"link", "unlink"} <= set(names)
    assert {"set", "unset"}.isdisjoint(names)
    # Last.fm names the account in the approval, so there is no username to pass.
    assert names["link"].clean_params == {}
    assert names["unlink"].clean_params == {}


def test_link_explains_a_missing_shared_secret():
    """Without the secret the approval cannot be exchanged, and nothing types a handle."""
    cog = _cog(_Pool(), {})
    cog.client.api_secret = ""

    view = cog._link_view(_Ctx(_Member()))
    assert "LASTFM_API_SECRET" in view.children[0].children[0].content


def test_unlink_without_a_link_says_there_is_nothing_to_unlink():
    pool = _Pool()
    cog = _cog(pool, {})
    ctx = _Ctx(_Member())

    asyncio.run(cog.fm_unlink.callback(cog, ctx))

    text = ctx.sent[0].kwargs["view"].children[0].children[0].content
    assert "nothing to unlink" in text
    assert "/fm link" in text
    # Claiming success would be a lie, and a DELETE would invent the work.
    assert "Unlinked" not in text
    assert not pool.executed


def test_unlink_confirms_the_handle_it_removed():
    pool = _Pool(row={"username": "soren", "checked_at": 1})
    cog = _cog(pool, {})
    ctx = _Ctx(_Member())

    asyncio.run(cog.fm_unlink.callback(cog, ctx))

    text = ctx.sent[0].kwargs["view"].children[0].children[0].content
    assert "@soren" in text
    # The member is told what actually happened: the key is gone, the plays and
    # the server's existing boards are not.
    assert "session key" in text
    assert "boards keep" in text
    assert "/fm link" in text
    assert any("DELETE FROM lastfm_users" in query for query, _ in pool.executed)


def _top_artists_payload(artists):
    return {
        "topartists": {
            "artist": [
                {"name": name, "playcount": str(plays), "@attr": {"rank": str(rank)}}
                for rank, (name, plays) in enumerate(artists, start=1)
            ]
        }
    }


def _update_client(pages):
    """A Last.fm client whose top-artists pages are answered from *pages*."""

    def answer(params):
        page = int(params.get("page") or 1)
        return _top_artists_payload(pages[page] if page in pages else [])

    return _client({"user.gettopartists": answer})


def test_update_answers_at_once_and_edits_that_same_message():
    """.fm update reads two Last.fm pages, so the reply is the notice itself."""
    pool = _Pool(row={"username": "soren", "checked_at": 1})
    cog = _cog(pool, {})
    cog.client = _update_client({
        1: [("Radiohead", 900), ("Björk", 400)],
        2: [("Portishead", 120)],
    })
    ctx = _Ctx(_Member())

    asyncio.run(cog.fm_update.callback(cog, ctx))

    # One message: the notice goes up before the crawl and is edited into the
    # result, rather than the member waiting on silence for two round trips.
    assert len(ctx.sent) == 1
    message = ctx.sent[0]
    assert "Reading your top artists" in message.kwargs["view"].children[0].children[0].content
    assert message.edited is not None
    text = message.edited["view"].children[0].children[0].content
    assert "3" in text and "@soren" in text
    assert "Updated" in text


def test_update_says_the_index_is_already_current():
    """A repeat run writes nothing; \"Updated 0 artists\" would read as a failure."""
    pool = _Pool(
        row={"username": "soren", "checked_at": 1},
        rows=[{"artist_key": "radiohead", "playcount": 900}],
    )
    cog = _cog(pool, {})
    cog.client = _update_client({1: [("Radiohead", 900)]})
    ctx = _Ctx(_Member())

    asyncio.run(cog.fm_update.callback(cog, ctx))

    text = ctx.sent[0].edited["view"].children[0].children[0].content
    assert "Nothing to update" in text
    assert "1" in text and "@soren" in text
    assert not pool.executed


def test_update_says_there_is_nothing_to_index_for_an_empty_library():
    """No rows is not "everything is up to date" — there is nothing to be up to date about."""
    pool = _Pool(row={"username": "soren", "checked_at": 1})
    cog = _cog(pool, {})
    cog.client = _update_client({})
    ctx = _Ctx(_Member())

    asyncio.run(cog.fm_update.callback(cog, ctx))

    text = ctx.sent[0].edited["view"].children[0].children[0].content
    assert "Nothing to index yet" in text
    assert "@soren" in text
    assert not pool.executed


def test_a_slash_update_answers_with_the_notice_instead_of_a_bare_defer():
    pool = _Pool(row={"username": "soren", "checked_at": 1})
    cog = _cog(pool, {})
    cog.client = _update_client({1: [("Radiohead", 900)]})
    ctx = _SlashCtx(_Member())

    asyncio.run(cog.fm_update.callback(cog, ctx))

    # ``send_message`` spends the initial response on the notice, so the member
    # sees it immediately; everything afterwards edits that same response.
    assert len(ctx.interaction.responded) == 1
    assert "Reading your top artists" in (
        ctx.interaction.responded[0]["view"].children[0].children[0].content
    )
    assert ctx.sent == []
    final = ctx.interaction.original[-1]
    assert "Updated" in final["view"].children[0].children[0].content


def test_update_checks_the_link_before_it_promises_to_index():
    """No link means no crawl, so the member is told that instead of a notice."""
    pool = _Pool()
    cog = _cog(pool, {})
    ctx = _Ctx(_Member())

    asyncio.run(cog.fm_update.callback(cog, ctx))

    text = ctx.sent[0].kwargs["view"].children[0].children[0].content
    assert "/fm link" in text
    assert "Reading your top artists" not in text
    assert ctx.sent[0].edited is None


def test_update_reports_the_error_over_the_notice_it_already_posted():
    pool = _Pool(row={"username": "soren", "checked_at": 1})
    cog = _cog(pool, {})

    async def boom(*args, **kwargs):
        raise LastFmError("No such user", code=6)

    cog.client.top_artists = boom
    ctx = _Ctx(_Member())

    asyncio.run(cog.fm_update.callback(cog, ctx))

    # The notice that was already on screen becomes the error: no second message,
    # no placeholder left sitting there with the spinner.
    assert len(ctx.sent) == 1
    text = ctx.sent[0].edited["view"].children[0].children[0].content
    assert "Reading your top artists" not in text
    assert "doesn't recognise the linked account" in text
    assert "/fm link" in text
