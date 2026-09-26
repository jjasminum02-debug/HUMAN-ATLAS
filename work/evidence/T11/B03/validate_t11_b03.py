"""Validate T11-B03 coverage, same-ID naming, provenance, and review separation."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
IDS = [f"HA-G-{number:06d}" for number in range(11, 17)] + [f"HA-M-{number:06d}" for number in range(7, 11)]
FIELDS = {"label", "korean", "hanja", "english", "aliases[0]"}
CHECKED = "2026-09-25"


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


names = read("atlas-data/terminology/learning-names.json")
ledger = read("atlas-data/terminology/term-review-batches.json")
catalog_data = read("atlas-data/catalog/canonical-catalog.json")["entities"]
crosswalk = read("atlas-data/catalog/source-crosswalk.json")
canonical = {row["id"]: row for row in catalog_data["muscleConcepts"]}
coverage = {row["id"]: row for row in ledger["canonicalCoverage"]}
names_by_id = {row["id"]: row for row in names["entries"]}
entries = [row for row in ledger["entries"] if row["id"] in IDS]
evidence = [row for row in ledger["fieldEvidence"] if row["entryId"] in IDS]
batch = next(row for row in ledger["batchOrder"] if row["batchId"] == "T11-B03")

assert [row["id"] for row in ledger["canonicalCoverage"] if row["batchId"] == "T11-B03"] == IDS
assert batch["canonicalIds"] == IDS and batch["size"] == 10 and batch["status"] == "complete_with_gaps"
assert len(entries) == 10 and {row["id"] for row in entries} == set(IDS)
assert len(evidence) == 50
assert all(coverage[identifier]["status"] == "web_checked_with_gaps" for identifier in IDS)
assert ledger["overallT11Status"] == "in_progress_partial"
assert sum(1 for row in ledger["canonicalCoverage"] if row["status"] == "web_checked_with_gaps") == 28

expected = {
    "HA-G-000011": (None, None, None),
    "HA-G-000012": (None, None, None),
    "HA-G-000013": ("종아리앞칸", "종아리앞칸", None),
    "HA-G-000014": ("종아리가쪽칸", "종아리가쪽칸", None),
    "HA-G-000015": ("종아리뒤칸", "종아리뒤칸", None),
    "HA-G-000016": (None, None, None),
    "HA-M-000007": ("상직근", "위곧은근", "上直筋"),
    "HA-M-000008": ("하직근", "아래곧은근", "下直筋"),
    "HA-M-000009": ("내직근", "안쪽곧은근", "內直筋"),
    "HA-M-000010": ("외직근", "가쪽곧은근", "外直筋"),
}
expected_overlays = {identifier for identifier, values in expected.items() if values[0] is not None}
assert {identifier for identifier in IDS if identifier in names_by_id} == expected_overlays

field_by_id = {identifier: {row["field"]: row for row in entries_by_id["fieldEvidence"]} for identifier, entries_by_id in ((row["id"], row) for row in entries)}
all_source_ids = set(names["sources"])
assert {source_id for source_id in all_source_ids if source_id.startswith("fipat-ta2-b03-") or source_id.startswith("kmle-b03-") or source_id.startswith("ko-wiki-b03-") or source_id.startswith("nikl-b03-")} == {source_id for source_id in ledger["sources"] if source_id.startswith("fipat-ta2-b03-") or source_id.startswith("kmle-b03-") or source_id.startswith("ko-wiki-b03-") or source_id.startswith("nikl-b03-")}
assert len(evidence) == len({(row["entryId"], row["field"]) for row in evidence})

for identifier in IDS:
    row = next(item for item in entries if item["id"] == identifier)
    concept = canonical[identifier]
    loc = coverage[identifier]["sourceCrosswalkLocator"]
    assert row["entityType"] == concept["entityType"]
    assert row["parentId"] == concept.get("parentId")
    assert row["canonicalSourceRow"] == {"sourceId": "FIPAT_TA2", "tableRow": loc["tableRow"], "printedPage": loc["printedPage"]}
    assert row["webVerificationStatus"] == "web_checked_with_gaps"
    assert row["humanReviewed"] is False and row["humanAnatomyReviewStatus"] == "not_performed" and row["humanReviewer"] is None
    assert row["fieldEvidenceCount"] == 5
    fields = field_by_id[identifier]
    assert set(fields) == FIELDS
    label, korean, hanja = expected[identifier]
    assert (fields["label"]["value"], fields["korean"]["value"], fields["hanja"]["value"]) == (label, korean, hanja)
    assert fields["english"]["value"] == loc["englishTextObservation"]
    assert fields["aliases[0]"]["value"] == loc["latinTextObservation"]
    for field in fields.values():
        assert field["entryId"] == identifier
        assert field["humanReviewed"] is False and field["humanAnatomyReviewStatus"] == "not_performed"
        if field["value"] is None:
            assert field["missingReason"]
        else:
            assert field["missingReason"] is None
        assert field["evidence"], (identifier, field["field"])
        for ev in field["evidence"]:
            sid = ev["sourceId"]
            assert sid in all_source_ids and sid in ledger["sources"]
            source = names["sources"][sid]
            manifest_source = ledger["sources"][sid]
            assert source == manifest_source
            assert source.get("url", "").startswith("https://")
            assert source.get("edition") and source.get("accessDate") == CHECKED
            assert ev["sourceEdition"] == source["edition"]
            assert ev["checkedDate"] == CHECKED
            assert ev["locator"] and ev["verificationMode"]
            if field["field"] in ("english", "aliases[0]"):
                assert f"table row {loc['tableRow']}" in ev["locator"]
    term_rows = [term for term in crosswalk["termRecords"] if term["conceptId"] == identifier and term["sourceTextObserved"]]
    assert {term["sourceLanguage"] for term in term_rows} >= {"en", "la"}
    if label is None:
        assert identifier not in names_by_id
        assert row["displayValue"] is None
        assert row.get("unadoptedCandidates")
    else:
        overlay = names_by_id[identifier]
        assert (overlay["label"], overlay["korean"], overlay["hanja"]) == (label, korean, hanja)
        assert overlay["english"] == loc["englishTextObservation"]
        assert overlay["aliases"] == [loc["latinTextObservation"]]
        assert overlay["parentId"] == concept.get("parentId")
        assert overlay["entityType"] == concept["entityType"] and overlay["lookupOnly"] is False
        assert overlay["humanReviewed"] is False
        assert set(overlay["sourceIds"]) <= all_source_ids

assert sum(1 for identifier in IDS if expected[identifier][0] is not None) == 7
assert sum(1 for identifier in IDS if expected[identifier][2] is not None) == 4
assert next(row for row in ledger["batchOrder"] if row["batchId"] == "T11-B04")["status"] == "not_started"
assert all(row["status"] == "not_started" for row in ledger["canonicalCoverage"] if row["batchId"] == "T11-B04")

print(json.dumps({
    "pass": True,
    "batchId": "T11-B03",
    "canonicalCoverage": len(entries),
    "fieldEvidence": len(evidence),
    "englishAndLatinFields": 20,
    "learnerNameOverlays": len(expected_overlays),
    "sourceHanjaValues": 4,
    "withheldGroupLabels": sorted(set(IDS) - expected_overlays),
    "checkedCoverageTotal": 28,
    "humanReviewed": False,
    "nextBatchStarted": False,
    "overallT11Status": ledger["overallT11Status"],
}, ensure_ascii=False, indent=2))
