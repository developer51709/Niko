"""Custom emoji and text formatting rendering.

Discord never draws a broken custom emoji: an emoji it cannot resolve is
written out as ``:name:`` instead. The popups, the export and the rendering lab
all follow that, and the rendering lab draws the bot's real emojis (the names
and ids from src/config/emojis.py) rather than made-up samples. The markdown
markers are covered here too, because a marker that is not a capture group
renders as the wrong formatting without any error.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.tickets.transcripts import _md_to_html, export_html  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

#: ``<:name:id>`` / ``<a:name:id>``, exactly what the bot sends and the config
#: and the generated web data file both hold.
TOKEN = re.compile(r"<(a?):([A-Za-z0-9_~]+):(\d+)>")

#: One entry of web/src/data/botEmojis.ts, written by
#: scripts/build-bot-emojis.mjs.
WEB_EMOJI_ENTRY = re.compile(
    r'\{ name: "([A-Za-z0-9_~]+)", id: "(\d+)", animated: (true|false), placeholder: (true|false) \}'
)


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


def test_the_web_emoji_list_matches_the_bot_config():
    """A new bot emoji means one run of scripts/build-bot-emojis.mjs."""
    source = (ROOT / "web" / "src" / "data" / "botEmojis.ts").read_text(encoding="utf-8")

    assert "scripts/build-bot-emojis.mjs" in source
    assert "export function botEmojiToken" in source
    web = [(name, emoji_id, animated == "true") for name, emoji_id, animated, _ in WEB_EMOJI_ENTRY.findall(source)]

    config = _config_emojis()
    assert len(config) > 100
    assert web == config


def test_retired_owner_and_developer_emojis_are_removed():
    config = (ROOT / "src" / "config" / "emojis.py").read_text(encoding="utf-8")
    web = (ROOT / "web" / "src" / "data" / "botEmojis.ts").read_text(encoding="utf-8")
    owner = (ROOT / "src" / "cogs" / "staff" / "owner.py").read_text(encoding="utf-8")

    # These two old application emojis are retired; neither the bot nor the
    # rendering lab should still carry their names or ids.
    assert "badge_developer" not in config
    assert "bot_owner" not in config
    assert "badge_developer" not in web
    assert 'name: "bot_owner"' not in web
    assert not (ROOT / "src" / "assets" / "emojis" / "badge_developer.png").exists()
    assert not (ROOT / "src" / "assets" / "emojis" / "bot_owner.png").exists()

    # Owner-only command panels use the owner role badge instead.
    assert "get_emoji('bot_owner')" not in owner
    assert owner.count("get_emoji('badge_owner')") >= 2
    assert 'name: "badge_owner"' in web


def test_the_bot_cards_partner_badge_uses_the_profile_badge_asset():
    config = (ROOT / "src" / "config" / "emojis.py").read_text(encoding="utf-8")
    web = (ROOT / "web" / "src" / "data" / "botEmojis.ts").read_text(encoding="utf-8")
    cog = (ROOT / "src" / "cogs" / "info" / "cog.py").read_text(encoding="utf-8")
    build = (ROOT / "scripts" / "build-badge-art.mjs").read_text(encoding="utf-8")
    assets = ROOT / "src" / "assets" / "emojis"

    # The old partner emoji art did not match the rest of the set, so neither
    # the bot config nor the rendering lab carries it anymore.
    assert 'emoji_name == "partner"' not in config
    assert 'name: "partner"' not in web
    assert not (assets / "partner.png").exists()
    assert not (assets / "icon_partner.png").exists()

    # Its replacement is generated from the same profile badge asset the
    # website popups draw, so the bot card and the site match.
    assert 'emoji_name == "partner_badge"' in config
    assert 'name: "partner_badge"' in web
    assert (assets / "partner_badge.png").exists()
    assert 'partner_badge: "badges/partner.svg"' in build
    assert '(("partner",),                                    "partner_badge")' in cog


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
    route = (ROOT / "src" / "webapp" / "transcript_routes.py").read_text(encoding="utf-8")

    # The generated bot emoji list decides the popup layout, so an app emoji
    # never has to be guessed from its name.
    assert "const APPLICATION_EMOJI_IDS = new Set(BOT_EMOJIS.map((emoji) => emoji.id));" in markdown
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
    application = _md_to_html("<:hypesquad_bravery:1520827369508700252>")
    server = _md_to_html("<:drinking~1:123456789012345678>")

    # The popup needs the id for its own artwork and whether the emoji belongs
    # to the Niko application or to the ticket's server.
    assert 'data-emoji-id="1520827369508700252"' in application
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


def test_the_render_lab_tests_emoji_rendering_with_the_bots_own_emojis():
    source = (ROOT / "web" / "src" / "pages" / "RenderLabPage.tsx").read_text(encoding="utf-8")

    assert "BOT_EMOJIS.map(botEmojiToken).join" in source
    assert "{BOT_EMOJIS.map((emoji) =>" in source
    assert ">Custom emoji<" in source
    # The lab has to show the invalid case too, wrapped in real formatting.
    assert "<:not_a_real_emoji:" in source
    assert "<:deleted:0>" in source
    # ...and every marker whose formatting can be checked in the same line.
    assert "**bold** <:not_a_real_emoji:" in source
    assert "~~strike~~" in source
    assert "||spoiler||" in source
