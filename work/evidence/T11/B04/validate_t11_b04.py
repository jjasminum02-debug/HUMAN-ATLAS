"""Validate T11-B04's fixed ID scope, values, coverage and field provenance."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
IDS = [f"HA-M-{n:06d}" for n in [11,12,13,14,15,16,17,18,20,21]]
FIELDS = {"label","korean","hanja","english","aliases[0]"}
CHECKED = "2026-09-25"
EXPECTED = {
 "HA-M-000011": ("상사근","위빗근","上斜筋"),
 "HA-M-000012": ("교근","깨물근","咬筋"),
 "HA-M-000013": ("측두근","관자근","側頭筋"),
 "HA-M-000014": ("외측익돌근","가쪽날개근","外側翼突筋"),
 "HA-M-000015": ("내측익돌근","안쪽날개근","內側翼突筋"),
 "HA-M-000016": ("이설근","턱끝혀근",None),
 "HA-M-000017": ("설골설근","목뿔혀근","舌骨舌筋"),
 "HA-M-000018": ("경돌설근","붓혀근","莖突舌筋"),
 "HA-M-000020": ("광배근","넓은등근","廣背筋"),
 "HA-M-000021": ("대능형근","큰마름근","大菱形筋"),
}

def read(path: str):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

names = read("atlas-data/terminology/learning-names.json")
ledger = read("atlas-data/terminology/term-review-batches.json")
catalog = read("atlas-data/catalog/canonical-catalog.json")["entities"]
crosswalk = read("atlas-data/catalog/source-crosswalk.json")
canonical = {row["id"]:row for row in catalog["muscleConcepts"]}
coverage = {row["id"]:row for row in ledger["canonicalCoverage"]}
name_by_id = {row["id"]:row for row in names["entries"]}
entries = [row for row in ledger["entries"] if row["id"] in IDS]
flat = [row for row in ledger["fieldEvidence"] if row["entryId"] in IDS]
batch = next(row for row in ledger["batchOrder"] if row["batchId"]=="T11-B04")

assert [row["id"] for row in ledger["canonicalCoverage"] if row["batchId"]=="T11-B04"] == IDS
assert batch["canonicalIds"]==IDS and batch["size"]==10 and batch["status"]=="complete_with_gaps"
assert len(entries)==10 and {row["id"] for row in entries}==set(IDS)
assert len(flat)==50 and len({(row["entryId"],row["field"]) for row in flat})==50
assert all(coverage[i]["status"]=="web_checked_with_gaps" for i in IDS)
assert sum(row["status"]=="web_checked_with_gaps" for row in ledger["canonicalCoverage"])==38
assert ledger["overallT11Status"]=="in_progress_partial"
assert next(row for row in ledger["batchOrder"] if row["batchId"]=="T11-B05")["status"]=="not_started"
assert next(row for row in ledger["batchOrder"] if row["batchId"]=="T11-B06")["status"]=="not_started"
assert ledger["revision"]=="T11-B04-web-checked-2026-09-25"
assert {i for i in IDS if i in name_by_id}==set(IDS)

entry_by_id={row["id"]:row for row in entries}
for identifier in IDS:
    row=entry_by_id[identifier]
    concept=canonical[identifier]
    loc=coverage[identifier]["sourceCrosswalkLocator"]
    expected_label,expected_korean,expected_hanja=EXPECTED[identifier]
    assert row["entityType"]==concept["entityType"] and row["parentId"]==concept.get("parentId")
    assert row["canonicalSourceRow"]=={"sourceId":"FIPAT_TA2","tableRow":loc["tableRow"],"printedPage":loc["printedPage"]}
    assert row["webVerificationStatus"]=="web_checked_with_gaps"
    assert row["humanAnatomyReviewStatus"]=="not_performed" and row["humanReviewer"] is None and row["humanReviewed"] is False
    assert row["fieldEvidenceCount"]==5
    fields={f["field"]:f for f in row["fieldEvidence"]}
    assert set(fields)==FIELDS
    assert [fields[key]["value"] for key in ["label","korean","hanja"]]==[expected_label,expected_korean,expected_hanja]
    assert fields["english"]["value"]==loc["englishTextObservation"]
    assert fields["aliases[0]"]["value"]==loc["latinTextObservation"]
    assert fields["english"]["sourceValue"]==loc["englishTextObservation"]
    assert fields["aliases[0]"]["sourceValue"]==loc["latinTextObservation"]
    overlay=name_by_id[identifier]
    assert (overlay["label"],overlay["korean"],overlay["hanja"])==(expected_label,expected_korean,expected_hanja)
    assert overlay["english"]==loc["englishTextObservation"] and overlay["aliases"]==[loc["latinTextObservation"]]
    assert overlay["parentId"]==concept.get("parentId") and overlay["entityType"]==concept["entityType"] and overlay["lookupOnly"] is False
    assert overlay["humanReviewed"] is False
    for field in fields.values():
        assert field["entryId"]==identifier
        assert field["humanAnatomyReviewStatus"]=="not_performed" and field["humanReviewed"] is False
        assert field["evidence"]
        if field["value"] is None: assert field["missingReason"]
        else: assert field["missingReason"] is None
        for ev in field["evidence"]:
            sid=ev["sourceId"]
            assert sid in names["sources"] and sid in ledger["sources"]
            source=names["sources"][sid]
            assert source==ledger["sources"][sid]
            assert source["url"].startswith("https://") and source["edition"] and source["accessDate"]==CHECKED
            assert ev["sourceEdition"]==source["edition"] and ev["checkedDate"]==CHECKED
            assert ev["locator"] and ev["verificationMode"]
            if field["field"] in {"english","aliases[0]"}:
                assert f"table row {loc['tableRow']}" in ev["locator"]
                assert sid=="fipat-ta2-b04-index"
            else:
                assert sid.startswith("kmle-b04-")

    terms=[term for term in crosswalk["termRecords"] if term["conceptId"]==identifier and term["sourceTextObserved"]]
    assert {term["sourceLanguage"] for term in terms}>={"en","la"}
    if identifier=="HA-M-000016":
        assert row["fieldEvidence"][2]["value"] is None
        assert "舌筋" in row["unadoptedCandidates"][0]["value"]
        search_fields=[overlay["label"],overlay["korean"],overlay["english"],overlay["hanja"],*overlay["aliases"]]
        assert all("舌筋" not in (value or "") for value in search_fields)

assert sum(EXPECTED[i][2] is not None for i in IDS)==9
assert sum(1 for row in flat if row["field"]=="english")==10
assert sum(1 for row in flat if row["field"]=="aliases[0]")==10
print(json.dumps({"pass":True,"batchId":"T11-B04","assignedCanonicalIds":IDS,"batchCoverage":len(entries),"fieldEvidence":len(flat),"englishAndLatinFields":20,"learnerNameOverlays":10,"sourceHanjaValues":9,"withheldIncompleteHanja":["HA-M-000016"],"checkedCoverageTotal":38,"humanReviewed":False,"nextBatchStarted":False,"nextTask":"T11-B05"},ensure_ascii=False,indent=2))
