#!/usr/bin/env python3
"""Range-acquire only T79's frozen ten BodyParts3D R4 IS-A OBJ members."""
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
FREEZE = ROOT / "work/evidence/T79/frozen-source-set.json"
OUT = ROOT / "work/evidence/T79/source-acquisition.json"
CACHE = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t79"
ARCHIVE_URL = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip"
EXPECTED = ["FJ1512", "FJ1512M", "FJ1478", "FJ1478M", "FJ1479", "FJ1479M", "FJ1480", "FJ1480M", "FJ1477", "FJ1477M"]
FJ_OBJ = re.compile(r"^(FJ[0-9]+M?)\.obj$", re.IGNORECASE)


class AcquisitionError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_helper():
    path = ROOT / "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py"
    spec = importlib.util.spec_from_file_location("ha_t79_range_helper", path)
    if spec is None or spec.loader is None:
        raise AcquisitionError(f"cannot load existing R4 selected-member helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_exact_members(data: bytes, expected_entries: int) -> dict[str, dict[str, Any]]:
    members: dict[str, dict[str, Any]] = {}
    cursor = 0
    while cursor < len(data):
        if cursor + 46 > len(data) or data[cursor:cursor + 4] != b"PK\x01\x02":
            raise AcquisitionError(f"invalid ZIP central-directory record at {cursor}")
        fields = struct.unpack_from("<4s6H3L5H2L", data, cursor)
        (_, _made, _needed, flags, method, _mtime, _mdate, crc, compressed, uncompressed,
         name_len, extra_len, comment_len, disk_start, _internal, _external, local_offset) = fields
        if disk_start or compressed == 0xFFFFFFFF or uncompressed == 0xFFFFFFFF or local_offset == 0xFFFFFFFF:
            raise AcquisitionError("ZIP64 or split-disk entry is outside the selected-member tool profile")
        name_start = cursor + 46
        name_end = name_start + name_len
        record_end = name_end + extra_len + comment_len
        if record_end > len(data):
            raise AcquisitionError("truncated ZIP central-directory record")
        encoding = "utf-8" if flags & 0x800 else "cp437"
        member_path = data[name_start:name_end].decode(encoding)
        match = FJ_OBJ.fullmatch(member_path.rsplit("/", 1)[-1])
        if match:
            file_id = match.group(1).upper()
            if file_id in members:
                raise AcquisitionError(f"duplicate FJ member in official archive: {file_id}")
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
    if cursor != len(data) or len(members) > expected_entries:
        raise AcquisitionError("unexpected central-directory ending or FJ inventory larger than archive entry count")
    return members


def parse_header(raw: bytes) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in raw.decode("utf-8", errors="strict").splitlines():
        if not line.startswith("#"):
            break
        match = re.match(r"^#\s*([^:]+):\s*(.*)$", line)
        if match:
            result[match.group(1).strip()] = match.group(2).strip()
    return result


def validate_header(raw: bytes, row: dict[str, Any]) -> dict[str, Any]:
    header = parse_header(raw)
    expected = {
        "File ID": row["sourceElementFileId"],
        "Representation ID": row["sourceRepresentationId"],
        "Build-up logic": "FMA 3.0 is_a",
        "Concept ID": row["sourceConceptId"],
        "English name": row["sourceNameEnglish"],
    }
    mismatch = {
        key: {"expected": value, "actual": header.get(key)}
        for key, value in expected.items()
        if key != "English name" and header.get(key) != value
    }
    if header.get("English name", "").casefold() != row["sourceNameEnglish"].casefold():
        mismatch["English name"] = {
            "expectedCaseInsensitive": row["sourceNameEnglish"],
            "actual": header.get("English name"),
            "preservedVerbatim": True,
        }
    if mismatch:
        raise AcquisitionError(f"official OBJ header disagrees with exact IS-A metadata for {row['sourceElementFileId']}: {mismatch}")
    if "Bounds(mm)" not in header or "License ID" in header:
        raise AcquisitionError(f"missing expected R4 millimeter bounds header for {row['sourceElementFileId']}")
    return header


def freeze() -> tuple[dict[str, Any], bytes]:
    if not FREEZE.is_file():
        raise AcquisitionError("T79 frozen source set is missing")
    raw = FREEZE.read_bytes()
    doc = json.loads(raw)
    if doc.get("revision") != "BodyParts3D-R4-T79-FROZEN-BILATERAL-BICEPS-TRICEPS-v1" or doc.get("status") != "frozen_before_mesh_acquisition":
        raise AcquisitionError("T79 freeze revision/status mismatch")
    if doc.get("archiveTree") != "IS-A" or doc.get("sourceElementFileIds") != EXPECTED:
        raise AcquisitionError("T79 exact source allowlist mismatch")
    if [row.get("sourceElementFileId") for row in doc.get("uniqueNewSourceAssets", [])] != EXPECTED:
        raise AcquisitionError("T79 source mapping rows differ from the exact allowlist")
    batches = doc.get("internalBatches", [])
    if len(batches) != 1 or batches[0].get("count") != 10 or batches[0].get("sourceElementFileIds") != EXPECTED:
        raise AcquisitionError("T79 must remain one bounded ten-member batch")
    return doc, raw


def next_attempt() -> Path:
    if not OUT.exists():
        return OUT
    index = 2
    while True:
        candidate = OUT.with_name(f"source-acquisition-attempt-{index:02d}.json")
        if not candidate.exists():
            return candidate
        index += 1


def prior_verified_rows() -> dict[str, tuple[Path, dict[str, Any]]]:
    rows: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in [OUT, *sorted(OUT.parent.glob("source-acquisition-attempt-*.json"))]:
        if not path.is_file():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("frozenSourceSetSha256") != sha(FREEZE.read_bytes()):
            continue
        for row in doc.get("files", []):
            fid = row.get("sourceElementFileId")
            if fid in EXPECTED and row.get("status") == "acquired":
                rows[fid] = (path, row)
    return rows


def acquire() -> dict[str, Any]:
    frozen, frozen_raw = freeze()
    path = next_attempt()
    helper = load_helper()
    requests: list[dict[str, Any]] = []
    active_id: str | None = None
    original_fetch = helper.fetch_range

    def fetch_logged(url: str, start: int, end: int, etag: str):
        body, headers = original_fetch(url, start, end, etag)
        requests.append({
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
        "revision": "BodyParts3D-R4-T79-SELECTED-RANGE-ACQUISITION-v1",
        "task": "T79",
        "attemptNumber": 1 if path == OUT else int(path.stem.rsplit("-", 1)[-1]),
        "evidencePath": path.relative_to(ROOT).as_posix(),
        "attemptedAtUtc": datetime.now(timezone.utc).isoformat(),
        "sourceVersion": "BodyParts3D Release 4.0",
        "archiveTree": "IS-A",
        "archiveUrl": ARCHIVE_URL,
        "frozenSourceSetSha256": sha(frozen_raw),
        "frozenMembershipSha256": frozen["membershipSha256"],
        "attemptedIds": EXPECTED,
        "fullArchiveDownloaded": False,
        "selectedMemberRangeRequestsOnly": True,
        "requestsRequiredHttp206": True,
        "files": [],
        "failures": [],
        "rangeRequests": requests,
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
        central_members = parse_exact_members(central, entry_count)
        result["archiveMetadata"] = {**metadata, "centralDirectoryEntries": entry_count, "centralDirectoryBytes": cd_size, "centralDirectoryStartByte": cd_offset, "archiveTailBytes": tail_size}
        absent = sorted(set(EXPECTED) - central_members.keys())
        if absent:
            raise AcquisitionError(f"official IS-A archive index is missing frozen IDs: {absent}")
    except Exception as exc:
        result["failures"].append({"phase": "archive_index_access", "error": f"{type(exc).__name__}: {exc}"})

    rows = {row["sourceElementFileId"]: row for row in frozen["uniqueNewSourceAssets"]}
    prior = prior_verified_rows()
    if central_members and metadata:
        for fid in EXPECTED:
            active_id = fid
            try:
                destination = CACHE / f"{fid}.obj"
                previous = prior.get(fid)
                if destination.is_file() and previous is not None:
                    previous_path, previous_row = previous
                    cached = destination.read_bytes()
                    if len(cached) != previous_row.get("bytes") or sha(cached) != previous_row.get("sha256") or f"{binascii.crc32(cached) & 0xffffffff:08x}" != previous_row.get("crc32"):
                        raise AcquisitionError(f"existing cached bytes no longer match their prior successful range record: {fid}")
                    header = validate_header(cached, rows[fid])
                    result["files"].append({
                        **previous_row,
                        "status": "acquired",
                        "sourceAcquisitionMethod": "previous_selected_range_payload_reverified_in_T79_cache",
                        "reusedFromEvidencePath": previous_path.relative_to(ROOT).as_posix(),
                        "header": header,
                    })
                    continue
                member = central_members[fid]
                last_error = None
                payload = None
                transferred = 0
                for retry in range(3):
                    try:
                        payload, transferred = helper.selected_member_bytes(ARCHIVE_URL, metadata, member)
                        result.setdefault("selectedMemberRetryCount", 0)
                        result["selectedMemberRetryCount"] += retry
                        break
                    except Exception as exc:
                        last_error = exc
                        if retry == 2:
                            raise
                if payload is None:
                    raise last_error or AcquisitionError(f"no payload returned for {fid}")
                header = validate_header(payload, rows[fid])
                digest = sha(payload)
                if destination.exists() and destination.read_bytes() != payload:
                    raise AcquisitionError(f"refusing to overwrite non-matching existing source bytes for {fid}")
                if not destination.exists():
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    temp = destination.with_suffix(".obj.partial")
                    temp.write_bytes(payload)
                    temp.replace(destination)
                result["files"].append({
                    **rows[fid],
                    "status": "acquired",
                    "sourceAcquisitionMethod": "official_HTTP_206_selected_member_byte_ranges",
                    "memberPath": member["memberPath"],
                    "zipCompressionMethod": member["compressionMethod"],
                    "centralDirectoryLocalHeaderOffset": member["localHeaderOffset"],
                    "crc32": f"{binascii.crc32(payload) & 0xffffffff:08x}",
                    "bytes": len(payload),
                    "compressedBytes": member["compressedBytes"],
                    "memberTransferBytes": transferred,
                    "sha256": digest,
                    "cacheRelativePath": destination.relative_to(ROOT).as_posix(),
                    "header": header,
                })
            except Exception as exc:
                result["files"].append({"sourceElementFileId": fid, "status": "failed", "failure": f"{type(exc).__name__}: {exc}"})
        active_id = None
    else:
        result["files"] = [{"sourceElementFileId": fid, "status": "not_acquired", "failure": "archive metadata/index unavailable; no full-archive fallback attempted"} for fid in EXPECTED]

    for request in requests:
        if request["httpStatus"] != 206 or request["bytes"] != request["end"] - request["start"] + 1:
            result["failures"].append({"phase": "range_validation", "error": "invalid partial-content range response", "request": request})
    result["allRangeResponsesHttp206"] = bool(requests) and all(request["httpStatus"] == 206 for request in requests)
    result["acquiredCount"] = sum(row.get("status") == "acquired" for row in result["files"])
    result["failedCount"] = 10 - result["acquiredCount"]
    result["selectedPayloadBytes"] = sum(row.get("bytes", 0) for row in result["files"])
    result["rightsBoundary"] = {
        "localDisplay": "not adjudicated until per-file header/mesh/scene validation; local engineering QA only",
        "publicRedistribution": "held pending reconciliation of the embedded CC BY-SA 2.1 Japan notice and current official database terms",
        "humanAnatomyReview": "not_performed",
    }
    result["result"] = "pass" if result["acquiredCount"] == 10 and not result["failures"] and result["allRangeResponsesHttp206"] else "partial_or_failed"
    write_json(path, result)
    return result


def check() -> dict[str, Any]:
    frozen, frozen_raw = freeze()
    candidates = [OUT, *sorted(OUT.parent.glob("source-acquisition-attempt-*.json"))]
    passed = []
    for path in candidates:
        if not path.is_file():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("result") == "pass":
            passed.append((path, doc))
    if not passed:
        return {"result": "partial_or_failed", "acquiredCount": 0, "expectedCount": 10, "reason": "no successful bounded range-acquisition attempt"}
    path, doc = passed[-1]
    if doc.get("frozenSourceSetSha256") != sha(frozen_raw) or doc.get("attemptedIds") != EXPECTED or doc.get("fullArchiveDownloaded") is not False or doc.get("selectedMemberRangeRequestsOnly") is not True:
        raise AcquisitionError("successful acquisition is not bound to exact T79 freeze or violates the range-only policy")
    rows = {row["sourceElementFileId"]: row for row in doc.get("files", [])}
    if set(rows) != set(EXPECTED) or len(rows) != 10:
        raise AcquisitionError("successful T79 acquisition does not contain exactly ten IDs")
    for fid in EXPECTED:
        row = rows[fid]
        if row.get("status") != "acquired":
            raise AcquisitionError(f"successful acquisition is missing {fid}")
        payload = (ROOT / row["cacheRelativePath"]).read_bytes()
        if len(payload) != row["bytes"] or sha(payload) != row["sha256"] or f"{binascii.crc32(payload) & 0xffffffff:08x}" != row["crc32"]:
            raise AcquisitionError(f"source bytes/CRC/SHA mismatch: {fid}")
        validate_header(payload, row)
    return {"result": "pass", "evidencePath": path.relative_to(ROOT).as_posix(), "acquiredCount": 10, "expectedCount": 10, "fullArchiveDownloaded": False, "rangeRequestCount": len(doc["rangeRequests"])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--acquire", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = acquire() if args.acquire else check()
    except Exception as exc:
        print(f"T79 acquisition failed closed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("result") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
