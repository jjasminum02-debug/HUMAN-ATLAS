#!/usr/bin/env python3
"""Capture HUMAN ATLAS and immutable OpenSim preservation evidence."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "work/evidence/T13b"
PROTECTED = [
    "atlas-data/catalog/canonical-catalog.json",
    "atlas-data/manifests/canonical-geometry-t12.json",
    "atlas-data/manifests/attachment-context-t13.json",
    "atlas-data/manifests/derived-assets-t07.json",
    "atlas-data/manifests/derived-bones-t13.json",
    "atlas-data/schemas/annotation-draft-exchange.schema.json",
    "atlas-data/assets/derived-glb/bodyparts3d-r4-right-lower-leg/right-lower-leg.glb",
    "atlas-data/assets/derived-glb/bodyparts3d-r4-t13-right-bones/right-bones.glb",
]


def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def status_paths(repo: Path) -> list[str]:
    raw = subprocess.check_output(
        ["git", "-C", str(repo), "status", "--porcelain=v1", "-z", "--untracked-files=all"]
    )
    entries = []
    for item in raw.decode("utf-8", "surrogateescape").split("\0"):
        if not item:
            continue
        entries.append(item[3:])
    return sorted(entries)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "before"
    if mode not in {"before", "after"}:
        raise SystemExit("usage: capture_preservation.py before|after")
    repo_status = status_paths(ROOT)
    opensim = ROOT / "OpenSim_Models"
    opensim_head = run("git", "-C", str(opensim), "rev-parse", "HEAD")
    opensim_status = status_paths(opensim)
    protected = {rel: sha(ROOT / rel) for rel in PROTECTED}
    payload = {
        "mode": mode,
        "repoRoot": str(ROOT),
        "repoStatusPaths": repo_status,
        "repoStatusPathCount": len(repo_status),
        "protectedSha256": protected,
        "openSim": {"head": opensim_head, "statusPaths": opensim_status},
    }
    path = OUT / f"preservation-{mode}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file": str(path.relative_to(ROOT)), **payload}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
