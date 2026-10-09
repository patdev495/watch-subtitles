import os
import re
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Tuple, Optional
import socket
import threading

DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

class VideoStreamHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Range, Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)

        # Handle Video Range Streaming
        if parsed_url.path == "/stream":
            self.handle_video_stream(parsed_url.query)
            return

        # Serve static frontend dist files
        self.handle_static_file(parsed_url.path)

    def handle_static_file(self, rel_path: str) -> None:
        if rel_path in ("/", ""):
            rel_path = "/index.html"

        safe_path = rel_path.lstrip("/\\")
        file_path = os.path.join(DIST_DIR, safe_path)

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            # Fallback to SPA index.html
            file_path = os.path.join(DIST_DIR, "index.html")

        if not os.path.exists(file_path):
            self.send_error(404, "Frontend dist not found")
            return

        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = "text/html" if file_path.endswith(".html") else "application/octet-stream"

        file_size = os.path.getsize(file_path)
        try:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            with open(file_path, "rb") as f:
                while chunk := f.read(64 * 1024):
                    self.wfile.write(chunk)
        except (ConnectionResetError, BrokenPipeError):
            pass

    def handle_video_stream(self, query: str) -> None:
        query_params = parse_qs(query)
        file_path_list = query_params.get("path")
        if not file_path_list or not file_path_list[0]:
            self.send_error(400, "Missing path parameter")
            return

        file_path = file_path_list[0]
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self.send_error(404, "File Not Found")
            return

        file_size = os.path.getsize(file_path)
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = "video/mp4"

        range_header = self.headers.get("Range")
        start: int = 0
        end: int = file_size - 1
        status_code: int = 200

        if range_header:
            range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
            if range_match:
                start_str, end_str = range_match.groups()
                start = int(start_str)
                if end_str:
                    end = int(end_str)
                status_code = 206

        if start >= file_size:
            self.send_error(416, "Requested Range Not Satisfiable")
            return

        end = min(end, file_size - 1)
        content_length = (end - start) + 1

        try:
            self.send_response(status_code)
            self.send_header("Content-Type", content_type)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(content_length))

            if status_code == 206:
                self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")

            self.end_headers()

            chunk_size = 64 * 1024
            with open(file_path, "rb") as f:
                f.seek(start)
                bytes_to_read = content_length
                while bytes_to_read > 0:
                    read_len = min(chunk_size, bytes_to_read)
                    data = f.read(read_len)
                    if not data:
                        break
                    self.wfile.write(data)
                    bytes_to_read -= len(data)
        except (ConnectionResetError, BrokenPipeError):
            pass


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def start_stream_server() -> Tuple[HTTPServer, int]:
    port = find_free_port()
    server = HTTPServer(("127.0.0.1", port), VideoStreamHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, port
