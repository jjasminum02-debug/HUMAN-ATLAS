"""Validate only fixed T11-B07 coverage, names, and field-level provenance."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
IDS = [*(f"HA-M-{n:06d}" for n in range(42, 49)), *(f"HA-P-{n:06d}" for n in range(1, 4))]
CORE = {"label", "korean", "hanja", "english", "aliases[0]"}
CHECKED = "2026-09-25"
EXPECTED = {
    "HA-M-000042": {"label": "이상근", "korean": "궁둥구멍근", "hanja": "梨狀筋", "english": "Piriformis muscle", "aliases": ["Musculus piriformis", "piriform muscle", "musculus pyriformis"], "count": 7},
    "HA-M-000043": {"label": "내폐쇄근", "korean": "속폐쇄근", "hanja": None, "english": "Obturator internus", "aliases": ["Obturator internus", "Musculus obturatorius internus", "Obturator internus muscle"], "count": 7},
    "HA-M-000044": {"label": "상쌍자근", "korean": "위쌍동이근", "hanja": "上雙子筋", "english": "Superior gemellus muscle", "aliases": ["Musculus gemellus superior", "Gemellus superior muscle", "Musculus gemellus spinalis"], "count": 7},
    "HA-M-000045": {"label": "하쌍자근", "korean": "아래쌍동이근", "hanja": "下雙子筋", "english": "Inferior gemellus muscle", "aliases": ["Musculus gemellus inferior", "Gemellus inferior muscle", "Musculus gemellus tuberalis"], "count": 7},
    "HA-M-000046": {"label": "대퇴방형근", "korean": "넙다리네모근", "hanja": None, "english": "Quadratus femoris muscle", "aliases": ["Musculus quadratus femoris", "quadrate muscle of thigh"], "count": 6},
    "HA-M-000047": {"label": "단무지굴근", "korean": "짧은엄지굽힘근", "hanja": None, "english": "Flexor hallucis brevis", "aliases": ["Flexor brevis hallucis", "Musculus flexor hallucis brevis", "Flexor hallucis brevis muscle", "short flexor muscle of great toe"], "count": 8},
    "HA-M-000048": {"label": "무지내전근", "korean": "엄지모음근", "hanja": "拇趾內轉筋", "english": "Adductor hallucis", "aliases": ["Adductor hallucis", "Musculus adductor hallucis", "Adductor hallucis muscle", "adductor muscle of great toe"], "count": 8},
    "HA-P-000001": {"label": "비복근 · 외측두", "korean": None, "hanja": None, "english": "Lateral head of gastrocnemius", "aliases": ["Caput laterale musculi gastrocnemii", "Caput fibulare musculi gastrocnemii"], "count": 6},
    "HA-P-000002": {"label": "비복근 · 내측두", "korean": None, "hanja": None, "english": "Medial head of gastrocnemius", "aliases": ["Caput mediale musculi gastrocnemii", "Caput tibiale musculi gastrocnemii"], "count": 6},
    "HA-P-000003": {"label": "교근의 천부", "korean": None, "hanja": None, "english": "Superficial part of masseter", "aliases": ["Pars superficialis masseteris"], "count": 5},
}
EXPECTED_TA2_LOCATORS = {
    "HA-M-000042": (2604, 94, "P73"), "HA-M-000043": (2605, 94, "P73"),
    "HA-M-000044": (2606, 94, "P73"), "HA-M-000045": (2607, 94, "P73"),
    "HA-M-000046": (2608, 94, "P73"), "HA-M-000047": (2673, 96, "P75"),
    "HA-M-000048": (2676, 96, "P75"), "HA-P-000001": (2658, 96, "P75"),
    "HA-P-000002": (2659, 96, "P75"), "HA-P-000003": (2106, 77, "P56"),
}


def read(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


names = read("atlas-data/terminology/learning-names.json")
ledger = read("atlas-data/terminology/term-review-batches.json")
catalog = read("atlas-data/catalog/canonical-catalog.json")["entities"]
names_by_id = {row["id"]: row for row in names["entries"]}
catalog_by_id = {row["id"]: row for row in catalog["muscleConcepts"]}
coverage = {row["id"]: row for row in ledger["canonicalCoverage"]}
batch_rows = {row["batchId"]: row for row in ledger["batchOrder"]}
entries = [row for row in ledger["entries"] if row["id"] in IDS]
field_rows = [row for row in ledger["fieldEvidence"] if row["entryId"] in IDS]
entries_by_id = {row["id"]: row for row in entries}

assert [row["id"] for row in ledger["canonicalCoverage"] if row["batchId"] == "T11-B07"] == IDS
assert batch_rows["T11-B07"]["canonicalIds"] == IDS and batch_rows["T11-B07"]["size"] == 10
assert batch_rows["T11-B07"]["status"] == "complete_with_gaps"
assert batch_rows["T11-B08"]["status"] == "not_started" and batch_rows["T11-B09"]["status"] == "not_started"
assert [row["batchId"] for row in ledger["batchOrder"]] == [f"T11-B{i:02d}" for i in range(1, 10)]
assert len(batch_rows) == 9
assert ledger["overallT11Status"] == "in_progress_partial"
assert sum(row["status"] == "web_checked_with_gaps" for row in ledger["canonicalCoverage"]) == 68
assert len(entries) == 10 and set(entries_by_id) == set(IDS)
assert len(field_rows) == 67 and len({(row["entryId"], row["field"]) for row in field_rows}) == 67
assert len(ledger["fieldEvidence"]) == 385
assert len(names["entries"]) == 64
assert ledger["catalogScope"]["currentPartialCatalogItems"] == 85

batch_evidence = {identifier: {row["field"]: row for row in field_rows if row["entryId"] == identifier} for identifier in IDS}
for identifier in IDS:
    expected = EXPECTED[identifier]
    name = names_by_id[identifier]
    entry = entries_by_id[identifier]
    concept = catalog_by_id[identifier]
    cov = coverage[identifier]
    locator = cov["sourceCrosswalkLocator"]
    row_fields = batch_evidence[identifier]

    assert set(row_fields).issuperset(CORE), identifier
    assert len(row_fields) == expected["count"] == entry["fieldEvidenceCount"], identifier
    assert cov["status"] == "web_checked_with_gaps", identifier
    assert entry["entityType"] == concept["entityType"] and entry["parentId"] == concept.get("parentId")
    assert name["entityType"] == concept["entityType"] and name["parentId"] == concept.get("parentId")
    assert entry["canonicalSourceRow"] == {"sourceId": "FIPAT_TA2", "tableRow": locator["tableRow"], "printedPage": locator["printedPage"]}
    assert entry["canonicalStatus"] == "canonical_existing_id" and entry["webVerificationStatus"] == "web_checked_with_gaps"
    assert entry["humanAnatomyReviewStatus"] == name.get("humanAnatomyReviewStatus", "not_performed") == "not_performed"
    assert entry["humanReviewer"] is None and entry["humanReviewed"] is False and name["humanReviewed"] is False
    assert (name["label"], name["korean"], name["hanja"], name["english"], name["aliases"]) == (
        expected["label"], expected["korean"], expected["hanja"], expected["english"], expected["aliases"]
    ), identifier
    assert row_fields["label"]["value"] == expected["label"]
    assert row_fields["korean"]["value"] == expected["korean"]
    assert row_fields["hanja"]["value"] == expected["hanja"]
    assert row_fields["english"]["value"] == expected["english"]
    assert row_fields["aliases[0]"]["value"] == expected["aliases"][0]

    observed = locator["observedTableCells"]
    expected_row, expected_page, expected_pdf_page = EXPECTED_TA2_LOCATORS[identifier]
    assert (locator["tableRow"], locator["printedPage"]) == (expected_row, expected_page)
    assert expected_pdf_page in ledger["sources"]["fipat-ta2-b07-opened-original-pdf"]["locator"]
    assert locator["latinTextObservation"] == observed["latinTerm"]
    assert locator["englishTextObservation"] == observed["ukEnglish"]
    assert locator["cellRoleStatus"].startswith("Chapter_4_column_roles_confirmed_from_opened_PDF_text_header")
    assert locator["edition"] == ledger["sources"]["fipat-ta2-b07-opened-original-pdf"]["edition"]
    assert "priorT04IndexObservation" in locator
    assert row_fields["english"]["evidence"][0]["sourceId"] == "fipat-ta2-b07-opened-original-pdf"
    assert row_fields["aliases[0]"]["evidence"][0]["sourceId"] == "fipat-ta2-b07-opened-original-pdf"
    alias_rows = [row_fields[f"aliases[{i}]"]["value"] for i in range(len(expected["aliases"]))]
    assert alias_rows == expected["aliases"]

    if expected["hanja"] is None:
        assert row_fields["hanja"]["missingReason"] and name["hanjaNote"] == row_fields["hanja"]["missingReason"]
    else:
        assert row_fields["hanja"]["missingReason"] is None
    if expected["korean"] is None:
        assert row_fields["korean"]["missingReason"] and name.get("koreanNote") == row_fields["korean"]["missingReason"]
    else:
        assert row_fields["korean"]["missingReason"] is None

    for field_record in entry["fieldEvidence"]:
        assert field_record["entryId"] == identifier
        assert field_record["humanReviewed"] is False and field_record["humanAnatomyReviewStatus"] == "not_performed"
        assert len(field_record["evidence"]) >= 1
        if field_record["value"] is None:
            assert field_record["missingReason"]
        else:
            assert field_record["missingReason"] is None
        for evidence in field_record["evidence"]:
            source_id = evidence["sourceId"]
            assert source_id in names["sources"] and source_id in ledger["sources"], (identifier, field_record["field"], source_id)
            source = names["sources"][source_id]
            assert source == ledger["sources"][source_id]
            assert source["url"].startswith("https://") and source["edition"] and source["accessDate"] == CHECKED
            assert evidence["sourceEdition"] == source["edition"] and evidence["checkedDate"] == CHECKED
            assert evidence["locator"] and evidence["verificationMode"]

    if identifier in {"HA-P-000001", "HA-P-000002"}:
        previous = entry.get("preservedPreviousOverlay")
        assert previous and previous["label"] == expected["label"]
        assert previous["korean"] in {"장딴지근 · 가쪽갈래", "장딴지근 · 안쪽갈래"}
        assert "kmle-gastro" in name["sourceIds"]
        assert any(candidate["field"] == "korean" and candidate["value"] == previous["korean"] for candidate in entry["unadoptedCandidates"])

assert len([x for x in entries if x["unadoptedCandidates"]]) == 5
assert not any(x["humanReviewed"] for x in field_rows)
assert batch_rows["T11-B06"]["status"] == "complete_with_gaps"
print(json.dumps({
    "pass": True,
    "batchId": "T11-B07",
    "assignedExistingIds": IDS,
    "coverageChecked": 10,
    "requiredCoreFieldEvidence": 50,
    "additionalAliasEvidence": 17,
    "batchFieldEvidence": 67,
    "cumulativeFieldEvidence": len(ledger["fieldEvidence"]),
    "learnerOverlaysTotal": len(names["entries"]),
    "newOverlays": 8,
    "enrichedPreexistingOverlays": 2,
    "hanjaAttested": 4,
    "hanjaMissing": [identifier for identifier in IDS if EXPECTED[identifier]["hanja"] is None],
    "koreanMissing": [identifier for identifier in IDS if EXPECTED[identifier]["korean"] is None],
    "checkedCanonicalTotal": 68,
    "catalogPartialDenominator": 85,
    "t11BatchCount": 9,
    "humanReviewed": False,
    "nextBatchStarted": False,
    "nextTask": "T11-B08",
}, ensure_ascii=False, indent=2))
