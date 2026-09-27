#!/usr/bin/env python3
"""Freeze T55 lower-limb source FJ IDs before any T55 mesh acquisition."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
T51_MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json"
REGION_ROOT = ROOT / "atlas-data/manifests/bodyparts3d-r4-regions-t51"
T07_CROSSWALK = ROOT / "atlas-data/manifests/mesh-crosswalk-t07.json"
T07_ASSET_MANIFEST = ROOT / "atlas-data/manifests/derived-assets-t07.json"
OUT = ROOT / "work/evidence/T55/frozen-source-set.json"
REGIONS = ("thigh", "leg", "foot")
BATCH_LIMIT = 10
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
SOURCE_VERSION = "BodyParts3D Release 4.0"
FJ_ID = re.compile(r"^FJ[0-9]+M?$")


class FreezeError(RuntimeError):
    pass


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise FreezeError(f"cannot load T51 source metadata helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INGEST = load_module("ha_t55_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def freeze() -> dict[str, Any]:
    required = (T51_MANIFEST, T07_CROSSWALK, T07_ASSET_MANIFEST)
    if any(not path.is_file() for path in required):
        raise FreezeError("T51 source inventory or T07 legacy crosswalk input is missing")
    t51_raw = T51_MANIFEST.read_bytes()
    t51 = json.loads(t51_raw)
    source_rows = {row["sourceElementFileId"]: row for row in t51["sourceElementFiles"]}
    concepts = t51["sourceConcepts"]
    crosswalk = json.loads(T07_CROSSWALK.read_text(encoding="utf-8"))
    derived = json.loads(T07_ASSET_MANIFEST.read_text(encoding="utf-8"))
    legacy_rows = {}
    for key in ("meshCrosswalk", "meshNodes"):
        for row in derived.get(key, []):
            file_id = row.get("sourceFileId")
            if file_id:
                legacy_rows.setdefault(file_id, {})[key] = row
    crosswalk_by_id = {row["fileId"]: row for row in crosswalk.get("entries", []) if row.get("fileId")}

    input_hashes: dict[str, str] = {
        T51_MANIFEST.relative_to(ROOT).as_posix(): sha256_bytes(t51_raw),
        T07_CROSSWALK.relative_to(ROOT).as_posix(): sha256_file(T07_CROSSWALK),
        T07_ASSET_MANIFEST.relative_to(ROOT).as_posix(): sha256_file(T07_ASSET_MANIFEST),
    }
    region_records: dict[str, dict[str, Any]] = {}
    sets: dict[str, set[str]] = {}
    for region in REGIONS:
        path = REGION_ROOT / f"{region}.json"
        if not path.is_file():
            raise FreezeError(f"missing T51 region chunk: {region}")
        raw = path.read_bytes()
        chunk = json.loads(raw)
        if chunk.get("revision") != "BodyParts3D-R4-T51-source-region-chunk-v1":
            raise FreezeError(f"unexpected T51 chunk revision: {region}")
        ids = chunk.get("sourceElementFileIds", [])
        if not ids or ids != sorted(ids) or len(ids) != len(set(ids)):
            raise FreezeError(f"empty, unsorted, or duplicate source ID list: {region}")
        if any(file_id not in source_rows for file_id in ids):
            raise FreezeError(f"T51 chunk contains an FJ ID absent from its whole-source manifest: {region}")
        region_records[region] = chunk
        sets[region] = set(ids)
        input_hashes[path.relative_to(ROOT).as_posix()] = sha256_bytes(raw)

    memberships: dict[str, set[str]] = {}
    for region in REGIONS:
        for file_id in sorted(sets[region]):
            memberships.setdefault(file_id, set()).add(region)
    if memberships.keys() != set().union(*sets.values()):
        raise FreezeError("region membership union changed during freeze")

    assets = []
    for file_id in sorted(memberships):
        if not FJ_ID.fullmatch(file_id):
            raise FreezeError(f"invalid BodyParts3D element file ID: {file_id}")
        row = source_rows[file_id]
        contexts = []
        for concept in concepts:
            if file_id not in concept.get("elementFileIds", []):
                continue
            contexts.append({
                "sourceFmaConceptId": concept["sourceFmaConceptId"],
                "sourceNameEnglish": concept["sourceNameEnglish"],
                "sourceEntityScopeCandidate": concept.get("sourceEntityScopeCandidate"),
                "sourceTrees": concept["sourceTrees"],
                "representations": concept["representations"],
                "compositionStatus": concept.get("compositionStatus"),
            })
        if not contexts:
            raise FreezeError(f"no exact T51 source concept context for frozen ID {file_id}")
        expected_trees = row.get("expectedInOfficialArchiveTrees", [])
        if not expected_trees or any(tree not in {"IS-A", "PART-OF"} for tree in expected_trees):
            raise FreezeError(f"missing archive-tree context for {file_id}")
        assets.append({
            "sourceElementFileId": file_id,
            "stableSourceMeshNodeId": f"HA-MESH-BP3D4-{file_id}",
            "regionMemberships": sorted(memberships[file_id]),
            "expectedArchiveTrees": expected_trees,
            "sourceContextRowCount": row["sourceContextRowCount"],
            "sourceContexts": contexts,
            "canonicalLearnerIds": [crosswalk_by_id[file_id]["targetEntityId"]] if file_id in crosswalk_by_id and crosswalk_by_id[file_id].get("targetEntityId") else [],
            "legacyT07Crosswalk": crosswalk_by_id.get(file_id),
            "legacyT07AssetRecords": legacy_rows.get(file_id),
        })

    region_rows = []
    for region in REGIONS:
        chunk = region_records[region]
        region_rows.append({
            "regionId": region,
            "labelKo": chunk["labelKo"],
            "sourceElementFileIds": sorted(sets[region]),
            "sourceElementFileCount": len(sets[region]),
            "t51ChunkSha256": input_hashes[(REGION_ROOT / f"{region}.json").relative_to(ROOT).as_posix()],
            "sourceRoots": chunk["sourceRoots"],
            "sourceBoneConceptIds": chunk["sourceBoneConceptIds"],
            "sourceMuscleConceptIds": chunk["sourceMuscleConceptIds"],
        })

    membership_lines = [f"{region}|{file_id}" for region in REGIONS for file_id in region_rows[REGIONS.index(region)]["sourceElementFileIds"]]
    batches = []
    all_ids = sorted(memberships)
    for offset in range(0, len(all_ids), BATCH_LIMIT):
        current = all_ids[offset : offset + BATCH_LIMIT]
        batches.append({"batchId": f"T55-B{len(batches)+1:02d}", "sourceElementFileIds": current})

    result: dict[str, Any] = {
        "revision": "BodyParts3D-R4-T55-FROZEN-ATOMIC-SOURCE-SET-v1",
        "task": "T55",
        "frozenAt": datetime.now(timezone.utc).isoformat(),
        "status": "frozen_before_T55_acquisition",
        "source": {"sourceId": SOURCE_ID, "version": SOURCE_VERSION, "officialT51Manifest": T51_MANIFEST.relative_to(ROOT).as_posix(), "frame": FRAME, "sourceUnit": "per-file OBJ Bounds(mm) header to verify after acquisition", "pose": "bodyparts3d-r4-static-reference", "archiveProfile": "official 99%-reduced source only; one resolution, no alternate LOD"},
        "scope": {"regionIds": list(REGIONS), "wholeBodyCanonicalDenominator": None, "canonicalMembershipCreated": False, "newClipCreated": False, "noCrossSourceVisualRegistration": True},
        "inputSha256": input_hashes,
        "frozenMembershipSha256": sha256_bytes(("\n".join(membership_lines) + "\n").encode("utf-8")),
        "regionSets": region_rows,
        "uniqueSourceAssets": assets,
        "uniqueSourceElementFileCount": len(assets),
        "sourceMembershipCount": sum(row["sourceElementFileCount"] for row in region_rows),
        "duplicatedMembershipReferences": {row["sourceElementFileId"]: row["regionMemberships"] for row in assets if len(row["regionMemberships"]) > 1},
        "t07LegacyMappingPreservation": {"crosswalkPath": T07_CROSSWALK.relative_to(ROOT).as_posix(), "t07AssetManifestPath": T07_ASSET_MANIFEST.relative_to(ROOT).as_posix(), "existingMappedSourceIdsInScope": sorted(file_id for file_id in memberships if file_id in crosswalk_by_id), "noNewCanonicalBindings": True},
        "internalBatches": batches,
        "internalBatchSizeLimit": BATCH_LIMIT,
        "rightsBoundary": {"officialCurrentLicense": "CC BY 4.0 with attribution per current official README", "perFileLegacyHeaders": "record exact source OBJ header; public redistribution held pending reconciliation", "wholeArchivesDownloaded": False},
        "identityPolicy": "BodyParts3D FMA concept ID, BP representation ID, FJ source mesh ID, stable HA-MESH source node ID, and canonical HA learner ID remain distinct. Only existing T07 crosswalk rows are copied; no new learner IDs or anatomy claims are created.",
    }
    result["frozenSetSha256"] = sha256_bytes(canonical_bytes(result))
    if OUT.exists():
        old = json.loads(OUT.read_text(encoding="utf-8"))
        if old.get("inputSha256") != input_hashes or old.get("frozenMembershipSha256") != result["frozenMembershipSha256"]:
            raise FreezeError("existing T55 freeze differs from current inputs; refusing to overwrite")
        return old
    write_json(OUT, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    if not args.freeze:
        parser.error("choose --freeze")
    result = freeze()
    print(json.dumps({"path": OUT.relative_to(ROOT).as_posix(), "status": result["status"], "uniqueSourceElementFileCount": result["uniqueSourceElementFileCount"], "sourceMembershipCount": result["sourceMembershipCount"], "regionCounts": {row["regionId"]: row["sourceElementFileCount"] for row in result["regionSets"]}, "batchCount": len(result["internalBatches"]), "maxBatchSize": max(map(lambda row: len(row["sourceElementFileIds"]), result["internalBatches"])), "legacyT07SourceIdsPreserved": result["t07LegacyMappingPreservation"]["existingMappedSourceIdsInScope"], "frozenMembershipSha256": result["frozenMembershipSha256"], "frozenSetSha256": result["frozenSetSha256"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
