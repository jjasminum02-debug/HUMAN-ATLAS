#!/usr/bin/env python3
"""Acquire only T76's frozen nine IS-A OBJ members using official HTTP ranges."""
from __future__ import annotations

import argparse
import binascii
import hashlib
import importlib.util
import json
import re
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "work/evidence/T76/frozen-source-set.json"
OUT = ROOT / "work/evidence/T76/source-acquisition.json"
CACHE = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t76/pelvic-floor"
EXPECTED = ["FJ1453M", "FJ1457M", "FJ1458M", "FJ2544", "FJ2545", "FJ2546", "FJ2549", "FJ2550", "FJ2551"]
ARCHIVE_URL = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip"


class AcquisitionError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_helper():
    path = ROOT / "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py"
    spec = importlib.util.spec_from_file_location("ha_t76_selected_zip_helper", path)
    if spec is None or spec.loader is None:
        raise AcquisitionError(f"cannot import selected-member range helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_t76_central_directory(data: bytes, expected_entries: int) -> dict[str, dict[str, Any]]:
    """Retain explicit BodyParts3D FJ IDs ending in M; the older shared parser accepted digits only."""
    members: dict[str, dict[str, Any]] = {}
    cursor = 0
    while cursor < len(data):
        if cursor + 46 > len(data) or data[cursor:cursor + 4] != b"PK\x01\x02":
            raise AcquisitionError(f"invalid ZIP central directory at byte {cursor}")
        values = struct.unpack_from("<4s6H3L5H2L", data, cursor)
        (_, _made, _needed, flags, method, _mtime, _mdate, crc, compressed, uncompressed,
         name_len, extra_len, comment_len, disk_start, _internal, _external, local_offset) = values
        if disk_start or compressed == 0xFFFFFFFF or uncompressed == 0xFFFFFFFF or local_offset == 0xFFFFFFFF:
            raise AcquisitionError("ZIP64 or split-disk entry is outside the T76 selected-range profile")
        name_start = cursor + 46
        name_end = name_start + name_len
        record_end = name_end + extra_len + comment_len
        if record_end > len(data):
            raise AcquisitionError("truncated ZIP central-directory entry")
        encoding = "utf-8" if flags & 0x800 else "cp437"
        member_path = data[name_start:name_end].decode(encoding)
        base_name = member_path.rsplit("/", 1)[-1]
        match = re.fullmatch(r"(FJ[0-9]+M?)\.obj", base_name, flags=re.IGNORECASE)
        if match:
            file_id = match.group(1).upper()
            if file_id in members:
                raise AcquisitionError(f"duplicate FJ element ID in the official archive: {file_id}")
            members[file_id] = {
                "memberPath": member_path,
                "flags": flags,
                "compressionMethod": method,
                "crc32": crc,
                "compressedBytes": compressed,
                "uncompressedBytes": uncompressed,
                "localHeaderOffset": local_offset,
            }
        cursor = record_end
    if cursor != len(data):
        raise AcquisitionError("unexpected trailing bytes in ZIP central directory")
    if len(members) > expected_entries:
        raise AcquisitionError("parsed FJ OBJ count exceeds official archive entry count")
    return members


def load_freeze() -> tuple[dict[str, Any], bytes]:
    if not FREEZE.is_file():
        raise AcquisitionError("T76 frozen source set is missing")
    raw = FREEZE.read_bytes()
    data = json.loads(raw)
    if data.get("revision") != "BodyParts3D-R4-T76-FROZEN-PELVIC-FLOOR-SOURCE-SET-v1":
        raise AcquisitionError("T76 freeze revision mismatch")
    if data.get("status") != "frozen_before_mesh_acquisition" or data.get("archiveTree") != "IS-A":
        raise AcquisitionError("T76 freeze is not a pre-acquisition IS-A exact-source set")
    if data.get("newSourceElementFileIds") != EXPECTED:
        raise AcquisitionError("T76 exact allowlist differs from the authorized nine FJ IDs")
    rows = data.get("uniqueNewSourceAssets", [])
    if [row.get("sourceElementFileId") for row in rows] != EXPECTED:
        raise AcquisitionError("T76 frozen source rows do not exactly match the allowlist")
    batches = data.get("internalBatches", [])
    if len(batches) != 2 or [batch.get("count") for batch in batches] != [5, 4] or [fid for batch in batches for fid in batch.get("sourceElementFileIds", [])] != EXPECTED:
        raise AcquisitionError("T76 must remain exact internal batches of five and four")
    return data, raw


def next_attempt_path() -> Path:
    if not OUT.exists():
        return OUT
    index = 2
    while True:
        path = OUT.with_name(f"source-acquisition-attempt-{index:02d}.json")
        if not path.exists():
            return path
        index += 1


def successful_attempt() -> tuple[Path, dict[str, Any]]:
    paths = [OUT, *sorted(OUT.parent.glob("source-acquisition-attempt-*.json"))]
    for path in reversed(paths):
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("result") == "pass":
                return path, data
    raise AcquisitionError("no T76 selected-source acquisition attempt has passed")


def acquire() -> dict[str, Any]:
    frozen, frozen_raw = load_freeze()
    output_path = next_attempt_path()
    helper = load_helper()
    range_log: list[dict[str, Any]] = []
    active_id: str | None = None
    original_fetch = helper.fetch_range

    def fetch_logged(url: str, start: int, end: int, etag: str):
        body, headers = original_fetch(url, start, end, etag)
        range_log.append({
            "sourceElementFileId": active_id,
            "url": url,
            "start": start,
            "end": end,
            "httpStatus": 206,
            "contentRange": headers.get("content-range"),
            "etag": headers.get("etag"),
            "bytes": len(body),
        })
        return body, headers

    helper.fetch_range = fetch_logged
    result: dict[str, Any] = {
        "revision": "BodyParts3D-R4-T76-SELECTED-RANGE-ACQUISITION-v1",
        "task": "T76",
        "attemptNumber": 1 if output_path == OUT else int(output_path.stem.rsplit("-", 1)[-1]),
        "evidencePath": output_path.relative_to(ROOT).as_posix(),
        "attemptedAtUtc": datetime.now(timezone.utc).isoformat(),
        "frozenSourceSetSha256": sha(frozen_raw),
        "frozenMembershipSha256": frozen["targetConceptMembershipSha256"],
        "sourceVersion": "BodyParts3D Release 4.0",
        "archiveTree": "IS-A",
        "archiveUrl": ARCHIVE_URL,
        "attemptedIds": EXPECTED,
        "fullArchiveDownloaded": False,
        "selectedMemberRangeRequestsOnly": True,
        "requestsRequiredHttp206": True,
        "files": [],
        "failures": [],
    }
    metadata = None
    central_members: dict[str, dict[str, Any]] = {}
    try:
        metadata = helper.head_archive(ARCHIVE_URL)
        tail_size = min(metadata["contentLength"], 65557)
        tail_start = metadata["contentLength"] - tail_size
        tail, _ = helper.fetch_range(ARCHIVE_URL, tail_start, metadata["contentLength"] - 1, metadata["etag"])
        entry_count, cd_size, cd_offset = helper.parse_eocd(tail, metadata["contentLength"])
        central, _ = helper.fetch_range(ARCHIVE_URL, cd_offset, cd_offset + cd_size - 1, metadata["etag"])
        central_members = parse_t76_central_directory(central, entry_count)
        result["archiveMetadata"] = {
            **metadata,
            "zipCentralDirectoryEntries": entry_count,
            "centralDirectoryBytes": cd_size,
            "centralDirectoryStartByte": cd_offset,
            "archiveTailBytes": tail_size,
        }
    except Exception as exc:
        result["failures"].append({"phase": "archive_directory_access", "error": f"{type(exc).__name__}: {exc}"})

    if central_members:
        targets = {row["sourceElementFileId"]: row for row in frozen["uniqueNewSourceAssets"]}
        for fid in EXPECTED:
            active_id = fid
            if fid not in central_members:
                result["files"].append({"sourceElementFileId": fid, "status": "failed", "failure": "exact FJ OBJ absent from official IS-A archive central directory"})
                continue
            try:
                member = central_members[fid]
                payload, transfer_bytes = helper.selected_member_bytes(ARCHIVE_URL, metadata, member)
                digest = sha(payload)
                crc = f"{binascii.crc32(payload) & 0xffffffff:08x}"
                destination = CACHE / f"{fid}.obj"
                if destination.exists():
                    old = destination.read_bytes()
                    if old != payload:
                        raise AcquisitionError(f"refusing to replace different pre-existing source bytes for {fid}")
                    method = "existing_T76_cache_bytes_reverified_against_official_ranges"
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    temporary = destination.with_suffix(".obj.partial")
                    temporary.write_bytes(payload)
                    temporary.replace(destination)
                    method = "official_HTTP_206_selected_member_ranges"
                identity = targets[fid]
                result["files"].append({
                    "sourceElementFileId": fid,
                    "sourceConceptMemberships": identity["sourceConceptMemberships"],
                    "officialFmaBpNameCandidates": identity["officialFmaBpNameCandidates"],
                    "lateralityFromExactSideSpecificSourceConcepts": identity["lateralityFromExactSideSpecificSourceConcepts"],
                    "headerIdentityValidationPending": True,
                    "status": "acquired",
                    "method": method,
                    "memberPath": member["memberPath"],
                    "zipCompressionMethod": member["compressionMethod"],
                    "localHeaderOffset": member["localHeaderOffset"],
                    "bytes": len(payload),
                    "compressedBytes": member["compressedBytes"],
                    "rangeBytesRequested": transfer_bytes,
                    "crc32": crc,
                    "sha256": digest,
                    "cacheRelativePath": destination.relative_to(ROOT).as_posix(),
                })
            except Exception as exc:
                result["files"].append({"sourceElementFileId": fid, "status": "failed", "failure": f"{type(exc).__name__}: {exc}"})
        active_id = None
    else:
        result["files"] = [
            {"sourceElementFileId": fid, "status": "failed", "failure": "official archive metadata/index unavailable; full-download fallback is forbidden"}
            for fid in EXPECTED
        ]

    acquired = [row for row in result["files"] if row.get("status") == "acquired"]
    range_ok = bool(range_log) and all(row["httpStatus"] == 206 for row in range_log)
    result.update({
        "rangeRequests": range_log,
        "allRangeResponsesHttp206": range_ok,
        "selectedMemberCount": len(acquired),
        "failedCount": len(result["files"]) - len(acquired),
        "selectedPayloadBytes": sum(row["bytes"] for row in acquired),
        "fullArchiveDownloaded": False,
        "rightsBoundary": "redistribution_held_pending_reconciliation_of_current_CC_BY_4.0_database_terms_and_legacy_per_OBJ_CC_BY_SA_2.1_Japan_header",
        "humanAnatomyReview": "not_performed",
        "result": "pass" if len(acquired) == len(EXPECTED) and not result["failures"] and len(range_log) == 29 and range_ok else "partial_or_failed",
    })
    write_json(output_path, result)
    return result


def check() -> dict[str, Any]:
    frozen, frozen_raw = load_freeze()
    attempt_path, data = successful_attempt()
    if data.get("frozenSourceSetSha256") != sha(frozen_raw) or data.get("frozenMembershipSha256") != frozen["targetConceptMembershipSha256"]:
        raise AcquisitionError("T76 acquisition evidence is not bound to frozen source set")
    if data.get("fullArchiveDownloaded") is not False or data.get("selectedMemberRangeRequestsOnly") is not True:
        raise AcquisitionError("T76 acquisition violates selected-range policy")
    if data.get("result") != "pass" or data.get("attemptedIds") != EXPECTED:
        raise AcquisitionError("T76 selected acquisition did not pass the exact frozen nine")
    requests = data.get("rangeRequests", [])
    if len(requests) != 29 or not data.get("allRangeResponsesHttp206"):
        raise AcquisitionError(f"T76 expects 2 archive-index ranges plus 3 selected member ranges x 9; found {len(requests)}")
    etag = data.get("archiveMetadata", {}).get("etag")
    for row in requests:
        if row.get("httpStatus") != 206 or row.get("bytes") != row.get("end", -1) - row.get("start", 0) + 1:
            raise AcquisitionError("T76 range record has invalid HTTP status or interval size")
        if row.get("url") != ARCHIVE_URL or row.get("etag") != etag:
            raise AcquisitionError("T76 archive URL or ETag changed within selected retrieval")
    by_id = {row.get("sourceElementFileId"): row for row in data.get("files", [])}
    if set(by_id) != set(EXPECTED) or any(by_id[fid].get("status") != "acquired" for fid in EXPECTED):
        raise AcquisitionError("T76 acquisition records do not exactly cover the nine frozen files")
    for fid, row in by_id.items():
        if row.get("memberPath") != f"isa_BP3D_4.0_obj_99/{fid}.obj":
            raise AcquisitionError(f"T76 archive member path is not the frozen IS-A entry: {fid}")
        path = ROOT / row["cacheRelativePath"]
        raw = path.read_bytes()
        if len(raw) != row.get("bytes") or sha(raw) != row.get("sha256") or f"{binascii.crc32(raw) & 0xffffffff:08x}" != row.get("crc32", "").lower():
            raise AcquisitionError(f"T76 cached source size/SHA/CRC mismatch: {fid}")
    return {"result": "pass", "evidencePath": attempt_path.relative_to(ROOT).as_posix(), "frozenCount": 9, "acquiredCount": 9, "failedCount": 0, "fullArchiveDownloaded": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--acquire", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = acquire() if args.acquire else check()
        print(json.dumps(result if args.check else {
            "result": result["result"], "selectedMemberCount": result["selectedMemberCount"],
            "failedCount": result["failedCount"], "fullArchiveDownloaded": result["fullArchiveDownloaded"],
            "rangeRequestCount": len(result["rangeRequests"]), "selectedPayloadBytes": result["selectedPayloadBytes"],
        }, ensure_ascii=False, indent=2))
        return 0 if result.get("result") == "pass" else 2
    except Exception as exc:
        print(f"T76 source acquisition failed closed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
