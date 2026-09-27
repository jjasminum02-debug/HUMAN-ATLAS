#!/usr/bin/env python3
"""Freeze T54 shoulder/upper-limb source FJ IDs before T54 acquisition."""

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
T53_FREEZE = ROOT / "work/evidence/T53/frozen-source-set.json"
T53_MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json"
T53_ACQUISITION = ROOT / "work/evidence/T53/source-acquisition.json"
T53_GLb = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t53/T53-trunk-pelvis-static-source.glb"
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
OUT = ROOT / "work/evidence/T54/frozen-source-set.json"
REGIONS = ("shoulder-scapular", "upper-limb")
BATCH_LIMIT = 10
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
SOURCE_VERSION = "BodyParts3D Release 4.0"
FJ_ID = re.compile(r"^FJ[0-9]+M?$")
SHOULDER_CONNECTORS = {
    "FJ3237": {"sourceFmaConceptId": "FMA13323", "expectedEnglishName": "left clavicle"},
    "FJ3279": {"sourceFmaConceptId": "FMA13396", "expectedEnglishName": "left scapula"},
}


class FreezeError(RuntimeError):
    pass


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("ha_t54_t51_ingest", path)
    if not spec or not spec.loader:
        raise FreezeError(f"cannot load T51 inventory helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INGEST = load_module(ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")


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
    for path in (T51_MANIFEST, T53_FREEZE, T53_MANIFEST, T53_ACQUISITION, T53_GLb):
        if not path.is_file():
            raise FreezeError(f"required T51/T53 prerequisite input is missing: {path.relative_to(ROOT)}")
    t51_raw = T51_MANIFEST.read_bytes()
    t51 = json.loads(t51_raw)
    t53_freeze_raw = T53_FREEZE.read_bytes()
    t53_freeze = json.loads(t53_freeze_raw)
    t53_manifest_raw = T53_MANIFEST.read_bytes()
    t53_manifest = json.loads(t53_manifest_raw)
    t53_acq_raw = T53_ACQUISITION.read_bytes()
    t53_acq = json.loads(t53_acq_raw)
    if t53_freeze.get("status") != "frozen_before_mesh_acquisition" or t53_manifest.get("task") != "T53":
        raise FreezeError("T53 source package is not a valid prior source-only artifact")

    source_rows = {row["sourceElementFileId"]: row for row in t51["sourceElementFiles"]}
    concepts = t51["sourceConcepts"]
    concept_by_id = {row["sourceFmaConceptId"]: row for row in concepts}
    t53_ids = {row["sourceElementFileId"] for row in t53_freeze["uniqueSourceAssets"]}
    t53_detail = {row["sourceElementFileId"]: row for row in t53_manifest["sourceAssets"]}
    t53_acquired = {row["sourceElementFileId"]: row for row in t53_acq["files"] if row.get("status") == "acquired"}

    region_chunks: dict[str, dict[str, Any]] = {}
    region_members: dict[str, set[str]] = {}
    input_hashes: dict[str, str] = {
        T51_MANIFEST.relative_to(ROOT).as_posix(): sha256_bytes(t51_raw),
        T53_FREEZE.relative_to(ROOT).as_posix(): sha256_bytes(t53_freeze_raw),
        T53_MANIFEST.relative_to(ROOT).as_posix(): sha256_bytes(t53_manifest_raw),
        T53_ACQUISITION.relative_to(ROOT).as_posix(): sha256_bytes(t53_acq_raw),
        T53_GLb.relative_to(ROOT).as_posix(): sha256_file(T53_GLb),
    }
    for region_id in REGIONS:
        path = REGION_ROOT / f"{region_id}.json"
        raw = path.read_bytes()
        chunk = json.loads(raw)
        if chunk.get("revision") != "BodyParts3D-R4-T51-source-region-chunk-v1":
            raise FreezeError(f"unexpected T51 chunk revision: {region_id}")
        ids = [row["sourceElementFileId"] for row in chunk.get("assetStates", [])]
        if not ids or len(ids) != len(set(ids)) or ids != sorted(ids):
            raise FreezeError(f"empty, duplicate, or unstable T51 source IDs: {region_id}")
        if any(file_id not in source_rows for file_id in ids):
            raise FreezeError(f"T51 region {region_id} references IDs missing from its whole-source manifest")
        region_chunks[region_id] = chunk
        region_members[region_id] = set(ids)
        input_hashes[path.relative_to(ROOT).as_posix()] = sha256_bytes(raw)

    # T51 routing roots omit the left clavicle/scapula elements that T53 actually
    # carried in its thorax chunk. Keep that original routing record unchanged;
    # T54 explicitly reuses these same source IDs as shoulder-boundary nodes.
    shoulder_ids = set(region_members["shoulder-scapular"])
    for file_id, proof in SHOULDER_CONNECTORS.items():
        if file_id not in t53_ids or file_id not in t53_detail or file_id not in t53_acquired:
            raise FreezeError(f"T53 does not provide a verified source mesh for shoulder connector {file_id}")
        fma = proof["sourceFmaConceptId"]
        concept = concept_by_id.get(fma)
        if not concept or concept.get("sourceNameEnglish") != proof["expectedEnglishName"] or file_id not in concept.get("elementFileIds", []):
            raise FreezeError(f"exact source metadata does not support {file_id} as {proof['expectedEnglishName']}")
        detail_contexts = t53_detail[file_id].get("sourceContextCandidates", [])
        if not any(row.get("sourceFmaConceptId") == fma and row.get("sourceNameEnglish") == proof["expectedEnglishName"] for row in detail_contexts):
            raise FreezeError(f"T53 exact source context does not confirm shoulder connector {file_id}")
        if file_id in shoulder_ids:
            raise FreezeError(f"T51 shoulder chunk already lists the connector; review the explicit supplement")
        shoulder_ids.add(file_id)

    if shoulder_ids & region_members["upper-limb"] != {"FJ3362", "FJ3384"}:
        raise FreezeError("unexpected T51 shoulder/upper-limb overlapping source IDs")
    if not set(SHOULDER_CONNECTORS).issubset(t53_ids) or set(SHOULDER_CONNECTORS) & region_members["upper-limb"]:
        raise FreezeError("T53 cross-task connector IDs overlap the T54 upper-limb candidate set unexpectedly")

    tables = INGEST.load_tables(METADATA)
    isa_edges = INGEST.adjacency(tables["isaInclusion"])
    partof_edges = INGEST.adjacency(tables["partofInclusion"])
    hand_bone_concepts = INGEST.closure(["FMA9713", "FMA9714"], partof_edges)
    hand_muscle_concepts = INGEST.closure(["FMA37372"], isa_edges) & INGEST.closure(["FMA5022"], isa_edges)
    hand_bone_files = {row[2] for row in tables["partofCompoundElements"] if row[0] in hand_bone_concepts}
    hand_muscle_files = {row[2] for row in tables["isaCompoundElements"] if row[0] in hand_muscle_concepts}

    memberships: dict[str, set[str]] = {}
    for file_id in shoulder_ids:
        memberships.setdefault(file_id, set()).add("shoulder-scapular")
    for file_id in region_members["upper-limb"]:
        memberships.setdefault(file_id, set()).add("upper-limb")
    unique_ids = sorted(memberships)
    if len(unique_ids) != 142:
        raise FreezeError(f"expected 142 unique shoulder/arm/hand source IDs including two T53 connectors; got {len(unique_ids)}")

    connector_records = []
    assets = []
    for file_id in unique_ids:
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
            raise FreezeError(f"no official T51 source context rows for {file_id}")
        for region_id in memberships[file_id]:
            chunk = region_chunks[region_id]
            if region_id == "shoulder-scapular" and file_id in SHOULDER_CONNECTORS:
                proof = SHOULDER_CONNECTORS[file_id]
                connector_records.append({
                    "sourceElementFileId": file_id,
                    "regionId": region_id,
                    "sourceFmaConceptId": proof["sourceFmaConceptId"],
                    "sourceNameEnglish": proof["expectedEnglishName"],
                    "sourceBasis": "exact T51 whole-source concept/FJ relation plus same verified source FJ already acquired in T53 thorax; T51 shoulder routing chunk omitted this left-side FJ",
                    "sharedSourceNodeWithTask": "T53",
                    "notCanonicalMembership": True,
                })
            elif file_id not in chunk["sourceElementFileIds"]:
                raise FreezeError(f"non-connector source ID has no T51 region membership: {region_id}/{file_id}")
        expected_trees = row.get("expectedInOfficialArchiveTrees", [])
        if not expected_trees or any(tree not in {"IS-A", "PART-OF"} for tree in expected_trees):
            raise FreezeError(f"missing official archive-tree context for {file_id}")
        assets.append({
            "sourceElementFileId": file_id,
            "stableSourceMeshNodeId": f"HA-MESH-BP3D4-{file_id}",
            "regionMemberships": sorted(memberships[file_id]),
            "expectedArchiveTrees": expected_trees,
            "sourceContextRowCount": row["sourceContextRowCount"],
            "sourceContexts": contexts,
            "handBoneSourceContexts": [c for c in contexts if c["sourceFmaConceptId"] in hand_bone_concepts],
            "handMuscleSourceContexts": [c for c in contexts if c["sourceFmaConceptId"] in hand_muscle_concepts],
            "canonicalLearnerIds": [],
            "priorT53SourceCachePath": t53_acquired[file_id]["cacheRelativePath"] if file_id in t53_detail else None,
        })

    batches = []
    for start in range(0, len(unique_ids), BATCH_LIMIT):
        ids = unique_ids[start : start + BATCH_LIMIT]
        batches.append({"batchId": f"T54-B{len(batches)+1:02d}", "sourceElementFileIds": ids})

    region_rows = []
    for region_id in REGIONS:
        chunk = region_chunks[region_id]
        ids = sorted(shoulder_ids if region_id == "shoulder-scapular" else region_members[region_id])
        region_rows.append({
            "regionId": region_id,
            "labelKo": chunk["labelKo"],
            "t51CandidateSourceElementFileCount": len(chunk["assetStates"]),
            "sourceElementFileIds": ids,
            "sourceElementFileCount": len(ids),
            "t51ChunkSha256": input_hashes[(REGION_ROOT / f"{region_id}.json").relative_to(ROOT).as_posix()],
            "sourceRoots": chunk["sourceRoots"],
            "sourceBoneConceptIds": chunk["sourceBoneConceptIds"],
            "sourceMuscleConceptIds": chunk["sourceMuscleConceptIds"],
            "explicitBoundaryConnectors": [row for row in connector_records if row["regionId"] == region_id],
        })

    membership_lines = [f"{region}|{file_id}" for region in REGIONS for file_id in region_rows[REGIONS.index(region)]["sourceElementFileIds"]]
    result: dict[str, Any] = {
        "revision": "BodyParts3D-R4-T54-FROZEN-ATOMIC-SOURCE-SET-v1",
        "task": "T54",
        "frozenAt": datetime.now(timezone.utc).isoformat(),
        "status": "frozen_before_T54_acquisition",
        "source": {"sourceId": SOURCE_ID, "version": SOURCE_VERSION, "officialT51Manifest": T51_MANIFEST.relative_to(ROOT).as_posix(), "frame": FRAME, "sourceUnit": "per-file OBJ Bounds(mm) header to be verified after acquisition", "pose": "bodyparts3d-r4-static-reference", "archiveProfile": "official 99%-reduced source only; no multilevel LOD chain is advertised"},
        "scope": {"regionIds": list(REGIONS), "wholeBodyCanonicalDenominator": None, "canonicalMembershipCreated": False, "newClipCreated": False, "noCrossSourceVisualRegistration": True},
        "inputSha256": input_hashes,
        "frozenMembershipSha256": sha256_bytes(("\n".join(membership_lines) + "\n").encode("utf-8")),
        "regionSets": region_rows,
        "uniqueSourceAssets": assets,
        "uniqueSourceElementFileCount": len(assets),
        "sourceMembershipCount": sum(len(row["sourceElementFileIds"]) for row in region_rows),
        "duplicatedMembershipReferences": {row["sourceElementFileId"]: row["regionMemberships"] for row in assets if len(row["regionMemberships"]) > 1},
        "explicitT53SharedNodes": connector_records,
        "handPickingPolicy": {"handBoneFmaRootIds": ["FMA9713", "FMA9714"], "handMuscleFmaRootId": "FMA37372", "handBoneSourceFileCount": len(hand_bone_files & set(unique_ids)), "handMuscleSourceFileCount": len(hand_muscle_files & set(unique_ids)), "eachSourceFjHasSeparatePickTarget": True, "canonicalSelectionOrHumanReview": False},
        "lodPolicy": {"sourceLevelCount": 1, "sourceProfile": "official 99%-reduced BodyParts3D R4 archive", "alternateSourceLodAvailable": False, "generatedDecimationOrProxy": False, "fjsuffixMIsNotTreatedAsLod": True, "pickingTargetIsIndependentOfLod": True},
        "internalBatches": batches,
        "internalBatchSizeLimit": BATCH_LIMIT,
        "rightsBoundary": {"officialCurrentLicense": "CC BY 4.0 with attribution per current official README", "perFileLegacyHeaders": "record exact source OBJ header; public redistribution held pending reconciliation", "wholeArchiveDownloaded": False},
        "identityPolicy": "BodyParts3D FMA concept ID, BP representation ID, FJ source mesh ID, stable HA-MESH source node ID, and canonical HA learner ID remain distinct. No canonical IDs or anatomy claims are created.",
    }
    result["frozenSetSha256"] = sha256_bytes(canonical_bytes(result))
    if OUT.exists():
        old = json.loads(OUT.read_text(encoding="utf-8"))
        if old.get("inputSha256") != input_hashes or old.get("frozenMembershipSha256") != result["frozenMembershipSha256"]:
            raise FreezeError("existing T54 freeze differs from current inputs; refusing to overwrite")
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
    print(json.dumps({"path": OUT.relative_to(ROOT).as_posix(), "status": result["status"], "uniqueSourceElementFileCount": result["uniqueSourceElementFileCount"], "sourceMembershipCount": result["sourceMembershipCount"], "regionCounts": {row["regionId"]: row["sourceElementFileCount"] for row in result["regionSets"]}, "batchCount": len(result["internalBatches"]), "maxBatchSize": max(map(lambda row: len(row["sourceElementFileIds"]), result["internalBatches"])), "sharedT53Nodes": [row["sourceElementFileId"] for row in result["explicitT53SharedNodes"]], "frozenMembershipSha256": result["frozenMembershipSha256"], "frozenSetSha256": result["frozenSetSha256"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
