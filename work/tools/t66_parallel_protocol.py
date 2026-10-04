#!/usr/bin/env python3
"""Shared validation primitives for the T66 wave candidate protocol.

This protocol freezes inputs and output ownership only. It does not approve
anatomy, learner binding, human review, public rights, or app registration.
"""
from __future__ import annotations

import hashlib
import json
import re
import copy
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "t66-parallel-wave-v1"
RIGHTS_STATE = {
    "sourceOnly": True,
    "publicRedistribution": "held",
    "humanReview": "not_performed",
    "canonicalBindingAdded": False,
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def inside(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def work_key_id(key: dict[str, Any]) -> str:
    required = ("family", "side", "action", "sourceKey", "part", "poseContractRevision")
    if any(name not in key for name in required):
        raise ValueError(f"work key must explicitly contain {required}")
    if not isinstance(key["family"], str) or not key["family"].strip():
        raise ValueError("work key family must be a nonempty string")
    if not isinstance(key["sourceKey"], str) or not key["sourceKey"].strip():
        raise ValueError("work key sourceKey must be a nonempty exact source reference")
    if not isinstance(key["poseContractRevision"], str) or not key["poseContractRevision"].strip():
        raise ValueError("work key poseContractRevision must be explicit")
    for field in ("side", "action", "part"):
        if key[field] is not None and (not isinstance(key[field], str) or not key[field].strip()):
            raise ValueError(f"work key {field} must be null or a nonempty string")
    return "T66-WK-" + sha_bytes(canonical_json({field: key[field] for field in required}))[:24]


def apply_writer_correction(manifest: dict[str, Any], receipt: dict[str, Any], *, manifest_file_sha256: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply a narrow, hash-pinned ownership-metadata correction to a copy.

    The frozen wave-2 manifest and worker assignment snapshots remain untouched.
    Only stale ownership fields duplicated inside D/E assignedWorkKeys rows are
    normalized to the already-frozen sourceActionScopeQueue and sourceDisposition.
    """
    if receipt.get("schemaVersion") != "t66-wave2-writer-correction-v1":
        raise ValueError("unsupported writer correction receipt")
    if manifest.get("waveNumber") != 2 or manifest.get("runId") != receipt.get("runId"):
        raise ValueError("writer correction is for another T66 wave/run")
    if manifest.get("manifestRevision") != receipt.get("manifestRevision"):
        raise ValueError("writer correction manifest revision mismatch")
    if manifest_file_sha256 != receipt.get("baseManifestFileSha256"):
        raise ValueError("writer correction base manifest file hash mismatch")

    original = copy.deepcopy(manifest)
    effective = copy.deepcopy(manifest)
    queue = {row["workKeyId"]: row for row in manifest.get("sourceActionScopeQueue", [])}
    source_rows = {row["sourceKey"]: row for row in manifest.get("sourceDisposition", [])}
    entry_by_id: dict[str, dict[str, Any]] = {}
    for entry in receipt.get("corrections", []):
        work_id = entry.get("workKeyId")
        if not isinstance(work_id, str) or work_id in entry_by_id:
            raise ValueError("writer correction contains missing/duplicate work key IDs")
        entry_by_id[work_id] = entry
    if receipt.get("correctionCount") != len(entry_by_id):
        raise ValueError("writer correction count does not match its entry list")

    expected_mismatches: dict[str, tuple[str, dict[str, Any], dict[str, Any], dict[str, Any]]] = {}
    for worker in ("D", "E"):
        record = manifest.get("assignments", {}).get(worker)
        if record is None:
            raise ValueError(f"writer correction run has no {worker} assignment")
        assigned_sources = set(record.get("assignedSourceKeys", []))
        for row in record.get("assignedWorkKeys", []):
            work_id = row.get("workKeyId")
            scope_row = queue.get(work_id)
            if scope_row is None:
                raise ValueError(f"assigned work key is absent from frozen source-action queue: {work_id}")
            if row.get("key") != scope_row.get("key") or work_key_id(row["key"]) != work_id:
                raise ValueError(f"writer correction found a changed exact work key: {work_id}")
            source_key = row["key"].get("sourceKey")
            source_row = source_rows.get(source_key)
            if source_row is None or source_key not in assigned_sources:
                raise ValueError(f"writer correction source is not in the assigned source inventory: {work_id}")
            if (scope_row.get("disposition"), scope_row.get("assignedTo"), scope_row.get("deferredTo")) != ("assigned", worker, None):
                raise ValueError(f"frozen source-action queue does not establish {worker} ownership: {work_id}")
            if (source_row.get("disposition"), source_row.get("assignedTo"), source_row.get("deferredTo")) != ("assigned", worker, None):
                raise ValueError(f"frozen source disposition does not establish {worker} ownership: {work_id}")
            before = {field: row.get(field) for field in ("disposition", "assignedTo", "deferredTo")}
            after = {field: scope_row.get(field) for field in ("disposition", "assignedTo", "deferredTo")}
            if before != after:
                expected_mismatches[work_id] = (worker, row, scope_row, source_row)

    if set(entry_by_id) != set(expected_mismatches):
        missing = sorted(set(expected_mismatches) - set(entry_by_id))
        extra = sorted(set(entry_by_id) - set(expected_mismatches))
        raise ValueError(f"writer correction mismatch universe changed; missing={missing[:3]} extra={extra[:3]}")

    patched = 0
    for work_id, (worker, before_row, scope_row, source_row) in expected_mismatches.items():
        entry = entry_by_id[work_id]
        if entry.get("assignment") != worker or entry.get("sourceKey") != before_row["key"]["sourceKey"]:
            raise ValueError(f"writer correction entry owner/source mismatch: {work_id}")
        if entry.get("assignmentRowSha256Before") != sha_bytes(canonical_json(before_row)):
            raise ValueError(f"writer correction assigned-row hash mismatch: {work_id}")
        if entry.get("exactKeySha256") != sha_bytes(canonical_json(before_row["key"])):
            raise ValueError(f"writer correction exact-key hash mismatch: {work_id}")
        if entry.get("scopeQueueRowSha256") != sha_bytes(canonical_json(scope_row)):
            raise ValueError(f"writer correction scope-row hash mismatch: {work_id}")
        if entry.get("sourceDispositionRowSha256") != sha_bytes(canonical_json(source_row)):
            raise ValueError(f"writer correction source-disposition hash mismatch: {work_id}")
        before = {field: before_row.get(field) for field in ("disposition", "assignedTo", "deferredTo")}
        after = {field: scope_row.get(field) for field in ("disposition", "assignedTo", "deferredTo")}
        if entry.get("before") != before or entry.get("after") != after:
            raise ValueError(f"writer correction owner transition mismatch: {work_id}")
        corrected_row = next(row for row in effective["assignments"][worker]["assignedWorkKeys"] if row["workKeyId"] == work_id)
        for field in ("disposition", "assignedTo", "deferredTo"):
            corrected_row[field] = after[field]
        if entry.get("assignmentRowSha256After") != sha_bytes(canonical_json(corrected_row)):
            raise ValueError(f"writer correction after-row hash mismatch: {work_id}")
        patched += 1

    return effective, {
        "applied": True,
        "revisionId": receipt.get("revisionId"),
        "baseManifestFileSha256": manifest_file_sha256,
        "originalManifestCanonicalSha256": sha_bytes(canonical_json(original)),
        "effectiveManifestCanonicalSha256": sha_bytes(canonical_json(effective)),
        "correctedAssignmentRows": patched,
        "byAssignment": {worker: sum(1 for entry in receipt["corrections"] if entry["assignment"] == worker) for worker in ("D", "E")},
        "frozenManifestMutated": False,
        "workerSnapshotsMutated": False,
    }


def assigned_bone_context(record: dict[str, Any], source_keys: list[str] | None = None) -> dict[str, Any]:
    """Return a typed, read-only bone context distinct from muscle members."""
    allowed = set(record.get("assignedBoneSourceKeys", []))
    selected = list(record.get("assignedBoneSourceKeys", [])) if source_keys is None else list(source_keys)
    if len(selected) != len(set(selected)) or not set(selected) <= allowed:
        raise ValueError("read-only bone context contains duplicate or unassigned source keys")
    return {
        "contextType": "t66_assigned_bone_source_context",
        "sourceKeys": selected,
        "accessMode": "read_only_context",
        "candidateMuscleMember": False,
        "independentDofGranted": False,
    }


def validate_assigned_bone_context(context: dict[str, Any], record: dict[str, Any]) -> None:
    expected = assigned_bone_context(record, context.get("sourceKeys", []))
    if context != expected:
        raise ValueError("typed bone context is not a read-only subset of assignedBoneSourceKeys")
    if set(context.get("sourceKeys", [])) & set(record.get("assignedSourceKeys", [])):
        # The same provider key must never silently change semantic roles in a package.
        raise ValueError("bone context source keys overlap assigned muscle source keys")


def validate_schema_instance(value: Any, schema: dict[str, Any], location: str = "$" ) -> None:
    """Validate the JSON Schema keywords intentionally used by the T66 package contract."""
    expected_type = schema.get("type")
    if expected_type is not None:
        types = expected_type if isinstance(expected_type, list) else [expected_type]
        checks = {
            "object": lambda v: isinstance(v, dict),
            "array": lambda v: isinstance(v, list),
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "null": lambda v: v is None,
        }
        if not any(kind in checks and checks[kind](value) for kind in types):
            raise ValueError(f"{location}: expected type {types}")
    if "const" in schema and value != schema["const"]:
        raise ValueError(f"{location}: value differs from schema const")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{location}: value is outside schema enum")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise ValueError(f"{location}: string shorter than minLength")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            raise ValueError(f"{location}: string does not match pattern")
        if schema.get("format") == "date-time":
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError(f"{location}: invalid date-time") from exc
            if parsed.tzinfo is None:
                raise ValueError(f"{location}: date-time must include a timezone")
    if isinstance(value, (int, float)) and not isinstance(value, bool) and value < schema.get("minimum", float("-inf")):
        raise ValueError(f"{location}: number is below minimum")
    if isinstance(value, dict):
        required = schema.get("required", [])
        missing = [key for key in required if key not in value]
        if missing:
            raise ValueError(f"{location}: missing required properties {missing}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(value) - set(properties)
            if extra:
                raise ValueError(f"{location}: unexpected properties {sorted(extra)}")
        for key, child in value.items():
            child_schema = properties.get(key)
            if child_schema is not None:
                validate_schema_instance(child, child_schema, f"{location}.{key}")
    if isinstance(value, list):
        if schema.get("uniqueItems") and len({canonical_json(item) for item in value}) != len(value):
            raise ValueError(f"{location}: array items are not unique")
        child_schema = schema.get("items")
        if child_schema is not None:
            for index, item in enumerate(value):
                validate_schema_instance(item, child_schema, f"{location}[{index}]")


def validate_candidate_schema(package: dict[str, Any], manifest: dict[str, Any], repo_root: Path) -> None:
    schema_path = repo_root / manifest["workerOutputSchema"]
    schema_ref = next((item for item in manifest.get("inputs", []) if item.get("path") == manifest["workerOutputSchema"]), None)
    if schema_ref is None:
        raise ValueError("worker output schema is not pinned as an input")
    if not schema_path.is_file() or schema_path.is_symlink() or sha_file(schema_path) != schema_ref.get("sha256"):
        raise ValueError("current worker output schema differs from frozen schema hash")
    validate_schema_instance(package, read_json(schema_path))
    action_rows = package.get("actionWorkKeys", [])
    seen: set[str] = set()
    for row in action_rows:
        key = {field: row[field] for field in ("family", "side", "action", "sourceKey", "part", "poseContractRevision")}
        expected = work_key_id(key)
        if row.get("workKeyId") != expected:
            raise ValueError(f"candidate action work key hash mismatch: {row.get('workKeyId')}")
        if expected in seen:
            raise ValueError(f"candidate repeats exact action work key: {expected}")
        seen.add(expected)


def validate_work_key_rows(rows: list[dict[str, Any]]) -> None:
    ids: set[str] = set()
    tuples: set[bytes] = set()
    for row in rows:
        key = row.get("key")
        if not isinstance(key, dict):
            raise ValueError("work-key row missing key object")
        expected = work_key_id(key)
        if row.get("workKeyId") != expected:
            raise ValueError(f"work-key ID mismatch: {row.get('workKeyId')} != {expected}")
        encoded = canonical_json(key)
        if encoded in tuples:
            raise ValueError(f"duplicate full responsibility key: {key}")
        tuples.add(encoded)
        if expected in ids:
            raise ValueError(f"duplicate workKeyId: {expected}")
        ids.add(expected)


def validate_manifest(manifest: dict[str, Any], *, repo_root: Path | None = None, verify_snapshot: bool = True, verify_source_bytes: bool = False, verify_original_inputs: bool = True, assignment_snapshot_source: dict[str, Any] | None = None) -> dict[str, Any]:
    if manifest.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("unsupported T66 parallel manifest schema")
    if manifest.get("task") != "T66" or manifest.get("nextUnit") != "author-and-integrate-normal-motion-bone-and-nerve":
        raise ValueError("manifest does not pin the requested T66 nextUnit")
    if not re.fullmatch(r"[0-9a-f]{40}", str(manifest.get("baselineHead", ""))):
        raise ValueError("manifest baselineHead must be a full git hash")
    if manifest.get("authority") != RIGHTS_STATE:
        raise ValueError("authority state was promoted or changed")
    schema_path = manifest.get("workerOutputSchema")
    schema_input = next((item for item in manifest.get("inputs", []) if item.get("path") == schema_path), None)
    if not schema_input or manifest.get("workerOutputSchemaSha256") != schema_input.get("sha256"):
        raise ValueError("worker output schema hash is not bound to the pinned schema input")
    denominators = manifest.get("denominators", {})
    required_counts = {
        "productTargets": 542,
        "productMemberships": 563,
        "regions": 12,
        "muscleTargets": 429,
        "muscleMemberships": 447,
        "sourceConcepts": 232,
        "sourceSurfaceInstances": 462,
        "historical163": {"6": 6, "20": 20, "135": 135, "2": 2},
    }
    for key, expected in required_counts.items():
        if denominators.get(key) != expected:
            raise ValueError(f"denominator {key} expected {expected}, got {denominators.get(key)}")
    if len(manifest.get("targetDisposition", [])) != 542:
        raise ValueError("target disposition must cover exactly 542 target IDs")
    targets = manifest["targetDisposition"]
    target_ids = [row.get("targetId") for row in targets]
    if len(set(target_ids)) != 542 or any(not x for x in target_ids):
        raise ValueError("target IDs are missing or duplicated")
    if len(manifest.get("membershipDisposition", [])) != 563:
        raise ValueError("membership disposition must cover exactly 563 target-region keys")
    membership_keys = [row.get("membershipKey") for row in manifest["membershipDisposition"]]
    if len(set(membership_keys)) != 563 or any(not x for x in membership_keys):
        raise ValueError("membership keys are missing or duplicated")
    if len(manifest.get("sourceDisposition", [])) != 462:
        raise ValueError("source disposition must cover exactly 462 source surfaces")
    source_keys = [row.get("sourceKey") for row in manifest["sourceDisposition"]]
    if len(set(source_keys)) != 462 or any(not x for x in source_keys):
        raise ValueError("source keys are missing or duplicated")
    if len(manifest.get("boneContextDisposition", [])) != 210:
        raise ValueError("bone source disposition must cover 210 source rows")
    bone_keys = [row.get("sourceKey") for row in manifest["boneContextDisposition"]]
    if len(set(bone_keys)) != 210 or any(not x for x in bone_keys):
        raise ValueError("bone source keys are missing or duplicated")
    if len(manifest.get("nerveTextDisposition", [])) != 98:
        raise ValueError("nerve text disposition must cover 98 source label rows")
    nerve_ids = [row.get("nerveRowId") for row in manifest["nerveTextDisposition"]]
    if len(set(nerve_ids)) != 98 or any(not x for x in nerve_ids):
        raise ValueError("nerve row IDs are missing or duplicated")

    workers = manifest.get("assignments", {})
    wave_number = manifest.get("waveNumber", 1)
    if wave_number == 1:
        expected_workers = {"A", "B", "C", "F"}
    elif wave_number == 2:
        expected_workers = {"A", "B", "C", "D", "E", "F"}
    else:
        raise ValueError(f"unsupported T66 wave number: {wave_number}")
    if set(workers) != expected_workers:
        raise ValueError(f"wave-{wave_number} must contain exactly {sorted(expected_workers)}")
    all_work_ids: set[str] = set()
    all_assigned_sources: dict[str, str] = {}
    all_targets: dict[str, str] = {}
    all_memberships: dict[str, str] = {}
    all_nerve: dict[str, str] = {}
    for worker, record in workers.items():
        rows = record.get("assignedWorkKeys", [])
        validate_work_key_rows(rows)
        for row in rows:
            if row["workKeyId"] in all_work_ids:
                raise ValueError(f"work key assigned more than once: {row['workKeyId']}")
            all_work_ids.add(row["workKeyId"])
        for field, seen, label in (
            ("assignedSourceKeys", all_assigned_sources, "sourceKey"),
            ("assignedTargetIds", all_targets, "targetId"),
            ("assignedMembershipKeys", all_memberships, "membershipKey"),
            ("assignedNerveRowIds", all_nerve, "nerveRowId"),
        ):
            for value in record.get(field, []):
                if value in seen:
                    raise ValueError(f"{label} assigned twice: {value} ({seen[value]}, {worker})")
                seen[value] = worker
        if record.get("outputRoot") is None:
            raise ValueError(f"{worker} missing outputRoot")

    assigned_work_set = set()
    for owner, record in workers.items():
        assigned_work_set.update(row["workKeyId"] for row in record.get("assignedWorkKeys", []))
    planned_work = manifest.get("sourceActionScopeQueue", [])
    validate_work_key_rows(planned_work)
    planned_by_id = {row["workKeyId"]: row for row in planned_work}
    planned_assigned = {r["workKeyId"] for r in planned_work if r.get("disposition") == "assigned"}
    if planned_assigned != assigned_work_set:
        raise ValueError("worker assignedWorkKeys do not equal the explicitly assigned source-action scope queue")
    assignment_owner = {r["workKeyId"]: r.get("assignedTo") for r in planned_work if r.get("disposition") == "assigned"}
    for worker, record in workers.items():
        for row in record.get("assignedWorkKeys", []):
            work_id = row["workKeyId"]
            if assignment_owner.get(work_id) != worker:
                raise ValueError(f"{worker} contains a work key owned by another assignment")
            planned = planned_by_id[work_id]
            for field in ("disposition", "assignedTo", "deferredTo"):
                if field in row and row.get(field) != planned.get(field):
                    raise ValueError(f"{worker} embedded owner metadata differs from source-action queue for {work_id}: {field}")

    def verify_disposition(items: list[dict[str, Any]], key: str, allowed: set[str], expected: set[str], name: str, assigned_field: str | None = None) -> None:
        owned: dict[str, str] = {}
        for row in items:
            item = row.get(key)
            disposition = row.get("disposition")
            owner = row.get("assignedTo")
            if disposition not in allowed:
                raise ValueError(f"invalid {name} disposition for {item}: {disposition}")
            if disposition == "assigned":
                if owner not in expected_workers:
                    raise ValueError(f"invalid {name} assigned owner for {item}: {owner}")
                if manifest.get("ownershipSemanticsRevision", 1) >= 2 and row.get("deferredTo") is not None:
                    raise ValueError(f"assigned {name} row also has deferredTo: {item}")
                if item in owned:
                    raise ValueError(f"duplicate {name} assignment: {item}")
                owned[item] = owner
            else:
                if manifest.get("ownershipSemanticsRevision", 1) >= 2 and owner is not None:
                    raise ValueError(f"deferred {name} row cannot be assignedTo: {item}")
                if not row.get("reason"):
                    raise ValueError(f"deferred {name} row needs an exact reason: {item}")
                if manifest.get("ownershipSemanticsRevision", 1) >= 2 and row.get("deferredTo") not in {"D", "E", "integrationWriter"}:
                    raise ValueError(f"deferred {name} row needs explicit D/E/writer destination: {item}")
        actual = {row.get(key) for row in items}
        if len(actual) != len(items) or actual != expected:
            raise ValueError(f"{name} disposition universe mismatch")
        default_fields = {"targetId": "assignedTargetIds", "membershipKey": "assignedMembershipKeys", "sourceKey": "assignedSourceKeys", "nerveRowId": "assignedNerveRowIds"}
        field = assigned_field or default_fields[key]
        assigned_lists = set().union(*(set(workers[w].get(field, [])) for w in expected_workers))
        if assigned_lists != set(owned):
            raise ValueError(f"{name} assigned disposition and assignment lists differ")
        for worker, record in workers.items():
            for value in record.get(field, []):
                if owned.get(value) != worker:
                    raise ValueError(f"{name} assignment owner differs from disposition: {value}")

    verify_disposition(targets, "targetId", {"assigned", "deferred", "outside_motion_scope"}, set(target_ids), "target")
    verify_disposition(manifest["membershipDisposition"], "membershipKey", {"assigned", "deferred", "outside_motion_scope"}, set(membership_keys), "membership")
    verify_disposition(manifest["sourceDisposition"], "sourceKey", {"assigned", "deferred", "unsupported_evidence"}, set(source_keys), "source")
    verify_disposition(manifest["boneContextDisposition"], "sourceKey", {"assigned", "deferred", "unsupported_evidence"}, set(bone_keys), "bone context", "assignedBoneSourceKeys")
    verify_disposition(manifest["nerveTextDisposition"], "nerveRowId", {"assigned", "deferred", "unsupported_evidence"}, set(nerve_ids), "nerve text")

    refs = manifest.get("sourceResourceRefs", [])
    ref_ids = [f"{r.get('sourceKey')}::{r.get('lod')}" for r in refs]
    if len(ref_ids) != len(set(ref_ids)):
        raise ValueError("duplicate source resource reference")
    if repo_root is not None:
        root = repo_root.resolve()
        compiled_ref = next((item for item in manifest.get("inputs", []) if item.get("path") == "atlas-data/source-cache/datasets/za/compiled/manifest.json"), None)
        if compiled_ref is None:
            raise ValueError("compiled source manifest is not pinned")
        compiled_path = root / (compiled_ref["snapshotPath"] if verify_snapshot else compiled_ref["path"])
        compiled_data = read_json(compiled_path)
        compiled_by_source = {row.get("sourceKey"): row for row in compiled_data.get("instances", []) if row.get("sourceKey")}
        expected_resource_refs: set[tuple[str, str, str, int, str, str | None]] = set()
        for disposition in manifest["sourceDisposition"]:
            source_key = disposition["sourceKey"]
            compiled_row = compiled_by_source.get(source_key)
            if compiled_row is None:
                raise ValueError(f"source disposition absent from frozen compiled manifest: {source_key}")
            for lod, detail in compiled_row.get("lods", {}).items():
                resource = detail["resource"]
                expected_resource_refs.add((source_key, lod, f"atlas-data/source-cache/datasets/za/resources/{resource}.glb",
                                            detail["bytes"], detail["sha256"], detail.get("chunk")))
        actual_resource_refs = {
            (row.get("sourceKey"), row.get("lod"), row.get("path"), row.get("bytes"), row.get("sha256"), row.get("geometryChunkSha256"))
            for row in refs
        }
        if actual_resource_refs != expected_resource_refs:
            raise ValueError("source resource refs do not exactly match frozen compiled instances for the 462 source surfaces")
        refs_by_hash: dict[str, list[dict[str, Any]]] = {}
        for row in refs:
            refs_by_hash.setdefault(row.get("sha256"), []).append(row)
        declared_unique = {row.get("sha256"): row for row in manifest.get("sourceResourceHashesUnique", [])}
        if set(declared_unique) != set(refs_by_hash) or any(
            item.get("bytes") != refs_by_hash[digest][0].get("bytes")
            or item.get("path") not in {row.get("path") for row in refs_by_hash[digest]}
            for digest, item in declared_unique.items()
        ):
            raise ValueError("unique source resource inventory differs from per-source refs")
        for item in manifest.get("inputs", []):
            original = root / item["path"]
            if verify_original_inputs:
                if not original.is_file() or original.is_symlink():
                    raise ValueError(f"pinned input missing or symlinked: {item['path']}")
                if original.stat().st_size != item["bytes"] or sha_file(original) != item["sha256"]:
                    raise ValueError(f"pinned input changed: {item['path']}")
            if verify_snapshot:
                snap = root / item["snapshotPath"]
                if not snap.is_file() or snap.is_symlink():
                    raise ValueError(f"snapshot missing or symlinked: {item['snapshotPath']}")
                if snap.stat().st_size != item["bytes"] or sha_file(snap) != item["sha256"]:
                    raise ValueError(f"snapshot changed: {item['snapshotPath']}")
        control_paths = {"work/NEXT.md", "work/EXECUTION.json"}
        controls = manifest.get("controlContextSnapshots", [])
        if {item.get("path") for item in controls} != control_paths:
            raise ValueError("task control context snapshots are incomplete")
        if verify_snapshot:
            for item in controls:
                snap = root / item["snapshotPath"]
                if not snap.is_file() or snap.is_symlink() or snap.stat().st_size != item["bytes"] or sha_file(snap) != item["sha256"]:
                    raise ValueError(f"control context snapshot missing or changed: {item['snapshotPath']}")
        if verify_source_bytes:
            for item in refs:
                source = root / item["path"]
                if not source.is_file() or source.is_symlink():
                    raise ValueError(f"source resource missing or symlinked: {item['path']}")
                if source.stat().st_size != item["bytes"] or sha_file(source) != item["sha256"]:
                    raise ValueError(f"source resource changed: {item['path']}")
        wave_root = (root / manifest["manifestPath"]).parent
        for worker, record in workers.items():
            output = root / record["outputRoot"]
            if not inside(output, wave_root / "workers" / worker):
                raise ValueError(f"{worker} output root escapes its owned directory")
        snapshot_manifest = assignment_snapshot_source or manifest
        snapshot_workers = snapshot_manifest.get("assignments", {})
        for item in manifest.get("assignmentSnapshots", []):
            path = root / item["path"]
            if not path.is_file() or path.is_symlink():
                raise ValueError(f"assignment snapshot missing or symlinked: {item['path']}")
            if path.stat().st_size != item["bytes"] or sha_file(path) != item["sha256"]:
                raise ValueError(f"assignment snapshot changed: {item['path']}")
            snapshot = read_json(path)
            worker = item.get("assignment")
            record = snapshot_workers.get(worker)
            if record is None or snapshot.get("runId") != manifest.get("runId") or snapshot.get("assignment") != worker:
                raise ValueError(f"assignment snapshot run/owner mismatch: {item['path']}")
            for field in ("assignedWorkKeys", "assignedSourceKeys", "assignedTargetIds", "assignedMembershipKeys", "assignedBoneSourceKeys", "assignedNerveRowIds"):
                if snapshot.get(field) != record.get(field):
                    raise ValueError(f"assignment snapshot differs from manifest field {field}: {item['path']}")
        dry = root / manifest["writerDryRun"]["outputRoot"]
        if not inside(dry, wave_root / "writer-dry-run"):
            raise ValueError("writer dry-run output escapes its owned directory")
    return {
        "valid": True,
        "manifestSha256": sha_bytes(canonical_json(manifest)),
        "counts": {
            "targets": len(targets),
            "memberships": len(membership_keys),
            "sourceSurfaces": len(source_keys),
            "boneSources": len(bone_keys),
            "nerveRows": len(nerve_ids),
            "workKeys": len(planned_work),
            "assignedWorkKeys": len(assigned_work_set),
            "sourceResourceRefs": len(refs),
        },
    }
