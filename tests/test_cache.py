import tempfile
from pathlib import Path
import pytest
from backend.cache import SubtitleCache


def test_cache_save_and_retrieve_round_trip():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "subtitles.db"
        cache = SubtitleCache(db_path=db_path)

        cues = [
            {"id": "1", "start": 0.0, "end": 2.5, "originalText": "Hello", "translatedText": "Xin chào"},
            {"id": "2", "start": 2.5, "end": 5.0, "originalText": "World", "translatedText": "Thế giới"},
        ]

        cache.save_cues(
            video_fingerprint="dummy_fp_123",
            source_language="en",
            target_language="vi",
            cues=cues,
            source_filename="video.mp4",
        )

        assert cache.has_cues("dummy_fp_123", "en", "vi") is True
        assert cache.has_cues("dummy_fp_123", "en", "en") is False
        assert cache.has_cues("other_fp", "en", "vi") is False

        retrieved = cache.get_cues("dummy_fp_123", "en", "vi")
        assert retrieved == cues


def test_cache_returns_none_on_missing_key():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "subtitles.db"
        cache = SubtitleCache(db_path=db_path)

        assert cache.get_cues("unknown_hash", "en", "vi") is None


def test_cache_differentiates_by_language_pair():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "subtitles.db"
        cache = SubtitleCache(db_path=db_path)

        vi_cues = [{"id": "1", "start": 0.0, "end": 1.0, "originalText": "Hi", "translatedText": "Chào"}]
        ja_cues = [{"id": "1", "start": 0.0, "end": 1.0, "originalText": "Hi", "translatedText": "こんにちは"}]

        cache.save_cues("fp_abc", "en", "vi", vi_cues)
        cache.save_cues("fp_abc", "ja", "vi", ja_cues)

        assert cache.get_cues("fp_abc", "en", "vi") == vi_cues
        assert cache.get_cues("fp_abc", "ja", "vi") == ja_cues

        langs = cache.list_cached_languages("fp_abc")
        assert set(langs) == {("en", "vi"), ("ja", "vi")}


def test_cache_overwrite_updates_existing_entry():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "subtitles.db"
        cache = SubtitleCache(db_path=db_path)

        old_cues = [{"id": "1", "start": 0.0, "end": 1.0, "originalText": "Old", "translatedText": "Cũ"}]
        new_cues = [{"id": "1", "start": 0.0, "end": 1.0, "originalText": "New", "translatedText": "Mới"}]

        cache.save_cues("fp_1", "en", "vi", old_cues)
        cache.save_cues("fp_1", "en", "vi", new_cues)

        assert cache.get_cues("fp_1", "en", "vi") == new_cues


def test_cache_delete():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "subtitles.db"
        cache = SubtitleCache(db_path=db_path)

        cache.save_cues("fp_del", "en", "vi", [{"id": "1", "start": 0, "end": 1, "originalText": "A", "translatedText": "B"}])
        cache.save_cues("fp_del", "en", "ja", [{"id": "1", "start": 0, "end": 1, "originalText": "A", "translatedText": "B"}])

        # Delete single language
        deleted_vi = cache.delete_cues("fp_del", "en", "vi")
        assert deleted_vi is True
        assert cache.has_cues("fp_del", "en", "vi") is False
        assert cache.has_cues("fp_del", "en", "ja") is True

        # Delete all languages for fingerprint
        deleted_all = cache.delete_cues("fp_del")
        assert deleted_all is True
        assert cache.has_cues("fp_del", "en", "ja") is False
