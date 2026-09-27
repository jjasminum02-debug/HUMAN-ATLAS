#!/usr/bin/env python3
"""Acquire only T74's frozen BodyParts3D R4 OBJ members via HTTP ranges."""
from __future__ import annotations

import argparse
import binascii
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "work/evidence/T74/frozen-source-set.json"
OUT = ROOT / "work/evidence/T74/source-acquisition.json"
CACHE = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t74/head"
EXPECTED = ["FJ3274", "FJ3386", "FJ3281", "FJ3392", "FJ3287", "FJ3375", "FJ3269", "FJ3378", "FJ3272"]


class AcquisitionError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AcquisitionError(f"cannot load range helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_freeze() -> tuple[dict[str, Any], bytes]:
    if not FREEZE.is_file():
        raise AcquisitionError("T74 exact-source freeze is missing")
    raw = FREEZE.read_bytes()
    frozen = json.loads(raw)
    if frozen.get("revision") != "BodyParts3D-R4-T74-FROZEN-EXACT-SOURCE-SET-v1" or frozen.get("status") != "frozen_before_mesh_acquisition":
        raise AcquisitionError("T74 freeze revision/status mismatch")
    if frozen.get("archiveTree") != "PART-OF" or frozen.get("sourceElementFileIds") != EXPECTED:
        raise AcquisitionError("T74 freeze is not the exact authorized PART-OF allowlist")
    if [row.get("sourceElementFileId") for row in frozen.get("uniqueNewSourceAssets", [])] != EXPECTED:
        raise AcquisitionError("T74 frozen mapping rows differ from the exact allowlist")
    if [len(row.get("sourceElementFileIds", [])) for row in frozen.get("internalBatches", [])] != [5, 4]:
        raise AcquisitionError("T74 expected 5+4 internal batch split changed")
    canonical = "".join(
        f"{row['sourceConceptId']}|{row['sourceRepresentationId']}|{row['sourceElementFileId']}|{row['sourceNameEnglish']}|{row['side']}|PART-OF\n"
        for row in frozen["uniqueNewSourceAssets"]
    )
    if sha(canonical.encode("utf-8")) != frozen.get("frozenMembershipSha256"):
        raise AcquisitionError("T74 frozen membership hash is invalid")
    if set(frozen.get("reuseOnly", {})) != {"FJ3380", "FJ3200", "FJ3289", "FJ3309"}:
        raise AcquisitionError("T74 reuse-only list must preserve the four existing IDs")
    return frozen, raw


def attempt_acquisition() -> dict[str, Any]:
    frozen, freeze_raw = validate_freeze()
    helper = load_module("ha_t74_selected_range", ROOT / "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py")
    url = frozen["archiveUrl"]
    range_log: list[dict[str, Any]] = []
    active_file_id: str | None = None
    original_fetch_range = helper.fetch_range

    def fetch_range_logged(request_url: str, start: int, end: int, etag: str):
        body, headers = original_fetch_range(request_url, start, end, etag)
        range_log.append({
            "sourceElementFileId": active_file_id,
            "url": request_url,
            "start": start,
            "end": end,
            "httpStatus": 206,
            "contentRange": headers.get("content-range"),
            "etag": headers.get("etag"),
            "bytes": len(body),
        })
        return body, headers

    helper.fetch_range = fetch_range_logged
    attempt: dict[str, Any] = {
        "revision": "BodyParts3D-R4-T74-SELECTED-RANGE-ACQUISITION-v1",
        "task": "T74",
        "attemptedAt": datetime.now(timezone.utc).isoformat(),
        "frozenSourceSetSha256": sha(freeze_raw),
        "frozenMembershipSha256": frozen["frozenMembershipSha256"],
        "archiveUrl": url,
        "archiveTree": "PART-OF",
        "sourceVersion": "BodyParts3D Release 4.0",
        "fullArchiveDownloaded": False,
        "requestsRequiredHttp206": True,
        "selectedMemberRangeRequestsOnly": True,
        "frozenCount": len(EXPECTED),
        "attemptedIds": EXPECTED,
        "files": [],
        "failures": [],
    }
    meta = None
    members: dict[str, dict[str, Any]] = {}
    try:
        meta = helper.head_archive(url)
        tail_size = min(meta["contentLength"], 65557)
        tail_start = meta["contentLength"] - tail_size
        tail, _ = helper.fetch_range(url, tail_start, meta["contentLength"] - 1, meta["etag"])
        count, cd_size, cd_offset = helper.parse_eocd(tail, meta["contentLength"])
        central, _ = helper.fetch_range(url, cd_offset, cd_offset + cd_size - 1, meta["etag"])
        members = helper.parse_central_directory(central, count)
        attempt["archiveMetadata"] = {
            **meta,
            "zipCentralDirectoryEntries": count,
            "centralDirectoryBytes": cd_size,
            "centralDirectoryStartByte": cd_offset,
            "archiveTailBytes": tail_size,
        }
    except Exception as exc:
        attempt["failures"].append({"phase": "archive_directory_access", "error": f"{type(exc).__name__}: {exc}"})

    frozen_by_id = {row["sourceElementFileId"]: row for row in frozen["uniqueNewSourceAssets"]}
    if members:
        for fid in EXPECTED:
            active_file_id = fid
            row = frozen_by_id[fid]
            if fid not in members:
                attempt["files"].append({"sourceElementFileId": fid, "status": "failed", "failure": "exact FJ OBJ absent from frozen PART-OF archive central directory"})
                continue
            try:
                payload, total_member_bytes = helper.selected_member_bytes(url, meta, members[fid])
                crc = f"{binascii.crc32(payload) & 0xffffffff:08x}"
                destination = CACHE / f"{fid}.obj"
                digest = sha(payload)
                if destination.exists():
                    existing = destination.read_bytes()
                    if existing != payload:
                        raise AcquisitionError(f"refusing to overwrite non-matching pre-existing source bytes: {fid}")
                    method = "preexisting_T74_cache_reverified_against_official_selected_ranges"
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    temp = destination.with_suffix(".obj.partial")
                    temp.write_bytes(payload)
                    temp.replace(destination)
                    method = "official_HTTP_206_selected_member_ranges"
                member = members[fid]
                attempt["files"].append({
                    "sourceElementFileId": fid,
                    "sourceConceptId": row["sourceConceptId"],
                    "sourceRepresentationId": row["sourceRepresentationId"],
                    "sourceNameEnglish": row["sourceNameEnglish"],
                    "side": row["side"],
                    "status": "acquired",
                    "sourceAcquisitionMethod": method,
                    "memberPath": member["memberPath"],
                    "zipCompressionMethod": member["compressionMethod"],
                    "centralDirectoryLocalHeaderOffset": member["localHeaderOffset"],
                    "crc32": crc,
                    "bytes": len(payload),
                    "compressedBytes": member["compressedBytes"],
                    "memberTransferBytes": total_member_bytes,
                    "sha256": digest,
                    "cacheRelativePath": destination.relative_to(ROOT).as_posix(),
                })
            except Exception as exc:
                attempt["files"].append({"sourceElementFileId": fid, "status": "failed", "failure": f"{type(exc).__name__}: {exc}"})
        active_file_id = None
    else:
        attempt["files"] = [{"sourceElementFileId": fid, "status": "failed", "failure": "archive directory unavailable; no full-download fallback attempted"} for fid in EXPECTED]

    acquired = [row for row in attempt["files"] if row.get("status") == "acquired"]
    failed = [row for row in attempt["files"] if row.get("status") != "acquired"]
    attempt.update({
        "rangeRequests": range_log,
        "allRangeResponsesHttp206": all(row["httpStatus"] == 206 for row in range_log),
        "acquiredCount": len(acquired),
        "failedCount": len(failed),
        "selectedPayloadBytes": sum(row["bytes"] for row in acquired),
        "fullArchiveDownloaded": False,
        "result": "pass" if len(acquired) == len(EXPECTED) and not attempt["failures"] else "partial_or_failed",
        "rightsBoundary": "redistribution held pending reconciliation of official current CC BY 4.0 notice and legacy OBJ header CC BY-SA 2.1 Japan wording",
        "humanAnatomyReview": "not_performed",
    })
    if OUT.exists():
        old = json.loads(OUT.read_text(encoding="utf-8"))
        if old.get("frozenSourceSetSha256") != attempt["frozenSourceSetSha256"]:
            raise AcquisitionError("existing T74 acquisition evidence belongs to another freeze")
        old_hashes = {row["sourceElementFileId"]: row.get("sha256") for row in old.get("files", []) if row.get("status") == "acquired"}
        new_hashes = {row["sourceElementFileId"]: row.get("sha256") for row in acquired}
        if any(fid not in new_hashes or old_hash != new_hashes[fid] for fid, old_hash in old_hashes.items()):
            raise AcquisitionError("refusing to change or lose a previously verified T74 source member")
    write_json(OUT, attempt)
    return attempt


def check() -> dict[str, Any]:
    frozen, freeze_raw = validate_freeze()
    if not OUT.is_file():
        raise AcquisitionError("T74 source-acquisition record missing")
    manifest = json.loads(OUT.read_text(encoding="utf-8"))
    if manifest.get("frozenSourceSetSha256") != sha(freeze_raw) or manifest.get("frozenMembershipSha256") != frozen["frozenMembershipSha256"]:
        raise AcquisitionError("T74 acquisition evidence is not bound to frozen source set")
    if manifest.get("fullArchiveDownloaded") is not False or manifest.get("selectedMemberRangeRequestsOnly") is not True:
        raise AcquisitionError("T74 acquisition violates range-only policy")
    requests = manifest.get("rangeRequests", [])
    if not requests or not manifest.get("allRangeResponsesHttp206"):
        raise AcquisitionError("T74 exact byte-range request evidence is missing or not all HTTP 206")
    if len(requests) != 29:
        raise AcquisitionError(f"T74 must have 2 archive metadata ranges plus three member ranges for each of 9 IDs; found {len(requests)}")
    for request in requests:
        if request.get("httpStatus") != 206 or request.get("bytes") != request.get("end", -1) - request.get("start", 0) + 1:
            raise AcquisitionError("T74 range record has an unverified status or byte interval")
        if request.get("url") != manifest.get("archiveUrl") or request.get("etag") != manifest.get("archiveMetadata", {}).get("etag"):
            raise AcquisitionError("T74 range URL or archive ETag changed during acquisition")
    rows = {row["sourceElementFileId"]: row for row in manifest.get("files", [])}
    if set(rows) != set(EXPECTED) or len(rows) != len(EXPECTED):
        raise AcquisitionError("T74 acquisition manifest IDs differ from frozen allowlist")
    for fid, row in rows.items():
        if row.get("status") != "acquired":
            continue
        path = ROOT / row["cacheRelativePath"]
        payload = path.read_bytes()
        if len(payload) != row["bytes"] or sha(payload) != row["sha256"] or f"{binascii.crc32(payload) & 0xffffffff:08x}" != row["crc32"]:
            raise AcquisitionError(f"T74 cached source hash/CRC/size mismatch for {fid}")
    acquired = sum(row.get("status") == "acquired" for row in rows.values())
    return {"result": "pass" if acquired == len(EXPECTED) else "partial_or_failed", "frozenCount": len(EXPECTED), "acquiredCount": acquired, "failedCount": len(EXPECTED) - acquired, "fullArchiveDownloaded": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--acquire", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = attempt_acquisition() if args.acquire else check()
    except Exception as exc:
        print(f"T74 acquisition tool error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.acquire:
        return 0 if result["result"] == "pass" else 1
    return 0 if result["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
