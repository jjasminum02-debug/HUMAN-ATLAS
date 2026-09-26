"""Validate only the fixed T11-B06 assigned IDs and field provenance."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
IDS = [f"HA-M-{number:06d}" for number in range(32, 42)]
CORE_FIELDS = {"label", "korean", "hanja", "english", "aliases[0]"}
EXPECTED = {
    "HA-M-000032": {"label": "극하근", "korean": "가시아래근", "hanja": "棘下筋", "aliases": []},
    "HA-M-000033": {"label": "소원근", "korean": "작은원근", "hanja": "小圓筋", "aliases": []},
    "HA-M-000034": {"label": "견갑하근", "korean": "어깨밑근", "hanja": "肩甲下筋", "aliases": ["subscapular muscle"]},
    "HA-M-000035": {"label": "상완이두근", "korean": "위팔두갈래근", "hanja": "上腕二頭筋", "aliases": []},
    "HA-M-000036": {"label": "오훼완근", "korean": "부리위팔근", "hanja": None, "aliases": ["Casserio's muscle", "Casser's perforated muscle", "coracobrachial muscle"]},
    "HA-M-000037": {"label": "상완근", "korean": "위팔근", "hanja": "上腕筋", "aliases": ["brachial muscle"]},
    "HA-M-000038": {"label": "상완삼두근", "korean": "위팔세갈래근", "hanja": "上腕三頭筋", "aliases": ["triceps muscle of arm"]},
    "HA-M-000039": {"label": "대둔근", "korean": "큰볼기근", "hanja": "大臀筋", "aliases": ["Musculus glutaeus maximus"]},
    "HA-M-000040": {"label": "중둔근", "korean": "중간볼기근", "hanja": "中臀筋", "aliases": ["Musculus glutaeus medius", "mesogluteus"]},
    "HA-M-000041": {"label": "소둔근", "korean": "작은볼기근", "hanja": "小臀筋", "aliases": ["Musculus glutaeus minimus"]},
}
EXPECTED_UNADOPTED = {
    "HA-M-000032": {"極下筋", "Muculus infra spinam"},
    "HA-M-000033": {"小園筋", "小圓形筋"},
    "HA-M-000036": {"烏喙腕筋", "烏口腕筋"},
}
EXPECTED_FIELD_COUNTS = {
    "HA-M-000032": 5, "HA-M-000033": 5, "HA-M-000034": 6, "HA-M-000035": 5,
    "HA-M-000036": 8, "HA-M-000037": 6, "HA-M-000038": 6, "HA-M-000039": 6,
    "HA-M-000040": 7, "HA-M-000041": 6,
}
CHECKED = "2026-09-25"
FIPAT_ID = "fipat-ta2-b06-opened-original-pdf"


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


names = read("atlas-data/terminology/learning-names.json")
ledger = read("atlas-data/terminology/term-review-batches.json")
catalog = read("atlas-data/catalog/canonical-catalog.json")["entities"]
crosswalk = read("atlas-data/catalog/source-crosswalk.json")
canonical = {row["id"]: row for row in catalog["muscleConcepts"]}
coverage = {row["id"]: row for row in ledger["canonicalCoverage"]}
name_by_id = {row["id"]: row for row in names["entries"]}
batch_entries = [row for row in ledger["entries"] if row["id"] in IDS]
flat = [row for row in ledger["fieldEvidence"] if row["entryId"] in IDS]
batch = next(row for row in ledger["batchOrder"] if row["batchId"] == "T11-B06")

assert [row["id"] for row in ledger["canonicalCoverage"] if row["batchId"] == "T11-B06"] == IDS
assert batch["canonicalIds"] == IDS and batch["size"] == 10 and batch["status"] == "complete_with_gaps"
assert len(batch_entries) == 10 and {row["id"] for row in batch_entries} == set(IDS)
assert len(flat) == 60 and len({(row["entryId"], row["field"]) for row in flat}) == 60
assert all(coverage[identifier]["status"] == "web_checked_with_gaps" for identifier in IDS)
assert sum(row["status"] == "web_checked_with_gaps" for row in ledger["canonicalCoverage"]) == 58
assert ledger["overallT11Status"] == "in_progress_partial"
assert next(row for row in ledger["batchOrder"] if row["batchId"] == "T11-B07")["status"] == "not_started"
assert next(row for row in ledger["batchOrder"] if row["batchId"] == "T11-B08")["status"] == "not_started"
assert len(name_by_id) == 56 and all(identifier in name_by_id for identifier in IDS)
assert len(ledger["fieldEvidence"]) == 318
assert len(batch_entries) == 10

entry_by_id = {row["id"]: row for row in batch_entries}
for identifier in IDS:
    entry = entry_by_id[identifier]
    concept = canonical[identifier]
    locator = coverage[identifier]["sourceCrosswalkLocator"]
    expected = EXPECTED[identifier]
    assert entry["entityType"] == concept["entityType"] and entry["parentId"] == concept.get("parentId")
    assert entry["canonicalSourceRow"] == {"sourceId": "FIPAT_TA2", "tableRow": locator["tableRow"], "printedPage": locator["printedPage"]}
    assert entry["webVerificationStatus"] == "web_checked_with_gaps"
    assert entry["humanAnatomyReviewStatus"] == "not_performed" and entry["humanReviewer"] is None and entry["humanReviewed"] is False
    assert locator["cellRoleStatus"] == "column_role_confirmed_from_opened_PDF_text_header; visual_table_layout_not_inspected"
    field_rows = {row["field"]: row for row in entry["fieldEvidence"]}
    assert set(field_rows).issuperset(CORE_FIELDS)
    assert len(field_rows) == EXPECTED_FIELD_COUNTS[identifier] == entry["fieldEvidenceCount"]
    assert field_rows["label"]["value"] == expected["label"]
    assert field_rows["korean"]["value"] == expected["korean"]
    assert field_rows["hanja"]["value"] == expected["hanja"]
    assert field_rows["english"]["value"] == locator["englishTextObservation"]
    assert field_rows["aliases[0]"]["value"] == locator["latinTextObservation"]
    assert name_by_id[identifier]["label"] == expected["label"]
    assert name_by_id[identifier]["korean"] == expected["korean"]
    assert name_by_id[identifier]["hanja"] == expected["hanja"]
    assert name_by_id[identifier]["english"] == locator["englishTextObservation"]
    assert name_by_id[identifier]["aliases"] == [locator["latinTextObservation"], *expected["aliases"]]
    assert name_by_id[identifier]["parentId"] == concept.get("parentId")
    assert name_by_id[identifier]["entityType"] == concept["entityType"]
    assert name_by_id[identifier]["humanReviewed"] is False
    assert {candidate["value"] for candidate in entry.get("unadoptedCandidates", [])} == EXPECTED_UNADOPTED.get(identifier, set())

    if expected["hanja"] is None:
        assert field_rows["hanja"]["missingReason"] and field_rows["hanja"]["state"] == "held_secondary_candidate_primary_source_unverified"
        assert name_by_id[identifier]["hanjaNote"] == field_rows["hanja"]["missingReason"]
        assert "secondary-b06-coracobrachialis-hanja-candidate" not in name_by_id[identifier]["sourceIds"]
    else:
        assert field_rows["hanja"]["missingReason"] is None

    for field in entry["fieldEvidence"]:
        assert field["entryId"] == identifier
        assert field["humanAnatomyReviewStatus"] == "not_performed" and field["humanReviewed"] is False
        assert field["evidence"]
        if field["value"] is None:
            assert field["missingReason"]
        else:
            assert field["missingReason"] is None
        for item in field["evidence"]:
            source_id = item["sourceId"]
            assert source_id in names["sources"] and source_id in ledger["sources"]
            source = names["sources"][source_id]
            assert source == ledger["sources"][source_id]
            assert source["url"].startswith("https://")
            assert source["edition"] and source["accessDate"] == CHECKED
            assert item["sourceEdition"] == source["edition"] and item["checkedDate"] == CHECKED
            assert item["locator"] and item["verificationMode"]
            if field["field"] in {"english", "aliases[0]"}:
                assert source_id == FIPAT_ID
                assert f"table row {locator['tableRow']}" in item["locator"]
                assert "PDF text page" in item["locator"]
            elif field["field"].startswith("aliases["):
                assert source_id != "secondary-b06-coracobrachialis-hanja-candidate"
            else:
                assert source_id.startswith("kmle-b06-") or source_id.startswith("secondary-")

    terms = [row for row in crosswalk["termRecords"] if row["conceptId"] == identifier and row["sourceTextObserved"]]
    assert {row["sourceLanguage"] for row in terms} >= {"en", "la"}

assert next(row for row in ledger["batchOrder"] if row["batchId"] == "T11-B05")["status"] == "complete_with_gaps"
print(json.dumps({
    "pass": True,
    "batchId": "T11-B06",
    "assignedExistingIds": IDS,
    "coverageChecked": 10,
    "requiredCoreFieldEvidence": 50,
    "additionalAliasEvidence": 10,
    "batchFieldEvidence": 60,
    "cumulativeFieldEvidence": 318,
    "learnerOverlaysTotal": 56,
    "newOverlays": 10,
    "hanjaAttested": 9,
    "hanjaMissing": ["HA-M-000036"],
    "checkedCanonicalTotal": 58,
    "catalogDenominator": 85,
    "humanReviewed": False,
    "nextBatchStarted": False,
    "nextTask": "T11-B07",
}, ensure_ascii=False, indent=2))
