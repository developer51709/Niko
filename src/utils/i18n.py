"""The one place that turns a guild's locale into a shipped language code.

Every cog resolves its wording through :func:`get_lang` instead of growing its
own ``_lang``/``get_lang``/``_panel_lang`` copy, so a new shipped language is a
one-line change in :data:`utils.locales.SUPPORTED_LANGUAGES`.
"""

from __future__ import annotations

from utils.locales import FALLBACK_LANGUAGE, SUPPORTED_LANGUAGES


def lang_from_locale(locale) -> str:
    """Map any Discord locale (``fr``, ``fr-FR``) to a shipped language code."""
    raw = str(locale or "").strip().lower()
    for code in SUPPORTED_LANGUAGES:
        if code != FALLBACK_LANGUAGE and raw.startswith(code):
            return code
    return FALLBACK_LANGUAGE


def guild_of(source):
    """The guild behind a command context, interaction, guild, or locale shim.

    Contexts and interactions carry ``.guild``; a guild carries the locale
    itself, which is what a DM to a server owner, a seeded panel, or a stored
    ``SimpleNamespace(preferred_locale=…)`` hands over.
    """
    if source is None:
        return None
    guild = getattr(source, "guild", None)
    if guild is not None:
        return guild
    if getattr(source, "preferred_locale", None) is not None:
        return source
    return None


def get_lang(source=None) -> str:
    """The shipped language code for a context, interaction, or guild.

    Anything without a guild (a DM, a web request) is served English, which is
    the same fallback a guild with an unsupported locale gets.
    """
    return lang_from_locale(getattr(guild_of(source), "preferred_locale", None))


def make_flat_msg(messages: dict, defaults: dict | None = None):
    """
    Return a ``msg(ctx, key, **kwargs)`` function bound to a flat
    language dictionary (lang → key → value).

    Falls back: lang → en → key itself.

    ``defaults`` fills ``{name}`` tokens that every message may use but no call
    site should have to repeat — a cog's own emoji, its configured links, a
    document date. It is substituted before ``str.format``, so a message that
    only carries those tokens does not need any keyword arguments.

    Usage in a cog module::

        from utils.i18n import make_flat_msg
        from utils.locales import load_locales

        MESSAGES = load_locales(__package__, "views")
        msg = make_flat_msg(MESSAGES, {"tick": get_emoji("tick")})
    """
    defaults = dict(defaults or {})

    def msg(ctx, key, **kwargs):
        lang = get_lang(ctx)
        text = messages.get(lang, {}).get(key) or messages.get("en", {}).get(key, key)
        for name, value in defaults.items():
            token = "{" + name + "}"
            if token in text:
                text = text.replace(token, value)
        return text.format(**kwargs) if kwargs else text
    return msg
