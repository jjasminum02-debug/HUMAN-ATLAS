"""Compare B03 post-task state against the pre-task project/OpenSim snapshot."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "work/evidence/T11/B03"
BEFORE = json.loads((EVIDENCE / "preservation-before.json").read_text(encoding="utf-8"))
ALLOWED_CHANGED = {
    "atlas-data/terminology/learning-names.json",
    "atlas-data/terminology/term-review-batches.json",
    "atlas-web/src/domain/search.test.ts",
    "work/STATUS.md",
    "work/reports/T11.md",
    "work/review-queue/terminology-gaps.md",
}
changed, missing = [], []
for rel, original_hash in BEFORE["projectFilesSha256"].items():
    path = ROOT / rel
    if not path.exists():
        missing.append(rel)
    elif hashlib.sha256(path.read_bytes()).hexdigest() != original_hash:
        changed.append(rel)
unexpected = sorted(set(changed) - ALLOWED_CHANGED)
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
opensim_root = ROOT / "OpenSim_Models"
opensim_head = subprocess.check_output(["git", "-C", str(opensim_root), "rev-parse", "HEAD"], text=True).strip()
opensim_status = subprocess.check_output(["git", "-C", str(opensim_root), "status", "--porcelain", "--untracked-files=all"], text=True).splitlines()
assert not missing, f"Pre-existing files missing: {missing}"
assert not unexpected, f"Unexpected pre-existing file changes: {unexpected}"
assert head == BEFORE["projectHead"], "Project HEAD changed during B03"
assert opensim_head == BEFORE["openSimHead"], "OpenSim_Models HEAD changed during B03"
assert not opensim_status, f"OpenSim_Models is no longer clean: {opensim_status}"
result = {
    "pass": True,
    "taskId": "T11-B03",
    "preExistingFilesCompared": len(BEFORE["projectFilesSha256"]),
    "allowedPreExistingFilesChanged": changed,
    "unexpectedPreExistingFilesChanged": unexpected,
    "preExistingFilesMissing": missing,
    "projectHeadBeforeAndAfter": head,
    "projectTrackedDiffSha256Before": BEFORE["projectTrackedDiffSha256"],
    "projectStatusAfter": subprocess.check_output(["git", "status", "--short", "--untracked-files=all"], cwd=ROOT, text=True).splitlines(),
    "openSimModels": {"headBeforeAndAfter": opensim_head, "statusAfter": opensim_status, "unchanged": True, "readOnly": True},
    "commitCreated": False,
    "note": "Pre-existing T10/B01/B02 user changes were preserved; no mixed-worktree commit was created.",
}
(EVIDENCE / "preservation-after.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: result[key] for key in ("pass", "preExistingFilesCompared", "allowedPreExistingFilesChanged", "unexpectedPreExistingFilesChanged", "preExistingFilesMissing", "openSimModels", "commitCreated")}, ensure_ascii=False, indent=2))
