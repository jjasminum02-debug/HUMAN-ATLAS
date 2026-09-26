"""Run the required T11-B09 evidence, regression, reference, and preservation checks."""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "work/evidence/T11/B09"
NODE_BIN = "/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin"
ENV = os.environ.copy()
ENV["PATH"] = NODE_BIN + os.pathsep + ENV.get("PATH", "")
COMMANDS = [
    ("coverage_and_field_provenance", ["python3", "work/evidence/T11/B09/validate_t11_b09.py"]),
    ("integrated_search_regression", ["pnpm", "--dir", "atlas-web", "test:search"]),
    ("existing_learning_data_references", ["pnpm", "--dir", "atlas-web", "validate:learning"]),
    ("git_diff_whitespace", ["git", "diff", "--check"]),
    ("pre_existing_and_opensim_preservation", ["python3", "work/evidence/T11/B09/check_preservation.py"]),
]
results = []
logs = []
for name, command in COMMANDS:
    proc = subprocess.run(command, cwd=ROOT, env=ENV, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    results.append({"name": name, "command": command, "exitCode": proc.returncode, "output": proc.stdout})
    logs.append(f"$ {' '.join(command)}\n[exit {proc.returncode}]\n{proc.stdout.rstrip()}\n")
    if proc.returncode:
        break

passed = len(results) == len(COMMANDS) and all(row["exitCode"] == 0 for row in results)
search = next((row for row in results if row["name"] == "integrated_search_regression"), None)
search_count = None
if search and search["exitCode"] == 0:
    match = re.search(r"(?:#|ℹ) tests\s+(\d+)", search["output"])
    if match:
        search_count = int(match.group(1))
report = {
    "pass": passed,
    "taskId": "T11-B09",
    "commands": results,
    "runtime": {"nodeExecutable": str(Path(NODE_BIN) / "node"), "pathPrefix": NODE_BIN},
    "searchTestCount": search_count,
    "scope": "B09 only; learner UI and search implementation unchanged; no T12, build, or deployment",
    "limitations": [
        "TA2 original PDF text layer and Chapter 4 header were directly read; rendered table pages were not visually inspected",
        "KMLE underlying dictionary editions/revisions are not exposed; indexed excerpts and opened aggregate HTML are recorded separately",
        "No part-specific Hanja is attested for these seven records, and P16 full Korean remains missing",
        "One legacy KMLE lateral-triceps row conflicts with the direct TA2 row and is excluded from learner search",
        "Human anatomy review was not performed; terminology evidence is not anatomical approval",
    ],
}
(EVIDENCE / "validation.log").write_text("\n".join(logs) + "\n", encoding="utf-8")
(EVIDENCE / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "pass": passed,
    "checks": [{"name": row["name"], "exitCode": row["exitCode"]} for row in results],
    "searchTestCount": search_count,
    "scope": report["scope"],
}, ensure_ascii=False, indent=2))
if not passed:
    raise SystemExit(1)
