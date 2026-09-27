#!/usr/bin/env python3
"""Freeze T53 BodyParts3D R4 source memberships before mesh acquisition."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
T51_MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json"
REGION_ROOT = ROOT / "atlas-data/manifests/bodyparts3d-r4-regions-t51"
OUT = ROOT / "work/evidence/T53/frozen-source-set.json"
REGIONS = ("back", "thorax", "abdomen-lumbar", "pelvis-perineum", "gluteal-hip")
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
SOURCE_VERSION = "BodyParts3D Release 4.0"
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
FJ_ID = re.compile(r"^FJ[0-9]+M?$")
BATCH_SIZE = 10


class FreezeError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def freeze() -> dict[str, Any]:
    t51_raw = T51_MANIFEST.read_bytes()
    t51 = json.loads(t51_raw)
    if t51.get("revision") != "BodyParts3D-R4-T51-source-inventory-v1":
        raise FreezeError("T51 source inventory revision is not the expected R4 input")
    source_files = {row["sourceElementFileId"]: row for row in t51["sourceElementFiles"]}
    concepts = {row["sourceFmaConceptId"]: row for row in t51["sourceConcepts"]}

    region_rows: list[dict[str, Any]] = []
    memberships: dict[str, set[str]] = {}
    member_contexts: dict[str, dict[str, set[str]]] = {}
    input_hashes = {T51_MANIFEST.relative_to(ROOT).as_posix(): sha256_bytes(t51_raw)}
    source_ids_by_region: dict[str, list[str]] = {}

    for region_id in REGIONS:
        path = REGION_ROOT / f"{region_id}.json"
        if not path.is_file():
            raise FreezeError(f"required T51 region candidate file is missing: {path}")
        raw = path.read_bytes()
        chunk = json.loads(raw)
        if chunk.get("revision") != "BodyParts3D-R4-T51-source-region-chunk-v1":
            raise FreezeError(f"unexpected T51 region chunk revision: {region_id}")
        ids = chunk.get("sourceElementFileIds")
        if not isinstance(ids, list) or not ids or len(ids) != len(set(ids)):
            raise FreezeError(f"empty or duplicate T51 source membership for {region_id}")
        if ids != sorted(ids):
            raise FreezeError(f"T51 region IDs must be stable-sorted before freezing: {region_id}")
        bone_concepts = set(chunk.get("sourceBoneConceptIds", []))
        muscle_concepts = set(chunk.get("sourceMuscleConceptIds", []))
        per_region_contexts: dict[str, dict[str, list[dict[str, Any]]]] = {}
        for file_id in ids:
            if not FJ_ID.fullmatch(file_id):
                raise FreezeError(f"invalid source ELEMENT File ID {file_id!r}")
            source_row = source_files.get(file_id)
            if source_row is None:
                raise FreezeError(f"T51 region {region_id} references absent source ID {file_id}")
            if region_id not in source_row.get("candidateProductRegionIds", []):
                raise FreezeError(f"T51 source crosswalk disagrees about {file_id} membership in {region_id}")
            context_rows = []
            for concept in t51["sourceConcepts"]:
                if file_id not in concept.get("elementFileIds", []):
                    continue
                fma_id = concept["sourceFmaConceptId"]
                context_rows.append({
                    "sourceFmaConceptId": fma_id,
                    "sourceNameEnglish": concept["sourceNameEnglish"],
                    "sourceTrees": concept["sourceTrees"],
                    "representations": concept["representations"],
                    "regionContextKind": [kind for kind, ids_set in (("bone", bone_concepts), ("muscle", muscle_concepts)) if fma_id in ids_set],
                })
            if not context_rows:
                raise FreezeError(f"T51 source FJ has no official FMA context: {file_id}")
            per_region_contexts[file_id] = {"contexts": context_rows}
            memberships.setdefault(file_id, set()).add(region_id)
            kind_map = member_contexts.setdefault(file_id, {"boneFmaIds": set(), "muscleFmaIds": set()})
            kind_map["boneFmaIds"].update(row["sourceFmaConceptId"] for row in context_rows if "bone" in row["regionContextKind"])
            kind_map["muscleFmaIds"].update(row["sourceFmaConceptId"] for row in context_rows if "muscle" in row["regionContextKind"])

        input_hashes[path.relative_to(ROOT).as_posix()] = sha256_bytes(raw)
        source_ids_by_region[region_id] = ids
        region_rows.append({
            "regionId": region_id,
            "labelKo": chunk["labelKo"],
            "sourceRoots": chunk["sourceRoots"],
            "sourceBoneConceptIds": sorted(bone_concepts),
            "sourceMuscleConceptIds": sorted(muscle_concepts),
            "sourceElementFileIds": ids,
            "sourceElementFileCount": len(ids),
            "sourceMeshClassCounts": {
                "boneContextElementFiles": sum(bool(member_contexts[file_id]["boneFmaIds"]) for file_id in ids),
                "muscleContextElementFiles": sum(bool(member_contexts[file_id]["muscleFmaIds"]) for file_id in ids),
                "bothContextElementFiles": sum(bool(member_contexts[file_id]["boneFmaIds"]) and bool(member_contexts[file_id]["muscleFmaIds"]) for file_id in ids),
            },
            "t51ChunkStatus": chunk["status"],
            "t51ChunkSha256": sha256_bytes(raw),
        })

    unique_ids = sorted(memberships)
    batches = []
    for start in range(0, len(unique_ids), BATCH_SIZE):
        batch_ids = unique_ids[start : start + BATCH_SIZE]
        batches.append({"batchId": f"T53-B{len(batches)+1:02d}", "sourceElementFileIds": batch_ids})

    asset_rows = []
    for file_id in unique_ids:
        source_row = source_files[file_id]
        kinds = member_contexts[file_id]
        asset_rows.append({
            "sourceElementFileId": file_id,
            "regionMemberships": sorted(memberships[file_id]),
            "expectedArchiveTrees": source_row["expectedInOfficialArchiveTrees"],
            "sourceContextRowCount": source_row["sourceContextRowCount"],
            "sourceContexts": [
                {"sourceFmaConceptId": c["sourceFmaConceptId"], "sourceNameEnglish": c["sourceNameEnglish"], "sourceTrees": c["sourceTrees"], "representations": c["representations"]}
                for c in t51["sourceConcepts"] if file_id in c.get("elementFileIds", [])
            ],
            "regionScopedBoneFmaIds": sorted(kinds["boneFmaIds"]),
            "regionScopedMuscleFmaIds": sorted(kinds["muscleFmaIds"]),
            "sourceIdentityState": "T51-source-index-only-header-not-yet-read",
            "sourceUnitState": "not-independently-read-from-this-OBJ",
            "canonicalLearnerIds": [],
        })

    membership_lines = []
    for region_id in REGIONS:
        membership_lines.extend(f"{region_id}|{file_id}" for file_id in source_ids_by_region[region_id])
    membership_hash = sha256_bytes(("\n".join(membership_lines) + "\n").encode("utf-8"))
    input_hashes.update({
        "atlas-data/source-cache/bodyparts3d-r4/metadata/isa_element_parts.txt": sha256_file(ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata/isa_element_parts.txt"),
        "atlas-data/source-cache/bodyparts3d-r4/metadata/partof_element_parts.txt": sha256_file(ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata/partof_element_parts.txt"),
        "atlas-data/source-cache/bodyparts3d-r4/metadata/isa_inclusion_relation_list.txt": sha256_file(ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata/isa_inclusion_relation_list.txt"),
        "atlas-data/source-cache/bodyparts3d-r4/metadata/partof_inclusion_relation_list.txt": sha256_file(ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata/partof_inclusion_relation_list.txt"),
    })
    result = {
        "revision": "BodyParts3D-R4-T53-FROZEN-ATOMIC-SOURCE-SET-v1",
        "task": "T53",
        "frozenAt": datetime.now(timezone.utc).isoformat(),
        "status": "frozen_before_mesh_acquisition",
        "source": {"sourceId": SOURCE_ID, "version": SOURCE_VERSION, "officialT51Manifest": T51_MANIFEST.relative_to(ROOT).as_posix(), "frame": FRAME, "sourceUnit": "mm, to be checked in each acquired OBJ Bounds(mm) header", "pose": POSE, "lod": "official 99%-reduced archive; no multilevel LOD chain asserted"},
        "scope": {"regionIds": list(REGIONS), "sourceRegionsFrozenSeparately": True, "sourceSetIsT51CandidateMembershipNotCanonicalCoverage": True, "wholeBodyCanonicalDenominator": None, "canonicalLearnerMembershipAdded": False},
        "inputSha256": input_hashes,
        "frozenMembershipSha256": membership_hash,
        "regionSets": region_rows,
        "uniqueSourceAssets": asset_rows,
        "uniqueSourceElementFileCount": len(unique_ids),
        "duplicatedMembershipReferences": {file_id: sorted(regs) for file_id, regs in sorted(memberships.items()) if len(regs) > 1},
        "internalBatches": batches,
        "internalBatchSizeLimit": BATCH_SIZE,
        "rightsBoundary": {"officialCurrentLicense": "CC BY 4.0 with required attribution per official README updated 2025-02-27", "legacyObjHeaderConflict": "preserve any per-file header; redistribution remains held pending file-level reconciliation", "wholeArchiveDownload": "forbidden; selected HTTP Range members only"},
        "identityPolicy": "FMA concepts, BP representations, FJ source mesh IDs, and canonical HA learner IDs remain separate; no new HA IDs are minted; no source surface is mirrored or swapped.",
    }
    result["frozenSetSha256"] = sha256_bytes(canonical_json(result))
    if OUT.exists():
        existing = json.loads(OUT.read_text(encoding="utf-8"))
        if existing.get("frozenMembershipSha256") != membership_hash or existing.get("inputSha256") != input_hashes:
            raise FreezeError("existing T53 freeze differs from current inputs; refusing to overwrite it")
        return existing
    write_json(OUT, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true", help="freeze the five T51 source region sets before acquisition")
    args = parser.parse_args()
    if not args.freeze:
        parser.error("only --freeze is supported by this scope-limited command")
    result = freeze()
    print(json.dumps({"path": OUT.relative_to(ROOT).as_posix(), "status": result["status"], "uniqueSourceElementFileCount": result["uniqueSourceElementFileCount"], "regions": {row["regionId"]: row["sourceElementFileCount"] for row in result["regionSets"]}, "batchCount": len(result["internalBatches"]), "frozenMembershipSha256": result["frozenMembershipSha256"], "frozenSetSha256": result["frozenSetSha256"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
