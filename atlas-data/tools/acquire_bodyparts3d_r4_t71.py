#!/usr/bin/env python3
"""Acquire only the frozen T71 BodyParts3D R4 trunk skeleton members."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "work/evidence/T71/frozen-source-set.json"
OUT = ROOT / "work/evidence/T71/source-acquisition.json"
MESH_ROOT = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t71"
ARCHIVES = {
    "IS-A": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip",
    "PART-OF": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/partof_BP3D_4.0_obj_99.zip",
}


class AcquisitionError(RuntimeError):
    pass


def load_range_helper():
    path = ROOT / "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py"
    spec = importlib.util.spec_from_file_location("ha_t71_range_helper", path)
    if not spec or not spec.loader:
        raise AcquisitionError(f"cannot load selected-range extractor: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def acquire() -> dict[str, Any]:
    if not FROZEN.is_file():
        raise AcquisitionError("T71 frozen source set is missing")
    frozen_raw = FROZEN.read_bytes()
    frozen = json.loads(frozen_raw)
    ids = frozen.get("sourceElementFileIds")
    if (
        frozen.get("revision") != "BodyParts3D-R4-T71-FROZEN-ATOMIC-SOURCE-SET-v1"
        or frozen.get("status") != "frozen_before_mesh_acquisition"
        or frozen.get("batchId") != "T71-B01-TRUNK-SKELETON"
        or not isinstance(ids, list)
        or len(ids) != 9
        or len(set(ids)) != 9
        or set(ids) != {row["sourceElementFileId"] for row in frozen.get("uniqueSourceAssets", [])}
    ):
        raise AcquisitionError("T71 frozen source set does not match the authorized exact nine-ID batch")
    if any(row.get("selectedArchiveTree") not in ARCHIVES for row in frozen["uniqueSourceAssets"]):
        raise AcquisitionError("T71 source set contains an unsupported official archive tree")

    helper = load_range_helper()
    meta_by_tree: dict[str, dict[str, Any]] = {}
    members_by_tree: dict[str, dict[str, dict[str, Any]]] = {}
    for tree in sorted({row["selectedArchiveTree"] for row in frozen["uniqueSourceAssets"]}):
        url = ARCHIVES[tree]
        meta = helper.head_archive(url)
        tail_size = min(meta["contentLength"], 65557)
        tail, _ = helper.fetch_range(url, meta["contentLength"] - tail_size, meta["contentLength"] - 1, meta["etag"])
        count, central_size, central_offset = helper.parse_eocd(tail, meta["contentLength"])
        directory, _ = helper.fetch_range(url, central_offset, central_offset + central_size - 1, meta["etag"])
        members = helper.parse_central_directory(directory, count)
        required = {row["sourceElementFileId"] for row in frozen["uniqueSourceAssets"] if row["selectedArchiveTree"] == tree}
        absent = sorted(required - set(members))
        if absent:
            raise AcquisitionError(f"selected IDs absent from official {tree} archive: {absent}")
        meta_by_tree[tree] = {
            **meta,
            "url": url,
            "centralDirectoryEntries": count,
            "centralDirectoryBytes": central_size,
            "archiveTailRangeBytes": tail_size,
            "centralDirectoryRangeBytes": central_size,
            "completeArchiveDownloaded": False,
        }
        members_by_tree[tree] = members

    files = []
    for row in frozen["uniqueSourceAssets"]:
        file_id = row["sourceElementFileId"]
        tree = row["selectedArchiveTree"]
        meta = meta_by_tree[tree]
        member = members_by_tree[tree][file_id]
        payload, fetched_range_bytes = helper.selected_member_bytes(ARCHIVES[tree], meta, member)
        if not payload:
            raise AcquisitionError(f"official source member is empty: {file_id}")
        destination = MESH_ROOT / f"{file_id}.obj"
        if destination.exists():
            existing = destination.read_bytes()
            if existing != payload:
                raise AcquisitionError(f"refusing to overwrite a different existing T71 cache object: {file_id}")
            method = "existing_T71_cache_verified_against_official_range"
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            temp = destination.with_suffix(".obj.partial")
            temp.write_bytes(payload)
            temp.replace(destination)
            method = "official_HTTP_206_selected_member_range"
        files.append({
            "sourceElementFileId": file_id,
            "status": "acquired",
            "sourceAcquisitionMethod": method,
            "cacheRelativePath": destination.relative_to(ROOT).as_posix(),
            "bytes": len(payload),
            "sha256": sha256_bytes(payload),
            "crc32": f"{member['crc32']:08x}",
            "archiveTree": tree,
            "archiveUrl": ARCHIVES[tree],
            "archiveEtag": meta["etag"],
            "archiveLastModified": meta.get("lastModified"),
            "memberPath": member["memberPath"],
            "zipCompressionMethod": member["compressionMethod"],
            "compressedBytes": member["compressedBytes"],
            "fetchedRangeBytes": fetched_range_bytes,
        })
    files.sort(key=lambda r: r["sourceElementFileId"])
    result = {
        "revision": "BodyParts3D-R4-T71-SELECTED-RANGE-ACQUISITION-v1",
        "task": "T71",
        "acquiredAt": datetime.now(timezone.utc).isoformat(),
        "frozenSourceSetSha256": sha256_bytes(frozen_raw),
        "frozenMembershipSha256": frozen["frozenMembershipSha256"],
        "fullArchivesDownloaded": False,
        "sourceElementFileCountFrozen": len(ids),
        "sourceElementFileCountAcquired": len(files),
        "sourceElementFileCountFailed": 0,
        "selectedPayloadBytes": sum(row["bytes"] for row in files),
        "archiveRequests": meta_by_tree,
        "selectedMemberRangeRequestsOnly": True,
        "files": files,
    }
    write_json(OUT, result)
    return result


def check() -> dict[str, Any]:
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    acquisition = json.loads(OUT.read_text(encoding="utf-8"))
    if acquisition.get("fullArchivesDownloaded") is not False or acquisition.get("selectedMemberRangeRequestsOnly") is not True:
        raise AcquisitionError("acquisition manifest does not prove selected-range-only retrieval")
    if acquisition.get("frozenSourceSetSha256") != sha256_bytes(FROZEN.read_bytes()):
        raise AcquisitionError("acquisition manifest is not bound to current frozen source set")
    if acquisition.get("frozenMembershipSha256") != frozen.get("frozenMembershipSha256"):
        raise AcquisitionError("acquisition manifest membership hash differs from frozen set")
    expected = set(frozen["sourceElementFileIds"])
    rows = acquisition.get("files", [])
    if {r.get("sourceElementFileId") for r in rows} != expected or len(rows) != len(expected):
        raise AcquisitionError("acquisition rows do not exactly cover the nine frozen IDs")
    for row in rows:
        path = ROOT / row["cacheRelativePath"]
        if row.get("status") != "acquired" or not path.is_file():
            raise AcquisitionError(f"source member missing or not acquired: {row.get('sourceElementFileId')}")
        if path.stat().st_size != row["bytes"] or sha256_file(path) != row["sha256"]:
            raise AcquisitionError(f"source cache hash or size changed: {row['sourceElementFileId']}")
    return {"result": "pass", "sourceElementFileCount": len(rows), "sourcePayloadBytes": acquisition["selectedPayloadBytes"]}


def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--acquire", action="store_true", help="fetch only the exact frozen source members")
    group.add_argument("--check", action="store_true", help="verify acquisition manifest and local bytes")
    args = parser.parse_args(argv)
    try:
        result = acquire() if args.acquire else check()
    except Exception as exc:
        print(f"T71 acquisition error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
