def get_lang(ctx) -> str:
    """Return 'de', 'es', or 'en' based on the guild's preferred locale.

    ``ctx`` may be a command context or interaction (it carries ``.guild``) or a
    guild itself, which is what a DM to a server owner has to pass.
    """
    guild = getattr(ctx, "guild", None)
    if guild is None and getattr(ctx, "preferred_locale", None):
        guild = ctx
    locale = getattr(guild, "preferred_locale", None)
    if locale:
        loc = str(locale).lower()
        if loc.startswith("de"):
            return "de"
        if loc.startswith("es"):
            return "es"
    return "en"


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
