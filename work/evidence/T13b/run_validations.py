#!/usr/bin/env python3
"""Run and retain T13b engineering and T03 contract verification outputs."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WEB = ROOT / "atlas-web"
NODE = Path("/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node")
PNPM = Path("/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/pnpm/bin/pnpm.mjs")
PATH = f"{NODE.parent}:/usr/bin:/bin"


def main() -> int:
    commands = [
        ("typecheck", [str(NODE), str(PNPM), "typecheck"], WEB),
        ("spatial_draft_tests_and_schema", [str(NODE), str(PNPM), "test:spatial-drafts"], WEB),
        ("annotation_regression_and_schema", [str(NODE), str(PNPM), "test:annotations"], WEB),
        ("integrated_search_regression", [str(NODE), str(PNPM), "test:search"], WEB),
        ("production_build_and_learning_content", [str(NODE), str(PNPM), "build"], WEB),
        ("t03_schema_keyword_check", ["python3", "atlas-data/schemas/validate.py", "--check-schemas"], ROOT),
        ("t03_17_fixture_suite", ["python3", "atlas-data/schemas/validate.py", "--fixtures"], ROOT),
    ]
    env = {**os.environ, "PATH": PATH}
    results = []
    for name, argv, cwd in commands:
        result = subprocess.run(argv, cwd=cwd, env=env, text=True, capture_output=True, check=False)
        results.append({
            "name": name,
            "command": argv,
            "cwd": str(cwd.relative_to(ROOT)),
            "exitCode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        })
    payload = {
        "task": "T13b",
        "capturedAtUtc": datetime.now(timezone.utc).isoformat(),
        "passed": all(row["exitCode"] == 0 for row in results),
        "results": results,
    }
    target = ROOT / "work/evidence/T13b/commands.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file": str(target.relative_to(ROOT)), "passed": payload["passed"], "results": [{"name": row["name"], "exitCode": row["exitCode"]} for row in results]}, ensure_ascii=False, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
