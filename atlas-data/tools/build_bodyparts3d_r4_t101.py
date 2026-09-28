#!/usr/bin/env python3
"""Reproducibly build and validate the frozen T101 R4 muscle surface extension."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import struct
import sys
import zlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "work/evidence/T101/frozen-source-set.json"
ACQUISITION = ROOT / "work/evidence/T101/source-acquisition.json"
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
SOURCE_CACHE = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t101"
DERIVED = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t101"
OUT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t101"
SOURCE_MANIFEST = OUT / "source-manifest.json"
EXTENSION = OUT / "integration-extension.json"
EVIDENCE = ROOT / "work/evidence/T101/validation.json"
BROWSER_EVIDENCE = ROOT / "work/evidence/T101/browser-validation.json"
T77_MANIFEST = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json"
T95_OVERLAY = ROOT / "atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json"
T79_SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t79/source-manifest.json"
T79_EXTENSION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t79/integration-extension.json"
T50_CONTRACT = ROOT / "work/evidence/T50/scene-contract.md"
T69_DIAGNOSTIC = ROOT / "work/evidence/T69/diagnostic.json"
T69_ASSESSMENT = ROOT / "work/evidence/T69/assessment.json"
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
CHUNK_ID = "t101-lower-limb-muscle"
EXPECTED = ["FJ1393", "FJ1393M", "FJ1394M", "FJ1395", "FJ1395M", "FJ1396", "FJ1396M", "FJ1397M", "FJ1398", "FJ1398M"]
HOLDS = ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"]
BOUNDS = re.compile(r"^#\s*Bounds\(mm\):\s*\(([^)]+)\)-\(([^)]+)\)\s*$")


class BuildError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise BuildError(f"cannot import existing converter: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def unpack_glb(raw: bytes) -> tuple[dict[str, Any], bytes]:
    if len(raw) < 28 or raw[:4] != b"glTF" or struct.unpack_from("<I", raw, 4)[0] != 2:
        raise BuildError("derived file is not a GLB 2.0 container")
    size, kind = struct.unpack_from("<II", raw, 12)
    if kind != 0x4E4F534A:
        raise BuildError("GLB JSON chunk missing")
    doc = json.loads(raw[20:20 + size].decode())
    offset = 20 + size
    binary_size, binary_kind = struct.unpack_from("<II", raw, offset)
    if binary_kind != 0x004E4942:
        raise BuildError("GLB BIN chunk missing")
    binary = raw[offset + 8:offset + 8 + binary_size]
    if len(binary) != binary_size:
        raise BuildError("GLB BIN chunk truncated")
    return doc, binary


def repack_glb(doc: dict[str, Any], binary: bytes) -> bytes:
    encoded = json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    encoded += b" " * (-len(encoded) % 4)
    binary += b"\0" * (-len(binary) % 4)
    total = 12 + 8 + len(encoded) + 8 + len(binary)
    return b"".join((struct.pack("<4sII", b"glTF", 2, total), struct.pack("<II", len(encoded), 0x4E4F534A), encoded,
                     struct.pack("<II", len(binary), 0x004E4942), binary))


def parse_header_bounds(path: Path) -> tuple[str, list[float], str]:
    name = None
    bounds = None
    license_header = None
    with path.open("r", encoding="utf-8", errors="strict") as handle:
        for line in handle:
            if not line.startswith("#"):
                break
            if line.startswith("# English name :"):
                name = line.split(":", 1)[1].strip()
            match = BOUNDS.match(line.rstrip("\r\n"))
            if match:
                bounds = [float(value.strip()) for value in match.group(1).split(",") + match.group(2).split(",")]
            if "license for this database" in line.lower():
                license_header = line.lstrip("# ").strip()
    if not name or not bounds or len(bounds) != 6 or not license_header or not all(math.isfinite(v) for v in bounds):
        raise BuildError(f"OBJ exact name/bounds/license header missing or invalid: {path.name}")
    return name, bounds, license_header


def write_owned(path: Path, raw: bytes, owner: str, frozen_hash: str) -> None:
    if path.exists() and path.read_bytes() != raw:
        try:
            old = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            old = {}
        old_owner = old.get("task")
        old_frozen = old.get("frozenSourceSetSha256")
        if old_owner != owner or old_frozen != frozen_hash:
            raise BuildError(f"refusing to overwrite unowned/differently frozen output: {path.relative_to(ROOT)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def load_inputs() -> dict[str, Any]:
    if not FREEZE.is_file() or not ACQUISITION.is_file():
        raise BuildError("T101 exact source freeze and bounded acquisition receipt are required")
    freeze_raw = FREEZE.read_bytes()
    frozen = json.loads(freeze_raw)
    acquisition_raw = ACQUISITION.read_bytes()
    acquisition = json.loads(acquisition_raw)
    if frozen.get("task") != "T101" or frozen.get("status") != "frozen_before_mesh_acquisition" or frozen.get("sourceElementFileIds") != EXPECTED:
        raise BuildError("T101 frozen ID allowlist/status differs from the exact task")
    if [row.get("sourceElementFileId") for row in frozen.get("assets", [])] != EXPECTED:
        raise BuildError("T101 frozen source mappings are incomplete or out of order")
    if acquisition.get("result") != "pass" or acquisition.get("attemptedIds") != EXPECTED or acquisition.get("fullArchiveDownloaded") is not False or acquisition.get("selectedMemberRangeRequestsOnly") is not True or acquisition.get("allRangeResponsesHttp206") is not True:
        raise BuildError("T101 acquisition did not pass exact selected-member HTTP 206 policy")
    if acquisition.get("frozenSourceSetSha256") != sha(freeze_raw) or acquisition.get("frozenMembershipSha256") != frozen.get("membershipSha256"):
        raise BuildError("T101 acquisition receipt is bound to a different source freeze")
    acquired = acquisition.get("files", [])
    if [row.get("sourceElementFileId") for row in acquired] != EXPECTED or any(row.get("status") != "acquired" for row in acquired):
        raise BuildError("T101 acquisition is not one-to-one for the exact ten members")

    input_hashes = dict(frozen.get("inputSha256", {}))
    paths = [T77_MANIFEST, T95_OVERLAY, T79_SOURCE, T79_EXTENSION, T50_CONTRACT, T69_DIAGNOSTIC, T69_ASSESSMENT]
    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
        if not path.is_file():
            raise BuildError(f"required frozen scene/frame input missing: {rel}")
        input_hashes[rel] = sha(path.read_bytes())
    for rel, expected in frozen.get("inputSha256", {}).items():
        path = ROOT / rel
        if not path.is_file() or sha(path.read_bytes()) != expected:
            raise BuildError(f"frozen T101 input hash changed: {rel}")

    ingest = load_module("ha_t101_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
    converter = load_module("ha_t101_converter", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")
    tables = ingest.load_tables(METADATA)
    metadata_hashes = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in sorted(METADATA.glob("*.txt"))}
    base_raw, overlay_raw = T77_MANIFEST.read_bytes(), T95_OVERLAY.read_bytes()
    t79_source_raw, t79_extension_raw = T79_SOURCE.read_bytes(), T79_EXTENSION.read_bytes()
    if sha(base_raw) != input_hashes["atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json"]:
        raise BuildError("T77 scene manifest differs from T101 freeze")
    if sha(overlay_raw) != input_hashes["atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json"]:
        raise BuildError("T95 product overlay differs from T101 freeze")
    if sha(t79_source_raw) != input_hashes["atlas-data/manifests/bodyparts3d-r4-t79/source-manifest.json"] or sha(t79_extension_raw) != input_hashes["atlas-data/manifests/bodyparts3d-r4-t79/integration-extension.json"]:
        raise BuildError("T79 scene extension/source manifest differs from T101 freeze")

    return {"frozen": frozen, "freezeRaw": freeze_raw, "acquisition": acquisition, "acquisitionRaw": acquisition_raw,
            "acquired": acquired, "inputHashes": input_hashes, "metadataHashes": metadata_hashes, "tables": tables,
            "ingest": ingest, "converter": converter, "baseRaw": base_raw, "overlayRaw": overlay_raw,
            "t79SourceRaw": t79_source_raw, "t79ExtensionRaw": t79_extension_raw}


def convert() -> dict[str, Any]:
    data = load_inputs()
    frozen_by_id = {row["sourceElementFileId"]: row for row in data["frozen"]["assets"]}
    acquired_by_id = {row["sourceElementFileId"]: row for row in data["acquired"]}
    tables, ingest, converter = data["tables"], data["ingest"], data["converter"]
    concepts = {tuple(row) for row in tables["isaConcepts"]}
    elements = {tuple(row) for row in tables["isaCompoundElements"]}
    inclusions = {tuple(row) for row in tables["isaInclusion"]}
    source_names = ingest.load_source_name_map(ROOT)
    source_assets: list[dict[str, Any]] = []
    identity_extras: list[dict[str, Any]] = []
    mesh_inputs: list[dict[str, Any]] = []

    for fid in EXPECTED:
        freeze_row, acquired = frozen_by_id[fid], acquired_by_id[fid]
        source_path = ROOT / acquired["cacheRelativePath"]
        if not source_path.is_file():
            raise BuildError(f"frozen source OBJ missing: {fid}")
        raw = source_path.read_bytes()
        if len(raw) != acquired.get("bytes") or sha(raw) != acquired.get("sha256"):
            raise BuildError(f"source file byte count/SHA-256 mismatch: {fid}")
        crc = f"{zlib.crc32(raw) & 0xffffffff:08x}"
        if crc != acquired.get("sourceCrc32") or crc != acquired.get("archiveMemberCrc32"):
            raise BuildError(f"source OBJ CRC32 differs from selected archive member: {fid}")
        header = ingest.read_obj_header(source_path)
        ingest.validate_obj_source_identity(header, tables)
        name, header_bounds, license_header = parse_header_bounds(source_path)
        official_name = source_names.get(header["conceptId"])
        exact_concept = (header["conceptId"], header["representationId"], official_name)
        if exact_concept not in concepts or tuple(freeze_row["officialConceptRow"]) != exact_concept:
            raise BuildError(f"OBJ header FMA/BP/name does not match exact frozen R4 concept row: {fid}")
        if tuple(freeze_row["officialElementRow"]) not in elements:
            raise BuildError(f"exact frozen FJ/FMA ELEM row absent from R4 IS-A metadata: {fid}")
        if (freeze_row["officialElementRow"][0], freeze_row["officialElementRow"][1].casefold(), fid) not in {
            (row[0], row[1].casefold(), row[2]) for row in tables["isaCompoundElements"]
        }:
            raise BuildError(f"case-folded OBJ exact FMA/name/FJ association missing from official R4 table: {fid}")
        if tuple(freeze_row["officialParentRelationRow"]) not in inclusions:
            raise BuildError(f"exact official IS-A parent relation absent for {fid}")
        if (header["fileId"], header["conceptId"], header["representationId"], header["buildUpLogic"]) != (fid, freeze_row["sourceConceptId"], freeze_row["sourceRepresentationId"], "FMA 3.0 is_a"):
            raise BuildError(f"OBJ header ID/tree/FMA/BP differs from exact frozen relation: {fid}")
        if not official_name or name.casefold() != official_name.casefold() or acquired["header"].get("English name") != name:
            raise BuildError(f"OBJ exact English name header differs from R4 metadata: {fid}")
        extracted_bounds = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", acquired["header"]["Bounds(mm)"])]
        if header_bounds != extracted_bounds:
            raise BuildError(f"OBJ bounds header changed since acquisition receipt: {fid}")
        side = freeze_row.get("sourceSide")
        if side not in {"left", "right"} or side != acquired.get("sourceSide") or freeze_row["sourceSideEvidence"] != acquired.get("sourceSideEvidence"):
            raise BuildError(f"laterality lacks exact, consistent named-source evidence: {fid}")

        vertices, normals, triangles = converter.parse_obj(source_path)
        actual_bounds = [min(v[i] for v in vertices) for i in range(3)] + [max(v[i] for v in vertices) for i in range(3)]
        max_delta = max(abs(header_bounds[i] - actual_bounds[i]) for i in range(6))
        sign_consistent = max(v[0] for v in vertices) < 0 if side == "right" else min(v[0] for v in vertices) > 0
        if not sign_consistent:
            raise BuildError(f"source x-sign contradicts independent exact-name side under T50/T69; no mirroring: {fid}")
        transformed = [converter.transform_vertex(v) for v in vertices]
        project_bounds = [[min(v[i] for v in transformed) for i in range(3)], [max(v[i] for v in transformed) for i in range(3)]]
        geometry = {"sourceVertexCount": len(vertices), "sourceNormalCount": len(normals), "sourceTriangleCount": len(triangles),
                    "sourceHeaderBoundsMm": header_bounds, "sourceActualVertexBoundsMm": actual_bounds,
                    "headerMinusActualBoundsMm": [header_bounds[i] - actual_bounds[i] for i in range(6)],
                    "headerActualBoundsMaxDeltaMm": max_delta, "projectBoundsM": project_bounds,
                    "sideXAxisSanityCheckOnly": {"sideFromExactOfficialName": side, "consistent": sign_consistent}}
        exact_header = {"fileId": header["fileId"], "representationId": header["representationId"],
                        "buildUpLogic": header["buildUpLogic"], "conceptId": header["conceptId"],
                        "englishNameExact": name, "boundsHeaderUnit": "mm", "boundsHeaderMm": header_bounds,
                        "legacyLicenseHeaderExact": license_header}
        identity = {"sourceElementFileId": fid, "sourceConceptId": header["conceptId"], "sourceRepresentationId": header["representationId"],
                    "sourceConceptEnglishName": official_name, "sourceSide": side, "sourceSideEvidence": freeze_row["sourceSideEvidence"],
                    "sourceUnit": "mm_from_exact_OBJ_Bounds_header", "projectUnit": "m", "projectFrame": FRAME,
                    "sourcePose": POSE, "transform": "[x,y,z] source mm -> [x,z,-y] HUMAN ATLAS m; preserve x sign; no mirror/recenter",
                    "humanAnatomyReviewed": False, "publicRedistribution": "held"}
        source_assets.append({**identity, "sourceArchiveTree": "IS-A", "sourceArchiveMemberPath": acquired["memberPath"],
                              "archiveMemberCrc32": acquired["archiveMemberCrc32"], "sourceCrc32": crc,
                              "sourceBytes": len(raw), "sourceSha256": acquired["sha256"], "sourceHeader": exact_header,
                              "officialConceptRow": list(freeze_row["officialConceptRow"]),
                              "officialExactSidePartElementRow": list(freeze_row["officialElementRow"]),
                              "officialPartParentRelationRow": list(freeze_row["officialParentRelationRow"]),
                              "allOfficialSemanticRowsForSameFj": list(freeze_row["allOfficialElementRowsForSameFj"]),
                              "genericAndSideRowsShareOneFjNode": True, "geometry": geometry})
        identity_extras.append(identity)
        mesh_inputs.append({"file_id": fid, "source_path": source_path, "source_relative_path": acquired["cacheRelativePath"],
                            "source_sha256": acquired["sha256"], "asset": {"bytes": len(raw), "vertex_count": len(vertices),
                            "polygon_count": len(triangles), "concept_id": header["conceptId"], "representation_id": header["representationId"]}})

    # Compare source ancestor/part members against the actual active parent manifests.
    parent = json.loads(data["baseRaw"])
    overlay = json.loads(data["overlayRaw"])
    t79_extension = json.loads(data["t79ExtensionRaw"])
    base_assets = [asset for chunk in parent["chunks"] for asset in chunk["assets"]]
    t79_assets = [asset for chunk in t79_extension["chunks"] for asset in chunk["assets"]]
    parent_ids = [asset["id"] for asset in base_assets + t79_assets]
    if len(parent_ids) != len(set(parent_ids)):
        raise BuildError("T77/T79 parent scene already has duplicate stable source member IDs")
    if set(EXPECTED) & set(parent_ids):
        raise BuildError("one or more T101 source FJs already exist in T77/T79; duplicate render node would result")
    if overlay.get("sourceManifestSha256") != sha(data["baseRaw"]):
        raise BuildError("T95 overlay no longer binds to the exact T77 parent")

    by_concept = {row[0]: row for row in tables["isaConcepts"]}
    parent_rows: dict[str, list[str]] = {}
    group_targets: dict[str, list[str]] = {}
    for item in data["frozen"]["assets"]:
        generic_fma = item["officialParentRelationRow"][0]
        group_targets.setdefault(generic_fma, []).append(item["sourceElementFileId"])
    for fma in group_targets:
        parent_rows[fma] = sorted({row[2] for row in tables["isaCompoundElements"] if row[0] == fma})
    family_groups = []
    for fma, target_fjs in sorted(group_targets.items()):
        relation_name = by_concept.get(fma, [fma, None, "unknown"])[2]
        member_fjs = parent_rows[fma]
        parent_matches = sorted(set(member_fjs) & set(parent_ids))
        family_groups.append({"genericPartFma": fma, "genericPartEnglishName": relation_name,
                              "officialMemberFjs": member_fjs, "t101SelectedFjs": sorted(target_fjs),
                              "sameOrSiblingPartFjsAlreadyInT77T79": parent_matches})
    exact_aggregate_names = sorted({"flexor hallucis brevis", "gastrocnemius", "biceps femoris", "adductor hallucis"})
    aggregate_concepts = [row for row in tables["isaConcepts"] if row[2].casefold() in exact_aggregate_names]
    aggregate_rows = [{"fma": row[0], "englishName": row[2], "fjs": sorted({element[2] for element in tables["isaCompoundElements"] if element[0] == row[0]})}
                      for row in aggregate_concepts]
    aggregate_ids = sorted({fid for row in aggregate_rows for fid in row["fjs"]})
    aggregate_parent_matches = sorted(set(aggregate_ids) & set(parent_ids))
    if set(EXPECTED) & set(parent_ids):
        raise BuildError("T101 subset would create duplicate mesh IDs in the active parent scene")

    converter.MODEL_ID = "HA-MODEL-BP3D4-T101-LOWER-LIMB-SOURCE"
    glb, mesh_records = converter.build_glb(mesh_inputs)
    gltf, binary = unpack_glb(glb)
    if len(gltf.get("scenes", [])) != 1 or len(gltf.get("nodes", [])) != len(EXPECTED) or len(gltf.get("meshes", [])) != len(EXPECTED):
        raise BuildError("R4 converter output does not contain one static GLB node per exact T101 FJ")
    if gltf.get("animations") or gltf.get("skins") or gltf.get("images"):
        raise BuildError("T101 static surface chunk unexpectedly contains animation/skin/image data")
    for index, extra in enumerate(identity_extras):
        for target in (gltf["nodes"], gltf["meshes"]):
            target[index].setdefault("extras", {}).update(extra)
    gltf["asset"]["generator"] = "HUMAN ATLAS T101; existing BodyParts3D R4 OBJ-to-GLB converter; static source surfaces"
    glb = repack_glb(gltf, binary)
    glb_path = DERIVED / f"{CHUNK_ID}.glb"
    if glb_path.exists() and glb_path.read_bytes() != glb:
        old_cache_manifest = DERIVED / "manifest.json"
        if not old_cache_manifest.is_file():
            raise BuildError("refusing to overwrite an unowned ignored GLB at the T101 cache path")
        old = json.loads(old_cache_manifest.read_text())
        if old.get("task") != "T101" or old.get("frozenSourceSetSha256") != sha(data["freezeRaw"]):
            raise BuildError("refusing to overwrite a differently owned T101 ignored GLB")

    records_by_id = {row["sourceFileId"]: row for row in mesh_records}
    owner_and_regions = {
        "FJ1393": ("foot", ["foot"]), "FJ1393M": ("foot", ["foot"]),
        "FJ1394M": ("leg", ["leg"]), "FJ1395": ("thigh", ["thigh"]), "FJ1395M": ("thigh", ["thigh"]),
        "FJ1396": ("foot", ["foot"]), "FJ1396M": ("foot", ["foot"]), "FJ1397M": ("leg", ["leg"]),
        "FJ1398": ("foot", ["foot"]), "FJ1398M": ("foot", ["foot"]),
    }
    runtime_assets = []
    for fid, source in zip(EXPECTED, source_assets):
        record = records_by_id[fid]
        primary_owner, regions = owner_and_regions[fid]
        bounds = [record["atlasBoundsM"]["min"], record["atlasBoundsM"]["max"]]
        local_display = {"beforeDefaultVisible": False, "afterDefaultVisible": True, "state": "allowed",
                         "sourceSha256": source["sourceSha256"], "integrityHolds": [],
                         "evidenceIds": ["work/evidence/T101/source-acquisition.json", "atlas-data/manifests/bodyparts3d-r4-t101/source-manifest.json", "work/evidence/T101/validation.json"],
                         "retainedHoldReasons": HOLDS, "bindingState": "source_only_unbound", "publicRedistribution": "held",
                         "humanReviewed": False, "basis": "verified_local_source_context_only"}
        runtime_assets.append({"id": fid, "nodeId": f"HA-MESH-BP3D4-{fid}", "sourceSha256": source["sourceSha256"],
                               "regions": regions, "primaryOwner": primary_owner, "side": source["sourceSide"], "layer": "muscle",
                               "defaultVisible": True, "supplement": False, "pickState": "source_only_unbound", "stableIds": [],
                               "holdReasons": HOLDS, "humanReviewed": False, "bounds": bounds, "localDisplay": local_display,
                               "publicRedistribution": "held", "sourcePackage": "T101",
                               "sourceConceptIdObservation": source["sourceConceptId"],
                               "sourceRepresentationIdObservation": source["sourceRepresentationId"],
                               "sourceNameObservation": source["sourceConceptEnglishName"],
                               "sourceGeometrySha256": record["geometrySha256"], "sourceTopologySha256": record["topologySha256"]})

    chunk = {"id": CHUNK_ID, "url": f"/__atlas/body/{CHUNK_ID}.glb", "sha256": sha(glb), "bytes": len(glb), "assets": runtime_assets}
    source_contract = {"projectFrame": FRAME, "projectUnit": "m", "sourceId": SOURCE_ID, "pose": POSE,
                       "transform": "[x,y,z] source mm -> [x,z,-y] HUMAN ATLAS m; preserve x sign; no mirror/recenter",
                       "oneAnatomySceneRoot": True, "oneRenderer": True, "cameraOwner": "existing AnatomySceneController",
                       "extensionMode": "append the T101 source-only chunk to the existing T77+T95+T79 scene revision"}
    source_manifest = {"revision": "BodyParts3D-R4-T101-SOURCE-MANIFEST-v1", "task": "T101",
                       "frozenSourceSetSha256": sha(data["freezeRaw"]), "frozenMembershipSha256": data["frozen"]["membershipSha256"],
                       "source": {"sourceId": SOURCE_ID, "version": "BodyParts3D Release 4.0", "tree": "IS-A",
                                  "archiveUrl": data["acquisition"]["archiveUrl"], "archiveEtag": data["acquisition"]["archiveMetadata"]["etag"],
                                  "archiveBytes": data["acquisition"]["archiveMetadata"]["contentLength"], "fullArchiveDownloaded": False},
                       "sceneContract": source_contract,
                       "inputs": {"frozenSourceSetSha256": sha(data["freezeRaw"]), "sourceAcquisitionSha256": sha(data["acquisitionRaw"]),
                                  **data["inputHashes"], **data["metadataHashes"]},
                       "rights": {"localDisplay": "allowed only for this exact technical subset after item-level identity/transform/scene/browser validation",
                                  "publicRedistribution": "held; each raw header retains legacy CC BY-SA 2.1 Japan wording and current terms are not reconciled here",
                                  "humanAnatomyReview": "not_performed"},
                       "sourceOnlyPolicy": {"canonicalLearnerBinding": "none", "learnerPickable": False, "humanReviewed": False,
                                            "threeNameOverlay": "deferred to the later target batch; no canonical ID/name created"},
                       "wholeMusclePartRepresentation": {"sourceGroupsByExactGenericPartFma": family_groups,
                           "exactWholeMuscleNameConceptCandidates": aggregate_rows, "exactWholeMuscleCandidateFjs": aggregate_ids,
                           "exactWholeMuscleCandidateFjsInParentScene": aggregate_parent_matches,
                           "sameFjSemanticRowsPolicy": "the FJ is the mesh identity; generic and side-specific IS-A semantic rows that reference one FJ map to one scene node, never one mesh per row",
                           "productRepresentationPolicy": "no exact whole-muscle aggregate FJ for the queried four exact muscle names was found in the official IS-A concept table; target-side parts are each emitted once. Existing T77 FJ1394/FJ1397 are right-side gastrocnemius heads; the T101 FJ1394M/FJ1397M are left-side counterparts, not whole-muscle parents. No source bytes are modified.",
                           "familyGeometryComparison": "per-source OBJ bounds/vertex ranges and exact source side were checked; right-side calf counterparts have negative X and added left-side members positive X under T50/T69, so no cross-midline overlap was observed. No whole-muscle aggregate surface was found in the T77/T79 active parent set for the exact-name candidates."},
                       "sourceAssets": source_assets,
                       "meshRecords": mesh_records,
                       "derivedChunk": {"id": CHUNK_ID, "path": f"atlas-data/source-cache/bodyparts3d-r4/converted/t101/{CHUNK_ID}.glb",
                                        "sha256": sha(glb), "bytes": len(glb), "nodeCount": len(EXPECTED)}}
    source_raw = json_bytes(source_manifest)
    extension = {"revision": "BodyParts3D-R4-T101-SAME-SCENE-EXTENSION-v1", "task": "T101",
                 "frozenSourceSetSha256": sha(data["freezeRaw"]),
                 "parentSourceManifestPath": "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json",
                 "parentSourceManifestSha256": sha(data["baseRaw"]),
                 "parentProductContextOverlayPath": "atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json",
                 "parentProductContextOverlaySha256": sha(data["overlayRaw"]),
                 "parentT79SourceManifestPath": T79_SOURCE.relative_to(ROOT).as_posix(), "parentT79SourceManifestSha256": sha(data["t79SourceRaw"]),
                 "parentT79IntegrationExtensionPath": T79_EXTENSION.relative_to(ROOT).as_posix(), "parentT79IntegrationExtensionSha256": sha(data["t79ExtensionRaw"]),
                 "sourceManifestPath": SOURCE_MANIFEST.relative_to(ROOT).as_posix(), "sourceManifestSha256": sha(source_raw),
                 "sceneContract": source_contract, "sourceOnly": True, "localOnly": True, "publicRedistribution": "held", "humanReview": "not_performed",
                 "learnerBinding": "none; no canonical/ancestor-only binding created", "displayPolicy": "exact T101 subset local technical display only; source-only and review/rights holds retained",
                 "chunks": [chunk],
                 "counts": {"sourceMembers": len(EXPECTED), "uniqueNodes": len({a["nodeId"] for a in runtime_assets}),
                            "foot": sum(a["primaryOwner"] == "foot" for a in runtime_assets), "leg": sum(a["primaryOwner"] == "leg" for a in runtime_assets),
                            "thigh": sum(a["primaryOwner"] == "thigh" for a in runtime_assets),
                            "right": sum(a["side"] == "right" for a in runtime_assets), "left": sum(a["side"] == "left" for a in runtime_assets),
                            "learnerBindings": 0, "humanReviewed": 0, "publicRedistributionReleased": 0},
                 "inputs": {"frozenSourceSetSha256": sha(data["freezeRaw"]), "sourceAcquisitionSha256": sha(data["acquisitionRaw"]),
                            "parentT77ManifestSha256": sha(data["baseRaw"]), "parentT95OverlaySha256": sha(data["overlayRaw"]),
                            "parentT79SourceManifestSha256": sha(data["t79SourceRaw"]), "parentT79IntegrationExtensionSha256": sha(data["t79ExtensionRaw"]),
                            "sourceManifestSha256": sha(source_raw)}}
    extension_raw = json_bytes(extension)
    cache_manifest = json_bytes({"revision": extension["revision"], "task": "T101", "frozenSourceSetSha256": sha(data["freezeRaw"]), "chunks": [chunk]})
    return {"data": data, "sourceAssets": source_assets, "runtimeAssets": runtime_assets, "meshRecords": mesh_records,
            "glb": glb, "glbPath": DERIVED / f"{CHUNK_ID}.glb", "sourceManifest": source_manifest, "sourceRaw": source_raw,
            "extension": extension, "extensionRaw": extension_raw, "cacheManifestRaw": cache_manifest, "parent": parent,
            "parentIds": parent_ids, "familyGroups": family_groups, "aggregateRows": aggregate_rows, "aggregateParentMatches": aggregate_parent_matches}


def check_result(result: dict[str, Any], write_evidence: bool) -> dict[str, Any]:
    gltf, binary = unpack_glb(result["glb"])
    if gltf.get("scene") != 0 or len(gltf.get("scenes", [])) != 1 or len(gltf.get("nodes", [])) != len(EXPECTED) or len(gltf.get("meshes", [])) != len(EXPECTED):
        raise BuildError("T101 GLB must contain one static scene node/mesh for each of the exact ten FJs")
    by_id = {row["sourceElementFileId"]: row for row in result["sourceAssets"]}
    seen = set()
    glb_bounds: dict[str, Any] = {}
    for i, fid in enumerate(EXPECTED):
        node, mesh, source, asset = gltf["nodes"][i], gltf["meshes"][i], by_id[fid], result["runtimeAssets"][i]
        if node.get("name") != f"HA-MESH-BP3D4-{fid}" or node.get("extras", {}).get("sourceElementFileId") != fid or node.get("extras", {}).get("sourceSha256") != source["sourceSha256"]:
            raise BuildError(f"T101 GLB node ID/hash invalid: {fid}")
        if any(key in node for key in ("children", "matrix", "translation", "rotation", "scale", "skin")):
            raise BuildError(f"T101 GLB node applies a transform/pivot/skin outside the shared frame: {fid}")
        if node["name"] in seen:
            raise BuildError(f"T101 GLB repeats a mesh node: {fid}")
        seen.add(node["name"])
        if mesh.get("name") != node["name"] or len(mesh.get("primitives", [])) != 1:
            raise BuildError(f"T101 GLB mesh does not map one-to-one to node: {fid}")
        primitive = mesh["primitives"][0]
        if set(primitive.get("attributes", {})) != {"POSITION", "NORMAL"}:
            raise BuildError(f"T101 GLB primitive layout invalid: {fid}")
        accessor = gltf["accessors"][primitive["attributes"]["POSITION"]]
        bounds = [accessor["min"], accessor["max"]]
        if any(abs(bounds[s][axis] - asset["bounds"][s][axis]) > 1e-6 for s in range(2) for axis in range(3)):
            raise BuildError(f"T101 GLB project-space vertex bounds differ from runtime manifest: {fid}")
        source_path = ROOT / next(row["cacheRelativePath"] for row in result["data"]["acquired"] if row["sourceElementFileId"] == fid)
        vertices, _, _ = result["data"]["converter"].parse_obj(source_path)
        transformed = [result["data"]["converter"].transform_vertex(v) for v in vertices]
        expected_bounds = [[min(v[axis] for v in transformed) for axis in range(3)], [max(v[axis] for v in transformed) for axis in range(3)]]
        if any(abs(expected_bounds[s][axis] - bounds[s][axis]) > 1e-6 for s in range(2) for axis in range(3)):
            raise BuildError(f"T50/T69 R4 axis+millimetre transform is not represented in GLB for {fid}")
        glb_bounds[fid] = bounds
    if seen != {f"HA-MESH-BP3D4-{fid}" for fid in EXPECTED}:
        raise BuildError("T101 GLB node ID set differs from exact frozen source ID set")
    if {asset["id"] for asset in result["runtimeAssets"]} != set(EXPECTED) or len({asset["id"] for asset in result["runtimeAssets"]}) != len(EXPECTED):
        raise BuildError("T101 runtime manifest has missing/extra/duplicate source IDs")
    if set(EXPECTED) & set(result["parentIds"]):
        raise BuildError("T101 source FJ collides with active T77/T79 runtime parent")
    for asset in result["runtimeAssets"]:
        if asset["pickState"] != "source_only_unbound" or asset["stableIds"] or asset["humanReviewed"] is not False or asset["publicRedistribution"] != "held" or asset["defaultVisible"] is not True or asset["localDisplay"]["state"] != "allowed":
            raise BuildError(f"T101 source-only/local-display/rights/review policy invalid: {asset['id']}")
    expected_outputs = {SOURCE_MANIFEST: result["sourceRaw"], EXTENSION: result["extensionRaw"], DERIVED / "manifest.json": result["cacheManifestRaw"], result["glbPath"]: result["glb"]}
    if not write_evidence:
        for path, raw in expected_outputs.items():
            if not path.is_file() or path.read_bytes() != raw:
                raise BuildError(f"T101 build output missing or not reproducible: {path.relative_to(ROOT)}")

    browser_evidence = json.loads(BROWSER_EVIDENCE.read_text(encoding="utf-8")) if BROWSER_EVIDENCE.is_file() else None
    browser_pass = bool(browser_evidence and browser_evidence.get("result") == "pass"
                        and browser_evidence.get("runtimeManifest", {}).get("t101Chunk", {}).get("ids") == EXPECTED
                        and browser_evidence.get("runtimeManifest", {}).get("t101Chunk", {}).get("sourceOnly") is True
                        and browser_evidence.get("runtimeManifest", {}).get("t101Chunk", {}).get("publicRedistribution") == "held"
                        and browser_evidence.get("browser", {}).get("canvasCount") == 1
                        and browser_evidence.get("browser", {}).get("consoleErrors") == 0
                        and browser_evidence.get("browser", {}).get("consoleWarnings") == 0
                        and all(browser_evidence.get("checks", {}).get(key) is True for key in ("wholeBody", "closeViews", "layerOff", "layerRestored", "sourceLabelsNotPromoted")))
    evidence = {"revision": "T101-local-technical-validation-v1", "task": "T101",
                "status": "passed_local_technical_validation" if browser_pass else "passed_local_technical_validation_pending_actual_browser",
                "browserEvidenceSha256": sha(BROWSER_EVIDENCE.read_bytes()) if browser_pass else None,
                "sourceMembers": len(EXPECTED), "ids": EXPECTED,
                "frozenSourceSetSha256": sha(result["data"]["freezeRaw"]), "frozenMembershipSha256": result["data"]["frozen"]["membershipSha256"],
                "sourceAcquisitionSha256": sha(result["data"]["acquisitionRaw"]),
                "fullArchiveDownloaded": False, "selectedMemberRangeBytes": result["data"]["acquisition"]["totalRangeResponseBytes"],
                "selectedObjPayloadBytes": result["data"]["acquisition"]["selectedPayloadBytes"],
                "allRangeResponsesHttp206": result["data"]["acquisition"]["allRangeResponsesHttp206"],
                "sourceSha256": {row["sourceElementFileId"]: row["sourceSha256"] for row in result["sourceAssets"]},
                "sourceCrc32": {row["sourceElementFileId"]: row["sourceCrc32"] for row in result["sourceAssets"]},
                "sourceHeaderBoundsVsVertexExtremaMaxDeltaMm": {row["sourceElementFileId"]: row["geometry"]["headerActualBoundsMaxDeltaMm"] for row in result["sourceAssets"]},
                "sourceVertexCounts": {row["sourceElementFileId"]: row["geometry"]["sourceVertexCount"] for row in result["sourceAssets"]},
                "sourceTriangleCounts": {row["sourceElementFileId"]: row["geometry"]["sourceTriangleCount"] for row in result["sourceAssets"]},
                "sourceSidesFromExactOfficialNames": {row["sourceElementFileId"]: row["sourceSide"] for row in result["sourceAssets"]},
                "projectBoundsM": glb_bounds, "derivedGlbSha256": sha(result["glb"]), "derivedGlbBytes": len(result["glb"]),
                "parentScene": {"t77ManifestSha256": sha(result["data"]["baseRaw"]), "t95OverlaySha256": sha(result["data"]["overlayRaw"]),
                                "t79SourceManifestSha256": sha(result["data"]["t79SourceRaw"]), "t79ExtensionSha256": sha(result["data"]["t79ExtensionRaw"]),
                                "frame": FRAME, "unit": "m", "pose": POSE, "root": "AnatomySceneRoot", "oneRenderer": True},
                "wholeMusclePartReview": result["sourceManifest"]["wholeMusclePartRepresentation"],
                "sourceOnlyAndRights": {"canonicalBindings": 0, "stableIds": 0, "humanAnatomyReview": "not_performed", "publicRedistribution": "held",
                                         "localDisplay": "allowed after exact item and same-scene technical validation"},
                "browserValidation": {"status": "pass" if browser_pass else "pending", "evidence": "work/evidence/T101/browser-validation.json"},
                "validationAssertions": ["exact frozen FJ/FMA/BP/name/ELEMENT/parent rows", "OBJ header/hash/archive CRC/side/part/mm unit/frame/bounds per item",
                                         "T50/T69 axis transform and metre scale; x-side consistency only as a sanity check; no mirror/recenter",
                                         "one GLB source node per exact FJ; generic+side-specific rows do not duplicate a node",
                                         "source family/parent runtime overlap inventory and exact whole-muscle aggregate candidate comparison",
                                         "append-only T77+T95+T79+T101 shared scene/root/renderer; local display distinct from public rights"]}
    if write_evidence:
        EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        EVIDENCE.write_bytes(json_bytes(evidence))
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = convert()
        if args.build:
            frozen_hash = sha(result["data"]["freezeRaw"])
            DERIVED.mkdir(parents=True, exist_ok=True)
            (result["glbPath"]).write_bytes(result["glb"])
            write_owned(SOURCE_MANIFEST, result["sourceRaw"], "T101", frozen_hash)
            write_owned(EXTENSION, result["extensionRaw"], "T101", frozen_hash)
            write_owned(DERIVED / "manifest.json", result["cacheManifestRaw"], "T101", frozen_hash)
            evidence = check_result(result, write_evidence=True)
        else:
            evidence = check_result(result, write_evidence=False)
        print(json.dumps({"status": evidence["status"], "members": evidence["sourceMembers"],
                          "glbSha256": evidence["derivedGlbSha256"], "evidence": "work/evidence/T101/validation.json"}, indent=2))
        return 0
    except Exception as exc:
        print(f"T101 build/check failed closed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
