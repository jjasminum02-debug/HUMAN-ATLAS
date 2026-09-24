#!/usr/bin/env python3
"""Compare pre-task user-file and OpenSim evidence with the current checkout."""
from __future__ import annotations
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
WORKSPACE = PROJECT.parent
BASELINE = HERE / "preexisting-files-before.sha256"
OPEN_SIM_BASELINE = HERE / "opensim-before.txt"


def run_git(path: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    expected = {}
    for line in BASELINE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, relative = line.split("  ", 1)
            expected[relative] = digest
    file_results = []
    for relative, expected_hash in expected.items():
        path = WORKSPACE / relative
        actual = sha256(path) if path.is_file() else None
        file_results.append({"path": relative, "expectedSha256": expected_hash, "actualSha256": actual, "unchanged": actual == expected_hash})

    baseline_text = OPEN_SIM_BASELINE.read_text(encoding="utf-8").splitlines()
    expected_head = next(line.split("=", 1)[1] for line in baseline_text if line.startswith("head="))
    expected_model_hash = next(line.split("=", 1)[1] for line in baseline_text if line.startswith("Rajagopal2016.osim_sha256="))
    opensim = PROJECT / "OpenSim_Models"
    actual_head = run_git(opensim, "rev-parse", "HEAD")
    opensim_status = run_git(opensim, "status", "--porcelain")
    actual_model_hash = sha256(opensim / "Models/Rajagopal/Rajagopal2016.osim")
    project_status = run_git(PROJECT, "status", "--short", "--branch")
    preserved_untracked = "?? README.md" in project_status.splitlines() and "?? design/" in project_status.splitlines()
    result = {
        "existingUserAndDesignFiles": {"count": len(file_results), "unchanged": all(row["unchanged"] for row in file_results), "files": file_results},
        "opensim": {"headBefore": expected_head, "headNow": actual_head, "headUnchanged": actual_head == expected_head, "statusPorcelain": opensim_status, "clean": not opensim_status, "rajagopalHashBefore": expected_model_hash, "rajagopalHashNow": actual_model_hash, "sampleModelUnchanged": actual_model_hash == expected_model_hash},
        "projectPreexistingUntracked": {"readmeAndDesignRemainUntracked": preserved_untracked},
        "passed": all(row["unchanged"] for row in file_results) and actual_head == expected_head and not opensim_status and actual_model_hash == expected_model_hash and preserved_untracked
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
