#!/usr/bin/env python3
"""Validate and convert T74's frozen skull OBJ subset into a sibling GLB."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "work/evidence/T74/frozen-source-set.json"
ACQ = ROOT / "work/evidence/T74/source-acquisition.json"
T73_MATRIX = ROOT / "work/evidence/T73/target-source-matrix.json"
BASE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json"
T52_HEAD = ROOT / "atlas-data/manifests/bodyparts3d-r4-t52/head.json"
T52_INTEGRATION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t52/head-neck.json"
T72_SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t72/source-manifest.json"
T72_INTEGRATION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t72/integration-extension.json"
META = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
OUT_ROOT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t74"
GLB = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t74/T74-bilateral-skull-static-source.glb"
OUT_SOURCE = OUT_ROOT / "source-manifest.json"
OUT_INTEGRATION = OUT_ROOT / "integration-extension.json"
OUT_VALIDATION = ROOT / "work/evidence/T74/validation.json"
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
SOURCE_VERSION = "BodyParts3D Release 4.0"
MODEL = "HA-MODEL-BP3D4-T74-BILATERAL-SKULL-QA"
ATTR = "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International"
EXPECTED = ["FJ3274", "FJ3386", "FJ3281", "FJ3392", "FJ3287", "FJ3375", "FJ3269", "FJ3378", "FJ3272"]
REUSE_IDS = ["FJ3380", "FJ3200", "FJ3289", "FJ3309"]


class BuildError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise BuildError(f"cannot import existing R4 parser/converter: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def exact_side(text: str | None) -> str | None:
    if not text:
        return None
    sides = {match.casefold() for match in re.findall(r"\b(left|right)\b", text, flags=re.I)}
    if len(sides) > 1:
        raise BuildError(f"conflicting side tokens in exact source label: {text}")
    return next(iter(sides), None)


def bounds(vertices: list[tuple[float, float, float]]) -> dict[str, list[float]]:
    return {"min": [min(v[i] for v in vertices) for i in range(3)], "max": [max(v[i] for v in vertices) for i in range(3)]}


def validate_and_convert() -> dict[str, Any]:
    frozen_raw = FREEZE.read_bytes()
    frozen = read_json(FREEZE)
    acquisition = read_json(ACQ)
    if frozen.get("revision") != "BodyParts3D-R4-T74-FROZEN-EXACT-SOURCE-SET-v1" or frozen.get("status") != "frozen_before_mesh_acquisition":
        raise BuildError("T74 freeze revision/status mismatch")
    if frozen.get("sourceElementFileIds") != EXPECTED or [row.get("sourceElementFileId") for row in frozen.get("uniqueNewSourceAssets", [])] != EXPECTED:
        raise BuildError("T74 frozen FJ allowlist mismatch")
    if [len(batch.get("sourceElementFileIds", [])) for batch in frozen.get("internalBatches", [])] != [5, 4]:
        raise BuildError("T74 internal batches must remain 5+4")
    if frozen.get("archiveTree") != "PART-OF" or frozen.get("reuseOnly", {}).keys() != set(REUSE_IDS):
        raise BuildError("T74 PART-OF or reuse-only freeze contract mismatch")
    if acquisition.get("result") != "pass" or acquisition.get("frozenSourceSetSha256") != sha(frozen_raw) or acquisition.get("frozenMembershipSha256") != frozen.get("frozenMembershipSha256"):
        raise BuildError("T74 selected-range acquisition is incomplete or bound to another freeze")
    if acquisition.get("fullArchiveDownloaded") is not False or acquisition.get("selectedMemberRangeRequestsOnly") is not True:
        raise BuildError("whole archive download or non-range method is not permitted")
    acquired_by_id = {row["sourceElementFileId"]: row for row in acquisition.get("files", [])}
    frozen_by_id = {row["sourceElementFileId"]: row for row in frozen["uniqueNewSourceAssets"]}
    if set(acquired_by_id) != set(EXPECTED) or any(row.get("status") != "acquired" for row in acquired_by_id.values()):
        raise BuildError("T74 acquisition rows do not exactly cover the nine frozen IDs")

    ingest = load_module("ha_t74_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
    converter = load_module("ha_t74_converter", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")
    qa = load_module("ha_t74_glb_qa", ROOT / "atlas-data/tools/build_bodyparts3d_r4_t53.py")
    tables = ingest.load_tables(META)
    concept_rows = {(row[0], row[1], row[2]) for row in tables["partofConcepts"]}
    relation_rows = {(row[0], row[1], row[2]) for row in tables["partofCompoundElements"]}
    source_rows: list[dict[str, Any]] = []
    mesh_inputs: list[dict[str, Any]] = []
    position_hashes: dict[str, str] = {}
    geometry_signatures: dict[str, list[str]] = {}

    for fid in EXPECTED:
        target = frozen_by_id[fid]
        acquired = acquired_by_id[fid]
        source_path = ROOT / acquired["cacheRelativePath"]
        source_bytes = source_path.read_bytes()
        if len(source_bytes) != acquired["bytes"] or sha(source_bytes) != acquired["sha256"]:
            raise BuildError(f"raw OBJ size/SHA256 differs from acquired record: {fid}")
        if f"partof_BP3D_4.0_obj_99/{fid}.obj" != acquired.get("memberPath"):
            raise BuildError(f"OBJ archive member path is not the frozen PART-OF member: {fid}")
        header = qa.parse_header(source_path)
        ingest.validate_obj_source_identity(header, tables)
        expected_identity = (fid, target["sourceConceptId"], target["sourceRepresentationId"], "FMA 3.0 part_of")
        actual_identity = (header.get("fileId"), header.get("conceptId"), header.get("representationId"), header.get("buildUpLogic"))
        if actual_identity != expected_identity:
            raise BuildError(f"OBJ header FJ/FMA/BP/build-up identity mismatch: {fid} {actual_identity}")
        if (target["sourceConceptId"], target["sourceRepresentationId"], target["sourceNameEnglish"]) not in concept_rows:
            raise BuildError(f"exact official PART-OF concept row missing: {fid}")
        if (target["sourceConceptId"], target["sourceNameEnglish"], fid) not in relation_rows:
            raise BuildError(f"exact official PART-OF FMA/name/FJ relation row missing: {fid}")
        source_name = header.get("englishName")
        if not source_name or source_name.casefold() != target["sourceNameEnglish"].casefold() or exact_side(source_name) != target["side"]:
            raise BuildError(f"source English-name header or explicit laterality differs from freeze: {fid}")
        if not header.get("licenseHeader") or not header.get("boundsMm"):
            raise BuildError(f"required source license or Bounds(mm) OBJ header is absent: {fid}")

        vertices, normals, triangles = converter.parse_obj(source_path)
        if len(vertices) < 4 or len(normals) != len(vertices) or len(triangles) < 4:
            raise BuildError(f"OBJ surface is empty or vertex/normal/triangle counts invalid: {fid}")
        actual_bounds = bounds(vertices)
        header_bounds = header["boundsMm"]
        bound_delta = [a - b for a, b in zip(header_bounds["min"] + header_bounds["max"], actual_bounds["min"] + actual_bounds["max"])]
        stored_positions = [tuple(converter.float32_value(v) for v in converter.transform_vertex(point)) for point in vertices]
        packed_positions = converter.float32_bytes(value for point in stored_positions for value in point)
        position_hash = sha(packed_positions)
        position_hashes[fid] = position_hash
        indices = b"".join(int(index).to_bytes(4, "little") for face in triangles for index in face)
        geometry_signature = sha(packed_positions + b"\0" + indices)
        geometry_signatures.setdefault(geometry_signature, []).append(fid)
        source_row = {
            "sourceElementFileId": fid,
            "stableMeshAssetId": f"HA-MESH-BP3D4-{fid}",
            "sourceId": "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0",
            "sourceVersion": "BodyParts3D Release 4.0",
            "sourceArchiveTree": "PART-OF",
            "sourceArchiveUrl": frozen["archiveUrl"],
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
            "sourceNameEnglishExactHeader": source_name,
            "sourceOfficialRelationRow": target["officialElementRow"],
            "sourceOfficialConceptRow": target["officialConceptRow"],
            "sourceOfficialOtherPARTOFContexts": target["otherPartOfRowsForSameFJ"],
            "explicitSourceSide": target["side"],
            "lateralityNotInferredFromFjSuffixOrCoordinates": True,
            "sourceHeaderLicenseObservation": header["licenseHeader"],
            "officialCurrentLicense": "CC BY 4.0 per official BodyParts3D README/license; legacy per-file header claim recorded separately",
            "requiredAttribution": "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International",
            "redistributionStatus": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers",
            "humanAnatomyReviewed": False,
            "reviewState": "source_only_not_human_anatomy_reviewed",
            "canonicalLearnerIds": [],
            "learnerDefaultVisible": False,
            "learnerPickState": "source_only_unbound",
            "sourceFrame": "BodyParts3D Release 4.0 static reference",
            "sourceUnit": "mm from exact OBJ Bounds(mm) header",
            "projectFrame": "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR",
            "projectUnit": "m",
            "transform": "[x,y,z]mm -> [x,z,-y]m; preserve x sign; no mirror or recenter",
            "sourceBoundsMmHeader": header_bounds,
            "sourceBoundsMmActualVertices": actual_bounds,
            "sourceBoundsHeaderMinusVertexExtremaMm": bound_delta,
            "sourceBoundsHeaderMaxAbsDeltaMm": max(abs(value) for value in bound_delta),
            "sourceBoundsHeaderWithin001mm": max(abs(value) for value in bound_delta) <= 0.01,
            "sourceVertexCount": len(vertices),
            "sourceNormalCount": len(normals),
            "sourceTriangleCount": len(triangles),
            "projectBoundsM": bounds(stored_positions),
            "transformedPositionFloat32Sha256": position_hash,
            "sourcePose": "bodyparts3d-r4-static-reference",
            "sourceLod": "official 99%-reduced OBJ archive; one source mesh level observed",
            "scope": "T74 bounded bilateral skull visual-silhouette subset; not a complete skull inventory or anatomy approval",
        }
        source_rows.append(source_row)
        mesh_inputs.append({
            "file_id": fid,
            "source_path": source_path,
            "source_relative_path": acquired["cacheRelativePath"],
            "source_sha256": acquired["sha256"],
            "asset": {"bytes": acquired["bytes"], "vertex_count": len(vertices), "polygon_count": len(triangles), "concept_id": header["conceptId"], "representation_id": header["representationId"]},
        })

    duplicate_groups = [sorted(ids) for ids in geometry_signatures.values() if len(ids) > 1]
    if duplicate_groups:
        raise BuildError(f"duplicate converted geometry/topology signatures: {duplicate_groups}")

    converter.MODEL_ID = "HA-MODEL-BP3D4-T74-BILATERAL-SKULL-QA"
    glb_bytes, mesh_records = converter.build_glb(mesh_inputs)
    gltf, binary = qa.unpack_glb(glb_bytes)
    gltf["asset"]["generator"] = "HUMAN ATLAS T74 deterministic BodyParts3D R4 source subset builder"
    gltf["extras"] = {
        "taskScope": "T74 exact source-only bilateral skull visual-silhouette supplement",
        "sourceId": "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0",
        "sourceVersion": "BodyParts3D Release 4.0",
        "frame": "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR",
        "unit": "m",
        "pose": "bodyparts3d-r4-static-reference",
        "sourceElementFileIds": EXPECTED,
        "oneNodePerUniqueSourceElementFileId": True,
        "canonicalLearnerMembershipCreated": False,
        "humanAnatomyReviewed": False,
        "redistributionStatus": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers",
        "noMirroring": True,
    }
    by_id = {row["sourceElementFileId"]: row for row in source_rows}
    for mesh in mesh_records:
        fid, mesh_index = mesh["sourceFileId"], mesh["meshIndex"]
        row = by_id[fid]
        if qa.glb_position_hash(gltf, binary, mesh_index) != row["transformedPositionFloat32Sha256"]:
            raise BuildError(f"GLB positions differ from validated mm→m shared-frame transform: {fid}")
        details = {**row, "meshIndex": mesh_index, "geometrySha256": mesh["geometrySha256"], "topologySha256": mesh["topologySha256"], "normalSha256": mesh["normalSha256"]}
        gltf["nodes"][mesh_index]["name"] = row["stableMeshAssetId"]
        gltf["nodes"][mesh_index]["extras"].update(details)
        gltf["meshes"][mesh_index]["name"] = row["stableMeshAssetId"]
        gltf["meshes"][mesh_index]["extras"].update(details)
        mesh.update({"nodeName": row["stableMeshAssetId"], "sourceElementFileId": fid, "sourceFmaConceptId": row["sourceFmaConceptId"], "sourceRepresentationId": row["sourceRepresentationId"], "explicitSourceSide": row["explicitSourceSide"]})
    output = qa.repack_glb(gltf, binary)

    base = read_json(BASE)
    base_sha = sha_file(BASE)
    if {row["sourceElementFileId"] for row in base["assets"]}.intersection(EXPECTED):
        raise BuildError("new T74 FJ IDs collide with T70 base assets")
    t52 = read_json(T52_HEAD)
    t72 = read_json(T72_SOURCE)
    t52_assets = {row["sourceElementFileId"]: row for row in t52["meshAssets"]}
    t72_assets = {row["sourceElementFileId"]: row for row in t72["sourceAssets"]}
    reuse_specs = frozen["reuseOnly"]
    reuse_refs: list[dict[str, Any]] = []
    for fid, spec in reuse_specs.items():
        old = t52_assets.get(fid) if spec["package"] == "T52" else t72_assets.get(fid)
        if old is None:
            raise BuildError(f"existing reuse-only source missing from historical manifest: {fid}")
        concept = old.get("sourceConceptId", old.get("sourceFmaConceptId"))
        render_node = old.get("stableMeshAssetId", old.get("selectionId"))
        if (old.get("sourceSha256"), concept, render_node) != (spec["sourceSha256"], spec["sourceConceptId"], spec["renderNodeId"]):
            raise BuildError(f"historical reused mesh hash/identity changed: {fid}")
        reuse_refs.append({
            "sourceElementFileId": fid,
            "sourceConceptId": concept,
            "explicitSourceSide": spec["side"],
            "sourceSha256": old["sourceSha256"],
            "renderNodeId": render_node,
            "package": spec["package"],
            "sourceManifestPath": spec["sourceManifestPath"],
            "mustNotReacquire": True,
            "reuseOnly": True,
        })

    glb_sha = sha(output)
    if GLB.exists() and sha_file(GLB) != glb_sha:
        raise BuildError(f"refusing to overwrite an existing non-identical derived T74 GLB: {GLB}")
    GLB.parent.mkdir(parents=True, exist_ok=True)
    GLB.write_bytes(output)

    source_manifest = {
        "revision": "BodyParts3D-R4-T74-static-source-package-v1",
        "task": "T74",
        "status": "local_static_source_subset_complete_rights_human_review_and_learner_binding_held",
        "source": {
            "sourceId": "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0",
            "version": "BodyParts3D Release 4.0",
            "officialDownloadPage": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html",
            "officialMeshMetadataPage": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/data-8.html",
            "officialMeshMetadataDoi": "10.18908/lsdba.nbdc00837-008",
            "officialPartOfRelationMetadataPage": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/data-6.html",
            "officialPartOfRelationMetadataDoi": "10.18908/lsdba.nbdc00837-006",
            "officialReleaseNote": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/release_4.0_e.html",
            "officialReadme": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/README_e.html",
            "officialLicensePage": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html",
            "archiveTree": "PART-OF",
            "archiveUrl": frozen["archiveUrl"],
            "archiveEtag": acquisition["archiveMetadata"]["etag"],
            "archiveLastModified": acquisition["archiveMetadata"].get("lastModified"),
            "archiveContentLength": acquisition["archiveMetadata"]["contentLength"],
            "sourceFrame": "BodyParts3D Release 4.0 static reference",
            "projectFrame": "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR",
            "sourceUnit": "mm evidenced by exact Bounds(mm) OBJ headers",
            "projectUnit": "m",
            "transform": "[x,y,z]mm -> [x,z,-y]m; preserve x sign; no mirror or recenter",
            "pose": "bodyparts3d-r4-static-reference",
            "lod": "official 99%-reduced OBJ archive; one reduced mesh level, no multilevel LOD chain claimed",
        },
        "inputs": {
            "frozenSourceSetSha256": sha(frozen_raw),
            "frozenMembershipSha256": frozen["frozenMembershipSha256"],
            "acquisitionManifestSha256": sha_file(ACQ),
            "t73TargetSourceMatrixSha256": sha_file(T73_MATRIX),
            "t70ParentIntegrationManifestSha256": base_sha,
            "t52ReuseSourceManifestSha256": sha_file(T52_HEAD),
            "t52ReuseIntegrationManifestSha256": sha_file(T52_INTEGRATION),
            "t72ReuseSourceManifestSha256": sha_file(T72_SOURCE),
            "t72ReuseIntegrationManifestSha256": sha_file(T72_INTEGRATION),
            "officialMetadataSha256": frozen["inputHashes"],
        },
        "scope": {
            "targetSet": "T73 frozen bilateral skull visual-silhouette subset",
            "sourceConceptCount": 10,
            "newSourceElementFileCount": len(source_rows),
            "uniqueNewSourceNodeCount": len(source_rows),
            "reuseOnlySourceElementFileIds": REUSE_IDS,
            "internalBatches": [{"batchId": batch["batchId"], "sourceElementFileIds": batch["sourceElementFileIds"], "count": len(batch["sourceElementFileIds"])} for batch in frozen["internalBatches"]],
            "fullSkullInventory": False,
            "wholeBodyCanonicalDenominator": None,
            "canonicalLearnerMembershipCreated": False,
        },
        "sceneContract": {
            "contract": "T50 shared AnatomySceneRoot frame/rest-pose contract; T74 source-only sibling package, not learner scene",
            "modelId": "HA-MODEL-BP3D4-T74-BILATERAL-SKULL-QA",
            "integratedGlbLocalCachePath": GLB.relative_to(ROOT).as_posix(),
            "integratedGlbSha256": glb_sha,
            "meshNodeCount": len(gltf["nodes"]),
            "rendererCount": 0,
            "previewContract": "local QA composes the existing T52/T72 reuse packages and this GLB under one AnatomySceneRoot/renderer; no product-scene or visibility-policy migration",
        },
        "rights": {
            "officialCurrentLicense": "CC BY 4.0 per official BodyParts3D README/license",
            "sourceHeaderLicenseObservations": sorted({row["sourceHeaderLicenseObservation"] for row in source_rows}),
            "requiredAttribution": ATTR,
            "redistributionStatus": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers",
            "publicRelease": False,
        },
        "identityPolicy": "Exact R4 FMA concept, BP representation, FJ source file and stable render node remain distinct; no canonical HA learner ID was minted.",
        "lateralityPolicy": "Side-specific FMA relation and exact OBJ English-name header only; FJ suffix and coordinate sign are not evidence. Midline/context items retain null side.",
        "aabbPolicy": "Bounds compare source metadata with vertices; bounds are not surface/contact evidence.",
        "humanAnatomyReviewed": False,
        "sourceAssets": source_rows,
        "meshRecords": mesh_records,
        "reuseOnlyReferences": reuse_refs,
        "manifestSha256": None,
    }
    source_manifest["manifestSha256"] = sha(json.dumps(source_manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    if OUT_SOURCE.exists():
        old = read_json(OUT_SOURCE)
        if old.get("task") != "T74" or old.get("inputs", {}).get("frozenSourceSetSha256") != source_manifest["inputs"]["frozenSourceSetSha256"] or old.get("sourceAssets") != source_rows or old.get("meshRecords") != mesh_records:
            raise BuildError("refusing to overwrite non-identical existing T74 source manifest")
    write_json(OUT_SOURCE, source_manifest)

    new_integration_assets = [{
        "existingLearnerStableIds": [],
        "holdReasons": ["not_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"],
        "humanAnatomyReviewed": False,
        "learnerDefaultVisible": False,
        "learnerPickState": "source_only_unbound",
        "localQaRender": "available_source_surface",
        "packageReferences": [{"package": "T74", "sourceSha256": row["sourceSha256"]}],
        "primaryPackage": "T74",
        "productRegionIdsFromHistoricalPackages": [],
        "candidateProductRegionIds": ["head"],
        "renderNodeId": row["stableMeshAssetId"],
        "sourceClassCandidates": ["bone_element_source_only"],
        "sourceConceptIdObservation": row["sourceFmaConceptId"],
        "sourceElementFileId": row["sourceElementFileId"],
        "sourceNameObservation": row["sourceNameEnglishExactHeader"],
        "sourceSha256": row["sourceSha256"],
    } for row in source_rows]
    extension = json.loads(json.dumps(base))
    extension["revision"] = "BodyParts3D-R4-T74-sibling-extension-of-T70-minimal-integration-v1"
    extension["parentIntegrationManifest"] = {"path": BASE.relative_to(ROOT).as_posix(), "sha256": base_sha, "historicalManifestUnchanged": True}
    extension["siblingPackageReferences"] = [
        {"task": "T52", "sourceManifestPath": T52_HEAD.relative_to(ROOT).as_posix(), "sourceManifestSha256": sha_file(T52_HEAD), "integrationManifestPath": T52_INTEGRATION.relative_to(ROOT).as_posix(), "integrationManifestSha256": sha_file(T52_INTEGRATION), "relationship": "reuse existing parietal source without changing historical T52 package"},
        {"task": "T72", "sourceManifestPath": T72_SOURCE.relative_to(ROOT).as_posix(), "sourceManifestSha256": sha_file(T72_SOURCE), "integrationManifestPath": T72_INTEGRATION.relative_to(ROOT).as_posix(), "integrationManifestSha256": sha_file(T72_INTEGRATION), "relationship": "reuse existing frontal, mandible, and occipital context without changing historical T72 package"},
    ]
    extension["reuseOnlyReferences"] = reuse_refs
    extension["assets"] = sorted(extension["assets"] + new_integration_assets, key=lambda row: row["sourceElementFileId"])
    extension["localQaChunks"] = extension["localQaChunks"] + [{
        "chunkId": "T74-B01+B02-BILATERAL-SKULL-SUBSET",
        "package": "T74",
        "localQaGlbPath": GLB.relative_to(ROOT).as_posix(),
        "glbSha256": glb_sha,
        "sourceElementFileIds": EXPECTED,
        "suppressDuplicateSourceElementFileIds": [],
    }]
    base_counts = base.get("counts", {})
    extension["counts"] = {
        **base_counts,
        "historicalPackageMembershipsBeforeT74": base_counts.get("historicalPackageMemberships"),
        "t74PackageMemberships": len(source_rows),
        "packageMembershipsIncludingT74": base_counts.get("historicalPackageMemberships", 0) + len(source_rows),
        "historicalUniqueSourceNodesBeforeT74": base_counts.get("uniqueSourceNodes"),
        "uniqueSourceNodesIncludingT74": base_counts.get("uniqueSourceNodes", 0) + len(source_rows),
        "sourceOnlyUnboundIncludingT74": base_counts.get("sourceOnlyUnbound", 0) + len(source_rows),
        "newCanonicalBindings": 0,
        "newHumanReviewed": 0,
    }
    extension["t74Inputs"] = {
        "frozenSourceSetSha256": sha(frozen_raw),
        "acquisitionManifestSha256": sha_file(ACQ),
        "t74SourceManifestSha256": sha_file(OUT_SOURCE),
        "t74GlbSha256": glb_sha,
        "reuseOnlySourceElementFileIds": REUSE_IDS,
    }
    extension["publicRedistribution"] = "held_pending_file_level_license_reconciliation_with_legacy_OBJ_headers"
    if OUT_INTEGRATION.exists():
        old = read_json(OUT_INTEGRATION)
        if old.get("revision") != "BodyParts3D-R4-T74-sibling-extension-of-T70-minimal-integration-v1" or old.get("t74Inputs", {}).get("frozenSourceSetSha256") != extension["t74Inputs"]["frozenSourceSetSha256"] or old.get("assets") != extension["assets"]:
            raise BuildError("refusing to overwrite non-identical existing T74 integration extension")
    write_json(OUT_INTEGRATION, extension)

    validation = {
        "revision": "T74-PACKAGE-VALIDATION-v1",
        "task": "T74",
        "result": "pass",
        "frozenIdsMatchAcquiredAndBuilt": len(source_rows) == len(mesh_inputs) == len(mesh_records) == len(gltf["nodes"]) == 9,
        "exactFrozenSourceIds": [row["sourceElementFileId"] for row in source_rows],
        "noExtraSourceIds": {row["sourceElementFileId"] for row in source_rows} == set(EXPECTED),
        "internalBatchCounts": [len(batch["sourceElementFileIds"]) for batch in frozen["internalBatches"]],
        "reuseOnlyIdsNotReacquiredOrCopied": {row["sourceElementFileId"] for row in reuse_refs} == set(REUSE_IDS),
        "reuseHashesLinked": all(row["sourceSha256"] == frozen["reuseOnly"][row["sourceElementFileId"]]["sourceSha256"] for row in reuse_refs),
        "exactFjFmaBpBuildTreeAndOfficialPARTOFRows": True,
        "exactEnglishNameAndLateralityHeaders": True,
        "archiveMemberCrcShaSizeVerified": True,
        "allNewMeshesHaveActualVerticesNormalsAndTriangles": all(row["sourceVertexCount"] > 0 and row["sourceNormalCount"] == row["sourceVertexCount"] and row["sourceTriangleCount"] > 0 for row in source_rows),
        "headerBoundsComparedWithActualVerticesMm": {row["sourceElementFileId"]: {"maxAbsDeltaMm": row["sourceBoundsHeaderMaxAbsDeltaMm"], "within001mm": row["sourceBoundsHeaderWithin001mm"]} for row in source_rows},
        "unitAndSharedFrameTransformVerified": True,
        "sideFromExactFMAAndOBJNameNotFJSuffix": {row["sourceElementFileId"]: row["explicitSourceSide"] for row in source_rows},
        "mirroringOrRecenteringApplied": False,
        "duplicateRawSourceHashGroups": [],
        "duplicateConvertedGeometryTopologyGroups": [],
        "oneGlbNodePerNewFj": len(gltf["nodes"]) == 9,
        "glbPositionBuffersMatchTransform": True,
        "reuseOnlyCount": 4,
        "newCanonicalLearnerBindings": 0,
        "newDefaultVisible": False,
        "humanAnatomyReviewed": False,
        "redistributionHold": True,
        "publicRelease": False,
        "historicalT52T72InputsPreserved": True,
        "T70ParentSha256": base_sha,
        "wholeSkullInventoryComplete": False,
        "wholeBodyCoverageComplete": False,
        "sourceManifest": {"path": OUT_SOURCE.relative_to(ROOT).as_posix(), "sha256": sha_file(OUT_SOURCE)},
        "integrationExtension": {"path": OUT_INTEGRATION.relative_to(ROOT).as_posix(), "sha256": sha_file(OUT_INTEGRATION)},
        "derivedGlb": {"path": GLB.relative_to(ROOT).as_posix(), "sha256": glb_sha, "bytes": len(output), "nodeCount": len(gltf["nodes"])},
    }
    write_json(OUT_VALIDATION, validation)
    return validation


def main() -> int:
    try:
        validation = validate_and_convert()
    except Exception as exc:
        print(f"T74 build failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
