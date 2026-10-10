import os
import threading
import json
from typing import Optional, Dict, Any
from urllib.parse import quote
import webview
from pydantic import BaseModel
from backend.settings import AppSettings, load_settings, save_settings as persist_settings
from backend.providers import STT_PROVIDERS, TRANSLATION_PROVIDERS, TTS_PROVIDERS
from backend.fingerprint import compute_video_fingerprint
from backend.cache import SubtitleCache
from backend.audio import extract_audio
from backend.pipeline import run_subtitling_pipeline
from backend.export import format_srt, format_vtt
from backend.jobs import DuplicateActiveJobError, JobRunner, SubtitleJob, SubtitleJobScheduler


STT_API_KEY_FIELDS: dict[str, str] = {
    "deepgram": "deepgram_api_key",
    "assemblyai": "assemblyai_api_key",
}


def _stt_api_key(settings: AppSettings, provider_name: str) -> str:
    """Return the credential assigned to a configured transcription provider."""
    field_name = STT_API_KEY_FIELDS.get(provider_name)
    return str(getattr(settings, field_name, "")) if field_name else ""

class PingResponse(BaseModel):
    status: str
    message: str

class VideoDialogResponse(BaseModel):
    cancelled: bool
    path: Optional[str] = None
    filename: Optional[str] = None
    stream_url: Optional[str] = None

class BridgeApi:
    def __init__(
        self, port: int, cache: Optional[SubtitleCache] = None, job_runner: Optional[JobRunner] = None
    ) -> None:
        self.port: int = port
        self._cache: SubtitleCache = cache if cache is not None else SubtitleCache()
        # Prefix with underscore so pywebview's js_api dir() introspector skips
        # this attribute. Without underscore, pywebview recurses into the webview
        # Window → native COM object from a non-UI thread, causing the
        # "CoreWebView2Controller members can only be accessed from the UI thread"
        # spam and AccessibilityObject errors on Windows.
        self._window: Optional[webview.Window] = None
        self._pipeline_state: Dict[str, Any] = {
            "status": "idle",
            "progress": 0.0,
            "step": "",
            "cues": [],
            "error": None,
        }
        self._pipeline_lock = threading.Lock()
        self._job_scheduler = SubtitleJobScheduler(job_runner or self._run_subtitle_job, self._emit_job_progress)

    def set_window(self, window: webview.Window) -> None:
        self._window = window

    def ping(self) -> Dict[str, Any]:
        """Verify Python backend and pywebview bridge connectivity."""
        return PingResponse(status="ok", message="Python UV backend ready").model_dump()

    def open_video_dialog(self) -> Dict[str, Any]:
        """Open native OS file dialog to select video file."""
        if not self._window:
            return VideoDialogResponse(cancelled=True).model_dump()

        file_types = (
            "Video Files (*.mp4;*.mkv;*.webm;*.avi;*.mov;*.flv;*.wmv;*.m4v)",
            "All Files (*.*)"
        )
        result = self._window.create_file_dialog(
            dialog_type=webview.FileDialog.OPEN,
            allow_multiple=False,
            file_types=file_types
        )

        if not result or len(result) == 0:
            return VideoDialogResponse(cancelled=True).model_dump()

        file_path = result[0]
        if not os.path.exists(file_path):
            return VideoDialogResponse(cancelled=True).model_dump()

        filename = os.path.basename(file_path)
        encoded_path = quote(file_path)
        stream_url = f"http://127.0.0.1:{self.port}/stream?path={encoded_path}"

        return VideoDialogResponse(
            cancelled=False,
            path=file_path,
            filename=filename,
            stream_url=stream_url
        ).model_dump()

    def load_video_path(self, file_path: str) -> Dict[str, Any]:
        """Resolve dropped or provided video path into stream URL."""
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return VideoDialogResponse(cancelled=True).model_dump()

        filename = os.path.basename(file_path)
        encoded_path = quote(file_path)
        stream_url = f"http://127.0.0.1:{self.port}/stream?path={encoded_path}"

        return VideoDialogResponse(
            cancelled=False,
            path=file_path,
            filename=filename,
            stream_url=stream_url
        ).model_dump()

    # ── Settings ────────────────────────────────────────────────────────────────

    def get_settings(self) -> Dict[str, Any]:
        """Return persisted AppSettings as a plain dict for the frontend."""
        return load_settings().model_dump()

    def save_settings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Persist settings from frontend. Returns saved settings for confirmation."""
        settings = AppSettings(**data)
        persist_settings(settings)
        return settings.model_dump()

    def test_connection(self, provider_type: str, provider_name: str, api_key: str) -> Dict[str, Any]:
        """Validate API key for a named provider. provider_type: 'stt' | 'translation'."""
        try:
            if provider_type == "stt":
                cls = STT_PROVIDERS.get(provider_name)
            elif provider_type == "translation":
                cls = TRANSLATION_PROVIDERS.get(provider_name)
            elif provider_type == "tts":
                cls = TTS_PROVIDERS.get(provider_name)
            else:
                return {"ok": False, "message": f"Unknown provider_type: {provider_type}"}

            if cls is None:
                return {"ok": False, "message": f"Provider '{provider_name}' not registered"}

            provider = cls(api_key)
            valid = provider.validate_key(api_key)
            return {"ok": valid, "message": "Connected" if valid else "Invalid API key"}
        except Exception as exc:
            return {"ok": False, "message": str(exc)}

    # ── Fingerprint, Cache & Audio Extraction ────────────────────────────────────

    def get_video_fingerprint(self, video_path: str) -> Dict[str, Any]:
        """Compute content hash for video file."""
        try:
            fp = compute_video_fingerprint(video_path)
            return {"ok": True, "fingerprint": fp}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def get_cached_subtitles(self, video_path: str, source_language: str, target_language: str) -> Dict[str, Any]:
        """Check cache for existing transcript/translation of this video."""
        try:
            fp = compute_video_fingerprint(video_path)
            cues = self._cache.get_cues(fp, source_language, target_language)
            return {
                "ok": True,
                "cached": cues is not None,
                "fingerprint": fp,
                "cues": cues or [],
            }
        except Exception as exc:
            return {"ok": False, "cached": False, "error": str(exc), "cues": []}

    def get_cached_subtitle_languages(self, video_path: str) -> Dict[str, Any]:
        """Return all cached language pairs for a video."""
        try:
            fingerprint = compute_video_fingerprint(video_path)
            return {"ok": True, "language_pairs": self._cache.list_cached_languages(fingerprint)}
        except Exception as exc:
            return {"ok": False, "language_pairs": [], "error": str(exc)}

    def save_cached_subtitles(
        self, video_path: str, source_language: str, target_language: str, cues: list
    ) -> Dict[str, Any]:
        """Persist generated cues into SQLite cache."""
        try:
            fp = compute_video_fingerprint(video_path)
            filename = os.path.basename(video_path)
            self._cache.save_cues(fp, source_language, target_language, cues, source_filename=filename)
            return {"ok": True, "fingerprint": fp}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def extract_video_audio(self, video_path: str) -> Dict[str, Any]:
        """Extract audio stream from video using local FFmpeg."""
        try:
            audio_path = extract_audio(video_path)
            return {"ok": True, "audio_path": str(audio_path)}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    # ── Subtitle Jobs ───────────────────────────────────────────────────────────

    def create_subtitle_job(
        self, video_path: str, source_language: str, target_language: str, force: bool = False
    ) -> Dict[str, Any]:
        """Queue one Subtitle Job, optionally discarding its cached language pair first."""
        if not os.path.isfile(video_path):
            return {"ok": False, "error": f"Video file not found: {video_path}"}
        job = SubtitleJob(
            video_path=video_path,
            source_language=source_language,
            target_language=target_language,
            force=force,
        )
        try:
            fingerprint = compute_video_fingerprint(video_path)
            if force:
                self._cache.delete_cues(fingerprint, source_language, target_language)
            cached_cues = self._cache.get_cues(fingerprint, source_language, target_language)
            if cached_cues is not None:
                completed = self._job_scheduler.complete_from_cache(job, cached_cues)
                return {"ok": True, "job": completed.model_dump()}
            queued = self._job_scheduler.enqueue(job)
            return {"ok": True, "job": queued.model_dump()}
        except DuplicateActiveJobError as exc:
            return {"ok": False, "error": str(exc), "duplicate": True}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def get_subtitle_job(self, job_id: str) -> Dict[str, Any]:
        """Return isolated state for one Subtitle Job."""
        job = self._job_scheduler.get(job_id)
        if not job:
            return {"ok": False, "error": "Subtitle Job not found"}
        return {"ok": True, "job": job.model_dump()}

    def list_subtitle_jobs(self) -> Dict[str, Any]:
        """Return all jobs in their creation order for Queue Screen rendering."""
        return {"ok": True, "jobs": [job.model_dump() for job in self._job_scheduler.list()]}

    def remove_subtitle_job(self, job_id: str) -> Dict[str, Any]:
        """Remove a waiting job. Processing jobs deliberately cannot be removed."""
        job = self._job_scheduler.cancel_waiting(job_id)
        if not job:
            return {"ok": False, "error": "Chỉ Subtitle Job đang chờ mới có thể xóa."}
        return {"ok": True, "job": job.model_dump()}

    def retry_subtitle_job(self, job_id: str) -> Dict[str, Any]:
        """Append a replacement job using a failed Job's original language pair."""
        failed_job = self._job_scheduler.get(job_id)
        if not failed_job or failed_job.status != "failed":
            return {"ok": False, "error": "Chỉ Subtitle Job thất bại mới có thể thử lại."}
        return self.create_subtitle_job(
            failed_job.video_path, failed_job.source_language, failed_job.target_language
        )

    def _run_subtitle_job(self, job: SubtitleJob, on_progress: Any) -> list[Dict[str, Any]]:
        settings = load_settings()
        stt_name = settings.stt_provider or "deepgram"
        trans_name = settings.translation_provider or "deepl"
        stt_cls = STT_PROVIDERS.get(stt_name)
        trans_cls = TRANSLATION_PROVIDERS.get(trans_name)
        if not stt_cls or not trans_cls:
            raise RuntimeError("Transcription hoặc Translation Provider chưa được đăng ký")
        stt_key = _stt_api_key(settings, stt_name)
        trans_key = settings.deepl_api_key if trans_name == "deepl" else ""
        if not stt_key or (trans_name == "deepl" and not trans_key):
            raise RuntimeError("Chưa cấu hình API key cho Transcription hoặc Translation Provider.")
        return run_subtitling_pipeline(
            video_path=job.video_path,
            source_language=job.source_language,
            target_language=job.target_language,
            stt_provider=stt_cls(stt_key),
            translation_provider=trans_cls(trans_key),
            cache=self._cache,
            on_progress=on_progress,
            force=job.force,
        )

    def _emit_job_progress(self, job: Dict[str, Any]) -> None:
        if not self._window:
            return
        try:
            payload = json.dumps(job)
            self._window.evaluate_js(
                f"window.dispatchEvent(new CustomEvent('subtitle-job-progress', {{ detail: {payload} }}));"
            )
        except Exception:
            pass

    # ── Subtitle Export ──────────────────────────────────────────────────────────

    def export_subtitles(
        self,
        cues: list,
        fmt: str = "srt",
        layout: str = "bilingual",
    ) -> Dict[str, Any]:
        """Format cues and write to a user-chosen file via native Save-As dialog.

        Args:
            cues:   list of cue dicts from the frontend (camelCase keys).
            fmt:    ``'srt'`` or ``'vtt'``.
            layout: ``'bilingual'`` | ``'original'`` | ``'translated'``.

        Returns:
            ``{ok: True, path: <saved_path>}`` or ``{ok: False, error: str}``.
        """
        if not cues:
            return {"ok": False, "error": "Không có phụ đề nào để xuất."}

        fmt = (fmt or "srt").lower().strip()
        if fmt not in ("srt", "vtt"):
            return {"ok": False, "error": f"Định dạng không hợp lệ: {fmt!r}"}

        try:
            if fmt == "srt":
                content = format_srt(cues, layout=layout)
                ext = "srt"
                description = "SubRip Subtitle Files (*.srt)"
            else:
                content = format_vtt(cues, layout=layout)
                ext = "vtt"
                description = "WebVTT Subtitle Files (*.vtt)"
        except Exception as exc:
            return {"ok": False, "error": f"Lỗi khi tạo nội dung subtitle: {exc}"}

        # Native Save-As dialog via pywebview
        if self._window:
            try:
                save_filename = f"subtitles.{ext}"
                result = self._window.create_file_dialog(
                    dialog_type=webview.SAVE_DIALOG,
                    directory="",
                    save_filename=save_filename,
                    file_types=(description, "All Files (*.*)"),
                )
                if not result:
                    return {"ok": False, "error": "Người dùng hủy hộp thoại lưu."}
                save_path: str = result if isinstance(result, str) else result[0]
            except Exception as exc:
                return {"ok": False, "error": f"Lỗi hộp thoại lưu file: {exc}"}
        else:
            # Headless / test mode: write to temp
            import tempfile
            tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=f".{ext}", delete=False, encoding="utf-8"
            )
            save_path = tmp.name
            tmp.close()

        try:
            with open(save_path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(content)
            return {"ok": True, "path": save_path}
        except Exception as exc:
            return {"ok": False, "error": f"Lỗi ghi file: {exc}"}

    # ── Pipeline Generation ──────────────────────────────────────────────────────

    def start_subtitles_pipeline(self, video_path: str, source_language: str, target_language: str, force: bool = False) -> Dict[str, Any]:
        """Launch subtitling pipeline asynchronously in background thread."""
        if not os.path.exists(video_path):
            return {"ok": False, "error": f"Video file not found: {video_path}"}

        settings = load_settings()
        stt_name = settings.stt_provider or "deepgram"
        trans_name = settings.translation_provider or "deepl"

        stt_cls = STT_PROVIDERS.get(stt_name)
        if not stt_cls:
            return {"ok": False, "error": f"STT Provider '{stt_name}' not registered"}

        trans_cls = TRANSLATION_PROVIDERS.get(trans_name)
        if not trans_cls:
            return {"ok": False, "error": f"Translation Provider '{trans_name}' not registered"}

        # Check API keys
        stt_key = _stt_api_key(settings, stt_name)
        if not stt_key:
            return {"ok": False, "error": "Chưa cấu hình API key cho Transcription Provider trong Cài đặt."}

        trans_key = settings.deepl_api_key if trans_name == "deepl" else ""
        if trans_name == "deepl" and not trans_key:
            return {"ok": False, "error": "Chưa cấu hình API key cho DeepL trong Cài đặt."}

        stt_provider = stt_cls(stt_key)
        trans_provider = trans_cls(trans_key)

        with self._pipeline_lock:
            self._pipeline_state = {
                "status": "running",
                "progress": 0.0,
                "step": "Đang khởi tạo quy trình...",
                "cues": [],
                "error": None,
            }

        worker_thread = threading.Thread(
            target=self._run_pipeline_worker,
            args=(video_path, source_language, target_language, stt_provider, trans_provider, force),
            daemon=True,
        )
        worker_thread.start()

        return {"ok": True, "message": "Pipeline started"}

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Query current state of running subtitle pipeline."""
        with self._pipeline_lock:
            return dict(self._pipeline_state)

    def _emit_progress_to_window(self, state: Dict[str, Any]) -> None:
        """Deliver progress event into WebView2 UI thread safely."""
        if not self._window:
            return
        try:
            payload_json = json.dumps(state)
            js_code = (
                f"window.dispatchEvent(new CustomEvent('pipeline-progress', "
                f"{{ detail: {payload_json} }}));"
            )
            self._window.evaluate_js(js_code)
        except Exception:
            pass

    def _run_pipeline_worker(
        self,
        video_path: str,
        source_language: str,
        target_language: str,
        stt_provider: Any,
        trans_provider: Any,
        force: bool,
    ) -> None:
        """Background execution worker for subtitle pipeline."""
        def on_progress(pct: float, step: str) -> None:
            with self._pipeline_lock:
                self._pipeline_state["progress"] = pct
                self._pipeline_state["step"] = step
                curr_state = dict(self._pipeline_state)
            self._emit_progress_to_window(curr_state)

        try:
            cues = run_subtitling_pipeline(
                video_path=video_path,
                source_language=source_language,
                target_language=target_language,
                stt_provider=stt_provider,
                translation_provider=trans_provider,
                cache=self._cache,
                on_progress=on_progress,
                force=force,
            )
            with self._pipeline_lock:
                self._pipeline_state["status"] = "completed"
                self._pipeline_state["progress"] = 100.0
                self._pipeline_state["step"] = "Hoàn thành!"
                self._pipeline_state["cues"] = cues
                curr_state = dict(self._pipeline_state)
            self._emit_progress_to_window(curr_state)
        except Exception as exc:
            with self._pipeline_lock:
                self._pipeline_state["status"] = "error"
                self._pipeline_state["error"] = str(exc)
                self._pipeline_state["step"] = f"Lỗi: {exc}"
                curr_state = dict(self._pipeline_state)
            self._emit_progress_to_window(curr_state)
