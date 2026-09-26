#!/usr/bin/env python3
"""Build and check a test-only migration preview from exact legacy summaries.

T16 deliberately leaves the production overlay empty. This preview exercises the
mapping and hash contract without importing legacy material into learner data.
It never changes canonical claims, terms, reviews, drafts, or source assets.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "atlas-data/catalog/canonical-catalog.json"
SUMMARY_PATH = ROOT / "atlas-data/terminology/learning-structure-summaries.json"
OVERLAY_PATH = ROOT / "atlas-data/terminology/ai-evidence-overlay.json"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def with_hash(row: dict[str, Any], field: str) -> dict[str, Any]:
    result = copy.deepcopy(row)
    result[field] = sha256(canonical({key: value for key, value in result.items() if key != field}))
    return result


def legacy_claim_set_hash(claims: list[dict[str, Any]]) -> str:
    # Keep the historical T10/T15 serializer verbatim: changing whitespace here
    # would make the new overlay cease to bind to the original summary contract.
    encoded = json.dumps(claims, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return sha256(encoded)


def migrate_summary(summary: dict[str, Any], entities: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    claim_by_id = {row["id"]: row for row in entities["claims"]}
    evidence_by_id = {row["id"]: row for row in entities["evidence"]}
    source_by_id = {row["id"]: row for row in entities["sources"]}
    review_rows = entities["reviews"]

    source_claim_ids = list(summary["sourceClaimIds"])
    try:
        legacy_claims = [claim_by_id[claim_id] for claim_id in source_claim_ids]
    except KeyError as exc:
        raise ValueError(f"legacy summary has an orphan claim reference: {exc.args[0]}") from exc
    claim_set_hash = legacy_claim_set_hash(legacy_claims)
    if claim_set_hash != summary["sourceClaimHash"]:
        raise ValueError(f"legacy summary claim hash is stale: {summary['conceptId']} {summary['role']}")

    legacy_evidence_ids: list[str] = []
    for old_claim in legacy_claims:
        for evidence_id in old_claim.get("evidenceIds", []):
            if evidence_id not in evidence_by_id:
                raise ValueError(f"legacy claim {old_claim['id']} has an orphan evidence reference: {evidence_id}")
            if evidence_id not in legacy_evidence_ids:
                legacy_evidence_ids.append(evidence_id)
    if not legacy_evidence_ids:
        raise ValueError(f"legacy summary has no source evidence: {summary['conceptId']} {summary['role']}")

    old_evidence = [evidence_by_id[evidence_id] for evidence_id in legacy_evidence_ids]
    source_ids = list(dict.fromkeys(row["sourceId"] for row in old_evidence))
    if len(source_ids) != 1:
        # A legacy row with multiple source works needs an explicit reconciliation;
        # never infer that it was cross-checked from row count alone.
        raise ValueError(f"legacy summary has multiple works and needs field review: {summary['conceptId']} {summary['role']}")
    source_id = source_ids[0]
    if source_id not in source_by_id:
        raise ValueError(f"legacy evidence has an orphan source reference: {source_id}")
    old_source = source_by_id[source_id]
    source_accessed = old_source.get("accessDate")
    if not source_accessed:
        raise ValueError(f"legacy source has no access date: {source_id}")

    item_id = f"AEF-{summary['conceptId']}-{summary['role'].upper()}"
    claim_id = f"AIC-{summary['conceptId']}-{summary['role'].upper()}"
    migrated_claim = {
        "id": claim_id,
        "value": summary["summary"],
        "valueHash": sha256(canonical(summary["summary"])),
        "evidenceIds": legacy_evidence_ids,
        "attribution": "legacy_summary_migration",
    }
    source = {
        "id": old_source["id"],
        "underlyingWorkId": old_source["id"],
        "title": old_source["title"],
        "url": old_source["urlOrLocalRef"],
        "editionStatus": "verified" if old_source.get("edition") else "unknown",
        "edition": old_source.get("edition"),
        "accessedOn": source_accessed,
        "accessMethod": "legacy_record",
        "textAccess": "legacy_record",
    }
    source = with_hash(source, "sourceHash")

    migrated_evidence = []
    for old in old_evidence:
        row = {
            "id": old["id"],
            "sourceId": old["sourceId"],
            "locator": old["locator"],
            "accessedOn": source_accessed,
            "accessMethod": "legacy_record",
            "textAccess": "legacy_record",
            "supportsClaimIds": [claim_id],
        }
        row["excerptHash"] = old.get("excerptHash")
        migrated_evidence.append(with_hash(row, "evidenceHash"))

    claim_review_states = [
        {"claimId": claim_id, "reviewState": claim["reviewState"]}
        for claim_id, claim in zip(source_claim_ids, legacy_claims)
    ]
    legacy_review_ids = sorted({
        row["id"] for row in review_rows
        if row["targetId"] in set(source_claim_ids) and row["reviewerKind"] == "human"
    })
    legacy_binding = {
        "summaryKey": f"{summary['conceptId']}#{summary['role']}",
        "summaryHash": sha256(summary["summary"]),
        "sourceClaimIds": source_claim_ids,
        "sourceClaimHash": summary["sourceClaimHash"],
        "summaryHumanReviewed": bool(summary.get("humanReviewed", False)),
        "claimReviewStates": claim_review_states,
        "humanReviewRecordIds": legacy_review_ids,
    }

    return {
        "id": item_id,
        "subjectId": summary["conceptId"],
        "field": summary["role"],
        "evidenceState": "single_source",
        "claims": [migrated_claim],
        "sources": [source],
        "evidence": migrated_evidence,
        "geometryState": "absent",
        "motionState": "absent",
        "legacyBinding": legacy_binding,
    }


def expected_migrated_items(catalog: dict[str, Any], summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entities = catalog["entities"]
    return [migrate_summary(row, entities) for row in summaries]


def validate_migration_preview(expected_items: list[dict[str, Any]]) -> list[dict[str, str]]:
    # Reuse the production validator against an in-memory preview so the legacy
    # mapping exercises the same ref/hash contract while remaining out of the
    # shipped overlay.
    from validate_ai_evidence import load_context, load_schema, validate_overlay

    preview = {
        "schemaVersion": "1.0.0",
        "revision": "T16-test-only-legacy-migration-preview",
        "denominatorFrozen": False,
        "wholeBodyIndividualMuscleCount": None,
        "coveragePercent": None,
        "items": expected_items,
    }
    return validate_overlay(preview, load_schema(), load_context())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="confirm the production overlay is empty and validate a legacy migration preview in memory")
    parser.add_argument("--preview", type=Path, help="write a test-only migration preview outside production data")
    args = parser.parse_args()
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    summaries = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    expected_items = expected_migrated_items(catalog, summaries)

    if args.preview:
        if args.preview.resolve() == OVERLAY_PATH.resolve() or args.preview.resolve().is_relative_to((ROOT / "atlas-data/terminology").resolve()):
            raise SystemExit("Refusing to write migration preview inside production terminology data.")
        if args.preview.exists():
            raise SystemExit(f"Refusing to overwrite an existing preview destination: {args.preview}")
        preview = {
            "schemaVersion": "1.0.0",
            "revision": "T16-test-only-legacy-migration-preview",
            "denominatorFrozen": False,
            "wholeBodyIndividualMuscleCount": None,
            "coveragePercent": None,
            "items": expected_items,
        }
        args.preview.parent.mkdir(parents=True, exist_ok=True)
        args.preview.write_text(json.dumps(preview, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"preview": str(args.preview), "purpose": "test_only_not_learning_data", "migratedRows": len(expected_items)}, ensure_ascii=False))
        return 0

    if args.check:
        if not OVERLAY_PATH.exists():
            raise SystemExit(f"Missing production overlay: {OVERLAY_PATH}")
        current = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
        issues = []
        if current.get("items") != []:
            issues.append("production_overlay_must_remain_empty_in_T16")
        issues.extend(f"migration_preview_invalid:{row['code']}:{row['path']}" for row in validate_migration_preview(expected_items))
        if issues:
            print(json.dumps({"pass": False, "issues": issues}, ensure_ascii=False, indent=2))
            return 1
        print(json.dumps({"pass": True, "productionRows": 0, "legacyMigrationPreviewRowsChecked": len(expected_items), "previewOnly": True}, ensure_ascii=False))
        return 0

    parser.error("choose --check or --preview PATH")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
