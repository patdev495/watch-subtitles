import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional, Sequence


def _default_db_path() -> Path:
    app_data = Path(os.environ.get("APPDATA", str(Path.home() / ".config")))
    cache_dir = app_data / "watch-subtitles"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "subtitles.db"


class SubtitleCache:
    """SQLite Subtitle Cache keyed by video fingerprint and language pair."""

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
            columns = conn.execute("PRAGMA table_info(subtitle_cache)").fetchall()
            if columns and "source_language" not in {column["name"] for column in columns}:
                conn.execute("DROP TABLE subtitle_cache")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS subtitle_cache (
                    video_fingerprint TEXT NOT NULL,
                    source_language TEXT NOT NULL,
                    target_language TEXT NOT NULL,
                    source_filename TEXT,
                    cues_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (video_fingerprint, source_language, target_language)
                )
                """
            )
            conn.commit()

    def save_cues(
        self,
        video_fingerprint: str,
        source_language: str,
        target_language: str,
        cues: Sequence[Any],
        source_filename: str = "",
    ) -> None:
        cues_json = json.dumps([
            cue.model_dump() if hasattr(cue, "model_dump") else dict(cue) if hasattr(cue, "_asdict") else cue
            for cue in cues
        ], ensure_ascii=False)
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO subtitle_cache (video_fingerprint, source_language, target_language, source_filename, cues_json)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(video_fingerprint, source_language, target_language) DO UPDATE SET
                    cues_json = excluded.cues_json, source_filename = excluded.source_filename, created_at = CURRENT_TIMESTAMP
                """,
                (video_fingerprint, source_language, target_language, source_filename, cues_json),
            )
            conn.commit()

    def get_cues(self, video_fingerprint: str, source_language: str, target_language: str) -> Optional[list[dict[str, Any]]]:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT cues_json FROM subtitle_cache WHERE video_fingerprint = ? AND source_language = ? AND target_language = ?",
                (video_fingerprint, source_language, target_language),
            ).fetchone()
            return json.loads(row["cues_json"]) if row else None

    def has_cues(self, video_fingerprint: str, source_language: str, target_language: str) -> bool:
        return self.get_cues(video_fingerprint, source_language, target_language) is not None

    def delete_cues(self, video_fingerprint: str, source_language: Optional[str] = None, target_language: Optional[str] = None) -> bool:
        with self._connection() as conn:
            if source_language is None or target_language is None:
                cursor = conn.execute("DELETE FROM subtitle_cache WHERE video_fingerprint = ?", (video_fingerprint,))
            else:
                cursor = conn.execute(
                    "DELETE FROM subtitle_cache WHERE video_fingerprint = ? AND source_language = ? AND target_language = ?",
                    (video_fingerprint, source_language, target_language),
                )
            conn.commit()
            return cursor.rowcount > 0

    def list_cached_languages(self, video_fingerprint: str) -> list[tuple[str, str]]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT source_language, target_language FROM subtitle_cache WHERE video_fingerprint = ?",
                (video_fingerprint,),
            ).fetchall()
            return [(row["source_language"], row["target_language"]) for row in rows]
