#!/usr/bin/env python3
"""Freeze T66 wave-1 inputs and explicit A/B/C/F work ownership.

This creates a bounded worker snapshot and a reviewable manifest. It never
downloads or copies source geometry and never changes the learner runtime.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from t66_parallel_protocol import (
    RIGHTS_STATE,
    SCHEMA_VERSION,
    canonical_json,
    read_json,
    sha_bytes,
    sha_file,
    validate_manifest,
    work_key_id,
)

MANIFEST_REL = Path("work/evidence/T66/parallel-completion-2026-10-03/wave-1/run-manifest.json")
SNAPSHOT_REL = MANIFEST_REL.parent / "input-snapshot"
POSE_REVISION = "all-muscle-motion-2026-10-02"
MUSCLE_KINDS = {"named_muscle", "muscle_part", "muscle_group", "repeated_muscle_family", "muscle_complex"}
LOWER = {"gluteal-hip", "thigh", "leg", "foot"}
AXIAL = {"neck", "back", "thorax", "abdomen-lumbar"}
HAND_TOKENS = re.compile(r"\b(hand|finger|thumb|digit\w*|thenar\w*|hypothenar\w*|metacarp\w*|phalang\w*|lumbrical\w*|interosse\w*|pollic\w*|digiti\w*|hallucis\w*|pedis\w*)\b", re.I)
CARPAL_TOKENS = re.compile(r"\b(carpal|capitate|hamate|lunate|pisiform|scaphoid|trapezium|trapezoid|triquetrum)\b", re.I)
JAW_TOKENS = re.compile(r"\b(jaw|mandib|hyoid|laryn|pharyn|laryngeal|pharyngeal)\b", re.I)


def load(root: Path, rel: str) -> Any:
    path = root / rel
    if not path.is_file() or path.is_symlink():
        raise FileNotFoundError(f"required regular input missing: {rel}")
    return read_json(path)


def git_head(root: Path) -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, text=True, capture_output=True).stdout.strip()


def git_dirty_snapshot(root: Path) -> list[dict[str, Any]]:
    baseline_path = root / "work/evidence/T66/parallel-completion-2026-10-03/start-baseline.json"
    if baseline_path.exists():
        base = read_json(baseline_path)
        result = []
        for item in base.get("dirtyPaths", []):
            result.append({"path": item.get("path"), "kind": item.get("kind"), "sha256": item.get("sha256"), "bytes": item.get("bytes")})
        return result
    raise FileNotFoundError("the T66 start baseline must be recorded before wave snapshot creation")


def source_owner(target: dict[str, Any]) -> tuple[str, str]:
    owner = target.get("primaryOwner")
    english = str((target.get("term") or {}).get("english") or "")
    latin = str((target.get("term") or {}).get("latin") or "")
    label = f"{english} {latin}"
    if owner == "upper-limb" and HAND_TOKENS.search(label):
        return "A", "T96 upper-limb target with hand/digit concept token; assignment is scope, not a new source-target approval"
    if owner in LOWER:
        return "B", "T96 lower-limb primary owner"
    if owner in AXIAL:
        return "C", "T96 axial primary owner"
    if owner == "head" and JAW_TOKENS.search(label):
        return "D", "wave-2 jaw/hyoid/larynx/pharynx exact term scope"
    if owner == "head":
        return "E", "wave-2 eye/face/tongue/head exact primary owner; motion extent remains unverified"
    if owner == "pelvis-perineum":
        return "E", "wave-2 pelvic/perineal exact primary owner; source coverage remains separate"
    if owner in {"shoulder-scapular", "upper-limb"}:
        return "integrationWriter", "unit-03 residual upper-limb/shoulder scope remains with the common integration writer"
    return "integrationWriter", f"unclassified primary owner {owner!r}; no anatomical assignment inferred"


def json_snapshot(root: Path, snapshot_files: Path, rel: str, role: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    source = root / rel
    if not source.is_file() or source.is_symlink():
        raise FileNotFoundError(f"required snapshot input missing: {rel}")
    target = snapshot_files / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = source.read_bytes()
    if target.exists():
        if target.is_symlink() or not target.is_file() or target.read_bytes() != raw:
            raise ValueError(f"existing snapshot file conflicts with frozen source: {rel}")
    else:
        shutil.copyfile(source, target)
    ref = {"path": rel, "snapshotPath": str(target.relative_to(root)), "sha256": sha_bytes(raw), "bytes": len(raw), "role": role}
    rows.append(ref)
    return ref


def copy_reference(root: Path, snapshot_files: Path, rel: str, role: str, rows: list[dict[str, Any]], *, replace_existing: bool = False) -> dict[str, Any]:
    source = root / rel
    if not source.is_file() or source.is_symlink():
        raise FileNotFoundError(f"required frozen code/reference missing: {rel}")
    target = snapshot_files / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = source.read_bytes()
    if target.exists():
        if target.is_symlink() or not target.is_file():
            raise ValueError(f"existing code snapshot conflicts with frozen source: {rel}")
        if target.read_bytes() != raw and replace_existing:
            target.write_bytes(raw)
        elif target.read_bytes() != raw:
            raise ValueError(f"existing code snapshot conflicts with frozen source: {rel}")
    else:
        shutil.copyfile(source, target)
    ref = {"path": rel, "snapshotPath": str(target.relative_to(root)), "sha256": sha_bytes(raw), "bytes": len(raw), "role": role}
    rows.append(ref)
    return ref


def side_value(value: Any) -> str | None:
    return value if value in ("left", "right") else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument(
        "--refresh-owned-draft",
        action="store_true",
        help="archive and rebuild only this unlaunched task-owned draft; refuses if any worker/dry-run output exists",
    )
    args = parser.parse_args()
    root = args.repo_root.expanduser().resolve()
    manifest_path = root / MANIFEST_REL
    snapshot_root = root / SNAPSHOT_REL
    if manifest_path.exists():
        existing = read_json(manifest_path)
        result = validate_manifest(existing, repo_root=root, verify_snapshot=True, verify_source_bytes=False,
                                   verify_original_inputs=not args.refresh_owned_draft)
        if not args.refresh_owned_draft:
            print(json.dumps({"status": "reused_existing_frozen_run", "manifestPath": str(MANIFEST_REL), **result}, ensure_ascii=False, indent=2))
            return
        wave_root = manifest_path.parent
        output_roots = [root / rec["outputRoot"] for rec in existing.get("assignments", {}).values()]
        output_roots.append(root / existing["writerDryRun"]["outputRoot"])
        for output in output_roots:
            if output.exists() and (output.is_symlink() or not output.is_dir() or any(output.iterdir())):
                raise ValueError(f"cannot refresh draft after worker or writer output exists: {output}")
        archive_manifest = wave_root / "run-manifest-attempt-01.json"
        archive_snapshot = wave_root / "input-snapshot-attempt-01"
        archive_receipt = wave_root / "attempt-01-preservation.json"
        if snapshot_root.is_symlink() or not snapshot_root.is_dir():
            raise ValueError("cannot refresh without the existing regular task-owned input snapshot")
        archive_parts_exist = archive_manifest.exists() or archive_snapshot.exists() or archive_receipt.exists()
        if archive_parts_exist:
            if not (archive_manifest.is_file() and archive_snapshot.is_dir() and archive_receipt.is_file()):
                raise FileExistsError("attempt-01 archive is incomplete; refusing to overwrite or guess")
            receipt = read_json(archive_receipt)
            if receipt.get("archivedManifestSha256") != sha_file(manifest_path) or sha_file(archive_manifest) != receipt.get("archivedManifestSha256"):
                raise FileExistsError("attempt-01 archive belongs to a different draft; refusing to overwrite")
        else:
            shutil.copyfile(manifest_path, archive_manifest)
            shutil.copytree(snapshot_root, archive_snapshot)
            archive_receipt.write_text(json.dumps({
                "schemaVersion": "t66-parallel-draft-preservation-v1",
                "archivedManifestPath": str(archive_manifest.relative_to(root)),
                "archivedManifestSha256": sha_file(archive_manifest),
                "archivedSnapshotPath": str(archive_snapshot.relative_to(root)),
                "reason": "preserve the pre-worker task-owned draft before correcting its scope assignment and code-reference set",
                "workerOrDryRunOutputsFound": False,
            }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    required_inputs = [
        ("AGENTS.md", "repository instructions"),
        ("work/product-acceptance.json", "app acceptance contract"),
        ("work/tasks/T66-APP-COMPLETION.md", "T66 task specification"),
        ("design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md", "product acceptance design"),
        ("design/2026-09-25-muscle-atlas/28-ALL-MUSCLE-MOTION-PIPELINE.md", "all-muscle motion design"),
        ("work/plans/t66-parallel-completion-2026-10-03/README.md", "parallel handoff plan"),
        ("work/evidence/T35/motion-contract.json", "all-muscle motion contract"),
        ("atlas-data/catalog/target-scope-t96.json", "frozen product target scope"),
        ("atlas-data/overlays/za-local-integration.json", "current source/target candidate overlay"),
        ("atlas-data/source-cache/datasets/za/compiled/manifest.json", "source instances and immutable resource references"),
        ("work/evidence/T59/authoring-run-manifest-r2.json", "whole-muscle authoring denominator and source mapping"),
        ("work/evidence/T66/implementation-2026-10-02/family-queue.json", "current family/source work queue"),
        ("work/evidence/T66/implementation-2026-10-02/whole-target-motion-ledger.json", "429-target motion disposition"),
        ("work/evidence/T66/implementation-2026-10-02/whole-bone-motion-ledger.json", "whole-bone motion contexts"),
        ("work/evidence/T66/implementation-2026-10-02/nerve-course-and-entrapment-ledger.json", "nerve text/geometry state"),
        ("work/evidence/T66/serial-completion-2026-10-02/unit-01/serial-queue.json", "unit-01 actual work/result queue"),
        ("work/evidence/T66/serial-completion-2026-10-02/unit-02/serial-queue.json", "unit-02 actual work/result queue"),
        ("work/evidence/T66/serial-completion-2026-10-02/unit-03/serial-queue.json", "unit-03 actual work/result queue"),
        ("work/evidence/T66/serial-completion-2026-10-02/unit-03/action-scope-ledger.json", "unit-03 action/claim scope"),
        ("work/evidence/T66/serial-completion-2026-10-02/unit-03/continuation-2026-10-03/common-writer-checkpoint.json", "unit-03 writer checkpoint"),
        ("work/evidence/T66/implementation-2026-10-02/final-validation.json", "latest runtime validation"),
        ("work/evidence/T66/implementation-2026-10-02/final-blockers.json", "latest unresolved engineering/content gaps"),
        ("work/evidence/T66/serial-completion-2026-10-02/unit-02/validation.json", "unit-02 actual validation"),
        ("work/evidence/T66/serial-completion-2026-10-02/unit-02/candidate-interpolation-r1.json", "prior successful package interpolation QC"),
        ("work/evidence/T66/serial-completion-2026-10-02/unit-02/trials-r1/hip-flexion-left/contact-qc.json", "prior successful package contact QC"),
        ("work/evidence/T66/serial-completion-2026-10-02/unit-02/trials-r1/hip-flexion-left/glb-pose-qc.json", "prior successful emitted GLB pose QC"),
        ("atlas-data/motion/motion-learning.json", "current actual learner motion registry"),
        ("atlas-data/motion/authoring/registry.json", "current authoring registry"),
    ]
    control_context_paths = [
        ("work/NEXT.md", "captured task-routing projection; administrative context only"),
        ("work/EXECUTION.json", "captured T66 execution authority; administrative context only"),
    ]
    code_paths = [
        "work/tools/author_t66_family_motion.py",
        "work/tools/author_source_surface_motion.py",
        "work/tools/derive_source_surface_motion.py",
        "work/tools/source_surface_constraints.py",
        "work/tools/t66_contact_correctives.py",
        "work/tools/t66_contact_weights.py",
        "work/tools/rewrite_t66_glb_rigid_tracks.py",
        "work/tools/refine_t66_glb_interpolation.py",
        "work/tools/verify_t66_glb_pose.py",
        "work/tools/verify_t66_family_contacts.py",
        "work/tools/validate_authored_surface_geometry.py",
        "work/evidence/T66/serial-completion-2026-10-02/unit-02/validate_unit02.py",
        "work/tools/t66_parallel_protocol.py",
        "work/tools/build_t66_parallel_wave1_manifest.py",
        "work/tools/run_t66_parallel_candidate.py",
        "work/tools/validate_t66_parallel_wave1.py",
        "work/schemas/t66-parallel-candidate-package.schema.json",
    ]
    snapshot_files = snapshot_root / "files"
    if snapshot_root.exists():
        if snapshot_root.is_symlink():
            raise ValueError("snapshot root cannot be a symlink")
        allowed = {str(Path("files") / rel) for rel, _ in required_inputs}
        allowed.update(str(Path("files") / rel) for rel in code_paths)
        allowed.update(str(Path("files") / rel) for rel, _ in control_context_paths)
        allowed.update({
            "files/work/evidence/T66/serial-completion-2026-10-02/unit-02/trials-r1/hip-flexion-left/input.json",
            "files/work/evidence/T66/implementation-2026-10-02/contact-production-r6/hip-flexion-left/input.json",
        })
        allowed.update(str(Path("assignments") / f"{worker}.json") for worker in ("A", "B", "C", "F"))
        for item in snapshot_root.rglob("*"):
            if item.is_symlink():
                raise ValueError(f"unexpected symlink in partial snapshot: {item}")
            if item.is_file() and item.relative_to(snapshot_root).as_posix() not in allowed:
                raise ValueError(f"unexpected file in partial snapshot without manifest: {item}")
        snapshot_files.mkdir(parents=True, exist_ok=True)
        (snapshot_root / "assignments").mkdir(exist_ok=True)
    else:
        snapshot_files.mkdir(parents=True, exist_ok=False)
        (snapshot_root / "assignments").mkdir()
    refs: list[dict[str, Any]] = []
    data: dict[str, Any] = {}
    for rel, role in required_inputs:
        ref = json_snapshot(root, snapshot_files, rel, role, refs)
        if rel.endswith(".json"):
            data[rel] = read_json(root / rel)
    control_context_refs = [json_snapshot(root, snapshot_files, rel, role, []) for rel, role in control_context_paths]
    for rel in code_paths:
        copy_reference(root, snapshot_files, rel, "frozen executable/reference code", refs,
                       replace_existing=args.refresh_owned_draft)

    scope = data["atlas-data/catalog/target-scope-t96.json"]
    overlay = data["atlas-data/overlays/za-local-integration.json"]
    compiled = data["atlas-data/source-cache/datasets/za/compiled/manifest.json"]
    authoring = data["work/evidence/T59/authoring-run-manifest-r2.json"]
    whole_target = data["work/evidence/T66/implementation-2026-10-02/whole-target-motion-ledger.json"]
    whole_bone = data["work/evidence/T66/implementation-2026-10-02/whole-bone-motion-ledger.json"]
    nerve_ledger = data["work/evidence/T66/implementation-2026-10-02/nerve-course-and-entrapment-ledger.json"]
    family_queue = data["work/evidence/T66/implementation-2026-10-02/family-queue.json"]
    motion_contract = data["work/evidence/T35/motion-contract.json"]
    baseline = read_json(root / "work/evidence/T66/parallel-completion-2026-10-03/start-baseline.json")
    head = git_head(root)
    if baseline.get("head") != head:
        raise ValueError(f"working HEAD changed after T66 baseline: {baseline.get('head')} != {head}")

    target_by_id = {row["id"]: row for row in scope["targets"]}
    if len(target_by_id) != 542:
        raise ValueError(f"T96 target denominator changed: {len(target_by_id)}")
    owner_by_target: dict[str, str] = {}
    target_disposition: list[dict[str, Any]] = []
    assigned_targets: dict[str, list[str]] = {k: [] for k in ("A", "B", "C", "F")}
    for target in scope["targets"]:
        owner, reason = source_owner(target)
        owner_by_target[target["id"]] = owner
        is_muscle = target.get("semanticKind") in MUSCLE_KINDS
        deferred_to = None
        if not is_muscle:
            status = "deferred"
            assigned = "integrationWriter"
            disposition_reason = "non-muscle target retained in the 542 denominator; motion target context is handled only where a linked wave family requires it"
        elif owner in ("A", "B", "C"):
            status = "assigned"
            assigned = owner
            assigned_targets[owner].append(target["id"])
            disposition_reason = reason
        else:
            status = "deferred"
            assigned = owner if owner in ("D", "E") else "integrationWriter"
            deferred_to = assigned
            disposition_reason = reason
        target_disposition.append({
            "targetId": target["id"], "semanticKind": target.get("semanticKind"),
            "primaryOwner": target.get("primaryOwner"), "regionIds": target.get("regionIds", []),
            "scopeDisposition": status, "disposition": status,
            "assignedTo": assigned if status == "assigned" else None,
            "deferredTo": deferred_to or ("integrationWriter" if status == "deferred" and not is_muscle else None),
            "reason": disposition_reason,
            "identityApprovalAdded": False, "fullExtentApprovalAdded": False,
        })
    muscle_targets = [x for x in scope["targets"] if x.get("semanticKind") in MUSCLE_KINDS]
    if len(muscle_targets) != 429:
        raise ValueError(f"muscle target count changed: {len(muscle_targets)}")

    memberships: list[dict[str, Any]] = []
    assigned_memberships: dict[str, list[str]] = {k: [] for k in ("A", "B", "C", "F")}
    for target in scope["targets"]:
        for region in target.get("regionIds", []):
            key = f"{target['id']}::{region}"
            target_owner = owner_by_target[target["id"]]
            is_muscle = target.get("semanticKind") in MUSCLE_KINDS
            owner = target_owner if is_muscle else "integrationWriter"
            status = "assigned" if owner in ("A", "B", "C") else "deferred"
            reason = "exact T96 targetId+regionId membership; source membership does not imply a geometry/action binding" if status == "assigned" else "retained in frozen denominator; explicitly deferred outside wave-1 ownership"
            memberships.append({"membershipKey": key, "targetId": target["id"], "regionId": region,
                                "disposition": status, "assignedTo": owner if status == "assigned" else None,
                                "deferredTo": owner if status == "deferred" else None, "reason": reason})
            if status == "assigned": assigned_memberships[owner].append(key)
    if len(memberships) != 563 or len([m for m in memberships if m["targetId"] in {t["id"] for t in muscle_targets}]) != 447:
        raise ValueError(f"T96 membership denominators changed: total={len(memberships)}")

    overlay_muscles = [obj for obj in overlay.get("objects", []) if obj.get("kind") == "muscle"]
    compiled_muscles = [row for row in compiled.get("instances", []) if row.get("kind") in ("muscle", "muscle_surface_or_part")]
    if len(overlay_muscles) != 462 or len({x["sourceKey"] for x in overlay_muscles}) != 462:
        raise ValueError(f"overlay muscle surface denominator changed: {len(overlay_muscles)}")
    compiled_by_key = {x["sourceKey"]: x for x in compiled.get("instances", [])}
    t59_surface = {x["sourceKey"]: x for x in authoring.get("sourceSurfaceUnits", [])}
    if len(t59_surface) != 462:
        raise ValueError(f"T59 surface unit denominator changed: {len(t59_surface)}")

    assigned_sources: dict[str, list[str]] = {k: [] for k in ("A", "B", "C", "F")}
    source_disposition: list[dict[str, Any]] = []
    source_resource_refs: list[dict[str, Any]] = []
    source_work_queue: list[dict[str, Any]] = []
    resource_pairs: set[tuple[str, str, str]] = set()
    for obj in overlay_muscles:
        key = obj["sourceKey"]
        target_id = obj.get("targetId")
        target_owner = owner_by_target.get(target_id) if target_id else None
        linked = [tid for tid in obj.get("targetIds", []) if tid in owner_by_target]
        linked_owners = {owner_by_target[tid] for tid in linked if owner_by_target[tid] in ("A", "B", "C", "D", "E")}
        if target_owner in ("A", "B", "C", "D", "E"):
            owner = target_owner
            basis = "existing overlay primary targetId joined to frozen T96; candidate relation is not newly approved"
        elif len(linked_owners) == 1:
            owner = next(iter(linked_owners))
            basis = "existing overlay targetIds joined to one T96 wave scope; relation remains existing candidate evidence"
        else:
            region_owners = set()
            for region in obj.get("regionIds", []):
                if region in LOWER:
                    region_owners.add("B")
                elif region in AXIAL:
                    region_owners.add("C")
                elif region == "upper-limb":
                    region_owners.add("A" if HAND_TOKENS.search(str(obj.get("sourceName", ""))) else "integrationWriter")
                elif region == "shoulder-scapular":
                    region_owners.add("integrationWriter")
                elif region == "head":
                    source_label = str(obj.get("sourceName", ""))
                    region_owners.add("D" if JAW_TOKENS.search(source_label) else "E")
                elif region == "pelvis-perineum":
                    region_owners.add("E")
            if len(region_owners) == 1 and next(iter(region_owners)) in ("A", "B", "C"):
                owner = next(iter(region_owners))
                basis = "existing source region hint only; does not assert target identity"
            else:
                owner = "integrationWriter"
                basis = "no unique wave-1 source/action scope from existing target and region hints; writer must disposition"
        status = "assigned" if owner in ("A", "B", "C") else "deferred"
        if status == "assigned": assigned_sources[owner].append(key)
        row = compiled_by_key.get(key)
        if row is None:
            raise ValueError(f"overlay muscle source missing compiled instance: {key}")
        relation_targets = sorted(set([target_id] if target_id else []) | set(linked))
        disposition = {
            "sourceKey": key, "sourceName": obj.get("sourceName"), "side": side_value(obj.get("side")),
            "regionIds": obj.get("regionIds", []), "existingTargetIds": relation_targets,
            "candidateRelationStatus": obj.get("mappingStatus"), "haConceptId": obj.get("haConceptId"),
            "sourceGeometrySha256": row.get("evaluatedGeometrySha256"), "sourceOnly": obj.get("sourceOnly"),
            "localUseRights": obj.get("localUseRights"), "publicRedistribution": obj.get("publicRedistribution"),
            "humanReview": obj.get("humanReview"), "disposition": status,
            "assignedTo": owner if status == "assigned" else None,
            "deferredTo": owner if status == "deferred" else None,
            "assignmentBasis": basis, "reason": basis, "targetIdentityApproved": False, "actionClaimAdded": False,
        }
        source_disposition.append(disposition)
        for lod, detail in sorted(row.get("lods", {}).items()):
            resource = detail["resource"]
            resource_path = f"atlas-data/source-cache/datasets/za/resources/{resource}.glb"
            file_path = root / resource_path
            if not file_path.is_file() or file_path.is_symlink() or file_path.stat().st_size != detail["bytes"]:
                raise FileNotFoundError(f"declared immutable source resource unavailable/size mismatch: {resource_path}")
            triple = (key, lod, resource)
            if triple in resource_pairs:
                raise ValueError(f"duplicate source resource selector {triple}")
            resource_pairs.add(triple)
            source_resource_refs.append({
                "sourceKey": key, "sourceLabel": row.get("name"), "explicitSourceSide": row.get("sourceLabelSide"),
                "lod": lod, "path": resource_path, "sha256": detail.get("sha256"),
                "bytes": detail.get("bytes"), "geometryChunkSha256": detail.get("chunk"),
                "verificationPolicy": "compiled-manifest hash pinned; actual byte SHA verified on harness access; no archive-wide rehash or copy",
            })
        scope_targets = [x for x in relation_targets if x in target_by_id]
        exact_part_targets = [t for t in scope_targets if target_by_id[t].get("semanticKind") == "muscle_part"]
        part = exact_part_targets[0] if len(exact_part_targets) == 1 else None
        family_queue_name = {"A": "wave1:hand-digit-scope", "B": "wave1:lower-limb-scope", "C": "wave1:axial-scope"}.get(owner)
        if family_queue_name:
            work_key = {
                "family": family_queue_name,
                "side": side_value(obj.get("side")),
                "action": None,
                "sourceKey": key,
                "part": part,
                "poseContractRevision": POSE_REVISION,
            }
            work_id = work_key_id(work_key)
            source_work_queue.append({
                "workKeyId": work_id, "key": work_key, "workKind": "source_action_scope_disposition",
                "disposition": "assigned", "assignedTo": owner,
                "reason": "worker must cite an exact action/pose scope or return unsupported_evidence; null action is a scope-review state, not an invented action",
                "sourceRelationIds": scope_targets,
            })

    # The source surface population must map exactly to the T59/compiled source population.
    if set(x["sourceKey"] for x in source_disposition) != set(t59_surface) or not set(t59_surface) <= set(compiled_by_key):
        raise ValueError("overlay/T59 source surface sets disagree or a source key is absent from compiled manifest")

    bone_rows = whole_bone["rows"]
    if len(bone_rows) != 210:
        raise ValueError(f"whole bone source rows changed: {len(bone_rows)}")
    bone_disposition = []
    assigned_bones: dict[str, list[str]] = {k: [] for k in ("A", "B", "C", "F")}
    for row in bone_rows:
        regions = set(row.get("regions", []))
        matches = set()
        if regions & LOWER: matches.add("B")
        if regions & AXIAL: matches.add("C")
        bone_name = str(row.get("name", ""))
        if "upper-limb" in regions and (HAND_TOKENS.search(bone_name) or CARPAL_TOKENS.search(bone_name)):
            matches.add("A")
        if len(matches) == 1:
            owner = next(iter(matches)); disposition = "assigned"; assigned_bones[owner].append(row["sourceKey"])
            reason = "existing whole-bone region context shares the worker's bounded scene family; this is context, not an inferred DOF"
        else:
            owner = "integrationWriter"; disposition = "deferred"
            reason = "cross-region or out-of-wave bone context remains with integration writer; no DOF inferred from label/region"
        bone_disposition.append({
            "sourceKey": row["sourceKey"], "sourceName": row.get("name"), "side": row.get("side"),
            "regionIds": row.get("regions", []), "motionActionId": row.get("motionActionId"),
            "disposition": disposition, "assignedTo": owner if disposition == "assigned" else None,
            "deferredTo": owner if disposition == "deferred" else None, "reason": reason,
            "independentDOFInferred": False,
        })

    nerve_rows = nerve_ledger["rows"]
    if len(nerve_rows) != 98:
        raise ValueError(f"nerve label row denominator changed: {len(nerve_rows)}")
    nerve_disposition = []
    for row in nerve_rows:
        nerve_id = "T66-NR-" + sha_bytes(canonical_json({
            "sourceNativeName": row.get("sourceNativeName"),
            "sourceInstanceIds": sorted(row.get("sourceInstanceIds", [])),
            "sourceKeys": sorted(row.get("sourceKeys", [])),
            "regionIds": sorted(row.get("regionIds", [])),
        }))[:24]
        nerve_disposition.append({
            "nerveRowId": nerve_id, "sourceNativeName": row.get("sourceNativeName"),
            "sourceInstanceIds": row.get("sourceInstanceIds", []), "sourceKeys": row.get("sourceKeys", []),
            "regionIds": row.get("regionIds", []), "courseTextSupport": row.get("courseTextSupport"),
            "entrapmentTextSupported": row.get("entrapmentTextSupported"),
            "fieldEvidenceCount": len(row.get("fieldEvidence", [])),
            "humanReview": row.get("humanReview"), "publicRedistribution": row.get("publicRedistribution"),
            "disposition": "assigned", "assignedTo": "F",
            "reason": "text-only full-current-ledger audit; exact claim evidence or unavailable must be returned per row",
            "anatomicalConceptIdentityAdded": False, "geometryAdded": False,
        })

    # Source-work scope keys are exact and disjoint. Existing U01/U02/U03 action
    # responsibility keys are snapshotted separately and remain writer-owned history.
    worker_work = {k: [] for k in ("A", "B", "C", "F")}
    for row in source_work_queue:
        worker_work[row["assignedTo"]].append(row)
    for nerve in nerve_disposition:
        nerve_key = {"family": "wave1:nerve-text", "side": None, "action": None,
                     "sourceKey": nerve["nerveRowId"], "part": None, "poseContractRevision": POSE_REVISION}
        nerve_work = {
            "workKeyId": work_key_id(nerve_key),
            "key": nerve_key,
            "workKind": "nerve_row_text_audit", "disposition": "assigned", "assignedTo": "F",
            "reason": "stable ledger-row reference only; not an anatomical nerve ID or clinical claim",
        }
        worker_work["F"].append(nerve_work)
        source_work_queue.append(nerve_work)

    assignments: dict[str, dict[str, Any]] = {}
    descriptions = {
        "A": "hand/digit geometry and source-bounded action candidates",
        "B": "remaining hip/knee/ankle/foot-digit geometry and action candidates",
        "C": "cervical/thoracolumbar/rib-respiration geometry and action candidates",
        "F": "all current nerve course/entrapment text rows; text-only, no nerve geometry",
    }
    for worker in ("A", "B", "C", "F"):
        assignment_record = {
            "description": descriptions[worker],
            "assignedWorkKeys": worker_work[worker],
            "assignedSourceKeys": sorted(set(assigned_sources[worker])) if worker != "F" else [],
            "assignedTargetIds": sorted(set(assigned_targets[worker])) if worker != "F" else [],
            "assignedMembershipKeys": sorted(set(assigned_memberships[worker])) if worker != "F" else [],
            "assignedBoneSourceKeys": sorted(set(assigned_bones[worker])) if worker != "F" else [],
            "assignedNerveRowIds": [x["nerveRowId"] for x in nerve_disposition] if worker == "F" else [],
            "outputRoot": str(MANIFEST_REL.parent / "workers" / worker),
            "writePolicy": "worker output root only; no shared runtime, common code, EXECUTION, T66 report, source cache, OpenSim_Models, or history evidence writes",
            "reviewStateOnSubmission": "candidate_unreviewed_not_registered",
        }
        assignments[worker] = assignment_record

    # All non-A/B/C source scope rows remain visible and have an exact reason.
    for obj in overlay_muscles:
        source_row = next(x for x in source_disposition if x["sourceKey"] == obj["sourceKey"])
        if source_row["disposition"] == "assigned":
            continue
        target_ids = source_row["existingTargetIds"]
        target_id = target_ids[0] if len(target_ids) == 1 else None
        deferred_to = source_row["deferredTo"]
        reason = source_row["assignmentBasis"]
        source_work_queue.append({
            "workKeyId": work_key_id({"family": "deferred:scope-disposition", "side": side_value(obj.get("side")), "action": None,
                                      "sourceKey": obj["sourceKey"], "part": target_id if target_id in target_by_id else None,
                                      "poseContractRevision": POSE_REVISION}),
            "key": {"family": "deferred:scope-disposition", "side": side_value(obj.get("side")), "action": None,
                    "sourceKey": obj["sourceKey"], "part": target_id if target_id in target_by_id else None,
                    "poseContractRevision": POSE_REVISION},
            "workKind": "source_action_scope_disposition", "disposition": "deferred",
            "assignedTo": None, "deferredTo": deferred_to,
            "reason": reason,
        })

    # Existing real action work is retained as a writer-owned prior ledger, not re-assigned.
    prior_responsibilities = []
    for rel in [
        "work/evidence/T66/serial-completion-2026-10-02/unit-01/serial-queue.json",
        "work/evidence/T66/serial-completion-2026-10-02/unit-02/serial-queue.json",
        "work/evidence/T66/serial-completion-2026-10-02/unit-03/serial-queue.json",
    ]:
        queue = data[rel]
        for row in queue.get("responsibilityKeys", []):
            key_src = row.get("key") or {}
            key = {
                "family": key_src.get("family"), "side": key_src.get("side"),
                "action": key_src.get("action"), "sourceKey": key_src.get("sourceKey"),
                "part": None, "poseContractRevision": queue.get("unitResult", {}).get("poseContractRevision") or f"historical:{queue.get('unit', 'unknown')}",
            }
            # Some old unit queues predate the explicit six-field contract. Preserve
            # an honest, namespaced revision marker rather than treating null as approval.
            if not key["poseContractRevision"]:
                key["poseContractRevision"] = f"historical:{queue.get('unit', 'unknown')}"
            try:
                identifier = work_key_id(key)
            except (ValueError, TypeError):
                continue
            prior_responsibilities.append({
                "workKeyId": identifier, "key": key,
                "historicalQueuePath": rel,
                "sourceImplementationStatus": row.get("implementationStatus", row.get("status")),
                "sourceRole": row.get("role"),
                "ownership": "integrationWriter_existing_unit_output",
                "reason": "already completed or dispositioned by prior T66 unit; frozen for no duplicate worker assignment",
            })

    # Exact current counts; input objects are not reinterpreted as unique concepts.
    denominators = {
        "productTargets": 542, "productMemberships": 563, "regions": 12,
        "muscleTargets": 429, "muscleMemberships": 447,
        "sourceConcepts": 232, "sourceSurfaceInstances": 462,
        "compiledAdditionalMuscleLikeInstancesNotInT59SurfaceDenominator": len(set(x["sourceKey"] for x in compiled_muscles) - set(t59_surface)),
        "wholeBoneSourceRows": 210, "independentAnatomicalBoneCount": whole_bone.get("independentAnatomicalBoneCount"),
        "nerveLabelRows": 98, "independentNerveConceptCount": nerve_ledger.get("independentAnatomicalConceptCount"),
        "haCanonicalBindings": 130,
        "historical163": {"6": 6, "20": 20, "135": 135, "2": 2},
    }
    if authoring.get("denominators", {}).get("existingCanonicalHaBindings") != 130:
        raise ValueError("T59 existing canonical HA binding denominator changed")
    contract_revision = motion_contract.get("revision") or "unknown-current-motion-contract"
    run_id = "T66-W1-20261003-" + sha_bytes(canonical_json({
        "baselineHead": head,
        "inputs": sorted((x["path"], x["sha256"]) for x in refs),
        "nextUnit": "author-and-integrate-normal-motion-bone-and-nerve",
    }))[:12]

    # Declare every exact source resource hash from the compiled manifest. The
    # source files remain at their immutable cache paths and are checked on use.
    unique_source_refs: dict[str, dict[str, Any]] = {}
    for ref in source_resource_refs:
        unique_source_refs.setdefault(ref["sha256"], {"path": ref["path"], "sha256": ref["sha256"], "bytes": ref["bytes"]})

    sample_success_rel = "work/evidence/T66/serial-completion-2026-10-02/unit-02/trials-r1/hip-flexion-left/input.json"
    sample_failure_rel = "work/evidence/T66/implementation-2026-10-02/contact-production-r6/hip-flexion-left/input.json"
    sample_success = json_snapshot(root, snapshot_files, sample_success_rel, "prior exact successful candidate input for harness smoke only", refs)
    sample_failure = json_snapshot(root, snapshot_files, sample_failure_rel, "historical rejected candidate input; inspection only, not rerun without new hypothesis", refs)

    wave = {
        "schemaVersion": SCHEMA_VERSION,
        "ownershipSemanticsRevision": 2,
        "task": "T66",
        "runId": run_id,
        "baselineHead": head,
        "nextUnit": "author-and-integrate-normal-motion-bone-and-nerve",
        "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "manifestPath": str(MANIFEST_REL),
        "snapshotRoot": str(SNAPSHOT_REL),
        "motionContractRevision": contract_revision,
        "authority": dict(RIGHTS_STATE),
        "baseline": {"dirtyPathCount": len(git_dirty_snapshot(root)), "dirtyPaths": git_dirty_snapshot(root), "OpenSim_Models": "read-only; start status clean; no change permitted"},
        "denominators": denominators,
        "scopeRules": {
            "targetAssignment": "T96 primary owner plus exact concept-term partition for hand/digits; only defines bounded research ownership, not identity, source binding, or target extent approval",
            "sourceAssignment": "existing overlay targetId/targetIds and region hints; assignment is candidate scope only; source identity, side, part, claims, geometry and action must be revalidated by worker",
            "unresolvedAction": "action=null is a source-scope disposition key only; a worker must provide exact action evidence or return unsupported_evidence/deferred",
            "sourceSurfaceAndConceptCounts": "462 source surface instances are distinct from 232 source concepts; duplicate source use across independently evidenced actions/families is allowed",
            "targetAndMembershipCounts": "target IDs and targetId::regionId membership keys are separate; a partial member result never approves whole target/group extent",
            "boneAndNerve": "210 bone source rows and 98 nerve label rows are not independent anatomical concept counts; the latter remains null where ledger says unknown",
            "wave1BoneContextAssignment": "A receives only exact hand/digit phalanx, finger/thumb, metacarpal, or named carpal source rows; generic upper-limb/shoulder bones remain writer-owned; region assignment does not infer a new DOF",
        },
        "inputs": sorted(refs, key=lambda x: x["path"]),
        "controlContextSnapshots": sorted(control_context_refs, key=lambda x: x["path"]),
        "sourceResourceRefs": sorted(source_resource_refs, key=lambda x: (x["sourceKey"], x["lod"])),
        "sourceResourceHashesUnique": sorted(unique_source_refs.values(), key=lambda x: x["sha256"]),
        "targetDisposition": target_disposition,
        "membershipDisposition": memberships,
        "sourceDisposition": source_disposition,
        "boneContextDisposition": bone_disposition,
        "nerveTextDisposition": nerve_disposition,
        "sourceActionScopeQueue": source_work_queue,
        "priorActionResponsibilityKeys": prior_responsibilities,
        "assignments": assignments,
        "sampleInputs": {
            "successfulPackage": {"path": sample_success["snapshotPath"], "sha256": sample_success["sha256"], "sourceEvidencePath": sample_success_rel,
                                  "reuseExistingQcIfExactOutputHashMatches": [
                                      "work/evidence/T66/serial-completion-2026-10-02/unit-02/trials-r1/hip-flexion-left/contact-qc.json",
                                      "work/evidence/T66/serial-completion-2026-10-02/unit-02/trials-r1/hip-flexion-left/glb-pose-qc.json",
                                      "work/evidence/T66/serial-completion-2026-10-02/unit-02/candidate-interpolation-r1.json"],
                                  "purpose": "writer harness only; prior source-bound educational pose candidate; no app registration"},
            "historicalFailure": {"path": sample_failure["snapshotPath"], "sha256": sample_failure["sha256"], "sourceEvidencePath": sample_failure_rel,
                                  "previousOutcome": "source_contact_rejected", "rerun": False,
                                  "reason": "same failed contact-production-r6 hypothesis is frozen as a regression reference; no new failure hypothesis was introduced"},
        },
        "writerDryRun": {"outputRoot": str(MANIFEST_REL.parent / "writer-dry-run" / "hip-flexion-left"), "assignment": "writer-dry-run", "sourceCandidateOnly": True},
        "assignmentsPolicy": {"wave1": ["A", "B", "C", "F"], "wave2Deferred": ["D", "E"], "integrationWriterDeferred": True, "workersAutoLaunched": False},
        "commonNoWritePaths": [
            "atlas-data/motion/", "atlas-data/assets/", "atlas-web/src/", "work/EXECUTION.json", "work/NEXT.md",
            "work/reports/T66.md", "work/tasks/", "atlas-data/source-cache/", "OpenSim_Models/",
            "work/evidence/T66/serial-completion-2026-10-02/", "work/evidence/T66/implementation-2026-10-02/",
            "work/evidence/T66/parallel-completion-2026-10-03/input-snapshot/files/work/tools/",
        ],
        "workerOutputSchema": "work/schemas/t66-parallel-candidate-package.schema.json",
        "workerOutputSchemaSha256": next(x["sha256"] for x in refs if x["path"] == "work/schemas/t66-parallel-candidate-package.schema.json"),
        "candidateOutputRules": {
            "geometryWorkers": "candidate derived GLB + authoring input/record/QC + exact work/source keys under assigned worker outputRoot; no production URI, route, runtime or canonical binding",
            "textWorkerF": "field-level verified claims/evidence delta for nerve rows under F outputRoot; no geometry or learner projection writes",
            "candidateReview": "sourceOnly=true, publicRedistribution=held, humanReview=not_performed, canonicalBindingAdded=false",
        },
        "preservation": {
            "sourceCacheCopied": False, "sourceCacheModified": False, "OpenSim_ModelsModified": False,
            "priorUnitEvidenceOverwritten": False, "historicalSourceAndClaimsPreserved": True,
            "denominatorsFixed": True, "rightsOrHumanReviewPromoted": False,
        },
    }

    # Write the filtered worker inputs after the manifest's schema boundaries are known.
    assignment_root = snapshot_root / "assignments"
    for worker, record in assignments.items():
        snapshot_assignment = {
            "schemaVersion": "t66-parallel-assignment-snapshot-v1",
            "runId": run_id,
            "assignment": worker,
            "description": record["description"],
            "assignedWorkKeys": record["assignedWorkKeys"],
            "assignedSourceKeys": record["assignedSourceKeys"],
            "assignedTargetIds": record["assignedTargetIds"],
            "assignedMembershipKeys": record["assignedMembershipKeys"],
            "assignedBoneSourceKeys": record["assignedBoneSourceKeys"],
            "assignedNerveRowIds": record["assignedNerveRowIds"],
            "workerOutputRoot": record["outputRoot"],
            "authority": dict(RIGHTS_STATE),
            "noWritePaths": wave["commonNoWritePaths"],
        }
        path = assignment_root / f"{worker}.json"
        path.write_text(json.dumps(snapshot_assignment, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        raw = path.read_bytes()
        wave.setdefault("assignmentSnapshots", []).append({"assignment": worker, "path": str(path.relative_to(root)), "sha256": sha_bytes(raw), "bytes": len(raw)})
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(wave, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    result = validate_manifest(wave, repo_root=root, verify_snapshot=True, verify_source_bytes=False)
    print(json.dumps({
        "status": "frozen_manifest_created",
        "manifestPath": str(MANIFEST_REL),
        "runId": run_id,
        **result,
        "assignments": {k: {"targets": len(v["assignedTargetIds"]), "memberships": len(v["assignedMembershipKeys"]),
                            "sources": len(v["assignedSourceKeys"]), "bones": len(v["assignedBoneSourceKeys"]),
                            "nerveRows": len(v["assignedNerveRowIds"]), "workKeys": len(v["assignedWorkKeys"])}
                        for k, v in assignments.items()},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
