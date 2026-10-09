"""Tests for BridgeApi.export_subtitles()."""
import os
import tempfile
import pathlib
import pytest
from backend.bridge import BridgeApi


CUES = [
    {"id": "1", "start": 0.0, "end": 2.5, "originalText": "Hello", "translatedText": "Xin chào"},
    {"id": "2", "start": 3.0, "end": 5.0, "originalText": "World", "translatedText": "Thế giới"},
]


def test_bridge_export_srt_headless():
    bridge = BridgeApi(port=8080)
    res = bridge.export_subtitles(CUES, fmt="srt", layout="bilingual")
    assert res["ok"] is True
    path = res["path"]
    assert path.endswith(".srt")
    content = pathlib.Path(path).read_text(encoding="utf-8")
    assert "00:00:00,000 --> 00:00:02,500" in content
    assert "Hello\nXin chào" in content
    os.unlink(path)


def test_bridge_export_vtt_headless():
    bridge = BridgeApi(port=8080)
    res = bridge.export_subtitles(CUES, fmt="vtt", layout="translated")
    assert res["ok"] is True
    path = res["path"]
    assert path.endswith(".vtt")
    content = pathlib.Path(path).read_text(encoding="utf-8")
    assert content.startswith("WEBVTT")
    assert "Xin chào" in content
    assert "Hello" not in content
    os.unlink(path)


def test_bridge_export_empty_cues_rejected():
    bridge = BridgeApi(port=8080)
    res = bridge.export_subtitles([], fmt="srt")
    assert res["ok"] is False
    assert "phụ đề" in res["error"].lower()


def test_bridge_export_invalid_format():
    bridge = BridgeApi(port=8080)
    res = bridge.export_subtitles(CUES, fmt="ass")
    assert res["ok"] is False
    assert "ass" in res["error"]
