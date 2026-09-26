#!/usr/bin/env python3
"""Test-only regressions for the local T17 source workflow."""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = HERE.parents[1] / "work/evidence/T17/fixtures/synthetic-manifest.json"
SPEC = importlib.util.spec_from_file_location("source_research", HERE / "source_research.py")
assert SPEC is not None and SPEC.loader is not None
source_research = importlib.util.module_from_spec(SPEC)
import sys
sys.modules[SPEC.name] = source_research
SPEC.loader.exec_module(source_research)


def fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def issue_codes(manifest: dict, *, allow_fixture: bool = True) -> set[str]:
    return {row["code"] for row in source_research.validate_manifest(manifest, allow_synthetic_fixtures=allow_fixture)}


class SourceResearchTests(unittest.TestCase):
    def test_synthetic_fixture_validates_only_with_explicit_test_flag(self) -> None:
        manifest = fixture()
        self.assertEqual(issue_codes(manifest, allow_fixture=True), set())
        self.assertIn("synthetic_fixture_not_enabled", issue_codes(manifest, allow_fixture=False))

    def test_run_keeps_comparison_classes_work_identity_and_review_separate(self) -> None:
        manifest = fixture()
        artifacts = source_research.build_artifacts(manifest)
        summary = json.loads(artifacts["run-summary.json"])
        table = artifacts["comparison-table.csv"]
        exceptions = json.loads(artifacts["exceptions.json"])
        field = summary["fieldSummaries"][0]
        self.assertEqual(summary["subjectCount"], 1)
        self.assertTrue(summary["fixtureOnly"])
        self.assertEqual(field["observedUnderlyingWorkCount"], 2)
        self.assertEqual(field["comparisonCount"], field["possiblePairCount"])
        self.assertEqual(field["comparisonOutcome"], "conflicted")
        self.assertEqual(field["humanAnatomyReview"], "not_performed_by_this_tool")
        self.assertEqual(summary["promotion"], {
            "aiEvidenceApproval": "none", "canonicalClaimsWritten": False, "productionOverlayWritten": False
        })
        self.assertIn("same_underlying_work", table)
        self.assertIn("independent_underlying_works", table)
        self.assertIn("wording_difference", table)
        self.assertIn("variation", table)
        self.assertIn("substantive_conflict", table)
        kinds = {row["kind"] for row in exceptions["exceptions"]}
        self.assertIn("unavailable", kinds)
        self.assertIn("index_only_not_source_text", kinds)
        self.assertIn("variation", kinds)
        self.assertIn("substantive_conflict", kinds)
        self.assertNotIn("reviewState", artifacts["run-summary.json"])
        self.assertNotIn("humanReviewed", artifacts["run-summary.json"])

    def test_duplicate_access_does_not_become_a_second_source_record(self) -> None:
        manifest = fixture()
        duplicate = copy.deepcopy(manifest["accesses"][0])
        duplicate["id"] = "ACC-SYN-A-DUP"
        manifest["accesses"].append(duplicate)
        self.assertIn("duplicate_access_identity", issue_codes(manifest))

    def test_duplicate_field_extraction_is_not_counted_twice(self) -> None:
        manifest = fixture()
        duplicate = copy.deepcopy(manifest["extractions"][0])
        duplicate["id"] = "OBS-SYN-A-DUP"
        manifest["extractions"].append(duplicate)
        self.assertIn("duplicate_extraction_identity", issue_codes(manifest))

    def test_two_urls_for_one_work_are_not_independent(self) -> None:
        manifest = fixture()
        artifacts = source_research.build_artifacts(manifest)
        table = artifacts["comparison-table.csv"]
        self.assertIn("same_underlying_work", table)
        summary = json.loads(artifacts["run-summary.json"])
        self.assertEqual(summary["fieldSummaries"][0]["observedUnderlyingWorkCount"], 2)
        self.assertLess(summary["fieldSummaries"][0]["observedUnderlyingWorkCount"], summary["fieldSummaries"][0]["extractionCount"])

    def test_manifest_is_capped_at_six_subjects(self) -> None:
        manifest = fixture()
        for index in range(2, 8):
            manifest["subjects"].append({
                "id": f"SYNTHETIC-MUSCLE-{index:02d}", "kind": "individual_muscle",
                "recordType": "synthetic_fixture", "fields": ["origin"],
            })
        self.assertIn("schema_maxItems", issue_codes(manifest))

    def test_canonical_subject_id_must_exist_in_the_current_catalog(self) -> None:
        manifest = fixture()
        manifest["fixtureOnly"] = False
        manifest["subjects"][0].update({"id": "HA-M-999999", "recordType": "canonical"})
        for access in manifest["accesses"]:
            if access["accessMethod"] == "synthetic_fixture":
                access["accessMethod"] = "secondary_full_text"
                access["textAccess"] = "full_text_opened"
        for extraction in manifest["extractions"]:
            extraction["subjectId"] = "HA-M-999999"
        for comparison in manifest["comparisons"]:
            comparison["subjectId"] = "HA-M-999999"
        self.assertIn("orphan_canonical_subject", issue_codes(manifest, allow_fixture=False))

    def test_index_only_extraction_is_rejected(self) -> None:
        manifest = fixture()
        extraction = copy.deepcopy(manifest["extractions"][0])
        extraction.update({
            "id": "OBS-SYN-INDEX-INVALID", "accessId": "ACC-SYN-INDEX",
            "reference": {"sourceId": "SRC-SYN-INDEX", "accessId": "ACC-SYN-INDEX", "locator": "Synthetic result snippet 1"},
        })
        manifest["extractions"].append(extraction)
        self.assertIn("extraction_without_opened_source", issue_codes(manifest))

    def test_failed_access_cannot_be_marked_as_success(self) -> None:
        manifest = fixture()
        failed = next(row for row in manifest["accesses"] if row["id"] == "ACC-SYN-FAILED")
        failed["accessOutcome"] = "opened"
        failed["textAccess"] = "full_text_opened"
        self.assertIn("opened_access_has_failure_reason", issue_codes(manifest))
        self.assertIn("opened_edition_unresolved", issue_codes(manifest))

    def test_field_hash_and_source_reference_are_verified(self) -> None:
        manifest = fixture()
        manifest["extractions"][0]["value"] += " changed"
        self.assertIn("field_value_hash_mismatch", issue_codes(manifest))
        manifest = fixture()
        manifest["extractions"][0]["reference"]["locator"] = "Different locator"
        self.assertIn("extraction_reference_mismatch", issue_codes(manifest))

    def test_output_source_access_and_observation_hashes_are_reproducible(self) -> None:
        manifest = fixture()
        artifacts = source_research.build_artifacts(manifest)
        ledger = json.loads(artifacts["access-ledger.json"])
        observations = json.loads(artifacts["field-observations.json"])["observations"]
        source = next(row for row in ledger["sources"] if row["id"] == "SRC-SYN-A")
        source_metadata = {key: value for key, value in source.items() if key != "sourceHash"}
        self.assertEqual(source["sourceHash"], source_research._source_hash(source_metadata))
        access = next(row for row in ledger["accesses"] if row["id"] == "ACC-SYN-A")
        input_access = next(row for row in manifest["accesses"] if row["id"] == "ACC-SYN-A")
        self.assertEqual(access["accessHash"], source_research._access_hash(input_access, source["sourceHash"]))
        for row in observations:
            self.assertEqual(row["valueHash"], source_research.value_hash(row["value"]))
            record = {key: value for key, value in row.items() if key != "recordHash"}
            self.assertEqual(row["recordHash"], source_research._record_hash(record))

    def test_unverified_edition_must_remain_null_and_access_failure_is_explicit(self) -> None:
        manifest = fixture()
        manifest["sources"][0]["editionStatus"] = "not_exposed"
        manifest["sources"][0]["edition"] = "guessed edition"
        self.assertIn("unverified_edition_filled", issue_codes(manifest))
        report = json.loads(source_research.build_artifacts(fixture())["access-ledger.json"])
        failed = next(row for row in report["accesses"] if row["id"] == "ACC-SYN-FAILED")
        self.assertEqual(failed["accessOutcome"], "failed")
        self.assertFalse(failed["openedOriginalText"])
        self.assertFalse(failed["supportsFieldExtraction"])

    def test_opened_source_requires_valid_url_and_exact_or_explicitly_unexposed_edition(self) -> None:
        manifest = fixture()
        manifest["sources"][0]["url"] = "https://"
        manifest["sources"][0]["editionStatus"] = "verified"
        manifest["sources"][0]["edition"] = None
        codes = issue_codes(manifest)
        self.assertIn("invalid_source_url", codes)
        self.assertIn("verified_edition_missing", codes)

    def test_ai_or_human_approval_fields_are_rejected(self) -> None:
        manifest = fixture()
        manifest["humanReview"] = {"status": "reviewed"}
        self.assertIn("schema_additional_property", issue_codes(manifest))

    def test_output_and_cache_cannot_target_canonical_or_opensim_trees(self) -> None:
        with self.assertRaises(ValueError):
            source_research._ensure_safe_output_path(source_research.ROOT / "atlas-data/terminology")
        with self.assertRaises(ValueError):
            source_research._ensure_safe_output_path(source_research.ROOT / "OpenSim_Models/source-cache.json")
        self.assertEqual(
            source_research._ensure_safe_output_path(source_research.ROOT / "work/evidence/T17/local-output"),
            (source_research.ROOT / "work/evidence/T17/local-output").resolve(),
        )
        with self.assertRaises(ValueError):
            source_research._ensure_safe_output_path(source_research.ROOT / "work/STATUS.md")

    def test_cache_cannot_overwrite_a_report_artifact(self) -> None:
        manifest = fixture()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "reports"
            collision = output / "access-ledger.json"
            with self.assertRaises(ValueError):
                source_research.run_manifest(manifest, output, collision)

    def test_tampered_cache_artifact_names_cannot_escape_output_directory(self) -> None:
        manifest = fixture()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "reports"
            cache = root / "cache.json"
            malicious_name = "../../escaped.txt"
            content = "must not be written"
            cache.write_text(json.dumps({
                "cacheVersion": source_research.CACHE_VERSION,
                "inputFingerprint": source_research.sha256(source_research.canonical(manifest)),
                "artifactHashes": {malicious_name: source_research.sha256(content)},
                "artifacts": {malicious_name: content},
            }), encoding="utf-8")
            cache_hit, _, artifacts = source_research.run_manifest(manifest, output, cache)
            self.assertFalse(cache_hit)
            self.assertEqual(set(artifacts), set(source_research.OUTPUT_NAMES))
            self.assertFalse((root / "escaped.txt").exists())

    def test_rerun_is_stable_and_cache_invalidates_when_source_changes(self) -> None:
        manifest = fixture()
        self.assertEqual(issue_codes(manifest), set())
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "reports"
            cache = Path(temporary) / "cache.json"
            first_hit, first_fingerprint, first_artifacts = source_research.run_manifest(manifest, output, cache)
            first_bytes = {name: (output / name).read_bytes() for name in first_artifacts}
            self.assertFalse(first_hit)
            second_hit, second_fingerprint, second_artifacts = source_research.run_manifest(manifest, output, cache)
            self.assertTrue(second_hit)
            self.assertEqual(first_fingerprint, second_fingerprint)
            self.assertEqual(first_artifacts, second_artifacts)
            self.assertEqual(first_bytes, {name: (output / name).read_bytes() for name in first_artifacts})
            changed = copy.deepcopy(manifest)
            changed["sources"][0]["title"] = "Synthetic source A revised title"
            changed["extractions"][0]["value"] += " (revised field value)"
            changed["extractions"][0]["valueHash"] = source_research.value_hash(changed["extractions"][0]["value"])
            self.assertEqual(issue_codes(changed), set())
            third_hit, third_fingerprint, third_artifacts = source_research.run_manifest(changed, output, cache)
            self.assertFalse(third_hit)
            self.assertNotEqual(first_fingerprint, third_fingerprint)
            self.assertNotEqual(first_artifacts["access-ledger.json"], third_artifacts["access-ledger.json"])
            self.assertNotEqual(first_artifacts["field-observations.json"], third_artifacts["field-observations.json"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
