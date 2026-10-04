#!/usr/bin/env python3
"""Positive/negative fixtures for T66 writer correction, paths, and aggregate indexes."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

from run_t66_parallel_candidate import (
    ensure_no_symlink_path,
    ensure_output_paths_unused,
    validate_existing_output_root,
)
from t66_parallel_protocol import (
    apply_writer_correction,
    assigned_bone_context,
    read_json,
    sha_file,
    validate_assigned_bone_context,
    validate_manifest,
)
from validate_t66_aggregate_candidate import verify_artifact_table


def expect_reject(name, action, results):
    try:
        action()
    except (OSError, ValueError) as exc:
        results.append({"name": name, "result": "rejected", "reason": str(exc)})
        return
    raise AssertionError(f"negative case unexpectedly accepted: {name}")


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    evidence = root / "work/evidence/T66/parallel-completion-2026-10-03/wave-2"
    manifest_path = evidence / "run-manifest.json"
    receipt_path = root / "work/evidence/T66/final-writer-2026-10-05/writer-correction-revision-r1.json"
    original = read_json(manifest_path)
    receipt = read_json(receipt_path)
    results = []

    try:
        validate_manifest(original, repo_root=root, verify_snapshot=True, verify_source_bytes=False,
                          verify_original_inputs=False)
        raise AssertionError("original frozen manifest should expose its duplicated D/E ownership metadata")
    except ValueError as exc:
        if "embedded owner metadata differs" not in str(exc):
            raise
        results.append({"name": "frozen-manifest-mismatch-reproduced", "result": "expected_rejection", "reason": str(exc)})

    effective, correction_summary = apply_writer_correction(original, receipt, manifest_file_sha256=sha_file(manifest_path))
    corrected_validation = validate_manifest(
        effective, repo_root=root, verify_snapshot=True, verify_source_bytes=False,
        verify_original_inputs=False, assignment_snapshot_source=original,
    )
    assert corrected_validation["valid"] is True
    assert correction_summary["frozenManifestMutated"] is False
    assert correction_summary["workerSnapshotsMutated"] is False
    assert correction_summary["byAssignment"] == {"D": 16, "E": 66}
    results.append({"name": "hash-pinned-writer-correction-and-immutable-snapshots", "result": "accepted",
                    "correctedRows": correction_summary["correctedAssignmentRows"],
                    "counts": corrected_validation["counts"]})

    bad_receipt = copy.deepcopy(receipt)
    bad_receipt["baseManifestFileSha256"] = "0" * 64
    expect_reject("reject-wrong-base-manifest-hash",
                  lambda: apply_writer_correction(original, bad_receipt, manifest_file_sha256=sha_file(manifest_path)), results)

    bad_manifest = copy.deepcopy(original)
    d_work_id = effective["assignments"]["D"]["assignedWorkKeys"][0]["workKeyId"]
    queue_row = next(row for row in bad_manifest["sourceActionScopeQueue"] if row["workKeyId"] == d_work_id)
    queue_row["assignedTo"] = "E"
    expect_reject("reject-changed-owner-source-row",
                  lambda: apply_writer_correction(bad_manifest, receipt, manifest_file_sha256=sha_file(manifest_path)), results)

    worker_e = effective["assignments"]["E"]
    bone_context = assigned_bone_context(worker_e)
    validate_assigned_bone_context(bone_context, worker_e)
    assert not set(bone_context["sourceKeys"]) & set(worker_e["assignedSourceKeys"])
    results.append({"name": "typed-read-only-bone-context", "result": "accepted",
                    "boneSourceKeys": len(bone_context["sourceKeys"]), "muscleSourceOverlap": 0})

    bad_bones = copy.deepcopy(bone_context)
    bad_bones["candidateMuscleMember"] = True
    expect_reject("reject-bone-context-as-muscle-member",
                  lambda: validate_assigned_bone_context(bad_bones, worker_e), results)
    unassigned_bones = copy.deepcopy(bone_context)
    unassigned_bones["sourceKeys"] = ["unassigned-bone-source"]
    expect_reject("reject-unassigned-bone-source",
                  lambda: validate_assigned_bone_context(unassigned_bones, worker_e), results)

    with tempfile.TemporaryDirectory(prefix=".t66-writer-contract-", dir=root / "work/evidence/T66/final-writer-2026-10-05") as temp:
        temp_root = Path(temp)
        owned = temp_root / "owned"
        owned.mkdir()
        (owned / "handoff.json").write_text(json.dumps({"runId": "run-x", "assignment": "E", "worker": "E"}) + "\n")
        ownership = validate_existing_output_root(owned, owned, "E", "run-x", "workers/E")
        assert ownership["nonempty"] and ownership["ownershipMarkers"] == ["handoff.json"]
        results.append({"name": "allow-prepopulated-owned-output-root", "result": "accepted", "ownership": ownership})

        other_owner = temp_root / "other-owner"
        other_owner.mkdir()
        (other_owner / "handoff.json").write_text(json.dumps({"runId": "run-x", "assignment": "D", "worker": "D"}) + "\n")
        expect_reject("reject-other-assignment-output-file",
                      lambda: validate_existing_output_root(other_owner, other_owner, "E", "run-x", "workers/E"), results)

        outside = temp_root / "outside.json"
        outside.write_text("{}\n")
        linked = temp_root / "symlink-root"
        linked.mkdir()
        (linked / "escape.json").symlink_to(outside)
        expect_reject("reject-symlink-in-owned-output-root",
                      lambda: validate_existing_output_root(linked, linked, "E", "run-x", "workers/E"), results)

        collision_root = temp_root / "collision"
        collision_root.mkdir()
        (collision_root / "package.json").write_text("{}\n")
        expect_reject("reject-output-overwrite-collision",
                      lambda: ensure_output_paths_unused(collision_root, ["package.json", "new.json"]), results)

        aggregate_root = temp_root / "aggregate"
        aggregate_root.mkdir()
        artifacts = []
        for index in range(2):
            artifact_path = aggregate_root / f"input-{index}.json"
            data = json.dumps({"fixture": index}, sort_keys=True).encode()
            artifact_path.write_bytes(data)
            artifacts.append({"role": "candidate_input", "path": str(artifact_path),
                              "sha256": __import__("hashlib").sha256(data).hexdigest(), "bytes": len(data)})
        package = {"artifacts": artifacts}
        verified, role_counts = verify_artifact_table(package, root, aggregate_root)
        assert len(verified) == 2 and role_counts["candidate_input"] == 2
        results.append({"name": "aggregate-index-keeps-two-payloads-distinct", "result": "accepted",
                        "candidateInputArtifacts": len(verified)})
    bad_package = copy.deepcopy(package)
    bad_package["artifacts"][1]["sha256"] = "f" * 64
    expect_reject("reject-aggregate-artifact-hash-mismatch",
                  lambda: verify_artifact_table(bad_package, root, aggregate_root), results)

    actual_e_result = read_json(root / "work/evidence/T66/final-writer-2026-10-05/e-aggregate-preflight.json")
    assert actual_e_result["status"] == "aggregate_index_preflight_failed"
    assert actual_e_result["failure"]["integrity"]["path"] == "proposals.json"
    assert actual_e_result["candidateRegistered"] is False
    results.append({"name": "preserve-actual-E-index-drift-as-failure",
                    "result": "rejected_as_unverified_candidate",
                    "mismatch": actual_e_result["failure"]["integrity"]})

    output = {
        "schemaVersion": "t66-writer-contract-tests-v1",
        "status": "passed",
        "wave2ManifestSha256": sha_file(manifest_path),
        "writerCorrectionSha256": sha_file(receipt_path),
        "testCount": len(results),
        "tests": results,
        "scope": "writer ownership correction, immutable snapshots, typed read-only bone context, output-root/path safety, and aggregate index artifact integrity; no geometry or learner acceptance",
    }
    destination = root / "work/evidence/T66/final-writer-2026-10-05/writer-contract-tests.json"
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "testCount": output["testCount"],
                      "output": str(destination.relative_to(root))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
