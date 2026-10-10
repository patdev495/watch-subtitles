from pathlib import Path
from unittest.mock import MagicMock

import webview

from backend.bridge import BridgeApi
from backend.cache import SubtitleCache
from backend.settings import load_settings


def test_bridge_imports_multiple_files_in_dialog_order_and_folder_files_by_name(tmp_path: Path) -> None:
    first = tmp_path / "b.mp4"
    second = tmp_path / "a.mkv"
    ignored = tmp_path / "readme.txt"
    nested = tmp_path / "nested"
    nested.mkdir()
    for path in (first, second, ignored, nested / "c.mp4"):
        path.write_bytes(b"video")
    window = MagicMock()
    window.create_file_dialog.side_effect = [(str(first), str(second)), str(tmp_path)]
    bridge = BridgeApi(port=8999)
    bridge.set_window(window)

    files = bridge.open_video_files_dialog()
    folder = bridge.open_video_folder_dialog()

    assert [entry["path"] for entry in files["videos"]] == [str(first), str(second)]
    assert [entry["path"] for entry in folder["videos"]] == [str(second), str(first)]
    assert window.create_file_dialog.call_args_list[0].kwargs["allow_multiple"] is True
    assert window.create_file_dialog.call_args_list[1].kwargs["dialog_type"] == webview.FileDialog.FOLDER


def test_playback_queue_round_trips_and_omits_missing_paths(tmp_path: Path, monkeypatch) -> None:
    settings_path = tmp_path / "settings.json"
    monkeypatch.setattr("backend.settings._settings_path", lambda: settings_path)
    playable = tmp_path / "playable.mp4"
    playable.write_bytes(b"video")
    missing = tmp_path / "gone.mp4"
    state = {
        "videos": [
            {"path": str(playable), "source_language": "ja"},
            {"path": str(missing), "source_language": "en"},
        ],
        "selected_path": str(playable), "playback_time": 42.5, "auto_advance": False,
    }
    bridge = BridgeApi(port=8999)
    assert bridge.get_playback_queue()["auto_advance"] is True
    bridge.save_playback_queue(state)

    restored = BridgeApi(port=8999).get_playback_queue()
    assert restored == {
        "videos": [{"path": str(playable), "source_language": "ja"}],
        "selected_path": str(playable), "playback_time": 42.5, "auto_advance": False,
    }
    assert load_settings().playback_queue.auto_advance is False


def test_player_loads_most_recent_cached_pair(tmp_path: Path) -> None:
    video = tmp_path / "lesson.mp4"
    video.write_bytes(b"video")
    bridge = BridgeApi(port=8999, cache=SubtitleCache(tmp_path / "cache.db"))
    bridge.save_cached_subtitles(str(video), "en", "vi", [{"id": "old"}])
    bridge.save_cached_subtitles(str(video), "ja", "en", [{"id": "new"}])

    latest = bridge.get_latest_cached_subtitles(str(video))
    assert latest["cached"] is True
    assert (latest["source_language"], latest["target_language"]) == ("ja", "en")
    assert latest["cues"] == [{"id": "new"}]

    bridge.save_cached_subtitles(str(video), "en", "vi", [{"id": "newest"}])
    updated = bridge.get_latest_cached_subtitles(str(video))
    assert (updated["source_language"], updated["target_language"]) == ("en", "vi")
    assert updated["cues"] == [{"id": "newest"}]
