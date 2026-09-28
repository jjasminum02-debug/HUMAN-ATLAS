#!/usr/bin/env python3
"""Freeze only T102's exact BodyParts3D R4 members before fetching mesh bytes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "work/evidence/T102/frozen-source-set.json"
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
SCOPE = ROOT / "atlas-data/catalog/target-scope-t96.json"
T78_TARGETS = ROOT / "work/evidence/T78/targets.json"
IDS = ["FJ1441", "FJ1441M", "FJ1442", "FJ1442M", "FJ1443", "FJ1443M", "FJ1444", "FJ1444M", "FJ1445", "FJ1445M"]
ROWS = [
    ("FJ1441", "FMA38934", "right vastus intermedius", "FMA22433", "vastus intermedius", "TA2:2619", "thigh", "right"),
    ("FJ1441M", "FMA38935", "left vastus intermedius", "FMA22433", "vastus intermedius", "TA2:2619", "thigh", "left"),
    ("FJ1442", "FMA38930", "right vastus lateralis", "FMA22431", "vastus lateralis", "TA2:2618", "thigh", "right"),
    ("FJ1442M", "FMA38931", "left vastus lateralis", "FMA22431", "vastus lateralis", "TA2:2618", "thigh", "left"),
    ("FJ1443", "FMA38932", "right vastus medialis", "FMA22432", "vastus medialis", "TA2:2620", "thigh", "right"),
    ("FJ1443M", "FMA38933", "left vastus medialis", "FMA22432", "vastus medialis", "TA2:2620", "thigh", "left"),
    ("FJ1444", "FMA45891", "short head of right biceps femoris", "FMA45890", "short head of biceps femoris", "TA2:2640", "thigh", "right"),
    ("FJ1444M", "FMA45892", "short head of left biceps femoris", "FMA45890", "short head of biceps femoris", "TA2:2640", "thigh", "left"),
    ("FJ1445", "FMA46020", "transverse head of right adductor hallucis", "FMA46015", "transverse head of adductor hallucis", "TA2:2678", "foot", "right"),
    ("FJ1445M", "FMA46021", "transverse head of left adductor hallucis", "FMA46015", "transverse head of adductor hallucis", "TA2:2678", "foot", "left"),
]
ARCHIVE_URL = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip"
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
TRANSFORM = "[x,y,z] source mm -> [x,z,-y] HUMAN ATLAS m; preserve x sign; no mirror or recenter"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_tsv(name: str) -> list[list[str]]:
    return [line.split("\t") for line in (METADATA / name).read_text(encoding="utf-8").splitlines()[1:]]


def main() -> int:
    concepts = {row[0]: row for row in read_tsv("isa_parts_list_e.txt")}
    elements = read_tsv("isa_element_parts.txt")
    inclusions = read_tsv("isa_inclusion_relation_list.txt")
    t96 = json.loads(SCOPE.read_text(encoding="utf-8"))
    t78 = json.loads(T78_TARGETS.read_text(encoding="utf-8"))
    t96_by_id = {row["id"]: row for row in t96["targets"]}
    t78_by_id = {row["id"]: row for row in t78}
    task_text = (ROOT / "work/tasks/T102.md").read_text(encoding="utf-8")
    queue = json.loads((ROOT / "work/evidence/T78/execution-queue.json").read_text(encoding="utf-8"))
    job = next((row for row in queue.get("jobs", []) if isinstance(row, dict) and row.get("id") == "T102"), None)
    if job is None or any(fid not in job.get("prompt", "") for fid in IDS):
        raise SystemExit("T78 queue does not preserve all exact frozen T102 IDs")
    if any(fid not in task_text for fid in IDS) or len(IDS) != len(set(IDS)):
        raise SystemExit("T102 task text and exact source allowlist disagree")

    assets: list[dict[str, Any]] = []
    for fid, side_fma, side_name, generic_fma, generic_name, target_id, owner, side in ROWS:
        side_concept = concepts.get(side_fma)
        generic_concept = concepts.get(generic_fma)
        target = t96_by_id.get(target_id)
        prior_target = t78_by_id.get(target_id)
        expected_element = [side_fma, side_name, fid]
        parent_relation = [generic_fma, generic_name, side_fma, side_name]
        if not side_concept or len(side_concept) != 3 or side_concept[0] != side_fma or side_concept[2] != side_name:
            raise SystemExit(f"Exact FMA/BP/name concept row missing for {fid}")
        if not generic_concept or generic_concept[2] != generic_name or expected_element not in elements:
            raise SystemExit(f"Exact source concept/member row missing for {fid}")
        if parent_relation not in inclusions:
            raise SystemExit(f"Exact generic-to-side relation missing for {fid}")
        if not target or not prior_target:
            raise SystemExit(f"T96/T78 target candidate missing for {fid}")
        if fid not in target.get("existingEvidence", {}).get("sourceLexicalCandidates", []) or fid not in prior_target.get("sourceCandidates", []):
            raise SystemExit(f"T78/T96 source candidate drift for {fid}")
        if target.get("primaryOwner") != owner or target.get("regionIds") != [owner]:
            raise SystemExit(f"Frozen primary owner/region differs for {target_id}: {owner}")
        if side not in side_name:
            raise SystemExit(f"Explicit side word absent from official source name for {fid}")
        assets.append({
            "sourceElementFileId": fid, "archiveTree": "IS-A", "sourceConceptId": side_fma,
            "sourceRepresentationId": side_concept[1], "sourceNameEnglish": side_name, "sourceSide": side,
            "sourceSideEvidence": f"Exact BodyParts3D R4 IS-A concept/name {side_fma} '{side_name}' and exact FJ element row; not inferred from suffix or coordinates.",
            "officialConceptRow": side_concept, "officialElementRow": expected_element,
            "officialGenericPartConceptRow": generic_concept, "officialParentRelationRow": parent_relation,
            "allOfficialElementRowsForSameFj": sorted([row for row in elements if row[2] == fid]),
            "targetCandidateId": target_id,
            "targetCandidateMeaning": "T78/T96 lexical candidate only; no canonical identity, learner binding, label, or review approval is created.",
            "primaryOwner": owner, "regionIds": [owner], "sourceUnit": "mm from exact selected OBJ Bounds(mm) header",
            "sourceFrame": "BodyParts3D Release 4.0 native static reference; not registered to OpenSim",
            "projectFrame": FRAME, "projectUnit": "m", "pose": POSE, "transform": TRANSFORM,
        })

    membership = "\n".join("|".join([r["sourceElementFileId"], r["sourceConceptId"], r["sourceRepresentationId"], r["sourceSide"], r["targetCandidateId"], r["primaryOwner"]]) for r in assets) + "\n"
    relative_inputs = [
        "AGENTS.md", "work/tasks/T102.md", "work/task-registry-r15.json", "work/STATUS.md",
        "design/2026-09-25-muscle-atlas/00-START-HERE.md", "design/2026-09-25-muscle-atlas/03-LUNA-SERIAL-RUNBOOK.md",
        "design/2026-09-25-muscle-atlas/22-EFFICIENT-DELIVERY-AND-PERFORMANCE.md", "design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md",
        "work/evidence/T78/execution-queue.json", "work/evidence/T78/source-elements.json", "work/evidence/T78/targets.json",
        "work/evidence/T78/target-task-map.json", "atlas-data/catalog/target-scope-t96.json",
        "atlas-data/source-cache/bodyparts3d-r4/metadata/isa_parts_list_e.txt", "atlas-data/source-cache/bodyparts3d-r4/metadata/isa_element_parts.txt",
        "atlas-data/source-cache/bodyparts3d-r4/metadata/isa_inclusion_relation_list.txt", "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json",
        "atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json", "atlas-data/manifests/bodyparts3d-r4-t79/source-manifest.json",
        "atlas-data/manifests/bodyparts3d-r4-t79/integration-extension.json", "atlas-data/manifests/bodyparts3d-r4-t101/source-manifest.json",
        "atlas-data/manifests/bodyparts3d-r4-t101/integration-extension.json", "work/evidence/T50/scene-contract.md",
        "work/evidence/T69/diagnostic.json", "work/evidence/T69/assessment.json", "work/evidence/T101/validation.json",
        "work/evidence/T101/browser-validation.json", "atlas-data/tools/acquire_bodyparts3d_r4_t101.py",
        "atlas-data/tools/build_bodyparts3d_r4_t101.py", "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py",
        "atlas-data/tools/ingest_bodyparts3d_r4.py", "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py",
    ]
    paths = {rel: ROOT / rel for rel in relative_inputs}
    missing = [rel for rel, path in paths.items() if not path.is_file()]
    if missing:
        raise SystemExit(f"required T102 input missing: {missing}")
    result = {
        "schemaVersion": "1.0.0", "revision": "BodyParts3D-R4-T102-FROZEN-TEN-SELECTED-SOURCE-MEMBERS-v1",
        "task": "T102", "status": "frozen_before_mesh_acquisition", "sourceVersion": "BodyParts3D Release 4.0",
        "sourceArchiveTree": "IS-A", "archiveUrl": ARCHIVE_URL, "fullArchiveDownload": False,
        "sourceElementFileIds": IDS, "sourceMemberCount": len(assets),
        "internalBatches": [{"batchId": "T102-B01", "sourceElementFileIds": IDS, "count": len(IDS)}],
        "membershipSha256": sha(membership.encode()), "inputSha256": {rel: sha(path.read_bytes()) for rel, path in paths.items()},
        "metadataSha256": {name: sha((METADATA / name).read_bytes()) for name in ["isa_parts_list_e.txt", "isa_element_parts.txt", "isa_inclusion_relation_list.txt"]},
        "sourceOnly": True, "canonicalBinding": "none", "humanAnatomyReview": "not_performed", "publicRedistribution": "held",
        "assets": assets,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"result": "pass", "frozenSourceMembers": len(assets), "membershipSha256": result["membershipSha256"], "output": OUT.relative_to(ROOT).as_posix()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
