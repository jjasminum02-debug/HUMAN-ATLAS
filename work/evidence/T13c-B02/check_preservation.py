#!/usr/bin/env python3
"""Compare protected inputs, prior B01 deliverables, and OpenSim checkout to B02 baseline."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T13c-B02"


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def git(args: list[str], cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=True).stdout.strip()


def compare(entries: list[dict[str, object]]) -> list[dict[str, object]]:
    result = []
    for entry in entries:
        path = ROOT / str(entry["path"])
        size = path.stat().st_size if path.is_file() else None
        sha = digest(path) if path.is_file() else None
        result.append({
            "path": entry["path"],
            "unchanged": size == entry["bytes"] and sha == entry["sha256"],
            "beforeBytes": entry["bytes"],
            "afterBytes": size,
            "beforeSha256": entry["sha256"],
            "afterSha256": sha,
        })
    return result


def main() -> int:
    before = json.loads((EVIDENCE / "preservation-before.json").read_text(encoding="utf-8"))
    protected = compare(before["protectedFiles"])
    prior_b01 = compare(before["priorEvidenceFiles"])
    opensim_root = ROOT / "OpenSim_Models"
    opensim = {
        "head": git(["rev-parse", "HEAD"], opensim_root),
        "status": git(["status", "--short", "--untracked-files=all"], opensim_root),
    }
    opensim["unchanged"] = opensim["head"] == before["openSimModels"]["head"] and opensim["status"] == before["openSimModels"]["status"]
    passed = all(item["unchanged"] for item in protected + prior_b01) and opensim["unchanged"]
    result = {
        "passed": passed,
        "protectedFileCount": len(protected),
        "protectedFiles": protected,
        "priorB01EvidenceCount": len(prior_b01),
        "priorB01Evidence": prior_b01,
        "openSimModels": {"before": before["openSimModels"], "after": opensim},
    }
    (EVIDENCE / "preservation-after.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "protectedFileCount": len(protected), "priorB01EvidenceCount": len(prior_b01), "openSimModels": opensim}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
