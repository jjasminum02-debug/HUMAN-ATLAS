#!/usr/bin/env python3
"""Build T70 source-scope and integration contracts without changing historical packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "atlas-data/tools"))
import ingest_bodyparts3d_r4 as source  # noqa: E402 - pinned T51 parser, read only

BASE = Path("atlas-data/manifests/bodyparts3d-r4-t70")
POLICY = BASE / "product-minimum-policy.json"
SCOPE = BASE / "scope-inventory.json"
INTEGRATION = BASE / "integration-manifest.json"
T51 = Path("atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json")
PACKAGES = {
    "T52": Path("atlas-data/manifests/bodyparts3d-r4-t52/head-neck.json"),
    "T53": Path("atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json"),
    "T54": Path("atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json"),
    "T55": Path("atlas-data/manifests/bodyparts3d-r4-t55/source-manifest.json"),
}
T69 = Path("work/evidence/T69/diagnostic.json")
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
EXPECTED_LATERALITY_HOLDS = {"FJ2742", "FJ2754", "FJ1469", "FJ1469M"}
EXPECTED_IDENTITY_HOLDS = {"FJ1450", "FJ1451", "FJ1454", "FJ1455", "FJ1525", "FJ1543", "FJ1547", "FJ1548"}


class ContractError(ValueError):
    pass


def load(path: Path) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def encoded(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def exact_source_indexes(tables: dict[str, list[list[str]]]) -> tuple[dict[str, list[dict[str, str]]], dict[str, str]]:
    contexts: dict[str, list[dict[str, str]]] = defaultdict(list)
    names: dict[str, str] = {}
    for tree, concept_key, element_key in (
        ("IS-A", "isaConcepts", "isaCompoundElements"),
        ("PART-OF", "partofConcepts", "partofCompoundElements"),
    ):
        for fma, _bp, name in tables[concept_key]:
            if fma in names and names[fma] != name:
                raise ContractError(f"inconsistent official concept name for {fma}")
            names[fma] = name
        for fma, name, file_id in tables[element_key]:
            contexts[file_id].append({"tree": tree, "sourceFmaConceptId": fma, "sourceName": name})
    return contexts, names


def package_frame_pose(task: str, package: dict[str, Any], row: dict[str, Any]) -> tuple[str, str]:
    if task == "T52":
        frame_pose = row["framePose"]
        return frame_pose["projectFrame"], frame_pose["poseId"]
    return row["projectFrame"], row["sourcePose"]


def source_chunks(task: str, package: dict[str, Any]) -> list[dict[str, Any]]:
    if task == "T52":
        return [{"chunkId": batch["batchId"], "path": batch["glbPath"], "sha256": batch["glbSha256"], "sourceElementFileIds": batch["sourceElementFileIds"]} for batch in package["internalBatches"]]
    scene = package["sceneContract"]
    path_key = "integratedGlbLocalCachePath" if task == "T53" else "qaGlbPath"
    hash_key = "integratedGlbSha256" if task == "T53" else "qaGlbSha256"
    return [{"chunkId": task, "path": scene[path_key], "sha256": scene[hash_key], "sourceElementFileIds": [r["sourceElementFileId"] for r in package["sourceAssets"]]}]


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    policy = load(POLICY)
    t51 = load(T51)
    packages = {task: load(path) for task, path in PACKAGES.items()}
    t69 = load(T69)
    metadata_hashes = {row["path"]: digest(Path(row["path"])) for row in t51["source"]["metadataFiles"]}
    if len(metadata_hashes) != 6 or any(metadata_hashes[row["path"]] != row["sha256"] for row in t51["source"]["metadataFiles"]):
        raise ContractError("official metadata differs from the pinned T51 source bytes")
    tables = source.load_tables(ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata")
    contexts, names = exact_source_indexes(tables)
    isa_edges = source.adjacency(tables["isaInclusion"])
    bone_concepts = source.closure(["FMA5018"], isa_edges)
    muscle_concepts = source.closure(["FMA5022"], isa_edges)
    bone_source_ids = {fj for fj, rows in contexts.items() if any(r["sourceFmaConceptId"] in bone_concepts for r in rows)}
    muscle_source_ids = {fj for fj, rows in contexts.items() if any(r["sourceFmaConceptId"] in muscle_concepts for r in rows)}
    _routes, muscle_regions, bone_regions = source.region_map(ROOT, tables)
    routed_bone_ids = set().union(*bone_regions.values())
    routed_muscle_ids = set().union(*muscle_regions.values())
    if len(bone_source_ids) != 203 or len(routed_bone_ids) != 168 or len(muscle_source_ids) != 323:
        raise ContractError("official metadata changed; re-audit source closure and product targets")

    package_rows: dict[str, dict[str, Any]] = {}
    package_references: dict[str, list[dict[str, Any]]] = defaultdict(list)
    region_refs: dict[str, set[str]] = defaultdict(set)
    learner_refs: dict[str, set[str]] = defaultdict(set)
    chunks: list[dict[str, Any]] = []
    package_counts: dict[str, int] = {}
    for task in ("T52", "T53", "T54", "T55"):
        package = packages[task]
        rows = package["sourceAssets"]
        package_counts[task] = len(rows)
        if task != "T52" and (package["source"]["sourceId"] != "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0" or package["source"]["projectFrame"] != FRAME or package["source"]["pose"] != POSE):
            raise ContractError(f"{task} package source/frame/pose differs")
        for row in rows:
            fj = row["sourceElementFileId"]
            frame, pose = package_frame_pose(task, package, row)
            if (frame, pose) != (FRAME, POSE):
                raise ContractError(f"{task}/{fj} has off-scene frame or pose")
            node = row.get("stableSourceMeshNodeId") or row.get("stableMeshAssetId")
            if node != f"HA-MESH-BP3D4-{fj}" or fj not in contexts:
                raise ContractError(f"{task}/{fj} has invalid stable source node or lacks official ELEMENT relation")
            old = package_rows.get(fj)
            if old and (old["sourceSha256"] != row["sourceSha256"] or old["nodeId"] != node):
                raise ContractError(f"overlapping package geometry/ID mismatch: {fj}")
            if not old:
                package_rows[fj] = {"sourceSha256": row["sourceSha256"], "nodeId": node, "sourceName": row.get("sourceName"), "sourceConceptId": row.get("sourceConceptId")}
            region_refs[fj].update(row.get("regionIds") or row.get("regionMemberships") or [])
            learner_refs[fj].update(row.get("canonicalLearnerIds") or ([row["existingLearnerStableId"]] if row.get("existingLearnerStableId") else []))
            package_references[fj].append({"package": task, "sourceSha256": row["sourceSha256"]})
        for chunk in source_chunks(task, package):
            chunk_ids = set(chunk["sourceElementFileIds"])
            if len(chunk_ids) != len(chunk["sourceElementFileIds"]):
                raise ContractError(f"duplicate source ID inside {chunk['chunkId']}")
            chunks.append({"chunkId": chunk["chunkId"], "package": task, "localQaGlbPath": chunk["path"], "glbSha256": chunk["sha256"], "sourceElementFileIds": sorted(chunk_ids)})
    package_ids = set(package_rows)
    if package_counts != {"T52": 85, "T53": 138, "T54": 142, "T55": 130} or len(package_ids) != 493:
        raise ContractError("historical package count or deduplicated source set changed")

    t69_holds = {r["sourceLabel"]["sourceElementFileId"] for r in t69["diagnostics"] if r["aiConclusion"]["code"] == "opposite_side_reciprocal_pair_conflict" and r["learnerUse"]["status"] == "source_only_held"}
    t54_holds = {r["sourceElementFileId"] for r in packages["T54"]["sourceAssets"] if r["lateralitySurfaceDiagnostic"].get("boundsWhollyOppositeToSourceLabel")}
    t53_identity_holds = {r["sourceElementFileId"] for r in packages["T53"]["sourceAssets"] if r["sourceIdentityState"] != "header_identity_validated_against_release_metadata"}
    if t69_holds != {"FJ2742", "FJ2754"} or t54_holds != {"FJ1469", "FJ1469M"} or t53_identity_holds != EXPECTED_IDENTITY_HOLDS:
        raise ContractError("a T69/T54 laterality or T53 identity hold was lost or changed")
    if t69["globalFrameVerification"]["status"] != "technically_consistent":
        raise ContractError("T69 shared frame is not technically consistent")

    integration_rows = []
    for fj in sorted(package_ids):
        row = package_rows[fj]
        reasons = []
        if fj in t69_holds:
            reasons.append("T69_source_label_surface_pair_conflict")
        if fj in t54_holds:
            reasons.append("T54_source_label_surface_pair_conflict")
        if fj in t53_identity_holds:
            reasons.append("T53_blank_OBJ_identity_header")
        if fj in t53_identity_holds and (row["sourceName"] is not None or row["sourceConceptId"] is not None):
            raise ContractError(f"unresolved T53 header identity was silently filled: {fj}")
        refs = package_references[fj]
        integration_rows.append({
            "sourceElementFileId": fj,
            "renderNodeId": row["nodeId"],
            "sourceSha256": row["sourceSha256"],
            "sourceNameObservation": row["sourceName"],
            "sourceConceptIdObservation": row["sourceConceptId"],
            "sourceClassCandidates": [kind for kind, source_ids in (("bone_root_closure", bone_source_ids), ("muscle_organ_root_closure", muscle_source_ids)) if fj in source_ids],
            "productRegionIdsFromHistoricalPackages": sorted(region_refs[fj]),
            "existingLearnerStableIds": sorted(learner_refs[fj]),
            "primaryPackage": refs[0]["package"],
            "packageReferences": refs,
            "holdReasons": reasons,
            "localQaRender": "available_source_surface",
            "learnerPickState": "held" if reasons else ("existing_binding_unreviewed" if learner_refs[fj] else "source_only_unbound"),
            "learnerDefaultVisible": not bool(reasons),
            "humanAnatomyReviewed": False,
        })
    primary = {r["sourceElementFileId"]: r["primaryPackage"] for r in integration_rows}
    for chunk in chunks:
        chunk["suppressDuplicateSourceElementFileIds"] = [fj for fj in chunk["sourceElementFileIds"] if primary[fj] != chunk["package"]]
    if {fj for c in chunks for fj in c["suppressDuplicateSourceElementFileIds"]} != {"FJ3237", "FJ3279"}:
        raise ContractError("shared T53/T54 nodes were not deduplicated exactly once")

    missing_bone_ids = bone_source_ids - package_ids
    if len(missing_bone_ids) != 35 or bone_source_ids & package_ids != routed_bone_ids:
        raise ContractError("bone closure versus regional package gap is not the audited 35 source IDs")
    bone_missing_rows = [{"sourceElementFileId": fj, "sourceContextsInBoneRoot": [r for r in contexts[fj] if r["sourceFmaConceptId"] in bone_concepts], "acquisitionState": "not_in_T52_T55_packages", "productMinimumRequired": False} for fj in sorted(missing_bone_ids)]
    targets = []
    target_ids: set[str] = set()
    for target in policy["conceptTargets"]:
        fma = target["sourceFmaConceptId"]
        exact = {fj for fj, rows in contexts.items() if any(r["sourceFmaConceptId"] == fma for r in rows)}
        expected = set(target["expectedElementFileIds"])
        if exact != expected or target_ids & exact:
            raise ContractError(f"product target elements differ from exact official compound rows: {fma}")
        edge_key = "isaInclusion" if target["requiredSourceRelationTree"] == "IS-A" else "partofInclusion"
        parent = target["requiredSourceParentId"]
        if not any(r[0] == parent and r[2] == fma for r in tables[edge_key]):
            raise ContractError(f"required official source parent/part relation absent: {parent} -> {fma}")
        target_ids |= exact
        targets.append({"sourceFmaConceptId": fma, "sourcePreferredNameEnglish": names[fma], "sourceRelation": {"tree": target["requiredSourceRelationTree"], "parentConceptId": parent}, "sourceClassification": [kind for kind, values in (("bone_root_closure", bone_concepts), ("muscle_organ_root_closure", muscle_concepts)) if fma in values] or ["outside_bone_and_muscle_organ_roots"], "sourceElementFileIds": sorted(exact), "productDecision": {"role": target["productRole"], "regionId": target["productRegionId"], "status": "first_pass_visual_candidate_not_canonical_identity_or_anatomy_approval"}, "alreadyInHistoricalPackages": sorted(exact & package_ids)})
    if len(target_ids) != 20 or target_ids & package_ids:
        raise ContractError("first-pass minimum source delta changed; inspect historical packages and policy")
    batch = policy["nextAcquisitionBatch"]
    batch_ids = set(batch["sourceElementFileIds"])
    if batch["taskId"] != "T71" or not batch_ids <= target_ids or len(batch_ids) > batch["maxSourceElements"] or len(batch_ids) != 9:
        raise ContractError("T71 acquisition batch must be nine exact missing first-pass targets")
    for row in bone_missing_rows:
        row["productMinimumRequired"] = row["sourceElementFileId"] in target_ids

    input_hashes = {str(path): digest(path) for path in (POLICY, T51, T69, *PACKAGES.values())}
    input_hashes.update(metadata_hashes)
    scope = {
        "revision": "BodyParts3D-R4-T70-source-scope-v1",
        "inputSha256": input_hashes,
        "sourceTaxonomy": {"boneOrganRootFmaId": "FMA5018", "boneClosureUniqueElementFileCount": len(bone_source_ids), "boneRegionAssignedUniqueElementFileCount": len(routed_bone_ids), "boneClosureAbsentFromHistoricalPackages": len(missing_bone_ids), "muscleOrganRootFmaId": "FMA5022", "muscleClosureUniqueElementFileCount": len(muscle_source_ids), "muscleRegionAssignedUniqueElementFileCount": len(routed_muscle_ids), "exactElementTrees": ["IS-A", "PART-OF"], "sourceFjCountIsNotCanonicalIndividualMuscleDenominator": True},
        "historicalPackages": {"tasks": package_counts, "uniqueSourceElementFileCount": len(package_ids), "boundExistingLearnerIdSourceMeshCount": sum(bool(v) for v in learner_refs.values())},
        "boneClosureMissingSourceElements": bone_missing_rows,
        "productFirstPassMinimum": {"policyRevision": policy["revision"], "meaning": policy["meaning"], "conceptTargets": targets, "sourceElementFileIds": sorted(target_ids), "sourceElementFileCount": len(target_ids), "alreadyAcquiredInHistoricalPackages": 0, "remainingAfterT71Batch": sorted(target_ids - batch_ids), "canonicalWholeBodyIndividualMuscleDenominator": None},
        "nextAcquisitionBatch": batch,
        "publicRedistribution": "held_pending_file_level_license_reconciliation",
    }
    integration = {
        "revision": "BodyParts3D-R4-T70-minimal-integration-v1",
        "inputSha256": input_hashes,
        "scopeInventorySha256": hashlib.sha256(encoded(scope)).hexdigest(),
        "sceneContract": {"sourceId": "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0", "projectFrame": FRAME, "sourceUnit": "mm_from_source_OBJ", "projectUnit": "m", "transform": "[x,y,z]mm -> [x,z,-y]m", "pose": POSE, "oneAnatomySceneRoot": True, "singleSourceRevisionOnly": True, "T69SharedFrameTechnicalState": "technically_consistent", "sourceLodLevelsAvailable": 1, "highLodAvailable": False, "productSceneImplemented": False},
        "localQaChunks": chunks,
        "assets": integration_rows,
        "counts": {"historicalPackageMemberships": sum(package_counts.values()), "uniqueSourceNodes": len(integration_rows), "sharedNodeSuppressionCount": sum(len(c["suppressDuplicateSourceElementFileIds"]) for c in chunks), "existingLearnerBindingSourceMeshes": sum(bool(v) for v in learner_refs.values()), "sourceOnlyUnbound": sum(r["learnerPickState"] == "source_only_unbound" for r in integration_rows), "lateralityHeld": len(EXPECTED_LATERALITY_HOLDS), "identityHeaderHeld": len(EXPECTED_IDENTITY_HOLDS)},
        "holdPolicy": {"T69LateralitySourceElementFileIds": sorted(t69_holds), "T54LateralitySourceElementFileIds": sorted(t54_holds), "T53IdentityHeaderSourceElementFileIds": sorted(t53_identity_holds), "affectedNodesKeepOriginalGeometryAndSourceIds": True, "heldNodesDefaultLearnerVisible": False, "heldNodesLearnerPickable": False, "unboundNodesLearnerCardAllowed": False, "allStructuresRequireHumanReviewBeforeIndependentLocalEngineering": False, "existingBindingsAreNotPromotedToHumanReviewed": True},
        "publicRedistribution": "held_pending_file_level_license_reconciliation",
        "notAProductBundleOrLearnerNameCatalog": True,
    }
    validate(scope, integration, package_ids, target_ids)
    return scope, integration


def validate(scope: dict[str, Any], integration: dict[str, Any], package_ids: set[str] | None = None, target_ids: set[str] | None = None) -> None:
    rows = integration["assets"]
    ids = [r["sourceElementFileId"] for r in rows]
    if len(ids) != 493 or len(set(ids)) != 493 or (package_ids is not None and set(ids) != package_ids):
        raise ContractError("integration must contain exactly one row for every historical source mesh")
    if len({r["renderNodeId"] for r in rows}) != len(rows):
        raise ContractError("duplicate render node ID")
    holds = {r["sourceElementFileId"] for r in rows if r["learnerPickState"] == "held"}
    if holds != EXPECTED_LATERALITY_HOLDS | EXPECTED_IDENTITY_HOLDS:
        raise ContractError("laterality/identity holds missing or unexpectedly expanded")
    for row in rows:
        if row["holdReasons"] and (row["learnerPickState"] != "held" or row["learnerDefaultVisible"]):
            raise ContractError(f"held source mesh became learner visible or selectable: {row['sourceElementFileId']}")
        if not row["existingLearnerStableIds"] and row["learnerPickState"] == "existing_binding_unreviewed":
            raise ContractError("unbound source mesh was promoted to a learner binding")
    chunks = integration["localQaChunks"]
    rendered = [fj for c in chunks for fj in c["sourceElementFileIds"] if fj not in c["suppressDuplicateSourceElementFileIds"]]
    if len(rendered) != 493 or set(rendered) != set(ids):
        raise ContractError("chunk deduplication lost or duplicated a source mesh")
    first_pass = set(scope["productFirstPassMinimum"]["sourceElementFileIds"])
    if len(first_pass) != 20 or (target_ids is not None and first_pass != target_ids):
        raise ContractError("first-pass product target list changed")
    if scope["sourceTaxonomy"]["boneClosureUniqueElementFileCount"] != 203 or scope["sourceTaxonomy"]["boneRegionAssignedUniqueElementFileCount"] != 168 or len(scope["boneClosureMissingSourceElements"]) != 35:
        raise ContractError("bone source/region/missing denominators have been conflated")
    if integration["holdPolicy"]["heldNodesLearnerPickable"] or integration["sceneContract"]["highLodAvailable"]:
        raise ContractError("unverified held selection or non-existent high LOD was enabled")


def verify_local_source_obj() -> int:
    verified = 0
    for task, package_path in PACKAGES.items():
        for row in load(package_path)["sourceAssets"]:
            fj = row["sourceElementFileId"]
            path = Path(row["cachePath"]) if task == "T52" else Path(f"atlas-data/source-cache/bodyparts3d-r4/mesh/{task.lower()}/{fj}.obj")
            if digest(path) != row["sourceSha256"]:
                raise ContractError(f"local source OBJ differs from {task} frozen source hash: {fj}")
            verified += 1
    return verified


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the new immutable T70 revision")
    mode.add_argument("--check", action="store_true", help="recompute and compare with the written revision")
    parser.add_argument("--verify-local-glb", action="store_true", help="also hash cached QA GLBs if present")
    parser.add_argument("--verify-local-source-obj", action="store_true", help="also hash cached OBJ bytes against frozen package manifests")
    args = parser.parse_args()
    try:
        scope, integration = build()
        for path, document in ((SCOPE, scope), (INTEGRATION, integration)):
            content = encoded(document)
            output = ROOT / path
            if args.write:
                if output.exists() and output.read_bytes() != content:
                    raise ContractError(f"refusing to overwrite existing T70 revision with changed content: {path}")
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(content)
            elif not output.exists() or output.read_bytes() != content:
                raise ContractError(f"written T70 revision is missing or stale: {path}")
        if args.verify_local_glb:
            for chunk in integration["localQaChunks"]:
                if digest(Path(chunk["localQaGlbPath"])) != chunk["glbSha256"]:
                    raise ContractError(f"local QA GLB hash differs: {chunk['chunkId']}")
        verified_source_obj = verify_local_source_obj() if args.verify_local_source_obj else 0
    except (ContractError, OSError, KeyError, ValueError) as exc:
        print(f"T70 scope/integration validation failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"boneSource": 203, "boneRegionAssigned": 168, "boneMissing": 35, "firstPassTargetMissing": scope["productFirstPassMinimum"]["sourceElementFileCount"], "integratedSourceMeshes": integration["counts"]["uniqueSourceNodes"], "lateralityHeld": integration["counts"]["lateralityHeld"], "identityHeld": integration["counts"]["identityHeaderHeld"], "localSourceObjVerified": verified_source_obj, "nextBatch": scope["nextAcquisitionBatch"]["taskId"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
