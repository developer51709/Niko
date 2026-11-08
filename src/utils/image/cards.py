"""Rendered command cards, and letting go of them once Discord has the bytes.

Every card the bot draws — economy balances and rewards, the shop and inventory
sheets, level cards, the Spotify panel and the Last.fm listings — is rendered for
one reply and never used again. One card is a megabyte or more of RGBA before it
is even encoded, and ``discord.File`` deliberately stubs out its stream's
``close`` so aiohttp cannot shut the buffer before a retry has read it. The PNG
therefore stays alive until the last reference is collected, which on a busy host
is a slow climb in RSS rather than anything a garbage collection is scheduled to
return.

:func:`edit_with_card` uploads a card and closes its stream before returning, so
the memory is handed back as soon as the command is done.
"""

from __future__ import annotations

import discord

from utils import logging


def release_card(card) -> None:
    """Close the PNG behind a ``discord.File`` (or a bare stream).

    Safe on ``None`` and safe to call twice: a send that failed partway through
    still has to give its buffer back.
    """
    if card is None:
        return
    stream = getattr(card, "fp", None)
    if stream is None:
        stream = card  # a bare BytesIO, or anything else with a close()
    else:
        # ``File.close`` restores the stream's own ``close`` after aiohttp's stub
        # replaced it. It only actually closes a file the ``File`` opened itself,
        # so the stream is closed below either way.
        try:
            card.close()
        except Exception:  # never let cleanup raise over a finished upload
            logging.debug("Cards", "Releasing an uploaded card file failed.")
    closer = getattr(stream, "close", None)
    if closer is None:
        return
    try:
        closer()
    except Exception:  # pragma: no cover - a closed stream is already freed
        logging.debug("Cards", "Closing an uploaded card stream failed.")


async def send_card(send, *, buffer, filename: str):
    """Hand *buffer* to *send* as a ``discord.File``, then free it.

    ``send`` receives the finished file, so the caller keeps its own route (an
    edit, a reply, an interaction follow-up) and still cannot forget the release.
    """
    card = discord.File(buffer, filename)
    try:
        return await send(card)
    finally:
        release_card(card)


async def edit_with_card(message, *, view, buffer, filename: str):
    """Edit *message* into a card, and free the PNG as soon as it is uploaded.

    This is the one way the economy, shop, level and Spotify cards are sent, so a
    command cannot upload a card and forget to release it.
    """
    card = discord.File(buffer, filename)
    try:
        return await message.edit(view=view, attachments=[card])
    finally:
        release_card(card)


async def reply_with_card(ctx, *, view, buffer, filename: str):
    """Reply with a card, falling back to a plain send, and free the upload.

    The processed frame stack a filter or a generator produces is the largest
    thing those commands build and it is never reused, so it is released here
    rather than whenever the event loop gets around to collecting it.
    """

    async def deliver(card):
        try:
            return await ctx.reply(view=view, file=card)
        except Exception:
            # A reply can fail on a deleted reference or a restricted channel;
            # the card still has somewhere to go.
            return await ctx.send(view=view, file=card)

    return await send_card(deliver, buffer=buffer, filename=filename)
