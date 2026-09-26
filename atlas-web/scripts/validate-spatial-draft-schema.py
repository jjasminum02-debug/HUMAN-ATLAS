#!/usr/bin/env python3
"""Validate the separate T13b spatial draft JSON schema and structural fixtures."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "atlas-data/schemas"))
import validate as atlas_validate  # noqa: E402

SCHEMA_PATH = ROOT / "atlas-data/schemas/spatial-draft-layer.schema.json"
FIXTURE_DIR = ROOT / "work/evidence/T13b/fixtures"


def load(path: Path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def codes(issues):
    return sorted({issue["code"] for issue in issues})


def main() -> int:
    schema = load(SCHEMA_PATH)
    positive = load(FIXTURE_DIR / "positive-spatial-layer.json")
    unknown = load(FIXTURE_DIR / "negative-unknown-field.json")
    invalid_status = load(FIXTURE_DIR / "negative-status.json")
    schema_errors = atlas_validate.check_schema(schema)
    positive_errors = atlas_validate.schema_issues(schema, positive)
    unknown_codes = codes(atlas_validate.schema_issues(schema, unknown))
    status_codes = codes(atlas_validate.schema_issues(schema, invalid_status))
    passed = (
        not schema_errors
        and not positive_errors
        and "schema_additional_property" in unknown_codes
        and "schema_enum" in status_codes
    )
    result = {
        "passed": passed,
        "schema": str(SCHEMA_PATH.relative_to(ROOT)),
        "positiveFixtureErrors": positive_errors,
        "unknownFieldRejected": "schema_additional_property" in unknown_codes,
        "invalidStatusRejected": "schema_enum" in status_codes,
        "schemaErrors": schema_errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
