#!/usr/bin/env python3
"""Create a reproducible, source-bound glTF morph clip from authored source-local deltas.

This tool never invents a deformation. A caller must provide one finite delta vector per source
vertex plus an exact pinned dataset/source binding. Outputs remain local candidates with public
redistribution held and human review not performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
from pathlib import Path
from typing import Any

SCHEMA = "t59-derived-morph-input-v1"
COMPONENTS = {5120: (1, "Int8Array", "b"), 5121: (1, "Uint8Array", "B"), 5122: (2, "Int16Array", "h"),
              5123: (2, "Uint16Array", "H"), 5125: (4, "Uint32Array", "I"), 5126: (4, "Float32Array", "f")}
TYPE_SIZE = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}
SEMANTIC_NAMES = {"POSITION": "position", "NORMAL": "normal", "TANGENT": "tangent", "TEXCOORD_0": "uv",
                  "TEXCOORD_1": "uv1", "TEXCOORD_2": "uv2", "COLOR_0": "color", "JOINTS_0": "skinIndex",
                  "WEIGHTS_0": "skinWeight"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_glb(path: Path) -> tuple[dict[str, Any], bytes]:
    data = path.read_bytes()
    if len(data) < 20:
        raise ValueError("source must be a self-contained GLB 2.0")
    magic, version, total, json_len, json_tag = struct.unpack_from("<IIIII", data, 0)
    if magic != 0x46546C67 or version != 2 or total != len(data) or json_tag != 0x4E4F534A:
        raise ValueError("invalid GLB 2.0 header")
    json_start = 20
    json_end = json_start + json_len
    doc = json.loads(data[json_start:json_end].decode("utf-8").rstrip(" \t\r\n\0"))
    offset = json_end
    bin_bytes = b""
    if offset + 8 <= len(data):
        length, tag = struct.unpack_from("<II", data, offset)
        if tag != 0x004E4942 or offset + 8 + length != len(data):
            raise ValueError("GLB must contain a single self-contained BIN chunk")
        bin_bytes = data[offset + 8:offset + 8 + length]
    if len(doc.get("buffers", [])) != 1 or doc["buffers"][0].get("uri") is not None:
        raise ValueError("external/multiple GLB buffers are not allowed")
    if any(row.get("uri") is not None for row in doc.get("images", [])):
        raise ValueError("external images are not allowed")
    if doc.get("animations"):
        raise ValueError("source GLB already has animations; export requires a static source")
    return doc, bin_bytes


def accessor_bytes(doc: dict[str, Any], binary: bytes, accessor_index: int) -> tuple[str, int, int, bool, bytes]:
    accessor = doc["accessors"][accessor_index]
    if accessor.get("sparse") or "bufferView" not in accessor:
        raise ValueError("sparse/implicit accessors are not supported by the deterministic exporter")
    view = doc["bufferViews"][accessor["bufferView"]]
    component_size, array_name, fmt = COMPONENTS[accessor["componentType"]]
    item_size = TYPE_SIZE[accessor["type"]]
    element_size = component_size * item_size
    stride = view.get("byteStride", element_size)
    base = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    packed = bytearray()
    for row in range(accessor["count"]):
        start = base + row * stride
        packed.extend(binary[start:start + element_size])
    if len(packed) != accessor["count"] * element_size:
        raise ValueError("accessor exceeds the source GLB binary buffer")
    return array_name, item_size, accessor["count"], bool(accessor.get("normalized", False)), bytes(packed)


def geometry_hash(doc: dict[str, Any], binary: bytes, mesh_index: int) -> tuple[str, int]:
    mesh = doc["meshes"][mesh_index]
    primitives = mesh.get("primitives", [])
    if len(primitives) != 1 or primitives[0].get("mode", 4) != 4:
        raise ValueError("one TRIANGLES primitive is required for the T59 source geometry digest")
    primitive = primitives[0]
    if primitive.get("targets") or mesh.get("weights"):
        raise ValueError("source GLB already has morph targets; this exporter only appends one source-derived target")
    parts = [b"HUMAN_ATLAS_GEOMETRY_CONTENT_V1\n"]
    vertex_count = None
    for semantic, accessor_index in sorted(primitive["attributes"].items(), key=lambda row: SEMANTIC_NAMES.get(row[0], row[0])):
        name = SEMANTIC_NAMES.get(semantic)
        if name is None:
            raise ValueError(f"unsupported base attribute semantic: {semantic}")
        array_name, item_size, count, normalized, raw = accessor_bytes(doc, binary, accessor_index)
        if vertex_count is None:
            vertex_count = count
        elif count != vertex_count:
            raise ValueError("source vertex attributes have different counts")
        parts.append(f"attribute:{name}|{array_name}|{item_size}|{int(normalized)}|{count}\n".encode())
        parts.append(raw)
    if "POSITION" not in primitive.get("attributes", {}):
        raise ValueError("source mesh has no POSITION accessor")
    if "indices" in primitive:
        array_name, item_size, count, normalized, raw = accessor_bytes(doc, binary, primitive["indices"])
        parts.append(f"index:{array_name}|{item_size}|{int(normalized)}|{count}\n".encode())
        parts.append(raw)
    else:
        parts.append(b"index:none\n")
    if "material" in primitive:
        index_count = doc["accessors"][primitive["indices"]]["count"] if "indices" in primitive else vertex_count or 0
        parts.append(f"group:0|{index_count}|{primitive['material']}\n".encode())
    return sha(b"".join(parts)), int(vertex_count or 0)


def validate_input(payload: dict[str, Any], source_path: Path, doc: dict[str, Any], binary: bytes) -> tuple[int, int, str]:
    if payload.get("schemaVersion") != SCHEMA:
        raise ValueError(f"input schemaVersion must be {SCHEMA}")
    if payload.get("fixtureOnly") is True:
        raise ValueError("test-only input cannot be used by the production exporter")
    source = payload.get("source", {})
    source_sha = sha(source_path.read_bytes())
    if source.get("glbSha256") != source_sha:
        raise ValueError("source GLB SHA-256 does not match the pinned input")
    binding = payload.get("sourceBinding", {})
    member_rows = binding.get("members", [])
    matches = [row for row in member_rows if row.get("sourceKey") == source.get("sourceKey")]
    if len(matches) != 1:
        raise ValueError("exactly one sourceBinding member must match the sourceKey")
    member = matches[0]
    if member.get("role") != "deforming_muscle_surface" or member.get("side") not in ("left", "right"):
        raise ValueError("sourceKey must be an explicitly sided deforming muscle surface")
    if source.get("side") != member.get("side"):
        raise ValueError("source-declared side must match the exact sourceBinding member side")
    if member.get("sourceChunkSha256") != source_sha or binding.get("subjectSourceKey") != source.get("sourceKey"):
        raise ValueError("sourceKey/chunk binding does not match the source bytes")
    if binding.get("units") != "m" or not binding.get("frameId") or not binding.get("referencePoseId"):
        raise ValueError("units, frame, and exact static reference pose are required")
    if payload.get("rights") != {"sourceOnly": True, "localUseRights": "inherits_pinned_source_decision", "publicRedistribution": "held", "humanReview": "not_performed"}:
        raise ValueError("source-only, held rights, and not-performed review must be preserved")
    if not payload.get("derivationEvidenceRefs") or not payload.get("derivationMethod"):
        raise ValueError("source-derived method and evidence refs are required; no deformation is invented here")
    node_name = source.get("nodeName")
    node_rows = [row for row in doc.get("nodes", []) if row.get("name") == node_name and "mesh" in row]
    if len(node_rows) != 1:
        raise ValueError("nodeName must resolve to exactly one mesh node")
    node_index = doc["nodes"].index(node_rows[0])
    mesh_index = node_rows[0]["mesh"]
    mesh = doc["meshes"][mesh_index]
    if mesh.get("name") != source.get("resourceKey"):
        raise ValueError("mesh name must exactly match the pinned resourceKey")
    if sum(1 for row in doc["nodes"] if row.get("mesh") == mesh_index) != 1:
        raise ValueError("the source mesh is shared by multiple nodes; side-specific morph export is ambiguous")
    digest, vertex_count = geometry_hash(doc, binary, mesh_index)
    if member.get("geometrySha256") != digest:
        raise ValueError("source geometry digest does not match sourceBinding")
    source_node_matrix = node_rows[0].get("matrix", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
    if node_rows[0].get("translation") or node_rows[0].get("rotation") or node_rows[0].get("scale"):
        raise ValueError("source node TRS must be resolved and frozen as an exact matrix before morph export")
    if source.get("nodeMatrix") != source_node_matrix:
        raise ValueError("source node matrix differs from the explicit frozen source node matrix")
    if not isinstance(member.get("instanceMatrix"), list) or len(member["instanceMatrix"]) != 16:
        raise ValueError("dataset instance matrix is missing from the source binding")
    morph = payload.get("morph", {})
    deltas = morph.get("positionDeltas")
    if not isinstance(deltas, list) or len(deltas) != vertex_count or any(not isinstance(row, list) or len(row) != 3 for row in deltas):
        raise ValueError("one three-component position delta is required for every exact source vertex")
    flat = [float(value) for row in deltas for value in row]
    if not all(math.isfinite(value) for value in flat) or not any(value != 0 for value in flat):
        raise ValueError("morph deltas must be finite and contain an explicit source-derived change")
    clip = payload.get("clip", {})
    times, weights = clip.get("timesSeconds"), clip.get("weights")
    duration = clip.get("durationSeconds")
    if not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0 or not isinstance(times, list) or not isinstance(weights, list) or len(times) != len(weights) or len(times) < 2:
        raise ValueError("clip needs matching, ordered source-authored time and weight keys")
    if times[0] != 0 or abs(times[-1] - duration) > 1e-6 or any(not math.isfinite(float(value)) for value in times + weights):
        raise ValueError("clip time must span exactly zero to duration with finite values")
    if any(times[index] >= times[index + 1] for index in range(len(times) - 1)) or any(value < 0 or value > 1 for value in weights) or weights[0] != 0:
        raise ValueError("clip keys must be increasing and start at the un-deformed reference weight")
    return node_index, mesh_index, digest


def append_bytes(buffer: bytearray, value: bytes) -> tuple[int, int]:
    while len(buffer) % 4:
        buffer.append(0)
    offset = len(buffer)
    buffer.extend(value)
    while len(buffer) % 4:
        buffer.append(0)
    return offset, len(value)


def build(payload: dict[str, Any], source_path: Path) -> bytes:
    doc, binary = load_glb(source_path)
    node_index, mesh_index, digest = validate_input(payload, source_path, doc, binary)
    buffer = bytearray(binary)
    morph = payload["morph"]
    position_accessor = doc["meshes"][mesh_index]["primitives"][0]["attributes"]["POSITION"]
    count = doc["accessors"][position_accessor]["count"]
    deltas = [float(value) for row in morph["positionDeltas"] for value in row]
    delta_bytes = struct.pack("<" + "f" * len(deltas), *deltas)
    delta_offset, delta_length = append_bytes(buffer, delta_bytes)
    delta_view = len(doc.setdefault("bufferViews", []))
    doc["bufferViews"].append({"buffer": 0, "byteOffset": delta_offset, "byteLength": delta_length, "target": 34962})
    delta_accessor = len(doc.setdefault("accessors", []))
    doc["accessors"].append({"bufferView": delta_view, "componentType": 5126, "count": count, "type": "VEC3"})
    primitive = doc["meshes"][mesh_index]["primitives"][0]
    primitive.setdefault("targets", []).append({"POSITION": delta_accessor})
    mesh = doc["meshes"][mesh_index]
    mesh["weights"] = [0.0]
    mesh.setdefault("extras", {})["HUMAN_ATLAS_T59"] = {"sourceGeometrySha256": digest, "candidateOnly": True, "sourceOnly": True}
    doc["nodes"][node_index]["weights"] = [0.0]
    doc["nodes"][node_index].setdefault("extras", {})["HUMAN_ATLAS_T59"] = {"sourceKey": payload["source"]["sourceKey"], "candidateOnly": True}

    times = [float(value) for value in payload["clip"]["timesSeconds"]]
    weights = [float(value) for value in payload["clip"]["weights"]]
    time_offset, time_length = append_bytes(buffer, struct.pack("<" + "f" * len(times), *times))
    time_view = len(doc["bufferViews"])
    doc["bufferViews"].append({"buffer": 0, "byteOffset": time_offset, "byteLength": time_length})
    time_accessor = len(doc["accessors"])
    doc["accessors"].append({"bufferView": time_view, "componentType": 5126, "count": len(times), "type": "SCALAR", "min": [min(times)], "max": [max(times)]})
    weight_offset, weight_length = append_bytes(buffer, struct.pack("<" + "f" * len(weights), *weights))
    weight_view = len(doc["bufferViews"])
    doc["bufferViews"].append({"buffer": 0, "byteOffset": weight_offset, "byteLength": weight_length})
    weight_accessor = len(doc["accessors"])
    doc["accessors"].append({"bufferView": weight_view, "componentType": 5126, "count": len(weights), "type": "SCALAR"})
    doc.setdefault("animations", []).append({
        "name": payload["clip"]["id"],
        "samplers": [{"input": time_accessor, "output": weight_accessor, "interpolation": "LINEAR"}],
        "channels": [{"sampler": 0, "target": {"node": node_index, "path": "weights"}}],
        "extras": {"HUMAN_ATLAS_T59": {"sourceKey": payload["source"]["sourceKey"], "derivationMethod": payload["derivationMethod"],
            "derivationEvidenceRefs": payload["derivationEvidenceRefs"], "sourceBinding": payload["sourceBinding"], "rights": payload["rights"]}},
    })
    doc["buffers"][0]["byteLength"] = len(buffer)
    json_bytes = json.dumps(doc, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    while len(json_bytes) % 4:
        json_bytes += b" "
    bin_bytes = bytes(buffer)
    total = 12 + 8 + len(json_bytes) + 8 + len(bin_bytes)
    return struct.pack("<III", 0x46546C67, 2, total) + struct.pack("<II", len(json_bytes), 0x4E4F534A) + json_bytes + struct.pack("<II", len(bin_bytes), 0x004E4942) + bin_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="source-derived authoring JSON; no default deformation is generated")
    parser.add_argument("--source", required=True, type=Path, help="immutable input GLB")
    parser.add_argument("--output", required=True, type=Path, help="new candidate GLB path")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        output = build(payload, args.source)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(output)
        print(json.dumps({"status": "candidate_exported", "output": str(args.output), "outputSha256": sha(output), "bytes": len(output),
            "sourceSha256": sha(args.source.read_bytes()), "sourceKey": payload["source"]["sourceKey"], "sourceOnly": True,
            "humanReview": "not_performed", "publicRedistribution": "held"}, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"T59 source-motion export failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
