"""Discord's content-scanning flags for attachments.

Discord scans uploaded media after a message is sent and sets one of the
``CONTAINS_*`` bits on the attachment when it decides the image is explicit,
gore, or self-harm. Reposting such a file — which is what a deleted-message log
does with its images — would put the media back in a channel, so the log swaps
in the website's placeholder artwork and explains the swap underneath it.

Scanning is asynchronous, so a flag can land after the log entry was posted: the
same helpers then read the result out of the message's raw components, and the
entry is edited to swap in the placeholder.

The flags are read from the raw bitfield rather than from ``AttachmentFlags``
members: discord.py only names the flags it knew about when it was released,
and an unknown bit would otherwise be dropped on the floor.

https://docs.discord.com/developers/resources/message#attachment-object-attachment-flags
"""

from __future__ import annotations

from config import links

#: The slugs used by the placeholder assets and the explainer page's ``?type=``.
EXPLICIT = "explicit"
GORE = "gore"
SELF_HARM = "self-harm"

#: ``(flag_type, bit)`` in the order Discord documents the flags. An image can
#: carry more than one bit; the first match names the placeholder so one image
#: never produces two notes.
FLAG_BITS: tuple[tuple[str, int], ...] = (
    (EXPLICIT, 1 << 4),
    (GORE, 1 << 6),
    (SELF_HARM, 1 << 7),
)

#: The logging locale key that names each type in the log note.
LABEL_KEYS: dict[str, str] = {
    EXPLICIT: "flag_explicit",
    GORE: "flag_gore",
    SELF_HARM: "flag_self_harm",
}

#: The flag types a served placeholder exists for.
FLAG_TYPES: tuple[str, ...] = tuple(flag for flag, _ in FLAG_BITS)

#: The component type of a media gallery in a raw message payload.
MEDIA_GALLERY_TYPE = 12


def flag_from_value(value) -> str | None:
    """The ``CONTAINS_*`` type a raw flag bitfield names, if any.

    Anything that does not look like a bitfield (an old library, a hand-built
    stub) simply reads as unflagged. When several bits are set the first one in
    ``FLAG_BITS`` wins, so one image never produces two notes.
    """
    if not isinstance(value, int) or isinstance(value, bool):
        return None
    for name, bit in FLAG_BITS:
        if value & bit:
            return name
    return None


def flag_type(attachment) -> str | None:
    """The ``CONTAINS_*`` type Discord flagged *attachment* with, if any."""
    if attachment is None:
        return None
    flags = getattr(attachment, "flags", None)
    return flag_from_value(getattr(flags, "value", flags))


def placeholder_url(flag: str) -> str:
    """The generated placeholder image that stands in for a flagged image."""
    return f"{links.FLAGGED_MEDIA_ASSETS}/{flag}.png"


def learn_more_url(flag: str) -> str:
    """The site page explaining why that placeholder is in the log."""
    return f"{links.FLAGGED_MEDIA_HELP}?type={flag}"


def placeholder_flag(url: str | None) -> str | None:
    """The flag type a gallery URL is already standing in for, if any.

    An entry that was edited once already shows the placeholder, so this is how
    a later scan wave tells what the gallery holds instead of re-replacing it
    and repeating its note.
    """
    if not url or not isinstance(url, str):
        return None
    prefix = f"{links.FLAGGED_MEDIA_ASSETS}/"
    if not url.startswith(prefix):
        return None
    name = url[len(prefix):].split("?", 1)[0]
    if name.endswith(".png"):
        name = name[:-4]
    return name if name in FLAG_TYPES else None


def is_flagged_note(text: str | None) -> bool:
    """Whether *text* is a note under a gallery explaining a placeholder."""
    return bool(text) and isinstance(text, str) and links.FLAGGED_MEDIA_HELP in text


def _gallery(components) -> dict | None:
    """The first media gallery in a raw ``components`` array, if there is one."""
    if not isinstance(components, (list, tuple)):
        return None
    for component in components:
        if not isinstance(component, dict):
            continue
        if component.get("type") == MEDIA_GALLERY_TYPE:
            return component
        found = _gallery(component.get("components"))
        if found is not None:
            return found
    return None


def _media_flag(media) -> str | None:
    """The flag a raw unfurled media item carries.

    Discord reports the content-scan result in ``content_scan_metadata.flags``;
    the item's own ``flags`` field is the older attachment flag set and is only
    read as a fallback, since a library that predates the metadata drops it.
    """
    if not isinstance(media, dict):
        return None
    metadata = media.get("content_scan_metadata")
    if isinstance(metadata, dict):
        flag = flag_from_value(metadata.get("flags"))
        if flag:
            return flag
    return flag_from_value(media.get("flags"))


def flagged_gallery_items(components) -> dict[int, str]:
    """Gallery position → flag type for the media Discord flagged in a payload.

    A log entry's own gallery is the one the entry built, so the positions match
    the ``media_flags`` the entry was rendered with: they are what tells the bot
    which placeholder has to go where.
    """
    gallery = _gallery(components)
    if gallery is None:
        return {}
    flagged: dict[int, str] = {}
    for index, item in enumerate(gallery.get("items") or []):
        if not isinstance(item, dict):
            continue
        flag = _media_flag(item.get("media"))
        if flag:
            flagged[index] = flag
    return flagged
