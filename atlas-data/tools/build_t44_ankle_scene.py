#!/usr/bin/env python3
"""T44: deterministic, stdlib-only Gait2392 right ankle rest scene.

Reads the unmodified OpenSim model and its VTP geometry. Does not solve OpenSim
kinematics or make an animation. All transforms are at the source default q=0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "OpenSim_Models/Models/Gait2392_Simbody/gait2392_thelen2003muscle.osim"
GEOMETRY = ROOT / "OpenSim_Models/Geometry"
OUT = ROOT / "atlas-data/assets/derived-glb/opensim-gait2392-t44-right-ankle"
MESHES = (("tibia_r", "tibia_r.vtp"), ("tibia_r", "fibula.vtp"),
          ("talus_r", "talus.vtp"), ("calcn_r", "foot.vtp"),
          ("toes_r", "bofoot.vtp"))
VERSION = "t44-stdlib-v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vec(text: str) -> list[float]:
    return [float(x) for x in text.split()]


def demo(v: list[float]) -> list[float]:
    # OpenSim +X anterior, +Y superior, +Z right -> demo +X left, +Y head, +Z anterior.
    return [-v[2], v[1], v[0]]


def add(a, b):
    return [x + y for x, y in zip(a, b)]


def parse_mesh(path: Path):
    root = ET.parse(path).getroot()
    piece = root.find(".//Piece")
    points = piece.find("./Points/DataArray")
    polys = piece.find("./Polys")
    arrays = {a.attrib.get("Name"): a for a in polys.findall("DataArray")}
    if points.attrib.get("format") != "ascii" or any(a.attrib.get("format") != "ascii" for a in arrays.values()):
        raise ValueError(f"Only ASCII VTP is supported: {path}")
    raw = vec(points.text)
    if len(raw) != 3 * int(piece.attrib["NumberOfPoints"]):
        raise ValueError(f"VTP point count: {path}")
    vertices = [demo(raw[i:i+3]) for i in range(0, len(raw), 3)]
    conn = [int(n) for n in arrays["connectivity"].text.split()]
    offsets = [int(n) for n in arrays["offsets"].text.split()]
    if len(offsets) != int(piece.attrib["NumberOfPolys"]) or offsets[-1] != len(conn):
        raise ValueError(f"VTP polygon count: {path}")
    faces, start = [], 0
    for stop in offsets:
        poly = conn[start:stop]
        if len(poly) < 3 or any(i < 0 or i >= len(vertices) for i in poly):
            raise ValueError(f"VTP malformed polygon: {path}")
        for j in range(1, len(poly)-1):
            faces += [poly[0], poly[j], poly[j+1]]
        start = stop
    return vertices, faces


def offset(joint, frame_name):
    f = joint.find(f'.//PhysicalOffsetFrame[@name="{frame_name}"]')
    if f is None or any(abs(x) > 1e-12 for x in vec(f.findtext("orientation"))):
        raise ValueError(f"Unexpected offset orientation: {frame_name}")
    return vec(f.findtext("translation"))


def glb_document(mesh_data, translations, path_world):
    binary = bytearray()
    views, accessors, meshes, nodes = [], [], [], []

    def accessor(values, kind, component, target=None):
        while len(binary) % 4:
            binary.append(0)
        start = len(binary)
        if kind == "VEC3":
            flat = [float(c) for row in values for c in row]
            binary.extend(struct.pack("<" + "f"*len(flat), *flat))
            count = len(values)
            mins = [min(v[i] for v in values) for i in range(3)]
            maxs = [max(v[i] for v in values) for i in range(3)]
        else:
            binary.extend(struct.pack("<" + "I"*len(values), *values))
            count = len(values)
            mins, maxs = None, None
        view = {"buffer": 0, "byteOffset": start, "byteLength": len(binary)-start}
        if target:
            view["target"] = target
        views.append(view)
        entry = {"bufferView": len(views)-1, "componentType": component, "count": count, "type": kind}
        if mins is not None:
            entry.update(min=mins, max=maxs)
        accessors.append(entry)
        return len(accessors)-1

    def mesh(vertices, indices, name, material, mode=4):
        pos = accessor(vertices, "VEC3", 5126, 34962)
        idx = accessor(indices, "SCALAR", 5125, 34963)
        meshes.append({"name": name, "primitives": [{"attributes": {"POSITION": pos},
                         "indices": idx, "material": material, "mode": mode}]})
        return len(meshes)-1

    # Fixed tibia and fibula, then source joint frames at q=0.
    nodes = [
        {"name": "tibia_r_fixed", "children": [1, 2, 3]},
        {"name": "tibia_r.vtp"}, {"name": "fibula.vtp"},
        {"name": "ankle_r_pivot_q0", "translation": demo(translations["ankle"]), "children": [4, 5]},
        {"name": "talus.vtp"},
        {"name": "subtalar_r_pivot_q0", "translation": demo(translations["subtalar"]), "children": [6, 7]},
        {"name": "foot.vtp"},
        {"name": "mtp_r_pivot_q0", "translation": demo(translations["mtp"]), "children": [8]},
        {"name": "bofoot.vtp"},
        {"name": "tib_ant_r_model_path_q0"},
    ]
    slot = {"tibia_r.vtp": 1, "fibula.vtp": 2, "talus.vtp": 4,
            "foot.vtp": 6, "bofoot.vtp": 8}
    palette = {"tibia_r.vtp": 0, "fibula.vtp": 1, "talus.vtp": 2,
               "foot.vtp": 3, "bofoot.vtp": 4}
    for name, (vertices, faces) in mesh_data.items():
        nodes[slot[name]]["mesh"] = mesh(vertices, faces, name, palette[name])
    nodes[9]["mesh"] = mesh(path_world, [0, 1, 1, 2], "tib_ant_r_model_path_q0", 5, 1)
    colors = ([.85,.81,.72,1], [.72,.72,.68,1], [.83,.61,.36,1],
              [.44,.7,.8,1], [.6,.8,.62,1], [.96,.22,.17,1])
    materials = [{"name": n, "pbrMetallicRoughness": {"baseColorFactor": c,
                 "metallicFactor": 0, "roughnessFactor": 0.85}, "doubleSided": True}
                 for n, c in zip([*slot.keys(), "model path, not attachment surface"], colors)]
    doc = {"asset": {"version": "2.0", "generator": VERSION},
           "scene": 0, "scenes": [{"name": "OpenSim Gait2392 right ankle rest, separate demo", "nodes": [0, 9]}],
           "nodes": nodes, "meshes": meshes, "materials": materials,
           "buffers": [{"byteLength": len(binary)}], "bufferViews": views, "accessors": accessors}
    payload = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode()
    payload += b" " * ((-len(payload)) % 4)
    binary += b"\0" * ((-len(binary)) % 4)
    total = 12 + 8 + len(payload) + 8 + len(binary)
    return struct.pack("<4sII", b"glTF", 2, total) + struct.pack("<I4s", len(payload), b"JSON") + payload + struct.pack("<I4s", len(binary), b"BIN\0") + binary


def build():
    root = ET.parse(MODEL).getroot()
    joints = {n: root.find(f'.//CustomJoint[@name="{n}"]') for n in ("ankle_r", "subtalar_r", "mtp_r")}
    if any(j is None for j in joints.values()):
        raise ValueError("Missing source joint")
    if [j.find(".//Coordinate").findtext("default_value") for j in joints.values()] != ["0", "0", "0"]:
        raise ValueError("Unexpected default coordinate")
    translations = {"ankle": offset(joints["ankle_r"], "tibia_r_offset"),
                    "subtalar": offset(joints["subtalar_r"], "talus_r_offset"),
                    "mtp": offset(joints["mtp_r"], "calcn_r_offset")}
    for j, child in (("ankle_r", "talus_r_offset"), ("subtalar_r", "calcn_r_offset"), ("mtp_r", "toes_r_offset")):
        if any(abs(v) > 1e-12 for v in offset(joints[j], child)):
            raise ValueError(f"Unexpected child offset: {j}")
    axes = {}
    for name, joint in joints.items():
        axis = next(x for x in joint.findall(".//SpatialTransform/TransformAxis") if x.findtext("coordinates"))
        axes[name] = vec(axis.findtext("axis"))
        function = axis.find("LinearFunction")
        if function is None or vec(function.findtext("coefficients")) != [1, 0]:
            raise ValueError(f"Unexpected joint coordinate function: {name}")
        for other in joint.findall(".//SpatialTransform/TransformAxis"):
            if other is not axis and (other.findtext("coordinates") or other.findtext("Constant/value") != "0"):
                raise ValueError(f"Unexpected coupled/nonzero transform: {name}")
        if not math.isclose(math.sqrt(sum(x*x for x in axes[name])), 1, abs_tol=1e-5):
            raise ValueError(f"Non-unit source axis: {name}")
    muscle = root.find('.//Thelen2003Muscle[@name="tib_ant_r"]')
    points = []
    for p in muscle.findall(".//PathPoint"):
        parent = p.findtext("socket_parent_frame").split("/")[-1]
        local = vec(p.findtext("location"))
        if parent not in ("tibia_r", "calcn_r"):
            raise ValueError(f"Unexpected path body: {parent}")
        origin = [0,0,0] if parent == "tibia_r" else add(translations["ankle"], translations["subtalar"])
        points.append({"id": p.attrib["name"], "body": parent, "localM": local,
                       "restWorldSourceM": add(origin, local), "restWorldSceneM": demo(add(origin, local))})
    if [p["id"] for p in points] != ["tib_ant_r-P1", "tib_ant_r-P2", "tib_ant_r-P3"]:
        raise ValueError("Unexpected model path points")
    mesh_data = {name: parse_mesh(GEOMETRY/name) for _, name in MESHES}
    for body_name, mesh_name in MESHES:
        body = root.find(f'.//Body[@name="{body_name}"]')
        attached = next((m for m in body.findall('.//Mesh') if m.findtext('mesh_file') == mesh_name), None)
        if attached is None or attached.findtext('socket_frame') != '..' or vec(attached.findtext('scale_factors')) != [1, 1, 1]:
            raise ValueError(f"Unexpected source geometry frame/scale: {body_name}/{mesh_name}")
    glb = glb_document(mesh_data, translations, [p["restWorldSceneM"] for p in points])
    source_files = [MODEL, *(GEOMETRY/name for _, name in MESHES)]
    geometry_stats = {name: {"sourceBody": body, "vertexCount": len(mesh_data[name][0]),
                             "triangleCount": len(mesh_data[name][1])//3,
                             "sha256": sha(GEOMETRY/name)} for body, name in MESHES}
    positions = {"tibia_r": [0,0,0], "talus_r": translations["ankle"],
                 "calcn_r": add(translations["ankle"], translations["subtalar"]),
                 "toes_r": add(add(translations["ankle"], translations["subtalar"]), translations["mtp"])}
    manifest = {
      "schemaVersion": "T44-1", "generatorVersion": VERSION,
      "generatorScript": {"path": str(Path(__file__).resolve().relative_to(ROOT)),
                          "sha256": sha(Path(__file__).resolve())},
      "status": "static_input_needs_review", "model": "OpenSim Gait2392 Simbody, Thelen2003 muscle",
      "sourceModel": {"path": str(MODEL.relative_to(ROOT)), "sha256": sha(MODEL)},
      "sourceGeometry": geometry_stats,
      "license": {"id": "CC-BY-3.0", "basis": "Exact .osim credits line 42 and OpenSim Gait2392 model catalog",
                  "attribution": "Delp, Loan, Hoy, Zajac, Topp, Rosen, Thelen, Anderson, Seth / OpenSim Gait2392. Derived static geometry; CC BY 3.0."},
      "sourceFrame": {"id": "OpenSim_Gait2392_tibia_r_local_q0", "unit": "m", "axes": ["anterior", "superior", "patient_right"]},
      "sceneFrame": {"id": "HA_OSIM_GAIT2392_TIBIA_LOCAL_XLEFT_YHEAD_ZANTERIOR_M", "unit": "m", "axes": ["patient_left", "head", "anterior"]},
      "sourceToSceneMatrixColumnMajor": [0,0,1,0, 0,1,0,0, -1,0,0,0, 0,0,0,1],
      "matrixDescription": "scene=(-source_z, source_y, source_x), scale 1, no BP3D registration",
      "demoSceneSwitchNoticeKo": "움직임 시범은 별도 OpenSim 모형으로 전환됩니다.",
      "canonicalJointId": "HA-S-JOINT-R-ANKLE-TALOCRURAL",
      "canonicalActionId": "HA-JA-T44-R-TIBANT-ANKLE-DF",
      "jointBinding": {"sourceJoint": "ankle_r", "sourceCoordinate": "ankle_angle_r", "defaultRadians": 0,
        "coordinateFunction": "rotation1 = 1*ankle_angle_r + 0; other rotation/translation axes Constant(0)",
        "fixedBody": "tibia_r", "movingBody": "talus_r", "movingSubtree": ["talus_r", "calcn_r", "toes_r"],
        "pivotSourceTibiaLocalM": translations["ankle"], "pivotSceneTibiaLocalM": demo(translations["ankle"]),
        "axisSourceJointFrame": axes["ankle_r"], "axisSceneJointFrame": demo(axes["ankle_r"]),
        "positiveDirection": "source model positive rotation1; dorsiflexion interpretation from right foot anterior lever direction; needs human anatomy review",
        "scenePivotNode": "ankle_r_pivot_q0"},
      "restPose": {"coordinateRadians": {"ankle_angle_r": 0, "subtalar_angle_r": 0, "mtp_angle_r": 0},
                   "bodyOriginsSourceTibiaLocalM": positions,
                   "bodyOriginsSceneTibiaLocalM": {k: demo(v) for k,v in positions.items()},
                   "notNeutralClinicalClaim": True},
      "otherSourceJoints": {"subtalar_r": {"pivotSourceTalusLocalM": translations["subtalar"], "axisSource": axes["subtalar_r"]},
                            "mtp_r": {"pivotSourceCalcnLocalM": translations["mtp"], "axisSource": axes["mtp_r"]}},
      "modelPath": {"id": "tib_ant_r", "kind": "simplified_source_model_line_not_attachment_surface",
                    "points": points, "boneLocalEndpointIds": ["tib_ant_r-P1", "tib_ant_r-P3"]},
      "validationLandmarks": [
        {"name": "ankle pivot", "sourceM": translations["ankle"], "sceneM": demo(translations["ankle"]), "residualM": 0},
        {"name": "subtalar pivot", "sourceM": positions["calcn_r"], "sceneM": demo(positions["calcn_r"]), "residualM": 0},
        {"name": "mtp pivot", "sourceM": positions["toes_r"], "sceneM": demo(positions["toes_r"]), "residualM": 0},
        *({"name": p["id"], "sourceM": p["restWorldSourceM"], "sceneM": p["restWorldSceneM"], "residualM": 0} for p in points)],
      "residualAcceptance": {"sameSourceAlgebraToleranceM": 1e-6, "crossModelRegistration": "not_attempted_no_shared_landmarks"},
      "staticScene": {"path": str((OUT/"right-ankle-rest.glb").relative_to(ROOT)),
                      "sha256": hashlib.sha256(glb).hexdigest(), "selfContained": True, "hasAnimation": False},
      "provenanceNote": "All bone meshes and path points derive from the same OpenSim model; BodyParts3D FJ3385 is not identified or mapped."
    }
    return glb, manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Compare regenerated output without writing")
    args = parser.parse_args()
    glb, manifest = build()
    path_glb = OUT / "right-ankle-rest.glb"
    path_json = OUT / "joint-binding-t44.json"
    data = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    if args.check:
        assert path_glb.read_bytes() == glb, "GLB differs"
        assert path_json.read_bytes() == data, "Manifest differs"
        print("T44 static scene and manifest reproducible")
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        path_glb.write_bytes(glb)
        path_json.write_bytes(data)
        print(f"{path_glb}: {len(glb)} bytes sha256={hashlib.sha256(glb).hexdigest()}")


if __name__ == "__main__":
    main()
