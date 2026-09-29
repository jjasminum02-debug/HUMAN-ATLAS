#!/usr/bin/env python3
"""Build a T100 coverage view without converting name candidates into identity claims."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "work/evidence/T100"
INPUTS = {
    "t96Freeze": "work/evidence/T96/freeze-summary.json",
    "t96Validation": "work/evidence/T96/validation-result.json",
    "t98Targets": "work/evidence/T98/target-reconciliation-t98.json",
    "t98SourceCatalog": "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json",
    "t99CompiledManifest": "atlas-data/source-cache/datasets/za/compiled/manifest.json",
    "t99CompiledReceipt": "work/evidence/T99/compiled-receipt.json",
    "t99Validation": "work/evidence/T99/validation.json",
}


def read_json(path: str):
    return json.loads((ROOT / path).read_text())


def sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main() -> None:
    inputs = {key: read_json(path) for key, path in INPUTS.items()}
    freeze = inputs["t96Freeze"]
    validation96 = inputs["t96Validation"]
    target_source = inputs["t98Targets"]
    source_catalog = inputs["t98SourceCatalog"]
    runtime = inputs["t99CompiledManifest"]
    receipt = inputs["t99CompiledReceipt"]
    validation99 = inputs["t99Validation"]

    targets = target_source["targets"]
    overlays = source_catalog["targetOverlay"]
    objects = source_catalog["objects"]
    target_by_id = {row["targetId"]: row for row in targets}
    overlay_by_id = {row["targetId"]: row for row in overlays}
    object_by_key = {row["sourceKey"]: row for row in objects}
    assert len(target_by_id) == 542 and len(overlay_by_id) == 542
    assert len(objects) == 960 and len(runtime["instances"]) == 960
    assert len(target_by_id) == len(targets)
    assert set(target_by_id) == set(overlay_by_id)

    source_class_counts = Counter(row["status"] for row in overlays)
    expected_classes = {
        "lexical_group_or_other_representation_needs_reconciliation": 91,
        "lexical_candidate_with_evaluated_geometry": 339,
        "no_ZA_lexical_candidate": 112,
    }
    assert dict(source_class_counts) == expected_classes
    assert source_catalog["targetStatusCounts"] == expected_classes

    by_region: dict[str, list[dict]] = {}
    target_rows = []
    for target in targets:
        target_id = target["targetId"]
        overlay = overlay_by_id[target_id]
        candidate_keys = list(overlay.get("candidateSourceKeys", []))
        candidates = [object_by_key[key] for key in candidate_keys if key in object_by_key]
        row = {
            "targetId": target_id,
            "sourceTa2Id": target.get("sourceTa2Id"),
            "semanticKind": target.get("semanticKind"),
            "latin": target.get("latin"),
            "english": target.get("english"),
            "primaryOwner": target["primaryOwner"],
            "regionIds": list(target["regionIds"]),
            "sourceCandidateStatus": overlay["status"],
            "candidateSourceKeys": candidate_keys,
            "candidateObjectLabels": [candidate["name"] for candidate in candidates],
            "candidateSourceLabelSides": [candidate.get("sourceLabelSide") for candidate in candidates],
            "candidateListTruncated": bool(target.get("zAnatomyCandidateTruncated", False)),
            "canonicalIdentityVerified": bool(overlay.get("canonicalIdentityVerified", False)),
            "learnerBindingAdded": bool(overlay.get("learnerBindingAdded", False)),
            "identityStatus": target.get("identityStatus"),
            "geometryStatus": target.get("geometryStatus"),
            "framePoseStatus": target.get("framePoseStatus"),
            "localUseRights": target.get("localUseRights"),
            "redistributionRights": target.get("redistributionRights"),
            "humanReview": target.get("humanReview"),
            "threeNameLearnerCard": "unavailable_no_verified_source_crosswalk",
            "selectionEligibility": "blocked_identity_unresolved",
        }
        target_rows.append(row)
        for region_id in row["regionIds"]:
            by_region.setdefault(region_id, []).append(row)

    region_rows = []
    freeze_rows = freeze["regions"]
    region_records = target_source["freeze"]["regionRows"]
    record_by_id = {row["regionId"]: row for row in region_records}
    for region_id, label in [
        ("head", "머리"), ("neck", "목"), ("back", "등"),
        ("shoulder-scapular", "어깨·어깨뼈"), ("thorax", "가슴우리"),
        ("abdomen-lumbar", "배·허리"), ("pelvis-perineum", "골반·샅"),
        ("gluteal-hip", "볼기·깊은엉덩이"), ("thigh", "넙다리"),
        ("leg", "종아리"), ("foot", "발"), ("upper-limb", "팔·손"),
    ]:
        assigned = by_region.get(region_id, [])
        primary = [row for row in targets if row["primaryOwner"] == region_id]
        status_counts = Counter(row["sourceCandidateStatus"] for row in assigned)
        info = record_by_id[region_id]
        package_path = info["packagePath"]
        package_exists = (ROOT / package_path).is_file()
        package_sha = sha256(package_path) if package_exists else None
        region_rows.append({
            "regionId": region_id,
            "labelKo": label,
            "primaryTargetCount": len(primary),
            "membershipTargetCount": len(assigned),
            "candidateStatusCounts": {key: status_counts.get(key, 0) for key in expected_classes},
            "exactSourceIdentityTargets": sum(bool(row["canonicalIdentityVerified"]) for row in assigned),
            "geometryJoinedToTarget": sum(row["geometryStatus"] == "verified_exact_target_geometry" for row in assigned),
            "verifiedThreeNameCards": sum(row["threeNameLearnerCard"] == "verified" for row in assigned),
            "typedLearnerSelections": sum(row["selectionEligibility"] == "eligible" for row in assigned),
            "allTargetIds": [row["targetId"] for row in assigned],
            "package": {
                "historicalTaskId": info["taskId"],
                "path": package_path,
                "expectedSha256": info["packageSha256"],
                "observedSha256": package_sha,
                "hashMatches": package_sha == info["packageSha256"],
                "retainedAsHistory": True,
            },
            "sourceObservation": "candidate labels/keys are inspectable in T98/T99 engineering evidence; not attached to this product region",
            "coverageState": "held_unresolved_target_to_source_identity",
        })

    assert len(region_rows) == 12
    assert sum(row["primaryTargetCount"] for row in region_rows) == 542
    assert sum(row["membershipTargetCount"] for row in region_rows) == 563
    assert all(row["package"]["hashMatches"] for row in region_rows)
    assert all(row["exactSourceIdentityTargets"] == 0 for row in region_rows)

    kind_counts = Counter(row["kind"] for row in objects)
    runtime_counts = Counter(row["kind"] for row in runtime["instances"])
    assert kind_counts == {
        "muscle_surface_or_part": 509,
        "skeletal_surface": 277,
        "musculoskeletal_accessory": 174,
    }
    assert runtime_counts == kind_counts
    holds = Counter((row.get("canonicalConceptId"), row.get("learnerBinding"), row.get("defaultLearnerVisible"), row.get("appDisplayRights"), row.get("publicRedistribution"), row.get("humanReview")) for row in objects)
    assert holds == Counter({(None, "source_only_unbound", False, "held_not_approved_by_this_task", "held", "not_performed"): 960})

    compiled_dir = ROOT / "atlas-data/source-cache/datasets/za/compiled"
    chunk_integrity = []
    for chunk in runtime["chunks"]:
        path = compiled_dir / Path(chunk["url"]).name
        exists = path.is_file()
        observed_sha = hashlib.sha256(path.read_bytes()).hexdigest() if exists else None
        observed_bytes = path.stat().st_size if exists else None
        chunk_integrity.append({
            "id": chunk["id"],
            "path": str(path.relative_to(ROOT)),
            "expectedSha256": chunk["sha256"],
            "observedSha256": observed_sha,
            "expectedBytes": chunk["bytes"],
            "observedBytes": observed_bytes,
            "valid": observed_sha == chunk["sha256"] and observed_bytes == chunk["bytes"],
        })
    assert len(chunk_integrity) == 10 and all(row["valid"] for row in chunk_integrity)

    work_unit_counts = freeze["workUnits"]
    assert len(work_unit_counts) == 12 and sum(work_unit_counts.values()) == 59 and max(work_unit_counts.values()) <= 12
    internal_units = []
    for region in region_rows:
        legacy_id = region["package"]["historicalTaskId"]
        units = work_unit_counts[legacy_id]
        region_targets = [row["targetId"] for row in targets if row["primaryOwner"] == region["regionId"]]
        batches = [region_targets[index:index + 10] for index in range(0, len(region_targets), 10)]
        for index, batch in enumerate(batches, start=1):
            internal_units.append({
                "unitId": f"{legacy_id}-U{index:02d}",
                "absorbedHistoricalTask": legacy_id,
                "regionId": region["regionId"],
                "targetIds": batch,
                "targetCount": len(batch),
                "maximumConcepts": 10,
                "status": "blocked_identity_crosswalk_missing",
                "sourcePackageReference": region["package"]["path"],
            })

    assert all(unit["targetCount"] <= 10 for unit in internal_units)
    assert len({target_id for unit in internal_units for target_id in unit["targetIds"]}) == 542
    assert all(item["canonicalIdentityVerified"] is False and item["learnerBindingAdded"] is False for item in target_rows)

    matrix = {
        "schemaVersion": 1,
        "task": "T100",
        "status": "partial_blocked_before_source_to_product_integration",
        "revision": "T100-target-coverage-v1",
        "inputHashes": {key: sha256(path) for key, path in INPUTS.items()},
        "sourceSnapshot": {
            "namespace": runtime["namespace"],
            "revision": runtime["revision"],
            "adapterRevision": runtime.get("adapterRevision"),
            "sourceHash": runtime.get("sourceHash"),
            "catalogHash": runtime.get("catalogHash"),
            "compiledManifestSha256": sha256(INPUTS["t99CompiledManifest"]),
            "compiledObjectInstances": len(runtime["instances"]),
            "sourceObjects": len(objects),
            "kindCounts": dict(kind_counts),
            "uniqueResources": receipt["metrics"]["uniqueResources"],
            "chunkCount": len(runtime["chunks"]),
            "chunkIntegrity": chunk_integrity,
            "performance": receipt["metrics"],
            "budgetPass": receipt["budgetPass"],
            "note": "T99 technical source compiler metrics; not learner draw cost, mobile FPS, or T100 scene integration evidence.",
        },
        "targetDenominator": {
            "frozenTargets": len(targets),
            "primaryOwnerAssignments": 542,
            "regionMemberships": 563,
            "individualMuscleDenominator": None,
            "targetStatusCounts": dict(source_class_counts),
            "exactSourceIdentityTargets": sum(bool(row.get("canonicalIdentityVerified")) for row in overlays),
            "exactTargetGeometryJoins": 0,
            "learnerBindingsAdded": sum(bool(row.get("learnerBindingAdded")) for row in overlays),
            "verifiedThreeNameLearnerCards": 0,
            "typedLearnerSelections": 0,
            "sourceObservationSelectableInProduct": 0,
            "defaultVisibleSourceObjects": sum(bool(row.get("defaultLearnerVisible")) for row in objects),
            "selectionGate": "blocked_until_exact_identity_crosswalk_and_per-target_display_eligibility",
        },
        "regionCoverage": region_rows,
        "targets": target_rows,
        "internalWorkUnits": {
            "absorbedT105ToT109": "T98/T99 inventory and source holds preserved; no separate fetch task reopened.",
            "absorbedT110ToT121": "T96 frozen region packages retained as historical inputs; target concepts are grouped into <=10-target T100 work units.",
            "absorbedT166": "core observation-control implementation remains under T100; no extra task is started.",
            "legacyPackageUnitCounts": work_unit_counts,
            "legacyPackageUnitTotal": sum(work_unit_counts.values()),
            "boundedT100Units": internal_units,
        },
        "requiredHoldState": {
            "sourceOnly": True,
            "learnerBinding": "none_added",
            "defaultVisible": False,
            "localUseRights": "held_not_approved_by_T100",
            "publicRedistribution": "held",
            "humanReview": "not_performed",
            "faceExpressionMotion": "disabled",
            "newAnimation": "none",
            "nervesInRuntime": False,
            "unverifiedExcelClaimsInRuntime": False,
            "bp3dAndZaCoDisplayedTogether": False,
        },
        "unresolvedGate": {
            "nextUnit": "resolve-z-anatomy-source-to-canonical-concept-and-12-region-crosswalk",
            "blockers": [
                "T98 has 0 exact TA2/canonical target to Z-Anatomy object joins; all 542 identity states remain unresolved.",
                "No verified 12-region membership overlay exists for the 960 source objects; 563 frozen target memberships cannot be projected by name or bounds.",
                "No per-target Korean/English/Latin three-name overlay or typed learner selection is authorized by the current evidence.",
                "All 960 objects remain default-hidden with appDisplayRights held, public redistribution held, and humanReview not_performed.",
            ],
            "evidenceNeeded": [
                "exact concept/part/side-to-source object key crosswalk with source locator and hash for each target",
                "reviewed mapping of each source object to primary and secondary product regions, including group/part/variant policy",
                "field-backed display-name crosswalk and per-object local display eligibility evidence",
                "human anatomy review for learner binding; source rights remain an independent gate",
            ],
        },
    }
    (OUT / "region-coverage-matrix.json").write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n")

    checks = {
        "frozenTargetCount542": len(targets) == 542,
        "membershipCount563": sum(len(row["regionIds"]) for row in targets) == 563,
        "twelveRegions": len(region_rows) == 12,
        "allHistoricalRegionPackageHashesMatch": all(row["package"]["hashMatches"] for row in region_rows),
        "candidateClasses91_339_112": dict(source_class_counts) == expected_classes,
        "zeroExactZaTargetIdentity": matrix["targetDenominator"]["exactSourceIdentityTargets"] == 0,
        "zeroZaLearnerBindings": matrix["targetDenominator"]["learnerBindingsAdded"] == 0,
        "all960RemainSourceOnlyHiddenAndHeld": sum(holds.values()) == 960,
        "actualCompiledManifestMatchesT99ReceiptAndValidation": runtime["revision"] == receipt["revision"] and sha256(INPUTS["t99CompiledManifest"]) == validation99["compiledManifestSha256"],
        "allTenCompiledChunksMatchManifestHashesAndBytes": len(chunk_integrity) == 10 and all(row["valid"] for row in chunk_integrity),
        "T99ValidationPassed": validation99.get("passed") is True,
        "T96FreezeHadNoHumanReviewPromotion": validation96.get("humanReviewPromotions") == 0,
        "internalWorkUnitConceptsAtMost10": all(unit["targetCount"] <= 10 for unit in internal_units),
        "all542TargetsInInternalUnits": len({target_id for unit in internal_units for target_id in unit["targetIds"]}) == 542,
        "sourceCostsNotMisreportedAsT100Performance": matrix["sourceSnapshot"]["note"].startswith("T99 technical source compiler metrics"),
    }
    result = {
        "schemaVersion": 1,
        "task": "T100",
        "result": "passed_with_gaps" if all(checks.values()) else "failed",
        "checks": checks,
        "checkCount": len(checks),
        "passedChecks": sum(checks.values()),
        "failedChecks": [name for name, passed in checks.items() if not passed],
        "matrixSha256": sha256("work/evidence/T100/region-coverage-matrix.json"),
        "scope": "input/denominator/hold and unresolved identity audit only; no canonical selection or 12-region product integration claim",
    }
    (OUT / "coverage-validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    if not all(checks.values()):
        raise SystemExit(f"T100 coverage validation failed: {result['failedChecks']}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
