#!/usr/bin/env python3
"""Compare T13b before/after working-tree and protected-source snapshots."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "work/evidence/T13b"


def read(name: str) -> dict:
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def main() -> int:
    before = read("preservation-before.json")
    after = read("preservation-after.json")
    before_paths = set(before["repoStatusPaths"])
    after_paths = set(after["repoStatusPaths"])
    missing = sorted(before_paths - after_paths)
    hash_differences = {
        path: {"before": before["protectedSha256"].get(path), "after": after["protectedSha256"].get(path)}
        for path in sorted(set(before["protectedSha256"]) | set(after["protectedSha256"]))
        if before["protectedSha256"].get(path) != after["protectedSha256"].get(path)
    }
    opensim_same = before["openSim"] == after["openSim"]
    payload = {
        "task": "T13b",
        "passed": not missing and not hash_differences and opensim_same,
        "preexistingStatusPaths": len(before_paths),
        "preexistingStatusPathsMissingAfter": missing,
        "protectedHashesUnchanged": not hash_differences,
        "protectedHashDifferences": hash_differences,
        "openSimBefore": before["openSim"],
        "openSimAfter": after["openSim"],
        "openSimUnchanged": opensim_same,
        "newOrAdditionalDirtyPaths": sorted(after_paths - before_paths),
    }
    target = OUT / "preservation-comparison.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file": str(target.relative_to(ROOT)), "passed": payload["passed"], "preexistingPathsMissing": len(missing), "protectedHashDifferences": len(hash_differences), "openSimUnchanged": opensim_same}, ensure_ascii=False, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
