"""Regression checks for rich ticket transcript HTML output."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.tickets.transcripts import _md_to_html, export_html


def test_export_html_renders_custom_emoji_and_stickers():
    html = export_html(
        [
            {
                "timestamp": "2026-01-01 00:00:00 UTC",
                "author": "Niko",
                "author_id": 1,
                "content": "hello <:coffee:123456> <a:wave:654321>",
                "stickers": [{"id": "987654", "name": "wave", "format_type": 1}],
            }
        ],
        {"channel_name": "ticket", "guild_name": "Server"},
    )

    assert 'cdn.discordapp.com/emojis/123456.png' in html
    assert 'cdn.discordapp.com/emojis/654321.gif' in html
    assert 'cdn.discordapp.com/stickers/987654.png' in html
    assert 'alt=":coffee:"' in html


def test_markdown_renders_discord_dynamic_timestamps():
    html = _md_to_html("Release <t:1788800225:f> (<t:1788800225:R>)")

    assert 'data-discord-ts="1788800225"' in html
    assert 'data-discord-style="f"' in html
    assert 'class="discord-timestamp"' in html
    assert "<t:1788800225:f>" not in html
    assert "discord-timestamp" in export_html(
        [{"timestamp": "now", "author": "Niko", "author_id": 1, "content": "<t:1788800225:f>"}],
        {"channel_name": "ticket", "guild_name": "Server"},
    )


def test_invalid_discord_timestamp_is_left_as_text():
    html = _md_to_html("<t:not-a-timestamp:f> <t:1788800225:x>")

    assert "&lt;t:not-a-timestamp:f&gt;" in html
    assert "&lt;t:1788800225:x&gt;" in html
