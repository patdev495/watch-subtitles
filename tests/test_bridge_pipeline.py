import json
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from backend.bridge import BridgeApi
from backend.cache import SubtitleCache
from backend.settings import AppSettings
from backend.providers.base import CueResult, STTProvider, TranslationProvider
from backend.providers import register_stt_provider, register_translation_provider


class MockSTT(STTProvider):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def transcribe(self, audio_path: str, language: str = ""):
        return [CueResult(id="1", start=1.0, end=3.0, original_text="Hello")]

    def validate_key(self, api_key: str) -> bool:
        return bool(api_key)


class MockTrans(TranslationProvider):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def translate(self, texts, source_language: str, target_language: str):
        return ["Xin chào"]

    def validate_key(self, api_key: str) -> bool:
        return bool(api_key)


def test_bridge_start_pipeline_missing_keys():
    with tempfile.TemporaryDirectory() as tmp:
        video_path = Path(tmp) / "video.mp4"
        video_path.write_bytes(b"dummy")
        bridge = BridgeApi(port=8080)
        with patch("backend.bridge.load_settings", return_value=AppSettings(deepgram_api_key="", deepl_api_key="")):
            res = bridge.start_subtitles_pipeline(str(video_path), "en", "vi")
            assert res["ok"] is False
            assert "API key" in res["error"]


def test_bridge_start_pipeline_background_execution():
    register_stt_provider("test_stt", MockSTT)
    register_translation_provider("test_trans", MockTrans)

    with tempfile.TemporaryDirectory() as tmp:
        video_path = Path(tmp) / "video.mp4"
        video_path.write_bytes(b"dummy video" * 100)

        cache = SubtitleCache(db_path=Path(tmp) / "cache.db")
        mock_window = MagicMock()
        bridge = BridgeApi(port=8080, cache=cache)
        bridge.set_window(mock_window)

        settings = AppSettings(
            deepgram_api_key="dg-key",
            deepl_api_key="dl-key",
            stt_provider="test_stt",
            translation_provider="test_trans",
        )

        dummy_audio = Path(tmp) / "audio.wav"
        dummy_audio.write_bytes(b"dummy wav")

        with patch("backend.bridge.load_settings", return_value=settings), \
             patch("backend.pipeline.extract_audio", return_value=dummy_audio):
            start_res = bridge.start_subtitles_pipeline(str(video_path), "en", "vi")
            assert start_res["ok"] is True

            # Wait briefly for background thread to complete
            for _ in range(50):
                status = bridge.get_pipeline_status()
                if status.get("status") in ("completed", "error"):
                    break
                time.sleep(0.05)

            final_status = bridge.get_pipeline_status()
            assert final_status["status"] == "completed"
            assert final_status["progress"] == 100.0
            assert len(final_status["cues"]) == 1
            assert final_status["cues"][0]["translatedText"] == "Xin chào"

            # Check that evaluate_js was invoked with progress
            assert mock_window.evaluate_js.called
