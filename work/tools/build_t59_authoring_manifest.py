#!/usr/bin/env python3
"""Build the T59-owned, manifest-gated whole-muscle authoring handoff."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PLAN_DIR = Path("work/evidence/motion-all-muscles-plan-2026-10-02")
EVIDENCE_DIR = Path("work/evidence/T59")
BASELINE_PATH = EVIDENCE_DIR / "start-baseline.json"
R2_PATH = PLAN_DIR / "run-manifest-r2.json"
R1_PATH = PLAN_DIR / "run-manifest.json"
TARGET_PATH = Path("work/evidence/T35/motion-readiness-ledger.json")
CONTRACT_PATH = Path("work/evidence/T35/motion-contract.json")
RECONCILIATION_PATH = Path("work/evidence/T35/manifest-reconciliation.json")
TARGET_SCOPE_PATH = Path("atlas-data/catalog/target-scope-t96.json")
COMPILED_PATH = Path("atlas-data/source-cache/datasets/za/compiled/manifest.json")
WORKER_PATHS = {
    "A": PLAN_DIR / "research-a/proposals.json",
    "B": PLAN_DIR / "research-b/proposals.json",
    "C": PLAN_DIR / "research-c/proposals.json",
}
MANIFEST_OUT = EVIDENCE_DIR / "authoring-run-manifest.json"
RECON_OUT = EVIDENCE_DIR / "worker-reconciliation.json"
AUTHORING_RUN_ID = "T59-authoring-handoff-2026-10-02-r1"
AUTHORING_NEXT_UNIT = "await-source-derived-candidate-packages"
CONTRACT_FILES = {
    "t59-source-motion-exporter": Path("work/tools/derive_source_surface_motion.py"),
    "t59-authoring-manifest-builder": Path("work/tools/build_t59_authoring_manifest.py"),
    "t59-authoring-manifest-validator": Path("work/tools/validate_t59_authoring_manifest.py"),
    "motion-learning-schema": Path("atlas-data/schemas/motion-learning.schema.json"),
    "motion-learning-validator": Path("atlas-data/schemas/validate_motion_learning.py"),
    "motion-domain-binding-contract": Path("atlas-web/src/domain/motionLearning.ts"),
    "animation-scene-adapter": Path("atlas-web/src/viewer/animationSceneAdapter.ts"),
    "shared-animation-clock-player": Path("atlas-web/src/viewer/animationPlayback.ts"),
    "dataset-scene-motion-host": Path("atlas-web/src/viewer/datasets/DatasetSceneAdapter.ts"),
    "source-motion-host-interface": Path("atlas-web/src/viewer/datasets/sourceMotionHost.ts"),
    "source-motion-geometry-hash": Path("atlas-web/src/viewer/datasets/sourceMotionGeometry.ts"),
    "motion-learner-panel": Path("atlas-web/src/ui/MotionLearningPanel.tsx"),
    "learner-safe-motion-runtime-builder": Path("atlas-web/scripts/buildLearnerMotionRuntime.mjs"),
    "learner-motion-action-link": Path("atlas-web/src/data/learning.ts"),
    "whole-body-motion-host-bridge": Path("atlas-web/src/viewer/wholeBody/WholeBodyViewer.tsx"),
}


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def value_sha(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def read(path: Path) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def owner_map(assignments: dict[str, dict[str, Any]], field: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for worker, assignment in assignments.items():
        for value in assignment[field]:
            if value in result:
                raise ValueError(f"duplicate {field} assignment: {value}")
            result[value] = worker
    return result


def row_source_keys(row: dict[str, Any]) -> list[str]:
    for key in ("sourceKeys", "assignedSourceKeys", "source_keys"):
        value = row.get(key)
        if isinstance(value, list):
            return sorted(set(str(item) for item in value))
    return []


def field_category(name: str) -> tuple[str, str]:
    key = name.lower().replace("_", "")
    if any(token in key for token in ("identity", "scope", "laterality", "side", "term", "relation", "target")):
        return "identity_scope_side", "revalidated against unchanged frozen assignments/snapshots; proposal remains observation-only"
    if any(token in key for token in ("origin", "insertion", "attachment", "action", "posture", "pose", "movement", "function", "condition")):
        return "attachment_action_pose", "refresh required because the fixed learner-card runtime projection changed in r2"
    if any(token in key for token in ("geometry", "rig", "deformation", "mesh", "surface")):
        return "geometry_rig", "candidate observation only; no native bind/rest pose or deformation authority is inferred"
    if any(token in key for token in ("right", "review", "license", "licence", "public")):
        return "rights_review", "held/not_performed states remain independent; proposal cannot promote either"
    if any(token in key for token in ("missing", "next", "dependency", "decision", "acceptance")):
        return "gap_and_next_action", "retained as a task lead only; no production readiness inferred"
    return "historical_note", "preserved in original proposal file; not adopted into production"


def build_worker_reconciliation(r2: dict[str, Any], manifest_hash: str) -> dict[str, Any]:
    rows_out: list[dict[str, Any]] = []
    worker_summary: dict[str, Any] = {}
    expected_run = r2["runId"]
    for worker, relpath in WORKER_PATHS.items():
        proposal = read(relpath)
        if worker == "A":
            recorded_run = proposal.get("header", {}).get("runId")
            recorded_worker = proposal.get("header", {}).get("assignment")
            proposal_hashes = proposal.get("header", {}).get("inputHashes", {})
            target_rows, source_rows = proposal.get("targetRows", []), proposal.get("sourceRows", [])
        else:
            recorded_run = proposal.get("runId")
            recorded_worker = proposal.get("assignment")
            proposal_hashes = proposal.get("inputHashes", {})
            target_rows, source_rows = proposal.get("targetRows", []), proposal.get("sourceRows", [])
        if recorded_worker != worker:
            raise ValueError(f"{worker} proposal identifies a different owner")
        assigned = r2["assignments"][worker]
        target_ids = sorted(row.get("targetId") for row in target_rows)
        concept_ids = sorted(row.get("sourceConceptKey") for row in source_rows)
        proposal_source_keys = sorted({key for row in source_rows for key in row_source_keys(row)})
        if target_ids != sorted(assigned["assignedTargetIds"]):
            raise ValueError(f"{worker} target proposal IDs differ from the fixed assignment")
        if concept_ids != sorted(assigned["assignedSourceConceptKeys"]):
            raise ValueError(f"{worker} source concept proposal IDs differ from the fixed assignment")
        if proposal_source_keys != sorted(assigned["assignedSourceKeys"]):
            raise ValueError(f"{worker} source key proposal set differs from the fixed assignment")
        stale_paths = sorted(path for path, digest in proposal_hashes.items() if r2["inputHashes"].get(path) != digest)
        row_count = 0
        for row_kind, proposal_rows in (("target", target_rows), ("source_concept", source_rows)):
            for index, row in enumerate(proposal_rows):
                raw_keys = sorted(row.keys())
                field_dispositions = []
                for field in raw_keys:
                    category, disposition = field_category(field)
                    field_dispositions.append({"field": field, "category": category, "disposition": disposition})
                rows_out.append({
                    "worker": worker,
                    "proposalPath": relpath.as_posix(),
                    "rowKind": row_kind,
                    "rowIndex": index,
                    "rowId": row.get("targetId") or row.get("sourceConceptKey"),
                    "rawRowCanonicalJsonSha256": value_sha(row),
                    "proposalFieldNames": raw_keys,
                    "sourceKeysReferenced": row_source_keys(row),
                    "fieldDispositions": field_dispositions,
                })
                row_count += 1
        support_artifacts = []
        for key, value in proposal.items():
            if not key.lower().endswith("path") or not isinstance(value, str):
                continue
            local_path = Path(value)
            if not local_path.is_absolute() and (ROOT / local_path).is_file():
                support_artifacts.append({"kind": key, "path": value, "sha256": sha256(ROOT / local_path)})
        external_sources = proposal.get("externalSources", [])
        for source in external_sources if isinstance(external_sources, list) else []:
            support_artifacts.append({
                "kind": "external_source_reference",
                "evidenceId": source.get("evidenceId"),
                "url": source.get("url"),
                "title": source.get("title"),
                "version": source.get("version"),
                "accessedOn": source.get("accessedOn"),
                "locator": source.get("locator"),
                "sourcePageBytesSha256": source.get("sourcePageBytesSha256"),
                "verificationMethod": source.get("verificationMethod"),
                "limitation": source.get("limitation"),
                "rawReferenceCanonicalJsonSha256": value_sha(source),
            })
        worker_summary[worker] = {
            "proposalPath": relpath.as_posix(),
            "proposalSha256": sha256(ROOT / relpath),
            "recordedRunId": recorded_run,
            "expectedRunId": expected_run,
            "recordedStatus": proposal.get("status") or proposal.get("freshness", {}).get("status"),
            "stale": recorded_run != expected_run or bool(stale_paths),
            "staleInputPaths": stale_paths,
            "targetRowCount": len(target_rows),
            "sourceConceptRowCount": len(source_rows),
            "assignedSourceKeyCount": len(proposal_source_keys),
            "assignmentSourcePath": r2["assignments"][worker]["outputDirectory"],
            "supportArtifacts": support_artifacts,
            "originalProposalUnmodified": True,
            "fullResearchIntegrated": False,
            "fieldDisposition": "raw row hashes and per-field stale/hold explanations only; no worker claim is promoted",
        }
        if row_count != len(target_rows) + len(source_rows):
            raise ValueError(f"proposal row normalization count mismatch for {worker}")
    return {
        "schemaVersion": "t59-worker-reconciliation-v1",
        "task": "T59",
        "manifestRunId": expected_run,
        "currentManifestSha256": manifest_hash,
        "sourceRunId": read(R1_PATH)["runId"],
        "r1ToR2": {
            "assignmentsUnchanged": True,
            "snapshotsUnchanged": True,
            "learnerCardRuntimeProjectionChanged": True,
            "policy": "keep original r1 headers, stale flags, files, and manifest immutable; reuse only data independently reproduced from current frozen inputs",
        },
        "workers": worker_summary,
        "normalizedProposalRows": rows_out,
        "normalizationPolicy": {
            "sourceIdentity": "source/target keys and side are copied only from current r2 frozen target/source snapshots; proposal rows remain historical observations",
            "attachmentActionPose": "r1 statements affected by the learner-card projection change are not accepted; refresh against current authoring snapshot",
            "rightsAndHumanReview": "source-only, local/public rights hold, and humanReview=not_performed remain independent",
            "targetIdentity": "no lexical/parent/member claim is promoted to exact target identity by this reconciliation",
        },
    }


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    r2 = read(R2_PATH)
    r1 = read(R1_PATH)
    ledger = read(TARGET_PATH)
    contract = read(CONTRACT_PATH)
    reconciliation = read(RECONCILIATION_PATH)
    scope = read(TARGET_SCOPE_PATH)
    compiled = read(COMPILED_PATH)
    baseline = read(BASELINE_PATH)
    if baseline.get("baselineHead") is None or baseline.get("dirtyPathCount") != len(baseline.get("dirtyPaths", [])):
        raise ValueError("T59 start baseline evidence is missing or internally inconsistent")
    frozen = {}
    for relpath, expected in r2["inputHashes"].items():
        actual = sha256(ROOT / Path(relpath))
        if actual != expected:
            raise ValueError(f"r2 input drift: {relpath}: {actual} != {expected}")
        frozen[relpath] = expected
    for relpath, expected in r2["snapshots"].items():
        actual = sha256(ROOT / Path(relpath))
        if actual != expected:
            raise ValueError(f"r2 snapshot drift: {relpath}: {actual} != {expected}")
    manifest_hash = sha256(ROOT / R2_PATH)
    if reconciliation.get("allAssignmentsUnchanged") is not True or reconciliation.get("snapshotHashesUnchanged") is not True:
        raise ValueError("T35 reconciliation does not confirm unchanged assignment/snapshot data")
    if r1["assignments"] != r2["assignments"]:
        raise ValueError("r1/r2 assignment objects differ")
    assignments = r2["assignments"]
    target_owner = owner_map(assignments, "assignedTargetIds")
    concept_owner = owner_map(assignments, "assignedSourceConceptKeys")
    surface_owner = owner_map(assignments, "assignedSourceKeys")
    targets = read(PLAN_DIR / "muscle-targets.json")
    concepts = read(PLAN_DIR / "source-concepts.json")
    surfaces = read(PLAN_DIR / "source-instances.json")
    if len(targets) != 429 or len(concepts) != 232 or len(surfaces) != 462:
        raise ValueError("frozen whole-muscle snapshot denominators changed")
    target_scope = {row["id"]: row for row in scope["targets"]}
    source_rows = {row["sourceKey"]: row for row in surfaces}
    compiled_rows = {row["sourceKey"]: row for row in compiled["instances"]}
    target_ids = {row["id"] for row in targets}
    concept_ids = {row["conceptKey"] for row in concepts}
    surface_ids = {row["sourceKey"] for row in surfaces}
    if set(target_owner) != target_ids or set(concept_owner) != concept_ids or set(surface_owner) != surface_ids:
        raise ValueError("r2 assignment union is not complete/disjoint over snapshots")
    if not target_ids.issubset(target_scope):
        raise ValueError("muscle targets do not resolve in T96 scope")
    memberships: list[dict[str, str]] = []
    target_by_id = {row["id"]: row for row in targets}
    for row in targets:
        scope_row = target_scope[row["id"]]
        regions = sorted(set(scope_row.get("regionIds", [])))
        if regions != sorted(set(row.get("regionIds", []))):
            raise ValueError(f"region memberships differ between T96 and T35 snapshot: {row['id']}")
        for region in regions:
            memberships.append({"targetId": row["id"], "regionId": region, "membershipKey": f"{row['id']}::{region}", "owner": target_owner[row["id"]]})
    if len(memberships) != 447 or len({row["membershipKey"] for row in memberships}) != 447:
        raise ValueError(f"expected 447 exact muscle memberships, got {len(memberships)}")

    concept_by_key = {row["conceptKey"]: row for row in concepts}
    concept_for_surface: dict[str, str] = {}
    for concept in concepts:
        for source_key in concept["sourceKeys"]:
            if source_key in concept_for_surface:
                raise ValueError(f"surface appears in multiple source concepts: {source_key}")
            concept_for_surface[source_key] = concept["conceptKey"]
    if set(concept_for_surface) != surface_ids:
        raise ValueError("source concept grouping does not cover 462 surfaces exactly once")

    target_candidates: dict[str, list[dict[str, Any]]] = {target_id: [] for target_id in target_ids}
    for source_key, row in source_rows.items():
        for target_id in row.get("targetIds", []):
            if target_id in target_candidates:
                target_candidates[target_id].append({
                    "sourceKey": source_key,
                    "sourceConceptKey": concept_for_surface[source_key],
                    "side": row.get("side"),
                    "relationStatus": "source_relation_candidate_requires_motion_scope_validation",
                    "existingHaConceptId": row.get("haConceptId"),
                })

    dependencies = {
        "r2-research-manifest": {"path": R2_PATH.as_posix(), "sha256": manifest_hash},
        "t35-motion-contract": {"path": CONTRACT_PATH.as_posix(), "sha256": sha256(ROOT / CONTRACT_PATH)},
        "t35-motion-readiness": {"path": TARGET_PATH.as_posix(), "sha256": sha256(ROOT / TARGET_PATH)},
        "t96-target-scope": {"path": TARGET_SCOPE_PATH.as_posix(), "sha256": frozen[TARGET_SCOPE_PATH.as_posix()]},
        "za-compiled-manifest": {"path": COMPILED_PATH.as_posix(), "sha256": frozen[COMPILED_PATH.as_posix()]},
        "motion-learning-current": {"path": "atlas-data/motion/motion-learning.json", "sha256": frozen["atlas-data/motion/motion-learning.json"]},
        "za-local-integration": {"path": "atlas-data/overlays/za-local-integration.json", "sha256": frozen["atlas-data/overlays/za-local-integration.json"]},
        "r2-target-snapshot": {"path": "work/evidence/motion-all-muscles-plan-2026-10-02/muscle-targets.json", "sha256": r2["snapshots"]["work/evidence/motion-all-muscles-plan-2026-10-02/muscle-targets.json"]},
        "r2-source-concept-snapshot": {"path": "work/evidence/motion-all-muscles-plan-2026-10-02/source-concepts.json", "sha256": r2["snapshots"]["work/evidence/motion-all-muscles-plan-2026-10-02/source-concepts.json"]},
        "r2-source-instance-snapshot": {"path": "work/evidence/motion-all-muscles-plan-2026-10-02/source-instances.json", "sha256": r2["snapshots"]["work/evidence/motion-all-muscles-plan-2026-10-02/source-instances.json"]},
    }
    for dependency_id, path in CONTRACT_FILES.items():
        if not (ROOT / path).is_file():
            raise ValueError(f"required T59 contract/exporter file is missing: {path}")
        dependencies[dependency_id] = {"path": path.as_posix(), "sha256": sha256(ROOT / path)}
    target_packages = []
    for target in targets:
        target_id = target["id"]
        owner = target_owner[target_id]
        members = [row["membershipKey"] for row in memberships if row["targetId"] == target_id]
        target_packages.append({
            "packageId": f"T66-TARGET-{target_id.replace(':', '-')}",
            "packageType": "target_scope_motion_authoring",
            "owner": owner,
            "assignedTargetIds": [target_id],
            "assignedMembershipKeys": members,
            "semanticKind": target["semanticKind"],
            "regionIds": sorted(set(target.get("regionIds", []))),
            "sourceTerm": target.get("term", {}),
            "sourceParentTargetId": target.get("sourceParentTargetId"),
            "candidateSourceRelations": sorted(target_candidates[target_id], key=lambda row: (row["sourceKey"], str(row["side"]))),
            "targetIdentityDisposition": "no_verified_target_identity_in_T35_readiness_ledger",
            "outputPath": f"work/evidence/T66/authoring-candidates/{owner}/{target_id.replace(':', '-')}/candidate-package.json",
            "dependencyIds": sorted(dependencies),
            "authoringStatus": "not_authorable_until_exact_source_scope_and_motion_inputs_are_provided",
            "missingInputs": ["exact source-target identity and full/part/member extent", "source-native rig bind/rest pose", "source-backed movement action and pose range", "exact side-specific moving/fixed/passive member set", "reproducible source-derived deformation and geometry validation"],
            "preservation": {"sourceOnlyStatusPreserved": True, "humanReview": "not_performed", "localRights": "held_per_source", "publicRedistribution": "held", "canonicalHaIdCreated": False},
        })

    concept_packages = []
    compiled_frame = compiled.get("frameContract", {})
    for concept in concepts:
        concept_key = concept["conceptKey"]
        owner = concept_owner[concept_key]
        member_rows = []
        for source_key in concept["sourceKeys"]:
            if surface_owner[source_key] != owner:
                raise ValueError(f"source concept and source surface have different workers: {concept_key}/{source_key}")
            src = source_rows[source_key]
            compiled_src = compiled_rows[source_key]
            member_rows.append({
                "sourceKey": source_key,
                "sourceName": src["sourceName"],
                "sourceSide": src.get("side"),
                "regionIds": src.get("regionIds", []),
                "targetIdsContextOnly": src.get("targetIds", []),
                "haConceptId": src.get("haConceptId"),
                "sourceOnly": compiled_src.get("sourceOnly", src.get("sourceOnly")),
                "humanReview": src.get("humanReview", "not_performed"),
                "publicRedistribution": src.get("publicRedistribution", "held"),
                "sourceNamespace": compiled_src.get("sourceNamespace", compiled["namespace"]),
                "sourceGeometrySha256": compiled_src.get("evaluatedGeometrySha256"),
                "sourceResourceFingerprint": compiled_src.get("fingerprint"),
                "instanceMatrix": compiled_src.get("matrix"),
                "geometrySpace": compiled_src.get("geometrySpace"),
                "overview": compiled_src.get("lods", {}).get("overview"),
                "detail": compiled_src.get("lods", {}).get("detail"),
                "upstreamFjId": compiled_src.get("upstreamFjId"),
                "sourceAncestry": compiled_src.get("upstreamPerObjectAncestry"),
                "defaultLearnerVisible": compiled_src.get("defaultLearnerVisible"),
                "appDisplayRights": compiled_src.get("appDisplayRights"),
                "nativeSourceRestPose": "unavailable_in_compiled_static_surface_manifest",
                "sourceFrame": {"runtimeTargetFrame": compiled_frame.get("targetFrameId"), "runtimeUnit": compiled.get("unit"), "staticReferencePose": compiled_frame.get("staticReferencePose")},
            })
        concept_packages.append({
            "packageId": f"T66-SOURCE-{hashlib.sha256(concept_key.encode()).hexdigest()[:16]}",
            "packageType": "source_concept_surface_motion_authoring",
            "owner": owner,
            "assignedSourceConceptKeys": [concept_key],
            "assignedSourceKeys": sorted(concept["sourceKeys"]),
            "sourceConceptKey": concept_key,
            "sourceDataName": concept["sourceDataName"],
            "sideState": concept.get("sourceSides", []),
            "targetIdsContextOnly": concept.get("targetIds", []),
            "members": member_rows,
            "outputPath": f"work/evidence/T66/authoring-candidates/{owner}/{hashlib.sha256(concept_key.encode()).hexdigest()[:16]}/candidate-package.json",
            "dependencyIds": sorted(dependencies),
            "authoringStatus": "source_surface_inventory_only_native_rig_pose_and_deformation_unavailable",
            "missingInputs": ["native source rig/bind/rest pose or an evidenced derivation", "source-bound action condition, fixed/moving bone and neighboring passive context", "source-derived non-scale muscle deformation per source topology", "part/group/side extent confirmation when source scope is compound"],
            "preservation": {"sourceOnlyStatusPreserved": True, "humanReview": "not_performed", "localRights": "held_per_source", "publicRedistribution": "held", "canonicalHaIdCreated": False},
        })

    target_owner_counts = {worker: sum(1 for value in target_owner.values() if value == worker) for worker in assignments}
    concept_owner_counts = {worker: sum(1 for value in concept_owner.values() if value == worker) for worker in assignments}
    surface_owner_counts = {worker: sum(1 for value in surface_owner.values() if value == worker) for worker in assignments}
    manifest = {
        "schemaVersion": "t59-authoring-run-manifest-v1",
        "task": "T59",
        "runId": AUTHORING_RUN_ID,
        "nextUnit": AUTHORING_NEXT_UNIT,
        "createdOn": "2026-10-02",
        "baselineHead": baseline["baselineHead"],
        "baselineEvidence": {"path": BASELINE_PATH.as_posix(), "sha256": sha256(ROOT / BASELINE_PATH)},
        "contractRevision": "t59-source-bound-same-scene-motion-v1",
        "acceptanceScope": "common motion runtime/export pipeline and complete T66 whole-muscle source/target authoring handoff; not all clips or human/release approval",
        "researchRun": {"r1Path": R1_PATH.as_posix(), "r1RunId": r1["runId"], "r2Path": R2_PATH.as_posix(), "r2RunId": r2["runId"], "r2ManifestSha256": manifest_hash, "assignmentSetUnchangedFromR1": True},
        "denominators": {"productTargets": 542, "productMemberships": 563, "regions": 12, "muscleTargets": 429, "muscleMemberships": 447, "sourceConcepts": 232, "sourceSurfaceInstances": 462, "existingCanonicalHaBindings": 130, "historical163": [6, 20, 135, 2]},
        "frozenInputHashes": frozen,
        "frozenSnapshotHashes": r2["snapshots"],
        "commonWriterContract": {
            "owner": "T59 integration; T66 must reference the pinned contract and cannot redefine shared scene/runtime",
            "sceneRoot": "existing whole-body scene root",
            "rendererCameraAndFrameClock": "existing AnatomySceneController; one renderer/camera/frame clock",
            "adapter": "AnimationSceneAdapter + DatasetSceneAdapter sourceKey binding",
            "sourceBinding": "exact sourceKey/namespace/revision/chunk/resource/LOD/geometry hash/matrix/frame/unit/side/reference pose",
            "deformation": "source-derived skinning and/or per-topology morph/corrective; no whole-muscle scale; no synthetic production geometry",
            "movingFixedPassive": "per-package role set; bone movement position/quaternion only; fixed/passive context receives no animation track",
            "unresolvedNativeRestPose": True,
            "currentSupportedProductionMuscleMotionAssets": 0,
        },
        "tools": {
            "deriveCommand": "python3 work/tools/derive_source_surface_motion.py --input <frozen-source-package> --output <candidate.glb>",
            "manifestValidator": "python3 work/tools/validate_t59_authoring_manifest.py --check --fixtures",
            "runtimeValidator": "python3 atlas-data/schemas/validate_motion_learning.py --check --fixtures",
            "syntheticFixturesProductionUse": False,
        },
        "authoringContractInputs": {dependency_id: dependencies[dependency_id] for dependency_id in CONTRACT_FILES},
        "workers": {worker: {
            "owner": worker,
            "assignedTargetIds": sorted(assignment["assignedTargetIds"]),
            "assignedMembershipKeys": sorted(row["membershipKey"] for row in memberships if target_owner[row["targetId"]] == worker),
            "assignedSourceConceptKeys": sorted(assignment["assignedSourceConceptKeys"]),
            "assignedSourceKeys": sorted(assignment["assignedSourceKeys"]),
            "targetCount": target_owner_counts[worker], "membershipCount": len([row for row in memberships if target_owner[row["targetId"]] == worker]),
            "sourceConceptCount": concept_owner_counts[worker], "sourceSurfaceCount": surface_owner_counts[worker],
            "outputDirectory": f"work/evidence/T66/authoring-candidates/{worker}",
            "candidatePackagePathPrefix": f"work/evidence/T66/authoring-candidates/{worker}/",
            "writeOwnership": "candidate package files assigned to this worker only; never shared manifest, schema, runtime, evidence, or other worker directory",
            "mayEditSharedRigOrActionContract": False,
        } for worker, assignment in assignments.items()},
        "sharedInputsAndDependencies": dependencies,
        "targetPackages": target_packages,
        "sourceConceptPackages": concept_packages,
        "validationRules": [
            "all 429 target records, their 447 (targetId,regionId) memberships, all 232 source concepts and 462 unique source keys appear exactly once in assigned packages",
            "candidate source relations are context-only until exact concept/part/member extent and laterality are independently validated",
            "native rest/bind pose, action condition, side, moving/fixed/passive context, topology hash and derived output hash must be provided per candidate",
            "each derived package must preserve source-only and local/public rights holds; humanReview remains not_performed",
            "no candidate output may be a generated guess, mirrored side, whole-muscle scale-only transform, or illustrative path presented as muscle contraction",
            "one source surface package may support multiple target context memberships only through explicit verified scope rows; group/part success is not inherited",
        ],
        "currentReadiness": {"authorableProductionPackages": 0, "targetPackagesNotAuthorable": len(target_packages), "sourceConceptPackagesNotAuthorable": len(concept_packages), "reason": "current frozen source manifest contains static surfaces but no source-native muscle rig/rest pose or source-derived movement package"},
        "preservation": {"sourceOnlyStatusPreserved": True, "localRights": "held", "publicRedistribution": "held", "humanReview": "not_performed", "existingCanonicalHaBindings": 130, "newCanonicalHaBindings": 0, "originalSourceAndOpenSimUnmodified": True},
    }
    worker_reconciliation = build_worker_reconciliation(r2, manifest_hash)
    return manifest, worker_reconciliation


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--refresh-owned", action="store_true", help="refresh only existing T59-generated outputs when their frozen scope is unchanged")
    args = parser.parse_args()
    manifest, reconciliation = build()
    outputs = ((MANIFEST_OUT, manifest), (RECON_OUT, reconciliation))
    if args.write or args.refresh_owned:
        if args.refresh_owned:
            existing_manifest = read(MANIFEST_OUT)
            existing_reconciliation = read(RECON_OUT)
            fixed_keys = ("baselineHead", "frozenInputHashes", "frozenSnapshotHashes", "denominators")
            if existing_manifest.get("task") != "T59" or any(existing_manifest.get(key) != manifest.get(key) for key in fixed_keys):
                raise SystemExit("refusing to refresh T59 evidence: task identity or frozen scope changed")
            if existing_reconciliation.get("task") != "T59" or existing_reconciliation.get("manifestRunId") != reconciliation.get("manifestRunId") or existing_reconciliation.get("currentManifestSha256") != reconciliation.get("currentManifestSha256"):
                raise SystemExit("refusing to refresh T59 evidence: worker reconciliation inputs changed")
        if args.write and any((ROOT / path).exists() for path, _ in outputs):
            raise SystemExit("refusing to overwrite existing task evidence; use --refresh-owned only for T59-generated outputs with the same frozen scope")
        for path, value in outputs:
            target = ROOT / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"written": [path.as_posix() for path, _ in outputs], "targets": len(manifest["targetPackages"]), "memberships": sum(len(row["assignedMembershipKeys"]) for row in manifest["targetPackages"]), "sourceConcepts": len(manifest["sourceConceptPackages"]), "surfaces": sum(len(row["assignedSourceKeys"]) for row in manifest["sourceConceptPackages"])}, ensure_ascii=False))
    else:
        print(json.dumps({"manifestHash": value_sha(manifest), "workerReconciliationHash": value_sha(reconciliation), "targets": len(manifest["targetPackages"]), "sourceConcepts": len(manifest["sourceConceptPackages"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
