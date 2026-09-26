"""Run and persist the explicit T11-B02 validation commands."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "work/evidence/T11/B02"
ENV = os.environ.copy()
ENV["PATH"] = ":".join([
    "/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin",
    "/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback",
    "/usr/bin", "/bin", ENV.get("PATH", ""),
])
COMMANDS = [
    ["python3", "work/evidence/T11/B02/validate_t11_b02.py"],
    ["pnpm", "--dir", "atlas-web", "test:search"],
    ["pnpm", "--dir", "atlas-web", "validate:learning"],
    ["pnpm", "--dir", "atlas-web", "typecheck"],
    ["git", "diff", "--check"],
    ["python3", "work/evidence/T11/B02/check_preservation.py"],
    ["python3", "work/evidence/T11/B02/validate_artifacts.py"],
]
outputs = []
for command in COMMANDS:
    result = subprocess.run(command, cwd=ROOT, env=ENV, text=True, capture_output=True, check=False)
    outputs.append({
        "command": command,
        "exitCode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    })
log = "\n".join(
    f"$ {' '.join(row['command'])}\nexit={row['exitCode']}\n{row['stdout']}{row['stderr']}".rstrip()
    for row in outputs
) + "\n"
(EVIDENCE / "validation.log").write_text(log, encoding="utf-8")
(EVIDENCE / "validation.json").write_text(json.dumps({
    "capturedAt": "2026-09-25",
    "batchId": "T11-B02",
    "commands": outputs,
    "allPassed": all(row["exitCode"] == 0 for row in outputs),
    "productionBuildRun": False,
    "reasonBuildNotRun": "No learner UI or build configuration changed; avoid rewriting pre-existing generated bundles.",
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"allPassed": all(row["exitCode"] == 0 for row in outputs), "results": [{"command": row["command"], "exitCode": row["exitCode"]} for row in outputs]}, ensure_ascii=False, indent=2))
if any(row["exitCode"] != 0 for row in outputs):
    raise SystemExit(1)
