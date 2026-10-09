"""
export.py
=========
Pure formatter utilities for bilingual subtitle export.
No I/O — only string generation so the logic is easily unit-tested.
"""
from __future__ import annotations

from typing import Any, Sequence


def _srt_timestamp(seconds: float) -> str:
    """Convert fractional seconds to SRT timestamp ``HH:MM:SS,mmm``."""
    ms = round(seconds * 1000)
    h, remainder = divmod(ms, 3_600_000)
    m, remainder = divmod(remainder, 60_000)
    s, ms_part = divmod(remainder, 1_000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms_part:03d}"


def _vtt_timestamp(seconds: float) -> str:
    """Convert fractional seconds to WebVTT timestamp ``HH:MM:SS.mmm``."""
    ms = round(seconds * 1000)
    h, remainder = divmod(ms, 3_600_000)
    m, remainder = divmod(remainder, 60_000)
    s, ms_part = divmod(remainder, 1_000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms_part:03d}"


def format_srt(cues: Sequence[dict[str, Any]], layout: str = "bilingual") -> str:
    """Render cues as an SRT string.

    Args:
        cues: list of cue dicts with keys ``id``, ``start``, ``end``,
              ``originalText``, ``translatedText``.
        layout: one of ``"bilingual"`` (original \\n translated),
                ``"original"`` (source language only),
                ``"translated"`` (target language only).

    Returns:
        A valid SRT-formatted string ready to be written to disk.
    """
    blocks: list[str] = []
    for seq, cue in enumerate(cues, start=1):
        start_ts = _srt_timestamp(float(cue.get("start", 0)))
        end_ts = _srt_timestamp(float(cue.get("end", 0)))
        original = (cue.get("originalText") or "").strip()
        translated = (cue.get("translatedText") or "").strip()

        if layout == "original":
            text = original
        elif layout == "translated":
            text = translated
        else:  # bilingual (default)
            text = f"{original}\n{translated}" if translated else original

        if not text:
            continue

        blocks.append(f"{seq}\n{start_ts} --> {end_ts}\n{text}")

    return "\n\n".join(blocks) + "\n"


def format_vtt(cues: Sequence[dict[str, Any]], layout: str = "bilingual") -> str:
    """Render cues as a WebVTT string.

    Args:
        cues: same shape as :func:`format_srt`.
        layout: same options as :func:`format_srt`.

    Returns:
        A valid WebVTT-formatted string ready to be written to disk.
    """
    lines: list[str] = ["WEBVTT", ""]
    for seq, cue in enumerate(cues, start=1):
        start_ts = _vtt_timestamp(float(cue.get("start", 0)))
        end_ts = _vtt_timestamp(float(cue.get("end", 0)))
        original = (cue.get("originalText") or "").strip()
        translated = (cue.get("translatedText") or "").strip()

        if layout == "original":
            text = original
        elif layout == "translated":
            text = translated
        else:
            text = f"{original}\n{translated}" if translated else original

        if not text:
            continue

        lines.append(str(seq))
        lines.append(f"{start_ts} --> {end_ts}")
        lines.append(text)
        lines.append("")

    return "\n".join(lines)
