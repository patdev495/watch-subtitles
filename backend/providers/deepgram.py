from io import BytesIO
from pathlib import Path
from typing import Any, Sequence
import wave
import httpx
from .base import STTProvider, CueResult


class DeepgramProvider(STTProvider):
    """Deepgram speech-to-text provider with gap recovery."""

    BASE_URL = "https://api.deepgram.com/v1"
    WORD_PAUSE_SECONDS = 0.5
    MAX_CUE_DURATION_SECONDS = 6.0
    MAX_CUE_TEXT_CHARS = 60
    MAX_CJK_CUE_CHARS = 14
    GAP_RECOVERY_SECONDS = 12.0
    GAP_PADDING_SECONDS = 1.0
    MAX_GAP_REQUESTS = 20
    DETECTED_LANGUAGE_ALIASES = {
        "zh": "zh-CN",
        "zh-hans": "zh-CN",
        "zh-hant": "zh-TW",
    }

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._detected_language: str | None = None

    def transcribe(self, audio_path: str, language: str = "") -> Sequence[CueResult]:
        """Send audio to Deepgram and return ordered cue list."""
        if not self._api_key:
            raise ValueError("Deepgram API key is not configured.")

        data = Path(audio_path).read_bytes()
        base_params = {
            "model": "nova-2",
            "smart_format": "true",
            "utterances": "true",
            "punctuate": "true",
        }
        self._detected_language = None
        if language == "auto":
            detection_response = self._request(data, {**base_params, "detect_language": "true"})
            detected_language = self._language_from_response(detection_response)
            self._detected_language = self._normalise_detected_language(detected_language)
            if not self._detected_language:
                raise RuntimeError("Deepgram could not detect the video's spoken language.")
            res_json = self._request(
                data, {**base_params, "language": self._detected_language}
            )
        elif language:
            res_json = self._request(data, {**base_params, "language": language})
        else:
            res_json = self._request(data, base_params)

        results = res_json.get("results", {})
        if self._detected_language is None:
            self._detected_language = self._language_from_response(res_json)
        cues = self._parse_cues(res_json)
        resolved_language = self._detected_language if language == "auto" else language or "en"
        if not resolved_language:
            return cues
        return self._recover_gaps(data, resolved_language, cues)

    def _parse_cues(self, res_json: dict[str, Any]) -> list[CueResult]:
        results = res_json.get("results", {})
        channels = results.get("channels") or []
        utterances = results.get("utterances") or []

        cues: list[CueResult] = []
        if utterances:
            for idx, utt in enumerate(utterances, start=1):
                word_cues = self._split_utterance_words(utt, idx)
                if word_cues:
                    cues.extend(word_cues)
                    continue

                text = (utt.get("transcript") or "").strip()
                if not text:
                    continue
                cues.append(
                    CueResult(
                        id=str(utt.get("id") or idx),
                        start=round(float(utt.get("start", 0.0)), 2),
                        end=round(float(utt.get("end", 0.0)), 2),
                        original_text=text,
                    )
                )
            return cues

        # Fallback to alternatives if utterances not generated
        if channels:
            alts = channels[0].get("alternatives") or []
            if alts:
                alt = alts[0]
                # Try paragraphs
                paragraphs = alt.get("paragraphs", {}).get("paragraphs", [])
                idx = 1
                for para in paragraphs:
                    for sentence in para.get("sentences", []):
                        stext = (sentence.get("text") or "").strip()
                        if stext:
                            cues.append(
                                CueResult(
                                    id=str(idx),
                                    start=round(float(sentence.get("start", 0.0)), 2),
                                    end=round(float(sentence.get("end", 0.0)), 2),
                                    original_text=stext,
                                )
                            )
                            idx += 1
                if cues:
                    return cues

                # Fallback to single full transcript
                transcript = (alt.get("transcript") or "").strip()
                if transcript:
                    words = alt.get("words") or []
                    start = float(words[0].get("start", 0.0)) if words else 0.0
                    end = float(words[-1].get("end", 0.0)) if words else 0.0
                    return [CueResult(id="1", start=start, end=end, original_text=transcript)]

        return cues

    def _recover_gaps(
        self, data: bytes, language: str, cues: list[CueResult]
    ) -> list[CueResult]:
        """Use Nova-3 only where Nova-2 left a substantial gap in a PCM WAV."""
        try:
            audio = wave.open(BytesIO(data), "rb")
        except (wave.Error, EOFError):
            return cues

        with audio:
            if audio.getcomptype() != "NONE" or audio.getframerate() <= 0:
                return cues
            rate = audio.getframerate()
            duration = audio.getnframes() / rate
            ordered = sorted(cues, key=lambda cue: cue.start)
            boundaries = [(0.0, ordered[0].start)] if ordered else []
            boundaries.extend(
                (left.end, right.start) for left, right in zip(ordered, ordered[1:])
            )
            boundaries.append((ordered[-1].end if ordered else 0.0, duration))
            gaps = sorted(
                ((start, end) for start, end in boundaries if end - start >= self.GAP_RECOVERY_SECONDS),
                key=lambda gap: gap[1] - gap[0],
                reverse=True,
            )[:self.MAX_GAP_REQUESTS]
            recovered: list[CueResult] = []
            for gap_start, gap_end in gaps:
                clip_start = max(0.0, gap_start - self.GAP_PADDING_SECONDS)
                clip_end = min(duration, gap_end + self.GAP_PADDING_SECONDS)
                audio.setpos(int(clip_start * rate))
                frames = audio.readframes(int((clip_end - clip_start) * rate))
                clip = BytesIO()
                with wave.open(clip, "wb") as writer:
                    writer.setparams(audio.getparams())
                    writer.writeframes(frames)
                try:
                    response = self._request(clip.getvalue(), {
                        "model": "nova-3", "language": language,
                        "smart_format": "true", "utterances": "true", "punctuate": "true",
                    })
                except (RuntimeError, httpx.HTTPError):
                    continue
                for cue in self._parse_cues(response):
                    start = round(cue.start + clip_start, 2)
                    end = round(cue.end + clip_start, 2)
                    if end <= start or end <= gap_start or start >= gap_end:
                        continue
                    if any(min(end, item.end) - max(start, item.start) > 0.3 for item in ordered):
                        continue
                    recovered.append(CueResult(
                        id=f"nova3-{int(gap_start * 100)}-{cue.id}",
                        start=start, end=end, original_text=cue.original_text,
                    ))

        return sorted([*cues, *recovered], key=lambda cue: cue.start)

    def _request(self, data: bytes, params: dict[str, str]) -> dict[str, Any]:
        headers = {
            "Authorization": f"Token {self._api_key.strip()}",
            "Content-Type": "audio/wav",
        }
        response = httpx.post(
            f"{self.BASE_URL}/listen",
            params=params,
            headers=headers,
            content=data,
            timeout=120.0,
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Deepgram transcription failed ({response.status_code}): {response.text}"
            )
        return response.json()

    @staticmethod
    def _language_from_response(response: dict[str, Any]) -> str | None:
        results = response.get("results", {})
        channels = results.get("channels") or []
        return (
            results.get("detected_language")
            or (channels[0].get("detected_language") if channels else None)
            or response.get("metadata", {}).get("detected_language")
        )

    @classmethod
    def _normalise_detected_language(cls, language: str | None) -> str | None:
        if not language:
            return None
        return cls.DETECTED_LANGUAGE_ALIASES.get(language.lower(), language)

    def detected_language(self) -> str | None:
        return self._detected_language

    def _split_utterance_words(
        self, utterance: dict[str, Any], utterance_index: int
    ) -> list[CueResult]:
        """Split word-timed speech at substantial pauses for playback cues."""
        words = utterance.get("words") or []
        if not words:
            return []

        segments: list[list[dict[str, float | str]]] = []
        current_segment: list[dict[str, float | str]] = []
        previous_end: float | None = None
        for word in words:
            text = str(word.get("punctuated_word") or word.get("word") or "").strip()
            if not text:
                continue
            start = float(word.get("start", 0.0))
            end = float(word.get("end", start))
            has_speech_pause = (
                bool(current_segment)
                and previous_end is not None
                and start - previous_end > self.WORD_PAUSE_SECONDS
            )
            exceeds_max_duration = (
                bool(current_segment)
                and end - float(current_segment[0]["start"]) > self.MAX_CUE_DURATION_SECONDS
            )
            segment_text = "".join(str(item["text"]) for item in current_segment) + text
            contains_cjk = any("\u4e00" <= char <= "\u9fff" for char in segment_text)
            max_chars = self.MAX_CJK_CUE_CHARS if contains_cjk else self.MAX_CUE_TEXT_CHARS
            exceeds_max_text = bool(current_segment) and len(segment_text) > max_chars
            if has_speech_pause or exceeds_max_duration or exceeds_max_text:
                segments.append(current_segment)
                current_segment = []
            current_segment.append({"text": text, "start": start, "end": end})
            previous_end = end

        if current_segment:
            segments.append(current_segment)

        utterance_id = str(utterance.get("id") or utterance_index)
        return [
            CueResult(
                id=f"{utterance_id}-{segment_index}",
                start=round(float(segment[0]["start"]), 2),
                end=round(float(segment[-1]["end"]), 2),
                original_text=" ".join(str(item["text"]) for item in segment),
            )
            for segment_index, segment in enumerate(segments, start=1)
        ]

    def validate_key(self, api_key: str) -> bool:
        """Ping Deepgram /projects to verify the key is valid."""
        try:
            resp = httpx.get(
                f"{self.BASE_URL}/projects",
                headers={"Authorization": f"Token {api_key.strip()}"},
                timeout=5.0,
            )
            return resp.status_code == 200
        except Exception:
            return False
