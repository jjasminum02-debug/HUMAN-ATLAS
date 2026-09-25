#!/usr/bin/env python3
"""Rerun both deterministic conversions and the T07 verification, saving logs."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T07"
CONVERTER = ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py"
VERIFIER = EVIDENCE / "validate_t07.py"
SYNTAX_CHECK = EVIDENCE / "check_t07_syntax.py"


def run(label, args):
    command = [sys.executable] + [str(item) for item in args]
    result = subprocess.run(
        command,
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    (EVIDENCE / (label + ".stdout.txt")).write_text(result.stdout, encoding="utf-8")
    (EVIDENCE / (label + ".stderr.txt")).write_text(result.stderr, encoding="utf-8")
    display_command = " ".join(
        "\"{}\"".format(value) if " " in value else value
        for value in ["python3"] + [str(item) for item in args]
    )
    return {
        "label": label,
        "command": display_command,
        "exitCode": result.returncode,
        "stdoutPath": "work/evidence/T07/" + label + ".stdout.txt",
        "stderrPath": "work/evidence/T07/" + label + ".stderr.txt",
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    syntax = run("syntax-check", [SYNTAX_CHECK])
    first = run("conversion-primary", [CONVERTER])
    second = run(
        "conversion-repeat",
        [
            CONVERTER,
            "--output-glb",
            "work/evidence/T07/repeat-run/right-lower-leg.glb",
            "--output-manifest",
            "work/evidence/T07/repeat-run/derived-assets-t07.json",
        ],
    )
    verification = run("verification", [VERIFIER])
    result = {
        "task": "T07",
        "commands": [syntax, first, second, verification],
        "allExitCodesZero": all(row["exitCode"] == 0 for row in (syntax, first, second, verification)),
    }
    (EVIDENCE / "commands.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for row in result["commands"]:
        print("{}: exit {}".format(row["label"], row["exitCode"]))
    if not result["allExitCodesZero"]:
        return 1
    print("Saved work/evidence/T07/commands.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
