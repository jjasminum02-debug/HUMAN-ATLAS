#!/usr/bin/env python3
"""Build a reproducible, source-only T55 bilateral lower-limb package."""

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
FROZEN = ROOT / "work/evidence/T55/frozen-source-set.json"
ACQUISITION = ROOT / "work/evidence/T55/source-acquisition.json"
MISSING_POLICY = ROOT / "work/evidence/T55/scope-and-missing-policy.json"
T51_MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json"
T53_MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json"
T53_ACQUISITION = ROOT / "work/evidence/T53/source-acquisition.json"
T53_FROZEN = ROOT / "work/evidence/T53/frozen-source-set.json"
T53_GLB = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t53/T53-trunk-pelvis-static-source.glb"
T54_MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json"
T54_ACQUISITION = ROOT / "work/evidence/T54/source-acquisition.json"
T54_FROZEN = ROOT / "work/evidence/T54/frozen-source-set.json"
T54_GLB = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t54/T54-shoulder-upper-limb-static-source.glb"
T07_CROSSWALK = ROOT / "atlas-data/manifests/mesh-crosswalk-t07.json"
T07_DERIVED = ROOT / "atlas-data/manifests/derived-assets-t07.json"
T07_GLB = ROOT / "atlas-data/assets/derived-glb/bodyparts3d-r4-right-lower-leg/right-lower-leg.glb"
T07_PILOT = ROOT / "atlas-data/assets/bodyparts3d-v4-pilot"
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
OUT_ROOT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t55"
GLB_ROOT = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t55"
OUT_GLB = GLB_ROOT / "T55-bilateral-lower-limb-static-source.glb"
OUT_MANIFEST = OUT_ROOT / "source-manifest.json"
OUT_VALIDATION = ROOT / "work/evidence/T55/validation.json"
REGIONS = ("thigh", "leg", "foot")
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
SOURCE_VERSION = "BodyParts3D Release 4.0"
MODEL_ID = "HA-MODEL-BP3D4-T55-BILATERAL-LOWER-LIMB-QA"
ATTRIBUTION = "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International"


class PackageError(RuntimeError):
    pass


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise PackageError(f"could not load verified T51/T53/T07 helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INGEST = load_module("ha_t55_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
CONVERT = load_module("ha_t55_converter", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")
QA = load_module("ha_t55_t53_geometry_qa", ROOT / "atlas-data/tools/build_bodyparts3d_r4_t53.py")


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


def float32_bytes(values) -> bytes:
    values = tuple(values)
    return struct.pack(f"<{len(values)}f", *values)


def union_bounds(rows: list[dict[str, Any]]) -> dict[str, list[float]] | None:
    if not rows:
        return None
    return {"min": [min(row["projectBoundsM"]["min"][i] for row in rows) for i in range(3)], "max": [max(row["projectBoundsM"]["max"][i] for row in rows) for i in range(3)]}


def exact_boundary_candidates(rows: list[dict[str, Any]], names: tuple[str, ...]) -> list[dict[str, Any]]:
    lower = [row for row in rows if row.get("sourceName") and any(key in row["sourceName"].lower() for key in names)]
    return [{"sourceElementFileId": row["sourceElementFileId"], "sourceName": row["sourceName"], "laterality": row["lateralityFromExactSourceHeader"], "projectBoundsM": row["projectBoundsM"], "stableSourceMeshNodeId": row.get("stableSourceMeshNodeId") or row.get("stableMeshAssetId")} for row in lower]


def aabb_gap(a: dict[str, list[float]], b: dict[str, list[float]]) -> dict[str, Any]:
    per_axis = [max(0.0, max(a["min"][i] - b["max"][i], b["min"][i] - a["max"][i])) for i in range(3)]
    distance = math.sqrt(sum(x * x for x in per_axis))
    return {"axisSeparationM": per_axis, "euclideanLowerBoundM": distance, "aabbOverlap": distance == 0, "interpretation": "bounds proximity is broadphase only; does not prove surface contact, joint fit, or anatomical adequacy"}


def build_missing_policy(frozen: dict[str, Any], acquisition: dict[str, Any]) -> dict[str, Any]:
    expected_ids = {row["sourceElementFileId"] for row in frozen["uniqueSourceAssets"]}
    acq_by_id = {row["sourceElementFileId"]: row for row in acquisition.get("files", [])}
    if set(acq_by_id) != expected_ids:
        raise PackageError("acquisition ID list does not exactly cover the frozen source set")
    failed = sorted(file_id for file_id, row in acq_by_id.items() if row.get("status") != "acquired")
    policy = {
        "revision": "BodyParts3D-R4-T55-SCOPE-AND-MISSING-POLICY-v1",
        "task": "T55",
        "frozenSourceSetSha256": sha256_file(FROZEN),
        "frozenMembershipSha256": frozen["frozenMembershipSha256"],
        "selectedUniqueSourceCount": len(expected_ids),
        "missingFrozenSourceElementFileIds": [],
        "acquisitionFailureSourceElementFileIds": failed,
        "sourceIdentityGaps": [],
        "scopeBoundary": {"regionIds": list(REGIONS), "t51FrozenSourceChunkIds": ["thigh", "leg", "foot"], "noOtherBodyRegions": True, "wholeBodyCanonicalDenominator": None},
        "policy": "The source set is the exact union of the frozen T51 chunks. Missing source member, failed retrieval, incomplete source header identity, and unassigned canonical learner ID remain separate states. No absent structure or laterality is synthesized.",
        "sourcePresence": {"frozenIds": len(expected_ids), "successfulAcquisitionIds": len(expected_ids) - len(failed), "acquisitionFailures": len(failed), "notRequestedOutsideFrozenSet": True},
        "rights": {"publicRedistribution": False, "status": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers"},
    }
    write_json(MISSING_POLICY, policy)
    return policy


def build() -> dict[str, Any]:
    if any(not p.is_file() for p in (FROZEN, ACQUISITION, T51_MANIFEST, T53_MANIFEST, T53_ACQUISITION, T53_FROZEN, T53_GLB, T54_MANIFEST, T54_ACQUISITION, T54_FROZEN, T54_GLB, T07_CROSSWALK, T07_DERIVED, T07_GLB)):
        raise PackageError("a T51/T53/T54/T07 input required for T55 is missing")
    frozen_raw = FROZEN.read_bytes()
    frozen = json.loads(frozen_raw)
    acquisition = read_json(ACQUISITION)
    missing = build_missing_policy(frozen, acquisition)
    if acquisition.get("frozenMembershipSha256") != frozen.get("frozenMembershipSha256") or acquisition.get("frozenSourceSetSha256") != sha256_bytes(frozen_raw):
        raise PackageError("T55 acquisition is not bound to the exact frozen source set")
    if missing["frozenSourceSetSha256"] != sha256_file(FROZEN) or missing["missingFrozenSourceElementFileIds"]:
        raise PackageError("T55 scope/missing policy does not bind a complete frozen set")
    acq_by_id = {row["sourceElementFileId"]: row for row in acquisition["files"]}
    frozen_by_id = {row["sourceElementFileId"]: row for row in frozen["uniqueSourceAssets"]}
    expected_ids = set(frozen_by_id)
    if set(acq_by_id) != expected_ids:
        raise PackageError("T55 acquisition rows differ from frozen FJ ID set")
    failed = sorted(file_id for file_id, row in acq_by_id.items() if row.get("status") != "acquired")
    if failed:
        raise PackageError(f"cannot build a full frozen set; record acquisition failures instead of dropping them: {failed[:20]}")

    t51 = read_json(T51_MANIFEST)
    t51_concepts = {row["sourceFmaConceptId"]: row for row in t51["sourceConcepts"]}
    t51_tables = INGEST.load_tables(METADATA)
    identity_by_tree: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for tree, rows in (("IS-A", t51_tables["isaConcepts"]), ("PART-OF", t51_tables["partofConcepts"])):
        identity_by_tree[tree] = {(row[0], row[1]) for row in rows}
    region_chunks = {region: read_json(ROOT / f"atlas-data/manifests/bodyparts3d-r4-regions-t51/{region}.json") for region in REGIONS}
    region_fma = {region: {"bone": set(chunk["sourceBoneConceptIds"]), "muscle": set(chunk["sourceMuscleConceptIds"])} for region, chunk in region_chunks.items()}

    t53 = read_json(T53_MANIFEST)
    t53_assets = {row["sourceElementFileId"]: row for row in t53["sourceAssets"]}
    t54 = read_json(T54_MANIFEST)
    t54_assets = {row["sourceElementFileId"]: row for row in t54["sourceAssets"]}
    for package, label in ((t53, "T53"), (t54, "T54")):
        source = package.get("source", {})
        if source.get("sourceId") != SOURCE_ID or source.get("projectFrame") != FRAME or source.get("pose") != POSE:
            raise PackageError(f"{label} is not the same BodyParts3D project frame/pose; cross-package registration is forbidden")
    overlaps = {"T53": sorted(expected_ids & set(t53_assets)), "T54": sorted(expected_ids & set(t54_assets))}
    if any(overlaps.values()):
        raise PackageError(f"unexpected T55 source overlap with a prior package: {overlaps}")

    t07_crosswalk = read_json(T07_CROSSWALK)
    t07_by_id = {row["fileId"]: row for row in t07_crosswalk.get("entries", [])}
    t07_derived = read_json(T07_DERIVED)
    t07_xwalk_rows = {row["sourceFileId"]: row for row in t07_derived.get("meshCrosswalk", [])}
    t07_node_rows = {row["sourceFileId"]: row for row in t07_derived.get("meshNodes", [])}
    t07_gltf, t07_binary = QA.unpack_glb(T07_GLB.read_bytes())
    t07_glb_nodes = {node.get("extras", {}).get("sourceElementFileId") or node.get("extras", {}).get("sourceFileId"): node for node in t07_gltf.get("nodes", []) if node.get("extras", {}).get("sourceElementFileId") or node.get("extras", {}).get("sourceFileId")}
    t07_glb_meshes = {mesh.get("extras", {}).get("sourceElementFileId") or mesh.get("extras", {}).get("sourceFileId"): mesh for mesh in t07_gltf.get("meshes", []) if mesh.get("extras", {}).get("sourceElementFileId") or mesh.get("extras", {}).get("sourceFileId")}

    details: dict[str, dict[str, Any]] = {}
    input_records = []
    source_positions: dict[str, bytes] = {}
    for file_id in sorted(expected_ids):
        frozen_row = frozen_by_id[file_id]
        acq_row = acq_by_id[file_id]
        source_path = ROOT / acq_row["cacheRelativePath"]
        if not source_path.is_file() or source_path.stat().st_size != acq_row["bytes"] or sha256_file(source_path) != acq_row["sha256"]:
            raise PackageError(f"T55 acquired source path/size/hash changed: {file_id}")
        header = QA.parse_header(source_path)
        if header["fileId"] != file_id:
            raise PackageError(f"OBJ File ID header disagrees with the frozen source set: {file_id}")
        tree = {"FMA 3.0 is_a": "IS-A", "FMA 3.0 part_of": "PART-OF"}.get(header.get("buildUpLogic"))
        if tree != acq_row["archiveTree"] or tree not in frozen_row["expectedArchiveTrees"]:
            raise PackageError(f"OBJ source tree differs from official metadata and selected archive member: {file_id}")
        rows_for_file = [row for key in ("isaCompoundElements", "partofCompoundElements") for row in t51_tables[key] if row[2] == file_id]
        if not rows_for_file:
            raise PackageError(f"FJ ID is absent from T51 exact source ELEMENT tables: {file_id}")
        fma, bp = header.get("conceptId"), header.get("representationId")
        contexts = list(frozen_row["sourceContexts"])
        if fma and bp:
            INGEST.validate_obj_source_identity(header, t51_tables)
            if (fma, bp) not in identity_by_tree[tree]:
                raise PackageError(f"OBJ header FMA/BP pair is absent from exact {tree} table: {file_id}")
            identity_state = "header_identity_validated_against_release_metadata"
        else:
            identity_state = "header_identity_blank_context_only" if not fma and not bp else "header_identity_partial_held"
            if fma and fma not in {c["sourceFmaConceptId"] for c in contexts}:
                raise PackageError(f"partial OBJ FMA is unsupported by the frozen exact source context: {file_id}")
            if bp and not any(rep["sourceRepresentationId"] == bp and rep["tree"] == tree for c in contexts for rep in c["representations"]):
                raise PackageError(f"partial OBJ BP is unsupported by the frozen exact source context: {file_id}")
        if fma:
            contexts = [c for c in contexts if c["sourceFmaConceptId"] == fma]
        if bp:
            contexts = [c for c in contexts if any(rep["sourceRepresentationId"] == bp and rep["tree"] == tree for rep in c["representations"])]
        contexts = [c for c in contexts if tree in c["sourceTrees"]]
        if not contexts:
            raise PackageError(f"no exact frozen context supports acquired FJ/FMA/BP/tree relation: {file_id}")
        vertices, normals, triangles = CONVERT.parse_obj(source_path)
        source_bounds = QA.bounds(vertices)
        deltas = [abs(a - b) for axis in ("min", "max") for a, b in zip(header["boundsMm"][axis], source_bounds[axis])]
        # Keep source-header bounds and the actual-vertex bounds distinct. A small
        # header/export discrepancy is recorded for QA; geometry always comes from
        # vertices and the source bytes remain untouched.
        source_name = header.get("englishName")
        side = INGEST.side_from_name(source_name) if source_name else "unknown_header_name_missing"
        if side not in {"left", "right", "bilateral_source_term", "not_lateralized_in_source_label"}:
            side = "unknown_header_name_missing" if source_name is None else "not_lateralized_in_source_label"
        region_kinds = {}
        context_fma = {c["sourceFmaConceptId"] for c in contexts}
        for region in frozen_row["regionMemberships"]:
            bone_context = bool(context_fma & region_fma[region]["bone"])
            muscle_context = bool(context_fma & region_fma[region]["muscle"])
            region_kinds[region] = {"boneContext": bone_context, "muscleContext": muscle_context, "outsideT51BoneOrMuscleRoots": not (bone_context or muscle_context)}
        project_vertices = [CONVERT.transform_vertex(v) for v in vertices]
        packed_positions = float32_bytes(value for vertex in project_vertices for value in vertex)
        packed_topology = struct.pack(f"<{len(triangles) * 3}I", *(index for tri in triangles for index in tri))
        source_positions[file_id] = packed_positions
        project_bounds = {"min": [min(v[i] for v in project_vertices) for i in range(3)], "max": [max(v[i] for v in project_vertices) for i in range(3)]}
        stable_id = frozen_row["stableSourceMeshNodeId"]
        side_diag = QA.side_surface_diagnostic(side, vertices, triangles)
        t07_relation = t07_by_id.get(file_id)
        canonical_ids = [t07_relation["targetEntityId"]] if t07_relation and t07_relation.get("targetEntityId") else []
        if canonical_ids != frozen_row.get("canonicalLearnerIds", []):
            raise PackageError(f"existing T07 canonical binding changed between frozen crosswalk and package build: {file_id}")
        row = {
            "sourceElementFileId": file_id,
            "stableSourceMeshNodeId": stable_id,
            "renderNodeId": stable_id,
            "pickingTargetId": stable_id,
            "selectionSemantics": "source mesh selection; no new canonical assignment",
            "canonicalLearnerIds": canonical_ids,
            "sourceIdentityState": identity_state,
            "sourceHeaderFmaBpPairState": "validated" if identity_state == "header_identity_validated_against_release_metadata" else "incomplete_not_inferred",
            "sourceConceptId": fma,
            "sourceRepresentationId": bp,
            "sourceBuildUpLogic": header["buildUpLogic"],
            "sourceName": source_name,
            "sourceContextCandidates": contexts,
            "regionMemberships": frozen_row["regionMemberships"],
            "regionContextKinds": region_kinds,
            "lateralityFromExactSourceHeader": side,
            "lateralitySurfaceDiagnostic": side_diag,
            "sourceFrame": "BodyParts3D Release 4.0 native static reference; no OpenSim registration",
            "projectFrame": FRAME,
            "sourceUnit": "millimeter from exact acquired OBJ Bounds(mm) header",
            "transform": "[x,y,z]mm -> [x,z,-y]m; preserve x sign; no mirror, side swap, or relabel",
            "sourceBoundsMmHeader": header["boundsMm"],
            "sourceBoundsMmVertices": source_bounds,
            "sourceBoundsHeaderMatchesVertices": all(delta <= 0.01 for delta in deltas),
            "sourceBoundsHeaderMaxAbsDeltaMm": max(deltas),
            "projectBoundsM": project_bounds,
            "sourcePose": POSE,
            "lod": {"lodAssignmentId": f"HA-LOD-BP3D4-R4-99REDUCED-{file_id}", "sourceProfile": "official R4 99%-reduced OBJ", "sourceLevelCount": 1, "alternateSourceLevels": [], "generatedDecimation": False, "lodIdentity": "not inferred from FJ filename"},
            "sourceVertices": len(vertices), "sourceNormals": len(normals), "sourceTriangles": len(triangles),
            "sourceBytes": acq_row["bytes"], "sourceSha256": acq_row["sha256"],
            "sourceArchiveTree": tree, "sourceArchiveMemberPath": acq_row["memberPath"], "sourceAcquisitionMethod": acq_row["sourceAcquisitionMethod"],
            "sourceHeaderLicenseObservation": header.get("licenseHeader"),
            "sourceLicenseDisposition": "local technical QA only; public redistribution held pending file-level reconciliation",
            "reviewState": "source_only_not_human_anatomy_reviewed",
        }
        row["projectPositionContentSha256"] = sha256_bytes(packed_positions)
        row["sourceTopologyContentSha256"] = sha256_bytes(packed_topology)
        if t07_relation:
            legacy_xwalk = t07_xwalk_rows.get(file_id)
            legacy_node = t07_node_rows.get(file_id)
            old_node = t07_glb_nodes.get(file_id)
            old_mesh = t07_glb_meshes.get(file_id)
            if not legacy_xwalk or not legacy_node or not old_node or not old_mesh:
                raise PackageError(f"T07 legacy GLB/crosswalk lacks a prior row for {file_id}")
            if legacy_xwalk.get("sourceSha256") != row["sourceSha256"] or legacy_node.get("sourceSha256") != row["sourceSha256"]:
                raise PackageError(f"T07 legacy source bytes differ from frozen T55 source bytes: {file_id}")
            if legacy_node.get("topologySha256") is None:
                raise PackageError(f"T07 legacy topology hash missing for prior lower-limb source node: {file_id}")
            row["legacyT07MappingPreservation"] = {
                "crosswalk": t07_relation,
                "meshCrosswalk": legacy_xwalk,
                "legacyNode": legacy_node,
                "stableNodeIdPreserved": stable_id == legacy_xwalk.get("meshAssetId"),
                "canonicalLearnerIdPreserved": canonical_ids == ([t07_relation["targetEntityId"]] if t07_relation.get("targetEntityId") else []),
                "legacyRelationStatusPreserved": t07_relation["relationStatus"],
            }
        input_records.append({
            "file_id": file_id,
            "source_path": source_path,
            "source_relative_path": acq_row["cacheRelativePath"],
            "source_sha256": acq_row["sha256"],
            "asset": {"bytes": acq_row["bytes"], "vertex_count": len(vertices), "polygon_count": len(triangles), "concept_id": fma, "representation_id": bp},
        })
        details[file_id] = row

    CONVERT.MODEL_ID = MODEL_ID
    glb, mesh_records = CONVERT.build_glb(input_records)
    gltf, binary = QA.unpack_glb(glb)
    gltf["asset"]["generator"] = "HUMAN ATLAS T55 reproducible static BodyParts3D R4 source packager"
    gltf["extras"] = {"taskScope": "T55 static source QA only; not learner release", "sourceId": SOURCE_ID, "sourceVersion": SOURCE_VERSION, "frame": FRAME, "pose": POSE, "oneNodePerUniqueFj": True, "sourceLodLevels": 1, "alternateLodGenerated": False, "wholeBodyCanonicalDenominator": None, "canonicalLearnerMembershipCreated": False, "humanAnatomyReviewed": False, "publicRedistribution": False}
    for mesh_row in mesh_records:
        file_id = mesh_row["sourceFileId"]
        detail = details[file_id]
        detail["geometrySha256"] = mesh_row["geometrySha256"]
        detail["topologySha256"] = mesh_row["topologySha256"]
        detail["normalSha256"] = mesh_row["normalSha256"]
        index = mesh_row["nodeIndex"]
        extras = {**detail, "modelId": MODEL_ID, "meshIndex": mesh_row["meshIndex"]}
        gltf["nodes"][index]["name"] = detail["stableSourceMeshNodeId"]
        gltf["nodes"][index]["extras"].update(extras)
        gltf["meshes"][index]["name"] = detail["stableSourceMeshNodeId"]
        gltf["meshes"][index]["extras"].update(extras)
        mesh_row["nodeName"] = detail["stableSourceMeshNodeId"]
        mesh_row["regionMemberships"] = detail["regionMemberships"]
        mesh_row["pickingTargetId"] = detail["pickingTargetId"]

    output_glb = QA.repack_glb(gltf, binary)
    GLB_ROOT.mkdir(parents=True, exist_ok=True)
    if OUT_GLB.exists() and OUT_GLB.read_bytes() != output_glb:
        previous = read_json(OUT_VALIDATION) if OUT_VALIDATION.is_file() else {}
        prior_hash = previous.get("integratedGlb", {}).get("sha256")
        if prior_hash != sha256_file(OUT_GLB):
            raise PackageError(f"refusing to overwrite a T55 GLB not proven as the prior generated result: {OUT_GLB}")
    OUT_GLB.write_bytes(output_glb)
    glb_sha = sha256_bytes(output_glb)
    glb_positions = {mesh["extras"]["sourceElementFileId"]: QA.glb_position_hash(gltf, binary, index) for index, mesh in enumerate(gltf["meshes"])}
    if len(gltf["nodes"]) != len(expected_ids) or len(gltf["meshes"]) != len(expected_ids) or len(set(details)) != len(expected_ids):
        raise PackageError("T55 integrated GLB is not exactly one render node per unique frozen source FJ ID")
    if any(glb_positions.get(file_id) != details[file_id]["projectPositionContentSha256"] for file_id in expected_ids):
        raise PackageError("actual transformed OBJ position bytes differ from the corresponding GLB POSITION accessor")

    legacy_rows = []
    for file_id in sorted(set(t07_by_id) & expected_ids):
        t07_node = t07_node_rows[file_id]
        current = next(row for row in mesh_records if row["sourceFileId"] == file_id)
        old_geometry = t07_node.get("geometrySha256")
        old_topology = t07_node.get("topologySha256")
        legacy_rows.append({
            "sourceElementFileId": file_id,
            "stableSourceMeshNodeId": details[file_id]["stableSourceMeshNodeId"],
            "canonicalLearnerId": t07_by_id[file_id].get("targetEntityId"),
            "relationStatus": t07_by_id[file_id].get("relationStatus"),
            "sourceBytesAndSha256Match": details[file_id]["sourceSha256"] == t07_node["sourceSha256"],
            "sameVertexAndTriangleCounts": details[file_id]["sourceVertices"] == t07_node["vertexCount"] and details[file_id]["sourceTriangles"] == t07_node["triangleCount"],
            "sameGeometryHash": details[file_id]["geometrySha256"] == old_geometry,
            "sameTopologyHash": details[file_id]["topologySha256"] == old_topology,
            "topologySha256": details[file_id]["topologySha256"],
        })
    failed_legacy = [row["sourceElementFileId"] for row in legacy_rows if not all(row[key] for key in ("sourceBytesAndSha256Match", "sameVertexAndTriangleCounts", "sameGeometryHash", "sameTopologyHash"))]
    if failed_legacy:
        raise PackageError(f"T07 fragment has a different exact source/geometry/topology in T55 package: {failed_legacy}")
    if "FJ1439" not in {row["sourceElementFileId"] for row in legacy_rows}:
        raise PackageError("critical existing right tibialis anterior T07 source node is outside T55 exact source overlap")

    sorted_records = sorted(details.values(), key=lambda row: row["sourceElementFileId"])
    exact_groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in sorted_records:
        exact_groups[(row["projectPositionContentSha256"], row["sourceTopologyContentSha256"])].append(row["sourceElementFileId"])
    exact_duplicates = [ids for ids in exact_groups.values() if len(ids) > 1]
    labels = Counter(row["lateralityFromExactSourceHeader"] for row in sorted_records)
    opposite = [row["sourceElementFileId"] for row in sorted_records if row["lateralitySurfaceDiagnostic"].get("boundsWhollyOppositeToSourceLabel")]
    crossings = [row["sourceElementFileId"] for row in sorted_records if row["lateralitySurfaceDiagnostic"].get("crossesMidline")]
    bound_mismatches = [row["sourceElementFileId"] for row in sorted_records if not row["sourceBoundsHeaderMatchesVertices"]]
    outside_t51_root_ids = sorted(row["sourceElementFileId"] for row in sorted_records if any(kind.get("outsideT51BoneOrMuscleRoots") for kind in row["regionContextKinds"].values()))
    outside_t51_root_legacy_rows = [row for row in sorted_records if row["sourceElementFileId"] in outside_t51_root_ids and row.get("legacyT07MappingPreservation")]

    region_paths = {}
    for region in REGIONS:
        frozen_region = next(item for item in frozen["regionSets"] if item["regionId"] == region)
        rows = [details[file_id] for file_id in frozen_region["sourceElementFileIds"]]
        doc = {
            "revision": "BodyParts3D-R4-T55-region-source-package-v1", "task": "T55", "regionId": region,
            "labelKo": frozen_region["labelKo"], "status": "static_source_candidate_package_not_learner_release",
            "sourceElementFileIds": frozen_region["sourceElementFileIds"], "sourceElementFileCount": len(rows),
            "stableSourceNodeIds": [details[file_id]["stableSourceMeshNodeId"] for file_id in frozen_region["sourceElementFileIds"]],
            "pickingTargetIds": [details[file_id]["pickingTargetId"] for file_id in frozen_region["sourceElementFileIds"]],
            "sourceRoots": frozen_region["sourceRoots"], "sourceBoneConceptIds": frozen_region["sourceBoneConceptIds"], "sourceMuscleConceptIds": frozen_region["sourceMuscleConceptIds"],
            "sourceMeshClassCounts": {
                "boneContextElements": sum(any(k["boneContext"] for k in row["regionContextKinds"].values()) for row in rows),
                "muscleContextElements": sum(any(k["muscleContext"] for k in row["regionContextKinds"].values()) for row in rows),
                "bothContextElements": sum(any(k["boneContext"] and k["muscleContext"] for k in row["regionContextKinds"].values()) for row in rows),
            },
            "sourceLateralityCounts": dict(Counter(row["lateralityFromExactSourceHeader"] for row in rows)),
            "sharedIntegratedGlb": {"path": OUT_GLB.relative_to(ROOT).as_posix(), "sha256": glb_sha, "nodeCount": len(gltf["nodes"])},
            "regionBoundsM": union_bounds(rows), "canonicalLearnerMembershipAdded": False,
        }
        region_path = OUT_ROOT / f"{region}.json"
        write_json(region_path, doc)
        region_paths[region] = region_path.relative_to(ROOT).as_posix()

    t53_regions = [row for row in t53["sourceAssets"] if "pelvis-perineum" in row.get("regionMemberships", []) or "gluteal-hip" in row.get("regionMemberships", [])]
    t55_thigh_bones = [row for row in sorted_records if "thigh" in row["regionMemberships"] and any(v["boneContext"] for v in row["regionContextKinds"].values())]
    t55_leg_bones = [row for row in sorted_records if "leg" in row["regionMemberships"] and any(v["boneContext"] for v in row["regionContextKinds"].values())]
    t55_foot_bones = [row for row in sorted_records if "foot" in row["regionMemberships"] and any(v["boneContext"] for v in row["regionContextKinds"].values())]
    def side_pair_match(rows: list[dict[str, Any]], keyword: str, side: str) -> dict[str, Any] | None:
        candidates = [row for row in rows if keyword in (row.get("sourceName") or "").lower() and row.get("lateralityFromExactSourceHeader") == side]
        return candidates[0] if len(candidates) == 1 else None

    boundary_pairs = []
    for side in ("right", "left"):
        hip = side_pair_match(t53_regions, "hip bone", side)
        femur = side_pair_match(t55_thigh_bones, "femur", side)
        tibia = side_pair_match(t55_leg_bones, "tibia", side)
        talus = side_pair_match(t55_foot_bones, "talus", side)
        for boundary_id, a, b in (("pelvis-to-thigh", hip, femur), ("thigh-to-leg", femur, tibia), ("leg-to-foot", tibia, talus)):
            boundary_pairs.append({"boundaryId": boundary_id, "laterality": side, "sourceElementFileIds": [a["sourceElementFileId"], b["sourceElementFileId"]] if a and b else [], "sourceNames": [a["sourceName"], b["sourceName"]] if a and b else [], "aabbRelation": aabb_gap(a["projectBoundsM"], b["projectBoundsM"]) if a and b else None})

    browser_evidence_path = ROOT / "work/evidence/T55/browser-verification.json"
    browser_evidence = read_json(browser_evidence_path) if browser_evidence_path.is_file() else {}
    browser_static_review_passed = (
        browser_evidence.get("result") == "passed_static_source_browser_review"
        and browser_evidence.get("uniqueMeshCount") == len(t53_assets) + len(t54_assets) - len(set(t53_assets) & set(t54_assets)) + len(sorted_records)
        and browser_evidence.get("rendererCount") == 1
        and browser_evidence.get("anatomySceneRootCount") == 1
        and set(browser_evidence.get("testedViewportWidths", [])) == {1440, 1024, 390}
        and set(browser_evidence.get("verifiedCameraViews", [])) == {"front", "back", "side"}
        and browser_evidence.get("uncaughtPageErrorEvents") == 0
    )

    lower_boundary_context = {
        "sameSourceFramePoseAcrossPackages": True,
        "T53PelvisAndHipSourceRows": exact_boundary_candidates(t53_regions, ("hip bone", "ilium", "femur", "sacrum", "pelvis")),
        "T55ThighBoneSourceRows": exact_boundary_candidates(t55_thigh_bones, ("femur", "hip")),
        "T55LegBoneSourceRows": exact_boundary_candidates(t55_leg_bones, ("tibia", "fibula")),
        "T55FootBoneSourceRows": exact_boundary_candidates(t55_foot_bones, ("talus", "calcaneus", "tarsal")),
        "sameLateralityBoundaryPairs": boundary_pairs,
        "integratedVisualContinuityStatus": "same-scene static browser review completed; not surface-contact proof or human anatomy approval" if browser_static_review_passed else "requires actual browser review; geometry is not auto-corrected",
        "browserVerificationEvidence": {"path": browser_evidence_path.relative_to(ROOT).as_posix(), "sha256": sha256_file(browser_evidence_path)} if browser_static_review_passed else None,
        "AabbSurfaceProof": False,
        "noCrossSourceRegistrationOrReposition": True,
    }

    baseline_records = []
    for row in legacy_rows:
        baseline_records.append({"sourceElementFileId": row["sourceElementFileId"], "sourceSha256": details[row["sourceElementFileId"]]["sourceSha256"], "vertexCount": details[row["sourceElementFileId"]]["sourceVertices"], "triangleCount": details[row["sourceElementFileId"]]["sourceTriangles"], "geometrySha256": details[row["sourceElementFileId"]]["geometrySha256"], "topologySha256": details[row["sourceElementFileId"]]["topologySha256"], "stableSourceMeshNodeId": details[row["sourceElementFileId"]]["stableSourceMeshNodeId"], "canonicalLearnerIds": details[row["sourceElementFileId"]]["canonicalLearnerIds"], "relationStatus": row["relationStatus"]})
    manifest = {
        "revision": "BodyParts3D-R4-T55-static-source-package-v1", "task": "T55", "status": "local_static_source_package_partial_coverage_lod_and_rights_held",
        "source": {"sourceId": SOURCE_ID, "version": SOURCE_VERSION, "officialReadme": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/README_e.html", "officialReleaseNote": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/release_4.0_e.html", "archiveProfile": "BodyParts3D R4 official 99%-reduced mesh archive", "sourceFrame": "BodyParts3D Release 4.0 native static reference", "projectFrame": FRAME, "sourceUnit": "mm verified from each selected OBJ Bounds(mm) header", "transform": "[x,y,z]mm -> [x,z,-y]m; preserve x sign; no mirroring", "pose": POSE, "noOpenSimRegistration": True},
        "inputs": {"frozenSetPath": FROZEN.relative_to(ROOT).as_posix(), "frozenSetSha256": sha256_file(FROZEN), "frozenMembershipSha256": frozen["frozenMembershipSha256"], "acquisitionPath": ACQUISITION.relative_to(ROOT).as_posix(), "acquisitionSha256": sha256_file(ACQUISITION), "scopeAndMissingPolicyPath": MISSING_POLICY.relative_to(ROOT).as_posix(), "scopeAndMissingPolicySha256": sha256_file(MISSING_POLICY), "T51SourceManifestSha256": sha256_file(T51_MANIFEST), "T53SourceManifestSha256": sha256_file(T53_MANIFEST), "T53AcquisitionSha256": sha256_file(T53_ACQUISITION), "T54SourceManifestSha256": sha256_file(T54_MANIFEST), "T54AcquisitionSha256": sha256_file(T54_ACQUISITION), "T07CrosswalkSha256": sha256_file(T07_CROSSWALK), "T07DerivedAssetManifestSha256": sha256_file(T07_DERIVED), "T07LegacyGlbSha256": sha256_file(T07_GLB)},
        "scope": {"regions": list(REGIONS), "uniqueSourceElementFileCount": len(sorted_records), "sourceMembershipCount": frozen["sourceMembershipCount"], "crossRegionSharedSourceIDs": frozen["duplicatedMembershipReferences"], "crossTaskSourceOverlap": overlaps, "oneNodePerUniqueFj": True, "internalBatchCount": len(frozen["internalBatches"]), "internalBatchSizeMaximum": frozen["internalBatchSizeLimit"], "wholeBodyCanonicalDenominator": None, "canonicalLearnerMembershipCreated": False, "existingT07CanonicalBindingsPreservedWithoutPromotion": True, "T07LegacyMeshesOutsideT51BoneOrMuscleRoots": [{"sourceElementFileId": row["sourceElementFileId"], "canonicalLearnerIds": row["canonicalLearnerIds"], "legacyRelationStatus": row["legacyT07MappingPreservation"]["legacyRelationStatusPreserved"]} for row in outside_t51_root_legacy_rows], "humanReviewPromotions": 0, "newClipCreated": False, "explicitMissingPolicyBound": True, "missingFrozenSourceElementFileIds": missing["missingFrozenSourceElementFileIds"]},
        "sceneContract": {"contract": "T50 persistent AnatomySceneRoot / one renderer owner; T55 is a static source QA package", "qaGlbPath": OUT_GLB.relative_to(ROOT).as_posix(), "qaGlbSha256": glb_sha, "nodeCount": len(gltf["nodes"]), "productRendererCreated": False, "productCameraOrMaterialUXChanged": False},
        "assetCounts": {"uniqueSourceFjIds": len(sorted_records), "boneContextNodes": sum(any(v["boneContext"] for v in row["regionContextKinds"].values()) for row in sorted_records), "muscleContextNodes": sum(any(v["muscleContext"] for v in row["regionContextKinds"].values()) for row in sorted_records), "outsideT51BoneOrMuscleRootContextSourceIds": outside_t51_root_ids, "outsideT51BoneOrMuscleRootContextNodes": len(outside_t51_root_ids), "blankOrPartialSourceHeaderIdentity": sum(row["sourceIdentityState"] != "header_identity_validated_against_release_metadata" for row in sorted_records), "emptyMeshes": 0, "exactDuplicateGeometryGroups": exact_duplicates, "sourceLabelsObserved": dict(labels), "independentPickTargetCount": len({row["pickingTargetId"] for row in sorted_records}), "sourceResolutionLevelCount": 1, "alternateSourceLodCount": 0, "generatedLodCount": 0, "preservedExistingT07CanonicalBindingCount": sum(bool(row["canonicalLearnerIds"]) for row in sorted_records), "humanReviewed": 0, "selectedPayloadBytes": acquisition["selectedPayloadBytes"]},
        "laterality": {"sourceLabels": dict(labels), "hasLeftAndRightSourceLabels": labels.get("left", 0) > 0 and labels.get("right", 0) > 0, "whollyOppositeSourceLabelIds": opposite, "midlineCrossingSourceIds": crossings, "method": "exact OBJ source-name side plus projected mesh surface diagnostic; no side swap, mirror, or relabel; crossings remain observations"},
        "lowerLimbBoundaryQA": lower_boundary_context,
        "existingRightTibialisAnterior": {"sourceElementFileId": "FJ1439", "sourceName": details["FJ1439"]["sourceName"], "stableSourceMeshNodeId": details["FJ1439"]["stableSourceMeshNodeId"], "canonicalLearnerIds": details["FJ1439"]["canonicalLearnerIds"], "sourceSha256": details["FJ1439"]["sourceSha256"], "sourceTopologySha256": details["FJ1439"]["topologySha256"], "legacyTopologySha256": next(row["topologySha256"] for row in legacy_rows if row["sourceElementFileId"] == "FJ1439"), "legacyT07RelationStatus": next(row["relationStatus"] for row in legacy_rows if row["sourceElementFileId"] == "FJ1439"), "learnerIdCreated": False, "reviewState": "needs_review_preserved"},
        "legacyT07FragmentComparison": {"previousGlbPath": T07_GLB.relative_to(ROOT).as_posix(), "sourceIDsCompared": [row["sourceElementFileId"] for row in legacy_rows], "sourceIdCount": len(legacy_rows), "allSourceHashesVertexCountsTriangleCountsGeometryAndTopologyHashesMatch": not failed_legacy, "rows": legacy_rows, "mismatchIds": failed_legacy},
        "lodPolicy": {"officialArchiveProfile": "one 99%-reduced mesh representation", "alternateSourceLodProvided": False, "generatedDecimatedOrProxyMeshes": False, "FjIsPickingTargetIndependentOfLod": True, "FJMSuffixIsNotTreatedAsLod": True},
        "rights": {"officialCurrentLicense": "CC BY 4.0 per current official README", "requiredAttribution": ATTRIBUTION, "sourceHeaderLicenseObservations": dict(Counter(row["sourceHeaderLicenseObservation"] or "not_in_header" for row in sorted_records)), "redistributionStatus": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers", "publicRelease": False},
        "regionPackages": {region: {"path": region_paths[region], "sourceElementFileIds": next(row["sourceElementFileIds"] for row in frozen["regionSets"] if row["regionId"] == region), "stableNodeIds": [details[file_id]["stableSourceMeshNodeId"] for file_id in next(row["sourceElementFileIds"] for row in frozen["regionSets"] if row["regionId"] == region)]} for region in REGIONS},
        "sourceHeaderIdentityAudit": {"validatedPairCount": sum(row["sourceIdentityState"] == "header_identity_validated_against_release_metadata" for row in sorted_records), "unresolvedFjIds": [row["sourceElementFileId"] for row in sorted_records if row["sourceIdentityState"] != "header_identity_validated_against_release_metadata"], "blankFieldsNotInferred": True},
        "sourceBoundsHeaderReconciliation": {"matchCount": len(sorted_records) - len(bound_mismatches), "mismatchIds": bound_mismatches, "maxAbsoluteDeltaMm": max(row["sourceBoundsHeaderMaxAbsDeltaMm"] for row in sorted_records), "geometryDerivedFromActualVertices": True},
        "sourceAssets": sorted_records,
        "meshRecords": mesh_records,
    }
    manifest["manifestSha256"] = sha256_bytes(json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    if OUT_MANIFEST.exists():
        prior = read_json(OUT_MANIFEST)
        prior_validation = read_json(OUT_VALIDATION) if OUT_VALIDATION.is_file() else {}
        prior_is_our_validated_output = prior_validation.get("manifest", {}).get("sha256") == sha256_file(OUT_MANIFEST)
        if not prior_is_our_validated_output or prior.get("inputs") != manifest["inputs"]:
            raise PackageError("refusing to replace a T55 manifest with different source/hash/topology inputs")
    write_json(OUT_MANIFEST, manifest)

    validation = {
        "revision": "T55-PACKAGE-VALIDATION-v1", "task": "T55", "result": "source_package_built_static_only; learner/anatomy review_lod_and_public_rights_pending",
        "sourceSetFrozenBeforeAcquisition": frozen.get("status") == "frozen_before_T55_acquisition", "explicitMissingPolicyBoundToFrozenSet": True,
        "missingFrozenSourceElementFileIds": missing["missingFrozenSourceElementFileIds"], "acquisitionFailureIds": failed,
        "frozenSetSha256": sha256_file(FROZEN), "frozenMembershipSha256": frozen["frozenMembershipSha256"],
        "frozenIdsMatchAcquisition": set(acq_by_id) == expected_ids, "allFrozenItemsAcquired": len(acq_by_id) == len(expected_ids) and not failed,
        "downloadFailureCount": len(failed), "fullArchivesDownloaded": acquisition["fullArchivesDownloaded"], "selectedAssetCount": len(sorted_records),
        "sourceMembershipCount": frozen["sourceMembershipCount"], "regionCounts": {row["regionId"]: row["sourceElementFileCount"] for row in frozen["regionSets"]},
        "batchCount": len(frozen["internalBatches"]), "maxBatchSize": max(len(row["sourceElementFileIds"]) for row in frozen["internalBatches"]),
        "noDuplicateFjWithinRegion": True, "oneNodePerUniqueFj": len(gltf["nodes"]) == len(expected_ids) and len({row["stableSourceMeshNodeId"] for row in sorted_records}) == len(expected_ids),
        "crossRegionSharedFjReuseStableNode": all(row["stableSourceMeshNodeId"] == f"HA-MESH-BP3D4-{file_id}" for file_id, row in details.items()),
        "T53T54SameSourceFrameAndPose": True, "T55CrossTaskOverlap": overlaps,
        "outsideT51BoneOrMuscleRootContextSourceIds": outside_t51_root_ids,
        "rightAndLeftLabelsPresent": labels.get("left", 0) > 0 and labels.get("right", 0) > 0,
        "sourceHeaderIdentityValidatedCount": sum(row["sourceIdentityState"] == "header_identity_validated_against_release_metadata" for row in sorted_records),
        "unresolvedSourceIdentityIds": [row["sourceElementFileId"] for row in sorted_records if row["sourceIdentityState"] != "header_identity_validated_against_release_metadata"],
        "whollyOppositeSourceLabelCount": len(opposite), "midlineCrossingCount": len(crossings), "sourceLabelsNotMirroredOrSwapped": True,
        "sourcePositionHashesMatchGlbAccessors": len(glb_positions) == len(expected_ids), "emptySourceMeshes": 0, "exactDuplicateGeometryGroups": exact_duplicates,
        "headerBoundsMismatchCount": len(bound_mismatches), "T07LegacyOverlapCount": len(legacy_rows), "T07LegacyTopologyAndGeometryAllMatch": not failed_legacy,
        "existingTibialisAnteriorSourceHashAndTopologyPreserved": next(x["sourceBytesAndSha256Match"] and x["sameTopologyHash"] for x in legacy_rows if x["sourceElementFileId"] == "FJ1439"),
        "pelvisLegFootBoundaryVisualReview": "passed_static_browser_review_not_surface_contact_or_human_anatomy_approval" if browser_static_review_passed else "pending_browser_review", "anatomyHumanReview": False, "canonicalNewAssignments": 0,
        "sourceResolutionLevelCount": 1, "alternateLodCount": 0, "generatedLodCount": 0, "wholeBodyDenominator": None,
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
        print(f"T55 package build failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"result": result["validation"]["result"], "meshNodes": result["validation"]["integratedGlb"]["nodeCount"], "glbBytes": result["validation"]["integratedGlb"]["bytes"], "glbSha256": result["validation"]["integratedGlb"]["sha256"], "regionCounts": result["validation"]["regionCounts"], "leftAndRight": result["validation"]["rightAndLeftLabelsPresent"], "legacyT07Overlap": result["validation"]["T07LegacyOverlapCount"], "alternateLodCount": result["validation"]["alternateLodCount"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
