#!/usr/bin/env python3
"""Audit T83 action-text coverage against the frozen supported-muscle set."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work/evidence/T83/function-card-coverage.json"
HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"T83 function audit failed: {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--validate-only", action="store_true", help="Validate current live function contracts without rewriting or requiring a historical coverage snapshot")
    parser.add_argument("--output", help="Current dependency audit; preserve the historical T83 artifact when another feature changes the runtime projection")
    args = parser.parse_args()
    output = (ROOT / args.output).resolve() if args.output else OUT
    if not output.is_relative_to(ROOT / 'work/evidence'):
        fail('current audit output must remain under work/evidence')

    coverage_path = "work/evidence/T81/supported-muscle-content-coverage.json"
    source_path = "atlas-data/terminology/learner-structure-source-content.json"
    motion_path = "atlas-data/motion/motion-learning.json"
    evidence_path = "atlas-data/terminology/ai-evidence-overlay.json"
    runtime_path = "atlas-data/terminology/learner-card-runtime.json"
    product_scope_path = "work/product-scope.json"

    coverage = load(coverage_path)
    source_content = load(source_path)
    motion = load(motion_path)
    evidence = load(evidence_path)
    runtime = load(runtime_path)
    product_scope = load(product_scope_path)

    denominators = coverage["denominators"]
    expected_denominators = {
        "targets": 542,
        "memberships": 563,
        "regions": 12,
        "existingCanonicalHaBindings": 130,
        "uniqueSupportedMuscleSourceConcepts": 232,
        "supportedMuscleSurfaces": 462,
        "workbookRows": 257,
    }
    for key, value in expected_denominators.items():
        if denominators.get(key) != value:
            fail(f"T81 denominator drift at {key}: {denominators.get(key)} != {value}")
    if product_scope["denominators"]["targets"] != 542 or product_scope["denominators"]["memberships"] != 563:
        fail("product-scope denominator changed")
    if product_scope["denominators"]["regions"] != 12:
        fail("region denominator changed")
    if product_scope["denominators"].get("existingCanonicalHaBindings") != 130:
        fail("existing canonical HA binding count changed")
    hist = product_scope["denominators"]["historical163"]["categoryCounts"]
    if sorted(hist.values()) != [2, 6, 20, 135] or sum(hist.values()) != 163:
        fail("historical 163 disposition changed")

    support_rows = coverage["supportedMuscles"]
    source_rows = source_content["records"]
    source_groups = {tuple(sorted(row["sourceKeys"])): row for row in source_rows}
    if len(support_rows) != 232 or len(source_rows) != 232 or len(source_groups) != 232:
        fail("supported concept/source content row count or uniqueness changed")

    field_by_id = {row["id"]: row for row in evidence["items"]}

    def verified_action_claim(action: dict) -> bool:
        action_refs = [ref for ref in action["sourceRefs"] if ref["appliesTo"] == "action_explanation"]
        if not action_refs:
            return False
        for ref in action_refs:
            field = field_by_id.get(ref.get("fieldEvidenceId"))
            if not field or field.get("field") != "action" or field.get("evidenceState") != "cross_checked":
                return False
            if action["subjectIds"] != [field.get("subjectId")]:
                return False
            claim = next((item for item in field.get("claims", []) if item.get("id") == ref.get("claimId")), None)
            if not claim or claim.get("valueHash") != ref.get("valueHash") or ref.get("evidenceId") not in claim.get("evidenceIds", []):
                return False
        return True

    actions = motion["muscleActions"]
    t21_actions = [row for row in actions if row["id"].startswith("T21-ACTION-")]
    verified_t21 = {row["subjectIds"][0]: row for row in t21_actions if verified_action_claim(row)}
    if len(t21_actions) != 6 or len(verified_t21) != 6:
        fail("the six previously cross-checked T21 action claims no longer validate")

    t24_actions = [row for row in actions if row["id"].startswith("T24-")]
    if len(t24_actions) != 1 or t24_actions[0]["sideApplicability"] != "right":
        fail("the existing T24 text candidate lost its right-only source scope")
    t24_assets = [asset for asset in motion["motionAssets"] if asset["motionDefinitionId"] in {
        definition["id"] for definition in motion["motionDefinitions"] if definition["actionId"] == t24_actions[0]["id"]
    }]
    playable = [asset for asset in motion["motionAssets"] if asset["technicalStatus"] == "binding_verified"]
    if t24_assets and any(asset["technicalStatus"] == "binding_verified" for asset in t24_assets):
        fail("T24 candidate was promoted to a playable clip")
    t83_playable = []
    for asset in playable:
        definition = next((row for row in motion["motionDefinitions"] if row["id"] == asset["motionDefinitionId"]), None)
        action = next((row for row in actions if definition and row["id"] == definition["actionId"]), None)
        if asset["id"].startswith("T83-") or (definition and definition["id"].startswith("T83-")) or (action and action["id"].startswith("T83-")):
            t83_playable.append(asset["id"])
    if t83_playable:
        fail(f"T83 must not add or promote its own playable clip: {t83_playable}")

    if len(runtime["actions"]) != 7:
        fail("expected only the six existing T21 action rows and one T24 text candidate")
    if any(HAN.search(row["label"] + row["explanation"]) for row in runtime["actions"]):
        fail("Hanja found in learner runtime action text")
    projected_t24 = [row for row in runtime["actions"] if row["conceptId"] == "HA-M-000003" and row["sideApplicability"] == "right"]
    if len(projected_t24) != 1:
        fail("right-only action applicability is not preserved in the learner projection")
    if any("이 시범은" in row["explanation"] for row in runtime["actions"]):
        fail("learner function copy implies a playable demo when no clip is available")

    records = []
    seen_source_keys: set[str] = set()
    available_concepts: set[str] = set()
    available_surfaces = 0
    exact_group_scope_count = 0
    part_noninheritance_count = 0
    for row in sorted(support_rows, key=lambda item: item["conceptKey"]):
        source_keys = row["sourceKeys"]
        source_row = source_groups.get(tuple(sorted(source_keys)))
        if not source_row:
            fail(f"T81 source projection missing or differs for {row['conceptKey']}")
        if seen_source_keys.intersection(source_keys):
            fail("a supported source surface is assigned to more than one muscle concept")
        seen_source_keys.update(source_keys)
        subject = row.get("canonicalContentSubjectId")
        scope = row.get("scopeType")
        direct_t21 = verified_t21.get(subject) if subject and scope == "whole_structure" else None
        candidate_t24 = next((item for item in t24_actions if subject in item["subjectIds"]), None) if subject else None
        if scope == "whole_structure":
            exact_group_scope_count += 1
        if scope == "explicit_part" and subject in {"HA-P-000001", "HA-P-000002"}:
            part_noninheritance_count += 1
        if direct_t21:
            status = "verified_text_available"
            ids = [direct_t21["id"]]
            available_concepts.add(row["conceptKey"])
            available_surfaces += len(source_keys)
        else:
            status = "no_exact_verified_action_text"
            ids = []
        records.append({
            "conceptKey": row["conceptKey"],
            "sourceDataName": row["sourceDataName"],
            "targetIds": row["targetIds"],
            "regionIds": row["regionIds"],
            "sourceSides": row["sourceSides"],
            "sourceKeys": source_keys,
            "canonicalContentSubjectId": subject,
            "targetContentScope": row.get("targetContentScope"),
            "scopeType": scope,
            "actionDisposition": status,
            "verifiedActionIds": ids,
            "separateRightTextCandidate": bool(candidate_t24),
            "candidateActionIds": [candidate_t24["id"]] if candidate_t24 else [],
            "sourceOnly": row["sourceOnly"],
            "humanReview": row["humanReview"],
            "publicRedistribution": row["publicRedistribution"],
            "canonicalLearnerBindingCreated": row["canonicalLearnerBindingCreated"],
        })

    if len(seen_source_keys) != 462:
        fail(f"expected 462 unique supported surfaces, received {len(seen_source_keys)}")
    if len(available_concepts) != 5 or available_surfaces != 10:
        fail(f"expected 5 exact whole-muscle groups/10 surfaces with T21 action text; got {len(available_concepts)}/{available_surfaces}")
    if part_noninheritance_count != 2:
        fail("gastrocnemius part-specific no-inheritance cases changed")
    if any(row["sourceOnly"] is not True or row["humanReview"] != "not_performed" or row["publicRedistribution"] != "held" or row["canonicalLearnerBindingCreated"] is not False for row in support_rows):
        fail("source/review/rights/canonical binding state changed")

    unmatched_verified = sorted(subject for subject in verified_t21 if subject not in {
        row.get("canonicalContentSubjectId") for row in support_rows
    })
    if unmatched_verified != ["HA-M-000001"]:
        fail(f"unexpected change in exact action target mapping: {unmatched_verified}")

    inputs = [coverage_path, source_path, motion_path, evidence_path, runtime_path, product_scope_path]
    result = {
        "schemaVersion": "t83-function-card-coverage-v1",
        "asOf": "2026-10-01",
        "inputs": {path: digest(path) for path in inputs},
        "denominators": {
            "targets": 542,
            "memberships": 563,
            "regions": 12,
            "existingCanonicalHaBindings": 130,
            "historical163": {"total": 163, "categories": {"6": 6, "20": 20, "135": 135, "2": 2}},
            "supportedMuscleConcepts": 232,
            "supportedMuscleSurfaces": 462,
        },
        "summary": {
            "supportedConceptsWithExactVerifiedText": len(available_concepts),
            "supportedSurfacesWithExactVerifiedText": available_surfaces,
            "supportedConceptsWithoutExactVerifiedText": len(records) - len(available_concepts),
            "existingCrossCheckedT21Claims": len(verified_t21),
            "T21ClaimsNotMappedToExactCurrentSurfaceScope": unmatched_verified,
            "gastrocnemiusHeadWholeClaimInheritance": "not_applied_to_two_explicit_part_subjects",
            "rightOnlyTextCandidates": 1,
            "playableClips": 0,
            "learnerActionTextHanjaCount": 0,
            "newClaims": 0,
            "newCanonicalBindings": 0,
            "humanReview": "not_performed",
            "publicRedistribution": "held",
            "sourceOnly": True,
        },
        "displayPolicy": {
            "unsupportedFunctionText": "현재 확인 가능한 기능 설명이 없습니다.",
            "motionDemoState": "independently_unavailable; button remains disabled",
            "postureAndTestingConditions": "not_presented_as_fixed_anatomical_structures",
            "faceEyeTongueSphincterJointRotationCoercion": "none; unverified workbook candidates are not learner claims",
            "workbookCandidates": "unverified_private_candidates_only",
        },
        "records": records,
    }
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.validate_only:
        if args.check or args.output:
            fail("--validate-only cannot be combined with snapshot --check/--output")
        print(json.dumps({"status": "passed", "mode": "live_contract_validation", **result["summary"]}, ensure_ascii=False))
    elif args.check:
        current = output.read_text(encoding="utf-8") if output.exists() else None
        if current != encoded:
            fail("coverage evidence is stale; rebuild without changing the frozen inputs")
        print(json.dumps({"status": "passed", **result["summary"]}, ensure_ascii=False))
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(json.dumps({"status": "built", **result["summary"], "records": len(records)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
