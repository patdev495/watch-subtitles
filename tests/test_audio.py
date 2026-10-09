import asyncio
import os
import subprocess
import tempfile
from pathlib import Path
import pytest
from backend.audio import extract_audio, extract_audio_async, get_ffmpeg_path


def test_get_ffmpeg_path_found():
    path = get_ffmpeg_path()
    assert os.path.exists(path)
    assert "ffmpeg" in path.lower()


def test_extract_audio_nonexistent_file_raises():
    with pytest.raises(FileNotFoundError):
        extract_audio("non_existent_file.mp4")


def test_extract_audio_real_file():
    # Generate a small 1-second test audio file using ffmpeg
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "test_input.mp4"
        cmd = [
            get_ffmpeg_path(),
            "-y",
            "-f", "lavfi",
            "-i", "sine=frequency=1000:duration=1",
            "-ac", "2",
            "-ar", "44100",
            str(input_file),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        assert input_file.exists()

        # Extract audio to 16kHz mono WAV
        out_wav = extract_audio(input_file)
        assert out_wav.exists()
        assert out_wav.stat().st_size > 0
        assert out_wav.suffix == ".wav"


@pytest.mark.anyio
async def test_extract_audio_async_nonblocking():
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "test_input.mp4"
        cmd = [
            get_ffmpeg_path(),
            "-y",
            "-f", "lavfi",
            "-i", "sine=frequency=500:duration=1",
            str(input_file),
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        out_wav = await extract_audio_async(input_file)
        assert out_wav.exists()
        assert out_wav.stat().st_size > 0
