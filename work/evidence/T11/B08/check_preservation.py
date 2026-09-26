"""Compare the project and read-only OpenSim with the pre-B08 baseline."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "work/evidence/T11/B08"
BEFORE = json.loads((EVIDENCE / "preservation-before.json").read_text(encoding="utf-8"))
ALLOWED_CHANGED = {
    "atlas-data/terminology/learning-names.json",
    "atlas-data/terminology/term-review-batches.json",
    "atlas-web/src/domain/search.test.ts",
    "work/STATUS.md",
    "work/reports/T11.md",
    "work/review-queue/terminology-gaps.md",
}
ALLOWED_NEW = {"work/tasks/T11-B08.md", "work/reports/T11-B08.md"}


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


current: dict[str, str] = {}
for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    relative = path.relative_to(ROOT).as_posix()
    if relative == ".git" or relative.startswith(".git/"):
        continue
    current[relative] = sha(path.read_bytes())

old = BEFORE["projectFilesSha256"]
missing = sorted(set(old) - set(current))
changed = sorted(relative for relative, digest in old.items() if relative in current and current[relative] != digest)
unexpected_changed = sorted(set(changed) - ALLOWED_CHANGED)
new = sorted(set(current) - set(old))
unexpected_new = sorted(
    relative for relative in new
    if relative not in ALLOWED_NEW and not relative.startswith("work/evidence/T11/B08/")
)
head = git("rev-parse", "HEAD").strip()
opensim = ROOT / "OpenSim_Models"
opensim_head = git("rev-parse", "HEAD", cwd=opensim).strip()
opensim_status = git("status", "--porcelain", "--untracked-files=all", cwd=opensim).splitlines()
opensim_before = BEFORE["openSimFilesSha256"]
opensim_current = {relative: digest for relative, digest in current.items() if relative.startswith("OpenSim_Models/")}
opensim_changed = sorted(relative for relative, digest in opensim_before.items() if opensim_current.get(relative) != digest)
opensim_new = sorted(set(opensim_current) - set(opensim_before))
tracked_diff = sha(subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=ROOT))

result = {
    "pass": not (
        missing or unexpected_changed or unexpected_new or head != BEFORE["projectHead"]
        or opensim_head != BEFORE["openSimHead"] or opensim_status or opensim_changed or opensim_new
    ),
    "taskId": "T11-B08",
    "preExistingProjectFilesCompared": len(old),
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
        "fileChanges": opensim_changed,
        "newFiles": opensim_new,
        "unchanged": not (opensim_status or opensim_changed or opensim_new),
        "readOnly": True,
    },
    "commitCreated": False,
    "note": "Only B08 allow-listed project files changed. The canonical T04 crosswalk remained byte-identical; OpenSim_Models remained byte-identical and clean.",
}
(EVIDENCE / "preservation-after.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if not result["pass"]:
    raise SystemExit(1)
