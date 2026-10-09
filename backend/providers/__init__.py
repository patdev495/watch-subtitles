"""Provider registry. Maps string names -> concrete provider classes.

Adding a new provider:
  1. Create a concrete class implementing STTProvider or TranslationProvider.
  2. Register it here.
"""
from .base import STTProvider, TranslationProvider, TTSProvider
from .deepgram import DeepgramProvider
from .deepl import DeepLProvider

STT_PROVIDERS: dict[str, type[STTProvider]] = {
    "deepgram": DeepgramProvider,
}

TRANSLATION_PROVIDERS: dict[str, type[TranslationProvider]] = {
    "deepl": DeepLProvider,
}

TTS_PROVIDERS: dict[str, type[TTSProvider]] = {}


def register_stt_provider(name: str, cls: type[STTProvider]) -> None:
    STT_PROVIDERS[name] = cls


def register_translation_provider(name: str, cls: type[TranslationProvider]) -> None:
    TRANSLATION_PROVIDERS[name] = cls


def register_tts_provider(name: str, cls: type[TTSProvider]) -> None:
    TTS_PROVIDERS[name] = cls


__all__ = [
    "STTProvider",
    "TranslationProvider",
    "TTSProvider",
    "DeepgramProvider",
    "DeepLProvider",
    "STT_PROVIDERS",
    "TRANSLATION_PROVIDERS",
    "TTS_PROVIDERS",
    "register_stt_provider",
    "register_translation_provider",
    "register_tts_provider",
]

