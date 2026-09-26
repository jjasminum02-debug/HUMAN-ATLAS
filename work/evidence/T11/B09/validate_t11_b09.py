"""Fixed-scope coverage and provenance checks for T11-B09."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from build_t11_b09 import FIELDS, IDS, ROWS, SOURCES, CHECKED

ROOT = Path(__file__).resolve().parents[4]
NAMES_PATH = ROOT / "atlas-data/terminology/learning-names.json"
BATCH_PATH = ROOT / "atlas-data/terminology/term-review-batches.json"
CROSSWALK_PATH = ROOT / "atlas-data/catalog/source-crosswalk.json"
PRESERVATION_BEFORE = ROOT / "work/evidence/T11/B09/preservation-before.json"
EXPECTED_LABELS = {
    "HA-P-000014": "쇄골부",
    "HA-P-000016": "Scapular spinal part of deltoid muscle",
    "HA-P-000017": "상완이두근장두",
    "HA-P-000018": "상완두갈래근짧은갈래",
    "HA-P-000019": "상완삼두근장두",
    "HA-P-000020": "상완 삼두근 외측두",
    "HA-P-000021": "안쪽갈래",
}
EXPECTED_KOREAN = {
    "HA-P-000014": "빗장부분",
    "HA-P-000016": None,
    "HA-P-000017": "긴갈래",
    "HA-P-000018": "위팔 두 갈래근 짧은 갈래",
    "HA-P-000019": "긴갈래",
    "HA-P-000020": "위팔 세 갈래 근 가쪽 갈래",
    "HA-P-000021": "안쪽갈래",
}
EXPECTED_FIELD_COUNTS = {
    "HA-P-000014": 5,
    "HA-P-000016": 7,
    "HA-P-000017": 6,
    "HA-P-000018": 7,
    "HA-P-000019": 6,
    "HA-P-000020": 8,
    "HA-P-000021": 9,
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


names = read_json(NAMES_PATH)
ledger = read_json(BATCH_PATH)
catalog = {
    row["id"]: row
    for row in read_json(ROOT / "atlas-data/catalog/canonical-catalog.json")["entities"]["muscleConcepts"]
}
crosswalk = read_json(CROSSWALK_PATH)
before = read_json(PRESERVATION_BEFORE)

coverage_rows = [row for row in ledger["canonicalCoverage"] if row["batchId"] == "T11-B09"]
require([row["id"] for row in coverage_rows] == IDS, "B09 assignment IDs/order changed")
require(len(ledger["canonicalCoverage"]) == 85, "Partial catalog denominator changed")
require(sum(row["status"] == "web_checked_with_gaps" for row in ledger["canonicalCoverage"]) == 85,
        "Expected all 85 current partial-catalog records to be checked with gaps after B09")
require(ledger["overallT11Status"] == "in_progress_partial", "T11 must remain partial")
batch_order = {row["batchId"]: row for row in ledger["batchOrder"]}
require(len(batch_order) == 9, "T11 must retain the nine fixed B01-B09 batches")
require(batch_order["T11-B09"]["canonicalIds"] == IDS, "B09 batch IDs changed")
require(batch_order["T11-B09"]["size"] == 7, "B09 batch size changed")
require(batch_order["T11-B09"]["status"] == "complete_with_gaps", "B09 status must be complete_with_gaps")
require(batch_order["T11-B08"]["status"] == "complete_with_gaps", "B08 must remain complete_with_gaps")
require("T12" not in batch_order, "T12 must not be represented as a T11 batch")

entries = [row for row in ledger["entries"] if row["id"] in IDS]
entries_by_id = {row["id"]: row for row in entries}
overlays = [row for row in names["entries"] if row["id"] in IDS]
overlays_by_id = {row["id"]: row for row in overlays}
field_rows = [row for row in ledger["fieldEvidence"] if row["entryId"] in IDS]
field_maps = {
    identifier: {row["field"]: row for row in field_rows if row["entryId"] == identifier}
    for identifier in IDS
}
require(len(entries) == 7 and set(entries_by_id) == set(IDS), "B09 must add exactly seven evidence entries")
require(len(overlays) == 7 and set(overlays_by_id) == set(IDS), "B09 must add exactly seven existing-ID overlays")
require(len(field_rows) == 48, "Expected 48 B09 core and separately evidenced alias fields")
require(len(ledger["fieldEvidence"]) == 489, "Cumulative field evidence total mismatch")
require(len(names["entries"]) == 81, "Cumulative learner overlay count mismatch")

crosswalk_hash_before = before["projectFilesSha256"].get("atlas-data/catalog/source-crosswalk.json")
crosswalk_hash_now = hashlib.sha256(CROSSWALK_PATH.read_bytes()).hexdigest()
require(crosswalk_hash_before == crosswalk_hash_now, "T04 source-crosswalk.json must remain byte-identical")
crosswalk_items = {row["stableConceptId"]: row for row in crosswalk["catalogItems"]}

for identifier in IDS:
    concept = catalog[identifier]
    cov = next(row for row in coverage_rows if row["id"] == identifier)
    entry = entries_by_id[identifier]
    overlay = overlays_by_id[identifier]
    rowspec = ROWS[identifier]
    cells = rowspec["cells"]
    locator = cov["sourceCrosswalkLocator"]
    fmap = field_maps[identifier]

    require(concept["entityType"] == "muscle_part", identifier + " must remain muscle_part")
    require(entry["entityType"] == concept["entityType"] == overlay["entityType"], identifier + " entityType mismatch")
    require(entry["parentId"] == concept.get("parentId") == overlay["parentId"], identifier + " parent changed")
    require(entry["canonicalStatus"] == "canonical_existing_id", identifier + " ID must remain canonical existing ID")
    require(entry["webVerificationStatus"] == cov["status"] == "web_checked_with_gaps", identifier + " coverage mismatch")
    require(entry["humanReviewed"] is False and entry["humanReviewer"] is None, identifier + " human review must remain false")
    require(entry["humanAnatomyReviewStatus"] == "not_performed", identifier + " anatomy review state mismatch")
    require(overlay["humanReviewed"] is False and overlay["status"] == "web_attested_with_gaps", identifier + " overlay review state mismatch")
    require(overlay["label"] == EXPECTED_LABELS[identifier], identifier + " display label mismatch")
    require(overlay["korean"] == EXPECTED_KOREAN[identifier], identifier + " Korean value mismatch")
    require(overlay["hanja"] is None, identifier + " Hanja must remain missing")
    require("hanjaNote" in overlay and overlay["hanjaNote"], identifier + " Hanja gap must be explained")
    require(entry["fieldEvidenceCount"] == EXPECTED_FIELD_COUNTS[identifier] == len(fmap),
            identifier + " field evidence count mismatch")
    require(set(fmap).issuperset({"label", "korean", "hanja", "english", "aliases[0]"}),
            identifier + " required core field evidence missing")
    require(fmap["label"]["value"] == overlay["label"], identifier + " label evidence mismatch")
    require(fmap["korean"]["value"] == overlay["korean"], identifier + " Korean evidence mismatch")
    require(fmap["hanja"]["value"] is None and fmap["hanja"]["missingReason"], identifier + " Hanja gap missing")
    require(fmap["english"]["value"] == cells["ukEnglish"], identifier + " English value mismatch")
    require(fmap["aliases[0]"]["value"] == cells["latinTerm"], identifier + " primary Latin alias mismatch")
    require(locator["tableRow"] == rowspec["row"] and locator["printedPage"] == 89,
            identifier + " TA2 locator mismatch")
    require(locator["latinTextObservation"] == cells["latinTerm"], identifier + " TA2 Latin row mismatch")
    require(locator["englishTextObservation"] == cells["ukEnglish"], identifier + " TA2 English row mismatch")
    require(locator["observedTableCells"] == cells, identifier + " TA2 table cells mismatch")
    require(locator["cellRoleStatus"].startswith("Chapter_4_column_roles_confirmed_from_opened_PDF_text_header"),
            identifier + " column role/header evidence missing")
    require(locator["priorT04IndexObservation"]["latinTextObservation"] == cells["latinTerm"],
            identifier + " prior T04 Latin observation not preserved")
    require(locator["priorT04IndexObservation"]["englishTextObservation"] == cells["ukEnglish"],
            identifier + " prior T04 English observation not preserved")
    require(locator["priorT04IndexObservation"]["sourceCrosswalkSha256BeforeBuild"] == crosswalk_hash_before,
            identifier + " T04 crosswalk hash evidence mismatch")
    old_crosswalk = crosswalk_items[identifier]
    require(old_crosswalk["tableRow"] == rowspec["row"] and old_crosswalk["printedPage"] == 89,
            identifier + " T04 original row/printed page mismatch")
    require(old_crosswalk["latinTextObservation"] == cells["latinTerm"], identifier + " T04 crosswalk Latin mismatch")
    require(old_crosswalk["englishTextObservation"] == cells["ukEnglish"], identifier + " T04 crosswalk English mismatch")

    alias_fields = sorted(
        ((int(field[8:-1]), row) for field, row in fmap.items() if field.startswith("aliases[")),
        key=lambda pair: pair[0],
    )
    require([index for index, _ in alias_fields] == list(range(len(alias_fields))), identifier + " alias indexes must be contiguous")
    require([value["value"] for _, value in alias_fields] == overlay["aliases"], identifier + " overlay aliases differ from evidence")
    require(overlay["sourceIds"] == sorted(set(overlay["sourceIds"])), identifier + " overlay sourceIds must be stable/deduped")
    require(set(overlay["sourceIds"]).issubset(set(ledger["sources"])), identifier + " overlay source id missing")
    require(entry["unadoptedCandidates"] == FIELDS[identifier]["unadoptedCandidates"],
            identifier + " unresolved candidates changed")

    for field_record in fmap.values():
        require(field_record["entryId"] == identifier, identifier + " field entry ID mismatch")
        require(field_record["evidence"], identifier + " field has no provenance evidence")
        require(field_record["humanReviewed"] is False, identifier + " field cannot be human-reviewed")
        require(field_record["humanAnatomyReviewStatus"] == "not_performed", identifier + " field anatomy review state mismatch")
        if field_record["value"] is None:
            require(field_record["missingReason"], identifier + " null field needs a missing reason")
        else:
            require(field_record["missingReason"] is None, identifier + " adopted field cannot also be missing")
        for evidence in field_record["evidence"]:
            source_id = evidence["sourceId"]
            require(source_id in names["sources"] and source_id in ledger["sources"], identifier + " field source missing")
            require(names["sources"][source_id] == ledger["sources"][source_id], source_id + " source registries differ")
            source = ledger["sources"][source_id]
            require(source["url"].startswith("https://"), source_id + " URL missing")
            require(source["edition"] and source["accessDate"] == CHECKED, source_id + " edition/date missing")
            require(evidence["sourceEdition"] == source["edition"], source_id + " field edition mismatch")
            require(evidence["checkedDate"] == CHECKED, source_id + " field check date mismatch")
            require(evidence["locator"] and evidence["verificationMode"], source_id + " field locator/access mode missing")

require(not any(row["humanReviewed"] for row in field_rows), "No B09 field may claim human review")
require([row["id"] for row in names["entries"] if row["id"] in IDS] == IDS, "B09 overlay order/assignment mismatch")
require([row["id"] for row in ledger["entries"] if row["id"] in IDS] == IDS, "B09 entry order/assignment mismatch")
require("T12 remains not started" in ledger["notes"][-1], "T12 must remain not started")

print(json.dumps({
    "pass": True,
    "batchId": "T11-B09",
    "assignedExistingIds": IDS,
    "coverageChecked": 7,
    "requiredCoreFieldEvidence": 35,
    "separatelyEvidencedAliases": len(field_rows) - 35,
    "batchFieldEvidence": len(field_rows),
    "cumulativeFieldEvidence": len(ledger["fieldEvidence"]),
    "partialCatalogCheckedWithGaps": str(sum(row["status"] == "web_checked_with_gaps" for row in ledger["canonicalCoverage"])) + "/85",
    "learnerOverlaysTotal": len(names["entries"]),
    "currentKoreanMissing": [identifier for identifier in IDS if EXPECTED_KOREAN[identifier] is None],
    "hanjaMissing": IDS,
    "sourceCrosswalkUnchanged": True,
    "humanReviewed": False,
    "nextTaskStarted": False,
    "nextTask": "T12",
}, ensure_ascii=False, indent=2))
