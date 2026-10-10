"""AssemblyAI implementation of the application's transcription provider seam."""

from pathlib import Path
import time
from typing import Any, Sequence

import httpx

from .base import CueResult, STTProvider


class AssemblyAIProvider(STTProvider):
    """Transcribe a local Audio Track through AssemblyAI's pre-recorded API."""

    BASE_URL = "https://api.assemblyai.com/v2"
    MODEL = "universal-3-5-pro"
    REQUEST_TIMEOUT_SECONDS = 30.0
    POLL_INTERVAL_SECONDS = 3.0
    MAX_RETRIES = 3
    WORD_PAUSE_SECONDS = 0.5
    MAX_CUE_DURATION_SECONDS = 6.0
    MAX_CUE_TEXT_CHARS = 60
    MAX_CJK_CUE_CHARS = 14

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._detected_language: str | None = None

    def transcribe(self, audio_path: str, language: str = "") -> Sequence[CueResult]:
        if not self._api_key:
            raise ValueError("AssemblyAI API key is not configured.")

        self._detected_language = None
        upload = self._post(
            f"{self.BASE_URL}/upload",
            headers=self._headers("application/octet-stream"),
            content=Path(audio_path).read_bytes(),
        )
        upload_url = str(upload.get("upload_url") or "")
        if not upload_url:
            raise RuntimeError("AssemblyAI upload response did not include upload_url.")

        request_body: dict[str, Any] = {
            "audio_url": upload_url,
            "speech_models": [self.MODEL],
            "speaker_labels": False,
        }
        if language == "auto":
            request_body["language_detection"] = True
        elif language:
            request_body["language_code"] = self._to_assemblyai_language(language)

        submitted = self._post(
            f"{self.BASE_URL}/transcript",
            headers=self._headers("application/json"),
            json=request_body,
        )
        transcript_id = str(submitted.get("id") or "")
        if not transcript_id:
            raise RuntimeError("AssemblyAI transcript response did not include an id.")

        completed = self._poll_transcript(transcript_id)
        if language == "auto":
            self._detected_language = self._normalise_detected_language(
                completed.get("language_code")
            )
            if not self._detected_language:
                raise RuntimeError("AssemblyAI could not detect the video's spoken language.")
        return self._build_cues(completed.get("words") or [])

    def validate_key(self, api_key: str) -> bool:
        if not api_key.strip():
            return False
        try:
            response = httpx.get(
                f"{self.BASE_URL}/transcript?limit=1",
                headers={"Authorization": api_key.strip()},
                timeout=self.REQUEST_TIMEOUT_SECONDS,
            )
            return 200 <= response.status_code < 300
        except httpx.HTTPError:
            return False

    def detected_language(self) -> str | None:
        return self._detected_language

    def _poll_transcript(self, transcript_id: str) -> dict[str, Any]:
        while True:
            transcript = self._get(
                f"{self.BASE_URL}/transcript/{transcript_id}", headers=self._headers()
            )
            status = transcript.get("status")
            if status == "completed":
                return transcript
            if status == "error":
                raise RuntimeError(
                    f"AssemblyAI transcription failed: {transcript.get('error') or 'Unknown error'}"
                )
            if status not in {"queued", "processing"}:
                raise RuntimeError(f"AssemblyAI returned an unknown transcription status: {status!r}")
            time.sleep(self.POLL_INTERVAL_SECONDS)

    def _post(self, url: str, **kwargs: Any) -> dict[str, Any]:
        return self._request(lambda: httpx.post(url, timeout=self.REQUEST_TIMEOUT_SECONDS, **kwargs))

    def _get(self, url: str, **kwargs: Any) -> dict[str, Any]:
        return self._request(lambda: httpx.get(url, timeout=self.REQUEST_TIMEOUT_SECONDS, **kwargs))

    def _request(self, send: Any) -> dict[str, Any]:
        last_error: str = "Unknown request error"
        for attempt in range(self.MAX_RETRIES):
            try:
                response = send()
                if 200 <= response.status_code < 300:
                    payload = response.json()
                    return payload if isinstance(payload, dict) else {}
                last_error = f"HTTP {response.status_code}: {response.text}"
                if response.status_code not in {429, 500, 502, 503, 504}:
                    break
            except httpx.HTTPError as exc:
                last_error = str(exc)
            if attempt < self.MAX_RETRIES - 1:
                time.sleep(2**attempt)
        raise RuntimeError(f"AssemblyAI request failed: {last_error}")

    def _headers(self, content_type: str | None = None) -> dict[str, str]:
        headers = {"Authorization": self._api_key.strip()}
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    @staticmethod
    def _to_assemblyai_language(language: str) -> str:
        return "zh" if language in {"zh-CN", "zh-TW"} else language

    @staticmethod
    def _normalise_detected_language(language: object) -> str | None:
        if not isinstance(language, str) or not language:
            return None
        return "zh-CN" if language.lower() == "zh" else language

    @classmethod
    def _build_cues(cls, words: list[dict[str, Any]]) -> list[CueResult]:
        segments: list[list[dict[str, Any]]] = []
        current: list[dict[str, Any]] = []
        previous_end: float | None = None
        for word in words:
            text = str(word.get("text") or "").strip()
            if not text:
                continue
            start = float(word.get("start", 0.0)) / 1000
            end = float(word.get("end", start * 1000)) / 1000
            current_text = " ".join(str(item["text"]) for item in current)
            candidate = f"{current_text} {text}".strip()
            contains_cjk = any("\u4e00" <= char <= "\u9fff" for char in candidate)
            max_chars = cls.MAX_CJK_CUE_CHARS if contains_cjk else cls.MAX_CUE_TEXT_CHARS
            should_split = bool(current) and (
                (previous_end is not None and start - previous_end > cls.WORD_PAUSE_SECONDS)
                or end - float(current[0]["start"]) > cls.MAX_CUE_DURATION_SECONDS
                or len(candidate) > max_chars
            )
            if should_split:
                segments.append(current)
                current = []
            current.append({"text": text, "start": start, "end": end})
            previous_end = end
        if current:
            segments.append(current)

        return [
            CueResult(
                id=str(index),
                start=round(float(segment[0]["start"]), 2),
                end=round(float(segment[-1]["end"]), 2),
                original_text=" ".join(str(item["text"]) for item in segment),
            )
            for index, segment in enumerate(segments, start=1)
        ]
