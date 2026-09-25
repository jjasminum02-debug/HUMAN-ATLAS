#!/usr/bin/env python3
"""Compile T07 Python sources in memory without creating bytecode files."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for relative in (
    "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py",
    "work/evidence/T07/validate_t07.py",
    "work/evidence/T07/run_t07_validation.py",
):
    path = ROOT / relative
    compile(path.read_text(encoding="utf-8"), str(path), "exec")
    print("{}: syntax_ok".format(relative))
