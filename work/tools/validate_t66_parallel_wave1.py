#!/usr/bin/env python3
"""Validate frozen T66 wave-1 manifest, assignments, references and candidates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from t66_parallel_protocol import (
    RIGHTS_STATE,
    canonical_json,
    read_json,
    sha_bytes,
    sha_file,
    validate_manifest,
    validate_candidate_schema,
)


def validate_candidate_package(package: dict[str, Any], manifest: dict[str, Any], worker: str, repo_root: Path, package_path: Path) -> dict[str, Any]:
    validate_candidate_schema(package, manifest, repo_root)
    if package.get("schemaVersion") != "t66-parallel-candidate-package-v1":
        raise ValueError(f"candidate schema mismatch: {package_path}")
    if package.get("runId") != manifest["runId"] or package.get("assignment") != worker:
        raise ValueError(f"candidate run/assignment mismatch: {package_path}")
    if package.get("sourceOnly") is not True or package.get("publicRedistribution") != "held" or package.get("humanReview") != "not_performed" or package.get("canonicalBindingAdded") is not False:
        raise ValueError(f"candidate authority was changed: {package_path}")
    assignment = manifest["assignments"][worker]
    source_keys = set(assignment["assignedSourceKeys"])
    nerve_ids = set(assignment["assignedNerveRowIds"])
    if worker == "F":
        submitted = set(package.get("nerveRowIds", []))
        if not submitted or not submitted <= nerve_ids:
            raise ValueError(f"F candidate row scope mismatch: {package_path}")
    else:
        submitted = set(package.get("sourceKeys", []))
        if not submitted or not submitted <= source_keys:
            raise ValueError(f"geometry candidate source scope mismatch: {package_path}")
    allowed_work = {row["workKeyId"] for row in assignment["assignedWorkKeys"]}
    if not set(package.get("completedWorkKeyIds", [])) <= allowed_work:
        raise ValueError(f"candidate work key outside assigned work: {package_path}")
    artifacts = []
    for item in package.get("artifacts", []):
        path = Path(item["path"])
        if not path.is_absolute():
            path = repo_root / path
        path = path.resolve()
        try:
            path.relative_to(package_path.parent.resolve())
        except ValueError as exc:
            raise ValueError(f"candidate artifact escapes package owner directory: {item['path']}") from exc
        if path.is_symlink() or not path.is_file():
            raise FileNotFoundError(f"candidate artifact missing or symlinked: {path}")
        digest = sha_file(path)
        if digest != item.get("sha256") or path.stat().st_size != item.get("bytes"):
            raise ValueError(f"candidate artifact hash/size mismatch: {path}")
        artifacts.append({"path": str(path.relative_to(repo_root)), "sha256": digest, "bytes": path.stat().st_size, "role": item.get("role")})
    if package.get("candidateKind") == "geometry_candidate" and worker in {"A", "B", "C"}:
        if sum(1 for item in package.get("artifacts", []) if item.get("role") == "candidate_input") != 1:
            raise ValueError("geometry candidate needs one candidate_input artifact")
        if not any(item.get("role") == "derived_glb" for item in package.get("artifacts", [])):
            raise ValueError("geometry candidate has no derived GLB artifact")
    if worker == "F" and package.get("candidateKind") == "text_evidence_candidate":
        if not any(item.get("role") == "evidence_delta" for item in package.get("artifacts", [])):
            raise ValueError("F text candidate needs an evidence_delta artifact")
    return {"packagePath": str(package_path.relative_to(repo_root)), "packageSha256": sha_file(package_path), "assignment": worker,
            "sourceKeys": sorted(submitted) if worker != "F" else [], "nerveRowIds": sorted(submitted) if worker == "F" else [], "artifactCount": len(artifacts), "artifacts": artifacts}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--check", action="store_true", help="validate only; never rewrites the manifest")
    parser.add_argument("--verify-source-bytes", action="store_true", help="hash every pinned source resource; use only for an explicitly bounded review")
    parser.add_argument("--candidate-package", action="append", default=[], metavar="WORKER=PATH")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    repo = args.repo_root.expanduser().resolve()
    manifest_path = args.manifest.expanduser().resolve()
    manifest = read_json(manifest_path)
    base = validate_manifest(manifest, repo_root=repo, verify_snapshot=True, verify_source_bytes=args.verify_source_bytes)
    result: dict[str, Any] = {
        "schemaVersion": "t66-parallel-wave-validation-v1",
        "status": "passed",
        "readOnlyCheck": bool(args.check),
        "manifestPath": str(manifest_path.relative_to(repo)),
        "manifestFileSha256": sha_file(manifest_path),
        "canonicalManifestSha256": sha_bytes(canonical_json(manifest)),
        "manifest": base,
        "authority": dict(RIGHTS_STATE),
        "sourceBytesFullyRehashed": bool(args.verify_source_bytes),
        "candidatePackages": [],
        "limitations": [
            "A valid assignment manifest is not an anatomical claim or application acceptance.",
            "Source cache resources are verified on candidate access; this check avoids a redundant archive-wide asset rehash unless --verify-source-bytes is explicitly set.",
            "Source-only, human review, and public redistribution remain independent authority fields.",
        ],
    }
    for spec in args.candidate_package:
        if "=" not in spec:
            raise ValueError("candidate package must be WORKER=PATH")
        worker, raw_path = spec.split("=", 1)
        if worker not in manifest["assignments"]:
            raise ValueError(f"unknown worker assignment: {worker}")
        path = Path(raw_path)
        path = (repo / path).resolve() if not path.is_absolute() else path.resolve()
        package = read_json(path)
        result["candidatePackages"].append(validate_candidate_package(package, manifest, worker, repo, path))
    if args.output:
        output = args.output.expanduser().resolve()
        wave_root = (repo / manifest["manifestPath"]).parent.resolve()
        try:
            output.relative_to(wave_root)
        except ValueError as exc:
            raise ValueError("validation output must remain inside this T66 wave evidence folder") from exc
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        result["outputPath"] = str(output.relative_to(repo))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
