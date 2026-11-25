"""Legal pages are paged so a document fits Discord's message text cap."""

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
