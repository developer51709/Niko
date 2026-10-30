"""
Moderation i18n — MESSAGES table, msg() helper, and shared view/purge utilities.

The strings carry ``{kick}``/``{warn}``-style placeholders instead of raw
Unicode emoji, and :data:`EMOJI` fills them with the bot's own art, so a
moderation reply draws the same neutral icons as every other Niko surface
rather than Discord's colourful built-ins.
"""
import discord
from config.emojis import get_emoji
from utils.i18n import make_flat_msg
from utils.ratelimit import purge_limiter
from utils.locales import load_locales

#: Filled into every message below by :func:`msg`. Module level on purpose:
#: the emoji sync rewrites these in place when an emoji is re-uploaded, so a
#: replacement reaches these replies without a restart.
EMOJI = {
    "kick":     get_emoji("log_kick"),
    "ban":      get_emoji("log_ban"),
    "unban":    get_emoji("log_unban"),
    "warn":     get_emoji("log_warn"),
    "tick":     get_emoji("tick"),
    "mute":     get_emoji("log_mute"),
    "tempmute": get_emoji("log_tempmute"),
    "unmute":   get_emoji("log_unmute"),
    "slowmode": get_emoji("pause"),
    "lock":     get_emoji("lock"),
    "unlock":   get_emoji("unlock"),
    "nick":     get_emoji("log_nickname"),
    "cross":    get_emoji("cross"),
}

MESSAGES = load_locales("cogs.moderation", "messages")

_flat_msg = make_flat_msg(MESSAGES)


def msg(ctx, key: str, **kwargs) -> str:
    """One localised reply with the bot's own emojis filled in."""
    return _flat_msg(ctx, key, **EMOJI, **kwargs)


def _cv2(text: str) -> discord.ui.LayoutView:
    """Wrap plain text in a cv2 Container."""
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return view


async def _delete_messages(channel, messages: list) -> list:
    """Delete a batch, falling back to one call each when bulk delete refuses.

    Discord only bulk-deletes messages younger than two weeks, so the batch
    call is tried first and anything it rejects is deleted individually.
    """
    if not messages:
        return []
    try:
        await channel.delete_messages(messages)
        return list(messages)
    except (discord.HTTPException, discord.Forbidden):
        pass
    deleted = []
    for message in messages:
        try:
            await message.delete()
            deleted.append(message)
        except (discord.HTTPException, discord.Forbidden):
            continue
    return deleted


async def _chunked_purge(channel, limit: int, check=None) -> list:
    """Delete messages in chunks of 100, up to ``limit`` messages scanned.

    Without a ``check`` this deletes ``limit`` messages. With one, ``limit``
    messages are *scanned* and every match among them is deleted — the meaning
    ``clear <amount> [member]`` has everywhere else. Stopping at the first page
    that happened to hold fewer matches, as this used to, left older messages
    from that member behind even though they were inside the requested range.
    """
    if check is None:
        deleted = []
        remaining = limit
        while remaining > 0:
            chunk = min(remaining, 100)
            await purge_limiter.acquire(channel.id)
            batch = await channel.purge(limit=chunk)
            deleted.extend(batch)
            remaining -= chunk
            if len(batch) < chunk:
                break
        return deleted

    deleted = []
    scanned = 0
    before = None
    while scanned < limit:
        chunk = min(limit - scanned, 100)
        await purge_limiter.acquire(channel.id)
        page = [message async for message in channel.history(limit=chunk, before=before)]
        if not page:
            break
        scanned += len(page)
        before = page[-1]  # newest-first: the last entry is the oldest scanned
        targets = [message for message in page if check(message)]
        deleted.extend(await _delete_messages(channel, targets))
    return deleted
