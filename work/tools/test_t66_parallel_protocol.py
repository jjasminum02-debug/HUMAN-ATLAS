#!/usr/bin/env python3
"""Run bounded negative/positive cases for the frozen T66 candidate contract."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from t66_parallel_protocol import (
    read_json,
    sha_file,
    validate_candidate_schema,
    validate_schema_instance,
    work_key_id,
)


def action_row(family: str, source_key: str) -> dict[str, Any]:
    key = {
        "family": family,
        "side": "left",
        "action": "flexion",
        "sourceKey": source_key,
        "part": None,
        "poseContractRevision": "all-muscle-motion-2026-10-02",
    }
    return {
        **key,
        "workKeyId": work_key_id(key),
        "evidenceRefs": ["frozen-claim-ref"],
        "implementationState": "qualitative_action_demonstration",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.repo_root.expanduser().resolve()
    manifest_path = args.manifest.expanduser().resolve()
    manifest = read_json(manifest_path)
    schema_path = root / manifest["workerOutputSchema"]
    schema = read_json(schema_path)
    source_key = manifest["assignments"]["A"]["assignedSourceKeys"][0]
    base = {
        "schemaVersion": "t66-parallel-candidate-package-v1",
        "runId": manifest["runId"],
        "assignment": "A",
        "candidateNamespace": "worker-A:protocol-test",
        "candidateKind": "geometry_candidate",
        "sourceOnly": True,
        "publicRedistribution": "held",
        "humanReview": "not_performed",
        "canonicalBindingAdded": False,
        "completedWorkKeyIds": [],
        "sourceKeys": [source_key],
        "artifacts": [],
        "disposition": "candidate_validated",
        "createdAt": "2026-10-03T12:00:00Z",
    }

    cases: list[tuple[str, dict[str, Any], bool, bool]] = [
        ("valid-minimal-package", copy.deepcopy(base), True, False),
    ]
    bad = copy.deepcopy(base)
    bad["extraPrivateField"] = "x"
    cases.append(("reject-additional-property", bad, False, False))
    bad = copy.deepcopy(base)
    del bad["sourceOnly"]
    cases.append(("reject-missing-required", bad, False, False))
    bad = copy.deepcopy(base)
    bad["sourceKeys"] = [source_key, source_key]
    cases.append(("reject-duplicate-source-list", bad, False, False))
    bad = copy.deepcopy(base)
    bad["createdAt"] = "2026-99-99T12:00:00Z"
    cases.append(("reject-invalid-date-time", bad, False, False))
    bad = copy.deepcopy(base)
    bad["createdAt"] = "2026-10-03T12:00:00"
    cases.append(("reject-date-time-without-zone", bad, False, False))
    bad = copy.deepcopy(base)
    bad["actionWorkKeys"] = [action_row("hip", source_key), action_row("hip", source_key)]
    cases.append(("reject-repeated-exact-action-work-key", bad, False, True))
    valid = copy.deepcopy(base)
    valid["actionWorkKeys"] = [action_row("hip", source_key), action_row("elbow", source_key)]
    cases.append(("allow-same-source-distinct-families", valid, True, True))

    results = []
    for name, value, should_accept, candidate_check in cases:
        try:
            if candidate_check:
                validate_candidate_schema(value, manifest, root)
            else:
                validate_schema_instance(value, schema)
            accepted, reason = True, None
        except (ValueError, TypeError) as error:
            accepted, reason = False, str(error)
        if accepted != should_accept:
            raise AssertionError(f"{name}: accepted={accepted}, expected={should_accept}, reason={reason}")
        results.append({
            "name": name,
            "result": "accepted" if accepted else "rejected",
            "expected": "accepted" if should_accept else "rejected",
            "validator": "candidate" if candidate_check else "schema",
            "reason": reason,
        })

    output = {
        "schemaVersion": "t66-parallel-protocol-contract-tests-v1",
        "status": "passed",
        "runId": manifest["runId"],
        "manifestSha256": sha_file(manifest_path),
        "schemaSha256": sha_file(schema_path),
        "count": len(results),
        "tests": results,
        "scope": "candidate package schema and exact six-field work-key identity; no anatomy, learner registration, rights or human review approval",
    }
    destination = args.output.expanduser().resolve()
    wave_root = (root / manifest["manifestPath"]).parent.resolve()
    if not destination.is_relative_to(wave_root):
        raise ValueError("test output must remain inside this T66 wave evidence folder")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "count": len(results), "output": str(destination.relative_to(root))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
