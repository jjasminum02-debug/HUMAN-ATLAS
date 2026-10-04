#!/usr/bin/env python3
"""Preflight an aggregate T66 worker index without treating it as one payload.

This validates a package index and its many independently hashed files. It does
not author geometry, run action-outcome QC, register learner content, or approve
anatomy, human review, or redistribution rights.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from run_t66_parallel_candidate import ensure_no_symlink_path, validate_existing_output_root
from t66_parallel_protocol import (
    RIGHTS_STATE,
    apply_writer_correction,
    canonical_json,
    read_json,
    sha_bytes,
    sha_file,
    validate_candidate_schema,
    validate_manifest,
)


class AggregateIntegrityError(ValueError):
    def __init__(self, message: str, *, path: str | None = None, expected_sha256: str | None = None,
                 observed_sha256: str | None = None, expected_bytes: int | None = None,
                 observed_bytes: int | None = None):
        super().__init__(message)
        self.details = {
            "path": path,
            "expectedSha256": expected_sha256,
            "observedSha256": observed_sha256,
            "expectedBytes": expected_bytes,
            "observedBytes": observed_bytes,
        }


def repo_path(repo_root: Path, raw: str | Path, boundary: Path) -> Path:
    value = Path(raw).expanduser()
    if ".." in value.parts:
        raise ValueError(f"parent traversal is forbidden in aggregate package path: {raw}")
    path = value if value.is_absolute() else repo_root / value
    ensure_no_symlink_path(path, boundary)
    return path


def verify_artifact_table(package: dict[str, Any], repo_root: Path, output_root: Path) -> tuple[dict[str, dict[str, Any]], Counter[str]]:
    by_path: dict[str, dict[str, Any]] = {}
    roles: Counter[str] = Counter()
    for artifact in package.get("artifacts", []):
        path = repo_path(repo_root, artifact["path"], output_root)
        rel = str(path.relative_to(output_root))
        if rel in by_path:
            raise ValueError(f"aggregate package repeats an artifact path: {rel}")
        if not path.is_file() or path.is_symlink():
            raise FileNotFoundError(f"aggregate candidate artifact missing or symlinked: {rel}")
        digest = sha_file(path)
        size = path.stat().st_size
        if digest != artifact.get("sha256") or size != artifact.get("bytes"):
            raise AggregateIntegrityError(
                f"aggregate candidate artifact hash/size mismatch: {rel}", path=rel,
                expected_sha256=artifact.get("sha256"), observed_sha256=digest,
                expected_bytes=artifact.get("bytes"), observed_bytes=size,
            )
        by_path[rel] = {**artifact, "resolvedPath": path, "sha256Observed": digest, "bytesObserved": size}
        roles[artifact["role"]] += 1
    return by_path, roles


def validate_aggregate_candidate(
    *, repo_root: Path, manifest: dict[str, Any], assignment_name: str,
    package_path: Path, handoff_path: Path, source_audit_path: Path,
) -> dict[str, Any]:
    assignment = manifest["assignments"][assignment_name]
    output_root = (repo_root / assignment["outputRoot"]).resolve()
    owner_check = validate_existing_output_root(output_root, output_root, assignment_name, manifest["runId"], assignment["outputRoot"])

    package = read_json(package_path)
    validate_candidate_schema(package, manifest, repo_root)
    if package.get("runId") != manifest.get("runId") or package.get("assignment") != assignment_name:
        raise ValueError("aggregate candidate index run/assignment mismatch")
    if package.get("sourceOnly") is not True or package.get("publicRedistribution") != "held" or package.get("humanReview") != "not_performed" or package.get("canonicalBindingAdded") is not False:
        raise ValueError("aggregate candidate index promoted rights, review, or canonical authority")
    if not str(package.get("candidateNamespace", "")).startswith(f"worker-{assignment_name}:"):
        raise ValueError("aggregate candidate namespace is outside its assignment")

    assigned_sources = set(assignment.get("assignedSourceKeys", []))
    assigned_bones = set(assignment.get("assignedBoneSourceKeys", []))
    assigned_work = {row["workKeyId"] for row in assignment.get("assignedWorkKeys", [])}
    submitted_sources = set(package.get("sourceKeys", []))
    if submitted_sources != assigned_sources:
        raise ValueError("aggregate package source inventory differs from the exact assigned muscle source set")
    if not set(package.get("completedWorkKeyIds", [])) <= assigned_work:
        raise ValueError("aggregate package contains work keys outside its assignment")
    for row in package.get("actionWorkKeys", []):
        if row["sourceKey"] not in assigned_sources:
            raise ValueError(f"aggregate action row refers to a non-assigned muscle source: {row['workKeyId']}")
        if row["action"] is not None and not row.get("evidenceRefs"):
            raise ValueError(f"named action row has no evidence references: {row['workKeyId']}")

    artifacts, role_counts = verify_artifact_table(package, repo_root, output_root)
    candidate_inputs = [p for p, row in artifacts.items() if row["role"] == "candidate_input"]
    if len(candidate_inputs) <= 1:
        raise ValueError("aggregate-index validator expects multiple candidate_input artifacts; use the single-payload runner otherwise")

    handoff = read_json(handoff_path)
    if handoff.get("runId") != manifest.get("runId") or handoff.get("assignment") != assignment_name:
        raise ValueError("aggregate worker handoff run/assignment mismatch")
    expected_work_ids = {row["workKeyId"] for row in assignment.get("assignedWorkKeys", [])}
    if set(handoff.get("assignedWorkKeyIds", [])) != expected_work_ids:
        raise ValueError("aggregate handoff does not cover the exact assigned work key IDs")
    if set(handoff.get("assignedSourceKeys", [])) != assigned_sources:
        raise ValueError("aggregate handoff muscle source set differs from the assignment")
    if handoff.get("assignedWorkKeysUnchanged") is not True:
        raise ValueError("aggregate handoff does not attest frozen assigned work-key identity")

    source_results = handoff.get("sourceWorkResults", [])
    result_ids = [row.get("workKeyId") for row in source_results]
    if len(result_ids) != len(set(result_ids)) or set(result_ids) != expected_work_ids:
        raise ValueError("aggregate handoff source work result rows are incomplete or duplicated")
    allowed_statuses = {"candidate_validated", "blocked_engineering", "missing_source_or_relation", "not_applicable_with_evidence"}
    if any(row.get("status") not in allowed_statuses for row in source_results):
        raise ValueError("aggregate handoff contains an unsupported work result status")

    candidate_assets = handoff.get("candidateAssets", [])
    asset_sources = [row.get("sourceKey") for row in candidate_assets]
    if len(asset_sources) != len(set(asset_sources)) or not set(asset_sources) <= assigned_sources:
        raise ValueError("aggregate candidate GLB inventory repeats or escapes assigned muscle sources")
    for asset in candidate_assets:
        source_key = asset["sourceKey"]
        for field, role, hash_field, bytes_field in (
            ("path", "derived_glb", "sha256", "bytes"),
            ("authoringInputPath", "authoring_record", "authoringInputSha256", None),
            ("qcPath", "geometry_qc", "qcSha256", None),
        ):
            path = repo_path(repo_root, asset[field], output_root)
            rel = str(path.relative_to(output_root))
            entry = artifacts.get(rel)
            if entry is None or entry["role"] != role or entry["sha256"] != asset[hash_field]:
                raise ValueError(f"candidate asset {source_key} is not linked to its {role} artifact")
            if bytes_field and entry[bytes_field] != asset[bytes_field]:
                raise ValueError(f"candidate asset {source_key} byte count differs from aggregate index")
        authoring_entry = artifacts[str(repo_path(repo_root, asset["authoringInputPath"], output_root).relative_to(output_root))]
        authoring = read_json(authoring_entry["resolvedPath"])
        if authoring.get("source", {}).get("sourceKey") != source_key:
            raise ValueError(f"authoring input source identity mismatch: {source_key}")
        if authoring.get("source", {}).get("side") != asset.get("side"):
            raise ValueError(f"authoring input side differs from candidate index: {source_key}")
        member_sources = {row.get("sourceKey") for row in authoring.get("sourceBinding", {}).get("members", [])}
        if not member_sources or not member_sources <= assigned_sources:
            raise ValueError(f"authoring input includes missing/unassigned source members: {source_key}")
        if authoring.get("rights") != {
            "sourceOnly": True, "localUseRights": "inherits_pinned_source_decision",
            "publicRedistribution": "held", "humanReview": "not_performed",
        }:
            raise ValueError(f"authoring input changed source rights/review state: {source_key}")
        qc_entry = artifacts[str(repo_path(repo_root, asset["qcPath"], output_root).relative_to(output_root))]
        qc = read_json(qc_entry["resolvedPath"])
        if qc.get("sourceKey") != source_key or qc.get("candidateGlbSha256") != asset.get("sha256"):
            raise ValueError(f"geometry QC does not bind to its source/output bytes: {source_key}")

    source_audit = read_json(source_audit_path)
    if source_audit.get("runId") != manifest.get("runId") or source_audit.get("assignment") != assignment_name:
        raise ValueError("aggregate source audit run/assignment mismatch")
    if source_audit.get("assignedMuscleSourceCount") != len(assigned_sources) or source_audit.get("assignedBoneContextSourceCount") != len(assigned_bones):
        raise ValueError("aggregate source audit mixes or drops muscle/bone assignment counts")
    muscle_resources = {row.get("sourceKey") for row in source_audit.get("resources", []) if row.get("kind") == "assigned_muscle"}
    bone_resources = {row.get("sourceKey") for row in source_audit.get("resources", []) if row.get("kind") == "assigned_bone_context"}
    if muscle_resources != assigned_sources or bone_resources != assigned_bones:
        raise ValueError("source audit resources do not preserve typed muscle and read-only bone source inventories")

    counts = handoff.get("counts", {})
    authority = handoff.get("authority", {})
    if authority.get("sourceOnly") is not True or authority.get("publicRedistribution") != "held" or authority.get("humanReview") != "not_performed" or authority.get("productionAcceptance") is not False or authority.get("registeredToLearner") is not False:
        raise ValueError("worker handoff authority state is not held/unregistered")
    if counts.get("actionOutcomeQcPassed") != 0 or counts.get("candidateValidatedWorkKeys") != 0:
        raise ValueError("worker handoff action-outcome evidence changed; writer review required")

    return {
        "schemaVersion": "t66-aggregate-package-preflight-v1",
        "status": "aggregate_index_integrity_passed_action_acceptance_not_passed",
        "runId": manifest["runId"], "assignment": assignment_name,
        "packageIndexPath": str(package_path.relative_to(repo_root)), "packageIndexSha256": sha_file(package_path),
        "handoffPath": str(handoff_path.relative_to(repo_root)), "handoffSha256": sha_file(handoff_path),
        "sourceAuditPath": str(source_audit_path.relative_to(repo_root)), "sourceAuditSha256": sha_file(source_audit_path),
        "outputRootOwnership": owner_check,
        "counts": {
            "assignedWorkKeys": len(assigned_work), "assignedMuscleSourceKeys": len(assigned_sources),
            "assignedBoneContextSourceKeysReadOnly": len(assigned_bones), "candidateActionRows": len(package.get("actionWorkKeys", [])),
            "artifactCount": len(artifacts), "artifactRoleCounts": dict(role_counts),
            "candidateInputArtifacts": len(candidate_inputs), "derivedGlbAssets": len(candidate_assets),
            "candidateAssetSourceKeys": len(set(asset_sources)),
            "geometryQcPassed": counts.get("localGeometryQcPassed"), "geometryQcFailed": counts.get("localGeometryQcFailed"),
            "actionOutcomeQcPassed": counts.get("actionOutcomeQcPassed"),
            "candidateValidatedWorkKeys": counts.get("candidateValidatedWorkKeys"),
            "blockedEngineeringWorkKeys": counts.get("blockedEngineeringWorkKeys"),
            "missingSourceOrRelationWorkKeys": counts.get("missingSourceOrRelationWorkKeys"),
        },
        "authority": dict(RIGHTS_STATE),
        "interpretation": "This validates one aggregate index and the files it references. Its many candidate_input assets are not one runner payload. Geometry/file integrity is not action-outcome acceptance or learner registration.",
        "registeredToLearner": False, "productionAcceptance": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--writer-correction", required=True, type=Path)
    parser.add_argument("--input-root", required=True, type=Path, help="base or supplemental frozen snapshot files root")
    parser.add_argument("--assignment", required=True, choices=["D", "E"])
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--handoff", required=True, type=Path)
    parser.add_argument("--source-audit", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    repo_root = args.repo_root.expanduser().resolve()
    manifest_path = repo_path(repo_root, args.manifest, repo_root)
    correction_path = repo_path(repo_root, args.writer_correction, repo_root)
    manifest_original = read_json(manifest_path)
    manifest, correction_summary = apply_writer_correction(
        manifest_original, read_json(correction_path), manifest_file_sha256=sha_file(manifest_path),
    )
    input_root = repo_path(repo_root, args.input_root, repo_root)
    allowed_inputs = {(repo_root / manifest["snapshotRoot"] / "files").resolve()}
    if manifest.get("supplementalSnapshotRoot"):
        allowed_inputs.add((repo_root / manifest["supplementalSnapshotRoot"] / "files").resolve())
    if input_root.resolve() not in allowed_inputs:
        raise ValueError("input-root is not one of the frozen snapshot roots")
    validation = validate_manifest(
        manifest, repo_root=repo_root, verify_snapshot=True, verify_source_bytes=False,
        verify_original_inputs=False, assignment_snapshot_source=manifest_original,
    )
    validation["writerCorrection"] = correction_summary
    assignment = manifest["assignments"][args.assignment]
    package_path = repo_path(repo_root, args.package, repo_root / assignment["outputRoot"])
    handoff_path = repo_path(repo_root, args.handoff, repo_root / assignment["outputRoot"])
    source_audit_path = repo_path(repo_root, args.source_audit, repo_root / assignment["outputRoot"])
    try:
        result = validate_aggregate_candidate(
            repo_root=repo_root, manifest=manifest, assignment_name=args.assignment,
            package_path=package_path, handoff_path=handoff_path, source_audit_path=source_audit_path,
        )
        exit_code = 0
    except Exception as exc:
        result = {
            "schemaVersion": "t66-aggregate-package-preflight-v1",
            "status": "aggregate_index_preflight_failed",
            "runId": manifest["runId"], "assignment": args.assignment,
            "packageIndexPath": str(package_path.relative_to(repo_root)),
            "packageIndexSha256": sha_file(package_path) if package_path.is_file() else None,
            "failure": {"type": type(exc).__name__, "message": str(exc),
                        "integrity": getattr(exc, "details", None)},
            "candidateRegistered": False, "productionAcceptance": False,
        }
        exit_code = 2
    result["manifestValidation"] = validation
    result["manifestFileSha256"] = sha_file(manifest_path)
    result["writerCorrectionPath"] = str(correction_path.relative_to(repo_root))
    result["writerCorrectionSha256"] = sha_file(correction_path)
    output_path = repo_path(repo_root, args.output, repo_root / "work/evidence/T66/final-writer-2026-10-05")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "failure": result.get("failure"), "counts": result.get("counts"), "output": str(output_path.relative_to(repo_root))}, ensure_ascii=False, indent=2))
    if exit_code:
        raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
