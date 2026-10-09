from typing import Sequence
import httpx
from .base import TranslationProvider


class DeepLProvider(TranslationProvider):
    """DeepL translation provider."""

    BASE_URL = "https://api-free.deepl.com/v2"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def translate(self, texts: Sequence[str], source_language: str, target_language: str) -> Sequence[str]:
        """Translate batch of texts via DeepL API preserving sentence boundaries."""
        if not texts:
            return []

        if not self._api_key:
            raise ValueError("DeepL API key is not configured.")

        base_url = "https://api-free.deepl.com/v2" if self._api_key.strip().endswith(":fx") else "https://api.deepl.com/v2"
        target_code = target_language.strip().lower()
        target_lang = {
            "en": "EN-US",
            "vi": "VI",
            "zh-cn": "ZH-HANS",
            "zh-tw": "ZH-HANT",
        }.get(target_code, target_code.upper())
        source_code = source_language.strip().lower()
        source_lang = "ZH" if source_code in {"zh-cn", "zh-tw"} else source_code.upper()

        headers = {
            "Authorization": f"DeepL-Auth-Key {self._api_key.strip()}",
            "Content-Type": "application/json",
        }

        # DeepL accepts up to 50 texts per request
        batch_size = 50
        translated: list[str] = []

        for i in range(0, len(texts), batch_size):
            batch = list(texts[i : i + batch_size])
            resp = httpx.post(
                f"{base_url}/translate",
                headers=headers,
                json={"text": batch, "source_lang": source_lang, "target_lang": target_lang},
                timeout=60.0,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"DeepL translation failed ({resp.status_code}): {resp.text}")

            data = resp.json()
            translations = data.get("translations", [])
            for item in translations:
                translated.append(item.get("text", ""))

        return translated

    def validate_key(self, api_key: str) -> bool:
        """Ping DeepL /usage to verify the key is valid (supports Free and Pro keys)."""
        base_url = "https://api-free.deepl.com/v2" if api_key.strip().endswith(":fx") else "https://api.deepl.com/v2"
        try:
            resp = httpx.get(
                f"{base_url}/usage",
                headers={"Authorization": f"DeepL-Auth-Key {api_key.strip()}"},
                timeout=5.0,
            )
            return resp.status_code == 200
        except Exception:
            return False
