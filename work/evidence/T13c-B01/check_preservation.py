#!/usr/bin/env python3
"""Compare protected project inputs and OpenSim_Models against the T13c-B01 baseline."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T13c-B01"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git(args: list[str], cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=True).stdout.strip()


def main() -> int:
    before = json.loads((EVIDENCE / "preservation-before.json").read_text(encoding="utf-8"))
    after_files = []
    for entry in before["protectedFiles"]:
        path = ROOT / entry["path"]
        after_files.append({"path": entry["path"], "bytes": path.stat().st_size if path.exists() else None, "sha256": digest(path) if path.exists() else None})
    file_results = []
    for old, new in zip(before["protectedFiles"], after_files):
        file_results.append({"path": old["path"], "unchanged": old["bytes"] == new["bytes"] and old["sha256"] == new["sha256"], "beforeSha256": old["sha256"], "afterSha256": new["sha256"]})
    opensim = ROOT / "OpenSim_Models"
    opensim_after = {"head": git(["rev-parse", "HEAD"], opensim), "status": git(["status", "--short", "--untracked-files=all"], opensim)}
    opensim_after["unchanged"] = opensim_after["head"] == before["openSimModels"]["head"] and opensim_after["status"] == before["openSimModels"]["status"]
    result = {"passed": all(row["unchanged"] for row in file_results) and opensim_after["unchanged"], "protectedFileCount": len(file_results), "protectedFiles": file_results, "openSimModels": {"before": before["openSimModels"], "after": opensim_after}}
    out = EVIDENCE / "preservation-after.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "protectedFileCount": result["protectedFileCount"], "openSimModels": opensim_after}, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
