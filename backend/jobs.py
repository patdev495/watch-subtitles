"""In-memory scheduling for subtitle generation jobs."""

from __future__ import annotations

import threading
from collections import deque
from collections.abc import Callable
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


JobStatus = Literal["waiting", "processing", "completed", "failed", "cancelled"]
ProgressReporter = Callable[[float, str], None]
JobRunner = Callable[["SubtitleJob", ProgressReporter], list[dict[str, Any]]]
JobChangeHandler = Callable[[dict[str, Any]], None]


class SubtitleJob(BaseModel):
    """One language-specific subtitle request for a Video."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    video_path: str
    source_language: str
    target_language: str
    status: JobStatus = "waiting"
    progress: float = 0.0
    step: str = "Đang chờ xử lý"
    cues: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None
    cached: bool = False

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.video_path, self.source_language, self.target_language)


class DuplicateActiveJobError(ValueError):
    """Raised when an active job already owns a video-language pair."""


class SubtitleJobScheduler:
    """FIFO scheduler that protects each job's state from other jobs."""

    def __init__(self, runner: JobRunner, on_change: JobChangeHandler | None = None) -> None:
        self._runner = runner
        self._on_change = on_change
        self._jobs: dict[str, SubtitleJob] = {}
        self._waiting: deque[str] = deque()
        self._lock = threading.Lock()
        self._processing = False

    def enqueue(self, job: SubtitleJob) -> SubtitleJob:
        with self._lock:
            if any(
                existing.key == job.key and existing.status in {"waiting", "processing"}
                for existing in self._jobs.values()
            ):
                raise DuplicateActiveJobError("Video này đã có Subtitle Job đang chờ hoặc đang xử lý cho cặp ngôn ngữ đã chọn.")
            self._jobs[job.id] = job
            self._waiting.append(job.id)
            self._notify_locked(job)
            if not self._processing:
                self._processing = True
                threading.Thread(target=self._process_waiting, daemon=True).start()
            return job.model_copy(deep=True)

    def complete_from_cache(self, job: SubtitleJob, cues: list[dict[str, Any]]) -> SubtitleJob:
        job.status = "completed"
        job.progress = 100.0
        job.step = "Tải từ Subtitle Cache thành công"
        job.cues = cues
        job.cached = True
        with self._lock:
            self._jobs[job.id] = job
            self._notify_locked(job)
            return job.model_copy(deep=True)

    def get(self, job_id: str) -> SubtitleJob | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return job.model_copy(deep=True) if job else None

    def list(self) -> list[SubtitleJob]:
        with self._lock:
            return [job.model_copy(deep=True) for job in self._jobs.values()]

    def cancel_waiting(self, job_id: str) -> SubtitleJob | None:
        """Cancel only waiting work; a running Job is intentionally immutable."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job.status != "waiting":
                return None
            self._waiting = deque(queued_id for queued_id in self._waiting if queued_id != job_id)
            job.status = "cancelled"
            job.step = "Đã xóa khỏi hàng đợi"
            self._notify_locked(job)
            return job.model_copy(deep=True)

    def _process_waiting(self) -> None:
        while True:
            with self._lock:
                if not self._waiting:
                    self._processing = False
                    return
                job = self._jobs[self._waiting.popleft()]
                job.status = "processing"
                job.step = "Đang khởi tạo quy trình..."
                self._notify_locked(job)

            def report(progress: float, step: str) -> None:
                with self._lock:
                    job.progress = progress
                    job.step = step
                    self._notify_locked(job)

            try:
                cues = self._runner(job, report)
                with self._lock:
                    job.status = "completed"
                    job.progress = 100.0
                    job.step = "Hoàn thành!"
                    job.cues = cues
                    self._notify_locked(job)
            except Exception as exc:
                with self._lock:
                    job.status = "failed"
                    job.error = str(exc)
                    job.step = f"Lỗi: {exc}"
                    self._notify_locked(job)

    def _notify_locked(self, job: SubtitleJob) -> None:
        if self._on_change:
            self._on_change(job.model_dump())
