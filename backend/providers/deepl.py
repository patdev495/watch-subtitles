from typing import Sequence
import httpx
from .base import TranslationProvider


class DeepLProvider(TranslationProvider):
    """DeepL translation provider."""

    BASE_URL = "https://api-free.deepl.com/v2"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def translate(self, texts: Sequence[str], target_language: str) -> Sequence[str]:
        """Translate batch of texts via DeepL API."""
        # TODO(issue-06): Implement full translation pipeline
        raise NotImplementedError("DeepL translation wired in Issue 06")

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
