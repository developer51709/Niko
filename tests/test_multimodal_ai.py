"""Regression checks for opt-in image and voice AI context."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_multimodal_experiment_is_opt_in_and_visible_in_config():
    config = (ROOT / "src/utils/ai/config.py").read_text(encoding="utf-8")
    panel = (ROOT / "src/cogs/ai/config.py").read_text(encoding="utf-8")
    assert '"multimodal_experiment": "False"' in config
    assert 'ExperimentToggle(self.bot, "multimodal", self.guild_id)' in panel
    assert "MultimodalExperimentAbout" in panel


def test_message_handler_only_collects_media_when_enabled():
    source = (ROOT / "src/events/on_message.py").read_text(encoding="utf-8")
    assert 'get_ai_config(guild.id, "multimodal_experiment") == "True"' in source
    assert 'content_type.startswith("image/")' in source
    assert 'content_type.startswith("audio/")' in source
    assert "transcribe_audio" in source
    assert "image_urls=image_urls" in source
    assert "transcribed_audio=transcribed_audio" in source


def test_api_logging_filters_successful_polling_noise():
    source = (ROOT / "src/api_server.py").read_text(encoding="utf-8")
    assert "class _QuietSuccessfulRequests" in source
    assert "return status >= 400" in source
    assert "werkzeug_logger.addFilter" in source


def test_openai_request_uses_vision_content_and_transcription_model():
    source = (ROOT / "src/utils/ai/openai_client.py").read_text(encoding="utf-8")
    assert "audio.transcriptions.create" in source
    assert 'OPENAI_TRANSCRIPTION_MODEL' in source
    assert 'OPENAI_VISION_MODEL' in source
    assert '"gpt-4.1-mini"' in source
    assert '"gpt-4o-mini"' not in source
    assert '"type": "image_url"' in source
