#!/usr/bin/env python3
"""Build and verify T79's exact ten-member BodyParts3D R4 scene extension.

The source OBJ bytes remain in the ignored source cache. This tool reuses the
repository's validated R4 parser/OBJ-to-GLB converter and writes only T79-owned
derived artifacts and manifests.
"""
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
FREEZE = ROOT / "work/evidence/T79/frozen-source-set.json"
ACQUISITION = ROOT / "work/evidence/T79/source-acquisition-attempt-04.json"
T77_MANIFEST = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json"
T95_OVERLAY = ROOT / "atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json"
T50_CONTRACT = ROOT / "work/evidence/T50/scene-contract.md"
T69_DIAGNOSTIC = ROOT / "work/evidence/T69/diagnostic.json"
T69_ASSESSMENT = ROOT / "work/evidence/T69/assessment.json"
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
SOURCE_CACHE = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t79"
DERIVED = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t79"
OUT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t79"
SOURCE_MANIFEST = OUT / "source-manifest.json"
EXTENSION = OUT / "integration-extension.json"
EVIDENCE = ROOT / "work/evidence/T79/validation.json"
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
CHUNK_ID = "t79-upper-limb-muscle"
MODEL_ID = "HA-MODEL-BP3D4-T79-BILATERAL-BICEPS-TRICEPS-SOURCE"
EXPECTED = ["FJ1512", "FJ1512M", "FJ1478", "FJ1478M", "FJ1479", "FJ1479M", "FJ1480", "FJ1480M", "FJ1477", "FJ1477M"]
CONTEXT_HOLDS = ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"]
BOUNDS_HEADER = re.compile(r"^#\s*Bounds\(mm\):\s*\(([^)]+)\)-\(([^)]+)\)\s*$")


class BuildError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise BuildError(f"cannot load required project tool: {path}")
    instance = importlib.util.module_from_spec(spec)
    sys.modules[name] = instance
    spec.loader.exec_module(instance)
    return instance


def unpack_glb(raw: bytes) -> tuple[dict[str, Any], bytes]:
    if len(raw) < 28 or raw[:4] != b"glTF" or struct.unpack_from("<I", raw, 4)[0] != 2:
        raise BuildError("derived file is not a GLB 2.0 container")
    json_length, json_type = struct.unpack_from("<II", raw, 12)
    if json_type != 0x4E4F534A:
        raise BuildError("GLB JSON chunk is missing")
    doc = json.loads(raw[20:20 + json_length].decode("utf-8"))
    binary_offset = 20 + json_length
    binary_length, binary_type = struct.unpack_from("<II", raw, binary_offset)
    if binary_type != 0x004E4942:
        raise BuildError("GLB BIN chunk is missing")
    binary = raw[binary_offset + 8:binary_offset + 8 + binary_length]
    if len(binary) != binary_length:
        raise BuildError("GLB BIN chunk is truncated")
    return doc, binary


def repack_glb(doc: dict[str, Any], binary: bytes) -> bytes:
    encoded = json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    encoded += b" " * (-len(encoded) % 4)
    binary += b"\0" * (-len(binary) % 4)
    total = 12 + 8 + len(encoded) + 8 + len(binary)
    return b"".join((
        struct.pack("<4sII", b"glTF", 2, total),
        struct.pack("<II", len(encoded), 0x4E4F534A), encoded,
        struct.pack("<II", len(binary), 0x004E4942), binary,
    ))


def parse_header_bounds(raw_path: Path) -> tuple[str, list[float], str]:
    name = None
    bounds = None
    license_header = None
    with raw_path.open("r", encoding="utf-8", errors="strict") as source:
        for line in source:
            if not line.startswith("#"):
                break
            if line.startswith("# English name :"):
                name = line.split(":", 1)[1].strip()
            found = BOUNDS_HEADER.match(line.rstrip("\r\n"))
            if found:
                bounds = [float(x.strip()) for x in found.group(1).split(",") + found.group(2).split(",")]
            if "license for this database" in line.lower():
                license_header = line.lstrip("# ").strip()
    if not name or not bounds or len(bounds) != 6 or not license_header:
        raise BuildError(f"required verbatim identity/bounds/license header missing: {raw_path.name}")
    if not all(math.isfinite(v) for v in bounds):
        raise BuildError(f"non-finite bounds header: {raw_path.name}")
    return name, bounds, license_header


def write_owned(path: Path, value: bytes, owner: str, frozen_hash: str) -> None:
    if path.exists() and path.read_bytes() != value:
        try:
            old = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            old = {}
        old_owner = old.get("task") or (old.get("revision", "").split("-")[0] if isinstance(old.get("revision"), str) else None)
        old_frozen = old.get("frozenSourceSetSha256")
        if old_frozen is None and isinstance(old.get("inputs"), dict):
            old_frozen = old["inputs"].get("frozenSourceSetSha256")
        if old_owner != owner or old_frozen != frozen_hash:
            raise BuildError(f"refusing to overwrite unowned or differently frozen artifact: {path.relative_to(ROOT)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)


def exact_inputs() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, str]]:
    if not FREEZE.is_file() or not ACQUISITION.is_file():
        raise BuildError("T79 freeze and successful exact-member acquisition are required")
    freeze_raw = FREEZE.read_bytes()
    frozen = json.loads(freeze_raw)
    acquisition = json.loads(ACQUISITION.read_text(encoding="utf-8"))
    if frozen.get("status") != "frozen_before_mesh_acquisition" or frozen.get("sourceElementFileIds") != EXPECTED:
        raise BuildError("T79 source freeze is not the exact ten-member set")
    if [row.get("sourceElementFileId") for row in frozen.get("uniqueNewSourceAssets", [])] != EXPECTED:
        raise BuildError("T79 freeze asset rows differ from exact allowlist")
    if acquisition.get("result") != "pass" or acquisition.get("fullArchiveDownloaded") is not False or acquisition.get("selectedMemberRangeRequestsOnly") is not True:
        raise BuildError("T79 acquisition did not pass bounded selected-member-only retrieval")
    if acquisition.get("frozenSourceSetSha256") != sha(freeze_raw) or acquisition.get("attemptedIds") != EXPECTED:
        raise BuildError("T79 acquisition does not bind to the exact frozen set")
    files = acquisition.get("files", [])
    if [row.get("sourceElementFileId") for row in files] != EXPECTED or any(row.get("status") != "acquired" for row in files):
        raise BuildError("T79 acquisition is not a successful one-to-one ten-member result")
    locked = dict(frozen.get("inputSha256", {}))
    for path in [T77_MANIFEST, T95_OVERLAY, T50_CONTRACT, T69_DIAGNOSTIC, T69_ASSESSMENT]:
        rel = path.relative_to(ROOT).as_posix()
        if not path.is_file():
            raise BuildError(f"required T79 scene/frame input missing: {rel}")
        locked[rel] = sha_file(path)
    for rel, expected in locked.items():
        path = ROOT / rel
        if not path.is_file() or sha_file(path) != expected:
            raise BuildError(f"locked T79 source/scene input changed: {rel}")
    return frozen, acquisition, files, locked


def convert() -> dict[str, Any]:
    frozen, acquisition, acquired, locked = exact_inputs()
    ingest = module("ha_t79_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
    converter = module("ha_t79_converter", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")
    tables = ingest.load_tables(METADATA)
    source_names = ingest.load_source_name_map(ROOT)
    concept_rows = {tuple(row) for row in tables["isaConcepts"]}
    element_rows = {tuple(row) for row in tables["isaCompoundElements"]}
    inclusion_rows = {tuple(row) for row in tables["isaInclusion"]}
    frozen_by_id = {row["sourceElementFileId"]: row for row in frozen["uniqueNewSourceAssets"]}
    acquired_by_id = {row["sourceElementFileId"]: row for row in acquired}
    inputs = []
    source_assets = []
    identity_extras = []

    for file_id in EXPECTED:
        freeze_row = frozen_by_id[file_id]
        acquisition_row = acquired_by_id[file_id]
        raw_path = ROOT / acquisition_row["cacheRelativePath"]
        if not raw_path.is_file():
            raise BuildError(f"selected source OBJ missing from ignored cache: {file_id}")
        raw = raw_path.read_bytes()
        if len(raw) != acquisition_row.get("bytes") or sha(raw) != acquisition_row.get("sha256"):
            raise BuildError(f"selected source bytes/hash mismatch: {file_id}")
        try:
            raw_crc = f"{zlib.crc32(raw) & 0xffffffff:08x}"
        except Exception as exc:
            raise BuildError(f"could not compute source OBJ CRC32 for {file_id}") from exc
        if raw_crc != str(acquisition_row.get("crc32", "")).lower():
            raise BuildError(f"selected source CRC32 differs from archive record: {file_id}")
        header = ingest.read_obj_header(raw_path)
        ingest.validate_obj_source_identity(header, tables)
        header_name, header_bounds, license_header = parse_header_bounds(raw_path)
        official_name = source_names.get(header.get("conceptId"))
        exact_identity = (header.get("conceptId"), header.get("representationId"), official_name)
        if exact_identity not in concept_rows:
            raise BuildError(f"OBJ FMA/BP/name identity absent from official R4 IS-A concept row: {file_id}")
        if tuple(freeze_row["officialConceptRow"]) != exact_identity:
            raise BuildError(f"frozen concept row differs from OBJ header identity: {file_id}")
        if tuple(freeze_row["officialElementRow"]) not in element_rows:
            raise BuildError(f"frozen FJ/FMA element mapping absent from official R4 table: {file_id}")
        if tuple(freeze_row["officialParentRelationRow"]) not in inclusion_rows:
            raise BuildError(f"frozen exact parent relation absent from official R4 IS-A table: {file_id}")
        if (header.get("fileId"), header.get("conceptId"), header.get("representationId"), header.get("buildUpLogic")) != (file_id, freeze_row["sourceConceptId"], freeze_row["sourceRepresentationId"], "FMA 3.0 is_a"):
            raise BuildError(f"OBJ header ID/tree/FMA/BP differs from frozen official relation: {file_id}")
        if not official_name or header_name.casefold() != official_name.casefold() or acquisition_row["header"]["English name"] != header_name:
            raise BuildError(f"OBJ English name header differs from exact source concept (case-only comparison not accepted here): {file_id}")
        if header_bounds != [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", acquisition_row["header"]["Bounds(mm)"])]:
            raise BuildError(f"OBJ Bounds(mm) header differs from acquisition record: {file_id}")
        source_side = freeze_row.get("sourceSide")
        if source_side not in {"left", "right"} or source_side != acquisition_row.get("sourceSide"):
            raise BuildError(f"exact named side is missing or conflicts across frozen relation/acquisition: {file_id}")
        if freeze_row.get("sourceSideEvidence") != acquisition_row.get("sourceSideEvidence"):
            raise BuildError(f"source side evidence drifted: {file_id}")
        vertices, normals, triangles = converter.parse_obj(raw_path)
        source_bounds = [min(v[i] for v in vertices) for i in range(3)] + [max(v[i] for v in vertices) for i in range(3)]
        max_header_delta = max(abs(header_bounds[i] - source_bounds[i]) for i in range(6))
        signed_header_delta = [header_bounds[i] - source_bounds[i] for i in range(6)]
        # The right/left interpretation comes from the exact official name; x is only a frame-consistency check.
        sign_consistent = max(v[0] for v in vertices) < 0 if source_side == "right" else min(v[0] for v in vertices) > 0
        if not sign_consistent:
            raise BuildError(f"source x-sign conflicts with the independently named side under T50/T69 frame check: {file_id}")
        frame = "[x,y,z] source mm -> [x,z,-y] HUMAN ATLAS m; preserve x sign; no mirror/recenter"
        transform = [converter.transform_vertex(v) for v in vertices]
        atlas_bounds = {"min": [min(v[i] for v in transform) for i in range(3)], "max": [max(v[i] for v in transform) for i in range(3)]}
        geometry = {
            "sourceVertexCount": len(vertices), "sourceNormalCount": len(normals), "sourceTriangleCount": len(triangles),
            "sourceBoundsActualMm": source_bounds, "sourceHeaderBoundsMm": header_bounds,
            "sourceHeaderVsVertexBoundsDeltaMm": signed_header_delta,
            "sourceHeaderVsVertexBoundsMaxDeltaMm": max_header_delta,
            "sourceHeaderVsVertexBoundsWithin001mm": max_header_delta <= 0.01,
            "projectBoundsM": atlas_bounds,
            "coordinateSideSanityCheckOnly": {"expectedByExactName": source_side, "sourceXAxisSignConsistent": sign_consistent},
        }
        inputs.append({
            "file_id": file_id,
            "source_path": raw_path,
            "source_relative_path": acquisition_row["cacheRelativePath"],
            "source_sha256": acquisition_row["sha256"],
            "asset": {"bytes": len(raw), "vertex_count": len(vertices), "polygon_count": len(triangles),
                      "concept_id": header["conceptId"], "representation_id": header["representationId"]},
        })
        identity_extras.append({
            "sourceElementFileId": file_id,
            "sourceConceptId": header["conceptId"], "sourceRepresentationId": header["representationId"],
            "sourceConceptEnglishName": official_name,
            "sourceSide": source_side,
            "sourceSideEvidence": freeze_row["sourceSideEvidence"],
            "projectFrame": FRAME, "projectUnit": "m", "sourceUnit": "mm_from_exact_OBJ_Bounds_header",
            "sourcePose": POSE, "transform": frame,
            "publicRedistribution": "held", "humanAnatomyReviewed": False,
        })
        source_assets.append({
            **identity_extras[-1],
            "sourceArchiveTree": "IS-A", "sourceArchiveMemberPath": acquisition_row["memberPath"],
            "sourceArchiveCrc32": raw_crc, "sourceBytes": len(raw), "sourceSha256": acquisition_row["sha256"],
            "sourceHeader": {
                "fileId": header["fileId"], "representationId": header["representationId"],
                "buildUpLogic": header["buildUpLogic"], "conceptId": header["conceptId"],
                "englishNameExact": header_name, "boundsHeaderUnit": "mm", "boundsHeaderMm": header_bounds,
                "legacyLicenseHeaderExact": license_header,
            },
            "officialConceptRow": list(freeze_row["officialConceptRow"]),
            "officialElementRow": list(freeze_row["officialElementRow"]),
            "officialParentRelationRow": list(freeze_row["officialParentRelationRow"]),
            "allOfficialElementRowsForSameFj": list(freeze_row["allOfficialElementRowsForSameFj"]),
            "multipleSemanticRowsShareOneSourceNode": len(freeze_row["allOfficialElementRowsForSameFj"]) > 1,
            "geometry": geometry,
        })

    # No exact aggregate biceps/triceps source geometry exists in the pinned IS-A element table.
    named_parts = [row for row in tables["isaConcepts"] if "biceps brachii" in row[2].casefold() or "triceps brachii" in row[2].casefold()]
    aggregate_names = [row for row in named_parts if row[2].casefold() in {"biceps brachii", "triceps brachii"}]
    aggregate_fmas = {row[0] for row in aggregate_names}
    aggregate_fjs = sorted({row[2] for row in tables["isaCompoundElements"] if row[0] in aggregate_fmas})
    family_fmas = {row[0] for row in named_parts}
    family_element_rows = [row for row in tables["isaCompoundElements"] if row[0] in family_fmas]
    family_fjs = sorted({row[2] for row in family_element_rows})
    t77 = json.loads(T77_MANIFEST.read_text(encoding="utf-8"))
    base_assets = [asset for chunk in t77["chunks"] for asset in chunk["assets"]]
    base_by_id = {asset["id"]: asset for asset in base_assets}
    if len(base_by_id) != len(base_assets):
        raise BuildError("parent T77 runtime manifest already contains duplicate source ID nodes")
    if set(EXPECTED) & set(base_by_id):
        raise BuildError("T79 source IDs are already present in parent runtime; duplicate node would be created")
    aggregate_base_ids = sorted(set(aggregate_fjs) & set(base_by_id))
    if aggregate_base_ids:
        raise BuildError("aggregate whole-muscle FJ source exists in parent manifest; geometry-range overlap must be reviewed before display")
    family_base_ids = sorted(set(family_fjs) & set(base_by_id))
    if set(family_fjs) != set(EXPECTED) or family_base_ids:
        raise BuildError("pinned IS-A biceps/triceps family element set or parent runtime intersections changed; re-review exact surface coverage")

    converter.MODEL_ID = MODEL_ID
    glb, mesh_records = converter.build_glb(inputs)
    gltf, binary = unpack_glb(glb)
    if len(gltf.get("scenes", [])) != 1 or len(gltf.get("nodes", [])) != len(EXPECTED) or len(gltf.get("meshes", [])) != len(EXPECTED):
        raise BuildError("deterministic converter did not emit one static scene node per frozen source FJ")
    for index, extra in enumerate(identity_extras):
        for target in (gltf["nodes"], gltf["meshes"]):
            target[index].setdefault("extras", {}).update(extra)
    gltf["asset"]["generator"] = "HUMAN ATLAS T79; existing BodyParts3D R4 OBJ-to-GLB converter; static source surface"
    glb = repack_glb(gltf, binary)
    gltf, _ = unpack_glb(glb)
    glb_path = DERIVED / f"{CHUNK_ID}.glb"
    if glb_path.exists() and glb_path.read_bytes() != glb:
        previous_manifest = DERIVED / "manifest.json"
        if not previous_manifest.is_file():
            raise BuildError("refusing to overwrite an unowned ignored GLB in the T79 cache path")
        previous = json.loads(previous_manifest.read_text(encoding="utf-8"))
        if previous.get("task") != "T79" or previous.get("frozenSourceSetSha256") != sha(FREEZE.read_bytes()):
            raise BuildError("refusing to overwrite a differently owned T79 cache artifact")
    DERIVED.mkdir(parents=True, exist_ok=True)
    glb_path.write_bytes(glb)
    glb_sha = sha(glb)

    converter_records = {row["sourceFileId"]: row for row in mesh_records}
    assets = []
    for id, source_row in zip(EXPECTED, source_assets):
        record = converter_records[id]
        side = source_row["sourceSide"]
        bounds = [record["atlasBoundsM"]["min"], record["atlasBoundsM"]["max"]]
        policy = {
            "beforeDefaultVisible": False, "afterDefaultVisible": True, "state": "allowed",
            "sourceSha256": source_row["sourceSha256"], "integrityHolds": [],
            "evidenceIds": ["work/evidence/T79/source-acquisition-attempt-04.json", "atlas-data/manifests/bodyparts3d-r4-t79/source-manifest.json", "work/evidence/T79/validation.json"],
            "retainedHoldReasons": CONTEXT_HOLDS, "bindingState": "source_only_unbound",
            "publicRedistribution": "held", "humanReviewed": False,
            "basis": "verified_local_source_context_only",
        }
        assets.append({
            "id": id, "nodeId": f"HA-MESH-BP3D4-{id}", "sourceSha256": source_row["sourceSha256"],
            "regions": ["upper-limb"], "side": side, "layer": "muscle", "defaultVisible": True,
            "supplement": False, "pickState": "source_only_unbound", "stableIds": [],
            "holdReasons": CONTEXT_HOLDS, "humanReviewed": False, "bounds": bounds,
            "localDisplay": policy, "publicRedistribution": "held", "sourcePackage": "T79",
            "sourceConceptIdObservation": source_row["sourceConceptId"],
            "sourceRepresentationIdObservation": source_row["sourceRepresentationId"],
            "sourceNameObservation": source_row["sourceConceptEnglishName"],
            "sourceGeometrySha256": record["geometrySha256"], "sourceTopologySha256": record["topologySha256"],
        })

    chunk = {"id": CHUNK_ID, "url": f"/__atlas/body/{CHUNK_ID}.glb", "sha256": glb_sha, "bytes": len(glb), "assets": assets}
    base_manifest_raw = T77_MANIFEST.read_bytes()
    overlay_raw = T95_OVERLAY.read_bytes()
    overlay = json.loads(overlay_raw)
    if overlay.get("sourceManifestSha256") != sha(base_manifest_raw):
        raise BuildError("current T95 overlay does not bind to the current parent T77 source manifest")
    scene_contract = {
        "projectFrame": FRAME, "projectUnit": "m", "sourceId": SOURCE_ID, "pose": POSE,
        "transform": "[x,y,z] source mm -> [x,z,-y] HUMAN ATLAS m; no mirror or recenter",
        "oneAnatomySceneRoot": True, "oneRenderer": True, "cameraOwner": "existing AnatomySceneController",
        "extensionMode": "append source-only nodes to T77 + T95 runtime manifest; do not replace renderer/root/camera",
    }
    source_manifest = {
        "revision": "BodyParts3D-R4-T79-SOURCE-MANIFEST-v1", "task": "T79",
        "frozenSourceSetSha256": sha(FREEZE.read_bytes()), "frozenMembershipSha256": frozen["membershipSha256"],
        "source": {"sourceId": SOURCE_ID, "version": "BodyParts3D Release 4.0", "tree": "IS-A", "archiveUrl": acquisition["archiveUrl"], "fullArchiveDownloaded": False},
        "sceneContract": scene_contract, "inputs": {"frozenSourceSetSha256": sha(FREEZE.read_bytes()), **locked},
        "rights": {"localDisplay": "allowed after item-level technical conversion/scene validation", "publicRedistribution": "held per item: legacy R4 OBJ CC BY-SA 2.1 Japan header retained; no release approval", "humanAnatomyReview": "not_performed"},
        "sourceOnlyPolicy": {"canonicalLearnerBinding": "none", "learnerPickable": False, "humanReviewed": False, "threeNameOverlay": "deferred to a later target batch"},
        "wholeMusclePartRepresentation": {
            "officialNamedConcepts": [{"fma": row[0], "englishName": row[2]} for row in named_parts],
            "officialFamilyElementRows": [list(row) for row in family_element_rows],
            "allFamilyFjsInPinnedR4": family_fjs,
            "familyFjsInParentManifest": family_base_ids,
            "exactAggregateNamesInPinnedR4": [row[2] for row in aggregate_names],
            "exactAggregateFjsInPinnedR4": aggregate_fjs,
            "parentManifestAggregateFjMatches": aggregate_base_ids,
            "productPolicy": "single source-file node per exact part FJ; generic and side-specific IS-A rows that share an FJ remain one node; no parent whole-muscle surface is present in this subset or T77, so no duplicate suppression is required; originals remain unchanged",
            "geometryScopeReview": "the exact pinned R4 IS-A biceps/triceps family element set consists of the ten head-specific FJs in this task, each with its generic and side-specific semantic rows; there is no exact whole-biceps or whole-triceps FJ, no family FJ is already in T77, and no separate aggregate parent surface is emitted. The 10 source surfaces are each emitted once.",
        },
        "sourceAssets": source_assets,
        "meshRecords": mesh_records,
        "derivedChunk": {"id": CHUNK_ID, "path": f"atlas-data/source-cache/bodyparts3d-r4/converted/t79/{CHUNK_ID}.glb", "sha256": glb_sha, "bytes": len(glb), "nodeCount": len(EXPECTED)},
    }
    source_raw = json_bytes(source_manifest)
    extension = {
        "revision": "BodyParts3D-R4-T79-SAME-SCENE-EXTENSION-v1", "task": "T79",
        "frozenSourceSetSha256": sha(FREEZE.read_bytes()),
        "parentSourceManifestPath": "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json",
        "parentSourceManifestSha256": sha(base_manifest_raw),
        "parentProductContextOverlayPath": "atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json",
        "parentProductContextOverlaySha256": sha(overlay_raw),
        "sourceManifestPath": SOURCE_MANIFEST.relative_to(ROOT).as_posix(), "sourceManifestSha256": sha(source_raw),
        "sceneContract": scene_contract,
        "sourceOnly": True, "localOnly": True, "publicRedistribution": "held", "humanReview": "not_performed",
        "learnerBinding": "none; no ancestor-only binding created", "displayPolicy": "T79 per-item local technical eligibility only; source-only holds retained",
        "chunks": [chunk],
        "counts": {"sourceMembers": len(EXPECTED), "uniqueNodes": len({a["nodeId"] for a in assets}), "right": sum(a["side"] == "right" for a in assets), "left": sum(a["side"] == "left" for a in assets), "learnerBindings": 0, "humanReviewed": 0, "publicRedistributionReleased": 0},
        "inputs": {"frozenSourceSetSha256": sha(FREEZE.read_bytes()), "sourceAcquisitionSha256": sha(ACQUISITION.read_bytes()), "parentT77ManifestSha256": sha(base_manifest_raw), "parentT95OverlaySha256": sha(overlay_raw), "sourceManifestSha256": sha(source_raw)},
    }
    cache_manifest = {"revision": extension["revision"], "task": "T79", "frozenSourceSetSha256": extension["frozenSourceSetSha256"], "chunks": [chunk]}
    result = {
        "sourceManifest": source_manifest, "sourceRaw": source_raw,
        "extension": extension, "extensionRaw": json_bytes(extension),
        "cacheManifest": cache_manifest, "cacheManifestRaw": json_bytes(cache_manifest),
        "glb": glb, "glbPath": glb_path, "assets": assets, "sourceAssets": source_assets,
        "meshRecords": mesh_records, "lockedInputs": locked, "frozen": frozen,
        "parent": json.loads(base_manifest_raw), "parentSha256": sha(base_manifest_raw), "overlaySha256": sha(overlay_raw),
    }
    return result


def check_output(result: dict[str, Any]) -> dict[str, Any]:
    expected = {
        SOURCE_MANIFEST: result["sourceRaw"], EXTENSION: result["extensionRaw"],
        DERIVED / "manifest.json": result["cacheManifestRaw"], result["glbPath"]: result["glb"],
    }
    for path, raw in expected.items():
        if not path.is_file() or path.read_bytes() != raw:
            raise BuildError(f"generated T79 artifact missing or non-reproducible: {path.relative_to(ROOT)}")
    return validate(result, write_evidence=False)


def validate(result: dict[str, Any], write_evidence: bool = True) -> dict[str, Any]:
    gltf, binary = unpack_glb(result["glb"])
    if gltf.get("scene") != 0 or len(gltf.get("scenes", [])) != 1 or len(gltf.get("nodes", [])) != len(EXPECTED):
        raise BuildError("derived T79 GLB does not have one scene and ten nodes")
    if gltf.get("animations") or gltf.get("skins") or gltf.get("images"):
        raise BuildError("unexpected animation/skin/image in static T79 GLB")
    nodes = gltf["nodes"]
    seen_nodes = set()
    gltf_bounds = {}
    for index, (node, asset, source) in enumerate(zip(nodes, result["assets"], result["sourceAssets"])):
        fid = EXPECTED[index]
        if node.get("name") != f"HA-MESH-BP3D4-{fid}" or node.get("extras", {}).get("sourceElementFileId") != fid or node.get("extras", {}).get("sourceSha256") != source["sourceSha256"]:
            raise BuildError(f"GLB node ID/hash is wrong: {fid}")
        if any(key in node for key in ("children", "matrix", "translation", "rotation", "scale", "skin")):
            raise BuildError(f"T79 node transform/pivot/skin would alter shared source frame: {fid}")
        if node["name"] in seen_nodes:
            raise BuildError(f"duplicate source node: {fid}")
        seen_nodes.add(node["name"])
        mesh = gltf["meshes"][node["mesh"]]
        if len(mesh["primitives"]) != 1 or len(mesh["primitives"][0].get("attributes", {})) != 2:
            raise BuildError(f"unexpected GLB primitive layout: {fid}")
        primitive = mesh["primitives"][0]
        accessor = gltf["accessors"][primitive["attributes"]["POSITION"]]
        gbound = [accessor["min"], accessor["max"]]
        if any(abs(gbound[side][axis] - asset["bounds"][side][axis]) > 1e-6 for side in range(2) for axis in range(3)):
            raise BuildError(f"GLB accessor bounds differ from T79 runtime manifest: {fid}")
        positions = binary[gltf["bufferViews"][accessor["bufferView"]].get("byteOffset", 0) + accessor.get("byteOffset", 0):]
        if len(positions) < accessor["count"] * 12:
            raise BuildError(f"GLB position buffer truncated: {fid}")
        gltf_bounds[fid] = gbound
        # Exact source-to-project transform is checked from the source parser output and packed GLB accessors.
        converter = module("ha_t79_verify_converter", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")
        verts, _, _ = converter.parse_obj(ROOT / next(a["cacheRelativePath"] for a in json.loads(ACQUISITION.read_text())["files"] if a["sourceElementFileId"] == fid))
        transformed = [converter.transform_vertex(v) for v in verts]
        expected_bounds = [[min(v[a] for v in transformed) for a in range(3)], [max(v[a] for v in transformed) for a in range(3)]]
        if any(abs(expected_bounds[s][a] - gbound[s][a]) > 1e-6 for s in range(2) for a in range(3)):
            raise BuildError(f"T50/T69 rotation+millimeter transform is not represented in GLB for {fid}")
    if seen_nodes != {f"HA-MESH-BP3D4-{fid}" for fid in EXPECTED}:
        raise BuildError("derived node identity set differs from the frozen T79 set")
    if len({asset["id"] for asset in result["assets"]}) != len(EXPECTED) or {asset["id"] for asset in result["assets"]} != set(EXPECTED):
        raise BuildError("T79 runtime manifest has a duplicate, missing or extra source FJ")
    if any(asset["pickState"] != "source_only_unbound" or asset["stableIds"] or asset["humanReviewed"] is not False or asset["publicRedistribution"] != "held" or not asset["defaultVisible"] or asset["localDisplay"]["state"] != "allowed" for asset in result["assets"]):
        raise BuildError("T79 must be locally displayable with source-only, no-review, and no-public-release status")
    base_ids = {asset["id"] for chunk in result["parent"]["chunks"] for asset in chunk["assets"]}
    if base_ids & set(EXPECTED):
        raise BuildError("T79 extension would duplicate source FJ nodes already in T77")
    input_hashes = result["lockedInputs"]
    evidence = {
        "revision": "T79-validation-v1", "task": "T79", "status": "passed_local_technical_validation",
        "frozenSourceSetSha256": sha(FREEZE.read_bytes()), "frozenMembershipSha256": result["frozen"]["membershipSha256"],
        "sourceMembers": len(EXPECTED), "ids": EXPECTED,
        "sidesFromOfficialNamedRelations": {asset["id"]: asset["side"] for asset in result["assets"]},
        "sourceSha256": {row["sourceElementFileId"]: row["sourceSha256"] for row in result["sourceAssets"]},
        "sourceHeaderBoundsDeltaMaxMm": {row["sourceElementFileId"]: row["geometry"]["sourceHeaderVsVertexBoundsMaxDeltaMm"] for row in result["sourceAssets"]},
        "sourceHeaderBoundsDiscrepancyIdsOver001mm": [row["sourceElementFileId"] for row in result["sourceAssets"] if not row["geometry"]["sourceHeaderVsVertexBoundsWithin001mm"]],
        "headerBoundsUsePolicy": "compare and preserve exact header values; use actual source vertex extrema for the derived runtime GLB bounds; header bounds are not surface/contact proof",
        "sourceVertexCounts": {row["sourceElementFileId"]: row["geometry"]["sourceVertexCount"] for row in result["sourceAssets"]},
        "sourceTriangleCounts": {row["sourceElementFileId"]: row["geometry"]["sourceTriangleCount"] for row in result["sourceAssets"]},
        "transformedBoundsM": gltf_bounds,
        "sourceArchivePayloadBytes": sum(row["sourceBytes"] for row in result["sourceAssets"]),
        "derivedGlbBytes": len(result["glb"]), "derivedGlbSha256": sha(result["glb"]),
        "sourceMetadataAndSceneInputSha256": input_hashes,
        "parentRuntimeExtension": {"t77ManifestSha256": result["parentSha256"], "t95OverlaySha256": result["overlaySha256"], "frame": FRAME, "unit": "m", "pose": POSE},
        "sameSceneContract": {"oneRoot": True, "oneRenderer": True, "root": "AnatomySceneRoot", "additionalViewport": False},
        "wholeMusclePartPolicy": result["sourceManifest"]["wholeMusclePartRepresentation"],
        "renderAndReleasePolicy": {"localDisplay": "allowed after scene QA", "sourceOnlyUnbound": True, "humanReview": "not_performed", "publicRedistribution": "held", "learnerNameBinding": "none"},
        "validationAssertions": ["exact FJ/FMA/BP/ELEMENT/parent relation", "OBJ header/hash/CRC/side/part/unit/frame/bounds", "finite triangular source parser with matching vertex normals", "T50/T69 axis transform and m scale, no mirror/recenter", "single GLB scene/one node per exact FJ/no transform", "T77+T95 runtime contract and no duplicate ID/node", "one source node for generic+side-specific rows sharing an FJ"],
    }
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
            freeze_sha = sha(FREEZE.read_bytes())
            write_owned(SOURCE_MANIFEST, result["sourceRaw"], "T79", freeze_sha)
            write_owned(EXTENSION, result["extensionRaw"], "T79", freeze_sha)
            write_owned(DERIVED / "manifest.json", result["cacheManifestRaw"], "T79", freeze_sha)
            evidence = validate(result)
        else:
            evidence = check_output(result)
        print(json.dumps({"status": evidence["status"], "members": evidence["sourceMembers"], "glbSha256": evidence["derivedGlbSha256"], "report": "work/evidence/T79/validation.json"}, indent=2))
        return 0
    except Exception as exc:
        print(f"T79 build/check failed closed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
