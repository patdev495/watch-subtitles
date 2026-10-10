import asyncio
import os
import subprocess
import tempfile
from pathlib import Path
import pytest
import backend.audio as audio
from backend.audio import extract_audio, extract_audio_async, get_ffmpeg_path


def test_get_ffmpeg_path_uses_bundled_binary(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    bundled_binary = tmp_path / "ffmpeg.exe"
    bundled_binary.touch()
    monkeypatch.setattr(audio.sys, "_MEIPASS", str(tmp_path), raising=False)
    monkeypatch.delenv("FFMPEG_PATH", raising=False)
    monkeypatch.setattr(audio.shutil, "which", lambda _: None)

    assert get_ffmpeg_path() == str(bundled_binary)


def test_get_ffmpeg_path_found():
    path = get_ffmpeg_path()
    assert os.path.exists(path)
    assert "ffmpeg" in path.lower()


def test_extract_audio_nonexistent_file_raises():
    with pytest.raises(FileNotFoundError):
        extract_audio("non_existent_file.mp4")


def test_extract_audio_decodes_ffmpeg_output_as_utf8_safely(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    input_file = tmp_path / "input.mp4"
    input_file.write_bytes(b"video")
    output_file = tmp_path / "audio.wav"
    recorded_options: dict[str, object] = {}

    def fake_run(_cmd: list[str], **options: object) -> subprocess.CompletedProcess[str]:
        recorded_options.update(options)
        return subprocess.CompletedProcess(_cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(audio, "get_ffmpeg_path", lambda: "ffmpeg")
    monkeypatch.setattr(audio.subprocess, "run", fake_run)

    assert extract_audio(input_file, output_file) == output_file
    assert recorded_options["encoding"] == "utf-8"
    assert recorded_options["errors"] == "replace"


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
