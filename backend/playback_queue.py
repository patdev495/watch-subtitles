"""Playback Queue import and persisted state for the desktop bridge."""

import os
from pathlib import Path
from typing import Any, Callable

import webview

from backend.settings import PlaybackQueueState, load_settings, save_settings


VIDEO_EXTENSIONS = {".mp4", ".mkv", ".webm", ".avi", ".mov", ".flv", ".wmv", ".m4v"}


def import_video_files(
    window: webview.Window | None,
    load_video_path: Callable[[str], dict[str, Any]],
) -> dict[str, Any]:
    if window is None:
        return {"cancelled": True, "videos": []}
    selected = window.create_file_dialog(
        dialog_type=webview.FileDialog.OPEN,
        allow_multiple=True,
        file_types=("Video Files (*.mp4;*.mkv;*.webm;*.avi;*.mov;*.flv;*.wmv;*.m4v)",),
    )
    paths = [selected] if isinstance(selected, str) else (selected or [])
    videos = [load_video_path(path) for path in paths if Path(path).suffix.lower() in VIDEO_EXTENSIONS]
    return {"cancelled": not selected, "videos": [video for video in videos if not video["cancelled"]]}


def import_video_folder(
    window: webview.Window | None,
    load_video_path: Callable[[str], dict[str, Any]],
) -> dict[str, Any]:
    if window is None:
        return {"cancelled": True, "videos": []}
    selected = window.create_file_dialog(dialog_type=webview.FileDialog.FOLDER)
    folder = selected if isinstance(selected, str) else (selected[0] if selected else "")
    if not folder or not os.path.isdir(folder):
        return {"cancelled": True, "videos": []}
    paths = sorted(
        (path for path in Path(folder).iterdir() if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS),
        key=lambda path: path.name.casefold(),
    )
    return {"cancelled": False, "videos": [load_video_path(str(path)) for path in paths]}


def get_playback_queue() -> dict[str, Any]:
    state = load_settings().playback_queue
    videos = [video for video in state.videos if os.path.isfile(video.path)]
    selected = state.selected_path if any(video.path == state.selected_path for video in videos) else ""
    return PlaybackQueueState(
        videos=videos,
        selected_path=selected,
        playback_time=state.playback_time if selected else 0,
        auto_advance=state.auto_advance,
    ).model_dump()


def save_playback_queue(data: dict[str, Any]) -> dict[str, Any]:
    settings = load_settings()
    settings.playback_queue = PlaybackQueueState(**data)
    save_settings(settings)
    return settings.playback_queue.model_dump()
