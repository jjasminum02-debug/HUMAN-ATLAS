#!/usr/bin/env python3
"""Compare pre-existing project files against the T11-B01 preservation baseline."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
before = json.loads((ROOT / "work/evidence/T11/preservation-before.json").read_text())
allowed = {
    "atlas-data/terminology/learning-names.json",
    "atlas-web/src/data/learning.ts",
    "atlas-web/src/domain/search.ts",
    "atlas-web/src/domain/search.test.ts",
    "work/STATUS.md",
}
generated_prefixes = ("atlas-web/dist/",)
generated_suffixes = (".tsbuildinfo",)
changed, missing = [], []
for rel, original_hash in before["projectFilesSha256"].items():
    path = ROOT / rel
    if not path.exists():
        missing.append(rel)
        continue
    current_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if current_hash != original_hash:
        changed.append(rel)

unexpected = [
    rel for rel in changed
    if rel not in allowed
    and not rel.startswith(generated_prefixes)
    and not rel.endswith(generated_suffixes)
]
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).splitlines()
opensim_head = subprocess.check_output(["git", "-C", "OpenSim_Models", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
opensim_status = subprocess.check_output(["git", "-C", "OpenSim_Models", "status", "--porcelain"], cwd=ROOT, text=True).splitlines()
generated_missing = [rel for rel in missing if rel.startswith(generated_prefixes)]
unexpected_missing = [rel for rel in missing if rel not in generated_missing]
assert not unexpected_missing, f"Pre-existing source/user files disappeared: {unexpected_missing}"
assert not unexpected, f"Unexpected pre-existing file changes: {unexpected}"
assert head == before["projectHead"], f"Project HEAD changed: {before['projectHead']} -> {head}"
assert opensim_head == before["openSimModels"]["head"], "OpenSim_Models HEAD changed"
assert not opensim_status, f"OpenSim_Models became dirty: {opensim_status}"
result = {
    "pass": True,
    "capturedDate": before["capturedAt"],
    "preExistingProjectFilesCompared": len(before["projectFilesSha256"]),
    "preExistingFilesChanged": changed,
    "allowedSourceChanges": [rel for rel in changed if rel in allowed],
    "generatedBuildOutputsChanged": [
        rel for rel in changed
        if rel.startswith(generated_prefixes) or rel.endswith(generated_suffixes)
    ],
    "preExistingSourceFilesMissing": unexpected_missing,
    "generatedHashBundlesRemovedByCleanBuild": generated_missing,
    "unexpectedPreExistingChanges": unexpected,
    "projectHead": head,
    "projectStatusAfter": status,
    "openSimModels": {
        "head": opensim_head,
        "statusPorcelain": opensim_status,
        "unchanged": True,
        "readOnly": True,
    },
    "commitCreated": False,
    "commitNote": "Pre-existing T10 working-tree changes remain; no mixed checkpoint commit was made.",
}
out = ROOT / "work/evidence/T11/preservation-after.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({key: value for key, value in result.items() if key == "pass" or key == "preExistingFilesCompared" or key == "preExistingFilesChanged" or key == "unexpectedPreExistingChanges" or key == "generatedHashBundlesRemovedByCleanBuild" or key == "preExistingSourceFilesMissing" or key == "openSimModels"}, ensure_ascii=False))
