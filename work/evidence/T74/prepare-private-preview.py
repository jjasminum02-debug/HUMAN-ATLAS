#!/usr/bin/env python3
"""Prepare a strict allowlisted local host for actual T74 browser renders."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T74"
HOST = EVIDENCE / "private-preview-host"
CONVERTED = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted"
ASSETS = {
    "T52-B09.glb": CONVERTED / "t52/T52-B09.glb",
    "T72-first-pass-residual-static-source.glb": CONVERTED / "t72/T72-first-pass-residual-static-source.glb",
    "T74-bilateral-skull-static-source.glb": CONVERTED / "t74/T74-bilateral-skull-static-source.glb",
}
VENDOR = {
    "three/build/three.module.js": ROOT / "atlas-web/node_modules/three/build/three.module.js",
    "three/build/three.core.js": ROOT / "atlas-web/node_modules/three/build/three.core.js",
    "three/examples/jsm/loaders/GLTFLoader.js": ROOT / "atlas-web/node_modules/three/examples/jsm/loaders/GLTFLoader.js",
    "three/examples/jsm/utils/BufferGeometryUtils.js": ROOT / "atlas-web/node_modules/three/examples/jsm/utils/BufferGeometryUtils.js",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare() -> None:
    if HOST.exists():
        raise RuntimeError(f"refusing to overwrite an existing preview host: {HOST}")
    for path in [*ASSETS.values(), *VENDOR.values()]:
        if not path.is_file():
            raise RuntimeError(f"allowlisted preview input missing: {path}")
    HOST.mkdir(parents=True)
    try:
        shutil.copyfile(EVIDENCE / "private-preview.html", HOST / "index.html")
        shutil.copyfile(EVIDENCE / "private-preview.mjs", HOST / "private-preview.mjs")
        (HOST / "assets").mkdir()
        (HOST / "vendor/three/build").mkdir(parents=True)
        (HOST / "vendor/three/examples/jsm/loaders").mkdir(parents=True)
        (HOST / "vendor/three/examples/jsm/utils").mkdir(parents=True)
        records = []
        for name, source in ASSETS.items():
            target = HOST / "assets" / name
            os.link(source, target)
            records.append({"path": target.relative_to(HOST).as_posix(), "sourcePath": source.relative_to(ROOT).as_posix(), "sha256": digest(source), "bytes": source.stat().st_size, "materialization": "read-only hardlink"})
        for relative, source in VENDOR.items():
            target = HOST / "vendor" / relative
            os.link(source, target)
            records.append({"path": target.relative_to(HOST).as_posix(), "sourcePath": source.relative_to(ROOT).as_posix(), "sha256": digest(source), "bytes": source.stat().st_size, "materialization": "read-only hardlink"})
        for target_name, source_name in [("index.html", "private-preview.html"), ("private-preview.mjs", "private-preview.mjs")]:
            target = HOST / target_name
            records.append({"path": target_name, "sourcePath": (EVIDENCE / source_name).relative_to(ROOT).as_posix(), "sha256": digest(target), "bytes": target.stat().st_size, "materialization": "task-owned preview copy"})
        document = {"task": "T74", "scope": "allowlisted temporary QA files only; project root and OpenSim not served", "serverRoot": HOST.relative_to(ROOT).as_posix(), "files": records, "fileCount": len(records), "openSimExposed": False, "privateDataExposed": False}
        (EVIDENCE / "preview-inputs.json").write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(document, ensure_ascii=False, indent=2))
    except Exception:
        shutil.rmtree(HOST, ignore_errors=True)
        raise


def clean() -> None:
    if not HOST.exists():
        print("preview host already absent")
        return
    manifest = json.loads((EVIDENCE / "preview-inputs.json").read_text(encoding="utf-8"))
    actual = {path.relative_to(HOST).as_posix() for path in HOST.rglob("*") if path.is_file()}
    expected = {row["path"] for row in manifest["files"]}
    if actual != expected:
        raise RuntimeError("unexpected file in preview host; refusing to delete")
    shutil.rmtree(HOST)
    print(json.dumps({"cleanedOnlyAllowlistedPreviewHost": True, "removedFileCount": len(actual), "sourceFilesUnlinkedOnly": True}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    try:
        prepare() if args.prepare else clean()
    except Exception as exc:
        print(f"T74 preview preparation failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
