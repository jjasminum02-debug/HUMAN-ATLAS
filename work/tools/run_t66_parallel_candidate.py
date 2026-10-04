#!/usr/bin/env python3
"""Run a frozen T66 candidate package into one explicit owned output root.

Geometry workers use only the frozen T66 authoring contract. F submits text
evidence only; no worker result is registered into the learner runtime here.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import stat
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from t66_parallel_protocol import (
    RIGHTS_STATE,
    canonical_json,
    inside,
    read_json,
    sha_bytes,
    sha_file,
    validate_candidate_schema,
    validate_manifest,
    validate_schema_instance,
    work_key_id,
    apply_writer_correction,
    assigned_bone_context,
    validate_assigned_bone_context,
)


def ensure_no_symlink_path(path: Path, boundary: Path) -> None:
    if ".." in path.parts or ".." in boundary.parts:
        raise ValueError("parent traversal is forbidden in worker paths")
    absolute_path = Path(os.path.abspath(str(path)))
    absolute_boundary = Path(os.path.abspath(str(boundary)))
    for candidate in (absolute_boundary, absolute_path):
        current = Path(candidate.anchor)
        for part in candidate.parts[1:]:
            current = current / part
            try:
                mode = current.lstat().st_mode
            except FileNotFoundError:
                continue
            if stat.S_ISLNK(mode):
                raise ValueError(f"symlink in worker path is forbidden: {current}")
    if not inside(absolute_path, absolute_boundary):
        raise ValueError(f"path escapes owned boundary: {path}")


def resolve_repo_argument(repo_root: Path, raw: Path) -> Path:
    if ".." in raw.parts:
        raise ValueError(f"parent traversal is forbidden in worker path: {raw}")
    return raw.expanduser() if raw.expanduser().is_absolute() else repo_root / raw.expanduser()


def validate_existing_output_root(output_root: Path, boundary: Path, worker: str, run_id: str, manifest_output_root: str) -> dict[str, Any]:
    ensure_no_symlink_path(output_root, boundary)
    if output_root.exists() and not output_root.is_dir():
        raise NotADirectoryError(f"worker output root is not a directory: {output_root}")
    owned_markers: list[str] = []
    inspected_json = 0
    if output_root.exists():
        for item in output_root.rglob("*"):
            ensure_no_symlink_path(item, output_root)
            if not item.is_file() or item.suffix.lower() != ".json":
                continue
            inspected_json += 1
            try:
                value = read_json(item)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if not isinstance(value, dict):
                continue
            file_run_id = value.get("runId")
            if file_run_id is not None and file_run_id != run_id:
                raise ValueError(f"worker output contains a file from another run: {item}")
            owner = value.get("assignment")
            if isinstance(owner, str):
                if owner != worker:
                    raise ValueError(f"worker output contains another assignment's file: {item} ({owner})")
                if file_run_id == run_id:
                    owned_markers.append(str(item.relative_to(output_root)))
            elif isinstance(owner, dict):
                stated_root = owner.get("outputRoot")
                if stated_root is not None and Path(stated_root) != Path(manifest_output_root):
                    raise ValueError(f"worker start record points to another output root: {item}")
                if item.name == "start.json" and file_run_id == run_id and stated_root == manifest_output_root:
                    owned_markers.append(str(item.relative_to(output_root)))
            stated_worker = value.get("worker")
            if stated_worker is not None and stated_worker != worker:
                raise ValueError(f"worker output contains another worker's file: {item} ({stated_worker})")
    nonempty = output_root.exists() and any(output_root.iterdir())
    if nonempty and not owned_markers:
        raise ValueError("non-empty worker output root has no matching run/assignment ownership record")
    return {"status": "owned_root_validated", "nonempty": nonempty, "inspectedJsonFiles": inspected_json,
            "ownershipMarkers": owned_markers, "symlinkCount": 0, "otherOwnerFiles": 0}


def ensure_output_paths_unused(output_root: Path, names: list[str]) -> None:
    collisions = [name for name in names if (output_root / name).exists() or (output_root / name).is_symlink()]
    if collisions:
        raise FileExistsError(f"refusing to overwrite existing worker output paths: {collisions}")


def write_new_bytes(path: Path, data: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(data)


def write_new_text(path: Path, data: str) -> None:
    with path.open("x", encoding="utf-8") as handle:
        handle.write(data)


def validate_package(package: dict[str, Any], manifest: dict[str, Any], worker: str, repo_root: Path, output_root: Path) -> tuple[dict[str, Any] | None, Path | None]:
    validate_candidate_schema(package, manifest, repo_root)
    if package.get("schemaVersion") != "t66-parallel-candidate-package-v1":
        raise ValueError("candidate package schemaVersion mismatch")
    if package.get("runId") != manifest.get("runId"):
        raise ValueError("candidate package belongs to another frozen run")
    if package.get("assignment") != worker:
        raise ValueError("candidate package assignment mismatch")
    if package.get("sourceOnly") is not True or package.get("publicRedistribution") != "held" or package.get("humanReview") != "not_performed" or package.get("canonicalBindingAdded") is not False:
        raise ValueError("candidate package promoted source authority, rights, review, or binding")
    if not isinstance(package.get("candidateNamespace"), str) or not package["candidateNamespace"].startswith(f"worker-{worker}:"):
        raise ValueError("candidate namespace must remain within the assigned worker namespace")
    assignment = manifest["assignments"][worker]
    allowed_sources = set(assignment.get("assignedSourceKeys", []))
    allowed_targets = set(assignment.get("assignedTargetIds", []))
    allowed_nerve_rows = set(assignment.get("assignedNerveRowIds", []))
    submitted_sources = set(package.get("sourceKeys", []))
    submitted_nerve = set(package.get("nerveRowIds", []))
    if worker == "F":
        if not submitted_nerve or not submitted_nerve <= allowed_nerve_rows:
            raise ValueError("F package must reference only its assigned nerve ledger rows")
    elif not submitted_sources or not submitted_sources <= allowed_sources:
        raise ValueError("geometry candidate includes unassigned source keys")
    allowed_work = {x["workKeyId"] for x in assignment.get("assignedWorkKeys", [])}
    completed = set(package.get("completedWorkKeyIds", []))
    if not completed <= allowed_work:
        raise ValueError("candidate claims completion of unassigned work keys")
    for row in package.get("actionWorkKeys", []):
        key = {field: row.get(field) for field in ("family", "side", "action", "sourceKey", "part", "poseContractRevision")}
        expected = work_key_id(key)
        if row.get("workKeyId") != expected:
            raise ValueError(f"candidate action work key hash mismatch: {row.get('workKeyId')}")
        if key["sourceKey"] not in allowed_sources:
            raise ValueError("new action key does not belong to an assigned source")
        if key["action"] is not None and not row.get("evidenceRefs"):
            raise ValueError("a named action must include evidence references")
    for artifact in package.get("artifacts", []):
        raw = artifact.get("path", "")
        p = Path(raw)
        path = resolve_repo_argument(repo_root, p)
        ensure_no_symlink_path(path, output_root)
        if not path.is_file() or path.is_symlink():
            raise FileNotFoundError(f"candidate artifact missing or symlinked: {raw}")
        if path.stat().st_size != artifact.get("bytes") or sha_file(path) != artifact.get("sha256"):
            raise ValueError(f"candidate artifact hash mismatch: {raw}")
    payload_path = None
    payload_artifacts = [x for x in package.get("artifacts", []) if x.get("role") == "candidate_input"]
    if worker != "F":
        if len(payload_artifacts) != 1:
            raise ValueError("geometry package must contain exactly one candidate_input artifact")
        item = payload_artifacts[0]
        p = Path(item["path"])
        payload_path = resolve_repo_argument(repo_root, p)
    return package, payload_path


def load_authoring_modules(snapshot_files: Path, repo_root: Path, input_root: Path):
    tools_snapshot = snapshot_files / "work/tools"
    if not tools_snapshot.is_dir():
        raise FileNotFoundError("frozen tool snapshot is missing")
    sys.path.insert(0, str(tools_snapshot))
    for name in (
        "author_t66_family_motion", "author_source_surface_motion", "derive_source_surface_motion",
        "source_surface_constraints", "t66_contact_correctives", "t66_contact_weights",
        "verify_t66_glb_pose",
    ):
        sys.modules.pop(name, None)
    asfm = importlib.import_module("author_source_surface_motion")
    at66 = importlib.import_module("author_t66_family_motion")
    verify = importlib.import_module("verify_t66_glb_pose")
    for module in (asfm, at66):
        module_path = Path(module.__file__).resolve()
        if not inside(module_path, tools_snapshot.resolve()):
            raise ValueError(f"runtime imported non-frozen module {module.__name__}: {module_path}")
    # Dataset metadata is resolved from the fixed snapshot; immutable source GLBs
    # are resolved only by source_geometry under repo_root and SHA-checked on read.
    def frozen_read(relative: str):
        rel = Path(relative)
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError(f"unsafe frozen input path: {relative}")
        snapshot_path = input_root / rel
        if snapshot_path.is_file() and not snapshot_path.is_symlink():
            return json.loads(snapshot_path.read_text(encoding="utf-8"))
        repo_path = repo_root / rel
        if repo_path.is_file() and not repo_path.is_symlink():
            return json.loads(repo_path.read_text(encoding="utf-8"))
        raise FileNotFoundError(f"path not present in snapshot/repository: {relative}")
    asfm.ROOT = repo_root
    asfm.read = frozen_read
    at66.ROOT = input_root
    at66.read = frozen_read
    return at66, asfm, verify


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--input-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--assignment", choices=["A", "B", "C", "D", "E", "F", "writer-dry-run"], required=True)
    parser.add_argument("--candidate-package", type=Path)
    parser.add_argument("--writer-sample-success", action="store_true")
    parser.add_argument("--disable-source-cache", action="store_true")
    parser.add_argument("--preflight-only", action="store_true", help="validate a worker assignment and execution boundaries without authoring geometry")
    parser.add_argument("--writer-correction", type=Path, help="hash-pinned writer-only ownership metadata correction; frozen manifest remains unchanged")
    args = parser.parse_args()

    # Keep geometry work predictable: one process, one numerical library thread.
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[key] = "1"
    repo_root = args.repo_root.expanduser().resolve()
    manifest_path = resolve_repo_argument(repo_root, args.manifest)
    ensure_no_symlink_path(manifest_path, repo_root)
    manifest_rel = manifest_path.relative_to(repo_root)
    original_manifest = read_json(manifest_path)
    manifest_file_sha256 = sha_file(manifest_path)
    correction_summary = None
    if args.writer_correction:
        correction_path = resolve_repo_argument(repo_root, args.writer_correction)
        ensure_no_symlink_path(correction_path, repo_root)
        receipt = read_json(correction_path)
        manifest, correction_summary = apply_writer_correction(
            original_manifest, receipt, manifest_file_sha256=manifest_file_sha256,
        )
    else:
        manifest = original_manifest
    if manifest.get("waveNumber") == 2 and args.assignment in {"D", "E"} and correction_summary is None:
        raise ValueError("wave-2 D/E execution requires the exact writer correction receipt")
    manifest_check = validate_manifest(
        manifest, repo_root=repo_root, verify_snapshot=True, verify_source_bytes=False,
        verify_original_inputs=manifest.get("waveNumber", 1) == 1,
        assignment_snapshot_source=original_manifest,
    )
    manifest_check["manifestFileSha256"] = manifest_file_sha256
    manifest_check["writerCorrection"] = correction_summary
    if manifest.get("waveNumber", 1) == 2 and args.assignment in {"A", "B", "C", "F"}:
        raise PermissionError("wave-2 A/B/C/F records are read-only carry-forward; only D/E may write new candidates")
    snapshot_root = (repo_root / manifest["snapshotRoot"]).resolve()
    input_root = resolve_repo_argument(repo_root, args.input_root)
    ensure_no_symlink_path(input_root, repo_root)
    allowed_input_roots = [(snapshot_root / "files").resolve()]
    supplemental = manifest.get("supplementalSnapshotRoot")
    if supplemental:
        allowed_input_roots.append((repo_root / supplemental / "files").resolve())
    if input_root.resolve() not in allowed_input_roots:
        raise ValueError("input-root must be one of the frozen snapshot files roots for this run")
    output_root = resolve_repo_argument(repo_root, args.output_root)
    if args.assignment == "writer-dry-run":
        boundary = (repo_root / manifest["writerDryRun"]["outputRoot"]).parent
        manifest_output_root = manifest["writerDryRun"]["outputRoot"]
    else:
        manifest_output_root = manifest["assignments"][args.assignment]["outputRoot"]
        boundary = repo_root / manifest_output_root
    output_root_ownership = validate_existing_output_root(
        output_root, boundary, args.assignment, manifest["runId"], manifest_output_root,
    )
    output_root.mkdir(parents=True, exist_ok=True)

    if args.assignment == "writer-dry-run":
        if not args.writer_sample_success or args.candidate_package:
            raise ValueError("writer-dry-run requires --writer-sample-success and no worker candidate package")
        item = manifest["sampleInputs"]["successfulPackage"]
        sample_path = (repo_root / item["path"]).resolve()
        if not sample_path.is_file() or sample_path.is_symlink() or sha_file(sample_path) != item["sha256"]:
            raise ValueError("frozen successful sample input hash mismatch")
        payload_path = sample_path
        worker = "writer-dry-run"
        package = None
    else:
        worker = args.assignment
        if args.preflight_only:
            if args.candidate_package or worker not in {"D", "E"}:
                raise ValueError("preflight-only is reserved for frozen wave-2 D/E assignments without a candidate package")
            assignment = manifest["assignments"][worker]
            if not assignment.get("assignedWorkKeys") or not assignment.get("assignedSourceKeys"):
                raise ValueError(f"{worker} assignment has no exact source work")
            bone_context = assigned_bone_context(assignment)
            validate_assigned_bone_context(bone_context, assignment)
            at66, asfm, verify = load_authoring_modules(snapshot_root / "files", repo_root, input_root)
            required_functions = [
                (at66, "author"), (asfm, "source_geometry"), (verify, "verify_glb"),
            ]
            missing = [name for module, name in required_functions if not callable(getattr(module, name, None))]
            if missing:
                raise ValueError(f"frozen authoring/QC functions unavailable: {missing}")
            schema_path = repo_root / manifest["workerOutputSchema"]
            schema = read_json(schema_path)
            first_key = assignment["assignedWorkKeys"][0]["workKeyId"]
            sample_source = assignment["assignedSourceKeys"][0]
            canary = {
                "schemaVersion": "t66-parallel-candidate-package-v1",
                "runId": manifest["runId"], "assignment": worker,
                "candidateNamespace": f"worker-{worker}:preflight",
                "candidateKind": "deferred_with_reason", "sourceOnly": True,
                "publicRedistribution": "held", "humanReview": "not_performed",
                "canonicalBindingAdded": False, "completedWorkKeyIds": [],
                "sourceKeys": [sample_source], "artifacts": [],
                "disposition": "deferred_with_reason", "unresolved": ["preflight-only; no candidate authored"],
            }
            validate_schema_instance(canary, schema)
            if canary["assignment"] != worker or first_key not in {row["workKeyId"] for row in assignment["assignedWorkKeys"]}:
                raise ValueError("worker package schema/assignment canary did not bind to its frozen owner")
            try:
                ensure_no_symlink_path(repo_root / "work/evidence/T66/parallel-completion-2026-10-03/wave-1", output_root)
            except ValueError:
                pass
            else:
                raise ValueError("output-root guard accepted a path outside this worker boundary")
            probe = output_root / f".preflight-write-probe-{uuid.uuid4().hex}"
            descriptor = os.open(probe, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            try:
                with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                    handle.write("scoped output permission check\n")
                if probe.read_text(encoding="utf-8") != "scoped output permission check\n":
                    raise OSError("worker output-root write/read probe failed")
            finally:
                probe.unlink(missing_ok=True)
            print(json.dumps({
                "status": "wave2_worker_preflight_passed_without_authoring",
                "assignment": worker, "runId": manifest["runId"],
                "assignedWorkKeys": len(assignment["assignedWorkKeys"]),
                "assignedSourceKeys": len(assignment["assignedSourceKeys"]),
                "assignedBoneSourceKeys": len(bone_context["sourceKeys"]),
                "boneContext": bone_context,
                "schemaPath": str(schema_path.relative_to(repo_root)),
                "authoringModuleRoot": str((snapshot_root / "files/work/tools").relative_to(repo_root)),
                "outputRoot": str(output_root.relative_to(repo_root)),
                "outputRootOwnership": output_root_ownership,
                "inputRoot": str(input_root.relative_to(repo_root)),
                "inputRootKind": "supplemental" if supplemental and input_root.resolve() == (repo_root / supplemental / "files").resolve() else "base",
                "manifestFileSha256": manifest_file_sha256,
                "writerCorrection": correction_summary,
                "outputProbeRemoved": True, "geometryAuthored": False,
                "sourceOnly": True, "publicRedistribution": "held", "humanReview": "not_performed",
            }, ensure_ascii=False, indent=2))
            return
        if worker == "F":
            ensure_output_paths_unused(output_root, ["candidate-handoff.json"])
        else:
            ensure_output_paths_unused(output_root, ["reference.glb", "motion.glb", "authoring-record.json", "pose-qc.json", "candidate-result.json", "candidate-handoff.json"])
        if not args.candidate_package:
            raise ValueError("worker execution needs --candidate-package from its owned output root")
        package_path = resolve_repo_argument(repo_root, args.candidate_package)
        ensure_no_symlink_path(package_path, output_root)
        package = read_json(package_path)
        package, payload_path = validate_package(package, manifest, worker, repo_root, output_root)
        if worker == "F":
            handoff = {
                "schemaVersion": "t66-parallel-candidate-handoff-v1", "runId": manifest["runId"],
                "assignment": worker, "packageSha256": sha_file(package_path),
                "candidateNamespace": package["candidateNamespace"], "candidateKind": package["candidateKind"],
                "disposition": package["disposition"], "nerveRowIds": package.get("nerveRowIds", []),
                "artifacts": package.get("artifacts", []), "authority": dict(RIGHTS_STATE),
                "registeredToLearner": False, "humanReview": "not_performed", "publicRedistribution": "held",
            }
            write_new_text(output_root / "candidate-handoff.json", json.dumps(handoff, ensure_ascii=False, indent=2) + "\n")
            print(json.dumps({"status": "text_candidate_handoff_validated", "handoffPath": str(output_root / 'candidate-handoff.json'), "nerveRows": len(handoff["nerveRowIds"])}, ensure_ascii=False, indent=2))
            return

    assert payload_path is not None
    timings: dict[str, float | None] = {}
    t0 = time.perf_counter()
    input_bytes = payload_path.read_bytes()
    timings["inputReadSeconds"] = time.perf_counter() - t0
    t0 = time.perf_counter()
    input_hash = sha_bytes(input_bytes)
    timings["inputSha256Seconds"] = time.perf_counter() - t0
    t0 = time.perf_counter()
    payload = json.loads(input_bytes)
    timings["inputJsonParseSeconds"] = time.perf_counter() - t0
    if payload.get("rights") != {
        "sourceOnly": True, "localUseRights": "inherits_pinned_source_decision",
        "publicRedistribution": "held", "humanReview": "not_performed",
    }:
        raise ValueError("authoring payload rights do not preserve the pinned local source decision")
    if payload.get("dataset", {}).get("sha256") != next(x["sha256"] for x in manifest["inputs"] if x["path"] == "atlas-data/source-cache/datasets/za/compiled/manifest.json"):
        raise ValueError("candidate authoring dataset hash does not match the frozen compiled manifest")
    payload_source_keys = {x.get("sourceKey") for x in payload.get("members", [])}
    if None in payload_source_keys or not payload_source_keys:
        raise ValueError("authoring input must contain exact sourceKey members")
    compiled = read_json(input_root / "atlas-data/source-cache/datasets/za/compiled/manifest.json")
    compiled_by_key = {row["sourceKey"]: row for row in compiled.get("instances", [])}
    if not payload_source_keys <= set(compiled_by_key):
        raise ValueError("candidate input references source keys absent from frozen compiled snapshot")
    for member in payload["members"]:
        actual_side = compiled_by_key[member["sourceKey"]].get("sourceLabelSide")
        if actual_side not in (None, payload.get("side")):
            raise ValueError(f"candidate source side conflicts with frozen source: {member['sourceKey']}")
    if package:
        if not payload_source_keys <= set(package.get("sourceKeys", [])):
            raise ValueError("candidate authoring payload includes source keys missing from package index")
    else:
        allowed_sample_keys = {x["sourceKey"] for x in payload["members"]}
        if not allowed_sample_keys:
            raise ValueError("sample input has no sources")

    module_started = time.perf_counter()
    at66, asfm, verify = load_authoring_modules(snapshot_root / "files", repo_root, input_root)
    timings["frozenModuleLoadSeconds"] = time.perf_counter() - module_started

    source_cache: dict[str, Any] = {}
    phase_seconds = {"sourceGeometryReadHashDecodeTransformSeconds": 0.0, "contactWeightSolveSeconds": 0.0,
                     "contactCorrectiveSeconds": 0.0, "glbContainerAssemblySeconds": 0.0}
    cache_stats = {"enabled": not args.disable_source_cache, "hits": 0, "misses": 0, "requests": 0, "missParseSeconds": 0.0, "hitLookupSeconds": 0.0}
    original_source_geometry = asfm.source_geometry
    candidate_digest = sha_bytes(canonical_json(payload))
    policy_digest = sha_bytes(canonical_json({"rights": payload["rights"], "sourceOnly": True, "publicRedistribution": "held", "humanReview": "not_performed"}))
    validator_path = snapshot_root / "files/work/tools/author_t66_family_motion.py"
    validator_digest = sha_file(validator_path)

    def cached_source_geometry(row, lod):
        cache_stats["requests"] += 1
        resource = row["lods"][lod]
        key = sha_bytes(canonical_json({
            "sourceResourceSha256": resource["sha256"], "lod": lod,
            "sourceFrameId": compiled.get("frameContract", {}).get("sourceFrameId"),
            "explicitSide": row.get("sourceLabelSide"), "geometryChunkSha256": resource.get("chunk"),
            "instanceMatrix": row.get("matrix"), "candidateInputSha256": candidate_digest,
            "poseHash": sha_bytes(canonical_json(payload.get("family", {}))),
            "weightsAndMasksHash": sha_bytes(canonical_json([m for m in payload.get("members", []) if m.get("sourceKey") == row["sourceKey"]])),
            "validatorRevisionHash": validator_digest, "authorityPolicyHash": policy_digest,
            "workKeyScope": payload.get("family", {}).get("id"),
        }))
        lookup = time.perf_counter()
        if not args.disable_source_cache and key in source_cache:
            cache_stats["hits"] += 1
            cache_stats["hitLookupSeconds"] += time.perf_counter() - lookup
            return source_cache[key]
        start = time.perf_counter()
        result = original_source_geometry(row, lod)
        elapsed = time.perf_counter() - start
        phase_seconds["sourceGeometryReadHashDecodeTransformSeconds"] += elapsed
        cache_stats["misses"] += 1
        cache_stats["missParseSeconds"] += elapsed
        if not args.disable_source_cache:
            source_cache[key] = result
        return result

    at66.source_geometry = cached_source_geometry
    def timed_phase(label, function):
        def wrapped(*values, **options):
            started = time.perf_counter()
            try:
                return function(*values, **options)
            finally:
                phase_seconds[label] += time.perf_counter() - started
        return wrapped
    for name in ("source_frame_contact_feasible_weights", "source_phase_contact_feasible_weight_fields"):
        function = getattr(at66, name, None)
        if function is not None:
            setattr(at66, name, timed_phase("contactWeightSolveSeconds", function))
    for name in ("wrap", "arap_wrap", "source_bone_projection_corrective", "source_topology_contact_patch_corrective"):
        function = getattr(at66, name, None)
        if function is not None:
            setattr(at66, name, timed_phase("contactCorrectiveSeconds", function))
    original_container = at66.container
    at66.container = timed_phase("glbContainerAssemblySeconds", original_container)
    author_started = time.perf_counter()
    rest_bytes, motion_bytes, record, frames = at66.author(payload)
    timings["authorGeometrySolverAndGlbAssemblySeconds"] = time.perf_counter() - author_started
    timings.update(phase_seconds)
    timings["authoringRemainderSeconds"] = max(0.0, timings["authorGeometrySolverAndGlbAssemblySeconds"] - sum(phase_seconds.values()))
    at66.source_geometry = original_source_geometry

    write_started = time.perf_counter()
    reference_path = output_root / "reference.glb"
    motion_path = output_root / "motion.glb"
    write_new_bytes(reference_path, rest_bytes)
    write_new_bytes(motion_path, motion_bytes)
    timings["glbFileWriteSeconds"] = time.perf_counter() - write_started
    record_path = output_root / "authoring-record.json"
    write_started = time.perf_counter()
    write_new_text(record_path, json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    timings["authoringRecordJsonWriteSeconds"] = time.perf_counter() - write_started

    pose_started = time.perf_counter()
    deforming_keys = [x["sourceKey"] for x in payload["members"] if x["role"] in ("deforming_muscle_surface", "deforming_passive_surface")]
    pose = verify.verify_glb_pose if hasattr(verify, "verify_glb_pose") else verify.verify_glb
    pose_result = pose(motion_path, payload, frames, deformation_source_keys=deforming_keys)
    timings["emittedGlbPoseReplaySeconds"] = time.perf_counter() - pose_started
    pose_path = output_root / "pose-qc.json"
    write_started = time.perf_counter()
    write_new_text(pose_path, json.dumps(pose_result, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    timings["poseQcJsonWriteSeconds"] = time.perf_counter() - write_started

    prior_qc = {}
    qc_reuse = {"reused": False, "reason": "no matching prior evidence"}
    qc_lookup_started = time.perf_counter()
    if args.writer_sample_success:
        sample = manifest["sampleInputs"]["successfulPackage"]
        baseline_input = repo_root / sample["sourceEvidencePath"]
        baseline_dir = baseline_input.parent
        old_record = read_json(baseline_dir / "authoring-record.json")
        old_motion = baseline_dir / "motion.glb"
        old_pose = read_json(baseline_dir / "glb-pose-qc.json")
        old_contact = read_json(baseline_dir / "contact-qc.json")
        interpolation = read_json(repo_root / "work/evidence/T66/serial-completion-2026-10-02/unit-02/candidate-interpolation-r1.json")
        same_input_file = sha_file(baseline_input) == sample["sha256"] == input_hash
        same_motion = old_motion.is_file() and sha_file(old_motion) == sha_file(motion_path) == old_record.get("motionSha256") == old_pose.get("motionSha256")
        same_rest = old_record.get("restSha256") == sha_file(reference_path)
        same_family = old_contact.get("familyId") == payload["family"]["id"] and old_contact.get("newContainmentMaximum") == 0
        interp_rows = [r for r in interpolation.get("rows", []) if r.get("familyId") == payload["family"]["id"]]
        same_interpolation = bool(interp_rows) and all(r.get("motionGlbSha256") == sha_file(motion_path) and r.get("inputSha256") == sample["sha256"] and r.get("passed") for r in interp_rows)
        if same_input_file and same_motion and same_rest and same_family and same_interpolation and old_pose.get("passed"):
            prior_qc = {"pose": old_pose, "contact": old_contact, "interpolation": {"rows": len(interp_rows), "allPassed": True, "subdivisionsPerSegment": interpolation.get("subdivisionsPerSegment"), "continuousCollisionFreedomClaimed": False}}
            qc_reuse = {"reused": True, "reason": "frozen source input byte hash and generated rest/motion GLB hashes match exactly; prior independent pose/contact/interpolation QC remains tied to the same bytes"}
        else:
            qc_reuse = {"reused": False, "reason": "existing QC inputs/results did not all match regenerated bytes; no pass inferred"}
    timings["historicalQcLookupSeconds"] = time.perf_counter() - qc_lookup_started if args.writer_sample_success else 0.0
    timings["learnerUiPreparationSeconds"] = None
    final = {
        "schemaVersion": "t66-parallel-writer-dry-run-v1" if args.writer_sample_success else "t66-parallel-worker-result-v1",
        "runId": manifest["runId"], "assignment": worker, "inputPath": str(payload_path), "inputSha256": input_hash,
        "authoringCanonicalInputSha256": record.get("inputSha256"),
        "sourceKeys": sorted(payload_source_keys), "memberCount": len(payload_source_keys),
        "referenceGlb": {"path": str(reference_path.relative_to(repo_root)), "bytes": len(rest_bytes), "sha256": sha_file(reference_path)},
        "motionGlb": {"path": str(motion_path.relative_to(repo_root)), "bytes": len(motion_bytes), "sha256": sha_file(motion_path)},
        "record": {"path": str(record_path.relative_to(repo_root)), "sha256": sha_file(record_path), "rights": record.get("rights"),
                   "sourceGeometryModified": record.get("sourceGeometryModified"), "measuredAnatomicalAxis": record.get("measuredAnatomicalAxis"),
                   "measuredAttachmentFootprints": record.get("measuredAttachmentFootprints"), "physiologicalROM": record.get("physiologicalROM")},
        "emittedPoseReplay": {"path": str(pose_path.relative_to(repo_root)), "rigidRowsPassed": sum(1 for x in pose_result["rows"] if x["passed"]),
                              "deformingRowsNeedGeometryQc": sum(1 for x in pose_result["rows"] if x.get("requiresGeometryQc")),
                              "maximumRigidWorldErrorMetres": pose_result.get("maximumWorldErrorMetres"),
                              "reflectionRowsPreserved": sum(1 for x in pose_result["rows"] if x.get("reflectionPreserved")),
                              "anatomicalApproval": False},
        "priorQcReuse": qc_reuse,
        "priorQcSummary": prior_qc,
        "cacheProfile": cache_stats,
        "stageTimingsSeconds": timings,
        "uiPreparation": {"status": "not_performed", "reason": "candidate dry-run deliberately does not register or edit the learner app"},
        "threadPolicy": {key: os.environ.get(key) for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS")},
        "authority": dict(RIGHTS_STATE),
        "learnerRegistration": "not_performed",
        "status": "candidate_handoff" if not args.writer_sample_success else ("actual_dry_run_passed_existing_identical_qc_reused" if qc_reuse["reused"] else "actual_dry_run_generated_but_qc_reuse_not_proven"),
        "limitations": ["This is a bounded pipeline smoke test on a previously registered T66 input, not new anatomical evidence, runtime registration, human approval, public-rights approval, or full product QA.",
                        "Source pose/mask/axis are authored educational data; motion is not a measured physiological axis, footprint, force, activation, or normal ROM."],
    }
    handoff = {
        "schemaVersion": "t66-parallel-candidate-handoff-v1", "runId": manifest["runId"], "assignment": worker,
        "candidateNamespace": "writer-dry-run:existing-u02-hip-flexion-left" if package is None else package["candidateNamespace"],
        "candidateKind": "geometry_candidate", "disposition": "candidate_validated" if qc_reuse.get("reused") else "deferred_with_reason",
        "workKeyIds": [] if package is None else package.get("completedWorkKeyIds", []),
        "sourceKeys": sorted(payload_source_keys),
        "artifacts": [
            {"path": str(reference_path.relative_to(repo_root)), "sha256": sha_file(reference_path), "bytes": reference_path.stat().st_size, "role": "derived_glb"},
            {"path": str(motion_path.relative_to(repo_root)), "sha256": sha_file(motion_path), "bytes": motion_path.stat().st_size, "role": "derived_glb"},
            {"path": str(record_path.relative_to(repo_root)), "sha256": sha_file(record_path), "bytes": record_path.stat().st_size, "role": "authoring_record"},
            {"path": str(pose_path.relative_to(repo_root)), "sha256": sha_file(pose_path), "bytes": pose_path.stat().st_size, "role": "pose_qc"},
        ],
        "authority": dict(RIGHTS_STATE), "registeredToLearner": False,
    }
    write_new_text(output_root / "candidate-result.json", json.dumps(final, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    write_new_text(output_root / "candidate-handoff.json", json.dumps(handoff, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": final["status"], "outputRoot": str(output_root), "motionSha256": final["motionGlb"]["sha256"],
                      "cache": cache_stats, "stageTimingsSeconds": timings, "manifest": manifest_check}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
