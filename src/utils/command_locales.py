"""Command wording, kept in each cog's ``locales`` folder.

Every command's help line, short description and argument text lives in the
cog's catalogue under one ``commands`` namespace. Because a catalogue table is
flat, the keys carry the command path plus the kind of text::

    "commands": {
      "slots.help": "play a casino-style 3×3 slot machine 🎰",
      "slots.play.description": "Play a game of slots",
      "slots.play.args.amount": "How many coins to bet",
      "voicemaster.default.limit.help": "Set the default user limit"
    }

The command path is the same path Discord shows (``slots play``), joined with
dots, so a subcommand's entries sit under its parent's prefix.

Cogs read their own table at import time to satisfy the decorators, which only
accept plain strings::

    from utils.command_locales import command_texts
    CMDS = command_texts(__package__)

    @commands.hybrid_command(name="slots", description=CMDS.text("slots.description"),
                             help=CMDS.help("slots"))
    @app_commands.describe(amount=CMDS.arg("slots", "amount"))

``CMDS.help`` serialises the three translations into the ``{ 'en': … }`` map the
help menu already reads, ``CMDS.text`` and ``CMDS.arg`` give Discord the English
wording, and the dashboard registry uses :func:`description_map` and
:func:`argument_maps` to hand the website every language.
"""

from __future__ import annotations

import ast
import json
from typing import Any

from utils.locales import (
    FALLBACK_LANGUAGE,
    SUPPORTED_LANGUAGES,
    available_namespaces,
    load_locales,
)

#: The namespace every cog keeps its command text in.
NAMESPACE = "commands"

HELP_SUFFIX = ".help"
DESCRIPTION_SUFFIX = ".description"
NAME_SUFFIX = ".name"
ARGS_SEGMENT = ".args."


def resolve_package(name: str | None) -> str | None:
    """The nearest package above ``name`` that owns a ``commands`` namespace.

    Modules live in sub-packages (``cogs.economy.commands``) while the
    catalogue sits on the cog (``cogs.economy``), so callers pass their own
    ``__package__`` and get the folder that actually holds the JSON.
    """
    if not name:
        return None
    parts = str(name).split(".")
    for index in range(len(parts), 0, -1):
        candidate = ".".join(parts[:index])
        try:
            namespaces = available_namespaces(candidate)
        except Exception:
            continue
        if NAMESPACE in namespaces:
            return candidate
    return None


class CommandTexts:
    """The ``commands`` table of one cog, with per-language lookups."""

    def __init__(self, package: str | None):
        self.package = package
        if package is None:
            self._tables: dict[str, dict[str, str]] = {lang: {} for lang in SUPPORTED_LANGUAGES}
        else:
            self._tables = load_locales(package, NAMESPACE)

    def english(self, key: str) -> str:
        """The English wording for a flat key, or an empty string."""
        return self._tables[FALLBACK_LANGUAGE].get(key, "")

    def language_map(self, key: str) -> dict[str, str]:
        """``{language: text}`` for a flat key, skipping languages without it."""
        return {
            lang: self._tables[lang][key]
            for lang in SUPPORTED_LANGUAGES
            if self._tables[lang].get(key)
        }

    def text(self, key: str) -> str:
        """English text for a decorator that only takes one string."""
        return self.english(key)

    def help(self, key: str) -> str:
        """A command's help line, serialised for the help menu's map parser."""
        values = self.language_map(f"{key}{HELP_SUFFIX}")
        if not values:
            return ""
        return json.dumps(values, ensure_ascii=False)

    def arg(self, key: str, parameter: str) -> str:
        """English text for one argument of one command."""
        return self.english(f"{key}{ARGS_SEGMENT}{parameter}")

    def args(self, key: str) -> dict[str, dict[str, str]]:
        """``{parameter: {language: text}}`` for one command."""
        prefix = f"{key}{ARGS_SEGMENT}"
        found: dict[str, dict[str, str]] = {}
        for flat_key in self._tables[FALLBACK_LANGUAGE]:
            if not flat_key.startswith(prefix):
                continue
            parameter = flat_key[len(prefix):]
            if not parameter or ARGS_SEGMENT in parameter or parameter.endswith(NAME_SUFFIX):
                continue
            values = self.language_map(flat_key)
            if values:
                found[parameter] = values
        return found


def command_texts(package: str | None) -> CommandTexts:
    """The command table for a package (or module inside it)."""
    return CommandTexts(resolve_package(package))


def help_mapping(value: Any) -> dict[str, str]:
    """Read ``command.help`` back into a ``{language: text}`` map.

    ``CMDS.help`` writes JSON, while older records hold a Python literal such as
    ``"{'en': 'Reset XP.'}"``. Both are parsed as written: rewriting one quote
    style into the other (``json.loads(raw.replace("'", '"'))``) corrupts every
    translation that contains an apostrophe — French ``d'objets`` became
    ``d"objets`` — and the command then showed its raw serialised map.

    Anything that is not such a map comes back as ``{}``.
    """
    if isinstance(value, dict):
        parsed = value
    elif isinstance(value, str) and value.strip().startswith("{"):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                return {}
    else:
        return {}
    if not isinstance(parsed, dict):
        return {}
    return {str(key): str(text) for key, text in parsed.items() if text}


def command_path(command: Any) -> str:
    """``slots play`` for a subcommand, as the catalogue key prefix."""
    names: list[str] = []
    node = command
    while node is not None:
        name = getattr(node, "name", None)
        if name:
            names.append(str(name))
        node = getattr(node, "parent", None)
    return ".".join(reversed(names))


def _texts_for(command: Any) -> CommandTexts | None:
    callback = getattr(command, "callback", None)
    # App command groups carry ``module`` but no callback or binding.
    module = getattr(callback, "__module__", None) or getattr(command, "module", None)
    if not module:
        binding = getattr(command, "binding", None) or getattr(command, "cog", None)
        module = type(binding).__module__ if binding is not None else None
    if not module:
        return None
    texts = CommandTexts(resolve_package(module))
    return texts if texts.package else None


def description_map(command: Any) -> dict[str, str]:
    """Every translation of a command's short description (``{}`` if none)."""
    texts = _texts_for(command)
    if texts is None:
        return {}
    return texts.language_map(f"{command_path(command)}{DESCRIPTION_SUFFIX}")


def help_map(command: Any) -> dict[str, str]:
    """Every translation of a command's help line (``{}`` if none)."""
    texts = _texts_for(command)
    if texts is None:
        return {}
    return texts.language_map(f"{command_path(command)}{HELP_SUFFIX}")


def argument_maps(command: Any) -> dict[str, dict[str, str]]:
    """``{parameter: {language: text}}`` for a command's documented arguments."""
    texts = _texts_for(command)
    if texts is None:
        return {}
    return texts.args(command_path(command))


__all__ = [
    "ARGS_SEGMENT",
    "DESCRIPTION_SUFFIX",
    "HELP_SUFFIX",
    "NAMESPACE",
    "CommandTexts",
    "argument_maps",
    "command_path",
    "command_texts",
    "description_map",
    "help_map",
    "help_mapping",
    "resolve_package",
]
