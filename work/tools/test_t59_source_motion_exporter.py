#!/usr/bin/env python3
"""Test the T59 exporter on an in-memory-style synthetic GLB, never production content."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("derive_source_surface_motion.py")
spec = importlib.util.spec_from_file_location("t59_exporter", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def make_glb() -> bytes:
    binary = struct.pack("<9f3H", 0, 0, 0, .1, 0, 0, 0, .1, 0, 0, 1, 2)
    doc = {"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": [0]}],
           "nodes": [{"name": "fixture-node", "matrix": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1], "mesh": 0}],
           "meshes": [{"name": "fixture-resource", "primitives": [{"attributes": {"POSITION": 0}, "indices": 1}]}],
           "buffers": [{"byteLength": len(binary)}],
           "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": 36, "target": 34962},
                           {"buffer": 0, "byteOffset": 36, "byteLength": 6, "target": 34963}],
           "accessors": [{"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3"},
                         {"bufferView": 1, "componentType": 5123, "count": 3, "type": "SCALAR"}]}
    json_bytes = json.dumps(doc, separators=(",", ":")).encode()
    json_bytes += b" " * ((-len(json_bytes)) % 4)
    binary += b"\0" * ((-len(binary)) % 4)
    total = 12 + 8 + len(json_bytes) + 8 + len(binary)
    return struct.pack("<III", 0x46546C67, 2, total) + struct.pack("<II", len(json_bytes), 0x4E4F534A) + json_bytes + struct.pack("<II", len(binary), 0x004E4942) + binary


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ha-t59-export-test-") as temp:
        root = Path(temp)
        source_path = root / "synthetic-source.glb"
        source_bytes = make_glb()
        source_path.write_bytes(source_bytes)
        doc, binary = module.load_glb(source_path)
        geometry_sha, _ = module.geometry_hash(doc, binary, 0)
        chunk_sha = hashlib.sha256(source_bytes).hexdigest()
        identity = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        payload = {"schemaVersion": module.SCHEMA, "source": {"glbSha256": chunk_sha, "nodeName": "fixture-node", "nodeMatrix": identity,
                    "resourceKey": "fixture-resource", "sourceKey": "ZA-test-muscle-right", "side": "right"},
                   "sourceBinding": {"contractVersion": "t59-source-motion-binding-v1", "datasetNamespace": "fixture-dataset",
                     "datasetRevision": "fixture-revision", "integrationRevision": "fixture-runtime", "sourceOverlaySha256": "a" * 64,
                     "subjectSourceKey": "ZA-test-muscle-right", "frameId": "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR", "units": "m",
                     "referencePoseId": "fixture-frame0", "deformation": "morph_targets", "members": [{"sourceKey": "ZA-test-muscle-right",
                       "nodeId": "fixture-node", "sourceNamespace": "za-c7010a9", "role": "deforming_muscle_surface", "side": "right",
                       "resourceKey": "fixture-resource", "lod": "overview", "sourceChunkSha256": chunk_sha, "geometrySha256": geometry_sha,
                       "instanceMatrix": identity}]},
                   "rights": {"sourceOnly": True, "localUseRights": "inherits_pinned_source_decision", "publicRedistribution": "held", "humanReview": "not_performed"},
                   "derivationMethod": "synthetic-test-only source-local position delta; not anatomy", "derivationEvidenceRefs": ["fixture-only"],
                   "morph": {"positionDeltas": [[0, 0, 0], [0, .02, 0], [0, 0, 0]]},
                   "clip": {"id": "fixture-motion", "durationSeconds": 1, "timesSeconds": [0, .5, 1], "weights": [0, 1, 0]}}
        output = module.build(payload, source_path)
        assert hashlib.sha256(source_path.read_bytes()).hexdigest() == chunk_sha
        json_length = struct.unpack_from("<I", output, 12)[0]
        exported = json.loads(output[20:20 + json_length].decode().rstrip(" \t\r\n\0"))
        assert len(exported["animations"]) == 1
        assert exported["animations"][0]["channels"][0]["target"]["path"] == "weights"
        assert exported["meshes"][0]["primitives"][0]["targets"][0]["POSITION"] >= 2
        assert exported["animations"][0]["extras"]["HUMAN_ATLAS_T59"]["rights"]["publicRedistribution"] == "held"
        assert "atlas-data/assets" not in str(root)
        bad = json.loads(json.dumps(payload)); bad["morph"]["positionDeltas"] = [[0, 0, 0]] * 3
        try:
            module.build(bad, source_path)
            raise AssertionError("zero morph must fail closed")
        except ValueError as error:
            assert "explicit source-derived change" in str(error)
        bad = json.loads(json.dumps(payload)); bad["sourceBinding"]["members"][0]["side"] = "left"
        try:
            module.build(bad, source_path)
            raise AssertionError("wrong-side binding must fail closed")
        except ValueError as error:
            assert "source-declared side must match" in str(error)
    print("T59 exporter synthetic fixture passed; no production anatomy or clip was created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
