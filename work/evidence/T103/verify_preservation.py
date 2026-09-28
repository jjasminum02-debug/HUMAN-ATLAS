#!/usr/bin/env python3
"""Recheck T103's frozen predecessor inputs and protected user data."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "work/evidence/T103/start-baseline.json"
OUT = ROOT / "work/evidence/T103/preservation.json"
ALLOWED_T103_INPUT_DELTAS = {
    "atlas-data/tools/build_bodyparts3d_r4_t102.py",
    "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py",
    "work/STATUS.md",
    "work/task-registry-r15.json",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def main() -> int:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    changed_inputs = []
    missing_inputs = []
    for rel, expected in baseline["inputFiles"].items():
        path = ROOT / rel
        if not path.is_file():
            missing_inputs.append(rel)
        elif digest(path) != expected["sha256"]:
            changed_inputs.append(rel)

    protected = []
    for group, rows in baseline["protectedHistoricalInputs"].items():
        for row in rows:
            path = ROOT / row["path"]
            actual = digest(path) if path.is_file() else None
            protected.append({"group": group, "path": row["path"], "expectedSha256": row["sha256"],
                              "actualSha256": actual, "unchanged": actual == row["sha256"]})

    opensim = ROOT / "OpenSim_Models"
    opensim_head = git(opensim, "rev-parse", "HEAD")
    opensim_status = git(opensim, "status", "--short")
    owned_files = [
        "atlas-data/tools/build_bodyparts3d_r4_t102.py",
        "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py",
        "work/STATUS.md",
        "work/task-registry-r15.json",
    ]
    unexpected = sorted(set(changed_inputs) - ALLOWED_T103_INPUT_DELTAS)
    report = {
        "task": "T103",
        "revision": "T103-preservation-check-v1",
        "baseline": "work/evidence/T103/start-baseline.json",
        "baselineHead": baseline["startHead"],
        "inputFilesChecked": len(baseline["inputFiles"]),
        "missingBaselineInputs": missing_inputs,
        "changedBaselineInputs": changed_inputs,
        "allowedTaskOwnedOrSharedDeltaPaths": owned_files,
        "unexpectedBaselineInputChanges": unexpected,
        "protectedHistoricalInputCount": len(protected),
        "protectedHistoricalInputsUnchanged": all(row["unchanged"] for row in protected),
        "protectedHistoricalInputs": protected,
        "openSimModels": {"headBefore": baseline["openSimModels"]["head"], "headAfter": opensim_head,
                          "statusBefore": baseline["openSimModels"]["status"], "statusAfter": opensim_status,
                          "unchanged": opensim_head == baseline["openSimModels"]["head"] and opensim_status == baseline["openSimModels"]["status"]},
        "result": "pass" if not missing_inputs and not unexpected and all(row["unchanged"] for row in protected)
                  and opensim_head == baseline["openSimModels"]["head"] and opensim_status == baseline["openSimModels"]["status"]
                  else "fail",
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["inputFilesChecked", "missingBaselineInputs", "changedBaselineInputs",
                                             "unexpectedBaselineInputChanges", "protectedHistoricalInputCount",
                                             "protectedHistoricalInputsUnchanged", "openSimModels", "result"]}, indent=2))
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
