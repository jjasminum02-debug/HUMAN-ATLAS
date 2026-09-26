#!/usr/bin/env python3
"""Compare protected inputs, prior T13c work, and OpenSim checkout to B03 baseline."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent


def digest(path: Path) -> str | None:
    if not path.is_file():
        return None
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def git(args: list[str], cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=True).stdout.strip()


def compare(entries: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for entry in entries:
        path = ROOT / str(entry["path"])
        current_hash = digest(path)
        size = path.stat().st_size if current_hash is not None else None
        rows.append({"path": entry["path"], "unchanged": size == entry["bytes"] and current_hash == entry["sha256"], "beforeBytes": entry["bytes"], "afterBytes": size, "beforeSha256": entry["sha256"], "afterSha256": current_hash})
    return rows


def main() -> int:
    before = json.loads((EVIDENCE / "preservation-before.json").read_text(encoding="utf-8"))
    protected = compare(before["protectedFiles"])
    prior = compare(before["priorT13cFiles"])
    opensim_root = ROOT / "OpenSim_Models"
    opensim_after = {"head": git(["rev-parse", "HEAD"], opensim_root), "status": git(["status", "--short", "--untracked-files=all"], opensim_root)}
    opensim_after["unchanged"] = opensim_after["head"] == before["openSimModels"]["head"] and opensim_after["status"] == before["openSimModels"]["status"]
    mutable_after = []
    for entry in before["mutableContextBefore"]:
        path = ROOT / entry["path"]
        mutable_after.append({"path": entry["path"], "changedAsAuthorizedContext": digest(path) != entry["sha256"]})
    passed = all(row["unchanged"] for row in protected + prior) and opensim_after["unchanged"]
    result = {
        "passed": passed,
        "protectedFileCount": len(protected),
        "protectedFiles": protected,
        "priorT13cFileCount": len(prior),
        "priorT13cFiles": prior,
        "authorizedMutableContext": mutable_after,
        "openSimModels": {"before": before["openSimModels"], "after": opensim_after},
    }
    (EVIDENCE / "preservation-after.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "protectedFileCount": len(protected), "priorT13cFileCount": len(prior), "authorizedMutableContext": mutable_after, "openSimModels": opensim_after}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
