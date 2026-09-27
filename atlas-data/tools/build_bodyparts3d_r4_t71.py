#!/usr/bin/env python3
"""Build a deterministic, source-only T71 static trunk skeleton package."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import struct
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "work/evidence/T71/frozen-source-set.json"
ACQUISITION = ROOT / "work/evidence/T71/source-acquisition.json"
T70_SCOPE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t70/scope-inventory.json"
T70_INTEGRATION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json"
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
OUT_ROOT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t71"
OUT_GLB = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t71/T71-trunk-skeleton-static-source.glb"
OUT_MANIFEST = OUT_ROOT / "source-manifest.json"
OUT_INTEGRATION = OUT_ROOT / "integration-manifest.json"
OUT_VALIDATION = ROOT / "work/evidence/T71/validation.json"
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
SOURCE_VERSION = "BodyParts3D Release 4.0"
MODEL_ID = "HA-MODEL-BP3D4-T71-TRUNK-SKELETON-QA"
ATTRIBUTION = "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International"
TARGET_BY_ID = {
    "FJ3153": ("FMA7488", "thorax"),
    "FJ3157": ("FMA13072", "back"),
    "FJ3159": ("FMA13073", "back"),
    "FJ3162": ("FMA13074", "back"),
    "FJ3165": ("FMA13075", "back"),
    "FJ3168": ("FMA13076", "back"),
    "FJ3178": ("FMA7487", "thorax"),
    "FJ3290": ("FMA7486", "thorax"),
    "FJ3393": ("FMA16202", "pelvis-perineum"),
}


class PackageError(RuntimeError):
    pass


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise PackageError(f"could not load existing verified helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INGEST = load_module("ha_t71_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
CONVERT = load_module("ha_t71_converter", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")
T53_QA = load_module("ha_t71_glb_qa", ROOT / "atlas-data/tools/build_bodyparts3d_r4_t53.py")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def vector_bounds(vertices):
    return {"min": [min(v[i] for v in vertices) for i in range(3)], "max": [max(v[i] for v in vertices) for i in range(3)]}


def source_side(name: str | None) -> str:
    if not name:
        return "unknown_missing_source_name"
    lower = name.lower()
    has_left = "left" in lower
    has_right = "right" in lower
    if has_left and has_right:
        return "conflicting_side_tokens"
    if has_left:
        return "left"
    if has_right:
        return "right"
    return "not_lateralized_by_exact_source_name"


def source_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    frozen_raw = FROZEN.read_bytes()
    frozen = json.loads(frozen_raw)
    acquisition = json.loads(ACQUISITION.read_text(encoding="utf-8"))
    ids = list(frozen["sourceElementFileIds"])
    if set(ids) != set(TARGET_BY_ID) or len(ids) != len(TARGET_BY_ID):
        raise PackageError("T71 frozen IDs differ from the exact authorized nine-element set")
    if acquisition.get("frozenSourceSetSha256") != sha256_bytes(frozen_raw) or acquisition.get("frozenMembershipSha256") != frozen.get("frozenMembershipSha256"):
        raise PackageError("acquisition does not bind the exact immutable T71 freeze")
    acquired = {r["sourceElementFileId"]: r for r in acquisition.get("files", [])}
    if set(acquired) != set(ids) or len(acquired) != len(ids) or any(r.get("status") != "acquired" for r in acquired.values()):
        raise PackageError("acquisition does not contain exactly nine successful frozen IDs")
    tables = INGEST.load_tables(METADATA)
    inputs: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for file_id in ids:
        acq = acquired[file_id]
        obj_path = ROOT / acq["cacheRelativePath"]
        if not obj_path.is_file() or obj_path.stat().st_size != acq["bytes"] or sha256_file(obj_path) != acq["sha256"]:
            raise PackageError(f"official source OBJ bytes changed or are missing: {file_id}")
        header = T53_QA.parse_header(obj_path)
        if header.get("fileId") != file_id:
            raise PackageError(f"OBJ File ID header differs from the exact source member: {file_id}")
        if header.get("buildUpLogic") != "FMA 3.0 is_a" or acq.get("archiveTree") != "IS-A":
            raise PackageError(f"T71 selected archive tree and exact OBJ header disagree: {file_id}")
        expected_fma, region = TARGET_BY_ID[file_id]
        if header.get("conceptId") != expected_fma:
            raise PackageError(f"OBJ header FMA differs from T70 source relationship for {file_id}: {header.get('conceptId')} != {expected_fma}")
        INGEST.validate_obj_source_identity(header, tables)
        vertices, normals, triangles = CONVERT.parse_obj(obj_path)
        if len(vertices) < 4 or len(triangles) < 4:
            raise PackageError(f"source mesh is empty or degenerate: {file_id}")
        if not header.get("licenseHeader"):
            raise PackageError(f"source license header missing; local use/rights status held: {file_id}")
        # The official metadata FJ→FMA name relation and the acquired OBJ header must agree exactly.
        source_index_rows = [row for row in tables["isaCompoundElements"] if row[2] == file_id and row[0] == expected_fma]
        if len(source_index_rows) != 1 or source_index_rows[0][1].casefold() != (header.get("englishName") or "").casefold():
            raise PackageError(f"OBJ name/FMA identity is not exactly supported by the pinned official source metadata: {file_id}")
        expected_side = source_side(header.get("englishName"))
        if expected_side != "not_lateralized_by_exact_source_name":
            raise PackageError(f"T71 central axial bone source label has an unexpected/conflicting side token: {file_id}")
        stable_id = f"HA-MESH-BP3D4-{file_id}"
        transformed = [CONVERT.transform_vertex(v) for v in vertices]
        transformed_f32 = [tuple(CONVERT.float32_value(c) for c in v) for v in transformed]
        actual_bounds = vector_bounds(vertices)
        source_bounds_header = T53_QA.parse_header(obj_path)["boundsMm"]
        header_delta = max(abs(a-b) for a,b in zip(source_bounds_header["min"]+source_bounds_header["max"], actual_bounds["min"]+actual_bounds["max"]))
        source_name = header.get("englishName")
        identity_contexts = []
        for tree, key in (("IS-A", "isaCompoundElements"), ("PART-OF", "partofCompoundElements")):
            for concept_id, concept_name, element_id in tables[key]:
                if element_id == file_id:
                    identity_contexts.append({"tree": tree, "sourceFmaConceptId": concept_id, "sourceNameEnglish": concept_name})
        transformed_position_hash = sha256_bytes(struct.pack(f"<{len(transformed_f32)*3}f", *(c for v in transformed_f32 for c in v)))
        source_record = {
            "sourceElementFileId": file_id,
            "stableMeshAssetId": stable_id,
            "canonicalLearnerIds": [],
            "sourceId": SOURCE_ID,
            "sourceVersion": SOURCE_VERSION,
            "sourceIdentityState": "header_and_official_index_exactly_validated",
            "sourceFmaConceptId": header["conceptId"],
            "sourceRepresentationId": header["representationId"],
            "sourceBuildUpLogic": header["buildUpLogic"],
            "sourceNameEnglishExactHeader": source_name,
            "sourceContextRows": identity_contexts,
            "sourceArchiveTree": acq["archiveTree"],
            "sourceArchiveUrl": acq["archiveUrl"],
            "sourceMemberPath": acq["memberPath"],
            "sourceAcquisitionMethod": acq["sourceAcquisitionMethod"],
            "sourceArchiveEtag": acq["archiveEtag"],
            "sourceCrc32": acq["crc32"],
            "sourceBytes": acq["bytes"],
            "sourceSha256": acq["sha256"],
            "sourceHeaderLicenseObservation": header["licenseHeader"],
            "officialCurrentLicense": "CC BY 4.0; attribution required according to official README dated 2025-02-27",
            "requiredAttribution": ATTRIBUTION,
            "redistributionStatus": "held_pending_file_level_license_reconciliation_with_legacy_OBJ_headers",
            "humanAnatomyReviewed": False,
            "reviewState": "source_only_not_human_anatomy_reviewed",
            "productCandidateRegion": region,
            "productSelectionState": "T70_first_pass_candidate_only_not_canonical_membership_or_release_approval",
            "lateralityFromExactSourceName": expected_side,
            "lateralitySourceLabelObservation": "no left/right token in exact OBJ English name; no side inferred from coordinates",
            "sourceFrame": "BodyParts3D Release 4.0 native static reference",
            "projectFrame": FRAME,
            "sourceUnit": "mm, evidenced by exact OBJ Bounds(mm) header",
            "transform": "[x,y,z]mm -> [x,z,-y]m; preserve x sign; no mirror or recenter",
            "sourceBoundsMmHeader": source_bounds_header,
            "sourceBoundsMmActualVertices": actual_bounds,
            "sourceBoundsHeaderMaxAbsDeltaMm": header_delta,
            "sourceBoundsHeaderWithin001Mm": header_delta <= 0.01,
            "projectBoundsM": vector_bounds(transformed_f32),
            "sourcePose": POSE,
            "sourceLod": "official 99%-reduced OBJ bundle; no multilevel LOD chain advertised",
            "sourceVertexCount": len(vertices),
            "sourceNormalCount": len(normals),
            "sourceTriangleCount": len(triangles),
            "transformedPositionFloat32Sha256": transformed_position_hash,
        }
        rows.append(source_record)
        inputs.append({
            "file_id": file_id,
            "source_path": obj_path,
            "source_relative_path": acq["cacheRelativePath"],
            "source_sha256": acq["sha256"],
            "asset": {"bytes": acq["bytes"], "vertex_count": len(vertices), "polygon_count": len(triangles), "concept_id": header["conceptId"], "representation_id": header["representationId"]},
        })
    return rows, inputs


def build() -> dict[str, Any]:
    if any(not path.is_file() for path in (FROZEN, ACQUISITION, T70_SCOPE, T70_INTEGRATION)):
        raise PackageError("a required T70 or T71 input is missing")
    frozen_raw = FROZEN.read_bytes()
    frozen = json.loads(frozen_raw)
    scope_hash = sha256_file(T70_SCOPE)
    integration_hash = sha256_file(T70_INTEGRATION)
    if frozen["inputHashes"].get("scopeInventorySha256") != scope_hash or frozen["inputHashes"].get("integrationManifestSha256") != integration_hash:
        raise PackageError("T70 scope/integration inputs changed after T71 source freeze")
    base_integration = json.loads(T70_INTEGRATION.read_text(encoding="utf-8"))
    rows, inputs = source_records()

    CONVERT.MODEL_ID = MODEL_ID
    glb, mesh_records = CONVERT.build_glb(inputs)
    gltf, binary = T53_QA.unpack_glb(glb)
    gltf["asset"]["generator"] = "HUMAN ATLAS T71 deterministic BodyParts3D R4 source package builder"
    gltf["extras"] = {
        "taskScope": "T71 local static source QA only",
        "sourceId": SOURCE_ID,
        "sourceVersion": SOURCE_VERSION,
        "frame": FRAME,
        "unit": "m",
        "pose": POSE,
        "sourceElementFileIds": frozen["sourceElementFileIds"],
        "oneNodePerUniqueSourceElementFileId": True,
        "canonicalLearnerMembershipCreated": False,
        "humanAnatomyReviewed": False,
        "redistributionStatus": "held_pending_file_level_license_reconciliation_with_legacy_OBJ_headers",
    }
    detail_by_id = {row["sourceElementFileId"]: row for row in rows}
    for mesh_record in mesh_records:
        file_id = mesh_record["sourceFileId"]
        row = detail_by_id[file_id]
        mesh_index = mesh_record["meshIndex"]
        transformed_hash = T53_QA.glb_position_hash(gltf, binary, mesh_index)
        if transformed_hash != row["transformedPositionFloat32Sha256"]:
            raise PackageError(f"source→GLB transformed position payload mismatch: {file_id}")
        details = {**row, "modelId": MODEL_ID, "meshIndex": mesh_index, "geometrySha256": mesh_record["geometrySha256"], "topologySha256": mesh_record["topologySha256"], "normalSha256": mesh_record["normalSha256"]}
        gltf["nodes"][mesh_index]["name"] = row["stableMeshAssetId"]
        gltf["nodes"][mesh_index]["extras"].update(details)
        gltf["meshes"][mesh_index]["name"] = row["stableMeshAssetId"]
        gltf["meshes"][mesh_index]["extras"].update(details)
        mesh_record.update({"nodeName": row["stableMeshAssetId"], "sourceElementFileId": file_id, "sourceFmaConceptId": row["sourceFmaConceptId"], "sourceRepresentationId": row["sourceRepresentationId"], "productCandidateRegion": row["productCandidateRegion"]})
    output_glb = T53_QA.repack_glb(gltf, binary)
    if OUT_GLB.exists() and OUT_GLB.read_bytes() != output_glb:
        raise PackageError(f"refusing to overwrite non-identical prior T71 GLB: {OUT_GLB}")
    OUT_GLB.parent.mkdir(parents=True, exist_ok=True)
    OUT_GLB.write_bytes(output_glb)
    glb_sha = sha256_bytes(output_glb)

    geometry_groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row, mesh in zip(rows, mesh_records):
        geometry_groups[(mesh["geometrySha256"], mesh["topologySha256"])].append(row["sourceElementFileId"])
    exact_duplicates = [members for members in geometry_groups.values() if len(members) > 1]
    if exact_duplicates:
        raise PackageError(f"exact duplicate geometry/topology groups among T71 files: {exact_duplicates}")

    manifest = {
        "revision": "BodyParts3D-R4-T71-static-source-package-v1",
        "task": "T71",
        "status": "local_static_source_package_partial_product_coverage_and_rights_held",
        "batchId": "T71-B01-TRUNK-SKELETON",
        "source": {"sourceId": SOURCE_ID, "version": SOURCE_VERSION, "officialReadme": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/README_e.html", "officialReleaseNote": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/release_4.0_e.html", "archiveUrl": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip", "officialVersionMetadataLastModified": "Wed, 22 May 2013 06:46:24 GMT", "sourceFrame": "BodyParts3D Release 4.0 static reference", "projectFrame": FRAME, "sourceUnit": "mm from each exact OBJ Bounds(mm) header", "projectUnit": "m", "transform": "[x,y,z]mm -> [x,z,-y]m; preserve x sign; no mirror or recenter", "pose": POSE, "lod": "official 99%-reduced bundle; no multilevel LOD chain advertised"},
        "inputs": {"frozenSourceSet": FROZEN.relative_to(ROOT).as_posix(), "frozenSourceSetSha256": sha256_bytes(frozen_raw), "frozenMembershipSha256": frozen["frozenMembershipSha256"], "acquisitionManifest": ACQUISITION.relative_to(ROOT).as_posix(), "acquisitionManifestSha256": sha256_file(ACQUISITION), "t70ScopeInventorySha256": scope_hash, "t70IntegrationManifestSha256": integration_hash},
        "scope": {"sourceElementFileCount": len(rows), "sourceMembershipCount": len(rows), "uniqueSourceNodeCount": len(rows), "oneNodePerUniqueFj": True, "internalBatchSizeMaximum": 10, "internalBatchCount": len(frozen["internalBatches"]), "regionCandidateCounts": {rid: sum(row["productCandidateRegion"] == rid for row in rows) for rid in sorted({row["productCandidateRegion"] for row in rows})}, "wholeBodyCanonicalDenominator": None, "canonicalLearnerMembershipCreated": False},
        "sceneContract": {"contract": "T50 shared AnatomySceneRoot, frame and reference-pose contract; T71 is source-only static QA, not learner scene", "modelId": MODEL_ID, "integratedGlbLocalCachePath": OUT_GLB.relative_to(ROOT).as_posix(), "integratedGlbSha256": glb_sha, "meshNodeCount": len(gltf["nodes"]), "rendererCount": 0, "rendererPolicy": "QA browser loads this package with T53/T55 source packages inside one scene root and one canvas; no product runtime is created"},
        "rights": {"officialCurrentLicense": "CC BY 4.0; attribution required per official README updated 2025-02-27", "requiredAttribution": ATTRIBUTION, "sourceHeaderLicenseObservations": sorted({row["sourceHeaderLicenseObservation"] for row in rows}), "redistributionStatus": "held_pending_file_level_license_reconciliation_with_legacy_OBJ_headers", "publicRelease": False},
        "identityPolicy": "FMA concept IDs, BP representation IDs, FJ source element IDs, and canonical HA IDs remain distinct. No source element has a canonical learner binding. Source IDs/names in this file are exact acquisition/header/index observations only.",
        "lateralityPolicy": "All nine selected source names are non-lateralized axial structures. No side is inferred from x bounds or surface position; the transform preserves x sign and does not mirror.",
        "aabbPolicy": "AABB proximity is broadphase only; it is not surface contact, joint fit, or collision proof. Boundary observations require actual surface geometry/render review.",
        "humanAnatomyReviewed": False,
        "sourceAssets": rows,
        "meshRecords": mesh_records,
        "manifestSha256": None,
    }
    manifest["manifestSha256"] = sha256_bytes(json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    if OUT_MANIFEST.exists():
        old = json.loads(OUT_MANIFEST.read_text(encoding="utf-8"))
        if old.get("inputs") != manifest["inputs"] or old.get("meshRecords") != manifest["meshRecords"]:
            raise PackageError("refusing to overwrite a non-identical T71 source manifest")
    write_json(OUT_MANIFEST, manifest)

    # New immutable extension: T70 remains untouched; this child contract adds only T71's nine nodes.
    base_ids = {row["sourceElementFileId"] for row in base_integration["assets"]}
    if base_ids.intersection(detail_by_id):
        raise PackageError("T71 source IDs unexpectedly overlap a historical T52–T55 source asset")
    t71_assets = []
    for row in rows:
        t71_assets.append({
            "existingLearnerStableIds": [],
            "holdReasons": ["not_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"],
            "humanAnatomyReviewed": False,
            "learnerDefaultVisible": False,
            "learnerPickState": "source_only_unbound",
            "localQaRender": "available_source_surface",
            "packageReferences": [{"package": "T71", "sourceSha256": row["sourceSha256"]}],
            "primaryPackage": "T71",
            "productRegionIdsFromHistoricalPackages": [],
            "candidateProductRegionIds": [row["productCandidateRegion"]],
            "renderNodeId": row["stableMeshAssetId"],
            "sourceClassCandidates": ["bone_element_source_only"],
            "sourceConceptIdObservation": row["sourceFmaConceptId"],
            "sourceElementFileId": row["sourceElementFileId"],
            "sourceNameObservation": row["sourceNameEnglishExactHeader"],
            "sourceSha256": row["sourceSha256"],
        })
    extended = json.loads(json.dumps(base_integration))
    extended["revision"] = "BodyParts3D-R4-T71-extension-of-T70-minimal-integration-v1"
    extended["parentIntegrationManifest"] = {"path": T70_INTEGRATION.relative_to(ROOT).as_posix(), "sha256": integration_hash, "historicalManifestUnchanged": True}
    extended["assets"] = sorted(extended["assets"] + t71_assets, key=lambda item: item["sourceElementFileId"])
    extended["localQaChunks"] = extended["localQaChunks"] + [{"chunkId": "T71-B01-TRUNK-SKELETON", "package": "T71", "localQaGlbPath": OUT_GLB.relative_to(ROOT).as_posix(), "glbSha256": glb_sha, "sourceElementFileIds": sorted(detail_by_id), "suppressDuplicateSourceElementFileIds": []}]
    extended["counts"] = {
        **base_integration["counts"],
        "historicalPackageMembershipsT52toT55": base_integration["counts"]["historicalPackageMemberships"],
        "t71PackageMemberships": len(rows),
        "packageMembershipsIncludingT71": base_integration["counts"]["historicalPackageMemberships"] + len(rows),
        "historicalUniqueSourceNodesT52toT55": base_integration["counts"]["uniqueSourceNodes"],
        "uniqueSourceNodesIncludingT71": base_integration["counts"]["uniqueSourceNodes"] + len(rows),
        "sourceOnlyUnboundIncludingT71": base_integration["counts"]["sourceOnlyUnbound"] + len(rows),
        "newCanonicalBindings": 0,
        "newHumanReviewed": 0,
    }
    extended["t71InputHashes"] = {"scopeInventorySha256": scope_hash, "frozenSourceSetSha256": sha256_bytes(frozen_raw), "acquisitionManifestSha256": sha256_file(ACQUISITION), "t71SourceManifestSha256": sha256_file(OUT_MANIFEST), "t71GlbSha256": glb_sha}
    extended["publicRedistribution"] = "held_pending_file_level_license_reconciliation_with_legacy_OBJ_headers"
    write_json(OUT_INTEGRATION, extended)

    validation = {
        "revision": "T71-PACKAGE-VALIDATION-v1",
        "task": "T71",
        "frozenIdsMatchAcquiredAndBuilt": len(rows) == len(inputs) == len(gltf["nodes"]) == 9,
        "exactFrozenSourceIds": [row["sourceElementFileId"] for row in rows],
        "noExtraSourceIds": set(row["sourceElementFileId"] for row in rows) == set(frozen["sourceElementFileIds"]),
        "allHeadersMatchExactFjAndExpectedFma": all(row["sourceElementFileId"] in detail_by_id and detail_by_id[row["sourceElementFileId"]]["sourceFmaConceptId"] == TARGET_BY_ID[row["sourceElementFileId"]][0] for row in rows),
        "allHeaderBpFmaPairsInOfficialMetadata": True,
        "sourceHeaderAndOfficialIndexEnglishNameMatch": True,
        "archiveMemberCrcShaAndSizesValidated": True,
        "allNonemptyMeshes": all(row["sourceVertexCount"] > 0 and row["sourceTriangleCount"] > 0 for row in rows),
        "oneGlbNodePerUniqueFj": len(gltf["nodes"]) == len(set(frozen["sourceElementFileIds"])),
        "exactDuplicateGeometryTopologyGroups": exact_duplicates,
        "positionPayloadMatchesExactSourceTransform": True,
        "sourceUnitAndProjectTransformVerifiedPerFile": all(row["sourceUnit"].startswith("mm") and row["projectFrame"] == FRAME for row in rows),
        "sideState": "all_source_labels_non_lateralized; source x sign preserved; no anatomical left/right inferred",
        "sourceBoundsHeaderVertexDeltaMm": {row["sourceElementFileId"]: row["sourceBoundsHeaderMaxAbsDeltaMm"] for row in rows},
        "sourceBoundsHeaderTolerance010mmPassIds": [row["sourceElementFileId"] for row in rows if row["sourceBoundsHeaderWithin001Mm"]],
        "redistributionStatus": "held_pending_file_level_license_reconciliation_with_legacy_OBJ_headers",
        "canonicalLearnerBindings": 0,
        "humanAnatomyReviewed": False,
        "publicRelease": False,
        "historicalT70InputPreservedAsParent": True,
        "derivedGlb": {"path": OUT_GLB.relative_to(ROOT).as_posix(), "bytes": len(output_glb), "sha256": glb_sha, "meshNodeCount": len(gltf["nodes"])},
        "sourceManifest": {"path": OUT_MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha256_file(OUT_MANIFEST)},
        "extendedIntegrationManifest": {"path": OUT_INTEGRATION.relative_to(ROOT).as_posix(), "sha256": sha256_file(OUT_INTEGRATION), "uniqueSourceNodesIncludingT71": extended["counts"]["uniqueSourceNodesIncludingT71"]},
    }
    write_json(OUT_VALIDATION, validation)
    return {"manifest": manifest, "validation": validation}


def main() -> int:
    try:
        result = build()
    except Exception as exc:
        print(f"T71 package error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result["validation"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
