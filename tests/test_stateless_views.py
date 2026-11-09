"""Views answered by a dedicated interaction handler must cost no memory.

discord.py keeps a sent message's view in ``ViewStore._synced_message_views``
for as long as the process runs whenever the view is dispatchable, and a
persistent view has no timeout to release it. Card views that resolve their own
clicks — the roleplay cards and picker through the cog's ``on_interaction``
listener, the avatar and userinfo panels through ``DynamicItem`` patterns — need
no stored view: the interaction arrives with the custom id either way.
"""

import asyncio
import sys
from pathlib import Path

import discord
from discord.ui.view import ViewStore

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.fun import roleplay  # noqa: E402
from cogs.info import _avatars as avatars  # noqa: E402
from utils import stateless_views  # noqa: E402


def _store() -> ViewStore:
    """A view store with no client attached, which is all ``add_view`` needs."""
    store = ViewStore.__new__(ViewStore)
    store._views = {}
    store._synced_message_views = {}
    store._modals = {}
    store._dynamic_items = {}
    return store


def _add(view, message_id: int = 1) -> ViewStore:
    """Register ``view`` the way a send does, and hand the store back."""
    store = _store()

    async def add():
        store.add_view(view, message_id=message_id)

    asyncio.run(add())
    return store


def _button_card() -> discord.ui.LayoutView:
    view = discord.ui.LayoutView(timeout=None)
    view.add_item(discord.ui.Container(discord.ui.ActionRow(
        discord.ui.Button(label="stored", custom_id="plain:button"),
    )))
    return view


# ── the harness itself ────────────────────────────────────────────────────

def test_the_store_would_keep_a_normal_button_view():
    """Guard against the assertions below passing because nothing ever stores."""
    view = _button_card()
    store = _add(view)
    assert store._synced_message_views == {1: view}
    assert 1 in store._views


# ── callback-only items ───────────────────────────────────────────────────

def test_a_callback_only_button_keeps_the_id_discord_routes_on():
    button = stateless_views.CallbackOnlyButton(
        label="Hug back", custom_id=f"{roleplay.BACK_PREFIX}hug")
    assert button.custom_id == f"{roleplay.BACK_PREFIX}hug"
    assert button.is_dispatchable() is False
    # The id is still what goes out with the message.
    assert button.to_component_dict()["custom_id"] == f"{roleplay.BACK_PREFIX}hug"


def test_a_callback_only_view_is_never_registered_by_a_send():
    view = stateless_views.CallbackOnlyLayoutView(timeout=None)
    view.add_item(discord.ui.Container(discord.ui.ActionRow(
        stateless_views.CallbackOnlyButton(label="x", custom_id="x:y"),
    )))
    # Sends only store a view when it reports itself dispatchable.
    assert view.is_dispatchable() is False
    # ...and a direct registration still leaves the store empty.
    store = _add(view)
    assert store._synced_message_views == {}
    assert store._views == {}


# ── roleplay: one card per action, answered by on_interaction ─────────────

def test_the_roleplay_card_costs_no_stored_view():
    view = roleplay.build_roleplay_view(
        title="hug",
        desc="a hugs b",
        gif="https://cdn.example/hug.gif",
        back_action="hug",
        back_label="Hug back",
    )
    assert view.is_dispatchable() is False
    store = _add(view)
    assert store._synced_message_views == {}
    assert store._views == {}


def test_the_roleplay_picker_costs_no_stored_view():
    view = roleplay.build_picker_view(target_id=4242, hint="pick one")
    selects = [item for item in view.walk_children() if isinstance(item, discord.ui.Select)]
    assert [select.custom_id for select in selects] == [f"{roleplay.PICK_PREFIX}4242"]
    assert view.is_dispatchable() is False
    store = _add(view)
    assert store._synced_message_views == {}
    assert store._views == {}


# ── avatar panels: resolved from DynamicItem templates ────────────────────

def _avatar_panel() -> discord.ui.LayoutView:
    view = discord.ui.LayoutView(timeout=None)
    view.add_item(discord.ui.Container(avatars.AvatarButtons(4242)))
    return view


def test_the_avatar_panel_stores_patterns_and_not_messages():
    store = _add(_avatar_panel())
    assert store._synced_message_views == {}
    assert store._views == {}
    # The two custom-id templates are registered once, by class, not per message.
    assert len(store._dynamic_items) == 2


def test_each_avatar_panel_leaves_nothing_behind():
    store = _store()

    async def send_ten():
        for message_id in range(1, 11):
            view = _avatar_panel()
            if view.is_dispatchable():
                store.add_view(view, message_id=message_id)

    asyncio.run(send_ten())
    assert store._synced_message_views == {}
    assert store._views == {}
    assert len(store._dynamic_items) == 2
