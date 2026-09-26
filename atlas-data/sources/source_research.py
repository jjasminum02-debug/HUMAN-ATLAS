#!/usr/bin/env python3
"""Offline source-access ledger and field-comparison compiler.

This tool does not browse, make model calls, write canonical anatomy data, or
grant human review. It only validates and renders a locally supplied manifest.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import re
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "atlas-data/schemas/source-research-manifest.schema.json"
CATALOG_PATH = ROOT / "atlas-data/catalog/canonical-catalog.json"
T03_VALIDATOR_PATH = ROOT / "atlas-data/schemas/validate.py"
CACHE_VERSION = "1.0.0"
OBSERVED_ORIGINAL_ACCESS = {"full_text_opened", "partial_text_opened"}
COMPARISON_CLASSES = {
    "agreement", "wording_difference", "variation", "substantive_conflict", "not_comparable"
}
OUTPUT_NAMES = (
    "access-ledger.json", "field-observations.json", "comparison-table.csv",
    "run-summary.json", "exceptions.json",
)

_SPEC = importlib.util.spec_from_file_location("human_atlas_t03_validator", T03_VALIDATOR_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("Could not load the project JSON Schema validator")
_T03 = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _T03
_SPEC.loader.exec_module(_T03)


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def value_hash(value: Any) -> str:
    return sha256(canonical(value))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_individual_muscle_ids() -> set[str]:
    data = load_json(CATALOG_PATH)
    return {row["id"] for row in data.get("entities", {}).get("muscleConcepts", [])}


def _issue(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _valid_source_url(url: str) -> bool:
    try:
        if any(character.isspace() or ord(character) < 32 for character in url):
            return False
        parsed = urlsplit(url)
        if parsed.scheme in ("http", "https"):
            # Accessing .port also rejects malformed ports.
            _ = parsed.port
            return bool(parsed.hostname) and parsed.username is None and parsed.password is None
        if parsed.scheme == "local":
            return bool(parsed.netloc or parsed.path) and parsed.username is None and parsed.password is None
    except ValueError:
        return False
    return False


def validate_manifest(
    manifest: Any,
    *,
    schema: dict[str, Any] | None = None,
    canonical_ids: set[str] | None = None,
    allow_synthetic_fixtures: bool = False,
) -> list[dict[str, str]]:
    schema = schema if schema is not None else load_json(SCHEMA_PATH)
    issues = [dict(item) for item in _T03.schema_issues(schema, manifest)]
    if issues:
        return issues

    fixture_only = manifest["fixtureOnly"]
    subjects = manifest["subjects"]
    if not 1 <= len(subjects) <= 6:
        issues.append(_issue("subject_limit", "$.subjects", "A source run must contain between one and six muscle subjects."))
    record_types = {row["recordType"] for row in subjects}
    if fixture_only:
        if not allow_synthetic_fixtures:
            issues.append(_issue("synthetic_fixture_not_enabled", "$.fixtureOnly", "Synthetic fixture manifests require the explicit test-only flag."))
        if record_types != {"synthetic_fixture"}:
            issues.append(_issue("fixture_subject_type_mismatch", "$.subjects", "Fixture-only manifests may contain synthetic subjects only."))
    elif record_types != {"canonical"}:
        issues.append(_issue("canonical_subject_type_mismatch", "$.subjects", "A non-fixture manifest must contain canonical subjects only."))

    known_ids = canonical_ids if canonical_ids is not None else canonical_individual_muscle_ids()
    subject_by_id: dict[str, dict[str, Any]] = {}
    global_ids: dict[str, str] = {}

    def register(row_id: str, path: str) -> None:
        prior = global_ids.get(row_id)
        if prior is not None:
            issues.append(_issue("duplicate_global_id", path, f"ID {row_id!r} is already used at {prior}."))
        else:
            global_ids[row_id] = path

    for i, subject in enumerate(subjects):
        path = f"$.subjects[{i}]"
        register(subject["id"], f"{path}.id")
        if subject["id"] in subject_by_id:
            issues.append(_issue("duplicate_subject_id", f"{path}.id", f"Duplicate subject {subject['id']!r}."))
        subject_by_id[subject["id"]] = subject
        if subject["recordType"] == "canonical" and subject["id"] not in known_ids:
            issues.append(_issue("orphan_canonical_subject", f"{path}.id", f"Unknown individual muscle ID {subject['id']!r}."))
        if len(subject["fields"]) != len(set(subject["fields"])):
            issues.append(_issue("duplicate_subject_field", f"{path}.fields", "Subject fields must be unique."))

    sources: dict[str, dict[str, Any]] = {}
    source_identity: dict[tuple[Any, ...], str] = {}
    for i, source in enumerate(manifest["sources"]):
        path = f"$.sources[{i}]"
        register(source["id"], f"{path}.id")
        if source["id"] in sources:
            issues.append(_issue("duplicate_source_id", f"{path}.id", f"Duplicate source ID {source['id']!r}."))
        sources[source["id"]] = source
        if not _valid_source_url(source["url"]):
            issues.append(_issue("invalid_source_url", f"{path}.url", "URL must be http(s) with a host or a local:// reference."))
        identity = (source["underlyingWorkId"], source["url"], source["editionStatus"], source["edition"])
        if identity in source_identity:
            issues.append(_issue("duplicate_source_identity", f"{path}.url", f"This source duplicates {source_identity[identity]!r}; reuse its source ID."))
        else:
            source_identity[identity] = source["id"]
        if source["editionStatus"] == "verified" and (not isinstance(source["edition"], str) or not source["edition"].strip()):
            issues.append(_issue("verified_edition_missing", f"{path}.edition", "Verified editions require the exact edition string."))
        if source["editionStatus"] in ("not_exposed", "unknown") and source["edition"] is not None:
            issues.append(_issue("unverified_edition_filled", f"{path}.edition", "Unexposed or unknown editions must remain null."))
        if source["underlyingWorkId"] is not None and not source["underlyingWorkId"].strip():
            issues.append(_issue("empty_underlying_work_id", f"{path}.underlyingWorkId", "Use null when the underlying work cannot be identified."))

    accesses: dict[str, dict[str, Any]] = {}
    access_identity: dict[tuple[Any, ...], str] = {}
    used_source_ids: set[str] = set()
    for i, access in enumerate(manifest["accesses"]):
        path = f"$.accesses[{i}]"
        register(access["id"], f"{path}.id")
        if access["id"] in accesses:
            issues.append(_issue("duplicate_access_id", f"{path}.id", f"Duplicate access ID {access['id']!r}."))
        accesses[access["id"]] = access
        source = sources.get(access["sourceId"])
        subject = subject_by_id.get(access["subjectId"])
        if source is None:
            issues.append(_issue("orphan_access_source", f"{path}.sourceId", f"Unknown source {access['sourceId']!r}."))
        else:
            used_source_ids.add(access["sourceId"])
        if subject is None:
            issues.append(_issue("orphan_access_subject", f"{path}.subjectId", f"Unknown subject {access['subjectId']!r}."))
        elif access["field"] not in subject["fields"]:
            issues.append(_issue("orphan_access_field", f"{path}.field", f"Field {access['field']!r} is not declared by this subject."))
        try:
            date.fromisoformat(access["accessedOn"])
        except (TypeError, ValueError):
            issues.append(_issue("invalid_access_date", f"{path}.accessedOn", "Access date must be a real ISO-8601 calendar date."))
        if access["accessOutcome"] == "failed":
            if access["textAccess"] != "unavailable":
                issues.append(_issue("failed_access_marked_open", f"{path}.textAccess", "A failed access must use textAccess=unavailable."))
            if not access.get("failureReason", "").strip():
                issues.append(_issue("failed_access_reason_missing", f"{path}.failureReason", "Record why this attempt failed."))
        else:
            if access["textAccess"] == "unavailable":
                issues.append(_issue("unavailable_access_marked_open", f"{path}.accessOutcome", "An unavailable access cannot be marked opened."))
            if access.get("failureReason"):
                issues.append(_issue("opened_access_has_failure_reason", f"{path}.failureReason", "An opened page cannot carry a failed-access reason."))
            if source is not None and source["editionStatus"] == "unknown":
                issues.append(_issue("opened_edition_unresolved", f"$.sources[{access['sourceId']}].editionStatus", "For opened material, record the exact edition or explicitly use not_exposed."))
        if access["accessMethod"] == "search_index" and access["textAccess"] != "index_only":
            issues.append(_issue("search_index_marked_as_source_text", f"{path}.textAccess", "A search index/snippet is index_only, never opened source text."))
        if access["accessMethod"] == "synthetic_fixture" and not fixture_only:
            issues.append(_issue("fixture_access_in_production_manifest", f"{path}.accessMethod", "Synthetic fixture access cannot be used in a canonical manifest."))
        if access["textAccess"] == "fixture_only" and not fixture_only:
            issues.append(_issue("fixture_text_in_production_manifest", f"{path}.textAccess", "Synthetic fixture text cannot be used in a canonical manifest."))
        identity = (
            access["sourceId"], access["subjectId"], access["field"], access["locator"],
            access["accessedOn"], access["accessMethod"], access["textAccess"], access["accessOutcome"]
        )
        if identity in access_identity:
            issues.append(_issue("duplicate_access_identity", f"{path}", f"Duplicate access record; first recorded as {access_identity[identity]!r}."))
        else:
            access_identity[identity] = access["id"]

    for source_id in sources:
        if source_id not in used_source_ids:
            issues.append(_issue("orphan_source_record", f"$.sources[{source_id}]", "Every source record must be linked to an access attempt."))

    extractions: dict[str, dict[str, Any]] = {}
    extraction_identity: dict[tuple[Any, ...], str] = {}
    for i, extraction in enumerate(manifest["extractions"]):
        path = f"$.extractions[{i}]"
        register(extraction["id"], f"{path}.id")
        if extraction["id"] in extractions:
            issues.append(_issue("duplicate_extraction_id", f"{path}.id", f"Duplicate extraction ID {extraction['id']!r}."))
        extractions[extraction["id"]] = extraction
        access = accesses.get(extraction["accessId"])
        subject = subject_by_id.get(extraction["subjectId"])
        if access is None:
            issues.append(_issue("orphan_extraction_access", f"{path}.accessId", f"Unknown access ID {extraction['accessId']!r}."))
            continue
        if subject is None or extraction["field"] not in subject["fields"]:
            issues.append(_issue("orphan_extraction_field", f"{path}.field", "Extraction field is not declared for its subject."))
        if access["subjectId"] != extraction["subjectId"] or access["field"] != extraction["field"]:
            issues.append(_issue("extraction_access_scope_mismatch", path, "Extraction subject/field must match its access record."))
        source = sources.get(access["sourceId"])
        if access["accessOutcome"] != "opened" or access["textAccess"] not in OBSERVED_ORIGINAL_ACCESS | ({"fixture_only"} if fixture_only else set()):
            issues.append(_issue("extraction_without_opened_source", path, "Field extraction requires opened original full/partial text; index, abstract, metadata, and failed attempts cannot support it."))
        if source is None or source["underlyingWorkId"] is None:
            issues.append(_issue("extraction_work_identity_missing", path, "An extracted field needs a resolvable underlying work identity."))
        if extraction["value"] is None or (isinstance(extraction["value"], str) and not extraction["value"].strip()):
            issues.append(_issue("empty_extracted_value", f"{path}.value", "Do not create an empty field claim."))
        if extraction["valueHash"] != value_hash(extraction["value"]):
            issues.append(_issue("field_value_hash_mismatch", f"{path}.valueHash", "Field value hash does not match canonical JSON value."))
        expected_ref = {"sourceId": access["sourceId"], "accessId": access["id"], "locator": access["locator"]}
        if extraction["reference"] != expected_ref:
            issues.append(_issue("extraction_reference_mismatch", f"{path}.reference", "Source/access/locator reference must exactly match the opened access record."))
        identity = (extraction["subjectId"], extraction["field"], extraction["accessId"], extraction["valueHash"])
        if identity in extraction_identity:
            issues.append(_issue("duplicate_extraction_identity", f"{path}", f"Repeated field extraction; first recorded as {extraction_identity[identity]!r}."))
        else:
            extraction_identity[identity] = extraction["id"]

    seen_pairs: set[tuple[str, str, str, str]] = set()
    for i, comparison in enumerate(manifest["comparisons"]):
        path = f"$.comparisons[{i}]"
        register(comparison["id"], f"{path}.id")
        left = extractions.get(comparison["leftExtractionId"])
        right = extractions.get(comparison["rightExtractionId"])
        if left is None or right is None:
            issues.append(_issue("orphan_comparison_extraction", path, "Both comparison references must resolve to field extractions."))
            continue
        if left["id"] == right["id"]:
            issues.append(_issue("self_comparison", path, "A comparison needs two distinct field observations."))
        if (left["subjectId"], left["field"]) != (right["subjectId"], right["field"]):
            issues.append(_issue("comparison_scope_mismatch", path, "Compared extractions must refer to the same subject and field."))
        if (comparison["subjectId"], comparison["field"]) != (left["subjectId"], left["field"]):
            issues.append(_issue("comparison_declared_scope_mismatch", path, "Comparison subject/field must match both extractions."))
        pair = (comparison["subjectId"], comparison["field"], *sorted((left["id"], right["id"])))
        if pair in seen_pairs:
            issues.append(_issue("duplicate_comparison_pair", path, "The same extraction pair may be compared only once."))
        seen_pairs.add(pair)
        if comparison["classification"] not in COMPARISON_CLASSES:
            issues.append(_issue("unknown_comparison_class", f"{path}.classification", "Comparison class is outside the supported vocabulary."))

    return issues


def _source_hash(source: dict[str, Any]) -> str:
    return sha256(canonical(source))


def _access_hash(access: dict[str, Any], source_hash_value: str) -> str:
    return sha256(canonical({"sourceHash": source_hash_value, "access": access}))


def _record_hash(record: dict[str, Any]) -> str:
    return sha256(canonical(record))


def build_artifacts(manifest: dict[str, Any]) -> dict[str, str]:
    source_by_id = {row["id"]: row for row in manifest["sources"]}
    access_by_id = {row["id"]: row for row in manifest["accesses"]}
    extraction_by_id = {row["id"]: row for row in manifest["extractions"]}
    source_hashes = {key: _source_hash(row) for key, row in source_by_id.items()}
    fingerprint = sha256(canonical(manifest))

    sources_out = []
    for source in manifest["sources"]:
        row = dict(source)
        row["sourceHash"] = source_hashes[source["id"]]
        sources_out.append(row)
    accesses_out = []
    for access in manifest["accesses"]:
        source = source_by_id[access["sourceId"]]
        source_hash_value = source_hashes[source["id"]]
        original_open = access["accessOutcome"] == "opened" and access["textAccess"] in OBSERVED_ORIGINAL_ACCESS
        row = {
            **access,
            "source": dict(source),
            "sourceHash": source_hash_value,
            "accessHash": _access_hash(access, source_hash_value),
            "openedOriginalText": original_open,
            "supportsFieldExtraction": original_open or (manifest["fixtureOnly"] and access["textAccess"] == "fixture_only" and access["accessOutcome"] == "opened"),
        }
        accesses_out.append(row)
    observations_out = []
    for extraction in manifest["extractions"]:
        access = access_by_id[extraction["accessId"]]
        record = {
            **extraction,
            "sourceId": access["sourceId"],
            "locator": access["locator"],
            "accessedOn": access["accessedOn"],
            "accessMethod": access["accessMethod"],
            "textAccess": access["textAccess"],
            "underlyingWorkId": source_by_id[access["sourceId"]]["underlyingWorkId"],
        }
        record["recordHash"] = _record_hash(record)
        observations_out.append(record)

    comparisons_out = []
    compared_extractions: set[str] = set()
    for comparison in manifest["comparisons"]:
        left = extraction_by_id[comparison["leftExtractionId"]]
        right = extraction_by_id[comparison["rightExtractionId"]]
        left_access, right_access = access_by_id[left["accessId"]], access_by_id[right["accessId"]]
        left_work = source_by_id[left_access["sourceId"]]["underlyingWorkId"]
        right_work = source_by_id[right_access["sourceId"]]["underlyingWorkId"]
        if left_work is None or right_work is None:
            relation = "unknown"
        elif left_work == right_work:
            relation = "same_underlying_work"
        else:
            relation = "independent_underlying_works"
        comparisons_out.append({
            **comparison,
            "leftValueHash": left["valueHash"],
            "rightValueHash": right["valueHash"],
            "underlyingWorkRelationship": relation,
        })
        compared_extractions.update((left["id"], right["id"]))

    summary_rows = []
    for subject in manifest["subjects"]:
        for field in subject["fields"]:
            accesses = [row for row in manifest["accesses"] if row["subjectId"] == subject["id"] and row["field"] == field]
            access_ids = {row["id"] for row in accesses}
            observations = [row for row in manifest["extractions"] if row["accessId"] in access_ids]
            comparisons = [row for row in manifest["comparisons"] if row["subjectId"] == subject["id"] and row["field"] == field]
            works = {
                source_by_id[access_by_id[row["accessId"]]["sourceId"]]["underlyingWorkId"]
                for row in observations
                if source_by_id[access_by_id[row["accessId"]]["sourceId"]]["underlyingWorkId"] is not None
            }
            opened_original = sum(
                row["accessOutcome"] == "opened" and row["textAccess"] in OBSERVED_ORIGINAL_ACCESS
                for row in accesses
            )
            index_only = sum(row["accessOutcome"] == "opened" and row["textAccess"] == "index_only" for row in accesses)
            failed = sum(row["accessOutcome"] == "failed" for row in accesses)
            possible_pairs = len(observations) * (len(observations) - 1) // 2
            classes = sorted({row["classification"] for row in comparisons})
            if any(row["classification"] == "substantive_conflict" for row in comparisons):
                outcome = "conflicted"
            elif observations and possible_pairs > len(comparisons):
                outcome = "comparison_incomplete"
            elif comparisons:
                outcome = "comparison_recorded_no_approval"
            elif observations:
                outcome = "single_observation" if len(observations) == 1 else "awaiting_comparison"
            elif failed:
                outcome = "unavailable"
            elif index_only or any(row["textAccess"] in {"abstract_only", "metadata_only"} for row in accesses):
                outcome = "original_not_opened"
            elif opened_original:
                outcome = "opened_without_extraction"
            elif accesses:
                outcome = "no_supporting_original"
            else:
                outcome = "unresearched"
            summary_rows.append({
                "subjectId": subject["id"],
                "field": field,
                "accessAttemptCount": len(accesses),
                "openedOriginalAccessCount": opened_original,
                "indexOnlyAccessCount": index_only,
                "failedAccessCount": failed,
                "extractionCount": len(observations),
                "observedUnderlyingWorkCount": len(works),
                "comparisonCount": len(comparisons),
                "possiblePairCount": possible_pairs,
                "comparisonClasses": classes,
                "comparisonOutcome": outcome,
                "humanAnatomyReview": "not_performed_by_this_tool",
            })

    exceptions: list[dict[str, Any]] = []
    for access in manifest["accesses"]:
        source = source_by_id[access["sourceId"]]
        if access["accessOutcome"] == "failed":
            exceptions.append({
                "kind": "unavailable",
                "subjectId": access["subjectId"], "field": access["field"],
                "sourceId": source["id"], "accessId": access["id"],
                "url": source["url"], "locator": access["locator"],
                "reason": access["failureReason"],
            })
        elif access["textAccess"] == "index_only":
            exceptions.append({
                "kind": "index_only_not_source_text",
                "subjectId": access["subjectId"], "field": access["field"],
                "sourceId": source["id"], "accessId": access["id"],
                "url": source["url"], "locator": access["locator"],
                "reason": "Search index/snippet was opened, but original field text was not opened and cannot support an extraction.",
            })
        elif access["textAccess"] in {"abstract_only", "metadata_only", "legacy_record", "fixture_only"}:
            exceptions.append({
                "kind": "non_full_text_not_claim_support",
                "subjectId": access["subjectId"], "field": access["field"],
                "sourceId": source["id"], "accessId": access["id"],
                "url": source["url"], "locator": access["locator"],
                "reason": "The accessed item is an abstract, metadata, legacy row, or test fixture; it is not treated as opened field-level original text.",
            })
        elif access["textAccess"] in OBSERVED_ORIGINAL_ACCESS and not any(row["accessId"] == access["id"] for row in manifest["extractions"]):
            exceptions.append({
                "kind": "opened_without_field_extraction",
                "subjectId": access["subjectId"], "field": access["field"],
                "sourceId": source["id"], "accessId": access["id"],
                "url": source["url"], "locator": access["locator"],
                "reason": "Original text was opened but no field extraction was entered.",
            })
    for row in comparisons_out:
        if row["classification"] in {"variation", "substantive_conflict", "not_comparable"}:
            exceptions.append({
                "kind": row["classification"], "subjectId": row["subjectId"], "field": row["field"],
                "comparisonId": row["id"], "leftExtractionId": row["leftExtractionId"],
                "rightExtractionId": row["rightExtractionId"], "rationale": row["rationale"],
                "underlyingWorkRelationship": row["underlyingWorkRelationship"],
            })
    for row in summary_rows:
        if row["comparisonOutcome"] == "comparison_incomplete":
            exceptions.append({
                "kind": "comparison_incomplete", "subjectId": row["subjectId"], "field": row["field"],
                "reason": "Not every pair of entered observations has an explicit comparison record.",
                "possiblePairCount": row["possiblePairCount"], "comparisonCount": row["comparisonCount"],
            })

    def json_artifact(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n"

    access_artifact = {
        "schemaVersion": "1.0.0", "manifestId": manifest["manifestId"],
        "inputFingerprint": fingerprint, "fixtureOnly": manifest["fixtureOnly"],
        "sources": sources_out, "accesses": accesses_out,
        "humanAnatomyReview": {"performed": False, "status": "not_performed_by_this_tool", "reviewer": None},
    }
    extraction_artifact = {
        "schemaVersion": "1.0.0", "manifestId": manifest["manifestId"],
        "inputFingerprint": fingerprint, "fixtureOnly": manifest["fixtureOnly"],
        "observations": observations_out,
        "humanAnatomyReview": {"performed": False, "status": "not_performed_by_this_tool", "reviewer": None},
    }
    comparison_artifact = _comparison_csv(manifest, source_by_id, access_by_id, extraction_by_id)
    summary_artifact = {
        "schemaVersion": "1.0.0", "manifestId": manifest["manifestId"],
        "inputFingerprint": fingerprint, "fixtureOnly": manifest["fixtureOnly"],
        "subjectCount": len(manifest["subjects"]), "sourceRecordCount": len(sources_out),
        "accessAttemptCount": len(accesses_out), "fieldExtractionCount": len(observations_out),
        "comparisonRecordCount": len(comparisons_out), "fieldSummaries": summary_rows,
        "comparisonClassCounts": {key: sum(row["classification"] == key for row in comparisons_out) for key in sorted(COMPARISON_CLASSES)},
        "humanAnatomyReview": {"performed": False, "status": "not_performed_by_this_tool", "reviewer": None},
        "promotion": {"aiEvidenceApproval": "none", "canonicalClaimsWritten": False, "productionOverlayWritten": False},
    }
    exception_artifact = {
        "schemaVersion": "1.0.0", "manifestId": manifest["manifestId"],
        "inputFingerprint": fingerprint, "fixtureOnly": manifest["fixtureOnly"],
        "exceptionCount": len(exceptions), "exceptions": exceptions,
    }
    return {
        "access-ledger.json": json_artifact(access_artifact),
        "field-observations.json": json_artifact(extraction_artifact),
        "comparison-table.csv": comparison_artifact,
        "run-summary.json": json_artifact(summary_artifact),
        "exceptions.json": json_artifact(exception_artifact),
    }


def _comparison_csv(
    manifest: dict[str, Any], source_by_id: dict[str, dict[str, Any]],
    access_by_id: dict[str, dict[str, Any]], extraction_by_id: dict[str, dict[str, Any]],
) -> str:
    headers = [
        "rowKind", "subjectId", "field", "extractionId", "value", "valueHash",
        "sourceId", "underlyingWorkId", "url", "editionStatus", "edition",
        "accessId", "locator", "accessedOn", "accessMethod", "textAccess",
        "classification", "assessmentMode", "comparisonId", "comparedWith",
        "underlyingWorkRelationship", "rationale",
    ]
    rows: list[dict[str, Any]] = []
    comparisons_by_extraction: dict[str, list[dict[str, Any]]] = {}
    for comparison in manifest["comparisons"]:
        comparisons_by_extraction.setdefault(comparison["leftExtractionId"], []).append(comparison)
        comparisons_by_extraction.setdefault(comparison["rightExtractionId"], []).append(comparison)
    for extraction in manifest["extractions"]:
        access = access_by_id[extraction["accessId"]]
        source = source_by_id[access["sourceId"]]
        comparisons = comparisons_by_extraction.get(extraction["id"], [])
        if not comparisons:
            rows.append(_csv_extraction_row(extraction, access, source, "not_compared", "", "", "", "", ""))
        for comparison in comparisons:
            other_id = comparison["rightExtractionId"] if comparison["leftExtractionId"] == extraction["id"] else comparison["leftExtractionId"]
            other_access = access_by_id[extraction_by_id[other_id]["accessId"]]
            other_source = source_by_id[other_access["sourceId"]]
            this_work, other_work = source["underlyingWorkId"], other_source["underlyingWorkId"]
            relationship = "unknown" if this_work is None or other_work is None else ("same_underlying_work" if this_work == other_work else "independent_underlying_works")
            rows.append(_csv_extraction_row(
                extraction, access, source, comparison["classification"], comparison["assessmentMode"],
                comparison["id"], other_id, relationship, comparison["rationale"],
            ))
    observed_access_ids = {row["accessId"] for row in manifest["extractions"]}
    for access in manifest["accesses"]:
        if access["id"] in observed_access_ids:
            continue
        source = source_by_id[access["sourceId"]]
        classification = "unavailable" if access["accessOutcome"] == "failed" else (
            "index_only" if access["textAccess"] == "index_only" else "not_original_field_text"
        )
        rows.append({
            "rowKind": "source_access_exception", "subjectId": access["subjectId"], "field": access["field"],
            "extractionId": "", "value": "", "valueHash": "", "sourceId": source["id"],
            "underlyingWorkId": source["underlyingWorkId"] or "", "url": source["url"],
            "editionStatus": source["editionStatus"], "edition": source["edition"] or "",
            "accessId": access["id"], "locator": access["locator"], "accessedOn": access["accessedOn"],
            "accessMethod": access["accessMethod"], "textAccess": access["textAccess"],
            "classification": classification, "assessmentMode": "", "comparisonId": "", "comparedWith": "",
            "underlyingWorkRelationship": "", "rationale": access.get("failureReason", access["note"]),
        })
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=headers, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return stream.getvalue()


def _csv_extraction_row(
    extraction: dict[str, Any], access: dict[str, Any], source: dict[str, Any],
    classification: str, assessment_mode: str, comparison_id: str, compared_with: str,
    work_relationship: str, rationale: str,
) -> dict[str, Any]:
    return {
        "rowKind": "field_observation", "subjectId": extraction["subjectId"], "field": extraction["field"],
        "extractionId": extraction["id"], "value": canonical(extraction["value"]), "valueHash": extraction["valueHash"],
        "sourceId": source["id"], "underlyingWorkId": source["underlyingWorkId"] or "", "url": source["url"],
        "editionStatus": source["editionStatus"], "edition": source["edition"] or "", "accessId": access["id"],
        "locator": access["locator"], "accessedOn": access["accessedOn"], "accessMethod": access["accessMethod"],
        "textAccess": access["textAccess"], "classification": classification, "assessmentMode": assessment_mode,
        "comparisonId": comparison_id, "comparedWith": compared_with,
        "underlyingWorkRelationship": work_relationship, "rationale": rationale,
    }


def _artifact_fingerprint(artifacts: dict[str, str]) -> str:
    return sha256(canonical({name: sha256(contents) for name, contents in sorted(artifacts.items())}))


def _is_below(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _ensure_safe_output_path(path: Path) -> Path:
    resolved = path.resolve()
    project_root = ROOT.resolve()
    evidence_root = (ROOT / "work/evidence").resolve()
    if resolved == project_root or (_is_below(resolved, project_root) and not _is_below(resolved, evidence_root)):
        raise ValueError("Project writes are limited to work/evidence/; choose a local path outside the project for other output.")
    return resolved


def run_manifest(
    manifest: dict[str, Any], output_dir: Path, cache_path: Path | None = None,
) -> tuple[bool, str, dict[str, str]]:
    fingerprint = sha256(canonical(manifest))
    output_dir = _ensure_safe_output_path(output_dir)
    cache_path = _ensure_safe_output_path(cache_path or output_dir / ".source-research-cache.json")
    if cache_path == output_dir or cache_path in {output_dir / name for name in OUTPUT_NAMES}:
        raise ValueError("Cache path must be separate from the output directory and its report files.")
    if _is_below(cache_path, (ROOT / "work/evidence").resolve()) and not _is_below(cache_path, output_dir):
        raise ValueError("A project-local cache must stay inside the selected output directory.")
    cache = None
    try:
        cache = load_json(cache_path)
    except (OSError, json.JSONDecodeError):
        cache = None
    cache_hit = False
    artifacts: dict[str, str] | None = None
    if isinstance(cache, dict) and cache.get("cacheVersion") == CACHE_VERSION and cache.get("inputFingerprint") == fingerprint:
        candidate = cache.get("artifacts")
        if (
            isinstance(candidate, dict)
            and set(candidate) == set(OUTPUT_NAMES)
            and all(isinstance(k, str) and Path(k).name == k and isinstance(v, str) for k, v in candidate.items())
        ):
            declared = cache.get("artifactHashes", {})
            if set(candidate) == set(declared) and all(sha256(candidate[name]) == declared[name] for name in candidate):
                artifacts = candidate
                cache_hit = True
    if artifacts is None:
        artifacts = build_artifacts(manifest)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in artifacts.items():
        _atomic_write(output_dir / name, content)
    result_fingerprint = _artifact_fingerprint(artifacts)
    cache_record = {
        "cacheVersion": CACHE_VERSION,
        "inputFingerprint": fingerprint,
        "resultFingerprint": result_fingerprint,
        "artifactHashes": {name: sha256(contents) for name, contents in sorted(artifacts.items())},
        "artifacts": {name: content for name, content in sorted(artifacts.items())},
    }
    _atomic_write(cache_path, json.dumps(cache_record, ensure_ascii=False, indent=2) + "\n")
    return cache_hit, fingerprint, artifacts


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False, prefix=f".{path.name}.", suffix=".tmp") as handle:
        handle.write(text)
        temporary = Path(handle.name)
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a local source manifest and emit a provenance-bound comparison report.")
    parser.add_argument("--manifest", type=Path, help="Explicitly entered local JSON manifest; no network access is performed.")
    parser.add_argument("--output-dir", type=Path, help="Directory for local generated reports.")
    parser.add_argument("--cache-file", type=Path, help="Optional cache file. Defaults to .source-research-cache.json under output-dir.")
    parser.add_argument("--allow-synthetic-fixtures", action="store_true", help="Test-only switch for synthetic fixture manifests.")
    parser.add_argument("--hash-value", help="Print canonical SHA-256 for one JSON value, for preparing valueHash.")
    parser.add_argument("--check-schema", action="store_true", help="Validate the manifest schema with the project schema subset checker.")
    args = parser.parse_args(argv)
    if args.hash_value is not None:
        try:
            value = json.loads(args.hash_value)
        except json.JSONDecodeError as exc:
            print(f"Invalid JSON value: {exc}", file=sys.stderr)
            return 2
        print(value_hash(value))
        return 0
    schema = load_json(SCHEMA_PATH)
    if args.check_schema:
        schema_problems = _T03.check_schema(schema)
        if schema_problems:
            print(json.dumps([dict(row) for row in schema_problems], ensure_ascii=False, indent=2), file=sys.stderr)
            return 2
        print("source research schema: valid")
        return 0
    if args.manifest is None or args.output_dir is None:
        parser.error("--manifest and --output-dir are required unless --hash-value or --check-schema is used")
    try:
        _ensure_safe_output_path(args.output_dir)
        if args.cache_file is not None:
            _ensure_safe_output_path(args.cache_file)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    try:
        manifest = load_json(args.manifest)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read manifest: {exc}", file=sys.stderr)
        return 2
    issues = validate_manifest(
        manifest,
        schema=schema,
        allow_synthetic_fixtures=args.allow_synthetic_fixtures,
    )
    if issues:
        print(json.dumps({"pass": False, "issues": issues}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    cache_hit, fingerprint, artifacts = run_manifest(manifest, args.output_dir, args.cache_file)
    print(json.dumps({
        "pass": True,
        "manifestId": manifest["manifestId"],
        "fixtureOnly": manifest["fixtureOnly"],
        "subjectCount": len(manifest["subjects"]),
        "inputFingerprint": fingerprint,
        "cache": "hit" if cache_hit else "miss_or_invalidated",
        "outputFiles": sorted(artifacts),
        "outputDirectory": str(args.output_dir),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
