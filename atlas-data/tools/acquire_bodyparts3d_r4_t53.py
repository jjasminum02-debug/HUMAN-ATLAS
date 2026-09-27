#!/usr/bin/env python3
"""Acquire only the pre-frozen T53 BodyParts3D R4 OBJ members by HTTP Range."""

from __future__ import annotations

import argparse
import concurrent.futures
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
FROZEN = ROOT / "work/evidence/T53/frozen-source-set.json"
OUT = ROOT / "work/evidence/T53/source-acquisition.json"
MESH_ROOT = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t53"
ARCHIVES = {
    "IS-A": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip",
    "PART-OF": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/partof_BP3D_4.0_obj_99.zip",
}
FJ_ID = re.compile(r"^FJ[0-9]+M?$")
FJ_OBJ = re.compile(r"^(FJ[0-9]+M?)\.obj$", re.IGNORECASE)


class AcquisitionError(RuntimeError):
    pass


def module_at(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise AcquisitionError(f"could not load the validated T52 HTTP Range helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RANGE = module_at("ha_t53_range_helper", ROOT / "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_central_directory(data: bytes, expected_entries: int) -> dict[str, dict[str, Any]]:
    """Read standard ZIP central-directory records; retain exact ELEMENT IDs including M suffix."""
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
            raise AcquisitionError("ZIP64 or split-disk archive member is outside the T53 selected-range profile")
        name_start = cursor + 46
        name_end = name_start + name_len
        record_end = name_end + extra_len + comment_len
        if record_end > len(data):
            raise AcquisitionError("truncated ZIP central directory")
        encoding = "utf-8" if flags & 0x800 else "cp437"
        member_path = data[name_start:name_end].decode(encoding)
        base = member_path.rsplit("/", 1)[-1]
        match = FJ_OBJ.fullmatch(base)
        if match:
            file_id = match.group(1).upper()
            if file_id in members:
                raise AcquisitionError(f"duplicate ELEMENT File ID in one archive: {file_id}")
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
        raise AcquisitionError("parsed FJ OBJ count exceeds official ZIP central-directory count")
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
        raise AcquisitionError(f"frozen IDs absent from the official {tree} archive index: {', '.join(absent)}")
    return ({**metadata, "url": url, "centralDirectoryEntries": count, "centralDirectoryBytes": cd_size,
             "archiveTailRangeBytes": tail_size, "centralDirectoryRangeBytes": cd_size,
             "completeArchiveDownloaded": False}, members)


def acquire_one(row: dict[str, Any], tree: str, meta: dict[str, Any], member: dict[str, Any]) -> dict[str, Any]:
    file_id = row["sourceElementFileId"]
    destination = MESH_ROOT / f"{file_id}.obj"
    try:
        if destination.exists():
            payload = destination.read_bytes()
            source = "existing_T53_cache"
        else:
            payload, range_bytes = RANGE.selected_member_bytes(ARCHIVES[tree], meta, member)
            if not payload:
                raise AcquisitionError("official archive member is empty")
            destination.parent.mkdir(parents=True, exist_ok=True)
            temp = destination.with_suffix(".obj.partial")
            temp.write_bytes(payload)
            temp.replace(destination)
            source = "official_HTTP_206_range"
        return {
            "sourceElementFileId": file_id,
            "status": "acquired",
            "sourceAcquisitionMethod": source,
            "cacheRelativePath": destination.relative_to(ROOT).as_posix(),
            "bytes": len(payload),
            "sha256": sha256_bytes(payload),
            "crc32": f"{member['crc32']:08x}",
            "archiveTree": tree,
            "archiveUrl": ARCHIVES[tree],
            "archiveEtag": meta["etag"],
            "memberPath": member["memberPath"],
            "zipCompressionMethod": member["compressionMethod"],
            "compressedBytes": member["compressedBytes"],
        }
    except Exception as exc:  # keep per-ID failures explicit; continue the remaining frozen set
        return {"sourceElementFileId": file_id, "status": "acquisition_failed", "archiveTree": tree,
                "archiveUrl": ARCHIVES[tree], "errorType": type(exc).__name__, "error": str(exc)}


def acquire(workers: int = 4) -> dict[str, Any]:
    if not FROZEN.is_file():
        raise AcquisitionError("run freeze_bodyparts3d_r4_t53.py --freeze before mesh acquisition")
    frozen_bytes = FROZEN.read_bytes()
    frozen = json.loads(frozen_bytes)
    if frozen.get("revision") != "BodyParts3D-R4-T53-FROZEN-ATOMIC-SOURCE-SET-v1" or frozen.get("status") != "frozen_before_mesh_acquisition":
        raise AcquisitionError("T53 source set was not frozen before acquisition")
    if any(not FJ_ID.fullmatch(row["sourceElementFileId"]) for row in frozen["uniqueSourceAssets"]):
        raise AcquisitionError("frozen source set contains an invalid source File ID")

    trees_by_id = {row["sourceElementFileId"]: row["expectedArchiveTrees"] for row in frozen["uniqueSourceAssets"]}
    # Match the T52 acquisition convention: prefer the IS-A representation when a source File ID is listed there.
    chosen_tree = {file_id: ("IS-A" if "IS-A" in trees else "PART-OF") for file_id, trees in trees_by_id.items()}
    if any(tree not in ARCHIVES for tree in chosen_tree.values()):
        raise AcquisitionError("a frozen source File ID has no supported official archive tree")
    required_by_tree = {tree: {file_id for file_id, chosen in chosen_tree.items() if chosen == tree} for tree in ARCHIVES}
    archive_metadata: dict[str, dict[str, Any]] = {}
    archive_member_index: dict[str, dict[str, dict[str, Any]]] = {}
    for tree, required in required_by_tree.items():
        if required:
            archive_metadata[tree], archive_member_index[tree] = archive_members(tree, required)

    jobs = []
    rows_by_id = {row["sourceElementFileId"]: row for row in frozen["uniqueSourceAssets"]}
    for file_id in sorted(chosen_tree):
        tree = chosen_tree[file_id]
        jobs.append((rows_by_id[file_id], tree, archive_metadata[tree], archive_member_index[tree][file_id]))
    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(workers, 6))) as pool:
        futures = [pool.submit(acquire_one, *job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda row: row["sourceElementFileId"])

    selected_payload_bytes = sum(row.get("bytes", 0) for row in results if row["status"] == "acquired")
    result = {
        "revision": "BodyParts3D-R4-T53-SELECTED-RANGE-ACQUISITION-v1",
        "task": "T53",
        "acquiredAt": datetime.now(timezone.utc).isoformat(),
        "frozenSourceSetSha256": sha256_bytes(frozen_bytes),
        "frozenMembershipSha256": frozen["frozenMembershipSha256"],
        "fullArchivesDownloaded": False,
        "sourceElementFileCountFrozen": len(frozen["uniqueSourceAssets"]),
        "sourceElementFileCountAcquired": sum(row["status"] == "acquired" for row in results),
        "sourceElementFileCountFailed": sum(row["status"] == "acquisition_failed" for row in results),
        "selectedPayloadBytes": selected_payload_bytes,
        "archiveRequests": archive_metadata,
        "chosenArchiveTreePolicy": "IS-A preferred when listed for the source ELEMENT File ID; PART-OF fallback only when IS-A is not listed; tree and header are validated per file.",
        "files": results,
        "rightsBoundary": {"requiredAttribution": "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International", "redistributionStatus": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers"},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        old = json.loads(OUT.read_text(encoding="utf-8"))
        if old.get("frozenSourceSetSha256") != result["frozenSourceSetSha256"]:
            raise AcquisitionError("existing acquisition belongs to a different frozen source set")
        old_by_id = {row["sourceElementFileId"]: row for row in old.get("files", [])}
        new_by_id = {row["sourceElementFileId"]: row for row in results}
        for file_id, row in old_by_id.items():
            if row.get("status") == "acquired" and new_by_id.get(file_id, {}).get("status") == "acquired" and row.get("sha256") != new_by_id[file_id].get("sha256"):
                raise AcquisitionError(f"refusing to replace previously recorded source bytes for {file_id}")
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args(argv)
    try:
        result = acquire(args.workers)
    except (OSError, ValueError, AcquisitionError) as exc:
        print(f"T53 acquisition could not complete: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"path": OUT.relative_to(ROOT).as_posix(), "frozen": result["sourceElementFileCountFrozen"], "acquired": result["sourceElementFileCountAcquired"], "failed": result["sourceElementFileCountFailed"], "selectedPayloadBytes": result["selectedPayloadBytes"], "fullArchivesDownloaded": result["fullArchivesDownloaded"], "archiveTrees": list(result["archiveRequests"])}, ensure_ascii=False, indent=2))
    return 0 if result["sourceElementFileCountFailed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
