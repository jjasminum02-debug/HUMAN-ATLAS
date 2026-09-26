#!/usr/bin/env python3
"""Capture pre-B03 hashes for source assets and earlier T13c work."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "preservation-before.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(args: list[str], cwd: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=True).stdout.strip()


def inventory(paths: set[str]) -> list[dict[str, object]]:
    rows = []
    for rel in sorted(paths):
        path = ROOT / rel
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha(path)})
    return rows


def main() -> None:
    prior = json.loads((ROOT / "work/evidence/T13c-B02/preservation-before.json").read_text(encoding="utf-8"))
    protected_paths = {row["path"] for row in prior["protectedFiles"]}
    protected_paths.update({
        "atlas-data/manifests/assets.json",
        "atlas-data/manifests/derived-assets-t07.json",
        "atlas-data/manifests/mesh-crosswalk-t07.json",
        "atlas-data/schemas/spatial-draft-layer.schema.json",
        "atlas-web/src/viewer/spatialDraftLayer.ts",
        "atlas-web/src/viewer/AnnotationWorkbench.tsx",
        "atlas-web/src/viewer/GLBViewer.tsx",
    })
    prior_task_paths = {
        "work/tasks/T13c-B01.md",
        "work/tasks/T13c-B02.md",
        "work/reports/T13c-B01.md",
        "work/reports/T13c-B02.md",
    }
    for rel_dir in ("work/evidence/T13c-B01", "work/evidence/T13c-B02"):
        prior_task_paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / rel_dir).rglob("*") if p.is_file())
    mutable_context = ["work/STATUS.md", "work/review-queue/attachment-surfaces-t13.md"]
    open_sim = ROOT / "OpenSim_Models"
    result = {
        "capturedAt": date.today().isoformat(),
        "projectHead": git(["rev-parse", "HEAD"]),
        "projectGitStatusBefore": git(["status", "--short", "--untracked-files=all"]),
        "protectedFiles": inventory(protected_paths),
        "priorT13cFiles": inventory(prior_task_paths),
        "mutableContextBefore": inventory(set(mutable_context)),
        "openSimModels": {
            "head": git(["rev-parse", "HEAD"], open_sim),
            "status": git(["status", "--short", "--untracked-files=all"], open_sim),
            "policy": "Read-only; no writes or commands inside OpenSim_Models.",
        },
        "browserDraftBaseline": "To be completed from live /review export before B03 import; do not clear browser storage.",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "protectedFileCount": len(result["protectedFiles"]),
        "priorT13cFileCount": len(result["priorT13cFiles"]),
        "mutableContext": result["mutableContextBefore"],
        "openSimModels": result["openSimModels"],
        "projectGitStatusBefore": result["projectGitStatusBefore"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
