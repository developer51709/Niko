"""Flask routes for transcript."""

from . import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

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
        guild_name = "Server"
        try:
            if _discord_bot:
                guild = _discord_bot.get_guild(int(result.get("guild_id", 0)))
                if guild:
                    guild_name = guild.name
        except Exception:
            pass
        metadata["guild_name"] = guild_name
        content = export_html(messages, metadata)
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
