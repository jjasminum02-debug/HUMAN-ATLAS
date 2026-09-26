"""Convert the five acquired T13 bones without changing the T07 GLB or OBJ inputs."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONVERTER = ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py"
TRANSFER = ROOT / "work/evidence/T13/source-transfer.json"
ADDITIONAL = ROOT / "work/evidence/T13/additional-transfer.json"
GLB_REL = "atlas-data/assets/derived-glb/bodyparts3d-r4-t13-right-bones/right-bones.glb"
MANIFEST = ROOT / "atlas-data/manifests/derived-bones-t13.json"
MODEL_ID = "HA-MODEL-BP3D4-R4-T13-RIGHT-BONES-STATIC"


def main() -> None:
    spec = importlib.util.spec_from_file_location("t07_converter", CONVERTER)
    assert spec and spec.loader
    conv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(conv)
    conv.MODEL_ID = MODEL_ID
    transfer = json.loads(TRANSFER.read_text())
    additional = json.loads(ADDITIONAL.read_text())
    assert all(additional[key] == transfer[key] for key in ("sourceArchiveUrl", "archiveSizeBytes", "archiveLastModified", "archiveEtag", "licensePage", "requiredCredit", "sourceCoordinates"))
    source_assets = sorted(transfer["assets"] + additional["assets"], key=lambda row: row["fileId"])
    source = json.loads((ROOT / "atlas-data/manifests/assets.json").read_text())
    assert transfer["sourceArchiveUrl"] == source["source"]["archiveUrl"]
    assert transfer["requiredCredit"] == source["license"]["archivePageRequiredCredit"]
    structure_by_file = {
        "FJ3308": "HA-S-NAVICULAR",
        "FJ3351": "HA-S-METATARSAL-1",
        "FJ3359": "HA-S-METATARSAL-5",
        "FJ3365": "HA-S-FEMUR",
        "FJ3377": "HA-S-MEDIAL-CUNEIFORM",
        "FJ3364": "HA-S-CUBOID",
        "FJ3353": None, "FJ3355": None, "FJ3357": None,
    }
    catalog = json.loads((ROOT / "atlas-data/catalog/canonical-catalog.json").read_text())
    structures = {row["id"]: row for row in catalog["entities"]["structures"]}
    inputs = []
    for row in source_assets:
        assert row["fileId"] in structure_by_file
        assert structure_by_file[row["fileId"]] is None or structure_by_file[row["fileId"]] in structures
        path = ROOT / row["localPath"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
        vertices, normals, triangles = conv.parse_obj(path)
        assert max(vertex[0] for vertex in vertices) < 0
        inputs.append({
            "file_id": row["fileId"], "source_path": path, "source_sha256": row["sha256"],
            "source_relative_path": row["localPath"],
            "asset": {"vertex_count": len(vertices), "polygon_count": len(triangles),
                      "bytes": row["bytes"], "representation_id": row["representationId"],
                      "concept_id": row["externalConceptId"]},
        })
    assert len(inputs) == 9
    glb, mesh_nodes = conv.build_glb(inputs)
    output = ROOT / GLB_REL
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(glb)
    digest = hashlib.sha256(glb).hexdigest()
    asset_rows = []
    expected_nodes = []
    for record, source_row in zip(mesh_nodes, source_assets):
        file_id = record["sourceFileId"]
        assert file_id == source_row["fileId"]
        asset_rows.append({
            "id": record["meshAssetId"], "revision": "BP3D-R4-T13-BONES-GLB-V1",
            "sourceId": conv.SOURCE_ID, "hash": digest, "uri": GLB_REL,
            "format": "glb", "units": "m", "axes": {
                "frameId": conv.ATLAS_FRAME, "handedness": "right", "positiveX": "patient_left",
                "positiveY": "head", "positiveZ": "anterior",
            },
            "pose": source["geometry"]["pose"], "laterality": "right",
            "licenseId": conv.LICENSE_ID, "topologyHash": record["topologySha256"],
        })
        asset_rows[-1]["pose"] = {
            "id": conv.POSE_ID,
            "description": source["geometry"]["pose"]["description"],
        }
        expected_nodes.append({
            "meshAssetId": record["meshAssetId"], "nodeIndex": record["nodeIndex"], "meshIndex": record["meshIndex"],
            "sourceName": source_row["sourceName"], "sourceFileId": file_id,
            "targetEntityId": structure_by_file[file_id], "targetEntityType": "structure",
            "relationStatus": "provisional_structure_mesh_context" if structure_by_file[file_id] else "source_verified_whole_bone_canonical_id_unconfirmed",
            "reviewState": "needs_review",
        })
    manifest = {
        "manifestVersion": "T13-derived-bones-v2", "modelId": MODEL_ID,
        "sourceId": conv.SOURCE_ID, "sourceArchiveUrl": transfer["sourceArchiveUrl"],
        "sourceLicenseUrl": transfer["licensePage"], "requiredCredit": transfer["requiredCredit"],
        "sourceArchiveEtag": transfer["archiveEtag"], "sourceTableUrls": {
            "conceptRepresentation": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_parts_list_e.txt",
            "elementMeshMapping": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_element_parts.txt",
        },
        "transform": {
            "sourceUnits": "mm", "targetUnits": "m", "sourceToAtlas": "[x,z,-y]/1000",
            "matrix": [[0.001, 0, 0], [0, 0, 0.001], [0, -0.001, 0]],
            "frameId": conv.ATLAS_FRAME, "handedness": "right", "poseId": conv.POSE_ID,
            "poseLimit": source["geometry"]["pose"]["description"],
        },
        "glb": {"uri": GLB_REL, "bytes": len(glb), "sha256": digest, "meshCount": len(mesh_nodes)},
        "sourceAssets": source_assets, "sourceTableSha256": additional["sourceTableSha256"], "meshNodes": mesh_nodes,
        "meshAssets": asset_rows, "viewerNodes": expected_nodes,
        "reviewState": "needs_review",
        "annotationBoundary": "Whole-bone context only; no attachment surface or triangle is asserted.",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"glbSha256": digest, "bytes": len(glb), "meshes": len(mesh_nodes)}))


if __name__ == "__main__":
    main()
