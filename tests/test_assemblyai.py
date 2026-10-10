from pathlib import Path
from unittest.mock import MagicMock, call, patch

from backend.providers.assemblyai import AssemblyAIProvider


def _response(status_code: int, payload: dict[str, object]) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    response.text = str(payload)
    return response


def test_transcribe_uploads_audio_polls_and_builds_cues(tmp_path: Path) -> None:
    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"audio-bytes")
    provider = AssemblyAIProvider(api_key="aai-key")

    upload = _response(200, {"upload_url": "https://cdn.assemblyai.test/audio"})
    submitted = _response(200, {"id": "transcript-123", "status": "queued"})
    queued = _response(200, {"status": "processing"})
    completed = _response(
        200,
        {
            "status": "completed",
            "language_code": "zh",
            "words": [
                {"text": "Hello", "start": 0, "end": 300},
                {"text": "world", "start": 350, "end": 650},
                {"text": "again", "start": 1300, "end": 1650},
            ],
        },
    )

    with patch("backend.providers.assemblyai.httpx.post", side_effect=[upload, submitted]) as post, patch(
        "backend.providers.assemblyai.httpx.get", side_effect=[queued, completed]
    ), patch("backend.providers.assemblyai.time.sleep"):
        cues = provider.transcribe(str(audio_path), language="auto")

    assert [(cue.start, cue.end, cue.original_text) for cue in cues] == [
        (0.0, 0.65, "Hello world"),
        (1.3, 1.65, "again"),
    ]
    assert provider.detected_language() == "zh-CN"
    assert post.call_args_list == [
        call(
            "https://api.assemblyai.com/v2/upload",
            headers={"Authorization": "aai-key", "Content-Type": "application/octet-stream"},
            content=b"audio-bytes",
            timeout=30.0,
        ),
        call(
            "https://api.assemblyai.com/v2/transcript",
            headers={"Authorization": "aai-key", "Content-Type": "application/json"},
            json={
                "audio_url": "https://cdn.assemblyai.test/audio",
                "speech_models": ["universal-3-5-pro"],
                "language_detection": True,
                "speaker_labels": False,
            },
            timeout=30.0,
        ),
    ]


def test_transcribe_maps_traditional_chinese_to_assemblyai_chinese(tmp_path: Path) -> None:
    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"audio-bytes")
    provider = AssemblyAIProvider(api_key="aai-key")

    with patch(
        "backend.providers.assemblyai.httpx.post",
        side_effect=[
            _response(200, {"upload_url": "https://cdn.assemblyai.test/audio"}),
            _response(200, {"id": "transcript-123", "status": "queued"}),
        ],
    ) as post, patch(
        "backend.providers.assemblyai.httpx.get",
        return_value=_response(200, {"status": "completed", "words": []}),
    ):
        assert provider.transcribe(str(audio_path), language="zh-TW") == []

    assert post.call_args_list[1].kwargs["json"]["language_code"] == "zh"
    assert "language_detection" not in post.call_args_list[1].kwargs["json"]


def test_transcribe_retries_a_transient_upload_error(tmp_path: Path) -> None:
    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"audio-bytes")
    provider = AssemblyAIProvider(api_key="aai-key")

    with patch(
        "backend.providers.assemblyai.httpx.post",
        side_effect=[
            _response(503, {"error": "temporarily unavailable"}),
            _response(200, {"upload_url": "https://cdn.assemblyai.test/audio"}),
            _response(200, {"id": "transcript-123", "status": "queued"}),
        ],
    ) as post, patch(
        "backend.providers.assemblyai.httpx.get",
        return_value=_response(200, {"status": "completed", "words": []}),
    ), patch("backend.providers.assemblyai.time.sleep") as sleep:
        assert provider.transcribe(str(audio_path), language="en") == []

    assert post.call_count == 3
    sleep.assert_called_once_with(1)


def test_validate_key_uses_a_non_billing_transcript_list_request() -> None:
    provider = AssemblyAIProvider(api_key="unused")
    with patch(
        "backend.providers.assemblyai.httpx.get", return_value=_response(200, {})
    ) as get:
        assert provider.validate_key("aai-key") is True

    get.assert_called_once_with(
        "https://api.assemblyai.com/v2/transcript?limit=1",
        headers={"Authorization": "aai-key"},
        timeout=30.0,
    )
