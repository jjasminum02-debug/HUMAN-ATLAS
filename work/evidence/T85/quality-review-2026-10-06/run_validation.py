#!/usr/bin/env python3
"""Run the T85 motion-context regression set and preserve exact output."""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
WEB = ROOT / "atlas-web"
OUT = Path(__file__).resolve().parent
RUNTIME = Path("/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies")
ENV = dict(os.environ)
ENV["PATH"] = f"{RUNTIME / 'node/bin'}:{RUNTIME / 'bin/fallback'}:{ENV.get('PATH', '')}"

COMMANDS = [
    ["pnpm", "run", "test:whole-body"],
    ["pnpm", "run", "test:motion-learning"],
    ["pnpm", "run", "test:motion-player"],
    ["pnpm", "run", "test:animation-loader"],
    ["pnpm", "run", "typecheck"],
    ["pnpm", "run", "build"],
]

results = []
for index, command in enumerate(COMMANDS, 1):
    started = time.monotonic()
    completed = subprocess.run(command, cwd=WEB, env=ENV, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    seconds = round(time.monotonic() - started, 3)
    log_name = f"check-{index:02d}-{command[2].replace(':', '-')}.log"
    (OUT / log_name).write_text(completed.stdout)
    results.append({
        "command": command,
        "exitCode": completed.returncode,
        "seconds": seconds,
        "log": f"work/evidence/T85/quality-review-2026-10-06/{log_name}",
    })
    if completed.returncode:
        break

summary = {
    "capturedAt": "2026-10-06",
    "passed": len(results) == len(COMMANDS) and all(row["exitCode"] == 0 for row in results),
    "checks": results,
}
(OUT / "validation-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(summary, ensure_ascii=False, indent=2))
raise SystemExit(0 if summary["passed"] else 1)
