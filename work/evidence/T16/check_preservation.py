#!/usr/bin/env python3
"""Read-only post-change comparison against the T16 recorded baseline."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE_PATH = ROOT / "work/evidence/T16/start-baseline.json"
OUTPUT_PATH = ROOT / "work/evidence/T16/preservation-after.json"
TASK_OWNED_INPUTS = {"atlas-data/schemas/README.md", "work/STATUS.md", "work/tasks/T16.md"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
issues: list[str] = []
preexisting_rows = []
for item in baseline["preexisting_untracked_files"]:
    path = ROOT / item["path"]
    actual = sha256(path) if path.is_file() else None
    passed = actual == item["sha256"]
    preexisting_rows.append({"path": item["path"], "expectedSha256": item["sha256"], "actualSha256": actual, "passed": passed})
    if not passed:
        issues.append(f"preexisting_untracked_changed:{item['path']}")

snapshot_groups: dict[str, dict[str, object]] = {}
for group, files in baseline["protected_snapshots"].items():
    rows = []
    excluded_task_owned = []
    for relative, expected in files.items():
        if relative in TASK_OWNED_INPUTS:
            excluded_task_owned.append(relative)
            continue
        path = ROOT / relative
        actual = sha256(path) if path.is_file() else None
        passed = actual == expected["expectedSha256"]
        rows.append({"path": relative, "expectedSha256": expected["expectedSha256"], "actualSha256": actual, "passed": passed})
        if not passed:
            issues.append(f"protected_snapshot_changed:{relative}")
    snapshot_groups[group] = {"count": len(rows), "passed": all(row["passed"] for row in rows), "taskOwnedPathsExcluded": excluded_task_owned, "files": rows}

input_rows = []
for relative, expected in baseline["requested_and_current_inputs"].items():
    if expected.get("missing") or relative in TASK_OWNED_INPUTS:
        continue
    path = ROOT / relative
    actual = sha256(path) if path.is_file() else None
    passed = actual == expected["sha256"]
    input_rows.append({"path": relative, "expectedSha256": expected["sha256"], "actualSha256": actual, "passed": passed})
    if not passed:
        issues.append(f"protected_input_changed:{relative}")

opensim_path = ROOT / "OpenSim_Models"
opensim_head = git("-C", str(opensim_path), "rev-parse", "HEAD") if opensim_path.exists() else None
opensim_status = git("-C", str(opensim_path), "status", "--porcelain") if opensim_path.exists() else "missing"
if opensim_head != baseline["OpenSim_Models"].get("head") or opensim_status:
    issues.append("OpenSim_Models_changed")

inventory = json.loads((ROOT / "atlas-data/catalog/whole-body-inventory-t15g.json").read_text(encoding="utf-8"))
denominator = {
    "frozen": inventory.get("denominatorFrozen"),
    "wholeBodyIndividualMuscleCount": inventory.get("wholeBodyIndividualMuscleCount"),
    "coveragePercent": inventory.get("coveragePercent"),
}
if denominator != {"frozen": False, "wholeBodyIndividualMuscleCount": None, "coveragePercent": None}:
    issues.append("T15g_denominator_changed")

report = {
    "task": "T16",
    "checkedAtLocal": datetime.now().astimezone().isoformat(timespec="seconds"),
    "startHead": baseline["head"],
    "preexistingUntrackedCount": len(preexisting_rows),
    "preexistingUntrackedPassed": all(row["passed"] for row in preexisting_rows),
    "preexistingUntracked": preexisting_rows,
    "protectedSnapshots": snapshot_groups,
    "protectedInputCount": len(input_rows),
    "protectedInputsPassed": all(row["passed"] for row in input_rows),
    "protectedInputs": input_rows,
    "OpenSim_Models": {"head": opensim_head, "statusPorcelain": opensim_status, "passed": opensim_head == baseline["OpenSim_Models"].get("head") and not opensim_status},
    "T15gDenominator": denominator,
    "taskOwnedChangedPaths": sorted(TASK_OWNED_INPUTS),
    "browserUserDraftStorage": "not read or written; /review was not opened",
    "issues": issues,
    "pass": not issues,
}
OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: value for key, value in report.items() if key not in {"preexistingUntracked", "protectedSnapshots", "protectedInputs"}}, ensure_ascii=False, indent=2))
raise SystemExit(0 if report["pass"] else 1)
