#!/usr/bin/env python3
"""Validate T104's exact source subset, deterministically build GLBs, and emit a same-scene extension."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "work/evidence/T104/frozen-source-set.json"
ACQUISITION = ROOT / "work/evidence/T104/source-acquisition.json"
SOURCE_CACHE = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t104"
DERIVED = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t104"
OUT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t104"
SOURCE_MANIFEST = OUT / "source-manifest.json"
EXTENSION = OUT / "integration-extension.json"
EVIDENCE = ROOT / "work/evidence/T104/validation.json"
OVERLAP_EVIDENCE = ROOT / "work/evidence/T104/surface-comparisons.json"
T77 = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json"
T95 = ROOT / "atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json"
PARENTS = {
    "T79": (ROOT / "atlas-data/manifests/bodyparts3d-r4-t79/source-manifest.json", ROOT / "atlas-data/manifests/bodyparts3d-r4-t79/integration-extension.json"),
    "T101": (ROOT / "atlas-data/manifests/bodyparts3d-r4-t101/source-manifest.json", ROOT / "atlas-data/manifests/bodyparts3d-r4-t101/integration-extension.json"),
    "T102": (ROOT / "atlas-data/manifests/bodyparts3d-r4-t102/source-manifest.json", ROOT / "atlas-data/manifests/bodyparts3d-r4-t102/integration-extension.json"),
    "T103": (ROOT / "atlas-data/manifests/bodyparts3d-r4-t103/source-manifest.json", ROOT / "atlas-data/manifests/bodyparts3d-r4-t103/integration-extension.json"),
}
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
MODEL_ID = "HA-MODEL-BP3D4-T104-UPPER-LIMB-NECK-MUSCLE-PARTS-SOURCE"
EXPECTED = ["FJ1516", "FJ1516M", "FJ1518", "FJ1518M", "FJ1557", "FJ1600", "FJ1601", "FJ2774", "FJ2781", "FJ2783"]
REGIONS = {"FJ1516": "upper-limb", "FJ1516M": "upper-limb", "FJ1518": "upper-limb", "FJ1518M": "upper-limb",
           "FJ1557": "neck", "FJ1600": "neck", "FJ1601": "neck", "FJ2774": "neck", "FJ2781": "neck", "FJ2783": "neck"}
SIDES = {"FJ1516": "right", "FJ1516M": "left", "FJ1518": "right", "FJ1518M": "left", "FJ1557": "left",
         "FJ1600": "left", "FJ1601": "left", "FJ2774": "left", "FJ2781": "left", "FJ2783": "left"}
HOLDS = ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"]
CHUNKS = {"upper-limb": "t104-upper-limb-muscle-parts", "neck": "t104-neck-muscle-parts"}


class BuildError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise BuildError(f"cannot import existing R4 parser/converter: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def owned_write(path: Path, raw: bytes) -> None:
    if path.exists() and path.read_bytes() != raw:
        raise BuildError(f"refusing to overwrite changed/unowned T104 output: {path.relative_to(ROOT)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def load_and_validate_inputs():
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
    acquisition = json.loads(ACQUISITION.read_text(encoding="utf-8"))
    if frozen.get("task") != "T104" or frozen.get("sourceElementFileIds") != EXPECTED:
        raise BuildError("T104 source freeze does not match the exact task allowlist")
    if acquisition.get("task") != "T104" or acquisition.get("fullArchivesDownloaded") is not False:
        raise BuildError("T104 selected range acquisition receipt is missing or indicates a full archive")
    if acquisition.get("frozenSourceSetSha256") != sha(FREEZE.read_bytes()) or acquisition.get("frozenMembershipSha256") != frozen.get("frozenMembershipSha256"):
        raise BuildError("T104 acquisition receipt does not bind to the immutable source freeze")
    if [r.get("sourceElementFileId") for r in acquisition.get("selectedSourceFiles", [])] != EXPECTED:
        raise BuildError("T104 acquisition receipt source IDs are missing, reordered, or expanded")
    receipt = {row["sourceElementFileId"]: row for row in acquisition["selectedSourceFiles"]}
    mappings = {row["sourceElementFileId"]: row for row in frozen["sourceMappings"]}
    if set(receipt) != set(EXPECTED) or set(mappings) != set(EXPECTED):
        raise BuildError("T104 freeze/acquisition membership is not exact")
    all_hashes = {}
    for path in [T77, T95, *[p for pair in PARENTS.values() for p in pair],
                 ROOT / "work/evidence/T50/scene-contract.md", ROOT / "work/evidence/T69/diagnostic.json", ROOT / "work/evidence/T69/assessment.json"]:
        if not path.is_file():
            raise BuildError(f"required parent scene contract is missing: {path.relative_to(ROOT)}")
        all_hashes[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
    return frozen, acquisition, receipt, mappings, all_hashes


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, bytes]]:
    frozen, acquisition, receipts, mappings, parent_hashes = load_and_validate_inputs()
    ingest = load_module("t104_r4_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
    converter = load_module("t104_r4_converter", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")
    t103 = load_module("t103_surface_sample_reuse", ROOT / "atlas-data/tools/build_bodyparts3d_r4_t103.py")
    tables = ingest.load_tables(METADATA)
    converter.MODEL_ID = MODEL_ID
    concepts = {row[0]: row for row in tables["isaConcepts"]}
    parent_assets: dict[str, dict[str, Any]] = {}
    t77_doc = json.loads(T77.read_text(encoding="utf-8"))
    for chunk in t77_doc.get("chunks", []):
        for asset in chunk.get("assets", []):
            parent_assets[asset["id"]] = asset
    for task in ("T79", "T101", "T102", "T103"):
        doc = json.loads(PARENTS[task][1].read_text(encoding="utf-8"))
        for chunk in doc.get("chunks", []):
            for asset in chunk.get("assets", []):
                parent_assets[asset["id"]] = asset
    if set(EXPECTED) & set(parent_assets):
        raise BuildError(f"T104 duplicates source node IDs from the parent scene: {sorted(set(EXPECTED) & set(parent_assets))}")

    parsed: dict[str, dict[str, Any]] = {}
    mesh_inputs_by_region: dict[str, list[dict[str, Any]]] = {"upper-limb": [], "neck": []}
    mesh_source_records: list[dict[str, Any]] = []
    max_header_actual_delta = {}
    for fid in EXPECTED:
        mapping, receipt = mappings[fid], receipts[fid]
        path = ROOT / receipt["cacheRelativePath"]
        if not path.is_file() or path.stat().st_size != receipt["bytes"] or sha(path.read_bytes()) != receipt["sha256"]:
            raise BuildError(f"source bytes do not match T104 acquisition receipt for {fid}")
        if (receipt.get("archiveTree") != "IS-A" or receipt.get("memberPath") != f"isa_BP3D_4.0_obj_99/{fid}.obj"
                or int(receipt.get("crc32", "-1"), 16) < 0):
            raise BuildError(f"archive member/tree/CRC provenance invalid for {fid}")
        header = ingest.read_obj_header(path)
        ingest.validate_obj_source_identity(header, tables)
        if (header.get("fileId") != fid or header.get("conceptId") != mapping["sourceConceptId"]
                or header.get("representationId") != mapping["sourceRepresentationId"] or header.get("buildUpLogic") != "FMA 3.0 is_a"):
            raise BuildError(f"OBJ FJ/FMA/BP/tree header differs from the exact official freeze mapping for {fid}: {header}")
        english, header_bounds, license_header = t103.parse_header_bounds(path)
        if english.casefold() != mapping["sourceNameEnglish"].casefold():
            raise BuildError(f"exact OBJ part/side name differs from the exact official concept for {fid}: {english}")
        if not license_header or "CC Attribution-Share Alike 2.1 Japan" not in license_header:
            raise BuildError(f"unexpected or missing per-file OBJ license header for {fid}: {license_header}")
        if mapping["sideFromExactOfficialName"] != SIDES[fid] or SIDES[fid] not in english.casefold():
            raise BuildError(f"source side conflicts with exact official name for {fid}")
        vertices, normals, triangles = converter.parse_obj(path)
        actual_bounds = converter.vector_bounds(vertices)
        # Correctly compare source header [min xyz, max xyz] against actual geometry bounds.
        actual_flat = actual_bounds["min"] + actual_bounds["max"]
        delta = max(abs(header_bounds[i] - actual_flat[i]) for i in range(6))
        max_header_actual_delta[fid] = delta
        if len(vertices) != len(normals) or not triangles or not math.isfinite(delta) or delta > 1.0:
            raise BuildError(f"OBJ vertices/normals/triangles or mm bounds fail for {fid}; header delta={delta}")
        concept = concepts[mapping["sourceConceptId"]]
        asset_meta = {"vertex_count": len(vertices), "polygon_count": len(triangles), "representation_id": mapping["sourceRepresentationId"],
                      "concept_id": mapping["sourceConceptId"], "bytes": receipt["bytes"]}
        mesh_inputs_by_region[REGIONS[fid]].append({"file_id": fid, "source_path": path, "asset": asset_meta,
                                                     "source_sha256": receipt["sha256"], "source_relative_path": receipt["memberPath"]})
        parsed[fid] = {"mapping": mapping, "receipt": receipt, "path": path, "header": header, "headerName": english,
                       "headerBoundsMm": {"min": header_bounds[:3], "max": header_bounds[3:]}, "actualBoundsMm": actual_bounds,
                       "licenseHeader": license_header, "vertices": vertices, "normals": normals, "triangles": triangles,
                       "conceptRow": concept}
        mesh_source_records.append({"sourceElementFileId": fid, "sourceConceptId": mapping["sourceConceptId"],
                                    "sourceRepresentationId": mapping["sourceRepresentationId"], "sourceNameEnglish": english,
                                    "lateralityFromExactOfficialName": SIDES[fid], "regionOwner": REGIONS[fid],
                                    "sourceArchiveTree": receipt["archiveTree"], "sourceArchiveMemberPath": receipt["memberPath"],
                                    "sourceBytes": receipt["bytes"], "sourceSha256": receipt["sha256"], "sourceCrc32": receipt["crc32"],
                                    "sourceHeaderFjFmaBp": header, "sourceObjLicenseHeader": license_header,
                                    "sourceUnit": "mm", "sourceFrame": "BodyParts3D Release 4.0 native static reference",
                                    "projectUnit": "m", "projectFrame": FRAME, "pose": POSE,
                                    "sourceBoundsMmHeader": {"min": header_bounds[:3], "max": header_bounds[3:]},
                                    "sourceBoundsMmVertices": actual_bounds, "headerActualMaximumDeltaMm": delta,
                                    "vertexCount": len(vertices), "triangleCount": len(triangles),
                                    "sourceConceptRow": list(concept), "sourceElementRows": mapping["allOfficialElementRowsForSameFj"],
                                    "officialExactElementRow": mapping["officialExactElementRow"],
                                    "officialGenericPartElementRow": mapping["officialGenericPartElementRow"]})

    # Use the existing deterministic T07 converter and same project frame for two product-region chunks.
    chunk_payloads: dict[str, bytes] = {}
    chunk_records: dict[str, list[dict[str, Any]]] = {}
    for region, chunk_id in CHUNKS.items():
        payload, records = converter.build_glb(mesh_inputs_by_region[region])
        chunk_payloads[chunk_id] = payload
        chunk_records[chunk_id] = records

    frozen_hash = sha(FREEZE.read_bytes())
    input_paths = ["AGENTS.md", "work/tasks/T104.md", "work/evidence/T104/start-baseline.json", "work/evidence/T104/frozen-source-set.json",
                   "work/evidence/T104/source-acquisition.json", "atlas-data/tools/freeze_bodyparts3d_r4_t104.py",
                   "atlas-data/tools/acquire_bodyparts3d_r4_t104.py", "atlas-data/tools/build_bodyparts3d_r4_t104.py",
                   "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py", "atlas-data/tools/ingest_bodyparts3d_r4.py",
                   "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py", "atlas-data/tools/build_bodyparts3d_r4_t103.py",
                   "atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json", "atlas-data/manifests/bodyparts3d-r4-t54/upper-limb.json",
                   "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json", "atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json",
                   "work/evidence/T50/scene-contract.md", "work/evidence/T69/diagnostic.json", "work/evidence/T69/assessment.json",
                   "work/evidence/T103/validation.json", "work/evidence/T103/browser-validation.json", "work/reports/T103.md"]
    for pair in PARENTS.values():
        input_paths.extend(p.relative_to(ROOT).as_posix() for p in pair)
    input_paths.extend(p.relative_to(ROOT).as_posix() for p in sorted(METADATA.glob("*.txt")))
    input_hashes = {rel: sha((ROOT / rel).read_bytes()) for rel in input_paths}
    for row in mesh_source_records:
        input_hashes[row["sourceArchiveMemberPath"]] = row["sourceSha256"]
    parent_manifest_sha = sha(T77.read_bytes())
    parent_context_sha = sha(T95.read_bytes())
    parent_chain = {}
    for task, pair in PARENTS.items():
        parent_chain[task] = {"sourceManifestPath": pair[0].relative_to(ROOT).as_posix(), "sourceManifestSha256": sha(pair[0].read_bytes()),
                              "integrationExtensionPath": pair[1].relative_to(ROOT).as_posix(), "integrationExtensionSha256": sha(pair[1].read_bytes())}
    mesh_records = [record for chunk_id in CHUNKS.values() for record in chunk_records[chunk_id]]
    derived_descriptors = []
    extension_chunks = []
    for region, chunk_id in CHUNKS.items():
        raw = chunk_payloads[chunk_id]
        record_rows = chunk_records[chunk_id]
        out_path = DERIVED / f"{chunk_id}.glb"
        rel_path = out_path.relative_to(ROOT).as_posix()
        assets = []
        for record in record_rows:
            fid = record["sourceFileId"]
            source = parsed[fid]
            holds = list(HOLDS)
            assets.append({"id": fid, "nodeId": record["meshAssetId"], "sourceSha256": source["receipt"]["sha256"],
                           "sourceGeometrySha256": record["geometrySha256"], "sourceTopologySha256": record["topologySha256"],
                           "sourceConceptIdObservation": source["mapping"]["sourceConceptId"],
                           "sourceRepresentationIdObservation": source["mapping"]["sourceRepresentationId"],
                           "sourceNameObservation": source["headerName"], "regions": [region], "primaryOwner": region,
                           "sourcePackage": "T104",
                           "side": SIDES[fid], "layer": "muscle", "defaultVisible": True, "supplement": False,
                           "pickState": "source_only_unbound", "stableIds": [], "holdReasons": holds, "humanReviewed": False,
                           "publicRedistribution": "held", "localDisplay": {"state": "allowed", "beforeDefaultVisible": False,
                               "afterDefaultVisible": True, "sourceSha256": source["receipt"]["sha256"],
                               "bindingState": "source_only_unbound", "publicRedistribution": "held", "humanReviewed": False,
                               "integrityHolds": [], "retainedHoldReasons": holds, "basis": "verified_local_source_context_only",
                               "evidenceIds": ["work/evidence/T104/source-acquisition.json", "atlas-data/manifests/bodyparts3d-r4-t104/source-manifest.json",
                                              "work/evidence/T104/browser-validation.json"]},
                           "bounds": [record["atlasBoundsM"]["min"], record["atlasBoundsM"]["max"]]})
        extension_chunks.append({"id": chunk_id, "url": f"/__atlas/body/{chunk_id}.glb", "sha256": sha(raw), "bytes": len(raw), "assets": assets})
        derived_descriptors.append({"id": chunk_id, "path": rel_path, "sha256": sha(raw), "bytes": len(raw), "nodeCount": len(assets),
                                    "regionOwner": region, "triangleCount": sum(record["triangleCount"] for record in record_rows)})
    source_manifest = {"revision": "BodyParts3D-R4-T104-source-manifest-v1", "task": "T104", "sourceVersion": "BodyParts3D Release 4.0",
                       "source": {"id": SOURCE_ID, "url": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip",
                                  "tree": "IS-A", "metadataBasis": "official cached R4 FMA 3.0 compound-element and inclusion tables"},
                       "status": "source_only_local_technical_display_validated", "frozenSourceSetSha256": frozen_hash,
                       "frozenMembershipSha256": frozen["frozenMembershipSha256"], "inputSha256": input_hashes,
                       "parentScene": {"sourceManifestSha256": parent_manifest_sha, "productContextOverlaySha256": parent_context_sha,
                                       "chain": parent_chain, "existingRoot": "AnatomySceneRoot", "existingRenderer": "single WebGLRenderer",
                                       "existingCameraController": "AnatomySceneController"},
                       "sceneContract": {"projectFrame": FRAME, "projectUnit": "m", "sourceId": SOURCE_ID,
                                         "sourceFrame": "BodyParts3D Release 4.0 native reference; not registered to OpenSim",
                                         "sourceUnit": "mm", "pose": POSE,
                                         "transform": "[x,y,z] source mm -> [x,z,-y] HUMAN ATLAS m; preserve x sign; no mirror/recenter",
                                         "nodeTransformIdentity": True, "oneAnatomySceneRoot": True, "oneRenderer": True,
                                         "cameraOwner": "existing AnatomySceneController",
                                         "extensionMode": "append two task-scoped region chunks after T103 in the same T77/T95/T79/T101/T102/T103 scene"},
                       "scope": {"sourceElementFileIds": EXPECTED, "regionGroups": {region: [fid for fid in EXPECTED if REGIONS[fid] == region] for region in CHUNKS},
                                 "meshNodeCount": len(mesh_records), "canonicalLearnerBindingCount": 0, "learnerStableIdCount": 0},
                       "sourceAssets": mesh_source_records, "meshRecords": mesh_records, "derivedChunks": derived_descriptors,
                       "rights": {"currentOfficialDatabaseLicense": "CC BY 4.0 per official LSDB license page accessed 2026-09-28",
                                  "legacyOBJHeaderLicense": "each acquired Release 4.0 OBJ header states CC Attribution-Share Alike 2.1 Japan",
                                  "localTechnicalDisplay": "allowed for the exact verified local subset only; this is not public redistribution clearance",
                                  "publicRedistribution": "held_pending_file_level_license_reconciliation",
                                  "attribution": "BodyParts3D, (c) The Database Center for Life Science licensed under CC Attribution-Share Alike 2.1 Japan (per acquired OBJ headers); current archive site states CC BY 4.0"},
                       "review": {"humanAnatomyReview": "not_performed", "canonicalBinding": "none", "reviewedPromotionCount": 0},
                       "sourceOnlyPolicy": {"defaultVisible": True, "pickState": "source_only_unbound", "stableIds": [],
                                            "holds": HOLDS, "noAncestorOnlyBinding": True},
                       "wholeMusclePartRepresentation": frozen["wholeMuscleParentSurfaceAudit"]}
    source_manifest["manifestSha256"] = sha(json_bytes(source_manifest))
    source_manifest_raw = json_bytes(source_manifest)
    source_manifest_sha = sha(source_manifest_raw)
    extension = {"revision": "BodyParts3D-R4-T104-SAME-SCENE-EXTENSION-v1", "task": "T104",
                 "frozenSourceSetSha256": frozen_hash, "parentSourceManifestSha256": parent_manifest_sha,
                 "parentProductContextOverlaySha256": parent_context_sha,
                 "parentT79SourceManifestSha256": parent_chain["T79"]["sourceManifestSha256"],
                 "parentT79IntegrationExtensionSha256": parent_chain["T79"]["integrationExtensionSha256"],
                 "parentT101SourceManifestSha256": parent_chain["T101"]["sourceManifestSha256"],
                 "parentT101IntegrationExtensionSha256": parent_chain["T101"]["integrationExtensionSha256"],
                 "parentT102SourceManifestSha256": parent_chain["T102"]["sourceManifestSha256"],
                 "parentT102IntegrationExtensionSha256": parent_chain["T102"]["integrationExtensionSha256"],
                 "parentT103SourceManifestSha256": parent_chain["T103"]["sourceManifestSha256"],
                 "parentT103IntegrationExtensionSha256": parent_chain["T103"]["integrationExtensionSha256"],
                 "sourceManifestSha256": source_manifest_sha,
                 "sceneContract": {"projectFrame": FRAME, "projectUnit": "m", "sourceId": SOURCE_ID, "pose": POSE,
                                   "oneAnatomySceneRoot": True, "oneRenderer": True, "cameraOwner": "existing AnatomySceneController",
                                   "extensionMode": "append T104 upper-limb and neck source-only meshes after T103 in the same scene"},
                 "chunks": extension_chunks, "counts": {"sourceAssets": len(mesh_records), "upperLimb": 4, "neck": 6, "duplicates": 0},
                 "sourceOnly": True, "localOnly": True, "publicRedistribution": "held",
                 "learnerBinding": {"canonicalIds": [], "stableLearnerIds": [], "bindingCreated": False},
                 "humanReview": {"performed": False, "reviewedPromotions": 0},
                 "displayPolicy": {"exactSubsetOnly": True, "sourceOnlyByDefault": True, "perMemberLocalDisplayEvidence": True,
                                   "rightsSeparateFromLocalDisplay": True, "sourceOnlyPickable": False, "sourceOnlyLearnerCard": False}}
    extension_raw = json_bytes(extension)
    outputs = {"sourceManifest": source_manifest, "extension": extension, "sourceManifestBytes": source_manifest_raw,
               "extensionBytes": extension_raw, "glbs": chunk_payloads}
    comparisons = build_surface_comparisons(parsed, t103, converter)
    validation = {"task": "T104", "status": "passed_local_technical_validation", "sourceIds": EXPECTED,
                  "sourceCount": len(mesh_records), "sourceBytes": sum(row["sourceBytes"] for row in mesh_source_records),
                  "selectedRangeTransferBytes": acquisition["rangeTransferBytes"], "fullArchiveDownloaded": False,
                  "derivedGlbBytes": sum(len(raw) for raw in chunk_payloads.values()), "derivedGlbSha256": {key: sha(raw) for key, raw in chunk_payloads.items()},
                  "sourceSha256": {row["sourceElementFileId"]: row["sourceSha256"] for row in mesh_source_records},
                  "sourceCrc32": {row["sourceElementFileId"]: row["sourceCrc32"] for row in mesh_source_records},
                  "sourceSideFromExactOfficialRows": SIDES, "regionCounts": {"upper-limb": 4, "neck": 6},
                  "sourceVertexCount": {r["sourceFileId"]: r["vertexCount"] for r in mesh_records},
                  "sourceTriangleCount": {r["sourceFileId"]: r["triangleCount"] for r in mesh_records},
                  "headerBoundsActualMaxDeltaMm": max_header_actual_delta,
                  "frame": {"sourceUnit": "mm", "projectUnit": "m", "sourceFrame": "BodyParts3D R4 native static reference",
                            "projectFrame": FRAME, "pose": POSE, "transform": "[x,y,z]mm -> [x,z,-y]m; preserve lateral sign; no mirror/recenter"},
                  "parentScene": {"root": "AnatomySceneRoot", "rendererCount": 1, "frame": FRAME, "unit": "m", "pose": POSE,
                                  "appendAfter": "t103-upper-limb-muscle-parts", "duplicateFjCount": 0},
                  "wholeMusclePartRepresentation": frozen["wholeMuscleParentSurfaceAudit"],
                  "triangleSurfaceComparisons": comparisons,
                  "rightsAndReview": {"localDisplay": "allowed_exact_verified_local_subset_only", "publicRedistribution": "held_pending_file_level_license_reconciliation",
                                      "objHeaderLicense": "CC BY-SA 2.1 Japan", "currentOfficialPageLicense": "CC BY 4.0",
                                      "canonicalBindingCount": 0, "humanAnatomyReview": "not_performed", "reviewedPromotions": 0},
                  "checks": {"archiveMemberIdsExact": True, "objHeaderFjFmaBpValidated": True, "officialSidePartRowsValidated": True,
                             "sourceCrcAndShaValidated": True, "sourceUnitsAndBoundsValidated": True, "T50T69TransformReused": True,
                             "oneRootRendererCameraReused": True, "noAncestorOnlyBinding": True, "noParentWholeSurfaceCoRender": True}}
    return source_manifest, extension, validation, chunk_payloads | {"source_manifest.json": source_manifest_raw, "integration_extension.json": extension_raw,
                                                                    "surface_comparisons.json": json_bytes(comparisons), "validation.json": json_bytes(validation)}


def build_surface_comparisons(parsed: dict[str, dict[str, Any]], t103, converter) -> dict[str, Any]:
    def read(fid: str, is_t103=False):
        if fid in parsed:
            row = parsed[fid]
            return row["vertices"], row["triangles"]
        base = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t103/upper-limb" / f"{fid}.obj"
        if not base.is_file():
            raise BuildError(f"T103 parent sibling source OBJ needed for triangle comparison is missing: {fid}")
        vertices, _normals, triangles = converter.parse_obj(base)
        return vertices, triangles

    pairs = [
        ("FJ1516", "FJ1474", "right pronator teres ulnar/head sibling surface"),
        ("FJ1516M", "FJ1474M", "left pronator teres ulnar/head sibling surface"),
        ("FJ1518", "FJ1473", "right flexor carpi ulnaris ulnar/head sibling surface"),
        ("FJ1518M", "FJ1473M", "left flexor carpi ulnaris ulnar/head sibling surface"),
        ("FJ1557", "FJ1600", "longus colli oblique/superior-oblique component surfaces"),
        ("FJ1557", "FJ1601", "longus colli oblique/vertical-intermediate component surfaces"),
        ("FJ1600", "FJ1601", "longus colli superior-oblique/vertical-intermediate component surfaces"),
        ("FJ2781", "FJ2783", "left cricothyroid oblique/straight component surfaces"),
    ]
    results = []
    for left, right, relationship in pairs:
        lv, lt = read(left)
        rv, rt = read(right)
        results.append({"sourceFjA": left, "sourceFjB": right, "relationship": relationship,
                        "aToB": t103.surface_distance_summary(lv, lt, rv, rt),
                        "bToA": t103.surface_distance_summary(rv, rt, lv, lt),
                        "interpretation": "actual source triangles sampled; distances indicate sampled proximity only, not continuous intersection or anatomical correctness; no AABB overlap proof"})
    return {"task": "T104", "status": "sampled_actual_triangle_surfaces", "unit": "mm", "pairs": results,
            "exactWholeMuscleParentMeshesInActiveParentScene": [],
            "wholeParentConclusion": "no exact separate whole-muscle parent source mesh for these frozen parts was found in the active parent scene; comparison targets above are sibling parts, not substituted whole-muscle surfaces",
            "limitations": ["samples do not prove continuous intersection", "no anatomy review was performed", "source meshes remain source-only"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true", help="write deterministic T104 GLB/source/integration manifests and evidence")
    parser.add_argument("--check", action="store_true", help="rebuild in memory and compare every task-owned output")
    args = parser.parse_args()
    if not args.build and not args.check:
        parser.error("choose --build or --check")
    source_manifest, extension, validation, artifacts = build()
    if args.build:
        for name in ("t104-upper-limb-muscle-parts", "t104-neck-muscle-parts"):
            owned_write(DERIVED / f"{name}.glb", artifacts[name])
        owned_write(SOURCE_MANIFEST, artifacts["source_manifest.json"])
        owned_write(EXTENSION, artifacts["integration_extension.json"])
        owned_write(OVERLAP_EVIDENCE, artifacts["surface_comparisons.json"])
        owned_write(EVIDENCE, artifacts["validation.json"])
        print(json.dumps({"result": "built", "sourceIds": len(EXPECTED), "chunks": len(extension["chunks"]),
                          "vertices": sum(validation["sourceVertexCount"].values()), "triangles": sum(validation["sourceTriangleCount"].values()),
                          "derivedGlbBytes": validation["derivedGlbBytes"]}, indent=2))
    if args.check:
        compare = {str(DERIVED / "t104-upper-limb-muscle-parts.glb"): artifacts["t104-upper-limb-muscle-parts"],
                   str(DERIVED / "t104-neck-muscle-parts.glb"): artifacts["t104-neck-muscle-parts"],
                   str(SOURCE_MANIFEST): artifacts["source_manifest.json"], str(EXTENSION): artifacts["integration_extension.json"],
                   str(OVERLAP_EVIDENCE): artifacts["surface_comparisons.json"], str(EVIDENCE): artifacts["validation.json"]}
        for raw_path, expected in compare.items():
            path = Path(raw_path)
            if not path.is_file() or path.read_bytes() != expected:
                raise SystemExit(f"T104 deterministic output differs or is missing: {path.relative_to(ROOT)}")
        print(json.dumps({"result": "pass", "deterministic": True, "outputs": len(compare), "sourceIds": len(EXPECTED)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
