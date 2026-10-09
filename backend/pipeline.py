import os
from pathlib import Path
from typing import Callable, Optional, Sequence, Dict, Any
from backend.audio import extract_audio
from backend.cache import SubtitleCache
from backend.fingerprint import compute_video_fingerprint
from backend.providers.base import STTProvider, TranslationProvider, CueResult

ProgressCallback = Callable[[float, str], None]


def run_subtitling_pipeline(
    video_path: str,
    source_language: str,
    target_language: str,
    stt_provider: STTProvider,
    translation_provider: TranslationProvider,
    cache: Optional[SubtitleCache] = None,
    on_progress: Optional[ProgressCallback] = None,
    force: bool = False,
) -> list[Dict[str, Any]]:
    """Execute complete automated subtitling pipeline with progress reporting.

    Stage 0: Cache Check
    Stage 1: Extract Audio Track locally (0% - 20%)
    Stage 2: Deepgram Speech-to-Text API (20% - 60%)
    Stage 3: DeepL Translation API (60% - 90%)
    Stage 4: Assemble finalized Cue objects & write to Subtitle Cache (90% - 100%)
    """
    def report(pct: float, step: str) -> None:
        if on_progress:
            on_progress(pct, step)

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    sub_cache = cache if cache is not None else SubtitleCache()
    fingerprint = compute_video_fingerprint(video_path)

    # ── Stage 0: Cache Check ──────────────────────────────────────────────────
    cached_cues = sub_cache.get_cues(fingerprint, source_language, target_language)
    if cached_cues and not force:
        report(100.0, "Tải từ bộ nhớ đệm (Subtitle Cache) thành công")
        return cached_cues

    # ── Stage 1: Extract Audio Track locally (0% - 20%) ──────────────────────
    report(5.0, "Đang trích xuất luồng âm thanh từ video...")
    audio_path = extract_audio(video_path)
    report(20.0, "Trích xuất âm thanh hoàn tất")

    # ── Stage 2: Deepgram Speech-to-Text API (20% - 60%) ─────────────────────
    report(25.0, "Đang nhận diện giọng nói (STT)...")
    cue_results: Sequence[CueResult] = stt_provider.transcribe(str(audio_path), language=source_language)
    report(60.0, f"Đã nhận diện {len(cue_results)} đoạn thoại")

    if not cue_results:
        report(100.0, "Không tìm thấy đoạn thoại nào trong video")
        return []

    # ── Stage 3: DeepL Translation API (60% - 90%) ───────────────────────────
    report(65.0, f"Đang dịch {len(cue_results)} phụ đề sang '{target_language.upper()}'...")
    original_texts = [cue.original_text for cue in cue_results]
    translated_texts = translation_provider.translate(original_texts, source_language, target_language)
    report(90.0, "Dịch phụ đề hoàn tất")

    # ── Stage 4: Assemble finalized Cue objects & Cache (90% - 100%) ─────────
    report(92.0, "Đang lưu phụ đề vào bộ nhớ đệm...")
    final_cues: list[Dict[str, Any]] = []
    for cue, trans in zip(cue_results, translated_texts):
        final_cues.append({
            "id": cue.id,
            "start": cue.start,
            "end": cue.end,
            "originalText": cue.original_text,
            "translatedText": trans,
        })

    filename = os.path.basename(video_path)
    sub_cache.save_cues(fingerprint, source_language, target_language, final_cues, source_filename=filename)
    report(100.0, "Hoàn thành xử lý phụ đề!")

    return final_cues
