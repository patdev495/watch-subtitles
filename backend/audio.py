import asyncio
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Union


def get_ffmpeg_path() -> str:
    """Return path to ffmpeg executable, or raise RuntimeError if missing."""
    custom_path = os.environ.get("FFMPEG_PATH")
    if custom_path and os.path.exists(custom_path):
        return custom_path

    resolved = shutil.which("ffmpeg")
    if resolved:
        return resolved

    raise RuntimeError(
        "FFmpeg not found. Please install FFmpeg and ensure it is on PATH, "
        "or set the FFMPEG_PATH environment variable."
    )


def extract_audio(
    video_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    sample_rate: int = 16000,
    channels: int = 1,
) -> Path:
    """Extract audio stream from video container to mono 16kHz WAV format using FFmpeg."""
    src = Path(video_path)
    if not src.exists() or not src.is_file():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if output_path is not None:
        dest = Path(output_path)
    else:
        temp_dir = Path(tempfile.gettempdir()) / "watch-subtitles-audio"
        temp_dir.mkdir(parents=True, exist_ok=True)
        dest = temp_dir / f"{src.stem}_{uuid.uuid4().hex[:8]}.wav"

    dest.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = get_ffmpeg_path()

    cmd = [
        ffmpeg,
        "-y",
        "-i", str(src),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", str(sample_rate),
        "-ac", str(channels),
        str(dest),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg extraction failed (code {result.returncode}): {result.stderr}")

    return dest


async def extract_audio_async(
    video_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    sample_rate: int = 16000,
    channels: int = 1,
) -> Path:
    """Run extract_audio asynchronously in a worker thread to keep UI responsive."""
    return await asyncio.to_thread(
        extract_audio,
        video_path=video_path,
        output_path=output_path,
        sample_rate=sample_rate,
        channels=channels,
    )
