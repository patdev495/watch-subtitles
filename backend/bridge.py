import os
from typing import Optional, Dict, Any
from urllib.parse import quote
import webview
from pydantic import BaseModel

class PingResponse(BaseModel):
    status: str
    message: str

class VideoDialogResponse(BaseModel):
    cancelled: bool
    path: Optional[str] = None
    filename: Optional[str] = None
    stream_url: Optional[str] = None

class BridgeApi:
    def __init__(self, port: int) -> None:
        self.port: int = port
        # Prefix with underscore so pywebview's js_api dir() introspector skips
        # this attribute. Without underscore, pywebview recurses into the webview
        # Window → native COM object from a non-UI thread, causing the
        # "CoreWebView2Controller members can only be accessed from the UI thread"
        # spam and AccessibilityObject errors on Windows.
        self._window: Optional[webview.Window] = None

    def set_window(self, window: webview.Window) -> None:
        self._window = window

    def ping(self) -> Dict[str, Any]:
        """Verify Python backend and pywebview bridge connectivity."""
        return PingResponse(status="ok", message="Python UV backend ready").model_dump()

    def open_video_dialog(self) -> Dict[str, Any]:
        """Open native OS file dialog to select video file."""
        if not self._window:
            return VideoDialogResponse(cancelled=True).model_dump()

        file_types = (
            "Video Files (*.mp4;*.mkv;*.webm;*.avi;*.mov;*.flv;*.wmv;*.m4v)",
            "All Files (*.*)"
        )
        result = self._window.create_file_dialog(
            dialog_type=webview.FileDialog.OPEN,
            allow_multiple=False,
            file_types=file_types
        )

        if not result or len(result) == 0:
            return VideoDialogResponse(cancelled=True).model_dump()

        file_path = result[0]
        if not os.path.exists(file_path):
            return VideoDialogResponse(cancelled=True).model_dump()

        filename = os.path.basename(file_path)
        encoded_path = quote(file_path)
        stream_url = f"http://127.0.0.1:{self.port}/stream?path={encoded_path}"

        return VideoDialogResponse(
            cancelled=False,
            path=file_path,
            filename=filename,
            stream_url=stream_url
        ).model_dump()

    def load_video_path(self, file_path: str) -> Dict[str, Any]:
        """Resolve dropped or provided video path into stream URL."""
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return VideoDialogResponse(cancelled=True).model_dump()

        filename = os.path.basename(file_path)
        encoded_path = quote(file_path)
        stream_url = f"http://127.0.0.1:{self.port}/stream?path={encoded_path}"

        return VideoDialogResponse(
            cancelled=False,
            path=file_path,
            filename=filename,
            stream_url=stream_url
        ).model_dump()

