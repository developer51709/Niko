"""The giveaway panels and replies use Niko's own emoji, never a unicode glyph.

Every text the giveaway feature sends is one of three things: a translated
string in ``MESSAGES``, a Components v2 panel, or a command reply. The panel
buttons were the last place still drawing default emoji (🛑 ⏳ 🏆 👥 🗑 ⌛), and
the translated strings can only carry an emoji as a ``{token}`` that ``msg``
resolves, since each language keeps its own copy of the sentence.

Run with:  python3 -m pytest tests/test_giveaway_emoji.py -v
"""

import re
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import discord  # noqa: E402

from cogs.giveaway.views import (  # noqa: E402
    MESSAGES,
    _build_manage_panel,
    _build_setup_view,
    _SetupState,
    msg,
)
from config.emojis import get_emoji  # noqa: E402

#: Emoji, dingbats, arrows and the variation selector — anything a person would
#: read as a glyph rather than punctuation.
UNICODE_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\u2190-\u21FF\u2300-\u23FF\uFE0F]"
)


def _buttons(view) -> dict:
    return {
        child.label: child
        for child in view.walk_children()
        if isinstance(child, discord.ui.Button) and child.label
    }


def _en() -> SimpleNamespace:
    return SimpleNamespace(guild=SimpleNamespace(preferred_locale="en-US"))


class GiveawayEmojiTests(unittest.TestCase):
    def test_no_translated_message_still_carries_a_unicode_emoji(self):
        for lang, table in MESSAGES["normal"].items():
            for key, text in table.items():
                self.assertIsNone(
                    UNICODE_EMOJI.search(text),
                    f"{lang}/{key} still carries a default emoji: {text}",
                )

    def test_messages_render_their_emoji_tokens(self):
        cases = {
            "end_confirmed": "tick",
            "join_already": "tick",
            "reroll_not_ended": "cross",
            "no_perm_manage": "cross",
            "join_success": "giveaway",
            "winner_announce": "giveaway",
            "manage_title": "settings",
            "select_result": "gambling",
            "participants_title": "participants",
            "no_participants_msg": "sad",
        }
        for key, emoji_name in cases.items():
            with self.subTest(key=key):
                self.assertIn(get_emoji(emoji_name), msg(_en(), key))

    def test_no_token_is_left_unrendered(self):
        """Every language resolves its tokens, not just English."""

        for lang in ("en", "de", "es"):
            ctx = SimpleNamespace(guild=SimpleNamespace(preferred_locale=f"{lang}-{'DE' if lang == 'de' else 'ES'}"))
            for key in MESSAGES["normal"][lang]:
                with self.subTest(lang=lang, key=key):
                    rendered = msg(ctx, key, prize="p", mentions="m", url="u", mention="m",
                                   user="u", count=1, command="c", s="s")
                    self.assertNotIn("{", rendered, rendered)

    def test_the_manage_panel_buttons_use_custom_emojis(self):
        row = {
            "message_id": 1000,
            "channel_id": 500,
            "guild_id": 111,
            "prize": "Nitro",
            "winners_count": 1,
            "host_id": 900,
        }
        buttons = _buttons(_build_manage_panel(None, row))

        self.assertEqual(str(buttons["End Giveaway"].emoji), get_emoji("stop"))
        self.assertEqual(str(buttons["Participants"].emoji), get_emoji("participants"))
        self.assertEqual(str(buttons["Select Random"].emoji), get_emoji("gambling"))

    def test_the_setup_panel_buttons_use_custom_emojis(self):
        view = _build_setup_view(None, _en(), _SetupState(channel_id=500), host_id=900)
        buttons = _buttons(view)

        self.assertEqual(str(buttons["Duration"].emoji), get_emoji("duration"))
        self.assertEqual(str(buttons["Winners"].emoji), get_emoji("trophy"))
        self.assertEqual(str(buttons["Prize"].emoji), get_emoji("gift"))


if __name__ == "__main__":
    unittest.main()
