"""Web transcript storage and retrieval.

Transcripts are stored in the main database (MongoDB or SQLite) and served
through the Flask web API for browser-based viewing and multi-format downloads.
"""

from __future__ import annotations

import asyncio
import base64
import csv
import html as _html
import io
import json
import re
import hashlib
import time
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import unquote, urlparse

import aiohttp

# CV2 component type ids (Components v2 layout messages)
_TYPE_ACTION_ROW = 1
_TYPE_BUTTON = 2
_TYPE_SECTION = 9
_TYPE_TEXT_DISPLAY = 10
_TYPE_THUMBNAIL = 11
_TYPE_MEDIA_GALLERY = 12
_TYPE_SEPARATOR = 14
_TYPE_CONTAINER = 17
_TYPE_LABEL = 18


async def save_transcript(
    cxn,
    *,
    transcript_id: str,
    guild_id: int,
    channel_id: int,
    channel_name: str,
    opener_id: int,
    category: str,
    messages: List[Dict[str, Any]],
    claimed_by: Optional[int] = None,
) -> str:
    """Store a transcript and return its ID.

    Parameters
    ----------
    cxn:
        The bot's database pool (``bot.cxn``).
    transcript_id:
        A unique short ID for this transcript (e.g. first 8 chars of SHA-256).
    guild_id, channel_id, channel_name, opener_id, category:
        Metadata about the ticket.
    messages:
        List of message dicts with ``timestamp``, ``author``, ``author_id``,
        ``content``, ``attachments``, ``embeds`` and ``components`` keys.
    claimed_by:
        User ID of the support member who claimed the ticket, if any.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    await cxn.execute(
        "INSERT INTO transcripts "
        "(transcript_id, guild_id, channel_id, channel_name, opener_id, "
        "category, claimed_by, message_count, messages, created_at) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
        transcript_id,
        guild_id,
        channel_id,
        channel_name,
        opener_id,
        category,
        claimed_by,
        len(messages),
        json.dumps(messages),
        now,
    )
    return transcript_id


async def get_transcript(cxn, transcript_id: str) -> Optional[dict]:
    """Fetch a transcript by its short ID."""
    row = await cxn.fetchrow(
        "SELECT * FROM transcripts WHERE transcript_id = $1",
        transcript_id,
    )
    if row is None:
        return None
    result = dict(row)
    # Parse messages JSON
    messages = result.get("messages")
    if isinstance(messages, str):
        try:
            result["messages"] = json.loads(messages)
        except (json.JSONDecodeError, TypeError):
            result["messages"] = []
    return result


async def get_guild_transcripts(
    cxn, guild_id: int, limit: int = 50, offset: int = 0
) -> List[dict]:
    """Fetch recent transcripts for a guild."""
    rows = await cxn.fetch(
        "SELECT transcript_id, guild_id, channel_name, opener_id, "
        "category, claimed_by, message_count, created_at "
        "FROM transcripts WHERE guild_id = $1 "
        "ORDER BY created_at DESC LIMIT $2 OFFSET $3",
        guild_id, limit, offset,
    )
    return [dict(row) for row in rows]


def generate_transcript_id(guild_id: int, channel_id: int, timestamp: float) -> str:
    """Generate a short unique transcript ID."""
    raw = f"{guild_id}-{channel_id}-{timestamp}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def _image_data_url(payload: bytes, content_type: str) -> str:
    """Encode downloaded image bytes for an offline HTML transcript."""
    media_type = content_type.split(";", 1)[0].strip().lower()
    if not media_type.startswith("image/"):
        media_type = "image/png"
    return f"data:{media_type};base64,{base64.b64encode(payload).decode('ascii')}"


# Badge artwork ships with the web app, but an exported transcript is a single
# offline file, so the SVGs are inlined instead of linked. Each entry is the
# path under ``web/public/assets`` plus the name and description the badge popup
# shows, and the keys are exactly the ones the profile API sends. The same three
# pieces live in web/src/data/profileBadges.ts for the website popups.
_PROFILE_BADGE_FILES = {
    # Discord's own profile badges.
    "staff": ("badges/staff.svg", "Discord Staff", "Part of the Discord team."),
    "partner": ("badges/partner.svg", "Partnered Server Owner", "Owns a server that is partnered with Discord."),
    "hypesquad_events": ("hypesquad/events.svg", "HypeSquad Events", "Helped host an official HypeSquad event."),
    "bug_hunter_level_1": ("badges/bug_hunter_level_1.svg", "Bug Hunter", "Reported a valid bug to Discord."),
    "hypesquad_bravery": ("hypesquad/bravery.svg", "HypeSquad Bravery", "Member of House Bravery."),
    "hypesquad_brilliance": ("hypesquad/brilliance.svg", "HypeSquad Brilliance", "Member of House Brilliance."),
    "hypesquad_balance": ("hypesquad/balance.svg", "HypeSquad Balance", "Member of House Balance."),
    "early_supporter": ("badges/early_supporter.svg", "Early Supporter", "Supported Discord before October 10, 2018."),
    "bug_hunter_level_2": ("badges/bug_hunter_level_2.svg", "Bug Hunter (Gold)", "Reported several valid bugs to Discord."),
    "early_verified_developer": (
        "badges/early_verified_developer.svg",
        "Early Verified Bot Developer",
        "Verified bot developer before August 19, 2020.",
    ),
    "certified_moderator": (
        "badges/certified_moderator.svg",
        "Moderator Programs Alumni",
        "Took part in Discord's Moderator Programs.",
    ),
    "supports_commands": ("badges/supports_commands.svg", "Supports Commands", "This app supports slash commands."),
    "active_developer": ("badges/active_developer.svg", "Active Developer", "Ran a slash command in the past 30 days."),
    # Niko's own role badges, next to Discord's the way the bot's card lists
    # them. Every key here also exists in utils/member_badges.py.
    "niko_owner": ("badges/niko_owner.svg", "Niko Owner", "Owns and runs Niko."),
    "niko_staff": ("badges/niko_staff.svg", "Niko Staff", "Part of the Niko team."),
    "niko_head_admin": ("badges/niko_head_admin.svg", "Head Admin", "Leads Niko's moderation team."),
    "niko_moderator": ("badges/niko_moderator.svg", "Moderator", "Keeps Niko's servers in order."),
    "niko_head_support": ("badges/niko_head_support.svg", "Head of Support", "Leads the Niko support team."),
    "niko_support": ("badges/niko_support.svg", "Support Team", "Answers tickets and helps members."),
    "niko_graphic_designer": ("badges/niko_graphic_designer.svg", "Graphic Designer", "Draws Niko's art and brand."),
    "niko_event_coordinator": ("badges/niko_event_coordinator.svg", "Event Coordinator", "Runs Niko's community events."),
    "niko_partnerships_promotions_lead": (
        "badges/niko_partnerships_promotions_lead.svg",
        "Partnerships & Promotions Lead",
        "Leads partnerships and promotions.",
    ),
    "niko_partnership_manager": ("badges/niko_partnership_manager.svg", "Partnership Manager", "Manages Niko's partner servers."),
    "niko_supporter": ("badges/niko_supporter.svg", "Supporter", "Donated to keep Niko's hosting running."),
    "niko_bug_hunter": ("badges/niko_bug_hunter.svg", "Bug Bounty Hunter", "Reported a bug that made Niko better."),
    "niko_partner": ("badges/niko_partner.svg", "Partner", "Owns a server partnered with Niko."),
    # Discord draws a different boosting badge for every tier, so every tier has
    # its own art, name and description here too.
    **{
        f"boosting_{months}_months": (
            f"badges/boosting_{months}_months.svg",
            f"Boosting a server for {months} month{'s' if months != 1 else ''}",
            f"Boosted a server for {months} month{'s' if months != 1 else ''}. "
            "The badge art upgrades at 1, 2, 3, 6, 9, 12, 15, 18 and 24 months.",
        )
        for months in (1, 2, 3, 6, 9, 12, 15, 18, 24)
    },
}


@lru_cache(maxsize=1)
def _profile_badge_art() -> dict:
    """Data URLs for the badges, keyed by the keys the profile API sends."""
    assets = Path(__file__).resolve().parents[3] / "web" / "public" / "assets"
    art = {}
    for key, (relative, label, description) in _PROFILE_BADGE_FILES.items():
        try:
            svg = (assets / relative).read_bytes()
        except OSError:
            continue
        art[key] = {
            "src": _image_data_url(svg, "image/svg+xml"),
            "label": label,
            "description": description,
        }
    return art


# Discord's presence dots ship with the web app too, but an exported transcript
# is a single offline file, so the PNGs are inlined exactly like the badges. The
# keys are the status names the profile API sends, and the labels are the wording
# the website popup and the Team page already use.
_PROFILE_STATUS_FILES = {
    "online": ("discord-status/status_online.png", "Online"),
    "idle": ("discord-status/status_idle.png", "Idle"),
    "dnd": ("discord-status/status_dnd.png", "Do Not Disturb"),
    "offline": ("discord-status/status_offline.png", "Offline"),
    "streaming": ("discord-status/status_streaming.png", "Streaming"),
}


@lru_cache(maxsize=1)
def _profile_status_art() -> dict:
    """Data URLs for the presence dots, keyed by the status the API sends."""
    assets = Path(__file__).resolve().parents[3] / "web" / "public" / "assets"
    art = {}
    for key, (relative, label) in _PROFILE_STATUS_FILES.items():
        try:
            png = (assets / relative).read_bytes()
        except OSError:
            continue
        art[key] = {"src": _image_data_url(png, "image/png"), "label": label}
    return art


async def inline_transcript_images(messages: List[dict], *, max_bytes: int = 12 * 1024 * 1024) -> int:
    """Replace Discord-hosted transcript images with base64 data URLs.

    Discord CDN URLs can stop working after a message or channel is removed.
    Downloading these images while the ticket still exists makes HTML exports
    self-contained and usable without an internet connection.
    """
    urls: set[str] = set()

    def add_media(media: Any) -> None:
        if isinstance(media, dict):
            url = media.get("url") or media.get("proxy_url")
            if isinstance(url, str) and url.startswith(("http://", "https://")):
                urls.add(url)

    for message in messages:
        for sticker in message.get("stickers") or []:
            if not isinstance(sticker, dict) or not sticker.get("id"):
                continue
            sticker_url = sticker.get("url") or (
                f"https://cdn.discordapp.com/stickers/{sticker['id']}."
                f"{'gif' if sticker.get('format_type') == 4 else 'png'}"
            )
            if isinstance(sticker_url, str) and sticker_url.startswith(("http://", "https://")):
                urls.add(sticker_url)
        for url in message.get("attachments") or []:
            if isinstance(url, str) and url.startswith(("http://", "https://")):
                urls.add(url)
        for embed in message.get("embeds") or []:
            if not isinstance(embed, dict):
                continue
            add_media(embed.get("image"))
            add_media(embed.get("thumbnail"))
            add_media(embed.get("author"))
            add_media(embed.get("footer"))
        def collect_components(components: Any) -> None:
            for component in components or []:
                if not isinstance(component, dict):
                    continue
                add_media(component.get("media"))
                collect_components(component.get("components"))
                if component.get("accessory"):
                    collect_components([component["accessory"]])
        collect_components(message.get("components"))

    if not urls:
        return 0

    timeout = aiohttp.ClientTimeout(total=20)
    semaphore = asyncio.Semaphore(6)
    downloaded: dict[str, str] = {}

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async def fetch(url: str) -> None:
            async with semaphore:
                try:
                    async with session.get(url) as response:
                        if response.status != 200:
                            return
                        content_type = response.headers.get("Content-Type", "")
                        if not content_type.lower().startswith("image/"):
                            return
                        payload = await response.read()
                        if 0 < len(payload) <= max_bytes:
                            downloaded[url] = _image_data_url(payload, content_type)
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    return

        await asyncio.gather(*(fetch(url) for url in urls))

    if not downloaded:
        return 0

    def replace_media(media: Any) -> None:
        if not isinstance(media, dict):
            return
        original = media.get("url") or media.get("proxy_url")
        if original in downloaded:
            media["url"] = downloaded[original]
            media.pop("proxy_url", None)

    for message in messages:
        attachments = message.get("attachments") or []
        message["attachments"] = [downloaded.get(url, url) for url in attachments]
        for sticker in message.get("stickers") or []:
            if not isinstance(sticker, dict):
                continue
            original = sticker.get("url")
            if not original and sticker.get("id"):
                original = (
                    f"https://cdn.discordapp.com/stickers/{sticker['id']}."
                    f"{'gif' if sticker.get('format_type') == 4 else 'png'}"
                )
            if original in downloaded:
                sticker["url"] = downloaded[original]
        for embed in message.get("embeds") or []:
            if not isinstance(embed, dict):
                continue
            for key in ("image", "thumbnail", "author", "footer"):
                replace_media(embed.get(key))
        def replace_components(components: Any) -> None:
            for component in components or []:
                if not isinstance(component, dict):
                    continue
                replace_media(component.get("media"))
                replace_components(component.get("components"))
                if component.get("accessory"):
                    replace_components([component["accessory"]])
        replace_components(message.get("components"))
    return len(downloaded)


# ── Shared render helpers ───────────────────────────────────────────────────


def _esc(value: Any) -> str:
    """Escape a value for safe HTML embedding."""
    return _html.escape("" if value is None else str(value), quote=True)


def _color_css(color) -> str:
    """Convert an int/hex color into a CSS color string."""
    if color is None:
        return ""
    try:
        color = int(color)
    except (TypeError, ValueError):
        return ""
    if not (0 <= color <= 0xFFFFFF):
        return ""
    return f"#{color:06x}"


def _media_url(media: Optional[dict]) -> str:
    """Best URL for a media payload (prefer real url over proxy)."""
    if not isinstance(media, dict):
        return ""
    return media.get("url") or media.get("proxy_url") or ""


def _is_image_url(url: str) -> bool:
    """Heuristic image check on a URL or content type."""
    if url.startswith("data:image/"):
        return True
    return bool(re.search(r"\.(?:png|jpe?g|gif|webp|bmp|svg)(?:[?#]|$)", url, re.I))


def _is_video_url(url: str) -> bool:
    """Heuristic video check on a URL or content type."""
    if url.startswith("data:video/"):
        return True
    return bool(re.search(r"\.(?:mp4|webm|mov|m4v|ogg)(?:[?#]|$)", url, re.I))


def _discord_timestamp_text(unix: int, style: str) -> Optional[str]:
    """Return a readable UTC fallback for a Discord dynamic timestamp."""
    if style not in {"t", "T", "d", "D", "f", "F", "R"}:
        return None
    try:
        value = datetime.fromtimestamp(unix, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None
    if style == "R":
        seconds = unix - int(time.time())
        absolute = abs(seconds)
        if absolute < 60:
            amount, unit = seconds, "second"
        elif absolute < 3600:
            amount, unit = round(seconds / 60), "minute"
        elif absolute < 86400:
            amount, unit = round(seconds / 3600), "hour"
        elif absolute < 604800:
            amount, unit = round(seconds / 86400), "day"
        elif absolute < 2592000:
            amount, unit = round(seconds / 604800), "week"
        elif absolute < 31536000:
            amount, unit = round(seconds / 2592000), "month"
        else:
            amount, unit = round(seconds / 31536000), "year"
        suffix = "s" if abs(amount) != 1 else ""
        return f"in {abs(amount)} {unit}{suffix}" if amount >= 0 else f"{abs(amount)} {unit}{suffix} ago"
    if style == "t":
        return value.strftime("%-I:%M %p UTC")
    if style == "T":
        return value.strftime("%-I:%M:%S %p UTC")
    if style == "d":
        return value.strftime("%m/%d/%Y")
    if style == "D":
        return value.strftime("%B %-d, %Y")
    if style == "F":
        return value.strftime("%A, %B %-d, %Y %-I:%M %p UTC")
    return value.strftime("%b %-d, %Y %-I:%M %p UTC")


@lru_cache(maxsize=1)
def _application_emoji_ids() -> frozenset[str]:
    """Every emoji registered to the Niko application, from the bot config."""
    config = Path(__file__).resolve().parents[3] / "src" / "config" / "emojis.py"
    try:
        text = config.read_text(encoding="utf-8")
    except OSError:
        return frozenset()
    return frozenset(re.findall(r"<a?:[A-Za-z0-9_~]+:(\d+)>", text))


def _md_to_html(text: Any, mention_names: dict | None = None) -> str:
    """Convert a light markdown subset into safe HTML.

    Supports bold, italics, underline, strikethrough, inline code, links and
    blockquote / small-text prefixes.  Everything is HTML-escaped first, so
    untrusted message content can never inject markup.
    """
    value = _esc(text)
    if not value:
        return ""

    code_holders: Dict[str, str] = {}

    def _protect_code(match: "re.Match[str]") -> str:
        key = f"\u0000{len(code_holders)}\u0000"
        code_holders[key] = f"<code>{match.group(1)}</code>"
        return key

    value = re.sub(r"`([^`\n]+)`", _protect_code, value)

    def _link(match: "re.Match[str]") -> str:
        label, url = match.group(1), match.group(2)
        if url.startswith(("http://", "https://")):
            return f'<a href="{_esc(url)}" target="_blank" rel="noopener noreferrer">{label}</a>'
        return label

    value = re.sub(r"\[([^\[\]\n]+)\]\((https?://[^\s)\]]+)\)", _link, value)
    value = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", value)
    value = re.sub(r"__([^_\n]+)__", r"<u>\1</u>", value)
    value = re.sub(r"~~([^~\n]+)~~", r"<s>\1</s>", value)

    # Discord spoilers stay hidden until clicked. The link inside a spoiler is
    # inert while hidden, so a spoiler can never be used to trick someone into
    # opening a link they have not chosen to reveal.
    def _spoiler(match: "re.Match[str]") -> str:
        return (
            '<span class="discord-md-spoiler" role="button" tabindex="0" '
            'aria-expanded="false" aria-label="Spoiler, click to reveal" '
            f'data-discord-spoiler>{match.group(1)}</span>'
        )

    # Stop at the closing ``||`` while still allowing a single pipe (and table
    # syntax) inside the hidden text.
    value = re.sub(r"\|\|((?:(?!\|\|)[^\n])+)\|\|", _spoiler, value)

    # Discord custom emoji are stored in message content as <:name:id> or
    # <a:name:id>. Render the CDN asset instead of exposing the raw token.
    def _custom_emoji(match: "re.Match[str]") -> str:
        animated = match.group(1) == "a"
        name = match.group(2)
        emoji_id = match.group(3)
        extension = "gif" if animated else "png"
        url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{extension}"
        is_application = emoji_id in _application_emoji_ids()
        return (
            f'<img class="custom-emoji" src="{url}" alt=":{name}:" title=":{name}:" '
            f'data-emoji-name="{name}" data-emoji-id="{emoji_id}" '
            f'data-emoji-animated="{str(animated).lower()}" '
            f'data-emoji-app="{1 if is_application else 0}" '
            'role="button" tabindex="0" aria-haspopup="dialog" aria-expanded="false" '
            f'aria-label=":{name}: emoji">'
        )

    value = re.sub(r"&lt;(a?):([A-Za-z0-9_~]+):(\d+)&gt;", _custom_emoji, value)

    def _timestamp(match: "re.Match[str]") -> str:
        unix = int(match.group(1))
        style = match.group(2)
        raw = f"&lt;t:{unix}:{style}&gt;"
        formatted = _discord_timestamp_text(unix, style)
        if formatted is None:
            return raw
        return (
            f'<time class="discord-timestamp" datetime="{unix}" '
            f'data-discord-ts="{unix}" data-discord-style="{style}" '
            f'title="{raw}">{_esc(formatted)}</time>'
        )

    value = re.sub(r"&lt;t:(-?\d+):([tTdDfFR])&gt;", _timestamp, value)

    def _mention(match: "re.Match[str]") -> str:
        raw_id = match.group(1) or match.group(2) or match.group(3)
        kind = "user" if match.group(1) else "role" if match.group(2) else "channel"
        label = (mention_names or {}).get(kind, {}).get(raw_id)
        safe_label = _esc(label or raw_id)
        if kind == "user":
            return f'<a class="discord-md-mention discord-md-mention-user" href="https://discord.com/users/{raw_id}" data-discord-user-id="{raw_id}" role="button" tabindex="0">@{safe_label}</a>'
        css_kind = "channel" if kind == "channel" else "role"
        prefix = "#" if kind == "channel" else "@"
        return f'<span class="discord-md-mention discord-md-mention-{css_kind}">{prefix}{safe_label}</span>'

    value = re.sub(r"&lt;@!?(\d+)&gt;|&lt;@&amp;(\d+)&gt;|&lt;#(\d+)&gt;", _mention, value)

    lines = value.split("\n")
    html_lines = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.lstrip()
        if stripped.startswith("&gt;"):
            # Consecutive quoted lines are one quote in Discord: the left bar
            # runs down the whole run and rounds only at its two ends.
            quote_lines = []
            while index < len(lines):
                current = lines[index].lstrip()
                if not current.startswith("&gt;"):
                    break
                quote_lines.append(current[4:].lstrip())
                index += 1
            html_lines.append(f'<span class="tq">{"<br>".join(quote_lines)}</span>')
            continue
        if stripped.startswith("-# "):
            html_lines.append(f'<span class="tsm">{stripped[3:]}</span>')
        elif re.match(r"#{1,4}\s", stripped):
            html_lines.append(f'<span class="th">{stripped}</span>')
        else:
            html_lines.append(line)
        index += 1
    value = "<br>".join(html_lines)

    for key, replacement in code_holders.items():
        value = value.replace(key, replacement)
    return value


def _embed_to_html(embed: dict, mention_names: dict | None = None) -> str:
    """Render a single embed payload into an HTML block."""
    color = _color_css(embed.get("color"))
    style = f"border-left-color: {color};" if color else ""
    parts = []

    author = embed.get("author") or {}
    if author.get("name"):
        icon = author.get("icon_url") or author.get("proxy_icon_url")
        icon_html = f'<img class="embed-author-icon" src="{_esc(icon)}" alt="">' if icon else ""
        parts.append(f'<div class="embed-author">{icon_html}{_esc(author.get("name"))}</div>')

    title = embed.get("title")
    if title:
        title_html = _esc(title)
        embed_url = embed.get("url")
        if embed_url and embed_url.startswith(("http://", "https://")):
            title_html = f'<a href="{_esc(embed_url)}" target="_blank" rel="noopener noreferrer">{title_html}</a>'
        parts.append(f'<div class="embed-title">{title_html}</div>')

    desc = embed.get("description")
    if desc:
        parts.append(f'<div class="embed-desc">{_md_to_html(desc, mention_names)}</div>')

    fields = embed.get("fields") or []
    if fields:
        field_html = []
        for field in fields:
            name = field.get("name", "")
            value = field.get("value", "")
            cls = "embed-field embed-field-inline" if field.get("inline") else "embed-field"
            field_html.append(
                f'<div class="{cls}"><div class="embed-field-name">{_md_to_html(name, mention_names)}</div>'
                f'<div class="embed-field-value">{_md_to_html(value, mention_names)}</div></div>'
            )
        parts.append(f'<div class="embed-fields">{"".join(field_html)}</div>')

    image = embed.get("image") or {}
    img_url = image.get("url") or image.get("proxy_url")
    if img_url:
        parts.append(
            f'<a class="embed-image-wrap" href="{_esc(img_url)}" target="_blank" rel="noopener noreferrer">'
            f'<img class="embed-image" src="{_esc(img_url)}" alt=""></a>'
        )

    footer_html = ""
    footer = embed.get("footer") or {}
    if footer.get("text"):
        icon = footer.get("icon_url") or footer.get("proxy_icon_url")
        icon_html = f'<img class="embed-footer-icon" src="{_esc(icon)}" alt="">' if icon else ""
        footer_html = f'<div class="embed-footer">{icon_html}{_esc(footer.get("text"))}</div>'

    timestamp = embed.get("timestamp")
    if timestamp:
        footer_html += f'<span class="embed-ts">{_esc(str(timestamp).replace("T", " ").replace("+00:00", " UTC"))}</span>'

    thumbnail = embed.get("thumbnail") or {}
    thumb_url = thumbnail.get("url") or thumbnail.get("proxy_url")
    thumb_html = ""
    if thumb_url:
        thumb_html = (
            f'<a class="embed-thumb" href="{_esc(thumb_url)}" target="_blank" rel="noopener noreferrer">'
            f'<img src="{_esc(thumb_url)}" alt=""></a>'
        )

    return (
        f'<div class="embed" style="{style}">'
        f'<div class="embed-body">{"".join(parts)}'
        f'<div class="embed-foot">{footer_html}</div>'
        f'</div>{thumb_html}</div>'
    )


def _component_children(component: dict) -> List[dict]:
    """Child payloads of a container-like component."""
    children = list(component.get("components") or [])
    accessory = component.get("accessory")
    if accessory:
        children.append(accessory)
    return children


def _component_to_html(component: dict, mention_names: dict | None = None) -> str:
    """Recursively render one CV2 component payload into HTML."""
    ctype = component.get("type")
    if ctype == _TYPE_CONTAINER:
        accent = _color_css(component.get("accent_color"))
        style = f"border-color: {accent};" if accent else ""
        bar = f'<div class="cv2-bar" style="background:{accent};"></div>' if accent else ""
        inner = "".join(_component_to_html(c, mention_names) for c in _component_children(component))
        return (
            f'<div class="cv2-card" style="{style}">{bar}'
            f'<div class="cv2-card-inner">{inner}</div></div>'
        )
    if ctype == _TYPE_ACTION_ROW:
        inner = "".join(_component_to_html(c, mention_names) for c in _component_children(component))
        return f'<div class="cv2-row">{inner}</div>'
    if ctype == _TYPE_BUTTON:
        style = component.get("style")
        url = component.get("url") or ""
        label = component.get("label") or ""
        emoji = component.get("emoji") or {}
        emoji_name = emoji.get("name") or ""
        label_html = _esc(f"{emoji_name} {label}".strip())
        if style == 5 and url.startswith(("http://", "https://")):
            return f'<a class="cv2-btn cv2-btn-link" href="{_esc(url)}" target="_blank" rel="noopener noreferrer">{label_html}</a>'
        disabled = " cv2-btn-disabled" if component.get("disabled") else ""
        return f'<span class="cv2-btn{disabled}">{label_html}</span>'
    if ctype == _TYPE_SECTION:
        children = [c for c in _component_children(component)]
        main = "".join(_component_to_html(c, mention_names) for c in children)
        return f'<div class="cv2-section">{main}</div>'
    if ctype == _TYPE_TEXT_DISPLAY:
        return f'<div class="cv2-text">{_md_to_html(component.get("content"), mention_names)}</div>'
    if ctype == _TYPE_LABEL:
        return f'<div class="cv2-label">{_md_to_html(component.get("content"), mention_names)}</div>'
    if ctype == _TYPE_SEPARATOR:
        if component.get("divider", True):
            return '<div class="cv2-sep"></div>'
        return '<div class="cv2-sep cv2-sep-spacer"></div>'
    if ctype == _TYPE_THUMBNAIL:
        media = component.get("media") or {}
        url = _media_url(media)
        if not url:
            return ""
        return (
            f'<span class="cv2-thumb"><a href="{_esc(url)}" target="_blank" rel="noopener noreferrer">'
            f'<img src="{_esc(url)}" alt=""></a></span>'
        )
    if ctype == _TYPE_MEDIA_GALLERY:
        items_html = []
        for item in component.get("items") or []:
            media = item.get("media") or {}
            url = _media_url(media)
            if not url:
                continue
            desc = item.get("description")
            desc_html = f'<figcaption>{_md_to_html(desc, mention_names)}</figcaption>' if desc else ""
            content_type = media.get("content_type") or ""
            if content_type.startswith("video/") or _is_video_url(url):
                items_html.append(
                    f'<figure class="cv2-media-item"><video src="{_esc(url)}" controls preload="metadata"></video>'
                    f'{desc_html}</figure>'
                )
            else:
                items_html.append(
                    f'<figure class="cv2-media-item"><a href="{_esc(url)}" target="_blank" rel="noopener noreferrer">'
                    f'<img src="{_esc(url)}" alt=""></a>{desc_html}</figure>'
                )
        if not items_html:
            return ""
        return f'<div class="cv2-gallery">{"".join(items_html)}</div>'
    return ""


def _components_to_html(components: List[dict], mention_names: dict | None = None) -> str:
    return "".join(_component_to_html(c, mention_names) for c in components)


def _flatten_message_text(msg: dict, indented: bool = False) -> List[str]:
    """Human-readable lines for txt/csv export covering all message content."""
    prefix = "  " if indented else ""
    lines = []
    content = msg.get("content", "")
    if content:
        lines.append(f"{prefix}Content: {content}")

    for url in msg.get("attachments") or []:
        lines.append(f"{prefix}Attachment: {url}")

    for embed in msg.get("embeds") or []:
        if not isinstance(embed, dict):
            continue
        bits = []
        author = (embed.get("author") or {}).get("name")
        if author:
            bits.append(author)
        if embed.get("title"):
            bits.append(embed["title"])
        if embed.get("description"):
            bits.append(embed["description"])
        for field in embed.get("fields") or []:
            name = field.get("name")
            value = field.get("value")
            if name or value:
                bits.append(f"{name}: {value}".strip())
        if bits:
            lines.append(f"{prefix}Embed: " + " | ".join(bits))
        for key in ("image", "thumbnail"):
            media = embed.get(key) or {}
            url = _media_url(media)
            if url:
                lines.append(f"{prefix}Embed {key}: {url}")

    for line in _flatten_component_text(msg.get("components") or [], prefix):
        lines.append(line)
    return lines


def _flatten_component_text(components: List[dict], prefix: str = "") -> List[str]:
    """Flatten CV2 components into readable text lines."""
    lines = []
    for component in components:
        if not isinstance(component, dict):
            continue
        ctype = component.get("type")
        if ctype == _TYPE_TEXT_DISPLAY:
            content = (component.get("content") or "").strip()
            if content:
                lines.append(f"{prefix}{content}")
        elif ctype == _TYPE_LABEL:
            content = (component.get("content") or "").strip()
            if content:
                lines.append(f"{prefix}◈ {content}")
        elif ctype == _TYPE_BUTTON:
            label = component.get("label") or ""
            url = component.get("url") or ""
            if url:
                lines.append(f"{prefix}▸ {label} ({url})")
            elif label:
                lines.append(f"{prefix}▸ {label}")
        elif ctype == _TYPE_THUMBNAIL:
            url = _media_url(component.get("media"))
            if url:
                lines.append(f"{prefix}Image: {url}")
        elif ctype == _TYPE_MEDIA_GALLERY:
            for item in component.get("items") or []:
                url = _media_url(item.get("media"))
                if not url:
                    continue
                desc = item.get("description")
                lines.append(f"{prefix}Media: {url}" + (f" ({desc})" if desc else ""))
        elif ctype in (_TYPE_CONTAINER, _TYPE_ACTION_ROW, _TYPE_SECTION):
            lines.extend(_flatten_component_text(_component_children(component), prefix))
    return lines


# ── Format exporters ────────────────────────────────────────────────────────


def export_txt(messages: List[dict]) -> str:
    """Plain text format — one line per message."""
    lines = []
    for msg in messages:
        ts = msg.get("timestamp", "")
        author = msg.get("author", "Unknown")
        content = msg.get("content", "")
        lines.append(f"[{ts}] {author}: {content}".rstrip())
        lines.extend(_flatten_message_text(msg, indented=True))
        lines.append("")
    return "\n".join(lines).strip()


_AVATAR_COLORS = ("#5865f2", "#3ba55d", "#faa61a", "#ed4245", "#eb459e", "#9b59b6")
_GROUP_WINDOW_SECONDS = 7 * 60


def _parse_transcript_time(value: Any) -> Optional[datetime]:
    """Return an aware timestamp for a stored transcript time, if it parses."""
    raw = str(value or "").strip()
    if not raw or raw.lower() == "now":
        return None
    normalized = raw[:-4] + "+00:00" if raw.endswith(" UTC") else raw
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        parsed = None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%m/%d/%Y %I:%M %p"):
            try:
                parsed = datetime.strptime(raw, fmt)
                break
            except ValueError:
                continue
    if parsed is None:
        return None
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def _message_clock(value: datetime) -> str:
    return value.strftime("%m/%d/%y, %-I:%M %p")


def _day_divider_label(value: datetime) -> str:
    return value.strftime("%B %-d, %Y")


def _message_avatar_html(name: str, author_id: str, avatar_url: Any) -> str:
    if avatar_url:
        visual = (
            f'<img class="message-avatar" src="{_esc(avatar_url)}" alt="" '
            'loading="lazy" referrerpolicy="no-referrer">'
        )
    else:
        initial = next((char for char in str(name) if char.isalnum()), "?")
        color = _AVATAR_COLORS[sum(ord(char) for char in str(author_id or name)) % len(_AVATAR_COLORS)]
        visual = f'<span class="message-avatar message-avatar-fallback" style="background:{color}">{_esc(initial.upper())}</span>'
    if author_id:
        return (
            f'<button type="button" class="message-avatar-button" '
            f'data-discord-user-id="{_esc(author_id)}" title="View {_esc(name)} profile" '
            f'aria-label="View {_esc(name)} profile">{visual}</button>'
        )
    return f'<span class="message-avatar-button" aria-hidden="true">{visual}</span>'


def _message_name_html(name: str, author_id: str) -> str:
    label = f'<span class="message-author-name">{_esc(name)}</span>'
    if author_id:
        return (
            f'<button type="button" class="message-author" '
            f'data-discord-user-id="{_esc(author_id)}" title="View {_esc(name)} profile">{label}</button>'
        )
    return f'<span class="message-author">{label}</span>'


def _message_guild_tag_html(profile: dict) -> str:
    tag = str(profile.get("guild_tag") or "").strip()
    if not tag:
        return ""
    badge = profile.get("guild_badge_url")
    art = f'<img src="{_esc(badge)}" alt="" loading="lazy">' if badge else ""
    return f'<span class="message-guild-tag">{art}<span>{_esc(tag)}</span></span>'


def _attachment_html(url: Any) -> str:
    value = str(url or "")
    if not value:
        return ""
    safe = _esc(value)
    if _is_image_url(value):
        return (
            f'<a class="message-attachment-image" href="{safe}" target="_blank" '
            f'rel="noopener noreferrer"><img src="{safe}" alt="Attachment" '
            'loading="lazy" referrerpolicy="no-referrer"></a>'
        )
    name = "Attachment"
    if not value.startswith("data:"):
        name = unquote(urlparse(value).path.rsplit("/", 1)[-1]) or name
    return (
        f'<a class="message-attachment-file" href="{safe}" target="_blank" '
        f'rel="noopener noreferrer"><span class="message-attachment-icon" '
        f'aria-hidden="true">&#128206;</span><span>{_esc(name)}</span></a>'
    )


def export_html(messages: List[dict], metadata: dict, mention_names: dict | None = None, user_profiles: dict | None = None) -> str:
    """Styled HTML transcript page (rich: content, attachments, embeds, CV2)."""
    title = metadata.get("channel_name", "Transcript")
    guild = metadata.get("guild_name", "Server")
    created = metadata.get("created_at", "")
    msg_count = len(messages)

    # Always give the author a card to open, even when live profile data was
    # unavailable at export time, so names and avatars stay clickable.
    profiles = {
        str(key): value for key, value in (user_profiles or {}).items()
        if isinstance(value, dict)
    }
    for msg in messages:
        author_id = str(msg.get("author_id") or "")
        if author_id and author_id not in profiles:
            author = str(msg.get("author") or "Unknown")
            profiles[author_id] = {"id": author_id, "display_name": author, "username": author}

    msg_rows = []
    last_author_id: Optional[str] = None
    last_time: Optional[datetime] = None
    last_day = None
    for msg in messages:
        ts = msg.get("timestamp", "")
        author = msg.get("author") or ""
        author_id = str(msg.get("author_id") or "")
        profile = profiles.get(author_id) or {}
        # Chat rows keep the server display name the message was saved with; the
        # profile card is where Discord's global name belongs.
        display_name = str(author or profile.get("display_name") or "Unknown")
        content = msg.get("content", "")
        timestamp = _parse_transcript_time(ts)
        day = timestamp.date() if timestamp else None

        if day is not None and day != last_day:
            msg_rows.append(
                '<div class="day-divider" role="separator">'
                f'<span>{_esc(_day_divider_label(timestamp))}</span></div>'
            )
            last_author_id = None
            last_time = None
            last_day = day

        grouped = bool(author_id) and author_id == last_author_id and (
            timestamp is None
            or last_time is None
            or 0 <= (timestamp - last_time).total_seconds() <= _GROUP_WINDOW_SECONDS
        )

        content_html = f'<div class="message-text">{_md_to_html(content, mention_names)}</div>' if content else ""

        attachments = msg.get("attachments") or []
        att_html = ""
        if attachments:
            items = "".join(_attachment_html(url) for url in attachments if url)
            if items:
                att_html = f'<div class="message-attachments">{items}</div>'

        embeds_html = "".join(
            _embed_to_html(embed, mention_names) for embed in msg.get("embeds") or []
            if isinstance(embed, dict)
        )

        components_html = _components_to_html(msg.get("components") or [], mention_names)

        stickers_html = ""
        for sticker in msg.get("stickers") or []:
            if not isinstance(sticker, dict):
                continue
            sticker_id = sticker.get("id")
            if not sticker_id:
                continue
            sticker_url = sticker.get("url") or (
                f"https://cdn.discordapp.com/stickers/{sticker_id}."
                f"{'gif' if sticker.get('format_type') == 4 else 'png'}"
            )
            stickers_html += (
                f'<a class="sticker" href="{_esc(sticker_url)}" target="_blank" rel="noopener noreferrer">'
                f'<img src="{_esc(sticker_url)}" alt="{_esc(sticker.get("name") or "Discord sticker")}" '
                f'title="{_esc(sticker.get("name") or "Discord sticker")}"></a>'
            )
        if stickers_html:
            stickers_html = f'<div class="stickers">{stickers_html}</div>'

        if not (content or attachments or embeds_html or components_html or stickers_html):
            content_html = '<div class="message-text ts-muted"><em>Message content unavailable</em></div>'

        time_html = ""
        if timestamp is not None:
            time_html = (
                f'<time class="message-timestamp" datetime="{timestamp.isoformat()}" '
                f'title="{_esc(ts)}">{_esc(_message_clock(timestamp))}</time>'
            )
        elif ts:
            time_html = f'<span class="message-timestamp">{_esc(ts)}</span>'

        if grouped:
            gutter = (
                f'<time class="message-gutter-time" datetime="{timestamp.isoformat()}">'
                f'{_esc(timestamp.strftime("%-I:%M %p"))}</time>'
                if timestamp is not None else ""
            )
            avatar_col = f'{gutter}<span class="message-avatar-spacer" aria-hidden="true"></span>'
            head_html = ""
        else:
            head_html = (
                '<div class="message-head">'
                f'{_message_name_html(display_name, author_id)}'
                f'{_message_guild_tag_html(profile)}'
                f'{time_html}</div>'
            )
            avatar_col = _message_avatar_html(display_name, author_id, profile.get("avatar_url"))

        msg_rows.append(
            f'<div class="message{" message-grouped" if grouped else ""}" '
            f'data-author-id="{_esc(author_id)}">'
            f'<div class="message-gutter">{avatar_col}</div>'
            '<div class="message-body">'
            f'{head_html}{content_html}{att_html}{embeds_html}{components_html}{stickers_html}'
            '</div></div>'
        )
        last_author_id = author_id or None
        last_time = timestamp

    msg_block = chr(10).join(msg_rows)
    created_html = f" · Created {_esc(created)}" if created else ""
    profile_json = json.dumps(profiles, ensure_ascii=False).replace("</", "<\\/")
    badge_art_json = json.dumps(_profile_badge_art(), ensure_ascii=False)
    status_art_json = json.dumps(_profile_status_art(), ensure_ascii=False)
    emoji_guild_json = json.dumps(
        {
            "name": guild,
            "iconUrl": metadata.get("guild_icon_url") or "",
        },
        ensure_ascii=False,
    ).replace("</", "<\\/")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Transcript — {_esc(title)}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'gg sans', 'Segoe UI', system-ui, -apple-system, sans-serif; background: #313338; color: #dbdee1; }}
  .app {{ display: flex; flex-direction: column; min-height: 100dvh; }}
  .channel-header {{ position: sticky; top: 0; z-index: 3; display: flex; align-items: center; gap: 14px; min-height: 48px; padding: 0 20px; background: #313338; border-bottom: 1px solid #26272b; }}
  .channel-heading {{ display: flex; align-items: center; gap: 8px; min-width: 0; }}
  .channel-hash {{ color: #80848e; font-size: 24px; font-weight: 500; line-height: 1; }}
  .channel-header h1 {{ overflow: hidden; color: #f2f3f5; font-size: 16px; font-weight: 600; text-overflow: ellipsis; white-space: nowrap; }}
  .channel-meta {{ overflow: hidden; margin-left: auto; color: #949ba4; font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }}
  .chat-log {{ display: flex; flex: 1 1 auto; flex-direction: column; padding: 8px 0 40px; }}
  .day-divider {{ display: flex; align-items: center; gap: 10px; margin: 20px 16px 6px; color: #949ba4; font-size: 12px; font-weight: 600; }}
  .day-divider::before, .day-divider::after {{ content: ""; flex: 1 1 auto; height: 1px; background: #3f4147; }}
  .message {{ position: relative; display: flex; margin-top: 17px; padding: 2px 20px 2px 0; color: #dbdee1; font-size: 16px; line-height: 1.375; }}
  .message:hover {{ background: #2e3035; }}
  .message-grouped {{ margin-top: 0; padding-top: 1px; padding-bottom: 1px; }}
  .message-gutter {{ position: relative; display: flex; flex: 0 0 72px; justify-content: center; align-items: flex-start; }}
  .message-avatar-button {{ display: block; width: 40px; height: 40px; flex: 0 0 auto; margin-top: 2px; padding: 0; border: 0; border-radius: 50%; background: none; }}
  button.message-avatar-button {{ cursor: pointer; }}
  .message-avatar-button:focus-visible {{ outline: 2px solid #00a8fc; outline-offset: 2px; }}
  .message-avatar {{ display: flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 50%; object-fit: cover; color: #fff; font-size: 16px; font-weight: 600; }}
  .message-avatar-fallback {{ background: #5865f2; }}
  .message-avatar-spacer {{ display: block; width: 40px; height: 1px; }}
  .message-gutter-time {{ position: absolute; top: 5px; right: 4px; display: none; color: #6d6f78; font-size: 11px; font-weight: 400; line-height: 1.2; white-space: nowrap; }}
  .message-grouped:hover .message-gutter-time {{ display: block; }}
  .message-body {{ min-width: 0; flex: 1 1 auto; }}
  .message-head {{ display: flex; align-items: center; flex-wrap: wrap; gap: 0 8px; min-height: 22px; }}
  .message-author {{ max-width: 100%; overflow: hidden; padding: 0; border: 0; background: none; color: #f2f3f5; font: inherit; font-weight: 500; text-overflow: ellipsis; white-space: nowrap; }}
  button.message-author {{ cursor: pointer; }}
  .message-author:hover .message-author-name {{ text-decoration: underline; }}
  .message-author:focus-visible {{ outline: 2px solid #00a8fc; outline-offset: 2px; border-radius: 2px; }}
  .message-guild-tag {{ display: inline-flex; align-items: center; gap: 4px; padding: 0 5px 0 4px; border: 1px solid #3f4147; border-radius: 4px; background: #2b2d31; color: #b5bac1; font-size: 12px; font-weight: 500; line-height: 16px; }}
  .message-guild-tag img {{ width: 14px; height: 14px; border-radius: 3px; object-fit: cover; }}
  .message-timestamp {{ color: #949ba4; font-size: 12px; font-weight: 400; }}
  .message-text {{ color: #dbdee1; white-space: pre-wrap; overflow-wrap: anywhere; word-break: break-word; }}
  .message-attachments {{ display: flex; flex-direction: column; gap: 8px; margin-top: 8px; }}
  .message-attachment-image {{ display: block; width: max-content; max-width: min(550px, 100%); }}
  .message-attachment-image img {{ display: block; max-width: 100%; max-height: 350px; border-radius: 8px; object-fit: contain; }}
  .message-attachment-file {{ display: inline-flex; align-items: center; gap: 8px; width: max-content; max-width: 100%; padding: 10px 16px; border: 1px solid #3f4147; border-radius: 8px; background: #2b2d31; color: #00a8fc; font-size: 14px; font-weight: 500; text-decoration: none; }}
  .message-attachment-file:hover {{ background: #313338; }}
  .message-attachment-icon {{ font-size: 16px; line-height: 1; }}
  .custom-emoji {{ width: 22px; height: 22px; object-fit: contain; vertical-align: -0.35em; display: inline-block; cursor: pointer; border-radius: 3px; }}
  .custom-emoji:focus-visible {{ outline: 2px solid #00a8fc; outline-offset: 2px; }}
  .custom-emoji-fallback {{ color: inherit; }}
  /* Discord's custom-emoji popup: application emojis name the app, while
     server emojis add the Nitro prompt and the server source row. */
  .discord-emoji-popup {{ position: fixed; left: var(--emoji-popup-left, 12px); top: var(--emoji-popup-top, 12px); z-index: 103; width: min(22rem, calc(100vw - 1.5rem)); padding: 16px; color: #dbdee1; background: #111214; border: 1px solid rgb(255 255 255 / .08); border-radius: 10px; box-shadow: 0 18px 52px rgb(0 0 0 / .6); font-size: 13px; line-height: 1.4; }}
  .discord-emoji-popup-main {{ display: flex; align-items: flex-start; gap: 14px; }}
  .discord-emoji-popup-art {{ width: 52px; height: 52px; flex: 0 0 auto; object-fit: contain; }}
  .discord-emoji-popup-copy {{ min-width: 0; }}
  .discord-emoji-popup-name {{ display: block; margin: 0 0 3px; color: #f2f3f5; font-size: 15.5px; font-weight: 700; overflow-wrap: anywhere; }}
  .discord-emoji-popup-copy p {{ margin: 0; color: #b5bac1; font-size: 13.5px; line-height: 1.4; }}
  .discord-emoji-popup-nitro {{ display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 14px; padding: 10px 12px; color: #111214; background: #fff; border-radius: 8px; font-size: 15px; font-weight: 700; text-decoration: none; box-shadow: 0 0 0 1px #fff, 0 0 18px rgb(88 101 242 / .65), 0 0 32px rgb(235 69 158 / .35); }}
  .discord-emoji-popup-nitro:hover {{ color: #111214; background: #f6f6f6; text-decoration: none; }}
  .discord-emoji-popup-nitro-mark {{ width: 18px; height: 18px; flex: 0 0 auto; }}
  .discord-emoji-popup-source {{ margin: 14px -16px 0; padding: 12px 16px 0; border-top: 1px solid #2b2d31; }}
  .discord-emoji-popup-source > p {{ margin: 0 0 10px; color: #949ba4; font-size: 13px; }}
  .discord-emoji-popup-guild {{ display: flex; align-items: center; gap: 10px; }}
  .discord-emoji-popup-guild-icon {{ width: 40px; height: 40px; flex: 0 0 auto; border-radius: 12px; object-fit: cover; background: #5865f2; }}
  .discord-emoji-popup-guild-fallback {{ display: grid; place-items: center; color: #fff; font-size: 18px; font-weight: 700; }}
  .discord-emoji-popup-guild-copy {{ display: grid; gap: 2px; min-width: 0; }}
  .discord-emoji-popup-guild-copy strong {{ color: #f2f3f5; font-size: 14.5px; font-weight: 650; overflow-wrap: anywhere; }}
  .discord-emoji-popup-guild-copy small {{ color: #949ba4; font-size: 12.5px; }}
  .discord-timestamp {{ color: #b5bac1; white-space: nowrap; }}
  .discord-md-mention {{ display: inline; padding: 1px 4px; color: #dce4ff; background: rgba(88, 101, 242, .3); border-radius: 4px; font-weight: 650; line-height: 1.5; text-decoration: none; }}
  /* Discord paints user, role and channel mentions with the same blue. */
  .discord-md-mention-role {{ color: #dce4ff; background: rgba(88, 101, 242, .3); }}
  .discord-md-mention-user {{ cursor: pointer; }}
  .discord-md-spoiler {{ margin: 0 -2px; padding: 0 2px; border-radius: 4px; background: #202225; cursor: pointer; box-decoration-break: clone; -webkit-box-decoration-break: clone; }}
  .discord-md-spoiler:not(.is-revealed) {{ color: transparent; }}
  .discord-md-spoiler:not(.is-revealed) > * {{ visibility: hidden; }}
  .discord-md-spoiler:not(.is-revealed) a {{ pointer-events: none; }}
  .discord-md-spoiler.is-revealed {{ background: transparent; cursor: auto; }}
  .discord-md-spoiler:focus-visible {{ outline: 2px solid #00a8fc; outline-offset: 2px; }}
  .discord-profile-popover {{ position: fixed; inset: 0; z-index: 100; pointer-events: none; }}
  .discord-profile-card {{ position: fixed; left: var(--profile-left); top: var(--profile-top); width: min(20rem, calc(100vw - 1.5rem)); max-height: min(35rem, calc(100dvh - 1.5rem)); overflow-y: auto; border: 1px solid rgb(255 255 255 / .08); border-radius: .85rem; background: #111214; color: #f2f3f5; box-shadow: 0 18px 52px rgb(0 0 0 / .58); pointer-events: auto; font-size: 13px; line-height: 1.45; }}
  .discord-profile-banner {{ display: block; width: 100%; height: 5.5rem; object-fit: cover; background: #202225 center / cover no-repeat; }}
  .discord-profile-menu {{ position: absolute; top: 8px; right: 8px; z-index: 3; }}
  .discord-profile-menu-button {{ display: flex; align-items: center; justify-content: center; width: 26px; height: 26px; padding: 0; border: 0; border-radius: 50%; background: rgb(24 25 28 / .62); cursor: pointer; }}
  .discord-profile-menu-button:hover {{ background: rgb(24 25 28 / .85); }}
  .discord-profile-menu-dots {{ display: flex; gap: 3px; }}
  .discord-profile-menu-dots i {{ width: 4px; height: 4px; border-radius: 50%; background: #fff; }}
  .discord-profile-menu-list {{ position: absolute; top: calc(100% + 6px); right: 0; min-width: 148px; padding: 4px; background: #232428; border: 1px solid rgb(255 255 255 / .08); border-radius: 6px; box-shadow: 0 10px 26px rgb(0 0 0 / .5); }}
  .discord-profile-menu-item {{ display: block; width: 100%; padding: 7px 9px; color: #dbdee1; background: transparent; border: 0; border-radius: 4px; font: inherit; text-align: left; cursor: pointer; }}
  .discord-profile-menu-item:hover {{ background: #35373c; }}
  .discord-profile-body {{ position: relative; padding: 0 16px 16px; }}
  .discord-profile-head {{ display: flex; align-items: center; gap: 8px; margin-top: -38px; }}
  .discord-profile-avatar-wrap {{ position: relative; display: block; flex: 0 0 auto; width: 76px; height: 76px; }}
  .discord-profile-avatar {{ display: block; width: 76px; height: 76px; border: 0; border-radius: 50%; object-fit: cover; background: #313338; }}
  .discord-profile-avatar-fallback {{ display: flex; align-items: center; justify-content: center; background: #5865f2; color: #fff; font-size: 28px; font-weight: 600; }}
  .discord-profile-avatar-decoration {{ position: absolute; top: 50%; left: 50%; width: 100%; height: 100%; object-fit: contain; transform: translate(-50%, -50%) scale(1.2); pointer-events: none; }}
  .discord-status-icon {{ position: absolute; right: 0; bottom: 0; z-index: 2; width: 20px; height: 20px; object-fit: contain; border: 2px solid #111214; border-radius: 50%; background: #111214; }}
  .discord-profile-status {{ position: relative; flex: 1 1 auto; min-width: 0; padding: 8px 11px; color: #dbdee1; background: #232428; border-radius: 12px; font-size: 12.5px; line-height: 1.4; }}
  .discord-profile-status::before {{ position: absolute; top: 50%; left: -6px; border: 6px solid transparent; border-right-color: #232428; border-left: 0; content: ""; transform: translateY(-50%); }}
  .discord-profile-status-text {{ display: -webkit-box; overflow: hidden; overflow-wrap: anywhere; -webkit-box-orient: vertical; -webkit-line-clamp: 3; }}
  .discord-profile-status-emoji {{ display: inline-block; width: 15px; height: 15px; margin-right: 5px; object-fit: contain; vertical-align: -.2em; }}
  .discord-profile-name {{ margin: 8px 0 0; color: #f2f3f5; font-size: 18px; font-weight: 700; }}
  .discord-profile-username {{ display: flex; align-items: center; flex-wrap: wrap; gap: 6px; margin: 0; color: #b5bac1; }}
  .discord-profile-user-tag {{ min-width: 0; overflow-wrap: anywhere; }}
  .discord-profile-guild-tag {{ display: inline-flex; align-items: center; gap: 5px; padding: 3px 6px; color: #e3e5e8; background: #232428; border: 1px solid transparent; border-radius: 4px; font: inherit; font-size: 10px; font-weight: 700; line-height: 1.2; }}
  button.discord-profile-guild-tag {{ cursor: pointer; }}
  button.discord-profile-guild-tag:hover, button.discord-profile-guild-tag[aria-expanded="true"] {{ background: #35373c; border-color: rgb(255 255 255 / .12); }}
  .discord-profile-guild-tag img {{ width: 14px; height: 14px; object-fit: contain; }}
  .discord-profile-badges {{ position: relative; display: flex; align-items: center; flex-wrap: wrap; gap: 6px; margin-top: 8px; }}
  .discord-profile-badge {{ width: 20px; height: 20px; object-fit: contain; }}
  .discord-profile-badge-button {{ display: block; padding: 2px; background: transparent; border: 0; border-radius: 5px; line-height: 0; cursor: pointer; }}
  .discord-profile-badge-button:hover, .discord-profile-badge-button[aria-expanded="true"] {{ background: #3f4147; }}
  /* Fixed to the page and stacked above the profile popup, so the badge popup
     neither stretches the profile card nor gets clipped by its scroll box. */
  .discord-badge-popup {{ position: fixed; z-index: 101; display: flex; align-items: center; gap: 10px; width: max-content; max-width: min(18rem, calc(100vw - 1.5rem)); padding: 10px 12px; background: #232428; border: 1px solid rgb(255 255 255 / .08); border-radius: 8px; box-shadow: 0 10px 26px rgb(0 0 0 / .5); }}
  .discord-badge-popup-art {{ width: 32px; height: 32px; flex: 0 0 auto; object-fit: contain; }}
  .discord-badge-popup-copy {{ display: grid; gap: 2px; min-width: 0; }}
  .discord-badge-popup-copy strong {{ color: #f2f3f5; font-size: 12.5px; font-weight: 700; }}
  .discord-badge-popup-copy p {{ margin: 0; color: #b5bac1; font-size: 11.5px; line-height: 1.4; }}
  /* Discord's server-tag popup: banner, overlapping icon, name and tag pill,
     member counts, description, then the green join button. Fixed above the
     profile popup so the card is neither stretched nor clipped by it. */
  .discord-server-tag-popup {{ position: fixed; z-index: 102; width: min(20rem, calc(100vw - 1.5rem)); overflow: hidden; color: #f2f3f5; background: #232428; border: 1px solid rgb(255 255 255 / .08); border-radius: 12px; box-shadow: 0 18px 46px rgb(0 0 0 / .6); font-size: 12.5px; line-height: 1.4; }}
  .discord-server-tag-banner {{ display: block; width: 100%; height: 5.25rem; object-fit: cover; background: linear-gradient(135deg, #5865f2, #3b3f8f); }}
  .discord-server-tag-popup.is-private .discord-server-tag-banner,
  .discord-server-tag-popup.is-unknown .discord-server-tag-banner {{ background: linear-gradient(135deg, #4e5058, #2b2d31); }}
  .discord-server-tag-body {{ padding: 0 16px 16px; }}
  .discord-server-tag-icon-shell {{ display: grid; place-items: center; width: 80px; height: 80px; margin-top: -40px; overflow: hidden; background: #1e1f22; border: 6px solid #232428; border-radius: 18px; }}
  .discord-server-tag-icon {{ width: 100%; height: 100%; object-fit: cover; }}
  .discord-server-tag-icon.is-placeholder {{ color: #dbdee1; font-size: 30px; font-weight: 700; }}
  .discord-server-tag-title-row {{ display: flex; align-items: center; flex-wrap: wrap; gap: 6px; margin-top: 10px; }}
  .discord-server-tag-name {{ margin: 0; color: #f2f3f5; font-size: 18px; font-weight: 700; line-height: 1.25; overflow-wrap: anywhere; }}
  .discord-server-tag-pill {{ display: inline-flex; align-items: center; gap: 5px; padding: 2px 6px; color: #e3e5e8; background: #35373c; border-radius: 5px; font-size: 11px; font-weight: 700; line-height: 1.3; }}
  .discord-server-tag-pill img {{ width: 14px; height: 14px; object-fit: contain; }}
  .discord-server-tag-stats {{ display: flex; align-items: center; flex-wrap: wrap; gap: 10px; margin: 6px 0 0; color: #dbdee1; font-size: 12.5px; }}
  .discord-server-tag-stats span {{ display: inline-flex; align-items: center; gap: 5px; }}
  .discord-server-tag-stats i {{ width: 8px; height: 8px; border-radius: 50%; background: #80848e; }}
  .discord-server-tag-online i {{ background: #23a55a; }}
  .discord-server-tag-created {{ margin: 3px 0 0; color: #b5bac1; font-size: 12.5px; }}
  .discord-server-tag-description {{ display: -webkit-box; overflow: hidden; margin: 10px 0 0; color: #dbdee1; font-size: 13px; line-height: 1.45; overflow-wrap: anywhere; -webkit-box-orient: vertical; -webkit-line-clamp: 3; }}
  .discord-server-tag-popup.is-private .discord-server-tag-description,
  .discord-server-tag-popup.is-unknown .discord-server-tag-description {{ color: #b5bac1; }}
  .discord-server-tag-invite {{ display: block; margin-top: 14px; padding: 11px 10px; color: #fff; background: #248046; border-radius: 8px; font-size: 14px; font-weight: 700; text-align: center; text-decoration: none; }}
  .discord-server-tag-invite:hover {{ background: #1a6334; text-decoration: none; }}
  .discord-server-tag-invite.is-join {{ background: #5865f2; }}
  .discord-server-tag-invite.is-join:hover {{ background: #4752c4; }}
  .discord-profile-spotify {{ margin-top: 14px; padding: 10px 12px 11px; background: #232428; border-radius: 8px; }}
  .discord-profile-spotify-link {{ display: block; color: inherit; text-decoration: none; }}
  .discord-profile-spotify-head {{ color: #b5bac1; font-size: 11px; font-weight: 700; }}
  .discord-profile-spotify-body {{ display: flex; align-items: center; gap: 10px; margin-top: 9px; }}
  .discord-profile-spotify-art {{ width: 56px; height: 56px; flex: 0 0 auto; border-radius: 6px; object-fit: cover; }}
  .discord-profile-spotify-copy {{ display: grid; flex: 1 1 auto; min-width: 0; gap: 3px; }}
  .discord-profile-spotify-copy strong {{ overflow: hidden; color: #f2f3f5; font-size: 12.5px; text-overflow: ellipsis; white-space: nowrap; }}
  .discord-profile-spotify-copy small {{ overflow: hidden; color: #b5bac1; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }}
  .discord-profile-spotify-progress {{ display: flex; align-items: center; gap: 7px; margin-top: 4px; color: #949ba4; font-size: 10px; }}
  .discord-profile-spotify-track {{ position: relative; display: block; height: 4px; flex: 1 1 auto; overflow: hidden; background: #4e5058; border-radius: 999px; }}
  .discord-profile-spotify-track > i {{ position: absolute; top: 0; bottom: 0; left: 0; width: 0; background: #1db954; border-radius: 999px; transition: width .95s linear; }}
  .discord-profile-about {{ margin-top: 14px; padding-top: 12px; border-top: 1px solid #3f4147; }}
  .discord-profile-about h3 {{ margin-bottom: 5px; color: #b5bac1; font-size: 11px; text-transform: uppercase; }}
  .discord-profile-about p {{ white-space: pre-wrap; }}
  .discord-profile-full-link {{ display: block; margin-top: 14px; padding: 8px; border-radius: 5px; background: #5865f2; color: white; text-align: center; text-decoration: none; }}
  .discord-profile-state {{ padding: 18px; }}
  @media (prefers-reduced-transparency: reduce) {{
    .discord-profile-card {{ box-shadow: none; }}
  }}
  .stickers {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }}
  .sticker img {{ width: 160px; max-width: 100%; max-height: 160px; object-fit: contain; display: block; }}
  .message-text strong {{ font-weight: 700; }}
  .message-text em {{ font-style: italic; }}
  .message-text u {{ text-decoration: underline; }}
  .message-text s {{ text-decoration: line-through; }}
  .ts-muted {{ color: #6d737a; }}
  .tsm {{ color: #949ba4; font-size: 12px; }}
  .th {{ font-size: 16px; font-weight: 700; color: #f2f3f5; }}
  /* One rounded bar for a whole run of quote lines, like Discord. */
  .tq {{ position: relative; display: block; padding-left: 12px; color: #dbdee1; }}
  .tq::before {{ position: absolute; top: 0; bottom: 0; left: 0; width: 4px; background: #4e5058; border-radius: 4px; content: ""; }}
  @media (max-width: 520px) {{
    .channel-header {{ gap: 8px; padding: 0 12px; }}
    .channel-meta {{ display: none; }}
    .message {{ padding-right: 12px; }}
    .message-gutter {{ flex-basis: 56px; }}
    .message-avatar-button, .message-avatar, .message-avatar-spacer {{ width: 36px; height: 36px; }}
    .message-avatar-spacer {{ height: 1px; }}
    .message-gutter-time {{ right: 2px; }}
    .message-attachment-image img {{ max-height: 260px; }}
  }}
  code {{ background: #2b2d31; padding: 1px 5px; border-radius: 4px; font-family: Consolas, monospace; font-size: 12px; color: #f2b8c2; }}
  a:hover {{ text-decoration: underline; }}

  .embed {{ display: flex; max-width: 560px; margin-top: 8px; background: #2b2d31; border: 1px solid #3f4147; border-left: 4px solid #5865f2; border-radius: 6px; padding: 10px 12px; }}
  .embed-body {{ flex: 1; min-width: 0; }}
  .embed-author {{ color: #f2f3f5; font-weight: 600; font-size: 13px; }}
  .embed-author-icon {{ width: 18px; height: 18px; border-radius: 50%; vertical-align: -4px; margin-right: 6px; }}
  .embed-title {{ color: #00a8fc; font-weight: 600; margin: 4px 0; }}
  .embed-title a {{ color: inherit; }}
  .embed-desc {{ color: #dbdee1; white-space: pre-wrap; word-break: break-word; font-size: 13px; }}
  .embed-fields {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }}
  .embed-field {{ flex: 0 0 100%; font-size: 13px; }}
  .embed-field-inline {{ flex: 0 0 50%; }}
  .embed-field-name {{ color: #f2f3f5; font-weight: 600; margin-bottom: 2px; }}
  .embed-field-value {{ color: #dbdee1; white-space: pre-wrap; word-break: break-word; }}
  .embed-image-wrap {{ margin-top: 8px; display: block; }}
  .embed-image {{ max-width: 100%; max-height: 350px; border-radius: 4px; }}
  .embed-foot {{ display: flex; align-items: center; gap: 6px; color: #949ba4; font-size: 11px; margin-top: 6px; }}
  .embed-footer-icon {{ width: 16px; height: 16px; border-radius: 50%; }}
  .embed-thumb {{ margin-left: 10px; flex: 0 0 auto; }}
  .embed-thumb img {{ width: 80px; height: 80px; border-radius: 6px; object-fit: cover; }}

  .cv2-card {{ position: relative; display: flex; overflow: hidden; max-width: 560px; margin-top: 8px; background: #2b2d31; border: 1px solid #3f4147; border-radius: 12px; }}
  .cv2-bar {{ flex: 0 0 4px; }}
  .cv2-card-inner {{ flex: 1; min-width: 0; padding: 8px 12px; }}
  .cv2-text {{ color: #dbdee1; white-space: pre-wrap; word-break: break-word; font-size: 14px; margin: 4px 0; }}
  .cv2-label {{ color: #f2f3f5; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; font-size: 12px; margin: 4px 0; }}
  .cv2-sep {{ border-top: 1px solid #3f4147; margin: 8px 0; }}
  .cv2-sep-spacer {{ border-top: 0; margin: 4px 0; }}
  .cv2-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 0; }}
  .cv2-btn {{ display: inline-block; padding: 2px 12px; background: #4e5058; border-radius: 3px; color: #f2f3f5; font-size: 13px; }}
  .cv2-btn-link {{ background: #5865f2; color: #fff; text-decoration: none; }}
  .cv2-btn-link:hover {{ background: #4752c4; text-decoration: none; }}
  .cv2-btn-disabled {{ opacity: .5; }}
  .cv2-section {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; margin: 4px 0; }}
  .cv2-thumb img {{ width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }}
  .cv2-gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 6px; margin: 6px 0; }}
  .cv2-media-item {{ margin: 0; }}
  .cv2-media-item img, .cv2-media-item video {{ width: 100%; max-height: 260px; border-radius: 6px; object-fit: cover; }}
  .cv2-media-item figcaption {{ color: #949ba4; font-size: 11px; margin-top: 2px; }}
</style>
</head>
<body>
<div class="app">
<header class="channel-header">
  <div class="channel-heading"><span class="channel-hash" aria-hidden="true">#</span><h1>{_esc(title)}</h1></div>
  <div class="channel-meta">{_esc(guild)} · {_esc(msg_count)} messages{created_html}</div>
</header>
<main class="chat-log">
{msg_block}
</main>
</div>
<script>
(() => {{
  const mentionProfiles = {profile_json};
  const badgeArt = {badge_art_json};
  const statusArt = {status_art_json};
  const emojiGuild = {emoji_guild_json};
  const escapeHtml = (value) => String(value ?? "").replace(/[&<>\"']/g, (char) => ({{ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\\\"": "&quot;", "'": "&#39;" }})[char]);
  // Discord never shows a broken custom emoji: an emoji it cannot resolve is
  // written out as its name between colons. The same swap keeps a dead emoji
  // from leaving a broken icon or eating the formatting around it.
  const fixCustomEmoji = (img) => {{
    const replace = () => {{
      const fallback = document.createElement("span");
      fallback.className = "custom-emoji-fallback";
      fallback.textContent = ":" + (img.dataset.emojiName || "") + ":";
      img.replaceWith(fallback);
    }};
    // An image that already failed has completed with no size, and its error
    // event is gone by the time this script runs.
    if (img.complete && img.naturalWidth === 0) {{ replace(); return; }}
    img.addEventListener("error", replace, {{ once: true }});
  }};
  document.querySelectorAll("img.custom-emoji").forEach(fixCustomEmoji);
  // Discord's custom-emoji popup: application emojis name the bot's app, while
  // server emojis add the Nitro prompt and the server they came from.
  const NITRO_MARK = '<svg class="discord-emoji-popup-nitro-mark" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M13.32 21.978a10.322 10.322 0 01-2.07-.36 6.638 6.638 0 01-.675-.219.152.152 0 00-.057-.019.372.372 0 01-.09-.03l-.137-.06a.383.383 0 00-.088-.03.418.418 0 01-.097-.038 7.412 7.412 0 00-.187-.088 8.155 8.155 0 01-.67-.325 4.26 4.26 0 01-.34-.19 1.966 1.966 0 01-.18-.11 1.274 1.274 0 00-.17-.103.763.763 0 01-.103-.07.397.397 0 00-.086-.056c-.007 0-.084-.054-.171-.12a1.052 1.052 0 00-.179-.12c-.011 0-.021-.008-.021-.018 0-.01-.072-.07-.16-.133a.873.873 0 01-.16-.132c0-.01-.01-.017-.02-.017-.012 0-.048-.027-.08-.06a.34.34 0 00-.069-.06.33.33 0 01-.068-.055 10.464 10.464 0 01-1.008-1.008.33.33 0 01-.055-.069.34.34 0 00-.06-.068c-.033-.033-.06-.068-.06-.08 0-.011-.008-.02-.017-.02a.873.873 0 01-.132-.16.825.825 0 00-.133-.16c-.01 0-.018-.01-.018-.022 0-.011-.054-.092-.12-.178a1.496 1.496 0 01-.12-.171.4.4 0 00-.055-.087c-.064-.084-.1-.14-.119-.182a.73.73 0 00-.055-.09 1.612 1.612 0 01-.11-.18 4.258 4.258 0 01-.19-.34 8.154 8.154 0 01-.325-.67 7.397 7.397 0 00-.088-.188.418.418 0 01-.038-.097.42.42 0 00-.033-.093c-.078-.175-.087-.2-.087-.221a.152.152 0 00-.02-.057c-.055-.098-.266-.812-.35-1.185-.06-.266-.161-.848-.181-1.045l-.014-.135-.523-.001c-.59-.001-.7-.018-.9-.139a.968.968 0 01.014-1.668c.189-.113.32-.132.89-.132h.498l.025-.225c.047-.438.196-1.222.29-1.525a.808.808 0 00.03-.125c0-.02-.352-.026-1.695-.026-1.446 0-1.714-.005-1.824-.03a1.116 1.116 0 01-.83-.83 1.111 1.111 0 01.83-1.329C.97 7.003 1.287 7 3.15 7c2.035 0 2.164-.003 2.193-.036a.35.35 0 00.043-.065c.018-.038.052-.095.103-.17.062-.093.089-.137.103-.17a.76.76 0 01.07-.103.397.397 0 00.057-.086c0-.007.054-.084.12-.17.066-.088.12-.168.12-.18 0-.011.008-.02.018-.02.01 0 .07-.073.133-.16a.873.873 0 01.132-.16c.01 0 .017-.01.017-.022 0-.01.027-.047.06-.079a.34.34 0 00.06-.069.33.33 0 01.055-.068c.03-.032.109-.118.175-.192.066-.074.131-.147.146-.162.021-.023-.233-.028-1.69-.033l-1.717-.006L3.208 5a1.48 1.48 0 01-.64-.392 1.44 1.44 0 01-.393-.651c-.038-.125-.046-.194-.046-.41 0-.216.008-.285.046-.41.085-.273.193-.451.393-.65.188-.19.346-.29.585-.372.283-.098.14-.096 6.016-.1 5.47-.002 5.626 0 6.12.063.236.03.698.112.956.17.366.083 1.082.294 1.18.35.019.01.045.019.057.019.012 0 .053.013.09.03l.136.06c.038.016.077.03.088.03.011 0 .055.017.097.038l.187.088a8.155 8.155 0 01.67.324 4.261 4.261 0 01.34.19c.057.03.112.064.18.11.093.062.138.089.17.103a.76.76 0 01.103.07c.04.031.08.057.086.057.008 0 .085.054.171.12.087.066.168.12.18.12.01 0 .02.008.02.018 0 .01.072.07.16.133.088.064.16.123.16.132 0 .01.01.017.021.017.012 0 .047.027.08.06a.34.34 0 00.068.06.33.33 0 01.068.055l.193.175a10.464 10.464 0 01.816.833.33.33 0 01.055.068.34.34 0 00.06.07c.033.031.06.067.06.078 0 .012.007.021.016.021.01 0 .07.072.132.16.064.088.124.16.134.16.01 0 .018.01.018.021 0 .012.054.092.12.18.066.086.12.163.12.17 0 .007.024.046.055.086.063.085.1.14.118.183a.727.727 0 00.055.09c.045.065.078.118.111.18a4.259 4.259 0 01.19.34 8.147 8.147 0 01.325.67c.027.06.067.145.088.187.02.043.038.086.038.097 0 .011.013.051.03.088l.06.136c.016.038.03.079.03.09a6.613 6.613 0 01.238.732 10.11 10.11 0 01-.219 6.176.152.152 0 00-.02.057.405.405 0 01-.031.095c-.078.175-.088.2-.088.22a.418.418 0 01-.038.096l-.088.187a8.153 8.153 0 01-.325.67 4.258 4.258 0 01-.19.34c-.03.057-.063.112-.11.181-.061.093-.088.137-.103.17a.764.764 0 01-.07.102.397.397 0 00-.056.087c0 .007-.054.084-.12.17-.066.087-.12.168-.12.18 0 .011-.008.02-.018.02-.01 0-.07.073-.134.16a.873.873 0 01-.132.16c-.009 0-.016.01-.016.021 0 .012-.027.047-.06.08a.34.34 0 00-.06.068.33.33 0 01-.055.068l-.175.193a10.463 10.463 0 01-.834.816.33.33 0 01-.068.055.34.34 0 00-.069.06c-.032.033-.067.06-.079.06-.011 0-.02.007-.02.017 0 .009-.073.068-.16.132a.825.825 0 00-.16.133c0 .01-.01.018-.022.018-.011 0-.092.054-.179.12-.086.066-.163.12-.17.12a.4.4 0 00-.087.055c-.084.063-.14.1-.183.118a.728.728 0 00-.09.055 1.612 1.612 0 01-.18.111 4.264 4.264 0 01-.34.19c-.099.05-.193.1-.21.111a8.155 8.155 0 01-.46.214c-.06.027-.144.067-.187.088a.419.419 0 01-.097.038.383.383 0 00-.088.03l-.136.06a.372.372 0 01-.09.03.153.153 0 00-.057.02c-.098.054-.814.266-1.18.348-.946.213-1.994.295-2.925.23zm1.74-3.135a7.374 7.374 0 001.66-.444c.346-.134 1.079-.535 1.35-.738.055-.042.172-.128.26-.191.088-.064.178-.136.2-.16.022-.025.13-.123.24-.218.243-.21.212-.18.423-.423.096-.11.196-.22.222-.247.027-.026.098-.116.16-.2.061-.084.145-.198.187-.253.176-.233.632-1.064.725-1.32l.092-.247c.446-1.186.543-2.575.271-3.853-.08-.377-.143-.581-.363-1.18-.095-.262-.55-1.089-.725-1.32a24.578 24.578 0 01-.191-.26 2.3 2.3 0 00-.16-.2 3.244 3.244 0 01-.16-.18 3.94 3.94 0 00-.536-.536 1.424 1.424 0 01-.175-.158c0-.008-.096-.084-.215-.17a5.702 5.702 0 01-.225-.167 4.486 4.486 0 00-.448-.288 6.844 6.844 0 00-2.937-.953 9.532 9.532 0 00-1.576.038c-.756.113-1.43.321-2.09.644-.249.122-.743.404-.77.439a1.6 1.6 0 01-.14.1c-.422.282-.954.771-1.328 1.223-.377.455-.64.854-.89 1.354a6.996 6.996 0 00-.558 4.564c.113.482.273.958.466 1.387.118.26.435.832.528.952.03.04.095.13.142.201a6.86 6.86 0 004.458 2.772c.453.076.609.086 1.243.08.467-.006.646-.016.86-.048zm-1.51-1.725a5.329 5.329 0 01-1.308-.308 5.763 5.763 0 01-.683-.326 7.122 7.122 0 01-.707-.482 6.14 6.14 0 01-.675-.676 7.121 7.121 0 01-.482-.707 5.026 5.026 0 01-.506-3.7 4.89 4.89 0 01.775-1.679c.17-.241.196-.274.385-.48.157-.171.3-.309.503-.484.115-.1.518-.373.707-.482a5.026 5.026 0 013.7-.505 4.89 4.89 0 011.68.774c.241.17.274.196.48.385.17.157.308.3.484.504.099.115.373.517.482.707a5.028 5.028 0 01.407 4.04 4.835 4.835 0 01-.677 1.338c-.17.242-.196.275-.385.481-.147.161-.15.164-.311.311-.206.19-.239.216-.48.386a4.89 4.89 0 01-1.68.774 5.276 5.276 0 01-1.71.129zm2.888-3.437c.477-.797.867-1.469.867-1.493 0-.036-1.485-2.586-1.697-2.914l-.049-.075H12.62l-.047.075c-.219.35-1.659 2.88-1.659 2.915 0 .036 1.46 2.567 1.658 2.875l.048.076 1.475-.006 1.475-.005z"/></svg>';
  let emojiTrigger = null;
  const closeEmojiPopup = () => {{
    document.querySelector(".discord-emoji-popup")?.remove();
    if (emojiTrigger) emojiTrigger.setAttribute("aria-expanded", "false");
    emojiTrigger = null;
  }};
  const positionEmojiPopup = () => {{
    const popup = document.querySelector(".discord-emoji-popup");
    if (!emojiTrigger || !popup) return;
    const rect = emojiTrigger.getBoundingClientRect();
    const margin = 12;
    const gap = 8;
    const width = popup.offsetWidth;
    const height = popup.offsetHeight;
    const left = Math.max(margin, Math.min(rect.left + rect.width / 2 - width / 2, window.innerWidth - width - margin));
    const below = rect.bottom + gap;
    const top = below + height <= window.innerHeight - margin
      ? below
      : Math.max(margin, rect.top - height - gap);
    popup.style.left = left + "px";
    popup.style.top = Math.min(top, window.innerHeight - height - margin) + "px";
  }};
  const emojiPopupMarkup = (img) => {{
    const isApplication = img.dataset.emojiApp === "1";
    const name = img.dataset.emojiName || "";
    const art = img.currentSrc || img.src;
    const main = '<div class="discord-emoji-popup-main">'
      + '<img class="discord-emoji-popup-art" src="' + escapeHtml(art) + '" alt="">'
      + '<div class="discord-emoji-popup-copy">'
      + '<strong class="discord-emoji-popup-name">:' + escapeHtml(name) + ':</strong>'
      + '<p>' + (isApplication
        ? "This emoji is from the Niko app"
        : "This emoji is from this server. Get Nitro to use it everywhere.") + '</p>'
      + '</div></div>';
    const label = ':' + escapeHtml(name) + ': emoji';
    if (isApplication) {{
      return '<div class="discord-emoji-popup" role="dialog" aria-label="' + label + '">' + main + '</div>';
    }}
    const guildName = emojiGuild.name || "This server";
    const initial = escapeHtml((Array.from(String(guildName).trim())[0] || "?").toUpperCase());
    const icon = emojiGuild.iconUrl
      ? '<img class="discord-emoji-popup-guild-icon" src="' + escapeHtml(emojiGuild.iconUrl) + '" alt="">'
      : '<span class="discord-emoji-popup-guild-icon discord-emoji-popup-guild-fallback" aria-hidden="true">' + initial + '</span>';
    return '<div class="discord-emoji-popup" role="dialog" aria-label="' + label + '">'
      + main
      + '<a class="discord-emoji-popup-nitro" href="https://discord.com/nitro" target="_blank" rel="noopener noreferrer">' + NITRO_MARK + '<span>Get Nitro</span></a>'
      + '<div class="discord-emoji-popup-source"><p>This emoji is from</p>'
      + '<div class="discord-emoji-popup-guild">' + icon
      + '<div class="discord-emoji-popup-guild-copy"><strong>' + escapeHtml(guildName) + '</strong><small>Invite-only server</small></div>'
      + '</div></div></div>';
  }};
  const openEmojiPopup = (img) => {{
    closeEmojiPopup();
    emojiTrigger = img;
    const holder = document.createElement("div");
    holder.innerHTML = emojiPopupMarkup(img);
    const popup = holder.firstElementChild;
    if (!popup) return;
    document.body.appendChild(popup);
    img.setAttribute("aria-expanded", "true");
    positionEmojiPopup();
  }};
  window.addEventListener("resize", positionEmojiPopup);
  window.addEventListener("scroll", positionEmojiPopup, true);
  // A spoiler is opened by its own click, and only then do the links inside it
  // become clickable. The first click never follows anything it hides.
  const bindSpoiler = (spoiler) => {{
    const reveal = () => {{
      if (spoiler.classList.contains("is-revealed")) return;
      spoiler.classList.add("is-revealed");
      spoiler.setAttribute("aria-expanded", "true");
      spoiler.removeAttribute("aria-label");
    }};
    spoiler.addEventListener("click", (event) => {{
      if (spoiler.classList.contains("is-revealed")) return;
      event.preventDefault();
      event.stopPropagation();
      reveal();
    }});
    spoiler.addEventListener("keydown", (event) => {{
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      reveal();
    }});
  }};
  document.querySelectorAll("[data-discord-spoiler]").forEach(bindSpoiler);
  let profileTimer = null;
  let profilePollTimer = null;
  let refreshProfilePresence = null;
  const stopProfileTimer = () => {{ if (profileTimer !== null) {{ clearInterval(profileTimer); profileTimer = null; }} }};
  const stopProfilePoll = () => {{
    if (profilePollTimer !== null) {{ clearInterval(profilePollTimer); profilePollTimer = null; }}
    if (refreshProfilePresence !== null) {{ document.removeEventListener("visibilitychange", refreshProfilePresence); refreshProfilePresence = null; }}
  }};
  const closeProfile = () => {{ stopProfileTimer(); stopProfilePoll(); document.querySelector(".discord-profile-popover")?.remove(); document.querySelector(".discord-badge-popup")?.remove(); document.querySelector(".discord-server-tag-popup")?.remove(); }};
  // The presence dot Discord draws on the avatar. The art is inlined, so the popup
  // shows live status without needing the web app's asset folder.
  const statusKey = (value) => {{
    const raw = value && typeof value === "object" ? value.name : value;
    const name = String(raw || "").split(".").pop().trim().toLowerCase();
    return statusArt[name] ? name : "offline";
  }};
  const statusDot = (profile) => {{
    const art = statusArt[statusKey(profile.status)];
    if (!art) return "";
    const label = escapeHtml(art.label || "Offline");
    return '<img class="discord-status-icon" data-profile-status src="' + art.src + '" alt="' + label + '" title="' + label + '">';
  }};
  const profileAvatar = (profile) => profile.avatar_url
    ? '<span class="discord-profile-avatar-wrap"><img class="discord-profile-avatar" src="' + escapeHtml(profile.avatar_url) + '" alt="">'
      + (profile.avatar_decoration_url ? '<img class="discord-profile-avatar-decoration" src="' + escapeHtml(profile.avatar_decoration_url) + '" alt="">' : '')
      + statusDot(profile) + '</span>'
    : '<span class="discord-profile-avatar-wrap"><span class="discord-profile-avatar discord-profile-avatar-fallback">' + escapeHtml((String(profile.display_name || '?').trim().charAt(0) || '?').toUpperCase()) + '</span>'
      + statusDot(profile) + '</span>';
  const profileStatusBubble = (profile) => {{
    const customStatus = profile.custom_status || {{}};
    const statusEmoji = customStatus.emoji_id
      ? '<img class="discord-profile-status-emoji" src="https://cdn.discordapp.com/emojis/' + encodeURIComponent(customStatus.emoji_id) + (customStatus.emoji_animated ? '.gif' : '.png') + '" alt="">'
      : (customStatus.emoji_name ? '<span class="discord-profile-status-emoji">' + escapeHtml(customStatus.emoji_name) + '</span>' : '');
    if (!customStatus.text && !statusEmoji) return '';
    return '<div class="discord-profile-status"><span class="discord-profile-status-text">' + statusEmoji + escapeHtml(customStatus.text || '') + '</span></div>';
  }};
  const closeServerTagPopup = () => {{
    document.querySelector(".discord-server-tag-popup")?.remove();
    document.querySelectorAll("[data-server-tag][aria-expanded='true']").forEach((button) => button.setAttribute("aria-expanded", "false"));
  }};
  const placeServerTagPopup = (button) => {{
    const popup = document.querySelector(".discord-server-tag-popup");
    if (!popup) return;
    const rect = button.getBoundingClientRect();
    const margin = 12;
    const gap = 8;
    const width = popup.offsetWidth;
    const height = popup.offsetHeight;
    const left = Math.max(margin, Math.min(rect.left + rect.width / 2 - width / 2, window.innerWidth - width - margin));
    const below = rect.bottom + gap;
    const top = below + height <= window.innerHeight - margin
      ? below
      : Math.max(margin, rect.top - height - gap);
    popup.style.left = left + "px";
    popup.style.top = Math.min(top, window.innerHeight - height - margin) + "px";
  }};
  const formatCount = (value) => Number.isFinite(value) && value >= 0
    ? new Intl.NumberFormat().format(Math.round(value))
    : "";
  const monthYear = (unix) => {{
    if (!Number.isFinite(unix)) return "";
    const date = new Date(unix * 1000);
    return Number.isFinite(date.getTime())
      ? new Intl.DateTimeFormat(undefined, {{ month: "short", year: "numeric" }}).format(date)
      : "";
  }};
  // Discord's server-tag popup has three states: a public server with its
  // identity, a private server that has limited who can see it, and a server
  // Niko is not in so nothing about it could be read.
  const serverTagPopup = (server, tag, badgeUrl) => {{
    const isPrivate = Boolean(server && server.private);
    const isUnknown = !isPrivate && !(server && server.available);
    const showDetails = !isPrivate && !isUnknown;
    const name = isPrivate ? "Private Server" : isUnknown ? "Unknown Server" : ((server && server.name) || tag || "Server");
    const description = isPrivate
      ? "The server has limited who can see this profile."
      : isUnknown
        ? "This server is unavailable, or Niko is not a member of it."
        : ((server && server.description) || "");
    const banner = showDetails && server && server.banner_url
      ? '<img class="discord-server-tag-banner" src="' + escapeHtml(server.banner_url) + '" alt="">'
      : '<div class="discord-server-tag-banner" aria-hidden="true"></div>';
    const icon = showDetails && server && server.icon_url
      ? '<img class="discord-server-tag-icon" src="' + escapeHtml(server.icon_url) + '" alt="">'
      : '<span class="discord-server-tag-icon is-placeholder" aria-hidden="true">?</span>';
    const stats = [];
    if (showDetails && server) {{
      const online = formatCount(server.online_count);
      const members = formatCount(server.member_count);
      if (online) stats.push('<span class="discord-server-tag-online"><i aria-hidden="true"></i>' + escapeHtml(online) + ' Online</span>');
      if (members) stats.push('<span class="discord-server-tag-members"><i aria-hidden="true"></i>' + escapeHtml(members) + ' Members</span>');
    }}
    const established = showDetails && server ? monthYear(server.created_at) : "";
    const badge = badgeUrl ? '<img src="' + escapeHtml(badgeUrl) + '" alt="">' : "";
    // Discord offers Go to Server to viewers who already belong to the server.
    // Everyone else gets Join only when the guild has a vanity invite it can
    // use; with no invite to offer the button is left out entirely.
    const isMember = Boolean(server && server.viewer_is_member);
    const memberUrl = isMember && server && server.id ? 'https://discord.com/channels/' + server.id : null;
    const joinUrl = showDetails && !isMember && server ? server.invite_url : null;
    const button = memberUrl
      ? '<a class="discord-server-tag-invite" href="' + escapeHtml(memberUrl) + '" target="_blank" rel="noopener noreferrer">Go to Server</a>'
      : joinUrl
        ? '<a class="discord-server-tag-invite is-join" href="' + escapeHtml(joinUrl) + '" target="_blank" rel="noopener noreferrer">Join</a>'
        : '';
    return '<div class="discord-server-tag-popup' + (isPrivate ? ' is-private' : '') + (isUnknown ? ' is-unknown' : '') + '" role="dialog" aria-label="' + escapeHtml(name) + ' server tag">'
      + banner
      + '<div class="discord-server-tag-body">'
      + '<div class="discord-server-tag-icon-shell">' + icon + '</div>'
      + '<div class="discord-server-tag-title-row"><h3 class="discord-server-tag-name">' + escapeHtml(name) + '</h3>'
      + (tag && !isPrivate ? '<span class="discord-server-tag-pill">' + badge + '<span>' + escapeHtml(tag) + '</span></span>' : '')
      + '</div>'
      + (stats.length ? '<p class="discord-server-tag-stats">' + stats.join('') + '</p>' : '')
      + (established ? '<p class="discord-server-tag-created">Est. ' + escapeHtml(established) + '</p>' : '')
      + (description ? '<p class="discord-server-tag-description">' + escapeHtml(description) + '</p>' : '')
      + button + '</div></div>';
  }};
  const clock = (seconds) => {{ const total = Math.max(0, Math.round(Number(seconds) || 0)); return Math.floor(total / 60) + ':' + String(total % 60).padStart(2, '0'); }};
  const profileSpotify = (profile) => {{
    const spotify = (profile.activities || []).find((activity) => activity && activity.album_cover_url);
    if (!spotify) return {{ html: '', timing: null }};
    const timing = Number.isFinite(spotify.start) && Number.isFinite(spotify.end) && spotify.end > spotify.start
      ? {{ start: spotify.start, total: spotify.duration_seconds || (spotify.end - spotify.start) }}
      : null;
    const inner = '<div class="discord-profile-spotify">'
      + '<div class="discord-profile-spotify-head">Listening to Spotify</div>'
      + '<div class="discord-profile-spotify-body">'
      + '<img class="discord-profile-spotify-art" src="' + escapeHtml(spotify.album_cover_url) + '" alt="">'
      + '<div class="discord-profile-spotify-copy"><strong>' + escapeHtml(spotify.title || 'Spotify') + '</strong>'
      + ((spotify.artists || []).length ? '<small>' + escapeHtml(spotify.artists.join(', ')) + '</small>' : '')
      + (timing ? '<div class="discord-profile-spotify-progress"><span data-spotify-elapsed></span><span class="discord-profile-spotify-track" aria-hidden="true"><i data-spotify-fill></i></span><span>' + clock(timing.total) + '</span></div>' : '')
      + '</div></div></div>';
    return {{ html: spotify.url ? '<a class="discord-profile-spotify-link" href="' + escapeHtml(spotify.url) + '" target="_blank" rel="noopener noreferrer">' + inner + '</a>' : inner, timing: timing }};
  }};
  const bindSpotify = (card, timing) => {{
    // A presence refresh rebinds the progress bar to the track it now shows.
    stopProfileTimer();
    if (!timing) return;
    const fill = card.querySelector("[data-spotify-fill]");
    const elapsedNode = card.querySelector("[data-spotify-elapsed]");
    const tick = () => {{
      const elapsed = Math.min(Math.max(Math.floor(Date.now() / 1000) - timing.start, 0), timing.total);
      if (fill) fill.style.width = (timing.total > 0 ? (elapsed / timing.total) * 100 : 0) + '%';
      if (elapsedNode) elapsedNode.textContent = clock(elapsed);
    }};
    tick();
    profileTimer = setInterval(tick, 1000);
  }};
  const openProfile = (link) => {{
    closeProfile();
    const profile = mentionProfiles[link.dataset.discordUserId];
    if (!profile) return;
    const rect = link.getBoundingClientRect();
    const width = Math.min(320, window.innerWidth - 24);
    const left = Math.max(12, Math.min(rect.left, window.innerWidth - width - 12));
    const top = Math.max(12, Math.min(rect.bottom + 8, window.innerHeight - 320));
    const popover = document.createElement("div");
    popover.className = "discord-profile-popover";
    const card = document.createElement("div");
    card.className = "discord-profile-card";
    card.setAttribute("role", "dialog");
    card.setAttribute("aria-label", escapeHtml(profile.display_name) + " Discord profile");
    card.style.setProperty("--profile-left", left + "px");
    card.style.setProperty("--profile-top", top + "px");
    const banner = profile.banner_url
      ? '<img class="discord-profile-banner" src="' + escapeHtml(profile.banner_url) + '" alt="">'
      : '<div class="discord-profile-banner" style="background-color:' + (/^#[0-9a-f]+$/i.test(profile.banner_color || '') && profile.banner_color.length === 7 ? profile.banner_color : '#202225') + '"></div>';
    const avatar = profileAvatar(profile);
    const statusBubble = profileStatusBubble(profile);
    const guildTagInner = (profile.guild_badge_url ? '<img src="' + escapeHtml(profile.guild_badge_url) + '" alt="">' : '') + '<span>' + escapeHtml(profile.guild_tag) + '</span>';
    const guildTag = profile.guild_tag
      ? (profile.server_tag
        ? '<button type="button" class="discord-profile-guild-tag" data-server-tag aria-haspopup="dialog" aria-expanded="false" title="' + escapeHtml(profile.guild_tag) + ' server tag">' + guildTagInner + '</button>'
        : '<span class="discord-profile-guild-tag">' + guildTagInner + '</span>')
      : '';
    const badges = (profile.badges || []).map((key) => {{
      const badge = badgeArt[key];
      if (!badge || !badge.src) return '';
      const label = badge.label ? ' alt="" aria-label="' + escapeHtml(badge.label) + '" title="' + escapeHtml(badge.label) + '"' : ' alt=""';
      return '<button type="button" class="discord-profile-badge-button" data-badge-key="' + escapeHtml(key) + '" aria-haspopup="dialog" aria-expanded="false"' + label + '><img class="discord-profile-badge" src="' + badge.src + '"></button>';
    }}).join('');
    const spotify = profileSpotify(profile);
    const menu = '<div class="discord-profile-menu"><button type="button" class="discord-profile-menu-button" aria-label="More options" aria-haspopup="menu" aria-expanded="false" data-profile-menu-button><span class="discord-profile-menu-dots" aria-hidden="true"><i></i><i></i><i></i></span></button><div class="discord-profile-menu-list" role="menu" hidden><button type="button" class="discord-profile-menu-item" role="menuitem" data-copy-user-id>Copy User ID</button></div></div>';
    card.innerHTML = banner + menu + '<div class="discord-profile-body">'
      + '<div class="discord-profile-head">' + avatar + statusBubble + '</div>'
      + '<h2 class="discord-profile-name">' + escapeHtml(profile.display_name) + '</h2>'
      + '<p class="discord-profile-username"><span class="discord-profile-user-tag">' + escapeHtml(profile.username) + '</span>' + guildTag + '</p>'
      + (badges ? '<div class="discord-profile-badges">' + badges + '</div>' : '')
      + (profile.bio ? '<section class="discord-profile-about"><h3>About Me</h3><p>' + escapeHtml(profile.bio) + '</p></section>' : '')
      + '<div data-profile-spotify>' + spotify.html + '</div>'
      + '<a class="discord-profile-full-link" href="https://discord.com/users/' + encodeURIComponent(profile.id) + '" target="_blank" rel="noopener noreferrer">Open Discord profile</a>'
      + '</div>';
    popover.appendChild(card);
    document.body.appendChild(popover);
    popover.addEventListener("click", (event) => {{ if (event.target === popover) closeProfile(); }});
    // A badge click opens the badge popup: the badge art on the left, its name
    // and description on the right. It is appended to the page instead of the
    // card, so it renders on top of the profile popup rather than inside it.
    const badgesRow = card.querySelector('.discord-profile-badges');
    if (badgesRow) {{
      const closeBadgePopup = () => {{
        document.querySelector('.discord-badge-popup')?.remove();
        badgesRow.querySelectorAll('[data-badge-key]').forEach((button) => button.setAttribute('aria-expanded', 'false'));
      }};
      const placeBadgePopup = (button) => {{
        const popup = document.querySelector('.discord-badge-popup');
        if (!popup) return;
        const rect = button.getBoundingClientRect();
        const margin = 12;
        const gap = 8;
        const width = popup.offsetWidth;
        const height = popup.offsetHeight;
        const left = Math.max(margin, Math.min(rect.left + rect.width / 2 - width / 2, window.innerWidth - width - margin));
        const below = rect.bottom + gap;
        const top = below + height <= window.innerHeight - margin
          ? below
          : Math.max(margin, rect.top - height - gap);
        popup.style.left = left + 'px';
        popup.style.top = Math.min(top, window.innerHeight - height - margin) + 'px';
      }};
      const openBadgePopup = (button) => {{
        const badge = badgeArt[button.dataset.badgeKey];
        closeBadgePopup();
        if (!badge || !badge.src) return;
        const popup = document.createElement('div');
        popup.className = 'discord-badge-popup';
        popup.setAttribute('role', 'dialog');
        popup.setAttribute('aria-label', escapeHtml(badge.label) + ' badge');
        popup.innerHTML = '<img class="discord-badge-popup-art" src="' + badge.src + '" alt="">'
          + '<div class="discord-badge-popup-copy"><strong>' + escapeHtml(badge.label) + '</strong><p>' + escapeHtml(badge.description) + '</p></div>';
        document.body.appendChild(popup);
        placeBadgePopup(button);
        button.setAttribute('aria-expanded', 'true');
      }};
      badgesRow.addEventListener('click', (event) => {{
        const button = event.target.closest('[data-badge-key]');
        if (!button) return;
        if (button.getAttribute('aria-expanded') === 'true') closeBadgePopup();
        else openBadgePopup(button);
      }});
      // Keep the floating popup under its badge as the page or the card scrolls,
      // and close it when the click lands anywhere else.
      const followBadgePopup = () => {{
        const button = badgesRow.querySelector('[data-badge-key][aria-expanded="true"]');
        if (button) placeBadgePopup(button);
      }};
      window.addEventListener('resize', followBadgePopup);
      window.addEventListener('scroll', followBadgePopup, true);
      document.addEventListener('mousedown', (event) => {{
        if (event.target instanceof Element && event.target.closest('.discord-badge-popup')) return;
        closeBadgePopup();
      }});
    }}
    const serverTagButton = card.querySelector("[data-server-tag]");
    if (serverTagButton) {{
      serverTagButton.addEventListener("click", () => {{
        if (serverTagButton.getAttribute("aria-expanded") === "true") {{ closeServerTagPopup(); return; }}
        closeServerTagPopup();
        const holder = document.createElement("div");
        const renderTagPopup = (tagProfile) => {{
          holder.innerHTML = serverTagPopup(tagProfile.server_tag, tagProfile.guild_tag, tagProfile.guild_badge_url);
          const next = holder.firstElementChild;
          if (!next) return;
          document.querySelector(".discord-server-tag-popup")?.remove();
          document.body.appendChild(next);
          placeServerTagPopup(serverTagButton);
          serverTagButton.setAttribute("aria-expanded", "true");
        }};
        renderTagPopup(profile);
        // An exported transcript can be viewed by someone other than the
        // person who generated it, so refresh the profile once from the live
        // API to pick up this viewer's server membership. A downloaded copy
        // has no API to call, and keeps the state embedded at export time.
        if (profile.id) {{
          fetch("/api/discord/users/" + encodeURIComponent(profile.id))
            .then((response) => response.ok ? response.json() : null)
            .then((fresh) => {{
              if (fresh && fresh.server_tag && serverTagButton.getAttribute("aria-expanded") === "true") renderTagPopup(fresh);
            }})
            .catch(() => {{}});
        }}
      }});
    }}
    const menuButton = card.querySelector("[data-profile-menu-button]");
    const menuList = card.querySelector(".discord-profile-menu-list");
    if (menuButton && menuList) {{
      menuButton.addEventListener("click", () => {{
        menuList.hidden = !menuList.hidden;
        menuButton.setAttribute("aria-expanded", String(!menuList.hidden));
      }});
    }}
    const copyButton = card.querySelector("[data-copy-user-id]");
    if (copyButton) {{
      copyButton.addEventListener("click", () => {{
        const write = navigator.clipboard && navigator.clipboard.writeText
          ? navigator.clipboard.writeText(String(profile.id))
          : Promise.reject(new Error("clipboard unavailable"));
        write.then(() => {{ copyButton.textContent = "Copied!"; }}, () => {{}});
      }});
    }}
    bindSpotify(card, spotify.timing);
    // Presence moves while the card is open, so an open popup re-reads the same
    // public endpoint the website popup uses instead of freezing the presence it
    // was opened with. The embedded snapshot stays the source when the API cannot
    // be reached: a transcript opened from disk is a file, so the poll only runs
    // over http(s) and a failed read keeps the last known profile.
    const profileId = String(profile.id || '');
    const applyPresence = (next) => {{
      if (!next || !card.isConnected) return;
      const head = card.querySelector('.discord-profile-head');
      if (head) head.innerHTML = profileAvatar(next) + profileStatusBubble(next);
      const spotifyNode = card.querySelector('[data-profile-spotify]');
      const nextSpotify = profileSpotify(next);
      if (spotifyNode) spotifyNode.innerHTML = nextSpotify.html;
      bindSpotify(card, nextSpotify.timing);
    }};
    if (/^\d{{1,22}}$/.test(profileId) && typeof window.fetch === "function" && location.protocol.indexOf("http") === 0) {{
      const loadPresence = () => {{
        fetch("/api/discord/users/" + encodeURIComponent(profileId))
          .then((response) => (response.ok ? response.json() : null))
          .then(applyPresence)
          .catch(() => {{}});
      }};
      refreshProfilePresence = () => {{ if (document.visibilityState === "visible") loadPresence(); }};
      document.addEventListener("visibilitychange", refreshProfilePresence);
      profilePollTimer = setInterval(() => {{ if (document.visibilityState === "visible") loadPresence(); }}, 5000);
    }}
  }};
  document.addEventListener("click", (event) => {{
    const emoji = event.target.closest?.("img.custom-emoji[data-emoji-id]");
    if (emoji) {{
      event.preventDefault();
      closeProfile();
      openEmojiPopup(emoji);
      return;
    }}
    const link = event.target.closest?.("[data-discord-user-id]");
    if (!link) {{
      // The badge and server popups float outside the card on purpose; a click
      // inside either one does not dismiss the profile it belongs to.
      if (!event.target.closest?.(".discord-profile-card") && !event.target.closest?.(".discord-badge-popup") && !event.target.closest?.(".discord-server-tag-popup")) closeProfile();
      return;
    }}
    event.preventDefault();
    openProfile(link);
  }});
  document.addEventListener("click", (event) => {{
    if (event.target.closest?.("img.custom-emoji[data-emoji-id]")) return;
    if (!event.target.closest?.(".discord-emoji-popup")) closeEmojiPopup();
  }});
  document.addEventListener("keydown", (event) => {{
    // A floating server-tag popup is the topmost layer, so Escape closes it
    // and leaves the profile underneath open for the next Escape.
    if (event.key === "Escape" && document.querySelector(".discord-server-tag-popup")) {{ closeServerTagPopup(); return; }}
    if (event.key === "Escape") {{ closeEmojiPopup(); closeProfile(); }}
    if ((event.key === "Enter" || event.key === " ") && event.target.matches?.("img.custom-emoji[data-emoji-id]")) {{ event.preventDefault(); openEmojiPopup(event.target); return; }}
    if ((event.key === "Enter" || event.key === " ") && event.target.matches?.("[data-discord-user-id]")) {{ event.preventDefault(); openProfile(event.target); }}
  }});
  // Keep the server popup under its tag as the page or the profile card scrolls.
  const followServerTagPopup = () => {{
    const button = document.querySelector('[data-server-tag][aria-expanded="true"]');
    if (button) placeServerTagPopup(button);
  }};
  window.addEventListener("resize", followServerTagPopup);
  window.addEventListener("scroll", followServerTagPopup, true);
  document.addEventListener("mousedown", (event) => {{
    if (event.target.closest?.(".discord-server-tag-popup") || event.target.closest?.("[data-server-tag]")) return;
    closeServerTagPopup();
  }});
  const styles = {{
    t: {{ hour: "numeric", minute: "2-digit" }},
    T: {{ hour: "numeric", minute: "2-digit", second: "2-digit" }},
    d: {{ year: "numeric", month: "2-digit", day: "2-digit" }},
    D: {{ year: "numeric", month: "long", day: "numeric" }},
    f: {{ year: "numeric", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }},
    F: {{ weekday: "long", year: "numeric", month: "long", day: "numeric", hour: "numeric", minute: "2-digit" }}
  }};
  document.querySelectorAll("[data-discord-ts]").forEach((node) => {{
    const unix = Number(node.dataset.discordTs);
    const style = node.dataset.discordStyle;
    if (!Number.isFinite(unix)) return;
    if (style === "R") {{
      const seconds = unix - Math.floor(Date.now() / 1000);
      const abs = Math.abs(seconds);
      const unit = abs < 60 ? "second" : abs < 3600 ? "minute" : abs < 86400 ? "hour" : abs < 604800 ? "day" : abs < 2592000 ? "week" : abs < 31536000 ? "month" : "year";
      const divisor = {{ second: 1, minute: 60, hour: 3600, day: 86400, week: 604800, month: 2592000, year: 31536000 }}[unit];
      node.textContent = new Intl.RelativeTimeFormat(undefined, {{ numeric: "always" }}).format(Math.round(seconds / divisor), unit);
    }} else if (styles[style]) {{
      node.textContent = new Intl.DateTimeFormat(undefined, styles[style]).format(new Date(unix * 1000));
    }}
  }});
}})();
</script>
</body>
</html>"""


def export_csv(messages: List[dict]) -> str:
    """CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "author", "author_id", "content", "attachments", "embeds", "components"])
    for msg in messages:
        writer.writerow([
            msg.get("timestamp", ""),
            msg.get("author", ""),
            msg.get("author_id", ""),
            msg.get("content", ""),
            " | ".join(msg.get("attachments", [])),
            json.dumps(msg.get("embeds", []), ensure_ascii=False),
            json.dumps(msg.get("components", []), ensure_ascii=False),
        ])
    return output.getvalue()


def export_json(messages: List[dict], metadata: dict) -> str:
    """JSON format with metadata wrapper."""
    return json.dumps({
        "metadata": metadata,
        "messages": messages,
    }, indent=2, ensure_ascii=False)
