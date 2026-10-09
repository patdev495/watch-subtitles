import hashlib
from pathlib import Path
from typing import Union

CHUNK_SIZE = 64 * 1024  # 64 KB


def compute_video_fingerprint(file_path: Union[str, Path]) -> str:
    """Compute a fast deterministic content hash of a video file.
    
    Combines file size, header (first 64KB), middle (64KB), and tail (last 64KB).
    This ensures deterministic fingerprinting regardless of filename or directory.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Video file not found: {file_path}")

    file_size = path.stat().st_size
    hasher = hashlib.sha256()
    hasher.update(str(file_size).encode("utf-8"))

    if file_size <= CHUNK_SIZE * 2:
        hasher.update(path.read_bytes())
        return hasher.hexdigest()

    with open(path, "rb") as f:
        # Head chunk
        hasher.update(f.read(CHUNK_SIZE))

        # Middle chunk
        mid_pos = max(0, (file_size - CHUNK_SIZE) // 2)
        f.seek(mid_pos)
        hasher.update(f.read(CHUNK_SIZE))

        # Tail chunk
        tail_pos = max(0, file_size - CHUNK_SIZE)
        f.seek(tail_pos)
        hasher.update(f.read(CHUNK_SIZE))

    return hasher.hexdigest()
