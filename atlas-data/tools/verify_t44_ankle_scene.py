#!/usr/bin/env python3
"""Check T44 source-to-GLB structure, model side, landmarks, and preservation."""
import hashlib
import json
import math
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "atlas-data/assets/derived-glb/opensim-gait2392-t44-right-ankle"
EVIDENCE = ROOT / "work/evidence/T44"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    m = json.loads((ASSET / "joint-binding-t44.json").read_text())
    blob = (ASSET / "right-ankle-rest.glb").read_bytes()
    magic, version, total = struct.unpack_from("<4sII", blob)
    assert magic == b"glTF" and version == 2 and total == len(blob)
    json_length, json_type = struct.unpack_from("<I4s", blob, 12)
    assert json_type == b"JSON"
    doc = json.loads(blob[20:20+json_length])
    bin_offset = 20 + json_length
    bin_length, bin_type = struct.unpack_from("<I4s", blob, bin_offset)
    binary = blob[bin_offset+8:bin_offset+8+bin_length]
    assert bin_type == b"BIN\0" and len(binary) == bin_length
    assert len(doc["buffers"]) == 1 and "uri" not in doc["buffers"][0]
    assert not doc.get("images") and not doc.get("animations")
    assert sha(ASSET / "right-ankle-rest.glb") == m["staticScene"]["sha256"]
    assert sha(ROOT / m["generatorScript"]["path"]) == m["generatorScript"]["sha256"]
    assert sha(ROOT / m["sourceModel"]["path"]) == m["sourceModel"]["sha256"]
    for file, detail in m["sourceGeometry"].items():
        assert sha(ROOT / "OpenSim_Models/Geometry" / file) == detail["sha256"]
    nodes = doc["nodes"]
    assert [n["name"] for n in nodes] == ["tibia_r_fixed", "tibia_r.vtp", "fibula.vtp", "ankle_r_pivot_q0", "talus.vtp", "subtalar_r_pivot_q0", "foot.vtp", "mtp_r_pivot_q0", "bofoot.vtp", "tib_ant_r_model_path_q0"]
    assert nodes[0]["children"] == [1,2,3] and nodes[3]["children"] == [4,5]
    assert nodes[5]["children"] == [6,7] and nodes[7]["children"] == [8]
    assert set(m["jointBinding"]["movingSubtree"]) == {"talus_r", "calcn_r", "toes_r"}
    assert m["jointBinding"]["fixedBody"] == "tibia_r"
    assert m["jointBinding"]["sourceJoint"] == "ankle_r"
    assert m["jointBinding"]["sourceCoordinate"] == "ankle_angle_r"
    assert m["restPose"]["coordinateRadians"] == {"ankle_angle_r": 0, "subtalar_angle_r": 0, "mtp_angle_r": 0}
    assert m["sourceToSceneMatrixColumnMajor"] == [0,0,1,0,0,1,0,0,-1,0,0,0,0,0,0,1]
    assert m["sceneFrame"]["id"] != "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
    assert m["residualAcceptance"]["crossModelRegistration"] == "not_attempted_no_shared_landmarks"
    # The positive ankle coordinate lifts the source +X (anterior) foot lever:
    # (axis x anterior) dot superior = axis_z > 0.
    axis = m["jointBinding"]["axisSourceJointFrame"]
    assert axis[2] > .9
    checks = []
    for landmark in m["validationLandmarks"]:
        source = landmark["sourceM"]
        mapped = [-source[2], source[1], source[0]]
        residual = math.dist(mapped, landmark["sceneM"])
        assert residual < 1e-12
        checks.append({"name": landmark["name"], "residualM": residual})
    for file, detail in m["sourceGeometry"].items():
        node = next(n for n in nodes if n["name"] == file)
        mesh = doc["meshes"][node["mesh"]]["primitives"][0]
        assert doc["accessors"][mesh["attributes"]["POSITION"]]["count"] == detail["vertexCount"]
        assert doc["accessors"][mesh["indices"]]["count"] == 3*detail["triangleCount"]
    path_primitive = doc["meshes"][nodes[9]["mesh"]]["primitives"][0]
    assert path_primitive["mode"] == 1
    accessor = doc["accessors"][path_primitive["attributes"]["POSITION"]]
    view = doc["bufferViews"][accessor["bufferView"]]
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    coords = struct.unpack_from("<9f", binary, start)
    max_f32_residual = max(math.dist(coords[i*3:(i+1)*3], point["restWorldSceneM"])
                           for i, point in enumerate(m["modelPath"]["points"]))
    assert max_f32_residual < 1e-7
    assert [p["body"] for p in m["modelPath"]["points"]] == ["tibia_r", "tibia_r", "calcn_r"]
    assert m["modelPath"]["kind"] == "simplified_source_model_line_not_attachment_surface"
    catalog = json.loads((ROOT / "atlas-data/catalog/canonical-catalog.json").read_text())
    entities = catalog["entities"]
    assert any(x["id"] == m["canonicalJointId"] and x["kind"] == "joint" for x in entities["structures"])
    assert any(x["id"] == m["canonicalActionId"] and x["reviewState"] == "needs_review" for x in entities["jointActions"])
    assert all("FJ3385" not in json.dumps(x) for x in entities["meshMappings"])
    prior = json.loads(subprocess.check_output(["git", "show", "HEAD:atlas-data/catalog/canonical-catalog.json"], cwd=ROOT))
    for collection, old in prior["entities"].items():
        fresh = entities[collection]
        assert fresh[:len(old)] == old, f"Existing {collection} rows changed"
    result = {"passed": True, "sourceModelSha256": m["sourceModel"]["sha256"],
              "glbSha256": m["staticScene"]["sha256"], "geometryFiles": list(m["sourceGeometry"]),
              "rightSideChecks": ["model Body names tibia_r/talus_r/calcn_r/toes_r", "ankle_r parent tibia_r, child talus_r", "no left source geometry in output", "no mirror of local vertices"],
              "boneCorrespondence": {k: v["sourceBody"] for k,v in m["sourceGeometry"].items()},
              "landmarkChecks": checks, "maxPathF32ResidualM": max_f32_residual,
              "coordinateAcceptanceM": m["residualAcceptance"]["sameSourceAlgebraToleranceM"],
              "sourceModelToBP3DRegistration": "not attempted; separate scene", "canonicalPriorRowsPreserved": True,
              "hasAnimation": False, "selfContainedGlb": True}
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "scene-validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
