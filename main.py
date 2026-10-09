import os
import argparse
import ctypes
import logging

import webview
from backend.server import start_stream_server
from backend.bridge import BridgeApi

# Silence any remaining pywebview noise (belt-and-suspenders).
# The primary fix is in BridgeApi: self._window (underscore) ensures pywebview's
# dir()-based introspector never recurses into the Window → COM objects.
logging.getLogger("pywebview").addFilter(
    type("_QuietFilter", (logging.Filter,), {
        "filter": lambda self, r: "AccessibilityObject" not in r.getMessage()
    })()
)

WINDOW_WIDTH = 1240
WINDOW_HEIGHT = 820
WINDOW_MIN_WIDTH = 920
WINDOW_MIN_HEIGHT = 620
WINDOW_EDGE_MARGIN = 16


def calculate_window_bounds(work_area: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """Fit the preferred window into a work area and return its centered bounds."""
    left, top, right, bottom = work_area
    available_width = max(1, right - left)
    available_height = max(1, bottom - top)
    horizontal_margin = min(WINDOW_EDGE_MARGIN, max(0, (available_width - WINDOW_MIN_WIDTH) // 2))
    vertical_margin = min(WINDOW_EDGE_MARGIN, max(0, (available_height - WINDOW_MIN_HEIGHT) // 2))
    width = min(WINDOW_WIDTH, available_width - horizontal_margin * 2)
    height = min(WINDOW_HEIGHT, available_height - vertical_margin * 2)
    return width, height, left + (available_width - width) // 2, top + (available_height - height) // 2


def get_windows_work_area() -> tuple[int, int, int, int] | None:
    """Return the primary monitor work area, excluding the taskbar when possible."""
    if os.name != "nt":
        return None
    from ctypes import wintypes

    rect = wintypes.RECT()
    if not ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0):
        return None
    return rect.left, rect.top, rect.right, rect.bottom


def main() -> None:
    parser = argparse.ArgumentParser(description="Watch Subtitles Desktop")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Connect to Vite dev server on http://localhost:5173",
    )
    args = parser.parse_args()

    server, port = start_stream_server()
    api = BridgeApi(port=port)

    dist_index = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "frontend", "dist", "index.html")
    )

    if args.dev or not os.path.exists(dist_index):
        url = "http://localhost:5173"
    else:
        url = f"http://127.0.0.1:{port}/"

    work_area = get_windows_work_area()
    width, height, x, y = calculate_window_bounds(work_area) if work_area else (WINDOW_WIDTH, WINDOW_HEIGHT, None, None)
    window = webview.create_window(
        title="Watch Subtitles",
        url=url,
        js_api=api,
        width=width,
        height=height,
        x=x,
        y=y,
        min_size=(min(WINDOW_MIN_WIDTH, width), min(WINDOW_MIN_HEIGHT, height)),
    )
    api.set_window(window)

    webview.start(debug=args.dev)


if __name__ == "__main__":
    main()
