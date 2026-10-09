from typing import Any, Sequence

import httpx

from .base import TranslationProvider


class GoogleTranslateProvider(TranslationProvider):
    """Google Translate web endpoint provider; no API credential is required."""

    BASE_URL = "https://translate.googleapis.com/translate_a/single"

    def __init__(self, api_key: str = "") -> None:
        self._api_key = api_key

    def translate(self, texts: Sequence[str], source_language: str, target_language: str) -> Sequence[str]:
        """Translate each cue while preserving its one-to-one correspondence."""
        translated: list[str] = []
        for text in texts:
            if not text:
                translated.append("")
                continue
            response = httpx.get(
                self.BASE_URL,
                params={"client": "gtx", "sl": source_language, "tl": target_language, "dt": "t", "q": text},
                timeout=20.0,
            )
            if response.status_code != 200:
                raise RuntimeError(f"Google Translate failed ({response.status_code}): {response.text}")
            translated.append(self._translation_from_payload(response.json()))
        return translated

    @staticmethod
    def _translation_from_payload(payload: Any) -> str:
        try:
            segments = payload[0]
            result = "".join(segment[0] for segment in segments if isinstance(segment[0], str))
        except (IndexError, KeyError, TypeError):
            result = ""
        if not result:
            raise RuntimeError("Google Translate returned an empty translation.")
        return result

    def validate_key(self, api_key: str) -> bool:
        """Check endpoint reachability; Google Translate does not use an API key here."""
        try:
            self.translate(["test"], "en", "vi")
            return True
        except (httpx.HTTPError, RuntimeError, ValueError):
            return False
