"""The DEVELOPMENT environment flag selects the beta status rotation.

Run with:  python -m pytest tests/test_status_config.py -v
"""

import importlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import status as status_config  # noqa: E402


class DevelopmentStatusTests(unittest.TestCase):
    def tearDown(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DEVELOPMENT", None)
            importlib.reload(status_config)

    def test_production_keeps_its_rotation_when_development_is_unset(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DEVELOPMENT", None)
            config = importlib.reload(status_config)
        self.assertFalse(config.DEVELOPMENT)
        self.assertTrue(config.STATUS_ROTATE)
        self.assertIn(".help | “hey niko”", config.STATUS_MESSAGES)
        self.assertNotIn("Niko beta | try !help", config.STATUS_MESSAGES)

    def test_development_uses_the_separate_beta_rotation(self):
        with patch.dict(os.environ, {"DEVELOPMENT": "true"}):
            config = importlib.reload(status_config)
        self.assertTrue(config.DEVELOPMENT)
        self.assertTrue(config.STATUS_ROTATE)
        self.assertEqual(config.STATUS_MESSAGE, config.DEVELOPMENT_STATUS_MESSAGES[0])
        self.assertEqual(config.STATUS_MESSAGES, config.DEVELOPMENT_STATUS_MESSAGES)
        self.assertNotEqual(config.STATUS_MESSAGES, config.PRODUCTION_STATUS_MESSAGES)

    def test_false_development_values_leave_production_status_active(self):
        with patch.dict(os.environ, {"DEVELOPMENT": "false"}):
            config = importlib.reload(status_config)
        self.assertFalse(config.DEVELOPMENT)
        self.assertEqual(config.STATUS_MESSAGES, config.PRODUCTION_STATUS_MESSAGES)

    def test_status_message_environment_variable_overrides_rotation_message(self):
        with patch.dict(os.environ, {"DEVELOPMENT": "true", "STATUS_MESSAGE": "Fixed status"}):
            config = importlib.reload(status_config)
        self.assertEqual(config.STATUS_MESSAGE_OVERRIDE, "Fixed status")
        self.assertEqual(config.STATUS_MESSAGE, "Fixed status")
        self.assertEqual(config.STATUS_MESSAGES, config.DEVELOPMENT_STATUS_MESSAGES)

    def test_status_placeholders_still_render(self):
        with patch.dict(os.environ, {"DEVELOPMENT": "1"}):
            config = importlib.reload(status_config)
        from events.startup import status as startup_status

        bot = type("Bot", (), {"guilds": [object(), object(), object()], "shard_count": 1})()
        self.assertEqual(
            startup_status._format_status_text(bot, "beta running in {servers} servers"),
            "beta running in 3 servers",
        )


if __name__ == "__main__":
    unittest.main()
