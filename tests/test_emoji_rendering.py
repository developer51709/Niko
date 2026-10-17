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
