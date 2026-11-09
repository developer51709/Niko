"""Views whose clicks are resolved from their custom id, not from a stored view.

discord.py keeps a sent message's view in memory for as long as the process
lives whenever that view carries a dispatchable item: ``Messageable.send`` calls
``state.store_view``, and ``ViewStore.add_view`` parks the view — with its
content, its cog and every item it holds, measured at ~2 KB — in
``_synced_message_views``. A ``timeout`` releases it, which a persistent view
does not have, so every card with a button on it pins a view until restart.

Some cards do not need that reference. When a cog resolves the click itself — an
``on_interaction`` listener reading the custom id, or a ``DynamicItem`` rebuilt
from it — Discord delivers the interaction with the custom id either way, so the
stored view is pure overhead. These classes say so:

* the view reports itself as not dispatchable, which keeps ``send()`` and
  ``edit_message()`` from registering it at all;
* the items report themselves as not dispatchable, which keeps the view out of
  the store on the paths that register a view directly (``bot.add_view``).

Only use them where nothing depends on the stored view: no item callbacks and no
per-message state. A view whose buttons run their own ``callback`` has to stay a
normal view — that callback is what the store dispatches to.
"""

from __future__ import annotations

import discord

__all__ = ["CallbackOnlyButton", "CallbackOnlyLayoutView", "CallbackOnlySelect"]


class CallbackOnlyLayoutView(discord.ui.LayoutView):
    """A CV2 layout whose interactive items are answered by a dedicated handler."""

    def is_dispatchable(self) -> bool:
        return False


class CallbackOnlyButton(discord.ui.Button):
    """A button whose custom id is routed to a dedicated handler.

    ``is_dispatchable`` only decides whether discord.py stores and dispatches the
    view; the custom id is still sent to Discord and still comes back in the
    interaction payload.
    """

    def is_dispatchable(self) -> bool:
        return False


class CallbackOnlySelect(discord.ui.Select):
    """A select whose custom id is routed to a dedicated handler."""

    def is_dispatchable(self) -> bool:
        return False
