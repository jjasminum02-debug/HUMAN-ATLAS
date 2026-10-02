#!/usr/bin/env python3
"""Run the focused, reproducible checks owned by T66 serial unit 02."""
from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
UNIT = ROOT / "work/evidence/T66/serial-completion-2026-10-02/unit-02"
NODE = "/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
ENV = dict(os.environ)
ENV["PATH"] = "/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:" + ENV.get("PATH", "")

checks = [
    ("unit02-data-contract", ["python3", "work/evidence/T66/serial-completion-2026-10-02/unit-02/validate_unit02.py"], ROOT),
    ("motion-learning-schema", ["python3", "atlas-data/schemas/validate_motion_learning.py", "--check"], ROOT),
    ("motion-asset-source-policy", ["python3", "atlas-data/schemas/validate_motion_asset_sources.py"], ROOT),
    ("focused-regressions", [NODE, "--experimental-strip-types", "--test", "src/viewer/unit02HipKneeMotion.test.ts", "src/viewer/animationSceneAdapter.test.ts", "src/domain/motionSubjectPresentation.test.ts"], ROOT / "atlas-web"),
    ("typecheck", [NODE, "node_modules/typescript/bin/tsc", "-b", "--pretty", "false"], ROOT / "atlas-web"),
    ("learner-runtime-projection", [NODE, "scripts/buildLearnerMotionRuntime.mjs", "--check"], ROOT / "atlas-web"),
    ("production-build", [NODE, "node_modules/vite/bin/vite.js", "build"], ROOT / "atlas-web"),
    ("execution-projection-sync", ["python3", "work/tools/sync_execution.py"], ROOT),
    ("execution-projection-check", ["python3", "work/tools/sync_execution.py", "--check"], ROOT),
]

results = []
for name, command, cwd in checks:
    started = time.monotonic()
    result = subprocess.run(command, cwd=cwd, env=ENV, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=240)
    duration = round(time.monotonic() - started, 3)
    log_path = UNIT / "verification" / f"{name}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(result.stdout)
    results.append({
        "name": name,
        "command": " ".join(command),
        "cwd": str(cwd.relative_to(ROOT)),
        "exitCode": result.returncode,
        "durationSeconds": duration,
        "logPath": str(log_path.relative_to(ROOT)),
        "outputTail": result.stdout[-2500:],
    })
    print(f"{name}: exit={result.returncode} duration={duration}s log={log_path.relative_to(ROOT)}")
    if result.returncode:
        break

record = {
    "schemaVersion": "t66-unit02-check-run-v1",
    "recordedAtLocal": datetime.now().astimezone().isoformat(timespec="seconds"),
    "checks": results,
    "allPassed": len(results) == len(checks) and all(x["exitCode"] == 0 for x in results),
    "browserEvidencePath": "work/evidence/T66/serial-completion-2026-10-02/unit-02/browser/browser-checks.json",
}
(UNIT / "verification-commands.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
if not record["allPassed"]:
    raise SystemExit(1)
