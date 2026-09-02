"""Web transcript storage and retrieval.

Transcripts are stored in the main database (MongoDB or SQLite) and served
through the Flask web API for browser-based viewing and multi-format downloads.
"""

from __future__ import annotations

import csv
import io
import json
import hashlib
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


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
        ``content``, and ``attachments`` keys.
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


# ── Format exporters ────────────────────────────────────────────────────────


def export_txt(messages: List[dict]) -> str:
    """Plain text format — one line per message."""
    lines = []
    for msg in messages:
        ts = msg.get("timestamp", "")
        author = msg.get("author", "Unknown")
        content = msg.get("content", "")
        attachments = msg.get("attachments", [])
        line = f"[{ts}] {author}: {content}"
        if attachments:
            line += f" [attachments: {', '.join(attachments)}]"
        lines.append(line)
    return "\n".join(lines)


def export_html(messages: List[dict], metadata: dict) -> str:
    """Styled HTML transcript page."""
    title = metadata.get("channel_name", "Transcript")
    guild = metadata.get("guild_name", "Server")
    created = metadata.get("created_at", "")
    msg_count = len(messages)

    msg_rows = []
    for msg in messages:
        ts = msg.get("timestamp", "")
        author = msg.get("author", "Unknown")
        author_id = msg.get("author_id", "")
        content = msg.get("content", "").replace("<", "&lt;").replace(">", "&gt;")
        attachments = msg.get("attachments", [])
        att_html = ""
        if attachments:
            att_html = '<div class="attachments">' + "".join(
                f'<a href="{a}" target="_blank">📎 Attachment</a>' for a in attachments
            ) + "</div>"
        msg_rows.append(
            f'<div class="message">'
            f'<span class="timestamp">{ts}</span> '
            f'<span class="author">{author}</span> '
            f'<span class="author-id">({author_id})</span>: '
            f'<span class="content">{content}</span>'
            f'{att_html}</div>'
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Transcript — {title}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: #1e1f22; color: #dbdee1; padding: 20px; }}
  .header {{ background: #2b2d31; border-radius: 8px; padding: 20px; margin-bottom: 20px; border: 1px solid #3f4147; }}
  .header h1 {{ font-size: 20px; color: #f2f3f5; margin-bottom: 8px; }}
  .header .meta {{ color: #949ba4; font-size: 13px; }}
  .message {{ padding: 8px 0; border-bottom: 1px solid #2b2d31; line-height: 1.5; font-size: 14px; }}
  .message:hover {{ background: #2e3035; border-radius: 4px; }}
  .timestamp {{ color: #949ba4; font-size: 11px; font-family: monospace; }}
  .author {{ color: #f2f3f5; font-weight: 600; }}
  .author-id {{ color: #949ba4; font-size: 11px; }}
  .content {{ color: #dbdee1; }}
  .attachments {{ margin-top: 4px; }}
  .attachments a {{ color: #00a8fc; text-decoration: none; font-size: 12px; }}
  .attachments a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<div class="header">
  <h1>#{title}</h1>
  <div class="meta">{guild} · {msg_count} messages · Created {created}</div>
</div>
{"chr(10).join(msg_rows)}
</body>
</html>"""


def export_csv(messages: List[dict]) -> str:
    """CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "author", "author_id", "content", "attachments"])
    for msg in messages:
        writer.writerow([
            msg.get("timestamp", ""),
            msg.get("author", ""),
            msg.get("author_id", ""),
            msg.get("content", ""),
            " | ".join(msg.get("attachments", [])),
        ])
    return output.getvalue()


def export_json(messages: List[dict], metadata: dict) -> str:
    """JSON format with metadata wrapper."""
    return json.dumps({
        "metadata": metadata,
        "messages": messages,
    }, indent=2, ensure_ascii=False)
