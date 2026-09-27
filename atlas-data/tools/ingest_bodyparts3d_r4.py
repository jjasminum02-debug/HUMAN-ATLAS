#!/usr/bin/env python3
"""Build a source-faithful BodyParts3D R4 inventory and convert cached samples.

The official indexes describe the complete downloadable ELEMENT inventory;
the local mesh cache is intentionally a partial subset. The tool never creates
canonical learner IDs, mirrors a unilateral mesh, synthesizes an LOD, or edits
an original source file.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import shutil
import struct
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "atlas-data/source-cache/bodyparts3d-r4"
METADATA = CACHE / "metadata"
SOURCE_ASSET_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
SOURCE_VERSION = "BodyParts3D Release 4.0; LATEST README updated 2025-02-27"
SOURCE_URL_ROOT = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/"
ATTRIBUTION = (
    "BodyParts3D, © The Database Center for Life Science licensed under "
    "CC Attribution 4.0 International"
)
METADATA_FILES = {
    "isaConcepts": "isa_parts_list_e.txt",
    "partofConcepts": "partof_parts_list_e.txt",
    "isaInclusion": "isa_inclusion_relation_list.txt",
    "partofInclusion": "partof_inclusion_relation_list.txt",
    "isaCompoundElements": "isa_element_parts.txt",
    "partofCompoundElements": "partof_element_parts.txt",
}
METADATA_HEADERS = {
    "isaConcepts": ["concept id", "representation id", "en"],
    "partofConcepts": ["concept id", "representation id", "en"],
    "isaInclusion": ["parent id", "parent name", "child id", "child name"],
    "partofInclusion": ["parent id", "parent name", "child id", "child name"],
    "isaCompoundElements": ["concept id", "name", "element file id"],
    "partofCompoundElements": ["concept id", "name", "element file id"],
}
PRODUCT_CATEGORIES = [
    {"id": "head", "labelKo": "머리", "muscleRoots": ["FMA9616"], "boneRoots": ["FMA7154"], "boneRootTree": "partof"},
    {"id": "neck", "labelKo": "목", "muscleRoots": ["FMA9617"], "muscleExclusions": ["FMA46619", "FMA46562"], "boneRoots": ["FMA7155"], "boneRootTree": "partof"},
    {"id": "back", "labelKo": "등", "muscleRoots": ["FMA22594"], "boneRoots": ["FMA24189", "FMA24217", "FMA61681"], "boneRootTree": "partof"},
    {"id": "shoulder-scapular", "labelKo": "어깨·어깨뼈", "muscleRoots": ["FMA37347"], "boneRoots": ["FMA23218", "FMA23219", "FMA33642", "FMA33644", "FMA33645", "FMA33646", "FMA33647"], "boneRootTree": "partof"},
    {"id": "thorax", "labelKo": "가슴우리", "muscleRoots": ["FMA9619"], "boneRoots": ["FMA9576", "FMA7481"], "boneRootTree": "partof"},
    {"id": "abdomen-lumbar", "labelKo": "배·허리", "muscleRoots": ["FMA9620"], "boneRoots": ["FMA9577"], "boneRootTree": "partof"},
    {"id": "pelvis-perineum", "labelKo": "골반·샅", "muscleRoots": ["FMA9623", "FMA19086"], "boneRoots": ["FMA9578", "FMA9579", "FMA16580", "FMA20226", "FMA20227", "FMA20347"], "boneRootTree": "partof"},
    {"id": "gluteal-hip", "labelKo": "볼기·깊은엉덩이", "muscleRoots": ["FMA37367"], "boneRoots": ["FMA24965", "FMA24966", "FMA16581", "FMA16582", "FMA16583"], "boneRootTree": "partof"},
    {"id": "thigh", "labelKo": "넙다리", "muscleRoots": ["FMA22470"], "boneRoots": ["FMA24968", "FMA24969"], "boneRootTree": "partof"},
    {"id": "leg", "labelKo": "종아리", "muscleRoots": ["FMA22471"], "boneRoots": ["FMA24980", "FMA24981"], "boneRootTree": "partof"},
    {"id": "foot", "labelKo": "발", "muscleRoots": ["FMA37369"], "boneRoots": ["FMA11343", "FMA11344", "FMA73086", "FMA73087"], "boneRootTree": "partof"},
    {"id": "upper-limb", "labelKo": "팔·손", "muscleRoots": ["FMA37348"], "boneRoots": ["FMA7185", "FMA7186", "FMA24880", "FMA24881", "FMA9713", "FMA9714", "FMA11345", "FMA11346"], "boneRootTree": "partof"},
]
MUSCLE_ROOT_SOURCE = "BodyParts3D IS-A source hierarchy exact FMA roots"
BONE_ROOT_SOURCE = "BodyParts3D PART-OF source hierarchy exact FMA roots"
REGION_POLICY = (
    "Acquisition routing candidates only, not canonical identities, runtime "
    "memberships, or anatomy approval. Root candidates are source FMA IDs; "
    "multi-region appearances reuse the same source FMA/FJ IDs."
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json_bytes(value))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_tsv(path: Path, expected_header: list[str]) -> list[list[str]]:
    if not path.is_file():
        raise ValueError(f"source metadata is missing: {path}; restore the T51 cache or fetch official metadata")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle, delimiter="\t"))
    if not rows or rows[0] != expected_header:
        raise ValueError(f"unexpected source metadata header in {path}: {rows[0] if rows else None}")
    return [row for row in rows[1:] if row and any(cell.strip() for cell in row)]


def load_tables(metadata_dir: Path = METADATA) -> dict[str, list[list[str]]]:
    return {
        key: read_tsv(metadata_dir / file_name, METADATA_HEADERS[key])
        for key, file_name in METADATA_FILES.items()
    }


def read_obj_header(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"fileId": None, "representationId": None, "buildUpLogic": None, "conceptId": None, "licenseHeader": None}
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.startswith("#"):
                break
            match = re.match(r"#\s*(File ID|Representation ID|Build-up logic|Concept ID)\s*:\s*(.*?)\s*$", line)
            if match:
                key = {"File ID": "fileId", "Representation ID": "representationId", "Build-up logic": "buildUpLogic", "Concept ID": "conceptId"}[match.group(1)]
                result[key] = match.group(2)
            if "license for this database" in line.lower():
                result["licenseHeader"] = line.lstrip("# ").strip()
    return result


def validate_obj_source_identity(header: dict[str, Any], tables: dict[str, list[list[str]]]) -> None:
    file_id = header.get("fileId")
    fma = header.get("conceptId")
    representation = header.get("representationId")
    build = header.get("buildUpLogic")
    if build == "FMA 3.0 is_a":
        concept_key, element_key = "isaConcepts", "isaCompoundElements"
    elif build == "FMA 3.0 part_of":
        concept_key, element_key = "partofConcepts", "partofCompoundElements"
    else:
        raise ValueError("OBJ build-up logic is not a recognized BodyParts3D Release 4.0 tree")
    if not file_id or not any(row[2] == file_id for key in ("isaCompoundElements", "partofCompoundElements") for row in tables[key]):
        raise ValueError("source ELEMENT file ID is absent from the official Release 4.0 metadata; mapping gap, not a download failure")
    if not fma or not representation:
        raise ValueError("OBJ header lacks source FMA/BP identity; no source identity will be inferred")
    if (fma, representation) not in {(row[0], row[1]) for row in tables[concept_key]}:
        raise ValueError("OBJ header FMA/BP pair is absent from its official source tree; identity mapping held")
    if (fma, file_id) not in {(row[0], row[2]) for row in tables[element_key]}:
        raise ValueError("OBJ header FJ/FMA association is absent from its official source tree; identity mapping held")


def sync_mesh_cache(root: Path = ROOT) -> list[dict[str, Any]]:
    inventory = load_json(root / "atlas-data/catalog/whole-body-inventory-t15g.json")
    samples = inventory["counts"]["localAssets"]["sourceObjFileInventory"]
    destination = root / "atlas-data/source-cache/bodyparts3d-r4/mesh/IS-A"
    destination.mkdir(parents=True, exist_ok=True)
    tables = load_tables(root / "atlas-data/source-cache/bodyparts3d-r4/metadata")
    records = []
    for row in sorted(samples, key=lambda item: Path(item["path"]).name):
        source = root / row["path"]
        file_id = source.stem
        target = destination / source.name
        if not source.is_file():
            raise ValueError(f"historical source OBJ is missing: {row['path']}")
        actual_hash = sha256_file(source)
        if actual_hash != row["sha256"]:
            raise ValueError(f"historical T15g hash mismatch for {row['path']}")
        if target.exists() and sha256_file(target) != actual_hash:
            raise ValueError(f"existing source-cache file differs; refusing to overwrite: {target}")
        if not target.exists():
            shutil.copyfile(source, target)
        header = read_obj_header(target)
        if header["fileId"] != file_id or header["buildUpLogic"] != "FMA 3.0 is_a":
            raise ValueError(f"source OBJ header identity/build tree mismatch: {target}")
        validate_obj_source_identity(header, tables)
        records.append({
            "sourceFileId": file_id,
            "sourceRelativePath": row["path"],
            "cacheRelativePath": target.relative_to(root).as_posix(),
            "bytes": target.stat().st_size,
            "sha256": actual_hash,
            "header": header,
            "sourceFileHeaderLicenseStatus": "legacy_header_claim_retained_verbatim",
            "distributionStatus": "held_pending_file_level_license_reconciliation",
        })
    return records


def merge_cache_index(root: Path, added_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cache_root = root / "atlas-data/source-cache/bodyparts3d-r4"
    index_path = cache_root / "cache-index.json"
    existing = load_json(index_path).get("files", []) if index_path.is_file() else []
    by_id = {row["sourceFileId"]: row for row in existing}
    if len(by_id) != len(existing):
        raise ValueError("duplicate FJ IDs in local source-cache index")
    for row in added_rows:
        prior = by_id.get(row["sourceFileId"])
        if prior and prior["sha256"] != row["sha256"]:
            raise ValueError(f"same FJ ID has a different cached hash; refusing to overwrite: {row['sourceFileId']}")
        by_id.setdefault(row["sourceFileId"], row)
    result = sorted(by_id.values(), key=lambda row: row["sourceFileId"])
    write_json(index_path, {"revision": "BodyParts3D-R4-T51-local-cache-index-v1", "sourceId": SOURCE_ASSET_ID, "files": result, "rightsBoundary": "Original source bytes and header claims retained; do not distribute pending file-level rights reconciliation."})
    return result


def ingest_obj_file(source_path: Path, root: Path = ROOT) -> dict[str, Any]:
    """Copy one externally obtained OBJ only when its source IDs occur in R4 metadata."""
    source_path = source_path.expanduser().resolve()
    if not source_path.is_file() or source_path.suffix.lower() != ".obj":
        raise ValueError(f"expected one local BodyParts3D .obj file: {source_path.name}")
    header = read_obj_header(source_path)
    tables = load_tables(root / "atlas-data/source-cache/bodyparts3d-r4/metadata")
    validate_obj_source_identity(header, tables)
    file_id = header["fileId"]
    vertices, normals, triangles = parse_obj_for_glb(source_path)
    if not vertices or len(normals) != len(vertices) or not triangles:
        raise ValueError("OBJ geometry is empty or structurally inconsistent; source file not cached")
    target = root / "atlas-data/source-cache/bodyparts3d-r4/mesh/ingested" / f"{file_id}.obj"
    digest = sha256_file(source_path)
    if target.exists():
        if sha256_file(target) != digest:
            raise ValueError(f"cache already contains this FJ ID with different bytes; refusing to overwrite: {file_id}")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target)
    row = {
        "sourceFileId": file_id,
        "sourceRelativePath": f"local-import:{source_path.name}",
        "cacheRelativePath": target.relative_to(root).as_posix(),
        "bytes": target.stat().st_size,
        "sha256": digest,
        "header": header,
        "acquisitionMethod": "explicit_local_obj_import_no_network_request",
        "downloadAttempt": False,
        "downloadFailure": False,
        "sourceFileHeaderLicenseStatus": "legacy_or_unreconciled_claim_retained_verbatim",
        "distributionStatus": "held_pending_file_level_license_reconciliation",
    }
    merge_cache_index(root, [row])
    return row


def validate_cached_source_records(root: Path, records: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    tables = load_tables(root / "atlas-data/source-cache/bodyparts3d-r4/metadata")
    for row in records:
        file_id = row.get("sourceFileId")
        if not isinstance(file_id, str) or file_id in seen:
            raise ValueError(f"missing or duplicate source FJ ID in local cache index: {file_id}")
        seen.add(file_id)
        path = root / row["cacheRelativePath"]
        if not path.is_file():
            raise ValueError(f"local cache source file is missing: {row['cacheRelativePath']}")
        if path.stat().st_size != row.get("bytes") or sha256_file(path) != row.get("sha256"):
            raise ValueError(f"local source cache size/hash changed; refusing to build: {file_id}")
        actual_header = read_obj_header(path)
        expected_header = row.get("header", {})
        for key in ("fileId", "conceptId", "representationId", "buildUpLogic", "licenseHeader"):
            if actual_header.get(key) != expected_header.get(key):
                raise ValueError(f"local source cache OBJ header changed; refusing to build: {file_id} ({key})")
        validate_obj_source_identity(actual_header, tables)


def adjacency(rows: list[list[str]], parent_index: int = 0, child_index: int = 2) -> dict[str, set[str]]:
    output: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        output[row[parent_index]].add(row[child_index])
    return output


def closure(roots: list[str], edges: dict[str, set[str]], excluded_roots: list[str] | None = None) -> set[str]:
    excluded = closure(excluded_roots or [], edges) if excluded_roots else set()
    found: set[str] = set()
    stack = list(roots)
    while stack:
        current = stack.pop()
        if current in found or current in excluded:
            continue
        found.add(current)
        stack.extend(sorted(edges.get(current, set()), reverse=True))
    return found


def region_map(root: Path, tables: dict[str, list[list[str]]]) -> tuple[dict[str, dict[str, Any]], dict[str, set[str]], dict[str, set[str]]]:
    isa_names = {row[0]: row[2] for row in tables["isaConcepts"]}
    partof_names = {row[0]: row[2] for row in tables["partofConcepts"]}
    isa_edges = adjacency(tables["isaInclusion"])
    partof_edges = adjacency(tables["partofInclusion"])
    bone_fma = closure(["FMA5018"], isa_edges)
    muscle_fma = closure(["FMA5022"], isa_edges)
    isa_elements_by_concept: dict[str, set[str]] = defaultdict(set)
    partof_elements_by_concept: dict[str, set[str]] = defaultdict(set)
    for fma, _name, file_id in tables["isaCompoundElements"]:
        isa_elements_by_concept[fma].add(file_id)
    for fma, _name, file_id in tables["partofCompoundElements"]:
        partof_elements_by_concept[fma].add(file_id)

    result: dict[str, dict[str, Any]] = {}
    muscle_sets: dict[str, set[str]] = {}
    bone_sets: dict[str, set[str]] = {}
    for category in PRODUCT_CATEGORIES:
        muscle_ids: set[str] = set()
        for source_root in category.get("muscleRoots", []):
            muscle_ids |= closure([source_root], isa_edges, category.get("muscleExclusions", []))
        muscle_ids &= muscle_fma
        bone_ids: set[str] = set()
        for source_root in category.get("boneRoots", []):
            bone_ids |= closure([source_root], partof_edges)
        bone_ids &= bone_fma
        muscle_file_ids = set().union(*(isa_elements_by_concept.get(concept_id, set()) for concept_id in muscle_ids)) if muscle_ids else set()
        bone_file_ids = set().union(*(partof_elements_by_concept.get(concept_id, set()) for concept_id in bone_ids)) if bone_ids else set()
        muscle_sets[category["id"]] = muscle_file_ids
        bone_sets[category["id"]] = bone_file_ids
        result[category["id"]] = {
            "sourceRoots": {
                "muscle": [{"id": item, "name": isa_names.get(item), "tree": "IS-A"} for item in category.get("muscleRoots", [])],
                "bone": [{"id": item, "name": partof_names.get(item), "tree": "PART-OF"} for item in category.get("boneRoots", [])],
            },
            "muscleConceptIds": muscle_ids,
            "boneConceptIds": bone_ids,
            "muscleElementFileIds": muscle_file_ids,
            "boneElementFileIds": bone_file_ids,
        }
    return result, muscle_sets, bone_sets


def canonical_binding_map(root: Path) -> tuple[dict[str, set[str]], dict[str, set[str]], dict[str, set[str]], dict[str, set[str]]]:
    crosswalk = load_json(root / "atlas-data/catalog/source-crosswalk.json")
    navigation = load_json(root / "atlas-data/navigation/atlas-navigation.json")
    canonical = load_json(root / "atlas-data/catalog/canonical-catalog.json")["entities"]
    learner_ids: dict[str, set[str]] = defaultdict(set)
    learner_states: dict[str, set[str]] = defaultdict(set)
    for row in crosswalk.get("bodyParts3dMappings", []):
        learner_ids[row["elementFileId"]].add(row["stableConceptId"])
        learner_states[row["elementFileId"]].add(row.get("relationStatus", "unspecified_source_crosswalk"))
    canonical_instances = {row["id"]: row for row in canonical.get("instances", [])}
    canonical_muscles = {row["id"]: row for row in canonical.get("muscleConcepts", [])}
    for mapping in canonical.get("meshMappings", []):
        for mesh_id in mapping.get("meshIds", []):
            file_id = mesh_id.removeprefix("HA-MESH-BP3D4-")
            for instance_id in mapping.get("instanceIds", []):
                instance = canonical_instances.get(instance_id)
                stable_id = instance.get("conceptId") if instance else None
                if stable_id:
                    learner_ids[file_id].add(stable_id)
                    learner_states[file_id].add(mapping.get("reviewState", "unspecified_canonical_mesh_mapping"))
            for stable_id in mapping.get("partIds", []):
                if stable_id in canonical_muscles:
                    learner_ids[file_id].add(stable_id)
                    learner_states[file_id].add(mapping.get("reviewState", "unspecified_canonical_mesh_mapping"))
    instance_by_id = {row["id"]: row for row in navigation.get("structureInstances", [])}
    nav_mappings = navigation.get("structureMeshMappings", [])
    for row in nav_mappings:
        instance = instance_by_id.get(row.get("structureInstanceId"), {})
        stable_id = instance.get("structureId")
        for mesh_id in row.get("meshIds", []):
            file_id = mesh_id.removeprefix("HA-MESH-BP3D4-")
            if stable_id:
                learner_ids[file_id].add(stable_id)
                learner_states[file_id].add(row.get("reviewState", "unspecified_structure_mapping"))
    memberships_by_id: dict[str, set[str]] = defaultdict(set)
    membership_rows_by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in navigation.get("memberships", []):
        memberships_by_id[row["entityId"]].add(row["categoryId"])
        membership_rows_by_id[row["entityId"]].append(row)
    return learner_ids, learner_states, memberships_by_id, membership_rows_by_id


def parse_obj_for_glb(path: Path) -> tuple[list[tuple[float, float, float]], list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    spec = importlib.util.spec_from_file_location("ha_existing_bp3d_converter", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")
    if not spec or not spec.loader:
        raise ValueError("could not load the existing deterministic OBJ parser")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_obj(path)


def converted_sample(root: Path, acquired: list[dict[str, Any]], output_path: Path, model_id: str = "HA-MODEL-BP3D4-T51-SOURCE-CACHE-SAMPLE") -> dict[str, Any]:
    """Write one same-frame GLB sample. No mesh deformation or mirroring occurs."""
    validate_cached_source_records(root, acquired)
    spec = importlib.util.spec_from_file_location("ha_existing_bp3d_converter", root / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")
    if not spec or not spec.loader:
        raise ValueError("could not load the existing deterministic GLB packing helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.MODEL_ID = model_id
    learner_ids, learner_states, membership_categories, _ = canonical_binding_map(root)
    source_names = load_source_name_map(root)
    input_items = []
    output_identity = []
    for row in sorted(acquired, key=lambda item: item["sourceFileId"]):
        source_path = root / row["cacheRelativePath"]
        vertices, _normals, triangles = module.parse_obj(source_path)
        header = row["header"]
        fma = header.get("conceptId")
        source_name = source_names.get(fma)
        side = side_from_name(source_name)
        item = {
            "file_id": row["sourceFileId"],
            "source_path": source_path,
            "source_relative_path": row["cacheRelativePath"],
            "source_sha256": row["sha256"],
            "asset": {
                "bytes": row["bytes"],
                "vertex_count": len(vertices),
                "polygon_count": len(triangles),
                "concept_id": fma,
                "representation_id": header.get("representationId"),
            },
        }
        input_items.append(item)
        output_identity.append({
            "sourceFileId": row["sourceFileId"],
            "sourceConceptId": fma,
            "sourceConceptEnglishName": source_name,
            "sourceRepresentationId": header.get("representationId"),
            "learnerStableIds": sorted(learner_ids.get(row["sourceFileId"], set())),
            "learnerMappingStates": sorted(learner_states.get(row["sourceFileId"], set())),
            "productMembershipCategoryIds": sorted({category for stable_id in learner_ids.get(row["sourceFileId"], set()) for category in membership_categories.get(stable_id, set())}),
            "laterality": side,
            "transform": "[x_source,y_source,z_source]mm -> [x,z,-y]m; no mirroring",
            "frame": "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR",
            "pose": "bodyparts3d-r4-static-reference; no standardized articulated pose asserted",
            "lod": "source_resolution_unverified; this conversion preserves source faces and creates no additional LOD",
        })
    glb, mesh_records = module.build_glb(input_items)
    # Carry identity, laterality, coordinate, and LOD boundaries inside GLB extras.
    json_length, json_type = struct.unpack_from("<II", glb, 12)
    if json_type != 0x4E4F534A:
        raise ValueError("source converter did not produce the expected GLB JSON chunk")
    gltf = json.loads(glb[20:20 + json_length].decode("utf-8"))
    for index, identity in enumerate(output_identity):
        for node_list in (gltf.get("nodes", []), gltf.get("meshes", [])):
            if index < len(node_list):
                node_list[index].setdefault("extras", {}).update(identity)
    gltf["asset"]["generator"] = "HUMAN ATLAS T51 BodyParts3D cache converter"
    json_chunk = json_bytes(gltf).rstrip(b"\n")
    while len(json_chunk) % 4:
        json_chunk += b" "
    bin_chunk_header = 20 + json_length
    old_bin_length, bin_type = struct.unpack_from("<II", glb, bin_chunk_header)
    if bin_type != 0x004E4942:
        raise ValueError("source converter did not produce the expected GLB BIN chunk")
    binary = glb[bin_chunk_header + 8:bin_chunk_header + 8 + old_bin_length]
    total_length = 12 + 8 + len(json_chunk) + 8 + len(binary)
    updated = bytearray(struct.pack("<4sII", b"glTF", 2, total_length))
    updated.extend(struct.pack("<II", len(json_chunk), 0x4E4F534A))
    updated.extend(json_chunk)
    updated.extend(struct.pack("<II", len(binary), 0x004E4942))
    updated.extend(binary)
    glb = bytes(updated)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(glb)
    return {
        "path": output_path.relative_to(root).as_posix() if output_path.is_relative_to(root) else str(output_path),
        "modelId": model_id,
        "bytes": len(glb),
        "sha256": sha256_bytes(glb),
        "rendererSampleScope": "T51 verification renders one cached right lower-limb source set; conversion input IDs are explicit and do not create category membership",
        "meshCount": len(mesh_records),
        "sourceSha256s": {row["sourceFileId"]: row["sha256"] for row in acquired},
        "meshRecords": mesh_records,
        "sourceIdentityOverlay": output_identity,
        "transformMatrix": [[0.001, 0.0, 0.0], [0.0, 0.0, 0.001], [0.0, -0.001, 0.0]],
        "sidePolicy": "preserve source laterality; no bilateral duplication or mirroring",
        "lodPolicy": "no decimation; no synthetic LOD; source resolution status remains unverified",
    }


def side_from_name(name: str | None) -> str:
    if not name:
        return "not_observed"
    lowered = name.lower().strip()
    if lowered.startswith("right ") or " of right " in lowered:
        return "right"
    if lowered.startswith("left ") or " of left " in lowered:
        return "left"
    if "bilateral" in lowered:
        return "bilateral_source_term"
    return "not_lateralized_in_source_label"


def transform_vertex(vertex: tuple[float, float, float]) -> tuple[float, float, float]:
    """Apply the T50-established source-mm to HUMAN ATLAS meter frame map."""
    x, y, z = vertex
    return (x * 0.001, z * 0.001, -y * 0.001)


def transform_normal(normal: tuple[float, float, float]) -> tuple[float, float, float]:
    """Apply the right-handed coordinate rotation without unit scaling."""
    x, y, z = normal
    return (x, z, -y)


def load_source_name_map(root: Path) -> dict[str, str]:
    tables = load_tables(root / "atlas-data/source-cache/bodyparts3d-r4/metadata")
    output = {}
    for key in ("isaConcepts", "partofConcepts"):
        for fma, _bp, name in tables[key]:
            output.setdefault(fma, name)
    return output


def build_inventory(root: Path = ROOT, manifest_path: Path | None = None, chunks_dir: Path | None = None) -> dict[str, Any]:
    metadata_dir = root / "atlas-data/source-cache/bodyparts3d-r4/metadata"
    tables = load_tables(metadata_dir)
    cache_index_path = root / "atlas-data/source-cache/bodyparts3d-r4/cache-index.json"
    evidence_index_path = root / "work/evidence/T51/source-cache-file-inventory.json"
    if cache_index_path.is_file():
        cache_inventory = load_json(cache_index_path).get("files", [])
    elif evidence_index_path.is_file():
        cache_inventory = load_json(evidence_index_path).get("files", [])
    else:
        cache_inventory = sync_mesh_cache(root)
    cache_by_fj = {row["sourceFileId"]: row for row in cache_inventory}
    if len(cache_by_fj) != len(cache_inventory):
        raise ValueError("duplicate cached BodyParts3D file IDs")
    validate_cached_source_records(root, cache_inventory)

    concept_records: dict[str, dict[str, Any]] = {}
    for tree_key, tree_name in (("isaConcepts", "IS-A"), ("partofConcepts", "PART-OF")):
        for fma, bp, name in tables[tree_key]:
            record = concept_records.setdefault(fma, {"sourceFmaConceptId": fma, "sourceNameEnglish": name, "nameObservations": set(), "representations": [], "elementFileIds": set(), "sourceTrees": set()})
            record["nameObservations"].add(name)
            record["sourceTrees"].add(tree_name)
            record["representations"].append({"tree": tree_name, "sourceRepresentationId": bp})
    context_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    asset_expected: dict[str, set[str]] = defaultdict(set)
    for tree, key in (("IS-A", "isaCompoundElements"), ("PART-OF", "partofCompoundElements")):
        for fma, name, file_id in tables[key]:
            if fma in concept_records:
                concept_records[fma]["elementFileIds"].add(file_id)
            context_rows[file_id].append({"tree": tree, "sourceFmaConceptId": fma, "sourceNameEnglish": name})
            asset_expected[file_id].add(tree)

    source_name_by_fma = {fma: sorted(record["nameObservations"])[0] for fma, record in concept_records.items()}
    isa_edges = adjacency(tables["isaInclusion"])
    partof_edges = adjacency(tables["partofInclusion"])
    bone_ids = closure(["FMA5018"], isa_edges)
    muscle_ids = closure(["FMA5022"], isa_edges)
    routes, region_muscle_fj, region_bone_fj = region_map(root, tables)
    learner_ids, learner_states, membership_categories, membership_rows = canonical_binding_map(root)
    explicit_membership_files: dict[str, set[str]] = defaultdict(set)
    for file_id, stable_ids in learner_ids.items():
        for stable_id in stable_ids:
            for category_id in membership_categories.get(stable_id, set()):
                explicit_membership_files[category_id].add(file_id)
    for category in PRODUCT_CATEGORIES:
        category_id = category["id"]
        source_root_files = region_muscle_fj[category_id] | region_bone_fj[category_id]
        routes[category_id]["sourceRootElementFileIds"] = source_root_files
        routes[category_id]["existingProductBindingElementFileIds"] = explicit_membership_files[category_id] - source_root_files
        routes[category_id]["candidateElementFileIds"] = source_root_files | explicit_membership_files[category_id]
    nav = load_json(root / "atlas-data/navigation/atlas-navigation.json")
    t15g = load_json(root / "atlas-data/catalog/whole-body-inventory-t15g.json")
    current_catalog = load_json(root / "atlas-data/catalog/canonical-catalog.json")
    t15g_hash = sha256_file(root / "atlas-data/catalog/whole-body-inventory-t15g.json")
    source_crosswalk_hash = sha256_file(root / "atlas-data/catalog/source-crosswalk.json")
    current_bone_ids = sorted(row["id"] for row in current_catalog["entities"]["structures"] if row.get("kind") == "bone")
    historical_bone_ids = sorted(row["id"] for row in t15g["currentCanonicalBoneInventory"])

    for fma, record in concept_records.items():
        record["nameObservations"] = sorted(record["nameObservations"])
        record["sourceTrees"] = sorted(record["sourceTrees"])
        record["representations"] = sorted(record["representations"], key=lambda item: (item["tree"], item["sourceRepresentationId"]))
        record["elementFileIds"] = sorted(record["elementFileIds"])
        if fma in muscle_ids and fma in bone_ids:
            record["sourceEntityScopeCandidate"] = "bone_and_muscle_ancestry_overlap_review_required"
        elif fma in muscle_ids:
            record["sourceEntityScopeCandidate"] = "muscle_organ_descendant_candidate"
        elif fma in bone_ids:
            record["sourceEntityScopeCandidate"] = "bone_organ_descendant_candidate"
        else:
            record["sourceEntityScopeCandidate"] = "outside_muscle_or_bone_source_root"
        record["compositionStatus"] = "has_source_ELEMENT_component_rows" if record["elementFileIds"] else "no_ELEMENT_component_row_in_loaded_indexes"
        record["canonicalLearnerId"] = None
        record["identityPolicy"] = "source FMA/BP identifiers remain separate; no HA ID is generated from a name"

    mesh_records = []
    for file_id in sorted(asset_expected):
        acquired = cache_by_fj.get(file_id)
        header = acquired["header"] if acquired else None
        header_fma = header.get("conceptId") if header else None
        source_name = source_name_by_fma.get(header_fma)
        matching_routes = []
        for category in PRODUCT_CATEGORIES:
            region_id = category["id"]
            if file_id in routes[region_id]["candidateElementFileIds"]:
                matching_routes.append(region_id)
        mapping_status = "exact_existing_file_id_crosswalk" if learner_ids.get(file_id) else "no_existing_HA_file_id_crosswalk"
        mesh_records.append({
            "sourceElementFileId": file_id,
            "sourceIdNamespace": "BodyParts3D ELEMENT FJ file ID",
            "expectedInOfficialArchiveTrees": sorted(asset_expected[file_id]),
            "sourceContextRowCount": len(context_rows[file_id]),
            "sourceContextIndex": "sourceConcepts[].elementFileIds; official source relation rows remain uncollapsed there",
            "headerSourceFmaConceptId": header_fma,
            "headerSourceRepresentationId": header.get("representationId") if header else None,
            "headerSourceBuildUpLogic": header.get("buildUpLogic") if header else None,
            "sourceConceptEnglishName": source_name,
            "laterality": side_from_name(source_name) if header else "not_read_from_unacquired_file",
            "cachedSource": ({"status": "acquired_cached_local", "path": acquired["cacheRelativePath"], "bytes": acquired["bytes"], "sha256": acquired["sha256"], "headerLicenseObservation": acquired["header"].get("licenseHeader"), "resolutionStatus": "source_resolution_unverified"} if acquired else {"status": "not_acquired_download_not_attempted", "path": None, "bytes": None, "sha256": None, "downloadFailure": False}),
            "learnerIdentity": {"stableIds": sorted(learner_ids.get(file_id, set())), "mappingStatus": mapping_status, "mappingStates": sorted(learner_states.get(file_id, set()))},
            "candidateProductRegionIds": matching_routes,
            "learnerMembershipCategoryIds": sorted({category for stable_id in learner_ids.get(file_id, set()) for category in membership_categories.get(stable_id, set())}),
            "selectableByCurrentProductNavigation": any(membership_categories.get(stable_id) for stable_id in learner_ids.get(file_id, set())),
            "sourceFrame": "BodyParts3D Release 4.0 native reference; no OpenSim registration",
            "sourceUnit": "mm as read from existing T51 cache sample; other unacquired source-file units not independently header-verifiable",
            "sourcePose": "static source reference; no standardized articulated pose asserted",
            "sourceLod": "source_resolution_unverified" if acquired else "official_archive_profile_99_percent_reduced; no multilevel LOD chain advertised",
        })

    acquired_fj = set(cache_by_fj)
    converted_path = root / "atlas-data/source-cache/bodyparts3d-r4/converted/t51-right-lower-limb-sample.glb"
    converted_manifest_path = root / "work/evidence/T51/converted-sample.json"
    converted = load_json(converted_manifest_path) if converted_manifest_path.is_file() else None
    converted_fj = set(converted.get("sourceSha256s", {})) if converted else set()
    learner_selectables: dict[str, set[str]] = defaultdict(set)
    for row in nav.get("memberships", []):
        learner_selectables[row["categoryId"]].add(row["entityId"])

    region_rows = []
    chunk_outputs = []
    all_expected_muscle_fma: set[str] = set()
    all_expected_bone_fma: set[str] = set()
    assigned_muscle_fma: set[str] = set()
    assigned_bone_fma: set[str] = set()
    for category in PRODUCT_CATEGORIES:
        route = routes[category["id"]]
        m_ids = route["muscleConceptIds"]
        b_ids = route["boneConceptIds"]
        all_expected_muscle_fma |= m_ids
        all_expected_bone_fma |= b_ids
        assigned_muscle_fma |= m_ids
        assigned_bone_fma |= b_ids
        m_fj = route["muscleElementFileIds"]
        b_fj = route["boneElementFileIds"]
        source_root_fj = route["sourceRootElementFileIds"]
        existing_membership_fj = route["existingProductBindingElementFileIds"]
        expected_fj = route["candidateElementFileIds"]
        acquired_in_region = expected_fj & acquired_fj
        converted_in_region = expected_fj & converted_fj
        explicit_selectable_ids = learner_selectables.get(category["id"], set())
        selectable_fj = {file_id for file_id in acquired_in_region if learner_ids.get(file_id, set()) & explicit_selectable_ids}
        chunk = {
            "revision": "BodyParts3D-R4-T51-source-region-chunk-v1",
            "productCategoryId": category["id"],
            "labelKo": category["labelKo"],
            "status": "source_acquisition_candidates_plus_existing_bindings_no_membership_created",
            "routingPolicy": REGION_POLICY,
            "sourceRoots": route["sourceRoots"],
            "existingProductBindingSourceFileIds": sorted(existing_membership_fj),
            "excludedMuscleSourceRoots": category.get("muscleExclusions", []),
            "sourceMuscleConceptIds": sorted(m_ids),
            "sourceBoneConceptIds": sorted(b_ids),
            "sourceElementFileIds": sorted(expected_fj),
            "counts": {
                "expectedSourceMuscleConceptIds": len(m_ids),
                "expectedSourceBoneConceptIds": len(b_ids),
                "expectedSourceElementFileIdsUniqueWithinCategory": len(expected_fj),
                "sourceRootExpectedSourceElementFileIdsUniqueWithinCategory": len(source_root_fj),
                "existingProductBindingSourceElementFilesSupplement": len(existing_membership_fj),
                "expectedSourceElementFileIdsMuscleContexts": len(m_fj),
                "expectedSourceElementFileIdsBoneContexts": len(b_fj),
                "acquiredCachedSourceElementFiles": len(acquired_in_region),
                "convertedCachedSourceElementFiles": len(converted_in_region),
                "currentSelectableStableIds": len(explicit_selectable_ids),
                "acquiredFilesBoundToCurrentlySelectableStableIds": len(selectable_fj),
                "canonicalWholeBodyMuscleDenominatorContribution": None,
            },
            "learnerMemberships": sorted(membership_rows.get(next(iter(explicit_selectable_ids), ""), [])) if len(explicit_selectable_ids) == 1 else [row for entity_id in sorted(explicit_selectable_ids) for row in membership_rows.get(entity_id, [])],
            "assetStates": [{"sourceElementFileId": file_id, "cached": file_id in acquired_fj, "converted": file_id in converted_fj, "learnerStableIds": sorted(learner_ids.get(file_id, set())), "routeBasis": [basis for basis, values in (("official_source_region_roots", source_root_fj), ("existing_explicit_learner_membership_file_binding", explicit_membership_files[category["id"]])) if file_id in values], "downloadFailure": False, "downloadAttempt": "not_performed_for_uncached_meshes"} for file_id in sorted(expected_fj)],
        }
        region_rows.append({"productCategoryId": category["id"], "labelKo": category["labelKo"], "counts": chunk["counts"], "status": chunk["status"]})
        if chunks_dir:
            output = chunks_dir / f"{category['id']}.json"
            write_json(output, chunk)
            chunk_outputs.append(output)

    mesh_file_ids = set(asset_expected)
    outside_scope_fma = set(concept_records) - muscle_ids - bone_ids
    unassigned_asset_ids = mesh_file_ids - set().union(*region_muscle_fj.values()) - set().union(*region_bone_fj.values())
    muscle_counts = {
        "sourceConceptIdsInMuscleOrganDescendantClosure": len(muscle_ids),
        "sourceConceptIdsWithMeshComponentRows": len(muscle_ids & set().union(*(set(row[0] for row in tables["isaCompoundElements"]),))),
        "uniqueElementFileIdsInMuscleOrganDescendantClosure": len(set().union(*(region_muscle_fj.values()))),
        "uniqueCanonicalLearnerIndividualMuscleIds": t15g["counts"]["muscleConcepts"]["separatelyCounted"]["individualMuscleConcepts"],
        "canonicalWholeBodyIndividualMuscleCount": None,
        "denominatorFrozen": False,
    }
    bone_counts = {
        "sourceConceptIdsInBoneOrganDescendantClosure": len(bone_ids),
        "uniqueElementFileIdsInBoneOrganDescendantClosure": len(set().union(*(region_bone_fj.values()))),
        "canonicalWholeBodyBoneCount": None,
    }
    concepts_out = []
    for fma in sorted(concept_records):
        row = concept_records[fma]
        concepts_out.append({
            "sourceFmaConceptId": fma,
            "sourceNameEnglish": row["sourceNameEnglish"],
            "nameObservations": row["nameObservations"],
            "representations": row["representations"],
            "sourceTrees": row["sourceTrees"],
            "elementFileIds": row["elementFileIds"],
            "compositionStatus": row["compositionStatus"],
            "sourceEntityScopeCandidate": row["sourceEntityScopeCandidate"],
            "canonicalLearnerId": None,
        })
    metadata_files = []
    for key, file_name in METADATA_FILES.items():
        path = metadata_dir / file_name
        metadata_files.append({"logicalName": key, "path": path.relative_to(root).as_posix(), "url": SOURCE_URL_ROOT + file_name, "bytes": path.stat().st_size, "sha256": sha256_file(path), "rowCount": len(tables[key]), "retrievedOn": "2026-09-27"})
    input_hashes = {
        "atlas-data/catalog/whole-body-inventory-t15g.json": t15g_hash,
        "atlas-data/review-queue/region-crosswalk-t15g.json": sha256_file(root / "work/review-queue/region-crosswalk-t15g.json"),
        "atlas-data/catalog/source-crosswalk.json": source_crosswalk_hash,
        "atlas-data/navigation/atlas-navigation.json": sha256_file(root / "atlas-data/navigation/atlas-navigation.json"),
        "atlas-data/catalog/canonical-catalog.json": sha256_file(root / "atlas-data/catalog/canonical-catalog.json"),
    }
    manifest = {
        "revision": "BodyParts3D-R4-T51-source-inventory-v1",
        "status": "complete_source_metadata_inventory_partial_local_mesh_acquisition",
        "source": {"sourceId": SOURCE_ASSET_ID, "version": SOURCE_VERSION, "readmeUrl": SOURCE_URL_ROOT + "README_e.html", "archiveListingUrl": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html", "dataReleaseDate": "2013-06-19 (official README update history)", "licenseUrl": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html", "license": "CC BY 4.0 per official license page last updated 2025-02-27", "requiredAttribution": ATTRIBUTION, "meshArchives": [{"tree": "IS-A", "url": SOURCE_URL_ROOT + "isa_BP3D_4.0_obj_99.zip", "advertisedCompressedBytesApprox": 136000000, "polygonReductionRate": "99%", "localArchiveAcquired": False}, {"tree": "PART-OF", "url": SOURCE_URL_ROOT + "partof_BP3D_4.0_obj_99.zip", "advertisedCompressedBytesApprox": 62000000, "polygonReductionRate": "99%", "localArchiveAcquired": False}], "metadataFiles": metadata_files, "metadataAccess": "Official raw TSV files opened and downloaded via HTTPS; no search API used."},
        "rightsAndIntegrity": {"officialDatabaseLicense": "CC BY 4.0; required attribution recorded", "sampleObjHeaderObservations": ["Existing local OBJ headers claim CC BY-SA 2.1 Japan."], "fileLevelRightsStatus": "needs_manual_reconciliation_between_2025_site_terms_and_legacy_OBJ_headers", "distribution": "Do not redistribute cached OBJs or derivatives until file-level rights review closes the observed mismatch."},
        "identityPolicy": {"sourceConceptId": "FMA...", "sourceRepresentationId": "BP...", "sourceElementFileId": "FJ...", "learnerStableId": "HA-... only when an explicit existing ID crosswalk exists", "atomicCompound": "One FJ element asset is counted once globally; compound FMA contexts retain lists of FJ components. IS-A and PART-OF references to the same FJ are not duplicate geometry.", "side": "side is from exact source concept labels or acquired OBJ headers; no mirroring or synthetic opposite-side instance.", "region": REGION_POLICY},
        "frameAndLod": {"sourceFrame": "BodyParts3D Release 4.0 native reference; not registered to OpenSim", "sourceUnit": "Existing local sample OBJ bounds are millimeters; no unit declaration found in the official metadata table; source-wide unit verification remains open.", "atlasFrameTransform": "[x,y,z] source mm -> [x,z,-y] HUMAN ATLAS meters", "pose": "static reference geometry; no standardized articulated pose is asserted", "lod": "Official listed polygon bundles are one 99%-reduced representation, not a multilevel LOD set; existing cached OBJs' reduction profile is unverified."},
        "counts": {"sourceConceptRowsIS-A": len(tables["isaConcepts"]), "sourceConceptRowsPART-OF": len(tables["partofConcepts"]), "uniqueSourceFmaConceptIds": len(concept_records), "compoundElementRowsIS-A": len(tables["isaCompoundElements"]), "compoundElementRowsPART-OF": len(tables["partofCompoundElements"]), "uniqueExpectedSourceElementFileIdsIS-A": len({row[2] for row in tables["isaCompoundElements"]}), "uniqueExpectedSourceElementFileIdsPART-OF": len({row[2] for row in tables["partofCompoundElements"]}), "uniqueExpectedSourceElementFileIdsAcrossTrees": len(mesh_file_ids), "sharedFileIdsAcrossTrees": len(set(row[2] for row in tables["isaCompoundElements"]) & set(row[2] for row in tables["partofCompoundElements"])), "cachedActualSourceObjFiles": len(cache_by_fj), "convertedSampleFiles": len(converted_fj), "notAcquiredAndNotAttempted": len(mesh_file_ids - acquired_fj), "downloadFailures": 0, "canonicalWholeBodyIndividualMuscleCount": None, "coveragePercent": None},
        "muscleSourceScopeCounts": muscle_counts,
        "boneSourceScopeCounts": bone_counts,
        "t15gDrift": {"historicalPath": "atlas-data/catalog/whole-body-inventory-t15g.json", "historicalSha256": t15g_hash, "historicalDenominatorFrozen": t15g["denominatorFrozen"], "historicalWholeBodyIndividualMuscleCount": t15g["wholeBodyIndividualMuscleCount"], "newInventoryIsSeparate": True, "historicalBoneStructureIds": historical_bone_ids, "currentCanonicalBoneStructureIds": current_bone_ids, "currentCanonicalBoneCount": len(current_bone_ids), "addedCanonicalBoneIdsSinceHistoricalInventory": sorted(set(current_bone_ids) - set(historical_bone_ids)), "historicalBoneIdsMissingFromCurrentCanonical": sorted(set(historical_bone_ids) - set(current_bone_ids))},
        "inputHashes": input_hashes,
        "productRegions": region_rows,
        "unassignedSourceScope": {"muscleSourceConceptIdsOutsideMappedRootsCount": len(muscle_ids - all_expected_muscle_fma), "boneSourceConceptIdsOutsideMappedRootsCount": len(bone_ids - all_expected_bone_fma), "otherBodyPartsSourceConceptIds": len(outside_scope_fma), "unassignedUniqueElementFileIds": len(unassigned_asset_ids), "note": "Source-root to 12-category routing is incomplete by design; unassigned does not mean absent from BodyParts3D or absent from the body."},
        "sourceConcepts": concepts_out,
        "sourceElementFiles": mesh_records,
        "interpretationBoundary": ["This manifest exhausts the official downloaded source index rows used here, not a frozen HUMAN ATLAS whole-body canonical muscle denominator.", "The source includes source FMA concepts, BP representations, and FJ element files; these are not learner IDs.", "The expected mesh file inventory comes from the official 99%-reduced archive index. The full OBJ archives were not acquired. Uncached files are not attempted, not failed.", "No source-absent muscle, opposite-side mesh, canonical learner ID, runtime membership, or reviewed status is created.", "Download/convert counts do not indicate product model completion. No continuous whole-body product scene or animation-ready model was released."]
    }

    if manifest_path:
        write_json(manifest_path, manifest)
    if chunks_dir:
        # chunks are written below in a single pass to keep their complete source rows compact
        for category in PRODUCT_CATEGORIES:
            region_id = category["id"]
            route = routes[region_id]
            m_ids = route["muscleConceptIds"]
            b_ids = route["boneConceptIds"]
            m_fj = route["muscleElementFileIds"]
            b_fj = route["boneElementFileIds"]
            source_root_fj = route["sourceRootElementFileIds"]
            existing_membership_fj = route["existingProductBindingElementFileIds"]
            expected_fj = route["candidateElementFileIds"]
            acquired_in_region = expected_fj & acquired_fj
            converted_in_region = expected_fj & converted_fj
            explicit_selectable_ids = learner_selectables.get(region_id, set())
            selectable_fj = {file_id for file_id in acquired_in_region if learner_ids.get(file_id, set()) & explicit_selectable_ids}
            chunk = {
                "revision": "BodyParts3D-R4-T51-source-region-chunk-v1",
                "productCategoryId": region_id,
                "labelKo": category["labelKo"],
                "status": "source_acquisition_candidates_plus_existing_bindings_no_membership_created",
                "routingPolicy": REGION_POLICY,
                "sourceRoots": route["sourceRoots"],
                "existingProductBindingSourceFileIds": sorted(existing_membership_fj),
                "excludedMuscleSourceRoots": category.get("muscleExclusions", []),
                "sourceMuscleConceptIds": sorted(m_ids),
                "sourceBoneConceptIds": sorted(b_ids),
                "sourceElementFileIds": sorted(expected_fj),
                "counts": {
                    "expectedSourceMuscleConceptIds": len(m_ids), "expectedSourceBoneConceptIds": len(b_ids),
                    "expectedSourceElementFileIdsUniqueWithinCategory": len(expected_fj),
                    "sourceRootExpectedSourceElementFileIdsUniqueWithinCategory": len(source_root_fj),
                    "existingProductBindingSourceElementFilesSupplement": len(existing_membership_fj),
                    "expectedSourceElementFileIdsMuscleContexts": len(m_fj), "expectedSourceElementFileIdsBoneContexts": len(b_fj),
                    "acquiredCachedSourceElementFiles": len(acquired_in_region), "convertedCachedSourceElementFiles": len(converted_in_region),
                    "currentSelectableStableIds": len(explicit_selectable_ids), "acquiredFilesBoundToCurrentlySelectableStableIds": len(selectable_fj),
                    "canonicalWholeBodyMuscleDenominatorContribution": None,
                },
                "learnerMemberships": [row for entity_id in sorted(explicit_selectable_ids) for row in membership_rows.get(entity_id, [])],
                "assetStates": [{"sourceElementFileId": file_id, "cached": file_id in acquired_fj, "converted": file_id in converted_fj, "learnerStableIds": sorted(learner_ids.get(file_id, set())), "routeBasis": [basis for basis, values in (("official_source_region_roots", source_root_fj), ("existing_explicit_learner_membership_file_binding", explicit_membership_files[region_id])) if file_id in values], "downloadFailure": False, "downloadAttempt": "not_performed_for_uncached_meshes"} for file_id in sorted(expected_fj)],
            }
            write_json(chunks_dir / f"{region_id}.json", chunk)
    return manifest


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors = []
    files = manifest["sourceElementFiles"]
    file_ids = [row["sourceElementFileId"] for row in files]
    if len(file_ids) != len(set(file_ids)):
        errors.append("duplicate FJ source IDs in unique file inventory")
    if any(not file_id.startswith("FJ") for file_id in file_ids):
        errors.append("sourceElementFileId does not remain in FJ namespace")
    if manifest["counts"]["uniqueExpectedSourceElementFileIdsIS-A"] != len(file_ids):
        errors.append("IS-A FJ expected file count differs from inventory")
    if manifest["counts"]["sharedFileIdsAcrossTrees"] != manifest["counts"]["uniqueExpectedSourceElementFileIdsPART-OF"]:
        errors.append("PART-OF file IDs should be a subset of IS-A IDs in this pinned metadata snapshot")
    if any(row["cachedSource"]["status"] == "not_acquired_download_not_attempted" and row["cachedSource"]["downloadFailure"] for row in files):
        errors.append("uncached files must not be reported as download failures without an attempt")
    if any(row["learnerIdentity"]["mappingStatus"] == "exact_existing_file_id_crosswalk" and not row["learnerIdentity"]["stableIds"] for row in files):
        errors.append("exact learner crosswalk status requires a stable learner ID")
    if manifest["t15gDrift"]["historicalDenominatorFrozen"] is not False or manifest["t15gDrift"]["historicalWholeBodyIndividualMuscleCount"] is not None:
        errors.append("T15g historical denominator was altered or misrepresented")
    if manifest["counts"]["canonicalWholeBodyIndividualMuscleCount"] is not None or manifest["counts"]["coveragePercent"] is not None:
        errors.append("source asset count must not become a frozen product denominator")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sync-cache", action="store_true", help="copy existing hash-verified source OBJ originals into the local source cache")
    parser.add_argument("--build", action="store_true", help="build full source manifest and 12 candidate region chunks")
    parser.add_argument("--convert-sample", action="store_true", help="convert only the cached right lower-limb sample set to one GLB")
    parser.add_argument("--all", action="store_true", help="run cache sync, complete metadata inventory, and the bounded T51 sample conversion")
    parser.add_argument("--ingest-obj", type=Path, help="copy one explicitly obtained local OBJ after exact R4 FJ/FMA/BP identity validation")
    parser.add_argument("--convert-file-id", action="append", dest="convert_file_ids", help="explicitly convert a cached source FJ ID; repeat once per mesh")
    parser.add_argument("--convert-output", type=Path, help="output path required with --convert-file-id; this does not imply product readiness")
    parser.add_argument("--output-dir", type=Path, help="optional manifest/chunk output directory for reproducibility checks")
    args = parser.parse_args(argv)
    if args.ingest_obj:
        if args.sync_cache or args.build or args.convert_sample or args.all or args.output_dir or args.convert_file_ids or args.convert_output:
            parser.error("--ingest-obj is a standalone local import; run --build separately to refresh inventory")
        try:
            record = ingest_obj_file(args.ingest_obj)
        except (OSError, ValueError) as exc:
            print(f"ingest rejected: {exc}", file=sys.stderr)
            return 2
        print(f"ingested source FJ={record['sourceFileId']} bytes={record['bytes']} sha256={record['sha256']} rights=held")
        return 0
    if args.convert_file_ids:
        if args.sync_cache or args.build or args.convert_sample or args.all or args.output_dir or not args.convert_output:
            parser.error("--convert-file-id requires --convert-output and runs as a standalone local conversion")
        index_path = ROOT / "atlas-data/source-cache/bodyparts3d-r4/cache-index.json"
        evidence_path = ROOT / "work/evidence/T51/source-cache-file-inventory.json"
        if index_path.is_file():
            records = load_json(index_path)["files"]
        elif evidence_path.is_file():
            records = load_json(evidence_path)["files"]
        else:
            parser.error("no local source cache index; first run --sync-cache or explicitly ingest a local OBJ")
        by_id = {row["sourceFileId"]: row for row in records}
        missing = [file_id for file_id in args.convert_file_ids if file_id not in by_id]
        if missing:
            print("conversion rejected; source files are not cached:", ", ".join(missing), file=sys.stderr)
            return 2
        try:
            converted = converted_sample(ROOT, [by_id[file_id] for file_id in sorted(set(args.convert_file_ids))], args.convert_output, model_id="HA-MODEL-BP3D4-LOCAL-CACHE-CONVERSION")
        except (OSError, ValueError) as exc:
            print(f"conversion rejected: {exc}", file=sys.stderr)
            return 2
        print(f"converted meshes={converted['meshCount']} bytes={converted['bytes']} sha256={converted['sha256']}")
        return 0
    if not (args.sync_cache or args.build or args.convert_sample or args.all):
        parser.error("choose --all or one of --sync-cache/--build/--convert-sample/--ingest-obj")
    if args.convert_output:
        parser.error("--convert-output is valid only with --convert-file-id")
    acquired = sync_mesh_cache(ROOT) if args.sync_cache or args.all else []
    if acquired:
        # Keep the historical T15g sample list as bounded evidence while merging
        # it with any separately imported, source-validated cache entries.
        merge_cache_index(ROOT, acquired)
        write_json(ROOT / "work/evidence/T51/source-cache-file-inventory.json", {"revision": "BodyParts3D-R4-T51-local-source-cache-v1", "sourceId": SOURCE_ASSET_ID, "files": acquired, "rightsBoundary": "Original source headers and hashes preserved; do not distribute pending file-level rights reconciliation."})
    if args.convert_sample or args.all:
        cache_index = ROOT / "work/evidence/T51/source-cache-file-inventory.json"
        if not acquired and cache_index.is_file():
            acquired = load_json(cache_index)["files"]
        elif not acquired:
            acquired = sync_mesh_cache(ROOT)
            write_json(cache_index, {"revision": "BodyParts3D-R4-T51-local-source-cache-v1", "sourceId": SOURCE_ASSET_ID, "files": acquired, "rightsBoundary": "Original source headers and hashes preserved; do not distribute pending file-level rights reconciliation."})
        sample_path = CACHE / "converted/t51-right-lower-limb-sample.glb"
        converted = converted_sample(ROOT, acquired, sample_path)
        write_json(ROOT / "work/evidence/T51/converted-sample.json", converted)
        print(f"converted sample meshes={converted['meshCount']} bytes={converted['bytes']} sha256={converted['sha256']}")
    if args.build or args.all:
        if not acquired:
            cache_index = ROOT / "work/evidence/T51/source-cache-file-inventory.json"
            source_cache_index = ROOT / "atlas-data/source-cache/bodyparts3d-r4/cache-index.json"
            if source_cache_index.is_file():
                acquired = load_json(source_cache_index)["files"]
            else:
                acquired = load_json(cache_index)["files"] if cache_index.is_file() else sync_mesh_cache(ROOT)
        base = args.output_dir or ROOT / "atlas-data/manifests/bodyparts3d-r4-t51"
        manifest_path = (base / "source-manifest.json") if args.output_dir else ROOT / "atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json"
        chunks_dir = (base / "regions") if args.output_dir else ROOT / "atlas-data/manifests/bodyparts3d-r4-regions-t51"
        manifest = build_inventory(ROOT, manifest_path, chunks_dir)
        errors = validate_manifest(manifest)
        if errors:
            print("validation failed:", *errors, sep="\n- ", file=sys.stderr)
            return 2
        print(f"built source concepts={manifest['counts']['uniqueSourceFmaConceptIds']} source files={manifest['counts']['uniqueExpectedSourceElementFileIdsAcrossTrees']} cached={manifest['counts']['cachedActualSourceObjFiles']} chunks={len(PRODUCT_CATEGORIES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
