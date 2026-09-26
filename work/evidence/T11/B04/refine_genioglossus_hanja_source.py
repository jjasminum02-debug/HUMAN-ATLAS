"""Separate the incomplete genioglossus Hanja source from its term source."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
EVIDENCE=ROOT/"work/evidence/T11/B04"
source_id="kmle-b04-genioglossus-hanja-fragment"
source={
 "title":"KMLE legacy genioglossal Hanja fragment check",
 "url":"https://m.kmle.co.kr/search.php?Page=5&Search=posterior+papillary+muscle",
 "locator":"Search-result excerpt, old 대한의협 2 row ‘genioglossal muscle’: 이설근·턱끝혀근(舌筋). Only the fragment 舌筋 is displayed, not a complete compound for this muscle. Direct open failed with cache miss; underlying edition/revision is not exposed.",
 "edition":"KMLE web aggregation; exact underlying dictionary edition/revision is not exposed in the checked page or index excerpt.",
 "accessDate":"2026-09-25",
 "verificationMode":"search_result_excerpt_only; direct_HTML_open_failed_cache_miss; incomplete_fragment_not_adopted",
 "scope":"Negative/near-match evidence for withholding a complete Hanja value; no term is created from the fragment.",
}
def load(rel):return json.loads((ROOT/rel).read_text(encoding="utf-8"))
def save(rel,data):(ROOT/rel).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
names=load("atlas-data/terminology/learning-names.json")
ledger=load("atlas-data/terminology/term-review-batches.json")
assert source_id not in names["sources"] and source_id not in ledger["sources"],"refinement already applied"
names["sources"][source_id]=source
ledger["sources"][source_id]=source
identifier="HA-M-000016"
for entry in ledger["entries"]:
 if entry["id"]==identifier:
  field=next(item for item in entry["fieldEvidence"] if item["field"]=="hanja")
  assert field["value"] is None
  field["evidence"]=[{"sourceId":source_id,"locator":source["locator"],"verificationMode":source["verificationMode"],"sourceEdition":source["edition"],"checkedDate":source["accessDate"]}]
  candidate=entry["unadoptedCandidates"][0]
  candidate["sourceIds"]=[source_id]
  break
else:raise SystemExit("B04 genioglossus evidence entry missing")
for field in ledger["fieldEvidence"]:
 if field["entryId"]==identifier and field["field"]=="hanja":
  field["evidence"]=[{"sourceId":source_id,"locator":source["locator"],"verificationMode":source["verificationMode"],"sourceEdition":source["edition"],"checkedDate":source["accessDate"]}]
  break
else:raise SystemExit("B04 flat genioglossus Hanja evidence missing")
for overlay in names["entries"]:
 if overlay["id"]==identifier:
  overlay["sourceIds"]=sorted(set(overlay["sourceIds"])|{source_id})
  break
else:raise SystemExit("B04 genioglossus overlay missing")
save("atlas-data/terminology/learning-names.json",names)
save("atlas-data/terminology/term-review-batches.json",ledger)
print(json.dumps({"pass":True,"entryId":identifier,"field":"hanja","sourceId":source_id,"value":None,"reason":"incomplete fragment withheld"},ensure_ascii=False,indent=2))
