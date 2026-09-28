#!/usr/bin/env python3
"""Read-only Blender BHead inventory extension for T98.

This reuses the T97 SDNA reader without loading the project file into Blender.
It records serialized Object/ID relationships and explicitly does not claim
that raw datablocks equal evaluated geometry.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
T97_READER = ROOT / "work/evidence/T97/parse_blend_datablocks.py"
T97_INVENTORY = ROOT / "work/evidence/T97/blender-object-inventory.json"
SOURCE = ROOT / "atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend"
OUT = Path(__file__).resolve().parent
SAMPLE_NAMES = [
    "Frontalis muscle.l",
    "Latissimus dorsi muscle.l", "Latissimus dorsi muscle.r",
    "Clavicular part of deltoid muscle.l", "Clavicular part of deltoid muscle.r",
    "Tibialis anterior muscle.l",
    "Scapula.l", "Scapula.r", "Vertebra L5", "Sacrum",
    "Clavicular part of deltoid muscle.ol", "Cross Section X",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_reader_module():
    spec = importlib.util.spec_from_file_location("t97_readonly_blend_reader", T97_READER)
    if not spec or not spec.loader:
        raise RuntimeError("could not load the pinned T97 read-only parser")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def name_of(record: dict) -> str | None:
    value = record.get("id")
    if isinstance(value, dict):
        name = value.get("name")
        return name[2:] if isinstance(name, str) and len(name) > 2 else name
    return None


def ptr_key(value):
    return f"0x{value:x}" if isinstance(value, int) and value else None


def linear_determinant(flat):
    if not isinstance(flat, list) or len(flat) < 11:
        return None
    a, b, c = flat[0:3], flat[4:7], flat[8:11]
    return a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])


def linked_nodes(reader, base, node_map, limit=10000):
    if not isinstance(base, dict):
        return {"count": 0, "nodes": [], "unresolvedPointer": None}
    current = base.get("first", 0) or 0
    seen = set()
    nodes = []
    unresolved = None
    while current and current not in seen and len(nodes) < limit:
        seen.add(current)
        node = node_map.get(current)
        if node is None:
            unresolved = ptr_key(current)
            break
        nodes.append({
            "pointer": ptr_key(current),
            "type": node["type"],
            "name": node["record"].get("name"),
            "subtype": node["record"].get("type"),
        })
        current = node["record"].get("next", 0) or 0
    if current in seen:
        unresolved = "cycle:" + ptr_key(current)
    elif len(nodes) >= limit:
        unresolved = "node_limit"
    return {"count": len(nodes), "nodes": nodes, "unresolvedPointer": unresolved}


def main():
    if not SOURCE.is_file():
        raise SystemExit(f"pinned source file missing: {SOURCE}")
    reader_module = load_reader_module()
    reader = reader_module.BlendReader(SOURCE)
    t97_inventory = json.loads(T97_INVENTORY.read_text(encoding="utf-8"))
    source_sha = sha256(SOURCE)
    if source_sha != "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd":
        raise SystemExit("pinned Startup.blend hash mismatch; refusing to inventory changed source")

    wanted_types = ["Object", "Mesh", "Curve", "Collection", "Scene"]
    by_type = defaultdict(list)
    for type_name in wanted_types:
        for block, old, record in reader.records(type_name):
            by_type[type_name].append({
                "pointer": old,
                "name": name_of(record),
                "record": record,
                "fileOffset": block.offset,
            })

    def index_rows(type_name):
        return {row["pointer"]: row for row in by_type[type_name] if row["pointer"]}

    objects = index_rows("Object")
    meshes = index_rows("Mesh")
    curves = index_rows("Curve")
    collections = index_rows("Collection")
    scenes = index_rows("Scene")
    ids_by_pointer = {}
    for type_name in ["Object", "Mesh", "Curve", "Collection", "Scene"]:
        ids_by_pointer.update(index_rows(type_name))

    # Exact DATA list node maps. These are serialized collection links, not a
    # calculated dependency graph.
    collection_object_map = {}
    collection_child_map = {}
    for type_name, output in (("CollectionObject", collection_object_map), ("CollectionChild", collection_child_map)):
        for block, old, record in reader.records(type_name):
            if old:
                output[old] = {"type": type_name, "record": record, "block": block.offset}

    def list_links(first, node_map, target_field):
        current = first or 0
        seen = set()
        result = []
        unresolved = None
        while current and current not in seen:
            seen.add(current)
            node = node_map.get(current)
            if node is None:
                unresolved = ptr_key(current)
                break
            target = node["record"].get(target_field, 0) or 0
            result.append(target)
            current = node["record"].get("next", 0) or 0
        if current in seen:
            unresolved = "cycle:" + ptr_key(current)
        return result, unresolved

    collection_object_targets = {}
    collection_child_targets = {}
    for address, row in collections.items():
        rec = row["record"]
        obj_list, obj_err = list_links((rec.get("gobject") or {}).get("first", 0), collection_object_map, "ob")
        child_list, child_err = list_links((rec.get("children") or {}).get("first", 0), collection_child_map, "collection")
        collection_object_targets[address] = (obj_list, obj_err)
        collection_child_targets[address] = (child_list, child_err)

    collection_paths = defaultdict(list)

    def walk_collection(address, names, ancestors):
        if address in ancestors or address not in collections:
            return
        row = collections[address]
        path = names + [row["name"]]
        object_targets, _ = collection_object_targets[address]
        for obj_ptr in object_targets:
            if obj_ptr in objects:
                collection_paths[obj_ptr].append(path)
        child_targets, _ = collection_child_targets[address]
        for child_ptr in child_targets:
            walk_collection(child_ptr, path, ancestors | {address})

    scene_roots = []
    for address, row in scenes.items():
        root = row["record"].get("master_collection", 0) or 0
        scene_roots.append({"sceneName": row["name"], "rootCollection": ptr_key(root), "rootCollectionName": collections.get(root, {}).get("name"), "unitSettingsRaw": row["record"].get("unit"), "unitSettingsInterpretation": "raw SDNA fields only; physical unit semantics not certified because Blender project evaluation was unavailable", "frameStartRaw": row["record"].get("r", {}).get("sfra") if isinstance(row["record"].get("r"), dict) else None, "frameEndRaw": row["record"].get("r", {}).get("efra") if isinstance(row["record"].get("r"), dict) else None, "currentFrameRaw": row["record"].get("r", {}).get("cfra") if isinstance(row["record"].get("r"), dict) else None})
        if root:
            walk_collection(root, [], set())

    # Identify linked-list node records for modifiers/constraints. A missing
    # node is reported as unresolved rather than silently counted as none.
    modifier_types = [t for t in reader.struct_type_names if "ModifierData" in t]
    constraint_types = [t for t in reader.struct_type_names if "Constraint" in t and t in {"bConstraint", "bConstraintChannel"}]

    def collect_link_map(types):
        result = {}
        for type_name in types:
            for block, old, record in reader.records(type_name):
                if old:
                    result[old] = {"type": type_name, "record": record}
        return result

    modifier_map = collect_link_map(modifier_types)
    constraint_map = collect_link_map(constraint_types)

    mesh_ref_counts = Counter()
    curve_ref_counts = Counter()
    object_rows = []
    for address, row in objects.items():
        rec = row["record"]
        data_address = rec.get("data", 0) or 0
        if data_address in meshes:
            mesh_ref_counts[data_address] += 1
        if data_address in curves:
            curve_ref_counts[data_address] += 1
        mods = linked_nodes(reader, rec.get("modifiers"), modifier_map)
        constraints = linked_nodes(reader, rec.get("constraints"), constraint_map)
        object_rows.append({
            "sourceObjectLocator": {"archivePath": "Z-Anatomy/Startup.blend", "sourceFileSha256": source_sha, "objectDataBlockPointer": ptr_key(address), "objectIdName": row["name"], "serializedFileBlockOffset": row["fileOffset"]},
            "objectTypeEnumRaw": rec.get("type"),
            "dataPointer": ptr_key(data_address),
            "dataKind": "Mesh" if data_address in meshes else "Curve" if data_address in curves else (ids_by_pointer.get(data_address, {}).get("record", {}).get("id", {}) or {}).get("name", "unresolved_or_non_geometry") if data_address else None,
            "dataBlockName": meshes.get(data_address, curves.get(data_address, ids_by_pointer.get(data_address, {}))).get("name") if data_address else None,
            "parentObjectPointer": ptr_key(rec.get("parent", 0) or 0),
            "parentObjectName": objects.get(rec.get("parent", 0) or 0, {}).get("name"),
            "collectionPaths": collection_paths.get(address, []),
            "transformRaw": {key: rec.get(key) for key in ("loc", "rot", "quat", "scale", "obmat", "imat", "parentinv") if key in rec},
            "serializedObjectMatrixLinearDeterminant": linear_determinant(rec.get("obmat")),
            "modifierEvidence": mods,
            "constraintEvidence": constraints,
            "collectionInstancePointer": ptr_key(rec.get("dup_group", 0) or 0),
            "animationDataPointer": ptr_key(rec.get("adt", 0) or 0),
            "rawVisibilityFlags": {key: rec.get(key) for key in ("flag", "restrictflag", "visibility_flag") if key in rec},
        })

    object_rows.sort(key=lambda row: (row["sourceObjectLocator"]["objectIdName"] or "", row["sourceObjectLocator"]["objectDataBlockPointer"] or ""))
    by_name = defaultdict(list)
    for row in object_rows:
        by_name[row["sourceObjectLocator"]["objectIdName"]].append(row)
    absent = [name for name in SAMPLE_NAMES if len(by_name.get(name, [])) != 1]
    if absent:
        raise SystemExit("representative sample labels absent/ambiguous: " + ", ".join(absent))
    sample = [by_name[name][0] for name in SAMPLE_NAMES]

    object_type_counts = Counter(row["objectTypeEnumRaw"] for row in object_rows)
    with_modifiers = [row for row in object_rows if row["modifierEvidence"]["count"] or row["modifierEvidence"]["unresolvedPointer"]]
    with_constraints = [row for row in object_rows if row["constraintEvidence"]["count"] or row["constraintEvidence"]["unresolvedPointer"]]
    collection_instances = [row for row in object_rows if row["collectionInstancePointer"]]
    mesh_shared = {ptr_key(address): count for address, count in mesh_ref_counts.items() if count > 1}
    curve_shared = {ptr_key(address): count for address, count in curve_ref_counts.items() if count > 1}
    modifier_type_counts = Counter(node["type"] for row in object_rows for node in row["modifierEvidence"]["nodes"])
    constraint_type_counts = Counter(node["type"] for row in object_rows for node in row["constraintEvidence"]["nodes"])
    sample_data_ptrs = [row["dataPointer"] for row in sample if row["dataPointer"]]
    sample_shared_mesh_pointers = sorted({ptr for ptr in sample_data_ptrs if sample_data_ptrs.count(ptr) > 1})
    sample_negative_matrix_objects = [row["sourceObjectLocator"]["objectIdName"] for row in sample if isinstance(row["serializedObjectMatrixLinearDeterminant"], (float, int)) and row["serializedObjectMatrixLinearDeterminant"] < 0]

    compact_meshes = []
    for address, row in meshes.items():
        rec = row["record"]
        compact_meshes.append({"meshDataBlockPointer": ptr_key(address), "name": row["name"], "objectReferenceCount": mesh_ref_counts[address], "verticesRaw": rec.get("totvert"), "edgesRaw": rec.get("totedge"), "loopsRaw": rec.get("totloop"), "polygonsRaw": rec.get("totpoly")})
    compact_curves = []
    for address, row in curves.items():
        compact_curves.append({"curveDataBlockPointer": ptr_key(address), "name": row["name"], "objectReferenceCount": curve_ref_counts[address], "curveTypeRaw": row["record"].get("type"), "pointCountRaw": row["record"].get("totpoint"), "splineCountRaw": row["record"].get("totcol")})
    compact_collections = []
    for address, row in collections.items():
        object_targets, object_error = collection_object_targets[address]
        child_targets, child_error = collection_child_targets[address]
        compact_collections.append({"collectionPointer": ptr_key(address), "name": row["name"], "objectMemberCount": len(object_targets), "objectNames": [objects[p]["name"] for p in object_targets if p in objects], "childCollectionNames": [collections[p]["name"] for p in child_targets if p in collections], "unresolvedObjectListPointer": object_error, "unresolvedChildListPointer": child_error})

    result = {
        "schemaVersion": "1.0.0",
        "task": "T98",
        "status": "raw_datablock_inventory_only_evaluated_export_unverified",
        "source": {"archivePath": "atlas-data/source-cache/z-anatomy/t97/Z-Anatomy.zip", "archiveSha256": "e029688545627bd0214b269e1063143abb580aad72b2c2445d6d8a9a0d9da736", "memberPath": "Z-Anatomy/Startup.blend", "memberSha256": source_sha, "memberBytes": SOURCE.stat().st_size, "blendFormatVersion": reader.version, "pointerSize": reader.pointer_size, "endian": reader.endian},
        "method": "T97 read-only custom BHead/SDNA parser; no Blender load, Python text execution, add-on, driver, depsgraph, evaluated mesh, or transform baking. Object arrays/matrices below are serialized source metadata only.",
        "denominators": {"fileArchiveEntries": 7, "fileArchiveFiles": 6, "sourceBlendFiles": 1, "objects": len(object_rows), "meshDatablocks": len(compact_meshes), "curveDatablocks": len(compact_curves), "collections": len(compact_collections), "scenes": len(scenes), "serializedDatablockCountsByTypeFromT97": t97_inventory.get("dataBlockCountsByType", {}), "rawObjectTypeEnumCounts": {str(k): v for k, v in sorted(object_type_counts.items(), key=lambda item: str(item[0]))}, "meshDataBlocksReferencedByMultipleObjects": sum(1 for count in mesh_ref_counts.values() if count > 1), "objectsReferencingSharedMeshData": sum(count for count in mesh_ref_counts.values() if count > 1), "curveDataBlocksReferencedByMultipleObjects": sum(1 for count in curve_ref_counts.values() if count > 1), "objectsWithSerializedModifiers": len(with_modifiers), "modifierNodeTypes": dict(sorted(modifier_type_counts.items())), "objectsWithSerializedConstraints": len(with_constraints), "constraintNodeTypes": dict(sorted(constraint_type_counts.items())), "objectsWithCollectionInstancePointer": len(collection_instances), "objectsWithAnimationDataPointer": sum(bool(row["animationDataPointer"]) for row in object_rows), "armatureDatablocks": t97_inventory.get("dataBlockCountsByType", {}).get("Armature", 0)},
        "scopeLimit": "These are Blender file datablock and serialized Object relationships. They do not count canonical concepts, evaluated geometry, active scene instances, exportable mesh resources, anatomical structures, or region coverage.",
        "instanceAndReuseNotes": {"sharedMeshDataPointers": mesh_shared, "sharedCurveDataPointers": curve_shared, "modifierObjectExamples": [row["sourceObjectLocator"]["objectIdName"] for row in with_modifiers[:50]], "constraintObjectExamples": [row["sourceObjectLocator"]["objectIdName"] for row in with_constraints[:50]], "collectionInstanceObjectExamples": [row["sourceObjectLocator"]["objectIdName"] for row in collection_instances[:50]]},
        "sceneRoots": scene_roots,
        "collections": compact_collections,
        "meshDataBlocks": compact_meshes,
        "curveDataBlocks": compact_curves,
        "allObjects": object_rows,
        "representativeSample": {"frozenObjectCount": len(sample), "anatomicalObjectCount": sum(row["sourceObjectLocator"]["objectIdName"] != "Cross Section X" for row in sample), "selectionRationale": "Exact labels cover a facial muscle, bilateral latissimus dorsi, bilateral clavicular deltoid part, a lower-limb muscle, bilateral scapula, L5, and sacrum; additionally one .ol-suffixed deltoid Object with a serialized modifier and the Cross Section X constraint helper are included to expose those serialized cases. The helper is not an anatomy target. Locator includes source file hash and pointer. Source side is only the literal label suffix, not an anatomy or mirror approval. This is a candidate test set only until evaluated export is verified.", "caseCoverage": {"serializedModifierObjectNames": [row["sourceObjectLocator"]["objectIdName"] for row in sample if row["modifierEvidence"]["count"]], "serializedConstraintObjectNames": [row["sourceObjectLocator"]["objectIdName"] for row in sample if row["constraintEvidence"]["count"]], "sharedMeshPointersInSample": sample_shared_mesh_pointers, "negativeSerializedMatrixDeterminantObjects": sample_negative_matrix_objects, "collectionInstanceInSource": len(collection_instances) > 0, "collectionInstanceCandidateInSample": [row["sourceObjectLocator"]["objectIdName"] for row in sample if row["collectionInstancePointer"]]}, "objects": sample},
    }
    out_path = OUT / "blender-raw-object-inventory.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    summary = {k: v for k, v in result.items() if k not in {"allObjects", "collections", "meshDataBlocks", "curveDataBlocks", "representativeSample"}}
    summary["rawObjectInventorySha256"] = sha256(out_path)
    (OUT / "blender-raw-object-inventory-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sample_freeze = {
        "schemaVersion": "1.0.0",
        "task": "T98",
        "revision": "T98-12-object-export-candidate-freeze-v1",
        "status": "source_locators_frozen_export_and_evaluated_surface_pending",
        "source": result["source"],
        "frozenObjectCount": len(sample),
        "anatomicalObjectCount": sum(row["sourceObjectLocator"]["objectIdName"] != "Cross Section X" for row in sample),
        "sampleSelection": result["representativeSample"]["selectionRationale"],
        "caseCoverage": result["representativeSample"]["caseCoverage"],
        "geometryHash": None,
        "previewPath": None,
        "evaluatedExportVerified": False,
        "objects": sample,
        "explicitLimits": ["source suffix is not approved laterality", "serialized matrix determinant is not a verified evaluated winding result", "modifier/constraint values have not been applied", "no collection-instance pointer exists in the serialized sample", "no source pose/frame/unit compatibility has been certified", "Cross Section X is a constraint helper and not an anatomy target"],
    }
    (OUT / "representative-sample-freeze.json").write_text(json.dumps(sample_freeze, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "sourceSha256": source_sha, "denominators": result["denominators"], "sampleNames": [row["sourceObjectLocator"]["objectIdName"] for row in sample], "sampleModifierConstraintInstance": [{"name": row["sourceObjectLocator"]["objectIdName"], "modifiers": row["modifierEvidence"]["count"], "constraints": row["constraintEvidence"]["count"], "instancePointer": row["collectionInstancePointer"]} for row in sample], "output": str(out_path), "outputSha256": sha256(out_path)}, ensure_ascii=False, indent=2))
    reader.mm.close()
    reader.file.close()


if __name__ == "__main__":
    main()
