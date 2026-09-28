#!/usr/bin/env python3
"""Update the T98 row only after verifying the captured execution baseline."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "work/EXECUTION.json"
BASELINE = ROOT / "work/evidence/T98/start-baseline.json"
OUT = Path(__file__).resolve().parent / "execution-record-delta.json"


def canonical_hash(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
expected_hash = baseline["protectedInputs"]["work/EXECUTION.json"]["sha256"]
before_raw = SOURCE.read_bytes()
before_hash = hashlib.sha256(before_raw).hexdigest()
if before_hash != expected_hash:
    raise SystemExit("EXECUTION.json changed since T98 baseline; refusing to overwrite concurrent edits")
data = json.loads(before_raw)
if "T98" not in data["tasks"]:
    raise SystemExit("T98 record missing")
old_row = data["tasks"]["T98"]
other_tasks_before = {key: value for key, value in data["tasks"].items() if key != "T98"}
new_row = json.loads(json.dumps(old_row))
new_row["executionStatus"] = "in_progress"
new_row["acceptance"] = "partial"
new_row["progress"] = {
    "nextUnit": "verified-evaluated-exporter-and-12-object-preview",
    "completedUnits": [
        "read-and-hash-pinned-inputs-and-prior-work",
        "inventory-all-serialized-source-objects-meshes-curves-collections-and-links",
        "freeze-all-12-t96-regions-and-542-target-records-with-563-memberships",
        "record-z-anatomy-and-bodyparts3d-rights-families-and-exceptions",
        "freeze-exact-12-object-export-candidate-set-with-source-hash-and-locators"
    ]
}
data["tasks"]["T98"] = new_row
after_raw = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode()
after = json.loads(after_raw)
other_tasks_after = {key: value for key, value in after["tasks"].items() if key != "T98"}
if canonical_hash(other_tasks_before) != canonical_hash(other_tasks_after):
    raise SystemExit("non-T98 task record changed; refusing write")
SOURCE.write_bytes(after_raw)

delta = {
    "task": "T98",
    "sourcePath": "work/EXECUTION.json",
    "beforeFileSha256": before_hash,
    "afterFileSha256": hashlib.sha256(after_raw).hexdigest(),
    "beforeT98Row": old_row,
    "afterT98Row": new_row,
    "unchangedOtherTaskRecordsSha256": canonical_hash(other_tasks_before),
    "onlyTaskRecordChanged": True,
    "acceptance": "partial",
    "executionStatus": "in_progress",
    "nextUnit": new_row["progress"]["nextUnit"]
}
OUT.write_text(json.dumps(delta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"beforeFileSha256": before_hash, "afterFileSha256": delta["afterFileSha256"], "changedTask": "T98", "unchangedOtherTaskRecordsSha256": delta["unchangedOtherTaskRecordsSha256"], "acceptance": delta["acceptance"], "nextUnit": delta["nextUnit"]}, ensure_ascii=False, indent=2))
