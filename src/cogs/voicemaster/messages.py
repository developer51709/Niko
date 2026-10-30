"""Translations for the VoiceMaster cog.

Every user-facing string — the control panel, the setup prompts, the channel
info card and every command reply — resolves through this table. ``msg`` takes
a command context *or* an interaction, because both expose
``guild.preferred_locale`` (that is what :func:`utils.i18n.get_lang` reads);
the panel's button callbacks therefore localize without a context object.
Views that are built from an already-resolved language use ``text``.

English is the fallback for a missing key or a language without a translation,
and the command names themselves (``lock``, ``claim``, …) stay English because
they are literal commands, not prose.
"""

from __future__ import annotations

from types import SimpleNamespace

from utils.i18n import get_lang, make_flat_msg
from utils.locales import load_locales

MESSAGES = load_locales("cogs.voicemaster", "messages")

# Command help and argument text live in the same ``commands`` namespace every
# other cog uses; ``utils.command_locales`` resolves them by command path.


# ``msg(ctx_or_interaction, key, **values)`` resolves through the guild's locale.
msg = make_flat_msg(MESSAGES)


def text(lang: str, key: str, **values) -> str:
    """Resolve ``key`` for an already-known language code.

    Views that are constructed once per language (the control panel) cannot use
    ``msg`` because they have no context to read a locale from, so they pass the
    language they were built for.
    """
    template = MESSAGES.get(lang, {}).get(key) or MESSAGES["en"].get(key, key)
    return template.format(**values) if values else template


def language_of(context) -> str:
    """The language code for a context, an interaction, or a raw guild.

    Panels posted outside a command (the support server's seeded panels) only
    have the guild to read from, and a guild carries the locale directly while
    ``get_lang`` expects something that holds a ``guild``.
    """
    if context is not None and hasattr(context, "preferred_locale"):
        context = SimpleNamespace(guild=context)
    return get_lang(context)


__all__ = ["MESSAGES", "msg", "text", "language_of"]
