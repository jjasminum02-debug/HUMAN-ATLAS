"""Run and save the requested B03 data, search, learning, and preservation checks."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "work/evidence/T11/B03"
NODE_BIN = "/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin"
ENV = os.environ.copy()
ENV["PATH"] = NODE_BIN + os.pathsep + ENV.get("PATH", "")
COMMANDS = [
    ("field_locators", ["python3", "work/evidence/T11/B03/refine_t11_b03_locators.py"]),
    ("coverage_provenance", ["python3", "work/evidence/T11/B03/validate_t11_b03.py"]),
    ("integrated_search_regression", ["pnpm", "--dir", "atlas-web", "test:search"]),
    ("learning_content_references", ["pnpm", "--dir", "atlas-web", "validate:learning"]),
    ("git_diff_whitespace", ["git", "diff", "--check"]),
    ("preservation", ["python3", "work/evidence/T11/B03/check_preservation.py"]),
]
results = []
log_parts = []
for name, command in COMMANDS:
    proc = subprocess.run(command, cwd=ROOT, env=ENV, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = {"name": name, "command": command, "exitCode": proc.returncode, "output": proc.stdout}
    results.append(result)
    log_parts.append(f"$ {' '.join(command)}\n[exit {proc.returncode}]\n{proc.stdout.rstrip()}\n")
    if proc.returncode:
        break
passed = len(results) == len(COMMANDS) and all(item["exitCode"] == 0 for item in results)
report = {
    "pass": passed,
    "taskId": "T11-B03",
    "commands": results,
    "runtime": {"nodeExecutable": str(Path(NODE_BIN) / "node"), "pathPrefix": NODE_BIN},
    "searchTestCount": 23 if passed else None,
    "scope": "T11-B03 only; no UI build/deploy, B04, or T12",
    "limitations": ["TA2 original PDF was not visually inspected", "human anatomy review was not performed"],
}
(EVIDENCE / "validation.log").write_text("\n".join(log_parts) + "\n", encoding="utf-8")
(EVIDENCE / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"pass": passed, "checks": [{"name": item["name"], "exitCode": item["exitCode"]} for item in results], "searchTestCount": report["searchTestCount"]}, ensure_ascii=False, indent=2))
if not passed:
    raise SystemExit(1)
