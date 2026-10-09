import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, List, Optional, Sequence


def _default_db_path() -> Path:
    app_data = Path(os.environ.get("APPDATA", str(Path.home() / ".config")))
    cache_dir = app_data / "watch-subtitles"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "subtitles.db"


class SubtitleCache:
    """SQLite-backed subtitle cache keyed by deterministic video fingerprint and target language."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = db_path if db_path is not None else _default_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS subtitle_cache (
                    video_fingerprint TEXT NOT NULL,
                    target_language TEXT NOT NULL,
                    source_filename TEXT,
                    cues_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (video_fingerprint, target_language)
                )
                """
            )
            conn.commit()

    def save_cues(
        self,
        video_fingerprint: str,
        target_language: str,
        cues: Sequence[Any],
        source_filename: str = "",
    ) -> None:
        """Persist or update cues for a given video fingerprint and language."""
        cues_data = [
            c.model_dump() if hasattr(c, "model_dump")
            else dict(c) if hasattr(c, "_asdict")
            else c
            for c in cues
        ]
        cues_json = json.dumps(cues_data, ensure_ascii=False)

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO subtitle_cache (video_fingerprint, target_language, source_filename, cues_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(video_fingerprint, target_language) DO UPDATE SET
                    cues_json = excluded.cues_json,
                    source_filename = excluded.source_filename,
                    created_at = CURRENT_TIMESTAMP
                """,
                (video_fingerprint, target_language, source_filename, cues_json),
            )
            conn.commit()

    def get_cues(self, video_fingerprint: str, target_language: str) -> Optional[List[dict]]:
        """Retrieve cues for a given fingerprint and language, or None if not found."""
        with self._connection() as conn:
            cursor = conn.execute(
                """
                SELECT cues_json FROM subtitle_cache
                WHERE video_fingerprint = ? AND target_language = ?
                """,
                (video_fingerprint, target_language),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return json.loads(row["cues_json"])

    def has_cues(self, video_fingerprint: str, target_language: str) -> bool:
        """Check if cached cues exist for the fingerprint and target language."""
        with self._connection() as conn:
            cursor = conn.execute(
                """
                SELECT 1 FROM subtitle_cache
                WHERE video_fingerprint = ? AND target_language = ?
                """,
                (video_fingerprint, target_language),
            )
            return cursor.fetchone() is not None

    def delete_cues(self, video_fingerprint: str, target_language: Optional[str] = None) -> bool:
        """Delete cached cues. If target_language is None, delete all entries for fingerprint."""
        with self._connection() as conn:
            if target_language is not None:
                cursor = conn.execute(
                    """
                    DELETE FROM subtitle_cache
                    WHERE video_fingerprint = ? AND target_language = ?
                    """,
                    (video_fingerprint, target_language),
                )
            else:
                cursor = conn.execute(
                    """
                    DELETE FROM subtitle_cache
                    WHERE video_fingerprint = ?
                    """,
                    (video_fingerprint,),
                )
            conn.commit()
            return cursor.rowcount > 0

    def list_cached_languages(self, video_fingerprint: str) -> List[str]:
        """Return list of target languages cached for this fingerprint."""
        with self._connection() as conn:
            cursor = conn.execute(
                """
                SELECT target_language FROM subtitle_cache
                WHERE video_fingerprint = ?
                """,
                (video_fingerprint,),
            )
            return [row["target_language"] for row in cursor.fetchall()]
