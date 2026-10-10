from pathlib import Path

from backend.bridge import BridgeApi


def test_bridge_restores_subtitle_display_preferences_after_relaunch(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("backend.settings._settings_path", lambda: tmp_path / "settings.json")
    first = BridgeApi(port=8999)
    selected = {
        "primary_line": "original",
        "overlay_visible": False,
        "lines": {
            "original": {"visible": True, "font_size": 27},
            "translated": {"visible": False, "font_size": 30},
            "originalPinyin": {"visible": True, "font_size": 15},
            "translatedPinyin": {"visible": True, "font_size": 15},
        },
    }

    assert first.save_subtitle_display_preferences(selected) == selected
    assert BridgeApi(port=8999).get_subtitle_display_preferences() == selected


def test_saving_api_settings_keeps_newer_subtitle_display_preferences(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("backend.settings._settings_path", lambda: tmp_path / "settings.json")
    bridge = BridgeApi(port=8999)
    stale_settings = bridge.get_settings()
    current = bridge.get_subtitle_display_preferences()
    current["primary_line"] = "original"
    bridge.save_subtitle_display_preferences(current)
    stale_settings["deepl_api_key"] = "updated"

    bridge.save_settings(stale_settings)

    assert BridgeApi(port=8999).get_subtitle_display_preferences()["primary_line"] == "original"
