from utils.ai_config import get_personality


def get_lang(ctx) -> str:
    """Return 'de' if the guild's preferred locale is German, else 'en'."""
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"


def resolve_msg(ctx, messages: dict, key: str, **kwargs) -> str:
    """
    Resolve a translated string from a MESSAGES dict.

    messages layout:
        {
            "normal": {"en": {key: str, ...}, "de": {key: str, ...}},
            "cafe":   {"en": {key: str, ...}, "de": {key: str, ...}},
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
    Return a ``msg(ctx, key, **kwargs)`` function bound to *messages*.

    Usage in a cog module::

        from utils.i18n import make_msg
        MESSAGES = { ... }
        msg = make_msg(MESSAGES)
    """
    def msg(ctx, key, **kwargs):
        return resolve_msg(ctx, messages, key, **kwargs)
    return msg
