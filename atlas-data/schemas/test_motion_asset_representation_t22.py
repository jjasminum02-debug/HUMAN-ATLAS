#!/usr/bin/env python3
"""T22 schema/validator checks for the separate bone-plus-path representation."""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = Path(__file__).with_name("validate_motion_learning.py")
FIXTURE_PATH = ROOT / "work/evidence/T22/fixtures/combined-bone-motion-path-positive.json"
CONTEXT_PATH = ROOT / "work/evidence/T20/fixtures/context.json"

spec = importlib.util.spec_from_file_location("human_atlas_motion_learning_validator_t22", VALIDATOR_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("Could not load the motion learning validator")
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)


def main() -> int:
    schema = validator.load_schema()
    context = json.loads(CONTEXT_PATH.read_text(encoding="utf-8"))
    context["fixtureMode"] = True
    context.setdefault("fixtureAssets", {})
    positive = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    positive_issues = validator.validate_bundle(positive, schema, context, allow_fixture=True)
    if positive_issues:
        raise SystemExit(f"combined positive fixture failed: {positive_issues}")

    wrong_subject = copy.deepcopy(positive)
    wrong_subject["motionAssets"][0]["illustration"]["trajectoryBindings"][0]["structureId"] = "FX-NOT-THE-ACTION-SUBJECT"
    issues = validator.validate_bundle(wrong_subject, schema, context, allow_fixture=True)
    codes = {row["code"] for row in issues}
    if "combined_path_subject_binding_mismatch" not in codes:
        raise SystemExit(f"combined path with an unrelated structure was not rejected: {issues}")

    missing_path = copy.deepcopy(positive)
    missing_path["motionAssets"][0]["illustration"] = None
    schema_issues = validator.validate_bundle(missing_path, schema, context, allow_fixture=True)
    if not schema_issues:
        raise SystemExit("combined representation without its path binding was accepted")

    print("PASS: combined bone-node + subject-path contract positive/negative fixtures (3/3)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
