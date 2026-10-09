import os
import shutil
import tempfile
from pathlib import Path
import pytest
from backend.fingerprint import compute_video_fingerprint


def test_fingerprint_deterministic_same_content():
    content = b"header_data_" * 1000 + b"middle_data_" * 1000 + b"tail_data_" * 1000
    with tempfile.TemporaryDirectory() as tmp:
        file1 = Path(tmp) / "video1.mp4"
        file1.write_bytes(content)

        hash1 = compute_video_fingerprint(file1)
        hash2 = compute_video_fingerprint(file1)
        assert hash1 == hash2
        assert len(hash1) == 64  # sha256 hex string


def test_fingerprint_identical_when_renamed_or_moved():
    content = b"sample_video_bytes_for_testing" * 2000
    with tempfile.TemporaryDirectory() as tmp:
        dir1 = Path(tmp) / "folder1"
        dir2 = Path(tmp) / "folder2"
        dir1.mkdir()
        dir2.mkdir()

        original_file = dir1 / "original_movie.mkv"
        original_file.write_bytes(content)

        renamed_file = dir2 / "completely_different_name.mp4"
        shutil.copyfile(original_file, renamed_file)

        hash_orig = compute_video_fingerprint(original_file)
        hash_moved = compute_video_fingerprint(renamed_file)

        assert hash_orig == hash_moved


def test_fingerprint_different_for_different_files():
    with tempfile.TemporaryDirectory() as tmp:
        file1 = Path(tmp) / "file1.mp4"
        file2 = Path(tmp) / "file2.mp4"
        file1.write_bytes(b"content_alpha" * 500)
        file2.write_bytes(b"content_beta" * 500)

        hash1 = compute_video_fingerprint(file1)
        hash2 = compute_video_fingerprint(file2)

        assert hash1 != hash2


def test_fingerprint_small_file():
    with tempfile.TemporaryDirectory() as tmp:
        small = Path(tmp) / "small.mp4"
        small.write_bytes(b"tiny")

        h = compute_video_fingerprint(small)
        assert isinstance(h, str)
        assert len(h) == 64


def test_fingerprint_nonexistent_raises():
    with pytest.raises(FileNotFoundError):
        compute_video_fingerprint("non_existent_video_path.mp4")
