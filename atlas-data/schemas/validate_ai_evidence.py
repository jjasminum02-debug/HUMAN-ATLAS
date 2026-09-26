#!/usr/bin/env python3
"""Validate AI field evidence without changing canonical review or anatomy state."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "atlas-data/schemas/ai-evidence-overlay.schema.json"
DATASET_PATH = ROOT / "atlas-data/terminology/ai-evidence-overlay.json"
CATALOG_PATH = ROOT / "atlas-data/catalog/canonical-catalog.json"
SOURCE_REGISTRY_PATH = ROOT / "atlas-data/sources/registry.json"
SUMMARY_PATH = ROOT / "atlas-data/terminology/learning-structure-summaries.json"
CROSSCHECK_PATH = ROOT / "atlas-data/terminology/learning-attachment-crosschecks.json"
FIXTURE_INDEX_PATH = ROOT / "work/evidence/T16/fixtures/index.json"

_T03_SPEC = importlib.util.spec_from_file_location("human_atlas_t03_validator", Path(__file__).with_name("validate.py"))
if _T03_SPEC is None or _T03_SPEC.loader is None:
    raise RuntimeError("Could not load the T03 schema keyword validator")
_T03 = importlib.util.module_from_spec(_T03_SPEC)
sys.modules[_T03_SPEC.name] = _T03
_T03_SPEC.loader.exec_module(_T03)

OPEN_TEXT_ACCESS = {"full_text_opened", "partial_text_opened"}


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def source_hash(row: dict[str, Any]) -> str:
    return sha256(canonical({key: value for key, value in row.items() if key != "sourceHash"}))


def evidence_hash(row: dict[str, Any]) -> str:
    return sha256(canonical({key: value for key, value in row.items() if key != "evidenceHash"}))


def value_hash(value: Any) -> str:
    return sha256(canonical(value))


def claim_set_hash(claims: list[dict[str, Any]]) -> str:
    # This must remain byte-compatible with the T15 learning overlay validator.
    return sha256(json.dumps(claims, ensure_ascii=False, sort_keys=True).encode("utf-8"))


def load_context() -> dict[str, Any]:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    registry = json.loads(SOURCE_REGISTRY_PATH.read_text(encoding="utf-8"))
    summaries = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    crosschecks = json.loads(CROSSCHECK_PATH.read_text(encoding="utf-8"))
    entities = catalog["entities"]
    subjects: set[str] = set()
    for name in ("muscleConcepts", "muscleParts", "structures"):
        subjects.update(row["id"] for row in entities.get(name, []))
    known_sources: dict[str, dict[str, Any]] = {}
    for row in entities.get("sources", []):
        known_sources[row["id"]] = {
            "id": row["id"], "title": row["title"], "url": row["urlOrLocalRef"],
            "edition": row.get("edition"), "accessedOn": row.get("accessDate"),
        }
    for row in registry.get("sources", []):
        known_sources.setdefault(row["id"], {
            "id": row["id"], "title": row.get("title"), "url": row.get("primary_locator") or row.get("url"),
            "edition": row.get("edition"), "accessedOn": registry.get("accessed_on"),
        })
    for row in crosschecks.get("sources", []):
        known_sources.setdefault(row["id"], {
            "id": row["id"], "title": row.get("title"), "url": row.get("url"),
            "edition": row.get("edition"), "accessedOn": row.get("accessDate"),
        })
    claims = {row["id"]: row for row in entities.get("claims", [])}
    evidence = {row["id"]: row for row in entities.get("evidence", [])}
    sources = {row["id"]: row for row in entities.get("sources", [])}
    reviews = {row["id"]: row for row in entities.get("reviews", [])}
    legacy_summaries = {f"{row['conceptId']}#{row['role']}": row for row in summaries}
    return {
        "subjects": subjects,
        "knownSources": known_sources,
        "claims": claims,
        "evidence": evidence,
        "sources": sources,
        "reviews": reviews,
        "legacySummaries": legacy_summaries,
    }


def validate_overlay(payload: Any, schema: dict[str, Any], context: dict[str, Any], *, allow_fixture: bool = False) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for issue in _T03.schema_issues(schema, payload):
        issues.append({"code": issue["code"], "path": issue["path"], "message": issue["message"]})
    if issues:
        return issues

    if not payload["denominatorFrozen"] and (payload["wholeBodyIndividualMuscleCount"] is not None or payload["coveragePercent"] is not None):
        issues.append({"code": "unfrozen_denominator_has_coverage", "path": "$.denominatorFrozen", "message": "An unfrozen whole-body denominator must keep count and coverage null."})

    seen_item_ids: set[str] = set()
    seen_subject_fields: set[tuple[str, str]] = set()
    for index, item in enumerate(payload["items"]):
        path = f"$.items[{index}]"
        if item["id"] in seen_item_ids:
            issues.append({"code": "duplicate_field_id", "path": f"{path}.id", "message": f"Duplicate field ID {item['id']!r}."})
        seen_item_ids.add(item["id"])
        subject_field = (item["subjectId"], item["field"])
        if subject_field in seen_subject_fields:
            issues.append({"code": "duplicate_subject_field", "path": path, "message": f"More than one overlay row for {subject_field!r}."})
        seen_subject_fields.add(subject_field)
        if item["subjectId"] not in context["subjects"]:
            issues.append({"code": "orphan_subject_reference", "path": f"{path}.subjectId", "message": f"Unknown canonical ID {item['subjectId']!r}."})

        sources: dict[str, dict[str, Any]] = {}
        for source_index, source in enumerate(item["sources"]):
            source_path = f"{path}.sources[{source_index}]"
            if source["id"] in sources:
                issues.append({"code": "duplicate_source_id", "path": f"{source_path}.id", "message": f"Duplicate source ID {source['id']!r}."})
            sources[source["id"]] = source
            if source.get("fixtureOnly") and not allow_fixture:
                issues.append({"code": "synthetic_source_in_production", "path": f"{source_path}.fixtureOnly", "message": "Synthetic fixture sources cannot enter the production overlay."})
            known = context["knownSources"].get(source["id"])
            if known is None and not (allow_fixture and source.get("fixtureOnly")):
                issues.append({"code": "orphan_source_reference", "path": f"{source_path}.id", "message": f"Source {source['id']!r} does not resolve in project sources."})
            if known is not None:
                for prop, source_prop in (("title", "title"), ("url", "url"), ("edition", "edition")):
                    expected = known.get(source_prop)
                    if expected is not None and source[prop] != expected:
                        issues.append({"code": "source_snapshot_mismatch", "path": f"{source_path}.{prop}", "message": f"Source snapshot {prop} does not match the current source registry."})
            if source["editionStatus"] == "verified" and (not isinstance(source["edition"], str) or not source["edition"].strip()):
                issues.append({"code": "verified_edition_missing", "path": f"{source_path}.edition", "message": "A verified edition must include its exact edition string."})
            if source["editionStatus"] == "not_exposed" and source["edition"] is not None:
                issues.append({"code": "unexposed_edition_filled", "path": f"{source_path}.edition", "message": "A source that does not expose its edition must keep edition null."})
            if source["sourceHash"] != source_hash(source):
                issues.append({"code": "source_hash_mismatch", "path": f"{source_path}.sourceHash", "message": "Source metadata hash is stale."})

        evidence_by_id: dict[str, dict[str, Any]] = {}
        for evidence_index, evidence in enumerate(item["evidence"]):
            evidence_path = f"{path}.evidence[{evidence_index}]"
            if evidence["id"] in evidence_by_id:
                issues.append({"code": "duplicate_evidence_id", "path": f"{evidence_path}.id", "message": f"Duplicate evidence ID {evidence['id']!r}."})
            evidence_by_id[evidence["id"]] = evidence
            if evidence["sourceId"] not in sources:
                issues.append({"code": "orphan_evidence_source", "path": f"{evidence_path}.sourceId", "message": f"Evidence source {evidence['sourceId']!r} is missing from this field."})
            if evidence["evidenceHash"] != evidence_hash(evidence):
                issues.append({"code": "evidence_hash_mismatch", "path": f"{evidence_path}.evidenceHash", "message": "Evidence locator/access metadata hash is stale."})

        claim_by_id: dict[str, dict[str, Any]] = {}
        value_hashes: set[str] = set()
        supported_work_ids: set[str] = set()
        supporting_rows: list[dict[str, Any]] = []
        for claim_index, claim in enumerate(item["claims"]):
            claim_path = f"{path}.claims[{claim_index}]"
            if claim["id"] in claim_by_id:
                issues.append({"code": "duplicate_claim_id", "path": f"{claim_path}.id", "message": f"Duplicate claim ID {claim['id']!r}."})
            claim_by_id[claim["id"]] = claim
            wanted_value_hash = value_hash(claim["value"])
            if claim["valueHash"] != wanted_value_hash:
                issues.append({"code": "claim_hash_mismatch", "path": f"{claim_path}.valueHash", "message": "Claim value hash is stale."})
            value_hashes.add(wanted_value_hash)
            if not claim["evidenceIds"]:
                issues.append({"code": "claim_missing_evidence", "path": f"{claim_path}.evidenceIds", "message": "A field claim needs at least one evidence reference."})
            for evidence_id in claim["evidenceIds"]:
                linked = evidence_by_id.get(evidence_id)
                if linked is None:
                    issues.append({"code": "orphan_claim_evidence", "path": f"{claim_path}.evidenceIds", "message": f"Unknown evidence ID {evidence_id!r}."})
                    continue
                if claim["id"] not in linked["supportsClaimIds"]:
                    issues.append({"code": "evidence_claim_link_not_reciprocal", "path": f"{claim_path}.evidenceIds", "message": f"Evidence {evidence_id!r} does not reciprocally list claim {claim['id']!r}."})
                for source_id in [linked["sourceId"]]:
                    source = sources.get(source_id)
                    if source is not None:
                        supported_work_ids.add(source["underlyingWorkId"])
                        supporting_rows.append({"claimId": claim["id"], "source": source, "evidence": linked})

        for evidence_index, evidence in enumerate(item["evidence"]):
            evidence_path = f"{path}.evidence[{evidence_index}]"
            for claim_id in evidence["supportsClaimIds"]:
                claim = claim_by_id.get(claim_id)
                if claim is None:
                    issues.append({"code": "orphan_evidence_claim", "path": f"{evidence_path}.supportsClaimIds", "message": f"Unknown claim ID {claim_id!r}."})
                elif evidence["id"] not in claim["evidenceIds"]:
                    issues.append({"code": "claim_evidence_link_not_reciprocal", "path": f"{evidence_path}.supportsClaimIds", "message": f"Claim {claim_id!r} does not reciprocally list evidence {evidence['id']!r}."})

        state = item["evidenceState"]
        if state == "unresearched":
            if item["claims"] or item["evidence"]:
                issues.append({"code": "unresearched_has_findings", "path": f"{path}.evidenceState", "message": "Unresearched fields cannot contain claim/evidence findings."})
            if "unavailableReason" in item:
                issues.append({"code": "unresearched_has_unavailable_reason", "path": f"{path}.unavailableReason", "message": "Unresearched differs from an attempted but unavailable source."})
        elif state == "unavailable":
            if item["claims"]:
                issues.append({"code": "unavailable_has_claims", "path": f"{path}.claims", "message": "An unavailable field cannot contain a settled value claim."})
            if not item.get("unavailableReason", "").strip():
                issues.append({"code": "unavailable_reason_missing", "path": f"{path}.unavailableReason", "message": "Record why evidence could not be obtained."})
            if any(row["supportsClaimIds"] for row in item["evidence"]):
                issues.append({"code": "unavailable_evidence_supports_claim", "path": f"{path}.evidence", "message": "Unavailable evidence may document an access attempt but cannot support a field claim."})
        elif state == "single_source":
            if not item["claims"] or len(value_hashes) != 1:
                issues.append({"code": "single_source_value_invalid", "path": f"{path}.claims", "message": "Single-source state needs one consistent field value."})
            if not supporting_rows:
                issues.append({"code": "single_source_evidence_missing", "path": f"{path}.evidence", "message": "Single-source state needs source-linked evidence."})
            if len(supported_work_ids) != 1:
                issues.append({"code": "single_source_multiple_works", "path": f"{path}.evidenceState", "message": "Single-source state must resolve to exactly one underlying work."})
            legacy_migration_only = bool(item.get("legacyBinding")) and bool(item["claims"]) and all(
                claim["attribution"] == "legacy_summary_migration" for claim in item["claims"]
            )
            if any(
                (
                    row["evidence"]["textAccess"] not in OPEN_TEXT_ACCESS
                    or row["evidence"]["accessMethod"] in {"search_index", "metadata", "abstract", "legacy_record", "synthetic_fixture"}
                )
                and not (
                    legacy_migration_only
                    and row["evidence"]["textAccess"] == "legacy_record"
                    and row["evidence"]["accessMethod"] == "legacy_record"
                    and row["source"]["textAccess"] == "legacy_record"
                    and row["source"]["accessMethod"] == "legacy_record"
                )
                for row in supporting_rows
            ):
                issues.append({"code": "single_source_text_not_opened", "path": f"{path}.evidence", "message": "A new single-source claim requires opened field-level text; search indexes, abstracts, metadata, and fixture-only rows are not final source evidence."})
        elif state == "cross_checked":
            if not item["claims"] or len(value_hashes) != 1:
                issues.append({"code": "cross_checked_value_invalid", "path": f"{path}.claims", "message": "Cross-checked state needs one field value that the sources support."})
            if len(supported_work_ids) < 2:
                issues.append({"code": "cross_checked_not_independent", "path": f"{path}.evidenceState", "message": "Cross-checked requires at least two distinct underlying works; separate URLs re-citing one work count once."})
            if any(row["evidence"]["textAccess"] not in OPEN_TEXT_ACCESS or row["evidence"]["accessMethod"] in {"search_index", "metadata", "abstract", "legacy_record", "synthetic_fixture"} for row in supporting_rows):
                issues.append({"code": "cross_checked_source_not_opened", "path": f"{path}.evidence", "message": "Cross-checking requires field evidence from opened full-text sources, not indexes, metadata, abstracts, fixtures, or unreaudited legacy rows."})
        elif state == "conflicted":
            if not item["claims"] or len(value_hashes) < 2:
                issues.append({"code": "conflict_values_missing", "path": f"{path}.claims", "message": "Conflicted state needs at least two distinct sourced values."})
            claims_with_support = {row["claimId"] for row in supporting_rows}
            if claims_with_support != set(claim_by_id):
                issues.append({"code": "conflict_claim_evidence_incomplete", "path": f"{path}.claims", "message": "Every conflicting value needs its own source evidence."})
            if any(row["evidence"]["textAccess"] not in OPEN_TEXT_ACCESS or row["evidence"]["accessMethod"] in {"search_index", "metadata", "abstract", "legacy_record", "synthetic_fixture"} for row in supporting_rows):
                issues.append({"code": "conflict_source_not_opened", "path": f"{path}.evidence", "message": "A conflict requires opened field-level source text."})

        if "legacyBinding" in item:
            validate_legacy_binding(item, path, context, issues)

    return issues


def validate_legacy_binding(item: dict[str, Any], path: str, context: dict[str, Any], issues: list[dict[str, str]]) -> None:
    binding = item["legacyBinding"]
    binding_path = f"{path}.legacyBinding"
    summary = context["legacySummaries"].get(binding["summaryKey"])
    if summary is None:
        issues.append({"code": "orphan_legacy_summary", "path": f"{binding_path}.summaryKey", "message": "Legacy summary key does not resolve."})
        return
    if summary["conceptId"] != item["subjectId"] or summary["role"] != item["field"]:
        issues.append({"code": "legacy_subject_field_mismatch", "path": f"{binding_path}.summaryKey", "message": "Legacy summary belongs to a different canonical field."})
    if binding["summaryHash"] != sha256(summary["summary"]):
        issues.append({"code": "legacy_summary_hash_mismatch", "path": f"{binding_path}.summaryHash", "message": "Migrated summary no longer matches its original text."})
    if binding["sourceClaimIds"] != summary["sourceClaimIds"]:
        issues.append({"code": "legacy_claim_ids_mismatch", "path": f"{binding_path}.sourceClaimIds", "message": "Legacy claim ID sequence changed during migration."})
    if binding["sourceClaimHash"] != summary["sourceClaimHash"]:
        issues.append({"code": "legacy_claim_hash_mismatch", "path": f"{binding_path}.sourceClaimHash", "message": "Legacy source claim hash changed during migration."})
    legacy_claims: list[dict[str, Any]] = []
    for claim_id in summary["sourceClaimIds"]:
        claim = context["claims"].get(claim_id)
        if claim is None:
            issues.append({"code": "orphan_legacy_claim", "path": f"{binding_path}.sourceClaimIds", "message": f"Legacy claim {claim_id!r} no longer exists."})
        else:
            legacy_claims.append(claim)
    if len(legacy_claims) == len(summary["sourceClaimIds"]) and claim_set_hash(legacy_claims) != binding["sourceClaimHash"]:
        issues.append({"code": "legacy_claim_content_hash_mismatch", "path": f"{binding_path}.sourceClaimHash", "message": "Canonical legacy claim contents changed after migration."})
    if binding["summaryHumanReviewed"] is not bool(summary.get("humanReviewed", False)):
        issues.append({"code": "legacy_review_flag_changed", "path": f"{binding_path}.summaryHumanReviewed", "message": "Legacy human-review flag was not preserved exactly."})
    expected_states = [{"claimId": claim_id, "reviewState": context["claims"][claim_id]["reviewState"]} for claim_id in summary["sourceClaimIds"] if claim_id in context["claims"]]
    if binding["claimReviewStates"] != expected_states:
        issues.append({"code": "legacy_claim_review_state_changed", "path": f"{binding_path}.claimReviewStates", "message": "Legacy claim review states were altered or detached from their canonical claims."})
    expected_human_reviews = sorted({
        review_id for review_id, review in context["reviews"].items()
        if review["targetId"] in set(summary["sourceClaimIds"]) and review["reviewerKind"] == "human"
    })
    if binding["humanReviewRecordIds"] != expected_human_reviews:
        issues.append({"code": "legacy_human_review_refs_changed", "path": f"{binding_path}.humanReviewRecordIds", "message": "Legacy binding must retain exactly the existing human review record references."})
    if binding["summaryHumanReviewed"] and not expected_human_reviews:
        issues.append({"code": "legacy_review_flag_without_review_record", "path": f"{binding_path}.summaryHumanReviewed", "message": "A legacy true flag without a current human record cannot be treated as approval."})


def load_schema() -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    problems = _T03.check_schema(schema)
    if problems:
        raise ValueError(json.dumps([dict(row) for row in problems], ensure_ascii=False, indent=2))
    return schema


def run_fixtures(schema: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
    index = json.loads(FIXTURE_INDEX_PATH.read_text(encoding="utf-8"))
    results = []
    for row in index["fixtures"]:
        fixture_path = ROOT / row["path"]
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        issues = validate_overlay(payload, schema, context, allow_fixture=True)
        actual_pass = not issues
        expected_pass = bool(row["valid"])
        expected_issue = row.get("expectedIssue")
        expected_issue_found = expected_issue is None or any(issue["code"] == expected_issue for issue in issues)
        passed = actual_pass == expected_pass and expected_issue_found
        results.append({
            "fixture": row["path"], "expectedValid": expected_pass, "actualValid": actual_pass,
            "expectedIssue": expected_issue, "expectedIssueFound": expected_issue_found,
            "issueCodes": [issue["code"] for issue in issues], "passed": passed,
        })
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="validate production overlay, schema, and all legacy hash bindings")
    group.add_argument("--fixtures", action="store_true", help="run synthetic positive/negative contract fixtures")
    parser.add_argument("--report", type=Path, help="write a JSON validation report")
    args = parser.parse_args()
    report: dict[str, Any] = {"task": "T16", "mode": "check" if args.check else "fixtures", "pass": False}
    try:
        schema = load_schema()
        context = load_context()
        if args.check:
            payload = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
            issues = validate_overlay(payload, schema, context)
            from build_ai_evidence_overlay import expected_migrated_items
            catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
            summaries = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
            migration_items = expected_migrated_items(catalog, summaries)
            migration_preview = {
                "schemaVersion": "1.0.0",
                "revision": "T16-test-only-legacy-migration-preview",
                "denominatorFrozen": False,
                "wholeBodyIndividualMuscleCount": None,
                "coveragePercent": None,
                "items": migration_items,
            }
            migration_issues = validate_overlay(migration_preview, schema, context)
            for issue in migration_issues:
                issues.append({**issue, "path": f"migrationPreview{issue['path'][1:]}"})
            if payload.get("items") != []:
                issues.append({"code": "production_overlay_must_remain_empty", "path": "$.items", "message": "T16 exercises migration against an in-memory preview; no legacy claims are imported into learner data."})
            if payload.get("denominatorFrozen") is not False or payload.get("wholeBodyIndividualMuscleCount") is not None or payload.get("coveragePercent") is not None:
                issues.append({"code": "t15g_denominator_changed", "path": "$.denominatorFrozen", "message": "T16 must preserve the unfrozen T15g denominator and null coverage."})
            report.update({"legacyRowsCheckedInTestOnlyMigrationPreview": len(migration_items), "productionFieldItems": len(payload.get("items", [])), "migrationPreviewIssues": migration_issues, "issues": issues, "pass": not issues})
        else:
            results = run_fixtures(schema, context)
            report.update({"fixtures": results, "fixtureCount": len(results), "passed": sum(row["passed"] for row in results), "failed": sum(not row["passed"] for row in results), "pass": all(row["passed"] for row in results)})
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
