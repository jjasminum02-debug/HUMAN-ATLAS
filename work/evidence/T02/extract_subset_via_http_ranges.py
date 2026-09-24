#!/usr/bin/env python3
"""Fetch only selected OBJ members from the official BodyParts3D ZIP by HTTP byte ranges."""
from __future__ import annotations
import hashlib
import io
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

URL = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip"
TARGETS = {
    "FJ1394.obj", "FJ1397.obj", "FJ1409.obj", "FJ1410.obj",
    "FJ1437.obj", "FJ1439.obj", "FJ1440.obj", "FJ3360.obj",
    "FJ3366.obj", "FJ3385.obj", "FJ3387.obj",
}
OUT = Path("HUMAN ATLAS/atlas-data/assets/bodyparts3d-v4-pilot")
EVIDENCE = Path("HUMAN ATLAS/work/evidence/T02/source-transfer.json")
BLOCK_SIZE = 256 * 1024
MAX_RANGE_BYTES = 24 * 1024 * 1024

class HttpRangeFile:
    def __init__(self, url: str):
        self.url = url
        head = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "HUMAN-ATLAS-T02/1.0"})
        with urllib.request.urlopen(head, timeout=60) as response:
            self.size = int(response.headers["Content-Length"])
            self.last_modified = response.headers.get("Last-Modified")
            self.etag = response.headers.get("ETag")
            self.accept_ranges = response.headers.get("Accept-Ranges")
        self.pos = 0
        self.blocks: dict[int, bytes] = {}
        self.total_range_bytes = 0
        probe = self._request_range(0, 0)
        if len(probe) != 1:
            raise RuntimeError("Range probe did not return one byte")

    def _request_range(self, start: int, end: int) -> bytes:
        req = urllib.request.Request(self.url, headers={
            "User-Agent": "HUMAN-ATLAS-T02/1.0",
            "Range": f"bytes={start}-{end}",
        })
        with urllib.request.urlopen(req, timeout=120) as response:
            if response.status != 206:
                raise RuntimeError(f"Server ignored HTTP Range (status {response.status}); refusing a full archive transfer")
            content_range = response.headers.get("Content-Range", "")
            match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", content_range)
            if not match or tuple(map(int, match.groups())) != (start, end, self.size):
                raise RuntimeError(f"Unexpected Content-Range: {content_range!r}")
            data = response.read(end - start + 1)
        self.total_range_bytes += len(data)
        if self.total_range_bytes > MAX_RANGE_BYTES:
            raise RuntimeError(f"Range-read budget exceeded ({MAX_RANGE_BYTES} bytes); no whole archive is retained")
        if len(data) != end - start + 1:
            raise RuntimeError("Truncated HTTP range response")
        return data

    def _block(self, index: int) -> bytes:
        if index not in self.blocks:
            start = index * BLOCK_SIZE
            end = min(start + BLOCK_SIZE, self.size) - 1
            self.blocks[index] = self._request_range(start, end)
        return self.blocks[index]

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if whence == io.SEEK_SET:
            new = offset
        elif whence == io.SEEK_CUR:
            new = self.pos + offset
        elif whence == io.SEEK_END:
            new = self.size + offset
        else:
            raise ValueError("invalid whence")
        if new < 0:
            raise ValueError("negative seek position")
        self.pos = new
        return new

    def tell(self) -> int:
        return self.pos

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def read(self, size: int = -1) -> bytes:
        if size is None or size < 0:
            size = self.size - self.pos
        size = min(size, max(0, self.size - self.pos))
        start = self.pos
        end = start + size
        result = bytearray()
        while start < end:
            index = start // BLOCK_SIZE
            block_start = index * BLOCK_SIZE
            block = self._block(index)
            local_start = start - block_start
            take = min(end - start, len(block) - local_start)
            result.extend(block[local_start:local_start + take])
            start += take
        self.pos = end
        return bytes(result)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    if any((OUT / name).exists() for name in TARGETS):
        raise FileExistsError("Refusing to overwrite an existing pilot asset")
    remote = HttpRangeFile(URL)
    with zipfile.ZipFile(remote) as archive:
        available = {Path(info.filename).name: info for info in archive.infolist() if Path(info.filename).suffix.lower() == ".obj"}
        missing = sorted(TARGETS - set(available))
        if missing:
            raise RuntimeError("Selected FJ OBJ member(s) not present in archive: " + ", ".join(missing))
        records = []
        for name in sorted(TARGETS):
            info = available[name]
            destination = OUT / name
            with archive.open(info, "r") as source, destination.open("xb") as output:
                while True:
                    block = source.read(1024 * 1024)
                    if not block:
                        break
                    output.write(block)
            records.append({
                "archive_member": info.filename,
                "file": str(destination),
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
                "zip_crc32": f"{info.CRC:08x}",
                "zip_compressed_bytes": info.compress_size,
                "zip_uncompressed_bytes": info.file_size,
            })
    result = {
        "source_archive_url": URL,
        "archive_size_bytes": remote.size,
        "archive_last_modified": remote.last_modified,
        "archive_etag": remote.etag,
        "server_accept_ranges_header": remote.accept_ranges,
        "retrieved_transport": "HTTP Range requests only; archive ZIP was not saved locally",
        "unique_cached_block_count": len(remote.blocks),
        "range_request_bytes_including_retries_and_probe": remote.total_range_bytes,
        "range_transfer_budget_bytes": MAX_RANGE_BYTES,
        "selected_member_count": len(records),
        "assets": records,
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
