#!/usr/bin/env python3
"""Run the final T66 integration checks and retain concise command evidence."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
WEB = ROOT / "atlas-web"
NODE = "/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
PYTHON = "python3"

checks = [
    ("motion-and-wave1-regression", WEB, [NODE, "--experimental-strip-types", "--test",
        "src/domain/motionLearning.test.ts", "src/domain/legacyJointActionAdapter.test.ts",
        "src/domain/t66Wave1Motion.test.ts", "src/viewer/animationSceneAdapter.test.ts",
        "src/data/learning.test.ts", "src/viewer/animationPlayback.test.ts"]),
    ("learner-card-runtime-check", WEB, [NODE, "scripts/buildLearnerCardRuntime.mjs", "--check"]),
    ("learner-motion-runtime-check", WEB, [NODE, "scripts/buildLearnerMotionRuntime.mjs", "--check"]),
    ("learner-content-validation", WEB, [PYTHON, "scripts/validate-learning-content.py"]),
    ("ai-evidence-contract", ROOT, [PYTHON, "atlas-data/schemas/validate_ai_evidence.py", "--check"]),
    ("bone-name-overlay-contract", ROOT, [PYTHON, "atlas-data/schemas/validate_bone_name_overlay.py", "--check"]),
    ("motion-learning-contract", ROOT, [PYTHON, "atlas-data/schemas/validate_motion_learning.py", "--check"]),
    ("motion-asset-source-contract", ROOT, [PYTHON, "atlas-data/schemas/validate_motion_asset_sources.py"]),
    ("function-content-contract", ROOT, [PYTHON, "work/tools/validate_t83_function_content.py", "--validate-only"]),
    ("scene-decoder-contract", WEB, [NODE, "scripts/check-scene-decoders.mjs"]),
    ("typescript-project-check", WEB, [NODE, "node_modules/typescript/bin/tsc", "-b", "--pretty", "false"]),
    ("production-vite-build", WEB, [NODE, "node_modules/vite/bin/vite.js", "build"]),
    ("learner-bundle-distribution-audit", WEB, [NODE, "scripts/auditLearnerCardDistribution.mjs", "--check"]),
]

env = os.environ.copy()
env["PATH"] = "/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:" + env.get("PATH", "")
results = []
for name, cwd, command in checks:
    proc = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
    results.append({
        "name": name,
        "cwd": str(cwd.relative_to(ROOT)),
        "command": command,
        "exitCode": proc.returncode,
        "passed": proc.returncode == 0,
        "stdoutTail": proc.stdout[-5000:],
        "stderrTail": proc.stderr[-3000:],
    })
    print(f"{name}: {'PASS' if proc.returncode == 0 else 'FAIL'} (exit {proc.returncode})")
    if proc.returncode:
        break

output = {
    "schemaVersion": "t66-final-validation-v1",
    "recordedAtUtc": datetime.now(timezone.utc).isoformat(),
    "checks": results,
    "allPassed": len(results) == len(checks) and all(row["passed"] for row in results),
    "notes": [
        "Vite may emit its existing large-chunk advisory; this is recorded separately from build success.",
        "No GPU/VRAM or total process-memory observation is inferred from these checks.",
        "Desktop viewport emulation is not a physical mobile-device test.",
    ],
}
(HERE / "final-validation.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
raise SystemExit(0 if output["allPassed"] else 1)
