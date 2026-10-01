#!/usr/bin/env python3
"""Validate T81 coverage, source-scoped display pointers, and private input handling."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "work/evidence/T81"


def read(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(value: str) -> str:
    text = " ".join(value.casefold().split())
    return re.sub(r"\s+muscle$", "", text)


def validate() -> dict[str, Any]:
    baseline = read("work/evidence/T81/baseline.json")
    scope = read("work/product-scope.json")
    product = read("atlas-data/terminology/learner-structure-source-content.json")
    coverage = read("work/evidence/T81/supported-muscle-content-coverage.json")
    workbook = read("work/evidence/T81/workbook-row-dispositions.json")
    compiled = read("atlas-data/source-cache/datasets/za/compiled/manifest.json")
    names = read("atlas-data/terminology/learning-names.json")
    target_scope = read("atlas-data/catalog/target-scope-t96.json")
    ai = read("atlas-data/terminology/ai-evidence-overlay.json")

    assert scope["denominators"]["targets"] == 542
    assert scope["denominators"]["memberships"] == 563
    assert scope["denominators"]["regions"] == 12
    assert scope["denominators"]["existingCanonicalHaBindings"] == 130
    historical = scope["denominators"]["historical163"]["categoryCounts"].values()
    assert sorted(historical) == [2, 6, 20, 135]
    assert scope["learnerRouteCounts"]["targetIdsWithVerifiedHistoricalMembershipRoutes"] == 409
    assert scope["learnerRouteCounts"]["membershipsWithVerifiedHistoricalRoutes"] == 427

    assert len(coverage["supportedMuscles"]) == 232
    assert coverage["denominators"]["supportedMuscleSurfaces"] == 462
    assert coverage["denominators"]["uniqueSupportedMuscleSourceConcepts"] == 232
    assert len(product["records"]) == 232
    supported_by_key = {row["sourceKey"]: row for row in scope["supportedStructures"]}
    instances = {row["sourceKey"]: row for row in compiled["instances"]}
    coverage_keys = [key for row in product["records"] for key in row["sourceKeys"]]
    assert len(coverage_keys) == 462 and len(set(coverage_keys)) == 462
    assert set(coverage_keys) == {
        key for key, source in instances.items()
        if source["kind"] == "muscle_surface_or_part" and key in supported_by_key
    }

    target_by_id = {row["id"]: row for row in target_scope["targets"]}
    canonical_by_id = {row["id"]: row for row in names["entries"]}
    ai_by_subject_field = {(row["subjectId"], row["field"]): row for row in ai["items"]}
    content_pointers = 0
    displayed_targets: set[str] = set()
    for record in product["records"]:
        assert record["sourceOnly"] is True
        assert record["humanReview"] == "not_performed"
        assert record["publicRedistribution"] == "held"
        assert record["canonicalBindingCreated"] is False
        assert set(record["fieldDisposition"]) == {"origin", "insertion", "motorNerve", "sensoryProprioception"}
        assert record["fieldDisposition"]["motorNerve"]["status"] == "no_verified_field_claim"
        assert record["fieldDisposition"]["sensoryProprioception"]["status"] == "no_verified_field_claim"
        for key in record["sourceKeys"]:
            source = instances[key]
            supported_row = supported_by_key[key]
            assert source["kind"] == "muscle_surface_or_part"
            assert source["canonicalConceptId"] is None
            assert source["learnerBinding"] == "source_only_unbound"
            assert source["humanReview"] == "not_performed"
            assert source["publicRedistribution"] == "held"
            assert supported_row["routeAudience"] == "learner"
            assert supported_row["side"] == source["sourceLabelSide"]
        if record["subjectId"] is None:
            assert record["targetId"] is None and record["scopeType"] is None
            assert all(record["fieldDisposition"][field]["status"] == "no_verified_field_claim" for field in ("origin", "insertion"))
            continue

        content_pointers += len(record["sourceKeys"])
        target_id = record["targetId"]
        assert target_id and target_id not in displayed_targets
        displayed_targets.add(target_id)
        target = target_by_id[target_id]
        canonical = canonical_by_id[record["subjectId"]]
        assert normalize(target["term"]["english"]) == normalize(canonical["english"])
        assert all(normalize(instances[key]["dataName"]) == normalize(target["term"]["english"]) for key in record["sourceKeys"])
        assert record["scopeType"] == ("explicit_part" if target["semanticKind"] == "muscle_part" else "whole_structure")
        side_set = {instances[key]["sourceLabelSide"] for key in record["sourceKeys"]}
        assert side_set == {"left", "right"}
        for field in ("origin", "insertion"):
            ai_field = ai_by_subject_field[(record["subjectId"], field)]
            field_disposition = record["fieldDisposition"][field]
            assert field_disposition["evidenceState"] == ai_field["evidenceState"]
            expected_status = "conflicted_not_asserted" if ai_field["evidenceState"] == "conflicted" else "claim_available"
            assert field_disposition["status"] == expected_status
            coverage_row = next(row for row in coverage["supportedMuscles"] if set(row["sourceKeys"]) == set(record["sourceKeys"]))
            covered = coverage_row["fieldDisposition"][field]
            assert covered["claimIds"] == [claim["id"] for claim in ai_field["claims"]]

    assert content_pointers == 14
    assert displayed_targets == {"TA2:2644", "TA2:2652", "TA2:2653", "TA2:2658", "TA2:2659", "TA2:2660", "TA2:2666"}
    assert "TA2:2657" not in displayed_targets, "whole gastrocnemius evidence cannot be applied to isolated heads"

    assert workbook["rowsExpected"] == workbook["rowsProcessed"] == 257
    row_ids = [row["row"] for row in workbook["rows"]]
    assert len(row_ids) == len(set(row_ids)) == 257 and min(row_ids) == 6 and max(row_ids) == 262
    assert sum(workbook["counts"].values()) == 257
    assert all(row["candidateIsEvidence"] is False and row["directRowSourceCitation"] is False for row in workbook["rows"])
    assert all(row["actionColumnUse"] == "candidate_only_not_imported_into_learner_content" for row in workbook["rows"])
    assert workbook["source"]["rowSourceReferences"]["sourceHyperlinks"] == 0
    assert workbook["source"]["rowSourceReferences"]["cellComments"] == 0
    assert workbook["source"]["rowSourceReferences"]["hasExternalLinks"] is False
    assert workbook["source"]["rowSourceReferences"]["formulas"] == 0

    expected_workbook_hash = baseline["privateWorkbook"]["sha256"]
    original_path = Path(baseline["privateWorkbook"]["originalPath"])
    private_path = ROOT / baseline["privateWorkbook"]["stagedPath"]
    assert digest(original_path) == expected_workbook_hash
    assert digest(private_path) == expected_workbook_hash
    assert workbook["source"]["sha256"] == expected_workbook_hash
    ignore = subprocess.run(["git", "check-ignore", "--quiet", str(private_path.relative_to(ROOT))], cwd=ROOT)
    assert ignore.returncode == 0, "private workbook must stay ignored and unstaged"

    for rel_path, expected_hash in baseline["inputHashes"].items():
        if rel_path in {"work/EXECUTION.json", "atlas-web/src/ui/App.tsx", "atlas-web/src/data/learning.ts"}:
            continue
        assert digest(ROOT / rel_path) == expected_hash, f"protected T81 input changed: {rel_path}"

    return {
        "status": "passed",
        "denominators": {"targets": 542, "memberships": 563, "regions": 12, "existingCanonicalHaBindings": 130, "historical163": [2, 6, 20, 135]},
        "supportedMuscleSurfaces": 462,
        "uniqueSupportedMuscleSourceConcepts": 232,
        "workbookRowsProcessed": 257,
        "workbookDispositionCounts": workbook["counts"],
        "existingClaimProjectionSurfaces": content_pointers,
        "existingClaimProjectionTargets": sorted(displayed_targets),
        "rawWorkbookPrivateAndIgnored": True,
        "canonicalBindingsOrClaimsCreated": 0,
        "humanReview": "not_performed",
        "publicRedistribution": "held",
    }


if __name__ == "__main__":
    result = validate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
