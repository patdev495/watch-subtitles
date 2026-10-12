"""Bridge surface for the interface shell: theme choice and Video poster frames.

Mixed into BridgeApi so pywebview exposes these methods alongside the rest of
the bridge, while keeping each module inside the project's file-length limit.
"""

import os
from typing import Any, Dict
from urllib.parse import quote

from backend.audio import get_ffmpeg_path
from backend.settings import load_theme as read_theme, save_theme as write_theme


class InterfaceBridge:
    # The local stream server port, injected by BridgeApi's constructor.
    port: int

    def get_theme(self) -> Dict[str, Any]:
        """Return the persisted interface theme."""
        return {"theme": read_theme()}

    def save_theme(self, theme: str) -> Dict[str, Any]:
        """Persist the interface theme chosen in the header."""
        return {"theme": write_theme(theme)}

    def get_thumbnail_url(self, video_path: str) -> Dict[str, Any]:
        """Resolve the cached poster frame URL for a Video in the Playback Queue."""
        if not os.path.isfile(video_path):
            return {"ok": False, "error": "Video not found"}
        try:
            get_ffmpeg_path()
        except RuntimeError as exc:
            # Without FFmpeg the frontend keeps its placeholder tiles.
            return {"ok": False, "error": str(exc)}
        return {"ok": True, "url": f"http://127.0.0.1:{self.port}/thumbnail?path={quote(video_path)}"}
