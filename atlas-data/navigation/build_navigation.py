#!/usr/bin/env python3
"""Build a non-destructive T15b navigation/structure overlay from reviewed inputs."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "design/2026-09-25-muscle-atlas/region12-navigation.design.json"
CATALOG = ROOT / "atlas-data/catalog/canonical-catalog.json"
T12 = ROOT / "atlas-data/manifests/canonical-geometry-t12.json"
T13 = ROOT / "atlas-data/manifests/derived-bones-t13.json"
OUTPUT = ROOT / "atlas-data/navigation/atlas-navigation.json"
ASSETS = ROOT / "atlas-data/manifests/assets.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def ref(path: Path, pointer: str) -> dict[str, str]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "jsonPointer": pointer,
        "manifestSha256": file_sha256(path),
    }


def add_bone_target(
    *,
    rows: dict[str, dict[str, Any]],
    structure_id: str | None,
    mesh_id: str,
    source_name: str,
    source_ref: dict[str, str],
    evidence_ids: list[str],
    source_linkage_state: str,
    catalog_structures: dict[str, dict[str, Any]],
    catalog_meshes: dict[str, dict[str, Any]],
    unmapped: list[dict[str, Any]],
    model_id: str,
) -> None:
    mesh = catalog_meshes.get(mesh_id)
    target = catalog_structures.get(structure_id or "")
    is_right = "right" in source_name.lower() or "right" in model_id.lower()
    if mesh is None:
        raise ValueError(f"Source mesh {mesh_id} is absent from the canonical catalog")
    if not is_right or mesh.get("laterality") != "right":
        raise ValueError(f"Bone side cannot be derived consistently for {mesh_id}")
    if target is None or target.get("kind") != "bone":
        unresolved_reason = "canonical_target_unconfirmed" if structure_id is None else "target_is_not_canonical_bone"
        unmapped.append({
            "meshAssetId": mesh_id,
            "modelId": model_id,
            "sourceName": source_name,
            "sourceRefs": [source_ref],
            "evidenceIds": evidence_ids,
            "selection": None,
            "reasonCode": unresolved_reason,
            "humanReviewState": "not_reviewed",
            "geometryState": "unlinked_source_mesh_context",
            "motionState": "absent",
        })
        return

    instance_id = f"HA-SI-R-{structure_id}"
    if structure_id in rows:
        rows[structure_id]["meshMappings"].append({
            "meshAssetId": mesh_id,
            "evidenceIds": evidence_ids,
            "sourceRefs": [source_ref],
            "sourceLinkageState": source_linkage_state,
        })
        return
    rows[structure_id] = {
        "structureInstance": {
            "id": instance_id,
            "structureId": structure_id,
            "side": "right",
            "variantId": None,
            "sourceRefs": [source_ref],
        },
        "meshMappings": [{
            "meshAssetId": mesh_id,
            "evidenceIds": evidence_ids,
            "sourceRefs": [source_ref],
            "sourceLinkageState": source_linkage_state,
        }],
    }


def build() -> dict[str, Any]:
    design = read_json(DESIGN)
    catalog_doc = read_json(CATALOG)
    catalog = catalog_doc["entities"]
    t12 = read_json(T12)
    t13 = read_json(T13)
    acquired = read_json(ASSETS)

    concepts = {row["id"]: row for row in catalog["muscleConcepts"]}
    muscle_instances = {row["id"]: row for row in catalog["instances"]}
    parts = {row["id"]: row for row in catalog["muscleConcepts"] if row["entityType"] == "muscle_part"}
    structures = {row["id"]: row for row in catalog["structures"]}
    mesh_assets = {row["id"]: row for row in catalog["meshAssets"]}
    source_mesh_names = {row["file_id"]: row.get("english_name") for row in acquired.get("acquiredAssets", [])}

    categories = [
        {key: row[key] for key in ("id", "order", "labelKo", "labelEn")}
        for row in design["categories"]
    ]
    if len(categories) != 12 or len({row["id"] for row in categories}) != 12:
        raise ValueError("The navigation design must define exactly 12 unique categories")

    pilot_instances: set[str] = set()
    for link in t12["muscleLinks"]:
        iid = link["instanceId"]
        instance = muscle_instances.get(iid)
        if instance is None or instance["side"] != "right":
            raise ValueError(f"T12 pilot instance {iid} is missing or not right-sided")
        pilot_instances.add(iid)
    if len(pilot_instances) != 6:
        raise ValueError(f"Expected the existing six-muscle pilot; found {len(pilot_instances)} instances")

    memberships = []
    for iid in sorted(pilot_instances):
        instance = muscle_instances[iid]
        concept_id = instance["conceptId"]
        concept = concepts.get(concept_id)
        if concept is None or concept["entityType"] != "individual_muscle":
            raise ValueError(f"T12 pilot instance {iid} does not point to a canonical individual muscle")
        memberships.append({
            "id": f"HA-RM-LEG-{concept_id}",
            "categoryId": "leg",
            "entityKind": "muscle",
            "entityId": concept_id,
            "reason": "Existing right lower-leg pilot is the product entry for the leg category; source regionIds remain unchanged.",
            "productDecisionRef": "T15b-D01",
            "status": "decision_only",
        })

    bone_rows: dict[str, dict[str, Any]] = {}
    unresolved: list[dict[str, Any]] = []
    t12_path = ROOT / "atlas-data/manifests/canonical-geometry-t12.json"
    for row_index, row in enumerate(t12["unmappedStructureAssets"]):
        file_id = row["fileId"]
        add_bone_target(
            rows=bone_rows,
            structure_id=row.get("structureId"),
            mesh_id=row["meshAssetId"],
            source_name=source_mesh_names.get(file_id) or file_id,
            source_ref=ref(t12_path, f"/unmappedStructureAssets/{row_index}"),
            evidence_ids=[],
            source_linkage_state="inherited_t12_source_manifest",
            catalog_structures=structures,
            catalog_meshes=mesh_assets,
            unmapped=unresolved,
            model_id=t12["modelId"],
        )

    t13_path = ROOT / "atlas-data/manifests/derived-bones-t13.json"
    evidence_ids = {row["id"] for row in catalog["evidence"]}
    for row_index, row in enumerate(t13["viewerNodes"]):
        file_id = row["sourceFileId"]
        evidence_id = f"EV-BP3D4-{file_id}-T13-ASSET"
        inherited_evidence = [evidence_id] if evidence_id in evidence_ids else []
        add_bone_target(
            rows=bone_rows,
            structure_id=row.get("targetEntityId"),
            mesh_id=row["meshAssetId"],
            source_name=row["sourceName"],
            source_ref=ref(t13_path, f"/viewerNodes/{row_index}"),
            evidence_ids=inherited_evidence,
            source_linkage_state="inherited_t13_source_crosswalk",
            catalog_structures=structures,
            catalog_meshes=mesh_assets,
            unmapped=unresolved,
            model_id=t13["modelId"],
        )

    state_dimensions = {
        "sourceRelation": "inherited_crosswalk_only",
        "humanAnatomyReview": "not_reviewed",
        "staticGeometry": "mesh_candidate_or_context_only",
        "attachmentLocation": "none",
        "motion": "absent",
    }
    structure_instances = []
    structure_mesh_mappings = []
    for structure_id in sorted(bone_rows):
        row = bone_rows[structure_id]
        structure_instances.append(row["structureInstance"])
        for index, mapping in enumerate(row["meshMappings"], start=1):
            file_suffix = mapping["meshAssetId"].rsplit("FJ", 1)[-1]
            structure_mesh_mappings.append({
                "id": f"HA-SMAP-BP3D4-FJ{file_suffix}",
                "structureInstanceId": row["structureInstance"]["id"],
                "meshIds": [mapping["meshAssetId"]],
                "representationType": "whole_bone_context_only",
                "evidenceIds": mapping["evidenceIds"],
                "sourceRefs": mapping["sourceRefs"],
                "sourceLinkageState": mapping["sourceLinkageState"],
                "reviewState": "needs_review",
                "humanReviewState": "not_reviewed",
                "geometryState": "whole_structure_context_only",
                "attachmentLocationState": "none",
                "motionState": "absent",
            })

    t12_mesh_ids = sorted({row["meshAssetId"] for row in t12["muscleLinks"]} | {row["meshAssetId"] for row in t12["unmappedStructureAssets"]})
    model_uri = next(iter(mesh_assets.values()))["uri"]
    model_asset = next(mesh_assets[mesh_id] for mesh_id in t12_mesh_ids if mesh_id in mesh_assets)
    model_uri = model_asset["uri"]
    if any(mesh_assets[mesh_id]["uri"] != model_uri for mesh_id in t12_mesh_ids):
        raise ValueError("T12 pilot mesh assets do not share one source GLB; do not merge model scenes")

    selectable_bindings = []
    for mapping in catalog["meshMappings"]:
        mesh_id = mapping["meshIds"][0]
        if mesh_id not in t12_mesh_ids:
            continue
        iid = mapping["instanceIds"][0]
        instance = muscle_instances[iid]
        selection = {
            "kind": "muscle",
            "conceptId": instance["conceptId"],
            "instanceId": iid,
            "meshId": mesh_id,
        }
        if mapping["partIds"]:
            part_id = mapping["partIds"][0]
            part = parts.get(part_id)
            if part is None or part.get("parentId") != instance["conceptId"]:
                raise ValueError(f"Muscle part {part_id} does not belong to {instance['conceptId']}")
            selection["partId"] = part_id
        selectable_bindings.append({
            "meshAssetId": mesh_id,
            "sourceMappingId": mapping["id"],
            "reviewState": mapping["reviewState"],
            "selection": selection,
            "stateDimensions": state_dimensions,
        })

    for mapping in structure_mesh_mappings:
        mesh_id = mapping["meshIds"][0]
        if mesh_id not in t12_mesh_ids:
            continue
        structure_instance = next(row for row in structure_instances if row["id"] == mapping["structureInstanceId"])
        selectable_bindings.append({
            "meshAssetId": mesh_id,
            "sourceMappingId": mapping["id"],
            "reviewState": mapping["reviewState"],
            "selection": {
                "kind": "bone",
                "conceptId": structure_instance["structureId"],
                "instanceId": structure_instance["id"],
                "meshId": mesh_id,
            },
            "stateDimensions": state_dimensions,
        })

    context_bindings = [{
        "meshAssetId": row["meshAssetId"],
        "modelId": row["modelId"],
        "selection": None,
        "reasonCode": row["reasonCode"],
        "stateDimensions": {
            "sourceRelation": "source_identity_without_canonical_structure_id",
            "humanAnatomyReview": row["humanReviewState"],
            "staticGeometry": row["geometryState"],
            "attachmentLocation": "none",
            "motion": row["motionState"],
        },
    } for row in unresolved if row["modelId"] == t12["modelId"]]

    scene = {
        "id": "HA-SCENE-LEG-RIGHT-PILOT-T12B",
        "categoryId": "leg",
        "revision": "T15b-navigation-v1",
        "availability": "partial",
        "assetRefs": [{
            "modelId": t12["modelId"],
            "uri": model_uri,
            "sha256": t12["sourceGlbSha256"],
            "meshAssetIds": t12_mesh_ids,
        }],
        "selectableBindings": sorted(selectable_bindings, key=lambda row: row["meshAssetId"]),
        "contextBindings": context_bindings,
        "defaultView": {"side": "right", "selection": None},
        "frameId": t12["frameId"],
        "units": t12["units"],
        "poseId": t12["poseId"],
        "modelId": t12["modelId"],
        "stateDimensions": {
            "sourceRelation": "inherited_t07_t12_source_crosswalks",
            "humanAnatomyReview": "not_reviewed",
            "staticGeometry": "partial_static_mesh_candidates",
            "attachmentLocation": "none",
            "motion": "absent",
        },
    }

    # T13 is a separate source model. It may share the leg category only while
    # its recorded source, frame, units and reference pose match the T12 scene.
    if (t13["sourceId"] != t12["sourceId"] or
            t13["transform"]["frameId"] != t12["frameId"] or
            t13["transform"]["targetUnits"] != t12["units"] or
            t13["transform"]["poseId"] != t12["poseId"]):
        raise ValueError("T12/T13 source frame or pose differs; do not combine these leg scenes")
    t13_mesh_ids = sorted(row["meshAssetId"] for row in t13["viewerNodes"])
    t13_uri = mesh_assets[t13_mesh_ids[0]]["uri"]
    if any(mesh_assets[mesh_id]["uri"] != t13_uri or mesh_assets[mesh_id]["hash"] != t13["glb"]["sha256"] for mesh_id in t13_mesh_ids):
        raise ValueError("T13 bone meshes do not share the recorded GLB revision")
    t13_bindings = []
    for mapping in structure_mesh_mappings:
        mesh_id = mapping["meshIds"][0]
        if mesh_id not in t13_mesh_ids:
            continue
        instance = next(row for row in structure_instances if row["id"] == mapping["structureInstanceId"])
        t13_bindings.append({
            "meshAssetId": mesh_id,
            "sourceMappingId": mapping["id"],
            "reviewState": mapping["reviewState"],
            "selection": {"kind": "bone", "conceptId": instance["structureId"], "instanceId": instance["id"], "meshId": mesh_id},
            "stateDimensions": state_dimensions,
        })
    t13_context = [{
        "meshAssetId": row["meshAssetId"], "modelId": row["modelId"], "selection": None,
        "reasonCode": row["reasonCode"],
        "stateDimensions": {
            "sourceRelation": "source_identity_without_canonical_structure_id",
            "humanAnatomyReview": row["humanReviewState"],
            "staticGeometry": row["geometryState"],
            "attachmentLocation": "none", "motion": row["motionState"],
        },
    } for row in unresolved if row["modelId"] == t13["modelId"]]
    t13_scene = {
        "id": "HA-SCENE-LEG-RIGHT-BONES-T13", "categoryId": "leg", "revision": "T15e-scene-v1",
        "availability": "partial",
        "assetRefs": [{"modelId": t13["modelId"], "uri": t13_uri, "sha256": t13["glb"]["sha256"], "meshAssetIds": t13_mesh_ids}],
        "selectableBindings": sorted(t13_bindings, key=lambda row: row["meshAssetId"]),
        "contextBindings": sorted(t13_context, key=lambda row: row["meshAssetId"]),
        "defaultView": {"side": "right", "selection": None},
        "frameId": t13["transform"]["frameId"], "units": t13["transform"]["targetUnits"],
        "poseId": t13["transform"]["poseId"], "modelId": t13["modelId"],
        "stateDimensions": {
            "sourceRelation": "inherited_t13_source_crosswalk", "humanAnatomyReview": "not_reviewed",
            "staticGeometry": "whole_bone_context_only", "attachmentLocation": "none", "motion": "absent",
        },
    }

    return {
        "schemaVersion": "T15b-navigation-v1",
        "status": "partial_pilot_contract",
        "sourceClassification": {
            "path": "atlas-data/catalog/region-tree.json",
            "policy": "source regions remain unchanged; product categories and memberships are a separate overlay",
        },
        "categories": categories,
        "memberships": memberships,
        "structureInstances": structure_instances,
        "structureMeshMappings": structure_mesh_mappings,
        "unmappedMeshContexts": unresolved,
        "sceneManifests": [scene, t13_scene],
        "migrationNotes": {
            "canonicalCatalogMutation": False,
            "legacyMuscleInstancesPreserved": True,
            "legacyMeshMappingsPreserved": True,
            "userSpatialDraftsReadOrChanged": False,
            "humanApprovalCreated": False,
            "anatomicalClaimsCreated": False,
            "sourceRegionsCopiedOrRenamed": False,
            "motionAssetsCreated": False,
            "unresolvedSourceMeshesRemainUnbound": True,
        },
    }


def summarize(value: dict[str, Any]) -> dict[str, Any]:
    catalog = read_json(CATALOG)
    t12 = read_json(T12)
    t13 = read_json(T13)
    design = read_json(DESIGN)
    inputs = [DESIGN, CATALOG, T12, T13, ASSETS]
    unresolved = [
        {"meshAssetId": row["meshAssetId"], "modelId": row["modelId"], "reasonCode": row["reasonCode"]}
        for row in value["unmappedMeshContexts"]
    ]
    return {
        "status": value["status"],
        "inputHashes": {path.relative_to(ROOT).as_posix(): file_sha256(path) for path in inputs},
        "sourceInventoryBefore": {
            "sourceRegionNodesExcludingRoot": len(read_json(ROOT / "atlas-data/catalog/region-tree.json")["regions"]),
            "sourceRegionRootId": read_json(ROOT / "atlas-data/catalog/region-tree.json")["root_id"],
            "sourceRegionRecordsIncludingRoot": len(read_json(ROOT / "atlas-data/catalog/region-tree.json")["regions"]) + 1,
            "canonicalMuscleConcepts": len(catalog["entities"]["muscleConcepts"]),
            "canonicalMuscleInstances": len(catalog["entities"]["instances"]),
            "canonicalMeshMappings": len(catalog["entities"]["meshMappings"]),
            "canonicalBoneStructures": sum(row["kind"] == "bone" for row in catalog["entities"]["structures"]),
            "canonicalSpatialAnnotations": len(catalog["entities"]["spatialAnnotations"]),
            "T12PilotMeshes": t12["coverage"]["meshAssets"],
            "T12PilotMuscleInstances": t12["coverage"]["rightMuscleInstances"],
            "T13BoneMeshes": len(t13["viewerNodes"]),
        },
        "counts": {
            "categories": len(value["categories"]),
            "productDecisionMemberships": len(value["memberships"]),
            "boneStructureInstances": len(value["structureInstances"]),
            "boneMeshMappings": len(value["structureMeshMappings"]),
            "unmappedSourceContexts": len(value["unmappedMeshContexts"]),
            "sceneManifests": len(value["sceneManifests"]),
            "sceneSelectableBindings": sum(len(row["selectableBindings"]) for row in value["sceneManifests"]),
            "sceneContextBindings": sum(len(row["contextBindings"]) for row in value["sceneManifests"]),
        },
        "migrationDelta": {
            "writeTarget": OUTPUT.relative_to(ROOT).as_posix(),
            "canonicalFilesAddedOrChanged": [],
            "sourceRegionRecordsAddedOrChanged": 0,
            "sourceMembershipsInferred": 0,
            "productDecisionMembershipsAdded": len(value["memberships"]),
            "structureInstancesAddedInOverlay": len(value["structureInstances"]),
            "boneMeshMappingsAddedInOverlay": len(value["structureMeshMappings"]),
            "unconfirmedMeshesLeftUnbound": len(unresolved),
            "unconfirmedMeshTargets": unresolved,
            "sceneAvailability": {row["categoryId"]: row["availability"] for row in value["sceneManifests"]},
        },
        "preservation": value["migrationNotes"],
        "generatedSha256": sha256_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Print non-mutating migration preview")
    mode.add_argument("--write", action="store_true", help="Write generated overlay only")
    mode.add_argument("--check", action="store_true", help="Fail if committed overlay differs from generated data")
    parser.add_argument("--report", type=Path, help="Write preview summary JSON (dry-run only)")
    args = parser.parse_args()

    generated = build()
    generated_text = json.dumps(generated, ensure_ascii=False, indent=2) + "\n"
    if args.dry_run:
        summary = summarize(generated)
        summary["mode"] = "dry_run_no_project_data_mutated"
        summary["outputPath"] = OUTPUT.relative_to(ROOT).as_posix()
        if OUTPUT.exists():
            current = OUTPUT.read_text(encoding="utf-8")
            diff = list(difflib.unified_diff(current.splitlines(), generated_text.splitlines(), fromfile="current", tofile="generated", lineterm=""))
            summary["existingOutputDiffLines"] = len(diff)
            summary["existingOutputDiffSha256"] = sha256_bytes("\n".join(diff).encode("utf-8")) if diff else None
        else:
            summary["existingOutputDiffLines"] = None
            summary["existingOutputDiffSha256"] = None
        if args.report:
            report = args.report if args.report.is_absolute() else ROOT / args.report
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    if args.report:
        parser.error("--report is available only with --dry-run")
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(generated_text, encoding="utf-8")
        print(json.dumps({"written": OUTPUT.relative_to(ROOT).as_posix(), "sha256": file_sha256(OUTPUT), "summary": summarize(generated)}, ensure_ascii=False, indent=2))
        return 0

    if not OUTPUT.exists():
        print(f"missing generated overlay: {OUTPUT.relative_to(ROOT)}", file=sys.stderr)
        return 1
    current = OUTPUT.read_text(encoding="utf-8")
    if current != generated_text:
        diff = "\n".join(difflib.unified_diff(current.splitlines(), generated_text.splitlines(), fromfile="committed", tofile="generated", lineterm=""))
        print(diff, file=sys.stderr)
        return 1
    print(json.dumps({"check": "passed", "path": OUTPUT.relative_to(ROOT).as_posix(), "sha256": file_sha256(OUTPUT), "summary": summarize(generated)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
