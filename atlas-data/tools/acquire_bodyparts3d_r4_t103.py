#!/usr/bin/env python3
"""Acquire exactly T103's ten frozen R4 OBJ members through the existing range extractor."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "work/evidence/T103/frozen-source-set.json"
OUT_ROOT = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t103"
RECEIPT = ROOT / "work/evidence/T103/source-acquisition.json"
HELPER = ROOT / "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py"
MAX_RANGE_TRANSFER = 120_000_000
MAX_CENTRAL_DIRECTORY = 64_000_000
MAX_SELECTED_UNCOMPRESSED = 1_000_000_000
MAX_SINGLE_MEMBER = 200_000_000
EXPECTED = ["FJ1473", "FJ1473M", "FJ1474", "FJ1474M", "FJ1481", "FJ1481M", "FJ1514", "FJ1514M", "FJ1515", "FJ1515M"]


class AcquireError(RuntimeError):
    pass


def load_helper():
    spec = importlib.util.spec_from_file_location("t103_existing_r4_range_extractor", HELPER)
    if not spec or not spec.loader:
        raise AcquireError("could not load the existing bounded R4 range extractor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def acquire() -> dict[str, Any]:
    helper = load_helper()
    frozen = helper.load_frozen(FREEZE)
    if frozen.get("task") != "T103" or frozen.get("sourceElementFileIds") != EXPECTED:
        raise AcquireError("T103 exact source freeze/allowlist mismatch")
    calls: list[dict[str, Any]] = []
    transferred = 0
    selected_uncompressed = 0
    original_fetch = helper.fetch_range

    def fetch_recorded(url: str, start: int, end: int, etag: str):
        nonlocal transferred
        requested = end - start + 1
        if transferred + requested > MAX_RANGE_TRANSFER:
            raise AcquireError(f"selected archive ranges would exceed {MAX_RANGE_TRANSFER} bytes")
        data, headers = original_fetch(url, start, end, etag)
        transferred += len(data)
        calls.append({"url": url, "startByte": start, "endByte": end, "httpStatus": 206,
                      "contentRange": headers.get("content-range"), "etag": headers.get("etag"), "bytes": len(data)})
        if transferred > MAX_RANGE_TRANSFER:
            raise AcquireError("selected archive range transfer exceeded the T103 bound")
        return data, headers

    helper.fetch_range = fetch_recorded
    try:
        result = helper.acquire(FREEZE, OUT_ROOT, RECEIPT)
    finally:
        helper.fetch_range = original_fetch
    files = result.get("selectedSourceFiles", [])
    if (result.get("task") != "T103" or result.get("completeSourceFileCount") != len(EXPECTED)
            or sorted(row.get("sourceElementFileId") for row in files) != sorted(EXPECTED)
            or result.get("fullArchivesDownloaded") is not False):
        raise AcquireError("selected extraction did not return exactly the frozen ten IDs")
    for row in files:
        if row.get("archiveTree") != "IS-A" or Path(row.get("cacheRelativePath", "")).name != f"{row['sourceElementFileId']}.obj":
            raise AcquireError(f"selected archive member identity/path is unexpected: {row.get('sourceElementFileId')}")
        if row.get("bytes", 0) > MAX_SINGLE_MEMBER:
            raise AcquireError(f"selected OBJ exceeds {MAX_SINGLE_MEMBER} bytes: {row['sourceElementFileId']}")
        selected_uncompressed += row.get("bytes", 0)
        if selected_uncompressed > MAX_SELECTED_UNCOMPRESSED:
            raise AcquireError(f"selected OBJ payload exceeds {MAX_SELECTED_UNCOMPRESSED} bytes")
    receipt = {**result, "result": "pass", "selectedSourceFiles": files,
               "fullArchivesDownloaded": False, "rangeTransferBytes": transferred,
               "rangeResponses": calls,
               "bounds": {"maxRangeTransferBytes": MAX_RANGE_TRANSFER,
                          "maxCentralDirectoryBytes": MAX_CENTRAL_DIRECTORY,
                          "maxSelectedUncompressedBytes": MAX_SELECTED_UNCOMPRESSED,
                          "maxSingleMemberBytes": MAX_SINGLE_MEMBER}}
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the stored receipt and files without network access")
    args = parser.parse_args()
    if args.check:
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
        if receipt.get("task") != "T103" or receipt.get("result") != "pass" or receipt.get("frozenSourceSetSha256") != __import__("hashlib").sha256(FREEZE.read_bytes()).hexdigest():
            raise SystemExit("T103 stored acquisition receipt does not bind to its exact freeze")
        if sorted(row.get("sourceElementFileId") for row in receipt.get("selectedSourceFiles", [])) != sorted(frozen.get("sourceElementFileIds", [])):
            raise SystemExit("T103 stored receipt IDs differ from the freeze")
        for row in receipt["selectedSourceFiles"]:
            path = ROOT / row["cacheRelativePath"]
            if not path.is_file() or path.stat().st_size != row["bytes"]:
                raise SystemExit(f"T103 selected source file missing/size changed: {path}")
            import hashlib
            if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
                raise SystemExit(f"T103 selected source file hash changed: {path}")
        print(json.dumps({"result": "pass", "files": len(receipt["selectedSourceFiles"]), "offlineCheck": True}, indent=2))
    else:
        result = acquire()
        print(json.dumps({"result": result["result"], "files": result["completeSourceFileCount"],
                          "fullArchivesDownloaded": result["fullArchivesDownloaded"],
                          "rangeTransferBytes": result["rangeTransferBytes"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
