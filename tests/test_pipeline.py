from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import pytest
from backend.cache import SubtitleCache
from backend.providers.base import CueResult, STTProvider, TranslationProvider
from backend.pipeline import run_subtitling_pipeline


class DummySTT(STTProvider):
    def __init__(self, cues=None):
        self._cues = cues if cues is not None else [
            CueResult(id="1", start=0.0, end=2.0, original_text="Hello world"),
            CueResult(id="2", start=2.5, end=4.5, original_text="How are you"),
        ]

    def transcribe(self, audio_path: str, language: str = ""):
        self.last_language = language
        return self._cues

    def validate_key(self, api_key: str) -> bool:
        return True


class DummyTranslation(TranslationProvider):
    def translate(self, texts, source_language: str, target_language: str):
        self.last_source_language = source_language
        return [f"[{target_language}] {t}" for t in texts]

    def validate_key(self, api_key: str) -> bool:
        return True


def test_pipeline_cache_hit():
    with tempfile.TemporaryDirectory() as tmp:
        video_path = Path(tmp) / "video.mp4"
        video_path.write_bytes(b"dummy video content" * 100)

        db_path = Path(tmp) / "cache.db"
        cache = SubtitleCache(db_path=db_path)

        cached_cues = [
            {"id": "1", "start": 0.0, "end": 2.0, "originalText": "Hi", "translatedText": "Chào"}
        ]
        from backend.fingerprint import compute_video_fingerprint
        fp = compute_video_fingerprint(str(video_path))
        cache.save_cues(fp, "en", "vi", cached_cues, "video.mp4")

        progress_events = []
        def on_progress(pct: float, step: str):
            progress_events.append((pct, step))

        result = run_subtitling_pipeline(
            video_path=str(video_path),
            source_language="en",
            target_language="vi",
            stt_provider=DummySTT(),
            translation_provider=DummyTranslation(),
            cache=cache,
            on_progress=on_progress,
        )

        assert result == cached_cues
        assert len(progress_events) == 1
        assert progress_events[0][0] == 100.0


def test_pipeline_force_regenerates_cached_subtitles():
    with tempfile.TemporaryDirectory() as tmp:
        video_path = Path(tmp) / "video.mp4"
        video_path.write_bytes(b"dummy video content" * 100)
        cache = SubtitleCache(db_path=Path(tmp) / "cache.db")
        from backend.fingerprint import compute_video_fingerprint
        fingerprint = compute_video_fingerprint(str(video_path))
        cache.save_cues(fingerprint, "en", "vi", [{"id": "old", "start": 0, "end": 1, "originalText": "Cached", "translatedText": "Đã cache"}])
        audio_path = Path(tmp) / "audio.wav"
        audio_path.write_bytes(b"fake wav")

        with patch("backend.pipeline.extract_audio", return_value=audio_path):
            result = run_subtitling_pipeline(
                video_path=str(video_path), source_language="en", target_language="vi",
                stt_provider=DummySTT(), translation_provider=DummyTranslation(), cache=cache, force=True,
            )

        assert result[0]["originalText"] == "Hello world"


def test_pipeline_cache_miss_full_run():
    with tempfile.TemporaryDirectory() as tmp:
        video_path = Path(tmp) / "video.mp4"
        video_path.write_bytes(b"dummy video content" * 100)

        db_path = Path(tmp) / "cache.db"
        cache = SubtitleCache(db_path=db_path)

        dummy_audio = Path(tmp) / "extracted.wav"
        dummy_audio.write_bytes(b"fake wav")

        progress_events = []
        def on_progress(pct: float, step: str):
            progress_events.append((pct, step))

        stt = DummySTT()
        translation = DummyTranslation()
        with patch("backend.pipeline.extract_audio", return_value=dummy_audio):
            result = run_subtitling_pipeline(
                video_path=str(video_path),
                source_language="ja",
                target_language="vi",
                stt_provider=stt,
                translation_provider=translation,
                cache=cache,
                on_progress=on_progress,
            )

        assert len(result) == 2
        assert result[0]["originalText"] == "Hello world"
        assert result[0]["translatedText"] == "[vi] Hello world"
        assert result[1]["originalText"] == "How are you"
        assert result[1]["translatedText"] == "[vi] How are you"
        assert stt.last_language == "ja"
        assert translation.last_source_language == "ja"

        # Check progress events sequence
        pcts = [p[0] for p in progress_events]
        assert pcts[0] == 5.0
        assert pcts[-1] == 100.0

        # Check cached in db
        from backend.fingerprint import compute_video_fingerprint
        fp = compute_video_fingerprint(str(video_path))
        stored = cache.get_cues(fp, "ja", "vi")
        assert stored == result


def test_pipeline_empty_transcription():
    with tempfile.TemporaryDirectory() as tmp:
        video_path = Path(tmp) / "video.mp4"
        video_path.write_bytes(b"dummy video content" * 100)

        cache = SubtitleCache(db_path=Path(tmp) / "cache.db")
        dummy_audio = Path(tmp) / "extracted.wav"
        dummy_audio.write_bytes(b"fake wav")

        with patch("backend.pipeline.extract_audio", return_value=dummy_audio):
            result = run_subtitling_pipeline(
                video_path=str(video_path),
                source_language="en",
                target_language="vi",
                stt_provider=DummySTT(cues=[]),
                translation_provider=DummyTranslation(),
                cache=cache,
            )

        assert result == []


def test_pipeline_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        run_subtitling_pipeline(
            video_path="/nonexistent/video.mp4",
            source_language="en",
            target_language="vi",
            stt_provider=DummySTT(),
            translation_provider=DummyTranslation(),
        )
