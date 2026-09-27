#!/usr/bin/env python3
"""Freeze T76's T73-derived pelvic-floor source scope before mesh acquisition."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work/evidence/T76/frozen-source-set.json"
MATRIX = ROOT / "work/evidence/T73/target-source-matrix.json"
COVERAGE = ROOT / "work/evidence/T73/region-coverage.json"
META = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
T53_SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json"
T53_REGION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t53/pelvis-perineum.json"
T70 = ROOT / "atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json"
ARCHIVE_URL = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip"
CONCEPTS = [
    ("FMA19089", "zone of levator ani", "group_or_zone"),
    ("FMA19090", "pubococcygeus", "named_muscle_concept"),
    ("FMA19092", "iliococcygeus", "named_muscle_concept"),
    ("FMA19088", "coccygeus", "named_muscle_concept"),
    ("FMA45854", "right pubococcygeus", "side_specific_muscle_concept"),
    ("FMA45855", "left pubococcygeus", "side_specific_muscle_concept"),
    ("FMA45858", "right iliococcygeus", "side_specific_muscle_concept"),
    ("FMA45859", "left iliococcygeus", "side_specific_muscle_concept"),
    ("FMA46443", "right coccygeus", "side_specific_muscle_concept"),
    ("FMA46444", "left coccygeus", "side_specific_muscle_concept"),
]
NEW_BATCHES = {
    "T76-B01": ["FJ1453M", "FJ1457M", "FJ1458M", "FJ2544", "FJ2545"],
    "T76-B02": ["FJ2546", "FJ2549", "FJ2550", "FJ2551"],
}
REUSE = {"FJ1449M", "FJ2542", "FJ2547"}
EXPECTED_ALL = ["FJ1449M", "FJ1453M", "FJ1457M", "FJ1458M", "FJ2542", "FJ2544", "FJ2545", "FJ2546", "FJ2547", "FJ2549", "FJ2550", "FJ2551"]
META_FILES = [
    "isa_parts_list_e.txt", "isa_inclusion_relation_list.txt", "isa_element_parts.txt",
    "partof_parts_list_e.txt", "partof_inclusion_relation_list.txt", "partof_element_parts.txt",
]


class FreezeError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("ha_t76_r4_ingest", path)
    if spec is None or spec.loader is None:
        raise FreezeError(f"cannot load R4 metadata parser: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def side_from_exact_name(name: str) -> str | None:
    sides = {value.casefold() for value in re.findall(r"\b(left|right)\b", name, flags=re.I)}
    if len(sides) > 1:
        raise FreezeError(f"conflicting source laterality words: {name}")
    return next(iter(sides), None)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def generate() -> dict[str, Any]:
    if OUT.exists():
        raise FreezeError("T76 source freeze already exists; do not regenerate after acquisition starts")
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    rows = [item for item in matrix.get("items", []) if item.get("task") == "T76"]
    by_fma = {item.get("sourceConceptId"): item for item in rows}
    expected_concepts = {item[0] for item in CONCEPTS}
    if len(rows) != 10 or set(by_fma) != expected_concepts:
        raise FreezeError(f"T73 T76 concept set changed: expected {sorted(expected_concepts)}, got {sorted(by_fma)}")

    ingest = load_module(ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
    tables = ingest.load_tables(META)
    concept_rows = {tuple(row) for row in tables["isaConcepts"]}
    relation_rows = {tuple(row) for row in tables["isaCompoundElements"]}
    target_concepts: list[dict[str, Any]] = []
    member_concepts: dict[str, list[dict[str, Any]]] = {}
    canonical_membership_lines: list[str] = []
    for fma, expected_name, concept_kind in CONCEPTS:
        target = by_fma[fma]
        if target.get("sourceTree") != "isaCompoundElements" or target.get("sourcePreferredName") != expected_name:
            raise FreezeError(f"T73 exact IS-A concept identity/name/tree changed: {fma}")
        representation = target.get("sourceRepresentationId")
        concept_row = [fma, representation, expected_name]
        if representation is None or tuple(concept_row) not in concept_rows:
            raise FreezeError(f"official R4 IS-A concept/representation row is not exact for {fma}")
        exact_rows = sorted([list(row) for row in relation_rows if row[0] == fma])
        frozen_members = sorted(member.get("sourceElementFileId") for member in target.get("exactMembers", []))
        actual_members = sorted(row[2] for row in exact_rows)
        if not frozen_members or frozen_members != actual_members:
            raise FreezeError(f"T73 member set and official R4 ELEMENT rows differ for {fma}: {frozen_members} vs {actual_members}")
        target_concepts.append({
            "sourceConceptId": fma,
            "sourceRepresentationId": representation,
            "sourceNameEnglish": expected_name,
            "sourceTree": "IS-A",
            "sourceRepresentationKind": "COMPOUND",
            "sourceSemanticLabel": concept_kind,
            "officialConceptRow": concept_row,
            "officialElementRows": exact_rows,
            "meshInterpretation": "one FJ ELEMENT may be referenced by several COMPOUND concepts; the concept row does not create a separate mesh",
        })
        canonical_membership_lines.append(f"{fma}|{representation}|{expected_name}|{','.join(actual_members)}\n")
        for rel in exact_rows:
            member_concepts.setdefault(rel[2], []).append({"sourceConceptId": fma, "sourceNameEnglish": rel[1], "sourceRepresentationId": representation, "sourceConceptKind": concept_kind})

    all_members = sorted(member_concepts)
    if all_members != EXPECTED_ALL:
        raise FreezeError(f"T73 target FJ union changed: {all_members}")
    if set(all_members) - REUSE != set(sum(NEW_BATCHES.values(), [])) or set(sum(NEW_BATCHES.values(), [])) & REUSE:
        raise FreezeError("T76 new batches and T53 reuse IDs are not an exact partition of the frozen target members")
    if [len(rows) for rows in NEW_BATCHES.values()] != [5, 4] or max(map(len, NEW_BATCHES.values())) > 10:
        raise FreezeError("T76 internal acquisition batches must stay 5 + 4 and at most ten")

    t53 = json.loads(T53_SOURCE.read_text(encoding="utf-8"))
    t53_region = json.loads(T53_REGION.read_text(encoding="utf-8"))
    t70 = json.loads(T70.read_text(encoding="utf-8"))
    t53_assets = {row["sourceElementFileId"]: row for row in t53.get("sourceAssets", [])}
    t70_assets = {row["sourceElementFileId"]: row for row in t70.get("assets", [])}
    cache_dir = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t53"
    reuse_only: list[dict[str, Any]] = []
    for fid in sorted(REUSE):
        path = cache_dir / f"{fid}.obj"
        source_row = t53_assets.get(fid)
        base_row = t70_assets.get(fid)
        if not path.is_file() or source_row is None or base_row is None:
            raise FreezeError(f"T53 raw source/T53 manifest/T70 base is missing reuse member {fid}")
        digest = sha_file(path)
        if source_row.get("sourceSha256") != digest or base_row.get("sourceSha256") != digest:
            raise FreezeError(f"T53/T70 historical hashes differ for reused member {fid}")
        reuse_only.append({"sourceElementFileId": fid, "stableMeshAssetId": source_row["stableMeshAssetId"], "sourceSha256": digest, "bytes": path.stat().st_size, "sourceManifestPath": T53_SOURCE.relative_to(ROOT).as_posix(), "packageAlreadyPresentInT70": True, "mustNotReacquireOrCopy": True})

    new_members: list[dict[str, Any]] = []
    by_fid_matrix = {m["sourceElementFileId"]: m for target in rows for m in target.get("exactMembers", [])}
    for fid in sum(NEW_BATCHES.values(), []):
        side_names = sorted({c["sourceNameEnglish"] for c in member_concepts[fid] if side_from_exact_name(c["sourceNameEnglish"])})
        side_values = sorted({side_from_exact_name(name) for name in side_names})
        if len(side_values) > 1:
            raise FreezeError(f"official target concept labels disagree on laterality for {fid}: {side_names}")
        matrix_member = by_fid_matrix.get(fid)
        if matrix_member is None:
            raise FreezeError(f"T73 has no exact member row for {fid}")
        identity_candidates = sorted({(row[0], row[2]) for row in relation_rows if row[2] == fid})
        target_identity_candidates = sorted({(fma, representation, name) for fma, name, _kind in CONCEPTS for representation in [by_fma[fma].get("sourceRepresentationId")] if any(row[0] == fma and row[2] == fid for row in relation_rows)})
        if not target_identity_candidates or any(tuple(candidate) not in concept_rows for candidate in target_identity_candidates):
            raise FreezeError(f"exact FMA/BP/name representation candidates missing for {fid}")
        exact_relation_rows = sorted([list(row) for row in relation_rows if row[2] == fid and row[0] in expected_concepts])
        new_members.append({
            "sourceElementFileId": fid,
            "sourceConceptMemberships": sorted(member_concepts[fid], key=lambda row: row["sourceConceptId"]),
            "officialTargetRelationRows": exact_relation_rows,
            "officialFmaBpNameCandidates": [list(row) for row in target_identity_candidates],
            "allOfficialIsAIdentityCandidates": [list(row) for row in identity_candidates],
            "lateralityFromExactSideSpecificSourceConcepts": side_values[0] if side_values else None,
            "exactSourceLabelAtFreeze": matrix_member.get("sourceElementName"),
            "frozenMatrixIdentityUnchanged": True,
            "stableMeshAssetId": f"HA-MESH-BP3D4-{fid}",
            "archiveMemberPath": f"isa_BP3D_4.0_obj_99/{fid}.obj",
            "archiveTree": "IS-A",
            "acquisitionStateAtFreeze": "not_yet_attempted",
            "derivedRegionMembershipCandidate": {"regionId": "pelvis-perineum", "stableRenderNodeId": f"HA-MESH-BP3D4-{fid}"},
        })

    # The old pelvis/perineum slice contains two explicit English source-name families;
    # FJ1450 is its single blank-identity hold. Keep it as unresolved context.
    old_region_ids = t53_region.get("sourceElementFileIds", [])
    if len(old_region_ids) != 7 or "FJ1450" not in old_region_ids:
        raise FreezeError("T53 pelvis/perineum historical seven-mesh scope or identity-held FJ1450 changed")
    old_region_assets = [t53_assets[fid] for fid in old_region_ids]
    exact_name_variants = sorted({row.get("sourceName") for row in old_region_assets if row.get("sourceName")})
    named_families = sorted({re.sub(r"^(left|right)\s+", "", name, flags=re.I) for name in exact_name_variants})
    unknown = [row.get("sourceElementFileId") for row in old_region_assets if row.get("sourceIdentityState") == "header_identity_blank_context_only"]
    if len(named_families) != 2 or unknown != ["FJ1450"]:
        raise FreezeError(f"T53 historical pelvis source names/identity hold changed: {named_families} / {unknown}")

    bone_context = []
    for fid in ["FJ3152", "FJ3288"]:
        row = next((r for r in t53.get("sourceAssets", []) if r.get("sourceElementFileId") == fid), None)
        base_row = t70_assets.get(fid)
        raw_path = ROOT / f"atlas-data/source-cache/bodyparts3d-r4/mesh/t53/{fid}.obj"
        if row is None or base_row is None or not raw_path.is_file() or sha_file(raw_path) != row.get("sourceSha256"):
            raise FreezeError(f"exact existing T53 same-frame hip-bone context is incomplete for {fid}")
        bone_context.append({
            "sourceElementFileId": fid,
            "sourceConceptId": row.get("sourceConceptId"),
            "sourceRepresentationId": row.get("sourceRepresentationId"),
            "sourceName": row.get("sourceName"),
            "exactSourceSide": row.get("lateralityFromExactSourceHeader"),
            "stableMeshAssetId": row.get("stableMeshAssetId"),
            "sourceSha256": row.get("sourceSha256"),
            "topologySha256": row.get("topologyContentSha256"),
            "positionSha256": row.get("positionContentSha256"),
            "sameFrameAndPose": row.get("projectFrame") == t53["source"]["projectFrame"] and row.get("sourcePose") == t53["source"]["pose"],
            "existingProductRegion": "gluteal-hip",
            "relationship": "same-frame bony-pelvis context only; no perineal attachment/containment claim",
            "alreadyInT70": True,
        })
    if {row["sourceElementFileId"] for row in bone_context} != {"FJ3152", "FJ3288"} or any(not row["sameFrameAndPose"] for row in bone_context):
        raise FreezeError("existing hip-bone context IDs/frame/pose are not exact")

    input_paths = [MATRIX, COVERAGE, *(META / filename for filename in META_FILES), T53_SOURCE, T53_REGION, T70,
                   ROOT / "work/evidence/T50/scene-contract.md",
                   ROOT / "atlas-data/manifests/bodyparts3d-r4-t74/source-manifest.json", ROOT / "atlas-data/manifests/bodyparts3d-r4-t74/integration-extension.json",
                   ROOT / "atlas-data/manifests/bodyparts3d-r4-t75/source-manifest.json", ROOT / "atlas-data/manifests/bodyparts3d-r4-t75/integration-extension.json"]
    input_hashes = {p.relative_to(ROOT).as_posix(): sha_file(p) for p in input_paths}
    t53_glb_path = ROOT / t53["sceneContract"]["integratedGlbLocalCachePath"]
    if sha_file(t53_glb_path) != t53["sceneContract"]["integratedGlbSha256"]:
        raise FreezeError("historical T53 shared trunk/pelvis GLB no longer matches its source manifest")

    frozen = {
        "revision": "BodyParts3D-R4-T76-FROZEN-PELVIC-FLOOR-SOURCE-SET-v1",
        "task": "T76",
        "status": "frozen_before_mesh_acquisition",
        "sourceVersion": "BodyParts3D Release 4.0 (2013-05-16)",
        "archiveTree": "IS-A",
        "archiveUrl": ARCHIVE_URL,
        "sourceConceptCount": 10,
        "targetUniqueElementCount": 12,
        "sourceConcepts": target_concepts,
        "targetElementFileIds": EXPECTED_ALL,
        "targetConceptMembershipSha256": sha("".join(canonical_membership_lines).encode("utf-8")),
        "uniqueNewSourceAssets": new_members,
        "newSourceElementFileIds": [row["sourceElementFileId"] for row in new_members],
        "reuseOnly": reuse_only,
        "internalBatches": [{"batchId": key, "sourceElementFileIds": value, "count": len(value)} for key, value in NEW_BATCHES.items()],
        "existingPelvisPerineumReference": {
            "historicalPackage": "T53",
            "sourceElementFileIds": old_region_ids,
            "distinctEnglishNameFamiliesObserved": named_families,
            "exactSourceNameVariantsObserved": exact_name_variants,
            "existingIdentityHold": {"sourceElementFileId": "FJ1450", "sourceIdentityState": "header_identity_blank_context_only", "action": "preserve_unknown_identity_and_context_only"},
            "thisIsNotAWholeRegionDenominator": True,
        },
        "relatedExistingBoneContext": bone_context,
        "sourceRepresentationInterpretation": {
            "zoneConcept": "FMA19089 zone of levator ani is a COMPOUND zone/group concept mapped to nine atomic FJ ELEMENT rows; it is not a tenth geometry surface or a separately named muscle.",
            "namedMuscleConcepts": ["FMA19090 pubococcygeus", "FMA19092 iliococcygeus", "FMA19088 coccygeus"],
            "sideSpecificConcepts": ["FMA45854", "FMA45855", "FMA45858", "FMA45859", "FMA46443", "FMA46444"],
            "meshRule": "one node per unique FJ; multiple IS-A concept rows reuse that same source member; no inferred part/branch or surface split",
            "unrepresented": "No extra perineal muscle or part distinction is invented beyond the frozen source concepts and ELEMENT rows.",
        },
        "frozenInputSha256": input_hashes,
        "policy": {
            "sideOnlyFromExactSourceConceptOrHeader": True,
            "neverInferFromFjSuffixOrCoordinates": True,
            "noMirrorOrRecenter": True,
            "reuseT53BytesWithoutReplacementOrCopy": True,
            "relatedBoneContextIsReferenceOnly": True,
            "noCanonicalLearnerBindingOrPolicyChange": True,
            "learnerDefaultVisibilityNotChanged": True,
            "humanAnatomyReview": "not_performed",
            "redistribution": "held_pending_file_level_reconciliation_of_current_CC_BY_4.0_terms_and_legacy_per_OBJ_CC_BY_SA_2.1_Japan_header",
            "wholeBodyCanonicalDenominator": None,
            "scope": "T73's bounded ten-concept pelvic-floor/perineum sample; not full perineal or whole-body coverage",
        },
    }
    write_json(OUT, frozen)
    return frozen


if __name__ == "__main__":
    try:
        print(json.dumps(generate(), ensure_ascii=False, indent=2))
    except Exception as exc:
        print(f"T76 freeze failed closed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
