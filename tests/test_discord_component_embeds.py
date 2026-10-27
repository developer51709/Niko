"""Discord Components V2 link embeds on the public website.

Discord renders a component embed from a JSON payload in the server-rendered
``<head>``: one top-level Container (type 17) holding text displays, an image, a
separator, and a row of link buttons. The payload is capped at 3,000 bytes, and
Discord discards an over-limit payload entirely — falling back to the plain Open
Graph card and losing the buttons.

The payload used to be baked into one HTML file per route by the website build.
It is rendered per request now (``src/webapp/social_preview.py``), so these tests
drive that renderer over the page list the build writes to
``src/website/dist/social-pages.json`` — the same input the running site uses —
and check the markup that ships. Shapes that must not regress: the page
information above the image, the generated Open Graph image in the embed, and the
invite / commands / support button row below it.
See https://docs.discord.com/developers/link-previews/component-embeds
"""

import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "src" / "website" / "dist"
MANIFEST = DIST / "social-pages.json"
SHELL = DIST / "index.html"
sys.path.insert(0, str(ROOT / "src"))

from webapp import social_preview  # noqa: E402

EMBED_SCRIPT = re.compile(
    r'<script id="discord:component-embed" type="application/json">(.*?)</script>', re.S
)
PAYLOAD_LIMIT = 3000
INVITE_URL = re.compile(
    r"^https://discord\.com/oauth2/authorize\?client_id=\d+&permissions=8&scope=bot\+applications\.commands$"
)
COMMANDS_URL = "https://niko.sryze.cc/commands"
SUPPORT_URL = "https://niko.sryze.cc/discord"
STATS_LINE = re.compile(r"^-# [\d,]+ commands · [\d,]+ servers · [\d,]+ members$", re.M)
STATS = {"command_count": 329, "guild_count": 63, "user_count": 2611}
# A stand-in for the invite the running site builds from its own app id.
INVITE = (
    "https://discord.com/oauth2/authorize"
    "?client_id=1520558530472448170&permissions=8&scope=bot+applications.commands"
)


def build_inputs():
    if not MANIFEST.is_file() or not SHELL.is_file():
        pytest.skip("the website has not been built (src/website/dist is missing)")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    pages = manifest.get("pages") or {}
    assert pages, "the build manifest has no pages"
    return pages, SHELL.read_text(encoding="utf-8")


def render(route: str, stats=True, shell: str = None, context=None):
    """The served document for one route, with fixed providers."""
    pages, built_shell = build_inputs()
    provider = (lambda: STATS) if stats else None
    return social_preview.inject(
        built_shell if shell is None else shell,
        str(DIST),
        route,
        INVITE,
        stats_provider=provider,
        context_provider=(lambda _route, ctx=context: ctx) if context is not None else None,
    )


GUILD_CONTEXT = {
    "kind": "guild",
    "template": "/levels",
    "title": "Sage Gardens — Level leaderboard",
    "description": "Leveling standings for Sage Gardens — 12,480 members, 1,204 ranked by XP.",
    "name": "Sage Gardens",
    "section": "LEVEL LEADERBOARD",
    "thumbnail": "https://cdn.discordapp.com/icons/123/sage.png",
    "accent": None,
    "lines": ["**12,480** members · **1,204** ranked by XP"],
}


def staff_context(name="Aiko", role="Head Support", accent=0xC8A882, links=3):
    return {
        "kind": "staff",
        "template": "/team",
        "title": f"{name} — Niko team",
        "description": f"{role} on the Niko team, keeping tickets tidy.",
        "name": name,
        "section": f"{role.upper()} · STAFF",
        "thumbnail": f"https://cdn.discordapp.com/avatars/{name}/avatar.png",
        "accent": accent,
        "lines": [f"-# {links} public links · niko.sryze.cc/team"] if links else [],
    }


def embed(html: str) -> dict:
    found = EMBED_SCRIPT.findall(html)
    assert len(found) == 1, f"expected exactly one component embed, found {len(found)}"
    return json.loads(found[0])


def routes():
    pages, _ = build_inputs()
    return sorted(pages)


def test_the_build_writes_a_page_list_and_one_shell_instead_of_a_page_per_route():
    pages, _ = build_inputs()
    assert len(pages) > 50, "the build should describe every public page"
    for page in pages.values():
        assert page.get("title") and page.get("description"), page
        assert page["image"].startswith("https://niko.sryze.cc/og/"), page
    # The whole point of the move: the build no longer writes per-route HTML.
    assert len(list(DIST.rglob("index.html"))) == 1, "the build must only emit the one shell"


@pytest.mark.parametrize("landing", [True, False])
def test_every_page_renders_a_container_embed_within_discords_byte_limit(landing):
    for route in routes():
        html = render(route, stats=landing)
        payload = embed(html)
        raw = json.dumps(payload, separators=(",", ":"))
        assert len(raw.encode("utf-8")) <= PAYLOAD_LIMIT, f"{route} payload is over Discord's byte limit"
        # The escaped form Discord measures has to fit too.
        escaped = raw.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        assert len(escaped.encode("utf-8")) <= PAYLOAD_LIMIT, route
        container = payload["component"]
        assert container["type"] == 17, f"{route}: the only top-level component must be a Container"
        assert isinstance(container.get("accent_color"), int)
        components = container["components"]
        assert len(components) + 1 <= 40, f"{route}: too many components for a component embed"
        # Page information, then the image, a separator, and the button row last.
        assert [component["type"] for component in components] == [10, 12, 14, 1], route


def test_the_page_information_sits_above_the_opengraph_image():
    for route in routes():
        html = render(route)
        payload = embed(html)
        text_display = payload["component"]["components"][0]
        gallery = payload["component"]["components"][1]
        content = text_display["content"]
        assert content.startswith("# "), f"{route}: the first text display must be the page heading"
        # A heading, the section kicker, and the description.
        assert len(content.splitlines()) >= 3, route
        # The image is the same file the plain fallback preview uses.
        image = gallery["items"][0]["media"]["url"]
        assert image.startswith("https://niko.sryze.cc/og/") and image.endswith(".png"), image
        assert f'<meta property="og:image" content="{image}"' in html, route
        assert len(gallery["items"]) <= 10


def test_the_button_row_links_the_invite_commands_and_support_server():
    for route in routes():
        buttons = embed(render(route))["component"]["components"][3]["components"]
        assert [button["type"] for button in buttons] == [2, 2, 2]
        assert [button["style"] for button in buttons] == [5, 5, 5], f"{route}: buttons must be link style"
        labels = [button["label"] for button in buttons]
        assert labels == ["Add Niko", "Commands", "Support server"], route
        assert all(len(label) <= 80 for label in labels)
        urls = [button["url"] for button in buttons]
        assert INVITE_URL.match(urls[0]), f"{route}: invite button points at {urls[0]}"
        assert urls[1:] == [COMMANDS_URL, SUPPORT_URL], route
        assert all(len(url) <= 2048 for url in urls)


def test_the_open_graph_fallback_survives_alongside_the_embed():
    for route in routes():
        html = render(route)
        assert EMBED_SCRIPT.search(html), route
        for tag in ("og:title", "og:description", "og:image", "og:url", "twitter:card"):
            assert f'"{tag}"' in html, f"{route} is missing the {tag} fallback"


def test_only_landing_pages_advertise_the_live_counts():
    pages, _ = build_inputs()
    landing = [route for route, page in pages.items() if page.get("landing")]
    assert landing, "no landing page is marked in the manifest"
    for route in routes():
        content = embed(render(route))["component"]["components"][0]["content"]
        if route in landing:
            assert STATS_LINE.search(content), f"{route} should show the command/server/member counts"
        else:
            assert not STATS_LINE.search(content), f"{route} is not a landing page but shows the counts"


def test_the_rendered_head_replaces_only_the_shells_own_title_region():
    _, shell = build_inputs()
    html = render("/commands", shell=shell)
    assert html.count("<title>") == 1
    assert html.count('<meta name="description"') == 1
    assert '<title>Commands — Niko</title>' in html
    # Everything else about the shell is untouched, including the hashed assets
    # Vite injected and the PWA tags.
    for needle in ("theme-color", "manifest.webmanifest", "apple-touch-icon", "viewport"):
        assert needle in html, needle
    assert re.search(r'src="/assets/index-[^"]+\.js"', html), "the built asset tag was lost"
    assert 'property="og:url" content="https://niko.sryze.cc/commands"' in html


def test_an_unlisted_route_still_gets_a_preview_pointing_at_its_own_url():
    for route in ("/billing", "/transcript", "/a-route-that-does-not-exist"):
        html = render(route)
        assert f'<link rel="canonical" href="https://niko.sryze.cc{route}" />' in html, route
        assert "<title>Niko — Discord companion</title>" in html, route
        assert embed(html)["component"]["components"][3]["components"], route


def test_the_trailing_slash_and_query_never_change_the_page():
    plain = render("/commands")
    for variant in ("/commands/", "/commands?ref=discord", "/commands#top"):
        assert render(variant) == plain, variant


def test_over_budget_copy_is_shortened_instead_of_dropped():
    page = {
        "title": "Commands — Niko",
        "description": "Long copy. " * 400,
        "section": "Command reference",
        "landing": True,
        "image": "https://niko.sryze.cc/og/commands.png",
    }
    script = social_preview.component_embed_script(page, INVITE, STATS)
    assert script, "an over-budget page must still render an embed"
    raw = script.split(">", 1)[1].rsplit("</script>", 1)[0]
    assert len(raw.encode("utf-8")) <= PAYLOAD_LIMIT
    content = json.loads(raw)["component"]["components"][0]["content"]
    # The heading loses its " — Niko" suffix, exactly like the Open Graph card.
    assert content.startswith("# Commands\n")
    # The counts are what gets dropped first, then the description is trimmed.
    assert not STATS_LINE.search(content)
    assert len(content) < 400


def test_hostile_page_copy_cannot_escape_the_script_or_the_head(tmp_path):
    page = {
        "title": "</script><script>alert(1)</script> — Niko",
        "description": 'a & b < c > d "quoted"',
        "section": "Sec",
        "landing": False,
        "image": "https://niko.sryze.cc/og/home.png",
    }
    script = social_preview.component_embed_script(page, INVITE)
    assert script.count("</script>") == 1
    assert "<script>alert" not in script

    # The same copy through a manifest, the way a real page reaches the head.
    tmp_path.joinpath(social_preview.MANIFEST_NAME).write_text(
        json.dumps({"site": social_preview.SITE_URL, "pages": {"/evil": page}}), encoding="utf-8"
    )
    head = social_preview.render_head(str(tmp_path), "/evil", INVITE)
    assert "&lt;/script&gt;" in head
    assert "<script>alert" not in head
    assert "&amp;" in head and "&quot;" in head
    assert head.count("</script>") == 1


def test_a_route_with_no_counts_provider_still_renders():
    for route in routes():
        html = render(route, stats=False)
        assert embed(html)["component"]["components"][3]["components"], route


def test_injection_falls_back_to_appending_when_the_shell_has_no_region():
    plain_shell = "<html><head><title>Plain</title></head><body></body></html>"
    html = render("/commands", shell=plain_shell)
    assert "<title>Commands — Niko</title>" in html
    assert EMBED_SCRIPT.search(html)


# ── Page types: a server's board and a team profile ───────────────────────────

SUBJECT_LAYOUT = [9, 14, 1]  # Section, Separator, Button row


def subject_section(payload: dict) -> dict:
    """The Section (type 9) a subject page leads with."""
    section = payload["component"]["components"][0]
    assert section["type"] == 9
    return section


def test_a_guild_leaderboard_describes_the_server_instead_of_niko():
    html = render("/levels/123456", context=GUILD_CONTEXT)
    payload = embed(html)
    container = payload["component"]
    assert [component["type"] for component in container["components"]] == SUBJECT_LAYOUT
    # No Niko-branded heading, card image or section kicker abstraction: the
    # server leads, with its own icon as a thumbnail accessory.
    assert not any(component["type"] == 12 for component in container["components"])
    section = subject_section(payload)
    text = section["components"][0]["content"]
    assert text.startswith("# Sage Gardens\n")
    assert "LEVEL LEADERBOARD" in text
    assert "12,480" in text and "1,204" in text
    accessory = section["accessory"]
    assert accessory == {"type": 11, "media": {"url": GUILD_CONTEXT["thumbnail"]}}
    assert container["accent_color"] == 0x8BD5B1  # Niko's own colour
    assert len(json.dumps(payload).encode()) <= PAYLOAD_LIMIT
    # The head still describes the server, and the OG fallback is intact.
    assert "<title>Sage Gardens — Level leaderboard</title>" in html
    assert '<link rel="canonical" href="https://niko.sryze.cc/levels/123456" />' in html
    assert '<meta property="og:image" content="https://niko.sryze.cc/og/' in html
    assert [button["label"] for button in container["components"][2]["components"]] == [
        "Add Niko", "Commands", "Support server"
    ]


def test_a_server_without_an_icon_still_gets_a_valid_thumbnail():
    context = {**GUILD_CONTEXT, "thumbnail": ""}
    payload = embed(render("/levels/123456", context=context))
    url = subject_section(payload)["accessory"]["media"]["url"]
    assert url == social_preview.FALLBACK_THUMBNAIL
    assert url.startswith("https://")


def test_a_staff_profile_uses_the_members_own_colour_and_avatar():
    context = staff_context()
    payload = embed(render("/team/9", context=context))
    container = payload["component"]
    assert [component["type"] for component in container["components"]] == SUBJECT_LAYOUT
    assert container["accent_color"] == 0xC8A882
    section = subject_section(payload)
    text = section["components"][0]["content"]
    assert text.startswith("# Aiko\n")
    assert "HEAD SUPPORT · STAFF" in text
    assert "3 public links" in text
    assert section["accessory"]["media"]["url"] == context["thumbnail"]
    assert "<title>Aiko — Niko team</title>" in render("/team/9", context=context)


def test_two_staff_profiles_do_not_share_a_layout():
    aiko = embed(render("/team/9", context=staff_context()))
    bo = embed(render("/team/10", context=staff_context("Bo", "Moderator", accent=None, links=0)))
    assert aiko["component"]["accent_color"] != bo["component"]["accent_color"]
    assert aiko["component"]["components"][0] != bo["component"]["components"][0]
    # A member with no card colour falls back to Niko's, and keeps a valid row.
    assert bo["component"]["accent_color"] == 0x8BD5B1
    assert "MODERATOR · STAFF" in bo["component"]["components"][0]["components"][0]["content"]


@pytest.mark.parametrize("context, route", [
    (GUILD_CONTEXT, "/levels/123456"),
    ({**GUILD_CONTEXT, "name": "N" * 300, "thumbnail": ""}, "/levels/1"),
    (staff_context(), "/team/9"),
    (staff_context("Bo", "Moderator", links=0), "/team/10"),
])
def test_subject_embeds_validate_and_fit_discords_limits(context, route):
    payload = embed(render(route, context=context))
    container = payload["component"]
    assert container["type"] == 17
    assert 1 + len(container["components"]) <= 40
    raw = json.dumps(payload, separators=(",", ":"))
    escaped = raw.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    assert len(escaped.encode("utf-8")) <= PAYLOAD_LIMIT
    url = subject_section(payload)["accessory"]["media"]["url"]
    assert url.startswith("https://") and len(url) <= 2048


def test_a_page_with_an_unrecognised_subject_keeps_the_standard_container():
    # A provider that only names the section (no server data, a hidden profile).
    html = render("/levels/999", context={"template": "/levels"})
    payload = embed(html)
    assert [component["type"] for component in payload["component"]["components"]] == [10, 12, 14, 1]
    assert "<title>Server Leaderboard — Niko</title>" in html
    assert '<link rel="canonical" href="https://niko.sryze.cc/levels/999" />' in html


# ── The same path through the running app ─────────────────────────────────────


@pytest.fixture(autouse=True)
def _fresh_social_caches():
    """Both resolvers cache per route; every test starts from a cold cache."""
    from webapp import server

    server._social_context_cache.clear()
    server._social_stats_cache = None
    yield
    server._social_context_cache.clear()
    server._social_stats_cache = None


def serve(path: str) -> str:
    from webapp import app

    return app.test_client().get(path, headers={"Accept": "text/html"}).get_data(as_text=True)


def test_the_server_describes_a_guild_leaderboard_from_its_own_bot(monkeypatch):
    from webapp import server

    guild = SimpleNamespace(
        id=123456, name="Sage Gardens",
        icon=SimpleNamespace(url="https://cdn.discordapp.com/icons/123/sage.png"),
        member_count=12480,
    )
    monkeypatch.setattr(server, "_discord_bot", SimpleNamespace(get_guild=lambda guild_id: guild if guild_id == 123456 else None))
    monkeypatch.setattr(server, "get_runtime_guild_level_page", lambda guild_id, offset, limit: ([], 1204))
    monkeypatch.setattr(server, "get_runtime_level_config", lambda guild_id: {"xp_enabled": True})

    context = server._guild_embed_context("123456")
    assert context["name"] == "Sage Gardens"
    assert context["template"] == "/levels"
    assert context["thumbnail"].endswith("sage.png")
    assert "12,480" in context["lines"][0] and "1,204" in context["lines"][0]
    assert "12,480 members, 1,204 ranked" in context["description"]
    # A guild the bot is not in has nothing to describe.
    assert server._guild_embed_context("999") is None
    assert server._staff_embed_context("not-a-number") is None

    html = serve("/levels/123456")
    payload = embed(html)
    assert [component["type"] for component in payload["component"]["components"]] == SUBJECT_LAYOUT
    assert subject_section(payload)["components"][0]["content"].startswith("# Sage Gardens")
    assert "<title>Sage Gardens — Level leaderboard</title>" in html

    # XP paused is called out rather than shown as an empty board.
    monkeypatch.setattr(server, "get_runtime_level_config", lambda guild_id: {"xp_enabled": False})
    server._social_context_cache.clear()
    paused = server._guild_embed_context("123456")
    assert any("paused" in line for line in paused["lines"])

    # An unknown server keeps the leaderboard section's copy in the standard layout.
    unknown = serve("/levels/999")
    assert "<title>Server Leaderboard — Niko</title>" in unknown
    assert [component["type"] for component in embed(unknown)["component"]["components"]] == [10, 12, 14, 1]


def test_the_server_describes_a_team_profile_from_the_public_roster(monkeypatch):
    from webapp import server

    roster = [
        {"id": "9", "name": "Aiko", "role_label": "Head Support",
         "bio": "Support lead,\n\tfond of   tea and tidy ticket queues.",
         "avatar_url": "https://cdn.discordapp.com/avatars/9/aiko.png",
         "public_links": [{"type": "github", "url": "https://github.com/aiko"}],
         "card": {"theme": "dark", "accent": "c8a882"}},
        {"id": "10", "name": "Bo", "role_label": "Moderator", "bio": None,
         "avatar_url": None, "public_links": [], "card": {"accent": None}},
    ]
    monkeypatch.setattr(server, "_load_staff_rows", lambda: roster)

    aiko = server._staff_embed_context("9")
    assert aiko["section"] == "HEAD SUPPORT · STAFF"
    assert aiko["accent"] == 0xC8A882
    assert aiko["description"] == "Support lead, fond of tea and tidy ticket queues."
    assert aiko["lines"] == ["-# 1 public link · niko.sryze.cc/team"]
    bo = server._staff_embed_context("10")
    assert bo["accent"] is None and bo["lines"] == []
    assert bo["description"] == "Moderator on the Niko team. Say hi in the support server."
    # Someone off the public roster is not described at all (hidden or former).
    assert server._staff_embed_context("404") is None

    html = serve("/team/9")
    payload = embed(html)
    assert payload["component"]["accent_color"] == 0xC8A882
    assert subject_section(payload)["accessory"]["media"]["url"].endswith("aiko.png")
    assert "<title>Aiko — Niko team</title>" in html

    # A hidden profile falls back to the team section's copy.
    hidden = serve("/team/404")
    assert [component["type"] for component in embed(hidden)["component"]["components"]] == [10, 12, 14, 1]
    assert "<title>Team — Niko</title>" in hidden
    # `/team/apply` is a page of its own, not a member id, and keeps its copy.
    application = serve("/team/apply")
    assert "<title>Join the Niko Team — Staff Applications</title>" in application
    assert [component["type"] for component in embed(application)["component"]["components"]] == [10, 12, 14, 1]


def test_a_long_staff_bio_is_trimmed_for_the_preview(monkeypatch):
    from webapp import server

    monkeypatch.setattr(server, "_load_staff_rows", lambda: [
        {"id": "9", "name": "Aiko", "role_label": "Head Support", "bio": "tea " * 400,
         "avatar_url": None, "public_links": [], "card": {}},
    ])
    context = server._staff_embed_context("9")
    assert len(context["description"]) <= 180
    assert context["description"].endswith("…")
    assert context["description"].count("  ") == 0


def test_subject_contexts_are_cached_per_route(monkeypatch):
    from webapp import server

    calls = []
    monkeypatch.setattr(server, "_guild_embed_context", lambda guild_id: (calls.append(guild_id), GUILD_CONTEXT)[1])
    server._social_context("/levels/123456")
    server._social_context("/levels/123456")
    assert len(calls) == 1
    server._social_context("/levels/999")
    assert len(calls) == 2
    assert server._social_context("/commands") is None
