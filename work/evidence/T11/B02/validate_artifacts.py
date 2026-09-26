"""Check B02 JSON syntax and task-owned text whitespace/final-newline integrity."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
JSON_FILES = [
    "atlas-data/terminology/learning-names.json",
    "atlas-data/terminology/term-review-batches.json",
    "work/evidence/T11/B02/preservation-before.json",
    "work/evidence/T11/B02/validation.json",
    "work/evidence/T11/B02/preservation-after.json",
]
TEXT_FILES = [
    *JSON_FILES,
    "work/tasks/T11-B02.md",
    "work/reports/T11-B02.md",
    "work/reports/T11.md",
    "work/review-queue/terminology-gaps.md",
    "work/STATUS.md",
    "work/evidence/T11/B02/build_t11_b02.py",
    "work/evidence/T11/B02/validate_t11_b02.py",
    "work/evidence/T11/B02/run_validations.py",
    "work/evidence/T11/B02/check_preservation.py",
    "work/evidence/T11/B02/web-source-log.md",
    "atlas-web/src/domain/search.test.ts",
]
for rel in JSON_FILES:
    json.loads((ROOT / rel).read_text(encoding="utf-8"))
violations = []
for rel in TEXT_FILES:
    content = (ROOT / rel).read_text(encoding="utf-8")
    if not content.endswith("\n"):
        violations.append(f"{rel}: missing final newline")
    for line_no, line in enumerate(content.splitlines(), 1):
        if line.rstrip() != line:
            violations.append(f"{rel}:{line_no}: trailing whitespace")
assert not violations, "\n".join(violations)
print(json.dumps({"pass": True, "jsonParsed": len(JSON_FILES), "textChecked": len(TEXT_FILES), "trailingWhitespace": 0, "finalNewlinesPresent": True}, ensure_ascii=False, indent=2))
