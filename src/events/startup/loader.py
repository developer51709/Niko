"""
Startup — cog loader.
Discovers and loads every cog under src/cogs/.

Every cog's outcome is recorded on ``bot.cog_status`` so the website's /status
page can say not just which cogs are loaded but why a missing one is missing:

    loaded       the extension loaded
    maintenance  the module declares ``MAINTENANCE = True``
    disabled     the module declares ``DNL = True`` (do not load)
    failed       importing or loading raised

A module can announce either state without touching this loader:

    MAINTENANCE = True
    MAINTENANCE_REASON = "Rewriting the queue; back on Friday."

``DNL_REASON`` is the older spelling of the same thing for ``DNL``. The record
is a list, not a dict keyed by module, so the page can render it in the order
the cogs were discovered.
"""

import os
import importlib

from utils import logging, maintenance


#: Names title-casing gets wrong, spelled the way the product spells them.
_LABELS = {
    "ai": "AI",
    "voicemaster": "VoiceMaster",
    "uwulock": "UwU Lock",
    "topgg": "top.gg",
    "pfps": "PFPs",
    "nsfw": "NSFW",
}


def _cog_label(module_name: str) -> str:
    """``cogs.music`` → ``Music``, so the status page reads like a list of names."""
    name = module_name.rsplit(".", 1)[-1]
    if name in _LABELS:
        return _LABELS[name]
    return name.replace("_", " ").title()


def _declare(bot, module_name: str, state: str, reason: str = None, declared: bool = False) -> None:
    """Record one cog's outcome.

    ``declared`` marks a state the module itself asked for (``MAINTENANCE`` or
    ``DNL``). The dashboard can pause and resume a cog, but it must not pretend
    it can override a constant in the source, so those rows stay read-only.
    """
    bot.cog_status.append({
        "name": module_name,
        "label": _cog_label(module_name),
        "state": state,
        "reason": reason or None,
        "commands": 0,
        "declared": declared,
    })


def _cog_of(bot, module_name: str):
    """The loaded cog whose class lives in this module.

    A cog's class name (``MusicSystem``) rarely matches its module
    (``cogs.music``), so the extension is found by module instead of by name.
    """
    for cog in bot.cogs.values():
        module = getattr(cog.__class__, "__module__", "")
        if module == module_name or module.startswith(f"{module_name}."):
            return cog
    return None


def _count_commands(bot, module_name: str) -> int:
    """How many commands this cog registered, for the loaded rows.

    Hybrid commands are registered as both a prefix and an application command,
    so the names are collected in a set to count each one once.
    """
    cog = _cog_of(bot, module_name)
    if cog is None:
        return 0
    names = set()
    try:
        for command in bot.commands:
            if getattr(command, "cog", None) is cog:
                names.add(command.qualified_name)
        for command in bot.tree.walk_commands():
            if getattr(command, "binding", None) is cog:
                names.add(getattr(command, "qualified_name", command.name))
    except Exception:
        pass
    return len(names)


async def load_cogs(bot):
    logging.info("Startup", "Loading cogs...")
    bot.cog_status: list[dict] = []
    # The owner's pauses come from the database, so a cog the dashboard paused is
    # recorded as maintained (its commands still load and answer with the notice).
    await maintenance.load(bot)
    # The status panel's card toggles are read before any panel can be posted, so
    # the first render already matches the dashboard's switches. The module is
    # imported here rather than at the top of the file because an update applies
    # one area at a time: this loader ships with the bot core, and the module it
    # reads ships with the utilities — a bot-core update must still start on a
    # deployment that has not taken the utilities area yet (the panel then loads
    # the flag itself on its first refresh).
    try:
        from utils import panel_settings

        await panel_settings.load(bot)
    except Exception as exc:
        logging.warning("Panel", f"Panel display settings not loaded: {exc}")

    for item in os.listdir("./src/cogs"):
        item_path = os.path.join("./src/cogs", item)

        if os.path.isfile(item_path) and item.endswith(".py") and item != "__init__.py":
            module_name = f"cogs.{item[:-3]}"
        elif os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "__init__.py")):
            module_name = f"cogs.{item}"
        else:
            continue

        try:
            module = importlib.import_module(module_name)

            if getattr(module, "MAINTENANCE", False):
                reason = getattr(module, "MAINTENANCE_REASON", "Under maintenance")
                logging.warning("Startup", f"Skipped cog: {module_name} (maintenance — {reason})")
                _declare(bot, module_name, "maintenance", reason, declared=True)
                continue

            if getattr(module, "DNL", False):
                reason = getattr(module, "DNL_REASON", "No reason provided")
                logging.warning("Startup", f"Skipped cog: {module_name} ({reason})")
                _declare(bot, module_name, "disabled", reason, declared=True)
                continue

            await bot.load_extension(module_name)
            # A cog the owner paused in the dashboard keeps its commands
            # registered so they still answer with the maintenance notice; only
            # the recorded state changes.
            paused = maintenance.entry("cog", module_name)
            _declare(bot, module_name, "maintenance" if paused else "loaded", (paused or {}).get("reason"))
            bot.cog_status[-1]["commands"] = _count_commands(bot, module_name)
            if paused:
                logging.warning("Startup", f"Loaded cog: {module_name} (maintenance — {(paused or {}).get('reason') or 'no reason given'})")
            else:
                logging.success("Startup", f"Loaded cog: {module_name}")

        except Exception as e:
            logging.error("Startup", f"Failed to load cog {module_name}: {e}")
            _declare(bot, module_name, "failed", f"{type(e).__name__}: {e}")
