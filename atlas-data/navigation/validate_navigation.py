#!/usr/bin/env python3
"""Validate T15b navigation schema, references, side, scene assets, and migration bounds."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "atlas-data/navigation/atlas-navigation.json"
SCHEMA = ROOT / "atlas-data/schemas/navigation.schema.json"
CATALOG = ROOT / "atlas-data/catalog/canonical-catalog.json"
DESIGN = ROOT / "design/2026-09-25-muscle-atlas/region12-navigation.design.json"
BASELINE = ROOT / "work/evidence/T15b/start-baseline.json"


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_pointer(value: Any, pointer: str) -> Any:
    if not pointer.startswith("/"):
        raise ValueError("jsonPointer must begin with '/'")
    node = value
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        node = node[int(token)] if isinstance(node, list) else node[token]
    return node


def load_schema_engine():
    path = ROOT / "atlas-data/schemas/validate.py"
    spec = importlib.util.spec_from_file_location("human_atlas_t03_schema_engine", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the dependency-free T03 schema validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(document: Any, schema: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    engine = load_schema_engine()
    for issue in engine.check_schema(schema):
        issues.append({"code": issue["code"], "path": issue["path"], "message": issue["message"]})
    for issue in engine.schema_issues(schema, document):
        issues.append({"code": issue["code"], "path": issue["path"], "message": issue["message"]})
    if issues:
        return issues

    catalog_doc = read(CATALOG)
    entities = catalog_doc["entities"]
    concepts = {row["id"]: row for row in entities["muscleConcepts"]}
    instances = {row["id"]: row for row in entities["instances"]}
    structures = {row["id"]: row for row in entities["structures"]}
    muscle_parts = {row["id"]: row for row in entities["muscleConcepts"] if row["entityType"] == "muscle_part"}
    mesh_assets = {row["id"]: row for row in entities["meshAssets"]}
    evidence = {row["id"] for row in entities["evidence"]}
    muscle_mappings = {row["id"]: row for row in entities["meshMappings"]}
    decisions_text = (ROOT / "work/DECISIONS.md").read_text(encoding="utf-8")
    t12_manifest_path = ROOT / "atlas-data/manifests/canonical-geometry-t12.json"
    t13_manifest_path = ROOT / "atlas-data/manifests/derived-bones-t13.json"
    t12_manifest = read(t12_manifest_path)
    t13_manifest = read(t13_manifest_path)
    model_manifests = {
        t12_manifest["modelId"]: {
            "frameId": t12_manifest["frameId"], "units": t12_manifest["units"],
            "poseId": t12_manifest["poseId"], "sha256": t12_manifest["sourceGlbSha256"],
        },
        t13_manifest["modelId"]: {
            "frameId": t13_manifest["transform"]["frameId"], "units": t13_manifest["transform"]["targetUnits"],
            "poseId": t13_manifest["transform"]["poseId"], "sha256": t13_manifest["glb"]["sha256"],
        },
    }

    def fail(code: str, path: str, message: str) -> None:
        issues.append({"code": code, "path": path, "message": message})

    def check_source_ref(source_ref: dict[str, str], path: str) -> None:
        source_path = Path(source_ref["path"])
        if source_path.is_absolute() or ".." in source_path.parts or "OpenSim_Models" in source_path.parts:
            fail("unsafe_source_path", path, "Source references must stay inside the project and outside OpenSim_Models.")
            return
        resolved = ROOT / source_path
        if not resolved.is_file():
            fail("missing_source_ref", path, f"Referenced input {source_ref['path']!r} is missing.")
            return
        if file_hash(resolved) != source_ref["manifestSha256"]:
            fail("source_manifest_hash_mismatch", path, f"The referenced source file hash changed: {source_ref['path']}.")
            return
        try:
            resolve_pointer(read(resolved), source_ref["jsonPointer"])
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            fail("source_locator_unresolved", path, f"Source locator does not resolve: {exc}")

    expected_categories = [
        {key: row[key] for key in ("id", "order", "labelKo", "labelEn")}
        for row in read(DESIGN)["categories"]
    ]
    if document["categories"] != expected_categories:
        fail("category_contract_mismatch", "$.categories", "Runtime category IDs, order, or labels differ from the approved 12-category design.")

    category_ids = {row["id"] for row in document["categories"]}
    seen_memberships: set[tuple[str, str, str]] = set()
    membership_ids: set[str] = set()
    for i, row in enumerate(document["memberships"]):
        path = f"$.memberships[{i}]"
        key = (row["categoryId"], row["entityKind"], row["entityId"])
        if row["id"] in membership_ids:
            fail("duplicate_id", f"{path}.id", f"Duplicate membership ID {row['id']!r}.")
        membership_ids.add(row["id"])
        if key in seen_memberships:
            fail("duplicate_membership", path, "The same category/entity-kind/entity-ID relation may occur only once.")
        seen_memberships.add(key)
        if row["categoryId"] not in category_ids:
            fail("unknown_category", f"{path}.categoryId", f"Unknown product category {row['categoryId']!r}.")
        if row["entityKind"] == "muscle":
            target = concepts.get(row["entityId"])
            if target is None or target["entityType"] not in ("individual_muscle", "muscle_group"):
                fail("membership_target_not_muscle", f"{path}.entityId", "Muscle membership must reference an existing muscle concept/group, not a part or source region.")
        else:
            target = structures.get(row["entityId"])
            if target is None or target["kind"] != "bone":
                fail("membership_target_not_bone", f"{path}.entityId", "Bone membership must reference an existing Structure(kind=bone).")
        if row["status"] == "decision_only" and not row.get("productDecisionRef"):
            fail("membership_missing_decision", f"{path}.productDecisionRef", "Decision-only membership needs a product decision reference.")
        elif row["productDecisionRef"] not in decisions_text:
            fail("missing_product_decision", f"{path}.productDecisionRef", f"Product decision {row['productDecisionRef']!r} is not recorded in work/DECISIONS.md.")

    structure_instances: dict[str, dict[str, Any]] = {}
    seen_structure_sides: set[tuple[str, str]] = set()
    for i, row in enumerate(document["structureInstances"]):
        path = f"$.structureInstances[{i}]"
        if row["id"] in structure_instances:
            fail("duplicate_id", f"{path}.id", f"Duplicate structure instance ID {row['id']!r}.")
        structure_instances[row["id"]] = row
        target = structures.get(row["structureId"])
        if target is None or target["kind"] != "bone":
            fail("instance_target_not_bone", f"{path}.structureId", "StructureInstance must reference an existing whole bone structure.")
        pair = (row["structureId"], row["side"])
        if pair in seen_structure_sides:
            fail("duplicate_structure_instance", path, "A structure and side pair has more than one instance.")
        seen_structure_sides.add(pair)
        side_prefix = {"right": "R", "left": "L", "midline": "M", "unpaired": "U"}[row["side"]]
        if row["id"] != f"HA-SI-{side_prefix}-{row['structureId']}":
            fail("unstable_structure_instance_id", f"{path}.id", "StructureInstance ID must remain derived from stable structure ID and laterality.")
        for j, source_ref in enumerate(row["sourceRefs"]):
            check_source_ref(source_ref, f"{path}.sourceRefs[{j}]")

    structure_mappings: dict[str, dict[str, Any]] = {}
    mapping_meshes: dict[str, str] = {}
    for i, row in enumerate(document["structureMeshMappings"]):
        path = f"$.structureMeshMappings[{i}]"
        if row["id"] in structure_mappings:
            fail("duplicate_id", f"{path}.id", f"Duplicate structure mesh mapping ID {row['id']!r}.")
        structure_mappings[row["id"]] = row
        instance = structure_instances.get(row["structureInstanceId"])
        if instance is None:
            fail("missing_structure_instance", f"{path}.structureInstanceId", "Structure mesh mapping references no StructureInstance.")
        if not row["meshIds"]:
            fail("empty_mesh_mapping", f"{path}.meshIds", "Structure mesh mapping must contain at least one mesh asset ID.")
        for mesh_id in row["meshIds"]:
            asset = mesh_assets.get(mesh_id)
            if asset is None:
                fail("missing_mesh_asset", f"{path}.meshIds", f"Mesh asset {mesh_id!r} is absent from the canonical catalog.")
                continue
            if instance is not None and asset.get("laterality") not in (None, "unknown", instance["side"]):
                fail("mesh_side_mismatch", f"{path}.meshIds", f"Mesh laterality {asset.get('laterality')!r} differs from instance side {instance['side']!r}.")
            if mesh_id in mapping_meshes:
                fail("mesh_mapped_twice", f"{path}.meshIds", f"Mesh asset {mesh_id!r} has multiple structure mappings.")
            mapping_meshes[mesh_id] = row["id"]
        for evidence_id in row["evidenceIds"]:
            if evidence_id not in evidence:
                fail("missing_evidence", f"{path}.evidenceIds", f"Evidence ID {evidence_id!r} does not resolve in the existing catalog.")
        for j, source_ref in enumerate(row["sourceRefs"]):
            check_source_ref(source_ref, f"{path}.sourceRefs[{j}]")
            try:
                source_doc = read(ROOT / source_ref["path"])
                source_row = resolve_pointer(source_doc, source_ref["jsonPointer"])
                instance = structure_instances.get(row["structureInstanceId"])
                if source_ref["path"] == "atlas-data/manifests/canonical-geometry-t12.json":
                    if source_row.get("meshAssetId") not in row["meshIds"] or source_row.get("structureId") != (instance or {}).get("structureId"):
                        fail("t12_mapping_source_mismatch", f"{path}.sourceRefs[{j}]", "T12 source row does not support this structure/mesh mapping.")
                elif source_ref["path"] == "atlas-data/manifests/derived-bones-t13.json":
                    if source_row.get("meshAssetId") not in row["meshIds"] or source_row.get("targetEntityId") != (instance or {}).get("structureId"):
                        fail("t13_mapping_source_mismatch", f"{path}.sourceRefs[{j}]", "T13 source row does not support this structure/mesh mapping.")
                    expected_evidence = f"EV-BP3D4-{source_row.get('sourceFileId')}-T13-ASSET"
                    if row["evidenceIds"] != [expected_evidence]:
                        fail("t13_mapping_evidence_mismatch", f"{path}.evidenceIds", "T13 mapping must retain the matching existing per-mesh source evidence ID.")
                else:
                    fail("unsupported_mapping_source", f"{path}.sourceRefs[{j}]", "Structure mesh mappings must retain their T12 or T13 source row.")
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                fail("mapping_source_locator_unresolved", f"{path}.sourceRefs[{j}]", f"Could not resolve mapping source locator: {exc}")
        if row["reviewState"] == "reviewed" and row["humanReviewState"] != "reviewed":
            fail("review_without_human_state", f"{path}.reviewState", "A reviewed mapping needs an explicitly recorded human review state.")
        if row["humanReviewState"] == "reviewed":
            fail("human_review_not_available", f"{path}.humanReviewState", "No human review is part of T15b; do not promote mappings here.")

    for i, row in enumerate(document["unmappedMeshContexts"]):
        path = f"$.unmappedMeshContexts[{i}]"
        if row["meshAssetId"] not in mesh_assets:
            fail("missing_mesh_asset", f"{path}.meshAssetId", f"Mesh asset {row['meshAssetId']!r} is absent from the canonical catalog.")
        if row["selection"] is not None:
            fail("unconfirmed_mesh_selectable", f"{path}.selection", "A source mesh without a canonical bone target must remain unbound.")
        for evidence_id in row["evidenceIds"]:
            if evidence_id not in evidence:
                fail("missing_evidence", f"{path}.evidenceIds", f"Evidence ID {evidence_id!r} does not resolve.")
        for j, source_ref in enumerate(row["sourceRefs"]):
            check_source_ref(source_ref, f"{path}.sourceRefs[{j}]")

    for i, scene in enumerate(document["sceneManifests"]):
        path = f"$.sceneManifests[{i}]"
        if scene["categoryId"] not in category_ids:
            fail("unknown_category", f"{path}.categoryId", f"Unknown product category {scene['categoryId']!r}.")
        if scene["stateDimensions"]["humanAnatomyReview"] == "reviewed":
            fail("scene_human_review_not_available", f"{path}.stateDimensions.humanAnatomyReview", "T15b cannot create human anatomy approval.")
        if scene["stateDimensions"]["attachmentLocation"] == "reviewed_surface":
            fail("scene_attachment_surface_not_available", f"{path}.stateDimensions.attachmentLocation", "T15b does not review attachment locations.")
        if scene["stateDimensions"]["motion"] != "absent":
            fail("scene_motion_not_available", f"{path}.stateDimensions.motion", "T15b creates no motion assets.")

        available_meshes: set[str] = set()
        for j, asset_ref in enumerate(scene["assetRefs"]):
            source_model = model_manifests.get(asset_ref["modelId"])
            if source_model is None:
                fail("scene_model_unregistered", f"{path}.assetRefs[{j}].modelId", "Scene model must resolve to a retained T12/T13 source manifest.")
            elif any(scene[field] != source_model[field] for field in ("frameId", "units", "poseId")) or scene["modelId"] != asset_ref["modelId"] or asset_ref["sha256"] != source_model["sha256"]:
                fail("scene_frame_pose_model_mismatch", f"{path}.assetRefs[{j}]", "Scene model, frame, units, pose, and revision must match the source manifest exactly.")
            asset_path = ROOT / asset_ref["uri"]
            if not asset_path.is_file():
                fail("scene_asset_missing", f"{path}.assetRefs[{j}].uri", f"Scene asset {asset_ref['uri']!r} is missing.")
            elif file_hash(asset_path) != asset_ref["sha256"]:
                fail("scene_asset_hash_mismatch", f"{path}.assetRefs[{j}].sha256", "Scene asset hash differs from the recorded revision.")
            for mesh_id in asset_ref["meshAssetIds"]:
                asset = mesh_assets.get(mesh_id)
                if asset is None:
                    fail("scene_mesh_missing", f"{path}.assetRefs[{j}].meshAssetIds", f"Scene mesh {mesh_id!r} is not canonical.")
                elif asset["uri"] != asset_ref["uri"] or asset["hash"] != asset_ref["sha256"]:
                    fail("scene_model_mismatch", f"{path}.assetRefs[{j}].meshAssetIds", f"Mesh {mesh_id!r} does not belong to the referenced model/hash.")
                if mesh_id in available_meshes:
                    fail("scene_mesh_duplicate", f"{path}.assetRefs[{j}].meshAssetIds", f"Mesh {mesh_id!r} occurs in more than one model ref.")
                available_meshes.add(mesh_id)

        covered_meshes: dict[str, str] = {}
        for j, binding in enumerate(scene["selectableBindings"]):
            bpath = f"{path}.selectableBindings[{j}]"
            mesh_id = binding["meshAssetId"]
            if mesh_id not in available_meshes:
                fail("binding_mesh_outside_scene", f"{bpath}.meshAssetId", f"Mesh {mesh_id!r} is not part of this scene model.")
            if mesh_id in covered_meshes:
                fail("scene_mesh_double_bound", f"{bpath}.meshAssetId", f"Mesh {mesh_id!r} already has a scene binding.")
            covered_meshes[mesh_id] = "selectable"
            selection = binding["selection"]
            if selection.get("meshId") not in (None, mesh_id):
                fail("selection_mesh_mismatch", f"{bpath}.selection.meshId", "Selection meshId must match the picked mesh binding.")
            if binding["stateDimensions"]["humanAnatomyReview"] == "reviewed":
                fail("binding_human_review_not_available", f"{bpath}.stateDimensions.humanAnatomyReview", "T15b does not create human review records.")
            if binding["stateDimensions"]["attachmentLocation"] == "reviewed_surface":
                fail("binding_surface_not_available", f"{bpath}.stateDimensions.attachmentLocation", "No attachment surface review is present.")
            if binding["stateDimensions"]["motion"] != "absent":
                fail("binding_motion_not_available", f"{bpath}.stateDimensions.motion", "No motion asset is present.")

            kind = selection["kind"]
            target_id = selection["conceptId"]
            if kind == "muscle":
                target = concepts.get(target_id)
                if target is None or target["entityType"] not in ("individual_muscle", "muscle_group"):
                    fail("selection_muscle_type_mismatch", f"{bpath}.selection.conceptId", "Muscle selection must reference a muscle concept, not a bone/landmark/part.")
                iid = selection.get("instanceId")
                if iid is not None:
                    muscle_instance = instances.get(iid)
                    if muscle_instance is None or muscle_instance["conceptId"] != target_id:
                        fail("selection_instance_mismatch", f"{bpath}.selection.instanceId", "Muscle instance must belong to the selected muscle concept.")
                    elif mesh_assets.get(mesh_id, {}).get("laterality") not in (None, "unknown", muscle_instance["side"]):
                        fail("selection_side_mismatch", f"{bpath}.selection.instanceId", "Muscle instance side differs from picked mesh laterality.")
                part_id = selection.get("partId")
                if part_id is not None:
                    part = muscle_parts.get(part_id)
                    if part is None or part.get("parentId") != target_id:
                        fail("selection_part_mismatch", f"{bpath}.selection.partId", "Muscle part must be a canonical part of the selected muscle.")
                source = muscle_mappings.get(binding["sourceMappingId"])
                if source is None or mesh_id not in source.get("meshIds", []):
                    fail("muscle_binding_mapping_mismatch", f"{bpath}.sourceMappingId", "Muscle scene binding must reuse an existing canonical MeshMapping for this mesh.")
            elif kind == "bone":
                target = structures.get(target_id)
                if target is None or target["kind"] != "bone":
                    fail("selection_bone_type_mismatch", f"{bpath}.selection.conceptId", "Bone selection must reference Structure(kind=bone), not a landmark or muscle.")
                iid = selection.get("instanceId")
                structure_instance = structure_instances.get(iid or "")
                if structure_instance is None or structure_instance["structureId"] != target_id:
                    fail("selection_bone_instance_mismatch", f"{bpath}.selection.instanceId", "Bone instance must resolve to the selected whole-bone structure.")
                elif mesh_assets.get(mesh_id, {}).get("laterality") not in (None, "unknown", structure_instance["side"]):
                    fail("selection_side_mismatch", f"{bpath}.selection.instanceId", "Bone instance side differs from picked mesh laterality.")
                source = structure_mappings.get(binding["sourceMappingId"])
                if source is None or source["structureInstanceId"] != iid or mesh_id not in source["meshIds"]:
                    fail("bone_binding_mapping_mismatch", f"{bpath}.sourceMappingId", "Bone binding must resolve through a typed StructureMeshMapping for this instance and mesh.")
            elif kind == "landmark":
                target = structures.get(target_id)
                if target is None or target["kind"] != "landmark":
                    fail("selection_landmark_type_mismatch", f"{bpath}.selection.conceptId", "Landmark selection must reference Structure(kind=landmark), not a whole bone.")
                iid = selection.get("instanceId")
                if iid is not None:
                    structure_instance = structure_instances.get(iid)
                    if structure_instance is None or structure_instance["structureId"] != target.get("parentId"):
                        fail("selection_landmark_instance_mismatch", f"{bpath}.selection.instanceId", "Landmark instance must reference its parent bone instance.")
            else:
                fail("selection_kind_unknown", f"{bpath}.selection.kind", f"Unsupported selection kind {kind!r}.")

        for j, binding in enumerate(scene["contextBindings"]):
            bpath = f"{path}.contextBindings[{j}]"
            mesh_id = binding["meshAssetId"]
            if mesh_id not in available_meshes:
                fail("context_mesh_outside_scene", f"{bpath}.meshAssetId", f"Context mesh {mesh_id!r} is not part of this scene model.")
            if mesh_id in covered_meshes:
                fail("scene_mesh_double_bound", f"{bpath}.meshAssetId", f"Mesh {mesh_id!r} already has a scene binding.")
            covered_meshes[mesh_id] = "context"
            if binding["selection"] is not None:
                fail("context_binding_selectable", f"{bpath}.selection", "A context-only binding cannot produce a typed card selection.")
        for mesh_id in sorted(available_meshes - set(covered_meshes)):
            fail("scene_mesh_unbound", f"{path}.assetRefs", f"Mesh {mesh_id!r} needs a typed selection or explicit context binding.")

    if BASELINE.exists():
        baseline = read(BASELINE)
        for relative, expected in baseline["protectedInputHashes"].items():
            path = ROOT / relative
            if not path.is_file() or file_hash(path) != expected["sha256"]:
                fail("protected_input_changed", f"baseline.{relative}", "A protected source/data input changed during T15b.")
        open_root = ROOT / "OpenSim_Models"
        try:
            import subprocess
            current_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=open_root, text=True, capture_output=True, check=True).stdout.strip()
            current_status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=open_root, text=True, capture_output=True, check=True).stdout.strip()
            if current_head != baseline["opensim"]["head"] or current_status.splitlines() != baseline["opensim"]["status"]:
                fail("opensim_changed", "baseline.opensim", "OpenSim_Models differs from the task start baseline.")
        except Exception as exc:
            fail("opensim_check_failed", "baseline.opensim", f"Could not verify OpenSim_Models baseline: {exc}")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--schema", type=Path, default=SCHEMA)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    data = read(args.data)
    schema = read(args.schema)
    issues = validate(data, schema)
    summary = {
        "passed": not issues,
        "schema": args.schema.relative_to(ROOT).as_posix() if args.schema.is_relative_to(ROOT) else str(args.schema),
        "data": args.data.relative_to(ROOT).as_posix() if args.data.is_relative_to(ROOT) else str(args.data),
        "counts": {
            "categories": len(data.get("categories", [])),
            "memberships": len(data.get("memberships", [])),
            "structureInstances": len(data.get("structureInstances", [])),
            "structureMeshMappings": len(data.get("structureMeshMappings", [])),
            "unmappedMeshContexts": len(data.get("unmappedMeshContexts", [])),
            "sceneManifests": len(data.get("sceneManifests", [])),
        },
        "issues": issues,
    }
    encoded = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    print(encoded, end="")
    if args.report:
        report = args.report if args.report.is_absolute() else ROOT / args.report
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(encoded, encoding="utf-8")
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
