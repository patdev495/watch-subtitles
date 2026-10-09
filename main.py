import os
import argparse
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

    window = webview.create_window(
        title="Watch Subtitles",
        url=url,
        js_api=api,
        width=1240,
        height=820,
        min_size=(920, 620),
    )
    api.set_window(window)

    webview.start(debug=args.dev)


if __name__ == "__main__":
    main()
