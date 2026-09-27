#!/usr/bin/env python3
"""Acquire only frozen T54 BodyParts3D Release 4.0 OBJ members via HTTP Range."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import re
import shutil
import struct
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "work/evidence/T54/frozen-source-set.json"
OUT = ROOT / "work/evidence/T54/source-acquisition.json"
T53_ACQUISITION = ROOT / "work/evidence/T53/source-acquisition.json"
MESH_ROOT = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t54"
ARCHIVES = {
    "IS-A": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip",
    "PART-OF": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/partof_BP3D_4.0_obj_99.zip",
}
FJ_ID = re.compile(r"^FJ[0-9]+M?$")
FJ_OBJ = re.compile(r"^(FJ[0-9]+M?)\.obj$", re.IGNORECASE)


class AcquisitionError(RuntimeError):
    pass


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise AcquisitionError(f"could not load selected ZIP member helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RANGE = load_module("ha_t54_range_helper", ROOT / "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_central_directory(data: bytes, expected_entries: int) -> dict[str, dict[str, Any]]:
    members: dict[str, dict[str, Any]] = {}
    cursor = 0
    signature = b"PK\x01\x02"
    while cursor < len(data):
        if cursor + 46 > len(data) or data[cursor : cursor + 4] != signature:
            raise AcquisitionError(f"invalid ZIP central directory at byte {cursor}")
        values = struct.unpack_from("<4s6H3L5H2L", data, cursor)
        (_, _made, _needed, flags, method, _mtime, _mdate, crc, compressed, uncompressed,
         name_len, extra_len, comment_len, disk_start, _internal, _external, local_offset) = values
        if disk_start or compressed == 0xFFFFFFFF or uncompressed == 0xFFFFFFFF or local_offset == 0xFFFFFFFF:
            raise AcquisitionError("ZIP64 or split-disk member is outside this selected-range profile")
        name_start = cursor + 46
        name_end = name_start + name_len
        record_end = name_end + extra_len + comment_len
        if record_end > len(data):
            raise AcquisitionError("truncated ZIP central directory")
        encoding = "utf-8" if flags & 0x800 else "cp437"
        member_path = data[name_start:name_end].decode(encoding)
        match = FJ_OBJ.fullmatch(member_path.rsplit("/", 1)[-1])
        if match:
            file_id = match.group(1).upper()
            if file_id in members:
                raise AcquisitionError(f"duplicate FJ source ID in archive: {file_id}")
            members[file_id] = {
                "memberPath": member_path, "flags": flags, "compressionMethod": method,
                "crc32": crc, "compressedBytes": compressed, "uncompressedBytes": uncompressed,
                "localHeaderOffset": local_offset,
            }
        cursor = record_end
    if cursor != len(data):
        raise AcquisitionError("unexpected trailing central-directory data")
    if len(members) > expected_entries:
        raise AcquisitionError("parsed FJ count exceeds official ZIP entry count")
    return members


def archive_members(tree: str, required: set[str]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    url = ARCHIVES[tree]
    try:
        metadata = RANGE.head_archive(url)
    except Exception as exc:
        raise AcquisitionError(f"official archive metadata access failed for {tree}: {type(exc).__name__}: {exc}") from exc
    tail_size = min(metadata["contentLength"], 65557)
    tail, _ = RANGE.fetch_range(url, metadata["contentLength"] - tail_size, metadata["contentLength"] - 1, metadata["etag"])
    count, cd_size, cd_offset = RANGE.parse_eocd(tail, metadata["contentLength"])
    directory, _ = RANGE.fetch_range(url, cd_offset, cd_offset + cd_size - 1, metadata["etag"])
    members = parse_central_directory(directory, count)
    absent = sorted(required - members.keys())
    if absent:
        raise AcquisitionError(f"frozen IDs are absent from official {tree} archive: {', '.join(absent)}")
    return ({**metadata, "url": url, "centralDirectoryEntries": count, "centralDirectoryBytes": cd_size,
             "archiveTailRangeBytes": tail_size, "centralDirectoryRangeBytes": cd_size,
             "completeArchiveDownloaded": False}, members)


def verify_member_bytes(payload: bytes, member: dict[str, Any], file_id: str) -> None:
    if len(payload) != member["uncompressedBytes"]:
        raise AcquisitionError(f"archive member size differs for {file_id}")
    if zlib.crc32(payload) & 0xFFFFFFFF != member["crc32"]:
        raise AcquisitionError(f"archive member CRC differs for {file_id}")


def acquire_one(row: dict[str, Any], tree: str, meta: dict[str, Any], member: dict[str, Any], t53_rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    file_id = row["sourceElementFileId"]
    destination = MESH_ROOT / f"{file_id}.obj"
    prior = t53_rows.get(file_id)
    try:
        if destination.exists():
            payload = destination.read_bytes()
            verify_member_bytes(payload, member, file_id)
            method = "existing_T54_cache_verified_against_official_member_crc"
        else:
            t53_rel = row.get("priorT53SourceCachePath")
            t53_path = ROOT / t53_rel if t53_rel else None
            if prior and t53_path and t53_path.is_file():
                prior_payload = t53_path.read_bytes()
                if len(prior_payload) != prior.get("bytes") or sha256_bytes(prior_payload) != prior.get("sha256"):
                    raise AcquisitionError(f"T53 connector cache hash differs from its acquisition record: {file_id}")
                verify_member_bytes(prior_payload, member, file_id)
                payload = prior_payload
                method = "verified_T53_cache_copy"
            else:
                payload, _range_bytes = RANGE.selected_member_bytes(ARCHIVES[tree], meta, member)
                verify_member_bytes(payload, member, file_id)
                method = "official_HTTP_206_selected_member_range"
            if not payload:
                raise AcquisitionError("official archive member is empty")
            destination.parent.mkdir(parents=True, exist_ok=True)
            temp = destination.with_suffix(".obj.partial")
            temp.write_bytes(payload)
            temp.replace(destination)
        result = {
            "sourceElementFileId": file_id, "status": "acquired", "sourceAcquisitionMethod": method,
            "cacheRelativePath": destination.relative_to(ROOT).as_posix(), "bytes": len(payload),
            "sha256": sha256_bytes(payload), "crc32": f"{member['crc32']:08x}", "archiveTree": tree,
            "archiveUrl": ARCHIVES[tree], "archiveEtag": meta["etag"], "archiveLastModified": meta.get("lastModified"),
            "memberPath": member["memberPath"], "zipCompressionMethod": member["compressionMethod"],
            "compressedBytes": member["compressedBytes"], "uncompressedBytes": member["uncompressedBytes"],
            "priorT53SourceAcquisition": ({"cacheRelativePath": prior["cacheRelativePath"], "sha256": prior["sha256"], "bytes": prior["bytes"]} if method == "verified_T53_cache_copy" and prior else None),
        }
        if result["sha256"] != sha256_file(destination):
            raise AcquisitionError(f"destination SHA-256 differs after atomic write: {file_id}")
        return result
    except Exception as exc:
        return {"sourceElementFileId": file_id, "status": "acquisition_failed", "archiveTree": tree,
                "archiveUrl": ARCHIVES[tree], "errorType": type(exc).__name__, "error": str(exc)}


def acquire(workers: int = 4) -> dict[str, Any]:
    if not FROZEN.is_file():
        raise AcquisitionError("freeze the T54 source set before requesting mesh bytes")
    frozen_raw = FROZEN.read_bytes()
    frozen = json.loads(frozen_raw)
    if frozen.get("revision") != "BodyParts3D-R4-T54-FROZEN-ATOMIC-SOURCE-SET-v1" or frozen.get("status") != "frozen_before_T54_acquisition":
        raise AcquisitionError("T54 source set is not in its pre-acquisition frozen state")
    if any(not FJ_ID.fullmatch(row["sourceElementFileId"]) for row in frozen["uniqueSourceAssets"]):
        raise AcquisitionError("frozen source set contains an invalid FJ ID")
    t53 = json.loads(T53_ACQUISITION.read_text(encoding="utf-8"))
    t53_rows = {row["sourceElementFileId"]: row for row in t53["files"] if row.get("status") == "acquired"}

    trees_by_id = {row["sourceElementFileId"]: row["expectedArchiveTrees"] for row in frozen["uniqueSourceAssets"]}
    chosen_tree = {}
    for row in frozen["uniqueSourceAssets"]:
        file_id = row["sourceElementFileId"]
        prior = t53_rows.get(file_id)
        prior_tree = prior.get("archiveTree") if prior else None
        chosen_tree[file_id] = prior_tree if prior_tree in trees_by_id[file_id] else ("IS-A" if "IS-A" in trees_by_id[file_id] else "PART-OF")
    required_by_tree = {tree: {file_id for file_id, selected in chosen_tree.items() if selected == tree} for tree in ARCHIVES}
    archive_metadata: dict[str, dict[str, Any]] = {}
    archive_member_index: dict[str, dict[str, dict[str, Any]]] = {}
    for tree, required in required_by_tree.items():
        if required:
            archive_metadata[tree], archive_member_index[tree] = archive_members(tree, required)

    assets_by_id = {row["sourceElementFileId"]: row for row in frozen["uniqueSourceAssets"]}
    jobs = [(assets_by_id[file_id], tree, archive_metadata[tree], archive_member_index[tree][file_id], t53_rows)
            for file_id, tree in sorted(chosen_tree.items())]
    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(workers, 6))) as pool:
        futures = [pool.submit(acquire_one, *job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda row: row["sourceElementFileId"])
    successful = [row for row in results if row["status"] == "acquired"]
    result = {
        "revision": "BodyParts3D-R4-T54-SELECTED-RANGE-ACQUISITION-v1", "task": "T54",
        "acquiredAt": datetime.now(timezone.utc).isoformat(), "frozenSourceSetSha256": sha256_bytes(frozen_raw),
        "frozenMembershipSha256": frozen["frozenMembershipSha256"], "fullArchivesDownloaded": False,
        "sourceElementFileCountFrozen": len(frozen["uniqueSourceAssets"]),
        "sourceElementFileCountAcquired": len(successful), "sourceElementFileCountFailed": len(results) - len(successful),
        "selectedPayloadBytes": sum(row.get("bytes", 0) for row in successful),
        "acquisitionMethods": {method: sum(row.get("sourceAcquisitionMethod") == method for row in successful) for method in sorted({row.get("sourceAcquisitionMethod") for row in successful})},
        "archiveRequests": archive_metadata,
        "chosenArchiveTreePolicy": "Use verified T53 archive tree for copied connector files; otherwise prefer IS-A when present and use PART-OF only when IS-A is not listed. Validate each archive member, OBJ header, FJ ID, and source tree separately.",
        "files": results,
        "rightsBoundary": {"requiredAttribution": "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International", "redistributionStatus": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers"},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        old = json.loads(OUT.read_text(encoding="utf-8"))
        if old.get("frozenSourceSetSha256") != result["frozenSourceSetSha256"]:
            raise AcquisitionError("existing T54 acquisition belongs to a different frozen source set")
        old_by = {row["sourceElementFileId"]: row for row in old.get("files", [])}
        new_by = {row["sourceElementFileId"]: row for row in results}
        for file_id, row in old_by.items():
            if row.get("status") == "acquired" and new_by.get(file_id, {}).get("status") == "acquired" and row.get("sha256") != new_by[file_id].get("sha256"):
                raise AcquisitionError(f"refusing to change a previously acquired T54 source hash: {file_id}")
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    try:
        result = acquire(args.workers)
    except (OSError, ValueError, AcquisitionError) as exc:
        print(f"T54 selected acquisition failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"path": OUT.relative_to(ROOT).as_posix(), "frozen": result["sourceElementFileCountFrozen"], "acquired": result["sourceElementFileCountAcquired"], "failed": result["sourceElementFileCountFailed"], "selectedPayloadBytes": result["selectedPayloadBytes"], "methods": result["acquisitionMethods"], "fullArchivesDownloaded": result["fullArchivesDownloaded"], "trees": list(result["archiveRequests"])}, ensure_ascii=False, indent=2))
    return 0 if result["sourceElementFileCountFailed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
