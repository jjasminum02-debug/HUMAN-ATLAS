#!/usr/bin/env python3
"""Compare the T18 working tree with the recorded source/data baseline."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE_PATH = ROOT / "work/evidence/T18/start-baseline.json"
OVERLAY_PATH = ROOT / "atlas-data/terminology/ai-evidence-overlay.json"
OUT_PATH = ROOT / "work/evidence/T18/preservation-after.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
checks: list[dict[str, object]] = []

unchanged_protected: list[str] = []
changed_protected: list[str] = []
for row in baseline["protectedFileHashes"]:
    path = row["path"]
    if path == "atlas-data/terminology/ai-evidence-overlay.json":
        continue  # This is the only production data file T18 was authorized to append.
    current = ROOT / path
    if current.is_file() and sha256(current) == row["sha256"]:
        unchanged_protected.append(path)
    else:
        changed_protected.append(path)
checks.append({
    "name": "protected_files_unchanged_except_authorized_ai_overlay",
    "pass": not changed_protected and len(unchanged_protected) == len(baseline["protectedFileHashes"]) - 1,
    "unchangedCount": len(unchanged_protected),
    "baselineProtectedCount": len(baseline["protectedFileHashes"]),
    "authorizedOverlayExclusion": "atlas-data/terminology/ai-evidence-overlay.json",
    "changedOrMissing": changed_protected,
})

preserved_user_files: list[str] = []
changed_user_files: list[str] = []
for row in baseline["preexistingUntrackedAndModifiedFiles"]:
    path = ROOT / row["path"]
    if path.is_file() and sha256(path) == row["sha256"]:
        preserved_user_files.append(row["path"])
    else:
        changed_user_files.append(row["path"])
checks.append({
    "name": "preexisting_untracked_user_files_preserved",
    "pass": not changed_user_files and len(preserved_user_files) == len(baseline["preexistingUntrackedAndModifiedFiles"]),
    "preservedCount": len(preserved_user_files),
    "baselineCount": len(baseline["preexistingUntrackedAndModifiedFiles"]),
    "changedOrMissing": changed_user_files,
})

opensim = ROOT / "OpenSim_Models"
opensim_head = git("rev-parse", "HEAD", cwd=opensim)
opensim_status = git("status", "--porcelain", cwd=opensim)
checks.append({
    "name": "opensim_models_read_only_and_clean",
    "pass": opensim_head == baseline["openSim"]["head"] and not opensim_status,
    "baselineHead": baseline["openSim"]["head"],
    "currentHead": opensim_head,
    "statusPorcelain": opensim_status,
})

overlay = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
t18_rows = [row for row in overlay["items"] if row.get("id", "").startswith("T18-FIELD-")]
target_subjects = {
    *(f"HA-M-{number:06d}" for number in range(1, 7)),
    "HA-P-000001",
    "HA-P-000002",
}
review_or_promotion = [
    row["id"] for row in t18_rows
    if "humanReviewed" in row or "reviewState" in row
    or row.get("geometryState") != "absent"
    or row.get("motionState") != "absent"
]
pair_set = {(row["subjectId"], row["field"]) for row in t18_rows}
expected_pair_set = {(subject, field) for subject in target_subjects for field in ("origin", "insertion")}
checks.append({
    "name": "ai_overlay_scope_and_independent_readiness_states",
    "pass": (
        len(t18_rows) == 16
        and {row["subjectId"] for row in t18_rows} == target_subjects
        and pair_set == expected_pair_set
        and not review_or_promotion
        and overlay.get("denominatorFrozen") is False
        and overlay.get("wholeBodyIndividualMuscleCount") is None
        and overlay.get("coveragePercent") is None
    ),
    "t18RowCount": len(t18_rows),
    "subjectCount": len({row["subjectId"] for row in t18_rows}),
    "geometryMotionOrHumanReviewPromotion": review_or_promotion,
    "denominatorFrozen": overlay.get("denominatorFrozen"),
    "wholeBodyIndividualMuscleCount": overlay.get("wholeBodyIndividualMuscleCount"),
    "coveragePercent": overlay.get("coveragePercent"),
})

result = {
    "task": "T18",
    "checkedAt": "2026-09-27",
    "startHead": baseline["startHead"],
    "currentHeadBeforeCommit": git("rev-parse", "HEAD"),
    "pass": all(row["pass"] for row in checks),
    "checks": checks,
}
OUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if result["pass"] else 1)
