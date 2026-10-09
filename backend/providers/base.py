from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence


@dataclass
class CueResult:
    """A single transcribed speech segment with timing."""
    id: str
    start: float  # seconds
    end: float    # seconds
    original_text: str


class STTProvider(ABC):
    """Abstract speech-to-text provider. Swap implementations without changing callers."""

    @abstractmethod
    def transcribe(self, audio_path: str, language: str) -> Sequence[CueResult]:
        """Transcribe audio file -> ordered cue list."""
        ...

    @abstractmethod
    def validate_key(self, api_key: str) -> bool:
        """Lightweight credential check. Returns True if key appears valid."""
        ...


TranscriptionProvider = STTProvider


class TranslationProvider(ABC):
    """Abstract translation provider. Swap implementations without changing callers."""

    @abstractmethod
    def translate(self, texts: Sequence[str], source_language: str, target_language: str) -> Sequence[str]:
        """Translate a batch of strings. Returns same-length list of translated strings."""
        ...

    @abstractmethod
    def validate_key(self, api_key: str) -> bool:
        """Lightweight credential check. Returns True if key appears valid."""
        ...


class TTSProvider(ABC):
    """Abstract text-to-speech provider. Swap implementations without changing callers."""

    @abstractmethod
    def synthesize(self, text: str, output_path: str, voice: str | None = None) -> str:
        """Synthesize text to audio file. Returns path to output audio."""
        ...

    @abstractmethod
    def validate_key(self, api_key: str) -> bool:
        """Lightweight credential check. Returns True if key appears valid."""
        ...
