from pathlib import Path
from threading import Event
from time import sleep

import pytest

from backend.bridge import BridgeApi
from backend.cache import SubtitleCache


def _video(tmp_path: Path, name: str) -> str:
    path = tmp_path / name
    path.write_bytes(name.encode())
    return str(path)


def _wait_for(bridge: BridgeApi, job_id: str, statuses: set[str]) -> dict:
    for _ in range(100):
        result = bridge.get_subtitle_job(job_id)
        if result["job"]["status"] in statuses:
            return result["job"]
        sleep(0.01)
    pytest.fail(f"Job {job_id} did not reach {statuses}")


def test_bridge_creates_identified_waiting_job(tmp_path: Path) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"video")
    cache = SubtitleCache(db_path=tmp_path / "cache.db")
    bridge = BridgeApi(port=8080, cache=cache)
    bridge.save_cached_subtitles(
        str(video), "en", "vi", [{"id": "1", "start": 0, "end": 1, "originalText": "Hi", "translatedText": "Chào"}]
    )

    response = bridge.create_subtitle_job(str(video), "en", "vi")

    assert response["ok"] is True
    assert response["job"]["id"]
    assert response["job"]["video_path"] == str(video)
    assert response["job"]["source_language"] == "en"
    assert response["job"]["target_language"] == "vi"
    assert response["job"]["status"] == "completed"


def test_bridge_force_regeneration_discards_only_the_selected_cached_language_pair(tmp_path: Path) -> None:
    started = Event()
    release = Event()

    def runner(job: object, report: object) -> list[dict]:
        started.set()
        release.wait(timeout=1)
        return [{"id": "fresh", "start": 0, "end": 1, "originalText": "Fresh", "translatedText": "Mới"}]

    video = _video(tmp_path, "video.mp4")
    cache = SubtitleCache(db_path=tmp_path / "cache.db")
    bridge = BridgeApi(port=8080, cache=cache, job_runner=runner)
    bridge.save_cached_subtitles(video, "en", "vi", [{"id": "old", "start": 0, "end": 1, "originalText": "Old", "translatedText": "Cũ"}])
    bridge.save_cached_subtitles(video, "en", "ja", [{"id": "other", "start": 0, "end": 1, "originalText": "Other", "translatedText": "別"}])

    response = bridge.create_subtitle_job(video, "en", "vi", force=True)

    assert response["ok"] is True
    assert started.wait(timeout=1)
    fingerprint = bridge.get_video_fingerprint(video)["fingerprint"]
    assert cache.get_cues(fingerprint, "en", "vi") is None
    assert cache.get_cues(fingerprint, "en", "ja") is not None

    release.set()
    assert _wait_for(bridge, response["job"]["id"], {"completed"})["cues"][0]["id"] == "fresh"


def test_bridge_runs_jobs_fifo_and_keeps_results_isolated(tmp_path: Path) -> None:
    started_first = Event()
    release_first = Event()
    run_order: list[str] = []

    def runner(job: object, report: object) -> list[dict]:
        name = Path(job.video_path).name  # type: ignore[attr-defined]
        run_order.append(name)
        if name == "first.mp4":
            started_first.set()
            release_first.wait(timeout=1)
        return [{"id": name, "start": 0, "end": 1, "originalText": name, "translatedText": name}]

    bridge = BridgeApi(port=8080, cache=SubtitleCache(db_path=tmp_path / "cache.db"), job_runner=runner)
    first = bridge.create_subtitle_job(_video(tmp_path, "first.mp4"), "en", "vi")["job"]
    assert started_first.wait(timeout=1)
    second = bridge.create_subtitle_job(_video(tmp_path, "second.mp4"), "en", "vi")["job"]
    assert bridge.get_subtitle_job(second["id"])["job"]["status"] == "waiting"

    release_first.set()
    completed_first = _wait_for(bridge, first["id"], {"completed"})
    completed_second = _wait_for(bridge, second["id"], {"completed"})

    assert run_order == ["first.mp4", "second.mp4"]
    assert completed_first["cues"][0]["id"] == "first.mp4"
    assert completed_second["cues"][0]["id"] == "second.mp4"


def test_bridge_rejects_duplicate_active_language_pair(tmp_path: Path) -> None:
    started = Event()
    release = Event()

    def runner(job: object, report: object) -> list[dict]:
        started.set()
        release.wait(timeout=1)
        return []

    bridge = BridgeApi(port=8080, cache=SubtitleCache(db_path=tmp_path / "cache.db"), job_runner=runner)
    video = _video(tmp_path, "video.mp4")
    first = bridge.create_subtitle_job(video, "en", "vi")
    assert started.wait(timeout=1)
    duplicate = bridge.create_subtitle_job(video, "en", "vi")
    release.set()

    assert first["ok"] is True
    assert duplicate["ok"] is False
    assert duplicate["duplicate"] is True
    assert "đang chờ" in duplicate["error"]


def test_bridge_allows_multiple_language_pairs_for_same_video(tmp_path: Path) -> None:
    release = Event()

    def runner(job: object, report: object) -> list[dict]:
        release.wait(timeout=1)
        return []

    bridge = BridgeApi(port=8080, cache=SubtitleCache(db_path=tmp_path / "cache.db"), job_runner=runner)
    video = _video(tmp_path, "lesson.mp4")
    vietnamese = bridge.create_subtitle_job(video, "en", "vi")
    japanese = bridge.create_subtitle_job(video, "en", "ja")
    release.set()

    assert vietnamese["ok"] is True
    assert japanese["ok"] is True
    assert japanese["job"]["target_language"] == "ja"


def test_bridge_continues_after_failed_job(tmp_path: Path) -> None:
    def runner(job: object, report: object) -> list[dict]:
        if Path(job.video_path).name == "bad.mp4":  # type: ignore[attr-defined]
            raise RuntimeError("provider unavailable")
        return []

    bridge = BridgeApi(port=8080, cache=SubtitleCache(db_path=tmp_path / "cache.db"), job_runner=runner)
    failed = bridge.create_subtitle_job(_video(tmp_path, "bad.mp4"), "en", "vi")["job"]
    succeeding = bridge.create_subtitle_job(_video(tmp_path, "good.mp4"), "en", "vi")["job"]

    assert _wait_for(bridge, failed["id"], {"failed"})["error"] == "provider unavailable"
    assert _wait_for(bridge, succeeding["id"], {"completed"})["status"] == "completed"


def test_bridge_retries_failed_job_at_end_with_original_languages(tmp_path: Path) -> None:
    calls: list[tuple[str, str]] = []

    def runner(job: object, report: object) -> list[dict]:
        calls.append((job.source_language, job.target_language))  # type: ignore[attr-defined]
        if len(calls) == 1:
            raise RuntimeError("offline")
        return []

    bridge = BridgeApi(port=8080, cache=SubtitleCache(db_path=tmp_path / "cache.db"), job_runner=runner)
    failed = bridge.create_subtitle_job(_video(tmp_path, "retry.mp4"), "ja", "vi")["job"]
    _wait_for(bridge, failed["id"], {"failed"})

    retried = bridge.retry_subtitle_job(failed["id"])

    assert retried["ok"] is True
    assert retried["job"]["id"] != failed["id"]
    assert _wait_for(bridge, retried["job"]["id"], {"completed"})["status"] == "completed"
    assert calls == [("ja", "vi"), ("ja", "vi")]


def test_bridge_removes_waiting_job_but_not_processing_job(tmp_path: Path) -> None:
    started = Event()
    release = Event()

    def runner(job: object, report: object) -> list[dict]:
        started.set()
        release.wait(timeout=1)
        return []

    bridge = BridgeApi(port=8080, cache=SubtitleCache(db_path=tmp_path / "cache.db"), job_runner=runner)
    processing = bridge.create_subtitle_job(_video(tmp_path, "active.mp4"), "en", "vi")["job"]
    assert started.wait(timeout=1)
    waiting = bridge.create_subtitle_job(_video(tmp_path, "waiting.mp4"), "en", "vi")["job"]

    assert bridge.remove_subtitle_job(processing["id"])["ok"] is False
    assert bridge.remove_subtitle_job(waiting["id"])["job"]["status"] == "cancelled"
    release.set()
