#!/usr/bin/env python3
"""Deterministically convert the T02 BodyParts3D right-calf OBJ subset to GLB.

Uses only Python's standard library. It refuses files that are not listed in
the T02 asset manifest and never writes into the source OBJ directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
LICENSE_ID = "LIC-BP3D-LSDB-ARCHIVE-CC-BY-4.0"
ATLAS_FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE_ID = "bodyparts3d-r4-static-reference"
ASSET_REVISION = "BP3D-R4-OBJ-TO-GLB-V1"
MODEL_ID = "HA-MODEL-BP3D4-R4-RIGHT-LOWER-LEG-STATIC"
REQUIRED_CREDIT = (
    "BodyParts3D, © The Database Center for Life Science licensed under "
    "CC Attribution 4.0 International"
)
TRANSFORM_ROTATION = ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0))
SCALE_TO_METERS = 0.001
COMBINED_LINEAR = ((0.001, 0.0, 0.0), (0.0, 0.0, 0.001), (0.0, -0.001, 0.0))
DEFAULT_GLB = Path(
    "atlas-data/assets/derived-glb/bodyparts3d-r4-right-lower-leg/"
    "right-lower-leg.glb"
)
DEFAULT_MANIFEST = Path("atlas-data/manifests/derived-assets-t07.json")


class ConversionError(RuntimeError):
    pass


def json_load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def parse_obj(path: Path) -> Tuple[
    List[Tuple[float, float, float]],
    List[Tuple[float, float, float]],
    List[Tuple[int, int, int]],
]:
    vertices: List[Tuple[float, float, float]] = []
    normals: List[Tuple[float, float, float]] = []
    triangles: List[Tuple[int, int, int]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for line_no, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            if fields[0] == "v":
                if len(fields) != 4:
                    raise ConversionError(
                        "{}:{}: expected exactly three OBJ vertex coordinates".format(
                            path, line_no
                        )
                    )
                try:
                    vertex = tuple(float(item) for item in fields[1:4])
                except ValueError as exc:
                    raise ConversionError("{}:{}: invalid vertex".format(path, line_no)) from exc
                if not all(math.isfinite(item) for item in vertex):
                    raise ConversionError("{}:{}: non-finite vertex".format(path, line_no))
                vertices.append(vertex)
            elif fields[0] == "vn":
                if len(fields) != 4:
                    raise ConversionError("{}:{}: expected exactly three OBJ normal coordinates".format(path, line_no))
                try:
                    normal = tuple(float(item) for item in fields[1:4])
                except ValueError as exc:
                    raise ConversionError("{}:{}: invalid normal".format(path, line_no)) from exc
                if not all(math.isfinite(item) for item in normal):
                    raise ConversionError("{}:{}: non-finite normal".format(path, line_no))
                length = math.sqrt(sum(value * value for value in normal))
                if abs(length - 1.0) > 1e-5:
                    raise ConversionError("{}:{}: source normal is not unit length".format(path, line_no))
                normals.append(normal)
            elif fields[0] == "f":
                if len(fields) != 4:
                    raise ConversionError(
                        "{}:{}: non-triangle faces are not silently triangulated".format(
                            path, line_no
                        )
                    )
                indices: List[int] = []
                normal_indices: List[int] = []
                for token in fields[1:4]:
                    components = token.split("/")
                    if len(components) != 3 or not components[2]:
                        raise ConversionError("{}:{}: each OBJ face must reference a vertex normal".format(path, line_no))
                    head = components[0]
                    try:
                        raw_index = int(head)
                    except ValueError as exc:
                        raise ConversionError(
                            "{}:{}: invalid face index".format(path, line_no)
                        ) from exc
                    if raw_index == 0:
                        raise ConversionError("{}:{}: OBJ index zero is invalid".format(path, line_no))
                    index = raw_index - 1 if raw_index > 0 else len(vertices) + raw_index
                    if index < 0 or index >= len(vertices):
                        raise ConversionError(
                            "{}:{}: face index outside the current vertex list".format(path, line_no)
                        )
                    indices.append(index)
                    try:
                        raw_normal_index = int(components[2])
                    except ValueError as exc:
                        raise ConversionError("{}:{}: invalid normal index".format(path, line_no)) from exc
                    if raw_normal_index == 0:
                        raise ConversionError("{}:{}: OBJ normal index zero is invalid".format(path, line_no))
                    normal_index = raw_normal_index - 1 if raw_normal_index > 0 else len(normals) + raw_normal_index
                    if normal_index < 0 or normal_index >= len(normals):
                        raise ConversionError("{}:{}: face normal index outside the current normal list".format(path, line_no))
                    normal_indices.append(normal_index)
                if normal_indices != indices:
                    raise ConversionError("{}:{}: per-vertex normal mapping differs; no implicit reindexing is allowed".format(path, line_no))
                triangles.append((indices[0], indices[1], indices[2]))
    if not vertices or not normals or not triangles:
        raise ConversionError("{}: vertices, normals, and triangles are all required".format(path))
    if len(normals) != len(vertices):
        raise ConversionError("{}: source normal and vertex counts differ".format(path))
    return vertices, normals, triangles


def transform_vertex(vertex: Sequence[float]) -> Tuple[float, float, float]:
    x, y, z = vertex
    return (x * SCALE_TO_METERS, z * SCALE_TO_METERS, -y * SCALE_TO_METERS)


def transform_normal(normal: Sequence[float]) -> Tuple[float, float, float]:
    x, y, z = normal
    return (x, z, -y)


def float32_bytes(values: Iterable[float]) -> bytes:
    values = tuple(values)
    return struct.pack("<{}f".format(len(values)), *values)


def float32_value(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def vector_bounds(vertices: Sequence[Sequence[float]]):
    return {
        "min": [min(vertex[axis] for vertex in vertices) for axis in range(3)],
        "max": [max(vertex[axis] for vertex in vertices) for axis in range(3)],
    }


def geometry_hash(position_bytes: bytes, index_bytes: bytes, mesh_id: str) -> str:
    digest = hashlib.sha256()
    digest.update(b"HUMAN-ATLAS-T07-GEOMETRY-V1\0")
    digest.update(mesh_id.encode("ascii"))
    digest.update(b"\0")
    digest.update(struct.pack("<Q", len(position_bytes)))
    digest.update(position_bytes)
    digest.update(struct.pack("<Q", len(index_bytes)))
    digest.update(index_bytes)
    return digest.hexdigest()


def topology_hash(index_bytes: bytes, vertex_count: int, mesh_id: str) -> str:
    digest = hashlib.sha256()
    digest.update(b"HUMAN-ATLAS-T07-TOPOLOGY-V1\0")
    digest.update(mesh_id.encode("ascii"))
    digest.update(b"\0")
    digest.update(struct.pack("<QQ", vertex_count, len(index_bytes)))
    digest.update(index_bytes)
    return digest.hexdigest()


def add_buffer_view(buffer: bytearray, data: bytes, target: int) -> Dict[str, int]:
    while len(buffer) % 4:
        buffer.append(0)
    offset = len(buffer)
    buffer.extend(data)
    return {"buffer": 0, "byteOffset": offset, "byteLength": len(data), "target": target}


def build_glb(mesh_inputs: Sequence[Dict]) -> Tuple[bytes, List[Dict]]:
    binary = bytearray()
    buffer_views: List[Dict] = []
    accessors: List[Dict] = []
    gltf_meshes: List[Dict] = []
    nodes: List[Dict] = []
    mesh_records: List[Dict] = []

    for index, item in enumerate(mesh_inputs):
        mesh_id = "HA-MESH-BP3D4-{}".format(item["file_id"])
        source_vertices, source_normals, triangles = parse_obj(item["source_path"])
        if len(source_vertices) != item["asset"]["vertex_count"]:
            raise ConversionError("{}: vertex count differs from T02 manifest".format(item["file_id"]))
        if len(triangles) != item["asset"]["polygon_count"]:
            raise ConversionError("{}: face count differs from T02 manifest".format(item["file_id"]))

        transformed = [transform_vertex(vertex) for vertex in source_vertices]
        packed_positions = float32_bytes(value for vertex in transformed for value in vertex)
        stored_vertices = [
            tuple(float32_value(value) for value in vertex) for vertex in transformed
        ]
        transformed_normals = [transform_normal(normal) for normal in source_normals]
        packed_normals = float32_bytes(value for normal in transformed_normals for value in normal)
        source_indices = [value for triangle in triangles for value in triangle]
        component_type = 5123 if len(source_vertices) <= 65535 else 5125
        if component_type == 5123:
            packed_indices = struct.pack("<{}H".format(len(source_indices)), *source_indices)
        else:
            packed_indices = struct.pack("<{}I".format(len(source_indices)), *source_indices)

        pos_view = add_buffer_view(binary, packed_positions, 34962)
        pos_accessor_index = len(accessors)
        accessors.append(
            {
                "bufferView": len(buffer_views),
                "byteOffset": 0,
                "componentType": 5126,
                "count": len(stored_vertices),
                "type": "VEC3",
                "min": [min(v[i] for v in stored_vertices) for i in range(3)],
                "max": [max(v[i] for v in stored_vertices) for i in range(3)],
            }
        )
        buffer_views.append(pos_view)

        normal_view = add_buffer_view(binary, packed_normals, 34962)
        normal_accessor_index = len(accessors)
        accessors.append(
            {
                "bufferView": len(buffer_views),
                "byteOffset": 0,
                "componentType": 5126,
                "count": len(transformed_normals),
                "type": "VEC3",
            }
        )
        buffer_views.append(normal_view)

        idx_view = add_buffer_view(binary, packed_indices, 34963)
        idx_accessor_index = len(accessors)
        accessors.append(
            {
                "bufferView": len(buffer_views),
                "byteOffset": 0,
                "componentType": component_type,
                "count": len(source_indices),
                "type": "SCALAR",
                "min": [min(source_indices)],
                "max": [max(source_indices)],
            }
        )
        buffer_views.append(idx_view)

        extras = {
            "stableModelId": MODEL_ID,
            "stableMeshAssetId": mesh_id,
            "sourceId": SOURCE_ID,
            "sourceFileId": item["file_id"],
            "representationId": item["asset"]["representation_id"],
            "externalConceptId": item["asset"]["concept_id"],
            "sourceSha256": item["source_sha256"],
            "reviewState": "needs_review",
        }
        gltf_meshes.append(
            {
                "name": mesh_id,
                "primitives": [
                    {
                        "attributes": {"NORMAL": normal_accessor_index, "POSITION": pos_accessor_index},
                        "indices": idx_accessor_index,
                        "mode": 4,
                    }
                ],
                "extras": extras,
            }
        )
        nodes.append({"name": mesh_id, "mesh": index, "extras": extras})
        mesh_records.append(
            {
                "meshAssetId": mesh_id,
                "modelId": MODEL_ID,
                "nodeIndex": index,
                "meshIndex": index,
                "sourceFileId": item["file_id"],
                "sourceFile": item["source_relative_path"],
                "sourceSha256": item["source_sha256"],
                "sourceBytes": item["asset"]["bytes"],
                "externalConceptId": item["asset"]["concept_id"],
                "representationId": item["asset"]["representation_id"],
                "vertexCount": len(stored_vertices),
                "triangleCount": len(triangles),
                "sourceBoundsMm": vector_bounds(source_vertices),
                "atlasBoundsM": vector_bounds(stored_vertices),
                "geometrySha256": geometry_hash(packed_positions, packed_indices, mesh_id),
                "topologySha256": topology_hash(packed_indices, len(stored_vertices), mesh_id),
                "normalSha256": sha256_bytes(packed_normals),
                "normalCount": len(transformed_normals),
                "indexComponentType": component_type,
            }
        )

    gltf = {
        "asset": {"version": "2.0", "generator": "HUMAN ATLAS T07 deterministic converter 1"},
        "scene": 0,
        "scenes": [{"nodes": list(range(len(nodes))), "name": MODEL_ID}],
        "nodes": nodes,
        "meshes": gltf_meshes,
        "accessors": accessors,
        "bufferViews": buffer_views,
        "buffers": [{"byteLength": len(binary)}],
    }
    json_chunk = canonical_json_bytes(gltf)
    while len(json_chunk) % 4:
        json_chunk += b" "
    bin_chunk = bytes(binary)
    while len(bin_chunk) % 4:
        bin_chunk += b"\0"
    total_length = 12 + 8 + len(json_chunk) + 8 + len(bin_chunk)
    glb = bytearray(struct.pack("<4sII", b"glTF", 2, total_length))
    glb.extend(struct.pack("<II", len(json_chunk), 0x4E4F534A))
    glb.extend(json_chunk)
    glb.extend(struct.pack("<II", len(bin_chunk), 0x004E4942))
    glb.extend(bin_chunk)
    return bytes(glb), mesh_records


def t02_crosswalk_index(path: Path) -> Dict[str, Dict]:
    data = json_load(path)
    result: Dict[str, Dict] = {}
    for row in data.get("pilot_muscles", []):
        result[row["element_file_id"]] = row
    for row in data.get("region_bone_inventory", []):
        if row.get("availability") == "subset_acquired":
            result[row["element_file_id"]] = row
    return result


def load_inputs(project_root: Path):
    asset_manifest_path = project_root / "atlas-data/manifests/assets.json"
    asset_manifest = json_load(asset_manifest_path)
    t02_crosswalk_path = project_root / "work/evidence/T02/source-crosswalk.json"
    source_crosswalk = t02_crosswalk_index(t02_crosswalk_path)
    t04_crosswalk_path = project_root / "atlas-data/catalog/source-crosswalk.json"
    t04_crosswalk = json_load(t04_crosswalk_path)
    t04_by_file = {
        row["elementFileId"]: row for row in t04_crosswalk.get("bodyParts3dMappings", [])
    }
    config_path = project_root / "atlas-data/manifests/mesh-crosswalk-t07.json"
    config = json_load(config_path)
    canonical_path = project_root / "atlas-data/catalog/canonical-catalog.json"
    canonical = json_load(canonical_path)
    entities = canonical["entities"]
    canonical_muscles = {row["id"]: row for row in entities["muscleConcepts"]}
    canonical_structures = {row["id"]: row for row in entities["structures"]}

    assets = asset_manifest.get("acquiredAssets", [])
    if len(assets) != 11 or len(config.get("entries", [])) != 11:
        raise ConversionError("T07 is restricted to the 11 acquired T02 files and 11 explicit crosswalk rows")
    if asset_manifest.get("source", {}).get("sourceId") != SOURCE_ID:
        raise ConversionError("T02 source ID changed; review the source before conversion")
    if len({row.get("file_id") for row in assets}) != 11:
        raise ConversionError("duplicate or missing T02 file IDs")
    if len({row.get("fileId") for row in config["entries"]}) != 11:
        raise ConversionError("duplicate T07 crosswalk file IDs")

    config_by_file = {row["fileId"]: row for row in config["entries"]}
    asset_by_file = {row["file_id"]: row for row in assets}
    if set(config_by_file) != set(asset_by_file) or set(source_crosswalk) != set(asset_by_file):
        raise ConversionError("T07 crosswalk and T02 actual-asset list must match exactly")

    items = []
    for file_id in sorted(asset_by_file):
        asset = asset_by_file[file_id]
        source_row = source_crosswalk[file_id]
        relation = config_by_file[file_id]
        manifest_file = asset["file"]
        if manifest_file.startswith("HUMAN ATLAS/"):
            manifest_file = manifest_file[len("HUMAN ATLAS/") :]
        if manifest_file != source_row.get("local_asset"):
            raise ConversionError("{}: T02 asset path does not match its source crosswalk".format(file_id))
        if asset["concept_id"] != source_row.get("concept_id"):
            raise ConversionError("{}: FMA source concept differs from T02 crosswalk".format(file_id))
        if asset["representation_id"] != source_row.get("representation_id"):
            raise ConversionError("{}: BP representation differs from T02 crosswalk".format(file_id))
        if relation["fileId"] != file_id or not relation.get("relationStatus"):
            raise ConversionError("{}: incomplete stable crosswalk entry".format(file_id))
        if relation.get("targetEntityId") is not None:
            target = relation["targetEntityId"]
            kind = relation["targetEntityType"]
            if kind in ("individual_muscle", "muscle_part"):
                record = canonical_muscles.get(target)
                if not record or record["entityType"] != kind:
                    raise ConversionError("{}: canonical muscle target is absent or has wrong type".format(file_id))
                if kind == "muscle_part" and record.get("parentId") not in canonical_muscles:
                    raise ConversionError("{}: canonical part parent is missing".format(file_id))
            elif kind == "structure":
                record = canonical_structures.get(target)
                if not record or record["kind"] != "bone":
                    raise ConversionError("{}: canonical bone structure is absent".format(file_id))
            else:
                raise ConversionError("{}: unsupported canonical target type".format(file_id))
        elif relation["targetEntityType"] != "structure" or not relation["relationStatus"].startswith("unmapped_"):
            raise ConversionError("{}: unresolved target must remain explicitly unresolved".format(file_id))

        if asset["kind"] == "muscle":
            t04 = t04_by_file.get(file_id)
            if not t04:
                raise ConversionError("{}: no T04 muscle source crosswalk".format(file_id))
            if t04["stableConceptId"] != relation.get("targetEntityId"):
                raise ConversionError("{}: target does not agree with T04 source crosswalk".format(file_id))
            if t04["externalConceptId"] != asset["concept_id"] or t04["externalRepresentationId"] != asset["representation_id"]:
                raise ConversionError("{}: T04 external IDs differ from T02 asset manifest".format(file_id))
        elif asset["kind"] != "bone":
            raise ConversionError("{}: unexpected T02 asset category".format(file_id))

        relative_path = Path(asset["file"])
        source_path = project_root / asset_manifest["assetFolder"] / relative_path.name
        if not source_path.is_file():
            raise ConversionError("{}: source OBJ missing from T02 asset folder".format(file_id))
        actual_hash = sha256_file(source_path)
        if actual_hash != asset["sha256"]:
            raise ConversionError("{}: source OBJ SHA-256 differs from T02 manifest".format(file_id))
        if source_path.stat().st_size != asset["bytes"]:
            raise ConversionError("{}: source OBJ byte count differs from T02 manifest".format(file_id))
        if asset.get("right_side_coordinate_check") != "pass_source_x_max_lt_0":
            raise ConversionError("{}: T02 right-side check is absent".format(file_id))
        items.append(
            {
                "file_id": file_id,
                "asset": asset,
                "source_row": source_row,
                "relation": relation,
                "source_path": source_path,
                "source_relative_path": relative_path.as_posix().removeprefix("HUMAN ATLAS/"),
                "source_sha256": actual_hash,
            }
        )
    return asset_manifest, config, items


def glb_asset_manifest(project_root: Path, glb_path: Path, records: Sequence[Dict]):
    asset_manifest = json_load(project_root / "atlas-data/manifests/assets.json")
    config = json_load(project_root / "atlas-data/manifests/mesh-crosswalk-t07.json")
    glb_hash = sha256_file(glb_path)
    glb_size = glb_path.stat().st_size
    uri = glb_path.relative_to(project_root).as_posix()
    crosswalk_index = {row["fileId"]: row for row in config["entries"]}
    mesh_assets = []
    crosswalks = []
    for record in records:
        relation = crosswalk_index[record["sourceFileId"]]
        mesh_assets.append(
            {
                "id": record["meshAssetId"],
                "revision": ASSET_REVISION,
                "sourceId": SOURCE_ID,
                "hash": glb_hash,
                "topologyHash": record["topologySha256"],
                "uri": uri,
                "format": "glb",
                "units": "m",
                "axes": {
                    "frameId": ATLAS_FRAME,
                    "handedness": "right",
                    "positiveX": "patient_left",
                    "positiveY": "head",
                    "positiveZ": "anterior",
                },
                "pose": {
                    "id": POSE_ID,
                    "description": asset_manifest["geometry"]["pose"]["description"],
                },
                "licenseId": LICENSE_ID,
                "laterality": "right",
            }
        )
        crosswalks.append(
            {
                "meshAssetId": record["meshAssetId"],
                "sourceFileId": record["sourceFileId"],
                "sourceSha256": record["sourceSha256"],
                "externalConceptId": record["externalConceptId"],
                "representationId": record["representationId"],
                "targetEntityType": relation["targetEntityType"],
                "targetEntityId": relation["targetEntityId"],
                "representationType": relation["representationType"],
                "relationStatus": relation["relationStatus"],
                "reviewState": "needs_review",
                "laterality": "right",
                "sourceTableLocators": record["sourceTableLocators"],
            }
        )
    return {
        "manifestVersion": "T07-derived-assets-v1",
        "task": "T07",
        "status": "local_candidate_needs_review",
        "modelId": MODEL_ID,
        "regionId": "right_lower_leg",
        "poseId": POSE_ID,
        "glb": {"uri": uri, "sha256": glb_hash, "bytes": glb_size, "meshCount": len(records)},
        "meshAssets": mesh_assets,
        "meshNodes": records,
        "meshCrosswalk": crosswalks,
        "transform": {
            "sourceId": SOURCE_ID,
            "sourceFrameDescription": "BodyParts3D Release 4.0 coordinates: RH; +X patient left; +Y posterior; +Z superior.",
            "sourceUnits": "mm",
            "targetFrameId": ATLAS_FRAME,
            "targetHandedness": "right",
            "targetPositiveX": "patient_left",
            "targetPositiveY": "head",
            "targetPositiveZ": "anterior",
            "targetUnits": "m",
            "formula": "[x,y,z]atlas_m = [x,z,-y]source_mm / 1000",
            "rotationMatrix": [list(row) for row in TRANSFORM_ROTATION],
            "scaleToMeters": SCALE_TO_METERS,
            "combinedLinearMatrix": [list(row) for row in COMBINED_LINEAR],
            "rotationDeterminant": 1,
            "triangleWindingReversed": False,
            "reflectionApplied": False,
        },
        "attribution": {
            "sourceId": SOURCE_ID,
            "sourceTitle": "BodyParts3D, Release 4.0",
            "sourceReleaseDate": asset_manifest["source"]["releaseDataUpdated"],
            "sourceArchiveUrl": asset_manifest["source"]["archiveUrl"],
            "sourceArchiveLicenseUrl": asset_manifest["source"]["licensePage"],
            "licenseId": LICENSE_ID,
            "license": "CC BY 4.0, as recorded for the exact LSDB Archive Release 4.0 source in the T02 manifest.",
            "requiredCreditVerbatim": REQUIRED_CREDIT,
            "embeddedLegacyObjNotice": asset_manifest["acquiredAssets"][0]["embedded_license_header"],
            "legacyNoticeHandling": "Original OBJ comments remain byte-identical; T07 does not alter source files. The legacy embedded notice is recorded separately from the current archive license terms.",
            "modificationSummary": "OBJ triangle positions converted from mm to m and reoriented by the right-handed source-to-Atlas rotation; source vertex normals rotated without scale; triangle indices and winding preserved; no remeshing, decimation, reflection, deformation, or annotation.",
            "sourceAssetManifestSha256": sha256_file(project_root / "atlas-data/manifests/assets.json"),
            "sourceCrosswalkSha256": sha256_file(project_root / "work/evidence/T02/source-crosswalk.json"),
            "canonicalCatalogSha256": sha256_file(project_root / "atlas-data/catalog/canonical-catalog.json"),
        },
        "validation": {
            "reviewState": "needs_review",
            "technicalValidation": "pending",
            "anatomyIdentityReviewed": False,
            "attachmentAnnotationsCreated": False,
            "publicDistribution": False,
        },
    }


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def convert(project_root: Path, output_glb: Path, output_manifest: Path) -> Dict:
    asset_manifest, config, items = load_inputs(project_root)
    glb_bytes, records = build_glb(items)
    output_glb = output_glb if output_glb.is_absolute() else project_root / output_glb
    output_manifest = output_manifest if output_manifest.is_absolute() else project_root / output_manifest
    output_glb.parent.mkdir(parents=True, exist_ok=True)
    output_glb.write_bytes(glb_bytes)

    # Source table row locators are copied from the inspected T02 crosswalk.
    rows = t02_crosswalk_index(project_root / "work/evidence/T02/source-crosswalk.json")
    for record in records:
        row = rows[record["sourceFileId"]]
        record["sourceTableLocators"] = row.get("table_rows", {})
        record["sourceName"] = row.get("source_name")
        record["targetEntityType"] = next(
            entry["targetEntityType"] for entry in config["entries"] if entry["fileId"] == record["sourceFileId"]
        )
        record["targetEntityId"] = next(
            entry["targetEntityId"] for entry in config["entries"] if entry["fileId"] == record["sourceFileId"]
        )
        record["relationStatus"] = next(
            entry["relationStatus"] for entry in config["entries"] if entry["fileId"] == record["sourceFileId"]
        )

    manifest = glb_asset_manifest(project_root, output_glb, records)
    write_json(output_manifest, manifest)
    return {
        "glb": output_glb,
        "manifest": output_manifest,
        "glbSha256": sha256_file(output_glb),
        "manifestSha256": sha256_file(output_manifest),
        "meshCount": len(records),
        "sourceCount": len(items),
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    project_root = Path(__file__).resolve().parents[2]
    parser.add_argument("--project-root", type=Path, default=project_root)
    parser.add_argument("--output-glb", type=Path, default=DEFAULT_GLB)
    parser.add_argument("--output-manifest", type=Path, default=DEFAULT_MANIFEST)
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        result = convert(args.project_root.resolve(), args.output_glb, args.output_manifest)
    except (ConversionError, OSError, KeyError, ValueError) as exc:
        print("T07 conversion failed: {}".format(exc), file=sys.stderr)
        return 2
    print("GLB: {}".format(result["glb"]))
    print("Manifest: {}".format(result["manifest"]))
    print("Meshes: {}".format(result["meshCount"]))
    print("GLB SHA-256: {}".format(result["glbSha256"]))
    print("Manifest SHA-256: {}".format(result["manifestSha256"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
