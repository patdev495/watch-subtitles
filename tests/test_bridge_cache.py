import os
import tempfile
from pathlib import Path
import pytest
from backend.bridge import BridgeApi
from backend.cache import SubtitleCache


def test_bridge_fingerprint_and_cached_subtitles():
    with tempfile.TemporaryDirectory() as tmp:
        video = Path(tmp) / "sample_movie.mp4"
        video.write_bytes(b"dummy video content for bridge testing" * 200)

        # Custom cache db in tmp
        db_path = Path(tmp) / "test_subtitles.db"
        cache = SubtitleCache(db_path=db_path)

        bridge = BridgeApi(port=8080)

        # 1. Get fingerprint
        fp_res = bridge.get_video_fingerprint(str(video))
        assert fp_res["ok"] is True
        assert len(fp_res["fingerprint"]) == 64

        # 2. Check cached before saving -> cached: False
        cached_res1 = bridge.get_cached_subtitles(str(video), "vi")
        assert cached_res1["ok"] is True
        assert cached_res1["cached"] is False
        assert cached_res1["cues"] == []

        # 3. Save cues via bridge
        cues = [
            {"id": "1", "start": 0.0, "end": 2.0, "originalText": "Hello", "translatedText": "Xin chào"},
        ]
        save_res = bridge.save_cached_subtitles(str(video), "vi", cues)
        assert save_res["ok"] is True

        # 4. Check cached after saving -> cached: True
        cached_res2 = bridge.get_cached_subtitles(str(video), "vi")
        assert cached_res2["ok"] is True
        assert cached_res2["cached"] is True
        assert cached_res2["cues"] == cues
