from typing import Sequence
import pytest
from backend.providers.base import STTProvider, TranslationProvider, TTSProvider, CueResult
from backend.providers import (
    STT_PROVIDERS,
    TRANSLATION_PROVIDERS,
    TTS_PROVIDERS,
    register_stt_provider,
    register_translation_provider,
    register_tts_provider,
)
from backend.bridge import BridgeApi


class MockCustomSTT(STTProvider):
    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    def transcribe(self, audio_path: str, language: str) -> Sequence[CueResult]:
        return [CueResult(id="1", start=0.0, end=1.0, original_text="Hello")]

    def validate_key(self, api_key: str) -> bool:
        return api_key == "valid-stt-key"


class MockCustomTranslation(TranslationProvider):
    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    def translate(self, texts: Sequence[str], target_language: str) -> Sequence[str]:
        return [f"[{target_language}] {t}" for t in texts]

    def validate_key(self, api_key: str) -> bool:
        return api_key == "valid-trans-key"


class MockCustomTTS(TTSProvider):
    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    def synthesize(self, text: str, output_path: str, voice: str | None = None) -> str:
        return output_path

    def validate_key(self, api_key: str) -> bool:
        return api_key == "valid-tts-key"


def test_stt_provider_extensibility():
    register_stt_provider("custom_stt", MockCustomSTT)
    assert "custom_stt" in STT_PROVIDERS
    instance = STT_PROVIDERS["custom_stt"]()
    assert instance.validate_key("valid-stt-key") is True
    assert instance.validate_key("invalid") is False


def test_translation_provider_extensibility():
    register_translation_provider("custom_trans", MockCustomTranslation)
    assert "custom_trans" in TRANSLATION_PROVIDERS
    instance = TRANSLATION_PROVIDERS["custom_trans"]()
    assert instance.validate_key("valid-trans-key") is True
    res = instance.translate(["Hello"], "vi")
    assert res == ["[vi] Hello"]


def test_tts_provider_extensibility():
    register_tts_provider("custom_tts", MockCustomTTS)
    assert "custom_tts" in TTS_PROVIDERS
    instance = TTS_PROVIDERS["custom_tts"]()
    assert instance.validate_key("valid-tts-key") is True
    assert instance.synthesize("test", "/tmp/out.wav") == "/tmp/out.wav"


def test_bridge_test_connection_extensible_providers():
    bridge = BridgeApi(port=8000)
    register_stt_provider("mock_stt", MockCustomSTT)
    register_translation_provider("mock_trans", MockCustomTranslation)
    register_tts_provider("mock_tts", MockCustomTTS)

    # Valid keys
    res_stt = bridge.test_connection("stt", "mock_stt", "valid-stt-key")
    assert res_stt["ok"] is True

    res_trans = bridge.test_connection("translation", "mock_trans", "valid-trans-key")
    assert res_trans["ok"] is True

    res_tts = bridge.test_connection("tts", "mock_tts", "valid-tts-key")
    assert res_tts["ok"] is True

    # Invalid keys
    res_bad = bridge.test_connection("tts", "mock_tts", "bad-key")
    assert res_bad["ok"] is False

    # Unknown provider
    res_unknown = bridge.test_connection("tts", "nonexistent", "key")
    assert res_unknown["ok"] is False

    # Unknown provider type
    res_unknown_type = bridge.test_connection("video", "mock", "key")
    assert res_unknown_type["ok"] is False
