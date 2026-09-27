#!/usr/bin/env python3
"""Acquire only frozen T55 BodyParts3D OBJ members with verified HTTP Range."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "work/evidence/T55/frozen-source-set.json"
OUT = ROOT / "work/evidence/T55/source-acquisition.json"
MESH_ROOT = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t55"


class AcquisitionError(RuntimeError):
    pass


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise AcquisitionError(f"cannot load selected-range acquisition helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INGEST = load_module("ha_t55_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
RANGE = load_module("ha_t55_range", ROOT / "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py")
T54_ACQ = load_module("ha_t55_t54_range_reuse", ROOT / "atlas-data/tools/acquire_bodyparts3d_r4_t54.py")
ARCHIVES = T54_ACQ.ARCHIVES


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def candidate_prior_path(file_id: str) -> Path | None:
    for candidate in (
        ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/IS-A" / f"{file_id}.obj",
        ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/PART-OF" / f"{file_id}.obj",
        ROOT / "atlas-data/assets/bodyparts3d-v4-pilot" / f"{file_id}.obj",
    ):
        if candidate.is_file():
            return candidate
    return None


def tree_from_header(path: Path) -> str | None:
    header = INGEST.read_obj_header(path)
    if header.get("fileId") != path.stem:
        return None
    return {"FMA 3.0 is_a": "IS-A", "FMA 3.0 part_of": "PART-OF"}.get(header.get("buildUpLogic"))


def acquire_one(row: dict[str, Any], tree: str, archive_meta: dict[str, Any], member: dict[str, Any], prior_path: Path | None) -> dict[str, Any]:
    file_id = row["sourceElementFileId"]
    destination = MESH_ROOT / f"{file_id}.obj"
    try:
        if destination.exists():
            payload = destination.read_bytes()
            T54_ACQ.verify_member_bytes(payload, member, file_id)
            method = "existing_T55_cache_reverified_against_official_member_crc"
        elif prior_path:
            payload = prior_path.read_bytes()
            if tree_from_header(prior_path) != tree:
                raise AcquisitionError(f"prior source header tree differs from chosen official archive: {file_id}")
            T54_ACQ.verify_member_bytes(payload, member, file_id)
            method = "existing_T51_or_T07_source_copy_verified_against_official_member_crc"
        else:
            payload, range_bytes = RANGE.selected_member_bytes(archive_meta["url"], archive_meta, member)
            T54_ACQ.verify_member_bytes(payload, member, file_id)
            method = "official_HTTP_206_selected_member_range"
        if not payload:
            raise AcquisitionError("official archive member is empty")
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_suffix(".obj.partial")
            temporary.write_bytes(payload)
            if sha256_file(temporary) != sha256_bytes(payload):
                temporary.unlink(missing_ok=True)
                raise AcquisitionError(f"atomic temporary write hash mismatch: {file_id}")
            temporary.replace(destination)
        header = INGEST.read_obj_header(destination)
        if header.get("fileId") != file_id or {"FMA 3.0 is_a": "IS-A", "FMA 3.0 part_of": "PART-OF"}.get(header.get("buildUpLogic")) != tree:
            raise AcquisitionError(f"acquired OBJ identity/tree header mismatch: {file_id}")
        return {
            "sourceElementFileId": file_id,
            "status": "acquired",
            "sourceAcquisitionMethod": method,
            "priorSourcePath": prior_path.relative_to(ROOT).as_posix() if prior_path else None,
            "cacheRelativePath": destination.relative_to(ROOT).as_posix(),
            "bytes": len(payload),
            "sha256": sha256_bytes(payload),
            "crc32": f"{member['crc32']:08x}",
            "archiveTree": tree,
            "archiveUrl": archive_meta["url"],
            "archiveEtag": archive_meta["etag"],
            "archiveLastModified": archive_meta.get("lastModified"),
            "memberPath": member["memberPath"],
            "zipCompressionMethod": member["compressionMethod"],
            "compressedBytes": member["compressedBytes"],
            "uncompressedBytes": member["uncompressedBytes"],
            "sourceHeaderIdentity": header,
        }
    except Exception as exc:
        return {"sourceElementFileId": file_id, "status": "acquisition_failed", "archiveTree": tree, "archiveUrl": archive_meta["url"], "errorType": type(exc).__name__, "error": str(exc)}


def acquire(workers: int = 4) -> dict[str, Any]:
    if not FROZEN.is_file():
        raise AcquisitionError("freeze the T55 source set before acquisition")
    frozen_raw = FROZEN.read_bytes()
    frozen = json.loads(frozen_raw)
    if frozen.get("revision") != "BodyParts3D-R4-T55-FROZEN-ATOMIC-SOURCE-SET-v1" or frozen.get("status") != "frozen_before_T55_acquisition":
        raise AcquisitionError("T55 source set is not frozen before acquisition")
    assets = frozen["uniqueSourceAssets"]
    selected: dict[str, tuple[str, Path | None]] = {}
    for row in assets:
        file_id = row["sourceElementFileId"]
        prior = candidate_prior_path(file_id)
        tree = tree_from_header(prior) if prior else None
        if tree and tree not in row["expectedArchiveTrees"]:
            raise AcquisitionError(f"cached OBJ tree is not supported by exact T51 source metadata: {file_id}")
        if not tree:
            tree = "IS-A" if "IS-A" in row["expectedArchiveTrees"] else row["expectedArchiveTrees"][0]
        if tree not in ARCHIVES:
            raise AcquisitionError(f"no official archive URL for selected source tree: {tree}")
        selected[file_id] = (tree, prior)

    required_by_tree = {tree: {file_id for file_id, (chosen, _prior) in selected.items() if chosen == tree} for tree in ARCHIVES}
    archive_metadata: dict[str, dict[str, Any]] = {}
    archive_members: dict[str, dict[str, dict[str, Any]]] = {}
    for tree, required in required_by_tree.items():
        if not required:
            continue
        archive_metadata[tree], archive_members[tree] = T54_ACQ.archive_members(tree, required)

    asset_by_id = {row["sourceElementFileId"]: row for row in assets}
    jobs = []
    for file_id, (tree, prior) in sorted(selected.items()):
        if file_id not in archive_members[tree]:
            raise AcquisitionError(f"frozen FJ ID is missing from official {tree} release archive index: {file_id}")
        jobs.append((asset_by_id[file_id], tree, archive_metadata[tree], archive_members[tree][file_id], prior))
    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(workers, 6))) as pool:
        futures = [pool.submit(acquire_one, *job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda row: row["sourceElementFileId"])
    successful = [row for row in results if row["status"] == "acquired"]
    result = {
        "revision": "BodyParts3D-R4-T55-SELECTED-RANGE-ACQUISITION-v1",
        "task": "T55",
        "acquiredAt": datetime.now(timezone.utc).isoformat(),
        "frozenSourceSetSha256": sha256_bytes(frozen_raw),
        "frozenMembershipSha256": frozen["frozenMembershipSha256"],
        "fullArchivesDownloaded": False,
        "sourceElementFileCountFrozen": len(assets),
        "sourceElementFileCountAcquired": len(successful),
        "sourceElementFileCountFailed": len(results) - len(successful),
        "selectedPayloadBytes": sum(row.get("bytes", 0) for row in successful),
        "acquisitionMethods": {method: sum(row.get("sourceAcquisitionMethod") == method for row in successful) for method in sorted({row.get("sourceAcquisitionMethod") for row in successful})},
        "archiveRequests": archive_metadata,
        "chosenArchiveTreePolicy": "For a cached OBJ, use its exact header tree if allowed by T51 metadata; otherwise prefer official IS-A when allowed, then exact listed alternative. Verify every member with archive CRC and each header identity/tree.",
        "files": results,
        "rightsBoundary": {"requiredAttribution": "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International", "redistributionStatus": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers"},
    }
    if OUT.exists():
        old = json.loads(OUT.read_text(encoding="utf-8"))
        if old.get("frozenSourceSetSha256") != result["frozenSourceSetSha256"]:
            raise AcquisitionError("existing T55 acquisition binds a different frozen set")
        old_by = {row["sourceElementFileId"]: row for row in old.get("files", [])}
        new_by = {row["sourceElementFileId"]: row for row in results}
        for file_id, row in old_by.items():
            new_row = new_by.get(file_id, {})
            if row.get("status") == "acquired" and new_row.get("status") == "acquired" and row.get("sha256") != new_row.get("sha256"):
                raise AcquisitionError(f"refusing to change an already acquired T55 source hash: {file_id}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acquire", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if not args.acquire:
        parser.error("choose --acquire")
    try:
        result = acquire(args.workers)
    except Exception as exc:
        print(f"T55 acquisition failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"path": OUT.relative_to(ROOT).as_posix(), "frozen": result["sourceElementFileCountFrozen"], "acquired": result["sourceElementFileCountAcquired"], "failed": result["sourceElementFileCountFailed"], "selectedPayloadBytes": result["selectedPayloadBytes"], "methods": result["acquisitionMethods"], "fullArchivesDownloaded": result["fullArchivesDownloaded"], "trees": list(result["archiveRequests"])}, ensure_ascii=False, indent=2))
    return 0 if result["sourceElementFileCountFailed"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
