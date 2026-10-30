"""Push each command's catalogue translations to Discord.

Discord only shows a localized command name, description or option description
when the bulk-overwrite payload it receives carries ``name_localizations`` and
``description_localizations`` (see the application-commands documentation on
docs.discord.com). discord.py fills those maps from a ``Translator``, so a bot
that wants them must either declare every string as a ``locale_str`` or hand the
library the translations itself.

Niko keeps its wording in each cog's ``locales/*.json`` and builds decorators
with plain English strings, so without help the payload Discord receives is
always English. :func:`apply_command_localizations` extends each top-level
application command's ``to_dict`` so the payload carries the German and Spanish
text from the catalogue, including nested subcommands and every option.

The helper never changes how a command is declared, is safe to run more than
once, and leaves commands whose cog has no catalogue untouched.
"""

from __future__ import annotations

from types import MethodType
from typing import Any

from discord import Locale, app_commands
from discord.utils import MISSING

from utils.command_locales import CommandTexts, command_path, resolve_package

#: Discord speaks its own locale codes: German is ``de``, while Spanish ships as
#: both the European and the Latin American variant. A catalogue language can
#: therefore map to more than one Discord locale.
DISCORD_LOCALES: dict[str, tuple[str, ...]] = {
    "de": (Locale.german.value,),
    "es": (Locale.spain_spanish.value, Locale.latin_american_spanish.value),
}

#: Discord rejects the whole payload when a localization is too long, so a text
#: that outgrew the limit is trimmed here instead of failing every command sync.
NAME_LIMIT = 32
DESCRIPTION_LIMIT = 100

#: Option type numbers that hold other commands (subcommand = 1, group = 2)
#: rather than a value, so they carry their own name and description.
_COMMAND_OPTION_TYPES = {1, 2}

_LOCALIZED_ATTRIBUTE = "_niko_localized"


def _texts_for(command: Any) -> CommandTexts | None:
    """The catalogue that owns ``command``'s wording, if it has one."""
    callback = getattr(command, "callback", None)
    module = getattr(callback, "__module__", None) or getattr(command, "module", None)
    if not module:
        binding = getattr(command, "binding", None) or getattr(command, "cog", None)
        module = type(binding).__module__ if binding is not None else None
    package = resolve_package(module) if module else None
    return CommandTexts(package) if package else None


def _clamp(text: str, limit: int = DESCRIPTION_LIMIT) -> str:
    """Discord's field limits, applied instead of failing the whole sync."""
    text = (text or "").strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _expand(values: dict[str, str] | None, limit: int = DESCRIPTION_LIMIT) -> dict[str, str]:
    """``{"de": …, "es": …}`` → ``{"de": …, "es-ES": …, "es-419": …}``."""
    if not values:
        return {}
    expanded: dict[str, str] = {}
    for language, text in values.items():
        clamped = _clamp(text, limit)
        if not clamped:
            continue
        for code in DISCORD_LOCALES.get(language, ()):
            expanded[code] = clamped
    return expanded


def _is_blank(description: Any) -> bool:
    """True when discord.py has no description for an option.

    Options declared without ``@app_commands.describe`` carry the library's
    ``MISSING`` sentinel, which serialises to a lonely ellipsis in Discord's UI.
    """
    if description is None or description is MISSING:
        return True
    text = str(description).strip()
    return not text or text == "…"


def _localizations(texts: CommandTexts, path: str) -> tuple[dict[str, str], dict[str, str]]:
    """The localized ``(name, description)`` maps for one command path."""
    return (
        _expand(texts.language_map(f"{path}.name"), NAME_LIMIT),
        _expand(texts.language_map(f"{path}.description")),
    )


def _argument_key(texts: CommandTexts, path: str, name: str) -> str:
    """The catalogue's parameter name for an option name Discord normalised."""
    if not name:
        return name
    if texts.language_map(f"{path}.args.{name}"):
        return name
    lowered = name.lower()
    for parameter in texts.args(path):
        if parameter.lower() == lowered:
            return parameter
    return name


def _localize_options(options: list[dict[str, Any]], texts: CommandTexts, path: str) -> None:
    """Add localizations to a command's options, recursing into subcommands."""
    for option in options:
        name = option.get("name") or ""
        child_path = f"{path}.{name}" if name else path
        if option.get("type") in _COMMAND_OPTION_TYPES:
            _localize_options(option.get("options") or [], texts, child_path)
            names, descriptions = _localizations(texts, child_path)
            english = texts.english(f"{child_path}.description")
            if english:
                option["description"] = _clamp(english)
        else:
            # Arguments are stored under the command's own path, not the option's.
            parameter = _argument_key(texts, path, name)
            names = _expand(texts.language_map(f"{path}.args.{parameter}.name"), NAME_LIMIT)
            values = texts.language_map(f"{path}.args.{parameter}")
            descriptions = _expand(values)
            if values and _is_blank(option.get("description")):
                # No @app_commands.describe() for this option: use the catalogue's
                # English text rather than Discord's empty placeholder.
                option["description"] = _clamp(values.get("en", ""))
        if names:
            option["name_localizations"] = names
        if descriptions:
            option["description_localizations"] = descriptions


def _inject_localizations(payload: dict[str, Any], command: Any, texts: CommandTexts) -> None:
    """Add the catalogue translations to one command's payload in place."""
    path = command_path(command)
    names, descriptions = _localizations(texts, path)

    if isinstance(command, app_commands.ContextMenu):
        # Context menus only carry a name; Discord has no description field.
        if names:
            payload["name_localizations"] = names
        return

    english = texts.english(f"{path}.description")
    if english:
        # Some hybrid subcommands fall back to their ``help`` argument, which is
        # a serialised locale map, so the English catalogue text is authoritative.
        payload["description"] = _clamp(english)
    if names:
        payload["name_localizations"] = names
    if descriptions:
        payload["description_localizations"] = descriptions
    _localize_options(payload.get("options") or [], texts, path)


def _to_dict_wrapper(command: Any, texts: CommandTexts):
    """A ``to_dict`` replacement that adds the catalogue translations."""
    original = command.to_dict

    def to_dict(self: Any, *args: Any) -> dict[str, Any]:
        try:
            payload = original(*args)
        except TypeError:  # ContextMenu.to_dict() has differed between versions
            payload = original()
        _inject_localizations(payload, command, texts)
        return payload

    return to_dict


def apply_command_localizations(tree: app_commands.CommandTree) -> int:
    """Attach the catalogue translations to every application command in ``tree``.

    ``to_dict`` is the payload every caller starts from — ``CommandTree.sync``
    uses it directly when no translator is installed, and the startup fingerprint
    hashes it — so localizing there covers the sync payload and makes a
    translation-only edit look like a tree change. Only top-level commands need
    patching: their payloads nest subcommands and options, which the wrapper
    localizes on the way out.

    Returns how many commands were touched.
    """
    applied = 0
    for command in tree.get_commands():
        if getattr(command, _LOCALIZED_ATTRIBUTE, False):
            continue
        texts = _texts_for(command)
        if texts is None:
            continue
        command.to_dict = MethodType(  # type: ignore[method-assign]
            _to_dict_wrapper(command, texts), command
        )
        setattr(command, _LOCALIZED_ATTRIBUTE, True)
        applied += 1
    return applied
