#!/usr/bin/env python3
"""Structural, provenance, batch-size, mapping, and review-state audit for T11-B01."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
review = json.loads((ROOT / "atlas-data/terminology/term-review-batches.json").read_text())
names = json.loads((ROOT / "atlas-data/terminology/learning-names.json").read_text())
catalog_doc = json.loads((ROOT / "atlas-data/catalog/canonical-catalog.json").read_text())
crosswalk = json.loads((ROOT / "atlas-data/catalog/source-crosswalk.json").read_text())
catalog_status = json.loads((ROOT / "atlas-data/catalog/catalog-status.json").read_text())

checks = []
def check(name, condition, detail=""):
    if not condition:
        raise AssertionError(f"{name}: {detail}")
    checks.append({"check": name, "passed": True, "detail": detail})

catalog_entities = catalog_doc["entities"]
catalog_ids = {
    row["id"]: row["entityType"]
    for key in ("muscleConcepts", "muscleParts")
    for row in catalog_entities[key]
}
crosswalk_ids = [row["stableConceptId"] for row in crosswalk["catalogItems"]]
coverage = review["canonicalCoverage"]
coverage_ids = [row["id"] for row in coverage]
check("catalog-crosswalk-equality", set(catalog_ids) == set(crosswalk_ids) == set(coverage_ids) and len(coverage_ids) == 85,
      f"catalog={len(catalog_ids)} crosswalk={len(crosswalk_ids)} coverage={len(coverage_ids)}")

batches = review["batchOrder"]
assigned = [identifier for batch in batches for identifier in batch["canonicalIds"]]
check("canonical-batch-unique-complete", len(assigned) == 85 and len(set(assigned)) == 85 and set(assigned) == set(catalog_ids),
      f"assigned={len(assigned)} unique={len(set(assigned))}")
check("all-batches-at-most-ten", all(batch["size"] <= 10 for batch in batches),
      str({batch["batchId"]: batch["size"] for batch in batches}))
check("batch-size-fields-match", all(batch["size"] == len(batch["canonicalIds"]) + len(batch["lookupEntryIds"]) for batch in batches),
      "all declared batch sizes equal target counts")

expected_canonical = {
    "HA-M-000001", "HA-M-000002", "HA-M-000003", "HA-M-000004",
    "HA-M-000005", "HA-M-000006", "HA-M-000019", "HA-P-000015",
}
expected_lookup = {"LOOKUP-SPLENIUS-CAPITIS", "LOOKUP-SPLENIUS-CERVICIS"}
b01 = batches[0]
check("B01-bounded-targets", b01["batchId"] == "T11-B01" and set(b01["canonicalIds"]) == expected_canonical and set(b01["lookupEntryIds"]) == expected_lookup and b01["size"] == 10,
      f"canonical={len(b01['canonicalIds'])}; lookup={len(b01['lookupEntryIds'])}")
check("partial-catalog-not-whole-body", review["catalogScope"]["currentPartialCatalogItems"] == 85 and review["catalogScope"]["denominatorFrozen"] is False and review["catalogScope"]["wholeBodyGate"] == "blocked",
      "85 is explicitly documented as a partial catalog")

overlay_ids = [entry["id"] for entry in names["entries"]]
check("no-overlay-id-duplicates", len(overlay_ids) == len(set(overlay_ids)), f"overlay entries={len(overlay_ids)}")
check("no-new-lookup-canonical-id", expected_lookup.isdisjoint(catalog_ids) and all(
    next(row for row in names["entries"] if row["id"] == identifier)["lookupOnly"] is True for identifier in expected_lookup
), "both splenius records remain lookupOnly and absent from canonical")
entry_by_id = {entry["id"]: entry for entry in names["entries"]}
review_by_id = {entry["id"]: entry for entry in review["entries"]}
check("B01-evidence-target-count", set(review_by_id) == expected_canonical | expected_lookup and len(review_by_id) == 10,
      f"review entries={len(review_by_id)}")
check("overlay-entry-ids-preserved", len(names["entries"]) == 13, "T10 overlay entry count remains 13")

for identifier, record in review_by_id.items():
    overlay_entry = entry_by_id[identifier]
    check(f"{identifier}-human-review-separated",
          record["humanAnatomyReviewStatus"] == "not_performed"
          and record["humanReviewed"] is False
          and record["humanReviewer"] is None
          and overlay_entry["humanReviewed"] is False,
          "web verification does not set or imply a human review")
    field_rows = record["fieldEvidence"]
    check(f"{identifier}-field-evidence-present",
          len(field_rows) == record["fieldEvidenceCount"] and all(row["entryId"] == identifier for row in field_rows),
          f"{len(field_rows)} field-level records")
    expected_values = {
        "label": overlay_entry.get("label"),
        "korean": overlay_entry.get("korean"),
        "english": overlay_entry.get("english"),
        "hanja": overlay_entry.get("hanja"),
    }
    for field_name, expected in expected_values.items():
        matches = [row for row in field_rows if row["field"] == field_name]
        check(f"{identifier}-{field_name}-single-value-record",
              len(matches) == 1 and matches[0]["value"] == expected,
              f"overlay value {expected!r}")
    alias_rows = [row for row in field_rows if row["field"].startswith("aliases[")]
    check(f"{identifier}-aliases-covered", len(alias_rows) == len(overlay_entry.get("aliases", [])),
          f"aliases={len(alias_rows)}")
    for row in field_rows:
        if row["value"] is None:
            check(f"{identifier}-{row['field']}-missing-reason",
                  bool(row["missingReason"]) and row["state"].startswith("missing"),
                  "null term has an explicit missing/conflict reason")
        for evidence in row["evidence"]:
            check(f"{identifier}-{row['field']}-source-reference",
                  evidence["sourceId"] in review["sources"]
                  and evidence["checkedDate"] == review["checkedDate"]
                  and bool(evidence["locator"])
                  and bool(evidence["sourceEdition"]),
                  f"{evidence['sourceId']} locator and edition state recorded")
    if identifier in expected_lookup:
        check(f"{identifier}-lookup-not-canonical",
              record["isCanonical"] is False
              and record["canonicalStatus"] == "no_matching_id_in_current_partial_catalog"
              and record["canonicalSourceRow"] is None,
              "no guessed stable ID or row-to-canonical join")

check("splenius-hanja-fields-added", entry_by_id["LOOKUP-SPLENIUS-CAPITIS"]["hanja"] == "頭板狀筋"
      and entry_by_id["LOOKUP-SPLENIUS-CERVICIS"]["hanja"] == "頸板狀筋",
      "both characters are visible in KMLE legacy terminology page text")
check("trapezius-same-concept-forms",
      entry_by_id["HA-M-000019"]["label"] == "승모근"
      and entry_by_id["HA-M-000019"]["korean"] == "등세모근"
      and entry_by_id["HA-M-000019"]["hanja"] == "僧帽筋"
      and entry_by_id["HA-M-000019"]["english"].lower() == "trapezius",
      "four name forms remain connected to HA-M-000019")
check("source-records-have-edition-state",
      all(source.get("edition") and source.get("accessDate") == review["checkedDate"] for source in review["sources"].values()),
      "edition is exact, explicitly unavailable, or not applicable")
check("review-manifest-does-not-claim-anatomy-approval",
      all(row["humanAnatomyReviewStatus"] == "not_performed" and row["humanReviewed"] is False for row in review["fieldEvidence"]),
      "all web/name evidence remains separate from human anatomy review")

result = {
    "pass": True,
    "validator": "T11-B01",
    "checkedDate": review["checkedDate"],
    "checkCount": len(checks),
    "canonicalCoverage": len(coverage_ids),
    "canonicalStatusCounts": {
        state: sum(1 for row in coverage if row["status"] == state)
        for state in sorted({row["status"] for row in coverage})
    },
    "batchSizes": {batch["batchId"]: batch["size"] for batch in batches},
    "B01EntryCount": len(review["entries"]),
    "fieldEvidenceCount": len(review["fieldEvidence"]),
    "humanAnatomyReview": "not_performed",
    "catalogDenominatorFrozen": catalog_status["denominatorFrozen"],
    "checks": checks,
}
out = ROOT / "work/evidence/T11/validation.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({key: value for key, value in result.items() if key != "checks"}, ensure_ascii=False))
