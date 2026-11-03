"""Owner-controlled maintenance mode for a whole cog or a single command.

The toggles live in the ``maintenance_targets`` table of the bot's database, not
on disk: production runs without a persistent disk, so anything kept outside
MongoDB disappears on the next restart. Rows are read once at startup into a
small in-process cache, so the command gates stay dictionary lookups instead of
a query per invocation.

    target                 reason              since        added_by
    "cog:cogs.music"       "Rewriting the…"    1793          "123"
    "command:ban"          NULL                1793          "123"

A cog entry blocks every command the cog registers, slash, prefix, and the
user/message context menus it adds to the tree. A command entry blocks that
command and anything under it, so maintaining ``ticket`` also stops
``ticket add``. Owners bypass the gate entirely: the person flipping the switch
is usually the one who needs to test the fix.

Blocked users are answered with a Components v2 notice in their guild's language,
carrying the optional reason the owner typed, which the website's /status page
shows too.
"""

from __future__ import annotations

import time

import discord

from config.emojis import get_emoji
from config.ids import OWNER_IDS
from utils import logging
from utils.i18n import make_flat_msg
from utils.locales import load_locales

#: The table both backends understand; see ``events/startup/database.py``.
TABLE = "maintenance_targets"

#: The longest reason the dashboard accepts, in characters.
MAX_REASON = 500

MESSAGES = load_locales("utils.maintenance", "gate")
msg = make_flat_msg(MESSAGES, {"warning": get_emoji("warning")})

#: Public target names and the cache bucket each one belongs to.
_BUCKETS = {"cog": "cogs", "command": "commands"}

_cache: dict | None = None
_loaded = False


def _empty() -> dict:
    return {"cogs": {}, "commands": {}}


def _read() -> dict:
    """The cached toggles. Never touches the database, so gates stay cheap."""
    global _cache
    if _cache is None:
        _cache = _empty()
    return _cache


async def load(bot) -> None:
    """Read every toggle from the database once, at startup."""
    global _cache, _loaded
    _cache = _empty()
    _loaded = True
    pool = getattr(bot, "cxn", None)
    if pool is None:
        logging.warning("Maintenance", "Database unavailable — maintenance state is empty.")
        return
    try:
        rows = await pool.fetch(f"SELECT target, reason, since, added_by FROM {TABLE}")
    except Exception as exc:
        logging.warning("Maintenance", f"Could not read maintenance state: {exc}")
        return
    for row in rows:
        kind, _, key = str(row.get("target") or "").partition(":")
        bucket = _BUCKETS.get(kind)
        if not bucket or not key:
            continue
        _cache[bucket][key] = {
            "reason": row.get("reason") or None,
            "since": row.get("since"),
            "by": row.get("added_by") or None,
        }
    paused = len(_cache["cogs"]) + len(_cache["commands"])
    if paused:
        logging.info("Maintenance", f"{paused} maintenance target(s) loaded from the database.")


async def ensure_loaded(bot) -> None:
    """Load on first use, for a process that never ran the startup path."""
    if not _loaded:
        await load(bot)


def entry(kind: str, key: str) -> dict | None:
    """The cached entry for one cog/command, or ``None`` when it runs normally."""
    bucket = _read().get(_BUCKETS.get(kind, kind)) or {}
    return bucket.get(key) or None


async def set_maintenance(kind: str, key: str, enabled: bool, reason: str = "", actor=None, bot=None) -> dict | None:
    """Pause or resume one cog/command, in the database and the cache.

    The row is written first: if the database rejects the change the cache is
    left alone, so the dashboard never reports a pause that would vanish on the
    next restart.
    """
    if kind not in _BUCKETS:
        raise ValueError("Maintenance applies to a cog or a command.")
    pool = getattr(bot, "cxn", None)
    if pool is None:
        raise RuntimeError("The database is not available.")

    target = f"{kind}:{key}"
    bucket = _read()[_BUCKETS[kind]]

    if not enabled:
        await pool.execute(f"DELETE FROM {TABLE} WHERE target = $1", target)
        bucket.pop(key, None)
        return None

    cleaned = (reason or "").strip()[:MAX_REASON] or None
    since = int(time.time())
    added_by = str(actor) if actor is not None else None
    await pool.execute(
        f"INSERT INTO {TABLE} (target, reason, since, added_by) VALUES ($1, $2, $3, $4) "
        "ON CONFLICT (target) DO UPDATE SET reason = $5, since = $6, added_by = $7",
        target, cleaned, since, added_by, cleaned, since, added_by,
    )
    record = {"reason": cleaned, "since": since, "by": added_by}
    bucket[key] = record
    return dict(record)


# ──────────────────────────────────────────────────────────────────────────────
# Lookups
# ──────────────────────────────────────────────────────────────────────────────
def extension_of(module: str | None) -> str | None:
    """``cogs.music.cog`` → ``cogs.music``.

    A cog class lives in one of the extension's modules, and the loader records
    the extension itself, so the first two dotted parts are the key both sides
    agree on.
    """
    if not module or not module.startswith("cogs."):
        return None
    return ".".join(module.split(".")[:2])


def _module_of(cog) -> str | None:
    return getattr(cog.__class__, "__module__", None) if cog is not None else None


def find_block(command_name: str | None, cog=None, extension: str | None = None) -> tuple[str, str, dict] | None:
    """The maintenance entry that blocks this command, if any.

    Command entries are checked longest-first (``ticket add`` before ``ticket``)
    so the message names the narrowest thing the owner paused, then the cog is
    checked — a paused cog takes its whole command set with it. ``extension`` is
    for callers that already resolved the owning extension, which is the only
    way a context menu can be attributed to its cog.
    """
    store = _read()
    parts = [part for part in str(command_name or "").split() if part]
    for size in range(len(parts), 0, -1):
        key = " ".join(parts[:size])
        found = store["commands"].get(key)
        if found is not None:
            return "command", key, dict(found)

    resolved = extension or extension_of(_module_of(cog))
    found = store["cogs"].get(resolved) if resolved else None
    if found is not None:
        return "cog", resolved, dict(found)
    return None


def _prefix_command(bot, qualified_name: str | None):
    """Resolve ``"ticket category"`` through the prefix command tree."""
    parts = [part for part in str(qualified_name or "").split() if part]
    if not parts:
        return None
    command = bot.get_command(parts[0])
    for part in parts[1:]:
        lookup = getattr(command, "get_command", None)
        command = lookup(part) if lookup else None
        if command is None:
            return None
    return command


def _deepest_prefix_command(bot, words: list[str]):
    """The deepest command ``!ticket category add …`` actually invokes.

    Walking one word at a time is what lets a pause on ``ticket category`` stop
    the prefix spelling as well as the slash one: resolving only ``ticket``
    would answer for the group and skip the narrower command the owner paused.
    """
    if not words:
        return None
    command = bot.get_command(words[0])
    for word in words[1:]:
        lookup = getattr(command, "get_command", None) if command is not None else None
        child = lookup(word) if lookup else None
        if child is None:
            break
        command = child
    return command


def extension_for_command(bot, command, binding=None) -> str | None:
    """The extension that owns an application command, context menus included.

    Slash commands carry their cog as ``binding``. Hybrid groups are built
    lazily and do not, so the prefix twin is asked instead. Context menus are
    added to the tree by hand from a cog's ``__init__``: they have no binding and
    no prefix twin at all, but their callback still lives in the cog's module,
    which names the extension — the case a paused cog used to miss.
    """
    extension = extension_of(_module_of(binding))
    if extension:
        return extension
    extension = extension_of(getattr(getattr(command, "callback", None), "__module__", None))
    if extension:
        return extension
    # A Group has neither a callback nor a binding of its own — only its
    # children are real commands bound to the owning cog, so ask them.
    children = getattr(command, "commands", None) or ()
    if hasattr(children, "values"):
        children = children.values()
    for child in children:
        extension = extension_for_command(bot, child, getattr(child, "binding", None))
        if extension:
            return extension
    qualified = getattr(command, "qualified_name", None) or getattr(command, "name", None)
    prefix = _prefix_command(bot, qualified) if bot is not None else None
    return extension_of(_module_of(getattr(prefix, "cog", None)))


def cog_for_command(bot, qualified_name: str | None, binding=None, command=None):
    """The cog that owns an application command.

    Hybrid groups (``/ticket``, ``/ticket category``) are built lazily by
    discord.py and carry no ``binding``; only their leaf commands do. The prefix
    side of the same hybrid tree does know its cog, so a missing binding is
    resolved through it. Without this, a paused cog kept answering on the group
    commands — and the dashboard filed them under "no cog".
    """
    if binding is not None and extension_of(_module_of(binding)):
        return binding
    if command is not None:
        resolved = extension_for_command(bot, command, binding)
        found = _cog_for(bot, resolved) if resolved else None
        if found is not None:
            return found
    prefix = _prefix_command(bot, qualified_name) if bot is not None else None
    return getattr(prefix, "cog", None) if prefix is not None else binding


def is_owner(user_id) -> bool:
    try:
        return int(user_id) in OWNER_IDS
    except (TypeError, ValueError):
        return False


def _cog_label(bot, extension: str | None) -> str:
    """The label the status page uses, so both pages name a cog the same way."""
    for row in getattr(bot, "cog_status", None) or []:
        if row.get("name") == extension:
            return row.get("label") or extension
    if not extension:
        return "This feature"
    name = extension.rsplit(".", 1)[-1]
    return name.replace("_", " ").title()


# ──────────────────────────────────────────────────────────────────────────────
# The notice
# ──────────────────────────────────────────────────────────────────────────────
def notice(source, target: str, reason: str | None) -> discord.ui.LayoutView:
    """The user-facing maintenance card, in their guild's language."""
    lines = [
        discord.ui.TextDisplay(content=msg(source, "title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(source, "body", target=target)),
    ]
    if reason:
        lines.append(discord.ui.TextDisplay(content=msg(source, "reason", reason=reason)))
    lines.append(discord.ui.TextDisplay(content=msg(source, "cta")))

    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(*lines, accent_colour=discord.Color.orange()))
    return view


def _target_text(source, kind: str, key: str, bot) -> str:
    if kind == "cog":
        return msg(source, "cog_target", name=_cog_label(bot, key))
    return msg(source, "command_target", command=key)


# ──────────────────────────────────────────────────────────────────────────────
# Gates
# ──────────────────────────────────────────────────────────────────────────────
async def check_interaction(interaction: discord.Interaction) -> bool:
    """Return False (and answer) when the invoked command is in maintenance.

    Attached next to the blacklist gate in ``bot.py``, which is the one place
    every slash and context-menu invocation passes through.
    """
    if interaction.command is None:
        return True
    if is_owner(getattr(interaction.user, "id", None)):
        return True
    bot = getattr(interaction, "client", None)
    await ensure_loaded(bot)
    qualified = getattr(interaction.command, "qualified_name", None) or getattr(interaction.command, "name", "")
    binding = getattr(interaction.command, "binding", None)
    blocked = find_block(
        qualified,
        cog_for_command(bot, qualified, binding, interaction.command),
        extension_for_command(bot, interaction.command, binding),
    )
    if blocked is None:
        return True
    kind, key, found = blocked
    view = notice(interaction, _target_text(interaction, kind, key, bot), found.get("reason"))
    try:
        await interaction.response.send_message(view=view, ephemeral=True)
    except discord.HTTPException:
        try:
            await interaction.followup.send(view=view, ephemeral=True)
        except discord.HTTPException:
            pass
    return False


async def check_feature(bot, message: discord.Message, extension: str) -> bool:
    """True when a whole cog is paused (already answered).

    Some cogs have entry points that never reach a command — the AI answers a
    name, a ping, or a reply — so those paths ask about the cog directly instead
    of going through :func:`check_message`.
    """
    if is_owner(getattr(message.author, "id", None)):
        return False
    await ensure_loaded(bot)
    found = _read()["cogs"].get(extension)
    if found is None:
        return False
    view = notice(message, _target_text(message, "cog", extension, bot), found.get("reason"))
    try:
        await message.reply(view=view)
    except discord.HTTPException:
        pass
    return True


async def check_message(bot, message: discord.Message, prefix: str) -> bool:
    """True when a prefix command was held in maintenance (already answered).

    Called from ``events.on_message`` before ``bot.process_commands``, so a
    paused command never reaches its own checks, cooldowns, or usage analytics.
    """
    if is_owner(getattr(message.author, "id", None)):
        return False
    # Slice by the matched prefix's length rather than comparing text: prefixes
    # are matched case-insensitively upstream, so `N!ban` and `n!ban` both land here.
    content = message.content[len(prefix):].strip()
    if not content:
        return False
    command = _deepest_prefix_command(bot, content.split())
    if command is None:
        return False
    await ensure_loaded(bot)
    blocked = find_block(command.qualified_name, getattr(command, "cog", None))
    if blocked is None:
        return False
    kind, key, found = blocked
    view = notice(message, _target_text(message, kind, key, bot), found.get("reason"))
    try:
        await message.reply(view=view)
    except discord.HTTPException:
        # Already answered counts as blocked: never let the command run.
        pass
    return True


# ──────────────────────────────────────────────────────────────────────────────
# Cog status
# ──────────────────────────────────────────────────────────────────────────────
def apply_to_cog_status(bot) -> None:
    """Re-mark the live cog rows after a toggle, for the status API and page.

    Rows the code itself declares (``MAINTENANCE = True`` / ``DNL = True``) are
    left alone: a dashboard switch cannot override a constant in the source, and
    pretending otherwise would flip back on the next restart.
    """
    store = _read()
    for row in getattr(bot, "cog_status", None) or []:
        if row.get("declared"):
            continue
        if row.get("state") == "failed":
            continue
        found = store["cogs"].get(row.get("name"))
        if found is not None:
            row["state"] = "maintenance"
            row["reason"] = found.get("reason") or None
        elif row.get("state") == "maintenance":
            row["state"] = "loaded"
            row["reason"] = None


# ──────────────────────────────────────────────────────────────────────────────
# Snapshot for the dashboard
# ──────────────────────────────────────────────────────────────────────────────
def _cog_for(bot, extension: str | None):
    for cog in getattr(bot, "cogs", {}).values():
        if extension_of(_module_of(cog)) == extension:
            return cog
    return None


def _command_rows(bot) -> list[dict]:
    """Every command the bot exposes, prefix and application, one row each."""
    labels = {
        row.get("name"): row.get("label")
        for row in getattr(bot, "cog_status", None) or []
    }
    rows: dict[str, dict] = {}

    def add(name: str, extension: str | None) -> None:
        if not name or name in rows:
            return
        rows[name] = {
            "name": name,
            "cog": extension,
            "cog_label": (labels.get(extension) or _cog_label(bot, extension)) if extension else None,
        }

    def add_prefix(command, parent_extension: str | None) -> None:
        """Prefix commands, including group subcommands, which the app tree alone
        cannot place when the app object has no binding."""
        extension = extension_of(_module_of(getattr(command, "cog", None))) or parent_extension
        add(getattr(command, "qualified_name", None) or getattr(command, "name", ""), extension)
        for child in getattr(command, "commands", ()) or ():
            add_prefix(child, extension)

    for command in getattr(bot, "commands", ()) or ():
        add_prefix(command, None)
    tree = getattr(bot, "tree", None)
    if tree is not None:
        for command in tree.walk_commands():
            name = getattr(command, "qualified_name", None) or getattr(command, "name", "")
            add(name, extension_for_command(bot, command, getattr(command, "binding", None)))

    for row in rows.values():
        found = find_block(row["name"], extension=row["cog"])
        row["maintenance"] = found is not None
        row["blocked_by"] = found[1] if found else None
        row["reason"] = found[2].get("reason") if found else None
        row["since"] = found[2].get("since") if found else None
        row["by"] = found[2].get("by") if found else None
    return sorted(rows.values(), key=lambda row: (row["cog"] or "zzz", row["name"]))


def snapshot(bot) -> dict:
    """Cogs and commands with their current maintenance state (cache only)."""
    store = _read()
    cogs = []
    for row in getattr(bot, "cog_status", None) or []:
        name = row.get("name")
        found = store["cogs"].get(name)
        cogs.append({
            "name": name,
            "label": row.get("label") or _cog_label(bot, name),
            "state": row.get("state"),
            "reason": (found.get("reason") if found else None) or (row.get("reason") if row.get("state") == "maintenance" else None),
            "declared": bool(row.get("declared")),
            "commands": row.get("commands", 0),
            "maintenance": found is not None,
            "since": found.get("since") if found else None,
            "by": found.get("by") if found else None,
        })
    return {
        "cogs": cogs,
        "commands": _command_rows(bot),
        "updated_at": int(time.time()),
    }
