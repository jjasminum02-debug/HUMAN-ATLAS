#!/usr/bin/env python3
"""Final JSON and whitespace check for T11-owned artifacts and touched code."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
json_files = [
    "atlas-data/terminology/learning-names.json",
    "atlas-data/terminology/term-review-batches.json",
    "work/evidence/T11/preservation-before.json",
    "work/evidence/T11/validation.json",
    "work/evidence/T11/commands.json",
    "work/evidence/T11/preservation-after.json",
]
text_files = [
    "atlas-data/terminology/learning-names.json",
    "atlas-data/terminology/term-review-batches.json",
    "work/evidence/T11/preservation-before.json",
    "work/evidence/T11/validation.json",
    "work/evidence/T11/commands.json",
    "work/evidence/T11/preservation-after.json",
    "work/evidence/T11/build_t11_b01.py",
    "work/evidence/T11/validate_t11_b01.py",
    "work/evidence/T11/check_t11_preservation.py",
    "work/tasks/T11-B01.md",
    "work/review-queue/terminology-gaps.md",
    "work/reports/T11-B01.md",
    "work/reports/T11.md",
    "work/STATUS.md",
    "atlas-web/src/domain/search.ts",
    "atlas-web/src/domain/search.test.ts",
    "atlas-web/src/data/learning.ts",
]
for rel in json_files:
    json.loads((ROOT / rel).read_text())
violations = []
for rel in text_files:
    path = ROOT / rel
    content = path.read_text()
    if not content.endswith("\n"):
        violations.append(f"{rel}: missing final newline")
    for index, line in enumerate(content.splitlines(), 1):
        if line.rstrip() != line:
            violations.append(f"{rel}:{index}: trailing whitespace")
assert not violations, "\n".join(violations)
print(json.dumps({
    "pass": True,
    "jsonFilesParsed": len(json_files),
    "textFilesChecked": len(text_files),
    "trailingWhitespace": 0,
    "finalNewlinesPresent": True,
}, ensure_ascii=False))
