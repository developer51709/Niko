"""Automatic ticket transcripts.

A ticket only needs one transcript. The first close (or a delete without a
close) stores it and records its ID on the ticket entry, so reopening and
closing again rewrites that same row with the newer messages instead of
creating a second copy of the conversation.

Everything here is best-effort: a transcript that cannot be saved must never
stop a ticket from closing or being deleted.
"""

from __future__ import annotations

from utils import logging

from . import transcripts


async def auto_capture_transcript(bot, guild_id: int, channel, ticket, cfg) -> None:
    """Save or refresh a ticket's transcript when the guild opted into it."""
    if not getattr(cfg, "auto_transcript", False):
        return
    if channel is None or not isinstance(ticket, dict):
        return

    try:
        transcript_id = await transcripts.capture_ticket_transcript(
            bot.cxn,
            guild_id=guild_id,
            channel=channel,
            ticket=ticket,
        )
    except Exception as error:
        logging.warning(
            "Tickets",
            f"Automatic transcript failed for channel {getattr(channel, 'id', '?')}: {error}",
        )
        return

    if transcript_id:
        ticket["transcript_id"] = transcript_id
