import json
import tempfile
from pathlib import Path
import pytest
from backend.settings import AppSettings, load_settings, save_settings


# ── Slice 1: defaults when no file ─────────────────────────────────────────────

def test_load_settings_returns_defaults_when_missing():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "settings.json"
        settings = load_settings(path=path)
        assert settings.deepgram_api_key == ""
        assert settings.deepl_api_key == ""
        assert settings.default_target_language == "vi"
        assert settings.stt_provider == "deepgram"
        assert settings.translation_provider == "deepl"


# ── Slice 2: save → load round-trip ────────────────────────────────────────────

def test_save_and_load_round_trip():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "settings.json"
        original = AppSettings(
            deepgram_api_key="dgk-test-123",
            deepl_api_key="deepl-test-456",
            default_target_language="en",
        )
        save_settings(original, path=path)

        loaded = load_settings(path=path)
        assert loaded.deepgram_api_key == "dgk-test-123"
        assert loaded.deepl_api_key == "deepl-test-456"
        assert loaded.default_target_language == "en"


# ── Slice 3: corrupt file → defaults (no crash) ────────────────────────────────

def test_load_settings_returns_defaults_on_corrupt_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "settings.json"
        path.write_text("not valid json{{", encoding="utf-8")
        settings = load_settings(path=path)
        assert settings.deepgram_api_key == ""


# ── Slice 4: save creates parent dirs ──────────────────────────────────────────

def test_save_creates_parent_directories():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "nested" / "dir" / "settings.json"
        save_settings(AppSettings(), path=path)
        assert path.exists()


# ── Slice 5: provider fields persisted ─────────────────────────────────────────

def test_provider_fields_persist():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "settings.json"
        original = AppSettings(
            assemblyai_api_key="aai-test-789",
            stt_provider="assemblyai",
            translation_provider="deepl",
        )
        save_settings(original, path=path)
        loaded = load_settings(path=path)
        assert loaded.assemblyai_api_key == "aai-test-789"
        assert loaded.stt_provider == "assemblyai"
        assert loaded.translation_provider == "deepl"


def test_load_settings_migrates_legacy_chinese_target_code():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "settings.json"
        path.write_text(json.dumps({"default_target_language": "zh"}), encoding="utf-8")

        assert load_settings(path=path).default_target_language == "zh-CN"
