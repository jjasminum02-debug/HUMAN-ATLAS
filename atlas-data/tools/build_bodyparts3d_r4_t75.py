#!/usr/bin/env python3
"""Validate and convert the frozen T75 deltoid source subset into an R4 sibling package."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "work/evidence/T75/frozen-source-set.json"
ACQ_DEFAULT = ROOT / "work/evidence/T75/source-acquisition.json"
MATRIX = ROOT / "work/evidence/T73/target-source-matrix.json"
T70_BASE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json"
T53_SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json"
T54_SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json"
T74_SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t74/source-manifest.json"
T74_EXTENSION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t74/integration-extension.json"
META = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
OUT_ROOT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t75"
GLB = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t75/T75-deltoid-bilateral-static-source.glb"
OUT_SOURCE = OUT_ROOT / "source-manifest.json"
OUT_INTEGRATION = OUT_ROOT / "integration-extension.json"
OUT_VALIDATION = ROOT / "work/evidence/T75/validation.json"
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
SOURCE_VERSION = "BodyParts3D Release 4.0"
MODEL = "HA-MODEL-BP3D4-T75-BILATERAL-DELTOID-SOURCE"
ATTRIBUTION = "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International"
EXPECTED = ["FJ1468", "FJ1468M", "FJ1467", "FJ1467M", "FJ1513", "FJ1513M"]
REGIONS = ["shoulder-scapular", "upper-limb"]
GENERIC_CONTEXT = {"clavicular": "FMA34677", "acromial": "FMA34678", "spinal": "FMA34679"}


class BuildError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_immutable_json(path: Path, value: Any) -> None:
    raw = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") != raw:
        raise BuildError(f"refusing to overwrite a non-identical T75 artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(raw, encoding="utf-8")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise BuildError(f"cannot import existing R4 utility: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def exact_side(text: str | None) -> str | None:
    if not text:
        return None
    values = {item.casefold() for item in re.findall(r"\b(left|right)\b", text, re.I)}
    if len(values) > 1:
        raise BuildError(f"conflicting side tokens in exact source label: {text}")
    return next(iter(values), None)


def bounds(vertices: list[tuple[float, float, float]]) -> dict[str, list[float]]:
    return {"min": [min(row[i] for row in vertices) for i in range(3)], "max": [max(row[i] for row in vertices) for i in range(3)]}


def acquisition_record() -> tuple[Path, dict[str, Any]]:
    candidates = [ACQ_DEFAULT, *sorted(ACQ_DEFAULT.parent.glob("source-acquisition-attempt-*.json"))]
    for path in reversed(candidates):
        if path.is_file():
            data = read_json(path)
            if data.get("result") == "pass":
                return path, data
    raise BuildError("T75 has no successful exact-member source acquisition; do not synthesize or substitute assets")


def validate_and_build() -> dict[str, Any]:
    freeze_raw = FREEZE.read_bytes()
    frozen = read_json(FREEZE)
    if frozen.get("revision") != "BodyParts3D-R4-T75-FROZEN-DELTOID-EXACT-SOURCE-SET-v1" or frozen.get("status") != "frozen_before_mesh_acquisition":
        raise BuildError("T75 freeze revision/status mismatch")
    if frozen.get("sourceElementFileIds") != EXPECTED or [row.get("sourceElementFileId") for row in frozen.get("uniqueNewSourceAssets", [])] != EXPECTED:
        raise BuildError("T75 exact FJ source set changed")
    if frozen.get("archiveTree") != "IS-A" or len(frozen.get("internalBatches", [])) != 1 or frozen["internalBatches"][0].get("count") != 6:
        raise BuildError("T75 IS-A tree or one-batch six-ID boundary changed")
    for rel, digest in frozen.get("inputSha256", {}).items():
        path = ROOT / rel
        if not path.is_file() or sha_file(path) != digest:
            raise BuildError(f"T73/frozen historical input changed after T75 freeze: {rel}")

    acq_path, acquisition = acquisition_record()
    acq_check = load_module("ha_t75_acquire", ROOT / "atlas-data/tools/acquire_bodyparts3d_r4_t75.py")
    acq_check.check()
    if acquisition.get("frozenSourceSetSha256") != sha(freeze_raw) or acquisition.get("frozenMembershipSha256") != frozen.get("membershipSha256"):
        raise BuildError("T75 acquisition evidence is not bound to exact freeze")
    if acquisition.get("fullArchiveDownloaded") is not False or acquisition.get("selectedMemberRangeRequestsOnly") is not True:
        raise BuildError("T75 acquisition violates selected-member range-only policy")
    if acquisition.get("attemptedIds") != EXPECTED or acquisition.get("selectedMemberCount") != 6 or acquisition.get("failedCount") != 0:
        raise BuildError("T75 acquisition does not pass the exact six frozen IDs")
    acquired_by_id = {row["sourceElementFileId"]: row for row in acquisition.get("files", [])}
    frozen_by_id = {row["sourceElementFileId"]: row for row in frozen["uniqueNewSourceAssets"]}
    if set(acquired_by_id) != set(EXPECTED) or any(row.get("status") != "acquired" for row in acquired_by_id.values()):
        raise BuildError("T75 acquisition rows differ from frozen source IDs")

    ingest = load_module("ha_t75_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
    converter = load_module("ha_t75_converter", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")
    qa = load_module("ha_t75_glb_qa", ROOT / "atlas-data/tools/build_bodyparts3d_r4_t53.py")
    tables = ingest.load_tables(META)
    concepts = {tuple(row) for row in tables["isaConcepts"]}
    relations = {tuple(row) for row in tables["isaCompoundElements"]}
    mesh_inputs: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    duplicate_raw: dict[str, list[str]] = {}
    duplicate_geometry: dict[str, list[str]] = {}

    for fid in EXPECTED:
        target = frozen_by_id[fid]
        acquired = acquired_by_id[fid]
        obj_path = ROOT / acquired["cacheRelativePath"]
        obj_raw = obj_path.read_bytes()
        if len(obj_raw) != acquired["bytes"] or sha(obj_raw) != acquired["sha256"]:
            raise BuildError(f"T75 raw OBJ size/hash differs from successful acquisition: {fid}")
        if acquired.get("memberPath") != f"isa_BP3D_4.0_obj_99/{fid}.obj":
            raise BuildError(f"T75 ZIP member path differs from exact IS-A archive: {fid}")
        header = qa.parse_header(obj_path)
        ingest.validate_obj_source_identity(header, tables)
        expected_identity = (fid, target["sourceConceptId"], target["sourceRepresentationId"], "FMA 3.0 is_a")
        actual_identity = (header.get("fileId"), header.get("conceptId"), header.get("representationId"), header.get("buildUpLogic"))
        if actual_identity != expected_identity:
            raise BuildError(f"T75 exact OBJ FJ/FMA/BP/IS-A header mismatch for {fid}: {actual_identity}")
        if tuple(target["officialConceptRow"]) not in concepts or tuple(target["officialElementRow"]) not in relations:
            raise BuildError(f"T75 exact official IS-A concept/ELEMENT relation row missing for {fid}")
        for row in target["genericAndZoneContextRows"]:
            if tuple(row) not in relations:
                raise BuildError(f"T75 generic/zone context relation differs for {fid}: {row}")
        name = header.get("englishName")
        if not name or name.casefold() != target["sourceNameEnglish"].casefold() or exact_side(name) != target["side"]:
            raise BuildError(f"T75 explicit OBJ source name/laterality differs from frozen FMA relation for {fid}")
        if not header.get("licenseHeader") or not header.get("boundsMm"):
            raise BuildError(f"T75 source license or Bounds(mm) header missing for {fid}")

        vertices, normals, triangles = converter.parse_obj(obj_path)
        if len(vertices) < 4 or len(normals) != len(vertices) or len(triangles) < 4:
            raise BuildError(f"T75 OBJ has no non-empty triangle surface or matching vertex normals: {fid}")
        source_bounds = bounds(vertices)
        header_bounds = header["boundsMm"]
        delta = [a - b for a, b in zip(header_bounds["min"] + header_bounds["max"], source_bounds["min"] + source_bounds["max"])]
        project_vertices = [tuple(converter.float32_value(value) for value in converter.transform_vertex(point)) for point in vertices]
        position_bytes = converter.float32_bytes(value for point in project_vertices for value in point)
        position_hash = sha(position_bytes)
        index_bytes = b"".join(int(i).to_bytes(4, "little") for face in triangles for i in face)
        geom_sig = sha(position_bytes + b"\0" + index_bytes)
        duplicate_raw.setdefault(sha(obj_raw), []).append(fid)
        duplicate_geometry.setdefault(geom_sig, []).append(fid)
        region_memberships = [{"regionId": region, "sourceElementFileId": fid, "stableRenderNodeId": f"HA-MESH-BP3D4-{fid}"} for region in target["declaredProductRegions"]]
        source_row = {
            "sourceElementFileId": fid,
            "stableMeshAssetId": f"HA-MESH-BP3D4-{fid}",
            "sourceId": SOURCE_ID,
            "sourceVersion": SOURCE_VERSION,
            "sourceArchiveTree": "IS-A",
            "sourceArchiveUrl": acquisition["archiveUrl"],
            "sourceArchiveEtag": acquisition["archiveMetadata"]["etag"],
            "sourceArchiveLastModified": acquisition["archiveMetadata"].get("lastModified"),
            "sourceMemberPath": acquired["memberPath"],
            "sourceCrc32": acquired["crc32"],
            "sourceBytes": acquired["bytes"],
            "sourceSha256": acquired["sha256"],
            "sourceZipCompressionMethod": acquired["zipCompressionMethod"],
            "sourceFmaConceptId": header["conceptId"],
            "sourceRepresentationId": header["representationId"],
            "sourceBuildUpLogic": header["buildUpLogic"],
            "sourceNameEnglishExactHeader": name,
            "sourceDeltoidPart": target["part"],
            "sourcePartContextConceptId": GENERIC_CONTEXT[target["part"]],
            "sourceZoneContextConceptId": "FMA34676",
            "sourceOfficialElementRow": target["officialElementRow"],
            "sourceOfficialConceptRow": target["officialConceptRow"],
            "sourceGenericAndZoneContextRows": target["genericAndZoneContextRows"],
            "explicitSourceSide": target["side"],
            "lateralityNotInferredFromFjSuffixOrCoordinates": True,
            "sourceHeaderLicenseObservation": header["licenseHeader"],
            "officialCurrentLicense": "CC BY 4.0 per current official BodyParts3D license page; legacy per-OBJ header claim remains separately recorded",
            "requiredAttribution": ATTRIBUTION,
            "redistributionStatus": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers",
            "humanAnatomyReviewed": False,
            "reviewState": "source_only_not_human_anatomy_reviewed",
            "canonicalLearnerIds": [],
            "learnerDefaultVisible": False,
            "learnerPickState": "source_only_unbound",
            "regionMemberships": region_memberships,
            "singleStableNodeAcrossRegionMemberships": True,
            "sourceFrame": "BodyParts3D Release 4.0 static reference",
            "sourceUnit": "mm from exact OBJ Bounds(mm) header",
            "projectFrame": FRAME,
            "projectUnit": "m",
            "transform": "[x,y,z]mm -> [x,z,-y]m; preserve x sign; no mirror or recenter",
            "sourceBoundsMmHeader": header_bounds,
            "sourceBoundsMmActualVertices": source_bounds,
            "sourceBoundsHeaderMinusVertexExtremaMm": delta,
            "sourceBoundsHeaderMaxAbsDeltaMm": max(abs(value) for value in delta),
            "sourceBoundsHeaderWithin001mm": max(abs(value) for value in delta) <= 0.01,
            "sourceVertexCount": len(vertices),
            "sourceNormalCount": len(normals),
            "sourceTriangleCount": len(triangles),
            "projectBoundsM": bounds(project_vertices),
            "transformedPositionFloat32Sha256": position_hash,
            "sourcePose": POSE,
            "sourceLod": "official 99%-reduced IS-A OBJ; one released source mesh level observed",
            "scope": "T75 six side-specific deltoid-part source surfaces only; does not assert complete whole deltoid or anatomy review",
        }
        source_rows.append(source_row)
        mesh_inputs.append({
            "file_id": fid,
            "source_path": obj_path,
            "source_relative_path": acquired["cacheRelativePath"],
            "source_sha256": acquired["sha256"],
            "asset": {"bytes": acquired["bytes"], "vertex_count": len(vertices), "polygon_count": len(triangles), "concept_id": header["conceptId"], "representation_id": header["representationId"]},
        })

    duplicate_raw_groups = [sorted(ids) for ids in duplicate_raw.values() if len(ids) > 1]
    duplicate_geometry_groups = [sorted(ids) for ids in duplicate_geometry.values() if len(ids) > 1]
    if duplicate_raw_groups or duplicate_geometry_groups:
        raise BuildError(f"T75 selected files contain duplicate raw/converted geometry groups: {duplicate_raw_groups} / {duplicate_geometry_groups}")

    converter.MODEL_ID = MODEL
    glb_bytes, mesh_records = converter.build_glb(mesh_inputs)
    gltf, binary = qa.unpack_glb(glb_bytes)
    gltf["asset"]["generator"] = "HUMAN ATLAS T75 deterministic BodyParts3D R4 IS-A source subset builder"
    gltf["extras"] = {
        "taskScope": "T75 exact source-only six side-specific deltoid-part surfaces",
        "sourceId": SOURCE_ID,
        "sourceVersion": SOURCE_VERSION,
        "frame": FRAME,
        "unit": "m",
        "pose": POSE,
        "sourceElementFileIds": EXPECTED,
        "oneNodePerUniqueSourceElementFileId": True,
        "regionMembershipsReferenceSameStableNode": True,
        "contextOnlyConceptIds": ["FMA34676", "FMA34677", "FMA34678", "FMA34679"],
        "canonicalLearnerMembershipCreated": False,
        "humanAnatomyReviewed": False,
        "redistributionStatus": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers",
        "noMirroring": True,
        "noRecentering": True,
    }
    by_id = {row["sourceElementFileId"]: row for row in source_rows}
    for mesh in mesh_records:
        fid, mesh_index = mesh["sourceFileId"], mesh["meshIndex"]
        row = by_id[fid]
        if qa.glb_position_hash(gltf, binary, mesh_index) != row["transformedPositionFloat32Sha256"]:
            raise BuildError(f"T75 GLB positions differ from the T50 shared mm→m transform: {fid}")
        details = {**row, "meshIndex": mesh_index, "geometrySha256": mesh["geometrySha256"], "topologySha256": mesh["topologySha256"], "normalSha256": mesh["normalSha256"]}
        gltf["nodes"][mesh_index]["name"] = row["stableMeshAssetId"]
        gltf["nodes"][mesh_index]["extras"].update(details)
        gltf["meshes"][mesh_index]["name"] = row["stableMeshAssetId"]
        gltf["meshes"][mesh_index]["extras"].update(details)
        mesh.update({"nodeName": row["stableMeshAssetId"], "sourceElementFileId": fid, "sourceFmaConceptId": row["sourceFmaConceptId"], "sourceRepresentationId": row["sourceRepresentationId"], "explicitSourceSide": row["explicitSourceSide"]})
    output = qa.repack_glb(gltf, binary)
    glb_digest = sha(output)
    if GLB.exists() and sha_file(GLB) != glb_digest:
        raise BuildError(f"refusing to replace a different existing T75 derived GLB: {GLB}")
    GLB.parent.mkdir(parents=True, exist_ok=True)
    if not GLB.exists():
        GLB.write_bytes(output)

    base = read_json(T70_BASE)
    base_sha = sha_file(T70_BASE)
    base_ids = {row.get("sourceElementFileId") for row in base.get("assets", [])}
    if base_ids & set(EXPECTED):
        raise BuildError(f"T75 target FJ already exists in the historical T70 integration: {sorted(base_ids & set(EXPECTED))}")
    for path in [T53_SOURCE, T54_SOURCE, T74_SOURCE, T74_EXTENSION]:
        data = read_json(path)
        for key in ("sourceAssets", "meshAssets", "meshRecords", "assets"):
            found = {row.get("sourceElementFileId") for row in data.get(key, []) if isinstance(row, dict)} & set(EXPECTED)
            if found:
                raise BuildError(f"T75 target FJ collision in historical package {path}: {sorted(found)}")

    freeze_sha = sha(freeze_raw)
    source_manifest = {
        "revision": "BodyParts3D-R4-T75-static-source-package-v1",
        "task": "T75",
        "status": "local_static_deltoid_part_surfaces_complete_rights_human_review_and_learner_binding_held",
        "source": {
            "sourceId": SOURCE_ID,
            "version": SOURCE_VERSION,
            "officialDownloadPage": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html",
            "officialMeshMetadataPage": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/data-7.html",
            "officialMeshMetadataDoi": "10.18908/lsdba.nbdc00837-007",
            "officialIsaRelationMetadataPage": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/data-5.html",
            "officialIsaRelationMetadataDoi": "10.18908/lsdba.nbdc00837-005",
            "officialReleaseNote": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/release_4.0_e.html",
            "officialLicensePage": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html",
            "archiveTree": "IS-A",
            "archiveUrl": acquisition["archiveUrl"],
            "archiveEtag": acquisition["archiveMetadata"]["etag"],
            "archiveLastModified": acquisition["archiveMetadata"].get("lastModified"),
            "archiveContentLength": acquisition["archiveMetadata"]["contentLength"],
            "sourceFrame": "BodyParts3D Release 4.0 static reference",
            "projectFrame": FRAME,
            "sourceUnit": "mm per selected OBJ Bounds(mm) headers",
            "projectUnit": "m",
            "transform": "[x,y,z]mm -> [x,z,-y]m; x sign preserved; no mirroring or recentering",
            "pose": POSE,
            "lod": "official 99%-reduced IS-A OBJ; one source level, no multilevel LOD chain claimed",
        },
        "inputs": {
            "frozenSourceSetSha256": freeze_sha,
            "frozenMembershipSha256": frozen["membershipSha256"],
            "acquisitionEvidencePath": acq_path.relative_to(ROOT).as_posix(),
            "acquisitionManifestSha256": sha_file(acq_path),
            "t73TargetSourceMatrixSha256": sha_file(MATRIX),
            "t70ParentIntegrationManifestSha256": base_sha,
            "t53SourceManifestSha256": sha_file(T53_SOURCE),
            "t54SourceManifestSha256": sha_file(T54_SOURCE),
            "t74SourceManifestSha256": sha_file(T74_SOURCE),
            "t74IntegrationExtensionSha256": sha_file(T74_EXTENSION),
            "frozenInputSha256": frozen["inputSha256"],
        },
        "scope": {
            "targetSet": "T73 frozen bilateral deltoid clavicular/acromial/spinal parts",
            "sourceConceptCount": 6,
            "sourceElementFileCount": 6,
            "uniqueNewSourceNodeCount": 6,
            "productRegionIds": REGIONS,
            "regionMembershipRowCount": 12,
            "oneNodePerUniqueFj": True,
            "genericPartAndZoneConceptsAreContextOnly": ["FMA34676", "FMA34677", "FMA34678", "FMA34679"],
            "wholeDeltoidSurfaceComplete": False,
            "latissimusDorsiSourceAvailability": "unavailable_in_bodyparts3d_r4_metadata; no substitute geometry",
            "canonicalLearnerMembershipCreated": False,
            "wholeBodyCanonicalDenominator": None,
        },
        "sceneContract": {
            "contract": "T50 one persistent AnatomySceneRoot/frame/rest-pose; T75 source-only sibling package, not a learner scene",
            "modelId": MODEL,
            "integratedGlbLocalCachePath": GLB.relative_to(ROOT).as_posix(),
            "integratedGlbSha256": glb_digest,
            "meshNodeCount": len(gltf["nodes"]),
            "rendererCount": 0,
            "previewContract": "QA may compose exact T53/T54 same-frame context plus T75 in one AnatomySceneRoot and one renderer; no product visibility or UX policy changes",
        },
        "rights": {
            "officialCurrentLicense": "CC BY 4.0 on current official BodyParts3D license page",
            "sourceHeaderLicenseObservations": sorted({row["sourceHeaderLicenseObservation"] for row in source_rows}),
            "requiredAttribution": ATTRIBUTION,
            "redistributionStatus": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers",
            "publicRelease": False,
        },
        "identityPolicy": "Exact R4 side-specific concept/FMA, BP representation, FJ source file and stable scene node stay separate; zone/generic part concepts share the referenced source surface and do not mint extra nodes or whole-deltoid equivalence.",
        "lateralityPolicy": "Use exact IS-A relation plus explicit OBJ English label; FJ suffix and coordinate sign are not side evidence.",
        "humanAnatomyReviewed": False,
        "canonicalLearnerIds": [],
        "sourceAssets": source_rows,
        "meshRecords": mesh_records,
        "manifestSha256": None,
    }
    source_manifest["manifestSha256"] = sha(json.dumps(source_manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    write_immutable_json(OUT_SOURCE, source_manifest)

    new_assets = []
    for row in source_rows:
        new_assets.append({
            "existingLearnerStableIds": [],
            "holdReasons": ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"],
            "humanAnatomyReviewed": False,
            "learnerDefaultVisible": False,
            "learnerPickState": "source_only_unbound",
            "localQaRender": "available_source_surface",
            "packageReferences": [{"package": "T75", "sourceSha256": row["sourceSha256"]}],
            "primaryPackage": "T75",
            "productRegionIdsFromHistoricalPackages": [],
            "candidateProductRegionIds": row["regionMemberships"] and [membership["regionId"] for membership in row["regionMemberships"]],
            "regionMembershipRows": row["regionMemberships"],
            "renderNodeId": row["stableMeshAssetId"],
            "sourceClassCandidates": ["muscle_element_source_only"],
            "sourceConceptIdObservation": row["sourceFmaConceptId"],
            "sourceElementFileId": row["sourceElementFileId"],
            "sourceNameObservation": row["sourceNameEnglishExactHeader"],
            "sourceSha256": row["sourceSha256"],
            "singleStableNodeAcrossRegionMemberships": True,
        })
    extension = json.loads(json.dumps(base))
    extension["revision"] = "BodyParts3D-R4-T75-sibling-extension-of-T70-minimal-integration-v1"
    extension["parentIntegrationManifest"] = {"path": T70_BASE.relative_to(ROOT).as_posix(), "sha256": base_sha, "historicalManifestUnchanged": True}
    extension["siblingPackageReferences"] = [
        {
            "task": "T53", "sourceManifestPath": T53_SOURCE.relative_to(ROOT).as_posix(), "sourceManifestSha256": sha_file(T53_SOURCE),
            "integratedGlbPath": read_json(T53_SOURCE)["sceneContract"]["integratedGlbLocalCachePath"],
            "integratedGlbSha256": read_json(T53_SOURCE)["sceneContract"]["integratedGlbSha256"],
            "relationship": "same-source trunk/back context; historical membership and node bytes unchanged",
        },
        {
            "task": "T54", "sourceManifestPath": T54_SOURCE.relative_to(ROOT).as_posix(), "sourceManifestSha256": sha_file(T54_SOURCE),
            "integratedGlbPath": read_json(T54_SOURCE)["sceneContract"]["qaGlbPath"],
            "integratedGlbSha256": read_json(T54_SOURCE)["sceneContract"]["qaGlbSha256"],
            "relationship": "same-source shoulder/upper-limb context; existing two-region node reuse is preserved",
        },
        {"task": "T74", "sourceManifestPath": T74_SOURCE.relative_to(ROOT).as_posix(), "sourceManifestSha256": sha_file(T74_SOURCE), "integrationManifestPath": T74_EXTENSION.relative_to(ROOT).as_posix(), "integrationManifestSha256": sha_file(T74_EXTENSION), "relationship": "sibling source extension unchanged; T75 does not repackage it"},
    ]
    existing_ids = {row.get("sourceElementFileId") for row in extension.get("assets", [])}
    if existing_ids & set(EXPECTED):
        raise BuildError(f"T75 would duplicate a source node in integration extension: {sorted(existing_ids & set(EXPECTED))}")
    extension["assets"] = sorted(extension["assets"] + new_assets, key=lambda row: row["sourceElementFileId"])
    extension["localQaChunks"] = extension["localQaChunks"] + [{
        "chunkId": "T75-B01-BILATERAL-DELTOID-PARTS",
        "package": "T75",
        "localQaGlbPath": GLB.relative_to(ROOT).as_posix(),
        "glbSha256": glb_digest,
        "sourceElementFileIds": EXPECTED,
        "productRegionMembershipRows": 12,
        "suppressDuplicateSourceElementFileIds": [],
    }]
    base_counts = base.get("counts", {})
    extension["counts"] = {
        **base_counts,
        "historicalPackageMembershipsBeforeT75": base_counts.get("historicalPackageMemberships"),
        "t75UniqueSourceNodes": len(source_rows),
        "t75RegionMembershipRows": sum(len(row["regionMemberships"]) for row in source_rows),
        "packageMembershipsIncludingT75": base_counts.get("historicalPackageMemberships", 0) + sum(len(row["regionMemberships"]) for row in source_rows),
        "historicalUniqueSourceNodesBeforeT75": base_counts.get("uniqueSourceNodes"),
        "uniqueSourceNodesIncludingT75": base_counts.get("uniqueSourceNodes", 0) + len(source_rows),
        "sourceOnlyUnboundIncludingT75": base_counts.get("sourceOnlyUnbound", 0) + len(source_rows),
        "newCanonicalBindings": 0,
        "newHumanReviewed": 0,
    }
    extension["t75Inputs"] = {
        "frozenSourceSetSha256": freeze_sha,
        "acquisitionEvidencePath": acq_path.relative_to(ROOT).as_posix(),
        "acquisitionManifestSha256": sha_file(acq_path),
        "t75SourceManifestSha256": sha_file(OUT_SOURCE),
        "t75GlbSha256": glb_digest,
        "productRegionMembershipRows": 12,
        "uniqueNewFjNodes": 6,
    }
    extension["publicRedistribution"] = "held_pending_file_level_license_reconciliation_with_legacy_OBJ_headers"
    write_immutable_json(OUT_INTEGRATION, extension)

    validation = {
        "revision": "T75-PACKAGE-VALIDATION-v1",
        "task": "T75",
        "result": "pass",
        "frozenIdsMatchAcquiredAndBuilt": len(source_rows) == len(mesh_inputs) == len(mesh_records) == len(gltf["nodes"]) == 6,
        "exactFrozenSourceIds": [row["sourceElementFileId"] for row in source_rows],
        "noExtraSourceIds": {row["sourceElementFileId"] for row in source_rows} == set(EXPECTED),
        "internalBatchCounts": [batch["count"] for batch in frozen["internalBatches"]],
        "exactOfficialIsaFjFmaBpRows": True,
        "genericAndZoneContextRowsAreNotAdditionalGeometry": True,
        "wholeDeltoidNotInferredFromPartSurface": True,
        "exactEnglishNameAndSideHeader": True,
        "sideNotInferredFromMFilenameSuffixOrCoordinates": True,
        "archiveMemberCrcShaSizeVerified": True,
        "allSixHaveActualVerticesNormalsAndTriangles": all(row["sourceVertexCount"] > 0 and row["sourceNormalCount"] == row["sourceVertexCount"] and row["sourceTriangleCount"] > 0 for row in source_rows),
        "headerBoundsVersusVertexExtremaMm": {row["sourceElementFileId"]: {"maxAbsDeltaMm": row["sourceBoundsHeaderMaxAbsDeltaMm"], "within001mm": row["sourceBoundsHeaderWithin001mm"]} for row in source_rows},
        "sourceAndProjectFramePoseUnitsMatchT50": all(row["projectFrame"] == FRAME and row["sourcePose"] == POSE and row["projectUnit"] == "m" for row in source_rows),
        "noMirrorOrRecenter": True,
        "duplicateRawSourceHashGroups": duplicate_raw_groups,
        "duplicateConvertedGeometryTopologyGroups": duplicate_geometry_groups,
        "oneGlbNodePerUniqueFj": len(gltf["nodes"]) == 6 and len({node["name"] for node in gltf["nodes"]}) == 6,
        "glbPositionBuffersMatchTransform": True,
        "oneStableNodeAcrossTwoProductRegionMemberships": all(len(row["regionMemberships"]) == 2 and len({m["stableRenderNodeId"] for m in row["regionMemberships"]}) == 1 for row in source_rows),
        "membershipRowsDoNotDuplicateMeshes": extension["counts"]["t75RegionMembershipRows"] == 12 and extension["counts"]["t75UniqueSourceNodes"] == 6,
        "historicalT53T54T70T74InputsPreserved": True,
        "noTargetIdCollisionWithPriorPackages": True,
        "canonicalLearnerBindings": 0,
        "defaultVisible": False,
        "humanAnatomyReviewed": False,
        "redistributionHold": True,
        "publicRelease": False,
        "latissimusDorsi": "unavailable_in_r4_no_substitute_geometry_T93_research_only",
        "wholeDeltoidComplete": False,
        "wholeBodyCanonicalDenominator": None,
        "derivedGlb": {"path": GLB.relative_to(ROOT).as_posix(), "sha256": glb_digest, "bytes": len(output), "nodeCount": len(gltf["nodes"])},
        "sourceManifest": {"path": OUT_SOURCE.relative_to(ROOT).as_posix(), "sha256": sha_file(OUT_SOURCE)},
        "integrationExtension": {"path": OUT_INTEGRATION.relative_to(ROOT).as_posix(), "sha256": sha_file(OUT_INTEGRATION)},
    }
    write_immutable_json(OUT_VALIDATION, validation)
    return validation


def main() -> int:
    try:
        validation = validate_and_build()
    except Exception as exc:
        print(f"T75 build failed closed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
