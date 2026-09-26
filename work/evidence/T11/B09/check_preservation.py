"""Compare the project and read-only OpenSim with the pre-B09 baseline."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "work/evidence/T11/B09"
BEFORE = json.loads((EVIDENCE / "preservation-before.json").read_text(encoding="utf-8"))
ALLOWED_CHANGED = {
    "atlas-data/terminology/learning-names.json",
    "atlas-data/terminology/term-review-batches.json",
    "atlas-web/src/domain/search.test.ts",
    "work/STATUS.md",
    "work/reports/T11.md",
    "work/review-queue/terminology-gaps.md",
    "work/tasks/T11.md",
}
ALLOWED_NEW = {"work/tasks/T11-B09.md", "work/reports/T11-B09.md"}


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
    if relative not in ALLOWED_NEW and not relative.startswith("work/evidence/T11/B09/")
)
head = git("rev-parse", "HEAD").strip()
open_sim = ROOT / "OpenSim_Models"
open_sim_head = git("rev-parse", "HEAD", cwd=open_sim).strip()
open_sim_status = git("status", "--porcelain", "--untracked-files=all", cwd=open_sim).splitlines()
open_sim_before = BEFORE["openSimFilesSha256"]
open_sim_current = {relative: digest for relative, digest in current.items() if relative.startswith("OpenSim_Models/")}
open_sim_changed = sorted(relative for relative, digest in open_sim_before.items() if open_sim_current.get(relative) != digest)
open_sim_new = sorted(set(open_sim_current) - set(open_sim_before))
tracked_diff = sha(subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=ROOT))
crosswalk = ROOT / "atlas-data/catalog/source-crosswalk.json"
crosswalk_hash_now = sha(crosswalk.read_bytes())

result = {
    "pass": not (
        missing or unexpected_changed or unexpected_new or head != BEFORE["projectHead"]
        or open_sim_head != BEFORE["openSimHead"] or open_sim_status or open_sim_changed or open_sim_new
        or crosswalk_hash_now != BEFORE["projectFilesSha256"].get("atlas-data/catalog/source-crosswalk.json")
    ),
    "taskId": "T11-B09",
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
    "t04SourceCrosswalkSha256BeforeAndAfter": crosswalk_hash_now,
    "openSimModels": {
        "headBeforeAndAfter": open_sim_head,
        "statusBefore": BEFORE["openSimStatusBefore"],
        "statusAfter": open_sim_status,
        "preExistingFilesCompared": len(open_sim_before),
        "fileChanges": open_sim_changed,
        "newFiles": open_sim_new,
        "unchanged": not (open_sim_status or open_sim_changed or open_sim_new),
        "readOnly": True,
    },
    "commitCreated": False,
    "note": "Only B09 allow-listed files changed; the T04 source crosswalk and read-only OpenSim_Models remained byte-identical.",
}
(EVIDENCE / "preservation-after.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if not result["pass"]:
    raise SystemExit(1)
