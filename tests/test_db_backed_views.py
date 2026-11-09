"""Giveaway, poll and suggestion buttons are answered from their custom ids.

These cards used to be registered as a persistent view per message with
``bot.add_view(view, message_id=...)``: one view (and the interaction it pinned)
stayed in memory for every giveaway ever run, every open poll and every open
suggestion, and a startup pass re-registered them all after a restart. The id
needed to answer a click is already in the custom id, and the handler reads the
row from the database, so none of it has to be stored or registered.
"""

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

import discord
from discord.ui.view import ViewStore

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.giveaway import views as giveaway_views  # noqa: E402
from cogs.social import polls as polls_module  # noqa: E402
from cogs.social import suggestions as suggestions_module  # noqa: E402


def _store() -> ViewStore:
    store = ViewStore.__new__(ViewStore)
    store._views = {}
    store._synced_message_views = {}
    store._modals = {}
    store._dynamic_items = {}
    return store


def _stored(view, message_id: int = 1) -> ViewStore:
    store = _store()

    async def register():
        store.add_view(view, message_id=message_id)

    asyncio.run(register())
    return store


def _component(custom_id: str) -> SimpleNamespace:
    return SimpleNamespace(
        type=discord.InteractionType.component,
        data={"custom_id": custom_id},
    )


# ── the cards cost no memory ─────────────────────────────────────────────

def test_a_giveaway_card_is_never_stored():
    view = giveaway_views._build_active_view(
        900001, "Nitro", 1900000000, 1, "<@1>",
    )
    ids = [item.custom_id for item in view.walk_children() if hasattr(item, "custom_id")]
    assert ids == ["giveaway_join_900001", "giveaway_manage_900001"]
    assert view.is_dispatchable() is False
    store = _stored(view)
    assert store._synced_message_views == {}
    assert store._views == {}


def test_a_poll_card_is_never_stored():
    view = discord.ui.LayoutView(timeout=None)
    view.add_item(discord.ui.Container(discord.ui.ActionRow(
        polls_module.PollVoteButton(555, 0),
        polls_module.PollVoteButton(555, 1),
    )))
    ids = [item.custom_id for item in view.walk_children() if hasattr(item, "custom_id")]
    assert ids == ["poll_vote_555_0", "poll_vote_555_1"]
    assert view.is_dispatchable() is False
    store = _stored(view)
    assert store._synced_message_views == {}


def test_a_suggestion_card_is_never_stored():
    suggestion = {
        "id": 7, "text": "add a cat command", "author_id": 42,
        "status": "open", "up": 0, "down": 0, "verdict": None,
    }
    view = suggestions_module._build_view(suggestion, None)
    ids = [item.custom_id for item in view.walk_children() if hasattr(item, "custom_id")]
    assert ids == ["sug_up:7", "sug_down:7"]
    store = _stored(view)
    assert store._synced_message_views == {}


# ── the click reaches the right handler with the right id ────────────────

def test_a_giveaway_click_is_routed_by_its_custom_id(monkeypatch):
    seen = []

    async def join(interaction, message_id=None):
        seen.append(("join", message_id))

    async def manage(interaction, message_id=None):
        seen.append(("manage", message_id))

    monkeypatch.setattr(giveaway_views, "join_giveaway", join)
    monkeypatch.setattr(giveaway_views, "open_manage_panel", manage)

    assert asyncio.run(giveaway_views.handle_component(_component("giveaway_join_42"))) is True
    assert asyncio.run(giveaway_views.handle_component(_component("giveaway_manage_42"))) is True
    assert asyncio.run(giveaway_views.handle_component(_component("poll_vote_1_0"))) is False
    assert seen == [("join", 42), ("manage", 42)]


def test_a_poll_click_is_routed_by_its_custom_id(monkeypatch):
    seen = []

    async def vote(interaction, poll_id, idx):
        seen.append((poll_id, idx))

    monkeypatch.setattr(polls_module, "cast_vote", vote)

    assert asyncio.run(polls_module.handle_component(_component("poll_vote_555_2"))) is True
    assert asyncio.run(polls_module.handle_component(_component("giveaway_join_1"))) is False
    # A malformed id is claimed but goes nowhere.
    assert asyncio.run(polls_module.handle_component(_component("poll_vote_garbage"))) is True
    assert seen == [(555, 2)]


def test_a_suggestion_click_is_routed_by_its_custom_id():
    cog = suggestions_module.Suggestions.__new__(suggestions_module.Suggestions)
    seen = []

    async def handle_vote(interaction, sid, direction):
        seen.append((sid, direction))

    cog.handle_vote = handle_vote
    asyncio.run(cog.on_interaction(_component("sug_up:12")))
    asyncio.run(cog.on_interaction(_component("sug_down:13")))
    asyncio.run(cog.on_interaction(_component("something_else")))
    assert seen == [(12, 1), (13, -1)]


# ── nothing is registered any more ───────────────────────────────────────

def test_no_giveaway_poll_or_suggestion_view_is_registered():
    for module in (giveaway_views, polls_module, suggestions_module):
        source = Path(module.__file__).read_text(encoding="utf-8")
        assert "add_view(" not in source, module.__name__

    giveaway_cog = Path(giveaway_views.__file__).with_name("cog.py").read_text(encoding="utf-8")
    assert "register_persistent_views" not in giveaway_cog
