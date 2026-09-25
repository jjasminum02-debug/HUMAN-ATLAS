#!/usr/bin/env python3
"""Recheck T07 source, GLB structure/geometry, mappings and repeatability."""

from __future__ import annotations

import hashlib
import json
import math
import struct
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T07"
PRIMARY_GLB = ROOT / "atlas-data/assets/derived-glb/bodyparts3d-r4-right-lower-leg/right-lower-leg.glb"
REPEAT_GLB = EVIDENCE / "repeat-run/right-lower-leg.glb"
PRIMARY_MANIFEST = ROOT / "atlas-data/manifests/derived-assets-t07.json"
REPEAT_MANIFEST = EVIDENCE / "repeat-run/derived-assets-t07.json"
T02_MANIFEST = ROOT / "atlas-data/manifests/assets.json"
T02_CROSSWALK = ROOT / "work/evidence/T02/source-crosswalk.json"
CANONICAL = ROOT / "atlas-data/catalog/canonical-catalog.json"
T04_CROSSWALK = ROOT / "atlas-data/catalog/source-crosswalk.json"
SCHEMA_VALIDATOR = ROOT / "atlas-data/schemas/validate.py"
ATLAS_FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
LICENSE_ID = "LIC-BP3D-LSDB-ARCHIVE-CC-BY-4.0"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
EXPECTED_CREDIT = (
    "BodyParts3D, © The Database Center for Life Science licensed under "
    "CC Attribution 4.0 International"
)
MAX_BOUNDS_ERROR_M = 1e-6
EXPECTED_OPENSIM_HEAD = "d9b05d470b1a481c222372c85b75772faf8f7792"


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_preservation():
    before_path = EVIDENCE / "preexisting-files-before.sha256"
    before = {}
    for line in before_path.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split(None, 1)
        before[relative.strip()] = digest
    after = {relative: file_hash(ROOT / relative) for relative in before}
    after_path = EVIDENCE / "preexisting-files-after.sha256"
    after_path.write_text(
        "".join("{}  {}\n".format(after[name], name) for name in before),
        encoding="utf-8",
    )
    changed = [name for name in before if before[name] != after[name]]
    opensim_head = subprocess.run(
        ["git", "-C", "OpenSim_Models", "rev-parse", "HEAD"],
        cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
    )
    opensim_status = subprocess.run(
        ["git", "-C", "OpenSim_Models", "status", "--porcelain"],
        cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
    )
    opensim_diff = subprocess.run(
        ["git", "-C", "OpenSim_Models", "diff", "--exit-code"],
        cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
    )
    opensim_cached_diff = subprocess.run(
        ["git", "-C", "OpenSim_Models", "diff", "--cached", "--exit-code"],
        cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
    )
    opensim_unchanged = (
        opensim_head.returncode == 0
        and opensim_head.stdout.strip() == EXPECTED_OPENSIM_HEAD
        and opensim_status.returncode == 0
        and not opensim_status.stdout.strip()
        and opensim_diff.returncode == 0
        and opensim_cached_diff.returncode == 0
    )
    result = {
        "preexistingHashesBeforePath": "work/evidence/T07/preexisting-files-before.sha256",
        "preexistingHashesAfterPath": "work/evidence/T07/preexisting-files-after.sha256",
        "preexistingFileCount": len(before),
        "preexistingFilesUnchanged": not changed,
        "changedPreexistingFiles": changed,
        "opensimExpectedHead": EXPECTED_OPENSIM_HEAD,
        "opensimHeadAfter": opensim_head.stdout.strip(),
        "opensimStatusAfter": opensim_status.stdout.strip(),
        "opensimWorkingAndIndexDiffClean": opensim_diff.returncode == 0 and opensim_cached_diff.returncode == 0,
        "opensimUnchanged": opensim_unchanged,
    }
    (EVIDENCE / "preservation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    check(not changed, "pre-existing user/design/schema file hash changed: " + ", ".join(changed))
    check(opensim_unchanged, "OpenSim_Models checkout changed or is not clean")
    return result


def parse_source_obj(path):
    vertices = []
    normals = []
    triangles = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        fields = raw.strip().split()
        if not fields or fields[0].startswith("#"):
            continue
        if fields[0] == "v":
            check(len(fields) == 4, "{}:{} has unsupported vertex form".format(path, line_no))
            vertex = tuple(float(value) for value in fields[1:4])
            check(all(math.isfinite(value) for value in vertex), "non-finite source vertex")
            vertices.append(vertex)
        elif fields[0] == "vn":
            check(len(fields) == 4, "{}:{} has unsupported normal form".format(path, line_no))
            normal = tuple(float(value) for value in fields[1:4])
            length = math.sqrt(sum(value * value for value in normal))
            check(abs(length - 1.0) <= 1e-5, "source normal is not unit length")
            normals.append(normal)
        elif fields[0] == "f":
            check(len(fields) == 4, "{}:{} is not a triangle".format(path, line_no))
            indices = []
            normal_indices = []
            for token in fields[1:4]:
                components = token.split("/")
                check(len(components) == 3 and components[2], "face has no vertex normal")
                value = int(components[0])
                check(value != 0, "OBJ face index zero")
                index = value - 1 if value > 0 else len(vertices) + value
                check(0 <= index < len(vertices), "OBJ face index out of range")
                indices.append(index)
                normal_value = int(components[2])
                check(normal_value != 0, "OBJ normal index zero")
                normal_index = normal_value - 1 if normal_value > 0 else len(normals) + normal_value
                check(0 <= normal_index < len(normals), "OBJ normal index out of range")
                normal_indices.append(normal_index)
            check(indices == normal_indices, "per-vertex normals require reindexing")
            triangles.append(tuple(indices))
    check(len(normals) == len(vertices), "source normals and vertices differ in count")
    return vertices, normals, triangles


def bounds(values):
    return {
        "min": [min(row[axis] for row in values) for axis in range(3)],
        "max": [max(row[axis] for row in values) for axis in range(3)],
    }


def max_bounds_delta(left, right):
    return max(
        abs(left[side][axis] - right[side][axis])
        for side in ("min", "max")
        for axis in range(3)
    )


def decode_glb(path):
    data = path.read_bytes()
    check(len(data) >= 28, "GLB is shorter than minimum header plus chunks")
    magic, version, declared_length = struct.unpack_from("<4sII", data, 0)
    check(magic == b"glTF", "GLB magic mismatch")
    check(version == 2, "GLB container version is not 2")
    check(declared_length == len(data), "GLB declared length differs from file size")
    chunks = []
    offset = 12
    while offset < len(data):
        check(offset % 4 == 0, "GLB chunk does not start on 4-byte boundary")
        check(offset + 8 <= len(data), "truncated GLB chunk header")
        length, kind = struct.unpack_from("<II", data, offset)
        offset += 8
        check(length % 4 == 0, "GLB chunk length is not 4-byte aligned")
        check(offset + length <= len(data), "truncated GLB chunk data")
        chunks.append((kind, data[offset : offset + length]))
        offset += length
    check(offset == len(data), "GLB chunks do not consume the file")
    check([kind for kind, _ in chunks] == [0x4E4F534A, 0x004E4942], "GLB must contain JSON then one BIN chunk")
    gltf = json.loads(chunks[0][1].rstrip(b" ").decode("utf-8"))
    binary = chunks[1][1]
    check(gltf["asset"]["version"] == "2.0", "glTF asset.version mismatch")
    check(len(gltf["buffers"]) == 1 and "uri" not in gltf["buffers"][0], "GLB must store one buffer in BIN")
    declared_buffer_bytes = gltf["buffers"][0]["byteLength"]
    check(declared_buffer_bytes <= len(binary) <= declared_buffer_bytes + 3, "BIN length/padding mismatch")
    return gltf, binary, data


def semantic_hash(mesh_id, positions, indices):
    digest = hashlib.sha256()
    digest.update(b"HUMAN-ATLAS-T07-GEOMETRY-V1\0")
    digest.update(mesh_id.encode("ascii"))
    digest.update(b"\0")
    digest.update(struct.pack("<Q", len(positions)))
    digest.update(positions)
    digest.update(struct.pack("<Q", len(indices)))
    digest.update(indices)
    return digest.hexdigest()


def topology_hash(mesh_id, vertex_count, indices):
    digest = hashlib.sha256()
    digest.update(b"HUMAN-ATLAS-T07-TOPOLOGY-V1\0")
    digest.update(mesh_id.encode("ascii"))
    digest.update(b"\0")
    digest.update(struct.pack("<QQ", vertex_count, len(indices)))
    digest.update(indices)
    return digest.hexdigest()


def validate_gltf_meshes(gltf, binary, manifest, t02_assets):
    nodes = gltf["nodes"]
    meshes = gltf["meshes"]
    accessors = gltf["accessors"]
    views = gltf["bufferViews"]
    check(len(nodes) == len(meshes) == len(manifest["meshNodes"]) == 11, "expected 11 GLB mesh nodes")
    check(gltf["scenes"][gltf["scene"]]["nodes"] == list(range(11)), "scene must include all stable mesh nodes once")
    by_id = {row["meshAssetId"]: row for row in manifest["meshNodes"]}
    check(len(by_id) == 11, "duplicate mesh asset IDs in mesh-node manifest")
    decoded = {}
    for node_index, node in enumerate(nodes):
        mesh_id = node["name"]
        check(mesh_id in by_id, "GLB node ID is absent from manifest: " + mesh_id)
        check(node["mesh"] == node_index, "stable node/mesh index mismatch")
        mesh = meshes[node["mesh"]]
        check(mesh["name"] == mesh_id and len(mesh["primitives"]) == 1, "mesh/node identity mismatch")
        primitive = mesh["primitives"][0]
        check(primitive.get("mode", 4) == 4, "primitive is not TRIANGLES")
        pos_accessor = accessors[primitive["attributes"]["POSITION"]]
        normal_accessor = accessors[primitive["attributes"]["NORMAL"]]
        idx_accessor = accessors[primitive["indices"]]
        check(pos_accessor["componentType"] == 5126 and pos_accessor["type"] == "VEC3", "POSITION must be float32 VEC3")
        check(normal_accessor["componentType"] == 5126 and normal_accessor["type"] == "VEC3", "NORMAL must be float32 VEC3")
        check(normal_accessor["count"] == pos_accessor["count"], "NORMAL count must match POSITION")
        check(idx_accessor["type"] == "SCALAR" and idx_accessor["componentType"] in (5123, 5125), "indices must use unsigned integer SCALAR")
        pview = views[pos_accessor["bufferView"]]
        nview = views[normal_accessor["bufferView"]]
        iview = views[idx_accessor["bufferView"]]
        pstart = pview.get("byteOffset", 0) + pos_accessor.get("byteOffset", 0)
        nstart = nview.get("byteOffset", 0) + normal_accessor.get("byteOffset", 0)
        istart = iview.get("byteOffset", 0) + idx_accessor.get("byteOffset", 0)
        pbytes = pos_accessor["count"] * 12
        nbytes = normal_accessor["count"] * 12
        isize = 2 if idx_accessor["componentType"] == 5123 else 4
        ibytes = idx_accessor["count"] * isize
        check(pview["byteLength"] == pbytes and nview["byteLength"] == nbytes and iview["byteLength"] == ibytes, "accessor byteLength mismatch")
        check(pstart % 4 == 0 and nstart % 4 == 0 and istart % 4 == 0, "accessor data is not 4-byte aligned")
        check(pstart + pbytes <= len(binary) and nstart + nbytes <= len(binary) and istart + ibytes <= len(binary), "accessor data exceeds BIN chunk")
        position_bytes = binary[pstart : pstart + pbytes]
        normal_bytes = binary[nstart : nstart + nbytes]
        index_bytes = binary[istart : istart + ibytes]
        count = pos_accessor["count"]
        positions = list(struct.iter_unpack("<fff", position_bytes))
        normals = list(struct.iter_unpack("<fff", normal_bytes))
        if isize == 2:
            indices = list(struct.unpack("<{}H".format(idx_accessor["count"]), index_bytes))
        else:
            indices = list(struct.unpack("<{}I".format(idx_accessor["count"]), index_bytes))
        check(len(indices) % 3 == 0, "triangle index count is not divisible by 3")
        check(all(0 <= index < count for index in indices), "triangle index outside POSITION accessor")
        check(all(abs(math.sqrt(sum(value * value for value in normal)) - 1.0) <= 1e-5 for normal in normals), "GLB normals are not normalized")
        actual_bounds = bounds(positions)
        check(actual_bounds == by_id[mesh_id]["atlasBoundsM"], "GLB accessor bounds differ from node manifest")
        expected_hash = semantic_hash(mesh_id, position_bytes, index_bytes)
        check(expected_hash == by_id[mesh_id]["geometrySha256"], "semantic geometry hash mismatch for " + mesh_id)
        mesh_asset = next(row for row in manifest["meshAssets"] if row["id"] == mesh_id)
        expected_topology = topology_hash(mesh_id, count, index_bytes)
        check(expected_topology == mesh_asset["topologyHash"] == by_id[mesh_id]["topologySha256"], "topology hash mismatch for " + mesh_id)
        check(mesh.get("extras", {}).get("stableMeshAssetId") == mesh_id, "mesh extras stable ID mismatch")
        check(node.get("extras", {}).get("stableModelId") == manifest["modelId"], "node stable model ID mismatch")
        check(manifest["modelId"] == "HA-MODEL-BP3D4-R4-RIGHT-LOWER-LEG-STATIC", "region model ID changed")
        check(node.get("extras", {}).get("sourceFileId") == by_id[mesh_id]["sourceFileId"], "node source FJ ID mismatch")
        decoded[mesh_id] = {
            "positions": position_bytes,
            "normals": normal_bytes,
            "indices": index_bytes,
            "positionValues": positions,
            "indicesValues": indices,
            "vertexCount": count,
            "triangleCount": len(indices) // 3,
            "bounds": actual_bounds,
            "semanticSha256": expected_hash,
            "normalSha256": hashlib.sha256(normal_bytes).hexdigest(),
        }
    return decoded


def validate_sources_and_contract(manifest, decoded):
    t02 = read_json(T02_MANIFEST)
    t02_source_xwalk = read_json(T02_CROSSWALK)
    catalog = read_json(CANONICAL)
    t04 = read_json(T04_CROSSWALK)
    mesh_xwalk = read_json(ROOT / "atlas-data/manifests/mesh-crosswalk-t07.json")
    asset_rows = {row["file_id"]: row for row in t02["acquiredAssets"]}
    muscle_rows = {row["element_file_id"]: row for row in t02_source_xwalk["pilot_muscles"]}
    bone_rows = {
        row["element_file_id"]: row
        for row in t02_source_xwalk["region_bone_inventory"]
        if row.get("availability") == "subset_acquired"
    }
    t04_rows = {row["elementFileId"]: row for row in t04["bodyParts3dMappings"]}
    config_rows = {row["fileId"]: row for row in mesh_xwalk["entries"]}
    check(mesh_xwalk.get("reviewState") == "needs_review", "source crosswalk must stay needs_review")
    canonical_muscles = {row["id"]: row for row in catalog["entities"]["muscleConcepts"]}
    canonical_structures = {row["id"]: row for row in catalog["entities"]["structures"]}
    stable_mesh_ids = {"HA-MESH-BP3D4-" + file_id for file_id in asset_rows}
    check(stable_mesh_ids == set(decoded) and set(asset_rows) == set(config_rows), "T02 acquired, crosswalk, and GLB mesh IDs differ")
    check(t02["geometry"]["sourceUnit"] == "mm" and t02["geometry"]["atlasInternalUnit"] == "m", "T02 coordinate units changed")
    check(t02["geometry"]["sourceToAtlasTransform"]["rotationDeterminant"] == 1, "T02 orientation determinant is not +1")
    transform = manifest["transform"]
    check(transform["targetFrameId"] == ATLAS_FRAME, "T07 frame ID mismatch")
    check(transform["sourceUnits"] == "mm" and transform["targetUnits"] == "m", "T07 units mismatch")
    check(transform["rotationMatrix"] == [[1, 0, 0], [0, 0, 1], [0, -1, 0]], "T07 rotation matrix mismatch")
    check(transform["rotationDeterminant"] == 1 and not transform["reflectionApplied"], "T07 must preserve handedness without reflection")
    sample = (17.0, -23.0, 31.0)
    expected = (0.017, 0.031, 0.023)
    actual = (sample[0] / 1000, sample[2] / 1000, -sample[1] / 1000)
    check(all(abs(a - b) < 1e-15 for a, b in zip(actual, expected)), "known-marker transform check failed")

    max_atlas_bounds_error = 0.0
    for mesh_id, item in decoded.items():
        row = asset_rows[mesh_id.removeprefix("HA-MESH-BP3D4-")]
        source_row = muscle_rows.get(row["file_id"], bone_rows.get(row["file_id"]))
        check(source_row is not None, "no T02 source table locator for " + row["file_id"])
        check(row["concept_id"] == source_row["concept_id"], "FMA crosswalk mismatch")
        check(row["representation_id"] == source_row["representation_id"], "BP crosswalk mismatch")
        source_path = ROOT / t02["assetFolder"] / (row["file_id"] + ".obj")
        check(file_hash(source_path) == row["sha256"], "source OBJ hash changed: " + row["file_id"])
        check(source_path.stat().st_size == row["bytes"], "source OBJ size changed: " + row["file_id"])
        vertices, normals, triangles = parse_source_obj(source_path)
        check(len(vertices) == item["vertexCount"] == row["vertex_count"], "source/GLB vertex count mismatch")
        check(len(triangles) == item["triangleCount"] == row["polygon_count"], "source/GLB triangle count mismatch")
        expected_positions = b"".join(
            struct.pack("<fff", point[0] / 1000, point[2] / 1000, -point[1] / 1000)
            for point in vertices
        )
        expected_normals = b"".join(
            struct.pack("<fff", normal[0], normal[2], -normal[1]) for normal in normals
        )
        source_indices = [index for triangle in triangles for index in triangle]
        expected_indices = struct.pack("<{}H".format(len(source_indices)), *source_indices)
        check(item["positions"] == expected_positions, "transformed GLB positions do not match source OBJ: " + row["file_id"])
        check(item["normals"] == expected_normals, "rotated GLB normals do not match source OBJ: " + row["file_id"])
        check(item["indices"] == expected_indices, "GLB face indices/winding do not match source OBJ: " + row["file_id"])
        src = bounds(vertices)
        atlas = item["bounds"]
        check(src["max"][0] < 0 and atlas["max"][0] < 0, "right-side x<0 check failed: " + row["file_id"])
        expected_t02 = row["derived_atlas_bounds_m"]
        delta = max(
            abs(atlas[axis][i] - expected_t02[side][i])
            for side, axis in (("min_m", "min"), ("max_m", "max"))
            for i in range(3)
        )
        max_atlas_bounds_error = max(max_atlas_bounds_error, delta)
        check(delta <= MAX_BOUNDS_ERROR_M, "T02/GLB Atlas bounds differ by more than 1 micron: " + row["file_id"])
        relation = config_rows[row["file_id"]]
        target_id = relation["targetEntityId"]
        if row["kind"] == "muscle":
            t04row = t04_rows[row["file_id"]]
            check(target_id == t04row["stableConceptId"], "muscle internal target differs from T04 crosswalk")
            check(t04row["externalConceptId"] == row["concept_id"] and t04row["externalRepresentationId"] == row["representation_id"], "muscle source IDs differ from T04 crosswalk")
            target = canonical_muscles[target_id]
            check(target["entityType"] == relation["targetEntityType"], "muscle target type mismatch")
        elif target_id is None:
            check(row["concept_id"] == "FMA24482", "only unresolved source mapping is the T02 talus mesh")
            check(relation["relationStatus"].startswith("unmapped_"), "unmapped target needs explicit status")
        else:
            check(target_id in canonical_structures and canonical_structures[target_id]["kind"] == "bone", "bone target missing from canonical structures")
        node_record = next(record for record in manifest["meshNodes"] if record["meshAssetId"] == mesh_id)
        check(node_record["normalSha256"] == item["normalSha256"] and node_record["normalCount"] == len(normals), "normal provenance mismatch")
        check(node_record["sourceSha256"] == row["sha256"], "manifest source hash mismatch")
        check(node_record["sourceTableLocators"] == source_row["table_rows"], "source table row locators mismatch")
    check(len(manifest["meshCrosswalk"]) == 11, "all source meshes must have a crosswalk row")
    check(all(row["laterality"] == "right" for row in manifest["meshAssets"]), "meshAsset laterality must be right")
    check(all(row["reviewState"] == "needs_review" for row in manifest["meshCrosswalk"]), "crosswalk cannot be promoted without human review")
    check(not manifest["validation"]["anatomyIdentityReviewed"], "T07 must not claim anatomy identity review")
    check(not manifest["validation"]["attachmentAnnotationsCreated"], "T07 must not create annotations")
    check(not manifest["validation"]["publicDistribution"], "T07 must not publish")

    credit = t02["license"]["archivePageRequiredCredit"]
    check(credit == EXPECTED_CREDIT == manifest["attribution"]["requiredCreditVerbatim"], "archive attribution mismatch")
    legacy = t02["acquiredAssets"][0]["embedded_license_header"]
    check(manifest["attribution"]["embeddedLegacyObjNotice"] == legacy, "legacy OBJ notice was not recorded")
    check(all(row["embedded_license_header"] == legacy for row in t02["acquiredAssets"]), "T02 embedded notices differ; attribution needs review")
    check(manifest["attribution"]["licenseId"] == LICENSE_ID, "license ID mismatch")
    return {"maxAtlasBoundsErrorMeters": max_atlas_bounds_error}


def integrate_t03_dataset(manifest):
    dataset = read_json(CANONICAL)
    source = {
        "id": SOURCE_ID,
        "title": "BodyParts3D downloadable dataset, Release 4.0",
        "authors": ["Database Center for Life Science (DBCLS), Japan Science and Technology Agency NBDC LSDB Archive"],
        "edition": "Data Release 4.0; release data updated 2013-06-19; LSDB Archive license metadata updated 2025-02-27",
        "year": 2013,
        "urlOrLocalRef": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html",
        "accessDate": "2026-09-25",
        "license": {
            "id": LICENSE_ID,
            "name": "Creative Commons Attribution 4.0 International",
            "spdxId": "CC-BY-4.0",
            "allowedUses": ["internal", "research", "learning", "public_learning", "derivative", "redistribute"],
            "attributionRequired": True,
            "attributionText": EXPECTED_CREDIT,
            "derivativesAllowed": True,
            "redistributionAllowed": True,
        },
    }
    sources = dataset["entities"]["sources"]
    check(all(row["id"] != SOURCE_ID for row in sources), "validation overlay source ID already exists")
    sources.append(source)
    check(not dataset["entities"].get("meshAssets"), "T07 overlay expects no existing catalog mesh assets")
    dataset["entities"]["meshAssets"] = manifest["meshAssets"]
    dataset["revision"] = "T07-validation-overlay-only-not-canonical-catalog"
    overlay_path = EVIDENCE / "t03-validation-dataset.json"
    overlay_path.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(SCHEMA_VALIDATOR), "--dataset", str(overlay_path)],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    result = {
        "command": "python3 atlas-data/schemas/validate.py --dataset work/evidence/T07/t03-validation-dataset.json",
        "exitCode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "overlayNotIngested": True,
        "overlayRevision": dataset["revision"],
    }
    (EVIDENCE / "t03-validator-result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    check(completed.returncode == 0, "T03 validator rejected T07 MeshAsset overlay: " + completed.stdout + completed.stderr)
    return result


def manifest_projection(manifest):
    projected = json.loads(json.dumps(manifest))
    projected["glb"]["uri"] = "<region-glb>"
    for row in projected["meshAssets"]:
        row["uri"] = "<region-glb>"
    return projected


def main():
    primary = read_json(PRIMARY_MANIFEST)
    repeated = read_json(REPEAT_MANIFEST)
    gltf_a, bin_a, bytes_a = decode_glb(PRIMARY_GLB)
    gltf_b, bin_b, bytes_b = decode_glb(REPEAT_GLB)
    check(file_hash(PRIMARY_GLB) == primary["glb"]["sha256"], "primary GLB hash differs from manifest")
    check(file_hash(REPEAT_GLB) == repeated["glb"]["sha256"], "repeat GLB hash differs from repeat manifest")
    check(bytes_a == bytes_b, "two independent converter runs are not byte-identical")
    check(manifest_projection(primary) == manifest_projection(repeated), "two run manifests differ semantically")
    t02_assets = {row["file_id"]: row for row in read_json(T02_MANIFEST)["acquiredAssets"]}
    decoded = validate_gltf_meshes(gltf_a, bin_a, primary, t02_assets)
    contract_result = validate_sources_and_contract(primary, decoded)
    t03_result = integrate_t03_dataset(primary)
    preservation = verify_preservation()
    output = {
        "task": "T07",
        "status": "pass_with_anatomy_review_pending",
        "checks": {
            "t02_actual_assets_only": True,
            "source_obj_hash_and_size_unchanged": True,
            "glb_v2_header_chunks_and_accessors": True,
            "glb_mesh_node_ids_stable_and_unique": True,
            "all_11_vertices_normals_triangles_match_source": True,
            "source_to_atlas_axes_units_and_right_sidedness": True,
            "bounds_match_t02_within_1_micron": True,
            "source_and_canonical_crosswalks_traceable": True,
            "repeated_glb_bytes_identical": True,
            "repeated_semantic_geometry_and_manifest_identical": True,
            "t03_mesh_asset_dataset_overlay_valid": t03_result["exitCode"] == 0,
            "anatomy_review_and_annotations_not_claimed": True,
            "preexisting_user_files_and_opensim_preserved": preservation["preexistingFilesUnchanged"] and preservation["opensimUnchanged"],
        },
        "glb": {
            "path": "atlas-data/assets/derived-glb/bodyparts3d-r4-right-lower-leg/right-lower-leg.glb",
            "sha256": file_hash(PRIMARY_GLB),
            "bytes": len(bytes_a),
            "meshCount": len(decoded),
        },
        "repeatRun": {
            "path": "work/evidence/T07/repeat-run/right-lower-leg.glb",
            "sha256": file_hash(REPEAT_GLB),
            "bytes": len(bytes_b),
            "byteIdentical": bytes_a == bytes_b,
            "semanticMeshCount": len(decoded),
        },
        "meshCountByKind": {
            "muscle": sum(row["kind"] == "muscle" for row in t02_assets.values()),
            "bone": sum(row["kind"] == "bone" for row in t02_assets.values()),
        },
        "unresolvedCrosswalk": [
            {"sourceFileId": row["sourceFileId"], "externalConceptId": row["externalConceptId"], "reason": row["relationStatus"]}
            for row in primary["meshCrosswalk"]
            if row["targetEntityId"] is None
        ],
        "t03Validator": t03_result,
        "preservation": preservation,
        "bounds": contract_result,
        "limitations": [
            "No independent anatomical review of mesh identity, pose, or attachment surfaces.",
            "The T03 catalog has no anatomical instances for laterality-specific MeshMapping and no talus structure; the T07 source crosswalk remains provisional, with talus internal target unresolved.",
            "The Khronos glTF structural requirements were checked locally; no separate Khronos glTF Validator binary was installed or run.",
        ],
    }
    result_path = EVIDENCE / "validation.json"
    result_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
