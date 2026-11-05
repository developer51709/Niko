"""Presence: when Discord draws the phone icon instead of the round dot.

The bot's /userinfo card and every website avatar read the same rule, so it is
pinned once here rather than by each surface's markup.

Run with:  python -m pytest tests/test_presence.py -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.presence import is_mobile_presence, status_name  # noqa: E402


class FakeMember:
    """Just the client statuses discord.py caches on a member."""

    def __init__(self, mobile="offline", desktop="offline", web="offline"):
        self.mobile_status = mobile
        self.desktop_status = desktop
        self.web_status = web


class PresenceStatusCodeTests(unittest.TestCase):
    def test_enum_strings_and_plain_words_normalise(self):
        for value, expected in (
            ("Status.online", "online"),
            ("online", "online"),
            ("DND", "dnd"),
            (None, "offline"),
            ("", "offline"),
        ):
            with self.subTest(value=value):
                self.assertEqual(status_name(value), expected)

    def test_enum_objects_use_their_name(self):
        class FakeStatus:
            name = "idle"

        self.assertEqual(status_name(FakeStatus()), "idle")


class MobilePresenceTests(unittest.TestCase):
    def test_the_phone_alone_is_mobile(self):
        self.assertTrue(is_mobile_presence(FakeMember(mobile="online")))
        self.assertTrue(is_mobile_presence(FakeMember(mobile="idle")))
        self.assertTrue(is_mobile_presence(FakeMember(mobile="dnd")))

    def test_an_active_desktop_or_web_session_keeps_the_round_dot(self):
        self.assertFalse(is_mobile_presence(FakeMember(mobile="online", desktop="online")))
        self.assertFalse(is_mobile_presence(FakeMember(mobile="idle", web="online")))

    def test_an_offline_phone_is_never_mobile(self):
        self.assertFalse(is_mobile_presence(FakeMember(mobile="offline", desktop="offline")))

    def test_a_missing_presence_is_not_mobile(self):
        self.assertFalse(is_mobile_presence(None))
        self.assertFalse(is_mobile_presence(object()))


if __name__ == "__main__":
    unittest.main()
