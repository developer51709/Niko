"""Presence helpers shared by the bot's commands and the website.

A member can hold a different status per client — desktop, web and mobile —
and Discord only swaps its round dot for a phone icon when the phone is the
client carrying the presence. Both the bot's /userinfo card and the website's
avatars need that same answer, so the rule lives here once.
"""


def status_name(value, default: str = "offline") -> str:
    """The bare status word for a ``discord.Status``, a string, or ``None``."""
    name = getattr(value, "name", None) or str(value or "")
    name = name.rsplit(".", 1)[-1].strip().lower()
    return name or default


def is_mobile_presence(member) -> bool:
    """Whether Discord would draw the phone icon for ``member``.

    The phone only replaces the dot while it is the client holding the
    presence: an active desktop or web session keeps the normal icon, which is
    also why an offline or streaming member never reads as mobile.
    """
    if member is None:
        return False
    if status_name(getattr(member, "mobile_status", "offline")) == "offline":
        return False
    return (
        status_name(getattr(member, "desktop_status", "offline")) == "offline"
        and status_name(getattr(member, "web_status", "offline")) == "offline"
    )
