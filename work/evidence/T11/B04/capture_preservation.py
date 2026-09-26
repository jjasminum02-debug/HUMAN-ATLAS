"""Capture the pre-B04 workspace and read-only OpenSim baseline."""
from __future__ import annotations
import hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "work/evidence/T11/B04"

def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True)

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

files: dict[str, str] = {}
for path in sorted(ROOT.rglob("*")):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith(".git/") or rel == ".git":
        continue
    if rel.startswith("work/evidence/T11/B04/"):
        continue
    files[rel] = digest(path.read_bytes())
open_sim = ROOT / "OpenSim_Models"
result = {
    "taskId": "T11-B04",
    "capturedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "projectHead": git("rev-parse", "HEAD").strip(),
    "projectTrackedDiffSha256": digest(subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=ROOT)),
    "projectStatusBefore": git("status", "--short", "--untracked-files=all").splitlines(),
    "projectFilesSha256": files,
    "openSimHead": git("rev-parse", "HEAD", cwd=open_sim).strip(),
    "openSimStatusBefore": git("status", "--porcelain", "--untracked-files=all", cwd=open_sim).splitlines(),
    "openSimFilesSha256": {rel: value for rel, value in files.items() if rel.startswith("OpenSim_Models/")},
    "note": "Read-only preservation baseline before T11-B04 edits; B04 evidence directory is excluded from the pre-existing file list.",
}
(EVIDENCE / "preservation-before.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"projectHead": result["projectHead"], "preExistingProjectFiles": len(files), "trackedDiffSha256": result["projectTrackedDiffSha256"], "openSimHead": result["openSimHead"], "openSimStatus": result["openSimStatusBefore"], "openSimFiles": len(result["openSimFilesSha256"])}, ensure_ascii=False, indent=2))
