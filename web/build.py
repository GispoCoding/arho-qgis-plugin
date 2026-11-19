"""Build the ARHO website with the user manual (Finnish and Swedish) into web/site.

Usage (from web/):

    uv run --no-project --with-requirements requirements.txt python build.py
    uv run --no-project --with-requirements requirements.txt python build.py --serve

The Finnish site goes to web/site/ and the Swedish site to web/site/sv/.
Both use the screenshots in web/fi/manual/images/. The script copies them to
web/sv/manual/images/ (ignored by git) before the Swedish build.

--serve starts a local web server at http://localhost:8000/arho-qgis-plugin/,
the same path as on GitHub Pages, so the language switch works.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import shutil
import subprocess
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent
SITE = WEB / "site"
PREFIX = "/arho-qgis-plugin"


def copy_shared_images() -> None:
    source = WEB / "fi" / "manual" / "images"
    target = WEB / "sv" / "manual" / "images"
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(source, target)


def build(config: str, *, strict: bool) -> None:
    command = [sys.executable, "-m", "zensical", "build", "-f", str(WEB / config)]
    if strict:
        command.append("--strict")
    subprocess.run(command, check=True, stdin=subprocess.DEVNULL)


class PrefixHandler(http.server.SimpleHTTPRequestHandler):
    """Serve web/site under /arho-qgis-plugin/ like GitHub Pages does."""

    def translate_path(self, path: str) -> str:
        if path == PREFIX:
            path = PREFIX + "/"
        # Paths outside the prefix map to a file that does not exist: 404, like on Pages.
        path = path[len(PREFIX) :] if path.startswith(PREFIX + "/") else "/__not_found__"
        return super().translate_path(path)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


class PreviewServer(http.server.ThreadingHTTPServer):
    # The default backlog of 5 refuses connections on Windows when a page
    # loads many files at once.
    request_queue_size = 64


def serve(port: int) -> None:
    handler = functools.partial(PrefixHandler, directory=str(SITE))
    with PreviewServer(("localhost", port), handler) as server:
        print(f"Serving http://localhost:{port}{PREFIX}/ (Ctrl+C stops)")
        server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--serve", action="store_true", help="serve the built site after the build")
    parser.add_argument("--port", type=int, default=8000, help="port for --serve (default 8000)")
    parser.add_argument("--strict", action="store_true", help="stop on warnings")
    args = parser.parse_args()

    copy_shared_images()
    build("zensical-fi.yml", strict=args.strict)  # cleans web/site first
    build("zensical-sv.yml", strict=args.strict)  # writes web/site/sv
    if args.serve:
        serve(args.port)


if __name__ == "__main__":
    main()
