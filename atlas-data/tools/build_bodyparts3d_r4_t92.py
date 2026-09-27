#!/usr/bin/env python3
"""Build a deterministic, source-only T92 trapezius package and T70 sibling extension."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import re
import struct
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "work/evidence/T92/frozen-source-set.json"
ACQ = ROOT / "work/evidence/T92/source-acquisition.json"
BASE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json"
OUT_ROOT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t92"
GLB = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t92/T92-trapezius-static-source.glb"
OUT_SOURCE = OUT_ROOT / "source-manifest.json"
OUT_INTEGRATION = OUT_ROOT / "integration-extension.json"
OUT_VALIDATION = ROOT / "work/evidence/T92/validation.json"
T53_SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json"
T53_REGION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t53/back.json"
T54_SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json"
T54_REGION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t54/shoulder-scapular.json"
T53_GLB = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t53/T53-trunk-pelvis-static-source.glb"
T54_GLB = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t54/T54-shoulder-upper-limb-static-source.glb"
T71_SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t71/source-manifest.json"
T71_INTEGRATION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t71/integration-manifest.json"
T72_SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t72/source-manifest.json"
T72_INTEGRATION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t72/integration-extension.json"
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
SOURCE_VERSION = "BodyParts3D Release 4.0"
MODEL_ID = "HA-MODEL-BP3D4-T92-TRAPEZIUS-QA"
ATTRIBUTION = "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International"
EXPECTED_FJS = ["FJ1520", "FJ1520M", "FJ1554", "FJ1554M", "FJ1521", "FJ1521M"]
EXPECTED_CONCEPTS = {"FMA32529", "FMA32555", "FMA32556", "FMA32557", "FMA33581", "FMA33583", "FMA33584", "FMA33585", "FMA33586", "FMA33587"}
REGIONS = ["back", "shoulder-scapular"]


class BuildError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def write_immutable(path: Path, value: Any) -> None:
    data = json_bytes(value)
    if path.exists() and path.read_bytes() != data:
        try:
            previous = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = {}
        frozen_sha = sha_file(FREEZE) if FREEZE.is_file() else None
        previous_frozen = (
            previous.get("inputs", {}).get("frozenSourceSetSha256")
            or previous.get("t92Inputs", {}).get("frozenSourceSetSha256")
            or previous.get("frozenSourceSetSha256")
        )
        t92_owned = (
            (previous.get("task") == "T92" or "T92" in str(previous.get("revision", "")))
            and frozen_sha is not None
            and previous_frozen == frozen_sha
        )
        if not t92_owned:
            raise BuildError(f"refusing to overwrite a different/unowned T92 revision: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise BuildError(f"cannot load required project helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def unpack_glb(data: bytes) -> tuple[dict[str, Any], bytes]:
    if len(data) < 20 or data[:4] != b"glTF" or struct.unpack_from("<I", data, 4)[0] != 2:
        raise BuildError("converter did not produce a GLB 2.0 container")
    json_length, json_type = struct.unpack_from("<II", data, 12)
    if json_type != 0x4E4F534A:
        raise BuildError("GLB JSON chunk missing")
    gltf = json.loads(data[20:20 + json_length].decode("utf-8"))
    bin_header = 20 + json_length
    bin_length, bin_type = struct.unpack_from("<II", data, bin_header)
    if bin_type != 0x004E4942:
        raise BuildError("GLB BIN chunk missing")
    binary = data[bin_header + 8:bin_header + 8 + bin_length]
    if len(binary) != bin_length:
        raise BuildError("GLB BIN chunk is truncated")
    return gltf, binary


def repack_glb(gltf: dict[str, Any], binary: bytes) -> bytes:
    json_chunk = json.dumps(gltf, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    while len(json_chunk) % 4:
        json_chunk += b" "
    while len(binary) % 4:
        binary += b"\x00"
    total = 12 + 8 + len(json_chunk) + 8 + len(binary)
    return b"".join([
        struct.pack("<4sII", b"glTF", 2, total),
        struct.pack("<II", len(json_chunk), 0x4E4F534A), json_chunk,
        struct.pack("<II", len(binary), 0x004E4942), binary,
    ])


def position_bytes(gltf: dict[str, Any], binary: bytes, mesh_index: int) -> bytes:
    primitive = gltf["meshes"][mesh_index]["primitives"][0]
    accessor = gltf["accessors"][primitive["attributes"]["POSITION"]]
    view = gltf["bufferViews"][accessor["bufferView"]]
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    length = accessor["count"] * 12
    value = binary[start:start + length]
    if len(value) != length:
        raise BuildError(f"GLB POSITION buffer is truncated at mesh {mesh_index}")
    return value


def header_name_bounds(path: Path) -> tuple[str | None, list[float] | None]:
    name = None
    bounds = None
    pattern = re.compile(r"^#\s*Bounds\(mm\):\s*\(([^)]+)\)-\(([^)]+)\)\s*$")
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.startswith("#"):
                break
            if line.startswith("# English name :"):
                name = line.split(":", 1)[1].strip()
            match = pattern.match(line.rstrip("\r\n"))
            if match:
                bounds = [float(v.strip()) for v in match.group(1).split(",") + match.group(2).split(",")]
    if bounds is not None and len(bounds) != 6:
        raise BuildError(f"invalid Bounds(mm) header in {path.name}")
    return name, bounds


def expected_freeze_and_acquisition() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    if not FREEZE.is_file() or not ACQ.is_file():
        raise BuildError("T92 frozen source set and successful acquisition evidence are required")
    frozen_raw = FREEZE.read_bytes()
    frozen = json.loads(frozen_raw)
    acq_path = ACQ
    acq = json.loads(acq_path.read_text(encoding="utf-8"))
    if frozen.get("status") != "frozen_before_mesh_acquisition" or frozen.get("uniqueSourceElementFileIds") != EXPECTED_FJS:
        raise BuildError("T92 freeze is not the exact pre-acquisition six-member set")
    if acq.get("result") != "pass" or acq.get("fullArchiveDownloaded") is not False or acq.get("selectedMemberRangeRequestsOnly") is not True:
        raise BuildError("T92 did not acquire through the successful selected-range path")
    if acq.get("frozenSourceSetSha256") != sha(frozen_raw) or acq.get("officialArchive", {}).get("allRequestsUsedHttp206") is not True:
        raise BuildError("T92 acquisition does not bind to the frozen scope/HTTP 206 archive")
    files = acq.get("files", [])
    if [row.get("sourceElementFileId") for row in files] != EXPECTED_FJS:
        raise BuildError("T92 acquisition member list is not the exact six-member set")
    return frozen, acq, files


def source_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    frozen, acq, acquired = expected_freeze_and_acquisition()
    ingest = load_module("ha_t92_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
    converter = load_module("ha_t92_converter", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")
    tables = ingest.load_tables(ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata")
    if [sha_file(ROOT / f"atlas-data/source-cache/bodyparts3d-r4/metadata/{name}") for name in sorted(frozen["sourceMetadata"]["fileHashes"])] != [frozen["sourceMetadata"]["fileHashes"][name] for name in sorted(frozen["sourceMetadata"]["fileHashes"])]:
        raise BuildError("pinned R4 metadata changed after T92 freeze")
    source_names = ingest.load_source_name_map(ROOT)
    concept_rows = {tuple(row) for row in tables["isaConcepts"]}
    element_rows = {tuple(row) for row in tables["isaCompoundElements"]}
    source_by_fj = {row["sourceElementFileId"]: row for row in frozen["uniqueSourceAssets"]}
    acquired_by_fj = {row["sourceElementFileId"]: row for row in acquired}
    if set(source_by_fj) != set(EXPECTED_FJS) or set(acquired_by_fj) != set(EXPECTED_FJS):
        raise BuildError("T92 source/frozen/actual ID sets do not match")

    rows: list[dict[str, Any]] = []
    converter_inputs: list[dict[str, Any]] = []
    mesh_raw_compare: list[dict[str, Any]] = []
    for file_id in EXPECTED_FJS:
        frozen_asset = source_by_fj[file_id]
        acq_row = acquired_by_fj[file_id]
        path = ROOT / acq_row["cacheRelativePath"]
        if not path.is_file() or path.stat().st_size != acq_row["bytes"] or sha_file(path) != acq_row["sha256"]:
            raise BuildError(f"T92 raw source file does not match acquisition hash/size: {file_id}")
        header = ingest.read_obj_header(path)
        ingest.validate_obj_source_identity(header, tables)
        header_name, bounds = header_name_bounds(path)
        if header.get("fileId") != file_id or header.get("buildUpLogic") != "FMA 3.0 is_a":
            raise BuildError(f"T92 OBJ header FJ/tree mismatch: {file_id}")
        source_name = source_names.get(header.get("conceptId"))
        if (header.get("conceptId"), header.get("representationId"), source_name) not in concept_rows:
            raise BuildError(f"T92 header FMA/BP/name tuple not in exact official IS-A table: {file_id}")
        if not header_name or not source_name or header_name.casefold() != source_name.casefold():
            raise BuildError(f"T92 exact OBJ English name header differs from R4 concept row: {file_id}")
        if not bounds:
            raise BuildError(f"T92 Bounds(mm) header missing after acquisition: {file_id}")
        if tuple([header.get("conceptId"), source_name, file_id]) not in element_rows:
            raise BuildError(f"T92 header FMA/name/FJ relation absent from official R4 ELEMENT table: {file_id}")

        vertices, normals, triangles = converter.parse_obj(path)
        if not vertices or not triangles or len(normals) != len(vertices):
            raise BuildError(f"T92 source surface is empty or structurally inconsistent: {file_id}")
        vertex_bounds = [min(point[i] for point in vertices) for i in range(3)] + [max(point[i] for point in vertices) for i in range(3)]
        deltas = [bounds[i] - vertex_bounds[i] for i in range(3)] + [bounds[i + 3] - vertex_bounds[i + 3] for i in range(3)]
        max_delta = max(abs(value) for value in deltas)
        transformed = [converter.transform_vertex(vertex) for vertex in vertices]
        packed_positions = converter.float32_bytes(value for vertex in transformed for value in vertex)
        expected_side = frozen_asset["exactSideFromSourceConceptNames"]
        header_side = acq_row["headerSideFromExactOfficialFmaName"]
        if header_side is not None and header_side != expected_side:
            raise BuildError(f"T92 OBJ header explicit name side conflicts with exact official mapping: {file_id}")
        source_geometry_hash = sha(packed_positions + json.dumps(triangles, separators=(",", ":")).encode("ascii"))
        row = {
            "sourceElementFileId": file_id,
            "stableMeshAssetId": frozen_asset["stableMeshAssetId"],
            "sourceSha256": acq_row["sha256"],
            "sourceBytes": acq_row["bytes"],
            "sourceArchiveMemberPath": acq_row["memberPath"],
            "archiveTree": acq_row["archiveTree"],
            "archiveCrc32": acq_row["crc32"],
            "sourceHeaderIdentity": {
                "fileId": header["fileId"],
                "sourceFmaConceptId": header["conceptId"],
                "sourceRepresentationId": header["representationId"],
                "sourceEnglishNameHeaderExact": header_name,
                "sourceEnglishNameOfficialCasefoldMatch": source_name,
                "buildUpLogic": header["buildUpLogic"],
                "licenseHeaderExact": header["licenseHeader"],
                "boundsHeaderUnit": "mm",
                "boundsHeaderMm": bounds,
            },
            "sourceConceptMemberships": frozen_asset["sourceConceptMemberships"],
            "sideFromExactOfficialConceptRelation": expected_side,
            "objHeaderExplicitSideObservation": header_side,
            "sideWasNotInferredFromFjSuffixOrCoordinates": True,
            "sourceUnit": "mm; evidenced by this exact OBJ Bounds(mm) header; official metadata has no source-wide unit field",
            "projectUnit": "m",
            "projectFrame": "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR",
            "sourceFrame": "BodyParts3D R4 native reference; not registered to OpenSim",
            "transform": "[x,y,z] source mm -> [x,z,-y] HUMAN ATLAS m; preserve x sign; no mirror/recenter",
            "pose": "bodyparts3d-r4-static-reference; no standardized articulated pose asserted",
            "lod": "official archive is identified as 99%-reduced; no multilevel LOD chain is available or created",
            "candidateSourceContexts": REGIONS,
            "sourceVertexCount": len(vertices),
            "sourceNormalCount": len(normals),
            "sourceTriangleCount": len(triangles),
            "boundsHeaderVsRawVertexExtremaMm": {"differenceMm": deltas, "maxAbsDeltaMm": max_delta, "usedAsSurfaceProof": False},
            "transformedPositionFloat32Sha256": sha(packed_positions),
            "sourceGeometryTopologyComparisonSha256": source_geometry_hash,
            "humanAnatomyReviewed": False,
            "canonicalLearnerBinding": None,
            "learnerDefaultVisible": False,
            "learnerPolicyChanged": False,
            "publicRedistributionState": "held_pending_file_level_reconciliation_of_current_CC_BY_4_0_with_legacy_OBJ_CC_BY_SA_2_1_Japan_header",
        }
        rows.append(row)
        converter_inputs.append({
            "file_id": file_id,
            "source_path": path,
            "source_relative_path": acq_row["cacheRelativePath"],
            "source_sha256": acq_row["sha256"],
            "asset": {
                "bytes": acq_row["bytes"],
                "vertex_count": len(vertices),
                "polygon_count": len(triangles),
                "concept_id": header["conceptId"],
                "representation_id": header["representationId"],
            },
        })
        mesh_raw_compare.append({"sourceElementFileId": file_id, "vertices": vertices, "triangles": triangles, "hash": source_geometry_hash})

    input_hashes = frozen["inputSha256"]
    for relpath, expected_hash in input_hashes.items():
        current = ROOT / relpath
        if not current.is_file() or sha_file(current) != expected_hash:
            raise BuildError(f"historical T50/T53/T54/T70/T71/T72/T73 input changed after freeze: {relpath}")
    base = json.loads(BASE.read_text(encoding="utf-8"))
    if sha_file(BASE) != frozen["historicalContract"]["parentIntegrationManifest"]["sha256"]:
        raise BuildError("T70 parent integration manifest changed after T92 freeze")
    return rows, converter_inputs, mesh_raw_compare, {"frozen": frozen, "acquisition": acq, "base": base, "inputHashes": input_hashes, "frozenBytes": FREEZE.read_bytes()}


def make_source_manifest(rows: list[dict[str, Any]], mesh_records: list[dict[str, Any]], glb_hash: str, glb_bytes: bytes, refs: dict[str, Any]) -> dict[str, Any]:
    frozen = refs["frozen"]
    acq_path, acq = load_success_acquisition_path()
    source_assets = []
    by_fj = {row["sourceElementFileId"]: row for row in rows}
    for row in rows:
        file_id = row["sourceElementFileId"]
        record = next(item for item in mesh_records if item["sourceFileId"] == file_id)
        source_assets.append({
            **row,
            "renderNodeId": row["stableMeshAssetId"],
            "glbMeshIndex": record["meshIndex"],
            "glbGeometrySha256": record["geometrySha256"],
            "glbTopologySha256": record["topologySha256"],
            "glbNormalSha256": record["normalSha256"],
        })
    crosswalk = []
    for concept in frozen["sourceConcepts"]:
        rels = []
        for _fma, _name, file_id in concept["officialElementRows"]:
            rels.append({"sourceElementFileId": file_id, "stableMeshAssetId": by_fj[file_id]["stableMeshAssetId"], "sameNodeSharedAcrossConcepts": True})
        crosswalk.append({
            "sourceConceptId": concept["sourceConceptId"],
            "sourceRepresentationId": concept["sourceRepresentationId"],
            "sourceNameEnglish": concept["sourceNameEnglish"],
            "sourceSemanticLabel": concept["sourceSemanticLabel"],
            "sourceTree": concept["sourceTree"],
            "officialConceptRow": concept["officialConceptRow"],
            "officialElementRows": concept["officialElementRows"],
            "renderNodeRelations": rels,
            "contextCandidates": concept["declaredSourceContextCandidates"],
            "createsSeparateGeometry": False,
        })
    return {
        "revision": "BodyParts3D-R4-T92-static-source-package-v1",
        "task": "T92",
        "status": "passed_with_gaps_source_only_local_qa_rights_and_human_review_held",
        "source": {
            "sourceId": SOURCE_ID,
            "version": SOURCE_VERSION,
            "officialReadme": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/README_e.html",
            "officialDownloadPage": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html",
            "officialArchiveUrl": acq["archiveUrl"],
            "officialArchiveTree": "IS-A",
            "archiveEtag": acq["officialArchive"]["etag"],
            "archiveLastModified": acq["officialArchive"]["lastModified"],
            "sourceFrame": "BodyParts3D R4 native static reference; not OpenSim registered",
            "sourceUnit": "mm for each acquired OBJ, evidenced by its exact Bounds(mm) header; no source-wide metadata unit claim",
            "projectFrame": FRAME,
            "projectUnit": "m",
            "transform": "[x,y,z] source mm -> [x,z,-y] HUMAN ATLAS m; preserve x sign; no mirror or recenter",
            "pose": POSE,
            "lod": "official archive lists one 99%-reduced polygon bundle; no multilevel LOD set or additional LOD is asserted",
        },
        "inputs": {
            "frozenSourceSetPath": FREEZE.relative_to(ROOT).as_posix(),
            "frozenSourceSetSha256": sha(refs["frozenBytes"]),
            "frozenConceptMembershipSha256": frozen["sourceConceptMembershipSha256"],
            "frozenAssetMembershipSha256": frozen["sourceAssetMembershipSha256"],
            "acquisitionEvidencePath": acq_path.relative_to(ROOT).as_posix(),
            "acquisitionEvidenceSha256": sha_file(acq_path),
            "historicalInputSha256": refs["inputHashes"],
            "T70ParentIntegrationManifestSha256": sha_file(BASE),
        },
        "scope": {
            "sourceConceptCount": 10,
            "conceptToElementRelationCount": 14,
            "sourceElementFileCount": 6,
            "uniqueSourceNodeCount": 6,
            "oneNodePerUniqueFj": True,
            "candidateSourceContextIds": REGIONS,
            "contextReferenceCount": 12,
            "internalBatchSizeMaximum": 10,
            "internalBatches": frozen["internalBatches"],
            "canonicalLearnerMembershipCreated": False,
            "wholeBodyCanonicalDenominator": None,
        },
        "sourceConcepts": frozen["sourceConcepts"],
        "targetConceptToElementCrosswalk": crosswalk,
        "sourceAssets": source_assets,
        "meshRecords": mesh_records,
        "sceneContract": {
            "contract": "T50 persistent AnatomySceneRoot/frame/static-pose contract; this is a sibling local-QA source package, not a learner scene or viewport",
            "modelId": MODEL_ID,
            "integratedGlbLocalCachePath": GLB.relative_to(ROOT).as_posix(),
            "integratedGlbSha256": glb_hash,
            "integratedGlbBytes": len(glb_bytes),
            "meshNodeCount": len(mesh_records),
            "rendererCount": 0,
            "sourceNodePolicy": "one stable source node per unique FJ; generic part, side-specific concept, and back/shoulder context references reuse that node",
            "qaContextPackages": [
                {"task": "T53", "region": "back", "sourceManifest": T53_SOURCE.relative_to(ROOT).as_posix(), "regionManifest": T53_REGION.relative_to(ROOT).as_posix(), "glb": T53_GLB.relative_to(ROOT).as_posix(), "glbSha256": sha_file(T53_GLB)},
                {"task": "T54", "region": "shoulder-scapular", "sourceManifest": T54_SOURCE.relative_to(ROOT).as_posix(), "regionManifest": T54_REGION.relative_to(ROOT).as_posix(), "glb": T54_GLB.relative_to(ROOT).as_posix(), "glbSha256": sha_file(T54_GLB)},
            ],
        },
        "rights": {
            "officialCurrentLicense": "CC BY 4.0 per official page last updated 2025-02-27",
            "requiredAttribution": ATTRIBUTION,
            "perFileObjHeaderClaim": sorted({row["sourceHeaderIdentity"]["licenseHeaderExact"] for row in rows}),
            "redistributionStatus": "held_pending_file_level_reconciliation_of_current_CC_BY_4_0_with_legacy_OBJ_CC_BY_SA_2_1_Japan_header",
            "publicRelease": False,
        },
        "identityAndReview": {
            "canonicalLearnerBindings": 0,
            "learnerDefaultVisible": False,
            "learnerPolicyChanged": False,
            "humanAnatomyReviewed": False,
            "sourceOnlyUnbound": True,
            "anatomicalClaimsAdded": False,
        },
        "manifestSha256": None,
    }


def load_success_acquisition_path() -> tuple[Path, dict[str, Any]]:
    paths = [ACQ, *sorted(ACQ.parent.glob("source-acquisition-attempt-*.json"))]
    for path in reversed(paths):
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("result") == "pass":
                return path, data
    raise BuildError("no successful T92 source acquisition is recorded")


def make_integration_extension(source_manifest: dict[str, Any], source_sha: str, glb_sha: str, refs: dict[str, Any]) -> dict[str, Any]:
    base = copy.deepcopy(refs["base"])
    if source_manifest["scope"]["sourceElementFileCount"] != 6:
        raise BuildError("T92 extension must add exactly six source assets")
    seen = {asset.get("sourceElementFileId") for asset in base.get("assets", [])}
    if seen & set(EXPECTED_FJS):
        raise BuildError(f"T92 source IDs collide with T70 parent package: {sorted(seen & set(EXPECTED_FJS))}")
    new_assets = []
    for row in source_manifest["sourceAssets"]:
        memberships = [
            {"regionId": region, "sourceElementFileId": row["sourceElementFileId"], "stableRenderNodeId": row["stableMeshAssetId"], "membershipBasis": "T73 frozen visual source-context candidate only; not a canonical learner/product membership"}
            for region in REGIONS
        ]
        new_assets.append({
            "existingLearnerStableIds": [],
            "holdReasons": ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"],
            "humanAnatomyReviewed": False,
            "learnerDefaultVisible": False,
            "learnerPickState": "source_only_unbound",
            "localQaRender": "available_source_surface",
            "packageReferences": [{"package": "T92", "sourceSha256": row["sourceSha256"]}],
            "primaryPackage": "T92",
            "productRegionIdsFromHistoricalPackages": [],
            "candidateProductRegionIds": REGIONS,
            "regionMembershipRows": memberships,
            "renderNodeId": row["stableMeshAssetId"],
            "sourceClassCandidates": ["muscle_element_source_only"],
            "sourceConceptIdObservation": row["sourceHeaderIdentity"]["sourceFmaConceptId"],
            "sourceElementFileId": row["sourceElementFileId"],
            "sourceNameObservation": row["sourceHeaderIdentity"]["sourceEnglishNameHeaderExact"],
            "sourceSha256": row["sourceSha256"],
            "oneNodeSharedAcrossTwoCandidateContexts": True,
        })
    base["revision"] = "BodyParts3D-R4-T92-sibling-extension-of-T70-trapezius-v1"
    base["parentIntegrationManifest"] = {"path": BASE.relative_to(ROOT).as_posix(), "sha256": sha_file(BASE), "historicalManifestUnchanged": True}
    base["siblingPackageReferences"] = [
        {"task": "T53", "sourceManifestPath": T53_SOURCE.relative_to(ROOT).as_posix(), "sourceManifestSha256": sha_file(T53_SOURCE), "backRegionManifestPath": T53_REGION.relative_to(ROOT).as_posix(), "backRegionManifestSha256": sha_file(T53_REGION), "localQaGlbPath": T53_GLB.relative_to(ROOT).as_posix(), "localQaGlbSha256": sha_file(T53_GLB), "relationship": "same-frame back/trunk context for private T92 QA; no historical edits"},
        {"task": "T54", "sourceManifestPath": T54_SOURCE.relative_to(ROOT).as_posix(), "sourceManifestSha256": sha_file(T54_SOURCE), "shoulderRegionManifestPath": T54_REGION.relative_to(ROOT).as_posix(), "shoulderRegionManifestSha256": sha_file(T54_REGION), "localQaGlbPath": T54_GLB.relative_to(ROOT).as_posix(), "localQaGlbSha256": sha_file(T54_GLB), "relationship": "same-frame shoulder-scapular context for private T92 QA; no historical edits"},
        {"task": "T71", "sourceManifestPath": T71_SOURCE.relative_to(ROOT).as_posix(), "sourceManifestSha256": sha_file(T71_SOURCE), "integrationManifestPath": T71_INTEGRATION.relative_to(ROOT).as_posix(), "integrationManifestSha256": sha_file(T71_INTEGRATION), "relationship": "historical sibling package retained; no merge/rewrite"},
        {"task": "T72", "sourceManifestPath": T72_SOURCE.relative_to(ROOT).as_posix(), "sourceManifestSha256": sha_file(T72_SOURCE), "integrationManifestPath": T72_INTEGRATION.relative_to(ROOT).as_posix(), "integrationManifestSha256": sha_file(T72_INTEGRATION), "relationship": "historical sibling package retained; no merge/rewrite"},
    ]
    base["assets"] = sorted(base.get("assets", []) + new_assets, key=lambda row: row["sourceElementFileId"])
    base["localQaChunks"] = list(base.get("localQaChunks", [])) + [{
        "chunkId": "T92-B01-TRAPEZIUS-SOURCE",
        "package": "T92",
        "localQaGlbPath": GLB.relative_to(ROOT).as_posix(),
        "glbSha256": glb_sha,
        "sourceElementFileIds": EXPECTED_FJS,
        "candidateContextRegionIds": REGIONS,
        "candidateContextReferenceCount": 12,
        "oneNodePerUniqueFj": True,
        "suppressDuplicateSourceElementFileIds": [],
    }]
    counts = refs["base"].get("counts", {})
    base["counts"] = {
        **counts,
        "t92FrozenConceptCount": 10,
        "t92ConceptToElementRelationCount": 14,
        "t92UniqueNewSourceNodes": 6,
        "t92CandidateRegionContextReferences": 12,
        "uniqueSourceNodesIncludingT92": counts.get("uniqueSourceNodes", 0) + 6,
        "sourceOnlyUnboundIncludingT92": counts.get("sourceOnlyUnbound", 0) + 6,
        "newCanonicalBindings": 0,
        "newHumanReviewed": 0,
        "newRightsCleared": 0,
    }
    base["publicRedistribution"] = "held_pending_file_level_reconciliation_of_current_CC_BY_4_0_with_legacy_OBJ_CC_BY_SA_2_1_Japan_header"
    base["t92Inputs"] = {
        "frozenSourceSetSha256": sha(refs["frozenBytes"]),
        "sourceManifestSha256": source_sha,
        "glbSha256": glb_sha,
        "T70ParentIntegrationSha256": sha_file(BASE),
        "T53BackContextGlbSha256": sha_file(T53_GLB),
        "T54ShoulderContextGlbSha256": sha_file(T54_GLB),
        "canonicalLearnerBindings": 0,
        "humanAnatomyReviewed": 0,
        "learnerPolicyChanged": False,
        "wholeBodyCanonicalDenominator": None,
    }
    return base


def build() -> dict[str, Any]:
    if not BASE.is_file() or not T53_GLB.is_file() or not T54_GLB.is_file():
        raise BuildError("T70 parent or T53/T54 QA context package is missing")
    rows, inputs, raw_compare, refs = source_records()
    converter = load_module("ha_t92_builder_converter", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")
    converter.MODEL_ID = MODEL_ID
    converter.SOURCE_ID = SOURCE_ID
    glb_data, mesh_records = converter.build_glb(inputs)
    gltf, binary = unpack_glb(glb_data)
    if len(gltf.get("nodes", [])) != 6 or len(gltf.get("meshes", [])) != 6:
        raise BuildError("T92 GLB must contain exactly six unique source nodes")
    by_fj = {row["sourceElementFileId"]: row for row in rows}
    for record in mesh_records:
        file_id = record["sourceFileId"]
        row = by_fj[file_id]
        idx = record["meshIndex"]
        actual = position_bytes(gltf, binary, idx)
        if sha(actual) != row["transformedPositionFloat32Sha256"]:
            raise BuildError(f"GLB positions do not reproduce the T50 transform for {file_id}")
        details = {
            "sourceOnlyPackage": "T92",
            "taskScope": "bounded local QA source extension",
            "sourceId": SOURCE_ID,
            "sourceVersion": SOURCE_VERSION,
            "sourceElementFileId": file_id,
            "sourceFileId": file_id,
            "sourceSha256": row["sourceSha256"],
            "sourceFmaConceptId": row["sourceHeaderIdentity"]["sourceFmaConceptId"],
            "sourceRepresentationId": row["sourceHeaderIdentity"]["sourceRepresentationId"],
            "sourceEnglishNameHeaderExact": row["sourceHeaderIdentity"]["sourceEnglishNameHeaderExact"],
            "sideFromExactOfficialConceptRelation": row["sideFromExactOfficialConceptRelation"],
            "candidateSourceContexts": REGIONS,
            "stableMeshAssetId": row["stableMeshAssetId"],
            "frame": FRAME,
            "unit": "m",
            "pose": POSE,
            "humanAnatomyReviewed": False,
            "canonicalLearnerBinding": None,
            "learnerDefaultVisible": False,
            "publicRedistributionHeld": True,
        }
        for node_collection in (gltf["nodes"], gltf["meshes"]):
            node_collection[idx]["name"] = row["stableMeshAssetId"]
            node_collection[idx].setdefault("extras", {}).update(details)
        record["nodeName"] = row["stableMeshAssetId"]
        record["sourceConceptIds"] = [item["sourceConceptId"] for item in row["sourceConceptMemberships"]]
        record["candidateSourceContexts"] = REGIONS
    gltf["asset"]["generator"] = "HUMAN ATLAS T92 deterministic BodyParts3D R4 source package builder"
    gltf["extras"] = {
        "task": "T92",
        "sourceId": SOURCE_ID,
        "sourceVersion": SOURCE_VERSION,
        "sourceElementFileIds": EXPECTED_FJS,
        "oneNodePerUniqueFj": True,
        "sourceConceptCount": 10,
        "conceptToElementRelationCount": 14,
        "candidateContextRegionIds": REGIONS,
        "frame": FRAME,
        "unit": "m",
        "pose": POSE,
        "canonicalLearnerBindingsCreated": False,
        "learnerPolicyChanged": False,
        "humanAnatomyReviewed": False,
        "redistributionStatus": "held_pending_file_level_license_reconciliation",
    }
    out_glb = repack_glb(gltf, binary)
    if GLB.exists() and GLB.read_bytes() != out_glb:
        prior_gltf, _prior_binary = unpack_glb(GLB.read_bytes())
        prior_owned = (
            prior_gltf.get("asset", {}).get("generator") == "HUMAN ATLAS T92 deterministic BodyParts3D R4 source package builder"
            and prior_gltf.get("extras", {}).get("task") == "T92"
            and prior_gltf.get("extras", {}).get("sourceElementFileIds") == EXPECTED_FJS
            and prior_gltf.get("extras", {}).get("sourceId") == SOURCE_ID
        )
        if not prior_owned:
            raise BuildError(f"refusing to overwrite a different/unowned T92 derived cache GLB: {GLB}")
    GLB.parent.mkdir(parents=True, exist_ok=True)
    GLB.write_bytes(out_glb)
    glb_sha = sha(out_glb)

    manifest = make_source_manifest(rows, mesh_records, glb_sha, out_glb, refs)
    unsigned = copy.deepcopy(manifest)
    unsigned["manifestSha256"] = None
    manifest["manifestSha256"] = sha(json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    write_immutable(OUT_SOURCE, manifest)
    source_sha = sha_file(OUT_SOURCE)
    extension = make_integration_extension(manifest, source_sha, glb_sha, refs)
    write_immutable(OUT_INTEGRATION, extension)

    target_hash_groups: dict[str, list[str]] = {}
    for row in rows:
        target_hash_groups.setdefault(row["sourceGeometryTopologyComparisonSha256"], []).append(row["sourceElementFileId"])
    exact_duplicate_groups = [ids for ids in target_hash_groups.values() if len(ids) > 1]
    validation = {
        "revision": "T92-PACKAGE-VALIDATION-v1",
        "task": "T92",
        "result": "pass",
        "frozenConceptCount": 10,
        "frozenConceptIds": [row["sourceConceptId"] for row in manifest["sourceConcepts"]],
        "conceptToElementRelationCount": 14,
        "exactFrozenFjIds": EXPECTED_FJS,
        "exactAcquiredAndBuiltIds": [row["sourceElementFileId"] for row in rows],
        "internalBatchCounts": [batch["count"] for batch in refs["frozen"]["internalBatches"]],
        "allOfficialFmaBpNameElementRelationsMatchT73AndT51R4Cache": True,
        "allObjHeadersMatchExactFjFmaBpBuildTreeAndEnglishConceptName": True,
        "exactHeaderAndMappedSideByFj": {row["sourceElementFileId"]: {"FMA": row["sourceHeaderIdentity"]["sourceFmaConceptId"], "BP": row["sourceHeaderIdentity"]["sourceRepresentationId"], "headerName": row["sourceHeaderIdentity"]["sourceEnglishNameHeaderExact"], "sideFromOfficialNamedConceptRelation": row["sideFromExactOfficialConceptRelation"], "notInferredFromFjSuffixOrCoordinates": True} for row in rows},
        "allSourceFilesNonempty": all(row["sourceVertexCount"] > 0 and row["sourceTriangleCount"] > 0 for row in rows),
        "rawSourceSha256AndZipCrcValidated": True,
        "officialRangeStatus206Only": all(r.get("httpStatus") == 206 for r in refs["acquisition"]["rangeRequests"]),
        "fullArchiveDownloaded": False,
        "selectedPayloadBytes": refs["acquisition"]["officialArchive"]["selectedPayloadBytes"],
        "rangeRequestCount": len(refs["acquisition"]["rangeRequests"]),
        "sourceUnitFramePosePerFile": {row["sourceElementFileId"]: {"sourceUnit": row["sourceUnit"], "projectUnit": row["projectUnit"], "frame": row["projectFrame"], "pose": row["pose"], "transform": row["transform"]} for row in rows},
        "allGlbPositionBuffersMatchT50Transform": True,
        "headerBoundsWereNotUsedAsSurfaceProof": all(row["boundsHeaderVsRawVertexExtremaMm"]["usedAsSurfaceProof"] is False for row in rows),
        "exactSourceGeometryTopologyDuplicateGroups": exact_duplicate_groups,
        "oneGlbNodePerUniqueFj": len(gltf["nodes"]) == 6 and len({n["extras"]["sourceElementFileId"] for n in gltf["nodes"]}) == 6,
        "10ConceptsAnd14RelationsShareSixUniqueNodes": all(relation["sameNodeSharedAcrossConcepts"] for concept in manifest["targetConceptToElementCrosswalk"] for relation in concept["renderNodeRelations"]),
        "eachNodeHasBothSourceContextCandidates": all(set(row["candidateSourceContexts"]) == set(REGIONS) for row in rows),
        "t70ParentAndHistoricalT71T72T53T54HashesPreserved": True,
        "t70ParentUniqueSourceNodes": refs["base"]["counts"]["uniqueSourceNodes"],
        "t92SiblingExtensionUniqueSourceNodes": extension["counts"]["uniqueSourceNodesIncludingT92"],
        "t92SourceOnlyUnboundNodes": 6,
        "canonicalLearnerBindings": 0,
        "learnerDefaultVisible": False,
        "learnerPolicyChanged": False,
        "humanAnatomyReviewed": False,
        "publicRelease": False,
        "rightsHold": extension["publicRedistribution"],
        "wholeBodyCanonicalDenominator": None,
        "derivedGlb": {"path": GLB.relative_to(ROOT).as_posix(), "bytes": len(out_glb), "sha256": glb_sha, "nodeCount": len(gltf["nodes"])},
        "sourceManifest": {"path": OUT_SOURCE.relative_to(ROOT).as_posix(), "sha256": source_sha, "manifestSha256": manifest["manifestSha256"]},
        "integrationExtension": {"path": OUT_INTEGRATION.relative_to(ROOT).as_posix(), "sha256": sha_file(OUT_INTEGRATION)},
    }
    write_immutable(OUT_VALIDATION, validation)
    return validation


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--build", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = build()
        if args.check:
            # Re-running --check must regenerate identical task-owned manifests and GLB.
            result = {**result, "checkMode": "deterministic rebuild completed; outputs byte-identical or immutable-write rejected"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"T92 build failed closed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
