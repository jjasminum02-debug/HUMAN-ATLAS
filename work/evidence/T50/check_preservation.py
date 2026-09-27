#!/usr/bin/env python3
"""Verify T50 did not alter pre-existing user files or read-only OpenSim inputs."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T50"
baseline = json.loads((EVIDENCE / "start-baseline.json").read_text())
allowed_existing_edits = {"work/STATUS.md", "work/task-registry-r15.json"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


preexisting = []
for item in baseline["initialGitStatus"]:
    path = ROOT / item["path"]
    actual = sha256(path) if path.is_file() else None
    changed = actual != item.get("sha256") or not path.is_file()
    preexisting.append({
        "path": item["path"],
        "expectedSha256": item.get("sha256"),
        "actualSha256": actual,
        "unchangedFromStart": not changed,
        "intentionalT50StatusChange": item["path"] in allowed_existing_edits and changed,
    })

protected = []
for rel, expected in baseline["protectedRelevantInputHashes"].items():
    path = ROOT / rel
    actual = sha256(path) if path.is_file() else None
    changed = actual != expected.get("sha256")
    protected.append({
        "path": rel,
        "expectedSha256": expected.get("sha256"),
        "actualSha256": actual,
        "unchanged": not changed,
        "intentionalT50StatusChange": rel in allowed_existing_edits and changed,
    })

models = ROOT / "OpenSim_Models"
head = subprocess.run(["git", "-C", str(models), "rev-parse", "HEAD"], check=True, text=True, capture_output=True).stdout.strip()
status = subprocess.run(["git", "-C", str(models), "status", "--short"], check=True, text=True, capture_output=True).stdout.splitlines()
tracked = subprocess.run(["git", "-C", str(models), "ls-files", "-z"], check=True, capture_output=True).stdout.decode().split("\0")
tracked = sorted(rel for rel in tracked if rel)
tree = hashlib.sha256()
for rel in tracked:
    path = models / rel
    if path.is_file():
        tree.update(rel.encode())
        tree.update(b"\0")
        tree.update(sha256(path).encode())
        tree.update(b"\n")
model_baseline = baseline["openSimModels"]
same_models = head == model_baseline["head"] and not status and len(tracked) == model_baseline["trackedFileCount"] and tree.hexdigest() == model_baseline["trackedFilesSha256"]
unexpected_preexisting = [row for row in preexisting if not row["unchangedFromStart"] and not row["intentionalT50StatusChange"]]
unexpected_protected = [row for row in protected if not row["unchanged"] and not row["intentionalT50StatusChange"]]

result = {
    "task": "T50",
    "checkedOn": "2026-09-27",
    "startingHead": baseline["startingHead"],
    "preexistingFiles": {
        "count": len(preexisting),
        "unchangedCount": sum(row["unchangedFromStart"] for row in preexisting),
        "intentionalT50StatusEdits": [row for row in preexisting if row["intentionalT50StatusChange"]],
        "unexpectedChangedOrMissing": unexpected_preexisting,
    },
    "protectedInputs": {
        "count": len(protected),
        "unchangedCount": sum(row["unchanged"] for row in protected),
        "intentionalT50StatusEdits": [row for row in protected if row["intentionalT50StatusChange"]],
        "unexpectedChanged": unexpected_protected,
    },
    "openSimModels": {
        "head": head,
        "expectedHead": model_baseline["head"],
        "clean": not status,
        "status": status,
        "trackedFileCount": len(tracked),
        "trackedFilesSha256": tree.hexdigest(),
        "sameAsStart": same_models,
    },
}
result["passed"] = not unexpected_preexisting and not unexpected_protected and same_models
(EVIDENCE / "preservation-after.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({
    "passed": result["passed"],
    "preexistingUnchanged": result["preexistingFiles"]["unchangedCount"],
    "preexistingCount": result["preexistingFiles"]["count"],
    "intentionalStatusEdits": result["preexistingFiles"]["intentionalT50StatusEdits"],
    "protectedUnchanged": result["protectedInputs"]["unchangedCount"],
    "protectedCount": result["protectedInputs"]["count"],
    "unexpectedChanges": unexpected_preexisting + unexpected_protected,
    "openSimModelsSame": same_models,
}, ensure_ascii=False, indent=2))
if not result["passed"]:
    raise SystemExit(1)
