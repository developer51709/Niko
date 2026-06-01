from utils.ai.config import get_personality


def get_lang(ctx) -> str:
    """Return 'de', 'es', or 'en' based on the guild's preferred locale."""
    if ctx and getattr(ctx, "guild", None) and getattr(ctx.guild, "preferred_locale", None):
        loc = str(ctx.guild.preferred_locale).lower()
        if loc.startswith("de"):
            return "de"
        if loc.startswith("es"):
            return "es"
    return "en"


def resolve_msg(ctx, messages: dict, key: str, **kwargs) -> str:
    """
    Resolve a translated string from a personality-aware MESSAGES dict.

    messages layout:
        {
            "normal": {"en": {key: str, ...}, "de": {key: str, ...}, "es": {...}},
            "cafe":   {"en": {key: str, ...}, "de": {key: str, ...}, "es": {...}},
        }

    Falls back: personality+lang → normal+lang → normal+en → key itself.
    """
    personality = "normal"
    try:
        if ctx:
            personality = get_personality(ctx)
    except Exception:
        pass

    lang = get_lang(ctx) if ctx else "en"

    text = messages.get(personality, {}).get(lang, {}).get(key)
    if text is None:
        text = messages.get("normal", {}).get(lang, {}).get(key)
    if text is None:
        text = messages.get("normal", {}).get("en", {}).get(key, key)

    return text.format(**kwargs) if kwargs else text


def make_msg(messages: dict):
    """
    Return a ``msg(ctx, key, **kwargs)`` function bound to a personality-aware
    *messages* dict (nested: personality → lang → key).

    Usage in a cog module::

        from utils.i18n import make_msg
        MESSAGES = {"normal": {"en": {...}, "de": {...}}, "cafe": {...}}
        msg = make_msg(MESSAGES)
    """
    def msg(ctx, key, **kwargs):
        return resolve_msg(ctx, messages, key, **kwargs)
    return msg


def make_flat_msg(messages: dict):
    """
    Return a ``msg(ctx, key, **kwargs)`` function bound to a flat
    *messages* dict (lang → key → value).

    Falls back: lang → en → key itself.

    Usage in a cog module::

        from utils.i18n import make_flat_msg
        MESSAGES = {"en": {key: str, ...}, "de": {...}, "es": {...}}
        msg = make_flat_msg(MESSAGES)
    """
    def msg(ctx, key, **kwargs):
        lang = get_lang(ctx)
        text = messages.get(lang, {}).get(key) or messages.get("en", {}).get(key, key)
        return text.format(**kwargs) if kwargs else text
    return msg
