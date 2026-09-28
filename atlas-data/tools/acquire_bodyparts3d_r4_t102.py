#!/usr/bin/env python3
"""Acquire only T102's frozen ten BodyParts3D R4 OBJ members by HTTP range."""
from __future__ import annotations

import argparse
import binascii
import hashlib
import importlib.util
import json
import re
import stat
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "work/evidence/T102/frozen-source-set.json"
OUT = ROOT / "work/evidence/T102/source-acquisition.json"
CACHE_ROOT = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t102"
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
HELPER = ROOT / "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py"
INGEST = ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py"
ARCHIVE_URL = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip"
EXPECTED = ["FJ1441", "FJ1441M", "FJ1442", "FJ1442M", "FJ1443", "FJ1443M", "FJ1444", "FJ1444M", "FJ1445", "FJ1445M"]
FJ_OBJ = re.compile(r"^(FJ[0-9]+M?)\.obj$", re.IGNORECASE)
MAX_CENTRAL_DIRECTORY_BYTES = 64_000_000
MAX_RANGE_TRANSFER_BYTES = 120_000_000
MAX_SELECTED_UNCOMPRESSED_BYTES = 1_000_000_000
MAX_SELECTED_FILE_BYTES = 200_000_000


class AcquisitionError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AcquisitionError(f"cannot load existing R4 helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def selected_central_members(data: bytes, expected_entries: int) -> dict[str, dict[str, Any]]:
    """Index names safely; never extract ZIP paths to disk."""
    members: dict[str, dict[str, Any]] = {}
    cursor = 0
    entries = 0
    while cursor < len(data):
        if cursor + 46 > len(data) or data[cursor:cursor + 4] != b"PK\x01\x02":
            raise AcquisitionError(f"invalid ZIP central-directory record at byte {cursor}")
        fields = struct.unpack_from("<4s6H3L5H2L", data, cursor)
        (_, made, _needed, flags, method, _mtime, _mdate, crc, compressed, uncompressed,
         name_len, extra_len, comment_len, disk_start, _internal, external, local_offset) = fields
        if disk_start or compressed == 0xFFFFFFFF or uncompressed == 0xFFFFFFFF or local_offset == 0xFFFFFFFF:
            raise AcquisitionError("ZIP64/split-disk entries are outside the existing selected-member helper profile")
        name_start = cursor + 46
        name_end = name_start + name_len
        record_end = name_end + extra_len + comment_len
        if record_end > len(data):
            raise AcquisitionError("truncated ZIP central directory")
        encoding = "utf-8" if flags & 0x800 else "cp437"
        name = data[name_start:name_end].decode(encoding, errors="strict")
        if not name or "\\" in name or "\x00" in name:
            raise AcquisitionError(f"unsafe ZIP member name rejected: {name!r}")
        path = PurePosixPath(name)
        if path.is_absolute() or any(part in {".", ".."} for part in path.parts):
            raise AcquisitionError(f"path traversal or absolute ZIP member rejected: {name!r}")
        cursor = record_end
        entries += 1
        match = FJ_OBJ.fullmatch(path.name)
        if match is None:
            continue
        file_id = match.group(1).upper()
        if file_id not in EXPECTED:
            continue
        if file_id in members:
            raise AcquisitionError(f"duplicate frozen FJ member in official archive: {file_id}")
        file_type = (external >> 16) & 0o170000
        if file_type == stat.S_IFLNK:
            raise AcquisitionError(f"selected source member is a symlink: {name}")
        if file_type not in (0, stat.S_IFREG):
            raise AcquisitionError(f"selected source member is not a regular file: {name}")
        if uncompressed > MAX_SELECTED_FILE_BYTES:
            raise AcquisitionError(f"selected OBJ exceeds per-file bound: {file_id} {uncompressed} bytes")
        members[file_id] = {
            "memberPath": name,
            "flags": flags,
            "compressionMethod": method,
            "crc32": crc,
            "compressedBytes": compressed,
            "uncompressedBytes": uncompressed,
            "localHeaderOffset": local_offset,
            "unixMode": (external >> 16) & 0xFFFF,
            "madeBy": made,
        }
    if cursor != len(data) or entries != expected_entries:
        raise AcquisitionError(f"ZIP central-directory entry count/length mismatch: parsed {entries}/{len(data)}, expected {expected_entries}")
    absent = sorted(set(EXPECTED) - members.keys())
    if absent:
        raise AcquisitionError(f"official IS-A archive index missing frozen IDs: {absent}")
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


def acquire() -> dict[str, Any]:
    if not FREEZE.is_file():
        raise AcquisitionError("T102 source freeze is missing; do not acquire un-frozen members")
    frozen_raw = FREEZE.read_bytes()
    frozen = json.loads(frozen_raw)
    if frozen.get("task") != "T102" or frozen.get("status") != "frozen_before_mesh_acquisition" or frozen.get("sourceElementFileIds") != EXPECTED:
        raise AcquisitionError("T102 exact frozen source allowlist/revision mismatch")
    assets = frozen.get("assets", [])
    if [row.get("sourceElementFileId") for row in assets] != EXPECTED:
        raise AcquisitionError("T102 frozen mapping rows differ from exact ordered allowlist")

    helper = load_module("ha_t101_r4_range_helper", HELPER)
    ingest = load_module("ha_t101_r4_ingest", INGEST)
    tables = ingest.load_tables(METADATA)
    archive_url = ARCHIVE_URL
    requests: list[dict[str, Any]] = []
    active_id: str | None = None
    original_fetch_range = helper.fetch_range

    def fetch_logged(url: str, start: int, end: int, etag: str):
        requested_bytes = end - start + 1
        if sum(row["bytes"] for row in requests) + requested_bytes > MAX_RANGE_TRANSFER_BYTES:
            raise AcquisitionError("selected HTTP range would exceed the 120 MB task safety bound")
        body, headers = original_fetch_range(url, start, end, etag)
        requests.append({"sourceElementFileId": active_id, "url": url, "start": start, "end": end,
                         "httpStatus": 206, "contentRange": headers.get("content-range"),
                         "etag": headers.get("etag"), "bytes": len(body)})
        if sum(row["bytes"] for row in requests) > MAX_RANGE_TRANSFER_BYTES:
            raise AcquisitionError("selected HTTP range bytes exceeded the 120 MB task safety bound")
        return body, headers

    helper.fetch_range = fetch_logged
    receipt: dict[str, Any] = {
        "revision": "BodyParts3D-R4-T102-SELECTED-RANGE-ACQUISITION-v1",
        "task": "T102",
        "attemptedAtUtc": datetime.now(timezone.utc).isoformat(),
        "sourceVersion": "BodyParts3D Release 4.0",
        "archiveTree": "IS-A",
        "archiveUrl": archive_url,
        "frozenSourceSetSha256": sha(frozen_raw),
        "frozenMembershipSha256": frozen["membershipSha256"],
        "attemptedIds": EXPECTED,
        "fullArchiveDownloaded": False,
        "selectedMemberRangeRequestsOnly": True,
        "rangeResponsesRequiredHttp206": True,
        "maxRangeTransferBytes": MAX_RANGE_TRANSFER_BYTES,
        "maxSelectedUncompressedBytes": MAX_SELECTED_UNCOMPRESSED_BYTES,
        "files": [],
        "failures": [],
        "rangeRequests": requests,
    }
    try:
        meta = helper.head_archive(archive_url)
        tail_bytes = min(meta["contentLength"], 65557)
        tail_start = meta["contentLength"] - tail_bytes
        tail, _ = helper.fetch_range(archive_url, tail_start, meta["contentLength"] - 1, meta["etag"])
        entry_count, central_size, central_offset = helper.parse_eocd(tail, meta["contentLength"])
        if central_size > MAX_CENTRAL_DIRECTORY_BYTES:
            raise AcquisitionError(f"central directory exceeds bounded metadata request: {central_size}")
        central, _ = helper.fetch_range(archive_url, central_offset, central_offset + central_size - 1, meta["etag"])
        members = selected_central_members(central, entry_count)
        receipt["archiveMetadata"] = {**meta, "centralDirectoryEntries": entry_count, "centralDirectoryBytes": central_size,
                                      "centralDirectoryStartByte": central_offset, "archiveTailBytes": tail_bytes}
        frozen_by_id = {row["sourceElementFileId"]: row for row in assets}
        total_payload = 0
        for file_id in EXPECTED:
            active_id = file_id
            member = members[file_id]
            destination = CACHE_ROOT / frozen_by_id[file_id]["primaryOwner"] / f"{file_id}.obj"
            try:
                payload, selected_range_bytes = helper.selected_member_bytes(archive_url, meta, member)
                total_payload += len(payload)
                if total_payload > MAX_SELECTED_UNCOMPRESSED_BYTES:
                    raise AcquisitionError("selected OBJ payloads exceeded the 1 GB total uncompressed task bound")
                expected_map = frozen_by_id[file_id]
                header = parse_header(payload)
                if header.get("File ID") != file_id:
                    raise AcquisitionError(f"OBJ File ID mismatch for {file_id}: {header.get('File ID')}")
                if header.get("Representation ID") != expected_map["sourceRepresentationId"]:
                    raise AcquisitionError(f"OBJ BP/representation mismatch for {file_id}: {header.get('Representation ID')}")
                if header.get("Concept ID") != expected_map["sourceConceptId"]:
                    raise AcquisitionError(f"OBJ FMA/concept mismatch for {file_id}: {header.get('Concept ID')}")
                if header.get("English name", "").casefold() != expected_map["sourceNameEnglish"].casefold():
                    raise AcquisitionError(f"OBJ exact source name mismatch for {file_id}: {header.get('English name')}")
                if header.get("Build-up logic") != "FMA 3.0 is_a" or "Bounds(mm)" not in header:
                    raise AcquisitionError(f"OBJ lacks expected R4 IS-A or mm bounds header for {file_id}")
                parsed = {
                    "fileId": header.get("File ID"),
                    "representationId": header.get("Representation ID"),
                    "buildUpLogic": header.get("Build-up logic"),
                    "conceptId": header.get("Concept ID"),
                    "licenseHeader": next((line.lstrip("# ").strip() for line in payload.decode("utf-8", errors="strict").splitlines()
                                            if "license for this database" in line.lower()), None),
                }
                ingest.validate_obj_source_identity(parsed, tables)
                actual_element_rows = [
                    row for row in tables["isaCompoundElements"]
                    if row[0] == parsed["conceptId"]
                    and row[1].casefold() == header["English name"].casefold()
                    and row[2] == file_id
                ]
                if not actual_element_rows:
                    raise AcquisitionError(f"exact official FMA/name/FJ source row missing for {file_id}")
                if (parsed["conceptId"], parsed["representationId"]) not in {tuple(row[:2]) for row in tables["isaConcepts"]}:
                    raise AcquisitionError(f"exact official FMA/BP source row missing for {file_id}")
                digest = sha(payload)
                crc = f"{binascii.crc32(payload) & 0xffffffff:08x}"
                if destination.exists() and destination.read_bytes() != payload:
                    raise AcquisitionError(f"refusing to overwrite different existing source bytes: {destination}")
                if not destination.exists():
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    partial = destination.with_suffix(".obj.partial")
                    partial.write_bytes(payload)
                    partial.replace(destination)
                receipt["files"].append({
                    **expected_map,
                    "status": "acquired",
                    "memberPath": member["memberPath"],
                    "zipCompressionMethod": member["compressionMethod"],
                    "archiveMemberCrc32": f"{member['crc32']:08x}",
                    "sourceCrc32": crc,
                    "bytes": len(payload),
                    "compressedBytes": member["compressedBytes"],
                    "memberTransferBytes": selected_range_bytes,
                    "sha256": digest,
                    "cacheRelativePath": destination.relative_to(ROOT).as_posix(),
                    "header": header,
                })
            except Exception as exc:
                receipt["files"].append({"sourceElementFileId": file_id, "status": "failed", "failure": f"{type(exc).__name__}: {exc}"})
        active_id = None
    except Exception as exc:
        receipt["failures"].append({"phase": "archive_index_access", "error": f"{type(exc).__name__}: {exc}"})
        receipt["archiveMetadata"] = receipt.get("archiveMetadata", {})
        receipt["files"] = [{"sourceElementFileId": fid, "status": "not_acquired", "failure": "bounded official archive index/member access unavailable; no full archive fallback attempted"} for fid in EXPECTED]

    acquired_count = sum(row.get("status") == "acquired" for row in receipt["files"])
    receipt["acquiredCount"] = acquired_count
    receipt["failedCount"] = len(EXPECTED) - acquired_count
    receipt["selectedPayloadBytes"] = sum(row.get("bytes", 0) for row in receipt["files"])
    receipt["totalRangeResponseBytes"] = sum(row["bytes"] for row in requests)
    receipt["allRangeResponsesHttp206"] = bool(requests) and all(row["httpStatus"] == 206 for row in requests)
    receipt["rightsBoundary"] = {
        "localDisplay": "not adjudicated until source/transform/scene validation completes",
        "publicRedistribution": "held; item-level legacy OBJ header and current official terms are not reconciled here",
        "humanAnatomyReview": "not_performed",
    }
    receipt["result"] = "pass" if acquired_count == len(EXPECTED) and not receipt["failures"] and receipt["allRangeResponsesHttp206"] else "partial_or_failed"
    write_json(OUT, receipt)
    return receipt


def check() -> dict[str, Any]:
    if not OUT.is_file() or not FREEZE.is_file():
        return {"result": "partial_or_failed", "reason": "T102 frozen source set or acquisition receipt missing"}
    frozen_raw = FREEZE.read_bytes()
    frozen = json.loads(frozen_raw)
    doc = json.loads(OUT.read_text(encoding="utf-8"))
    if doc.get("result") != "pass" or doc.get("frozenSourceSetSha256") != sha(frozen_raw) or doc.get("attemptedIds") != EXPECTED:
        return {"result": "partial_or_failed", "reason": "acquisition receipt is not a passing exact T102 frozen set"}
    if doc.get("fullArchiveDownloaded") is not False or doc.get("selectedMemberRangeRequestsOnly") is not True or doc.get("allRangeResponsesHttp206") is not True:
        raise AcquisitionError("T102 acquisition violates selected-range-only policy")
    rows = {row["sourceElementFileId"]: row for row in doc.get("files", [])}
    if set(rows) != set(EXPECTED) or len(rows) != len(EXPECTED):
        raise AcquisitionError("T102 acquisition does not contain exactly the frozen ten IDs")
    for row in doc["files"]:
        if row.get("status") != "acquired":
            raise AcquisitionError(f"T102 source was not acquired: {row.get('sourceElementFileId')}")
        payload = (ROOT / row["cacheRelativePath"]).read_bytes()
        if len(payload) != row["bytes"] or sha(payload) != row["sha256"] or f"{binascii.crc32(payload) & 0xffffffff:08x}" != row["sourceCrc32"]:
            raise AcquisitionError(f"cached source bytes/hash/CRC mismatch: {row['sourceElementFileId']}")
        parsed = parse_header(payload)
        if parsed.get("File ID") != row["sourceElementFileId"] or parsed.get("Concept ID") != row["sourceConceptId"] or parsed.get("Representation ID") != row["sourceRepresentationId"]:
            raise AcquisitionError(f"rechecked OBJ source header mismatch: {row['sourceElementFileId']}")
    return {"result": "pass", "acquiredCount": len(rows), "expectedCount": len(EXPECTED), "fullArchiveDownloaded": False,
            "http206RangeResponses": len(doc["rangeRequests"]), "rangeBytes": doc["totalRangeResponseBytes"], "payloadBytes": doc["selectedPayloadBytes"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--acquire", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = acquire() if args.acquire else check()
    except Exception as exc:
        print(f"T102 selected R4 acquisition failed closed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("result") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
