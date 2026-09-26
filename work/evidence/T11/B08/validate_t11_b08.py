"""Fixed-scope T11-B08 coverage, overlay, and field-provenance checks."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
IDS = [f"HA-P-{number:06d}" for number in range(4, 14)]
CHECKED = "2026-09-25"
CORE = {"label", "korean", "hanja", "english", "aliases[0]"}
ROWS = {
    "HA-P-000004": (2107, 77, "Pars profunda masseteris", "Deep part of masseter"),
    "HA-P-000005": (2110, 77, "Caput superius musculi pterygoidei lateralis", "Superior head of lateral pterygoid muscle"),
    "HA-P-000006": (2111, 77, "Caput inferius musculi pterygoidei lateralis", "Inferior head of lateral pterygoid muscle"),
    "HA-P-000007": (2114, 77, "Caput profundum musculi pterygoidei medialis", "Deep head of medial pterygoid muscle"),
    "HA-P-000008": (2115, 77, "Caput superficiale musculi pterygoidei medialis", "Superficial head of medial pterygoid muscle"),
    "HA-P-000009": (2227, 81, "Pars descendens musculi trapezii", "Descending part of trapezius muscle"),
    "HA-P-000010": (2228, 81, "Pars transversa musculi trapezii", "Transverse part of trapezius muscle"),
    "HA-P-000011": (2229, 81, "Pars ascendens musculi trapezii", "Ascending part of trapezius muscle"),
    "HA-P-000012": (2302, 83, "Pars clavicularis musculi pectoralis majoris", "Clavicular head of pectoralis major muscle"),
    "HA-P-000013": (2303, 83, "Pars sternocostalis musculi pectoralis majoris", "Sternocostal head of pectoralis major muscle"),
}
EXPECTED_LABELS = {
    "HA-P-000004": "심부 교근",
    "HA-P-000005": "외익돌근 상두",
    "HA-P-000006": "외익돌근 하두",
    "HA-P-000007": "Deep head of medial pterygoid muscle",
    "HA-P-000008": "Superficial head of medial pterygoid muscle",
    "HA-P-000009": "승모근 상부",
    "HA-P-000010": "승모근 중부",
    "HA-P-000011": "승모근 하부",
    "HA-P-000012": "대흉근 쇄골부",
    "HA-P-000013": "대흉근 흉늑부",
}
EXPECTED_KOREAN = {
    "HA-P-000004": None,
    "HA-P-000005": None,
    "HA-P-000006": None,
    "HA-P-000007": None,
    "HA-P-000008": None,
    "HA-P-000009": "등세모근 위부분",
    "HA-P-000010": "등세모근 중간부분",
    "HA-P-000011": "등세모근 아래부분",
    "HA-P-000012": "큰가슴근 빗장부분",
    "HA-P-000013": "큰가슴근 복장갈비부분",
}


def read(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


names = read("atlas-data/terminology/learning-names.json")
ledger = read("atlas-data/terminology/term-review-batches.json")
catalog = read("atlas-data/catalog/canonical-catalog.json")["entities"]["muscleConcepts"]
batch_rows = {row["batchId"]: row for row in ledger["batchOrder"]}
coverage = {row["id"]: row for row in ledger["canonicalCoverage"]}
names_by_id = {row["id"]: row for row in names["entries"]}
catalog_by_id = {row["id"]: row for row in catalog}
entries = [row for row in ledger["entries"] if row["id"] in IDS]
entries_by_id = {row["id"]: row for row in entries}
field_rows = [row for row in ledger["fieldEvidence"] if row["entryId"] in IDS]
fields_by_id = {identifier: {row["field"]: row for row in field_rows if row["entryId"] == identifier} for identifier in IDS}

assert [row["id"] for row in ledger["canonicalCoverage"] if row["batchId"] == "T11-B08"] == IDS
assert batch_rows["T11-B08"]["canonicalIds"] == IDS and batch_rows["T11-B08"]["size"] == 10
assert batch_rows["T11-B08"]["status"] == "complete_with_gaps"
assert batch_rows["T11-B09"]["status"] == "not_started"
assert batch_rows["T11-B07"]["status"] == "complete_with_gaps"
assert len(batch_rows) == 9 and [row["batchId"] for row in ledger["batchOrder"]] == [f"T11-B{i:02d}" for i in range(1, 10)]
assert ledger["overallT11Status"] == "in_progress_partial"
assert sum(row["status"] == "web_checked_with_gaps" for row in ledger["canonicalCoverage"]) == 78
assert len(ledger["fieldEvidence"]) == 441
assert len(names["entries"]) == 74
assert len(entries) == 10 and set(entries_by_id) == set(IDS)
assert len(field_rows) == 56 and len({(row["entryId"], row["field"]) for row in field_rows}) == 56

batch_record = {row["batchId"]: row for row in ledger["batchOrder"]}["T11-B08"]
assert batch_record["size"] == 10
for identifier in IDS:
    row_number, printed_page, latin, english = ROWS[identifier]
    cov = coverage[identifier]
    entry = entries_by_id[identifier]
    overlay = names_by_id[identifier]
    concept = catalog_by_id[identifier]
    field_map = fields_by_id[identifier]
    locator = cov["sourceCrosswalkLocator"]
    cells = locator["observedTableCells"]
    assert cov["status"] == "web_checked_with_gaps"
    assert concept["entityType"] == "muscle_part" and entry["entityType"] == concept["entityType"] == overlay["entityType"]
    assert entry["parentId"] == concept["parentId"] == overlay["parentId"]
    assert entry["canonicalStatus"] == "canonical_existing_id" and entry["webVerificationStatus"] == "web_checked_with_gaps"
    assert entry["humanReviewed"] is False and entry["humanReviewer"] is None
    assert entry["humanAnatomyReviewStatus"] == "not_performed" and overlay["humanReviewed"] is False
    expected_field_count = 7 if identifier == "HA-P-000005" else 6 if identifier in {"HA-P-000006", "HA-P-000009", "HA-P-000010", "HA-P-000011"} else 5
    assert entry["fieldEvidenceCount"] == len(field_map) == expected_field_count
    assert set(field_map).issuperset(CORE)
    assert (locator["tableRow"], locator["printedPage"]) == (row_number, printed_page)
    assert locator["latinTextObservation"] == cells["latinTerm"] == latin
    assert locator["englishTextObservation"] == cells["ukEnglish"] == english
    assert locator["priorT04IndexObservation"]["latinTextObservation"] == latin
    assert locator["priorT04IndexObservation"]["englishTextObservation"] == english
    assert locator["cellRoleStatus"].startswith("Chapter_4_column_roles_confirmed_from_opened_PDF_text_header")
    assert entry["canonicalSourceRow"] == {"sourceId": "FIPAT_TA2", "tableRow": row_number, "printedPage": printed_page}
    assert overlay["label"] == EXPECTED_LABELS[identifier]
    assert overlay["korean"] == EXPECTED_KOREAN[identifier]
    assert overlay["hanja"] is None and field_map["hanja"]["value"] is None and field_map["hanja"]["missingReason"]
    assert overlay["english"] == english
    assert overlay["status"] == "web_attested_with_gaps"
    assert cells["usEnglish"] == english
    assert overlay["aliases"][0] == latin
    assert field_map["aliases[0]"]["value"] == latin

    for field_record in field_map.values():
        assert field_record["humanReviewed"] is False and field_record["humanAnatomyReviewStatus"] == "not_performed"
        assert field_record["evidence"] and field_record["entryId"] == identifier
        if field_record["value"] is None:
            assert field_record["missingReason"]
        else:
            assert field_record["missingReason"] is None
        for evidence in field_record["evidence"]:
            source_id = evidence["sourceId"]
            assert source_id in names["sources"] and source_id in ledger["sources"]
            source = ledger["sources"][source_id]
            assert source == names["sources"][source_id]
            assert source["url"].startswith("https://") and source["edition"] and source["accessDate"] == CHECKED
            assert evidence["sourceEdition"] == source["edition"]
            assert evidence["checkedDate"] == CHECKED and evidence["locator"] and evidence["verificationMode"]
    assert all(evidence["locator"] != field_map["hanja"]["missingReason"] for evidence in field_map["hanja"]["evidence"])

    assert set(overlay["sourceIds"]).issubset(set(ledger["sources"]))

assert [row["id"] for row in names["entries"] if row["id"] in IDS] == IDS
assert sum(row["value"] is None for row in field_rows if row["field"] == "hanja") == 10
assert [row["id"] for row in ledger["canonicalCoverage"] if row["batchId"] == "T11-B09"] == [f"HA-P-{n:06d}" for n in range(14, 22) if n != 15]
assert not any(row["humanReviewed"] for row in field_rows)

print(json.dumps({
    "pass": True,
    "batchId": "T11-B08",
    "assignedExistingIds": IDS,
    "coverageChecked": 10,
    "requiredCoreFieldEvidence": 50,
    "additionalAliasEvidence": 6,
    "batchFieldEvidence": len(field_rows),
    "cumulativeFieldEvidence": len(ledger["fieldEvidence"]),
    "learnerOverlaysTotal": len(names["entries"]),
    "newOverlays": 10,
    "koreanCurrentTermMissing": [identifier for identifier in IDS if EXPECTED_KOREAN[identifier] is None],
    "hanjaMissing": IDS,
    "checkedCanonicalTotal": 78,
    "catalogPartialDenominator": 85,
    "t11BatchCount": 9,
    "humanReviewed": False,
    "nextBatchStarted": False,
    "nextTask": "T11-B09",
}, ensure_ascii=False, indent=2))
