import subprocess
import tempfile
from pathlib import Path

import httpx
import pytest

from backend import server as server_module
from backend import thumbnails
from backend.bridge import BridgeApi
from backend.settings import AppSettings
from backend.thumbnails import generate_thumbnail


def test_generate_thumbnail_reuses_cached_frame(tmp_path, monkeypatch):
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"video")
    cache_dir = tmp_path / "thumbs"
    cache_dir.mkdir()
    cached = cache_dir / "fingerprint.jpg"
    cached.write_bytes(b"jpeg")

    def fail_extract(*args):
        raise AssertionError("an already cached thumbnail must not be re-extracted")

    monkeypatch.setattr(thumbnails, "_extract_frame", fail_extract)
    assert generate_thumbnail(video, "fingerprint", directory=cache_dir) == cached


def test_generate_thumbnail_retries_from_start_for_short_video(tmp_path, monkeypatch):
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"video")
    attempts = []

    def fake_extract(ffmpeg, source, target, seek_seconds):
        attempts.append(seek_seconds)
        target.write_bytes(b"" if seek_seconds else b"jpeg")

    monkeypatch.setattr(thumbnails, "get_ffmpeg_path", lambda: "ffmpeg")
    monkeypatch.setattr(thumbnails, "_extract_frame", fake_extract)

    result = generate_thumbnail(video, "fp", directory=tmp_path / "thumbs")
    assert attempts == [thumbnails.THUMBNAIL_SEEK_SECONDS, 0]
    assert result.read_bytes() == b"jpeg"


def test_generate_thumbnail_reports_failure(tmp_path, monkeypatch):
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"video")

    def failing_extract(*args):
        raise subprocess.CalledProcessError(1, "ffmpeg")

    monkeypatch.setattr(thumbnails, "get_ffmpeg_path", lambda: "ffmpeg")
    monkeypatch.setattr(thumbnails, "_extract_frame", failing_extract)

    with pytest.raises(RuntimeError):
        generate_thumbnail(video, "fp", directory=tmp_path / "thumbs")


def test_generate_thumbnail_rejects_missing_video(tmp_path):
    with pytest.raises(FileNotFoundError):
        generate_thumbnail(tmp_path / "missing.mp4", "fp", directory=tmp_path / "thumbs")


def test_thumbnail_route_serves_jpeg(tmp_path, monkeypatch):
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"video")
    frame = tmp_path / "frame.jpg"
    frame.write_bytes(b"\xff\xd8\xff\xe0fake-jpeg")
    monkeypatch.setattr(server_module, "compute_video_fingerprint", lambda path: "fp")
    monkeypatch.setattr(server_module, "generate_thumbnail", lambda path, fingerprint: frame)

    server, port = server_module.start_stream_server()
    try:
        response = httpx.get(f"http://127.0.0.1:{port}/thumbnail", params={"path": str(video)})
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"
        assert response.content == frame.read_bytes()
    finally:
        server.shutdown()


def test_thumbnail_route_rejects_unknown_video():
    server, port = server_module.start_stream_server()
    try:
        response = httpx.get(f"http://127.0.0.1:{port}/thumbnail", params={"path": "Z:/does-not-exist.mp4"})
        assert response.status_code == 404
    finally:
        server.shutdown()


def test_bridge_get_thumbnail_url_resolves_local_server():
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as handle:
        handle.write(b"dummy video content")
        temp_path = handle.name
    try:
        api = BridgeApi(port=8999)
        result = api.get_thumbnail_url(temp_path)
        assert result["ok"] is True
        assert result["url"].startswith("http://127.0.0.1:8999/thumbnail?path=")
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_bridge_get_thumbnail_url_rejects_missing_video():
    assert BridgeApi(port=8999).get_thumbnail_url("Z:/missing.mp4")["ok"] is False


def test_bridge_theme_round_trip(monkeypatch):
    stored = {"settings": AppSettings()}
    monkeypatch.setattr("backend.settings.load_settings", lambda: stored["settings"])
    monkeypatch.setattr("backend.settings.save_settings", lambda settings: stored.update(settings=settings))

    api = BridgeApi(port=8080)
    assert api.get_theme() == {"theme": "dark"}
    assert api.save_theme("light") == {"theme": "light"}
    assert stored["settings"].theme == "light"
    # An unknown theme is ignored rather than persisted.
    assert api.save_theme("neon") == {"theme": "light"}


def test_save_settings_keeps_stored_theme(monkeypatch):
    stored = {"settings": AppSettings(theme="light")}
    monkeypatch.setattr("backend.settings.load_settings", lambda: stored["settings"])
    monkeypatch.setattr("backend.bridge.persist_settings", lambda settings: stored.update(settings=settings))

    saved = BridgeApi(port=8080).save_settings({"default_target_language": "ja"})
    assert saved["theme"] == "light"
    assert saved["default_target_language"] == "ja"
