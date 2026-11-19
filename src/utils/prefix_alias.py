"""Short prefix twins for grouped commands.

A hybrid group keeps both ways of invoking its subcommands behind the group
name: ``/bank deposit`` is ``.bank deposit`` with a prefix. That nesting exists
only to keep the slash tree inside Discord's 100-command budget, and typing the
group name is friction for members, so a subcommand can also be given a
top-level prefix twin.

:func:`prefix_alias` registers the target's callback a second time as a hidden
prefix command. Because the twin is a plain command and not a hybrid one, the
slash tree does not grow: ``/bank deposit`` keeps its slot, and ``.deposit``
simply answers to the same function with the same parameters and checks.

The twin carries :data:`ALIAS_OF` in its ``extras``, so the places that show
commands can tell a shortcut from a command of its own:

* the public commands page folds the short name into the grouped command's
  aliases instead of adding a second card (``events/startup/writers.py``),
* the help menu keeps it out of the category lists but still answers
  ``.help deposit`` (:func:`hidden_from_lists`, used by ``cogs/help``),
* maintenance maps a pause of the grouped command onto its shortcut and leaves
  the shortcut out of the dashboard's command list (``utils/maintenance``).

Usage, directly after the grouped command is defined::

    @bank.command(name="deposit", description=CMDS.text("bank.deposit.description"))
    async def bank_deposit(self, ctx: commands.Context, amount: str):
        ...

    deposit = prefix_alias(bank_deposit)
"""

from __future__ import annotations

from discord.ext import commands

from utils.command_locales import PATH_OVERRIDE, command_path

#: ``extras`` key holding the qualified name of the command an alias invokes.
ALIAS_OF = "prefix_alias_of"


def prefix_alias(target: commands.Command, *, name: str = None) -> commands.Command:
    """A hidden top-level prefix command that runs *target*.

    The alias shares the target's callback, so ``.deposit 500`` parses and runs
    exactly like ``.bank deposit 500``; the target's checks are copied, and its
    wording is read from the target's catalogue keys
    (:data:`utils.command_locales.PATH_OVERRIDE`), so ``.help deposit`` shows the
    same text as the grouped command.
    """
    attrs = {
        "hidden": True,
        "extras": {
            ALIAS_OF: target.qualified_name,
            PATH_OVERRIDE: command_path(target),
        },
        "checks": list(getattr(target, "checks", ()) or ()),
    }
    for attribute in ("description", "help", "brief"):
        value = getattr(target, attribute, None)
        if value:
            attrs[attribute] = value
    return commands.command(name=name or target.name, **attrs)(target.callback)


def alias_of(command) -> str | None:
    """The qualified name *command* stands in for, or ``None``."""
    extras = getattr(command, "extras", None) or {}
    value = extras.get(ALIAS_OF)
    return str(value) if value else None


def is_prefix_alias(command) -> bool:
    """True when *command* is a shortcut registered by :func:`prefix_alias`."""
    return alias_of(command) is not None


def hidden_from_lists(command) -> bool:
    """True when *command* must stay out of the help's category lists.

    Aliases are hidden so they never read as commands of their own, but
    ``.help deposit`` should still explain the shortcut, so they are exempt from
    the "hidden means unsearchable" rule.
    """
    return bool(getattr(command, "hidden", False)) and not is_prefix_alias(command)


__all__ = [
    "ALIAS_OF",
    "alias_of",
    "hidden_from_lists",
    "is_prefix_alias",
    "prefix_alias",
]
