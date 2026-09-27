#!/usr/bin/env python3
"""Verify T92 did not alter the frozen pre-existing workspace or OpenSim source tree."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "work/evidence/T92/start-baseline.json"
ALLOWED_SHARED_DELTAS = {"work/STATUS.md", "work/task-registry-r15.json"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(cwd), *args], text=True).strip()


def main() -> int:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    changed = []
    missing = []
    checked = []
    for row in baseline["preservedInputs"]:
        path = ROOT / row["path"]
        if not path.is_file():
            missing.append(row["path"])
            continue
        actual = sha(path)
        if actual != row["sha256"]:
            if row["path"] in ALLOWED_SHARED_DELTAS:
                changed.append({"path": row["path"], "baselineSha256": row["sha256"], "currentSha256": actual, "allowed": True})
            else:
                changed.append({"path": row["path"], "baselineSha256": row["sha256"], "currentSha256": actual, "allowed": False})
        else:
            checked.append(row["path"])

    opensim = ROOT / "OpenSim_Models"
    opensim_head = git(opensim, "rev-parse", "HEAD")
    opensim_status = git(opensim, "status", "--porcelain", "--untracked-files=all")
    opensim_clean = not opensim_status
    source_acq = json.loads((ROOT / "work/evidence/T92/source-acquisition.json").read_text(encoding="utf-8"))
    source_cache_hashes = []
    for row in source_acq["files"]:
        path = ROOT / row["cacheRelativePath"]
        actual = sha(path)
        ok = actual == row["sha256"]
        source_cache_hashes.append({"sourceElementFileId": row["sourceElementFileId"], "sha256": actual, "matchesAcquisition": ok})

    unexpected_changes = [row for row in changed if not row["allowed"]]
    result = {
        "revision": "T92-PRESERVATION-CHECK-v1",
        "task": "T92",
        "result": "pass" if not missing and not unexpected_changes and opensim_clean and opensim_head == baseline["openSimModels"]["head"] and all(row["matchesAcquisition"] for row in source_cache_hashes) else "fail",
        "baselineHead": baseline["startedFromHead"],
        "baselineInputCount": len(baseline["preservedInputs"]),
        "unchangedBaselineInputCount": len(checked),
        "allowedSharedStatusDeltas": changed,
        "missingBaselineInputs": missing,
        "unexpectedChangedBaselineInputs": unexpected_changes,
        "openSimModels": {"baselineHead": baseline["openSimModels"]["head"], "currentHead": opensim_head, "baselineClean": baseline["openSimModels"]["clean"], "currentClean": opensim_clean, "statusPorcelain": opensim_status.splitlines()},
        "newT92RawCacheMatchesAcquisition": source_cache_hashes,
        "scopeNote": "New T92 evidence/package files are outside the start inventory. The only permitted edits to pre-existing files are the requested shared STATUS and R15 registry state deltas."
    }
    output = ROOT / "work/evidence/T92/preservation-final.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
