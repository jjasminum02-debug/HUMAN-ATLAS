#!/usr/bin/env python3
"""Compare T05 protected files and T02 assets against the captured baseline."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "work/evidence/T05/state-before.json"
OUTPUT = ROOT / "work/evidence/T05/preservation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> int:
    before = json.loads(BASELINE.read_text(encoding="utf-8"))
    protected = {}
    errors = []
    for category in ("preexistingUserFilesSha256", "t02AssetsSha256"):
        rows = {}
        for relative_path, expected in before[category].items():
            path = ROOT / relative_path
            actual = sha256(path) if path.is_file() else None
            rows[relative_path] = {"before": expected, "after": actual, "unchanged": actual == expected}
            if actual != expected:
                errors.append(f"protected file/hash mismatch: {relative_path}")
        protected[category] = rows

    opensim_head = subprocess.check_output(["git", "-C", str(ROOT / "OpenSim_Models"), "rev-parse", "HEAD"], text=True).strip()
    opensim_dirty = subprocess.check_output(["git", "-C", str(ROOT / "OpenSim_Models"), "status", "--short"], text=True).strip()
    if opensim_head != before["openSimModelsHead"]:
        errors.append("OpenSim_Models HEAD changed")
    if opensim_dirty:
        errors.append("OpenSim_Models worktree is dirty")

    result = {
        "passed": not errors,
        "baselineProjectHead": before["projectHead"],
        "projectHeadAtCheck": git("rev-parse", "HEAD"),
        "preexistingUserFilesSha256": protected["preexistingUserFilesSha256"],
        "t02AssetsSha256": protected["t02AssetsSha256"],
        "openSimModels": {
            "baselineHead": before["openSimModelsHead"],
            "headAtCheck": opensim_head,
            "statusShort": opensim_dirty,
            "unchangedAndClean": opensim_head == before["openSimModelsHead"] and not opensim_dirty,
        },
        "errors": errors,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "errors": errors, "openSimModels": result["openSimModels"]}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
