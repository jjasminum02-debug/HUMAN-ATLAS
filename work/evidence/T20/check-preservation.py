#!/usr/bin/env python3
"""Compare T20 outputs against its pre-implementation preservation baseline."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "work/evidence/T20/start-baseline.json"


def run(args: list[str]) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
t19_baseline = json.loads((ROOT / "work/evidence/T19/start-baseline.json").read_text(encoding="utf-8"))
failures: list[str] = []
user_results = []
for row in baseline["preexistingUserFiles"]:
    path = ROOT / row["path"]
    actual = sha(path) if path.is_file() else None
    ok = actual == row["sha256"]
    user_results.append({"path": row["path"], "preserved": ok, "expectedSha256": row["sha256"], "actualSha256": actual})
    if not ok:
        failures.append(f"preexisting user snapshot changed or missing: {row['path']}")

protected_results = []
for row in baseline["protectedTrackedInputs"]:
    path = ROOT / row["path"]
    actual = sha(path) if path.is_file() else None
    ok = actual == row["sha256"]
    protected_results.append({"path": row["path"], "preserved": ok, "expectedSha256": row["sha256"], "actualSha256": actual})
    if not ok:
        failures.append(f"protected input changed or missing: {row['path']}")

prior_task_protected_results = []
for row in t19_baseline["protectedFileHashes"]:
    path = ROOT / row["path"]
    actual = sha(path) if path.is_file() else None
    ok = actual == row["sha256"]
    prior_task_protected_results.append({"path": row["path"], "preserved": ok, "expectedSha256": row["sha256"], "actualSha256": actual})
    if not ok:
        failures.append(f"T19 protected source/data/asset changed or missing: {row['path']}")

opensim_head = run(["git", "-C", "OpenSim_Models", "rev-parse", "HEAD"])
opensim_status = run(["git", "-C", "OpenSim_Models", "status", "--short", "--untracked-files=all"])
opensim_ok = opensim_head == baseline["openSim"]["head"] and not opensim_status and baseline["openSim"]["clean"]
if not opensim_ok:
    failures.append("OpenSim_Models HEAD or clean status changed")

committed_t19 = subprocess.check_output(["git", "show", "HEAD:work/reports/T19.md"], cwd=ROOT)
t19_head_hash = hashlib.sha256(committed_t19).hexdigest()
t19_work_hash = sha(ROOT / "work/reports/T19.md")
t19_unchanged = t19_head_hash == t19_work_hash
if not t19_unchanged:
    failures.append("T19 report was modified")

overlay = json.loads((ROOT / "atlas-data/terminology/ai-evidence-overlay.json").read_text(encoding="utf-8"))
denominator_ok = overlay["denominatorFrozen"] is False and overlay["wholeBodyIndividualMuscleCount"] is None and overlay["coveragePercent"] is None
inventory = json.loads((ROOT / "atlas-data/catalog/whole-body-inventory-t15g.json").read_text(encoding="utf-8"))
denominator_ok = denominator_ok and inventory["denominatorFrozen"] is False and inventory["wholeBodyIndividualMuscleCount"] is None and inventory["coveragePercent"] is None
if not denominator_ok:
    failures.append("T15g denominator or coverage was changed")

review = json.loads((ROOT / "work/evidence/T14b/validation-summary.json").read_text(encoding="utf-8"))
review_pending = review.get("taskState") == "needs_human_review"
if not review_pending:
    failures.append("T14b human review state changed")

conflict = next((row for row in overlay["items"] if row["subjectId"] == "HA-M-000005" and row["field"] == "origin"), None)
conflict_preserved = conflict is not None and conflict["evidenceState"] == "conflicted" and len(conflict["claims"]) == 2
if not conflict_preserved:
    failures.append("T18 fibularis-longus origin conflict changed")

result = {
    "pass": not failures,
    "startHead": baseline["startHead"],
    "preexistingUserFileCount": len(user_results),
    "preexistingUserFilesPreserved": all(row["preserved"] for row in user_results),
    "protectedTrackedInputCount": len(protected_results),
    "protectedTrackedInputsPreserved": all(row["preserved"] for row in protected_results),
    "t19ProtectedInputCount": len(prior_task_protected_results),
    "t19ProtectedInputsPreserved": all(row["preserved"] for row in prior_task_protected_results),
    "openSim": {"head": opensim_head, "clean": not opensim_status, "preserved": opensim_ok},
    "t19ReportUnchanged": t19_unchanged,
    "t14bHumanReviewPending": review_pending,
    "t15gDenominatorFalseNullNull": denominator_ok,
    "t18FibularisLongusOriginConflictPreserved": conflict_preserved,
    "failures": failures,
    "userFiles": user_results,
    "protectedInputs": protected_results,
    "t19ProtectedInputs": prior_task_protected_results,
}
out = ROOT / "work/evidence/T20/preservation-after.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k not in ("userFiles", "protectedInputs")}, ensure_ascii=False, indent=2))
raise SystemExit(0 if result["pass"] else 1)
