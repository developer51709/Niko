"""Custom emoji and text formatting rendering.

Discord never draws a broken custom emoji: an emoji it cannot resolve is
written out as ``:name:`` instead. The popups, the export and the rendering lab
all follow that, and the rendering lab draws the bot's real emojis — the names
and ids ``/api/emojis`` parses out of src/config/emojis.py, including the ids
the bot's emoji sync re-uploaded — rather than a copy that goes stale. The
markdown markers are covered here too, because a marker that is not a capture
group renders as the wrong formatting without any error.
"""

import re
import sys
from pathlib import Path

import discord

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config.emojis import get_emoji  # noqa: E402
from utils.tickets.transcripts import _md_to_html, export_html  # noqa: E402
from webapp import app  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

#: ``<:name:id>`` / ``<a:name:id>``, exactly what the bot sends and the config
#: and the generated web data file both hold.
TOKEN = re.compile(r"<(a?):([A-Za-z0-9_~]+):(\d+)>")

def _config_emojis():
    """The bot's emojis as (name, id, animated), in config order."""
    tokens = TOKEN.findall((ROOT / "src" / "config" / "emojis.py").read_text(encoding="utf-8"))
    seen = set()
    emojis = []
    for animated, name, emoji_id in tokens:
        if (name, emoji_id) in seen:
            continue
        seen.add((name, emoji_id))
        emojis.append((name, emoji_id, animated == "a"))
    return emojis


def _emoji_api_payload():
    response = app.test_client().get("/api/emojis")
    assert response.status_code == 200
    return response.get_json()["emojis"]


def _catalog_names():
    from utils.emoji_sync import live_emoji_catalog

    return [emoji.discord_name for emoji in live_emoji_catalog()]


def test_the_website_reads_the_bots_emojis_from_the_api():
    """One source of truth: the site asks the bot instead of carrying a copy.

    The web app used to hold a table generated from src/config/emojis.py, so a
    new or re-uploaded emoji stayed dead there until somebody ran the generator
    — and a re-upload always changes the id.
    """
    from utils.emoji_sync import parse_config

    assert _emoji_api_payload() == [
        {
            "name": parsed.discord_name,
            "id": str(parsed.emoji_id),
            "animated": parsed.animated,
            "placeholder": parsed.is_placeholder,
        }
        for parsed in parse_config()
    ]

    source = (ROOT / "web" / "src" / "data" / "botEmojis.ts").read_text(encoding="utf-8")
    # The web app holds no emoji names or ids of its own any more.
    assert not TOKEN.search(source), "the web emoji list is hardcoded again"
    assert "BOT_EMOJIS" not in source
    assert "getBotEmojis()" in source
    assert "export function botEmojiToken" in source

    api = (ROOT / "web" / "src" / "api.ts").read_text(encoding="utf-8")
    assert 'export const getBotEmojis = () => api<BotEmojisResponse>("/api/emojis");' in api


def test_the_emoji_api_reports_the_ids_the_running_sync_adopted(monkeypatch):
    """A re-uploaded emoji reaches the website without a build or a restart."""
    from utils import emoji_sync

    parsed = emoji_sync.parse_config()[0]
    monkeypatch.setattr(
        emoji_sync,
        "live_emoji_ids",
        lambda: {parsed.emoji_id: f"<:{parsed.discord_name}:1560000000000000001>"},
    )

    assert _emoji_api_payload()[0] == {
        "name": parsed.discord_name,
        "id": "1560000000000000001",
        "animated": parsed.animated,
        "placeholder": False,
    }


def test_a_stub_emoji_id_is_marked_instead_of_drawn():
    """A config stub is not a snowflake, so the CDN has nothing to serve."""
    from utils.emoji_sync import ParsedEmoji

    assert ParsedEmoji("log_kick", 9000001, False).is_placeholder
    assert not ParsedEmoji("log_kick", 1564762780425265172, False).is_placeholder
    # The stub ids in the config are exactly the ones the site marks.
    payload = {emoji["name"]: emoji for emoji in _emoji_api_payload()}
    for emoji in payload.values():
        assert emoji["placeholder"] is (len(emoji["id"]) < 15), emoji


def test_retired_owner_and_developer_emojis_are_removed():
    config = (ROOT / "src" / "config" / "emojis.py").read_text(encoding="utf-8")
    web = (ROOT / "web" / "src" / "data" / "botEmojis.ts").read_text(encoding="utf-8")
    owner = (ROOT / "src" / "cogs" / "staff" / "owner.py").read_text(encoding="utf-8")

    # These two old application emojis are retired; neither the bot nor the
    # rendering lab should still carry their names or ids.
    assert "badge_developer" not in config
    assert "bot_owner" not in config
    assert "badge_developer" not in web
    assert "bot_owner" not in web
    assert not (ROOT / "src" / "assets" / "emojis" / "badge_developer.png").exists()
    assert not (ROOT / "src" / "assets" / "emojis" / "bot_owner.png").exists()

    # The lab draws the catalog the API reports, so a retired emoji has to be
    # gone from the config itself rather than from a copy.
    names = _catalog_names()
    assert "badge_developer" not in names
    assert "bot_owner" not in names

    # Owner-only command panels use the owner role badge instead.
    assert "get_emoji('bot_owner')" not in owner
    assert owner.count("get_emoji('badge_owner')") >= 2
    assert "badge_owner" in names


def _info_cards_source() -> str:
    """Every module of the info cog: its cards are split by subject."""
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "src" / "cogs" / "info").glob("*.py"))
    )


def test_the_bot_cards_partner_badge_uses_the_profile_badge_asset():
    config = (ROOT / "src" / "config" / "emojis.py").read_text(encoding="utf-8")
    web = (ROOT / "web" / "src" / "data" / "botEmojis.ts").read_text(encoding="utf-8")
    cog = _info_cards_source()
    build = (ROOT / "scripts" / "build-badge-art.mjs").read_text(encoding="utf-8")
    assets = ROOT / "src" / "assets" / "emojis"

    # The old partner emoji art did not match the rest of the set, so neither
    # the bot config nor the rendering lab carries it anymore.
    assert 'emoji_name == "partner"' not in config
    assert "partner" not in web
    assert not (assets / "partner.png").exists()
    assert not (assets / "icon_partner.png").exists()

    # Its replacement is generated from the same profile badge asset the
    # website popups draw, so the bot card and the site match.
    assert 'emoji_name == "partner_badge"' in config
    names = _catalog_names()
    assert "partner" not in names
    assert "partner_badge" in names
    assert (assets / "partner_badge.png").exists()
    assert 'partner_badge: "badges/partner.svg"' in build
    assert re.search(r'\(\("partner",\),\s*"partner_badge"\)', cog)


def test_the_react_markdown_writes_the_emoji_name_out_when_it_cannot_load():
    source = (ROOT / "web" / "src" / "components" / "DiscordMarkdown.tsx").read_text(encoding="utf-8")

    # The emoji node goes through the component that owns the fallback...
    assert "<DiscordEmoji key={key} name={node.name} id={node.id} animated={node.animated}" in source
    # ...and a missing id or a failed image is the `:name:` text Discord shows,
    # never an image whose alt text stands in for a broken icon.
    assert "discord-emoji-fallback" in source
    assert "{`:${name}:`}" in source
    assert "onError={() => setBroken(true)}" in source
    assert "event.currentTarget.alt" not in source
    # The profile popup's custom status uses the same component.
    assert 'className="discord-profile-status-emoji"' in source


def test_the_react_emoji_popup_matches_discord_and_gets_the_ticket_server():
    markdown = (ROOT / "web" / "src" / "components" / "DiscordMarkdown.tsx").read_text(encoding="utf-8")
    page = (ROOT / "web" / "src" / "pages" / "TranscriptPage.tsx").read_text(encoding="utf-8")
    route = (ROOT / "src" / "webapp" / "routes" / "transcript_routes.py").read_text(encoding="utf-8")

    # The bot's live emoji catalog decides the popup layout, so an app emoji
    # never has to be guessed from its name and never comes from a frozen list.
    assert "const isApplication = source ? source === \"app\" : isApplicationEmoji(id);" in markdown
    assert "useBotEmojis();" in markdown
    assert "BOT_EMOJIS" not in markdown
    assert 'data-emoji-app={isApplication ? "1" : "0"}' in markdown
    assert "This emoji is from the Niko app" in markdown
    assert "This emoji is from this server. Get Nitro to use it everywhere." in markdown
    # The button uses Discord's own Nitro mark, not a hand-drawn placeholder.
    assert 'd="M13.32 21.978' in markdown
    # The popup is a fixed layer on the page, not a child clipped by the chat.
    assert "createPortal(" in markdown
    assert 'window.addEventListener("scroll", positionPopup, true);' in markdown
    assert 'if (event.key === "Escape") setOpen(false);' in markdown

    # The transcript page supplies the ticket server's identity, and the API
    # resolves it from the stored guild id instead of trusting old metadata.
    assert "<DiscordEmojiProvider guildName={data.guild_name} guildIconUrl={data.guild_icon_url}>" in page
    assert 'result.update(_guild_identity(result.get("guild_id")))' in route
    assert 'metadata.update(_guild_identity(result.get("guild_id")))' in route


def test_custom_emoji_popup_knows_application_and_server_emojis():
    # The application emoji is read from the config, so this never pins an id
    # that a re-upload has already retired.
    token = get_emoji("hypesquad_bravery")
    emoji_id = TOKEN.search(token).group(3)
    application = _md_to_html(token)
    server = _md_to_html("<:drinking~1:123456789012345678>")

    # The popup needs the id for its own artwork and whether the emoji belongs
    # to the Niko application or to the ticket's server.
    assert f'data-emoji-id="{emoji_id}"' in application
    assert 'data-emoji-app="1"' in application
    assert 'data-emoji-id="123456789012345678"' in server
    assert 'data-emoji-app="0"' in server
    # A resolved emoji is a keyboard-operable popup trigger; a broken one later
    # falls back to its name and loses that role.
    assert 'role="button" tabindex="0" aria-haspopup="dialog"' in application


def test_export_includes_both_discord_emoji_popup_layouts():
    page = export_html(
        [{
            "timestamp": "now",
            "author": "Niko",
            "author_id": 1,
            "content": "<:hypesquad_bravery:1520827369508700252> <:drinking~1:123456789012345678>",
        }],
        {
            "channel_name": "ticket",
            "guild_name": "Niko",
            "guild_icon_url": "https://cdn.example/icon.png",
        },
    )

    # The application popup names the app; the server popup adds the Nitro
    # prompt and the ticket server's icon and name.
    assert "This emoji is from the Niko app" in page
    assert "This emoji is from this server. Get Nitro to use it everywhere." in page
    assert "discord-emoji-popup-nitro" in page
    # The downloaded page carries the same official Nitro mark.
    assert 'd="M13.32 21.978' in page
    assert 'const emojiGuild = {"name": "Niko", "iconUrl": "https://cdn.example/icon.png"};' in page
    assert "Invite-only server" in page
    # Clicking the emoji opens the popup, and Escape closes it again.
    assert "const openEmojiPopup = (img) =>" in page
    assert 'event.target.closest?.("img.custom-emoji[data-emoji-id]")' in page
    assert "if (event.key === \"Escape\") { closeEmojiPopup(); closeProfile(); }" in page


def test_the_export_swaps_a_broken_emoji_for_its_name():
    html = _md_to_html("hello <:coffee:123456> and <a:wave:654321>")

    # The name travels with the image so the script can fall back to it.
    assert 'data-emoji-name="coffee"' in html
    assert 'data-emoji-name="wave"' in html
    assert 'cdn.discordapp.com/emojis/654321.gif' in html

    page = export_html(
        [{"timestamp": "now", "author": "Niko", "author_id": 1, "content": "<:coffee:123456>"}],
        {"channel_name": "ticket", "guild_name": "Server"},
    )

    assert "const fixCustomEmoji = (img) => {" in page
    assert 'fallback.textContent = ":" + (img.dataset.emojiName || "") + ":";' in page
    # An image that failed before the script ran is caught by its size.
    assert "img.complete && img.naturalWidth === 0" in page
    assert 'document.querySelectorAll("img.custom-emoji").forEach(fixCustomEmoji);' in page


def _capture_groups(pattern: str) -> int:
    """Count capturing groups: not escaped, and not a ``(?:`` / ``(?<`` form."""
    return len(re.findall(r"(?<!\\)\((?!\?)", pattern))


def test_every_markdown_marker_is_a_capture_group():
    """The format a marker opens is chosen by the group that matched.

    An uncaptured marker still matches, so its characters disappear and the
    text between them silently takes another format: the italics were dropped,
    strikethrough rendered as italics and spoilers as italics too. Every marker
    therefore has to be a capture group, numbered the way the branches expect.
    """
    source = (ROOT / "web" / "src" / "components" / "DiscordMarkdown.tsx").read_text(encoding="utf-8")
    pattern = re.search(r"const tokenPattern = /(.+)/g;", source)
    assert pattern, "DiscordMarkdown no longer defines tokenPattern"

    assert _capture_groups(pattern.group(1)) == 13
    branches = re.findall(
        r'else if \(match\[(\d+)\]\) tokens\.push\(\{ kind: "marker", format: "([A-Za-z]+)" \}\)',
        source,
    )
    assert branches == [
        ("8", "bold"),
        ("9", "underline"),
        ("10", "italic"),
        ("11", "italicAlt"),
        ("12", "strike"),
        ("13", "spoiler"),
    ]


# ── The generated icon emojis ────────────────────────────────────────────────

#: A name from the families scripts/build-emoji-icons.mjs must never write.
PROTECTED_EMOJI = re.compile(r"(?:badge|c4|white|logo|loading)", re.I)


def test_the_emoji_icon_script_owns_only_the_main_and_log_emojis():
    """Badge art, Connect Four, the logo and the loading emojis are off limits.

    Each of those comes from a different owner (build-badge-art.mjs, the game
    sprites, the hand-exported brand marks, the spinner frames), and a script
    that rewrites them silently replaces artwork nobody asked it to touch. The
    script refuses those names outright, so the table cannot grow into them.
    """
    source = (ROOT / "scripts" / "build-emoji-icons.mjs").read_text(encoding="utf-8")
    emojis = re.findall(r'\["([a-z_0-9]+)", "[a-z0-9-]+", [A-Z]+\]', source)

    assert len(emojis) > 100
    assert len(emojis) == len(set(emojis)), "an emoji is listed twice"
    # The general-purpose set and the per-message-type log set.
    assert {"tick", "cross", "warning"} <= set(emojis)
    assert sum(1 for name in emojis if name.startswith("log_")) > 40
    # Every table entry goes through the guard, and the guard names all four
    # protected families.
    assert "assertWritable(name)" in source
    for family in ("badge art", "Connect Four", "logo", "loading spinner"):
        assert family in source, family

    for name in emojis:
        assert not PROTECTED_EMOJI.search(name), f"{name} belongs to a family the script must not write"
        # The sync uploads art by name, so an emoji with no art never reaches
        # Discord; one with no config entry can never be sent at all.
        assert (ROOT / "src" / "assets" / "emojis" / f"{name}.png").exists(), name
        assert get_emoji(name), name


def test_every_log_message_type_has_its_own_emoji():
    """Two log entries in a channel never share an icon.

    The heading used to be the category's emoji, so every moderation entry
    looked the same and a channel of them read as one repeated picture.
    """
    from cogs.logging.formatters import LOG_EMOJI_KEYS

    names = list(LOG_EMOJI_KEYS.values())
    assert len(names) > 40
    assert len(names) == len(set(names)), "two log message types share an emoji"
    for title, name in LOG_EMOJI_KEYS.items():
        assert not PROTECTED_EMOJI.search(name), title
        assert (ROOT / "src" / "assets" / "emojis" / f"{name}.png").exists(), title
        # A typo here is a heading that renders the literal text `:log_kick:`.
        # The Discord-side name may differ in case only (`automod` is uploaded
        # as `Automod`), which renders identically, so compare case-insensitively.
        emoji = get_emoji(name) or ""
        assert f":{name}:" in emoji.lower(), title


def test_the_log_emoji_ids_are_unique_until_the_sync_uploads_the_art():
    """The startup sync keys on the id, so two entries must never share one.

    A duplicate id makes the sync parse a single emoji, upload only the first
    name, and rewrite both config entries to it. The ids are stubs on a fresh
    checkout and live application-emoji ids after the first sync; both have to
    stay unique.
    """
    source = (ROOT / "src" / "config" / "emojis.py").read_text(encoding="utf-8")
    ids = re.findall(r'return "<:log_[a-z0-9_]+:(\d+)>"', source)

    assert len(ids) > 40
    assert len(ids) == len(set(ids)), "two log emojis share an id"


def test_a_log_entry_is_headed_by_its_message_types_emoji():
    from cogs.logging import formatters

    def heading(title, action_key=None):
        view = formatters._build_log_view(
            category="moderation", title=title, body="body", guild_id=1, action_key=action_key
        )
        return [
            item.content for item in view.walk_children() if isinstance(item, discord.ui.TextDisplay)
        ][0]

    assert get_emoji("log_kick") in heading("Kick")
    assert get_emoji("log_ban") in heading("Ban")
    # The action key counts too: the gateway join event logs a shorter one.
    assert get_emoji("log_member_join") in heading("Member Joined", action_key="member_join")
    # A type with no entry of its own still renders, with its category emoji.
    assert get_emoji("moderation") in heading("Something New")


def test_the_render_lab_tests_emoji_rendering_with_the_bots_own_emojis():
    source = (ROOT / "web" / "src" / "pages" / "RenderLabPage.tsx").read_text(encoding="utf-8")

    # The lab draws the catalog the API reports, live, and never a copy of it.
    assert "const emojis = useBotEmojis();" in source
    assert "emojis.map(botEmojiToken).join" in source
    assert "{emojis.map((emoji) =>" in source
    assert "BOT_EMOJIS" not in source
    # The popup samples take their id from the catalog too, so a re-uploaded
    # emoji cannot leave a dead id behind in this page.
    assert 'emojis.find((emoji) => emoji.name === "hypesquad_bravery")' in source
    assert "id=\"1520827369508700252\"" not in source
    assert ">Custom emoji<" in source
    # The lab has to show the invalid case too, wrapped in real formatting.
    assert "<:not_a_real_emoji:" in source
    assert "<:deleted:0>" in source
    # ...and every marker whose formatting can be checked in the same line.
    assert "**bold** <:not_a_real_emoji:" in source
    assert "~~strike~~" in source
    assert "||spoiler||" in source
