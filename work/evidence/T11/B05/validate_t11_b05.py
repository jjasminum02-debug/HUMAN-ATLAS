"""Validate T11-B05 assignment, names, coverage and field-level provenance."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
IDS=[f"HA-M-{n:06d}" for n in range(22,32)]
FIELDS={"label","korean","hanja","english","aliases[0]"}
EXPECTED={
 "HA-M-000022":("소능형근","작은마름근","小菱形筋"),
 "HA-M-000023":("견갑거근","어깨올림근","肩甲擧筋"),
 "HA-M-000024":("대흉근","큰가슴근","大胸筋"),
 "HA-M-000025":("소흉근","작은가슴근","小胸筋"),
 "HA-M-000026":("쇄골하근","빗장밑근","鎖骨下筋"),
 "HA-M-000027":("전거근","앞톱니근","前鋸筋"),
 "HA-M-000028":("내복사근","배속빗근","內腹斜筋"),
 "HA-M-000029":("복횡근","배가로근","腹橫筋"),
 "HA-M-000030":("삼각근","어깨세모근","三角筋"),
 "HA-M-000031":("극상근","가시위근","棘上筋"),
}
CHECKED="2026-09-25"
def read(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
names=read("atlas-data/terminology/learning-names.json")
ledger=read("atlas-data/terminology/term-review-batches.json")
catalog=read("atlas-data/catalog/canonical-catalog.json")["entities"]
crosswalk=read("atlas-data/catalog/source-crosswalk.json")
canonical={row["id"]:row for row in catalog["muscleConcepts"]}
coverage={row["id"]:row for row in ledger["canonicalCoverage"]}
name_by_id={row["id"]:row for row in names["entries"]}
entries=[row for row in ledger["entries"] if row["id"] in IDS]
flat=[row for row in ledger["fieldEvidence"] if row["entryId"] in IDS]
batch=next(row for row in ledger["batchOrder"] if row["batchId"]=="T11-B05")
assert [row["id"] for row in ledger["canonicalCoverage"] if row["batchId"]=="T11-B05"]==IDS
assert batch["canonicalIds"]==IDS and batch["size"]==10 and batch["status"]=="complete_with_gaps"
assert len(entries)==10 and {row["id"] for row in entries}==set(IDS)
assert len(flat)==51 and len({(row["entryId"],row["field"]) for row in flat})==51
assert all(coverage[i]["status"]=="web_checked_with_gaps" for i in IDS)
assert sum(row["status"]=="web_checked_with_gaps" for row in ledger["canonicalCoverage"])==48
assert ledger["overallT11Status"]=="in_progress_partial"
assert next(row for row in ledger["batchOrder"] if row["batchId"]=="T11-B06")["status"]=="not_started"
assert len(name_by_id)==46 and all(i in name_by_id for i in IDS)
assert len(ledger["fieldEvidence"])==258
entry_by_id={row["id"]:row for row in entries}
for identifier in IDS:
 row=entry_by_id[identifier]; concept=canonical[identifier]; loc=coverage[identifier]["sourceCrosswalkLocator"]
 label,korean,hanja=EXPECTED[identifier]
 assert row["entityType"]==concept["entityType"] and row["parentId"]==concept.get("parentId")
 assert row["canonicalSourceRow"]=={"sourceId":"FIPAT_TA2","tableRow":loc["tableRow"],"printedPage":loc["printedPage"]}
 assert row["webVerificationStatus"]=="web_checked_with_gaps"
 assert row["humanAnatomyReviewStatus"]=="not_performed" and row["humanReviewer"] is None and row["humanReviewed"] is False
 fields={f["field"]:f for f in row["fieldEvidence"]}
 wanted=FIELDS|({"aliases[1]"} if identifier=="HA-M-000030" else set())
 assert set(fields)==wanted
 assert [fields[k]["value"] for k in ("label","korean","hanja")] == [label,korean,hanja]
 assert fields["english"]["value"]==loc["englishTextObservation"]
 assert fields["aliases[0]"]["value"]==loc["latinTextObservation"]
 assert row["fieldEvidenceCount"]==len(wanted)
 overlay=name_by_id[identifier]
 assert (overlay["label"],overlay["korean"],overlay["hanja"])==(label,korean,hanja)
 assert overlay["english"]==loc["englishTextObservation"] and overlay["aliases"][0]==loc["latinTextObservation"]
 assert overlay["parentId"]==concept.get("parentId") and overlay["entityType"]==concept["entityType"] and overlay["lookupOnly"] is False
 assert overlay["humanReviewed"] is False and overlay["status"]=="web_attested_with_gaps"
 if identifier=="HA-M-000030":
  assert overlay["aliases"]==["Musculus deltoideus","Deltoid"]
  assert fields["aliases[1]"]["value"]=="Deltoid"
 for f in fields.values():
  assert f["entryId"]==identifier
  assert f["humanAnatomyReviewStatus"]=="not_performed" and f["humanReviewed"] is False
  assert f["evidence"]
  assert f["missingReason"] is None
  for ev in f["evidence"]:
   sid=ev["sourceId"]
   assert sid in names["sources"] and sid in ledger["sources"]
   source=names["sources"][sid]
   assert source==ledger["sources"][sid]
   assert source["url"].startswith("https://") and source["edition"] and source["accessDate"]==CHECKED
   assert ev["sourceEdition"]==source["edition"] and ev["checkedDate"]==CHECKED
   assert ev["locator"] and ev["verificationMode"]
   if f["field"] in {"english","aliases[0]"}:
    assert sid=="fipat-ta2-b05-opened-original-pdf"
    assert f"table row {loc['tableRow']}" in ev["locator"]
    assert "PDF text opened" in ev["locator"]
   elif f["field"]=="aliases[1]":
    assert sid=="kmle-deltoid" and source["url"]=="https://m.kmle.co.kr/search.php?Search=deltoid"
   else:
    assert sid.startswith("kmle-")
 terms=[term for term in crosswalk["termRecords"] if term["conceptId"]==identifier and term["sourceTextObserved"]]
 assert {term["sourceLanguage"] for term in terms}>={"en","la"}
 assert loc["cellRoleStatus"]=="column_role_confirmed_from_opened_PDF_text_header; visual_table_layout_not_inspected"
assert next(row for row in ledger["batchOrder"] if row["batchId"]=="T11-B07")["status"]=="not_started"
print(json.dumps({"pass":True,"batchId":"T11-B05","assignedExistingIds":IDS,"coverageChecked":10,"requiredFieldEvidence":50,"preservedDeltoidAliasEvidence":1,"batchFieldEvidence":51,"cumulativeFieldEvidence":258,"learnerOverlaysTotal":46,"newOverlays":9,"preexistingOverlayEnriched":["HA-M-000030"],"checkedCanonicalTotal":48,"catalogDenominator":85,"humanReviewed":False,"nextBatchStarted":False,"nextTask":"T11-B06"},ensure_ascii=False,indent=2))
