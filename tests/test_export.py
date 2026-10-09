"""Tests for backend/export.py — SRT and VTT formatter utilities."""
import pytest
from backend.export import format_srt, format_vtt

CUES = [
    {
        "id": "1",
        "start": 0.0,
        "end": 2.5,
        "originalText": "Hello world",
        "translatedText": "Xin chào thế giới",
    },
    {
        "id": "2",
        "start": 3.0,
        "end": 5.1,
        "originalText": "Testing subtitles",
        "translatedText": "Kiểm tra phụ đề",
    },
]


# ── SRT ───────────────────────────────────────────────────────────────────────

class TestFormatSrt:
    def test_bilingual_block_structure(self):
        out = format_srt(CUES)
        blocks = [b.strip() for b in out.strip().split("\n\n")]
        assert len(blocks) == 2

    def test_sequence_numbers(self):
        out = format_srt(CUES)
        assert out.startswith("1\n")
        assert "\n2\n" in out

    def test_srt_timestamp_format(self):
        out = format_srt(CUES)
        # start=0.0 → 00:00:00,000, end=2.5 → 00:00:02,500
        assert "00:00:00,000 --> 00:00:02,500" in out

    def test_bilingual_text_two_lines(self):
        out = format_srt(CUES)
        assert "Hello world\nXin chào thế giới" in out

    def test_original_only_layout(self):
        out = format_srt(CUES, layout="original")
        assert "Hello world" in out
        assert "Xin chào" not in out

    def test_translated_only_layout(self):
        out = format_srt(CUES, layout="translated")
        assert "Xin chào thế giới" in out
        assert "Hello world" not in out

    def test_empty_cues_returns_newline(self):
        out = format_srt([])
        assert out == "\n"

    def test_skips_blank_text_cues(self):
        cues = [{"id": "1", "start": 0.0, "end": 1.0, "originalText": "", "translatedText": ""}]
        out = format_srt(cues)
        assert out.strip() == ""

    def test_large_timestamp(self):
        cues = [{"id": "1", "start": 3723.456, "end": 3725.0, "originalText": "A", "translatedText": ""}]
        out = format_srt(cues, layout="original")
        # 3723.456s = 1h 2m 3s 456ms
        assert "01:02:03,456 --> 01:02:05,000" in out


# ── VTT ───────────────────────────────────────────────────────────────────────

class TestFormatVtt:
    def test_starts_with_webvtt_header(self):
        out = format_vtt(CUES)
        assert out.startswith("WEBVTT\n")

    def test_vtt_timestamp_format(self):
        out = format_vtt(CUES)
        # VTT uses dot, not comma
        assert "00:00:00.000 --> 00:00:02.500" in out
        assert "," not in out.split("\n")[3]  # timestamp line has dot

    def test_bilingual_text(self):
        out = format_vtt(CUES)
        assert "Hello world\nXin chào thế giới" in out

    def test_original_only_layout(self):
        out = format_vtt(CUES, layout="original")
        assert "Testing subtitles" in out
        assert "Kiểm tra" not in out

    def test_translated_only_layout(self):
        out = format_vtt(CUES, layout="translated")
        assert "Kiểm tra phụ đề" in out
        assert "Testing subtitles" not in out

    def test_empty_cues(self):
        out = format_vtt([])
        assert out.startswith("WEBVTT")
