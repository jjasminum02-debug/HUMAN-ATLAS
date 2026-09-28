#!/usr/bin/env python3
"""Fetch exactly the pinned official Z-Anatomy archive with a hard byte cap."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
from zoneinfo import ZoneInfo

REPOSITORY = "Z-Anatomy/Models-of-human-anatomy"
COMMIT = "c7010a903b75a2fd24a13b1c2c4c3546a9223780"
SOURCE_URL = f"https://github.com/{REPOSITORY}/raw/{COMMIT}/Z-Anatomy.zip"
MAX_BYTES = 120_000_000
ALLOWED_HOSTS = {
    "github.com",
    "raw.githubusercontent.com",
    "objects.githubusercontent.com",
    "github-cloud.s3.amazonaws.com",
    "release-assets.githubusercontent.com",
}


class RestrictedRedirects(HTTPRedirectHandler):
    def __init__(self) -> None:
        super().__init__()
        self.chain: list[dict[str, object]] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        host = (urlparse(newurl).hostname or "").lower()
        if host not in ALLOWED_HOSTS:
            raise RuntimeError(f"refusing redirect outside GitHub asset hosts: {newurl}")
        self.chain.append({"status": code, "from": req.full_url, "to": newurl})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    root = args.project_root.resolve(strict=True)
    destination = args.destination.absolute()
    receipt_path = args.receipt.absolute()
    cache_root = (root / "atlas-data/source-cache/z-anatomy/t97").resolve()
    if destination.parent.resolve() != cache_root:
        raise RuntimeError("destination must be directly inside the T97 ignored cache")
    if not destination.parent.exists():
        destination.parent.mkdir(parents=True)
    if destination.parent.is_symlink() or destination.exists() or destination.is_symlink():
        raise RuntimeError("refusing symlink or overwrite in the source cache")
    if not receipt_path.resolve().is_relative_to(root / "work/evidence/T97"):
        raise RuntimeError("receipt must be written inside work/evidence/T97")

    redirect = RestrictedRedirects()
    opener = build_opener(redirect)
    request = Request(SOURCE_URL, headers={"User-Agent": "HUMAN-ATLAS-T97/1.0"})
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
    partial = destination.with_suffix(destination.suffix + ".part")
    total = 0
    digest = hashlib.sha256()
    receipt: dict[str, object] = {
        "task": "T97",
        "requestedAt": now,
        "repository": REPOSITORY,
        "commit": COMMIT,
        "requestedUrl": SOURCE_URL,
        "transferLimitBytes": MAX_BYTES,
        "downloadedBytes": 0,
        "sha256": None,
        "responseStatus": None,
        "finalUrl": None,
        "redirects": redirect.chain,
        "headers": {},
        "complete": False,
    }
    try:
        with opener.open(request, timeout=60) as response:
            status = response.getcode()
            final_url = response.geturl()
            final_host = (urlparse(final_url).hostname or "").lower()
            if status != 200:
                raise RuntimeError(f"expected HTTP 200 after redirects, got {status}")
            if final_host not in ALLOWED_HOSTS:
                raise RuntimeError(f"refusing final URL outside GitHub asset hosts: {final_url}")
            headers = {k.lower(): v for k, v in response.headers.items()}
            advertised = headers.get("content-length")
            if advertised is not None and int(advertised) > MAX_BYTES:
                raise RuntimeError(f"advertised Content-Length exceeds cap: {advertised}")
            with partial.open("xb") as out:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_BYTES:
                        raise RuntimeError(f"response exceeded {MAX_BYTES} bytes")
                    digest.update(chunk)
                    out.write(chunk)
                out.flush()
                os.fsync(out.fileno())
            if advertised is not None and total != int(advertised):
                raise RuntimeError(f"received byte count {total} differs from Content-Length {advertised}")
            receipt.update({
                "responseStatus": status,
                "finalUrl": final_url,
                "headers": {
                    key: headers[key]
                    for key in ("content-type", "content-length", "content-disposition", "etag", "last-modified", "accept-ranges")
                    if key in headers
                },
                "downloadedBytes": total,
                "sha256": digest.hexdigest(),
                "complete": True,
            })
        partial.replace(destination)
        receipt["cacheRelativePath"] = destination.relative_to(root).as_posix()
        receipt["downloadedAt"] = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        partial.unlink(missing_ok=True)
        receipt["downloadedBytes"] = total
        receipt["error"] = f"{type(exc).__name__}: {exc}"
        receipt["redirects"] = redirect.chain
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(receipt, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
