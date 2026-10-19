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


def test_markdown_draws_discord_blockquotes_without_the_marker():
    html = _md_to_html("> quoted\n>no space")

    # Adjacent lines are one quote with one bar, so the bar connects rather than
    # restarting (and rounding) on every line.
    assert html.count('<span class="tq">') == 1
    assert '<span class="tq">quoted<br>no space</span>' in html
    assert "&gt;" not in html


def test_markdown_separates_quote_runs_from_plain_lines():
    html = _md_to_html("> one\nplain\n> two\n> three")

    assert html.count('<span class="tq">') == 2
    assert '<span class="tq">one</span><br>plain<br><span class="tq">two<br>three</span>' in html


def test_markdown_renders_click_to_reveal_spoilers():
    html = _md_to_html("||secret|| and ||[link](https://example.com)||")

    assert html.count("data-discord-spoiler") == 2
    assert 'role="button"' in html
    assert 'aria-expanded="false"' in html
    assert 'href="https://example.com"' in html
    # A single pipe inside the hidden text does not end the spoiler early.
    assert '>a | b</span>' in _md_to_html("||a | b||")


def test_export_styles_role_mentions_and_spoilers_like_discord():
    page = export_html(
        [{"timestamp": "now", "author": "Staff", "author_id": 1, "content": "Hi <@&101> ||secret||"}],
        {"channel_name": "ticket", "guild_name": "Server"},
        {"role": {"101": "Helpers"}},
    )

    # Roles share the user/channel mention blue instead of their own purple.
    assert '.discord-md-mention-role { color: #dce4ff; background: rgba(88, 101, 242, .3); }' in page
    assert "#f1d7ff" not in page
    # A hidden spoiler hides its content and makes any link inside inert until
    # the spoiler itself has been clicked.
    assert ".discord-md-spoiler:not(.is-revealed) a { pointer-events: none; }" in page
    assert 'document.querySelectorAll("[data-discord-spoiler]").forEach(bindSpoiler);' in page
    assert 'spoiler.classList.add("is-revealed");' in page
    # One rounded bar spans a run of quote lines.
    assert '.tq::before { position: absolute; top: 0; bottom: 0; left: 0; width: 4px; background: #4e5058; border-radius: 4px;' in page


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


def test_export_groups_messages_and_separates_days_like_discord():
    html = export_html(
        [
            {"timestamp": "2026-10-15 15:03:00 UTC", "author": "Soren", "author_id": 101, "content": "first"},
            {"timestamp": "2026-10-15 15:04:00 UTC", "author": "Soren", "author_id": 101, "content": "second"},
            {"timestamp": "2026-10-15 15:20:00 UTC", "author": "Soren", "author_id": 101, "content": "after the group window"},
            {"timestamp": "2026-10-18 13:43:00 UTC", "author": "Kumie", "author_id": 202, "content": "a new day"},
        ],
        {"channel_name": "ticket", "guild_name": "Server"},
        {},
    )

    # Two calendar days get a labelled divider, and the repeated author inside
    # the seven-minute window loses its header and avatar the way Discord does.
    assert html.count('<div class="day-divider"') == 2
    assert "October 15, 2026" in html
    assert "October 18, 2026" in html
    assert html.count('<div class="message-head">') == 3
    assert html.count('<div class="message message-grouped"') == 1
    assert 'class="message-gutter-time"' in html
    assert ">3:04 PM</time>" in html
    assert "10/15/26, 3:03 PM</time>" in html


def test_export_makes_message_names_and_avatars_open_the_profile_popup():
    html = export_html(
        [{"timestamp": "2026-10-15 15:03:00 UTC", "author": "Soren", "author_id": 101, "content": "hello"}],
        {"channel_name": "ticket", "guild_name": "Server"},
        {},
    )

    # A name and avatar are buttons that carry the same user id the document
    # click handler uses for mention links, so both open the profile card.
    assert '<button type="button" class="message-avatar-button" data-discord-user-id="101"' in html
    assert '<button type="button" class="message-author" data-discord-user-id="101"' in html
    assert 'class="message-avatar message-avatar-fallback"' in html
    # Even without a live lookup the export carries a minimal profile, so the
    # card still opens instead of doing nothing.
    assert '"101": {"id": "101", "display_name": "Soren", "username": "Soren"}' in html
    assert "const mentionProfiles =" in html


def test_export_keeps_the_saved_server_display_name_in_the_chat_row():
    html = export_html(
        [{"timestamp": "2026-10-15 15:03:00 UTC", "author": "Soren \U0001f319 MOON", "author_id": 101, "content": "hello"}],
        {"channel_name": "ticket", "guild_name": "Server"},
        {},
        {"101": {"id": "101", "username": "soren", "display_name": "Soren", "avatar_url": None}},
    )

    # The chat row is what Discord showed in the server, while the profile card
    # still carries Discord's global name.
    assert '<span class="message-author-name">Soren \U0001f319 MOON</span>' in html
    assert '"display_name": "Soren"' in html


def test_export_renders_attachments_inside_the_message():
    html = export_html(
        [{
            "timestamp": "2026-10-15 15:03:00 UTC",
            "author": "Soren",
            "author_id": 101,
            "content": "look",
            "attachments": [
                "https://cdn.discordapp.com/attachments/1/2/screenshot.png",
                "https://cdn.discordapp.com/attachments/1/2/logs.zip",
            ],
        }],
        {"channel_name": "ticket", "guild_name": "Server"},
        {},
    )

    # Images get Discord's inline preview; other files keep their real name.
    assert 'class="message-attachment-image"' in html
    assert 'screenshot.png' in html
    assert 'class="message-attachment-file"' in html
    assert ">logs.zip</span>" in html


def test_export_popup_matches_the_discord_layout():
    profile = {
        "id": "456",
        "username": "liveuser",
        "display_name": "Live Nick",
        "avatar_url": "https://cdn.example/avatar.png",
        "avatar_decoration_url": "https://cdn.example/decoration.png",
        "banner_url": None,
        "banner_color": "#12abef",
        "bio": "Hello",
        "guild_tag": "MOON",
        "guild_badge_url": "https://cdn.example/badge.png",
        "server_tag": {
            "id": "999",
            "tag": "MOON",
            "badge_url": "https://cdn.example/badge.png",
            "available": True,
            "private": False,
            "name": "The Gamer Nation",
            "icon_url": "https://cdn.example/icon.png",
            "banner_url": None,
            "description": "Roleplay and gaming",
            "online_count": 33,
            "member_count": 72,
            "created_at": 1760000000,
            "invite_url": "https://discord.gg/gamernation",
            "viewer_is_member": False,
        },
        "guild_nick": "Server Nick",
        "custom_status": {
            "text": "Available for website and Discord bot work",
            "emoji_name": "\U0001f4bb",
            "emoji_id": None,
            "emoji_animated": False,
        },
        "badges": ["hypesquad_bravery", "hypesquad_balance"],
        "activities": [
            {
                "album_cover_url": "https://cdn.example/cover.jpg",
                "title": "Man Down",
                "artists": ["Eden Project"],
                "url": "https://open.spotify.com/track/x",
                "start": 1000,
                "end": 1315,
                "duration_seconds": 315,
            }
        ],
    }
    html = export_html(
        [{"timestamp": "now", "author": "Staff", "author_id": 1, "content": "Hi <@!456>"}],
        {"channel_name": "ticket", "guild_name": "Server"},
        {"user": {"456": "Live Nick"}},
        {"456": profile},
    )

    # The popup shows the Discord user, never a server-specific nickname.
    assert "Server name:" not in html
    # The avatar is a bare circle: no ring, decorations scaled 1.2x and centred.
    assert "border: 6px solid #111214" not in html
    assert "translate(-50%, -50%) scale(1.2)" in html
    # The custom status sits beside the avatar, and the "..." menu top-right.
    assert '<div class="discord-profile-head">' in html
    assert "Available for website and Discord bot work" in html
    assert 'class="discord-profile-menu-button"' in html
    assert "data-copy-user-id" in html
    assert ".discord-profile-menu { position: absolute; top: 8px; right: 8px" in html
    # The tag pill rides the username row, badges follow on their own row.
    assert '<p class="discord-profile-username"><span class="discord-profile-user-tag">' in html
    assert 'class="discord-profile-guild-tag"' in html
    assert "data-server-tag" in html
    assert "data:image/svg+xml;base64," in html
    # The tag opens Discord's server popup, which owns all three states.
    assert "discord-server-tag-popup" in html
    assert "The server has limited who can see this profile." in html
    assert "Unknown Server" in html
    assert "is-disabled" not in html
    # Members get Go to Server; non-members and guests get Join only when the
    # guild has a vanity invite, otherwise no button is rendered at all.
    assert ".discord-server-tag-invite.is-join" in html
    assert "const isMember = Boolean(server && server.viewer_is_member);" in html
    assert "const memberUrl = isMember && server && server.id" in html
    assert "const joinUrl = showDetails && !isMember && server ? server.invite_url : null;" in html
    assert '<a class="discord-server-tag-invite" href="' in html
    assert '>Go to Server</a>' in html
    assert '>Join</a>' in html
    # The Spotify card is drawn above the profile link and can tick its progress.
    assert "Listening to Spotify" in html
    assert "discord-profile-spotify-track" in html
    assert "setInterval(tick, 1000)" in html
    assert html.index("discord-profile-spotify") < html.index("discord-profile-full-link")


def test_export_inlines_every_profile_badge_and_sizes_them_bigger():
    from utils.member_badges import NIKO_BADGE_ORDER
    from utils.tickets import transcripts

    art = transcripts._profile_badge_art()
    assert set(art) == set(transcripts._PROFILE_BADGE_FILES)
    assert all(entry["src"].startswith("data:image/svg+xml;base64,") for entry in art.values())
    # Every badge the profile API can send has artwork behind it, including
    # Niko's own role badges next to Discord's.
    assert {
        "staff", "partner", "hypesquad_events", "bug_hunter_level_1", "bug_hunter_level_2",
        "hypesquad_bravery", "hypesquad_brilliance", "hypesquad_balance", "early_supporter",
        "early_verified_developer", "certified_moderator", "supports_commands",
        "active_developer", "boosting_1_months", "boosting_2_months", "boosting_3_months",
        "boosting_6_months", "boosting_9_months", "boosting_12_months",
        "boosting_15_months", "boosting_18_months", "boosting_24_months",
        *NIKO_BADGE_ORDER,
    } == set(art)

    html = export_html(
        [{"timestamp": "now", "author": "Staff", "author_id": 1, "content": "Hi <@!456>"}],
        {"channel_name": "ticket", "guild_name": "Server"},
        {"user": {"456": "Live Nick"}},
        {"456": {
            "id": "456", "username": "liveuser", "display_name": "Live Nick",
            "badges": [
                "staff", "supports_commands", "boosting_24_months",
                "niko_head_admin", "not_a_badge",
            ],
        }},
    )

    assert art["staff"]["src"] in html
    # Niko's own role badges inline the same way Discord's do.
    assert art["niko_head_admin"]["src"] in html
    assert "Head Admin" in html
    # The popup script reads the inlined art and labels, and ignores unknown keys.
    assert "const badge = badgeArt[key];" in html
    assert "if (!badge || !badge.src) return '';" in html
    assert "title=\"' + escapeHtml(badge.label) + '" in html
    assert "Boosting a server for 24 months" in html
    assert '.discord-profile-badge { width: 20px; height: 20px;' in html


def test_export_badge_popup_shows_the_art_name_and_description():
    from utils.tickets import transcripts

    art = transcripts._profile_badge_art()
    html = export_html(
        [{"timestamp": "now", "author": "Staff", "author_id": 1, "content": "Hi <@!456>"}],
        {"channel_name": "ticket", "guild_name": "Server"},
        {"user": {"456": "Live Nick"}},
        {"456": {
            "id": "456", "username": "liveuser", "display_name": "Live Nick",
            "badges": ["staff", "boosting_9_months", "niko_supporter"],
        }},
    )

    # Every badge carries a name and a description for the popup to show.
    assert all(entry["label"] and entry["description"] for entry in art.values())
    # A badge is a button, and clicking it opens the badge popup.
    assert 'class="discord-profile-badge-button" data-badge-key="' in html
    assert "badgeArt[button.dataset.badgeKey]" in html
    assert "badgesRow.addEventListener('click'" in html
    assert "button.getAttribute('aria-expanded') === 'true'" in html
    # The popup lays the badge art out on the left with the name and description
    # on the right, exactly like the website popup.
    assert "discord-badge-popup-art" in html
    assert "discord-badge-popup-copy" in html
    # The popup is appended to the page and fixed above the profile popup, so it
    # renders on top of the card instead of stretching it: no room is reserved
    # under the badge row for it.
    assert '.discord-badge-popup { position: fixed; z-index: 101;' in html
    assert "document.body.appendChild(popup);" in html
    assert "placeBadgePopup(button);" in html
    assert ":has(.discord-badge-popup)" not in html
    assert '.discord-badge-popup-copy { display: grid' in html
    assert art["staff"]["description"] in html
    assert art["boosting_9_months"]["description"] in html
    assert art["niko_supporter"]["description"] in html


def test_html_export_escapes_untrusted_live_profile_data():
    html = export_html(
        [{"content": "<@456>"}],
        {"channel_name": "ticket"},
        {"user": {"456": "<img src=x onerror=alert(1)>"}},
        {"456": {"id": "456", "username": "<script>bad</script>", "display_name": "<b>bad</b>", "avatar_url": None, "banner_url": None, "bio": "</script><script>alert(1)</script>", "guild_nick": None}},
    )

    assert "&lt;img src=x onerror=alert(1)&gt;" in html
    assert "</script><script>alert(1)</script>" not in html
    assert '"display_name": "<b>bad<\\/b>"' in html
    assert '"bio": "<\\/script><script>alert(1)<\\/script>"' in html


def test_invalid_discord_timestamp_is_left_as_text():
    html = _md_to_html("<t:not-a-timestamp:f> <t:1788800225:x>")

    assert "&lt;t:not-a-timestamp:f&gt;" in html
    assert "&lt;t:1788800225:x&gt;" in html


def test_export_popup_draws_the_presence_dot_from_inlined_art():
    from utils.tickets import transcripts

    art = transcripts._profile_status_art()
    assert set(art) == {"online", "idle", "dnd", "offline", "streaming"}
    assert [entry["label"] for entry in art.values()] == [
        "Online", "Idle", "Do Not Disturb", "Offline", "Streaming"
    ]
    assert all(entry["src"].startswith("data:image/png;base64,") for entry in art.values())

    page = export_html(
        [{"timestamp": "now", "author": "Staff", "author_id": 1, "content": "Hi <@!456>"}],
        {"channel_name": "ticket", "guild_name": "Server"},
        {"user": {"456": "Live Nick"}},
        {"456": {
            "id": "456", "username": "liveuser", "display_name": "Live Nick",
            "avatar_url": "https://cdn.example/avatar.png", "status": "dnd",
        }},
    )

    # A transcript is a single offline file, so every dot travels inline and the
    # popup never reaches for the web app's asset folder.
    assert "/assets/discord-status/" not in page
    assert all(entry["src"] in page for entry in art.values())
    assert ".discord-status-icon { position: absolute; right: 0; bottom: 0;" in page
    # The dot rides the avatar, and its alt/title name the status in words.
    assert '<img class="discord-status-icon" data-profile-status src="' in page
    assert 'const label = escapeHtml(art.label || "Offline");' in page
    # A profile Discord shares no presence for still shows the offline dot rather
    # than a blank avatar corner.
    assert 'return statusArt[name] ? name : "offline";' in page


def test_export_popup_refreshes_presence_while_the_card_is_open():
    page = export_html(
        [{"timestamp": "now", "author": "Staff", "author_id": 1, "content": "Hi <@!456>"}],
        {"channel_name": "ticket", "guild_name": "Server"},
        {"user": {"456": "Live Nick"}},
        {"456": {"id": "456", "username": "liveuser", "display_name": "Live Nick", "status": "online"}},
    )

    # An open card re-reads the same public endpoint the website popup polls, on
    # its own 5s timer and again whenever the tab comes back to the foreground.
    assert 'fetch("/api/discord/users/" + encodeURIComponent(profileId))' in page
    assert 'profilePollTimer = setInterval(() => { if (document.visibilityState === "visible") loadPresence(); }, 5000);' in page
    assert 'refreshProfilePresence = () => { if (document.visibilityState === "visible") loadPresence(); };' in page
    # Only over http(s): a transcript opened from disk keeps the embedded profile
    # instead of firing requests at an origin that does not serve the API.
    assert 'location.protocol.indexOf("http") === 0' in page
    assert 'typeof window.fetch === "function"' in page
    # A refresh replaces only the presence parts, so an open badge popup, the
    # "..." menu and the card's position all survive it.
    assert "head.innerHTML = profileAvatar(next) + profileStatusBubble(next);" in page
    assert "spotifyNode.innerHTML = nextSpotify.html;" in page
    assert "if (!next || !card.isConnected) return;" in page
    # A failed read keeps the last known presence rather than blanking the popup.
    assert ".catch(() => {});" in page
    # Closing the card tears the poll and its visibility listener down.
    assert "const closeProfile = () => { stopProfileTimer(); stopProfilePoll();" in page
    assert 'document.removeEventListener("visibilitychange", refreshProfilePresence);' in page


def test_export_popup_status_bubble_matches_discords_layout():
    page = export_html(
        [{"timestamp": "now", "author": "Staff", "author_id": 1, "content": "Hi <@!456>"}],
        {"channel_name": "ticket", "guild_name": "Server"},
        {"user": {"456": "Live Nick"}},
        {"456": {
            "id": "456", "username": "liveuser", "display_name": "Live Nick",
            "status": "online",
            "custom_status": {
                "text": None, "emoji_name": "\U0001f4bb", "emoji_id": None, "emoji_animated": False,
            },
        }},
    )

    # An emoji-only status is the compact square, not a text bubble.
    assert 'class="discord-profile-status is-emoji-only"' in page
    # Long text clamps to two lines and expands in place, like Discord's popup.
    assert "-webkit-line-clamp: 2" in page
    assert "bindStatusBubble(card);" in page
    assert "text.scrollHeight > text.clientHeight + 1" in page
    # The five-second presence poll rebuilds the bubble without collapsing a
    # status the reader has opened.
    assert "bindStatusBubble(card, wasExpanded);" in page
