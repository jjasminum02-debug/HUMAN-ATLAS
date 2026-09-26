"""Compare pre-B06 project files and the read-only OpenSim archive to baseline."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "work/evidence/T11/B06"
BEFORE = json.loads((EVIDENCE / "preservation-before.json").read_text(encoding="utf-8"))
ALLOWED_CHANGED = {
    "atlas-data/terminology/learning-names.json",
    "atlas-data/terminology/term-review-batches.json",
    "atlas-web/src/domain/search.test.ts",
    "work/STATUS.md",
    "work/reports/T11.md",
    "work/review-queue/terminology-gaps.md",
}
ALLOWED_NEW_FILES = {"work/tasks/T11-B06.md", "work/reports/T11-B06.md"}


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


current: dict[str, str] = {}
for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT).as_posix()
    if rel == ".git" or rel.startswith(".git/"):
        continue
    current[rel] = sha(path)

old = BEFORE["projectFilesSha256"]
missing = sorted(set(old) - set(current))
changed = sorted(rel for rel, digest in old.items() if rel in current and current[rel] != digest)
unexpected_changed = sorted(set(changed) - ALLOWED_CHANGED)
new = sorted(set(current) - set(old))
unexpected_new = sorted(
    rel for rel in new
    if rel not in ALLOWED_NEW_FILES and not rel.startswith("work/evidence/T11/B06/")
)
head = git("rev-parse", "HEAD").strip()
opensim = ROOT / "OpenSim_Models"
opensim_head = git("rev-parse", "HEAD", cwd=opensim).strip()
opensim_status = git("status", "--porcelain", "--untracked-files=all", cwd=opensim).splitlines()
opensim_before = BEFORE["openSimFilesSha256"]
opensim_current = {rel: digest for rel, digest in current.items() if rel.startswith("OpenSim_Models/")}
opensim_file_changes = sorted(rel for rel, digest in opensim_before.items() if opensim_current.get(rel) != digest)
opensim_new = sorted(set(opensim_current) - set(opensim_before))
tracked_diff = hashlib.sha256(subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=ROOT)).hexdigest()

assert not missing, f"Pre-existing project files missing: {missing}"
assert not unexpected_changed, f"Unexpected pre-existing changes: {unexpected_changed}"
assert not unexpected_new, f"Unexpected new project files: {unexpected_new}"
assert head == BEFORE["projectHead"], "Project HEAD changed during B06"
assert opensim_head == BEFORE["openSimHead"], "OpenSim_Models HEAD changed during B06"
assert not opensim_status, f"OpenSim_Models Git status changed: {opensim_status}"
assert not opensim_file_changes and not opensim_new, "OpenSim_Models file hashes changed"

result = {
    "pass": True,
    "taskId": "T11-B06",
    "preExistingFilesCompared": len(old),
    "preExistingFilesMissing": missing,
    "preExistingFilesChanged": changed,
    "unexpectedPreExistingChanges": unexpected_changed,
    "newProjectFiles": new,
    "unexpectedNewFiles": unexpected_new,
    "projectHeadBeforeAndAfter": head,
    "projectTrackedDiffSha256Before": BEFORE["projectTrackedDiffSha256"],
    "projectTrackedDiffSha256After": tracked_diff,
    "projectStatusBefore": BEFORE["projectStatusBefore"],
    "projectStatusAfter": git("status", "--short", "--untracked-files=all").splitlines(),
    "openSimModels": {
        "headBeforeAndAfter": opensim_head,
        "statusBefore": BEFORE["openSimStatusBefore"],
        "statusAfter": opensim_status,
        "preExistingFilesCompared": len(opensim_before),
        "fileChanges": opensim_file_changes,
        "newFiles": opensim_new,
        "unchanged": True,
        "readOnly": True,
    },
    "commitCreated": False,
    "note": "Prior user and task files were compared against the B06 baseline. Only the explicit B06 allow-list changed; OpenSim_Models stayed byte-identical and clean.",
}
(EVIDENCE / "preservation-after.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({
    key: result[key] for key in [
        "pass", "preExistingFilesCompared", "preExistingFilesMissing",
        "preExistingFilesChanged", "unexpectedPreExistingChanges", "unexpectedNewFiles",
        "projectHeadBeforeAndAfter", "openSimModels", "commitCreated",
    ]
}, ensure_ascii=False, indent=2))
