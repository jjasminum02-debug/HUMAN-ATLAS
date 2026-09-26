#!/usr/bin/env python3
"""Run and retain T13c-B03 schema, spatial, typecheck, and build verification."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
PNPM = "/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm"
NODE_BIN = "/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin"

CHECKS = [
    ("record-validator", [sys.executable, "work/evidence/T13c-B03/validate_record.py"], ROOT),
    ("t03-schema-fixtures", [sys.executable, "atlas-data/schemas/validate.py", "--check-schemas", "--fixtures"], ROOT),
    ("spatial-draft-tests", [PNPM, "run", "test:spatial-drafts"], ROOT / "atlas-web"),
    ("typecheck", [PNPM, "run", "typecheck"], ROOT / "atlas-web"),
    ("build", [PNPM, "run", "build"], ROOT / "atlas-web"),
]


def main() -> int:
    env = os.environ.copy()
    env["PATH"] = NODE_BIN + os.pathsep + env.get("PATH", "")
    results = []
    for name, command, cwd in CHECKS:
        completed = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
        output = completed.stdout + ("\n[stderr]\n" + completed.stderr if completed.stderr else "")
        (EVIDENCE / f"{name}.log").write_text(output, encoding="utf-8")
        results.append({"name": name, "command": command, "cwd": cwd.relative_to(ROOT).as_posix(), "exitCode": completed.returncode, "passed": completed.returncode == 0, "log": f"work/evidence/T13c-B03/{name}.log"})
        print(f"{name}: {'PASS' if completed.returncode == 0 else 'FAIL'} (exit {completed.returncode})")
        if completed.returncode != 0:
            print(output[-5000:])
    summary = {"passed": all(row["passed"] for row in results), "checks": results}
    (EVIDENCE / "validation-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
