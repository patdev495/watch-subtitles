from unittest.mock import patch, MagicMock
import pytest
from backend.providers.deepl import DeepLProvider


def test_deepl_translate_batches_and_preserves_order():
    provider = DeepLProvider(api_key="mock-key:fx")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "translations": [
            {"text": "Xin chào thế giới"},
            {"text": "Kiểm tra phụ đề"},
        ]
    }

    texts = ["Hello world", "Testing subtitles"]
    with patch("httpx.post", return_value=mock_resp) as mock_post:
        result = provider.translate(texts, source_language="en", target_language="vi")

    assert result == ["Xin chào thế giới", "Kiểm tra phụ đề"]
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "https://api-free.deepl.com/v2/translate" in args[0]
    assert kwargs["headers"]["Authorization"] == "DeepL-Auth-Key mock-key:fx"
    assert kwargs["json"]["text"] == texts
    assert kwargs["json"]["source_lang"] == "EN"
    assert kwargs["json"]["target_lang"] == "VI"


def test_deepl_translate_empty():
    provider = DeepLProvider(api_key="mock-key")
    assert provider.translate([], "en", "vi") == []


def test_deepl_maps_chinese_ui_codes_to_api_codes():
    provider = DeepLProvider(api_key="mock-key:fx")
    response = MagicMock(status_code=200)
    response.json.return_value = {"translations": [{"text": "简体中文"}]}

    with patch("httpx.post", return_value=response) as mock_post:
        provider.translate(["繁體中文"], source_language="zh-TW", target_language="zh-CN")

    assert mock_post.call_args.kwargs["json"]["source_lang"] == "ZH"
    assert mock_post.call_args.kwargs["json"]["target_lang"] == "ZH-HANS"


def test_deepl_translate_missing_key():
    provider = DeepLProvider(api_key="")
    with pytest.raises(ValueError, match="API key is not configured"):
        provider.translate(["Hello"], "en", "vi")
