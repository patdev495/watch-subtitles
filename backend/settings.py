import json
import os
from pathlib import Path
from pydantic import BaseModel, field_validator


class AppSettings(BaseModel):
    deepgram_api_key: str = ""
    assemblyai_api_key: str = ""
    deepl_api_key: str = ""
    default_target_language: str = "vi"
    stt_provider: str = "deepgram"
    translation_provider: str = "deepl"
    tts_provider: str = ""
    tts_api_key: str = ""

    @field_validator("default_target_language", mode="before")
    @classmethod
    def migrate_legacy_chinese_code(cls, value: object) -> object:
        return "zh-CN" if value == "zh" else value


def _settings_path() -> Path:
    app_data = Path(os.environ.get("APPDATA", str(Path.home() / ".config")))
    settings_dir = app_data / "watch-subtitles"
    settings_dir.mkdir(parents=True, exist_ok=True)
    return settings_dir / "settings.json"


def load_settings(path: Path | None = None) -> AppSettings:
    """Load persisted settings; return defaults if missing or corrupt."""
    target = path if path is not None else _settings_path()
    if not target.exists():
        return AppSettings()
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        return AppSettings(**data)
    except Exception:
        return AppSettings()


def save_settings(settings: AppSettings, path: Path | None = None) -> None:
    """Persist settings to JSON file."""
    target = path if path is not None else _settings_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(settings.model_dump_json(indent=2), encoding="utf-8")
