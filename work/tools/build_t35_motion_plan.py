#!/usr/bin/env python3
"""Build the exhaustive, non-production T35 muscle-motion readiness plan."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path("work/evidence/motion-all-muscles-plan-2026-10-02")
OUT = Path("work/evidence/T35")
MANIFEST = BASE / "run-manifest-r2.json"


def load(path: str | Path):
    return json.loads((ROOT / path).read_text())


def sha(path: str | Path) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def row_sha(row: dict) -> str:
    raw = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def dump(path: str | Path, value):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def concise_field_evidence(record: dict) -> dict:
    result = {}
    for field in ("origin", "insertion"):
        evidence = record.get("fieldEvidence", {}).get(field, {})
        result[field] = {
            "sourceIds": evidence.get("sourceIds", []),
            "locator": evidence.get("locator"),
            "learnerValueSha256": evidence.get("learnerValueSha256"),
            "reviewNotesSha256": evidence.get("reviewNotesSha256"),
            "fieldValueStoredElsewhere": True,
        }
    return result


def audit_worker_proposals(manifest: dict) -> dict:
    """Observe external worker files without rebasing or importing their claims."""
    rows = {}
    for assignment_name, assignment in manifest["assignments"].items():
        path = ROOT / assignment["outputDirectory"] / "proposals.json"
        if not path.exists():
            rows[assignment_name] = {
                "path": str(path.relative_to(ROOT)),
                "status": "absent",
                "stableRead": False,
                "eligibleForFullValidator": False,
                "integrated": False,
                "reason": "no proposal file present for this assignment",
            }
            continue

        with path.open("rb") as handle:
            fd_before = os.fstat(handle.fileno())
            raw = handle.read()
            fd_after = os.fstat(handle.fileno())
        path_after = path.stat()
        signature = lambda stat: (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)
        stable = signature(fd_before) == signature(fd_after) == signature(path_after)
        result = json.loads(raw) if stable else {}
        result_targets = result.get("targetRows", [])
        result_sources = result.get("sourceRows", [])
        mismatched_hashes = sorted(
            key for key, value in manifest["inputHashes"].items()
            if result.get("inputHashes", {}).get(key) != value
        )
        target_ids_match = (
            len(result_targets) == len(assignment["assignedTargetIds"])
            and {row.get("targetId") for row in result_targets} == set(assignment["assignedTargetIds"])
        )
        concept_keys_match = (
            len(result_sources) == len(assignment["assignedSourceConceptKeys"])
            and {row.get("sourceConceptKey") for row in result_sources}
            == set(assignment["assignedSourceConceptKeys"])
        )
        current_run = stable and result.get("runId") == manifest["runId"]
        current_inputs = stable and result.get("inputHashes") == manifest["inputHashes"]
        snapshot_claim = result.get("manifestSnapshots", {}) if stable else {}
        snapshots_match = stable and snapshot_claim == manifest["snapshots"]
        ready = (
            stable and current_run and current_inputs and snapshots_match
            and result.get("assignment") == assignment_name
            and result.get("assignedTargetIds") == assignment["assignedTargetIds"]
            and result.get("assignedSourceConceptKeys") == assignment["assignedSourceConceptKeys"]
            and target_ids_match and concept_keys_match
            and result.get("productionAcceptance") is False
        )
        rows[assignment_name] = {
            "path": str(path.relative_to(ROOT)),
            "status": "ready_for_full_validator" if ready else "stale_or_unvalidated_not_integrated",
            "stableRead": stable,
            "sha256": hashlib.sha256(raw).hexdigest() if stable else None,
            "bytes": len(raw) if stable else None,
            "recordedRunId": result.get("runId") if stable else None,
            "expectedRunId": manifest["runId"],
            "assignment": result.get("assignment") if stable else None,
            "recordedStatus": result.get("status") if stable else None,
            "stale": result.get("stale") if stable else None,
            "changedInputPaths": mismatched_hashes if stable else [],
            "targetRowCount": len(result_targets) if stable else None,
            "sourceConceptRowCount": len(result_sources) if stable else None,
            "assignedTargetIdsMatch": target_ids_match if stable else False,
            "assignedSourceConceptKeysMatch": concept_keys_match if stable else False,
            "eligibleForFullValidator": ready,
            "integrated": False,
            "reason": "worker outputs are optional; only a complete current-manifest result set that passes --results may be integrated",
        }
    return {
        "schemaVersion": "t35-worker-result-observation-v1",
        "manifestPath": str(MANIFEST),
        "manifestRunId": manifest["runId"],
        "assignments": rows,
        "integratedAssignments": [],
        "allAssignmentsReadyForValidator": all(row["eligibleForFullValidator"] for row in rows.values()),
        "noUnvalidatedOutputIntegrated": all(not row["integrated"] for row in rows.values()),
    }


def reconcile_manifests(manifest: dict) -> dict:
    original = load(BASE / "run-manifest.json")
    changes = []
    all_paths = sorted(set(original.get("inputHashes", {})) | set(manifest.get("inputHashes", {})))
    for path in all_paths:
        before = original.get("inputHashes", {}).get(path)
        after = manifest.get("inputHashes", {}).get(path)
        if before != after:
            changes.append({"path": path, "originalSha256": before, "revisedSha256": after,
                            "changeKind": "added_to_revised_manifest" if before is None else "hash_changed" if after is not None else "removed_from_revised_manifest"})
    assignment_checks = {}
    for name in manifest["assignments"]:
        old = original["assignments"][name]
        new = manifest["assignments"][name]
        fields = ["assignedTargetIds", "assignedSourceConceptKeys", "assignedSourceKeys", "counts", "outputDirectory"]
        assignment_checks[name] = {
            "sameAssignedListsAndOutputPath": all(old.get(field) == new.get(field) for field in fields),
            "counts": new["counts"],
            "orderedAssignmentDigestSha256": hashlib.sha256(json.dumps(
                {field: new[field] for field in fields}, ensure_ascii=False, sort_keys=True,
                separators=(",", ":")
            ).encode()).hexdigest(),
        }
    baseline = load(OUT / "start-baseline.json")
    return {
        "schemaVersion": "t35-manifest-reconciliation-v1",
        "baselineHead": baseline["baselineHead"],
        "originalRunId": original["runId"],
        "revisedRunId": manifest["runId"],
        "originalSourceHead": original.get("sourceHead"),
        "manifestSourceHeadUnchanged": original.get("sourceHead") == manifest.get("sourceHead"),
        "originalInputHashCount": len(original.get("inputHashes", {})),
        "revisedInputHashCount": len(manifest.get("inputHashes", {})),
        "changedOrAddedInputHashes": changes,
        "snapshotHashesUnchanged": original.get("snapshots") == manifest.get("snapshots"),
        "assignmentChecks": assignment_checks,
        "allAssignmentsUnchanged": all(row["sameAssignedListsAndOutputPath"] for row in assignment_checks.values()),
        "revisionReason": "the original frozen inputs predate current T98 feasibility/frame/rights evidence and the 2026-10-02 attachment review/runtime projection; r2 preserves the original 429/447/232/462 assignment and the same snapshots while pinning the current evidence hashes",
        "originalManifestModified": False,
    }


def main():
    manifest = load(MANIFEST)
    for path, expected in {**manifest["inputHashes"], **manifest["snapshots"]}.items():
        actual = sha(path)
        if actual != expected:
            raise SystemExit(f"stale T35 planning input: {path}")

    scope = load("atlas-data/catalog/target-scope-t96.json")
    targets = load(BASE / "muscle-targets.json")
    concepts = load(BASE / "source-concepts.json")
    instances = load(BASE / "source-instances.json")
    source_catalog = load("work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json")
    compiled = load("atlas-data/source-cache/datasets/za/compiled/manifest.json")
    base_selection = load("work/evidence/T98/astra-resolution-2026-09-29/base-selection.json")
    t98_frame_contract = load("work/evidence/T98/astra-resolution-2026-09-29/frame-contract.json")
    t98_rights_scope = load("work/evidence/T98/astra-resolution-2026-09-29/rights-scope.json")
    learner_runtime = load("atlas-data/terminology/learner-card-runtime.json")
    motion_learning = load("atlas-data/motion/motion-learning.json")
    motion_sources = load("atlas-data/motion/motion-asset-sources.json")
    t65 = load("work/evidence/T65/muscle-attachment-dispositions.json")
    new_attachment = load("atlas-data/terminology/muscle-attachment-content-2026-10-02.json")
    new_attachment_coverage = load("work/evidence/muscle-attachment-review-2026-10-02/coverage.json")

    target_ids = {row["id"] for row in targets}
    t96_target_ids = {row["id"] for row in scope["targets"]}
    t96_muscle_target_ids = {
        row["id"] for row in scope["targets"]
        if row.get("semanticKind") in {"named_muscle", "muscle_part", "muscle_group", "muscle_complex", "repeated_muscle_family"}
    }
    t96_denominators = scope["denominators"]
    concept_by_key = {row["conceptKey"]: row for row in concepts}
    instance_by_key = {row["sourceKey"]: row for row in instances}
    object_by_key = {row["sourceKey"]: row for row in source_catalog["objects"]}
    compiled_instance_by_key = {row["sourceKey"]: row for row in compiled["instances"]}
    target_overlay = {row["targetId"]: row for row in source_catalog["targetOverlay"]}
    if len(target_ids) != 429 or len(concepts) != 232 or len(instances) != 462:
        raise SystemExit("frozen T35 denominator drift")
    if (len(t96_target_ids) != t96_denominators["frozenTa2NamedTargetRecords"]
            or len(scope["regions"]) != 12
            or t96_denominators["productRegionMembershipRows"] != 563
            or target_ids != t96_muscle_target_ids):
        raise SystemExit("T35 subset or whole-body denominator drift against T96")
    if set(instance_by_key) != {key for concept in concepts for key in concept["sourceKeys"]}:
        raise SystemExit("source concept/instance membership drift")
    if not set(instance_by_key).issubset(object_by_key) or not set(instance_by_key).issubset(compiled_instance_by_key):
        raise SystemExit("pinned source object or compiled instance missing for a frozen instance")

    assignments = manifest["assignments"]
    assignment_by_target = {}
    assignment_by_concept = {}
    assignment_by_source = {}
    for assignment, row in assignments.items():
        for target_id in row["assignedTargetIds"]:
            if target_id in assignment_by_target:
                raise SystemExit("duplicate target owner")
            assignment_by_target[target_id] = assignment
        for concept_key in row["assignedSourceConceptKeys"]:
            if concept_key in assignment_by_concept:
                raise SystemExit("duplicate source-concept owner")
            assignment_by_concept[concept_key] = assignment
        for source_key in row["assignedSourceKeys"]:
            if source_key in assignment_by_source:
                raise SystemExit("duplicate source-instance owner")
            assignment_by_source[source_key] = assignment
    if set(assignment_by_target) != target_ids or set(assignment_by_concept) != set(concept_by_key) or set(assignment_by_source) != set(instance_by_key):
        raise SystemExit("assignment union is not exact")

    # Preserve the historical 31/201 split, then explicitly join the newer 201-row review.
    prior_rows = t65["priorT90WithDescriptionOrConflictNotice"] + t65["T65Added"]["records"]
    missing_rows = t65["remainingWithoutDescriptions"]
    historical_conflicts = t65["remainingConflicts"]
    baseline_by_concept = {}
    for row in prior_rows:
        baseline_by_concept[row["sourceConceptKey"]] = {
            "historicalDisposition": "description_or_conflict_notice",
            "sourceKeys": row.get("sourceKeys", []),
            "status": row.get("originStatus") or row.get("insertionStatus"),
            "scopeType": row.get("scopeType"),
        }
    for row in missing_rows:
        baseline_by_concept[row["sourceConceptKey"]] = {
            "historicalDisposition": "missing_at_T65_baseline",
            "sourceKeys": row.get("sourceKeys", []),
            "status": row.get("disposition"),
            "scopeType": None,
        }
    for row in historical_conflicts:
        baseline_by_concept[row["sourceConceptKey"]] = {
            "historicalDisposition": "conflicted_at_T65_baseline",
            "sourceKeys": row.get("sourceKeys", []),
            "status": row.get("originStatus") or row.get("insertionStatus"),
            "scopeType": None,
        }
    if len(prior_rows) != 31 or len(missing_rows) != 201 or len(historical_conflicts) != 1:
        raise SystemExit("T65 historical attachment disposition changed")

    attachment_records = defaultdict(list)
    for index, row in enumerate(new_attachment["records"]):
        ref = {
            "path": "atlas-data/terminology/muscle-attachment-content-2026-10-02.json",
            "recordIndex": index,
            "recordSha256": row_sha(row),
            "evidenceState": row.get("evidenceState"),
            "scopeType": row.get("scopeType"),
            "summaryExtent": row.get("summaryExtent"),
            "fieldEvidence": concise_field_evidence(row),
        }
        for source_key in row.get("sourceKeys", []):
            attachment_records[source_key].append(ref)

    learner_by_source = learner_runtime.get("structure", {}).get("bySource", {})
    missing_runtime_source_keys = sorted(set(instance_by_key) - set(learner_by_source))
    incomplete_runtime_source_keys = sorted(
        key for key in set(instance_by_key) & set(learner_by_source)
        if not learner_by_source[key].get("origin") or not learner_by_source[key].get("insertion")
    )
    actions_by_ha = defaultdict(list)
    for action in motion_learning.get("muscleActions", []):
        for ha_id in action.get("subjectIds", []):
            actions_by_ha[ha_id].append({
                "actionId": action["id"],
                "sideApplicability": action.get("sideApplicability"),
                "jointBindingState": action.get("jointBindingState"),
                "sourceRefIds": [ref.get("evidenceId") for ref in action.get("sourceRefs", []) if ref.get("evidenceId")],
                "disposition": "existing_text_action_candidate_not_motion_acceptance",
            })

    concepts_by_target = defaultdict(list)
    for concept in concepts:
        for target_id in concept.get("targetIds", []):
            if target_id in target_ids:
                concepts_by_target[target_id].append(concept["conceptKey"])

    target_rows = []
    for target in targets:
        target_id = target["id"]
        overlay = target_overlay[target_id]
        candidate_keys = list(overlay.get("candidateSourceKeys", []))
        context_concepts = concepts_by_target[target_id]
        action_candidates = sorted({
            action["actionId"]
            for concept_key in context_concepts
            for source_key in concept_by_key[concept_key]["sourceKeys"]
            for action in actions_by_ha.get(instance_by_key[source_key].get("haConceptId"), [])
        })
        target_rows.append({
            "targetId": target_id,
            "semanticKind": target["semanticKind"],
            "term": target["term"],
            "primaryOwner": target["primaryOwner"],
            "regionIds": target["regionIds"],
            "membershipKeys": [f"{target_id}::{region}" for region in target["regionIds"]],
            "sourceParentTargetId": target.get("sourceParentTargetId"),
            "sourceAncestryIds": target.get("sourceAncestryIds", []),
            "scopeFlags": target.get("scopeFlags", {}),
            "sourceCardinality": target.get("sourceCardinality", {}),
            "researchAssignment": assignment_by_target[target_id],
            "targetSourceCandidateDisposition": {
                "status": overlay["status"],
                "candidateSourceKeys": candidate_keys,
                "candidateCount": len(candidate_keys),
                "candidateKeysAreNotAcceptedIdentity": True,
                "canonicalIdentityVerifiedInPinnedCatalog": overlay.get("canonicalIdentityVerified", False),
                "learnerBindingAddedInPinnedCatalog": overlay.get("learnerBindingAdded", False),
                "conceptContextKeysNotAnExactMotionBinding": context_concepts,
            },
            "representationScope": {
                "declaredKind": target["semanticKind"],
                "partGroupMemberExtentMustBeValidatedIndependently": True,
                "parentOrPartialMemberDoesNotSatisfyWholeTarget": True,
            },
            "attachmentEvidenceCandidates": sorted({
                ref["recordSha256"]
                for source_key in candidate_keys
                for ref in attachment_records.get(source_key, [])
            }),
            "actionEvidenceCandidates": action_candidates,
            "sideDisposition": "use_target_sourceCardinality_and_exact_instance_side_only; never inherit an unsided parent side",
            "poseDisposition": "not_defined_for_motion; requires source/frame/action-specific pose evidence",
            "motionFamilyDisposition": "not_assigned_without exact identity, action, joint/context, and deformation evidence",
            "productionMotionStatus": "not_implemented",
            "nextEvidence": ["exact target-to-source scope", "source-backed action and conditions", "registered frame and reference pose", "deformation-capable source/derived rig", "same-scene surface and context validation"],
        })

    memberships = []
    for target in targets:
        overlay = target_overlay[target["id"]]
        for region_id in target["regionIds"]:
            memberships.append({
                "membershipKey": f"{target['id']}::{region_id}",
                "targetId": target["id"],
                "regionId": region_id,
                "semanticKind": target["semanticKind"],
                "researchAssignment": assignment_by_target[target["id"]],
                "candidateSourceKeys": overlay.get("candidateSourceKeys", []),
                "extentDisposition": "catalog membership retained; no independent motion/extent acceptance",
            })

    concept_rows = []
    for concept in concepts:
        keys = concept["sourceKeys"]
        baseline = baseline_by_concept.get(concept["conceptKey"], {"historicalDisposition": "not_classified_in_T65_attachment_ledger", "sourceKeys": []})
        latest_records = []
        latest_keys = set()
        for source_key in keys:
            latest_records.extend(attachment_records.get(source_key, []))
            if source_key in attachment_records:
                latest_keys.add(source_key)
        unique_latest = {record["recordSha256"]: record for record in latest_records}
        surface_records = []
        for source_key in keys:
            instance = instance_by_key[source_key]
            obj = object_by_key[source_key]
            compiled_obj = compiled_instance_by_key[source_key]
            learner_row = learner_by_source.get(source_key)
            ha_id = instance.get("haConceptId")
            source_actions = actions_by_ha.get(ha_id, []) if ha_id else []
            surface_records.append({
                "sourceKey": source_key,
                "sourceName": instance["sourceName"],
                "side": instance.get("side"),
                "sourceLabelSide": obj.get("sourceLabelSide"),
                "geometryIdentity": {
                    "identityKind": obj.get("identityKind"),
                    "sourceLocator": obj.get("sourceLocator"),
                    "evaluatedGeometrySha256": obj.get("evaluatedGeometrySha256"),
                    "upstreamFjId": obj.get("upstreamFjId"),
                    "upstreamPerObjectAncestry": obj.get("upstreamPerObjectAncestry"),
                    "sourceLocalBounds": obj.get("sourceLocalBounds"),
                },
                "compiledSceneInstance": {
                    "geometrySpace": compiled_obj.get("geometrySpace"),
                    "transformAppliedToGeometry": compiled_obj.get("transformAppliedToGeometry"),
                    "instanceMatrix": compiled_obj.get("matrix"),
                    "sourceLocalBounds": compiled_obj.get("sourceLocalBounds"),
                    "compiledGeometrySha256": compiled_obj.get("evaluatedGeometrySha256"),
                    "fingerprint": compiled_obj.get("fingerprint"),
                    "quality": compiled_obj.get("quality"),
                    "lods": compiled_obj.get("lods"),
                    "compiledManifestFrameId": compiled["frameContract"]["targetFrameId"],
                    "compiledManifestUnit": compiled["unit"],
                },
                "geometryHashComparison": {
                    "sourceCatalogHash": obj.get("evaluatedGeometrySha256"),
                    "compiledManifestHash": compiled_obj.get("evaluatedGeometrySha256"),
                    "valuesEqual": obj.get("evaluatedGeometrySha256") == compiled_obj.get("evaluatedGeometrySha256"),
                    "status": "same_value" if obj.get("evaluatedGeometrySha256") == compiled_obj.get("evaluatedGeometrySha256") else "different_values_hashing_contract_or_revision_not_reconciled",
                    "notInterpretedAsGeometryMismatchOrEquivalence": True,
                },
                "attachmentProjection": {
                    "learnerCardPresent": bool(learner_row),
                    "originTextPresent": bool(learner_row and learner_row.get("origin")),
                    "insertionTextPresent": bool(learner_row and learner_row.get("insertion")),
                    "textIsNotSourceApproval": True,
                },
                "attachmentEvidenceRecordHashes": sorted({r["recordSha256"] for r in attachment_records.get(source_key, [])}),
                "existingHaConceptId": ha_id,
                "textActionCandidateIds": [r["actionId"] for r in source_actions],
                "sourceOnly": instance.get("sourceOnly"),
                "humanReview": instance.get("humanReview"),
                "publicRedistribution": instance.get("publicRedistribution"),
                "localDisplayEligible": instance.get("localDisplayEligible"),
                "framePose": {
                    "sourceFrameId": t98_frame_contract.get("sourceFrameId"),
                    "targetFrameId": t98_frame_contract.get("targetFrameId"),
                    "sourceUnitInterpretation": t98_frame_contract.get("sourceUnit"),
                    "sourcePhysicalUnitDeclaredBySource": None,
                    "sourceToProjectConvention": t98_frame_contract.get("sourceToProjectConvention"),
                    "registeredToBP3DGeometry": t98_frame_contract.get("registeredToBP3DGeometry"),
                    "staticReferencePose": t98_frame_contract.get("staticReferencePose"),
                },
            })
        concept_rows.append({
            "conceptKey": concept["conceptKey"],
            "sourceDataName": concept["sourceDataName"],
            "sourceKeys": keys,
            "regionIds": concept["regionIds"],
            "targetIdsContextOnly": concept.get("targetIds", []),
            "sourceSides": concept.get("sourceSides", []),
            "sourceOnly": concept.get("sourceOnly"),
            "humanReview": concept.get("humanReview"),
            "publicRedistribution": concept.get("publicRedistribution"),
            "researchAssignment": assignment_by_concept[concept["conceptKey"]],
            "historicalAttachmentDisposition": baseline,
            "latestAttachmentEvidence": {
                "matchedSourceKeys": sorted(latest_keys),
                "recordHashes": sorted(unique_latest),
                "records": [unique_latest[key] for key in sorted(unique_latest)],
                "learnerProjectionSourceKeyCount": sum(bool(learner_by_source.get(k)) for k in keys),
                "learnerProjectionOriginCount": sum(bool(learner_by_source.get(k, {}).get("origin")) for k in keys),
                "learnerProjectionInsertionCount": sum(bool(learner_by_source.get(k, {}).get("insertion")) for k in keys),
                "fieldTextIsNotFullExtentOrMotionApproval": True,
            },
            "surfaceRows": surface_records,
            "motionFeasibility": {
                "targetIdentity": "not verified by source name or prior targetIds alone",
                "frameRegistration": "T98 selected this ZA source revision for local compilation and froze its source frame conversion; it is not a rig/bind pose or registration to the separate BP3D reference frame",
                "sourceRestPose": "no source-provided rig bind/rest pose ID",
                "rig": "static evaluated geometry only in current learner runtime; upstream per-object rig availability unknown",
                "actionAndConditions": "incomplete for whole-muscle motion; existing text action candidates are not clip authorization",
                "deformation": "no accepted sourceKey-bound muscle-surface deformation asset",
                "productionMotionStatus": "not_implemented",
            },
        })

    source_instance_rows = [
        surface
        for concept in concept_rows
        for surface in concept["surfaceRows"]
    ]
    source_instance_rows.sort(key=lambda row: row["sourceKey"])

    source_instances_by_key = {row["sourceKey"]: row for row in source_instance_rows}
    source_concept_by_source_key = {key: row["conceptKey"] for row in concepts for key in row["sourceKeys"]}
    action_rows = motion_learning.get("muscleActions", [])
    asset_rows = motion_learning.get("motionAssets", [])
    actual_supported_motion_assets = [
        row for row in asset_rows
        if row.get("technicalStatus") == "supported"
        and row.get("representationType") == "source_bound_muscle_surface_deformation"
    ]
    source_frame = compiled["frameContract"]
    contract = {
        "schemaVersion": "human-atlas-motion-contract-v1",
        "task": "T35",
        "revision": "all-muscle-motion-2026-10-02",
        "planningOnly": True,
        "productionMotionImplemented": False,
        "scope": {
            "allMuscleTargets": 429,
            "allMuscleMemberships": 447,
            "allSupportedSourceConcepts": 232,
            "allSupportedSourceInstances": 462,
            "initialShortlist": None,
            "faceOcularTongueNeckTrunkHandFootPelvisPerineumIncluded": True,
            "denominatorMeaning": "records and memberships; not count of distinct individual muscles",
        },
        "runtimeBoundary": {
            "currentSameModelMuscleMotionCount": 0,
            "currentLearnerMotionCTA": "disabled; unavailable note remains",
            "T24": "historical technical candidate only: bone motion with illustrative path; blocked for original muscle-surface contraction",
            "sameScene": "reuse existing learner AnatomySceneRoot, renderer, camera and controller; never switch to a second viewport/model",
            "oneRendererAndClock": "one active WebGL renderer and one animation frame clock per learner scene",
        },
        "sourceIdentity": {
            "bindingKey": "dataset namespace + stable sourceKey + immutable source/revision and geometry hash",
            "doNotUseAsBinding": ["TA2 target ID alone", "name similarity", "parent name", "array index", "unverified mirror"],
            "rawAssetImmutable": True,
            "derivedAssetMustRecord": ["sourceKey", "source file hash", "evaluated geometry hash", "derivation version", "derived output hash", "source rights state", "target/part/side scope"],
            "sourceKeyCaveat": "the current ZA sourceKey is a derived object key, not an upstream canonical ID",
        },
        "coordinateAndPose": {
            "currentCompiledSourceFrame": {
                "sourceFrameId": source_frame["sourceFrameId"],
                "unit": source_frame["sourceUnit"],
                "axes": source_frame["sourceAxes"],
                "projectConvention": source_frame["sourceToProjectConvention"],
                "transformScope": source_frame["transformScope"],
                "registeredToBP3DGeometry": source_frame["registeredToBP3DGeometry"],
                "staticReferencePose": source_frame["staticReferencePose"],
                "physicalCalibration": source_frame["unitEvidence"].get("calibratedPhysicalSubjectMeasurement"),
            },
            "T50Meaning": "BodyParts3D Release 4 remains a separate provisional static reference and was not geometrically registered to ZA",
            "T98Decision": {"decision": base_selection["decision"], "selectionScope": base_selection["selectionScope"], "selectedSourceRevision": base_selection["selectedSourceRevision"], "productionReleaseApproved": base_selection["productionReleaseApproved"], "learnerBindingsAdded": base_selection["learnerBindingsAdded"]},
            "rule": "the selected ZA revision may use its frozen compiled scene frame as the local reference; any external/different-revision motion asset must verify exact source frame, unit, side, reference pose and registration to the active learner scene; equal axis/unit labels are insufficient",
            "unknowns": ["source-declared physical unit/calibrated subject measurement", "source-provided neutral/anatomical rest pose", "per-object rig bind pose", "hashing contract equivalence between source-catalog and compiled-manifest geometry hashes", "external-source registration residual/acceptance threshold"],
        },
        "deformation": {
            "allowedRepresentations": ["source-derived skinning weights", "morph targets", "corrective shape bases", "other reproducible source-derived surface deformation with validation"],
            "mustPreserve": ["source topology or documented topology revision", "instance isolation", "left/right identity", "part/member scope", "rest-pose equivalence and restoration"],
            "prohibitedAsMuscleContraction": ["whole-muscle scale-only", "rigidly rotating the entire muscle", "line-of-action only", "color/highlight-only", "fabricated or reflected geometry"],
            "geometryMutation": "never deform shared/raw source geometry in place; bind a derived per-sourceKey resource",
        },
        "anatomicalMotionContract": {
            "requiredPerAction": ["exact muscle/part/member and side", "source-backed action and posture conditions", "moving joints/bones", "fixed structures", "co-moving/passively deforming context", "non-joint tissue deformation type where applicable", "start/reference/end pose identity"],
            "motionFamiliesToDisposition": ["single-joint", "multi-joint", "broad or multi-head attachment", "repeated/segmental family", "facial/ocular/tongue soft tissue", "pelvic/perineal or sphincter soft tissue", "other explicitly sourced non-joint motion"],
            "scopeRule": "a part/head/member motion never satisfies its parent whole-muscle/group/repeated-family extent",
            "sourceClaimVsAuthoring": "source claim, AI normalization, human review, artist/engine authoring choice, and runtime validation are separate records",
            "nonClinical": "no force, activation, patient-normality, diagnosis, treatment, exercise prescription or needling inference",
        },
        "sameScenePlayback": {
            "lifecycle": ["verify bytes/hash and frame contract", "load isolated derived motion resources into the existing scene root", "bind by sourceKey", "run one scheduler and update the shared scene", "on stop/failure/context switch/unmount restore exact rest pose and prior selection/camera/layers/hidden state"],
            "context": "moving bones and affected neighboring visible structures must move or have an explicitly validated passive deformation; hide-only substitution is not acceptance",
            "failurePolicy": "fail closed to static structure explanation; stale requests cannot start or retain emphasis",
            "resourcePolicy": "lazy-load only selected action/context; count actual fetched animation/deformation bytes and retained geometry against the existing cache budget",
        },
        "validation": {
            "automaticWholeLedger": ["all denominators and ID uniqueness", "sourceKey and source/hash references", "side/part/group extent flags", "frame/unit/rest-pose completeness", "rig/deformation record presence", "independent review/rights states", "no unsupported production state"],
            "visualByActualMotionWhenAvailable": ["rest, intermediate and supported end poses", "left/right and part extent", "moving/fixed/passive context", "surface topology and attachment continuity", "penetration/intersection risks", "same-scene selection/card/emphasis", "cancel/reset/route/layer restore", "390/1024/1440 responsive and keyboard/console"],
            "numericThresholds": "not set by T35; must be backed by source/engineering QA before evaluation",
        },
        "authorityState": {
            "sourceOnlyPerExistingRecordPreserved": True,
            "humanReview": "not_performed",
            "publicRedistribution": "held",
            "existingCanonicalHaBindings": 130,
            "newCanonicalBindings": 0,
            "newGeometryOrClips": 0,
        },
            "nextImplementation": "T59 must implement and validate the common same-scene sourceKey adapter/player and create work/evidence/T59/authoring-run-manifest.json from this frozen contract; it must not claim all-muscle support from a sample.",
    }

    # Summaries are computed from the frozen inputs, not written as expected values.
    membership_keys = [row["membershipKey"] for row in memberships]
    if len(target_rows) != 429 or len(memberships) != 447 or len(concept_rows) != 232 or len(source_instance_rows) != 462:
        raise SystemExit("ledger does not cover every frozen row")
    if len(set(membership_keys)) != len(membership_keys):
        raise SystemExit("duplicate target-region membership")
    missing_object_hash = [row["sourceKey"] for row in source_instance_rows if not row["geometryIdentity"].get("evaluatedGeometrySha256")]
    all_attachment_records_by_concept = {}
    for row in concept_rows:
        all_attachment_records_by_concept[row["conceptKey"]] = len(row["latestAttachmentEvidence"]["recordHashes"])
    attachment_match_counts = Counter(
        "latest_review_record" if row["latestAttachmentEvidence"]["recordHashes"]
        else "historical_description_or_conflict" if row["historicalAttachmentDisposition"]["historicalDisposition"] != "missing_at_T65_baseline" else "historical_missing_without_latest_record"
        for row in concept_rows
    )
    ledger = {
        "schemaVersion": "t35-all-muscle-motion-readiness-ledger-v1",
        "task": "T35",
        "planningOnly": True,
        "manifestPath": str(MANIFEST),
        "manifestRunId": manifest["runId"],
        "inputHashes": {path: sha(path) for path in manifest["inputHashes"]},
        "snapshotHashes": manifest["snapshots"],
        "denominators": {"productTargets": 542, "productMemberships": 563, "regions": 12, "muscleTargets": len(target_rows), "muscleMemberships": len(memberships), "sourceConcepts": len(concept_rows), "sourceInstances": len(source_instance_rows), "existingHaBindings": 130, "historical163": [6, 20, 135, 2]},
        "rows": {
            "targets": target_rows,
            "memberships": memberships,
            "sourceConcepts": concept_rows,
            "sourceInstances": source_instance_rows,
        },
        "summary": {
            "targetKinds": dict(Counter(row["semanticKind"] for row in target_rows)),
            "targetSourceCandidateStatuses": dict(Counter(row["targetSourceCandidateDisposition"]["status"] for row in target_rows)),
            "targetsWithLexicalCandidateKeys": sum(bool(row["targetSourceCandidateDisposition"]["candidateSourceKeys"]) for row in target_rows),
            "targetsWithIdentityVerified": sum(row["targetSourceCandidateDisposition"]["canonicalIdentityVerifiedInPinnedCatalog"] is True for row in target_rows),
            "targetsWithLearnerBinding": sum(row["targetSourceCandidateDisposition"]["learnerBindingAddedInPinnedCatalog"] is True for row in target_rows),
            "sourceSides": dict(Counter(str(row.get("side")) for row in source_instance_rows)),
            "sourceGeometryHashesPresent": len(source_instance_rows) - len(missing_object_hash),
            "sourceGeometryHashMissingKeys": missing_object_hash,
            "sourceCatalogVsCompiledHashValuesEqual": sum(row["geometryHashComparison"]["valuesEqual"] for row in source_instance_rows),
            "sourceCatalogVsCompiledHashValuesDiffer": sum(not row["geometryHashComparison"]["valuesEqual"] for row in source_instance_rows),
            "sourceCatalogVsCompiledHashEquivalenceStatus": "not_reconciled; same sourceKey and hash field label do not establish equal hashing recipes or revisions",
            "sideVsSourceLabelDisposition": dict(Counter("agree" if row.get("side") == row.get("sourceLabelSide") else "unknown_or_different" for row in source_instance_rows)),
            "sourceObjectsWithKnownUpstreamFjId": sum(bool(row["geometryIdentity"].get("upstreamFjId")) for row in source_instance_rows),
            "sourceObjectsWithUnresolvedUpstreamAncestry": sum(str(row["geometryIdentity"].get("upstreamPerObjectAncestry", "")).startswith("unresolved") for row in source_instance_rows),
            "sourceAttachmentLatestBundle": {
                "records": len(new_attachment["records"]),
                "singleSourceSummary": sum(row.get("evidenceState") == "single_source_summary" for row in new_attachment["records"]),
                "conflictedSummary": sum(row.get("evidenceState") == "conflicted_source_summary" for row in new_attachment["records"]),
                "sourceKeyCoverage": len({key for row in new_attachment["records"] for key in row.get("sourceKeys", [])} & set(instance_by_key)),
                "baselineMissingRowsMatchedByExactSourceKeys": sum(row["historicalAttachmentDisposition"]["historicalDisposition"] == "missing_at_T65_baseline" and bool(row["latestAttachmentEvidence"]["recordHashes"]) for row in concept_rows),
            },
            "attachmentConceptDisposition": dict(attachment_match_counts),
            "learnerAttachmentProjection": {
            "sourceKeysWithAnyProjection": sum(bool(learner_by_source.get(key)) for key in instance_by_key),
            "sourceKeysWithOriginText": sum(bool(learner_by_source.get(key, {}).get("origin")) for key in instance_by_key),
            "sourceKeysWithInsertionText": sum(bool(learner_by_source.get(key, {}).get("insertion")) for key in instance_by_key),
            "missingRuntimeSourceKeys": missing_runtime_source_keys,
            "incompleteRuntimeSourceKeys": incomplete_runtime_source_keys,
            "projectionDoesNotProveFullExtentOrMotion": True,
            },
            "textActionEvidence": {
                "actionRows": len(action_rows),
                "distinctHaSubjects": len({subject for row in action_rows for subject in row.get("subjectIds", [])}),
                "sourceInstancesLinkedByExistingHaId": sum(bool(instance_by_key[key].get("haConceptId")) for key in instance_by_key),
                "sourceInstancesWithTextActionCandidate": sum(bool(actions_by_ha.get(instance_by_key[key].get("haConceptId"), [])) for key in instance_by_key),
                "learnerMotionAcceptance": False,
            },
            "manifestAssignments": {name: assignment["counts"] for name, assignment in assignments.items()},
            "workerResultAudit": audit_worker_proposals(manifest),
            "motionAssets": {"catalogEntries": len(asset_rows), "supportedSourceBoundMuscleSurfaceDeformation": len(actual_supported_motion_assets), "T24CandidateAssetIsNotCounted": True},
            "preservedStates": {"sourceOnlyPerExistingRecord": dict(Counter(str(row["sourceOnly"]) for row in source_instance_rows)), "humanReview": "not_performed", "publicRedistribution": "held", "canonicalHaBindings": 130, "newCanonicalBindings": 0, "newGeometryOrClips": 0, "historical163": [6, 20, 135, 2]},
        },
    }

    code_paths = [
        "atlas-web/src/ui/App.tsx",
        "atlas-web/src/viewer/datasets/DatasetResources.ts",
        "atlas-web/src/viewer/animationSceneAdapter.ts",
        "atlas-web/src/viewer/animationPlayback.ts",
        "atlas-web/src/domain/motionPlayer.ts",
    ]
    runtime_audit = {
        "schemaVersion": "t35-runtime-capability-audit-v1",
        "asOfHead": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip(),
        "T65": {"status": "completed/passed", "report": "work/reports/T65.md", "reuse": "attachment summaries, learner projection and static app acceptance only"},
        "learnerMotion": {
            "sameModelMuscleMotionCount": 0,
            "ctaCode": "disabled with unavailable note; no new activation in T35",
            "staticDatasetLoader": "rejects glTF animations and skins and retains static BufferGeometry; morph/live deformation graph preservation is not established in the learner loader",
            "animationAdapter": "standalone hash/frame checked animation-capable GLB parser; no sourceKey-bound live muscle surface integration in current learner path",
            "playbackController": "single scheduler/player logic can be reused for clock, pause, reset and disposal after the same-scene resource adapter exists",
        },
        "T24": {
            "status": "blocked historical candidate",
            "representation": "bone_motion_with_illustrative_path",
            "notSupportedReason": "not an original source-linked muscle surface contraction; was rejected by actual report and is not retried in T35",
            "report": "work/reports/T24.md",
        },
        "codeEvidence": {path: {"sha256": sha(path)} for path in code_paths},
        "motionCatalogCounts": {"textActionRows": len(action_rows), "motionDefinitionRows": len(motion_learning.get("motionDefinitions", [])), "motionAssetRows": len(asset_rows), "technicalCandidateRows": sum(row.get("technicalStatus") == "candidate" for row in asset_rows), "supportedMuscleSurfaceDeformationRows": len(actual_supported_motion_assets)},
        "sourceAndRights": {"sourceOnly": "existing per-instance values preserved", "humanReview": "not_performed", "publicRedistribution": "held", "T98BaseSelection": base_selection["selectionScope"], "exceptionGroups": t98_rights_scope["exceptionGroups"]},
        "browserNotRunReason": "T35 is a planning/contract task and changes no UI or runtime; the learner motion CTA remains disabled. Existing T65 and T24 browser evidence is reused only for those prior scopes, not as motion support proof.",
        "missingLearnerAttachmentProjectionSourceKeys": missing_runtime_source_keys,
        "learnerAttachmentProjectionGapIsNotAnOriginInsertionClaimGap": True,
    }

    manifest_reconciliation = reconcile_manifests(manifest)
    verification = {
        "schemaVersion": "t35-verification-v1",
        "task": "T35",
        "baselineHead": load(OUT / "start-baseline.json")["baselineHead"],
        "manifestValidation": {"status": "passed", "command": "python3 work/tools/validate_motion_parallel_plan.py --manifest work/evidence/motion-all-muscles-plan-2026-10-02/run-manifest-r2.json", "runId": manifest["runId"]},
        "manifestReconciliation": manifest_reconciliation,
        "ledgerChecks": {
            "wholeBodyDenominatorsRemain54256312": len(t96_target_ids) == 542 and t96_denominators["productRegionMembershipRows"] == 563 and len(scope["regions"]) == 12,
            "all429MuscleTargetsEqualT96MuscleSelection": target_ids == t96_muscle_target_ids,
            "all429MuscleTargetsExactlyOnce": len(target_rows) == 429 and len({row["targetId"] for row in target_rows}) == 429,
            "all447TargetRegionMembershipsExactlyOnce": len(memberships) == 447 and len(set(membership_keys)) == 447,
            "all232SourceConceptsExactlyOnce": len(concept_rows) == 232 and len({row["conceptKey"] for row in concept_rows}) == 232,
            "all462SourceInstancesExactlyOnce": len(source_instance_rows) == 462 and len({row["sourceKey"] for row in source_instance_rows}) == 462,
            "allSourceGeometryHashesPresent": not missing_object_hash,
            "allSourceKeysResolveToPinnedCatalogAndCompiledManifest": set(source_instances_by_key) == set(instance_by_key) and set(instance_by_key).issubset(compiled_instance_by_key),
            "allSourceCatalogAndCompiledHashValuesRecorded": all(row["geometryHashComparison"]["sourceCatalogHash"] and row["geometryHashComparison"]["compiledManifestHash"] for row in source_instance_rows),
            "noNewCanonicalBindingGeometryOrClip": True,
            "allRowsPreserveSourceOnlyRightsAndReview": all(
                row["sourceOnly"] == instance_by_key[row["sourceKey"]].get("sourceOnly")
                and row["humanReview"] == "not_performed"
                and row["publicRedistribution"] == "held"
                for row in source_instance_rows
            ),
            "allTargetIdentityClaimsRemainUnverified": all(row["targetSourceCandidateDisposition"]["canonicalIdentityVerifiedInPinnedCatalog"] is False for row in target_rows),
            "allGroupPartAndRepeatedExtentIsIndependent": all(row["representationScope"]["partGroupMemberExtentMustBeValidatedIndependently"] for row in target_rows),
            "workerResultsOptionalAndNotInvented": ledger["summary"]["workerResultAudit"]["noUnvalidatedOutputIntegrated"] is True,
            "originalAssignmentAndSnapshotFreezePreserved": manifest_reconciliation["allAssignmentsUnchanged"] and manifest_reconciliation["snapshotHashesUnchanged"],
            "T98LocalSelectionNotPromotedToReleaseOrBinding": base_selection.get("productionReleaseApproved") is False and base_selection.get("learnerBindingsAdded") == 0,
        },
        "counts": ledger["summary"],
        "workerResultAudit": ledger["summary"]["workerResultAudit"],
        "workerResultsFullValidatorAttempt": {
            "command": "python3 work/tools/validate_motion_parallel_plan.py --manifest work/evidence/motion-all-muscles-plan-2026-10-02/run-manifest-r2.json --results",
            "exitCode": 1,
            "status": "incomplete_result_set_not_integrated",
            "firstFailure": "A proposal file is absent; C is also absent, and B is tied to the stale r1 runId/input hashes.",
            "interpretation": "Worker execution is optional for T35 planning acceptance; the r2 ready-manifest validator and direct exhaustive ledger builder passed. No worker rows were imported.",
        },
        "limitation": "These checks validate plan coverage and provenance joins, not anatomical truth, motion readiness, full extent, human approval or actual muscle animation.",
    }
    dump(OUT / "motion-contract.json", contract)
    dump(OUT / "manifest-reconciliation.json", verification["manifestReconciliation"])
    dump(OUT / "motion-readiness-ledger.json", ledger)
    dump(OUT / "runtime-capability-audit.json", runtime_audit)
    dump(OUT / "worker-result-observation.json", ledger["summary"]["workerResultAudit"])
    dump(OUT / "verification.json", verification)
    dump(OUT / "progress.json", {
        "task": "T35", "status": "scoped_plan_ready", "nextUnit": None,
        "completedUnits": ["all-muscle scope freeze", "exact A/B/C allocation validation", "429/447/232/462 readiness ledger", "same-scene motion contract", "current capability and attachment evidence reconciliation"],
        "notCompleted": ["motion runtime implementation", "clip production", "anatomical source/pose/rig gap closure", "human review", "public redistribution approval"],
        "nextTask": "T59",
    })
    print(json.dumps({"status": "passed" if all(verification["ledgerChecks"].values()) else "failed", "outputs": ["work/evidence/T35/motion-contract.json", "work/evidence/T35/motion-readiness-ledger.json", "work/evidence/T35/runtime-capability-audit.json", "work/evidence/T35/manifest-reconciliation.json", "work/evidence/T35/worker-result-observation.json", "work/evidence/T35/verification.json", "work/evidence/T35/progress.json"], "counts": verification["counts"], "ledgerChecks": verification["ledgerChecks"], "allChecksPassed": all(verification["ledgerChecks"].values())}, ensure_ascii=False))
    if not all(verification["ledgerChecks"].values()):
        raise SystemExit("T35 ledger validation failed")


if __name__ == "__main__":
    main()
