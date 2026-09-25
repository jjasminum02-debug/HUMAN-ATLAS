#!/usr/bin/env python3
"""Check the T09 exchange schema and representative fixtures using T03's schema engine."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "atlas-data/schemas"))
import validate as atlas_validate  # noqa: E402

SCHEMA_PATH = ROOT / "atlas-data/schemas/annotation-draft-exchange.schema.json"
FIXTURE_DIR = ROOT / "work/evidence/T09/fixtures"


def load(path: Path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def main() -> int:
    schema = load(SCHEMA_PATH)
    positive = load(FIXTURE_DIR / "positive-exchange.json")
    reviewed = load(FIXTURE_DIR / "negative-reviewed-state.json")
    unknown_field = copy.deepcopy(positive)
    unknown_field["annotations"][0]["anatomyApproved"] = True

    schema_errors = atlas_validate.check_schema(schema)
    positive_errors = atlas_validate.schema_issues(schema, positive)
    reviewed_errors = atlas_validate.schema_issues(schema, reviewed)
    unknown_errors = atlas_validate.schema_issues(schema, unknown_field)
    reviewed_codes = sorted({issue["code"] for issue in reviewed_errors})
    unknown_codes = sorted({issue["code"] for issue in unknown_errors})
    passed = (
        not schema_errors
        and not positive_errors
        and "schema_enum" in reviewed_codes
        and "schema_additional_property" in unknown_codes
    )
    print(json.dumps({
        "passed": passed,
        "schemaErrors": schema_errors,
        "positiveErrors": positive_errors,
        "reviewedStateRejected": "schema_enum" in reviewed_codes,
        "unknownFieldRejected": "schema_additional_property" in unknown_codes,
    }, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
