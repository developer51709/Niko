"""Legal pages are paged so a document fits Discord's message text cap."""

import asyncio
import sys
from pathlib import Path

import discord

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.legal import cog


def _document(key: str) -> str:
    """The text a legal command sends, in the shape ``_send_legal`` builds."""
    return f"### title\n\n{cog.MESSAGES['en'][key]}\n\n-# footer"


def test_every_legal_page_fits_the_message_text_budget():
    for key in ("privacy_body", "terms_body", "community_body"):
        pages = cog._chunks(_document(key))
        assert pages, key
        # Discord counts every component's text against one 4,000 cap, which is
        # what made /legal terms fail before pages were sent one at a time.
        assert all(len(page) <= 4000 for page in pages), key
        # Splitting must not drop or reorder anything. Pages are separate
        # messages, so they are rejoined with the paragraph break the split
        # consumed before comparing whitespace-normalised text.
        assert " ".join("\n\n".join(pages).split()) == " ".join(_document(key).split()), key


def test_the_privacy_policy_and_terms_need_several_pages():
    for key in ("privacy_body", "terms_body"):
        assert len(cog._chunks(_document(key))) > 1, key


def test_the_community_policy_still_fits_in_one_message():
    assert len(cog._chunks(_document("community_body"))) == 1


def _pager(pages: list[str]) -> "cog.LegalPager":
    return cog.LegalPager(pages, 1234, "Previous", "Next", "locked")


def _buttons(view: "cog.LegalPager") -> list[discord.ui.Button]:
    return [item for item in view.walk_children() if isinstance(item, discord.ui.Button)]


def test_a_single_page_sends_no_navigation():
    view = _pager(["one"])
    assert view.nav_buttons == []
    assert _buttons(view) == []
    assert not [item for item in view.walk_children() if isinstance(item, discord.ui.ActionRow)]


def test_pages_get_previous_a_counter_and_next():
    view = _pager(["one", "two", "three"])
    buttons = _buttons(view)

    assert [button.label for button in buttons] == ["Previous", "1/3", "Next"]
    # The counter is informational, and the first page cannot go back.
    assert [button.disabled for button in buttons] == [True, True, False]


class _Response:
    def __init__(self):
        self.edits: list[dict] = []

    async def edit_message(self, **kwargs):
        self.edits.append(kwargs)


class _Interaction:
    def __init__(self, user_id: int):
        self.user = _User(user_id)
        self.response = _Response()


class _User:
    def __init__(self, user_id: int):
        self.id = user_id


class _Message:
    def __init__(self):
        self.edits: list[dict] = []

    async def edit(self, **kwargs):
        self.edits.append(kwargs)


def test_timing_out_suppresses_mentions_too():
    """Greyed-out buttons are an edit like any other page turn."""
    view = _pager(["one", "two"])
    view.message = _Message()
    view.page = 1

    asyncio.run(view.on_timeout())

    edit = view.message.edits[-1]
    assert edit["allowed_mentions"].users is False
    assert all(button.disabled for button in view.nav_buttons)


def test_turning_a_page_suppresses_mentions():
    """The owner credit in the footer must not ping when it first appears."""
    view = _pager(["one", "two"])
    interaction = _Interaction(view.author_id)
    asyncio.run(view._next(interaction))

    edit = interaction.response.edits[-1]
    allowed = edit["allowed_mentions"]
    # Discord notifies on a mention introduced by an edit, so an edit without
    # this would ping the owner as soon as the last page is opened.
    assert allowed.everyone is False
    assert allowed.users is False
    assert allowed.roles is False
