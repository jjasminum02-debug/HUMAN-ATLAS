#!/usr/bin/env python3
"""Derive a bounded BodyParts3D-to-ZA translation from paired pelvis surfaces.

The transform is estimated from evaluated vertex centroids of the exact right
hip, left hip, and sacrum meshes (not their AABBs), then checked against held
out anchor-centroid residuals and symmetric nearest-vertex surface distances.
This is a local geometric registration check, not human anatomy approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work/evidence/T100/source-completion-2026-10-01/integration/registration-evidence.json"
ZA_MANIFEST = "atlas-data/source-cache/datasets/za/compiled/manifest.json"
BP_REGISTRY = "atlas-data/source-cache/datasets/bp3d/registry.json"
BP_T77 = "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json"
SCENE_CONTRACT = "work/evidence/T50/scene-contract.md"
T69_DIAGNOSTIC = "work/evidence/T69/diagnostic.json"
ANCHORS = [
    {"fj": "FJ3152", "zaName": "Hip bone.r", "sourceKey": "ZA-c7010a9-74a765dc396d690d1642153e",
     "chunk": "06-gluteal-hip-bone-0", "memberSide": "right"},
    {"fj": "FJ3288", "zaName": "Hip bone.l", "sourceKey": "ZA-c7010a9-ecb65ff4cc3da710e5a2d157",
     "chunk": "06-gluteal-hip-bone-0", "memberSide": "left"},
    {"fj": "FJ3393", "zaName": "Sacrum", "sourceKey": "ZA-c7010a9-95b8d859c84ae9e56cacdafc",
     "chunk": "15-pelvis-perineum-bone-1", "memberSide": None},
]


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: str) -> str:
    return sha_bytes((ROOT / path).read_bytes())


def glb(path: Path):
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF" or struct.unpack_from("<I", data, 8)[0] != len(data):
        raise ValueError(f"invalid GLB container: {path}")
    json_size = struct.unpack_from("<I", data, 12)[0]
    json_end = 20 + json_size
    if data[json_end + 4:json_end + 8] != b"BIN\x00":
        raise ValueError(f"missing GLB binary chunk: {path}")
    binary_size = struct.unpack_from("<I", data, json_end)[0]
    binary = data[json_end + 8:json_end + 8 + binary_size]
    if len(binary) != binary_size:
        raise ValueError(f"truncated GLB binary: {path}")
    return data, json.loads(data[20:json_end]), binary


def position_accessor(doc, binary, mesh_index: int):
    primitive = doc["meshes"][mesh_index]["primitives"][0]
    accessor = doc["accessors"][primitive["attributes"]["POSITION"]]
    if accessor["componentType"] != 5126 or accessor["type"] != "VEC3" or accessor.get("sparse"):
        raise ValueError("registration requires non-sparse float32 VEC3 positions")
    view = doc["bufferViews"][accessor["bufferView"]]
    stride = view.get("byteStride", 12)
    offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    count = accessor["count"]
    points = []
    for i in range(count):
        points.append(struct.unpack_from("<fff", binary, offset + i * stride))
    return points


def bp_mesh(path: Path, fj: str):
    _, doc, binary = glb(path)
    node = next((n for n in doc["nodes"] if n.get("name") == f"HA-MESH-BP3D4-{fj}"), None)
    if not node or "mesh" not in node:
        raise ValueError(f"exact BP3D source node missing: {fj}")
    if any(k in node for k in ("matrix", "translation", "rotation", "scale")):
        raise ValueError(f"unexpected object transform; T77 output is expected baked: {fj}")
    return position_accessor(doc, binary, node["mesh"])


def za_mesh(path: Path, instance):
    _, doc, binary = glb(path)
    points = position_accessor(doc, binary, 0)
    matrix = instance["matrix"]
    # Serialized Matrix4 values use Three.js column-major order.
    return [(
        matrix[0] * x + matrix[4] * y + matrix[8] * z + matrix[12],
        matrix[1] * x + matrix[5] * y + matrix[9] * z + matrix[13],
        matrix[2] * x + matrix[6] * y + matrix[10] * z + matrix[14],
    ) for x, y, z in points]


def mean(points):
    n = len(points)
    return tuple(sum(p[i] for p in points) / n for i in range(3))


def sub(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def norm(a):
    return math.sqrt(sum(x * x for x in a))


def quantile(values, q):
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    lo, hi = math.floor(index), math.ceil(index)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - index) + ordered[hi] * (index - lo)


def nearest_vertex_distances(points, cloud):
    # Deterministic at-most-256 evenly strided query vertices, each tested
    # against every actual vertex in the counterpart evaluated mesh.
    stride = max(1, math.ceil(len(points) / 256))
    sampled = points[::stride]
    out = []
    for point in sampled:
        best = float("inf")
        for other in cloud:
            dx, dy, dz = point[0] - other[0], point[1] - other[1], point[2] - other[2]
            distance2 = dx * dx + dy * dy + dz * dz
            if distance2 < best:
                best = distance2
        out.append(math.sqrt(best))
    return out


def surface_stats(a, b):
    ab = nearest_vertex_distances(a, b)
    ba = nearest_vertex_distances(b, a)
    merged = ab + ba
    return {
        "queryVerticesEachDirection": [len(ab), len(ba)],
        "directedNearestVertexMedianM": [quantile(ab, .5), quantile(ba, .5)],
        "directedNearestVertexP95M": [quantile(ab, .95), quantile(ba, .95)],
        "symmetricNearestVertexMedianM": quantile(merged, .5),
        "symmetricNearestVertexP95M": quantile(merged, .95),
        "interpretation": "vertex-to-vertex diagnostic; not exact point-to-triangle distance or human anatomy approval",
    }


def run():
    za = read(ZA_MANIFEST)
    bp_registry = read(BP_REGISTRY)
    bp_manifest = read(BP_T77)
    za_by_key = {x["sourceKey"]: x for x in za["instances"]}
    za_chunks = {x["id"]: x for x in za["chunks"]}
    bp_chunks = {x["id"]: x for x in bp_registry["manifest"]["chunks"]}
    bp_files = {x["id"]: x for x in bp_registry["files"]}
    bp_manifest_chunks = {x["id"]: x for x in bp_manifest["chunks"]}
    t77_inventory = {x["sourceElementId"]: x for x in read("work/evidence/T77/current-inventory.json")["items"]}
    input_paths = [ZA_MANIFEST, BP_REGISTRY, BP_T77, SCENE_CONTRACT, T69_DIAGNOSTIC]
    result_rows = []
    clouds = {}
    for anchor in ANCHORS:
        za_instance = za_by_key[anchor["sourceKey"]]
        if za_instance["sourceName"] != anchor["zaName"]:
            raise ValueError(f"ZA anchor identity changed: {anchor['sourceKey']}")
        resource = za_instance["lods"]["detail"]["resource"]
        za_relative = f"atlas-data/source-cache/datasets/za/resources/{resource}.glb"
        input_paths.append(za_relative)
        bp_chunk = bp_chunks[anchor["chunk"]]
        bp_file = bp_files[anchor["chunk"]]
        t77_chunk = bp_manifest_chunks[anchor["chunk"]]
        if bp_file["sha256"] != bp_chunk["sha256"] or bp_file["bytes"] != bp_chunk["bytes"]:
            raise ValueError(f"BP3D cache registry mismatch: {anchor['chunk']}")
        if bp_chunk["sha256"] != t77_chunk["sha256"] or bp_chunk["bytes"] != t77_chunk["bytes"]:
            raise ValueError(f"T77 compiled chunk mismatch: {anchor['chunk']}")
        bp_relative = bp_file["path"]
        input_paths.append(bp_relative)
        bp_asset = next(x for x in t77_chunk["assets"] if x["id"] == anchor["fj"])
        if bp_asset.get("side") != anchor["memberSide"]:
            raise ValueError(f"source-declared side changed: {anchor['fj']}")
        # Keep the exact source member identity/sha available for the report.
        bp_catalog_member = t77_inventory.get(anchor["fj"])
        if not bp_catalog_member or bp_catalog_member.get("geometry") != "present":
            raise ValueError(f"BP3D source member not present in T77 inventory: {anchor['fj']}")
        bp_points = bp_mesh(ROOT / bp_relative, anchor["fj"])
        za_points = za_mesh(ROOT / za_relative, za_instance)
        if not bp_points or not za_points:
            raise ValueError(f"empty anchor mesh: {anchor['fj']}")
        bp_center, za_center = mean(bp_points), mean(za_points)
        proposed = sub(za_center, bp_center)
        pair_stats = surface_stats(bp_points, za_points)
        result_rows.append({
            "sourceElementFileId": anchor["fj"], "sourceName": bp_asset.get("id"),
            "sourceSha256": bp_catalog_member.get("sourceSha256"), "compiledChunkId": anchor["chunk"],
            "compiledChunkSha256": bp_chunk["sha256"], "bp3dVertexCount": len(bp_points),
            "zaSourceKey": anchor["sourceKey"], "zaSourceName": za_instance["sourceName"],
            "zaEvaluatedGeometrySha256": za_instance["evaluatedGeometrySha256"],
            "zaResource": resource, "zaResourceSha256": sha(za_relative), "zaVertexCount": len(za_points),
            "sourceLabelSide": anchor["memberSide"], "bp3dVertexMeanM": bp_center, "zaVertexMeanM": za_center,
            "centroidDerivedBp3dToZaTranslationM": proposed, "preRegistrationSurface": pair_stats,
        })
        clouds[anchor["fj"]] = (bp_points, za_points)
    offsets = [row["centroidDerivedBp3dToZaTranslationM"] for row in result_rows]
    translation = tuple(sorted(x[i] for x in offsets)[1] for i in range(3))
    for row, anchor in zip(result_rows, ANCHORS):
        bp_points, za_points = clouds[anchor["fj"]]
        residual = sub(row["centroidDerivedBp3dToZaTranslationM"], translation)
        moved = [(p[0] + translation[0], p[1] + translation[1], p[2] + translation[2]) for p in bp_points]
        row["translationResidualFromRobustMedianM"] = residual
        row["translationResidualNormM"] = norm(residual)
        row["postRegistrationSurface"] = surface_stats(moved, za_points)
    input_hashes = {path: sha(path) for path in sorted(set(input_paths))}
    t69 = read(T69_DIAGNOSTIC)
    za_frame = za.get("frameContract", {})
    if za_frame.get("sourceAxes") != {"positiveX": "subject_left", "positiveY": "posterior", "positiveZ": "superior"}:
        raise ValueError("ZA native source axis convention changed")
    if t69.get("globalFrameVerification", {}).get("sourceCoordinateConvention", {}).get("xPositive") != "subject left":
        raise ValueError("T69 source axis convention changed")
    if not t69.get("globalFrameVerification", {}).get("status"):
        raise ValueError("T69 historical source-axis evidence is unavailable")
    return {
        "schemaVersion": 1, "taskId": "T100", "status": "rigid_translation_geometric_registration_candidate",
        "sourcePair": {"bp3d": "BodyParts3D Release 4.0/T77 evaluated static reference", "za": za.get("revision"),
            "projectFrame": "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR", "units": "m after source-specific frame conversion"},
        "method": {
            "anchors": "exact right hip bone, left hip bone, and sacrum evaluated meshes; source names/FJ identity and source-labeled side checked",
            "fit": "componentwise median of per-object evaluated-vertex arithmetic-mean differences; translation only because both source-axis bases are already established in the project frame",
            "translationBp3dToZaM": translation,
            "sourceAabbsUsedForFit": False,
            "heldOutCheck": "each anchor translation compared to robust median; each anchor surface compared with all other-source vertices using deterministic at-most-256 strided query vertices in both directions",
            "limits": ["mesh sampling and anatomical model differences remain", "no human anatomy approval", "global transform is only established by the pelvis anchor set; non-pelvic candidates require local surrounding-structure visual QA", "nearest-vertex distances are not exact point-to-triangle distances", "T69 supplied source-axis validation only; it did not provide this inter-model translation"],
        },
        "anchors": result_rows,
        "inputSha256": input_hashes,
        "preservation": {"sourceGlbBytesModified": False, "sourceObjBytesModified": False,
            "zaCompiledManifestModified": False, "historicalT69DiagnosticModified": False},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    result = run()
    data = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not args.out.is_file() or args.out.read_text(encoding="utf-8") != data:
            raise SystemExit("registration evidence is stale; preserve it and inspect the specific changed input")
    elif args.write:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        if args.out.exists():
            raise SystemExit("refusing to overwrite existing registration evidence")
        args.out.write_text(data, encoding="utf-8")
    else:
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        return
    print(json.dumps({"status": result["status"], "translationM": result["method"]["translationBp3dToZaM"],
        "anchors": len(result["anchors"]), "output": str(args.out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
