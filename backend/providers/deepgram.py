from pathlib import Path
from typing import Sequence
import httpx
from .base import STTProvider, CueResult


class DeepgramProvider(STTProvider):
    """Deepgram Nova speech-to-text provider."""

    BASE_URL = "https://api.deepgram.com/v1"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def transcribe(self, audio_path: str, language: str = "") -> Sequence[CueResult]:
        """Send audio to Deepgram and return ordered cue list."""
        if not self._api_key:
            raise ValueError("Deepgram API key is not configured.")

        data = Path(audio_path).read_bytes()
        params = {
            "model": "nova-2",
            "smart_format": "true",
            "utterances": "true",
            "punctuate": "true",
        }
        if language:
            params["language"] = language

        headers = {
            "Authorization": f"Token {self._api_key.strip()}",
            "Content-Type": "audio/wav",
        }

        resp = httpx.post(
            f"{self.BASE_URL}/listen",
            params=params,
            headers=headers,
            content=data,
            timeout=120.0,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Deepgram transcription failed ({resp.status_code}): {resp.text}")

        res_json = resp.json()
        results = res_json.get("results", {})
        utterances = results.get("utterances") or []

        cues: list[CueResult] = []
        if utterances:
            for idx, utt in enumerate(utterances, start=1):
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
        channels = results.get("channels") or []
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
