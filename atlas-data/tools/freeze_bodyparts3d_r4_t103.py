#!/usr/bin/env python3
"""Freeze T103's exact ten official BodyParts3D R4 source members before download."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
OUT = ROOT / "work/evidence/T103/frozen-source-set.json"
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
TRANSFORM = "[x,y,z] source mm -> [x,z,-y] HUMAN ATLAS m; preserve x sign; no mirror/recenter"
EXPECTED = ["FJ1473", "FJ1473M", "FJ1474", "FJ1474M", "FJ1481", "FJ1481M", "FJ1514", "FJ1514M", "FJ1515", "FJ1515M"]
# Side is bound to exact side-specific FMA rows in the cached official R4 table;
# no FJ suffix or coordinate is used to infer it.
IDENTITY = {
    "FJ1473": ("FMA38617", "FMA38615", "right"),
    "FJ1473M": ("FMA38618", "FMA38615", "left"),
    "FJ1474": ("FMA38560", "FMA38558", "right"),
    "FJ1474M": ("FMA38561", "FMA38558", "left"),
    "FJ1481": ("FMA46121", "FMA46119", "right"),
    "FJ1481M": ("FMA46122", "FMA46119", "left"),
    "FJ1514": ("FMA65198", "FMA46104", "right"),
    "FJ1514M": ("FMA65199", "FMA46104", "left"),
    "FJ1515": ("FMA46123", "FMA46120", "right"),
    "FJ1515M": ("FMA46124", "FMA46120", "left"),
}
IMMUTABLE_INPUTS = [
    "AGENTS.md", "work/tasks/T103.md", "work/reports/T102.md",
    "work/evidence/T102/validation.json", "work/evidence/T102/browser-validation.json",
    "work/evidence/T50/scene-contract.md", "work/evidence/T69/diagnostic.json", "work/evidence/T69/assessment.json",
    "work/evidence/T78/execution-queue.json", "work/evidence/T78/target-task-map.json",
    "atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json", "atlas-data/manifests/bodyparts3d-r4-t54/upper-limb.json",
    "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json",
    "atlas-data/manifests/bodyparts3d-r4-t79/source-manifest.json", "atlas-data/manifests/bodyparts3d-r4-t79/integration-extension.json",
    "atlas-data/manifests/bodyparts3d-r4-t101/source-manifest.json", "atlas-data/manifests/bodyparts3d-r4-t101/integration-extension.json",
    "atlas-data/manifests/bodyparts3d-r4-t102/source-manifest.json", "atlas-data/manifests/bodyparts3d-r4-t102/integration-extension.json",
    "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py", "atlas-data/tools/ingest_bodyparts3d_r4.py",
    "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py", "atlas-data/tools/acquire_bodyparts3d_r4_t103.py",
    "atlas-data/tools/freeze_bodyparts3d_r4_t103.py",
]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_ingest():
    path = ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py"
    spec = importlib.util.spec_from_file_location("t103_r4_ingest", path)
    if not spec or not spec.loader:
        raise RuntimeError("could not load the existing R4 metadata parser")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_freeze() -> dict[str, Any]:
    ingest = load_ingest()
    tables = ingest.load_tables(METADATA)
    concepts = {row[0]: row for row in tables["isaConcepts"]}
    element_rows = {tuple(row) for row in tables["isaCompoundElements"]}
    inclusions = {tuple(row) for row in tables["isaInclusion"]}
    assets: list[dict[str, Any]] = []
    for file_id in EXPECTED:
        side_fma, generic_fma, side = IDENTITY[file_id]
        direct = sorted(row for row in element_rows if row[2] == file_id)
        exact_rows = [row for row in direct if row[0] == side_fma]
        generic_rows = [row for row in direct if row[0] == generic_fma]
        if len(exact_rows) != 1 or len(generic_rows) != 1:
            raise RuntimeError(f"official exact side/generic element rows are not one-to-one for {file_id}")
        exact_element = exact_rows[0]
        generic_element = generic_rows[0]
        concept = concepts.get(side_fma)
        generic_concept = concepts.get(generic_fma)
        if not concept or not generic_concept:
            raise RuntimeError(f"official concept/BP rows missing for {file_id}")
        parent_rows = [row for row in inclusions if row[0] == generic_fma and row[2] == side_fma]
        if len(parent_rows) != 1:
            raise RuntimeError(f"exact generic-to-side IS-A row is not unique for {file_id}")
        if side not in exact_element[1].casefold():
            raise RuntimeError(f"exact side label does not agree with the frozen side for {file_id}")
        if file_id in ("FJ1473", "FJ1473M", "FJ1474", "FJ1474M") and "humeral head" not in exact_element[1].casefold():
            raise RuntimeError(f"expected an exact humeral-head source name for {file_id}")
        if file_id in ("FJ1481", "FJ1481M") and "oblique head" not in exact_element[1].casefold():
            raise RuntimeError(f"expected an exact oblique-head source name for {file_id}")
        if file_id in ("FJ1514", "FJ1514M") and "superficial head" not in exact_element[1].casefold():
            raise RuntimeError(f"expected an exact superficial-head source name for {file_id}")
        if file_id in ("FJ1515", "FJ1515M") and "transverse head" not in exact_element[1].casefold():
            raise RuntimeError(f"expected an exact transverse-head source name for {file_id}")
        assets.append({
            "sourceElementFileId": file_id,
            "archiveTree": "IS-A",
            "regionCandidates": ["upper-limb"],
            "primaryOwner": "upper-limb",
            "sideFromExactOfficialName": side,
            "sideEvidence": {"sourceConceptRow": list(concept), "sourceElementRow": list(exact_element),
                             "genericSameFjRow": list(generic_element), "notInferredFromFjSuffixOrBounds": True},
            "sourceConceptId": side_fma,
            "sourceRepresentationId": concept[1],
            "sourceNameEnglish": concept[2],
            "officialConceptRow": list(concept),
            "officialExactElementRow": list(exact_element),
            "officialGenericPartConceptRow": list(generic_concept),
            "officialGenericPartElementRow": list(generic_element),
            "officialParentRelationRow": list(parent_rows[0]),
            "allOfficialElementRowsForSameFj": [list(row) for row in direct],
            "sourceUnit": "mm_from_exact_OBJ_Bounds_header",
            "sourceFrame": "BodyParts3D Release 4.0 native static reference; not registered to OpenSim",
            "projectUnit": "m", "projectFrame": FRAME, "pose": POSE, "transform": TRANSFORM,
        })

    atomic = [{"sourceElementFileId": fid, "regionCandidates": ["upper-limb"],
               "expectedArchiveTrees": ["IS-A"], "preferredArchiveTree": "IS-A"} for fid in EXPECTED]
    membership = "\n".join(row["sourceElementFileId"] + "|upper-limb|IS-A" for row in atomic) + "\n"
    parent_t54 = json.loads((ROOT / "atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json").read_text())
    parent_matches = [row for row in parent_t54.get("sourceAssets", [])
                      if row.get("sourceElementFileId") in {"FJ1469", "FJ1469M"}]
    parent_ids = set()
    for path in [ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json",
                 ROOT / "atlas-data/manifests/bodyparts3d-r4-t79/integration-extension.json",
                 ROOT / "atlas-data/manifests/bodyparts3d-r4-t101/integration-extension.json",
                 ROOT / "atlas-data/manifests/bodyparts3d-r4-t102/integration-extension.json"]:
        doc = json.loads(path.read_text())
        if "chunks" in doc:
            chunks = doc["chunks"]
        else:
            chunks = doc.get("chunks", [])
        for chunk in chunks:
            parent_ids.update(asset.get("id") for asset in chunk.get("assets", []))
    for fid in EXPECTED:
        if f"HA-MESH-BP3D4-{fid}" in parent_ids:
            raise RuntimeError(f"T103 exact source node already exists in active parent scene: {fid}")
    if {row.get("sourceElementFileId") for row in parent_matches} != {"FJ1469", "FJ1469M"}:
        raise RuntimeError("T54 active parent/whole-muscle candidates for flexor pollicis brevis are incomplete")
    input_hashes = {}
    for rel in IMMUTABLE_INPUTS:
        path = ROOT / rel
        if not path.is_file():
            raise RuntimeError(f"required T103 freeze input is missing: {rel}")
        input_hashes[rel] = sha(path.read_bytes())
    metadata_hashes = {path.name: sha(path.read_bytes()) for path in sorted(METADATA.glob("*.txt"))}
    return {
        "revision": "BodyParts3D-R4-T103-FROZEN-SOURCE-SET-v1", "task": "T103",
        "status": "frozen_before_mesh_acquisition", "sourceVersion": "BodyParts3D Release 4.0",
        "sourceUrl": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip",
        "officialArchiveTree": "IS-A", "officialMetadataBasis": "cached official BodyParts3D R4 IS-A FMA 3.0 tables",
        "scope": "Only the ten FJ IDs in work/tasks/T103.md; no other member or full archive.",
        "sourceElementFileIds": EXPECTED, "atomicSourceFiles": atomic,
        "membershipCanonical": membership, "frozenMembershipSha256": sha(membership.encode()),
        "sourceMappings": assets,
        "wholeMuscleParentCandidates": [{"conceptFma": "FMA37378", "name": "flexor pollicis brevis",
                                           "fjs": ["FJ1469", "FJ1469M"],
                                           "activeParentSceneMatches": ["FJ1469", "FJ1469M"],
                                           "relationshipNote": "The generic whole-muscle concept and side-specific concept rows reuse each FJ; the current T54 scene contains these whole-muscle candidate surfaces."}],
        "otherTargetWholeMuscleCandidates": "Exact source metadata and the active parent manifests are recorded in T103 validation; no parent node is inferred from a name alone.",
        "inputSha256": input_hashes, "metadataSha256": metadata_hashes,
        "parentWholeMuscleCandidateEvidence": [{"path": "atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json",
                                                  "sourceElementFileId": row.get("sourceElementFileId"),
                                                  "sourceSha256": row.get("sourceSha256"),
                                                  "sourceConceptId": row.get("sourceConceptId"),
                                                  "sourceRepresentationId": row.get("sourceRepresentationId"),
                                                  "sourceNameEnglish": row.get("sourceNameEnglish"),
                                                  "side": row.get("lateralityFromExactSourceHeader"),
                                                  "sourceFile": row.get("sourceFile")}
                                                 for row in parent_matches],
        "noCanonicalBinding": True, "humanReview": "not_performed", "publicRedistribution": "held",
        "createdFromStartBaselineSha256": sha((ROOT / "work/evidence/T103/start-baseline.json").read_bytes()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the frozen source set without writing")
    args = parser.parse_args()
    result = build_freeze()
    encoded = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != encoded:
            raise SystemExit("T103 frozen source set differs; rerun freeze only after reviewing the exact source mapping")
    else:
        if OUT.exists() and OUT.read_text(encoding="utf-8") != encoded:
            raise SystemExit("refusing to overwrite a different T103 source freeze")
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(encoded, encoding="utf-8")
    print(json.dumps({"task": "T103", "sourceIds": len(EXPECTED), "membershipSha256": result["frozenMembershipSha256"], "status": result["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
