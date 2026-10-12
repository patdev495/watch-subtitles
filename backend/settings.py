import json
import os
from pathlib import Path
from typing import Any, Literal, get_args

from pydantic import BaseModel, Field, field_validator

ThemeName = Literal["dark", "light"]


class PlaybackQueueVideo(BaseModel):
    path: str
    source_language: str = "en"


class PlaybackQueueState(BaseModel):
    videos: list[PlaybackQueueVideo] = Field(default_factory=list)
    selected_path: str = ""
    playback_time: float = 0
    auto_advance: bool = True


class SubtitleLinePreference(BaseModel):
    visible: bool = True
    font_size: int = Field(default=18, ge=10, le=36)


class SubtitleDisplayLines(BaseModel):
    original: SubtitleLinePreference = Field(default_factory=lambda: SubtitleLinePreference(font_size=20))
    translated: SubtitleLinePreference = Field(default_factory=lambda: SubtitleLinePreference(font_size=18))
    originalPinyin: SubtitleLinePreference = Field(default_factory=lambda: SubtitleLinePreference(font_size=15))
    translatedPinyin: SubtitleLinePreference = Field(default_factory=lambda: SubtitleLinePreference(font_size=15))


class SubtitleDisplayPreferences(BaseModel):
    primary_line: Literal["original", "translated"] = "translated"
    overlay_visible: bool = True
    caption_color: str = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    lines: SubtitleDisplayLines = Field(default_factory=SubtitleDisplayLines)


class AppSettings(BaseModel):
    playback_queue: PlaybackQueueState = Field(default_factory=PlaybackQueueState)
    subtitle_display_preferences: SubtitleDisplayPreferences = Field(default_factory=SubtitleDisplayPreferences)
    theme: ThemeName = "dark"
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


def merge_settings(data: dict[str, Any]) -> AppSettings:
    """Build AppSettings from submitted data, keeping state the dialog does not own."""
    stored = load_settings()
    settings = AppSettings(**data)
    settings.playback_queue = stored.playback_queue
    settings.subtitle_display_preferences = stored.subtitle_display_preferences
    settings.theme = stored.theme
    return settings


def load_theme() -> ThemeName:
    """Return the persisted interface theme."""
    return load_settings().theme


def save_theme(theme: str) -> ThemeName:
    """Persist an interface theme; an unknown value keeps the stored theme."""
    settings = load_settings()
    if theme in get_args(ThemeName):
        settings.theme = theme
        save_settings(settings)
    return settings.theme
