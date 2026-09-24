#!/usr/bin/env python3
"""Check that T03 schema/fixture/result JSON is parseable and validator syntax compiles."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T03"
paths = [ROOT / "atlas-data/schemas/atlas.schema.json", *sorted((EVIDENCE / "fixtures").rglob("*.json")), *[EVIDENCE / name for name in ("schema-check.json", "validation.json", "dataset-validation.json", "preservation.json")]]
for path in paths:
    json.loads(path.read_text(encoding="utf-8"))
validator = ROOT / "atlas-data/schemas/validate.py"
compile(validator.read_text(encoding="utf-8"), str(validator), "exec")
result = {"passed": True, "jsonFilesParsed": len(paths), "validatorSyntax": "passed", "method": "in-memory compile; no bytecode cache output"}
print(json.dumps(result, ensure_ascii=False, indent=2))
