#!/usr/bin/env python3
"""Freeze T104's exact ten official BodyParts3D R4 source members before acquisition."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
OUT = ROOT / "work/evidence/T104/frozen-source-set.json"
BASELINE = ROOT / "work/evidence/T104/start-baseline.json"
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
TRANSFORM = "[x,y,z] source mm -> [x,z,-y] HUMAN ATLAS m; preserve x sign; no mirror/recenter"
ARCHIVE_URL = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip"
EXPECTED = ["FJ1516", "FJ1516M", "FJ1518", "FJ1518M", "FJ1557", "FJ1600", "FJ1601", "FJ2774", "FJ2781", "FJ2783"]

# FMA rows from the cached official BodyParts3D R4 IS-A compound-element tables.
# Side is derived only from the exact side-specific source concept/element row.
IDENTITY = {
    "FJ1516": {"sideFma": "FMA38562", "genericFma": "FMA38559", "side": "right", "region": "upper-limb", "familyFma": "FMA38559"},
    "FJ1516M": {"sideFma": "FMA38563", "genericFma": "FMA38559", "side": "left", "region": "upper-limb", "familyFma": "FMA38559"},
    "FJ1518": {"sideFma": "FMA38619", "genericFma": "FMA38616", "side": "right", "region": "upper-limb", "familyFma": "FMA38616"},
    "FJ1518M": {"sideFma": "FMA38620", "genericFma": "FMA38616", "side": "left", "region": "upper-limb", "familyFma": "FMA38616"},
    "FJ1557": {"sideFma": "FMA46288", "genericFma": "FMA46281", "side": "left", "region": "neck", "familyFma": "FMA46279"},
    "FJ1600": {"sideFma": "FMA46284", "genericFma": "FMA46280", "side": "left", "region": "neck", "familyFma": "FMA46279"},
    "FJ1601": {"sideFma": "FMA46286", "genericFma": "FMA46282", "side": "left", "region": "neck", "familyFma": "FMA46279"},
    "FJ2774": {"sideFma": "FMA46605", "genericFma": "FMA46602", "side": "left", "region": "neck", "familyFma": "FMA46602"},
    "FJ2781": {"sideFma": "FMA46614", "genericFma": "FMA46610", "side": "left", "region": "neck", "familyFma": "FMA46608"},
    "FJ2783": {"sideFma": "FMA46612", "genericFma": "FMA46609", "side": "left", "region": "neck", "familyFma": "FMA46608"},
}

INPUTS = [
    "AGENTS.md", "design/2026-09-25-muscle-atlas/00-START-HERE.md", "design/2026-09-25-muscle-atlas/03-LUNA-SERIAL-RUNBOOK.md",
    "design/2026-09-25-muscle-atlas/13-CONTINUOUS-WHOLE-BODY-EXPERIENCE-R15.md", "design/2026-09-25-muscle-atlas/14-TASK-PROMPTS-R15.md",
    "design/2026-09-25-muscle-atlas/15-NERVE-AND-ASSESSMENT-SCOPE-R15.md", "design/2026-09-25-muscle-atlas/16-ASTRA-UI-HANDOFF.md",
    "design/2026-09-25-muscle-atlas/22-EFFICIENT-DELIVERY-AND-PERFORMANCE.md", "design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md",
    "design/2026-09-25-muscle-atlas/24-WORKBOOK-FACE-AND-OBSERVATION.md", "work/tasks/T104.md", "work/reports/T103.md",
    "work/evidence/T103/validation.json", "work/evidence/T103/preservation.json", "work/evidence/T103/browser-validation.json",
    "work/evidence/T103/frozen-source-set.json", "work/evidence/T103/source-acquisition.json", "work/evidence/T78/execution-queue.json",
    "work/evidence/T78/source-elements.json", "work/evidence/T78/target-task-map.json", "work/evidence/T50/scene-contract.md",
    "work/evidence/T69/diagnostic.json", "work/evidence/T69/assessment.json", "work/evidence/T104/start-baseline.json",
    "atlas-data/source-cache/bodyparts3d-r4/metadata/isa_parts_list_e.txt", "atlas-data/source-cache/bodyparts3d-r4/metadata/isa_element_parts.txt",
    "atlas-data/source-cache/bodyparts3d-r4/metadata/isa_inclusion_relation_list.txt", "atlas-data/source-cache/bodyparts3d-r4/metadata/partof_parts_list_e.txt",
    "atlas-data/source-cache/bodyparts3d-r4/metadata/partof_element_parts.txt", "atlas-data/source-cache/bodyparts3d-r4/metadata/partof_inclusion_relation_list.txt",
    "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json", "atlas-data/manifests/bodyparts3d-r4-t79/source-manifest.json",
    "atlas-data/manifests/bodyparts3d-r4-t79/integration-extension.json", "atlas-data/manifests/bodyparts3d-r4-t101/source-manifest.json",
    "atlas-data/manifests/bodyparts3d-r4-t101/integration-extension.json", "atlas-data/manifests/bodyparts3d-r4-t102/source-manifest.json",
    "atlas-data/manifests/bodyparts3d-r4-t102/integration-extension.json", "atlas-data/manifests/bodyparts3d-r4-t103/source-manifest.json",
    "atlas-data/manifests/bodyparts3d-r4-t103/integration-extension.json", "atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json",
    "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py", "atlas-data/tools/ingest_bodyparts3d_r4.py",
    "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py", "atlas-data/tools/freeze_bodyparts3d_r4_t103.py",
    "atlas-data/tools/acquire_bodyparts3d_r4_t103.py", "atlas-data/tools/build_bodyparts3d_r4_t103.py",
]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_ingest():
    path = ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py"
    spec = importlib.util.spec_from_file_location("t104_r4_ingest", path)
    if not spec or not spec.loader:
        raise RuntimeError("could not load the existing R4 metadata parser")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def active_parent_ids() -> set[str]:
    paths = [
        ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json",
        ROOT / "atlas-data/manifests/bodyparts3d-r4-t79/integration-extension.json",
        ROOT / "atlas-data/manifests/bodyparts3d-r4-t101/integration-extension.json",
        ROOT / "atlas-data/manifests/bodyparts3d-r4-t102/integration-extension.json",
        ROOT / "atlas-data/manifests/bodyparts3d-r4-t103/integration-extension.json",
    ]
    result: set[str] = set()
    for path in paths:
        doc = json.loads(path.read_text(encoding="utf-8"))
        chunks = doc.get("chunks", [])
        for chunk in chunks:
            for asset in chunk.get("assets", []):
                asset_id = asset.get("id")
                if asset_id:
                    result.add(asset_id)
    return result


def build_freeze() -> dict[str, Any]:
    if list(IDENTITY) != EXPECTED:
        raise RuntimeError("T104 source ID order/map differs from the task allowlist")
    ingest = load_ingest()
    tables = ingest.load_tables(METADATA)
    concepts = {row[0]: row for row in tables["isaConcepts"]}
    element_rows = {tuple(row) for row in tables["isaCompoundElements"]}
    inclusions = {tuple(row) for row in tables["isaInclusion"]}
    assets: list[dict[str, Any]] = []
    for file_id in EXPECTED:
        spec = IDENTITY[file_id]
        direct = sorted(row for row in element_rows if row[2] == file_id)
        exact = [row for row in direct if row[0] == spec["sideFma"]]
        generic = [row for row in direct if row[0] == spec["genericFma"]]
        if len(exact) != 1 or len(generic) != 1:
            raise RuntimeError(f"official exact side/generic rows are not one-to-one for {file_id}: exact={exact}, generic={generic}")
        exact_row, generic_row = exact[0], generic[0]
        exact_concept = concepts.get(spec["sideFma"])
        generic_concept = concepts.get(spec["genericFma"])
        family_concept = concepts.get(spec["familyFma"])
        if not exact_concept or not generic_concept or not family_concept:
            raise RuntimeError(f"official concept row missing for {file_id}")
        parent_rows = [row for row in inclusions if row[0] == spec["genericFma"] and row[2] == spec["sideFma"]]
        if len(parent_rows) != 1:
            raise RuntimeError(f"official generic-to-side parent relation is not unique for {file_id}: {parent_rows}")
        if spec["side"] not in exact_row[1].casefold() or spec["side"] not in exact_concept[2].casefold():
            raise RuntimeError(f"exact official side label contradicts T104 side map for {file_id}")
        family_members = sorted({row[2] for row in element_rows if row[0] == spec["familyFma"]})
        assets.append({
            "sourceElementFileId": file_id, "archiveTree": "IS-A", "regionOwner": spec["region"],
            "regionAssignmentBasis": "task-level product-region owner derived from exact BodyParts3D source concept anatomy labels; not a canonical identity/binding",
            "sideFromExactOfficialName": spec["side"], "sideEvidence": {"exactConceptRow": list(exact_concept), "exactElementRow": list(exact_row), "notInferredFromFjSuffixOrBounds": True},
            "sourceConceptId": spec["sideFma"], "sourceRepresentationId": exact_concept[1], "sourceNameEnglish": exact_concept[2],
            "officialConceptRow": list(exact_concept), "officialExactElementRow": list(exact_row),
            "genericPartConceptId": spec["genericFma"], "officialGenericPartConceptRow": list(generic_concept),
            "officialGenericPartElementRow": list(generic_row), "officialParentRelationRow": list(parent_rows[0]),
            "familyConceptId": spec["familyFma"], "officialFamilyConceptRow": list(family_concept),
            "familySourceElementFileIds": family_members, "allOfficialElementRowsForSameFj": [list(row) for row in direct],
            "sourceUnit": "mm_from_exact_OBJ_Bounds_header", "sourceFrame": "BodyParts3D Release 4.0 native static reference; not registered to OpenSim",
            "projectUnit": "m", "projectFrame": FRAME, "pose": POSE, "transform": TRANSFORM,
        })

    parent_ids = active_parent_ids()
    already_present = sorted(set(EXPECTED) & parent_ids)
    if already_present:
        raise RuntimeError(f"T104 source FJs already exist in the parent scene; refusing duplicate node: {already_present}")
    groups = {"upper-limb": [row["sourceElementFileId"] for row in assets if row["regionOwner"] == "upper-limb"],
              "neck": [row["sourceElementFileId"] for row in assets if row["regionOwner"] == "neck"]}
    atomic = [{"sourceElementFileId": fid, "regionCandidates": [next(x["regionOwner"] for x in assets if x["sourceElementFileId"] == fid)],
               "expectedArchiveTrees": ["IS-A"], "preferredArchiveTree": "IS-A"} for fid in EXPECTED]
    membership = "\n".join(row["sourceElementFileId"] + "|" + ",".join(row["regionCandidates"]) + "|" + ",".join(row["expectedArchiveTrees"]) for row in atomic) + "\n"
    hashes = {}
    for rel in INPUTS:
        path = ROOT / rel
        if not path.is_file():
            raise RuntimeError(f"required immutable T104 freeze input is missing: {rel}")
        hashes[rel] = sha(path.read_bytes())
    metadata_hashes = {path.name: sha(path.read_bytes()) for path in sorted(METADATA.glob("*.txt"))}
    active_parent_whole_candidates = []
    for name, fma, fjs in [
        ("ulnar head of pronator teres", "FMA38559", ["FJ1516", "FJ1516M"]),
        ("ulnar head of flexor carpi ulnaris", "FMA38616", ["FJ1518", "FJ1518M"]),
        ("longus colli component zone", "FMA46279", ["FJ1557", "FJ1600", "FJ1601"]),
        ("aryepiglotticus", "FMA46602", ["FJ2774", "FJ2791"]),
        ("cricothyroid component zone", "FMA46608", ["FJ2781", "FJ2783", "FJ2799", "FJ2801"]),
    ]:
        active_parent_whole_candidates.append({"sourceConceptId": fma, "sourceConceptLabel": name, "officialSameConceptSourceMembers": fjs,
                                               "activeParentSceneMembers": sorted(set(fjs) & parent_ids),
                                               "exactWholeMuscleParentSurfaceIdentified": False,
                                               "note": "R4 rows identify a head/component/zone; no separate exact whole-muscle source mesh is registered in the active parent scene. Same FJ aliases remain one node."})
    return {
        "revision": "BodyParts3D-R4-T104-FROZEN-SOURCE-SET-v1", "task": "T104", "status": "frozen_before_mesh_acquisition",
        "sourceVersion": "BodyParts3D Release 4.0", "sourceUrl": ARCHIVE_URL, "officialArchiveTree": "IS-A",
        "officialMetadataBasis": "cached official BodyParts3D R4 IS-A FMA 3.0 tables; exact named source rows",
        "scope": "Only the ten exact IDs in work/tasks/T104.md and the R15 execution queue; no full archive or other source member.",
        "sourceElementFileIds": EXPECTED, "atomicSourceFiles": atomic,
        "regionMemberGroups": groups, "membershipCanonical": membership, "frozenMembershipSha256": sha(membership.encode()),
        "sourceMappings": assets, "parentSceneSourceNodeCount": len(parent_ids), "parentSceneDuplicateSourceIds": already_present,
        "wholeMuscleParentSurfaceAudit": {"status": "no_exact_active_whole_parent_mesh_found_for_frozen_targets", "candidates": active_parent_whole_candidates,
                                           "comparisonPlan": "compare actual triangle surfaces of matched sibling source parts where both are in the active scene; do not treat AABB as overlap proof; sampling is not a continuous intersection proof"},
        "sceneContract": {"projectFrame": FRAME, "projectUnit": "m", "sourceId": "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0", "sourceVersion": "4.0",
                          "pose": POSE, "transform": TRANSFORM, "oneAnatomySceneRoot": True, "oneRenderer": True, "cameraOwner": "existing AnatomySceneController"},
        "rightsAndReview": {"officialDatabaseLicenseReference": "CC BY 4.0 per LSDB Archive page; local technical display evaluated separately",
                            "localDisplay": "pending per-member OBJ identity/header/bounds/frame validation", "canonicalLearnerBinding": "none",
                            "humanAnatomyReview": "not_performed", "publicRedistribution": "held_pending_file_level_project_reconciliation"},
        "inputSha256": hashes, "metadataSha256": metadata_hashes,
        "createdFromStartBaselineSha256": sha(BASELINE.read_bytes()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the exact frozen source set without writing")
    args = parser.parse_args()
    result = build_freeze()
    encoded = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != encoded:
            raise SystemExit("T104 frozen source set differs; inspect the exact official mapping before updating it")
    else:
        if OUT.exists() and OUT.read_text(encoding="utf-8") != encoded:
            if (ROOT / "work/evidence/T104/source-acquisition.json").exists():
                raise SystemExit("refusing to revise T104 source freeze after acquisition has begun")
            prior = json.loads(OUT.read_text(encoding="utf-8"))
            if prior.get("task") != "T104":
                raise SystemExit("refusing to overwrite a non-T104 source freeze")
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(encoded, encoding="utf-8")
    print(json.dumps({"task": "T104", "sourceIds": len(EXPECTED), "membershipSha256": result["frozenMembershipSha256"], "status": result["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
