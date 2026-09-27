#!/usr/bin/env python3
"""Acquire exactly T92's frozen six BodyParts3D R4 OBJ members via HTTP ranges."""
from __future__ import annotations

import argparse
import binascii
import csv
import hashlib
import importlib.util
import json
import re
import struct
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "work/evidence/T92/frozen-source-set.json"
OUT = ROOT / "work/evidence/T92/source-acquisition.json"
CACHE = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t92"
ARCHIVE_URL = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip"
EXPECTED_FJS = ["FJ1520", "FJ1520M", "FJ1554", "FJ1554M", "FJ1521", "FJ1521M"]
EXPECTED_ETAG = '"8848a5a-4dd48ec9df000"'
EXPECTED_LENGTH = 142903898
EXPECTED_LAST_MODIFIED = "Wed, 22 May 2013 06:46:24 GMT"


class AcquisitionError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AcquisitionError(f"cannot load project helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: Any) -> None:
    data = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if path.exists() and path.read_bytes() != data:
        raise AcquisitionError(f"refusing to overwrite prior evidence with different bytes: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def parse_fj_central_directory(data: bytes, expected_entries: int) -> dict[str, dict[str, Any]]:
    """Parse only central-directory metadata; preserve exact names and FJ suffix M."""
    rows: dict[str, dict[str, Any]] = {}
    cursor = 0
    while cursor < len(data):
        if cursor + 46 > len(data) or data[cursor:cursor + 4] != b"PK\x01\x02":
            raise AcquisitionError(f"invalid ZIP central directory at byte {cursor}")
        fields = struct.unpack_from("<4s6H3L5H2L", data, cursor)
        (_, _made, _needed, flags, method, _time, _date, crc, compressed, uncompressed,
         name_len, extra_len, comment_len, disk_start, _internal, _external, local_offset) = fields
        if disk_start or compressed == 0xFFFFFFFF or uncompressed == 0xFFFFFFFF or local_offset == 0xFFFFFFFF:
            raise AcquisitionError("ZIP64/split-disk member is outside T92 selected-range profile")
        name_start = cursor + 46
        name_end = name_start + name_len
        record_end = name_end + extra_len + comment_len
        if record_end > len(data):
            raise AcquisitionError("truncated ZIP central-directory entry")
        encoding = "utf-8" if flags & 0x800 else "cp437"
        member_path = data[name_start:name_end].decode(encoding)
        cursor = record_end
        base = PurePosixPath(member_path).name
        match = re.fullmatch(r"(FJ[0-9]+M?)\.obj", base, flags=re.IGNORECASE)
        if not match:
            continue
        file_id = match.group(1).upper()
        if file_id in rows:
            raise AcquisitionError(f"duplicate FJ member in official archive: {file_id}")
        rows[file_id] = {
            "memberPath": member_path,
            "flags": flags,
            "compressionMethod": method,
            "crc32": crc,
            "compressedBytes": compressed,
            "uncompressedBytes": uncompressed,
            "localHeaderOffset": local_offset,
        }
    if cursor != len(data):
        raise AcquisitionError("unexpected trailing bytes after central directory")
    if len(rows) > expected_entries:
        raise AcquisitionError("parsed FJ OBJ row count exceeds central-directory entry count")
    return rows


def side_from_name(name: str) -> str | None:
    sides = {value.casefold() for value in re.findall(r"\b(left|right)\b", name, flags=re.I)}
    if len(sides) > 1:
        raise AcquisitionError(f"conflicting left/right source name: {name}")
    return next(iter(sides), None)


def read_obj_name_and_bounds(path: Path) -> tuple[str | None, list[float] | None]:
    header_name: str | None = None
    bounds: list[float] | None = None
    bounds_pattern = re.compile(r"^#\s*Bounds\(mm\):\s*\(([^)]+)\)-\(([^)]+)\)\s*$")
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.startswith("#"):
                break
            if line.startswith("# English name :"):
                header_name = line.split(":", 1)[1].strip()
            match = bounds_pattern.match(line.rstrip("\r\n"))
            if match:
                try:
                    bounds = [float(v.strip()) for v in match.group(1).split(",") + match.group(2).split(",")]
                except ValueError as exc:
                    raise AcquisitionError(f"invalid Bounds(mm) numeric header: {path.name}") from exc
    if bounds is not None and len(bounds) != 6:
        raise AcquisitionError(f"Bounds(mm) header must contain six values: {path.name}")
    return header_name, bounds


def validate_frozen() -> tuple[dict[str, Any], bytes]:
    if not FREEZE.is_file():
        raise AcquisitionError("T92 scope must be frozen before requesting any mesh bytes")
    raw = FREEZE.read_bytes()
    frozen = json.loads(raw)
    if frozen.get("revision") != "BodyParts3D-R4-T92-FROZEN-TRAPEZIUS-SOURCE-SET-v1" or frozen.get("status") != "frozen_before_mesh_acquisition":
        raise AcquisitionError("T92 freeze revision/status is invalid")
    if frozen.get("uniqueSourceElementFileIds") != EXPECTED_FJS:
        raise AcquisitionError("T92 frozen allowlist differs from the six authorized exact FJ IDs")
    if [len(batch.get("sourceElementFileIds", [])) for batch in frozen.get("internalBatches", [])] != [6]:
        raise AcquisitionError("T92 must use a single six-member internal batch")
    canonical = "".join(
        f"{row['sourceElementFileId']}|IS-A|back,shoulder-scapular\n"
        for row in frozen["uniqueSourceAssets"]
    )
    if sha(canonical.encode()) != frozen.get("sourceAssetMembershipSha256"):
        raise AcquisitionError("T92 frozen FJ/context membership hash mismatch")
    return frozen, raw


def next_evidence_path() -> Path:
    if not OUT.exists():
        return OUT
    index = 2
    while True:
        candidate = OUT.with_name(f"source-acquisition-attempt-{index:02d}.json")
        if not candidate.exists():
            return candidate
        index += 1


def successful_acquisition() -> tuple[Path, dict[str, Any]]:
    paths = [OUT, *sorted(OUT.parent.glob("source-acquisition-attempt-*.json"))]
    for path in reversed(paths):
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if data.get("result") == "pass":
                return path, data
    raise AcquisitionError("no T92 selected-range acquisition has passed")


def acquire() -> dict[str, Any]:
    frozen, frozen_raw = validate_frozen()
    helper = load_module("ha_t92_selected_range_helper", ROOT / "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py")
    ingest = load_module("ha_t92_r4_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
    if not FREEZE.is_file():
        raise AcquisitionError("T92 freeze disappeared before acquisition")

    range_rows: list[dict[str, Any]] = []
    active_fj: str | None = None
    original_fetch = helper.fetch_range

    def fetch_logged(url: str, start: int, end: int, etag: str):
        body, headers = original_fetch(url, start, end, etag)
        range_rows.append({
            "sourceElementFileId": active_fj,
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
    attempt_path = next_evidence_path()
    evidence: dict[str, Any] = {
        "revision": "BodyParts3D-R4-T92-SELECTED-RANGE-ACQUISITION-v1",
        "task": "T92",
        "result": "running",
        "evidencePath": attempt_path.relative_to(ROOT).as_posix(),
        "attemptedAtUtc": datetime.now(timezone.utc).isoformat(),
        "sourceVersion": "BodyParts3D Release 4.0; 99%-reduced IS-A OBJ archive",
        "archiveTree": "IS-A",
        "archiveUrl": ARCHIVE_URL,
        "frozenSourceSetSha256": sha(frozen_raw),
        "frozenAssetMembershipSha256": frozen["sourceAssetMembershipSha256"],
        "attemptedIds": EXPECTED_FJS,
        "fullArchiveDownloaded": False,
        "selectedMemberRangeRequestsOnly": True,
        "requestsRequiredHttp206": True,
        "files": [],
        "rangeRequests": [],
        "failures": [],
    }
    try:
        archive_meta = helper.head_archive(ARCHIVE_URL)
        if archive_meta.get("etag") != EXPECTED_ETAG or archive_meta.get("contentLength") != EXPECTED_LENGTH or archive_meta.get("lastModified") != EXPECTED_LAST_MODIFIED:
            raise AcquisitionError(f"official R4 archive identity changed from T71/T72 pin: {archive_meta}")
        tail_size = min(archive_meta["contentLength"], 65557)
        tail_start = archive_meta["contentLength"] - tail_size
        tail, _ = helper.fetch_range(ARCHIVE_URL, tail_start, archive_meta["contentLength"] - 1, archive_meta["etag"])
        entries, central_bytes, central_offset = helper.parse_eocd(tail, archive_meta["contentLength"])
        central, _ = helper.fetch_range(ARCHIVE_URL, central_offset, central_offset + central_bytes - 1, archive_meta["etag"])
        members = parse_fj_central_directory(central, entries)
        missing = sorted(set(EXPECTED_FJS) - set(members))
        if missing:
            raise AcquisitionError(f"exact frozen FJ IDs absent from official IS-A archive directory: {missing}")

        tables = ingest.load_tables(ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata")
        source_names = ingest.load_source_name_map(ROOT)
        concept_relations = {row[0]: row for row in tables["isaConcepts"]}
        element_rows = {row[2]: [] for row in tables["isaCompoundElements"]}
        for row in tables["isaCompoundElements"]:
            element_rows.setdefault(row[2], []).append(row)
        by_fj = {row["sourceElementFileId"]: row for row in frozen["uniqueSourceAssets"]}
        files = []
        for file_id in EXPECTED_FJS:
            active_fj = file_id
            member = members[file_id]
            expected_path = by_fj[file_id]["archiveMemberPathExpectation"]
            if member["memberPath"] != expected_path:
                raise AcquisitionError(f"official ZIP member path mismatch for {file_id}: {member['memberPath']!r} != {expected_path!r}")
            if member["compressionMethod"] not in (0, 8):
                raise AcquisitionError(f"unsupported ZIP compression method for {file_id}: {member['compressionMethod']}")
            payload, consumed = helper.selected_member_bytes(ARCHIVE_URL, archive_meta, member)
            if not payload:
                raise AcquisitionError(f"selected source OBJ is empty: {file_id}")
            temp_path = CACHE / f"{file_id}.obj.pending"
            destination = CACHE / f"{file_id}.obj"
            if destination.exists() and destination.read_bytes() != payload:
                raise AcquisitionError(f"refusing to overwrite an existing different source-cache object: {file_id}")
            if not destination.exists():
                CACHE.mkdir(parents=True, exist_ok=True)
                temp_path.write_bytes(payload)
                temp_path.replace(destination)

            header = ingest.read_obj_header(destination)
            ingest.validate_obj_source_identity(header, tables)
            if header.get("fileId") != file_id or header.get("buildUpLogic") != "FMA 3.0 is_a":
                raise AcquisitionError(f"OBJ header FJ/tree mismatch for {file_id}: {header}")
            header_pair = (header.get("conceptId"), header.get("representationId"))
            if header_pair not in {(row[0], row[1]) for row in tables["isaConcepts"]}:
                raise AcquisitionError(f"OBJ header FMA/BP pair is absent from official R4 IS-A concept table: {file_id}")
            exact_header_name = source_names.get(header.get("conceptId"))
            exact_header_rows = [row for row in element_rows.get(file_id, []) if row[0] == header.get("conceptId") and row[1] == exact_header_name]
            if not exact_header_name or not exact_header_rows:
                raise AcquisitionError(f"OBJ header FMA/name has no exact official R4 ELEMENT relation for {file_id}")
            if (header.get("conceptId"), exact_header_name, file_id) not in {tuple(row) for row in by_fj[file_id]["allOfficialIsAElementRowsForFj"]}:
                raise AcquisitionError(f"OBJ header identity is outside the frozen official FJ relation set: {file_id}")
            obj_english_name, bounds_mm = read_obj_name_and_bounds(destination)
            if not obj_english_name or obj_english_name.casefold() != exact_header_name.casefold():
                raise AcquisitionError(f"OBJ English-name header does not match exact official FMA concept row: {file_id}")
            if bounds_mm is None:
                raise AcquisitionError(f"OBJ header lacks explicit Bounds(mm) unit/extent: {file_id}")
            observed_side = side_from_name(exact_header_name)
            frozen_side = by_fj[file_id].get("exactSideFromSourceConceptNames")
            if observed_side is not None and observed_side != frozen_side:
                raise AcquisitionError(f"explicit OBJ header source-name side conflicts with exact T73/official side-specific relation for {file_id}")
            row = {
                "sourceElementFileId": file_id,
                "sourceAcquisitionMethod": "official_HTTP_206_selected_member_range",
                "archiveTree": "IS-A",
                "archiveUrl": ARCHIVE_URL,
                "archiveEtag": archive_meta["etag"],
                "archiveLastModified": archive_meta["lastModified"],
                "memberPath": member["memberPath"],
                "centralDirectoryLocalHeaderOffset": member["localHeaderOffset"],
                "zipCompressionMethod": member["compressionMethod"],
                "compressedBytes": member["compressedBytes"],
                "rangeBytesFetchedForMember": consumed,
                "crc32": f"{member['crc32']:08x}",
                "bytes": len(payload),
                "sha256": sha(payload),
                "cacheRelativePath": destination.relative_to(ROOT).as_posix(),
                "objHeader": header,
                "objEnglishNameHeaderExact": obj_english_name,
                "boundsHeaderMm": bounds_mm,
                "headerExactOfficialSourceConcept": {"FMA": header["conceptId"], "BP": header["representationId"], "nameEnglish": exact_header_name},
                "headerSideFromExactOfficialFmaName": observed_side,
                "sourceSideFromExactOfficialT73ConceptRelation": frozen_side,
                "sideEvidenceRule": "side is from exact left/right wording on an official FMA concept row mapped to this FJ; absent header side is retained as absent; no FJ suffix or coordinate inference",
                "frozenSourceConceptMemberships": by_fj[file_id]["sourceConceptMemberships"],
            }
            files.append(row)
        active_fj = None
        if [row["sourceElementFileId"] for row in files] != EXPECTED_FJS:
            raise AcquisitionError("acquired member list/order differs from the frozen six IDs")
        if set(range_row["httpStatus"] for range_row in range_rows) != {206}:
            raise AcquisitionError("not every ZIP byte-range request returned HTTP 206")
        evidence.update({
            "result": "pass",
            "officialArchive": {
                **archive_meta,
                "url": ARCHIVE_URL,
                "tree": "IS-A",
                "centralDirectoryEntryCount": entries,
                "centralDirectoryBytes": central_bytes,
                "centralDirectoryStartByte": central_offset,
                "archiveTailRangeBytes": tail_size,
                "selectedMemberCount": len(files),
                "selectedPayloadBytes": sum(row["bytes"] for row in files),
                "selectedMemberRangeBytes": sum(row["rangeBytesFetchedForMember"] for row in files),
                "allRequestsUsedHttp206": True,
                "completeArchiveDownloaded": False,
            },
            "internalBatchResults": frozen["internalBatches"],
            "sourceElementFileCountFrozen": 6,
            "sourceElementFileCountAcquired": 6,
            "sourceElementFileCountFailed": 0,
            "files": files,
            "rangeRequests": range_rows,
            "officialCurrentLicenseEvidence": {
                "url": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html",
                "version": "CC BY 4.0; official page last updated 2025-02-27",
                "perFileHeaderReconciliation": "held; preserve each OBJ header claim verbatim and do not redistribute pending file-level reconciliation",
            },
            "rightsBoundary": "source cache is local technical validation only; no public release, canonical learner binding, or human anatomy approval",
        })
        write_json(attempt_path, evidence)
        return evidence
    except Exception as exc:
        evidence["result"] = "failed"
        evidence["failure"] = {"type": type(exc).__name__, "message": str(exc)}
        evidence["rangeRequests"] = range_rows
        evidence["fullArchiveDownloaded"] = False
        write_json(attempt_path, evidence)
        raise


def check() -> dict[str, Any]:
    frozen, raw = validate_frozen()
    evidence_path, acquisition = successful_acquisition()
    if acquisition.get("frozenSourceSetSha256") != sha(raw):
        raise AcquisitionError("successful acquisition does not bind to the current T92 frozen source set")
    if acquisition.get("fullArchiveDownloaded") is not False or acquisition.get("selectedMemberRangeRequestsOnly") is not True:
        raise AcquisitionError("T92 full archive exclusion/range-only acquisition contract failed")
    if acquisition.get("officialArchive", {}).get("allRequestsUsedHttp206") is not True:
        raise AcquisitionError("T92 archive range requests did not all use HTTP 206")
    if [row.get("sourceElementFileId") for row in acquisition.get("files", [])] != EXPECTED_FJS:
        raise AcquisitionError("T92 acquisition does not contain exactly the six frozen FJ IDs")
    if len(acquisition.get("rangeRequests", [])) == 0 or any(row.get("httpStatus") != 206 or row.get("bytes") != row.get("end", -1) - row.get("start", 0) + 1 for row in acquisition["rangeRequests"]):
        raise AcquisitionError("T92 range evidence contains a missing/non-206/short range")
    for row in acquisition["files"]:
        source_path = ROOT / row["cacheRelativePath"]
        data = source_path.read_bytes()
        if len(data) != row["bytes"] or sha(data) != row["sha256"] or (binascii.crc32(data) & 0xFFFFFFFF) != int(row["crc32"], 16):
            raise AcquisitionError(f"T92 source cache bytes/CRC/SHA changed: {row['sourceElementFileId']}")
    return {"result": "pass", "task": "T92", "evidencePath": evidence_path.relative_to(ROOT).as_posix(), "sourceElementFileCount": 6, "conceptCount": len(frozen["sourceConcepts"]), "rangeRequestCount": len(acquisition["rangeRequests"]), "selectedPayloadBytes": acquisition["officialArchive"]["selectedPayloadBytes"], "completeArchiveDownloaded": False}


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--acquire", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = acquire() if args.acquire else check()
    except Exception as exc:
        print(f"T92 acquisition failed closed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
