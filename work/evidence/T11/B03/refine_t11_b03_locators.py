"""Write the exact TA2 row/field into every B03 English and Latin evidence locator."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "atlas-data/terminology/term-review-batches.json"
FIPAT_ID = "fipat-ta2-b03-index"
IDS = [f"HA-G-{number:06d}" for number in range(11, 17)] + [f"HA-M-{number:06d}" for number in range(7, 11)]
ledger = json.loads(PATH.read_text(encoding="utf-8"))
coverage = {row["id"]: row for row in ledger["canonicalCoverage"]}
updated = 0
def refine(field):
    global updated
    if field["entryId"] not in IDS or field["field"] not in ("english", "aliases[0]"):
        return
    identifier = field["entryId"]
    loc = coverage[identifier]["sourceCrosswalkLocator"]
    source_text = loc["englishTextObservation"] if field["field"] == "english" else loc["latinTextObservation"]
    language = "English" if field["field"] == "english" else "Latin"
    field["evidence"] = [
        {
            **item,
            "locator": f"TA2 Part 2 printed p. {loc['printedPage']}, table row {loc['tableRow']}: {language} text observation '{source_text}' in official hosted-PDF search-result text; table-cell role remains unverified and original PDF was not visually checked.",
        }
        if item["sourceId"] == FIPAT_ID else item
        for item in field["evidence"]
    ]
    updated += 1
for field in ledger["fieldEvidence"]:
    refine(field)
for entry in ledger["entries"]:
    if entry["id"] in IDS:
        for field in entry["fieldEvidence"]:
            refine(field)
PATH.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"updated": True, "batchId": "T11-B03", "logicalEnglishLatinFields": updated // 2, "serializedLocatorCopiesUpdated": updated, "ids": IDS}, ensure_ascii=False, indent=2))
