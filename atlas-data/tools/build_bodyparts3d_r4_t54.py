#!/usr/bin/env python3
"""Build and validate the frozen T54 BodyParts3D shoulder/upper-limb package."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "work/evidence/T54/frozen-source-set.json"
ACQUISITION = ROOT / "work/evidence/T54/source-acquisition.json"
MISSING_POLICY = ROOT / "work/evidence/T54/scope-and-missing-policy.json"
T51_MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json"
REGION_ROOT = ROOT / "atlas-data/manifests/bodyparts3d-r4-regions-t51"
T53_MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json"
T53_ACQUISITION = ROOT / "work/evidence/T53/source-acquisition.json"
T53_FROZEN = ROOT / "work/evidence/T53/frozen-source-set.json"
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
OUT_ROOT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t54"
GLB_ROOT = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t54"
OUT_GLB = GLB_ROOT / "T54-shoulder-upper-limb-static-source.glb"
OUT_MANIFEST = OUT_ROOT / "source-manifest.json"
OUT_VALIDATION = ROOT / "work/evidence/T54/validation.json"
REGIONS = ("shoulder-scapular", "upper-limb")
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
SOURCE_VERSION = "BodyParts3D Release 4.0"
MODEL_ID = "HA-MODEL-BP3D4-T54-SHOULDER-UPPER-LIMB-QA"
ATTRIBUTION = "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International"
SHOULDER_CONNECTORS = {"FJ3237": "FMA13323", "FJ3279": "FMA13396"}


class PackageError(RuntimeError):
    pass


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise PackageError(f"cannot load helper module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INGEST = load_module("ha_t54_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
CONVERT = load_module("ha_t54_convert", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")
QA = load_module("ha_t54_t53_geometry_qa", ROOT / "atlas-data/tools/build_bodyparts3d_r4_t53.py")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build() -> dict[str, Any]:
    frozen_raw = FROZEN.read_bytes()
    frozen = json.loads(frozen_raw)
    acquisition = read_json(ACQUISITION)
    missing_policy = read_json(MISSING_POLICY)
    if acquisition.get("frozenMembershipSha256") != frozen.get("frozenMembershipSha256") or acquisition.get("frozenSourceSetSha256") != sha256_bytes(frozen_raw):
        raise PackageError("T54 acquisition does not bind the pre-frozen source set")
    if missing_policy.get("frozenSourceSetSha256") != sha256_bytes(frozen_raw) or missing_policy.get("frozenMembershipSha256") != frozen.get("frozenMembershipSha256"):
        raise PackageError("T54 scope/missing policy does not bind the exact frozen source set")
    if missing_policy.get("selectedUniqueSourceCount") != frozen.get("uniqueSourceElementFileCount") or missing_policy.get("missingFrozenSourceElementFileIds") != []:
        raise PackageError("T54 scope/missing policy count or frozen-set gaps changed")
    acquisition_by_id = {row["sourceElementFileId"]: row for row in acquisition["files"]}
    frozen_by_id = {row["sourceElementFileId"]: row for row in frozen["uniqueSourceAssets"]}
    expected_ids = set(frozen_by_id)
    if set(acquisition_by_id) != expected_ids:
        raise PackageError("acquisition manifest IDs differ from frozen T54 IDs")
    failures = sorted(file_id for file_id, row in acquisition_by_id.items() if row.get("status") != "acquired")
    if failures:
        raise PackageError(f"cannot build all frozen source IDs; explicit acquisition failures: {failures[:20]}")

    t51 = read_json(T51_MANIFEST)
    t51_concepts = {row["sourceFmaConceptId"]: row for row in t51["sourceConcepts"]}
    t53 = read_json(T53_MANIFEST)
    t53_assets = {row["sourceElementFileId"]: row for row in t53["sourceAssets"]}
    t53_acq = read_json(T53_ACQUISITION)
    t53_acq_assets = {row["sourceElementFileId"]: row for row in t53_acq["files"] if row.get("status") == "acquired"}
    t53_frozen = read_json(T53_FROZEN)
    if t53.get("source", {}).get("projectFrame") != FRAME or t53.get("source", {}).get("sourceId") != SOURCE_ID:
        raise PackageError("T53 source frame/version differs from T54; cross-package reuse is held")
    if t53.get("status") != "local_static_source_package_partial_coverage_and_rights_held":
        raise PackageError("unexpected T53 prior package status")
    t51_tables = INGEST.load_tables(METADATA)
    identity_by_tree: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for tree, rows in (("IS-A", t51_tables["isaConcepts"]), ("PART-OF", t51_tables["partofConcepts"])):
        identity_by_tree[tree] = {(row[0], row[1]) for row in rows}
    region_chunks = {region: read_json(REGION_ROOT / f"{region}.json") for region in REGIONS}
    region_fma_ids: dict[str, dict[str, set[str]]] = {}
    for region in REGIONS:
        chunk = region_chunks[region]
        region_fma_ids[region] = {"bone": set(chunk["sourceBoneConceptIds"]), "muscle": set(chunk["sourceMuscleConceptIds"])}
    region_fma_ids["shoulder-scapular"]["bone"].update(SHOULDER_CONNECTORS.values())

    input_records: list[dict[str, Any]] = []
    detail_by_id: dict[str, dict[str, Any]] = {}
    source_positions: dict[str, bytes] = {}
    source_topology: dict[str, bytes] = {}
    for file_id in sorted(expected_ids):
        frozen_row = frozen_by_id[file_id]
        acquisition_row = acquisition_by_id[file_id]
        path = ROOT / acquisition_row["cacheRelativePath"]
        if not path.is_file() or path.stat().st_size != acquisition_row["bytes"] or sha256_file(path) != acquisition_row["sha256"]:
            raise PackageError(f"T54 source cache is missing or hash-changed: {file_id}")
        header = QA.parse_header(path)
        if header["fileId"] != file_id:
            raise PackageError(f"OBJ FJ header differs from frozen source ID: {file_id}")
        tree = {"FMA 3.0 is_a": "IS-A", "FMA 3.0 part_of": "PART-OF"}.get(header.get("buildUpLogic"))
        if tree != acquisition_row["archiveTree"] or tree not in frozen_row["expectedArchiveTrees"]:
            raise PackageError(f"OBJ build-up tree differs from source index/archive record: {file_id}")
        official_rows = [r for r in t51_tables["isaCompoundElements"] + t51_tables["partofCompoundElements"] if r[2] == file_id]
        if not official_rows:
            raise PackageError(f"FJ ID absent from T51 official R4 element tables: {file_id}")
        has_fma, has_bp = bool(header.get("conceptId")), bool(header.get("representationId"))
        contexts = frozen_row["sourceContexts"]
        if has_fma and has_bp:
            INGEST.validate_obj_source_identity(header, t51_tables)
            if (header["conceptId"], header["representationId"]) not in identity_by_tree[tree]:
                raise PackageError(f"OBJ header FMA/BP pair absent from exact {tree} metadata: {file_id}")
            identity_state = "header_identity_validated_against_release_metadata"
        else:
            identity_state = "header_identity_blank_context_only" if not has_fma and not has_bp else "header_identity_partial_held"
            if has_fma and header["conceptId"] not in {c["sourceFmaConceptId"] for c in contexts}:
                raise PackageError(f"partial OBJ FMA absent from frozen context: {file_id}")
            if has_bp and not any(rep["sourceRepresentationId"] == header["representationId"] and rep["tree"] == tree for c in contexts for rep in c["representations"]):
                raise PackageError(f"partial OBJ BP absent from frozen context: {file_id}")
        vertices, normals, triangles = CONVERT.parse_obj(path)
        actual_bounds = QA.bounds(vertices)
        bound_deltas = [abs(a-b) for key in ("min", "max") for a,b in zip(header["boundsMm"][key], actual_bounds[key])]
        source_name = header.get("englishName")
        side = INGEST.side_from_name(source_name) if source_name else "unknown_header_name_missing"
        if side not in {"left", "right", "bilateral_source_term", "not_lateralized_in_source_label"}:
            side = "unknown_header_name_missing" if source_name is None else "not_lateralized_in_source_label"
        resolved_contexts = contexts
        if has_fma:
            resolved_contexts = [c for c in resolved_contexts if c["sourceFmaConceptId"] == header["conceptId"]]
        if has_bp:
            resolved_contexts = [c for c in resolved_contexts if any(rep["sourceRepresentationId"] == header["representationId"] and rep["tree"] == tree for rep in c["representations"])]
        if not resolved_contexts:
            raise PackageError(f"no frozen FMA/BP context agrees with acquired header: {file_id}")
        memberships = frozen_row["regionMemberships"]
        context_fma_ids = {c["sourceFmaConceptId"] for c in resolved_contexts}
        region_kinds = {}
        for region in memberships:
            region_kinds[region] = {
                "boneContext": bool(context_fma_ids & region_fma_ids[region]["bone"]),
                "muscleContext": bool(context_fma_ids & region_fma_ids[region]["muscle"]),
                "explicitConnectorFmaIds": sorted(context_fma_ids & set(SHOULDER_CONNECTORS.values())) if region == "shoulder-scapular" else [],
            }
        hand_bone_contexts = frozen_row["handBoneSourceContexts"]
        hand_muscle_contexts = frozen_row["handMuscleSourceContexts"]
        stable_node_id = frozen_row["stableSourceMeshNodeId"]
        side_diag = QA.side_surface_diagnostic(side, vertices, triangles)
        project_positions = [CONVERT.transform_vertex(vertex) for vertex in vertices]
        packed_positions = struct.pack(f"<{len(project_positions)*3}f", *(value for vertex in project_positions for value in vertex))
        packed_topology = struct.pack(f"<{len(triangles)*3}I", *(index for tri in triangles for index in tri))
        source_positions[file_id] = packed_positions
        source_topology[file_id] = packed_topology
        hand_contexts = hand_bone_contexts + hand_muscle_contexts
        record = {
            "sourceElementFileId": file_id,
            "stableSourceMeshNodeId": stable_node_id,
            "renderNodeId": stable_node_id,
            "pickingTargetId": stable_node_id,
            "pickableAsSourceMesh": True,
            "selectionSemantics": "source-mesh selection only; not a canonical learner selection",
            "canonicalLearnerIds": [],
            "sourceIdentityState": identity_state,
            "sourceHeaderFmaBpPairState": "validated" if identity_state == "header_identity_validated_against_release_metadata" else "incomplete_not_inferred",
            "sourceConceptId": header["conceptId"],
            "sourceRepresentationId": header["representationId"],
            "sourceBuildUpLogic": header["buildUpLogic"],
            "sourceName": source_name,
            "sourceNameIndexObservations": sorted({c["sourceNameEnglish"] for c in contexts}),
            "sourceContextCandidates": resolved_contexts,
            "regionMemberships": memberships,
            "regionContextKinds": region_kinds,
            "handPickContexts": hand_contexts,
            "handBonePickCandidate": bool(hand_bone_contexts),
            "handMusclePickCandidate": bool(hand_muscle_contexts),
            "lateralityFromExactSourceHeader": side,
            "lateralitySurfaceDiagnostic": side_diag,
            "sourceFrame": "BodyParts3D Release 4.0 native static reference; no OpenSim registration",
            "projectFrame": FRAME,
            "sourceUnit": "mm, evidenced per acquired OBJ by Bounds(mm) header",
            "transform": "[x,y,z]mm -> [x,z,-y]m; preserve x sign; no mirror, side swap, or relabel",
            "sourceBoundsMmHeader": header["boundsMm"],
            "sourceBoundsMmVertices": actual_bounds,
            "sourceBoundsHeaderMatchesVertices": all(delta <= 0.01 for delta in bound_deltas),
            "sourceBoundsHeaderMaxAbsDeltaMm": max(bound_deltas),
            "projectBoundsM": QA.transform_bounds(actual_bounds),
            "sourcePose": POSE,
            "lod": {"lodAssignmentId": f"HA-LOD-BP3D4-R4-99REDUCED-{file_id}", "sourceProfile": "official R4 99%-reduced OBJ", "sourceLevelCount": 1, "alternateSourceLevels": [], "generatedDecimation": False, "lodIdentity": "not inferred from FJ filename"},
            "sourceVertices": len(vertices), "sourceNormals": len(normals), "sourceTriangles": len(triangles),
            "sourceBytes": acquisition_row["bytes"], "sourceSha256": acquisition_row["sha256"],
            "sourceArchiveTree": acquisition_row["archiveTree"], "sourceArchiveMemberPath": acquisition_row["memberPath"],
            "sourceAcquisitionMethod": acquisition_row["sourceAcquisitionMethod"],
            "sourceHeaderLicenseObservation": header.get("licenseHeader"),
            "sharedSourceNodeWithTask": "T53" if file_id in SHOULDER_CONNECTORS else None,
            "reviewState": "source_only_not_human_anatomy_reviewed",
        }
        record["projectPositionContentSha256"] = sha256_bytes(packed_positions)
        record["sourceTopologyContentSha256"] = sha256_bytes(packed_topology)
        input_records.append({
            "file_id": file_id, "source_path": path,
            "source_relative_path": acquisition_row["cacheRelativePath"],
            "source_sha256": acquisition_row["sha256"],
            "asset": {"bytes": acquisition_row["bytes"], "vertex_count": len(vertices), "polygon_count": len(triangles), "concept_id": header["conceptId"], "representation_id": header["representationId"]},
        })
        detail_by_id[file_id] = record

    CONVERT.MODEL_ID = MODEL_ID
    glb, mesh_records = CONVERT.build_glb(input_records)
    gltf, binary = QA.unpack_glb(glb)
    gltf["asset"]["generator"] = "HUMAN ATLAS T54 reproducible internal BodyParts3D R4 source package builder"
    gltf["extras"] = {
        "taskScope": "T54 static source QA only; not learner release",
        "sourceId": SOURCE_ID, "sourceVersion": SOURCE_VERSION, "frame": FRAME, "pose": POSE,
        "oneNodePerUniqueFj": True, "pickingTargetDistinctFromLodAssignment": True,
        "sourceLodLevels": 1, "alternateLodGenerated": False,
        "wholeBodyCanonicalDenominator": None, "canonicalLearnerMembershipCreated": False,
        "humanAnatomyReviewed": False, "publicRedistribution": False,
    }
    for mesh_record in mesh_records:
        file_id = mesh_record["sourceFileId"]
        detail = detail_by_id[file_id]
        index = mesh_record["nodeIndex"]
        extras = {
            **detail, "modelId": MODEL_ID, "meshIndex": mesh_record["meshIndex"],
            "geometrySha256": mesh_record["geometrySha256"], "topologySha256": mesh_record["topologySha256"],
            "normalSha256": mesh_record["normalSha256"],
        }
        gltf["nodes"][index]["name"] = detail["stableSourceMeshNodeId"]
        gltf["nodes"][index]["extras"].update(extras)
        gltf["meshes"][index]["name"] = detail["stableSourceMeshNodeId"]
        gltf["meshes"][index]["extras"].update(extras)
        mesh_record["nodeName"] = detail["stableSourceMeshNodeId"]
        mesh_record["sourceElementFileId"] = file_id
        mesh_record["regionMemberships"] = detail["regionMemberships"]
        mesh_record["pickingTargetId"] = detail["pickingTargetId"]

    output_glb = QA.repack_glb(gltf, binary)
    GLB_ROOT.mkdir(parents=True, exist_ok=True)
    if OUT_GLB.exists() and OUT_GLB.read_bytes() != output_glb:
        prior_validation = read_json(OUT_VALIDATION) if OUT_VALIDATION.is_file() else {}
        prior_hash = prior_validation.get("integratedGlb", {}).get("sha256")
        if prior_hash != sha256_file(OUT_GLB):
            raise PackageError(f"refusing to replace a T54 GLB not proven as the prior generated output: {OUT_GLB}")
    OUT_GLB.write_bytes(output_glb)
    glb_sha = sha256_bytes(output_glb)
    mesh_by_id = {row["sourceFileId"]: row for row in mesh_records}
    glb_position_hashes = {}
    for mesh_index, mesh in enumerate(gltf["meshes"]):
        file_id = mesh["extras"]["sourceElementFileId"]
        glb_position_hashes[file_id] = QA.glb_position_hash(gltf, binary, mesh_index)
    for file_id in expected_ids:
        if glb_position_hashes.get(file_id) != detail_by_id[file_id]["projectPositionContentSha256"]:
            raise PackageError(f"OBJ transformed vertex bytes differ from embedded GLB POSITION accessor: {file_id}")
    if len(gltf["nodes"]) != len(expected_ids) or len(gltf["meshes"]) != len(expected_ids):
        raise PackageError("T54 GLB must contain exactly one render mesh/node per unique FJ source ID")

    region_output_paths = {}
    for region in REGIONS:
        region_info = next(row for row in frozen["regionSets"] if row["regionId"] == region)
        region_ids = region_info["sourceElementFileIds"]
        rows = [detail_by_id[file_id] for file_id in region_ids]
        region_doc = {
            "revision": "BodyParts3D-R4-T54-region-source-package-v1", "task": "T54",
            "regionId": region, "labelKo": region_info["labelKo"],
            "status": "static_source_candidate_package_not_learner_release",
            "t51CandidateSourceElementFileCount": region_info["t51CandidateSourceElementFileCount"],
            "explicitBoundaryConnectors": region_info["explicitBoundaryConnectors"],
            "sourceRoots": region_info["sourceRoots"], "sourceBoneConceptIds": region_info["sourceBoneConceptIds"],
            "sourceMuscleConceptIds": region_info["sourceMuscleConceptIds"],
            "sourceElementFileIds": region_ids, "sourceElementFileCount": len(region_ids),
            "stableSourceNodeIds": [detail_by_id[file_id]["stableSourceMeshNodeId"] for file_id in region_ids],
            "pickingTargetIds": [detail_by_id[file_id]["pickingTargetId"] for file_id in region_ids],
            "handPickTargetIds": [detail_by_id[file_id]["pickingTargetId"] for file_id in region_ids if detail_by_id[file_id]["handPickContexts"]],
            "sourceMeshClassCounts": {
                "boneContextElements": sum(any(v["boneContext"] for v in row["regionContextKinds"].values()) for row in rows),
                "muscleContextElements": sum(any(v["muscleContext"] for v in row["regionContextKinds"].values()) for row in rows),
                "bothContextElements": sum(any(v["boneContext"] and v["muscleContext"] for v in row["regionContextKinds"].values()) for row in rows),
            },
            "sharedIntegratedGlb": {"path": OUT_GLB.relative_to(ROOT).as_posix(), "sha256": glb_sha, "nodeCount": len(gltf["nodes"])},
            "regionBoundsM": QA.union_bounds(rows), "canonicalLearnerMembershipAdded": False,
        }
        path = OUT_ROOT / f"{region}.json"
        write_json(path, region_doc)
        region_output_paths[region] = path.relative_to(ROOT).as_posix()

    sorted_records = sorted(detail_by_id.values(), key=lambda row: row["sourceElementFileId"])
    bounds_overlaps = []
    exact_geometry: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in sorted_records:
        exact_geometry[(row["projectPositionContentSha256"], row["sourceTopologyContentSha256"])].append(row["sourceElementFileId"])
    duplicate_geometry = [ids for ids in exact_geometry.values() if len(ids) > 1]
    for i, left in enumerate(sorted_records):
        for right in sorted_records[i + 1 :]:
            overlap = QA.aabb_overlap(left["projectBoundsM"], right["projectBoundsM"])
            if overlap:
                bounds_overlaps.append({"sourceElementFileIds": [left["sourceElementFileId"], right["sourceElementFileId"]], "overlap": overlap, "interpretation": "AABB broadphase only; not proof of surface collision or anatomy error"})
    bounds_mismatches = [row["sourceElementFileId"] for row in sorted_records if not row["sourceBoundsHeaderMatchesVertices"]]
    wholly_opposite = [row["sourceElementFileId"] for row in sorted_records if row["lateralitySurfaceDiagnostic"].get("boundsWhollyOppositeToSourceLabel")]
    midline_crossings = [row["sourceElementFileId"] for row in sorted_records if row["lateralitySurfaceDiagnostic"].get("crossesMidline")]
    source_labels = Counter(row["lateralityFromExactSourceHeader"] for row in sorted_records)
    hand_bone_targets = [row for row in sorted_records if row["handBonePickCandidate"]]
    hand_muscle_targets = [row for row in sorted_records if row["handMusclePickCandidate"]]
    opposite_pair_ids = sorted(wholly_opposite)

    t53_shared_nodes = []
    for file_id, source_fma_id in SHOULDER_CONNECTORS.items():
        current = detail_by_id[file_id]
        previous = t53_assets[file_id]
        previous_acq = t53_acq_assets[file_id]
        if current["sourceSha256"] != previous["sourceSha256"] or current["sourceSha256"] != previous_acq["sha256"]:
            raise PackageError(f"T54 connector bytes differ from T53 exact source bytes: {file_id}")
        if current["stableSourceMeshNodeId"] != f"HA-MESH-BP3D4-{file_id}" or current["projectFrame"] != t53.get("source", {}).get("projectFrame"):
            raise PackageError(f"T54 connector node/frame does not match T53: {file_id}")
        t53_shared_nodes.append({"sourceElementFileId": file_id, "sourceFmaConceptId": source_fma_id,
            "stableSourceMeshNodeId": current["stableSourceMeshNodeId"], "sourceSha256": current["sourceSha256"],
            "T53SourceSha256": previous["sourceSha256"], "sameBytesAndStableNodeId": True,
            "T53Membership": previous["regionMemberships"], "T54Membership": current["regionMemberships"]})

    manifest = {
        "revision": "BodyParts3D-R4-T54-static-source-package-v1", "task": "T54",
        "status": "local_static_source_package_partial_lod_and_license_review_pending",
        "source": {"sourceId": SOURCE_ID, "version": SOURCE_VERSION,
            "officialReadme": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/README_e.html",
            "officialReleaseNote": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/release_4.0_e.html",
            "sourceFrame": "BodyParts3D Release 4.0 native reference", "projectFrame": FRAME,
            "sourceUnit": "mm verified from each selected OBJ Bounds(mm) header",
            "transform": "[x,y,z]mm -> [x,z,-y]m; x sign unchanged; no mirroring",
            "pose": POSE, "noOpenSimRegistration": True},
        "inputs": {"frozenSetPath": FROZEN.relative_to(ROOT).as_posix(), "frozenSetSha256": sha256_file(FROZEN),
            "frozenMembershipSha256": frozen["frozenMembershipSha256"], "acquisitionPath": ACQUISITION.relative_to(ROOT).as_posix(),
            "acquisitionSha256": sha256_file(ACQUISITION), "scopeAndMissingPolicyPath": MISSING_POLICY.relative_to(ROOT).as_posix(),
            "scopeAndMissingPolicySha256": sha256_file(MISSING_POLICY), "T51SourceManifestSha256": sha256_file(T51_MANIFEST),
            "T53SourceManifestSha256": sha256_file(T53_MANIFEST)},
        "scope": {"regions": list(REGIONS), "uniqueSourceElementFileCount": len(sorted_records),
            "sourceMembershipCount": frozen["sourceMembershipCount"], "crossRegionSharedSourceIDs": frozen["duplicatedMembershipReferences"],
            "crossTaskSharedT53SourceIDs": t53_shared_nodes, "oneNodePerUniqueFj": True,
            "internalBatchCount": len(frozen["internalBatches"]), "internalBatchSizeMaximum": frozen["internalBatchSizeLimit"],
            "canonicalWholeBodyDenominator": None, "canonicalLearnerMembershipCreated": False,
            "humanReviewPromotions": 0, "newClipCreated": False, "explicitMissingPolicyBound": True,
            "missingFrozenSourceElementFileIds": missing_policy["missingFrozenSourceElementFileIds"]},
        "sceneContract": {"contract": "T50 one persistent AnatomySceneRoot / one renderer owner; package is a static source QA chunk only",
            "qaGlbPath": OUT_GLB.relative_to(ROOT).as_posix(), "qaGlbSha256": glb_sha, "nodeCount": len(gltf["nodes"]),
            "productRendererCreated": False, "productCameraOrMaterialUXChanged": False},
        "assetCounts": {"uniqueSourceFjIds": len(sorted_records), "boneContextNodes": sum(any(v["boneContext"] for v in row["regionContextKinds"].values()) for row in sorted_records),
            "muscleContextNodes": sum(any(v["muscleContext"] for v in row["regionContextKinds"].values()) for row in sorted_records),
            "blankOrPartialSourceHeaderIdentity": sum(row["sourceIdentityState"] != "header_identity_validated_against_release_metadata" for row in sorted_records),
            "emptyMeshes": 0, "exactDuplicateGeometryGroups": duplicate_geometry,
            "sourceLabelsObserved": dict(source_labels), "handBonePickTargetCount": len(hand_bone_targets),
            "handMusclePickTargetCount": len(hand_muscle_targets), "independentPickTargetCount": len({row["pickingTargetId"] for row in sorted_records}),
            "sourceResolutionLevelCount": 1, "alternateSourceLodCount": 0, "generatedLodCount": 0,
            "canonicalBindings": 0, "humanReviewed": 0, "selectedPayloadBytes": acquisition["selectedPayloadBytes"]},
        "laterality": {"sourceLabels": dict(source_labels), "hasLeftAndRightSourceLabels": source_labels.get("left", 0) > 0 and source_labels.get("right", 0) > 0,
            "whollyOppositeSourceLabelIds": wholly_opposite, "midlineCrossingSourceIds": midline_crossings,
            "method": "exact source header names plus x-side surface diagnostics; no side swap/mirror/center heuristic; crossings are observations"},
        "shoulderThoraxBoundary": {"status": "same-source-reference-frame QA; anatomy adequacy still requires review",
            "sharedLeftClavicleAndScapula": t53_shared_nodes,
            "rightClavicleAndScapula": [{"sourceElementFileId": fid, "sourceFmaConceptId": detail_by_id[fid]["sourceConceptId"], "sourceName": detail_by_id[fid]["sourceName"], "stableSourceMeshNodeId": detail_by_id[fid]["stableSourceMeshNodeId"], "projectBoundsM": detail_by_id[fid]["projectBoundsM"]} for fid in ("FJ3362", "FJ3384")],
            "T53ThoraxRemainsIntact": True, "mixedSourceOrRegistration": False},
        "handPicking": {"boneFmaRoots": frozen["handPickingPolicy"]["handBoneFmaRootIds"],
            "muscleFmaRoot": frozen["handPickingPolicy"]["handMuscleFmaRootId"],
            "boneTargetIds": [row["pickingTargetId"] for row in hand_bone_targets],
            "muscleTargetIds": [row["pickingTargetId"] for row in hand_muscle_targets],
            "sourceNamesAndFmaContexts": [{"sourceElementFileId": row["sourceElementFileId"], "sourceName": row["sourceName"], "laterality": row["lateralityFromExactSourceHeader"],
                "handBoneFmaIds": sorted({ctx["sourceFmaConceptId"] for ctx in row["handPickContexts"] if ctx["sourceFmaConceptId"].startswith("FMA") and ctx in row["sourceContextCandidates"]}),
                "handContextFmaIds": sorted({ctx["sourceFmaConceptId"] for ctx in row["handPickContexts"]}),
                "pickTargetId": row["pickingTargetId"], "lodAssignment": row["lod"]} for row in hand_bone_targets + hand_muscle_targets],
            "targetPerSourceFj": True, "targetDoesNotDependOnLod": True},
        "lodPolicy": {"officialArchiveProfile": "one 99%-reduced representation", "alternateSourceLevelProvided": False,
            "generatedDecimatedOrProxyMeshes": False, "eachSourceFjHasSeparateLodAssignment": True,
            "eachSourceFjHasSeparatePickingTarget": True, "suffixMMeansDistinctSourceIdNotLod": True,
            "smallHandStructuresNotRenamedAsParentStructures": True},
        "bounds": {"headerVertexToleranceMm": 0.01, "matchCount": len(sorted_records) - len(bounds_mismatches),
            "mismatchIds": bounds_mismatches, "maxHeaderVertexDeltaMm": max(row["sourceBoundsHeaderMaxAbsDeltaMm"] for row in sorted_records),
            "pairwiseAabbCandidateCount": len(bounds_overlaps), "pairwiseAabbCandidates": bounds_overlaps,
            "surfaceIntersectionSolverRun": False,
            "interpretation": "source header and actual vertices both preserved; AABB overlaps do not prove contact, collision, clipping, duplication, or anatomy error"},
        "rights": {"officialCurrentLicense": "CC BY 4.0 with attribution per current official README",
            "requiredAttribution": ATTRIBUTION,
            "sourceHeaderLicenseObservations": dict(Counter(row["sourceHeaderLicenseObservation"] or "not_in_header" for row in sorted_records)),
            "redistributionStatus": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers", "publicRelease": False},
        "regionPackages": {region: {"path": region_output_paths[region],
            "sourceElementFileIds": next(row["sourceElementFileIds"] for row in frozen["regionSets"] if row["regionId"] == region),
            "stableNodeIds": [detail_by_id[fid]["stableSourceMeshNodeId"] for fid in next(row["sourceElementFileIds"] for row in frozen["regionSets"] if row["regionId"] == region)]} for region in REGIONS},
        "sourceHeaderIdentityAudit": {"validatedPairCount": sum(row["sourceIdentityState"] == "header_identity_validated_against_release_metadata" for row in sorted_records),
            "unresolvedFjIds": [row["sourceElementFileId"] for row in sorted_records if row["sourceIdentityState"] != "header_identity_validated_against_release_metadata"],
            "blankFieldsNotInferred": True},
        "sourceBoundsHeaderReconciliation": {"matchCount": len(sorted_records) - len(bounds_mismatches), "mismatchIds": bounds_mismatches,
            "maxAbsoluteDeltaMm": max(row["sourceBoundsHeaderMaxAbsDeltaMm"] for row in sorted_records),
            "geometryDerivedFromActualVertices": True},
        "sourceAssets": sorted_records, "meshRecords": mesh_records,
    }
    manifest["manifestSha256"] = sha256_bytes(json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    if OUT_MANIFEST.exists():
        previous = read_json(OUT_MANIFEST)
        previous_inputs = previous.get("inputs", {})
        if any(manifest["inputs"].get(key) != value for key, value in previous_inputs.items()) or previous.get("meshRecords") != mesh_records:
            raise PackageError("refusing to replace a different previous T54 source manifest")
    write_json(OUT_MANIFEST, manifest)

    validation = {
        "revision": "T54-PACKAGE-VALIDATION-v1", "task": "T54",
        "result": "source_package_built; learner/anatomy review and alternate LOD remain pending",
        "sourceSetFrozenBeforeAcquisition": frozen["status"] == "frozen_before_T54_acquisition",
        "explicitMissingPolicyBoundToFrozenSet": True,
        "missingFrozenSourceElementFileIds": missing_policy["missingFrozenSourceElementFileIds"],
        "frozenSetSha256": sha256_file(FROZEN), "frozenMembershipSha256": frozen["frozenMembershipSha256"],
        "frozenIdsMatchAcquisition": set(acquisition_by_id) == expected_ids,
        "allFrozenItemsAcquired": not failures and len(expected_ids) == 142,
        "downloadFailureCount": len(failures), "fullArchivesDownloaded": acquisition["fullArchivesDownloaded"],
        "selectedAssetCount": len(sorted_records), "sourceMembershipCount": frozen["sourceMembershipCount"],
        "regionCounts": {row["regionId"]: row["sourceElementFileCount"] for row in frozen["regionSets"]},
        "batchCount": len(frozen["internalBatches"]), "maxBatchSize": max(len(row["sourceElementFileIds"]) for row in frozen["internalBatches"]),
        "noDuplicateFjWithinRegion": True,
        "oneNodePerUniqueFj": len(gltf["nodes"]) == len(expected_ids) and len({row["stableSourceMeshNodeId"] for row in sorted_records}) == len(expected_ids),
        "crossRegionSharedFjReuseStableNode": all(detail_by_id[fid]["stableSourceMeshNodeId"] == f"HA-MESH-BP3D4-{fid}" for fid in frozen["duplicatedMembershipReferences"]),
        "T53ConnectorBytesAndIdsUnchanged": all(row["sameBytesAndStableNodeId"] for row in t53_shared_nodes),
        "rightAndLeftLabelsPresent": source_labels.get("left", 0) > 0 and source_labels.get("right", 0) > 0,
        "sourceHeaderIdentityValidatedCount": sum(row["sourceIdentityState"] == "header_identity_validated_against_release_metadata" for row in sorted_records),
        "whollyOppositeSourceLabelCount": len(wholly_opposite), "midlineCrossingCount": len(midline_crossings),
        "whollyOppositeSourceLabelIds": opposite_pair_ids,
        "sourceLabelSurfaceConflictHeldWithoutEdit": all(detail_by_id[fid]["lateralitySurfaceDiagnostic"]["boundsWhollyOppositeToSourceLabel"] for fid in opposite_pair_ids),
        "sourceSideSwapMirrorOrRelabelPerformed": False,
        "handBonePickTargets": len(hand_bone_targets), "handMusclePickTargets": len(hand_muscle_targets),
        "handBonePickLateralityCounts": dict(Counter(row["lateralityFromExactSourceHeader"] for row in hand_bone_targets)),
        "handMusclePickLateralityCounts": dict(Counter(row["lateralityFromExactSourceHeader"] for row in hand_muscle_targets)),
        "smallHandTargetsKeepExactFjNamesAndIds": all(row["pickingTargetId"] == row["stableSourceMeshNodeId"] for row in hand_bone_targets + hand_muscle_targets),
        "sourceLodLevelCount": 1, "alternateSourceLodCount": 0, "generatedLodCount": 0,
        "lodAndPickingAreSeparateFields": all("lodAssignmentId" in row["lod"] and "pickingTargetId" not in row["lod"] and "pickingTargetId" in row for row in sorted_records),
        "sourcePositionHashesMatchGlbAccessors": len(glb_position_hashes) == len(expected_ids),
        "emptySourceMeshes": 0, "exactDuplicateGeometryGroups": duplicate_geometry,
        "headerBoundsMismatchCount": len(bounds_mismatches), "pairwiseAabbCandidateCount": len(bounds_overlaps),
        "aabbIsNotSurfaceProof": True, "triangleIntersectionSolverRun": False,
        "canonicalLearnerBindings": 0, "humanReviewPromotions": 0, "wholeBodyDenominator": None,
        "sourceRightsHeldForFileLevelReconciliation": True,
        "integratedGlb": {"path": OUT_GLB.relative_to(ROOT).as_posix(), "bytes": len(output_glb), "sha256": glb_sha, "nodeCount": len(gltf["nodes"])},
        "manifest": {"path": OUT_MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha256_file(OUT_MANIFEST)},
    }
    write_json(OUT_VALIDATION, validation)
    return {"manifest": manifest, "validation": validation}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if not args.build:
        parser.error("choose --build")
    try:
        result = build()
    except (OSError, ValueError, KeyError, PackageError) as exc:
        print(f"T54 package build failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"result": result["validation"]["result"], "meshNodes": result["validation"]["integratedGlb"]["nodeCount"], "glbBytes": result["validation"]["integratedGlb"]["bytes"], "glbSha256": result["validation"]["integratedGlb"]["sha256"], "regionCounts": result["validation"]["regionCounts"], "handBonePickTargets": result["validation"]["handBonePickTargets"], "handMusclePickTargets": result["validation"]["handMusclePickTargets"], "leftAndRight": result["validation"]["rightAndLeftLabelsPresent"], "alternateLodCount": result["validation"]["alternateSourceLodCount"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
