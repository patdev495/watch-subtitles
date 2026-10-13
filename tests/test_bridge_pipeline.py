"""Exercise the real pipeline through the Subtitle Job interface."""

from pathlib import Path
from time import sleep
from typing import Any, Sequence
from unittest.mock import MagicMock, patch

import pytest

from backend.bridge import BridgeApi
from backend.cache import SubtitleCache
from backend.providers.base import CueResult, STTProvider, TranslationProvider
from backend.settings import AppSettings


class MockSTT(STTProvider):
    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    def transcribe(self, audio_path: str, language: str = "") -> Sequence[CueResult]:
        return [CueResult(id="1", start=1.0, end=3.0, original_text="Hello")]

    def validate_key(self, api_key: str) -> bool:
        return bool(api_key)


class MockTrans(TranslationProvider):
    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    def translate(self, texts: Sequence[str], source_language: str, target_language: str) -> Sequence[str]:
        return ["Xin chào"]

    def validate_key(self, api_key: str) -> bool:
        return bool(api_key)


class KeyRecordingSTT(MockSTT):
    received_keys: list[str] = []

    def __init__(self, api_key: str = "") -> None:
        super().__init__(api_key)
        self.received_keys.append(api_key)


def _wait_for_job(bridge: BridgeApi, job_id: str) -> dict[str, Any]:
    for _ in range(100):
        result = bridge.get_subtitle_job(job_id)
        job = result["job"]
        if job["status"] in {"completed", "failed"}:
            return job
        sleep(0.01)
    pytest.fail(f"Subtitle Job {job_id} did not finish")


def test_subtitle_job_reports_missing_keys(tmp_path: Path) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"dummy")
    bridge = BridgeApi(port=8080, cache=SubtitleCache(tmp_path / "cache.db"))

    with patch("backend.bridge.load_settings", return_value=AppSettings(deepgram_api_key="", deepl_api_key="")):
        response = bridge.create_subtitle_job(str(video), "en", "vi")
        job = _wait_for_job(bridge, response["job"]["id"])

    assert response["ok"] is True
    assert job["status"] == "failed"
    assert "API key" in job["error"]


def test_subtitle_job_runs_pipeline_and_emits_progress(tmp_path: Path) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"dummy video" * 100)
    audio = tmp_path / "audio.wav"
    audio.write_bytes(b"dummy wav")
    window = MagicMock()
    bridge = BridgeApi(port=8080, cache=SubtitleCache(tmp_path / "cache.db"))
    bridge.set_window(window)
    settings = AppSettings(
        assemblyai_api_key="aai-key",
        stt_provider="assemblyai",
        translation_provider="test-trans",
    )

    with patch.dict("backend.bridge.STT_PROVIDERS", {"assemblyai": MockSTT}), \
         patch.dict("backend.bridge.TRANSLATION_PROVIDERS", {"test-trans": MockTrans}), \
         patch("backend.bridge.load_settings", return_value=settings), \
         patch("backend.pipeline.extract_audio", return_value=audio):
        response = bridge.create_subtitle_job(str(video), "en", "vi")
        job = _wait_for_job(bridge, response["job"]["id"])

    assert response["ok"] is True
    assert job["status"] == "completed"
    assert job["progress"] == 100.0
    assert job["cues"][0]["translatedText"] == "Xin chào"
    assert any("subtitle-job-progress" in call.args[0] for call in window.evaluate_js.call_args_list)


def test_subtitle_job_uses_selected_stt_credential(tmp_path: Path) -> None:
    KeyRecordingSTT.received_keys.clear()
    video = tmp_path / "video.mp4"
    video.write_bytes(b"dummy video" * 100)
    audio = tmp_path / "audio.wav"
    audio.write_bytes(b"dummy wav")
    bridge = BridgeApi(port=8080, cache=SubtitleCache(tmp_path / "cache.db"))
    settings = AppSettings(
        assemblyai_api_key="aai-key",
        stt_provider="assemblyai",
        translation_provider="test-trans",
    )

    with patch.dict("backend.bridge.STT_PROVIDERS", {"assemblyai": KeyRecordingSTT}), \
         patch.dict("backend.bridge.TRANSLATION_PROVIDERS", {"test-trans": MockTrans}), \
         patch("backend.bridge.load_settings", return_value=settings), \
         patch("backend.pipeline.extract_audio", return_value=audio):
        response = bridge.create_subtitle_job(str(video), "en", "vi")
        job = _wait_for_job(bridge, response["job"]["id"])

    assert job["status"] == "completed"
    assert KeyRecordingSTT.received_keys == ["aai-key"]
