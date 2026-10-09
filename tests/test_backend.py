import os
import tempfile
import httpx
import pytest
from backend.server import start_stream_server
from backend.bridge import BridgeApi

def test_bridge_ping():
    api = BridgeApi(port=8080)
    res = api.ping()
    assert res["status"] == "ok"
    assert "Python UV" in res["message"]

def test_bridge_load_video_path_nonexistent():
    api = BridgeApi(port=8080)
    res = api.load_video_path("non_existent_file.mp4")
    assert res["cancelled"] is True
    assert res["stream_url"] is None

def test_bridge_load_video_path_valid():
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        f.write(b"dummy video content")
        temp_path = f.name

    try:
        api = BridgeApi(port=8999)
        res = api.load_video_path(temp_path)
        assert res["cancelled"] is False
        assert res["filename"] == os.path.basename(temp_path)
        assert res["stream_url"] is not None
        assert "http://127.0.0.1:8999/stream?path=" in res["stream_url"]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_stream_server_range_requests():
    test_content = b"0123456789" * 100  # 1000 bytes
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        f.write(test_content)
        temp_path = f.name

    server, port = start_stream_server()
    try:
        # Full content request
        url = f"http://127.0.0.1:{port}/stream"
        resp = httpx.get(url, params={"path": temp_path})
        assert resp.status_code == 200
        assert resp.content == test_content
        assert resp.headers.get("accept-ranges") == "bytes"

        # Byte range request
        range_resp = httpx.get(url, params={"path": temp_path}, headers={"Range": "bytes=10-19"})
        assert range_resp.status_code == 206
        assert range_resp.content == test_content[10:20]
        assert range_resp.headers.get("content-range") == "bytes 10-19/1000"
    finally:
        server.shutdown()
        if os.path.exists(temp_path):
            os.remove(temp_path)
