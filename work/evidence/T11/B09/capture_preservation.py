"""Capture the exact pre-T11-B09 project and read-only OpenSim baseline."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "work/evidence/T11/B09"


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


files: dict[str, str] = {}
for path in sorted(ROOT.rglob("*")):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT).as_posix()
    if rel == ".git" or rel.startswith(".git/") or rel.startswith("work/evidence/T11/B09/"):
        continue
    files[rel] = digest(path.read_bytes())

open_sim = ROOT / "OpenSim_Models"
before = {
    "taskId": "T11-B09",
    "capturedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "projectHead": git("rev-parse", "HEAD").strip(),
    "projectTrackedDiffSha256": digest(subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=ROOT)),
    "projectStatusBefore": git("status", "--short", "--untracked-files=all").splitlines(),
    "projectFilesSha256": files,
    "openSimHead": git("rev-parse", "HEAD", cwd=open_sim).strip(),
    "openSimStatusBefore": git("status", "--porcelain", "--untracked-files=all", cwd=open_sim).splitlines(),
    "openSimFilesSha256": {rel: value for rel, value in files.items() if rel.startswith("OpenSim_Models/")},
    "note": "Fresh baseline captured before B09 edits; pre-existing changes are treated as user/task data and compared at end.",
}
(EVIDENCE / "preservation-before.json").write_text(json.dumps(before, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "projectHead": before["projectHead"],
    "preExistingProjectFiles": len(files),
    "trackedDiffSha256": before["projectTrackedDiffSha256"],
    "openSimHead": before["openSimHead"],
    "openSimStatus": before["openSimStatusBefore"],
    "openSimFiles": len(before["openSimFilesSha256"]),
}, ensure_ascii=False, indent=2))
