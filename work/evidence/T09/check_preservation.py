#!/usr/bin/env python3
"""Compare T09's pre-implementation file inventory and read-only OpenSim checkout."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "work/evidence/T09/preservation-before.json"
OUTPUT = ROOT / "work/evidence/T09/preservation-after.json"
INTENTIONAL = {
    "atlas-web/package.json",
    "atlas-web/src/ui/App.tsx",
    "atlas-web/src/ui/styles.css",
    "atlas-web/src/viewer/GLBViewer.tsx",
    "atlas-web/src/viewer/glb.ts",
    "atlas-web/src/viewer/manifest.ts",
    "work/DECISIONS.md",
    "work/STATUS.md",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def main() -> int:
    before = json.loads(BASELINE.read_text(encoding="utf-8"))
    unchanged: list[str] = []
    intentional_changes: list[str] = []
    unexpected_changes: list[str] = []
    missing: list[str] = []
    for relative, expected in before["files"].items():
        path = ROOT / relative
        if not path.is_file():
            missing.append(relative)
            continue
        if sha256(path) == expected:
            unchanged.append(relative)
        elif relative in INTENTIONAL:
            intentional_changes.append(relative)
        else:
            unexpected_changes.append(relative)

    open_sim = ROOT / "OpenSim_Models"
    open_sim_head = git(open_sim, "rev-parse", "HEAD")
    open_sim_status = git(open_sim, "status", "--porcelain")
    root_head = git(ROOT, "rev-parse", "HEAD")
    root_status = git(ROOT, "status", "--porcelain")
    preserved_user_paths = []
    for relative in ("README.md", "AGENTS.md", "design/2026-09-25-muscle-atlas"):
        path = ROOT / relative
        if path.is_file():
            preserved_user_paths.append(relative)
        elif path.is_dir():
            preserved_user_paths.append(relative)
    result = {
        "task": "T09",
        "baselineRootHead": before["rootGitHead"],
        "rootHeadAtCheck": root_head,
        "openSimBaselineHead": before["openSimHead"],
        "openSimHeadAtCheck": open_sim_head,
        "openSimWorkingTreeClean": not open_sim_status,
        "rootStatusAtCheck": root_status.splitlines(),
        "baselineFileCount": len(before["files"]),
        "unchangedBaselineFileCount": len(unchanged),
        "intentionalChangedPaths": sorted(intentional_changes),
        "unexpectedChangedPaths": sorted(unexpected_changes),
        "missingPaths": sorted(missing),
        "preexistingUserPathsPresent": preserved_user_paths,
        "passed": (
            open_sim_head == before["openSimHead"]
            and not open_sim_status
            and not unexpected_changes
            and not missing
            and all(path in preserved_user_paths for path in ("README.md", "AGENTS.md", "design/2026-09-25-muscle-atlas"))
        ),
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
