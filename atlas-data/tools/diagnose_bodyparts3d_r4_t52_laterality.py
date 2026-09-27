#!/usr/bin/env python3
"""Read-only T69 laterality diagnostics for the frozen T52 BodyParts3D set.

This tool preserves source labels and raw OBJ vertices. It reports measurements;
it does not infer or edit anatomy, recenter a region, mirror a mesh, or promote
human review. Historical T52 counts remain in the T52 package validator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
T52_MANIFEST = Path("atlas-data/manifests/bodyparts3d-r4-t52/head-neck.json")
T51_MANIFEST = Path("atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json")
DEFAULT_OUTPUT = Path("work/evidence/T69/diagnostic.json")
DEFAULT_ASSESSMENT = Path("work/evidence/T69/assessment.json")
EXPECTED_TRANSFORM = "[x,y,z]mm -> [x,z,-y]m; no mirroring"
EXPECTED_FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
SOURCE_COORDINATE_IMAGE = "https://dbarchive.biosciencedbc.jp/archive/bodyparts3d/images/coordinate_system.png"
SOURCE_RELEASE_NOTE = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/release_4.0_e.html"
SOURCE_README = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/README_e.html"


class DiagnosticError(ValueError):
    pass


@dataclass
class MeshMetrics:
    source_path: str
    source_sha256: str
    source_bytes: int
    header: dict[str, str]
    vertex_count: int
    surface_vertex_count: int
    orphan_vertex_count: int
    orphan_negative_x_vertex_count: int
    orphan_near_plane_vertex_count: int
    orphan_positive_x_vertex_count: int
    polygon_face_count: int
    triangle_count: int
    bounds_min_mm: list[float]
    bounds_max_mm: list[float]
    surface_bounds_min_mm: list[float]
    surface_bounds_max_mm: list[float]
    centroid_mm: list[float]
    negative_x_vertex_count: int
    near_plane_vertex_count: int
    positive_x_vertex_count: int
    negative_x_surface_area_mm2: float
    near_plane_band_mm: float
    exact_plane_surface_area_mm2: float
    positive_x_surface_area_mm2: float
    total_surface_area_mm2: float
    component_count: int
    components: list[dict[str, Any]]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_obj(path: Path, *, near_plane_band_mm: float = 0.001) -> MeshMetrics:
    """Parse OBJ geometry and measure its actual surface on either side of x=0.

    The 0.001 mm band is the project's recorded coordinate quantization scale
    (T50 surface comparison), not an anatomical tolerance or laterality rule.
    Surface portions are clipped at the exact source x=0 plane.
    """
    vertices: list[tuple[float, float, float]] = []
    triangles: list[tuple[int, int, int]] = []
    referenced_vertices: set[int] = set()
    polygon_face_count = 0
    header: dict[str, str] = {}
    header_keys = {
        "File ID": "fileId",
        "Representation ID": "representationId",
        "Concept ID": "conceptId",
        "English name": "englishName",
        "Build-up logic": "buildUpLogic",
        "Bounds(mm)": "boundsMm",
        "Volume(cm3)": "volumeCm3",
    }
    with path.open("r", encoding="utf-8", errors="strict") as stream:
        for line in stream:
            if line.startswith("#"):
                match = re.match(r"^#\s*([^:]+):\s*(.*)\s*$", line)
                if match and match.group(1).strip() in header_keys:
                    header[header_keys[match.group(1).strip()]] = match.group(2)
                continue
            parts = line.strip().split()
            if not parts:
                continue
            if parts[0] == "v":
                if len(parts) < 4:
                    raise DiagnosticError(f"Malformed vertex row in {path}")
                vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif parts[0] == "f":
                if len(parts) < 4:
                    raise DiagnosticError(f"Malformed polygon row in {path}")
                polygon_face_count += 1
                indices: list[int] = []
                for raw in parts[1:]:
                    index = int(raw.split("/", 1)[0])
                    index = index - 1 if index > 0 else len(vertices) + index
                    if index < 0 or index >= len(vertices):
                        raise DiagnosticError(f"Face index out of range in {path}: {raw}")
                    indices.append(index)
                for i in range(1, len(indices) - 1):
                    triangles.append((indices[0], indices[i], indices[i + 1]))
                    referenced_vertices.update((indices[0], indices[i], indices[i + 1]))
    if not vertices or not triangles:
        raise DiagnosticError(f"Empty OBJ geometry: {path}")

    xs = [v[0] for v in vertices]
    mins = [min(v[i] for v in vertices) for i in range(3)]
    maxs = [max(v[i] for v in vertices) for i in range(3)]
    sums = [sum(v[i] for v in vertices) / len(vertices) for i in range(3)]
    used_points = [vertices[i] for i in referenced_vertices]
    surface_mins = [min(v[i] for v in used_points) for i in range(3)]
    surface_maxs = [max(v[i] for v in used_points) for i in range(3)]
    orphan_indices = set(range(len(vertices))) - referenced_vertices
    orphan_xs = [vertices[i][0] for i in orphan_indices]
    negative_count = sum(x < -near_plane_band_mm for x in xs)
    near_count = sum(abs(x) <= near_plane_band_mm for x in xs)
    positive_count = sum(x > near_plane_band_mm for x in xs)

    parent = list(range(len(vertices)))
    rank = [0] * len(vertices)

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1

    triangle_areas: list[float] = []
    negative_area = positive_area = exact_plane_area = 0.0
    for tri in triangles:
        a, b, c = (vertices[i] for i in tri)
        union(tri[0], tri[1])
        union(tri[1], tri[2])
        total_area = triangle_area(a, b, c)
        triangle_areas.append(total_area)
        if all(v[0] == 0.0 for v in (a, b, c)):
            exact_plane_area += total_area
        else:
            negative_area += clipped_triangle_area((a, b, c), keep_positive=False)
            positive_area += clipped_triangle_area((a, b, c), keep_positive=True)

    comp_area: dict[int, float] = {}
    comp_vertices: dict[int, set[int]] = {}
    for tri, area in zip(triangles, triangle_areas):
        root = find(tri[0])
        comp_area[root] = comp_area.get(root, 0.0) + area
        comp_vertices.setdefault(root, set()).update(tri)

    components: list[dict[str, Any]] = []
    for root, indices in comp_vertices.items():
        pts = [vertices[i] for i in indices]
        cmin = [min(v[i] for v in pts) for i in range(3)]
        cmax = [max(v[i] for v in pts) for i in range(3)]
        centroid = [sum(v[i] for v in pts) / len(pts) for i in range(3)]
        area = comp_area[root]
        components.append({
            "vertexCount": len(indices),
            "surfaceAreaMm2": round(area, 6),
            "surfaceAreaFraction": round(area / (negative_area + positive_area + exact_plane_area), 8),
            "boundsMinMm": [round(x, 6) for x in cmin],
            "boundsMaxMm": [round(x, 6) for x in cmax],
            "vertexCentroidMm": [round(x, 6) for x in centroid],
            "centerSideDiagnosticOnly": "positive_x" if centroid[0] > 0 else "negative_x" if centroid[0] < 0 else "on_plane",
            "crossesPlaneByVertexBounds": cmin[0] <= 0 <= cmax[0],
        })
    components.sort(key=lambda x: (-x["surfaceAreaMm2"], -x["vertexCount"]))

    return MeshMetrics(
        source_path=str(path), source_sha256=sha256_file(path), source_bytes=path.stat().st_size,
        header=header, vertex_count=len(vertices), polygon_face_count=polygon_face_count,
        surface_vertex_count=len(referenced_vertices), orphan_vertex_count=len(orphan_indices),
        orphan_negative_x_vertex_count=sum(x < -near_plane_band_mm for x in orphan_xs),
        orphan_near_plane_vertex_count=sum(abs(x) <= near_plane_band_mm for x in orphan_xs),
        orphan_positive_x_vertex_count=sum(x > near_plane_band_mm for x in orphan_xs),
        triangle_count=len(triangles), bounds_min_mm=[round(x, 6) for x in mins],
        bounds_max_mm=[round(x, 6) for x in maxs],
        surface_bounds_min_mm=[round(x, 6) for x in surface_mins],
        surface_bounds_max_mm=[round(x, 6) for x in surface_maxs], centroid_mm=[round(x, 6) for x in sums],
        negative_x_vertex_count=negative_count, near_plane_vertex_count=near_count,
        positive_x_vertex_count=positive_count, negative_x_surface_area_mm2=round(negative_area, 6),
        near_plane_band_mm=near_plane_band_mm, exact_plane_surface_area_mm2=round(exact_plane_area, 6),
        positive_x_surface_area_mm2=round(positive_area, 6),
        total_surface_area_mm2=round(negative_area + positive_area + exact_plane_area, 6),
        component_count=len(components), components=components,
    )


def read_obj_vertices(path: Path) -> list[tuple[float, float, float]]:
    """Read vertex rows in source order for direct OBJ→GLB transform checks."""
    vertices: list[tuple[float, float, float]] = []
    with path.open("r", encoding="utf-8", errors="strict") as stream:
        for line in stream:
            if line.startswith("v "):
                fields = line.split()
                if len(fields) < 4:
                    raise DiagnosticError(f"Malformed OBJ vertex row in {path}")
                vertices.append((float(fields[1]), float(fields[2]), float(fields[3])))
    if not vertices:
        raise DiagnosticError(f"OBJ has no vertices: {path}")
    return vertices


def _node_transform_is_identity(node: dict[str, Any]) -> bool:
    if "matrix" in node:
        matrix = node["matrix"]
        identity = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        return len(matrix) == 16 and all(abs(float(a) - b) <= 1e-12 for a, b in zip(matrix, identity))
    return (
        all(abs(float(x)) <= 1e-12 for x in node.get("translation", [0.0, 0.0, 0.0]))
        and all(
            abs(float(value) - expected) <= 1e-12
            for value, expected in zip(node.get("rotation", [0.0, 0.0, 0.0, 1.0]), [0.0, 0.0, 0.0, 1.0])
        )
        and all(abs(float(x) - 1.0) <= 1e-12 for x in node.get("scale", [1.0, 1.0, 1.0]))
    )


def read_glb_positions(path: Path, source_fj_id: str) -> tuple[list[tuple[float, float, float]], dict[str, Any]]:
    """Read one source mesh's actual float32 POSITION accessor from a GLB."""
    raw = path.read_bytes()
    if len(raw) < 20:
        raise DiagnosticError(f"GLB is too short: {path}")
    magic, version, declared_length = struct.unpack_from("<4sII", raw, 0)
    if magic != b"glTF" or version != 2 or declared_length != len(raw):
        raise DiagnosticError(f"Invalid GLB 2 header or byte length: {path}")
    offset = 12
    document: dict[str, Any] | None = None
    binary: bytes | None = None
    while offset < len(raw):
        if offset + 8 > len(raw):
            raise DiagnosticError(f"Truncated GLB chunk header: {path}")
        chunk_length, chunk_type = struct.unpack_from("<II", raw, offset)
        offset += 8
        chunk = raw[offset:offset + chunk_length]
        if len(chunk) != chunk_length:
            raise DiagnosticError(f"Truncated GLB chunk: {path}")
        offset += chunk_length
        if chunk_type == 0x4E4F534A:
            document = json.loads(chunk.decode("utf-8").rstrip(" \t\r\n\0"))
        elif chunk_type == 0x004E4942:
            binary = chunk
    if document is None or binary is None:
        raise DiagnosticError(f"GLB requires JSON and BIN chunks: {path}")
    matches = [node for node in document.get("nodes", []) if node.get("extras", {}).get("sourceFileId") == source_fj_id]
    if len(matches) != 1:
        raise DiagnosticError(f"Expected one GLB node for {source_fj_id}; got {len(matches)} in {path}")
    node = matches[0]
    mesh_index = node.get("mesh")
    if not isinstance(mesh_index, int):
        raise DiagnosticError(f"GLB source node has no mesh binding: {source_fj_id}")
    primitives = document["meshes"][mesh_index].get("primitives", [])
    if len(primitives) != 1:
        raise DiagnosticError(f"Expected one primitive for {source_fj_id}; got {len(primitives)}")
    accessor_index = primitives[0].get("attributes", {}).get("POSITION")
    if not isinstance(accessor_index, int):
        raise DiagnosticError(f"GLB source primitive has no POSITION accessor: {source_fj_id}")
    accessor = document["accessors"][accessor_index]
    if accessor.get("componentType") != 5126 or accessor.get("type") != "VEC3" or accessor.get("normalized", False):
        raise DiagnosticError(f"GLB POSITION is not non-normalized float32 VEC3: {source_fj_id}")
    view = document["bufferViews"][accessor["bufferView"]]
    stride = view.get("byteStride", 12)
    if stride < 12:
        raise DiagnosticError(f"Invalid GLB POSITION byte stride: {source_fj_id}")
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    count = accessor["count"]
    end = start + (count - 1) * stride + 12 if count else start
    if start < 0 or end > len(binary):
        raise DiagnosticError(f"GLB POSITION accessor exceeds BIN chunk: {source_fj_id}")
    positions = [struct.unpack_from("<3f", binary, start + i * stride) for i in range(count)]
    return positions, {
        "sourceElementFileId": source_fj_id,
        "sourceNodeName": node.get("name"),
        "sourceSha256": node.get("extras", {}).get("sourceSha256"),
        "sourceFrame": node.get("extras", {}).get("sourceFrame"),
        "projectFrame": node.get("extras", {}).get("atlasFrame"),
        "transform": node.get("extras", {}).get("transform"),
        "nodeTransformIdentity": _node_transform_is_identity(node),
        "vertexCount": count,
        "glbPath": str(path),
        "glbSha256": sha256_file(path),
    }


def compare_obj_to_glb_transform(
    obj_path: Path, glb_path: Path, source_fj_id: str, expected_obj_sha256: str,
    expected_glb_sha256: str, positions_cache: dict[tuple[Path, str], tuple[list[tuple[float, float, float]], dict[str, Any]]],
) -> dict[str, Any]:
    cache_key = (glb_path, source_fj_id)
    if cache_key not in positions_cache:
        positions_cache[cache_key] = read_glb_positions(glb_path, source_fj_id)
    actual, glb_meta = positions_cache[cache_key]
    source = read_obj_vertices(obj_path)
    expected = [
        tuple(struct.unpack("<3f", struct.pack("<3f", x / 1000.0, z / 1000.0, -y / 1000.0)))
        for x, y, z in source
    ]
    count_matches = len(source) == len(actual)
    max_abs_delta = max(
        (abs(expected[i][axis] - actual[i][axis]) for i in range(min(len(expected), len(actual))) for axis in range(3)),
        default=math.inf,
    )
    identity = glb_meta["nodeTransformIdentity"]
    source_hash_matches = glb_meta["sourceSha256"] == expected_obj_sha256
    glb_hash_matches = glb_meta["glbSha256"] == expected_glb_sha256
    metadata_matches = (
        glb_meta["sourceFrame"] == "native BodyParts3D R4 static reference; not registered to OpenSim"
        and glb_meta["projectFrame"] == EXPECTED_FRAME
        and glb_meta["transform"] in {
            EXPECTED_TRANSFORM,
            "[x,y,z]mm -> [x,z,-y]m; no reflection or mirroring",
        }
    )
    return {
        **glb_meta,
        "objPath": str(obj_path),
        "objSha256": sha256_file(obj_path),
        "expectedObjSha256": expected_obj_sha256,
        "expectedGlbSha256": expected_glb_sha256,
        "sourceHashMatches": source_hash_matches,
        "glbHashMatchesManifest": glb_hash_matches,
        "metadataMatchesTransformContract": metadata_matches,
        "objVertexCount": len(source),
        "vertexCountMatches": count_matches,
        "maxAbsoluteVertexDeltaM": round(max_abs_delta, 12) if math.isfinite(max_abs_delta) else None,
        "float32VertexPositionsMatch": count_matches and max_abs_delta == 0.0,
        "nodeTransformIdentity": identity,
        "passed": source_hash_matches and glb_hash_matches and metadata_matches and count_matches and max_abs_delta == 0.0 and identity,
    }


def read_glb_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if len(raw) < 20:
        raise DiagnosticError(f"GLB is too short: {path}")
    magic, version, declared_length = struct.unpack_from("<4sII", raw, 0)
    if magic != b"glTF" or version != 2 or declared_length != len(raw):
        raise DiagnosticError(f"Invalid GLB 2 header or byte length: {path}")
    offset = 12
    while offset < len(raw):
        if offset + 8 > len(raw):
            raise DiagnosticError(f"Truncated GLB chunk header: {path}")
        chunk_length, chunk_type = struct.unpack_from("<II", raw, offset)
        offset += 8
        chunk = raw[offset:offset + chunk_length]
        if len(chunk) != chunk_length:
            raise DiagnosticError(f"Truncated GLB chunk: {path}")
        offset += chunk_length
        if chunk_type == 0x4E4F534A:
            return json.loads(chunk.decode("utf-8").rstrip(" \t\r\n\0"))
    raise DiagnosticError(f"GLB JSON chunk not found: {path}")


def verify_t52_frozen_package(project_root: Path, manifest: dict[str, Any], acquisition: dict[str, Any]) -> dict[str, Any]:
    assets_by_id = {row["sourceElementFileId"]: row for row in manifest["sourceAssets"]}
    acquired_by_id = {row["sourceElementFileId"]: row for row in acquisition["selectedSourceFiles"]}
    expected_ids = set(assets_by_id)
    source_hash_checks = []
    for fj_id in sorted(expected_ids):
        asset = assets_by_id[fj_id]
        acquired = acquired_by_id.get(fj_id)
        if acquired is None:
            raise DiagnosticError(f"Frozen package lacks acquisition row: {fj_id}")
        source_path = project_root / acquired["cacheRelativePath"]
        if not source_path.is_file():
            raise DiagnosticError(f"Missing frozen source OBJ: {fj_id}")
        actual_hash = sha256_file(source_path)
        actual_bytes = source_path.stat().st_size
        ok = actual_hash == acquired["sha256"] == asset["sourceSha256"] and actual_bytes == acquired["bytes"] == asset["sourceBytes"]
        source_hash_checks.append({"sourceElementFileId": fj_id, "passed": ok, "sha256": actual_hash, "bytes": actual_bytes})
        if not ok:
            raise DiagnosticError(f"Frozen source OBJ hash/size mismatch: {fj_id}")

    batch_checks = []
    for batch in manifest["internalBatches"]:
        glb_path = project_root / batch["glbPath"]
        if not glb_path.is_file():
            raise DiagnosticError(f"Missing frozen QA GLB: {batch['batchId']}")
        glb_hash = sha256_file(glb_path)
        glb_json = read_glb_json(glb_path)
        actual_ids = [node.get("extras", {}).get("sourceFileId") for node in glb_json.get("nodes", [])]
        source_set_matches = sorted(actual_ids) == sorted(batch["sourceElementFileIds"]) and len(actual_ids) == len(set(actual_ids))
        nodes_match_sources = all(
            node.get("extras", {}).get("sourceSha256") == assets_by_id[node["extras"]["sourceFileId"]]["sourceSha256"]
            for node in glb_json.get("nodes", [])
            if node.get("extras", {}).get("sourceFileId") in assets_by_id
        )
        passed = (
            glb_hash == batch["glbSha256"] and glb_path.stat().st_size == batch["glbBytes"]
            and source_set_matches and nodes_match_sources
            and len(actual_ids) == batch["meshCount"]
            and not glb_json.get("animations") and not glb_json.get("skins")
        )
        batch_checks.append({
            "batchId": batch["batchId"], "glbPath": batch["glbPath"], "glbSha256": glb_hash,
            "glbBytes": glb_path.stat().st_size, "meshCount": len(actual_ids),
            "sourceIdsMatchBatch": source_set_matches, "nodeSourceHashesMatchManifest": nodes_match_sources,
            "noAnimationsOrSkins": not glb_json.get("animations") and not glb_json.get("skins"), "passed": passed,
        })
        if not passed:
            raise DiagnosticError(f"Frozen QA GLB integrity mismatch: {batch['batchId']}")
    return {
        "frozenSourceAssetCount": len(expected_ids), "acquisitionAssetCount": len(acquired_by_id),
        "all85SourceObjHashesAndSizesMatch": len(source_hash_checks) == 85 and all(row["passed"] for row in source_hash_checks),
        "sourceObjChecks": source_hash_checks,
        "qaBatchCount": len(batch_checks), "all9InternalQaGlbChecksPass": len(batch_checks) == 9 and all(row["passed"] for row in batch_checks),
        "qaBatches": batch_checks, "canonicalBindings": manifest["scope"]["canonicalStableLearnerBindings"],
        "sourceOnlyAssets": manifest["scope"]["sourceOnlyMeshAssets"], "passed": len(source_hash_checks) == 85 and len(batch_checks) == 9 and all(row["passed"] for row in batch_checks),
    }


def triangle_area(a: tuple[float, float, float], b: tuple[float, float, float], c: tuple[float, float, float]) -> float:
    ab = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    ac = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    cross = (ab[1] * ac[2] - ab[2] * ac[1], ab[2] * ac[0] - ab[0] * ac[2], ab[0] * ac[1] - ab[1] * ac[0])
    return math.sqrt(sum(x * x for x in cross)) / 2.0


def clipped_triangle_area(triangle: tuple[tuple[float, float, float], ...], *, keep_positive: bool) -> float:
    """Return exact planar-triangle area clipped by x>=0 or x<=0."""
    poly: list[tuple[float, float, float]] = list(triangle)
    clipped: list[tuple[float, float, float]] = []
    for i, current in enumerate(poly):
        previous = poly[i - 1]
        cur_inside = current[0] >= 0 if keep_positive else current[0] <= 0
        prev_inside = previous[0] >= 0 if keep_positive else previous[0] <= 0
        if cur_inside != prev_inside:
            denom = current[0] - previous[0]
            t = 0.0 if denom == 0 else -previous[0] / denom
            clipped.append(tuple(previous[j] + t * (current[j] - previous[j]) for j in range(3)))
        if cur_inside:
            clipped.append(current)
    if len(clipped) < 3:
        return 0.0
    return sum(triangle_area(clipped[0], clipped[i], clipped[i + 1]) for i in range(1, len(clipped) - 1))


def load_tsv(path: Path) -> list[list[str]]:
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_indexes(project_root: Path, t51: dict[str, Any]) -> dict[str, Any]:
    paths = {entry["logicalName"]: project_root / entry["path"] for entry in t51["source"]["metadataFiles"]}
    expected = {entry["logicalName"]: entry for entry in t51["source"]["metadataFiles"]}
    metadata_hashes = {}
    for logical_name, path in paths.items():
        if not path.is_file():
            raise DiagnosticError(f"Missing T51 source metadata: {path}")
        actual = sha256_file(path)
        wanted = expected[logical_name]["sha256"]
        if actual != wanted:
            raise DiagnosticError(f"T51 source metadata hash mismatch: {logical_name}")
        metadata_hashes[logical_name] = {"path": str(path.relative_to(project_root)), "sha256": actual, "bytes": path.stat().st_size}

    concepts: dict[str, dict[str, dict[str, str]]] = {"IS-A": {}, "PART-OF": {}}
    for tree, key in (("IS-A", "isaConcepts"), ("PART-OF", "partofConcepts")):
        for row in load_tsv(paths[key]):
            if len(row) < 3:
                raise DiagnosticError(f"Malformed {key} metadata row")
            concepts[tree][row[0]] = {"conceptId": row[0], "representationId": row[1], "englishName": row[2]}

    element_rows: dict[str, list[dict[str, str]]] = {"IS-A": [], "PART-OF": []}
    for tree, key in (("IS-A", "isaCompoundElements"), ("PART-OF", "partofCompoundElements")):
        element_rows[tree] = [
            {"conceptId": row[0], "conceptName": row[1], "elementFileId": row[2]}
            for row in load_tsv(paths[key]) if len(row) >= 3
        ]
    is_a_edges = [
        {"parentId": r[0], "parentName": r[1], "childId": r[2], "childName": r[3]}
        for r in load_tsv(paths["isaInclusion"]) if len(r) >= 4
    ]
    return {"concepts": concepts, "elements": element_rows, "isAEdges": is_a_edges, "metadataHashes": metadata_hashes}


def source_frame_transform(point: Iterable[float]) -> tuple[float, float, float]:
    x, y, z = point
    return (x / 1000.0, z / 1000.0, -y / 1000.0)


def expected_laterality_fraction(metrics: MeshMetrics, laterality: str) -> float:
    if laterality not in {"left", "right"}:
        raise DiagnosticError(f"Source laterality must be explicitly left/right, got: {laterality!r}")
    total = metrics.total_surface_area_mm2
    if total <= 0:
        return 0.0
    # BodyParts3D's official coordinate diagram: x>0 is subject's left, x<0 right.
    expected_area = metrics.positive_x_surface_area_mm2 if laterality == "left" else metrics.negative_x_surface_area_mm2
    return expected_area / total


def bounds_center_side_diagnostic(metrics: MeshMetrics) -> str:
    """Report the raw source AABB center side without interpreting it as a verdict."""
    center_x = (metrics.bounds_min_mm[0] + metrics.bounds_max_mm[0]) / 2.0
    return "positive_x" if center_x > 0 else "negative_x" if center_x < 0 else "on_plane"


def validate_assessment(assessment: dict[str, Any], target_ids: set[str]) -> dict[str, dict[str, Any]]:
    if assessment.get("revision") != "T69-SOURCE-VS-GEOMETRY-ASSESSMENT-v1":
        raise DiagnosticError("Unexpected T69 assessment revision")
    records = assessment.get("records")
    if not isinstance(records, list):
        raise DiagnosticError("T69 assessment records must be an array")
    by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        fj_id = record.get("sourceElementFileId")
        if not isinstance(fj_id, str) or fj_id in by_id:
            raise DiagnosticError(f"Missing or duplicate T69 assessment FJ ID: {fj_id!r}")
        required_fields = {"aiConclusion", "unresolvedReason", "humanReview", "learnerUse", "evidenceRefs"}
        if not required_fields.issubset(record):
            raise DiagnosticError(f"Incomplete T69 assessment record: {fj_id}")
        if not isinstance(record["aiConclusion"], dict) or not record["aiConclusion"].get("code") or not record["aiConclusion"].get("text"):
            raise DiagnosticError(f"Missing AI conclusion code/text: {fj_id}")
        human = record["humanReview"]
        if human.get("status") != "not_performed" or human.get("promoted") is not False:
            raise DiagnosticError(f"T69 may not report/promotion human review: {fj_id}")
        learner = record["learnerUse"]
        if learner.get("status") != "source_only_held" or learner.get("canonicalBinding") is not None:
            raise DiagnosticError(f"T69 assessment may not create learner/canonical release: {fj_id}")
        if record["aiConclusion"].get("correctionAction") not in {"none", "hold_for_source_identity_adjudication"}:
            raise DiagnosticError(f"Unsupported corrective action in T69 assessment: {fj_id}")
        by_id[fj_id] = record
    if set(by_id) != target_ids:
        missing = sorted(target_ids - set(by_id))
        extra = sorted(set(by_id) - target_ids)
        raise DiagnosticError(f"T69 assessment ID set mismatch; missing={missing}, extra={extra}")
    source_ids = {source.get("id") for source in assessment.get("sources", [])}
    for fj_id, record in by_id.items():
        if not record["evidenceRefs"] or not set(record["evidenceRefs"]).issubset(source_ids):
            raise DiagnosticError(f"Invalid/empty evidenceRefs in T69 assessment: {fj_id}")
    return by_id


def source_identity_matches(header: dict[str, str], *, fj_id: str, fma_id: str, bp_id: str, english_name: str) -> bool:
    return all(header.get(key) == value for key, value in (
        ("fileId", fj_id), ("conceptId", fma_id), ("representationId", bp_id), ("englishName", english_name)
    ))


def frame_contract_matches(frame: str, transform: str) -> bool:
    return frame == EXPECTED_FRAME and transform == EXPECTED_TRANSFORM


def split_side_name(name: str) -> tuple[str | None, str]:
    match = re.match(r"^(left|right)\s+(.+)$", name.strip(), flags=re.IGNORECASE)
    return (match.group(1).lower(), match.group(2).lower()) if match else (None, name.strip().lower())


def find_official_bilateral_counterpart(
    concept_id: str,
    name: str,
    is_a_edges: list[dict[str, str]],
    assets_by_concept: dict[str, list[dict[str, Any]]],
    element_rows_by_tree: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    side, base_name = split_side_name(name)
    if side is None:
        return {"status": "source_concept_has_no_explicit_left_right_prefix", "concepts": []}
    opposite = "right" if side == "left" else "left"
    parents = [edge for edge in is_a_edges if edge["childId"] == concept_id]
    found: list[dict[str, Any]] = []
    for parent in parents:
        for child in is_a_edges:
            child_side, child_base = split_side_name(child["childName"])
            if child["parentId"] != parent["parentId"] or child_side != opposite or child_base != base_name:
                continue
            mapped_assets = assets_by_concept.get(child["childId"], [])
            element_file_ids = sorted({
                element["elementFileId"]
                for rows in element_rows_by_tree.values()
                for element in rows
                if element["conceptId"] == child["childId"]
            })
            found.append({
                "parentConceptId": parent["parentId"], "parentConceptName": parent["parentName"],
                "counterpartConceptId": child["childId"], "counterpartConceptName": child["childName"],
                "counterpartFjElementIds": element_file_ids,
                "counterpartAssetsInT52FrozenPackage": [item["sourceElementFileId"] for item in mapped_assets],
                "counterpartSourceNames": [item["sourceName"] for item in mapped_assets],
            })
    if not found:
        return {"status": "no_explicit_opposite_side_sibling_in_frozen_source_index", "sourceSide": side, "sourceConceptName": name, "concepts": []}
    return {"status": "official_source_index_opposite_side_relation_found", "sourceSide": side, "sourceConceptName": name, "concepts": found}


def build_diagnostic(project_root: Path, manifest_path: Path, t51_path: Path, assessment_path: Path, output_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    t51 = json.loads(t51_path.read_text(encoding="utf-8"))
    assessment = json.loads(assessment_path.read_text(encoding="utf-8"))
    indexes = load_indexes(project_root, t51)
    acquisition_path = project_root / manifest["sourceAcquisitionPath"]
    acquisition = json.loads(acquisition_path.read_text(encoding="utf-8"))
    frozen_package_integrity = verify_t52_frozen_package(project_root, manifest, acquisition)
    acquired = {row["sourceElementFileId"]: row for row in acquisition["selectedSourceFiles"]}
    by_fj = {row["sourceElementFileId"]: row for row in manifest["sourceAssets"]}
    by_diag = {row["sourceElementFileId"]: row for row in manifest["lateralityBoundsDiagnostics"]}
    assessment_by_id = validate_assessment(assessment, set(by_diag))
    assets_by_concept: dict[str, list[dict[str, Any]]] = {}
    for row in manifest["sourceAssets"]:
        assets_by_concept.setdefault(row["sourceConceptId"], []).append(row)
    pair_metric_cache: dict[str, MeshMetrics] = {}
    glb_by_batch = {row["batchId"]: row for row in manifest["internalBatches"]}
    glb_position_cache: dict[tuple[Path, str], tuple[list[tuple[float, float, float]], dict[str, Any]]] = {}
    target_glb_checks: list[dict[str, Any]] = []

    def measure_frozen_pair_mesh(fj: str) -> dict[str, Any]:
        pair_asset = by_fj.get(fj)
        pair_acquired = acquired.get(fj)
        if pair_asset is None or pair_acquired is None:
            return {"sourceElementFileId": fj, "availability": "not_in_t52_frozen_85_meshes", "downloadAttempted": False}
        pair_path = project_root / pair_acquired["cacheRelativePath"]
        if fj not in pair_metric_cache:
            pair_metrics = parse_obj(pair_path)
            if pair_metrics.source_sha256 != pair_acquired["sha256"] or pair_metrics.source_sha256 != pair_asset["sourceSha256"]:
                raise DiagnosticError(f"Bilateral comparison OBJ hash mismatch: {fj}")
            pair_metric_cache[fj] = pair_metrics
        pair_metrics = pair_metric_cache[fj]
        expected_fraction = expected_laterality_fraction(pair_metrics, pair_asset["laterality"])
        total = pair_metrics.total_surface_area_mm2
        return {
            "sourceElementFileId": fj, "availability": "measured_from_existing_t52_frozen_mesh",
            "sourceConceptId": pair_asset["sourceConceptId"], "sourceRepresentationId": pair_asset["sourceRepresentationId"],
            "sourceName": pair_asset["sourceName"], "sourceLaterality": pair_asset["laterality"],
            "sourceSha256": pair_metrics.source_sha256, "vertices": pair_metrics.vertex_count,
            "trianglesFanTriangulated": pair_metrics.triangle_count, "connectedComponents": pair_metrics.component_count,
            "boundsMinMm": pair_metrics.bounds_min_mm, "boundsMaxMm": pair_metrics.bounds_max_mm,
            "surfaceBoundsMinMm": pair_metrics.surface_bounds_min_mm, "surfaceBoundsMaxMm": pair_metrics.surface_bounds_max_mm,
            "surfaceAreaOnSourceLabeledSideFraction": round(expected_fraction, 8),
            "surfaceAreaOppositeSourceLabelFraction": round(1 - expected_fraction, 8),
            "surfaceAreaNegativeXFraction": round(pair_metrics.negative_x_surface_area_mm2 / total, 8) if total else 0.0,
            "surfaceAreaPositiveXFraction": round(pair_metrics.positive_x_surface_area_mm2 / total, 8) if total else 0.0,
            "sourceLabel": pair_asset["sourceName"],
        }

    # T52 frame claims are checked against official source coordinate documentation,
    # unchanged source vertices, and generated package bounds. This is not an assertion
    # that BodyParts3D is a universal, clinically approved canonical model.
    source_points = ((-1.0, 2.0, 3.0), (10.0, -20.0, 30.0), (0.0, 0.0, 0.0))
    transformed = [source_frame_transform(p) for p in source_points]
    transform_preserves_lateral_sign = all((p[0] == 0 and q[0] == 0) or (p[0] * q[0] > 0) for p, q in zip(source_points, transformed))
    transform_has_expected_units = transformed[1] == (0.01, 0.03, 0.02)
    region_transform_checks = []
    all_transform_ok = True
    for row in manifest["sourceAssets"]:
        src = row["sourceVertexBounds"]
        atlas = row["atlasBounds"]
        expected_min = source_frame_transform(src["min"])
        expected_max = source_frame_transform(src["max"])
        lo = [min(expected_min[i], expected_max[i]) for i in range(3)]
        hi = [max(expected_min[i], expected_max[i]) for i in range(3)]
        delta = max(abs(lo[i] - atlas["min"][i]) for i in range(3)) + max(abs(hi[i] - atlas["max"][i]) for i in range(3))
        ok = frame_contract_matches(row["framePose"]["projectFrame"], row["framePose"]["transform"]) and delta <= 1e-9
        all_transform_ok = all_transform_ok and ok
        region_transform_checks.append({"sourceElementFileId": row["sourceElementFileId"], "passed": ok, "maxBoundDeltaM": round(delta, 12)})

    target_rows = []
    for fj, diag in sorted(by_diag.items()):
        asset = by_fj[fj]
        acquisition_row = acquired[fj]
        source_path = project_root / acquisition_row["cacheRelativePath"]
        if not source_path.is_file():
            raise DiagnosticError(f"Missing T52 source OBJ: {source_path}")
        metrics = parse_obj(source_path)
        if metrics.source_sha256 != acquisition_row["sha256"] or metrics.source_sha256 != asset["sourceSha256"]:
            raise DiagnosticError(f"Source OBJ hash mismatch: {fj}")
        batch = glb_by_batch.get(asset["batchId"])
        if batch is None or asset["qaGlbPath"] != batch["glbPath"]:
            raise DiagnosticError(f"Target source does not resolve to its frozen T52 QA GLB: {fj}")
        glb_path = project_root / batch["glbPath"]
        glb_check = compare_obj_to_glb_transform(
            source_path, glb_path, fj, metrics.source_sha256, batch["glbSha256"], glb_position_cache
        )
        target_glb_checks.append({**glb_check, "batchId": asset["batchId"]})
        if not glb_check["passed"]:
            raise DiagnosticError(f"Actual OBJ→GLB vertex transform check failed: {fj}: {json.dumps(glb_check, ensure_ascii=False)}")
        header = metrics.header
        header_ok = source_identity_matches(
            header, fj_id=fj, fma_id=asset["sourceConceptId"],
            bp_id=asset["sourceRepresentationId"], english_name=asset["sourceName"]
        )
        tree = asset["sourceArchiveTree"]
        concept_row = indexes["concepts"][tree].get(asset["sourceConceptId"])
        concept_ok = concept_row == {"conceptId": asset["sourceConceptId"], "representationId": asset["sourceRepresentationId"], "englishName": asset["sourceName"].lower()}
        element_evidence = []
        for relation_tree, rows in indexes["elements"].items():
            for edge in rows:
                if edge["elementFileId"] == fj:
                    element_evidence.append({**edge, "tree": relation_tree})
        exact_element_binding = any(e["conceptId"] == asset["sourceConceptId"] and e["tree"] == tree for e in element_evidence)
        bilateral_pair = find_official_bilateral_counterpart(
            asset["sourceConceptId"], asset["sourceName"], indexes["isAEdges"], assets_by_concept, indexes["elements"]
        )
        for pair_concept in bilateral_pair.get("concepts", []):
            pair_concept["measuredFjElements"] = [measure_frozen_pair_mesh(pair_fj) for pair_fj in pair_concept["counterpartFjElementIds"]]
        laterality = asset["laterality"]
        expected_fraction = expected_laterality_fraction(metrics, laterality)
        opposite_fraction = 1.0 - expected_fraction
        volume = float(header.get("volumeCm3", "nan"))
        total_area = metrics.total_surface_area_mm2
        negative_fraction = metrics.negative_x_surface_area_mm2 / total_area if total_area else 0.0
        positive_fraction = metrics.positive_x_surface_area_mm2 / total_area if total_area else 0.0
        exact_plane_fraction = metrics.exact_plane_surface_area_mm2 / total_area if total_area else 0.0
        relation_parent_rows = [edge for edge in indexes["isAEdges"] if edge["childId"] == asset["sourceConceptId"]]
        bounds_source = asset["sourceVertexBounds"]
        actual_bounds_match = max(abs(metrics.bounds_min_mm[i] - bounds_source["min"][i]) for i in range(3)) <= 0.000001 and max(abs(metrics.bounds_max_mm[i] - bounds_source["max"][i]) for i in range(3)) <= 0.000001
        header_numbers = [float(v) for v in re.findall(r"[-+]?\d+(?:\.\d+)?", header.get("boundsMm", ""))]
        header_bounds_match = len(header_numbers) == 6 and max(abs(header_numbers[i] - metrics.bounds_min_mm[i]) for i in range(3)) <= 0.0001 and max(abs(header_numbers[i + 3] - metrics.bounds_max_mm[i]) for i in range(3)) <= 0.0001
        ai_record = assessment_by_id[fj]
        target_rows.append({
            "sourceLabel": {
                "sourceElementFileId": fj, "sourceConceptId": asset["sourceConceptId"],
                "sourceRepresentationId": asset["sourceRepresentationId"], "sourceLaterality": laterality,
                "objEnglishName": header.get("englishName"), "objHeaderLicense": asset["sourceHeaderLicense"],
                "t52Status": asset["lateralityBoundsDiagnostic"], "stableSourceMeshId": asset["stableMeshAssetId"],
            },
            "identityEvidence": {
                "objHeaderMatchesFjFmaBpName": header_ok, "bodypartsIndexConceptRowMatches": concept_ok,
                "officialFjElementRelationIncludesSourceConcept": exact_element_binding,
                "fmaElementRows": element_evidence,
                "directIsAParentRows": relation_parent_rows,
                "note": "OBJ header and BodyParts3D index are same-source identity lineage, not independent corroboration.",
            },
            "bilateralComparison": bilateral_pair,
            "geometryObservation": {
                "sourcePath": str(source_path.relative_to(project_root)), "sourceSha256": metrics.source_sha256,
                "sourceBytes": metrics.source_bytes, "rawObjBoundsMinMm": metrics.bounds_min_mm,
                "rawObjBoundsMaxMm": metrics.bounds_max_mm, "rawObjVertexCentroidMm": metrics.centroid_mm,
                "boundsCenterXSideDiagnosticOnly": bounds_center_side_diagnostic(metrics),
                "boundsCenterXDiagnosticOnlyMm": round((metrics.bounds_min_mm[0] + metrics.bounds_max_mm[0]) / 2.0, 6),
                "rawObjHeaderBounds": header.get("boundsMm"), "headerBoundsMatchActualExtremaWithinT52Precision": header_bounds_match,
                "actualVertexBoundsMatchT52Manifest": actual_bounds_match,
                "vertices": metrics.vertex_count, "polygonFaces": metrics.polygon_face_count,
                "verticesReferencedByFaces": metrics.surface_vertex_count,
                "unreferencedOrphanVertices": metrics.orphan_vertex_count,
                "orphanVerticesByXSignOutsideQuantizationBand": {
                    "negativeX": metrics.orphan_negative_x_vertex_count,
                    "withinPlusMinus001mm": metrics.orphan_near_plane_vertex_count,
                    "positiveX": metrics.orphan_positive_x_vertex_count,
                    "quantizationBandMm": metrics.near_plane_band_mm,
                },
                "surfaceBoundsFromFaceReferencedVerticesMinMm": metrics.surface_bounds_min_mm,
                "surfaceBoundsFromFaceReferencedVerticesMaxMm": metrics.surface_bounds_max_mm,
                "trianglesFanTriangulated": metrics.triangle_count, "sourceHeaderVolumeCm3": volume,
                "connectedComponents": metrics.component_count, "components": metrics.components,
                "surfaceAreaNegativeXmm2": metrics.negative_x_surface_area_mm2,
                "surfaceAreaExactlyOnPlaneMm2": metrics.exact_plane_surface_area_mm2,
                "surfaceAreaPositiveXmm2": metrics.positive_x_surface_area_mm2,
                "totalSurfaceAreaMm2": metrics.total_surface_area_mm2,
                "surfaceAreaNegativeXFraction": round(negative_fraction, 8),
                "surfaceAreaExactlyOnPlaneFraction": round(exact_plane_fraction, 8),
                "surfaceAreaPositiveXFraction": round(positive_fraction, 8),
                "surfaceAreaOnSourceLabeledSideFraction": round(expected_fraction, 8),
                "surfaceAreaOppositeSourceLabelFraction": round(opposite_fraction, 8),
                "verticesByXSignOutsideQuantizationBand": {
                    "negativeX": metrics.negative_x_vertex_count,
                    "withinPlusMinus001mm": metrics.near_plane_vertex_count,
                    "positiveX": metrics.positive_x_vertex_count,
                    "quantizationBandMm": metrics.near_plane_band_mm,
                    "quantizationBandBasis": "T50 records 0.001 mm source-coordinate quantization for geometry comparison; diagnostic only, not anatomy threshold.",
                },
                "boundsCrossExactSourceMedianPlane": metrics.bounds_min_mm[0] <= 0 <= metrics.bounds_max_mm[0],
                "surfaceBoundsCrossExactSourceMedianPlane": metrics.surface_bounds_min_mm[0] <= 0 <= metrics.surface_bounds_max_mm[0],
                "metricCaveat": "AABB, vertex fractions, component centroids, and shape similarity are observations; no single one establishes anatomical side.",
            },
            "transformObservation": {
                "sourceFrame": "BodyParts3D R4 native; not registered to OpenSim",
                "sourceUnit": "mm as used by release coordinate note and OBJ bounds; project unit m",
                "transform": EXPECTED_TRANSFORM, "projectFrame": EXPECTED_FRAME,
                "xSignPreserved": transform_preserves_lateral_sign,
                "projectBoundsMatchTransformedSourceBounds": next(x["passed"] for x in region_transform_checks if x["sourceElementFileId"] == fj),
            },
            "aiConclusion": ai_record["aiConclusion"],
            "unresolvedReason": ai_record["unresolvedReason"],
            "humanReview": ai_record["humanReview"],
            "learnerUse": ai_record["learnerUse"],
            "evidenceRefs": ai_record["evidenceRefs"],
        })

    frame_anchor_pairs = [
        {"name": "inferior oblique", "sourceElementFileIds": ["FJ1294", "FJ1345"]},
        {"name": "superior rectus", "sourceElementFileIds": ["FJ1323", "FJ1374"]},
    ]
    for pair in frame_anchor_pairs:
        pair["measurements"] = [measure_frozen_pair_mesh(fj) for fj in pair["sourceElementFileIds"]]

    legacy_opposition_ids = sorted(
        row["sourceElementFileId"] for row in manifest["lateralityBoundsDiagnostics"]
        if row["status"].startswith("bounds_center_opposes_source_name")
    )
    legacy_crossing_ids = sorted(
        row["sourceElementFileId"] for row in manifest["lateralityBoundsDiagnostics"]
        if row["bounds"]["min"][0] <= 0 <= row["bounds"]["max"][0]
    )
    legacy_target_ids = sorted(set(legacy_opposition_ids) | set(legacy_crossing_ids))
    result = {
        "revision": "T69-BODYPARTS3D-R4-T52-LATERALITY-DIAGNOSTIC-v1",
        "scope": {"frozenSourceFjCount": len(manifest["sourceAssets"]), "uniqueDiagnosticTargetCount": len(target_rows), "sourceIds": [r["sourceLabel"]["sourceElementFileId"] for r in target_rows], "historicalT52ManifestSha256": sha256_file(manifest_path), "frozenMembershipSha256": manifest["frozenMembershipSha256"], "noSourceFilesModified": True},
        "historicalT52DiagnosticSet": {
            "sourceManifestPreserved": True,
            "boundsCenterOppositionCount": len(legacy_opposition_ids), "boundsCenterOppositionFjIds": legacy_opposition_ids,
            "aabbMedianCrossingCount": len(legacy_crossing_ids), "aabbMedianCrossingFjIds": legacy_crossing_ids,
            "crossingsBeyondTwoOverlappingOppositionCasesCount": len(set(legacy_crossing_ids) - set(legacy_opposition_ids)),
            "uniqueRevalidationTargetCount": len(legacy_target_ids), "uniqueRevalidationTargetFjIds": legacy_target_ids,
            "interpretation": "Historical T52 flags are preserved as input labels for this revalidation; none is treated as an anatomy verdict.",
        },
        "sourceEvidence": {
            "assessmentPath": str(assessment_path.relative_to(project_root)), "assessmentSha256": sha256_file(assessment_path),
            "t51ManifestPath": str(t51_path.relative_to(project_root)), "t51ManifestSha256": sha256_file(t51_path),
            "t52ManifestPath": str(manifest_path.relative_to(project_root)), "t52AcquisitionPath": str(acquisition_path.relative_to(project_root)),
            "officialBodyPartsMetadata": indexes["metadataHashes"],
            "officialCoordinateDiagram": SOURCE_COORDINATE_IMAGE,
            "officialReleaseNote": SOURCE_RELEASE_NOTE,
            "officialReadme": SOURCE_README,
        },
        "globalFrameVerification": {
            "sourceCoordinateConvention": {"lengthUnit": "mm", "xPositive": "subject left", "xNegative": "subject right", "yPositive": "posterior", "yNegative": "anterior", "z": "superior increases; whole-body centerline approximately parallel to z"},
            "coordinateBasis": "Official BodyParts3D Release 4.0 coordinate-system diagram; T51/T52 source index and OBJ identity remain same-source records.",
            "projectTransform": EXPECTED_TRANSFORM, "projectFrame": EXPECTED_FRAME,
            "testVectorSourceMm": source_points, "testVectorProjectM": transformed,
            "transformPreservesLateralSign": transform_preserves_lateral_sign,
            "transformUnitAndAxisPermutationCorrect": transform_has_expected_units,
            "all85BoundsAgreeWithTransform": all_transform_ok,
            "t52FrozenPackageIntegrity": frozen_package_integrity,
            "perMeshBoundChecks": region_transform_checks,
            "targetObjToGlbVertexChecks": target_glb_checks,
            "all17ObjToGlbVertexChecksPass": len(target_glb_checks) == 17 and all(row["passed"] for row in target_glb_checks),
            "bilateralFrameAnchorPairs": frame_anchor_pairs,
            "anchorPairEvidenceLimit": "Pair geometry corroborates the source x-axis sign within BodyParts3D; it is not independent of that dataset and does not validate a particular pharyngeal mesh label.",
            "status": "technically_consistent" if transform_preserves_lateral_sign and transform_has_expected_units and all_transform_ok else "unverified_or_defective",
            "scopeLimit": "Confirms this T52 package's recorded BodyParts3D frame/axis mapping and generated bounds; not a canonical pose assertion or anatomy/label correctness certification.",
        },
        "interpretationPolicy": {
            "sourceSideRule": "BodyParts3D coordinate diagram states x>0 left and x<0 right; the central axis is approximate, so x=0 crossing is an observation.",
            "noSingleMetricIsGroundTruth": True,
            "noRecenterMirrorOrLabelSwap": True,
            "noHumanReviewPromotion": True,
            "surfaceAreaMethod": "Fan triangulate OBJ polygons, then clip each triangle against exact source plane x=0 and sum mm^2 on each side.",
            "surfaceAreaIsTessellationLessBiasedThanVertexCounts": True,
        },
        "diagnostics": target_rows,
        "outputPath": str(output_path.relative_to(project_root)),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--t52-manifest", type=Path, default=T52_MANIFEST)
    parser.add_argument("--t51-manifest", type=Path, default=T51_MANIFEST)
    parser.add_argument("--assessment", type=Path, default=DEFAULT_ASSESSMENT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    project_root = args.root.resolve()
    manifest_path = (project_root / args.t52_manifest).resolve() if not args.t52_manifest.is_absolute() else args.t52_manifest
    t51_path = (project_root / args.t51_manifest).resolve() if not args.t51_manifest.is_absolute() else args.t51_manifest
    assessment_path = (project_root / args.assessment).resolve() if not args.assessment.is_absolute() else args.assessment
    output_path = (project_root / args.output).resolve() if not args.output.is_absolute() else args.output
    try:
        result = build_diagnostic(project_root, manifest_path, t51_path, assessment_path, output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (DiagnosticError, KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps({
        "status": result["globalFrameVerification"]["status"],
        "globalFrameBoundsChecks": len(result["globalFrameVerification"]["perMeshBoundChecks"]),
        "diagnosticTargets": len(result["diagnostics"]),
        "historicalOppositionCount": result["historicalT52DiagnosticSet"]["boundsCenterOppositionCount"],
        "historicalAabbCrossingCount": result["historicalT52DiagnosticSet"]["aabbMedianCrossingCount"],
        "uniqueRevalidationTargetCount": result["historicalT52DiagnosticSet"]["uniqueRevalidationTargetCount"],
        "identityMismatches": [r["sourceLabel"]["sourceElementFileId"] for r in result["diagnostics"] if not all(r["identityEvidence"][k] for k in ("objHeaderMatchesFjFmaBpName", "bodypartsIndexConceptRowMatches", "officialFjElementRelationIncludesSourceConcept"))],
        "output": str(output_path),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
