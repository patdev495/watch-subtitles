from unittest.mock import MagicMock, patch

from backend.providers import TRANSLATION_PROVIDERS
from backend.providers.google_translate import GoogleTranslateProvider


def test_google_provider_translates_cues_without_an_api_key() -> None:
    response = MagicMock(status_code=200)
    response.json.side_effect = [
        [[["Xin chào", "Hello", None, None]]],
        [[["Tạm biệt", "Goodbye", None, None]]],
    ]
    provider = GoogleTranslateProvider()

    with patch("httpx.get", return_value=response) as get:
        result = provider.translate(["Hello", "Goodbye"], "en", "vi")

    assert result == ["Xin chào", "Tạm biệt"]
    assert get.call_count == 2
    assert get.call_args_list[0].kwargs["params"]["client"] == "gtx"
    assert get.call_args_list[0].kwargs["params"]["sl"] == "en"
    assert get.call_args_list[0].kwargs["params"]["tl"] == "vi"


def test_google_provider_is_registered_alongside_deepl() -> None:
    assert TRANSLATION_PROVIDERS["google"] is GoogleTranslateProvider
