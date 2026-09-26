#!/usr/bin/env python3
"""Compare T17 exit state with its recorded start and protected T16 inputs."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "work/evidence/T17/start-baseline.json"


def run(args: list[str]) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def digest(path: str) -> str | None:
    file_path = ROOT / path
    return hashlib.sha256(file_path.read_bytes()).hexdigest() if file_path.is_file() else None


def main() -> int:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    issues: list[str] = []

    current_untracked = run(["git", "ls-files", "--others", "--exclude-standard"]).splitlines()
    for row in baseline["preexistingUntracked"]:
        if row["path"] not in current_untracked:
            issues.append(f"pre-existing untracked file disappeared: {row['path']}")
        elif digest(row["path"]) != row["sha256"]:
            issues.append(f"pre-existing untracked file changed: {row['path']}")

    protected = []
    for group in baseline["protectedSnapshotsComparedWithT16"]:
        for row in group["files"]:
            actual = digest(row["path"])
            passed = actual == row["sha256"]
            protected.append({"path": row["path"], "expectedSha256": row["sha256"], "actualSha256": actual, "passed": passed})
            if not passed:
                issues.append(f"protected file changed or missing: {row['path']}")

    opensim_head = run(["git", "-C", "OpenSim_Models", "rev-parse", "HEAD"])
    opensim_status = run(["git", "-C", "OpenSim_Models", "status", "--porcelain"])
    if opensim_head != baseline["OpenSim_Models"]["head"] or opensim_status:
        issues.append("OpenSim_Models revision or clean state changed")

    overlay = json.loads((ROOT / "atlas-data/terminology/ai-evidence-overlay.json").read_text(encoding="utf-8"))
    if len(overlay.get("items", [])) != baseline["productionAiEvidenceOverlayItemCount"] or len(overlay.get("items", [])) != 0:
        issues.append("production AI evidence overlay is no longer empty")

    inventory = json.loads((ROOT / "atlas-data/catalog/whole-body-inventory-t15g.json").read_text(encoding="utf-8"))
    denominator = {
        "frozen": inventory.get("denominatorFrozen"),
        "wholeBodyIndividualMuscleCount": inventory.get("wholeBodyIndividualMuscleCount"),
        "coveragePercent": inventory.get("coveragePercent"),
    }
    if denominator != baseline["T15gDenominator"]:
        issues.append("T15g denominator changed")

    tracked_paths = set(run(["git", "diff", "--name-only", "HEAD"]).splitlines())
    allowed_tracked = {
        "work/tasks/T17.md", "work/reports/T17.md", "work/STATUS.md",
        "atlas-data/schemas/source-research-manifest.schema.json",
        "atlas-data/sources/source_research.py", "atlas-data/sources/test_source_research.py",
        "atlas-data/sources/README-T17-source-research.md",
    }
    unexpected_tracked = sorted(path for path in tracked_paths if path not in allowed_tracked and not path.startswith("work/evidence/T17/"))
    if unexpected_tracked:
        issues.append("unexpected tracked changes: " + ", ".join(unexpected_tracked))

    owned_untracked_prefixes = ("work/evidence/T17/",)
    previous_paths = {row["path"] for row in baseline["preexistingUntracked"]}
    unexpected_untracked = sorted(
        path for path in current_untracked
        if path not in previous_paths and not path.startswith(owned_untracked_prefixes)
        and path not in {
            "atlas-data/schemas/source-research-manifest.schema.json",
            "atlas-data/sources/source_research.py", "atlas-data/sources/test_source_research.py",
            "atlas-data/sources/README-T17-source-research.md", "work/reports/T17.md",
        }
    )
    if unexpected_untracked:
        issues.append("unexpected untracked changes: " + ", ".join(unexpected_untracked))

    result = {
        "task": "T17", "startHead": baseline["head"],
        "preexistingUntrackedCount": baseline["preexistingUntrackedCount"],
        "preexistingUntrackedPreserved": not any("pre-existing untracked" in row or "pre-existing untracked file changed" in row for row in issues),
        "protectedInputCount": len(protected), "protectedInputsPassed": all(row["passed"] for row in protected),
        "protectedInputs": protected,
        "OpenSim_Models": {"head": opensim_head, "statusPorcelain": opensim_status, "passed": opensim_head == baseline["OpenSim_Models"]["head"] and not opensim_status},
        "productionAiEvidenceOverlayItemCount": len(overlay.get("items", [])),
        "T15gDenominator": denominator,
        "taskOwnedTrackedPaths": sorted(path for path in tracked_paths if path in allowed_tracked or path.startswith("work/evidence/T17/")),
        "taskOwnedUntrackedPaths": sorted(
            path for path in current_untracked
            if path not in previous_paths and (path.startswith("work/evidence/T17/") or path in {
                "atlas-data/schemas/source-research-manifest.schema.json",
                "atlas-data/sources/source_research.py", "atlas-data/sources/test_source_research.py",
                "atlas-data/sources/README-T17-source-research.md", "work/reports/T17.md",
            })
        ),
        "unexpectedTrackedPaths": unexpected_tracked,
        "unexpectedUntrackedPaths": unexpected_untracked,
        "issues": issues, "pass": not issues,
    }
    output = ROOT / "work/evidence/T17/preservation-after.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in ("protectedInputs",)}, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
