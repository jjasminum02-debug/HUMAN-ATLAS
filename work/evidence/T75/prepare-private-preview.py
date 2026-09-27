#!/usr/bin/env python3
"""Create/clean a strict local-only browser QA allowlist for T75."""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HOST = Path(__file__).resolve().parent / "private-preview-host"
ALLOWLIST = {
    "index.html": ROOT / "work/evidence/T75/private-preview.html",
    "private-preview.mjs": ROOT / "work/evidence/T75/private-preview.mjs",
    "assets/T53-trunk-pelvis-static-source.glb": ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t53/T53-trunk-pelvis-static-source.glb",
    "assets/T54-shoulder-upper-limb-static-source.glb": ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t54/T54-shoulder-upper-limb-static-source.glb",
    "assets/T75-deltoid-bilateral-static-source.glb": ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t75/T75-deltoid-bilateral-static-source.glb",
    "vendor/three/build/three.module.js": ROOT / "atlas-web/node_modules/three/build/three.module.js",
    "vendor/three/build/three.core.js": ROOT / "atlas-web/node_modules/three/build/three.core.js",
    "vendor/three/examples/jsm/loaders/GLTFLoader.js": ROOT / "atlas-web/node_modules/three/examples/jsm/loaders/GLTFLoader.js",
    "vendor/three/examples/jsm/utils/BufferGeometryUtils.js": ROOT / "atlas-web/node_modules/three/examples/jsm/utils/BufferGeometryUtils.js",
    "vendor/three/examples/jsm/utils/SkeletonUtils.js": ROOT / "atlas-web/node_modules/three/examples/jsm/utils/SkeletonUtils.js",
}


def prepare() -> dict:
    if HOST.exists():
        raise RuntimeError(f"refusing to replace existing browser host: {HOST}")
    for relative, source in ALLOWLIST.items():
        if not source.is_file():
            raise RuntimeError(f"allowlisted input missing: {source}")
        destination = HOST / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.link(source, destination)
    actual = {p.relative_to(HOST).as_posix() for p in HOST.rglob("*") if p.is_file()}
    if actual != set(ALLOWLIST):
        raise RuntimeError(f"private host differs from exact allowlist: {sorted(actual ^ set(ALLOWLIST))}")
    rows = []
    for relative in sorted(ALLOWLIST):
        path = HOST / relative
        rows.append({"path": relative, "bytes": path.stat().st_size})
    return {"result": "pass", "relativeHostPath": HOST.relative_to(ROOT).as_posix(), "files": rows, "repoRootExposed": False, "sourceCacheExposed": False, "onlyExactAllowlist": True}


def cleanup() -> dict:
    if not HOST.exists():
        return {"result": "already_clean", "relativeHostPath": HOST.relative_to(ROOT).as_posix()}
    actual = {p.relative_to(HOST).as_posix() for p in HOST.rglob("*") if p.is_file()}
    if actual != set(ALLOWLIST):
        raise RuntimeError(f"refusing cleanup because host file set changed: {sorted(actual ^ set(ALLOWLIST))}")
    for relative in sorted(ALLOWLIST, reverse=True):
        (HOST / relative).unlink()
    for path in sorted((p for p in HOST.rglob("*") if p.is_dir()), reverse=True):
        path.rmdir()
    HOST.rmdir()
    return {"result": "pass", "relativeHostPath": HOST.relative_to(ROOT).as_posix(), "removedOnlyAllowlistLinks": True, "sourceInodesUntouched": True, "hostRemoved": not HOST.exists()}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()
    print(json.dumps(prepare() if args.prepare else cleanup(), ensure_ascii=False, indent=2))
