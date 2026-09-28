#!/usr/bin/env python3
"""Check that T101 left baseline inputs, prior WIP, OpenSim, and old cache alone."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "work/evidence/T101/start-baseline.json"
OUT = ROOT / "work/evidence/T101/preservation.json"
MUTABLE_SHARED = {"work/STATUS.md", "work/task-registry-r15.json"}
T101_CACHE = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t101"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(cwd: Path, *args: str) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def main() -> int:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    unchanged = []
    changed = []
    for rel, expected in baseline["inputFiles"].items():
        if rel in MUTABLE_SHARED:
            continue
        path = ROOT / rel
        actual = {"exists": path.is_file(), "bytes": path.stat().st_size if path.is_file() else None,
                  "sha256": sha(path) if path.is_file() else None}
        (unchanged if actual == {"exists": expected["exists"], "bytes": expected["bytes"], "sha256": expected["sha256"]} else changed).append(rel)
    status_lines = subprocess.check_output(["git", "status", "--short", "--untracked-files=all"], cwd=ROOT, text=True).splitlines()
    current_paths = {line[3:] for line in status_lines if len(line) >= 4}
    baseline_paths = set(baseline["preexistingStatusPaths"])
    missing_wip_paths = sorted(baseline_paths - current_paths)
    opensim = ROOT / "OpenSim_Models"
    opensim_head = run(opensim, "git", "rev-parse", "HEAD")
    opensim_status = run(opensim, "git", "status", "--porcelain")
    source_files = sorted(p.relative_to(ROOT).as_posix() for p in T101_CACHE.rglob("*.obj")) if T101_CACHE.exists() else []
    expected_files = sorted(f"atlas-data/source-cache/bodyparts3d-r4/mesh/t101/{owner}/{fid}.obj"
                            for fid, owner in [("FJ1393", "foot"), ("FJ1393M", "foot"), ("FJ1394M", "leg"),
                                               ("FJ1395", "thigh"), ("FJ1395M", "thigh"), ("FJ1396", "foot"),
                                               ("FJ1396M", "foot"), ("FJ1397M", "leg"), ("FJ1398", "foot"), ("FJ1398M", "foot")])
    result = {
        "task": "T101",
        "baselineHead": baseline["head"],
        "baselineIndexEmpty": baseline["indexEmpty"],
        "baselinePreexistingStatusEntries": baseline["preexistingStatusEntries"],
        "preexistingPathNamesStillPresent": len(missing_wip_paths) == 0,
        "missingPreexistingPaths": missing_wip_paths,
        "baselineInputsUnchanged": len(changed) == 0,
        "unchangedInputCount": len(unchanged),
        "changedProtectedInputs": changed,
        "sharedMutableInputsExcludedFromContentComparison": sorted(MUTABLE_SHARED),
        "OpenSim_Models": {"baselineHead": baseline["opensimHead"], "currentHead": opensim_head,
                            "baselineStatus": baseline["opensimStatusPorcelain"], "currentStatus": opensim_status,
                            "unchangedAndClean": opensim_head == baseline["opensimHead"] and opensim_status == ""},
        "priorT13Drafts": {"changedPaths": [p for p in sorted(current_paths - baseline_paths) if p.startswith("work/evidence/T13") or p.startswith("atlas-data/spatial")],
                           "untouched": not any(p.startswith("work/evidence/T13") or p.startswith("atlas-data/spatial") for p in current_paths - baseline_paths)},
        "T101IgnoredRawCache": {"count": len(source_files), "paths": source_files, "exactExpectedSet": source_files == expected_files},
    }
    result["result"] = "pass" if (result["preexistingPathNamesStillPresent"] and result["baselineInputsUnchanged"]
                                     and result["OpenSim_Models"]["unchangedAndClean"] and result["priorT13Drafts"]["untouched"]
                                     and result["T101IgnoredRawCache"]["exactExpectedSet"]) else "fail"
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
