#!/usr/bin/env python3
"""Freeze T101's exact BodyParts3D R4 IS-A member set before acquisition."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "work/evidence/T101/frozen-source-set.json"
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
SCOPE = ROOT / "atlas-data/catalog/target-scope-t96.json"
T78_TARGETS = ROOT / "work/evidence/T78/targets.json"
EXPECTED = [
    ("FJ1393", "FMA45973", "lateral head of right flexor hallucis brevis", "FMA45970", "lateral head of flexor hallucis brevis", "TA2:2675", "foot", "right"),
    ("FJ1393M", "FMA45974", "lateral head of left flexor hallucis brevis", "FMA45970", "lateral head of flexor hallucis brevis", "TA2:2675", "foot", "left"),
    ("FJ1394M", "FMA45961", "lateral head of left gastrocnemius", "FMA45959", "lateral head of gastrocnemius", "TA2:2658", "leg", "left"),
    ("FJ1395", "FMA45888", "long head of right biceps femoris", "FMA45887", "long head of biceps femoris", "TA2:2639", "thigh", "right"),
    ("FJ1395M", "FMA45889", "long head of left biceps femoris", "FMA45887", "long head of biceps femoris", "TA2:2639", "thigh", "left"),
    ("FJ1396", "FMA45971", "medial head of right flexor hallucis brevis", "FMA45969", "medial head of flexor hallucis brevis", "TA2:2674", "foot", "right"),
    ("FJ1396M", "FMA45972", "medial head of left flexor hallucis brevis", "FMA45969", "medial head of flexor hallucis brevis", "TA2:2674", "foot", "left"),
    ("FJ1397M", "FMA45958", "medial head of left gastrocnemius", "FMA45956", "medial head of gastrocnemius", "TA2:2659", "leg", "left"),
    ("FJ1398", "FMA46018", "oblique head of right adductor hallucis", "FMA46014", "oblique head of adductor hallucis", "TA2:2677", "foot", "right"),
    ("FJ1398M", "FMA46019", "oblique head of left adductor hallucis", "FMA46014", "oblique head of adductor hallucis", "TA2:2677", "foot", "left"),
]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_tsv(name: str) -> list[list[str]]:
    return [line.split("\t") for line in (METADATA / name).read_text(encoding="utf-8").splitlines()[1:]]


def main() -> int:
    paths = {
        "work/tasks/T101.md": ROOT / "work/tasks/T101.md",
        "work/evidence/T78/execution-queue.json": ROOT / "work/evidence/T78/execution-queue.json",
        "work/evidence/T78/targets.json": T78_TARGETS,
        "atlas-data/catalog/target-scope-t96.json": SCOPE,
        "atlas-data/source-cache/bodyparts3d-r4/metadata/isa_parts_list_e.txt": METADATA / "isa_parts_list_e.txt",
        "atlas-data/source-cache/bodyparts3d-r4/metadata/isa_element_parts.txt": METADATA / "isa_element_parts.txt",
        "atlas-data/source-cache/bodyparts3d-r4/metadata/isa_inclusion_relation_list.txt": METADATA / "isa_inclusion_relation_list.txt",
        "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json": ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json",
        "atlas-data/manifests/bodyparts3d-r4-t79/integration-extension.json": ROOT / "atlas-data/manifests/bodyparts3d-r4-t79/integration-extension.json",
        "atlas-data/manifests/bodyparts3d-r4-t79/source-manifest.json": ROOT / "atlas-data/manifests/bodyparts3d-r4-t79/source-manifest.json",
        "atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json": ROOT / "atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json",
        "work/evidence/T50/scene-contract.md": ROOT / "work/evidence/T50/scene-contract.md",
        "work/evidence/T69/diagnostic.json": ROOT / "work/evidence/T69/diagnostic.json",
    }
    missing = [relative for relative, path in paths.items() if not path.is_file()]
    if missing:
        raise SystemExit(f"required frozen input missing: {missing}")

    concepts = {row[0]: row for row in read_tsv("isa_parts_list_e.txt")}
    elements = read_tsv("isa_element_parts.txt")
    inclusions = read_tsv("isa_inclusion_relation_list.txt")
    scope = json.loads(SCOPE.read_text(encoding="utf-8"))
    targets = json.loads(T78_TARGETS.read_text(encoding="utf-8"))
    scope_by_id = {row["id"]: row for row in scope["targets"]}
    t78_by_id = {row["id"]: row for row in targets}

    expected_ids = [row[0] for row in EXPECTED]
    queue = json.loads(paths["work/evidence/T78/execution-queue.json"].read_text(encoding="utf-8"))
    queue_tasks = queue.get("jobs", [])
    queue_row = next((row for row in queue_tasks if row.get("id") == "T101"), None)
    if queue_row is None:
        raise SystemExit("T78 execution queue has no explicit T101 entry")
    prompt = queue_row.get("prompt", "")
    for file_id in expected_ids:
        if file_id not in prompt:
            raise SystemExit(f"T101 queue prompt does not contain frozen source ID {file_id}")

    assets: list[dict[str, Any]] = []
    for file_id, fma, source_name, parent_fma, parent_name, ta2_id, region, side in EXPECTED:
        concept = concepts.get(fma)
        if not concept or len(concept) != 3 or concept[2] != source_name:
            raise SystemExit(f"official exact IS-A FMA/BP/name row not found for {file_id}: {fma} / {source_name}")
        element = [fma, source_name, file_id]
        if element not in elements:
            raise SystemExit(f"official exact IS-A FMA/name/FJ element row not found: {element}")
        parent = [parent_fma, parent_name, fma, source_name]
        if parent not in inclusions:
            raise SystemExit(f"official exact IS-A parent relation not found for {file_id}: {parent}")
        source_rows = sorted([row for row in elements if row[2] == file_id])
        target = scope_by_id.get(ta2_id)
        t78 = t78_by_id.get(ta2_id)
        if not target or not t78:
            raise SystemExit(f"frozen TA2 target row is missing for {file_id}: {ta2_id}")
        target_candidates = target.get("existingEvidence", {}).get("sourceLexicalCandidates", [])
        t78_candidates = t78.get("sourceCandidates", [])
        if file_id not in target_candidates or file_id not in t78_candidates:
            raise SystemExit(f"T96/T78 lexical candidate set drift for {file_id} and {ta2_id}")
        if target.get("primaryOwner") != region or target.get("regionIds") != [region]:
            raise SystemExit(f"T96 target region/owner differs for {file_id}: {ta2_id}")
        if side not in source_name:
            raise SystemExit(f"explicit side word is absent from official exact concept name: {file_id}")
        assets.append({
            "sourceElementFileId": file_id,
            "archiveTree": "IS-A",
            "sourceConceptId": fma,
            "sourceRepresentationId": concept[1],
            "sourceNameEnglish": source_name,
            "sourceSide": side,
            "sourceSideEvidence": f"Exact official IS-A source concept/name {fma} '{source_name}' and exact FJ element row; not inferred from the FJ suffix or coordinates.",
            "officialConceptRow": concept,
            "officialElementRow": element,
            "officialParentRelationRow": parent,
            "allOfficialElementRowsForSameFj": source_rows,
            "targetCandidateId": ta2_id,
            "targetCandidateMeaning": "T78/T96 frozen lexical candidate only; no canonical identity, binding, learner label, or review approval is created.",
            "primaryOwner": region,
            "regionIds": [region],
            "sourceUnit": "mm from each exact OBJ Bounds(mm) header",
            "sourceFrame": "BodyParts3D Release 4.0 native static reference; not registered to OpenSim",
            "projectFrame": "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR",
            "projectUnit": "m",
            "pose": "bodyparts3d-r4-static-reference",
            "transform": "[x,y,z] source mm -> [x,z,-y] HUMAN ATLAS m; preserve x sign; no mirror or recenter",
        })

    membership = "\n".join(
        "|".join([r["sourceElementFileId"], r["sourceConceptId"], r["sourceRepresentationId"], r["sourceSide"], r["targetCandidateId"], r["primaryOwner"]])
        for r in assets
    ) + "\n"
    result = {
        "schemaVersion": "1.0.0",
        "revision": "BodyParts3D-R4-T101-FROZEN-TEN-SELECTED-SOURCE-MEMBERS-v1",
        "task": "T101",
        "status": "frozen_before_mesh_acquisition",
        "sourceVersion": "BodyParts3D Release 4.0",
        "sourceArchiveTree": "IS-A",
        "archiveUrl": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip",
        "fullArchiveDownload": False,
        "sourceElementFileIds": expected_ids,
        "sourceMemberCount": len(assets),
        "internalBatches": [{"batchId": "T101-B01", "sourceElementFileIds": expected_ids, "count": len(expected_ids)}],
        "membershipSha256": sha(membership.encode("utf-8")),
        "inputSha256": {relative: sha(path.read_bytes()) for relative, path in paths.items()},
        "metadataSha256": {
            "isa_parts_list_e.txt": sha((METADATA / "isa_parts_list_e.txt").read_bytes()),
            "isa_element_parts.txt": sha((METADATA / "isa_element_parts.txt").read_bytes()),
            "isa_inclusion_relation_list.txt": sha((METADATA / "isa_inclusion_relation_list.txt").read_bytes()),
        },
        "sourceOnly": True,
        "canonicalBinding": "none",
        "humanAnatomyReview": "not_performed",
        "publicRedistribution": "held",
        "assets": assets,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"result": "pass", "frozenSourceMembers": len(assets), "membershipSha256": result["membershipSha256"], "output": OUT.relative_to(ROOT).as_posix()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
