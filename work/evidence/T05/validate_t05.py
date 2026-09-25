#!/usr/bin/env python3
"""Structural/provenance audit and coverage summary for the T05 pilot data."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "atlas-data/catalog/canonical-catalog.json"
REGISTRY = ROOT / "atlas-data/sources/registry.json"
RESULT = ROOT / "work/evidence/T05/validation.json"
COVERAGE = ROOT / "atlas-data/catalog/pilot-structure-coverage.json"

PILOT = {
    "HA-M-000001": "gastrocnemius",
    "HA-M-000002": "soleus",
    "HA-M-000003": "tibialis anterior",
    "HA-M-000004": "tibialis posterior",
    "HA-M-000005": "fibularis longus",
    "HA-M-000006": "fibularis brevis",
}
PARTS = {
    "HA-P-000001": "gastrocnemius lateral head",
    "HA-P-000002": "gastrocnemius medial head",
}
TA2_ROWS = {
    "HA-M-000001": "2657",
    "HA-P-000001": "2658",
    "HA-P-000002": "2659",
    "HA-M-000002": "2660",
    "HA-M-000003": "2644",
    "HA-M-000004": "2666",
    "HA-M-000005": "2652",
    "HA-M-000006": "2653",
}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    dataset = read(DATA)
    registry = read(REGISTRY)
    entities = dataset["entities"]
    all_ids: dict[str, dict] = {}
    errors: list[str] = []

    def index(kind: str):
        rows = entities.get(kind, [])
        found = {}
        for row in rows:
            ident = row.get("id")
            if ident in found:
                errors.append(f"duplicate {kind} id: {ident}")
            found[ident] = row
            if ident in all_ids:
                errors.append(f"cross-entity duplicate id: {ident}")
            all_ids[ident] = row
        return found

    concepts = index("muscleConcepts")
    all_muscles = list(concepts.values())
    parts = {row["id"]: row for row in all_muscles if row.get("entityType") == "muscle_part"}
    terms = index("terms")
    structures = index("structures")
    attachments = index("attachments")
    claims = index("claims")
    evidence = index("evidence")
    index("sources")

    expected_ids = set(PILOT) | set(PARTS)
    for ident in PILOT:
        if ident not in concepts:
            errors.append(f"missing pilot muscle concept: {ident}")
    for ident in PARTS:
        if ident not in parts:
            errors.append(f"missing gastrocnemius head part: {ident}")

    term_summary = {}
    for concept_id, label in {**PILOT, **PARTS}.items():
        rows = [row for row in entities["terms"] if row.get("conceptId") == concept_id]
        by_key = {(row.get("language"), row.get("script")): row for row in rows}
        latin = by_key.get(("la", "Latn"))
        english = by_key.get(("en", "Latn"))
        if not latin or not isinstance(latin.get("text"), str):
            errors.append(f"missing Latin term: {concept_id}")
        if not english or not isinstance(english.get("text"), str):
            errors.append(f"missing English term: {concept_id}")
        for term in (latin, english):
            if term is None:
                continue
            if term.get("reviewState") != "needs_review":
                errors.append(f"TA2 term is not needs_review: {term['id']}")
            if term.get("evidenceIds") != [f"EV-TA2-P2-R{TA2_ROWS[concept_id]}"]:
                errors.append(f"TA2 term evidence mismatch: {term['id']}")
        for language, script in (("ko", "Hang"), ("ko", "Hani")):
            missing = by_key.get((language, script))
            if not missing or missing.get("text") is not None or not missing.get("missingReason"):
                errors.append(f"Korean/Hanja must remain explicit missing: {concept_id}/{script}")
            elif missing.get("reviewState") != "held":
                errors.append(f"missing Korean/Hanja term must be held: {missing['id']}")
        term_summary[concept_id] = {
            "label": label,
            "termIds": [row["id"] for row in rows],
            "latin": latin.get("text") if latin else None,
            "english": english.get("text") if english else None,
            "koreanHangul": None,
            "koreanHanja": None,
            "koreanStatus": "held_missing_primary_edition_and_item_locator",
            "ta2Status": "needs_review_source_column_role_not_visually_verified",
        }
        row_num = TA2_ROWS[concept_id]
        ta2_ev = evidence.get(f"EV-TA2-P2-R{row_num}")
        if not ta2_ev or row_num not in ta2_ev.get("locator", ""):
            errors.append(f"missing exact TA2 source row evidence: {concept_id}")

    t05_structures = [row for row in entities["structures"] if row["id"].startswith("HA-S-") and any(tid.startswith("HA-T-T05-S-") for tid in row.get("termIds", []))]
    t05_terms = [row for row in entities["terms"] if row["id"].startswith("HA-T-T05-S-")]
    t05_attachments = [row for row in entities["attachments"] if row["id"].startswith("HA-A-T05-")]
    t05_claims = [row for row in entities["claims"] if row["id"].startswith("HA-C-T05-")]
    t05_evidence = [row for row in entities["evidence"] if row["id"].startswith("EV-GRAY1918-")]
    if len(t05_structures) != 54 or len(t05_terms) != 54:
        errors.append(f"expected 54 sourced structures/terms; found {len(t05_structures)}/{len(t05_terms)}")
    if len(t05_attachments) != 41 or len(t05_claims) != 45 or len(t05_evidence) != 11:
        errors.append(f"unexpected T05 record counts: attachments={len(t05_attachments)}, claims={len(t05_claims)}, evidence={len(t05_evidence)}")

    for term in t05_terms:
        if term.get("reviewState") != "needs_review" or term.get("termRole") != "historical":
            errors.append(f"historical structure term must remain unreviewed: {term['id']}")
        if not term.get("evidenceIds"):
            errors.append(f"structure term lacks evidence: {term['id']}")

    for row in t05_attachments:
        if row.get("muscleOrPartId") not in expected_ids:
            errors.append(f"attachment owner is not a T05 pilot ID: {row['id']}")
        if row.get("targetStructureId") not in structures:
            errors.append(f"attachment target is orphaned: {row['id']}")
        if row.get("landmarkId") is not None and row["landmarkId"] not in structures:
            errors.append(f"attachment landmark is orphaned: {row['id']}")
        claim = claims.get(row.get("descriptionClaimId"))
        if not claim or claim.get("subjectId") != row["id"]:
            errors.append(f"attachment description claim link invalid: {row['id']}")
        elif claim.get("field") != "attachment_description":
            errors.append(f"wrong attachment claim field: {claim['id']}")

    gray_claim_ids = {row["id"] for row in t05_claims}
    for claim in t05_claims:
        if claim.get("reviewState") != "needs_review":
            errors.append(f"T05 claim is incorrectly promoted: {claim['id']}")
        if not claim.get("evidenceIds"):
            errors.append(f"T05 claim lacks evidence: {claim['id']}")
        if claim.get("field") not in {"attachment_description", "tendon_course_related_structures"}:
            errors.append(f"out-of-scope claim field: {claim['field']}")
        for evidence_id in claim.get("evidenceIds", []):
            row = evidence.get(evidence_id)
            if not row or claim["id"] not in row.get("supportedClaimIds", []):
                errors.append(f"claim/evidence links not reciprocal: {claim['id']} -> {evidence_id}")

    for row in t05_evidence:
        if row.get("sourceId") != "GRAY_ANATOMY_20E_1918":
            errors.append(f"unexpected T05 evidence source: {row['id']}")
        if "http" not in row.get("locator", "") or "subsection" not in row.get("locator", "") and row["id"] != "EV-GRAY1918-CALCANEAL-TENDON":
            errors.append(f"evidence locator needs exact subsection/page and URL: {row['id']}")
        for claim_id in row.get("supportedClaimIds", []):
            if claim_id not in gray_claim_ids:
                errors.append(f"evidence has orphan or non-T05 claim: {row['id']} -> {claim_id}")

    for concept_id in PILOT:
        owners = {concept_id}
        if concept_id == "HA-M-000001":
            owners |= set(PARTS)
        owned = [row for row in t05_attachments if row.get("muscleOrPartId") in owners]
        roles = {row.get("role") for row in owned}
        if "origin" not in roles or "insertion" not in roles:
            errors.append(f"pilot lacks sourced origin or insertion: {concept_id}")
    for part_id in PARTS:
        if not any(row.get("muscleOrPartId") == part_id and row.get("role") == "origin" for row in t05_attachments):
            errors.append(f"gastrocnemius head lacks sourced origin: {part_id}")

    for kind in ("jointActions", "assessments", "spatialAnnotations"):
        if entities.get(kind):
            errors.append(f"out-of-scope {kind} records were added")

    source = next((row for row in registry["sources"] if row.get("id") == "GRAY_ANATOMY_20E_1918"), None)
    source_entity = next((row for row in entities["sources"] if row.get("id") == "GRAY_ANATOMY_20E_1918"), None)
    if not source or "not in copyright" not in source.get("license", {}).get("status", "").lower():
        errors.append("Gray source registry record or US public-domain note missing")
    if not source_entity or source_entity.get("license", {}).get("allowedUses") != ["internal", "research"]:
        errors.append("Gray source use scope widened unexpectedly")
    openstax = next((row for row in registry["sources"] if row.get("id") == "OPENSTAX_AP2E"), None)
    if not openstax or openstax.get("t05_ai_extraction_status") != "not_used_due_to_publisher_ingestion_restriction":
        errors.append("OpenStax T05 exclusion/restriction was not recorded")

    coverage = {
        "revision": "T05-pilot-structure-text-v1",
        "generatedOn": date.today().isoformat(),
        "wholeBodyCatalogComplete": False,
        "publicRelease": "not_authorized",
        "humanReviewPerformed": False,
        "recordCounts": {
            "pilotMuscleConcepts": len(PILOT),
            "gastrocnemiusHeadParts": len(PARTS),
            "historicalStructureConcepts": len(t05_structures),
            "historicalStructureTerms": len(t05_terms),
            "sourcedAttachments": len(t05_attachments),
            "sourceClaims": len(t05_claims),
            "sourceEvidence": len(t05_evidence),
        },
        "items": [],
    }
    for concept_id, label in PILOT.items():
        owners = {concept_id} | (set(PARTS) if concept_id == "HA-M-000001" else set())
        owned = [row for row in t05_attachments if row.get("muscleOrPartId") in owners]
        owned_claims = [claim for claim in t05_claims if claim.get("subjectId") in {a["id"] for a in owned} or claim.get("subjectId") == concept_id]
        coverage["items"].append({
            "conceptId": concept_id,
            "label": label,
            **term_summary[concept_id],
            "attachments": {role: sum(1 for row in owned if row.get("role") == role) for role in ("origin", "insertion", "other_attachment")},
            "claims": len(owned_claims),
            "claimReviewStates": sorted({claim.get("reviewState") for claim in owned_claims}),
            "spatialAnnotations": 0,
        })
    for part_id, label in PARTS.items():
        owned = [row for row in t05_attachments if row.get("muscleOrPartId") == part_id]
        coverage["items"].append({
            "conceptId": part_id,
            "label": label,
            **term_summary[part_id],
            "attachments": {role: sum(1 for row in owned if row.get("role") == role) for role in ("origin", "insertion", "other_attachment")},
            "claims": len([claim for claim in t05_claims if claim.get("subjectId") in {a["id"] for a in owned}]),
            "claimReviewStates": ["needs_review"] if owned else [],
            "spatialAnnotations": 0,
        })

    result = {
        "passed": not errors,
        "checks": {
            "stableIdsAndReferences": not any("missing pilot" in e or "orphan" in e or "duplicate" in e for e in errors),
            "languageGapsExplicit": not any("Korean/Hanja" in e or "missing Korean" in e for e in errors),
            "sourceAndReviewProvenance": not any("evidence" in e or "review" in e or "locator" in e or "source" in e for e in errors),
            "originInsertionCoverage": not any("lacks sourced" in e for e in errors),
            "scopeBoundary": not any("out-of-scope" in e for e in errors),
        },
        "recordCounts": coverage["recordCounts"],
        "errors": errors,
        "coveragePath": str(COVERAGE.relative_to(ROOT)),
    }
    write(RESULT, result)
    write(COVERAGE, coverage)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
