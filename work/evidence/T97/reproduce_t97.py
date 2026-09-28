#!/usr/bin/env python3
"""Rerun the bounded T97 inventory, extraction, and surface preview pipeline."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
E = ROOT / "work/evidence/T97"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def output_paths():
    cache = ROOT / "atlas-data/source-cache/z-anatomy/t97"
    paths = [E / "blender-object-inventory.json", E / "latissimus-extraction.json", E / "surface-preview.json"]
    paths.extend(sorted((cache / "latissimus-obj").glob("*.obj")))
    paths.extend(sorted(E.glob("surface-*.png")))
    return paths


def main():
    before = {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name: sha(p) for p in output_paths()}
    commands = [
        [sys.executable, str(E / "parse_blend_datablocks.py"), str(ROOT / "atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend"), "--output", str(E / "blender-object-inventory.json")],
        [sys.executable, str(E / "extract_latissimus_objects.py")],
        [sys.executable, str(E / "render_surface_preview_stdlib.py")],
    ]
    results = []
    for command in commands:
        run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        results.append({"command": [Path(command[0]).name, *[Path(x).name if x.endswith(".py") else x for x in command[1:]]], "exitCode": run.returncode, "stdoutTail": run.stdout[-2000:], "stderrTail": run.stderr[-1000:]})
        if run.returncode:
            raise SystemExit(f"T97 reproduction command failed: {command}; {run.stderr[-1000:]}")
    after = {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name: sha(p) for p in output_paths()}
    if set(before) != set(after) or before != after:
        raise SystemExit("T97 output hashes changed on deterministic rerun")
    data = {
        "task": "T97",
        "result": "reproducible",
        "sourceCodeOnly": True,
        "commands": results,
        "outputSha256Before": before,
        "outputSha256After": after,
        "allOutputHashesIdentical": before == after,
    }
    (E / "reproducibility.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": data["result"], "allOutputHashesIdentical": data["allOutputHashesIdentical"], "fileCount": len(after)}, indent=2))


if __name__ == "__main__":
    main()
