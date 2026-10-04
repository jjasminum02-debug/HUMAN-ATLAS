#!/usr/bin/env python3
"""Verify the immutable T66 wave-1 handoff and bounded wave-2 D/E freeze."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


W1_SHA = "7d12000c2a049d1c2bf09f8349159609a6dd7b5f93f1d0710742ede84aacad95"
D_NAMES = {
    "Bucinator", "Deep part of masseter", "Inferior head of lateral pterygoid muscle",
    "Medial pterygoid muscle", "Palatopharyngeus muscle", "Superficial part of masseter",
    "Superior head of lateral pterygoid muscle", "Temporalis muscle",
}


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--run-preflight", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    base = root / "work/evidence/T66/parallel-completion-2026-10-03"
    w1_path = base / "wave-1/run-manifest.json"
    w2_path = base / "wave-2/run-manifest.json"
    w1_bytes = w1_path.read_bytes()
    w2_bytes = w2_path.read_bytes()
    if sha_bytes(w1_bytes) != W1_SHA:
        raise ValueError("wave-1 manifest bytes changed from reviewed fixed run")
    w1, w2 = json.loads(w1_bytes), json.loads(w2_bytes)

    sys.path.insert(0, str(root / "work/tools"))
    from t66_parallel_protocol import validate_manifest

    w1_validation = validate_manifest(
        w1, repo_root=root, verify_snapshot=True,
        verify_original_inputs=False, verify_source_bytes=False,
    )
    w2_validation = validate_manifest(
        w2, repo_root=root, verify_snapshot=True,
        verify_original_inputs=False, verify_source_bytes=False,
    )
    if w2.get("waveNumber") != 2 or w2.get("parentWave", {}).get("manifestSha256") != W1_SHA:
        raise ValueError("wave-2 parent linkage mismatch")
    correction_path = base / "wave-2/prelaunch-correction-r2.json"
    correction = read(correction_path) if correction_path.is_file() else None
    if correction:
        archived_path = root / correction["initialManifestPath"]
        if (
            correction.get("correctedRunId") != w2.get("runId")
            or correction.get("correctedManifestSha256") != sha_bytes(w2_bytes)
            or not archived_path.is_file()
            or sha_file(archived_path) != correction.get("initialManifestSha256")
            or correction.get("initialRunId") != "T66-W2-20261004-9f5926a80312"
            or w2.get("manifestRevision") != 2
        ):
            raise ValueError("wave-2 prelaunch correction chain is inconsistent")
    elif w2.get("runId") != "T66-W2-20261004-9f5926a80312":
        raise ValueError("unexpected wave-2 run identity; no audited correction record")

    assign = w2["assignments"]
    for worker in ("A", "B", "C", "F"):
        if assign[worker].get("outputAccess") != "read_only_carry_forward":
            raise ValueError(f"{worker} is not read-only in wave-2")
    for worker in ("D", "E"):
        if assign[worker].get("outputAccess") != "write":
            raise ValueError(f"{worker} does not own its wave-2 output")
        if assign[worker].get("assignedTargetIds") or assign[worker].get("assignedMembershipKeys"):
            raise ValueError(f"{worker} assignment improperly promotes target/membership scope")
        for ref in assign[worker].get("targetContextRefs", []):
            if ref.get("use") != "context_only_not_an_accepted_target_or_membership_binding":
                raise ValueError(f"{worker} target context is not explicitly non-authoritative")

    expected_counts = {"D": 16, "E": 66}
    work_ids: dict[str, set[str]] = {}
    source_ids: dict[str, set[str]] = {}
    for worker in ("A", "B", "C", "D", "E", "F"):
        rows = assign[worker].get("assignedWorkKeys", [])
        rows = rows if isinstance(rows, list) else []
        work_ids[worker] = {
            row if isinstance(row, str) else row.get("workKeyId")
            for row in rows
        }
        work_ids[worker].discard(None)
        source_ids[worker] = set(assign[worker].get("assignedSourceKeys", []))
    if len(work_ids["D"]) != expected_counts["D"] or len(work_ids["E"]) != expected_counts["E"]:
        raise ValueError(f"D/E exact work-key counts changed: D={len(work_ids['D'])}, E={len(work_ids['E'])}")
    if work_ids["D"] & work_ids["E"] or source_ids["D"] & source_ids["E"]:
        raise ValueError("D/E work or source assignment overlaps")

    names = set()
    for row in assign["D"].get("assignedWorkKeys", []):
        names.add(row.get("sourceName", ""))
    w1_src = {row["sourceKey"]: row for row in w1["sourceDisposition"]}
    d_names_actual = {
        w1_src[key]["sourceName"].rsplit(".", 1)[0]
        for key in source_ids["D"]
    }
    if d_names_actual != D_NAMES:
        raise ValueError(f"D exact concept set mismatch: {sorted(d_names_actual)}")
    d_bones = assign["D"].get("assignedBoneSourceKeys", [])
    e_bones = assign["E"].get("assignedBoneSourceKeys", [])
    if len(d_bones) != 1 or len(e_bones) != 16 or set(d_bones) & set(e_bones):
        raise ValueError("D/E typed bone-context assignment counts or overlap differ")

    owner_ids: dict[str, str] = {}
    for worker, ids in work_ids.items():
        for item in ids:
            if item in owner_ids:
                raise ValueError(f"work key assigned twice: {item}")
            owner_ids[item] = worker
    scope_rows = w2.get("sourceActionScopeQueue", [])
    assigned_scope = {row["workKeyId"] for row in scope_rows if row.get("disposition") == "assigned"}
    deferred_scope = {row["workKeyId"] for row in scope_rows if row.get("disposition") != "assigned"}
    if assigned_scope != set(owner_ids):
        raise ValueError("manifest scope queue and six worker assignments differ")
    if len(assigned_scope) != 500 or len(deferred_scope) != 60 or assigned_scope & deferred_scope:
        raise ValueError(f"wave-2 scope totals differ: assigned={len(assigned_scope)}, deferred={len(deferred_scope)}")

    registration_path = root / "atlas-data/motion/t66-wave1-registration.json"
    registration = read(registration_path)
    package_rows = registration.get("packages", [])
    unique_assets: dict[str, dict] = {}
    for package in package_rows:
        uri = package["uri"]
        prior = unique_assets.get(uri)
        if prior and prior["sha256"] != package["sha256"]:
            raise ValueError(f"duplicate URI with conflicting content hash: {uri}")
        unique_assets[uri] = package
    asset_checks = []
    for uri, package in sorted(unique_assets.items()):
        path = root / uri
        if path.is_symlink() or not path.is_file():
            raise FileNotFoundError(f"registered motion asset missing or symlinked: {uri}")
        digest = sha_file(path)
        size = path.stat().st_size
        if digest != package["sha256"]:
            raise ValueError(f"registered motion asset hash mismatch: {uri}")
        if registration.get("authority", {}).get("sourceOnly") is not True:
            raise ValueError("wave-1 registration sourceOnly state changed")
        asset_checks.append({"uri": uri, "sha256": digest, "bytes": size})
    if len(unique_assets) != 28 or len({x["sha256"] for x in asset_checks}) != 28:
        raise ValueError(f"expected 28 unique registered wave-1 GLBs, got {len(unique_assets)}")

    preflight_results = []
    negative_result = None
    if args.run_preflight:
        copied_runner = root / w2["workerToolSnapshots"][0]["snapshotPath"]
        snapshot_files = (root / w2["snapshotRoot"] / "files").resolve()
        for worker in ("D", "E"):
            out = root / assign[worker]["outputRoot"]
            if out.exists() and any(out.iterdir()):
                raise FileExistsError(f"refusing to reuse non-empty assigned output root: {out}")
            cmd = [sys.executable, str(copied_runner), "--repo-root", str(root), "--manifest", str(w2_path), "--input-root", str(snapshot_files), "--output-root", str(out), "--assignment", worker, "--preflight-only"]
            done = subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=False)
            if done.returncode != 0:
                raise RuntimeError(f"{worker} preflight failed (rc={done.returncode})\nstdout:\n{done.stdout}\nstderr:\n{done.stderr}")
            result = json.loads(done.stdout)
            if result.get("status") != "wave2_worker_preflight_passed_without_authoring" or result.get("geometryAuthored") is not False or result.get("outputProbeRemoved") is not True:
                raise ValueError(f"{worker} preflight did not stay authoring-free: {result}")
            preflight_results.append({"assignment": worker, "command": cmd, "result": result, "stderr": done.stderr})

        out_a = root / assign["A"]["outputRoot"]
        if out_a.exists():
            raise FileExistsError("read-only A output path exists before negative write-boundary check")
        cmd = [sys.executable, str(copied_runner), "--repo-root", str(root), "--manifest", str(w2_path), "--input-root", str(snapshot_files), "--output-root", str(out_a), "--assignment", "A", "--preflight-only"]
        denied = subprocess.run(cmd, cwd=root, text=True, capture_output=True)
        if denied.returncode == 0 or "read-only carry-forward" not in denied.stderr or out_a.exists():
            raise ValueError(f"read-only carry-forward write attempt was not rejected before output creation: rc={denied.returncode}; stderr={denied.stderr}")
        negative_result = {"assignment": "A", "returnCode": denied.returncode, "stderr": denied.stderr.strip(), "outputPathCreated": out_a.exists()}

    result = {
        "schemaVersion": "t66-wave2-freeze-validation-v1",
        "wave1": {
            "runId": w1["runId"], "rawManifestSha256": sha_bytes(w1_bytes),
            "validation": w1_validation,
        },
        "wave2": {
            "runId": w2["runId"], "rawManifestSha256": sha_bytes(w2_bytes),
            "baselineHead": w2["baselineHead"], "validation": w2_validation,
            "exactAssignments": {"D": {"workKeys": len(work_ids["D"]), "sourceKeys": len(source_ids["D"]), "boneContextSources": len(d_bones)}, "E": {"workKeys": len(work_ids["E"]), "sourceKeys": len(source_ids["E"]), "boneContextSources": len(e_bones)}, "otherDeferredWorkKeys": len(deferred_scope), "assignedWorkKeysAcrossAtoF": len(assigned_scope)},
            "readOnlyCarryForward": {worker: assign[worker]["outputAccess"] for worker in ("A", "B", "C", "F")},
            "writableOwners": {worker: assign[worker]["outputRoot"] for worker in ("D", "E")},
            "assignmentNoTargetOrMembershipPromotion": all(not assign[worker].get("assignedTargetIds") and not assign[worker].get("assignedMembershipKeys") for worker in ("D", "E")),
            "authority": w2["wave2Authority"],
            "promptFiles": w2["promptFiles"],
            "preflightResults": preflight_results,
            "readOnlyNegativeCheck": negative_result,
        },
        "wave1Registration": {
            "path": registration_path.relative_to(root).as_posix(),
            "sha256": sha_file(registration_path),
            "packageSelectorRows": len(registration.get("selectors", [])),
            "packageTemplates": len(package_rows),
            "uniqueGlbUris": len(unique_assets), "uniqueGlbSha256": len({x["sha256"] for x in asset_checks}),
            "uniqueGlbBytes": sum(x["bytes"] for x in asset_checks),
            "assetChecks": asset_checks,
            "authority": registration.get("authority"),
        },
    }
    if args.output:
        output = args.output if args.output.is_absolute() else root / args.output
        if output.exists() or output.is_symlink():
            raise FileExistsError(f"refusing to overwrite validation evidence: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"valid": True, "wave1RunId": w1["runId"], "wave2RunId": w2["runId"], "d": result["wave2"]["exactAssignments"]["D"], "e": result["wave2"]["exactAssignments"]["E"], "deferred": len(deferred_scope), "registeredUniqueGlbs": len(unique_assets), "registeredGlbBytes": result["wave1Registration"]["uniqueGlbBytes"], "preflights": len(preflight_results), "readOnlyNegativeCheck": bool(negative_result)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
