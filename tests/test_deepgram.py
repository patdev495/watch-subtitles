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
    assert kwargs["params"]["model"] == "nova-3"
    assert kwargs["params"]["utterances"] == "true"


def test_deepgram_transcribe_empty_key_raises():
    provider = DeepgramProvider(api_key="")
    with pytest.raises(ValueError, match="API key is not configured"):
        provider.transcribe("fake.wav", "en")


def test_deepgram_auto_detects_then_transcribes_using_the_detected_language():
    provider = DeepgramProvider(api_key="test-key")
    detection_response = MagicMock()
    detection_response.status_code = 200
    detection_response.json.return_value = {
        "results": {
            "channels": [{"detected_language": "zh", "alternatives": []}],
            "utterances": [],
        }
    }
    transcription_response = MagicMock()
    transcription_response.status_code = 200
    transcription_response.json.return_value = {
        "results": {
            "utterances": [
                {"id": "zh-1", "start": 0.5, "end": 2.0, "transcript": "你好"},
            ],
        },
    }

    with patch("httpx.post", side_effect=[detection_response, transcription_response]) as mock_post, patch(
        "pathlib.Path.read_bytes", return_value=b"fake-audio-bytes"
    ):
        cues = provider.transcribe("fake_audio.wav", language="auto")

    assert mock_post.call_count == 2
    assert mock_post.call_args_list[0].kwargs["params"]["detect_language"] == "true"
    assert "language" not in mock_post.call_args_list[0].kwargs["params"]
    assert mock_post.call_args_list[1].kwargs["params"]["language"] == "zh-CN"
    assert "detect_language" not in mock_post.call_args_list[1].kwargs["params"]
    assert provider.detected_language() == "zh-CN"
    assert cues == [CueResult(id="zh-1", start=0.5, end=2.0, original_text="你好")]


def test_deepgram_splits_word_timestamps_at_a_speech_pause():
    provider = DeepgramProvider(api_key="test-key")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": {
            "utterances": [
                {
                    "id": "utt-1",
                    "start": 0.0,
                    "end": 2.0,
                    "transcript": "Hello world. Again now.",
                    "words": [
                        {"word": "hello", "punctuated_word": "Hello", "start": 0.12, "end": 0.30},
                        {"word": "world", "punctuated_word": "world.", "start": 0.31, "end": 0.55},
                        {"word": "again", "punctuated_word": "Again", "start": 1.30, "end": 1.60},
                        {"word": "now", "punctuated_word": "now.", "start": 1.61, "end": 1.90},
                    ],
                }
            ]
        }
    }

    with patch("httpx.post", return_value=mock_resp), patch(
        "pathlib.Path.read_bytes", return_value=b"fake-audio-bytes"
    ):
        cues = provider.transcribe("fake_audio.wav", language="en")

    assert cues == [
        CueResult(id="utt-1-1", start=0.12, end=0.55, original_text="Hello world."),
        CueResult(id="utt-1-2", start=1.30, end=1.90, original_text="Again now."),
    ]


def test_deepgram_limits_a_continuous_word_timed_cue_to_six_seconds():
    provider = DeepgramProvider(api_key="test-key")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": {
            "utterances": [
                {
                    "id": "utt-2",
                    "words": [
                        {"word": "one", "start": 0.0, "end": 2.0},
                        {"word": "two", "start": 2.1, "end": 4.0},
                        {"word": "three", "start": 4.1, "end": 6.0},
                        {"word": "four", "start": 6.1, "end": 7.0},
                    ],
                }
            ]
        }
    }

    with patch("httpx.post", return_value=mock_resp), patch(
        "pathlib.Path.read_bytes", return_value=b"fake-audio-bytes"
    ):
        cues = provider.transcribe("fake_audio.wav", language="en")

    assert cues == [
        CueResult(id="utt-2-1", start=0.0, end=6.0, original_text="one two three"),
        CueResult(id="utt-2-2", start=6.1, end=7.0, original_text="four"),
    ]


def test_deepgram_splits_long_chinese_text_at_word_boundaries():
    provider = DeepgramProvider(api_key="test-key")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": {
            "utterances": [{
                "id": "zh-1",
                "words": [
                    {"word": "我想和你", "start": 0.0, "end": 0.8},
                    {"word": "一起去看", "start": 0.9, "end": 1.7},
                    {"word": "远方的海", "start": 1.8, "end": 2.6},
                    {"word": "再慢慢走", "start": 2.7, "end": 3.5},
                ],
            }],
        },
    }

    with patch("httpx.post", return_value=mock_resp), patch(
        "pathlib.Path.read_bytes", return_value=b"fake-audio-bytes"
    ):
        cues = provider.transcribe("fake_audio.wav", language="zh-CN")

    assert cues == [
        CueResult(id="zh-1-1", start=0.0, end=2.6, original_text="我想和你 一起去看 远方的海"),
        CueResult(id="zh-1-2", start=2.7, end=3.5, original_text="再慢慢走"),
    ]


def test_deepgram_transcribe_error_status():
    provider = DeepgramProvider(api_key="test-key")
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = "Bad Request"

    with patch("httpx.post", return_value=mock_resp), \
         patch("pathlib.Path.read_bytes", return_value=b"fake-bytes"):
        with pytest.raises(RuntimeError, match="Deepgram transcription failed"):
            provider.transcribe("fake.wav", "en")
