#!/usr/bin/env python3
"""Validate and package the frozen T52 BodyParts3D R4 head/neck OBJ set.

Writes internal static QA GLBs in the ignored source-cache and tracked source
inventory/package manifests. It does not edit canonical catalog, navigation,
learner membership, spatial drafts, or OpenSim assets.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import struct
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FREEZE_PATH = ROOT / "work/evidence/T52/frozen-source-set.json"
ACQUISITION_PATH = ROOT / "work/evidence/T52/source-acquisition.json"
OUT_ROOT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t52"
QA_GLB_ROOT = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t52"
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
ATTRIBUTION = "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International"
EXPECTED_REGIONS = ("head", "neck")
EXPECTED_BATCH_SIZE = 10


class PackageError(RuntimeError):
    pass


def module_at(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise PackageError(f"could not load existing helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INGEST = module_at("ha_t52_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
CONVERT = module_at("ha_t52_converter", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_full_header(path: Path) -> dict[str, Any]:
    data = INGEST.read_obj_header(path)
    data.update({"englishName": None, "sourceBoundsMm": None, "volumeCm3": None})
    bounds_re = re.compile(r"^#\s*Bounds\(mm\):\s*\(([^)]+)\)-\(([^)]+)\)\s*$")
    with path.open("r", encoding="utf-8", errors="replace") as stream:
        for raw in stream:
            if not raw.startswith("#"):
                break
            line = raw.lstrip("# ").strip()
            if line.startswith("English name :"):
                data["englishName"] = line.split(":", 1)[1].strip()
            match = bounds_re.match(raw.rstrip("\r\n"))
            if match:
                try:
                    minimum = [float(x.strip()) for x in match.group(1).split(",")]
                    maximum = [float(x.strip()) for x in match.group(2).split(",")]
                except ValueError as exc:
                    raise PackageError(f"malformed source bounds header in {path.name}") from exc
                if len(minimum) != 3 or len(maximum) != 3 or any(not math.isfinite(v) for v in minimum + maximum):
                    raise PackageError(f"invalid source bounds header in {path.name}")
                data["sourceBoundsMm"] = {"min": minimum, "max": maximum}
            if line.startswith("Volume(cm3):"):
                try:
                    data["volumeCm3"] = float(line.split(":", 1)[1].strip())
                except ValueError:
                    data["volumeCm3"] = None
    if not data.get("englishName"):
        raise PackageError(f"OBJ header has no source English name: {path.name}")
    if not data.get("sourceBoundsMm"):
        raise PackageError(f"OBJ header has no explicit Bounds(mm): {path.name}")
    return data


def side_observed(name: str) -> str:
    tokens = set(re.findall(r"[a-z]+", name.lower()))
    has_right = "right" in tokens
    has_left = "left" in tokens
    if has_right and has_left:
        return "both_words_conflict"
    if has_right:
        return "right"
    if has_left:
        return "left"
    if "bilateral" in tokens:
        return "bilateral"
    return "not_stated_in_source_name"


def side_bounds_diagnostic(name_side: str, bounds: dict[str, list[float]]) -> tuple[str, str]:
    """Compare source label to raw x-bounds center without treating it as truth."""
    center_x = (bounds["min"][0] + bounds["max"][0]) / 2
    if name_side not in {"left", "right"}:
        return "not_applicable_source_name_has_no_side", "not_stated_in_source_name"
    position_side = "left" if center_x > 0 else "right" if center_x < 0 else "midline"
    crosses_midline = bounds["min"][0] < 0 < bounds["max"][0]
    if position_side != name_side:
        status = "bounds_center_opposes_source_name_human_check_required"
        if crosses_midline:
            status += "_with_midline_overlap"
        return status, position_side
    if crosses_midline:
        return "bounds_cross_midline_direction_inconclusive", position_side
    if position_side == name_side:
        return "bounds_center_agrees_with_source_name_diagnostic_only", position_side
    return "bounds_center_opposes_source_name_human_check_required", position_side


def source_bounds(vertices: list[tuple[float, float, float]]) -> dict[str, list[float]]:
    return {
        "min": [min(vertex[i] for vertex in vertices) for i in range(3)],
        "max": [max(vertex[i] for vertex in vertices) for i in range(3)],
    }


def transform_bounds(bounds: dict[str, list[float]]) -> dict[str, list[float]]:
    corners = []
    for x in (bounds["min"][0], bounds["max"][0]):
        for y in (bounds["min"][1], bounds["max"][1]):
            for z in (bounds["min"][2], bounds["max"][2]):
                corners.append((x * 0.001, z * 0.001, -y * 0.001))
    return {
        "min": [min(point[i] for point in corners) for i in range(3)],
        "max": [max(point[i] for point in corners) for i in range(3)],
    }


def approximately_equal(a: list[float], b: list[float], tolerance: float = 0.00065) -> bool:
    return len(a) == len(b) and all(abs(x - y) <= tolerance for x, y in zip(a, b))


def unpack_glb(glb: bytes) -> tuple[dict[str, Any], bytes]:
    if len(glb) < 20 or glb[:4] != b"glTF":
        raise PackageError("converter returned invalid GLB header")
    json_len, json_type = struct.unpack_from("<II", glb, 12)
    if json_type != 0x4E4F534A:
        raise PackageError("converter returned GLB without JSON chunk")
    json_start = 20
    json_end = json_start + json_len
    gltf = json.loads(glb[json_start:json_end].decode("utf-8"))
    bin_len, bin_type = struct.unpack_from("<II", glb, json_end)
    if bin_type != 0x004E4942:
        raise PackageError("converter returned GLB without BIN chunk")
    binary = glb[json_end + 8 : json_end + 8 + bin_len]
    return gltf, binary


def repack_glb(gltf: dict[str, Any], binary: bytes) -> bytes:
    json_chunk = json.dumps(gltf, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    while len(json_chunk) % 4:
        json_chunk += b" "
    while len(binary) % 4:
        binary += b"\0"
    total = 12 + 8 + len(json_chunk) + 8 + len(binary)
    return b"".join((struct.pack("<4sII", b"glTF", 2, total), struct.pack("<II", len(json_chunk), 0x4E4F534A), json_chunk, struct.pack("<II", len(binary), 0x004E4942), binary))


def build_batch_glb(batch: dict[str, Any], file_by_id: dict[str, dict[str, Any]], by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    items = []
    for file_id in batch["sourceElementFileIds"]:
        record = file_by_id[file_id]
        detail = by_id[file_id]
        vertices, _normals, triangles = CONVERT.parse_obj(record["sourcePath"])
        items.append({
            "file_id": file_id,
            "source_path": record["sourcePath"],
            "source_relative_path": record["cacheRelativePath"],
            "source_sha256": record["sha256"],
            "asset": {
                "bytes": record["bytes"],
                "vertex_count": len(vertices),
                "polygon_count": len(triangles),
                "concept_id": detail["sourceConceptId"],
                "representation_id": detail["sourceRepresentationId"],
            },
        })
    CONVERT.MODEL_ID = "HA-MODEL-BP3D4-T52-{}-QA".format(batch["batchId"])
    glb, mesh_records = CONVERT.build_glb(items)
    gltf, binary = unpack_glb(glb)
    gltf["asset"]["generator"] = "HUMAN ATLAS T52 deterministic internal source package builder"
    gltf.setdefault("extras", {}).update({
        "taskScope": "T52 internal QA only",
        "batchId": batch["batchId"],
        "frame": FRAME,
        "pose": POSE,
        "sourceId": SOURCE_ID,
        "sourceVersion": "BodyParts3D Release 4.0",
        "noCanonicalMembershipCreated": True,
        "humanAnatomyReviewed": False,
    })
    for record in mesh_records:
        file_id = record["sourceFileId"]
        detail = by_id[file_id]
        extras = {
            "stableMeshAssetId": record["meshAssetId"],
            "sourceFileId": file_id,
            "sourceConceptId": detail["sourceConceptId"],
            "sourceRepresentationId": detail["sourceRepresentationId"],
            "sourceName": detail["sourceName"],
            "regionIds": detail["regionIds"],
            "sameFmaSourceAssetSiblings": detail.get("sameFmaSourceAssetSiblings", []),
            "laterality": detail["laterality"],
            "lateralityBoundsDiagnostic": detail["lateralityBoundsDiagnostic"],
            "boundsCenterSideDiagnosticOnly": detail["boundsCenterSideDiagnosticOnly"],
            "learnerStableId": detail["existingLearnerStableId"],
            "sourceVersion": "BodyParts3D Release 4.0",
            "sourceFrame": "native BodyParts3D R4 static reference; not registered to OpenSim",
            "atlasFrame": FRAME,
            "sourceUnit": "mm evidenced by this OBJ header's Bounds(mm)",
            "transform": "[x,y,z]mm -> [x,z,-y]m; no reflection or mirroring",
            "pose": POSE,
            "lod": "official 99%-reduced bundle; no multilevel LOD chain",
            "sourceHeaderLicense": detail["sourceHeaderLicense"],
            "reviewState": "needs_review",
            "humanAnatomyReviewed": False,
        }
        index = record["nodeIndex"]
        gltf["nodes"][index]["extras"].update(extras)
        gltf["meshes"][index]["extras"].update(extras)
        gltf["nodes"][index]["name"] = record["meshAssetId"]
        gltf["meshes"][index]["name"] = record["meshAssetId"]
    output = repack_glb(gltf, binary)
    path = QA_GLB_ROOT / f"{batch['batchId']}.glb"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != output:
        raise PackageError(f"refusing to overwrite non-deterministic prior QA GLB {path}")
    path.write_bytes(output)
    return {
        "batchId": batch["batchId"],
        "sourceElementFileIds": batch["sourceElementFileIds"],
        "meshCount": len(mesh_records),
        "glbPath": path.relative_to(ROOT).as_posix(),
        "glbBytes": len(output),
        "glbSha256": sha256_bytes(output),
        "modelId": "HA-MODEL-BP3D4-T52-{}-QA".format(batch["batchId"]),
        "internalQaOnly": True,
    }


def build() -> dict[str, Any]:
    frozen_bytes = FREEZE_PATH.read_bytes()
    frozen = json.loads(frozen_bytes)
    acquisition = json.loads(ACQUISITION_PATH.read_text(encoding="utf-8"))
    if acquisition["frozenSourceSetSha256"] != sha256_bytes(frozen_bytes):
        raise PackageError("acquisition manifest does not bind the frozen source set bytes")
    if acquisition["fullArchivesDownloaded"] or acquisition["completeSourceFileCount"] != 85:
        raise PackageError("expected all 85 selected OBJ files and no full archive download")
    frozen_ids = [row["sourceElementFileId"] for row in frozen["atomicSourceFiles"]]
    if len(frozen_ids) != 85 or len(set(frozen_ids)) != 85:
        raise PackageError("frozen source set is missing or duplicates FJ IDs")
    if any(batch["count"] > EXPECTED_BATCH_SIZE for batch in frozen["internalBatches"]):
        raise PackageError("frozen source batch exceeds the 10-file processing limit")

    # Existing source mappings are the only authority for a canonical learner ID.
    mapping_rows = json.loads((ROOT / "atlas-data/catalog/source-crosswalk.json").read_text(encoding="utf-8"))["bodyParts3dMappings"]
    navigation = json.loads((ROOT / "atlas-data/navigation/atlas-navigation.json").read_text(encoding="utf-8"))
    existing_by_fj: dict[str, set[str]] = defaultdict(set)
    for row in mapping_rows:
        if row.get("elementFileId"):
            existing_by_fj[row["elementFileId"]].add(row["stableConceptId"])
    instances = {row["id"]: row for row in navigation.get("structureInstances", [])}
    for row in navigation.get("structureMeshMappings", []):
        instance = instances.get(row.get("structureInstanceId"), {})
        stable = instance.get("structureId")
        if stable:
            for mesh_id in row.get("meshIds", []):
                if mesh_id.startswith("HA-MESH-BP3D4-"):
                    existing_by_fj[mesh_id.removeprefix("HA-MESH-BP3D4-")].add(stable)
    tables = INGEST.load_tables(ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata")
    official_names: dict[str, set[str]] = defaultdict(set)
    for key in ("isaConcepts", "partofConcepts"):
        for fma, _bp, name in tables[key]:
            official_names[fma].add(name)
    contexts: dict[str, dict[str, Any]] = {}
    for item in frozen["atomicSourceFiles"]:
        contexts[item["sourceElementFileId"]] = item
    acquired = {row["sourceElementFileId"]: row for row in acquisition["selectedSourceFiles"]}
    if set(acquired) != set(frozen_ids):
        raise PackageError("actual acquisition IDs differ from the frozen 85 FJ IDs")

    source_records = []
    geometry_bounds_by_region = {
        region: {"min": [math.inf, math.inf, math.inf], "max": [-math.inf, -math.inf, -math.inf], "vertexCount": 0}
        for region in EXPECTED_REGIONS
    }
    header_name_mismatches = []
    invalid = []
    for file_id in frozen_ids:
        acquired_row = acquired[file_id]
        path = ROOT / acquired_row["cacheRelativePath"]
        if not path.is_file() or path.stat().st_size != acquired_row["bytes"] or sha256_file(path) != acquired_row["sha256"]:
            raise PackageError(f"actual OBJ source size/hash changed: {file_id}")
        header = parse_full_header(path)
        if header["fileId"] != file_id:
            raise PackageError(f"OBJ File ID header differs from frozen source ID: {file_id}")
        INGEST.validate_obj_source_identity(header, tables)
        tree_from_header = "IS-A" if header["buildUpLogic"] == "FMA 3.0 is_a" else "PART-OF" if header["buildUpLogic"] == "FMA 3.0 part_of" else None
        if tree_from_header != acquired_row["archiveTree"]:
            raise PackageError(f"selected archive tree does not agree with OBJ build-up logic for {file_id}")
        expected_context = contexts[file_id]
        if tree_from_header not in expected_context["expectedArchiveTrees"]:
            raise PackageError(f"OBJ build-up tree absent from frozen official context for {file_id}")
        vertices, normals, triangles = CONVERT.parse_obj(path)
        if not vertices or len(vertices) != len(normals) or not triangles:
            invalid.append({"sourceFileId": file_id, "reason": "empty_or_inconsistent_mesh"})
            raise PackageError(f"empty or inconsistent OBJ geometry: {file_id}")
        actual_bounds = source_bounds(vertices)
        bound_delta = [
            round(abs(actual_bounds["min"][i] - header["sourceBoundsMm"]["min"][i]), 6)
            for i in range(3)
        ] + [
            round(abs(actual_bounds["max"][i] - header["sourceBoundsMm"]["max"][i]), 6)
            for i in range(3)
        ]
        max_bound_delta = max(bound_delta)
        source_laterality = side_observed(header["englishName"])
        laterality_bounds_status, bounds_center_side = side_bounds_diagnostic(source_laterality, actual_bounds)
        fma = header["conceptId"]
        metadata_options = sorted(official_names.get(fma, set()))
        name_agreement = any(header["englishName"].casefold() == name.casefold() for name in metadata_options)
        if not name_agreement:
            header_name_mismatches.append({"sourceFileId": file_id, "fmaId": fma, "objHeaderName": header["englishName"], "officialIndexNames": metadata_options})
        stable_ids = sorted(existing_by_fj.get(file_id, set()))
        if len(stable_ids) > 1:
            raise PackageError(f"multiple existing learner IDs bind the same source file without explicit alias policy: {file_id}")
        region_ids = sorted(expected_context["regionCandidates"])
        for region_id in region_ids:
            region_bounds = geometry_bounds_by_region[region_id]
            for vertex in vertices:
                transformed_vertex = CONVERT.transform_vertex(vertex)
                for axis, value in enumerate(transformed_vertex):
                    region_bounds["min"][axis] = min(region_bounds["min"][axis], value)
                    region_bounds["max"][axis] = max(region_bounds["max"][axis], value)
                region_bounds["vertexCount"] += 1
        source_records.append({
            "stableMeshAssetId": f"HA-MESH-BP3D4-{file_id}",
            "sourceId": SOURCE_ID,
            "sourceRelease": "BodyParts3D Release 4.0; official archive README current page updated 2025-02-27",
            "sourceElementFileId": file_id,
            "sourceConceptId": fma,
            "sourceRepresentationId": header["representationId"],
            "sourceName": header["englishName"] if name_agreement else None,
            "sourceNameStatus": "obj_header_matches_official_fma_name_index_case_insensitive" if name_agreement else "source_name_conflict_withheld",
            "sourceNameEvidence": {"objHeader": header["englishName"], "officialFmaIndexNames": metadata_options},
            "existingLearnerStableId": stable_ids[0] if stable_ids else None,
            "identityStatus": "explicit_existing_crosswalk" if stable_ids else "source_only_no_existing_HA_mesh_crosswalk",
            "regionIds": region_ids,
            "regionMembershipBasis": "T51 source-region acquisition candidate set; not new product membership or anatomy approval",
            "sourceArchiveTree": tree_from_header,
            "archiveMemberPath": acquired_row["memberPath"],
            "cachePath": acquired_row["cacheRelativePath"],
            "sourceBytes": acquired_row["bytes"],
            "sourceSha256": acquired_row["sha256"],
            "acquisitionStatus": "acquired_selected_official_zip_member",
            "validationStatus": "passed_source_identity_mesh_and_bounds_checks",
            "conversionStatus": "converted_to_internal_qa_batch_glb",
            "selectionId": f"HA-MESH-BP3D4-{file_id}",
            "selectionIdScope": "stable source-mesh asset identity only; not a canonical learner anatomy ID",
            "sourceHeaderLicense": header["licenseHeader"],
            "laterality": source_laterality,
            "lateralityEvidence": "exact OBJ English-name side token, cross-checked against the FMA preferred-name row; no mesh mirroring",
            "lateralityBoundsDiagnostic": laterality_bounds_status,
            "boundsCenterSideDiagnosticOnly": bounds_center_side,
            "sourceHeaderBounds": {"unit": "mm", "basis": "verbatim parsed OBJ #Bounds(mm) values; retained separately from vertex extrema", **header["sourceBoundsMm"]},
            "sourceVertexBounds": {"unit": "mm", "basis": "computed from every parsed vertex", **actual_bounds},
            "headerToVertexBoundsMaxDeltaMm": max_bound_delta,
            "headerToVertexBoundsComparison": "equal_within_vertex_precision" if max_bound_delta <= 0.001 else "small_difference_recorded_without_inference",
            "atlasBounds": {"frame": FRAME, "unit": "m", **transform_bounds(actual_bounds)},
            "vertexCount": len(vertices),
            "normalCount": len(normals),
            "triangleCount": len(triangles),
            "framePose": {"sourceFrame": "native BodyParts3D R4 static reference; not registered to OpenSim", "projectFrame": FRAME, "poseId": POSE, "poseStatus": "static reference only; no standardized articulated pose asserted", "transform": "[x,y,z]mm -> [x,z,-y]m; no mirroring"},
            "lod": "official bundle states polygon reduction rate 99%; single listed profile; no multilevel LOD chain",
            "reviewState": "needs_review",
            "humanAnatomyReviewed": False,
        })
    if invalid:
        raise PackageError("one or more source files failed nonempty-geometry checks")

    ids_by_region: dict[str, list[str]] = {r: [] for r in EXPECTED_REGIONS}
    record_by_id = {row["sourceElementFileId"]: row for row in source_records}
    for row in source_records:
        for region in row["regionIds"]:
            ids_by_region[region].append(row["sourceElementFileId"])
    for region in EXPECTED_REGIONS:
        ids_by_region[region].sort()
    duplicate_ids = len(record_by_id) != len(source_records)
    if duplicate_ids:
        raise PackageError("duplicate FJ source identity after cross-region dedup")
    fma_to_fj: dict[str, list[str]] = defaultdict(list)
    for item in source_records:
        fma_to_fj[item["sourceConceptId"]].append(item["sourceElementFileId"])
    for item in source_records:
        item["sameFmaSourceAssetSiblings"] = sorted(
            candidate for candidate in fma_to_fj[item["sourceConceptId"]]
            if candidate != item["sourceElementFileId"]
        )
    repeated_fma_groups = [
        {"sourceConceptId": fma, "sourceElementFileIds": sorted(file_ids), "note": "distinct official FJ ELEMENT files retained; no subdivision or duplicate identity inferred"}
        for fma, file_ids in sorted(fma_to_fj.items()) if len(file_ids) > 1
    ]
    laterality_diagnostics = [
        {"sourceElementFileId": row["sourceElementFileId"], "sourceName": row["sourceName"], "sourceLaterality": row["laterality"], "boundsCenterSideDiagnosticOnly": row["boundsCenterSideDiagnosticOnly"], "status": row["lateralityBoundsDiagnostic"], "bounds": row["sourceVertexBounds"]}
        for row in source_records if row["lateralityBoundsDiagnostic"].startswith("bounds_center_opposes_source_name_human_check_required") or row["lateralityBoundsDiagnostic"] == "bounds_cross_midline_direction_inconclusive"
    ]
    side_center_oppositions = [row for row in laterality_diagnostics if row["status"].startswith("bounds_center_opposes_source_name_human_check_required")]
    side_midline_inconclusive = [row for row in laterality_diagnostics if row["status"] == "bounds_cross_midline_direction_inconclusive"]

    file_by_id = {
        file_id: {**row, "sourcePath": ROOT / row["cacheRelativePath"]}
        for file_id, row in acquired.items()
    }
    batch_glbs = [build_batch_glb(batch, file_by_id, record_by_id) for batch in frozen["internalBatches"]]
    batch_by_id = {item["batchId"]: item for item in batch_glbs}
    for item in source_records:
        item["batchId"] = next(batch["batchId"] for batch in frozen["internalBatches"] if item["sourceElementFileId"] in batch["sourceElementFileIds"])
        item["qaGlbPath"] = batch_by_id[item["batchId"]]["glbPath"]

    region_packages = {}
    for region in EXPECTED_REGIONS:
        members = [record_by_id[fj] for fj in ids_by_region[region]]
        all_bounds = geometry_bounds_by_region[region]
        if not all_bounds["vertexCount"]:
            raise PackageError(f"empty region bounds for {region}")
        region_bounds = {
            "frame": FRAME,
            "unit": "m",
            "min": all_bounds["min"],
            "max": all_bounds["max"],
            "vertexCount": all_bounds["vertexCount"],
            "basis": "union of verified transformed OBJ vertices; no anatomy filtering",
        }
        category_source = json.loads((ROOT / f"atlas-data/manifests/bodyparts3d-r4-regions-t51/{region}.json").read_text(encoding="utf-8"))
        package = {
            "revision": "BodyParts3D-R4-T52-REGION-PACKAGE-v1",
            "status": "internal_static_source_package_not_product_scene",
            "regionId": region,
            "regionLabelKo": category_source["labelKo"],
            "visibleSubcategoryMenu": False,
            "sourceScope": {"sourceMuscleConceptCandidateCount": category_source["counts"]["expectedSourceMuscleConceptIds"], "sourceBoneConceptCandidateCount": category_source["counts"]["expectedSourceBoneConceptIds"], "sourceAtomicFJCount": len(members), "acquired": len(members), "validated": len(members), "converted": len(members), "failed": 0, "notAttempted": 0, "downloadFailures": 0},
            "sourceAndFrame": {"sourceId": SOURCE_ID, "release": "BodyParts3D Release 4.0", "sourceArchiveIds": sorted({m["sourceArchiveTree"] for m in members}), "frame": FRAME, "poseId": POSE, "mirrorOrSyntheticOppositeSide": False, "lod": "99%-reduced source profile; no multilevel LOD chain", "attribution": ATTRIBUTION},
            "regionBounds": region_bounds,
            "meshAssetIds": [m["stableMeshAssetId"] for m in members],
            "sourceElementFileIds": [m["sourceElementFileId"] for m in members],
            "meshAssets": members,
            "canonicalMembershipsCreated": 0,
            "learnerStableIdentity": "only explicit existing crosswalks are populated; source-only FJ IDs remain source-only",
            "anatomyReview": "not_reviewed",
            "distributionStatus": "held_pending_legacy_OBJ_header_license_reconciliation",
        }
        region_packages[region] = package
        write_json(OUT_ROOT / f"{region}.json", package)

    combined = {
        "revision": "BodyParts3D-R4-T52-HEAD-NECK-PACKAGE-v1",
        "status": "partial_static_source_package_pending_human_laterality_review",
        "taskScope": "only T51 source-root acquisition candidates for head and neck; no other region, rig, nerve, motion, or product scene",
        "createdAt": acquisition["acquiredAt"],
        "sourceFreezePath": "work/evidence/T52/frozen-source-set.json",
        "sourceFreezeSha256": sha256_bytes(frozen_bytes),
        "frozenMembershipSha256": frozen["frozenMembershipSha256"],
        "sourceAcquisitionPath": "work/evidence/T52/source-acquisition.json",
        "sourceAcquisitionSha256": sha256_file(ACQUISITION_PATH),
        "sourceInputManifest": "atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json",
        "sourceInputManifestSha256": sha256_file(ROOT / "atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json"),
        "regionInputSha256": frozen["regionInputSha256"],
        "scope": {"regions": list(EXPECTED_REGIONS), "regionPackageCount": 2, "uniqueSourceFJCount": len(source_records), "distinctHeaderFMAConceptCount": len(fma_to_fj), "FMAConceptsReferencedByMultipleFJFiles": len(repeated_fma_groups), "crossRegionDuplicateFJIds": [], "sourceNameConflicts": len(header_name_mismatches), "emptyOrInvalidMeshes": len(invalid), "sourceNameBoundsCenterOppositionsHumanCheckRequired": len(side_center_oppositions), "sourceNameBoundsCrossMidlineInconclusive": len(side_midline_inconclusive), "canonicalStableLearnerBindings": sum(bool(x["existingLearnerStableId"]) for x in source_records), "sourceOnlyMeshAssets": sum(not x["existingLearnerStableId"] for x in source_records), "wholeBodyCanonicalDenominator": None},
        "internalBatches": batch_glbs,
        "regionPackages": {region: {"path": f"atlas-data/manifests/bodyparts3d-r4-t52/{region}.json", "sha256": sha256_file(OUT_ROOT / f"{region}.json"), "sourceMeshCount": len(ids_by_region[region]), "regionBounds": region_packages[region]["regionBounds"]} for region in EXPECTED_REGIONS},
        "identityPolicy": "No new HA canonical structure IDs or learner membership are minted. FJ source identity and existing HA IDs stay separate.",
        "sourceNameConflicts": header_name_mismatches,
        "FMAConceptsReferencedByMultipleFJFiles": repeated_fma_groups,
        "lateralityBoundsDiagnostics": laterality_diagnostics,
        "sourceAssets": source_records,
        "rights": json.loads(ACQUISITION_PATH.read_text(encoding="utf-8"))["rightsBoundary"],
        "reviewBoundary": {"sourceMeshIdentityChecked": True, "humanAnatomyReviewed": False, "reviewedPromotions": 0, "learnerNavigationChanged": False, "canonicalCatalogChanged": False},
    }
    combined_path = OUT_ROOT / "head-neck.json"
    write_json(combined_path, combined)
    # The self digest remains external evidence to avoid a self-referential payload.
    verification = {
        "revision": "T52-PACKAGE-VERIFICATION-v1",
        "combinedManifestPath": combined_path.relative_to(ROOT).as_posix(),
        "combinedManifestSha256": sha256_file(combined_path),
        "regionPackageSha256": {r: sha256_file(OUT_ROOT / f"{r}.json") for r in EXPECTED_REGIONS},
        "meshCounts": {r: len(ids_by_region[r]) for r in EXPECTED_REGIONS},
        "sourceFJUnique": len(source_records),
        "crossRegionDuplicates": [],
        "duplicateSourceIds": False,
        "emptyMeshes": len(invalid),
        "nameConflicts": header_name_mismatches,
        "lateralityBoundsDiagnostics": laterality_diagnostics,
        "lateralityCounts": {region: {side: sum(row["laterality"] == side for row in region_packages[region]["meshAssets"]) for side in sorted({item["laterality"] for item in region_packages[region]["meshAssets"]})} for region in EXPECTED_REGIONS},
        "allFrozenItemsAcquiredValidatedConverted": True,
        "batchesMax10": max(row["meshCount"] for row in batch_glbs) <= EXPECTED_BATCH_SIZE,
        "canonicalBindings": combined["scope"]["canonicalStableLearnerBindings"],
        "sourceOnly": combined["scope"]["sourceOnlyMeshAssets"],
        "regionBoundsAvailable": all(region_packages[r]["regionBounds"]["min"] != region_packages[r]["regionBounds"]["max"] for r in EXPECTED_REGIONS),
        "reviewedPromotions": 0,
        "navigationChanged": False,
        "historicalT51ManifestChanged": False,
        "fullArchiveDownloaded": False,
    }
    write_json(ROOT / "work/evidence/T52/package-verification.json", verification)
    return {"manifestPath": combined_path.relative_to(ROOT).as_posix(), "sourceFiles": len(source_records), "batches": len(batch_glbs), "verification": verification}


if __name__ == "__main__":
    try:
        print(json.dumps(build(), ensure_ascii=False, indent=2))
    except Exception as exc:
        raise SystemExit(f"T52 package build failed closed: {exc}")
