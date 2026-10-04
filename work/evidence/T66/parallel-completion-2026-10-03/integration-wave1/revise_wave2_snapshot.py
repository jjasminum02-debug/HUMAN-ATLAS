#!/usr/bin/env python3
"""Preserve the first wave-2 freeze and publish a corrected pre-launch revision."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[5]
W2 = ROOT / "work/evidence/T66/parallel-completion-2026-10-03/wave-2"
LIVE_RUNNER = ROOT / "work/tools/run_t66_parallel_candidate.py"
LIVE_PROTOCOL = ROOT / "work/tools/t66_parallel_protocol.py"


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def replace_prefix(value: Any, old: str, new: str) -> Any:
    if isinstance(value, str):
        return value.replace(old, new)
    if isinstance(value, list):
        return [replace_prefix(item, old, new) for item in value]
    if isinstance(value, dict):
        return {key: replace_prefix(item, old, new) for key, item in value.items()}
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    manifest_path = W2 / "run-manifest.json"
    raw = manifest_path.read_bytes()
    initial = json.loads(raw)
    old_hash = sha_bytes(raw)
    archive = W2 / "run-manifest-r1-preflight-failed.json"
    snapshot_old = W2 / "input-snapshot"
    snapshot_new = W2 / "input-snapshot-r2"
    if archive.exists() or snapshot_new.exists():
        raise FileExistsError("wave-2 correction artifacts already exist; refusing to overwrite")
    if not snapshot_old.is_dir() or snapshot_old.is_symlink():
        raise FileNotFoundError(snapshot_old)
    if not LIVE_RUNNER.is_file() or LIVE_RUNNER.is_symlink() or not LIVE_PROTOCOL.is_file() or LIVE_PROTOCOL.is_symlink():
        raise FileNotFoundError("live writer runner/protocol is missing or symlinked")

    shutil.copyfile(manifest_path, archive)
    shutil.copytree(snapshot_old, snapshot_new, symlinks=False)
    runner_snap = snapshot_new / "tools/run_t66_parallel_candidate.py"
    protocol_snap = snapshot_new / "tools/t66_parallel_protocol.py"
    shutil.copyfile(LIVE_RUNNER, runner_snap)
    shutil.copyfile(LIVE_PROTOCOL, protocol_snap)

    old_prefix = snapshot_old.relative_to(ROOT).as_posix()
    new_prefix = snapshot_new.relative_to(ROOT).as_posix()
    revised = replace_prefix(initial, old_prefix, new_prefix)
    revised["manifestRevision"] = 2
    revised["supersedesManifestSha256"] = old_hash
    revised["preLaunchCorrection"] = "runner schema canary referenced validate_schema_instance without importing it; corrected snapshot imports the frozen protocol validator"
    revised["runId"] = f"T66-W2-20261004-r2-{sha_file(runner_snap)[:12]}"

    for ref in revised.get("workerToolSnapshots", []):
        path = ROOT / ref["snapshotPath"]
        ref["bytes"] = path.stat().st_size
        ref["sha256"] = sha_file(path)
    for ref in revised.get("assignmentSnapshots", []):
        path = ROOT / ref["path"]
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        snapshot["runId"] = revised["runId"]
        write_json(path, snapshot)
        ref["bytes"] = path.stat().st_size
        ref["sha256"] = sha_file(path)
    for ref in revised.get("controlContextSnapshots", []):
        path = ROOT / ref["snapshotPath"]
        ref["bytes"] = path.stat().st_size
        ref["sha256"] = sha_file(path)

    index_path = ROOT / revised["snapshotIndexPath"]
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["runId"] = revised["runId"]
    index["wave2SnapshotRoot"] = new_prefix
    index["workerToolSnapshots"] = revised.get("workerToolSnapshots", [])
    index["controlSnapshots"] = revised.get("controlContextSnapshots", [])
    index["assignmentSnapshots"] = revised.get("assignmentSnapshots", [])
    index["workerOutputSchema"] = {
        "path": revised["workerOutputSchema"],
        "sha256": revised["workerOutputSchemaSha256"],
        "bytes": next(x["bytes"] for x in revised["inputs"] if x["path"] == revised["workerOutputSchema"]),
    }
    write_json(index_path, index)

    # The generated schema is copied byte-for-byte; refresh its snapshot binding after path relocation.
    schema_ref = next(x for x in revised["inputs"] if x["path"] == revised["workerOutputSchema"])
    schema_path = ROOT / schema_ref["snapshotPath"]
    schema_ref["bytes"] = schema_path.stat().st_size
    schema_ref["sha256"] = sha_file(schema_path)
    revised["workerOutputSchemaSha256"] = schema_ref["sha256"]
    index["workerOutputSchema"] = {"path": revised["workerOutputSchema"], "sha256": schema_ref["sha256"], "bytes": schema_ref["bytes"]}
    write_json(index_path, index)

    write_json(manifest_path, revised)
    correction = {
        "schemaVersion": "t66-wave2-prelaunch-correction-v1",
        "initialRunId": initial["runId"],
        "initialManifestPath": archive.relative_to(ROOT).as_posix(),
        "initialManifestSha256": old_hash,
        "correctedRunId": revised["runId"],
        "correctedManifestPath": manifest_path.relative_to(ROOT).as_posix(),
        "correctedManifestSha256": sha_file(manifest_path),
        "initialSnapshotRoot": old_prefix,
        "correctedSnapshotRoot": new_prefix,
        "runnerSnapshotSha256": sha_file(runner_snap),
        "protocolSnapshotSha256": sha_file(protocol_snap),
        "cause": "D preflight exposed NameError: validate_schema_instance was not imported by the candidate runner.",
        "scope": "No A/B/C/F input or output was modified; no D/E candidate authoring started. The original manifest and snapshot remain preserved.",
    }
    write_json(W2 / "prelaunch-correction-r2.json", correction)
    print(json.dumps(correction, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
