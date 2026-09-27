#!/usr/bin/env python3
"""Serve the private T69 comparison page and accept only named local PNG captures."""

from __future__ import annotations

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[2]
CAPTURE_DIR = ROOT / "work/evidence/T69/screenshots"
ALLOWED = {
    f"pair-{pair}-{view}.png"
    for pair in ("2742-2754", "2780-2798", "1595-1573", "2738-2750")
    for view in ("front", "back", "side")
}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        name = unquote(parsed.path.removeprefix("/__capture/"))
        if parsed.path != f"/__capture/{name}" or name not in ALLOWED:
            self.send_error(404, "capture name is not allowlisted")
            return
        if self.headers.get_content_type() != "image/png":
            self.send_error(415, "image/png required")
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400, "invalid content length")
            return
        if size <= 8 or size > 12_000_000:
            self.send_error(413, "capture size outside local QA limit")
            return
        body = self.rfile.read(size)
        if len(body) != size or not body.startswith(b"\x89PNG\r\n\x1a\n"):
            self.send_error(400, "invalid PNG payload")
            return
        CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
        target = (CAPTURE_DIR / name).resolve()
        if target.parent != CAPTURE_DIR.resolve():
            self.send_error(400, "invalid capture destination")
            return
        target.write_bytes(body)
        payload = json.dumps({"path": str(target.relative_to(ROOT)), "bytes": len(body)}).encode()
        self.send_response(201)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} {fmt % args}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8769)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"T69 private QA server: http://127.0.0.1:{args.port}/work/evidence/T69/private-comparison.html")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
