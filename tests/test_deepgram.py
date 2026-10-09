from unittest.mock import patch, MagicMock
import pytest
from backend.providers.deepgram import DeepgramProvider
from backend.providers.base import CueResult


def test_deepgram_transcribe_utterances():
    provider = DeepgramProvider(api_key="test-key")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": {
            "utterances": [
                {
                    "id": "utt-1",
                    "start": 0.5,
                    "end": 2.3,
                    "transcript": "Hello world",
                },
                {
                    "id": "utt-2",
                    "start": 2.5,
                    "end": 4.1,
                    "transcript": "Testing subtitles",
                },
            ]
        }
    }

    with patch("httpx.post", return_value=mock_resp) as mock_post, \
         patch("pathlib.Path.read_bytes", return_value=b"fake-audio-bytes"):
        cues = provider.transcribe("fake_audio.wav", language="en")

    assert len(cues) == 2
    assert cues[0] == CueResult(id="utt-1", start=0.5, end=2.3, original_text="Hello world")
    assert cues[1] == CueResult(id="utt-2", start=2.5, end=4.1, original_text="Testing subtitles")

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "https://api.deepgram.com/v1/listen" in args[0]
    assert kwargs["headers"]["Authorization"] == "Token test-key"
    assert kwargs["params"]["utterances"] == "true"


def test_deepgram_transcribe_empty_key_raises():
    provider = DeepgramProvider(api_key="")
    with pytest.raises(ValueError, match="API key is not configured"):
        provider.transcribe("fake.wav", "en")


def test_deepgram_transcribe_error_status():
    provider = DeepgramProvider(api_key="test-key")
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = "Bad Request"

    with patch("httpx.post", return_value=mock_resp), \
         patch("pathlib.Path.read_bytes", return_value=b"fake-bytes"):
        with pytest.raises(RuntimeError, match="Deepgram transcription failed"):
            provider.transcribe("fake.wav", "en")
