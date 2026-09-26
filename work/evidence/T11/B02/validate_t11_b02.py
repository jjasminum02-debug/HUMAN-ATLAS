"""Validate T11-B02 coverage, same-ID aliases, source provenance, and review separation."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXPECTED = [f"HA-G-{i:06d}" for i in range(1, 11)]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


names = read_json(ROOT / "atlas-data/terminology/learning-names.json")
ledger = read_json(ROOT / "atlas-data/terminology/term-review-batches.json")
crosswalk = read_json(ROOT / "atlas-data/catalog/source-crosswalk.json")
catalog = read_json(ROOT / "atlas-data/catalog/canonical-catalog.json")["entities"]
canonical = {row["id"]: row for row in catalog["muscleConcepts"]}
name_by_id = {row["id"]: row for row in names["entries"]}
coverage = {row["id"]: row for row in ledger["canonicalCoverage"]}
batch_rows = [row for row in ledger["entries"] if row["id"] in EXPECTED]
evidence_rows = [row for row in ledger["fieldEvidence"] if row["entryId"] in EXPECTED]
source_ids = set(names["sources"])
manifest_source_ids = set(ledger["sources"])

assert [row["id"] for row in ledger["canonicalCoverage"] if row["batchId"] == "T11-B02"] == EXPECTED
assert len(batch_rows) == 10 and {row["id"] for row in batch_rows} == set(EXPECTED)
assert len(evidence_rows) == 50
assert all(coverage[identifier]["status"] == "web_checked_with_gaps" for identifier in EXPECTED)
assert next(row for row in ledger["batchOrder"] if row["batchId"] == "T11-B02")["status"] == "complete_with_gaps"
assert ledger["overallT11Status"] == "in_progress_partial"

for row in batch_rows:
    identifier = row["id"]
    assert row["entityType"] == "muscle_group"
    assert row["humanReviewed"] is False and row["humanAnatomyReviewStatus"] == "not_performed"
    assert row["fieldEvidenceCount"] == 5 and len(row["fieldEvidence"]) == 5
    assert {item["field"] for item in row["fieldEvidence"]} == {"label", "korean", "hanja", "english", "aliases[0]"}
    for item in row["fieldEvidence"]:
        assert item["entryId"] == identifier
        assert item["humanReviewed"] is False and item["humanAnatomyReviewStatus"] == "not_performed"
        if item["value"] is None:
            assert item["missingReason"], (identifier, item["field"])
        for ev in item["evidence"]:
            assert ev["sourceId"] in source_ids, (identifier, item["field"], ev["sourceId"])
            assert ev["sourceId"] in manifest_source_ids
            name_source = names["sources"][ev["sourceId"]]
            manifest_source = ledger["sources"][ev["sourceId"]]
            assert name_source.get("url") and name_source["url"] == manifest_source.get("url")
            assert ev["sourceEdition"] == name_source.get("edition") == manifest_source.get("edition")
            assert ev["checkedDate"] == name_source.get("accessDate") == manifest_source.get("accessDate") == "2026-09-25"
            assert ev["locator"] and ev["sourceEdition"] and ev["checkedDate"] == "2026-09-25"
            assert ev["verificationMode"]

overlay_expected = {"HA-G-000001", "HA-G-000002", "HA-G-000003", "HA-G-000004", "HA-G-000006", "HA-G-000007", "HA-G-000010"}
assert {identifier for identifier in EXPECTED if identifier in name_by_id} == overlay_expected
assert len(name_by_id) == len(names["entries"])
for identifier in overlay_expected:
    item = name_by_id[identifier]
    assert canonical[identifier]["entityType"] == item["entityType"] == "muscle_group"
    assert item["label"] and item["english"] and item["sourceIds"]
    assert item["humanReviewed"] is False and item["lookupOnly"] is False
    assert item["parentId"] == canonical[identifier].get("parentId")
    assert all(source_id in source_ids for source_id in item["sourceIds"])
    assert len(item["aliases"]) == 1
    assert item["aliases"][0] == coverage[identifier]["sourceCrosswalkLocator"]["latinTextObservation"]

for identifier in ("HA-G-000005", "HA-G-000008", "HA-G-000009"):
    assert identifier not in name_by_id, f"unsupported Korean group label must not enter the learner overlay: {identifier}"

for row in (row for row in crosswalk["termRecords"] if row["conceptId"] in EXPECTED and row["sourceLanguage"] in ("en", "la")):
    assert row["sourceTextObserved"]
assert sum(1 for row in batch_rows if next(e for e in row["fieldEvidence"] if e["field"] == "hanja")["value"]) == 4
assert all(
    names["sources"][sid]["accessDate"] == "2026-09-25"
    for sid in ("fipat-ta2-b02-index", "kmle-b02-head-groups", "kmle-b02-extraocular", "kmle-b02-mastication", "kmle-b02-muscle-terms", "kmle-b02-back-groups", "kmle-b02-thorax", "kmle-b02-upper-limb", "kmle-b02-scapulohumeral", "kmle-b02-rotator-cuff", "kmle-b02-lower-limb")
)

print(json.dumps({
    "pass": True,
    "batchId": "T11-B02",
    "canonicalCoverage": len(batch_rows),
    "fieldEvidence": len(evidence_rows),
    "englishAndLatinRows": 20,
    "koreanDisplayOverlays": len(overlay_expected),
    "sourceHanjaValues": 4,
    "withheldGroupLabels": 3,
    "humanReviewed": False,
    "overallT11Status": ledger["overallT11Status"],
}, ensure_ascii=False, indent=2))
