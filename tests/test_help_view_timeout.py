"""The help card must look expired once its view stops listening.

Discord keeps a timed-out view's buttons and dropdown on screen, but every click
on them fails, so the card looks usable forever. ``HelpView`` disables its
components when it times out, which is the only visible signal a member gets.
"""

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import discord  # noqa: E402

from cogs.help.views import HelpView, _make_layout  # noqa: E402


class FakeMessage:
    def __init__(self):
        self.id = 1000
        self.edits = []

    async def edit(self, *, view=None, **kwargs):
        self.edits.append(view)


class FakeResponse:
    def __init__(self):
        self.edited = []

    async def edit_message(self, *, view=None, **kwargs):
        self.edited.append(view)


class FakeInteraction:
    def __init__(self):
        self.message = FakeMessage()
        self.response = FakeResponse()
        self.guild = SimpleNamespace(preferred_locale="en-US")
        self.guild_id = 1


def components(view):
    return [
        child for child in view.walk_children()
        if isinstance(child, (discord.ui.Button, discord.ui.Select))
    ]


def test_the_general_help_card_is_a_help_view():
    view = _make_layout(None, "Help", "en", include_dropdown=True, general_page=False)

    assert isinstance(view, HelpView)
    assert view.timeout == HelpView.TIMEOUT
    # The dropdown is live while the view is listening.
    assert len(components(view)) == 1
    assert components(view)[0].disabled is False


def test_timing_out_disables_the_dropdown_and_redraws_the_card():
    async def scenario():
        view = _make_layout(None, "Help", "en", include_dropdown=True, general_page=False)
        view.message = FakeMessage()

        await view.on_timeout()
        return view

    view = asyncio.run(scenario())

    selects = [c for c in components(view) if isinstance(c, discord.ui.Select)]
    assert selects and all(select.disabled for select in selects)
    # The disabled card is pushed to Discord, otherwise nothing changes on screen.
    assert view.message.edits == [view]


def test_timing_out_disables_pagination_buttons_too():
    async def scenario():
        view = HelpView()
        container = discord.ui.Container(
            discord.ui.ActionRow(
                discord.ui.Button(label="Prev", style=discord.ButtonStyle.secondary),
                discord.ui.Button(label="Page 1/3", style=discord.ButtonStyle.secondary, disabled=True),
                discord.ui.Button(label="Next", style=discord.ButtonStyle.secondary),
            ),
            discord.ui.ActionRow(discord.ui.Select(
                placeholder="Category",
                options=[discord.SelectOption(label="Moderation")],
            )),
        )
        view.add_item(container)
        view.message = FakeMessage()

        await view.on_timeout()
        return view

    view = asyncio.run(scenario())

    buttons = [c for c in components(view) if isinstance(c, discord.ui.Button)]
    assert [button.disabled for button in buttons] == [True, True, True]


def test_a_card_without_components_does_not_edit_its_message():
    async def scenario():
        view = _make_layout(None, "Detail", "en", include_dropdown=False)
        view.message = FakeMessage()

        await view.on_timeout()
        return view

    view = asyncio.run(scenario())

    assert components(view) == []
    assert view.message.edits == []


def test_swapping_the_card_retires_the_old_timer():
    """A replaced card must not re-render its stale page minutes later."""

    async def scenario():
        view = _make_layout(None, "Help", "en", include_dropdown=True, general_page=False)
        view.message = FakeMessage()
        dropdown = components(view)[0]
        interaction = FakeInteraction()

        replacement = _make_layout(
            None, "Help", "en", include_dropdown=True, general_page=False,
        )
        await dropdown._show(interaction, replacement)
        return view, replacement, interaction

    view, replacement, interaction = asyncio.run(scenario())

    # The new card owns the message and can still expire visibly.
    assert replacement.message is interaction.message
    # The old view cannot fire its timeout over the new page.
    task = view._BaseView__timeout_task
    assert task is None or task.done() or task.cancelled()
    assert interaction.response.edited == [replacement]
