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


def test_transcript_html_embeds_live_mention_names_and_profile_data():
    html = export_html(
        [{"timestamp": "now", "author": "Staff", "author_id": 1, "content": "Hi <@!456> in <#789> as <@&101>"}],
        {"channel_name": "ticket", "guild_name": "Server"},
        {"user": {"456": "Live Nick"}, "channel": {"789": "support"}, "role": {"101": "Helpers"}},
        {"456": {"id": "456", "username": "liveuser", "display_name": "Live Nick", "avatar_url": "https://cdn.example/avatar.png", "banner_url": None, "banner_color": "#12abef", "guild_tag": "NIKO", "guild_badge_url": "https://cdn.example/badge.png", "avatar_decoration_url": "https://cdn.example/decoration.png", "bio": "Hello"}},
    )

    assert '>\u0040Live Nick</a>' in html
    assert '>#support</span>' in html
    assert '>@Helpers</span>' in html
    assert '"456": {"id": "456", "username": "liveuser"' in html
    assert "profile.banner_color" in html
    assert "profile.banner_color.length === 7" in html
    assert 'class="discord-profile-guild-tag"' in html
    assert 'https://cdn.example/badge.png' in html
    assert 'https://cdn.example/decoration.png' in html
    assert 'data-discord-user-id="456"' in html
    assert "Loading Discord profile" not in html


def test_html_export_escapes_untrusted_live_profile_data():
    html = export_html(
        [{"content": "<@456>"}],
        {"channel_name": "ticket"},
        {"user": {"456": "<img src=x onerror=alert(1)>"}},
        {"456": {"id": "456", "username": "<script>bad</script>", "display_name": "<b>bad</b>", "avatar_url": None, "banner_url": None, "bio": "</script><script>alert(1)</script>", "guild_nick": None}},
    )

    assert "&lt;img src=x onerror=alert(1)&gt;" in html
    assert "</script><script>alert(1)</script>" not in html
    assert '"display_name": "<b>bad<\\\\/b>"' in html


def test_invalid_discord_timestamp_is_left_as_text():
    html = _md_to_html("<t:not-a-timestamp:f> <t:1788800225:x>")

    assert "&lt;t:not-a-timestamp:f&gt;" in html
    assert "&lt;t:1788800225:x&gt;" in html
