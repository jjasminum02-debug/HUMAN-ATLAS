#!/usr/bin/env python3
"""Build and validate the frozen T53 BodyParts3D trunk/pelvis source package."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "work/evidence/T53/frozen-source-set.json"
ACQUISITION = ROOT / "work/evidence/T53/source-acquisition.json"
T51_MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json"
REGION_ROOT = ROOT / "atlas-data/manifests/bodyparts3d-r4-regions-t51"
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
OUT_ROOT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t53"
GLB_ROOT = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t53"
OUT_GLB = GLB_ROOT / "T53-trunk-pelvis-static-source.glb"
OUT_MANIFEST = OUT_ROOT / "source-manifest.json"
OUT_VALIDATION = ROOT / "work/evidence/T53/validation.json"
REGIONS = ("back", "thorax", "abdomen-lumbar", "pelvis-perineum", "gluteal-hip")
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
SOURCE_VERSION = "BodyParts3D Release 4.0"
MODEL_ID = "HA-MODEL-BP3D4-T53-TRUNK-PELVIS-QA"
ATTRIBUTION = "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International"
FJ_ID = re.compile(r"^FJ[0-9]+M?$")
BOUNDS = re.compile(r"^#\s*Bounds\(mm\):\s*\(([^)]+)\)-\(([^)]+)\)\s*$")


class PackageError(RuntimeError):
    pass


def module_at(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise PackageError(f"could not load validated T51/T07 helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INGEST = module_at("ha_t53_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
CONVERT = module_at("ha_t53_converter", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")


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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_header(path: Path) -> dict[str, Any]:
    header = INGEST.read_obj_header(path)
    header.update({"englishName": None, "boundsMm": None, "volumeCm3": None})
    with path.open("r", encoding="utf-8", errors="replace") as stream:
        for raw in stream:
            if not raw.startswith("#"):
                break
            line = raw.lstrip("# ").strip()
            if line.startswith("English name :"):
                header["englishName"] = line.split(":", 1)[1].strip() or None
            match = BOUNDS.match(raw.rstrip("\r\n"))
            if match:
                low = [float(x.strip()) for x in match.group(1).split(",")]
                high = [float(x.strip()) for x in match.group(2).split(",")]
                if len(low) != 3 or len(high) != 3 or not all(math.isfinite(x) for x in low + high):
                    raise PackageError(f"invalid Bounds(mm) in {path.name}")
                header["boundsMm"] = {"min": low, "max": high}
            if line.startswith("Volume(cm3):"):
                try:
                    header["volumeCm3"] = float(line.split(":", 1)[1].strip())
                except ValueError:
                    header["volumeCm3"] = None
    for key in ("conceptId", "representationId", "buildUpLogic"):
        if isinstance(header.get(key), str) and not header[key].strip():
            header[key] = None
    if not header.get("fileId") or not header.get("buildUpLogic") or not header.get("boundsMm"):
        raise PackageError(f"source File ID, build-up tree, or Bounds(mm) header missing in {path.name}")
    if not FJ_ID.fullmatch(header["fileId"]):
        raise PackageError(f"unexpected FJ File ID header: {header['fileId']}")
    return header


def bounds(vertices: list[tuple[float, float, float]]) -> dict[str, list[float]]:
    return {"min": [min(v[i] for v in vertices) for i in range(3)], "max": [max(v[i] for v in vertices) for i in range(3)]}


def transform_bounds(source: dict[str, list[float]]) -> dict[str, list[float]]:
    corners = []
    for x in (source["min"][0], source["max"][0]):
        for y in (source["min"][1], source["max"][1]):
            for z in (source["min"][2], source["max"][2]):
                corners.append((x * 0.001, z * 0.001, -y * 0.001))
    return {"min": [min(v[i] for v in corners) for i in range(3)], "max": [max(v[i] for v in corners) for i in range(3)]}


def triangle_area(poly: list[tuple[float, float, float]]) -> float:
    if len(poly) < 3:
        return 0.0
    area = 0.0
    for i in range(1, len(poly) - 1):
        a, b, c = poly[0], poly[i], poly[i + 1]
        ab = tuple(b[j] - a[j] for j in range(3))
        ac = tuple(c[j] - a[j] for j in range(3))
        cross = (ab[1] * ac[2] - ab[2] * ac[1], ab[2] * ac[0] - ab[0] * ac[2], ab[0] * ac[1] - ab[1] * ac[0])
        area += 0.5 * math.sqrt(sum(x * x for x in cross))
    return area


def clip_x(poly: list[tuple[float, float, float]], sign: str) -> list[tuple[float, float, float]]:
    def inside(p):
        return p[0] >= 0 if sign == "left" else p[0] <= 0
    output = []
    for a, b in zip(poly, poly[1:] + poly[:1]):
        ia, ib = inside(a), inside(b)
        if ia and ib:
            output.append(b)
        elif ia and not ib:
            t = (0.0 - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 0.0
            output.append(tuple(a[i] + t * (b[i] - a[i]) for i in range(3)))
        elif not ia and ib:
            t = (0.0 - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 0.0
            output.append(tuple(a[i] + t * (b[i] - a[i]) for i in range(3)))
            output.append(b)
    return output


def side_surface_diagnostic(side: str, vertices: list[tuple[float, float, float]], triangles: list[tuple[int, int, int]]) -> dict[str, Any]:
    if side == "unknown_header_name_missing":
        return {"sourceLabelSide": side, "diagnostic": "header-name-missing-side-unknown", "surfaceAreaOnLabelSideFraction": None, "surfaceAreaOppositeSideFraction": None}
    if side not in {"left", "right"}:
        return {"sourceLabelSide": side, "diagnostic": "source-label-not-unilateral", "surfaceAreaOnLabelSideFraction": None, "surfaceAreaOppositeSideFraction": None}
    side_area = 0.0
    other_area = 0.0
    total_area = 0.0
    for tri in triangles:
        poly = [vertices[idx] for idx in tri]
        area = triangle_area(poly)
        total_area += area
        on = triangle_area(clip_x(poly, side))
        side_area += on
        other_area += max(0.0, area - on)
    fraction = side_area / total_area if total_area else None
    min_x, max_x = min(v[0] for v in vertices), max(v[0] for v in vertices)
    cross = min_x < 0 < max_x
    if side == "left":
        wholly_opposite = max_x < 0
    else:
        wholly_opposite = min_x > 0
    return {
        "sourceLabelSide": side,
        "sourceFrameXPositiveMeans": "left",
        "surfaceAreaOnLabelSideFraction": fraction,
        "surfaceAreaOppositeSideFraction": other_area / total_area if total_area else None,
        "xBoundsMm": [min_x, max_x],
        "crossesMidline": cross,
        "boundsWhollyOppositeToSourceLabel": wholly_opposite,
        "diagnostic": "bounds_wholly_opposite_hold_without_edit" if wholly_opposite else "midline-crossing-observation-only" if cross else "bounds-side-agrees-diagnostic-only",
    }


def union_bounds(rows: list[dict[str, Any]]) -> dict[str, list[float]] | None:
    if not rows:
        return None
    return {
        "min": [min(row["projectBoundsM"]["min"][i] for row in rows) for i in range(3)],
        "max": [max(row["projectBoundsM"]["max"][i] for row in rows) for i in range(3)],
    }


def aabb_overlap(a: dict[str, list[float]], b: dict[str, list[float]]) -> dict[str, Any] | None:
    lo = [max(a["min"][i], b["min"][i]) for i in range(3)]
    hi = [min(a["max"][i], b["max"][i]) for i in range(3)]
    if any(hi[i] <= lo[i] for i in range(3)):
        return None
    return {"min": lo, "max": hi, "overlapExtentM": [hi[i] - lo[i] for i in range(3)]}


def unpack_glb(glb: bytes) -> tuple[dict[str, Any], bytes]:
    if len(glb) < 20 or glb[:4] != b"glTF":
        raise PackageError("converter returned an invalid GLB header")
    json_len, json_type = struct.unpack_from("<II", glb, 12)
    if json_type != 0x4E4F534A:
        raise PackageError("GLB JSON chunk is missing")
    json_start = 20
    json_end = json_start + json_len
    gltf = json.loads(glb[json_start:json_end].decode("utf-8"))
    bin_len, bin_type = struct.unpack_from("<II", glb, json_end)
    if bin_type != 0x004E4942:
        raise PackageError("GLB BIN chunk is missing")
    return gltf, glb[json_end + 8 : json_end + 8 + bin_len]


def repack_glb(gltf: dict[str, Any], binary: bytes) -> bytes:
    json_chunk = json.dumps(gltf, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    while len(json_chunk) % 4:
        json_chunk += b" "
    while len(binary) % 4:
        binary += b"\0"
    total = 12 + 8 + len(json_chunk) + 8 + len(binary)
    return b"".join((struct.pack("<4sII", b"glTF", 2, total), struct.pack("<II", len(json_chunk), 0x4E4F534A), json_chunk, struct.pack("<II", len(binary), 0x004E4942), binary))


def glb_position_hash(gltf: dict[str, Any], binary: bytes, mesh_index: int) -> str:
    mesh = gltf["meshes"][mesh_index]
    attrs = mesh["primitives"][0]["attributes"]
    accessor = gltf["accessors"][attrs["POSITION"]]
    view = gltf["bufferViews"][accessor["bufferView"]]
    offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    size = accessor["count"] * 12
    return sha256_bytes(binary[offset : offset + size])


def build() -> dict[str, Any]:
    frozen = read_json(FROZEN)
    acquisition = read_json(ACQUISITION)
    if acquisition.get("frozenMembershipSha256") != frozen.get("frozenMembershipSha256") or acquisition.get("frozenSourceSetSha256") != sha256_file(FROZEN):
        raise PackageError("T53 acquisition does not bind the frozen source set")
    acquisition_by_id = {row["sourceElementFileId"]: row for row in acquisition["files"]}
    frozen_by_id = {row["sourceElementFileId"]: row for row in frozen["uniqueSourceAssets"]}
    expected_ids = set(frozen_by_id)
    if set(acquisition_by_id) != expected_ids:
        raise PackageError("acquisition records differ from the frozen T53 ID set")
    failures = [row["sourceElementFileId"] for row in acquisition["files"] if row["status"] != "acquired"]
    if failures:
        raise PackageError(f"cannot build a complete frozen package; acquisition failures: {failures[:20]}")

    tables = INGEST.load_tables(METADATA)
    t51 = read_json(T51_MANIFEST)
    t51_concepts = {row["sourceFmaConceptId"]: row for row in t51["sourceConcepts"]}
    regions_t51 = {rid: read_json(REGION_ROOT / f"{rid}.json") for rid in REGIONS}
    input_records: list[dict[str, Any]] = []
    detail_by_id: dict[str, dict[str, Any]] = {}
    identity_by_tree: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for rows in (tables["isaConcepts"], tables["partofConcepts"]):
        for fma, bp, _name in rows:
            identity_by_tree["IS-A" if rows is tables["isaConcepts"] else "PART-OF"].add((fma, bp))

    for file_id in sorted(expected_ids):
        acquisition_row = acquisition_by_id[file_id]
        path = ROOT / acquisition_row["cacheRelativePath"]
        if not path.is_file() or path.stat().st_size != acquisition_row["bytes"] or sha256_file(path) != acquisition_row["sha256"]:
            raise PackageError(f"source cache file changed or missing: {file_id}")
        header = parse_header(path)
        if header["fileId"] != file_id:
            raise PackageError(f"source OBJ File ID header differs from frozen ID: {file_id}")
        expected_tree = {"FMA 3.0 is_a": "IS-A", "FMA 3.0 part_of": "PART-OF"}.get(header.get("buildUpLogic"))
        if expected_tree != acquisition_row["archiveTree"]:
            raise PackageError(f"OBJ header tree {expected_tree} differs from acquired archive {acquisition_row['archiveTree']}: {file_id}")
        if expected_tree not in frozen_by_id[file_id]["expectedArchiveTrees"]:
            raise PackageError(f"chosen archive tree is absent from T51's official source-index context: {file_id}")
        official_element_rows = [row for row in tables["isaCompoundElements"] + tables["partofCompoundElements"] if row[2] == file_id]
        if not official_element_rows:
            raise PackageError(f"source File ID is absent from official Release 4.0 element metadata: {file_id}")
        header_has_fma = bool(header.get("conceptId"))
        header_has_bp = bool(header.get("representationId"))
        if header_has_fma and header_has_bp:
            INGEST.validate_obj_source_identity(header, tables)
            if (header["conceptId"], header["representationId"]) not in identity_by_tree[expected_tree]:
                raise PackageError(f"OBJ header FMA/BP pair is not in the official {expected_tree} concept index: {file_id}")
            identity_state = "header_identity_validated_against_release_metadata"
        else:
            identity_state = "header_identity_blank_context_only" if not header_has_fma and not header_has_bp else "header_identity_partial_held"
            contexts = frozen_by_id[file_id]["sourceContexts"]
            if header_has_fma and header["conceptId"] not in {ctx["sourceFmaConceptId"] for ctx in contexts}:
                raise PackageError(f"partial OBJ header FMA is absent from exact T51 source contexts: {file_id}")
            if header_has_bp and not any(rep["sourceRepresentationId"] == header["representationId"] and rep["tree"] == expected_tree for ctx in contexts for rep in ctx["representations"]):
                raise PackageError(f"partial OBJ header representation is absent from exact T51 source contexts: {file_id}")
        vertices, normals, triangles = CONVERT.parse_obj(path)
        actual_bounds = bounds(vertices)
        bounds_header_deltas = [abs(a - b) for key in ("min", "max") for a, b in zip(header["boundsMm"][key], actual_bounds[key])]
        name = header["englishName"]
        side = INGEST.side_from_name(name) if name else "unknown_header_name_missing"
        if side not in {"left", "right", "bilateral_source_term", "not_lateralized_in_source_label"}:
            side = "unknown_header_name_missing" if name is None else "not_lateralized_in_source_label"
        source_regions = frozen_by_id[file_id]["regionMemberships"]
        source_contexts = frozen_by_id[file_id]["sourceContexts"]
        if header_has_fma:
            source_contexts = [ctx for ctx in source_contexts if ctx["sourceFmaConceptId"] == header["conceptId"]]
        if header_has_bp:
            source_contexts = [ctx for ctx in source_contexts if any(rep["sourceRepresentationId"] == header["representationId"] and rep["tree"] == expected_tree for rep in ctx["representations"])]
        if not source_contexts:
            raise PackageError(f"no frozen official source contexts are consistent with present OBJ identity fields: {file_id}")
        concepts = t51_concepts.get(header["conceptId"]) if header_has_fma else None
        by_region = {}
        for region in source_regions:
            region_chunk = regions_t51[region]
            context_fma_ids = {ctx["sourceFmaConceptId"] for ctx in source_contexts}
            bone = bool(context_fma_ids & set(region_chunk["sourceBoneConceptIds"]))
            muscle = bool(context_fma_ids & set(region_chunk["sourceMuscleConceptIds"]))
            by_region[region] = {"boneContext": bone, "muscleContext": muscle, "sourceRootNames": region_chunk["sourceRoots"]}
        source_side = side
        side_diag = side_surface_diagnostic(source_side, vertices, triangles)
        record = {
            "sourceElementFileId": file_id,
            "stableMeshAssetId": f"HA-MESH-BP3D4-{file_id}",
            "canonicalLearnerIds": [],
            "sourceIdentityState": identity_state,
            "sourceHeaderFmaBpPairState": "validated" if identity_state == "header_identity_validated_against_release_metadata" else "incomplete_not_inferred",
            "sourceConceptId": header["conceptId"],
            "sourceRepresentationId": header["representationId"],
            "sourceBuildUpLogic": header["buildUpLogic"],
            "sourceName": name,
            "sourceNameIndexObservation": concepts["sourceNameEnglish"] if concepts else None,
            "sourceContextCandidates": source_contexts,
            "sourceConceptRepresentations": concepts["representations"] if concepts else None,
            "regionMemberships": source_regions,
            "regionContextKinds": by_region,
            "lateralityFromExactSourceHeader": side,
            "lateralitySurfaceDiagnostic": side_diag,
            "sourceFrame": "BodyParts3D Release 4.0 native static reference; no OpenSim registration",
            "projectFrame": FRAME,
            "sourceUnit": "mm, evidenced per file by Bounds(mm) OBJ header",
            "transform": "[x,y,z]mm -> [x,z,-y]m; preserve x sign; no mirror or source-label change",
            "sourceBoundsMmHeader": header["boundsMm"],
            "sourceBoundsMmVertices": actual_bounds,
            "sourceBoundsHeaderMatchesVertices": all(abs(a-b) <= 0.01 for a,b in zip(header["boundsMm"]["min"] + header["boundsMm"]["max"], actual_bounds["min"] + actual_bounds["max"])),
            "sourceBoundsHeaderMaxAbsDeltaMm": max(bounds_header_deltas),
            "projectBoundsM": transform_bounds(actual_bounds),
            "sourcePose": POSE,
            "sourceLod": "official 99%-reduced bundle; no multilevel LOD chain advertised",
            "sourceVertices": len(vertices),
            "sourceNormals": len(normals),
            "sourceTriangles": len(triangles),
            "sourceBytes": acquisition_row["bytes"],
            "sourceSha256": acquisition_row["sha256"],
            "sourceArchiveTree": acquisition_row["archiveTree"],
            "sourceHeaderLicenseObservation": header.get("licenseHeader"),
            "reviewState": "source_only_not_human_anatomy_reviewed",
        }
        record["positionContentSha256"] = sha256_bytes(struct.pack(f"<{len(vertices)*3}f", *(value for v in vertices for value in CONVERT.transform_vertex(v))))
        record["topologyContentSha256"] = sha256_bytes(struct.pack(f"<{len(triangles)*3}I", *(index for tri in triangles for index in tri)))
        input_records.append({"file_id": file_id, "source_path": path, "source_relative_path": acquisition_row["cacheRelativePath"], "source_sha256": acquisition_row["sha256"], "asset": {"bytes": acquisition_row["bytes"], "vertex_count": len(vertices), "polygon_count": len(triangles), "concept_id": header["conceptId"], "representation_id": header["representationId"]}})
        detail_by_id[file_id] = record

    CONVERT.MODEL_ID = MODEL_ID
    glb, mesh_records = CONVERT.build_glb(input_records)
    gltf, binary = unpack_glb(glb)
    gltf["asset"]["generator"] = "HUMAN ATLAS T53 reproducible internal BodyParts3D R4 package builder"
    gltf["extras"] = {
        "taskScope": "T53 internal static source QA only",
        "sourceId": SOURCE_ID,
        "sourceVersion": SOURCE_VERSION,
        "frame": FRAME,
        "pose": POSE,
        "oneNodePerUniqueSourceElementFileId": True,
        "wholeBodyCanonicalDenominator": None,
        "canonicalLearnerMembershipCreated": False,
        "humanAnatomyReviewed": False,
        "licenseRedistributionStatus": "held_pending_file_level_reconciliation",
    }
    for mesh_record in mesh_records:
        file_id = mesh_record["sourceFileId"]
        detail = detail_by_id[file_id]
        index = mesh_record["nodeIndex"]
        extras = {
            **detail,
            "modelId": MODEL_ID,
            "meshIndex": mesh_record["meshIndex"],
            "geometrySha256": mesh_record["geometrySha256"],
            "topologySha256": mesh_record["topologySha256"],
            "normalSha256": mesh_record["normalSha256"],
        }
        gltf["nodes"][index]["name"] = detail["stableMeshAssetId"]
        gltf["nodes"][index]["extras"].update(extras)
        gltf["meshes"][index]["name"] = detail["stableMeshAssetId"]
        gltf["meshes"][index]["extras"].update(extras)
        mesh_record["nodeName"] = detail["stableMeshAssetId"]
        mesh_record["sourceElementFileId"] = file_id
        mesh_record["regionMemberships"] = detail["regionMemberships"]
        mesh_record["sourceFmaConceptId"] = detail["sourceConceptId"]
        mesh_record["sourceRepresentationId"] = detail["sourceRepresentationId"]
    output_glb = repack_glb(gltf, binary)
    GLB_ROOT.mkdir(parents=True, exist_ok=True)
    if OUT_GLB.exists() and OUT_GLB.read_bytes() != output_glb:
        raise PackageError(f"refusing to overwrite an existing non-deterministic GLB: {OUT_GLB}")
    OUT_GLB.write_bytes(output_glb)
    glb_sha = sha256_bytes(output_glb)

    # Verify GLB membership, identity and direct POSITION payloads against all source OBJ inputs.
    positions_by_id = {}
    mesh_by_id = {row["sourceFileId"]: row for row in mesh_records}
    for mesh_index, mesh in enumerate(gltf["meshes"]):
        file_id = mesh["extras"]["sourceElementFileId"]
        positions_by_id[file_id] = glb_position_hash(gltf, binary, mesh_index)
    for file_id in sorted(expected_ids):
        if positions_by_id[file_id] != detail_by_id[file_id]["positionContentSha256"]:
            raise PackageError(f"OBJ transformed positions do not match GLB FLOAT32 positions: {file_id}")
    if len(gltf["nodes"]) != len(expected_ids) or len(gltf["meshes"]) != len(expected_ids):
        raise PackageError("integrated GLB must have one node and one mesh per unique source File ID")

    for region in REGIONS:
        region_chunk = regions_t51[region]
        region_ids = region_chunk["sourceElementFileIds"]
        region_records = [detail_by_id[file_id] for file_id in region_ids]
        region_output = {
            "revision": "BodyParts3D-R4-T53-region-reference-v1",
            "task": "T53",
            "regionId": region,
            "labelKo": region_chunk["labelKo"],
            "status": "static_source_candidate_package_not_learner_release",
            "sourceRoots": region_chunk["sourceRoots"],
            "sourceBoneConceptIds": region_chunk["sourceBoneConceptIds"],
            "sourceMuscleConceptIds": region_chunk["sourceMuscleConceptIds"],
            "sourceElementFileIds": region_ids,
            "sourceElementFileCount": len(region_ids),
            "uniqueSceneNodeIds": [detail_by_id[file_id]["stableMeshAssetId"] for file_id in region_ids],
            "sourceMeshClassCounts": {
                "boneContextElements": sum(any(v["boneContext"] for v in row["regionContextKinds"].values()) for row in region_records),
                "muscleContextElements": sum(any(v["muscleContext"] for v in row["regionContextKinds"].values()) for row in region_records),
                "bothContextElements": sum(any(v["boneContext"] and v["muscleContext"] for v in row["regionContextKinds"].values()) for row in region_records),
            },
            "sharedIntegratedChunk": {"path": OUT_GLB.relative_to(ROOT).as_posix(), "sha256": glb_sha, "nodeCount": len(gltf["nodes"])},
            "regionBoundsM": union_bounds(region_records),
            "wholeBodyCanonicalDenominator": None,
            "regionMembershipDoesNotCreateCanonicalMembership": True,
        }
        write_json(OUT_ROOT / f"{region}.json", region_output)

    sorted_records = sorted(detail_by_id.values(), key=lambda row: row["sourceElementFileId"])
    union = union_bounds(sorted_records)
    bounds_overlaps = []
    exact_geometry = defaultdict(list)
    for row in sorted_records:
        exact_geometry[(row["positionContentSha256"], row["topologyContentSha256"])].append(row["sourceElementFileId"])
    duplicate_geometry = [ids for ids in exact_geometry.values() if len(ids) > 1]
    for i, left in enumerate(sorted_records):
        for right in sorted_records[i + 1 :]:
            overlap = aabb_overlap(left["projectBoundsM"], right["projectBoundsM"])
            if overlap:
                bounds_overlaps.append({"sourceElementFileIds": [left["sourceElementFileId"], right["sourceElementFileId"]], "regionMemberships": sorted(set(left["regionMemberships"] + right["regionMemberships"])), "overlap": overlap, "interpretation": "AABB candidate only; not proof of surface collision or anatomical error; included for actual 3D preview inspection."})

    manifest = {
        "revision": "BodyParts3D-R4-T53-static-source-package-v1",
        "task": "T53",
        "status": "local_static_source_package_partial_coverage_and_rights_held",
        "source": {"sourceId": SOURCE_ID, "version": SOURCE_VERSION, "officialReadme": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/README_e.html", "officialReleaseNote": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/release_4.0_e.html", "sourceFrame": "BodyParts3D Release 4.0 static reference", "projectFrame": FRAME, "sourceUnit": "mm, each source OBJ Bounds(mm) header checked", "transform": "[x,y,z]mm -> [x,z,-y]m; no reflection/mirroring", "pose": POSE, "lod": "official 99%-reduced mesh bundle; no multilevel LOD chain advertised"},
        "inputs": {"frozenSourceSet": FROZEN.relative_to(ROOT).as_posix(), "frozenSourceSetSha256": sha256_file(FROZEN), "frozenMembershipSha256": frozen["frozenMembershipSha256"], "acquisitionManifest": ACQUISITION.relative_to(ROOT).as_posix(), "acquisitionManifestSha256": sha256_file(ACQUISITION), "t51ManifestSha256": sha256_file(T51_MANIFEST)},
        "scope": {"regionIds": list(REGIONS), "sourceElementFileCount": len(sorted_records), "sourceMembershipCount": sum(len(row["regionMemberships"]) for row in sorted_records), "crossRegionReusedSourceIds": {row["sourceElementFileId"]: row["regionMemberships"] for row in sorted_records if len(row["regionMemberships"]) > 1}, "oneNodePerUniqueFj": True, "internalBatchSizeMaximum": 10, "internalBatchCount": len(frozen["internalBatches"]), "wholeBodyCanonicalDenominator": None, "deepMuscleCoverageComplete": False, "learnerNavigationChanged": False},
        "sceneContract": {"contract": "T50 shared learner scene contract; QA-only static package, no learner scene implementation", "modelId": MODEL_ID, "integratedGlbLocalCachePath": OUT_GLB.relative_to(ROOT).as_posix(), "integratedGlbSha256": glb_sha, "meshNodeCount": len(gltf["nodes"]), "rendererCount": 0, "rendererPolicy": "render verification uses one preview canvas and one persistent AnatomySceneRoot; no product or second learner viewport"},
        "assetCounts": {"uniqueMeshIds": len(sorted_records), "boneContextMeshIds": sum(any(v["boneContext"] for v in row["regionContextKinds"].values()) for row in sorted_records), "muscleContextMeshIds": sum(any(v["muscleContext"] for v in row["regionContextKinds"].values()) for row in sorted_records), "sourceFjMLabels": sum(row["sourceElementFileId"].endswith("M") for row in sorted_records), "canonicalLearnerBindings": 0, "humanReviewed": 0, "reviewedPromotions": 0, "sourceMeshEmpty": 0, "duplicateExactGeometryGroups": duplicate_geometry},
        "bounds": {"projectFrameUnionM": union, "regionBounds": {region: read_json(OUT_ROOT / f"{region}.json")["regionBoundsM"] for region in REGIONS}, "pairwiseAabbOverlapCandidateCount": len(bounds_overlaps), "pairwiseAabbOverlapCandidates": bounds_overlaps, "diagnosticLimit": "AABB overlap is a broadphase observation only; it cannot prove penetration, clipping, contact, duplication, or anatomy error."},
        "sourceBoundsHeaderReconciliation": {"comparison": "per-file OBJ Bounds(mm) versus bounds computed from all actual source vertices", "toleranceMm": 0.01, "matchCount": sum(row["sourceBoundsHeaderMatchesVertices"] for row in sorted_records), "mismatchIds": [row["sourceElementFileId"] for row in sorted_records if not row["sourceBoundsHeaderMatchesVertices"]], "maxAbsoluteDeltaMm": max(row["sourceBoundsHeaderMaxAbsDeltaMm"] for row in sorted_records), "policy": "actual vertex coordinates drive transformed geometry; header/vertex bounds differences are preserved as observations and do not change identity, laterality, or geometry"},
        "sideDiagnostics": {"sourceLabelsObserved": dict(Counter(row["lateralityFromExactSourceHeader"] for row in sorted_records)), "boundsWhollyOppositeSourceLabel": [row["sourceElementFileId"] for row in sorted_records if row["lateralitySurfaceDiagnostic"].get("boundsWhollyOppositeToSourceLabel")], "midlineCrossings": [row["sourceElementFileId"] for row in sorted_records if row["lateralitySurfaceDiagnostic"].get("crossesMidline")], "policy": "Source-side strings and x-side surface fractions are separate; no threshold, AABB center, side swap, or mirror changes identity."},
        "rights": {"officialCurrentLicense": "CC BY 4.0; required attribution recorded", "requiredAttribution": ATTRIBUTION, "sourceHeaderLicenseObservations": dict(Counter(row["sourceHeaderLicenseObservation"] or "not_in_header" for row in sorted_records)), "redistributionStatus": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers", "publicRelease": False},
        "identityPolicy": "Source FMA concept IDs, BP representation IDs, FJ mesh IDs, and canonical HA IDs remain distinct. No source mesh is remapped or promoted. Repeated region membership points to one HA-MESH-BP3D4-FJ node.",
        "regionPackages": {region: {"path": (OUT_ROOT / f"{region}.json").relative_to(ROOT).as_posix(), "sourceElementFileIds": regions_t51[region]["sourceElementFileIds"], "uniqueNodeIds": [detail_by_id[x]["stableMeshAssetId"] for x in regions_t51[region]["sourceElementFileIds"]]} for region in REGIONS},
        "sourceAssets": sorted_records,
        "sourceHeaderIdentityAudit": {"exactHeaderPairsValidated": sum(row["sourceIdentityState"] == "header_identity_validated_against_release_metadata" for row in sorted_records), "unresolvedHeaderIdentityIds": [row["sourceElementFileId"] for row in sorted_records if row["sourceIdentityState"] != "header_identity_validated_against_release_metadata"], "policy": "blank OBJ FMA/BP/name fields are preserved as null; T51 context candidate names are not promoted to exact source identity or laterality"},
        "meshRecords": mesh_records,
    }
    manifest["manifestSha256"] = sha256_bytes(json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    if OUT_MANIFEST.exists():
        previous = read_json(OUT_MANIFEST)
        if previous.get("inputs") != manifest["inputs"] or previous.get("meshRecords") != manifest["meshRecords"]:
            raise PackageError("refusing to overwrite a changed prior T53 source manifest")
    write_json(OUT_MANIFEST, manifest)

    validation = {
        "revision": "T53-PACKAGE-VALIDATION-v1",
        "task": "T53",
        "result": "source_package_built; anatomical visual review pending",
        "frozenIdsMatchAcquired": len(expected_ids) == len(acquisition_by_id) and expected_ids == set(acquisition_by_id),
        "allFrozenItemsAcquired": not failures,
        "exactHeaderIdentityCount": sum(row["sourceIdentityState"] == "header_identity_validated_against_release_metadata" for row in sorted_records),
        "unresolvedHeaderIdentitySourceIds": [row["sourceElementFileId"] for row in sorted_records if row["sourceIdentityState"] != "header_identity_validated_against_release_metadata"],
        "allSourceFileIdsVerifiedInOfficialElementMetadata": len(sorted_records) == len(expected_ids),
        "allPresentSourceTreeHeaderPairsValid": True,
        "allSourceUnitsAndBoundsHeadersPresent": len(sorted_records) == len(expected_ids),
        "sourceBoundsHeaderMatchCount": sum(row["sourceBoundsHeaderMatchesVertices"] for row in sorted_records),
        "sourceBoundsHeaderMismatchIds": [row["sourceElementFileId"] for row in sorted_records if not row["sourceBoundsHeaderMatchesVertices"]],
        "sourceBoundsHeaderMaxAbsDeltaMm": max(row["sourceBoundsHeaderMaxAbsDeltaMm"] for row in sorted_records),
        "allSourcePositionsMatchProjectGlbFloat32": len(positions_by_id) == len(expected_ids),
        "maxBatches": max((len(batch["sourceElementFileIds"]) for batch in frozen["internalBatches"]), default=0),
        "maxBatchLimit": frozen["internalBatchSizeLimit"],
        "batchCount": len(frozen["internalBatches"]),
        "oneSceneNodePerUniqueFj": len(gltf["nodes"]) == len(expected_ids),
        "regionMembershipsReuseNodeIds": all(all(detail_by_id[file_id]["stableMeshAssetId"] in read_json(OUT_ROOT / f"{region}.json")["uniqueSceneNodeIds"] for file_id in regions_t51[region]["sourceElementFileIds"]) for region in REGIONS),
        "exactDuplicateGeometryGroups": duplicate_geometry,
        "sideLabelSurfaceDiagnostics": {"whollyOpposite": len(manifest["sideDiagnostics"]["boundsWhollyOppositeSourceLabel"]), "crossesMidline": len(manifest["sideDiagnostics"]["midlineCrossings"]), "allHeldWithoutMutation": True},
        "aabbOverlapCandidates": len(bounds_overlaps),
        "aabbOverlapIsNotTreatedAsPenetrationProof": True,
        "visualMeshIntersectionReview": "pending_browser",
        "deepMuscleCoverageComplete": False,
        "wholeBodyDenominator": None,
        "redistributionStatus": manifest["rights"]["redistributionStatus"],
        "canonicalLearnerBindings": 0,
        "humanReviewed": 0,
        "sourceCacheOnly": True,
        "sourceCacheFiles": len(sorted_records),
        "sourceCacheBytes": sum(row["sourceBytes"] for row in sorted_records),
        "sourceCacheSha256Map": {row["sourceElementFileId"]: row["sourceSha256"] for row in sorted_records},
        "integratedGlb": {"path": OUT_GLB.relative_to(ROOT).as_posix(), "bytes": len(output_glb), "sha256": glb_sha, "meshNodeCount": len(gltf["nodes"])},
        "manifest": {"path": OUT_MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha256_file(OUT_MANIFEST)},
    }
    write_json(OUT_VALIDATION, validation)
    return {"manifest": manifest, "validation": validation}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true", help="validate all frozen local source files and build one integrated local static GLB")
    args = parser.parse_args()
    if not args.build:
        parser.error("choose --build")
    try:
        result = build()
    except (OSError, ValueError, PackageError) as exc:
        print(f"T53 package build rejected: {exc}", file=sys.stderr)
        return 2
    v = result["validation"]
    print(json.dumps({"result": v["result"], "meshNodes": v["integratedGlb"]["meshNodeCount"], "sourceBytes": v["sourceCacheBytes"], "glbBytes": v["integratedGlb"]["bytes"], "glbSha256": v["integratedGlb"]["sha256"], "aabbOverlapCandidates": v["aabbOverlapCandidates"], "sideWhollyOpposite": v["sideLabelSurfaceDiagnostics"]["whollyOpposite"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
