"""Regression checks for rich ticket transcript HTML output."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.tickets.transcripts import export_html


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
