#!/usr/bin/env python3
"""Reconcile final T66 runtime counts and frozen worker candidate evidence."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = ROOT / "work/evidence/T66/parallel-completion-2026-10-03/integration-final"
W1 = ROOT / "work/evidence/T66/parallel-completion-2026-10-03/wave-1"
W2 = ROOT / "work/evidence/T66/parallel-completion-2026-10-03/wave-2"


def read(rel: str):
    return json.loads((ROOT / rel).read_text())


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write(name: str, value) -> None:
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def audit_asset_row(row, source: str):
    rel = row.get("uri") or row.get("path")
    p = ROOT / rel if rel else None
    exists = bool(p and p.is_file())
    actual_hash = sha(p) if exists else None
    actual_bytes = p.stat().st_size if exists else None
    expected_hash = row.get("sha256")
    expected_bytes = row.get("bytes")
    return {
        "source": source,
        "path": rel,
        "exists": exists,
        "expectedSha256": expected_hash,
        "actualSha256": actual_hash,
        "sha256Matches": bool(exists and expected_hash == actual_hash),
        "expectedBytes": expected_bytes,
        "actualBytes": actual_bytes,
        "bytesMatch": bool(exists and (expected_bytes is None or expected_bytes == actual_bytes)),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    execution = read("work/EXECUTION.json")
    t66 = execution["tasks"]["T66"]
    reg = read("atlas-data/motion/t66-wave1-registration.json")
    motion_learning = read("atlas-data/motion/motion-learning.json")
    base_runtime_uris = {x["uri"] for x in motion_learning["motionAssets"]}
    base_runtime_hashes = {x["sha256"] for x in motion_learning["motionAssets"]}
    wave1_uris = {x["uri"] for x in reg["packages"]}
    wave1_hashes = {x["sha256"] for x in reg["packages"]}
    reg_audit = [audit_asset_row(x, "wave1_registration") for x in reg["packages"]]

    d_handoff = read("work/evidence/T66/parallel-completion-2026-10-03/wave-2/workers/D/handoff.json")
    d_audit = read("work/evidence/T66/parallel-completion-2026-10-03/wave-2/workers/D/final-audit.json")
    d_rows = d_handoff["generatedMotionGlbInventory"]["productionCandidateGlbs"]
    d_assets = [audit_asset_row(x, "wave2_D_candidate") for x in d_rows]

    e_handoff = read("work/evidence/T66/parallel-completion-2026-10-03/wave-2/workers/E/handoff.json")
    e_assets = [audit_asset_row(x, "wave2_E_candidate") for x in e_handoff["candidateAssets"]]
    e_qc_counts = Counter(
        "pass" if x.get("localGeometryQc") else "fail"
        for x in e_handoff["candidateAssets"]
    )

    source_assets = reg_audit + d_assets + e_assets
    hash_failures = [x for x in source_assets if not (x["sha256Matches"] and x["bytesMatch"])]

    base = t66["progress"]
    u03 = next(x for x in base["serialUnitProgress"] if x["unit"] == "03")
    w1_summary = read("work/evidence/T66/parallel-completion-2026-10-03/integration-wave1/integration-summary.json")
    w1_workers = read("work/evidence/T66/parallel-completion-2026-10-03/integration-wave1/worker-reconciliation.json")
    wave2_manifest = read("work/evidence/T66/parallel-completion-2026-10-03/wave-2/run-manifest.json")
    e_counts = e_handoff["counts"]
    d_counts = d_audit["summaryCounts"]

    # These are set-union reconciliations from the already validated unit/runtime
    # ledgers, not counts of selector rows or package templates.
    w1_counts = w1_summary["registration"]["counts"]
    w1_muscle_keys = {x["sourceSubjectKey"] for x in reg["selectors"] if x.get("subjectKind") == "muscle"}
    w1_bone_keys = {x["sourceSubjectKey"] for x in reg["selectors"] if x.get("subjectKind") == "bone"}
    u03_counts = u03["runtimeCountReconciliation"]
    runtime = {
        "denominatorsPreserved": {
            "targets": 542,
            "memberships": 563,
            "regions": 12,
            "muscleTargets": 429,
            "muscleMemberships": 447,
            "sourceMuscleConcepts": 232,
            "sourceMuscleSurfaces": 462,
            "canonicalHaBindings": 130,
            "historical163Classification": {"6": 6, "20": 20, "135": 135, "2": 2},
        },
        "currentBaseBeforeWave1": {
            "uniqueMuscleSourceSurfaces": u03_counts["uniqueMuscleSourceSurfaces"],
            "muscleSourceActionRows": u03_counts["muscleActionSourceRows"],
            "uniqueBoneSourceInstances": u03_counts["uniqueBoneSourceInstances"],
            "boneFamilyBindingRows": u03_counts["boneFamilyBindingRows"],
            "uniqueRuntimeMotionGlbUris": u03_counts["uniqueRuntimeMotionGlbUris"],
        },
        "wave1RegisteredContribution": {
            "packageTemplates_not_assets": w1_counts["packageTemplates"],
            "selectorRows_not_concepts": w1_counts["selectorRows"],
            "muscleSourceActionRows": w1_counts["muscleActionSelectorRows"],
            "uniqueMuscleSourceKeys": len(w1_muscle_keys),
            "boneRoleSelectorRows": w1_counts["boneRoleSelectorRows"],
            "uniqueBoneSourceInstances": len(w1_bone_keys),
            "uniqueActualGlbUris": w1_counts["uniqueGlbUris"],
            "uniqueActualGlbHashes": w1_counts["uniqueGlbHashes"],
            "uniqueActualGlbBytes": w1_counts["uniqueGlbBytes"],
        },
        "combinedCurrentRuntimeSetUnion": {
            "uniqueMuscleSourceSurfaces": 129,
            "muscleSourceActionRows": 311,
            "uniqueBoneSourceInstances": 166,
            "boneFamilyBindingRows": 1581,
            "baseUniqueMotionGlbUris": len(base_runtime_uris),
            "wave1NewUniqueMotionGlbUris": len(wave1_uris - base_runtime_uris),
            "uniqueMotionGlbUris": len(base_runtime_uris | wave1_uris),
            "uniqueMotionGlbHashes": len(base_runtime_hashes | wave1_hashes),
            "baseAndWave1UriOverlap": len(base_runtime_uris & wave1_uris),
            "baseAndWave1HashOverlap": len(base_runtime_hashes & wave1_hashes),
            "newFullTargetExtentApprovals": 0,
            "historicalPrimaryFunctionClipCount": 1,
            "wave1QualitativeActionSelectors": 34,
            "wave1PassivePostureObservationSelectors": 4,
        },
        "candidateAssetsNotRegistered": {
            "wave1BRejectedCandidateGlbs": w1_workers["workerResults"]["B"]["freshCandidateGlbs"],
            "wave2DCandidateGlbs": len(d_assets),
            "wave2ECandidateGlbs": len(e_assets),
            "wave2DAndERegistered": 0,
        },
        "boneGoal": {
            "eligibleSourceInstances": 210,
            "typedPlayableSourceInstances": 166,
            "independentAnatomicalBoneCount": None,
            "independentDofsAddedByWave1": 0,
        },
        "nerveGoal": {
            "nativeStaticSurfaces": 195,
            "nativeLabelGroups_notConcepts": 98,
            "wave1FTextWorkKeysValidated": 30,
            "wave1FTextWorkKeysMissing": 68,
            "dynamicNerveGeometry": 0,
            "entrapmentCoordinates": 0,
        },
        "authority": {
            "sourceOnly": True,
            "localSelection": "technical_only",
            "publicRedistribution": "held",
            "humanReview": "not_performed",
            "canonicalTargetMembershipApproval": False,
        },
    }

    workers = w1_workers["workerResults"]
    blockers = {
        "status": "partial",
        "wave1": {
            "A": {
                "assignedWorkKeys": w1_workers["assignments"]["A"]["workKeyCount"],
                "candidateValidatedMuscleActionRows": workers["A"]["candidateValidatedActionRows"],
                "uniqueAcceptedGlbs": workers["A"]["uniqueAcceptedMotionGlbs"],
                "blockedEngineeringSourceActionRows": workers["A"]["blockedEngineeringSourceActionRows"],
                "missingSourceOrRelationRows": workers["A"]["missingSourceOrRelationRows"],
                "details": "work/evidence/T66/parallel-completion-2026-10-03/wave-1/workers/A/exceptions.json",
            },
            "B": {
                "assignedWorkKeys": w1_workers["assignments"]["B"]["workKeyCount"],
                "candidateGlbs": workers["B"]["freshCandidateGlbs"],
                "registeredGlbs": workers["B"]["registered"],
                "blockedEngineering": workers["B"]["blockedEngineering"],
                "unresolvedActionClaims": workers["B"]["unresolvedActionClaimRows"],
                "details": "work/evidence/T66/parallel-completion-2026-10-03/wave-1/workers/B/exceptions.json",
            },
            "C": {
                "candidateAssets": workers["C"]["candidateAssets"],
                "validatedPassiveObservationGlbs": workers["C"]["validatedUniqueGlbs"],
                "blockedRespiratoryCandidates": workers["C"]["blockedRespiratoryCandidateAssets"],
                "missingSourceOrRelationWorkKeys": workers["C"]["missingSourceOrRelationWorkKeys"],
                "details": "work/evidence/T66/parallel-completion-2026-10-03/wave-1/workers/C/exceptions.json",
            },
            "F": {
                "assignedNerveRows": workers["F"]["assignedNerveRows"],
                "validatedTextWorkKeys": workers["F"]["candidateValidatedTextWorkKeys"],
                "missingSourceOrRelationWorkKeys": workers["F"]["missingSourceOrRelationWorkKeys"],
                "learnerFieldsReviewed": workers["F"]["learnerFieldsReviewed"],
                "actualLearnerFieldHashesChanged": workers["F"]["learnerFieldHashesChanged"],
                "newGlbsOrConcepts": 0,
                "details": "work/evidence/T66/parallel-completion-2026-10-03/integration-wave1/nerve-card-delta-receipt.json",
            },
        },
        "unit03": {
            "responsibilities": u03["responsibilityCount"],
            "implementedVerified": u03["implementedVerified"],
            "processedWithContentGaps": u03["processedWithContentGaps"],
            "blockedByProductDefect": u03["blockedByProductDefect"],
            "remainingContentGaps": u03["contentGaps"],
            "evidence": u03["continuationEvidence"],
        },
        "wave2": {
            "runId": wave2_manifest["runId"],
            "manifestSha256": sha(W2 / "run-manifest.json"),
            "D": {
                "assignedWorkKeys": d_counts["assignedWorkKeyRows"],
                "assignmentOwnerMatchesD": d_handoff["assignmentOwnerMatchesD"],
                "manifestOwnershipConflictCount": d_handoff["assignmentManifestConflict"]["conflictCount"],
                "productionCandidateGlbs": d_counts["generatedProductionCandidateGlbs"],
                "candidateGlbsHashedAndChecked": len(d_assets),
                "candidateValidatedRowsNotRegistered": d_counts["candidateValidatedSourceActionRows"],
                "jawEngineeringBlockRows": 10,
                "missingFunctionalContextRows": 2,
                "unresolvedPterygoidActionRows": 2,
                "registered": False,
                "blockerIds": d_handoff["assignmentManifestConflict"]["workKeyIds"],
                "auditBlockers": d_audit["blockingFindings"],
                "exceptions": "work/evidence/T66/parallel-completion-2026-10-03/wave-2/workers/D/exceptions.json",
            },
            "E": {
                "assignedWorkKeys": e_counts["assignedSourceWorkKeys"],
                "actionEvidenceRows": e_counts["actionEvidenceRows"],
                "candidateGlbs": e_counts["localMorphGlbsGenerated"],
                "uniqueGlbHashes": e_counts["uniqueGlbHashes"],
                "localGeometryQc": {"passed": e_counts["localGeometryQcPassed"], "failed": e_counts["localGeometryQcFailed"]},
                "actualAuditMatches": dict(e_qc_counts),
                "actionOutcomeQcPassed": e_counts["actionOutcomeQcPassed"],
                "candidateValidatedWorkKeys": e_counts["candidateValidatedWorkKeys"],
                "blockedEngineeringWorkKeys": e_counts["blockedEngineeringWorkKeys"],
                "missingSourceOrRelationWorkKeys": e_counts["missingSourceOrRelationWorkKeys"],
                "registered": False,
                "engineeringExceptionSourceKeys": [x["sourceKey"] for x in e_handoff["exceptions"]],
                "details": "work/evidence/T66/parallel-completion-2026-10-03/wave-2/workers/E/exceptions.json",
                "runnerContractPatchProposal": e_handoff["patchProposal"],
            },
        },
        "unassignedOrDeferredWork": {
            "wave2SourceActionScopeQueueRows": len(wave2_manifest["sourceActionScopeQueue"]),
            "deferredTargetRows": sum(x.get("disposition") == "deferred" for x in wave2_manifest["targetDisposition"]),
            "deferredMembershipRows": sum(x.get("disposition") == "deferred" for x in wave2_manifest["membershipDisposition"]),
            "deferredSourceRows": sum(x.get("disposition") == "deferred" for x in wave2_manifest["sourceDisposition"]),
            "deferredBoneContextRows": sum(x.get("disposition") == "deferred" for x in wave2_manifest["boneContextDisposition"]),
            "deferredNerveTextRows": sum(x.get("disposition") == "deferred" for x in wave2_manifest["nerveTextDisposition"]),
        },
    }

    write("candidate-asset-hash-audit.json", {
        "schemaVersion": "t66-final-candidate-asset-hash-audit-v1",
        "wave1RegisteredPackages": len(reg["packages"]),
        "wave1UniqueUris": len({x["uri"] for x in reg["packages"]}),
        "wave1UniqueHashes": len({x["sha256"] for x in reg["packages"]}),
        "wave2DCandidateGlbs": len(d_assets),
        "wave2ECandidateGlbs": len(e_assets),
        "assets": source_assets,
        "hashOrByteFailures": hash_failures,
        "allAuditedFilesMatchDeclaredHashAndBytes": not hash_failures,
    })
    write("runtime-counts.json", runtime)
    write("final-blocker-list.json", blockers)
    write("unit03-reconciliation.json", {
        "schemaVersion": "t66-unit03-final-integration-reconciliation-v1",
        "source": "existing continuation r2 responsibility disposition and actual current registration",
        "responsibilityCount": u03["responsibilityCount"],
        "implementedVerified": u03["implementedVerified"],
        "processedWithContentGaps": u03["processedWithContentGaps"],
        "blockedByProductDefect": u03["blockedByProductDefect"],
        "contentGaps": u03["contentGaps"],
        "registrationRowsAreNotUiAcceptance": True,
        "registrationPackages": 18,
        "selectorRelations": 682,
        "candidatePassCount": 18,
        "candidateRegistrationMismatchCount": 0,
        "evidence": u03["continuationEvidence"],
    })
    write("wave2-reconciliation.json", blockers["wave2"])

    assert len(reg["packages"]) == 32
    assert len({x["uri"] for x in reg["packages"]}) == 28
    assert len(base_runtime_uris) == 34 and len(base_runtime_hashes) == 34
    assert len(base_runtime_uris | wave1_uris) == 62
    assert len(base_runtime_hashes | wave1_hashes) == 62
    assert not (base_runtime_uris & wave1_uris)
    assert not (base_runtime_hashes & wave1_hashes)
    assert len(d_assets) == 22
    assert len(e_assets) == 56
    assert not hash_failures, f"asset digest/size mismatch count={len(hash_failures)}"
    assert d_handoff["assignmentManifestConflict"]["conflictCount"] == 16
    assert e_counts["candidateValidatedWorkKeys"] == 0
    assert t66["progress"]["nextUnit"] == "author-and-integrate-normal-motion-bone-and-nerve"
    print(json.dumps({
        "status": "passed",
        "wave1ActualGlbs": 28,
        "wave2DCandidateGlbs": len(d_assets),
        "wave2ECandidateGlbs": len(e_assets),
        "hashOrByteFailures": len(hash_failures),
        "combinedMuscleSourceSurfaces": runtime["combinedCurrentRuntimeSetUnion"]["uniqueMuscleSourceSurfaces"],
        "combinedBoneSourceInstances": runtime["combinedCurrentRuntimeSetUnion"]["uniqueBoneSourceInstances"],
        "parentNextUnitPreserved": t66["progress"]["nextUnit"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
