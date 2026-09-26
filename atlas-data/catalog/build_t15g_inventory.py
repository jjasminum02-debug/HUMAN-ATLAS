#!/usr/bin/env python3
"""Build T15g planning-only inventories from the existing partial catalog.

This tool writes review-queue/planning artifacts. It deliberately does not
modify canonical IDs, runtime memberships, source assets, or learner data.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
INPUTS = [
    "atlas-data/catalog/canonical-catalog.json",
    "atlas-data/catalog/catalog-status.json",
    "atlas-data/catalog/region-tree.json",
    "atlas-data/catalog/source-crosswalk.json",
    "atlas-data/terminology/learning-names.json",
    "atlas-data/manifests/scope.json",
    "atlas-data/manifests/assets.json",
    "atlas-data/manifests/derived-assets-t07.json",
    "atlas-data/manifests/derived-bones-t13.json",
    "atlas-data/navigation/atlas-navigation.json",
    "work/task-registry-r13.json",
]
OUTPUTS = {
    "inventory": "atlas-data/catalog/whole-body-inventory-t15g.json",
    "crosswalk": "work/review-queue/region-crosswalk-t15g.json",
    "batches": "work/review-queue/expansion-batches-t15g.json",
}
ROUTING = {
    "head": {"targets": ["head"], "rule": "merge_head_face_mastication_eye_tongue"},
    "face": {"targets": ["head"], "rule": "merge_head_face_mastication_eye_tongue"},
    "mastication": {"targets": ["head"], "rule": "merge_head_face_mastication_eye_tongue"},
    "eye": {"targets": ["head"], "rule": "merge_head_face_mastication_eye_tongue"},
    "tongue": {"targets": ["head"], "rule": "merge_head_face_mastication_eye_tongue"},
    "pharynx": {"targets": [], "rule": "manual_per_concept_boundary_decision"},
    "larynx": {"targets": [], "rule": "manual_per_concept_boundary_decision"},
    "neck": {"targets": ["neck"], "rule": "candidate_same_named_region_not_membership"},
    "back": {"targets": ["back"], "rule": "candidate_same_named_region_not_membership"},
    "thorax_respiratory": {"targets": ["thorax"], "rule": "candidate_same_named_region_not_membership"},
    "abdominal_wall": {"targets": ["abdomen-lumbar"], "rule": "candidate_same_named_region_not_membership"},
    "pelvic_floor_perineum": {"targets": ["pelvis-perineum"], "rule": "candidate_same_named_region_not_membership"},
    "shoulder": {"targets": ["shoulder-scapular"], "rule": "candidate_same_named_region_not_membership"},
    "upper_extremity": {"targets": ["upper-limb"], "rule": "candidate_same_named_region_not_membership"},
    "hand": {"targets": ["upper-limb"], "rule": "candidate_same_named_region_not_membership"},
    "gluteal": {"targets": ["gluteal-hip"], "rule": "candidate_same_named_region_not_membership"},
    "lower_extremity": {"targets": [], "rule": "manual_per_concept_split_thigh_leg_foot"},
    "foot": {"targets": ["foot"], "rule": "candidate_same_named_region_not_membership"},
}


def read_json(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> dict[str, Any]:
    canonical = read_json(INPUTS[0])
    catalog_status = read_json(INPUTS[1])
    region_tree = read_json(INPUTS[2])
    source_crosswalk = read_json(INPUTS[3])
    learning_names = read_json(INPUTS[4])
    scope = read_json(INPUTS[5])
    asset_manifest = read_json(INPUTS[6])
    t07 = read_json(INPUTS[7])
    t13 = read_json(INPUTS[8])
    navigation = read_json(INPUTS[9])
    registry = read_json(INPUTS[10])

    entities = canonical["entities"]
    concepts = entities["muscleConcepts"]
    concept_by_id = {row["id"]: row for row in concepts}
    if len(concept_by_id) != len(concepts):
        raise ValueError("duplicate canonical muscle concept IDs")
    crosswalk_by_id = {row["stableConceptId"]: row for row in source_crosswalk["catalogItems"]}
    if len(crosswalk_by_id) != len(source_crosswalk["catalogItems"]):
        raise ValueError("duplicate source-crosswalk stableConceptId")
    if set(crosswalk_by_id) != set(concept_by_id):
        raise ValueError("source crosswalk IDs do not exactly match the current partial muscle catalog")
    for concept_id, row in crosswalk_by_id.items():
        concept = concept_by_id[concept_id]
        if row["entityType"] != concept["entityType"] or row["regionIds"] != concept["regionIds"] or row.get("parentConceptId") != concept.get("parentId"):
            raise ValueError(f"source crosswalk classification/region/parent mismatch for {concept_id}")
    learning_by_id = {row["id"]: row for row in learning_names["entries"]}
    membership_by_id: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in navigation["memberships"]:
        membership_by_id[row["entityId"]].append(row)

    concept_mesh_ids: dict[str, set[str]] = collections.defaultdict(set)
    concept_map_ids: dict[str, set[str]] = collections.defaultdict(set)
    instance_by_id = {row["id"]: row for row in entities["instances"]}
    for mapping in entities["meshMappings"]:
        target_ids = {instance_by_id[i]["conceptId"] for i in mapping.get("instanceIds", []) if i in instance_by_id}
        for target_id in target_ids:
            if target_id in concept_by_id:
                concept_mesh_ids[target_id].update(mapping.get("meshIds", []))
                concept_map_ids[target_id].add(mapping["id"])
    # Parts point to parent muscle IDs; map crosswalk entries to the same stable IDs.
    parts_by_parent: dict[str, list[str]] = collections.defaultdict(list)
    for row in concepts:
        if row["entityType"] == "muscle_part" and row.get("parentId"):
            parts_by_parent[row["parentId"]].append(row["id"])
    for mapping in entities["meshMappings"]:
        parent_targets = {instance_by_id[i]["conceptId"] for i in mapping.get("instanceIds", []) if i in instance_by_id}
        parent_targets.update(
            concept_by_id[part].get("parentId")
            for part in mapping.get("partIds", [])
            if part in concept_by_id and concept_by_id[part].get("parentId")
        )
        for target_id in parent_targets:
            if target_id in concept_by_id and concept_by_id[target_id]["entityType"] == "individual_muscle":
                concept_mesh_ids[target_id].update(mapping.get("meshIds", []))
                concept_map_ids[target_id].add(mapping["id"])

    bp3d_by_part = {row["stableConceptId"]: row for row in source_crosswalk["bodyParts3dMappings"]}
    for part_id, mapping in bp3d_by_part.items():
        part = concept_by_id.get(part_id)
        if part and part.get("parentId") in concept_by_id:
            concept_mesh_ids[part["parentId"]].add(f"HA-MESH-BP3D4-{mapping['elementFileId']}")

    region_counts: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    for concept in concepts:
        for region_id in concept.get("regionIds", []):
            region_counts[region_id][concept["entityType"]] += 1
    crosswalk_row_counts = collections.Counter(region_id for row in source_crosswalk["catalogItems"] for region_id in row["regionIds"])

    muscle_entries = []
    for concept in sorted(concepts, key=lambda item: item["id"]):
        identifier = concept["id"]
        row = crosswalk_by_id[identifier]
        overlay = learning_by_id.get(identifier)
        related_parts = sorted(parts_by_parent.get(identifier, []))
        related_source_meshes = [
            {
                "stablePartId": part_id,
                "sourceCrosswalk": bp3d_by_part[part_id],
                "localAssetExists": (ROOT / bp3d_by_part[part_id]["localAsset"]).is_file(),
                "localAssetSha256": sha256(ROOT / bp3d_by_part[part_id]["localAsset"]) if (ROOT / bp3d_by_part[part_id]["localAsset"]).is_file() else None,
            }
            for part_id in related_parts if part_id in bp3d_by_part
        ]
        muscle_entries.append({
            "id": identifier,
            "entityType": concept["entityType"],
            "parentId": concept.get("parentId"),
            "sourceRegionIds": concept["regionIds"],
            "sourceCrosswalk": {
                "sourceId": row["sourceId"],
                "edition": row["edition"],
                "part": row["part"],
                "printedPage": row["printedPage"],
                "tableRow": row["tableRow"],
                "latinTextObservation": row["latinTextObservation"],
                "englishTextObservation": row["englishTextObservation"],
                "termCellRoleStatus": row["termCellRoleStatus"],
                "reviewState": row["reviewState"],
                "denominatorTreatment": row["denominatorTreatment"],
            },
            "learningNameOverlay": ({
                "present": True,
                "label": overlay.get("label"),
                "korean": overlay.get("korean"),
                "english": overlay.get("english"),
                "status": overlay.get("status"),
                "humanReviewed": overlay.get("humanReviewed", False),
            } if overlay else {
                "present": False,
                "label": None,
                "korean": None,
                "english": None,
                "status": "missing_overlay_entry",
                "humanReviewed": False,
            }),
            "currentProductMemberships": membership_by_id.get(identifier, []),
            "existingMeshCandidates": sorted(concept_mesh_ids.get(identifier, set())),
            "existingMeshMappingIds": sorted(concept_map_ids.get(identifier, set())),
            "existingMeshMappingStates": [
                {
                    "mappingId": mapping["id"],
                    "partIds": mapping.get("partIds", []),
                    "meshIds": mapping.get("meshIds", []),
                    "evidenceIds": mapping.get("evidenceIds", []),
                    "reviewState": mapping.get("reviewState"),
                }
                for mapping in entities["meshMappings"]
                if mapping["id"] in concept_map_ids.get(identifier, set())
            ],
            "relatedSourceMeshCrosswalks": related_source_meshes,
            "relatedPartIds": related_parts,
            "humanAnatomyReview": "not_recorded_as_approved",
            "motionEvidence": "absent",
        })

    bone_structures = [row for row in entities["structures"] if row.get("kind") == "bone"]
    bone_by_id = {row["id"]: row for row in bone_structures}
    nav_instances = {row["id"]: row for row in navigation["structureInstances"]}
    bone_maps_by_id: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for mapping in navigation["structureMeshMappings"]:
        instance = nav_instances.get(mapping["structureInstanceId"])
        if instance and instance["structureId"] in bone_by_id:
            bone_maps_by_id[instance["structureId"]].append(mapping)
    scene_bindings_by_id: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for scene in navigation["sceneManifests"]:
        for binding in scene.get("selectableBindings", []):
            selection = binding.get("selection") or {}
            if selection.get("kind") == "bone" and selection.get("conceptId") in bone_by_id:
                scene_bindings_by_id[selection["conceptId"]].append({
                    "sceneId": scene["id"],
                    "meshAssetId": binding.get("meshAssetId"),
                    "reviewState": binding.get("reviewState"),
                })
    bone_terms = {row["conceptId"]: row for row in entities["terms"] if row["conceptId"] in bone_by_id}
    related_bones_by_file = {row["element_file_id"]: row for row in asset_manifest["relatedBoneInventory"]}
    t13_by_file = {row["fileId"]: row for row in t13["sourceAssets"]}
    raw_obj_by_file_id = {path.stem: path for path in (ROOT / "atlas-data/assets").rglob("*.obj")}
    bone_entries = []
    for structure in sorted(bone_structures, key=lambda item: item["id"]):
        identifier = structure["id"]
        maps = bone_maps_by_id.get(identifier, [])
        mapped_mesh_ids = sorted({mesh_id for row in maps for mesh_id in row["meshIds"]})
        mapped_file_ids = sorted({mesh_id.rsplit("-", 1)[-1] for mesh_id in mapped_mesh_ids})
        source_assets = []
        for file_id in mapped_file_ids:
            source = t13_by_file.get(file_id) or related_bones_by_file.get(file_id)
            if source:
                local_path = source.get("localPath", source.get("local_asset"))
                absolute_local_path = ROOT / local_path if local_path else raw_obj_by_file_id.get(file_id)
                source_assets.append({
                    "fileId": file_id,
                    "sourceName": source.get("sourceName"),
                    "externalConceptId": source.get("externalConceptId", source.get("concept_id")),
                    "localPath": local_path or (absolute_local_path.relative_to(ROOT).as_posix() if absolute_local_path else None),
                    "expectedSourceSha256": source.get("sha256"),
                    "localAssetExists": bool(absolute_local_path and absolute_local_path.is_file()),
                    "localAssetSha256": sha256(absolute_local_path) if absolute_local_path and absolute_local_path.is_file() else None,
                    "availabilityInOriginalT02Manifest": related_bones_by_file.get(file_id, {}).get("availability"),
                })
        bone_entries.append({
            "id": identifier,
            "kind": structure["kind"],
            "historicalEnglishTerm": bone_terms.get(identifier, {}).get("text"),
            "termEvidence": {
                "termId": bone_terms.get(identifier, {}).get("id"),
                "edition": bone_terms.get(identifier, {}).get("edition"),
                "reviewState": bone_terms.get(identifier, {}).get("reviewState"),
            },
            "currentProductMemberships": membership_by_id.get(identifier, []),
            "rightSideSceneBindings": scene_bindings_by_id.get(identifier, []),
            "structureMeshMappingIds": [row["id"] for row in maps],
            "meshAssetIds": mapped_mesh_ids,
            "sourceAssets": source_assets,
            "structureMeshMappingStates": [
                {
                    "mappingId": row["id"],
                    "meshIds": row["meshIds"],
                    "sourceLinkageState": row.get("sourceLinkageState"),
                    "sourceRefs": row.get("sourceRefs", []),
                    "reviewState": row.get("reviewState"),
                    "humanReviewState": row.get("humanReviewState"),
                    "geometryState": row.get("geometryState"),
                    "attachmentLocationState": row.get("attachmentLocationState"),
                    "motionState": row.get("motionState"),
                }
                for row in maps
            ],
            "humanAnatomyReview": "not_reviewed" if maps else "not_recorded_as_approved",
            "geometryMeaning": "whole_bone_context_only" if maps else "no_current_navigation_mesh_mapping",
            "motionEvidence": "absent",
        })

    muscles = [row for row in concepts if row["entityType"] == "individual_muscle"]
    groups = [row for row in concepts if row["entityType"] == "muscle_group"]
    parts = [row for row in concepts if row["entityType"] == "muscle_part"]
    names_overlap = set(concept_by_id) & set(learning_by_id)
    nav_muscle_membership_categories: dict[str, set[str]] = collections.defaultdict(set)
    for row in navigation["memberships"]:
        if row["entityKind"] == "muscle":
            nav_muscle_membership_categories[row["entityId"]].add(row["categoryId"])
    multi_region_ids = sorted(k for k, v in nav_muscle_membership_categories.items() if len(v) > 1)
    local_obj_files = sorted((ROOT / "atlas-data/assets").rglob("*.obj"))
    local_glb_files = sorted((ROOT / "atlas-data/assets").rglob("*.glb"))
    t13_source_asset_hash_checks = []
    for source_asset in t13["sourceAssets"]:
        local_path = ROOT / source_asset["localPath"]
        actual_hash = sha256(local_path) if local_path.is_file() else None
        t13_source_asset_hash_checks.append({
            "fileId": source_asset["fileId"],
            "path": source_asset["localPath"],
            "expectedSha256": source_asset["sha256"],
            "actualSha256": actual_hash,
            "exists": local_path.is_file(),
            "passed": local_path.is_file() and actual_hash == source_asset["sha256"],
        })
    unmapped_context_details = []
    for context in navigation["unmappedMeshContexts"]:
        file_id = context["meshAssetId"].rsplit("-", 1)[-1]
        asset_path = raw_obj_by_file_id.get(file_id)
        unmapped_context_details.append({
            **context,
            "sourceFileId": file_id,
            "rawSourceAssetPath": asset_path.relative_to(ROOT).as_posix() if asset_path else None,
            "rawSourceAssetExists": bool(asset_path and asset_path.is_file()),
            "rawSourceAssetSha256": sha256(asset_path) if asset_path and asset_path.is_file() else None,
        })
    scene_asset_hash_checks = []
    for scene in navigation["sceneManifests"]:
        for asset in scene["assetRefs"]:
            asset_path = ROOT / asset["uri"]
            scene_asset_hash_checks.append({
                "sceneId": scene["id"],
                "path": asset["uri"],
                "expectedSha256": asset["sha256"],
                "actualSha256": sha256(asset_path) if asset_path.is_file() else None,
                "exists": asset_path.is_file(),
            })
    registry_ids = [int(task["id"][1:]) for task in registry.get("tasks", []) if task.get("id", "").startswith("T") and task["id"][1:].isdigit()]
    next_task_id_candidate = f"T{max(registry_ids, default=40) + 1}"

    inventory = {
        "revision": "T15g-planning-inventory-v1",
        "generatedBy": "atlas-data/catalog/build_t15g_inventory.py",
        "status": "planning_only_partial_inventory",
        "sourceCatalogStatus": catalog_status["status"],
        "denominatorFrozen": False,
        "wholeBodyIndividualMuscleCount": None,
        "coveragePercent": None,
        "scope": {
            "manifestId": scope["manifest_id"],
            "revision": scope["revision"],
            "targetEntity": scope["target_entity"],
            "sourceRegions": len(scope["regions"]),
            "sourceRootIsSynthetic": True,
        },
        "inputs": [{"path": rel, "sha256": sha256(ROOT / rel)} for rel in INPUTS],
        "counts": {
            "muscleConcepts": {
                "uniqueStableIds": len(concepts),
                "byEntityType": dict(collections.Counter(row["entityType"] for row in concepts)),
                "separatelyCounted": {
                    "individualMuscleConcepts": len(muscles),
                    "muscleGroups": len(groups),
                    "muscleParts": len(parts),
                    "variantRecords": 0,
                "sideInstances": len(entities["instances"]),
                "sideInstancesBySide": dict(collections.Counter(row["side"] for row in entities["instances"])),
                "individualMuscleConceptsWithMeshCandidate": sum(1 for row in concepts if row["entityType"] == "individual_muscle" and concept_mesh_ids.get(row["id"])),
                    "canonicalMeshAssetRecords": len(entities["meshAssets"]),
                    "canonicalMuscleMeshMappings": len(entities["meshMappings"]),
                },
                "sourceCrosswalkRows": len(source_crosswalk["catalogItems"]),
                "sourceCrosswalkIdsExactlyMatchCurrentPartialCatalog": set(crosswalk_by_id) == set(concept_by_id),
                "learningNameOverlayEntries": len(learning_by_id),
                "learningNameCanonicalOverlap": len(names_overlap),
                "learningNameMissingCanonicalIds": sorted(set(concept_by_id) - set(learning_by_id)),
                "lookupOnlyOverlayIdsNotInCanonicalCatalog": sorted(set(learning_by_id) - set(concept_by_id)),
                "confirmedCurrentProductMembershipRows": sum(1 for row in navigation["memberships"] if row["entityKind"] == "muscle"),
                "currentlyMultiCategoryMuscleIds": multi_region_ids,
            },
            "bones": {
                "uniqueCanonicalBoneIds": len(bone_structures),
                "uniqueRightSceneBoundBoneIds": len(scene_bindings_by_id),
                "canonicalStructureMeshMappings": len(navigation["structureMeshMappings"]),
                "currentBoneProductMembershipRows": sum(1 for row in navigation["memberships"] if row["entityKind"] == "bone"),
            },
            "navigation": {
                "productCategories": len(navigation["categories"]),
                "regionMembershipRows": len(navigation["memberships"]),
                "muscleMembershipRowsByCategory": dict(collections.Counter(row["categoryId"] for row in navigation["memberships"] if row["entityKind"] == "muscle")),
                "boneMembershipRowsByCategory": dict(collections.Counter(row["categoryId"] for row in navigation["memberships"] if row["entityKind"] == "bone")),
                "sceneManifests": len(navigation["sceneManifests"]),
                "categoriesWithScene": sorted({row["categoryId"] for row in navigation["sceneManifests"]}),
                "categoriesWithoutScene": sorted({row["id"] for row in navigation["categories"]} - {row["categoryId"] for row in navigation["sceneManifests"]}),
                "unboundMeshContexts": len(navigation["unmappedMeshContexts"]),
                "categoryMatrix": [
                    {
                        "categoryId": category["id"],
                        "labelKo": category["labelKo"],
                        "muscleMembershipCount": sum(1 for row in navigation["memberships"] if row["categoryId"] == category["id"] and row["entityKind"] == "muscle"),
                        "boneMembershipCount": sum(1 for row in navigation["memberships"] if row["categoryId"] == category["id"] and row["entityKind"] == "bone"),
                        "sceneIds": [scene["id"] for scene in navigation["sceneManifests"] if scene["categoryId"] == category["id"]],
                        "sceneAvailability": "partial" if any(scene["categoryId"] == category["id"] and scene.get("availability") == "partial" for scene in navigation["sceneManifests"]) else "unavailable",
                    }
                    for category in navigation["categories"]
                ],
            },
            "localAssets": {
                "sourceObjFiles": len(local_obj_files),
                "sourceObjFileInventory": [
                    {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}
                    for path in local_obj_files
                ],
                "derivedGlbFiles": len(local_glb_files),
                "derivedGlbFileInventory": [
                    {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}
                    for path in local_glb_files
                ],
                "pilotT07SceneMeshNodes": len(t07["meshNodes"]),
                "t13BoneSceneMeshNodes": len(t13["meshNodes"]),
                "t13SourceAssetHashChecks": t13_source_asset_hash_checks,
                "verifiedSceneGlbReferences": scene_asset_hash_checks,
            },
        },
        "sourceRegionCounts": [
            {
                "id": row["id"],
                "label": row["label"],
                "currentPartialCatalogRows": crosswalk_row_counts[row["id"]],
                "currentCanonicalCountsByType": dict(region_counts[row["id"]]),
                "sourceCoverageStatus": next((x.get("coverageStatus") for x in region_tree["regions"] if x["id"] == row["id"]), None),
                "wholeRegionEnumerationStatus": "not_established_by_partial_source_extract",
            }
            for row in scope["regions"]
        ],
        "currentMuscleConceptInventory": muscle_entries,
        "currentCanonicalBoneInventory": bone_entries,
        "knownUnmappedMeshContexts": unmapped_context_details,
        "knownGaps": {
            "wholeBodyMissingConceptIds": None,
            "wholeBodyMissingMuscleConceptIds": None,
            "wholeBodyMissingBoneIds": None,
            "whyNull": "No frozen complete authority-derived denominator; the 85 current crosswalk rows are a partial extraction, not a whole-body list.",
            "sourceRegionsWithZeroCapturedRows": [row["id"] for row in scope["regions"] if crosswalk_row_counts[row["id"]] == 0],
            "sourceRegionsWithPartialRowsStillNotExhaustive": [row["id"] for row in scope["regions"] if crosswalk_row_counts[row["id"]] > 0],
            "untranslatedOrMissingDisplayNameIds": sorted(set(concept_by_id) - set(learning_by_id)),
            "canonicalBoneWithoutCurrentRightSceneBinding": sorted(set(bone_by_id) - set(scene_bindings_by_id)),
            "surfaceAnnotations": len(entities["spatialAnnotations"]),
            "attachmentsAwaitingSurfaceReview": len(entities["attachments"]),
            "motionRecords": len(entities["jointActions"]) + len(entities["modelElements"]),
            "humanReviewRecords": len(entities["reviews"]),
        },
        "interpretationBoundary": [
            "This is a planning inventory of currently recorded rows, not a complete anatomy catalog.",
            "Group, individual muscle, part, side instance, mesh asset, and scene binding are separate counts.",
            "Source-region tags are not product RegionMembership decisions.",
            "Mesh existence or source crosswalk does not imply reviewed anatomical identity, attachment surface, or movement.",
            "All unconfirmed concepts and asset relations remain unassigned, missing, or review-pending; no anatomy was inferred.",
        ],
    }

    crosswalk = {
        "revision": "T15g-source-region-routing-candidates-v1",
        "status": "candidate_policy_only_not_runtime_memberships",
        "denominatorFrozen": False,
        "sourceTaxonomyPath": "atlas-data/manifests/scope.json",
        "productTaxonomyPath": "atlas-data/navigation/atlas-navigation.json",
        "policyReference": "design/2026-09-25-muscle-atlas/06-REGION12-MUSCLE-BONE-REVISION.md#2",
        "rules": [
            "Preserve all source region IDs and stable concept IDs.",
            "A candidate route is not an approved per-concept membership and never creates a second concept ID.",
            "For a concept genuinely spanning product regions, create evidence-backed memberships using the same stable ID in each relevant category.",
            "Resolve lower_extremity records individually; do not copy the source region to thigh, leg, and foot.",
            "Resolve pharynx/larynx and other boundaries individually; unresolved concepts stay in an internal unassigned queue.",
            "Region scene context, including nearby bones, does not establish muscle or bone membership.",
        ],
        "sourceRegions": [
            {
                "sourceRegionId": row["id"],
                "sourceLabel": row["label"],
                "capturedRows": crosswalk_row_counts[row["id"]],
                "candidateProductCategoryIds": ROUTING[row["id"]]["targets"],
                "routingRule": ROUTING[row["id"]]["rule"],
                "status": "per_concept_membership_review_required",
                "membershipRowsCreated": 0,
                "notes": "Candidate taxonomy routing only; this generated plan does not add runtime membership rows.",
            }
            for row in scope["regions"]
        ],
        "currentConfirmedProductMemberships": navigation["memberships"],
        "unassignedPolicy": "Do not invent a 13th product category or fill uncertain membership by anatomical guess; keep candidates internal until evidence and product decision are recorded.",
    }

    batches = {
        "revision": "T15g-expansion-batches-v1",
        "status": "plan_only_ids_not_frozen",
        "denominatorFrozen": False,
        "taskNumberPolicyReference": "design/2026-09-25-muscle-atlas/08-SERIAL-ROADMAP-AND-GIT.md#더-필요한-task를-추가하는-방법",
        "gates": [
            {
                "taskId": "T32",
                "role": "freeze authoritative whole-body inventory and per-region gaps after T31",
                "maxConcepts": None,
                "requiredOutputs": ["frozen authority and edition", "stable unique IDs", "group/part/variant exclusions", "per-concept region decisions", "source/term/asset gaps", "bounded task specs"],
                "status": "planned_not_started",
            },
            {
                "taskId": "T33",
                "role": "first structure expansion batch, only after T32 freezes IDs",
                "maxConcepts": 10,
                "targetStableIds": [],
                "targetStableIdsStatus": "pending_T32; do not fabricate IDs",
                "acceptance": ["all source fields have edition/locator or explicit missing reason", "stable-ID and parent/type/reference validation", "name/text/source/membership states separated", "asset missingness separate from surface and human-review state"],
                "status": "planned_not_started",
            },
            {
                "taskId": "T41+",
                "role": "additional independent data batches after T32",
                "maxConcepts": 10,
                "targetStableIds": [],
                "targetStableIdsStatus": "assigned only after T32 and registry audit",
                "numbering": "next unused integer in work/task-registry-r13.json; register exact scope/dependency/output/acceptance before execution",
                "status": "not_issued",
            },
        ],
        "sceneBatchRule": {
            "maxScenesPerTask": 1,
            "currentSceneCategoryIds": sorted({row["categoryId"] for row in navigation["sceneManifests"]}),
            "currentSceneStatus": "leg has two partial scene manifests; other categories have no scene manifest",
            "newSceneTaskRequires": ["source license", "asset hash", "side", "frame", "units", "pose limits", "scene-scoped validator", "actual browser validation"],
            "taskIds": "not issued until T32 work sizing and registry audit",
            "runtimeValidationDependency": {
                "taskId": "T15f-FU01",
                "status": "not_started_backlog",
                "requirement": "Complete before T33 adds new regional canonical/runtime scene data: replace manifest.ts global canonical-count assumptions with scene-scoped validation.",
                "T15gAction": "recorded_as_dependency_only; not implemented here",
            },
        },
        "additionalTaskIdCandidateAfterRegistryAudit": next_task_id_candidate,
        "ordering": ["T15g inventory/plan", "T16-T31 in registry order", "T32 freeze", "T33 first bounded batch", "T41+ only if T32 creates additional tasks"],
        "doNotStartAutomatically": True,
    }

    # Fail closed on the invariants this planning artifact reports.
    assert len(concepts) == 85
    assert collections.Counter(row["entityType"] for row in concepts) == {"individual_muscle": 48, "muscle_group": 16, "muscle_part": 21}
    assert len(scope["regions"]) == 18 and len(navigation["categories"]) == 12
    assert {row["id"] for row in scope["regions"]} == {row["sourceRegionId"] for row in crosswalk["sourceRegions"]}
    assert len(navigation["memberships"]) == 6 and set(row["categoryId"] for row in navigation["memberships"]) == {"leg"}
    assert len(bone_structures) == 10 and len(navigation["structureMeshMappings"]) == 9
    assert len(scene_bindings_by_id) == 9
    assert len(navigation["unmappedMeshContexts"]) == 4
    assert len(local_obj_files) == 20 and len(local_glb_files) == 2
    assert all(item["localAssetExists"] for row in muscle_entries for item in row["relatedSourceMeshCrosswalks"])
    assert all(item["localAssetExists"] for row in bone_entries for item in row["sourceAssets"])
    assert all(item["rawSourceAssetExists"] for item in unmapped_context_details)
    assert len(t13_source_asset_hash_checks) == 9 and all(item["passed"] for item in t13_source_asset_hash_checks)
    assert all(row["exists"] and row["expectedSha256"] == row["actualSha256"] for row in scene_asset_hash_checks)
    assert batches["gates"][1]["maxConcepts"] <= 10
    assert batches["sceneBatchRule"]["maxScenesPerTask"] == 1
    assert all(row["membershipRowsCreated"] == 0 for row in crosswalk["sourceRegions"])
    assert inventory["coveragePercent"] is None and inventory["wholeBodyIndividualMuscleCount"] is None
    return {"inventory": inventory, "crosswalk": crosswalk, "batches": batches}


def validate_existing(artifacts: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, rel in OUTPUTS.items():
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing generated artifact: {rel}")
            continue
        actual = json.loads(path.read_text(encoding="utf-8"))
        if actual != artifacts[key]:
            errors.append(f"generated artifact differs from current inputs: {rel}")
    inv = artifacts["inventory"]
    counts = inv["counts"]
    if counts["muscleConcepts"]["uniqueStableIds"] != 85:
        errors.append("partial muscle catalog count drifted")
    if counts["muscleConcepts"]["byEntityType"] != {"individual_muscle": 48, "muscle_group": 16, "muscle_part": 21}:
        errors.append("muscle entity type counts drifted")
    if inv["denominatorFrozen"] or inv["coveragePercent"] is not None:
        errors.append("whole-body denominator or percentage must stay unfrozen/null")
    if len(inv["currentMuscleConceptInventory"]) != 85 or len(inv["currentCanonicalBoneInventory"]) != 10:
        errors.append("stable-ID inventory length mismatch")
    if len(artifacts["crosswalk"]["sourceRegions"]) != 18:
        errors.append("source-region crosswalk must retain all 18 T01 regions")
    if any(row["membershipRowsCreated"] for row in artifacts["crosswalk"]["sourceRegions"]):
        errors.append("candidate crosswalk must not create runtime membership")
    for batch in artifacts["batches"]["gates"]:
        if batch.get("maxConcepts") is not None and batch["maxConcepts"] > 10:
            errors.append(f"batch exceeds 10 concepts: {batch['taskId']}")
    if artifacts["batches"]["sceneBatchRule"]["maxScenesPerTask"] > 1:
        errors.append("scene batch exceeds one scene")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the three planning artifacts")
    parser.add_argument("--check", action="store_true", help="compare existing artifacts to current inputs")
    args = parser.parse_args()
    artifacts = build()
    if args.write:
        for key, rel in OUTPUTS.items():
            dump(ROOT / rel, artifacts[key])
    errors = validate_existing(artifacts) if args.check else []
    if args.check and errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    if args.check:
        print("PASS: T15g inventory, 18-region candidate crosswalk, and bounded expansion plan match current input hashes and invariants")
    elif not args.write:
        print("T15g inputs parse; use --write to generate or --check to verify planning artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
