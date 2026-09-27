#!/usr/bin/env python3
"""Validate T76's exact pelvic-floor source members and build a sibling GLB."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "work/evidence/T76/frozen-source-set.json"
ACQ_TOOL = ROOT / "atlas-data/tools/acquire_bodyparts3d_r4_t76.py"
ACQ_DIR = ROOT / "work/evidence/T76"
MATRIX = ROOT / "work/evidence/T73/target-source-matrix.json"
T70 = ROOT / "atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json"
T53_SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json"
T53_REGION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t53/pelvis-perineum.json"
T53_GLB = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t53/T53-trunk-pelvis-static-source.glb"
META = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
OUT_ROOT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t76"
GLB = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t76/T76-pelvic-floor-static-source.glb"
OUT_SOURCE = OUT_ROOT / "source-manifest.json"
OUT_INTEGRATION = OUT_ROOT / "integration-extension.json"
OUT_VALIDATION = ROOT / "work/evidence/T76/validation.json"
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
SOURCE_VERSION = "BodyParts3D Release 4.0 (2013-05-16)"
MODEL = "HA-MODEL-BP3D4-T76-PELVIC-FLOOR-SOURCE"
ATTR = "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International"
EXPECTED_NEW = ["FJ1453M", "FJ1457M", "FJ1458M", "FJ2544", "FJ2545", "FJ2546", "FJ2549", "FJ2550", "FJ2551"]
EXPECTED_ALL = ["FJ1449M", "FJ1453M", "FJ1457M", "FJ1458M", "FJ2542", "FJ2544", "FJ2545", "FJ2546", "FJ2547", "FJ2549", "FJ2550", "FJ2551"]
REUSE = ["FJ1449M", "FJ2542", "FJ2547"]
BONE_CONTEXT = ["FJ3152", "FJ3288"]
REGION = "pelvis-perineum"


class BuildError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_immutable_json(path: Path, value: Any) -> None:
    raw = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") != raw:
        raise BuildError(f"refusing to replace a different immutable T76 artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(raw, encoding="utf-8")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise BuildError(f"cannot load existing R4 utility: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def exact_side(name: str | None) -> str | None:
    if not name:
        return None
    sides = {value.casefold() for value in re.findall(r"\b(left|right)\b", name, flags=re.I)}
    if len(sides) > 1:
        raise BuildError(f"conflicting laterality words in exact OBJ header: {name}")
    return next(iter(sides), None)


def bounds(vertices: list[tuple[float, float, float]]) -> dict[str, list[float]]:
    return {"min": [min(v[i] for v in vertices) for i in range(3)], "max": [max(v[i] for v in vertices) for i in range(3)]}


def successful_acquisition() -> tuple[Path, dict[str, Any]]:
    candidates = [ACQ_DIR / "source-acquisition.json", *sorted(ACQ_DIR.glob("source-acquisition-attempt-*.json"))]
    for path in reversed(candidates):
        if path.is_file():
            data = read_json(path)
            if data.get("result") == "pass":
                return path, data
    raise BuildError("T76 has no passing exact-member acquisition attempt; do not substitute or synthesize geometry")


def validate_and_build() -> dict[str, Any]:
    freeze_raw = FREEZE.read_bytes()
    frozen = read_json(FREEZE)
    if frozen.get("revision") != "BodyParts3D-R4-T76-FROZEN-PELVIC-FLOOR-SOURCE-SET-v1" or frozen.get("status") != "frozen_before_mesh_acquisition":
        raise BuildError("T76 immutable pre-acquisition freeze has wrong revision/status")
    if frozen.get("newSourceElementFileIds") != EXPECTED_NEW or frozen.get("targetElementFileIds") != EXPECTED_ALL:
        raise BuildError("T76 exact T73 target source IDs changed")
    if [row.get("count") for row in frozen.get("internalBatches", [])] != [5, 4] or max(row.get("count", 0) for row in frozen["internalBatches"]) > 10:
        raise BuildError("T76 batch limits changed")
    if [row.get("sourceElementFileId") for row in frozen.get("uniqueNewSourceAssets", [])] != EXPECTED_NEW:
        raise BuildError("T76 new member allowlist is not exact")
    if [row.get("sourceElementFileId") for row in frozen.get("reuseOnly", [])] != REUSE:
        raise BuildError("T76 T53 reuse-only set changed")
    for rel, digest in frozen.get("frozenInputSha256", {}).items():
        path = ROOT / rel
        if not path.is_file() or sha_file(path) != digest:
            raise BuildError(f"T76 frozen T73/T53/T70/history input changed: {rel}")

    acquisition_path, acquisition = successful_acquisition()
    acquirer = load_module("ha_t76_acquirer", ACQ_TOOL)
    acq_check = acquirer.check()
    if acq_check.get("result") != "pass" or acquisition.get("frozenSourceSetSha256") != sha(freeze_raw):
        raise BuildError("T76 acquisition is not complete or is bound to another frozen scope")
    if acquisition.get("attemptedIds") != EXPECTED_NEW or acquisition.get("fullArchiveDownloaded") is not False or acquisition.get("selectedMemberRangeRequestsOnly") is not True:
        raise BuildError("T76 selected-source acquisition violates its exact range-only policy")
    if len(acquisition.get("rangeRequests", [])) != 29 or not acquisition.get("allRangeResponsesHttp206"):
        raise BuildError("T76 acquisition must log 2 archive-index ranges plus 3 ranges per each of 9 files")
    acquired_by_id = {row["sourceElementFileId"]: row for row in acquisition.get("files", [])}
    frozen_by_id = {row["sourceElementFileId"]: row for row in frozen["uniqueNewSourceAssets"]}
    if set(acquired_by_id) != set(EXPECTED_NEW) or any(row.get("status") != "acquired" for row in acquired_by_id.values()):
        raise BuildError("T76 acquired IDs differ from the exact nine frozen new members")

    ingest = load_module("ha_t76_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
    converter = load_module("ha_t76_converter", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")
    qa = load_module("ha_t76_qa", ROOT / "atlas-data/tools/build_bodyparts3d_r4_t53.py")
    tables = ingest.load_tables(META)
    target_fmas = {row["sourceConceptId"] for row in frozen["sourceConcepts"]}
    target_relation_rows = {tuple(row) for concept in frozen["sourceConcepts"] for row in concept["officialElementRows"]}
    source_relation_rows = {tuple(row) for row in tables["isaCompoundElements"]}
    concept_rows = {tuple(row) for row in tables["isaConcepts"]}
    mesh_inputs: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    geometry_signatures: dict[str, list[str]] = {}
    for fid in EXPECTED_NEW:
        frozen_row = frozen_by_id[fid]
        acquired = acquired_by_id[fid]
        source_path = ROOT / acquired["cacheRelativePath"]
        raw = source_path.read_bytes()
        if len(raw) != acquired.get("bytes") or sha(raw) != acquired.get("sha256"):
            raise BuildError(f"T76 source OBJ bytes differ from verified selected archive payload: {fid}")
        if f"isa_BP3D_4.0_obj_99/{fid}.obj" != acquired.get("memberPath"):
            raise BuildError(f"T76 archive member is not the exact official IS-A member: {fid}")
        header = qa.parse_header(source_path)
        ingest.validate_obj_source_identity(header, tables)
        if header.get("fileId") != fid or header.get("buildUpLogic") != "FMA 3.0 is_a":
            raise BuildError(f"T76 OBJ File ID/build-up relation mismatch: {fid}")
        fma, bp = header.get("conceptId"), header.get("representationId")
        header_name = header.get("englishName")
        header_rel = (fma, header_name, fid)
        header_concept = (fma, bp, header_name)
        official_relation_rows = [row for row in source_relation_rows if row[0] == fma and row[2] == fid and row[1].casefold() == (header_name or "").casefold()]
        official_concept_rows = [row for row in concept_rows if row[0] == fma and row[1] == bp and row[2].casefold() == (header_name or "").casefold()]
        if len(official_relation_rows) != 1 or len(official_concept_rows) != 1:
            raise BuildError(f"T76 exact OBJ header FMA/name/FJ/BP identity not present in the official R4 tables: {fid} {header_concept}")
        if not header.get("licenseHeader") or not header.get("boundsMm"):
            raise BuildError(f"T76 source header lacks a file-level license observation or Bounds(mm): {fid}")
        side = exact_side(header_name)
        frozen_side = frozen_row.get("lateralityFromExactSideSpecificSourceConcepts")
        if frozen_side is not None and side != frozen_side:
            raise BuildError(f"T76 exact source concept-side and OBJ label-side differ for {fid}: {frozen_side}/{side}")

        vertices, normals, triangles = converter.parse_obj(source_path)
        if len(vertices) < 4 or len(normals) != len(vertices) or len(triangles) < 4:
            raise BuildError(f"T76 source surface is empty or malformed: {fid}")
        actual_bounds = bounds(vertices)
        header_bounds = header["boundsMm"]
        delta = [a - b for a, b in zip(header_bounds["min"] + header_bounds["max"], actual_bounds["min"] + actual_bounds["max"])]
        transformed = [tuple(converter.float32_value(v) for v in converter.transform_vertex(point)) for point in vertices]
        position_bytes = converter.float32_bytes(value for point in transformed for value in point)
        position_hash = sha(position_bytes)
        index_bytes = b"".join(int(i).to_bytes(4, "little") for tri in triangles for i in tri)
        geometry_signature = sha(position_bytes + b"\0" + index_bytes)
        geometry_signatures.setdefault(geometry_signature, []).append(fid)
        side_diagnostic = qa.side_surface_diagnostic(side, vertices, triangles)
        target_memberships = [row for row in frozen_row["sourceConceptMemberships"] if tuple((row["sourceConceptId"], row["sourceNameEnglish"], fid)) in target_relation_rows]
        if not target_memberships:
            raise BuildError(f"T76 source member has no frozen T73 concept membership: {fid}")
        if any(tuple((row["sourceConceptId"], row["sourceNameEnglish"], fid)) not in source_relation_rows for row in target_memberships):
            raise BuildError(f"T76 frozen target relation missing from official R4 source: {fid}")
        if len({row["sourceConceptId"] for row in target_memberships}) != len(target_memberships):
            raise BuildError(f"T76 duplicate target concept relation for one FJ member: {fid}")
        row = {
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
            "sourceHeaderIdentity": {"sourceFmaConceptId": fma, "sourceRepresentationId": bp, "sourceEnglishNameExactHeader": header_name, "sourceBuildUpLogic": header["buildUpLogic"], "officialConceptRow": list(official_concept_rows[0]), "officialElementRow": list(official_relation_rows[0]), "headerFmaIsAmongT73ConceptTargets": fma in target_fmas, "headerRelationIncludedInTargetMembership": tuple(official_relation_rows[0]) in target_relation_rows},
            "targetT73ConceptMemberships": target_memberships,
            "targetConceptMembershipRows": [list((r["sourceConceptId"], r["sourceNameEnglish"], fid)) for r in target_memberships],
            "sourceHeaderConceptOutsideFrozenTenConceptRows": fma not in target_fmas,
            "sourceHeaderConceptTreatment": "exact official header identity recorded, but not added as an extra T73 target concept or learner identity",
            "exactSourceSideFromHeader": side,
            "t73SideFromFrozenTargetConcepts": frozen_side,
            "lateralityNotInferredFromFjSuffixOrCoordinates": True,
            "surfaceSideDiagnostic": side_diagnostic,
            "sourceHeaderLicenseObservation": header["licenseHeader"],
            "officialCurrentLicenseObservation": "CC BY 4.0 on official page checked 2026-09-28; exact per-file header remains separately recorded",
            "requiredAttribution": ATTR,
            "redistributionStatus": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers",
            "humanAnatomyReviewed": False,
            "reviewState": "source_only_not_human_anatomy_reviewed",
            "canonicalLearnerIds": [],
            "learnerDefaultVisible": False,
            "learnerPickState": "source_only_unbound",
            "candidateProductRegionIds": [REGION],
            "sourceFrame": "BodyParts3D Release 4.0 static reference",
            "sourceUnit": "mm from exact OBJ Bounds(mm) header",
            "projectFrame": FRAME,
            "projectUnit": "m",
            "transform": "[x,y,z]mm -> [x,z,-y]m; preserve x sign; no mirror or recenter",
            "sourceBoundsMmHeader": header_bounds,
            "sourceBoundsMmActualVertices": actual_bounds,
            "sourceBoundsHeaderMinusVertexExtremaMm": delta,
            "sourceBoundsHeaderMaxAbsDeltaMm": max(abs(value) for value in delta),
            "sourceBoundsHeaderWithin001mm": max(abs(value) for value in delta) <= 0.01,
            "sourceVertexCount": len(vertices),
            "sourceNormalCount": len(normals),
            "sourceTriangleCount": len(triangles),
            "sourceSurfaceAreaMm2": sum(qa.triangle_area([vertices[index] for index in tri]) for tri in triangles),
            "projectBoundsM": bounds(transformed),
            "transformedPositionFloat32Sha256": position_hash,
            "sourcePose": POSE,
            "sourceLod": "official 99%-reduced IS-A OBJ; a single released level observed",
            "sourceIdentityState": "OBJ header FJ/FMA/BP/name matches official R4 metadata; human anatomical identity review not performed",
            "scope": "T76 exact selected source member; one stable node shared by all recorded target concept relations",
        }
        source_rows.append(row)
        mesh_inputs.append({
            "file_id": fid,
            "source_path": source_path,
            "source_relative_path": acquired["cacheRelativePath"],
            "source_sha256": acquired["sha256"],
            "asset": {"bytes": acquired["bytes"], "vertex_count": len(vertices), "polygon_count": len(triangles), "concept_id": fma, "representation_id": bp},
        })

    if [row["sourceElementFileId"] for row in source_rows] != EXPECTED_NEW:
        raise BuildError("T76 built new source rows differ from the exact nine FJ allowlist")
    duplicate_geometry = [sorted(ids) for ids in geometry_signatures.values() if len(ids) > 1]
    duplicate_raw = {}
    for row in source_rows:
        duplicate_raw.setdefault(row["sourceSha256"], []).append(row["sourceElementFileId"])
    duplicate_raw = [sorted(ids) for ids in duplicate_raw.values() if len(ids) > 1]
    if duplicate_geometry or duplicate_raw:
        raise BuildError(f"T76 source target set includes duplicate raw or exact transformed topology: {duplicate_raw}/{duplicate_geometry}")

    converter.MODEL_ID = MODEL
    glb_bytes, mesh_records = converter.build_glb(mesh_inputs)
    gltf, binary = qa.unpack_glb(glb_bytes)
    gltf["asset"]["generator"] = "HUMAN ATLAS T76 deterministic BodyParts3D R4 IS-A selected source builder"
    gltf["extras"] = {
        "taskScope": "T76 exact nine newly acquired pelvic-floor/perineum source members",
        "sourceId": SOURCE_ID,
        "sourceVersion": SOURCE_VERSION,
        "frame": FRAME,
        "unit": "m",
        "pose": POSE,
        "sourceElementFileIds": EXPECTED_NEW,
        "oneNodePerUniqueSourceElementFileId": True,
        "canonicalLearnerMembershipCreated": False,
        "humanAnatomyReviewed": False,
        "redistributionStatus": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers",
        "noMirroring": True,
        "noRecentering": True,
        "wholeBodyCanonicalDenominator": None,
    }
    by_id = {row["sourceElementFileId"]: row for row in source_rows}
    for mesh in mesh_records:
        fid, mesh_index = mesh["sourceFileId"], mesh["meshIndex"]
        row = by_id[fid]
        if qa.glb_position_hash(gltf, binary, mesh_index) != row["transformedPositionFloat32Sha256"]:
            raise BuildError(f"T76 GLB positions do not match shared T50 mm→m transform: {fid}")
        details = {**row, "meshIndex": mesh_index, "geometrySha256": mesh["geometrySha256"], "topologySha256": mesh["topologySha256"], "normalSha256": mesh["normalSha256"]}
        gltf["nodes"][mesh_index]["name"] = row["stableMeshAssetId"]
        gltf["nodes"][mesh_index]["extras"].update(details)
        gltf["meshes"][mesh_index]["name"] = row["stableMeshAssetId"]
        gltf["meshes"][mesh_index]["extras"].update(details)
        mesh.update({"nodeName": row["stableMeshAssetId"], "sourceElementFileId": fid, "sourceFmaConceptId": row["sourceHeaderIdentity"]["sourceFmaConceptId"], "sourceRepresentationId": row["sourceHeaderIdentity"]["sourceRepresentationId"], "explicitSourceSide": row["exactSourceSideFromHeader"]})
    output = qa.repack_glb(gltf, binary)
    glb_digest = sha(output)
    if GLB.exists() and sha_file(GLB) != glb_digest:
        raise BuildError(f"refusing to replace a different existing T76 derived GLB: {GLB}")
    GLB.parent.mkdir(parents=True, exist_ok=True)
    if not GLB.exists():
        GLB.write_bytes(output)

    base = read_json(T70)
    base_sha = sha_file(T70)
    base_assets = {row.get("sourceElementFileId"): row for row in base.get("assets", [])}
    collisions = set(base_assets) & set(EXPECTED_NEW)
    if collisions:
        raise BuildError(f"T76 new target IDs already exist in T70 base: {sorted(collisions)}")
    for fid in REUSE + BONE_CONTEXT:
        if fid not in base_assets:
            raise BuildError(f"T76 reuse/context ID missing from historical T70 base: {fid}")

    source_manifest = {
        "revision": "BodyParts3D-R4-T76-static-pelvic-floor-source-package-v1",
        "task": "T76",
        "status": "local_source_meshes_validated_rights_human_review_learner_binding_held",
        "source": {
            "sourceId": SOURCE_ID,
            "version": SOURCE_VERSION,
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
            "sourceUnit": "mm per selected OBJ Bounds(mm) header",
            "projectUnit": "m",
            "transform": "[x,y,z]mm -> [x,z,-y]m; x sign preserved; no mirroring or recentering",
            "pose": POSE,
            "lod": "official 99%-reduced IS-A OBJ; one source level, no alternate LOD claimed",
        },
        "inputs": {
            "frozenSourceSetSha256": sha(freeze_raw),
            "targetConceptMembershipSha256": frozen["targetConceptMembershipSha256"],
            "acquisitionEvidencePath": acquisition_path.relative_to(ROOT).as_posix(),
            "acquisitionManifestSha256": sha_file(acquisition_path),
            "t73TargetSourceMatrixSha256": sha_file(MATRIX),
            "t70ParentIntegrationManifestSha256": base_sha,
            "t53SourceManifestSha256": sha_file(T53_SOURCE),
            "t53PelvisPerineumManifestSha256": sha_file(T53_REGION),
            "t53IntegratedGlbSha256": sha_file(T53_GLB),
            "frozenInputSha256": frozen["frozenInputSha256"],
        },
        "scope": {
            "targetSet": "T73 exact pelvic-floor/perineum group/zone and side-concept sample",
            "sourceConceptCount": 10,
            "sourceElementFileCount": 12,
            "newSourceElementFileIds": EXPECTED_NEW,
            "newSourceNodeCount": 9,
            "t53ReuseOnlySourceElementFileIds": REUSE,
            "targetConceptToElementRelationCount": sum(len(row["officialElementRows"]) for row in frozen["sourceConcepts"]),
            "oneNodePerUniqueFj": True,
            "zoneIsSeparateGeometry": False,
            "declaresMissingPartsOrConcepts": False,
            "existingPelvisPerineumSample": frozen["existingPelvisPerineumReference"],
            "relatedBoneContextReferencesOnly": frozen["relatedExistingBoneContext"],
            "canonicalLearnerMembershipCreated": False,
            "wholeBodyCanonicalDenominator": None,
        },
        "sourceRepresentationInterpretation": frozen["sourceRepresentationInterpretation"],
        "sourceConceptTargets": frozen["sourceConcepts"],
        "targetConceptToElementCrosswalk": [
            {"sourceConceptId": concept["sourceConceptId"], "sourceRepresentationId": concept["sourceRepresentationId"], "sourceNameEnglish": concept["sourceNameEnglish"], "sourceSemanticLabel": concept["sourceSemanticLabel"], "memberSourceElementFileIds": [row[2] for row in concept["officialElementRows"]], "stableRenderNodeIds": [f"HA-MESH-BP3D4-{row[2]}" for row in concept["officialElementRows"]], "sameNodeReusedAcrossConceptRelations": True}
            for concept in frozen["sourceConcepts"]
        ],
        "reuseOnly": frozen["reuseOnly"],
        "relatedExistingBoneContext": frozen["relatedExistingBoneContext"],
        "sourceAssets": source_rows,
        "meshRecords": mesh_records,
        "rights": {
            "officialCurrentLicense": "CC BY 4.0 observed on the official database license page",
            "sourceHeaderLicenseObservations": sorted({row["sourceHeaderLicenseObservation"] for row in source_rows}),
            "requiredAttribution": ATTR,
            "redistributionStatus": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers",
            "publicRelease": False,
        },
        "humanAnatomyReviewed": False,
        "canonicalLearnerIds": [],
        "learnerDefaultVisible": False,
        "learnerPolicyChanged": False,
        "existingIdentityHold": frozen["existingPelvisPerineumReference"]["existingIdentityHold"],
        "sceneContract": {
            "contract": "T50 one persistent AnatomySceneRoot/frame/rest-pose; T76 is an opt-in local QA sibling package, not a learner-scene policy update",
            "modelId": MODEL,
            "integratedGlbLocalCachePath": GLB.relative_to(ROOT).as_posix(),
            "integratedGlbSha256": glb_digest,
            "meshNodeCount": len(gltf["nodes"]),
            "rendererCount": 0,
            "previewContract": "QA composes T53 and T76 once under one AnatomySceneRoot/renderer; reused T53 FJ nodes and related hip-bone context are never duplicated",
        },
        "manifestSha256": None,
    }
    source_manifest["manifestSha256"] = sha(json.dumps(source_manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    write_immutable_json(OUT_SOURCE, source_manifest)

    new_assets = []
    for row in source_rows:
        memberships = [{"regionId": REGION, "sourceElementFileId": row["sourceElementFileId"], "stableRenderNodeId": row["stableMeshAssetId"], "membershipBasis": "T73 frozen source-root candidate only; not a canonical/learner membership"}]
        new_assets.append({
            "existingLearnerStableIds": [],
            "holdReasons": ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"],
            "humanAnatomyReviewed": False,
            "learnerDefaultVisible": False,
            "learnerPickState": "source_only_unbound",
            "localQaRender": "available_source_surface",
            "packageReferences": [{"package": "T76", "sourceSha256": row["sourceSha256"]}],
            "primaryPackage": "T76",
            "productRegionIdsFromHistoricalPackages": [],
            "candidateProductRegionIds": [REGION],
            "regionMembershipRows": memberships,
            "renderNodeId": row["stableMeshAssetId"],
            "sourceClassCandidates": ["muscle_element_source_only"],
            "sourceConceptIdObservation": row["sourceHeaderIdentity"]["sourceFmaConceptId"],
            "sourceElementFileId": row["sourceElementFileId"],
            "sourceNameObservation": row["sourceHeaderIdentity"]["sourceEnglishNameExactHeader"],
            "sourceSha256": row["sourceSha256"],
            "singleStableNodeAcrossConceptRelations": True,
        })

    extension = json.loads(json.dumps(base))
    extension["revision"] = "BodyParts3D-R4-T76-sibling-extension-of-T70-pelvic-floor-v1"
    extension["parentIntegrationManifest"] = {"path": T70.relative_to(ROOT).as_posix(), "sha256": base_sha, "historicalManifestUnchanged": True}
    extension["siblingPackageReferences"] = [
        {"task": "T53", "sourceManifestPath": T53_SOURCE.relative_to(ROOT).as_posix(), "sourceManifestSha256": sha_file(T53_SOURCE), "pelvisPerineumManifestPath": T53_REGION.relative_to(ROOT).as_posix(), "pelvisPerineumManifestSha256": sha_file(T53_REGION), "integratedGlbPath": T53_GLB.relative_to(ROOT).as_posix(), "integratedGlbSha256": sha_file(T53_GLB), "relationship": "existing pelvis-perineum sample, FJ1449M/FJ2542/FJ2547 reuse, FJ1450 identity hold, and same-frame hip-bone context"},
        {"task": "T74", "sourceManifestPath": "atlas-data/manifests/bodyparts3d-r4-t74/source-manifest.json", "sourceManifestSha256": frozen["frozenInputSha256"]["atlas-data/manifests/bodyparts3d-r4-t74/source-manifest.json"], "relationship": "historic sibling package retained; no repackaging"},
        {"task": "T75", "sourceManifestPath": "atlas-data/manifests/bodyparts3d-r4-t75/source-manifest.json", "sourceManifestSha256": frozen["frozenInputSha256"]["atlas-data/manifests/bodyparts3d-r4-t75/source-manifest.json"], "relationship": "historic sibling package retained; no repackaging"},
    ]
    existing_ids = {row.get("sourceElementFileId") for row in extension.get("assets", [])}
    if existing_ids & set(EXPECTED_NEW):
        raise BuildError(f"T76 would duplicate new source nodes in T70 extension: {sorted(existing_ids & set(EXPECTED_NEW))}")
    extension["assets"] = sorted(extension["assets"] + new_assets, key=lambda row: row["sourceElementFileId"])
    extension["localQaChunks"] = extension["localQaChunks"] + [{
        "chunkId": "T76-B01-B02-PELVIC-FLOOR-SOURCE",
        "package": "T76",
        "localQaGlbPath": GLB.relative_to(ROOT).as_posix(),
        "glbSha256": glb_digest,
        "sourceElementFileIds": EXPECTED_NEW,
        "productRegionMembershipRows": len(EXPECTED_NEW),
        "targetConceptToElementRelationCount": sum(len(row["officialElementRows"]) for row in frozen["sourceConcepts"]),
        "suppressDuplicateSourceElementFileIds": REUSE + BONE_CONTEXT,
    }]
    counts = base.get("counts", {})
    extension["counts"] = {
        **counts,
        "historicalPackageMembershipsBeforeT76": counts.get("historicalPackageMemberships"),
        "t76UniqueNewSourceNodes": len(source_rows),
        "t76CandidateRegionMembershipRows": len(source_rows),
        "t76FrozenConceptCount": 10,
        "t76ConceptToElementRelations": sum(len(row["officialElementRows"]) for row in frozen["sourceConcepts"]),
        "t76ReuseOnlySourceNodeCount": len(REUSE),
        "t76RelatedBoneContextReferenceCount": len(BONE_CONTEXT),
        "packageMembershipsIncludingT76": counts.get("historicalPackageMemberships", 0) + len(source_rows),
        "uniqueSourceNodesIncludingT76": counts.get("uniqueSourceNodes", 0) + len(source_rows),
        "sourceOnlyUnboundIncludingT76": counts.get("sourceOnlyUnbound", 0) + len(source_rows),
        "newCanonicalBindings": 0,
        "newHumanReviewed": 0,
        "newRightsCleared": 0,
    }
    extension["t76Inputs"] = {
        "frozenSourceSetSha256": sha(freeze_raw),
        "acquisitionEvidencePath": acquisition_path.relative_to(ROOT).as_posix(),
        "acquisitionManifestSha256": sha_file(acquisition_path),
        "t76SourceManifestSha256": sha_file(OUT_SOURCE),
        "t76GlbSha256": glb_digest,
        "newUniqueFjNodes": len(source_rows),
        "targetConceptToElementRelationCount": sum(len(row["officialElementRows"]) for row in frozen["sourceConcepts"]),
        "canonicalLearnerBindings": 0,
        "humanAnatomyReviewed": 0,
        "wholeBodyCanonicalDenominator": None,
    }
    extension["publicRedistribution"] = "held_pending_file_level_license_reconciliation_with_legacy_OBJ_headers"
    extension["t76TargetConceptCrosswalk"] = source_manifest["targetConceptToElementCrosswalk"]
    extension["t76ReuseOnlyReferences"] = frozen["reuseOnly"]
    extension["t76RelatedBoneContextReferences"] = frozen["relatedExistingBoneContext"]
    extension["t76ExistingIdentityHold"] = frozen["existingPelvisPerineumReference"]["existingIdentityHold"]
    write_immutable_json(OUT_INTEGRATION, extension)

    validation = {
        "revision": "T76-PACKAGE-VALIDATION-v1",
        "task": "T76",
        "result": "pass",
        "frozenConceptCount": 10,
        "frozenTargetFjCount": 12,
        "exactNewSourceIds": [row["sourceElementFileId"] for row in source_rows],
        "exactT53ReuseOnlyIds": REUSE,
        "internalBatchCounts": [row["count"] for row in frozen["internalBatches"]],
        "exactOfficialFmaBpNameFjRows": True,
        "actualHeaderConceptNamesAndSide": {row["sourceElementFileId"]: {"FMA": row["sourceHeaderIdentity"]["sourceFmaConceptId"], "BP": row["sourceHeaderIdentity"]["sourceRepresentationId"], "name": row["sourceHeaderIdentity"]["sourceEnglishNameExactHeader"], "side": row["exactSourceSideFromHeader"], "sideDiagnostic": row["surfaceSideDiagnostic"]} for row in source_rows},
        "zoneAndConceptRelationsShareUniqueFjNodes": True,
        "puborectalisHeaderConceptsRecordedWithoutExpandingFrozenTargetSet": all(row["sourceHeaderIdentity"]["sourceFmaConceptId"] in {"FMA45856", "FMA45857"} if row["sourceHeaderConceptOutsideFrozenTenConceptRows"] else True for row in source_rows),
        "actualVerticesNormalsAndTriangles": {row["sourceElementFileId"]: {"vertices": row["sourceVertexCount"], "normals": row["sourceNormalCount"], "triangles": row["sourceTriangleCount"], "surfaceAreaMm2": row["sourceSurfaceAreaMm2"]} for row in source_rows},
        "headerBoundsVsVertexExtremaMm": {row["sourceElementFileId"]: {"maxAbsDeltaMm": row["sourceBoundsHeaderMaxAbsDeltaMm"], "within001mm": row["sourceBoundsHeaderWithin001mm"]} for row in source_rows},
        "sourceAndProjectFramePoseUnitsMatchT50": all(row["projectFrame"] == FRAME and row["sourcePose"] == POSE and row["sourceUnit"] == "mm from exact OBJ Bounds(mm) header" and row["projectUnit"] == "m" for row in source_rows),
        "noMirrorOrRecenter": True,
        "duplicateRawGroups": duplicate_raw,
        "duplicateConvertedGeometryTopologyGroups": duplicate_geometry,
        "oneGlbNodePerUniqueNewFj": len(gltf["nodes"]) == 9 and len({node["name"] for node in gltf["nodes"]}) == 9,
        "glbPositionBuffersMatchT50Transform": True,
        "reuseHashesUnchanged": {row["sourceElementFileId"]: row["sourceSha256"] for row in frozen["reuseOnly"]},
        "existingIdentityHoldPreserved": frozen["existingPelvisPerineumReference"]["existingIdentityHold"],
        "relatedHipBoneContextReferenceOnly": frozen["relatedExistingBoneContext"],
        "historicalT50T53T70T74T75InputsPreserved": True,
        "noTargetCollisionWithT70": True,
        "canonicalLearnerBindings": 0,
        "learnerPolicyChanged": False,
        "defaultVisible": False,
        "humanAnatomyReviewed": False,
        "redistributionHold": True,
        "perinealDenominatorComplete": False,
        "wholeBodyCanonicalDenominator": None,
        "boneContextGap": "T53 pelvis-perineum historical source slice declares 0 bone-context elements; paired existing hip bones FJ3152/FJ3288 are referenced from gluteal-hip as general bony-pelvis context only. Sacrum/coccyx bone source surface is not asserted or fabricated.",
        "derivedGlb": {"path": GLB.relative_to(ROOT).as_posix(), "sha256": glb_digest, "bytes": len(output), "nodeCount": len(gltf["nodes"])},
        "sourceManifest": {"path": OUT_SOURCE.relative_to(ROOT).as_posix(), "sha256": sha_file(OUT_SOURCE)},
        "integrationExtension": {"path": OUT_INTEGRATION.relative_to(ROOT).as_posix(), "sha256": sha_file(OUT_INTEGRATION)},
    }
    write_immutable_json(OUT_VALIDATION, validation)
    return validation


def main() -> int:
    try:
        result = validate_and_build()
    except Exception as exc:
        print(f"T76 build failed closed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
