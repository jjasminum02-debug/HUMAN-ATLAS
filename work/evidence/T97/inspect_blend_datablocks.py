"""Read-only Blender inventory for the T97 pinned startup file.

Run with Blender's --background --factory-startup --disable-autoexec flags.
This script does not import/run the archive's Python text blocks, add-on, or drivers.
"""

import bpy
import json
import re
import sys
from pathlib import Path


def simple_value(value, depth=0):
    if depth > 6:
        return "<depth-limit>"
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [simple_value(v, depth + 1) for v in value]
    if hasattr(value, "to_list"):
        try:
            return simple_value(value.to_list(), depth + 1)
        except Exception:
            return repr(value)
    if hasattr(value, "keys") and hasattr(value, "__getitem__"):
        try:
            return {str(k): simple_value(value[k], depth + 1) for k in value.keys()}
        except Exception:
            return repr(value)
    return repr(value)


def custom_props(id_block):
    props = {}
    try:
        for key in id_block.keys():
            if key != "_RNA_UI":
                props[str(key)] = simple_value(id_block[key])
    except Exception as exc:
        return {"_readError": f"{type(exc).__name__}: {exc}"}
    return props


def block_names(collection_name):
    collection = getattr(bpy.data, collection_name, None)
    if collection is None:
        return None
    try:
        return sorted(str(item.name_full if hasattr(item, "name_full") else item.name) for item in collection)
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def all_collection_paths():
    paths = {}
    for scene in bpy.data.scenes:
        root = scene.collection

        def walk(collection, prefix, visited):
            if collection.as_pointer() in visited:
                return
            next_visited = set(visited)
            next_visited.add(collection.as_pointer())
            here = prefix + [collection.name_full]
            for obj in collection.objects:
                paths.setdefault(obj.as_pointer(), []).append(here + [obj.name_full])
            for child in collection.children:
                walk(child, here, next_visited)

        for obj in root.objects:
            paths.setdefault(obj.as_pointer(), []).append([scene.name_full, root.name_full, obj.name_full])
        for child in root.children:
            walk(child, [scene.name_full], set())
    return paths


def parent_path(obj):
    result = []
    seen = set()
    parent = obj.parent
    while parent is not None and parent.as_pointer() not in seen:
        seen.add(parent.as_pointer())
        result.append(parent.name_full)
        parent = parent.parent
    return list(reversed(result))


def matrix_rows(matrix):
    return [[float(matrix[r][c]) for c in range(4)] for r in range(4)]


def object_row(obj, collection_paths, candidate_pattern):
    data = obj.data
    data_type = getattr(data, "bl_rna", None)
    data_kind = data_type.identifier if data_type is not None else None
    data_name = data.name_full if data is not None and hasattr(data, "name_full") else None
    mesh_counts = None
    shape_keys = []
    if obj.type == "MESH" and data is not None:
        mesh_counts = {
            "vertices": len(data.vertices),
            "edges": len(data.edges),
            "polygons": len(data.polygons),
            "loops": len(data.loops),
        }
        if data.shape_keys is not None:
            shape_keys = [key.name for key in data.shape_keys.key_blocks]
    custom = custom_props(obj)
    data_custom = custom_props(data) if data is not None and hasattr(data, "keys") else {}
    search_values = [obj.name_full, data_name or ""]
    search_values.extend(str(v) for v in custom.values())
    search_values.extend(str(v) for v in data_custom.values())
    hits = sorted({m.group(0) for value in search_values for m in candidate_pattern.finditer(value)})
    try:
        session_uid = int(obj.session_uid)
    except Exception:
        session_uid = None
    try:
        dimensions = [float(v) for v in obj.dimensions]
    except Exception:
        dimensions = None
    return {
        "objectName": obj.name_full,
        "objectId": custom.get("id", custom.get("ID", custom.get("fma_id", custom.get("FMAID", custom.get("TA2ID"))))),
        "runtimeSessionUid": session_uid,
        "objectType": obj.type,
        "dataBlockName": data_name,
        "dataBlockKind": data_kind,
        "dataBlockProps": data_custom,
        "objectProps": custom,
        "collectionObjectPaths": sorted(collection_paths.get(obj.as_pointer(), [])),
        "parentPath": parent_path(obj),
        "parentInverseMatrix": matrix_rows(obj.matrix_parent_inverse),
        "localBasisMatrix": matrix_rows(obj.matrix_basis),
        "localDimensions": dimensions,
        "meshCounts": mesh_counts,
        "shapeKeyNames": shape_keys,
        "modifiers": [{"name": m.name, "type": m.type, "show_viewport": bool(m.show_viewport), "show_render": bool(m.show_render)} for m in obj.modifiers],
        "candidateSearchHits": hits,
    }


def main():
    if "--" not in sys.argv:
        raise SystemExit("expected output path after --")
    output = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    root = Path.cwd().resolve()
    if not output.is_relative_to((root / "work/evidence/T97").resolve()):
        raise SystemExit("output must remain inside work/evidence/T97")
    target_tokens = re.compile(r"(?i)(latissimus|latiss|dorsi|dorsal|2231|broad\s+back)")
    paths = all_collection_paths()
    object_rows = [object_row(obj, paths, target_tokens) for obj in bpy.data.objects]
    object_rows.sort(key=lambda row: (row["objectName"].casefold(), row["objectName"], row["dataBlockName"] or ""))
    category_names = [
        "objects", "meshes", "collections", "scenes", "materials", "curves", "armatures",
        "cameras", "lights", "images", "texts", "actions", "fonts", "worlds", "node_groups",
        "grease_pencils", "movieclips", "masks", "particles", "pointclouds", "volumes",
    ]
    data_inventory = {name: block_names(name) for name in category_names}
    candidate_rows = [row for row in object_rows if row["candidateSearchHits"]]
    result = {
        "task": "T97",
        "sourceFile": "Z-Anatomy/Startup.blend",
        "sourceFileSha256": "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd",
        "inspectionMode": "read_only_blender_background",
        "blenderVersion": bpy.app.version_string,
        "autoExecutionControl": {
            "commandFlagRequired": "--disable-autoexec",
            "commandFlagUsedByTaskRunner": True,
            "archivePythonTextBlocksExecuted": False,
            "archiveAddonExecuted": False,
            "driversEvaluated": False,
            "geometryEvaluationOrModifiersApplied": False,
            "rationale": "Direct data-block reads only; no depsgraph evaluation, scripts, drivers, modifiers, or archive add-on invocation.",
        },
        "scenes": sorted(scene.name_full for scene in bpy.data.scenes),
        "sceneRootCollections": {scene.name_full: scene.collection.name_full for scene in bpy.data.scenes},
        "dataBlockInventory": data_inventory,
        "objectCount": len(object_rows),
        "meshObjectCount": sum(1 for row in object_rows if row["objectType"] == "MESH"),
        "candidateSearchDefinition": "Inventory-only lexical pass over exact object name, linked mesh datablock name and primitive custom-property values; a match is not identity evidence or acceptance.",
        "candidateSearchCount": len(candidate_rows),
        "candidateSearchHits": candidate_rows,
        "allObjects": object_rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "blenderVersion": result["blenderVersion"],
        "objectCount": result["objectCount"],
        "meshObjectCount": result["meshObjectCount"],
        "candidateSearchCount": result["candidateSearchCount"],
        "candidateNames": [r["objectName"] for r in candidate_rows],
        "output": str(output),
    }, ensure_ascii=False, indent=2))


main()
