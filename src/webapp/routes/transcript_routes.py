"""Flask routes for transcript."""

import json

from flask import Response

from .. import server as _server
from .discord_text_routes import resolve_discord_text_mentions, resolve_discord_user_profiles

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

def _guild_identity(guild_id):
    """The ticket server's name and icon for the emoji popup's source row."""
    guild = None
    try:
        if _discord_bot is not None:
            guild = _discord_bot.get_guild(int(guild_id))
    except (AttributeError, TypeError, ValueError):
        guild = None
    if guild is None:
        return {"guild_name": "Server", "guild_icon_url": None}
    icon = getattr(guild, "icon", None)
    return {
        "guild_name": getattr(guild, "name", None) or "Server",
        "guild_icon_url": str(icon.url) if icon is not None else None,
    }


def _resolve_transcript_mentions(guild_id, messages):
    """Resolve all transcript mentions through the shared bounded resolver."""
    if not isinstance(messages, list):
        return {"user": {}, "channel": {}, "role": {}}
    # Scan the full serialized payload: mentions can appear in content, embeds,
    # and nested Components V2 text fields, not only the top-level content.
    text = json.dumps(messages, ensure_ascii=False)
    return resolve_discord_text_mentions(guild_id, text)


@app.route("/api/transcript/<transcript_id>")
def api_get_transcript(transcript_id):
    """Fetch a transcript by its short ID."""
    if _discord_bot is None or not getattr(_discord_bot, "cxn", None):
        return jsonify({"error": "Database unavailable."}), 503
    try:
        row = run_on_bot_loop(_discord_bot.cxn.fetchrow(
            "SELECT * FROM transcripts WHERE transcript_id = $1",
            transcript_id,
        ))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    if row is None:
        return jsonify({"error": "Transcript not found."}), 404
    result = dict(row)
    messages = result.get("messages")
    if isinstance(messages, str):
        try:
            result["messages"] = json.loads(messages)
        except (json.JSONDecodeError, TypeError):
            result["messages"] = []
    result.update(_guild_identity(result.get("guild_id")))
    result["mention_names"] = _resolve_transcript_mentions(
        result.get("guild_id"), result.get("messages", [])
    )
    # The web transcript draws the same author row as the HTML export, so the
    # page gets avatars and display names for every message author up front.
    author_ids = [
        message.get("author_id") for message in result.get("messages", [])
        if isinstance(message, dict) and message.get("author_id")
    ]
    result["author_profiles"] = resolve_discord_user_profiles(
        result.get("guild_id"), "", author_ids
    )
    return jsonify(result)

@app.route("/api/transcript/<transcript_id>/download")
def api_download_transcript(transcript_id):
    """Download a transcript in the specified format."""
    fmt = request.args.get("format", "txt").lower()
    if fmt not in {"txt", "html", "csv", "json"}:
        return jsonify({"error": "Invalid format. Supported: txt, html, csv, json"}), 400

    if _discord_bot is None or not getattr(_discord_bot, "cxn", None):
        return jsonify({"error": "Database unavailable."}), 503
    try:
        row = run_on_bot_loop(_discord_bot.cxn.fetchrow(
            "SELECT * FROM transcripts WHERE transcript_id = $1",
            transcript_id,
        ))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    if row is None:
        return jsonify({"error": "Transcript not found."}), 404

    result = dict(row)
    messages = result.get("messages", [])
    if isinstance(messages, str):
        try:
            messages = json.loads(messages)
        except (json.JSONDecodeError, TypeError):
            messages = []

    metadata = {
        "channel_name": result.get("channel_name", "unknown"),
        "guild_id": result.get("guild_id"),
        "opener_id": result.get("opener_id"),
        "category": result.get("category"),
        "created_at": result.get("created_at"),
        "message_count": result.get("message_count", len(messages)),
    }

    if fmt == "txt":
        from utils.tickets.transcripts import export_txt
        content = export_txt(messages)
        return Response(
            content,
            mimetype="text/plain",
            headers={"Content-Disposition": f'attachment; filename="transcript-{transcript_id}.txt"'},
        )
    elif fmt == "html":
        from utils.tickets.transcripts import export_html
        metadata.update(_guild_identity(result.get("guild_id")))
        mention_text = json.dumps(messages, ensure_ascii=False)
        mention_names = _resolve_transcript_mentions(result.get("guild_id"), messages)
        author_ids = [
            message.get("author_id") for message in messages
            if isinstance(message, dict) and message.get("author_id")
        ]
        user_profiles = resolve_discord_user_profiles(
            result.get("guild_id"), mention_text, author_ids
        )
        content = export_html(messages, metadata, mention_names, user_profiles)
        return Response(
            content,
            mimetype="text/html",
            headers={"Content-Disposition": f'attachment; filename="transcript-{transcript_id}.html"'},
        )
    elif fmt == "csv":
        from utils.tickets.transcripts import export_csv
        content = export_csv(messages)
        return Response(
            content,
            mimetype="text/csv",
            headers={"Content-Disposition": f'attachment; filename="transcript-{transcript_id}.csv"'},
        )
    elif fmt == "json":
        from utils.tickets.transcripts import export_json
        content = export_json(messages, metadata)
        return Response(
            content,
            mimetype="application/json",
            headers={"Content-Disposition": f'attachment; filename="transcript-{transcript_id}.json"'},
        )
