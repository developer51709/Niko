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
from typing import Any, Dict, List, Optional

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


def _md_to_html(text: Any) -> str:
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

    lines = value.split("\n")
    html_lines = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("&gt; ") or stripped.startswith(">"):
            body = stripped[4:] if stripped.startswith("&gt; ") else stripped[1:].lstrip()
            html_lines.append(f'<span class="tq">&gt; {body}</span>')
        elif stripped.startswith("-# "):
            html_lines.append(f'<span class="tsm">{stripped[3:]}</span>')
        elif re.match(r"#{1,4}\s", stripped):
            html_lines.append(f'<span class="th">{stripped}</span>')
        else:
            html_lines.append(line)
    value = "<br>".join(html_lines)

    for key, replacement in code_holders.items():
        value = value.replace(key, replacement)
    return value


def _embed_to_html(embed: dict) -> str:
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
        parts.append(f'<div class="embed-desc">{_md_to_html(desc)}</div>')

    fields = embed.get("fields") or []
    if fields:
        field_html = []
        for field in fields:
            name = field.get("name", "")
            value = field.get("value", "")
            cls = "embed-field embed-field-inline" if field.get("inline") else "embed-field"
            field_html.append(
                f'<div class="{cls}"><div class="embed-field-name">{_md_to_html(name)}</div>'
                f'<div class="embed-field-value">{_md_to_html(value)}</div></div>'
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


def _component_to_html(component: dict) -> str:
    """Recursively render one CV2 component payload into HTML."""
    ctype = component.get("type")
    if ctype == _TYPE_CONTAINER:
        accent = _color_css(component.get("accent_color"))
        style = f"border-color: {accent};" if accent else ""
        bar = f'<div class="cv2-bar" style="background:{accent};"></div>' if accent else ""
        inner = "".join(_component_to_html(c) for c in _component_children(component))
        return (
            f'<div class="cv2-card" style="{style}">{bar}'
            f'<div class="cv2-card-inner">{inner}</div></div>'
        )
    if ctype == _TYPE_ACTION_ROW:
        inner = "".join(_component_to_html(c) for c in _component_children(component))
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
        main = "".join(_component_to_html(c) for c in children)
        return f'<div class="cv2-section">{main}</div>'
    if ctype == _TYPE_TEXT_DISPLAY:
        return f'<div class="cv2-text">{_md_to_html(component.get("content"))}</div>'
    if ctype == _TYPE_LABEL:
        return f'<div class="cv2-label">{_md_to_html(component.get("content"))}</div>'
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
            desc_html = f'<figcaption>{_md_to_html(desc)}</figcaption>' if desc else ""
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


def _components_to_html(components: List[dict]) -> str:
    return "".join(_component_to_html(c) for c in components)


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


def export_html(messages: List[dict], metadata: dict) -> str:
    """Styled HTML transcript page (rich: content, attachments, embeds, CV2)."""
    title = metadata.get("channel_name", "Transcript")
    guild = metadata.get("guild_name", "Server")
    created = metadata.get("created_at", "")
    msg_count = len(messages)

    msg_rows = []
    for msg in messages:
        ts = msg.get("timestamp", "")
        author = msg.get("author", "Unknown")
        author_id = msg.get("author_id", "")
        content = msg.get("content", "")

        content_html = f'<div class="content">{_md_to_html(content)}</div>' if content else ""

        attachments = msg.get("attachments") or []
        att_html = ""
        if attachments:
            att_html = '<div class="attachments">' + "".join(
                f'<a href="{_esc(a)}" target="_blank" rel="noopener noreferrer">📎 Attachment</a>'
                for a in attachments
            ) + "</div>"

        embeds_html = "".join(
            _embed_to_html(embed) for embed in msg.get("embeds") or []
            if isinstance(embed, dict)
        )

        components_html = _components_to_html(msg.get("components") or [])

        if not (content or attachments or embeds_html or components_html):
            content_html = '<div class="content ts-muted"><em>Message content unavailable</em></div>'

        msg_rows.append(
            f'<div class="message">'
            f'<div class="message-head"><span class="timestamp">{_esc(ts)}</span> '
            f'<span class="author">{_esc(author)}</span> '
            f'<span class="author-id">({_esc(author_id)})</span></div>'
            f'{content_html}{att_html}{embeds_html}{components_html}'
            f'</div>'
        )

    msg_block = chr(10).join(msg_rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Transcript — {_esc(title)}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: #1e1f22; color: #dbdee1; padding: 20px; }}
  .header {{ background: #2b2d31; border-radius: 8px; padding: 20px; margin-bottom: 20px; border: 1px solid #3f4147; }}
  .header h1 {{ font-size: 20px; color: #f2f3f5; margin-bottom: 8px; }}
  .header .meta {{ color: #949ba4; font-size: 13px; }}
  .message {{ padding: 10px 14px; border-bottom: 1px solid #2b2d31; line-height: 1.55; font-size: 14px; }}
  .message:hover {{ background: #2e3035; }}
  .message-head {{ margin-bottom: 2px; }}
  .timestamp {{ color: #949ba4; font-size: 11px; font-family: monospace; }}
  .author {{ color: #f2f3f5; font-weight: 600; }}
  .author-id {{ color: #949ba4; font-size: 11px; }}
  .content {{ color: #dbdee1; white-space: pre-wrap; word-break: break-word; }}
  .ts-muted {{ color: #6d737a; }}
  .tsm {{ color: #949ba4; font-size: 12px; }}
  .th {{ font-size: 16px; font-weight: 700; color: #f2f3f5; }}
  .tq {{ display: inline-block; color: #b5bac1; border-left: 3px solid #4e5058; padding-left: 8px; }}
  code {{ background: #2b2d31; padding: 1px 5px; border-radius: 4px; font-family: Consolas, monospace; font-size: 12px; color: #f2b8c2; }}
  .attachments {{ margin-top: 4px; }}
  .attachments a {{ color: #00a8fc; text-decoration: none; font-size: 12px; margin-right: 10px; }}
  .attachments a:hover, a:hover {{ text-decoration: underline; }}

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
<div class="header">
  <h1>#{_esc(title)}</h1>
  <div class="meta">{_esc(guild)} · {_esc(msg_count)} messages · Created {_esc(created)}</div>
</div>
{msg_block}
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
