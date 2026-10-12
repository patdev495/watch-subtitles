"""Poster frames for Playback Queue Videos.

One JPEG per Video Fingerprint is extracted with FFmpeg on first request and
cached on disk next to the Subtitle Cache, so the library can show frames
without decoding video again on every launch.
"""

import os
import subprocess
from pathlib import Path
from typing import Union

from backend.audio import get_ffmpeg_path

THUMBNAIL_WIDTH = 400
THUMBNAIL_QUALITY = 4
THUMBNAIL_SEEK_SECONDS = 3


def _app_data_dir() -> Path:
    app_data = Path(os.environ.get("APPDATA", str(Path.home() / ".config")))
    return app_data / "watch-subtitles"


def thumbnail_cache_dir() -> Path:
    """Return the directory holding cached Video thumbnails."""
    directory = _app_data_dir() / "thumbnails"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _is_usable(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def _extract_frame(ffmpeg: str, source: Path, target: Path, seek_seconds: int) -> None:
    command = [
        ffmpeg,
        "-y",
        "-loglevel", "error",
        "-ss", str(seek_seconds),
        "-i", str(source),
        "-frames:v", "1",
        "-vf", f"scale={THUMBNAIL_WIDTH}:-2",
        "-q:v", str(THUMBNAIL_QUALITY),
        str(target),
    ]
    subprocess.run(
        command,
        check=True,
        capture_output=True,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )


def generate_thumbnail(
    video_path: Union[str, Path],
    fingerprint: str,
    directory: Path | None = None,
) -> Path:
    """Return the cached poster frame for a Video, extracting it when missing."""
    source = Path(video_path)
    if not source.is_file():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    target_dir = directory if directory is not None else thumbnail_cache_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{fingerprint}.jpg"
    if _is_usable(target):
        return target

    ffmpeg = get_ffmpeg_path()
    # A Video shorter than the seek offset yields an empty file, so retry from the start.
    for seek_seconds in (THUMBNAIL_SEEK_SECONDS, 0):
        try:
            _extract_frame(ffmpeg, source, target, seek_seconds)
        except subprocess.CalledProcessError:
            continue
        if _is_usable(target):
            return target

    raise RuntimeError(f"Could not extract a thumbnail frame from {video_path}")
