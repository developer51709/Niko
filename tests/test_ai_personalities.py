"""AI personality catalogue and prompt dispatch."""

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import utils.ai.config as ai_config  # noqa: E402
import utils.ai.reply as reply  # noqa: E402
from utils.ai.prompts import (  # noqa: E402
    PERSONALITY_KEYS,
    PERSONALITY_PROMPTS,
    SYSTEM_PROMPT_SUBJECT_DELTA,
)


def test_subject_delta_is_in_the_personality_catalogue():
    assert "subject_delta" in PERSONALITY_KEYS
    assert PERSONALITY_PROMPTS["subject_delta"] is SYSTEM_PROMPT_SUBJECT_DELTA
    assert "Subject Delta" in SYSTEM_PROMPT_SUBJECT_DELTA
    assert "Rapture" in SYSTEM_PROMPT_SUBJECT_DELTA


def test_every_personality_has_a_non_empty_prompt():
    assert set(PERSONALITY_KEYS) == set(PERSONALITY_PROMPTS)
    assert all(prompt.strip() for prompt in PERSONALITY_PROMPTS.values())


def test_stored_subject_delta_personality_is_preserved():
    assert "subject_delta" in ai_config.PERSONALITIES
    assert ai_config._row_to_config({
        "personality": "subject_delta",
    })["personality"] == "subject_delta"


def test_dashboard_config_advertises_the_personality_catalogue():
    from webapp import app
    from webapp.routes import dashboard_routes

    with patch.object(dashboard_routes, "get_runtime_moderation_config", lambda guild_id: {}), \
            patch.object(dashboard_routes, "_get_runtime_server_config", lambda guild_id: {}), \
            patch.object(dashboard_routes, "_guild_premium_view", lambda guild_id: {"active": False}), \
            patch.object(dashboard_routes, "cached_ai_config", lambda guild_id: {"personality": "cafe"}), \
            patch.object(dashboard_routes, "get_runtime_level_config", lambda guild_id: {}):
        with app.test_request_context():
            payload = dashboard_routes.api_guild_config.__wrapped__.__wrapped__("1").get_json()

    assert payload["ai"]["personalities"] == list(ai_config.PERSONALITIES)
    assert "subject_delta" in payload["ai"]["personalities"]


def test_subject_delta_prompt_is_used_for_replies(monkeypatch):
    captured = {}

    async def generate(*args, **kwargs):
        captured["system_prompt"] = args[5]
        return "The city is quiet."

    monkeypatch.setattr(reply, "generate_reply_openai", generate)

    result = asyncio.run(reply.generate_reply(
        None,
        7,
        SimpleNamespace(id=1),
        "Are you there?",
        "tester",
        config={
            "enabled": "True",
            "ai_name": "Niko",
            "personality": "subject_delta",
        },
    ))

    assert result == "The city is quiet."
    assert "You are Subject Delta" in captured["system_prompt"]
    assert "Your configured name in this server is Niko" in captured["system_prompt"]


def test_unknown_personality_falls_back_to_the_cafe_prompt(monkeypatch):
    captured = {}

    async def generate(*args, **kwargs):
        captured["system_prompt"] = args[5]
        return "ok"

    monkeypatch.setattr(reply, "generate_reply_openai", generate)

    asyncio.run(reply.generate_reply(
        None,
        7,
        SimpleNamespace(id=1),
        "hello",
        "tester",
        config={
            "enabled": "True",
            "ai_name": "Niko",
            "personality": "not-real",
        },
    ))

    assert captured["system_prompt"].startswith("you are niko")
