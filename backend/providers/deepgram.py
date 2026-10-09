from typing import Sequence
import httpx
from .base import STTProvider, CueResult


class DeepgramProvider(STTProvider):
    """Deepgram Nova speech-to-text provider."""

    BASE_URL = "https://api.deepgram.com/v1"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def transcribe(self, audio_path: str, language: str) -> Sequence[CueResult]:
        """Send audio to Deepgram and return ordered cue list."""
        # TODO(issue-06): Implement full transcription pipeline
        raise NotImplementedError("Deepgram transcription wired in Issue 06")

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
